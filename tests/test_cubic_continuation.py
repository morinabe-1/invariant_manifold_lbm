from __future__ import annotations

import json

import pytest

from ttim_lbm.cubic_continuation import run_cubic_continuation_audit


@pytest.fixture(scope="module")
def cubic_continuation():
    return run_cubic_continuation_audit()


def test_q007b_passes_independent_construction_validity(
    cubic_continuation,
) -> None:
    derivative = cubic_continuation["independent_derivative"]["summary"]
    coefficients = cubic_continuation["coefficient_construction"]["summary"]

    assert cubic_continuation["study_validity"] == "passed"
    assert all(
        gate["passed"] for gate in cubic_continuation["validity_gates"].values()
    )
    assert derivative["minimum_analytic_derivative_norm"] > 1.0e-12
    assert derivative["maximum_best_relative_error"] <= 5.0e-4
    assert coefficients["triple_count"] == 2600
    assert coefficients["sector_counts"] == {
        "zero_wave_kinetic": 108,
        "internal_selected": 1044,
        "external": 1448,
    }
    assert coefficients["numerically_singular_block_count"] == 0
    assert coefficients["maximum_condition_number"] == pytest.approx(
        10821.814847751179
    )


def test_q007b_coefficients_pass_equation_symmetry_and_leaf_gates(
    cubic_continuation,
) -> None:
    construction = cubic_continuation["coefficient_construction"]
    summary = construction["summary"]
    conjugacy = construction["conjugacy_audit"]
    c4 = cubic_continuation["c4_equivariance"]["summary"]

    assert summary["maximum_solve_relative_residual"] <= 1.0e-10
    assert summary["maximum_homological_relative_residual"] <= 1.0e-10
    assert summary["maximum_graph_gauge_relative_residual"] <= 1.0e-10
    assert (
        summary["maximum_zero_wave_forcing_conservation_relative_residual"]
        <= 1.0e-10
    )
    assert (
        summary["maximum_zero_wave_coefficient_conservation_relative_residual"]
        <= 1.0e-10
    )
    assert conjugacy["missing_conjugate_count"] == 0
    assert conjugacy["maximum_coefficient_conjugacy_relative_residual"] <= 1.0e-10
    assert c4["maximum_chart_relative_error"] <= 1.0e-10
    assert c4["maximum_reduced_map_relative_error"] <= 1.0e-10


def test_q007b_raises_residual_order_but_fails_the_registered_ratio(
    cubic_continuation,
) -> None:
    summary = cubic_continuation["residual_order_campaign"]["summary"]
    gates = cubic_continuation["hypothesis_gates"]

    assert 2.9 <= summary["minimum_quadratic_slope"]
    assert summary["maximum_quadratic_slope"] <= 3.1
    assert 3.85 <= summary["minimum_cubic_slope"]
    assert summary["maximum_cubic_slope"] <= 4.15
    assert gates["held_out_residual_orders"]["passed"]
    assert summary["maximum_directional_residual_ratio"] > 0.10
    assert summary["residual_ratio_failure_count"] == 9
    assert not gates["held_out_residual_ratio"]["passed"]


def test_q007b_passes_shadowing_and_forward_error_gates(
    cubic_continuation,
) -> None:
    summary = cubic_continuation["shadowing_campaign"]["summary"]
    ratios = summary["maximum_directional_improvement_ratios"]

    assert all(ratio <= 0.8 for ratio in ratios.values())
    assert summary["cubic_budget_component_check_count"] == 9600
    assert summary["cubic_budget_violation_count"] == 0
    assert summary["maximum_final_component_budget"] <= 1.2e-11
    assert cubic_continuation["hypothesis_gates"][
        "held_out_directional_shadowing_ratios"
    ]["passed"]
    assert cubic_continuation["hypothesis_gates"][
        "cubic_shadowing_forward_error_budget"
    ]["passed"]


def test_q007b_records_a_valid_performance_rejection(
    cubic_continuation,
) -> None:
    assert cubic_continuation["hypothesis_outcome"] == "rejected"
    assert cubic_continuation["scientific_classification"] == (
        "cubic continuation does not improve the registered chart"
    )
    assert not cubic_continuation["preserved_prior_outcome"]["revised"]
    assert "not a quartic" in cubic_continuation["claim_boundary"]
    json.dumps(cubic_continuation, allow_nan=False)
