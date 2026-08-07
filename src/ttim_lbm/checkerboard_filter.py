"""Sealed Q006f conservative checkerboard-filter model audit."""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations_with_replacement
from typing import Any

import numpy as np

from .coefficient_scaling import (
    FIT_GRID_SIZES,
    FIT_WINDOWS,
    TARGET_CLASSES,
    TARGET_PAIR_COUNT,
    _orbit_summary,
    _target_class,
)
from .d2q9 import (
    bgk_periodic_step,
    conserved_moment_matrix,
    fourier_symbol,
    global_conserved_quantities,
    uniform_equilibrium,
)
from .mode_closure import (
    FORCING_SENSITIVITY_THRESHOLD,
    LOCAL_SYLVESTER_SEPARATION_THRESHOLD,
    MATERIAL_NEAR_CONDITION_CEILING,
    NEAR_SINGULAR_RELATIVE_THRESHOLD,
    NORMAL_DOMINANCE_GAP_THRESHOLD,
    PROJECTOR_NORM_CEILING,
    STRUCTURAL_RESIDUAL_TOLERANCE,
    SpectralBlock,
    _build_sector,
    _initial_blocks,
    _product_block_and_forcing,
    _Sector,
    _symmetry_diagnostics,
)
from .nonresonance import (
    NUMERICAL_RANK_MULTIPLIER,
    add_wave_indices,
    canonical_wave_index,
    wave_vector_from_index,
)

REGISTERED_ETAS = (0.0, 0.01, 0.02, 0.03, 0.05)
REGISTERED_OMEGAS = (1.0, 1.2, 1.5, 1.8)
REGISTERED_GRID_SIZES = (17, 33, 65, 129, 257)
REGISTERED_CONDITION_COUNT = 100
ALGEBRA_SEED = 20260809
ALGEBRA_STATE_COUNT = 64
FOURIER_SAMPLE_COUNT = 32
LOW_WAVE_SUBSPACE_ANGLE_TOLERANCE = 1.0e-10
LOW_WAVE_PHASE_TOLERANCE = 1.0e-12
LOW_WAVE_RELATIVE_MODULUS_TOLERANCE = 5.0e-3
EXTERNAL_CONDITION_CEILING = 1.0e9
GLOBAL_L2_RESPONSE_RATIO_CEILING = 1.10
FILTER_ALGEBRA_TOLERANCE = 1.0e-13
NYQUIST_ANCHOR_TOLERANCE = 1.0e-12


def _require_eta(eta: float) -> float:
    value = float(eta)
    if not np.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("filter eta must be finite and lie in [0, 1]")
    return value


def filter_multiplier(kx: float, ky: float, eta: float) -> float:
    """Return the scalar Fourier multiplier of the five-point filter."""

    eta = _require_eta(eta)
    return float(
        1.0
        - eta
        * (
            np.sin(0.5 * float(kx)) ** 2
            + np.sin(0.5 * float(ky)) ** 2
        )
    )


def conservative_checkerboard_filter(state: np.ndarray, eta: float) -> np.ndarray:
    """Apply the population-wise periodic five-point convex filter."""

    eta = _require_eta(eta)
    populations = np.asarray(state)
    if populations.ndim != 3 or populations.shape[-1] != 9:
        raise ValueError("D2Q9 state must have shape (ny, nx, 9)")
    neighbours = (
        np.roll(populations, 1, axis=0)
        + np.roll(populations, -1, axis=0)
        + np.roll(populations, 1, axis=1)
        + np.roll(populations, -1, axis=1)
    )
    return (1.0 - eta) * populations + 0.25 * eta * neighbours


def filtered_bgk_periodic_step(
    state: np.ndarray,
    omega: float,
    eta: float,
) -> np.ndarray:
    """Apply one periodic BGK step followed by the registered filter."""

    return conservative_checkerboard_filter(bgk_periodic_step(state, omega), eta)


def filtered_fourier_symbol(
    kx: float,
    ky: float,
    omega: float,
    eta: float,
) -> np.ndarray:
    """Return the exact linear Fourier block of the filtered map."""

    return filter_multiplier(kx, ky, eta) * fourier_symbol(kx, ky, omega)


def _complex_record(value: complex) -> dict[str, float]:
    return {"real": float(value.real), "imag": float(value.imag)}


def _relative_residual(numerator: np.ndarray, denominator: np.ndarray) -> float:
    denominator_norm = max(float(np.linalg.norm(denominator)), np.finfo(float).eps)
    return float(np.linalg.norm(numerator)) / denominator_norm


