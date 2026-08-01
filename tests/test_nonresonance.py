from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.d2q9 import (
    bgk_periodic_step,
    equilibrium_tangent_matrix,
    uniform_equilibrium,
)
from ttim_lbm.nonresonance import (
    add_wave_indices,
    canonical_wave_index,
    orthogonal_acoustic_resonance_witness,
    quadratic_fourier_forcing,
    radial_band_normal_dominance,
    realify_complex_matrix,
    stripe_quadratic_audit,
    wave_vector_from_index,
)


def test_odd_grid_wave_indices_use_centered_modular_arithmetic() -> None:
    assert canonical_wave_index((5, -5), 9) == (-4, 4)
    assert add_wave_indices((4, 0), (1, 0), 9) == (-4, 0)
    assert add_wave_indices((3, -2), (-3, 2), 17) == (0, 0)
    with pytest.raises(ValueError, match="odd integer"):
        canonical_wave_index((1, 0), 16)


def test_realification_duplicates_complex_singular_values() -> None:
    matrix = np.array(
        [[1.0 + 2.0j, -0.3j], [0.4 - 0.2j, -0.7 + 0.1j]],
        dtype=np.complex128,
    )
    complex_singular = np.linalg.svd(matrix, compute_uv=False)
    real_singular = np.linalg.svd(realify_complex_matrix(matrix), compute_uv=False)
    np.testing.assert_allclose(
        np.sort(real_singular),
        np.sort(np.repeat(complex_singular, 2)),
        rtol=1.0e-13,
        atol=1.0e-14,
    )


def test_minimum_shell_has_a_compatible_nonunique_external_resonance() -> None:
    witness = orthogonal_acoustic_resonance_witness(17, 1.2)
    homological = witness["homological"]
    assert witness["output_wave_index"] == [1, 1]
    assert witness["closest_output_hydrodynamic_label"] == "shear"
    assert homological["status"] == "compatible_nonunique"
    assert homological["minimum_eigenvalue_distance"] < 1.0e-12
    assert homological["null_forcing_ratio"] < 1.0e-10


def test_analytic_fourier_forcing_matches_full_map_mixed_difference() -> None:
    size = 17
    omega = 1.2
    step = 1.0e-3
    base = uniform_equilibrium(size, size, np.zeros(3))
    tangent = equilibrium_tangent_matrix()
    left_population = tangent[:, 1]
    right_population = tangent[:, 2]
    y_index, x_index = np.indices((size, size))
    left_field = (
        np.cos(2.0 * np.pi * x_index / size)[..., None] * left_population
    )
    right_field = (
        np.cos(2.0 * np.pi * y_index / size)[..., None] * right_population
    )

    def full_map(delta: np.ndarray) -> np.ndarray:
        return bgk_periodic_step(base + delta, omega)

    mixed_difference = (
        full_map(step * (left_field + right_field))
        - full_map(step * (left_field - right_field))
        - full_map(step * (-left_field + right_field))
        + full_map(-step * (left_field + right_field))
    ) / (4.0 * step**2)
    numerical_coefficient = (
        np.fft.fftn(mixed_difference, axes=(0, 1))[1, 1] / float(size**2)
    )
    analytic_coefficient = 0.25 * quadratic_fourier_forcing(
        left_population,
        right_population,
        wave_vector_from_index((1, 1), size),
        omega,
    )
    np.testing.assert_allclose(
        numerical_coefficient,
        analytic_coefficient,
        rtol=1.0e-9,
        atol=1.0e-11,
    )


def test_stripe_oracle_enforces_fixed_leaf_and_remains_nonsingular() -> None:
    audit = stripe_quadratic_audit(17, 1.2)
    assert audit["fixed_leaf_kinetic_dimension"] == 6
    assert audit["all_sector_statuses"] == ["nonsingular_practical"]
    assert audit["maximum_zero_wave_conservation_residual"] < 1.0e-12
    assert audit["complex_realification_singular_value_relative_error"] < 1.0e-10
    assert audit["second_harmonic_minimum_smallest_singular_value"] > 1.0e-2
    assert audit["second_harmonic_maximum_condition_number"] < 100.0
    with pytest.raises(ValueError, match="avoid 2k aliasing"):
        stripe_quadratic_audit(3, 1.2)


def test_registered_radial_band_lacks_normal_dominance_on_n17() -> None:
    audit = radial_band_normal_dominance(17, 1.2, 0.925486111111111)
    assert audit["finite_grid_normal_attraction"] is False
    assert audit["normal_dominance_ratio"] > 1.0
    assert audit["worst_external_wave_index"] in ([-8, 0], [0, -8])
    assert audit["minimum_ordered_schur_separation"] > 0.02
    assert audit["maximum_master_projector_residual"] < 1.0e-12
