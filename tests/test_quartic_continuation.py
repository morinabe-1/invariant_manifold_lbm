from __future__ import annotations

import json

import pytest

from ttim_lbm.quartic_continuation import run_quartic_continuation_audit


@pytest.fixture(scope="module")
def quartic_continuation():
    return run_quartic_continuation_audit()


def test_q007c1_passes_registered_validity_gates(quartic_continuation) -> None:
    assert quartic_continuation["study_validity"] == "passed"
    assert all(
        gate["passed"] for gate in quartic_continuation["validity_gates"].values()
    )
    assert quartic_continuation["direction_registration"]["duplicate_count"] == 0


def test_q007c1_passes_independent_derivative_and_forcing_checks(
    quartic_continuation,
) -> None:
    map_derivative = quartic_continuation["independent_map_fourth_derivative"][
        "summary"
    ]
    forcing = quartic_continuation["independent_assembled_forcing_derivative"][
        "summary"
    ]

    assert map_derivative["minimum_analytic_derivative_norm"] > 1.0e-12
    assert map_derivative["maximum_best_relative_error"] <= 5.0e-3
    assert forcing["minimum_analytic_forcing_norm"] > 1.0e-12
    assert forcing["maximum_best_relative_error"] <= 2.0e-2


def test_q007c1_reproduces_operators_and_solves_all_coefficients(
    quartic_continuation,
) -> None:
    upstream = quartic_continuation["upstream_reproduction"]
    summary = quartic_continuation["coefficient_construction"]["summary"]
    conjugacy = quartic_continuation["coefficient_construction"][
        "conjugacy_audit"
    ]

    assert upstream["cubic_hashes_match"]
    assert upstream["quartet_summary"]["record_count"] == 17550
    assert upstream["quartet_summary"]["sector_counts"] == {
        "zero_wave_kinetic": 846,
        "internal_selected": 4536,
        "external": 12168,
    }
    assert upstream["quartet_summary"]["numerically_singular_block_count"] == 0
    assert summary["maximum_solve_relative_residual"] <= 1.0e-10
    assert summary["maximum_homological_relative_residual"] <= 1.0e-10
    assert summary["maximum_graph_gauge_relative_residual"] <= 1.0e-10
    assert conjugacy["missing_conjugate_count"] == 0
    assert conjugacy["maximum_relative_residual"] <= 1.0e-10


def test_q007c1_raises_order_and_passes_sampled_radius_residuals(
    quartic_continuation,
) -> None:
    summary = quartic_continuation["residual_order_campaign"]["summary"]

    assert 3.85 <= summary["minimum_cubic_slope"]
    assert summary["maximum_cubic_slope"] <= 4.15
    assert 4.70 <= summary["minimum_quartic_slope"]
    assert summary["maximum_quartic_slope"] <= 5.30
    assert summary["maximum_quartic_to_cubic_residual_ratio"] <= 0.8
    assert summary["maximum_quartic_to_quadratic_residual_ratio"] <= 0.10
    assert quartic_continuation["hypothesis_gates"][
        "held_out_residual_orders"
    ]["passed"]
    assert quartic_continuation["hypothesis_gates"][
        "held_out_radius_residual_ratios"
    ]["passed"]


def test_q007c1_records_valid_shadowing_performance_rejection(
    quartic_continuation,
) -> None:
    summary = quartic_continuation["shadowing_campaign"]["summary"]
    ratios = summary["maximum_directional_improvement_ratios"]

    assert ratios["maximum_absolute_error_ratio"] <= 0.8
    assert ratios["final_absolute_error_ratio"] > 0.8
    assert ratios["maximum_perturbation_relative_error_ratio"] > 0.8
    assert summary["quartic_budget_component_check_count"] == 9600
    assert summary["quartic_budget_violation_count"] == 0
    assert summary["maximum_quartic_budget_utilization"] <= 1.0
    assert summary["maximum_final_component_budget"] <= 1.2e-11
    assert not quartic_continuation["hypothesis_gates"][
        "held_out_directional_shadowing_ratios"
    ]["passed"]
    assert quartic_continuation["hypothesis_gates"][
        "quartic_shadowing_forward_error_budget"
    ]["passed"]
    assert quartic_continuation["hypothesis_outcome"] == "rejected"
    assert quartic_continuation["scientific_classification"] == (
        "quartic continuation does not restore registered radius"
    )
    assert not quartic_continuation["preserved_prior_outcomes"]["revised"]
    json.dumps(quartic_continuation, allow_nan=False)
