"""Q011co individual-disc partition audit for Q011cb flatten ordinal six."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011ck_degree34_fifth_individual_partition_audit as q011ck
import research.q011cn_degree34_sixth_component_safe_phase_discs as q011cn
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011ck.q011b
q011z = q011ck.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
SELECTED_COUNTS = (13, 9, 5, 7)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7
PARENT_FLAT_ORDINAL = 6
PARENT_LEFT_INDEX = 0
PARENT_RIGHT_INDEX = 6
PARENT_CLASS_COUNTS = (
    (0, 0, 0, 13),
    (0, 9),
    (5,),
    (6, 1),
)
OCCUPIED_SPEC = (
    (0, 3, 13),
    (1, 1, 9),
    (2, 0, 5),
    (3, 0, 6),
    (3, 1, 1),
)
EXPECTED_IDENTIFIER_ORDER = q011ck.EXPECTED_IDENTIFIER_ORDER
EXPECTED_SOURCE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 6, 0, 1)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 9, 0, 5, 4, 2, 1, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 6, 0, 1)
EXPECTED_PARENT_ALLOCATION_INDEX = 11_676
EXPECTED_PARENT_COMPATIBLE_INDEX = 664
EXPECTED_ALLOCATION_COUNT = 11_760
EXPECTED_COMPATIBLE_COUNT = 665

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = q011ck.EXPECTED_OCCUPIED_INTERVAL_DIGESTS
EXPECTED_OCCUPIED_RECORD_DIGEST = "07b2f369092602bf74d5317a70c2af93c3435d9f12b1362935e845da93bbbc90"
EXPECTED_IDENTIFIER_ORDER_DIGEST = q011ck.EXPECTED_IDENTIFIER_ORDER_DIGEST
EXPECTED_ALLOCATION_DIGEST = "8eb0864c845e98bc78a17228c12c6c073605d470ada26caa4f673f3782c640fb"
EXPECTED_COMPATIBLE_DIGEST = "ddb902ffaa442c353438962da8b25bcecc34bf8d8ebafc097a260a26579746bb"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 665
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.9d491ea075959p-32"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.3aa03226fd1afp-28"
EXPECTED_PARENT_WITNESS_DIGEST = "691a3a4253ad8a448c49ee75c6c23b89d5e50a373443ed4d913693a48cde04ea"
EXPECTED_PARENT_PRODUCT_DIGEST = "3b1386389a353cbae907c5a3de1d33732c3637e6fa82efe520f3361dad6d6be3"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "b0b9beea2008fd5e91eb84f4f0779122fccdae44407f760f0c3eef7cd798f520"
)
EXPECTED_PARENT_TARGET_DIGEST = q011ck.EXPECTED_PARENT_TARGET_DIGEST
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "c9dab9030cbaa97435aefce1c471278b5d382fc2b304c8c7450af6f41ee4c156"
)
EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST = (
    "8c8cf6e53c96a08c4f432a201d6736541e31ce7940c2070ae4edcd68d8b31342"
)
EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST = (
    "514c3194347c4be6775cc7a53518fbee0c3d97586a962c6e2b63378ce8a8614f"
)

Q011CN_ARTIFACT_SHA256 = "e8b714a50eedadd3a9ac8e5556586c95167573a51c853c5f491b4660112d80c3"
Q011CN_RUNNER_SHA256 = "bc506ea76eefa4a84d2cf19c8f92b6fcd197c5a0ea28873c1d0eb4d51a3a6b6e"
Q011CN_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011CN_DIGESTS = (
    "07b46cf876293a6067a81d25b46a14cfe4e2a1a20f5ee223a2132fd6a4a7a87e",
    "e1cc6364bc6882c3d6768e0dea40de260e9b7a7142d563c9d25b501125fbbd15",
    "18fbba9e20f12a0fbba3b3e6593cea3453079ab541753264d02eb6089692b17c",
    "7428c19a264f67bd134792b9d64b3ce621b3ca56356fe80a683f95ed05ea7b0f",
    "32b4a2e64fcf491c365814737e34ec716bc88c97655c42a532cc66b7ffebe8c7",
)
EXPECTED_Q011CN_STREAM_DIGEST = "9e2a0c5a47749cf103dcf3595aa043d522e14aaa70763bf5a412ba294a82858a"

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the seventh Q011cb witness"
)
RESOLVED_CLASSIFICATION = "the seventh Q011cb witness is resolved by individual partition"
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the seventh Q011cb witness persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011co individual-disc partition audit is inconclusive"

_Q011CK_PROTOCOL_BASELINE = q011ck._PROTOCOL_OVERRIDES
_Q011CK_PROTOCOL_OVERRIDE: dict[str, Any] = {
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
    "EXPECTED_IDENTIFIER_ORDER_DIGEST": EXPECTED_IDENTIFIER_ORDER_DIGEST,
    "EXPECTED_ALLOCATION_DIGEST": EXPECTED_ALLOCATION_DIGEST,
    "EXPECTED_COMPATIBLE_DIGEST": EXPECTED_COMPATIBLE_DIGEST,
    "EXPECTED_PARENT_WAVE_MULTIPLICITY": EXPECTED_PARENT_WAVE_MULTIPLICITY,
    "EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY": (EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY),
    "EXPECTED_PARENT_INTERSECTION_WIDTH_HEX": (EXPECTED_PARENT_INTERSECTION_WIDTH_HEX),
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
def _q011ck_protocol_context() -> Iterator[None]:
    original = q011ck._PROTOCOL_OVERRIDES
    try:
        q011ck._PROTOCOL_OVERRIDES = _Q011CK_PROTOCOL_OVERRIDE
        yield
    finally:
        q011ck._PROTOCOL_OVERRIDES = original


def _protocol_globals_are_restored() -> bool:
    return bool(
        q011ck._PROTOCOL_OVERRIDES is _Q011CK_PROTOCOL_BASELINE
        and q011ck._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011cn._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011cn_degree34_sixth_component_safe_phase_discs.json"
    )
    runner_path = Path(q011cn.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CN_DIGEST_NAMES)
    checks = {
        "q011cn_seventy_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 70
            and prior["direct_digest_count"] == 327
            and len(artifacts) == 70
            and all(prior["checks"].values())
        ),
        "q011cn_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CN_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CN_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CN_RUNNER_SHA256
        ),
        "q011cn_section_digests_match": digests == Q011CN_DIGESTS,
        "q011cn_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["component_safe_complex_phase_discs_resolve_sixth_q011cb_witness"]
            and theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011cn_registered_ordinal_five_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 18_718
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 18_718,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"] == EXPECTED_Q011CN_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011cn_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "three_hundred_thirty_two_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 332
        ),
    }
    artifacts["q011cn"] = artifact
    return (
        {
            "prior_q011cn_sealed_input_audit": prior,
            "q011cn": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CN_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": (EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST),
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
    with _q011ck_protocol_context():
        fixed, lookup, compatible, parent = q011ck._fixed_individual_input_audit(artifacts)
    selection = fixed.pop("fifth_parent_witness_selection_audit")
    selection["previous_phase_resolved_ordinals"] = [0, 1, 2, 3, 4, 5]
    selection["ordinal_four_resolution_digest_sha256"] = EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    selection["ordinal_five_resolution_digest_sha256"] = EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    selection["checks"]["ordinal_four_is_the_sealed_q011cl_phase_resolution"] = (
        artifacts["q011cl"]["cycle"]["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_fifth_q011cb_witness"
        ]
        and artifacts["q011cl"]["cycle"]["complex_phase_product_disc_audit"][
            "global_minimum_margin_witness"
        ]["witness_digest_sha256"]
        == EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    )
    selection["checks"]["ordinal_five_is_the_sealed_q011cn_phase_resolution"] = bool(
        artifacts["q011cn"]["cycle"]["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_sixth_q011cb_witness"
        ]
        and artifacts["q011cn"]["cycle"]["complex_phase_product_disc_audit"][
            "global_minimum_margin_witness"
        ]["witness_digest_sha256"]
        == EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    )
    selection["checks"]["registered_ordinal_six_parent_witness_reproduces"] = selection[
        "checks"
    ].pop("registered_ordinal_four_parent_witness_reproduces")
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
    selection["seventh_parent_witness"] = selection.pop("fifth_parent_witness")
    selection["seventh_parent_witness_digest_sha256"] = selection.pop(
        "fifth_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["seventh_parent_witness_selection_audit"] = selection
    fixed["checks"]["registered_seventh_parent_selection_reproduces"] = fixed["checks"].pop(
        "registered_fifth_parent_selection_reproduces"
    )
    fixed["checks"]["q011ck_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    fixed["passed"] = all(fixed["checks"].values())
    return fixed, lookup, compatible, parent


def _individual_partition_audit(
    lookup: dict[str, q011z._UniformDisc],
    compatible: tuple[dict[str, Any], ...],
    parent: dict[str, Any],
) -> dict[str, Any]:
    with _q011ck_protocol_context():
        partition = q011ck._individual_partition_audit(lookup, compatible, parent)
    partition["checks"]["q011ck_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    partition["passed"] = all(partition["checks"].values())
    return partition


def _registered_parameters() -> dict[str, Any]:
    with _q011ck_protocol_context():
        registered = q011ck._registered_parameters()
    registered["q011ck_protocol_adapter"] = {
        "source_runner_sha256": _file_sha256(Path(q011ck.__file__).resolve()),
        "temporary_override_names": sorted(_Q011CK_PROTOCOL_OVERRIDE),
        "globals_restored_after_use": _protocol_globals_are_restored(),
    }
    return registered


_result_digest_sections = q011ck._result_digest_sections


def run_degree_thirty_four_seventh_individual_partition_audit() -> dict[str, Any]:
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
    selection = fixed["seventh_parent_witness_selection_audit"]
    validity_gates = {
        "q011cn_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "71 artifacts and 332 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_seventh_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 6, class counts, 665 multiplicity and exact witness",
            "value": selection["seventh_parent_witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "five occupied pairs, ten identifiers and equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "11760 total and 665 output-block-7 compatible allocations",
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
            "threshold": "665 unit allocations, degree 34 and output block 7",
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
                and runner["filename"] == "q011co_degree34_seventh_individual_partition_audit.py"
                and partition["first_allocation_record"] is not None
                and partition["last_allocation_record"] is not None
                and _protocol_globals_are_restored()
            ),
            "threshold": ("three section digests, endpoint records, runner and restored protocol"),
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
        "only_the_registered_seventh_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 6 only, one target and no other aggregate",
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
            "threshold": "665 complete parent-comparison records",
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
            "Does splitting Q011cb flatten ordinal 6 into ten singleton identifiers "
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
        "individual_partition_is_interval_inert_for_seventh_q011cb_witness": inert,
        "seventh_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_seventh_q011cb_witness_persists": (
            effective_persistent
        ),
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
        "This diagnostic concerns only Q011cb flatten ordinal 6, its 665 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 5 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44793 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cp to expand only the 665 registered wave allocations into "
        "component-safe complex phase discs."
        if inert
        else "Preregister Q011cp for the next Q011cb refined overlap."
        if resolved
        else "Preregister Q011cp to apply component-safe complex phase discs only to "
        "the first remaining individual overlap."
        if effective_persistent
        else "Repair only the first Q011co validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011co cycle failed strict serialization or digest")
    return cycle


def run_q011co_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_seventh_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "ten registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "full_allocation_target_matrix_retained": False,
            "complex_phase_product_evaluated": False,
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "seventh Q011cb witness individual-disc partition invariance",
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
    result = run_q011co_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