def _wave_multiplier(wave_index: tuple[int, int], size: int, eta: float) -> float:
    return filter_multiplier(*wave_vector_from_index(wave_index, size), eta)


def _filtered_blocks(
    base_blocks: list[SpectralBlock],
    size: int,
    eta: float,
) -> list[SpectralBlock]:
    return [
        replace(
            block,
            dynamics=_wave_multiplier(block.wave_index, size, eta)
            * block.dynamics,
            eigenvalues=_wave_multiplier(block.wave_index, size, eta)
            * block.eigenvalues,
        )
        for block in base_blocks
    ]


def _filtered_sector(
    wave_index: tuple[int, int],
    base_blocks: list[SpectralBlock],
    size: int,
    omega: float,
    eta: float,
    cache: dict[tuple[int, int], _Sector],
) -> _Sector:
    canonical = canonical_wave_index(wave_index, size)
    if canonical not in cache:
        cache[canonical] = _build_sector(canonical, base_blocks, size, omega)
    base = cache[canonical]
    multiplier = _wave_multiplier(canonical, size, eta)
    local_separation = base.local_sylvester_separation
    return replace(
        base,
        active_matrix=multiplier * base.active_matrix,
        selected_matrix=multiplier * base.selected_matrix,
        external_matrix=multiplier * base.external_matrix,
        selected_eigenvalues=multiplier * base.selected_eigenvalues,
        excluded_eigenvalues=multiplier * base.excluded_eigenvalues,
        local_sylvester_separation=(
            None
            if local_separation is None
            else abs(multiplier) * local_separation
        ),
    )


@dataclass(frozen=True)
class _BaseSpectralGrid:
    selected_eigenvalues: np.ndarray
    selected_wave_indices: np.ndarray
    excluded_eigenvalues: np.ndarray
    excluded_wave_indices: np.ndarray
    local_separations: np.ndarray
    local_wave_indices: np.ndarray
    maximum_projector_norm: float
    maximum_projector_wave_index: tuple[int, int]
    maximum_structural_residual: float
    maximum_fixed_leaf_residual: float


def _base_spectral_grid(
    size: int,
    omega: float,
    base_blocks: list[SpectralBlock],
) -> _BaseSpectralGrid:
    half = size // 2
    selected_waves = {block.wave_index for block in base_blocks}
    selected_eigenvalues: list[complex] = []
    selected_indices: list[tuple[int, int]] = []
    excluded_eigenvalues: list[complex] = []
    excluded_indices: list[tuple[int, int]] = []
    local_separations: list[float] = []
    local_indices: list[tuple[int, int]] = []
    projector_records: list[tuple[float, tuple[int, int]]] = []
    maximum_structural = 0.0
    maximum_fixed_leaf = 0.0
    for ix in range(-half, half + 1):
        for iy in range(-half, half + 1):
            wave_index = (ix, iy)
            if wave_index == (0, 0) or wave_index in selected_waves:
                sector = _build_sector(wave_index, base_blocks, size, omega)
                for value in sector.selected_eigenvalues:
                    selected_eigenvalues.append(complex(value))
                    selected_indices.append(wave_index)
                for value in sector.excluded_eigenvalues:
                    excluded_eigenvalues.append(complex(value))
                    excluded_indices.append(wave_index)
                if sector.local_sylvester_separation is not None:
                    local_separations.append(sector.local_sylvester_separation)
                    local_indices.append(wave_index)
                    projector_records.append(
                        (sector.selected_projector_norm, wave_index)
                    )
                maximum_structural = max(
                    maximum_structural,
                    sector.maximum_structural_residual,
                )
                maximum_fixed_leaf = max(
                    maximum_fixed_leaf,
                    sector.fixed_leaf_residual,
                )
            else:
                eigenvalues = np.linalg.eigvals(
                    fourier_symbol(
                        *wave_vector_from_index(wave_index, size),
                        omega,
                    )
                )
                excluded_eigenvalues.extend(complex(value) for value in eigenvalues)
                excluded_indices.extend([wave_index] * eigenvalues.size)
    if len(selected_eigenvalues) != 16:
        raise RuntimeError("Q006f spectral grid lost the registered 16 modes")
    maximum_projector = max(projector_records, key=lambda record: record[0])
    return _BaseSpectralGrid(
        selected_eigenvalues=np.asarray(selected_eigenvalues, dtype=np.complex128),
        selected_wave_indices=np.asarray(selected_indices, dtype=np.int64),
        excluded_eigenvalues=np.asarray(excluded_eigenvalues, dtype=np.complex128),
        excluded_wave_indices=np.asarray(excluded_indices, dtype=np.int64),
        local_separations=np.asarray(local_separations, dtype=float),
        local_wave_indices=np.asarray(local_indices, dtype=np.int64),
        maximum_projector_norm=float(maximum_projector[0]),
        maximum_projector_wave_index=maximum_projector[1],
        maximum_structural_residual=maximum_structural,
        maximum_fixed_leaf_residual=maximum_fixed_leaf,
    )


