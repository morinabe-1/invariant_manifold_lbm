"""Exact sums of existing binary64 fields, not an exact-real LBM simulator.

Q012g1 preserves the original chart/map and its failures. Integer exponent bins
and a separate GMP rational loop audit only the arithmetic of conserved sums.
"""

from __future__ import annotations

import re
from fractions import Fraction
from math import isfinite, prod
from numbers import Integral

import gmpy2
import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as chart

CHUNK_SIZE = 1024
BACKENDS = ("integer", "gmp")
THRESHOLD_FLOAT = 5e-13
THRESHOLD = Fraction.from_float(THRESHOLD_FLOAT)
DELTA = 2.0**-36
MOMENTS = np.vstack((np.ones(27, dtype=np.int64), d3.VELOCITIES.T))
MOMENTS.setflags(write=False)


def _values(values):
    raw = np.asarray(values)
    if raw.dtype != np.dtype(np.float64):
        raise TypeError("native binary64 values are required without conversion")
    if not np.all(np.isfinite(raw)):
        raise ValueError("nonfinite values cannot be exactly summed")
    return np.ascontiguousarray(raw).ravel()


def exact_sum(values, *, backend="integer") -> Fraction:
    """Sum every input value exactly; no floating-point accumulation or cutoff."""
    if backend not in BACKENDS:
        raise ValueError("unregistered exact summation backend")
    value = _values(values)
    if backend == "gmp":
        total = gmpy2.mpq(0)
        for entry in value:
            total += gmpy2.mpq(*float(entry).as_integer_ratio())
        return Fraction(int(total.numerator), int(total.denominator))
    bits = value.view(np.uint64)
    exponents = (bits >> 52) & 0x7FF
    mantissas = (bits & ((1 << 52) - 1)).astype(np.int64)
    mantissas[exponents != 0] |= 1 << 52
    mantissas[(bits >> 63) != 0] *= -1
    total = 0
    for exponent in np.unique(exponents):
        terms = mantissas[exponents == exponent]
        # Each signed mantissa is at most 2^53 - 1 in magnitude. Every partial
        # sum has <= 1024 terms, hence magnitude <= 2^63 - 1024 < int64 max.
        starts = np.arange(0, len(terms), CHUNK_SIZE)
        partials = np.add.reduceat(terms, starts, dtype=np.int64)
        subtotal = sum(int(partial) for partial in partials)
        total += subtotal << (int(exponent) - 1 if exponent else 0)
    return Fraction(total, 1 << 1074)


def exact_float(value) -> Fraction:
    if isinstance(value, (bool, str, bytes)):
        raise TypeError("a finite real numeric value is required")
    converted = float(value)
    if not isfinite(converted):
        raise ValueError("nonfinite legacy value")
    return Fraction.from_float(converted)


def encode(value: Fraction) -> dict:
    value = Fraction(value)
    try:
        approximation = float(value)
    except OverflowError as exc:
        raise ValueError("exact value has no finite display approximation") from exc
    if not isfinite(approximation):
        raise ValueError("nonfinite exact-value display approximation")
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "float": approximation,
    }


def decode(value: dict) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator", "float"}:
        raise ValueError("an exact value needs canonical numerator, denominator and display")
    if not isinstance(value["numerator"], str) or not isinstance(value["denominator"], str):
        raise TypeError("exact integers must be decimal strings")
    numerator, denominator = int(value["numerator"]), int(value["denominator"])
    if denominator <= 0:
        raise ValueError("positive exact denominator required")
    result = Fraction(numerator, denominator)
    if encode(result) != value or isinstance(value["float"], bool):
        raise ValueError("noncanonical or inaccurate exact-value record")
    return result


def conserved_from_populations(populations):
    if len(populations) != 27 or not all(isinstance(v, Fraction) for v in populations):
        raise ValueError("all 27 exact population sums are required")
    return tuple(
        sum((int(c) * v for c, v in zip(row, populations, strict=True)), Fraction(0))
        for row in MOMENTS
    )


def field_record(field, *, backend="integer"):
    raw = np.asarray(field)
    if raw.ndim != 4 or raw.shape[-1] != 27 or min(raw.shape[:3]) <= 0:
        raise ValueError("a nonempty (nz, ny, nx, 27) field is required")
    _values(raw)
    populations = tuple(exact_sum(raw[..., q], backend=backend) for q in range(27))
    conserved = conserved_from_populations(populations)
    legacy = d3.global_conserved_quantities(raw)
    sites = prod(raw.shape[:3])
    return {
        "array": chart.array_metadata(raw),
        "site_count": sites,
        "coverage": {"populations": 27, "sites_per_population": sites, "values": sites * 27},
        "population_sums": [encode(v) for v in populations],
        "conserved_sums": [encode(v) for v in conserved],
        "legacy_conserved_sums": legacy.tolist(),
        "sum_rounding": [
            encode(exact_float(v) - s) for v, s in zip(legacy, conserved, strict=True)
        ],
    }


