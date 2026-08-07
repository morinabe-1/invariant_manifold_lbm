"""Sealed Q006k audit of fixed-leaf projection representability."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any

import numpy as np
import numpy.typing as npt

from .conservation_drift import compensated_conserved_quantities
from .d2q9 import conserved_moment_matrix, equilibrium_tangent_matrix
from .full2d_chart import (
    SHADOW_SEED,
    Full2DQuadraticModel,
    build_full2d_quadratic_model,
)

Array = npt.NDArray[np.float64]

REGISTERED_DIRECTION_COUNT = 32
REGISTERED_AMPLITUDE = 0.01
REGISTERED_STEPS = 100
REGISTERED_TRAJECTORY_COUNT = 64
REGISTERED_CONTROL_STEP_COUNT = 6400
REGISTERED_TOTAL_CONTROL_STEP_COUNT = 19200
REGISTERED_STANDARD_DRIFT = 2.7285041507210106e-12
REGISTERED_UNIFORM_DRIFT = 2.1600518690316044e-12

REPRODUCTION_TOLERANCE = 5.0e-15
INDEPENDENT_SUM_TOLERANCE = 5.0e-14
MOMENT_MATRIX_CONDITION_LIMIT = 10.0
MOMENT_SOLVE_RESIDUAL_LIMIT = 1.0e-15
CONSERVATION_LIMIT = 1.0e-12
LOCALIZED_CORRECTION_LIMIT = 1.0e-11
LOCALIZED_STATE_DIFFERENCE_LIMIT = 1.0e-10

PIVOT_SITE = (0, 0)
PIVOT_POPULATIONS = (0, 1, 2)


def _normalized_directions() -> Array:
    rng = np.random.default_rng(SHADOW_SEED)
    directions = rng.normal(size=(REGISTERED_DIRECTION_COUNT, 24))
    return np.asarray(
        directions / np.linalg.norm(directions, axis=1)[:, None],
        dtype=np.float64,
    )


def _measurement(state: Array) -> tuple[Array, Array]:
    return compensated_conserved_quantities(state)


def _array_hash(value: Array) -> str:
    contiguous = np.ascontiguousarray(value, dtype=np.float64)
    return sha256(contiguous.view(np.uint8)).hexdigest()


def _new_drift_record() -> dict[str, Any]:
    return {
        "norm": 0.0,
        "step": 0,
        "signed_drift": [0.0, 0.0, 0.0],
        "component": "mass",
        "signed_value": 0.0,
    }


def _update_drift_record(record: dict[str, Any], drift: Array, step: int) -> None:
    norm = float(np.linalg.norm(drift))
    if norm <= record["norm"]:
        return
    component_index = int(np.argmax(np.abs(drift)))
    record.update(
        {
            "norm": norm,
            "step": step,
            "signed_drift": drift.tolist(),
            "component": ("mass", "momentum_x", "momentum_y")[component_index],
            "signed_value": float(drift[component_index]),
        }
    )


def _uniform_projection(
    mapped: Array,
    moment_error: Array,
    tangent: Array,
) -> tuple[Array, dict[str, Any]]:
    site_count = mapped.shape[0] * mapped.shape[1]
    intended_per_site = -(tangent @ moment_error) / float(site_count)
    intended_state_delta = np.broadcast_to(intended_per_site, mapped.shape)
    corrected = mapped + intended_state_delta
    realized_state_delta = corrected - mapped
    mapped_fsum, _ = _measurement(mapped)
    corrected_fsum, _ = _measurement(corrected)
    intended_global_correction = -moment_error
    realized_global_correction = corrected_fsum - mapped_fsum
    correction_error = realized_global_correction - intended_global_correction
    nonzero_mask = intended_state_delta != 0.0
    spacing = np.abs(np.spacing(mapped))
    ratios = np.abs(intended_state_delta[nonzero_mask]) / spacing[nonzero_mask]
    changed_count = int(np.count_nonzero(realized_state_delta))
    return corrected, {
        "intended_global_moment_correction": intended_global_correction.tolist(),
        "intended_population_correction": intended_per_site.tolist(),
        "intended_state_correction_norm": float(
            np.sqrt(float(site_count)) * np.linalg.norm(intended_per_site)
        ),
        "realized_state_delta_sha256": _array_hash(realized_state_delta),
        "realized_state_delta_norm": float(np.linalg.norm(realized_state_delta)),
        "realized_state_delta_maximum_absolute_entry": float(
            np.max(np.abs(realized_state_delta))
        ),
        "changed_population_count": changed_count,
        "changed_population_fraction": changed_count / float(mapped.size),
        "nonzero_intended_population_count": int(np.count_nonzero(nonzero_mask)),
        "ulp_ratio": {
            "minimum": float(np.min(ratios)),
            "median": float(np.median(ratios)),
            "maximum": float(np.max(ratios)),
        },
        "realized_global_moment_correction": realized_global_correction.tolist(),
        "realized_global_correction_error": correction_error.tolist(),
        "realized_global_correction_error_norm": float(
            np.linalg.norm(correction_error)
        ),
    }


def _localized_projection(
    mapped: Array,
    moment_error: Array,
    moment_matrix: Array,
) -> tuple[Array, dict[str, Any]]:
    delta = np.asarray(
        [
            -moment_error[0] + moment_error[1] + moment_error[2],
            -moment_error[1],
            -moment_error[2],
        ],
        dtype=np.float64,
    )
    solve_residual = moment_matrix @ delta + moment_error
    corrected = mapped.copy()
    corrected[PIVOT_SITE[0], PIVOT_SITE[1], list(PIVOT_POPULATIONS)] += delta
    mapped_fsum, _ = _measurement(mapped)
    corrected_fsum, _ = _measurement(corrected)
    realized_global_correction = corrected_fsum - mapped_fsum
    intended_global_correction = -moment_error
    correction_error = realized_global_correction - intended_global_correction
    return corrected, {
        "intended_population_correction": delta.tolist(),
        "intended_global_moment_correction": intended_global_correction.tolist(),
        "moment_solve_residual": solve_residual.tolist(),
        "moment_solve_residual_norm": float(np.linalg.norm(solve_residual)),
        "correction_norm": float(np.linalg.norm(delta)),
        "realized_population_delta": (
            corrected[PIVOT_SITE[0], PIVOT_SITE[1], list(PIVOT_POPULATIONS)]
            - mapped[PIVOT_SITE[0], PIVOT_SITE[1], list(PIVOT_POPULATIONS)]
        ).tolist(),
        "realized_global_moment_correction": realized_global_correction.tolist(),
        "realized_global_correction_error": correction_error.tolist(),
        "realized_global_correction_error_norm": float(
            np.linalg.norm(correction_error)
        ),
    }


def _trajectory_audit(
    model: Full2DQuadraticModel,
    direction: Array,
    direction_index: int,
    moment_matrix: Array,
    *,
    quadratic: bool,
) -> dict[str, Any]:
    chart = model.chart if quadratic else model.linear_chart
    chart_name = "quadratic" if quadratic else "linear"
    initial = chart.evaluate(REGISTERED_AMPLITUDE * direction).reshape(
        model.size,
        model.size,
        9,
    )
    standard_state = initial.copy()
    uniform_state = initial.copy()
    localized_state = initial.copy()
    initial_fsum, initial_neumaier = _measurement(initial)
    maximum_independent_sum_difference = float(
        np.max(np.abs(initial_fsum - initial_neumaier))
    )
    maximum_drift = {
        "standard": _new_drift_record(),
        "uniform": _new_drift_record(),
        "localized": _new_drift_record(),
    }
    maximum_uniform_correction_error = 0.0
    nonzero_uniform_correction_error_step_count = 0
    maximum_localized_correction_norm = 0.0
    maximum_localized_solve_residual = 0.0
    maximum_localized_standard_state_difference = 0.0
    minimum_localized_population = float(np.min(localized_state))
    step_records = []
    tangent = equilibrium_tangent_matrix()

    for step in range(1, REGISTERED_STEPS + 1):
        standard_state = model.full_map(standard_state.ravel()).reshape(initial.shape)
        standard_fsum, standard_neumaier = _measurement(standard_state)

        uniform_before_fsum, uniform_before_neumaier = _measurement(uniform_state)
        uniform_mapped = model.full_map(uniform_state.ravel()).reshape(initial.shape)
        uniform_mapped_fsum, uniform_mapped_neumaier = _measurement(uniform_mapped)
        uniform_error = uniform_mapped_fsum - uniform_before_fsum
        uniform_state, uniform_record = _uniform_projection(
            uniform_mapped,
            uniform_error,
            tangent,
        )
        uniform_fsum, uniform_neumaier = _measurement(uniform_state)
        uniform_remaining_error = uniform_fsum - uniform_before_fsum
        uniform_record["remaining_local_moment_error"] = (
            uniform_remaining_error.tolist()
        )
        uniform_record["remaining_local_moment_error_norm"] = float(
            np.linalg.norm(uniform_remaining_error)
        )

        localized_before_fsum, localized_before_neumaier = _measurement(
            localized_state
        )
        localized_mapped = model.full_map(localized_state.ravel()).reshape(
            initial.shape
        )
        localized_mapped_fsum, localized_mapped_neumaier = _measurement(
            localized_mapped
        )
        localized_error = localized_mapped_fsum - localized_before_fsum
        localized_state, localized_record = _localized_projection(
            localized_mapped,
            localized_error,
            moment_matrix,
        )
        localized_fsum, localized_neumaier = _measurement(localized_state)
        localized_remaining_error = localized_fsum - localized_before_fsum
        localized_record["remaining_local_moment_error"] = (
            localized_remaining_error.tolist()
        )
        localized_record["remaining_local_moment_error_norm"] = float(
            np.linalg.norm(localized_remaining_error)
        )
        localized_standard_difference = float(
            np.linalg.norm(localized_state - standard_state)
        )
        localized_record["standard_state_difference"] = (
            localized_standard_difference
        )

        all_measurement_pairs = (
            (standard_fsum, standard_neumaier),
            (uniform_before_fsum, uniform_before_neumaier),
            (uniform_mapped_fsum, uniform_mapped_neumaier),
            (uniform_fsum, uniform_neumaier),
            (localized_before_fsum, localized_before_neumaier),
            (localized_mapped_fsum, localized_mapped_neumaier),
            (localized_fsum, localized_neumaier),
        )
        maximum_independent_sum_difference = max(
            maximum_independent_sum_difference,
            *(
                float(np.max(np.abs(faithful - neumaier)))
                for faithful, neumaier in all_measurement_pairs
            ),
        )
        drifts = {
            "standard": standard_fsum - initial_fsum,
            "uniform": uniform_fsum - initial_fsum,
            "localized": localized_fsum - initial_fsum,
        }
        for control_name, drift in drifts.items():
            _update_drift_record(maximum_drift[control_name], drift, step)

        correction_error = uniform_record[
            "realized_global_correction_error_norm"
        ]
        maximum_uniform_correction_error = max(
            maximum_uniform_correction_error,
            correction_error,
        )
        if correction_error > 0.0:
            nonzero_uniform_correction_error_step_count += 1
        maximum_localized_correction_norm = max(
            maximum_localized_correction_norm,
            localized_record["correction_norm"],
        )
        maximum_localized_solve_residual = max(
            maximum_localized_solve_residual,
            localized_record["moment_solve_residual_norm"],
        )
        maximum_localized_standard_state_difference = max(
            maximum_localized_standard_state_difference,
            localized_standard_difference,
        )
        minimum_localized_population = min(
            minimum_localized_population,
            float(np.min(localized_state)),
        )
        step_records.append(
            {
                "step": step,
                "standard_fsum_drift": drifts["standard"].tolist(),
                "uniform": uniform_record,
                "uniform_fsum_drift": drifts["uniform"].tolist(),
                "localized": localized_record,
                "localized_fsum_drift": drifts["localized"].tolist(),
            }
        )

    ulp_minima = [record["uniform"]["ulp_ratio"]["minimum"] for record in step_records]
    ulp_medians = [record["uniform"]["ulp_ratio"]["median"] for record in step_records]
    ulp_maxima = [record["uniform"]["ulp_ratio"]["maximum"] for record in step_records]
    changed_counts = [
        record["uniform"]["changed_population_count"] for record in step_records
    ]
    return {
        "chart": chart_name,
        "direction_index": direction_index,
        "direction": direction.tolist(),
        "step_records": step_records,
        "summary": {
            "maximum_drift": maximum_drift,
            "maximum_independent_sum_component_difference": (
                maximum_independent_sum_difference
            ),
            "uniform_representability": {
                "nonzero_correction_error_step_count": (
                    nonzero_uniform_correction_error_step_count
                ),
                "maximum_global_correction_error_norm": (
                    maximum_uniform_correction_error
                ),
                "minimum_changed_population_count": min(changed_counts),
                "maximum_changed_population_count": max(changed_counts),
                "mean_changed_population_count": float(np.mean(changed_counts)),
                "minimum_ulp_ratio": min(ulp_minima),
                "median_of_step_median_ulp_ratios": float(np.median(ulp_medians)),
                "maximum_ulp_ratio": max(ulp_maxima),
            },
            "maximum_localized_correction_norm": (
                maximum_localized_correction_norm
            ),
            "maximum_localized_solve_residual": maximum_localized_solve_residual,
            "maximum_localized_standard_state_difference": (
                maximum_localized_standard_state_difference
            ),
            "minimum_localized_population": minimum_localized_population,
        },
    }


def _maximum_control_witness(
    records: list[dict[str, Any]],
    control_name: str,
) -> dict[str, Any]:
    record = max(
        records,
        key=lambda value: value["summary"]["maximum_drift"][control_name]["norm"],
    )
    return {
        "chart": record["chart"],
        "direction_index": record["direction_index"],
        **record["summary"]["maximum_drift"][control_name],
    }


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_projection_representability_audit() -> dict[str, Any]:
    """Run the sealed Q006k uniform-versus-localized projection audit."""

    model = build_full2d_quadratic_model()
    directions = _normalized_directions()
    moment_matrix = conserved_moment_matrix()[:, list(PIVOT_POPULATIONS)]
    matrix_rank = int(np.linalg.matrix_rank(moment_matrix))
    matrix_condition = float(np.linalg.cond(moment_matrix))
    records = [
        _trajectory_audit(
            model,
            direction,
            direction_index,
            moment_matrix,
            quadratic=quadratic,
        )
        for quadratic in (False, True)
        for direction_index, direction in enumerate(directions)
    ]
    standard_witness = _maximum_control_witness(records, "standard")
    uniform_witness = _maximum_control_witness(records, "uniform")
    localized_witness = _maximum_control_witness(records, "localized")
    maximum_independent_sum_difference = max(
        record["summary"]["maximum_independent_sum_component_difference"]
        for record in records
    )
    maximum_solve_residual = max(
        record["summary"]["maximum_localized_solve_residual"] for record in records
    )
    nonzero_uniform_error_steps = sum(
        record["summary"]["uniform_representability"][
            "nonzero_correction_error_step_count"
        ]
        for record in records
    )
    maximum_uniform_correction_error = max(
        record["summary"]["uniform_representability"][
            "maximum_global_correction_error_norm"
        ]
        for record in records
    )
    maximum_localized_correction = max(
        record["summary"]["maximum_localized_correction_norm"] for record in records
    )
    maximum_localized_state_difference = max(
        record["summary"]["maximum_localized_standard_state_difference"]
        for record in records
    )
    minimum_localized_population = min(
        record["summary"]["minimum_localized_population"] for record in records
    )
    summary = {
        "trajectory_count": len(records),
        "step_record_count_per_control": sum(
            len(record["step_records"]) for record in records
        ),
        "total_control_step_count": 3
        * sum(len(record["step_records"]) for record in records),
        "maximum_standard_fsum_drift": standard_witness,
        "maximum_uniform_fsum_drift": uniform_witness,
        "maximum_localized_fsum_drift": localized_witness,
        "maximum_independent_sum_component_difference": (
            maximum_independent_sum_difference
        ),
        "moment_matrix": {
            "values": moment_matrix.tolist(),
            "rank": matrix_rank,
            "condition_number": matrix_condition,
            "maximum_solve_residual": maximum_solve_residual,
        },
        "uniform_representability": {
            "nonzero_global_correction_error_step_count": (
                nonzero_uniform_error_steps
            ),
            "maximum_global_correction_error_norm": (
                maximum_uniform_correction_error
            ),
            "minimum_changed_population_count": min(
                record["summary"]["uniform_representability"][
                    "minimum_changed_population_count"
                ]
                for record in records
            ),
            "maximum_changed_population_count": max(
                record["summary"]["uniform_representability"][
                    "maximum_changed_population_count"
                ]
                for record in records
            ),
            "mean_changed_population_count": float(
                np.mean(
                    [
                        record["summary"]["uniform_representability"][
                            "mean_changed_population_count"
                        ]
                        for record in records
                    ]
                )
            ),
            "minimum_ulp_ratio": min(
                record["summary"]["uniform_representability"][
                    "minimum_ulp_ratio"
                ]
                for record in records
            ),
            "median_of_trajectory_step_median_ulp_ratios": float(
                np.median(
                    [
                        record["summary"]["uniform_representability"][
                            "median_of_step_median_ulp_ratios"
                        ]
                        for record in records
                    ]
                )
            ),
            "maximum_ulp_ratio": max(
                record["summary"]["uniform_representability"][
                    "maximum_ulp_ratio"
                ]
                for record in records
            ),
        },
        "maximum_localized_correction_norm": maximum_localized_correction,
        "maximum_localized_standard_state_difference": (
            maximum_localized_state_difference
        ),
        "minimum_localized_population": minimum_localized_population,
    }
    serializable_probe = {"records": records, "summary": summary}
    validity_gates = {
        "registered_enumeration": {
            "value": {
                "trajectory_count": summary["trajectory_count"],
                "step_record_count_per_control": summary[
                    "step_record_count_per_control"
                ],
                "total_control_step_count": summary["total_control_step_count"],
            },
            "threshold": {
                "trajectory_count": REGISTERED_TRAJECTORY_COUNT,
                "step_record_count_per_control": REGISTERED_CONTROL_STEP_COUNT,
                "total_control_step_count": REGISTERED_TOTAL_CONTROL_STEP_COUNT,
            },
            "passed": (
                summary["trajectory_count"] == REGISTERED_TRAJECTORY_COUNT
                and summary["step_record_count_per_control"]
                == REGISTERED_CONTROL_STEP_COUNT
                and summary["total_control_step_count"]
                == REGISTERED_TOTAL_CONTROL_STEP_COUNT
            ),
        },
        "q006j_standard_reproduction": {
            "value": abs(standard_witness["norm"] - REGISTERED_STANDARD_DRIFT),
            "threshold": REPRODUCTION_TOLERANCE,
            "passed": abs(
                standard_witness["norm"] - REGISTERED_STANDARD_DRIFT
            )
            <= REPRODUCTION_TOLERANCE,
        },
        "q006j_uniform_reproduction": {
            "value": abs(uniform_witness["norm"] - REGISTERED_UNIFORM_DRIFT),
            "threshold": REPRODUCTION_TOLERANCE,
            "passed": abs(uniform_witness["norm"] - REGISTERED_UNIFORM_DRIFT)
            <= REPRODUCTION_TOLERANCE,
        },
        "independent_compensated_sums": {
            "value": maximum_independent_sum_difference,
            "threshold": INDEPENDENT_SUM_TOLERANCE,
            "passed": maximum_independent_sum_difference
            <= INDEPENDENT_SUM_TOLERANCE,
        },
        "localized_moment_matrix": {
            "value": {
                "rank": matrix_rank,
                "condition_number": matrix_condition,
                "maximum_solve_residual": maximum_solve_residual,
            },
            "threshold": {
                "rank": 3,
                "condition_number": MOMENT_MATRIX_CONDITION_LIMIT,
                "maximum_solve_residual": MOMENT_SOLVE_RESIDUAL_LIMIT,
            },
            "passed": (
                matrix_rank == 3
                and matrix_condition <= MOMENT_MATRIX_CONDITION_LIMIT
                and maximum_solve_residual <= MOMENT_SOLVE_RESIDUAL_LIMIT
            ),
        },
        "strict_json_finite_values": {
            "value": _strict_json_serializable(serializable_probe),
            "threshold": True,
            "passed": _strict_json_serializable(serializable_probe),
        },
    }
    hypothesis_gates = {
        "uniform_realization_error_observed": {
            "value": nonzero_uniform_error_steps,
            "threshold": 1,
            "passed": nonzero_uniform_error_steps >= 1,
        },
        "localized_conservation": {
            "value": localized_witness["norm"],
            "threshold": CONSERVATION_LIMIT,
            "passed": localized_witness["norm"] <= CONSERVATION_LIMIT,
        },
        "localized_single_correction": {
            "value": maximum_localized_correction,
            "threshold": LOCALIZED_CORRECTION_LIMIT,
            "passed": maximum_localized_correction
            <= LOCALIZED_CORRECTION_LIMIT,
        },
        "localized_standard_state_difference": {
            "value": maximum_localized_state_difference,
            "threshold": LOCALIZED_STATE_DIFFERENCE_LIMIT,
            "passed": maximum_localized_state_difference
            <= LOCALIZED_STATE_DIFFERENCE_LIMIT,
        },
        "localized_positivity": {
            "value": minimum_localized_population,
            "threshold": 0.0,
            "passed": minimum_localized_population > 0.0,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006k projection audit validity failure"
        decision = (
            "A registered enumeration, reproduction, independent-sum, moment-"
            "matrix, or serialization gate failed."
        )
        next_change = "Repair the first Q006k validity failure without tuning it."
    elif hypothesis_passed:
        outcome = "accepted"
        classification = "uniform projection representability failure localized"
        decision = (
            "The distributed correction is not realized exactly, while the fixed "
            "three-population diagnostic controls the registered conservation drift."
        )
        next_change = (
            "Preregister a symmetry-preserving conservative arithmetic realization "
            "for collision and filtering; do not adopt the fixed-site diagnostic."
        )
    else:
        outcome = "rejected"
        classification = "localized correction does not resolve projection failure"
        decision = (
            "At least one registered representability, conservation, correction, "
            "state-difference, or positivity gate failed."
        )
        next_change = "Stop continuation and isolate the first failed Q006k gate."
    return {
        "question": (
            "Does sub-ULP distribution explain the Q006j uniform projection "
            "failure, with a fixed three-population diagnostic controlling drift?"
        ),
        "hypothesis": (
            "Uniform correction has a nonzero realization error and the sealed "
            "localized control restores the registered conservation bound."
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
            "controls": ["standard", "uniform", "localized"],
            "pivot_site": list(PIVOT_SITE),
            "pivot_populations": list(PIVOT_POPULATIONS),
            "localized_refinement_passes": 1,
        },
        "trajectory_records": records,
        "summary": summary,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "The fixed-site correction is a symmetry-breaking diagnostic only. "
            "It is not adopted as the production map and does not alter the sealed "
            "Q006i or Q006j outcomes or thresholds."
        ),
    }
