"""Sealed Q007a order-three homological-family prequalification."""

from __future__ import annotations

import json
import math
from collections import Counter
from itertools import combinations_with_replacement
from typing import Any

import numpy as np

from .checkerboard_filter import filtered_fourier_symbol
from .full2d_chart import (
    MODE_ORDER,
    REDUCED_DIMENSION,
    REGISTERED_ETA,
    REGISTERED_OMEGA,
    REGISTERED_SIZE,
    WAVE_ORDER,
    _build_complex_modes,
    _negative_wave,
    _selected_output_basis,
)
from .nonresonance import (
    NUMERICAL_RANK_MULTIPLIER,
    add_wave_indices,
    canonical_wave_index,
    fixed_leaf_kinetic_restriction,
    wave_vector_from_index,
)

REGISTERED_PAIR_COUNT = 300
REGISTERED_TRIPLE_COUNT = 2600
REGISTERED_PAIR_SECTOR_COUNTS = {
    "zero_wave_kinetic": 36,
    "internal_selected": 108,
    "external": 156,
}
REGISTERED_PAIR_MINIMUM_SINGULAR_VALUE = 0.00015502435597333105
REGISTERED_PAIR_MAXIMUM_CONDITION_NUMBER = 14513.930547954875
PAIR_REPRODUCTION_RELATIVE_TOLERANCE = 1.0e-10
CONJUGACY_RELATIVE_TOLERANCE = 1.0e-10
NEAR_RESONANCE_RELATIVE_THRESHOLD = 1.0e-4
MAXIMUM_CONDITION_NUMBER = 1.0e9

WaveIndex = tuple[int, int]


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _relative_error(value: float, reference: float) -> float:
    return float(abs(value - reference) / max(abs(reference), np.finfo(float).eps))


def _permutation_multiplicity(indices: tuple[int, ...]) -> int:
    counts = Counter(indices)
    denominator = math.prod(math.factorial(count) for count in counts.values())
    return math.factorial(len(indices)) // denominator


def _sum_waves(
    indices: tuple[int, ...],
    modes: list[Any],
    size: int,
) -> WaveIndex:
    output = (0, 0)
    for index in indices:
        output = add_wave_indices(output, modes[index].wave_index, size)
    return output


