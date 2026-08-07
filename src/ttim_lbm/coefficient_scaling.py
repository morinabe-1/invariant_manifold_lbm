"""Sealed Q006c small-wave quadratic coefficient-scaling campaign."""

from __future__ import annotations

from itertools import combinations_with_replacement
from typing import Any

import numpy as np

from .mode_closure import (
    FORCING_SENSITIVITY_THRESHOLD,
    MATERIAL_NEAR_CONDITION_CEILING,
    STRUCTURAL_RESIDUAL_TOLERANCE,
    SpectralBlock,
    _audit_round,
    _build_sector,
    _initial_blocks,
    _product_block_and_forcing,
)
from .nonresonance import add_wave_indices

REGISTERED_GRID_SIZES = (17, 33, 65, 129, 257)
REGISTERED_OMEGAS = (1.0, 1.2, 1.5, 1.8)
FIT_GRID_SIZES = (33, 65, 129, 257)
TARGET_PAIR_COUNT = 16
ORBIT_RELATIVE_SPREAD_TOLERANCE = 1.0e-8

ACOUSTIC_SELF = "axial_acoustic_self_second_harmonic"
SHEAR_DIAGONAL = "axial_shear_diagonal_mixed_harmonic"
TARGET_CLASSES = (ACOUSTIC_SELF, SHEAR_DIAGONAL)

FIT_WINDOWS = {
    "smallest_singular_value": (-2.25, -1.75),
    "minimum_eigenvalue_detuning": (-2.25, -1.75),
    "condition_number": (1.75, 2.25),
    "forcing_norm": (-0.25, 0.25),
    "minimum_left_forcing_magnitude": (-1.25, -0.75),
    "local_amplitude_response_norm": (0.75, 1.25),
    "global_l2_response_norm": (-0.25, 0.25),
}
SPECTRAL_METRICS = (
    "smallest_singular_value",
    "minimum_eigenvalue_detuning",
    "condition_number",
)
FORCING_RESPONSE_METRICS = (
    "forcing_norm",
    "minimum_left_forcing_magnitude",
    "local_amplitude_response_norm",
    "global_l2_response_norm",
)
ORBIT_METRICS = (
    "smallest_singular_value",
    "largest_singular_value",
    "minimum_eigenvalue_detuning",
    "condition_number",
    "forcing_norm",
    "minimum_left_forcing_magnitude",
    "minimum_left_forcing_sensitivity",
    "local_amplitude_response_norm",
    "global_l2_response_norm",
)


def _complex_vector(values: np.ndarray) -> list[list[float]]:
    vector = np.asarray(values, dtype=np.complex128).reshape(-1)
    return [[float(value.real), float(value.imag)] for value in vector]


def _complex_matrix(values: np.ndarray) -> list[list[list[float]]]:
    matrix = np.asarray(values, dtype=np.complex128)
    if matrix.ndim != 2:
        raise ValueError("complex matrix serialization requires two dimensions")
    return [
        [[float(value.real), float(value.imag)] for value in row]
        for row in matrix
    ]


def _is_axial_first_shell(wave_index: tuple[int, int]) -> bool:
    return sorted(abs(int(value)) for value in wave_index) == [0, 1]


def _is_diagonal_first_shell(wave_index: tuple[int, int]) -> bool:
    return sorted(abs(int(value)) for value in wave_index) == [1, 1]


def _target_class(
    left: SpectralBlock,
    right: SpectralBlock,
    size: int,
) -> str | None:
    if (
        left.identifier == right.identifier
        and left.label in {"acoustic_positive", "acoustic_negative"}
        and _is_axial_first_shell(left.wave_index)
    ):
        return ACOUSTIC_SELF
    if left.label != "shear" or right.label != "shear":
        return None
    waves = (left.wave_index, right.wave_index)
    if not (
        any(_is_axial_first_shell(wave) for wave in waves)
        and any(_is_diagonal_first_shell(wave) for wave in waves)
    ):
        return None
    output_wave = add_wave_indices(left.wave_index, right.wave_index, size)
    if sorted(abs(int(value)) for value in output_wave) != [1, 2]:
        return None
    return SHEAR_DIAGONAL


