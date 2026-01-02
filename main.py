# owner: george toloraia

import subprocess
import os
import re
from fastecdsa.curve import secp256k1
from fastecdsa.point import Point
from binascii import unhexlify, hexlify
from random import randint
import hashlib
import base58

# Parameters
G = secp256k1.G
p = secp256k1.p
n = secp256k1.q
target_hex = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"

# Decompress compressed public key
def decompress(pub_hex: str) -> Point:
    b = unhexlify(pub_hex)
    x = int.from_bytes(b[1:], 'big')
    y_even = b[0] == 0x02
    alpha = (x ** 3 + secp256k1.b) % p
    beta = pow(alpha, (p + 1) // 4, p)
    y = beta if (beta % 2 == 0) == y_even else p - beta
    return Point(x, y, curve=secp256k1)

# Compress point to pubkey hex
def compress(P: Point) -> str:
    prefix = '02' if P.y % 2 == 0 else '03'
    return prefix + format(P.x, '064x')

# Convert private key to WIF (compressed=True)
def priv_to_wif(privkey_int, compressed=True) -> str:
    priv_bytes = privkey_int.to_bytes(32, 'big')
    prefix = b'\x80' + priv_bytes + (b'\x01' if compressed else b'')
    checksum = hashlib.sha256(hashlib.sha256(prefix).digest()).digest()[:4]
    wif = base58.b58encode(prefix + checksum)
    return wif.decode()