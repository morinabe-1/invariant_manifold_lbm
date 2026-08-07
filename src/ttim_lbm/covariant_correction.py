"""Sealed Q006l stagewise state-covariant conservation audit."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import numpy as np
import numpy.typing as npt

from .checkerboard_filter import conservative_checkerboard_filter
from .conservation_drift import compensated_conserved_quantities
from .d2q9 import (
    collide_bgk,
    conserved_moment_matrix,
    quarter_turn_population_matrix,
    stream_periodic,
)
from .full2d_chart import (
    SHADOW_SEED,
    Full2DQuadraticModel,
    build_full2d_quadratic_model,
)

Array = npt.NDArray[np.float64]
Anchor = tuple[int, int]
StateTransform = Callable[[Array], Array]

REGISTERED_DIRECTION_COUNT = 32
REGISTERED_AMPLITUDE = 0.01
REGISTERED_STEPS = 100
REGISTERED_TRAJECTORY_COUNT = 64
REGISTERED_STEP_COUNT_PER_CONTROL = 6400
REGISTERED_TOTAL_CONTROL_STEP_COUNT = 19200
REGISTERED_STANDARD_DRIFT = 2.7285041507210106e-12
REGISTERED_FIXED_DRIFT = 1.5115007100657805e-16

REPRODUCTION_TOLERANCE = 5.0e-15
INDEPENDENT_SUM_TOLERANCE = 5.0e-14
ANCHOR_GAP_MINIMUM = 1.0e-12
RIGHT_INVERSE_CONDITION_LIMIT = 10.0
RIGHT_INVERSE_RESIDUAL_LIMIT = 1.0e-14
CONSERVATION_LIMIT = 1.0e-12
CORRECTION_NORM_LIMIT = 1.0e-11
STATE_DIFFERENCE_LIMIT = 1.0e-10
EQUIVARIANCE_LIMIT = 1.0e-13

FIXED_SITE = (0, 0)
FIXED_POPULATIONS = (0, 1, 2)


def _normalized_directions() -> Array:
    rng = np.random.default_rng(SHADOW_SEED)
    directions = rng.normal(size=(REGISTERED_DIRECTION_COUNT, 24))
    return np.asarray(
        directions / np.linalg.norm(directions, axis=1)[:, None],
        dtype=np.float64,
    )


def _measurement(state: Array) -> tuple[Array, Array]:
    return compensated_conserved_quantities(state)


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


def _anchor_and_gap(state: Array) -> tuple[Anchor, float]:
    rest = np.asarray(state[..., 0], dtype=np.float64)
    flat = rest.ravel()
    maximum_index = int(np.argmax(flat))
    largest_two = np.partition(flat, -2)[-2:]
    gap = float(np.max(largest_two) - np.min(largest_two))
    return tuple(int(value) for value in np.unravel_index(maximum_index, rest.shape)), gap


def _covariant_stage_correction(
    before: Array,
    raw_after: Array,
    right_inverse: Array,
) -> tuple[Array, dict[str, Any]]:
    before_fsum, before_neumaier = _measurement(before)
    raw_fsum, raw_neumaier = _measurement(raw_after)
    error = raw_fsum - before_fsum
    anchor, gap = _anchor_and_gap(raw_after)
    delta = -(right_inverse @ error)
    corrected = raw_after.copy()
    corrected[anchor[0], anchor[1], :] += delta
    corrected_fsum, corrected_neumaier = _measurement(corrected)
    realized = corrected_fsum - raw_fsum
    remaining = corrected_fsum - before_fsum
    independent_sum_difference = max(
        float(np.max(np.abs(before_fsum - before_neumaier))),
        float(np.max(np.abs(raw_fsum - raw_neumaier))),
        float(np.max(np.abs(corrected_fsum - corrected_neumaier))),
    )
    return corrected, {
        "anchor": list(anchor),
        "anchor_gap": gap,
        "raw_stage_moment_error": error.tolist(),
        "intended_population_correction": delta.tolist(),
        "correction_norm": float(np.linalg.norm(delta)),
        "realized_global_moment_correction": realized.tolist(),
        "realization_error": (realized + error).tolist(),
        "realization_error_norm": float(np.linalg.norm(realized + error)),
        "remaining_stage_moment_error": remaining.tolist(),
        "remaining_stage_moment_error_norm": float(np.linalg.norm(remaining)),
        "maximum_independent_sum_component_difference": (
            independent_sum_difference
        ),
    }


def _fixed_full_step_correction(before: Array, mapped: Array) -> Array:
    before_fsum, _ = _measurement(before)
    mapped_fsum, _ = _measurement(mapped)
    error = mapped_fsum - before_fsum
    delta = np.asarray(
        [
            -error[0] + error[1] + error[2],
            -error[1],
            -error[2],
        ],
        dtype=np.float64,
    )
    corrected = mapped.copy()
    corrected[FIXED_SITE[0], FIXED_SITE[1], list(FIXED_POPULATIONS)] += delta
    return corrected


def _translate(shift: tuple[int, int]) -> StateTransform:
    def transform(state: Array) -> Array:
        return np.roll(state, shift=shift, axis=(0, 1))

    return transform


def _quarter_turn(state: Array) -> Array:
    size = state.shape[0]
    target_y, target_x = np.indices((size, size))
    pulled_back = state[(-target_x) % size, target_y]
    rotation = quarter_turn_population_matrix()
    return np.einsum("qr,xyr->xyq", rotation, pulled_back)


def _transformed_anchor(
    anchor: Anchor,
    generator: str,
    size: int,
) -> Anchor:
    y, x = anchor
    if generator == "translation_y":
        return (y + 1) % size, x
    if generator == "translation_x":
        return y, (x + 1) % size
    if generator == "quarter_turn":
        return x, (-y) % size
    raise ValueError(f"unknown symmetry generator: {generator}")


def _symmetry_audit(
    before: Array,
    raw_after: Array,
    corrected: Array,
    anchor: Anchor,
    right_inverse: Array,
) -> dict[str, Any]:
    generators: tuple[tuple[str, StateTransform], ...] = (
        ("translation_y", _translate((1, 0))),
        ("translation_x", _translate((0, 1))),
        ("quarter_turn", _quarter_turn),
    )
    records = {}
    for generator, transform in generators:
        transformed_corrected, transformed_record = _covariant_stage_correction(
            transform(before),
            transform(raw_after),
            right_inverse,
        )
        expected = transform(corrected)
        expected_anchor = _transformed_anchor(anchor, generator, before.shape[0])
        actual_anchor = tuple(transformed_record["anchor"])
        records[generator] = {
            "equivariance_error": float(
                np.linalg.norm(transformed_corrected - expected)
            ),
            "expected_anchor": list(expected_anchor),
            "actual_anchor": list(actual_anchor),
            "anchor_covariant": actual_anchor == expected_anchor,
        }
    return records


def _stagewise_step(
    state: Array,
    model: Full2DQuadraticModel,
    right_inverse: Array,
) -> tuple[Array, dict[str, Any]]:
    raw_collision = collide_bgk(state, model.omega)
    collision, collision_record = _covariant_stage_correction(
        state,
        raw_collision,
        right_inverse,
    )
    collision_symmetry = _symmetry_audit(
        state,
        raw_collision,
        collision,
        tuple(collision_record["anchor"]),
        right_inverse,
    )
    streamed = stream_periodic(collision)
    raw_filter = conservative_checkerboard_filter(streamed, model.eta)
    filtered, filter_record = _covariant_stage_correction(
        streamed,
        raw_filter,
        right_inverse,
    )
    filter_symmetry = _symmetry_audit(
        streamed,
        raw_filter,
        filtered,
        tuple(filter_record["anchor"]),
        right_inverse,
    )
    return filtered, {
        "collision": collision_record,
        "filter": filter_record,
        "symmetry": {
            "collision": collision_symmetry,
            "filter": filter_symmetry,
        },
    }


def _trajectory_audit(
    model: Full2DQuadraticModel,
    direction: Array,
    direction_index: int,
    right_inverse: Array,
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
    fixed_state = initial.copy()
    covariant_state = initial.copy()
    initial_fsum, initial_neumaier = _measurement(initial)
    maximum_independent_sum_difference = float(
        np.max(np.abs(initial_fsum - initial_neumaier))
    )
    maximum_drift = {
        "standard": _new_drift_record(),
        "fixed": _new_drift_record(),
        "covariant": _new_drift_record(),
    }
    minimum_anchor_gap = {"collision": np.inf, "filter": np.inf}
    anchor_covariance_failure_count = 0
    maximum_equivariance_error = {
        "translation": 0.0,
        "quarter_turn": 0.0,
    }
    maximum_correction_norm = 0.0
    maximum_covariant_standard_state_difference = 0.0
    minimum_covariant_population = float(np.min(covariant_state))
    step_records = []

    for step in range(1, REGISTERED_STEPS + 1):
        standard_state = model.full_map(standard_state.ravel()).reshape(initial.shape)
        standard_fsum, standard_neumaier = _measurement(standard_state)

        fixed_mapped = model.full_map(fixed_state.ravel()).reshape(initial.shape)
        fixed_state = _fixed_full_step_correction(fixed_state, fixed_mapped)
        fixed_fsum, fixed_neumaier = _measurement(fixed_state)

        covariant_state, covariant_record = _stagewise_step(
            covariant_state,
            model,
            right_inverse,
        )
        covariant_fsum, covariant_neumaier = _measurement(covariant_state)
        covariant_standard_difference = float(
            np.linalg.norm(covariant_state - standard_state)
        )
        drifts = {
            "standard": standard_fsum - initial_fsum,
            "fixed": fixed_fsum - initial_fsum,
            "covariant": covariant_fsum - initial_fsum,
        }
        for control, drift in drifts.items():
            _update_drift_record(maximum_drift[control], drift, step)

        maximum_independent_sum_difference = max(
            maximum_independent_sum_difference,
            float(np.max(np.abs(standard_fsum - standard_neumaier))),
            float(np.max(np.abs(fixed_fsum - fixed_neumaier))),
            float(np.max(np.abs(covariant_fsum - covariant_neumaier))),
            covariant_record["collision"][
                "maximum_independent_sum_component_difference"
            ],
            covariant_record["filter"][
                "maximum_independent_sum_component_difference"
            ],
        )
        for stage in ("collision", "filter"):
            stage_record = covariant_record[stage]
            minimum_anchor_gap[stage] = min(
                minimum_anchor_gap[stage],
                stage_record["anchor_gap"],
            )
            maximum_correction_norm = max(
                maximum_correction_norm,
                stage_record["correction_norm"],
            )
            for generator, symmetry_record in covariant_record["symmetry"][
                stage
            ].items():
                if not symmetry_record["anchor_covariant"]:
                    anchor_covariance_failure_count += 1
                symmetry_class = (
                    "quarter_turn" if generator == "quarter_turn" else "translation"
                )
                maximum_equivariance_error[symmetry_class] = max(
                    maximum_equivariance_error[symmetry_class],
                    symmetry_record["equivariance_error"],
                )
        maximum_covariant_standard_state_difference = max(
            maximum_covariant_standard_state_difference,
            covariant_standard_difference,
        )
        minimum_covariant_population = min(
            minimum_covariant_population,
            float(np.min(covariant_state)),
        )
        step_records.append(
            {
                "step": step,
                "standard_fsum_drift": drifts["standard"].tolist(),
                "fixed_fsum_drift": drifts["fixed"].tolist(),
                "covariant_fsum_drift": drifts["covariant"].tolist(),
                "covariant_standard_state_difference": (
                    covariant_standard_difference
                ),
                **covariant_record,
            }
        )

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
            "minimum_anchor_gap": minimum_anchor_gap,
            "anchor_covariance_failure_count": anchor_covariance_failure_count,
            "maximum_equivariance_error": maximum_equivariance_error,
            "maximum_correction_norm": maximum_correction_norm,
            "maximum_covariant_standard_state_difference": (
                maximum_covariant_standard_state_difference
            ),
            "minimum_covariant_population": minimum_covariant_population,
        },
    }


def _maximum_control_witness(
    records: list[dict[str, Any]],
    control: str,
) -> dict[str, Any]:
    record = max(
        records,
        key=lambda value: value["summary"]["maximum_drift"][control]["norm"],
    )
    return {
        "chart": record["chart"],
        "direction_index": record["direction_index"],
        **record["summary"]["maximum_drift"][control],
    }


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_covariant_correction_audit() -> dict[str, Any]:
    """Run the sealed Q006l stagewise symmetry and conservation audit."""

    model = build_full2d_quadratic_model()
    moment_matrix = conserved_moment_matrix()
    right_inverse = moment_matrix.T @ np.linalg.inv(
        moment_matrix @ moment_matrix.T
    )
    right_inverse_condition = float(np.linalg.cond(right_inverse))
    right_inverse_residual = float(
        np.linalg.norm(moment_matrix @ right_inverse - np.eye(3), ord=2)
    )
    directions = _normalized_directions()
    records = [
        _trajectory_audit(
            model,
            direction,
            direction_index,
            right_inverse,
            quadratic=quadratic,
        )
        for quadratic in (False, True)
        for direction_index, direction in enumerate(directions)
    ]
    standard_witness = _maximum_control_witness(records, "standard")
    fixed_witness = _maximum_control_witness(records, "fixed")
    covariant_witness = _maximum_control_witness(records, "covariant")
    maximum_independent_sum_difference = max(
        record["summary"]["maximum_independent_sum_component_difference"]
        for record in records
    )
    minimum_collision_anchor_gap = min(
        record["summary"]["minimum_anchor_gap"]["collision"]
        for record in records
    )
    minimum_filter_anchor_gap = min(
        record["summary"]["minimum_anchor_gap"]["filter"] for record in records
    )
    anchor_covariance_failures = sum(
        record["summary"]["anchor_covariance_failure_count"] for record in records
    )
    maximum_translation_error = max(
        record["summary"]["maximum_equivariance_error"]["translation"]
        for record in records
    )
    maximum_quarter_turn_error = max(
        record["summary"]["maximum_equivariance_error"]["quarter_turn"]
        for record in records
    )
    maximum_correction_norm = max(
        record["summary"]["maximum_correction_norm"] for record in records
    )
    maximum_state_difference = max(
        record["summary"]["maximum_covariant_standard_state_difference"]
        for record in records
    )
    minimum_population = min(
        record["summary"]["minimum_covariant_population"] for record in records
    )
    step_count = sum(len(record["step_records"]) for record in records)
    summary = {
        "trajectory_count": len(records),
        "step_record_count_per_control": step_count,
        "total_control_step_count": 3 * step_count,
        "maximum_standard_fsum_drift": standard_witness,
        "maximum_fixed_fsum_drift": fixed_witness,
        "maximum_covariant_fsum_drift": covariant_witness,
        "maximum_independent_sum_component_difference": (
            maximum_independent_sum_difference
        ),
        "right_inverse": {
            "values": right_inverse.tolist(),
            "condition_number": right_inverse_condition,
            "right_inverse_residual": right_inverse_residual,
        },
        "minimum_anchor_gap": {
            "collision": minimum_collision_anchor_gap,
            "filter": minimum_filter_anchor_gap,
        },
        "anchor_covariance_failure_count": anchor_covariance_failures,
        "maximum_translation_equivariance_error": maximum_translation_error,
        "maximum_quarter_turn_equivariance_error": maximum_quarter_turn_error,
        "maximum_single_correction_norm": maximum_correction_norm,
        "maximum_covariant_standard_state_difference": maximum_state_difference,
        "minimum_covariant_population": minimum_population,
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
                "step_record_count_per_control": REGISTERED_STEP_COUNT_PER_CONTROL,
                "total_control_step_count": REGISTERED_TOTAL_CONTROL_STEP_COUNT,
            },
            "passed": (
                summary["trajectory_count"] == REGISTERED_TRAJECTORY_COUNT
                and summary["step_record_count_per_control"]
                == REGISTERED_STEP_COUNT_PER_CONTROL
                and summary["total_control_step_count"]
                == REGISTERED_TOTAL_CONTROL_STEP_COUNT
            ),
        },
        "q006k_standard_reproduction": {
            "value": abs(standard_witness["norm"] - REGISTERED_STANDARD_DRIFT),
            "threshold": REPRODUCTION_TOLERANCE,
            "passed": abs(
                standard_witness["norm"] - REGISTERED_STANDARD_DRIFT
            )
            <= REPRODUCTION_TOLERANCE,
        },
        "q006k_fixed_reproduction": {
            "value": abs(fixed_witness["norm"] - REGISTERED_FIXED_DRIFT),
            "threshold": REPRODUCTION_TOLERANCE,
            "passed": abs(fixed_witness["norm"] - REGISTERED_FIXED_DRIFT)
            <= REPRODUCTION_TOLERANCE,
        },
        "independent_compensated_sums": {
            "value": maximum_independent_sum_difference,
            "threshold": INDEPENDENT_SUM_TOLERANCE,
            "passed": maximum_independent_sum_difference
            <= INDEPENDENT_SUM_TOLERANCE,
        },
        "unique_covariant_anchors": {
            "value": {
                "minimum_collision_gap": minimum_collision_anchor_gap,
                "minimum_filter_gap": minimum_filter_anchor_gap,
                "anchor_covariance_failure_count": anchor_covariance_failures,
            },
            "threshold": {
                "minimum_gap": ANCHOR_GAP_MINIMUM,
                "anchor_covariance_failure_count": 0,
            },
            "passed": (
                minimum_collision_anchor_gap >= ANCHOR_GAP_MINIMUM
                and minimum_filter_anchor_gap >= ANCHOR_GAP_MINIMUM
                and anchor_covariance_failures == 0
            ),
        },
        "c4_covariant_right_inverse": {
            "value": {
                "condition_number": right_inverse_condition,
                "right_inverse_residual": right_inverse_residual,
            },
            "threshold": {
                "condition_number": RIGHT_INVERSE_CONDITION_LIMIT,
                "right_inverse_residual": RIGHT_INVERSE_RESIDUAL_LIMIT,
            },
            "passed": (
                right_inverse_condition <= RIGHT_INVERSE_CONDITION_LIMIT
                and right_inverse_residual <= RIGHT_INVERSE_RESIDUAL_LIMIT
            ),
        },
        "strict_json_finite_values": {
            "value": _strict_json_serializable(serializable_probe),
            "threshold": True,
            "passed": _strict_json_serializable(serializable_probe),
        },
    }
    hypothesis_gates = {
        "covariant_conservation": {
            "value": covariant_witness["norm"],
            "threshold": CONSERVATION_LIMIT,
            "passed": covariant_witness["norm"] <= CONSERVATION_LIMIT,
        },
        "single_stage_correction": {
            "value": maximum_correction_norm,
            "threshold": CORRECTION_NORM_LIMIT,
            "passed": maximum_correction_norm <= CORRECTION_NORM_LIMIT,
        },
        "covariant_standard_state_difference": {
            "value": maximum_state_difference,
            "threshold": STATE_DIFFERENCE_LIMIT,
            "passed": maximum_state_difference <= STATE_DIFFERENCE_LIMIT,
        },
        "translation_equivariance": {
            "value": maximum_translation_error,
            "threshold": EQUIVARIANCE_LIMIT,
            "passed": maximum_translation_error <= EQUIVARIANCE_LIMIT,
        },
        "quarter_turn_equivariance": {
            "value": maximum_quarter_turn_error,
            "threshold": EQUIVARIANCE_LIMIT,
            "passed": maximum_quarter_turn_error <= EQUIVARIANCE_LIMIT,
        },
        "covariant_positivity": {
            "value": minimum_population,
            "threshold": 0.0,
            "passed": minimum_population > 0.0,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q006l covariant arithmetic validity failure"
        decision = (
            "A registered enumeration, reproduction, independent-sum, unique-"
            "anchor, right-inverse, or serialization validity gate failed."
        )
        next_change = "Repair the first Q006l validity failure without tuning it."
    elif hypothesis_passed:
        outcome = "accepted"
        classification = "covariant anchor correction controls registered drift"
        decision = (
            "The stagewise state-covariant correction passes conservation, "
            "translation, quarter-turn, state-difference, and positivity gates."
        )
        next_change = (
            "Preregister differentiability-domain and full-chart residual/shadow "
            "audits before treating this arithmetic control as a candidate map."
        )
    else:
        outcome = "rejected"
        classification = "covariant correction fails conservation or symmetry gate"
        decision = (
            "The valid stagewise correction fails at least one registered "
            "conservation, magnitude, symmetry, state-difference, or positivity gate."
        )
        next_change = "Stop continuation and isolate the first failed Q006l gate."
    return {
        "question": (
            "Can stagewise state-covariant anchor corrections preserve the "
            "registered moments and translation/C4 symmetry simultaneously?"
        ),
        "hypothesis": (
            "A unique q0 anchor and the minimum-norm conserved-moment right inverse "
            "control collision/filter roundoff without the fixed-site symmetry defect."
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
            "controls": ["standard", "fixed", "stagewise_covariant"],
            "corrected_stages": ["collision", "filter"],
            "streaming": "unchanged",
            "anchor_rule": "unique maximum raw-stage rest population q0",
            "correction_passes_per_stage": 1,
            "symmetry_generators": [
                "translation_y",
                "translation_x",
                "quarter_turn",
            ],
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
            "This control depends on global residuals and a unique argmax and is "
            "nonsmooth at anchor switches. It is not adopted as the production map "
            "and does not revise the sealed Q006i-Q006k outcomes."
        ),
    }
