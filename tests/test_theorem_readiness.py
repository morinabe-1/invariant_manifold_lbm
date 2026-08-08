from __future__ import annotations

import json

import pytest

from ttim_lbm.theorem_readiness import run_theorem_readiness_audit


@pytest.fixture(scope="module")
def theorem_readiness():
    return run_theorem_readiness_audit()


def test_q007g_reproduces_the_structural_and_spectral_inputs(
    theorem_readiness,
) -> None:
    structure = theorem_readiness["map_structure"]
    spectral = theorem_readiness["spectral_audit"]

    assert theorem_readiness["study_validity"] == "passed"
    assert len(theorem_readiness["validity_gates"]) == 6
    assert all(
        gate["passed"] for gate in theorem_readiness["validity_gates"].values()
    )
    assert structure["local_diffeomorphism_structurally_proved"]
    assert structure["collision_derivative_determinant_per_site"] == 0.015625
    assert structure["filter_multiplier_uniform_lower_bound"] == 0.98
    assert spectral["selected_complex_dimension"] == 24
    assert spectral["excluded_complex_dimension"] == 2574
    assert spectral["fixed_leaf_complex_dimension"] == 2598
    assert spectral["all_eigenvalues_nonzero"]
    assert max(spectral["q007e_reproduction"].values()) <= 1.0e-10


def test_q007g_locates_the_registered_spectral_quotient(
    theorem_readiness,
) -> None:
    quotient = theorem_readiness["spectral_quotient"]

    assert quotient["observed_L"] == 89
    assert quotient["registered_L_match"]
    assert quotient["tail_ratio_at_L"] < 1.0
    assert quotient["previous_ratio"] >= 1.0
    assert quotient["tail_margin_below_one"] >= 1.0e-6
    assert quotient["previous_margin_above_one"] >= 1.0e-6
    assert quotient["tail_separation_starts_at_degree"] == 90


def test_q007g_keeps_sector_evidence_distinct_from_the_direct_theorem(
    theorem_readiness,
) -> None:
    evidence = theorem_readiness["order_evidence"]

    assert evidence["required_order_count"] == 88
    assert evidence["sector_aware_float64_orders"] == [2, 3, 4]
    assert evidence["global_direct_theorem_float64_orders"] == []
    assert evidence["certified_direct_theorem_orders"] == []
    assert evidence["missing_sector_aware_float64_order_count"] == 85
    assert evidence["uncertified_direct_theorem_order_count"] == 88
    assert evidence["first_missing_sector_aware_float64_order"] == 5
    assert evidence["first_uncertified_direct_theorem_order"] == 2
    assert evidence["all_existing_numerical_gates_passed"]
    assert all(
        record["numerical_gate_passed"]
        and not record["direct_theorem_condition_certified"]
        for record in evidence["degree_records"]
    )


def test_q007g_reports_a_valid_not_ready_result_without_changing_q007f(
    theorem_readiness,
) -> None:
    readiness = theorem_readiness["readiness"]

    assert theorem_readiness["hypothesis_outcome"] == "not_ready"
    assert theorem_readiness["scientific_classification"] == (
        "current evidence is not theorem-ready"
    )
    assert not readiness["qualitative_theorem_ready"]
    assert not readiness["quantitative_chart_ready"]
    assert not readiness["ready_for_computer_assisted_existence_proof"]
    assert readiness["quantitative_proof_objects"]["graph_gauge"]
    assert not readiness["quantitative_proof_objects"][
        "rigorous_linearized_inverse_bound"
    ]
    assert not any(theorem_readiness["preserved_prior_outcomes"].values())
    assert "not an invariant-manifold nonexistence result" in theorem_readiness[
        "claim_boundary"
    ]
    json.dumps(theorem_readiness, allow_nan=False)
