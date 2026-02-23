"""
Small secp256k1 playground for compressed public-key math.

Use this file to experiment with:
- point addition:   P + Q
- point subtraction: P - Q
- scalar multiplication: k * G

This is a pure-Python educational implementation (not optimized).
"""

P_FIELD = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
N_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (Gx, Gy)
INF = None


def mod_inv(a: int, m: int) -> int:
    return pow(a, -1, m)


def is_on_curve(point) -> bool:
    if point is INF:
        return True
    x, y = point
    return (y * y - (pow(x, 3, P_FIELD) + 7)) % P_FIELD == 0


def point_neg(point):
    if point is INF:
        return INF
    x, y = point
    return (x, (-y) % P_FIELD)


def point_add(a, b):
    if a is INF:
        return b
    if b is INF:
        return a

    x1, y1 = a
    x2, y2 = b

    if x1 == x2 and (y1 + y2) % P_FIELD == 0:
        return INF

    if a == b:
        # Tangent slope for point doubling.
        lam = (3 * x1 * x1) * mod_inv((2 * y1) % P_FIELD, P_FIELD)
    else:
        # Chord slope for point addition.
        lam = (y2 - y1) * mod_inv((x2 - x1) % P_FIELD, P_FIELD)

    lam %= P_FIELD
    x3 = (lam * lam - x1 - x2) % P_FIELD
    y3 = (lam * (x1 - x3) - y1) % P_FIELD
    return (x3, y3)


def scalar_mult(k: int, point=G):
    if point is INF or k % N_ORDER == 0:
        return INF
    if k < 0:
        return scalar_mult(-k, point_neg(point))

    result = INF
    addend = point

    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1

    return result


def decompress_pubkey(pub_hex: str):
    raw = bytes.fromhex(pub_hex)
    if len(raw) != 33 or raw[0] not in (2, 3):
        raise ValueError("Expected compressed secp256k1 pubkey (33 bytes)")

    x = int.from_bytes(raw[1:], "big")
    alpha = (pow(x, 3, P_FIELD) + 7) % P_FIELD
    beta = pow(alpha, (P_FIELD + 1) // 4, P_FIELD)  # p % 4 == 3
    y_even = raw[0] == 2
    y = beta if ((beta % 2 == 0) == y_even) else (P_FIELD - beta)
    point = (x, y)

    if not is_on_curve(point):
        raise ValueError("Compressed pubkey does not decode to a curve point")
    return point


def compress_pubkey(point) -> str:
    if point is INF:
        return "INF"
    x, y = point
    return ("02" if y % 2 == 0 else "03") + format(x, "064x")


def add_pubkeys(pubkey_a: str, pubkey_b: str) -> str:
    a = decompress_pubkey(pubkey_a)
    b = decompress_pubkey(pubkey_b)
    return compress_pubkey(point_add(a, b))


def subtract_pubkeys(pubkey_a: str, pubkey_b: str) -> str:
    a = decompress_pubkey(pubkey_a)
    b = decompress_pubkey(pubkey_b)
    return compress_pubkey(point_add(a, point_neg(b)))


def pubkey_from_scalar(k: int) -> str:
    if not (0 <= k < N_ORDER):
        raise ValueError("Scalar must be in range 0 <= k < n")
    return compress_pubkey(scalar_mult(k, G))


if __name__ == "__main__":
    # ====================== STEP 1: WHERE I NEED FIND FIRST CHAR FOR ORIGINAL POINT ======================
    # Example usage: 7xx + 100 = 8000 [this is a example only, not actual math]
    # current_point = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16" 
    # test_plius = "02e4f3fb0176af85d65ff99ff9198c36091f48e86503681e3e6686fd5053231e11"
    '''
    current_point           = 02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16
    test_plius              = 02e4f3fb0176af85d65ff99ff9198c36091f48e86503681e3e6686fd5053231e11
    current_point + test    = 03249b09c8ad975a5ce73af7a7dfe53fb8eb59de40680c7cd44eb91ebb3ea3f209
    current_point - test    = 02e3d171ac16b58a231f45cdaa48be38d77b551738263757cb966f9b07b314c1f3
    '''

    # Example: now 8xxx - 8000 = 7[xxx] (I think removed first 1 character from 7xxx and == xxx)
    # current_point = "03249b09c8ad975a5ce73af7a7dfe53fb8eb59de40680c7cd44eb91ebb3ea3f209"    # 7xxx + 100 = 8xxx
    # test_plius = "02f478056d9c102c1cd06d7b1e7557244c6d9cdac5874610e94d4786e106de12c0"       # 8000
    '''
    current_point           = 03249b09c8ad975a5ce73af7a7dfe53fb8eb59de40680c7cd44eb91ebb3ea3f209
    test_plius              = 02f478056d9c102c1cd06d7b1e7557244c6d9cdac5874610e94d4786e106de12c0 # 8000
    current_point + test    = 02830fbb58f673b28d0e79996fbe283c62148833bac2a80570db0655417675fe8c
    current_point - test    = 03170ce536294fab6c0e8eee99b8cf215b672aa691b303707b11befed7e145f4ca
    '''

    # Example: now 7xxx - 7000 if == 7[xxx]
    # current_point = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"
    # test_plius =  "03d93f4d031232f60a48ef3a5776cba4e83772f8a59292292c647e18b9b2d64feb" # 7000
    '''
    current_point           = 02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16
    test_plius              = 03d93f4d031232f60a48ef3a5776cba4e83772f8a59292292c647e18b9b2d64feb
    current_point + test    = 0217307ea2da8fcbd5090a74ae33e1ced13a2e1c5f8bde567204a411dbcce4b3f6
    current_point - test    = 03170ce536294fab6c0e8eee99b8cf215b672aa691b303707b11befed7e145f4ca

    this example shows that original point starts 7
    '''

    # ====================== STEP 2: WHERE I NEED FIND SECOND CHAR FOR ORIGINAL POINT ======================
    # Example: now [xxx] + 100 = ?xx
    # 100... + [xxx] = 1xxx 028f68b9d2f63b5f339239c1ad981f162ee88c5678723ea3351b7b444c9ec4c0da
    current_point = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"   # 7 ჩამოშორებულით [xxx]
    test_plius = "02e4f3fb0176af85d65ff99ff9198c36091f48e86503681e3e6686fd5053231e11" # unda gavagrdzelo e0000 idan




    current_point_test_plius = add_pubkeys(current_point, test_plius)
    current_point_minus_test_plius = subtract_pubkeys(current_point, test_plius)

    print("current_point           =", current_point)
    print("test_plius              =", test_plius)
    print("current_point + test    =", current_point_test_plius)
    print("current_point - test    =", current_point_minus_test_plius)

    # Extra examples (uncomment as needed):
    # print("G =", pubkey_from_scalar(1))
    # print("2G =", pubkey_from_scalar(2))
    # print("3G =", pubkey_from_scalar(3))
