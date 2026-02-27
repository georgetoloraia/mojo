import os
import random
import time
import multiprocessing as mp
from example import *   # Assumes pubkey_from_scalar, subtract_pubkeys are fast (C extensions)

import asyncio
from telegram import Bot

BOT_TOKEN = '8'
CHAT_ID = 0

async def send_message(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)
    print("Message sent successfully!")

def load_precomputed(filename):
    """Load precomputed points from file.
       Returns a dict: compressed_pubkey -> exponent (int)
    """
    table = {}
    try:
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 2:
                    print(f"Warning: line {line_num} malformed, skipping: {line}")
                    continue
                exp_str, pub_hex = parts
                try:
                    table[pub_hex] = int(exp_str)
                except ValueError:
                    print(f"Warning: line {line_num} has non-integer exponent, skipping: {line}")
    except FileNotFoundError:
        print(f"Error: file '{filename}' not found.")
        raise
    return table

def worker(target_pub_hex, low, high, precomputed_table, stop_event, result_queue, worker_id, max_attempts=None):
    """
    Worker process: repeatedly picks random r, computes Q - r*G, checks if in table.
    If found, puts (k, r, exp) into result_queue and sets stop_event.
    """
    # Use a local random generator seeded uniquely
    rng = random.Random()
    rng.seed(os.urandom(8) + worker_id.to_bytes(4, 'big'))

    attempts = 0
    start_time = time.time()

    while True:
        # Stop if global event is set (another worker found a match)
        if stop_event.is_set():
            break

        # Stop if we've reached our individual attempt limit
        if max_attempts is not None and attempts >= max_attempts:
            break

        attempts += 1
        r = rng.randint(low, high)
        R_pub = pubkey_from_scalar(r)                # compute r*G
        diff_pub = subtract_pubkeys(target_pub_hex, R_pub)   # Q - r*G

        if diff_pub in precomputed_table:
            exp = precomputed_table[diff_pub]
            k_candidate = r + exp
            # Verify quickly (optional, but safe)
            if pubkey_from_scalar(k_candidate) == target_pub_hex:
                elapsed = time.time() - start_time
                print(f"Worker {worker_id}: found after {attempts} attempts in {elapsed:.2f}s")
                result_queue.put((k_candidate, r, exp))
                stop_event.set()
                break

        # Optional progress report (every million attempts)
        # if attempts % 1_000_000 == 0:
        #     elapsed = time.time() - start_time
        #     rate = attempts / elapsed
        #     print(f"Worker {worker_id}: {attempts} attempts, {rate:.0f} tries/sec")

def parallel_find_match(target_pub_hex, precomputed_table, low, high,
                        num_workers=4, total_max_attempts=None):
    """
    Parallel version using multiprocessing.
    total_max_attempts: if set, each worker gets total_max_attempts // num_workers attempts.
    Returns (k, r, exp) if found, else None.
    """
    # Prepare per-worker attempt limit
    if total_max_attempts is not None:
        per_worker = total_max_attempts // num_workers
    else:
        per_worker = None

    # Create shared event and queue
    stop_event = mp.Event()
    result_queue = mp.Queue()

    processes = []
    for i in range(num_workers):
        p = mp.Process(target=worker,
                       args=(target_pub_hex, low, high, precomputed_table,
                             stop_event, result_queue, i, per_worker))
        p.start()
        processes.append(p)

    # Monitor for a result or for all workers to finish
    try:
        while True:
            # Check if any process is still alive
            alive = any(p.is_alive() for p in processes)
            if not alive:
                # All processes finished without setting stop_event
                break

            # Peek at the queue without blocking (timeout 0.1 sec)
            try:
                result = result_queue.get(timeout=0.1)
                # We got a result – signal all workers to stop
                stop_event.set()
                # Wait a short moment for workers to notice the event
                for p in processes:
                    p.join(timeout=0.5)
                return result
            except mp.queues.Empty:
                # No result yet, continue monitoring
                pass

            # Small sleep to avoid busy waiting
            time.sleep(0.01)

        # All workers finished, check queue one last time
        if not result_queue.empty():
            return result_queue.get()
        else:
            return None

    except KeyboardInterrupt:
        print("Interrupted, stopping workers...")
        stop_event.set()
        for p in processes:
            p.join(timeout=1)
        return None
    finally:
        # Terminate any lingering processes
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()

if __name__ == "__main__":
    # Load precomputed table
    try:
        table = load_precomputed("precomputed_hex.txt")
        print(f"Loaded {len(table)} precomputed points.")
    except Exception as e:
        print(f"Failed to load table: {e}")
        exit(1)

    # Target public key (compressed hex)
    target = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"
    # Search range for r (must be positive integers)
    HIGH = 43556142965880123323311949751266331066368
    LOW = 21778071482940061661655974875633165533184

    # Notify start via Telegram (only from main process)
    asyncio.run(send_message(BOT_TOKEN, CHAT_ID, "Starting the search for k..."))

    # Use all available CPU cores
    num_cores = mp.cpu_count()
    print(f"Starting parallel search with {num_cores} workers...")

    # Adjust total attempts based on expected probability and time constraints
    # For a 32-bit range and a table of size M, the expected number of random trials
    # to find a match is about (2^32) / M. If M is 10,000, that's ~429,000 trials.
    # Here we set a conservative limit; you may increase or remove it.
    total_attempts = 10**7  # 10 million total attempts (adjust as needed)

    result = parallel_find_match(target, table, LOW, HIGH,
                                 num_workers=num_cores,
                                 total_max_attempts=total_attempts)

    if result:
        k, r, exp = result
        message = (f"\nSUCCESS: k = {k} (r = {r}, exponent = {exp})")
        print(message)
        asyncio.run(send_message(BOT_TOKEN, CHAT_ID, message))
    else:
        message = "\nNo match found within attempt limit."
        print(message)
        asyncio.run(send_message(BOT_TOKEN, CHAT_ID, message))