def _relative_residual(numerator: np.ndarray, denominator: np.ndarray) -> float:
    denominator_norm = max(float(np.linalg.norm(denominator)), np.finfo(float).eps)
    return float(np.linalg.norm(numerator)) / denominator_norm


def _target_pair_record(
    pair_identifier: str,
    target_class: str,
    left: SpectralBlock,
    right: SpectralBlock,
    blocks: list[SpectralBlock],
    size: int,
    omega: float,
    compact_audit: dict[str, Any],
) -> dict[str, Any]:
    output_wave = add_wave_indices(left.wave_index, right.wave_index, size)
    sector = _build_sector(output_wave, blocks, size, omega)
    product_dynamics, forcing, product_basis, product_leakage = (
        _product_block_and_forcing(left, right, output_wave, size, omega)
    )
    if sector.external_dimension == 0:
        raise RuntimeError("registered Q006c target unexpectedly has no external output")
    active_forcing = sector.active_basis.conj().T @ forcing
    external_forcing = sector.external_basis.conj().T @ (
        sector.external_projector @ active_forcing
    )
    product_dimension = int(product_dynamics.shape[0])
    operator = (
        np.kron(np.eye(product_dimension), sector.external_matrix)
        - np.kron(product_dynamics.T, np.eye(sector.external_dimension))
    )
    forcing_vector = external_forcing.reshape(-1, order="F")
    left_singular, singular_values, right_adjoint = np.linalg.svd(
        operator,
        full_matrices=False,
    )
    solution = np.linalg.solve(operator, forcing_vector)
    residual = operator @ solution - forcing_vector
    largest = float(singular_values[0])
    smallest = float(singular_values[-1])
    forcing_norm = float(np.linalg.norm(forcing_vector))
    minimum_left_forcing = float(
        abs(np.vdot(left_singular[:, -1], forcing_vector))
    )
    product_eigenvalues = np.linalg.eigvals(product_dynamics)
    external_eigenvalues = np.linalg.eigvals(sector.external_matrix)
    detuning = min(
        float(abs(external - internal))
        for external in external_eigenvalues
        for internal in product_eigenvalues
    )
    response_norm = float(np.linalg.norm(solution))
    backward_denominator = max(
        float(np.linalg.norm(operator, ord=2)) * response_norm + forcing_norm,
        np.finfo(float).eps,
    )
    return {
        "pair_identifier": pair_identifier,
        "target_class": target_class,
        "left_block": left.identifier,
        "right_block": right.identifier,
        "left_label": left.label,
        "right_label": right.label,
        "left_wave_index": list(left.wave_index),
        "right_wave_index": list(right.wave_index),
        "output_wave_index": list(output_wave),
        "product_basis": product_basis,
        "product_dimension": product_dimension,
        "external_dimension": sector.external_dimension,
        "operator_shape": list(operator.shape),
        "operator": _complex_matrix(operator),
        "forcing_vector": _complex_vector(forcing_vector),
        "minimum_norm_response": _complex_vector(solution),
        "singular_values": [float(value) for value in singular_values],
        "left_singular_vectors": _complex_matrix(left_singular),
        "right_adjoint_singular_vectors": _complex_matrix(right_adjoint),
        "minimum_left_singular_vector": _complex_vector(left_singular[:, -1]),
        "minimum_right_singular_vector": _complex_vector(
            right_adjoint.conj().T[:, -1]
        ),
        "product_eigenvalues": _complex_vector(product_eigenvalues),
        "external_eigenvalues": _complex_vector(external_eigenvalues),
        "smallest_singular_value": smallest,
        "largest_singular_value": largest,
        "minimum_eigenvalue_detuning": detuning,
        "condition_number": largest / smallest,
        "forcing_norm": forcing_norm,
        "minimum_left_forcing_magnitude": minimum_left_forcing,
        "minimum_left_forcing_sensitivity": minimum_left_forcing
        / max(forcing_norm, np.finfo(float).eps),
        "local_amplitude_response_norm": response_norm,
        "global_l2_response_norm": response_norm / size,
        "solve_relative_residual": _relative_residual(residual, forcing_vector),
        "solve_normwise_backward_error": float(np.linalg.norm(residual))
        / backward_denominator,
        "product_invariance_leakage": product_leakage,
        "sector_structural_residual": sector.maximum_structural_residual,
        "fixed_leaf_forcing_residual": compact_audit[
            "fixed_leaf_forcing_residual"
        ],
        "full_audit_status": compact_audit["status"],
        "full_audit_condition_number": compact_audit["condition_number"],
    }


