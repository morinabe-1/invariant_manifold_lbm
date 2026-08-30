"""Q011mo individual-disc partition audit for Q011cb flatten ordinal one hundred thirty-six."""

from __future__ import annotations

import argparse
import json
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011da_degree34_thirteenth_individual_partition_audit as q011da
import research.q011mn_degree34_one_hundred_thirty_sixth_component_safe_phase_discs as q011mn
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
PARENT_FLAT_ORDINAL = 136
PARENT_LEFT_INDEX = 17
PARENT_RIGHT_INDEX = 0
PARENT_CLASS_COUNTS = (
    (0, 0, 1, 12),
    (7, 2),
    (5,),
    (0, 7),
)
OCCUPIED_SPEC = (
    (0, 2, 1),
    (0, 3, 12),
    (1, 0, 7),
    (1, 1, 2),
    (2, 0, 5),
    (3, 1, 7),
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
    "block=16;center=149",
    "block=1;center=149",
)
EXPECTED_SOURCE_COUNTS = (1, 0, 12, 0, 7, 0, 2, 0, 0, 5, 0, 7)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 1, 0, 12, 0, 7, 0, 2, 0, 5, 5, 2)
EXPECTED_LAST_COMPATIBLE_COUNTS = EXPECTED_SOURCE_COUNTS
EXPECTED_PARENT_ALLOCATION_INDEX = 29_904
EXPECTED_PARENT_COMPATIBLE_INDEX = 1_666
EXPECTED_ALLOCATION_COUNT = 29_952
EXPECTED_COMPATIBLE_COUNT = 1_667

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "8c192189449f149db3b3786d791a4fc262ff9ff3c89d831307cbab2faa614734",
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "e5b5ce415bac811880fc0ccaa97743c37d7e2510a679d48e627a6eaad2c05399",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
    "66a6c269ac137479694f186884d49ca3a4d11070e69132bab822391a557075d8",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = "b99e46aa8b06b9c1a8ee2624747989734c5631b52a1b2572aa1d4e17dc50e395"
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "5063f9638bf5dfbe8b90cf76615268ba4ba6f3b3825d56aac972329725852257"
)
EXPECTED_ALLOCATION_DIGEST = "ebcc79dbd8ebb5cabf420bc5103c6e312082fa35434545f64e44b3051d32f8fe"
EXPECTED_COMPATIBLE_DIGEST = "ff5ba3af2f7d4fed204710a09078e1c07a56155bab984392263eafe8c0cae173"

EXPECTED_PARENT_WAVE_MULTIPLICITY = 1_667
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.3ba1774ead540p-31"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.33d072f343652p-28"
EXPECTED_PARENT_WITNESS_DIGEST = "4800695011aff621eae717f57291f37d6c22e9591f595cdfc436f925193873ea"
EXPECTED_PARENT_PRODUCT_DIGEST = "5d01f5f0ddd84669c9aea65c7b59fc777f59d65d1f46e7d40c5fb7437d7b0b2a"
EXPECTED_PARENT_CENTER_PRODUCT_DIGEST = (
    "8e2eb300b288a76ea8c12cab263a4d7c0038ed8ba8308d0d6ace07057b16794a"
)
EXPECTED_PARENT_TARGET_DIGEST = "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
EXPECTED_PARENT_INTERSECTION_DIGEST = (
    "902f32def2a9b6e06e2c437e1b18c2ab67c92dbf4a479bf9866bbff11c57c144"
)
EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_FIVE_RESOLUTION_DIGEST = (
    "cba06ceb15335a288a1ea6e0d24caf4f450a26e54b3b51f5e46e84b7526d6868"
)

