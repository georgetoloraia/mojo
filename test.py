from __future__ import annotations

from dataclasses import dataclass
from binascii import unhexlify

from fastecdsa.curve import secp256k1
from fastecdsa.point import Point


# --- Curve constants ---
G: Point = secp256k1.G
P_FIELD: int = secp256k1.p
B_CURVE: int = secp256k1.b  # secp256k1: y^2 = x^3 + 7 (mod p)


# --- EC helpers ---
def neg(pt: Point) -> Point:
    """Group inverse: (x, y) -> (x, -y mod p)."""
    return Point(pt.x, (-pt.y) % P_FIELD, curve=secp256k1)


def compress(pt: Point) -> str:
    """Compressed SEC1 pubkey hex: 02/03 + 32-byte x."""
    prefix = "02" if (pt.y % 2 == 0) else "03"
    return prefix + format(pt.x, "064x")


def decompress(pub_hex: str) -> Point:
    """Decompress a compressed secp256k1 pubkey hex into a Point."""
    raw = unhexlify(pub_hex)
    if len(raw) != 33 or raw[0] not in (0x02, 0x03):
        raise ValueError("Invalid compressed pubkey (need 33 bytes, prefix 02/03).")

    x = int.from_bytes(raw[1:], "big")
    want_even = (raw[0] == 0x02)

    alpha = (pow(x, 3, P_FIELD) + B_CURVE) % P_FIELD
    beta = pow(alpha, (P_FIELD + 1) // 4, P_FIELD)  # valid for secp256k1 (p % 4 == 3)
    y = beta if ((beta % 2 == 0) == want_even) else (P_FIELD - beta)

    # On-curve check
    if (y * y - (pow(x, 3, P_FIELD) + B_CURVE)) % P_FIELD != 0:
        raise ValueError("Point not on curve.")

    return Point(x, y, curve=secp256k1)


# --- Identity check harness ---
@dataclass(frozen=True)
class StepParams:
    name: str
    max_scalar: int  # A
    sub_scalar: int  # B


def run_step(step: StepParams, T: Point, *, verbose: bool = False) -> Point:
    """
    Validates: (A*G - T) + (T - B*G) == (A - B)*G
    Returns the expected (A - B)*G point, which you can reuse as "maximum" in a later step.
    """
    A = step.max_scalar
    B = step.sub_scalar

    left = (A * G) + neg(T)      # A*G - T
    right = T + neg(B * G)       # T - B*G
    combined = left + right      # (A-B)*G
    expected = (A - B) * G

    if verbose:
        print(f"\n=== {step.name} ===")
        print("A*G - T   :", compress(left))
        print("T - B*G   :", compress(right))
        print("combined  :", compress(combined))
        print("expected  :", compress(expected))

    if compress(combined) == compress(expected):
        print(f"Success: {step.name}")
    else:
        print(f"FAIL: {step.name}")
        print("combined :", compress(combined))
        print("expected :", compress(expected))

    return expected


def main() -> None:
    target_hex = "02145d2611c823a396ef6712ce0f712f09b9b4f3135e3e0aa3230fb9b6d08d1e16"
    T0 = decompress(target_hex)

    # STEP 1: choose A and B consistently (same magnitude class)
    step1 = StepParams(
        name="STEP-1",
        max_scalar=0x8000000000000000000000000000000000,
        sub_scalar=0x7000000000000000000000000000000000,
    )
    T1 = run_step(step1, T0, verbose=True)  # This returns (A-B)*G

    # STEP 2: Now treat T := (T0 - B1*G) OR any point you intend, but keep identity consistent.
    # In your latest code, you set:
    #   maximum_point_2 = result_point  (which is T1)
    #   target_point_2  = minusSHVIDS_minus_shvidi (which equals T0 - B1*G)
    #
    # That matches running the same identity again with T = (T0 - B1*G).
    T_target_2 = T0 + neg(step1.sub_scalar * G)  # equals: T0 - B1*G

    step2 = StepParams(
        name="STEP-2",
        max_scalar=(step1.max_scalar - step1.sub_scalar),  # A2 == T1 scalar
        sub_scalar=0x700000000000000000000000000000000,
    )
    _T2 = run_step(step2, T_target_2, verbose=True)


if __name__ == "__main__":
    main()