def _homological_operator(
    indices: tuple[int, ...],
    modes: list[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
    omega: float,
    eta: float,
) -> tuple[np.ndarray, WaveIndex, str, float]:
    output_wave = _sum_waves(indices, modes, size)
    multiplier = complex(math.prod(modes[index].eigenvalue for index in indices))
    if output_wave == (0, 0):
        kinetic, unfiltered_block, invariance = fixed_leaf_kinetic_restriction(
            omega
        )
        operator = unfiltered_block - multiplier * np.eye(
            kinetic.shape[1],
            dtype=np.complex128,
        )
        output_kind = "zero_wave_kinetic"
    elif output_wave in WAVE_ORDER:
        output_vector = wave_vector_from_index(output_wave, size)
        output_matrix = filtered_fourier_symbol(*output_vector, omega, eta)
        selected_right, selected_left, _ = _selected_output_basis(
            output_wave,
            modes,
            lookup,
        )
        operator = np.block(
            [
                [
                    output_matrix
                    - multiplier * np.eye(9, dtype=np.complex128),
                    -selected_right,
                ],
                [selected_left, np.zeros((3, 3), dtype=np.complex128)],
            ]
        )
        output_kind = "internal_selected"
        invariance = 0.0
    else:
        output_vector = wave_vector_from_index(output_wave, size)
        output_matrix = filtered_fourier_symbol(*output_vector, omega, eta)
        operator = output_matrix - multiplier * np.eye(
            9,
            dtype=np.complex128,
        )
        output_kind = "external"
        invariance = 0.0
    return (
        np.asarray(operator, dtype=np.complex128),
        output_wave,
        output_kind,
        float(invariance),
    )


def _operator_record(
    record_index: int,
    indices: tuple[int, ...],
    modes: list[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
    omega: float,
    eta: float,
) -> dict[str, Any]:
    operator, output_wave, output_kind, invariance = _homological_operator(
        indices,
        modes,
        lookup,
        size,
        omega,
        eta,
    )
    multiplier = complex(math.prod(modes[index].eigenvalue for index in indices))
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
    relative_smallest = float(smallest / largest)
    condition_number = None if numerically_singular else float(largest / smallest)
    order = len(indices)
    prefix = {2: "p", 3: "t", 4: "q"}.get(order, f"o{order}_")
    return {
        "record_identifier": f"{prefix}{record_index:05d}",
        "order": order,
        "input_indices": list(indices),
        "input_modes": [modes[index].identifier for index in indices],
        "input_labels": [modes[index].label for index in indices],
        "input_wave_indices": [list(modes[index].wave_index) for index in indices],
        "input_eigenvalues": [
            _complex_record(modes[index].eigenvalue) for index in indices
        ],
        "multiplier_product": _complex_record(multiplier),
        "output_wave_index": list(output_wave),
        "output_kind": output_kind,
        "operator_dimension": int(operator.shape[1]),
        "operator_rank": rank,
        "singular_values": singular_values.tolist(),
        "numerical_rank_threshold": rank_threshold,
        "smallest_singular_value": smallest,
        "largest_singular_value": largest,
        "relative_smallest_singular_value": relative_smallest,
        "rank_margin": float(smallest / rank_threshold),
        "condition_number": condition_number,
        "numerically_singular": numerically_singular,
        "near_resonant": (
            not numerically_singular
            and relative_smallest < NEAR_RESONANCE_RELATIVE_THRESHOLD
        ),
        "permutation_multiplicity": _permutation_multiplicity(indices),
        "fixed_leaf_subspace_invariance_residual": invariance,
    }


def _enumerate_records(
    order: int,
    modes: list[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
    omega: float,
    eta: float,
) -> list[dict[str, Any]]:
    return [
        _operator_record(
            record_index,
            tuple(indices),
            modes,
            lookup,
            size,
            omega,
            eta,
        )
        for record_index, indices in enumerate(
            combinations_with_replacement(range(len(modes)), order)
        )
    ]


def _record_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    finite_conditions = [
        float(record["condition_number"])
        for record in records
        if record["condition_number"] is not None
    ]
    worst = max(
        (
            record
            for record in records
            if record["condition_number"] is not None
        ),
        key=lambda record: float(record["condition_number"]),
    )
    weakest = min(
        records,
        key=lambda record: float(record["smallest_singular_value"]),
    )
    sector_counts = {
        kind: sum(record["output_kind"] == kind for record in records)
        for kind in REGISTERED_PAIR_SECTOR_COUNTS
    }
    return {
        "record_count": len(records),
        "unique_input_index_count": len(
            {tuple(record["input_indices"]) for record in records}
        ),
        "duplicate_input_index_count": len(records)
        - len({tuple(record["input_indices"]) for record in records}),
        "sector_counts": sector_counts,
        "numerically_singular_block_count": sum(
            record["numerically_singular"] for record in records
        ),
        "near_resonant_block_count": sum(
            record["near_resonant"] for record in records
        ),
        "minimum_operator_singular_value": min(
            float(record["smallest_singular_value"]) for record in records
        ),
        "minimum_rank_margin": min(
            float(record["rank_margin"]) for record in records
        ),
        "maximum_operator_condition_number": max(finite_conditions),
        "weakest_singular_value_witness": {
            "record_identifier": weakest["record_identifier"],
            "input_modes": weakest["input_modes"],
            "output_wave_index": weakest["output_wave_index"],
            "output_kind": weakest["output_kind"],
            "smallest_singular_value": weakest["smallest_singular_value"],
            "condition_number": weakest["condition_number"],
        },
        "maximum_condition_witness": {
            "record_identifier": worst["record_identifier"],
            "input_modes": worst["input_modes"],
            "output_wave_index": worst["output_wave_index"],
            "output_kind": worst["output_kind"],
            "smallest_singular_value": worst["smallest_singular_value"],
            "condition_number": worst["condition_number"],
        },
    }


def _conjugate_indices(
    modes: list[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
) -> list[int]:
    conjugate_label = {
        "shear": "shear",
        "acoustic_positive": "acoustic_negative",
        "acoustic_negative": "acoustic_positive",
    }
    return [
        lookup[
            (
                _negative_wave(mode.wave_index, size),
                conjugate_label[mode.label],
            )
        ]
        for mode in modes
    ]


def _conjugacy_audit(
    records: list[dict[str, Any]],
    modes: list[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    size: int,
) -> dict[str, Any]:
    conjugate_indices = _conjugate_indices(modes, lookup, size)
    record_lookup = {
        tuple(record["input_indices"]): record for record in records
    }
    maximum_multiplier_error = 0.0
    maximum_singular_value_error = 0.0
    missing_count = 0
    output_wave_failure_count = 0
    output_kind_failure_count = 0
    maximum_witness: dict[str, Any] | None = None
    for record in records:
        input_indices = tuple(int(index) for index in record["input_indices"])
        conjugate_key = tuple(sorted(conjugate_indices[index] for index in input_indices))
        conjugate = record_lookup.get(conjugate_key)
        if conjugate is None:
            missing_count += 1
            continue
        multiplier = complex(
            record["multiplier_product"]["real"],
            record["multiplier_product"]["imag"],
        )
        conjugate_multiplier = complex(
            conjugate["multiplier_product"]["real"],
            conjugate["multiplier_product"]["imag"],
        )
        multiplier_error = float(
            abs(conjugate_multiplier - np.conjugate(multiplier))
            / max(abs(multiplier), np.finfo(float).eps)
        )
        singular_values = np.asarray(record["singular_values"], dtype=np.float64)
        conjugate_singular_values = np.asarray(
            conjugate["singular_values"],
            dtype=np.float64,
        )
        singular_error = float(
            np.linalg.norm(conjugate_singular_values - singular_values)
            / max(float(np.linalg.norm(singular_values)), np.finfo(float).eps)
        )
        expected_output = canonical_wave_index(
            tuple(-int(value) for value in record["output_wave_index"]),
            size,
        )
        output_wave_failed = tuple(conjugate["output_wave_index"]) != expected_output
        output_kind_failed = conjugate["output_kind"] != record["output_kind"]
        output_wave_failure_count += int(output_wave_failed)
        output_kind_failure_count += int(output_kind_failed)
        maximum_multiplier_error = max(
            maximum_multiplier_error,
            multiplier_error,
        )
        if singular_error > maximum_singular_value_error:
            maximum_singular_value_error = singular_error
            maximum_witness = {
                "record_identifier": record["record_identifier"],
                "conjugate_record_identifier": conjugate["record_identifier"],
                "input_indices": list(input_indices),
                "conjugate_input_indices": list(conjugate_key),
                "singular_value_relative_error": singular_error,
                "multiplier_relative_error": multiplier_error,
            }
    return {
        "record_count": len(records),
        "missing_conjugate_count": missing_count,
        "output_wave_failure_count": output_wave_failure_count,
        "output_kind_failure_count": output_kind_failure_count,
        "maximum_multiplier_relative_error": maximum_multiplier_error,
        "maximum_singular_value_relative_error": maximum_singular_value_error,
        "maximum_singular_value_error_witness": maximum_witness,
    }


def _wave_count_audit(
    records: list[dict[str, Any]],
    size: int,
) -> dict[str, Any]:
    counts = Counter(tuple(record["output_wave_index"]) for record in records)
    rotation_failure_count = 0
    conjugacy_failure_count = 0
    maximum_rotation_count_difference = 0
    maximum_conjugacy_count_difference = 0
    for wave, count in counts.items():
        rotated = canonical_wave_index((-wave[1], wave[0]), size)
        conjugate = canonical_wave_index((-wave[0], -wave[1]), size)
        rotation_difference = abs(count - counts.get(rotated, 0))
        conjugacy_difference = abs(count - counts.get(conjugate, 0))
        rotation_failure_count += int(rotation_difference != 0)
        conjugacy_failure_count += int(conjugacy_difference != 0)
        maximum_rotation_count_difference = max(
            maximum_rotation_count_difference,
            rotation_difference,
        )
        maximum_conjugacy_count_difference = max(
            maximum_conjugacy_count_difference,
            conjugacy_difference,
        )
    return {
        "output_wave_count": len(counts),
        "counts": [
            {"output_wave_index": list(wave), "count": count}
            for wave, count in sorted(counts.items())
        ],
        "rotation_failure_count": rotation_failure_count,
        "conjugacy_failure_count": conjugacy_failure_count,
        "maximum_rotation_count_difference": maximum_rotation_count_difference,
        "maximum_conjugacy_count_difference": maximum_conjugacy_count_difference,
    }


def _all_records_finite(records: list[dict[str, Any]]) -> bool:
    for record in records:
        finite_values = [
            *record["singular_values"],
            record["numerical_rank_threshold"],
            record["smallest_singular_value"],
            record["largest_singular_value"],
            record["relative_smallest_singular_value"],
            record["rank_margin"],
            record["fixed_leaf_subspace_invariance_residual"],
            record["multiplier_product"]["real"],
            record["multiplier_product"]["imag"],
        ]
        if not np.all(np.isfinite(finite_values)):
            return False
        condition = record["condition_number"]
        if record["numerically_singular"]:
            if condition is not None:
                return False
        elif condition is None or not np.isfinite(condition) or condition <= 0.0:
            return False
    return True


def _strict_json_serializable(value: Any) -> bool:
    try:
        json.dumps(value, allow_nan=False)
    except (TypeError, ValueError):
        return False
    return True


def run_cubic_prequalification_audit() -> dict[str, Any]:
    """Run the preregistered Q007a order-three operator audit."""

    size = REGISTERED_SIZE
    omega = REGISTERED_OMEGA
    eta = REGISTERED_ETA
    modes, lookup = _build_complex_modes(size, omega, eta)
    pair_records = _enumerate_records(
        2,
        modes,
        lookup,
        size,
        omega,
        eta,
    )
    triple_records = _enumerate_records(
        3,
        modes,
        lookup,
        size,
        omega,
        eta,
    )
    pair_summary = _record_summary(pair_records)
    triple_summary = _record_summary(triple_records)
    conjugacy = _conjugacy_audit(
        triple_records,
        modes,
        lookup,
        size,
    )
    wave_counts = _wave_count_audit(triple_records, size)
    pair_minimum_error = _relative_error(
        pair_summary["minimum_operator_singular_value"],
        REGISTERED_PAIR_MINIMUM_SINGULAR_VALUE,
    )
    pair_condition_error = _relative_error(
        pair_summary["maximum_operator_condition_number"],
        REGISTERED_PAIR_MAXIMUM_CONDITION_NUMBER,
    )
    serializable_probe = {
        "pair_records": pair_records,
        "triple_records": triple_records,
        "pair_summary": pair_summary,
        "triple_summary": triple_summary,
        "conjugacy_audit": conjugacy,
        "wave_count_audit": wave_counts,
    }
    finite_records = _all_records_finite(pair_records + triple_records)
    strict_json = _strict_json_serializable(serializable_probe)
    validity_gates = {
        "order_two_sector_reproduction": {
            "value": {
                "record_count": pair_summary["record_count"],
                "sector_counts": pair_summary["sector_counts"],
                "numerically_singular_block_count": pair_summary[
                    "numerically_singular_block_count"
                ],
            },
            "threshold": {
                "record_count": REGISTERED_PAIR_COUNT,
                "sector_counts": REGISTERED_PAIR_SECTOR_COUNTS,
                "numerically_singular_block_count": 0,
            },
            "passed": (
                pair_summary["record_count"] == REGISTERED_PAIR_COUNT
                and pair_summary["sector_counts"]
                == REGISTERED_PAIR_SECTOR_COUNTS
                and pair_summary["numerically_singular_block_count"] == 0
            ),
        },
        "order_two_spectral_reproduction": {
            "value": {
                "minimum_singular_value_relative_error": pair_minimum_error,
                "maximum_condition_relative_error": pair_condition_error,
            },
            "threshold": PAIR_REPRODUCTION_RELATIVE_TOLERANCE,
            "passed": (
                pair_minimum_error <= PAIR_REPRODUCTION_RELATIVE_TOLERANCE
                and pair_condition_error
                <= PAIR_REPRODUCTION_RELATIVE_TOLERANCE
            ),
        },
        "complete_order_three_enumeration": {
            "value": {
                "record_count": triple_summary["record_count"],
                "unique_input_index_count": triple_summary[
                    "unique_input_index_count"
                ],
                "duplicate_input_index_count": triple_summary[
                    "duplicate_input_index_count"
                ],
                "sector_counts": triple_summary["sector_counts"],
            },
            "threshold": {
                "record_count": REGISTERED_TRIPLE_COUNT,
                "unique_input_index_count": REGISTERED_TRIPLE_COUNT,
                "duplicate_input_index_count": 0,
                "all_sector_counts_positive": True,
            },
            "passed": (
                triple_summary["record_count"] == REGISTERED_TRIPLE_COUNT
                and triple_summary["unique_input_index_count"]
                == REGISTERED_TRIPLE_COUNT
                and triple_summary["duplicate_input_index_count"] == 0
                and all(
                    count > 0
                    for count in triple_summary["sector_counts"].values()
                )
            ),
        },
        "conjugate_operator_closure": {
            "value": conjugacy,
            "threshold": {
                "missing_conjugate_count": 0,
                "output_wave_failure_count": 0,
                "output_kind_failure_count": 0,
                "maximum_multiplier_relative_error": (
                    CONJUGACY_RELATIVE_TOLERANCE
                ),
                "maximum_singular_value_relative_error": (
                    CONJUGACY_RELATIVE_TOLERANCE
                ),
            },
            "passed": (
                conjugacy["missing_conjugate_count"] == 0
                and conjugacy["output_wave_failure_count"] == 0
                and conjugacy["output_kind_failure_count"] == 0
                and conjugacy["maximum_multiplier_relative_error"]
                <= CONJUGACY_RELATIVE_TOLERANCE
                and conjugacy["maximum_singular_value_relative_error"]
                <= CONJUGACY_RELATIVE_TOLERANCE
            ),
        },
        "c4_and_conjugate_wave_count_closure": {
            "value": {
                "rotation_failure_count": wave_counts[
                    "rotation_failure_count"
                ],
                "conjugacy_failure_count": wave_counts[
                    "conjugacy_failure_count"
                ],
                "maximum_rotation_count_difference": wave_counts[
                    "maximum_rotation_count_difference"
                ],
                "maximum_conjugacy_count_difference": wave_counts[
                    "maximum_conjugacy_count_difference"
                ],
            },
            "threshold": {
                "rotation_failure_count": 0,
                "conjugacy_failure_count": 0,
                "maximum_rotation_count_difference": 0,
                "maximum_conjugacy_count_difference": 0,
            },
            "passed": (
                wave_counts["rotation_failure_count"] == 0
                and wave_counts["conjugacy_failure_count"] == 0
                and wave_counts["maximum_rotation_count_difference"] == 0
                and wave_counts["maximum_conjugacy_count_difference"] == 0
            ),
        },
        "finite_and_strict_json": {
            "value": {
                "all_record_values_finite": finite_records,
                "strict_json_serializable": strict_json,
            },
            "threshold": {
                "all_record_values_finite": True,
                "strict_json_serializable": True,
            },
            "passed": finite_records and strict_json,
        },
    }
    hypothesis_gates = {
        "no_numerically_singular_order_three_block": {
            "value": triple_summary["numerically_singular_block_count"],
            "threshold": 0,
            "passed": triple_summary["numerically_singular_block_count"] == 0,
        },
        "practical_condition_ceiling": {
            "value": triple_summary["maximum_operator_condition_number"],
            "threshold": MAXIMUM_CONDITION_NUMBER,
            "passed": triple_summary["maximum_operator_condition_number"]
            <= MAXIMUM_CONDITION_NUMBER,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q007a cubic-prequalification validity failure"
        decision = (
            "An order-two reproduction, order-three enumeration, conjugacy, "
            "wave-count closure, finiteness, or serialization validity gate "
            "failed."
        )
        next_change = "Repair the first Q007a validity failure without tuning gates."
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "order-three homological family prequalified on registered grid"
        )
        decision = (
            "All 2,600 registered order-three blocks are nonsingular and stay "
            "below the preregistered finite-grid condition ceiling."
        )
        next_change = (
            "Preregister Q007b cubic forcing, coefficient, independent-"
            "derivative, residual-order, and shadowing gates."
        )
    else:
        outcome = "rejected"
        classification = "order-three homological obstruction on registered grid"
        decision = (
            "At least one valid order-three block is numerically singular or "
            "exceeds the preregistered condition ceiling."
        )
        next_change = (
            "Stop cubic coefficient construction and freeze the first singular "
            "or over-conditioned witness."
        )
    return {
        "question": (
            "Do all order-three homological blocks for the Q006i 24-coordinate "
            "cluster form a uniquely solvable finite-grid family?"
        ),
        "hypothesis": (
            "All 2,600 unordered cubic input triples yield nonsingular blocks "
            "with condition number at most 1e9."
        ),
        "registered_setup": {
            "grid": [size, size],
            "omega": omega,
            "eta": eta,
            "complex_mode_count": len(modes),
            "real_reduced_dimension": REDUCED_DIMENSION,
            "mode_order": list(MODE_ORDER),
            "selected_waves": [list(wave) for wave in WAVE_ORDER],
            "pair_count": REGISTERED_PAIR_COUNT,
            "triple_count": REGISTERED_TRIPLE_COUNT,
            "rank_threshold": (
                "100 * eps * max(operator_shape) * largest_singular_value"
            ),
            "near_resonance_relative_threshold": (
                NEAR_RESONANCE_RELATIVE_THRESHOLD
            ),
            "maximum_condition_number": MAXIMUM_CONDITION_NUMBER,
            "coefficient_or_forcing_solve": "not performed",
        },
        "pair_control_records": pair_records,
        "triple_records": triple_records,
        "pair_control_summary": pair_summary,
        "triple_summary": triple_summary,
        "conjugacy_audit": conjugacy,
        "wave_count_audit": wave_counts,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if study_valid else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "next_change": next_change,
        "claim_boundary": (
            "This is an operator-only finite-grid prequalification. It does not "
            "construct or validate cubic forcing or coefficients, does not show "
            "fourth-order invariance residuals or improved shadowing, and is not "
            "an SSM existence or grid-uniform nonresonance theorem."
        ),
    }
