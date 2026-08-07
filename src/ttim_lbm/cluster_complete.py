"""Sealed Q006h first-shell cluster-complete filtered-family audit."""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from .checkerboard_filter import (
    EXTERNAL_CONDITION_CEILING,
    GLOBAL_L2_RESPONSE_RATIO_CEILING,
    LOW_WAVE_PHASE_TOLERANCE,
    LOW_WAVE_RELATIVE_MODULUS_TOLERANCE,
    LOW_WAVE_SUBSPACE_ANGLE_TOLERANCE,
    _audit_condition,
    _base_spectral_grid,
    _filter_algebra_audit,
)
from .coefficient_scaling import (
    FIT_GRID_SIZES,
    FIT_WINDOWS,
    TARGET_CLASSES,
    TARGET_PAIR_COUNT,
)
from .mode_closure import (
    LOCAL_SYLVESTER_SEPARATION_THRESHOLD,
    NORMAL_DOMINANCE_GAP_THRESHOLD,
    PROJECTOR_NORM_CEILING,
    STRUCTURAL_RESIDUAL_TOLERANCE,
    SpectralBlock,
    _initial_blocks,
    _make_block,
)
from .nonresonance import simple_hydrodynamic_modes, wave_vector_from_index

REGISTERED_ETAS = (0.0, 0.01, 0.02, 0.03, 0.05)
REGISTERED_OMEGAS = (1.0, 1.2, 1.5, 1.8)
REGISTERED_GRID_SIZES = (17, 33, 65, 129, 257)
REGISTERED_CONDITION_COUNT = 100
SELECTED_REAL_DIMENSION = 24
PAIR_COUNT = 300
DIAGONAL_ORBIT = ((1, 1), (-1, 1), (-1, -1), (1, -1))
DIAGONAL_ACOUSTIC_SELF = "diagonal_acoustic_self_second_harmonic"


def build_first_shell_cluster_blocks(
    size: int,
    omega: float,
) -> list[SpectralBlock]:
    """Build the registered 24-mode first-shell hydrodynamic family."""

    blocks = _initial_blocks(size, omega)
    counter = len(blocks)
    for wave_index in DIAGONAL_ORBIT:
        modes = simple_hydrodynamic_modes(
            *wave_vector_from_index(wave_index, size),
            omega,
        )
        for label in ("acoustic_positive", "acoustic_negative"):
            blocks.append(
                _make_block(
                    identifier=f"i{counter:03d}",
                    wave_index=wave_index,
                    raw_basis=modes[label].right_eigenvector[:, None],
                    origin=(
                        "cluster-complete diagonal first-shell hydrodynamic mode"
                    ),
                    label=label,
                    size=size,
                    omega=omega,
                )
            )
            counter += 1
    if len(blocks) != SELECTED_REAL_DIMENSION or sum(
        block.dimension for block in blocks
    ) != SELECTED_REAL_DIMENSION:
        raise RuntimeError("Q006h family must contain 24 one-dimensional blocks")
    wave_labels = {
        wave_index: {
            block.label for block in blocks if block.wave_index == wave_index
        }
        for wave_index in {
            block.wave_index for block in blocks
        }
    }
    expected_labels = {"shear", "acoustic_positive", "acoustic_negative"}
    if len(wave_labels) != 8 or any(
        labels != expected_labels for labels in wave_labels.values()
    ):
        raise RuntimeError("Q006h family is not hydrodynamically cluster-complete")
    return blocks


def _material_witness_class(record: dict[str, Any]) -> str | None:
    target_class = record["target_class"]
    if target_class is not None:
        return str(target_class)
    left_wave = tuple(int(value) for value in record["left_wave_index"])
    right_wave = tuple(int(value) for value in record["right_wave_index"])
    output_wave = tuple(int(value) for value in record["output_wave_index"])
    if (
        record["left_block"] == record["right_block"]
        and record["left_label"]
        in {"acoustic_positive", "acoustic_negative"}
        and record["right_label"] == record["left_label"]
        and left_wave == right_wave
        and sorted(abs(value) for value in left_wave) == [1, 1]
        and output_wave == tuple(2 * value for value in left_wave)
    ):
        return DIAGONAL_ACOUSTIC_SELF
    return None


