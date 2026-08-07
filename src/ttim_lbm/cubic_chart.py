"""Fourier-fiber cubic chart construction for the sealed Q007b audit."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations_with_replacement
from typing import Any

import numpy as np
import numpy.typing as npt

from .checkerboard_filter import filter_multiplier, filtered_fourier_symbol
from .cubic_prequalification import _homological_operator
from .d2q9 import (
    D2Q9_VELOCITIES,
    conserved_moment_matrix,
    exact_uniform_hessian,
)
from .full2d_chart import (
    MODE_ORDER,
    POSITIVE_WAVES,
    REDUCED_DIMENSION,
    REGISTERED_ETA,
    REGISTERED_OMEGA,
    REGISTERED_SIZE,
    Full2DQuadraticModel,
    _build_complex_modes,
    _complex_coefficients,
    _coordinate_map,
    _filter_tensor,
    _phase_field,
    _selected_output_basis,
    build_full2d_quadratic_model,
)
from .nonresonance import (
    NUMERICAL_RANK_MULTIPLIER,
    fixed_leaf_kinetic_restriction,
    quadratic_fourier_forcing,
    wave_vector_from_index,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]
IntegerArray = npt.NDArray[np.int64]
WaveIndex = tuple[int, int]

REGISTERED_TRIPLE_COUNT = 2600


def _array_hash(value: npt.ArrayLike) -> str:
    array = np.ascontiguousarray(np.asarray(value))
    digest = sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(str(array.shape).encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _complex_vector_record(value: npt.ArrayLike) -> dict[str, list[float]]:
    array = np.asarray(value, dtype=np.complex128)
    return {"real": array.real.tolist(), "imag": array.imag.tolist()}


def _relative_norm(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).eps)
    )


def _permutation_multiplicity(indices: tuple[int, int, int]) -> int:
    if indices[0] == indices[2]:
        return 1
    if indices[0] == indices[1] or indices[1] == indices[2]:
        return 3
    return 6


def _filtered_quadratic_action(
    left: npt.ArrayLike,
    right: npt.ArrayLike,
    output_wave: WaveIndex,
    size: int,
    omega: float,
    eta: float,
) -> ComplexArray:
    output_vector = wave_vector_from_index(output_wave, size)
    return np.asarray(
        filter_multiplier(*output_vector, eta)
        * quadratic_fourier_forcing(left, right, output_vector, omega),
        dtype=np.complex128,
    )


def cubic_fourier_derivative(
    first: npt.ArrayLike,
    second: npt.ArrayLike,
    third: npt.ArrayLike,
    output_wave: WaveIndex,
    size: int = REGISTERED_SIZE,
    omega: float = REGISTERED_OMEGA,
    eta: float = REGISTERED_ETA,
) -> ComplexArray:
    """Apply the analytic third derivative of the filtered D2Q9 map."""

    vectors = [
        np.asarray(value, dtype=np.complex128)
        for value in (first, second, third)
    ]
    if any(value.shape != (9,) for value in vectors):
        raise ValueError("cubic Fourier inputs must each have shape (9,)")
    moments = conserved_moment_matrix()
    conserved = [moments @ value for value in vectors]
    hessian = exact_uniform_hessian(1, 1)
    local = -float(omega) * (
        conserved[0][0]
        * np.einsum("qab,a,b->q", hessian, conserved[1], conserved[2])
        + conserved[1][0]
        * np.einsum("qab,a,b->q", hessian, conserved[0], conserved[2])
        + conserved[2][0]
        * np.einsum("qab,a,b->q", hessian, conserved[0], conserved[1])
    )
    output_vector = wave_vector_from_index(output_wave, size)
    streaming_phase = np.exp(-1j * (D2Q9_VELOCITIES @ output_vector))
    return np.asarray(
        filter_multiplier(*output_vector, eta) * streaming_phase * local,
        dtype=np.complex128,
    )


def _reduced_composition_action(
    indices: tuple[int, int, int],
    complex_hessian: ComplexArray,
    complex_reduced_hessian: ComplexArray,
    modes: list[Any],
) -> ComplexArray:
    first, second, third = indices
    terms = (
        (first, second, third),
        (first, third, second),
        (second, third, first),
    )
    result = np.zeros(9, dtype=np.complex128)
    for left, right, linear_index in terms:
        reduced = complex_reduced_hessian[:, left, right]
        result += modes[linear_index].eigenvalue * np.einsum(
            "pq,p->q",
            complex_hessian[:, linear_index],
            reduced,
        )
    return result


def _triple_forcing(
    indices: tuple[int, int, int],
    modes: list[Any],
    complex_hessian: ComplexArray,
    complex_reduced_hessian: ComplexArray,
    output_wave: WaveIndex,
    size: int,
    omega: float,
    eta: float,
) -> tuple[ComplexArray, dict[str, float]]:
    first, second, third = indices
    direct = cubic_fourier_derivative(
        modes[first].right,
        modes[second].right,
        modes[third].right,
        output_wave,
        size,
        omega,
        eta,
    )
    mixed = (
        _filtered_quadratic_action(
            complex_hessian[first, second],
            modes[third].right,
            output_wave,
            size,
            omega,
            eta,
        )
        + _filtered_quadratic_action(
            complex_hessian[first, third],
            modes[second].right,
            output_wave,
            size,
            omega,
            eta,
        )
        + _filtered_quadratic_action(
            complex_hessian[second, third],
            modes[first].right,
            output_wave,
            size,
            omega,
            eta,
        )
    )
    reduced_composition = _reduced_composition_action(
        indices,
        complex_hessian,
        complex_reduced_hessian,
        modes,
    )
    forcing = direct + mixed - reduced_composition
    return np.asarray(forcing, dtype=np.complex128), {
        "direct_cubic_derivative_norm": float(np.linalg.norm(direct)),
        "mixed_quadratic_norm": float(np.linalg.norm(mixed)),
        "reduced_composition_norm": float(np.linalg.norm(reduced_composition)),
        "forcing_norm": float(np.linalg.norm(forcing)),
    }


def _solve_triple(
    triple_index: int,
    indices: tuple[int, int, int],
    modes: list[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    complex_hessian: ComplexArray,
    complex_reduced_hessian: ComplexArray,
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
    forcing, forcing_norms = _triple_forcing(
        indices,
        modes,
        complex_hessian,
        complex_reduced_hessian,
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
        _, _, output_indices = _selected_output_basis(
            output_wave,
            modes,
            lookup,
        )
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
    multiplier = complex(
        modes[indices[0]].eigenvalue
        * modes[indices[1]].eigenvalue
        * modes[indices[2]].eigenvalue
    )
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
        "triple_identifier": f"t{triple_index:05d}",
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
class Full2DCubicModel:
    """Q006i quadratic model plus symmetric cubic Fourier fibers."""

    quadratic: Full2DQuadraticModel
    coordinate_map: ComplexArray
    modes: tuple[Any, ...]
    lookup: dict[tuple[WaveIndex, str], int]
    triple_indices: IntegerArray
    output_waves: IntegerArray
    multiplicities: IntegerArray
    cubic_coefficients: ComplexArray
    reduced_cubic_coefficients: ComplexArray
    forcing_coefficients: ComplexArray
    coefficient_records: tuple[dict[str, Any], ...]
    wave_groups: dict[WaveIndex, IntegerArray]
    phase_fields: dict[WaveIndex, ComplexArray]
    positive_mode_indices: IntegerArray
    coordinate_scale: float

    @property
    def size(self) -> int:
        return self.quadratic.size

    @property
    def reduced_dimension(self) -> int:
        return self.quadratic.reduced_dimension

    def _complex_coordinate_products(self, coordinates: npt.ArrayLike) -> ComplexArray:
        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("coordinate dimension does not match cubic chart")
        complex_coordinates = self.coordinate_map @ value
        products = (
            complex_coordinates[self.triple_indices[:, 0]]
            * complex_coordinates[self.triple_indices[:, 1]]
            * complex_coordinates[self.triple_indices[:, 2]]
        )
        return np.asarray(self.multiplicities * products, dtype=np.complex128)

    def _triple_mask(self, triple_mask: npt.ArrayLike | None) -> npt.NDArray[np.bool_]:
        if triple_mask is None:
            return np.ones(len(self.triple_indices), dtype=bool)
        mask = np.asarray(triple_mask)
        if mask.dtype == bool:
            if mask.shape != (len(self.triple_indices),):
                raise ValueError("boolean cubic triple mask has the wrong shape")
            return np.asarray(mask, dtype=bool)
        if mask.ndim != 1 or not np.issubdtype(mask.dtype, np.integer):
            raise ValueError("cubic triple selection must be a boolean mask or indices")
        if np.any(mask < 0) or np.any(mask >= len(self.triple_indices)):
            raise ValueError("cubic triple index is out of range")
        result = np.zeros(len(self.triple_indices), dtype=bool)
        result[np.asarray(mask, dtype=np.int64)] = True
        return result

    def complex_cubic_field(
        self,
        coordinates: npt.ArrayLike,
        *,
        triple_mask: npt.ArrayLike | None = None,
    ) -> ComplexArray:
        products = self._complex_coordinate_products(coordinates)
        selected = self._triple_mask(triple_mask)
        field = np.zeros((self.size, self.size, 9), dtype=np.complex128)
        for wave, group in self.wave_groups.items():
            active = group[selected[group]]
            if len(active) == 0:
                continue
            coefficient = np.einsum(
                "t,tq->q",
                products[active],
                self.cubic_coefficients[active],
            )
            field += np.einsum(
                "xy,q->xyq",
                self.phase_fields[wave],
                coefficient,
            )
        return field

    def cubic_chart_term(
        self,
        coordinates: npt.ArrayLike,
        *,
        triple_mask: npt.ArrayLike | None = None,
    ) -> Array:
        return np.asarray(
            self.complex_cubic_field(
                coordinates,
                triple_mask=triple_mask,
            ).real,
            dtype=np.float64,
        ).ravel()

    def complex_reduced_cubic_term(
        self,
        coordinates: npt.ArrayLike,
        *,
        triple_mask: npt.ArrayLike | None = None,
    ) -> ComplexArray:
        products = self._complex_coordinate_products(coordinates)
        selected = self._triple_mask(triple_mask)
        return np.asarray(
            np.einsum(
                "t,tr->r",
                products[selected],
                self.reduced_cubic_coefficients[selected],
            ),
            dtype=np.complex128,
        )

    def reduced_cubic_term(
        self,
        coordinates: npt.ArrayLike,
        *,
        triple_mask: npt.ArrayLike | None = None,
    ) -> Array:
        complex_term = self.complex_reduced_cubic_term(
            coordinates,
            triple_mask=triple_mask,
        )
        result = np.empty(self.reduced_dimension, dtype=np.float64)
        for coordinate, mode_index in enumerate(self.positive_mode_indices):
            if coordinate % 2 == 0:
                result[coordinate] = complex_term[mode_index].real / self.coordinate_scale
            else:
                result[coordinate] = complex_term[mode_index].imag / self.coordinate_scale
        return result

    def complex_cubic_jacobian_field(
        self,
        coordinates: npt.ArrayLike,
        *,
        triple_mask: npt.ArrayLike | None = None,
    ) -> ComplexArray:
        """Differentiate ``T[a,a,a]`` with respect to all real coordinates."""

        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("coordinate dimension does not match cubic chart")
        complex_coordinates = self.coordinate_map @ value
        first = self.triple_indices[:, 0]
        second = self.triple_indices[:, 1]
        third = self.triple_indices[:, 2]
        derivative_products = self.multiplicities[:, None] * (
            self.coordinate_map[first]
            * complex_coordinates[second, None]
            * complex_coordinates[third, None]
            + complex_coordinates[first, None]
            * self.coordinate_map[second]
            * complex_coordinates[third, None]
            + complex_coordinates[first, None]
            * complex_coordinates[second, None]
            * self.coordinate_map[third]
        )
        selected = self._triple_mask(triple_mask)
        field = np.zeros(
            (self.size, self.size, 9, self.reduced_dimension),
            dtype=np.complex128,
        )
        for wave, group in self.wave_groups.items():
            active = group[selected[group]]
            if len(active) == 0:
                continue
            coefficient = np.einsum(
                "tr,tq->qr",
                derivative_products[active],
                self.cubic_coefficients[active],
            )
            field += np.einsum(
                "xy,qr->xyqr",
                self.phase_fields[wave],
                coefficient,
            )
        return field

    def chart_jacobian(self, coordinates: npt.ArrayLike) -> Array:
        """Evaluate the analytic physical-by-reduced Jacobian of ``W3``."""

        value = np.asarray(coordinates, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("coordinate dimension does not match cubic chart")
        quadratic = np.einsum(
            "ijk,j->ik",
            self.quadratic.chart.hessian,
            value,
        )
        cubic = self.complex_cubic_jacobian_field(value).real.reshape(
            self.quadratic.chart.base.size,
            self.reduced_dimension,
        )
        return np.asarray(
            self.quadratic.chart.tangent + quadratic + cubic / 6.0,
            dtype=np.float64,
        )

    def chart_jacobian_action(
        self,
        coordinates: npt.ArrayLike,
        direction: npt.ArrayLike,
    ) -> Array:
        """Apply the analytic cubic-chart Jacobian to one real direction."""

        value = np.asarray(direction, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("direction dimension does not match cubic chart")
        return np.asarray(self.chart_jacobian(coordinates) @ value, dtype=np.float64)

    def chart_evaluate(
        self,
        coordinates: npt.ArrayLike,
        *,
        cubic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        result = self.quadratic.chart.evaluate(value)
        if cubic:
            result = result + self.cubic_chart_term(value) / 6.0
        return np.asarray(result, dtype=np.float64)

    def reduced_map(
        self,
        coordinates: npt.ArrayLike,
        *,
        cubic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        result = self.quadratic.reduced_map(value, quadratic=True)
        if cubic:
            result = result + self.reduced_cubic_term(value) / 6.0
        return np.asarray(result, dtype=np.float64)

    def invariance_defect(
        self,
        coordinates: npt.ArrayLike,
        *,
        cubic: bool = True,
    ) -> Array:
        value = np.asarray(coordinates, dtype=np.float64)
        lifted = self.chart_evaluate(value, cubic=cubic)
        mapped = self.quadratic.full_map(lifted)
        predicted = self.chart_evaluate(
            self.reduced_map(value, cubic=cubic),
            cubic=cubic,
        )
        return mapped - predicted

    def analytic_map_third_action(self, direction: npt.ArrayLike) -> Array:
        value = np.asarray(direction, dtype=np.float64)
        if value.shape != (self.reduced_dimension,):
            raise ValueError("direction dimension does not match cubic chart")
        tangent_field = (self.quadratic.chart.tangent @ value).reshape(
            self.size,
            self.size,
            9,
        )
        conserved = np.einsum(
            "aq,xyq->xya",
            conserved_moment_matrix(),
            tangent_field,
        )
        local = -3.0 * self.quadratic.omega * conserved[..., 0, None] * np.einsum(
            "qab,xya,xyb->xyq",
            exact_uniform_hessian(1, 1),
            conserved,
            conserved,
        )
        streamed = np.empty_like(local)
        for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(int)):
            streamed[:, :, population] = np.roll(
                local[:, :, population],
                shift=(int(cy), int(cx)),
                axis=(0, 1),
            )
        return np.asarray(
            _filter_tensor(streamed, self.quadratic.eta),
            dtype=np.float64,
        ).ravel()

    def coefficient_hashes(self) -> dict[str, str]:
        return {
            "triple_indices_sha256": _array_hash(self.triple_indices),
            "output_waves_sha256": _array_hash(self.output_waves),
            "chart_coefficients_sha256": _array_hash(self.cubic_coefficients),
            "reduced_coefficients_sha256": _array_hash(
                self.reduced_cubic_coefficients
            ),
            "forcing_coefficients_sha256": _array_hash(self.forcing_coefficients),
        }


def build_full2d_cubic_model() -> Full2DCubicModel:
    """Construct the preregistered Q007b symmetric cubic Fourier fibers."""

    quadratic = build_full2d_quadratic_model()
    size = quadratic.size
    omega = quadratic.omega
    eta = quadratic.eta
    modes, lookup = _build_complex_modes(size, omega, eta)
    coordinate_map = _coordinate_map(modes, lookup, size)
    complex_hessian, complex_reduced_hessian, _, _ = _complex_coefficients(
        modes,
        lookup,
        size,
        omega,
        eta,
    )
    triples = list(combinations_with_replacement(range(len(modes)), 3))
    if len(triples) != REGISTERED_TRIPLE_COUNT:
        raise RuntimeError("Q007b did not enumerate the registered 2,600 triples")
    triple_indices = np.asarray(triples, dtype=np.int64)
    output_waves = np.empty((len(triples), 2), dtype=np.int64)
    multiplicities = np.empty(len(triples), dtype=np.int64)
    cubic_coefficients = np.empty((len(triples), 9), dtype=np.complex128)
    reduced_cubic_coefficients = np.empty(
        (len(triples), len(modes)),
        dtype=np.complex128,
    )
    forcing_coefficients = np.empty((len(triples), 9), dtype=np.complex128)
    records = []
    for triple_index, indices in enumerate(triples):
        coefficient, reduced, forcing, output_wave, record = _solve_triple(
            triple_index,
            indices,
            modes,
            lookup,
            complex_hessian,
            complex_reduced_hessian,
            size,
            omega,
            eta,
        )
        cubic_coefficients[triple_index] = coefficient
        reduced_cubic_coefficients[triple_index] = reduced
        forcing_coefficients[triple_index] = forcing
        output_waves[triple_index] = output_wave
        multiplicities[triple_index] = _permutation_multiplicity(indices)
        records.append(record)

    wave_groups = {
        tuple(int(value) for value in wave): np.flatnonzero(
            np.all(output_waves == wave, axis=1)
        )
        for wave in np.unique(output_waves, axis=0)
    }
    phase_fields = {
        wave: _phase_field(wave, size) for wave in wave_groups
    }
    positive_mode_indices = []
    for wave in POSITIVE_WAVES:
        for label in MODE_ORDER:
            mode_index = lookup[(wave, label)]
            positive_mode_indices.extend([mode_index, mode_index])
    if len(positive_mode_indices) != REDUCED_DIMENSION:
        raise RuntimeError("Q007b positive-mode realification has the wrong size")
    return Full2DCubicModel(
        quadratic=quadratic,
        coordinate_map=coordinate_map,
        modes=tuple(modes),
        lookup=lookup,
        triple_indices=triple_indices,
        output_waves=output_waves,
        multiplicities=multiplicities,
        cubic_coefficients=cubic_coefficients,
        reduced_cubic_coefficients=reduced_cubic_coefficients,
        forcing_coefficients=forcing_coefficients,
        coefficient_records=tuple(records),
        wave_groups=wave_groups,
        phase_fields=phase_fields,
        positive_mode_indices=np.asarray(positive_mode_indices, dtype=np.int64),
        coordinate_scale=1.0 / (np.sqrt(2.0) * size),
    )
