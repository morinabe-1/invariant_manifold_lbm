"""Sealed Q007e equilibrium Riesz/Stein metric prequalification audit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.linalg import solve_discrete_lyapunov
from scipy.sparse.linalg import LinearOperator, svds

from .checkerboard_filter import filter_multiplier
from .cluster_complete import build_first_shell_cluster_blocks
from .cubic_chart import _array_hash
from .cubic_continuation import (
    _all_numeric_values_finite,
    _strict_json_serializable,
)
from .full2d_chart import WAVE_ORDER
from .mode_closure import _build_sector
from .nonresonance import wave_vector_from_index
from .normal_cocycle import (
    NORMAL_SVD_SEED as Q007D_NORMAL_SVD_SEED,
)
from .normal_cocycle import (
    FixedLeafProjector,
    _coefficient_reproduction,
    _trajectory_record,
)
from .quartic_chart import Full2DQuarticModel, build_full2d_quartic_model

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]
WaveIndex = tuple[int, int]

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_COMPLEX_DIMENSION = 24
FIXED_LEAF_DIMENSION = 2598
EXPECTED_SELECTED_WAVE_COUNT = 8
HORIZONS = (1, 10)
TRANSFORM_SEED = 20260906
TRANSFORM_DIRECTION_COUNT = 16
ADAPTED_SVD_SEED = 20260907
SVD_TOLERANCE = 1.0e-12
SVD_MAXIMUM_ITERATIONS = 5000

REGISTERED_Q007D_EQUILIBRIUM_GAMMA = {
    1: 2.4223625220259515,
    10: 2.592215401693412,
}
REGISTERED_MINIMUM_SELECTED_MODULUS = 0.9837709569927497
REGISTERED_MAXIMUM_EXCLUDED_MODULUS = 0.9817098358325437

MAXIMUM_Q007D_REPRODUCTION_RELATIVE_ERROR = 1.0e-10
MAXIMUM_SPLIT_RESIDUAL = 1.0e-10
MAXIMUM_STEIN_RESIDUAL = 1.0e-10
MAXIMUM_HERMITIAN_RESIDUAL = 1.0e-12
MINIMUM_STEIN_EIGENVALUE = 1.0e-12
MAXIMUM_CONDITION_NUMBER = 1.0e10
MAXIMUM_CONJUGACY_RESIDUAL = 1.0e-10
MAXIMUM_TRANSFORM_ROUNDTRIP_ERROR = 1.0e-10
MAXIMUM_TRANSFORM_IMAGINARY_LEAKAGE = 1.0e-10
MAXIMUM_BLOCKWISE_SVD_ERROR = 1.0e-8
MAXIMUM_TRIPLET_RESIDUAL = 1.0e-8
MAXIMUM_TWO_START_DISAGREEMENT = 1.0e-6


def _relative_norm(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).eps)
    )


def _relative_scalar_error(observed: float, registered: float) -> float:
    return abs(float(observed) - float(registered)) / max(
        abs(float(registered)),
        np.finfo(float).eps,
    )


def _complex_columns(
    value: npt.ArrayLike,
    dimension: int,
    *,
    label: str,
) -> tuple[ComplexArray, bool]:
    array = np.asarray(value, dtype=np.complex128)
    if array.shape == (dimension,):
        return array[:, None], True
    if array.ndim == 2 and array.shape[0] == dimension:
        return array, False
    raise ValueError(f"{label} must have shape ({dimension},) or ({dimension}, m)")


def _restore_complex_columns(
    value: ComplexArray,
    was_vector: bool,
) -> ComplexArray:
    return np.asarray(value[:, 0] if was_vector else value, dtype=np.complex128)


def _wave_indices(size: int = SIZE) -> tuple[WaveIndex, ...]:
    half = size // 2
    return tuple(
        (ix, iy)
        for ix in range(-half, half + 1)
        for iy in range(-half, half + 1)
    )


@dataclass(frozen=True)
class _RawWaveSplit:
    wave_index: WaveIndex
    active_basis: ComplexArray
    active_matrix: ComplexArray
    selected_basis: ComplexArray
    external_basis: ComplexArray
    riesz_basis: ComplexArray
    riesz_inverse: ComplexArray
    riesz_matrix: ComplexArray
    selected_dimension: int
    filter_multiplier: float
    structural_residual: float
    fixed_leaf_residual: float
    riesz_inverse_residual: float
    block_diagonalization_residual: float

    @property
    def active_dimension(self) -> int:
        return int(self.active_matrix.shape[0])

    @property
    def external_dimension(self) -> int:
        return self.active_dimension - self.selected_dimension

    @property
    def selected_matrix(self) -> ComplexArray:
        stop = self.selected_dimension
        return np.asarray(self.riesz_matrix[:stop, :stop], dtype=np.complex128)

    @property
    def external_matrix(self) -> ComplexArray:
        start = self.selected_dimension
        return np.asarray(self.riesz_matrix[start:, start:], dtype=np.complex128)


@dataclass(frozen=True)
class AdaptedWaveBlock:
    """One whitened Fourier block of the registered adapted norm."""

    wave_index: WaveIndex
    active_basis: ComplexArray
    active_matrix: ComplexArray
    metric: ComplexArray
    whitening: ComplexArray
    whitening_inverse: ComplexArray
    whitened_matrix: ComplexArray
    tangent_basis: ComplexArray
    normal_basis: ComplexArray
    tangent_matrix: ComplexArray
    normal_matrix: ComplexArray
    selected_dimension: int
    external_dimension: int
    record: dict[str, Any]

    @property
    def active_dimension(self) -> int:
        return int(self.active_matrix.shape[0])

    def normal_project(self, value: npt.ArrayLike) -> ComplexArray:
        array = np.asarray(value, dtype=np.complex128)
        if self.selected_dimension == 0:
            return array
        return np.asarray(
            self.normal_basis @ (self.normal_basis.conj().T @ array),
            dtype=np.complex128,
        )


@dataclass(frozen=True)
class AdaptedFourierMetric:
    """Block-Fourier whitening transform on the global fixed leaf."""

    size: int
    blocks: tuple[AdaptedWaveBlock, ...]
    slices: tuple[slice, ...]

    @property
    def dimension(self) -> int:
        return sum(block.active_dimension for block in self.blocks)

    def forward(self, state: npt.ArrayLike) -> ComplexArray:
        physical_dimension = self.size * self.size * 9
        value, was_vector = _complex_columns(
            state,
            physical_dimension,
            label="physical state",
        )
        spectrum = np.fft.fft2(
            value.reshape(self.size, self.size, 9, value.shape[1]),
            axes=(0, 1),
            norm="ortho",
        )
        transformed = np.empty(
            (self.dimension, value.shape[1]),
            dtype=np.complex128,
        )
        for block, target in zip(self.blocks, self.slices, strict=True):
            ix, iy = block.wave_index
            population = spectrum[iy % self.size, ix % self.size]
            active = block.active_basis.conj().T @ population
            transformed[target] = block.whitening @ active
        return _restore_complex_columns(transformed, was_vector)

    def inverse(self, coordinates: npt.ArrayLike) -> ComplexArray:
        value, was_vector = _complex_columns(
            coordinates,
            self.dimension,
            label="adapted coordinates",
        )
        spectrum = np.zeros(
            (self.size, self.size, 9, value.shape[1]),
            dtype=np.complex128,
        )
        for block, source in zip(self.blocks, self.slices, strict=True):
            ix, iy = block.wave_index
            active = block.whitening_inverse @ value[source]
            spectrum[iy % self.size, ix % self.size] = block.active_basis @ active
        physical = np.asarray(
            np.fft.ifft2(spectrum, axes=(0, 1), norm="ortho").reshape(
                self.size * self.size * 9,
                value.shape[1],
            ),
            dtype=np.complex128,
        )
        return _restore_complex_columns(physical, was_vector)

    def forward_adjoint(self, coordinates: npt.ArrayLike) -> ComplexArray:
        """Apply the Euclidean adjoint of ``forward``."""

        value, was_vector = _complex_columns(
            coordinates,
            self.dimension,
            label="adapted coordinates",
        )
        spectrum = np.zeros(
            (self.size, self.size, 9, value.shape[1]),
            dtype=np.complex128,
        )
        for block, source in zip(self.blocks, self.slices, strict=True):
            ix, iy = block.wave_index
            active = block.whitening.conj().T @ value[source]
            spectrum[iy % self.size, ix % self.size] = block.active_basis @ active
        physical = np.asarray(
            np.fft.ifft2(spectrum, axes=(0, 1), norm="ortho").reshape(
                self.size * self.size * 9,
                value.shape[1],
            ),
            dtype=np.complex128,
        )
        return _restore_complex_columns(physical, was_vector)

    def inverse_adjoint(self, state: npt.ArrayLike) -> ComplexArray:
        """Apply the Euclidean adjoint of ``inverse``."""

        physical_dimension = self.size * self.size * 9
        value, was_vector = _complex_columns(
            state,
            physical_dimension,
            label="physical state",
        )
        spectrum = np.fft.fft2(
            value.reshape(self.size, self.size, 9, value.shape[1]),
            axes=(0, 1),
            norm="ortho",
        )
        transformed = np.empty(
            (self.dimension, value.shape[1]),
            dtype=np.complex128,
        )
        for block, target in zip(self.blocks, self.slices, strict=True):
            ix, iy = block.wave_index
            population = spectrum[iy % self.size, ix % self.size]
            active = block.active_basis.conj().T @ population
            transformed[target] = block.whitening_inverse.conj().T @ active
        return _restore_complex_columns(transformed, was_vector)


def _raw_wave_splits() -> tuple[_RawWaveSplit, ...]:
    selected_blocks = build_first_shell_cluster_blocks(SIZE, OMEGA)
    splits = []
    for wave_index in _wave_indices():
        sector = _build_sector(wave_index, selected_blocks, SIZE, OMEGA)
        multiplier = filter_multiplier(
            *wave_vector_from_index(wave_index, SIZE),
            ETA,
        )
        active_matrix = multiplier * sector.active_matrix
        riesz_basis = np.column_stack(
            (sector.selected_basis, sector.external_basis)
        )
        riesz_inverse = np.linalg.inv(riesz_basis)
        riesz_matrix = riesz_inverse @ active_matrix @ riesz_basis
        selected_dimension = sector.selected_dimension
        off_diagonal = np.zeros_like(riesz_matrix)
        if selected_dimension:
            off_diagonal[:selected_dimension, selected_dimension:] = riesz_matrix[
                :selected_dimension, selected_dimension:
            ]
            off_diagonal[selected_dimension:, :selected_dimension] = riesz_matrix[
                selected_dimension:, :selected_dimension
            ]
        splits.append(
            _RawWaveSplit(
                wave_index=wave_index,
                active_basis=np.asarray(sector.active_basis, dtype=np.complex128),
                active_matrix=np.asarray(active_matrix, dtype=np.complex128),
                selected_basis=np.asarray(
                    sector.selected_basis,
                    dtype=np.complex128,
                ),
                external_basis=np.asarray(
                    sector.external_basis,
                    dtype=np.complex128,
                ),
                riesz_basis=np.asarray(riesz_basis, dtype=np.complex128),
                riesz_inverse=np.asarray(riesz_inverse, dtype=np.complex128),
                riesz_matrix=np.asarray(riesz_matrix, dtype=np.complex128),
                selected_dimension=selected_dimension,
                filter_multiplier=float(multiplier),
                structural_residual=float(sector.maximum_structural_residual),
                fixed_leaf_residual=float(sector.fixed_leaf_residual),
                riesz_inverse_residual=float(
                    np.linalg.norm(
                        riesz_inverse @ riesz_basis
                        - np.eye(riesz_basis.shape[0])
                    )
                ),
                block_diagonalization_residual=_relative_norm(
                    off_diagonal,
                    riesz_matrix,
                ),
            )
        )
    return tuple(splits)


def _spectral_gap(splits: tuple[_RawWaveSplit, ...]) -> dict[str, Any]:
    selected_records = [
        (abs(value), split.wave_index, complex(value))
        for split in splits
        for value in np.linalg.eigvals(split.selected_matrix)
    ]
    external_records = [
        (abs(value), split.wave_index, complex(value))
        for split in splits
        for value in np.linalg.eigvals(split.external_matrix)
    ]
    minimum_selected = min(selected_records, key=lambda item: item[0])
    maximum_external = max(external_records, key=lambda item: item[0])
    rate = float(np.sqrt(minimum_selected[0] * maximum_external[0]))
    return {
        "minimum_selected_modulus": float(minimum_selected[0]),
        "minimum_selected_wave_index": list(minimum_selected[1]),
        "minimum_selected_eigenvalue": {
            "real": float(minimum_selected[2].real),
            "imag": float(minimum_selected[2].imag),
        },
        "maximum_excluded_modulus": float(maximum_external[0]),
        "maximum_excluded_wave_index": list(maximum_external[1]),
        "maximum_excluded_eigenvalue": {
            "real": float(maximum_external[2].real),
            "imag": float(maximum_external[2].imag),
        },
        "normal_dominance_gap": float(
            minimum_selected[0] - maximum_external[0]
        ),
        "registered_rate": rate,
        "lower_rate_margin": float(rate - maximum_external[0]),
        "upper_rate_margin": float(minimum_selected[0] - rate),
        "minimum_selected_reproduction_relative_error": _relative_scalar_error(
            minimum_selected[0],
            REGISTERED_MINIMUM_SELECTED_MODULUS,
        ),
        "maximum_excluded_reproduction_relative_error": _relative_scalar_error(
            maximum_external[0],
            REGISTERED_MAXIMUM_EXCLUDED_MODULUS,
        ),
    }


def _stein_metric(
    matrix: ComplexArray,
    *,
    tangent: bool,
    rate: float,
) -> tuple[ComplexArray, dict[str, float]]:
    scaled = (
        rate * np.linalg.inv(matrix)
        if tangent
        else matrix / rate
    )
    raw = np.asarray(
        solve_discrete_lyapunov(
            scaled.conj().T,
            np.eye(matrix.shape[0]),
        ),
        dtype=np.complex128,
    )
    hermitian_residual = _relative_norm(raw - raw.conj().T, raw)
    metric = np.asarray(0.5 * (raw + raw.conj().T), dtype=np.complex128)
    eigenvalues = np.linalg.eigvalsh(metric)
    residual = _relative_norm(
        scaled.conj().T @ metric @ scaled
        - metric
        + np.eye(matrix.shape[0]),
        np.eye(matrix.shape[0]),
    )
    return metric, {
        "relative_residual": residual,
        "hermitian_relative_residual": hermitian_residual,
        "minimum_eigenvalue": float(eigenvalues[0]),
        "maximum_eigenvalue": float(eigenvalues[-1]),
        "condition_number": float(eigenvalues[-1] / eigenvalues[0]),
        "scaled_spectral_radius": float(
            np.max(np.abs(np.linalg.eigvals(scaled)))
        ),
    }


def _adapted_wave_block(
    split: _RawWaveSplit,
    rate: float,
) -> AdaptedWaveBlock:
    selected_dimension = split.selected_dimension
    active_dimension = split.active_dimension
    block_metric = np.zeros(
        (active_dimension, active_dimension),
        dtype=np.complex128,
    )
    selected_stein: dict[str, float] | None = None
    if selected_dimension:
        selected_metric, selected_stein = _stein_metric(
            split.selected_matrix,
            tangent=True,
            rate=rate,
        )
        block_metric[:selected_dimension, :selected_dimension] = selected_metric
    external_metric, external_stein = _stein_metric(
        split.external_matrix,
        tangent=False,
        rate=rate,
    )
    block_metric[selected_dimension:, selected_dimension:] = external_metric

    metric = (
        split.riesz_inverse.conj().T
        @ block_metric
        @ split.riesz_inverse
    )
    metric = np.asarray(0.5 * (metric + metric.conj().T), dtype=np.complex128)
    metric_eigenvalues = np.linalg.eigvalsh(metric)
    lower_cholesky = np.linalg.cholesky(metric)
    whitening = np.asarray(lower_cholesky.conj().T, dtype=np.complex128)
    whitening_inverse = np.linalg.inv(whitening)
    whitened_matrix = whitening @ split.active_matrix @ whitening_inverse

    if selected_dimension:
        tangent_basis = np.linalg.qr(
            whitening @ split.selected_basis,
            mode="reduced",
        )[0]
        normal_basis = np.linalg.qr(
            whitening @ split.external_basis,
            mode="reduced",
        )[0]
        tangent_matrix = (
            tangent_basis.conj().T @ whitened_matrix @ tangent_basis
        )
        normal_matrix = normal_basis.conj().T @ whitened_matrix @ normal_basis
    else:
        tangent_basis = np.empty(
            (active_dimension, 0),
            dtype=np.complex128,
        )
        normal_basis = np.eye(active_dimension, dtype=np.complex128)
        tangent_matrix = np.empty((0, 0), dtype=np.complex128)
        normal_matrix = whitened_matrix.copy()

    tangent_normal_orthogonality = float(
        np.linalg.norm(tangent_basis.conj().T @ normal_basis)
    )
    projector_completeness = float(
        np.linalg.norm(
            tangent_basis @ tangent_basis.conj().T
            + normal_basis @ normal_basis.conj().T
            - np.eye(active_dimension)
        )
    )
    tangent_leakage = 0.0
    if selected_dimension:
        tangent_leakage = _relative_norm(
            normal_basis.conj().T @ whitened_matrix @ tangent_basis,
            whitened_matrix @ tangent_basis,
        )
    normal_leakage = _relative_norm(
        tangent_basis.conj().T @ whitened_matrix @ normal_basis,
        whitened_matrix @ normal_basis,
    ) if selected_dimension else 0.0

    one_normal = np.linalg.svd(normal_matrix, compute_uv=False)
    ten_normal = np.linalg.svd(
        np.linalg.matrix_power(normal_matrix, 10),
        compute_uv=False,
    )
    if selected_dimension:
        one_tangent = np.linalg.svd(tangent_matrix, compute_uv=False)
        ten_tangent = np.linalg.svd(
            np.linalg.matrix_power(tangent_matrix, 10),
            compute_uv=False,
        )
    else:
        one_tangent = np.empty(0)
        ten_tangent = np.empty(0)

    record: dict[str, Any] = {
        "wave_index": list(split.wave_index),
        "filter_multiplier": split.filter_multiplier,
        "active_dimension": active_dimension,
        "selected_dimension": selected_dimension,
        "external_dimension": split.external_dimension,
        "selected_spectral_radius": (
            None
            if selected_dimension == 0
            else float(np.max(np.abs(np.linalg.eigvals(split.selected_matrix))))
        ),
        "external_spectral_radius": float(
            np.max(np.abs(np.linalg.eigvals(split.external_matrix)))
        ),
        "riesz_basis_condition_number": float(np.linalg.cond(split.riesz_basis)),
        "riesz_inverse_residual": split.riesz_inverse_residual,
        "block_diagonalization_relative_residual": (
            split.block_diagonalization_residual
        ),
        "sector_structural_residual": split.structural_residual,
        "fixed_leaf_residual": split.fixed_leaf_residual,
        "selected_stein": selected_stein,
        "external_stein": external_stein,
        "metric_minimum_eigenvalue": float(metric_eigenvalues[0]),
        "metric_maximum_eigenvalue": float(metric_eigenvalues[-1]),
        "metric_condition_number": float(
            metric_eigenvalues[-1] / metric_eigenvalues[0]
        ),
        "whitening_condition_number": float(np.linalg.cond(whitening)),
        "whitening_inverse_residual": float(
            np.linalg.norm(
                whitening @ whitening_inverse - np.eye(active_dimension)
            )
        ),
        "tangent_normal_orthogonality_residual": tangent_normal_orthogonality,
        "projector_completeness_residual": projector_completeness,
        "adapted_tangent_leakage": tangent_leakage,
        "adapted_normal_leakage": normal_leakage,
        "normal_singular_values": {
            "horizon_1_maximum": float(one_normal[0]),
            "horizon_10_maximum": float(ten_normal[0]),
        },
        "tangent_singular_values": {
            "horizon_1_minimum": (
                None if selected_dimension == 0 else float(one_tangent[-1])
            ),
            "horizon_10_minimum": (
                None if selected_dimension == 0 else float(ten_tangent[-1])
            ),
        },
    }
    return AdaptedWaveBlock(
        wave_index=split.wave_index,
        active_basis=split.active_basis,
        active_matrix=split.active_matrix,
        metric=metric,
        whitening=whitening,
        whitening_inverse=np.asarray(whitening_inverse, dtype=np.complex128),
        whitened_matrix=np.asarray(whitened_matrix, dtype=np.complex128),
        tangent_basis=np.asarray(tangent_basis, dtype=np.complex128),
        normal_basis=np.asarray(normal_basis, dtype=np.complex128),
        tangent_matrix=np.asarray(tangent_matrix, dtype=np.complex128),
        normal_matrix=np.asarray(normal_matrix, dtype=np.complex128),
        selected_dimension=selected_dimension,
        external_dimension=split.external_dimension,
        record=record,
    )


def build_adapted_fourier_metric() -> tuple[AdaptedFourierMetric, dict[str, Any]]:
    """Construct the preregistered Q007e block-Riesz Stein metric."""

    splits = _raw_wave_splits()
    spectral_gap = _spectral_gap(splits)
    rate = spectral_gap["registered_rate"]
    blocks = tuple(_adapted_wave_block(split, rate) for split in splits)
    starts = np.cumsum(
        [0, *(block.active_dimension for block in blocks)],
        dtype=np.int64,
    )
    slices = tuple(
        slice(int(starts[index]), int(starts[index + 1]))
        for index in range(len(blocks))
    )
    metric = AdaptedFourierMetric(size=SIZE, blocks=blocks, slices=slices)

    selected_wave_records = [
        block for block in blocks if block.selected_dimension > 0
    ]
    selected_wave_set = {block.wave_index for block in selected_wave_records}
    expected_wave_set = {tuple(value) for value in WAVE_ORDER}
    missing_waves = sorted(expected_wave_set - selected_wave_set)
    unexpected_waves = sorted(selected_wave_set - expected_wave_set)

    all_metric_eigenvalues = np.concatenate(
        [np.linalg.eigvalsh(block.metric) for block in blocks]
    )
    all_whitening_singular_values = np.concatenate(
        [np.linalg.svd(block.whitening, compute_uv=False) for block in blocks]
    )
    all_riesz_singular_values = np.concatenate(
        [
            np.linalg.svd(split.riesz_basis, compute_uv=False)
            for split in splits
        ]
    )
    block_records = [block.record for block in blocks]
    selected_stein_records = [
        record["selected_stein"]
        for record in block_records
        if record["selected_stein"] is not None
    ]
    external_stein_records = [record["external_stein"] for record in block_records]
    all_stein_records = [*selected_stein_records, *external_stein_records]
    metric_sha256 = _array_hash(
        np.concatenate([block.metric.ravel() for block in blocks])
    )
    whitening_sha256 = _array_hash(
        np.concatenate([block.whitening.ravel() for block in blocks])
    )
    summary = {
        "wave_block_count": len(blocks),
        "fixed_leaf_dimension": metric.dimension,
        "selected_complex_dimension": sum(
            block.selected_dimension for block in blocks
        ),
        "external_complex_dimension": sum(
            block.external_dimension for block in blocks
        ),
        "selected_wave_count": len(selected_wave_records),
        "metric_sha256": metric_sha256,
        "whitening_sha256": whitening_sha256,
        "missing_selected_waves": [list(value) for value in missing_waves],
        "unexpected_selected_waves": [list(value) for value in unexpected_waves],
        "maximum_sector_structural_residual": max(
            record["sector_structural_residual"] for record in block_records
        ),
        "maximum_fixed_leaf_residual": max(
            record["fixed_leaf_residual"] for record in block_records
        ),
        "maximum_riesz_inverse_residual": max(
            record["riesz_inverse_residual"] for record in block_records
        ),
        "maximum_block_diagonalization_relative_residual": max(
            record["block_diagonalization_relative_residual"]
            for record in block_records
        ),
        "maximum_tangent_normal_orthogonality_residual": max(
            record["tangent_normal_orthogonality_residual"]
            for record in block_records
        ),
        "maximum_projector_completeness_residual": max(
            record["projector_completeness_residual"]
            for record in block_records
        ),
        "maximum_adapted_tangent_leakage": max(
            record["adapted_tangent_leakage"] for record in block_records
        ),
        "maximum_adapted_normal_leakage": max(
            record["adapted_normal_leakage"] for record in block_records
        ),
        "maximum_stein_relative_residual": max(
            record["relative_residual"] for record in all_stein_records
        ),
        "maximum_stein_hermitian_relative_residual": max(
            record["hermitian_relative_residual"] for record in all_stein_records
        ),
        "minimum_stein_eigenvalue": min(
            record["minimum_eigenvalue"] for record in all_stein_records
        ),
        "maximum_local_stein_condition_number": max(
            record["condition_number"] for record in all_stein_records
        ),
        "maximum_local_riesz_basis_condition_number": max(
            record["riesz_basis_condition_number"] for record in block_records
        ),
        "maximum_local_metric_condition_number": max(
            record["metric_condition_number"] for record in block_records
        ),
        "maximum_local_whitening_condition_number": max(
            record["whitening_condition_number"] for record in block_records
        ),
        "global_riesz_basis_condition_number": float(
            np.max(all_riesz_singular_values)
            / np.min(all_riesz_singular_values)
        ),
        "global_metric_condition_number": float(
            np.max(all_metric_eigenvalues) / np.min(all_metric_eigenvalues)
        ),
        "global_whitening_condition_number": float(
            np.max(all_whitening_singular_values)
            / np.min(all_whitening_singular_values)
        ),
    }
    return metric, {
        "spectral_gap": spectral_gap,
        "block_records": block_records,
        "summary": summary,
    }


def _conjugacy_audit(metric: AdaptedFourierMetric) -> dict[str, Any]:
    lookup = {block.wave_index: block for block in metric.blocks}
    records = []
    visited: set[WaveIndex] = set()
    for block in metric.blocks:
        wave = block.wave_index
        if wave in visited:
            continue
        negative = (-wave[0], -wave[1])
        partner = lookup[negative]
        residual = _relative_norm(
            partner.metric - np.conjugate(block.metric),
            block.metric,
        )
        records.append(
            {
                "wave_index": list(wave),
                "negative_wave_index": list(negative),
                "metric_conjugacy_relative_residual": residual,
            }
        )
        visited.add(wave)
        visited.add(negative)
    return {
        "pair_count": len(records),
        "pair_records": records,
        "maximum_metric_conjugacy_relative_residual": max(
            record["metric_conjugacy_relative_residual"] for record in records
        ),
    }


def _transform_roundtrip_audit(
    metric: AdaptedFourierMetric,
) -> dict[str, Any]:
    leaf = FixedLeafProjector.for_square_grid(metric.size)
    rng = np.random.default_rng(TRANSFORM_SEED)
    raw = rng.normal(
        size=(TRANSFORM_DIRECTION_COUNT, metric.size * metric.size * 9)
    )
    directions = leaf.project(raw.T).T
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    records = []
    for direction_index, direction in enumerate(directions):
        transformed = metric.forward(direction)
        reconstructed = metric.inverse(transformed)
        records.append(
            {
                "direction_index": direction_index,
                "roundtrip_relative_error": _relative_norm(
                    reconstructed.real - direction,
                    direction,
                ),
                "imaginary_leakage_relative_norm": _relative_norm(
                    reconstructed.imag,
                    direction,
                ),
                "adapted_norm": float(np.linalg.norm(transformed)),
            }
        )
    return {
        "seed": TRANSFORM_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "direction_records": records,
        "summary": {
            "maximum_roundtrip_relative_error": max(
                record["roundtrip_relative_error"] for record in records
            ),
            "maximum_imaginary_leakage_relative_norm": max(
                record["imaginary_leakage_relative_norm"] for record in records
            ),
            "minimum_adapted_norm": min(
                record["adapted_norm"] for record in records
            ),
            "maximum_adapted_norm": max(
                record["adapted_norm"] for record in records
            ),
        },
    }


def _normal_operator(
    metric: AdaptedFourierMetric,
    horizon: int,
) -> LinearOperator:
    def matvec(value: npt.ArrayLike) -> ComplexArray:
        array = np.asarray(value, dtype=np.complex128)
        result = np.empty_like(array)
        for block, block_slice in zip(metric.blocks, metric.slices, strict=True):
            current = block.normal_project(array[block_slice])
            for _ in range(horizon):
                current = block.normal_project(block.whitened_matrix @ current)
            result[block_slice] = current
        return result

    def rmatvec(value: npt.ArrayLike) -> ComplexArray:
        array = np.asarray(value, dtype=np.complex128)
        result = np.empty_like(array)
        for block, block_slice in zip(metric.blocks, metric.slices, strict=True):
            current = block.normal_project(array[block_slice])
            for _ in range(horizon):
                current = block.normal_project(
                    block.whitened_matrix.conj().T @ current
                )
            result[block_slice] = current
        return result

    return LinearOperator(
        shape=(metric.dimension, metric.dimension),
        matvec=matvec,
        rmatvec=rmatvec,
        dtype=np.dtype(np.complex128),
    )


def _largest_singular_triplet(
    operator: LinearOperator,
    start: ComplexArray,
) -> dict[str, Any]:
    u, singular_values, vh = svds(
        operator,
        k=1,
        which="LM",
        tol=SVD_TOLERANCE,
        maxiter=SVD_MAXIMUM_ITERATIONS,
        v0=start,
        solver="arpack",
        return_singular_vectors=True,
    )
    singular_value = float(singular_values[0])
    left = np.asarray(u[:, 0], dtype=np.complex128)
    # ``svds`` returns the row of V^H; the right singular vector is its
    # conjugate transpose.  The distinction is essential for complex blocks.
    right = np.asarray(vh[0].conj(), dtype=np.complex128)
    right_residual = _relative_norm(
        operator.matvec(right) - singular_value * left,
        singular_value * left,
    )
    left_residual = _relative_norm(
        operator.rmatvec(left) - singular_value * right,
        singular_value * right,
    )
    return {
        "singular_value": singular_value,
        "right_triplet_relative_residual": right_residual,
        "left_triplet_relative_residual": left_residual,
        "maximum_triplet_relative_residual": max(right_residual, left_residual),
    }


def _adapted_svd_audit(metric: AdaptedFourierMetric) -> dict[str, Any]:
    rng = np.random.default_rng(ADAPTED_SVD_SEED)
    primary = rng.normal(size=metric.dimension) + 1j * rng.normal(
        size=metric.dimension
    )
    primary = np.asarray(primary / np.linalg.norm(primary), dtype=np.complex128)
    secondary = np.roll(primary, 1)
    horizon_records = []
    for horizon in HORIZONS:
        operator = _normal_operator(metric, horizon)
        primary_record = _largest_singular_triplet(operator, primary)
        secondary_record = _largest_singular_triplet(operator, secondary)
        blockwise_normal = max(
            float(
                np.linalg.svd(
                    np.linalg.matrix_power(block.normal_matrix, horizon),
                    compute_uv=False,
                )[0]
            )
            for block in metric.blocks
        )
        blockwise_tangent = min(
            float(
                np.linalg.svd(
                    np.linalg.matrix_power(block.tangent_matrix, horizon),
                    compute_uv=False,
                )[-1]
            )
            for block in metric.blocks
            if block.selected_dimension
        )
        disagreement = abs(
            primary_record["singular_value"]
            - secondary_record["singular_value"]
        ) / max(
            primary_record["singular_value"],
            secondary_record["singular_value"],
            np.finfo(float).eps,
        )
        blockwise_error = _relative_scalar_error(
            primary_record["singular_value"],
            blockwise_normal,
        )
        gamma = primary_record["singular_value"] / blockwise_tangent
        horizon_records.append(
            {
                "horizon": horizon,
                "primary": primary_record,
                "secondary": secondary_record,
                "two_start_singular_value_relative_disagreement": float(
                    disagreement
                ),
                "blockwise_normal_maximum_singular_value": blockwise_normal,
                "blockwise_tangent_minimum_singular_value": blockwise_tangent,
                "matrix_free_vs_blockwise_normal_relative_error": blockwise_error,
                "gamma": float(gamma),
                "margin_1_minus_gamma": float(1.0 - gamma),
            }
        )
    return {
        "seed": ADAPTED_SVD_SEED,
        "primary_start_sha256": _array_hash(primary),
        "secondary_start_rule": "one-entry cyclic roll of primary start",
        "secondary_start_sha256": _array_hash(secondary),
        "horizon_records": horizon_records,
        "summary": {
            "maximum_matrix_free_vs_blockwise_normal_relative_error": max(
                record["matrix_free_vs_blockwise_normal_relative_error"]
                for record in horizon_records
            ),
            "maximum_triplet_relative_residual": max(
                max(
                    record["primary"]["maximum_triplet_relative_residual"],
                    record["secondary"]["maximum_triplet_relative_residual"],
                )
                for record in horizon_records
            ),
            "maximum_two_start_singular_value_relative_disagreement": max(
                record["two_start_singular_value_relative_disagreement"]
                for record in horizon_records
            ),
        },
    }


def _q007d_reproduction(
    model: Full2DQuarticModel | None = None,
) -> dict[str, Any]:
    if model is None:
        model = build_full2d_quartic_model()
    coefficient_reproduction = _coefficient_reproduction(model)
    leaf = FixedLeafProjector.for_square_grid(model.size)
    rng = np.random.default_rng(Q007D_NORMAL_SVD_SEED)
    primary_start = rng.normal(size=leaf.dimension)
    primary_start /= np.linalg.norm(primary_start)
    equilibrium = _trajectory_record(
        model,
        leaf,
        np.zeros(model.reduced_dimension),
        identifier="equilibrium",
        amplitude=0.0,
        direction_index=None,
        direction=None,
        primary_start=primary_start,
        secondary_start=np.roll(primary_start, 1),
    )
    observed = {
        1: equilibrium["one_step_diagnostic"]["gamma_1"],
        10: equilibrium["gamma_10"],
    }
    relative_errors = {
        horizon: _relative_scalar_error(
            observed[horizon],
            REGISTERED_Q007D_EQUILIBRIUM_GAMMA[horizon],
        )
        for horizon in HORIZONS
    }
    return {
        "coefficient_reproduction": coefficient_reproduction,
        "registered_equilibrium_gamma": REGISTERED_Q007D_EQUILIBRIUM_GAMMA,
        "observed_equilibrium_gamma": observed,
        "relative_errors": relative_errors,
        "maximum_relative_error": max(relative_errors.values()),
    }


def run_adapted_metric_audit(
    *,
    model: Full2DQuarticModel | None = None,
) -> dict[str, Any]:
    """Run the preregistered Q007e equilibrium adapted-metric audit."""

    upstream = _q007d_reproduction(model)
    metric, construction = build_adapted_fourier_metric()
    conjugacy = _conjugacy_audit(metric)
    roundtrip = _transform_roundtrip_audit(metric)
    svd_audit = _adapted_svd_audit(metric)
    construction_summary = construction["summary"]
    roundtrip_summary = roundtrip["summary"]
    svd_summary = svd_audit["summary"]
    spectral_gap = construction["spectral_gap"]

    serializable_probe = {
        "upstream": upstream,
        "construction": construction,
        "conjugacy": conjugacy,
        "roundtrip": roundtrip,
        "svd_audit": svd_audit,
    }
    all_finite = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)
    maximum_split_residual = max(
        construction_summary["maximum_sector_structural_residual"],
        construction_summary["maximum_fixed_leaf_residual"],
        construction_summary["maximum_riesz_inverse_residual"],
        construction_summary["maximum_block_diagonalization_relative_residual"],
        construction_summary[
            "maximum_tangent_normal_orthogonality_residual"
        ],
        construction_summary["maximum_projector_completeness_residual"],
        construction_summary["maximum_adapted_tangent_leakage"],
        construction_summary["maximum_adapted_normal_leakage"],
    )
    maximum_condition_number = max(
        construction_summary["maximum_local_riesz_basis_condition_number"],
        construction_summary["maximum_local_stein_condition_number"],
        construction_summary["maximum_local_metric_condition_number"],
        construction_summary["maximum_local_whitening_condition_number"],
        construction_summary["global_riesz_basis_condition_number"],
        construction_summary["global_metric_condition_number"],
        construction_summary["global_whitening_condition_number"],
    )

    validity_gates = {
        "q007d_reproduction": {
            "value": {
                "coefficient_hashes_match": upstream[
                    "coefficient_reproduction"
                ]["match"],
                "maximum_gamma_relative_error": upstream[
                    "maximum_relative_error"
                ],
            },
            "threshold": {
                "coefficient_hashes_match": True,
                "maximum_gamma_relative_error": (
                    MAXIMUM_Q007D_REPRODUCTION_RELATIVE_ERROR
                ),
            },
            "passed": bool(
                upstream["coefficient_reproduction"]["match"]
                and upstream["maximum_relative_error"]
                <= MAXIMUM_Q007D_REPRODUCTION_RELATIVE_ERROR
            ),
        },
        "spectral_gap_and_dimensions": {
            "value": {
                "wave_block_count": construction_summary["wave_block_count"],
                "fixed_leaf_dimension": construction_summary[
                    "fixed_leaf_dimension"
                ],
                "selected_complex_dimension": construction_summary[
                    "selected_complex_dimension"
                ],
                "selected_wave_count": construction_summary[
                    "selected_wave_count"
                ],
                "missing_selected_waves": construction_summary[
                    "missing_selected_waves"
                ],
                "unexpected_selected_waves": construction_summary[
                    "unexpected_selected_waves"
                ],
                "maximum_excluded_modulus": spectral_gap[
                    "maximum_excluded_modulus"
                ],
                "registered_rate": spectral_gap["registered_rate"],
                "minimum_selected_modulus": spectral_gap[
                    "minimum_selected_modulus"
                ],
            },
            "threshold": {
                "wave_block_count": SIZE * SIZE,
                "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
                "selected_complex_dimension": SELECTED_COMPLEX_DIMENSION,
                "selected_wave_count": EXPECTED_SELECTED_WAVE_COUNT,
                "missing_selected_waves": [],
                "unexpected_selected_waves": [],
                "strict_ordering": "rho_N < r_* < mu_T",
            },
            "passed": bool(
                construction_summary["wave_block_count"] == SIZE * SIZE
                and construction_summary["fixed_leaf_dimension"]
                == FIXED_LEAF_DIMENSION
                and construction_summary["selected_complex_dimension"]
                == SELECTED_COMPLEX_DIMENSION
                and construction_summary["selected_wave_count"]
                == EXPECTED_SELECTED_WAVE_COUNT
                and not construction_summary["missing_selected_waves"]
                and not construction_summary["unexpected_selected_waves"]
                and spectral_gap["maximum_excluded_modulus"]
                < spectral_gap["registered_rate"]
                < spectral_gap["minimum_selected_modulus"]
            ),
        },
        "riesz_split": {
            "value": maximum_split_residual,
            "threshold": MAXIMUM_SPLIT_RESIDUAL,
            "passed": maximum_split_residual <= MAXIMUM_SPLIT_RESIDUAL,
        },
        "stein_positive_definite_metrics": {
            "value": {
                "maximum_relative_residual": construction_summary[
                    "maximum_stein_relative_residual"
                ],
                "maximum_hermitian_relative_residual": construction_summary[
                    "maximum_stein_hermitian_relative_residual"
                ],
                "minimum_eigenvalue": construction_summary[
                    "minimum_stein_eigenvalue"
                ],
            },
            "threshold": {
                "maximum_relative_residual": MAXIMUM_STEIN_RESIDUAL,
                "maximum_hermitian_relative_residual": (
                    MAXIMUM_HERMITIAN_RESIDUAL
                ),
                "minimum_eigenvalue_strictly_greater_than": (
                    MINIMUM_STEIN_EIGENVALUE
                ),
            },
            "passed": bool(
                construction_summary["maximum_stein_relative_residual"]
                <= MAXIMUM_STEIN_RESIDUAL
                and construction_summary[
                    "maximum_stein_hermitian_relative_residual"
                ]
                <= MAXIMUM_HERMITIAN_RESIDUAL
                and construction_summary["minimum_stein_eigenvalue"]
                > MINIMUM_STEIN_EIGENVALUE
            ),
        },
        "metric_conditioning": {
            "value": maximum_condition_number,
            "threshold": MAXIMUM_CONDITION_NUMBER,
            "passed": maximum_condition_number <= MAXIMUM_CONDITION_NUMBER,
        },
        "conjugacy_and_real_roundtrip": {
            "value": {
                "maximum_metric_conjugacy_relative_residual": conjugacy[
                    "maximum_metric_conjugacy_relative_residual"
                ],
                "maximum_roundtrip_relative_error": roundtrip_summary[
                    "maximum_roundtrip_relative_error"
                ],
                "maximum_imaginary_leakage_relative_norm": roundtrip_summary[
                    "maximum_imaginary_leakage_relative_norm"
                ],
                "minimum_adapted_norm": roundtrip_summary[
                    "minimum_adapted_norm"
                ],
            },
            "threshold": {
                "maximum_metric_conjugacy_relative_residual": (
                    MAXIMUM_CONJUGACY_RESIDUAL
                ),
                "maximum_roundtrip_relative_error": (
                    MAXIMUM_TRANSFORM_ROUNDTRIP_ERROR
                ),
                "maximum_imaginary_leakage_relative_norm": (
                    MAXIMUM_TRANSFORM_IMAGINARY_LEAKAGE
                ),
                "minimum_adapted_norm_strictly_greater_than": 0.0,
            },
            "passed": bool(
                conjugacy["maximum_metric_conjugacy_relative_residual"]
                <= MAXIMUM_CONJUGACY_RESIDUAL
                and roundtrip_summary["maximum_roundtrip_relative_error"]
                <= MAXIMUM_TRANSFORM_ROUNDTRIP_ERROR
                and roundtrip_summary[
                    "maximum_imaginary_leakage_relative_norm"
                ]
                <= MAXIMUM_TRANSFORM_IMAGINARY_LEAKAGE
                and roundtrip_summary["minimum_adapted_norm"] > 0.0
            ),
        },
        "matrix_free_adapted_svd": {
            "value": svd_summary,
            "threshold": {
                "maximum_matrix_free_vs_blockwise_normal_relative_error": (
                    MAXIMUM_BLOCKWISE_SVD_ERROR
                ),
                "maximum_triplet_relative_residual": MAXIMUM_TRIPLET_RESIDUAL,
                "maximum_two_start_singular_value_relative_disagreement": (
                    MAXIMUM_TWO_START_DISAGREEMENT
                ),
            },
            "passed": bool(
                svd_summary[
                    "maximum_matrix_free_vs_blockwise_normal_relative_error"
                ]
                <= MAXIMUM_BLOCKWISE_SVD_ERROR
                and svd_summary["maximum_triplet_relative_residual"]
                <= MAXIMUM_TRIPLET_RESIDUAL
                and svd_summary[
                    "maximum_two_start_singular_value_relative_disagreement"
                ]
                <= MAXIMUM_TWO_START_DISAGREEMENT
            ),
        },
        "finite_and_strict_json": {
            "value": {
                "all_numeric_values_finite": all_finite,
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "all_numeric_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": all_finite and strict_json,
        },
    }

    horizon_lookup = {
        record["horizon"]: record for record in svd_audit["horizon_records"]
    }
    hypothesis_gates = {
        "adapted_equilibrium_gamma_1": {
            "value": horizon_lookup[1]["gamma"],
            "threshold_strictly_less_than": 1.0,
            "passed": horizon_lookup[1]["gamma"] < 1.0,
        },
        "adapted_equilibrium_gamma_10": {
            "value": horizon_lookup[10]["gamma"],
            "threshold_strictly_less_than": 1.0,
            "passed": horizon_lookup[10]["gamma"] < 1.0,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not study_valid:
        outcome = "inconclusive"
        classification = "registered equilibrium adapted-metric audit is inconclusive"
        decision = "Do not run the finite-radius adapted campaign."
        next_change = (
            "Diagnose the registered split, metric, transform, or SVD validity "
            "failure without changing the metric construction."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "equilibrium Riesz/Stein metric prequalified for finite-radius testing"
        )
        decision = (
            "Proceed to a separately sealed Q007f campaign on the same 33 Q007d "
            "starting points without changing the equilibrium-derived metric."
        )
        next_change = (
            "Preregister Q007f finite-radius adapted tangent/normal cocycles using "
            "this fixed Fourier-Riesz Stein metric."
        )
    else:
        outcome = "rejected"
        classification = (
            "registered equilibrium adapted metric does not recover normal dominance"
        )
        decision = "Do not run this metric on the finite-radius campaign."
        next_change = (
            "Close this adapted-metric branch unless a different metric is "
            "separately preregistered."
        )

    return {
        "question": (
            "Does the Q006h spectral gap yield one- and ten-step normal dominance "
            "in the preregistered equilibrium Riesz/Stein norm?"
        ),
        "hypothesis": (
            "Both adapted equilibrium gamma_1 and gamma_10 are strictly less "
            "than one after every split, metric, transform, and SVD validity gate."
        ),
        "registered_setup": {
            "grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "fixed_global_conservation_leaf": True,
            "wave_block_count": SIZE * SIZE,
            "selected_complex_dimension": SELECTED_COMPLEX_DIMENSION,
            "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
            "horizons": list(HORIZONS),
            "metric": (
                "ordered-Schur Riesz split with geometric-gap-rate Stein metrics"
            ),
            "finite_radius_data_used_to_construct_metric": False,
        },
        "q007d_reproduction": upstream,
        "metric_construction": construction,
        "conjugacy_audit": conjugacy,
        "transform_roundtrip_audit": roundtrip,
        "adapted_svd_audit": svd_audit,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "preserved_prior_outcomes": {
            "q006h_spectral_gap_revised": False,
            "q007d_euclidean_rejection_revised": False,
            "q007c2_finite_shadow_domain_revised": False,
        },
        "claim_boundary": (
            "The outcome is an equilibrium, single-grid adapted-metric "
            "prequalification. It is not finite-radius normal attraction, a true "
            "invariant normal bundle, a grid-uniform bound, or an invariant-"
            "manifold existence or uniqueness theorem."
        ),
    }
