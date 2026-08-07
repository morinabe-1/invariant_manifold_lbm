from __future__ import annotations

import json

import pytest

from ttim_lbm.anchor_obstruction import (
    anchor_metrics,
    run_anchor_obstruction_audit,
)
from ttim_lbm.d2q9 import uniform_equilibrium


@pytest.fixture(scope="module")
def obstruction_audit():
    return run_anchor_obstruction_audit()


def test_anchor_metrics_records_an_exact_uniform_tie() -> None:
    state = uniform_equilibrium(17, 17, [0.0, 0.0, 0.0])

    metrics = anchor_metrics(state)

    assert metrics["anchor"] == [0, 0]
    assert metrics["maximum_multiplicity"] == 289
    assert metrics["top_two_gap"] == 0.0


def test_q006m_enumerates_the_registered_finite_ladder(obstruction_audit) -> None:
    summary = obstruction_audit["summary"]

    assert obstruction_audit["study_validity"] == "passed"
    assert all(gate["passed"] for gate in obstruction_audit["validity_gates"].values())
    assert summary["direction_amplitude_record_count"] == 384
    assert summary["signed_state_count"] == 768
    assert summary["stage_observation_count"] == 1536
    assert summary["minimum_population"] > 0.0
    assert summary["all_registered_values_finite"]


def test_q006m_confirms_the_translation_fixed_point_obstruction(
    obstruction_audit,
) -> None:
    summary = obstruction_audit["summary"]

    assert obstruction_audit["hypothesis_outcome"] == "accepted"
    assert obstruction_audit["scientific_classification"] == (
        "equivariant unique-anchor obstruction confirmed"
    )
    assert all(
        gate["passed"] for gate in obstruction_audit["hypothesis_gates"].values()
    )
    assert summary["uniform_q0_maximum_multiplicity"] == 289
    assert summary["uniform_q0_top_two_gap"] == 0.0
    assert summary["translation_fixed_site_counts"] == {
        "translation_y": 0,
        "translation_x": 0,
    }
    assert summary["common_translation_fixed_site_count"] == 0
    assert summary["maximum_uniform_translation_invariance_error"] == 0.0
    assert summary["uniform_translation_bitwise_invariant"]
    assert summary["row_major_translation_covariance_failure_count"] == 2


def test_q006m_records_all_eight_shrinking_gap_ladders(obstruction_audit) -> None:
    ladders = obstruction_audit["gap_ladders"]
    summary = obstruction_audit["summary"]

    assert len(ladders) == 8
    assert all(ladder["passed"] for ladder in ladders)
    assert summary["failed_gap_ladder_count"] == 0
    assert summary["maximum_smallest_to_largest_gap_ratio"] <= 1.0e-4
    assert len(obstruction_audit["plus_minus_anchor_match_summary"]) == 24
    assert "only unique-site selectors" in obstruction_audit["claim_boundary"]


def test_q006m_result_is_strict_json(obstruction_audit) -> None:
    json.dumps(obstruction_audit, allow_nan=False)
