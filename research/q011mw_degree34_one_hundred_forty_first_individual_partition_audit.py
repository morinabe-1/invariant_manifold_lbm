"""Q011mw individual-disc partition audit for Q011cb flatten ordinal one hundred forty."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011mu_degree34_one_hundred_fortieth_individual_partition_audit as q011mu
import research.q011mv_degree34_one_hundred_fortieth_component_safe_phase_discs as q011mv
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011mu.q011b
q011z = q011mu.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
SELECTED_COUNTS = (13, 9, 5, 7)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7
PARENT_FLAT_ORDINAL = 140
PARENT_LEFT_INDEX = 17
PARENT_RIGHT_INDEX = 4
PARENT_CLASS_COUNTS = (
    (0, 0, 1, 12),
    (7, 2),
    (5,),
    (4, 3),
)
OCCUPIED_SPEC = (
    (0, 2, 1),
    (0, 3, 12),
    (1, 0, 7),
    (1, 1, 2),
    (2, 0, 5),
    (3, 0, 4),
    (3, 1, 3),
)
EXPECTED_IDENTIFIER_ORDER = (
    "block=16;center=144",
    "block=1;center=144",
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
EXPECTED_SOURCE_COUNTS = (1, 0, 12, 0, 7, 0, 2, 0, 0, 5, 0, 4, 0, 3)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 1, 0, 12, 0, 7, 0, 2, 0, 5, 2, 2, 3, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = EXPECTED_SOURCE_COUNTS
EXPECTED_PARENT_ALLOCATION_INDEX = 74_760
EXPECTED_PARENT_COMPATIBLE_INDEX = 4_135
EXPECTED_ALLOCATION_COUNT = 74_880
EXPECTED_COMPATIBLE_COUNT = 4_136

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "8c192189449f149db3b3786d791a4fc262ff9ff3c89d831307cbab2faa614734",
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "e5b5ce415bac811880fc0ccaa97743c37d7e2510a679d48e627a6eaad2c05399",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
    "aea681cab5d2a0c4176e23896038ecfc3433ebb73dfc9ecd3567248e73d989db",
    "66a6c269ac137479694f186884d49ca3a4d11070e69132bab822391a557075d8",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = "25d3c2d8bf3859e0c9554f61226d5f82a3b59d2f5c7f9a012d143b3cde8104bc"
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "c90ea70931e0bb67733cb9179566e166baf2a67756933394db785fb4f941276a"
)
EXPECTED_ALLOCATION_DIGEST = "aa781a9e46806a2a7d7a9fa89b6ee1a0225842f2dc5a59cd00a62e21e360606f"
EXPECTED_COMPATIBLE_DIGEST = "e7a03731835a02de51a4632ae667d9c1ac07c0ec23e27c4a32ff04616d356dcc"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 4_136
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.3ba1402c161f7p-31"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.33d069845dbf8p-28"
EXPECTED_PARENT_WITNESS_DIGEST = "f6a30e7678a6b2096057de899a4359851a2a7879bb91279d135e5b0d1571ee60"
EXPECTED_PARENT_PRODUCT_DIGEST = "99712ec650e8852d2ece78339ca6d2c5c60ac2396d1a42509a74dd34ba7a94b9"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "b4064fc4c76dd501cc8fdb53bae1161f0c4d877d63b7a34446efe17e0c0c6b27"
)
EXPECTED_PARENT_TARGET_DIGEST = "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "5b1918de7bbef114ccb8c6d66d862f37204fc9056742e79543f27e9bfa6b654e"
)
EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_NINE_RESOLUTION_DIGEST = (
    "5230fd7936461e9a4b0c7c22bece80b21c02827e9ec05805b4ac2135b88fa34e"
)

Q011MV_ARTIFACT_SHA256 = "37d1a3dba4d8f7990376e42b9448e582fa62ddb44c60135df4d84ecd9bace3d0"
Q011MV_RUNNER_SHA256 = "9c84020ef514647b899e1a90c9ae68f751f19fc9e497c0bd47bb1addf85d6cc3"
Q011MV_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011MV_DIGESTS = (
    "09fa09356a4cbbc494b29b12ee4ec19dfcd73a73749ad54a76c6da15f2d71c98",
    "e97cabacf47c7bf27a25d9101adf056cce641398709387bd8a7f13e7ee6c9b09",
    "a9a54993eebce96f919a353676604a920ccb975b646e7b9c970ecbb6b91e1410",
    "7985084e9fa10284c9aabc70ca28d6af023225408e16905c1c96b6f3493e8263",
    "c2ea50d1f5676e422f195ad998e589484e4836f6af09747b2bffaa70f1cf1dcf",
)
EXPECTED_Q011MV_STREAM_DIGEST = "c3490cfb845c595976f5d844b6743f2a5ac8605b455f51e14135a933221b32d2"

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the one-hundred-forty-first Q011cb witness"
)
RESOLVED_CLASSIFICATION = (
    "the one-hundred-forty-first Q011cb witness is resolved by individual partition"
)
EFFECTIVE_PERSISTENT_CLASSIFICATION = "the individual-disc partition changes intervals but the one-hundred-forty-first Q011cb witness persists"
INCONCLUSIVE_CLASSIFICATION = "the Q011mw individual-disc partition audit is inconclusive"

_Q011MU_PROTOCOL_BASELINE = q011mu._Q011DA_PROTOCOL_OVERRIDE
_Q011MU_PROTOCOL_OVERRIDE: dict[str, Any] = {
    **q011mu._Q011DA_PROTOCOL_OVERRIDE,
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
def _q011mu_protocol_context() -> Iterator[None]:
    original = q011mu._Q011DA_PROTOCOL_OVERRIDE
    try:
        q011mu._Q011DA_PROTOCOL_OVERRIDE = _Q011MU_PROTOCOL_OVERRIDE
        yield
    finally:
        q011mu._Q011DA_PROTOCOL_OVERRIDE = original


def _protocol_globals_are_restored() -> bool:
    return bool(
        q011mu._Q011DA_PROTOCOL_OVERRIDE is _Q011MU_PROTOCOL_BASELINE
        and q011mu._protocol_globals_are_restored()
        and q011mv._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011mv._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011mv_degree34_one_hundred_fortieth_component_safe_phase_discs.json"
    )
    runner_path = Path(q011mv.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011MV_DIGEST_NAMES)
    checks = {
        "q011mv_three_hundred_thirty_eight_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 338
            and prior["direct_digest_count"] == 1_533
            and len(artifacts) == 338
            and all(prior["checks"].values())
        ),
        "q011mv_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011MV_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011MV_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011MV_RUNNER_SHA256
        ),
        "q011mv_section_digests_match": digests == Q011MV_DIGESTS,
        "q011mv_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "component_safe_complex_phase_discs_resolve_one_hundred_fortieth_q011cb_witness"
            ]
            and theorem[
                "q011mu_ordinal_one_hundred_thirty_nine_interval_inert_diagnostic_is_preserved"
            ]
            and all(
                value
                for name, value in theorem.items()
                if name.endswith("_is_preserved") and isinstance(value, bool)
            )
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011mv_registered_ordinal_one_hundred_thirty_nine_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 37_940
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 37_940,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"] == EXPECTED_Q011MV_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_NINE_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011mv_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_thousand_five_hundred_thirty_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 1_538
        ),
    }
    artifacts["q011mv"] = artifact
    return (
        {
            "prior_q011mv_sealed_input_audit": prior,
            "q011mv": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011MV_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": (
                    EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_NINE_RESOLUTION_DIGEST
                ),
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
    with _q011mu_protocol_context():
        fixed, lookup, compatible, parent = q011mu._fixed_individual_input_audit(artifacts)
    selection = fixed.pop("one_hundred_fortieth_parent_witness_selection_audit")
    selection["previous_phase_resolved_ordinals"] = list(range(140))
    selection["ordinal_one_hundred_thirty_nine_resolution_digest_sha256"] = (
        EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_NINE_RESOLUTION_DIGEST
    )
    selection["checks"]["ordinal_one_hundred_thirty_nine_is_the_sealed_q011mv_phase_resolution"] = (
        bool(
            artifacts["q011mv"]["cycle"]["theorem_consequence"][
                "component_safe_complex_phase_discs_resolve_one_hundred_fortieth_q011cb_witness"
            ]
            and artifacts["q011mv"]["cycle"]["theorem_consequence"][
                "q011mu_ordinal_one_hundred_thirty_nine_interval_inert_diagnostic_is_preserved"
            ]
            and artifacts["q011mv"]["cycle"]["complex_phase_product_disc_audit"][
                "global_minimum_margin_witness"
            ]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_NINE_RESOLUTION_DIGEST
        )
    )
    selection["checks"]["registered_ordinal_one_hundred_forty_parent_witness_reproduces"] = (
        selection["checks"].pop(
            "registered_ordinal_one_hundred_thirty_nine_parent_witness_reproduces"
        )
    )
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
    selection["one_hundred_forty_first_parent_witness"] = selection.pop(
        "one_hundred_fortieth_parent_witness"
    )
    selection["one_hundred_forty_first_parent_witness_digest_sha256"] = selection.pop(
        "one_hundred_fortieth_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["one_hundred_forty_first_parent_witness_selection_audit"] = selection
    fixed["checks"].pop("registered_one_hundred_fortieth_parent_selection_reproduces")
    fixed["checks"]["registered_one_hundred_forty_first_parent_selection_reproduces"] = selection[
        "passed"
    ]
    fixed["checks"].pop("q011da_protocol_globals_are_restored")
    fixed["checks"]["q011mu_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    fixed["passed"] = all(fixed["checks"].values())
    return fixed, lookup, compatible, parent


def _individual_partition_audit(
    lookup: dict[str, q011z._UniformDisc],
    compatible: tuple[dict[str, Any], ...],
    parent: dict[str, Any],
) -> dict[str, Any]:
    with _q011mu_protocol_context():
        partition = q011mu._individual_partition_audit(lookup, compatible, parent)
    partition["checks"]["q011mu_protocol_globals_are_restored"] = _protocol_globals_are_restored()
    partition["passed"] = all(partition["checks"].values())
    return partition


def _registered_parameters() -> dict[str, Any]:
    with _q011mu_protocol_context():
        registered = q011mu._registered_parameters()
    registered["q011mu_protocol_adapter"] = {
        "source_runner_sha256": _file_sha256(Path(q011mu.__file__).resolve()),
        "temporary_override_names": sorted(_Q011MU_PROTOCOL_OVERRIDE),
        "globals_restored_after_use": _protocol_globals_are_restored(),
    }
    return registered


_result_digest_sections = q011mu._result_digest_sections


def run_degree_thirty_four_one_hundred_forty_first_individual_partition_audit() -> dict[str, Any]:
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
    selection = fixed["one_hundred_forty_first_parent_witness_selection_audit"]
    validity_gates = {
        "q011mv_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "339 artifacts and 1538 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_one_hundred_forty_first_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 140, class counts, 4136 multiplicity and exact witness",
            "value": selection["one_hundred_forty_first_parent_witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "seven occupied pairs, fourteen identifiers and equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "74880 total and 4136 output-block-7 compatible allocations",
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
            "threshold": "4136 unit allocations, degree 34 and output block 7",
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
                == "q011mw_degree34_one_hundred_forty_first_individual_partition_audit.py"
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
        "only_the_registered_one_hundred_forty_first_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 140 only, one target and no other aggregate",
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
            "threshold": "4136 complete parent-comparison records",
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
            "Does splitting Q011cb flatten ordinal 140 into fourteen singleton identifiers "
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
        "actual_resonance_outcome": "not_established" if validity_passed else "inconclusive",
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    prior_theorem = artifacts["q011mv"]["cycle"]["theorem_consequence"]
    cycle["theorem_consequence"] = {
        "individual_partition_is_interval_inert_for_one_hundred_forty_first_q011cb_witness": inert,
        "one_hundred_forty_first_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_one_hundred_forty_first_q011cb_witness_persists": (
            effective_persistent
        ),
        "q011mv_ordinal_one_hundred_thirty_nine_phase_resolution_is_preserved": True,
        **{name: value for name, value in prior_theorem.items() if name.endswith("_is_preserved")},
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
        "This diagnostic concerns only Q011cb flatten ordinal 140, its 4136 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 139 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44659 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011mx to expand only the registered 4136 wave allocations into component-safe complex phase discs."
        if inert
        else "Preregister Q011mx to audit the next Q011cb refined overlap in registered order."
        if resolved
        else (
            "Preregister Q011mx to refine only the first remaining individual-allocation overlap by component-safe complex phase."
        )
        if effective_persistent
        else "Repair only the first Q011mw validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011mw cycle failed strict serialization or digest")
    return cycle


def run_q011mw_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_one_hundred_forty_first_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "fourteen registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "binary64_outward_enclosure": True,
            "complex_phase_product_evaluated": False,
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "one-hundred-forty-first Q011cb witness individual-disc partition",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
            "target_identifier": TARGET_IDENTIFIER,
            "degree_thirty_four_nonresonance_claim": False,
            "actual_resonance_claim": False,
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
    result = run_q011mw_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
