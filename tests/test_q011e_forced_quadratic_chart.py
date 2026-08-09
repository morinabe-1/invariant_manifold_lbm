from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import research.q011e_forced_quadratic_chart as q011e
from ttim_lbm.d2q9 import exact_uniform_hessian, uniform_equilibrium
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011e_cycle() -> dict:
    return q011e.run_forced_quadratic_chart_audit()


def test_q011e_general_equilibrium_hessian_reduces_to_rest_formula() -> None:
    rest = uniform_equilibrium(
        q011e.SIZE,
        q011e.SIZE,
        np.zeros(3),
    )
    observed = q011e._local_equilibrium_hessian(rest)
    expected = exact_uniform_hessian(q011e.SIZE, q011e.SIZE).reshape(
        q011e.SIZE,
        q011e.SIZE,
        9,
        3,
        3,
    )

    np.testing.assert_allclose(observed, expected, rtol=0.0, atol=0.0)
    np.testing.assert_allclose(
        observed,
        observed.swapaxes(-1, -2),
        rtol=0.0,
        atol=0.0,
    )


def test_q011e_replays_q011d_and_preserves_prior_outcomes(
    q011e_cycle: dict,
) -> None:
    audit = q011e_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["q011d_artifact"]["study_validity"] == "passed"
    assert audit["q011d_artifact"]["hypothesis_outcome"] == "accepted"
    assert audit["preserved_prior_outcomes"] == {
        "q011c1_study_validity": "passed",
        "q011c1_hypothesis_outcome": "accepted",
        "q011c_study_validity": "failed",
        "q011c_hypothesis_outcome": "inconclusive",
    }


def test_q011e_invariant_schur_and_real_linear_coordinates_pass(
    q011e_cycle: dict,
) -> None:
    complex_audit = q011e_cycle["complex_linear_coordinate_audit"]
    real_audit = q011e_cycle["real_linear_coordinate_audit"]

    assert [record["selected_dimension"] for record in complex_audit["selected_block_records"]] == [
        6,
        9,
        9,
    ]
    assert complex_audit["maximum_structural_residual"] <= (q011e.STRUCTURAL_TOLERANCE)
    assert complex_audit["passed"]
    assert all(complex_audit["checks"].values())
    assert len(real_audit["candidate_singular_values"]) == 2 * q011e.SELECTED_DIMENSION
    assert real_audit["complex_range_relative_residual"] <= (q011e.STRUCTURAL_TOLERANCE)
    assert real_audit["coordinate_map_unitarity_frobenius_residual"] <= (q011e.STRUCTURAL_TOLERANCE)
    assert real_audit["real_extractor_duality_frobenius_residual"] <= (q011e.STRUCTURAL_TOLERANCE)
    assert real_audit["real_linear_invariance_relative_residual"] <= (q011e.STRUCTURAL_TOLERANCE)
    assert real_audit["passed"]
    assert all(real_audit["checks"].values())


def test_q011e_independent_forced_hessian_campaign_passes(
    q011e_cycle: dict,
) -> None:
    audit = q011e_cycle["independent_hessian_audit"]

    assert audit["direction_pair_count"] == 16
    assert len(audit["direction_records"]) == 16
    assert audit["maximum_analytic_relative_discrepancy"] <= (q011e.HESSIAN_DISCREPANCY_TOLERANCE)
    assert audit["maximum_coarse_to_fine_relative_change"] <= (q011e.HESSIAN_STEP_CHANGE_TOLERANCE)
    assert audit["minimum_analytic_directional_hessian_norm"] >= (
        q011e.HESSIAN_DIRECTIONAL_NORM_FLOOR
    )
    assert audit["minimum_input_or_mapped_population"] > 0.0
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]
    assert all(audit["checks"].values())
    assert all(audit["hypothesis_checks"].values())


def test_q011e_all_quadratic_coefficients_satisfy_the_homological_equation(
    q011e_cycle: dict,
) -> None:
    audit = q011e_cycle["quadratic_construction_audit"]

    assert audit["pair_count"] == 300
    assert len(audit["pair_records"]) == 300
    assert [record["pair_count"] for record in audit["sector_records"]] == [
        102,
        54,
        54,
        45,
        45,
    ]
    assert audit["maximum_sector_sylvester_relative_residual"] <= (
        q011e.SYLVESTER_RESIDUAL_TOLERANCE
    )
    assert audit["full_homological_relative_residual"] <= (q011e.HOMOLOGICAL_RELATIVE_TOLERANCE)
    assert audit["maximum_pairwise_homological_relative_residual"] <= (
        q011e.PAIRWISE_HOMOLOGICAL_TOLERANCE
    )
    assert audit["graph_gauge_relative_residual"] <= (q011e.GRAPH_GAUGE_TOLERANCE)
    assert audit["hessian_global_conservation_relative_residual"] <= (q011e.CONSERVATION_TOLERANCE)
    assert audit["zero_kx_hessian_global_conservation_relative_residual"] <= (
        q011e.CONSERVATION_TOLERANCE
    )
    assert audit["chart_hessian_kx_leakage_relative_norm"] <= (q011e.FOURIER_LEAKAGE_TOLERANCE)
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]
    assert all(audit["structural_checks"].values())
    assert all(audit["hypothesis_checks"].values())


