"""Sealed Q007l rational cubic-jet bridge.

NumPy supplies only registered cubic coefficient centers and inverse
candidates.  Exact rational rectangles enclose the linear eigencoordinates,
quadratic jet, cubic forcing, homological operators, and Krawczyk images.
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

import research.q007k_quadratic_jet_bridge as q007k
from ttim_lbm.checkerboard_filter import filtered_fourier_symbol
from ttim_lbm.cubic_chart import build_full2d_cubic_model
from ttim_lbm.full2d_chart import MODE_ORDER, _complex_coefficients
from ttim_lbm.nonresonance import wave_vector_from_index
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    INTERVAL_DECIMAL_DIGITS,
    MAXIMUM_PI_TRIGONOMETRIC_WIDTH,
    MAXIMUM_SYMBOL_ENTRY_WIDTH,
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
    _strict_json_serializable,
    machin_pi_interval,
    rational_collision_symbol,
    rational_fourier_symbol,
    trigonometric_intervals,
)

Q007B_ARTIFACT = "q007b_cubic_continuation.json"
Q007J_ARTIFACT = "q007j_eigencoordinate_bridge.json"
Q007K_ARTIFACT = "q007k_quadratic_jet_bridge.json"

REGISTERED_INPUT_SHA256 = {
    "q007b": "5524fd316bece33387a3d1f6590321bc74579c48a87ee31bba090a295f9fa6dd",
    "q007k": "022f9ded6b40dc754a1b935f69554db9407e5e07715bd9132990ca9876fc8bbf",
}
REGISTERED_Q007K_RUNNER_SHA256 = (
    "963862710b772a63a9293bbb100ea50a21f3469932ee54d84cfd197a384f89cb"
)
REGISTERED_COEFFICIENT_HASHES = {
    "triple_indices_sha256": (
        "e646d2de7212c823cbca5804fbf20e9543918ecca80452dd508c278dfc5f130c"
    ),
    "output_waves_sha256": (
        "d431bfabad714d9d7ee9d8bfaf779eb2362ab27c916740494a379610c1389a6f"
    ),
    "chart_coefficients_sha256": (
        "ed182069713bff0558b806ce7a70e77299ea9fbc6671de38c4fa58019da5615b"
    ),
    "reduced_coefficients_sha256": (
        "4ca5a953833d5913f160e9fc36061e31697c7531865c4ef06d7517898f7c597e"
    ),
    "forcing_coefficients_sha256": (
        "6e2559a194d2b1e6a96f01653c1bccbe1852db00233700e16b3b980ae96df8eb"
    ),
}

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SEARCH_RADIUS = Fraction(1, 10**3)
MAXIMUM_KRAWCZYK_UTILIZATION = Fraction(1, 10**2)
MAXIMUM_REGISTERED_CORRECTION = Fraction(1, 10**5)
EXPECTED_TRIPLE_COUNT = 2600
EXPECTED_ZERO_WAVE_COUNT = 108
EXPECTED_INTERNAL_COUNT = 1044
EXPECTED_EXTERNAL_COUNT = 1448
EXPECTED_OUTPUT_SUPPORT_COUNT = 49
EXPECTED_COMPLEX_UNKNOWN_COUNT = 26532
EXPECTED_Q007J_PROOF_COUNT = 12
EXPECTED_Q007K_PROOF_COUNT = 300


@dataclass(frozen=True, slots=True)
class _QuadraticJet:
    hessian: tuple[
        tuple[tuple[ComplexRationalInterval, ...], ...],
        ...,
    ]
    reduced_outputs: dict[
        tuple[int, int],
        tuple[tuple[int, ComplexRationalInterval], ...],
    ]
    pair_output_waves: dict[tuple[int, int], WaveIndex]


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
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    q007b, q007b_record = _artifact_record(
        artifact_directory / Q007B_ARTIFACT,
        REGISTERED_INPUT_SHA256["q007b"],
    )
    q007k_artifact, q007k_record = _artifact_record(
        artifact_directory / Q007K_ARTIFACT,
        REGISTERED_INPUT_SHA256["q007k"],
    )

    q007b_scope = q007b.get("mathematical_scope", {})
    q007b_cycle = q007b.get("cycle", {})
    q007b_failed_hypotheses = sorted(
        name
        for name, gate in q007b_cycle.get("hypothesis_gates", {}).items()
        if not gate.get("passed", False)
    )
    q007b_record.update(
        {
            "scope_match": bool(
                q007b_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q007b_scope.get("omega", math.nan)) == OMEGA
                and float(q007b_scope.get("eta", math.nan)) == ETA
                and q007b_scope.get("real_reduced_dimension") == 24
                and q007b_scope.get("unordered_triple_count")
                == EXPECTED_TRIPLE_COUNT
            ),
            "all_validity_gates_passed": bool(
                len(q007b_cycle.get("validity_gates", {})) == 7
                and all(
                    gate.get("passed", False)
                    for gate in q007b_cycle["validity_gates"].values()
                )
            ),
            "failed_hypothesis_gates": q007b_failed_hypotheses,
        }
    )
    q007b_record["passed"] = bool(
        q007b_record["sha256_matches"]
        and q007b_record["source_match"]
        and q007b.get("study_gate") == "passed"
        and q007b.get("scientific_outcome") == "rejected"
        and q007b_record["scope_match"]
        and q007b_record["all_validity_gates_passed"]
        and q007b_failed_hypotheses == ["held_out_residual_ratio"]
    )

    q007k_scope = q007k_artifact.get("mathematical_scope", {})
    q007k_cycle = q007k_artifact.get("cycle", {})
    q007k_runner_sha = _file_sha256(Path(q007k.__file__).resolve())
    q007k_record.update(
        {
            "scope_match": bool(
                q007k_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q007k_scope.get("omega", math.nan)) == OMEGA
                and float(q007k_scope.get("eta", math.nan)) == ETA
                and q007k_scope.get("selected_real_dimension") == 24
                and q007k_scope.get("unordered_pair_count")
                == EXPECTED_Q007K_PROOF_COUNT
            ),
            "all_validity_gates_passed": bool(
                len(q007k_cycle.get("validity_gates", {})) == 5
                and all(
                    gate.get("passed", False)
                    for gate in q007k_cycle["validity_gates"].values()
                )
            ),
            "all_hypothesis_gates_passed": bool(
                len(q007k_cycle.get("hypothesis_gates", {})) == 4
                and all(
                    gate.get("passed", False)
                    for gate in q007k_cycle["hypothesis_gates"].values()
                )
            ),
            "registered_runner_sha256": REGISTERED_Q007K_RUNNER_SHA256,
            "artifact_runner_sha256": q007k_artifact.get(
                "runner_source", {}
            ).get("sha256"),
            "observed_runner_sha256": q007k_runner_sha,
            "runner_sha_matches": bool(
                q007k_runner_sha == REGISTERED_Q007K_RUNNER_SHA256
                and q007k_artifact.get("runner_source", {}).get("sha256")
                == REGISTERED_Q007K_RUNNER_SHA256
            ),
        }
    )
    q007k_record["passed"] = bool(
        q007k_record["sha256_matches"]
        and q007k_record["source_match"]
        and q007k_artifact.get("study_gate") == "passed"
        and q007k_artifact.get("scientific_outcome") == "accepted"
        and q007k_record["scope_match"]
        and q007k_record["all_validity_gates_passed"]
        and q007k_record["all_hypothesis_gates_passed"]
        and q007k_record["runner_sha_matches"]
    )

    embedded_q007j = q007k_cycle.get("input_artifacts", {}).get("q007j", {})
    q007j_path = artifact_directory / Q007J_ARTIFACT
    q007j_artifact = json.loads(q007j_path.read_text(encoding="utf-8"))
    q007j_sha = _file_sha256(q007j_path)
    q007j_record = {
        "filename": q007j_path.name,
        "sha256": q007j_sha,
        "q007k_embedded_sha256": embedded_q007j.get("sha256"),
        "q007k_embedded_registered_sha256": embedded_q007j.get(
            "registered_sha256"
        ),
        "source_match": q007j_artifact.get("source") == source_metadata(),
        "passed": bool(
            embedded_q007j.get("passed", False)
            and q007j_sha == embedded_q007j.get("sha256")
            and q007j_sha == embedded_q007j.get("registered_sha256")
            and q007j_artifact.get("study_gate") == "passed"
            and q007j_artifact.get("scientific_outcome") == "accepted"
            and q007j_artifact.get("source") == source_metadata()
        ),
    }
    return q007b, q007j_artifact, q007k_artifact, {
        "q007b": q007b_record,
        "q007j_transitive": q007j_record,
        "q007k": q007k_record,
    }


def _reproduce_q007b_model(
    q007b: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    model = build_full2d_cubic_model()
    observed = model.coefficient_hashes()
    artifact = q007b["cycle"]["coefficient_construction"][
        "coefficient_hashes"
    ]
    return model, {
        "registered": REGISTERED_COEFFICIENT_HASHES,
        "artifact": artifact,
        "observed": observed,
        "matches": bool(
            observed == REGISTERED_COEFFICIENT_HASHES
            and artifact == REGISTERED_COEFFICIENT_HASHES
        ),
    }


def _reconstruct_quadratic_jet(
    q007j_artifact: dict[str, Any],
    q007k_artifact: dict[str, Any],
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
    collision: tuple[tuple[Fraction, ...], ...],
) -> tuple[
    _QuadraticJet,
    dict[int, Any],
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[tuple[Fraction, ...], ...], ...],
    dict[str, Any],
]:
    q007k_cycle = q007k_artifact["cycle"]
    output_support = {
        tuple(wave) for wave in q007k_cycle["enumeration"]["output_wave_support"]
    }
    output_support.update(q007k.q007j.REPRESENTATIVE_WAVES)
    symbols = {
        wave: rational_fourier_symbol(wave, trig, collision)
        for wave in output_support
    }
    mode_enclosures, mode_reconstruction = q007k._reconstruct_mode_enclosures(
        q007j_artifact,
        modes,
        lookup,
        symbols,
    )
    moments, equilibrium_hessian, exact_identities = (
        q007k._exact_identity_audit(trig, collision)
    )
    hessian_centers, reduced_centers, _waves, pair_metadata = (
        _complex_coefficients(modes, lookup, SIZE, OMEGA, ETA)
    )
    artifact_records = {
        record["pair_identifier"]: record
        for record in q007k_cycle["krawczyk_certification"]["records"]
    }

    dimension = len(modes)
    hessian_boxes: list[list[tuple[ComplexRationalInterval, ...] | None]] = [
        [None for _ in range(dimension)] for _ in range(dimension)
    ]
    reduced_outputs: dict[
        tuple[int, int],
        tuple[tuple[int, ComplexRationalInterval], ...],
    ] = {}
    pair_output_waves = {}
    digest_mismatches = 0
    metadata_mismatches = 0
    included_count = 0
    maximum_hessian_width = Fraction(0)
    maximum_reduced_width = Fraction(0)
    maximum_hessian_absolute_upper = Fraction(0)
    maximum_reduced_absolute_upper = Fraction(0)
    proof_records = []

    pair_indices = combinations_with_replacement(range(dimension), 2)
    for (left_index, right_index), metadata in zip(
        pair_indices,
        pair_metadata,
        strict=True,
    ):
        output_wave = tuple(metadata["output_wave_index"])
        output_kind = metadata["output_kind"]
        left = mode_enclosures[left_index]
        right = mode_enclosures[right_index]
        forcing = q007k._quadratic_forcing(
            left,
            right,
            output_wave,
            moments,
            equilibrium_hessian,
            trig,
        )
        interval_operator = q007k._interval_operator(
            output_wave,
            output_kind,
            left,
            right,
            mode_enclosures,
            lookup,
            symbols,
        )
        numeric_operator = q007k._numeric_operator(
            output_wave,
            output_kind,
            left_index,
            right_index,
            modes,
            lookup,
        )
        right_hand_side = q007k._right_hand_side(forcing, output_kind)
        center = q007k._registered_center(
            left_index,
            right_index,
            output_wave,
            output_kind,
            hessian_centers,
            reduced_centers,
            lookup,
        )
        proof = q007k._certify_linear_system(
            interval_operator,
            numeric_operator,
            right_hand_side,
            center,
        )
        included_count += proof.included
        artifact_record = artifact_records.get(metadata["pair_identifier"], {})
        digest_matches = (
            proof.proof_digest
            == artifact_record.get("proof_digest_sha256")
        )
        digest_mismatches += not digest_matches
        metadata_matches = bool(
            artifact_record.get("left_mode") == metadata["left_mode"]
            and artifact_record.get("right_mode") == metadata["right_mode"]
            and artifact_record.get("output_wave_index")
            == list(output_wave)
            and artifact_record.get("output_kind") == output_kind
        )
        metadata_mismatches += not metadata_matches

        hessian_box = tuple(proof.image[:9])
        hessian_boxes[left_index][right_index] = hessian_box
        hessian_boxes[right_index][left_index] = hessian_box
        pair_output_waves[(left_index, right_index)] = output_wave
        pair_output_waves[(right_index, left_index)] = output_wave
        for value in hessian_box:
            maximum_hessian_width = max(
                maximum_hessian_width,
                value.real.width,
                value.imag.width,
            )
            maximum_hessian_absolute_upper = max(
                maximum_hessian_absolute_upper,
                _complex_rectangle_absolute_upper(value),
            )

        entries: tuple[tuple[int, ComplexRationalInterval], ...] = ()
        if output_kind == "internal_selected":
            output_indices = q007k._selected_mode_indices(
                output_wave,
                lookup,
            )
            entries = tuple(
                (index, value)
                for index, value in zip(
                    output_indices,
                    proof.image[9:],
                    strict=True,
                )
            )
            for _index, value in entries:
                maximum_reduced_width = max(
                    maximum_reduced_width,
                    value.real.width,
                    value.imag.width,
                )
                maximum_reduced_absolute_upper = max(
                    maximum_reduced_absolute_upper,
                    _complex_rectangle_absolute_upper(value),
                )
        reduced_outputs[(left_index, right_index)] = entries
        reduced_outputs[(right_index, left_index)] = entries
        proof_records.append(
            {
                "pair_identifier": metadata["pair_identifier"],
                "proof_digest_sha256": proof.proof_digest,
                "artifact_digest_sha256": artifact_record.get(
                    "proof_digest_sha256"
                ),
                "digest_matches": digest_matches,
                "metadata_matches": metadata_matches,
                "included": proof.included,
            }
        )

    if any(value is None for row in hessian_boxes for value in row):
        raise RuntimeError("Q007l did not reconstruct all symmetric H2 boxes")
    frozen_hessian = tuple(
        tuple(value for value in row if value is not None)
        for row in hessian_boxes
    )
    jet = _QuadraticJet(
        hessian=frozen_hessian,
        reduced_outputs=reduced_outputs,
        pair_output_waves=pair_output_waves,
    )
    summary = {
        "q007j_representative_proof_count": mode_reconstruction[
            "representative_system_count"
        ],
        "q007j_proof_digest_mismatch_count": mode_reconstruction[
            "proof_digest_mismatch_count"
        ],
        "transported_mode_count": mode_reconstruction[
            "transported_mode_count"
        ],
        "q007k_artifact_proof_count": len(artifact_records),
        "q007k_reconstructed_proof_count": len(proof_records),
        "q007k_proof_digest_mismatch_count": digest_mismatches,
        "q007k_pair_metadata_mismatch_count": metadata_mismatches,
        "q007k_included_count": included_count,
        "maximum_hessian_component_width": _fraction_record(
            maximum_hessian_width
        ),
        "maximum_reduced_component_width": _fraction_record(
            maximum_reduced_width
        ),
        "maximum_hessian_component_absolute_upper": _fraction_record(
            maximum_hessian_absolute_upper
        ),
        "maximum_reduced_component_absolute_upper": _fraction_record(
            maximum_reduced_absolute_upper
        ),
        "exact_quadratic_identities": exact_identities,
        "proof_records": proof_records,
    }
    return (
        jet,
        mode_enclosures,
        moments,
        equilibrium_hessian,
        summary,
    )


def _local_second_action(
    left_moments: Sequence[ComplexRationalInterval],
    right_moments: Sequence[ComplexRationalInterval],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
) -> tuple[ComplexRationalInterval, ...]:
    result = []
    for population in range(9):
        total = ComplexRationalInterval.zero()
        for left_moment in range(3):
            for right_moment in range(3):
                coefficient = equilibrium_hessian[population][left_moment][
                    right_moment
                ]
                if not coefficient:
                    continue
                product = q007k._rounded_multiply(
                    left_moments[left_moment],
                    right_moments[right_moment],
                )
                total = q007k._rounded_add(
                    total,
                    q007k._rounded_scale(product, coefficient),
                )
        result.append(total)
    return tuple(result)


def _filtered_second_action(
    left_moments: Sequence[ComplexRationalInterval],
    right_moments: Sequence[ComplexRationalInterval],
    phase_factors: Sequence[ComplexRationalInterval],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
) -> tuple[ComplexRationalInterval, ...]:
    local = _local_second_action(
        left_moments,
        right_moments,
        equilibrium_hessian,
    )
    return tuple(
        q007k._rounded_multiply(
            phase,
            q007k._rounded_scale(value, q007k.OMEGA_RATIONAL),
        )
        for phase, value in zip(phase_factors, local, strict=True)
    )


def _filtered_third_action(
    first_moments: Sequence[ComplexRationalInterval],
    second_moments: Sequence[ComplexRationalInterval],
    third_moments: Sequence[ComplexRationalInterval],
    phase_factors: Sequence[ComplexRationalInterval],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
) -> tuple[ComplexRationalInterval, ...]:
    second_third = _local_second_action(
        second_moments,
        third_moments,
        equilibrium_hessian,
    )
    first_third = _local_second_action(
        first_moments,
        third_moments,
        equilibrium_hessian,
    )
    first_second = _local_second_action(
        first_moments,
        second_moments,
        equilibrium_hessian,
    )
    result = []
    for population, phase in enumerate(phase_factors):
        local = ComplexRationalInterval.zero()
        terms = (
            (first_moments[0], second_third[population]),
            (second_moments[0], first_third[population]),
            (third_moments[0], first_second[population]),
        )
        for density, quadratic in terms:
            local = q007k._rounded_add(
                local,
                q007k._rounded_multiply(density, quadratic),
            )
        result.append(
            q007k._rounded_multiply(
                phase,
                q007k._rounded_scale(local, -q007k.OMEGA_RATIONAL),
            )
        )
    return tuple(result)


def _reduced_composition_action(
    indices: tuple[int, int, int],
    quadratic_jet: _QuadraticJet,
    mode_enclosures: dict[int, Any],
) -> tuple[ComplexRationalInterval, ...]:
    first, second, third = indices
    terms = (
        (first, second, third),
        (first, third, second),
        (second, third, first),
    )
    result = [ComplexRationalInterval.zero() for _ in range(9)]
    for left, right, linear_index in terms:
        reduced_entries = quadratic_jet.reduced_outputs[(left, right)]
        if not reduced_entries:
            continue
        contribution = [ComplexRationalInterval.zero() for _ in range(9)]
        for output_index, reduced_value in reduced_entries:
            hessian = quadratic_jet.hessian[output_index][linear_index]
            for population, hessian_value in enumerate(hessian):
                contribution[population] = q007k._rounded_add(
                    contribution[population],
                    q007k._rounded_multiply(
                        hessian_value,
                        reduced_value,
                    ),
                )
        eigenvalue = mode_enclosures[linear_index].eigenvalue
        for population, value in enumerate(contribution):
            result[population] = q007k._rounded_add(
                result[population],
                q007k._rounded_multiply(eigenvalue, value),
            )
    return tuple(result)


def _cubic_forcing(
    indices: tuple[int, int, int],
    mode_moments: dict[int, tuple[ComplexRationalInterval, ...]],
    hessian_moments: dict[
        tuple[int, int],
        tuple[ComplexRationalInterval, ...],
    ],
    phase_factors: Sequence[ComplexRationalInterval],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
    quadratic_jet: _QuadraticJet,
    mode_enclosures: dict[int, Any],
) -> tuple[ComplexRationalInterval, ...]:
    first, second, third = indices
    direct = _filtered_third_action(
        mode_moments[first],
        mode_moments[second],
        mode_moments[third],
        phase_factors,
        equilibrium_hessian,
    )
    mixed_terms = (
        (hessian_moments[(first, second)], mode_moments[third]),
        (hessian_moments[(first, third)], mode_moments[second]),
        (hessian_moments[(second, third)], mode_moments[first]),
    )
    mixed = [ComplexRationalInterval.zero() for _ in range(9)]
    for left_moments, right_moments in mixed_terms:
        action = _filtered_second_action(
            left_moments,
            right_moments,
            phase_factors,
            equilibrium_hessian,
        )
        for population, value in enumerate(action):
            mixed[population] = q007k._rounded_add(
                mixed[population],
                value,
            )
    reduced = _reduced_composition_action(
        indices,
        quadratic_jet,
        mode_enclosures,
    )
    return tuple(
        q007k._rounded_add(
            q007k._rounded_add(direct_value, mixed_value),
            -reduced_value,
        )
        for direct_value, mixed_value, reduced_value in zip(
            direct,
            mixed,
            reduced,
            strict=True,
        )
    )


def _triple_multiplier(
    indices: tuple[int, int, int],
    mode_enclosures: dict[int, Any],
) -> ComplexRationalInterval:
    first = q007k._rounded_multiply(
        mode_enclosures[indices[0]].eigenvalue,
        mode_enclosures[indices[1]].eigenvalue,
    )
    return q007k._rounded_multiply(
        first,
        mode_enclosures[indices[2]].eigenvalue,
    )


def _interval_operator(
    indices: tuple[int, int, int],
    output_wave: WaveIndex,
    output_kind: str,
    mode_enclosures: dict[int, Any],
    lookup: dict[tuple[WaveIndex, str], int],
    symbols: dict[WaveIndex, ComplexIntervalMatrix],
) -> ComplexIntervalMatrix:
    multiplier = _triple_multiplier(indices, mode_enclosures)
    base = [list(row) for row in symbols[output_wave]]
    for diagonal in range(9):
        base[diagonal][diagonal] = q007k._rounded_add(
            base[diagonal][diagonal],
            -multiplier,
        )
    if output_kind != "internal_selected":
        return base

    output_indices = q007k._selected_mode_indices(output_wave, lookup)
    output_modes = tuple(mode_enclosures[index] for index in output_indices)
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
                *(
                    q007k.q007j._complex_conjugate(value)
                    for value in mode.left
                ),
                *(ComplexRationalInterval.zero() for _ in range(3)),
            ]
        )
    return augmented


def _numeric_operator(
    indices: tuple[int, int, int],
    output_wave: WaveIndex,
    output_kind: str,
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
) -> np.ndarray:
    multiplier = (
        modes[indices[0]].eigenvalue
        * modes[indices[1]].eigenvalue
        * modes[indices[2]].eigenvalue
    )
    matrix = filtered_fourier_symbol(
        *wave_vector_from_index(output_wave, SIZE),
        OMEGA,
        ETA,
    )
    base = matrix - multiplier * np.eye(9)
    if output_kind != "internal_selected":
        return np.asarray(base, dtype=np.complex128)

    output_indices = q007k._selected_mode_indices(output_wave, lookup)
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


def _registered_center(
    triple_index: int,
    output_wave: WaveIndex,
    output_kind: str,
    cubic_model: Any,
    lookup: dict[tuple[WaveIndex, str], int],
) -> np.ndarray:
    hessian = np.asarray(
        cubic_model.cubic_coefficients[triple_index],
        dtype=np.complex128,
    )
    if output_kind != "internal_selected":
        return hessian
    output_indices = q007k._selected_mode_indices(output_wave, lookup)
    reduced = np.asarray(
        cubic_model.reduced_cubic_coefficients[
            triple_index,
            list(output_indices),
        ],
        dtype=np.complex128,
    )
    return np.concatenate([hessian, reduced])


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


def _symmetric_variation(
    contraction: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    result = []
    for row in contraction:
        radius = SEARCH_RADIUS * sum(
            (
                value.real.maximum_absolute_value
                + value.imag.maximum_absolute_value
                for value in row
            ),
            Fraction(0),
        )
        rounded = RationalInterval(-radius, radius).rounded_outward(
            INTERVAL_DECIMAL_DIGITS
        )
        result.append([ComplexRationalInterval(rounded, rounded)])
    return result


def _proof_digest_for_boxes(
    boxes: Sequence[ComplexRationalInterval],
    extra: Sequence[Fraction],
) -> str:
    digest = sha256()
    values = []
    for box in boxes:
        values.extend(
            (box.real.lower, box.real.upper, box.imag.lower, box.imag.upper)
        )
    values.extend(extra)
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
    center_values = tuple(complex(value) for value in center)
    center_points = tuple(_complex_point(value) for value in center_values)
    inverse_candidate = np.linalg.inv(numeric_operator)
    preconditioner = _matrix_from_numpy(inverse_candidate)
    point_operator = _matrix_from_numpy(numeric_operator)
    point_inverse_defect = _matrix_infinity_norm_upper(
        q007k._matrix_subtract(
            _identity_matrix(dimension),
            q007k._matrix_multiply(preconditioner, point_operator),
        )
    )
    contraction = q007k._matrix_subtract(
        _identity_matrix(dimension),
        q007k._matrix_multiply(preconditioner, interval_operator),
    )
    contraction_bound = _matrix_infinity_norm_upper(contraction)
    residual = q007k._matrix_subtract(
        q007k._matrix_multiply(
            interval_operator,
            q007k._column(center_points),
        ),
        q007k._column(right_hand_side),
    )
    center_term = q007k._matrix_subtract(
        q007k._column(center_points),
        q007k._matrix_multiply(preconditioner, residual),
    )
    image = q007k._flatten_column(
        q007k._matrix_add(center_term, _symmetric_variation(contraction))
    )
    utilization = _krawczyk_utilization(image, center_values)
    corrections = tuple(
        _complex_rectangle_absolute_upper(value - center_point)
        for value, center_point in zip(image, center_points, strict=True)
    )
    correction = max(corrections)
    hessian_correction = max(corrections[:9])
    reduced_correction = (
        max(corrections[9:]) if len(corrections) > 9 else Fraction(0)
    )
    proof_digest = _proof_digest_for_boxes(
        image,
        (
            utilization,
            point_inverse_defect,
            contraction_bound,
            correction,
            hessian_correction,
            reduced_correction,
        ),
    )
    return _LinearProof(
        image=image,
        utilization=utilization,
        point_inverse_defect=point_inverse_defect,
        contraction_bound=contraction_bound,
        correction_upper=correction,
        hessian_correction_upper=hessian_correction,
        reduced_correction_upper=reduced_correction,
        proof_digest=proof_digest,
    )


def _exact_cubic_identity_audit(
    moments: tuple[tuple[Fraction, ...], ...],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
) -> dict[str, Any]:
    third_tensor = []
    for population in range(9):
        population_tensor = []
        for first in range(3):
            first_matrix = []
            for second in range(3):
                row = []
                for third in range(3):
                    value = -(
                        int(first == 0)
                        * equilibrium_hessian[population][second][third]
                        + int(second == 0)
                        * equilibrium_hessian[population][first][third]
                        + int(third == 0)
                        * equilibrium_hessian[population][first][second]
                    )
                    row.append(value)
                first_matrix.append(tuple(row))
            population_tensor.append(tuple(first_matrix))
        third_tensor.append(tuple(population_tensor))
    third_tensor_frozen = tuple(third_tensor)
    moment_third = tuple(
        tuple(
            tuple(
                tuple(
                    sum(
                        (
                            moments[output][population]
                            * third_tensor_frozen[population][first][second][
                                third
                            ]
                            for population in range(9)
                        ),
                        Fraction(0),
                    )
                    for third in range(3)
                )
                for second in range(3)
            )
            for first in range(3)
        )
        for output in range(3)
    )
    tensor_values = [
        value
        for population in third_tensor_frozen
        for matrix in population
        for row in matrix
        for value in row
    ]
    moment_values = [
        value
        for tensor in moment_third
        for matrix in tensor
        for row in matrix
        for value in row
    ]
    return {
        "third_derivative_tensor_sha256": q007k._proof_digest(tensor_values),
        "moment_third_derivative_sha256": q007k._proof_digest(
            moment_values
        ),
        "third_derivative_entry_count": len(tensor_values),
        "moment_third_derivative_entry_count": len(moment_values),
        "moment_third_derivative_all_zero": all(
            value == 0 for value in moment_values
        ),
    }


def _triple_correspondence(
    observed: Sequence[dict[str, Any]],
    artifact: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    fields = (
        "triple_identifier",
        "input_indices",
        "input_modes",
        "input_wave_indices",
        "output_wave_index",
        "output_kind",
        "permutation_multiplicity",
    )
    mismatches = []
    for index, (observed_record, artifact_record) in enumerate(
        zip(observed, artifact, strict=False)
    ):
        fields_mismatched = [
            field
            for field in fields
            if observed_record.get(field) != artifact_record.get(field)
        ]
        if fields_mismatched:
            mismatches.append(
                {
                    "index": index,
                    "fields": fields_mismatched,
                }
            )
    length_matches = len(observed) == len(artifact)
    return {
        "observed_triple_count": len(observed),
        "artifact_triple_count": len(artifact),
        "length_matches": length_matches,
        "mismatch_count": len(mismatches)
        + (0 if length_matches else abs(len(observed) - len(artifact))),
        "mismatch_records": mismatches,
    }


def run_cubic_jet_bridge_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Run the sealed Q007l rational cubic-jet certification."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007b, q007j_artifact, q007k_artifact, input_records = (
        _load_registered_inputs(directory)
    )
    cubic_model, coefficient_reproduction = _reproduce_q007b_model(q007b)
    modes = cubic_model.modes
    lookup = cubic_model.lookup
    artifact_triples = q007b["cycle"]["coefficient_construction"][
        "triple_records"
    ]
    triple_correspondence = _triple_correspondence(
        cubic_model.coefficient_records,
        artifact_triples,
    )

    pi_interval = machin_pi_interval()
    trig = trigonometric_intervals(pi_interval)
    collision = rational_collision_symbol()
    (
        quadratic_jet,
        mode_enclosures,
        moments,
        equilibrium_hessian,
        quadratic_reconstruction,
    ) = _reconstruct_quadratic_jet(
        q007j_artifact,
        q007k_artifact,
        modes,
        lookup,
        trig,
        collision,
    )
    cubic_identities = _exact_cubic_identity_audit(
        moments,
        equilibrium_hessian,
    )

    output_support = tuple(
        sorted(
            {
                tuple(int(value) for value in wave)
                for wave in cubic_model.output_waves
            }
        )
    )
    symbols = {
        wave: rational_fourier_symbol(wave, trig, collision)
        for wave in output_support
    }
    phase_factors = {
        wave: q007k._filter_phase_factors(wave, trig)
        for wave in output_support
    }
    mode_moments = {
        index: q007k._mode_moments(moments, mode_enclosures[index].right)
        for index in range(len(modes))
    }
    hessian_moments = {
        (left, right): q007k._mode_moments(
            moments,
            quadratic_jet.hessian[left][right],
        )
        for left in range(len(modes))
        for right in range(len(modes))
    }

    maximum_trigonometric_width = max(
        max(sine.width, cosine.width) for sine, cosine in trig.values()
    )
    maximum_symbol_width = max(
        max(value.real.width, value.imag.width)
        for matrix in symbols.values()
        for row in matrix
        for value in row
    )
    proof_records = []
    proofs: list[_LinearProof] = []
    kind_counts = {
        "zero_wave_kinetic": 0,
        "internal_selected": 0,
        "external": 0,
    }
    zero_wave_separations = []
    zero_wave_selection_chain_count = 0
    zero_wave_reduced_term_count = 0
    graph_gauge_inclusion_count = 0
    singular_system_count = 0
    unassigned_system_count = 0
    complex_unknown_count = 0
    maximum_correction = Fraction(-1)
    maximum_correction_triple = None
    maximum_forcing_center_difference = Fraction(0)

    triples = tuple(
        tuple(int(value) for value in triple)
        for triple in cubic_model.triple_indices
    )
    for triple_index, (indices, metadata) in enumerate(
        zip(triples, cubic_model.coefficient_records, strict=True)
    ):
        output_wave = tuple(metadata["output_wave_index"])
        output_kind = metadata["output_kind"]
        kind_counts[output_kind] += 1
        forcing = _cubic_forcing(
            indices,
            mode_moments,
            hessian_moments,
            phase_factors[output_wave],
            equilibrium_hessian,
            quadratic_jet,
            mode_enclosures,
        )
        registered_forcing = cubic_model.forcing_coefficients[triple_index]
        for value, center_value in zip(
            forcing,
            registered_forcing,
            strict=True,
        ):
            maximum_forcing_center_difference = max(
                maximum_forcing_center_difference,
                _complex_rectangle_absolute_upper(
                    value - _complex_point(center_value)
                ),
            )

        interval_operator = _interval_operator(
            indices,
            output_wave,
            output_kind,
            mode_enclosures,
            lookup,
            symbols,
        )
        numeric_operator = _numeric_operator(
            indices,
            output_wave,
            output_kind,
            modes,
            lookup,
        )
        right_hand_side = q007k._right_hand_side(forcing, output_kind)
        center = _registered_center(
            triple_index,
            output_wave,
            output_kind,
            cubic_model,
            lookup,
        )
        complex_unknown_count += len(center)
        if len(interval_operator) != len(center):
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
        selection_chain_passed = None
        reduced_term_count = 0
        if output_wave == (0, 0):
            product_separation = q007k.q007j._complex_absolute_bounds(
                ComplexRationalInterval.point(1)
                - _triple_multiplier(indices, mode_enclosures)
            ).lower
            zero_wave_separations.append(product_separation)
            first, second, third = indices
            terms = (
                (first, second, third),
                (first, third, second),
                (second, third, first),
            )
            selection_chain_passed = True
            for left, right, linear_index in terms:
                for output_index, _value in quadratic_jet.reduced_outputs[
                    (left, right)
                ]:
                    reduced_term_count += 1
                    if quadratic_jet.pair_output_waves[
                        (output_index, linear_index)
                    ] != (0, 0):
                        selection_chain_passed = False
            zero_wave_reduced_term_count += reduced_term_count
            zero_wave_selection_chain_count += bool(selection_chain_passed)

        if proof.correction_upper > maximum_correction:
            maximum_correction = proof.correction_upper
            maximum_correction_triple = metadata["triple_identifier"]
        proof_records.append(
            {
                "triple_index": triple_index,
                "triple_identifier": metadata["triple_identifier"],
                "input_modes": metadata["input_modes"],
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
                "zero_wave_selection_chain_passed": selection_chain_passed,
                "zero_wave_reduced_term_count": reduced_term_count,
                "proof_digest_sha256": proof.proof_digest,
            }
        )

    if not proofs:
        maximum_correction = Fraction(1)
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
        "triple_count": len(triples),
        "kind_counts": kind_counts,
        "output_wave_support_count": len(output_support),
        "output_wave_support": [list(wave) for wave in output_support],
        "complex_unknown_count": complex_unknown_count,
        "assigned_system_count": len(proofs),
        "singular_system_count": singular_system_count,
        "unassigned_system_count": unassigned_system_count,
    }
    structural_conservation = {
        "quadratic_moment_hessian_all_zero": quadratic_reconstruction[
            "exact_quadratic_identities"
        ]["moment_hessian_all_zero"],
        "zero_wave_moment_symbol_exact": quadratic_reconstruction[
            "exact_quadratic_identities"
        ]["zero_wave_moment_symbol_exact"],
        **cubic_identities,
        "zero_wave_triple_count": len(zero_wave_separations),
        "zero_wave_selection_chain_count": zero_wave_selection_chain_count,
        "zero_wave_reduced_composition_term_count": (
            zero_wave_reduced_term_count
        ),
        "structural_fixed_leaf_count": (
            zero_wave_selection_chain_count
            if quadratic_reconstruction["exact_quadratic_identities"][
                "moment_hessian_all_zero"
            ]
            and cubic_identities["moment_third_derivative_all_zero"]
            else 0
        ),
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
            maximum_correction
        ),
        "maximum_hessian_correction_upper": _fraction_record(
            maximum_hessian_correction
        ),
        "maximum_reduced_correction_upper": _fraction_record(
            maximum_reduced_correction
        ),
        "maximum_correction_triple_identifier": maximum_correction_triple,
        "maximum_registered_forcing_center_difference_upper": (
            _fraction_record(maximum_forcing_center_difference)
        ),
        "zero_wave_product_separation_count": len(zero_wave_separations),
        "minimum_zero_wave_product_separation_lower": _fraction_record(
            minimum_zero_wave_separation
        ),
        "zero_wave_structural_fixed_leaf_count": structural_conservation[
            "structural_fixed_leaf_count"
        ],
        "internal_graph_gauge_inclusion_count": (
            graph_gauge_inclusion_count
        ),
        "records": proof_records,
    }

    serializable_sections = {
        "input_artifacts": input_records,
        "coefficient_reproduction": coefficient_reproduction,
        "quadratic_jet_reconstruction": quadratic_reconstruction,
        "triple_correspondence": triple_correspondence,
        "structural_conservation": structural_conservation,
        "interval_construction": interval_construction,
        "enumeration": enumeration,
        "krawczyk_certification": certification,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )

    validity_gates = {
        "registered_inputs_coefficients_and_lower_jet_proofs": {
            "passed": bool(
                all(record["passed"] for record in input_records.values())
                and coefficient_reproduction["matches"]
                and quadratic_reconstruction[
                    "q007j_representative_proof_count"
                ]
                == EXPECTED_Q007J_PROOF_COUNT
                and quadratic_reconstruction[
                    "q007j_proof_digest_mismatch_count"
                ]
                == 0
                and quadratic_reconstruction[
                    "q007k_artifact_proof_count"
                ]
                == EXPECTED_Q007K_PROOF_COUNT
                and quadratic_reconstruction[
                    "q007k_reconstructed_proof_count"
                ]
                == EXPECTED_Q007K_PROOF_COUNT
                and quadratic_reconstruction[
                    "q007k_proof_digest_mismatch_count"
                ]
                == 0
                and quadratic_reconstruction[
                    "q007k_pair_metadata_mismatch_count"
                ]
                == 0
                and quadratic_reconstruction["q007k_included_count"]
                == EXPECTED_Q007K_PROOF_COUNT
            ),
            "threshold": (
                "fixed Q007b/Q007k artifacts and Q007k runner; five cubic "
                "coefficient hashes; all 12 eigenpair and 300 quadratic "
                "proof digests match"
            ),
            "value": {
                "inputs": {
                    name: record["passed"]
                    for name, record in input_records.items()
                },
                "coefficient_hashes_match": coefficient_reproduction[
                    "matches"
                ],
                "q007j_digest_mismatches": quadratic_reconstruction[
                    "q007j_proof_digest_mismatch_count"
                ],
                "q007k_digest_mismatches": quadratic_reconstruction[
                    "q007k_proof_digest_mismatch_count"
                ],
            },
        },
        "registered_triple_enumeration": {
            "passed": bool(
                enumeration["triple_count"] == EXPECTED_TRIPLE_COUNT
                and kind_counts["zero_wave_kinetic"]
                == EXPECTED_ZERO_WAVE_COUNT
                and kind_counts["internal_selected"] == EXPECTED_INTERNAL_COUNT
                and kind_counts["external"] == EXPECTED_EXTERNAL_COUNT
                and enumeration["output_wave_support_count"]
                == EXPECTED_OUTPUT_SUPPORT_COUNT
                and complex_unknown_count == EXPECTED_COMPLEX_UNKNOWN_COUNT
            ),
            "threshold": (
                "2600 = 108 zero + 1044 internal + 1448 external triples, "
                "49 output waves, 26532 complex unknowns"
            ),
            "value": enumeration,
        },
        "exact_cubic_forcing_and_conservation_structure": {
            "passed": bool(
                structural_conservation["quadratic_moment_hessian_all_zero"]
                and structural_conservation["zero_wave_moment_symbol_exact"]
                and structural_conservation[
                    "moment_third_derivative_all_zero"
                ]
                and structural_conservation["structural_fixed_leaf_count"]
                == EXPECTED_ZERO_WAVE_COUNT
            ),
            "threshold": (
                "exact D2/D3 moment identities and all 108 zero-wave "
                "quadratic selection-rule chains"
            ),
            "value": structural_conservation,
        },
        "rational_interval_construction": {
            "passed": bool(
                INTERVAL_DECIMAL_DIGITS == 140
                and pi_interval.width <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_trigonometric_width
                <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_symbol_width <= MAXIMUM_SYMBOL_ENTRY_WIDTH
                and len(proofs) == EXPECTED_TRIPLE_COUNT
                and maximum_point_inverse_defect < 1
            ),
            "threshold": (
                "140-digit outward rounding, pi/trig <=1e-120, symbol "
                "<=1e-110, 2600 point inverse defects <1"
            ),
            "value": interval_construction,
        },
        "triple_correspondence_and_strict_json": {
            "passed": bool(
                triple_correspondence["length_matches"]
                and triple_correspondence["mismatch_count"] == 0
                and finite_strict_json
            ),
            "threshold": (
                "all triple identifiers/input modes/output waves/kinds match "
                "Q007b and all summaries are finite strict JSON"
            ),
            "value": {
                "triple_mismatch_count": triple_correspondence[
                    "mismatch_count"
                ],
                "finite_strict_json": finite_strict_json,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    hypothesis_gates = {
        "all_two_thousand_six_hundred_krawczyk_inclusions": {
            "passed": bool(
                included_count == EXPECTED_TRIPLE_COUNT
                and maximum_utilization <= MAXIMUM_KRAWCZYK_UTILIZATION
            ),
            "threshold": (
                "2600 strict inclusions and maximum utilization <=1e-2"
            ),
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
        "registered_cubic_coefficient_correction": {
            "passed": bool(
                maximum_correction <= MAXIMUM_REGISTERED_CORRECTION
            ),
            "threshold": (
                "maximum componentwise exact-root correction to registered "
                "complex H3/R3 <=1e-5"
            ),
            "value": {
                "maximum_correction": float(maximum_correction),
                "maximum_hessian_correction": float(
                    maximum_hessian_correction
                ),
                "maximum_reduced_correction": float(
                    maximum_reduced_correction
                ),
                "witness_triple_identifier": maximum_correction_triple,
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
                "108 positive zero-wave product separations and structural "
                "fixed-leaf solutions; 1044 augmented graph-gauge inclusions"
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
        scientific_classification = "registered cubic-jet bridge audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        scientific_classification = (
            "registered Q007b cubic coefficients identify the "
            "theorem-manifold graph-gauge cubic jet"
        )
    else:
        outcome = "not_certified"
        scientific_classification = (
            "registered cubic-jet bridge not certified"
        )

    return {
        "question": (
            "Do the 2600 registered Q007b complex H3/R3 coefficients "
            "enclose the unique exact graph-gauge cubic jet of the theorem "
            "manifold?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "mode_order": list(MODE_ORDER),
            "search_box_component_radius": _fraction_record(SEARCH_RADIUS),
            "outward_rounding_decimal_digits": INTERVAL_DECIMAL_DIGITS,
        },
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": scientific_classification,
        "claim_boundary": (
            "This identifies only the degree-three graph-gauge Taylor jet "
            "of the local analytic theorem manifold on the fixed 17x17 "
            "conservation leaf. It does not change Q007b's finite-amplitude "
            "performance rejection and does not certify quartic "
            "coefficients, an explicit neighborhood radius, finite-ball "
            "normal attraction, grid uniformity, or a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007b_finite_amplitude_rejection_changed": False,
            "q007i_theorem_acceptance_changed": False,
            "q007j_linear_eigencoordinate_acceptance_changed": False,
            "q007k_quadratic_jet_acceptance_changed": False,
            "q007h_independent_preconditioner_inconclusive_changed": False,
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister a separate Q007m degree-four bridge; "
            "keep the explicit local radius in a later gate."
        ),
    }


def run_q007l_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_cubic_jet_bridge_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational graph-gauge cubic-jet bridge",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": 24,
            "unordered_triple_count": EXPECTED_TRIPLE_COUNT,
            "complex_unknown_count": EXPECTED_COMPLEX_UNKNOWN_COUNT,
            "claim": (
                "degree-three Taylor-jet identification only; no quartic, "
                "explicit-radius, finite-ball, grid-uniform, or continuum "
                "claim"
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
    result = run_q007l_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
