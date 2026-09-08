"""Q012h2a lossless finite binary values and precision-explicit diagnostics."""

import re

import gmpy2 as mp
import numpy as np

PRECISIONS = (128, 192)


def context(bits):
    if type(bits) is not int or bits not in PRECISIONS:
        raise ValueError("registered 128/192-bit precision required")
    return mp.context(
        precision=bits,
        real_prec=bits,
        imag_prec=bits,
        round=mp.RoundToNearest,
        real_round=mp.RoundToNearest,
        imag_round=mp.RoundToNearest,
    )


def exact64(values):
    values = np.asarray(values)
    if values.dtype != np.dtype("complex128") or not np.isfinite(values).all():
        raise ValueError("finite complex128 input required, without silent coercion")
    current = mp.get_context()
    if current.precision not in PRECISIONS or (current.real_prec, current.imag_prec) != (
        current.precision,
        current.precision,
    ):
        raise ValueError("binary64 inputs must be imported inside a registered precision context")
    return np.array([mp.mpc(complex(z)) for z in values.ravel()], dtype=object).reshape(
        values.shape
    )


def rounded(values):
    values = np.asarray(values, dtype=object)
    if not all(mp.is_finite(z) for z in values.flat):
        raise ValueError("nonfinite multiprecision coefficients")
    result = np.array([complex(z) for z in values.flat], dtype=np.complex128).reshape(values.shape)
    if not np.isfinite(result).all():
        raise ValueError("complex128 conversion overflow")
    return result


def binary(value):
    if not isinstance(value, mp.mpfr) or not mp.is_finite(value):
        raise ValueError("finite MPFR scalar required")
    mantissa, exponent = value.as_mantissa_exp()
    mantissa, exponent = int(mantissa), int(exponent)
    if mantissa == 0:
        return ["0", 0]
    shift = (abs(mantissa) & -abs(mantissa)).bit_length() - 1
    return [str(mantissa >> shift), exponent + shift]


def encode(values, bits):
    values = np.asarray(values, dtype=object)
    if values.ndim not in (1, 2) or values.size == 0:
        raise ValueError("nonempty MP vectors/matrices required")
    with context(bits):
        if not all(
            isinstance(z, mp.mpc) and z.precision == (bits, bits) and mp.is_finite(z)
            for z in values.flat
        ):
            raise ValueError("coefficient precision is not the recorded precision")
        return {
            "shape": list(values.shape),
            "bits": bits,
            "values": [[binary(z.real), binary(z.imag)] for z in values.flat],
        }


def decode_real(value, bits):
    if not (
        isinstance(value, list)
        and len(value) == 2
        and type(value[0]) is str
        and re.fullmatch(r"0|-?[1-9][0-9]*", value[0])
        and len(value[0]) <= 65
        and type(value[1]) is int
        and abs(value[1]) <= 16384
    ):
        raise ValueError("bounded canonical binary scalar required")
    mantissa, exponent = int(value[0]), value[1]
    if (
        (mantissa == 0 and exponent != 0)
        or (mantissa != 0 and mantissa % 2 == 0)
        or abs(mantissa).bit_length() > bits
    ):
        raise ValueError("noncanonical or overprecision mantissa")
    numerator = mantissa << max(0, exponent)
    denominator = 1 << max(0, -exponent)
    return mp.mpfr(mp.mpq(numerator, denominator), precision=bits)


def decode(record):
    if not isinstance(record, dict) or set(record) != {"shape", "bits", "values"}:
        raise ValueError("exact MP array schema required")
    shape, bits = record["shape"], record["bits"]
    if not (
        isinstance(shape, list)
        and len(shape) in (1, 2)
        and all(type(n) is int and 0 < n <= 100000 for n in shape)
        and isinstance(record["values"], list)
        and len(record["values"]) == np.prod(shape)
    ):
        raise ValueError("full MP array shape/coverage required")
    with context(bits):
        values = []
        for pair in record["values"]:
            if not isinstance(pair, list) or len(pair) != 2:
                raise ValueError("real/imaginary binary scalar pair required")
            values.append(mp.mpc(decode_real(pair[0], bits), decode_real(pair[1], bits)))
        result = np.array(values, dtype=object).reshape(shape)
        if encode(result, bits) != record:
            raise ValueError("MP value did not decode exactly")
        return result


def norm(vector):
    return mp.sqrt(sum((z.real * z.real + z.imag * z.imag for z in vector), mp.mpfr(0)))


def errors(actual, reference):
    """192-bit norm diagnostics even when both coefficient arrays are 128-bit."""
    actual, reference = (np.asarray(x, dtype=object) for x in (actual, reference))
    if (
        actual.shape != reference.shape
        or actual.ndim != 2
        or actual.shape[0] != 27
        or actual.shape[1] == 0
    ):
        raise ValueError("matching full population columns required")
    if not all(isinstance(z, mp.mpc) and mp.is_finite(z) for z in (*actual.flat, *reference.flat)):
        raise ValueError("finite MP columns required")
    with context(192):
        result = [
            norm(actual[:, i] - reference[:, i]) / max(mp.mpfr("1e-14"), norm(reference[:, i]))
            for i in range(actual.shape[1])
        ]
        return {
            "relative": [float(v) for v in result],
            "passed_1e8": [bool(v <= mp.mpfr("1e-8")) for v in result],
            "passed_1e10": [bool(v <= mp.mpfr("1e-10")) for v in result],
        }
