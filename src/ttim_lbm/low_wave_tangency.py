"""Sealed Q006g diagonal low-wave hydrodynamic tangency audit."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from .checkerboard_filter import filter_multiplier, filtered_fourier_symbol
from .d2q9 import conserved_moment_matrix, equilibrium_tangent_matrix
from .nonresonance import simple_hydrodynamic_modes, wave_vector_from_index

REGISTERED_GRID_SIZES = (33, 65, 129, 257, 513, 1025, 2049)
FIT_GRID_SIZES = (129, 257, 513, 1025, 2049)
REGISTERED_ETAS = (0.0, 0.01, 0.02, 0.03, 0.05)
REGISTERED_OMEGAS = (1.0, 1.2, 1.5, 1.8)
DIAGONAL_ORBIT = ((1, 1), (-1, 1), (-1, -1), (1, -1))
REGISTERED_CONDITION_COUNT = 140
REGISTERED_WAVE_RECORD_COUNT = 560
EIGENSYSTEM_RESIDUAL_TOLERANCE = 1.0e-11
ORBIT_GAP_ABSOLUTE_SPREAD_TOLERANCE = 5.0e-13
SCALAR_GAP_IDENTITY_TOLERANCE = 5.0e-13
SCALING_WINDOW = (-4.25, -3.75)
SCALED_GAP_RELATIVE_SPREAD_TOLERANCE = 0.10


@dataclass(frozen=True)
class _DirectMode:
    eigenvalue: complex
    right_eigenvector: np.ndarray
    hydrodynamic_score: float
    transverse_fraction: float


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _direct_hydrodynamic_modes(
    matrix: np.ndarray,
    wave_vector: tuple[float, float],
) -> dict[str, _DirectMode]:
    eigenvalues, right = np.linalg.eig(matrix)
    moments = conserved_moment_matrix()
    equilibrium_projector = equilibrium_tangent_matrix() @ moments
    magnitude = float(np.hypot(*wave_vector))
    tangent = np.asarray(wave_vector, dtype=float) / magnitude
    transverse = np.array([-tangent[1], tangent[0]])
    diagnostics: list[tuple[float, float, int]] = []
    for index in range(eigenvalues.size):
        vector = right[:, index]
        conserved = moments @ vector
        diagnostics.append(
            (
                float(
                    np.linalg.norm(equilibrium_projector @ vector)
                    / np.linalg.norm(vector)
                ),
                float(
                    abs(transverse @ conserved[1:])
                    / max(float(np.linalg.norm(conserved)), np.finfo(float).eps)
                ),
                index,
            )
        )
    selected = sorted(diagnostics, key=lambda item: item[0], reverse=True)[:3]
    shear = max(selected, key=lambda item: item[1])
    acoustic = [item for item in selected if item[2] != shear[2]]
    acoustic.sort(key=lambda item: eigenvalues[item[2]].imag, reverse=True)
    labeled = {
        "shear": shear,
        "acoustic_positive": acoustic[0],
        "acoustic_negative": acoustic[1],
    }
    return {
        label: _DirectMode(
            eigenvalue=complex(eigenvalues[diagnostic[2]]),
            right_eigenvector=np.asarray(
                right[:, diagnostic[2]],
                dtype=np.complex128,
            ),
            hydrodynamic_score=diagnostic[0],
            transverse_fraction=diagnostic[1],
        )
        for label, diagnostic in labeled.items()
    }


def _wave_record(
    size: int,
    omega: float,
    eta: float,
    wave_index: tuple[int, int],
) -> dict[str, Any]:
    wave_vector = wave_vector_from_index(wave_index, size)
    multiplier = filter_multiplier(*wave_vector, eta)
    base_modes = simple_hydrodynamic_modes(*wave_vector, omega)
    matrix = filtered_fourier_symbol(*wave_vector, omega, eta)
    direct_modes = _direct_hydrodynamic_modes(matrix, wave_vector)
    matrix_scale = max(float(np.linalg.norm(matrix)), np.finfo(float).eps)
    mode_records = {}
    maximum_eigensystem_residual = 0.0
    maximum_matching_residual = 0.0
    for label in ("shear", "acoustic_positive", "acoustic_negative"):
        base = base_modes[label]
        direct = direct_modes[label]
        predicted = multiplier * base.eigenvalue
        eigensystem_residual = float(
            np.linalg.norm(
                matrix @ direct.right_eigenvector
                - direct.eigenvalue * direct.right_eigenvector
            )
            / matrix_scale
        )
        matching_residual = float(
            abs(direct.eigenvalue - predicted)
            / max(abs(predicted), np.finfo(float).eps)
        )
        maximum_eigensystem_residual = max(
            maximum_eigensystem_residual,
            eigensystem_residual,
        )
        maximum_matching_residual = max(
            maximum_matching_residual,
            matching_residual,
        )
        mode_records[label] = {
            "base_eigenvalue": _complex_record(base.eigenvalue),
            "predicted_filtered_eigenvalue": _complex_record(predicted),
            "direct_filtered_eigenvalue": _complex_record(direct.eigenvalue),
            "eigensystem_residual": eigensystem_residual,
            "matching_relative_residual": matching_residual,
            "base_hydrodynamic_score": base.hydrodynamic_score,
            "direct_hydrodynamic_score": direct.hydrodynamic_score,
            "base_transverse_fraction": base.transverse_fraction,
            "direct_transverse_fraction": direct.transverse_fraction,
        }
    base_shear_modulus = abs(base_modes["shear"].eigenvalue)
    base_acoustic_modulus = max(
        abs(base_modes["acoustic_positive"].eigenvalue),
        abs(base_modes["acoustic_negative"].eigenvalue),
    )
    direct_shear_modulus = abs(direct_modes["shear"].eigenvalue)
    direct_acoustic_modulus = max(
        abs(direct_modes["acoustic_positive"].eigenvalue),
        abs(direct_modes["acoustic_negative"].eigenvalue),
    )
    base_gap = float(base_shear_modulus - base_acoustic_modulus)
    direct_gap = float(direct_shear_modulus - direct_acoustic_modulus)
    predicted_gap = float(multiplier * base_gap)
    return {
        "grid_size": size,
        "omega": omega,
        "eta": eta,
        "wave_index": list(wave_index),
        "wave_vector": list(wave_vector),
        "filter_multiplier": multiplier,
        "modes": mode_records,
        "base_signed_gap": base_gap,
        "predicted_filtered_signed_gap": predicted_gap,
        "direct_filtered_signed_gap": direct_gap,
        "absolute_gap": abs(direct_gap),
        "relative_absolute_gap": abs(direct_gap)
        / max(direct_shear_modulus, np.finfo(float).eps),
        "scaled_signed_gap_n_fourth": float(size**4 * direct_gap),
        "scalar_gap_identity_absolute_error": abs(direct_gap - predicted_gap),
        "maximum_eigensystem_residual": maximum_eigensystem_residual,
        "maximum_eigenvalue_matching_relative_residual": (
            maximum_matching_residual
        ),
    }


def audit_tangency_condition(
    size: int,
    omega: float,
    eta: float,
) -> dict[str, Any]:
    """Audit one registered Q006g parameter/grid condition."""

    if (
        size not in REGISTERED_GRID_SIZES
        or float(omega) not in REGISTERED_OMEGAS
        or float(eta) not in REGISTERED_ETAS
    ):
        raise ValueError("condition is outside the sealed Q006g campaign")
    size = int(size)
    omega = float(omega)
    eta = float(eta)
    wave_records = [
        _wave_record(size, omega, eta, wave_index)
        for wave_index in DIAGONAL_ORBIT
    ]
    signed_gaps = [
        record["direct_filtered_signed_gap"] for record in wave_records
    ]
    absolute_gaps = [record["absolute_gap"] for record in wave_records]
    relative_gaps = [
        record["relative_absolute_gap"] for record in wave_records
    ]
    return {
        "grid_size": size,
        "omega": omega,
        "eta": eta,
        "wave_record_count": len(wave_records),
        "wave_records": wave_records,
        "median_signed_gap": float(np.median(signed_gaps)),
        "median_absolute_gap": float(np.median(absolute_gaps)),
        "median_relative_absolute_gap": float(np.median(relative_gaps)),
        "median_scaled_signed_gap_n_fourth": float(
            np.median(
                [record["scaled_signed_gap_n_fourth"] for record in wave_records]
            )
        ),
        "orbit_gap_absolute_spread": float(max(signed_gaps) - min(signed_gaps)),
        "maximum_eigensystem_residual": max(
            record["maximum_eigensystem_residual"] for record in wave_records
        ),
        "maximum_eigenvalue_matching_relative_residual": max(
            record["maximum_eigenvalue_matching_relative_residual"]
            for record in wave_records
        ),
        "maximum_scalar_gap_identity_absolute_error": max(
            record["scalar_gap_identity_absolute_error"]
            for record in wave_records
        ),
        "minimum_filter_multiplier": min(
            record["filter_multiplier"] for record in wave_records
        ),
    }


def _relative_spread(values: list[float]) -> float:
    array = np.asarray(values, dtype=float)
    median = float(np.median(array))
    return float(np.max(array) - np.min(array)) / max(
        abs(median),
        np.finfo(float).eps,
    )


def _fit_family(
    conditions: list[dict[str, Any]],
    eta: float,
    omega: float,
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
    metric_records = {}
    for metric in ("median_absolute_gap", "median_relative_absolute_gap"):
        values = np.asarray([condition[metric] for condition in selected])
        slope, intercept = np.polyfit(np.log(grid_sizes), np.log(values), 1)
        metric_records[metric] = {
            "grid_sizes": [int(value) for value in grid_sizes],
            "values": [float(value) for value in values],
            "slope": float(slope),
            "log_intercept": float(intercept),
            "registered_window": list(SCALING_WINDOW),
            "passed": bool(SCALING_WINDOW[0] <= slope <= SCALING_WINDOW[1]),
        }
    plateau_conditions = [
        condition for condition in selected if condition["grid_size"] >= 257
    ]
    scaled_values = [
        condition["grid_size"] ** 4 * condition["median_absolute_gap"]
        for condition in plateau_conditions
    ]
    scaled_spread = _relative_spread(scaled_values)
    expected_sign = -1 if omega == 1.0 else 1
    sign_passed = all(
        expected_sign * record["direct_filtered_signed_gap"] > 0.0
        for condition in selected
        for record in condition["wave_records"]
    )
    gates = {
        "absolute_gap_fourth_order_slope": {
            "value": metric_records["median_absolute_gap"]["slope"],
            "threshold": list(SCALING_WINDOW),
            "passed": metric_records["median_absolute_gap"]["passed"],
        },
        "relative_gap_fourth_order_slope": {
            "value": metric_records["median_relative_absolute_gap"]["slope"],
            "threshold": list(SCALING_WINDOW),
            "passed": metric_records["median_relative_absolute_gap"]["passed"],
        },
        "scaled_gap_plateau": {
            "value": scaled_spread,
            "threshold": SCALED_GAP_RELATIVE_SPREAD_TOLERANCE,
            "passed": scaled_spread <= SCALED_GAP_RELATIVE_SPREAD_TOLERANCE,
        },
        "registered_sign_pattern": {
            "value": expected_sign,
            "threshold": expected_sign,
            "passed": sign_passed,
        },
    }
    return {
        "eta": eta,
        "omega": omega,
        "fit_grid_sizes": list(FIT_GRID_SIZES),
        "metrics": metric_records,
        "scaled_gap_plateau": {
            "grid_sizes": [
                condition["grid_size"] for condition in plateau_conditions
            ],
            "values": [float(value) for value in scaled_values],
            "relative_spread": scaled_spread,
        },
        "expected_signed_gap_sign": expected_sign,
        "gates": gates,
        "passed": all(gate["passed"] for gate in gates.values()),
    }


def run_low_wave_tangency_audit() -> dict[str, Any]:
    """Run the sealed Q006g 140-condition diagonal tangency campaign."""

    conditions = [
        audit_tangency_condition(size, omega, eta)
        for size in REGISTERED_GRID_SIZES
        for omega in REGISTERED_OMEGAS
        for eta in REGISTERED_ETAS
    ]
    fits = [
        _fit_family(conditions, eta, omega)
        for eta in REGISTERED_ETAS
        for omega in REGISTERED_OMEGAS
    ]
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
    observed_wave_records = {
        (
            condition["grid_size"],
            condition["omega"],
            condition["eta"],
            tuple(record["wave_index"]),
        )
        for condition in conditions
        for record in condition["wave_records"]
    }
    numeric_values = [
        value
        for condition in conditions
        for record in condition["wave_records"]
        for value in (
            record["filter_multiplier"],
            record["base_signed_gap"],
            record["predicted_filtered_signed_gap"],
            record["direct_filtered_signed_gap"],
            record["absolute_gap"],
            record["relative_absolute_gap"],
            record["scaled_signed_gap_n_fourth"],
            record["scalar_gap_identity_absolute_error"],
            record["maximum_eigensystem_residual"],
            record["maximum_eigenvalue_matching_relative_residual"],
        )
    ]
    validity_gates = {
        "registered_coverage": {
            "value": {
                "condition_count": len(conditions),
                "unique_condition_count": len(observed_conditions),
                "wave_record_count": sum(
                    condition["wave_record_count"] for condition in conditions
                ),
                "unique_wave_record_count": len(observed_wave_records),
            },
            "threshold": {
                "condition_count": REGISTERED_CONDITION_COUNT,
                "wave_record_count": REGISTERED_WAVE_RECORD_COUNT,
            },
            "passed": (
                len(conditions) == REGISTERED_CONDITION_COUNT
                and observed_conditions == registered_conditions
                and len(observed_wave_records) == REGISTERED_WAVE_RECORD_COUNT
            ),
        },
        "direct_eigensystem": {
            "value": max(
                condition["maximum_eigensystem_residual"]
                for condition in conditions
            ),
            "threshold": EIGENSYSTEM_RESIDUAL_TOLERANCE,
            "passed": all(
                condition["maximum_eigensystem_residual"]
                <= EIGENSYSTEM_RESIDUAL_TOLERANCE
                for condition in conditions
            ),
        },
        "filtered_eigenvalue_matching": {
            "value": max(
                condition["maximum_eigenvalue_matching_relative_residual"]
                for condition in conditions
            ),
            "threshold": EIGENSYSTEM_RESIDUAL_TOLERANCE,
            "passed": all(
                condition["maximum_eigenvalue_matching_relative_residual"]
                <= EIGENSYSTEM_RESIDUAL_TOLERANCE
                for condition in conditions
            ),
        },
        "c4_gap_symmetry": {
            "value": max(
                condition["orbit_gap_absolute_spread"]
                for condition in conditions
            ),
            "threshold": ORBIT_GAP_ABSOLUTE_SPREAD_TOLERANCE,
            "passed": all(
                condition["orbit_gap_absolute_spread"]
                <= ORBIT_GAP_ABSOLUTE_SPREAD_TOLERANCE
                for condition in conditions
            ),
        },
        "scalar_gap_identity": {
            "value": max(
                condition["maximum_scalar_gap_identity_absolute_error"]
                for condition in conditions
            ),
            "threshold": SCALAR_GAP_IDENTITY_TOLERANCE,
            "passed": all(
                condition["maximum_scalar_gap_identity_absolute_error"]
                <= SCALAR_GAP_IDENTITY_TOLERANCE
                for condition in conditions
            ),
        },
        "finite_positive_multiplier": {
            "value": min(
                condition["minimum_filter_multiplier"]
                for condition in conditions
            ),
            "threshold": 0.0,
            "passed": bool(
                np.all(np.isfinite(numeric_values))
                and all(
                    condition["minimum_filter_multiplier"] > 0.0
                    for condition in conditions
                )
            ),
        },
    }
    hypothesis_gates = {
        "all_registered_family_fits": {
            "value": sum(fit["passed"] for fit in fits),
            "threshold": len(fits),
            "passed": all(fit["passed"] for fit in fits),
        },
        "registered_sign_pattern": {
            "value": sum(
                fit["gates"]["registered_sign_pattern"]["passed"]
                for fit in fits
            ),
            "threshold": len(fits),
            "passed": all(
                fit["gates"]["registered_sign_pattern"]["passed"]
                for fit in fits
            ),
        },
    }
    study_validity = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if study_validity and hypothesis_passed:
        outcome = "accepted"
        classification = (
            "same-sector hydrodynamic fourth-order tangency confirmed"
        )
        decision = (
            "The diagonal shear/acoustic modulus gap has the registered signed "
            "fourth-order scaling, and a positive scalar population filter "
            "cannot change its ordering or exponent."
        )
        next_change = (
            "Preregister a cluster-complete candidate family that promotes the "
            "diagonal acoustic modes; do not relax the Q006f gap threshold."
        )
    elif study_validity:
        outcome = "rejected"
        classification = "registered fourth-order tangency pattern not supported"
        decision = (
            "The symbol audit is valid, but at least one registered sign, slope, "
            "or scaled-gap plateau gate fails."
        )
        next_change = "Inspect the first failed Q006g hypothesis gate."
    else:
        outcome = "inconclusive"
        classification = "low-wave tangency audit validity failure"
        decision = (
            "Coverage, eigensystem, symmetry, scalar-identity, or finiteness "
            "validation failed, so no tangency classification is issued."
        )
        next_change = "Repair the failed validity gate without changing the sweep."
    return {
        "question": (
            "Is the sole Q006f failed family gate explained by a diagonal "
            "same-sector shear/acoustic fourth-order tangency that scalar "
            "population filtering cannot remove?"
        ),
        "hypothesis": (
            "Every registered eta/omega family has the fixed signed gap pattern, "
            "an N^-4 absolute and relative gap, and a bounded N^4 gap plateau."
        ),
        "registered_scope": {
            "grid_sizes": list(REGISTERED_GRID_SIZES),
            "fit_grid_sizes": list(FIT_GRID_SIZES),
            "etas": list(REGISTERED_ETAS),
            "omegas": list(REGISTERED_OMEGAS),
            "diagonal_orbit": [list(wave) for wave in DIAGONAL_ORBIT],
            "condition_count": REGISTERED_CONDITION_COUNT,
            "wave_record_count": REGISTERED_WAVE_RECORD_COUNT,
            "scaling_window": list(SCALING_WINDOW),
            "mode_addition_enabled": False,
            "full_brillouin_zone_sweep": False,
        },
        "conditions": conditions,
        "fits": fits,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "summary": {
            "fit_pass_count": sum(fit["passed"] for fit in fits),
            "minimum_absolute_gap_slope": min(
                fit["metrics"]["median_absolute_gap"]["slope"] for fit in fits
            ),
            "maximum_absolute_gap_slope": max(
                fit["metrics"]["median_absolute_gap"]["slope"] for fit in fits
            ),
            "minimum_relative_gap_slope": min(
                fit["metrics"]["median_relative_absolute_gap"]["slope"]
                for fit in fits
            ),
            "maximum_relative_gap_slope": max(
                fit["metrics"]["median_relative_absolute_gap"]["slope"]
                for fit in fits
            ),
            "maximum_scaled_gap_relative_spread": max(
                fit["scaled_gap_plateau"]["relative_spread"] for fit in fits
            ),
            "maximum_eigensystem_residual": validity_gates[
                "direct_eigensystem"
            ]["value"],
            "maximum_matching_residual": validity_gates[
                "filtered_eigenvalue_matching"
            ]["value"],
            "maximum_scalar_gap_identity_error": validity_gates[
                "scalar_gap_identity"
            ]["value"],
        },
        "study_validity": "passed" if study_validity else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "limitations": [
            (
                "This is a symbol-level diagonal-sector audit, not a full "
                "Brillouin-zone or quadratic coefficient campaign."
            ),
            (
                "Acceptance does not reverse Q006f, relax its absolute gap "
                "threshold, or establish a normally attracting manifold."
            ),
            (
                "The finite extended grid ladder supports a scaling diagnosis, "
                "not an all-grid asymptotic theorem."
            ),
        ],
        "next_change": next_change,
    }
