"""Registered artificial map, exact reference, complete coverage and tamper tests."""

from copy import deepcopy
from fractions import Fraction as F

import numpy as np
import pytest

from research import q012g2_cubic_defect_oracle as r


@pytest.fixture(scope="module")
def evidence():
    return r.build_evidence()


def test_all_registered_coefficients_cases_and_controls(evidence):
    decision = r.adjudicate(evidence, {"passed": True}, True)
    assert decision["scientific_outcome"] == "accepted"
    assert all(decision["validity_gates"].values())
    assert set(evidence["controls"]) == r.CONTROL_KEYS
    assert len(evidence["directions"]) == 12
    assert sum(len(v["cases"]) for v in evidence["directions"]) == 96
    for record in evidence["directions"]:
        assert set(record["coefficients"]) == r.COEFFICIENT_KEYS
        for case in record["cases"]:
            assert case["values"]["density"] > 0
            assert case["checks"]["remainder_identity"]["passed"]
            assert set(case["values"]) == set(case["reference"])


def test_closed_axis_coefficients_and_ninth_order_composition():
    ref = r.reference_coefficients((1, 0), 3)
    assert [row[2] for row in ref["defect"][:4]] == [0] * 4
    assert [row[2] for row in ref["defect"][4:]] == [
        F(1),
        F(-1, 4),
        F(0),
        F(1, 64),
        F(-1, 256),
        F(0),
    ]
    mixed = r.reference_coefficients((1, 1), 3)
    assert mixed["composed"][9][2] == F(29, 524288)
    assert all(row[:2] == [0, 0] for row in mixed["defect"])


def test_quadratic_chart_does_not_drop_G3_from_physical_map():
    second = r.reference_coefficients((1, 1), 2)
    assert second["defect"][3][:2] == [F(1, 16), F(1, 32)]
    assert second["reduced_model"][3] == [0, 0]
    assert second["reduced_full"][3] == [F(1, 16), F(1, 32)]


def test_wrong_factor_and_missing_G3_fail_coefficient_checks():
    actual, reference = r.primary_coefficients((1, 1), 3), r.reference_coefficients((1, 1), 3)
    bad = {k: v.copy() for k, v in actual.items()}
    bad["composed"][9, 2] /= 6
    assert not r.coefficient_checks(bad, reference)["composed"]["passed"]
    bad["reduced_full"][3] = 0
    assert not r.coefficient_checks(bad, reference)["reduced_full"]["passed"]


def test_exact_geometric_reference_has_nonzero_constant_density():
    assert r.geometric_quotient([F(3)], [F(2), F(1, 2)], 4) == [
        F(3, 2) * F(-1, 4) ** k for k in range(5)
    ]
    with pytest.raises(ValueError):
        r.geometric_quotient([F(1)], [F(0), F(1)], 9)


def test_nonzero_finite_amplitude_remainder_is_not_called_zero(evidence):
    mixed = next(
        v for v in evidence["directions"] if v["direction_index"] == 2 and v["degree"] == 3
    )
    case = mixed["cases"][-1]
    exact = case["reference"]["remainder"][2]
    assert F(int(exact["numerator"]), int(exact["denominator"])) != 0
    assert case["values"]["remainder"][2] != 0


@pytest.mark.parametrize(
    "damage", ["last_case", "last_direction", "last_check", "control", "source"]
)
def test_missing_evidence_never_becomes_accepted(evidence, damage):
    broken = deepcopy(evidence)
    unchanged = True
    if damage == "last_case":
        broken["directions"][-1]["cases"].pop()
    elif damage == "last_direction":
        broken["directions"].pop()
    elif damage == "last_check":
        broken["directions"][-1]["checks"].pop("remainder_numerator")
    elif damage == "control":
        broken["controls"].pop("invalid_inputs_rejected")
    else:
        unchanged = False
    decision = r.adjudicate(broken, {"passed": True}, unchanged)
    assert decision["scientific_outcome"] == "inconclusive"
    assert decision["hypothesis_gates"]["H1_exact_degree_oracle"] is None


def test_valid_failed_prediction_is_rejected_not_inconclusive(evidence):
    broken = deepcopy(evidence)
    broken["directions"][-1]["cases"][-1]["passed"] = False
    decision = r.adjudicate(broken, {"passed": True}, True)
    assert decision["study_gate"] == "passed" and decision["scientific_outcome"] == "rejected"


def test_comparison_checks_complex_reference_and_rejects_shape_mismatch():
    assert r.comparison([1 + 2j], [1 + 2j], 1e-13)["passed"]
    assert not r.comparison([1 + 2j], [1 + 3j], 1e-13)["passed"]
    with pytest.raises(ValueError):
        r.comparison([1, 2], [1], 1e-13)
    with pytest.raises(ValueError):
        r.comparison([np.inf], [1], 1e-13)


@pytest.fixture
def saved(tmp_path, monkeypatch):
    monkeypatch.setattr(r, "input_audit", lambda: {"passed": True, "synthetic_test": True})
    path = tmp_path / "oracle.json"
    result, audited = r.run(path)
    assert audited
    assert r.prior.read_json(path) == result
    return result, path


def test_saved_roundtrip_and_no_overwrite(saved):
    result, path = saved
    before = path.read_bytes()
    assert r.audit_document(result)
    with pytest.raises(FileExistsError):
        r.run(path)
    assert path.read_bytes() == before


@pytest.mark.parametrize(
    "damage", ["coefficient", "last_component", "fraction", "case", "decision", "source"]
)
def test_saved_audit_rejects_tampering_even_with_recomputed_digest(saved, damage):
    original, _ = saved
    broken = deepcopy(original)
    last = broken["evidence"]["directions"][-1]
    if damage == "coefficient":
        last["coefficients"]["defect"][9][2] += 1e-5
    elif damage == "last_component":
        last["cases"][-1]["values"]["defect"][2] += 1e-5
    elif damage == "fraction":
        last["reference"]["defect"][9][2]["numerator"] = "1"
    elif damage == "case":
        last["cases"].pop()
    elif damage == "decision":
        broken["decision"]["scientific_outcome"] = "rejected"
    else:
        broken["source_sha256"]["research/polynomial_path.py"] = "0" * 64
    broken["evidence_digest_sha256"] = r.digest(broken["evidence"])
    assert not r.audit_document(broken)


@pytest.mark.parametrize("failure", ["exception", "nonfinite"])
def test_failed_artificial_build_is_saved_as_inconclusive(tmp_path, monkeypatch, failure):
    monkeypatch.setattr(r, "input_audit", lambda: {"passed": True})

    def fail():
        if failure == "exception":
            raise FloatingPointError("artificial failure")
        return {"invalid": float("nan")}

    monkeypatch.setattr(r, "build_evidence", fail)
    result, audited = r.run(tmp_path / "failed.json")
    assert not audited
    assert result["decision"]["scientific_outcome"] == "inconclusive"
    assert "error" in result and "evidence" not in result
