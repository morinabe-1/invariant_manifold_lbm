"""Two independent exact residual kernels for fixed binary64 Sylvester problems."""

from __future__ import annotations

import math
import struct
from fractions import Fraction

import gmpy2
import numpy as np

from research import d3q27_cubic_precision as precision
from research import q012a_d3q27_foundation as q012a

TOLERANCE, FLOOR = 1e-10, 1e-14
EXACT_GATES = (
    "exact_residual_stored_denominator",
    "exact_residual_exact_denominator",
    "exact_decimal_constants",
)
ARRAY_NAMES = ("a", "d", "f", "x", "r64", "r128")


def validate_arrays(a, d, f, x, r64, r128):
    arrays = tuple(np.asarray(v, dtype=np.complex128) for v in (a, d, f, x, r64, r128))
    aa, dd, ff, xx, low, high = arrays
    if aa.ndim != 2 or dd.ndim != 2 or aa.shape[0] == 0 or dd.shape[0] == 0:
        raise ValueError("nonempty square dynamics matrices are required")
    expected = (aa.shape[0], dd.shape[0])
    if (
        aa.shape[0] != aa.shape[1]
        or dd.shape[0] != dd.shape[1]
        or any(v.shape != expected for v in (ff, xx, low, high))
    ):
        raise ValueError("incompatible Sylvester matrix shapes")
    if not all(np.all(np.isfinite(v)) for v in arrays):
        raise ValueError("only finite binary64 inputs are accepted")
    return arrays


def rational_record(value):
    return [str(value.numerator), str(value.denominator)]


def rational(value):
    return Fraction(int(value[0]), int(value[1]))


def digest_residual(real, imag):
    return q012a._digest(
        {
            "shape": list(real.shape),
            "real": [rational_record(v) for v in real.ravel()],
            "imag": [rational_record(v) for v in imag.ravel()],
        }
    )


def approximate_root(value):
    # Display only. All decisions below use rational squared norms.
    try:
        return math.sqrt(float(value))
    except OverflowError:
        return None


def report(norms, residual_digest, shape, r64, stored_denominator):
    if not math.isfinite(stored_denominator) or stored_denominator <= 0:
        raise ValueError("a positive finite stored denominator is required")
    exact = {
        key: Fraction(int(value.numerator), int(value.denominator)) for key, value in norms.items()
    }
    tolerance = Fraction.from_float(TOLERANCE)
    floor = Fraction.from_float(FLOOR)
    denominator2 = Fraction.from_float(float(stored_denominator)) ** 2
    exact_denominator2 = max(floor**2, exact["forcing_norm_squared"])
    decimal_denominator2 = max(Fraction(1, 10**28), exact["forcing_norm_squared"])
    legacy = float(np.linalg.norm(r64) / stored_denominator)
    rr = exact["exact_residual_norm_squared"]
    gates = {
        "legacy": legacy <= TOLERANCE,
        "rounded_vector_exact_norm": exact["rounded_residual_norm_squared"]
        <= tolerance**2 * denominator2,
        "exact_residual_stored_denominator": rr <= tolerance**2 * denominator2,
        "exact_residual_exact_denominator": rr <= tolerance**2 * exact_denominator2,
        "exact_decimal_constants": rr <= Fraction(1, 10**20) * decimal_denominator2,
    }
    return {
        "shape": list(shape),
        "residual_digest_sha256": residual_digest,
        "norms_squared": {key: rational_record(value) for key, value in exact.items()},
        "stored_denominator_squared": rational_record(denominator2),
        "exact_denominator_squared": rational_record(exact_denominator2),
        "decimal_denominator_squared": rational_record(decimal_denominator2),
        "binary_tolerance_squared": rational_record(tolerance**2),
        "legacy_relative_residual": legacy,
        "gates": gates,
        "evaluation_only_mismatch": not gates["legacy"]
        and not gates["rounded_vector_exact_norm"]
        and all(gates[k] for k in EXACT_GATES),
        "mp128_agrees": exact["evaluation128_error_squared"]
        <= Fraction(1, 10**48) * exact_denominator2,
        "approximate_relative_norms": {
            "exact_residual": approximate_root(rr / exact_denominator2),
            "evaluation64_error": approximate_root(
                exact["evaluation64_error_squared"] / exact_denominator2
            ),
            "evaluation128_error": approximate_root(
                exact["evaluation128_error_squared"] / exact_denominator2
            ),
        },
    }


