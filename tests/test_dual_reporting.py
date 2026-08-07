from __future__ import annotations

import json

import pytest

from ttim_lbm.dual_reporting import run_dual_reporting_audit


@pytest.fixture(scope="module")
def dual_audit():
    return run_dual_reporting_audit()


def test_q006p_aligns_the_sealed_studies_and_directions(dual_audit) -> None:
    summary = dual_audit["summary"]

    assert dual_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in dual_audit["validity_gates"].values())
    assert summary["direction_alignment_record_count"] == 64
    assert summary["maximum_direction_alignment_error"] == 0.0
    assert summary["q006i_original_maximum_drift"] == pytest.approx(
        2.728496323152741e-12
    )
    assert summary["q006o_fsum_maximum_drift"] == pytest.approx(
        2.7285041507210106e-12
    )
    assert summary["q006i_q006o_drift_difference"] <= 5.0e-15


def test_q006p_preserves_the_original_q006i_failure(dual_audit) -> None:
    original = dual_audit["original_column"]
    gate = original["gates"]["global_conservation"]

    assert original["failed_gate_count"] == 1
    assert original["failed_gate_names"] == ["global_conservation"]
    assert gate["threshold"] == 1.0e-12
    assert not gate["passed"]
    assert original["sealed_hypothesis_outcome"] == "rejected"


def test_q006p_policy_column_replaces_only_conservation(dual_audit) -> None:
    original = dual_audit["original_column"]
    policy = dual_audit["policy_column"]

    assert policy["failed_gate_count"] == 0
    assert policy["global_gate_replacement_only"]
    assert policy["gates"]["global_conservation"]["passed"]
    for name, original_gate in original["gates"].items():
        if name != "global_conservation":
            assert policy["gates"][name] == original_gate


def test_q006p_accepts_only_conditional_chart_continuation(dual_audit) -> None:
    assert all(
        gate["passed"] for gate in dual_audit["dual_decision_gates"].values()
    )
    assert dual_audit["hypothesis_outcome"] == "accepted"
    assert dual_audit["scientific_classification"] == (
        "dual reporting supports unmodified-map chart continuation"
    )
    assert dual_audit["summary"]["q006o_standard_policy_outcome"] == "passed"
    assert dual_audit["summary"]["q006o_uniform_policy_outcome"] == "failed"
    assert "preserves the sealed Q006i rejection" in dual_audit["claim_boundary"]
    assert "independent holdout" in dual_audit["claim_boundary"]


def test_q006p_result_is_strict_json(dual_audit) -> None:
    json.dumps(dual_audit, allow_nan=False)
