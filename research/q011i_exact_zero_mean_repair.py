"""Q011i exact-dyadic zero-mean forcing compatibility repair."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from scipy import linalg

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011h_sparse_chart_equivalence as q011h
from ttim_lbm.checkerboard_filter import conservative_checkerboard_filter
from ttim_lbm.d2q9 import (
    D2Q9_VELOCITIES,
    collide_bgk,
    macroscopic,
    stream_periodic,
    uniform_equilibrium,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]
ComplexArray = npt.NDArray[np.complex128]

SIZE = q011b.SIZE
STRIPE_DIMENSION = q011b.STRIPE_DIMENSION
FIXED_LEAF_DIMENSION = q011b.FIXED_LEAF_DIMENSION

Q011B_ARTIFACT_SHA256 = "477202184694da1386c6b5bc0f0441e004a7a44f7a7b064f1d060d50adc66c27"
Q011B_RUNNER_SHA256 = "bac9448f280ce2dfb2e1627ce1558b792cb53e05746b94246baa6c329b8c8ef0"
Q011B_INPUT_DIGEST = "53dea81353ed4bcd77ab0c06533528f6d867d8b1bfa80d3d2ac3eddd7cf7dfbb"
Q011B_FIXED_POINT_DIGEST = "8db05ad1e7ae7806b70b6330d798f6dad05bc8718027ba13cb315116b021b17c"
Q011B_SPECTRUM_DIGEST = "3ab8866e141b64a4d1d81bdfae1a70c61d8e7964d8480e2bd7ec7c7e174850fc"
Q011B_RESULT_DIGEST = "66c4b579dbd7d7c391fd2017f165c2de251ecf850b7c485cb936b9742c8addf6"
RAW_WAVEFORM_SHA256 = "0c1d55dfbd0611f7dcc3413ecde839e01487d6317e232c9362aad984e5bab162"
RAW_SOURCE_SHA256 = "7d69bfc45429c43e8094e03565fd71c83e5f48d3077437949b38d185d5fe7972"
RAW_STRIPE_STATE_SHA256 = "612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613"
RAW_EXACT_WAVEFORM_SUM = Fraction(-71, 2**78)
SYMMETRIZED_EXACT_WAVEFORM_SUM = Fraction(-7, 2**75)

Q011H_ARTIFACT_SHA256 = "2cfcf5cb76698ae8e451f448a3048e3d29a1b8aed034d3afa5c25f7fd66038f5"
Q011H_RUNNER_SHA256 = "1e6848e572137d019531514235741b18ca10644dd7d14e304dc26d92d81cda9e"
Q011H_INPUT_DIGEST = "c9ea06c8961940f54dd3c02e3d68d7ba777e77fc9be2f0a7c3eecab5ab257b83"
Q011H_COEFFICIENT_DIGEST = "2ab44a23811ef9f7e1975fb27561dd92660938778bf73ef149e46ed04f399669"
Q011H_CAMPAIGN_DIGEST = "bbb6a489fc76af150a3a162f585b0b2e1a65d0445d5eb14ab11b280bc492a035"
Q011H_RESULT_DIGEST = "a78812d93063ed7deeaca09dad5feb2cf018fb1bec315dab94b4f02d27f75864"
SEALED_PACKAGE_SOURCE_SHA256 = q011h.q011g.SEALED_PACKAGE_SOURCE_SHA256

REPAIRED_WAVEFORM_SHA256 = "025d6122db8e0d3512224ce4a2af82d57b5728ce0c7450425436218dd561bcbf"
REPAIRED_SOURCE_SHA256 = "24bb558464cce4ac154b3f2574bd1fe816d11d58c9365e8312f12b0a389df490"
REGISTERED_WAVEFORM_PAIR = 3
REGISTERED_WAVEFORM_ULP_SHIFT = 7
WAVEFORM_SEARCH_MAXIMUM_ULPS = 128
SOURCE_SEARCH_MAXIMUM_ULPS = 8

MAXIMUM_WAVEFORM_CHANGED_ENTRY_COUNT = 11
MAXIMUM_WAVEFORM_COMPONENT_PERTURBATION = 5.0e-22
MAXIMUM_WAVEFORM_RELATIVE_PERTURBATION = 1.0e-14
MAXIMUM_WAVEFORM_FOURIER_LEAKAGE = 1.0e-14
MAXIMUM_SOURCE_COMPONENT_PERTURBATION = 1.0e-22
MAXIMUM_SOURCE_RELATIVE_PERTURBATION = 1.0e-14
MAXIMUM_SOURCE_ULP_SHIFT = 1

MAXIMUM_PROJECTED_RESIDUAL = 5.0e-13
MAXIMUM_FULL_RESIDUAL = 5.0e-12
MAXIMUM_COMPONENT_RESIDUAL = 5.0e-13
MAXIMUM_TWO_START_DISTANCE = 1.0e-11
MAXIMUM_TWO_START_RELATIVE_DISTANCE = 1.0e-9
MAXIMUM_SEALED_STATE_DISTANCE = 1.0e-11
MAXIMUM_SEALED_STATE_RELATIVE_DISTANCE = 1.0e-6
MAXIMUM_BLOCK_MATRIX_RELATIVE_PERTURBATION = 1.0e-10
MAXIMUM_BLOCK_SPECTRUM_HAUSDORFF_DISTANCE = 1.0e-9


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _fraction_from_float(value: float | np.floating[Any]) -> Fraction:
    return Fraction.from_float(float(value))


def _exact_sum(values: npt.ArrayLike) -> Fraction:
    return sum(
        (_fraction_from_float(value) for value in np.asarray(values).ravel()),
        Fraction(0),
    )


def _fraction_vector_record(values: list[Fraction]) -> list[dict[str, Any]]:
    return [_fraction_record(value) for value in values]


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "omega": q011b.OMEGA,
        "eta": q011b.ETA,
        "fixed_conservation_leaf": True,
        "raw_exact_waveform_sum": _fraction_record(RAW_EXACT_WAVEFORM_SUM),
        "symmetrized_exact_waveform_sum": _fraction_record(SYMMETRIZED_EXACT_WAVEFORM_SUM),
        "waveform_repair": {
            "pair_midpoint_rounding": "nearest-even binary64",
            "search_maximum_ulps": WAVEFORM_SEARCH_MAXIMUM_ULPS,
            "candidate_order": "0,+1,-1,+2,-2,...",
            "selection_order": "absolute shift, pair index, signed shift",
            "selected_pair": [REGISTERED_WAVEFORM_PAIR, SIZE - REGISTERED_WAVEFORM_PAIR],
            "selected_ulp_shift": REGISTERED_WAVEFORM_ULP_SHIFT,
            "repaired_waveform_sha256": REPAIRED_WAVEFORM_SHA256,
        },
        "source_repair": {
            "search_maximum_ulps": SOURCE_SEARCH_MAXIMUM_ULPS,
            "candidate_order": "0,+1,-1,+2,-2,...",
            "repaired_source_shape": [SIZE, 1, 9],
            "repaired_source_nonzero_count": 102,
            "repaired_source_sha256": REPAIRED_SOURCE_SHA256,
        },
        "newton_protocol": {
            "starts": ["zero", "sealed-q011b-coordinate"],
            "maximum_steps": q011b.NEWTON_MAXIMUM_STEPS,
            "line_search_factors": list(q011b.LINE_SEARCH_FACTORS),
        },
        "thresholds": {
            "maximum_waveform_changed_entry_count": (MAXIMUM_WAVEFORM_CHANGED_ENTRY_COUNT),
            "maximum_waveform_component_perturbation": (MAXIMUM_WAVEFORM_COMPONENT_PERTURBATION),
            "maximum_waveform_relative_l2_perturbation": (MAXIMUM_WAVEFORM_RELATIVE_PERTURBATION),
            "maximum_waveform_fourier_leakage": MAXIMUM_WAVEFORM_FOURIER_LEAKAGE,
            "maximum_source_component_perturbation": (MAXIMUM_SOURCE_COMPONENT_PERTURBATION),
            "maximum_source_relative_l2_perturbation": (MAXIMUM_SOURCE_RELATIVE_PERTURBATION),
            "maximum_source_search_ulp_shift": MAXIMUM_SOURCE_ULP_SHIFT,
            "maximum_projected_residual": MAXIMUM_PROJECTED_RESIDUAL,
            "maximum_full_residual": MAXIMUM_FULL_RESIDUAL,
            "maximum_component_residual": MAXIMUM_COMPONENT_RESIDUAL,
            "maximum_two_start_solution_distance": MAXIMUM_TWO_START_DISTANCE,
            "maximum_two_start_relative_distance": (MAXIMUM_TWO_START_RELATIVE_DISTANCE),
            "maximum_repaired_vs_sealed_state_distance": MAXIMUM_SEALED_STATE_DISTANCE,
            "maximum_repaired_vs_sealed_state_relative_distance": (
                MAXIMUM_SEALED_STATE_RELATIVE_DISTANCE
            ),
            "maximum_block_matrix_relative_perturbation": (
                MAXIMUM_BLOCK_MATRIX_RELATIVE_PERTURBATION
            ),
            "maximum_block_spectrum_hausdorff_distance": (
                MAXIMUM_BLOCK_SPECTRUM_HAUSDORFF_DISTANCE
            ),
            "maximum_fixed_leaf_spectral_radius": q011b.SPECTRAL_RADIUS_CEILING,
            "minimum_i_minus_j_singular_value": (q011b.MINIMUM_RESOLVENT_SINGULAR_VALUE),
            "maximum_i_minus_j_condition_number": (q011b.MAXIMUM_RESOLVENT_CONDITION_NUMBER),
        },
    }


def _sealed_q011b_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011b.__file__).resolve().parent
        / "artifacts"
        / "q011b_zero_mean_forced_fixed_point.json"
    )
    runner_path = Path(q011b.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    observed_digests = (
        cycle["input_digest_sha256"],
        cycle["fixed_point_digest_sha256"],
        cycle["spectrum_digest_sha256"],
        cycle["result_digest_sha256"],
    )
    checks = {
        "artifact_sha256_matches": _file_sha256(artifact_path) == Q011B_ARTIFACT_SHA256,
        "runner_sha256_matches": (
            _file_sha256(runner_path) == Q011B_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011B_RUNNER_SHA256
        ),
        "package_source_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "four_digests_match": observed_digests
        == (
            Q011B_INPUT_DIGEST,
            Q011B_FIXED_POINT_DIGEST,
            Q011B_SPECTRUM_DIGEST,
            Q011B_RESULT_DIGEST,
        ),
        "valid_accepted_numerical_outcome_reproduces": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
        ),
        "claim_boundary_remains_numerical": (
            cycle["numerical_consequence"]["registered_fixed_point_is_numerically_resolved"]
            and cycle["numerical_consequence"][
                "registered_fixed_point_is_strictly_stable_on_fixed_leaf"
            ]
            and not cycle["numerical_consequence"][
                "rigorous_existence_or_uniqueness_has_been_proved"
            ]
        ),
        "raw_hashes_reproduce": (
            cycle["source_and_stage_audit"]["waveform_sha256"] == RAW_WAVEFORM_SHA256
            and cycle["source_and_stage_audit"]["source_sha256"] == RAW_SOURCE_SHA256
            and cycle["physical_fourier_audit"]["stripe_state_sha256"] == RAW_STRIPE_STATE_SHA256
        ),
        "artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact) and _strict_json_serializable(artifact)
        ),
    }
    audit = {
        "artifact": {
            "filename": artifact_path.name,
            "sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "input_digest_sha256": observed_digests[0],
            "fixed_point_digest_sha256": observed_digests[1],
            "spectrum_digest_sha256": observed_digests[2],
            "result_digest_sha256": observed_digests[3],
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return q011h.q011e._json_native(audit), artifact


def _sealed_q011h_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011h.__file__).resolve().parent / "artifacts" / "q011h_sparse_chart_equivalence.json"
    )
    runner_path = Path(q011h.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    observed_digests = (
        cycle["input_digest_sha256"],
        cycle["coefficient_digest_sha256"],
        cycle["campaign_digest_sha256"],
        cycle["result_digest_sha256"],
    )
    decision = cycle["decision_consequence"]
    checks = {
        "artifact_sha256_matches": _file_sha256(artifact_path) == Q011H_ARTIFACT_SHA256,
        "runner_sha256_matches": (
            _file_sha256(runner_path) == Q011H_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011H_RUNNER_SHA256
        ),
        "package_source_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "four_digests_match": observed_digests
        == (
            Q011H_INPUT_DIGEST,
            Q011H_COEFFICIENT_DIGEST,
            Q011H_CAMPAIGN_DIGEST,
            Q011H_RESULT_DIGEST,
        ),
        "valid_accepted_outcome_reproduces": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
        ),
        "q011g_and_tt_cross_decisions_remain_sealed": (
            not decision["q011g_rejected_tt_svd_outcome_changed"]
            and not decision["tt_cross_followup_is_authorized"]
            and not decision["forced_ssm_exists_or_is_unique"]
        ),
        "artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact) and _strict_json_serializable(artifact)
        ),
    }
    audit = {
        "artifact": {
            "filename": artifact_path.name,
            "sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "input_digest_sha256": observed_digests[0],
            "coefficient_digest_sha256": observed_digests[1],
            "campaign_digest_sha256": observed_digests[2],
            "result_digest_sha256": observed_digests[3],
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return q011h.q011e._json_native(audit), artifact


def _exact_moment_ledger(source: Array) -> list[list[Fraction]]:
    velocities = np.asarray(D2Q9_VELOCITIES, dtype=np.int64)
    table = np.asarray(source, dtype=np.float64).reshape(SIZE, 9)
    result: list[list[Fraction]] = []
    for row in table:
        moments: list[Fraction] = []
        for component in range(3):
            moment = Fraction(0)
            for value, (cx, cy) in zip(row, velocities, strict=True):
                multiplier = (1, int(cx), int(cy))[component]
                moment += multiplier * _fraction_from_float(value)
            moments.append(moment)
        result.append(moments)
    return result


def _raw_obstruction_audit(q011b_artifact: dict[str, Any]) -> dict[str, Any]:
    raw_waveform = q011b.force_waveform()
    raw_source = q011b.spatial_body_force_source(raw_waveform[:, None])
    raw_source_stripe = raw_source[:, 0, :]
    waveform_sum = _exact_sum(raw_waveform)
    source_ledger = _exact_moment_ledger(raw_source)
    global_source_moments = [
        sum((record[index] for record in source_ledger), Fraction(0)) for index in range(3)
    ]
    stored_cycle = q011b_artifact["cycle"]
    checks = {
        "raw_waveform_and_source_hashes_match": (
            q011b._array_sha256(raw_waveform) == RAW_WAVEFORM_SHA256
            and q011b._array_sha256(raw_source_stripe) == RAW_SOURCE_SHA256
            and stored_cycle["source_and_stage_audit"]["waveform_sha256"] == RAW_WAVEFORM_SHA256
            and stored_cycle["source_and_stage_audit"]["source_sha256"] == RAW_SOURCE_SHA256
        ),
        "raw_exact_waveform_sum_reproduces": waveform_sum == RAW_EXACT_WAVEFORM_SUM,
        "raw_exact_global_momentum_increment_is_nonzero": (
            global_source_moments[0] == 0
            and global_source_moments[1] != 0
            and global_source_moments[2] == 0
        ),
        "q011b_did_not_claim_rigorous_existence": not stored_cycle["numerical_consequence"][
            "rigorous_existence_or_uniqueness_has_been_proved"
        ],
    }
    return q011h.q011e._json_native(
        {
            "raw_waveform_sha256": q011b._array_sha256(raw_waveform),
            "raw_source_sha256": q011b._array_sha256(raw_source_stripe),
            "raw_exact_waveform_sum": _fraction_record(waveform_sum),
            "raw_exact_global_source_moments": _fraction_vector_record(global_source_moments),
            "raw_exact_fixed_point_is_compatible_with_global_momentum_ledger": False,
            "q011b_numerical_outcome_is_regraded": False,
            "checks": checks,
            "passed": all(checks.values()),
        }
    )


def _shift_ulps(value: float, shift: int) -> float:
    result = float(value)
    if shift == 0:
        return result
    target = np.inf if shift > 0 else -np.inf
    for _ in range(abs(shift)):
        result = float(np.nextafter(result, target))
    return result


def _signed_shift_order(maximum: int) -> list[int]:
    return [0, *(shift for index in range(1, maximum + 1) for shift in (index, -index))]


def _waveform_repair_audit() -> tuple[Array, dict[str, Any]]:
    raw = q011b.force_waveform()
    symmetrized = np.empty_like(raw)
    symmetrized[0] = raw[0]
    midpoint_records: list[dict[str, Any]] = []
    for index in range(1, 9):
        exact_midpoint = (
            _fraction_from_float(raw[index]) + _fraction_from_float(raw[SIZE - index])
        ) / 2
        rounded = float(exact_midpoint)
        symmetrized[index] = rounded
        symmetrized[SIZE - index] = rounded
        midpoint_records.append(
            {
                "pair": [index, SIZE - index],
                "exact_midpoint": _fraction_record(exact_midpoint),
                "rounded_hex": rounded.hex(),
                "rounding_error": _fraction_record(_fraction_from_float(rounded) - exact_midpoint),
            }
        )
    symmetrized_sum = _exact_sum(symmetrized)
    candidates_checked = 0
    eligible: list[tuple[int, int, Array]] = []
    shifts = _signed_shift_order(WAVEFORM_SEARCH_MAXIMUM_ULPS)
    for pair_index in range(1, 9):
        for shift in shifts:
            candidate = symmetrized.copy()
            shifted = _shift_ulps(float(symmetrized[pair_index]), shift)
            candidate[pair_index] = shifted
            candidate[SIZE - pair_index] = shifted
            candidates_checked += 1
            if _exact_sum(candidate) == 0:
                eligible.append((pair_index, shift, candidate))
    eligible.sort(key=lambda record: (abs(record[1]), record[0], record[1]))
    if not eligible:
        repaired = symmetrized.copy()
        selected_pair = -1
        selected_shift = 0
    else:
        selected_pair, selected_shift, repaired = eligible[0]
    difference = repaired - raw
    transform = np.fft.fft(repaired)
    outside = np.ones(SIZE, dtype=bool)
    outside[[1, SIZE - 1]] = False
    leakage = float(
        np.linalg.norm(transform[outside])
        / max(float(np.linalg.norm(transform)), np.finfo(float).tiny)
    )
    changed_count = int(np.count_nonzero(repaired != raw))
    maximum_component = float(np.max(np.abs(difference)))
    relative_l2 = float(np.linalg.norm(difference) / np.linalg.norm(raw))
    checks = {
        "raw_and_symmetrized_exact_sums_reproduce": (
            _exact_sum(raw) == RAW_EXACT_WAVEFORM_SUM
            and symmetrized_sum == SYMMETRIZED_EXACT_WAVEFORM_SUM
        ),
        "all_registered_candidates_are_checked": (
            candidates_checked == 8 * (1 + 2 * WAVEFORM_SEARCH_MAXIMUM_ULPS)
        ),
        "registered_unique_minimum_candidate_is_selected": (
            len(eligible) >= 1
            and selected_pair == REGISTERED_WAVEFORM_PAIR
            and selected_shift == REGISTERED_WAVEFORM_ULP_SHIFT
            and sum(abs(record[1]) == abs(selected_shift) for record in eligible) == 2
        ),
        "repaired_hash_exact_sum_and_symmetry_reproduce": (
            q011b._array_sha256(repaired) == REPAIRED_WAVEFORM_SHA256
            and _exact_sum(repaired) == 0
            and repaired[0] == raw[0]
            and all(repaired[index] == repaired[SIZE - index] for index in range(1, 9))
        ),
        "registered_perturbation_bounds_hold": (
            changed_count <= MAXIMUM_WAVEFORM_CHANGED_ENTRY_COUNT
            and maximum_component <= MAXIMUM_WAVEFORM_COMPONENT_PERTURBATION
            and relative_l2 <= MAXIMUM_WAVEFORM_RELATIVE_PERTURBATION
        ),
        "registered_fourier_support_and_phase_hold": (
            leakage <= MAXIMUM_WAVEFORM_FOURIER_LEAKAGE
            and transform[0] == 0.0
            and transform[1].imag == 0.0
        ),
        "all_values_are_finite": bool(
            np.all(np.isfinite(symmetrized))
            and np.all(np.isfinite(repaired))
            and np.all(np.isfinite(transform))
        ),
    }
    audit = {
        "raw_waveform_sha256": q011b._array_sha256(raw),
        "symmetrized_waveform_sha256": q011b._array_sha256(symmetrized),
        "repaired_waveform_sha256": q011b._array_sha256(repaired),
        "raw_exact_sum": _fraction_record(_exact_sum(raw)),
        "symmetrized_exact_sum": _fraction_record(symmetrized_sum),
        "repaired_exact_sum": _fraction_record(_exact_sum(repaired)),
        "midpoint_records": midpoint_records,
        "search_maximum_ulps": WAVEFORM_SEARCH_MAXIMUM_ULPS,
        "candidate_count": candidates_checked,
        "eligible_candidates": [
            {"pair": [index, SIZE - index], "ulp_shift": shift} for index, shift, _ in eligible
        ],
        "selected_pair": [selected_pair, SIZE - selected_pair],
        "selected_ulp_shift": selected_shift,
        "changed_entry_count": changed_count,
        "maximum_component_perturbation": maximum_component,
        "relative_l2_perturbation": relative_l2,
        "fft_relative_leakage_outside_plus_minus_one": leakage,
        "fft_zero_mode": {
            "real": float(transform[0].real),
            "imag": float(transform[0].imag),
        },
        "fft_first_mode": {
            "real": float(transform[1].real),
            "imag": float(transform[1].imag),
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return np.asarray(repaired, dtype=np.float64), q011h.q011e._json_native(audit)


def _source_repair_audit(waveform: Array) -> tuple[Array, dict[str, Any]]:
    velocities = np.asarray(D2Q9_VELOCITIES, dtype=np.int64)
    source = np.zeros((SIZE, 1, 9), dtype=np.float64)
    search_records: list[dict[str, Any]] = []
    for y_index, value in enumerate(waveform):
        exact_force = _fraction_from_float(value)
        initial_diagonal = float(exact_force / 12)
        chosen: tuple[int, float, float] | None = None
        candidates_checked = 0
        for shift in _signed_shift_order(SOURCE_SEARCH_MAXIMUM_ULPS):
            diagonal = _shift_ulps(initial_diagonal, shift)
            exact_axis = exact_force / 2 - 2 * _fraction_from_float(diagonal)
            axis = float(exact_axis)
            candidates_checked += 1
            if _fraction_from_float(axis) == exact_axis:
                chosen = (shift, diagonal, axis)
                break
        if chosen is None:
            shift, diagonal, axis = 0, initial_diagonal, 0.0
        else:
            shift, diagonal, axis = chosen
        for population, (cx, cy) in enumerate(velocities):
            if cx == 0:
                entry = 0.0
            elif cy == 0:
                entry = float(cx) * axis
            else:
                entry = float(cx) * diagonal
            source[y_index, 0, population] = entry
        search_records.append(
            {
                "site_index": y_index,
                "force_hex": float(value).hex(),
                "initial_diagonal_hex": initial_diagonal.hex(),
                "selected_ulp_shift": shift,
                "diagonal_hex": diagonal.hex(),
                "axis_hex": axis.hex(),
                "candidate_count": candidates_checked,
                "exact_axis_identity": _fraction_record(
                    _fraction_from_float(axis)
                    - (exact_force / 2 - 2 * _fraction_from_float(diagonal))
                ),
            }
        )
    ledger = _exact_moment_ledger(source)
    global_moments = [sum((record[index] for record in ledger), Fraction(0)) for index in range(3)]
    raw_source = q011b.spatial_body_force_source(q011b.force_waveform()[:, None])
    difference = source - raw_source
    maximum_component = float(np.max(np.abs(difference)))
    relative_l2 = float(np.linalg.norm(difference) / np.linalg.norm(raw_source))
    maximum_shift = max(abs(record["selected_ulp_shift"]) for record in search_records)
    local_identities = all(
        record[0] == 0 and record[1] == _fraction_from_float(waveform[index]) and record[2] == 0
        for index, record in enumerate(ledger)
    )
    checks = {
        "source_shape_count_and_hash_reproduce": (
            source.shape == (SIZE, 1, 9)
            and int(np.count_nonzero(source)) == 102
            and q011b._array_sha256(source) == REPAIRED_SOURCE_SHA256
        ),
        "all_site_searches_complete_within_registered_ulps": (
            len(search_records) == SIZE
            and maximum_shift <= MAXIMUM_SOURCE_ULP_SHIFT
            and all(record["candidate_count"] <= 3 for record in search_records)
        ),
        "all_local_exact_moment_identities_hold": local_identities,
        "global_exact_moment_ledger_is_zero": global_moments
        == [Fraction(0), Fraction(0), Fraction(0)],
        "source_perturbation_is_within_registered_bounds": (
            maximum_component <= MAXIMUM_SOURCE_COMPONENT_PERTURBATION
            and relative_l2 <= MAXIMUM_SOURCE_RELATIVE_PERTURBATION
        ),
        "all_source_values_are_finite": bool(np.all(np.isfinite(source))),
    }
    audit = {
        "source_shape": list(source.shape),
        "source_nonzero_count": int(np.count_nonzero(source)),
        "source_sha256": q011b._array_sha256(source),
        "search_records": search_records,
        "maximum_selected_ulp_shift": maximum_shift,
        "local_exact_moment_ledger": [_fraction_vector_record(record) for record in ledger],
        "global_exact_moment_ledger": _fraction_vector_record(global_moments),
        "raw_source_sha256": q011b._array_sha256(raw_source),
        "maximum_component_perturbation_vs_raw": maximum_component,
        "relative_l2_perturbation_vs_raw": relative_l2,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return source, q011h.q011e._json_native(audit)


def repaired_stripe_step(state: npt.ArrayLike, source: npt.ArrayLike) -> Array:
    populations = np.asarray(state, dtype=np.float64)
    source_table = np.asarray(source, dtype=np.float64)
    if populations.shape != (SIZE, 1, 9) or source_table.shape != (SIZE, 1, 9):
        raise ValueError("Q011i stripe state and source must have shape (17, 1, 9)")
    post_source = collide_bgk(populations, q011b.OMEGA) + source_table
    streamed = stream_periodic(post_source)
    return conservative_checkerboard_filter(streamed, q011b.ETA)


def _residual_metrics(
    state: Array,
    source: Array,
    basis: Array,
) -> tuple[Array, Array, dict[str, float]]:
    residual = (repaired_stripe_step(state, source) - state).ravel()
    projected = basis.T @ residual
    return (
        residual,
        projected,
        {
            "projected_l2": float(np.linalg.norm(projected)),
            "full_l2": float(np.linalg.norm(residual)),
            "maximum_component": float(np.max(np.abs(residual))),
        },
    )


def _newton_solve(
    start_name: str,
    initial_coordinate: Array,
    rest: Array,
    basis: Array,
    source: Array,
) -> tuple[Array, Array, dict[str, Any]]:
    coordinate = np.asarray(initial_coordinate, dtype=np.float64).copy()
    trace: list[dict[str, Any]] = []
    status = "maximum_steps_reached"
    for iteration in range(q011b.NEWTON_MAXIMUM_STEPS + 1):
        state = rest + (basis @ coordinate).reshape(SIZE, 1, 9)
        residual, projected, metrics = _residual_metrics(state, source, basis)
        record: dict[str, Any] = {
            "iteration": iteration,
            **metrics,
            "state_minimum_population": float(np.min(state)),
            "state_minimum_density": float(np.min(macroscopic(state)[0])),
        }
        if not (
            np.all(np.isfinite(coordinate))
            and np.all(np.isfinite(residual))
            and np.all(np.isfinite(projected))
        ):
            record["decision"] = "nonfinite_failure"
            trace.append(record)
            status = "nonfinite_failure"
            break
        if metrics["projected_l2"] <= MAXIMUM_PROJECTED_RESIDUAL:
            record["decision"] = "projected_tolerance_reached"
            trace.append(record)
            status = "projected_tolerance_reached"
            break
        if iteration == q011b.NEWTON_MAXIMUM_STEPS:
            record["decision"] = "maximum_steps_reached"
            trace.append(record)
            break
        jacobian = q011b.RectangularFilteredBGKJacobian.at_state(
            state,
            q011b.OMEGA,
            q011b.ETA,
        )
        reduced_derivative = basis.T @ (jacobian.matmat(basis) - basis)
        record["reduced_jacobian_condition_number"] = float(np.linalg.cond(reduced_derivative))
        try:
            newton_step = linalg.solve(
                reduced_derivative,
                -projected,
                assume_a="gen",
                check_finite=True,
            )
        except linalg.LinAlgError:
            record["decision"] = "linear_solve_failure"
            trace.append(record)
            status = "linear_solve_failure"
            break
        record["newton_step_l2"] = float(np.linalg.norm(newton_step))
        accepted_factor: float | None = None
        trial_records: list[dict[str, float]] = []
        for factor in q011b.LINE_SEARCH_FACTORS:
            trial_coordinate = coordinate + factor * newton_step
            trial_state = rest + (basis @ trial_coordinate).reshape(SIZE, 1, 9)
            _, trial_projected, _ = _residual_metrics(trial_state, source, basis)
            trial_norm = float(np.linalg.norm(trial_projected))
            trial_records.append({"factor": factor, "projected_l2": trial_norm})
            if np.isfinite(trial_norm) and trial_norm < metrics["projected_l2"]:
                coordinate = trial_coordinate
                accepted_factor = factor
                break
        record["line_search_trials"] = trial_records
        record["accepted_factor"] = accepted_factor
        if accepted_factor is None:
            record["decision"] = "line_search_failure"
            trace.append(record)
            status = "line_search_failure"
            break
        record["decision"] = "accepted_step"
        trace.append(record)
    terminal_state = rest + (basis @ coordinate).reshape(SIZE, 1, 9)
    terminal_residual, _, terminal_metrics = _residual_metrics(
        terminal_state,
        source,
        basis,
    )
    checks = {
        "terminal_values_are_finite": bool(
            np.all(np.isfinite(coordinate))
            and np.all(np.isfinite(terminal_state))
            and np.all(np.isfinite(terminal_residual))
        ),
        "projected_residual_within_tolerance": (
            terminal_metrics["projected_l2"] <= MAXIMUM_PROJECTED_RESIDUAL
        ),
        "full_residual_within_tolerance": (terminal_metrics["full_l2"] <= MAXIMUM_FULL_RESIDUAL),
        "component_residual_within_tolerance": (
            terminal_metrics["maximum_component"] <= MAXIMUM_COMPONENT_RESIDUAL
        ),
    }
    record = {
        "start_name": start_name,
        "status": status,
        "attempted_newton_steps": sum(item["decision"] == "accepted_step" for item in trace),
        "trace": trace,
        "terminal_coordinate_sha256": q011b._array_sha256(coordinate),
        "terminal_state_sha256": q011b._array_sha256(terminal_state),
        "terminal_metrics": terminal_metrics,
        "minimum_population": float(np.min(terminal_state)),
        "minimum_density": float(np.min(macroscopic(terminal_state)[0])),
        "checks": checks,
        "converged": all(checks.values()),
    }
    return coordinate, terminal_state, q011h.q011e._json_native(record)


def _fixed_point_bridge_audit(
    source: Array,
    q011b_artifact: dict[str, Any],
) -> tuple[Array, Array, Array, dict[str, Any]]:
    conservation, basis, basis_audit = q011b._fixed_leaf_basis()
    rest = uniform_equilibrium(SIZE, 1, np.zeros(3))
    sealed_state = np.asarray(
        q011b_artifact["cycle"]["physical_fourier_audit"]["stripe_state"],
        dtype=np.float64,
    ).reshape(SIZE, 1, 9)
    sealed_coordinate = np.asarray(
        basis.T @ (sealed_state - rest).ravel(),
        dtype=np.float64,
    )
    starts = {
        "zero": np.zeros(FIXED_LEAF_DIMENSION, dtype=np.float64),
        "sealed-q011b-coordinate": sealed_coordinate,
    }
    coordinates: dict[str, Array] = {}
    states: dict[str, Array] = {}
    records: dict[str, dict[str, Any]] = {}
    replay_records: dict[str, dict[str, Any]] = {}
    for name, start in starts.items():
        coordinate, state, record = _newton_solve(name, start, rest, basis, source)
        replay_coordinate, replay_state, replay = _newton_solve(
            name,
            start,
            rest,
            basis,
            source,
        )
        coordinates[name] = coordinate
        states[name] = state
        records[name] = record
        replay_records[name] = {
            "terminal_coordinate_sha256": q011b._array_sha256(replay_coordinate),
            "terminal_state_sha256": q011b._array_sha256(replay_state),
            "coordinate_bitwise_matches": np.array_equal(coordinate, replay_coordinate),
            "state_bitwise_matches": np.array_equal(state, replay_state),
            "trace_exact_json_matches": record["trace"] == replay["trace"],
            "terminal_metrics_exact_json_matches": (
                record["terminal_metrics"] == replay["terminal_metrics"]
            ),
        }
    zero_state = states["zero"]
    sealed_start_state = states["sealed-q011b-coordinate"]
    two_start_distance = float(np.linalg.norm(zero_state - sealed_start_state))
    departure_scale = max(
        float(np.linalg.norm(zero_state - rest)),
        float(np.linalg.norm(sealed_start_state - rest)),
        np.finfo(float).tiny,
    )
    two_start_relative = two_start_distance / departure_scale
    sealed_distance = float(np.linalg.norm(zero_state - sealed_state))
    sealed_departure = max(
        float(np.linalg.norm(sealed_state - rest)),
        np.finfo(float).tiny,
    )
    sealed_relative = sealed_distance / sealed_departure
    physical_full_state, physical_audit = q011b._physical_fourier_audit(zero_state, rest)
    deterministic = all(
        record["coordinate_bitwise_matches"]
        and record["state_bitwise_matches"]
        and record["trace_exact_json_matches"]
        and record["terminal_metrics_exact_json_matches"]
        for record in replay_records.values()
    )
    checks = {
        "fixed_leaf_basis_reproduces": basis_audit["passed"],
        "two_registered_starts_converge": (
            len(records) == 2 and all(record["converged"] for record in records.values())
        ),
        "repeat_runs_are_bitwise_and_trace_deterministic": deterministic,
        "two_start_solution_bridge_is_within_tolerance": (
            two_start_distance <= MAXIMUM_TWO_START_DISTANCE
            and two_start_relative <= MAXIMUM_TWO_START_RELATIVE_DISTANCE
        ),
        "sealed_q011b_state_bridge_is_within_tolerance": (
            sealed_distance <= MAXIMUM_SEALED_STATE_DISTANCE
            and sealed_relative <= MAXIMUM_SEALED_STATE_RELATIVE_DISTANCE
        ),
        "repaired_state_is_positive_and_physical": (
            float(np.min(zero_state)) > 0.0
            and float(np.min(macroscopic(zero_state)[0])) > 0.0
            and physical_audit["passed"]
        ),
        "all_values_are_finite": bool(
            _all_numeric_values_finite(records)
            and _all_numeric_values_finite(replay_records)
            and np.all(np.isfinite(zero_state))
            and np.all(np.isfinite(physical_full_state))
        ),
    }
    audit = {
        "fixed_leaf_basis_audit": basis_audit,
        "sealed_state_sha256": q011b._array_sha256(sealed_state),
        "sealed_coordinate_sha256": q011b._array_sha256(sealed_coordinate),
        "primary_runs": records,
        "determinism_replays": replay_records,
        "two_start_solution_l2_distance": two_start_distance,
        "two_start_solution_relative_distance": two_start_relative,
        "repaired_vs_sealed_state_l2_distance": sealed_distance,
        "sealed_state_departure_from_rest": sealed_departure,
        "repaired_vs_sealed_state_relative_distance": sealed_relative,
        "representative_repaired_state_sha256": q011b._array_sha256(zero_state),
        "physical_fourier_audit": physical_audit,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        zero_state,
        physical_full_state,
        conservation,
        q011h.q011e._json_native(audit),
    )


def _complex_values(records: list[dict[str, float]]) -> ComplexArray:
    return np.asarray(
        [complex(record["real"], record["imag"]) for record in records],
        dtype=np.complex128,
    )


def _spectrum_bridge_audit(
    repaired_state: Array,
    repaired_full_state: Array,
    conservation: Array,
    q011b_artifact: dict[str, Any],
) -> dict[str, Any]:
    _, basis, _ = q011b._fixed_leaf_basis()
    fresh = q011b._spectrum_audit(
        repaired_state,
        repaired_full_state,
        conservation,
        basis,
    )
    stored = q011b_artifact["cycle"]["spectrum_audit"]
    sealed_state = np.asarray(
        q011b_artifact["cycle"]["physical_fourier_audit"]["stripe_state"],
        dtype=np.float64,
    ).reshape(SIZE, 1, 9)
    records: list[dict[str, Any]] = []
    maximum_matrix_perturbation = 0.0
    maximum_spectrum_hausdorff = 0.0
    for wave_index in range(SIZE):
        kx = 2.0 * np.pi * wave_index / SIZE
        repaired_block = q011b._block_matrix(repaired_state, kx)
        sealed_block = q011b._block_matrix(sealed_state, kx)
        matrix_perturbation = q011b._relative_error(repaired_block, sealed_block)
        fresh_values = _complex_values(fresh["block_records"][wave_index]["fixed_leaf_eigenvalues"])
        stored_values = _complex_values(
            stored["block_records"][wave_index]["fixed_leaf_eigenvalues"]
        )
        spectrum_hausdorff = q011b._spectrum_hausdorff(fresh_values, stored_values)
        maximum_matrix_perturbation = max(
            maximum_matrix_perturbation,
            matrix_perturbation,
        )
        maximum_spectrum_hausdorff = max(
            maximum_spectrum_hausdorff,
            spectrum_hausdorff,
        )
        records.append(
            {
                "wave_index": wave_index,
                "block_matrix_relative_perturbation": matrix_perturbation,
                "spectrum_absolute_hausdorff_distance": spectrum_hausdorff,
                "fresh_fixed_leaf_eigenvalue_count": int(fresh_values.size),
                "stored_fixed_leaf_eigenvalue_count": int(stored_values.size),
            }
        )
    checks = {
        "fresh_spectrum_protocol_passes": (
            fresh["passed"]
            and fresh["hypothesis_passed"]
            and all(fresh["checks"].values())
            and all(fresh["hypothesis_checks"].values())
        ),
        "registered_block_count_and_fixed_leaf_count_reproduce": (
            len(records) == SIZE and fresh["fixed_leaf_eigenvalue_count"] == 2598
        ),
        "block_matrix_perturbations_are_within_tolerance": (
            maximum_matrix_perturbation <= MAXIMUM_BLOCK_MATRIX_RELATIVE_PERTURBATION
        ),
        "block_spectrum_perturbations_are_within_tolerance": (
            maximum_spectrum_hausdorff <= MAXIMUM_BLOCK_SPECTRUM_HAUSDORFF_DISTANCE
        ),
        "stability_and_resolvent_gates_hold": (
            fresh["maximum_fixed_leaf_eigenvalue_modulus"] <= q011b.SPECTRAL_RADIUS_CEILING
            and fresh["minimum_i_minus_j_singular_value"] >= q011b.MINIMUM_RESOLVENT_SINGULAR_VALUE
            and fresh["maximum_i_minus_j_condition_number"]
            <= q011b.MAXIMUM_RESOLVENT_CONDITION_NUMBER
        ),
        "all_values_are_finite": bool(
            _all_numeric_values_finite(fresh) and _all_numeric_values_finite(records)
        ),
    }
    return q011h.q011e._json_native(
        {
            "fresh_spectrum_audit": fresh,
            "block_bridge_records": records,
            "maximum_block_matrix_relative_perturbation": maximum_matrix_perturbation,
            "maximum_block_spectrum_absolute_hausdorff_distance": (maximum_spectrum_hausdorff),
            "checks": checks,
            "passed": all(checks.values()),
        }
    )


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "repair_digest_sha256": cycle["repair_digest_sha256"],
        "fixed_point_digest_sha256": cycle["fixed_point_digest_sha256"],
        "spectrum_digest_sha256": cycle["spectrum_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_exact_zero_mean_repair_audit() -> dict[str, Any]:
    registered_parameters = _registered_parameters()
    sealed_q011b, q011b_artifact = _sealed_q011b_artifact_audit()
    sealed_q011h, _ = _sealed_q011h_artifact_audit()
    raw_obstruction = _raw_obstruction_audit(q011b_artifact)
    repaired_waveform, waveform_audit = _waveform_repair_audit()
    repaired_source, source_audit = _source_repair_audit(repaired_waveform)
    repaired_state, repaired_full_state, conservation, fixed_point_audit = (
        _fixed_point_bridge_audit(repaired_source, q011b_artifact)
    )
    spectrum_audit = _spectrum_bridge_audit(
        repaired_state,
        repaired_full_state,
        conservation,
        q011b_artifact,
    )
    runner = _runner_source_metadata()

    input_sections = q011h.q011e._json_native(
        {
            "registered_parameters": registered_parameters,
            "sealed_q011b_artifact_audit": sealed_q011b,
            "sealed_q011h_artifact_audit": sealed_q011h,
            "raw_exact_obstruction_audit": raw_obstruction,
        }
    )
    repair_sections = q011h.q011e._json_native(
        {
            "waveform_repair_audit": waveform_audit,
            "source_repair_audit": source_audit,
        }
    )
    fixed_point_sections = q011h.q011e._json_native(
        {"repaired_fixed_point_bridge_audit": fixed_point_audit}
    )
    spectrum_sections = q011h.q011e._json_native({"repaired_spectrum_bridge_audit": spectrum_audit})
    input_digest = q011b._canonical_json_sha256(input_sections)
    repair_digest = q011b._canonical_json_sha256(repair_sections)
    fixed_point_digest = q011b._canonical_json_sha256(fixed_point_sections)
    spectrum_digest = q011b._canonical_json_sha256(spectrum_sections)
    strict_payload = {
        **input_sections,
        **repair_sections,
        **fixed_point_sections,
        **spectrum_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(strict_payload) and _strict_json_serializable(strict_payload)
    )
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and repair_digest == q011b._canonical_json_sha256(repair_sections)
        and fixed_point_digest == q011b._canonical_json_sha256(fixed_point_sections)
        and spectrum_digest == q011b._canonical_json_sha256(spectrum_sections)
    )
    runner_reproduces = bool(
        runner["filename"] == Path(__file__).name
        and runner["sha256"] == _file_sha256(Path(__file__).resolve())
    )
    numerical_protocol_finite = bool(
        fixed_point_audit["checks"]["all_values_are_finite"]
        and spectrum_audit["checks"]["all_values_are_finite"]
    )
    validity_gates = {
        "q011b_q011h_and_prior_outcomes_are_sealed": {
            "passed": bool(sealed_q011b["passed"] and sealed_q011h["passed"]),
            "threshold": (
                "Q011b and Q011h artifact, runner, package source, digests, "
                "outcomes and numerical-only claim boundaries reproduce"
            ),
            "value": {
                "q011b_checks": sealed_q011b["checks"],
                "q011h_checks": sealed_q011h["checks"],
            },
        },
        "raw_exact_momentum_obstruction_reproduces": {
            "passed": raw_obstruction["passed"],
            "threshold": (
                "raw hashes and exact dyadic sum -71/2^78 reproduce with "
                "nonzero global x-momentum source and no prior rigorous claim"
            ),
            "value": raw_obstruction["checks"],
        },
        "waveform_repair_search_is_complete": {
            "passed": waveform_audit["passed"],
            "threshold": (
                "all registered pair/ULP candidates are checked and the "
                "registered exact-zero-sum symmetric waveform is reproduced"
            ),
            "value": waveform_audit["checks"],
        },
        "source_repair_and_exact_ledgers_are_complete": {
            "passed": source_audit["passed"],
            "threshold": (
                "all 17 source searches, shape, count, hash and exact local/global "
                "mass-momentum ledgers reproduce"
            ),
            "value": source_audit["checks"],
        },
        "repaired_newton_and_spectrum_protocols_are_complete": {
            "passed": numerical_protocol_finite,
            "threshold": (
                "two registered Newton starts and all 17 fixed-leaf spectrum "
                "blocks complete with finite records"
            ),
            "value": {
                "fixed_point_finiteness": fixed_point_audit["checks"]["all_values_are_finite"],
                "spectrum_finiteness": spectrum_audit["checks"]["all_values_are_finite"],
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce and runner_reproduces),
            "threshold": (
                "finite strict JSON, four section digests and newline-normalized "
                "runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_reproduces": runner_reproduces,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    exact_compatibility_passed = bool(
        raw_obstruction["passed"]
        and waveform_audit["checks"]["repaired_hash_exact_sum_and_symmetry_reproduce"]
        and source_audit["checks"]["all_local_exact_moment_identities_hold"]
        and source_audit["checks"]["global_exact_moment_ledger_is_zero"]
    )
    perturbation_passed = bool(
        waveform_audit["checks"]["registered_perturbation_bounds_hold"]
        and waveform_audit["checks"]["registered_fourier_support_and_phase_hold"]
        and source_audit["checks"]["source_perturbation_is_within_registered_bounds"]
    )
    fixed_point_passed = fixed_point_audit["passed"]
    spectrum_passed = spectrum_audit["passed"]
    hypothesis_gates = {
        "raw_obstruction_is_removed_by_exact_local_global_ledgers": {
            "passed": bool(validity_passed and exact_compatibility_passed),
            "threshold": (
                "raw exact momentum increment is nonzero while repaired waveform "
                "and all repaired local/global source ledgers are exactly zero-compatible"
            ),
            "value": {
                "raw_checks": raw_obstruction["checks"],
                "waveform_exact_checks": waveform_audit["checks"],
                "source_exact_checks": source_audit["checks"],
            },
        },
        "waveform_and_source_perturbations_are_small": {
            "passed": bool(validity_passed and perturbation_passed),
            "threshold": (
                "registered component, relative-l2, reflection and Fourier "
                "perturbation bounds all pass"
            ),
            "value": {
                "waveform_maximum_component": waveform_audit["maximum_component_perturbation"],
                "waveform_relative_l2": waveform_audit["relative_l2_perturbation"],
                "source_maximum_component": source_audit["maximum_component_perturbation_vs_raw"],
                "source_relative_l2": source_audit["relative_l2_perturbation_vs_raw"],
            },
        },
        "repaired_numerical_fixed_point_preserves_q011b_baseline": {
            "passed": bool(validity_passed and fixed_point_passed),
            "threshold": (
                "two-start Newton, sealed-state bridge, positivity and Q011b "
                "physical checks all pass registered thresholds"
            ),
            "value": fixed_point_audit["checks"],
        },
        "repaired_linear_spectrum_preserves_q011b_baseline": {
            "passed": bool(validity_passed and spectrum_passed),
            "threshold": (
                "all block perturbation, spectrum Hausdorff, stability, "
                "resolvent, conjugacy, Schur and block-action gates pass"
            ),
            "value": spectrum_audit["checks"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011i exact zero-mean repair audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the exact-dyadic zero-mean repair preserves the numerical forced "
            "fixed-point and linear-spectrum baseline"
        )
    else:
        outcome = "rejected"
        classification = (
            "the exact-dyadic zero-mean repair does not preserve the registered numerical baseline"
        )

    cycle: dict[str, Any] = q011h.q011e._json_native(
        {
            "question": (
                "Can a uniquely registered reflection-symmetric exact-dyadic "
                "zero-mean waveform and exact-moment source remove the raw "
                "momentum obstruction while preserving the Q011b numerical "
                "fixed-point and linear-spectrum baseline?"
            ),
            **strict_payload,
            "input_digest_sha256": input_digest,
            "repair_digest_sha256": repair_digest,
            "fixed_point_digest_sha256": fixed_point_digest,
            "spectrum_digest_sha256": spectrum_digest,
            "validity_gates": validity_gates,
            "hypothesis_gates": hypothesis_gates,
            "study_validity": "passed" if validity_passed else "failed",
            "hypothesis_outcome": outcome,
            "scientific_classification": classification,
        }
    )
    result_digest = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["decision_consequence"] = {
        "raw_q011b_exact_dyadic_source_is_fixed_point_compatible": False,
        "repaired_source_is_the_target_for_rigorous_fixed_point_work": bool(
            validity_passed and hypotheses_passed
        ),
        "interval_fixed_point_proof_is_authorized": bool(validity_passed and hypotheses_passed),
        "q011b_numerical_accepted_outcome_changed": False,
        "q011h_sparse_equivalence_outcome_changed": False,
        "q011e_through_q011h_coefficients_transfer_to_repaired_map": False,
        "forced_ssm_exists_or_is_unique": False,
        "rigorous_linear_spectrum_is_certified": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This audit defines one repaired 17x17 periodic source at the registered "
        "amplitude, proves exact dyadic waveform and source moment ledgers, and "
        "checks a binary64 numerical fixed-point and linear-spectrum bridge. It "
        "does not change Q011b--Q011h raw-map outcomes or transfer their chart "
        "coefficients, residual order or shadowing to the repaired map. It does "
        "not prove an interval fixed point, rigorous spectrum, external "
        "nonresonance, a forced SSM, normal attraction, a basin, another grid, "
        "force or wall, or D3Q27."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011b_raw_numerical_fixed_point_acceptance_changed": False,
        "q011h_sparse_chart_equivalence_acceptance_changed": False,
        "q011g_tt_svd_rejection_changed": False,
        "q011f1_shadowing_reissue_acceptance_changed": False,
        "q011f_shadowing_window_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister exact affine fixed-leaf coordinates and an interval Newton "
        "or Krawczyk existence and local-uniqueness proof for the repaired fixed point."
        if outcome == "accepted"
        else (
            "Localize the first valid waveform, source, fixed-point or spectrum "
            "compatibility failure without changing the registered repair."
            if outcome == "rejected"
            else (
                "Localize the first failed sealing, exact-ledger, repair-search, "
                "numerical-protocol or serialization validity gate."
            )
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011i cycle failed strict serialization or digest")
    return cycle


def run_q011i_study() -> dict[str, Any]:
    cycle = run_exact_zero_mean_repair_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "exact-dyadic zero-mean forcing compatibility repair with "
                "numerical fixed-point and linear-spectrum bridge"
            ),
            "grid": [SIZE, SIZE],
            "omega": q011b.OMEGA,
            "eta": q011b.ETA,
            "force_amplitude": q011b.AMPLITUDE,
            "fixed_conservation_leaf": True,
            "raw_and_repaired_maps_are_distinct": True,
            "claim": ("exact source compatibility and finite binary64 numerical bridge only"),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011i_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
