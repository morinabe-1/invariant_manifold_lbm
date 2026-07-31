"""Physical classification of low-wave-number D2Q9 Fourier modes."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

from .d2q9 import (
    conserved_moment_matrix,
    equilibrium_tangent_matrix,
    fourier_symbol,
)

ComplexArray = npt.NDArray[np.complex128]


@dataclass(frozen=True)
class ClassifiedMode:
    """One Fourier eigenmode with its physical participation diagnostics."""

    label: str
    eigenvalue: complex
    right_eigenvector: ComplexArray
    conserved_moments: ComplexArray
    hydrodynamic_score: float
    transverse_fraction: float


def classify_low_wave_hydrodynamic_modes(
    kx: float,
    ky: float,
    omega: float,
) -> dict[str, ClassifiedMode]:
    """Classify shear and acoustic modes by moment content at nonzero low k.

    This is a local classifier, not yet a full branch-continuation algorithm.
    It is intentionally restricted to wave numbers where the three modes with
    largest equilibrium-tangent participation form the hydrodynamic cluster.
    """

    if not np.isfinite(kx) or not np.isfinite(ky):
        raise ValueError("wave-vector components must be finite")
    magnitude = float(np.hypot(kx, ky))
    if not 1.0e-6 <= magnitude <= 0.5:
        raise ValueError(
            "local mode classification requires 1e-6 <= |k| <= 0.5"
        )

    eigenvalues, right = np.linalg.eig(fourier_symbol(kx, ky, omega))
    moments = conserved_moment_matrix()
    projector = equilibrium_tangent_matrix() @ moments
    tangent = np.array([kx, ky], dtype=np.float64) / magnitude
    transverse = np.array([-tangent[1], tangent[0]])

    diagnostics: list[tuple[float, float, int, ComplexArray]] = []
    for index in range(9):
        vector = right[:, index]
        conserved = moments @ vector
        hydro_score = float(np.linalg.norm(projector @ vector) / np.linalg.norm(vector))
        conserved_norm = max(float(np.linalg.norm(conserved)), np.finfo(float).eps)
        transverse_fraction = float(
            abs(transverse @ conserved[1:]) / conserved_norm
        )
        diagnostics.append(
            (hydro_score, transverse_fraction, index, conserved)
        )

    selected = sorted(diagnostics, key=lambda item: item[0], reverse=True)[:3]
    shear_diagnostic = max(selected, key=lambda item: item[1])
    acoustic_diagnostics = [
        item for item in selected if item[2] != shear_diagnostic[2]
    ]
    acoustic_diagnostics.sort(
        key=lambda item: eigenvalues[item[2]].imag,
        reverse=True,
    )

    def build(label: str, diagnostic: tuple[float, float, int, ComplexArray]) -> ClassifiedMode:
        hydro_score, transverse_fraction, index, conserved = diagnostic
        return ClassifiedMode(
            label=label,
            eigenvalue=complex(eigenvalues[index]),
            right_eigenvector=np.asarray(right[:, index], dtype=np.complex128),
            conserved_moments=np.asarray(conserved, dtype=np.complex128),
            hydrodynamic_score=hydro_score,
            transverse_fraction=transverse_fraction,
        )

    classified = {
        "shear": build("shear", shear_diagnostic),
        "acoustic_positive": build(
            "acoustic_positive", acoustic_diagnostics[0]
        ),
        "acoustic_negative": build(
            "acoustic_negative", acoustic_diagnostics[1]
        ),
    }
    conjugacy_error = abs(
        classified["acoustic_positive"].eigenvalue
        - classified["acoustic_negative"].eigenvalue.conjugate()
    )
    if (
        conjugacy_error > 1.0e-8
        or classified["shear"].transverse_fraction < 0.5
    ):
        raise ValueError(
            "moment diagnostics do not resolve a shear/acoustic hydrodynamic cluster"
        )
    return classified
