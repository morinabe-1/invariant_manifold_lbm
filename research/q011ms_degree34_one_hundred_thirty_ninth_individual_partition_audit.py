"""Q011ms individual-disc partition audit for Q011cb flatten ordinal one hundred thirty-eight."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011da_degree34_thirteenth_individual_partition_audit as q011da
import research.q011mr_degree34_one_hundred_thirty_eighth_component_safe_phase_discs as q011mr
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
PARENT_FLAT_ORDINAL = 138
PARENT_LEFT_INDEX = 17
PARENT_RIGHT_INDEX = 2
PARENT_CLASS_COUNTS = (
    (0, 0, 1, 12),
    (7, 2),
    (5,),
    (2, 5),
)
OCCUPIED_SPEC = (
    (0, 2, 1),
    (0, 3, 12),
    (1, 0, 7),
    (1, 1, 2),
    (2, 0, 5),
    (3, 0, 2),
    (3, 1, 5),
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
EXPECTED_SOURCE_COUNTS = (1, 0, 12, 0, 7, 0, 2, 0, 0, 5, 0, 2, 0, 5)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 1, 0, 12, 0, 7, 0, 2, 0, 5, 0, 2, 5, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = EXPECTED_SOURCE_COUNTS
EXPECTED_PARENT_ALLOCATION_INDEX = 67_284
EXPECTED_PARENT_COMPATIBLE_INDEX = 3_726
EXPECTED_ALLOCATION_COUNT = 67_392
EXPECTED_COMPATIBLE_COUNT = 3_727

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "8c192189449f149db3b3786d791a4fc262ff9ff3c89d831307cbab2faa614734",
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "e5b5ce415bac811880fc0ccaa97743c37d7e2510a679d48e627a6eaad2c05399",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
    "aea681cab5d2a0c4176e23896038ecfc3433ebb73dfc9ecd3567248e73d989db",
    "66a6c269ac137479694f186884d49ca3a4d11070e69132bab822391a557075d8",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = "08d656c80f64b96d56518ed16f01e60a3b27a361996a9e8a8297a860d0c4f7ea"
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "c90ea70931e0bb67733cb9179566e166baf2a67756933394db785fb4f941276a"
)
EXPECTED_ALLOCATION_DIGEST = "91e58b9b6fe7d1f04e888d64a64b47a561cefe16d2f98e9e13c408157a41edf1"
EXPECTED_COMPATIBLE_DIGEST = "1b3031c954841a495e4fc1b3d2ca3709f4b9536064ee1219ced946edb365d16e"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 3_727
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.3ba15bbd61b9cp-31"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.33d06e3bd0925p-28"
EXPECTED_PARENT_WITNESS_DIGEST = "6128f3a723750195fde10cda46788dd575f0229445c5c9f955b4e49754a99a42"
EXPECTED_PARENT_PRODUCT_DIGEST = "52903af47bd60f1d49fb21a6a5133dd9d9c66bc4a02ae3dcc0f7a8fe00651bfa"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "a7b328d296e4fa064b7a38b98cbe50b6185063bb016f4a0f8aeb561ee143c235"
)
EXPECTED_PARENT_TARGET_DIGEST = "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "5a999d67b110ffdd3ab8880b3937d8b97783ade7f409c5c6efd1319b4b87ba6a"
)
EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_SEVEN_RESOLUTION_DIGEST = (
    "9d542b49c39fd1540ca85a454354fb568fed3d9fabd5fb55e44188171d03875d"
)

Q011MR_ARTIFACT_SHA256 = "9b0b28b7b7825f641d50bce65164b13e27709b91ead3a280f906602139cecc2d"
Q011MR_RUNNER_SHA256 = "fac1bcaa26028ef10eccf5458685919496d4881d38beeda51ff2b0b2f1e73a7b"
Q011MR_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011MR_DIGESTS = (
    "257b4bd4c5399741929a7cec5c1b938cd0250bb6fa285a8db7f3fd3605bf02f1",
    "328b6126590409f631f5dbba9d720782555175f6ade98450e9f554a516a3dde5",
    "c3f7ed307fd129e8dcf40bd4605eae7f299885ed72a19cd99b46962facd306c5",
    "fff03687602c38edc87a9ad4e9adfd82de6b312c7a1c0658584ad9048d01a207",
    "84a81fcce73bc7c68dbafa49913db60d8f46d8b7a68fb9c2d7cf6e6e7cd54237",
)
EXPECTED_Q011MR_STREAM_DIGEST = "97694244c1cdbd36bfa47cf10d8f428b690296dc732d3f6418e2dad59d822686"

INERT_CLASSIFICATION = "the individual-disc partition is interval-inert for the one-hundred-thirty-ninth Q011cb witness"
RESOLVED_CLASSIFICATION = (
    "the one-hundred-thirty-ninth Q011cb witness is resolved by individual partition"
)
EFFECTIVE_PERSISTENT_CLASSIFICATION = "the individual-disc partition changes intervals but the one-hundred-thirty-ninth Q011cb witness persists"
INCONCLUSIVE_CLASSIFICATION = "the Q011ms individual-disc partition audit is inconclusive"

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
        and q011mr._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011mr._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011mr_degree34_one_hundred_thirty_eighth_component_safe_phase_discs.json"
    )
    runner_path = Path(q011mr.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011MR_DIGEST_NAMES)
    checks = {
        "q011mr_three_hundred_thirty_four_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 334
            and prior["direct_digest_count"] == 1_515
            and len(artifacts) == 334
            and all(prior["checks"].values())
        ),
        "q011mr_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011MR_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011MR_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011MR_RUNNER_SHA256
        ),
        "q011mr_section_digests_match": digests == Q011MR_DIGESTS,
        "q011mr_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "component_safe_complex_phase_discs_resolve_one_hundred_thirty_eighth_q011cb_witness"
            ]
            and theorem[
                "q011mq_ordinal_one_hundred_thirty_seven_interval_inert_diagnostic_is_preserved"
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
        "q011mr_registered_ordinal_one_hundred_thirty_seven_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 26_644
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 26_644,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"] == EXPECTED_Q011MR_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_SEVEN_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011mr_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_thousand_five_hundred_twenty_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 1_520
        ),
    }
    artifacts["q011mr"] = artifact
    return (
        {
            "prior_q011mr_sealed_input_audit": prior,
            "q011mr": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011MR_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": (
                    EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_SEVEN_RESOLUTION_DIGEST
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
    with _q011da_protocol_context():
        fixed, lookup, compatible, parent = q011da._fixed_individual_input_audit(artifacts)
    selection = fixed.pop("thirteenth_parent_witness_selection_audit")
    selection["previous_phase_resolved_ordinals"] = list(range(138))
    selection["ordinal_one_hundred_thirty_seven_resolution_digest_sha256"] = (
        EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_SEVEN_RESOLUTION_DIGEST
    )
    selection["checks"][
        "ordinal_one_hundred_thirty_seven_is_the_sealed_q011mr_phase_resolution"
    ] = bool(
        artifacts["q011mr"]["cycle"]["theorem_consequence"][
            "component_safe_complex_phase_discs_resolve_one_hundred_thirty_eighth_q011cb_witness"
        ]
        and artifacts["q011mr"]["cycle"]["theorem_consequence"][
            "q011mq_ordinal_one_hundred_thirty_seven_interval_inert_diagnostic_is_preserved"
        ]
        and artifacts["q011mr"]["cycle"]["complex_phase_product_disc_audit"][
            "global_minimum_margin_witness"
        ]["witness_digest_sha256"]
        == EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_SEVEN_RESOLUTION_DIGEST
    )
    selection["checks"]["registered_ordinal_one_hundred_thirty_eight_parent_witness_reproduces"] = (
        selection["checks"].pop("registered_ordinal_twelve_parent_witness_reproduces")
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
    selection["one_hundred_thirty_ninth_parent_witness"] = selection.pop(
        "thirteenth_parent_witness"
    )
    selection["one_hundred_thirty_ninth_parent_witness_digest_sha256"] = selection.pop(
        "thirteenth_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["one_hundred_thirty_ninth_parent_witness_selection_audit"] = selection
    fixed["checks"].pop("registered_thirteenth_parent_selection_reproduces")
    fixed["checks"]["registered_one_hundred_thirty_ninth_parent_selection_reproduces"] = selection[
        "passed"
    ]
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


def run_degree_thirty_four_one_hundred_thirty_ninth_individual_partition_audit() -> dict[str, Any]:
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
    selection = fixed["one_hundred_thirty_ninth_parent_witness_selection_audit"]
    validity_gates = {
        "q011mr_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "335 artifacts and 1520 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_one_hundred_thirty_ninth_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 138, class counts, 3727 multiplicity and exact witness",
            "value": selection["one_hundred_thirty_ninth_parent_witness_digest_sha256"],
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
            "threshold": "67392 total and 3727 output-block-7 compatible allocations",
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
            "threshold": "3727 unit allocations, degree 34 and output block 7",
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
                == "q011ms_degree34_one_hundred_thirty_ninth_individual_partition_audit.py"
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
        "only_the_registered_one_hundred_thirty_ninth_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 138 only, one target and no other aggregate",
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
            "threshold": "3727 complete parent-comparison records",
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
            "Does splitting Q011cb flatten ordinal 138 into fourteen singleton identifiers "
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
    prior_theorem = artifacts["q011mr"]["cycle"]["theorem_consequence"]
    cycle["theorem_consequence"] = {
        "individual_partition_is_interval_inert_for_one_hundred_thirty_ninth_q011cb_witness": inert,
        "one_hundred_thirty_ninth_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_one_hundred_thirty_ninth_q011cb_witness_persists": (
            effective_persistent
        ),
        "q011mr_ordinal_one_hundred_thirty_seven_phase_resolution_is_preserved": True,
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
        "This diagnostic concerns only Q011cb flatten ordinal 138, its 3727 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 137 only as sealed selection boundaries and does "
        "not reevaluate them. It does not evaluate complex phase, the later 44661 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole or aggregate 972. It leaves prior "
        "rejection, persistence, partition-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011mt to expand only the registered 3727 wave allocations into component-safe complex phase discs."
        if inert
        else "Preregister Q011mt to audit the next Q011cb refined overlap in registered order."
        if resolved
        else (
            "Preregister Q011mt to refine only the first remaining individual-allocation overlap by component-safe complex phase."
        )
        if effective_persistent
        else "Repair only the first Q011ms validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011ms cycle failed strict serialization or digest")
    return cycle


def run_q011ms_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_one_hundred_thirty_ninth_individual_partition_audit()
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
            "diagnostic": "one-hundred-thirty-ninth Q011cb witness individual-disc partition",
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
    result = run_q011ms_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