def _witness_class_counts(
    conditions: list[dict[str, Any]],
) -> dict[str, int]:
    counts = Counter(
        witness["witness_class"] or "unclassified"
        for condition in conditions
        for witness in condition["materially_forced_near_witnesses"]
    )
    return dict(sorted(counts.items()))


def _condition_diagnostics(condition: dict[str, Any]) -> dict[str, Any]:
    pair_table = condition["pair_table"]
    pair_by_identifier = {
        record["pair_identifier"]: record for record in pair_table
    }
    material_witnesses = []
    for witness in condition["materially_forced_near_witnesses"]:
        pair = pair_by_identifier[witness["pair_identifier"]]
        material_witnesses.append(
            {
                **witness,
                "witness_class": _material_witness_class(pair),
                "left_label": pair["left_label"],
                "right_label": pair["right_label"],
                "left_wave_index": pair["left_wave_index"],
                "right_wave_index": pair["right_wave_index"],
            }
        )
    conditioned = [
        record for record in pair_table if record["condition_number"] is not None
    ]
    condition_values = np.asarray(
        [record["condition_number"] for record in conditioned],
        dtype=float,
    )
    worst = max(conditioned, key=lambda record: record["condition_number"])
    status_counts = {
        status: sum(record["status"] == status for record in pair_table)
        for status in (
            "internal_output_only",
            "nonsingular",
            "near_singular",
            "numerically_singular",
        )
    }
    classification_complete = all(
        (
            record["external_dimension"] == 0
            and record["status"] == "internal_output_only"
        )
        or (
            record["external_dimension"] > 0
            and record["status"]
            in {"nonsingular", "near_singular", "numerically_singular"}
            and record["smallest_singular_value"] is not None
            and np.isfinite(record["smallest_singular_value"])
            and record["largest_singular_value"] is not None
            and np.isfinite(record["largest_singular_value"])
            and (
                (
                    record["status"] == "numerically_singular"
                    and record["condition_number"] is None
                )
                or (
                    record["status"] != "numerically_singular"
                    and record["condition_number"] is not None
                    and np.isfinite(record["condition_number"])
                    and record["solve_relative_residual"] is not None
                    and np.isfinite(record["solve_relative_residual"])
                )
            )
        )
        for record in pair_table
    )
    return {
        **condition,
        "materially_forced_near_witnesses": material_witnesses,
        "material_witness_classification_complete": all(
            witness["witness_class"] is not None
            for witness in material_witnesses
        ),
        "pair_status_counts": status_counts,
        "condition_quantiles": {
            "minimum": float(np.min(condition_values)),
            "median": float(np.quantile(condition_values, 0.5)),
            "q90": float(np.quantile(condition_values, 0.9)),
            "q99": float(np.quantile(condition_values, 0.99)),
            "maximum": float(np.max(condition_values)),
        },
        "worst_condition_pair": {
            "pair_identifier": worst["pair_identifier"],
            "left_block": worst["left_block"],
            "right_block": worst["right_block"],
            "left_label": worst["left_label"],
            "right_label": worst["right_label"],
            "output_wave_index": worst["output_wave_index"],
            "target_class": worst["target_class"],
            "condition_number": worst["condition_number"],
            "near_forcing_sensitivity": worst["near_forcing_sensitivity"],
        },
        "singular_classification_complete": bool(classification_complete),
    }


def _raw_condition(
    size: int,
    omega: float,
    eta: float,
    blocks: list[SpectralBlock],
    base_grid: Any,
    baseline_responses: dict[str, float] | None,
) -> dict[str, Any]:
    return _condition_diagnostics(
        _audit_condition(
            size,
            omega,
            eta,
            blocks,
            base_grid,
            baseline_responses,
        )
    )