def gmp_parts(value):
    real = np.empty(value.shape, dtype=object)
    imag = np.empty_like(real)
    for index in np.ndindex(value.shape):
        real[index] = gmpy2.mpq(*float(value[index].real).as_integer_ratio())
        imag[index] = gmpy2.mpq(*float(value[index].imag).as_integer_ratio())
    return real, imag


def gmp_norm2(real, imag):
    return sum(
        (r * r + i * i for r, i in zip(real.ravel(), imag.ravel(), strict=True)), gmpy2.mpq(0)
    )


def audit_gmp(a, d, f, x, r64, r128, stored_denominator):
    arrays = validate_arrays(a, d, f, x, r64, r128)
    (ar, ai), (dr, di), (fr, fi), (xr, xi), (lr, li), (hr, hi) = map(gmp_parts, arrays)
    rr = ar @ xr - ai @ xi - xr @ dr + xi @ di + fr
    ri = ar @ xi + ai @ xr - xr @ di - xi @ dr + fi
    norms = {
        "forcing_norm_squared": gmp_norm2(fr, fi),
        "exact_residual_norm_squared": gmp_norm2(rr, ri),
        "rounded_residual_norm_squared": gmp_norm2(lr, li),
        "mp128_residual_norm_squared": gmp_norm2(hr, hi),
        "evaluation64_error_squared": gmp_norm2(lr - rr, li - ri),
        "evaluation128_error_squared": gmp_norm2(hr - rr, hi - ri),
    }
    return report(norms, digest_residual(rr, ri), rr.shape, arrays[4], stored_denominator)


def binary64_parts(value):
    """Independent IEEE754 decoding; deliberately does not use as_integer_ratio."""
    bits = struct.unpack("<Q", struct.pack("<d", float(value)))[0]
    exponent = (bits >> 52) & 0x7FF
    mantissa = bits & ((1 << 52) - 1)
    if exponent == 0x7FF:
        raise ValueError("nonfinite IEEE754 value")
    if exponent:
        mantissa |= 1 << 52
        shift = exponent - 1023 - 52
    else:
        shift = -1074
    if bits >> 63:
        mantissa = -mantissa
    if mantissa == 0:
        return 0, 0
    return (mantissa << shift, 0) if shift >= 0 else (mantissa, -shift)


def integer_parts(value):
    decoded = [(binary64_parts(z.real), binary64_parts(z.imag)) for z in value.ravel()]
    exponent = max(e for pair in decoded for _, e in pair)
    real = np.array([r << (exponent - e) for (r, e), _ in decoded], dtype=object).reshape(
        value.shape
    )
    imag = np.array([i << (exponent - e) for _, (i, e) in decoded], dtype=object).reshape(
        value.shape
    )
    return real, imag, exponent


def integer_norm2(real, imag, exponent):
    numerator = sum(
        int(r) ** 2 + int(i) ** 2 for r, i in zip(real.ravel(), imag.ravel(), strict=True)
    )
    return Fraction(numerator, 1 << (2 * exponent))


def integer_difference(left, right):
    lr, li, le = left
    rr, ri, re = right
    common = max(le, re)
    return (
        lr * (1 << (common - le)) - rr * (1 << (common - re)),
        li * (1 << (common - le)) - ri * (1 << (common - re)),
        common,
    )


def audit_integer(a, d, f, x, r64, r128, stored_denominator):
    # Conversion, products, and squared-norm accumulation are independent of the GMP kernel.
    arrays = validate_arrays(a, d, f, x, r64, r128)
    aa, dd, ff, xx, low, high = map(integer_parts, arrays)
    ar, ai, ae = aa
    dr, di, de = dd
    fr, fi, fe = ff
    xr, xi, xe = xx
    common = max(ae + xe, xe + de, fe)
    rr = (
        (ar @ xr - ai @ xi) * (1 << (common - ae - xe))
        - (xr @ dr - xi @ di) * (1 << (common - xe - de))
        + fr * (1 << (common - fe))
    )
    ri = (
        (ar @ xi + ai @ xr) * (1 << (common - ae - xe))
        - (xr @ di + xi @ dr) * (1 << (common - xe - de))
        + fi * (1 << (common - fe))
    )
    result = (rr, ri, common)
    norms = {
        "forcing_norm_squared": integer_norm2(*ff),
        "exact_residual_norm_squared": integer_norm2(*result),
        "rounded_residual_norm_squared": integer_norm2(*low),
        "mp128_residual_norm_squared": integer_norm2(*high),
        "evaluation64_error_squared": integer_norm2(*integer_difference(low, result)),
        "evaluation128_error_squared": integer_norm2(*integer_difference(high, result)),
    }
    real = np.array([Fraction(int(v), 1 << common) for v in rr.ravel()], dtype=object).reshape(
        rr.shape
    )
    imag = np.array([Fraction(int(v), 1 << common) for v in ri.ravel()], dtype=object).reshape(
        ri.shape
    )
    return report(norms, digest_residual(real, imag), rr.shape, arrays[4], stored_denominator)


