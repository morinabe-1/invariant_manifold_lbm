"""Sealed Q007k rational quadratic-jet bridge.

NumPy supplies only registered coefficient centers and inverse candidates.
Every forcing enclosure, homological operator, Krawczyk inclusion, conservation
identity, and acceptance gate is evaluated with exact ``Fraction`` endpoints.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path
from typing import Any

import numpy as np

import research.q007j_eigencoordinate_bridge as q007j
from ttim_lbm.checkerboard_filter import filtered_fourier_symbol
from ttim_lbm.full2d_chart import (
    MODE_ORDER,
    WAVE_ORDER,
    _build_complex_modes,
    _complex_coefficients,
)
from ttim_lbm.nonresonance import wave_vector_from_index
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    INTERVAL_DECIMAL_DIGITS,
    MAXIMUM_PI_TRIGONOMETRIC_WIDTH,
    MAXIMUM_SYMBOL_ENTRY_WIDTH,
    VELOCITIES,
    WEIGHTS,
    ComplexIntervalMatrix,
    ComplexRationalInterval,
    RationalInterval,
    WaveIndex,
    _all_numeric_values_finite,
    _complex_point,
    _complex_rectangle_absolute_upper,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _identity_matrix,
    _matrix_from_numpy,
    _matrix_infinity_norm_upper,
    _proof_digest,
    _strict_json_serializable,
    machin_pi_interval,
    rational_collision_symbol,
    rational_fourier_symbol,
    trigonometric_intervals,
)

Q006I_ARTIFACT = "q006i_full2d_quadratic.json"
Q007J_ARTIFACT = "q007j_eigencoordinate_bridge.json"

REGISTERED_INPUT_SHA256 = {
    "q006i": "347d5349af349618333df17733ba372c8ca6f5ee02784a9e788898acefb5db89",
    "q007j": "feae846b81dc0991aa2c9babbd38ee72eb9ae493526655435cf0bf5951c7ec44",
}
REGISTERED_Q007J_RUNNER_SHA256 = (
    "7ef97e55ffff46244fee98d8017db1637a0e6c73ba3f1caf5c7dad77b7a26b57"
)
REGISTERED_COEFFICIENT_HASHES = q007j.REGISTERED_COEFFICIENT_HASHES

SIZE = 17
OMEGA = 1.5
ETA = 0.01
OMEGA_RATIONAL = Fraction(3, 2)
SEARCH_RADIUS = Fraction(1, 10**6)
MAXIMUM_KRAWCZYK_UTILIZATION = Fraction(1, 10**2)
MAXIMUM_REGISTERED_CORRECTION = Fraction(1, 10**8)
EXPECTED_PAIR_COUNT = 300
EXPECTED_ZERO_WAVE_COUNT = 36
EXPECTED_INTERNAL_COUNT = 108
EXPECTED_EXTERNAL_COUNT = 156
EXPECTED_OUTPUT_SUPPORT_COUNT = 25
EXPECTED_COMPLEX_UNKNOWN_COUNT = 3024
EXPECTED_EIGENPAIR_PROOF_COUNT = 12
EXPECTED_MODE_COUNT = 24


@dataclass(frozen=True, slots=True)
class _ModeEnclosure:
    identifier: str
    wave_index: WaveIndex
    branch: str
    right: tuple[ComplexRationalInterval, ...]
    left: tuple[ComplexRationalInterval, ...]
    eigenvalue: ComplexRationalInterval


@dataclass(frozen=True, slots=True)
class _LinearProof:
    image: tuple[ComplexRationalInterval, ...]
    utilization: Fraction
    point_inverse_defect: Fraction
    contraction_bound: Fraction
    correction_upper: Fraction
    hessian_correction_upper: Fraction
    reduced_correction_upper: Fraction
    proof_digest: str

    @property
    def included(self) -> bool:
        return self.utilization < 1 and self.contraction_bound < 1


def _rounded_complex(
    value: ComplexRationalInterval,
) -> ComplexRationalInterval:
    return ComplexRationalInterval(
        value.real.rounded_outward(INTERVAL_DECIMAL_DIGITS),
        value.imag.rounded_outward(INTERVAL_DECIMAL_DIGITS),
    )


def _rounded_add(
    left: ComplexRationalInterval,
    right: ComplexRationalInterval,
) -> ComplexRationalInterval:
    return _rounded_complex(left + right)


def _rounded_multiply(
    left: ComplexRationalInterval,
    right: ComplexRationalInterval,
) -> ComplexRationalInterval:
    return _rounded_complex(left * right)


def _rounded_scale(
    value: ComplexRationalInterval,
    scalar: int | Fraction,
) -> ComplexRationalInterval:
    return _rounded_complex(value.scale(scalar))


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _artifact_record(
    path: Path,
    registered_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    observed_sha256 = _file_sha256(path)
    return payload, {
        "filename": path.name,
        "sha256": observed_sha256,
        "registered_sha256": registered_sha256,
        "sha256_matches": observed_sha256 == registered_sha256,
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
    }


def _load_registered_inputs(
    artifact_directory: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    q006i, q006i_record = _artifact_record(
        artifact_directory / Q006I_ARTIFACT,
        REGISTERED_INPUT_SHA256["q006i"],
    )
    q007j_artifact, q007j_record = _artifact_record(
        artifact_directory / Q007J_ARTIFACT,
        REGISTERED_INPUT_SHA256["q007j"],
    )

    q006i_scope = q006i.get("mathematical_scope", {})
    q006i_cycle = q006i.get("cycle", {})
    q006i_failed_hypotheses = sorted(
        name
        for name, gate in q006i_cycle.get("hypothesis_gates", {}).items()
        if not gate.get("passed", False)
    )
    q006i_record.update(
        {
            "scope_match": bool(
                q006i_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q006i_scope.get("omega", math.nan)) == OMEGA
                and float(q006i_scope.get("eta", math.nan)) == ETA
                and q006i_scope.get("selected_real_dimension") == 24
                and q006i_scope.get("conservation_treatment")
                == "fixed global mass and momentum leaf"
            ),
            "all_validity_gates_passed": bool(
                q006i_cycle.get("validity_gates")
                and all(
                    gate.get("passed", False)
                    for gate in q006i_cycle["validity_gates"].values()
                )
            ),
            "failed_hypothesis_gates": q006i_failed_hypotheses,
        }
    )
    q006i_record["passed"] = bool(
        q006i_record["sha256_matches"]
        and q006i_record["source_match"]
        and q006i.get("study_gate") == "passed"
        and q006i.get("scientific_outcome") == "rejected"
        and q006i_record["scope_match"]
        and q006i_record["all_validity_gates_passed"]
        and q006i_failed_hypotheses == ["global_conservation"]
    )

    q007j_scope = q007j_artifact.get("mathematical_scope", {})
    q007j_cycle = q007j_artifact.get("cycle", {})
    q007j_runner_sha = _file_sha256(Path(q007j.__file__).resolve())
    q007j_record.update(
        {
            "scope_match": bool(
                q007j_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q007j_scope.get("omega", math.nan)) == OMEGA
                and float(q007j_scope.get("eta", math.nan)) == ETA
                and q007j_scope.get("selected_real_dimension") == 24
                and q007j_scope.get("right_left_system_count")
                == EXPECTED_EIGENPAIR_PROOF_COUNT
                and q007j_scope.get("conservation_treatment")
                == "fixed global mass and momentum leaf"
            ),
            "all_validity_gates_passed": bool(
                len(q007j_cycle.get("validity_gates", {})) == 5
                and all(
                    gate.get("passed", False)
                    for gate in q007j_cycle["validity_gates"].values()
                )
            ),
            "all_hypothesis_gates_passed": bool(
                len(q007j_cycle.get("hypothesis_gates", {})) == 4
                and all(
                    gate.get("passed", False)
                    for gate in q007j_cycle["hypothesis_gates"].values()
                )
            ),
            "registered_runner_sha256": REGISTERED_Q007J_RUNNER_SHA256,
            "artifact_runner_sha256": q007j_artifact.get("runner_source", {}).get(
                "sha256"
            ),
            "observed_runner_sha256": q007j_runner_sha,
            "runner_sha_matches": bool(
                q007j_runner_sha == REGISTERED_Q007J_RUNNER_SHA256
                and q007j_artifact.get("runner_source", {}).get("sha256")
                == REGISTERED_Q007J_RUNNER_SHA256
            ),
        }
    )
    q007j_record["passed"] = bool(
        q007j_record["sha256_matches"]
        and q007j_record["source_match"]
        and q007j_artifact.get("study_gate") == "passed"
        and q007j_artifact.get("scientific_outcome") == "accepted"
        and q007j_record["scope_match"]
        and q007j_record["all_validity_gates_passed"]
        and q007j_record["all_hypothesis_gates_passed"]
        and q007j_record["runner_sha_matches"]
    )
    return q006i, q007j_artifact, {
        "q006i": q006i_record,
        "q007j": q007j_record,
    }


def _representative_eigenpair_proofs(
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    symbols: dict[WaveIndex, ComplexIntervalMatrix],
) -> dict[tuple[WaveIndex, str, str], Any]:
    proofs = {}
    for wave_index in q007j.REPRESENTATIVE_WAVES:
        numeric_matrix = filtered_fourier_symbol(
            *wave_vector_from_index(wave_index, SIZE),
            OMEGA,
            ETA,
        )
        for branch in MODE_ORDER:
            mode = modes[lookup[(wave_index, branch)]]
            right_proof = q007j._certify_eigenpair(
                wave_index=wave_index,
                branch=branch,
                role="right",
                interval_matrix=symbols[wave_index],
                numeric_matrix=numeric_matrix,
                vector_center=mode.right,
                eigenvalue_center=mode.eigenvalue,
                pivot=int(np.argmax(np.abs(mode.right))),
            )
            left_proof = q007j._certify_eigenpair(
                wave_index=wave_index,
                branch=branch,
                role="left",
                interval_matrix=q007j._complex_adjoint(symbols[wave_index]),
                numeric_matrix=numeric_matrix.conj().T,
                vector_center=mode.left,
                eigenvalue_center=np.conjugate(mode.eigenvalue),
                pivot=int(np.argmax(np.abs(mode.left))),
            )
            proofs[(wave_index, branch, "right")] = right_proof
            proofs[(wave_index, branch, "left")] = left_proof
    return proofs


def _reconstruct_mode_enclosures(
    q007j_artifact: dict[str, Any],
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    symbols: dict[WaveIndex, ComplexIntervalMatrix],
) -> tuple[
    dict[int, _ModeEnclosure],
    dict[str, Any],
]:
    proofs = _representative_eigenpair_proofs(modes, lookup, symbols)
    artifact_records = {
        (
            tuple(record["wave_index"]),
            record["branch"],
            record["role"],
        ): record
        for record in q007j_artifact["cycle"]["krawczyk_certification"][
            "records"
        ]
    }
    proof_records = []
    digest_mismatches = 0
    for key, proof in proofs.items():
        artifact_digest = artifact_records.get(key, {}).get(
            "proof_digest_sha256"
        )
        digest_matches = proof.proof_digest == artifact_digest
        digest_mismatches += not digest_matches
        proof_records.append(
            {
                "wave_index": list(key[0]),
                "branch": key[1],
                "role": key[2],
                "proof_digest_sha256": proof.proof_digest,
                "artifact_digest_sha256": artifact_digest,
                "digest_matches": digest_matches,
                "included": proof.included,
            }
        )

    enclosures = {}
    maximum_right_correction = Fraction(0)
    maximum_left_correction = Fraction(0)
    maximum_eigenvalue_correction = Fraction(0)
    minimum_overlap: Fraction | None = None
    transport_records = []
    for target_wave in WAVE_ORDER:
        source_wave = (
            q007j.REPRESENTATIVE_WAVES[0]
            if 0 in target_wave
            else q007j.REPRESENTATIVE_WAVES[1]
        )
        power = q007j._rotation_power(source_wave, target_wave)
        for branch in MODE_ORDER:
            mode_index = lookup[(target_wave, branch)]
            target_mode = modes[mode_index]
            right_proof = proofs[(source_wave, branch, "right")]
            left_proof = proofs[(source_wave, branch, "left")]
            transported_right = q007j._transport_vector(
                right_proof.root_vector,
                power,
            )
            transported_left = q007j._transport_vector(
                left_proof.root_vector,
                power,
            )
            right_pivot = int(np.argmax(np.abs(target_mode.right)))
            left_pivot = int(np.argmax(np.abs(target_mode.left)))
            right_enclosure = q007j._normalize_to_registered_scale(
                transported_right,
                target_mode.right,
                right_pivot,
            )
            left_pivot_normalized = q007j._scale_vector(
                transported_left,
                q007j._complex_reciprocal(transported_left[left_pivot]),
            )
            left_enclosure, overlap = q007j._biorthogonal_left(
                left_pivot_normalized,
                right_enclosure,
            )
            right_enclosure = tuple(
                _rounded_complex(value) for value in right_enclosure
            )
            left_enclosure = tuple(
                _rounded_complex(value) for value in left_enclosure
            )
            eigenvalue_enclosure = _rounded_complex(
                right_proof.root_eigenvalue
            )
            right_correction = q007j._maximum_vector_correction(
                right_enclosure,
                target_mode.right,
            )
            left_correction = q007j._maximum_vector_correction(
                left_enclosure,
                target_mode.left,
            )
            eigenvalue_correction = _complex_rectangle_absolute_upper(
                eigenvalue_enclosure - _complex_point(target_mode.eigenvalue)
            )
            maximum_right_correction = max(
                maximum_right_correction,
                right_correction,
            )
            maximum_left_correction = max(
                maximum_left_correction,
                left_correction,
            )
            maximum_eigenvalue_correction = max(
                maximum_eigenvalue_correction,
                eigenvalue_correction,
            )
            minimum_overlap = (
                overlap.lower
                if minimum_overlap is None
                else min(minimum_overlap, overlap.lower)
            )
            enclosure = _ModeEnclosure(
                identifier=target_mode.identifier,
                wave_index=target_wave,
                branch=branch,
                right=right_enclosure,
                left=left_enclosure,
                eigenvalue=eigenvalue_enclosure,
            )
            enclosures[mode_index] = enclosure
            transport_records.append(
                {
                    "mode_identifier": target_mode.identifier,
                    "wave_index": list(target_wave),
                    "branch": branch,
                    "source_wave": list(source_wave),
                    "rotation_power": power,
                    "right_correction_upper": _fraction_record(
                        right_correction
                    ),
                    "biorthogonal_left_correction_upper": _fraction_record(
                        left_correction
                    ),
                    "eigenvalue_correction_upper": _fraction_record(
                        eigenvalue_correction
                    ),
                    "overlap_modulus_lower": _fraction_record(overlap.lower),
                }
            )
    return enclosures, {
        "representative_system_count": len(proofs),
        "artifact_proof_record_count": len(artifact_records),
        "proof_digest_mismatch_count": digest_mismatches,
        "all_reconstructed_proofs_included": all(
            proof.included for proof in proofs.values()
        ),
        "transported_mode_count": len(enclosures),
        "maximum_right_correction_upper": _fraction_record(
            maximum_right_correction
        ),
        "maximum_biorthogonal_left_correction_upper": _fraction_record(
            maximum_left_correction
        ),
        "maximum_eigenvalue_correction_upper": _fraction_record(
            maximum_eigenvalue_correction
        ),
        "minimum_overlap_modulus_lower": _fraction_record(
            Fraction(0) if minimum_overlap is None else minimum_overlap
        ),
        "proof_records": proof_records,
        "transport_records": transport_records,
    }


def _exact_moment_matrix() -> tuple[tuple[Fraction, ...], ...]:
    return (
        tuple(Fraction(1) for _ in VELOCITIES),
        tuple(Fraction(cx) for cx, _cy in VELOCITIES),
        tuple(Fraction(cy) for _cx, cy in VELOCITIES),
    )


def _exact_equilibrium_hessian() -> tuple[
    tuple[tuple[Fraction, ...], ...],
    ...,
]:
    result = []
    for (cx, cy), weight in zip(VELOCITIES, WEIGHTS, strict=True):
        population = [[Fraction(0) for _ in range(3)] for _ in range(3)]
        population[1][1] = weight * (9 * cx * cx - 3)
        population[2][2] = weight * (9 * cy * cy - 3)
        population[1][2] = 9 * weight * cx * cy
        population[2][1] = population[1][2]
        result.append(tuple(tuple(row) for row in population))
    return tuple(result)


def _moment_hessian_contraction(
    moments: tuple[tuple[Fraction, ...], ...],
    hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
) -> tuple[tuple[tuple[Fraction, ...], ...], ...]:
    return tuple(
        tuple(
            tuple(
                sum(
                    (
                        moments[output_moment][population]
                        * hessian[population][left_moment][right_moment]
                        for population in range(9)
                    ),
                    Fraction(0),
                )
                for right_moment in range(3)
            )
            for left_moment in range(3)
        )
        for output_moment in range(3)
    )


def _moment_symbol_product(
    moments: tuple[tuple[Fraction, ...], ...],
    symbol: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    result = []
    for moment_row in moments:
        output_row = []
        for column in range(9):
            total = ComplexRationalInterval.zero()
            for coefficient, symbol_row in zip(
                moment_row,
                symbol,
                strict=True,
            ):
                total = total + symbol_row[column].scale(coefficient)
            output_row.append(total)
        result.append(output_row)
    return result


def _exact_identity_audit(
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
    collision: tuple[tuple[Fraction, ...], ...],
) -> tuple[
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[tuple[Fraction, ...], ...], ...],
    dict[str, Any],
]:
    moments = _exact_moment_matrix()
    hessian = _exact_equilibrium_hessian()
    moment_hessian = _moment_hessian_contraction(moments, hessian)
    moment_hessian_zero = all(
        value == 0
        for matrix in moment_hessian
        for row in matrix
        for value in row
    )
    zero_symbol = rational_fourier_symbol((0, 0), trig, collision)
    moment_symbol = _moment_symbol_product(moments, zero_symbol)
    moment_symbol_exact = all(
        value
        == ComplexRationalInterval.point(moments[row_index][column_index])
        for row_index, row in enumerate(moment_symbol)
        for column_index, value in enumerate(row)
    )
    hessian_values = [
        value
        for population in hessian
        for row in population
        for value in row
    ]
    moment_hessian_values = [
        value
        for matrix in moment_hessian
        for row in matrix
        for value in row
    ]
    return moments, hessian, {
        "equilibrium_hessian_sha256": _proof_digest(hessian_values),
        "moment_hessian_sha256": _proof_digest(moment_hessian_values),
        "moment_hessian_entry_count": len(moment_hessian_values),
        "moment_hessian_all_zero": moment_hessian_zero,
        "zero_wave_moment_symbol_exact": moment_symbol_exact,
        "zero_wave_moment_symbol_entry_count": sum(
            len(row) for row in moment_symbol
        ),
    }


def _canonical_index(value: int) -> int:
    half = SIZE // 2
    return (int(value) + half) % SIZE - half


def _filter_phase_factors(
    wave_index: WaveIndex,
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
) -> tuple[ComplexRationalInterval, ...]:
    nx, ny = wave_index
    cosine_x = trig[nx][1]
    cosine_y = trig[ny][1]
    multiplier = (
        RationalInterval.point(Fraction(99, 100))
        + (cosine_x + cosine_y).scale(Fraction(1, 200))
    )
    result = []
    for cx, cy in VELOCITIES:
        sine, cosine = trig[_canonical_index(nx * cx + ny * cy)]
        phase = ComplexRationalInterval(cosine, -sine)
        result.append(
            _rounded_complex(
                ComplexRationalInterval(
                    phase.real * multiplier,
                    phase.imag * multiplier,
                )
            )
        )
    return tuple(result)


def _mode_moments(
    moments: tuple[tuple[Fraction, ...], ...],
    vector: Sequence[ComplexRationalInterval],
) -> tuple[ComplexRationalInterval, ...]:
    result = []
    for row in moments:
        total = ComplexRationalInterval.zero()
        for coefficient, value in zip(row, vector, strict=True):
            total = _rounded_add(
                total,
                _rounded_scale(value, coefficient),
            )
        result.append(total)
    return tuple(result)


def _quadratic_forcing(
    left: _ModeEnclosure,
    right: _ModeEnclosure,
    wave_index: WaveIndex,
    moments: tuple[tuple[Fraction, ...], ...],
    hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
) -> tuple[ComplexRationalInterval, ...]:
    left_moments = _mode_moments(moments, left.right)
    right_moments = _mode_moments(moments, right.right)
    phase_factors = _filter_phase_factors(wave_index, trig)
    forcing = []
    for population in range(9):
        local = ComplexRationalInterval.zero()
        for left_moment in range(3):
            for right_moment in range(3):
                coefficient = hessian[population][left_moment][right_moment]
                if coefficient:
                    product = _rounded_multiply(
                        left_moments[left_moment],
                        right_moments[right_moment],
                    )
                    local = _rounded_add(
                        local,
                        _rounded_scale(product, coefficient),
                    )
        forcing.append(
            _rounded_multiply(
                phase_factors[population],
                _rounded_scale(local, OMEGA_RATIONAL),
            )
        )
    return tuple(forcing)


def _selected_mode_indices(
    wave_index: WaveIndex,
    lookup: dict[tuple[WaveIndex, str], int],
) -> tuple[int, int, int]:
    return tuple(lookup[(wave_index, branch)] for branch in MODE_ORDER)


def _interval_operator(
    output_wave: WaveIndex,
    output_kind: str,
    left: _ModeEnclosure,
    right: _ModeEnclosure,
    enclosures: dict[int, _ModeEnclosure],
    lookup: dict[tuple[WaveIndex, str], int],
    symbols: dict[WaveIndex, ComplexIntervalMatrix],
) -> ComplexIntervalMatrix:
    multiplier_product = _rounded_multiply(
        left.eigenvalue,
        right.eigenvalue,
    )
    base = [list(row) for row in symbols[output_wave]]
    for diagonal in range(9):
        base[diagonal][diagonal] = _rounded_add(
            base[diagonal][diagonal],
            -multiplier_product,
        )
    if output_kind != "internal_selected":
        return base

    output_indices = _selected_mode_indices(output_wave, lookup)
    output_modes = tuple(enclosures[index] for index in output_indices)
    augmented = []
    for row_index, row in enumerate(base):
        augmented.append(
            [
                *row,
                *(-mode.right[row_index] for mode in output_modes),
            ]
        )
    for mode in output_modes:
        augmented.append(
            [
                *(q007j._complex_conjugate(value) for value in mode.left),
                *(ComplexRationalInterval.zero() for _ in range(3)),
            ]
        )
    return augmented


def _numeric_operator(
    output_wave: WaveIndex,
    output_kind: str,
    left_index: int,
    right_index: int,
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
) -> np.ndarray:
    left = modes[left_index]
    right = modes[right_index]
    matrix = filtered_fourier_symbol(
        *wave_vector_from_index(output_wave, SIZE),
        OMEGA,
        ETA,
    )
    base = matrix - left.eigenvalue * right.eigenvalue * np.eye(9)
    if output_kind != "internal_selected":
        return np.asarray(base, dtype=np.complex128)

    output_indices = _selected_mode_indices(output_wave, lookup)
    selected_right = np.column_stack(
        [modes[index].right for index in output_indices]
    )
    selected_left = np.vstack(
        [np.conjugate(modes[index].left) for index in output_indices]
    )
    return np.block(
        [
            [base, -selected_right],
            [selected_left, np.zeros((3, 3), dtype=np.complex128)],
        ]
    )


def _right_hand_side(
    forcing: Sequence[ComplexRationalInterval],
    output_kind: str,
) -> tuple[ComplexRationalInterval, ...]:
    result = tuple(-value for value in forcing)
    if output_kind == "internal_selected":
        result = (
            *result,
            *(ComplexRationalInterval.zero() for _ in range(3)),
        )
    return result


def _column(
    values: Sequence[ComplexRationalInterval],
) -> ComplexIntervalMatrix:
    return [[value] for value in values]


def _flatten_column(
    matrix: ComplexIntervalMatrix,
) -> tuple[ComplexRationalInterval, ...]:
    if any(len(row) != 1 for row in matrix):
        raise ValueError("matrix is not a column")
    return tuple(row[0] for row in matrix)


def _matrix_add(
    left: ComplexIntervalMatrix,
    right: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    if len(left) != len(right) or any(
        len(left_row) != len(right_row)
        for left_row, right_row in zip(left, right, strict=True)
    ):
        raise ValueError("matrix shapes differ")
    return [
        [
            _rounded_add(left_value, right_value)
            for left_value, right_value in zip(
                left_row,
                right_row,
                strict=True,
            )
        ]
        for left_row, right_row in zip(left, right, strict=True)
    ]


def _matrix_subtract(
    left: ComplexIntervalMatrix,
    right: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    if len(left) != len(right) or any(
        len(left_row) != len(right_row)
        for left_row, right_row in zip(left, right, strict=True)
    ):
        raise ValueError("matrix shapes differ")
    return [
        [
            _rounded_add(left_value, -right_value)
            for left_value, right_value in zip(
                left_row,
                right_row,
                strict=True,
            )
        ]
        for left_row, right_row in zip(left, right, strict=True)
    ]


def _matrix_multiply(
    left: ComplexIntervalMatrix,
    right: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    if not left or not right or len(left[0]) != len(right):
        raise ValueError("incompatible matrix dimensions")
    output = []
    for left_row in left:
        output_row = []
        for column in range(len(right[0])):
            total = ComplexRationalInterval.zero()
            for index, left_value in enumerate(left_row):
                total = _rounded_add(
                    total,
                    _rounded_multiply(left_value, right[index][column]),
                )
            output_row.append(total)
        output.append(output_row)
    return output


def _krawczyk_utilization(
    image: Sequence[ComplexRationalInterval],
    centers: Sequence[complex],
) -> Fraction:
    utilization = Fraction(0)
    for value, center_value in zip(image, centers, strict=True):
        center = _complex_point(center_value)
        utilization = max(
            utilization,
            abs(value.real.lower - center.real.lower) / SEARCH_RADIUS,
            abs(value.real.upper - center.real.upper) / SEARCH_RADIUS,
            abs(value.imag.lower - center.imag.lower) / SEARCH_RADIUS,
            abs(value.imag.upper - center.imag.upper) / SEARCH_RADIUS,
        )
    return utilization


def _proof_digest_for_boxes(
    boxes: Sequence[ComplexRationalInterval],
    extra: Sequence[Fraction],
) -> str:
    values = []
    for box in boxes:
        values.extend(
            (box.real.lower, box.real.upper, box.imag.lower, box.imag.upper)
        )
    values.extend(extra)
    digest = sha256()
    for value in values:
        digest.update(hex(value.numerator).encode("ascii"))
        digest.update(b"/")
        digest.update(hex(value.denominator).encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _certify_linear_system(
    interval_operator: ComplexIntervalMatrix,
    numeric_operator: np.ndarray,
    right_hand_side: Sequence[ComplexRationalInterval],
    center: np.ndarray,
) -> _LinearProof:
    dimension = len(center)
    if numeric_operator.shape != (dimension, dimension):
        raise ValueError("numeric operator and center dimensions differ")
    center_values = tuple(complex(value) for value in center)
    center_points = tuple(_complex_point(value) for value in center_values)
    inverse_candidate = np.linalg.inv(numeric_operator)
    preconditioner = _matrix_from_numpy(inverse_candidate)
    point_operator = _matrix_from_numpy(numeric_operator)
    point_inverse_defect = _matrix_infinity_norm_upper(
        _matrix_subtract(
            _identity_matrix(dimension),
            _matrix_multiply(preconditioner, point_operator),
        )
    )
    contraction_matrix = _matrix_subtract(
        _identity_matrix(dimension),
        _matrix_multiply(preconditioner, interval_operator),
    )
    contraction_bound = _matrix_infinity_norm_upper(contraction_matrix)
    residual = _matrix_subtract(
        _matrix_multiply(interval_operator, _column(center_points)),
        _column(right_hand_side),
    )
    center_term = _matrix_subtract(
        _column(center_points),
        _matrix_multiply(preconditioner, residual),
    )
    centered_box = tuple(
        ComplexRationalInterval(
            RationalInterval(-SEARCH_RADIUS, SEARCH_RADIUS),
            RationalInterval(-SEARCH_RADIUS, SEARCH_RADIUS),
        )
        for _ in range(dimension)
    )
    variation = _matrix_multiply(
        contraction_matrix,
        _column(centered_box),
    )
    image = _flatten_column(_matrix_add(center_term, variation))
    utilization = _krawczyk_utilization(image, center_values)
    component_corrections = tuple(
        _complex_rectangle_absolute_upper(value - center_point)
        for value, center_point in zip(image, center_points, strict=True)
    )
    correction_upper = max(component_corrections)
    hessian_correction = max(component_corrections[:9])
    reduced_correction = (
        max(component_corrections[9:])
        if len(component_corrections) > 9
        else Fraction(0)
    )
    proof_digest = _proof_digest_for_boxes(
        image,
        (
            utilization,
            point_inverse_defect,
            contraction_bound,
            correction_upper,
            hessian_correction,
            reduced_correction,
        ),
    )
    return _LinearProof(
        image=image,
        utilization=utilization,
        point_inverse_defect=point_inverse_defect,
        contraction_bound=contraction_bound,
        correction_upper=correction_upper,
        hessian_correction_upper=hessian_correction,
        reduced_correction_upper=reduced_correction,
        proof_digest=proof_digest,
    )


def _pair_correspondence(
    observed: Sequence[dict[str, Any]],
    artifact: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    fields = (
        "pair_identifier",
        "left_mode",
        "right_mode",
        "left_wave_index",
        "right_wave_index",
        "output_wave_index",
        "output_kind",
    )
    mismatch_records = []
    for index, (observed_record, artifact_record) in enumerate(
        zip(observed, artifact, strict=False)
    ):
        mismatches = {
            field: {
                "observed": observed_record.get(field),
                "artifact": artifact_record.get(field),
            }
            for field in fields
            if observed_record.get(field) != artifact_record.get(field)
        }
        if mismatches:
            mismatch_records.append(
                {
                    "index": index,
                    "fields": mismatches,
                }
            )
    length_matches = len(observed) == len(artifact)
    return {
        "observed_pair_count": len(observed),
        "artifact_pair_count": len(artifact),
        "length_matches": length_matches,
        "mismatch_count": len(mismatch_records)
        + (0 if length_matches else abs(len(observed) - len(artifact))),
        "mismatch_records": mismatch_records,
    }


def _registered_center(
    left_index: int,
    right_index: int,
    output_wave: WaveIndex,
    output_kind: str,
    hessian_coefficients: np.ndarray,
    reduced_coefficients: np.ndarray,
    lookup: dict[tuple[WaveIndex, str], int],
) -> np.ndarray:
    hessian_center = np.asarray(
        hessian_coefficients[left_index, right_index],
        dtype=np.complex128,
    )
    if output_kind != "internal_selected":
        return hessian_center
    output_indices = _selected_mode_indices(output_wave, lookup)
    reduced_center = np.asarray(
        reduced_coefficients[list(output_indices), left_index, right_index],
        dtype=np.complex128,
    )
    return np.concatenate([hessian_center, reduced_center])


def run_quadratic_jet_bridge_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Run the sealed Q007k rational quadratic-jet certification."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q006i, q007j_artifact, input_records = _load_registered_inputs(directory)
    _model, coefficient_reproduction = q007j._reproduce_q006i_model(q006i)
    modes, lookup = _build_complex_modes(SIZE, OMEGA, ETA)
    (
        hessian_coefficients,
        reduced_coefficients,
        _output_waves,
        pair_metadata,
    ) = _complex_coefficients(modes, lookup, SIZE, OMEGA, ETA)

    artifact_pair_metadata = q006i["cycle"]["construction"]["pair_records"]
    pair_correspondence = _pair_correspondence(
        pair_metadata,
        artifact_pair_metadata,
    )
    output_support = tuple(
        sorted({tuple(record["output_wave_index"]) for record in pair_metadata})
    )

    pi_interval = machin_pi_interval()
    trig = trigonometric_intervals(pi_interval)
    collision = rational_collision_symbol()
    symbols = {
        wave_index: rational_fourier_symbol(wave_index, trig, collision)
        for wave_index in output_support
    }
    for wave_index in q007j.REPRESENTATIVE_WAVES:
        symbols.setdefault(
            wave_index,
            rational_fourier_symbol(wave_index, trig, collision),
        )
    maximum_trigonometric_width = max(
        max(sine.width, cosine.width) for sine, cosine in trig.values()
    )
    maximum_symbol_width = max(
        max(value.real.width, value.imag.width)
        for matrix in symbols.values()
        for row in matrix
        for value in row
    )

    mode_enclosures, eigencoordinate_reconstruction = (
        _reconstruct_mode_enclosures(
            q007j_artifact,
            modes,
            lookup,
            symbols,
        )
    )
    moments, equilibrium_hessian, exact_identities = _exact_identity_audit(
        trig,
        collision,
    )

    proof_records = []
    proofs: list[_LinearProof] = []
    zero_wave_separations = []
    kind_counts = {
        "zero_wave_kinetic": 0,
        "internal_selected": 0,
        "external": 0,
    }
    complex_unknown_count = 0
    graph_gauge_inclusion_count = 0
    singular_system_count = 0
    unassigned_system_count = 0
    maximum_correction_pair = None
    maximum_correction = Fraction(-1)

    pair_indices = combinations_with_replacement(range(len(modes)), 2)
    for pair_index, ((left_index, right_index), metadata) in enumerate(
        zip(pair_indices, pair_metadata, strict=True)
    ):
        output_wave = tuple(metadata["output_wave_index"])
        output_kind = metadata["output_kind"]
        kind_counts[output_kind] += 1
        left = mode_enclosures[left_index]
        right = mode_enclosures[right_index]
        forcing = _quadratic_forcing(
            left,
            right,
            output_wave,
            moments,
            equilibrium_hessian,
            trig,
        )
        interval_operator = _interval_operator(
            output_wave,
            output_kind,
            left,
            right,
            mode_enclosures,
            lookup,
            symbols,
        )
        numeric_operator = _numeric_operator(
            output_wave,
            output_kind,
            left_index,
            right_index,
            modes,
            lookup,
        )
        right_hand_side = _right_hand_side(forcing, output_kind)
        center = _registered_center(
            left_index,
            right_index,
            output_wave,
            output_kind,
            hessian_coefficients,
            reduced_coefficients,
            lookup,
        )
        complex_unknown_count += len(center)
        if interval_operator is None or len(interval_operator) != len(center):
            unassigned_system_count += 1
            continue
        try:
            proof = _certify_linear_system(
                interval_operator,
                numeric_operator,
                right_hand_side,
                center,
            )
        except np.linalg.LinAlgError:
            singular_system_count += 1
            continue
        proofs.append(proof)
        if output_kind == "internal_selected" and proof.included:
            graph_gauge_inclusion_count += 1

        product_separation = None
        if output_wave == (0, 0):
            product_separation = q007j._complex_absolute_bounds(
                ComplexRationalInterval.point(1)
                - _rounded_multiply(left.eigenvalue, right.eigenvalue)
            ).lower
            zero_wave_separations.append(product_separation)

        if proof.correction_upper > maximum_correction:
            maximum_correction = proof.correction_upper
            maximum_correction_pair = metadata["pair_identifier"]
        proof_records.append(
            {
                "pair_index": pair_index,
                "pair_identifier": metadata["pair_identifier"],
                "left_mode": metadata["left_mode"],
                "right_mode": metadata["right_mode"],
                "output_wave_index": list(output_wave),
                "output_kind": output_kind,
                "system_dimension": len(center),
                "included": proof.included,
                "graph_gauge_rows_included": bool(
                    output_kind == "internal_selected" and proof.included
                ),
                "krawczyk_utilization": _fraction_record(proof.utilization),
                "point_inverse_defect": _fraction_record(
                    proof.point_inverse_defect
                ),
                "interval_contraction_bound": _fraction_record(
                    proof.contraction_bound
                ),
                "registered_correction_upper": _fraction_record(
                    proof.correction_upper
                ),
                "hessian_correction_upper": _fraction_record(
                    proof.hessian_correction_upper
                ),
                "reduced_correction_upper": _fraction_record(
                    proof.reduced_correction_upper
                ),
                "product_separation_from_one_lower": (
                    None
                    if product_separation is None
                    else _fraction_record(product_separation)
                ),
                "proof_digest_sha256": proof.proof_digest,
            }
        )

    maximum_utilization = max(
        (proof.utilization for proof in proofs),
        default=Fraction(1),
    )
    maximum_point_inverse_defect = max(
        (proof.point_inverse_defect for proof in proofs),
        default=Fraction(1),
    )
    maximum_contraction = max(
        (proof.contraction_bound for proof in proofs),
        default=Fraction(1),
    )
    maximum_hessian_correction = max(
        (proof.hessian_correction_upper for proof in proofs),
        default=Fraction(1),
    )
    maximum_reduced_correction = max(
        (proof.reduced_correction_upper for proof in proofs),
        default=Fraction(1),
    )
    if not proofs:
        maximum_correction = Fraction(1)
    minimum_zero_wave_separation = min(
        zero_wave_separations,
        default=Fraction(-1),
    )
    included_count = sum(proof.included for proof in proofs)

    interval_construction = {
        "outward_rounding_decimal_digits": INTERVAL_DECIMAL_DIGITS,
        "pi_width": _fraction_record(pi_interval.width),
        "maximum_trigonometric_width": _fraction_record(
            maximum_trigonometric_width
        ),
        "maximum_symbol_entry_width": _fraction_record(maximum_symbol_width),
        "maximum_point_inverse_defect": _fraction_record(
            maximum_point_inverse_defect
        ),
    }
    enumeration = {
        "pair_count": len(pair_metadata),
        "kind_counts": kind_counts,
        "output_wave_support_count": len(output_support),
        "output_wave_support": [list(wave) for wave in output_support],
        "complex_unknown_count": complex_unknown_count,
        "assigned_system_count": len(proofs),
        "singular_system_count": singular_system_count,
        "unassigned_system_count": unassigned_system_count,
    }
    certification = {
        "search_box_component_radius": _fraction_record(SEARCH_RADIUS),
        "system_count": len(proofs),
        "included_count": included_count,
        "maximum_krawczyk_utilization": _fraction_record(
            maximum_utilization
        ),
        "maximum_interval_contraction_bound": _fraction_record(
            maximum_contraction
        ),
        "maximum_registered_correction_upper": _fraction_record(
            max(Fraction(0), maximum_correction)
        ),
        "maximum_hessian_correction_upper": _fraction_record(
            maximum_hessian_correction
        ),
        "maximum_reduced_correction_upper": _fraction_record(
            maximum_reduced_correction
        ),
        "maximum_correction_pair_identifier": maximum_correction_pair,
        "zero_wave_product_separation_count": len(zero_wave_separations),
        "minimum_zero_wave_product_separation_lower": _fraction_record(
            minimum_zero_wave_separation
        ),
        "zero_wave_structural_fixed_leaf_count": (
            len(zero_wave_separations)
            if exact_identities["moment_hessian_all_zero"]
            and exact_identities["zero_wave_moment_symbol_exact"]
            else 0
        ),
        "internal_graph_gauge_inclusion_count": (
            graph_gauge_inclusion_count
        ),
        "records": proof_records,
    }

    serializable_sections = {
        "input_artifacts": input_records,
        "coefficient_reproduction": coefficient_reproduction,
        "eigencoordinate_reconstruction": eigencoordinate_reconstruction,
        "pair_correspondence": pair_correspondence,
        "exact_identities": exact_identities,
        "interval_construction": interval_construction,
        "enumeration": enumeration,
        "krawczyk_certification": certification,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )

    validity_gates = {
        "registered_inputs_coefficients_and_eigenpair_proofs": {
            "passed": bool(
                all(record["passed"] for record in input_records.values())
                and coefficient_reproduction["matches"]
                and eigencoordinate_reconstruction[
                    "representative_system_count"
                ]
                == EXPECTED_EIGENPAIR_PROOF_COUNT
                and eigencoordinate_reconstruction[
                    "artifact_proof_record_count"
                ]
                == EXPECTED_EIGENPAIR_PROOF_COUNT
                and eigencoordinate_reconstruction[
                    "proof_digest_mismatch_count"
                ]
                == 0
                and eigencoordinate_reconstruction[
                    "transported_mode_count"
                ]
                == EXPECTED_MODE_COUNT
            ),
            "threshold": (
                "fixed Q006i/Q007j SHAs, package/runner sources, coefficient "
                "hashes, and all 12 reconstructed proof digests match"
            ),
            "value": {
                "inputs": {
                    name: record["passed"]
                    for name, record in input_records.items()
                },
                "coefficient_hashes_match": coefficient_reproduction[
                    "matches"
                ],
                "proof_digest_mismatches": eigencoordinate_reconstruction[
                    "proof_digest_mismatch_count"
                ],
                "transported_modes": eigencoordinate_reconstruction[
                    "transported_mode_count"
                ],
            },
        },
        "registered_pair_enumeration": {
            "passed": bool(
                enumeration["pair_count"] == EXPECTED_PAIR_COUNT
                and kind_counts["zero_wave_kinetic"]
                == EXPECTED_ZERO_WAVE_COUNT
                and kind_counts["internal_selected"] == EXPECTED_INTERNAL_COUNT
                and kind_counts["external"] == EXPECTED_EXTERNAL_COUNT
                and enumeration["output_wave_support_count"]
                == EXPECTED_OUTPUT_SUPPORT_COUNT
                and complex_unknown_count == EXPECTED_COMPLEX_UNKNOWN_COUNT
            ),
            "threshold": (
                "300 = 36 zero + 108 internal + 156 external pairs, 25 "
                "output waves, 3024 complex unknowns"
            ),
            "value": enumeration,
        },
        "exact_quadratic_and_conservation_identities": {
            "passed": bool(
                exact_identities["moment_hessian_all_zero"]
                and exact_identities["zero_wave_moment_symbol_exact"]
            ),
            "threshold": "rational equilibrium Hessian has ME=0 and MA(0)=M entrywise",
            "value": exact_identities,
        },
        "rational_interval_construction": {
            "passed": bool(
                pi_interval.width <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_trigonometric_width
                <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_symbol_width <= MAXIMUM_SYMBOL_ENTRY_WIDTH
                and len(proofs) == EXPECTED_PAIR_COUNT
                and maximum_point_inverse_defect < 1
            ),
            "threshold": (
                "pi/trig <=1e-120, symbol <=1e-110, 300 point inverse "
                "defects <1"
            ),
            "value": interval_construction,
        },
        "pair_correspondence_and_strict_json": {
            "passed": bool(
                pair_correspondence["length_matches"]
                and pair_correspondence["mismatch_count"] == 0
                and finite_strict_json
            ),
            "threshold": (
                "all pair identifiers/waves/kinds match Q006i and all "
                "summaries are finite strict JSON"
            ),
            "value": {
                "pair_mismatch_count": pair_correspondence[
                    "mismatch_count"
                ],
                "finite_strict_json": finite_strict_json,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    hypothesis_gates = {
        "all_three_hundred_krawczyk_inclusions": {
            "passed": bool(
                included_count == EXPECTED_PAIR_COUNT
                and maximum_utilization <= MAXIMUM_KRAWCZYK_UTILIZATION
            ),
            "threshold": "300 strict inclusions and maximum utilization <=1e-2",
            "value": {
                "included_count": included_count,
                "maximum_utilization": float(maximum_utilization),
            },
        },
        "uniform_contraction_and_assignment": {
            "passed": bool(
                maximum_contraction < 1
                and singular_system_count == 0
                and unassigned_system_count == 0
            ),
            "threshold": (
                "maximum interval contraction <1 and zero singular or "
                "unassigned systems"
            ),
            "value": {
                "maximum_contraction": float(maximum_contraction),
                "singular_system_count": singular_system_count,
                "unassigned_system_count": unassigned_system_count,
            },
        },
        "registered_quadratic_coefficient_correction": {
            "passed": bool(
                maximum_correction <= MAXIMUM_REGISTERED_CORRECTION
            ),
            "threshold": (
                "maximum componentwise exact-root correction to registered "
                "complex H2/R2 <=1e-8"
            ),
            "value": {
                "maximum_correction": float(maximum_correction),
                "maximum_hessian_correction": float(
                    maximum_hessian_correction
                ),
                "maximum_reduced_correction": float(
                    maximum_reduced_correction
                ),
                "witness_pair_identifier": maximum_correction_pair,
            },
        },
        "fixed_leaf_and_graph_gauge_structure": {
            "passed": bool(
                len(zero_wave_separations) == EXPECTED_ZERO_WAVE_COUNT
                and minimum_zero_wave_separation > 0
                and certification["zero_wave_structural_fixed_leaf_count"]
                == EXPECTED_ZERO_WAVE_COUNT
                and graph_gauge_inclusion_count == EXPECTED_INTERNAL_COUNT
            ),
            "threshold": (
                "36 positive zero-wave product separations and structural "
                "fixed-leaf solutions; 108 augmented graph-gauge inclusions"
            ),
            "value": {
                "zero_wave_product_separation_count": len(
                    zero_wave_separations
                ),
                "minimum_zero_wave_product_separation": float(
                    minimum_zero_wave_separation
                ),
                "zero_wave_structural_fixed_leaf_count": certification[
                    "zero_wave_structural_fixed_leaf_count"
                ],
                "internal_graph_gauge_inclusion_count": (
                    graph_gauge_inclusion_count
                ),
            },
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        scientific_classification = (
            "registered quadratic-jet bridge audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        scientific_classification = (
            "registered Q006i quadratic coefficients identify the "
            "theorem-manifold graph-gauge quadratic jet"
        )
    else:
        outcome = "not_certified"
        scientific_classification = (
            "registered quadratic-jet bridge not certified"
        )

    return {
        "question": (
            "Do the 300 registered Q006i complex H2/R2 coefficients enclose "
            "the unique exact graph-gauge quadratic jet of the theorem manifold?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "mode_order": list(MODE_ORDER),
            "wave_order": [list(wave) for wave in WAVE_ORDER],
            "search_box_component_radius": _fraction_record(SEARCH_RADIUS),
        },
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": scientific_classification,
        "claim_boundary": (
            "This identifies only the degree-two graph-gauge Taylor jet of "
            "the local analytic theorem manifold on the fixed 17x17 "
            "conservation leaf. It does not certify cubic or quartic "
            "coefficients, an explicit neighborhood radius, finite-ball "
            "normal attraction, grid uniformity, or a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q006i_float64_global_conservation_rejection_changed": False,
            "q007i_theorem_acceptance_changed": False,
            "q007j_linear_eigencoordinate_acceptance_changed": False,
            "q007h_independent_preconditioner_inconclusive_changed": False,
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister a separate Q007l degree-three bridge; "
            "keep quartic coefficients and explicit radius in later gates."
        ),
    }


def run_q007k_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_quadratic_jet_bridge_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational graph-gauge quadratic-jet bridge",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": 24,
            "unordered_pair_count": EXPECTED_PAIR_COUNT,
            "complex_unknown_count": EXPECTED_COMPLEX_UNKNOWN_COUNT,
            "claim": (
                "degree-two Taylor-jet identification only; no cubic, "
                "quartic, explicit-radius, finite-ball, grid-uniform, or "
                "continuum claim"
            ),
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
    result = run_q007k_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
