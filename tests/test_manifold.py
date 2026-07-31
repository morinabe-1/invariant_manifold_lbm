from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.d2q9 import (
    bgk_periodic_step,
    dense_linearized_map,
    exact_uniform_hessian,
    uniform_center_basis,
    uniform_equilibrium,
)
from ttim_lbm.manifold import (
    QuadraticChart,
    invariance_residual,
    log_log_slope,
    second_derivative_tensor,
    solve_identity_center_quadratic,
)


def test_quadratic_homological_solve_recovers_uniform_center_curvature() -> None:
    ny = nx = 3
    omega = 1.2
    base = uniform_equilibrium(ny, nx, np.zeros(3)).ravel()
    tangent, extractor = uniform_center_basis(ny, nx)
    jacobian = dense_linearized_map(ny, nx, omega)

    def full_map(flat_state: np.ndarray) -> np.ndarray:
        return bgk_periodic_step(flat_state.reshape(ny, nx, 9), omega).ravel()

    second = second_derivative_tensor(full_map, base, tangent)
    hessian, reduced_hessian, diagnostics = solve_identity_center_quadratic(
        jacobian, tangent, extractor, second
    )
    np.testing.assert_allclose(hessian, exact_uniform_hessian(ny, nx), atol=2.0e-7)
    np.testing.assert_allclose(extractor @ hessian.reshape(base.size, -1), 0.0, atol=2.0e-13)
    np.testing.assert_allclose(reduced_hessian, 0.0, atol=2.0e-8)
    assert diagnostics.global_equation_relative_residual < 2.0e-10
    assert diagnostics.maximum_gauge_residual < 2.0e-13
    assert diagnostics.augmented_rank == diagnostics.augmented_dimension
    assert diagnostics.condition_number < 1.0e4


def test_quadratic_chart_raises_observed_residual_order() -> None:
    ny = nx = 3
    omega = 1.2
    base = uniform_equilibrium(ny, nx, np.zeros(3)).ravel()
    tangent, _ = uniform_center_basis(ny, nx)

    def full_map(flat_state: np.ndarray) -> np.ndarray:
        return bgk_periodic_step(flat_state.reshape(ny, nx, 9), omega).ravel()

    linear = QuadraticChart(base, tangent, np.zeros((base.size, 3, 3)))
    quadratic = QuadraticChart(base, tangent, exact_uniform_hessian(ny, nx))
    direction = np.array([0.35, 0.72, -0.48])
    direction /= np.linalg.norm(direction)
    amplitudes = np.array([0.0025, 0.005, 0.01, 0.02])
    linear_residuals = [
        invariance_residual(full_map, linear, amplitude * direction)
        for amplitude in amplitudes
    ]
    quadratic_residuals = [
        invariance_residual(full_map, quadratic, amplitude * direction)
        for amplitude in amplitudes
    ]
    assert 1.8 < log_log_slope(amplitudes, linear_residuals) < 2.2
    assert log_log_slope(amplitudes, quadratic_residuals) > 2.7
    assert quadratic_residuals[-1] < linear_residuals[-1]


def test_quadratic_chart_normalizes_array_like_inputs() -> None:
    chart = QuadraticChart(
        base=[1.0, 2.0],
        tangent=[[1.0], [0.5]],
        hessian=[[[2.0]], [[-1.0]]],
    )
    np.testing.assert_allclose(chart.evaluate([0.2]), [1.24, 2.08])


def test_second_derivative_supports_coordinate_wise_steps() -> None:
    def polynomial_map(state: np.ndarray) -> np.ndarray:
        x, y = state
        return np.array([x * x + 3.0 * x * y, 2.0 * y * y])

    actual = second_derivative_tensor(
        polynomial_map,
        np.zeros(2),
        np.eye(2),
        step=np.array([1.0e-3, 2.0e-3]),
    )
    expected = np.array(
        [
            [[2.0, 3.0], [3.0, 0.0]],
            [[0.0, 0.0], [0.0, 4.0]],
        ]
    )
    np.testing.assert_allclose(actual, expected, atol=1.0e-12)


def test_homological_solver_rejects_inexact_coordinate_duality() -> None:
    ny = nx = 3
    tangent, extractor = uniform_center_basis(ny, nx)
    dimension = tangent.shape[0]
    with pytest.raises(ValueError, match="L @ V"):
        solve_identity_center_quadratic(
            np.eye(dimension),
            tangent,
            (1.0 + 1.0e-8) * extractor,
            np.zeros((dimension, 3, 3)),
        )


def test_homological_solver_rejects_unresolved_extra_center_modes() -> None:
    tangent = np.array([[1.0], [0.0]])
    extractor = np.array([[1.0, 0.0]])
    with pytest.raises(np.linalg.LinAlgError, match="rank deficient"):
        solve_identity_center_quadratic(
            np.eye(2),
            tangent,
            extractor,
            np.zeros((2, 1, 1)),
        )
