from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.d2q9 import (
    exact_uniform_hessian,
    uniform_center_basis,
    uniform_equilibrium,
)
from ttim_lbm.manifold import QuadraticChart
from ttim_lbm.tensor_train import (
    evaluate_polynomial,
    polynomial_coefficient_tensor,
    reconstruct,
    tt_ranks,
    tt_svd,
)


def test_tt_svd_reconstructs_general_tensor() -> None:
    rng = np.random.default_rng(20260731)
    tensor = rng.normal(size=(4, 3, 2, 5))
    cores = tt_svd(tensor)
    np.testing.assert_allclose(reconstruct(cores), tensor, atol=2.0e-14)


def test_polynomial_tt_matches_dense_quadratic_chart() -> None:
    ny = nx = 3
    base = uniform_equilibrium(ny, nx, np.zeros(3)).ravel()
    tangent, _ = uniform_center_basis(ny, nx)
    hessian = exact_uniform_hessian(ny, nx)
    chart = QuadraticChart(base, tangent, hessian)
    coefficients = polynomial_coefficient_tensor(base, tangent, hessian)
    cores = tt_svd(coefficients, relative_tolerance=1.0e-13)
    coordinate = np.array([0.01, -0.015, 0.007])
    np.testing.assert_allclose(
        evaluate_polynomial(cores, coordinate),
        chart.evaluate(coordinate),
        atol=2.0e-13,
    )


def test_zero_tensor_uses_rank_one_cores() -> None:
    tensor = np.zeros((7, 3, 4, 2))
    cores = tt_svd(tensor, relative_tolerance=1.0e-12)
    assert tt_ranks(cores) == [1, 1, 1, 1, 1]
    np.testing.assert_array_equal(reconstruct(cores), tensor)


@pytest.mark.parametrize("max_rank", [0, -1, 1.5, True])
def test_tt_svd_rejects_invalid_max_rank(max_rank: object) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        tt_svd(np.ones(3), max_rank=max_rank)  # type: ignore[arg-type]


@pytest.mark.parametrize("tolerance", [np.nan, np.inf, -1.0])
def test_tt_svd_rejects_invalid_tolerance(tolerance: float) -> None:
    with pytest.raises(ValueError, match="finite and nonnegative"):
        tt_svd(np.ones((2, 2)), relative_tolerance=tolerance)


def test_tt_svd_rejects_unresolvable_float64_tolerance() -> None:
    with pytest.raises(ValueError, match="too close to float64 roundoff"):
        tt_svd(np.ones((2, 2)), relative_tolerance=1.0e-16)


def test_rank_cap_cannot_silently_override_requested_tolerance() -> None:
    rng = np.random.default_rng(20260731)
    tensor = rng.normal(size=(8, 7, 6, 5))
    with pytest.raises(ValueError, match="prevents TT-SVD"):
        tt_svd(tensor, relative_tolerance=1.0e-12, max_rank=2)
    best_effort = tt_svd(tensor, relative_tolerance=0.0, max_rank=2)
    assert max(tt_ranks(best_effort)) <= 2


def test_tt_svd_handles_large_finite_scale() -> None:
    tensor = np.arange(1.0, 17.0).reshape(4, 4) * 1.0e200
    cores = tt_svd(tensor, relative_tolerance=1.0e-12)
    relative_error = np.linalg.norm(
        reconstruct(cores) / 1.0e200 - tensor / 1.0e200
    ) / np.linalg.norm(tensor / 1.0e200)
    assert relative_error < 1.0e-12


def test_tt_svd_rejects_unrepresentable_frobenius_norm() -> None:
    tensor = np.arange(1.0, 17.0).reshape(4, 4) * 1.0e307
    with pytest.raises(ValueError, match="Frobenius norm"):
        tt_svd(tensor, relative_tolerance=1.0e-12)
