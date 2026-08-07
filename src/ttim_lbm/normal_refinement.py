"""Registered Q006n near-Nyquist refinement obstruction campaign."""

from __future__ import annotations

from typing import Any

import numpy as np

from .d2q9 import fourier_symbol
from .mode_closure import (
    FORCING_SENSITIVITY_THRESHOLD,
    LOCAL_SYLVESTER_SEPARATION_THRESHOLD,
    MATERIAL_NEAR_CONDITION_CEILING,
    NORMAL_DOMINANCE_GAP_THRESHOLD,
    PRACTICAL_CONDITION_CEILING,
    PROJECTOR_NORM_CEILING,
    STRUCTURAL_RESIDUAL_TOLERANCE,
    _audit_round,
    _initial_blocks,
    _normal_dominance_screen,
)

REGISTERED_GRID_SIZES = (9, 17, 33, 65, 129)
REGISTERED_OMEGAS = (1.0, 1.2, 1.5, 1.8)
REFINEMENT_GRID_SIZES = (17, 33, 65, 129)


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _compact_pair_record(record: dict[str, Any]) -> dict[str, Any]:
    singular_values = record["singular_values"]
    return {
        "pair_identifier": record["pair_identifier"],
        "left_block": record["left_block"],
        "right_block": record["right_block"],
        "left_wave_index": record["left_wave_index"],
        "right_wave_index": record["right_wave_index"],
        "output_wave_index": record["output_wave_index"],
        "product_dimension": record["product_dimension"],
        "external_dimension": record["external_dimension"],
        "status": record["status"],
        "smallest_singular_value": (
            singular_values[-1] if singular_values else None
        ),
        "largest_singular_value": (
            singular_values[0] if singular_values else None
        ),
        "relative_smallest_singular_value": record.get(
            "relative_smallest_singular_value"
        ),
        "condition_number": record["condition_number"],
        "numerical_rank_threshold": record.get("numerical_rank_threshold"),
        "numerical_singular_count": record["numerical_singular_count"],
        "near_singular_count": record["near_singular_count"],
        "near_forcing_sensitivity": record["near_forcing_sensitivity"],
        "null_forcing_ratio": record["null_forcing_ratio"],
        "solve_relative_residual": record["solve_relative_residual"],
        "fixed_leaf_forcing_residual": record["fixed_leaf_forcing_residual"],
        "product_invariance_leakage": record["product_invariance_leakage"],
        "maximum_external_cluster_structural_residual": record[
            "maximum_external_cluster_structural_residual"
        ],
    }


def _is_axial_near_nyquist(wave_index: list[int], size: int) -> bool:
    half = size // 2
    return sorted(abs(int(value)) for value in wave_index) == [0, half]


