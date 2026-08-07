from __future__ import annotations

import json

import pytest

from ttim_lbm.projection_representability import (
    run_projection_representability_audit,
)


@pytest.fixture(scope="module")
def projection_audit():
    return run_projection_representability_audit()


def test_q006k_reproduces_both_q006j_controls(projection_audit) -> None:
    summary = projection_audit["summary"]

    assert projection_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in projection_audit["validity_gates"].values())
    assert summary["trajectory_count"] == 64
    assert summary["step_record_count_per_control"] == 6400
    assert summary["total_control_step_count"] == 19200
    assert summary["maximum_standard_fsum_drift"]["norm"] == pytest.approx(
        2.7285041507210106e-12
    )
    assert summary["maximum_uniform_fsum_drift"]["norm"] == pytest.approx(
        2.1600518690316044e-12
    )


def test_q006k_observes_distributed_projection_realization_error(
    projection_audit,
) -> None:
    representability = projection_audit["summary"]["uniform_representability"]

    assert representability["nonzero_global_correction_error_step_count"] == 6400
    assert representability["maximum_global_correction_error_norm"] == pytest.approx(
        5.712534286801892e-14
    )
    assert representability["minimum_changed_population_count"] == 0
    assert representability["maximum_changed_population_count"] == 2601
    assert 0.0 < representability["mean_changed_population_count"] < 2601.0


def test_q006k_accepts_only_the_symmetry_breaking_diagnostic(
    projection_audit,
) -> None:
    summary = projection_audit["summary"]

    assert projection_audit["hypothesis_outcome"] == "accepted"
    assert projection_audit["scientific_classification"] == (
        "uniform projection representability failure localized"
    )
    assert all(
        gate["passed"] for gate in projection_audit["hypothesis_gates"].values()
    )
    assert summary["maximum_localized_fsum_drift"]["norm"] == pytest.approx(
        1.5115007100657805e-16
    )
    assert summary["maximum_localized_correction_norm"] == pytest.approx(
        5.929251100471871e-14
    )
    assert summary["maximum_localized_standard_state_difference"] == pytest.approx(
        1.0385188929820109e-13
    )
    assert summary["minimum_localized_population"] > 0.0
    assert "symmetry-breaking diagnostic only" in projection_audit["claim_boundary"]


def test_q006k_result_is_strict_json(projection_audit) -> None:
    json.dumps(projection_audit, allow_nan=False)
