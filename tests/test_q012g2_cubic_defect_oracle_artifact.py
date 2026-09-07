"""Full saved oracle with independent scalar identities and multinomial sums."""

from copy import deepcopy
from fractions import Fraction as F
from math import factorial, isfinite
from pathlib import Path

import numpy as np
import pytest

from research import q012g2_cubic_defect_oracle as r
from ttim_lbm.rational_spectrum import _file_sha256

PATH = Path("research/artifacts/q012g2_cubic_defect_oracle.json")
SHA = "493f78e85887821862dbfae135b30c019979369b285db5e114772eb71dd90b03"


def exact(value):
    if isinstance(value, list):
        return [exact(v) for v in value]
    # A coefficient container also has a key called "numerator". A scalar
    # rational is identified by its denominator/display fields, not that name.
    if "denominator" not in value and "float" not in value:
        return {k: exact(v) for k, v in value.items()}
    assert set(value) == {"numerator", "denominator", "float"}
    result = F(int(value["numerator"]), int(value["denominator"]))
    assert (str(result.numerator), str(result.denominator)) == (
        value["numerator"],
        value["denominator"],
    )
    assert isfinite(value["float"]) and value["float"] == float(result)
    return result


def test_exact_decoder_distinguishes_a_numerator_polynomial_from_a_scalar():
    rational = {"numerator": "1", "denominator": "2", "float": 0.5}
    assert exact({"numerator": [rational]}) == {"numerator": [F(1, 2)]}
    for bad in (
        {"numerator": "2", "denominator": "4", "float": 0.5},
        {"numerator": "1", "denominator": "2", "float": 0.4},
        {"numerator": "1", "float": 0.5},
    ):
        with pytest.raises(AssertionError):
            exact(bad)


def h(x, y, degree):
    second = x * x + F(1, 2) * x * y - F(1, 4) * y * y
    third = F(1, 4) * x**3 - F(1, 8) * x * y * y + F(1, 16) * y**3
    return second + (third if degree == 3 else 0)


def direct(x, y, degree):
    l1, l2 = F(1, 2) * x - F(1, 4) * y, F(1, 4) * x + F(1, 2) * y
    a, b = l1 + x * x / 8, l2 - x * y / 8
    c, d = a + x * y * y / 16, b + y**3 / 32
    if degree == 3:
        a, b = c, d
    state = [x, y, h(x, y, degree)]
    density = 1 + (2 * x - y) / 8 + x * x / 16 + y**3 / 32
    numerator = x**4 + x**3 * y / 2 - x * y**3 / 4 + y**6 / 8
    phi = [c, d, h(c, d, 3) + (state[2] - h(x, y, 3)) / 8 + numerator / density]
    composed = [a, b, h(a, b, degree)]
    return {
        "W": state,
        "Phi_W": phi,
        "W_R": composed,
        "defect": [v - w for v, w in zip(phi, composed, strict=True)],
        "density": density,
    }


def at(coefficients, t):
    return sum((c * t**n for n, c in enumerate(coefficients)), F(0))


@pytest.fixture(scope="module")
def saved():
    assert _file_sha256(PATH) == SHA
    result = r.prior.read_json(PATH)
    assert result["source_sha256"] == r.source_seals()
    assert result["input_audit"] == r.input_audit()
    assert result["evidence_digest_sha256"] == r.digest(result["evidence"])
    assert r.audit_document(result)
    return result