def _relative_range(values: list[float]) -> float:
    array = np.asarray(values, dtype=float)
    median = float(np.median(array))
    return float(np.max(array) - np.min(array)) / max(
        abs(median),
        np.finfo(float).eps,
    )


def _orbit_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    medians = {
        metric: float(np.median([float(record[metric]) for record in records]))
        for metric in ORBIT_METRICS
    }
    relative_spreads = {
        metric: _relative_range([float(record[metric]) for record in records])
        for metric in ORBIT_METRICS
    }
    return {
        "pair_count": len(records),
        "pair_identifiers": [record["pair_identifier"] for record in records],
        "medians": medians,
        "relative_spreads": relative_spreads,
        "maximum_relative_spread": max(relative_spreads.values()),
    }


def audit_scaling_condition(size: int, omega: float) -> dict[str, Any]:
    """Audit one sealed Q006c grid/relaxation condition."""

    if size not in REGISTERED_GRID_SIZES or float(omega) not in REGISTERED_OMEGAS:
        raise ValueError("condition is outside the sealed Q006c campaign")
    size = int(size)
    omega = float(omega)
    blocks = _initial_blocks(size, omega)
    round_record, _ = _audit_round(blocks, 0, size, omega)
    audit_by_identifier = {
        record["pair_identifier"]: record for record in round_record["pair_table"]
    }
    target_records: list[dict[str, Any]] = []
    material_witnesses: list[dict[str, Any]] = []
    outside_target_count = 0
    for pair_index, (left, right) in enumerate(
        combinations_with_replacement(blocks, 2)
    ):
        pair_identifier = f"p{pair_index:05d}"
        pair_audit = audit_by_identifier[pair_identifier]
        target_class = _target_class(left, right, size)
        materially_forced = bool(
            pair_audit["near_singular_count"] > 0
            and pair_audit["near_forcing_sensitivity"] is not None
            and pair_audit["near_forcing_sensitivity"]
            >= FORCING_SENSITIVITY_THRESHOLD
            and pair_audit["condition_number"] is not None
            and pair_audit["condition_number"]
            > MATERIAL_NEAR_CONDITION_CEILING
        )
        if materially_forced:
            material_witnesses.append(
                {
                    "pair_identifier": pair_identifier,
                    "target_class": target_class,
                    "left_block": left.identifier,
                    "right_block": right.identifier,
                    "left_label": left.label,
                    "right_label": right.label,
                    "left_wave_index": list(left.wave_index),
                    "right_wave_index": list(right.wave_index),
                    "output_wave_index": pair_audit["output_wave_index"],
                    "condition_number": pair_audit["condition_number"],
                    "near_forcing_sensitivity": pair_audit[
                        "near_forcing_sensitivity"
                    ],
                }
            )
            outside_target_count += target_class is None
        if target_class is not None:
            target_records.append(
                _target_pair_record(
                    pair_identifier,
                    target_class,
                    left,
                    right,
                    blocks,
                    size,
                    omega,
                    pair_audit,
                )
            )
    orbit_summaries = {
        target_class: _orbit_summary(
            [
                record
                for record in target_records
                if record["target_class"] == target_class
            ]
        )
        for target_class in TARGET_CLASSES
    }
    return {
        "grid_size": size,
        "omega": omega,
        "selected_real_dimension": sum(block.dimension for block in blocks),
        "pair_count": round_record["enumerated_pair_count"],
        "pair_enumeration_complete": round_record["pair_enumeration_complete"],
        "target_pair_count": len(target_records),
        "target_pair_counts_by_class": {
            target_class: sum(
                record["target_class"] == target_class
                for record in target_records
            )
            for target_class in TARGET_CLASSES
        },
        "target_pairs": target_records,
        "orbit_summaries": orbit_summaries,
        "materially_forced_near_witnesses": material_witnesses,
        "materially_forced_near_witness_count": len(material_witnesses),
        "materially_forced_near_outside_target_count": outside_target_count,
        "numerically_singular_external_block_count": round_record[
            "numerically_singular_external_block_count"
        ],
        "maximum_condition_number": round_record["maximum_condition_number"],
        "maximum_materially_forced_near_condition_number": round_record[
            "maximum_materially_forced_near_condition_number"
        ],
        "maximum_structural_residual": round_record[
            "maximum_structural_residual"
        ],
        "maximum_solve_relative_residual": round_record[
            "maximum_solve_relative_residual"
        ],
    }


