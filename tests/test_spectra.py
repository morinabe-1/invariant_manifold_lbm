from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.spectra import (
    classify_low_wave_hydrodynamic_modes,
    maximum_principal_angle,
    path_reversal_subspace_error,
    track_hydrodynamic_cluster_path,
)


def test_low_wave_classifier_recovers_shear_and_acoustic_polarizations() -> None:
    modes = classify_low_wave_hydrodynamic_modes(0.08, 0.0, 1.2)
    assert modes["shear"].transverse_fraction > 0.999
    assert modes["acoustic_positive"].transverse_fraction < 1.0e-10
    assert modes["acoustic_negative"].transverse_fraction < 1.0e-10
    np.testing.assert_allclose(
        modes["acoustic_positive"].eigenvalue,
        modes["acoustic_negative"].eigenvalue.conjugate(),
        atol=2.0e-15,
    )


@pytest.mark.parametrize("angle", [0.0, np.pi / 8.0, np.pi / 4.0])
def test_small_wave_limits_recover_viscosity_and_sound_speed(angle: float) -> None:
    omega = 1.2
    magnitude = 0.01
    modes = classify_low_wave_hydrodynamic_modes(
        magnitude * np.cos(angle),
        magnitude * np.sin(angle),
        omega,
    )
    effective_viscosity = -np.log(abs(modes["shear"].eigenvalue)) / magnitude**2
    acoustic_speed = (
        abs(np.angle(modes["acoustic_positive"].eigenvalue)) / magnitude
    )
    expected_viscosity = (1.0 / 3.0) * (1.0 / omega - 0.5)
    np.testing.assert_allclose(effective_viscosity, expected_viscosity, rtol=1.0e-5)
    np.testing.assert_allclose(acoustic_speed, 1.0 / np.sqrt(3.0), rtol=1.0e-5)


def test_classifier_rejects_zero_wave_vector() -> None:
    with pytest.raises(ValueError, match=r"1e-6 <= \|k\| <= 0.5"):
        classify_low_wave_hydrodynamic_modes(0.0, 0.0, 1.2)


@pytest.mark.parametrize(
    ("kx", "ky"),
    [(1.0, 0.0), (np.nan, 0.1), (0.1, np.inf)],
)
def test_classifier_rejects_out_of_domain_wave_vectors(kx: float, ky: float) -> None:
    with pytest.raises(ValueError):
        classify_low_wave_hydrodynamic_modes(kx, ky, 1.2)


def test_principal_angle_ignores_basis_rotation_and_internal_permutation() -> None:
    rng = np.random.default_rng(20260731)
    basis, _ = np.linalg.qr(rng.normal(size=(9, 3)))
    internal_rotation, _ = np.linalg.qr(rng.normal(size=(3, 3)))
    assert maximum_principal_angle(basis, basis @ internal_rotation) < 3.0e-8


def test_cluster_tracker_uses_simple_labels_only_away_from_collisions() -> None:
    wave_vectors = [(0.01, 0.0), (0.02, 0.0), (0.03, 0.0)]
    simple = track_hydrodynamic_cluster_path(wave_vectors, 1.2)
    assert simple[0].label_method == "moment_initialization"
    assert all(point.classification == "simple_branches" for point in simple)
    assert all(
        point.schur_separation > 1.0
        and point.schur_invariance_residual < 2.0e-14
        and 1.0 <= point.spectral_projector_norm < 2.0
        and point.spectral_projector_idempotency_residual < 2.0e-14
        and point.spectral_projector_commutator_residual < 2.0e-14
        for point in simple
    )
    clustered = track_hydrodynamic_cluster_path(
        wave_vectors,
        1.2,
        simple_eigenvalue_separation=10.0,
    )
    assert all(point.classification == "invariant_cluster" for point in clustered)
    assert all(not point.branch_eigenvalues for point in clustered)


def test_external_collision_disables_individual_branch_labels() -> None:
    magnitudes = np.linspace(1.0e-3, np.pi - 1.0e-8, 129)
    points = track_hydrodynamic_cluster_path(
        [(float(magnitude), 0.0) for magnitude in magnitudes],
        1.5,
    )
    assert points[-1].external_spectral_separation < 1.0e-10
    assert points[-1].classification == "invariant_cluster"
    assert not points[-1].branch_eigenvalues


def test_cluster_path_reversal_compares_subspaces_not_internal_labels() -> None:
    magnitudes = np.linspace(0.01, 0.4, 13)
    wave_vectors = [(float(value), 0.0) for value in magnitudes]
    forward = track_hydrodynamic_cluster_path(wave_vectors, 1.2)
    backward = track_hydrodynamic_cluster_path(
        list(reversed(wave_vectors)),
        1.2,
        initial_reference_basis=forward[-1].right_basis,
    )
    assert path_reversal_subspace_error(forward, backward) < 6.0e-8
