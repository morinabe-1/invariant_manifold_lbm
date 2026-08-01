"""Fourier-sector diagnostics for quadratic D2Q9 nonresonance.

Translation invariance reduces every scalar quadratic mode interaction to an
output block of dimension at most nine.  This module never materializes a
full-grid homological operator.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement, product
from numbers import Integral
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.linalg import null_space, schur

from .d2q9 import (
    D2Q9_VELOCITIES,
    conserved_moment_matrix,
    equilibrium_tangent_matrix,
    exact_uniform_hessian,
    fourier_symbol,
)

ComplexArray = npt.NDArray[np.complex128]
WaveIndex = tuple[int, int]

NUMERICAL_RANK_MULTIPLIER = 100.0
NULL_FORCING_TOLERANCE = 1.0e-10
PRACTICAL_CONDITION_CEILING = 1.0e8


@dataclass(frozen=True)
class SimpleHydrodynamicMode:
    """One simple hydrodynamic eigenmode with biorthogonal normalization."""

    label: str
    eigenvalue: complex
    right_eigenvector: ComplexArray
    left_eigenvector: ComplexArray
    eigenvalue_condition_number: float
    reduced_resolvent_norm: float
    hydrodynamic_score: float
    transverse_fraction: float
    right_invariance_residual: float
    left_invariance_residual: float
    duality_residual: float


@dataclass(frozen=True)
class ScalarHomologicalDiagnostic:
    """SVD and compatibility classification for a scalar-input output block."""

    multiplier_product: complex
    minimum_eigenvalue_distance: float
    smallest_singular_value: float
    largest_singular_value: float
    relative_smallest_singular_value: float
    numerical_rank_threshold: float
    condition_number: float | None
    null_forcing_ratio: float | None
    status: str


def _require_odd_size(size: int) -> int:
    if (
        isinstance(size, bool)
        or not isinstance(size, Integral)
        or size < 3
        or size % 2 == 0
    ):
        raise ValueError("construction grid size must be an odd integer of at least three")
    return int(size)


def canonical_wave_index(index: WaveIndex, size: int) -> WaveIndex:
    """Return the unique centered representative of an odd-grid wave index."""

    size = _require_odd_size(size)
    if (
        len(index) != 2
        or any(isinstance(value, bool) for value in index)
        or not all(isinstance(value, Integral) for value in index)
    ):
        raise ValueError("wave index must contain two integers")
    half = size // 2
    return tuple(int((int(value) + half) % size - half) for value in index)


def add_wave_indices(left: WaveIndex, right: WaveIndex, size: int) -> WaveIndex:
    """Add two Fourier indices modulo an odd periodic grid."""

    left = canonical_wave_index(left, size)
    right = canonical_wave_index(right, size)
    return canonical_wave_index((left[0] + right[0], left[1] + right[1]), size)


def wave_vector_from_index(index: WaveIndex, size: int) -> tuple[float, float]:
    """Convert a canonical Fourier index to a wave vector in radians."""

    canonical = canonical_wave_index(index, size)
    scale = 2.0 * np.pi / size
    return float(scale * canonical[0]), float(scale * canonical[1])


def radial_wave_indices(size: int, cutoff: float) -> list[WaveIndex]:
    """Enumerate nonzero odd-grid indices inside a radial cutoff."""

    size = _require_odd_size(size)
    cutoff = float(cutoff)
    if not np.isfinite(cutoff) or cutoff <= 0.0 or cutoff >= np.pi:
        raise ValueError("cutoff must be finite and lie in (0, pi)")
    half = size // 2
    scale = 2.0 * np.pi / size
    tolerance = 64.0 * np.finfo(float).eps * max(cutoff, 1.0)
    indices = [
        (ix, iy)
        for ix in range(-half, half + 1)
        for iy in range(-half, half + 1)
        if (ix != 0 or iy != 0)
        and scale * float(np.hypot(ix, iy)) <= cutoff + tolerance
    ]
    return sorted(indices, key=lambda item: (item[0] ** 2 + item[1] ** 2, item))


def realify_complex_matrix(matrix: npt.ArrayLike) -> npt.NDArray[np.float64]:
    """Return the standard real block representation of a complex matrix."""

    value = np.asarray(matrix, dtype=np.complex128)
    if value.ndim != 2:
        raise ValueError("matrix must be two-dimensional")
    return np.block([[value.real, -value.imag], [value.imag, value.real]])


def _matched_left_eigenvector(
    matrix: ComplexArray,
    eigenvalue: complex,
    right: ComplexArray,
) -> ComplexArray:
    left_values, left_vectors = np.linalg.eig(matrix.conj().T)
    index = int(np.argmin(np.abs(left_values - np.conjugate(eigenvalue))))
    left = np.asarray(left_vectors[:, index], dtype=np.complex128)
    overlap = np.vdot(left, right)
    scale = max(float(np.linalg.norm(left) * np.linalg.norm(right)), np.finfo(float).eps)
    if abs(overlap) <= 1.0e-12 * scale:
        raise np.linalg.LinAlgError("left and right eigenvectors cannot be normalized")
    return left / np.conjugate(overlap)


def _hydrodynamic_decomposition(
    matrix: ComplexArray,
    wave_vector: tuple[float, float],
) -> tuple[ComplexArray, ComplexArray, tuple[int, int, int], dict[str, int], npt.NDArray[np.float64]]:
    eigenvalues, right = np.linalg.eig(matrix)
    right = np.asarray(right, dtype=np.complex128)
    right /= np.linalg.norm(right, axis=0)
    tangent_projector = equilibrium_tangent_matrix() @ conserved_moment_matrix()
    scores = np.linalg.norm(tangent_projector @ right, axis=0)
    selected = tuple(int(index) for index in np.argsort(scores)[-3:])

    magnitude = float(np.hypot(*wave_vector))
    if magnitude <= 0.0:
        raise ValueError("hydrodynamic branch labels require a nonzero wave vector")
    tangent = np.asarray(wave_vector, dtype=np.float64) / magnitude
    transverse = np.array([-tangent[1], tangent[0]])
    moments = conserved_moment_matrix()
    transverse_scores: dict[int, float] = {}
    for index in selected:
        conserved = moments @ right[:, index]
        transverse_scores[index] = float(
            abs(transverse @ conserved[1:])
            / max(float(np.linalg.norm(conserved)), np.finfo(float).eps)
        )
    shear = max(selected, key=transverse_scores.__getitem__)
    acoustic = [index for index in selected if index != shear]
    acoustic.sort(key=lambda index: eigenvalues[index].imag, reverse=True)
    labels = {
        "shear": shear,
        "acoustic_positive": acoustic[0],
        "acoustic_negative": acoustic[1],
    }
    return (
        np.asarray(eigenvalues, dtype=np.complex128),
        right,
        selected,
        labels,
        np.asarray(scores, dtype=np.float64),
    )


def _ordered_schur_diagnostics(
    matrix: ComplexArray,
    eigenvalues: ComplexArray,
    selected: tuple[int, int, int],
) -> tuple[float, float]:
    selected_values = eigenvalues[list(selected)]
    excluded_values = np.delete(eigenvalues, list(selected))

    def selector(value: complex) -> bool:
        return bool(
            np.min(np.abs(value - selected_values))
            < np.min(np.abs(value - excluded_values))
        )

    triangular, unitary, selected_dimension = schur(
        matrix,
        output="complex",
        sort=selector,
    )
    if selected_dimension != 3:
        raise np.linalg.LinAlgError(
            "ordered Schur decomposition did not preserve the hydrodynamic cluster"
        )
    selected_block = triangular[:3, :3]
    excluded_block = triangular[3:, 3:]
    sylvester_operator = (
        np.kron(np.eye(excluded_block.shape[0]), selected_block)
        - np.kron(excluded_block.T, np.eye(selected_block.shape[0]))
    )
    separation = float(np.min(np.linalg.svd(sylvester_operator, compute_uv=False)))
    basis = unitary[:, :3]
    invariance_residual = float(
        np.linalg.norm(matrix @ basis - basis @ selected_block)
        / max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
    )
    return separation, invariance_residual


def simple_hydrodynamic_modes(
    kx: float,
    ky: float,
    omega: float,
) -> dict[str, SimpleHydrodynamicMode]:
    """Classify and normalize the three simple hydrodynamic modes at nonzero k."""

    wave_vector = (float(kx), float(ky))
    if not np.all(np.isfinite(wave_vector)) or np.hypot(*wave_vector) <= 0.0:
        raise ValueError("wave vector must be finite and nonzero")
    matrix = fourier_symbol(*wave_vector, omega)
    eigenvalues, right, selected, labels, scores = _hydrodynamic_decomposition(
        matrix,
        wave_vector,
    )
    separation = min(
        abs(eigenvalues[left] - eigenvalues[other])
        for left in selected
        for other in range(eigenvalues.size)
        if other != left
    )
    if separation <= 1.0e-10:
        raise np.linalg.LinAlgError("hydrodynamic modes are not simple at this wave vector")

    moments = conserved_moment_matrix()
    tangent = np.asarray(wave_vector, dtype=np.float64) / float(np.hypot(*wave_vector))
    transverse = np.array([-tangent[1], tangent[0]])
    modes: dict[str, SimpleHydrodynamicMode] = {}
    for label, index in labels.items():
        eigenvalue = complex(eigenvalues[index])
        right_vector = np.asarray(right[:, index], dtype=np.complex128)
        left_vector = _matched_left_eigenvector(matrix, eigenvalue, right_vector)
        conserved = moments @ right_vector
        spectral_projector = np.outer(right_vector, left_vector.conj())
        reduced_resolvent = float(
            np.linalg.norm(
                np.linalg.inv(
                    matrix - eigenvalue * np.eye(9) + spectral_projector
                )
                - spectral_projector,
                ord=2,
            )
        )
        matrix_scale = max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
        modes[label] = SimpleHydrodynamicMode(
            label=label,
            eigenvalue=eigenvalue,
            right_eigenvector=right_vector,
            left_eigenvector=left_vector,
            eigenvalue_condition_number=float(
                np.linalg.norm(left_vector) * np.linalg.norm(right_vector)
            ),
            reduced_resolvent_norm=reduced_resolvent,
            hydrodynamic_score=float(scores[index]),
            transverse_fraction=float(
                abs(transverse @ conserved[1:])
                / max(float(np.linalg.norm(conserved)), np.finfo(float).eps)
            ),
            right_invariance_residual=float(
                np.linalg.norm(matrix @ right_vector - eigenvalue * right_vector)
                / matrix_scale
            ),
            left_invariance_residual=float(
                np.linalg.norm(
                    left_vector.conj().T @ matrix
                    - eigenvalue * left_vector.conj().T
                )
                / matrix_scale
            ),
            duality_residual=float(abs(np.vdot(left_vector, right_vector) - 1.0)),
        )
    return modes


def quadratic_fourier_forcing(
    left_mode: npt.ArrayLike,
    right_mode: npt.ArrayLike,
    output_wave_vector: tuple[float, float],
    omega: float,
) -> ComplexArray:
    """Apply the analytic D2Q9 map Hessian to two Fourier population modes."""

    left = np.asarray(left_mode, dtype=np.complex128)
    right = np.asarray(right_mode, dtype=np.complex128)
    if left.shape != (9,) or right.shape != (9,):
        raise ValueError("Fourier population modes must each have shape (9,)")
    output = np.asarray(output_wave_vector, dtype=np.float64)
    if output.shape != (2,) or not np.all(np.isfinite(output)):
        raise ValueError("output wave vector must contain two finite values")
    moments = conserved_moment_matrix()
    local_forcing = float(omega) * np.einsum(
        "qab,a,b->q",
        exact_uniform_hessian(1, 1),
        moments @ left,
        moments @ right,
    )
    phase = np.exp(-1j * (D2Q9_VELOCITIES @ output))
    return np.asarray(phase * local_forcing, dtype=np.complex128)


def audit_scalar_homological_sector(
    output_matrix: npt.ArrayLike,
    multiplier_product: complex,
    forcing: npt.ArrayLike,
) -> ScalarHomologicalDiagnostic:
    """Classify a scalar-input homological block by SVD and null compatibility."""

    matrix = np.asarray(output_matrix, dtype=np.complex128)
    forcing_vector = np.asarray(forcing, dtype=np.complex128)
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("output matrix must be square")
    if forcing_vector.shape != (matrix.shape[0],):
        raise ValueError("forcing must match the output dimension")
    operator = matrix - complex(multiplier_product) * np.eye(matrix.shape[0])
    left_singular, singular_values, _ = np.linalg.svd(operator)
    largest = float(singular_values[0])
    smallest = float(singular_values[-1])
    rank_threshold = float(
        NUMERICAL_RANK_MULTIPLIER
        * np.finfo(float).eps
        * max(operator.shape)
        * largest
    )
    eigenvalue_gap = float(
        np.min(np.abs(np.linalg.eigvals(matrix) - multiplier_product))
    )
    if smallest <= rank_threshold:
        null_columns = left_singular[:, singular_values <= rank_threshold]
        forcing_norm = max(float(np.linalg.norm(forcing_vector)), np.finfo(float).eps)
        null_forcing_ratio = float(
            np.linalg.norm(null_columns.conj().T @ forcing_vector) / forcing_norm
        )
        condition_number = None
        status = (
            "compatible_nonunique"
            if null_forcing_ratio <= NULL_FORCING_TOLERANCE
            else "incompatible"
        )
    else:
        null_forcing_ratio = None
        condition_number = float(largest / smallest)
        status = (
            "nonsingular_practical"
            if condition_number <= PRACTICAL_CONDITION_CEILING
            else "nonsingular_ill_conditioned"
        )
    return ScalarHomologicalDiagnostic(
        multiplier_product=complex(multiplier_product),
        minimum_eigenvalue_distance=eigenvalue_gap,
        smallest_singular_value=smallest,
        largest_singular_value=largest,
        relative_smallest_singular_value=smallest / max(largest, np.finfo(float).eps),
        numerical_rank_threshold=rank_threshold,
        condition_number=condition_number,
        null_forcing_ratio=null_forcing_ratio,
        status=status,
    )


def fixed_leaf_kinetic_restriction(
    omega: float,
) -> tuple[ComplexArray, ComplexArray, float]:
    """Return a basis and the zero-wave kinetic block on the fixed leaf."""

    basis = np.asarray(null_space(conserved_moment_matrix()), dtype=np.complex128)
    matrix = fourier_symbol(0.0, 0.0, omega)
    block = basis.conj().T @ matrix @ basis
    residual = float(
        np.linalg.norm(matrix @ basis - basis @ block)
        / max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
    )
    return basis, np.asarray(block, dtype=np.complex128), residual


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _diagnostic_record(diagnostic: ScalarHomologicalDiagnostic) -> dict[str, Any]:
    return {
        "multiplier_product": _complex_record(diagnostic.multiplier_product),
        "minimum_eigenvalue_distance": diagnostic.minimum_eigenvalue_distance,
        "smallest_singular_value": diagnostic.smallest_singular_value,
        "largest_singular_value": diagnostic.largest_singular_value,
        "relative_smallest_singular_value": diagnostic.relative_smallest_singular_value,
        "numerical_rank_threshold": diagnostic.numerical_rank_threshold,
        "condition_number": diagnostic.condition_number,
        "null_forcing_ratio": diagnostic.null_forcing_ratio,
        "status": diagnostic.status,
    }


def orthogonal_acoustic_resonance_witness(
    size: int,
    omega: float,
    radial_index: int = 1,
) -> dict[str, Any]:
    """Audit the orthogonal acoustic product at (m,0)+(0,m)=(m,m)."""

    size = _require_odd_size(size)
    if (
        isinstance(radial_index, bool)
        or not isinstance(radial_index, Integral)
        or not 1 <= radial_index <= size // 2
    ):
        raise ValueError("radial_index must lie in the positive canonical half-grid")
    radial_index = int(radial_index)
    left_index = (radial_index, 0)
    right_index = (0, radial_index)
    output_index = add_wave_indices(left_index, right_index, size)
    left_wave = wave_vector_from_index(left_index, size)
    right_wave = wave_vector_from_index(right_index, size)
    output_wave = wave_vector_from_index(output_index, size)
    left = simple_hydrodynamic_modes(*left_wave, omega)["acoustic_positive"]
    right = simple_hydrodynamic_modes(*right_wave, omega)["acoustic_negative"]
    multiplier_product = left.eigenvalue * right.eigenvalue
    forcing = quadratic_fourier_forcing(
        left.right_eigenvector,
        right.right_eigenvector,
        output_wave,
        omega,
    )
    diagnostic = audit_scalar_homological_sector(
        fourier_symbol(*output_wave, omega),
        multiplier_product,
        forcing,
    )
    output_modes = simple_hydrodynamic_modes(*output_wave, omega)
    closest_label, closest_mode = min(
        output_modes.items(),
        key=lambda item: abs(item[1].eigenvalue - multiplier_product),
    )
    return {
        "grid_size": size,
        "omega": float(omega),
        "input_wave_indices": [list(left_index), list(right_index)],
        "output_wave_index": list(output_index),
        "input_labels": [left.label, right.label],
        "closest_output_hydrodynamic_label": closest_label,
        "closest_output_eigenvalue": _complex_record(closest_mode.eigenvalue),
        "forcing_norm": float(np.linalg.norm(forcing)),
        "input_maximum_eigenvalue_condition_number": max(
            left.eigenvalue_condition_number,
            right.eigenvalue_condition_number,
        ),
        "input_maximum_reduced_resolvent_norm": max(
            left.reduced_resolvent_norm,
            right.reduced_resolvent_norm,
        ),
        "homological": _diagnostic_record(diagnostic),
    }


def radial_band_normal_dominance(
    size: int,
    omega: float,
    cutoff: float,
) -> dict[str, Any]:
    """Compare radial-master decay with every excluded fixed-leaf multiplier."""

    size = _require_odd_size(size)
    master_indices = set(radial_wave_indices(size, cutoff))
    selected_moduli: list[float] = []
    maximum_projector_norm = 0.0
    maximum_projector_residual = 0.0
    minimum_local_gap = float("inf")
    minimum_schur_separation = float("inf")
    maximum_schur_invariance_residual = 0.0
    worst_external: tuple[float, WaveIndex, complex, ComplexArray] | None = None
    half = size // 2
    for raw_index in product(range(-half, half + 1), repeat=2):
        wave_index = (int(raw_index[0]), int(raw_index[1]))
        wave_vector = wave_vector_from_index(wave_index, size)
        matrix = fourier_symbol(*wave_vector, omega)
        eigenvalues, right = np.linalg.eig(matrix)
        right = np.asarray(right, dtype=np.complex128)
        right /= np.linalg.norm(right, axis=0)
        if wave_index in master_indices:
            _, _, selected, _, _ = _hydrodynamic_decomposition(matrix, wave_vector)
            selected_set = set(selected)
            selected_moduli.extend(float(abs(eigenvalues[index])) for index in selected)
            schur_separation, schur_invariance = _ordered_schur_diagnostics(
                matrix,
                np.asarray(eigenvalues, dtype=np.complex128),
                selected,
            )
            minimum_schur_separation = min(
                minimum_schur_separation,
                schur_separation,
            )
            maximum_schur_invariance_residual = max(
                maximum_schur_invariance_residual,
                schur_invariance,
            )
            modes = simple_hydrodynamic_modes(*wave_vector, omega)
            spectral_projector = sum(
                np.outer(mode.right_eigenvector, mode.left_eigenvector.conj())
                for mode in modes.values()
            )
            projector_residual = max(
                float(
                    np.linalg.norm(
                        spectral_projector @ spectral_projector - spectral_projector
                    )
                ),
                float(
                    np.linalg.norm(
                        matrix @ spectral_projector - spectral_projector @ matrix
                    )
                    / max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
                ),
            )
            maximum_projector_norm = max(
                maximum_projector_norm,
                float(np.linalg.norm(spectral_projector, ord=2)),
            )
            maximum_projector_residual = max(
                maximum_projector_residual,
                projector_residual,
            )
            minimum_local_gap = min(
                minimum_local_gap,
                min(
                    abs(eigenvalues[inside] - eigenvalues[outside])
                    for inside in selected_set
                    for outside in range(9)
                    if outside not in selected_set
                ),
            )
        elif wave_index == (0, 0):
            selected_set = {
                int(index) for index in np.argsort(np.abs(eigenvalues - 1.0))[:3]
            }
        else:
            selected_set = set()
        for eigen_index, eigenvalue in enumerate(eigenvalues):
            if eigen_index in selected_set:
                continue
            modulus = float(abs(eigenvalue))
            if worst_external is None or modulus > worst_external[0]:
                worst_external = (modulus, wave_index, complex(eigenvalue), matrix)
    if not selected_moduli or worst_external is None:
        raise RuntimeError("normal-dominance audit did not find both spectral sets")
    external_modulus, external_index, external_eigenvalue, external_matrix = worst_external
    external_values, external_right = np.linalg.eig(external_matrix)
    matched = int(np.argmin(np.abs(external_values - external_eigenvalue)))
    right_vector = np.asarray(external_right[:, matched], dtype=np.complex128)
    right_vector /= np.linalg.norm(right_vector)
    left_vector = _matched_left_eigenvector(
        external_matrix,
        external_eigenvalue,
        right_vector,
    )
    departure = float(
        np.linalg.norm(
            external_matrix.conj().T @ external_matrix
            - external_matrix @ external_matrix.conj().T
        )
        / max(float(np.linalg.norm(external_matrix) ** 2), np.finfo(float).eps)
    )
    minimum_selected_modulus = min(selected_moduli)
    return {
        "grid_size": size,
        "omega": float(omega),
        "cutoff": float(cutoff),
        "master_wave_count": len(master_indices),
        "master_real_dimension": 3 * len(master_indices),
        "minimum_master_multiplier_modulus": minimum_selected_modulus,
        "maximum_external_multiplier_modulus": external_modulus,
        "normal_dominance_ratio": external_modulus / minimum_selected_modulus,
        "finite_grid_normal_attraction": external_modulus < minimum_selected_modulus,
        "worst_external_wave_index": list(external_index),
        "worst_external_eigenvalue": _complex_record(external_eigenvalue),
        "worst_external_eigenvalue_condition_number": float(
            np.linalg.norm(left_vector) * np.linalg.norm(right_vector)
        ),
        "worst_external_symbol_departure_from_normality": departure,
        "minimum_local_selected_excluded_eigenvalue_gap": float(minimum_local_gap),
        "minimum_ordered_schur_separation": minimum_schur_separation,
        "maximum_schur_invariance_residual": maximum_schur_invariance_residual,
        "maximum_master_spectral_projector_norm": maximum_projector_norm,
        "maximum_master_projector_residual": maximum_projector_residual,
    }


def stripe_quadratic_audit(size: int, omega: float) -> dict[str, Any]:
    """Audit the finite-grid y-independent master pair at the first shell."""

    size = _require_odd_size(size)
    if size < 5:
        raise ValueError("stripe audit requires size at least five to avoid 2k aliasing")
    positive_index = (1, 0)
    negative_index = (-1, 0)
    second_index = add_wave_indices(positive_index, positive_index, size)
    positive_wave = wave_vector_from_index(positive_index, size)
    negative_wave = wave_vector_from_index(negative_index, size)
    second_wave = wave_vector_from_index(second_index, size)
    positive_modes = simple_hydrodynamic_modes(*positive_wave, omega)
    negative_modes = simple_hydrodynamic_modes(*negative_wave, omega)
    labels = tuple(positive_modes)

    second_matrix = fourier_symbol(*second_wave, omega)
    second_records: list[tuple[tuple[str, str], ScalarHomologicalDiagnostic]] = []
    for left_label, right_label in combinations_with_replacement(labels, 2):
        left = positive_modes[left_label]
        right = positive_modes[right_label]
        forcing = quadratic_fourier_forcing(
            left.right_eigenvector,
            right.right_eigenvector,
            second_wave,
            omega,
        )
        second_records.append(
            (
                (left_label, right_label),
                audit_scalar_homological_sector(
                    second_matrix,
                    left.eigenvalue * right.eigenvalue,
                    forcing,
                ),
            )
        )

    kinetic_basis, kinetic_block, kinetic_invariance = fixed_leaf_kinetic_restriction(omega)
    zero_records: list[tuple[tuple[str, str], ScalarHomologicalDiagnostic]] = []
    maximum_conservation_residual = 0.0
    for left_label, right_label in product(labels, repeat=2):
        left = positive_modes[left_label]
        right = negative_modes[right_label]
        full_forcing = quadratic_fourier_forcing(
            left.right_eigenvector,
            right.right_eigenvector,
            (0.0, 0.0),
            omega,
        )
        forcing_norm = max(float(np.linalg.norm(full_forcing)), np.finfo(float).eps)
        maximum_conservation_residual = max(
            maximum_conservation_residual,
            float(np.linalg.norm(conserved_moment_matrix() @ full_forcing) / forcing_norm),
        )
        zero_records.append(
            (
                (left_label, right_label),
                audit_scalar_homological_sector(
                    kinetic_block,
                    left.eigenvalue * right.eigenvalue,
                    kinetic_basis.conj().T @ full_forcing,
                ),
            )
        )

    worst_second = min(second_records, key=lambda item: item[1].smallest_singular_value)
    worst_zero = min(zero_records, key=lambda item: item[1].smallest_singular_value)
    worst_operator = (
        second_matrix
        - worst_second[1].multiplier_product * np.eye(second_matrix.shape[0])
    )
    complex_singular = np.linalg.svd(worst_operator, compute_uv=False)
    real_singular = np.linalg.svd(
        realify_complex_matrix(worst_operator),
        compute_uv=False,
    )
    expected_real = np.sort(np.repeat(complex_singular, 2))
    realification_error = float(
        np.linalg.norm(np.sort(real_singular) - expected_real)
        / max(float(np.linalg.norm(expected_real)), np.finfo(float).eps)
    )
    positive_matrix = fourier_symbol(*positive_wave, omega)
    all_positive_values = list(np.linalg.eigvals(positive_matrix))
    selected_values = np.array(
        [mode.eigenvalue for mode in positive_modes.values()],
        dtype=np.complex128,
    )
    excluded_values: list[complex] = []
    for selected in selected_values:
        closest = int(np.argmin(np.abs(np.asarray(all_positive_values) - selected)))
        all_positive_values.pop(closest)
    excluded_values = [complex(value) for value in all_positive_values]
    local_gap = min(
        abs(selected - excluded)
        for selected in selected_values
        for excluded in excluded_values
    )
    conjugacy_residual = float(
        np.linalg.norm(
            fourier_symbol(*negative_wave, omega) - np.conjugate(positive_matrix)
        )
    )
    condition_fallback = PRACTICAL_CONDITION_CEILING * 10.0
    return {
        "grid_size": size,
        "omega": float(omega),
        "master_wave_indices": [list(positive_index), list(negative_index)],
        "master_real_dimension": 6,
        "nonlinear_invariant_subspace": "y-independent periodic populations",
        "second_harmonic_wave_index": list(second_index),
        "second_harmonic_interaction_count": len(second_records),
        "second_harmonic_minimum_smallest_singular_value": (
            worst_second[1].smallest_singular_value
        ),
        "second_harmonic_maximum_condition_number": max(
            record.condition_number or condition_fallback
            for _, record in second_records
        ),
        "second_harmonic_worst_input_labels": list(worst_second[0]),
        "second_harmonic_worst_diagnostic": _diagnostic_record(worst_second[1]),
        "zero_wave_interaction_count": len(zero_records),
        "zero_wave_minimum_smallest_singular_value": (
            worst_zero[1].smallest_singular_value
        ),
        "zero_wave_maximum_condition_number": max(
            record.condition_number or condition_fallback for _, record in zero_records
        ),
        "zero_wave_worst_input_labels": list(worst_zero[0]),
        "zero_wave_worst_diagnostic": _diagnostic_record(worst_zero[1]),
        "fixed_leaf_kinetic_dimension": int(kinetic_block.shape[0]),
        "fixed_leaf_kinetic_invariance_residual": kinetic_invariance,
        "maximum_zero_wave_conservation_residual": maximum_conservation_residual,
        "minimum_master_selected_excluded_eigenvalue_gap": float(local_gap),
        "maximum_master_eigenvalue_condition_number": max(
            mode.eigenvalue_condition_number for mode in positive_modes.values()
        ),
        "symbol_conjugacy_residual": conjugacy_residual,
        "complex_realification_singular_value_relative_error": realification_error,
        "all_sector_statuses": sorted(
            {record.status for _, record in second_records + zero_records}
        ),
    }
