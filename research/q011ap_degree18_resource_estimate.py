"""Q011ap design-only degree-eighteen hierarchical resource audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from math import ceil, comb
from math import prod as integer_product
from pathlib import Path
from typing import Any

import research.q011ao_degree17_hierarchical_sweep as q011ao
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011af = q011ao.q011af
q011ag = q011ao.q011ag
q011b = q011ao.q011b
q011u = q011ao.q011u
q011z = q011ao.q011z

SIZE = 17
DEGREE = 18

EXPECTED_DEGREE_AGGREGATE_COUNT = 1_330
EXPECTED_EXPANDED_CONTROL_COUNT = 33_649
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 1_078
EXPECTED_OVERLAP_AGGREGATE_COUNT = 252
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_UNIQUE_EXTERNAL_GROUP_COUNT = 18
EXPECTED_TARGET_IDENTIFIER_COUNT = 164
EXPECTED_MULTI_TARGET_AGGREGATE_COUNT = 4
EXPECTED_MAXIMUM_EXTERNAL_COMPONENT_COUNT = 2
EXPECTED_TARGET_BLOCK_COUNTS = (10, 8, 6, 8, 16, 17, 12, 6, 4, 4, 6, 12, 17, 16, 8, 6, 8)
EXPECTED_FIRST_COUNTS = (0, 0, 0, 18)
EXPECTED_LAST_COUNTS = (18, 0, 0, 0)
EXPECTED_COUNT_TUPLE_DIGEST = "ab1d05431038fd8e1331106f83beb3e26477f489b2e537dde3a29c28a4e99d1f"
EXPECTED_EXTERNAL_GROUP_DIGEST = "86cd7247a3db94d6be1e9fe49a9868415f3aae37b4e1e84af3a23691d51e9277"
EXPECTED_OVERLAP_RECORD_DIGEST = "68d98874e2268a2b32db780e7cc24e7fc604b2da97daf763d160a9cb3a0eef00"
EXPECTED_TARGET_RECORD_DIGEST = "e3b90982a4bac3b3617ed7c02cd04c2e7dcf8df62556d4cdbc222cb316879cbf"
EXPECTED_INVENTORY_DIGEST = "9f052dc63d04fab009e2bef1dca55c171294a808dc572d5e2348e95c3ed8b0f8"

NEW_TARGET_IDENTIFIERS = (
    "block=0;center=102",
    "block=0;center=103",
    "block=0;center=104",
    "block=0;center=105",
    "block=11;center=10",
    "block=11;center=110",
    "block=11;center=111",
    "block=11;center=9",
    "block=12;center=6",
    "block=12;center=7",
    "block=13;center=86",
    "block=13;center=87",
    "block=13;center=88",
    "block=13;center=89",
    "block=15;center=4",
    "block=15;center=5",
    "block=2;center=4",
    "block=2;center=5",
    "block=4;center=86",
    "block=4;center=87",
    "block=4;center=88",
    "block=4;center=89",
    "block=5;center=6",
    "block=5;center=7",
    "block=6;center=10",
    "block=6;center=110",
    "block=6;center=111",
    "block=6;center=9",
)
EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_REUSED_TARGET_IDENTIFIER_COUNT = 136
EXPECTED_REUSED_IDENTIFIER_COUNT = 160
EXPECTED_NEW_TARGET_IDENTIFIER_COUNT = 28
EXPECTED_FINAL_IDENTIFIER_COUNT = 188
EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST = (
    "fa8d902e6ef56d10f23ee96f3b887c27006363185dfcabac877912a2b2a0b64b"
)
EXPECTED_NEW_TARGET_RECORD_DIGEST = (
    "a4a3cd788af254ee03a594e539387916582b713d5f76ae738a60dcd7319ec7b8"
)
EXPECTED_FINAL_RECORD_DIGEST = "177bf6efc8f75a8a3fe4de1a08caf642aeb108fabd9ba325a7b1d1fdf31bea1b"
EXPECTED_CLASS_MEMBERSHIP_DIGEST = (
    "269187f8489521c7e37ae8a91669b9dc020ac10d4ef1d42272bb636fa7bc9b8c"
)

EXPECTED_CLASS_POWER_COUNT = 268
EXPECTED_CLASS_POWER_KEY_DIGEST = (
    "d279d6ae3ec1e2cfce1db59b02538ac3d53a9f630ae5dc24210745b35a101de2"
)
EXPECTED_GROUP_POOL_KEY_COUNT = 66
EXPECTED_GROUP_POOL_KEY_DIGEST = (
    "28f7bb6aff77e6ceb9f6612ac9564715bcb892d04ab2be3d69f64ebc34f73d65"
)
EXPECTED_PAIR_POOL_KEY_COUNT = 125
EXPECTED_PAIR_POOL_KEY_DIGEST = (
    "d2ef4192f7d6b50bf3433b4b5c70c721c6ccb0b30962129bdbc000446248219b"
)
EXPECTED_GROUP_SIGNATURE_COUNT = 139_922
EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT = 1_450_127
EXPECTED_CONVOLUTION_CALL_COUNT = 2_277_951
EXPECTED_MODULUS_SIGNATURE_COUNT = 112_289_821
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 2_102_100
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 33_633_600
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 50_931_347_136
EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND = 996_565_068
EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND = 485_076_664_408
EXPECTED_RESOURCE_RECORD_DIGEST = (
    "dc111aed9decab559e698958995121b4044980f4236f189bf47cf323bd8641fe"
)
EXPECTED_MAXIMUM_AGGREGATE_MONOMIAL_COUNT = 1_177_862_400
EXPECTED_SAFE_INT64_CRUDE_BOUND = 20_023_660_800

Q011AO_BASELINE_CONVOLUTION_COUNT = 1_339_913
Q011AO_BASELINE_MODULUS_SIGNATURE_COUNT = 55_452_003
Q011AO_BASELINE_PEAK_SIGNATURE_COUNT = 1_201_200
Q011AO_BASELINE_DISTINCT_COMPARISON_UPPER_BOUND = 461_958_272
Q011AO_BASELINE_WEIGHTED_COMPARISON_UPPER_BOUND = 177_384_288_880
Q011AO_BASELINE_PILOT_SECONDS = Fraction(2_140_647, 10_000)
Q011AO_BASELINE_TRACEMALLOC_PEAK_BYTES = 593_140_005
Q011AO_BASELINE_PROCESS_PEAK_WORKING_SET_BYTES = 1_636_917_248

RESOURCE_LIMITS = {
    "modulus_signature_count": 125_000_000,
    "peak_live_combined_signature_count": 2_500_000,
    "peak_two_product_bound_array_bytes": 41_943_040,
    "exact_convolution_call_count": 2_500_000,
    "distinct_comparison_upper_bound": 1_100_000_000,
    "wall_time_double_safety_upper_seconds": 1_200,
    "process_memory_one_point_five_safety_upper_bytes": 6_442_450_944,
}

GO_DECISION = "go_for_degree_eighteen_preregistration"
STOP_DECISION = "stop_before_degree_eighteen_full_sweep"
INCONCLUSIVE_DECISION = "inconclusive_resource_audit"
SCIENTIFIC_OUTCOME = "not_evaluated"
ACTUAL_RESONANCE_OUTCOME = "not_evaluated"

Q011AO_ARTIFACT_SHA256 = "7b439a9d4634f895a0cbd98660da7147237f6cc026531e700597bab04f8fc81a"
Q011AO_RUNNER_SHA256 = "0fbf8f9bad5217ff0a61d0b76255d283d2845816321207382d35fc69d3753cc1"
Q011AO_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "envelope_digest_sha256",
    "sweep_digest_sha256",
    "result_digest_sha256",
)
Q011AO_DIGESTS = (
    "8a893e802bc4b93cd2f9be5da7e872b5a79a2e956a1b445386a63cd97aed9aad",
    "4806963b4e1cc0ace653881e6102dd055220b95d9d5157f1a4699f71cd85f02c",
    "8eebcf226ffb9ad38d0d14f2ae42c4b89cea37c553a1b88d72dfc1ce6a4c5f50",
    "e046e2d7675155aba98b97266dda283e4cfd3b3a22698a7e6edbad6e2dcfa9a8",
    "f76db860a63b31c3152ddbe8ef6ce1ea6ee58e2d62b3554895bce4a25834b746",
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
    prior, artifacts = q011ao._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ao_degree17_hierarchical_sweep.json"
    runner_path = Path(q011ao.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AO_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    checks = {
        "q011ao_nineteen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 98
            and len(artifacts) == 19
            and all(prior["checks"].values())
        ),
        "q011ao_artifact_sha256_matches": _file_sha256(artifact_path) == Q011AO_ARTIFACT_SHA256,
        "q011ao_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AO_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AO_RUNNER_SHA256
        ),
        "q011ao_digests_match": digests == Q011AO_DIGESTS,
        "q011ao_registered_acceptance_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and artifact["actual_resonance_outcome"] == q011ao.ACTUAL_RESONANCE_OUTCOME
            and cycle["scientific_classification"] == q011ao.ACCEPTED_CLASSIFICATION
            and theorem["degree_seventeen_external_nonresonance_is_certified"]
            and theorem["missing_external_nonresonance_degrees"] == list(range(18, 91))
        ),
        "q011ao_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ao_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ao_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_hundred_three_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 103
        ),
    }
    artifacts["q011ao"] = artifact
    return (
        {
            "prior_q011ao_sealed_input_audit": prior,
            "q011ao": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AO_DIGEST_NAMES),
                "digests": list(digests),
                "scientific_classification": cycle["scientific_classification"],
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _degree_eighteen_inventory_audit(
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
        "q011u_degree_eighteen_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"] == EXPECTED_EXPANDED_CONTROL_COUNT
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
        "degree_expanded_product_control_count": degree_record["expanded_product_control_count"],
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


def _degree_eighteen_envelope_inventory_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_merged: tuple[q011u._MergedModulusInterval, ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    tuple[tuple[tuple[str, ...], ...], ...],
]:
    centers, _, _, _, reconstruction = q011z.q011l._spectral_data(artifacts["q011k"])
    q011ak_records = artifacts["q011ak"]["cycle"][
        "blockwise_transformed_residual_envelope_audit"
    ]["blockwise_disc_records"]
    q011ao_records = {
        record["identifier"]: record
        for record in artifacts["q011ao"]["cycle"][
            "degree_seventeen_component_safe_envelope_audit"
        ]["final_disc_records"]
    }
    radius_by_block: dict[int, Fraction] = {}
    radii_consistent = True
    for record in q011ak_records:
        block = record["block_index"]
        radius = q011z._fraction(record["transformed_residual_radius_upper"])
        if block in radius_by_block and radius_by_block[block] != radius:
            radii_consistent = False
        radius_by_block[block] = radius
    center_cache: dict[tuple[int, int], RationalInterval] = {}

    def center_modulus(identifier: str) -> RationalInterval:
        block, center_index = q011z._identifier_indices(identifier)
        key = (block, center_index)
        if key not in center_cache:
            center_cache[key] = q011u.q011o._center_modulus_bounds(centers[block][center_index])
        return center_cache[key]

    replay_records = []
    q011ak_replay = bool(reconstruction["passed"] and radii_consistent)
    for record in q011ak_records:
        identifier = record["identifier"]
        block = record["block_index"]
        center = center_modulus(identifier)
        radius = radius_by_block[block]
        lower = max(Fraction(0), center.lower - radius)
        upper = center.upper + radius
        q011ak_replay = bool(
            q011ak_replay
            and center.lower == q011z._fraction(record["center_modulus_lower"])
            and center.upper == q011z._fraction(record["center_modulus_upper"])
            and lower == q011z._fraction(record["blockwise_modulus_lower"])
            and upper == q011z._fraction(record["blockwise_modulus_upper"])
        )
        replay_records.append(
            {
                "identifier": identifier,
                "modulus_lower": q011z._exact_fraction_record(lower),
                "modulus_upper": q011z._exact_fraction_record(upper),
            }
        )

    selected_identifiers = set().union(*map(set, selected_groups))
    target_identifiers = set().union(*map(set, target_groups))
    needed = selected_identifiers | target_identifiers
    reused = needed & set(q011ao_records)
    new_identifiers = tuple(sorted(needed - set(q011ao_records)))
    lookup: dict[str, q011z._UniformDisc] = {}
    new_records = []
    final_records = []
    reused_moduli_match = True
    for identifier in sorted(needed):
        block, center_index = q011z._identifier_indices(identifier)
        center = center_modulus(identifier)
        if identifier in q011ao_records:
            source = q011ao_records[identifier]
            modulus = RationalInterval(
                q011z._fraction(source["modulus_lower"]),
                q011z._fraction(source["modulus_upper"]),
            )
            radius_kind = "q011ao_reused"
            reused_moduli_match = bool(
                reused_moduli_match
                and q011z._exact_fraction_record(modulus.lower) == source["modulus_lower"]
                and q011z._exact_fraction_record(modulus.upper) == source["modulus_upper"]
            )
        else:
            radius = radius_by_block[block]
            modulus = RationalInterval(
                max(Fraction(0), center.lower - radius), center.upper + radius
            )
            radius_kind = "q011ak_blockwise_extension"
            new_records.append(
                {
                    "identifier": identifier,
                    "block_index": block,
                    "center_index": center_index,
                    "blockwise_radius_upper": q011z._exact_fraction_record(radius),
                    "modulus_lower": q011z._exact_fraction_record(modulus.lower),
                    "modulus_upper": q011z._exact_fraction_record(modulus.upper),
                }
            )
        lookup[identifier] = q011z._UniformDisc(
            identifier=identifier,
            block_index=block,
            center_index=center_index,
            center_modulus=center,
            modulus=modulus,
        )
        final_records.append(
            {
                "identifier": identifier,
                "block_index": block,
                "center_index": center_index,
                "radius_kind": radius_kind,
                "modulus_lower": q011z._exact_fraction_record(modulus.lower),
                "modulus_upper": q011z._exact_fraction_record(modulus.upper),
            }
        )

    selected_owner = {
        identifier: component
        for component in q011u._spectral_compression_audit({"q011k": artifacts["q011k"]})[1]
        for identifier in component.identifiers
    }
    external_owner = {
        identifier: component for component in external_merged for identifier in component.identifiers
    }
    selected_containment = all(
        lookup[identifier].modulus.lower >= selected_owner[identifier].lower
        and lookup[identifier].modulus.upper <= selected_owner[identifier].upper
        for identifier in selected_identifiers
    )
    target_containment = all(
        lookup[identifier].modulus.lower >= external_owner[identifier].lower
        and lookup[identifier].modulus.upper <= external_owner[identifier].upper
        for identifier in target_identifiers
    )
    classes, class_records = q011ag._modulus_classes(selected_groups, lookup)
    new_identifier_digest = q011b._canonical_json_sha256(list(new_identifiers))
    new_record_digest = q011b._canonical_json_sha256(new_records)
    final_record_digest = q011b._canonical_json_sha256(final_records)
    class_digest = q011b._canonical_json_sha256(class_records)
    checks = {
        "q011k_centers_and_q011ak_block_radii_reconstruct": bool(
            reconstruction["passed"]
            and radii_consistent
            and set(radius_by_block) == set(range(SIZE))
        ),
        "all_two_hundred_four_q011ak_formulas_replay_exactly": bool(
            q011ak_replay and len(replay_records) == 204
        ),
        "registered_identifier_partition_reproduces": bool(
            not (selected_identifiers & target_identifiers)
            and len(selected_identifiers) == EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT
            and len(target_identifiers) == EXPECTED_TARGET_IDENTIFIER_COUNT
            and len(reused) == EXPECTED_REUSED_IDENTIFIER_COUNT
            and len(selected_identifiers & reused) == EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT
            and len(target_identifiers & reused) == EXPECTED_REUSED_TARGET_IDENTIFIER_COUNT
            and len(new_identifiers) == EXPECTED_NEW_TARGET_IDENTIFIER_COUNT
            and len(needed) == EXPECTED_FINAL_IDENTIFIER_COUNT
        ),
        "q011ao_reused_modulus_records_are_bitwise_identical": reused_moduli_match,
        "registered_new_target_identifiers_reproduce": bool(
            new_identifiers == NEW_TARGET_IDENTIFIERS
            and new_identifier_digest == EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST
        ),
        "registered_extension_and_final_record_digests_reproduce": bool(
            new_record_digest == EXPECTED_NEW_TARGET_RECORD_DIGEST
            and final_record_digest == EXPECTED_FINAL_RECORD_DIGEST
        ),
        "selected_and_target_intervals_are_q011u_contained": bool(
            selected_containment and target_containment
        ),
        "selected_modulus_classes_reproduce": bool(
            tuple(map(len, classes)) == EXPECTED_CLASS_COUNTS
            and class_digest == EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "no_product_target_relation_is_evaluated": True,
        "envelope_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(final_records)
            and _strict_json_serializable(final_records)
            and json.dumps(final_records, allow_nan=False)
        ),
    }
    audit = {
        "selected_source_identifier_count": len(selected_identifiers),
        "external_target_identifier_count": len(target_identifiers),
        "reused_q011ao_identifier_count": len(reused),
        "reused_q011ao_selected_identifier_count": len(selected_identifiers & reused),
        "reused_q011ao_target_identifier_count": len(target_identifiers & reused),
        "new_q011ak_target_identifier_count": len(new_identifiers),
        "final_identifier_count": len(needed),
        "new_q011ak_target_identifiers": list(new_identifiers),
        "new_target_identifier_digest_sha256": new_identifier_digest,
        "new_q011ak_target_records": new_records,
        "new_q011ak_target_record_digest_sha256": new_record_digest,
        "final_disc_records": final_records,
        "final_disc_record_digest_sha256": final_record_digest,
        "q011ak_formula_replay_record_count": len(replay_records),
        "q011ak_formula_replay_digest_sha256": q011b._canonical_json_sha256(replay_records),
        "selected_modulus_class_counts": list(map(len, classes)),
        "selected_class_membership_digest_sha256": class_digest,
        "product_target_relation_evaluation_count": 0,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup, classes


def _fraction_record(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "float": float(value),
    }


def _degree_eighteen_resource_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    selected_groups: tuple[tuple[str, ...], ...],
    overlap_counts: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    class_sizes = tuple(map(len, classes))

    def pool_size(group_index: int, count: int) -> int:
        return comb(count + class_sizes[group_index] - 1, class_sizes[group_index] - 1)

    group_keys = {
        (group_index, counts[group_index])
        for counts in overlap_counts
        for group_index in range(4)
    }
    left_keys = {(counts[0], counts[1]) for counts in overlap_counts}
    right_keys = {(counts[2], counts[3]) for counts in overlap_counts}
    signature_counts = [
        integer_product(pool_size(group_index, counts[group_index]) for group_index in range(4))
        for counts in overlap_counts
    ]
    original_counts = [
        integer_product(
            comb(counts[group_index] + len(selected_groups[group_index]) - 1, counts[group_index])
            for group_index in range(4)
        )
        for counts in overlap_counts
    ]
    resource_records = [
        {
            "aggregate_index": aggregate_index,
            "selected_type_counts": list(counts),
            "target_identifier_count": len(target_group),
            "modulus_signature_count": signatures,
            "original_monomial_count": monomials,
            "distinct_comparison_upper_bound": signatures * len(target_group),
            "weighted_comparison_upper_bound": monomials * len(target_group),
        }
        for aggregate_index, (counts, target_group, signatures, monomials) in enumerate(
            zip(overlap_counts, target_groups, signature_counts, original_counts, strict=True)
        )
    ]
    group_signature_count = sum(pool_size(group, count) for group, count in group_keys)
    pair_signature_entry_count = sum(
        pool_size(0, left) * pool_size(1, right) for left, right in left_keys
    ) + sum(pool_size(2, left) * pool_size(3, right) for left, right in right_keys)
    convolution_call_count = (
        sum(class_sizes[group] * pool_size(group, count) for group, count in group_keys)
        + pair_signature_entry_count
    )
    power_keys = set()
    for group, count in group_keys:
        for allocation in q011af._weak_compositions(count, class_sizes[group]):
            for class_index, class_count in enumerate(allocation):
                power_keys.add((group, class_index, class_count))
    peak_signatures = max(signature_counts)
    maximum_aggregate_monomials = max(original_counts)
    safe_int64_crude_bound = SIZE * maximum_aggregate_monomials
    class_power_digest = q011b._canonical_json_sha256(
        [list(key) for key in sorted(power_keys)]
    )
    group_key_digest = q011b._canonical_json_sha256(
        [list(key) for key in sorted(group_keys)]
    )
    pair_key_digest = q011b._canonical_json_sha256(
        {
            "left": [list(key) for key in sorted(left_keys)],
            "right": [list(key) for key in sorted(right_keys)],
        }
    )
    resource_record_digest = q011b._canonical_json_sha256(resource_records)

    distinct_upper = sum(record["distinct_comparison_upper_bound"] for record in resource_records)
    weighted_upper = sum(record["weighted_comparison_upper_bound"] for record in resource_records)
    convolution_ratio = Fraction(convolution_call_count, Q011AO_BASELINE_CONVOLUTION_COUNT)
    signature_ratio = Fraction(sum(signature_counts), Q011AO_BASELINE_MODULUS_SIGNATURE_COUNT)
    peak_ratio = Fraction(peak_signatures, Q011AO_BASELINE_PEAK_SIGNATURE_COUNT)
    distinct_ratio = Fraction(distinct_upper, Q011AO_BASELINE_DISTINCT_COMPARISON_UPPER_BOUND)
    weighted_ratio = Fraction(weighted_upper, Q011AO_BASELINE_WEIGHTED_COMPARISON_UPPER_BOUND)
    projected_seconds = Q011AO_BASELINE_PILOT_SECONDS * distinct_ratio
    double_safety_seconds = 2 * projected_seconds
    projected_tracemalloc = Fraction(Q011AO_BASELINE_TRACEMALLOC_PEAK_BYTES) * peak_ratio
    tracemalloc_safety = Fraction(3, 2) * projected_tracemalloc
    projected_process_memory = (
        Fraction(Q011AO_BASELINE_PROCESS_PEAK_WORKING_SET_BYTES) * peak_ratio
    )
    process_memory_safety = Fraction(3, 2) * projected_process_memory

    record = {
        "class_power_record_count": len(power_keys),
        "class_power_key_digest_sha256": class_power_digest,
        "group_pool_cache_key_count": len(group_keys),
        "group_pool_key_digest_sha256": group_key_digest,
        "group_signature_record_count": group_signature_count,
        "pair_pool_cache_key_count": len(left_keys) + len(right_keys),
        "pair_pool_key_digest_sha256": pair_key_digest,
        "cached_pair_signature_entry_count": pair_signature_entry_count,
        "exact_convolution_call_count": convolution_call_count,
        "modulus_signature_count": sum(signature_counts),
        "peak_live_combined_signature_count": peak_signatures,
        "peak_two_product_bound_array_bytes": 2 * 8 * peak_signatures,
        "original_monomial_count": sum(original_counts),
        "maximum_aggregate_monomial_count": maximum_aggregate_monomials,
        "safe_int64_convolution_crude_upper_bound": safe_int64_crude_bound,
        "distinct_comparison_upper_bound": distinct_upper,
        "weighted_comparison_upper_bound": weighted_upper,
        "aggregate_resource_records": resource_records,
        "aggregate_resource_record_digest_sha256": resource_record_digest,
        "q011ao_workload_ratios": {
            "convolution": _fraction_record(convolution_ratio),
            "modulus_signature": _fraction_record(signature_ratio),
            "peak_live_signature": _fraction_record(peak_ratio),
            "distinct_comparison_upper_bound": _fraction_record(distinct_ratio),
            "weighted_comparison_upper_bound": _fraction_record(weighted_ratio),
        },
        "calibrated_projection": {
            "q011ao_design_only_pilot_seconds": _fraction_record(Q011AO_BASELINE_PILOT_SECONDS),
            "projected_wall_seconds": _fraction_record(projected_seconds),
            "wall_time_double_safety_upper_seconds": _fraction_record(double_safety_seconds),
            "projected_tracemalloc_peak_bytes": _fraction_record(projected_tracemalloc),
            "tracemalloc_one_point_five_safety_upper_bytes": ceil(tracemalloc_safety),
            "projected_process_peak_working_set_bytes": _fraction_record(
                projected_process_memory
            ),
            "process_memory_one_point_five_safety_upper_bytes": ceil(process_memory_safety),
            "wall_time_projection_driver": "distinct comparison upper-bound ratio",
            "memory_projection_driver": "peak live signature ratio",
            "projection_is_a_scientific_acceptance_threshold": False,
        },
        "full_degree_eighteen_monomial_list_retained": False,
        "product_bound_matrix_constructed": False,
        "fourier_coefficient_matrix_constructed": False,
        "classification_matrix_constructed": False,
        "product_target_relation_evaluation_count": 0,
    }
    checks = {
        "registered_class_power_keys_reproduce": bool(
            len(power_keys) == EXPECTED_CLASS_POWER_COUNT
            and class_power_digest == EXPECTED_CLASS_POWER_KEY_DIGEST
        ),
        "registered_group_pool_keys_reproduce": bool(
            len(group_keys) == EXPECTED_GROUP_POOL_KEY_COUNT
            and group_key_digest == EXPECTED_GROUP_POOL_KEY_DIGEST
            and group_signature_count == EXPECTED_GROUP_SIGNATURE_COUNT
        ),
        "registered_pair_pool_resources_reproduce": bool(
            len(left_keys) + len(right_keys) == EXPECTED_PAIR_POOL_KEY_COUNT
            and pair_key_digest == EXPECTED_PAIR_POOL_KEY_DIGEST
            and pair_signature_entry_count == EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT
        ),
        "registered_convolution_signature_and_memory_counts_reproduce": bool(
            convolution_call_count == EXPECTED_CONVOLUTION_CALL_COUNT
            and sum(signature_counts) == EXPECTED_MODULUS_SIGNATURE_COUNT
            and peak_signatures == EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT
            and record["peak_two_product_bound_array_bytes"]
            == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
        ),
        "registered_monomial_and_comparison_upper_counts_reproduce": bool(
            sum(original_counts) == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and distinct_upper == EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND
            and weighted_upper == EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND
            and resource_record_digest == EXPECTED_RESOURCE_RECORD_DIGEST
        ),
        "closed_form_counts_and_int64_bound_are_safe": bool(
            maximum_aggregate_monomials == EXPECTED_MAXIMUM_AGGREGATE_MONOMIAL_COUNT
            and safe_int64_crude_bound == EXPECTED_SAFE_INT64_CRUDE_BOUND
            and safe_int64_crude_bound < 2**63
        ),
        "streaming_design_does_not_evaluate_relations_or_retain_full_expansions": bool(
            not record["full_degree_eighteen_monomial_list_retained"]
            and not record["product_bound_matrix_constructed"]
            and not record["fourier_coefficient_matrix_constructed"]
            and not record["classification_matrix_constructed"]
            and record["product_target_relation_evaluation_count"] == 0
        ),
        "calibrated_projection_is_exact_and_non_scientific": bool(
            peak_ratio == Fraction(7, 4)
            and ceil(tracemalloc_safety) == 1_556_992_514
            and ceil(process_memory_safety) == 4_296_907_776
            and not record["calibrated_projection"][
                "projection_is_a_scientific_acceptance_threshold"
            ]
        ),
        "resource_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(record)
            and _strict_json_serializable(record)
            and json.dumps(record, allow_nan=False)
        ),
    }
    return {
        **record,
        "checks": checks,
        "passed": all(checks.values()),
    }


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
        "go_decision": GO_DECISION,
        "stop_decision": STOP_DECISION,
        "degree_eighteen_external_nonresonance_claimed": False,
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


def run_degree_eighteen_resource_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        _external_indices,
        target_groups,
    ) = _degree_eighteen_inventory_audit(artifacts)
    envelope, _lookup, classes = _degree_eighteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    resource = _degree_eighteen_resource_audit(
        classes, selected_groups, overlap_counts, target_groups
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    inventory_sections = {"degree_eighteen_inventory_audit": inventory}
    envelope_sections = {"degree_eighteen_envelope_inventory_audit": envelope}
    resource_sections = {"degree_eighteen_hierarchical_resource_audit": resource}
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(inventory_sections)
    envelope_digest = q011b._canonical_json_sha256(envelope_sections)
    resource_digest = q011b._canonical_json_sha256(resource_sections)
    validity_gates = {
        "q011ao_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "20 artifacts and 103 direct digests reproduce",
            "value": sealed["checks"],
        },
        "degree_eighteen_inventory_reproduces": {
            "passed": inventory["passed"],
            "threshold": "1330 aggregates partition into 1078 old and 252 overlap",
            "value": inventory["checks"],
        },
        "degree_eighteen_envelope_inventory_reproduces": {
            "passed": envelope["passed"],
            "threshold": "160 reused plus 28 extended identifiers form 188 safe discs",
            "value": envelope["checks"],
        },
        "deterministic_hierarchical_resource_contract_reproduces": {
            "passed": resource["passed"],
            "threshold": "registered exact counts, bounds and projections reproduce",
            "value": resource["checks"],
        },
        "strict_serialization_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(
                    len(digest) == 64
                    for digest in (input_digest, inventory_digest, envelope_digest, resource_digest)
                )
                and runner["filename"] == "q011ap_degree18_resource_estimate.py"
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
            "Does the design-only degree-eighteen hierarchical workload fit every "
            "preregistered resource limit without evaluating a spectral relation?"
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
        "degree_eighteen_full_sweep_preregistration_is_resource_supported": decision
        == GO_DECISION,
        "degree_eighteen_external_nonresonance_is_certified": False,
        "an_actual_degree_eighteen_external_resonance_is_ruled_out": False,
        "certified_external_nonresonance_degrees": list(range(2, 18)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(18, 91)),
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011ao_degree_seventeen_certificate_is_preserved": True,
    }
    cycle["claim_boundary"] = (
        "This design-only audit concerns the exact degree-eighteen modulus-overlap "
        "inventory, component-safe disc inventory, combinatorial streaming resource "
        "counts and calibrated resource projections for the fixed 17x17 repaired exact "
        "map on one fixed conservation leaf. It constructs no product-bound, Fourier "
        "coefficient or classification matrix and evaluates no product-target relation. "
        "It therefore certifies no degree-eighteen external nonresonance, actual resonance, "
        "minimum gap, higher graph smoothness, SSM uniqueness, attraction or basin."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011ao_degree_seventeen_certificate_changed": False,
        "certified_degrees_two_through_seventeen_changed": False,
        "degree_91_and_higher_tail_changed": False,
    }
    cycle["next_change"] = (
        "Preregister the Q011aq degree-eighteen full component-safe hierarchical sweep "
        "before evaluating any degree-eighteen product-target relation."
        if decision == GO_DECISION
        else "Redesign the hierarchical resource representation before any degree-eighteen sweep."
        if decision == STOP_DECISION
        else "Repair only the first Q011ap validity failure before changing the resource design."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ap cycle failed strict serialization or digest")
    return cycle


def run_q011ap_study() -> dict[str, Any]:
    cycle = run_degree_eighteen_resource_audit()
    resource = cycle["degree_eighteen_hierarchical_resource_audit"]
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
            "diagnostic": "design-only degree-18 hierarchical resource feasibility",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_eighteen_external_nonresonance_claim": False,
            "actual_degree_eighteen_external_resonance_ruled_out_claim": False,
            "degrees_18_through_90_claim": False,
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
    result = run_q011ap_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
