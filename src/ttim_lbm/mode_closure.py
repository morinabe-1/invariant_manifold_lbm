"""Finite-grid resonant mode-closure audit for the Q006r candidate.

The audit works entirely in D2Q9 Fourier sectors.  Selected coordinates are
stored as invariant spectral blocks, while nonresonant quadratic outputs remain
coefficient sectors of the chart.  Only singular or materially forced
near-singular external response clusters are promoted to reduced coordinates.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations_with_replacement, product
from numbers import Integral
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.linalg import orth, schur, solve_sylvester
from scipy.optimize import linear_sum_assignment

from .d2q9 import (
    conserved_moment_matrix,
    fourier_symbol,
    quarter_turn_population_matrix,
)
from .nonresonance import (
    NUMERICAL_RANK_MULTIPLIER,
    add_wave_indices,
    canonical_wave_index,
    fixed_leaf_kinetic_restriction,
    orthogonal_acoustic_resonance_witness,
    quadratic_fourier_forcing,
    simple_hydrodynamic_modes,
    wave_vector_from_index,
)

ComplexArray = npt.NDArray[np.complex128]
WaveIndex = tuple[int, int]

CLUSTER_RELATIVE_TOLERANCE = 1.0e-8
RESPONSE_ENERGY_TOLERANCE = 1.0e-8
RESPONSE_ENERGY_TIE_TOLERANCE = 1.0e-12
NEAR_SINGULAR_RELATIVE_THRESHOLD = 1.0e-4
FORCING_SENSITIVITY_THRESHOLD = 1.0e-10
MATERIAL_NEAR_CONDITION_CEILING = 1.0e4
PRACTICAL_CONDITION_CEILING = 1.0e8
MAXIMUM_NONEMPTY_ADDITIONS = 4
MAXIMUM_REAL_COORDINATES = 64
STRUCTURAL_RESIDUAL_TOLERANCE = 1.0e-10
NORMAL_DOMINANCE_GAP_THRESHOLD = 1.0e-6
LOCAL_SYLVESTER_SEPARATION_THRESHOLD = 1.0e-6
PROJECTOR_NORM_CEILING = 100.0


@dataclass(frozen=True)
class SpectralBlock:
    """One selected complex invariant block at a discrete Fourier wave."""

    identifier: str
    wave_index: WaveIndex
    basis: ComplexArray
    dynamics: ComplexArray
    eigenvalues: ComplexArray
    origin: str
    label: str
    invariance_residual: float

    @property
    def dimension(self) -> int:
        return int(self.basis.shape[1])


@dataclass(frozen=True)
class _OrderedSelection:
    basis: ComplexArray
    dynamics: ComplexArray
    projector: ComplexArray
    selected_eigenvalues: ComplexArray
    excluded_eigenvalues: ComplexArray
    invariance_residual: float
    projector_idempotency_residual: float
    projector_commutator_residual: float


@dataclass(frozen=True)
class _Sector:
    wave_index: WaveIndex
    active_basis: ComplexArray
    active_matrix: ComplexArray
    selected_basis: ComplexArray
    selected_matrix: ComplexArray
    selected_projector: ComplexArray
    external_projector: ComplexArray
    external_basis: ComplexArray
    external_matrix: ComplexArray
    selected_eigenvalues: ComplexArray
    excluded_eigenvalues: ComplexArray
    local_sylvester_separation: float | None
    selected_projector_norm: float
    maximum_structural_residual: float
    fixed_leaf_residual: float

    @property
    def selected_dimension(self) -> int:
        return int(self.selected_basis.shape[1])

    @property
    def external_dimension(self) -> int:
        return int(self.external_basis.shape[1])


@dataclass(frozen=True)
class _ExternalCluster:
    identifier: int
    basis: ComplexArray
    dynamics: ComplexArray
    eigenvalues: ComplexArray
    invariance_residual: float
    projector_norm: float
    projector_residual: float

    @property
    def dimension(self) -> int:
        return int(self.basis.shape[1])


@dataclass(frozen=True)
class _AdditionCandidate:
    wave_index: WaveIndex
    basis: ComplexArray
    source_pair: str
    response_kind: str
    cluster_identifier: int
    eigenvalues: ComplexArray
    response_energy: float


def _require_registered_parameters(size: int, omega: float) -> tuple[int, float]:
    if (
        isinstance(size, bool)
        or not isinstance(size, Integral)
        or int(size) < 5
        or int(size) % 2 == 0
    ):
        raise ValueError("Q006r requires an odd grid size of at least five")
    omega = float(omega)
    if not np.isfinite(omega) or not 0.0 < omega < 2.0:
        raise ValueError("omega must be finite and lie in (0, 2)")
    if int(size) != 17 or omega != 1.2:
        raise ValueError("the sealed Q006r audit is fixed at N=17 and omega=1.2")
    return int(size), omega


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _complex_records(values: npt.ArrayLike) -> list[dict[str, float]]:
    return [_complex_record(complex(value)) for value in np.asarray(values).ravel()]


def _orthonormal_basis(vectors: npt.ArrayLike, expected_dimension: int) -> ComplexArray:
    matrix = np.asarray(vectors, dtype=np.complex128)
    if matrix.ndim != 2:
        raise ValueError("basis candidates must form a matrix")
    if expected_dimension == 0:
        return np.empty((matrix.shape[0], 0), dtype=np.complex128)
    basis = np.asarray(orth(matrix), dtype=np.complex128)
    if basis.shape != (matrix.shape[0], expected_dimension):
        raise np.linalg.LinAlgError(
            "candidate invariant blocks do not form the registered direct sum"
        )
    return basis


def _relative_residual(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    numerator_norm = float(np.linalg.norm(np.asarray(numerator)))
    denominator_norm = max(
        float(np.linalg.norm(np.asarray(denominator))),
        np.finfo(float).eps,
    )
    return numerator_norm / denominator_norm


def _subspace_residual(candidate: ComplexArray, reference: ComplexArray) -> float:
    if candidate.shape[1] == 0:
        return 0.0
    if reference.shape[1] == 0:
        return 1.0
    candidate_basis = _orthonormal_basis(candidate, candidate.shape[1])
    reference_basis = _orthonormal_basis(reference, reference.shape[1])
    residual = candidate_basis - reference_basis @ (
        reference_basis.conj().T @ candidate_basis
    )
    return float(np.linalg.norm(residual, ord=2))


def _matched_partition(
    eigenvalues: ComplexArray,
    target_eigenvalues: ComplexArray,
) -> tuple[ComplexArray, ComplexArray]:
    target = np.asarray(target_eigenvalues, dtype=np.complex128).ravel()
    values = np.asarray(eigenvalues, dtype=np.complex128).ravel()
    if target.size == 0:
        return target, values
    if target.size > values.size:
        raise ValueError("more selected eigenvalues were requested than exist")
    row_indices, column_indices = linear_sum_assignment(
        np.abs(target[:, None] - values[None, :])
    )
    if row_indices.size != target.size:
        raise np.linalg.LinAlgError("selected eigenvalues could not be matched")
    selected_indices = {int(index) for index in column_indices}
    selected = values[sorted(selected_indices)]
    excluded = values[
        [index for index in range(values.size) if index not in selected_indices]
    ]
    return selected, excluded


def _ordered_selection(
    matrix: npt.ArrayLike,
    target_eigenvalues: npt.ArrayLike,
) -> _OrderedSelection:
    value = np.asarray(matrix, dtype=np.complex128)
    if value.ndim != 2 or value.shape[0] != value.shape[1]:
        raise ValueError("ordered selection requires a square matrix")
    dimension = value.shape[0]
    targets = np.asarray(target_eigenvalues, dtype=np.complex128).ravel()
    selected_dimension = int(targets.size)
    if selected_dimension == 0:
        return _OrderedSelection(
            basis=np.empty((dimension, 0), dtype=np.complex128),
            dynamics=np.empty((0, 0), dtype=np.complex128),
            projector=np.zeros_like(value),
            selected_eigenvalues=targets,
            excluded_eigenvalues=np.asarray(
                np.linalg.eigvals(value), dtype=np.complex128
            ),
            invariance_residual=0.0,
            projector_idempotency_residual=0.0,
            projector_commutator_residual=0.0,
        )
    if selected_dimension == dimension:
        identity = np.eye(dimension, dtype=np.complex128)
        return _OrderedSelection(
            basis=identity,
            dynamics=value.copy(),
            projector=identity,
            selected_eigenvalues=np.asarray(
                np.linalg.eigvals(value), dtype=np.complex128
            ),
            excluded_eigenvalues=np.empty(0, dtype=np.complex128),
            invariance_residual=0.0,
            projector_idempotency_residual=0.0,
            projector_commutator_residual=0.0,
        )

    all_eigenvalues = np.asarray(np.linalg.eigvals(value), dtype=np.complex128)
    selected_reference, excluded_reference = _matched_partition(
        all_eigenvalues,
        targets,
    )

    def selector(eigenvalue: complex) -> bool:
        selected_distance = float(np.min(np.abs(eigenvalue - selected_reference)))
        excluded_distance = float(np.min(np.abs(eigenvalue - excluded_reference)))
        return selected_distance < excluded_distance

    triangular, unitary, count = schur(
        value,
        output="complex",
        sort=selector,
    )
    if count != selected_dimension:
        raise np.linalg.LinAlgError(
            "ordered Schur selection split an unresolved eigenvalue cluster"
        )
    selected_block = np.asarray(
        triangular[:selected_dimension, :selected_dimension],
        dtype=np.complex128,
    )
    coupling = triangular[:selected_dimension, selected_dimension:]
    excluded_block = triangular[selected_dimension:, selected_dimension:]
    projector_coupling = solve_sylvester(
        selected_block,
        -excluded_block,
        coupling,
    )
    schur_projector = np.zeros_like(triangular)
    schur_projector[:selected_dimension, :selected_dimension] = np.eye(
        selected_dimension
    )
    schur_projector[:selected_dimension, selected_dimension:] = projector_coupling
    projector = unitary @ schur_projector @ unitary.conj().T
    basis = np.asarray(unitary[:, :selected_dimension], dtype=np.complex128)
    matrix_scale = max(float(np.linalg.norm(value)), np.finfo(float).eps)
    return _OrderedSelection(
        basis=basis,
        dynamics=selected_block,
        projector=np.asarray(projector, dtype=np.complex128),
        selected_eigenvalues=np.asarray(
            np.linalg.eigvals(selected_block), dtype=np.complex128
        ),
        excluded_eigenvalues=np.asarray(
            np.linalg.eigvals(excluded_block), dtype=np.complex128
        ),
        invariance_residual=float(
            np.linalg.norm(value @ basis - basis @ selected_block) / matrix_scale
        ),
        projector_idempotency_residual=float(
            np.linalg.norm(projector @ projector - projector)
        ),
        projector_commutator_residual=float(
            np.linalg.norm(value @ projector - projector @ value) / matrix_scale
        ),
    )


def _active_sector(
    wave_index: WaveIndex,
    size: int,
    omega: float,
) -> tuple[ComplexArray, ComplexArray, float]:
    wave_index = canonical_wave_index(wave_index, size)
    if wave_index == (0, 0):
        basis, block, invariance = fixed_leaf_kinetic_restriction(omega)
        return basis, block, invariance
    wave_vector = wave_vector_from_index(wave_index, size)
    identity = np.eye(9, dtype=np.complex128)
    return identity, fourier_symbol(*wave_vector, omega), 0.0


def _make_block(
    identifier: str,
    wave_index: WaveIndex,
    raw_basis: npt.ArrayLike,
    origin: str,
    label: str,
    size: int,
    omega: float,
) -> SpectralBlock:
    wave_index = canonical_wave_index(wave_index, size)
    candidate = np.asarray(raw_basis, dtype=np.complex128)
    if candidate.ndim != 2 or candidate.shape[0] != 9 or candidate.shape[1] == 0:
        raise ValueError("population spectral blocks must have shape (9, d), d > 0")
    basis = _orthonormal_basis(candidate, candidate.shape[1])
    wave_vector = wave_vector_from_index(wave_index, size)
    matrix = fourier_symbol(*wave_vector, omega)
    dynamics = basis.conj().T @ matrix @ basis
    invariance = _relative_residual(matrix @ basis - basis @ dynamics, matrix)
    if invariance > STRUCTURAL_RESIDUAL_TOLERANCE:
        raise np.linalg.LinAlgError("candidate mode addition is not invariant")
    if wave_index == (0, 0):
        conservation = np.linalg.norm(conserved_moment_matrix() @ basis)
        if conservation > STRUCTURAL_RESIDUAL_TOLERANCE:
            raise np.linalg.LinAlgError("zero-wave block leaves the fixed leaf")
    return SpectralBlock(
        identifier=identifier,
        wave_index=wave_index,
        basis=basis,
        dynamics=np.asarray(dynamics, dtype=np.complex128),
        eigenvalues=np.asarray(np.linalg.eigvals(dynamics), dtype=np.complex128),
        origin=origin,
        label=label,
        invariance_residual=invariance,
    )


def _initial_blocks(size: int, omega: float) -> list[SpectralBlock]:
    axial_orbit = ((1, 0), (0, 1), (-1, 0), (0, -1))
    diagonal_orbit = ((1, 1), (-1, 1), (-1, -1), (1, -1))
    labels = ("shear", "acoustic_positive", "acoustic_negative")
    blocks: list[SpectralBlock] = []
    counter = 0
    for wave_index in axial_orbit:
        modes = simple_hydrodynamic_modes(
            *wave_vector_from_index(wave_index, size),
            omega,
        )
        for label in labels:
            mode = modes[label]
            blocks.append(
                _make_block(
                    identifier=f"i{counter:03d}",
                    wave_index=wave_index,
                    raw_basis=mode.right_eigenvector[:, None],
                    origin="initial axial first-shell hydrodynamic mode",
                    label=label,
                    size=size,
                    omega=omega,
                )
            )
            counter += 1
    for wave_index in diagonal_orbit:
        mode = simple_hydrodynamic_modes(
            *wave_vector_from_index(wave_index, size),
            omega,
        )["shear"]
        blocks.append(
            _make_block(
                identifier=f"i{counter:03d}",
                wave_index=wave_index,
                raw_basis=mode.right_eigenvector[:, None],
                origin="initial diagonal-shear witness orbit",
                label="shear",
                size=size,
                omega=omega,
            )
        )
        counter += 1
    if sum(block.dimension for block in blocks) != 16:
        raise RuntimeError("registered Q006r initial set must have 16 real coordinates")
    return blocks


def _blocks_at_wave(
    blocks: list[SpectralBlock],
    wave_index: WaveIndex,
) -> list[SpectralBlock]:
    return [block for block in blocks if block.wave_index == wave_index]


def _build_sector(
    wave_index: WaveIndex,
    blocks: list[SpectralBlock],
    size: int,
    omega: float,
) -> _Sector:
    wave_index = canonical_wave_index(wave_index, size)
    active_basis, active_matrix, active_invariance = _active_sector(
        wave_index,
        size,
        omega,
    )
    wave_blocks = _blocks_at_wave(blocks, wave_index)
    selected_dimension = sum(block.dimension for block in wave_blocks)
    if wave_blocks:
        population_basis = np.column_stack([block.basis for block in wave_blocks])
        active_candidates = active_basis.conj().T @ population_basis
        selected_basis = _orthonormal_basis(
            active_candidates,
            selected_dimension,
        )
        target_eigenvalues = np.concatenate(
            [block.eigenvalues for block in wave_blocks]
        )
    else:
        selected_basis = np.empty(
            (active_matrix.shape[0], 0), dtype=np.complex128
        )
        target_eigenvalues = np.empty(0, dtype=np.complex128)
    ordered = _ordered_selection(active_matrix, target_eigenvalues)
    selected_range_error = max(
        _subspace_residual(selected_basis, ordered.basis),
        _subspace_residual(ordered.basis, selected_basis),
    )
    if selected_range_error > STRUCTURAL_RESIDUAL_TOLERANCE:
        raise np.linalg.LinAlgError(
            "selected block basis and ordered Schur range disagree"
        )
    selected_matrix = selected_basis.conj().T @ active_matrix @ selected_basis
    external_projector = np.eye(active_matrix.shape[0]) - ordered.projector
    external_dimension = active_matrix.shape[0] - selected_dimension
    external_basis = _orthonormal_basis(
        external_projector,
        external_dimension,
    )
    external_matrix = external_basis.conj().T @ active_matrix @ external_basis
    external_invariance = _relative_residual(
        active_matrix @ external_basis - external_basis @ external_matrix,
        active_matrix,
    )
    selected_invariance = _relative_residual(
        active_matrix @ selected_basis - selected_basis @ selected_matrix,
        active_matrix,
    )
    if selected_dimension and external_dimension:
        sylvester = (
            np.kron(np.eye(external_dimension), selected_matrix)
            - np.kron(external_matrix.T, np.eye(selected_dimension))
        )
        local_separation = float(
            np.min(np.linalg.svd(sylvester, compute_uv=False))
        )
    else:
        local_separation = None
    fixed_leaf_residual = active_invariance
    if wave_index == (0, 0):
        fixed_leaf_residual = max(
            fixed_leaf_residual,
            float(np.linalg.norm(conserved_moment_matrix() @ active_basis)),
        )
    maximum_structural_residual = max(
        active_invariance,
        selected_range_error,
        selected_invariance,
        external_invariance,
        ordered.invariance_residual,
        ordered.projector_idempotency_residual,
        ordered.projector_commutator_residual,
        max((block.invariance_residual for block in wave_blocks), default=0.0),
    )
    return _Sector(
        wave_index=wave_index,
        active_basis=active_basis,
        active_matrix=active_matrix,
        selected_basis=selected_basis,
        selected_matrix=np.asarray(selected_matrix, dtype=np.complex128),
        selected_projector=ordered.projector,
        external_projector=np.asarray(external_projector, dtype=np.complex128),
        external_basis=external_basis,
        external_matrix=np.asarray(external_matrix, dtype=np.complex128),
        selected_eigenvalues=ordered.selected_eigenvalues,
        excluded_eigenvalues=ordered.excluded_eigenvalues,
        local_sylvester_separation=local_separation,
        selected_projector_norm=float(np.linalg.norm(ordered.projector, ord=2)),
        maximum_structural_residual=maximum_structural_residual,
        fixed_leaf_residual=fixed_leaf_residual,
    )


def _cluster_components(eigenvalues: ComplexArray, tolerance: float) -> list[list[int]]:
    remaining = set(range(eigenvalues.size))
    components: list[list[int]] = []
    while remaining:
        seed = min(remaining)
        stack = [seed]
        component: set[int] = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            remaining.discard(current)
            neighbors = {
                index
                for index in list(remaining)
                if abs(eigenvalues[current] - eigenvalues[index]) <= tolerance
            }
            stack.extend(sorted(neighbors, reverse=True))
        components.append(sorted(component))
    components.sort(
        key=lambda component: (
            min(float(eigenvalues[index].real) for index in component),
            min(float(eigenvalues[index].imag) for index in component),
            len(component),
        )
    )
    return components


def _external_clusters(matrix: ComplexArray) -> list[_ExternalCluster]:
    dimension = matrix.shape[0]
    if dimension == 0:
        return []
    eigenvalues = np.asarray(np.linalg.eigvals(matrix), dtype=np.complex128)
    tolerance = CLUSTER_RELATIVE_TOLERANCE * max(
        1.0,
        float(np.linalg.norm(matrix, ord=2)),
    )
    clusters: list[_ExternalCluster] = []
    for identifier, component in enumerate(
        _cluster_components(eigenvalues, tolerance)
    ):
        ordered = _ordered_selection(matrix, eigenvalues[component])
        projector_residual = max(
            ordered.projector_idempotency_residual,
            ordered.projector_commutator_residual,
        )
        clusters.append(
            _ExternalCluster(
                identifier=identifier,
                basis=ordered.basis,
                dynamics=ordered.dynamics,
                eigenvalues=ordered.selected_eigenvalues,
                invariance_residual=ordered.invariance_residual,
                projector_norm=float(np.linalg.norm(ordered.projector, ord=2)),
                projector_residual=projector_residual,
            )
        )
    if sum(cluster.dimension for cluster in clusters) != dimension:
        raise RuntimeError("external eigenvalue clusters do not cover the block")
    return clusters


def _symmetric_product_basis(dimension: int) -> ComplexArray:
    columns: list[ComplexArray] = []
    for left in range(dimension):
        for right in range(left, dimension):
            tensor = np.zeros(dimension * dimension, dtype=np.complex128)
            tensor[left * dimension + right] += 1.0
            tensor[right * dimension + left] += 1.0
            tensor /= np.sqrt(2.0 * (1.0 + float(left == right)))
            columns.append(tensor)
    return np.column_stack(columns)


def _product_block_and_forcing(
    left: SpectralBlock,
    right: SpectralBlock,
    output_wave: WaveIndex,
    size: int,
    omega: float,
) -> tuple[ComplexArray, ComplexArray, str, float]:
    left_dimension = left.dimension
    right_dimension = right.dimension
    full_dynamics = np.kron(left.dynamics, right.dynamics)
    forcing_columns = [
        quadratic_fourier_forcing(
            left.basis[:, left_index],
            right.basis[:, right_index],
            wave_vector_from_index(output_wave, size),
            omega,
        )
        for left_index in range(left_dimension)
        for right_index in range(right_dimension)
    ]
    full_forcing = np.column_stack(forcing_columns)
    if left.identifier != right.identifier:
        return full_dynamics, full_forcing, "Kronecker", 0.0
    symmetric_basis = _symmetric_product_basis(left_dimension)
    product_dynamics = symmetric_basis.conj().T @ full_dynamics @ symmetric_basis
    leakage = _relative_residual(
        full_dynamics @ symmetric_basis
        - symmetric_basis @ product_dynamics,
        full_dynamics,
    )
    return (
        np.asarray(product_dynamics, dtype=np.complex128),
        np.asarray(full_forcing @ symmetric_basis, dtype=np.complex128),
        "orthonormal symmetric tensor product",
        leakage,
    )


def _response_energy_records(
    clusters: list[_ExternalCluster],
    right_singular_vectors: ComplexArray,
    singular_indices: npt.NDArray[np.int64],
    external_dimension: int,
    product_dimension: int,
) -> tuple[list[dict[str, Any]], list[int]]:
    if singular_indices.size == 0:
        return [], []
    covariance = np.zeros(
        (external_dimension, external_dimension), dtype=np.complex128
    )
    for index in singular_indices:
        response = right_singular_vectors[:, int(index)].reshape(
            (external_dimension, product_dimension),
            order="F",
        )
        covariance += response @ response.conj().T
    denominator = max(float(np.trace(covariance).real), np.finfo(float).eps)
    energies = [
        float(np.trace(cluster.basis.conj().T @ covariance @ cluster.basis).real)
        / denominator
        for cluster in clusters
    ]
    chosen = [
        index
        for index, energy in enumerate(energies)
        if energy >= RESPONSE_ENERGY_TOLERANCE
    ]
    if not chosen:
        maximum = max(energies)
        chosen = [
            index
            for index, energy in enumerate(energies)
            if maximum - energy <= RESPONSE_ENERGY_TIE_TOLERANCE
        ]
    records = [
        {
            "cluster_identifier": cluster.identifier,
            "dimension": cluster.dimension,
            "eigenvalues": _complex_records(cluster.eigenvalues),
            "energy": energies[index],
            "selected_for_addition": index in chosen,
            "invariance_residual": cluster.invariance_residual,
            "projector_norm": cluster.projector_norm,
            "projector_residual": cluster.projector_residual,
        }
        for index, cluster in enumerate(clusters)
    ]
    return records, chosen


def _audit_pair(
    pair_index: int,
    left: SpectralBlock,
    right: SpectralBlock,
    sector: _Sector,
    size: int,
    omega: float,
) -> tuple[dict[str, Any], list[_AdditionCandidate]]:
    pair_identifier = f"p{pair_index:05d}"
    output_wave = sector.wave_index
    product_dynamics, forcing, product_basis, product_leakage = (
        _product_block_and_forcing(left, right, output_wave, size, omega)
    )
    product_dimension = product_dynamics.shape[0]
    base_record: dict[str, Any] = {
        "pair_identifier": pair_identifier,
        "left_block": left.identifier,
        "right_block": right.identifier,
        "left_wave_index": list(left.wave_index),
        "right_wave_index": list(right.wave_index),
        "output_wave_index": list(output_wave),
        "left_dimension": left.dimension,
        "right_dimension": right.dimension,
        "product_dimension": product_dimension,
        "product_basis": product_basis,
        "product_invariance_leakage": product_leakage,
        "external_dimension": sector.external_dimension,
    }
    if output_wave == (0, 0):
        fixed_leaf_forcing_residual = _relative_residual(
            conserved_moment_matrix() @ forcing,
            forcing,
        )
    else:
        fixed_leaf_forcing_residual = 0.0
    base_record["fixed_leaf_forcing_residual"] = fixed_leaf_forcing_residual
    if sector.external_dimension == 0:
        base_record.update(
            {
                "status": "internal_output_only",
                "operator_dimension": 0,
                "singular_values": [],
                "condition_number": None,
                "numerical_singular_count": 0,
                "near_singular_count": 0,
                "near_forcing_sensitivity": None,
                "null_forcing_ratio": None,
                "solve_relative_residual": None,
                "external_clusters": [],
                "maximum_external_cluster_structural_residual": 0.0,
                "response_groups": [],
            }
        )
        return base_record, []

    active_forcing = sector.active_basis.conj().T @ forcing
    external_forcing = sector.external_basis.conj().T @ (
        sector.external_projector @ active_forcing
    )
    operator = (
        np.kron(np.eye(product_dimension), sector.external_matrix)
        - np.kron(product_dynamics.T, np.eye(sector.external_dimension))
    )
    forcing_vector = external_forcing.reshape(-1, order="F")
    left_singular, singular_values, right_adjoint = np.linalg.svd(
        operator,
        full_matrices=False,
    )
    right_singular = right_adjoint.conj().T
    largest = float(singular_values[0])
    smallest = float(singular_values[-1])
    rank_threshold = float(
        NUMERICAL_RANK_MULTIPLIER
        * np.finfo(float).eps
        * max(operator.shape)
        * largest
    )
    singular_indices = np.flatnonzero(singular_values <= rank_threshold).astype(
        np.int64
    )
    relative_values = singular_values / max(largest, np.finfo(float).eps)
    near_indices = np.flatnonzero(
        (singular_values > rank_threshold)
        & (relative_values < NEAR_SINGULAR_RELATIVE_THRESHOLD)
    ).astype(np.int64)
    forcing_norm = max(float(np.linalg.norm(forcing_vector)), np.finfo(float).eps)

    def sensitivity(indices: npt.NDArray[np.int64]) -> float | None:
        if indices.size == 0:
            return None
        return float(
            np.linalg.norm(left_singular[:, indices].conj().T @ forcing_vector)
            / forcing_norm
        )

    null_forcing_ratio = sensitivity(singular_indices)
    near_forcing_sensitivity = sensitivity(near_indices)
    clusters = _external_clusters(sector.external_matrix)
    cluster_records = [
        {
            "cluster_identifier": cluster.identifier,
            "dimension": cluster.dimension,
            "eigenvalues": _complex_records(cluster.eigenvalues),
            "invariance_residual": cluster.invariance_residual,
            "projector_norm": cluster.projector_norm,
            "projector_residual": cluster.projector_residual,
        }
        for cluster in clusters
    ]
    maximum_cluster_structural = max(
        (
            max(cluster.invariance_residual, cluster.projector_residual)
            for cluster in clusters
        ),
        default=0.0,
    )
    candidates: list[_AdditionCandidate] = []
    response_groups: list[dict[str, Any]] = []
    for kind, indices, triggered in (
        ("numerically_singular", singular_indices, singular_indices.size > 0),
        (
            "materially_forced_near_singular",
            near_indices,
            near_indices.size > 0
            and near_forcing_sensitivity is not None
            and near_forcing_sensitivity >= FORCING_SENSITIVITY_THRESHOLD,
        ),
    ):
        energy_records, chosen = _response_energy_records(
            clusters,
            right_singular,
            indices,
            sector.external_dimension,
            product_dimension,
        )
        response_groups.append(
            {
                "kind": kind,
                "singular_direction_count": int(indices.size),
                "forcing_sensitivity": sensitivity(indices),
                "triggered": bool(triggered),
                "cluster_energies": energy_records,
            }
        )
        if triggered:
            for cluster_index in chosen:
                cluster = clusters[cluster_index]
                population_basis = (
                    sector.active_basis
                    @ sector.external_basis
                    @ cluster.basis
                )
                energy = next(
                    record["energy"]
                    for record in energy_records
                    if record["cluster_identifier"] == cluster.identifier
                )
                candidates.append(
                    _AdditionCandidate(
                        wave_index=output_wave,
                        basis=np.asarray(population_basis, dtype=np.complex128),
                        source_pair=pair_identifier,
                        response_kind=kind,
                        cluster_identifier=cluster.identifier,
                        eigenvalues=cluster.eigenvalues,
                        response_energy=float(energy),
                    )
                )
    if singular_indices.size:
        condition_number = None
        solve_residual = None
        status = "numerically_singular"
    else:
        condition_number = largest / max(smallest, np.finfo(float).eps)
        solution = np.linalg.solve(operator, forcing_vector)
        solve_residual = _relative_residual(
            operator @ solution - forcing_vector,
            forcing_vector,
        )
        status = (
            "near_singular"
            if near_indices.size
            else "nonsingular"
        )
    base_record.update(
        {
            "status": status,
            "operator_dimension": int(operator.shape[0]),
            "singular_values": [float(value) for value in singular_values],
            "relative_smallest_singular_value": smallest
            / max(largest, np.finfo(float).eps),
            "numerical_rank_threshold": rank_threshold,
            "condition_number": (
                None if condition_number is None else float(condition_number)
            ),
            "forcing_norm": float(np.linalg.norm(forcing_vector)),
            "numerical_singular_count": int(singular_indices.size),
            "near_singular_count": int(near_indices.size),
            "near_forcing_sensitivity": near_forcing_sensitivity,
            "null_forcing_ratio": null_forcing_ratio,
            "solve_relative_residual": solve_residual,
            "external_clusters": cluster_records,
            "maximum_external_cluster_structural_residual": (
                maximum_cluster_structural
            ),
            "response_groups": response_groups,
        }
    )
    return base_record, candidates


def _rotation_index(index: WaveIndex, size: int) -> WaveIndex:
    return canonical_wave_index((-index[1], index[0]), size)


def _negative_index(index: WaveIndex, size: int) -> WaveIndex:
    return canonical_wave_index((-index[0], -index[1]), size)


def _best_matching_block(
    blocks: list[SpectralBlock],
    wave_index: WaveIndex,
    basis: ComplexArray,
) -> tuple[str | None, float]:
    matches = [
        block
        for block in blocks
        if block.wave_index == wave_index and block.dimension == basis.shape[1]
    ]
    if not matches:
        return None, 1.0
    scored = [
        (max(_subspace_residual(basis, block.basis), _subspace_residual(block.basis, basis)), block)
        for block in matches
    ]
    residual, block = min(scored, key=lambda item: (item[0], item[1].identifier))
    return block.identifier, float(residual)


def _symmetry_diagnostics(
    blocks: list[SpectralBlock],
    size: int,
) -> dict[str, Any]:
    rotation = np.asarray(quarter_turn_population_matrix(), dtype=np.complex128)
    c4_mapping = []
    conjugate_mapping = []
    maximum_c4 = 0.0
    maximum_conjugacy = 0.0
    for block in blocks:
        rotated_wave = _rotation_index(block.wave_index, size)
        rotated_identifier, c4_residual = _best_matching_block(
            blocks,
            rotated_wave,
            rotation @ block.basis,
        )
        conjugate_wave = _negative_index(block.wave_index, size)
        conjugate_identifier, conjugacy_residual = _best_matching_block(
            blocks,
            conjugate_wave,
            np.conjugate(block.basis),
        )
        maximum_c4 = max(maximum_c4, c4_residual)
        maximum_conjugacy = max(maximum_conjugacy, conjugacy_residual)
        c4_mapping.append(
            {
                "source": block.identifier,
                "target": rotated_identifier,
                "source_wave_index": list(block.wave_index),
                "target_wave_index": list(rotated_wave),
                "subspace_residual": c4_residual,
            }
        )
        conjugate_mapping.append(
            {
                "source": block.identifier,
                "target": conjugate_identifier,
                "source_wave_index": list(block.wave_index),
                "target_wave_index": list(conjugate_wave),
                "subspace_residual": conjugacy_residual,
            }
        )
    return {
        "c4_mapping": c4_mapping,
        "conjugate_pairing": conjugate_mapping,
        "maximum_c4_subspace_residual": maximum_c4,
        "maximum_conjugacy_subspace_residual": maximum_conjugacy,
    }


def _candidate_is_contained(
    blocks: list[SpectralBlock],
    wave_index: WaveIndex,
    basis: ComplexArray,
) -> bool:
    existing = _blocks_at_wave(blocks, wave_index)
    if not existing:
        return False
    existing_matrix = np.column_stack([block.basis for block in existing])
    existing_basis = _orthonormal_basis(
        existing_matrix,
        sum(block.dimension for block in existing),
    )
    residual = _subspace_residual(basis, existing_basis)
    if residual <= STRUCTURAL_RESIDUAL_TOLERANCE:
        return True
    combined = np.column_stack([existing_basis, basis])
    combined_rank = np.linalg.matrix_rank(
        combined,
        tol=STRUCTURAL_RESIDUAL_TOLERANCE,
    )
    expected = existing_basis.shape[1] + basis.shape[1]
    if combined_rank != expected:
        raise np.linalg.LinAlgError(
            "a symmetry orbit partially overlaps an existing spectral cluster"
        )
    return False


def _collect_orbit_additions(
    blocks: list[SpectralBlock],
    candidates: list[_AdditionCandidate],
    round_index: int,
    size: int,
    omega: float,
) -> tuple[list[SpectralBlock], list[dict[str, Any]]]:
    rotation = np.asarray(quarter_turn_population_matrix(), dtype=np.complex128)
    pending: list[SpectralBlock] = []
    orbit_records: list[dict[str, Any]] = []
    for candidate in candidates:
        members: list[dict[str, Any]] = []
        seed_basis = candidate.basis
        seed_wave = candidate.wave_index
        rotation_basis = seed_basis
        rotation_wave = seed_wave
        transformations: list[tuple[str, WaveIndex, ComplexArray]] = []
        for power in range(4):
            transformations.append((f"C4^{power}", rotation_wave, rotation_basis))
            transformations.append(
                (
                    f"conjugate(C4^{power})",
                    _negative_index(rotation_wave, size),
                    np.conjugate(rotation_basis),
                )
            )
            rotation_wave = _rotation_index(rotation_wave, size)
            rotation_basis = rotation @ rotation_basis
        for transformation, wave_index, raw_basis in transformations:
            current = blocks + pending
            if _candidate_is_contained(current, wave_index, raw_basis):
                continue
            identifier = (
                f"r{round_index + 1:02d}o{len(orbit_records):03d}"
                f"m{len(members):02d}"
            )
            block = _make_block(
                identifier=identifier,
                wave_index=wave_index,
                raw_basis=raw_basis,
                origin=(
                    f"{candidate.response_kind} response from "
                    f"{candidate.source_pair}"
                ),
                label="added_external_cluster",
                size=size,
                omega=omega,
            )
            pending.append(block)
            members.append(
                {
                    "identifier": block.identifier,
                    "wave_index": list(block.wave_index),
                    "dimension": block.dimension,
                    "transformation": transformation,
                    "eigenvalues": _complex_records(block.eigenvalues),
                }
            )
        if members:
            orbit_records.append(
                {
                    "source_pair": candidate.source_pair,
                    "response_kind": candidate.response_kind,
                    "source_wave_index": list(candidate.wave_index),
                    "source_cluster_identifier": candidate.cluster_identifier,
                    "source_cluster_eigenvalues": _complex_records(
                        candidate.eigenvalues
                    ),
                    "response_energy": candidate.response_energy,
                    "members": members,
                }
            )
    return pending, orbit_records


def _condition_summary(pair_records: list[dict[str, Any]]) -> dict[str, Any]:
    conditioned = [
        record
        for record in pair_records
        if record["condition_number"] is not None
    ]
    conditions = np.asarray(
        [record["condition_number"] for record in conditioned],
        dtype=np.float64,
    )
    if conditions.size:
        worst_index = int(np.argmax(conditions))
        worst = conditioned[worst_index]
        quantiles = {
            "minimum": float(np.min(conditions)),
            "median": float(np.quantile(conditions, 0.5)),
            "q90": float(np.quantile(conditions, 0.9)),
            "q99": float(np.quantile(conditions, 0.99)),
            "maximum": float(np.max(conditions)),
        }
        worst_pair = worst["pair_identifier"]
    else:
        quantiles = {
            "minimum": None,
            "median": None,
            "q90": None,
            "q99": None,
            "maximum": None,
        }
        worst_pair = None
    materially_forced_near = [
        record
        for record in conditioned
        if record["near_singular_count"] > 0
        and record["near_forcing_sensitivity"] is not None
        and record["near_forcing_sensitivity"] >= FORCING_SENSITIVITY_THRESHOLD
    ]
    return {
        "condition_quantiles": quantiles,
        "worst_condition_pair": worst_pair,
        "maximum_condition_number": (
            float(np.max(conditions)) if conditions.size else 0.0
        ),
        "maximum_materially_forced_near_condition_number": max(
            (record["condition_number"] for record in materially_forced_near),
            default=0.0,
        ),
    }


def _audit_round(
    blocks: list[SpectralBlock],
    round_index: int,
    size: int,
    omega: float,
) -> tuple[dict[str, Any], list[_AdditionCandidate]]:
    sector_cache: dict[WaveIndex, _Sector] = {}

    def sector(wave_index: WaveIndex) -> _Sector:
        canonical = canonical_wave_index(wave_index, size)
        if canonical not in sector_cache:
            sector_cache[canonical] = _build_sector(
                canonical,
                blocks,
                size,
                omega,
            )
        return sector_cache[canonical]

    pair_records: list[dict[str, Any]] = []
    candidates: list[_AdditionCandidate] = []
    for pair_index, (left, right) in enumerate(
        combinations_with_replacement(blocks, 2)
    ):
        output_wave = add_wave_indices(left.wave_index, right.wave_index, size)
        record, pair_candidates = _audit_pair(
            pair_index,
            left,
            right,
            sector(output_wave),
            size,
            omega,
        )
        pair_records.append(record)
        candidates.extend(pair_candidates)

    for wave_index in {block.wave_index for block in blocks}:
        sector(wave_index)
    symmetry = _symmetry_diagnostics(blocks, size)
    condition_summary = _condition_summary(pair_records)
    expected_pairs = len(blocks) * (len(blocks) + 1) // 2
    numerical_singular_count = sum(
        record["numerical_singular_count"] > 0 for record in pair_records
    )
    near_singular_count = sum(
        record["near_singular_count"] > 0 for record in pair_records
    )
    maximum_solve_residual = max(
        (
            record["solve_relative_residual"]
            for record in pair_records
            if record["solve_relative_residual"] is not None
        ),
        default=0.0,
    )
    maximum_product_leakage = max(
        record["product_invariance_leakage"] for record in pair_records
    )
    maximum_cluster_structural = max(
        record["maximum_external_cluster_structural_residual"]
        for record in pair_records
    )
    maximum_sector_structural = max(
        item.maximum_structural_residual for item in sector_cache.values()
    )
    maximum_fixed_leaf = max(
        max(item.fixed_leaf_residual for item in sector_cache.values()),
        max(record["fixed_leaf_forcing_residual"] for record in pair_records),
    )
    maximum_structural = max(
        maximum_product_leakage,
        maximum_cluster_structural,
        maximum_sector_structural,
        maximum_fixed_leaf,
        symmetry["maximum_c4_subspace_residual"],
        symmetry["maximum_conjugacy_subspace_residual"],
    )
    round_record = {
        "round_index": round_index,
        "selected_block_count": len(blocks),
        "selected_real_dimension": sum(block.dimension for block in blocks),
        "enumerated_pair_count": len(pair_records),
        "expected_pair_count": expected_pairs,
        "pair_enumeration_complete": len(pair_records) == expected_pairs,
        "numerically_singular_external_block_count": numerical_singular_count,
        "near_singular_external_block_count": near_singular_count,
        "requested_response_cluster_count": len(candidates),
        "maximum_solve_relative_residual": maximum_solve_residual,
        "maximum_product_invariance_leakage": maximum_product_leakage,
        "maximum_external_cluster_structural_residual": (
            maximum_cluster_structural
        ),
        "maximum_sector_structural_residual": maximum_sector_structural,
        "maximum_fixed_leaf_residual": maximum_fixed_leaf,
        "maximum_structural_residual": maximum_structural,
        "symmetry": symmetry,
        **condition_summary,
        "pair_table": pair_records,
    }
    return round_record, candidates


def _normal_dominance_screen(
    blocks: list[SpectralBlock],
    size: int,
    omega: float,
    coefficient_passed: bool,
) -> dict[str, Any]:
    half = size // 2
    sectors: list[dict[str, Any]] = []
    selected_moduli: list[tuple[float, WaveIndex, complex]] = []
    excluded_moduli: list[tuple[float, WaveIndex, complex]] = []
    local_separations: list[tuple[float, WaveIndex]] = []
    projector_norms: list[tuple[float, WaveIndex]] = []
    maximum_structural = 0.0
    for raw_index in product(range(-half, half + 1), repeat=2):
        wave_index = (int(raw_index[0]), int(raw_index[1]))
        sector = _build_sector(wave_index, blocks, size, omega)
        maximum_structural = max(
            maximum_structural,
            sector.maximum_structural_residual,
            sector.fixed_leaf_residual,
        )
        selected_moduli.extend(
            (float(abs(value)), wave_index, complex(value))
            for value in sector.selected_eigenvalues
        )
        excluded_moduli.extend(
            (float(abs(value)), wave_index, complex(value))
            for value in sector.excluded_eigenvalues
        )
        if sector.selected_dimension and sector.external_dimension:
            if sector.local_sylvester_separation is None:
                raise RuntimeError("mixed sector omitted its local separation")
            local_separations.append(
                (sector.local_sylvester_separation, wave_index)
            )
            projector_norms.append((sector.selected_projector_norm, wave_index))
            sectors.append(
                {
                    "wave_index": list(wave_index),
                    "selected_dimension": sector.selected_dimension,
                    "external_dimension": sector.external_dimension,
                    "local_sylvester_separation": (
                        sector.local_sylvester_separation
                    ),
                    "selected_riesz_projector_norm": (
                        sector.selected_projector_norm
                    ),
                    "maximum_structural_residual": (
                        sector.maximum_structural_residual
                    ),
                }
            )
    if not selected_moduli or not excluded_moduli:
        raise RuntimeError("normal-dominance screen requires both spectral sets")
    minimum_selected = min(selected_moduli, key=lambda item: item[0])
    maximum_excluded = max(excluded_moduli, key=lambda item: item[0])
    normal_gap = minimum_selected[0] - maximum_excluded[0]
    minimum_local = min(local_separations, key=lambda item: item[0])
    maximum_projector = max(projector_norms, key=lambda item: item[0])
    gates = {
        "coefficient_solvability_prerequisite": {
            "value": coefficient_passed,
            "threshold": True,
            "passed": coefficient_passed,
        },
        "normal_dominance_gap": {
            "value": normal_gap,
            "threshold": NORMAL_DOMINANCE_GAP_THRESHOLD,
            "passed": normal_gap >= NORMAL_DOMINANCE_GAP_THRESHOLD,
        },
        "local_sylvester_separation": {
            "value": minimum_local[0],
            "threshold": LOCAL_SYLVESTER_SEPARATION_THRESHOLD,
            "passed": minimum_local[0]
            >= LOCAL_SYLVESTER_SEPARATION_THRESHOLD,
        },
        "selected_riesz_projector_norm": {
            "value": maximum_projector[0],
            "threshold": PROJECTOR_NORM_CEILING,
            "passed": maximum_projector[0] <= PROJECTOR_NORM_CEILING,
        },
    }
    return {
        "gates": gates,
        "passed": all(gate["passed"] for gate in gates.values()),
        "minimum_selected_modulus": minimum_selected[0],
        "minimum_selected_wave_index": list(minimum_selected[1]),
        "minimum_selected_eigenvalue": _complex_record(minimum_selected[2]),
        "maximum_excluded_modulus": maximum_excluded[0],
        "maximum_excluded_wave_index": list(maximum_excluded[1]),
        "maximum_excluded_eigenvalue": _complex_record(maximum_excluded[2]),
        "normal_dominance_gap": normal_gap,
        "minimum_local_sylvester_separation": minimum_local[0],
        "minimum_local_separation_wave_index": list(minimum_local[1]),
        "maximum_selected_riesz_projector_norm": maximum_projector[0],
        "maximum_projector_wave_index": list(maximum_projector[1]),
        "maximum_structural_residual": maximum_structural,
        "mixed_sector_count": len(sectors),
        "mixed_sectors": sectors,
        "zero_wave_conserved_directions": (
            "excluded from both selected and external sets by the active "
            "fixed-leaf restriction"
        ),
    }


def _block_record(block: SpectralBlock) -> dict[str, Any]:
    return {
        "identifier": block.identifier,
        "wave_index": list(block.wave_index),
        "dimension": block.dimension,
        "label": block.label,
        "origin": block.origin,
        "eigenvalues": _complex_records(block.eigenvalues),
        "invariance_residual": block.invariance_residual,
    }


def run_mode_added_closure_audit(
    size: int = 17,
    omega: float = 1.2,
) -> dict[str, Any]:
    """Run the sealed Q006r closure and normal-dominance audit."""

    size, omega = _require_registered_parameters(size, omega)
    blocks = _initial_blocks(size, omega)
    initial_symmetry = _symmetry_diagnostics(blocks, size)
    initial_records = [_block_record(block) for block in blocks]
    rounds: list[dict[str, Any]] = []
    nonempty_additions = 0
    cap_failure_reason: str | None = None
    closure_stopped = False

    while True:
        round_index = len(rounds)
        round_record, candidates = _audit_round(
            blocks,
            round_index,
            size,
            omega,
        )
        pending, orbit_records = _collect_orbit_additions(
            blocks,
            candidates,
            round_index,
            size,
            omega,
        )
        requested_dimension = sum(block.dimension for block in pending)
        round_record["requested_orbits"] = orbit_records
        round_record["requested_new_block_count"] = len(pending)
        round_record["requested_new_real_dimension"] = requested_dimension
        round_record["addition_applied"] = False
        if not pending:
            if candidates:
                raise RuntimeError(
                    "flagged external response clusters produced no new orbit"
                )
            round_record["terminal_reaudit"] = True
            rounds.append(round_record)
            closure_stopped = True
            break
        proposed_dimension = sum(block.dimension for block in blocks) + requested_dimension
        if nonempty_additions >= MAXIMUM_NONEMPTY_ADDITIONS:
            cap_failure_reason = (
                "mandatory terminal re-audit requested a fifth nonempty addition"
            )
            round_record["terminal_reaudit"] = True
            round_record["cap_failure_reason"] = cap_failure_reason
            rounds.append(round_record)
            break
        if proposed_dimension > MAXIMUM_REAL_COORDINATES:
            cap_failure_reason = (
                f"the next required addition would raise the real dimension to "
                f"{proposed_dimension}, above the cap of {MAXIMUM_REAL_COORDINATES}"
            )
            round_record["terminal_reaudit"] = False
            round_record["cap_failure_reason"] = cap_failure_reason
            rounds.append(round_record)
            break
        blocks.extend(pending)
        nonempty_additions += 1
        round_record["addition_applied"] = True
        round_record["terminal_reaudit"] = False
        round_record["post_addition_real_dimension"] = sum(
            block.dimension for block in blocks
        )
        rounds.append(round_record)

    terminal = rounds[-1]
    materially_forced_condition = terminal[
        "maximum_materially_forced_near_condition_number"
    ]
    coefficient_gates = {
        "closure_stops_within_cap": {
            "value": {
                "stopped": closure_stopped,
                "nonempty_additions": nonempty_additions,
                "final_real_dimension": sum(block.dimension for block in blocks),
                "cap_failure_reason": cap_failure_reason,
            },
            "threshold": {
                "maximum_nonempty_additions": MAXIMUM_NONEMPTY_ADDITIONS,
                "maximum_real_dimension": MAXIMUM_REAL_COORDINATES,
            },
            "passed": closure_stopped and cap_failure_reason is None,
        },
        "no_numerically_singular_external_block": {
            "value": terminal["numerically_singular_external_block_count"],
            "threshold": 0,
            "passed": terminal["numerically_singular_external_block_count"] == 0,
        },
        "materially_forced_near_condition": {
            "value": materially_forced_condition,
            "threshold": MATERIAL_NEAR_CONDITION_CEILING,
            "passed": materially_forced_condition
            <= MATERIAL_NEAR_CONDITION_CEILING,
        },
        "remaining_external_condition": {
            "value": terminal["maximum_condition_number"],
            "threshold": PRACTICAL_CONDITION_CEILING,
            "passed": terminal["maximum_condition_number"]
            <= PRACTICAL_CONDITION_CEILING,
        },
        "schur_projector_symmetry_fixed_leaf_residual": {
            "value": terminal["maximum_structural_residual"],
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": terminal["maximum_structural_residual"]
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
    }
    coefficient_passed = all(
        gate["passed"] for gate in coefficient_gates.values()
    )
    normal_screen = _normal_dominance_screen(
        blocks,
        size,
        omega,
        coefficient_passed,
    )
    validity_gates = {
        "registered_initial_dimension": {
            "value": sum(record["dimension"] for record in initial_records),
            "threshold": 16,
            "passed": sum(record["dimension"] for record in initial_records) == 16,
        },
        "initial_c4_and_conjugacy_closure": {
            "value": max(
                initial_symmetry["maximum_c4_subspace_residual"],
                initial_symmetry["maximum_conjugacy_subspace_residual"],
            ),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": max(
                initial_symmetry["maximum_c4_subspace_residual"],
                initial_symmetry["maximum_conjugacy_subspace_residual"],
            )
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
        "complete_pair_enumeration": {
            "value": all(record["pair_enumeration_complete"] for record in rounds),
            "threshold": True,
            "passed": all(record["pair_enumeration_complete"] for record in rounds),
        },
        "finite_structural_audit": {
            "value": max(
                record["maximum_structural_residual"] for record in rounds
            ),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": max(
                record["maximum_structural_residual"] for record in rounds
            )
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
        "finite_homological_solve_residual": {
            "value": max(
                record["maximum_solve_relative_residual"] for record in rounds
            ),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": max(
                record["maximum_solve_relative_residual"] for record in rounds
            )
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
    }
    study_validity = all(gate["passed"] for gate in validity_gates.values())
    both_passed = coefficient_passed and normal_screen["passed"]
    if both_passed:
        decision = (
            "The finite-grid quadratic SSM screening passed; Q006 may construct "
            "the dense full-2D candidate without promoting this to an existence claim."
        )
        next_change = "Construct the Q006 full-2D fixed-leaf dense quadratic chart."
    elif coefficient_passed:
        decision = (
            "Record a coefficient-solvable finite-grid candidate, but do not start "
            "Q006 because linear normal-dominance prequalification failed."
        )
        next_change = (
            "Resolve the finite-grid normal-dominance obstruction without adding "
            "normal-gap modes inside the sealed Q006r closure rule."
        )
    else:
        decision = (
            "Reject this capped mode-added coefficient candidate and do not start Q006."
        )
        next_change = (
            "Analyze the terminal singular/conditioning or coordinate-cap witness "
            "before proposing a new full-2D reduced set."
        )
    witness = orthogonal_acoustic_resonance_witness(size, omega)
    internalized_pair = next(
        record
        for record in rounds[0]["pair_table"]
        if record["left_block"] == "i001" and record["right_block"] == "i005"
    )
    return {
        "question": (
            "Does the sealed N=17 mode-added set close every quadratic external "
            "Schur block and pass finite-grid linear normal-dominance screening?"
        ),
        "hypothesis": (
            "Internalizing the diagonal-shear resonance orbit permits capped "
            "resonant/near-resonant closure and leaves a normally dominant "
            "finite-grid selected spectrum."
        ),
        "registered_scope": {
            "grid": [size, size],
            "omega": omega,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "initial_real_dimension": 16,
            "maximum_nonempty_additions": MAXIMUM_NONEMPTY_ADDITIONS,
            "maximum_real_dimension": MAXIMUM_REAL_COORDINATES,
            "cluster_relative_tolerance": CLUSTER_RELATIVE_TOLERANCE,
            "near_singular_relative_threshold": (
                NEAR_SINGULAR_RELATIVE_THRESHOLD
            ),
            "forcing_sensitivity_threshold": FORCING_SENSITIVITY_THRESHOLD,
            "response_energy_threshold": RESPONSE_ENERGY_TOLERANCE,
            "response_energy_tie_tolerance": RESPONSE_ENERGY_TIE_TOLERANCE,
            "normal_gap_modes_are_not_added": True,
        },
        "initial_mode_order": initial_records,
        "initial_symmetry_maps": initial_symmetry,
        "diagonal_resonance_witness": witness,
        "diagonal_resonance_internalization": {
            "input_blocks": ["i001", "i005"],
            "output_wave_index": internalized_pair["output_wave_index"],
            "unprojected_status": witness["homological"]["status"],
            "external_projected_status": internalized_pair["status"],
            "external_dimension": internalized_pair["external_dimension"],
            "external_smallest_singular_value": internalized_pair[
                "singular_values"
            ][-1],
            "external_condition_number": internalized_pair["condition_number"],
            "interpretation": (
                "The exact diagonal-shear resonance is internal, while the "
                "remaining external block is nonsingular."
            ),
        },
        "rounds": rounds,
        "terminal_selected_blocks": [_block_record(block) for block in blocks],
        "terminal_summary": {
            "closure_stopped": closure_stopped,
            "cap_failure_reason": cap_failure_reason,
            "nonempty_additions": nonempty_additions,
            "round_count": len(rounds),
            "final_block_count": len(blocks),
            "final_real_dimension": sum(block.dimension for block in blocks),
            "terminal_pair_count": terminal["enumerated_pair_count"],
            "terminal_numerically_singular_external_block_count": terminal[
                "numerically_singular_external_block_count"
            ],
            "terminal_near_singular_external_block_count": terminal[
                "near_singular_external_block_count"
            ],
            "terminal_condition_quantiles": terminal["condition_quantiles"],
            "terminal_worst_condition_pair": terminal["worst_condition_pair"],
            "terminal_maximum_condition_number": terminal[
                "maximum_condition_number"
            ],
            "terminal_maximum_structural_residual": terminal[
                "maximum_structural_residual"
            ],
        },
        "coefficient_solvability": {
            "gates": coefficient_gates,
            "passed": coefficient_passed,
        },
        "linear_normal_dominance_prequalification": normal_screen,
        "validity_gates": validity_gates,
        "study_validity": "passed" if study_validity else "failed",
        "hypothesis_outcome": "accepted" if both_passed else "rejected",
        "decision": decision,
        "limitations": [
            (
                "This is a quadratic finite-grid spectral audit, not an invariant-"
                "manifold existence or uniqueness theorem."
            ),
            (
                "Passing the modulus and local-projector screens would not prove "
                "nonlinear normal attraction."
            ),
            (
                "The audit is fixed at N=17 and omega=1.2 and makes no grid-uniform "
                "conditioning claim."
            ),
        ],
        "next_change": next_change,
    }
