"""Sealed Q007ae phase-aware selected-output internal resolvent audit.

The Q007ad external-output certificate, Q007o external-complement coordinate
constants, Q007n zero-wave inverse, scalar majorants, and candidate grid are
held fixed.  Only the selected-output center separation in the Q007o internal
resolvent is replaced by a complete complex-phase disc certificate.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q007ad_asymmetric_phase_resolvent as q007ad
from research.q007n_explicit_local_radius import (
    CANDIDATE_EXPONENTS,
    MAJORANT_DECIMAL_DIGITS,
    MAXIMUM_CONTRACTION,
    _round_up,
)
from research.q007o_external_complement_radius import (
    _radius_scan,
    _working_coefficients_from_q007n,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_COMPLEX_DIMENSION = 24
TARGET_CENTER_COUNT = 12
SCREEN_LOG_GAP = Fraction(1, 10**6)
PHASE_GAP = Fraction(21, 10**9)
MAXIMUM_INTERNAL_INVERSE = Fraction(2 * 10**9)
MINIMUM_TOTAL_IMPROVEMENT_FACTOR = Fraction(104, 100)

REGISTERED_CRITICAL_GAP_NUMERATOR = int(
    "13b365003d68998a2eff2773756558d32ebe28d1a2d8f901f16ac1fcb4787a91"
    "e6a181a003a99e14f9735a6c54a7d153fad5d6f931002887e9b498dda887fcde"
    "8201bc36f4f4de76bdc9467222a8603a6d9768d3f0c66e798187db670d0ed9e4"
    "55960aef38632333de25ffba5b21bb8d0f07c947cbdf3cd29f3cba3410234571"
    "c00057afe4f22bce515bc4541e485acb69f11f545c12dbf8ef45",
    16,
)
REGISTERED_CRITICAL_GAP_DENOMINATOR = int(
    "ce54d951f6b1b735456e9141526f4160dafe61661b02c9c49be7c18aa2cabce0"
    "2d1d2c83a3aba864c96ece92e130d585fe3409cfce8d627aabd927c60e874d75"
    "edc1fac720de10bcc2b25b16124f937daa544038adc15d83e51808e736f429c6"
    "941a2cb56b9d53f7747285969bcc3c454c3d4844306b3dcde3034",
    16,
) * 16**69
REGISTERED_CRITICAL_GAP = Fraction(
    REGISTERED_CRITICAL_GAP_NUMERATOR,
    REGISTERED_CRITICAL_GAP_DENOMINATOR,
)

Q007AD_ARTIFACT_FILENAME = "q007ad_asymmetric_phase_resolvent.json"
Q007AD_ARTIFACT_SHA256 = (
    "6a6f642cb681409ca160773180e025c1ffbc1929d6ec84423c384c57007571e4"
)
Q007AD_RUNNER_SHA256 = (
    "3ca5e39c3ddb79c886ef7bf4d6e6ad923deb66e53da3663251f183abbab7b0ae"
)
Q007AD_INPUT_DIGEST = (
    "b1b1b2750e871c6ee3b243f7df590ec19dd6d604d9699f183af007b89d0f7935"
)
Q007AD_RESULT_DIGEST = (
    "f5df89c55a86978c85542eeec82e6419884b69b919c0385ca77e9677b1c1d17f"
)
Q007AD_PHASE_DIGEST = (
    "086516b273f30d7c94c276399c16f8a6433bd90e3dc03fb740d2ab45754e4a37"
)

EXPECTED_GLOBAL_WITNESS = {
    "counts": [1, 19, 27, 4],
    "degree": 51,
    "external_identifier_count": 2,
    "external_identifiers": [
        "wave=-2,-2;eigenvalue_index=8",
        "wave=-2,-2;eigenvalue_index=7",
    ],
    "external_side": "left",
    "merged_external_index": 40,
}


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _load_registered_inputs(
    directory: Path,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    payloads, input_records = (
        q007ad.q007ac._load_registered_inputs(directory)
    )
    q007ad_path = directory / Q007AD_ARTIFACT_FILENAME
    q007ad_payload = json.loads(q007ad_path.read_text(encoding="utf-8"))
    cycle = q007ad_payload.get("cycle", {})
    scope = q007ad_payload.get("mathematical_scope", {})
    runner_path = Path(q007ad.__file__).resolve()
    observed_artifact_sha = _file_sha256(q007ad_path)
    observed_runner_sha = _file_sha256(runner_path)
    q007ad_record = {
        "filename": Q007AD_ARTIFACT_FILENAME,
        "sha256": observed_artifact_sha,
        "registered_sha256": Q007AD_ARTIFACT_SHA256,
        "sha256_matches": observed_artifact_sha == Q007AD_ARTIFACT_SHA256,
        "runner_filename": runner_path.name,
        "runner_sha256": observed_runner_sha,
        "registered_runner_sha256": Q007AD_RUNNER_SHA256,
        "runner_sha256_matches": observed_runner_sha == Q007AD_RUNNER_SHA256,
        "source_match": q007ad_payload.get("source") == source_metadata(),
        "scope_match": bool(
            scope.get("construction_grid") == [SIZE, SIZE]
            and float(scope.get("omega")) == OMEGA
            and float(scope.get("eta")) == ETA
        ),
        "study_gate": q007ad_payload.get("study_gate"),
        "scientific_outcome": q007ad_payload.get("scientific_outcome"),
        "scientific_classification": cycle.get("scientific_classification"),
        "all_validity_gates_passed": bool(
            cycle.get("validity_gates")
            and all(
                gate.get("passed", False)
                for gate in cycle["validity_gates"].values()
            )
        ),
        "all_hypothesis_gates_passed": bool(
            cycle.get("hypothesis_gates")
            and all(
                gate.get("passed", False)
                for gate in cycle["hypothesis_gates"].values()
            )
        ),
        "input_digest_sha256": cycle.get("input_digest_sha256"),
        "result_digest_sha256": cycle.get("result_digest_sha256"),
        "phase_comparison_digest_sha256": cycle.get(
            "phase_aware_separation_audit", {}
        )
        .get("phase", {})
        .get("comparison_digest_sha256"),
    }
    q007ad_record["passed"] = bool(
        q007ad_record["sha256_matches"]
        and q007ad_record["runner_sha256_matches"]
        and q007ad_record["source_match"]
        and q007ad_record["scope_match"]
        and q007ad_record["study_gate"] == "passed"
        and q007ad_record["scientific_outcome"] == "accepted"
        and q007ad_record["scientific_classification"]
        == (
            "original asymmetric discs certify the critical "
            "external-output phase gap"
        )
        and q007ad_record["all_validity_gates_passed"]
        and q007ad_record["all_hypothesis_gates_passed"]
        and q007ad_record["input_digest_sha256"] == Q007AD_INPUT_DIGEST
        and q007ad_record["result_digest_sha256"] == Q007AD_RESULT_DIGEST
        and q007ad_record["phase_comparison_digest_sha256"]
        == Q007AD_PHASE_DIGEST
    )
    return payloads, input_records, q007ad_payload, q007ad_record


def _implementation_source_audit() -> dict[str, Any]:
    base = q007ad.q007ac._implementation_source_audit()
    records = dict(base["records"])
    runner_path = Path(q007ad.__file__).resolve()
    observed = _file_sha256(runner_path)
    records["q007ad"] = {
        "path": "research/q007ad_asymmetric_phase_resolvent.py",
        "sha256": observed,
        "registered_sha256": Q007AD_RUNNER_SHA256,
        "passed": observed == Q007AD_RUNNER_SHA256,
    }
    return {
        "records": records,
        "all_registered_implementation_sha256_match": all(
            record["passed"] for record in records.values()
        ),
    }


def _selected_output_center_targets(
    representatives: tuple[Any, ...],
    q007o_cycle: dict[str, Any],
) -> tuple[
    tuple[q007ad.q007ac._TargetDisc, ...],
    dict[str, Any],
    bool,
]:
    by_wave = {proof.wave_index: proof for proof in representatives}
    q007o_records = q007o_cycle[
        "external_complement_inverse_refinement"
    ]["representative_records"]
    targets = []
    records = []
    all_indices_match = True
    all_digests_match = True
    for q007o_record in q007o_records:
        source_wave = tuple(q007o_record["q007h1_source_wave_index"])
        output_wave = tuple(q007o_record["wave_index"])
        proof = by_wave[source_wave]
        selected_indices = frozenset(proof.selected_indices)
        external_indices = tuple(
            index for index in range(9) if index not in selected_indices
        )
        indices_match = bool(
            list(external_indices)
            == q007o_record["external_indices_in_returned_order"]
            and sorted(proof.selected_indices)
            == q007o_record["selected_indices_sorted"]
        )
        digest_match = bool(
            proof.digest_matches
            and proof.proof_digest
            == q007o_record["q007h1_proof_digest_sha256"]
        )
        all_indices_match = all_indices_match and indices_match
        all_digests_match = all_digests_match and digest_match
        identifiers = []
        for eigenvalue_index in external_indices:
            identifier = (
                f"selected_output_wave={output_wave[0]},{output_wave[1]};"
                f"external_index={eigenvalue_index}"
            )
            center = q007ad.q007ac._complex_fraction(
                proof.eigenvalues[eigenvalue_index]
            )
            identifiers.append(identifier)
            targets.append(
                q007ad.q007ac._TargetDisc(
                    identifier=identifier,
                    wave_index=output_wave,
                    eigenvalue_index=eigenvalue_index,
                    center=center,
                    center_complex=complex(
                        proof.eigenvalues[eigenvalue_index]
                    ),
                    radius=Fraction(0),
                )
            )
        records.append(
            {
                "output_wave_index": list(output_wave),
                "q007h1_source_wave_index": list(source_wave),
                "q007h1_rotation_power": q007o_record[
                    "q007h1_rotation_power"
                ],
                "selected_indices_sorted": sorted(proof.selected_indices),
                "external_indices_in_returned_order": list(
                    external_indices
                ),
                "indices_match_q007o": indices_match,
                "proof_digest_matches_q007o": digest_match,
                "target_identifiers": identifiers,
            }
        )
    passed = bool(
        len(q007o_records) == 2
        and len(targets) == TARGET_CENTER_COUNT
        and all_indices_match
        and all_digests_match
    )
    audit = {
        "target_definition": (
            "Q007o approximate external eigenvalue point centers; zero "
            "target radius because Q007o gamma accounts for residual"
        ),
        "representative_count": len(records),
        "target_center_count": len(targets),
        "all_indices_match_q007o": all_indices_match,
        "all_proof_digests_match_q007o": all_digests_match,
        "target_radius_is_zero": all(target.radius == 0 for target in targets),
        "c4_selected_output_wave_coverage": 8,
        "fourier_wave_sum_restriction_used": False,
        "representative_records": records,
        "target_centers": {
            target.identifier: {
                "center": q007ad.q007ac._complex_fraction_record(
                    target.center
                ),
                "radius": _fraction_record(target.radius),
            }
            for target in targets
        },
    }
    return tuple(targets), audit, passed


def _internal_inverse_refinement(
    q007o_cycle: dict[str, Any],
    zero_inverse: Fraction,
) -> tuple[dict[str, Any], Fraction, Fraction, bool]:
    q007o_records = q007o_cycle[
        "external_complement_inverse_refinement"
    ]["representative_records"]
    records = []
    working_values = []
    critical_values = []
    for record in q007o_records:
        external_basis = q007ad.q007ac._fraction_from_record(
            record["external_basis_l1_upper"]
        )
        coordinate_inverse = q007ad.q007ac._fraction_from_record(
            record["coordinate_inverse_l1_upper"]
        )
        selector_projector = q007ad.q007ac._fraction_from_record(
            record["selector_projector_l1_upper"]
        )
        gamma = q007ad.q007ac._fraction_from_record(
            record["representation_perturbation_gamma"]
        )
        weighted_reduced = q007ad.q007ac._fraction_from_record(
            record["weighted_reduced_inverse_upper"]
        )
        numerator = (
            external_basis * coordinate_inverse * selector_projector
        )
        critical_gap = gamma + numerator / zero_inverse
        critical_values.append(critical_gap)
        denominator = PHASE_GAP - gamma
        chart_inverse = (
            numerator / denominator
            if denominator > 0
            else Fraction(10**1000)
        )
        raw_pair = max(chart_inverse, weighted_reduced)
        working_pair = _round_up(raw_pair, MAJORANT_DECIMAL_DIGITS)
        working_values.append(working_pair)
        records.append(
            {
                "wave_index": record["wave_index"],
                "external_basis_l1_upper": _fraction_record(
                    external_basis
                ),
                "coordinate_inverse_l1_upper": _fraction_record(
                    coordinate_inverse
                ),
                "selector_projector_l1_upper": _fraction_record(
                    selector_projector
                ),
                "resolvent_numerator": _fraction_record(numerator),
                "representation_perturbation_gamma": _fraction_record(
                    gamma
                ),
                "critical_gap_for_zero_inverse": _fraction_record(
                    critical_gap
                ),
                "registered_phase_gap_minus_gamma": _fraction_record(
                    denominator
                ),
                "raw_chart_internal_inverse_upper": _fraction_record(
                    chart_inverse
                ),
                "weighted_reduced_inverse_upper": _fraction_record(
                    weighted_reduced
                ),
                "raw_pair_internal_inverse_upper": _fraction_record(
                    raw_pair
                ),
                "working_pair_internal_inverse_upper": _fraction_record(
                    working_pair
                ),
            }
        )
    maximum_critical_gap = max(critical_values)
    raw_internal = max(
        q007ad.q007ac._fraction_from_record(
            record["raw_pair_internal_inverse_upper"]
        )
        for record in records
    )
    working_internal = _round_up(
        raw_internal, MAJORANT_DECIMAL_DIGITS
    )
    critical_matches = maximum_critical_gap == REGISTERED_CRITICAL_GAP
    audit = {
        "formula": (
            "max_k max(N_k/(phase_gap-gamma_k), weighted_reduced_k)"
        ),
        "registered_phase_gap": _fraction_record(PHASE_GAP),
        "representative_records": records,
        "registered_maximum_critical_gap": _fraction_record(
            REGISTERED_CRITICAL_GAP
        ),
        "reconstructed_maximum_critical_gap": _fraction_record(
            maximum_critical_gap
        ),
        "critical_gap_matches_registration": critical_matches,
        "target_to_maximum_critical_ratio": _fraction_record(
            PHASE_GAP / maximum_critical_gap
        ),
        "raw_internal_pair_inverse_upper": _fraction_record(raw_internal),
        "working_internal_pair_inverse_upper": _fraction_record(
            working_internal
        ),
        "working_internal_strictly_below_zero": (
            working_internal < zero_inverse
        ),
        "only_selected_output_center_gap_changed": True,
    }
    return audit, raw_internal, working_internal, critical_matches


def run_internal_phase_resolvent_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        q007ad.q007ac._default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    (
        payloads,
        input_records,
        q007ad_payload,
        q007ad_input_audit,
    ) = _load_registered_inputs(directory)
    implementation_audit = _implementation_source_audit()
    q007h1 = payloads["q007h1"]
    q007i_cycle = payloads["q007i"]["cycle"]
    q007n_cycle = payloads["q007n"]["cycle"]
    q007o_cycle = payloads["q007o"]["cycle"]
    q007ad_cycle = q007ad_payload["cycle"]
    q007n_spectral = q007n_cycle["spectral_separation_and_inverse"]

    representatives, reconstruction = (
        q007ad.q007ac._rebuild_representative_proofs(q007h1)
    )
    selected_radius_upper = q007ad.q007ac._fraction_from_record(
        q007n_spectral["working_selected_spectral_radius_upper"]
    )
    discs, disc_audit, discs_passed = q007ad._original_selected_discs(
        representatives, selected_radius_upper
    )
    targets, target_audit, targets_passed = (
        _selected_output_center_targets(representatives, q007o_cycle)
    )
    selected_types, _unused_external, _classification_internal = (
        q007ad.q007ac._selected_types_and_external_disks(representatives)
    )
    target_log_inputs = q007ad.q007ac._target_log_inputs(targets)
    selected_logs, external_logs, logarithms_internal = (
        q007ad.q007ac._log_enclosures(selected_types, target_log_inputs)
    )
    merged_external = q007ad.q007ac._merge_external_logs(external_logs)
    dangerous, screen_audit, screen_passed = (
        q007ad.q007ac._screen_aggregates(
            selected_logs, merged_external
        )
    )
    phase_audit, phase_passed = q007ad._phase_certificate(
        dangerous,
        discs,
        targets,
        selected_radius_upper,
    )

    finite_modulus_floor = q007ad.q007ac._fraction_from_record(
        q007n_spectral["finite_degree_minimum_modulus"]
    )
    safe_absolute_gap = finite_modulus_floor * SCREEN_LOG_GAP
    tail_gap = q007ad.q007ac._fraction_from_record(
        q007n_spectral["degree_90_tail_absolute_gap_lower"]
    )
    zero_inverse = q007ad.q007ac._fraction_from_record(
        q007n_spectral["zero_wave_fixed_leaf_inverse_upper"]
    )
    (
        internal_audit,
        _raw_internal_inverse,
        working_internal_inverse,
        critical_matches,
    ) = _internal_inverse_refinement(q007o_cycle, zero_inverse)
    q007ad_external_inverse = q007ad.q007ac._fraction_from_record(
        q007ad_cycle["inverse_refinement"][
            "working_asymmetric_phase_external_inverse_upper"
        ]
    )
    q007ad_total_inverse = q007ad.q007ac._fraction_from_record(
        q007ad_cycle["inverse_refinement"][
            "working_new_total_pair_inverse_upper"
        ]
    )
    raw_total_inverse = max(
        working_internal_inverse,
        q007ad_external_inverse,
        zero_inverse,
    )
    working_total_inverse = _round_up(
        raw_total_inverse, MAJORANT_DECIMAL_DIGITS
    )
    total_improvement_factor = (
        q007ad_total_inverse / working_total_inverse
    )

    coefficients = _working_coefficients_from_q007n(q007n_cycle)
    old_scan, _old_exact = _radius_scan(
        coefficients,
        selected_radius_upper,
        q007ad_total_inverse,
    )
    stored_old_scan = q007ad_cycle["radius_comparison"][
        "asymmetric_phase_refined_radius_search"
    ]
    old_records_reproduced = (
        old_scan["records"] == stored_old_scan["records"]
    )
    new_scan, _new_exact = _radius_scan(
        coefficients,
        selected_radius_upper,
        working_total_inverse,
    )
    new_selected = new_scan["selected_candidate"]
    previous = new_scan["previous_larger_candidate"]
    radius_boundary_matches = bool(
        new_selected is not None
        and new_selected["modal_radius_decimal"] == "1e-16"
        and previous is not None
        and previous["modal_radius_decimal"] == "1e-15"
        and not previous["passed"]
    )
    strict_boundary = bool(
        radius_boundary_matches
        and new_selected["passed"]
        and new_selected["density_buffer_positive"]
        and new_selected["reduced_range_buffer_positive"]
        and new_selected["contraction_strictly_below_one_half"]
        and new_selected["radii_inequality_strict"]
    )

    global_witness = q007i_cycle["enumeration"][
        "global_minimum_gap_witness"
    ]
    global_witness_reproduced = (
        global_witness == EXPECTED_GLOBAL_WITNESS
    )
    global_gap = q007ad.q007ac._fraction_from_record(
        q007n_spectral["working_uniform_absolute_gap_lower"]
    )
    bottleneck_audit = {
        "q007i_global_minimum_gap_witness": global_witness,
        "registered_global_witness": EXPECTED_GLOBAL_WITNESS,
        "global_witness_reproduced": global_witness_reproduced,
        "global_witness_is_selected_output": False,
        "q007n_working_global_absolute_gap": _fraction_record(global_gap),
        "q007o_working_internal_pair_inverse": q007o_cycle[
            "external_complement_inverse_refinement"
        ]["working_internal_pair_inverse_upper"],
        "q007ad_total_is_q007o_internal_limited": (
            q007ad_total_inverse
            == q007ad.q007ac._fraction_from_record(
                q007o_cycle["external_complement_inverse_refinement"][
                    "working_internal_pair_inverse_upper"
                ]
            )
        ),
    }
    logarithms = {
        key: value
        for key, value in logarithms_internal.items()
        if not key.endswith("_exact")
    }
    merged_records = [
        {
            "merged_index": index,
            "lower_scaled_integer": str(interval.lower),
            "upper_scaled_integer": str(interval.upper),
            "source_center_count": len(interval.identifiers),
            "identifiers": list(interval.identifiers),
        }
        for index, interval in enumerate(merged_external)
    ]
    selected_center_certificate_digest = (
        q007ad.q007ac._canonical_json_sha256(
            {
                "target_center_audit": target_audit,
                "phase_comparison_digest_sha256": phase_audit[
                    "comparison_digest_sha256"
                ],
            }
        )
    )
    separation_audit = {
        "log_series_terms": q007ad.q007ac.LOG_SERIES_TERMS,
        "log_internal_decimal_digits": (
            q007ad.q007ac.LOG_INTERNAL_DECIMAL_DIGITS
        ),
        "log_final_decimal_digits": (
            q007ad.q007ac.LOG_FINAL_DECIMAL_DIGITS
        ),
        "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
        "phase_gap": _fraction_record(PHASE_GAP),
        "finite_modulus_floor_reused_from_q007n": _fraction_record(
            finite_modulus_floor
        ),
        "safe_absolute_gap_lower": _fraction_record(safe_absolute_gap),
        "degree_90_tail_gap_reused_from_q007n": _fraction_record(
            tail_gap
        ),
        "safe_screen_exceeds_phase_gap": (
            safe_absolute_gap > PHASE_GAP
        ),
        "tail_exceeds_phase_gap": tail_gap > PHASE_GAP,
        "selected_log_records": logarithms["selected_type_records"],
        "target_center_log_digest_sha256": logarithms[
            "external_disk_log_digest_sha256"
        ],
        "merged_target_interval_count": len(merged_external),
        "merged_target_intervals": merged_records,
        "screen": screen_audit,
        "phase": phase_audit,
        "selected_center_certificate_digest_sha256": (
            selected_center_certificate_digest
        ),
    }
    total_inverse_audit = {
        "q007ad_working_external_inverse_upper": _fraction_record(
            q007ad_external_inverse
        ),
        "q007n_zero_wave_inverse_upper": _fraction_record(zero_inverse),
        "q007ae_working_internal_inverse_upper": _fraction_record(
            working_internal_inverse
        ),
        "raw_new_total_pair_inverse_upper": _fraction_record(
            raw_total_inverse
        ),
        "working_new_total_pair_inverse_upper": _fraction_record(
            working_total_inverse
        ),
        "q007ad_working_total_pair_inverse_upper": _fraction_record(
            q007ad_total_inverse
        ),
        "total_inverse_improvement_factor": _fraction_record(
            total_improvement_factor
        ),
        "new_total_is_q007ad_external_limited": (
            working_total_inverse == q007ad_external_inverse
        ),
        "only_selected_output_internal_inverse_changed": True,
    }
    radius_comparison = {
        "q007ad_old_candidate_records_reproduced_exactly": (
            old_records_reproduced
        ),
        "registered_radius_boundary_matches": radius_boundary_matches,
        "internal_phase_refined_radius_search": new_scan,
    }

    input_digest = q007ad.q007ac._canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "q007ad_accepted_input_audit": q007ad_input_audit,
            "implementation_source_audit": implementation_audit,
            "registered_parameters": {
                "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
                "phase_gap": _fraction_record(PHASE_GAP),
                "registered_critical_gap": _fraction_record(
                    REGISTERED_CRITICAL_GAP
                ),
                "target_center_count": TARGET_CENTER_COUNT,
                "target_radius": _fraction_record(Fraction(0)),
                "fourier_wave_sum_restriction_used": False,
                "candidate_exponents": list(CANDIDATE_EXPONENTS),
            },
        }
    )
    result_digest = q007ad.q007ac._canonical_json_sha256(
        {
            "bottleneck_reproduction_audit": bottleneck_audit,
            "original_selected_disc_audit": disc_audit,
            "selected_output_target_center_audit": target_audit,
            "separation_summary": {
                "target_center_log_digest_sha256": separation_audit[
                    "target_center_log_digest_sha256"
                ],
                "screen": {
                    key: value
                    for key, value in screen_audit.items()
                    if key not in {"degree_records", "dangerous_records"}
                },
                "phase": phase_audit,
                "selected_center_certificate_digest_sha256": (
                    selected_center_certificate_digest
                ),
            },
            "internal_inverse_refinement": internal_audit,
            "total_inverse_refinement": total_inverse_audit,
            "radius_comparison": radius_comparison,
        }
    )

    serializable_sections = {
        "input_artifacts": input_records,
        "q007ad_accepted_input_audit": q007ad_input_audit,
        "implementation_source_audit": implementation_audit,
        "spectral_reconstruction": reconstruction,
        "bottleneck_reproduction_audit": bottleneck_audit,
        "original_selected_disc_audit": disc_audit,
        "selected_output_target_center_audit": target_audit,
        "phase_aware_separation_audit": separation_audit,
        "internal_inverse_refinement": internal_audit,
        "total_inverse_refinement": total_inverse_audit,
        "radius_comparison": radius_comparison,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    input_passed = bool(
        all(record["passed"] for record in input_records.values())
        and q007ad_input_audit["passed"]
        and implementation_audit[
            "all_registered_implementation_sha256_match"
        ]
    )
    bottleneck_passed = bool(
        global_witness_reproduced
        and not bottleneck_audit["global_witness_is_selected_output"]
        and bottleneck_audit[
            "q007ad_total_is_q007o_internal_limited"
        ]
        and critical_matches
    )
    spectral_target_passed = bool(
        reconstruction["representative_count"] == 72
        and reconstruction["proof_digest_mismatch_count"] == 0
        and discs_passed
        and targets_passed
        and target_audit["target_radius_is_zero"]
    )
    complete_phase_execution = bool(
        screen_passed
        and screen_audit["aggregate_count"]
        == q007ad.q007ac.EXPECTED_AGGREGATE_COUNT
        and safe_absolute_gap > PHASE_GAP
        and phase_audit["complete"]
        and tail_gap > PHASE_GAP
    )
    reuse_passed = bool(
        old_records_reproduced
        and q007n_cycle["radius_search"]["candidate_exponents"]
        == list(CANDIDATE_EXPONENTS)
        and working_total_inverse
        == max(
            working_internal_inverse,
            q007ad_external_inverse,
            zero_inverse,
        )
        and total_inverse_audit[
            "only_selected_output_internal_inverse_changed"
        ]
    )
    validity_gates = {
        "registered_inputs_and_q007ad_acceptance": {
            "passed": input_passed,
            "threshold": (
                "five artifact and five implementation SHA values match; "
                "Q007ad remains accepted with sealed digests"
            ),
            "value": {
                "accepted_input_count": sum(
                    record["passed"] for record in input_records.values()
                ),
                "q007ad_accepted_input_passed": q007ad_input_audit[
                    "passed"
                ],
            },
        },
        "q007o_bottleneck_and_critical_gap_reproduction": {
            "passed": bottleneck_passed,
            "threshold": (
                "Q007i nonselected global witness, Q007o constants, and "
                "registered maximum critical fraction reproduce"
            ),
            "value": {
                "global_witness_reproduced": global_witness_reproduced,
                "critical_gap_matches_registration": critical_matches,
            },
        },
        "original_discs_and_selected_target_centers": {
            "passed": spectral_target_passed,
            "threshold": (
                "72 proofs, six original selected discs, 12 zero-radius "
                "Q007o point centers, and C4 coverage reproduce"
            ),
            "value": {
                "proof_digest_mismatch_count": reconstruction[
                    "proof_digest_mismatch_count"
                ],
                "selected_disc_count": disc_audit["disc_count"],
                "target_center_count": target_audit[
                    "target_center_count"
                ],
            },
        },
        "complete_modulus_screen_phase_expansion_and_tail": {
            "passed": complete_phase_execution,
            "threshold": (
                "2,919,730 aggregates partitioned, every dangerous split/"
                "center compared, safe screen and degree-90 tail complete"
            ),
            "value": {
                "aggregate_count": screen_audit["aggregate_count"],
                "dangerous_aggregate_count": screen_audit[
                    "dangerous_aggregate_count"
                ],
                "expanded_product_count": phase_audit[
                    "expanded_product_count"
                ],
                "comparison_count": phase_audit["comparison_count"],
            },
        },
        "q007ad_majorant_and_candidate_reuse": {
            "passed": reuse_passed,
            "threshold": (
                "Q007ad external, Q007n zero, Q007o coordinate constants, "
                "majorants, 119 candidates, and old records are unchanged"
            ),
            "value": {
                "old_records_reproduced": old_records_reproduced,
                "only_internal_inverse_changed": total_inverse_audit[
                    "only_selected_output_internal_inverse_changed"
                ],
            },
        },
        "finite_strict_json_and_digests": {
            "passed": finite_strict_json,
            "threshold": (
                "finite strict JSON with input/phase/result digests"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest,
                "phase_certificate_digest_sha256": (
                    selected_center_certificate_digest
                ),
                "result_digest_sha256": result_digest,
            },
        },
    }
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )

    internal_below_threshold = bool(
        working_internal_inverse < MAXIMUM_INTERNAL_INVERSE
        and working_internal_inverse < zero_inverse
    )
    total_external_limited = bool(
        working_total_inverse == q007ad_external_inverse
        and total_improvement_factor
        >= MINIMUM_TOTAL_IMPROVEMENT_FACTOR
    )
    hypothesis_gates = {
        "registered_selected_output_phase_gap_certified": {
            "passed": bool(phase_passed and tail_gap > PHASE_GAP),
            "threshold": (
                "every finite-degree selected-output center comparison and "
                "the degree-90 tail strictly exceed 2.1e-8"
            ),
            "value": {
                "failed_comparison_count": phase_audit[
                    "failed_comparison_count"
                ],
                "minimum_squared_margin": phase_audit[
                    "minimum_squared_margin"
                ]["float"],
            },
        },
        "working_internal_inverse_is_below_two_billion_and_zero": {
            "passed": internal_below_threshold,
            "threshold": "working internal <2e9<zero-wave inverse",
            "value": {
                "internal": float(working_internal_inverse),
                "zero": float(zero_inverse),
            },
        },
        "new_total_is_q007ad_external_limited": {
            "passed": total_external_limited,
            "threshold": (
                "new total equals Q007ad external and Q007ad total/new "
                "total >=1.04"
            ),
            "value": {
                "new_total": float(working_total_inverse),
                "q007ad_external": float(q007ad_external_inverse),
                "improvement_factor": float(total_improvement_factor),
            },
        },
        "registered_radius_boundary_remains_1e_minus_16": {
            "passed": radius_boundary_matches,
            "threshold": (
                "1e-16 remains the largest passing candidate and 1e-15 "
                "fails"
            ),
            "value": {
                "selected_radius": (
                    None
                    if new_selected is None
                    else new_selected["modal_radius_decimal"]
                ),
                "previous_radius": (
                    None
                    if previous is None
                    else previous["modal_radius_decimal"]
                ),
            },
        },
        "registered_radius_boundary_is_strict": {
            "passed": strict_boundary,
            "threshold": (
                "1e-16 has strict density/range buffers, Z<1/2, and "
                "radii inequality"
            ),
            "value": {
                "selected_passed": (
                    False if new_selected is None else new_selected["passed"]
                ),
                "previous_passed": (
                    None if previous is None else previous["passed"]
                ),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q007ae selected-output phase audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "phase-aware selected-output centers remove the internal "
            "resolvent bottleneck"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered selected-output phase certificate did not remove "
            "the internal bottleneck"
        )

    return {
        "question": (
            "Does a complete 2.1e-8 phase certificate against the 12 Q007o "
            "selected-output external point centers remove the Q007o "
            "internal resolvent bottleneck while all Q007ad radius inputs "
            "remain fixed?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
            "phase_gap": _fraction_record(PHASE_GAP),
            "registered_maximum_critical_gap": _fraction_record(
                REGISTERED_CRITICAL_GAP
            ),
            "maximum_internal_inverse": _fraction_record(
                MAXIMUM_INTERNAL_INVERSE
            ),
            "minimum_total_improvement_factor": _fraction_record(
                MINIMUM_TOTAL_IMPROVEMENT_FACTOR
            ),
            "target_center_count": TARGET_CENTER_COUNT,
            "target_radius": _fraction_record(Fraction(0)),
            "fourier_wave_sum_restriction_used": False,
            "candidate_exponents": list(CANDIDATE_EXPONENTS),
            "maximum_contraction": _fraction_record(MAXIMUM_CONTRACTION),
            "phase_gap_reused_from_q007ad_without_search": True,
        },
        "input_artifacts": input_records,
        "q007ad_accepted_input_audit": q007ad_input_audit,
        "implementation_source_audit": implementation_audit,
        "spectral_reconstruction": reconstruction,
        "bottleneck_reproduction_audit": bottleneck_audit,
        "original_selected_disc_audit": disc_audit,
        "selected_output_target_center_audit": target_audit,
        "phase_aware_separation_audit": separation_audit,
        "internal_inverse_refinement": internal_audit,
        "total_inverse_refinement": total_inverse_audit,
        "radius_comparison": radius_comparison,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "q007ad_explicit_radius_1e_minus_16_preserved": bool(
                validity_passed and radius_boundary_matches
            ),
            "selected_output_internal_resolvent_bottleneck_removed": bool(
                validity_passed and internal_below_threshold
            ),
            "new_total_is_nonselected_external_limited": bool(
                validity_passed and total_external_limited
            ),
            "strictly_larger_decimal_grid_radius_certified": False,
            "q007p_through_q007ab_tube_constants_enlarged": False,
        },
        "claim_boundary": (
            "If accepted, this removes only the Q007o selected-output "
            "internal resolvent as the total-inverse bottleneck for the "
            "fixed 17x17 map, conservation leaf, and modal/Wiener norms. "
            "The explicit decimal-grid radius remains 1e-16 and the new "
            "bottleneck is Q007ad's nonselected-output external inverse. "
            "The certificate does not optimize the phase gap, use Fourier "
            "wave-sum restrictions, improve the external or zero-wave "
            "inverse, enlarge Q007p--Q007ab tube/MPFR constants, or certify "
            "Euclidean/grid-uniform attraction, a global basin, boundaries, "
            "forcing, or D3Q27."
        ),
        "preserved_prior_outcomes": {
            "q007ad_external_phase_certificate_changed": False,
            "q007ad_explicit_radius_changed": False,
            "q007p_through_q007ab_tube_results_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q010_sparse_cost_dominance_changed": False,
        },
        "next_change": (
            "If accepted, the next analytic-radius bottleneck is Q007ad's "
            "nonselected-output external inverse. A sharper external gap, "
            "continuous radius optimization, or downstream tube enlargement "
            "must be preregistered separately."
        ),
    }


def run_q007ae_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_internal_phase_resolvent_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "rational phase-aware selected-output internal resolvent "
                "certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": (
                "fixed global mass and momentum leaf"
            ),
            "selected_real_dimension": SELECTED_COMPLEX_DIMENSION,
            "selected_complex_dimension": SELECTED_COMPLEX_DIMENSION,
            "claim": (
                "selected-output internal bottleneck removal only; no "
                "strict decimal-grid radius or downstream tube enlargement"
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
    result = run_q007ae_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