def test_q011e_real_quadratic_chart_passes_structural_checks(
    q011e_cycle: dict,
) -> None:
    audit = q011e_cycle["real_quadratic_audit"]

    assert audit["analytic_transform_relative_residual"] <= (q011e.STRUCTURAL_TOLERANCE)
    assert audit["chart_hessian_imaginary_leakage_relative_norm"] <= (q011e.STRUCTURAL_TOLERANCE)
    assert audit["real_graph_gauge_relative_residual"] <= (q011e.GRAPH_GAUGE_TOLERANCE)
    assert audit["real_hessian_global_conservation_relative_residual"] <= (
        q011e.CONSERVATION_TOLERANCE
    )
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]
    assert all(audit["structural_checks"].values())
    assert all(audit["hypothesis_checks"].values())


def test_q011e_registered_residual_window_is_underresolved(
    q011e_cycle: dict,
) -> None:
    audit = q011e_cycle["residual_order_audit"]

    assert audit["direction_count"] == 32
    assert audit["amplitudes"] == list(q011e.RESIDUAL_AMPLITUDES)
    assert audit["slope_eligible_direction_count"] == 0
    assert audit["degenerate_direction_count"] == 32
    assert all(
        record["linear_fit_point_count"] == 5
        and record["quadratic_fit_point_count"] == 1
        and not record["slope_eligible"]
        for record in audit["direction_records"]
    )
    assert audit["maximum_largest_amplitude_residual_ratio"] < 1.0e-3
    assert audit["minimum_chart_or_mapped_population"] > 0.0
    assert audit["maximum_global_conservation_drift"] <= (q011e.CONSERVATION_TOLERANCE)
    assert audit["structural_passed"]
    assert not audit["hypothesis_passed"]
    assert all(audit["checks"].values())
    assert not audit["hypothesis_checks"]["at_least_twenty_eight_directions_are_slope_eligible"]
    assert not audit["hypothesis_checks"]["eligible_linear_slopes_are_second_order"]
    assert not audit["hypothesis_checks"]["eligible_quadratic_slopes_are_third_order"]
    assert audit["hypothesis_checks"]["largest_amplitude_residual_improves"]
    assert audit["hypothesis_checks"]["all_chart_and_mapped_states_are_positive"]
    assert audit["hypothesis_checks"]["global_conservation_drift_is_within_tolerance"]


def test_q011e_is_valid_but_rejects_the_registered_slope_gate(
    q011e_cycle: dict,
) -> None:
    assert len(q011e_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011e_cycle["validity_gates"].values())
    assert len(q011e_cycle["hypothesis_gates"]) == 6
    failed = [name for name, gate in q011e_cycle["hypothesis_gates"].items() if not gate["passed"]]
    assert failed == ["linear_and_quadratic_residual_orders_pass"]
    assert q011e_cycle["study_validity"] == "passed"
    assert q011e_cycle["hypothesis_outcome"] == "rejected"
    assert q011e_cycle["scientific_classification"] == (
        "the forced fixed-leaf quadratic chart is constructed, but the "
        "registered residual-order window is underresolved"
    )
    assert q011e_cycle["next_change"] == (
        "Preregister Q011e1 with a larger independent residual-amplitude "
        "window while preserving the Q011e noise floor and slope thresholds."
    )
    consequence = q011e_cycle["numerical_consequence"]
    assert consequence["fixed_conservation_leaf_is_used"]
    assert consequence["dense_forced_quadratic_chart_is_constructed"]
    assert not consequence["registered_residual_order_is_confirmed"]
    assert not consequence["zero_wave_center_coordinates_are_included"]
    assert not consequence["forced_ssm_exists_or_is_unique"]
    assert not any(q011e_cycle["preserved_prior_outcomes"].values())


def test_q011e_records_reproducible_digests_and_provenance(
    q011e_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011e_cycle["registered_parameters"],
        "sealed_input_audit": q011e_cycle["sealed_input_audit"],
    }
    derivative_sections = {
        "complex_linear_coordinate_audit": q011e_cycle["complex_linear_coordinate_audit"],
        "real_linear_coordinate_audit": q011e_cycle["real_linear_coordinate_audit"],
        "independent_hessian_audit": q011e_cycle["independent_hessian_audit"],
    }
    chart_sections = {
        "quadratic_construction_audit": q011e_cycle["quadratic_construction_audit"],
        "real_quadratic_audit": q011e_cycle["real_quadratic_audit"],
    }
    residual_sections = {
        "residual_order_audit": q011e_cycle["residual_order_audit"],
    }

    assert q011e_cycle["input_digest_sha256"] == (
        q011e.q011c._canonical_json_sha256(input_sections)
    )
    assert q011e_cycle["derivative_digest_sha256"] == (
        q011e.q011c._canonical_json_sha256(derivative_sections)
    )
    assert q011e_cycle["chart_digest_sha256"] == (
        q011e.q011c._canonical_json_sha256(chart_sections)
    )
    assert q011e_cycle["residual_digest_sha256"] == (
        q011e.q011c._canonical_json_sha256(residual_sections)
    )
    assert q011e_cycle["result_digest_sha256"] == (
        q011e.q011c._canonical_json_sha256(q011e._result_digest_sections(q011e_cycle))
    )
    runner_path = Path(q011e.__file__).resolve()
    assert q011e_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    json.dumps(q011e_cycle, allow_nan=False)