Q011MN_ARTIFACT_SHA256 = "5bc691436ff9d75f5e4b2af7af1850cefdb32b50147439ef6c4c022615171446"
Q011MN_RUNNER_SHA256 = "43647809f759b5936eddc5ecbbff3eb7aecb742daf4a57374dad45d4105958f1"
Q011MN_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011MN_DIGESTS = (
    "a9c63865f7770397d2b61b6a57fea595a4254b39c19a93723051f7654b5a4e1b",
    "4b2c4c05ffe94f35810bb784c6a11eaa2f69b0ddd41350ff36b37f0a25ce9ea0",
    "8dd3d1110d024ce7a49ae811715f7e7fde9244db9f4aa897681274a5cd1c5ec1",
    "ab5d843c6628625abd07fcf367235ccadea590dba9578a861c34365f6ee60ba8",
    "dcb27eea4dca32b693cb985d054580d98328cc4f5a1bc916af5fad1a8a90579c",
)
EXPECTED_Q011MN_STREAM_DIGEST = "6a21a34db585086f4b689c0c1932d9d23b30535f11cb604e56d7e8f3e7952dd6"

INERT_CLASSIFICATION = "the individual-disc partition is interval-inert for the one-hundred-thirty-seventh Q011cb witness"
RESOLVED_CLASSIFICATION = (
    "the one-hundred-thirty-seventh Q011cb witness is resolved by individual partition"
)
EFFECTIVE_PERSISTENT_CLASSIFICATION = "the individual-disc partition changes intervals but the one-hundred-thirty-seventh Q011cb witness persists"
INCONCLUSIVE_CLASSIFICATION = "the Q011mo individual-disc partition audit is inconclusive"

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
        and q011mn._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011mn._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011mn_degree34_one_hundred_thirty_sixth_component_safe_phase_discs.json"
    )
    runner_path = Path(q011mn.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011MN_DIGEST_NAMES)
    checks = {
        "q011mn_three_hundred_thirty_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 330
            and prior["direct_digest_count"] == 1_497
            and len(artifacts) == 330
            and all(prior["checks"].values())
        ),
        "q011mn_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011MN_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011MN_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011MN_RUNNER_SHA256
        ),
        "q011mn_section_digests_match": digests == Q011MN_DIGESTS,
        "q011mn_valid_phase_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "component_safe_complex_phase_discs_resolve_one_hundred_thirty_sixth_q011cb_witness"
            ]
            and theorem[
                "q011mm_ordinal_one_hundred_thirty_five_interval_inert_diagnostic_is_preserved"
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
        "q011mn_registered_ordinal_one_hundred_thirty_five_resolution_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 15_278
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 15_278,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"] == EXPECTED_Q011MN_STREAM_DIGEST
            and comparison["global_minimum_margin_witness"]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_FIVE_RESOLUTION_DIGEST
            and comparison["first_unresolved_witness"] is None
        ),
        "q011mn_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_thousand_five_hundred_two_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 1_502
        ),
    }
    artifacts["q011mn"] = artifact
    return (
        {
            "prior_q011mn_sealed_input_audit": prior,
            "q011mn": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011MN_DIGEST_NAMES),
                "digests": list(digests),
                "resolved_witness_digest_sha256": (
                    EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_FIVE_RESOLUTION_DIGEST
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
    selection["previous_phase_resolved_ordinals"] = list(range(136))
    selection["ordinal_one_hundred_thirty_five_resolution_digest_sha256"] = (
        EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_FIVE_RESOLUTION_DIGEST
    )
    selection["checks"]["ordinal_one_hundred_thirty_five_is_the_sealed_q011mn_phase_resolution"] = (
        bool(
            artifacts["q011mn"]["cycle"]["theorem_consequence"][
                "component_safe_complex_phase_discs_resolve_one_hundred_thirty_sixth_q011cb_witness"
            ]
            and artifacts["q011mn"]["cycle"]["complex_phase_product_disc_audit"][
                "global_minimum_margin_witness"
            ]["witness_digest_sha256"]
            == EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_FIVE_RESOLUTION_DIGEST
        )
    )
    selection["checks"]["registered_ordinal_one_hundred_thirty_six_parent_witness_reproduces"] = (
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
    selection["one_hundred_thirty_seventh_parent_witness"] = selection.pop(
        "thirteenth_parent_witness"
    )
    selection["one_hundred_thirty_seventh_parent_witness_digest_sha256"] = selection.pop(
        "thirteenth_parent_witness_digest_sha256"
    )
    selection["passed"] = all(selection["checks"].values())
    fixed["one_hundred_thirty_seventh_parent_witness_selection_audit"] = selection
    fixed["checks"].pop("registered_thirteenth_parent_selection_reproduces")
    fixed["checks"]["registered_one_hundred_thirty_seventh_parent_selection_reproduces"] = (
        selection["passed"]
    )
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


def run_degree_thirty_four_one_hundred_thirty_seventh_individual_partition_audit() -> dict[
    str, Any
]:
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
    selection = fixed["one_hundred_thirty_seventh_parent_witness_selection_audit"]
    validity_gates = {
        "q011mn_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "331 artifacts and 1502 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_one_hundred_thirty_seventh_parent_witness_reproduces": {
            "passed": selection["passed"],
            "threshold": "ordinal 136, class counts, 1667 multiplicity and exact witness",
            "value": selection["one_hundred_thirty_seventh_parent_witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "six occupied pairs, twelve identifiers and zero-power exclusion",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "29952 total and 1667 output-block-7 compatible allocations",
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
            "threshold": "1667 unit allocations, degree 34 and output block 7",
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
                == "q011mo_degree34_one_hundred_thirty_seventh_individual_partition_audit.py"
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
        "only_the_registered_one_hundred_thirty_seventh_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["previous_q011cb_refined_signatures_recomputed"]
                and not fixed["later_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "ordinal 136 only, one target and no other aggregate",
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
            "threshold": "1667 complete parent-comparison records",
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
            "Does splitting Q011cb flatten ordinal 136 into twelve positive-power singleton identifiers "
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
    prior_theorem = artifacts["q011mn"]["cycle"]["theorem_consequence"]
    cycle["theorem_consequence"] = {
        "individual_partition_is_interval_inert_for_one_hundred_thirty_seventh_q011cb_witness": inert,
        "one_hundred_thirty_seventh_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_one_hundred_thirty_seventh_q011cb_witness_persists": effective_persistent,
        "q011mn_ordinal_one_hundred_thirty_five_phase_resolution_is_preserved": True,
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
        "This diagnostic concerns only Q011cb flatten ordinal 136, its 1667 "
        "output-block-7 singleton allocations and target block=7;center=44 for the "
        "fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. "
        "It uses ordinals 0 through 135 only as sealed selection boundaries and does "
        "not reevaluate them. All twelve positive-power singleton identifiers, "
        "including center 149, are retained; the zero-power center-148 pair is "
        "excluded. It does not evaluate complex phase, the later 44663 Q011cb "
        "refined signatures, the other 31 parent "
        "coalesced overlaps, other targets, aggregate 2340 as a whole or aggregate "
        "972. It leaves prior rejection, persistence, partition-inert and "
        "phase-resolution results, certified degrees 2--33 and 91+, and missing "
        "degrees 34--90 unchanged, and makes no claim about an actual resonance, "
        "degree-34 or all-order nonresonance, higher graph smoothness, SSM existence "
        "or uniqueness, normal attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011mp to expand only the registered 1667 wave allocations into component-safe complex phase discs."
        if inert
        else "Preregister Q011mp to audit Q011cb flatten ordinal 137 in registered order."
        if resolved
        else (
            "Preregister Q011mp to refine only the first remaining individual-allocation overlap by component-safe complex phase."
        )
        if effective_persistent
        else "Repair only the first Q011mo validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011mo cycle failed strict serialization or digest")
    return cycle


def run_q011mo_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_one_hundred_thirty_seventh_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "twelve positive-power registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "binary64_outward_enclosure": True,
            "complex_phase_product_evaluated": False,
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "one-hundred-thirty-seventh Q011cb witness individual-disc partition",
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
    result = run_q011mo_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
