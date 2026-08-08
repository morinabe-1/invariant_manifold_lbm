"""Sealed Q007m rational quartic-jet bridge.

NumPy supplies only registered quartic coefficient centers and inverse
candidates. Exact rational rectangles enclose every lower jet, quartic
forcing, homological operator, and Krawczyk image.
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
from itertools import combinations, combinations_with_replacement
from pathlib import Path
from typing import Any

import numpy as np

import research.q007k_quadratic_jet_bridge as q007k
import research.q007l_cubic_jet_bridge as q007l
from ttim_lbm.checkerboard_filter import filtered_fourier_symbol
from ttim_lbm.nonresonance import wave_vector_from_index
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.quartic_chart import build_full2d_quartic_model
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

Q007C1_ARTIFACT = "q007c1_quartic_continuation.json"
Q007J_ARTIFACT = "q007j_eigencoordinate_bridge.json"
Q007K_ARTIFACT = "q007k_quadratic_jet_bridge.json"
Q007L_ARTIFACT = "q007l_cubic_jet_bridge.json"

REGISTERED_INPUT_SHA256 = {
    "q007c1": "680dddad3d84a8ea6fa030fb6e2ed7001e3bd0b4c55c79464a76daccef5ecdbc",
    "q007l": "aa0e572b43ed4f5544e2b8ead9d01c13bc08c47f40ec8963bcd37a1b51fc1bbd",
}
REGISTERED_Q007L_RUNNER_SHA256 = (
    "bb2be852c5413ceb2d27abd4f48db36ed2045ed79f2330e45ae89818067d33a4"
)
REGISTERED_COEFFICIENT_HASHES = {
    "quartet_indices_sha256": (
        "968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16"
    ),
    "output_waves_sha256": (
        "9f9720e1114cc489ef7bbca81562e7d4cf211999e8d4a4958c06c02ee0df1fe8"
    ),
    "chart_coefficients_sha256": (
        "9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b"
    ),
    "reduced_coefficients_sha256": (
        "061cd66caf83850a45eeec05ed0f62fafb748a3076d7a6eb591bc69be2e008f7"
    ),
    "forcing_coefficients_sha256": (
        "6ab2337ea60b87dbe404e1aeb6b9c090fa8f950d43815966e0933879901b8eef"
    ),
}

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SEARCH_RADIUS = Fraction(1)
MAXIMUM_KRAWCZYK_UTILIZATION = Fraction(1, 10**2)
MAXIMUM_REGISTERED_CORRECTION = Fraction(1, 10**2)
EXPECTED_QUARTET_COUNT = 17_550
EXPECTED_ZERO_WAVE_COUNT = 846
EXPECTED_INTERNAL_COUNT = 4_536
EXPECTED_EXTERNAL_COUNT = 12_168
EXPECTED_OUTPUT_SUPPORT_COUNT = 81
EXPECTED_MULTIPLICITY_SUM = 24**4
EXPECTED_COMPLEX_UNKNOWN_COUNT = 171_558
EXPECTED_Q007J_PROOF_COUNT = 12
EXPECTED_Q007K_PROOF_COUNT = 300
EXPECTED_Q007L_PROOF_COUNT = 2_600

_PAIR_PARTITIONS = (
    ((0, 1), (2, 3)),
    ((0, 2), (1, 3)),
    ((0, 3), (1, 2)),
)


@dataclass(frozen=True, slots=True)
class _LowerJets:
    hessian: dict[
        tuple[int, int],
        tuple[ComplexRationalInterval, ...],
    ]
    reduced_hessian: dict[
        tuple[int, int],
        tuple[tuple[int, ComplexRationalInterval], ...],
    ]
    pair_output_waves: dict[tuple[int, int], WaveIndex]
    cubic: dict[
        tuple[int, int, int],
        tuple[ComplexRationalInterval, ...],
    ]
    reduced_cubic: dict[
        tuple[int, int, int],
        tuple[tuple[int, ComplexRationalInterval], ...],
    ]
    triple_output_waves: dict[tuple[int, int, int], WaveIndex]


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
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    q007c1, q007c1_record = _artifact_record(
        artifact_directory / Q007C1_ARTIFACT,
        REGISTERED_INPUT_SHA256["q007c1"],
    )
    q007l_artifact, q007l_record = _artifact_record(
        artifact_directory / Q007L_ARTIFACT,
        REGISTERED_INPUT_SHA256["q007l"],
    )

    q007c1_scope = q007c1.get("mathematical_scope", {})
    q007c1_cycle = q007c1.get("cycle", {})
    failed_q007c1_hypotheses = sorted(
        name
        for name, gate in q007c1_cycle.get("hypothesis_gates", {}).items()
        if not gate.get("passed", False)
    )
    q007c1_record.update(
        {
            "scope_match": bool(
                q007c1_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q007c1_scope.get("omega", math.nan)) == OMEGA
                and float(q007c1_scope.get("eta", math.nan)) == ETA
                and q007c1_scope.get("real_reduced_dimension") == 24
                and q007c1_scope.get("unordered_quartic_tuple_count")
                == EXPECTED_QUARTET_COUNT
            ),
            "all_validity_gates_passed": bool(
                len(q007c1_cycle.get("validity_gates", {})) == 8
                and all(
                    gate.get("passed", False)
                    for gate in q007c1_cycle["validity_gates"].values()
                )
            ),
            "failed_hypothesis_gates": failed_q007c1_hypotheses,
        }
    )
    q007c1_record["passed"] = bool(
        q007c1_record["sha256_matches"]
        and q007c1_record["source_match"]
        and q007c1.get("study_gate") == "passed"
        and q007c1.get("scientific_outcome") == "rejected"
        and q007c1_record["scope_match"]
        and q007c1_record["all_validity_gates_passed"]
        and failed_q007c1_hypotheses
        == ["held_out_directional_shadowing_ratios"]
    )

    q007l_scope = q007l_artifact.get("mathematical_scope", {})
    q007l_cycle = q007l_artifact.get("cycle", {})
    q007l_runner_sha = _file_sha256(Path(q007l.__file__).resolve())
    q007l_record.update(
        {
            "scope_match": bool(
                q007l_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q007l_scope.get("omega", math.nan)) == OMEGA
                and float(q007l_scope.get("eta", math.nan)) == ETA
                and q007l_scope.get("selected_real_dimension") == 24
                and q007l_scope.get("unordered_triple_count")
                == EXPECTED_Q007L_PROOF_COUNT
            ),
            "all_validity_gates_passed": bool(
                len(q007l_cycle.get("validity_gates", {})) == 5
                and all(
                    gate.get("passed", False)
                    for gate in q007l_cycle["validity_gates"].values()
                )
            ),
            "all_hypothesis_gates_passed": bool(
                len(q007l_cycle.get("hypothesis_gates", {})) == 4
                and all(
                    gate.get("passed", False)
                    for gate in q007l_cycle["hypothesis_gates"].values()
                )
            ),
            "registered_runner_sha256": REGISTERED_Q007L_RUNNER_SHA256,
            "artifact_runner_sha256": q007l_artifact.get(
                "runner_source", {}
            ).get("sha256"),
            "observed_runner_sha256": q007l_runner_sha,
            "runner_sha_matches": bool(
                q007l_runner_sha == REGISTERED_Q007L_RUNNER_SHA256
                and q007l_artifact.get("runner_source", {}).get("sha256")
                == REGISTERED_Q007L_RUNNER_SHA256
            ),
        }
    )
    q007l_record["passed"] = bool(
        q007l_record["sha256_matches"]
        and q007l_record["source_match"]
        and q007l_artifact.get("study_gate") == "passed"
        and q007l_artifact.get("scientific_outcome") == "accepted"
        and q007l_record["scope_match"]
        and q007l_record["all_validity_gates_passed"]
        and q007l_record["all_hypothesis_gates_passed"]
        and q007l_record["runner_sha_matches"]
    )
    return q007c1, q007l_artifact, {
        "q007c1": q007c1_record,
        "q007l": q007l_record,
    }


def _reproduce_q007c1_model(
    q007c1: dict[str, Any],
) -> tuple[Any, dict[str, Any]]:
    model = build_full2d_quartic_model()
    observed = model.coefficient_hashes()
    artifact = q007c1["cycle"]["coefficient_construction"][
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


def _capture_lower_proofs(
    artifact_directory: Path,
) -> tuple[list[Any], list[Any], dict[str, Any]]:
    pair_proofs: list[Any] = []
    cubic_proofs: list[Any] = []
    original_pair_certifier = q007k._certify_linear_system
    original_cubic_certifier = q007l._certify_linear_system

    def capture_pair(*args: Any, **kwargs: Any) -> Any:
        proof = original_pair_certifier(*args, **kwargs)
        pair_proofs.append(proof)
        return proof

    def capture_cubic(*args: Any, **kwargs: Any) -> Any:
        proof = original_cubic_certifier(*args, **kwargs)
        cubic_proofs.append(proof)
        return proof

    q007k._certify_linear_system = capture_pair
    q007l._certify_linear_system = capture_cubic
    try:
        audit = q007l.run_cubic_jet_bridge_audit(artifact_directory)
    finally:
        q007k._certify_linear_system = original_pair_certifier
        q007l._certify_linear_system = original_cubic_certifier

    if len(pair_proofs) != EXPECTED_Q007K_PROOF_COUNT:
        raise RuntimeError("Q007m did not capture all Q007k proof images")
    if len(cubic_proofs) != EXPECTED_Q007L_PROOF_COUNT:
        raise RuntimeError("Q007m did not capture all Q007l proof images")
    return pair_proofs, cubic_proofs, audit


def _sorted_pair(first: int, second: int) -> tuple[int, int]:
    return (first, second) if first <= second else (second, first)


def _sorted_triple(
    first: int,
    second: int,
    third: int,
) -> tuple[int, int, int]:
    return tuple(sorted((first, second, third)))


def _proof_box_summary(
    pair_proofs: Sequence[Any],
    cubic_proofs: Sequence[Any],
) -> dict[str, Any]:
    maxima = {
        "h2_width": Fraction(0),
        "r2_width": Fraction(0),
        "h3_width": Fraction(0),
        "r3_width": Fraction(0),
        "h2_absolute_upper": Fraction(0),
        "r2_absolute_upper": Fraction(0),
        "h3_absolute_upper": Fraction(0),
        "r3_absolute_upper": Fraction(0),
    }
    for degree, proofs in ((2, pair_proofs), (3, cubic_proofs)):
        for proof in proofs:
            for component, value in enumerate(proof.image):
                kind = "h" if component < 9 else "r"
                width_key = f"{kind}{degree}_width"
                upper_key = f"{kind}{degree}_absolute_upper"
                maxima[width_key] = max(
                    maxima[width_key],
                    value.real.width,
                    value.imag.width,
                )
                maxima[upper_key] = max(
                    maxima[upper_key],
                    _complex_rectangle_absolute_upper(value),
                )
    return {
        "maximum_h2_component_width": _fraction_record(maxima["h2_width"]),
        "maximum_r2_component_width": _fraction_record(maxima["r2_width"]),
        "maximum_h3_component_width": _fraction_record(maxima["h3_width"]),
        "maximum_r3_component_width": _fraction_record(maxima["r3_width"]),
        "maximum_h2_component_absolute_upper": _fraction_record(
            maxima["h2_absolute_upper"]
        ),
        "maximum_r2_component_absolute_upper": _fraction_record(
            maxima["r2_absolute_upper"]
        ),
        "maximum_h3_component_absolute_upper": _fraction_record(
            maxima["h3_absolute_upper"]
        ),
        "maximum_r3_component_absolute_upper": _fraction_record(
            maxima["r3_absolute_upper"]
        ),
    }


def _reconstruct_lower_jets(
    artifact_directory: Path,
    q007l_artifact: dict[str, Any],
    quartic_model: Any,
    symbols: dict[WaveIndex, ComplexIntervalMatrix],
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
    collision: tuple[tuple[Fraction, ...], ...],
) -> tuple[
    _LowerJets,
    dict[int, Any],
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[tuple[Fraction, ...], ...], ...],
    dict[str, Any],
]:
    pair_proofs, cubic_proofs, lower_audit = _capture_lower_proofs(
        artifact_directory
    )
    q007j_artifact = json.loads(
        (artifact_directory / Q007J_ARTIFACT).read_text(encoding="utf-8")
    )
    q007k_artifact = json.loads(
        (artifact_directory / Q007K_ARTIFACT).read_text(encoding="utf-8")
    )
    modes = quartic_model.modes
    lookup = quartic_model.lookup
    mode_enclosures, mode_reconstruction = q007k._reconstruct_mode_enclosures(
        q007j_artifact,
        modes,
        lookup,
        symbols,
    )
    moments, equilibrium_hessian, exact_identities = (
        q007k._exact_identity_audit(trig, collision)
    )

    hessian = {}
    reduced_hessian = {}
    pair_output_waves = {}
    pair_digest_mismatches = 0
    pair_metadata_mismatches = 0
    q007k_records = q007k_artifact["cycle"]["krawczyk_certification"][
        "records"
    ]
    pair_indices = combinations_with_replacement(range(len(modes)), 2)
    for (left, right), metadata, proof, artifact_record in zip(
        pair_indices,
        quartic_model.cubic.quadratic.pair_records,
        pair_proofs,
        q007k_records,
        strict=True,
    ):
        key = _sorted_pair(left, right)
        output_wave = tuple(int(value) for value in metadata["output_wave_index"])
        output_kind = metadata["output_kind"]
        hessian[key] = tuple(proof.image[:9])
        if output_kind == "internal_selected":
            output_indices = q007k._selected_mode_indices(output_wave, lookup)
            entries = tuple(zip(output_indices, proof.image[9:], strict=True))
        else:
            entries = ()
        reduced_hessian[key] = entries
        pair_output_waves[key] = output_wave
        pair_digest_mismatches += bool(
            proof.proof_digest != artifact_record["proof_digest_sha256"]
        )
        pair_metadata_mismatches += bool(
            metadata["pair_identifier"] != artifact_record["pair_identifier"]
            or metadata["left_mode"] != artifact_record["left_mode"]
            or metadata["right_mode"] != artifact_record["right_mode"]
            or list(output_wave) != artifact_record["output_wave_index"]
            or output_kind != artifact_record["output_kind"]
        )

    cubic = {}
    reduced_cubic = {}
    triple_output_waves = {}
    cubic_digest_mismatches = 0
    cubic_metadata_mismatches = 0
    q007l_records = q007l_artifact["cycle"]["krawczyk_certification"][
        "records"
    ]
    for metadata, proof, artifact_record in zip(
        quartic_model.cubic.coefficient_records,
        cubic_proofs,
        q007l_records,
        strict=True,
    ):
        key = _sorted_triple(
            *(int(value) for value in metadata["input_indices"])
        )
        output_wave = tuple(int(value) for value in metadata["output_wave_index"])
        output_kind = metadata["output_kind"]
        cubic[key] = tuple(proof.image[:9])
        if output_kind == "internal_selected":
            output_indices = q007k._selected_mode_indices(output_wave, lookup)
            entries = tuple(zip(output_indices, proof.image[9:], strict=True))
        else:
            entries = ()
        reduced_cubic[key] = entries
        triple_output_waves[key] = output_wave
        cubic_digest_mismatches += bool(
            proof.proof_digest != artifact_record["proof_digest_sha256"]
        )
        cubic_metadata_mismatches += bool(
            metadata["triple_identifier"]
            != artifact_record["triple_identifier"]
            or metadata["input_modes"] != artifact_record["input_modes"]
            or list(output_wave) != artifact_record["output_wave_index"]
            or output_kind != artifact_record["output_kind"]
        )

    lower_jets = _LowerJets(
        hessian=hessian,
        reduced_hessian=reduced_hessian,
        pair_output_waves=pair_output_waves,
        cubic=cubic,
        reduced_cubic=reduced_cubic,
        triple_output_waves=triple_output_waves,
    )
    summary = {
        "q007l_recomputed_study_validity": lower_audit["study_validity"],
        "q007l_recomputed_hypothesis_outcome": lower_audit[
            "hypothesis_outcome"
        ],
        "q007l_all_validity_gates_passed": all(
            gate["passed"] for gate in lower_audit["validity_gates"].values()
        ),
        "q007l_all_hypothesis_gates_passed": all(
            gate["passed"] for gate in lower_audit["hypothesis_gates"].values()
        ),
        "q007j_representative_proof_count": mode_reconstruction[
            "representative_system_count"
        ],
        "q007j_proof_digest_mismatch_count": mode_reconstruction[
            "proof_digest_mismatch_count"
        ],
        "transported_mode_count": mode_reconstruction["transported_mode_count"],
        "q007k_reconstructed_proof_count": len(pair_proofs),
        "q007k_proof_digest_mismatch_count": pair_digest_mismatches,
        "q007k_pair_metadata_mismatch_count": pair_metadata_mismatches,
        "q007l_reconstructed_proof_count": len(cubic_proofs),
        "q007l_proof_digest_mismatch_count": cubic_digest_mismatches,
        "q007l_triple_metadata_mismatch_count": cubic_metadata_mismatches,
        "exact_quadratic_identities": exact_identities,
        **_proof_box_summary(pair_proofs, cubic_proofs),
    }
    return (
        lower_jets,
        mode_enclosures,
        moments,
        equilibrium_hessian,
        summary,
    )


def _zero_vector() -> list[ComplexRationalInterval]:
    return [ComplexRationalInterval.zero() for _ in range(9)]


def _add_vector_in_place(
    target: list[ComplexRationalInterval],
    values: Sequence[ComplexRationalInterval],
) -> None:
    for index, value in enumerate(values):
        target[index] = q007k._rounded_add(target[index], value)


def _add_scaled_vector_in_place(
    target: list[ComplexRationalInterval],
    values: Sequence[ComplexRationalInterval],
    scalar: ComplexRationalInterval,
) -> None:
    for index, value in enumerate(values):
        target[index] = q007k._rounded_add(
            target[index],
            q007k._rounded_multiply(value, scalar),
        )


def _filtered_fourth_action(
    input_moments: Sequence[Sequence[ComplexRationalInterval]],
    phase_factors: Sequence[ComplexRationalInterval],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
) -> tuple[ComplexRationalInterval, ...]:
    if len(input_moments) != 4:
        raise ValueError("quartic action requires four moment vectors")
    local = _zero_vector()
    for density_positions in combinations(range(4), 2):
        momentum_positions = tuple(
            position
            for position in range(4)
            if position not in density_positions
        )
        density_product = q007k._rounded_multiply(
            input_moments[density_positions[0]][0],
            input_moments[density_positions[1]][0],
        )
        quadratic = q007l._local_second_action(
            input_moments[momentum_positions[0]],
            input_moments[momentum_positions[1]],
            equilibrium_hessian,
        )
        _add_scaled_vector_in_place(local, quadratic, density_product)
    coefficient = 2 * q007k.OMEGA_RATIONAL
    return tuple(
        q007k._rounded_multiply(
            phase,
            q007k._rounded_scale(value, coefficient),
        )
        for phase, value in zip(phase_factors, local, strict=True)
    )


def _reduced_quartic_composition(
    indices: tuple[int, int, int, int],
    lower_jets: _LowerJets,
    mode_enclosures: dict[int, Any],
) -> tuple[ComplexRationalInterval, ...]:
    result = _zero_vector()

    for singleton_position in range(4):
        singleton = indices[singleton_position]
        triple = _sorted_triple(
            *(
                indices[position]
                for position in range(4)
                if position != singleton_position
            )
        )
        contribution = _zero_vector()
        for output_index, reduced_value in lower_jets.reduced_cubic[triple]:
            hessian = lower_jets.hessian[
                _sorted_pair(output_index, singleton)
            ]
            _add_scaled_vector_in_place(
                contribution,
                hessian,
                reduced_value,
            )
        eigenvalue = mode_enclosures[singleton].eigenvalue
        _add_scaled_vector_in_place(result, contribution, eigenvalue)

    for left_positions, right_positions in _PAIR_PARTITIONS:
        left = _sorted_pair(
            indices[left_positions[0]],
            indices[left_positions[1]],
        )
        right = _sorted_pair(
            indices[right_positions[0]],
            indices[right_positions[1]],
        )
        for left_output, left_reduced in lower_jets.reduced_hessian[left]:
            for right_output, right_reduced in lower_jets.reduced_hessian[
                right
            ]:
                product = q007k._rounded_multiply(
                    left_reduced,
                    right_reduced,
                )
                _add_scaled_vector_in_place(
                    result,
                    lower_jets.hessian[
                        _sorted_pair(left_output, right_output)
                    ],
                    product,
                )

    for hessian_positions in combinations(range(4), 2):
        linear_positions = tuple(
            position
            for position in range(4)
            if position not in hessian_positions
        )
        hessian_key = _sorted_pair(
            indices[hessian_positions[0]],
            indices[hessian_positions[1]],
        )
        first_linear = indices[linear_positions[0]]
        second_linear = indices[linear_positions[1]]
        eigenvalue_product = q007k._rounded_multiply(
            mode_enclosures[first_linear].eigenvalue,
            mode_enclosures[second_linear].eigenvalue,
        )
        contribution = _zero_vector()
        for output_index, reduced_value in lower_jets.reduced_hessian[
            hessian_key
        ]:
            cubic = lower_jets.cubic[
                _sorted_triple(
                    output_index,
                    first_linear,
                    second_linear,
                )
            ]
            _add_scaled_vector_in_place(
                contribution,
                cubic,
                reduced_value,
            )
        _add_scaled_vector_in_place(
            result,
            contribution,
            eigenvalue_product,
        )
    return tuple(result)


def _quartic_forcing(
    indices: tuple[int, int, int, int],
    mode_moments: dict[int, tuple[ComplexRationalInterval, ...]],
    hessian_moments: dict[
        tuple[int, int],
        tuple[ComplexRationalInterval, ...],
    ],
    cubic_moments: dict[
        tuple[int, int, int],
        tuple[ComplexRationalInterval, ...],
    ],
    phase_factors: Sequence[ComplexRationalInterval],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
    lower_jets: _LowerJets,
    mode_enclosures: dict[int, Any],
) -> tuple[ComplexRationalInterval, ...]:
    result = list(
        _filtered_fourth_action(
            tuple(mode_moments[index] for index in indices),
            phase_factors,
            equilibrium_hessian,
        )
    )

    for singleton_position in range(4):
        singleton = indices[singleton_position]
        triple = _sorted_triple(
            *(
                indices[position]
                for position in range(4)
                if position != singleton_position
            )
        )
        action = q007l._filtered_second_action(
            cubic_moments[triple],
            mode_moments[singleton],
            phase_factors,
            equilibrium_hessian,
        )
        _add_vector_in_place(result, action)

    for left_positions, right_positions in _PAIR_PARTITIONS:
        left = _sorted_pair(
            indices[left_positions[0]],
            indices[left_positions[1]],
        )
        right = _sorted_pair(
            indices[right_positions[0]],
            indices[right_positions[1]],
        )
        action = q007l._filtered_second_action(
            hessian_moments[left],
            hessian_moments[right],
            phase_factors,
            equilibrium_hessian,
        )
        _add_vector_in_place(result, action)

    for hessian_positions in combinations(range(4), 2):
        linear_positions = tuple(
            position
            for position in range(4)
            if position not in hessian_positions
        )
        hessian_key = _sorted_pair(
            indices[hessian_positions[0]],
            indices[hessian_positions[1]],
        )
        action = q007l._filtered_third_action(
            hessian_moments[hessian_key],
            mode_moments[indices[linear_positions[0]]],
            mode_moments[indices[linear_positions[1]]],
            phase_factors,
            equilibrium_hessian,
        )
        _add_vector_in_place(result, action)

    reduced = _reduced_quartic_composition(
        indices,
        lower_jets,
        mode_enclosures,
    )
    for population, value in enumerate(reduced):
        result[population] = q007k._rounded_add(
            result[population],
            -value,
        )
    return tuple(result)


def _quartet_multiplier(
    indices: tuple[int, int, int, int],
    mode_enclosures: dict[int, Any],
) -> ComplexRationalInterval:
    result = ComplexRationalInterval.point(1)
    for index in indices:
        result = q007k._rounded_multiply(
            result,
            mode_enclosures[index].eigenvalue,
        )
    return result


def _interval_operator(
    indices: tuple[int, int, int, int],
    output_wave: WaveIndex,
    output_kind: str,
    mode_enclosures: dict[int, Any],
    lookup: dict[tuple[WaveIndex, str], int],
    symbols: dict[WaveIndex, ComplexIntervalMatrix],
) -> ComplexIntervalMatrix:
    multiplier = _quartet_multiplier(indices, mode_enclosures)
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
    indices: tuple[int, int, int, int],
    output_wave: WaveIndex,
    output_kind: str,
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
) -> np.ndarray:
    multiplier = complex(math.prod(modes[index].eigenvalue for index in indices))
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
    quartet_index: int,
    output_wave: WaveIndex,
    output_kind: str,
    quartic_model: Any,
    lookup: dict[tuple[WaveIndex, str], int],
) -> np.ndarray:
    hessian = np.asarray(
        quartic_model.quartic_coefficients[quartet_index],
        dtype=np.complex128,
    )
    if output_kind != "internal_selected":
        return hessian
    output_indices = q007k._selected_mode_indices(output_wave, lookup)
    reduced = np.asarray(
        quartic_model.reduced_quartic_coefficients[
            quartet_index,
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
    if numeric_operator.shape != (dimension, dimension):
        raise ValueError("numeric operator and center dimensions differ")
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


def _exact_quartic_identity_audit(
    moments: tuple[tuple[Fraction, ...], ...],
    equilibrium_hessian: tuple[tuple[tuple[Fraction, ...], ...], ...],
) -> dict[str, Any]:
    tensor = []
    for population in range(9):
        population_tensor = []
        for first in range(3):
            first_tensor = []
            for second in range(3):
                second_matrix = []
                for third in range(3):
                    row = []
                    for fourth in range(3):
                        moment_indices = (first, second, third, fourth)
                        value = Fraction(0)
                        for density_positions in combinations(range(4), 2):
                            other = tuple(
                                position
                                for position in range(4)
                                if position not in density_positions
                            )
                            if all(
                                moment_indices[position] == 0
                                for position in density_positions
                            ):
                                value += 2 * equilibrium_hessian[population][
                                    moment_indices[other[0]]
                                ][moment_indices[other[1]]]
                        row.append(value)
                    second_matrix.append(tuple(row))
                first_tensor.append(tuple(second_matrix))
            population_tensor.append(tuple(first_tensor))
        tensor.append(tuple(population_tensor))
    tensor_frozen = tuple(tensor)
    moment_tensor = tuple(
        tuple(
            tuple(
                tuple(
                    tuple(
                        sum(
                            (
                                moments[output][population]
                                * tensor_frozen[population][first][second][
                                    third
                                ][fourth]
                                for population in range(9)
                            ),
                            Fraction(0),
                        )
                        for fourth in range(3)
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
        for population in tensor_frozen
        for first in population
        for second in first
        for third in second
        for value in third
    ]
    moment_values = [
        value
        for output in moment_tensor
        for first in output
        for second in first
        for third in second
        for value in third
    ]
    return {
        "fourth_derivative_tensor_sha256": q007k._proof_digest(tensor_values),
        "moment_fourth_derivative_sha256": q007k._proof_digest(moment_values),
        "fourth_derivative_entry_count": len(tensor_values),
        "moment_fourth_derivative_entry_count": len(moment_values),
        "moment_fourth_derivative_all_zero": all(
            value == 0 for value in moment_values
        ),
    }


def _quartet_correspondence(
    observed: Sequence[dict[str, Any]],
    artifact: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    fields = (
        "quartet_identifier",
        "input_indices",
        "input_modes",
        "output_wave_index",
        "output_kind",
        "permutation_multiplicity",
    )
    length_matches = len(observed) == len(artifact)
    mismatches = []
    for index, (observed_record, artifact_record) in enumerate(
        zip(observed, artifact)
    ):
        failed = [
            field
            for field in fields
            if observed_record.get(field) != artifact_record.get(field)
        ]
        if failed:
            mismatches.append(
                {
                    "quartet_index": index,
                    "failed_fields": failed,
                    "observed_identifier": observed_record.get(
                        "quartet_identifier"
                    ),
                    "artifact_identifier": artifact_record.get(
                        "quartet_identifier"
                    ),
                }
            )
    return {
        "observed_quartet_count": len(observed),
        "artifact_quartet_count": len(artifact),
        "length_matches": length_matches,
        "mismatch_count": len(mismatches)
        + (0 if length_matches else abs(len(observed) - len(artifact))),
        "mismatch_records": mismatches,
    }


def _zero_wave_selection_chain(
    indices: tuple[int, int, int, int],
    lower_jets: _LowerJets,
) -> tuple[bool, int]:
    passed = True
    count = 0
    for singleton_position in range(4):
        singleton = indices[singleton_position]
        triple = _sorted_triple(
            *(
                indices[position]
                for position in range(4)
                if position != singleton_position
            )
        )
        for output_index, _value in lower_jets.reduced_cubic[triple]:
            count += 1
            if lower_jets.pair_output_waves[
                _sorted_pair(output_index, singleton)
            ] != (0, 0):
                passed = False

    for left_positions, right_positions in _PAIR_PARTITIONS:
        left = _sorted_pair(
            indices[left_positions[0]],
            indices[left_positions[1]],
        )
        right = _sorted_pair(
            indices[right_positions[0]],
            indices[right_positions[1]],
        )
        for left_output, _left_value in lower_jets.reduced_hessian[left]:
            for right_output, _right_value in lower_jets.reduced_hessian[
                right
            ]:
                count += 1
                if lower_jets.pair_output_waves[
                    _sorted_pair(left_output, right_output)
                ] != (0, 0):
                    passed = False

    for hessian_positions in combinations(range(4), 2):
        linear_positions = tuple(
            position
            for position in range(4)
            if position not in hessian_positions
        )
        pair = _sorted_pair(
            indices[hessian_positions[0]],
            indices[hessian_positions[1]],
        )
        for output_index, _value in lower_jets.reduced_hessian[pair]:
            count += 1
            if lower_jets.triple_output_waves[
                _sorted_triple(
                    output_index,
                    indices[linear_positions[0]],
                    indices[linear_positions[1]],
                )
            ] != (0, 0):
                passed = False
    return passed, count


def run_quartic_jet_bridge_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Run the sealed Q007m rational quartic-jet certification."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007c1, q007l_artifact, input_records = _load_registered_inputs(directory)
    quartic_model, coefficient_reproduction = _reproduce_q007c1_model(q007c1)
    modes = quartic_model.modes
    lookup = quartic_model.lookup
    artifact_quartets = q007c1["cycle"]["coefficient_construction"][
        "quartet_records"
    ]
    quartet_correspondence = _quartet_correspondence(
        quartic_model.coefficient_records,
        artifact_quartets,
    )

    pi_interval = machin_pi_interval()
    trig = trigonometric_intervals(pi_interval)
    collision = rational_collision_symbol()
    output_support = tuple(
        sorted(
            {
                tuple(int(value) for value in wave)
                for wave in quartic_model.output_waves
            }
            | set(q007k.q007j.REPRESENTATIVE_WAVES)
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
    (
        lower_jets,
        mode_enclosures,
        moments,
        equilibrium_hessian,
        lower_reconstruction,
    ) = _reconstruct_lower_jets(
        directory,
        q007l_artifact,
        quartic_model,
        symbols,
        trig,
        collision,
    )
    cubic_identities = q007l._exact_cubic_identity_audit(
        moments,
        equilibrium_hessian,
    )
    quartic_identities = _exact_quartic_identity_audit(
        moments,
        equilibrium_hessian,
    )

    mode_moments = {
        index: q007k._mode_moments(moments, mode_enclosures[index].right)
        for index in range(len(modes))
    }
    hessian_moments = {
        key: q007k._mode_moments(moments, value)
        for key, value in lower_jets.hessian.items()
    }
    cubic_moments = {
        key: q007k._mode_moments(moments, value)
        for key, value in lower_jets.cubic.items()
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
    maximum_correction_quartet = None
    maximum_forcing_center_difference = Fraction(0)
    multiplicity_sum = 0

    quartets = tuple(
        tuple(int(value) for value in quartet)
        for quartet in quartic_model.quartet_indices
    )
    for quartet_index, (indices, metadata) in enumerate(
        zip(quartets, quartic_model.coefficient_records, strict=True)
    ):
        output_wave = tuple(int(value) for value in metadata["output_wave_index"])
        output_kind = metadata["output_kind"]
        kind_counts[output_kind] += 1
        multiplicity_sum += int(metadata["permutation_multiplicity"])
        forcing = _quartic_forcing(
            indices,
            mode_moments,
            hessian_moments,
            cubic_moments,
            phase_factors[output_wave],
            equilibrium_hessian,
            lower_jets,
            mode_enclosures,
        )
        registered_forcing = quartic_model.forcing_coefficients[quartet_index]
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
            quartet_index,
            output_wave,
            output_kind,
            quartic_model,
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
                - _quartet_multiplier(indices, mode_enclosures)
            ).lower
            zero_wave_separations.append(product_separation)
            selection_chain_passed, reduced_term_count = (
                _zero_wave_selection_chain(indices, lower_jets)
            )
            zero_wave_reduced_term_count += reduced_term_count
            zero_wave_selection_chain_count += bool(selection_chain_passed)

        if proof.correction_upper > maximum_correction:
            maximum_correction = proof.correction_upper
            maximum_correction_quartet = metadata["quartet_identifier"]
        proof_records.append(
            {
                "quartet_index": quartet_index,
                "quartet_identifier": metadata["quartet_identifier"],
                "input_modes": metadata["input_modes"],
                "output_wave_index": list(output_wave),
                "output_kind": output_kind,
                "permutation_multiplicity": metadata[
                    "permutation_multiplicity"
                ],
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
        "quartet_count": len(quartets),
        "kind_counts": kind_counts,
        "permutation_multiplicity_sum": multiplicity_sum,
        "output_wave_support_count": len(
            {tuple(int(value) for value in wave) for wave in quartic_model.output_waves}
        ),
        "output_wave_support": [
            list(wave)
            for wave in sorted(
                {
                    tuple(int(value) for value in wave)
                    for wave in quartic_model.output_waves
                }
            )
        ],
        "complex_unknown_count": complex_unknown_count,
        "assigned_system_count": len(proofs),
        "singular_system_count": singular_system_count,
        "unassigned_system_count": unassigned_system_count,
    }
    structural_conservation = {
        "quadratic_moment_hessian_all_zero": lower_reconstruction[
            "exact_quadratic_identities"
        ]["moment_hessian_all_zero"],
        "zero_wave_moment_symbol_exact": lower_reconstruction[
            "exact_quadratic_identities"
        ]["zero_wave_moment_symbol_exact"],
        **cubic_identities,
        **quartic_identities,
        "zero_wave_quartet_count": len(zero_wave_separations),
        "zero_wave_selection_chain_count": zero_wave_selection_chain_count,
        "zero_wave_reduced_composition_term_count": (
            zero_wave_reduced_term_count
        ),
        "structural_fixed_leaf_count": (
            zero_wave_selection_chain_count
            if lower_reconstruction["exact_quadratic_identities"][
                "moment_hessian_all_zero"
            ]
            and cubic_identities["moment_third_derivative_all_zero"]
            and quartic_identities["moment_fourth_derivative_all_zero"]
            else 0
        ),
    }
    memoization = {
        "orbit_reduction_used": False,
        "mode_moment_direct_construction_count": len(mode_moments),
        "hessian_moment_direct_construction_count": len(hessian_moments),
        "cubic_moment_direct_construction_count": len(cubic_moments),
        "quartet_operator_forcing_and_proof_count": len(proofs),
        "exact_index_key_semantics": True,
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
        "maximum_correction_quartet_identifier": maximum_correction_quartet,
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
        "lower_jet_reconstruction": lower_reconstruction,
        "quartet_correspondence": quartet_correspondence,
        "structural_conservation": structural_conservation,
        "memoization": memoization,
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
                and lower_reconstruction[
                    "q007l_recomputed_study_validity"
                ]
                == "passed"
                and lower_reconstruction[
                    "q007l_recomputed_hypothesis_outcome"
                ]
                == "accepted"
                and lower_reconstruction["q007l_all_validity_gates_passed"]
                and lower_reconstruction["q007l_all_hypothesis_gates_passed"]
                and lower_reconstruction["q007j_representative_proof_count"]
                == EXPECTED_Q007J_PROOF_COUNT
                and lower_reconstruction[
                    "q007j_proof_digest_mismatch_count"
                ]
                == 0
                and lower_reconstruction["q007k_reconstructed_proof_count"]
                == EXPECTED_Q007K_PROOF_COUNT
                and lower_reconstruction[
                    "q007k_proof_digest_mismatch_count"
                ]
                == 0
                and lower_reconstruction[
                    "q007k_pair_metadata_mismatch_count"
                ]
                == 0
                and lower_reconstruction["q007l_reconstructed_proof_count"]
                == EXPECTED_Q007L_PROOF_COUNT
                and lower_reconstruction[
                    "q007l_proof_digest_mismatch_count"
                ]
                == 0
                and lower_reconstruction[
                    "q007l_triple_metadata_mismatch_count"
                ]
                == 0
            ),
            "threshold": (
                "fixed Q007c1/Q007l artifacts and Q007l runner; five "
                "quartic coefficient hashes; all 12 eigenpair, 300 "
                "quadratic, and 2600 cubic proof digests match"
            ),
            "value": {
                "inputs": {
                    name: record["passed"]
                    for name, record in input_records.items()
                },
                "coefficient_hashes_match": coefficient_reproduction[
                    "matches"
                ],
                "q007j_digest_mismatches": lower_reconstruction[
                    "q007j_proof_digest_mismatch_count"
                ],
                "q007k_digest_mismatches": lower_reconstruction[
                    "q007k_proof_digest_mismatch_count"
                ],
                "q007l_digest_mismatches": lower_reconstruction[
                    "q007l_proof_digest_mismatch_count"
                ],
            },
        },
        "registered_quartet_enumeration": {
            "passed": bool(
                enumeration["quartet_count"] == EXPECTED_QUARTET_COUNT
                and kind_counts["zero_wave_kinetic"]
                == EXPECTED_ZERO_WAVE_COUNT
                and kind_counts["internal_selected"] == EXPECTED_INTERNAL_COUNT
                and kind_counts["external"] == EXPECTED_EXTERNAL_COUNT
                and enumeration["permutation_multiplicity_sum"]
                == EXPECTED_MULTIPLICITY_SUM
                and enumeration["output_wave_support_count"]
                == EXPECTED_OUTPUT_SUPPORT_COUNT
                and complex_unknown_count == EXPECTED_COMPLEX_UNKNOWN_COUNT
            ),
            "threshold": (
                "17550 = 846 zero + 4536 internal + 12168 external "
                "quartets, multiplicity 331776, 81 output waves, 171558 "
                "complex unknowns"
            ),
            "value": enumeration,
        },
        "exact_quartic_forcing_and_conservation_structure": {
            "passed": bool(
                structural_conservation["quadratic_moment_hessian_all_zero"]
                and structural_conservation["zero_wave_moment_symbol_exact"]
                and structural_conservation[
                    "moment_third_derivative_all_zero"
                ]
                and structural_conservation[
                    "moment_fourth_derivative_all_zero"
                ]
                and structural_conservation["structural_fixed_leaf_count"]
                == EXPECTED_ZERO_WAVE_COUNT
            ),
            "threshold": (
                "exact D2/D3/D4 moment identities and all 846 zero-wave "
                "reduced-composition selection-rule chains"
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
                and len(proofs) == EXPECTED_QUARTET_COUNT
                and maximum_point_inverse_defect < 1
            ),
            "threshold": (
                "140-digit outward rounding, pi/trig <=1e-120, symbol "
                "<=1e-110, 17550 point inverse defects <1"
            ),
            "value": interval_construction,
        },
        "quartet_correspondence_memoization_and_strict_json": {
            "passed": bool(
                quartet_correspondence["length_matches"]
                and quartet_correspondence["mismatch_count"] == 0
                and not memoization["orbit_reduction_used"]
                and memoization["exact_index_key_semantics"]
                and memoization["quartet_operator_forcing_and_proof_count"]
                == EXPECTED_QUARTET_COUNT
                and finite_strict_json
            ),
            "threshold": (
                "all quartet identifiers/input modes/output waves/kinds/"
                "multiplicities match Q007c1, no orbit reduction, exact "
                "memoization keys, and finite strict JSON"
            ),
            "value": {
                "quartet_mismatch_count": quartet_correspondence[
                    "mismatch_count"
                ],
                "memoization": memoization,
                "finite_strict_json": finite_strict_json,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    hypothesis_gates = {
        "all_seventeen_thousand_five_hundred_krawczyk_inclusions": {
            "passed": bool(
                included_count == EXPECTED_QUARTET_COUNT
                and maximum_utilization <= MAXIMUM_KRAWCZYK_UTILIZATION
            ),
            "threshold": (
                "17550 strict inclusions and maximum utilization <=1e-2"
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
        "registered_quartic_coefficient_correction": {
            "passed": bool(
                maximum_correction <= MAXIMUM_REGISTERED_CORRECTION
            ),
            "threshold": (
                "maximum componentwise exact-root correction to registered "
                "complex H4/R4 <=1e-2"
            ),
            "value": {
                "maximum_correction": float(maximum_correction),
                "maximum_hessian_correction": float(
                    maximum_hessian_correction
                ),
                "maximum_reduced_correction": float(
                    maximum_reduced_correction
                ),
                "witness_quartet_identifier": maximum_correction_quartet,
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
                "846 positive zero-wave product separations and structural "
                "fixed-leaf solutions; 4536 augmented graph-gauge inclusions"
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
        scientific_classification = "registered quartic-jet bridge audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        scientific_classification = (
            "registered Q007c1 quartic coefficients identify the "
            "theorem-manifold graph-gauge quartic jet"
        )
    else:
        outcome = "not_certified"
        scientific_classification = (
            "registered quartic-jet bridge not certified"
        )

    return {
        "question": (
            "Do the 17550 registered Q007c1 complex H4/R4 coefficients "
            "enclose the unique exact graph-gauge quartic jet of the theorem "
            "manifold?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "mode_order": list(q007l.MODE_ORDER),
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
            "This identifies only the degree-four graph-gauge Taylor jet of "
            "the local analytic theorem manifold on the fixed 17x17 "
            "conservation leaf. It does not change Q007c1's finite-amplitude "
            "directional-shadowing rejection and does not certify an explicit "
            "neighborhood radius, finite-ball normal attraction, grid "
            "uniformity, or a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007i_theorem_acceptance_changed": False,
            "q007j_linear_eigencoordinate_acceptance_changed": False,
            "q007k_quadratic_jet_acceptance_changed": False,
            "q007l_cubic_jet_acceptance_changed": False,
            "q007h_independent_preconditioner_inconclusive_changed": False,
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister a separate Q007n explicit-local-radius "
            "gate; do not infer finite-ball attraction here."
        ),
    }


def run_q007m_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_quartic_jet_bridge_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational graph-gauge quartic-jet bridge",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": 24,
            "unordered_quartet_count": EXPECTED_QUARTET_COUNT,
            "complex_unknown_count": EXPECTED_COMPLEX_UNKNOWN_COUNT,
            "claim": (
                "degree-four Taylor-jet identification only; no explicit-"
                "radius, finite-ball, grid-uniform, or continuum claim"
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
    result = run_q007m_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