def test_all_1824_coefficient_scalars_and_2976_case_values(saved):
    coefficients = cases = 0
    schedule = []
    for record in saved["evidence"]["directions"]:
        reference = exact(record["reference"])
        for key, values in record["coefficients"].items():
            a, b = np.asarray(values), np.asarray(reference[key], dtype=float)
            assert a.shape == b.shape and np.all(np.isfinite(a))
            coefficients += a.size
            error = float(np.max(np.abs(a - b)))
            threshold = 5e-13 * max(1, float(np.max(np.abs(b))))
            assert record["checks"][key] == {
                "maximum_absolute_error": error,
                "tolerance": threshold,
                "passed": error <= threshold,
            }
        for case in record["cases"]:
            schedule.append(
                (case["direction_index"], case["degree"], case["amplitude"], case["sign"])
            )
            reference_values = exact(case["reference"])
            scale = max(
                1.0,
                *(
                    float(np.max(np.abs(case["values"][key])))
                    for key in ("Phi_W", "W_R", "P9", "remainder")
                ),
            )
            assert case["scale"] == scale
            for key, value in case["values"].items():
                a, b = np.asarray(value), np.asarray(reference_values[key], dtype=float)
                cases += a.size
                assert a.shape == b.shape and np.all(np.isfinite(a))
                error = float(np.max(np.abs(a - b)))
                threshold = 256 * np.finfo(float).eps * scale
                assert case["checks"][key] == {
                    "maximum_absolute_error": error,
                    "tolerance": threshold,
                    "passed": error <= threshold,
                }
    assert coefficients == 1824 and cases == 2976
    assert schedule == [
        (i, d, a, s)
        for i in range(6)
        for d in (2, 3)
        for a in (1 / 128, 1 / 64, 1 / 32, 1 / 16)
        for s in (-1, 1)
    ]


def test_all_96_exact_direct_maps_and_remainder_identities(saved):
    for record in saved["evidence"]["directions"]:
        ref = exact(record["reference"])
        for case in record["cases"]:
            t = F.from_float(case["sign"] * case["amplitude"])
            x, y = [F(v) * t for v in record["direction"]]
            values = exact(case["reference"])
            expected = direct(x, y, case["degree"])
            assert {k: values[k] for k in expected} == expected
            p9 = [at([row[i] for row in ref["defect"]], t) for i in range(3)]
            rational_tail = at(ref["numerator"], t) / at(ref["rho"], t) - at(ref["quotient"], t)
            tail = [F(0), F(0), rational_tail]
            assert values["P9"] == p9 and values["remainder"] == tail
            assert [v + w for v, w in zip(p9, tail, strict=True)] == expected["defect"]
            assert values["reconstructed"] == expected["defect"]


def test_cubic_coefficients_from_independent_multinomial_inverse(saved):
    for record in saved["evidence"]["directions"]:
        if record["degree"] != 3:
            continue
        x, y = map(F, record["direction"])
        r1, r2, r3 = x / 4 - y / 8, x * x / 16, y**3 / 32
        inverse = []
        for n in range(10):
            value = F(0)
            for i in range(n + 1):
                for j in range(n // 2 + 1):
                    for k in range(n // 3 + 1):
                        if i + 2 * j + 3 * k == n:
                            count = factorial(i + j + k) // (
                                factorial(i) * factorial(j) * factorial(k)
                            )
                            value += (-1) ** (i + j + k) * count * r1**i * r2**j * r3**k
            inverse.append(value)
        numerator4, numerator6 = x**4 + x**3 * y / 2 - x * y**3 / 4, y**6 / 8
        reference = exact(record["reference"])
        for n, row in enumerate(reference["defect"]):
            value = numerator4 * inverse[n - 4] if n >= 4 else 0
            value += numerator6 * inverse[n - 6] if n >= 6 else 0
            assert row == [0, 0, value]
        gx, gy = x * y * y / 16, y**3 / 32
        assert reference["composed"][9][2] == h(gx, gy, 3) - h(gx, gy, 2)


def test_decision_scope_and_all_controls(saved):
    assert all(saved["decision"]["validity_gates"].values())
    assert saved["decision"]["hypothesis_gates"] == {"H1_exact_degree_oracle": True}
    assert saved["decision"]["scientific_outcome"] == "accepted"
    assert all(saved["evidence"]["controls"].values())
    assert saved["claim_boundary"] == r.BOUNDARY
    assert r.prior.read_json(r.prior.PARENT_PATH)["scientific_outcome"] == "rejected"


def test_last_saved_value_cannot_be_replaced_by_a_success_flag(saved):
    altered = deepcopy(saved)
    altered["evidence"]["directions"][-1]["cases"][-1]["values"]["defect"][2] += 1e-5
    altered["evidence_digest_sha256"] = r.digest(altered["evidence"])
    assert not r.audit_document(altered)
