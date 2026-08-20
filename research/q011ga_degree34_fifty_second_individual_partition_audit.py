"""Q011ga individual-disc partition audit for Q011cb flatten ordinal fifty-one."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011da_degree34_thirteenth_individual_partition_audit as q011da
import research.q011fz_degree34_fifty_first_component_safe_phase_discs as q011fz
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011da.q011b
q011z = q011da.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
SELECTED_COUNTS = (13, 9, 5, 7)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7
PARENT_FLAT_ORDINAL = 51
PARENT_LEFT_INDEX = 6
PARENT_RIGHT_INDEX = 3
PARENT_CLASS_COUNTS = (
    (0, 0, 0, 13),
    (6, 3),
    (5,),
    (3, 4),
)
OCCUPIED_SPEC = (
    (0, 3, 13),
    (1, 0, 6),
    (1, 1, 3),
    (2, 0, 5),
    (3, 0, 3),
    (3, 1, 4),
)
EXPECTED_IDENTIFIER_ORDER = (
    "block=16;center=145",
    "block=1;center=145",
    "block=16;center=150",
    "block=1;center=150",
    "block=16;center=151",
    "block=1;center=151",
    "block=16;center=152",
    "block=1;center=152",
    "block=16;center=148",
    "block=1;center=148",
    "block=16;center=149",
    "block=1;center=149",
)
EXPECTED_SOURCE_COUNTS = (13, 0, 6, 0, 3, 0, 0, 5, 0, 3, 0, 4)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 6, 0, 3, 0, 5, 1, 2, 4, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = EXPECTED_SOURCE_COUNTS
EXPECTED_PARENT_ALLOCATION_INDEX = 46_920
EXPECTED_PARENT_COMPATIBLE_INDEX = 2_645
EXPECTED_ALLOCATION_COUNT = 47_040
EXPECTED_COMPATIBLE_COUNT = 2_646

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "e5b5ce415bac811880fc0ccaa97743c37d7e2510a679d48e627a6eaad2c05399",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
    "aea681cab5d2a0c4176e23896038ecfc3433ebb73dfc9ecd3567248e73d989db",
    "66a6c269ac137479694f186884d49ca3a4d11070e69132bab822391a557075d8",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = "df58709d2f9dc53eb07d8977fe30ec22049de985b61d4bfd546ceef1ee2efffd"
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "ff33e554ab95aad7ae696a37e1eeb5812b602f126e9697ccfdca46d21fc4f8f6"
)
EXPECTED_ALLOCATION_DIGEST = "05a26f32c073fc1d8ded72343f4cdbc7adcd80321e38884ce0e1548d5b6cfcee"
EXPECTED_COMPATIBLE_DIGEST = "9608c294ae7fbc0c897cf0058b3e7dde1582dec07355fe8ecdbd1324a4aab531"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 2_646
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.2c0f8d8072decp-31"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.34c98becc4ec6p-28"
EXPECTED_PARENT_WITNESS_DIGEST = "04a052ac6cbcd632479e28b8f2f53ab8e8e682a066fe14b32fa5318a955bc15f"
EXPECTED_PARENT_PRODUCT_DIGEST = "30548f6f7674e4f01fbf653f90e759c253c14a7ba625595e0ec7bfcb2629cdb0"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "72b8b5f47d43a0ee71a5b01d328a229c5e35140636aaad359df7e8ebeec9c7cd"
)
EXPECTED_PARENT_TARGET_DIGEST = "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "61d24b048215f8a51ee26f32b58a2cda7c22dcb83cf640d10ecfc417ccc9f9b7"
)
EXPECTED_ORDINAL_FIFTY_RESOLUTION_DIGEST = (
    "fcbac38dd950f2aedb42ca9b4f2543d54616a5938c7f645e2a2437c3ad04e645"
)

Q011FZ_ARTIFACT_SHA256 = "56df025e749692f791a8646e7ae010b858554e1c5ad0e4170b54a9f141465cb8"
Q011FZ_RUNNER_SHA256 = "fc13959ec906d336e2c17bfdf4c979c8c3d7e86b85ddcb7faa726fd6619279c8"
Q011FZ_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011FZ_DIGESTS = (
    "589210c06d7b0c80feb1c76eae645f92a322d1674e70f8432d43d4a143d58606",
    "30f600ad2b326f3ae377aa09614ce70e858b938310f47f850117bf3cba5cda4a",
    "44f7e37e32f4470e16e621a947e24f51c43047ad0f2692273687d6f575e91ade",
    "98f21b7a204ec83574edc20b94189b0bfed5d75210d34072a80668aba4587f9d",
    "f21ae43121baf90cc191bbb2184b281e90308f1c8e24142dddee8146b871b403",
)
EXPECTED_Q011FZ_STREAM_DIGEST = "2e6aa0f929004f17a86229db6193057bc5e8bd3aa3e27dffa58ae0e23bc8c60c"

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the fifty-second Q011cb witness"
)
RESOLVED_CLASSIFICATION = "the fifty-second Q011cb witness is resolved by individual partition"
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the fifty-second Q011cb witness persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011ga individual-disc partition audit is inconclusive"

_Q011DA_PROTOCOL_BASELINE = q011da._Q011CY_PROTOCOL_OVERRIDE
_Q011DA_PROTOCOL_OVERRIDE: dict[str, Any] = {
    **q011da._Q011CY_PROTOCOL_OVERRIDE,
    "PARENT_FLAT_ORDINAL": PARENT_FLAT_ORDINAL,
    "PARENT_LEFT_INDEX": PARENT_LEFT_INDEX,
    "PARENT_RIGHT_INDEX": PARENT_RIGHT_INDEX,
    "PARENT_CLASS_COUNTS": PARENT_CLASS_COUNTS,
    "OCCUPIED_SPEC": OCCUPIED_SPEC,
    "EXPECTED_SOURCE_COUNTS": EXPECTED_SOURCE_COUNTS,
    "EXPECTED_FIRST_COMPATIBLE_COUNTS": EXPECTED_FIRST_COMPATIBLE_COUNTS,
    "EXPECTED_LAST_COMPATIBLE_COUNTS": EXPECTED_LAST_COMPATIBLE_COUNTS,
    "EXPECTED_PARENT_ALLOCATION_INDEX": EXPECTED_PARENT_ALLOCATION_INDEX,
    "EXPECTED_PARENT_COMPATIBLE_INDEX": EXPECTED_PARENT_COMPATIBLE_INDEX,
    "EXPECTED_ALLOCATION_COUNT": EXPECTED_ALLOCATION_COUNT,
    "EXPECTED_COMPATIBLE_COUNT": EXPECTED_COMPATIBLE_COUNT,
    "EXPECTED_OCCUPIED_INTERVAL_DIGESTS": EXPECTED_OCCUPIED_INTERVAL_DIGESTS,
    "EXPECTED_OCCUPIED_RECORD_DIGEST": EXPECTED_OCCUPIED_RECORD_DIGEST,
    "EXPECTED_IDENTIFIER_ORDER": EXPECTED_IDENTIFIER_ORDER,
    "EXPECTED_IDENTIFIER_ORDER_DIGEST": EXPECTED_IDENTIFIER_ORDER_DIGEST,
    "EXPECTED_ALLOCATION_DIGEST": EXPECTED_ALLOCATION_DIGEST,
    "EXPECTED_COMPATIBLE_DIGEST": EXPECTED_COMPATIBLE_DIGEST,
    "EXPECTED_PARENT_WAVE_MULTIPLICITY": EXPECTED_PARENT_WAVE_MULTIPLICITY,
    "EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY": EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY,
    "EXPECTED_PARENT_INTERSECTION_WIDTH_HEX": EXPECTED_PARENT_INTERSECTION_WIDTH_HEX,
    "EXPECTED_PARENT_CENTER_RELATION": EXPECTED_PARENT_CENTER_RELATION,
    "EXPECTED_PARENT_CENTER_GAP_HEX": EXPECTED_PARENT_CENTER_GAP_HEX,
    "EXPECTED_PARENT_WITNESS_DIGEST": EXPECTED_PARENT_WITNESS_DIGEST,
    "INERT_CLASSIFICATION": INERT_CLASSIFICATION,
    "RESOLVED_CLASSIFICATION": RESOLVED_CLASSIFICATION,
    "EFFECTIVE_PERSISTENT_CLASSIFICATION": EFFECTIVE_PERSISTENT_CLASSIFICATION,
    "INCONCLUSIVE_CLASSIFICATION": INCONCLUSIVE_CLASSIFICATION,
}


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


@contextmanager
def _q011da_protocol_context() -> Iterator[None]:
    original = q011da._Q011CY_PROTOCOL_OVERRIDE
    try:
        q011da._Q011CY_PROTOCOL_OVERRIDE = _Q011DA_PROTOCOL_OVERRIDE
        yield
    finally:
        q011da._Q011CY_PROTOCOL_OVERRIDE = original


def _protocol_globals_are_restored() -> bool:
    return bool(
        q011da._Q011CY_PROTOCOL_OVERRIDE is _Q011DA_PROTOCOL_BASELINE
        and q011da._protocol_globals_are_restored()
        and q011fz._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011fz._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011fz_degree34_fifty_first_component_safe_phase_discs.json"
    )
    runner_path = Path(q011fz.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011FZ_DIGEST_NAMES)
    checks = {
        "q011fz_one_hundred_sixty_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 160
            and prior["direct_digest_count"] == 732
            and len(artifacts) == 160
            and all(prior["checks"].values())
        ),
        "q011fz_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011FZ_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011FZ_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011FZ_RUNNER_SHA256
        ),
        "q011fz_section_digests_match": digests == Q011FZ_DIGESTS,
        "q011fz_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["component_safe_complex_phase_discs_resolve_fifty_first_q011cb_witness"]
            and theorem["q011fy_ordinal_fifty_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fx_ordinal_forty_nine_phase_resolution_is_preserved"]
            and theorem["q011fv_ordinal_forty_eight_phase_resolution_is_preserved"]
            and theorem["q011fu_ordinal_forty_eight_interval_inert_diagnostic_is_preserved"]
            and theorem["q011ft_ordinal_forty_seven_phase_resolution_is_preserved"]
            and theorem["q011fs_ordinal_forty_seven_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fr_ordinal_forty_six_phase_resolution_is_preserved"]
            and theorem["q011fq_ordinal_forty_six_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fp_ordinal_forty_five_phase_resolution_is_preserved"]
            and theorem["q011fo_ordinal_forty_five_interval_inert_diagnostic_is_preserved"]
            and theorem["q011ff_ordinal_forty_phase_resolution_is_preserved"]
            and theorem["q011fd_ordinal_thirty_nine_phase_resolution_is_preserved"]
            and theorem["q011ez_ordinal_thirty_seven_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011fz_registered_ordinal_fifty_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 18_718
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 18_718,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"] == EXPECTED_Q011FZ_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_FIFTY_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011fz_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "seven_hundred_thirty_seven_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 737
        ),
    }
    artifacts["q011fz"] = artifact
    return (
        {
            "prior_q011fz_sealed_input_audit": prior,
            "q011fz": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011FZ_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": EXPECTED_ORDINAL_FIFTY_RESOLUTION_DIGEST,
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _fixed_individual_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    tuple[dict[str, Any], ...],
    dict[str, Any],
]:
    with _q011da_protocol_context():
        fixed, lookup, compatible, parent = q011da._fixed_individual_input_audit(artifacts)
    selection = fixed.pop("thirteenth_parent_witness_selection_audit")
    selection["previous_phase_resolved_ordinals"] = list(range(51))
    selection["ordinal_fifty_resolution_digest_sha256"] = EXPECTED_ORDINAL_FIFTY_RESOLUTION_DIGEST
    selection["checks"]["ordinal_fifty_is_the_sealed_q011fz_phase_resolution"] = bool(
        artifacts["q011fz"]["cycle"]["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_fifty_first_q011cb_witness"
        ]
        and artifacts["q011fz"]["cycle"]["theorem_consequence"][
            "q011fy_ordinal_fifty_interval_inert_diagnostic_is_preserved"
        ]
        and artifacts["q011fz"]["cycle"]["complex_phase_product_disc_audit"][
            "global_minimum_margin_witness"
        ]["witness_digest_sha256"]
        == EXPECTED_ORDINAL_FIFTY_RESOLUTION_DIGEST
    )
    selection["checks"]["registered_ordinal_fifty_one_parent_witness_reproduces"] = selection[
        "checks"
    ].pop("registered_ordinal_twelve_parent_witness_reproduces")
    selection["checks"]["registered_parent_interval_subdigests_reproduce"] = bool(
        q011b._canonical_json_sha256(parent["hybrid_product_interval"])
        == EXPECTED_PARENT_PRODUCT_DIGEST
        and q011b._canonical_json_sha256(parent["center_product_interval"])
        == EXPECTED_PARENT_CENTER_PRODUCT_DIGEST
        and q011b._canonical_json_sha256(parent["hybrid_target_interval"])
        == EXPECTED_PARENT_TARGET_DIGEST
        and q011b._canonical_json_sha256(parent["intersection_interval"])
        == EXPECTED_PARENT_INTERSECTION_DIGEST
    )
    selection["fifty_second_parent_witness"] = selection.pop("thirteenth_parent_witness")
    selection["fifty_second_parent_witness_digest_sha256"] = selection.pop(
        "thirteenth_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["fifty_second_parent_witness_selection_audit"] = selection
    fixed["checks"].pop("registered_thirteenth_parent_selection_reproduces")
    fixed["checks"]["registered_fifty_second_parent_selection_reproduces"] = selection["passed"]
    fixed["checks"].pop("q011cy_protocol_globals_are_restored")
    fixed["checks"]["q011da_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    fixed["passed"] = all(fixed["checks"].values())
    return fixed, lookup, compatible, parent


def _individual_partition_audit(
    lookup: dict[str, q011z._UniformDisc],
    compatible: tuple[dict[str, Any], ...],
    parent: dict[str, Any],
) -> dict[str, Any]:
    with _q011da_protocol_context():
        partition = q011da._individual_partition_audit(lookup, compatible, parent)
    partition["checks"]["q011da_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    partition["passed"] = all(partition["checks"].values())
    return partition


def _registered_parameters() -> dict[str, Any]:
    with _q011da_protocol_context():
        registered = q011da._registered_parameters()
    registered["q011da_protocol_adapter"] = {
        "source_runner_sha256": _file_sha256(Path(q011da.__file__).resolve()),
        "temporary_override_names": sorted(_Q011DA_PROTOCOL_OVERRIDE),
        "globals_restored_after_use": _protocol_globals_are_restored(),
    }
    return registered


_result_digest_sections = q011da._result_digest_sections


def run_degree_thirty_four_fifty_second_individual_partition_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    fixed, lookup, compatible, parent = _fixed_individual_input_audit(artifacts)
    partition = _individual_partition_audit(lookup, compatible, parent)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    partition_sections = {"fixed_individual_partition_input_audit": fixed}
    allocation_sections = {"individual_allocation_interval_audit": partition}
    input_digest = q011b._canonical_json_sha256(input_sections)
    partition_digest = q011b._canonical_json_sha256(partition_sections)
    allocation_digest = q011b._canonical_json_sha256(allocation_sections)
    selection = fixed["fifty_second_parent_witness_selection_audit"]
    validity_gates = {
        "q011fz_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "161 artifacts and 737 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_fifty_second_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 51, class counts, 2646 multiplicity and exact witness",
            "value": selection["fifty_second_parent_witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "six occupied pairs, twelve identifiers and equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "47040 total and 2646 output-block-7 compatible allocations",
            "value": {
                "full": fixed["full_allocation_count"],
                "compatible": fixed["compatible_allocation_count"],
            },
        },
        "all_count_degree_and_output_constraints_close": {
            "passed": bool(
                fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
                and partition["checks"]["all_degree_and_output_block_constraints_close"]
            ),
            "threshold": "2646 unit allocations, degree 34 and output block 7",
            "value": partition["compatible_allocation_count"],
        },
        "all_exact_interval_and_classification_invariants_pass": {
            "passed": partition["passed"],
            "threshold": "exact/outward exclusive relations and strict finite records",
            "value": partition["checks"],
        },
        "strict_section_digests_runner_and_protocol_provenance_reproduce": {
            "passed": bool(
                len(input_digest) == len(partition_digest) == len(allocation_digest) == 64
                and runner["filename"]
                == "q011ga_degree34_fifty_second_individual_partition_audit.py"
                and partition["first_allocation_record"] is not None
                and partition["last_allocation_record"] is not None
                and _protocol_globals_are_restored()
            ),
            "threshold": "three section digests, endpoint records, runner and restored protocol",
            "value": {
                "input": input_digest,
                "partition": partition_digest,
                "allocation": allocation_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    all_parent_equal = partition["all_product_target_intersection_and_center_records_equal_parent"]
    exact_counts = partition["exact_relation_counts"]
    binary_counts = partition["binary64_outward_relation_counts"]
    strict_count = exact_counts["product_below_target"] + exact_counts["target_below_product"]
    all_overlap = bool(
        exact_counts["overlap"] == EXPECTED_COMPATIBLE_COUNT and binary_counts == exact_counts
    )
    all_strict = bool(
        strict_count == EXPECTED_COMPATIBLE_COUNT
        and binary_counts["overlap"] == 0
        and all(
            record["exact_gap_positive"] and record["binary64_outward_gap_positive"]
            for record in partition["allocation_classification_records"]
        )
    )
    inert = validity_passed and all_parent_equal and all_overlap
    resolved = validity_passed and all_strict
    effective_persistent = bool(
        validity_passed and not inert and not resolved and exact_counts["overlap"] > 0
    )
    outcome_flags = (inert, resolved, effective_persistent)
    refinement_outcome = (
        "partition_inert_persistent"
        if inert
        else "resolved_by_individual_partition"
        if resolved
        else "partition_effective_but_persistent"
        if effective_persistent
        else "inconclusive"
    )
    classification = (
        INERT_CLASSIFICATION
        if inert
        else RESOLVED_CLASSIFICATION
        if resolved
        else EFFECTIVE_PERSISTENT_CLASSIFICATION
        if effective_persistent
        else INCONCLUSIVE_CLASSIFICATION
    )
    diagnostic_gates = {
        "only_the_registered_fifty_second_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 51 only, one target and no other aggregate",
            "value": fixed["parent_class_counts"],
        },
        "parent_interval_comparison_is_complete": {
            "passed": bool(
                len(partition["allocation_classification_records"]) == EXPECTED_COMPATIBLE_COUNT
                and all(
                    isinstance(record["product_equals_parent"], bool)
                    and isinstance(record["intersection_equals_parent"], bool)
                    for record in partition["allocation_classification_records"]
                )
            ),
            "threshold": "2646 complete parent-comparison records",
            "value": all_parent_equal,
        },
        "registered_stopping_rule_is_exclusive_and_reproduces": {
            "passed": bool(validity_passed and sum(outcome_flags) == 1),
            "threshold": "exactly one inert, resolved or effective-persistent branch",
            "value": {
                "inert": inert,
                "resolved": resolved,
                "effective_persistent": effective_persistent,
            },
        },
        "scientific_boundary_is_preserved": {
            "passed": True,
            "threshold": "no phase, degree-34, actual-resonance or SSM claim",
            "value": "certified 2--33 and 91+, missing 34--90",
        },
    }
    cycle = {
        "question": (
            "Does splitting Q011cb flatten ordinal 51 into twelve singleton identifiers "
            "change any compatible exact product interval or classification?"
        ),
        **input_sections,
        **partition_sections,
        **allocation_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "partition_input_digest_sha256": partition_digest,
        "allocation_audit_digest_sha256": allocation_digest,
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
        "actual_resonance_outcome": "not_established",
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "individual_partition_is_interval_inert_for_fifty_second_q011cb_witness": inert,
        "fifty_second_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_fifty_second_q011cb_witness_persists": (
            effective_persistent
        ),
        "q011fz_ordinal_fifty_phase_resolution_is_preserved": True,
        "q011fy_ordinal_fifty_interval_inert_diagnostic_is_preserved": True,
        "q011fx_ordinal_forty_nine_phase_resolution_is_preserved": True,
        "q011fw_ordinal_forty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011fv_ordinal_forty_eight_phase_resolution_is_preserved": True,
        "q011fu_ordinal_forty_eight_interval_inert_diagnostic_is_preserved": True,
        "q011ft_ordinal_forty_seven_phase_resolution_is_preserved": True,
        "q011fs_ordinal_forty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011fr_ordinal_forty_six_phase_resolution_is_preserved": True,
        "q011fq_ordinal_forty_six_interval_inert_diagnostic_is_preserved": True,
        "q011fp_ordinal_forty_five_phase_resolution_is_preserved": True,
        "q011fo_ordinal_forty_five_interval_inert_diagnostic_is_preserved": True,
        "q011fn_ordinal_forty_four_phase_resolution_is_preserved": True,
        "q011fm_ordinal_forty_four_interval_inert_diagnostic_is_preserved": True,
        "q011fl_ordinal_forty_three_phase_resolution_is_preserved": True,
        "q011fk_ordinal_forty_three_interval_inert_diagnostic_is_preserved": True,
        "q011fj_ordinal_forty_two_phase_resolution_is_preserved": True,
        "q011fi_ordinal_forty_two_interval_inert_diagnostic_is_preserved": True,
        "q011fh_ordinal_forty_one_phase_resolution_is_preserved": True,
        "q011fg_ordinal_forty_one_interval_inert_diagnostic_is_preserved": True,
        "q011ff_ordinal_forty_phase_resolution_is_preserved": True,
        "q011fe_ordinal_forty_interval_inert_diagnostic_is_preserved": True,
        "q011fd_ordinal_thirty_nine_phase_resolution_is_preserved": True,
        "q011fc_ordinal_thirty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011fb_ordinal_thirty_eight_phase_resolution_is_preserved": True,
        "q011fa_ordinal_thirty_eight_interval_inert_diagnostic_is_preserved": True,
        "q011ez_ordinal_thirty_seven_phase_resolution_is_preserved": True,
        "q011ey_ordinal_thirty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011ex_ordinal_thirty_six_phase_resolution_is_preserved": True,
        "q011ew_ordinal_thirty_six_interval_inert_diagnostic_is_preserved": True,
        "q011ev_ordinal_thirty_five_phase_resolution_is_preserved": True,
        "q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved": True,
        "q011et_ordinal_thirty_four_phase_resolution_is_preserved": True,
        "q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved": True,
        "q011er_ordinal_thirty_three_phase_resolution_is_preserved": True,
        "q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved": True,
        "q011ep_ordinal_thirty_two_phase_resolution_is_preserved": True,
        "q011eo_ordinal_thirty_two_interval_inert_diagnostic_is_preserved": True,
        "q011en_ordinal_thirty_one_phase_resolution_is_preserved": True,
        "q011em_ordinal_thirty_one_interval_inert_diagnostic_is_preserved": True,
        "q011el_ordinal_thirty_phase_resolution_is_preserved": True,
        "q011ek_ordinal_thirty_interval_inert_diagnostic_is_preserved": True,
        "q011ej_ordinal_twenty_nine_phase_resolution_is_preserved": True,
        "q011ei_ordinal_twenty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011eh_ordinal_twenty_eight_phase_resolution_is_preserved": True,
        "q011eg_ordinal_twenty_eight_interval_inert_diagnostic_is_preserved": True,
        "q011ef_ordinal_twenty_seven_phase_resolution_is_preserved": True,
        "q011ee_ordinal_twenty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011ed_ordinal_twenty_six_phase_resolution_is_preserved": True,
        "q011ec_ordinal_twenty_six_interval_inert_diagnostic_is_preserved": True,
        "q011eb_ordinal_twenty_five_phase_resolution_is_preserved": True,
        "q011ea_ordinal_twenty_five_interval_inert_diagnostic_is_preserved": True,
        "q011dz_ordinal_twenty_four_phase_resolution_is_preserved": True,
        "q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved": True,
        "q011dx_ordinal_twenty_three_phase_resolution_is_preserved": True,
        "q011dw_ordinal_twenty_three_interval_inert_diagnostic_is_preserved": True,
        "q011dv_ordinal_twenty_two_phase_resolution_is_preserved": True,
        "q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved": True,
        "q011dt_ordinal_twenty_one_phase_resolution_is_preserved": True,
        "q011ds_ordinal_twenty_one_interval_inert_diagnostic_is_preserved": True,
        "q011dr_ordinal_twenty_phase_resolution_is_preserved": True,
        "q011dq_ordinal_twenty_interval_inert_diagnostic_is_preserved": True,
        "q011dp_ordinal_nineteen_phase_resolution_is_preserved": True,
        "q011do_ordinal_nineteen_interval_inert_diagnostic_is_preserved": True,
        "q011dn_ordinal_eighteen_phase_resolution_is_preserved": True,
        "q011dm_ordinal_eighteen_interval_inert_diagnostic_is_preserved": True,
        "q011dl_ordinal_seventeen_phase_resolution_is_preserved": True,
        "q011dk_ordinal_seventeen_interval_inert_diagnostic_is_preserved": True,
        "q011dj_ordinal_sixteen_phase_resolution_is_preserved": True,
        "q011di_ordinal_sixteen_interval_inert_diagnostic_is_preserved": True,
        "q011dh_ordinal_fifteen_phase_resolution_is_preserved": True,
        "q011dg_ordinal_fifteen_interval_inert_diagnostic_is_preserved": True,
        "q011df_ordinal_fourteen_phase_resolution_is_preserved": True,
        "q011de_ordinal_fourteen_interval_inert_diagnostic_is_preserved": True,
        "q011dd_ordinal_thirteen_phase_resolution_is_preserved": True,
        "q011dc_ordinal_thirteen_interval_inert_diagnostic_is_preserved": True,
        "q011db_ordinal_twelve_phase_resolution_is_preserved": True,
        "q011da_ordinal_twelve_interval_inert_diagnostic_is_preserved": True,
        "q011cx_ordinal_ten_phase_resolution_is_preserved": True,
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
        "q011bx_degree_thirty_four_sufficient_certificate_remains_rejected": True,
        "degree_thirty_four_external_nonresonance_is_certified": False,
        "an_actual_degree_thirty_four_external_resonance_is_established": False,
        "certified_external_nonresonance_degrees": list(range(2, 34)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(34, 91)),
        "complex_phase_product_is_audited": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This diagnostic concerns only Q011cb flatten ordinal 51, its 2646 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 50 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44748 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011gb to expand only the 2646 registered wave allocations into "
        "component-safe complex phase discs."
        if inert
        else "Preregister Q011gb to audit the next Q011cb refined overlap in registered order."
        if resolved
        else "Preregister Q011gb to apply component-safe complex phase discs only to "
        "the first remaining individual overlap."
        if effective_persistent
        else "Repair only the first Q011ga validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011ga cycle failed strict serialization or digest")
    return cycle


def run_q011ga_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_fifty_second_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "twelve registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "full_allocation_target_matrix_retained": False,
            "complex_phase_product_evaluated": False,
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "fifty-second Q011cb witness individual-disc partition invariance",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
            "target_identifier": TARGET_IDENTIFIER,
            "complex_phase_claim": False,
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
    result = run_q011ga_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
