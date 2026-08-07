from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.d2q9 import global_conserved_quantities
from ttim_lbm.full2d_chart import (
    build_full2d_quadratic_model,
    run_full2d_quadratic_audit,
)


@pytest.fixture(scope="module")
def full2d_model():
    return build_full2d_quadratic_model()


@pytest.fixture(scope="module")
def full2d_audit():
    return run_full2d_quadratic_audit()


def test_full2d_model_solves_all_registered_homological_blocks(
    full2d_model,
) -> None:
    diagnostics = full2d_model.diagnostics

    assert full2d_model.chart.base.shape == (2601,)
    assert full2d_model.chart.tangent.shape == (2601, 24)
    assert full2d_model.chart.hessian.shape == (2601, 24, 24)
    assert full2d_model.reduced_hessian.shape == (24, 24, 24)
    assert diagnostics.pair_count == 300
    assert diagnostics.zero_wave_pair_count == 36
    assert diagnostics.internal_output_pair_count == 108
    assert diagnostics.external_output_pair_count == 156
    assert diagnostics.numerical_singular_block_count == 0
    assert diagnostics.maximum_operator_condition_number == pytest.approx(
        14513.930547954875
    )
    assert diagnostics.maximum_solve_relative_residual < 1.0e-10
    assert diagnostics.homological_relative_residual < 1.0e-10
    assert diagnostics.graph_gauge_relative_residual < 1.0e-10
    assert diagnostics.hessian_conservation_relative_residual < 1.0e-10
    assert diagnostics.complex_conjugacy_relative_residual < 1.0e-10
    assert diagnostics.c4_hessian_relative_residual < 1.0e-10
    assert diagnostics.hessian_fourier_leakage_relative_norm < 1.0e-12


def test_full2d_model_has_all_registered_nonlinear_outputs(full2d_model) -> None:
    diagnostics = full2d_model.diagnostics

    assert diagnostics.reduced_hessian_frobenius_norm > 0.6
    assert diagnostics.zero_wave_hessian_frobenius_norm > 0.07
    assert diagnostics.axial_second_harmonic_hessian_frobenius_norm > 0.47
    assert diagnostics.diagonal_second_harmonic_hessian_frobenius_norm > 0.24


def test_full2d_chart_stays_on_the_fixed_conservation_leaf(full2d_model) -> None:
    direction = np.arange(1.0, 25.0)
    coordinates = 0.01 * direction / np.linalg.norm(direction)
    base_conserved = global_conserved_quantities(
        full2d_model.chart.base.reshape(17, 17, 9)
    )
    chart_conserved = global_conserved_quantities(
        full2d_model.chart.evaluate(coordinates).reshape(17, 17, 9)
    )
    np.testing.assert_allclose(chart_conserved, base_conserved, atol=2.0e-13)


def test_sealed_q006i_is_valid_but_rejects_only_the_conservation_gate(
    full2d_audit,
) -> None:
    assert full2d_audit["study_validity"] == "passed"
    assert full2d_audit["hypothesis_outcome"] == "rejected"
    assert full2d_audit["scientific_classification"] == (
        "Q006i local chart hypothesis rejected"
    )
    assert all(
        gate["passed"] for gate in full2d_audit["validity_gates"].values()
    )
    failed = [
        name
        for name, gate in full2d_audit["hypothesis_gates"].items()
        if not gate["passed"]
    ]
    assert failed == ["global_conservation"]
    assert full2d_audit["hypothesis_gates"]["global_conservation"][
        "value"
    ] == pytest.approx(2.728496323152741e-12)


def test_sealed_q006i_passes_residual_and_shadowing_gates(full2d_audit) -> None:
    residual = full2d_audit["residual_order_campaign"]["summary"]
    shadow = full2d_audit["shadowing_campaign"]

    assert 1.9 <= residual["minimum_linear_slope"]
    assert residual["maximum_linear_slope"] <= 2.1
    assert 2.9 <= residual["minimum_quadratic_slope"]
    assert residual["maximum_quadratic_slope"] <= 3.1
    assert residual["maximum_directional_residual_ratio"] < 0.1
    assert shadow["quadratic"]["summary"]["maximum_absolute_error"] < 1.0e-5
    assert (
        shadow["quadratic"]["summary"][
            "maximum_perturbation_relative_error"
        ]
        < 1.0e-2
    )
    assert shadow["maximum_absolute_error_improvement_ratio"] < 0.1


def test_sealed_q006i_result_is_strict_json(full2d_audit) -> None:
    json.dumps(full2d_audit, allow_nan=False)


@pytest.mark.parametrize(
    ("size", "omega", "eta"),
    [(15, 1.5, 0.01), (17, 1.2, 0.01), (17, 1.5, 0.02)],
)
def test_full2d_model_rejects_unregistered_parameters(
    size: int,
    omega: float,
    eta: float,
) -> None:
    with pytest.raises(ValueError, match="sealed Q006i"):
        build_full2d_quadratic_model(size=size, omega=omega, eta=eta)


def test_full2d_model_checks_state_and_coordinate_dimensions(full2d_model) -> None:
    with pytest.raises(ValueError, match="state dimension"):
        full2d_model.full_map(np.zeros(2600))
    with pytest.raises(ValueError, match="coordinate dimension"):
        full2d_model.reduced_map(np.zeros(23))
