"""Sealed Q006i filtered full-2D dense quadratic chart oracle."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from itertools import combinations_with_replacement
from numbers import Integral
from typing import Any

import numpy as np
import numpy.typing as npt

from .checkerboard_filter import (
    filter_multiplier,
    filtered_bgk_periodic_step,
    filtered_fourier_symbol,
)
from .d2q9 import (
    D2Q9_VELOCITIES,
    conserved_moment_matrix,
    equilibrium_tangent_matrix,
    exact_uniform_hessian,
    global_conserved_quantities,
    quarter_turn_population_matrix,
    uniform_equilibrium,
)
from .manifold import QuadraticChart, log_log_slope
from .nonresonance import (
    NUMERICAL_RANK_MULTIPLIER,
    add_wave_indices,
    canonical_wave_index,
    fixed_leaf_kinetic_restriction,
    quadratic_fourier_forcing,
    simple_hydrodynamic_modes,
    wave_vector_from_index,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]
WaveIndex = tuple[int, int]

REGISTERED_SIZE = 17
REGISTERED_OMEGA = 1.5
REGISTERED_ETA = 0.01
MODE_ORDER = ("shear", "acoustic_positive", "acoustic_negative")
POSITIVE_WAVES = ((1, 0), (0, 1), (1, 1), (-1, 1))
WAVE_ORDER = (
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
    (1, 1),
    (-1, 1),
    (-1, -1),
    (1, -1),
)
CONJUGATE_LABEL = {
    "shear": "shear",
    "acoustic_positive": "acoustic_negative",
    "acoustic_negative": "acoustic_positive",
}
REDUCED_DIMENSION = 24
PAIR_COUNT = 300
RESIDUAL_SEED = 20260809
HESSIAN_SEED = 20260808
SHADOW_SEED = 20260810
AMPLITUDES = (0.000625, 0.00125, 0.0025, 0.005, 0.01)


@dataclass(frozen=True)
class _ComplexMode:
    identifier: str
    wave_index: WaveIndex
    label: str
    right: ComplexArray
    left: ComplexArray
    eigenvalue: complex


@dataclass(frozen=True)
class Full2DConstructionDiagnostics:
    pair_count: int
    zero_wave_pair_count: int
    internal_output_pair_count: int
    external_output_pair_count: int
    axial_second_harmonic_pair_count: int
    diagonal_second_harmonic_pair_count: int
    numerical_singular_block_count: int
    minimum_operator_singular_value: float
    maximum_operator_condition_number: float
    maximum_solve_relative_residual: float
    tangent_relative_residual: float
    duality_residual: float
    hessian_symmetry_relative_residual: float
    reduced_hessian_symmetry_relative_residual: float
    homological_relative_residual: float
    maximum_homological_residual: float
    graph_gauge_relative_residual: float
    tangent_conservation_relative_residual: float
    hessian_conservation_relative_residual: float
    zero_wave_conserved_moment_relative_residual: float
    complex_conjugacy_relative_residual: float
    realification_imaginary_leakage_relative_norm: float
    hessian_fourier_leakage_relative_norm: float
    c4_tangent_relative_residual: float
    c4_reduced_linear_relative_residual: float
    c4_hessian_relative_residual: float
    c4_reduced_hessian_relative_residual: float
    reduced_hessian_frobenius_norm: float
    zero_wave_hessian_frobenius_norm: float
    axial_second_harmonic_hessian_frobenius_norm: float
    diagonal_second_harmonic_hessian_frobenius_norm: float
    dense_hessian_sha256: str
    reduced_hessian_sha256: str


@dataclass(frozen=True)
class Full2DQuadraticModel:
    """Dense real chart and quadratic reduced map for sealed Q006i."""

    size: int
    omega: float
    eta: float
    mode_order: tuple[str, str, str]
    positive_waves: tuple[WaveIndex, ...]
    chart: QuadraticChart
    linear_chart: QuadraticChart
    extractor: Array
    reduced_linear: Array
    reduced_hessian: Array
    second_derivative: Array
    pair_records: tuple[dict[str, Any], ...]
    diagnostics: Full2DConstructionDiagnostics

    @property
    def reduced_dimension(self) -> int:
        return self.chart.reduced_dimension

    def full_map(self, state: npt.ArrayLike) -> Array:
        value = np.asarray(state, dtype=np.float64)
        if value.shape != self.chart.base.shape:
            raise ValueError("state dimension does not match the full-2D chart")
        return filtered_bgk_periodic_step(
            value.reshape(self.size, self.size, 9),
            self.omega,
            self.eta,
        ).ravel()

    def reduced_map(
        self,
        coordinates: npt.ArrayLike,
        *,
        quadratic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("coordinate dimension does not match the full-2D chart")
        result = self.reduced_linear @ value
        if quadratic:
            result = result + 0.5 * np.einsum(
                "ijk,j,k->i",
                self.reduced_hessian,
                value,
                value,
            )
        return np.asarray(result, dtype=np.float64)

    def invariance_defect(
        self,
        coordinates: npt.ArrayLike,
        *,
        quadratic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        chart = self.chart if quadratic else self.linear_chart
        return self.full_map(chart.evaluate(value)) - chart.evaluate(
            self.reduced_map(value, quadratic=quadratic)
        )


def _require_registered_parameters(
    size: int,
    omega: float,
    eta: float,
) -> tuple[int, float, float]:
    if isinstance(size, bool) or not isinstance(size, Integral):
        raise TypeError("sealed Q006i requires integer N=17")
    values = (int(size), float(omega), float(eta))
    if values != (REGISTERED_SIZE, REGISTERED_OMEGA, REGISTERED_ETA):
        raise ValueError("sealed Q006i is fixed at N=17, omega=1.5, eta=0.01")
    return values


def _relative_norm(
    numerator: npt.ArrayLike,
    denominator: npt.ArrayLike,
) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).eps)
    )


def _negative_wave(wave_index: WaveIndex, size: int) -> WaveIndex:
    return canonical_wave_index((-wave_index[0], -wave_index[1]), size)


def _wave_shape(wave_index: WaveIndex) -> tuple[int, int]:
    return tuple(sorted(abs(int(value)) for value in wave_index))


def _build_complex_modes(
    size: int,
    omega: float,
    eta: float,
) -> tuple[list[_ComplexMode], dict[tuple[WaveIndex, str], int]]:
    raw: dict[tuple[WaveIndex, str], tuple[ComplexArray, ComplexArray, complex]] = {}
    for wave_index in POSITIVE_WAVES:
        modes = simple_hydrodynamic_modes(
            *wave_vector_from_index(wave_index, size),
            omega,
        )
        multiplier = filter_multiplier(
            *wave_vector_from_index(wave_index, size),
            eta,
        )
        negative = _negative_wave(wave_index, size)
        for label in MODE_ORDER:
            mode = modes[label]
            raw[(wave_index, label)] = (
                np.asarray(mode.right_eigenvector, dtype=np.complex128),
                np.asarray(mode.left_eigenvector, dtype=np.complex128),
                complex(multiplier * mode.eigenvalue),
            )
            negative_label = CONJUGATE_LABEL[label]
            raw[(negative, negative_label)] = (
                np.conjugate(mode.right_eigenvector),
                np.conjugate(mode.left_eigenvector),
                complex(multiplier * np.conjugate(mode.eigenvalue)),
            )

    modes = []
    lookup: dict[tuple[WaveIndex, str], int] = {}
    for wave_index in WAVE_ORDER:
        for label in MODE_ORDER:
            right, left, eigenvalue = raw[(wave_index, label)]
            index = len(modes)
            lookup[(wave_index, label)] = index
            modes.append(
                _ComplexMode(
                    identifier=f"m{index:03d}",
                    wave_index=wave_index,
                    label=label,
                    right=right,
                    left=left,
                    eigenvalue=eigenvalue,
                )
            )
    if len(modes) != REDUCED_DIMENSION:
        raise RuntimeError("Q006i must contain 24 complex conjugate-constrained modes")
    return modes, lookup


def _coordinate_map(
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
) -> ComplexArray:
    scale = 1.0 / (np.sqrt(2.0) * size)
    transform = np.zeros(
        (len(modes), REDUCED_DIMENSION),
        dtype=np.complex128,
    )
    coordinate = 0
    for wave_index in POSITIVE_WAVES:
        negative = _negative_wave(wave_index, size)
        for label in MODE_ORDER:
            positive_index = lookup[(wave_index, label)]
            negative_index = lookup[(negative, CONJUGATE_LABEL[label])]
            transform[positive_index, coordinate] = scale
            transform[positive_index, coordinate + 1] = 1j * scale
            transform[negative_index, coordinate] = scale
            transform[negative_index, coordinate + 1] = -1j * scale
            coordinate += 2
    if coordinate != REDUCED_DIMENSION:
        raise RuntimeError("Q006i real coordinate map has the wrong dimension")
    return transform


def _phase_field(wave_index: WaveIndex, size: int) -> ComplexArray:
    y, x = np.indices((size, size))
    return np.exp(
        2j
        * np.pi
        * (wave_index[0] * x + wave_index[1] * y)
        / float(size)
    )


def _real_tangent_and_extractor(
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
    coordinate_map: ComplexArray,
    size: int,
) -> tuple[Array, Array, float]:
    complex_tangent = np.zeros(
        (size, size, 9, REDUCED_DIMENSION),
        dtype=np.complex128,
    )
    for mode_index, mode in enumerate(modes):
        complex_tangent += np.einsum(
            "xy,q,j->xyqj",
            _phase_field(mode.wave_index, size),
            mode.right,
            coordinate_map[mode_index],
        )
    imaginary_leakage = _relative_norm(complex_tangent.imag, complex_tangent.real)
    tangent = np.asarray(complex_tangent.real, dtype=np.float64).reshape(
        size * size * 9,
        REDUCED_DIMENSION,
    )

    scale = 1.0 / (np.sqrt(2.0) * size)
    extractor = np.zeros(
        (REDUCED_DIMENSION, size * size * 9),
        dtype=np.float64,
    )
    coordinate = 0
    for wave_index in POSITIVE_WAVES:
        phase = np.conjugate(_phase_field(wave_index, size))
        for label in MODE_ORDER:
            mode = modes[lookup[(wave_index, label)]]
            coefficient = np.einsum(
                "xy,q->xyq",
                phase,
                np.conjugate(mode.left),
            ) / (float(size * size) * scale)
            extractor[coordinate] = coefficient.real.ravel()
            extractor[coordinate + 1] = coefficient.imag.ravel()
            coordinate += 2
    return tangent, extractor, imaginary_leakage


def _real_reduced_linear(
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
) -> Array:
    reduced = np.zeros(
        (REDUCED_DIMENSION, REDUCED_DIMENSION),
        dtype=np.float64,
    )
    coordinate = 0
    for wave_index in POSITIVE_WAVES:
        for label in MODE_ORDER:
            eigenvalue = modes[lookup[(wave_index, label)]].eigenvalue
            reduced[coordinate : coordinate + 2, coordinate : coordinate + 2] = (
                np.array(
                    [
                        [eigenvalue.real, -eigenvalue.imag],
                        [eigenvalue.imag, eigenvalue.real],
                    ]
                )
            )
            coordinate += 2
    return reduced


def _filter_tensor(field: npt.ArrayLike, eta: float) -> np.ndarray:
    value = np.asarray(field)
    neighbours = (
        np.roll(value, 1, axis=0)
        + np.roll(value, -1, axis=0)
        + np.roll(value, 1, axis=1)
        + np.roll(value, -1, axis=1)
    )
    return (1.0 - eta) * value + 0.25 * eta * neighbours


def _linear_filtered_action(
    field: npt.ArrayLike,
    omega: float,
    eta: float,
) -> np.ndarray:
    value = np.asarray(field)
    moments = np.einsum("aq,xyq...->xya...", conserved_moment_matrix(), value)
    equilibrium_tangent = np.einsum(
        "qa,xya...->xyq...",
        equilibrium_tangent_matrix(),
        moments,
    )
    collided = (1.0 - omega) * value + omega * equilibrium_tangent
    streamed = np.empty_like(collided)
    for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(int)):
        streamed[:, :, population] = np.roll(
            collided[:, :, population],
            shift=(int(cy), int(cx)),
            axis=(0, 1),
        )
    return _filter_tensor(streamed, eta)


def _analytic_second_derivative(
    tangent: Array,
    size: int,
    omega: float,
    eta: float,
) -> Array:
    field = tangent.reshape(size, size, 9, REDUCED_DIMENSION)
    moments = np.einsum(
        "aq,xyqj->xyaj",
        conserved_moment_matrix(),
        field,
    )
    local = omega * np.einsum(
        "qab,xyaj,xybk->xyqjk",
        exact_uniform_hessian(1, 1),
        moments,
        moments,
    )
    streamed = np.empty_like(local)
    for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(int)):
        streamed[:, :, population] = np.roll(
            local[:, :, population],
            shift=(int(cy), int(cx)),
            axis=(0, 1),
        )
    filtered = _filter_tensor(streamed, eta)
    return np.asarray(filtered, dtype=np.float64).reshape(
        size * size * 9,
        REDUCED_DIMENSION,
        REDUCED_DIMENSION,
    )


def _selected_output_basis(
    wave_index: WaveIndex,
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
) -> tuple[ComplexArray, ComplexArray, list[int]]:
    indices = [lookup[(wave_index, label)] for label in MODE_ORDER]
    right = np.column_stack([modes[index].right for index in indices])
    left_adjoint = np.vstack(
        [np.conjugate(modes[index].left) for index in indices]
    )
    return right, left_adjoint, indices


def _solve_pair(
    pair_index: int,
    left_index: int,
    right_index: int,
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
    omega: float,
    eta: float,
) -> tuple[ComplexArray, ComplexArray, dict[str, Any]]:
    left = modes[left_index]
    right = modes[right_index]
    output_wave = add_wave_indices(left.wave_index, right.wave_index, size)
    output_vector = wave_vector_from_index(output_wave, size)
    forcing = filter_multiplier(*output_vector, eta) * quadratic_fourier_forcing(
        left.right,
        right.right,
        output_vector,
        omega,
    )
    multiplier_product = left.eigenvalue * right.eigenvalue
    reduced_output = np.zeros(len(modes), dtype=np.complex128)
    fixed_leaf_forcing_residual = (
        _relative_norm(conserved_moment_matrix() @ forcing, forcing)
        if output_wave == (0, 0)
        else 0.0
    )

    if output_wave == (0, 0):
        kinetic, unfiltered_block, invariance = fixed_leaf_kinetic_restriction(
            omega
        )
        block = unfiltered_block - multiplier_product * np.eye(kinetic.shape[1])
        restricted_forcing = kinetic.conj().T @ forcing
        operator = block
        right_hand_side = -restricted_forcing
        output_kind = "zero_wave_kinetic"
    elif output_wave in WAVE_ORDER:
        output_matrix = filtered_fourier_symbol(*output_vector, omega, eta)
        selected_right, selected_left, output_indices = _selected_output_basis(
            output_wave,
            modes,
            lookup,
        )
        operator = np.block(
            [
                [
                    output_matrix
                    - multiplier_product * np.eye(9, dtype=np.complex128),
                    -selected_right,
                ],
                [selected_left, np.zeros((3, 3), dtype=np.complex128)],
            ]
        )
        right_hand_side = np.concatenate(
            [-forcing, np.zeros(3, dtype=np.complex128)]
        )
        output_kind = "internal_selected"
        invariance = 0.0
    else:
        output_matrix = filtered_fourier_symbol(*output_vector, omega, eta)
        operator = output_matrix - multiplier_product * np.eye(
            9,
            dtype=np.complex128,
        )
        right_hand_side = -forcing
        output_kind = "external"
        invariance = 0.0

    singular_values = np.linalg.svd(operator, compute_uv=False)
    largest = float(singular_values[0])
    smallest = float(singular_values[-1])
    rank_threshold = float(
        NUMERICAL_RANK_MULTIPLIER
        * np.finfo(float).eps
        * max(operator.shape)
        * largest
    )
    rank = int(np.count_nonzero(singular_values > rank_threshold))
    numerically_singular = rank < operator.shape[1]
    solution, *_ = np.linalg.lstsq(operator, right_hand_side, rcond=None)
    solve_residual = _relative_norm(
        operator @ solution - right_hand_side,
        right_hand_side,
    )

    if output_kind == "zero_wave_kinetic":
        hessian = kinetic @ solution
    elif output_kind == "internal_selected":
        hessian = solution[:9]
        reduced_output[output_indices] = solution[9:]
    else:
        hessian = solution

    shape = _wave_shape(output_wave)
    record = {
        "pair_identifier": f"p{pair_index:05d}",
        "left_mode": left.identifier,
        "right_mode": right.identifier,
        "left_label": left.label,
        "right_label": right.label,
        "left_wave_index": list(left.wave_index),
        "right_wave_index": list(right.wave_index),
        "output_wave_index": list(output_wave),
        "output_kind": output_kind,
        "operator_dimension": int(operator.shape[1]),
        "operator_rank": rank,
        "numerical_rank_threshold": rank_threshold,
        "smallest_singular_value": smallest,
        "largest_singular_value": largest,
        "condition_number": (
            None if numerically_singular else float(largest / smallest)
        ),
        "numerically_singular": numerically_singular,
        "solve_relative_residual": solve_residual,
        "forcing_norm": float(np.linalg.norm(forcing)),
        "fixed_leaf_forcing_residual": fixed_leaf_forcing_residual,
        "active_sector_invariance_residual": float(invariance),
        "hessian_coefficient_norm": float(np.linalg.norm(hessian)),
        "reduced_coefficient_norm": float(np.linalg.norm(reduced_output)),
        "axial_second_harmonic": shape == (0, 2),
        "diagonal_second_harmonic": shape == (2, 2),
    }
    return (
        np.asarray(hessian, dtype=np.complex128),
        reduced_output,
        record,
    )


def _complex_coefficients(
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
    omega: float,
    eta: float,
) -> tuple[ComplexArray, ComplexArray, np.ndarray, list[dict[str, Any]]]:
    count = len(modes)
    hessian = np.zeros((count, count, 9), dtype=np.complex128)
    reduced = np.zeros((count, count, count), dtype=np.complex128)
    output_waves = np.zeros((count, count, 2), dtype=np.int64)
    records = []
    for pair_index, (left_index, right_index) in enumerate(
        combinations_with_replacement(range(count), 2)
    ):
        coefficient, reduced_output, record = _solve_pair(
            pair_index,
            left_index,
            right_index,
            modes,
            lookup,
            size,
            omega,
            eta,
        )
        output_wave = tuple(record["output_wave_index"])
        hessian[left_index, right_index] = coefficient
        hessian[right_index, left_index] = coefficient
        reduced[:, left_index, right_index] = reduced_output
        reduced[:, right_index, left_index] = reduced_output
        output_waves[left_index, right_index] = output_wave
        output_waves[right_index, left_index] = output_wave
        records.append(record)
    if len(records) != PAIR_COUNT:
        raise RuntimeError("Q006i did not enumerate the registered 300 pairs")
    return hessian, reduced, output_waves, records


def _conjugate_mode_indices(
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
) -> np.ndarray:
    return np.asarray(
        [
            lookup[
                (
                    _negative_wave(mode.wave_index, size),
                    CONJUGATE_LABEL[mode.label],
                )
            ]
            for mode in modes
        ],
        dtype=np.int64,
    )


def _complex_conjugacy_residual(
    hessian: ComplexArray,
    reduced: ComplexArray,
    conjugate_indices: np.ndarray,
) -> float:
    conjugate_hessian = hessian[
        conjugate_indices[:, None],
        conjugate_indices[None, :],
    ]
    hessian_error = conjugate_hessian - np.conjugate(hessian)
    conjugate_reduced = reduced[
        conjugate_indices[:, None, None],
        conjugate_indices[None, :, None],
        conjugate_indices[None, None, :],
    ]
    reduced_error = conjugate_reduced - np.conjugate(reduced)
    return max(
        _relative_norm(hessian_error, hessian),
        _relative_norm(reduced_error, reduced),
    )


def _realify_coefficients(
    hessian: ComplexArray,
    reduced: ComplexArray,
    output_waves: np.ndarray,
    coordinate_map: ComplexArray,
    modes: list[_ComplexMode],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
) -> tuple[Array, Array, float, dict[WaveIndex, ComplexArray]]:
    fourier_coefficients: dict[WaveIndex, ComplexArray] = {}
    for left_index in range(len(modes)):
        for right_index in range(len(modes)):
            wave_index = tuple(int(value) for value in output_waves[left_index, right_index])
            contribution = np.einsum(
                "q,j,k->qjk",
                hessian[left_index, right_index],
                coordinate_map[left_index],
                coordinate_map[right_index],
            )
            if wave_index not in fourier_coefficients:
                fourier_coefficients[wave_index] = np.zeros_like(contribution)
            fourier_coefficients[wave_index] += contribution

    physical = np.zeros(
        (size, size, 9, REDUCED_DIMENSION, REDUCED_DIMENSION),
        dtype=np.complex128,
    )
    for wave_index, coefficient in fourier_coefficients.items():
        physical += np.einsum(
            "xy,qjk->xyqjk",
            _phase_field(wave_index, size),
            coefficient,
        )
    imaginary_leakage = _relative_norm(physical.imag, physical.real)
    real_hessian = np.asarray(physical.real, dtype=np.float64).reshape(
        size * size * 9,
        REDUCED_DIMENSION,
        REDUCED_DIMENSION,
    )

    transformed_reduced = np.einsum(
        "gab,aj,bk->gjk",
        reduced,
        coordinate_map,
        coordinate_map,
        optimize=True,
    )
    scale = 1.0 / (np.sqrt(2.0) * size)
    real_reduced = np.zeros(
        (REDUCED_DIMENSION, REDUCED_DIMENSION, REDUCED_DIMENSION),
        dtype=np.float64,
    )
    coordinate = 0
    for wave_index in POSITIVE_WAVES:
        for label in MODE_ORDER:
            mode_index = lookup[(wave_index, label)]
            real_reduced[coordinate] = transformed_reduced[mode_index].real / scale
            real_reduced[coordinate + 1] = (
                transformed_reduced[mode_index].imag / scale
            )
            coordinate += 2
    return real_hessian, real_reduced, imaginary_leakage, fourier_coefficients


def _quarter_turn_field(field: npt.ArrayLike, size: int) -> np.ndarray:
    value = np.asarray(field).reshape(size, size, 9, *np.asarray(field).shape[3:])
    target_y, target_x = np.indices((size, size))
    pulled_back = value[(-target_x) % size, target_y]
    rotation = quarter_turn_population_matrix()
    return np.einsum("qr,xyr...->xyq...", rotation, pulled_back)


def _fourier_support_diagnostics(
    hessian: Array,
    expected_support: set[WaveIndex],
    size: int,
) -> tuple[float, float, float, float]:
    field = hessian.reshape(
        size,
        size,
        9,
        REDUCED_DIMENSION,
        REDUCED_DIMENSION,
    )
    transformed = np.fft.fft2(field, axes=(0, 1)) / float(size * size)
    included = np.zeros((size, size), dtype=bool)
    for wave_index in expected_support:
        included[wave_index[1] % size, wave_index[0] % size] = True
    leakage = _relative_norm(transformed[~included], transformed)

    def sector_norm(shape: tuple[int, int]) -> float:
        return float(
            np.sqrt(
                sum(
                    np.linalg.norm(transformed[iy, ix]) ** 2
                    for iy in range(size)
                    for ix in range(size)
                    if _wave_shape(
                        canonical_wave_index((ix, iy), size)
                    )
                    == shape
                )
            )
        )

    zero_norm = float(np.linalg.norm(transformed[0, 0]))
    return leakage, zero_norm, sector_norm((0, 2)), sector_norm((2, 2))


def _array_hash(value: npt.ArrayLike) -> str:
    array = np.ascontiguousarray(np.asarray(value, dtype=np.float64))
    digest = sha256()
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def build_full2d_quadratic_model(
    size: int = REGISTERED_SIZE,
    omega: float = REGISTERED_OMEGA,
    eta: float = REGISTERED_ETA,
) -> Full2DQuadraticModel:
    """Construct the sealed Q006i 24-coordinate dense quadratic chart."""

    size, omega, eta = _require_registered_parameters(size, omega, eta)
    modes, lookup = _build_complex_modes(size, omega, eta)
    coordinate_map = _coordinate_map(modes, lookup, size)
    tangent, extractor, tangent_imaginary_leakage = _real_tangent_and_extractor(
        modes,
        lookup,
        coordinate_map,
        size,
    )
    reduced_linear = _real_reduced_linear(modes, lookup)
    complex_hessian, complex_reduced, output_waves, pair_records = (
        _complex_coefficients(modes, lookup, size, omega, eta)
    )
    conjugate_indices = _conjugate_mode_indices(modes, lookup, size)
    conjugacy_residual = _complex_conjugacy_residual(
        complex_hessian,
        complex_reduced,
        conjugate_indices,
    )
    hessian, reduced_hessian, hessian_imaginary_leakage, fourier_coefficients = (
        _realify_coefficients(
            complex_hessian,
            complex_reduced,
            output_waves,
            coordinate_map,
            modes,
            lookup,
            size,
        )
    )
    second_derivative = _analytic_second_derivative(tangent, size, omega, eta)

    linear_tangent = _linear_filtered_action(
        tangent.reshape(size, size, 9, REDUCED_DIMENSION),
        omega,
        eta,
    ).reshape(size * size * 9, REDUCED_DIMENSION)
    linear_hessian = _linear_filtered_action(
        hessian.reshape(
            size,
            size,
            9,
            REDUCED_DIMENSION,
            REDUCED_DIMENSION,
        ),
        omega,
        eta,
    ).reshape(size * size * 9, REDUCED_DIMENSION, REDUCED_DIMENSION)
    transformed_hessian = np.einsum(
        "ipq,pj,qk->ijk",
        hessian,
        reduced_linear,
        reduced_linear,
        optimize=True,
    )
    lifted_reduced = np.einsum(
        "ir,rjk->ijk",
        tangent,
        reduced_hessian,
        optimize=True,
    )
    homological_equation = (
        linear_hessian - transformed_hessian - lifted_reduced + second_derivative
    )

    base = uniform_equilibrium(size, size, np.zeros(3)).ravel()
    chart = QuadraticChart(base=base, tangent=tangent, hessian=hessian)
    linear_chart = QuadraticChart(
        base=base,
        tangent=tangent,
        hessian=np.zeros_like(hessian),
    )

    hessian_matrix = hessian.reshape(size * size * 9, REDUCED_DIMENSION**2)
    conservation = np.tile(conserved_moment_matrix(), (1, size * size))
    zero_wave = fourier_coefficients[(0, 0)]
    zero_conservation = np.einsum(
        "aq,qjk->ajk",
        conserved_moment_matrix(),
        zero_wave,
    )
    expected_support = {
        tuple(int(value) for value in output_waves[left, right])
        for left in range(len(modes))
        for right in range(len(modes))
    }
    (
        fourier_leakage,
        zero_wave_norm,
        axial_second_norm,
        diagonal_second_norm,
    ) = _fourier_support_diagnostics(hessian, expected_support, size)

    rotated_tangent = _quarter_turn_field(
        tangent.reshape(size, size, 9, REDUCED_DIMENSION),
        size,
    ).reshape(size * size * 9, REDUCED_DIMENSION)
    coordinate_rotation = extractor @ rotated_tangent
    rotated_hessian = _quarter_turn_field(
        hessian.reshape(
            size,
            size,
            9,
            REDUCED_DIMENSION,
            REDUCED_DIMENSION,
        ),
        size,
    ).reshape(size * size * 9, REDUCED_DIMENSION, REDUCED_DIMENSION)
    transformed_c4_hessian = np.einsum(
        "ipq,pj,qk->ijk",
        hessian,
        coordinate_rotation,
        coordinate_rotation,
        optimize=True,
    )
    transformed_c4_reduced = np.einsum(
        "ipq,pj,qk->ijk",
        reduced_hessian,
        coordinate_rotation,
        coordinate_rotation,
        optimize=True,
    )
    rotated_reduced = np.einsum(
        "ir,rjk->ijk",
        coordinate_rotation,
        reduced_hessian,
        optimize=True,
    )

    finite_conditions = [
        float(record["condition_number"])
        for record in pair_records
        if record["condition_number"] is not None
    ]
    diagnostics = Full2DConstructionDiagnostics(
        pair_count=len(pair_records),
        zero_wave_pair_count=sum(
            record["output_kind"] == "zero_wave_kinetic"
            for record in pair_records
        ),
        internal_output_pair_count=sum(
            record["output_kind"] == "internal_selected"
            for record in pair_records
        ),
        external_output_pair_count=sum(
            record["output_kind"] == "external" for record in pair_records
        ),
        axial_second_harmonic_pair_count=sum(
            record["axial_second_harmonic"] for record in pair_records
        ),
        diagonal_second_harmonic_pair_count=sum(
            record["diagonal_second_harmonic"] for record in pair_records
        ),
        numerical_singular_block_count=sum(
            record["numerically_singular"] for record in pair_records
        ),
        minimum_operator_singular_value=min(
            float(record["smallest_singular_value"])
            for record in pair_records
        ),
        maximum_operator_condition_number=max(finite_conditions),
        maximum_solve_relative_residual=max(
            float(record["solve_relative_residual"])
            for record in pair_records
        ),
        tangent_relative_residual=_relative_norm(
            linear_tangent - tangent @ reduced_linear,
            tangent,
        ),
        duality_residual=float(
            np.linalg.norm(extractor @ tangent - np.eye(REDUCED_DIMENSION))
        ),
        hessian_symmetry_relative_residual=_relative_norm(
            hessian - hessian.swapaxes(1, 2),
            hessian,
        ),
        reduced_hessian_symmetry_relative_residual=_relative_norm(
            reduced_hessian - reduced_hessian.swapaxes(1, 2),
            reduced_hessian,
        ),
        homological_relative_residual=_relative_norm(
            homological_equation,
            second_derivative,
        ),
        maximum_homological_residual=float(
            max(
                np.linalg.norm(homological_equation[:, left, right])
                for left in range(REDUCED_DIMENSION)
                for right in range(REDUCED_DIMENSION)
            )
        ),
        graph_gauge_relative_residual=_relative_norm(
            extractor @ hessian_matrix,
            hessian_matrix,
        ),
        tangent_conservation_relative_residual=_relative_norm(
            conservation @ tangent,
            tangent,
        ),
        hessian_conservation_relative_residual=_relative_norm(
            conservation @ hessian_matrix,
            hessian_matrix,
        ),
        zero_wave_conserved_moment_relative_residual=_relative_norm(
            zero_conservation,
            zero_wave,
        ),
        complex_conjugacy_relative_residual=conjugacy_residual,
        realification_imaginary_leakage_relative_norm=max(
            tangent_imaginary_leakage,
            hessian_imaginary_leakage,
        ),
        hessian_fourier_leakage_relative_norm=fourier_leakage,
        c4_tangent_relative_residual=_relative_norm(
            rotated_tangent - tangent @ coordinate_rotation,
            tangent,
        ),
        c4_reduced_linear_relative_residual=_relative_norm(
            coordinate_rotation @ reduced_linear
            - reduced_linear @ coordinate_rotation,
            reduced_linear,
        ),
        c4_hessian_relative_residual=_relative_norm(
            rotated_hessian - transformed_c4_hessian,
            hessian,
        ),
        c4_reduced_hessian_relative_residual=_relative_norm(
            rotated_reduced - transformed_c4_reduced,
            reduced_hessian,
        ),
        reduced_hessian_frobenius_norm=float(np.linalg.norm(reduced_hessian)),
        zero_wave_hessian_frobenius_norm=zero_wave_norm,
        axial_second_harmonic_hessian_frobenius_norm=axial_second_norm,
        diagonal_second_harmonic_hessian_frobenius_norm=diagonal_second_norm,
        dense_hessian_sha256=_array_hash(hessian),
        reduced_hessian_sha256=_array_hash(reduced_hessian),
    )
    return Full2DQuadraticModel(
        size=size,
        omega=omega,
        eta=eta,
        mode_order=MODE_ORDER,
        positive_waves=POSITIVE_WAVES,
        chart=chart,
        linear_chart=linear_chart,
        extractor=extractor,
        reduced_linear=reduced_linear,
        reduced_hessian=reduced_hessian,
        second_derivative=second_derivative,
        pair_records=tuple(pair_records),
        diagnostics=diagnostics,
    )


def _normalized_directions(seed: int, count: int, dimension: int) -> Array:
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(count, dimension))
    return np.asarray(
        directions / np.linalg.norm(directions, axis=1)[:, None],
        dtype=np.float64,
    )


def _independent_hessian_campaign(
    model: Full2DQuadraticModel,
) -> dict[str, Any]:
    rng = np.random.default_rng(HESSIAN_SEED)
    left_directions = rng.normal(size=(32, model.reduced_dimension))
    right_directions = rng.normal(size=(32, model.reduced_dimension))
    left_directions /= np.linalg.norm(left_directions, axis=1)[:, None]
    right_directions /= np.linalg.norm(right_directions, axis=1)[:, None]
    records = []
    for left, right in zip(left_directions, right_directions, strict=True):
        analytic = np.einsum(
            "ijk,j,k->i",
            model.second_derivative,
            left,
            right,
        )

        def centered(
            step: float,
            left_direction: Array = left,
            right_direction: Array = right,
        ) -> Array:
            left_state = step * (model.chart.tangent @ left_direction)
            right_state = step * (model.chart.tangent @ right_direction)
            return (
                model.full_map(model.chart.base + left_state + right_state)
                - model.full_map(model.chart.base + left_state - right_state)
                - model.full_map(model.chart.base - left_state + right_state)
                + model.full_map(model.chart.base - left_state - right_state)
            ) / (4.0 * step * step)

        coarse = centered(0.006)
        fine = centered(0.003)
        richardson = (4.0 * fine - coarse) / 3.0
        records.append(
            {
                "left_direction": left.tolist(),
                "right_direction": right.tolist(),
                "analytic_norm": float(np.linalg.norm(analytic)),
                "analytic_relative_discrepancy": _relative_norm(
                    richardson - analytic,
                    analytic,
                ),
                "coarse_to_fine_relative_change": _relative_norm(
                    fine - coarse,
                    richardson,
                ),
            }
        )
    return {
        "seed": HESSIAN_SEED,
        "direction_pair_count": len(records),
        "coarse_step": 0.006,
        "fine_step": 0.003,
        "method": "centered mixed difference with Richardson extrapolation",
        "direction_records": records,
        "summary": {
            "maximum_analytic_relative_discrepancy": max(
                record["analytic_relative_discrepancy"] for record in records
            ),
            "maximum_coarse_to_fine_relative_change": max(
                record["coarse_to_fine_relative_change"] for record in records
            ),
            "minimum_analytic_norm": min(
                record["analytic_norm"] for record in records
            ),
        },
    }


def _residual_campaign(
    model: Full2DQuadraticModel,
    directions: Array,
    amplitudes: Array,
) -> dict[str, Any]:
    base_conserved = global_conserved_quantities(
        model.chart.base.reshape(model.size, model.size, 9)
    )
    records = []
    for direction in directions:
        linear_residuals = []
        quadratic_residuals = []
        minimum_population = np.inf
        maximum_conservation_drift = 0.0
        for amplitude in amplitudes:
            coordinates = amplitude * direction
            linear_residuals.append(
                float(
                    np.linalg.norm(
                        model.invariance_defect(coordinates, quadratic=False)
                    )
                )
            )
            quadratic_residuals.append(
                float(
                    np.linalg.norm(
                        model.invariance_defect(coordinates, quadratic=True)
                    )
                )
            )
            for chart in (model.linear_chart, model.chart):
                lifted = chart.evaluate(coordinates)
                mapped = model.full_map(lifted)
                minimum_population = min(
                    minimum_population,
                    float(np.min(lifted)),
                    float(np.min(mapped)),
                )
                maximum_conservation_drift = max(
                    maximum_conservation_drift,
                    float(
                        np.linalg.norm(
                            global_conserved_quantities(
                                mapped.reshape(model.size, model.size, 9)
                            )
                            - base_conserved
                        )
                    ),
                )
        records.append(
            {
                "direction": direction.tolist(),
                "linear_residuals": linear_residuals,
                "quadratic_residuals": quadratic_residuals,
                "linear_slope": log_log_slope(amplitudes, linear_residuals),
                "quadratic_slope": log_log_slope(
                    amplitudes,
                    quadratic_residuals,
                ),
                "maximum_amplitude_residual_ratio": (
                    quadratic_residuals[-1] / linear_residuals[-1]
                ),
                "minimum_population": minimum_population,
                "maximum_conservation_drift": maximum_conservation_drift,
            }
        )
    return {
        "seed": RESIDUAL_SEED,
        "amplitudes": amplitudes.tolist(),
        "direction_records": records,
        "summary": {
            "minimum_linear_slope": min(
                record["linear_slope"] for record in records
            ),
            "maximum_linear_slope": max(
                record["linear_slope"] for record in records
            ),
            "minimum_quadratic_slope": min(
                record["quadratic_slope"] for record in records
            ),
            "maximum_quadratic_slope": max(
                record["quadratic_slope"] for record in records
            ),
            "maximum_directional_residual_ratio": max(
                record["maximum_amplitude_residual_ratio"] for record in records
            ),
            "minimum_population": min(
                record["minimum_population"] for record in records
            ),
            "maximum_conservation_drift": max(
                record["maximum_conservation_drift"] for record in records
            ),
        },
    }


def _shadow_campaign(
    model: Full2DQuadraticModel,
    directions: Array,
    amplitude: float,
    steps: int,
    *,
    quadratic: bool,
) -> dict[str, Any]:
    chart = model.chart if quadratic else model.linear_chart
    records = []
    for direction in directions:
        coordinates = amplitude * direction
        state = chart.evaluate(coordinates)
        initial_conserved = global_conserved_quantities(
            state.reshape(model.size, model.size, 9)
        )
        maximum_absolute_error = 0.0
        maximum_relative_error = 0.0
        maximum_coordinate_drift = 0.0
        maximum_conservation_drift = 0.0
        minimum_population = np.inf
        maximum_absolute_error_step = 0
        maximum_relative_error_step = 0
        final_absolute_error = 0.0
        final_relative_error = 0.0
        for step in range(steps + 1):
            predicted = chart.evaluate(coordinates)
            absolute_error = float(np.linalg.norm(state - predicted))
            perturbation_scale = max(
                float(np.linalg.norm(state - chart.base)),
                float(np.linalg.norm(predicted - chart.base)),
                np.finfo(float).eps,
            )
            relative_error = absolute_error / perturbation_scale
            coordinate_drift = float(
                np.linalg.norm(
                    model.extractor @ (state - chart.base) - coordinates
                )
            )
            conservation_drift = float(
                np.linalg.norm(
                    global_conserved_quantities(
                        state.reshape(model.size, model.size, 9)
                    )
                    - initial_conserved
                )
            )
            if absolute_error > maximum_absolute_error:
                maximum_absolute_error = absolute_error
                maximum_absolute_error_step = step
            if relative_error > maximum_relative_error:
                maximum_relative_error = relative_error
                maximum_relative_error_step = step
            maximum_coordinate_drift = max(
                maximum_coordinate_drift,
                coordinate_drift,
            )
            maximum_conservation_drift = max(
                maximum_conservation_drift,
                conservation_drift,
            )
            minimum_population = min(
                minimum_population,
                float(np.min(state)),
                float(np.min(predicted)),
            )
            if step == steps:
                final_absolute_error = absolute_error
                final_relative_error = relative_error
            else:
                state = model.full_map(state)
                coordinates = model.reduced_map(
                    coordinates,
                    quadratic=quadratic,
                )
        records.append(
            {
                "direction": direction.tolist(),
                "maximum_absolute_error": maximum_absolute_error,
                "maximum_absolute_error_step": maximum_absolute_error_step,
                "maximum_perturbation_relative_error": maximum_relative_error,
                "maximum_relative_error_step": maximum_relative_error_step,
                "final_absolute_error": final_absolute_error,
                "final_perturbation_relative_error": final_relative_error,
                "maximum_projected_coordinate_drift": maximum_coordinate_drift,
                "maximum_conservation_drift": maximum_conservation_drift,
                "minimum_population": minimum_population,
            }
        )
    return {
        "chart": "quadratic" if quadratic else "linear",
        "seed": SHADOW_SEED,
        "amplitude": amplitude,
        "steps": steps,
        "direction_records": records,
        "summary": {
            "maximum_absolute_error": max(
                record["maximum_absolute_error"] for record in records
            ),
            "maximum_perturbation_relative_error": max(
                record["maximum_perturbation_relative_error"]
                for record in records
            ),
            "maximum_final_absolute_error": max(
                record["final_absolute_error"] for record in records
            ),
            "maximum_final_perturbation_relative_error": max(
                record["final_perturbation_relative_error"]
                for record in records
            ),
            "maximum_projected_coordinate_drift": max(
                record["maximum_projected_coordinate_drift"] for record in records
            ),
            "maximum_conservation_drift": max(
                record["maximum_conservation_drift"] for record in records
            ),
            "minimum_population": min(
                record["minimum_population"] for record in records
            ),
        },
    }


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_full2d_quadratic_audit() -> dict[str, Any]:
    """Run the sealed Q006i construction, residual, and shadow campaigns."""

    model = build_full2d_quadratic_model()
    diagnostics = asdict(model.diagnostics)
    hessian_check = _independent_hessian_campaign(model)
    residual_directions = _normalized_directions(
        RESIDUAL_SEED,
        64,
        model.reduced_dimension,
    )
    residual_campaign = _residual_campaign(
        model,
        residual_directions,
        np.asarray(AMPLITUDES, dtype=np.float64),
    )
    shadow_directions = _normalized_directions(
        SHADOW_SEED,
        32,
        model.reduced_dimension,
    )
    linear_shadow = _shadow_campaign(
        model,
        shadow_directions,
        0.01,
        100,
        quadratic=False,
    )
    quadratic_shadow = _shadow_campaign(
        model,
        shadow_directions,
        0.01,
        100,
        quadratic=True,
    )
    residual_summary = residual_campaign["summary"]
    linear_shadow_summary = linear_shadow["summary"]
    quadratic_shadow_summary = quadratic_shadow["summary"]
    shadow_improvement = (
        quadratic_shadow_summary["maximum_absolute_error"]
        / linear_shadow_summary["maximum_absolute_error"]
    )

    construction_residual = max(
        diagnostics["tangent_relative_residual"],
        diagnostics["duality_residual"],
        diagnostics["hessian_symmetry_relative_residual"],
        diagnostics["reduced_hessian_symmetry_relative_residual"],
        diagnostics["homological_relative_residual"],
        diagnostics["maximum_homological_residual"],
        diagnostics["graph_gauge_relative_residual"],
        diagnostics["tangent_conservation_relative_residual"],
        diagnostics["hessian_conservation_relative_residual"],
        diagnostics["zero_wave_conserved_moment_relative_residual"],
        diagnostics["complex_conjugacy_relative_residual"],
        diagnostics["realification_imaginary_leakage_relative_norm"],
        diagnostics["c4_tangent_relative_residual"],
        diagnostics["c4_reduced_linear_relative_residual"],
        diagnostics["c4_hessian_relative_residual"],
        diagnostics["c4_reduced_hessian_relative_residual"],
    )
    serializable_probe = {
        "diagnostics": diagnostics,
        "pair_records": model.pair_records,
        "hessian_check": hessian_check,
        "residual_campaign": residual_campaign,
        "linear_shadow": linear_shadow,
        "quadratic_shadow": quadratic_shadow,
    }
    validity_gates = {
        "registered_enumeration": {
            "value": {
                "state_dimension": model.chart.base.size,
                "reduced_dimension": model.reduced_dimension,
                "pair_count": diagnostics["pair_count"],
            },
            "threshold": {
                "state_dimension": 2601,
                "reduced_dimension": REDUCED_DIMENSION,
                "pair_count": PAIR_COUNT,
            },
            "passed": (
                model.chart.base.size == 2601
                and model.reduced_dimension == REDUCED_DIMENSION
                and diagnostics["pair_count"] == PAIR_COUNT
            ),
        },
        "nonsingular_sector_solves": {
            "value": {
                "numerically_singular_block_count": diagnostics[
                    "numerical_singular_block_count"
                ],
                "maximum_solve_relative_residual": diagnostics[
                    "maximum_solve_relative_residual"
                ],
            },
            "threshold": {
                "numerically_singular_block_count": 0,
                "maximum_solve_relative_residual": 1.0e-10,
            },
            "passed": (
                diagnostics["numerical_singular_block_count"] == 0
                and diagnostics["maximum_solve_relative_residual"] <= 1.0e-10
            ),
        },
        "algebraic_chart_consistency": {
            "value": construction_residual,
            "threshold": 1.0e-10,
            "passed": construction_residual <= 1.0e-10,
        },
        "fourier_selection_rule": {
            "value": diagnostics["hessian_fourier_leakage_relative_norm"],
            "threshold": 1.0e-12,
            "passed": diagnostics["hessian_fourier_leakage_relative_norm"]
            <= 1.0e-12,
        },
        "independent_analytic_hessian_check": {
            "value": hessian_check["summary"][
                "maximum_analytic_relative_discrepancy"
            ],
            "threshold": 1.0e-8,
            "passed": hessian_check["summary"][
                "maximum_analytic_relative_discrepancy"
            ]
            <= 1.0e-8,
        },
        "strict_json_finite_values": {
            "value": _strict_json_serializable(serializable_probe),
            "threshold": True,
            "passed": _strict_json_serializable(serializable_probe),
        },
    }
    hypothesis_gates = {
        "linear_residual_order": {
            "value": {
                "minimum": residual_summary["minimum_linear_slope"],
                "maximum": residual_summary["maximum_linear_slope"],
            },
            "threshold": {"minimum": 1.9, "maximum": 2.1},
            "passed": residual_summary["minimum_linear_slope"] >= 1.9
            and residual_summary["maximum_linear_slope"] <= 2.1,
        },
        "quadratic_residual_order": {
            "value": {
                "minimum": residual_summary["minimum_quadratic_slope"],
                "maximum": residual_summary["maximum_quadratic_slope"],
            },
            "threshold": {"minimum": 2.9, "maximum": 3.1},
            "passed": residual_summary["minimum_quadratic_slope"] >= 2.9
            and residual_summary["maximum_quadratic_slope"] <= 3.1,
        },
        "maximum_amplitude_directional_improvement": {
            "value": residual_summary["maximum_directional_residual_ratio"],
            "threshold": 0.1,
            "passed": residual_summary["maximum_directional_residual_ratio"]
            < 0.1,
        },
        "positive_populations": {
            "value": min(
                residual_summary["minimum_population"],
                linear_shadow_summary["minimum_population"],
                quadratic_shadow_summary["minimum_population"],
            ),
            "threshold": 0.0,
            "passed": min(
                residual_summary["minimum_population"],
                linear_shadow_summary["minimum_population"],
                quadratic_shadow_summary["minimum_population"],
            )
            > 0.0,
        },
        "global_conservation": {
            "value": max(
                residual_summary["maximum_conservation_drift"],
                linear_shadow_summary["maximum_conservation_drift"],
                quadratic_shadow_summary["maximum_conservation_drift"],
            ),
            "threshold": 1.0e-12,
            "passed": max(
                residual_summary["maximum_conservation_drift"],
                linear_shadow_summary["maximum_conservation_drift"],
                quadratic_shadow_summary["maximum_conservation_drift"],
            )
            <= 1.0e-12,
        },
        "quadratic_shadowing_absolute_error": {
            "value": quadratic_shadow_summary["maximum_absolute_error"],
            "threshold": 1.0e-5,
            "passed": quadratic_shadow_summary["maximum_absolute_error"]
            < 1.0e-5,
        },
        "quadratic_shadowing_perturbation_relative_error": {
            "value": quadratic_shadow_summary[
                "maximum_perturbation_relative_error"
            ],
            "threshold": 1.0e-2,
            "passed": quadratic_shadow_summary[
                "maximum_perturbation_relative_error"
            ]
            < 1.0e-2,
        },
        "quadratic_shadowing_improvement": {
            "value": shadow_improvement,
            "threshold": 0.1,
            "passed": shadow_improvement < 0.1,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006i construction validity failure"
        decision = (
            "A registered algebra, derivative, support, or serialization gate "
            "failed, so no chart verdict is issued."
        )
        next_change = "Repair the first failed validity gate without tuning Q006i."
    elif hypothesis_passed:
        outcome = "accepted"
        classification = "N17 filtered full-2D quadratic candidate chart verified"
        decision = (
            "The fixed filtered N=17 dense chart passes every registered local "
            "invariance and 100-step shadowing gate."
        )
        next_change = (
            "Preregister dense, Fourier-sparse, and TT-SVD storage and evaluation "
            "comparisons for this fixed chart before TT-cross."
        )
    else:
        outcome = "rejected"
        classification = "Q006i local chart hypothesis rejected"
        decision = (
            "The construction is valid, but at least one preregistered residual, "
            "positivity, conservation, or shadowing gate fails."
        )
        next_change = "Diagnose the first deterministic failed Q006i hypothesis gate."

    return {
        "question": (
            "Does the fixed N=17, eta=0.01, omega=1.5 24-coordinate dense "
            "quadratic chart raise the filtered full-2D invariance residual "
            "from second to third order on the fixed conservation leaf?"
        ),
        "hypothesis": (
            "The sealed chart passes independent Hessian, algebra, residual-order, "
            "positivity, conservation, and 100-step shadowing gates."
        ),
        "registered_scope": {
            "grid": [REGISTERED_SIZE, REGISTERED_SIZE],
            "omega": REGISTERED_OMEGA,
            "eta": REGISTERED_ETA,
            "selected_wave_indices": [list(wave) for wave in WAVE_ORDER],
            "positive_wave_representatives": [
                list(wave) for wave in POSITIVE_WAVES
            ],
            "mode_order": list(MODE_ORDER),
            "real_coordinate_order": (
                "positive-wave representative, mode, interleaved real/imaginary"
            ),
            "complex_lift_scale": float(
                1.0 / (np.sqrt(2.0) * REGISTERED_SIZE)
            ),
            "state_dimension": 2601,
            "reduced_dimension": REDUCED_DIMENSION,
            "pair_count": PAIR_COUNT,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "hessian_seed": HESSIAN_SEED,
            "residual_seed": RESIDUAL_SEED,
            "shadow_seed": SHADOW_SEED,
            "amplitudes": list(AMPLITUDES),
            "shadow_steps": 100,
        },
        "construction": {
            "chart_shape": {
                "base": list(model.chart.base.shape),
                "tangent": list(model.chart.tangent.shape),
                "hessian": list(model.chart.hessian.shape),
                "reduced_linear": list(model.reduced_linear.shape),
                "reduced_hessian": list(model.reduced_hessian.shape),
            },
            "diagnostics": diagnostics,
            "pair_records": list(model.pair_records),
        },
        "independent_hessian_check": hessian_check,
        "residual_order_campaign": residual_campaign,
        "shadowing_campaign": {
            "linear": linear_shadow,
            "quadratic": quadratic_shadow,
            "maximum_absolute_error_improvement_ratio": shadow_improvement,
        },
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "limitations": [
            (
                "This verifies one modified map on N=17 and does not establish an "
                "all-grid or grid-uniform invariant family."
            ),
            (
                "The sampled directions, amplitudes no larger than 0.01, and 100 "
                "steps do not certify the entire coordinate ball."
            ),
            (
                "A numerical candidate chart is not an existence or uniqueness "
                "theorem and does not transfer to the unfiltered BGK map."
            ),
        ],
        "next_change": next_change,
    }