def control_problems():
    problems = []
    a = np.array([[0.5, 0.25j], [-0.125j, 0.75]])
    d = np.array([[0.25, 0.125], [0, 0.5]])
    x = np.array([[1 + 2j, -0.5j], [0.75, -1]])
    problems.append(("complex_exact_solution", a, d, x @ d - a @ x, x, True, True))
    a = np.array([[1 + 2**-52]], dtype=complex)
    problems.append(
        (
            "lost_product_bits",
            a,
            np.zeros((1, 1)),
            np.array([[-(1 + 2**-51)]]),
            a.copy(),
            True,
            True,
        )
    )
    zero = np.zeros((1, 1))
    problems.append(("zero_forcing", zero, zero, zero, zero, True, True))
    tiny = np.array([[np.nextafter(0.0, 1.0)]])
    problems.append(("subnormal_product", tiny, zero, zero, tiny, True, True))
    for name, value, binary, decimal in (
        ("inside", np.nextafter(TOLERANCE, 0), True, True),
        ("binary_boundary", TOLERANCE, True, False),
        ("outside", np.nextafter(TOLERANCE, np.inf), False, False),
    ):
        problems.append(
            (
                name,
                np.zeros((2, 2)),
                np.ones((1, 1)),
                np.array([[1.0], [0.0]]),
                np.array([[1.0], [value]]),
                binary,
                decimal,
            )
        )
    problems.append(
        (
            "decimal_boundary",
            np.zeros((2, 2)),
            np.ones((1, 1)),
            np.array([[1e10], [0.0]]),
            np.array([[1e10], [-1.0]]),
            True,
            True,
        )
    )
    problems.append(
        (
            "false_float_acceptance",
            np.array([[1.0, 1.0], [0.0, 1.0]]),
            np.ones((1, 1)),
            np.zeros((2, 1)),
            np.array([[2.0**54], [1.0]]),
            False,
            False,
        )
    )
    problems.append(
        (
            "false_float_rejection",
            np.array([[1.0, 1.0], [0.0, 1.0]]),
            np.ones((1, 1)),
            np.array([[-1.0], [0.0]]),
            np.array([[2.0**54], [1.0]]),
            True,
            True,
        )
    )
    return problems


def known_controls():
    records = []
    for name, a, d, f, x, binary, decimal in control_problems():
        arrays = [np.asarray(v, dtype=complex) for v in (a, d, f, x)]
        a, d, f, x = arrays
        low = a @ x - x @ d + f
        high = precision.residual_mpc(a, d, f, x)
        denominator = max(FLOOR, float(np.linalg.norm(f)))
        first = audit_gmp(a, d, f, x, low, high, denominator)
        second = audit_integer(a, d, f, x, low, high, denominator)
        checks = {
            "independent_equal": first == second,
            "binary_expected": all(first["gates"][k] == binary for k in EXACT_GATES[:2]),
            "decimal_expected": first["gates"]["exact_decimal_constants"] == decimal,
            "mp128_agrees": first["mp128_agrees"],
        }
        if name == "false_float_acceptance":
            checks["legacy_false_acceptance_exposed"] = (
                first["gates"]["legacy"] and not first["gates"]["exact_residual_exact_denominator"]
            )
        if name == "false_float_rejection":
            checks["legacy_false_rejection_exposed"] = first["evaluation_only_mismatch"]
        if name == "lost_product_bits":
            checks["exact_nonzero_product"] = rational(
                first["norms_squared"]["exact_residual_norm_squared"]
            ) == Fraction(1, 2**208)
        if name == "subnormal_product":
            checks["subnormal_exact_nonzero"] = rational(
                first["norms_squared"]["exact_residual_norm_squared"]
            ) == Fraction(1, 2**4296)
        records.append(
            {"name": name, "proof": first, "checks": checks, "passed": all(checks.values())}
        )
    return {"records": records, "passed": all(r["passed"] for r in records)}
