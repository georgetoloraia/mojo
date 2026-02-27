import os
from example import pubkey_from_scalar  # Assumes this function returns a compressed pubkey hex string

def generate_power_of_16_multiples(filename="precomputed_hex.txt", max_hex="0x1000000000000000000000000000000000"):
    """
    Generate public keys for exponents of the form d * 16^k,
    where d = 1..15 and k = 1..max_k, with 16^k <= max_hex.
    Saves each line as "exponent pubkey_hex".
    """
    # Convert the maximum hex value to an integer
    max_val = int(max_hex, 16)

    # Determine the largest k such that 16**k <= max_val
    k = 1
    while True:
        power = 16 ** k
        if power > max_val:
            break
        k += 1
    max_k = k - 1
    print(f"Maximum k: {max_k} (16^{max_k} = {hex(16**max_k)})")

    # Check if the output file already exists
    if os.path.exists(filename):
        print(f"File {filename} already exists. Overwrite? (y/n)")
        ans = input().strip().lower()
        if ans != 'y':
            print("Aborting.")
            return

    total = 0
    with open(filename, 'w') as f:
        for k in range(1, max_k + 1):
            base = 16 ** k
            for d in range(1, 16):          # hex digits 1..F
                exp = d * base
                pub = pubkey_from_scalar(exp)
                f.write(f"{exp} {pub}\n")
                total += 1
                if total % 100 == 0:
                    print(f"Generated {total} entries...")
        print(f"Done. Generated {total} points saved to {filename}")

if __name__ == "__main__":
    generate_power_of_16_multiples()