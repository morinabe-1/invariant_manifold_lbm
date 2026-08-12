"""Q011bb block-support-coalesced degree-twenty-three nonresonance audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import research.q011ba_degree23_resource_estimate as q011ba
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011az = q011ba.q011az
q011an = q011az.q011an
q011b = q011ba.q011b
q011z = q011ba.q011z

SIZE = 17
DEGREE = 23

EXPECTED_DEGREE_AGGREGATE_COUNT = 2_600
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 2_161
EXPECTED_OVERLAP_AGGREGATE_COUNT = 439
EXPECTED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_TARGET_IDENTIFIER_COUNT = 300
EXPECTED_ACTIVE_IDENTIFIER_COUNT = 324
EXPECTED_MONOTONE_IDENTIFIER_COUNT = 356
EXPECTED_INACTIVE_RETAINED_IDENTIFIER_COUNT = 32
EXPECTED_MERGED_CLASS_COUNTS = (1, 1, 2, 2)
EXPECTED_CLASS_POWER_COUNT = 124
EXPECTED_GROUP_SIGNATURE_COUNT = 489
EXPECTED_PAIR_POOL_KEY_COUNT = 208
EXPECTED_CONVOLUTION_CALL_COUNT = 8_085
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 1_010_254_243_160
EXPECTED_MODULUS_SIGNATURE_COUNT = 16_792
EXPECTED_PEAK_LIVE_SIGNATURE_COUNT = 144
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 2_304
EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND = 252_396
EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND = 18_941_796_258_208
EXPECTED_SAFE_INT64_CRUDE_BOUND = 317_708_751_360

ACCEPTED_CLASSIFICATION = (
    "the block-support-coalesced component-safe sweep certifies degree-23 "
    "external nonresonance"
)
REJECTED_CLASSIFICATION = (
    "the block-support-coalesced degree-23 sufficient certificate is rejected"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011bb degree-23 coalesced audit is inconclusive"
ACCEPTED_ACTUAL_RESONANCE_OUTCOME = (
    "ruled_out_within_registered_degree_twenty_three_scope"
)

Q011BA_ARTIFACT_SHA256 = "b4069be49ec744e17eaa83eadde5947ead58c4e9dc52f812a8d3c90ab6f4ec28"
Q011BA_RUNNER_SHA256 = "ef5a20f3db4172a8f5e8791c8bff60d5c519d3d809fcc1df5a3ea64e329820fb"
Q011BA_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "envelope_digest_sha256",
    "resource_digest_sha256",
    "result_digest_sha256",
)
Q011BA_DIGESTS = (
    "2afe9132fb5f1e2b635c30a0f88be6fcfb218fdc163ff4f140d6ea40d6f4b7da",
    "27863d434c9a9a970e1e0de1bebce046fae1d9d217453974013585ecba433b36",
    "e0496aefd2de7a18ee62809f2bc38cf79d43ba31a4f489d161a989a36606203f",
    "a3e48adcca7d4d8f86e1f0d166334b0cd76f72d83d112ace56dcaef0fa05d224",
    "b060fe612a3e7bc36df532642ee703cff5e4ffbe2cdc05e7727de2e31c6a7d2b",
)


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011ba._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ba_degree23_resource_estimate.json"
    runner_path = Path(q011ba.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011BA_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    resource = cycle["degree_twenty_three_coalesced_resource_audit"]
    checks = {
        "q011ba_thirty_one_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 153
            and len(artifacts) == 31
            and all(prior["checks"].values())
        ),
        "q011ba_artifact_sha256_matches": _file_sha256(artifact_path)
        == Q011BA_ARTIFACT_SHA256,
        "q011ba_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011BA_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011BA_RUNNER_SHA256
        ),
        "q011ba_section_digests_match": digests == Q011BA_DIGESTS,
        "q011ba_registered_resource_go_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["resource_decision"] == q011ba.GO_DECISION
            and artifact["scientific_outcome"] == q011ba.SCIENTIFIC_OUTCOME
            and artifact["actual_resonance_outcome"] == q011ba.ACTUAL_RESONANCE_OUTCOME
            and cycle["failed_validity_order"] == []
            and cycle["failed_resource_limit_order"] == []
            and theorem[
                "degree_twenty_three_coalesced_full_sweep_preregistration_is_resource_supported"
            ]
            and not theorem["degree_twenty_three_external_nonresonance_is_certified"]
            and resource["product_target_relation_evaluation_count"] == 0
        ),
        "q011ba_preserves_q011az_accepted_certificate": bool(
            theorem["q011az_degree_twenty_two_certificate_is_preserved"]
            and artifacts["q011az"]["scientific_outcome"] == "accepted"
            and artifacts["q011az"]["cycle"]["theorem_consequence"][
                "degree_twenty_two_external_nonresonance_is_certified"
            ]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 23))
            and theorem["missing_external_nonresonance_degrees"] == list(range(23, 91))
        ),
        "q011ba_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ba_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ba_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_hundred_fifty_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 158
        ),
    }
    artifacts["q011ba"] = artifact
    return (
        {
            "prior_q011ba_sealed_input_audit": prior,
            "q011ba": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011BA_DIGEST_NAMES),
                "digests": list(digests),
                "resource_decision": cycle["resource_decision"],
                "degree_twenty_three_relation_evaluation_count": resource[
                    "product_target_relation_evaluation_count"
                ],
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _fixed_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[tuple[tuple[str, ...], ...], ...],
    dict[str, q011z._UniformDisc],
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
    tuple[tuple[str, ...], ...],
]:
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        external_indices,
        target_groups,
    ) = q011ba._degree_twenty_three_inventory_audit(artifacts)
    envelope, merged_classes, hull_lookup = q011ba._degree_twenty_three_envelope_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    resource = q011ba._degree_twenty_three_resource_audit(
        merged_classes, selected_groups, overlap_counts, target_groups
    )
    stored_cycle = artifacts["q011ba"]["cycle"]
    stored_inventory = stored_cycle["degree_twenty_three_inventory_audit"]
    stored_envelope = stored_cycle["degree_twenty_three_envelope_audit"]
    stored_resource = stored_cycle["degree_twenty_three_coalesced_resource_audit"]
    selected_identifiers = set().union(*map(set, selected_groups))
    target_identifiers = set().union(*map(set, target_groups))
    checks = {
        "q011ba_degree_twenty_three_inventory_recomputes_bitwise": bool(
            inventory["passed"] and inventory == stored_inventory
        ),
        "q011ba_degree_twenty_three_envelope_recomputes_bitwise": bool(
            envelope["passed"] and envelope == stored_envelope
        ),
        "q011ba_degree_twenty_three_resource_contract_recomputes_bitwise": bool(
            resource["passed"] and resource == stored_resource
        ),
        "registered_inventory_and_identifier_counts_reproduce": bool(
            inventory["degree_aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and inventory["old_modulus_separated_aggregate_count"]
            == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            and inventory["old_modulus_overlap_aggregate_count"]
            == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(selected_identifiers) == EXPECTED_SELECTED_IDENTIFIER_COUNT
            and len(target_identifiers) == EXPECTED_TARGET_IDENTIFIER_COUNT
            and len(selected_identifiers | target_identifiers) == EXPECTED_ACTIVE_IDENTIFIER_COUNT
            and envelope["final_monotone_identifier_count"]
            == EXPECTED_MONOTONE_IDENTIFIER_COUNT
            and envelope["inactive_retained_q011ay_identifier_count"]
            == EXPECTED_INACTIVE_RETAINED_IDENTIFIER_COUNT
        ),
        "registered_hull_membership_and_active_targets_reproduce": bool(
            envelope["merged_source_class_counts"] == list(EXPECTED_MERGED_CLASS_COUNTS)
            and envelope["source_hull_record_digest_sha256"]
            == q011ba.EXPECTED_HULL_RECORD_DIGEST
            and envelope["source_merged_membership_digest_sha256"]
            == q011ba.EXPECTED_MERGED_MEMBERSHIP_DIGEST
            and envelope["active_disc_record_digest_sha256"]
            == q011ba.EXPECTED_ACTIVE_RECORD_DIGEST
            and envelope["final_disc_record_digest_sha256"]
            == q011ba.EXPECTED_FINAL_RECORD_DIGEST
        ),
        "only_current_targets_are_retained_for_comparison": bool(
            not envelope["target_lookup_changed"]
            and envelope["external_target_identifier_count"]
            == EXPECTED_TARGET_IDENTIFIER_COUNT
            and set(hull_lookup) == selected_identifiers | target_identifiers
            and envelope["product_target_relation_evaluation_count"] == 0
        ),
        "fixed_inputs_are_finite_strict_json": bool(
            _all_numeric_values_finite(inventory)
            and _all_numeric_values_finite(envelope)
            and _strict_json_serializable(inventory)
            and _strict_json_serializable(envelope)
            and json.dumps({"inventory": inventory, "envelope": envelope}, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "degree_aggregate_count": inventory["degree_aggregate_count"],
        "old_modulus_separated_aggregate_count": inventory[
            "old_modulus_separated_aggregate_count"
        ],
        "direct_overlap_aggregate_count": inventory["old_modulus_overlap_aggregate_count"],
        "selected_identifier_count": len(selected_identifiers),
        "target_identifier_count": len(target_identifiers),
        "active_identifier_count": len(selected_identifiers | target_identifiers),
        "monotone_identifier_count": envelope["final_monotone_identifier_count"],
        "inactive_retained_identifier_count": envelope[
            "inactive_retained_q011ay_identifier_count"
        ],
        "merged_class_counts": envelope["merged_source_class_counts"],
        "inventory_digest_sha256": inventory["exact_inventory_digest_sha256"],
        "active_disc_record_digest_sha256": envelope["active_disc_record_digest_sha256"],
        "monotone_disc_record_digest_sha256": envelope["final_disc_record_digest_sha256"],
        "hull_record_digest_sha256": envelope["source_hull_record_digest_sha256"],
        "merged_class_membership_digest_sha256": envelope[
            "source_merged_membership_digest_sha256"
        ],
        "resource_result_digest_sha256": q011b._canonical_json_sha256(resource),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        merged_classes,
        hull_lookup,
        overlap_counts,
        external_indices,
        target_groups,
    )


def _registered_full_sweep(
    merged_classes: tuple[tuple[tuple[str, ...], ...], ...],
    hull_lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_indices: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    sweep = dict(
        q011an._full_component_safe_sweep(
            merged_classes,
            hull_lookup,
            overlap_counts,
            external_indices,
            target_groups,
        )
    )
    sweep["degree"] = DEGREE
    total_target_comparison_upper = sum(
        record["modulus_signature_count"] * record["target_identifier_count"]
        for record in sweep["aggregate_records"]
    )
    total_weighted_comparison_upper = sum(
        record["original_monomial_count"] * record["target_identifier_count"]
        for record in sweep["aggregate_records"]
    )
    all_invariants = all(
        sweep[name]
        for name in (
            "all_convolutions_nonnegative",
            "all_convolution_fiber_sums_exact",
            "all_product_bound_arrays_are_finite",
            "all_product_bound_arrays_are_nonnegative_and_ordered",
            "all_original_monomial_counts_match_multiset_coefficients",
            "all_modulus_signature_counts_match_weak_compositions",
        )
    )
    checks = {
        "all_registered_aggregates_are_processed_once": bool(
            sweep["audited_overlap_aggregate_count"] == len(overlap_counts)
            == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and len(sweep["aggregate_records"]) == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and [record["aggregate_index"] for record in sweep["aggregate_records"]]
            == list(range(EXPECTED_OVERLAP_AGGREGATE_COUNT))
        ),
        "registered_factorization_resources_reproduce": bool(
            sweep["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and sweep["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_COUNT
            and sweep["pair_pool_record_count"] == EXPECTED_PAIR_POOL_KEY_COUNT
            and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
        ),
        "registered_monomial_signature_and_peak_resources_reproduce": bool(
            sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and sweep["maximum_live_combined_signature_count"]
            == EXPECTED_PEAK_LIVE_SIGNATURE_COUNT
            and 2 * 8 * sweep["maximum_live_combined_signature_count"]
            == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
        ),
        "registered_comparison_upper_bounds_reproduce": bool(
            total_target_comparison_upper == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
            and total_weighted_comparison_upper == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
            and sweep["distinct_comparison_count"] <= total_target_comparison_upper
            and sweep["weighted_comparison_count"] <= total_weighted_comparison_upper
        ),
        "all_integer_and_outward_interval_invariants_hold": bool(
            all_invariants
            and sweep["maximum_convolution_crude_int64_bound"]
            <= EXPECTED_SAFE_INT64_CRUDE_BOUND
            and sweep["maximum_fourier_crude_int64_bound"] < 2**63
        ),
        "matrix_summaries_and_witnesses_are_present": bool(
            sweep["bound_matrix_record_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and sweep["coefficient_matrix_record_count"] > 0
            and sweep["classification_matrix_record_count"] > 0
            and sweep["global_minimum_separated_witness"] is not None
        ),
        "full_sweep_is_finite_strict_json": bool(
            _all_numeric_values_finite(sweep)
            and _strict_json_serializable(sweep)
            and json.dumps(sweep, allow_nan=False)
        ),
    }
    return {
        **sweep,
        "distinct_comparison_upper_bound": total_target_comparison_upper,
        "weighted_comparison_upper_bound": total_weighted_comparison_upper,
        "registered_checks": checks,
        "registered_passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "degree_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "direct_overlap_aggregate_count": EXPECTED_OVERLAP_AGGREGATE_COUNT,
        "selected_identifier_count": EXPECTED_SELECTED_IDENTIFIER_COUNT,
        "current_target_identifier_count": EXPECTED_TARGET_IDENTIFIER_COUNT,
        "inactive_monotone_records_compared": False,
        "merged_class_counts": list(EXPECTED_MERGED_CLASS_COUNTS),
        "target_folding_used": False,
        "target_merge_used": False,
        "full_monomial_list_retained": False,
        "full_classification_matrices_retained": False,
        "accepted_classification": ACCEPTED_CLASSIFICATION,
        "rejected_classification": REJECTED_CLASSIFICATION,
        "actual_resonance_outcome_if_accepted": ACCEPTED_ACTUAL_RESONANCE_OUTCOME,
        "degree_twenty_four_or_higher_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "preparation_digest_sha256": cycle["preparation_digest_sha256"],
        "sweep_digest_sha256": cycle["sweep_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "scientific_outcome": cycle["scientific_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_degree_twenty_three_coalesced_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        fixed,
        merged_classes,
        hull_lookup,
        overlap_counts,
        external_indices,
        target_groups,
    ) = _fixed_input_audit(artifacts)
    sweep = _registered_full_sweep(
        merged_classes, hull_lookup, overlap_counts, external_indices, target_groups
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    preparation_sections = {"fixed_coalesced_input_audit": fixed}
    sweep_sections = {"degree_twenty_three_block_support_coalesced_sweep": sweep}
    input_digest = q011b._canonical_json_sha256(input_sections)
    preparation_digest = q011b._canonical_json_sha256(preparation_sections)
    sweep_digest = q011b._canonical_json_sha256(sweep_sections)
    minimum = sweep["global_minimum_separated_witness"]
    first_overlap = sweep["first_unresolved_witness"]
    minimum_outward_positive = bool(
        minimum
        and minimum["relation"] != "overlap"
        and minimum["outward_gap_lower"]["float"] > 0
    )
    minimum_exact_positive = bool(
        minimum
        and minimum["relation"] != "overlap"
        and q011z._fraction(minimum["exact_gap"]) > 0
    )
    validity_gates = {
        "q011ba_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "32 artifacts and 158 direct digests reproduce",
            "value": sealed["checks"],
        },
        "fixed_inventory_hulls_active_targets_and_resource_contract_reproduce": {
            "passed": fixed["passed"],
            "threshold": (
                "registered inventory, monotone envelope, six hulls, active targets and "
                "resource identity"
            ),
            "value": fixed["checks"],
        },
        "all_registered_aggregates_and_arithmetic_invariants_pass": {
            "passed": sweep["registered_passed"],
            "threshold": "439 aggregates, exact integer convolutions and outward arrays",
            "value": sweep["registered_checks"],
        },
        "registered_resource_counts_reproduce": {
            "passed": bool(
                sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
                and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
                and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
                and sweep["maximum_live_combined_signature_count"]
                == EXPECTED_PEAK_LIVE_SIGNATURE_COUNT
                and sweep["distinct_comparison_upper_bound"]
                == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
                and sweep["weighted_comparison_upper_bound"]
                == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
            ),
            "threshold": "all preregistered degree-23 coalesced resource identities",
            "value": {
                "original_monomial_count": sweep["original_monomial_count"],
                "modulus_signature_count": sweep["modulus_signature_count"],
                "convolution_call_count": sweep["convolution_call_count"],
                "peak_live_signature_count": sweep[
                    "maximum_live_combined_signature_count"
                ],
            },
        },
        "matrix_summaries_are_strict_and_digestible": {
            "passed": bool(
                sweep["bound_matrix_record_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
                and sweep["coefficient_matrix_record_count"] > 0
                and sweep["classification_matrix_record_count"] > 0
                and len(sweep["bound_matrix_digest_sha256"]) == 64
                and len(sweep["coefficient_matrix_digest_sha256"]) == 64
                and len(sweep["classification_matrix_digest_sha256"]) == 64
            ),
            "threshold": "aggregate, bound, coefficient and classification streams are sealed",
            "value": {
                "aggregate": sweep["aggregate_record_digest_sha256"],
                "bound": sweep["bound_matrix_digest_sha256"],
                "coefficient": sweep["coefficient_matrix_digest_sha256"],
                "classification": sweep["classification_matrix_digest_sha256"],
            },
        },
        "registered_witness_protocol_is_satisfied": {
            "passed": bool(
                minimum is not None
                and (first_overlap is None or first_overlap["relation"] == "overlap")
            ),
            "threshold": "global separated minimum and optional first overlap exact witness",
            "value": {
                "minimum_witness_digest": minimum["witness_digest_sha256"],
                "first_overlap_witness_digest": (
                    first_overlap["witness_digest_sha256"] if first_overlap else None
                ),
            },
        },
        "q011az_certificate_sections_and_runner_provenance_reproduce": {
            "passed": bool(
                artifacts["q011az"]["scientific_outcome"] == "accepted"
                and artifacts["q011az"]["cycle"]["theorem_consequence"][
                    "degree_twenty_two_external_nonresonance_is_certified"
                ]
                and len(input_digest) == len(preparation_digest) == len(sweep_digest) == 64
                and runner["filename"] == "q011bb_degree23_coalesced_sweep.py"
            ),
            "threshold": "degree-22 certificate, three section digests and runner metadata",
            "value": {
                "input": input_digest,
                "preparation": preparation_digest,
                "sweep": sweep_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "six_hulls_cover_sources_and_all_current_targets_are_preserved": {
            "passed": bool(
                fixed["merged_class_counts"] == list(EXPECTED_MERGED_CLASS_COUNTS)
                and fixed["selected_identifier_count"] == EXPECTED_SELECTED_IDENTIFIER_COUNT
                and fixed["target_identifier_count"] == EXPECTED_TARGET_IDENTIFIER_COUNT
                and fixed["inactive_retained_identifier_count"]
                == EXPECTED_INACTIVE_RETAINED_IDENTIFIER_COUNT
            ),
            "threshold": "six source hulls, 24 sources and 300 current targets only",
            "value": fixed["checks"],
        },
        "every_direct_comparison_is_strictly_separated": {
            "passed": sweep["distinct_relation_counts"]["overlap"] == 0,
            "threshold": "every compatible comparison has overlap count zero",
            "value": sweep["distinct_relation_counts"],
        },
        "old_and_direct_aggregates_cover_degree_twenty_three": {
            "passed": bool(
                EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
                + sweep["fully_separated_overlap_aggregate_count"]
                == EXPECTED_DEGREE_AGGREGATE_COUNT
            ),
            "threshold": "2161 preserved plus 439 direct equals 2600",
            "value": {
                "old": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
                "direct": sweep["fully_separated_overlap_aggregate_count"],
            },
        },
        "global_minimum_outward_and_exact_gaps_are_positive": {
            "passed": minimum_outward_positive and minimum_exact_positive,
            "threshold": "strictly positive outward and exact rational minimum gap",
            "value": {
                "outward": minimum["outward_gap_lower"],
                "exact_gap_hex": minimum.get("exact_gap_hex"),
            },
        },
        "claim_is_limited_to_registered_degree_twenty_three_scope": {
            "passed": True,
            "threshold": "no degree 24--90, all-order, SSM or basin extrapolation",
            "value": "fixed 17x17 leaf and registered degree-23 external relation only",
        },
    }
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    accepted = validity_passed and hypothesis_passed
    rejected = validity_passed and not hypothesis_passed
    classification = (
        ACCEPTED_CLASSIFICATION
        if accepted
        else REJECTED_CLASSIFICATION
        if rejected
        else INCONCLUSIVE_CLASSIFICATION
    )
    scientific_outcome = "accepted" if accepted else "rejected" if rejected else "inconclusive"
    actual_resonance_outcome = (
        ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        if accepted
        else "not_established"
        if rejected
        else "not_evaluated"
    )
    cycle = {
        "question": (
            "Does the preregistered block-support-coalesced component-safe sweep separate "
            "every degree-twenty-three external product-target relation?"
        ),
        **input_sections,
        **preparation_sections,
        **sweep_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "preparation_digest_sha256": preparation_digest,
        "sweep_digest_sha256": sweep_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_validity_order": [
            name for name, gate in validity_gates.items() if not gate["passed"]
        ],
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "scientific_outcome": scientific_outcome,
        "scientific_classification": classification,
        "actual_resonance_outcome": actual_resonance_outcome,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    certified_degrees = list(range(2, 24)) if accepted else list(range(2, 23))
    missing_degrees = list(range(24, 91)) if accepted else list(range(23, 91))
    cycle["theorem_consequence"] = {
        "degree_twenty_three_external_nonresonance_is_certified": accepted,
        "an_actual_degree_twenty_three_external_resonance_is_ruled_out": accepted,
        "registered_degree_twenty_three_sufficient_certificate_is_rejected": rejected,
        "certified_external_nonresonance_degrees": certified_degrees,
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": missing_degrees,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011az_degree_twenty_two_certificate_is_preserved": True,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only the registered degree-twenty-three external "
        "product-target relations for the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf, using the six Q011as source hulls, all 300 current Q011ba "
        "target discs, exact Fourier multiplicities and outward-rounded hierarchical "
        "product intervals. Thirty-two inactive monotone proof records are retained but "
        "not compared. It makes no claim for degrees 24--90, all-order nonresonance, "
        "higher graph smoothness, SSM existence or uniqueness, normal attraction, a "
        "basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Run a design-only Q011bc degree-twenty-four resource estimate before "
        "preregistering any degree-twenty-four full sweep."
        if accepted
        else "Audit only the first registered degree-twenty-three overlap witness before "
        "changing any hull or target representation."
        if rejected
        else "Repair only the first Q011bb validity failure before changing the sweep."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011bb cycle failed strict serialization or digest")
    return cycle


def run_q011bb_study() -> dict[str, Any]:
    cycle = run_degree_twenty_three_coalesced_audit()
    sweep = cycle["degree_twenty_three_block_support_coalesced_sweep"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_hulls": "exact rational endpoint hulls fixed by Q011as",
            "product_enclosure": "outward-rounded binary64 hierarchical products",
            "fourier_multiplicity": "exact int64 cyclic convolution",
            "target_comparisons": "all 300 current target discs without folding",
            "inactive_monotone_records_compared": False,
            "full_monomial_list_retained": False,
            "full_classification_matrices_retained": False,
            "convolution_call_count": sweep["convolution_call_count"],
            "peak_live_signature_count": sweep["maximum_live_combined_signature_count"],
        },
        "mathematical_scope": {
            "diagnostic": "degree-23 block-support-coalesced external nonresonance",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_twenty_four_or_higher_claim": False,
            "all_order_nonresonance_claim": False,
            "ssm_uniqueness_claim": False,
            "normal_attraction_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011bb_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