def validate_field_record(record):
    array = record["array"]
    shape = array["shape"]
    if (
        len(shape) != 4
        or shape[-1] != 27
        or any(isinstance(n, bool) or not isinstance(n, int) or n <= 0 for n in shape)
        or array["dtype"] != np.dtype(np.float64).str
        or array["bytes"] != prod(shape) * 8
        or re.fullmatch("[0-9a-f]{64}", array["sha256"]) is None
    ):
        raise ValueError("invalid exact-field array witness")
    sites = prod(shape[:3])
    if record["site_count"] != sites or record["coverage"] != {
        "populations": 27,
        "sites_per_population": sites,
        "values": sites * 27,
    }:
        raise ValueError("incomplete exact-field coverage")
    populations = tuple(map(decode, record["population_sums"]))
    conserved = conserved_from_populations(populations)
    if tuple(map(decode, record["conserved_sums"])) != conserved:
        raise ValueError("exact population sums disagree with conserved moments")
    legacy = record["legacy_conserved_sums"]
    if len(legacy) != 4 or len(record["sum_rounding"]) != 4:
        raise ValueError("all four conserved components are required")
    expected = tuple(exact_float(v) - s for v, s in zip(legacy, conserved, strict=True))
    if tuple(map(decode, record["sum_rounding"])) != expected:
        raise ValueError("stored sum-rounding contribution is inconsistent")
    return True


def decompose_component(sa, sb, la, lb, global_error, mean_error, sites, *, leaf):
    """Exact identity for the ORIGINAL signed errors, plus two sum-only alternatives."""
    if isinstance(sites, bool) or not isinstance(sites, Integral) or sites <= 0:
        raise ValueError("positive integer site count required")
    if not isinstance(sa, Fraction) or not isinstance(sb, Fraction):
        raise TypeError("exact field sums must be rational")
    laq, lbq = exact_float(la), exact_float(lb)
    dl, el = exact_float(global_error), exact_float(mean_error)
    if float(np.float64(la) - np.float64(lb)) != global_error:
        raise ValueError("legacy global difference was not faithfully reproduced")
    if float(np.float64(global_error) / sites) != mean_error:
        raise ValueError("legacy site-average difference was not faithfully reproduced")
    terms = {
        "exact_field_error": (sa - sb) / sites,
        "sum_rounding_A": (laq - sa) / sites,
        "sum_rounding_minus_B": -(lbq - sb) / sites,
        "sum_rounding": ((laq - sa) - (lbq - sb)) / sites,
        "sub_rounding": (dl - (laq - lbq)) / sites,
        "mean_rounding": el - dl / sites,
    }
    identity = (
        sum(
            terms[k] for k in ("exact_field_error", "sum_rounding", "sub_rounding", "mean_rounding")
        )
        == el
    )

    def alternative(a, b):
        difference = float(np.float64(a) - np.float64(b))
        mean = float(np.float64(difference) / sites)
        if not isfinite(difference) or not isfinite(mean):
            raise ValueError("nonfinite sum-only alternative")
        return {
            "global_error": difference,
            "site_average_error": mean,
            "passed": abs(mean) <= THRESHOLD_FLOAT,
        }

    return {
        "terms": {k: encode(v) for k, v in terms.items()},
        "legacy_global_error": float(global_error),
        "legacy_site_average_error": float(mean_error),
        "legacy_passed": bool(abs(mean_error) <= THRESHOLD_FLOAT),
        "exact_field_error_passed": abs(terms["exact_field_error"]) <= THRESHOLD,
        "sum_only_counterfactual": alternative(float(sa), float(sb)),
        "base_only_counterfactual": alternative(la, float(sb)) if leaf else None,
        "identity_exact": identity,
    }


def comparison(a, b, global_errors, mean_errors, *, leaf):
    validate_field_record(a)
    validate_field_record(b)
    if (
        a["array"]["shape"] != b["array"]["shape"]
        or len(global_errors) != 4
        or len(mean_errors) != 4
    ):
        raise ValueError("matching fields and all four original error components are required")
    return [
        {
            "component": i,
            **decompose_component(
                decode(a["conserved_sums"][i]),
                decode(b["conserved_sums"][i]),
                a["legacy_conserved_sums"][i],
                b["legacy_conserved_sums"][i],
                global_errors[i],
                mean_errors[i],
                a["site_count"],
                leaf=leaf,
            ),
        }
        for i in range(4)
    ]