def _fit_record(
    conditions: list[dict[str, Any]],
    omega: float,
    target_class: str,
) -> dict[str, Any]:
    selected = sorted(
        (
            condition
            for condition in conditions
            if condition["omega"] == omega
            and condition["grid_size"] in FIT_GRID_SIZES
        ),
        key=lambda condition: condition["grid_size"],
    )
    grid_sizes = np.asarray(
        [condition["grid_size"] for condition in selected],
        dtype=float,
    )
    metric_fits: dict[str, Any] = {}
    for metric, bounds in FIT_WINDOWS.items():
        values = np.asarray(
            [
                condition["orbit_summaries"][target_class]["medians"][metric]
                for condition in selected
            ],
            dtype=float,
        )
        slope, intercept = np.polyfit(np.log(grid_sizes), np.log(values), 1)
        fitted = np.exp(intercept + slope * np.log(grid_sizes))
        relative_fit_residual = float(
            np.linalg.norm(fitted - values) / np.linalg.norm(values)
        )
        metric_fits[metric] = {
            "grid_sizes": [int(value) for value in grid_sizes],
            "values": [float(value) for value in values],
            "slope": float(slope),
            "log_intercept": float(intercept),
            "relative_fit_residual": relative_fit_residual,
            "registered_window": list(bounds),
            "passed": bool(bounds[0] <= slope <= bounds[1]),
        }
    return {
        "omega": float(omega),
        "target_class": target_class,
        "metrics": metric_fits,
        "spectral_scaling_passed": all(
            metric_fits[metric]["passed"] for metric in SPECTRAL_METRICS
        ),
        "forcing_response_scaling_passed": all(
            metric_fits[metric]["passed"]
            for metric in FORCING_RESPONSE_METRICS
        ),
        "all_registered_windows_passed": all(
            record["passed"] for record in metric_fits.values()
        ),
    }


