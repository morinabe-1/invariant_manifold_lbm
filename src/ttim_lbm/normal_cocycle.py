"""Sealed Q007d finite-radius projected tangent/normal cocycle audit."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import chain
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy.sparse.linalg import LinearOperator, svds

from .cubic_chart import _array_hash
from .cubic_continuation import (
    _all_numeric_values_finite,
    _normalized_directions,
    _strict_json_serializable,
)
from .d2q9 import D2Q9_VELOCITIES, D2Q9_WEIGHTS, conserved_moment_matrix, macroscopic
from .full2d_chart import MODE_ORDER
from .quartic_chart import Full2DQuarticModel, build_full2d_quartic_model
from .quartic_shadow_radius import (
    SHADOW_DOMAIN_DIRECTION_COUNT,
    SHADOW_DOMAIN_SEED,
    _reference_direction_groups,
)
from .tt_storage_prequalification import (
    ACTION_DIRECTION_COUNT as Q008A_ACTION_DIRECTION_COUNT,
)
from .tt_storage_prequalification import ACTION_SEED as Q008A_ACTION_SEED
from .tt_storage_prequalification import (
    TIMING_DIRECTION_COUNT as Q008A_TIMING_DIRECTION_COUNT,
)
from .tt_storage_prequalification import TIMING_SEED as Q008A_TIMING_SEED
from .wave_qtt_prequalification import (
    ACTION_DIRECTION_COUNT as Q008C_ACTION_DIRECTION_COUNT,
)
from .wave_qtt_prequalification import ACTION_SEED as Q008C_ACTION_SEED
from .wave_qtt_prequalification import (
    TIMING_DIRECTION_COUNT as Q008C_TIMING_DIRECTION_COUNT,
)
from .wave_qtt_prequalification import TIMING_SEED as Q008C_TIMING_SEED

Array = npt.NDArray[np.float64]

REGISTERED_COEFFICIENT_HASHES = {
    "mode_table_sha256": (
        "6e08a2706a44965143944b692615c6a8525799d3e01ca06a636d852d6610d4d9"
    ),
    "quadratic_chart_hessian_sha256": (
        "3f26eadcc6d25514671d9b741c53df5cf87c0dc598d0ff1cf9b9fd19f47d412f"
    ),
    "quadratic_reduced_hessian_sha256": (
        "61f5f3a9663a29022e1b41f56df0a6408d93d770a2821d012ba1974954645da5"
    ),
    "cubic_triple_indices_sha256": (
        "e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c"
    ),
    "cubic_output_waves_sha256": (
        "d431bfabad714d9d7ee9d8bfaf779eb2362ab27c916740494a379610c1389a6f"
    ),
    "cubic_chart_coefficients_sha256": (
        "ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b"
    ),
    "cubic_reduced_coefficients_sha256": (
        "4ca5a953833d5913f160e9fc36061e31697c7531865c4ef06d7517898f7c597e"
    ),
    "cubic_forcing_coefficients_sha256": (
        "6e2559a194d2b1e6a96f01653c1bccbe1852db00233700e16b3b980ae96df8eb"
    ),
    "quartic_quartet_indices_sha256": (
        "968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16"
    ),
    "quartic_output_waves_sha256": (
        "9f9720e1114cc489ef7bbca81562e7d4cf211999e8d4a4958c06c02ee0df1fe8"
    ),
    "quartic_chart_coefficients_sha256": (
        "9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b"
    ),
    "quartic_reduced_coefficients_sha256": (
        "061cd66caf83850a45eeec05ed0f62fafb748a3076d7a6eb591bc69be2e008f7"
    ),
    "quartic_forcing_coefficients_sha256": (
        "6ab2337ea60b87dbe404e1aeb6b9c090fa8f950d43815966e0933879901b8eef"
    ),
}

COCYCLE_SEED = 20260831
COCYCLE_DIRECTION_COUNT = 16
AMPLITUDES = (0.004, 0.01)
HORIZON = 10
DERIVATIVE_SEED = 20260902
DERIVATIVE_POINT_COUNT_PER_AMPLITUDE = 4
DERIVATIVE_TANGENT_DIRECTION_COUNT = 8
DERIVATIVE_NORMAL_DIRECTION_COUNT = 8
ADJOINT_PAIR_COUNT = 4
DIFFERENCE_STEPS = (2.0e-5, 1.0e-5, 5.0e-6)
NORMAL_SVD_SEED = 20260901
NORMAL_SVD_TOLERANCE = 1.0e-12
NORMAL_SVD_MAXIMUM_ITERATIONS = 5000

COEFFICIENT_HASH_MATCH_REQUIRED = True
DIRECTION_NORM_TOLERANCE = 5.0e-15
MAXIMUM_FULL_MAP_DERIVATIVE_ERROR = 2.0e-8
MAXIMUM_CHART_DERIVATIVE_ERROR = 2.0e-9
MAXIMUM_ADJOINT_ERROR = 5.0e-13
MAXIMUM_CONSERVATION_DERIVATIVE_RESIDUAL = 5.0e-13
MAXIMUM_PROJECTOR_RESIDUAL = 1.0e-12
MINIMUM_CHART_TANGENT_SINGULAR_VALUE = 1.0e-8
MAXIMUM_NORMAL_TRIPLET_RESIDUAL = 1.0e-8
MAXIMUM_NORMAL_SINGULAR_VALUE_DISAGREEMENT = 1.0e-6
MAXIMUM_COORDINATE_GROWTH_FACTOR = 1.05
MINIMUM_TANGENT_COCYCLE_SINGULAR_VALUE = 1.0e-8
MAXIMUM_TANGENT_LEAKAGE = 1.0e-3


def _as_columns(value: npt.ArrayLike, dimension: int) -> tuple[Array, bool]:
    array = np.asarray(value, dtype=np.float64)
    if array.shape == (dimension,):
        return array[:, None], True
    if array.ndim == 2 and array.shape[0] == dimension:
        return array, False
    raise ValueError(f"linearized state must have shape ({dimension},) or ({dimension}, m)")


def _restore_columns(value: Array, was_vector: bool) -> Array:
    return np.asarray(value[:, 0] if was_vector else value, dtype=np.float64)


def _filter_columns(field: Array, eta: float) -> Array:
    neighbours = (
        np.roll(field, 1, axis=0)
        + np.roll(field, -1, axis=0)
        + np.roll(field, 1, axis=1)
        + np.roll(field, -1, axis=1)
    )
    return np.asarray((1.0 - eta) * field + 0.25 * eta * neighbours)


@dataclass(frozen=True)
class FilteredBGKJacobian:
    """Matrix-free derivative and Euclidean adjoint of one filtered BGK step."""

    size: int
    omega: float
    eta: float
    equilibrium_density_partial: Array
    equilibrium_momentum_partial: Array

    @property
    def dimension(self) -> int:
        return self.size * self.size * 9

    @classmethod
    def at_state(
        cls,
        state: npt.ArrayLike,
        omega: float,
        eta: float,
    ) -> FilteredBGKJacobian:
        populations = np.asarray(state, dtype=np.float64)
        if populations.ndim == 1:
            dimension = populations.size
            size = round(np.sqrt(dimension / 9))
            if size * size * 9 != dimension:
                raise ValueError("flat D2Q9 state must contain 9*N*N entries")
            populations = populations.reshape(size, size, 9)
        elif populations.ndim == 3 and populations.shape[0] == populations.shape[1]:
            size = populations.shape[0]
        else:
            raise ValueError("D2Q9 state must have shape (N, N, 9) or (9*N*N,)")
        if populations.shape != (size, size, 9):
            raise ValueError("D2Q9 state must have shape (N, N, 9)")

        density, momentum = macroscopic(populations)
        if np.any(density <= 0.0):
            raise ValueError("BGK Jacobian requires strictly positive density")
        momentum_square = np.sum(momentum * momentum, axis=-1)
        population_momentum = np.einsum(
            "xyd,qd->xyq",
            momentum,
            D2Q9_VELOCITIES,
        )
        density_square = density * density
        density_partial = D2Q9_WEIGHTS * (
            1.0
            - 4.5 * population_momentum**2 / density_square[..., None]
            + 1.5 * momentum_square[..., None] / density_square[..., None]
        )
        momentum_partial = D2Q9_WEIGHTS[None, None, :, None] * (
            3.0 * D2Q9_VELOCITIES[None, None, :, :]
            + 9.0
            * population_momentum[..., None]
            * D2Q9_VELOCITIES[None, None, :, :]
            / density[..., None, None]
            - 3.0 * momentum[:, :, None, :] / density[..., None, None]
        )
        return cls(
            size=size,
            omega=float(omega),
            eta=float(eta),
            equilibrium_density_partial=np.asarray(density_partial),
            equilibrium_momentum_partial=np.asarray(momentum_partial),
        )

    def matmat(self, value: npt.ArrayLike) -> Array:
        columns, was_vector = _as_columns(value, self.dimension)
        field = columns.reshape(self.size, self.size, 9, columns.shape[1])
        density = np.sum(field, axis=2)
        momentum = np.einsum("xyqm,qd->xydm", field, D2Q9_VELOCITIES)
        equilibrium = (
            self.equilibrium_density_partial[..., None] * density[:, :, None, :]
            + np.einsum(
                "xyqd,xydm->xyqm",
                self.equilibrium_momentum_partial,
                momentum,
            )
        )
        collided = (1.0 - self.omega) * field + self.omega * equilibrium
        streamed = np.empty_like(collided)
        for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(int)):
            streamed[:, :, population] = np.roll(
                collided[:, :, population],
                shift=(int(cy), int(cx)),
                axis=(0, 1),
            )
        result = _filter_columns(streamed, self.eta).reshape(
            self.dimension,
            columns.shape[1],
        )
        return _restore_columns(result, was_vector)

    def matvec(self, value: npt.ArrayLike) -> Array:
        return self.matmat(value)

    def rmatmat(self, value: npt.ArrayLike) -> Array:
        columns, was_vector = _as_columns(value, self.dimension)
        field = columns.reshape(self.size, self.size, 9, columns.shape[1])
        filtered = _filter_columns(field, self.eta)
        unstreamed = np.empty_like(filtered)
        for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(int)):
            unstreamed[:, :, population] = np.roll(
                filtered[:, :, population],
                shift=(-int(cy), -int(cx)),
                axis=(0, 1),
            )
        density_cotangent = np.einsum(
            "xyq,xyqm->xym",
            self.equilibrium_density_partial,
            unstreamed,
        )
        momentum_cotangent = np.einsum(
            "xyqd,xyqm->xydm",
            self.equilibrium_momentum_partial,
            unstreamed,
        )
        equilibrium_cotangent = density_cotangent[:, :, None, :] + np.einsum(
            "qd,xydm->xyqm",
            D2Q9_VELOCITIES,
            momentum_cotangent,
        )
        result = (
            (1.0 - self.omega) * unstreamed
            + self.omega * equilibrium_cotangent
        ).reshape(self.dimension, columns.shape[1])
        return _restore_columns(result, was_vector)

    def rmatvec(self, value: npt.ArrayLike) -> Array:
        return self.rmatmat(value)


@dataclass(frozen=True)
class TangentGeometry:
    """Orthonormal chart tangent basis within one fixed conservation leaf."""

    leaf: FixedLeafProjector
    basis: Array
    tangent_singular_values: Array
    diagnostics: dict[str, Any]

    def project_normal(self, value: npt.ArrayLike) -> Array:
        leaf_value = self.leaf.project(value)
        columns, was_vector = _as_columns(leaf_value, self.leaf.dimension)
        result = columns - self.basis @ (self.basis.T @ columns)
        return _restore_columns(result, was_vector)


@dataclass(frozen=True)
class FixedLeafProjector:
    """Euclidean projector onto fixed total mass and momentum."""

    conservation: Array
    inverse_gram: Array
    conserved_basis: Array
    symmetry_probes: Array

    @property
    def dimension(self) -> int:
        return self.conservation.shape[1]

    @classmethod
    def for_square_grid(
        cls,
        size: int,
        *,
        probe_seed: int = DERIVATIVE_SEED,
    ) -> FixedLeafProjector:
        conservation = np.tile(conserved_moment_matrix(), (1, size * size))
        gram = conservation @ conservation.T
        conserved_basis, _ = np.linalg.qr(conservation.T, mode="reduced")
        rng = np.random.default_rng(probe_seed)
        probes = rng.normal(size=(size * size * 9, 4))
        probes /= np.linalg.norm(probes, axis=0)[None, :]
        return cls(
            conservation=np.asarray(conservation, dtype=np.float64),
            inverse_gram=np.asarray(np.linalg.inv(gram), dtype=np.float64),
            conserved_basis=np.asarray(conserved_basis, dtype=np.float64),
            symmetry_probes=np.asarray(probes, dtype=np.float64),
        )

    def project(self, value: npt.ArrayLike) -> Array:
        columns, was_vector = _as_columns(value, self.dimension)
        result = columns - self.conservation.T @ (
            self.inverse_gram @ (self.conservation @ columns)
        )
        return _restore_columns(result, was_vector)

    def tangent_geometry(self, chart_jacobian: npt.ArrayLike) -> TangentGeometry:
        derivative = np.asarray(chart_jacobian, dtype=np.float64)
        if derivative.ndim != 2 or derivative.shape[0] != self.dimension:
            raise ValueError("chart Jacobian has the wrong physical dimension")
        tangent = self.project(derivative)
        singular_values = np.linalg.svd(tangent, compute_uv=False)
        basis, _ = np.linalg.qr(tangent, mode="reduced")
        numerical_rank_threshold = (
            np.finfo(float).eps
            * max(tangent.shape)
            * float(singular_values[0])
        )
        numerical_rank = int(np.count_nonzero(singular_values > numerical_rank_threshold))

        q_orthogonality = float(
            np.linalg.norm(basis.T @ basis - np.eye(basis.shape[1]), ord=2)
        )
        conservation_tangency = float(
            np.linalg.norm(self.conservation @ basis, ord=2)
            / max(float(np.linalg.norm(self.conservation, ord=2)), np.finfo(float).eps)
        )
        geometry = TangentGeometry(
            leaf=self,
            basis=np.asarray(basis, dtype=np.float64),
            tangent_singular_values=np.asarray(singular_values, dtype=np.float64),
            diagnostics={},
        )
        projected_probes = geometry.project_normal(self.symmetry_probes)
        twice_projected = geometry.project_normal(projected_probes)
        idempotency = float(
            np.linalg.norm(twice_projected - projected_probes)
            / max(float(np.linalg.norm(projected_probes)), np.finfo(float).eps)
        )
        left = self.symmetry_probes[:, :2]
        right = self.symmetry_probes[:, 2:]
        projected_left = geometry.project_normal(left)
        projected_right = geometry.project_normal(right)
        symmetry_numerator = np.linalg.norm(
            projected_left.T @ right - left.T @ projected_right
        )
        symmetry_denominator = max(
            float(np.linalg.norm(projected_left) * np.linalg.norm(right)),
            float(np.linalg.norm(left) * np.linalg.norm(projected_right)),
            np.finfo(float).eps,
        )
        diagnostics = {
            "chart_tangent_numerical_rank": numerical_rank,
            "chart_tangent_rank_threshold": float(numerical_rank_threshold),
            "minimum_chart_tangent_singular_value": float(singular_values[-1]),
            "maximum_chart_tangent_singular_value": float(singular_values[0]),
            "q_orthogonality_residual": q_orthogonality,
            "conservation_tangency_relative_residual": conservation_tangency,
            "projector_symmetry_relative_residual": float(
                symmetry_numerator / symmetry_denominator
            ),
            "projector_idempotency_relative_residual": idempotency,
        }
        return TangentGeometry(
            leaf=self,
            basis=np.asarray(basis, dtype=np.float64),
            tangent_singular_values=np.asarray(singular_values, dtype=np.float64),
            diagnostics=diagnostics,
        )


def _mode_table(model: Full2DQuarticModel) -> npt.NDArray[np.int64]:
    label_index = {label: index for index, label in enumerate(MODE_ORDER)}
    return np.asarray(
        [
            [
                int(mode.wave_index[0]),
                int(mode.wave_index[1]),
                label_index[mode.label],
            ]
            for mode in model.modes
        ],
        dtype=np.int64,
    )


def _coefficient_reproduction(model: Full2DQuarticModel) -> dict[str, Any]:
    cubic_hashes = model.cubic.coefficient_hashes()
    quartic_hashes = model.coefficient_hashes()
    observed = {
        "mode_table_sha256": _array_hash(_mode_table(model)),
        "quadratic_chart_hessian_sha256": (
            model.cubic.quadratic.diagnostics.dense_hessian_sha256
        ),
        "quadratic_reduced_hessian_sha256": (
            model.cubic.quadratic.diagnostics.reduced_hessian_sha256
        ),
        "cubic_triple_indices_sha256": cubic_hashes["triple_indices_sha256"],
        "cubic_output_waves_sha256": cubic_hashes["output_waves_sha256"],
        "cubic_chart_coefficients_sha256": cubic_hashes[
            "chart_coefficients_sha256"
        ],
        "cubic_reduced_coefficients_sha256": cubic_hashes[
            "reduced_coefficients_sha256"
        ],
        "cubic_forcing_coefficients_sha256": cubic_hashes[
            "forcing_coefficients_sha256"
        ],
        "quartic_quartet_indices_sha256": quartic_hashes[
            "quartet_indices_sha256"
        ],
        "quartic_output_waves_sha256": quartic_hashes["output_waves_sha256"],
        "quartic_chart_coefficients_sha256": quartic_hashes[
            "chart_coefficients_sha256"
        ],
        "quartic_reduced_coefficients_sha256": quartic_hashes[
            "reduced_coefficients_sha256"
        ],
        "quartic_forcing_coefficients_sha256": quartic_hashes[
            "forcing_coefficients_sha256"
        ],
    }
    return {
        "registered": REGISTERED_COEFFICIENT_HASHES,
        "observed": observed,
        "match": observed == REGISTERED_COEFFICIENT_HASHES,
    }


def _direction_registration(directions: Array) -> dict[str, Any]:
    references = _reference_direction_groups()
    references.update(
        {
            "q007c2_shadow_domain": _normalized_directions(
                SHADOW_DOMAIN_SEED,
                SHADOW_DOMAIN_DIRECTION_COUNT,
                directions.shape[1],
            ),
            "q008a_action": _normalized_directions(
                Q008A_ACTION_SEED,
                Q008A_ACTION_DIRECTION_COUNT,
                directions.shape[1],
            ),
            "q008a_timing": _normalized_directions(
                Q008A_TIMING_SEED,
                Q008A_TIMING_DIRECTION_COUNT,
                directions.shape[1],
            ),
            "q008c_action": _normalized_directions(
                Q008C_ACTION_SEED,
                Q008C_ACTION_DIRECTION_COUNT,
                directions.shape[1],
            ),
            "q008c_timing": _normalized_directions(
                Q008C_TIMING_SEED,
                Q008C_TIMING_DIRECTION_COUNT,
                directions.shape[1],
            ),
        }
    )
    duplicates = []
    for direction_index, direction in enumerate(directions):
        for group_name, group in references.items():
            matching = np.flatnonzero(np.all(group == direction, axis=1))
            for prior_index in matching:
                duplicates.append(
                    {
                        "direction_index": direction_index,
                        "prior_group": group_name,
                        "prior_direction_index": int(prior_index),
                    }
                )
        matching_current = np.flatnonzero(
            np.all(directions[:direction_index] == direction, axis=1)
        )
        for prior_index in matching_current:
            duplicates.append(
                {
                    "direction_index": direction_index,
                    "prior_group": "q007d_cocycle",
                    "prior_direction_index": int(prior_index),
                }
            )
    return {
        "seed": COCYCLE_SEED,
        "direction_count": len(directions),
        "direction_sha256": _array_hash(directions),
        "maximum_norm_error": float(
            np.max(np.abs(np.linalg.norm(directions, axis=1) - 1.0))
        ),
        "reference_group_hashes": {
            name: _array_hash(value) for name, value in references.items()
        },
        "duplicate_count": len(duplicates),
        "duplicate_records": duplicates,
    }


def _relative_norm(numerator: npt.ArrayLike, denominator: npt.ArrayLike) -> float:
    return float(
        np.linalg.norm(np.asarray(numerator))
        / max(float(np.linalg.norm(np.asarray(denominator))), np.finfo(float).eps)
    )


def _derivative_directions(
    model: Full2DQuarticModel,
) -> tuple[Array, Array, Array, Array]:
    rng = np.random.default_rng(DERIVATIVE_SEED)
    reduced = rng.normal(
        size=(DERIVATIVE_TANGENT_DIRECTION_COUNT, model.reduced_dimension)
    )
    reduced /= np.linalg.norm(reduced, axis=1)[:, None]
    physical_normal_raw = rng.normal(
        size=(DERIVATIVE_NORMAL_DIRECTION_COUNT, model.size * model.size * 9)
    )
    adjoint_left = rng.normal(size=(ADJOINT_PAIR_COUNT, model.size * model.size * 9))
    adjoint_right = rng.normal(size=(ADJOINT_PAIR_COUNT, model.size * model.size * 9))
    adjoint_left /= np.linalg.norm(adjoint_left, axis=1)[:, None]
    adjoint_right /= np.linalg.norm(adjoint_right, axis=1)[:, None]
    return tuple(
        np.asarray(value, dtype=np.float64)
        for value in (reduced, physical_normal_raw, adjoint_left, adjoint_right)
    )


def _derivative_validation(
    model: Full2DQuarticModel,
    leaf: FixedLeafProjector,
    directions: Array,
) -> dict[str, Any]:
    reduced_directions, normal_raw, adjoint_left, adjoint_right = (
        _derivative_directions(model)
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

    records = []
    for identifier, direction_index, coordinates in points:
        state = model.chart_evaluate(coordinates)
        chart_jacobian = model.chart_jacobian(coordinates)
        geometry = leaf.tangent_geometry(chart_jacobian)
        jacobian = FilteredBGKJacobian.at_state(
            state,
            model.cubic.quadratic.omega,
            model.cubic.quadratic.eta,
        )

        physical_tangent = geometry.basis @ reduced_directions.T
        physical_normal = geometry.project_normal(normal_raw.T)
        physical_normal /= np.linalg.norm(physical_normal, axis=0)[None, :]
        physical_directions = np.column_stack((physical_tangent, physical_normal))
        analytic_full = jacobian.matmat(physical_directions)
        full_direction_records = []
        for column in range(physical_directions.shape[1]):
            direction = physical_directions[:, column]
            step_errors = []
            for step in DIFFERENCE_STEPS:
                finite_difference = (
                    model.cubic.quadratic.full_map(state + step * direction)
                    - model.cubic.quadratic.full_map(state - step * direction)
                ) / (2.0 * step)
                step_errors.append(
                    _relative_norm(
                        finite_difference - analytic_full[:, column],
                        analytic_full[:, column],
                    )
                )
            full_direction_records.append(
                {
                    "direction_kind": (
                        "tangent"
                        if column < DERIVATIVE_TANGENT_DIRECTION_COUNT
                        else "leaf_normal"
                    ),
                    "direction_index": (
                        column
                        if column < DERIVATIVE_TANGENT_DIRECTION_COUNT
                        else column - DERIVATIVE_TANGENT_DIRECTION_COUNT
                    ),
                    "step_relative_errors": step_errors,
                    "best_relative_error": min(step_errors),
                }
            )

        analytic_chart = chart_jacobian @ reduced_directions.T
        chart_direction_records = []
        for column, direction in enumerate(reduced_directions):
            step_errors = []
            for step in DIFFERENCE_STEPS:
                finite_difference = (
                    model.chart_evaluate(coordinates + step * direction)
                    - model.chart_evaluate(coordinates - step * direction)
                ) / (2.0 * step)
                step_errors.append(
                    _relative_norm(
                        finite_difference - analytic_chart[:, column],
                        analytic_chart[:, column],
                    )
                )
            chart_direction_records.append(
                {
                    "direction_index": column,
                    "step_relative_errors": step_errors,
                    "best_relative_error": min(step_errors),
                }
            )

        adjoint_records = []
        for pair_index, (left_raw, right_raw) in enumerate(
            zip(adjoint_left, adjoint_right, strict=True)
        ):
            left = geometry.project_normal(left_raw)
            right = leaf.project(right_raw)
            left /= np.linalg.norm(left)
            right /= np.linalg.norm(right)
            forward = jacobian.matvec(left)
            adjoint = jacobian.rmatvec(right)
            forward_inner = float(np.vdot(forward, right).real)
            adjoint_inner = float(np.vdot(left, adjoint).real)
            scale = max(
                float(np.linalg.norm(forward) * np.linalg.norm(right)),
                float(np.linalg.norm(left) * np.linalg.norm(adjoint)),
                np.finfo(float).eps,
            )
            adjoint_records.append(
                {
                    "pair_index": pair_index,
                    "forward_inner_product": forward_inner,
                    "adjoint_inner_product": adjoint_inner,
                    "relative_error": abs(forward_inner - adjoint_inner) / scale,
                }
            )

        records.append(
            {
                "point_identifier": identifier,
                "direction_index": direction_index,
                "coordinates": coordinates.tolist(),
                "full_map_direction_records": full_direction_records,
                "chart_direction_records": chart_direction_records,
                "adjoint_pair_records": adjoint_records,
            }
        )

    all_full_records = list(
        chain.from_iterable(record["full_map_direction_records"] for record in records)
    )
    all_chart_records = list(
        chain.from_iterable(record["chart_direction_records"] for record in records)
    )
    all_adjoint_records = list(
        chain.from_iterable(record["adjoint_pair_records"] for record in records)
    )
    return {
        "seed": DERIVATIVE_SEED,
        "point_count": len(points),
        "points_per_amplitude": DERIVATIVE_POINT_COUNT_PER_AMPLITUDE,
        "tangent_direction_count_per_point": DERIVATIVE_TANGENT_DIRECTION_COUNT,
        "leaf_normal_direction_count_per_point": DERIVATIVE_NORMAL_DIRECTION_COUNT,
        "adjoint_pair_count_per_point": ADJOINT_PAIR_COUNT,
        "difference_steps": list(DIFFERENCE_STEPS),
        "direction_hashes": {
            "reduced_tangent_sha256": _array_hash(reduced_directions),
            "physical_normal_raw_sha256": _array_hash(normal_raw),
            "adjoint_left_sha256": _array_hash(adjoint_left),
            "adjoint_right_sha256": _array_hash(adjoint_right),
        },
        "point_records": records,
        "summary": {
            "maximum_best_full_map_relative_error": max(
                record["best_relative_error"] for record in all_full_records
            ),
            "maximum_best_chart_relative_error": max(
                record["best_relative_error"] for record in all_chart_records
            ),
            "maximum_adjoint_inner_product_relative_error": max(
                record["relative_error"] for record in all_adjoint_records
            ),
        },
    }


def _normal_operator(
    jacobians: list[FilteredBGKJacobian],
    geometries: list[TangentGeometry],
) -> LinearOperator:
    if len(geometries) != len(jacobians) + 1:
        raise ValueError("normal cocycle needs one more geometry than Jacobian")
    dimension = geometries[0].leaf.dimension

    def matmat(value: npt.ArrayLike) -> Array:
        result = geometries[0].project_normal(value)
        for step, jacobian in enumerate(jacobians):
            result = geometries[step + 1].project_normal(jacobian.matmat(result))
        return np.asarray(result, dtype=np.float64)

    def rmatmat(value: npt.ArrayLike) -> Array:
        result = geometries[-1].project_normal(value)
        for step in reversed(range(len(jacobians))):
            result = geometries[step].project_normal(
                jacobians[step].rmatmat(result)
            )
        return np.asarray(result, dtype=np.float64)

    return LinearOperator(
        shape=(dimension, dimension),
        matvec=matmat,
        rmatvec=rmatmat,
        matmat=matmat,
        rmatmat=rmatmat,
        dtype=np.dtype(np.float64),
    )


def _largest_singular_triplet(
    operator: LinearOperator,
    start: Array,
) -> dict[str, Any]:
    u, singular_values, vh = svds(
        operator,
        k=1,
        which="LM",
        tol=NORMAL_SVD_TOLERANCE,
        maxiter=NORMAL_SVD_MAXIMUM_ITERATIONS,
        v0=np.asarray(start, dtype=np.float64),
        solver="arpack",
        return_singular_vectors=True,
    )
    singular_value = float(singular_values[0])
    left = np.asarray(u[:, 0], dtype=np.float64)
    right = np.asarray(vh[0], dtype=np.float64)
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
    primary_start: Array,
    secondary_start: Array,
) -> dict[str, Any]:
    primary = _largest_singular_triplet(operator, primary_start)
    secondary = _largest_singular_triplet(operator, secondary_start)
    agreement = abs(primary["singular_value"] - secondary["singular_value"]) / max(
        primary["singular_value"],
        secondary["singular_value"],
        np.finfo(float).eps,
    )
    return {
        "primary": primary,
        "secondary": secondary,
        "singular_value_relative_disagreement": float(agreement),
        "maximum_triplet_relative_residual": max(
            primary["maximum_triplet_relative_residual"],
            secondary["maximum_triplet_relative_residual"],
        ),
    }


def _conservation_derivative_residual(
    jacobian: FilteredBGKJacobian,
    leaf: FixedLeafProjector,
) -> float:
    return _relative_norm(
        jacobian.rmatmat(leaf.conservation.T) - leaf.conservation.T,
        leaf.conservation.T,
    )


def _trajectory_record(
    model: Full2DQuarticModel,
    leaf: FixedLeafProjector,
    initial_coordinates: Array,
    *,
    identifier: str,
    amplitude: float,
    direction_index: int | None,
    direction: Array | None,
    primary_start: Array,
    secondary_start: Array,
) -> dict[str, Any]:
    coordinates = [np.asarray(initial_coordinates, dtype=np.float64)]
    for _ in range(HORIZON):
        coordinates.append(model.reduced_map(coordinates[-1]))
    states = [model.chart_evaluate(value) for value in coordinates]
    chart_jacobians = [model.chart_jacobian(value) for value in coordinates]
    geometries = [leaf.tangent_geometry(value) for value in chart_jacobians]
    jacobians = [
        FilteredBGKJacobian.at_state(
            state,
            model.cubic.quadratic.omega,
            model.cubic.quadratic.eta,
        )
        for state in states[:-1]
    ]

    tangent_product = np.eye(model.reduced_dimension)
    step_records = []
    conservation_residuals = []
    tangent_blocks = []
    for step, jacobian in enumerate(jacobians):
        propagated_tangent = jacobian.matmat(geometries[step].basis)
        tangent_block = geometries[step + 1].basis.T @ propagated_tangent
        tangent_blocks.append(tangent_block)
        tangent_product = tangent_block @ tangent_product
        normal_leakage = geometries[step + 1].project_normal(propagated_tangent)
        leakage = float(
            np.linalg.norm(normal_leakage, ord=2)
            / max(float(np.linalg.norm(propagated_tangent, ord=2)), np.finfo(float).eps)
        )
        tangent_singular_values = np.linalg.svd(tangent_block, compute_uv=False)
        conservation_residual = _conservation_derivative_residual(jacobian, leaf)
        conservation_residuals.append(conservation_residual)
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
                "fixed_leaf_conservation_derivative_relative_residual": (
                    conservation_residual
                ),
            }
        )

    tangent_singular_values = np.linalg.svd(tangent_product, compute_uv=False)
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
        0.0
        if initial_norm == 0.0
        else max(coordinate_norms) / initial_norm
    )
    geometry_diagnostics = [geometry.diagnostics for geometry in geometries]
    projector_keys = (
        "q_orthogonality_residual",
        "conservation_tangency_relative_residual",
        "projector_symmetry_relative_residual",
        "projector_idempotency_relative_residual",
    )
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
                f"maximum_{key}": max(record[key] for record in geometry_diagnostics)
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
        "maximum_conservation_derivative_relative_residual": max(
            conservation_residuals
        ),
        "all_values_finite": bool(
            all(np.all(np.isfinite(value)) for value in coordinates)
            and all(np.all(np.isfinite(state)) for state in states)
            and all(np.all(np.isfinite(value)) for value in chart_jacobians)
        ),
    }


def _cocycle_campaign(
    model: Full2DQuarticModel,
    leaf: FixedLeafProjector,
    directions: Array,
) -> dict[str, Any]:
    rng = np.random.default_rng(NORMAL_SVD_SEED)
    primary_start = rng.normal(size=leaf.dimension)
    primary_start /= np.linalg.norm(primary_start)
    secondary_start = np.roll(primary_start, 1)

    equilibrium = _trajectory_record(
        model,
        leaf,
        np.zeros(model.reduced_dimension),
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
                leaf,
                amplitude * direction,
                identifier=f"amplitude_{amplitude:g}_direction_{direction_index}",
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
                    "maximum_gamma_10": max(record["gamma_10"] for record in records),
                    "minimum_margin_1_minus_gamma_10": min(
                        record["margin_1_minus_gamma_10"] for record in records
                    ),
                    "maximum_gamma_1": max(
                        record["one_step_diagnostic"]["gamma_1"] for record in records
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
        "maximum_conservation_tangency_relative_residual",
        "maximum_projector_symmetry_relative_residual",
        "maximum_projector_idempotency_relative_residual",
    )
    return {
        "seed": COCYCLE_SEED,
        "normal_svd_seed": NORMAL_SVD_SEED,
        "normal_svd_primary_start_sha256": _array_hash(primary_start),
        "normal_svd_secondary_start_rule": "one-entry cyclic roll of primary start",
        "normal_svd_secondary_start_sha256": _array_hash(secondary_start),
        "direction_count_per_amplitude": len(directions),
        "amplitudes": list(AMPLITUDES),
        "horizon": HORIZON,
        "starting_point_count": len(all_records),
        "equilibrium_control": equilibrium,
        "amplitude_records": amplitude_records,
        "summary": {
            "maximum_gamma_10": max(record["gamma_10"] for record in all_records),
            "minimum_margin_1_minus_gamma_10": min(
                record["margin_1_minus_gamma_10"] for record in all_records
            ),
            "maximum_gamma_1": max(
                record["one_step_diagnostic"]["gamma_1"] for record in all_records
            ),
            "minimum_population": min(record["minimum_population"] for record in all_records),
            "maximum_coordinate_growth_factor": max(
                record["maximum_coordinate_growth_factor"] for record in all_records
            ),
            "minimum_tangent_cocycle_singular_value": min(
                record["tangent_cocycle"]["minimum_singular_value"]
                for record in all_records
            ),
            "minimum_chart_tangent_singular_value": min(
                record["geometry_summary"]["minimum_chart_tangent_singular_value"]
                for record in all_records
            ),
            "minimum_chart_tangent_rank": min(
                record["geometry_summary"]["minimum_chart_tangent_rank"]
                for record in all_records
            ),
            "maximum_tangent_leakage": max(
                record["maximum_tangent_leakage"] for record in all_records
            ),
            "maximum_conservation_derivative_relative_residual": max(
                record["maximum_conservation_derivative_relative_residual"]
                for record in all_records
            ),
            "maximum_normal_triplet_relative_residual": max(
                record["normal_cocycle"]["maximum_triplet_relative_residual"]
                for record in all_records
            ),
            "maximum_normal_singular_value_relative_disagreement": max(
                record["normal_cocycle"]["singular_value_relative_disagreement"]
                for record in all_records
            ),
            **{
                key: max(record["geometry_summary"][key] for record in all_records)
                for key in projector_keys
            },
            "all_values_finite": all(record["all_values_finite"] for record in all_records),
        },
    }


def run_normal_cocycle_audit() -> dict[str, Any]:
    """Run the preregistered Q007d projected normal-cocycle audit."""

    model = build_full2d_quartic_model()
    leaf = FixedLeafProjector.for_square_grid(model.size)
    directions = _normalized_directions(
        COCYCLE_SEED,
        COCYCLE_DIRECTION_COUNT,
        model.reduced_dimension,
    )
    coefficient_reproduction = _coefficient_reproduction(model)
    direction_registration = _direction_registration(directions)
    derivative_validation = _derivative_validation(model, leaf, directions)
    campaign = _cocycle_campaign(model, leaf, directions)
    derivative_summary = derivative_validation["summary"]
    campaign_summary = campaign["summary"]

    serializable_probe = {
        "coefficient_reproduction": coefficient_reproduction,
        "direction_registration": direction_registration,
        "derivative_validation": derivative_validation,
        "cocycle_campaign": campaign,
    }
    all_finite = _all_numeric_values_finite(serializable_probe)
    strict_json = _strict_json_serializable(serializable_probe)
    maximum_projector_residual = max(
        campaign_summary["maximum_q_orthogonality_residual"],
        campaign_summary["maximum_conservation_tangency_relative_residual"],
        campaign_summary["maximum_projector_symmetry_relative_residual"],
        campaign_summary["maximum_projector_idempotency_relative_residual"],
    )
    validity_gates = {
        "registered_coefficient_reproduction": {
            "value": coefficient_reproduction["match"],
            "threshold": COEFFICIENT_HASH_MATCH_REQUIRED,
            "passed": coefficient_reproduction["match"],
        },
        "independent_direction_integrity": {
            "value": {
                "direction_count": direction_registration["direction_count"],
                "maximum_norm_error": direction_registration["maximum_norm_error"],
                "duplicate_count": direction_registration["duplicate_count"],
            },
            "threshold": {
                "direction_count": COCYCLE_DIRECTION_COUNT,
                "maximum_norm_error": DIRECTION_NORM_TOLERANCE,
                "duplicate_count": 0,
            },
            "passed": bool(
                direction_registration["direction_count"] == COCYCLE_DIRECTION_COUNT
                and direction_registration["maximum_norm_error"]
                <= DIRECTION_NORM_TOLERANCE
                and direction_registration["duplicate_count"] == 0
            ),
        },
        "analytic_derivatives_and_adjoint": {
            "value": derivative_summary,
            "threshold": {
                "maximum_best_full_map_relative_error": (
                    MAXIMUM_FULL_MAP_DERIVATIVE_ERROR
                ),
                "maximum_best_chart_relative_error": MAXIMUM_CHART_DERIVATIVE_ERROR,
                "maximum_adjoint_inner_product_relative_error": MAXIMUM_ADJOINT_ERROR,
            },
            "passed": bool(
                derivative_summary["maximum_best_full_map_relative_error"]
                <= MAXIMUM_FULL_MAP_DERIVATIVE_ERROR
                and derivative_summary["maximum_best_chart_relative_error"]
                <= MAXIMUM_CHART_DERIVATIVE_ERROR
                and derivative_summary["maximum_adjoint_inner_product_relative_error"]
                <= MAXIMUM_ADJOINT_ERROR
            ),
        },
        "fixed_leaf_and_projector_geometry": {
            "value": {
                "minimum_chart_tangent_rank": campaign_summary[
                    "minimum_chart_tangent_rank"
                ],
                "minimum_chart_tangent_singular_value": campaign_summary[
                    "minimum_chart_tangent_singular_value"
                ],
                "maximum_projector_residual": maximum_projector_residual,
                "maximum_conservation_derivative_relative_residual": campaign_summary[
                    "maximum_conservation_derivative_relative_residual"
                ],
            },
            "threshold": {
                "minimum_chart_tangent_rank": model.reduced_dimension,
                "minimum_chart_tangent_singular_value": (
                    MINIMUM_CHART_TANGENT_SINGULAR_VALUE
                ),
                "maximum_projector_residual": MAXIMUM_PROJECTOR_RESIDUAL,
                "maximum_conservation_derivative_relative_residual": (
                    MAXIMUM_CONSERVATION_DERIVATIVE_RESIDUAL
                ),
            },
            "passed": bool(
                campaign_summary["minimum_chart_tangent_rank"]
                == model.reduced_dimension
                and campaign_summary["minimum_chart_tangent_singular_value"]
                >= MINIMUM_CHART_TANGENT_SINGULAR_VALUE
                and maximum_projector_residual <= MAXIMUM_PROJECTOR_RESIDUAL
                and campaign_summary[
                    "maximum_conservation_derivative_relative_residual"
                ]
                <= MAXIMUM_CONSERVATION_DERIVATIVE_RESIDUAL
            ),
        },
        "matrix_free_normal_svd": {
            "value": {
                "maximum_triplet_relative_residual": campaign_summary[
                    "maximum_normal_triplet_relative_residual"
                ],
                "maximum_singular_value_relative_disagreement": campaign_summary[
                    "maximum_normal_singular_value_relative_disagreement"
                ],
            },
            "threshold": {
                "maximum_triplet_relative_residual": MAXIMUM_NORMAL_TRIPLET_RESIDUAL,
                "maximum_singular_value_relative_disagreement": (
                    MAXIMUM_NORMAL_SINGULAR_VALUE_DISAGREEMENT
                ),
            },
            "passed": bool(
                campaign_summary["maximum_normal_triplet_relative_residual"]
                <= MAXIMUM_NORMAL_TRIPLET_RESIDUAL
                and campaign_summary[
                    "maximum_normal_singular_value_relative_disagreement"
                ]
                <= MAXIMUM_NORMAL_SINGULAR_VALUE_DISAGREEMENT
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
                "starting_point_count": 1 + len(AMPLITUDES) * COCYCLE_DIRECTION_COUNT,
                "minimum_population_strictly_greater_than": 0.0,
                "maximum_coordinate_growth_factor": MAXIMUM_COORDINATE_GROWTH_FACTOR,
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
                and campaign_summary["minimum_tangent_cocycle_singular_value"]
                >= MINIMUM_TANGENT_COCYCLE_SINGULAR_VALUE
                and all_finite
                and strict_json
            ),
        },
        "tangent_leakage": {
            "value": campaign_summary["maximum_tangent_leakage"],
            "threshold": MAXIMUM_TANGENT_LEAKAGE,
            "passed": campaign_summary["maximum_tangent_leakage"]
            <= MAXIMUM_TANGENT_LEAKAGE,
        },
    }

    equilibrium_passed = campaign["equilibrium_control"]["gamma_10"] < 1.0
    amplitude_gates = {
        amplitude_record["amplitude"]: (
            amplitude_record["summary"]["maximum_gamma_10"] < 1.0
        )
        for amplitude_record in campaign["amplitude_records"]
    }
    hypothesis_gates = {
        "equilibrium_gamma_10": {
            "value": campaign["equilibrium_control"]["gamma_10"],
            "threshold_strictly_less_than": 1.0,
            "passed": equilibrium_passed,
        },
        "amplitude_0p004_gamma_10": {
            "value": next(
                record["summary"]["maximum_gamma_10"]
                for record in campaign["amplitude_records"]
                if record["amplitude"] == 0.004
            ),
            "threshold_strictly_less_than": 1.0,
            "passed": amplitude_gates[0.004],
        },
        "amplitude_0p01_gamma_10": {
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
        classification = "registered projected normal-cocycle audit is inconclusive"
        decision = (
            "Do not interpret the normal ratio until every derivative, projector, "
            "trajectory, leakage, and matrix-free SVD validity gate passes."
        )
        next_change = (
            "Diagnose the preregistered validity failure without changing the "
            "normal-dominance hypothesis threshold."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "registered finite-sample projected normal-cocycle dominance observed"
        )
        decision = (
            "Proceed to a separately preregistered Q007e a posteriori defect and "
            "derivative-Lipschitz bound audit."
        )
        next_change = (
            "Preregister Q007e finite-domain defect, inverse, and Lipschitz bounds "
            "before claiming an invariant manifold theorem."
        )
    else:
        outcome = "rejected"
        classification = (
            "registered finite-sample projected normal-cocycle dominance not observed"
        )
        decision = (
            "Reject only the registered Euclidean projected bundle; do not infer "
            "failure of every adapted or Riesz bundle."
        )
        next_change = (
            "Preregister any adapted-norm or Riesz-bundle candidate and thresholds "
            "before evaluating it."
        )

    return {
        "question": (
            "Does the Q006h equilibrium gap persist as ten-step projected normal "
            "dominance on the two Q007c2 finite shadow cells?"
        ),
        "hypothesis": (
            "The ten-step maximum projected-normal singular value is strictly "
            "smaller than the minimum tangent-cocycle singular value at equilibrium "
            "and along all 32 registered finite-radius trajectories."
        ),
        "registered_setup": {
            "grid": [model.size, model.size],
            "omega": model.cubic.quadratic.omega,
            "eta": model.cubic.quadratic.eta,
            "fixed_global_conservation_leaf": True,
            "real_reduced_dimension": model.reduced_dimension,
            "amplitudes": list(AMPLITUDES),
            "direction_count_per_amplitude": COCYCLE_DIRECTION_COUNT,
            "starting_point_count": 1 + len(AMPLITUDES) * COCYCLE_DIRECTION_COUNT,
            "horizon": HORIZON,
            "projector": "Euclidean fixed-leaf orthogonal tangent/normal projector",
            "full_map": "unmodified standard filtered D2Q9 map",
        },
        "coefficient_reproduction": coefficient_reproduction,
        "direction_registration": direction_registration,
        "derivative_validation": derivative_validation,
        "cocycle_campaign": campaign,
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
            "q007c2_radius_0p004_horizon_100_revised": False,
            "q007c2_radius_0p01_horizon_10_revised": False,
            "q008a_tt_svd_rejection_revised": False,
            "q008c_wave_qtt_rejection_revised": False,
        },
        "claim_boundary": (
            "The outcome is a finite-sample Euclidean-projector diagnostic on one "
            "17x17 grid, two radii, 16 directions per radius, and ten steps. It is "
            "not a full-ball, other-horizon, adapted-norm, true invariant normal-"
            "bundle, grid-uniform normal-attraction, existence, or uniqueness theorem."
        ),
    }
