"""Sealed Q011b zero-mean periodic forced fixed-point study."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy import linalg

import research.q011a_periodic_forcing_compatibility as q011a
from ttim_lbm.checkerboard_filter import conservative_checkerboard_filter
from ttim_lbm.conservation_drift import compensated_conserved_quantities
from ttim_lbm.d2q9 import (
    D2Q9_VELOCITIES,
    D2Q9_WEIGHTS,
    collide_bgk,
    conserved_moment_matrix,
    macroscopic,
    stream_periodic,
    uniform_equilibrium,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]

SIZE = 17
SITE_COUNT = SIZE * SIZE
STRIPE_DIMENSION = SIZE * 9
FIXED_LEAF_DIMENSION = STRIPE_DIMENSION - 3
OMEGA = 1.5
ETA = 0.01
EXACT_OMEGA = Fraction(3, 2)
EXACT_ETA = Fraction(1, 100)
EXACT_AMPLITUDE = Fraction(3, 2**24)
AMPLITUDE = float(EXACT_AMPLITUDE)

Q011A_ARTIFACT_SHA256 = "31c427660b10771af7756c249408606578a9b7a02d756bc77b918b56e7a5b14a"
Q011A_RUNNER_SHA256 = "41e45565066fd4c96c2ae927bc8cc6a1218377f67b711f6cc312ecbf0d1c68de"
Q011A_SOURCE_DIGEST = "75fd3fe1050b39a333f483375969a67c79ab9ec75009a2048359d0f0dabb7492"
Q011A_PROBE_DIGEST = "43d0b722ba63a45ccf6b5a41cffaef387448fcc2cd9324538887fd3169571001"
Q011A_RESULT_DIGEST = "9b1f0c1516a365481c72617957b30424a7873136d221bd164b6d0617c4c3d958"

DERIVATIVE_SEED = 20260812
DERIVATIVE_DIRECTION_COUNT = 4
DERIVATIVE_STEPS = (2.0e-5, 1.0e-5, 5.0e-6)
BLOCK_ACTION_SEED = 20260813
BLOCK_ACTION_INDICES = (0, 1, 4, 8)
NEWTON_MAXIMUM_STEPS = 12
LINE_SEARCH_FACTORS = tuple(2.0**-index for index in range(7))

WAVEFORM_SUM_TOLERANCE = 1.0e-14
WAVEFORM_LEAKAGE_TOLERANCE = 1.0e-13
SOURCE_MOMENT_TOLERANCE = 1.0e-20
STAGE_REPLAY_TOLERANCE = 1.0e-15
BASIS_TOLERANCE = 1.0e-12
LINEAR_RESPONSE_RESIDUAL_TOLERANCE = 1.0e-12
DERIVATIVE_RELATIVE_TOLERANCE = 2.0e-8
PROJECTED_RESIDUAL_TOLERANCE = 5.0e-13
FULL_RESIDUAL_TOLERANCE = 5.0e-12
COMPONENT_RESIDUAL_TOLERANCE = 5.0e-13
SOLUTION_DISTANCE_TOLERANCE = 1.0e-11
SOLUTION_RELATIVE_DISTANCE_TOLERANCE = 1.0e-9
GLOBAL_MOMENT_TOLERANCE = 5.0e-11
SECTOR_LEAKAGE_TOLERANCE = 1.0e-8
UNIT_EIGENVALUE_TOLERANCE = 1.0e-9
SCHUR_RESIDUAL_TOLERANCE = 1.0e-10
SPECTRUM_HAUSDORFF_TOLERANCE = 1.0e-10
BLOCK_ACTION_RELATIVE_TOLERANCE = 2.0e-10
SPECTRAL_RADIUS_CEILING = 0.9999
MINIMUM_RESOLVENT_SINGULAR_VALUE = 1.0e-4
MAXIMUM_RESOLVENT_CONDITION_NUMBER = 1.0e6


def _canonical_json_sha256(value: Any) -> str:
    encoded = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _array_sha256(value: npt.ArrayLike) -> str:
    array = np.ascontiguousarray(value)
    digest = sha256()
    digest.update(array.dtype.str.encode("ascii"))
    digest.update(b"\0")
    digest.update(json.dumps(array.shape).encode("ascii"))
    digest.update(b"\0")
    digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _relative_error(left: npt.ArrayLike, right: npt.ArrayLike) -> float:
    left_array = np.asarray(left)
    right_array = np.asarray(right)
    denominator = max(float(np.linalg.norm(right_array)), np.finfo(float).tiny)
    return float(np.linalg.norm(left_array - right_array) / denominator)


def force_waveform() -> Array:
    """Return the registered unmodified binary64 cosine waveform."""

    y = np.arange(SIZE, dtype=np.float64)
    return np.asarray(AMPLITUDE * np.cos(2.0 * np.pi * y / SIZE))


def spatial_body_force_source(force_x: npt.ArrayLike) -> Array:
    """Return the Q011a rest-linear source for a spatial x-force field."""

    field = np.asarray(force_x, dtype=np.float64)
    if field.ndim != 2 or not np.all(np.isfinite(field)):
        raise ValueError("force_x must be a finite two-dimensional field")
    return np.asarray(
        field[..., None] * (3.0 * D2Q9_WEIGHTS * D2Q9_VELOCITIES[:, 0]),
        dtype=np.float64,
    )


def zero_mean_forced_filtered_bgk_periodic_step(
    state: npt.ArrayLike,
    omega: float,
    eta: float,
    force_x: npt.ArrayLike,
) -> Array:
    """Apply collision, spatial source, periodic streaming, and filtering."""

    populations = np.asarray(state, dtype=np.float64)
    if populations.ndim != 3 or populations.shape[-1] != 9:
        raise ValueError("D2Q9 state must have shape (ny, nx, 9)")
    force = np.asarray(force_x, dtype=np.float64)
    if force.shape != populations.shape[:2] or not np.all(np.isfinite(force)):
        raise ValueError("force_x must match the state spatial shape")
    post_source = collide_bgk(populations, omega) + spatial_body_force_source(force)
    streamed = stream_periodic(post_source)
    return conservative_checkerboard_filter(streamed, eta)


def _stripe_force() -> Array:
    return force_waveform()[:, None]


def _full_force() -> Array:
    return np.repeat(_stripe_force(), SIZE, axis=1)


def _stripe_step(state: npt.ArrayLike) -> Array:
    return zero_mean_forced_filtered_bgk_periodic_step(
        state,
        OMEGA,
        ETA,
        _stripe_force(),
    )


@dataclass(frozen=True)
class RectangularFilteredBGKJacobian:
    """Derivative of the unforced part of the additive-source map."""

    ny: int
    nx: int
    omega: float
    eta: float
    equilibrium_density_partial: Array
    equilibrium_momentum_partial: Array

    @property
    def dimension(self) -> int:
        return self.ny * self.nx * 9

    @classmethod
    def at_state(
        cls,
        state: npt.ArrayLike,
        omega: float,
        eta: float,
    ) -> RectangularFilteredBGKJacobian:
        populations = np.asarray(state, dtype=np.float64)
        if populations.ndim != 3 or populations.shape[-1] != 9:
            raise ValueError("D2Q9 state must have shape (ny, nx, 9)")
        if not np.all(np.isfinite(populations)):
            raise ValueError("Jacobian state must be finite")
        density, momentum = macroscopic(populations)
        if np.any(density <= 0.0):
            raise ValueError("Jacobian state density must be strictly positive")

        momentum_square = np.sum(momentum * momentum, axis=-1)
        population_momentum = np.einsum(
            "yxd,qd->yxq",
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
            ny=populations.shape[0],
            nx=populations.shape[1],
            omega=float(omega),
            eta=float(eta),
            equilibrium_density_partial=np.asarray(density_partial),
            equilibrium_momentum_partial=np.asarray(momentum_partial),
        )

    def matmat(self, value: npt.ArrayLike) -> np.ndarray:
        array = np.asarray(value)
        was_vector = array.ndim == 1
        if was_vector:
            if array.shape != (self.dimension,):
                raise ValueError("Jacobian vector has the wrong dimension")
            columns = array[:, None]
        elif array.ndim == 2 and array.shape[0] == self.dimension:
            columns = array
        else:
            raise ValueError("Jacobian input has the wrong shape")

        field = columns.reshape(self.ny, self.nx, 9, columns.shape[1])
        density = np.sum(field, axis=2)
        momentum = np.einsum("yxqm,qd->yxdm", field, D2Q9_VELOCITIES)
        equilibrium_action = self.equilibrium_density_partial[..., None] * density[
            :, :, None, :
        ] + np.einsum(
            "yxqd,yxdm->yxqm",
            self.equilibrium_momentum_partial,
            momentum,
        )
        collided = (1.0 - self.omega) * field + self.omega * equilibrium_action
        streamed = np.empty_like(collided)
        for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(np.int64)):
            streamed[:, :, population] = np.roll(
                collided[:, :, population],
                shift=(int(cy), int(cx)),
                axis=(0, 1),
            )
        neighbours = (
            np.roll(streamed, 1, axis=0)
            + np.roll(streamed, -1, axis=0)
            + np.roll(streamed, 1, axis=1)
            + np.roll(streamed, -1, axis=1)
        )
        result = ((1.0 - self.eta) * streamed + 0.25 * self.eta * neighbours).reshape(
            self.dimension, columns.shape[1]
        )
        return result[:, 0] if was_vector else result

    def dense(self) -> np.ndarray:
        return self.matmat(np.eye(self.dimension, dtype=np.float64))


def _q011a_replay_audit() -> dict[str, Any]:
    artifact_path = (
        Path(__file__).resolve().parent / "artifacts" / "q011a_periodic_forcing_compatibility.json"
    )
    runner_path = Path(q011a.__file__).resolve()
    stored = json.loads(artifact_path.read_text(encoding="utf-8"))
    fresh_cycle = q011a.run_periodic_forcing_compatibility_audit()
    checks = {
        "artifact_sha256_matches": (_file_sha256(artifact_path) == Q011A_ARTIFACT_SHA256),
        "runner_sha256_matches": (_file_sha256(runner_path) == Q011A_RUNNER_SHA256),
        "stored_cycle_replays_exactly": stored["cycle"] == fresh_cycle,
        "stored_validity_is_six_of_six": (
            len(stored["cycle"]["validity_gates"]) == 6
            and all(gate["passed"] for gate in stored["cycle"]["validity_gates"].values())
        ),
        "stored_hypothesis_is_four_of_four": (
            len(stored["cycle"]["hypothesis_gates"]) == 4
            and all(gate["passed"] for gate in stored["cycle"]["hypothesis_gates"].values())
        ),
        "stored_outcome_is_accepted": (
            stored["study_gate"] == "passed" and stored["scientific_outcome"] == "accepted"
        ),
        "stored_source_digest_matches": (
            stored["cycle"]["source_digest_sha256"] == Q011A_SOURCE_DIGEST
        ),
        "stored_probe_digest_matches": (
            stored["cycle"]["probe_digest_sha256"] == Q011A_PROBE_DIGEST
        ),
        "stored_result_digest_matches": (
            stored["cycle"]["result_digest_sha256"] == Q011A_RESULT_DIGEST
        ),
        "registered_map_matches": (
            stored["cycle"]["registered_parameters"]["size"] == SIZE
            and stored["cycle"]["registered_parameters"]["omega"] == _fraction_record(EXACT_OMEGA)
            and stored["cycle"]["registered_parameters"]["eta"] == _fraction_record(EXACT_ETA)
        ),
    }
    return {
        "artifact_filename": artifact_path.name,
        "artifact_sha256": _file_sha256(artifact_path),
        "runner_filename": runner_path.name,
        "runner_sha256": _file_sha256(runner_path),
        "source_digest_sha256": fresh_cycle["source_digest_sha256"],
        "probe_digest_sha256": fresh_cycle["probe_digest_sha256"],
        "result_digest_sha256": fresh_cycle["result_digest_sha256"],
        "fresh_validity_gate_count": len(fresh_cycle["validity_gates"]),
        "fresh_hypothesis_gate_count": len(fresh_cycle["hypothesis_gates"]),
        "fresh_study_validity": fresh_cycle["study_validity"],
        "fresh_hypothesis_outcome": fresh_cycle["hypothesis_outcome"],
        "fresh_scientific_classification": fresh_cycle["scientific_classification"],
        "checks": checks,
        "passed": all(checks.values()),
    }


def _source_and_stage_audit() -> dict[str, Any]:
    waveform = force_waveform()
    waveform_transform = np.fft.fft(waveform, norm="ortho")
    outside = np.ones(SIZE, dtype=bool)
    outside[[1, SIZE - 1]] = False
    waveform_leakage = float(
        np.linalg.norm(waveform_transform[outside])
        / max(float(np.linalg.norm(waveform_transform)), np.finfo(float).tiny)
    )

    source = spatial_body_force_source(_stripe_force())[:, 0, :]
    observed_moments = np.column_stack(
        (
            np.sum(source, axis=1),
            source @ D2Q9_VELOCITIES[:, 0],
            source @ D2Q9_VELOCITIES[:, 1],
        )
    )
    expected_moments = np.column_stack((np.zeros(SIZE), waveform, np.zeros(SIZE)))
    moment_residual = observed_moments - expected_moments
    q011a_sources = np.vstack(
        [q011a.rest_linear_body_force_source((force_x, 0.0)) for force_x in waveform]
    )

    rest = uniform_equilibrium(SIZE, 1, np.zeros(3))
    public_step = _stripe_step(rest)
    manual_source = q011a_sources[:, None, :]
    manual_step = conservative_checkerboard_filter(
        stream_periodic(collide_bgk(rest, OMEGA) + manual_source),
        ETA,
    )
    checks = {
        "float_waveform_sum_within_tolerance": (
            abs(float(np.sum(waveform))) <= WAVEFORM_SUM_TOLERANCE
        ),
        "waveform_support_within_tolerance": (waveform_leakage <= WAVEFORM_LEAKAGE_TOLERANCE),
        "source_matches_q011a_definition_bitwise": np.array_equal(
            source,
            q011a_sources,
        ),
        "source_moments_within_tolerance": (
            float(np.max(np.abs(moment_residual))) <= SOURCE_MOMENT_TOLERANCE
        ),
        "stage_replay_within_tolerance": (
            float(np.max(np.abs(public_step - manual_step))) <= STAGE_REPLAY_TOLERANCE
        ),
        "source_spatial_mean_is_within_float_tolerance": (
            float(np.max(np.abs(np.sum(observed_moments, axis=0)))) <= WAVEFORM_SUM_TOLERANCE
        ),
    }
    return {
        "waveform": waveform.tolist(),
        "waveform_sha256": _array_sha256(waveform),
        "float_waveform_sum": float(np.sum(waveform)),
        "waveform_fft_relative_leakage_outside_plus_minus_one": (waveform_leakage),
        "source_sha256": _array_sha256(source),
        "maximum_source_moment_residual": float(np.max(np.abs(moment_residual))),
        "source_spatial_moment_sum": np.sum(
            observed_moments,
            axis=0,
        ).tolist(),
        "maximum_stage_replay_discrepancy": float(np.max(np.abs(public_step - manual_step))),
        "stage_replay_is_bitwise": np.array_equal(public_step, manual_step),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _fixed_leaf_basis() -> tuple[Array, Array, dict[str, Any]]:
    conservation = np.tile(conserved_moment_matrix(), (1, SIZE))
    basis = linalg.null_space(conservation)
    orthogonality = float(
        np.linalg.norm(
            basis.T @ basis - np.eye(basis.shape[1]),
            ord="fro",
        )
    )
    annihilation = float(np.linalg.norm(conservation @ basis, ord="fro"))
    checks = {
        "dimension_is_registered": basis.shape == (STRIPE_DIMENSION, FIXED_LEAF_DIMENSION),
        "orthogonality_within_tolerance": (orthogonality <= BASIS_TOLERANCE),
        "moment_annihilation_within_tolerance": (annihilation <= BASIS_TOLERANCE),
    }
    audit = {
        "conservation_matrix_shape": list(conservation.shape),
        "basis_shape": list(basis.shape),
        "basis_sha256": _array_sha256(basis),
        "orthogonality_frobenius_residual": orthogonality,
        "moment_annihilation_frobenius_residual": annihilation,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return np.asarray(conservation), np.asarray(basis), audit


def _linear_response(
    rest: Array,
    basis: Array,
) -> tuple[Array, Array, dict[str, Any]]:
    rest_jacobian = RectangularFilteredBGKJacobian.at_state(
        rest,
        OMEGA,
        ETA,
    )
    reduced_jacobian = basis.T @ rest_jacobian.matmat(basis)
    response_operator = np.eye(FIXED_LEAF_DIMENSION) - reduced_jacobian
    right_hand_side = basis.T @ (_stripe_step(rest) - rest).ravel()
    try:
        coordinate = linalg.solve(
            response_operator,
            right_hand_side,
            assume_a="gen",
            check_finite=True,
        )
        solve_succeeded = True
    except linalg.LinAlgError:
        coordinate = np.zeros(FIXED_LEAF_DIMENSION, dtype=np.float64)
        solve_succeeded = False
    residual = response_operator @ coordinate - right_hand_side
    relative_residual = float(
        np.linalg.norm(residual) / max(float(np.linalg.norm(right_hand_side)), np.finfo(float).tiny)
    )
    state = rest + (basis @ coordinate).reshape(SIZE, 1, 9)
    checks = {
        "linear_solve_succeeded": solve_succeeded,
        "coordinate_is_finite": bool(np.all(np.isfinite(coordinate))),
        "state_is_finite": bool(np.all(np.isfinite(state))),
        "equation_residual_within_tolerance": (
            relative_residual <= LINEAR_RESPONSE_RESIDUAL_TOLERANCE
        ),
        "state_density_is_positive": bool(np.all(macroscopic(state)[0] > 0.0)),
    }
    return (
        coordinate,
        state,
        {
            "response_operator_shape": list(response_operator.shape),
            "response_operator_condition_number": float(np.linalg.cond(response_operator)),
            "right_hand_side_l2": float(np.linalg.norm(right_hand_side)),
            "coordinate_l2": float(np.linalg.norm(coordinate)),
            "coordinate_sha256": _array_sha256(coordinate),
            "state_sha256": _array_sha256(state),
            "equation_relative_residual": relative_residual,
            "checks": checks,
            "passed": all(checks.values()),
        },
    )


def _derivative_audit(state: Array, basis: Array) -> dict[str, Any]:
    rng = np.random.default_rng(DERIVATIVE_SEED)
    coordinates = rng.normal(size=(FIXED_LEAF_DIMENSION, DERIVATIVE_DIRECTION_COUNT))
    coordinates /= np.linalg.norm(coordinates, axis=0)[None, :]
    directions = basis @ coordinates
    jacobian = RectangularFilteredBGKJacobian.at_state(state, OMEGA, ETA)
    records: list[dict[str, Any]] = []
    for index in range(DERIVATIVE_DIRECTION_COUNT):
        direction = directions[:, index]
        analytic = jacobian.matmat(direction)
        step_records: list[dict[str, float]] = []
        for step in DERIVATIVE_STEPS:
            plus = _stripe_step(state + (step * direction).reshape(SIZE, 1, 9))
            minus = _stripe_step(state - (step * direction).reshape(SIZE, 1, 9))
            finite_difference = ((plus - minus) / (2.0 * step)).ravel()
            step_records.append(
                {
                    "step": step,
                    "relative_error": _relative_error(
                        finite_difference,
                        analytic,
                    ),
                }
            )
        best_error = min(record["relative_error"] for record in step_records)
        records.append(
            {
                "direction_index": index,
                "direction_l2": float(np.linalg.norm(direction)),
                "direction_sha256": _array_sha256(direction),
                "step_records": step_records,
                "best_relative_error": best_error,
                "passed": best_error <= DERIVATIVE_RELATIVE_TOLERANCE,
            }
        )
    maximum_best_error = max(record["best_relative_error"] for record in records)
    checks = {
        "direction_count_is_registered": len(records) == DERIVATIVE_DIRECTION_COUNT,
        "directions_are_fixed_leaf": (
            float(np.linalg.norm(np.tile(conserved_moment_matrix(), (1, SIZE)) @ directions))
            <= BASIS_TOLERANCE
        ),
        "all_actions_within_tolerance": all(record["passed"] for record in records),
    }
    return {
        "seed": DERIVATIVE_SEED,
        "direction_count": DERIVATIVE_DIRECTION_COUNT,
        "steps": list(DERIVATIVE_STEPS),
        "evaluation_state": "rest linear-response state",
        "direction_matrix_sha256": _array_sha256(directions),
        "records": records,
        "maximum_best_relative_error": maximum_best_error,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _residual_metrics(
    state: Array,
    basis: Array,
) -> tuple[Array, Array, dict[str, float]]:
    residual = (_stripe_step(state) - state).ravel()
    projected = basis.T @ residual
    return (
        residual,
        projected,
        {
            "projected_l2": float(np.linalg.norm(projected)),
            "full_l2": float(np.linalg.norm(residual)),
            "maximum_component": float(np.max(np.abs(residual))),
        },
    )


def _newton_solve(
    start_name: str,
    initial_coordinate: Array,
    rest: Array,
    basis: Array,
) -> tuple[Array, dict[str, Any]]:
    coordinate = np.asarray(initial_coordinate, dtype=np.float64).copy()
    trace: list[dict[str, Any]] = []
    status = "maximum_steps_reached"
    for iteration in range(NEWTON_MAXIMUM_STEPS + 1):
        state = rest + (basis @ coordinate).reshape(SIZE, 1, 9)
        residual, projected, metrics = _residual_metrics(state, basis)
        record: dict[str, Any] = {
            "iteration": iteration,
            **metrics,
            "state_minimum_population": float(np.min(state)),
            "state_minimum_density": float(np.min(macroscopic(state)[0])),
        }
        if (
            not np.all(np.isfinite(coordinate))
            or not np.all(np.isfinite(residual))
            or not np.all(np.isfinite(projected))
        ):
            record["decision"] = "nonfinite_failure"
            trace.append(record)
            status = "nonfinite_failure"
            break
        if metrics["projected_l2"] <= PROJECTED_RESIDUAL_TOLERANCE:
            record["decision"] = "projected_tolerance_reached"
            trace.append(record)
            status = "projected_tolerance_reached"
            break
        if iteration == NEWTON_MAXIMUM_STEPS:
            record["decision"] = "maximum_steps_reached"
            trace.append(record)
            break

        jacobian = RectangularFilteredBGKJacobian.at_state(
            state,
            OMEGA,
            ETA,
        )
        reduced_derivative = basis.T @ (jacobian.matmat(basis) - basis)
        record["reduced_jacobian_condition_number"] = float(np.linalg.cond(reduced_derivative))
        try:
            newton_step = linalg.solve(
                reduced_derivative,
                -projected,
                assume_a="gen",
                check_finite=True,
            )
        except linalg.LinAlgError:
            record["decision"] = "linear_solve_failure"
            trace.append(record)
            status = "linear_solve_failure"
            break
        record["newton_step_l2"] = float(np.linalg.norm(newton_step))

        accepted_factor: float | None = None
        accepted_norm: float | None = None
        trial_norms: list[dict[str, float]] = []
        for factor in LINE_SEARCH_FACTORS:
            trial_coordinate = coordinate + factor * newton_step
            trial_state = rest + (basis @ trial_coordinate).reshape(
                SIZE,
                1,
                9,
            )
            _, trial_projected, _ = _residual_metrics(trial_state, basis)
            trial_norm = float(np.linalg.norm(trial_projected))
            trial_norms.append(
                {
                    "factor": factor,
                    "projected_l2": trial_norm,
                }
            )
            if np.isfinite(trial_norm) and trial_norm < metrics["projected_l2"]:
                accepted_factor = factor
                accepted_norm = trial_norm
                coordinate = trial_coordinate
                break
        record["line_search_trials"] = trial_norms
        record["accepted_factor"] = accepted_factor
        record["accepted_projected_l2"] = accepted_norm
        if accepted_factor is None:
            record["decision"] = "line_search_failure"
            trace.append(record)
            status = "line_search_failure"
            break
        record["decision"] = "accepted_step"
        trace.append(record)

    terminal_state = rest + (basis @ coordinate).reshape(SIZE, 1, 9)
    terminal_residual, _, terminal_metrics = _residual_metrics(
        terminal_state,
        basis,
    )
    checks = {
        "terminal_values_are_finite": bool(
            np.all(np.isfinite(coordinate))
            and np.all(np.isfinite(terminal_state))
            and np.all(np.isfinite(terminal_residual))
        ),
        "projected_residual_within_tolerance": (
            terminal_metrics["projected_l2"] <= PROJECTED_RESIDUAL_TOLERANCE
        ),
        "full_residual_within_tolerance": (terminal_metrics["full_l2"] <= FULL_RESIDUAL_TOLERANCE),
        "component_residual_within_tolerance": (
            terminal_metrics["maximum_component"] <= COMPONENT_RESIDUAL_TOLERANCE
        ),
    }
    return coordinate, {
        "start_name": start_name,
        "status": status,
        "attempted_newton_steps": sum(record["decision"] == "accepted_step" for record in trace),
        "trace": trace,
        "terminal_coordinate": coordinate.tolist(),
        "terminal_coordinate_sha256": _array_sha256(coordinate),
        "terminal_state_sha256": _array_sha256(terminal_state),
        "terminal_metrics": terminal_metrics,
        "checks": checks,
        "converged": all(checks.values()),
    }


def _solver_audit(
    rest: Array,
    basis: Array,
    linear_coordinate: Array,
) -> tuple[Array, dict[str, Any]]:
    starts = {
        "zero": np.zeros(FIXED_LEAF_DIMENSION, dtype=np.float64),
        "linear_response": np.asarray(linear_coordinate, dtype=np.float64),
    }
    primary_coordinates: dict[str, Array] = {}
    primary_records: dict[str, dict[str, Any]] = {}
    replay_records: dict[str, dict[str, Any]] = {}
    for name, start in starts.items():
        coordinate, record = _newton_solve(name, start, rest, basis)
        replay_coordinate, replay_record = _newton_solve(
            name,
            start,
            rest,
            basis,
        )
        primary_coordinates[name] = coordinate
        primary_records[name] = record
        replay_records[name] = {
            "terminal_coordinate_sha256": _array_sha256(replay_coordinate),
            "trace": replay_record["trace"],
            "terminal_coordinate_bitwise_matches": np.array_equal(
                coordinate,
                replay_coordinate,
            ),
            "trace_exact_json_matches": (record["trace"] == replay_record["trace"]),
            "terminal_record_exact_json_matches": (
                record["terminal_metrics"] == replay_record["terminal_metrics"]
            ),
        }

    zero_state = rest + (basis @ primary_coordinates["zero"]).reshape(SIZE, 1, 9)
    linear_state = rest + (basis @ primary_coordinates["linear_response"]).reshape(SIZE, 1, 9)
    distance = float(np.linalg.norm(zero_state - linear_state))
    departure_scale = max(
        float(np.linalg.norm(zero_state - rest)),
        float(np.linalg.norm(linear_state - rest)),
        np.finfo(float).tiny,
    )
    relative_distance = distance / departure_scale
    deterministic = all(
        record["terminal_coordinate_bitwise_matches"]
        and record["trace_exact_json_matches"]
        and record["terminal_record_exact_json_matches"]
        for record in replay_records.values()
    )
    validity_checks = {
        "all_primary_and_replay_values_are_finite": bool(
            _all_numeric_values_finite(primary_records)
            and _all_numeric_values_finite(replay_records)
        ),
        "repeat_runs_are_bitwise_and_trace_deterministic": deterministic,
        "registered_start_count_is_two": len(primary_records) == 2,
        "registered_maximum_step_is_respected": all(
            len(record["trace"]) <= NEWTON_MAXIMUM_STEPS + 1 for record in primary_records.values()
        ),
    }
    hypothesis_checks = {
        "both_starts_converged": all(record["converged"] for record in primary_records.values()),
        "absolute_solution_distance_within_tolerance": (distance <= SOLUTION_DISTANCE_TOLERANCE),
        "relative_solution_distance_within_tolerance": (
            relative_distance <= SOLUTION_RELATIVE_DISTANCE_TOLERANCE
        ),
    }
    return zero_state, {
        "maximum_newton_steps": NEWTON_MAXIMUM_STEPS,
        "line_search_factors": list(LINE_SEARCH_FACTORS),
        "primary_runs": primary_records,
        "determinism_replays": replay_records,
        "solution_population_l2_distance": distance,
        "solution_departure_scale": departure_scale,
        "solution_relative_distance": relative_distance,
        "validity_checks": validity_checks,
        "validity_passed": all(validity_checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _physical_fourier_audit(
    representative_state: Array,
    rest: Array,
) -> tuple[Array, dict[str, Any]]:
    full_state = np.repeat(representative_state, SIZE, axis=1)
    restricted = full_state[:, :1, :]
    density, momentum = macroscopic(representative_state)
    faithful, neumaier = compensated_conserved_quantities(full_state)
    target = np.asarray([float(SITE_COUNT), 0.0, 0.0])
    faithful_residual = faithful - target
    neumaier_residual = neumaier - target

    momentum_x = momentum[:, 0, 0]
    momentum_transform = np.fft.fft(momentum_x, norm="ortho")
    first_harmonic_amplitude = float(2.0 * abs(momentum_transform[1]) / np.sqrt(SIZE))
    departure = (representative_state - rest)[:, 0, :]
    departure_transform = np.fft.fft(
        departure,
        axis=0,
        norm="ortho",
    )
    outside = np.ones(SIZE, dtype=bool)
    outside[[0, 1, 2, SIZE - 2, SIZE - 1]] = False
    sector_leakage = float(
        np.linalg.norm(departure_transform[outside])
        / max(
            float(np.linalg.norm(departure_transform)),
            np.finfo(float).tiny,
        )
    )
    maximum_global_residual = max(
        float(np.max(np.abs(faithful_residual))),
        float(np.max(np.abs(neumaier_residual))),
    )
    checks = {
        "minimum_population_is_positive": bool(np.min(representative_state) > 0.0),
        "minimum_density_is_positive": bool(np.min(density) > 0.0),
        "global_target_within_tolerance": (maximum_global_residual <= GLOBAL_MOMENT_TOLERANCE),
        "first_harmonic_is_strictly_positive": (first_harmonic_amplitude > 0.0),
        "first_harmonic_exceeds_force_amplitude": (first_harmonic_amplitude > AMPLITUDE),
        "registered_sector_leakage_within_tolerance": (sector_leakage <= SECTOR_LEAKAGE_TOLERANCE),
        "lift_restriction_roundtrip_is_bitwise": np.array_equal(
            restricted,
            representative_state,
        ),
        "lift_is_exactly_x_independent": np.array_equal(
            full_state,
            np.repeat(restricted, SIZE, axis=1),
        ),
    }
    return full_state, {
        "representative_state": "zero-start first-run terminal iterate",
        "stripe_state": representative_state[:, 0, :].tolist(),
        "stripe_state_sha256": _array_sha256(representative_state),
        "full_state_sha256": _array_sha256(full_state),
        "minimum_population": float(np.min(representative_state)),
        "minimum_density": float(np.min(density)),
        "compensated_fsum_global_moments": faithful.tolist(),
        "compensated_neumaier_global_moments": neumaier.tolist(),
        "compensated_fsum_target_residual": faithful_residual.tolist(),
        "compensated_neumaier_target_residual": neumaier_residual.tolist(),
        "maximum_compensated_global_target_residual": (maximum_global_residual),
        "first_harmonic_momentum_x_cosine_amplitude": (first_harmonic_amplitude),
        "force_amplitude": AMPLITUDE,
        "departure_fft_relative_leakage_outside_zero_plus_minus_one_two": (sector_leakage),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _block_action(
    stripe_state: Array,
    kx: float,
    value: npt.ArrayLike,
) -> np.ndarray:
    jacobian = RectangularFilteredBGKJacobian.at_state(
        stripe_state,
        OMEGA,
        ETA,
    )
    array = np.asarray(value, dtype=np.complex128)
    was_vector = array.ndim == 1
    if was_vector:
        if array.shape != (STRIPE_DIMENSION,):
            raise ValueError("Fourier-block vector has the wrong dimension")
        columns = array[:, None]
    elif array.ndim == 2 and array.shape[0] == STRIPE_DIMENSION:
        columns = array
    else:
        raise ValueError("Fourier-block input has the wrong shape")

    field = columns.reshape(SIZE, 9, columns.shape[1])
    density = np.sum(field, axis=1)
    momentum = np.einsum("yqm,qd->ydm", field, D2Q9_VELOCITIES)
    equilibrium_action = jacobian.equilibrium_density_partial[:, 0, :, None] * density[
        :, None, :
    ] + np.einsum(
        "yqd,ydm->yqm",
        jacobian.equilibrium_momentum_partial[:, 0],
        momentum,
    )
    collided = (1.0 - OMEGA) * field + OMEGA * equilibrium_action
    streamed = np.empty_like(collided)
    for population, (cx, cy) in enumerate(D2Q9_VELOCITIES.astype(np.int64)):
        streamed[:, population] = np.exp(-1j * kx * int(cx)) * np.roll(
            collided[:, population],
            shift=int(cy),
            axis=0,
        )
    filtered = (1.0 - ETA) * streamed + 0.25 * ETA * (
        np.roll(streamed, 1, axis=0) + np.roll(streamed, -1, axis=0) + 2.0 * np.cos(kx) * streamed
    )
    result = filtered.reshape(STRIPE_DIMENSION, columns.shape[1])
    return result[:, 0] if was_vector else result


def _block_matrix(stripe_state: Array, kx: float) -> ComplexArray:
    identity = np.eye(STRIPE_DIMENSION, dtype=np.complex128)
    return np.asarray(
        _block_action(stripe_state, kx, identity),
        dtype=np.complex128,
    )


def _complex_records(values: npt.ArrayLike) -> list[dict[str, float]]:
    complex_values = [complex(value) for value in np.asarray(values).ravel()]
    complex_values.sort(key=lambda value: (value.real, value.imag))
    return [{"real": float(value.real), "imag": float(value.imag)} for value in complex_values]


def _spectrum_hausdorff(
    left: npt.ArrayLike,
    right: npt.ArrayLike,
) -> float:
    left_values = np.asarray(left, dtype=np.complex128).ravel()
    right_values = np.asarray(right, dtype=np.complex128).ravel()
    distances = np.abs(left_values[:, None] - right_values[None, :])
    return float(
        max(
            np.max(np.min(distances, axis=1)),
            np.max(np.min(distances, axis=0)),
        )
    )


def _block_action_audit(
    stripe_state: Array,
    full_state: Array,
) -> dict[str, Any]:
    rng = np.random.default_rng(BLOCK_ACTION_SEED)
    full_jacobian = RectangularFilteredBGKJacobian.at_state(
        full_state,
        OMEGA,
        ETA,
    )
    records: list[dict[str, Any]] = []
    direction_columns: list[ComplexArray] = []
    x = np.arange(SIZE, dtype=np.float64)
    for index in BLOCK_ACTION_INDICES:
        direction = rng.normal(size=STRIPE_DIMENSION) + 1j * rng.normal(size=STRIPE_DIMENSION)
        direction /= np.linalg.norm(direction)
        direction_columns.append(np.asarray(direction))
        kx = 2.0 * np.pi * index / SIZE
        phase = np.exp(1j * kx * x)
        full_direction = direction.reshape(SIZE, 1, 9) * phase.reshape(1, SIZE, 1)
        block_result = _block_action(stripe_state, kx, direction)
        expected_full = block_result.reshape(SIZE, 1, 9) * phase.reshape(1, SIZE, 1)
        observed_full = full_jacobian.matmat(full_direction.ravel()).reshape(
            SIZE,
            SIZE,
            9,
        )
        relative_error = _relative_error(observed_full, expected_full)
        records.append(
            {
                "wave_index": index,
                "kx": float(kx),
                "direction_l2": float(np.linalg.norm(direction)),
                "direction_sha256": _array_sha256(direction),
                "relative_error": relative_error,
                "passed": (relative_error <= BLOCK_ACTION_RELATIVE_TOLERANCE),
            }
        )
    direction_matrix = np.column_stack(direction_columns)
    return {
        "seed": BLOCK_ACTION_SEED,
        "wave_indices": list(BLOCK_ACTION_INDICES),
        "direction_matrix_sha256": _array_sha256(direction_matrix),
        "records": records,
        "maximum_relative_error": max(record["relative_error"] for record in records),
        "passed": all(record["passed"] for record in records),
    }


def _spectrum_audit(
    stripe_state: Array,
    full_state: Array,
    conservation: Array,
    basis: Array,
) -> dict[str, Any]:
    blocks: list[ComplexArray] = []
    unrestricted_values: list[ComplexArray] = []
    fixed_leaf_values: list[ComplexArray] = []
    records: list[dict[str, Any]] = []
    maximum_reconstruction = 0.0
    maximum_unitarity = 0.0
    maximum_radius = -np.inf
    maximum_radius_index = -1
    minimum_singular = np.inf
    minimum_singular_index = -1
    maximum_condition = -np.inf
    maximum_condition_index = -1
    zero_leaf_invariance = 0.0

    for index in range(SIZE):
        kx = 2.0 * np.pi * index / SIZE
        block = _block_matrix(stripe_state, kx)
        blocks.append(block)
        schur_form, schur_vectors = linalg.schur(
            block,
            output="complex",
            check_finite=True,
        )
        values = np.diag(schur_form)
        unrestricted_values.append(np.asarray(values))
        reconstruction = float(
            np.linalg.norm(
                block - schur_vectors @ schur_form @ schur_vectors.conj().T,
                ord="fro",
            )
            / max(float(np.linalg.norm(block, ord="fro")), np.finfo(float).tiny)
        )
        unitarity = float(
            np.linalg.norm(
                schur_vectors.conj().T @ schur_vectors - np.eye(STRIPE_DIMENSION),
                ord="fro",
            )
        )

        if index == 0:
            stability_matrix = np.asarray(
                basis.T @ block @ basis,
                dtype=np.complex128,
            )
            zero_leaf_invariance = float(np.linalg.norm(conservation @ block @ basis, ord="fro"))
            stable_schur, stable_vectors = linalg.schur(
                stability_matrix,
                output="complex",
                check_finite=True,
            )
            stable_values = np.diag(stable_schur)
            stable_reconstruction = float(
                np.linalg.norm(
                    stability_matrix - stable_vectors @ stable_schur @ stable_vectors.conj().T,
                    ord="fro",
                )
                / max(
                    float(np.linalg.norm(stability_matrix, ord="fro")),
                    np.finfo(float).tiny,
                )
            )
            stable_unitarity = float(
                np.linalg.norm(
                    stable_vectors.conj().T @ stable_vectors - np.eye(FIXED_LEAF_DIMENSION),
                    ord="fro",
                )
            )
            reconstruction = max(reconstruction, stable_reconstruction)
            unitarity = max(unitarity, stable_unitarity)
        else:
            stability_matrix = block
            stable_values = values

        fixed_leaf_values.append(np.asarray(stable_values))
        singular_values = linalg.svdvals(
            np.eye(stability_matrix.shape[0], dtype=np.complex128) - stability_matrix,
            check_finite=True,
        )
        block_minimum_singular = float(singular_values[-1])
        block_condition = float(singular_values[0] / singular_values[-1])
        block_radius = float(np.max(np.abs(stable_values)))
        if block_radius > maximum_radius:
            maximum_radius = block_radius
            maximum_radius_index = index
        if block_minimum_singular < minimum_singular:
            minimum_singular = block_minimum_singular
            minimum_singular_index = index
        if block_condition > maximum_condition:
            maximum_condition = block_condition
            maximum_condition_index = index
        maximum_reconstruction = max(maximum_reconstruction, reconstruction)
        maximum_unitarity = max(maximum_unitarity, unitarity)
        record = {
            "wave_index": index,
            "kx": float(kx),
            "unrestricted_dimension": STRIPE_DIMENSION,
            "fixed_leaf_dimension": int(stability_matrix.shape[0]),
            "fixed_leaf_eigenvalues": _complex_records(stable_values),
            "maximum_fixed_leaf_eigenvalue_modulus": block_radius,
            "minimum_i_minus_j_singular_value": block_minimum_singular,
            "i_minus_j_condition_number": block_condition,
            "schur_reconstruction_relative_residual": reconstruction,
            "schur_unitarity_frobenius_residual": unitarity,
        }
        if index == 0:
            record["unrestricted_eigenvalues"] = _complex_records(values)
        records.append(record)

    pair_records: list[dict[str, Any]] = []
    for index in range(SIZE):
        partner = (-index) % SIZE
        error = _spectrum_hausdorff(
            unrestricted_values[index],
            np.conjugate(unrestricted_values[partner]),
        )
        pair_records.append(
            {
                "wave_index": index,
                "conjugate_wave_index": partner,
                "absolute_hausdorff_error": error,
                "passed": error <= SPECTRUM_HAUSDORFF_TOLERANCE,
            }
        )
    maximum_hausdorff = max(record["absolute_hausdorff_error"] for record in pair_records)
    zero_unit_count = int(
        np.count_nonzero(np.abs(unrestricted_values[0] - 1.0) <= UNIT_EIGENVALUE_TOLERANCE)
    )
    block_action = _block_action_audit(stripe_state, full_state)
    fixed_leaf_spectrum = np.concatenate(fixed_leaf_values)
    checks = {
        "block_count_is_registered": len(blocks) == SIZE,
        "block_dimensions_are_registered": all(
            block.shape == (STRIPE_DIMENSION, STRIPE_DIMENSION) for block in blocks
        ),
        "zero_wave_unit_eigenvalue_count_is_three": zero_unit_count == 3,
        "schur_reconstruction_within_tolerance": (
            maximum_reconstruction <= SCHUR_RESIDUAL_TOLERANCE
        ),
        "schur_unitarity_within_tolerance": (maximum_unitarity <= SCHUR_RESIDUAL_TOLERANCE),
        "conjugate_spectrum_within_tolerance": (maximum_hausdorff <= SPECTRUM_HAUSDORFF_TOLERANCE),
        "registered_block_actions_within_tolerance": block_action["passed"],
        "all_spectral_values_are_finite": bool(
            np.all(np.isfinite(fixed_leaf_spectrum))
            and np.isfinite(maximum_reconstruction)
            and np.isfinite(maximum_unitarity)
            and np.isfinite(minimum_singular)
            and np.isfinite(maximum_condition)
        ),
    }
    hypothesis_checks = {
        "fixed_leaf_spectral_radius_within_ceiling": (maximum_radius <= SPECTRAL_RADIUS_CEILING),
        "minimum_resolvent_singular_value_within_floor": (
            minimum_singular >= MINIMUM_RESOLVENT_SINGULAR_VALUE
        ),
        "maximum_resolvent_condition_number_within_ceiling": (
            maximum_condition <= MAXIMUM_RESOLVENT_CONDITION_NUMBER
        ),
    }
    return {
        "block_count": len(blocks),
        "unrestricted_block_dimension": STRIPE_DIMENSION,
        "zero_wave_fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
        "nonzero_wave_fixed_leaf_dimension": STRIPE_DIMENSION,
        "zero_wave_unrestricted_unit_eigenvalue_count": zero_unit_count,
        "zero_wave_unit_eigenvalue_tolerance": UNIT_EIGENVALUE_TOLERANCE,
        "zero_wave_fixed_leaf_invariance_frobenius_residual": (zero_leaf_invariance),
        "block_records": records,
        "conjugate_pair_records": pair_records,
        "maximum_schur_reconstruction_relative_residual": (maximum_reconstruction),
        "maximum_schur_unitarity_frobenius_residual": maximum_unitarity,
        "maximum_conjugate_spectrum_absolute_hausdorff_error": (maximum_hausdorff),
        "block_action_audit": block_action,
        "fixed_leaf_eigenvalue_count": int(fixed_leaf_spectrum.size),
        "fixed_leaf_spectrum_sha256": _array_sha256(fixed_leaf_spectrum),
        "maximum_fixed_leaf_eigenvalue_modulus": maximum_radius,
        "maximum_modulus_wave_index": maximum_radius_index,
        "minimum_i_minus_j_singular_value": minimum_singular,
        "minimum_singular_value_wave_index": minimum_singular_index,
        "maximum_i_minus_j_condition_number": maximum_condition,
        "maximum_condition_number_wave_index": maximum_condition_index,
        "checks": checks,
        "passed": all(checks.values()),
        "hypothesis_checks": hypothesis_checks,
        "hypothesis_passed": all(hypothesis_checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "site_count": SITE_COUNT,
        "stripe_dimension": STRIPE_DIMENSION,
        "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
        "omega": _fraction_record(EXACT_OMEGA),
        "eta": _fraction_record(EXACT_ETA),
        "force_amplitude": _fraction_record(EXACT_AMPLITUDE),
        "force_waveform": "F_x(y)=A*cos(2*pi*y/17), F_y(y)=0",
        "source": "S_q(y)=3*w_q*c_qx*F_x(y)",
        "stage_order": (
            "BGK collision, additive spatial source, periodic streaming, "
            "populationwise conservative five-point filter"
        ),
        "boundary": "periodic",
        "momentum_sink": "none",
        "target_stripe_moments": [17.0, 0.0, 0.0],
        "target_full_grid_moments": [289.0, 0.0, 0.0],
        "derivative_seed": DERIVATIVE_SEED,
        "derivative_direction_count": DERIVATIVE_DIRECTION_COUNT,
        "derivative_steps": list(DERIVATIVE_STEPS),
        "block_action_seed": BLOCK_ACTION_SEED,
        "block_action_indices": list(BLOCK_ACTION_INDICES),
        "newton_maximum_steps": NEWTON_MAXIMUM_STEPS,
        "line_search_factors": list(LINE_SEARCH_FACTORS),
        "thresholds": {
            "waveform_sum": WAVEFORM_SUM_TOLERANCE,
            "waveform_leakage": WAVEFORM_LEAKAGE_TOLERANCE,
            "source_moment": SOURCE_MOMENT_TOLERANCE,
            "stage_replay": STAGE_REPLAY_TOLERANCE,
            "basis": BASIS_TOLERANCE,
            "linear_response_relative_residual": (LINEAR_RESPONSE_RESIDUAL_TOLERANCE),
            "derivative_relative": DERIVATIVE_RELATIVE_TOLERANCE,
            "projected_residual": PROJECTED_RESIDUAL_TOLERANCE,
            "full_residual": FULL_RESIDUAL_TOLERANCE,
            "component_residual": COMPONENT_RESIDUAL_TOLERANCE,
            "solution_distance": SOLUTION_DISTANCE_TOLERANCE,
            "solution_relative_distance": (SOLUTION_RELATIVE_DISTANCE_TOLERANCE),
            "global_moment": GLOBAL_MOMENT_TOLERANCE,
            "sector_leakage": SECTOR_LEAKAGE_TOLERANCE,
            "unit_eigenvalue": UNIT_EIGENVALUE_TOLERANCE,
            "schur": SCHUR_RESIDUAL_TOLERANCE,
            "spectrum_hausdorff": SPECTRUM_HAUSDORFF_TOLERANCE,
            "block_action_relative": BLOCK_ACTION_RELATIVE_TOLERANCE,
            "spectral_radius": SPECTRAL_RADIUS_CEILING,
            "minimum_resolvent_singular_value": (MINIMUM_RESOLVENT_SINGULAR_VALUE),
            "maximum_resolvent_condition_number": (MAXIMUM_RESOLVENT_CONDITION_NUMBER),
        },
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "fixed_point_digest_sha256": cycle["fixed_point_digest_sha256"],
        "spectrum_digest_sha256": cycle["spectrum_digest_sha256"],
        "validity_gate_passes": {
            name: gate["passed"] for name, gate in cycle["validity_gates"].items()
        },
        "hypothesis_gate_passes": {
            name: gate["passed"] for name, gate in cycle["hypothesis_gates"].items()
        },
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_zero_mean_forced_fixed_point_audit() -> dict[str, Any]:
    """Run the preregistered Q011b fixed-point and spectrum gate."""

    registered_parameters = _registered_parameters()
    q011a_replay = _q011a_replay_audit()
    source_audit = _source_and_stage_audit()
    conservation, basis, basis_audit = _fixed_leaf_basis()
    rest = uniform_equilibrium(SIZE, 1, np.zeros(3))
    linear_coordinate, linear_state, linear_audit = _linear_response(
        rest,
        basis,
    )
    derivative_audit = _derivative_audit(linear_state, basis)
    representative_state, solver_audit = _solver_audit(
        rest,
        basis,
        linear_coordinate,
    )
    full_state, physical_audit = _physical_fourier_audit(
        representative_state,
        rest,
    )
    spectrum_audit = _spectrum_audit(
        representative_state,
        full_state,
        conservation,
        basis,
    )

    input_sections = {
        "registered_parameters": registered_parameters,
        "q011a_replay_audit": q011a_replay,
        "source_and_stage_audit": source_audit,
        "fixed_leaf_basis_audit": basis_audit,
    }
    fixed_point_sections = {
        "linear_response_audit": linear_audit,
        "derivative_audit": derivative_audit,
        "solver_audit": solver_audit,
        "physical_fourier_audit": physical_audit,
    }
    spectrum_sections = {
        "spectrum_audit": spectrum_audit,
    }
    input_digest = _canonical_json_sha256(input_sections)
    fixed_point_digest = _canonical_json_sha256(fixed_point_sections)
    spectrum_digest = _canonical_json_sha256(spectrum_sections)
    runner = _runner_source_metadata()
    pre_gate_sections = {
        **input_sections,
        **fixed_point_sections,
        **spectrum_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(pre_gate_sections)
        and _strict_json_serializable(pre_gate_sections)
    )
    digests_reproduce = bool(
        input_digest == _canonical_json_sha256(input_sections)
        and fixed_point_digest == _canonical_json_sha256(fixed_point_sections)
        and spectrum_digest == _canonical_json_sha256(spectrum_sections)
    )
    runner_provenance_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
        and len(runner["sha256"]) == 64
    )
    validity_gates = {
        "sealed_q011a_cycle_replays": {
            "passed": q011a_replay["passed"],
            "threshold": (
                "sealed artifact and runner hashes, three digests, 6/6 "
                "validity, 4/4 hypotheses, and accepted cycle reproduce"
            ),
            "value": q011a_replay["checks"],
        },
        "registered_source_and_stage_reproduce": {
            "passed": source_audit["passed"],
            "threshold": (
                "waveform sum <=1e-14, leakage <=1e-13, source moments "
                "<=1e-20, Q011a source equality, stage replay <=1e-15"
            ),
            "value": source_audit["checks"],
        },
        "fixed_leaf_basis_jacobian_and_linear_response_reproduce": {
            "passed": bool(
                basis_audit["passed"] and linear_audit["passed"] and derivative_audit["passed"]
            ),
            "threshold": (
                "basis residuals <=1e-12, linear response residual "
                "<=1e-12, four best derivative errors <=2e-8"
            ),
            "value": {
                "basis_passed": basis_audit["passed"],
                "linear_response_passed": linear_audit["passed"],
                "derivative_passed": derivative_audit["passed"],
            },
        },
        "deterministic_finite_newton_protocol_reproduces": {
            "passed": solver_audit["validity_passed"],
            "threshold": (
                "two registered starts, at most 12 steps, finite traces, "
                "bitwise terminal-coordinate and exact trace replay"
            ),
            "value": solver_audit["validity_checks"],
        },
        "full_grid_block_action_and_schur_reproduce": {
            "passed": spectrum_audit["passed"],
            "threshold": (
                "four block actions <=2e-10, Schur residuals <=1e-10, "
                "conjugate Hausdorff <=1e-10, zero-wave unit count 3"
            ),
            "value": spectrum_audit["checks"],
        },
        "finite_strict_json_digests_and_provenance_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_provenance_reproduces),
            "threshold": (
                "all values finite strict JSON; input, fixed-point, and "
                "spectrum digests plus runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_provenance_reproduces": (runner_provenance_reproduces),
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    raw_hypotheses = {
        "two_newton_starts_certify_the_same_fixed_point": (solver_audit["hypothesis_passed"]),
        "fixed_point_is_positive_on_target_leaf_and_fourier_concentrated": (
            physical_audit["passed"]
        ),
        "full_fixed_leaf_spectrum_is_strictly_stable": (
            spectrum_audit["hypothesis_checks"]["fixed_leaf_spectral_radius_within_ceiling"]
        ),
        "all_i_minus_j_blocks_pass_isolation_gates": bool(
            spectrum_audit["hypothesis_checks"]["minimum_resolvent_singular_value_within_floor"]
            and spectrum_audit["hypothesis_checks"][
                "maximum_resolvent_condition_number_within_ceiling"
            ]
        ),
    }
    hypothesis_gates = {
        "two_newton_starts_certify_the_same_fixed_point": {
            "passed": bool(
                validity_passed and raw_hypotheses["two_newton_starts_certify_the_same_fixed_point"]
            ),
            "threshold": (
                "both residual triples pass and absolute/relative solution distance <=1e-11/1e-9"
            ),
            "value": solver_audit["hypothesis_checks"],
        },
        "fixed_point_is_positive_on_target_leaf_and_fourier_concentrated": {
            "passed": bool(
                validity_passed
                and raw_hypotheses[
                    "fixed_point_is_positive_on_target_leaf_and_fourier_concentrated"
                ]
            ),
            "threshold": (
                "positive populations and density, target residual <=5e-11, "
                "first response > force, sector leakage <=1e-8"
            ),
            "value": physical_audit["checks"],
        },
        "full_fixed_leaf_spectrum_is_strictly_stable": {
            "passed": bool(
                validity_passed and raw_hypotheses["full_fixed_leaf_spectrum_is_strictly_stable"]
            ),
            "threshold": SPECTRAL_RADIUS_CEILING,
            "value": spectrum_audit["maximum_fixed_leaf_eigenvalue_modulus"],
        },
        "all_i_minus_j_blocks_pass_isolation_gates": {
            "passed": bool(
                validity_passed and raw_hypotheses["all_i_minus_j_blocks_pass_isolation_gates"]
            ),
            "threshold": {
                "minimum_singular_value": (MINIMUM_RESOLVENT_SINGULAR_VALUE),
                "maximum_condition_number": (MAXIMUM_RESOLVENT_CONDITION_NUMBER),
            },
            "value": {
                "minimum_singular_value": spectrum_audit["minimum_i_minus_j_singular_value"],
                "maximum_condition_number": spectrum_audit["maximum_i_minus_j_condition_number"],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    solver_and_physical = bool(
        raw_hypotheses["two_newton_starts_certify_the_same_fixed_point"]
        and raw_hypotheses["fixed_point_is_positive_on_target_leaf_and_fourier_concentrated"]
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered zero-mean forced fixed-point audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "zero-mean single-wave periodic forcing yields a numerically "
            "resolved stable fixed-leaf fixed point"
        )
    elif solver_and_physical and not raw_hypotheses["full_fixed_leaf_spectrum_is_strictly_stable"]:
        outcome = "rejected"
        classification = (
            "registered zero-mean forced fixed point is not spectrally stable on the fixed leaf"
        )
    elif not solver_and_physical:
        outcome = "not_certified"
        classification = "registered zero-mean forced fixed point was not numerically certified"
    else:
        outcome = "not_certified"
        classification = "registered zero-mean forced fixed point did not pass the isolation gate"

    cycle: dict[str, Any] = {
        "question": (
            "Does the registered zero-mean single-wave periodic source "
            "admit a positive fixed-leaf fixed point whose complete "
            "x-Fourier linearization is strictly stable?"
        ),
        **pre_gate_sections,
        "input_digest_sha256": input_digest,
        "fixed_point_digest_sha256": fixed_point_digest,
        "spectrum_digest_sha256": spectrum_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = _canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["numerical_consequence"] = {
        "registered_fixed_point_is_numerically_resolved": bool(
            validity_passed and solver_and_physical
        ),
        "registered_fixed_point_is_strictly_stable_on_fixed_leaf": bool(
            validity_passed and hypotheses_passed
        ),
        "forced_slow_spectral_subspace_has_been_selected": False,
        "forced_invariant_manifold_has_been_constructed": False,
        "rigorous_existence_or_uniqueness_has_been_proved": False,
    }
    cycle["claim_boundary"] = (
        "An accepted result is a binary64 Newton and complex-Schur "
        "prequalification for one amplitude on one 17x17 periodic filtered "
        "BGK map. It is not a rigorous existence, uniqueness, basin, "
        "normal-attraction, nonresonance, all-iterate shadowing, other-grid, "
        "other-amplitude, boundary, Poiseuille, Couette, continuum, or D3Q27 "
        "result, and it does not yet select or construct a forced slow "
        "invariant manifold."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011a_nonzero_mean_obstruction_changed": False,
        "q007ap_unforced_shadowing_changed": False,
        "q008c_tt_rejection_changed": False,
        "q010_tt_cost_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister Q011c at this forced fixed point to identify the "
        "candidate slow spectral cluster and its external separation."
        if outcome == "accepted"
        else (
            "Separate the first failed fixed-point, physical, stability, or "
            "isolation gate before changing the amplitude or thresholds."
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == _canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011b cycle failed strict serialization or digest")
    return cycle


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }


def run_q011b_study() -> dict[str, Any]:
    cycle = run_zero_mean_forced_fixed_point_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "binary64 fixed-leaf fixed-point solve and full x-Fourier linear stability audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "force_amplitude": AMPLITUDE,
            "force_wave": [0, 1],
            "boundary": "periodic",
            "forcing": ("state-independent Q011a rest-linear additive source after collision"),
            "conservation_leaf": ("total mass 289 and total momenta zero"),
            "claim": (
                "single-grid numerical prequalification only; no forced "
                "invariant-manifold or rigorous existence claim"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011b_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