def run_coefficient_scaling_audit() -> dict[str, Any]:
    """Run the sealed 20-condition Q006c scaling campaign."""

    conditions = [
        audit_scaling_condition(size, omega)
        for size in REGISTERED_GRID_SIZES
        for omega in REGISTERED_OMEGAS
    ]
    fits = [
        _fit_record(conditions, omega, target_class)
        for omega in REGISTERED_OMEGAS
        for target_class in TARGET_CLASSES
    ]
    target_values = [
        float(record[metric])
        for condition in conditions
        for record in condition["target_pairs"]
        for metric in (
            "smallest_singular_value",
            "minimum_eigenvalue_detuning",
            "minimum_left_forcing_magnitude",
            "local_amplitude_response_norm",
            "global_l2_response_norm",
        )
    ]
    n257_conditions = [
        condition for condition in conditions if condition["grid_size"] == 257
    ]
    maximum_orbit_spread = max(
        summary["maximum_relative_spread"]
        for condition in conditions
        for summary in condition["orbit_summaries"].values()
    )
    validity_gates = {
        "registered_condition_count": {
            "value": len(conditions),
            "threshold": 20,
            "passed": len(conditions) == 20,
        },
        "complete_pair_and_target_enumeration": {
            "value": {
                "minimum_pair_count": min(
                    condition["pair_count"] for condition in conditions
                ),
                "minimum_target_count": min(
                    condition["target_pair_count"] for condition in conditions
                ),
            },
            "threshold": {"pair_count": 136, "target_count": TARGET_PAIR_COUNT},
            "passed": all(
                condition["pair_enumeration_complete"]
                and condition["pair_count"] == 136
                and condition["target_pair_count"] == TARGET_PAIR_COUNT
                and all(
                    count == TARGET_PAIR_COUNT // len(TARGET_CLASSES)
                    for count in condition["target_pair_counts_by_class"].values()
                )
                for condition in conditions
            ),
        },
        "structural_and_solve_residual": {
            "value": max(
                max(
                    condition["maximum_structural_residual"],
                    condition["maximum_solve_relative_residual"],
                    max(
                        max(
                            record["solve_relative_residual"],
                            record["solve_normwise_backward_error"],
                            record["product_invariance_leakage"],
                            record["sector_structural_residual"],
                            record["fixed_leaf_forcing_residual"],
                        )
                        for record in condition["target_pairs"]
                    ),
                )
                for condition in conditions
            ),
            "threshold": STRUCTURAL_RESIDUAL_TOLERANCE,
            "passed": all(
                condition["maximum_structural_residual"]
                <= STRUCTURAL_RESIDUAL_TOLERANCE
                and condition["maximum_solve_relative_residual"]
                <= STRUCTURAL_RESIDUAL_TOLERANCE
                and all(
                    max(
                        record["solve_relative_residual"],
                        record["solve_normwise_backward_error"],
                        record["product_invariance_leakage"],
                        record["sector_structural_residual"],
                        record["fixed_leaf_forcing_residual"],
                    )
                    <= STRUCTURAL_RESIDUAL_TOLERANCE
                    for record in condition["target_pairs"]
                )
                for condition in conditions
            ),
        },
        "no_numerical_singularity_and_positive_targets": {
            "value": {
                "numerically_singular_block_count": sum(
                    condition["numerically_singular_external_block_count"]
                    for condition in conditions
                ),
                "minimum_target_value": min(target_values),
            },
            "threshold": {
                "numerically_singular_block_count": 0,
                "minimum_target_value": 0.0,
            },
            "passed": all(
                condition["numerically_singular_external_block_count"] == 0
                for condition in conditions
            )
            and all(np.isfinite(value) and value > 0.0 for value in target_values),
        },
        "orbit_symmetry_spread": {
            "value": maximum_orbit_spread,
            "threshold": ORBIT_RELATIVE_SPREAD_TOLERANCE,
            "passed": maximum_orbit_spread
            <= ORBIT_RELATIVE_SPREAD_TOLERANCE,
        },
        "n257_witness_completeness": {
            "value": sum(
                condition["materially_forced_near_outside_target_count"]
                for condition in n257_conditions
            ),
            "threshold": 0,
            "passed": all(
                condition["materially_forced_near_outside_target_count"] == 0
                for condition in n257_conditions
            ),
        },
    }
    study_validity = all(gate["passed"] for gate in validity_gates.values())
    spectral_scaling = all(record["spectral_scaling_passed"] for record in fits)
    forcing_response_scaling = all(
        record["forcing_response_scaling_passed"] for record in fits
    )
    all_scaling = spectral_scaling and forcing_response_scaling
    if study_validity and all_scaling:
        outcome = "accepted"
        classification = "genuine weakly-forced small-k resonance supported"
        decision = (
            "The sealed ladder supports a genuine N^-2 spectral separation, "
            "N^-1 weakest-direction forcing, N local-amplitude response, and "
            "bounded global-L2 response for both registered witness orbits."
        )
        next_change = (
            "Preregister a checkerboard-damping model modification; retain the "
            "Q006c local-amplitude and global-L2 scaling baselines."
        )
    elif study_validity and spectral_scaling:
        outcome = "inconclusive"
        classification = "spectral-only near resonance"
        decision = (
            "The spectral near resonance scales as registered, but its forcing "
            "or response scaling does not support the sealed curvature claim."
        )
        next_change = (
            "Isolate the failed forcing or response exponent before changing "
            "the collision model."
        )
    elif study_validity:
        outcome = "rejected"
        classification = "registered small-k resonance scaling rejected"
        decision = "The registered spectral scaling windows are not satisfied."
        next_change = "Inspect the failed spectral witness before model modification."
    else:
        outcome = "inconclusive"
        classification = "validity or completeness failure"
        decision = (
            "The sealed campaign cannot issue a clean scaling classification "
            "because a validity or N=257 witness-completeness gate failed."
        )
        next_change = (
            "Expand or repair the witness audit without changing the Q006c "
            "registered outcome."
        )
    return {
        "question": (
            "Do the Q006n coefficient failures represent a genuine weakly forced "
            "small-wave second-harmonic resonance under the two registered "
            "coordinate normalizations?"
        ),
        "hypothesis": (
            "Both registered witness orbits have N^-2 spectral separation, N^2 "
            "condition growth, N^-1 weakest-direction forcing, N local-amplitude "
            "response, and bounded global-L2 response."
        ),
        "registered_scope": {
            "grid_sizes": list(REGISTERED_GRID_SIZES),
            "fit_grid_sizes": list(FIT_GRID_SIZES),
            "omegas": list(REGISTERED_OMEGAS),
            "condition_count": 20,
            "pair_count_per_condition": 136,
            "target_pair_count_per_condition": TARGET_PAIR_COUNT,
            "target_classes": list(TARGET_CLASSES),
            "mode_addition_enabled": False,
            "fit_windows": {
                metric: list(bounds) for metric, bounds in FIT_WINDOWS.items()
            },
            "orbit_relative_spread_tolerance": (
                ORBIT_RELATIVE_SPREAD_TOLERANCE
            ),
            "global_l2_normalization": (
                "local symbol response norm divided by side length N"
            ),
        },
        "conditions": conditions,
        "fits": fits,
        "summary": {
            "spectral_scaling_passed": spectral_scaling,
            "forcing_response_scaling_passed": forcing_response_scaling,
            "all_registered_scaling_windows_passed": all_scaling,
            "maximum_orbit_relative_spread": maximum_orbit_spread,
            "n257_materially_forced_near_witness_count": sum(
                condition["materially_forced_near_witness_count"]
                for condition in n257_conditions
            ),
            "n257_outside_target_witness_count": sum(
                condition["materially_forced_near_outside_target_count"]
                for condition in n257_conditions
            ),
            "maximum_condition_number": max(
                condition["maximum_condition_number"] for condition in conditions
            ),
            "maximum_target_condition_number": max(
                record["condition_number"]
                for condition in conditions
                for record in condition["target_pairs"]
            ),
            "maximum_structural_residual": max(
                condition["maximum_structural_residual"]
                for condition in conditions
            ),
            "maximum_solve_relative_residual": max(
                condition["maximum_solve_relative_residual"]
                for condition in conditions
            ),
        },
        "validity_gates": validity_gates,
        "study_validity": "passed" if study_validity else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "limitations": [
            (
                "The fitted powers cover four registered finite odd grids; they "
                "are not asymptotic proofs for every grid."
            ),
            (
                "Bounded global-L2 response corresponds to local Fourier "
                "amplitudes shrinking with N and does not imply bounded "
                "local-amplitude curvature."
            ),
            (
                "Q006c diagnoses coefficient scaling only and does not repair "
                "the negative near-Nyquist normal gap."
            ),
        ],
        "next_change": next_change,
    }