def _multipliers(
    wave_indices: np.ndarray,
    size: int,
    eta: float,
) -> np.ndarray:
    wave_indices = np.asarray(wave_indices, dtype=float)
    wave_vectors = 2.0 * np.pi * wave_indices / float(size)
    return 1.0 - eta * np.sum(np.sin(0.5 * wave_vectors) ** 2, axis=1)


def _spectral_screen(
    grid: _BaseSpectralGrid,
    size: int,
    eta: float,
) -> dict[str, Any]:
    selected_multipliers = _multipliers(grid.selected_wave_indices, size, eta)
    excluded_multipliers = _multipliers(grid.excluded_wave_indices, size, eta)
    selected_moduli = np.abs(grid.selected_eigenvalues) * np.abs(
        selected_multipliers
    )
    excluded_moduli = np.abs(grid.excluded_eigenvalues) * np.abs(
        excluded_multipliers
    )
    selected_index = int(np.argmin(selected_moduli))
    excluded_index = int(np.argmax(excluded_moduli))
    local_multipliers = _multipliers(grid.local_wave_indices, size, eta)
    filtered_local = grid.local_separations * np.abs(local_multipliers)
    local_index = int(np.argmin(filtered_local))
    selected_value = (
        selected_multipliers[selected_index] * grid.selected_eigenvalues[selected_index]
    )
    excluded_value = (
        excluded_multipliers[excluded_index] * grid.excluded_eigenvalues[excluded_index]
    )
    phase_changes = np.abs(
        np.angle(
            selected_multipliers.astype(np.complex128)
            * grid.selected_eigenvalues
            / grid.selected_eigenvalues
        )
    )
    return {
        "minimum_selected_modulus": float(selected_moduli[selected_index]),
        "minimum_selected_wave_index": grid.selected_wave_indices[
            selected_index
        ].tolist(),
        "minimum_selected_eigenvalue": _complex_record(complex(selected_value)),
        "maximum_excluded_modulus": float(excluded_moduli[excluded_index]),
        "maximum_excluded_wave_index": grid.excluded_wave_indices[
            excluded_index
        ].tolist(),
        "maximum_excluded_eigenvalue": _complex_record(complex(excluded_value)),
        "normal_dominance_gap": float(
            selected_moduli[selected_index] - excluded_moduli[excluded_index]
        ),
        "minimum_local_sylvester_separation": float(
            filtered_local[local_index]
        ),
        "minimum_local_separation_wave_index": grid.local_wave_indices[
            local_index
        ].tolist(),
        "maximum_selected_riesz_projector_norm": grid.maximum_projector_norm,
        "maximum_projector_wave_index": list(
            grid.maximum_projector_wave_index
        ),
        "maximum_structural_residual": grid.maximum_structural_residual,
        "maximum_fixed_leaf_residual": grid.maximum_fixed_leaf_residual,
        "maximum_selected_subspace_principal_angle": 0.0,
        "maximum_selected_phase_change": float(np.max(phase_changes)),
        "maximum_selected_relative_modulus_change": float(
            np.max(np.abs(selected_multipliers - 1.0))
        ),
    }


