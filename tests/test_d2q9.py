from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.d2q9 import (
    D2Q9_VELOCITIES,
    D2Q9_WEIGHTS,
    bgk_periodic_step,
    dense_linearized_map,
    equilibrium,
    exact_uniform_hessian,
    fourier_symbol,
    linearized_periodic_step,
    macroscopic,
    spectrum_audit,
    uniform_center_basis,
    uniform_equilibrium,
)


def test_equilibrium_recovers_conserved_variables() -> None:
    density = np.array([[0.97, 1.03], [1.01, 0.99]])
    momentum = np.array(
        [
            [[0.01, -0.02], [0.015, 0.01]],
            [[-0.02, 0.005], [0.0, -0.01]],
        ]
    )
    populations = equilibrium(density, momentum)
    recovered_density, recovered_momentum = macroscopic(populations)
    np.testing.assert_allclose(recovered_density, density, atol=2.0e-16)
    np.testing.assert_allclose(recovered_momentum, momentum, atol=2.0e-16)


def test_d2q9_quadrature_identities() -> None:
    np.testing.assert_allclose(D2Q9_WEIGHTS.sum(), 1.0)
    np.testing.assert_allclose(D2Q9_WEIGHTS @ D2Q9_VELOCITIES, np.zeros(2))
    second_moment = np.einsum(
        "q,qi,qj->ij", D2Q9_WEIGHTS, D2Q9_VELOCITIES, D2Q9_VELOCITIES
    )
    np.testing.assert_allclose(second_moment, np.eye(2) / 3.0)


def test_uniform_equilibrium_is_an_exact_fixed_family() -> None:
    state = uniform_equilibrium(3, 5, np.array([0.02, 0.01, -0.015]))
    np.testing.assert_allclose(bgk_periodic_step(state, 1.2), state, atol=2.0e-16)


def test_periodic_bgk_step_conserves_global_mass_and_momentum() -> None:
    rng = np.random.default_rng(20260731)
    state = uniform_equilibrium(4, 5, np.zeros(3)) + 1.0e-3 * rng.normal(
        size=(4, 5, 9)
    )
    density_before, momentum_before = macroscopic(state)
    density_after, momentum_after = macroscopic(bgk_periodic_step(state, 1.2))
    np.testing.assert_allclose(density_after.sum(), density_before.sum(), atol=1.0e-14)
    np.testing.assert_allclose(
        momentum_after.sum(axis=(0, 1)),
        momentum_before.sum(axis=(0, 1)),
        atol=1.0e-14,
    )


def test_uniform_center_basis_uses_conserved_coordinate_gauge() -> None:
    tangent, extractor = uniform_center_basis(3, 5)
    np.testing.assert_allclose(extractor @ tangent, np.eye(3), atol=2.0e-16)


def test_dense_jacobian_matches_linearized_operator() -> None:
    ny, nx, omega = 2, 3, 1.2
    rng = np.random.default_rng(20260731)
    delta = rng.normal(size=(ny, nx, 9))
    jacobian = dense_linearized_map(ny, nx, omega)
    np.testing.assert_allclose(
        jacobian @ delta.ravel(),
        linearized_periodic_step(delta, omega).ravel(),
        atol=5.0e-15,
    )


def test_linearized_operator_is_derivative_of_nonlinear_step() -> None:
    ny, nx, omega = 3, 3, 1.2
    rng = np.random.default_rng(20260731)
    base = uniform_equilibrium(ny, nx, np.zeros(3))
    direction = rng.normal(size=base.shape)
    step = 1.0e-6
    finite_difference = (
        bgk_periodic_step(base + step * direction, omega)
        - bgk_periodic_step(base - step * direction, omega)
    ) / (2.0 * step)
    np.testing.assert_allclose(
        finite_difference,
        linearized_periodic_step(direction, omega),
        atol=2.0e-9,
        rtol=2.0e-9,
    )


def test_fourier_blocks_reproduce_dense_periodic_spectrum() -> None:
    size, omega = 3, 1.2
    dense_values = list(np.linalg.eigvals(dense_linearized_map(size, size, omega)))
    block_values: list[complex] = []
    for ix in range(size):
        for iy in range(size):
            block_values.extend(
                np.linalg.eigvals(
                    fourier_symbol(
                        2.0 * np.pi * ix / size,
                        2.0 * np.pi * iy / size,
                        omega,
                    )
                )
            )
    for value in dense_values:
        distances = np.abs(np.asarray(block_values) - value)
        nearest = int(np.argmin(distances))
        assert distances[nearest] < 5.0e-14
        block_values.pop(nearest)
    assert not block_values


def test_grid_parity_exposes_nyquist_unit_modes() -> None:
    even = spectrum_audit(8, 1.2)
    odd = spectrum_audit(9, 1.2)
    assert even["strict_unit_count"] == 5
    assert even["nonzero_wave_unit_count"] == 2
    assert odd["strict_unit_count"] == 3
    assert odd["nonzero_wave_unit_count"] == 0


@pytest.mark.parametrize("omega", [0.5, 1.2, 1.8])
@pytest.mark.parametrize("size", range(3, 11))
def test_grid_parity_unit_mode_count_persists_over_sizes_and_relaxation(
    size: int,
    omega: float,
) -> None:
    audit = spectrum_audit(size, omega)
    expected = 5 if size % 2 == 0 else 3
    assert audit["strict_unit_count"] == expected
    assert audit["nonzero_wave_unit_count"] == expected - 3


@pytest.mark.parametrize("omega", [0.0, 2.0, -0.1, 2.1, np.nan, np.inf])
def test_spectrum_audit_rejects_invalid_relaxation(omega: float) -> None:
    with pytest.raises(ValueError, match="omega"):
        spectrum_audit(5, omega)


@pytest.mark.parametrize("omega", [1.0e-12, 2.0 - 1.0e-12])
def test_spectrum_audit_rejects_unresolved_unit_separation(omega: float) -> None:
    with pytest.raises(ValueError, match="separation is unresolved"):
        spectrum_audit(5, omega)


def test_spectrum_audit_rejects_grid_resolved_near_unit_slow_modes() -> None:
    with pytest.raises(ValueError, match="classification is unresolved"):
        spectrum_audit(9, 2.0 - 1.1e-9)


@pytest.mark.parametrize("tolerance", [0.0, -1.0, 1.0, np.nan, np.inf])
def test_spectrum_audit_rejects_invalid_unit_tolerance(tolerance: float) -> None:
    with pytest.raises(ValueError, match="unit_tolerance"):
        spectrum_audit(5, 1.2, unit_tolerance=tolerance)


@pytest.mark.parametrize("shape", [(0, 3), (3, 0), (-1, 3), (2.5, 3), (True, 3)])
def test_dense_helpers_reject_invalid_grid_shapes(shape: tuple[object, object]) -> None:
    ny, nx = shape
    with pytest.raises(ValueError, match="positive integers"):
        dense_linearized_map(ny, nx, 1.2)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="positive integers"):
        exact_uniform_hessian(ny, nx)  # type: ignore[arg-type]