def audit_cluster_complete_condition(
    size: int,
    omega: float,
    eta: float,
) -> dict[str, Any]:
    """Audit one registered Q006h condition with an unfiltered baseline."""

    if (
        size not in REGISTERED_GRID_SIZES
        or float(omega) not in REGISTERED_OMEGAS
        or float(eta) not in REGISTERED_ETAS
    ):
        raise ValueError("condition is outside the sealed Q006h campaign")
    size = int(size)
    omega = float(omega)
    eta = float(eta)
    blocks = build_first_shell_cluster_blocks(size, omega)
    base_grid = _base_spectral_grid(size, omega, blocks)
    baseline = _raw_condition(size, omega, 0.0, blocks, base_grid, None)
    if eta == 0.0:
        return baseline
    baseline_responses = {
        record["pair_identifier"]: record["global_l2_response_norm"]
        for record in baseline["target_pairs"]
    }
    return _raw_condition(
        size,
        omega,
        eta,
        blocks,
        base_grid,
        baseline_responses,
    )


def _fit_target_family(
    conditions: list[dict[str, Any]],
    eta: float,
    omega: float,
    target_class: str,
) -> dict[str, Any]:
    selected = sorted(
        (
            condition
            for condition in conditions
            if condition["eta"] == eta
            and condition["omega"] == omega
            and condition["grid_size"] in FIT_GRID_SIZES
        ),
        key=lambda condition: condition["grid_size"],
    )
    grid_sizes = np.asarray(
        [condition["grid_size"] for condition in selected],
        dtype=float,
    )
    metrics = {}
    for metric, bounds in FIT_WINDOWS.items():
        values = np.asarray(
            [
                condition["orbit_summaries"][target_class]["medians"][metric]
                for condition in selected
            ],
            dtype=float,
        )
        slope, intercept = np.polyfit(np.log(grid_sizes), np.log(values), 1)
        metrics[metric] = {
            "grid_sizes": [int(value) for value in grid_sizes],
            "values": [float(value) for value in values],
            "slope": float(slope),
            "log_intercept": float(intercept),
            "registered_window": list(bounds),
            "passed": bool(bounds[0] <= slope <= bounds[1]),
        }
    return {
        "eta": eta,
        "omega": omega,
        "target_class": target_class,
        "metrics": metrics,
        "all_registered_windows_passed": all(
            record["passed"] for record in metrics.values()
        ),
    }


def _spectral_gates(selected: list[dict[str, Any]]) -> dict[str, Any]:
    gates = {
        "normal_dominance_gap": {
            "value": min(
                condition["spectral"]["normal_dominance_gap"]
                for condition in selected
            ),
            "threshold": NORMAL_DOMINANCE_GAP_THRESHOLD,
        },
        "local_sylvester_separation": {
            "value": min(
                condition["spectral"]["minimum_local_sylvester_separation"]
                for condition in selected
            ),
            "threshold": LOCAL_SYLVESTER_SEPARATION_THRESHOLD,
        },
        "selected_riesz_projector_norm": {
            "value": max(
                condition["spectral"]["maximum_selected_riesz_projector_norm"]
                for condition in selected
            ),
            "threshold": PROJECTOR_NORM_CEILING,
        },
        "structural_fixed_leaf_residual": {
            "value": max(
                max(
                    condition["spectral"]["maximum_structural_residual"],
                    condition["spectral"]["maximum_fixed_leaf_residual"],
                )
                for condition in selected
            ),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
        },
        "selected_subspace_principal_angle": {
            "value": max(
                condition["spectral"][
                    "maximum_selected_subspace_principal_angle"
                ]
                for condition in selected
            ),
            "threshold": LOW_WAVE_SUBSPACE_ANGLE_TOLERANCE,
        },
        "selected_phase_change": {
            "value": max(
                condition["spectral"]["maximum_selected_phase_change"]
                for condition in selected
            ),
            "threshold": LOW_WAVE_PHASE_TOLERANCE,
        },
        "selected_relative_modulus_change": {
            "value": max(
                condition["spectral"][
                    "maximum_selected_relative_modulus_change"
                ]
                for condition in selected
            ),
            "threshold": LOW_WAVE_RELATIVE_MODULUS_TOLERANCE,
        },
    }
    lower_bounded = {"normal_dominance_gap", "local_sylvester_separation"}
    for name, gate in gates.items():
        gate["passed"] = (
            gate["value"] >= gate["threshold"]
            if name in lower_bounded
            else gate["value"] <= gate["threshold"]
        )
    return gates


