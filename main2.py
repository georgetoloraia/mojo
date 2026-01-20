# owner: george toloraia
from fastecdsa.curve import secp256k1
from fastecdsa.point import Point
from binascii import unhexlify, hexlify
import base58

# Parameters
G = secp256k1.G
p = secp256k1.p
n = secp256k1.q
target_hex = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"


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


def neg(P: Point) -> Point:
    return Point(P.x, (-P.y) % p, curve=secp256k1)

outname = "output.txt"

##### Decompress target public key #####
target_point = decompress(target_hex)

# maximumi
maximum_hex = 0x8000000000000000000000000000000000
maximum_point = maximum_hex * G

# maxsimums vakleb loop it saTiTaod 0x1000...
# shemdeg targets vakleb 0x1000...
# magalitad
'''
7123

7123 - 1000 = 6123
6023 - 1000 = 5123
5023 - 1000 = 4123
4023 - 1000 = 3123
3023 - 1000 = 2123
2023 - 1000 = 1123

mere target-hex - 1000 # 7123 - 1000 = 6123
shemdeg 7123 - 6123 == 1000 eseigi raRac logikaas


'''