def _filtered_pair_audit(
    size: int,
    omega: float,
    eta: float,
    base_blocks: list[SpectralBlock],
    baseline_responses: dict[str, float] | None,
) -> dict[str, Any]:
    blocks = _filtered_blocks(base_blocks, size, eta)
    sector_cache: dict[tuple[int, int], _Sector] = {}
    pair_table: list[dict[str, Any]] = []
    for pair_index, (left, right) in enumerate(
        combinations_with_replacement(blocks, 2)
    ):
        pair_identifier = f"p{pair_index:05d}"
        output_wave = add_wave_indices(left.wave_index, right.wave_index, size)
        target_class = _target_class(left, right, size)
        sector = _filtered_sector(
            output_wave,
            base_blocks,
            size,
            omega,
            eta,
            sector_cache,
        )
        product_dynamics, forcing, _, product_leakage = (
            _product_block_and_forcing(
                left,
                right,
                output_wave,
                size,
                omega,
            )
        )
        forcing = _wave_multiplier(output_wave, size, eta) * forcing
        fixed_leaf_residual = (
            _relative_residual(conserved_moment_matrix() @ forcing, forcing)
            if output_wave == (0, 0)
            else 0.0
        )
        record: dict[str, Any] = {
            "pair_identifier": pair_identifier,
            "target_class": target_class,
            "left_block": left.identifier,
            "right_block": right.identifier,
            "left_label": left.label,
            "right_label": right.label,
            "left_wave_index": list(left.wave_index),
            "right_wave_index": list(right.wave_index),
            "output_wave_index": list(output_wave),
            "product_dimension": int(product_dynamics.shape[0]),
            "external_dimension": sector.external_dimension,
            "product_invariance_leakage": product_leakage,
            "fixed_leaf_forcing_residual": fixed_leaf_residual,
            "sector_structural_residual": sector.maximum_structural_residual,
            "sector_fixed_leaf_residual": sector.fixed_leaf_residual,
        }
        if sector.external_dimension == 0:
            record.update(
                {
                    "status": "internal_output_only",
                    "smallest_singular_value": None,
                    "largest_singular_value": None,
                    "condition_number": None,
                    "numerical_singular_count": 0,
                    "near_singular_count": 0,
                    "near_forcing_sensitivity": None,
                    "solve_relative_residual": None,
                }
            )
            pair_table.append(record)
            continue
        active_forcing = sector.active_basis.conj().T @ forcing
        external_forcing = sector.external_basis.conj().T @ (
            sector.external_projector @ active_forcing
        )
        product_dimension = int(product_dynamics.shape[0])
        operator = (
            np.kron(np.eye(product_dimension), sector.external_matrix)
            - np.kron(
                product_dynamics.T,
                np.eye(sector.external_dimension),
            )
        )
        forcing_vector = external_forcing.reshape(-1, order="F")
        left_singular, singular_values, _ = np.linalg.svd(
            operator,
            full_matrices=False,
        )
        largest = float(singular_values[0])
        smallest = float(singular_values[-1])
        rank_threshold = float(
            NUMERICAL_RANK_MULTIPLIER
            * np.finfo(float).eps
            * max(operator.shape)
            * largest
        )
        singular_indices = np.flatnonzero(singular_values <= rank_threshold)
        relative_values = singular_values / max(largest, np.finfo(float).eps)
        near_indices = np.flatnonzero(
            (singular_values > rank_threshold)
            & (relative_values < NEAR_SINGULAR_RELATIVE_THRESHOLD)
        )
        forcing_norm = float(np.linalg.norm(forcing_vector))
        near_sensitivity = (
            None
            if near_indices.size == 0
            else float(
                np.linalg.norm(
                    left_singular[:, near_indices].conj().T @ forcing_vector
                )
                / max(forcing_norm, np.finfo(float).eps)
            )
        )
        record.update(
            {
                "smallest_singular_value": smallest,
                "largest_singular_value": largest,
                "condition_number": (
                    None if singular_indices.size else largest / smallest
                ),
                "numerical_singular_count": int(singular_indices.size),
                "near_singular_count": int(near_indices.size),
                "near_forcing_sensitivity": near_sensitivity,
                "forcing_norm": forcing_norm,
            }
        )
        if singular_indices.size:
            record.update(
                {
                    "status": "numerically_singular",
                    "solve_relative_residual": None,
                }
            )
            pair_table.append(record)
            continue
        solution = np.linalg.solve(operator, forcing_vector)
        solve_residual = _relative_residual(
            operator @ solution - forcing_vector,
            forcing_vector,
        )
        record.update(
            {
                "status": "near_singular" if near_indices.size else "nonsingular",
                "solve_relative_residual": solve_residual,
            }
        )
        if target_class is not None:
            product_eigenvalues = np.linalg.eigvals(product_dynamics)
            external_eigenvalues = np.linalg.eigvals(sector.external_matrix)
            minimum_left_forcing = float(
                abs(np.vdot(left_singular[:, -1], forcing_vector))
            )
            response_norm = float(np.linalg.norm(solution))
            global_response = response_norm / size
            baseline = (
                global_response
                if baseline_responses is None
                else baseline_responses[pair_identifier]
            )
            record.update(
                {
                    "minimum_eigenvalue_detuning": min(
                        float(abs(external - internal))
                        for external in external_eigenvalues
                        for internal in product_eigenvalues
                    ),
                    "minimum_left_forcing_magnitude": minimum_left_forcing,
                    "minimum_left_forcing_sensitivity": minimum_left_forcing
                    / max(forcing_norm, np.finfo(float).eps),
                    "local_amplitude_response_norm": response_norm,
                    "global_l2_response_norm": global_response,
                    "unfiltered_global_l2_response_norm": baseline,
                    "global_l2_response_ratio_to_unfiltered": global_response
                    / max(baseline, np.finfo(float).eps),
                }
            )
        pair_table.append(record)
    for wave_index in {block.wave_index for block in blocks}:
        _filtered_sector(
            wave_index,
            base_blocks,
            size,
            omega,
            eta,
            sector_cache,
        )
    symmetry = _symmetry_diagnostics(blocks, size)
    target_pairs = [
        record for record in pair_table if record["target_class"] is not None
    ]
    orbit_summaries = {
        target_class: {
            **_orbit_summary(
                [
                    record
                    for record in target_pairs
                    if record["target_class"] == target_class
                ]
            ),
            "maximum_global_l2_response_ratio_to_unfiltered": max(
                record["global_l2_response_ratio_to_unfiltered"]
                for record in target_pairs
                if record["target_class"] == target_class
            ),
        }
        for target_class in TARGET_CLASSES
    }
    conditioned = [
        record
        for record in pair_table
        if record["condition_number"] is not None
    ]
    material_witnesses = [
        record
        for record in conditioned
        if record["near_singular_count"] > 0
        and record["near_forcing_sensitivity"] is not None
        and record["near_forcing_sensitivity"]
        >= FORCING_SENSITIVITY_THRESHOLD
        and record["condition_number"] > MATERIAL_NEAR_CONDITION_CEILING
    ]
    maximum_solve_residual = max(
        (
            record["solve_relative_residual"]
            for record in pair_table
            if record["solve_relative_residual"] is not None
        ),
        default=0.0,
    )
    maximum_structural = max(
        max(record["product_invariance_leakage"] for record in pair_table),
        max(record["fixed_leaf_forcing_residual"] for record in pair_table),
        max(record["sector_structural_residual"] for record in pair_table),
        max(record["sector_fixed_leaf_residual"] for record in pair_table),
        symmetry["maximum_c4_subspace_residual"],
        symmetry["maximum_conjugacy_subspace_residual"],
    )
    return {
        "pair_count": len(pair_table),
        "target_pair_count": len(target_pairs),
        "pair_table": pair_table,
        "target_pairs": target_pairs,
        "orbit_summaries": orbit_summaries,
        "numerically_singular_external_block_count": sum(
            record["numerical_singular_count"] > 0 for record in pair_table
        ),
        "materially_forced_near_witness_count": len(material_witnesses),
        "materially_forced_near_outside_target_count": sum(
            record["target_class"] is None for record in material_witnesses
        ),
        "materially_forced_near_witnesses": [
            {
                "pair_identifier": record["pair_identifier"],
                "target_class": record["target_class"],
                "output_wave_index": record["output_wave_index"],
                "condition_number": record["condition_number"],
                "near_forcing_sensitivity": record[
                    "near_forcing_sensitivity"
                ],
            }
            for record in material_witnesses
        ],
        "maximum_condition_number": max(
            record["condition_number"] for record in conditioned
        ),
        "maximum_structural_residual": maximum_structural,
        "maximum_solve_relative_residual": maximum_solve_residual,
        "maximum_fixed_leaf_residual": max(
            max(record["fixed_leaf_forcing_residual"] for record in pair_table),
            max(record["sector_fixed_leaf_residual"] for record in pair_table),
        ),
        "maximum_target_global_l2_response_ratio_to_unfiltered": max(
            record["global_l2_response_ratio_to_unfiltered"]
            for record in target_pairs
        ),
    }


