from __future__ import annotations

import json

import pytest

from ttim_lbm.covariant_correction import run_covariant_correction_audit


@pytest.fixture(scope="module")
def covariant_audit():
    return run_covariant_correction_audit()


def test_q006l_reproduces_q006k_controls(covariant_audit) -> None:
    summary = covariant_audit["summary"]

    assert covariant_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in covariant_audit["validity_gates"].values())
    assert summary["trajectory_count"] == 64
    assert summary["step_record_count_per_control"] == 6400
    assert summary["total_control_step_count"] == 19200
    assert summary["maximum_standard_fsum_drift"]["norm"] == pytest.approx(
        2.7285041507210106e-12
    )
    assert summary["maximum_fixed_fsum_drift"]["norm"] == pytest.approx(
        1.5115007100657805e-16
    )


def test_q006l_has_unique_covariant_anchors(covariant_audit) -> None:
    summary = covariant_audit["summary"]

    assert summary["minimum_anchor_gap"]["collision"] == pytest.approx(
        1.634885504753214e-09
    )
    assert summary["minimum_anchor_gap"]["filter"] == pytest.approx(
        1.2466925825016517e-09
    )
    assert summary["anchor_covariance_failure_count"] == 0
    assert summary["right_inverse"]["condition_number"] < 10.0
    assert summary["right_inverse"]["right_inverse_residual"] < 1.0e-14


def test_q006l_accepts_conservation_and_exact_generator_equivariance(
    covariant_audit,
) -> None:
    summary = covariant_audit["summary"]

    assert covariant_audit["hypothesis_outcome"] == "accepted"
    assert covariant_audit["scientific_classification"] == (
        "covariant anchor correction controls registered drift"
    )
    assert all(
        gate["passed"] for gate in covariant_audit["hypothesis_gates"].values()
    )
    assert summary["maximum_covariant_fsum_drift"]["norm"] == pytest.approx(
        1.1368683983919837e-13
    )
    assert summary["maximum_translation_equivariance_error"] == 0.0
    assert summary["maximum_quarter_turn_equivariance_error"] == 0.0
    assert summary["maximum_single_correction_norm"] == pytest.approx(
        1.8963155506680104e-14
    )
    assert summary["maximum_covariant_standard_state_difference"] == pytest.approx(
        1.1557706939439593e-13
    )
    assert summary["minimum_covariant_population"] > 0.0
    assert "nonsmooth at anchor switches" in covariant_audit["claim_boundary"]


def test_q006l_result_is_strict_json(covariant_audit) -> None:
    json.dumps(covariant_audit, allow_nan=False)
