"""Q011cx component-safe complex phase discs for Q011cb flatten ordinal ten."""

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

import research.q011ch_degree34_third_component_safe_phase_discs as q011ch
import research.q011cj_degree34_fourth_component_safe_phase_discs as q011cj
import research.q011cv_degree34_tenth_component_safe_phase_discs as q011cv
import research.q011cw_degree34_eleventh_individual_partition_audit as q011cw
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011cw.q011b
q011z = q011cw.q011z

_ExactDisc = q011cv._ExactDisc

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
PARENT_FLAT_ORDINAL = 10
OUTPUT_BLOCK = 7
TARGET_IDENTIFIER = "block=7;center=44"

SOURCE_VARIANTS = q011cv.SOURCE_VARIANTS
EXPECTED_SOURCE_RADIUS_HEX = q011cv.EXPECTED_SOURCE_RADIUS_HEX
EXPECTED_TARGET_RADIUS_HEX = q011cv.EXPECTED_TARGET_RADIUS_HEX
EXPECTED_SOURCE_RECORD_DIGEST = q011cv.EXPECTED_SOURCE_RECORD_DIGEST
EXPECTED_TARGET_RECORD_DIGEST = q011cv.EXPECTED_TARGET_RECORD_DIGEST

EXPECTED_FULL_ALLOCATION_COUNT = 332_640
EXPECTED_COMPATIBLE_ALLOCATION_COUNT = 18_718
EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT = 1_531
EXPECTED_WAVE_PROJECTION_COUNT = 852
EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT = 10
EXPECTED_FULL_ALLOCATION_DIGEST = "3ec75e818c2fddf04cf9f6a9ea6847553ab6fd6dbd0d58088631923e9f647619"
EXPECTED_COMPATIBLE_ALLOCATION_DIGEST = (
    "bdcbb44f66d1d0dbcd818dbf280ef60f762d29528932875d25f60d03ab168671"
)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 0, 0, 9, 0, 5, 0, 2, 5, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = (13, 0, 9, 0, 0, 0, 0, 5, 0, 2, 0, 5)
EXPECTED_WAVE_PROJECTION_DIGEST = "629cf594b5adbb8f10c66daf11f6bff80d91c667a7d4f641f164a804ca96e5e2"
EXPECTED_PHASE_FIBER_HISTOGRAM = {10: 173, 18: 169, 24: 169, 28: 170, 30: 171}
EXPECTED_BRIDGE_FIBER_HISTOGRAM = {1: 173, 2: 679}
EXPECTED_BRIDGE_RECORD_DIGEST = "c6ab582a7be8cb48a791eef78b2ed053fe03f117e01d9caaeaf09ff9d66da462"
EXPECTED_PAIRED_RECORD_DIGEST = "c52742dd901e00bf537f26e7e4bb6d5b0e9fe44889274385529ae5971af3c58f"

Q011CW_ARTIFACT_SHA256 = "88f4f7b05675c58c523f58910b1c795507c92cceea89006658862722be7be355"
Q011CW_RUNNER_SHA256 = "4053f6f3738331414e2b1620a7892b1cadfbbdd98f104c3bb52a676e3291093e"
Q011CW_DIGEST_NAMES = (
    "input_digest_sha256",
    "partition_input_digest_sha256",
    "allocation_audit_digest_sha256",
    "result_digest_sha256",
)
Q011CW_DIGESTS = (
    "6a59a48d974eb6d42af91ee12bfe9b927b4d7ce477340748bc85ca805233882d",
    "53acd6d0d2638c5939ee367de45d3e4a260346e4f9edde4f2ae5a362389f44c8",
    "023b5b1c20f87a84eb63ac43b5ebe47cb3a62e05adbb31a0d46d6add5ddee66b",
    "5b34510714ab89816f2f1e1830f2b4fa4d91c678b0401821aa11baff31da4da5",
)
EXPECTED_Q011CW_ALLOCATION_RECORD_DIGEST = (
    "4998d8e6dc452f53f25b80ef8484d0326e02e20de22550891ae2ff924375fa95"
)

