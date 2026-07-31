from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from ttim_lbm.manifold import (
    second_derivative_tensor,
    solve_general_quadratic_parameterization,
)
from ttim_lbm.manufactured import (
    make_manufactured_quadratic_map,
    real_basis_from_dominant_complex_pair,
)


def test_manufactured_chart_is_exactly_invariant_with_nontrivial_reduced_map() -> None:
    model = make_manufactured_quadratic_map()
    assert np.linalg.norm(model.reduced_hessian) > 0.0
    for coordinates in (
        np.array([0.10, 0.05]),
        np.array([-0.08, 0.03]),
        np.array([0.02, -0.11]),
    ):
        lifted = model.chart.evaluate(coordinates)
        expected = model.chart.evaluate(model.reduced_map(coordinates))
        np.testing.assert_allclose(model.full_map(lifted), expected, atol=2.0e-16)


def test_general_homological_solver_recovers_manufactured_coefficients() -> None:
    model = make_manufactured_quadratic_map()
    hessian, reduced_hessian, diagnostics = solve_general_quadratic_parameterization(
        model.jacobian,
        model.tangent,
        model.extractor,
        model.reduced_linear,
        model.second_derivative,
    )
    np.testing.assert_allclose(
        hessian,
        model.chart_hessian,
        atol=8.0e-15,
        rtol=0.0,
    )
    np.testing.assert_allclose(
        reduced_hessian,
        model.reduced_hessian,
        atol=8.0e-15,
        rtol=0.0,
    )
    assert diagnostics.augmented_rank == diagnostics.augmented_dimension
    assert diagnostics.global_equation_relative_residual < 5.0e-14
    assert diagnostics.maximum_gauge_residual < 5.0e-15


def test_manufactured_derivative_matches_centered_finite_difference() -> None:
    model = make_manufactured_quadratic_map()
    actual = second_derivative_tensor(
        model.full_map,
        np.zeros(5),
        model.tangent,
        step=1.0e-4,
    )
    np.testing.assert_allclose(actual, model.second_derivative, atol=2.0e-8)


def test_real_complex_pair_conversion_recovers_real_rotation_block() -> None:
    model = make_manufactured_quadratic_map()
    pair = real_basis_from_dominant_complex_pair(model.jacobian)
    np.testing.assert_allclose(
        pair.block,
        model.reduced_linear,
        atol=2.0e-15,
        rtol=0.0,
    )
    np.testing.assert_allclose(
        pair.left_extractor @ pair.right_basis,
        np.eye(2),
        atol=5.0e-15,
        rtol=0.0,
    )
    assert pair.right_invariance_residual < 5.0e-15
    assert pair.left_invariance_residual < 5.0e-15
    assert pair.duality_residual < 5.0e-15
    assert pair.conjugacy_error < 2.0e-15
    assert np.linalg.norm(model.extractor - np.linalg.pinv(model.tangent)) > 0.1


def test_manufactured_model_rejects_asymmetric_or_off_gauge_hessians() -> None:
    model = make_manufactured_quadratic_map()
    asymmetric = model.chart_hessian.copy()
    asymmetric[2, 0, 1] += 0.1
    with pytest.raises(ValueError, match="symmetric"):
        replace(model, chart_hessian=asymmetric)

    off_gauge = model.chart_hessian.copy()
    off_gauge += np.einsum(
        "ir,rjk->ijk",
        model.tangent,
        np.ones((2, 2, 2)),
    )
    with pytest.raises(ValueError, match="graph gauge"):
        replace(model, chart_hessian=off_gauge)


def test_general_solver_rejects_complex_input_without_real_block_conversion() -> None:
    model = make_manufactured_quadratic_map()
    complex_jacobian = model.jacobian.astype(np.complex128)
    complex_jacobian[0, 0] += 1.0j
    with pytest.raises(ValueError, match="explicit real-block"):
        solve_general_quadratic_parameterization(
            complex_jacobian,
            model.tangent,
            model.extractor,
            model.reduced_linear,
            model.second_derivative,
        )
    with pytest.raises(ValueError, match="matrix must be real"):
        real_basis_from_dominant_complex_pair(complex_jacobian)


def test_homological_condition_number_detects_mean_sector_near_resonance() -> None:
    multipliers = [0.25, 0.60, 0.66, 0.671, 0.6723]
    conditions = []
    smallest_singular_values = []
    for multiplier in multipliers:
        model = make_manufactured_quadratic_map(multiplier)
        _, _, diagnostics = solve_general_quadratic_parameterization(
            model.jacobian,
            model.tangent,
            model.extractor,
            model.reduced_linear,
            model.second_derivative,
        )
        conditions.append(diagnostics.condition_number)
        smallest_singular_values.append(diagnostics.smallest_singular_value)
    assert np.all(np.diff(conditions) > 0.0)
    assert np.all(np.diff(smallest_singular_values) < 0.0)
    assert conditions[-1] > 1.0e3 * conditions[0]


def test_exact_quadratic_resonance_is_rejected() -> None:
    model = make_manufactured_quadratic_map(0.82**2)
    with pytest.raises(np.linalg.LinAlgError, match="rank deficient"):
        solve_general_quadratic_parameterization(
            model.jacobian,
            model.tangent,
            model.extractor,
            model.reduced_linear,
            model.second_derivative,
        )
