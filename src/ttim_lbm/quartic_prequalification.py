"""Sealed Q007c order-four homological-family prequalification."""

from __future__ import annotations

from typing import Any

from .cubic_prequalification import (
    CONJUGACY_RELATIVE_TOLERANCE,
    MAXIMUM_CONDITION_NUMBER,
    NEAR_RESONANCE_RELATIVE_THRESHOLD,
    REGISTERED_PAIR_COUNT,
    REGISTERED_PAIR_MAXIMUM_CONDITION_NUMBER,
    REGISTERED_PAIR_MINIMUM_SINGULAR_VALUE,
    REGISTERED_PAIR_SECTOR_COUNTS,
    REGISTERED_TRIPLE_COUNT,
    _all_records_finite,
    _conjugacy_audit,
    _enumerate_records,
    _record_summary,
    _relative_error,
    _strict_json_serializable,
    _wave_count_audit,
)
from .full2d_chart import (
    MODE_ORDER,
    REDUCED_DIMENSION,
    REGISTERED_ETA,
    REGISTERED_OMEGA,
    REGISTERED_SIZE,
    WAVE_ORDER,
    _build_complex_modes,
)

REGISTERED_QUARTIC_COUNT = 17550
REGISTERED_QUARTIC_MULTIPLICITY_SUM = 24**4
REGISTERED_QUARTIC_MULTIPLICITIES = {1, 4, 6, 12, 24}
REGISTERED_TRIPLE_SECTOR_COUNTS = {
    "zero_wave_kinetic": 108,
    "internal_selected": 1044,
    "external": 1448,
}
REGISTERED_TRIPLE_MINIMUM_SINGULAR_VALUE = 0.00020787972673242753
REGISTERED_TRIPLE_MAXIMUM_CONDITION_NUMBER = 10821.814847751179
REGISTERED_TRIPLE_NEAR_RESONANT_COUNT = 24
CONTROL_REPRODUCTION_RELATIVE_TOLERANCE = 1.0e-10


