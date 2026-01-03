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
# 4000000000000000000000000000000000
# 0001000000000000000000000000000000


# Decompress compressed public key
def decompress(pub_hex: str) -> Point:
    b = unhexlify(pub_hex)
    if len(b) != 33 or b[0] not in (0x02, 0x03):
        raise ValueError("Invalid compressed pubkey")
    x = int.from_bytes(b[1:], 'big')
    y_even = b[0] == 0x02
    alpha = (pow(x, 3, p) + secp256k1.b) % p
    beta = pow(alpha, (p + 1) // 4, p)
    y = beta if ((beta % 2 == 0) == y_even) else (p - beta)

    # on-curve check
    if (y * y - (pow(x, 3, p) + secp256k1.b)) % p != 0:
        raise ValueError("Point not on curve")

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

def neg(P: Point) -> Point:
    return Point(P.x, (-P.y) % p, curve=secp256k1)

outname = "output.txt"

##### Decompress target public key #####
target_point = decompress(target_hex)

#### target value for test #####
newseed = 0x1000000000000000000000000000000
point_newseed = newseed * G

need_point = target_point + neg(point_newseed)

# maximumi
maximum_hex = 0x8000000000000000000000000000000000
maximum_point = maximum_hex * G

# 2**135 unda gamovaklo target_hex
maximumsMinusTargetPoint = maximum_point + neg(target_point)
print("maximumsMinusTargetPoint:", compress(maximumsMinusTargetPoint))

# target_hex unda gamovaklo 0x7000..
minusSHVIDI_point = 0x7000000000000000000000000000000000 * G
minusSHVIDS_minus_shvidi = target_point + neg(minusSHVIDI_point)
print("minusSHVIDS_minus_shvidi:", compress(minusSHVIDS_minus_shvidi))

# amat vamatyeb ertmanetze
plius_plius = maximumsMinusTargetPoint + minusSHVIDS_minus_shvidi
print("plius_plius:", compress(plius_plius))

result_point = 0x1000000000000000000000000000000000 * G
print(compress(result_point))
print(compress(plius_plius))
if compress(result_point) == compress(plius_plius):
    print("Success: they are equal")
    print(f"\ndaemTxva")