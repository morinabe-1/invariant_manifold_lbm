"""Sealed Q007f fixed-metric finite-radius normal-cocycle audit."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.sparse.linalg import LinearOperator, svds

from .adapted_metric import (
    AdaptedFourierMetric,
    build_adapted_fourier_metric,
    run_adapted_metric_audit,
)
from .cubic_chart import _array_hash
from .cubic_continuation import (
    _all_numeric_values_finite,
    _normalized_directions,
    _strict_json_serializable,
)
from .normal_cocycle import (
    AMPLITUDES,
    COCYCLE_DIRECTION_COUNT,
    COCYCLE_SEED,
    HORIZON,
    REGISTERED_COEFFICIENT_HASHES,
    FilteredBGKJacobian,
    FixedLeafProjector,
    _coefficient_reproduction,
    _direction_registration,
    _relative_norm,
)
from .quartic_chart import Full2DQuarticModel, build_full2d_quartic_model

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]

REGISTERED_DIRECTION_SHA256 = (
    "99861e73b9204938e254cbfc1c01a81de7be0bd6fed726ab131b26708c741424"
)
REGISTERED_METRIC_SHA256 = (
    "23a18bd5f281ad21874da17a3a28bfeb66b36c9170fdb57308ef0eb40ff5c5d5"
)
REGISTERED_WHITENING_SHA256 = (
    "acf2be2aaec50c3ffa19658325e7dad736a0bce438e3343a72527b96f27b196b"
)
REGISTERED_Q007D_EQUILIBRIUM_GAMMA = {
    1: 2.4223625220259515,
    10: 2.592215401693412,
}
REGISTERED_Q007E_EQUILIBRIUM_GAMMA = {
    1: 0.9988057257445229,
    10: 0.9796329537956986,
}
REGISTERED_Q007E_NORMAL_SINGULAR_VALUE = {
    1: 0.9820654543743582,
    10: 0.831552014305928,
}

ADAPTED_SVD_SEED = 20260908
DERIVATIVE_SEED = 20260909
DERIVATIVE_POINT_COUNT_PER_AMPLITUDE = 4
DERIVATIVE_DIRECTION_COUNT = 8
ADJOINT_PAIR_COUNT = 4
GEOMETRY_PROBE_COUNT = 4
DIFFERENCE_STEPS = (2.0e-5, 1.0e-5, 5.0e-6)
SVD_TOLERANCE = 1.0e-12
SVD_MAXIMUM_ITERATIONS = 5000

MAXIMUM_UPSTREAM_RELATIVE_ERROR = 1.0e-10
MAXIMUM_TRANSFORM_ROUNDTRIP_ERROR = 1.0e-10
MAXIMUM_TRANSFORM_IMAGINARY_LEAKAGE = 1.0e-10
MAXIMUM_MAP_DERIVATIVE_ERROR = 2.0e-8
MAXIMUM_ADJOINT_ERROR = 5.0e-12
MAXIMUM_PROJECTOR_RESIDUAL = 1.0e-11
MINIMUM_CHART_TANGENT_SINGULAR_VALUE = 1.0e-8
MAXIMUM_TANGENT_LEAKAGE = 1.0e-3
MINIMUM_TANGENT_COCYCLE_SINGULAR_VALUE = 1.0e-8
MAXIMUM_EQUILIBRIUM_BLOCKWISE_ERROR = 1.0e-8
MAXIMUM_TRIPLET_RESIDUAL = 1.0e-8
MAXIMUM_TWO_START_DISAGREEMENT = 1.0e-6
MAXIMUM_COORDINATE_GROWTH_FACTOR = 1.05


def _complex_columns(
    value: npt.ArrayLike,
    dimension: int,
) -> tuple[ComplexArray, bool]:
    array = np.asarray(value, dtype=np.complex128)
    if array.shape == (dimension,):
        return array[:, None], True
    if array.ndim == 2 and array.shape[0] == dimension:
        return array, False
    raise ValueError(
        f"adapted value must have shape ({dimension},) or ({dimension}, m)"
    )


def _restore_columns(value: ComplexArray, was_vector: bool) -> ComplexArray:
    return np.asarray(value[:, 0] if was_vector else value, dtype=np.complex128)


def _apply_real_linear_complex(
    action: Any,
    value: npt.ArrayLike,
) -> ComplexArray:
    array = np.asarray(value, dtype=np.complex128)
    return np.asarray(
        action(array.real) + 1j * action(array.imag),
        dtype=np.complex128,
    )


def _relative_scalar_error(observed: float, registered: float) -> float:
    return abs(float(observed) - float(registered)) / max(
        abs(float(registered)),
        np.finfo(float).eps,
    )


@dataclass(frozen=True)
class AdaptedMapJacobian:
    """The fixed-metric conjugate ``S J S^{-1}`` and its exact adjoint."""

    metric: AdaptedFourierMetric
    physical: FilteredBGKJacobian

    @property
    def dimension(self) -> int:
        return self.metric.dimension

    def matmat(self, value: npt.ArrayLike) -> ComplexArray:
        columns, was_vector = _complex_columns(value, self.dimension)
        physical = self.metric.inverse(columns)
        propagated = _apply_real_linear_complex(self.physical.matmat, physical)
        result = self.metric.forward(propagated)
        return _restore_columns(result, was_vector)

    def matvec(self, value: npt.ArrayLike) -> ComplexArray:
        return self.matmat(value)

    def rmatmat(self, value: npt.ArrayLike) -> ComplexArray:
        columns, was_vector = _complex_columns(value, self.dimension)
        physical_cotangent = self.metric.forward_adjoint(columns)
        propagated = _apply_real_linear_complex(
            self.physical.rmatmat,
            physical_cotangent,
        )
        result = self.metric.inverse_adjoint(propagated)
        return _restore_columns(result, was_vector)

    def rmatvec(self, value: npt.ArrayLike) -> ComplexArray:
        return self.rmatmat(value)


@dataclass(frozen=True)
class AdaptedTangentGeometry:
    """Metric-orthonormal chart tangent and its sampled normal projector."""

    basis: ComplexArray
    tangent_singular_values: Array
    diagnostics: dict[str, Any]

    @property
    def dimension(self) -> int:
        return int(self.basis.shape[0])

    def project_normal(self, value: npt.ArrayLike) -> ComplexArray:
        columns, was_vector = _complex_columns(value, self.dimension)
        result = columns - self.basis @ (self.basis.conj().T @ columns)
        return _restore_columns(result, was_vector)


def _tangent_geometry(
    metric: AdaptedFourierMetric,
    chart_jacobian: npt.ArrayLike,
    geometry_probes: ComplexArray,
    hermitian_left: ComplexArray,
    hermitian_right: ComplexArray,
) -> AdaptedTangentGeometry:
    derivative = np.asarray(chart_jacobian, dtype=np.float64)
    adapted_tangent = metric.forward(derivative)
    singular_values = np.linalg.svd(adapted_tangent, compute_uv=False)
    basis, _ = np.linalg.qr(adapted_tangent, mode="reduced")
    basis = np.asarray(basis, dtype=np.complex128)
    rank_threshold = (
        np.finfo(float).eps
        * max(adapted_tangent.shape)
        * float(singular_values[0])
    )
    numerical_rank = int(np.count_nonzero(singular_values > rank_threshold))
    provisional = AdaptedTangentGeometry(
        basis=basis,
        tangent_singular_values=np.asarray(singular_values, dtype=np.float64),
        diagnostics={},
    )
    projected = provisional.project_normal(geometry_probes)
    twice_projected = provisional.project_normal(projected)
    idempotency = _relative_norm(twice_projected - projected, projected)
    projected_left = provisional.project_normal(hermitian_left)
    projected_right = provisional.project_normal(hermitian_right)
    forward_inner = np.vdot(projected_left, hermitian_right)
    adjoint_inner = np.vdot(hermitian_left, projected_right)
    hermitian_scale = max(
        float(np.linalg.norm(projected_left) * np.linalg.norm(hermitian_right)),
        float(np.linalg.norm(hermitian_left) * np.linalg.norm(projected_right)),
        np.finfo(float).eps,
    )
    diagnostics = {
        "chart_tangent_numerical_rank": numerical_rank,
        "chart_tangent_rank_threshold": float(rank_threshold),
        "minimum_chart_tangent_singular_value": float(singular_values[-1]),
        "maximum_chart_tangent_singular_value": float(singular_values[0]),
        "q_orthogonality_residual": float(
            np.linalg.norm(
                basis.conj().T @ basis - np.eye(basis.shape[1]),
                ord=2,
            )
        ),
        "projector_idempotency_relative_residual": idempotency,
        "projector_hermitian_relative_residual": float(
            abs(forward_inner - adjoint_inner) / hermitian_scale
        ),
    }
    return AdaptedTangentGeometry(
        basis=basis,
        tangent_singular_values=np.asarray(singular_values, dtype=np.float64),
        diagnostics=diagnostics,
    )


def _normal_operator(
    jacobians: list[AdaptedMapJacobian],
    geometries: list[AdaptedTangentGeometry],
) -> LinearOperator:
    if len(geometries) != len(jacobians) + 1:
        raise ValueError("normal cocycle needs one more geometry than Jacobian")
    dimension = geometries[0].dimension

    def matmat(value: npt.ArrayLike) -> ComplexArray:
        result = geometries[0].project_normal(value)
        for step, jacobian in enumerate(jacobians):
            result = geometries[step + 1].project_normal(jacobian.matmat(result))
        return np.asarray(result, dtype=np.complex128)

    def rmatmat(value: npt.ArrayLike) -> ComplexArray:
        result = geometries[-1].project_normal(value)
        for step in reversed(range(len(jacobians))):
            result = geometries[step].project_normal(
                jacobians[step].rmatmat(result)
            )
        return np.asarray(result, dtype=np.complex128)

    return LinearOperator(
        shape=(dimension, dimension),
        matvec=matmat,
        rmatvec=rmatmat,
        matmat=matmat,
        rmatmat=rmatmat,
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
        v0=np.asarray(start, dtype=np.complex128),
        solver="arpack",
        return_singular_vectors=True,
    )
    singular_value = float(singular_values[0])
    left = np.asarray(u[:, 0], dtype=np.complex128)
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


def _two_start_largest_singular_value(
    operator: LinearOperator,
    primary_start: ComplexArray,
    secondary_start: ComplexArray,
) -> dict[str, Any]:
    primary = _largest_singular_triplet(operator, primary_start)
    secondary = _largest_singular_triplet(operator, secondary_start)
    disagreement = abs(
        primary["singular_value"] - secondary["singular_value"]
    ) / max(
        primary["singular_value"],
        secondary["singular_value"],
        np.finfo(float).eps,
    )
    return {
        "primary": primary,
        "secondary": secondary,
        "singular_value_relative_disagreement": float(disagreement),
        "maximum_triplet_relative_residual": max(
            primary["maximum_triplet_relative_residual"],
            secondary["maximum_triplet_relative_residual"],
        ),
    }


def _normalize_columns(value: npt.ArrayLike) -> ComplexArray:
    array = np.asarray(value, dtype=np.complex128)
    norms = np.linalg.norm(array, axis=0)
    if np.any(norms == 0.0):
        raise ValueError("registered validation direction has zero norm")
    return np.asarray(array / norms[None, :], dtype=np.complex128)


def _validation_directions(
    metric: AdaptedFourierMetric,
    leaf: FixedLeafProjector,
) -> dict[str, ComplexArray]:
    rng = np.random.default_rng(DERIVATIVE_SEED)
    physical_raw = rng.normal(
        size=(leaf.dimension, DERIVATIVE_DIRECTION_COUNT)
    )
    physical_leaf = leaf.project(physical_raw)
    real_directions = _normalize_columns(metric.forward(physical_leaf))
    adjoint_left = _normalize_columns(
        rng.normal(size=(metric.dimension, ADJOINT_PAIR_COUNT))
        + 1j * rng.normal(size=(metric.dimension, ADJOINT_PAIR_COUNT))
    )
    adjoint_right = _normalize_columns(
        rng.normal(size=(metric.dimension, ADJOINT_PAIR_COUNT))
        + 1j * rng.normal(size=(metric.dimension, ADJOINT_PAIR_COUNT))
    )
    geometry_probes = _normalize_columns(
        rng.normal(size=(metric.dimension, GEOMETRY_PROBE_COUNT))
        + 1j * rng.normal(size=(metric.dimension, GEOMETRY_PROBE_COUNT))
    )
    return {
        "physical_raw": np.asarray(physical_raw, dtype=np.complex128),
        "real_adapted": real_directions,
        "adjoint_left": adjoint_left,
        "adjoint_right": adjoint_right,
        "geometry_probes": geometry_probes,
    }


def _derivative_validation(
    model: Full2DQuarticModel,
    metric: AdaptedFourierMetric,
    directions: Array,
    validation_directions: dict[str, ComplexArray],
) -> dict[str, Any]:
    real_directions = validation_directions["real_adapted"]
    adjoint_left = validation_directions["adjoint_left"]
    adjoint_right = validation_directions["adjoint_right"]
    physical_directions_complex = metric.inverse(real_directions)
    physical_directions = np.asarray(
        physical_directions_complex.real,
        dtype=np.float64,
    )
    roundtrip = metric.forward(physical_directions)
    roundtrip_error = _relative_norm(roundtrip - real_directions, real_directions)
    imaginary_leakage = _relative_norm(
        physical_directions_complex.imag,
        physical_directions_complex,
    )

    points = [("equilibrium", None, np.zeros(model.reduced_dimension))]
    for amplitude in AMPLITUDES:
        points.extend(
            (
                f"amplitude_{amplitude:g}_direction_{direction_index}",
                direction_index,
                amplitude * directions[direction_index],
            )
            for direction_index in range(DERIVATIVE_POINT_COUNT_PER_AMPLITUDE)
        )

    point_records = []
    for identifier, direction_index, coordinates in points:
        state = model.chart_evaluate(coordinates)
        physical_jacobian = FilteredBGKJacobian.at_state(
            state,
            model.cubic.quadratic.omega,
            model.cubic.quadratic.eta,
        )
        jacobian = AdaptedMapJacobian(metric, physical_jacobian)
        analytic = jacobian.matmat(real_directions)
        direction_records = []
        for column in range(DERIVATIVE_DIRECTION_COUNT):
            step_errors = []
            physical_direction = physical_directions[:, column]
            for step in DIFFERENCE_STEPS:
                finite_difference = metric.forward(
                    (
                        model.cubic.quadratic.full_map(
                            state + step * physical_direction
                        )
                        - model.cubic.quadratic.full_map(
                            state - step * physical_direction
                        )
                    )
                    / (2.0 * step)
                )
                step_errors.append(
                    _relative_norm(
                        finite_difference - analytic[:, column],
                        analytic[:, column],
                    )
                )
            direction_records.append(
                {
                    "direction_index": column,
                    "step_relative_errors": step_errors,
                    "best_relative_error": min(step_errors),
                }
            )

        adjoint_records = []
        for pair_index in range(ADJOINT_PAIR_COUNT):
            left = adjoint_left[:, pair_index]
            right = adjoint_right[:, pair_index]
            forward = jacobian.matvec(left)
            adjoint = jacobian.rmatvec(right)
            forward_inner = np.vdot(forward, right)
            adjoint_inner = np.vdot(left, adjoint)
            scale = max(
                float(np.linalg.norm(forward) * np.linalg.norm(right)),
                float(np.linalg.norm(left) * np.linalg.norm(adjoint)),
                np.finfo(float).eps,
            )
            adjoint_records.append(
                {
                    "pair_index": pair_index,
                    "forward_inner_product": {
                        "real": float(forward_inner.real),
                        "imag": float(forward_inner.imag),
                    },
                    "adjoint_inner_product": {
                        "real": float(adjoint_inner.real),
                        "imag": float(adjoint_inner.imag),
                    },
                    "relative_error": float(
                        abs(forward_inner - adjoint_inner) / scale
                    ),
                }
            )
        point_records.append(
            {
                "point_identifier": identifier,
                "direction_index": direction_index,
                "coordinates": coordinates.tolist(),
                "map_direction_records": direction_records,
                "adjoint_pair_records": adjoint_records,
            }
        )

    all_direction_records = list(
        chain.from_iterable(
            record["map_direction_records"] for record in point_records
        )
    )
    all_adjoint_records = list(
        chain.from_iterable(
            record["adjoint_pair_records"] for record in point_records
        )
    )
    return {
        "seed": DERIVATIVE_SEED,
        "point_count": len(points),
        "points_per_amplitude": DERIVATIVE_POINT_COUNT_PER_AMPLITUDE,
        "real_direction_count_per_point": DERIVATIVE_DIRECTION_COUNT,
        "adjoint_pair_count_per_point": ADJOINT_PAIR_COUNT,
        "difference_steps": list(DIFFERENCE_STEPS),
        "direction_hashes": {
            name: _array_hash(value)
            for name, value in validation_directions.items()
        },
        "transform_roundtrip_relative_error": roundtrip_error,
        "transform_imaginary_leakage_relative_norm": imaginary_leakage,
        "point_records": point_records,
        "summary": {
            "maximum_best_map_relative_error": max(
                record["best_relative_error"]
                for record in all_direction_records
            ),
            "maximum_adjoint_inner_product_relative_error": max(
                record["relative_error"] for record in all_adjoint_records
            ),
        },
    }


def _trajectory_record(
    model: Full2DQuarticModel,
    metric: AdaptedFourierMetric,
    initial_coordinates: Array,
    validation_directions: dict[str, ComplexArray],
    *,
    identifier: str,
    amplitude: float,
    direction_index: int | None,
    direction: Array | None,
    primary_start: ComplexArray,
    secondary_start: ComplexArray,
) -> dict[str, Any]:
    coordinates = [np.asarray(initial_coordinates, dtype=np.float64)]
    for _ in range(HORIZON):
        coordinates.append(model.reduced_map(coordinates[-1]))
    states = [model.chart_evaluate(value) for value in coordinates]
    chart_jacobians = [model.chart_jacobian(value) for value in coordinates]
    geometries = [
        _tangent_geometry(
            metric,
            derivative,
            validation_directions["geometry_probes"],
            validation_directions["adjoint_left"],
            validation_directions["adjoint_right"],
        )
        for derivative in chart_jacobians
    ]
    jacobians = [
        AdaptedMapJacobian(
            metric,
            FilteredBGKJacobian.at_state(
                state,
                model.cubic.quadratic.omega,
                model.cubic.quadratic.eta,
            ),
        )
        for state in states[:-1]
    ]

    tangent_product = np.eye(model.reduced_dimension, dtype=np.complex128)
    tangent_blocks = []
    step_records = []
    for step, jacobian in enumerate(jacobians):
        propagated_tangent = jacobian.matmat(geometries[step].basis)
        tangent_block = (
            geometries[step + 1].basis.conj().T @ propagated_tangent
        )
        tangent_blocks.append(tangent_block)
        tangent_product = tangent_block @ tangent_product
        leakage = _relative_norm(
            geometries[step + 1].project_normal(propagated_tangent),
            propagated_tangent,
        )
        tangent_singular_values = np.linalg.svd(
            tangent_block,
            compute_uv=False,
        )
        step_records.append(
            {
                "step": step,
                "minimum_tangent_block_singular_value": float(
                    tangent_singular_values[-1]
                ),
                "maximum_tangent_block_singular_value": float(
                    tangent_singular_values[0]
                ),
                "relative_tangent_leakage": leakage,
            }
        )

    tangent_singular_values = np.linalg.svd(
        tangent_product,
        compute_uv=False,
    )
    normal_ten_step = _two_start_largest_singular_value(
        _normal_operator(jacobians, geometries),
        primary_start,
        secondary_start,
    )
    gamma_ten = normal_ten_step["primary"]["singular_value"] / max(
        float(tangent_singular_values[-1]),
        np.finfo(float).eps,
    )

    one_step_tangent_singular_values = np.linalg.svd(
        tangent_blocks[0],
        compute_uv=False,
    )
    one_step_normal = _largest_singular_triplet(
        _normal_operator(jacobians[:1], geometries[:2]),
        primary_start,
    )
    gamma_one = one_step_normal["singular_value"] / max(
        float(one_step_tangent_singular_values[-1]),
        np.finfo(float).eps,
    )

    initial_norm = float(np.linalg.norm(coordinates[0]))
    coordinate_norms = [float(np.linalg.norm(value)) for value in coordinates]
    coordinate_growth = (
        0.0 if initial_norm == 0.0 else max(coordinate_norms) / initial_norm
    )
    geometry_diagnostics = [geometry.diagnostics for geometry in geometries]
    projector_keys = (
        "q_orthogonality_residual",
        "projector_idempotency_relative_residual",
        "projector_hermitian_relative_residual",
    )
    equilibrium_blockwise_errors = None
    if amplitude == 0.0:
        equilibrium_blockwise_errors = {
            "horizon_1_normal_relative_error": _relative_scalar_error(
                one_step_normal["singular_value"],
                REGISTERED_Q007E_NORMAL_SINGULAR_VALUE[1],
            ),
            "horizon_10_normal_relative_error": _relative_scalar_error(
                normal_ten_step["primary"]["singular_value"],
                REGISTERED_Q007E_NORMAL_SINGULAR_VALUE[10],
            ),
            "horizon_1_gamma_relative_error": _relative_scalar_error(
                gamma_one,
                REGISTERED_Q007E_EQUILIBRIUM_GAMMA[1],
            ),
            "horizon_10_gamma_relative_error": _relative_scalar_error(
                gamma_ten,
                REGISTERED_Q007E_EQUILIBRIUM_GAMMA[10],
            ),
        }

    return {
        "trajectory_identifier": identifier,
        "amplitude": amplitude,
        "direction_index": direction_index,
        "direction": None if direction is None else direction.tolist(),
        "initial_coordinates": coordinates[0].tolist(),
        "coordinate_norms": coordinate_norms,
        "maximum_coordinate_growth_factor": coordinate_growth,
        "minimum_population": min(float(np.min(state)) for state in states),
        "step_records": step_records,
        "geometry_summary": {
            "point_count": len(geometries),
            "minimum_chart_tangent_singular_value": min(
                record["minimum_chart_tangent_singular_value"]
                for record in geometry_diagnostics
            ),
            "minimum_chart_tangent_rank": min(
                record["chart_tangent_numerical_rank"]
                for record in geometry_diagnostics
            ),
            **{
                f"maximum_{key}": max(
                    record[key] for record in geometry_diagnostics
                )
                for key in projector_keys
            },
        },
        "tangent_cocycle": {
            "minimum_singular_value": float(tangent_singular_values[-1]),
            "maximum_singular_value": float(tangent_singular_values[0]),
        },
        "normal_cocycle": normal_ten_step,
        "gamma_10": float(gamma_ten),
        "margin_1_minus_gamma_10": float(1.0 - gamma_ten),
        "one_step_diagnostic": {
            "minimum_tangent_singular_value": float(
                one_step_tangent_singular_values[-1]
            ),
            "maximum_tangent_singular_value": float(
                one_step_tangent_singular_values[0]
            ),
            "normal_singular_triplet": one_step_normal,
            "gamma_1": float(gamma_one),
        },
        "maximum_tangent_leakage": max(
            record["relative_tangent_leakage"] for record in step_records
        ),
        "equilibrium_blockwise_errors": equilibrium_blockwise_errors,
        "all_values_finite": bool(
            all(np.all(np.isfinite(value)) for value in coordinates)
            and all(np.all(np.isfinite(state)) for state in states)
            and all(np.all(np.isfinite(value)) for value in chart_jacobians)
            and all(np.all(np.isfinite(geometry.basis)) for geometry in geometries)
        ),
    }


def _cocycle_campaign(
    model: Full2DQuarticModel,
    metric: AdaptedFourierMetric,
    directions: Array,
    validation_directions: dict[str, ComplexArray],
) -> dict[str, Any]:
    rng = np.random.default_rng(ADAPTED_SVD_SEED)
    primary_start = rng.normal(size=metric.dimension) + 1j * rng.normal(
        size=metric.dimension
    )
    primary_start = np.asarray(
        primary_start / np.linalg.norm(primary_start),
        dtype=np.complex128,
    )
    secondary_start = np.roll(primary_start, 1)

    equilibrium = _trajectory_record(
        model,
        metric,
        np.zeros(model.reduced_dimension),
        validation_directions,
        identifier="equilibrium",
        amplitude=0.0,
        direction_index=None,
        direction=None,
        primary_start=primary_start,
        secondary_start=secondary_start,
    )
    amplitude_records = []
    for amplitude in AMPLITUDES:
        records = [
            _trajectory_record(
                model,
                metric,
                amplitude * direction,
                validation_directions,
                identifier=(
                    f"amplitude_{amplitude:g}_direction_{direction_index}"
                ),
                amplitude=amplitude,
                direction_index=direction_index,
                direction=direction,
                primary_start=primary_start,
                secondary_start=secondary_start,
            )
            for direction_index, direction in enumerate(directions)
        ]
        amplitude_records.append(
            {
                "amplitude": amplitude,
                "direction_count": len(records),
                "direction_records": records,
                "summary": {
                    "minimum_gamma_10": min(
                        record["gamma_10"] for record in records
                    ),
                    "maximum_gamma_10": max(
                        record["gamma_10"] for record in records
                    ),
                    "minimum_margin_1_minus_gamma_10": min(
                        record["margin_1_minus_gamma_10"] for record in records
                    ),
                    "minimum_gamma_1": min(
                        record["one_step_diagnostic"]["gamma_1"]
                        for record in records
                    ),
                    "maximum_gamma_1": max(
                        record["one_step_diagnostic"]["gamma_1"]
                        for record in records
                    ),
                    "gamma_10_failure_count": sum(
                        record["gamma_10"] >= 1.0 for record in records
                    ),
                },
            }
        )

    all_records = [
        equilibrium,
        *chain.from_iterable(
            record["direction_records"] for record in amplitude_records
        ),
    ]
    projector_keys = (
        "maximum_q_orthogonality_residual",
        "maximum_projector_idempotency_relative_residual",
        "maximum_projector_hermitian_relative_residual",
    )
    return {
        "seed": COCYCLE_SEED,
        "adapted_svd_seed": ADAPTED_SVD_SEED,
        "adapted_svd_primary_start_sha256": _array_hash(primary_start),
        "adapted_svd_secondary_start_rule": (
            "one-entry cyclic roll of primary start"
        ),
        "adapted_svd_secondary_start_sha256": _array_hash(secondary_start),
        "direction_count_per_amplitude": len(directions),
        "amplitudes": list(AMPLITUDES),
        "horizon": HORIZON,
        "starting_point_count": len(all_records),
        "equilibrium_control": equilibrium,
        "amplitude_records": amplitude_records,
        "summary": {
            "minimum_gamma_10": min(
                record["gamma_10"] for record in all_records
            ),
            "maximum_gamma_10": max(
                record["gamma_10"] for record in all_records
            ),
            "minimum_margin_1_minus_gamma_10": min(
                record["margin_1_minus_gamma_10"] for record in all_records
            ),
            "minimum_gamma_1": min(
                record["one_step_diagnostic"]["gamma_1"]
                for record in all_records
            ),
            "maximum_gamma_1": max(
                record["one_step_diagnostic"]["gamma_1"]
                for record in all_records
            ),
            "minimum_population": min(
                record["minimum_population"] for record in all_records
            ),
            "maximum_coordinate_growth_factor": max(
                record["maximum_coordinate_growth_factor"]
                for record in all_records
            ),
            "minimum_tangent_cocycle_singular_value": min(
                record["tangent_cocycle"]["minimum_singular_value"]
                for record in all_records
            ),
            "minimum_chart_tangent_singular_value": min(
                record["geometry_summary"][
                    "minimum_chart_tangent_singular_value"
                ]
                for record in all_records
            ),
            "minimum_chart_tangent_rank": min(
                record["geometry_summary"]["minimum_chart_tangent_rank"]
                for record in all_records
            ),
            "maximum_tangent_leakage": max(
                record["maximum_tangent_leakage"] for record in all_records
            ),
            "maximum_normal_triplet_relative_residual": max(
                record["normal_cocycle"]["maximum_triplet_relative_residual"]
                for record in all_records
            ),
            "maximum_normal_singular_value_relative_disagreement": max(
                record["normal_cocycle"][
                    "singular_value_relative_disagreement"
                ]
                for record in all_records
            ),
            "maximum_equilibrium_blockwise_relative_error": max(
                equilibrium["equilibrium_blockwise_errors"].values()
            ),
            **{
                key: max(
                    record["geometry_summary"][key]
                    for record in all_records
                )
                for key in projector_keys
            },
            "all_values_finite": all(
                record["all_values_finite"] for record in all_records
            ),
        },
    }


def run_adapted_finite_cocycle_audit() -> dict[str, Any]:
    """Run the preregistered Q007f fixed-metric finite-radius audit."""

    model = build_full2d_quartic_model()
    q007e = run_adapted_metric_audit(model=model)
    metric, metric_construction = build_adapted_fourier_metric()
    leaf = FixedLeafProjector.for_square_grid(model.size)
    directions = _normalized_directions(
        COCYCLE_SEED,
        COCYCLE_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    coefficient_reproduction = _coefficient_reproduction(model)
    direction_registration = _direction_registration(directions)
    validation_directions = _validation_directions(metric, leaf)
    derivative_validation = _derivative_validation(
        model,
        metric,
        directions,
        validation_directions,
    )
    campaign = _cocycle_campaign(
        model,
        metric,
        directions,
        validation_directions,
    )

    q007e_horizons = {
        record["horizon"]: record
        for record in q007e["adapted_svd_audit"]["horizon_records"]
    }
    q007e_gamma_errors = {
        horizon: _relative_scalar_error(
            q007e_horizons[horizon]["gamma"],
            REGISTERED_Q007E_EQUILIBRIUM_GAMMA[horizon],
        )
        for horizon in (1, 10)
    }
    q007d_gamma_errors = {
        horizon: _relative_scalar_error(
            q007e["q007d_reproduction"]["observed_equilibrium_gamma"][horizon],
            REGISTERED_Q007D_EQUILIBRIUM_GAMMA[horizon],
        )
        for horizon in (1, 10)
    }
    metric_summary = metric_construction["summary"]
    derivative_summary = derivative_validation["summary"]
    campaign_summary = campaign["summary"]
    maximum_projector_residual = max(
        campaign_summary["maximum_q_orthogonality_residual"],
        campaign_summary["maximum_projector_idempotency_relative_residual"],
        campaign_summary["maximum_projector_hermitian_relative_residual"],
    )

    serializable_probe = {
        "q007e": q007e,
        "coefficient_reproduction": coefficient_reproduction,
        "direction_registration": direction_registration,
        "derivative_validation": derivative_validation,
        "campaign": campaign,
    }
    all_finite = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)

    validity_gates = {
        "q007d_inputs_and_equilibrium_reproduction": {
            "value": {
                "coefficient_hashes_match": coefficient_reproduction["match"],
                "direction_sha256": direction_registration["direction_sha256"],
                "direction_count": direction_registration["direction_count"],
                "starting_point_count": campaign["starting_point_count"],
                "maximum_equilibrium_gamma_relative_error": max(
                    q007d_gamma_errors.values()
                ),
            },
            "threshold": {
                "coefficient_hashes_match": True,
                "direction_sha256": REGISTERED_DIRECTION_SHA256,
                "direction_count": COCYCLE_DIRECTION_COUNT,
                "starting_point_count": (
                    1 + len(AMPLITUDES) * COCYCLE_DIRECTION_COUNT
                ),
                "maximum_equilibrium_gamma_relative_error": (
                    MAXIMUM_UPSTREAM_RELATIVE_ERROR
                ),
            },
            "passed": bool(
                coefficient_reproduction["match"]
                and coefficient_reproduction["observed"]
                == REGISTERED_COEFFICIENT_HASHES
                and direction_registration["direction_sha256"]
                == REGISTERED_DIRECTION_SHA256
                and direction_registration["direction_count"]
                == COCYCLE_DIRECTION_COUNT
                and campaign["starting_point_count"]
                == 1 + len(AMPLITUDES) * COCYCLE_DIRECTION_COUNT
                and max(q007d_gamma_errors.values())
                <= MAXIMUM_UPSTREAM_RELATIVE_ERROR
            ),
        },
        "q007e_metric_reproduction": {
            "value": {
                "study_validity": q007e["study_validity"],
                "validity_gate_count": len(q007e["validity_gates"]),
                "all_validity_gates_passed": all(
                    gate["passed"]
                    for gate in q007e["validity_gates"].values()
                ),
                "metric_sha256": metric_summary["metric_sha256"],
                "whitening_sha256": metric_summary["whitening_sha256"],
                "maximum_equilibrium_gamma_relative_error": max(
                    q007e_gamma_errors.values()
                ),
            },
            "threshold": {
                "study_validity": "passed",
                "validity_gate_count": 8,
                "all_validity_gates_passed": True,
                "metric_sha256": REGISTERED_METRIC_SHA256,
                "whitening_sha256": REGISTERED_WHITENING_SHA256,
                "maximum_equilibrium_gamma_relative_error": (
                    MAXIMUM_UPSTREAM_RELATIVE_ERROR
                ),
            },
            "passed": bool(
                q007e["study_validity"] == "passed"
                and len(q007e["validity_gates"]) == 8
                and all(
                    gate["passed"]
                    for gate in q007e["validity_gates"].values()
                )
                and metric_summary["metric_sha256"]
                == REGISTERED_METRIC_SHA256
                and metric_summary["whitening_sha256"]
                == REGISTERED_WHITENING_SHA256
                and max(q007e_gamma_errors.values())
                <= MAXIMUM_UPSTREAM_RELATIVE_ERROR
            ),
        },
        "adapted_transform_derivative_and_adjoint": {
            "value": {
                "transform_roundtrip_relative_error": derivative_validation[
                    "transform_roundtrip_relative_error"
                ],
                "transform_imaginary_leakage_relative_norm": (
                    derivative_validation[
                        "transform_imaginary_leakage_relative_norm"
                    ]
                ),
                **derivative_summary,
            },
            "threshold": {
                "transform_roundtrip_relative_error": (
                    MAXIMUM_TRANSFORM_ROUNDTRIP_ERROR
                ),
                "transform_imaginary_leakage_relative_norm": (
                    MAXIMUM_TRANSFORM_IMAGINARY_LEAKAGE
                ),
                "maximum_best_map_relative_error": (
                    MAXIMUM_MAP_DERIVATIVE_ERROR
                ),
                "maximum_adjoint_inner_product_relative_error": (
                    MAXIMUM_ADJOINT_ERROR
                ),
            },
            "passed": bool(
                derivative_validation["transform_roundtrip_relative_error"]
                <= MAXIMUM_TRANSFORM_ROUNDTRIP_ERROR
                and derivative_validation[
                    "transform_imaginary_leakage_relative_norm"
                ]
                <= MAXIMUM_TRANSFORM_IMAGINARY_LEAKAGE
                and derivative_summary["maximum_best_map_relative_error"]
                <= MAXIMUM_MAP_DERIVATIVE_ERROR
                and derivative_summary[
                    "maximum_adjoint_inner_product_relative_error"
                ]
                <= MAXIMUM_ADJOINT_ERROR
            ),
        },
        "adapted_tangent_and_projector_geometry": {
            "value": {
                "minimum_chart_tangent_rank": campaign_summary[
                    "minimum_chart_tangent_rank"
                ],
                "minimum_chart_tangent_singular_value": campaign_summary[
                    "minimum_chart_tangent_singular_value"
                ],
                "maximum_projector_residual": maximum_projector_residual,
            },
            "threshold": {
                "minimum_chart_tangent_rank": model.reduced_dimension,
                "minimum_chart_tangent_singular_value": (
                    MINIMUM_CHART_TANGENT_SINGULAR_VALUE
                ),
                "maximum_projector_residual": MAXIMUM_PROJECTOR_RESIDUAL,
            },
            "passed": bool(
                campaign_summary["minimum_chart_tangent_rank"]
                == model.reduced_dimension
                and campaign_summary["minimum_chart_tangent_singular_value"]
                >= MINIMUM_CHART_TANGENT_SINGULAR_VALUE
                and maximum_projector_residual <= MAXIMUM_PROJECTOR_RESIDUAL
            ),
        },
        "matrix_free_adapted_normal_svd": {
            "value": {
                "maximum_equilibrium_blockwise_relative_error": (
                    campaign_summary[
                        "maximum_equilibrium_blockwise_relative_error"
                    ]
                ),
                "maximum_triplet_relative_residual": campaign_summary[
                    "maximum_normal_triplet_relative_residual"
                ],
                "maximum_two_start_disagreement": campaign_summary[
                    "maximum_normal_singular_value_relative_disagreement"
                ],
            },
            "threshold": {
                "maximum_equilibrium_blockwise_relative_error": (
                    MAXIMUM_EQUILIBRIUM_BLOCKWISE_ERROR
                ),
                "maximum_triplet_relative_residual": MAXIMUM_TRIPLET_RESIDUAL,
                "maximum_two_start_disagreement": (
                    MAXIMUM_TWO_START_DISAGREEMENT
                ),
            },
            "passed": bool(
                campaign_summary[
                    "maximum_equilibrium_blockwise_relative_error"
                ]
                <= MAXIMUM_EQUILIBRIUM_BLOCKWISE_ERROR
                and campaign_summary[
                    "maximum_normal_triplet_relative_residual"
                ]
                <= MAXIMUM_TRIPLET_RESIDUAL
                and campaign_summary[
                    "maximum_normal_singular_value_relative_disagreement"
                ]
                <= MAXIMUM_TWO_START_DISAGREEMENT
            ),
        },
        "trajectory_domain_and_serialization": {
            "value": {
                "starting_point_count": campaign["starting_point_count"],
                "minimum_population": campaign_summary["minimum_population"],
                "maximum_coordinate_growth_factor": campaign_summary[
                    "maximum_coordinate_growth_factor"
                ],
                "minimum_tangent_cocycle_singular_value": campaign_summary[
                    "minimum_tangent_cocycle_singular_value"
                ],
                "all_numeric_values_finite": all_finite,
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "starting_point_count": (
                    1 + len(AMPLITUDES) * COCYCLE_DIRECTION_COUNT
                ),
                "minimum_population_strictly_greater_than": 0.0,
                "maximum_coordinate_growth_factor": (
                    MAXIMUM_COORDINATE_GROWTH_FACTOR
                ),
                "minimum_tangent_cocycle_singular_value": (
                    MINIMUM_TANGENT_COCYCLE_SINGULAR_VALUE
                ),
                "all_numeric_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": bool(
                campaign["starting_point_count"]
                == 1 + len(AMPLITUDES) * COCYCLE_DIRECTION_COUNT
                and campaign_summary["minimum_population"] > 0.0
                and campaign_summary["maximum_coordinate_growth_factor"]
                <= MAXIMUM_COORDINATE_GROWTH_FACTOR
                and campaign_summary[
                    "minimum_tangent_cocycle_singular_value"
                ]
                >= MINIMUM_TANGENT_COCYCLE_SINGULAR_VALUE
                and all_finite
                and strict_json
            ),
        },
        "adapted_tangent_leakage": {
            "value": campaign_summary["maximum_tangent_leakage"],
            "threshold": MAXIMUM_TANGENT_LEAKAGE,
            "passed": campaign_summary["maximum_tangent_leakage"]
            <= MAXIMUM_TANGENT_LEAKAGE,
        },
    }

    amplitude_gates = {
        record["amplitude"]: record["summary"]["maximum_gamma_10"] < 1.0
        for record in campaign["amplitude_records"]
    }
    hypothesis_gates = {
        "equilibrium_adapted_gamma_10": {
            "value": campaign["equilibrium_control"]["gamma_10"],
            "threshold_strictly_less_than": 1.0,
            "passed": campaign["equilibrium_control"]["gamma_10"] < 1.0,
        },
        "amplitude_0p004_adapted_gamma_10": {
            "value": next(
                record["summary"]["maximum_gamma_10"]
                for record in campaign["amplitude_records"]
                if record["amplitude"] == 0.004
            ),
            "threshold_strictly_less_than": 1.0,
            "passed": amplitude_gates[0.004],
        },
        "amplitude_0p01_adapted_gamma_10": {
            "value": next(
                record["summary"]["maximum_gamma_10"]
                for record in campaign["amplitude_records"]
                if record["amplitude"] == 0.01
            ),
            "threshold_strictly_less_than": 1.0,
            "passed": amplitude_gates[0.01],
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not study_valid:
        outcome = "inconclusive"
        classification = (
            "registered fixed-metric finite-radius cocycle audit is inconclusive"
        )
        decision = (
            "Do not interpret the adapted normal ratios until every upstream, "
            "transform, derivative, geometry, SVD, and trajectory gate passes."
        )
        next_change = (
            "Diagnose the registered validity failure without changing the fixed "
            "metric or normal-dominance threshold."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "registered finite-sample adapted-metric projected normal-cocycle "
            "dominance observed"
        )
        decision = (
            "Proceed only to a separately preregistered Q007g a posteriori "
            "defect and derivative-variation audit."
        )
        next_change = (
            "Preregister Q007g finite-domain defect, inverse, and derivative-"
            "variation bounds before any invariant-manifold theorem claim."
        )
    else:
        outcome = "rejected"
        classification = (
            "registered finite-sample adapted-metric projected normal-cocycle "
            "dominance not observed"
        )
        decision = (
            "Do not retune this equilibrium-derived metric on the same finite-"
            "radius data."
        )
        next_change = (
            "Localize the registered radius and horizon failures without adding "
            "a metric candidate from these observations."
        )

    return {
        "question": (
            "Does the fixed Q007e equilibrium Fourier-Riesz Stein metric retain "
            "ten-step projected normal dominance on the same 33 Q007d starts?"
        ),
        "hypothesis": (
            "The adapted ten-step maximum projected-normal singular value is "
            "strictly smaller than the minimum adapted tangent-cocycle singular "
            "value at equilibrium and on all 32 registered finite-radius starts."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.cubic.quadratic.omega,
            "eta": model.cubic.quadratic.eta,
            "fixed_global_conservation_leaf": True,
            "real_reduced_dimension": model.reduced_dimension,
            "adapted_fixed_leaf_dimension": metric.dimension,
            "amplitudes": list(AMPLITUDES),
            "direction_count_per_amplitude": COCYCLE_DIRECTION_COUNT,
            "starting_point_count": (
                1 + len(AMPLITUDES) * COCYCLE_DIRECTION_COUNT
            ),
            "horizon": HORIZON,
            "metric_sha256": REGISTERED_METRIC_SHA256,
            "whitening_sha256": REGISTERED_WHITENING_SHA256,
            "metric_reestimated_at_finite_radius": False,
            "projector": (
                "fixed-metric orthogonal complement of the varying quartic "
                "chart tangent"
            ),
        },
        "q007e_reproduction": q007e,
        "coefficient_reproduction": coefficient_reproduction,
        "direction_registration": direction_registration,
        "derivative_validation": derivative_validation,
        "adapted_cocycle_campaign": campaign,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "preserved_prior_outcomes": {
            "q006h_equilibrium_spectral_gap_revised": False,
            "q007c1_radius_0p01_horizon_100_revised": False,
            "q007c2_shadow_domain_revised": False,
            "q007d_euclidean_rejection_revised": False,
            "q007e_equilibrium_acceptance_revised": False,
            "q008a_tt_svd_rejection_revised": False,
            "q008c_wave_qtt_rejection_revised": False,
        },
        "claim_boundary": (
            "The outcome is a same-direction comparative finite-sample diagnostic "
            "on one 17x17 grid, two radii, 16 directions per radius, and ten "
            "steps, using a fixed equilibrium metric and metric-orthogonal chart "
            "normal projector. It is not an independent holdout, full-ball, other-"
            "horizon, true invariant normal-bundle, grid-uniform normal-attraction, "
            "existence, or uniqueness theorem."
        ),
    }