def baseline_record(field, *, backend):
    record = field_record(field, backend=backend)
    sites = record["site_count"]
    analytic = (Fraction(sites), Fraction(0), Fraction(0), Fraction(0))
    return {
        "field": record,
        "analytic_conserved_sums": [encode(v) for v in analytic],
        "rounded_baseline_minus_analytic_site_average": [
            encode((decode(v) - a) / sites)
            for v, a in zip(record["conserved_sums"], analytic, strict=True)
        ],
    }


def negative_controls(base, baseline, *, backend):
    """Known mass and three momentum violations, on actual binary64 fields."""
    if chart.array_metadata(base) != baseline["field"]["array"]:
        raise ValueError("negative-control baseline does not match its exact witness")
    if not np.all(base == d3.WEIGHTS):
        raise ValueError("negative controls require the registered uniform equilibrium")
    velocity_index = {tuple(v): i for i, v in enumerate(d3.VELOCITIES)}
    modifications = [[(velocity_index[(0, 0, 0)], DELTA)]]
    for axis in range(3):
        direction = tuple(int(i == axis) for i in range(3))
        modifications.append(
            [
                (velocity_index[direction], DELTA),
                (velocity_index[tuple(-v for v in direction)], -DELTA),
            ]
        )
    records = []
    for component, changes in enumerate(modifications):
        field = base.copy()
        addition_exact = True
        for population, shift in changes:
            field[..., population] += shift
            addition_exact &= exact_float(field[0, 0, 0, population]) - exact_float(
                base[0, 0, 0, population]
            ) == exact_float(shift)
        measured = field_record(field, backend=backend)
        actual = [
            (decode(a) - decode(b)) / measured["site_count"]
            for a, b in zip(
                measured["conserved_sums"], baseline["field"]["conserved_sums"], strict=True
            )
        ]
        expected = [Fraction(0)] * 4
        expected[component] = exact_float(DELTA) * (1 if component == 0 else 2)
        detected = max(map(abs, actual)) > THRESHOLD
        records.append(
            {
                "component": component,
                "field": measured,
                "expected_site_average_change": [encode(v) for v in expected],
                "actual_site_average_change": [encode(v) for v in actual],
                "additions_exact": bool(addition_exact),
                "detected_violation": bool(detected),
                "passed": bool(addition_exact and actual == expected and detected),
            }
        )
        del field
    return {"delta": DELTA, "records": records, "passed": all(r["passed"] for r in records)}


def artificial_controls():
    """Small independent Fraction loops, including signed and exponent extremes."""
    tiny = np.nextafter(0.0, 1.0)
    largest = np.finfo(np.float64).max
    cases = {
        "empty": np.array([], dtype=np.float64),
        "signed_zero": np.array([0.0, -0.0]),
        "cancellation": np.array([2.0**53, 1.0, -(2.0**53)]),
        "exponent_gap": np.array([2.0**900, tiny, -(2.0**900)]),
        "subnormal": np.array([tiny, -tiny, -tiny]),
        "largest_finite_chunk_cancellation": np.array(
            [largest] * 1025 + [-largest] * 1025 + [tiny]
        ),
        "one_ulp": np.array([np.nextafter(1.0, 2.0), -1.0]),
    }
    for count in (1023, 1024, 1025, 2049):
        cases[f"chunk_boundary_{count}"] = np.full(count, np.nextafter(2.0, 1.0))
    rows = []
    for name, values in cases.items():
        reference = sum((Fraction.from_float(float(x)) for x in values), Fraction(0))
        actual = {backend: exact_sum(values, backend=backend) for backend in BACKENDS}
        rows.append(
            {
                "name": name,
                "input": chart.array_metadata(values),
                "reference": encode(reference),
                "actual": {backend: encode(value) for backend, value in actual.items()},
                "passed": all(value == reference for value in actual.values()),
            }
        )
    rejection_rows = []
    for name, values in (
        ("float32", np.ones(3, dtype=np.float32)),
        ("integer", np.ones(3, dtype=np.int64)),
        ("complex", np.ones(3, dtype=np.complex128)),
        ("nan", np.array([np.nan])),
        ("inf", np.array([np.inf])),
        ("negative_inf", np.array([-np.inf])),
    ):
        rejected = {}
        for backend in BACKENDS:
            try:
                exact_sum(values, backend=backend)
            except (TypeError, ValueError):
                rejected[backend] = True
            else:
                rejected[backend] = False
        rejection_rows.append(
            {"name": name, "rejected": rejected, "passed": all(rejected.values())}
        )
    return {
        "chunk_size": CHUNK_SIZE,
        "threshold": encode(THRESHOLD),
        "sums": rows,
        "rejections": rejection_rows,
        "passed": all(row["passed"] for row in rows + rejection_rows),
    }
