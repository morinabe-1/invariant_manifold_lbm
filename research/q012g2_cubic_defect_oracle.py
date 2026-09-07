"""Q012g2 artificial degree oracle, not an LBM campaign or a chart solver."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path

import numpy as np

from research import polynomial_path as poly
from research import q012g1_d3q27_conservation as prior
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

DIRECTIONS = ((1, 0), (0, 1), (1, 1), (1, -1), (2, 1), (-1, 2))
AMPLITUDES = (1 / 128, 1 / 64, 1 / 32, 1 / 16)
ORDER = 9
INPUT_SEALS = {
    "research/artifacts/q012g_d3q27_cubic_chart.json": prior.PARENT_SHA,
    "research/artifacts/q012g1_d3q27_conservation.json": "ca6b15627880cbe390f6a53bc87eb9a6ba0833f1f370c5b9ea2c494625e75000",
}
KIND = "Q012g2 manufactured degree-resolved defect oracle"
BOUNDARY = "Artificial algebra only; Q012g rejection and LBM defect failures remain unchanged."
COEFFICIENT_KEYS = frozenset(
    (
        "reduced_full",
        "reduced_model",
        "state",
        "composed",
        "phi_polynomial",
        "rho",
        "numerator",
        "quotient",
        "defect",
        "remainder_numerator",
    )
)
CONTROL_KEYS = frozenset(
    (
        "axis_closed_coefficients",
        "nonzero_ninth_composition",
        "wrong_factor_detected",
        "dropped_G3_detected",
        "nonunit_constant_density",
        "constant_complex_duplicate_path",
        "empty_support",
        "low_degree_residue_retained",
        "invalid_inputs_rejected",
    )
)


def source_seals():
    return {
        str(Path(p).as_posix()): _file_sha256(Path(p))
        for p in ("research/polynomial_path.py", "research/q012g2_cubic_defect_oracle.py")
    }


def input_audit():
    seals = {p: _file_sha256(Path(p)) for p in INPUT_SEALS}
    saved = prior.read_json(Path("research/artifacts/q012g1_d3q27_conservation.json"))
    checks = {
        "sealed_parents": seals == INPUT_SEALS,
        "conservation_accepted": saved["study_gate"] == "passed"
        and saved["scientific_outcome"] == "accepted",
        "frozen_parent_sources": prior.parent.source_equal(saved, prior.metadata()),
    }
    return {"sha256": seals, "checks": checks, "passed": all(checks.values())}


def pad(value, length=10):
    value = np.asarray(value)
    if len(value) > length:
        raise ValueError("padding must not truncate coefficients")
    return np.pad(value, ((0, length - len(value)),) + ((0, 0),) * (value.ndim - 1))


def h_path(path, degree):
    h2 = poly.homogeneous_composition(
        np.array(((0, 0), (0, 1), (1, 1))),
        np.zeros(3, dtype=int),
        np.array(((1,), (0.5,), (-0.25,))),
        path,
        group_count=1,
    )[:, 0, 0]
    if degree == 2:
        return h2
    h3 = poly.homogeneous_composition(
        np.array(((0, 0, 0), (0, 1, 1), (1, 1, 1))),
        np.zeros(3, dtype=int),
        np.array(((0.25,), (-0.125,), (0.0625,))),
        path,
        group_count=1,
    )[:, 0, 0]
    return poly.add(h2, h3)


def primary_coefficients(direction, degree):
    x, y = map(float, direction)
    a = np.array(((0, 0), (x, y)))
    r3 = np.array(
        (
            (0, 0),
            (x / 2 - y / 4, x / 4 + y / 2),
            (x * x / 8, -x * y / 8),
            (x * y * y / 16, y * y * y / 32),
        )
    )
    rd = r3.copy()
    if degree == 2:
        rd[3] = 0
    w = np.column_stack((pad(a, 4), pad(h_path(a, degree), 4)))
    composed = np.column_stack((pad(rd), pad(h_path(rd, degree))))
    phi_poly = np.column_stack(
        (pad(r3), pad(poly.add(h_path(r3, 3), poly.add(h_path(a, degree), -h_path(a, 3)) / 8)))
    )
    rho = np.array((1, x / 4 - y / 8, x * x / 16, y * y * y / 32))
    numerator = np.array((0, 0, 0, 0, x**4 + x**3 * y / 2 - x * y**3 / 4, 0, y**6 / 8))
    quotient = poly.quotient(numerator, rho, order=ORDER)
    defect = phi_poly - composed
    defect[:, 2] += quotient
    return {
        "reduced_full": r3,
        "reduced_model": rd,
        "state": w,
        "composed": composed,
        "phi_polynomial": phi_poly,
        "rho": rho,
        "numerator": numerator,
        "quotient": quotient,
        "defect": defect,
        "remainder_numerator": poly.remainder_numerator(numerator, rho, quotient),
    }


# Independent scalar Fraction polynomials. No NumPy or primary path operations
# occur in these routines; in particular division uses a finite geometric sum.
def fadd(a, b):
    return [
        sum((a[i] if i < len(a) else F(0), b[i] if i < len(b) else F(0)))
        for i in range(max(len(a), len(b)))
    ]


def fscale(a, factor):
    return [v * factor for v in a]


def fmul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, left in enumerate(a):
        for j, right in enumerate(b):
            out[i + j] += left * right
    return out


def fpow(a, exponent):
    out = [F(1)]
    for _ in range(exponent):
        out = fmul(out, a)
    return out


def fh(x, y, degree):
    second = fadd(fadd(fmul(x, x), fscale(fmul(x, y), F(1, 2))), fscale(fmul(y, y), F(-1, 4)))
    if degree == 2:
        return second
    third = fadd(
        fadd(fscale(fpow(x, 3), F(1, 4)), fscale(fmul(x, fpow(y, 2)), F(-1, 8))),
        fscale(fpow(y, 3), F(1, 16)),
    )
    return fadd(second, third)


def feval(a, t):
    # Direct power sum, distinct from the primary Horner evaluator.
    return sum((c * t**i for i, c in enumerate(a)), F(0))


def fpad(a, length):
    if len(a) > length:
        raise ValueError("exact padding must not truncate coefficients")
    return list(a) + [F(0)] * (length - len(a))


def fcolumns(*columns, length):
    return list(map(list, zip(*(fpad(c, length) for c in columns), strict=True)))


def geometric_quotient(numerator, denominator, order):
    if denominator[0] == 0:
        raise ValueError("zero exact constant denominator")
    delta = [F(0)] + fscale(denominator[1:], -1 / denominator[0])
    inverse, power = [F(1)], [F(1)]
    for _ in range(order):
        power = fmul(power, delta)[: order + 1]
        inverse = fadd(inverse, power)[: order + 1]
    return fpad(fmul(numerator, fscale(inverse, 1 / denominator[0]))[: order + 1], order + 1)


def reference_coefficients(direction, degree):
    x, y = [F(0), F(direction[0])], [F(0), F(direction[1])]
    rx = fadd(
        fadd(fscale(x, F(1, 2)), fscale(y, F(-1, 4))),
        fadd(fscale(fpow(x, 2), F(1, 8)), fscale(fmul(x, fpow(y, 2)), F(1, 16))),
    )
    ry = fadd(
        fadd(fscale(x, F(1, 4)), fscale(y, F(1, 2))),
        fadd(fscale(fmul(x, y), F(-1, 8)), fscale(fpow(y, 3), F(1, 32))),
    )
    mx, my = (rx, ry) if degree == 3 else (rx[:3], ry[:3])
    composed_z = fh(mx, my, degree)
    phi_z = fadd(fh(rx, ry, 3), fscale(fadd(fh(x, y, degree), fscale(fh(x, y, 3), -1)), F(1, 8)))
    rho = fadd(
        [F(1)],
        fadd(
            fadd(fscale(x, F(1, 4)), fscale(y, F(-1, 8))),
            fadd(fscale(fpow(x, 2), F(1, 16)), fscale(fpow(y, 3), F(1, 32))),
        ),
    )
    numerator = fadd(
        fadd(fpow(x, 4), fscale(fmul(fpow(x, 3), y), F(1, 2))),
        fadd(fscale(fmul(x, fpow(y, 3)), F(-1, 4)), fscale(fpow(y, 6), F(1, 8))),
    )
    quotient = geometric_quotient(numerator, rho, ORDER)
    dz = fadd(fadd(phi_z, fscale(composed_z, -1)), quotient)
    return {
        "reduced_full": fcolumns(rx, ry, length=4),
        "reduced_model": fcolumns(mx, my, length=4),
        "state": fcolumns(x, y, fh(x, y, degree), length=4),
        "composed": fcolumns(mx, my, composed_z, length=10),
        "phi_polynomial": fcolumns(rx, ry, phi_z, length=10),
        "rho": rho,
        "numerator": numerator,
        "quotient": quotient,
        "defect": fcolumns(fadd(rx, fscale(mx, -1)), fadd(ry, fscale(my, -1)), dz, length=10),
        "remainder_numerator": fadd(numerator, fscale(fmul(rho, quotient), -1)),
    }


def explicit_values(x, y, degree):
    """Independent scalar reference values, with no coefficient engine."""

    def h(a, b, d):
        result = a * a + a * b / 2 - b * b / 4
        return result if d == 2 else result + a * a * a / 4 - a * b * b / 8 + b * b * b / 16

    rx, ry = x / 2 - y / 4 + x * x / 8 + x * y * y / 16, x / 4 + y / 2 - x * y / 8 + y * y * y / 32
    mx, my = (rx, ry) if degree == 3 else (x / 2 - y / 4 + x * x / 8, x / 4 + y / 2 - x * y / 8)
    rho = 1 + x / 4 - y / 8 + x * x / 16 + y * y * y / 32
    forcing = (x**4 + x**3 * y / 2 - x * y**3 / 4 + y**6 / 8) / rho
    state = [x, y, h(x, y, degree)]
    phi = [rx, ry, h(rx, ry, 3) + (state[2] - h(x, y, 3)) / 8 + forcing]
    composed = [mx, my, h(mx, my, degree)]
    return {
        "W": state,
        "Phi_W": phi,
        "W_R": composed,
        "defect": [p - c for p, c in zip(phi, composed, strict=True)],
        "density": rho,
    }


def numeric_values(x, y, degree):
    a = np.array((x, y))
    linear = np.array(((0.5, -0.25), (0.25, 0.5))) @ a
    r2 = linear + np.array((x * x, -x * y)) / 8
    r3 = r2 + np.array((x * y * y / 16, y * y * y / 32))
    rd = r3 if degree == 3 else r2
    h = lambda value, d: float(h_path(value[None, :], d)[0])
    state = np.r_[a, h(a, degree)]
    rho = 1 + np.dot((0.25, -0.125), a) + x * x / 16 + y**3 / 32
    numerator = np.dot((1.0, 0.5, -0.25, 0.125), (x**4, x**3 * y, x * y**3, y**6))
    if rho == 0 or not np.isfinite(rho):
        raise ValueError("invalid artificial density")
    phi = np.r_[r3, h(r3, 3) + (state[2] - h(a, 3)) / 8 + numerator / rho]
    composed = np.r_[rd, h(rd, degree)]
    return {
        "W": state.tolist(),
        "Phi_W": phi.tolist(),
        "W_R": composed.tolist(),
        "defect": (phi - composed).tolist(),
        "density": float(rho),
    }


def encode(value):
    if isinstance(value, F):
        return {
            "numerator": str(value.numerator),
            "denominator": str(value.denominator),
            "float": float(value),
        }
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    return [encode(v) for v in value]


def comparison(actual, reference, tolerance):
    a = np.asarray(actual)
    b = np.asarray(reference, dtype=complex if np.iscomplexobj(reference) else float)
    if a.shape != b.shape or not np.all(np.isfinite(a)) or not np.all(np.isfinite(b)):
        raise ValueError("comparison needs matching finite arrays")
    error = float(np.max(np.abs(a - b)))
    return {
        "maximum_absolute_error": error,
        "tolerance": float(tolerance),
        "passed": bool(error <= tolerance),
    }


def coefficient_checks(actual, reference):
    return {
        k: comparison(actual[k], v, 5e-13 * max(1, np.max(np.abs(np.asarray(v, dtype=float)))))
        for k, v in reference.items()
    }


def one_case(actual, reference, direction_index, degree, amplitude, sign):
    direction = DIRECTIONS[direction_index]
    t, ft = sign * amplitude, F.from_float(sign * amplitude)
    values = numeric_values(*(t * v for v in direction), degree)
    exact = explicit_values(*(ft * F(v) for v in direction), degree)
    p9 = poly.evaluate(actual["defect"], t)
    tail = np.array(
        (
            0.0,
            0.0,
            poly.evaluate(actual["remainder_numerator"], t) / poly.evaluate(actual["rho"], t),
        )
    )
    fp9 = [feval([row[i] for row in reference["defect"]], ft) for i in range(3)]
    ftail = [F(0), F(0), feval(reference["remainder_numerator"], ft) / feval(reference["rho"], ft)]
    values.update(
        {
            "P9": p9.tolist(),
            "remainder": tail.tolist(),
            "reconstructed": (p9 + tail).tolist(),
            "state_path": poly.evaluate(actual["state"], t).tolist(),
            "composed_path": poly.evaluate(actual["composed"], t).tolist(),
            "phi_path": (
                poly.evaluate(actual["phi_polynomial"], t)
                + np.array(
                    (
                        0.0,
                        0.0,
                        poly.evaluate(actual["numerator"], t) / poly.evaluate(actual["rho"], t),
                    )
                )
            ).tolist(),
        }
    )
    exact.update(
        {
            "P9": fp9,
            "remainder": ftail,
            "reconstructed": [p + r for p, r in zip(fp9, ftail, strict=True)],
            "state_path": exact["W"],
            "composed_path": exact["W_R"],
            "phi_path": exact["Phi_W"],
        }
    )
    if exact["reconstructed"] != exact["defect"]:
        raise ValueError("independent exact remainder identity failed")
    scale = max(
        1.0, *(float(np.max(np.abs(values[k]))) for k in ("Phi_W", "W_R", "P9", "remainder"))
    )
    tolerance = 256 * np.finfo(float).eps * scale
    checks = {k: comparison(v, exact[k], tolerance) for k, v in values.items()}
    checks["remainder_identity"] = comparison(values["reconstructed"], values["defect"], tolerance)
    return {
        "direction_index": direction_index,
        "degree": degree,
        "amplitude": amplitude,
        "sign": sign,
        "scale": scale,
        "values": values,
        "reference": encode(exact),
        "checks": checks,
        "passed": all(c["passed"] for c in checks.values()),
    }


def controls():
    axis = primary_coefficients((1, 0), 3)["defect"][4:, 2]
    mixed = primary_coefficients((1, 1), 3)
    bad_factor = mixed["composed"][9, 2] / 6
    constant = poly.quotient([1.0, 2.0], [2.0, 0.5], order=9)
    expected = geometric_quotient([F(1), F(2)], [F(2), F(1, 2)], 9)
    residue = poly.remainder_numerator([1.0], [1.0], [np.nextafter(1.0, 2.0)])
    path = np.array(((1 + 1j, 2), (0.5, -1j)))
    indices = np.array(((0, 0), (0, 0), (0, 1)))
    coefficients = np.array(((1.0,), (2.0,), (1j,)))
    lifted = poly.homogeneous_composition(
        indices, np.array((1, 1, 0)), coefficients, path, group_count=3
    )
    t = 0.125
    z = path[0] + t * path[1]
    explicit = np.array(((1j * z[0] * z[1],), (3 * z[0] ** 2,), (0.0,)))
    empty = poly.homogeneous_composition(
        np.empty((0, 3), dtype=int), np.empty(0, dtype=int), np.empty((0, 2)), path, group_count=2
    )
    invalid = (
        lambda: poly.quotient([1.0], [0.0, 1.0], order=9),
        lambda: poly.evaluate([np.nan], 0.5),
        lambda: poly.evaluate([np.inf], 0.5),
        lambda: poly.evaluate([1.0, 2.0], [0.5]),
        lambda: poly.evaluate([True], 0.5),
        lambda: poly.evaluate([1e308, 1e308], 2.0),
        lambda: poly.quotient([1.0], [1.0], order=True),
        lambda: poly.homogeneous_composition(
            np.array(((2,),)), np.array((0,)), np.ones((1, 1)), path, group_count=1
        ),
    )
    rejected = []
    for operation in invalid:
        try:
            operation()
        except (ValueError, FloatingPointError):
            rejected.append(True)
        else:
            rejected.append(False)
    return {
        "axis_closed_coefficients": bool(
            np.array_equal(axis, [1.0, -0.25, 0.0, 1 / 64, -1 / 256, 0.0])
        ),
        "nonzero_ninth_composition": mixed["composed"][9, 2] == float(F(29, 524288)),
        "wrong_factor_detected": abs(bad_factor - float(F(29, 524288))) > 5e-13,
        "dropped_G3_detected": float(np.max(np.abs(mixed["reduced_full"][3]))) > 5e-13,
        "nonunit_constant_density": comparison(constant, expected, 5e-13)["passed"],
        "constant_complex_duplicate_path": comparison(poly.evaluate(lifted, t), explicit, 5e-13)[
            "passed"
        ],
        "empty_support": empty.shape == (4, 2, 2) and bool(np.all(empty == 0)),
        "low_degree_residue_retained": residue[0] == -np.finfo(float).eps,
        "invalid_inputs_rejected": all(rejected),
    }


def build_evidence():
    records = []
    for index, direction in enumerate(DIRECTIONS):
        for degree in (2, 3):
            actual, reference = (
                primary_coefficients(direction, degree),
                reference_coefficients(direction, degree),
            )
            records.append(
                {
                    "direction_index": index,
                    "direction": list(direction),
                    "degree": degree,
                    "coefficients": {k: v.tolist() for k, v in actual.items()},
                    "reference": encode(reference),
                    "checks": coefficient_checks(actual, reference),
                    "cases": [
                        one_case(actual, reference, index, degree, amplitude, sign)
                        for amplitude in AMPLITUDES
                        for sign in (-1, 1)
                    ],
                }
            )
    return {"controls": {k: bool(v) for k, v in controls().items()}, "directions": records}


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def adjudicate(evidence, inputs, unchanged):
    records = evidence.get("directions", [])
    coverage = [(r["direction_index"], r["degree"]) for r in records]
    expected = [(i, d) for i in range(6) for d in (2, 3)]
    cases = [c for r in records for c in r["cases"]]
    case_keys = [(c["direction_index"], c["degree"], c["amplitude"], c["sign"]) for c in cases]
    expected_cases = [(i, d, a, s) for i, d in expected for a in AMPLITUDES for s in (-1, 1)]
    validity = {
        "sealed_inputs": inputs["passed"],
        "unchanged_sources": unchanged,
        "all_twelve_coefficient_sets": coverage == expected
        and all(set(r["checks"]) == COEFFICIENT_KEYS for r in records),
        "all_96_cases": case_keys == expected_cases,
        "finite_evidence": _all_numeric_values_finite(evidence),
        "artificial_controls": set(evidence.get("controls", {})) == CONTROL_KEYS
        and all(evidence["controls"].values()),
    }
    valid = all(validity.values())
    h1 = all(c["passed"] for r in records for c in r["checks"].values()) and all(
        c["passed"] for c in cases
    )
    return {
        "validity_gates": validity,
        "hypothesis_gates": {"H1_exact_degree_oracle": h1 if valid else None},
        "study_gate": "passed" if valid else "failed",
        "scientific_outcome": ("accepted" if h1 else "rejected") if valid else "inconclusive",
    }


def audit_document(saved):
    """The small artificial experiment can be completely regenerated on readback."""
    try:
        evidence = build_evidence()
        inputs = input_audit()
        return bool(
            saved["kind"] == KIND
            and saved["claim_boundary"] == BOUNDARY
            and saved["source_sha256"] == source_seals()
            and saved["input_audit"] == inputs
            and saved["evidence"] == evidence
            and saved["evidence_digest_sha256"] == digest(evidence)
            and saved["decision"] == adjudicate(evidence, inputs, True)
            and _all_numeric_values_finite(saved)
        )
    except (KeyError, ValueError, TypeError, FloatingPointError):
        return False


def run(output):
    output = Path(output)
    if output.exists():
        raise FileExistsError(output)
    sources, inputs = source_seals(), input_audit()
    saved = {
        "kind": KIND,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "process_id": os.getpid(),
        "source_sha256": sources,
        "input_audit": inputs,
        "claim_boundary": BOUNDARY,
    }
    try:
        evidence = build_evidence() if inputs["passed"] else {}
        if not _all_numeric_values_finite(evidence):
            raise ValueError("nonfinite artificial evidence cannot be saved as numeric data")
        saved["evidence"] = evidence
        saved["decision"] = adjudicate(saved["evidence"], inputs, source_seals() == sources)
        saved["evidence_digest_sha256"] = digest(saved["evidence"])
    except (ValueError, FloatingPointError, ArithmeticError) as exc:
        saved["error"] = {"type": type(exc).__name__, "message": str(exc)}
        saved["decision"] = {"study_gate": "failed", "scientific_outcome": "inconclusive"}
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        json.dump(saved, handle, allow_nan=False, separators=(",", ":"))
        handle.write("\n")
    readback = prior.read_json(output)
    audited = audit_document(readback)
    return saved, audited


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    saved, audited = run(args.output)
    print(
        json.dumps(
            {"output": str(args.output), "decision": saved["decision"], "full_saved_audit": audited}
        )
    )
    if not audited or saved["decision"]["study_gate"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
