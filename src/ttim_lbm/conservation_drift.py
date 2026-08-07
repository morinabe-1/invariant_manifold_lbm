"""Sealed Q006j audit of the Q006i float64 conservation drift."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable
from typing import Any

import numpy as np
import numpy.typing as npt

from .checkerboard_filter import conservative_checkerboard_filter
from .d2q9 import (
    D2Q9_VELOCITIES,
    collide_bgk,
    equilibrium_tangent_matrix,
    global_conserved_quantities,
    stream_periodic,
)
from .full2d_chart import (
    SHADOW_SEED,
    Full2DQuadraticModel,
    build_full2d_quadratic_model,
)

Array = npt.NDArray[np.float64]

REGISTERED_DIRECTION_COUNT = 32
REGISTERED_AMPLITUDE = 0.01
REGISTERED_STEPS = 100
REGISTERED_CHECKPOINTS = (0, 1, 2, 5, 10, 20, 50, 100)
REGISTERED_TRAJECTORY_COUNT = 64
REGISTERED_STAGE_RECORD_COUNT = 6400
REGISTERED_CHECKPOINT_RECORD_COUNT = 512
REGISTERED_Q006I_MAXIMUM_DRIFT = 2.728496323152741e-12

INDEPENDENT_SUM_TOLERANCE = 5.0e-14
STREAMING_DRIFT_TOLERANCE = 5.0e-14
STAGE_RECONSTRUCTION_TOLERANCE = 1.0e-13
Q006I_REPRODUCTION_TOLERANCE = 5.0e-15
CONSERVATION_THRESHOLD = 1.0e-12
PROJECTION_CORRECTION_NORM_LIMIT = 1.0e-11


def _require_state(state: npt.ArrayLike) -> Array:
    populations = np.asarray(state, dtype=np.float64)
    if populations.ndim != 3 or populations.shape[-1] != 9:
        raise ValueError("D2Q9 state must have shape (ny, nx, 9)")
    return populations


def _neumaier_sum(values: Iterable[float]) -> float:
    total = 0.0
    correction = 0.0
    for raw_value in values:
        value = float(raw_value)
        updated = total + value
        if abs(total) >= abs(value):
            correction += (total - updated) + value
        else:
            correction += (value - updated) + total
        total = updated
    return float(total + correction)


def _moment_term_lists(state: npt.ArrayLike) -> tuple[list[float], ...]:
    populations = _require_state(state)
    mass = populations.ravel().tolist()
    momentum_terms: list[list[float]] = []
    for component in range(2):
        planes = []
        for population_index, velocity in enumerate(D2Q9_VELOCITIES[:, component]):
            if velocity == 1.0:
                planes.append(populations[..., population_index].ravel())
            elif velocity == -1.0:
                planes.append(-populations[..., population_index].ravel())
        momentum_terms.append(np.concatenate(planes).tolist())
    return mass, momentum_terms[0], momentum_terms[1]


def compensated_conserved_quantities(
    state: npt.ArrayLike,
) -> tuple[Array, Array]:
    """Return independent ``math.fsum`` and Neumaier global moments."""

    terms = _moment_term_lists(state)
    faithful = np.asarray([math.fsum(component) for component in terms])
    neumaier = np.asarray([_neumaier_sum(component) for component in terms])
    return faithful, neumaier


def _measurement(state: npt.ArrayLike) -> dict[str, Array]:
    populations = _require_state(state)
    faithful, neumaier = compensated_conserved_quantities(populations)
    return {
        "numpy": global_conserved_quantities(populations),
        "fsum": faithful,
        "neumaier": neumaier,
    }


def _measurement_record(measurement: dict[str, Array]) -> dict[str, list[float]]:
    return {method: values.tolist() for method, values in measurement.items()}


def _increment_record(
    before: dict[str, Array],
    after: dict[str, Array],
) -> dict[str, Any]:
    increments = {method: after[method] - before[method] for method in before}
    return {
        **{f"{method}_increment": value.tolist() for method, value in increments.items()},
        **{
            f"{method}_increment_norm": float(np.linalg.norm(value))
            for method, value in increments.items()
        },
    }


def _normalized_directions() -> Array:
    rng = np.random.default_rng(SHADOW_SEED)
    directions = rng.normal(size=(REGISTERED_DIRECTION_COUNT, 24))
    return np.asarray(
        directions / np.linalg.norm(directions, axis=1)[:, None],
        dtype=np.float64,
    )


def _vector_fsum(vectors: list[Array]) -> Array:
    if not vectors:
        return np.zeros(3, dtype=np.float64)
    return np.asarray(
        [math.fsum(float(vector[index]) for vector in vectors) for index in range(3)],
        dtype=np.float64,
    )


def _maximum_component_witness(value: Array) -> dict[str, Any]:
    component_index = int(np.argmax(np.abs(value)))
    return {
        "component": ("mass", "momentum_x", "momentum_y")[component_index],
        "signed_value": float(value[component_index]),
    }


def _update_maximum_drift(
    maximum: dict[str, Any],
    drift: Array,
    step: int,
) -> None:
    norm = float(np.linalg.norm(drift))
    if norm > maximum["norm"]:
        maximum.update(
            {
                "norm": norm,
                "step": step,
                "signed_drift": drift.tolist(),
                **_maximum_component_witness(drift),
            }
        )


def _stage_states(
    state: Array,
    omega: float,
    eta: float,
) -> tuple[Array, Array, Array]:
    collided = collide_bgk(state, omega)
    streamed = stream_periodic(collided)
    filtered = conservative_checkerboard_filter(streamed, eta)
    return collided, streamed, filtered


def _trajectory_audit(
    model: Full2DQuadraticModel,
    direction: Array,
    direction_index: int,
    *,
    quadratic: bool,
) -> dict[str, Any]:
    chart = model.chart if quadratic else model.linear_chart
    chart_name = "quadratic" if quadratic else "linear"
    state = chart.evaluate(REGISTERED_AMPLITUDE * direction).reshape(
        model.size,
        model.size,
        9,
    )
    initial_measurement = _measurement(state)
    current_measurement = initial_measurement
    maximum_drift = {
        method: {
            "norm": 0.0,
            "step": 0,
            "signed_drift": [0.0, 0.0, 0.0],
            "component": "mass",
            "signed_value": 0.0,
        }
        for method in initial_measurement
    }
    maximum_independent_sum_component_difference = float(
        np.max(np.abs(initial_measurement["fsum"] - initial_measurement["neumaier"]))
    )
    maximum_numpy_fsum_difference = float(
        np.linalg.norm(initial_measurement["numpy"] - initial_measurement["fsum"])
    )
    maximum_stage_map_identity_error = 0.0
    maximum_streaming_fsum_drift = 0.0
    minimum_population = float(np.min(state))
    stage_increments: dict[str, list[Array]] = {
        "collision": [],
        "streaming": [],
        "filter": [],
    }
    all_stage_increments: list[Array] = []
    checkpoint_records = [
        {
            "step": 0,
            "measurements": _measurement_record(initial_measurement),
            "drift": {
                method: [0.0, 0.0, 0.0] for method in initial_measurement
            },
        }
    ]
    stage_records = []
    maximum_reconstruction_error = 0.0

    for step in range(1, REGISTERED_STEPS + 1):
        collided, streamed, filtered = _stage_states(
            state,
            model.omega,
            model.eta,
        )
        mapped = model.full_map(state.ravel()).reshape(state.shape)
        maximum_stage_map_identity_error = max(
            maximum_stage_map_identity_error,
            float(np.max(np.abs(filtered - mapped))),
        )
        collision_measurement = _measurement(collided)
        streaming_measurement = _measurement(streamed)
        filter_measurement = _measurement(filtered)
        measurements = (
            collision_measurement,
            streaming_measurement,
            filter_measurement,
        )
        maximum_independent_sum_component_difference = max(
            maximum_independent_sum_component_difference,
            *(
                float(np.max(np.abs(value["fsum"] - value["neumaier"])))
                for value in measurements
            ),
        )
        maximum_numpy_fsum_difference = max(
            maximum_numpy_fsum_difference,
            *(
                float(np.linalg.norm(value["numpy"] - value["fsum"]))
                for value in measurements
            ),
        )
        stage_measurements = {
            "collision": (current_measurement, collision_measurement),
            "streaming": (collision_measurement, streaming_measurement),
            "filter": (streaming_measurement, filter_measurement),
        }
        step_record: dict[str, Any] = {"step": step}
        for stage_name, (before, after) in stage_measurements.items():
            step_record[stage_name] = _increment_record(before, after)
            fsum_increment = after["fsum"] - before["fsum"]
            stage_increments[stage_name].append(fsum_increment)
            all_stage_increments.append(fsum_increment)
        maximum_streaming_fsum_drift = max(
            maximum_streaming_fsum_drift,
            step_record["streaming"]["fsum_increment_norm"],
        )
        cumulative_stage_increment = _vector_fsum(all_stage_increments)
        total_fsum_drift = filter_measurement["fsum"] - initial_measurement["fsum"]
        reconstruction_error = float(
            np.linalg.norm(cumulative_stage_increment - total_fsum_drift)
        )
        maximum_reconstruction_error = max(
            maximum_reconstruction_error,
            reconstruction_error,
        )
        step_record["cumulative_fsum_stage_increment"] = (
            cumulative_stage_increment.tolist()
        )
        step_record["total_fsum_drift"] = total_fsum_drift.tolist()
        step_record["reconstruction_error"] = reconstruction_error
        stage_records.append(step_record)

        state = mapped
        current_measurement = filter_measurement
        minimum_population = min(minimum_population, float(np.min(state)))
        for method in initial_measurement:
            drift = current_measurement[method] - initial_measurement[method]
            _update_maximum_drift(maximum_drift[method], drift, step)
        if step in REGISTERED_CHECKPOINTS:
            checkpoint_records.append(
                {
                    "step": step,
                    "measurements": _measurement_record(current_measurement),
                    "drift": {
                        method: (
                            current_measurement[method] - initial_measurement[method]
                        ).tolist()
                        for method in initial_measurement
                    },
                }
            )

    cumulative_stage_contribution = {
        stage_name: _vector_fsum(values)
        for stage_name, values in stage_increments.items()
    }
    return {
        "chart": chart_name,
        "direction_index": direction_index,
        "direction": direction.tolist(),
        "initial_measurement": _measurement_record(initial_measurement),
        "checkpoint_records": checkpoint_records,
        "stage_records": stage_records,
        "summary": {
            "maximum_drift": maximum_drift,
            "maximum_independent_sum_component_difference": (
                maximum_independent_sum_component_difference
            ),
            "maximum_numpy_fsum_difference": maximum_numpy_fsum_difference,
            "maximum_stage_map_identity_error": maximum_stage_map_identity_error,
            "maximum_streaming_fsum_drift": maximum_streaming_fsum_drift,
            "maximum_stage_reconstruction_error": maximum_reconstruction_error,
            "cumulative_fsum_stage_contribution": {
                stage_name: value.tolist()
                for stage_name, value in cumulative_stage_contribution.items()
            },
            "minimum_population": minimum_population,
        },
    }


def _stage_statistics(records: list[dict[str, Any]], stage_name: str) -> dict[str, Any]:
    values = [
        stage_record[stage_name]["fsum_increment_norm"]
        for record in records
        for stage_record in record["stage_records"]
    ]
    maximum_record = max(
        (
            (
                stage_record[stage_name]["fsum_increment_norm"],
                record["chart"],
                record["direction_index"],
                stage_record["step"],
                stage_record[stage_name]["fsum_increment"],
            )
            for record in records
            for stage_record in record["stage_records"]
        ),
        key=lambda item: item[0],
    )
    cumulative_witness = max(
        (
            (
                float(
                    np.linalg.norm(
                        record["summary"]["cumulative_fsum_stage_contribution"][
                            stage_name
                        ]
                    )
                ),
                record["chart"],
                record["direction_index"],
                record["summary"]["cumulative_fsum_stage_contribution"][stage_name],
            )
            for record in records
        ),
        key=lambda item: item[0],
    )
    return {
        "maximum_one_step_norm": maximum_record[0],
        "root_mean_square_one_step_norm": float(
            np.sqrt(np.mean(np.square(values)))
        ),
        "maximum_one_step_witness": {
            "chart": maximum_record[1],
            "direction_index": maximum_record[2],
            "step": maximum_record[3],
            "signed_increment": maximum_record[4],
        },
        "maximum_cumulative_signed_norm": cumulative_witness[0],
        "maximum_cumulative_witness": {
            "chart": cumulative_witness[1],
            "direction_index": cumulative_witness[2],
            "signed_contribution": cumulative_witness[3],
        },
    }


def _maximum_trajectory_witness(
    records: list[dict[str, Any]],
    method: str,
) -> dict[str, Any]:
    record = max(
        records,
        key=lambda item: item["summary"]["maximum_drift"][method]["norm"],
    )
    return {
        "chart": record["chart"],
        "direction_index": record["direction_index"],
        **record["summary"]["maximum_drift"][method],
    }


def _projection_control_trajectory(
    model: Full2DQuadraticModel,
    direction: Array,
    direction_index: int,
    *,
    quadratic: bool,
) -> dict[str, Any]:
    chart = model.chart if quadratic else model.linear_chart
    chart_name = "quadratic" if quadratic else "linear"
    state = chart.evaluate(REGISTERED_AMPLITUDE * direction).reshape(
        model.size,
        model.size,
        9,
    )
    standard_state = state.copy()
    initial_measurement = _measurement(state)
    maximum_compensated_drift = 0.0
    maximum_single_correction_norm = 0.0
    cumulative_correction_norm = 0.0
    maximum_standard_state_difference = 0.0
    maximum_independent_sum_component_difference = 0.0
    minimum_population = float(np.min(state))
    correction_records = []
    tangent = equilibrium_tangent_matrix()
    site_count = float(model.size * model.size)

    for step in range(1, REGISTERED_STEPS + 1):
        before = _measurement(state)
        mapped = model.full_map(state.ravel()).reshape(state.shape)
        after = _measurement(mapped)
        local_error = after["fsum"] - before["fsum"]
        local_correction = tangent @ local_error / site_count
        corrected = mapped - local_correction[None, None, :]
        corrected_measurement = _measurement(corrected)
        correction_norm = float(
            np.sqrt(site_count) * np.linalg.norm(local_correction)
        )
        remaining_local_drift = corrected_measurement["fsum"] - before["fsum"]
        compensated_drift = (
            corrected_measurement["fsum"] - initial_measurement["fsum"]
        )
        standard_state = model.full_map(standard_state.ravel()).reshape(state.shape)
        standard_state_difference = float(np.linalg.norm(corrected - standard_state))
        maximum_compensated_drift = max(
            maximum_compensated_drift,
            float(np.linalg.norm(compensated_drift)),
        )
        maximum_single_correction_norm = max(
            maximum_single_correction_norm,
            correction_norm,
        )
        cumulative_correction_norm += correction_norm
        maximum_standard_state_difference = max(
            maximum_standard_state_difference,
            standard_state_difference,
        )
        maximum_independent_sum_component_difference = max(
            maximum_independent_sum_component_difference,
            float(
                np.max(
                    np.abs(
                        corrected_measurement["fsum"]
                        - corrected_measurement["neumaier"]
                    )
                )
            ),
        )
        minimum_population = min(minimum_population, float(np.min(corrected)))
        correction_records.append(
            {
                "step": step,
                "pre_projection_fsum_error": local_error.tolist(),
                "correction_norm": correction_norm,
                "remaining_local_fsum_drift": remaining_local_drift.tolist(),
                "total_compensated_fsum_drift": compensated_drift.tolist(),
                "standard_state_difference": standard_state_difference,
            }
        )
        state = corrected

    return {
        "chart": chart_name,
        "direction_index": direction_index,
        "correction_records": correction_records,
        "summary": {
            "maximum_compensated_conservation_drift": maximum_compensated_drift,
            "maximum_single_correction_norm": maximum_single_correction_norm,
            "cumulative_correction_norm": cumulative_correction_norm,
            "maximum_standard_state_difference": maximum_standard_state_difference,
            "maximum_independent_sum_component_difference": (
                maximum_independent_sum_component_difference
            ),
            "minimum_population": minimum_population,
        },
    }


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_conservation_drift_audit() -> dict[str, Any]:
    """Run the sealed Q006j reduction, stage, and projection controls."""

    model = build_full2d_quadratic_model()
    directions = _normalized_directions()
    trajectory_records = [
        _trajectory_audit(
            model,
            direction,
            direction_index,
            quadratic=quadratic,
        )
        for quadratic in (False, True)
        for direction_index, direction in enumerate(directions)
    ]
    projection_records = [
        _projection_control_trajectory(
            model,
            direction,
            direction_index,
            quadratic=quadratic,
        )
        for quadratic in (False, True)
        for direction_index, direction in enumerate(directions)
    ]
    naive_witness = _maximum_trajectory_witness(trajectory_records, "numpy")
    fsum_witness = _maximum_trajectory_witness(trajectory_records, "fsum")
    neumaier_witness = _maximum_trajectory_witness(trajectory_records, "neumaier")
    maximum_independent_sum_difference = max(
        record["summary"]["maximum_independent_sum_component_difference"]
        for record in trajectory_records
    )
    maximum_stage_map_identity_error = max(
        record["summary"]["maximum_stage_map_identity_error"]
        for record in trajectory_records
    )
    maximum_streaming_drift = max(
        record["summary"]["maximum_streaming_fsum_drift"]
        for record in trajectory_records
    )
    maximum_reconstruction_error = max(
        record["summary"]["maximum_stage_reconstruction_error"]
        for record in trajectory_records
    )
    maximum_projection_drift = max(
        record["summary"]["maximum_compensated_conservation_drift"]
        for record in projection_records
    )
    maximum_single_correction_norm = max(
        record["summary"]["maximum_single_correction_norm"]
        for record in projection_records
    )
    minimum_projection_population = min(
        record["summary"]["minimum_population"] for record in projection_records
    )
    summary = {
        "trajectory_count": len(trajectory_records),
        "stage_record_count": sum(
            len(record["stage_records"]) for record in trajectory_records
        ),
        "checkpoint_record_count": sum(
            len(record["checkpoint_records"]) for record in trajectory_records
        ),
        "maximum_numpy_conservation_drift": naive_witness,
        "maximum_fsum_conservation_drift": fsum_witness,
        "maximum_neumaier_conservation_drift": neumaier_witness,
        "maximum_independent_sum_component_difference": (
            maximum_independent_sum_difference
        ),
        "maximum_numpy_fsum_measurement_difference": max(
            record["summary"]["maximum_numpy_fsum_difference"]
            for record in trajectory_records
        ),
        "maximum_stage_map_identity_error": maximum_stage_map_identity_error,
        "maximum_streaming_fsum_drift": maximum_streaming_drift,
        "maximum_stage_reconstruction_error": maximum_reconstruction_error,
        "stage_statistics": {
            stage_name: _stage_statistics(trajectory_records, stage_name)
            for stage_name in ("collision", "streaming", "filter")
        },
        "projection_control": {
            "maximum_compensated_conservation_drift": maximum_projection_drift,
            "maximum_single_correction_norm": maximum_single_correction_norm,
            "maximum_cumulative_correction_norm": max(
                record["summary"]["cumulative_correction_norm"]
                for record in projection_records
            ),
            "maximum_standard_state_difference": max(
                record["summary"]["maximum_standard_state_difference"]
                for record in projection_records
            ),
            "maximum_independent_sum_component_difference": max(
                record["summary"]["maximum_independent_sum_component_difference"]
                for record in projection_records
            ),
            "minimum_population": minimum_projection_population,
        },
    }
    serializable_probe = {
        "trajectory_records": trajectory_records,
        "projection_records": projection_records,
        "summary": summary,
    }
    validity_gates = {
        "registered_enumeration": {
            "value": {
                "trajectory_count": summary["trajectory_count"],
                "stage_record_count": summary["stage_record_count"],
                "checkpoint_record_count": summary["checkpoint_record_count"],
            },
            "threshold": {
                "trajectory_count": REGISTERED_TRAJECTORY_COUNT,
                "stage_record_count": REGISTERED_STAGE_RECORD_COUNT,
                "checkpoint_record_count": REGISTERED_CHECKPOINT_RECORD_COUNT,
            },
            "passed": (
                summary["trajectory_count"] == REGISTERED_TRAJECTORY_COUNT
                and summary["stage_record_count"] == REGISTERED_STAGE_RECORD_COUNT
                and summary["checkpoint_record_count"]
                == REGISTERED_CHECKPOINT_RECORD_COUNT
            ),
        },
        "independent_compensated_sums": {
            "value": maximum_independent_sum_difference,
            "threshold": INDEPENDENT_SUM_TOLERANCE,
            "passed": maximum_independent_sum_difference
            <= INDEPENDENT_SUM_TOLERANCE,
        },
        "stage_map_matches_q006i": {
            "value": maximum_stage_map_identity_error,
            "threshold": 0.0,
            "passed": maximum_stage_map_identity_error == 0.0,
        },
        "streaming_permutation_conservation": {
            "value": maximum_streaming_drift,
            "threshold": STREAMING_DRIFT_TOLERANCE,
            "passed": maximum_streaming_drift <= STREAMING_DRIFT_TOLERANCE,
        },
        "stage_telescoping_reconstruction": {
            "value": maximum_reconstruction_error,
            "threshold": STAGE_RECONSTRUCTION_TOLERANCE,
            "passed": maximum_reconstruction_error
            <= STAGE_RECONSTRUCTION_TOLERANCE,
        },
        "q006i_naive_drift_reproduction": {
            "value": abs(
                naive_witness["norm"] - REGISTERED_Q006I_MAXIMUM_DRIFT
            ),
            "threshold": Q006I_REPRODUCTION_TOLERANCE,
            "passed": abs(
                naive_witness["norm"] - REGISTERED_Q006I_MAXIMUM_DRIFT
            )
            <= Q006I_REPRODUCTION_TOLERANCE,
        },
        "strict_json_finite_values": {
            "value": _strict_json_serializable(serializable_probe),
            "threshold": True,
            "passed": _strict_json_serializable(serializable_probe),
        },
    }
    projection_gates = {
        "projected_conservation": {
            "value": maximum_projection_drift,
            "threshold": CONSERVATION_THRESHOLD,
            "passed": maximum_projection_drift <= CONSERVATION_THRESHOLD,
        },
        "single_projection_correction": {
            "value": maximum_single_correction_norm,
            "threshold": PROJECTION_CORRECTION_NORM_LIMIT,
            "passed": maximum_single_correction_norm
            <= PROJECTION_CORRECTION_NORM_LIMIT,
        },
        "projected_positivity": {
            "value": minimum_projection_population,
            "threshold": 0.0,
            "passed": minimum_projection_population > 0.0,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    projection_passed = all(gate["passed"] for gate in projection_gates.values())
    naive_exceeds = naive_witness["norm"] > CONSERVATION_THRESHOLD
    fsum_exceeds = fsum_witness["norm"] > CONSERVATION_THRESHOLD
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006j arithmetic audit validity failure"
        decision = (
            "A registered enumeration, independent-sum, stage, reproduction, "
            "or serialization validity gate failed."
        )
        next_change = "Repair the first failed Q006j validity gate without tuning it."
    elif naive_exceeds and not fsum_exceeds:
        outcome = "accepted"
        classification = "reduction-only conservation measurement failure"
        decision = (
            "Compensated measurement stays below the sealed threshold, so the "
            "Q006i excess is localized to the original NumPy reduction."
        )
        next_change = (
            "Preregister compensated conservation measurement for future studies "
            "without changing the sealed Q006i verdict."
        )
    elif naive_exceeds and fsum_exceeds and projection_passed:
        outcome = "accepted"
        classification = "float64 map roundoff accumulation localized"
        decision = (
            "Compensated measurement confirms state drift, stage increments "
            "reconstruct it, and the registered roundoff projection controls it."
        )
        next_change = (
            "Preregister whether a conservation-projected arithmetic realization "
            "or the explicitly non-bitwise-conservative float64 map is carried forward."
        )
    else:
        outcome = "rejected"
        classification = "structural or unresolved conservation defect"
        decision = (
            "The registered reduction/stage/projection controls do not localize "
            "the Q006i conservation failure to bounded float64 accumulation."
        )
        next_change = "Stop chart continuation and isolate the failed projection gate."
    return {
        "question": (
            "Is the single Q006i conservation failure a reduction artifact or a "
            "stage-localized float64 state drift?"
        ),
        "hypothesis": (
            "The excess is either reduction-only or reproducible float64 map "
            "roundoff controlled by the sealed fixed-leaf projection."
        ),
        "registered_setup": {
            "size": model.size,
            "omega": model.omega,
            "eta": model.eta,
            "direction_seed": SHADOW_SEED,
            "direction_count": REGISTERED_DIRECTION_COUNT,
            "chart_types": ["linear", "quadratic"],
            "amplitude": REGISTERED_AMPLITUDE,
            "steps": REGISTERED_STEPS,
            "checkpoints": list(REGISTERED_CHECKPOINTS),
            "aggregation_methods": ["numpy", "math.fsum", "neumaier"],
        },
        "trajectory_records": trajectory_records,
        "projection_control_records": projection_records,
        "summary": summary,
        "validity_gates": validity_gates,
        "projection_gates": projection_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "This is a finite 64-trajectory arithmetic audit. It does not alter "
            "the sealed Q006i rejection or threshold and is not a theorem of exact "
            "conservation for all states or all time horizons."
        ),
    }