def _coefficient_gates(
    selected: list[dict[str, Any]],
    selected_fits: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "complete_pair_enumeration": {
            "value": min(condition["pair_count"] for condition in selected),
            "threshold": PAIR_COUNT,
            "passed": all(
                condition["pair_count"] == PAIR_COUNT
                and condition["target_pair_count"] == TARGET_PAIR_COUNT
                for condition in selected
            ),
        },
        "no_numerical_singularity": {
            "value": sum(
                condition["numerically_singular_external_block_count"]
                for condition in selected
            ),
            "threshold": 0,
            "passed": all(
                condition["numerically_singular_external_block_count"] == 0
                for condition in selected
            ),
        },
        "structural_fixed_leaf_solve_residual": {
            "value": max(
                max(
                    condition["maximum_structural_residual"],
                    condition["maximum_fixed_leaf_residual"],
                    condition["maximum_solve_relative_residual"],
                )
                for condition in selected
            ),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": all(
                max(
                    condition["maximum_structural_residual"],
                    condition["maximum_fixed_leaf_residual"],
                    condition["maximum_solve_relative_residual"],
                )
                <= STRUCTURAL_RESIDUAL_TOLERANCE
                for condition in selected
            ),
        },
        "external_condition_ceiling": {
            "value": max(
                condition["maximum_condition_number"] for condition in selected
            ),
            "threshold": EXTERNAL_CONDITION_CEILING,
            "passed": all(
                condition["maximum_condition_number"]
                <= EXTERNAL_CONDITION_CEILING
                for condition in selected
            ),
        },
        "global_l2_response_ratio": {
            "value": max(
                condition[
                    "maximum_target_global_l2_response_ratio_to_unfiltered"
                ]
                for condition in selected
            ),
            "threshold": GLOBAL_L2_RESPONSE_RATIO_CEILING,
            "passed": all(
                condition[
                    "maximum_target_global_l2_response_ratio_to_unfiltered"
                ]
                <= GLOBAL_L2_RESPONSE_RATIO_CEILING
                for condition in selected
            ),
        },
        "registered_scaling_windows": {
            "value": sum(
                fit["all_registered_windows_passed"] for fit in selected_fits
            ),
            "threshold": len(TARGET_CLASSES),
            "passed": all(
                fit["all_registered_windows_passed"] for fit in selected_fits
            ),
        },
    }


def _family_record(
    conditions: list[dict[str, Any]],
    fits: list[dict[str, Any]],
    eta: float,
    omega: float,
) -> dict[str, Any]:
    selected = [
        condition
        for condition in conditions
        if condition["eta"] == eta and condition["omega"] == omega
    ]
    selected_fits = [
        fit for fit in fits if fit["eta"] == eta and fit["omega"] == omega
    ]
    spectral = _spectral_gates(selected)
    coefficient = _coefficient_gates(selected, selected_fits)
    spectral_passed = all(gate["passed"] for gate in spectral.values())
    coefficient_passed = all(gate["passed"] for gate in coefficient.values())
    return {
        "eta": eta,
        "omega": omega,
        "grid_count": len(selected),
        "minimum_normal_dominance_gap": spectral["normal_dominance_gap"][
            "value"
        ],
        "spectral_gates": spectral,
        "coefficient_gates": coefficient,
        "materially_forced_near_witness_count": sum(
            condition["materially_forced_near_witness_count"]
            for condition in selected
        ),
        "material_witness_class_counts": _witness_class_counts(selected),
        "spectral_passed": spectral_passed,
        "coefficient_passed": coefficient_passed,
        "viable": eta > 0.0 and spectral_passed and coefficient_passed,
    }