def _audit_condition(
    size: int,
    omega: float,
    eta: float,
    base_blocks: list[SpectralBlock],
    base_grid: _BaseSpectralGrid,
    baseline_responses: dict[str, float] | None,
) -> dict[str, Any]:
    pairs = _filtered_pair_audit(
        size,
        omega,
        eta,
        base_blocks,
        baseline_responses,
    )
    spectral = _spectral_screen(base_grid, size, eta)
    return {
        "grid_size": size,
        "omega": omega,
        "eta": eta,
        "selected_real_dimension": 16,
        "spectral": spectral,
        **pairs,
    }


def audit_filter_condition(size: int, omega: float, eta: float) -> dict[str, Any]:
    """Audit one registered Q006f condition with an unfiltered baseline."""

    if (
        size not in REGISTERED_GRID_SIZES
        or float(omega) not in REGISTERED_OMEGAS
        or float(eta) not in REGISTERED_ETAS
    ):
        raise ValueError("condition is outside the sealed Q006f campaign")
    size = int(size)
    omega = float(omega)
    eta = float(eta)
    base_blocks = _initial_blocks(size, omega)
    base_grid = _base_spectral_grid(size, omega, base_blocks)
    baseline = _audit_condition(
        size,
        omega,
        0.0,
        base_blocks,
        base_grid,
        None,
    )
    if eta == 0.0:
        return baseline
    baseline_responses = {
        record["pair_identifier"]: record["global_l2_response_norm"]
        for record in baseline["target_pairs"]
    }
    return _audit_condition(
        size,
        omega,
        eta,
        base_blocks,
        base_grid,
        baseline_responses,
    )


