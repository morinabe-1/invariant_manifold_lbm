"""Q011bk design-only degree-twenty-eight block-support resource audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

import research.q011bj_degree27_coalesced_sweep as q011bj
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011bi = q011bj.q011bi
q011ap = q011bi.q011ap
q011as = q011bi.q011as
q011b = q011bi.q011b
q011u = q011bi.q011u
q011z = q011bi.q011z

SIZE = 17
DEGREE = 28

EXPECTED_DEGREE_AGGREGATE_COUNT = 4_495
EXPECTED_EXPANDED_CONTROL_COUNT = 237_336
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 3_325
EXPECTED_OVERLAP_AGGREGATE_COUNT = 1_170
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_UNIQUE_EXTERNAL_GROUP_COUNT = 49
EXPECTED_TARGET_IDENTIFIER_COUNT = 612
EXPECTED_MULTI_TARGET_AGGREGATE_COUNT = 2
EXPECTED_MAXIMUM_EXTERNAL_COMPONENT_COUNT = 3
EXPECTED_TARGET_BLOCK_COUNTS = (
    22,
    28,
    20,
    22,
    35,
    49,
    47,
    40,
    54,
    54,
    40,
    47,
    49,
    35,
    22,
    20,
    28,
)
EXPECTED_FIRST_COUNTS = (0, 3, 2, 23)
EXPECTED_LAST_COUNTS = (25, 1, 2, 0)
EXPECTED_COUNT_TUPLE_DIGEST = "57ec3fb44805445f6551d07a559c3db5d86f87b178bbbe36a2ff367eb07c8687"
EXPECTED_EXTERNAL_GROUP_DIGEST = "d4a000e8a40f4072942ce7a800f49c35c0c818e2e2817c78f5d94757f6acdaeb"
EXPECTED_OVERLAP_RECORD_DIGEST = "ceeb0b4133a0b6724a0335ff6cac6a3092ae8871fd362edbbf20537ec25ff8b3"
EXPECTED_TARGET_RECORD_DIGEST = "213c785d2df051dcde94460e45b28d1fd68fbaac6d53372764230935ca4e56c8"
EXPECTED_INVENTORY_DIGEST = "8f252e9fef87b452eb34d4de5710dbe8c93e3882c9d48fd3a15a78c05d00e23a"

EXPECTED_PRIOR_IDENTIFIER_COUNT = 604
EXPECTED_ACTIVE_REUSED_IDENTIFIER_COUNT = 512
EXPECTED_INACTIVE_RETAINED_IDENTIFIER_COUNT = 92
EXPECTED_ADDED_TARGET_IDENTIFIER_COUNT = 124
EXPECTED_ACTIVE_IDENTIFIER_COUNT = 636
EXPECTED_FINAL_IDENTIFIER_COUNT = 728
EXPECTED_PRIOR_RECORD_DIGEST = "7fe2788ea086583cc7b6c4f19ceb24df3b8135ad35f92883a182c2b04fcd3b5f"
EXPECTED_ACTIVE_REUSED_RECORD_DIGEST = (
    "1a6fd9676b3ccdca51587ef4587937f8f0af8a778bdb4ce364a89ef0fde2db08"
)
EXPECTED_INACTIVE_IDENTIFIER_DIGEST = (
    "0fa1279c56f06e9de2ff8c20128d611d0e53e01981628fa88f05fe1c201f1b0d"
)
EXPECTED_ADDED_IDENTIFIER_DIGEST = (
    "197d42997b4a2470edd61be7ec8af34c7ddd3887e93d5e23dfa0159274fe2ddc"
)
EXPECTED_ADDED_RECORD_DIGEST = "bc2aac7fa7405e3628b600298c2fad3116fa38b3bc1132798f41a64e19c11f38"
EXPECTED_ACTIVE_RECORD_DIGEST = "3ff49a56c7f7d04700e3fabbfc0016cb7bafe58ead2bf2679d2983b55e18485f"
EXPECTED_FINAL_RECORD_DIGEST = "fd71582666951d84182354bbc8a1df7f8b5d298a4a5a01256595c26a319f2911"
EXPECTED_OLD_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_MERGED_CLASS_COUNTS = (1, 1, 2, 2)
EXPECTED_HULL_RECORD_DIGEST = q011bi.EXPECTED_HULL_RECORD_DIGEST
EXPECTED_MERGED_MEMBERSHIP_DIGEST = q011bi.EXPECTED_MERGED_MEMBERSHIP_DIGEST

EXPECTED_CLASS_POWER_COUNT = 161
EXPECTED_CLASS_POWER_KEY_DIGEST = (
    "0a547ea979be4a9fb7d71f9efada338b1b6048e75530faee224d48f31f8758bd"
)
EXPECTED_GROUP_POOL_KEY_COUNT = 107
EXPECTED_GROUP_POOL_KEY_DIGEST = (
    "3ff0eff6c14e72d766685240df4171afd9ab2b10cc469298199ebddebea4d4f8"
)
EXPECTED_GROUP_SIGNATURE_COUNT = 810
EXPECTED_PAIR_POOL_KEY_COUNT = 398
EXPECTED_PAIR_POOL_KEY_DIGEST = (
    "4f3847d4b838d0c17f192259d0e33768f7ae504e6c1227c72a8fabe1451398db"
)
EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT = 12_938
EXPECTED_CONVOLUTION_CALL_COUNT = 14_505
EXPECTED_MODULUS_SIGNATURE_COUNT = 57_529
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 182
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 2_912
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 53_517_100_201_931
EXPECTED_MAXIMUM_AGGREGATE_MONOMIAL_COUNT = 445_981_536_000
EXPECTED_SAFE_INT64_CRUDE_BOUND = 7_581_686_112_000
EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND = 995_152
EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND = 971_674_189_747_228
EXPECTED_RESOURCE_RECORD_DIGEST = (
    "d79ca8b4614df01342c731e095d4d0143c71497fe39433b24f04739f9fd3a5e2"
)
EXPECTED_PROJECTED_SECONDS = Fraction(133_141_821_459, 288_723_920_000)
EXPECTED_DOUBLE_SAFETY_SECONDS = Fraction(133_141_821_459, 144_361_960_000)
EXPECTED_TRACEMALLOC_SAFETY_BYTES = 134_805
EXPECTED_PROCESS_MEMORY_SAFETY_BYTES = 372_027

RESOURCE_LIMITS = dict(q011bi.RESOURCE_LIMITS)
GO_DECISION = "go_for_degree_twenty_eight_coalesced_preregistration"
STOP_DECISION = "stop_before_degree_twenty_eight_coalesced_full_sweep"
INCONCLUSIVE_DECISION = "inconclusive_resource_audit"
SCIENTIFIC_OUTCOME = "not_evaluated"
ACTUAL_RESONANCE_OUTCOME = "not_evaluated"

Q011BJ_ARTIFACT_SHA256 = "e3ac46e0e44fb4138980ddecfa5a41d65c0ebadfa5755e936281f0157152ff3e"
Q011BJ_RUNNER_SHA256 = "ebc93c5114b9b96f7cdff5b764119e08f14575c616c3427b30cc4de7be41349b"
Q011BJ_DIGEST_NAMES = (
    "input_digest_sha256",
    "preparation_digest_sha256",
    "sweep_digest_sha256",
    "result_digest_sha256",
)
Q011BJ_DIGESTS = (
    "7ac35285a7ada2fb49dd682f19f00a47409cc787df38efd161f71a2f7a14a97a",
    "487e461a87c3ff5348bec8a7d2a9aa2edf6a0cf395d75621cadbb1488eac794d",
    "c03d4005541cd1d2ebb6479cfb141cac890c54b61df600e7cfaa7f5ae4f097e1",
    "39d7e3966f6369077d7de9d1ad0838a40be14ac68c53cbb5fb2a1c6a1a8b19fc",
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


def _fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "float": float(value),
    }


def _record_fraction(record: dict[str, Any]) -> Fraction:
    return Fraction(record["numerator"], record["denominator"])


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011bj._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011bj_degree27_coalesced_sweep.json"
    runner_path = Path(q011bj.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011BJ_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    checks = {
        "q011bj_forty_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 194
            and len(artifacts) == 40
            and all(prior["checks"].values())
        ),
        "q011bj_artifact_sha256_matches": _file_sha256(artifact_path)
        == Q011BJ_ARTIFACT_SHA256,
        "q011bj_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011BJ_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011BJ_RUNNER_SHA256
        ),
        "q011bj_section_digests_match": digests == Q011BJ_DIGESTS,
        "q011bj_accepted_degree_twenty_seven_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and artifact["actual_resonance_outcome"]
            == q011bj.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
            and cycle["failed_validity_order"] == []
            and cycle["failed_hypothesis_order"] == []
            and theorem["degree_twenty_seven_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 28))
            and theorem["missing_external_nonresonance_degrees"] == list(range(28, 91))
        ),
        "q011bj_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011bj_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011bj_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_hundred_ninety_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 198
        ),
    }
    artifacts["q011bj"] = artifact
    return (
        {
            "prior_q011bj_sealed_input_audit": prior,
            "q011bj": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011BJ_DIGEST_NAMES),
                "digests": list(digests),
                "scientific_outcome": artifact["scientific_outcome"],
                "actual_resonance_outcome": artifact["actual_resonance_outcome"],
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _degree_twenty_eight_inventory_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[tuple[str, ...], ...],
    tuple[q011u._MergedModulusInterval, ...],
    tuple[tuple[int, ...], ...],
    tuple[tuple[int, ...], ...],
    tuple[tuple[str, ...], ...],
]:
    u_cycle = artifacts["q011u"]["cycle"]
    stored_spectrum = u_cycle["exact_modulus_compression_audit"]
    reconstructed, selected_merged, external_merged = q011u._spectral_compression_audit(
        {"q011k": artifacts["q011k"]}
    )
    selected_groups = tuple(tuple(sorted(component.identifiers)) for component in selected_merged)
    degree_records = [
        record
        for record in u_cycle["degree_3_through_90_enumeration_audit"]["degree_records"]
        if record["degree"] == DEGREE
    ]
    degree_record = degree_records[0]
    log_audit = u_cycle["rational_log_enclosure_audit"]
    selected_logs = tuple(
        q011z._scaled_log_pair(record) for record in log_audit["selected_log_records"]
    )
    external_logs = tuple(
        q011z._scaled_log_pair(record) for record in log_audit["external_log_records"]
    )
    overlap_counts: list[tuple[int, ...]] = []
    external_indices: list[tuple[int, ...]] = []
    target_groups: list[tuple[str, ...]] = []
    overlap_records: list[dict[str, Any]] = []
    for counts in q011z._count_tuples(DEGREE):
        aggregate_lower = sum(
            count * interval[0] for count, interval in zip(counts, selected_logs, strict=True)
        )
        aggregate_upper = sum(
            count * interval[1] for count, interval in zip(counts, selected_logs, strict=True)
        )
        indices = tuple(
            index
            for index, (lower, upper) in enumerate(external_logs)
            if lower <= aggregate_upper and upper >= aggregate_lower
        )
        if not indices:
            continue
        identifiers = tuple(
            sorted(set().union(*(set(external_merged[index].identifiers) for index in indices)))
        )
        overlap_counts.append(counts)
        external_indices.append(indices)
        target_groups.append(identifiers)
        overlap_records.append(
            {
                "selected_type_counts": list(counts),
                "aggregate_log_interval": q011u._scaled_log_record(
                    q011u._ScaledLogInterval(aggregate_lower, aggregate_upper)
                ),
                "external_group_indices": list(indices),
                "external_log_intervals": [
                    q011u._scaled_log_record(q011u._ScaledLogInterval(*external_logs[index]))
                    for index in indices
                ],
            }
        )
    target_records = [
        {
            "aggregate_index": aggregate_index,
            "external_group_indices": list(indices),
            "identifiers": list(group),
        }
        for aggregate_index, (indices, group) in enumerate(
            zip(external_indices, target_groups, strict=True)
        )
    ]
    exact_inventory = {
        "selected_source_groups": [
            {"group_index": index, "identifiers": list(group)}
            for index, group in enumerate(selected_groups)
        ],
        "overlap_records": overlap_records,
        "external_target_groups": target_records,
    }
    unique_external = tuple(sorted({index for indices in external_indices for index in indices}))
    unique_targets = set().union(*map(set, target_groups))
    target_block_counts = tuple(
        Counter(q011z._identifier_indices(identifier)[0] for identifier in unique_targets)[block]
        for block in range(SIZE)
    )
    multi_target = [indices for indices in external_indices if len(indices) > 1]
    count_digest = q011b._canonical_json_sha256([list(counts) for counts in overlap_counts])
    external_digest = q011b._canonical_json_sha256([list(indices) for indices in external_indices])
    overlap_digest = q011b._canonical_json_sha256(overlap_records)
    target_digest = q011b._canonical_json_sha256(target_records)
    inventory_digest = q011b._canonical_json_sha256(exact_inventory)
    checks = {
        "q011u_modulus_spectrum_reconstructs_exactly": bool(
            reconstructed["passed"] and reconstructed == stored_spectrum
        ),
        "q011u_degree_twenty_eight_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
        ),
        "closed_form_count_tuple_total_reproduces": comb(DEGREE + 3, 3)
        == EXPECTED_DEGREE_AGGREGATE_COUNT,
        "registered_overlap_count_tuples_reproduce": bool(
            len(overlap_counts) == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and overlap_counts[0] == EXPECTED_FIRST_COUNTS
            and overlap_counts[-1] == EXPECTED_LAST_COUNTS
            and count_digest == EXPECTED_COUNT_TUPLE_DIGEST
        ),
        "external_components_and_targets_reproduce": bool(
            len(unique_external) == EXPECTED_UNIQUE_EXTERNAL_GROUP_COUNT
            and len(unique_targets) == EXPECTED_TARGET_IDENTIFIER_COUNT
            and len(multi_target) == EXPECTED_MULTI_TARGET_AGGREGATE_COUNT
            and max(map(len, external_indices)) == EXPECTED_MAXIMUM_EXTERNAL_COMPONENT_COUNT
            and external_digest == EXPECTED_EXTERNAL_GROUP_DIGEST
            and target_block_counts == EXPECTED_TARGET_BLOCK_COUNTS
        ),
        "selected_source_memberships_reproduce": tuple(map(len, selected_groups))
        == EXPECTED_SELECTED_GROUP_SIZES,
        "registered_inventory_digests_reproduce": bool(
            overlap_digest == EXPECTED_OVERLAP_RECORD_DIGEST
            and target_digest == EXPECTED_TARGET_RECORD_DIGEST
            and inventory_digest == EXPECTED_INVENTORY_DIGEST
        ),
        "selected_sources_and_external_targets_are_disjoint": not (
            set().union(*map(set, selected_groups)) & unique_targets
        ),
        "inventory_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(exact_inventory)
            and _strict_json_serializable(exact_inventory)
            and json.dumps(exact_inventory, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "degree_aggregate_count": degree_record["aggregate_count"],
        "degree_expanded_product_control_count": degree_record[
            "expanded_product_control_count"
        ],
        "old_modulus_separated_aggregate_count": degree_record["nonoverlap_count"],
        "old_modulus_overlap_aggregate_count": degree_record["overlap_count"],
        "selected_source_group_sizes": list(map(len, selected_groups)),
        "selected_source_group_memberships": [list(group) for group in selected_groups],
        "overlap_records": overlap_records,
        "external_target_groups": target_records,
        "unique_external_group_indices": list(unique_external),
        "unique_external_group_count": len(unique_external),
        "unique_external_target_count": len(unique_targets),
        "multi_target_external_component_aggregate_count": len(multi_target),
        "maximum_external_component_count": max(map(len, external_indices)),
        "target_identifier_block_counts": list(target_block_counts),
        "overlap_count_tuple_digest_sha256": count_digest,
        "external_group_index_tuple_digest_sha256": external_digest,
        "overlap_record_digest_sha256": overlap_digest,
        "external_target_record_digest_sha256": target_digest,
        "exact_inventory_digest_sha256": inventory_digest,
        "product_target_relation_evaluation_count": 0,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        selected_groups,
        external_merged,
        tuple(overlap_counts),
        tuple(external_indices),
        tuple(target_groups),
    )


def _degree_twenty_eight_envelope_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_merged: tuple[q011u._MergedModulusInterval, ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> tuple[
    dict[str, Any],
    tuple[tuple[tuple[str, ...], ...], ...],
    dict[str, q011z._UniformDisc],
]:
    base, lookup, classes = q011ap._degree_eighteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    coalescing, merged_classes, hull_lookup = q011as._coalesce_classes(classes, lookup)
    stored_coalescing = artifacts["q011as"]["cycle"][
        "degree_nineteen_coalescing_input_audit"
    ]["block_support_hull_coalescing_audit"]
    prior_records = artifacts["q011bi"]["cycle"]["degree_twenty_seven_envelope_audit"][
        "final_disc_records"
    ]
    active_records = base["final_disc_records"]
    prior_by_identifier = {record["identifier"]: record for record in prior_records}
    active_by_identifier = {record["identifier"]: record for record in active_records}
    common_identifiers = tuple(sorted(set(prior_by_identifier) & set(active_by_identifier)))
    added_identifiers = tuple(sorted(set(active_by_identifier) - set(prior_by_identifier)))
    inactive_identifiers = tuple(sorted(set(prior_by_identifier) - set(active_by_identifier)))
    common_records = [prior_by_identifier[identifier] for identifier in common_identifiers]
    added_records = [active_by_identifier[identifier] for identifier in added_identifiers]
    monotone_by_identifier = dict(prior_by_identifier)
    monotone_by_identifier.update(active_by_identifier)
    final_records = [
        monotone_by_identifier[identifier] for identifier in sorted(monotone_by_identifier)
    ]
    selected_identifiers = set().union(*map(set, selected_groups))
    target_identifiers = set().union(*map(set, target_groups))
    prior_digest = q011b._canonical_json_sha256(prior_records)
    common_digest = q011b._canonical_json_sha256(common_records)
    inactive_digest = q011b._canonical_json_sha256(list(inactive_identifiers))
    added_identifier_digest = q011b._canonical_json_sha256(list(added_identifiers))
    added_record_digest = q011b._canonical_json_sha256(added_records)
    active_digest = q011b._canonical_json_sha256(active_records)
    final_digest = q011b._canonical_json_sha256(final_records)
    target_lookup_unchanged = all(
        hull_lookup[identifier] == lookup[identifier] for identifier in target_identifiers
    )
    checks = {
        "generic_blockwise_envelope_primitives_reconstruct": bool(
            base["checks"]["q011k_centers_and_q011ak_block_radii_reconstruct"]
            and base["checks"]["all_two_hundred_four_q011ak_formulas_replay_exactly"]
            and base["checks"]["q011ao_reused_modulus_records_are_bitwise_identical"]
            and base["checks"]["selected_and_target_intervals_are_q011u_contained"]
            and base["checks"]["envelope_records_are_finite_strict_json"]
        ),
        "all_q011bi_records_are_retained_bitwise": bool(
            len(prior_records) == EXPECTED_PRIOR_IDENTIFIER_COUNT
            and prior_digest == EXPECTED_PRIOR_RECORD_DIGEST
            and len(common_identifiers) == EXPECTED_ACTIVE_REUSED_IDENTIFIER_COUNT
            and common_digest == EXPECTED_ACTIVE_REUSED_RECORD_DIGEST
            and all(
                prior_by_identifier[identifier] == active_by_identifier[identifier]
                for identifier in common_identifiers
            )
            and all(
                monotone_by_identifier[identifier] == prior_by_identifier[identifier]
                for identifier in prior_by_identifier
            )
        ),
        "inactive_prior_records_are_explicitly_retained": bool(
            len(inactive_identifiers) == EXPECTED_INACTIVE_RETAINED_IDENTIFIER_COUNT
            and inactive_digest == EXPECTED_INACTIVE_IDENTIFIER_DIGEST
            and all(identifier in monotone_by_identifier for identifier in inactive_identifiers)
        ),
        "registered_degree_twenty_eight_extension_reproduces": bool(
            len(added_identifiers) == EXPECTED_ADDED_TARGET_IDENTIFIER_COUNT
            and added_identifier_digest == EXPECTED_ADDED_IDENTIFIER_DIGEST
            and added_record_digest == EXPECTED_ADDED_RECORD_DIGEST
            and len(active_records) == EXPECTED_ACTIVE_IDENTIFIER_COUNT
            and active_digest == EXPECTED_ACTIVE_RECORD_DIGEST
            and len(final_records) == EXPECTED_FINAL_IDENTIFIER_COUNT
            and final_digest == EXPECTED_FINAL_RECORD_DIGEST
        ),
        "selected_and_current_target_partition_reproduces": bool(
            len(selected_identifiers) == 24
            and len(target_identifiers) == EXPECTED_TARGET_IDENTIFIER_COUNT
            and not (selected_identifiers & target_identifiers)
            and selected_identifiers | target_identifiers == set(active_by_identifier)
            and set(monotone_by_identifier) == set(prior_by_identifier) | set(active_by_identifier)
        ),
        "registered_source_hulls_and_memberships_reproduce": bool(
            tuple(map(len, classes)) == EXPECTED_OLD_CLASS_COUNTS
            and tuple(map(len, merged_classes)) == EXPECTED_MERGED_CLASS_COUNTS
            and coalescing["passed"]
            and coalescing["hull_record_digest_sha256"] == EXPECTED_HULL_RECORD_DIGEST
            and coalescing["merged_class_membership_digest_sha256"]
            == EXPECTED_MERGED_MEMBERSHIP_DIGEST
            and coalescing["hull_records"] == stored_coalescing["hull_records"]
            and coalescing["merged_class_memberships"]
            == stored_coalescing["merged_class_memberships"]
        ),
        "all_current_targets_are_preserved_without_folding": bool(
            target_lookup_unchanged and base["product_target_relation_evaluation_count"] == 0
        ),
        "envelope_audit_is_finite_strict_json": bool(
            _all_numeric_values_finite(final_records)
            and _strict_json_serializable(final_records)
            and json.dumps(final_records, allow_nan=False)
        ),
    }
    audit = {
        "selected_source_identifier_count": len(selected_identifiers),
        "external_target_identifier_count": len(target_identifiers),
        "prior_q011bi_identifier_count": len(prior_by_identifier),
        "active_reused_q011bi_identifier_count": len(common_identifiers),
        "inactive_retained_q011bi_identifier_count": len(inactive_identifiers),
        "added_target_identifier_count": len(added_identifiers),
        "removed_q011bi_identifier_count": 0,
        "active_identifier_count": len(active_records),
        "final_monotone_identifier_count": len(final_records),
        "inactive_retained_identifiers": list(inactive_identifiers),
        "added_target_identifiers": list(added_identifiers),
        "prior_record_digest_sha256": prior_digest,
        "active_reused_record_digest_sha256": common_digest,
        "inactive_retained_identifier_digest_sha256": inactive_digest,
        "added_target_identifier_digest_sha256": added_identifier_digest,
        "added_target_records": added_records,
        "added_target_record_digest_sha256": added_record_digest,
        "active_disc_records": active_records,
        "active_disc_record_digest_sha256": active_digest,
        "final_disc_records": final_records,
        "final_disc_record_digest_sha256": final_digest,
        "old_source_class_counts": list(map(len, classes)),
        "merged_source_class_counts": list(map(len, merged_classes)),
        "source_hull_record_digest_sha256": coalescing["hull_record_digest_sha256"],
        "source_merged_membership_digest_sha256": coalescing[
            "merged_class_membership_digest_sha256"
        ],
        "target_lookup_changed": not target_lookup_unchanged,
        "product_target_relation_evaluation_count": 0,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, merged_classes, hull_lookup


def _degree_twenty_eight_resource_audit(
    merged_classes: tuple[tuple[tuple[str, ...], ...], ...],
    selected_groups: tuple[tuple[str, ...], ...],
    overlap_counts: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    base = q011ap._degree_eighteen_resource_audit(
        merged_classes, selected_groups, overlap_counts, target_groups
    )
    record = {
        name: value
        for name, value in base.items()
        if name not in {"checks", "passed", "full_degree_eighteen_monomial_list_retained"}
    }
    record["full_degree_twenty_eight_monomial_list_retained"] = False
    projection = record["calibrated_projection"]
    checks = {
        "registered_class_power_keys_reproduce": bool(
            record["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and record["class_power_key_digest_sha256"] == EXPECTED_CLASS_POWER_KEY_DIGEST
        ),
        "registered_group_pool_keys_reproduce": bool(
            record["group_pool_cache_key_count"] == EXPECTED_GROUP_POOL_KEY_COUNT
            and record["group_pool_key_digest_sha256"] == EXPECTED_GROUP_POOL_KEY_DIGEST
            and record["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_COUNT
        ),
        "registered_pair_pool_resources_reproduce": bool(
            record["pair_pool_cache_key_count"] == EXPECTED_PAIR_POOL_KEY_COUNT
            and record["pair_pool_key_digest_sha256"] == EXPECTED_PAIR_POOL_KEY_DIGEST
            and record["cached_pair_signature_entry_count"]
            == EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT
        ),
        "registered_convolution_signature_and_memory_counts_reproduce": bool(
            record["exact_convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
            and record["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and record["peak_live_combined_signature_count"]
            == EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT
            and record["peak_two_product_bound_array_bytes"]
            == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
        ),
        "registered_monomial_and_comparison_upper_counts_reproduce": bool(
            record["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and record["maximum_aggregate_monomial_count"]
            == EXPECTED_MAXIMUM_AGGREGATE_MONOMIAL_COUNT
            and record["safe_int64_convolution_crude_upper_bound"]
            == EXPECTED_SAFE_INT64_CRUDE_BOUND
            and record["distinct_comparison_upper_bound"]
            == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
            and record["weighted_comparison_upper_bound"]
            == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
            and record["aggregate_resource_record_digest_sha256"]
            == EXPECTED_RESOURCE_RECORD_DIGEST
        ),
        "streaming_design_does_not_evaluate_degree_twenty_eight_relations": bool(
            not record["full_degree_twenty_eight_monomial_list_retained"]
            and not record["product_bound_matrix_constructed"]
            and not record["fourier_coefficient_matrix_constructed"]
            and not record["classification_matrix_constructed"]
            and record["product_target_relation_evaluation_count"] == 0
        ),
        "registered_variable_work_projection_reproduces": bool(
            projection["projected_wall_seconds"]
            == _fraction_record(EXPECTED_PROJECTED_SECONDS)
            and projection["wall_time_double_safety_upper_seconds"]
            == _fraction_record(EXPECTED_DOUBLE_SAFETY_SECONDS)
            and projection["tracemalloc_one_point_five_safety_upper_bytes"]
            == EXPECTED_TRACEMALLOC_SAFETY_BYTES
            and projection["process_memory_one_point_five_safety_upper_bytes"]
            == EXPECTED_PROCESS_MEMORY_SAFETY_BYTES
            and not projection["projection_is_a_scientific_acceptance_threshold"]
        ),
        "q011ap_absolute_resource_limits_are_preserved": RESOURCE_LIMITS
        == q011ap.RESOURCE_LIMITS
        == q011bi.RESOURCE_LIMITS,
        "integer_and_json_records_are_safe": bool(
            record["safe_int64_convolution_crude_upper_bound"] < 2**63
            and _all_numeric_values_finite(record)
            and _strict_json_serializable(record)
            and json.dumps(record, allow_nan=False)
        ),
    }
    return {**record, "checks": checks, "passed": all(checks.values())}


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "source_hull_semantics": "Q011as exact rational block-support hulls",
        "current_target_identifiers_merged_or_removed": False,
        "prior_disc_records_removed": False,
        "inactive_prior_disc_records_retained": EXPECTED_INACTIVE_RETAINED_IDENTIFIER_COUNT,
        "conjugate_target_folding_used": False,
        "degree_twenty_eight_relations_evaluated": False,
        "resource_limits": RESOURCE_LIMITS,
        "resource_limits_are_inherited_unchanged_from_q011ap": True,
        "go_decision": GO_DECISION,
        "stop_decision": STOP_DECISION,
        "degree_twenty_eight_external_nonresonance_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "inventory_digest_sha256": cycle["inventory_digest_sha256"],
        "envelope_digest_sha256": cycle["envelope_digest_sha256"],
        "resource_digest_sha256": cycle["resource_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "resource_feasibility_gates": cycle["resource_feasibility_gates"],
        "study_validity": cycle["study_validity"],
        "resource_decision": cycle["resource_decision"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_degree_twenty_eight_resource_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        _external_indices,
        target_groups,
    ) = _degree_twenty_eight_inventory_audit(artifacts)
    envelope, merged_classes, _ = _degree_twenty_eight_envelope_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    resource = _degree_twenty_eight_resource_audit(
        merged_classes, selected_groups, overlap_counts, target_groups
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    inventory_sections = {"degree_twenty_eight_inventory_audit": inventory}
    envelope_sections = {"degree_twenty_eight_envelope_audit": envelope}
    resource_sections = {"degree_twenty_eight_coalesced_resource_audit": resource}
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(inventory_sections)
    envelope_digest = q011b._canonical_json_sha256(envelope_sections)
    resource_digest = q011b._canonical_json_sha256(resource_sections)
    validity_gates = {
        "q011bj_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "41 artifacts and 198 direct digests reproduce",
            "value": sealed["checks"],
        },
        "degree_twenty_eight_inventory_reproduces": {
            "passed": inventory["passed"],
            "threshold": "4495 aggregates split as 3325 old plus 1170 overlap",
            "value": inventory["checks"],
        },
        "degree_twenty_eight_monotone_envelope_and_source_hulls_reproduce": {
            "passed": envelope["passed"],
            "threshold": "604 prior records retained, 124 added and six source hulls",
            "value": envelope["checks"],
        },
        "degree_twenty_eight_design_only_resource_contract_reproduces": {
            "passed": resource["passed"],
            "threshold": "registered exact combinatorial resources with zero relations",
            "value": resource["checks"],
        },
        "no_degree_twenty_eight_relation_object_is_constructed": {
            "passed": bool(
                inventory["product_target_relation_evaluation_count"] == 0
                and envelope["product_target_relation_evaluation_count"] == 0
                and resource["product_target_relation_evaluation_count"] == 0
                and not resource["product_bound_matrix_constructed"]
                and not resource["fourier_coefficient_matrix_constructed"]
                and not resource["classification_matrix_constructed"]
            ),
            "threshold": "relation evaluation count zero and all relation matrices absent",
            "value": 0,
        },
        "section_digests_runner_and_json_are_strict": {
            "passed": bool(
                len(input_digest)
                == len(inventory_digest)
                == len(envelope_digest)
                == len(resource_digest)
                == 64
                and runner["filename"] == "q011bk_degree28_resource_estimate.py"
                and _all_numeric_values_finite(resource)
                and _strict_json_serializable(resource)
            ),
            "threshold": "four section digests, runner provenance and strict finite JSON",
            "value": {
                "input": input_digest,
                "inventory": inventory_digest,
                "envelope": envelope_digest,
                "resource": resource_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    projection = resource["calibrated_projection"]
    resource_feasibility_gates = {
        "modulus_signature_limit": {
            "passed": resource["modulus_signature_count"]
            <= RESOURCE_LIMITS["modulus_signature_count"],
            "threshold": RESOURCE_LIMITS["modulus_signature_count"],
            "value": resource["modulus_signature_count"],
        },
        "peak_live_signature_limit": {
            "passed": resource["peak_live_combined_signature_count"]
            <= RESOURCE_LIMITS["peak_live_combined_signature_count"],
            "threshold": RESOURCE_LIMITS["peak_live_combined_signature_count"],
            "value": resource["peak_live_combined_signature_count"],
        },
        "two_product_array_limit": {
            "passed": resource["peak_two_product_bound_array_bytes"]
            <= RESOURCE_LIMITS["peak_two_product_bound_array_bytes"],
            "threshold": RESOURCE_LIMITS["peak_two_product_bound_array_bytes"],
            "value": resource["peak_two_product_bound_array_bytes"],
        },
        "exact_convolution_limit": {
            "passed": resource["exact_convolution_call_count"]
            <= RESOURCE_LIMITS["exact_convolution_call_count"],
            "threshold": RESOURCE_LIMITS["exact_convolution_call_count"],
            "value": resource["exact_convolution_call_count"],
        },
        "distinct_comparison_limit": {
            "passed": resource["distinct_comparison_upper_bound"]
            <= RESOURCE_LIMITS["distinct_comparison_upper_bound"],
            "threshold": RESOURCE_LIMITS["distinct_comparison_upper_bound"],
            "value": resource["distinct_comparison_upper_bound"],
        },
        "double_safety_wall_time_limit": {
            "passed": _record_fraction(projection["wall_time_double_safety_upper_seconds"])
            <= RESOURCE_LIMITS["wall_time_double_safety_upper_seconds"],
            "threshold": RESOURCE_LIMITS["wall_time_double_safety_upper_seconds"],
            "value": projection["wall_time_double_safety_upper_seconds"],
        },
        "process_memory_safety_limit": {
            "passed": projection["process_memory_one_point_five_safety_upper_bytes"]
            <= RESOURCE_LIMITS["process_memory_one_point_five_safety_upper_bytes"],
            "threshold": RESOURCE_LIMITS["process_memory_one_point_five_safety_upper_bytes"],
            "value": projection["process_memory_one_point_five_safety_upper_bytes"],
        },
    }
    feasible = all(gate["passed"] for gate in resource_feasibility_gates.values())
    decision = (
        GO_DECISION
        if validity_passed and feasible
        else STOP_DECISION
        if validity_passed
        else INCONCLUSIVE_DECISION
    )
    cycle = {
        "question": (
            "Can the degree-twenty-eight block-support-coalesced full sweep be "
            "preregistered within unchanged absolute resource limits without evaluating "
            "a relation?"
        ),
        **input_sections,
        **inventory_sections,
        **envelope_sections,
        **resource_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "inventory_digest_sha256": inventory_digest,
        "envelope_digest_sha256": envelope_digest,
        "resource_digest_sha256": resource_digest,
        "validity_gates": validity_gates,
        "resource_feasibility_gates": resource_feasibility_gates,
        "failed_validity_order": [
            name for name, gate in validity_gates.items() if not gate["passed"]
        ],
        "failed_resource_limit_order": [
            name for name, gate in resource_feasibility_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "resource_decision": decision,
        "scientific_outcome": SCIENTIFIC_OUTCOME,
        "actual_resonance_outcome": ACTUAL_RESONANCE_OUTCOME,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "degree_twenty_eight_coalesced_full_sweep_preregistration_is_resource_supported": decision
        == GO_DECISION,
        "degree_twenty_eight_external_nonresonance_is_certified": False,
        "an_actual_degree_twenty_eight_external_resonance_is_ruled_out": False,
        "certified_external_nonresonance_degrees": list(range(2, 28)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(28, 91)),
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011bj_degree_twenty_seven_certificate_is_preserved": True,
    }
    cycle["claim_boundary"] = (
        "This design-only audit concerns the degree-twenty-eight modulus-overlap "
        "inventory, six Q011as source hulls, all 612 current target discs, the "
        "728-record monotone proof inventory, exact combinatorial resource counts and "
        "calibrated projections for the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf. It evaluates no degree-twenty-eight product-target relation "
        "and certifies no degree-twenty-eight nonresonance, actual resonance, minimum "
        "gap, all-order result, higher smoothness, SSM existence or uniqueness, normal "
        "attraction, basin, other grid, forcing, wall or D3Q27 result."
    )
    cycle["next_change"] = (
        "Preregister the Q011bl degree-twenty-eight full sweep with fixed inputs, "
        "arithmetic and acceptance rules."
        if decision == GO_DECISION
        else "Redesign only the first failed degree-twenty-eight resource dimension "
        "before any degree-twenty-eight relation evaluation."
        if decision == STOP_DECISION
        else "Repair only the first Q011bk validity failure before changing the design."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011bk cycle failed strict serialization or digest")
    return cycle


def run_q011bk_study() -> dict[str, Any]:
    cycle = run_degree_twenty_eight_resource_audit()
    resource = cycle["degree_twenty_eight_coalesced_resource_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "inventory_arithmetic": "exact integer and rational-log interval arithmetic",
            "resource_arithmetic": "exact integer combinatorics and rational projections",
            "degree_twenty_eight_product_enclosure": "not constructed",
            "degree_twenty_eight_fourier_coefficient_matrices": "not constructed",
            "degree_twenty_eight_relation_classification": "not evaluated",
            "exact_convolution_call_count_if_full_sweep_runs": resource[
                "exact_convolution_call_count"
            ],
            "peak_live_signature_count_if_full_sweep_runs": resource[
                "peak_live_combined_signature_count"
            ],
        },
        "mathematical_scope": {
            "diagnostic": "design-only degree-28 block-support resource feasibility",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_twenty_eight_external_nonresonance_claim": False,
            "actual_degree_twenty_eight_external_resonance_ruled_out_claim": False,
            "all_order_nonresonance_claim": False,
            "ssm_existence_or_uniqueness_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "resource_decision": cycle["resource_decision"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011bk_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