def run_quartic_prequalification_audit() -> dict[str, Any]:
    """Run the preregistered Q007c order-four operator audit."""

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
    quartic_records = _enumerate_records(
        4,
        modes,
        lookup,
        size,
        omega,
        eta,
    )
    pair_summary = _record_summary(pair_records)
    triple_summary = _record_summary(triple_records)
    quartic_summary = _record_summary(quartic_records)
    conjugacy = _conjugacy_audit(
        quartic_records,
        modes,
        lookup,
        size,
    )
    wave_counts = _wave_count_audit(quartic_records, size)

    pair_spectral_errors = {
        "minimum_singular_value_relative_error": _relative_error(
            pair_summary["minimum_operator_singular_value"],
            REGISTERED_PAIR_MINIMUM_SINGULAR_VALUE,
        ),
        "maximum_condition_relative_error": _relative_error(
            pair_summary["maximum_operator_condition_number"],
            REGISTERED_PAIR_MAXIMUM_CONDITION_NUMBER,
        ),
    }
    triple_spectral_errors = {
        "minimum_singular_value_relative_error": _relative_error(
            triple_summary["minimum_operator_singular_value"],
            REGISTERED_TRIPLE_MINIMUM_SINGULAR_VALUE,
        ),
        "maximum_condition_relative_error": _relative_error(
            triple_summary["maximum_operator_condition_number"],
            REGISTERED_TRIPLE_MAXIMUM_CONDITION_NUMBER,
        ),
    }
    multiplicity_sum = sum(
        record["permutation_multiplicity"] for record in quartic_records
    )
    multiplicity_values = {
        record["permutation_multiplicity"] for record in quartic_records
    }
    maximum_fixed_leaf_invariance_residual = max(
        record["fixed_leaf_subspace_invariance_residual"]
        for record in quartic_records
    )
    serializable_probe = {
        "pair_records": pair_records,
        "triple_records": triple_records,
        "quartic_records": quartic_records,
        "pair_summary": pair_summary,
        "triple_summary": triple_summary,
        "quartic_summary": quartic_summary,
        "conjugacy_audit": conjugacy,
        "wave_count_audit": wave_counts,
    }
    finite_records = _all_records_finite(
        pair_records + triple_records + quartic_records
    )
    strict_json = _strict_json_serializable(serializable_probe)

    validity_gates = {
        "order_two_control_reproduction": {
            "value": {
                "record_count": pair_summary["record_count"],
                "sector_counts": pair_summary["sector_counts"],
                "numerically_singular_block_count": pair_summary[
                    "numerically_singular_block_count"
                ],
                **pair_spectral_errors,
            },
            "threshold": {
                "record_count": REGISTERED_PAIR_COUNT,
                "sector_counts": REGISTERED_PAIR_SECTOR_COUNTS,
                "numerically_singular_block_count": 0,
                "spectral_relative_error": (
                    CONTROL_REPRODUCTION_RELATIVE_TOLERANCE
                ),
            },
            "passed": (
                pair_summary["record_count"] == REGISTERED_PAIR_COUNT
                and pair_summary["sector_counts"]
                == REGISTERED_PAIR_SECTOR_COUNTS
                and pair_summary["numerically_singular_block_count"] == 0
                and all(
                    error <= CONTROL_REPRODUCTION_RELATIVE_TOLERANCE
                    for error in pair_spectral_errors.values()
                )
            ),
        },
        "order_three_control_reproduction": {
            "value": {
                "record_count": triple_summary["record_count"],
                "sector_counts": triple_summary["sector_counts"],
                "numerically_singular_block_count": triple_summary[
                    "numerically_singular_block_count"
                ],
                "near_resonant_block_count": triple_summary[
                    "near_resonant_block_count"
                ],
                **triple_spectral_errors,
            },
            "threshold": {
                "record_count": REGISTERED_TRIPLE_COUNT,
                "sector_counts": REGISTERED_TRIPLE_SECTOR_COUNTS,
                "numerically_singular_block_count": 0,
                "near_resonant_block_count": (
                    REGISTERED_TRIPLE_NEAR_RESONANT_COUNT
                ),
                "spectral_relative_error": (
                    CONTROL_REPRODUCTION_RELATIVE_TOLERANCE
                ),
            },
            "passed": (
                triple_summary["record_count"] == REGISTERED_TRIPLE_COUNT
                and triple_summary["sector_counts"]
                == REGISTERED_TRIPLE_SECTOR_COUNTS
                and triple_summary["numerically_singular_block_count"] == 0
                and triple_summary["near_resonant_block_count"]
                == REGISTERED_TRIPLE_NEAR_RESONANT_COUNT
                and all(
                    error <= CONTROL_REPRODUCTION_RELATIVE_TOLERANCE
                    for error in triple_spectral_errors.values()
                )
            ),
        },
        "complete_order_four_enumeration": {
            "value": {
                "record_count": quartic_summary["record_count"],
                "unique_input_index_count": quartic_summary[
                    "unique_input_index_count"
                ],
                "duplicate_input_index_count": quartic_summary[
                    "duplicate_input_index_count"
                ],
                "sector_counts": quartic_summary["sector_counts"],
                "multiplicity_sum": multiplicity_sum,
                "multiplicity_values": sorted(multiplicity_values),
            },
            "threshold": {
                "record_count": REGISTERED_QUARTIC_COUNT,
                "unique_input_index_count": REGISTERED_QUARTIC_COUNT,
                "duplicate_input_index_count": 0,
                "all_sector_counts_positive": True,
                "multiplicity_sum": REGISTERED_QUARTIC_MULTIPLICITY_SUM,
                "multiplicity_values": sorted(
                    REGISTERED_QUARTIC_MULTIPLICITIES
                ),
            },
            "passed": (
                quartic_summary["record_count"] == REGISTERED_QUARTIC_COUNT
                and quartic_summary["unique_input_index_count"]
                == REGISTERED_QUARTIC_COUNT
                and quartic_summary["duplicate_input_index_count"] == 0
                and all(
                    count > 0
                    for count in quartic_summary["sector_counts"].values()
                )
                and multiplicity_sum == REGISTERED_QUARTIC_MULTIPLICITY_SUM
                and multiplicity_values == REGISTERED_QUARTIC_MULTIPLICITIES
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
        "no_numerically_singular_order_four_block": {
            "value": quartic_summary["numerically_singular_block_count"],
            "threshold": 0,
            "passed": quartic_summary["numerically_singular_block_count"] == 0,
        },
        "practical_condition_ceiling": {
            "value": quartic_summary["maximum_operator_condition_number"],
            "threshold": MAXIMUM_CONDITION_NUMBER,
            "passed": quartic_summary["maximum_operator_condition_number"]
            <= MAXIMUM_CONDITION_NUMBER,
        },
    }
    study_valid = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not study_valid:
        outcome = "inconclusive"
        classification = "Q007c quartic-prequalification validity failure"
        decision = (
            "An order-two/three control, order-four enumeration, conjugacy, "
            "wave-count, finiteness, or serialization validity gate failed."
        )
        next_change = (
            "Repair the first Q007c validity failure without tuning the sealed "
            "order-four condition gates."
        )
    elif hypothesis_passed:
        outcome = "accepted"
        classification = (
            "order-four homological family prequalified on registered grid"
        )
        decision = (
            "All 17,550 registered order-four blocks are nonsingular and stay "
            "below the preregistered finite-grid condition ceiling."
        )
        next_change = (
            "Preregister Q007c1 quartic forcing, coefficient, derivative, "
            "residual-order, radius, and shadowing gates."
        )
    else:
        outcome = "rejected"
        classification = "order-four homological obstruction on registered grid"
        decision = (
            "At least one valid order-four block is numerically singular or "
            "exceeds the preregistered condition ceiling."
        )
        next_change = (
            "Stop quartic coefficient construction and freeze the first singular "
            "or over-conditioned witness."
        )
    return {
        "question": (
            "Do all order-four homological blocks for the Q006i 24-coordinate "
            "cluster form a uniquely solvable finite-grid family?"
        ),
        "hypothesis": (
            "All 17,550 unordered quartic input tuples yield nonsingular blocks "
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
            "pair_control_count": REGISTERED_PAIR_COUNT,
            "triple_control_count": REGISTERED_TRIPLE_COUNT,
            "quartic_tuple_count": REGISTERED_QUARTIC_COUNT,
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
        "triple_control_records": triple_records,
        "quartic_records": quartic_records,
        "pair_control_summary": pair_summary,
        "triple_control_summary": triple_summary,
        "quartic_summary": {
            **quartic_summary,
            "permutation_multiplicity_sum": multiplicity_sum,
            "permutation_multiplicity_values": sorted(multiplicity_values),
            "maximum_fixed_leaf_subspace_invariance_residual": (
                maximum_fixed_leaf_invariance_residual
            ),
        },
        "control_spectral_errors": {
            "order_two": pair_spectral_errors,
            "order_three": triple_spectral_errors,
        },
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
            "construct or validate quartic forcing or coefficients, does not show "
            "fifth-order invariance residuals or radius/shadowing improvement, and "
            "is not an invariant-manifold existence or grid-uniform theorem."
        ),
    }
