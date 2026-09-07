"""Subspace-based D3Q27 spectral diagnostics for the Q012b experiment."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import product
from typing import Any

import numpy as np
from scipy.linalg import schur, solve_sylvester, svdvals
from scipy.optimize import linear_sum_assignment

from research import d3q27 as d3


@dataclass(frozen=True)
class ClusterPoint:
    wavevector: np.ndarray
    eigenvalues: np.ndarray
    basis: np.ndarray
    spectral_projector: np.ndarray
    shear_basis: np.ndarray | None
    shear_values: np.ndarray | None
    acoustic_values: np.ndarray | None
    measurements: dict[str, Any]
    failed_gates: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.failed_gates

    def record(self) -> dict[str, Any]:
        def values(array: np.ndarray | None) -> list[list[float]] | None:
            return None if array is None else [[float(z.real), float(z.imag)] for z in array]

        return {
            "wavevector": self.wavevector.tolist(),
            "radius": float(np.linalg.norm(self.wavevector)),
            "eigenvalues": values(self.eigenvalues),
            "shear_values": values(self.shear_values),
            "acoustic_values": values(self.acoustic_values),
            "measurements": self.measurements,
            "failed_gates": list(self.failed_gates),
            "passed": self.passed,
        }


def orthogonal_projector(basis: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(basis, mode="reduced")
    return q @ q.conj().T


def subspace_difference(first: np.ndarray, second: np.ndarray) -> float:
    """Operator norm of orthogonal-projector difference, independent of labels."""
    return float(np.linalg.norm(orthogonal_projector(first) - orthogonal_projector(second), ord=2))


def _ordered_schur(
    matrix: np.ndarray, selected: np.ndarray, excluded: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    gap = float(np.min(np.abs(selected[:, None] - excluded[None, :])))
    if gap <= 1e-10:
        raise np.linalg.LinAlgError(
            "selected/excluded collision is unresolved; do not split the cluster"
        )

    def selector(value: complex) -> bool:
        return bool(np.min(np.abs(value - selected)) < np.min(np.abs(value - excluded)))

    triangular, unitary, dimension = schur(matrix, output="complex", sort=selector)
    if dimension != len(selected):
        raise np.linalg.LinAlgError("ordered Schur changed the cluster dimension")
    return triangular, unitary


def cluster_point(
    wavevector: np.ndarray,
    omega: float,
    previous: ClusterPoint | None = None,
    reference_values: np.ndarray | None = None,
) -> ClusterPoint:
    k = np.asarray(wavevector, dtype=float)
    matrix = d3.fourier_symbol(k, omega)
    values = np.linalg.eigvals(matrix)
    reference = (
        (previous.eigenvalues if previous is not None else np.ones(4))
        if reference_values is None
        else reference_values
    )
    if np.shape(reference) != (4,):
        raise ValueError("exactly four reference eigenvalues are required")
    _, selected_indices = linear_sum_assignment(
        np.abs(np.asarray(reference)[:, None] - values[None, :])
    )
    selected, excluded = values[selected_indices], np.delete(values, selected_indices)
    triangular, unitary = _ordered_schur(matrix, selected, excluded)
    a, b, coupling = triangular[:4, :4], triangular[4:, 4:], triangular[:4, 4:]
    basis = unitary[:, :4]
    operator = np.kron(np.eye(23), a) - np.kron(b.T, np.eye(4))
    sep = float(svdvals(operator)[-1])
    x = solve_sylvester(a, -b, coupling)
    p_schur = np.zeros((27, 27), dtype=complex)
    p_schur[:4, :4], p_schur[:4, 4:] = np.eye(4), x
    projector = unitary @ p_schur @ unitary.conj().T
    equilibrium_basis, _ = np.linalg.qr(d3.equilibrium_tangent_matrix(), mode="reduced")
    alignment = float(svdvals(equilibrium_basis.conj().T @ basis)[-1])
    previous_angle = (
        0.0
        if previous is None
        else float(np.arcsin(np.clip(subspace_difference(previous.basis, basis), 0.0, 1.0)))
    )
    matrix_norm = float(np.linalg.norm(matrix))
    measurements = {
        "equilibrium_alignment": alignment,
        "previous_principal_angle": previous_angle,
        "external_eigenvalue_gap": float(np.min(np.abs(selected[:, None] - excluded[None, :]))),
        "schur_sylvester_sep": sep,
        "spectral_projector_norm": float(np.linalg.norm(projector, ord=2)),
        "invariance_residual": float(np.linalg.norm(matrix @ basis - basis @ a) / matrix_norm),
        "idempotency_residual": float(np.linalg.norm(projector @ projector - projector)),
        "commutator_residual": float(
            np.linalg.norm(matrix @ projector - projector @ matrix) / matrix_norm
        ),
    }
    gates = {
        "equilibrium_alignment": alignment >= 0.75,
        "adjacent_principal_angle": previous_angle <= 0.20,
        "external_eigenvalue_gap": measurements["external_eigenvalue_gap"] >= 0.05,
        "schur_sylvester_sep": sep >= 0.02,
        "spectral_projector_norm": measurements["spectral_projector_norm"] <= 100,
        "invariance_residual": measurements["invariance_residual"] <= 1e-12,
        "idempotency_residual": measurements["idempotency_residual"] <= 1e-12,
        "commutator_residual": measurements["commutator_residual"] <= 1e-12,
    }
    shear_basis = shear_values = acoustic_values = None
    if np.linalg.norm(k) > 1e-14:
        hydro_values = np.diag(a)
        shear_indices = np.argsort(np.abs(hydro_values.imag), kind="stable")[:2]
        shear_values, acoustic_values = (
            hydro_values[shear_indices],
            np.delete(hydro_values, shear_indices),
        )
        internal_gap = float(np.min(np.abs(shear_values[:, None] - acoustic_values[None, :])))
        gates["shear_acoustic_separation"] = internal_gap > 1e-8
        measurements["shear_acoustic_gap"] = internal_gap
        if internal_gap > 1e-8:
            _, internal_basis = _ordered_schur(a, shear_values, acoustic_values)
            shear_basis = basis @ internal_basis[:, :2]
            moments = d3.conserved_moment_matrix() @ shear_basis
            momentum_basis, triangular_momentum = np.linalg.qr(moments[1:], mode="reduced")
            n = k / np.linalg.norm(k)
            transverse = np.eye(3) - np.outer(n, n)
            momentum_norm = float(np.linalg.norm(moments[1:]))
            transverse_alignment = float(svdvals(transverse @ momentum_basis)[-1])
            density_leakage = float(np.linalg.norm(moments[0]) / max(momentum_norm, 1e-30))
            longitudinal_leakage = float(
                np.linalg.norm(n @ moments[1:]) / max(momentum_norm, 1e-30)
            )
            measurements.update(
                {
                    "transverse_momentum_alignment": transverse_alignment,
                    "shear_density_leakage": density_leakage,
                    "shear_longitudinal_leakage": longitudinal_leakage,
                    "shear_invariance_residual": float(
                        np.linalg.norm(
                            (np.eye(27) - orthogonal_projector(shear_basis)) @ matrix @ shear_basis
                        )
                        / matrix_norm
                    ),
                }
            )
            gates.update(
                {
                    "shear_momentum_rank": bool(
                        np.min(np.abs(np.diag(triangular_momentum))) > 1e-10
                    ),
                    "transverse_alignment": transverse_alignment >= 0.75,
                    "shear_density_leakage": density_leakage <= 0.25,
                    "shear_longitudinal_leakage": longitudinal_leakage <= 0.25,
                }
            )
    return ClusterPoint(
        k,
        np.diag(a).copy(),
        basis,
        projector,
        shear_basis,
        shear_values,
        acoustic_values,
        measurements,
        tuple(name for name, passed in gates.items() if not passed),
    )


def track_ray(
    direction: np.ndarray, omega: float, radii: np.ndarray
) -> tuple[list[ClusterPoint], dict | None]:
    direction = np.array(direction, dtype=float, copy=True)
    if (
        direction.shape != (3,)
        or not np.all(np.isfinite(direction))
        or np.linalg.norm(direction) == 0
    ):
        raise ValueError("direction must be a finite nonzero three-vector")
    direction /= np.linalg.norm(direction)
    radii = np.asarray(radii, dtype=float)
    if (
        radii.ndim != 1
        or len(radii) == 0
        or radii[0] != 0
        or not np.all(np.isfinite(radii))
        or np.any(np.diff(radii) <= 0)
    ):
        raise ValueError("radii must increase strictly from zero")
    accepted = []
    for radius in radii:
        try:
            point = cluster_point(radius * direction, omega, accepted[-1] if accepted else None)
        except np.linalg.LinAlgError as exc:
            return accepted, {
                "radius": float(radius),
                "passed": False,
                "failed_gates": ["unresolved_schur_cluster"],
                "diagnostic": str(exc),
            }
        if not point.passed:
            return accepted, point.record()
        accepted.append(point)
    return accepted, None


def parity_audit(size: int, omega: float = 1.2, *, brute_force: bool = False) -> dict[str, Any]:
    if isinstance(size, bool) or not isinstance(size, int) or size < 2:
        raise ValueError("grid size must be an integer at least two")
    multiplicities = (
        Counter(
            tuple(sorted(min(i, size - i) for i in index))
            for index in product(range(size), repeat=3)
        )
        if not brute_force
        else {index: 1 for index in product(range(size), repeat=3)}
    )
    unit_records, unit_count, ambiguous = [], 0, 0
    nonunit_max = 0.0
    for index, multiplicity in sorted(multiplicities.items()):
        values = np.linalg.eigvals(d3.fourier_symbol(2 * np.pi * np.asarray(index) / size, omega))
        distance = np.abs(np.abs(values) - 1)
        mask = distance < 1e-10
        count = int(np.count_nonzero(mask))
        unit_count += multiplicity * count
        ambiguous += multiplicity * int(np.count_nonzero((distance >= 1e-11) & (distance <= 1e-9)))
        if np.any(~mask):
            nonunit_max = max(nonunit_max, float(np.max(np.abs(values[~mask]))))
        if count:
            unit_records.append(
                {
                    "index": list(index),
                    "orbit_multiplicity": multiplicity,
                    "unit_count_per_block": count,
                    "values": [[float(v.real), float(v.imag)] for v in values[mask]],
                }
            )
    expected = 4 if size % 2 else 7
    return {
        "size": size,
        "omega": omega,
        "brute_force": brute_force,
        "orbit_count": len(multiplicities),
        "represented_wave_count": sum(multiplicities.values()),
        "strict_unit_count": unit_count,
        "expected_strict_unit_count": expected,
        "zero_wave_unit_count": sum(
            r["unit_count_per_block"] for r in unit_records if r["index"] == [0, 0, 0]
        ),
        "classification_boundary_count": ambiguous,
        "largest_nonunit_modulus": nonunit_max,
        "unit_records": unit_records,
        "passed": unit_count == expected
        and ambiguous == 0
        and sum(multiplicities.values()) == size**3,
    }
