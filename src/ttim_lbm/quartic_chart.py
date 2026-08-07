"""Fourier-fiber quartic chart construction for the sealed Q007c1 audit."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement, permutations
from typing import Any

import numpy as np
import numpy.typing as npt

from .checkerboard_filter import filter_multiplier, filtered_fourier_symbol
from .cubic_chart import (
    Full2DCubicModel,
    _array_hash,
    _complex_record,
    _complex_vector_record,
    _filtered_quadratic_action,
    _relative_norm,
    build_full2d_cubic_model,
    cubic_fourier_derivative,
)
from .cubic_prequalification import _homological_operator, _permutation_multiplicity
from .d2q9 import D2Q9_VELOCITIES, conserved_moment_matrix, exact_uniform_hessian
from .full2d_chart import (
    MODE_ORDER,
    POSITIVE_WAVES,
    REDUCED_DIMENSION,
    _complex_coefficients,
    _filter_tensor,
    _phase_field,
    _selected_output_basis,
)
from .nonresonance import (
    NUMERICAL_RANK_MULTIPLIER,
    fixed_leaf_kinetic_restriction,
    wave_vector_from_index,
)
from .quartic_prequalification import REGISTERED_QUARTIC_COUNT

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]
IntegerArray = npt.NDArray[np.int64]
WaveIndex = tuple[int, int]


def quartic_fourier_derivative(
    first: npt.ArrayLike,
    second: npt.ArrayLike,
    third: npt.ArrayLike,
    fourth: npt.ArrayLike,
    output_wave: WaveIndex,
    size: int,
    omega: float,
    eta: float,
) -> ComplexArray:
    """Apply the analytic fourth derivative of the filtered D2Q9 map."""

    vectors = [
        np.asarray(value, dtype=np.complex128)
        for value in (first, second, third, fourth)
    ]
    if any(value.shape != (9,) for value in vectors):
        raise ValueError("quartic Fourier inputs must each have shape (9,)")
    moments = conserved_moment_matrix()
    conserved = [moments @ value for value in vectors]
    hessian = exact_uniform_hessian(1, 1)
    local = np.zeros(9, dtype=np.complex128)
    for density_pair in combinations(range(4), 2):
        momentum_pair = tuple(
            index for index in range(4) if index not in density_pair
        )
        local += (
            2.0
            * float(omega)
            * conserved[density_pair[0]][0]
            * conserved[density_pair[1]][0]
            * np.einsum(
                "qab,a,b->q",
                hessian,
                conserved[momentum_pair[0]],
                conserved[momentum_pair[1]],
            )
        )
    output_vector = wave_vector_from_index(output_wave, size)
    streaming_phase = np.exp(-1j * (D2Q9_VELOCITIES @ output_vector))
    return np.asarray(
        filter_multiplier(*output_vector, eta) * streaming_phase * local,
        dtype=np.complex128,
    )


def _dense_cubic_tensors(
    cubic: Full2DCubicModel,
) -> tuple[ComplexArray, ComplexArray]:
    count = len(cubic.modes)
    chart = np.zeros((count, count, count, 9), dtype=np.complex128)
    reduced = np.zeros((count, count, count, count), dtype=np.complex128)
    for triple_index, triple_array in enumerate(cubic.triple_indices):
        triple = tuple(int(value) for value in triple_array)
        for ordered in set(permutations(triple)):
            chart[ordered] = cubic.cubic_coefficients[triple_index]
            reduced[(slice(None), *ordered)] = cubic.reduced_cubic_coefficients[
                triple_index
            ]
    return chart, reduced


def _quartet_forcing(
    indices: tuple[int, int, int, int],
    modes: list[Any],
    complex_hessian: ComplexArray,
    complex_reduced_hessian: ComplexArray,
    dense_cubic: ComplexArray,
    dense_reduced_cubic: ComplexArray,
    output_wave: WaveIndex,
    size: int,
    omega: float,
    eta: float,
) -> tuple[ComplexArray, dict[str, float]]:
    direct = quartic_fourier_derivative(
        *(modes[index].right for index in indices),
        output_wave,
        size,
        omega,
        eta,
    )

    quadratic_cubic = np.zeros(9, dtype=np.complex128)
    reduced_hessian_cubic = np.zeros(9, dtype=np.complex128)
    for singleton_position in range(4):
        singleton = indices[singleton_position]
        triple = tuple(
            indices[position]
            for position in range(4)
            if position != singleton_position
        )
        quadratic_cubic += _filtered_quadratic_action(
            dense_cubic[triple],
            modes[singleton].right,
            output_wave,
            size,
            omega,
            eta,
        )
        reduced_hessian_cubic += modes[singleton].eigenvalue * np.einsum(
            "p,pq->q",
            dense_reduced_cubic[(slice(None), *triple)],
            complex_hessian[singleton],
        )

    pair_partitions = (
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    )
    quadratic_hessian = np.zeros(9, dtype=np.complex128)
    reduced_hessian_pair = np.zeros(9, dtype=np.complex128)
    for left_positions, right_positions in pair_partitions:
        left = tuple(indices[position] for position in left_positions)
        right = tuple(indices[position] for position in right_positions)
        quadratic_hessian += _filtered_quadratic_action(
            complex_hessian[left],
            complex_hessian[right],
            output_wave,
            size,
            omega,
            eta,
        )
        reduced_hessian_pair += np.einsum(
            "p,q,pqr->r",
            complex_reduced_hessian[(slice(None), *left)],
            complex_reduced_hessian[(slice(None), *right)],
            complex_hessian,
            optimize=True,
        )

    cubic_hessian = np.zeros(9, dtype=np.complex128)
    reduced_cubic_hessian = np.zeros(9, dtype=np.complex128)
    for hessian_positions in combinations(range(4), 2):
        linear_positions = tuple(
            position for position in range(4) if position not in hessian_positions
        )
        hessian_indices = tuple(indices[position] for position in hessian_positions)
        first_linear = indices[linear_positions[0]]
        second_linear = indices[linear_positions[1]]
        cubic_hessian += cubic_fourier_derivative(
            complex_hessian[hessian_indices],
            modes[first_linear].right,
            modes[second_linear].right,
            output_wave,
            size,
            omega,
            eta,
        )
        reduced_cubic_hessian += (
            modes[first_linear].eigenvalue
            * modes[second_linear].eigenvalue
            * np.einsum(
                "p,pq->q",
                complex_reduced_hessian[(slice(None), *hessian_indices)],
                dense_cubic[:, first_linear, second_linear],
            )
        )

    reduced_composition = (
        reduced_hessian_cubic
        + reduced_hessian_pair
        + reduced_cubic_hessian
    )
    forcing = (
        direct
        + quadratic_cubic
        + quadratic_hessian
        + cubic_hessian
        - reduced_composition
    )
    return np.asarray(forcing, dtype=np.complex128), {
        "direct_quartic_derivative_norm": float(np.linalg.norm(direct)),
        "quadratic_cubic_composition_norm": float(
            np.linalg.norm(quadratic_cubic)
        ),
        "quadratic_hessian_composition_norm": float(
            np.linalg.norm(quadratic_hessian)
        ),
        "cubic_hessian_composition_norm": float(np.linalg.norm(cubic_hessian)),
        "reduced_hessian_cubic_composition_norm": float(
            np.linalg.norm(reduced_hessian_cubic)
        ),
        "reduced_hessian_pair_composition_norm": float(
            np.linalg.norm(reduced_hessian_pair)
        ),
        "reduced_cubic_hessian_composition_norm": float(
            np.linalg.norm(reduced_cubic_hessian)
        ),
        "reduced_composition_norm": float(np.linalg.norm(reduced_composition)),
        "forcing_norm": float(np.linalg.norm(forcing)),
    }


def _solve_quartet(
    quartet_index: int,
    indices: tuple[int, int, int, int],
    modes: list[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    complex_hessian: ComplexArray,
    complex_reduced_hessian: ComplexArray,
    dense_cubic: ComplexArray,
    dense_reduced_cubic: ComplexArray,
    size: int,
    omega: float,
    eta: float,
) -> tuple[ComplexArray, ComplexArray, ComplexArray, WaveIndex, dict[str, Any]]:
    operator, output_wave, output_kind, invariance = _homological_operator(
        indices,
        modes,
        lookup,
        size,
        omega,
        eta,
    )
    forcing, forcing_norms = _quartet_forcing(
        indices,
        modes,
        complex_hessian,
        complex_reduced_hessian,
        dense_cubic,
        dense_reduced_cubic,
        output_wave,
        size,
        omega,
        eta,
    )
    reduced_output = np.zeros(len(modes), dtype=np.complex128)
    if output_kind == "zero_wave_kinetic":
        kinetic, _, _ = fixed_leaf_kinetic_restriction(omega)
        right_hand_side = -(kinetic.conj().T @ forcing)
    elif output_kind == "internal_selected":
        _, _, output_indices = _selected_output_basis(output_wave, modes, lookup)
        right_hand_side = np.concatenate(
            [-forcing, np.zeros(3, dtype=np.complex128)]
        )
    else:
        right_hand_side = -forcing

    solution, *_ = np.linalg.lstsq(operator, right_hand_side, rcond=None)
    if output_kind == "zero_wave_kinetic":
        coefficient = kinetic @ solution
    elif output_kind == "internal_selected":
        coefficient = solution[:9]
        reduced_output[output_indices] = solution[9:]
    else:
        coefficient = solution

    solve_relative_residual = _relative_norm(
        operator @ solution - right_hand_side,
        right_hand_side,
    )
    multiplier = complex(math.prod(modes[index].eigenvalue for index in indices))
    output_matrix = filtered_fourier_symbol(
        *wave_vector_from_index(output_wave, size),
        omega,
        eta,
    )
    lifted_reduced = np.zeros(9, dtype=np.complex128)
    graph_gauge_residual = 0.0
    if output_kind == "internal_selected":
        selected_right, selected_left, output_indices = _selected_output_basis(
            output_wave,
            modes,
            lookup,
        )
        lifted_reduced = selected_right @ reduced_output[output_indices]
        graph_gauge_residual = _relative_norm(
            selected_left @ coefficient,
            coefficient,
        )
    homological_equation = (
        output_matrix @ coefficient
        - multiplier * coefficient
        - lifted_reduced
        + forcing
    )
    homological_relative_residual = _relative_norm(
        homological_equation,
        forcing,
    )
    zero_wave_forcing_conservation_residual = 0.0
    zero_wave_coefficient_conservation_residual = 0.0
    if output_wave == (0, 0):
        moments = conserved_moment_matrix()
        zero_wave_forcing_conservation_residual = _relative_norm(
            moments @ forcing,
            forcing,
        )
        zero_wave_coefficient_conservation_residual = _relative_norm(
            moments @ coefficient,
            coefficient,
        )

    singular_values = np.linalg.svd(operator, compute_uv=False)
    rank_threshold = float(
        NUMERICAL_RANK_MULTIPLIER
        * np.finfo(float).eps
        * max(operator.shape)
        * singular_values[0]
    )
    rank = int(np.count_nonzero(singular_values > rank_threshold))
    numerically_singular = rank < operator.shape[1]
    condition_number = (
        None
        if numerically_singular
        else float(singular_values[0] / singular_values[-1])
    )
    record = {
        "quartet_identifier": f"q{quartet_index:05d}",
        "input_indices": list(indices),
        "input_modes": [modes[index].identifier for index in indices],
        "input_wave_indices": [list(modes[index].wave_index) for index in indices],
        "output_wave_index": list(output_wave),
        "output_kind": output_kind,
        "permutation_multiplicity": _permutation_multiplicity(indices),
        "multiplier_product": _complex_record(multiplier),
        "smallest_singular_value": float(singular_values[-1]),
        "operator_rank": rank,
        "operator_dimension": int(operator.shape[1]),
        "numerical_rank_threshold": rank_threshold,
        "numerically_singular": numerically_singular,
        "condition_number": condition_number,
        "solve_relative_residual": solve_relative_residual,
        "homological_relative_residual": homological_relative_residual,
        "graph_gauge_relative_residual": graph_gauge_residual,
        "zero_wave_forcing_conservation_relative_residual": (
            zero_wave_forcing_conservation_residual
        ),
        "zero_wave_coefficient_conservation_relative_residual": (
            zero_wave_coefficient_conservation_residual
        ),
        "fixed_leaf_subspace_invariance_residual": invariance,
        "coefficient_norm": float(np.linalg.norm(coefficient)),
        "reduced_coefficient_norm": float(np.linalg.norm(reduced_output)),
        **forcing_norms,
        "forcing": _complex_vector_record(forcing),
        "chart_coefficient": _complex_vector_record(coefficient),
        "reduced_coefficient": _complex_vector_record(reduced_output),
    }
    return (
        np.asarray(coefficient, dtype=np.complex128),
        np.asarray(reduced_output, dtype=np.complex128),
        forcing,
        output_wave,
        record,
    )


@dataclass(frozen=True)
class Full2DQuarticModel:
    """Q007b cubic model plus symmetric quartic Fourier fibers."""

    cubic: Full2DCubicModel
    coordinate_map: ComplexArray
    modes: tuple[Any, ...]
    lookup: dict[tuple[WaveIndex, str], int]
    quartet_indices: IntegerArray
    output_waves: IntegerArray
    multiplicities: IntegerArray
    quartic_coefficients: ComplexArray
    reduced_quartic_coefficients: ComplexArray
    forcing_coefficients: ComplexArray
    coefficient_records: tuple[dict[str, Any], ...]
    wave_groups: dict[WaveIndex, IntegerArray]
    phase_fields: dict[WaveIndex, ComplexArray]
    positive_mode_indices: IntegerArray
    coordinate_scale: float

    @property
    def size(self) -> int:
        return self.cubic.size

    @property
    def reduced_dimension(self) -> int:
        return self.cubic.reduced_dimension

    def _complex_coordinate_products(self, coordinates: npt.ArrayLike) -> ComplexArray:
        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("coordinate dimension does not match quartic chart")
        complex_coordinates = self.coordinate_map @ value
        products = np.prod(complex_coordinates[self.quartet_indices], axis=1)
        return np.asarray(self.multiplicities * products, dtype=np.complex128)

    def _complex_physical_field(
        self,
        coordinates: npt.ArrayLike,
        coefficients: ComplexArray,
    ) -> ComplexArray:
        products = self._complex_coordinate_products(coordinates)
        field = np.zeros((self.size, self.size, 9), dtype=np.complex128)
        for wave, group in self.wave_groups.items():
            coefficient = np.einsum(
                "t,tq->q",
                products[group],
                coefficients[group],
            )
            field += np.einsum(
                "xy,q->xyq",
                self.phase_fields[wave],
                coefficient,
            )
        return field

    def complex_quartic_field(self, coordinates: npt.ArrayLike) -> ComplexArray:
        return self._complex_physical_field(coordinates, self.quartic_coefficients)

    def quartic_chart_term(self, coordinates: npt.ArrayLike) -> Array:
        return np.asarray(
            self.complex_quartic_field(coordinates).real,
            dtype=np.float64,
        ).ravel()

    def complex_forcing_field(self, coordinates: npt.ArrayLike) -> ComplexArray:
        return self._complex_physical_field(coordinates, self.forcing_coefficients)

    def forcing_field(self, coordinates: npt.ArrayLike) -> Array:
        return np.asarray(
            self.complex_forcing_field(coordinates).real,
            dtype=np.float64,
        ).ravel()

    def complex_reduced_quartic_term(
        self,
        coordinates: npt.ArrayLike,
    ) -> ComplexArray:
        products = self._complex_coordinate_products(coordinates)
        return np.asarray(
            np.einsum(
                "t,tr->r",
                products,
                self.reduced_quartic_coefficients,
            ),
            dtype=np.complex128,
        )

    def reduced_quartic_term(self, coordinates: npt.ArrayLike) -> Array:
        complex_term = self.complex_reduced_quartic_term(coordinates)
        result = np.empty(self.reduced_dimension, dtype=np.float64)
        for coordinate, mode_index in enumerate(self.positive_mode_indices):
            if coordinate % 2 == 0:
                result[coordinate] = complex_term[mode_index].real / self.coordinate_scale
            else:
                result[coordinate] = complex_term[mode_index].imag / self.coordinate_scale
        return result

    def chart_evaluate(
        self,
        coordinates: npt.ArrayLike,
        *,
        quartic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        result = self.cubic.chart_evaluate(value, cubic=True)
        if quartic:
            result = result + self.quartic_chart_term(value) / 24.0
        return np.asarray(result, dtype=np.float64)

    def reduced_map(
        self,
        coordinates: npt.ArrayLike,
        *,
        quartic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        result = self.cubic.reduced_map(value, cubic=True)
        if quartic:
            result = result + self.reduced_quartic_term(value) / 24.0
        return np.asarray(result, dtype=np.float64)

    def invariance_defect(
        self,
        coordinates: npt.ArrayLike,
        *,
        quartic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        lifted = self.chart_evaluate(value, quartic=quartic)
        mapped = self.cubic.quadratic.full_map(lifted)
        predicted = self.chart_evaluate(
            self.reduced_map(value, quartic=quartic),
            quartic=quartic,
        )
        return mapped - predicted

    def analytic_map_fourth_action(self, direction: npt.ArrayLike) -> Array:
        value = np.asarray(direction, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("direction dimension does not match quartic chart")
        tangent_field = (self.cubic.quadratic.chart.tangent @ value).reshape(
            self.size,
            self.size,
            9,
        )
        conserved = np.einsum(
            "aq,xyq->xya",
            conserved_moment_matrix(),
            tangent_field,
        )
        local = (
            12.0
            * self.cubic.quadratic.omega
            * conserved[..., 0, None] ** 2
            * np.einsum(
                "qab,xya,xyb->xyq",
                exact_uniform_hessian(1, 1),
                conserved,
                conserved,
            )
        )
        streamed = np.empty_like(local)
        for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(int)):
            streamed[:, :, population] = np.roll(
                local[:, :, population],
                shift=(int(cy), int(cx)),
                axis=(0, 1),
            )
        return np.asarray(
            _filter_tensor(streamed, self.cubic.quadratic.eta),
            dtype=np.float64,
        ).ravel()

    def coefficient_hashes(self) -> dict[str, str]:
        return {
            "quartet_indices_sha256": _array_hash(self.quartet_indices),
            "output_waves_sha256": _array_hash(self.output_waves),
            "chart_coefficients_sha256": _array_hash(self.quartic_coefficients),
            "reduced_coefficients_sha256": _array_hash(
                self.reduced_quartic_coefficients
            ),
            "forcing_coefficients_sha256": _array_hash(self.forcing_coefficients),
        }


def build_full2d_quartic_model() -> Full2DQuarticModel:
    """Construct the preregistered Q007c1 symmetric quartic Fourier fibers."""

    cubic = build_full2d_cubic_model()
    size = cubic.size
    omega = cubic.quadratic.omega
    eta = cubic.quadratic.eta
    modes = list(cubic.modes)
    lookup = cubic.lookup
    complex_hessian, complex_reduced_hessian, _, _ = _complex_coefficients(
        modes,
        lookup,
        size,
        omega,
        eta,
    )
    dense_cubic, dense_reduced_cubic = _dense_cubic_tensors(cubic)
    quartets = list(combinations_with_replacement(range(len(modes)), 4))
    if len(quartets) != REGISTERED_QUARTIC_COUNT:
        raise RuntimeError("Q007c1 did not enumerate the registered 17,550 quartets")

    quartet_indices = np.asarray(quartets, dtype=np.int64)
    output_waves = np.empty((len(quartets), 2), dtype=np.int64)
    multiplicities = np.empty(len(quartets), dtype=np.int64)
    quartic_coefficients = np.empty((len(quartets), 9), dtype=np.complex128)
    reduced_quartic_coefficients = np.empty(
        (len(quartets), len(modes)),
        dtype=np.complex128,
    )
    forcing_coefficients = np.empty((len(quartets), 9), dtype=np.complex128)
    records = []
    for quartet_index, indices in enumerate(quartets):
        coefficient, reduced, forcing, output_wave, record = _solve_quartet(
            quartet_index,
            indices,
            modes,
            lookup,
            complex_hessian,
            complex_reduced_hessian,
            dense_cubic,
            dense_reduced_cubic,
            size,
            omega,
            eta,
        )
        quartic_coefficients[quartet_index] = coefficient
        reduced_quartic_coefficients[quartet_index] = reduced
        forcing_coefficients[quartet_index] = forcing
        output_waves[quartet_index] = output_wave
        multiplicities[quartet_index] = _permutation_multiplicity(indices)
        records.append(record)

    wave_groups = {
        tuple(int(value) for value in wave): np.flatnonzero(
            np.all(output_waves == wave, axis=1)
        )
        for wave in np.unique(output_waves, axis=0)
    }
    phase_fields = {wave: _phase_field(wave, size) for wave in wave_groups}
    positive_mode_indices = []
    for wave in POSITIVE_WAVES:
        for label in MODE_ORDER:
            mode_index = lookup[(wave, label)]
            positive_mode_indices.extend([mode_index, mode_index])
    if len(positive_mode_indices) != REDUCED_DIMENSION:
        raise RuntimeError("Q007c1 positive-mode realification has the wrong size")
    return Full2DQuarticModel(
        cubic=cubic,
        coordinate_map=cubic.coordinate_map,
        modes=tuple(modes),
        lookup=lookup,
        quartet_indices=quartet_indices,
        output_waves=output_waves,
        multiplicities=multiplicities,
        quartic_coefficients=quartic_coefficients,
        reduced_quartic_coefficients=reduced_quartic_coefficients,
        forcing_coefficients=forcing_coefficients,
        coefficient_records=tuple(records),
        wave_groups=wave_groups,
        phase_fields=phase_fields,
        positive_mode_indices=np.asarray(positive_mode_indices, dtype=np.int64),
        coordinate_scale=cubic.coordinate_scale,
    )
