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

# 2**135 unda gamovaklo target_hex
maximumsMinusTargetPoint = maximum_point + neg(target_point)
# print("maximumsMinusTargetPoint:", compress(maximumsMinusTargetPoint))

# target_hex unda gamovaklo 0x7000..
minusSHVIDI_point = 0x7000000000000000000000000000000000 * G
minusSHVIDS_minus_shvidi = target_point + neg(minusSHVIDI_point)
# print("minusSHVIDS_minus_shvidi:", compress(minusSHVIDS_minus_shvidi))

# amat vamatyeb ertmanetze
plius_plius = maximumsMinusTargetPoint + minusSHVIDS_minus_shvidi
# print("plius_plius:", compress(plius_plius))

result_point = 0x1000000000000000000000000000000000 * G
# print(compress(result_point))
# print(compress(plius_plius))
if compress(result_point) == compress(plius_plius):
    print("Success: they are equal")
    print("Success STEP-1")

################### S T E P - 2 #################################
#################################################################
#0x7
maximum_point_2 = result_point
target_point_2 = minusSHVIDS_minus_shvidi

# 2**135 unda gamovaklo target_hex
maximumsMinusTargetPoint_2 = maximum_point_2 + neg(target_point_2)
# print("maximumsMinusTargetPoint:", compress(maximumsMinusTargetPoint))

# target_hex unda gamovaklo 0x7000..
minusSHVIDI_point_2 = 0xf00000000000000000000000000000000 * G
minusSHVIDS_minus_shvidi_2 = target_point_2 + neg(minusSHVIDI_point_2)
# print("minusSHVIDS_minus_shvidi:", compress(minusSHVIDS_minus_shvidi))

# amat vamatyeb ertmanetze
plius_plius_2 = maximumsMinusTargetPoint_2 + minusSHVIDS_minus_shvidi_2
# print("plius_plius:", compress(plius_plius_2))

result_point_2 = 0x100000000000000000000000000000000 * G
# print(compress(result_point_2))
# print(compress(plius_plius_2))
if compress(result_point_2) == compress(plius_plius_2):
    print("Success: they are equal")
    print("Success STEP-2")

################### STEP 3 ##########################
#####################################################
# 0x7f

maximum_point_3 = result_point_2
target_point_3 = minusSHVIDS_minus_shvidi_2

# 2**135 unda gamovaklo target_hex
maximumsMinusTargetPoint_3 = maximum_point_3 + neg(target_point_3)
# print("maximumsMinusTargetPoint:", compress(maximumsMinusTargetPoint))

# target_hex unda gamovaklo 0x7000..
minusSHVIDI_point_3 = 0xf0000000000000000000000000000000 * G
minusSHVIDS_minus_shvidi_3 = target_point_3 + neg(minusSHVIDI_point_3)
# print("minusSHVIDS_minus_shvidi:", compress(minusSHVIDS_minus_shvidi))

# amat vamatyeb ertmanetze
plius_plius_3 = maximumsMinusTargetPoint_3 + minusSHVIDS_minus_shvidi_3
# print("plius_plius:", compress(plius_plius_2))

result_point_3 = 0x10000000000000000000000000000000 * G
# print(compress(result_point_3))
# print(compress(plius_plius_2))
if compress(result_point_3) == compress(plius_plius_3):
    print("Success: they are equal")
    print("Success STEP-3")

############### STEP 4 ##########################
#####################################################
# 0x7ff or 0x7f0f

maximum_point_4 = result_point_3
target_point_4 = minusSHVIDS_minus_shvidi_3

# 2**135 unda gamovaklo target_hex
maximumsMinusTargetPoint_4 = maximum_point_4 + neg(target_point_4)
# print("maximumsMinusTargetPoint:", compress(maximumsMinusTargetPoint))

# target_hex unda gamovalo 0x7000..
minusSHVIDI_point_4 = 0xf000000000000000000000000000000 * G
minusSHVIDS_minus_shvidi_4 = target_point_4 + neg(minusSHVIDI_point_4)
# print("minusSHVIDS_minus_shvidi:", compress(minusSHVIDS_minus_shvidi))

# amat vamatyeb ertmanetze
plius_plius_4 = maximumsMinusTargetPoint_4 + minusSHVIDS_minus_shvidi_4
# print("plius_plius:", compress(plius_plius_2))

result_point_4 = 0x1000000000000000000000000000000 * G
# print(compress(result_point_3))
# print(compress(plius_plius_2))
if compress(result_point_4) == compress(plius_plius_4):
    print("Success: they are equal")
    print("Success STEP-4")