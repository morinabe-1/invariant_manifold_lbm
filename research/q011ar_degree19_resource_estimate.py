"""Q011ar design-only degree-nineteen hierarchical resource audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

import research.q011aq_degree18_hierarchical_sweep as q011aq
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ap = q011aq.q011ap
q011b = q011ap.q011b
q011u = q011ap.q011u
q011z = q011ap.q011z

SIZE = 17
DEGREE = 19

EXPECTED_DEGREE_AGGREGATE_COUNT = 1_540
EXPECTED_EXPANDED_CONTROL_COUNT = 42_504
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 1_255
EXPECTED_OVERLAP_AGGREGATE_COUNT = 285
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_UNIQUE_EXTERNAL_GROUP_COUNT = 17
EXPECTED_TARGET_IDENTIFIER_COUNT = 160
EXPECTED_MULTI_TARGET_AGGREGATE_COUNT = 8
EXPECTED_MAXIMUM_EXTERNAL_COMPONENT_COUNT = 2
EXPECTED_TARGET_BLOCK_COUNTS = (6, 8, 8, 6, 16, 19, 10, 6, 4, 4, 6, 10, 19, 16, 6, 8, 8)
EXPECTED_FIRST_COUNTS = (0, 2, 14, 3)
EXPECTED_LAST_COUNTS = (19, 0, 0, 0)
EXPECTED_COUNT_TUPLE_DIGEST = "a4bf39f39306cd8832546d1745488c0346170d44a6bc182d614cf36e6a465ff7"
EXPECTED_EXTERNAL_GROUP_DIGEST = "c0007260259ef5c77b3cbc0d707e4cbf1f35fc71ff2dd9d65f62f1e6d7a5639c"
EXPECTED_OVERLAP_RECORD_DIGEST = "b89ecea6ccca6aa3e7c5563ab258a0d3d1a8c57d28fd25df6bc578f6301a929b"
EXPECTED_TARGET_RECORD_DIGEST = "a234f6b0d6e02eb363a366839696b065a6977272c5c736bf0ff3e456bdaebf14"
EXPECTED_INVENTORY_DIGEST = "0a43e3e4ac5fc0683e85cfa88ee2bdc801643be23c8ededd20ea077d3f7c55b0"

NEW_TARGET_IDENTIFIERS = (
    "block=11;center=10",
    "block=11;center=9",
    "block=12;center=148",
    "block=12;center=149",
    "block=12;center=6",
    "block=12;center=7",
    "block=13;center=86",
    "block=13;center=87",
    "block=13;center=88",
    "block=13;center=89",
    "block=15;center=132",
    "block=15;center=133",
    "block=15;center=4",
    "block=15;center=5",
    "block=2;center=132",
    "block=2;center=133",
    "block=2;center=4",
    "block=2;center=5",
    "block=4;center=86",
    "block=4;center=87",
    "block=4;center=88",
    "block=4;center=89",
    "block=5;center=148",
    "block=5;center=149",
    "block=5;center=6",
    "block=5;center=7",
    "block=6;center=10",
    "block=6;center=9",
)
EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_REUSED_TARGET_IDENTIFIER_COUNT = 132
EXPECTED_REUSED_IDENTIFIER_COUNT = 156
EXPECTED_NEW_TARGET_IDENTIFIER_COUNT = 28
EXPECTED_FINAL_IDENTIFIER_COUNT = 184
EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST = (
    "67d7684d8ea1575255e4f7aa2e7798f141859df6d2433ce00bc08cebbc1e5473"
)
EXPECTED_NEW_TARGET_RECORD_DIGEST = (
    "56ee3a6f8a241a718a67849ed31059cb213c36ba5047972cb28d7d3a67c2ba75"
)
EXPECTED_FINAL_RECORD_DIGEST = "7e5cd881925e6e2c6a60a4124cabb7d844c4cd305d7be0a5ad10c2402e9abdd2"
EXPECTED_CLASS_MEMBERSHIP_DIGEST = (
    "269187f8489521c7e37ae8a91669b9dc020ac10d4ef1d42272bb636fa7bc9b8c"
)

EXPECTED_CLASS_POWER_COUNT = 276
EXPECTED_CLASS_POWER_KEY_DIGEST = (
    "b336dbfdc4ccc76a14145f6074a1bf08a1177bf563a52bd078e1ec350caaf452"
)
EXPECTED_GROUP_POOL_KEY_COUNT = 66
EXPECTED_GROUP_POOL_KEY_DIGEST = (
    "8749302ce7d5e76cf4f6e2080f18b8747c74c4c5c336d33fd4d163fb101dc1d1"
)
EXPECTED_PAIR_POOL_KEY_COUNT = 140
EXPECTED_PAIR_POOL_KEY_DIGEST = (
    "343b3ff58a70c485ce89830ff12f4a501ca8c122525f8a25b5bbe0e2531b0d68"
)
EXPECTED_GROUP_SIGNATURE_COUNT = 105_979
EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT = 1_646_172
EXPECTED_CONVOLUTION_CALL_COUNT = 2_270_568
EXPECTED_MODULUS_SIGNATURE_COUNT = 204_937_508
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 3_363_360
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 53_813_760
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 107_797_786_672
EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND = 1_974_912_192
EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND = 1_124_800_752_224
EXPECTED_RESOURCE_RECORD_DIGEST = (
    "97fd2f23c9b03f50071e9daec5dab48c9f1813a708ea878bd278cb417daf6642"
)
EXPECTED_MAXIMUM_AGGREGATE_MONOMIAL_COUNT = 2_038_608_000
EXPECTED_SAFE_INT64_CRUDE_BOUND = 34_656_336_000

EXPECTED_PROJECTED_SECONDS = Fraction(66_056_091_547_941, 72_180_980_000)
EXPECTED_DOUBLE_SAFETY_SECONDS = Fraction(66_056_091_547_941, 36_090_490_000)
EXPECTED_TRACEMALLOC_SAFETY_BYTES = 2_491_188_021
EXPECTED_PROCESS_MEMORY_SAFETY_BYTES = 6_875_052_442

# Preserve the Q011ap absolute limits; Q011ar must not relax them post hoc.
RESOURCE_LIMITS = dict(q011ap.RESOURCE_LIMITS)

GO_DECISION = "go_for_degree_nineteen_preregistration"
STOP_DECISION = "stop_before_degree_nineteen_full_sweep"
INCONCLUSIVE_DECISION = "inconclusive_resource_audit"
SCIENTIFIC_OUTCOME = "not_evaluated"
ACTUAL_RESONANCE_OUTCOME = "not_evaluated"

Q011AQ_ARTIFACT_SHA256 = "246540feb2733de13f7a5a982c609aaca6188982d927d6a2f82aa50cc35f157a"
Q011AQ_RUNNER_SHA256 = "358c89e86f8e6b5bb82cc47cafe553bee4549a197af57648b6e698e49d6dd52f"
Q011AQ_DIGEST_NAMES = (
    "input_digest_sha256",
    "preparation_digest_sha256",
    "sweep_digest_sha256",
    "result_digest_sha256",
)
Q011AQ_DIGESTS = (
    "b872654abf4e29b9c6d4fb40c6bf9e7ba5d1a05589f443b72a63bc37e338a501",
    "063d871e07ce95e0bd66219544e6406a0869074e18cd3ac8e6bbb44f65208d3c",
    "86ac41c9499150e6c9fa26a24924b7db71a48b8a05ade2f90c2d74ba83078d34",
    "0011b3f04770f7b2ff4528b2db9e2c71c3455dee9db23f378a3f699b78e697d4",
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
    prior, artifacts = q011aq._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011aq_degree18_hierarchical_sweep.json"
    runner_path = Path(q011aq.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AQ_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    checks = {
        "q011aq_twenty_one_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 108
            and len(artifacts) == 21
            and all(prior["checks"].values())
        ),
        "q011aq_artifact_sha256_matches": _file_sha256(artifact_path)
        == Q011AQ_ARTIFACT_SHA256,
        "q011aq_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AQ_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AQ_RUNNER_SHA256
        ),
        "q011aq_digests_match": digests == Q011AQ_DIGESTS,
        "q011aq_registered_acceptance_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and artifact["actual_resonance_outcome"]
            == q011aq.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
            and cycle["scientific_classification"] == q011aq.ACCEPTED_CLASSIFICATION
            and theorem["degree_eighteen_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 19))
            and theorem["missing_external_nonresonance_degrees"] == list(range(19, 91))
        ),
        "q011aq_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011aq_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011aq_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_hundred_twelve_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 112
        ),
    }
    artifacts["q011aq"] = artifact
    return (
        {
            "prior_q011aq_sealed_input_audit": prior,
            "q011aq": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AQ_DIGEST_NAMES),
                "digests": list(digests),
                "scientific_classification": cycle["scientific_classification"],
                "actual_resonance_outcome": artifact["actual_resonance_outcome"],
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _degree_nineteen_inventory_audit(
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
        "q011u_degree_nineteen_record_is_unique_and_complete": bool(
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


def _degree_nineteen_envelope_inventory_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_merged: tuple[q011u._MergedModulusInterval, ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    tuple[tuple[tuple[str, ...], ...], ...],
]:
    base, lookup, classes = q011ap._degree_eighteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    checks = {
        "q011k_centers_and_q011ak_block_radii_reconstruct": base["checks"][
            "q011k_centers_and_q011ak_block_radii_reconstruct"
        ],
        "all_two_hundred_four_q011ak_formulas_replay_exactly": base["checks"][
            "all_two_hundred_four_q011ak_formulas_replay_exactly"
        ],
        "registered_identifier_partition_reproduces": bool(
            base["selected_source_identifier_count"]
            == EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT
            and base["external_target_identifier_count"] == EXPECTED_TARGET_IDENTIFIER_COUNT
            and base["reused_q011ao_identifier_count"] == EXPECTED_REUSED_IDENTIFIER_COUNT
            and base["reused_q011ao_selected_identifier_count"]
            == EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT
            and base["reused_q011ao_target_identifier_count"]
            == EXPECTED_REUSED_TARGET_IDENTIFIER_COUNT
            and base["new_q011ak_target_identifier_count"]
            == EXPECTED_NEW_TARGET_IDENTIFIER_COUNT
            and base["final_identifier_count"] == EXPECTED_FINAL_IDENTIFIER_COUNT
        ),
        "q011ao_reused_modulus_records_are_bitwise_identical": base["checks"][
            "q011ao_reused_modulus_records_are_bitwise_identical"
        ],
        "registered_new_target_identifiers_reproduce": bool(
            tuple(base["new_q011ak_target_identifiers"]) == NEW_TARGET_IDENTIFIERS
            and base["new_target_identifier_digest_sha256"]
            == EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST
        ),
        "registered_extension_and_final_record_digests_reproduce": bool(
            base["new_q011ak_target_record_digest_sha256"]
            == EXPECTED_NEW_TARGET_RECORD_DIGEST
            and base["final_disc_record_digest_sha256"] == EXPECTED_FINAL_RECORD_DIGEST
        ),
        "selected_and_target_intervals_are_q011u_contained": base["checks"][
            "selected_and_target_intervals_are_q011u_contained"
        ],
        "selected_modulus_classes_reproduce": bool(
            tuple(base["selected_modulus_class_counts"]) == EXPECTED_CLASS_COUNTS
            and base["selected_class_membership_digest_sha256"]
            == EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "no_product_target_relation_is_evaluated": base["product_target_relation_evaluation_count"]
        == 0,
        "envelope_records_are_finite_strict_json": base["checks"][
            "envelope_records_are_finite_strict_json"
        ],
    }
    audit = {name: value for name, value in base.items() if name not in {"checks", "passed"}}
    audit["checks"] = checks
    audit["passed"] = all(checks.values())
    return audit, lookup, classes


def _fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "float": float(value),
    }


def _degree_nineteen_resource_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    selected_groups: tuple[tuple[str, ...], ...],
    overlap_counts: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    base = q011ap._degree_eighteen_resource_audit(
        classes, selected_groups, overlap_counts, target_groups
    )
    record = {
        name: value
        for name, value in base.items()
        if name not in {"checks", "passed", "full_degree_eighteen_monomial_list_retained"}
    }
    record["full_degree_nineteen_monomial_list_retained"] = False
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
            and record["distinct_comparison_upper_bound"]
            == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
            and record["weighted_comparison_upper_bound"]
            == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
            and record["aggregate_resource_record_digest_sha256"]
            == EXPECTED_RESOURCE_RECORD_DIGEST
        ),
        "closed_form_counts_and_int64_bound_are_safe": bool(
            record["maximum_aggregate_monomial_count"]
            == EXPECTED_MAXIMUM_AGGREGATE_MONOMIAL_COUNT
            and record["safe_int64_convolution_crude_upper_bound"]
            == EXPECTED_SAFE_INT64_CRUDE_BOUND
            and record["safe_int64_convolution_crude_upper_bound"] < 2**63
        ),
        "streaming_design_does_not_evaluate_relations_or_retain_full_expansions": bool(
            not record["full_degree_nineteen_monomial_list_retained"]
            and not record["product_bound_matrix_constructed"]
            and not record["fourier_coefficient_matrix_constructed"]
            and not record["classification_matrix_constructed"]
            and record["product_target_relation_evaluation_count"] == 0
        ),
        "calibrated_projection_is_exact_and_non_scientific": bool(
            record["q011ao_workload_ratios"]["peak_live_signature"]
            == _fraction_record(Fraction(14, 5))
            and projection["projected_wall_seconds"]
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
        == q011ap.RESOURCE_LIMITS,
        "resource_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(record)
            and _strict_json_serializable(record)
            and json.dumps(record, allow_nan=False)
        ),
    }
    return {**record, "checks": checks, "passed": all(checks.values())}


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "degree_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "direct_overlap_inventory_aggregate_count": EXPECTED_OVERLAP_AGGREGATE_COUNT,
        "selected_source_identifier_count": EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT,
        "external_target_identifier_count": EXPECTED_TARGET_IDENTIFIER_COUNT,
        "new_q011ak_target_identifier_count": EXPECTED_NEW_TARGET_IDENTIFIER_COUNT,
        "final_identifier_count": EXPECTED_FINAL_IDENTIFIER_COUNT,
        "selected_modulus_class_counts": list(EXPECTED_CLASS_COUNTS),
        "full_monomial_list_retained": False,
        "product_or_classification_matrices_constructed": False,
        "product_target_relations_evaluated": False,
        "resource_limits": RESOURCE_LIMITS,
        "resource_limits_are_inherited_unchanged_from_q011ap": True,
        "go_decision": GO_DECISION,
        "stop_decision": STOP_DECISION,
        "degree_nineteen_external_nonresonance_claimed": False,
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


def run_degree_nineteen_resource_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        _external_indices,
        target_groups,
    ) = _degree_nineteen_inventory_audit(artifacts)
    envelope, _lookup, classes = _degree_nineteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    resource = _degree_nineteen_resource_audit(
        classes, selected_groups, overlap_counts, target_groups
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    inventory_sections = {"degree_nineteen_inventory_audit": inventory}
    envelope_sections = {"degree_nineteen_envelope_inventory_audit": envelope}
    resource_sections = {"degree_nineteen_hierarchical_resource_audit": resource}
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(inventory_sections)
    envelope_digest = q011b._canonical_json_sha256(envelope_sections)
    resource_digest = q011b._canonical_json_sha256(resource_sections)
    validity_gates = {
        "q011aq_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "22 artifacts and 112 direct digests reproduce",
            "value": sealed["checks"],
        },
        "degree_nineteen_inventory_reproduces": {
            "passed": inventory["passed"],
            "threshold": "1540 aggregates partition into 1255 old and 285 overlap",
            "value": inventory["checks"],
        },
        "degree_nineteen_envelope_inventory_reproduces": {
            "passed": envelope["passed"],
            "threshold": "156 reused plus 28 extended identifiers form 184 safe discs",
            "value": envelope["checks"],
        },
        "deterministic_hierarchical_resource_contract_reproduces": {
            "passed": resource["passed"],
            "threshold": "registered exact counts, inherited limits and projections reproduce",
            "value": resource["checks"],
        },
        "strict_serialization_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(
                    len(digest) == 64
                    for digest in (input_digest, inventory_digest, envelope_digest, resource_digest)
                )
                and runner["filename"] == "q011ar_degree19_resource_estimate.py"
            ),
            "threshold": "strict finite JSON, four section digests and runner metadata",
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
        "modulus_signature_count_is_within_limit": {
            "passed": resource["modulus_signature_count"]
            <= RESOURCE_LIMITS["modulus_signature_count"],
            "threshold": RESOURCE_LIMITS["modulus_signature_count"],
            "value": resource["modulus_signature_count"],
        },
        "peak_live_signature_count_is_within_limit": {
            "passed": resource["peak_live_combined_signature_count"]
            <= RESOURCE_LIMITS["peak_live_combined_signature_count"],
            "threshold": RESOURCE_LIMITS["peak_live_combined_signature_count"],
            "value": resource["peak_live_combined_signature_count"],
        },
        "two_product_bound_arrays_are_within_limit": {
            "passed": resource["peak_two_product_bound_array_bytes"]
            <= RESOURCE_LIMITS["peak_two_product_bound_array_bytes"],
            "threshold": RESOURCE_LIMITS["peak_two_product_bound_array_bytes"],
            "value": resource["peak_two_product_bound_array_bytes"],
        },
        "exact_convolution_count_is_within_limit": {
            "passed": resource["exact_convolution_call_count"]
            <= RESOURCE_LIMITS["exact_convolution_call_count"],
            "threshold": RESOURCE_LIMITS["exact_convolution_call_count"],
            "value": resource["exact_convolution_call_count"],
        },
        "distinct_comparison_upper_bound_is_within_limit": {
            "passed": resource["distinct_comparison_upper_bound"]
            <= RESOURCE_LIMITS["distinct_comparison_upper_bound"],
            "threshold": RESOURCE_LIMITS["distinct_comparison_upper_bound"],
            "value": resource["distinct_comparison_upper_bound"],
        },
        "calibrated_double_wall_time_upper_is_within_limit": {
            "passed": projection["wall_time_double_safety_upper_seconds"]["float"]
            <= RESOURCE_LIMITS["wall_time_double_safety_upper_seconds"],
            "threshold": RESOURCE_LIMITS["wall_time_double_safety_upper_seconds"],
            "value": projection["wall_time_double_safety_upper_seconds"],
        },
        "calibrated_process_memory_upper_is_within_limit": {
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
            "Does the design-only degree-nineteen hierarchical workload fit every "
            "unchanged Q011ap resource limit without evaluating a spectral relation?"
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
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "degree_nineteen_full_sweep_preregistration_is_resource_supported": decision
        == GO_DECISION,
        "degree_nineteen_external_nonresonance_is_certified": False,
        "an_actual_degree_nineteen_external_resonance_is_ruled_out": False,
        "certified_external_nonresonance_degrees": list(range(2, 19)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(19, 91)),
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011aq_degree_eighteen_certificate_is_preserved": True,
    }
    cycle["claim_boundary"] = (
        "This design-only audit concerns the exact degree-nineteen modulus-overlap "
        "inventory, component-safe disc inventory, combinatorial streaming resource "
        "counts and calibrated resource projections for the fixed 17x17 repaired exact "
        "map on one fixed conservation leaf. It constructs no product-bound, Fourier "
        "coefficient or classification matrix and evaluates no product-target relation. "
        "It therefore certifies no degree-nineteen external nonresonance, actual resonance, "
        "minimum gap, higher graph smoothness, SSM uniqueness, attraction or basin."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011aq_degree_eighteen_certificate_changed": False,
        "certified_degrees_two_through_eighteen_changed": False,
        "degree_91_and_higher_tail_changed": False,
    }
    cycle["next_change"] = (
        "Preregister the Q011as degree-nineteen full component-safe hierarchical sweep "
        "before evaluating any degree-nineteen product-target relation."
        if decision == GO_DECISION
        else "Preregister a Q011as degree-nineteen resource redesign that preserves the "
        "disc and relation semantics before any degree-nineteen full sweep."
        if decision == STOP_DECISION
        else "Repair only the first Q011ar validity failure before changing the resource design."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ar cycle failed strict serialization or digest")
    return cycle


def run_q011ar_study() -> dict[str, Any]:
    cycle = run_degree_nineteen_resource_audit()
    resource = cycle["degree_nineteen_hierarchical_resource_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "inventory_arithmetic": "exact integer log-grid intervals",
            "resource_arithmetic": "exact integer combinatorics and rational projections",
            "source_multiplicity_arithmetic": "counted but not executed",
            "product_enclosure": "not constructed",
            "fourier_coefficient_matrices": "not constructed",
            "relation_classification": "not evaluated",
            "exact_convolution_call_count_if_full_sweep_runs": resource[
                "exact_convolution_call_count"
            ],
            "peak_live_signature_count_if_full_sweep_runs": resource[
                "peak_live_combined_signature_count"
            ],
        },
        "mathematical_scope": {
            "diagnostic": "design-only degree-19 hierarchical resource feasibility",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_nineteen_external_nonresonance_claim": False,
            "actual_degree_nineteen_external_resonance_ruled_out_claim": False,
            "degrees_19_through_90_claim": False,
            "all_order_nonresonance_claim": False,
            "ssm_uniqueness_claim": False,
            "normal_attraction_claim": False,
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
    result = run_q011ar_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
