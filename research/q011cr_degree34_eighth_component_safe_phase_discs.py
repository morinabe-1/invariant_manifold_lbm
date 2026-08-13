"""Q011cr component-safe complex phase discs for Q011cb flatten ordinal seven."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

import research.q011cj_degree34_fourth_component_safe_phase_discs as q011cj
import research.q011cl_degree34_fifth_component_safe_phase_discs as q011cl
import research.q011cq_degree34_eighth_individual_partition_audit as q011cq
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011cq.q011b
q011z = q011cq.q011z

ExactComplex = tuple[Fraction, Fraction]
_ExactDisc = q011cl._ExactDisc

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
PARENT_FLAT_ORDINAL = 7
OUTPUT_BLOCK = 7
TARGET_IDENTIFIER = "block=7;center=44"

SOURCE_VARIANTS = q011cl.SOURCE_VARIANTS
EXPECTED_SOURCE_RADIUS_HEX = q011cl.EXPECTED_SOURCE_RADIUS_HEX
EXPECTED_TARGET_RADIUS_HEX = q011cl.EXPECTED_TARGET_RADIUS_HEX
EXPECTED_SOURCE_RECORD_DIGEST = q011cl.EXPECTED_SOURCE_RECORD_DIGEST
EXPECTED_TARGET_RECORD_DIGEST = q011cl.EXPECTED_TARGET_RECORD_DIGEST

EXPECTED_FULL_ALLOCATION_COUNT = 147_840
EXPECTED_COMPATIBLE_ALLOCATION_COUNT = 8_350
EXPECTED_WAVE_PROJECTION_COUNT = 382
EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT = 10
EXPECTED_FULL_ALLOCATION_DIGEST = "f140b67195a9935eacee5db2ab43e9bc0f07ac5dfb4856bed3aeedbf84756b1d"
EXPECTED_COMPATIBLE_ALLOCATION_DIGEST = (
    "8293e5ae53c2bb28cae1a2cf51b26653c4c87e7f631c5702c2a3d2a625f8367a"
)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 0, 0, 9, 0, 5, 5, 2, 0, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = (13, 0, 9, 0, 0, 0, 0, 5, 0, 7, 0, 0)
EXPECTED_WAVE_PROJECTION_DIGEST = "a5bcbaccfa447976fa13bec3687f708c6985b758199ff816e71ee3b1f4c3fb97"
EXPECTED_PHASE_FIBER_HISTOGRAM = {10: 79, 18: 77, 24: 76, 28: 75, 30: 75}

Q011CQ_ARTIFACT_SHA256 = "7f07489552736b5c5105aa64929870f5cf22bdd430be012ced1acb8eb0282e0b"
Q011CQ_RUNNER_SHA256 = "db9be5e8652b16ebe42ff8d46e9b7f4703ca4cdf4ae93d98d6eaf138cb0a0595"
Q011CQ_DIGEST_NAMES = (
    "input_digest_sha256",
    "partition_input_digest_sha256",
    "allocation_audit_digest_sha256",
    "result_digest_sha256",
)
Q011CQ_DIGESTS = (
    "bc327d381eee5a285d5fc35b0543e16050c65e57dcd4e43a405c97edab3732e3",
    "c42fa3b0729531f0123498591ae56ded15526347a3ae680d59486d10929bc4b7",
    "d24be289597289e30edc367825e37b89526659aebe9c055e10139aef94b8d7f9",
    "72c1bb458bb8ce2b77f152922e9c96a69de33ffc2df30948ed6a1a56ee73aff2",
)
EXPECTED_Q011CQ_ALLOCATION_RECORD_DIGEST = (
    "21e135468c9c03c73927cdb423dfbd258ad15a54b56cd2a589da723fbd53b855"
)

RESOLVED_CLASSIFICATION = (
    "the component-safe complex phase discs resolve the eighth Q011cb persistent refined witness"
)
PERSISTENT_CLASSIFICATION = (
    "the eighth Q011cb persistent refined witness persists under component-safe complex phase discs"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011cr component-safe phase-disc audit is inconclusive"

_BASE_FRAMED_RECORD_DIGEST = q011cl._BASE_FRAMED_RECORD_DIGEST
_BASE_EXACT_FRACTION_SEQUENCE_SHA256 = q011cl._BASE_EXACT_FRACTION_SEQUENCE_SHA256
_PROTOCOL_NAMES = (
    "q011ci",
    "PARENT_FLAT_ORDINAL",
    "EXPECTED_FULL_ALLOCATION_COUNT",
    "EXPECTED_COMPATIBLE_ALLOCATION_COUNT",
    "EXPECTED_WAVE_PROJECTION_COUNT",
    "EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT",
    "EXPECTED_FULL_ALLOCATION_DIGEST",
    "EXPECTED_COMPATIBLE_ALLOCATION_DIGEST",
    "EXPECTED_FIRST_COMPATIBLE_COUNTS",
    "EXPECTED_LAST_COMPATIBLE_COUNTS",
    "EXPECTED_WAVE_PROJECTION_DIGEST",
    "EXPECTED_PHASE_FIBER_HISTOGRAM",
    "_power_tables",
    "_q011cj_framed_record_digest",
    "_q011cj_exact_fraction_sequence_sha256",
)
_PROTOCOL_BASELINE = {name: getattr(q011cj, name) for name in _PROTOCOL_NAMES}


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _q011cr_framed_record_digest(domain: str) -> Any:
    if domain != "q011ch-component-safe-phase-comparisons-v1":
        raise ValueError(f"unexpected inherited comparison domain: {domain}")
    return _BASE_FRAMED_RECORD_DIGEST("q011cr-component-safe-phase-comparisons-v1")


def _q011cr_exact_fraction_sequence_sha256(
    domain: bytes,
    values: tuple[Fraction, ...],
) -> str:
    if domain == b"q011ch-complex-margin-expression-v1":
        domain = b"q011cr-complex-margin-expression-v1"
    return _BASE_EXACT_FRACTION_SEQUENCE_SHA256(domain, values)


def _power_tables(
    center_uppers: tuple[Fraction, ...],
    source_discs: tuple[_ExactDisc, ...],
) -> tuple[
    tuple[tuple[ExactComplex, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    bool,
]:
    maximum_counts = (13, 13, 9, 9, 9, 9, 5, 5, 7, 7, 0, 0)
    center_powers = []
    upper_powers = []
    full_powers = []
    radius_powers = []
    recurrence_checks = []
    for upper, disc, maximum in zip(
        center_uppers,
        source_discs,
        maximum_counts,
        strict=True,
    ):
        disc_center_powers = []
        disc_upper_powers = []
        disc_full_powers = []
        disc_radius_powers = []
        recurrence_center = Fraction(1)
        recurrence_radius = Fraction(0)
        for count in range(maximum + 1):
            center_power = q011cj.q011ch.q011ca._complex_power(
                disc.center,
                count,
            )
            upper_power = upper**count
            full_power = (upper + disc.radius) ** count
            closed_radius = full_power - upper_power
            if count:
                recurrence_radius = (
                    recurrence_center * disc.radius
                    + upper * recurrence_radius
                    + recurrence_radius * disc.radius
                )
                recurrence_center *= upper
            recurrence_checks.append(
                recurrence_center == upper_power and recurrence_radius == closed_radius
            )
            disc_center_powers.append(center_power)
            disc_upper_powers.append(upper_power)
            disc_full_powers.append(full_power)
            disc_radius_powers.append(recurrence_radius)
        center_powers.append(tuple(disc_center_powers))
        upper_powers.append(tuple(disc_upper_powers))
        full_powers.append(tuple(disc_full_powers))
        radius_powers.append(tuple(disc_radius_powers))
    return (
        tuple(center_powers),
        tuple(upper_powers),
        tuple(full_powers),
        tuple(radius_powers),
        all(recurrence_checks),
    )


def _protocol_overrides() -> dict[str, Any]:
    return {
        "q011ci": q011cq,
        "PARENT_FLAT_ORDINAL": PARENT_FLAT_ORDINAL,
        "EXPECTED_FULL_ALLOCATION_COUNT": EXPECTED_FULL_ALLOCATION_COUNT,
        "EXPECTED_COMPATIBLE_ALLOCATION_COUNT": (EXPECTED_COMPATIBLE_ALLOCATION_COUNT),
        "EXPECTED_WAVE_PROJECTION_COUNT": EXPECTED_WAVE_PROJECTION_COUNT,
        "EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT": (EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT),
        "EXPECTED_FULL_ALLOCATION_DIGEST": EXPECTED_FULL_ALLOCATION_DIGEST,
        "EXPECTED_COMPATIBLE_ALLOCATION_DIGEST": (EXPECTED_COMPATIBLE_ALLOCATION_DIGEST),
        "EXPECTED_FIRST_COMPATIBLE_COUNTS": EXPECTED_FIRST_COMPATIBLE_COUNTS,
        "EXPECTED_LAST_COMPATIBLE_COUNTS": EXPECTED_LAST_COMPATIBLE_COUNTS,
        "EXPECTED_WAVE_PROJECTION_DIGEST": EXPECTED_WAVE_PROJECTION_DIGEST,
        "EXPECTED_PHASE_FIBER_HISTOGRAM": EXPECTED_PHASE_FIBER_HISTOGRAM,
        "_power_tables": _power_tables,
        "_q011cj_framed_record_digest": _q011cr_framed_record_digest,
        "_q011cj_exact_fraction_sequence_sha256": (_q011cr_exact_fraction_sequence_sha256),
    }


@contextmanager
def _q011cj_protocol_context() -> Iterator[None]:
    overrides = _protocol_overrides()
    original = {name: getattr(q011cj, name) for name in overrides}
    try:
        for name, value in overrides.items():
            setattr(q011cj, name, value)
        yield
    finally:
        for name, value in original.items():
            setattr(q011cj, name, value)


def _protocol_globals_are_restored() -> bool:
    return bool(
        all(getattr(q011cj, name) == value for name, value in _PROTOCOL_BASELINE.items())
        and q011cj._protocol_globals_are_restored()
        and q011cq._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011cq._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011cq_degree34_eighth_individual_partition_audit.json"
    )
    runner_path = Path(q011cq.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    fixed = cycle["fixed_individual_partition_input_audit"]
    partition = cycle["individual_allocation_interval_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CQ_DIGEST_NAMES)
    checks = {
        "q011cq_seventy_three_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 73
            and prior["direct_digest_count"] == 341
            and len(artifacts) == 73
            and all(prior["checks"].values())
        ),
        "q011cq_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CQ_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CQ_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CQ_RUNNER_SHA256
        ),
        "q011cq_section_digests_match": digests == Q011CQ_DIGESTS,
        "q011cq_valid_interval_inert_outcome_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "partition_inert_persistent"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["individual_partition_is_interval_inert_for_eighth_q011cb_witness"]
            and theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
            and theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011cq_parent_partition_and_relations_reproduce": bool(
            fixed["eighth_parent_witness_selection_audit"]["selected_flat_ordinal"]
            == PARENT_FLAT_ORDINAL
            and fixed["compatible_allocation_count"] == EXPECTED_WAVE_PROJECTION_COUNT
            and fixed["compatible_allocation_digest_sha256"] == q011cq.EXPECTED_COMPATIBLE_DIGEST
            and partition["compatible_allocation_count"] == EXPECTED_WAVE_PROJECTION_COUNT
            and partition["exact_relation_counts"]
            == {
                "product_below_target": 0,
                "target_below_product": 0,
                "overlap": EXPECTED_WAVE_PROJECTION_COUNT,
            }
            and partition["all_product_target_intersection_and_center_records_equal_parent"]
            and partition["allocation_classification_record_digest_sha256"]
            == EXPECTED_Q011CQ_ALLOCATION_RECORD_DIGEST
        ),
        "q011cq_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "three_hundred_forty_five_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 345
        ),
    }
    artifacts["q011cq"] = artifact
    return (
        {
            "prior_q011cq_sealed_input_audit": prior,
            "q011cq": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CQ_DIGEST_NAMES),
                "digests": list(digests),
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _fixed_phase_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[_ExactDisc, ...],
    _ExactDisc,
    tuple[dict[str, Any], ...],
]:
    adapted = dict(artifacts)
    adapted["q011ci"] = artifacts["q011cq"]
    with _q011cj_protocol_context():
        audit, sources, target, wave_compatible = q011cj._fixed_phase_input_audit(adapted)
    audit["checks"]["q011cq_fixed_parent_and_interval_partition_replay_bitwise"] = audit[
        "checks"
    ].pop("q011ci_fixed_parent_and_interval_partition_replay_bitwise")
    audit["q011cq_compatible_wave_allocation_count"] = audit.pop(
        "q011ci_compatible_wave_allocation_count"
    )
    audit["q011cq_compatible_wave_allocation_digest_sha256"] = audit.pop(
        "q011ci_compatible_wave_allocation_digest_sha256"
    )
    audit["checks"]["q011cj_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    audit["passed"] = all(audit["checks"].values())
    return audit, sources, target, wave_compatible


def _allocation_inventory(
    source_discs: tuple[_ExactDisc, ...],
    wave_compatible: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    records = []
    for count_16_145 in range(14):
        for count_16_150 in range(10):
            for count_16_151 in range(10 - count_16_150):
                for count_1_150 in range(10 - count_16_150 - count_16_151):
                    count_1_151 = 9 - count_16_150 - count_16_151 - count_1_150
                    for count_16_152 in range(6):
                        for count_16_148 in range(8):
                            for count_16_149 in range(1):
                                counts = [
                                    count_16_145,
                                    13 - count_16_145,
                                    count_16_150,
                                    count_16_151,
                                    count_1_150,
                                    count_1_151,
                                    count_16_152,
                                    5 - count_16_152,
                                    count_16_148,
                                    7 - count_16_148,
                                    count_16_149,
                                    0 - count_16_149,
                                ]
                                output_block = (
                                    sum(
                                        count * disc.block_index
                                        for count, disc in zip(
                                            counts,
                                            source_discs,
                                            strict=True,
                                        )
                                    )
                                    % SIZE
                                )
                                records.append(
                                    {
                                        "counts": counts,
                                        "output_block": output_block,
                                        "compatible": output_block == OUTPUT_BLOCK,
                                    }
                                )
    compatible = tuple(record for record in records if record["compatible"])
    projection = Counter(
        (
            record["counts"][0],
            record["counts"][1],
            record["counts"][2] + record["counts"][3],
            record["counts"][4] + record["counts"][5],
            record["counts"][6],
            record["counts"][7],
            record["counts"][8],
            record["counts"][9],
        )
        for record in compatible
    )
    projection_records = [
        {"wave_counts": list(counts), "phase_allocation_count": projection[counts]}
        for counts in sorted(projection)
    ]
    wave_counts = {tuple(record["individual_counts"]) for record in wave_compatible}
    fiber_histogram = dict(sorted(Counter(projection.values()).items()))
    full_digest = q011b._canonical_json_sha256(records)
    compatible_digest = q011b._canonical_json_sha256(list(compatible))
    projection_digest = q011b._canonical_json_sha256(projection_records)
    checks = {
        "full_component_safe_allocation_inventory_reproduces": bool(
            len(records) == EXPECTED_FULL_ALLOCATION_COUNT
            and full_digest == EXPECTED_FULL_ALLOCATION_DIGEST
        ),
        "compatible_component_safe_allocation_inventory_reproduces": bool(
            len(compatible) == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            and compatible_digest == EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
            and tuple(compatible[0]["counts"]) == EXPECTED_FIRST_COMPATIBLE_COUNTS
            and tuple(compatible[-1]["counts"]) == EXPECTED_LAST_COMPATIBLE_COUNTS
        ),
        "all_count_degree_and_wave_constraints_close": all(
            sum(record["counts"]) == DEGREE
            and record["counts"][0] + record["counts"][1] == 13
            and sum(record["counts"][2:6]) == 9
            and record["counts"][6] + record["counts"][7] == 5
            and record["counts"][8] + record["counts"][9] == 7
            and record["counts"][10] + record["counts"][11] == 0
            and all(count >= 0 for count in record["counts"])
            and record["output_block"] == OUTPUT_BLOCK
            for record in compatible
        ),
        "projection_matches_all_q011cq_wave_allocations": bool(
            set(projection) == wave_counts
            and len(projection) == len(wave_counts) == EXPECTED_WAVE_PROJECTION_COUNT
            and projection_digest == EXPECTED_WAVE_PROJECTION_DIGEST
        ),
        "all_phase_fibers_are_nonempty_and_registered": bool(
            min(projection.values()) == 10
            and max(projection.values()) == 30
            and sum(projection.values()) == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            and fiber_histogram == EXPECTED_PHASE_FIBER_HISTOGRAM
        ),
        "allocation_summary_is_finite_strict_json": bool(
            _all_numeric_values_finite(projection_records)
            and _strict_json_serializable(projection_records)
            and json.dumps(projection_records, allow_nan=False)
        ),
    }
    return (
        {
            "source_variant_order": [disc.identifier for disc in source_discs],
            "full_allocation_count": len(records),
            "full_allocation_digest_sha256": full_digest,
            "compatible_allocation_count": len(compatible),
            "compatible_allocation_digest_sha256": compatible_digest,
            "first_compatible_counts": compatible[0]["counts"],
            "last_compatible_counts": compatible[-1]["counts"],
            "wave_projection_count": len(projection_records),
            "wave_projection_records": projection_records,
            "wave_projection_record_digest_sha256": projection_digest,
            "minimum_phase_allocations_per_wave": min(projection.values()),
            "maximum_phase_allocations_per_wave": max(projection.values()),
            "phase_allocation_count_per_wave_histogram": {
                str(count): frequency for count, frequency in fiber_histogram.items()
            },
            "full_allocation_records_retained": False,
            "compatible_allocation_records_retained": False,
            "checks": checks,
            "passed": all(checks.values()),
        },
        compatible,
    )


def _phase_product_audit(
    source_discs: tuple[_ExactDisc, ...],
    target: _ExactDisc,
    compatible: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    with _q011cj_protocol_context():
        comparison = q011cj._phase_product_audit(
            source_discs,
            target,
            compatible,
        )
    comparison["comparison_stream_domain"] = "q011cr-component-safe-phase-comparisons-v1"
    comparison["checks"]["q011cj_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    comparison["passed"] = all(comparison["checks"].values())
    return comparison


def _registered_parameters() -> dict[str, Any]:
    with _q011cj_protocol_context():
        registered = q011cj._registered_parameters()
    registered["q011cj_protocol_adapter"] = {
        "source_runner_sha256": _file_sha256(Path(q011cj.__file__).resolve()),
        "temporary_override_names": sorted(_PROTOCOL_NAMES),
        "globals_restored_after_use": _protocol_globals_are_restored(),
    }
    return registered


_result_digest_sections = q011cj._result_digest_sections


def run_degree_thirty_four_eighth_component_safe_phase_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    phase_input, sources, target, wave_compatible = _fixed_phase_input_audit(artifacts)
    allocation, compatible = _allocation_inventory(sources, wave_compatible)
    comparison = _phase_product_audit(sources, target, compatible)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    phase_input_sections = {"fixed_component_safe_phase_input_audit": phase_input}
    allocation_sections = {"component_safe_phase_allocation_audit": allocation}
    comparison_sections = {"complex_phase_product_disc_audit": comparison}
    input_digest = q011b._canonical_json_sha256(input_sections)
    phase_input_digest = q011b._canonical_json_sha256(phase_input_sections)
    allocation_digest = q011b._canonical_json_sha256(allocation_sections)
    comparison_digest = q011b._canonical_json_sha256(comparison_sections)
    validity_gates = {
        "q011cq_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "74 artifacts and 345 direct digests reproduce",
            "value": sealed["checks"],
        },
        "q011cq_parent_partition_and_interval_inert_result_replay": {
            "passed": phase_input["checks"][
                "q011cq_fixed_parent_and_interval_partition_replay_bitwise"
            ],
            "threshold": "ordinal 7, 382 wave allocations and inert result replay",
            "value": phase_input["q011cq_compatible_wave_allocation_digest_sha256"],
        },
        "exact_centers_radii_components_and_target_reproduce": {
            "passed": bool(
                phase_input["checks"]["q011k_centers_and_q011ak_block_radii_reconstruct"]
                and phase_input["checks"]["registered_source_and_target_phase_records_reproduce"]
                and phase_input["checks"][
                    "active_singleton_and_two_row_components_have_exact_multiplicity"
                ]
            ),
            "threshold": "twelve source discs, one target and components reproduce",
            "value": {
                "source": phase_input["source_phase_disc_record_digest_sha256"],
                "target": phase_input["target_phase_disc_record_digest_sha256"],
            },
        },
        "containment_conjugacy_and_label_free_semantics_pass": {
            "passed": bool(
                phase_input["checks"]["row_discs_are_contained_in_q011am_and_q011ak"]
                and phase_input["checks"]["block_discs_and_target_replay_the_q011ak_formula"]
                and phase_input["checks"]["all_conjugate_source_pairs_transport_exactly"]
                and phase_input["checks"]["component_union_semantics_do_not_assign_internal_labels"]
            ),
            "threshold": "safe containment, six conjugate pairs and no internal labels",
            "value": phase_input["checks"],
        },
        "component_safe_allocation_and_wave_projection_reproduce": {
            "passed": allocation["passed"],
            "threshold": "147840 total, 8350 compatible and 382 nonempty wave fibers",
            "value": allocation["checks"],
        },
        "exact_product_radius_distance_and_categories_close": {
            "passed": comparison["passed"],
            "threshold": (
                "8350 exact products, ten radius signatures, sqrt enclosures and "
                "exclusive categories"
            ),
            "value": comparison["checks"],
        },
        "strict_stream_section_digests_runner_and_protocol_provenance_reproduce": {
            "passed": bool(
                comparison["comparison_stream_count"] == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
                and all(
                    len(value) == 64
                    for value in (
                        input_digest,
                        phase_input_digest,
                        allocation_digest,
                        comparison_digest,
                        comparison["comparison_stream_digest_sha256"],
                    )
                )
                and runner["filename"] == "q011cr_degree34_eighth_component_safe_phase_discs.py"
                and _protocol_globals_are_restored()
            ),
            "threshold": ("framed stream, four section digests, runner and restored protocol"),
            "value": {
                "input": input_digest,
                "phase_input": phase_input_digest,
                "allocation": allocation_digest,
                "comparison": comparison_digest,
                "stream": comparison["comparison_stream_digest_sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    unresolved_count = comparison["category_counts"]["unresolved_product_disk_overlap"]
    global_margin = q011z._fraction(
        comparison["global_minimum_margin_witness"]["complex_separation_margin_lower"]["exact"]
    )
    resolved = validity_passed and unresolved_count == 0 and global_margin > 0
    persistent = validity_passed and not resolved
    diagnostic_gates = {
        "only_the_registered_eighth_q011cb_witness_is_refined": {
            "passed": bool(
                not comparison["previous_q011cb_refined_signatures_recomputed"]
                and not comparison["later_q011cb_refined_signatures_recomputed"]
                and not comparison["other_parent_targets_recomputed"]
                and not comparison["other_parent_coalesced_overlaps_recomputed"]
            ),
            "threshold": "ordinal 7 only, one target and no other overlap",
            "value": PARENT_FLAT_ORDINAL,
        },
        "all_component_safe_phase_product_discs_are_processed": {
            "passed": bool(
                validity_passed
                and sum(comparison["category_counts"].values())
                == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            ),
            "threshold": "all 8350 compatible phase allocations have one category",
            "value": comparison["category_counts"],
        },
        "registered_resolution_stopping_rule_is_applied": {
            "passed": bool(resolved or persistent),
            "threshold": "zero unresolved and positive minimum, or retained obstruction",
            "value": {
                "unresolved": unresolved_count,
                "global_minimum_margin_sign": (global_margin > 0) - (global_margin < 0),
            },
        },
        "scientific_boundary_is_preserved": {
            "passed": True,
            "threshold": "no degree-34, actual-resonance, all-order or SSM claim",
            "value": "certified 2--33 and 91+, missing 34--90",
        },
    }
    refinement_outcome = (
        "component_safe_phase_resolved"
        if resolved
        else "component_safe_phase_persistent"
        if persistent
        else "inconclusive"
    )
    classification = (
        RESOLVED_CLASSIFICATION
        if resolved
        else PERSISTENT_CLASSIFICATION
        if persistent
        else INCONCLUSIVE_CLASSIFICATION
    )
    cycle = {
        "question": (
            "Do label-free Q011an component-row unions and Q011ak block discs "
            "strictly separate every complex product in Q011cb flatten ordinal 7?"
        ),
        **input_sections,
        **phase_input_sections,
        **allocation_sections,
        **comparison_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "phase_input_digest_sha256": phase_input_digest,
        "allocation_digest_sha256": allocation_digest,
        "phase_comparison_digest_sha256": comparison_digest,
        "validity_gates": validity_gates,
        "diagnostic_gates": diagnostic_gates,
        "failed_validity_order": [
            name for name, gate in validity_gates.items() if not gate["passed"]
        ],
        "failed_diagnostic_order": [
            name for name, gate in diagnostic_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "refinement_outcome": refinement_outcome,
        "diagnostic_classification": classification,
        "scientific_outcome": "not_evaluated",
        "actual_resonance_outcome": ("not_established" if validity_passed else "inconclusive"),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "component_safe_complex_phase_discs_resolve_eighth_q011cb_witness": (resolved),
        "eighth_q011cb_witness_persists_under_component_safe_phase_discs": (persistent),
        "q011an_component_internal_eigenvalue_labels_are_assumed": False,
        "q011cq_interval_inert_diagnostic_is_preserved": True,
        "q011cp_ordinal_six_phase_resolution_is_preserved": True,
        "q011cn_ordinal_five_phase_resolution_is_preserved": True,
        "q011cl_ordinal_four_phase_resolution_is_preserved": True,
        "q011cj_ordinal_three_phase_resolution_is_preserved": True,
        "q011ch_ordinal_two_phase_resolution_is_preserved": True,
        "q011cf_ordinal_one_phase_resolution_is_preserved": True,
        "q011cd_ordinal_zero_phase_resolution_is_preserved": True,
        "q011cb_persistent_diagnostic_is_preserved": True,
        "q011ca_first_family_phase_resolution_is_preserved": True,
        "q011bx_degree_thirty_four_sufficient_certificate_remains_rejected": True,
        "degree_thirty_four_external_nonresonance_is_certified": False,
        "an_actual_degree_thirty_four_external_resonance_is_established": False,
        "certified_external_nonresonance_degrees": list(range(2, 34)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(34, 91)),
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only the fixed 17x17 repaired exact map on one "
        "fixed conservation leaf, degree-34 parent aggregate 2340, Q011cb flatten "
        "ordinal 7, its 8350 registered component-safe phase allocations and "
        "target block=7;center=44. It does not reevaluate ordinals 0 through 6 or "
        "classify the later 44792 Q011cb refined signatures, the other 31 parent "
        "coalesced overlaps, other targets, aggregate 2340 as a whole, aggregate "
        "972 or the full degree-34 sweep. Product-disc overlap does not establish "
        "an actual resonance. The audit leaves all prior rejection, persistence, "
        "interval-inert and phase-resolution results, certified degrees 2--33 and "
        "91+, and missing degrees 34--90 unchanged, and makes no claim about "
        "degree-34 or all-order nonresonance, higher graph smoothness, SSM "
        "existence or uniqueness, normal attraction, a basin, other grids, "
        "forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cs to audit the next Q011cb refined overlap in registered order."
        if resolved
        else (
            "Preregister Q011cs to refine only the first unresolved component-safe phase witness."
        )
        if persistent
        else "Repair only the first Q011cr validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011cr cycle failed strict serialization or digest")
    return cycle


def run_q011cr_study() -> dict[str, Any]:
    started = perf_counter()
    cycle = run_degree_thirty_four_eighth_component_safe_phase_audit()
    elapsed = perf_counter() - started
    comparison = cycle["complex_phase_product_disc_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_input_scalar_type": "fractions.Fraction",
            "center_distance_enclosure": "integer-isqrt rational bounds via Q011o",
            "product_disc_radius": "exact rational closed form and factor recurrence",
            "fourier_compatibility": "exact block-index sum modulo 17",
            "target_comparisons": comparison["compatible_phase_allocation_count"],
            "full_comparison_records_retained": False,
            "elapsed_seconds": elapsed,
            "floating_point_used_for_gate_decisions": False,
            "protocol_globals_restored_after_use": (_protocol_globals_are_restored()),
        },
        "mathematical_scope": {
            "diagnostic": "eighth Q011cb witness component-safe complex phase discs",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
            "target_identifier": TARGET_IDENTIFIER,
            "component_internal_eigenvalue_labels_assumed": False,
            "degree_thirty_four_nonresonance_claim": False,
            "actual_resonance_claim": False,
            "all_order_nonresonance_claim": False,
            "ssm_uniqueness_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "refinement_outcome": cycle["refinement_outcome"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011cr_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