RESOLVED_CLASSIFICATION = (
    "the component-safe complex phase discs resolve the eleventh Q011cb persistent refined witness"
)
PERSISTENT_CLASSIFICATION = (
    "the eleventh Q011cb persistent refined witness persists under component-safe "
    "complex phase discs"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011cx component-safe phase-disc audit is inconclusive"

_BASE_FRAMED_RECORD_DIGEST = q011cv._BASE_FRAMED_RECORD_DIGEST
_BASE_EXACT_FRACTION_SEQUENCE_SHA256 = q011cv._BASE_EXACT_FRACTION_SEQUENCE_SHA256
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


def _q011cx_framed_record_digest(domain: str) -> Any:
    if domain != "q011ch-component-safe-phase-comparisons-v1":
        raise ValueError(f"unexpected inherited comparison domain: {domain}")
    return _BASE_FRAMED_RECORD_DIGEST("q011cx-component-safe-phase-comparisons-v1")


def _q011cx_exact_fraction_sequence_sha256(
    domain: bytes,
    values: tuple[Fraction, ...],
) -> str:
    if domain == b"q011ch-complex-margin-expression-v1":
        domain = b"q011cx-complex-margin-expression-v1"
    return _BASE_EXACT_FRACTION_SEQUENCE_SHA256(domain, values)


def _protocol_overrides() -> dict[str, Any]:
    return {
        "q011ci": q011cw,
        "PARENT_FLAT_ORDINAL": PARENT_FLAT_ORDINAL,
        "EXPECTED_FULL_ALLOCATION_COUNT": EXPECTED_FULL_ALLOCATION_COUNT,
        "EXPECTED_COMPATIBLE_ALLOCATION_COUNT": EXPECTED_COMPATIBLE_ALLOCATION_COUNT,
        "EXPECTED_WAVE_PROJECTION_COUNT": EXPECTED_WAVE_PROJECTION_COUNT,
        "EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT": EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT,
        "EXPECTED_FULL_ALLOCATION_DIGEST": EXPECTED_FULL_ALLOCATION_DIGEST,
        "EXPECTED_COMPATIBLE_ALLOCATION_DIGEST": EXPECTED_COMPATIBLE_ALLOCATION_DIGEST,
        "EXPECTED_FIRST_COMPATIBLE_COUNTS": EXPECTED_FIRST_COMPATIBLE_COUNTS,
        "EXPECTED_LAST_COMPATIBLE_COUNTS": EXPECTED_LAST_COMPATIBLE_COUNTS,
        "EXPECTED_WAVE_PROJECTION_DIGEST": EXPECTED_WAVE_PROJECTION_DIGEST,
        "EXPECTED_PHASE_FIBER_HISTOGRAM": EXPECTED_PHASE_FIBER_HISTOGRAM,
        "_power_tables": q011ch._power_tables,
        "_q011cj_framed_record_digest": _q011cx_framed_record_digest,
        "_q011cj_exact_fraction_sequence_sha256": (_q011cx_exact_fraction_sequence_sha256),
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
        and q011cw._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011cw._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011cw_degree34_eleventh_individual_partition_audit.json"
    )
    runner_path = Path(q011cw.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    fixed = cycle["fixed_individual_partition_input_audit"]
    partition = cycle["individual_allocation_interval_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CW_DIGEST_NAMES)
    checks = {
        "q011cw_seventy_nine_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 79
            and prior["direct_digest_count"] == 368
            and len(artifacts) == 79
            and all(prior["checks"].values())
        ),
        "q011cw_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CW_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CW_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CW_RUNNER_SHA256
        ),
        "q011cw_section_digests_match": digests == Q011CW_DIGESTS,
        "q011cw_valid_interval_inert_outcome_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "partition_inert_persistent"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["individual_partition_is_interval_inert_for_eleventh_q011cb_witness"]
            and theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
            and theorem["q011ct_ordinal_eight_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011cw_parent_partition_and_relations_reproduce": bool(
            fixed["eleventh_parent_witness_selection_audit"]["selected_flat_ordinal"]
            == PARENT_FLAT_ORDINAL
            and fixed["compatible_allocation_count"] == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and fixed["compatible_allocation_digest_sha256"] == q011cw.EXPECTED_COMPATIBLE_DIGEST
            and partition["compatible_allocation_count"]
            == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and partition["exact_relation_counts"]
            == {
                "product_below_target": 0,
                "target_below_product": 0,
                "overlap": EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT,
            }
            and partition["all_product_target_intersection_and_center_records_equal_parent"]
            and partition["allocation_classification_record_digest_sha256"]
            == EXPECTED_Q011CW_ALLOCATION_RECORD_DIGEST
        ),
        "q011cw_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "three_hundred_seventy_two_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 372
        ),
    }
    artifacts["q011cw"] = artifact
    return (
        {
            "prior_q011cw_sealed_input_audit": prior,
            "q011cw": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CW_DIGEST_NAMES),
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
    fixed, lookup, replay_wave_compatible, parent = q011cw._fixed_individual_input_audit(artifacts)
    partition = q011cw._individual_partition_audit(lookup, replay_wave_compatible, parent)
    stored = artifacts["q011cw"]["cycle"]
    parent_replay_passed = bool(
        fixed == stored["fixed_individual_partition_input_audit"]
        and partition == stored["individual_allocation_interval_audit"]
        and fixed["passed"]
        and partition["passed"]
    )
    adapted = dict(artifacts)
    adapted["q011ci"] = artifacts["q011cw"]
    with _q011cj_protocol_context():
        audit, sources, target, _ = q011cj._fixed_phase_input_audit(adapted)
    audit["checks"].pop("q011ci_fixed_parent_and_interval_partition_replay_bitwise")
    audit["checks"]["q011cw_fixed_parent_and_interval_partition_replay_bitwise"] = (
        parent_replay_passed
    )
    audit["q011cw_compatible_wave_allocation_count"] = audit.pop(
        "q011ci_compatible_wave_allocation_count"
    )
    audit["q011cw_compatible_wave_allocation_digest_sha256"] = audit.pop(
        "q011ci_compatible_wave_allocation_digest_sha256"
    )
    audit["checks"]["q011cj_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    audit["passed"] = all(audit["checks"].values())
    return audit, sources, target, replay_wave_compatible


def _component_wave_counts(individual_counts: tuple[int, ...]) -> tuple[int, ...]:
    if len(individual_counts) != 12:
        raise ValueError("Q011cx requires twelve Q011cw individual counts")
    return (
        individual_counts[0],
        individual_counts[1],
        individual_counts[2] + individual_counts[4],
        individual_counts[3] + individual_counts[5],
        individual_counts[6],
        individual_counts[7],
        individual_counts[8],
        individual_counts[9],
        individual_counts[10],
        individual_counts[11],
    )


def _allocation_inventory(
    source_discs: tuple[_ExactDisc, ...],
    wave_compatible: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    individual_counts = tuple(tuple(record["individual_counts"]) for record in wave_compatible)
    bridge = Counter(_component_wave_counts(counts) for counts in individual_counts)
    bridge_records = [
        {
            "component_wave_counts": list(counts),
            "individual_wave_allocation_count": bridge[counts],
        }
        for counts in sorted(bridge)
    ]
    bridge_histogram = dict(sorted(Counter(bridge.values()).items()))
    bridge_digest = q011b._canonical_json_sha256(bridge_records)
    component_wave_records = tuple({"individual_counts": list(counts)} for counts in sorted(bridge))
    allocation, compatible = q011ch._allocation_inventory(
        source_discs,
        component_wave_records,
    )
    allocation["checks"]["phase_projection_matches_component_wave_quotient"] = allocation[
        "checks"
    ].pop("projection_matches_all_q011cg_wave_allocations")
    projection = {
        tuple(record["wave_counts"]): record["phase_allocation_count"]
        for record in allocation["wave_projection_records"]
    }
    paired_records = [
        {
            "component_wave_counts": list(counts),
            "individual_wave_allocation_count": bridge[counts],
            "phase_allocation_count": projection[counts],
        }
        for counts in sorted(projection)
    ]
    paired_digest = q011b._canonical_json_sha256(paired_records)
    bridge_constraints_close = all(
        sum(counts) == DEGREE
        and counts[0] + counts[1] == 13
        and counts[2] + counts[3] == 1
        and counts[4] + counts[5] == 8
        and counts[6] + counts[7] == 5
        and counts[8] + counts[9] == 2
        and counts[10] + counts[11] == 5
        and all(count >= 0 for count in counts)
        and (
            sum(
                count * block
                for count, block in zip(
                    counts,
                    (16, 1, 16, 1, 16, 1, 16, 1, 16, 1, 16, 1),
                    strict=True,
                )
            )
            % SIZE
            == OUTPUT_BLOCK
        )
        for counts in individual_counts
    )
    allocation["checks"]["individual_to_component_wave_bridge_reproduces"] = bool(
        len(individual_counts) == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
        and len(set(individual_counts)) == len(individual_counts)
        and sum(bridge.values()) == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
        and len(bridge) == EXPECTED_WAVE_PROJECTION_COUNT
        and min(bridge.values()) == 1
        and max(bridge.values()) == 2
        and bridge_histogram == EXPECTED_BRIDGE_FIBER_HISTOGRAM
        and bridge_digest == EXPECTED_BRIDGE_RECORD_DIGEST
        and bridge_constraints_close
    )
    allocation["checks"]["bridge_phase_pairing_reproduces"] = bool(
        set(projection) == set(bridge) and paired_digest == EXPECTED_PAIRED_RECORD_DIGEST
    )
    allocation.update(
        {
            "individual_wave_allocation_count": len(individual_counts),
            "component_wave_projection_count": len(bridge_records),
            "individual_to_component_bridge_records": bridge_records,
            "individual_to_component_bridge_record_digest_sha256": bridge_digest,
            "minimum_individual_allocations_per_component_wave": min(bridge.values()),
            "maximum_individual_allocations_per_component_wave": max(bridge.values()),
            "individual_allocation_count_per_component_wave_histogram": {
                str(count): frequency for count, frequency in bridge_histogram.items()
            },
            "bridge_phase_paired_records": paired_records,
            "bridge_phase_paired_record_digest_sha256": paired_digest,
            "allocation_protocol_adapter": {
                "source_runner_sha256": _file_sha256(Path(q011ch.__file__).resolve()),
                "component_wave_records_replace_q011cg_wave_records": True,
                "protocol_globals_modified": False,
            },
        }
    )
    allocation["passed"] = all(allocation["checks"].values())
    return allocation, compatible


def _phase_product_audit(
    source_discs: tuple[_ExactDisc, ...],
    target: _ExactDisc,
    compatible: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    with _q011cj_protocol_context():
        comparison = q011cj._phase_product_audit(source_discs, target, compatible)
    comparison["comparison_stream_domain"] = "q011cx-component-safe-phase-comparisons-v1"
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
    registered["q011ch_allocation_adapter"] = {
        "source_runner_sha256": _file_sha256(Path(q011ch.__file__).resolve()),
        "component_wave_records_replace_q011cg_wave_records": True,
        "protocol_globals_modified": False,
    }
    registered["component_label_coalescing_bridge"] = {
        "individual_identifier_count": 12,
        "component_wave_identifier_count": 10,
        "individual_wave_allocation_count": EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT,
        "component_wave_projection_count": EXPECTED_WAVE_PROJECTION_COUNT,
        "bridge_record_digest_sha256": EXPECTED_BRIDGE_RECORD_DIGEST,
        "paired_record_digest_sha256": EXPECTED_PAIRED_RECORD_DIGEST,
        "internal_component_labels_assumed": False,
    }
    return registered


_result_digest_sections = q011cj._result_digest_sections


def run_degree_thirty_four_eleventh_component_safe_phase_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    phase_input, sources, target, wave_compatible = _fixed_phase_input_audit(artifacts)
    allocation, compatible = _allocation_inventory(sources, wave_compatible)
    comparison = _phase_product_audit(sources, target, compatible)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    phase_input_sections = {"fixed_component_safe_phase_input_audit": phase_input}
    allocation_sections = {"component_safe_phase_allocation_audit": allocation}
    comparison_sections = {"complex_phase_product_disc_audit": comparison}
    input_digest = q011b._canonical_json_sha256(input_sections)
    phase_input_digest = q011b._canonical_json_sha256(phase_input_sections)
    allocation_digest = q011b._canonical_json_sha256(allocation_sections)
    comparison_digest = q011b._canonical_json_sha256(comparison_sections)
    validity_gates = {
        "q011cw_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "80 artifacts and 372 direct digests reproduce",
            "value": sealed["checks"],
        },
        "q011cw_parent_partition_and_interval_inert_result_replay": {
            "passed": phase_input["checks"][
                "q011cw_fixed_parent_and_interval_partition_replay_bitwise"
            ],
            "threshold": ("ordinal 10, 1531 individual wave allocations and inert result replay"),
            "value": phase_input["q011cw_compatible_wave_allocation_digest_sha256"],
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
        "component_safe_allocation_and_component_quotient_reproduce": {
            "passed": allocation["passed"],
            "threshold": (
                "1531 individual waves quotient to 852 component waves; "
                "332640 total and 18718 compatible phase allocations"
            ),
            "value": allocation["checks"],
        },
        "exact_product_radius_distance_and_categories_close": {
            "passed": comparison["passed"],
            "threshold": (
                "18718 exact products, ten radius signatures, sqrt enclosures and "
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
                and runner["filename"] == "q011cx_degree34_eleventh_component_safe_phase_discs.py"
                and _protocol_globals_are_restored()
            ),
            "threshold": "framed stream, four section digests, runner and restored protocol",
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
        "only_the_registered_eleventh_q011cb_witness_is_refined": {
            "passed": bool(
                not comparison["previous_q011cb_refined_signatures_recomputed"]
                and not comparison["later_q011cb_refined_signatures_recomputed"]
                and not comparison["other_parent_targets_recomputed"]
                and not comparison["other_parent_coalesced_overlaps_recomputed"]
            ),
            "threshold": "ordinal 10 only, one target and no other overlap",
            "value": PARENT_FLAT_ORDINAL,
        },
        "all_component_safe_phase_product_discs_are_processed": {
            "passed": bool(
                validity_passed
                and sum(comparison["category_counts"].values())
                == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            ),
            "threshold": "all 18718 compatible phase allocations have one category",
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
            "strictly separate every complex product in Q011cb flatten ordinal 10?"
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
        "actual_resonance_outcome": "not_established" if validity_passed else "inconclusive",
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "component_safe_complex_phase_discs_resolve_eleventh_q011cb_witness": resolved,
        "eleventh_q011cb_witness_persists_under_component_safe_phase_discs": persistent,
        "q011an_component_internal_eigenvalue_labels_are_assumed": False,
        "q011cw_interval_inert_diagnostic_is_preserved": True,
        "q011cv_ordinal_nine_phase_resolution_is_preserved": True,
        "q011ct_ordinal_eight_phase_resolution_is_preserved": True,
        "q011cr_ordinal_seven_phase_resolution_is_preserved": True,
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
        "ordinal 10, its 1531-to-852 component-wave quotient and 18718 registered "
        "component-safe phase allocations and target block=7;center=44. It does not "
        "reevaluate ordinals 0 through 9 or classify the later 44789 Q011cb refined "
        "signatures, the other 31 parent coalesced overlaps, other targets, aggregate "
        "2340 as a whole, aggregate 972 or the full degree-34 sweep. Product-disc "
        "overlap does not establish an actual resonance. The audit leaves all prior "
        "rejection, persistence, interval-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about degree-34 or all-order nonresonance, higher graph "
        "smoothness, SSM existence or uniqueness, normal attraction, a basin, other "
        "grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cy to audit the next Q011cb refined overlap in registered order."
        if resolved
        else (
            "Preregister Q011cy to refine only the first unresolved component-safe phase witness."
        )
        if persistent
        else "Repair only the first Q011cx validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011cx cycle failed strict serialization or digest")
    return cycle


def run_q011cx_study() -> dict[str, Any]:
    started = perf_counter()
    cycle = run_degree_thirty_four_eleventh_component_safe_phase_audit()
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
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "eleventh Q011cb witness component-safe complex phase discs",
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
    result = run_q011cx_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
