import os
from example import *
import random

HIGH = 4355614296588012332331194975126633106636
LOW = 2177807148294006166165597487563316553318

# ---------- Your existing EC functions (assumed defined) ----------
# P_FIELD, N_ORDER, G, scalar_mult, pubkey_from_scalar, etc.

def generate_precomputed_hex(filename="precomputed_hex.txt", max_exponent=135):
    """
    Generate a file with precomputed points 16^i * G for i = 0..max_exponent.
    Each line: i <compressed_pubkey>
    """
    # Check if file already exists
    if os.path.exists(filename):
        print(f"File {filename} already exists. Overwrite? (y/n)")
        ans = input().strip().lower()
        if ans != 'y':
            print("Aborting.")
            return

    with open(filename, 'w') as f:
        for i in range(max_exponent + 1):
            # scalar = 2 ** i
            scalar = random.randint(LOW, HIGH)  
            # print(hex(scalar))
            # Optional: ensure scalar < N_ORDER (curve order)
            # if scalar >= N_ORDER:
            #     print(f"Stopping at i={i-1} because 16^{i} >= N_ORDER")
            #     break
            pub_hex = pubkey_from_scalar(scalar)
            # print(pub_hex)
            f.write(f"{scalar} {pub_hex}\n")
            # await() 
            # if i % 5 == 0:
            #     print(f"Generated i = {i} (16^{i} * G)")
    print(f"Done. Points saved to {filename}")

# Example: generate up to 16^40 (i=40)
if __name__ == "__main__":
    generate_precomputed_hex("precomputed_hex.txt", max_exponent=9000000)