def audit_fixed_family_condition(size: int, omega: float) -> dict[str, Any]:
    """Audit one registered fixed-16-dimensional condition without mode addition."""

    if size not in REGISTERED_GRID_SIZES or float(omega) not in REGISTERED_OMEGAS:
        raise ValueError("condition is outside the sealed Q006n campaign")
    size = int(size)
    omega = float(omega)
    blocks = _initial_blocks(size, omega)
    round_record, candidates = _audit_round(blocks, 0, size, omega)
    coefficient_gates = {
        "complete_pair_enumeration": {
            "value": round_record["enumerated_pair_count"],
            "threshold": 136,
            "passed": round_record["pair_enumeration_complete"]
            and round_record["enumerated_pair_count"] == 136,
        },
        "structural_residual": {
            "value": round_record["maximum_structural_residual"],
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": round_record["maximum_structural_residual"]
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
        "homological_solve_residual": {
            "value": round_record["maximum_solve_relative_residual"],
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": round_record["maximum_solve_relative_residual"]
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
        "no_numerically_singular_external_block": {
            "value": round_record[
                "numerically_singular_external_block_count"
            ],
            "threshold": 0,
            "passed": round_record[
                "numerically_singular_external_block_count"
            ]
            == 0,
        },
        "materially_forced_near_condition": {
            "value": round_record[
                "maximum_materially_forced_near_condition_number"
            ],
            "threshold": MATERIAL_NEAR_CONDITION_CEILING,
            "passed": round_record[
                "maximum_materially_forced_near_condition_number"
            ]
            <= MATERIAL_NEAR_CONDITION_CEILING,
        },
        "remaining_external_condition": {
            "value": round_record["maximum_condition_number"],
            "threshold": PRACTICAL_CONDITION_CEILING,
            "passed": round_record["maximum_condition_number"]
            <= PRACTICAL_CONDITION_CEILING,
        },
    }
    coefficient_passed = all(gate["passed"] for gate in coefficient_gates.values())
    normal = _normal_dominance_screen(
        blocks,
        size,
        omega,
        coefficient_passed,
    )
    blockwise_passed = (
        normal["gates"]["local_sylvester_separation"]["passed"]
        and normal["gates"]["selected_riesz_projector_norm"]["passed"]
    )
    pair_table = [
        _compact_pair_record(record) for record in round_record["pair_table"]
    ]
    worst_pair_identifier = round_record["worst_condition_pair"]
    worst_pair = next(
        (
            record
            for record in pair_table
            if record["pair_identifier"] == worst_pair_identifier
        ),
        None,
    )
    gap = float(normal["normal_dominance_gap"])
    return {
        "grid_size": size,
        "omega": omega,
        "selected_real_dimension": sum(block.dimension for block in blocks),
        "mode_addition_enabled": False,
        "requested_response_cluster_count": len(candidates),
        "coefficient_gates": coefficient_gates,
        "coefficient_passed": coefficient_passed,
        "blockwise_projector_passed": blockwise_passed,
        "normal_dominance_passed": bool(
            coefficient_passed
            and blockwise_passed
            and gap >= NORMAL_DOMINANCE_GAP_THRESHOLD
        ),
        "normal_dominance_gap": gap,
        "scaled_normal_dominance_gap_n_squared": float(size * size * gap),
        "minimum_selected_modulus": normal["minimum_selected_modulus"],
        "minimum_selected_wave_index": normal["minimum_selected_wave_index"],
        "minimum_selected_eigenvalue": normal["minimum_selected_eigenvalue"],
        "maximum_excluded_modulus": normal["maximum_excluded_modulus"],
        "maximum_excluded_wave_index": normal["maximum_excluded_wave_index"],
        "maximum_excluded_eigenvalue": normal["maximum_excluded_eigenvalue"],
        "worst_external_is_axial_near_nyquist": _is_axial_near_nyquist(
            normal["maximum_excluded_wave_index"], size
        ),
        "minimum_local_sylvester_separation": normal[
            "minimum_local_sylvester_separation"
        ],
        "minimum_local_separation_wave_index": normal[
            "minimum_local_separation_wave_index"
        ],
        "maximum_selected_riesz_projector_norm": normal[
            "maximum_selected_riesz_projector_norm"
        ],
        "maximum_projector_wave_index": normal[
            "maximum_projector_wave_index"
        ],
        "maximum_condition_number": round_record["maximum_condition_number"],
        "condition_quantiles": round_record["condition_quantiles"],
        "worst_condition_pair": worst_pair,
        "numerically_singular_external_block_count": round_record[
            "numerically_singular_external_block_count"
        ],
        "near_singular_external_block_count": round_record[
            "near_singular_external_block_count"
        ],
        "maximum_materially_forced_near_condition_number": round_record[
            "maximum_materially_forced_near_condition_number"
        ],
        "maximum_structural_residual": round_record[
            "maximum_structural_residual"
        ],
        "maximum_solve_relative_residual": round_record[
            "maximum_solve_relative_residual"
        ],
        "maximum_fixed_leaf_residual": round_record[
            "maximum_fixed_leaf_residual"
        ],
        "pair_count": round_record["enumerated_pair_count"],
        "pair_table": pair_table,
    }


def _nyquist_anchor(omega: float) -> dict[str, Any]:
    directions = {}
    for label, wave_vector in {"pi_0": (np.pi, 0.0), "0_pi": (0.0, np.pi)}.items():
        eigenvalues = np.asarray(
            np.linalg.eigvals(fourier_symbol(*wave_vector, omega)),
            dtype=np.complex128,
        )
        distances = np.abs(eigenvalues + 1.0)
        matched = int(np.argmin(distances))
        directions[label] = {
            "minimum_distance_to_minus_one": float(distances[matched]),
            "closest_eigenvalue": _complex_record(complex(eigenvalues[matched])),
            "minus_one_count_at_tolerance": int(np.count_nonzero(distances <= 1.0e-12)),
        }
    return {"omega": float(omega), "directions": directions}


def run_normal_gap_refinement_audit() -> dict[str, Any]:
    """Run the sealed 20-condition Q006n refinement campaign."""

    conditions = [
        audit_fixed_family_condition(size, omega)
        for size in REGISTERED_GRID_SIZES
        for omega in REGISTERED_OMEGAS
    ]
    anchors = [_nyquist_anchor(omega) for omega in REGISTERED_OMEGAS]
    refinement = [
        record for record in conditions if record["grid_size"] in REFINEMENT_GRID_SIZES
    ]
    coefficient_and_blockwise = all(
        record["coefficient_passed"] and record["blockwise_projector_passed"]
        for record in refinement
    )
    all_negative = all(
        record["normal_dominance_gap"] < -NORMAL_DOMINANCE_GAP_THRESHOLD
        for record in refinement
    )
    all_near_nyquist = all(
        record["worst_external_is_axial_near_nyquist"] for record in refinement
    )
    anchors_pass = all(
        direction["minimum_distance_to_minus_one"] <= 1.0e-12
        and direction["minus_one_count_at_tolerance"] >= 1
        for anchor in anchors
        for direction in anchor["directions"].values()
    )
    obstruction_supported = (
        coefficient_and_blockwise
        and all_negative
        and all_near_nyquist
        and anchors_pass
    )
    viable_omegas = []
    for omega in REGISTERED_OMEGAS:
        records = [
            record
            for record in refinement
            if record["omega"] == omega
        ]
        if all(record["normal_dominance_passed"] for record in records):
            viable_omegas.append(
                {
                    "omega": omega,
                    "minimum_refinement_gap": min(
                        record["normal_dominance_gap"] for record in records
                    ),
                }
            )
    viable_omegas.sort(
        key=lambda record: (-record["minimum_refinement_gap"], record["omega"])
    )
    coarse_passes = [
        {"omega": record["omega"], "normal_dominance_gap": record["normal_dominance_gap"]}
        for record in conditions
        if record["grid_size"] == 9 and record["normal_dominance_passed"]
    ]
    validity_gates = {
        "registered_condition_count": {
            "value": len(conditions),
            "threshold": 20,
            "passed": len(conditions) == 20,
        },
        "complete_pair_enumeration": {
            "value": min(record["pair_count"] for record in conditions),
            "threshold": 136,
            "passed": all(record["pair_count"] == 136 for record in conditions),
        },
        "structural_residual": {
            "value": max(record["maximum_structural_residual"] for record in conditions),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": max(
                record["maximum_structural_residual"] for record in conditions
            )
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
        "homological_solve_residual": {
            "value": max(record["maximum_solve_relative_residual"] for record in conditions),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": max(
                record["maximum_solve_relative_residual"] for record in conditions
            )
            <= STRUCTURAL_RESIDUAL_TOLERANCE,
        },
    }
    study_validity = all(gate["passed"] for gate in validity_gates.values())
    if obstruction_supported:
        outcome = "accepted"
        decision = (
            "The registered refinement ladder supports a near-Nyquist obstruction "
            "for the standard periodic-BGK 16-coordinate family."
        )
        next_change = (
            "Preregister a checkerboard-damping model modification before any "
            "full-2D Q006 chart construction."
        )
    elif viable_omegas:
        outcome = "rejected"
        decision = (
            "The obstruction hypothesis is rejected; a registered omega remains "
            "normally dominant throughout the refinement ladder."
        )
        next_change = (
            "Use the deterministically selected viable omega in a new finite-grid "
            "Q006 chart preregistration."
        )
    else:
        outcome = "inconclusive"
        decision = (
            "The campaign found a mixed coefficient/normal-gap obstruction that "
            "does not satisfy either preregistered clean classification."
        )
        next_change = (
            "Isolate the failing coefficient or non-near-Nyquist witness before "
            "changing the collision model."
        )
    return {
        "question": (
            "Does the Q006r normal-gap failure persist for the fixed 16-coordinate "
            "family on the registered odd-grid refinement ladder?"
        ),
        "hypothesis": (
            "All coefficient-valid N>=17 conditions fail normal dominance because "
            "an axial near-Nyquist mode decays more slowly than the selected set."
        ),
        "registered_scope": {
            "grid_sizes": list(REGISTERED_GRID_SIZES),
            "refinement_grid_sizes": list(REFINEMENT_GRID_SIZES),
            "omegas": list(REGISTERED_OMEGAS),
            "condition_count": 20,
            "selected_real_dimension": 16,
            "pair_count_per_condition": 136,
            "mode_addition_enabled": False,
            "normal_gap_threshold": NORMAL_DOMINANCE_GAP_THRESHOLD,
            "local_sylvester_separation_threshold": (
                LOCAL_SYLVESTER_SEPARATION_THRESHOLD
            ),
            "projector_norm_ceiling": PROJECTOR_NORM_CEILING,
            "forcing_sensitivity_threshold": FORCING_SENSITIVITY_THRESHOLD,
        },
        "conditions": conditions,
        "nyquist_anchors": anchors,
        "summary": {
            "refinement_condition_count": len(refinement),
            "refinement_coefficient_and_blockwise_pass_count": sum(
                record["coefficient_passed"] and record["blockwise_projector_passed"]
                for record in refinement
            ),
            "refinement_negative_gap_count": sum(
                record["normal_dominance_gap"] < -NORMAL_DOMINANCE_GAP_THRESHOLD
                for record in refinement
            ),
            "refinement_axial_near_nyquist_worst_count": sum(
                record["worst_external_is_axial_near_nyquist"]
                for record in refinement
            ),
            "coarse_grid_passes": coarse_passes,
            "nyquist_anchor_passed": anchors_pass,
            "registered_obstruction_supported": obstruction_supported,
            "viable_omegas": viable_omegas,
            "selected_viable_omega": (
                viable_omegas[0]["omega"] if viable_omegas else None
            ),
            "maximum_condition_number": max(
                record["maximum_condition_number"] for record in conditions
            ),
            "maximum_structural_residual": max(
                record["maximum_structural_residual"] for record in conditions
            ),
            "maximum_solve_relative_residual": max(
                record["maximum_solve_relative_residual"] for record in conditions
            ),
        },
        "validity_gates": validity_gates,
        "study_validity": "passed" if study_validity else "failed",
        "hypothesis_outcome": outcome,
        "decision": decision,
        "limitations": [
            (
                "The result covers five registered odd grids and four BGK "
                "relaxation values; it is not a theorem for every odd grid."
            ),
            (
                "The exact even-grid Nyquist anchor explains the limiting "
                "obstruction but does not by itself prove the odd-grid rate."
            ),
            (
                "No normal-gap mode is promoted and no collision/filter parameter "
                "is tuned inside this sealed campaign."
            ),
        ],
        "next_change": next_change,
    }
