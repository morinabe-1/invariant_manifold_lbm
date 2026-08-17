"""Q011cy individual-disc partition audit for Q011cb flatten ordinal eleven."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011cw_degree34_eleventh_individual_partition_audit as q011cw
import research.q011cx_degree34_eleventh_component_safe_phase_discs as q011cx
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011cw.q011b
q011z = q011cw.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
SELECTED_COUNTS = (13, 9, 5, 7)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7
PARENT_FLAT_ORDINAL = 11
PARENT_LEFT_INDEX = 1
PARENT_RIGHT_INDEX = 3
PARENT_CLASS_COUNTS = (
    (0, 0, 0, 13),
    (1, 8),
    (5,),
    (3, 4),
)
OCCUPIED_SPEC = (
    (0, 3, 13),
    (1, 0, 1),
    (1, 1, 8),
    (2, 0, 5),
    (3, 0, 3),
    (3, 1, 4),
)
EXPECTED_IDENTIFIER_ORDER = q011cw.EXPECTED_IDENTIFIER_ORDER
EXPECTED_SOURCE_COUNTS = (13, 0, 1, 0, 8, 0, 0, 5, 0, 3, 0, 4)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 1, 0, 8, 0, 5, 1, 2, 4, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = EXPECTED_SOURCE_COUNTS
EXPECTED_PARENT_ALLOCATION_INDEX = 30_120
EXPECTED_PARENT_COMPATIBLE_INDEX = 1_698
EXPECTED_ALLOCATION_COUNT = 30_240
EXPECTED_COMPATIBLE_COUNT = 1_699

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = q011cw.EXPECTED_OCCUPIED_INTERVAL_DIGESTS
EXPECTED_OCCUPIED_RECORD_DIGEST = "69136bc4836114e56d60a96c099cd7d5be374fc749326438b2ae6242a0866bec"
EXPECTED_IDENTIFIER_ORDER_DIGEST = q011cw.EXPECTED_IDENTIFIER_ORDER_DIGEST
EXPECTED_ALLOCATION_DIGEST = "726cc53b8d64ef1bc9aa3abdbd0febe07acf29591a067b416d348b1b7f485993"
EXPECTED_COMPATIBLE_DIGEST = "9589fc30bff53304106998ca010f2d5ff5bbcf4c6cccbca944ca71a01b16f4ae"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 1_699
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.bc6d0d9bccb71p-32"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.39a71c57edb49p-28"
EXPECTED_PARENT_WITNESS_DIGEST = "66692c24fa69380e1a47af6eef7e5b964a5f6479982f6a25feb62a3eb1851f90"
EXPECTED_PARENT_PRODUCT_DIGEST = "2620c3859a303a798cc08be27b20a10b6c4628c49f8f278ade9d119d38bff278"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "c28de1513f367df3c6aacc2b26813e698dbc533f6830d82426e0a8181bf97654"
)
EXPECTED_PARENT_TARGET_DIGEST = "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "9dbab563a088e4318266e0b9aec14ecdeb883ce6716c2cdc11f139a0aa9e5dbe"
)
EXPECTED_ORDINAL_TEN_RESOLUTION_DIGEST = (
    "fcbac38dd950f2aedb42ca9b4f2543d54616a5938c7f645e2a2437c3ad04e645"
)

Q011CX_ARTIFACT_SHA256 = "0ec1b9ac8a32a7952a3fe6362b2842de489d7d416c540b82127902d08dd6062b"
Q011CX_RUNNER_SHA256 = "c0f599af9e873e8a17e44eecd74de0e4765c35a02b177c14f7f86dd388566c11"
Q011CX_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011CX_DIGESTS = (
    "6aa64d524e0d4e415ac3e4ce274bd8f5f5148b56799a6eda9859b59af3d1eaa3",
    "ea5033fb9d5e1ce850afc545587caadd909a925b6458b3c4c10a607310cb3257",
    "8ff676de72da7d00b19a40b30d809014fa3f2d4bd5e6d799c6fa0359fc11abdc",
    "05c4e2a4c9a62caaa083790416f468ffc81cf10fa52815e14f9d9feb860023f1",
    "d9f73a50463e117521ed7da2b531333db015d9672265f7f8c7d0e58571a5fb47",
)
EXPECTED_Q011CX_STREAM_DIGEST = "2c0339e4a7ae797d9fcdc0b154cc07d8f9fcfb7fc7199e2190b1fc7e192bdabf"

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the twelfth Q011cb witness"
)
RESOLVED_CLASSIFICATION = "the twelfth Q011cb witness is resolved by individual partition"
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the twelfth Q011cb witness persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011cy individual-disc partition audit is inconclusive"

_Q011CW_PROTOCOL_BASELINE = q011cw._Q011CK_PROTOCOL_OVERRIDE
_Q011CW_PROTOCOL_OVERRIDE: dict[str, Any] = {
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
def _q011cw_protocol_context() -> Iterator[None]:
    original = q011cw._Q011CK_PROTOCOL_OVERRIDE
    try:
        q011cw._Q011CK_PROTOCOL_OVERRIDE = _Q011CW_PROTOCOL_OVERRIDE
        yield
    finally:
        q011cw._Q011CK_PROTOCOL_OVERRIDE = original


def _protocol_globals_are_restored() -> bool:
    return bool(
        q011cw._Q011CK_PROTOCOL_OVERRIDE is _Q011CW_PROTOCOL_BASELINE
        and q011cw._protocol_globals_are_restored()
        and q011cx._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011cx._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011cx_degree34_eleventh_component_safe_phase_discs.json"
    )
    runner_path = Path(q011cx.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CX_DIGEST_NAMES)
    checks = {
        "q011cx_eighty_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 80
            and prior["direct_digest_count"] == 372
            and len(artifacts) == 80
            and all(prior["checks"].values())
        ),
        "q011cx_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CX_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CX_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CX_RUNNER_SHA256
        ),
        "q011cx_section_digests_match": digests == Q011CX_DIGESTS,
        "q011cx_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["component_safe_complex_phase_discs_resolve_eleventh_q011cb_witness"]
            and theorem["q011cw_interval_inert_diagnostic_is_preserved"]
            and theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011cx_registered_ordinal_ten_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 18_718
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 18_718,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"] == EXPECTED_Q011CX_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_TEN_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011cx_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "three_hundred_seventy_seven_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 377
        ),
    }
    artifacts["q011cx"] = artifact
    return (
        {
            "prior_q011cx_sealed_input_audit": prior,
            "q011cx": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CX_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": EXPECTED_ORDINAL_TEN_RESOLUTION_DIGEST,
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
    with _q011cw_protocol_context():
        fixed, lookup, compatible, parent = q011cw._fixed_individual_input_audit(artifacts)
    selection = fixed.pop("eleventh_parent_witness_selection_audit")
    selection["previous_phase_resolved_ordinals"] = list(range(11))
    selection["ordinal_ten_resolution_digest_sha256"] = EXPECTED_ORDINAL_TEN_RESOLUTION_DIGEST
    selection["checks"]["ordinal_ten_is_the_sealed_q011cx_phase_resolution"] = bool(
        artifacts["q011cx"]["cycle"]["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_eleventh_q011cb_witness"
        ]
        and artifacts["q011cx"]["cycle"]["complex_phase_product_disc_audit"][
            "global_minimum_margin_witness"
        ]["witness_digest_sha256"]
        == EXPECTED_ORDINAL_TEN_RESOLUTION_DIGEST
    )
    selection["checks"]["registered_ordinal_eleven_parent_witness_reproduces"] = selection[
        "checks"
    ].pop("registered_ordinal_ten_parent_witness_reproduces")
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
    selection["twelfth_parent_witness"] = selection.pop("eleventh_parent_witness")
    selection["twelfth_parent_witness_digest_sha256"] = selection.pop(
        "eleventh_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["twelfth_parent_witness_selection_audit"] = selection
    fixed["checks"]["registered_twelfth_parent_selection_reproduces"] = fixed["checks"].pop(
        "registered_eleventh_parent_selection_reproduces"
    )
    fixed["checks"]["q011cw_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    fixed["passed"] = all(fixed["checks"].values())
    return fixed, lookup, compatible, parent


def _individual_partition_audit(
    lookup: dict[str, q011z._UniformDisc],
    compatible: tuple[dict[str, Any], ...],
    parent: dict[str, Any],
) -> dict[str, Any]:
    with _q011cw_protocol_context():
        partition = q011cw._individual_partition_audit(lookup, compatible, parent)
    partition["checks"]["q011cw_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    partition["passed"] = all(partition["checks"].values())
    return partition


def _registered_parameters() -> dict[str, Any]:
    with _q011cw_protocol_context():
        registered = q011cw._registered_parameters()
    registered["q011cw_protocol_adapter"] = {
        "source_runner_sha256": _file_sha256(Path(q011cw.__file__).resolve()),
        "temporary_override_names": sorted(_Q011CW_PROTOCOL_OVERRIDE),
        "globals_restored_after_use": _protocol_globals_are_restored(),
    }
    return registered


_result_digest_sections = q011cw._result_digest_sections


def run_degree_thirty_four_twelfth_individual_partition_audit() -> dict[str, Any]:
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
    selection = fixed["twelfth_parent_witness_selection_audit"]
    validity_gates = {
        "q011cx_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "81 artifacts and 377 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_twelfth_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 11, class counts, 1699 multiplicity and exact witness",
            "value": selection["twelfth_parent_witness_digest_sha256"],
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
            "threshold": "30240 total and 1699 output-block-7 compatible allocations",
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
            "threshold": "1699 unit allocations, degree 34 and output block 7",
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
                and runner["filename"] == "q011cy_degree34_twelfth_individual_partition_audit.py"
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
        "only_the_registered_twelfth_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 11 only, one target and no other aggregate",
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
            "threshold": "1699 complete parent-comparison records",
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
            "Does splitting Q011cb flatten ordinal 11 into twelve singleton identifiers "
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
        "individual_partition_is_interval_inert_for_twelfth_q011cb_witness": inert,
        "twelfth_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_twelfth_q011cb_witness_persists": (
            effective_persistent
        ),
        "q011cx_ordinal_ten_phase_resolution_is_preserved": True,
        "q011cw_ordinal_ten_interval_inert_diagnostic_is_preserved": True,
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
        "This diagnostic concerns only Q011cb flatten ordinal 11, its 1699 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 10 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44788 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cz to expand only the 1699 registered wave allocations into "
        "component-safe complex phase discs."
        if inert
        else "Preregister Q011cz for the next Q011cb refined overlap."
        if resolved
        else "Preregister Q011cz to apply component-safe complex phase discs only to "
        "the first remaining individual overlap."
        if effective_persistent
        else "Repair only the first Q011cy validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011cy cycle failed strict serialization or digest")
    return cycle


def run_q011cy_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_twelfth_individual_partition_audit()
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
            "diagnostic": "twelfth Q011cb witness individual-disc partition invariance",
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
    result = run_q011cy_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