def run_cluster_complete_audit() -> dict[str, Any]:
    """Run the sealed Q006h 100-condition 24-mode campaign."""

    algebra = _filter_algebra_audit()
    conditions: list[dict[str, Any]] = []
    for size in REGISTERED_GRID_SIZES:
        for omega in REGISTERED_OMEGAS:
            blocks = build_first_shell_cluster_blocks(size, omega)
            base_grid = _base_spectral_grid(size, omega, blocks)
            baseline = _raw_condition(size, omega, 0.0, blocks, base_grid, None)
            conditions.append(baseline)
            baseline_responses = {
                record["pair_identifier"]: record["global_l2_response_norm"]
                for record in baseline["target_pairs"]
            }
            for eta in REGISTERED_ETAS[1:]:
                conditions.append(
                    _raw_condition(
                        size,
                        omega,
                        eta,
                        blocks,
                        base_grid,
                        baseline_responses,
                    )
                )
    fits = [
        _fit_target_family(conditions, eta, omega, target_class)
        for eta in REGISTERED_ETAS
        for omega in REGISTERED_OMEGAS
        for target_class in TARGET_CLASSES
    ]
    families = [
        _family_record(conditions, fits, eta, omega)
        for eta in REGISTERED_ETAS
        for omega in REGISTERED_OMEGAS
    ]
    viable = [family for family in families if family["viable"]]
    viable.sort(
        key=lambda family: (
            family["eta"],
            -family["minimum_normal_dominance_gap"],
            family["omega"],
        )
    )
    selected = viable[0] if viable else None
    registered_conditions = {
        (size, omega, eta)
        for size in REGISTERED_GRID_SIZES
        for omega in REGISTERED_OMEGAS
        for eta in REGISTERED_ETAS
    }
    observed_conditions = {
        (condition["grid_size"], condition["omega"], condition["eta"])
        for condition in conditions
    }
    validity_gates = {
        "filter_algebra": {
            "value": algebra["passed"],
            "threshold": True,
            "passed": algebra["passed"],
        },
        "registered_coverage": {
            "value": {
                "record_count": len(conditions),
                "unique_condition_count": len(observed_conditions),
                "missing_condition_count": len(
                    registered_conditions - observed_conditions
                ),
                "extra_condition_count": len(
                    observed_conditions - registered_conditions
                ),
            },
            "threshold": REGISTERED_CONDITION_COUNT,
            "passed": (
                len(conditions) == REGISTERED_CONDITION_COUNT
                and observed_conditions == registered_conditions
            ),
        },
        "selected_dimension_and_pair_enumeration": {
            "value": {
                "minimum_selected_dimension": min(
                    condition["selected_real_dimension"]
                    for condition in conditions
                ),
                "minimum_pair_count": min(
                    condition["pair_count"] for condition in conditions
                ),
                "minimum_target_pair_count": min(
                    condition["target_pair_count"] for condition in conditions
                ),
            },
            "threshold": {
                "selected_dimension": SELECTED_REAL_DIMENSION,
                "pair_count": PAIR_COUNT,
                "target_pair_count": TARGET_PAIR_COUNT,
            },
            "passed": all(
                condition["selected_real_dimension"] == SELECTED_REAL_DIMENSION
                and condition["pair_count"] == PAIR_COUNT
                and condition["target_pair_count"] == TARGET_PAIR_COUNT
                for condition in conditions
            ),
        },
        "structural_fixed_leaf_solve_residual": {
            "value": max(
                max(
                    condition["maximum_structural_residual"],
                    condition["maximum_fixed_leaf_residual"],
                    condition["maximum_solve_relative_residual"],
                    condition["spectral"]["maximum_structural_residual"],
                    condition["spectral"]["maximum_fixed_leaf_residual"],
                )
                for condition in conditions
            ),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": all(
                max(
                    condition["maximum_structural_residual"],
                    condition["maximum_fixed_leaf_residual"],
                    condition["maximum_solve_relative_residual"],
                    condition["spectral"]["maximum_structural_residual"],
                    condition["spectral"]["maximum_fixed_leaf_residual"],
                )
                <= STRUCTURAL_RESIDUAL_TOLERANCE
                for condition in conditions
            ),
        },
        "singular_classification_completeness": {
            "value": sum(
                condition["singular_classification_complete"]
                for condition in conditions
            ),
            "threshold": REGISTERED_CONDITION_COUNT,
            "passed": all(
                condition["singular_classification_complete"]
                for condition in conditions
            ),
        },
        "material_witness_classification_completeness": {
            "value": sum(
                condition["material_witness_classification_complete"]
                for condition in conditions
            ),
            "threshold": REGISTERED_CONDITION_COUNT,
            "passed": all(
                condition["material_witness_classification_complete"]
                for condition in conditions
            ),
        },
    }
    study_validity = all(gate["passed"] for gate in validity_gates.values())
    if study_validity and selected is not None:
        outcome = "accepted"
        classification = (
            "cluster-complete filtered finite-ladder prequalification passed"
        )
        decision = (
            "At least one registered positive-filter 24-mode family passes every "
            "five-grid spectral, coefficient, and scaling gate."
        )
        next_change = (
            "Preregister the full 2D dense quadratic chart at the deterministically "
            "selected eta/omega pair."
        )
    elif study_validity:
        outcome = "rejected"
        classification = "no viable registered cluster-complete filtered family"
        decision = (
            "The sealed 24-mode campaign is valid, but no positive-filter family "
            "passes every registered gate."
        )
        next_change = "Inspect the first deterministic failed Q006h family gate."
    else:
        outcome = "inconclusive"
        classification = "cluster-complete audit validity failure"
        decision = (
            "Coverage, enumeration, structural residual, or singular-classification "
            "validity failed, so no family verdict is issued."
        )
        next_change = "Repair the failed validity gate without tuning the sweep."
    return {
        "question": (
            "Does the 24-mode first-shell hydrodynamic cluster pass coefficient "
            "solvability and finite-ladder normal dominance under a registered "
            "conservative checkerboard filter?"
        ),
        "hypothesis": (
            "At least one registered positive eta/omega family passes every "
            "five-grid spectral, coefficient, response, and scaling gate."
        ),
        "registered_scope": {
            "grid_sizes": list(REGISTERED_GRID_SIZES),
            "fit_grid_sizes": list(FIT_GRID_SIZES),
            "etas": list(REGISTERED_ETAS),
            "omegas": list(REGISTERED_OMEGAS),
            "selected_wave_indices": [
                [-1, -1],
                [-1, 0],
                [-1, 1],
                [0, -1],
                [0, 1],
                [1, -1],
                [1, 0],
                [1, 1],
            ],
            "selected_labels_per_wave": [
                "shear",
                "acoustic_positive",
                "acoustic_negative",
            ],
            "selected_real_dimension": SELECTED_REAL_DIMENSION,
            "condition_count": REGISTERED_CONDITION_COUNT,
            "pair_count_per_condition": PAIR_COUNT,
            "target_pair_count_per_condition": TARGET_PAIR_COUNT,
            "selection_rule": [
                "minimum positive eta",
                "maximum five-grid minimum normal gap",
                "minimum omega",
            ],
            "mode_addition_enabled": False,
        },
        "filter_algebra": algebra,
        "conditions": conditions,
        "fits": fits,
        "families": families,
        "viable_families": viable,
        "selected_family": selected,
        "validity_gates": validity_gates,
        "summary": {
            "viable_family_count": len(viable),
            "selected_eta": None if selected is None else selected["eta"],
            "selected_omega": None if selected is None else selected["omega"],
            "selected_minimum_normal_gap": (
                None
                if selected is None
                else selected["minimum_normal_dominance_gap"]
            ),
            "maximum_condition_number": max(
                condition["maximum_condition_number"] for condition in conditions
            ),
            "maximum_structural_residual": max(
                condition["maximum_structural_residual"]
                for condition in conditions
            ),
            "maximum_solve_relative_residual": max(
                condition["maximum_solve_relative_residual"]
                for condition in conditions
            ),
            "materially_forced_near_witness_count": sum(
                condition["materially_forced_near_witness_count"]
                for condition in conditions
            ),
            "material_witness_class_counts": _witness_class_counts(conditions),
            "selected_material_witness_class_counts": (
                {}
                if selected is None
                else selected["material_witness_class_counts"]
            ),
        },
        "study_validity": "passed" if study_validity else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "limitations": [
            (
                "The selected family and filter define a finite-dimensional "
                "modified-map prequalification on five odd grids only."
            ),
            (
                "Acceptance would not prove all-grid or nonlinear normal "
                "attraction, nor existence or uniqueness of a full chart."
            ),
            (
                "No resonant response cluster is promoted in this minimal "
                "cluster-complete campaign."
            ),
        ],
        "next_change": next_change,
    }
