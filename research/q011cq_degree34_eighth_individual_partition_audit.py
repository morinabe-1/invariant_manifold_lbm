"""Q011cq individual-disc partition audit for Q011cb flatten ordinal seven."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011ck_degree34_fifth_individual_partition_audit as q011ck
import research.q011cp_degree34_seventh_component_safe_phase_discs as q011cp
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
PARENT_FLAT_ORDINAL = 7
PARENT_LEFT_INDEX = 0
PARENT_RIGHT_INDEX = 7
PARENT_CLASS_COUNTS = (
    (0, 0, 0, 13),
    (0, 9),
    (5,),
    (7, 0),
)
OCCUPIED_SPEC = (
    (0, 3, 13),
    (1, 1, 9),
    (2, 0, 5),
    (3, 0, 7),
)
EXPECTED_IDENTIFIER_ORDER = (
    "block=16;center=145",
    "block=1;center=145",
    "block=16;center=151",
    "block=1;center=151",
    "block=16;center=152",
    "block=1;center=152",
    "block=16;center=148",
    "block=1;center=148",
)
EXPECTED_SOURCE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 7)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 9, 0, 5, 5, 2)
EXPECTED_LAST_COMPATIBLE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 7)
EXPECTED_PARENT_ALLOCATION_INDEX = 6_672
EXPECTED_PARENT_COMPATIBLE_INDEX = 381
EXPECTED_ALLOCATION_COUNT = 6_720
EXPECTED_COMPATIBLE_COUNT = 382

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
    "aea681cab5d2a0c4176e23896038ecfc3433ebb73dfc9ecd3567248e73d989db",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = "ca1862e86385a81d89b8b09e9b472ffdb2073129b1530b9db88e7729b8cf81ba"
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "a7824d876eaa7930e47add591124d8fffcbaec7ec5e3a5721789461ba0c39784"
)
EXPECTED_ALLOCATION_DIGEST = "44ba5fda9f1d5c7512d2008e655865d4b2e8f04698e196093067d887952d110f"
EXPECTED_COMPATIBLE_DIGEST = "ddb8dd5db8780f285cca94fbc0c1b57f540259841a03631b211d8605becc5b60"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 382
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.9d49030f29fb8p-32"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.3aa02fcb43b19p-28"
EXPECTED_PARENT_WITNESS_DIGEST = "ec8ac7bf477b2456b75cd671ad2c26f02fc08686425d83ddcc211000c3a180f8"
EXPECTED_PARENT_PRODUCT_DIGEST = "e9d957944f564935b6f3b0ab1bd38fd14534201b180f9d075be0d6d81f4052a8"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "c1fc6160f171274904add68c4401e687492d0c3eb2d0745200217d71e8f87a6d"
)
EXPECTED_PARENT_TARGET_DIGEST = q011ck.EXPECTED_PARENT_TARGET_DIGEST
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "f6878297ed8400dc4a0a40dc1cd3a497d17343746400231e2bf3102baadd56df"
)
EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST = (
    "8c8cf6e53c96a08c4f432a201d6736541e31ce7940c2070ae4edcd68d8b31342"
)
EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST = (
    "514c3194347c4be6775cc7a53518fbee0c3d97586a962c6e2b63378ce8a8614f"
)
EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST = (
    "1b7f6cc19a74cdefa602f28a6251f0c9b874cdd0a3a9b6f7ee438ea4618fea8d"
)

Q011CP_ARTIFACT_SHA256 = "06dc34b9f2aaf8fc1b6d41a6d55905056886fa3f8a1149b52d10203b7d381e96"
Q011CP_RUNNER_SHA256 = "5b678936cc1095faa7cb43d8e66900d0698a59cf317d12ddce55d37b5fb3ab18"
Q011CP_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011CP_DIGESTS = (
    "d9c6a7d5b041b7bd6d9450909057c661953cbb34d601f9f877608b64e2eae5d1",
    "cfa6cfacbf58246791fdf7cbc89b3b05ec0a261bd226c4adce08105688a3280e",
    "1e5ca23bb127c01ec823f65012d05821ff3de229289155d4f4ec89d062a82075",
    "eaaac30c1fc4ba318ef0c6fd9ec2241a2b517934af8c29eebf4cd7b247864dc6",
    "66205c3fe78eb873817cfcbd3c06ed3e1f15aae8f2a668791523402deb59b301",
)
EXPECTED_Q011CP_STREAM_DIGEST = "a4f98b1f04ba8060597dcf31fbce4d5408304082a77020744cb59cb1807aed21"

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the eighth Q011cb witness"
)
RESOLVED_CLASSIFICATION = "the eighth Q011cb witness is resolved by individual partition"
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the eighth Q011cb witness persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011cq individual-disc partition audit is inconclusive"

_Q011CK_PROTOCOL_BASELINE = q011ck._PROTOCOL_OVERRIDES
_Q011CG_IDENTIFIER_ORDER_BASELINE = q011ck.q011cg.EXPECTED_IDENTIFIER_ORDER
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
    "EXPECTED_IDENTIFIER_ORDER": EXPECTED_IDENTIFIER_ORDER,
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
        and q011ck.q011cg.EXPECTED_IDENTIFIER_ORDER == _Q011CG_IDENTIFIER_ORDER_BASELINE
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011cp._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011cp_degree34_seventh_component_safe_phase_discs.json"
    )
    runner_path = Path(q011cp.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CP_DIGEST_NAMES)
    checks = {
        "q011cp_seventy_two_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 72
            and prior["direct_digest_count"] == 336
            and len(artifacts) == 72
            and all(prior["checks"].values())
        ),
        "q011cp_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CP_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CP_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CP_RUNNER_SHA256
        ),
        "q011cp_section_digests_match": digests == Q011CP_DIGESTS,
        "q011cp_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["component_safe_complex_phase_discs_resolve_seventh_q011cb_witness"]
            and theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011cp_registered_ordinal_six_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 14_578
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 14_578,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"] == EXPECTED_Q011CP_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011cp_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "three_hundred_forty_one_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 341
        ),
    }
    artifacts["q011cp"] = artifact
    return (
        {
            "prior_q011cp_sealed_input_audit": prior,
            "q011cp": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CP_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": (EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST),
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
    selection["previous_phase_resolved_ordinals"] = [0, 1, 2, 3, 4, 5, 6]
    selection["ordinal_four_resolution_digest_sha256"] = EXPECTED_ORDINAL_FOUR_RESOLUTION_DIGEST
    selection["ordinal_five_resolution_digest_sha256"] = EXPECTED_ORDINAL_FIVE_RESOLUTION_DIGEST
    selection["ordinal_six_resolution_digest_sha256"] = EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
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
    selection["checks"]["ordinal_six_is_the_sealed_q011cp_phase_resolution"] = bool(
        artifacts["q011cp"]["cycle"]["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_seventh_q011cb_witness"
        ]
        and artifacts["q011cp"]["cycle"]["complex_phase_product_disc_audit"][
            "global_minimum_margin_witness"
        ]["witness_digest_sha256"]
        == EXPECTED_ORDINAL_SIX_RESOLUTION_DIGEST
    )
    selection["checks"]["registered_ordinal_seven_parent_witness_reproduces"] = selection[
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
    selection["eighth_parent_witness"] = selection.pop("fifth_parent_witness")
    selection["eighth_parent_witness_digest_sha256"] = selection.pop(
        "fifth_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["eighth_parent_witness_selection_audit"] = selection
    fixed["checks"]["registered_eighth_parent_selection_reproduces"] = fixed["checks"].pop(
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


def run_degree_thirty_four_eighth_individual_partition_audit() -> dict[str, Any]:
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
    selection = fixed["eighth_parent_witness_selection_audit"]
    validity_gates = {
        "q011cp_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "73 artifacts and 341 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_eighth_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 7, class counts, 382 multiplicity and exact witness",
            "value": selection["eighth_parent_witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "four occupied pairs, eight identifiers and equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "6720 total and 382 output-block-7 compatible allocations",
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
            "threshold": "382 unit allocations, degree 34 and output block 7",
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
                and runner["filename"] == "q011cq_degree34_eighth_individual_partition_audit.py"
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
        "only_the_registered_eighth_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 7 only, one target and no other aggregate",
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
            "threshold": "382 complete parent-comparison records",
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
            "Does splitting Q011cb flatten ordinal 7 into eight singleton identifiers "
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
        "individual_partition_is_interval_inert_for_eighth_q011cb_witness": inert,
        "eighth_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_eighth_q011cb_witness_persists": (
            effective_persistent
        ),
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
        "This diagnostic concerns only Q011cb flatten ordinal 7, its 382 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 6 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44792 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cr to expand only the 382 registered wave allocations into "
        "component-safe complex phase discs."
        if inert
        else "Preregister Q011cr for the next Q011cb refined overlap."
        if resolved
        else "Preregister Q011cr to apply component-safe complex phase discs only to "
        "the first remaining individual overlap."
        if effective_persistent
        else "Repair only the first Q011cq validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011cq cycle failed strict serialization or digest")
    return cycle


def run_q011cq_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_eighth_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "eight registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "full_allocation_target_matrix_retained": False,
            "complex_phase_product_evaluated": False,
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "eighth Q011cb witness individual-disc partition invariance",
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
    result = run_q011cq_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
