import os
import random
import time
import multiprocessing as mp
from example import *  

def load_precomputed(filename):
    """Load precomputed points from file.
       Returns a dict: compressed_pubkey -> exponent (int)
    """
    table = {}
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 2:
                continue
            exp_str, pub_hex = parts
            table[pub_hex] = int(exp_str)
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
    local_stop = False

    while not local_stop and (max_attempts is None or attempts < max_attempts):
        # Check global stop event occasionally
        if attempts % 1000 == 0 and stop_event.is_set():
            break

        attempts += 1
        r = rng.randint(low, high)
        R_pub = pubkey_from_scalar(r)                # compute r*G
        diff_pub = subtract_pubkeys(target_pub_hex, R_pub)   # Q - r*G

        if diff_pub in precomputed_table:
            exp = precomputed_table[diff_pub]
            k_candidate = r + (16 ** exp)            # because we stored 16^i
            # Verify quickly (optional, but safe)
            if pubkey_from_scalar(k_candidate) == target_pub_hex:
                elapsed = time.time() - start_time
                print(f"Worker {worker_id}: found after {attempts} attempts in {elapsed:.2f}s")
                result_queue.put((k_candidate, r, exp))
                stop_event.set()
                break

        # Optional progress report (every million attempts)
        if attempts % 1_000_000 == 0:
            elapsed = time.time() - start_time
            rate = attempts / elapsed
            print(f"Worker {worker_id}: {attempts} attempts, {rate:.0f} tries/sec")

def parallel_find_match(target_pub_hex, precomputed_table, low, high,
                        num_workers=4, total_max_attempts=None):
    """
    Parallel version using multiprocessing.
    total_max_attempts: if set, each worker gets total_max_attempts // num_workers attempts.
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

    # Wait for a result or for all processes to finish
    try:
        result = result_queue.get(timeout=None)  # blocks until something is queued
        # Signal all workers to stop
        stop_event.set()
        # Wait for all to finish
        for p in processes:
            p.join(timeout=1)
        return result   # (k, r, exp)
    except KeyboardInterrupt:
        print("Interrupted, stopping workers...")
        stop_event.set()
        for p in processes:
            p.join(timeout=1)
        return None
    finally:
        # Ensure all processes are terminated if still alive
        for p in processes:
            if p.is_alive():
                p.terminate()
                p.join()

if __name__ == "__main__":
    # Load precomputed table (16^i points)
    table = load_precomputed("precomputed_hex.txt")
    print(f"Loaded {len(table)} precomputed points.")

    target = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"  # replace with actual

    LOW = 2**134
    HIGH = 2**135 - 1

    # Use all available CPU cores
    num_cores = mp.cpu_count()
    print(f"Starting parallel search with {num_cores} workers...")

    result = parallel_find_match(target, table, LOW, HIGH,
                                 num_workers=num_cores,
                                 total_max_attempts=10**9)  # 1e9 total attempts across workers

    if result:
        k, r, exp = result
        print(f"\nSUCCESS: k = {k} (r = {r}, exponent = {exp}, 16^{exp} = {16**exp})")
    else:
        print("\nNo match found within attempt limit.")