def _fit_family(
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
    spectral_gates = {
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
        "structural_residual": {
            "value": max(
                condition["spectral"]["maximum_structural_residual"]
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
    for name, gate in spectral_gates.items():
        gate["passed"] = (
            gate["value"] <= gate["threshold"]
            if name
            in {
                "selected_riesz_projector_norm",
                "structural_residual",
                "selected_subspace_principal_angle",
                "selected_phase_change",
                "selected_relative_modulus_change",
            }
            else gate["value"] >= gate["threshold"]
        )
    coefficient_gates = {
        "complete_pair_enumeration": {
            "value": min(condition["pair_count"] for condition in selected),
            "threshold": 136,
            "passed": all(
                condition["pair_count"] == 136
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
        "n257_witness_completeness": {
            "value": sum(
                condition["materially_forced_near_outside_target_count"]
                for condition in selected
                if condition["grid_size"] == 257
            ),
            "threshold": 0,
            "passed": all(
                condition["materially_forced_near_outside_target_count"] == 0
                for condition in selected
                if condition["grid_size"] == 257
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
    spectral_passed = all(gate["passed"] for gate in spectral_gates.values())
    coefficient_passed = all(
        gate["passed"] for gate in coefficient_gates.values()
    )
    return {
        "eta": eta,
        "omega": omega,
        "grid_count": len(selected),
        "minimum_normal_dominance_gap": spectral_gates[
            "normal_dominance_gap"
        ]["value"],
        "spectral_gates": spectral_gates,
        "coefficient_gates": coefficient_gates,
        "spectral_passed": spectral_passed,
        "coefficient_passed": coefficient_passed,
        "viable": eta > 0.0 and spectral_passed and coefficient_passed,
    }


def _filter_algebra_audit() -> dict[str, Any]:
    rng = np.random.default_rng(ALGEBRA_SEED)
    states = [rng.uniform(0.01, 1.0, size=(7, 9, 9)) for _ in range(ALGEBRA_STATE_COUNT)]
    coordinates = [
        np.array(
            [
                rng.uniform(-0.1, 0.1),
                rng.uniform(-0.02, 0.02),
                rng.uniform(-0.02, 0.02),
            ]
        )
        for _ in range(ALGEBRA_STATE_COUNT)
    ]
    wave_indices = [
        (
            int(rng.integers(-8, 9)),
            int(rng.integers(-8, 9)),
        )
        for _ in range(FOURIER_SAMPLE_COUNT)
    ]
    eta_records = []
    for eta in REGISTERED_ETAS:
        weights = [1.0 - eta] + [0.25 * eta] * 4
        conservation_residual = 0.0
        constant_residual = 0.0
        minimum_margin = np.inf
        for state, coordinate in zip(states, coordinates, strict=True):
            filtered = conservative_checkerboard_filter(state, eta)
            conservation_residual = max(
                conservation_residual,
                _relative_residual(
                    global_conserved_quantities(filtered)
                    - global_conserved_quantities(state),
                    global_conserved_quantities(state),
                ),
            )
            minimum_margin = min(
                minimum_margin,
                float(np.min(filtered) - np.min(state)),
            )
            equilibrium = uniform_equilibrium(7, 9, coordinate)
            constant_residual = max(
                constant_residual,
                _relative_residual(
                    conservative_checkerboard_filter(equilibrium, eta)
                    - equilibrium,
                    equilibrium,
                ),
            )
        fourier_discrepancy = 0.0
        y, x = np.meshgrid(np.arange(17), np.arange(17), indexing="ij")
        for wave_index in wave_indices:
            kx, ky = wave_vector_from_index(wave_index, 17)
            plane = np.exp(1j * (kx * x + ky * y))
            state = np.zeros((17, 17, 9), dtype=np.complex128)
            state[..., 0] = plane
            expected = filter_multiplier(kx, ky, eta) * state
            fourier_discrepancy = max(
                fourier_discrepancy,
                _relative_residual(
                    conservative_checkerboard_filter(state, eta) - expected,
                    expected,
                ),
            )
        anchor_error = 0.0
        for omega in REGISTERED_OMEGAS:
            for wave_vector in ((np.pi, 0.0), (0.0, np.pi)):
                eigenvalues = np.linalg.eigvals(
                    filtered_fourier_symbol(*wave_vector, omega, eta)
                )
                anchor_error = max(
                    anchor_error,
                    float(np.min(np.abs(eigenvalues + (1.0 - eta)))),
                )
        eta_records.append(
            {
                "eta": eta,
                "weights": weights,
                "minimum_weight": min(weights),
                "weight_sum_error": abs(sum(weights) - 1.0),
                "maximum_conservation_residual": conservation_residual,
                "maximum_constant_state_residual": constant_residual,
                "minimum_population_margin": float(minimum_margin),
                "maximum_fourier_multiplier_discrepancy": fourier_discrepancy,
                "maximum_checkerboard_anchor_error": anchor_error,
            }
        )
    gates = {
        "convex_weights": {
            "value": min(record["minimum_weight"] for record in eta_records),
            "threshold": 0.0,
            "passed": all(
                record["minimum_weight"] >= 0.0
                and record["weight_sum_error"] <= FILTER_ALGEBRA_TOLERANCE
                for record in eta_records
            ),
        },
        "conservation_and_constant_state": {
            "value": max(
                max(
                    record["maximum_conservation_residual"],
                    record["maximum_constant_state_residual"],
                )
                for record in eta_records
            ),
            "threshold": FILTER_ALGEBRA_TOLERANCE,
            "passed": all(
                record["maximum_conservation_residual"]
                <= FILTER_ALGEBRA_TOLERANCE
                and record["maximum_constant_state_residual"]
                <= FILTER_ALGEBRA_TOLERANCE
                for record in eta_records
            ),
        },
        "positivity_minimum_principle": {
            "value": min(
                record["minimum_population_margin"] for record in eta_records
            ),
            "threshold": -FILTER_ALGEBRA_TOLERANCE,
            "passed": all(
                record["minimum_population_margin"]
                >= -FILTER_ALGEBRA_TOLERANCE
                for record in eta_records
            ),
        },
        "fourier_multiplier": {
            "value": max(
                record["maximum_fourier_multiplier_discrepancy"]
                for record in eta_records
            ),
            "threshold": FILTER_ALGEBRA_TOLERANCE,
            "passed": all(
                record["maximum_fourier_multiplier_discrepancy"]
                <= FILTER_ALGEBRA_TOLERANCE
                for record in eta_records
            ),
        },
        "checkerboard_anchor": {
            "value": max(
                record["maximum_checkerboard_anchor_error"]
                for record in eta_records
            ),
            "threshold": NYQUIST_ANCHOR_TOLERANCE,
            "passed": all(
                record["maximum_checkerboard_anchor_error"]
                <= NYQUIST_ANCHOR_TOLERANCE
                for record in eta_records
            ),
        },
    }
    return {
        "seed": ALGEBRA_SEED,
        "state_count": ALGEBRA_STATE_COUNT,
        "fourier_sample_count": FOURIER_SAMPLE_COUNT,
        "eta_records": eta_records,
        "gates": gates,
        "passed": all(gate["passed"] for gate in gates.values()),
    }


def run_checkerboard_filter_audit() -> dict[str, Any]:
    """Run the sealed Q006f 100-condition filtered-map campaign."""

    algebra = _filter_algebra_audit()
    conditions: list[dict[str, Any]] = []
    for size in REGISTERED_GRID_SIZES:
        for omega in REGISTERED_OMEGAS:
            base_blocks = _initial_blocks(size, omega)
            base_grid = _base_spectral_grid(size, omega, base_blocks)
            baseline = _audit_condition(
                size,
                omega,
                0.0,
                base_blocks,
                base_grid,
                None,
            )
            conditions.append(baseline)
            baseline_responses = {
                record["pair_identifier"]: record["global_l2_response_norm"]
                for record in baseline["target_pairs"]
            }
            for eta in REGISTERED_ETAS[1:]:
                conditions.append(
                    _audit_condition(
                        size,
                        omega,
                        eta,
                        base_blocks,
                        base_grid,
                        baseline_responses,
                    )
                )
    fits = [
        _fit_family(conditions, eta, omega, target_class)
        for eta in REGISTERED_ETAS
        for omega in REGISTERED_OMEGAS
        for target_class in TARGET_CLASSES
    ]
    families = [
        _family_record(conditions, fits, eta, omega)
        for eta in REGISTERED_ETAS
        for omega in REGISTERED_OMEGAS
    ]
    viable = [record for record in families if record["viable"]]
    viable.sort(
        key=lambda record: (
            record["eta"],
            -record["minimum_normal_dominance_gap"],
            record["omega"],
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
        "registered_condition_count": {
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
        "complete_pair_and_target_enumeration": {
            "value": {
                "minimum_pair_count": min(
                    condition["pair_count"] for condition in conditions
                ),
                "minimum_target_count": min(
                    condition["target_pair_count"] for condition in conditions
                ),
            },
            "threshold": {
                "pair_count": 136,
                "target_pair_count": TARGET_PAIR_COUNT,
            },
            "passed": all(
                condition["pair_count"] == 136
                and condition["target_pair_count"] == TARGET_PAIR_COUNT
                for condition in conditions
            ),
        },
        "structural_and_solve_residual": {
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
    }
    study_validity = all(gate["passed"] for gate in validity_gates.values())
    if study_validity and selected is not None:
        outcome = "accepted"
        classification = "filtered finite-ladder prequalification passed"
        decision = (
            "The deterministic registered rule selected a conservative filtered "
            "map that passes all five-grid spectral, coefficient, scaling, and "
            "low-wave-distortion gates."
        )
        next_change = (
            "Preregister the full 2D dense quadratic Q006 chart for the selected "
            "filtered map; keep unfiltered BGK as a failed baseline."
        )
    elif study_validity:
        outcome = "rejected"
        classification = "no viable registered filtered family"
        decision = (
            "The sealed filter sweep is numerically valid but no registered "
            "eta/omega pair passes every family gate."
        )
        next_change = (
            "Inspect the first deterministic failed family gate before proposing "
            "another model modification."
        )
    else:
        outcome = "inconclusive"
        classification = "filter audit validity failure"
        decision = (
            "A filter algebra, enumeration, or residual gate failed, so the "
            "sealed sweep cannot issue a model-selection verdict."
        )
        next_change = "Repair the failed validity gate without tuning the sweep."
    return {
        "question": (
            "Can the registered conservative checkerboard filter recover finite-"
            "ladder normal dominance without degrading low-wave geometry or the "
            "Q006c coefficient scaling baselines?"
        ),
        "hypothesis": (
            "At least one registered eta/omega pair passes all five-grid spectral, "
            "coefficient, scaling, conservation, positivity, and low-wave gates."
        ),
        "registered_scope": {
            "etas": list(REGISTERED_ETAS),
            "omegas": list(REGISTERED_OMEGAS),
            "grid_sizes": list(REGISTERED_GRID_SIZES),
            "condition_count": REGISTERED_CONDITION_COUNT,
            "pair_count_per_condition": 136,
            "target_pair_count_per_condition": TARGET_PAIR_COUNT,
            "fit_grid_sizes": list(FIT_GRID_SIZES),
            "fit_windows": {
                metric: list(bounds) for metric, bounds in FIT_WINDOWS.items()
            },
            "selection_rule": [
                "minimum positive eta",
                "maximum five-grid minimum normal gap",
                "minimum omega",
            ],
            "mode_addition_enabled": False,
            "filter_order": "post-BGK-step population-wise five-point convolution",
        },
        "filter_algebra": algebra,
        "conditions": conditions,
        "fits": fits,
        "families": families,
        "viable_families": viable,
        "selected_family": selected,
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
        },
        "validity_gates": validity_gates,
        "study_validity": "passed" if study_validity else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "decision": decision,
        "limitations": [
            (
                "The filter defines a modified map and adds eta*|k|^2/4 low-wave "
                "attenuation; it does not preserve the original transport "
                "coefficients exactly."
            ),
            (
                "Passing five finite odd grids is not a theorem for every grid or "
                "a proof of nonlinear normal attraction."
            ),
            (
                "The audit is a prequalification only and does not construct or "
                "prove existence or uniqueness of the full 2D invariant chart."
            ),
        ],
        "next_change": next_change,
    }
