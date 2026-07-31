from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.spectra import classify_low_wave_hydrodynamic_modes


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
