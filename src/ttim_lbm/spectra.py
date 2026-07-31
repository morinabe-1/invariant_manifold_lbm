"""Physical classification of low-wave-number D2Q9 Fourier modes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import combinations, permutations

import numpy as np
import numpy.typing as npt
from scipy.linalg import schur, solve_sylvester

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


@dataclass(frozen=True)
class TrackedHydrodynamicCluster:
    """One point on a continued three-dimensional hydrodynamic eigenspace."""

    wave_vector: tuple[float, float]
    eigenvalues: ComplexArray
    right_basis: ComplexArray
    selected_indices: tuple[int, int, int]
    equilibrium_subspace_alignment: float
    maximum_principal_angle_from_previous: float
    external_spectral_separation: float
    schur_separation: float
    schur_invariance_residual: float
    internal_spectral_separation: float
    eigenvector_condition_number: float
    spectral_projector_norm: float
    spectral_projector_idempotency_residual: float
    spectral_projector_commutator_residual: float
    classification: str
    label_method: str
    branch_eigenvalues: dict[str, complex]


def _orthonormal_basis(vectors: npt.ArrayLike) -> ComplexArray:
    matrix = np.asarray(vectors, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[1] == 0:
        raise ValueError("vectors must be a nonempty matrix")
    basis, triangular = np.linalg.qr(matrix, mode="reduced")
    diagonal = np.abs(np.diag(triangular))
    scale = max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
    if diagonal.size != matrix.shape[1] or float(np.min(diagonal)) <= 1.0e-12 * scale:
        raise np.linalg.LinAlgError("candidate eigenvectors do not span the requested cluster")
    return np.asarray(basis, dtype=np.complex128)


def maximum_principal_angle(left: npt.ArrayLike, right: npt.ArrayLike) -> float:
    """Return the largest principal angle between two equal-dimensional subspaces."""

    left_basis = _orthonormal_basis(left)
    right_basis = _orthonormal_basis(right)
    if left_basis.shape != right_basis.shape:
        raise ValueError("subspaces must have the same ambient and reduced dimensions")
    singular_values = np.linalg.svd(
        left_basis.conj().T @ right_basis,
        compute_uv=False,
    )
    smallest_cosine = float(np.clip(np.min(singular_values), 0.0, 1.0))
    return float(np.arccos(smallest_cosine))


def _equilibrium_subspace_basis() -> ComplexArray:
    return _orthonormal_basis(equilibrium_tangent_matrix())


def _subspace_alignment(
    candidate_basis: ComplexArray,
    equilibrium_basis: ComplexArray | None = None,
) -> float:
    if equilibrium_basis is None:
        equilibrium_basis = _equilibrium_subspace_basis()
    singular_values = np.linalg.svd(
        equilibrium_basis.conj().T @ candidate_basis,
        compute_uv=False,
    )
    return float(np.clip(np.min(singular_values), 0.0, 1.0))


def _normalized_eigendecomposition(
    matrix: ComplexArray,
) -> tuple[ComplexArray, ComplexArray, ComplexArray, float]:
    eigenvalues, right = np.linalg.eig(matrix)
    norms = np.linalg.norm(right, axis=0)
    if np.any(norms <= np.finfo(float).eps):
        raise np.linalg.LinAlgError("eigendecomposition returned a zero eigenvector")
    right = right / norms
    condition_number = float(np.linalg.cond(right))
    try:
        inverse = np.linalg.inv(right)
    except np.linalg.LinAlgError:
        inverse = np.linalg.pinv(right)
        condition_number = float("inf")
    left = inverse.conj().T
    return (
        np.asarray(eigenvalues, dtype=np.complex128),
        np.asarray(right, dtype=np.complex128),
        np.asarray(left, dtype=np.complex128),
        condition_number,
    )


def _select_three_dimensional_cluster(
    right: ComplexArray,
    reference_basis: ComplexArray | None,
) -> tuple[tuple[int, int, int], ComplexArray, float, float]:
    best: tuple[tuple[float, float], tuple[int, int, int], ComplexArray, float, float] | None = None
    equilibrium_basis = _equilibrium_subspace_basis()
    for raw_indices in combinations(range(right.shape[1]), 3):
        indices = tuple(int(index) for index in raw_indices)
        try:
            basis = _orthonormal_basis(right[:, indices])
        except np.linalg.LinAlgError:
            continue
        alignment = _subspace_alignment(basis, equilibrium_basis)
        if reference_basis is None:
            angle = 0.0
        else:
            singular_values = np.linalg.svd(
                reference_basis.conj().T @ basis,
                compute_uv=False,
            )
            angle = float(
                np.arccos(float(np.clip(np.min(singular_values), 0.0, 1.0)))
            )
        objective = (-alignment, 0.0) if reference_basis is None else (angle, -alignment)
        candidate = (objective, indices, basis, alignment, angle)
        if best is None or candidate[0] < best[0]:
            best = candidate
    if best is None:
        raise np.linalg.LinAlgError("no full-rank three-dimensional eigenspace was found")
    _, indices, basis, alignment, angle = best
    return indices, basis, alignment, angle


def _minimum_pairwise_separation(values: ComplexArray) -> float:
    if values.size < 2:
        return float("inf")
    return float(
        min(
            abs(values[left] - values[right])
            for left in range(values.size)
            for right in range(left + 1, values.size)
        )
    )


def _external_separation(
    eigenvalues: ComplexArray,
    selected_indices: tuple[int, int, int],
) -> float:
    selected = set(selected_indices)
    return float(
        min(
            abs(eigenvalues[inside] - eigenvalues[outside])
            for inside in selected
            for outside in range(eigenvalues.size)
            if outside not in selected
        )
    )


def _ordered_schur_cluster(
    matrix: ComplexArray,
    eigenvalues: ComplexArray,
    selected_indices: tuple[int, int, int],
) -> tuple[ComplexArray, float, float, float, float, float]:
    selected = eigenvalues[list(selected_indices)]
    excluded = np.delete(eigenvalues, list(selected_indices))

    def selector(value: complex) -> bool:
        return bool(
            np.min(np.abs(value - selected))
            < np.min(np.abs(value - excluded))
        )

    triangular, unitary, selected_dimension = schur(
        matrix,
        output="complex",
        sort=selector,
    )
    if selected_dimension != 3:
        raise np.linalg.LinAlgError(
            "ordered Schur decomposition did not preserve a three-dimensional cluster"
        )
    basis = np.asarray(unitary[:, :3], dtype=np.complex128)
    selected_block = triangular[:3, :3]
    coupling_block = triangular[:3, 3:]
    excluded_block = triangular[3:, 3:]
    sylvester_operator = (
        np.kron(np.eye(excluded_block.shape[0]), selected_block)
        - np.kron(excluded_block.T, np.eye(selected_block.shape[0]))
    )
    separation = float(
        np.min(np.linalg.svd(sylvester_operator, compute_uv=False))
    )
    invariance_residual = float(
        np.linalg.norm(matrix @ basis - basis @ selected_block)
        / max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
    )
    projector_coupling = solve_sylvester(
        selected_block,
        -excluded_block,
        coupling_block,
    )
    projector_in_schur_basis = np.zeros_like(triangular)
    projector_in_schur_basis[:3, :3] = np.eye(3)
    projector_in_schur_basis[:3, 3:] = projector_coupling
    spectral_projector = unitary @ projector_in_schur_basis @ unitary.conj().T
    projector_norm = float(np.linalg.norm(spectral_projector, ord=2))
    idempotency_residual = float(
        np.linalg.norm(spectral_projector @ spectral_projector - spectral_projector)
    )
    commutator_residual = float(
        np.linalg.norm(matrix @ spectral_projector - spectral_projector @ matrix)
        / max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
    )
    return (
        basis,
        separation,
        invariance_residual,
        projector_norm,
        idempotency_residual,
        commutator_residual,
    )


def _moment_labels(
    selected_indices: tuple[int, int, int],
    eigenvalues: ComplexArray,
    right: ComplexArray,
    wave_vector: tuple[float, float],
) -> dict[str, int]:
    magnitude = float(np.hypot(*wave_vector))
    tangent = np.asarray(wave_vector, dtype=np.float64) / magnitude
    transverse = np.array([-tangent[1], tangent[0]])
    moments = conserved_moment_matrix()
    transverse_scores: dict[int, float] = {}
    for index in selected_indices:
        conserved = moments @ right[:, index]
        denominator = max(float(np.linalg.norm(conserved)), np.finfo(float).eps)
        transverse_scores[index] = float(abs(transverse @ conserved[1:]) / denominator)
    shear = max(selected_indices, key=transverse_scores.__getitem__)
    acoustic = [index for index in selected_indices if index != shear]
    acoustic.sort(key=lambda index: eigenvalues[index].imag, reverse=True)
    return {
        "shear": shear,
        "acoustic_positive": acoustic[0],
        "acoustic_negative": acoustic[1],
    }


def _continued_labels(
    previous: dict[str, tuple[ComplexArray, ComplexArray]],
    selected_indices: tuple[int, int, int],
    right: ComplexArray,
    left: ComplexArray,
) -> dict[str, int]:
    labels = tuple(previous)
    best_score = -float("inf")
    best_assignment: dict[str, int] | None = None
    for assignment in permutations(selected_indices):
        score = 0.0
        for label, current_index in zip(labels, assignment, strict=True):
            previous_right, previous_left = previous[label]
            forward = abs(np.vdot(previous_left, right[:, current_index]))
            backward = abs(np.vdot(left[:, current_index], previous_right))
            score += float(np.sqrt(forward * backward))
        if score > best_score:
            best_score = score
            best_assignment = dict(zip(labels, assignment, strict=True))
    if best_assignment is None:
        raise RuntimeError("branch assignment failed")
    return best_assignment


def track_hydrodynamic_cluster_path(
    wave_vectors: Sequence[tuple[float, float]],
    omega: float,
    *,
    initial_reference_basis: npt.ArrayLike | None = None,
    simple_eigenvalue_separation: float = 1.0e-6,
    maximum_simple_eigenvector_condition_number: float = 1.0e8,
) -> list[TrackedHydrodynamicCluster]:
    """Continue the hydrodynamic cluster along a continuous wave-vector path.

    Individual shear/acoustic labels are reported only where the three selected
    eigenvalues are internally and externally separated and the eigensystem is
    below the requested condition bound.  At collisions the invariant cluster,
    rather than an arbitrary eigenvector basis, is the tracked object.
    """

    if len(wave_vectors) < 2:
        raise ValueError("at least two wave vectors are required")
    if not np.isfinite(simple_eigenvalue_separation) or simple_eigenvalue_separation <= 0.0:
        raise ValueError("simple_eigenvalue_separation must be positive and finite")
    if (
        not np.isfinite(maximum_simple_eigenvector_condition_number)
        or maximum_simple_eigenvector_condition_number < 1.0
    ):
        raise ValueError(
            "maximum_simple_eigenvector_condition_number must be finite and at least one"
        )
    reference = (
        None
        if initial_reference_basis is None
        else _orthonormal_basis(initial_reference_basis)
    )
    points: list[TrackedHydrodynamicCluster] = []
    previous_simple: dict[str, tuple[ComplexArray, ComplexArray]] | None = None
    for raw_wave_vector in wave_vectors:
        wave_vector = (float(raw_wave_vector[0]), float(raw_wave_vector[1]))
        if not np.all(np.isfinite(wave_vector)) or np.hypot(*wave_vector) <= 0.0:
            raise ValueError("path wave vectors must be finite and nonzero")
        symbol = fourier_symbol(*wave_vector, omega)
        eigenvalues, right, left, eigenvector_condition = (
            _normalized_eigendecomposition(symbol)
        )
        indices, _, _, _ = _select_three_dimensional_cluster(
            right,
            reference,
        )
        (
            basis,
            schur_separation,
            schur_invariance_residual,
            projector_norm,
            projector_idempotency_residual,
            projector_commutator_residual,
        ) = _ordered_schur_cluster(
            symbol,
            eigenvalues,
            indices,
        )
        alignment = _subspace_alignment(basis)
        angle = (
            0.0
            if reference is None
            else maximum_principal_angle(reference, basis)
        )
        selected_values = eigenvalues[list(indices)]
        internal_separation = _minimum_pairwise_separation(selected_values)
        external_separation = _external_separation(eigenvalues, indices)
        simple_and_resolved = (
            internal_separation > simple_eigenvalue_separation
            and external_separation > simple_eigenvalue_separation
            and eigenvector_condition <= maximum_simple_eigenvector_condition_number
        )
        if simple_and_resolved:
            if previous_simple is None:
                label_indices = _moment_labels(indices, eigenvalues, right, wave_vector)
                label_method = "moment_initialization"
            else:
                label_indices = _continued_labels(
                    previous_simple,
                    indices,
                    right,
                    left,
                )
                label_method = "symmetric_biorthogonal_overlap"
            branch_eigenvalues = {
                label: complex(eigenvalues[index])
                for label, index in label_indices.items()
            }
            previous_simple = {
                label: (right[:, index].copy(), left[:, index].copy())
                for label, index in label_indices.items()
            }
            classification = "simple_branches"
        else:
            branch_eigenvalues = {}
            label_method = "invariant_cluster"
            classification = "invariant_cluster"
            previous_simple = None
        points.append(
            TrackedHydrodynamicCluster(
                wave_vector=wave_vector,
                eigenvalues=selected_values,
                right_basis=basis,
                selected_indices=indices,
                equilibrium_subspace_alignment=alignment,
                maximum_principal_angle_from_previous=angle,
                external_spectral_separation=external_separation,
                schur_separation=schur_separation,
                schur_invariance_residual=schur_invariance_residual,
                internal_spectral_separation=internal_separation,
                eigenvector_condition_number=eigenvector_condition,
                spectral_projector_norm=projector_norm,
                spectral_projector_idempotency_residual=(
                    projector_idempotency_residual
                ),
                spectral_projector_commutator_residual=(
                    projector_commutator_residual
                ),
                classification=classification,
                label_method=label_method,
                branch_eigenvalues=branch_eigenvalues,
            )
        )
        reference = basis
    return points


def path_reversal_subspace_error(
    forward: Sequence[TrackedHydrodynamicCluster],
    backward: Sequence[TrackedHydrodynamicCluster],
) -> float:
    """Compare forward/backward cluster subspaces, ignoring internal permutations."""

    if len(forward) != len(backward) or not forward:
        raise ValueError("forward and backward paths must have the same nonzero length")
    return float(
        max(
            maximum_principal_angle(left.right_basis, right.right_basis)
            for left, right in zip(forward, reversed(backward), strict=True)
        )
    )


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
