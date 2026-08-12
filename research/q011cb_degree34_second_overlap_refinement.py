"""Q011cb blockwise refinement of the second Q011bx aggregate's first overlap."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from math import comb, prod
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

import research.q011bx_degree34_coalesced_sweep as q011bx
import research.q011ca_degree34_component_safe_phase_discs as q011ca
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011bw = q011bx.q011bw
q011an = q011bx.q011an
q011am = q011an.q011am
q011ag = q011an.q011ag
q011b = q011bx.q011b
q011z = q011bx.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
SELECTED_COUNTS = (13, 9, 5, 7)
PARENT_EXTERNAL_GROUP_INDICES = (97,)
PARENT_MERGED_CLASS_INDICES = (0, 0, 1, 1)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7

EXPECTED_PARENT_TARGET_COUNT = 16
EXPECTED_PARENT_TARGET_GROUP_DIGEST = (
    "3ba064cd1fb2cfb330e31b18b8cfffbd64da7ed60e03a529ab8b3b9d6693266e"
)
EXPECTED_PARENT_AGGREGATE_RECORD_DIGEST = (
    "89fc350db6a53cb9dfb4ae76159ec2b4c2cdb38836e42211f2b8a98f9d04341c"
)
EXPECTED_PARENT_RELATION_COUNTS = {
    "product_below_target": 0,
    "target_below_product": 736,
    "overlap": 32,
}
EXPECTED_PARENT_WEIGHTED_RELATION_COUNTS = {
    "product_below_target": 0,
    "target_below_product": 2_991_468_348_800,
    "overlap": 82_513_244_160,
}
EXPECTED_PARENT_LEFT_INDEX = 0
EXPECTED_PARENT_RIGHT_INDEX = 0
EXPECTED_PARENT_WAVE_MULTIPLICITY = 629_841_280
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_CLASS_COUNTS = ((13,), (9,), (0, 5), (0, 7))
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.2ce2f11752629p-31"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.31de02af5b67ap-28"
EXPECTED_PARENT_WITNESS_DIGEST = (
    "5adbaf7e28575c5dc1bda880244b3399f0d65479bb10ba6b46e511df9ea14a58"
)

EXPECTED_REFINED_CLASS_COUNTS = (4, 2, 1, 2)
EXPECTED_SELECTED_IDENTIFIER_COUNT = 18
EXPECTED_CLASS_MEMBERSHIP_DIGEST = (
    "2a474335f20f4923ff147d831062f57145828216010bad67e5f15ed0ca31133f"
)
EXPECTED_SELECTED_IDENTIFIER_DIGEST = (
    "77ec8c096490621edbee63e73c18044cd8220953030119a00dbc360c873735ac"
)
EXPECTED_SELECTED_RECORD_DIGEST = (
    "616221535afe55a8c5074848d659ffb7bf0a4499404185c8006946abd488d819"
)
EXPECTED_TARGET_RECORD_DIGEST = (
    "8fead9d0902e3aa3cf2ad0c5b8eb3996a58ce6614f2e76176f21f2c1b5797c71"
)
EXPECTED_CLASS_SIGNATURE_UPPER = 44_800
EXPECTED_INDIVIDUAL_MONOMIAL_UPPER = 12_279_168_000
EXPECTED_LEFT_POOL_SIZE = 5_600
EXPECTED_RIGHT_POOL_SIZE = 8
EXPECTED_CLASS_POWER_COUNT = 93
EXPECTED_GROUP_SIGNATURE_COUNT = 579
EXPECTED_PAIR_POOL_COUNT = 2
EXPECTED_CONVOLUTION_COUNT = 7_885
EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND = 4_250
EXPECTED_CLASS_POWER_DIGEST = (
    "4f3f082ab45e8b743a22d9315a472a6a11bfe4504e569d8743117e7dff49e438"
)
EXPECTED_GROUP_SIGNATURE_DIGEST = (
    "f5477dcb209f78f4614867753385d89fc96ea921e39f91b5d9faa7268c0f8ef9"
)
EXPECTED_PAIR_POOL_DIGEST = (
    "dbdffe49d1db1768ba071671e0469ec4efa0246cfa5f6047849b7099ae2cae62"
)
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 716_800

Q011CA_ARTIFACT_SHA256 = (
    "df97cbade918c7b71fee33be97779b4615982c13a8f3fbd7715255ba8ee1b1ae"
)
Q011CA_RUNNER_SHA256 = (
    "a4fc7f9bbcee84b587cd57721636e826070ae8a0ec1237c7e2a29f1bc11cc253"
)
Q011CA_DIGEST_NAMES = (
    "input_digest_sha256",
    "phase_input_digest_sha256",
    "allocation_digest_sha256",
    "phase_comparison_digest_sha256",
    "result_digest_sha256",
)
Q011CA_DIGESTS = (
    "f404ad913fd8b46298b70a6e333489ad0cd2d1a7b7ee42789dc943facf761251",
    "88b59df6111f44524da55737bccfa3675ac1f8a24b77e56e7406f58bd8e95fa4",
    "323f5249f5c2b827bf125ef74af9a9dd67c6eae2afd41213d8e28f1e426d8cc4",
    "e56d72fef79d91f307173985b322d52c0f4152be4ac20ed949f03ca99c720193",
    "8b0e9c1b02231c950ef117b6517ffce97dbd1383617d84ad8d79e3a92febca2c",
)

RESOLVED_CLASSIFICATION = (
    "the second Q011bx aggregate first overlap is resolved by the registered "
    "blockwise partition"
)
PERSISTENT_CLASSIFICATION = (
    "the second Q011bx aggregate first overlap persists under the registered "
    "blockwise partition"
)
INCONCLUSIVE_CLASSIFICATION = (
    "the Q011cb second-aggregate first-overlap refinement is inconclusive"
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
    prior, artifacts = q011ca._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011ca_degree34_component_safe_phase_discs.json"
    )
    runner_path = Path(q011ca.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    comparison = cycle["complex_phase_product_disc_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CA_DIGEST_NAMES)
    checks = {
        "q011ca_fifty_seven_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 57
            and prior["direct_digest_count"] == 269
            and len(artifacts) == 57
            and all(prior["checks"].values())
        ),
        "q011ca_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CA_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CA_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CA_RUNNER_SHA256
        ),
        "q011ca_section_digests_match": digests == Q011CA_DIGESTS,
        "q011ca_valid_resolution_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "component_safe_phase_resolved"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "component_safe_complex_phase_discs_resolve_first_q011by_witness_family"
            ]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"]
            == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"]
            == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011ca_registered_comparison_result_reproduces": bool(
            comparison["compatible_phase_allocation_count"] == 5_140
            and comparison["category_counts"]
            == {
                "individual_modulus_separation": 0,
                "complex_phase_separation": 5_140,
                "unresolved_product_disk_overlap": 0,
            }
            and comparison["comparison_stream_digest_sha256"]
            == "0095b012cab089b477e20a3729d91f601ade466df2090c9ddbd330d69791653c"
        ),
        "q011ca_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "two_hundred_seventy_four_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 274
        ),
    }
    artifacts["q011ca"] = artifact
    return (
        {
            "prior_q011ca_sealed_input_audit": prior,
            "q011ca": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CA_DIGEST_NAMES),
                "digests": list(digests),
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _fixed_refinement_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[tuple[tuple[str, ...], ...], ...],
    dict[str, q011z._UniformDisc],
]:
    (
        parent_fixed,
        merged_classes,
        hull_lookup,
        parent_counts,
        parent_external_indices,
        parent_target_groups,
    ) = q011bx._fixed_input_audit(artifacts)
    stored_sweep = artifacts["q011bx"]["cycle"][
        "degree_thirty_four_block_support_coalesced_sweep"
    ]
    stored_record = stored_sweep["aggregate_records"][PARENT_AGGREGATE_INDEX]
    parent_target_group = parent_target_groups[PARENT_AGGREGATE_INDEX]
    parent_relations = q011an._single_aggregate_relations(
        merged_classes,
        hull_lookup,
        parent_counts[PARENT_AGGREGATE_INDEX],
        parent_target_group,
    )
    parent_raw = {
        **parent_relations["first_unresolved"],
        "aggregate_index": PARENT_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "relation": "overlap",
    }
    parent_witness = q011am._exact_witness(
        merged_classes,
        hull_lookup,
        parent_raw,
    )

    (
        inventory,
        selected_groups,
        external_merged,
        _overlap_counts,
        external_indices,
        target_groups,
    ) = q011bw._degree_thirty_four_inventory_audit(artifacts)
    base, lookup, original_classes = (
        q011bw.q011ap._degree_eighteen_envelope_inventory_audit(
            artifacts,
            selected_groups,
            external_merged,
            target_groups,
        )
    )
    refined_classes = (
        original_classes[0],
        original_classes[1],
        (original_classes[2][2],),
        original_classes[3][4:6],
    )
    class_record = [[list(members) for members in group] for group in refined_classes]
    selected_identifiers = tuple(
        sorted(set().union(*(set(members) for group in refined_classes for members in group)))
    )
    records_by_identifier = {
        record["identifier"]: record for record in base["final_disc_records"]
    }
    selected_records = [records_by_identifier[value] for value in selected_identifiers]
    target_record = records_by_identifier[TARGET_IDENTIFIER]
    parent_target_digest = q011b._canonical_json_sha256(list(parent_target_group))
    stored_record_digest = q011b._canonical_json_sha256(stored_record)
    class_digest = q011b._canonical_json_sha256(class_record)
    selected_identifier_digest = q011b._canonical_json_sha256(
        list(selected_identifiers)
    )
    selected_record_digest = q011b._canonical_json_sha256(selected_records)
    target_record_digest = q011b._canonical_json_sha256(target_record)

    occupied_parent_members = tuple(
        set(merged_classes[group_index][merged_index])
        for group_index, merged_index in enumerate(PARENT_MERGED_CLASS_INDICES)
    )
    refined_members = tuple(
        set().union(*(set(members) for members in group)) for group in refined_classes
    )
    all_original_discs_contained = all(
        hull_lookup[identifier].modulus.lower <= lookup[identifier].modulus.lower
        <= lookup[identifier].modulus.upper <= hull_lookup[identifier].modulus.upper
        and hull_lookup[identifier].center_modulus.lower
        <= lookup[identifier].center_modulus.lower
        <= lookup[identifier].center_modulus.upper
        <= hull_lookup[identifier].center_modulus.upper
        for identifier in selected_identifiers
    )

    class_signature_upper = prod(
        comb(count + len(refined_classes[group_index]) - 1, count)
        for group_index, count in enumerate(SELECTED_COUNTS)
    )
    individual_monomial_upper = prod(
        comb(
            count + sum(map(len, refined_classes[group_index])) - 1,
            count,
        )
        for group_index, count in enumerate(SELECTED_COUNTS)
    )
    pools = q011am._HierarchicalPools(refined_classes, lookup)
    left = pools.pair_pool(0, SELECTED_COUNTS[0], 1, SELECTED_COUNTS[1])
    right = pools.pair_pool(2, SELECTED_COUNTS[2], 3, SELECTED_COUNTS[3])
    power_records = pools.power_records()
    group_record_count, group_digest, pair_records = pools.factorization_digest()
    power_digest = q011b._canonical_json_sha256(power_records)
    pair_digest = q011b._canonical_json_sha256(pair_records)

    parent_counts_match = tuple(parent_counts[PARENT_AGGREGATE_INDEX]) == SELECTED_COUNTS
    parent_record_relations_match = bool(
        parent_relations["distinct_relation_counts"] == EXPECTED_PARENT_RELATION_COUNTS
        and parent_relations["weighted_relation_counts"]
        == EXPECTED_PARENT_WEIGHTED_RELATION_COUNTS
        and stored_record["distinct_relation_counts"]
        == EXPECTED_PARENT_RELATION_COUNTS
        and stored_record["weighted_relation_counts"]
        == EXPECTED_PARENT_WEIGHTED_RELATION_COUNTS
    )
    parent_witness_matches = bool(
        parent_witness["aggregate_index"] == PARENT_AGGREGATE_INDEX
        and tuple(parent_witness["selected_type_counts"]) == SELECTED_COUNTS
        and parent_witness["target_identifier"] == TARGET_IDENTIFIER
        and parent_witness["output_block"] == OUTPUT_BLOCK
        and parent_witness["left_index"] == EXPECTED_PARENT_LEFT_INDEX
        and parent_witness["right_index"] == EXPECTED_PARENT_RIGHT_INDEX
        and parent_witness["wave_multiplicity"]
        == EXPECTED_PARENT_WAVE_MULTIPLICITY
        and parent_witness["block_zero_multiplicity"]
        == EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY
        and tuple(tuple(row) for row in parent_witness["class_counts"])
        == EXPECTED_PARENT_CLASS_COUNTS
        and parent_witness["intersection_interval"]["width_hex"]
        == EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        and parent_witness["center_only_diagnostic"]["relation"]
        == EXPECTED_PARENT_CENTER_RELATION
        and parent_witness["center_only_diagnostic"]["gap_hex"]
        == EXPECTED_PARENT_CENTER_GAP_HEX
        and parent_witness["witness_digest_sha256"]
        == EXPECTED_PARENT_WITNESS_DIGEST
    )
    checks = {
        "q011bx_fixed_inventory_and_hulls_recompute": bool(
            parent_fixed["passed"]
            and inventory["passed"]
            and base["checks"]["q011k_centers_and_q011ak_block_radii_reconstruct"]
            and base["checks"]["all_two_hundred_four_q011ak_formulas_replay_exactly"]
            and base["checks"]["q011ao_reused_modulus_records_are_bitwise_identical"]
        ),
        "second_parent_aggregate_record_and_relations_reproduce": bool(
            parent_counts_match
            and tuple(parent_external_indices[PARENT_AGGREGATE_INDEX])
            == PARENT_EXTERNAL_GROUP_INDICES
            and tuple(external_indices[PARENT_AGGREGATE_INDEX])
            == PARENT_EXTERNAL_GROUP_INDICES
            and len(parent_target_group) == EXPECTED_PARENT_TARGET_COUNT
            and TARGET_IDENTIFIER in parent_target_group
            and parent_target_digest == EXPECTED_PARENT_TARGET_GROUP_DIGEST
            and stored_record_digest == EXPECTED_PARENT_AGGREGATE_RECORD_DIGEST
            and parent_record_relations_match
        ),
        "registered_parent_first_overlap_witness_reproduces": parent_witness_matches,
        "registered_nine_class_partition_and_records_reproduce": bool(
            tuple(map(len, refined_classes)) == EXPECTED_REFINED_CLASS_COUNTS
            and class_digest == EXPECTED_CLASS_MEMBERSHIP_DIGEST
            and len(selected_identifiers) == EXPECTED_SELECTED_IDENTIFIER_COUNT
            and selected_identifier_digest == EXPECTED_SELECTED_IDENTIFIER_DIGEST
            and selected_record_digest == EXPECTED_SELECTED_RECORD_DIGEST
            and target_record_digest == EXPECTED_TARGET_RECORD_DIGEST
        ),
        "refined_members_exactly_partition_occupied_parent_hulls": bool(
            refined_members == occupied_parent_members and all_original_discs_contained
        ),
        "registered_combinatorial_and_factorization_resources_reproduce": bool(
            class_signature_upper == EXPECTED_CLASS_SIGNATURE_UPPER
            and individual_monomial_upper == EXPECTED_INDIVIDUAL_MONOMIAL_UPPER
            and len(left) == EXPECTED_LEFT_POOL_SIZE
            and len(right) == EXPECTED_RIGHT_POOL_SIZE
            and len(left) * len(right) == EXPECTED_CLASS_SIGNATURE_UPPER
            and len(power_records) == EXPECTED_CLASS_POWER_COUNT
            and group_record_count == EXPECTED_GROUP_SIGNATURE_COUNT
            and len(pair_records) == EXPECTED_PAIR_POOL_COUNT
            and pools.ledger.call_count == EXPECTED_CONVOLUTION_COUNT
            and pools.ledger.maximum_crude_bound
            == EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND
            and power_digest == EXPECTED_CLASS_POWER_DIGEST
            and group_digest == EXPECTED_GROUP_SIGNATURE_DIGEST
            and pair_digest == EXPECTED_PAIR_POOL_DIGEST
            and pools.ledger.all_nonnegative
            and pools.ledger.all_fiber_sums_exact
        ),
        "fixed_refinement_input_is_finite_strict_json": bool(
            _all_numeric_values_finite(class_record)
            and _strict_json_serializable(class_record)
            and json.dumps(class_record, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "parent_external_group_indices": list(PARENT_EXTERNAL_GROUP_INDICES),
        "parent_target_identifier_count": len(parent_target_group),
        "parent_target_group_digest_sha256": parent_target_digest,
        "parent_aggregate_record": stored_record,
        "parent_aggregate_record_digest_sha256": stored_record_digest,
        "parent_first_overlap_witness": parent_witness,
        "target_identifier": TARGET_IDENTIFIER,
        "output_block": OUTPUT_BLOCK,
        "parent_merged_class_indices": list(PARENT_MERGED_CLASS_INDICES),
        "refined_class_counts": list(map(len, refined_classes)),
        "refined_class_memberships": class_record,
        "refined_class_membership_digest_sha256": class_digest,
        "selected_identifier_count": len(selected_identifiers),
        "selected_identifier_digest_sha256": selected_identifier_digest,
        "selected_record_digest_sha256": selected_record_digest,
        "target_record_digest_sha256": target_record_digest,
        "class_signature_upper_bound": class_signature_upper,
        "individual_source_monomial_upper_bound": individual_monomial_upper,
        "left_pool_size": len(left),
        "right_pool_size": len(right),
        "class_power_record_count": len(power_records),
        "class_power_record_digest_sha256": power_digest,
        "group_signature_record_count": group_record_count,
        "group_signature_digest_sha256": group_digest,
        "pair_pool_record_count": len(pair_records),
        "pair_pool_record_digest_sha256": pair_digest,
        "convolution_call_count": pools.ledger.call_count,
        "maximum_convolution_crude_int64_bound": pools.ledger.maximum_crude_bound,
        "other_parent_targets_recomputed": False,
        "other_parent_overlap_signatures_recomputed": False,
        "aggregate_972_recomputed": False,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, refined_classes, lookup


def _targeted_refined_sweep(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> dict[str, Any]:
    pools = q011am._HierarchicalPools(classes, lookup)
    left = pools.pair_pool(0, SELECTED_COUNTS[0], 1, SELECTED_COUNTS[1])
    right = pools.pair_pool(2, SELECTED_COUNTS[2], 3, SELECTED_COUNTS[3])
    left_wave = np.stack([record.wave for record in left])
    right_wave = np.stack([record.wave for record in right])
    product_lower, product_upper = q011ag._product_bound_matrices(left, right)
    wave_matrix, crude_bound = q011ag._wave_matrix(
        left_wave,
        right_wave,
        OUTPUT_BLOCK,
    )
    active = wave_matrix > 0
    target = lookup[TARGET_IDENTIFIER]
    product_below_gap = q011ag._down_subtract(
        q011ag._fraction_lower(target.modulus.lower),
        product_upper,
    )
    target_below_gap = q011ag._down_subtract(
        product_lower,
        q011ag._fraction_upper(target.modulus.upper),
    )
    product_below = active & (product_below_gap > 0)
    target_below = active & (target_below_gap > 0)
    unresolved = active & ~(product_below | target_below)
    relation_counter: Counter[str] = Counter()
    for relation, mask in (
        ("product_below_target", product_below),
        ("target_below_product", target_below),
        ("overlap", unresolved),
    ):
        relation_counter[f"{relation}_distinct"] = int(mask.sum())
        relation_counter[f"{relation}_weighted"] = int(wave_matrix[mask].sum())

    first_raw: dict[str, Any] | None = None
    if unresolved.any():
        flat_index = int(np.flatnonzero(unresolved)[0])
        left_index, right_index = map(
            int,
            np.unravel_index(flat_index, unresolved.shape),
        )
        first_raw = {
            "aggregate_index": 0,
            "selected_type_counts": list(SELECTED_COUNTS),
            "target_identifier": TARGET_IDENTIFIER,
            "output_block": OUTPUT_BLOCK,
            "left_index": left_index,
            "right_index": right_index,
            "wave_multiplicity": int(wave_matrix[left_index, right_index]),
            "relation": "overlap",
            "class_counts": [
                list(group)
                for group in q011ag._signature_counts(
                    left,
                    right,
                    left_index,
                    right_index,
                )
            ],
        }

    minimum: tuple[tuple[Any, ...], dict[str, Any]] | None = None
    for relation, gaps, mask in (
        ("product_below_target", product_below_gap, product_below),
        ("target_below_product", target_below_gap, target_below),
    ):
        if not mask.any():
            continue
        candidates = np.where(mask, gaps, np.inf)
        flat_index = int(candidates.argmin())
        left_index, right_index = map(
            int,
            np.unravel_index(flat_index, candidates.shape),
        )
        gap = float(candidates[left_index, right_index])
        key = (gap, TARGET_IDENTIFIER, left_index, right_index)
        raw = {
            "aggregate_index": 0,
            "selected_type_counts": list(SELECTED_COUNTS),
            "target_identifier": TARGET_IDENTIFIER,
            "output_block": OUTPUT_BLOCK,
            "left_index": left_index,
            "right_index": right_index,
            "wave_multiplicity": int(wave_matrix[left_index, right_index]),
            "relation": relation,
            "class_counts": [
                list(group)
                for group in q011ag._signature_counts(
                    left,
                    right,
                    left_index,
                    right_index,
                )
            ],
            "outward_gap": gap,
        }
        if minimum is None or key < minimum[0]:
            minimum = (key, raw)

    first_witness = q011am._exact_witness(classes, lookup, first_raw) if first_raw else None
    minimum_witness = (
        q011am._exact_witness(classes, lookup, minimum[1])
        if minimum is not None
        else None
    )
    original_monomials = sum(record.fiber_multiplicity for record in left) * sum(
        record.fiber_multiplicity for record in right
    )
    expected_original_monomials = prod(
        comb(count + sum(map(len, classes[group_index])) - 1, count)
        for group_index, count in enumerate(SELECTED_COUNTS)
    )
    signature_count = len(left) * len(right)
    expected_signatures = prod(
        comb(count + len(classes[group_index]) - 1, count)
        for group_index, count in enumerate(SELECTED_COUNTS)
    )
    distinct_relations = q011am._relation_counts(relation_counter, "distinct")
    weighted_relations = q011am._relation_counts(relation_counter, "weighted")
    separated_count = (
        distinct_relations["product_below_target"]
        + distinct_relations["target_below_product"]
    )
    compatible_multiplicity = int(wave_matrix[active].sum())
    aggregate_record = {
        "aggregate_index": 0,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "parent_merged_class_counts": [list(row) for row in EXPECTED_PARENT_CLASS_COUNTS],
        "target_identifier_count": 1,
        "original_monomial_count": original_monomials,
        "modulus_signature_count": signature_count,
        "compatible_modulus_signature_count": int(active.sum()),
        "compatible_original_monomial_count": compatible_multiplicity,
        "weighted_comparison_count": compatible_multiplicity,
        "distinct_comparison_count": int(active.sum()),
        "weighted_relation_counts": weighted_relations,
        "distinct_relation_counts": distinct_relations,
        "minimum_certified_gap_lower": (
            q011am._float_record(minimum[0][0]) if minimum is not None else None
        ),
        "minimum_witness": (
            {key: value for key, value in minimum[1].items() if key != "outward_gap"}
            if minimum is not None
            else None
        ),
    }
    power_records = pools.power_records()
    group_record_count, factor_digest, pair_records = pools.factorization_digest()
    bound_records = [
        {
            "aggregate_index": 0,
            "selected_type_counts": list(SELECTED_COUNTS),
            "shape": list(product_lower.shape),
            "lower_sha256": q011b._array_sha256(product_lower.astype(">f8")),
            "upper_sha256": q011b._array_sha256(product_upper.astype(">f8")),
        }
    ]
    coefficient_records = [
        {
            "aggregate_index": 0,
            "output_block": OUTPUT_BLOCK,
            "shape": list(wave_matrix.shape),
            "coefficient_sha256": q011b._array_sha256(wave_matrix.astype(">i8")),
        }
    ]
    codes = np.zeros(wave_matrix.shape, dtype=np.uint8)
    codes[product_below] = 1
    codes[target_below] = 2
    codes[unresolved] = 3
    classification_records = [
        {
            "aggregate_index": 0,
            "output_block": OUTPUT_BLOCK,
            "target_identifier": TARGET_IDENTIFIER,
            "shape": list(codes.shape),
            "classification_sha256": q011b._array_sha256(codes),
        }
    ]
    sweep = {
        "degree": DEGREE,
        "local_aggregate_index": 0,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "audited_parent_witness_family_count": 1,
        "fully_separated_parent_witness_family_count": int(not unresolved.any()),
        "remaining_overlap_parent_witness_family_count": int(unresolved.any()),
        "original_monomial_count": original_monomials,
        "modulus_signature_count": signature_count,
        "compatible_modulus_signature_count": int(active.sum()),
        "compatible_original_monomial_count": compatible_multiplicity,
        "weighted_comparison_count": compatible_multiplicity,
        "distinct_comparison_count": int(active.sum()),
        "weighted_relation_counts": weighted_relations,
        "distinct_relation_counts": distinct_relations,
        "aggregate_records": [aggregate_record],
        "aggregate_record_digest_sha256": q011b._canonical_json_sha256([aggregate_record]),
        "class_power_record_count": len(power_records),
        "class_power_record_digest_sha256": q011b._canonical_json_sha256(power_records),
        "group_signature_record_count": group_record_count,
        "group_signature_digest_sha256": factor_digest,
        "pair_pool_record_count": len(pair_records),
        "pair_pool_record_digest_sha256": q011b._canonical_json_sha256(pair_records),
        "bound_matrix_record_count": len(bound_records),
        "bound_matrix_digest_sha256": q011b._canonical_json_sha256(bound_records),
        "coefficient_matrix_record_count": len(coefficient_records),
        "coefficient_matrix_digest_sha256": q011b._canonical_json_sha256(
            coefficient_records
        ),
        "classification_matrix_record_count": len(classification_records),
        "classification_matrix_digest_sha256": q011b._canonical_json_sha256(
            classification_records
        ),
        "separated_comparison_exists": separated_count > 0,
        "global_minimum_separated_witness": minimum_witness,
        "first_unresolved_witness": first_witness,
        "maximum_live_combined_signature_count": signature_count,
        "two_product_bound_array_bytes": 2 * 8 * signature_count,
        "maximum_wave_coefficient": int(wave_matrix.max(initial=0)),
        "maximum_fourier_crude_int64_bound": crude_bound,
        "convolution_call_count": pools.ledger.call_count,
        "maximum_convolution_crude_int64_bound": pools.ledger.maximum_crude_bound,
        "all_convolutions_nonnegative": pools.ledger.all_nonnegative,
        "all_convolution_fiber_sums_exact": pools.ledger.all_fiber_sums_exact,
        "all_product_bound_arrays_are_finite": bool(
            np.isfinite(product_lower).all() and np.isfinite(product_upper).all()
        ),
        "all_product_bound_arrays_are_nonnegative_and_ordered": bool(
            np.all(product_lower >= 0) and np.all(product_lower <= product_upper)
        ),
        "all_original_monomial_counts_match_multiset_coefficients": (
            original_monomials == expected_original_monomials
        ),
        "all_modulus_signature_counts_match_weak_compositions": (
            signature_count == expected_signatures
        ),
        "parent_wave_multiplicity_is_exactly_partitioned": (
            compatible_multiplicity == EXPECTED_PARENT_WAVE_MULTIPLICITY
        ),
        "other_parent_targets_recomputed": False,
        "other_parent_overlap_signatures_recomputed": False,
        "aggregate_972_recomputed": False,
        "streaming_contract": {
            "full_individual_source_monomial_list_retained": False,
            "full_classification_matrix_retained": False,
            "aggregate_summary_count": 1,
            "peak_live_combined_signature_count": signature_count,
            "hierarchical_class_power_cache_count": len(power_records),
            "group_pool_cache_count": len(pools.group_cache),
            "pair_pool_cache_count": len(pools.pair_cache),
        },
    }
    minimum_record = sweep["global_minimum_separated_witness"]
    first_overlap = sweep["first_unresolved_witness"]
    exclusive_count = sum(sweep["distinct_relation_counts"].values())
    checks = {
        "one_registered_parent_witness_family_is_processed": bool(
            sweep["audited_parent_witness_family_count"] == 1
            and len(sweep["aggregate_records"]) == 1
            and sweep["aggregate_records"][0]["parent_q011bx_aggregate_index"]
            == PARENT_AGGREGATE_INDEX
            and sweep["aggregate_records"][0]["target_identifier_count"] == 1
        ),
        "registered_signature_monomial_and_memory_resources_reproduce": bool(
            signature_count == EXPECTED_CLASS_SIGNATURE_UPPER
            and original_monomials == EXPECTED_INDIVIDUAL_MONOMIAL_UPPER
            and sweep["two_product_bound_array_bytes"]
            == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
            and sweep["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and sweep["group_signature_record_count"]
            == EXPECTED_GROUP_SIGNATURE_COUNT
            and sweep["pair_pool_record_count"] == EXPECTED_PAIR_POOL_COUNT
            and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_COUNT
        ),
        "exact_convolution_partitions_parent_wave_multiplicity": bool(
            sweep["all_convolutions_nonnegative"]
            and sweep["all_convolution_fiber_sums_exact"]
            and sweep["parent_wave_multiplicity_is_exactly_partitioned"]
            and compatible_multiplicity == sum(weighted_relations.values())
        ),
        "outward_arrays_and_integer_bounds_are_valid": bool(
            sweep["all_product_bound_arrays_are_finite"]
            and sweep["all_product_bound_arrays_are_nonnegative_and_ordered"]
            and sweep["all_original_monomial_counts_match_multiset_coefficients"]
            and sweep["all_modulus_signature_counts_match_weak_compositions"]
            and sweep["maximum_fourier_crude_int64_bound"] < 2**63
            and sweep["maximum_convolution_crude_int64_bound"] < 2**63
        ),
        "classification_is_exclusive_and_complete": bool(
            exclusive_count == sweep["distinct_comparison_count"]
            and sum(weighted_relations.values()) == sweep["weighted_comparison_count"]
        ),
        "stream_summaries_and_witness_protocol_are_present": bool(
            sweep["bound_matrix_record_count"] == 1
            and sweep["coefficient_matrix_record_count"] == 1
            and sweep["classification_matrix_record_count"] == 1
            and (minimum_record is not None or separated_count == 0)
            and (first_overlap is None or first_overlap["relation"] == "overlap")
        ),
        "targeted_sweep_is_finite_strict_json": bool(
            _all_numeric_values_finite(sweep)
            and _strict_json_serializable(sweep)
            and json.dumps(sweep, allow_nan=False)
        ),
    }
    return {
        **sweep,
        "registered_checks": checks,
        "registered_passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "parent_first_overlap_target_identifier": TARGET_IDENTIFIER,
        "parent_first_overlap_output_block": OUTPUT_BLOCK,
        "parent_merged_class_counts": [list(row) for row in EXPECTED_PARENT_CLASS_COUNTS],
        "source_partition_change": "four occupied merged hulls to nine blockwise classes",
        "class_signature_upper_bound": EXPECTED_CLASS_SIGNATURE_UPPER,
        "individual_source_monomial_upper_bound": EXPECTED_INDIVIDUAL_MONOMIAL_UPPER,
        "other_parent_targets_recomputed": False,
        "other_parent_overlap_signatures_recomputed": False,
        "aggregate_972_recomputed": False,
        "target_folding_used": False,
        "complex_phase_used": False,
        "post_observation_class_split_used": False,
        "full_individual_source_monomial_list_retained": False,
        "full_classification_matrix_retained": False,
        "resolved_classification": RESOLVED_CLASSIFICATION,
        "persistent_classification": PERSISTENT_CLASSIFICATION,
        "q011bx_rejection_changed": False,
        "degree_thirty_four_nonresonance_claimed": False,
        "actual_resonance_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "refinement_input_digest_sha256": cycle["refinement_input_digest_sha256"],
        "targeted_sweep_digest_sha256": cycle["targeted_sweep_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "diagnostic_gates": cycle["diagnostic_gates"],
        "study_validity": cycle["study_validity"],
        "refinement_outcome": cycle["refinement_outcome"],
        "diagnostic_classification": cycle["diagnostic_classification"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_degree_thirty_four_second_overlap_refinement() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    fixed, classes, lookup = _fixed_refinement_input_audit(artifacts)
    sweep = _targeted_refined_sweep(classes, lookup)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    refinement_sections = {"fixed_blockwise_refinement_input_audit": fixed}
    sweep_sections = {"targeted_blockwise_refinement_sweep": sweep}
    input_digest = q011b._canonical_json_sha256(input_sections)
    refinement_digest = q011b._canonical_json_sha256(refinement_sections)
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
        "q011ca_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "58 artifacts and 274 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_second_parent_aggregate_and_first_overlap_reproduce": {
            "passed": bool(
                fixed["checks"][
                    "second_parent_aggregate_record_and_relations_reproduce"
                ]
                and fixed["checks"][
                    "registered_parent_first_overlap_witness_reproduces"
                ]
            ),
            "threshold": "aggregate 2340, 32 overlaps and the fixed first witness",
            "value": fixed["parent_first_overlap_witness"]["witness_digest_sha256"],
        },
        "registered_nine_class_partition_records_and_containment_reproduce": {
            "passed": bool(
                fixed["checks"][
                    "registered_nine_class_partition_and_records_reproduce"
                ]
                and fixed["checks"][
                    "refined_members_exactly_partition_occupied_parent_hulls"
                ]
            ),
            "threshold": "nine classes, 18 selected records and unchanged target",
            "value": {
                "class": fixed["refined_class_membership_digest_sha256"],
                "target": fixed["target_record_digest_sha256"],
            },
        },
        "registered_combinatorial_and_factorization_resources_reproduce": {
            "passed": fixed["checks"][
                "registered_combinatorial_and_factorization_resources_reproduce"
            ],
            "threshold": "44800 signatures and registered factorization digests",
            "value": {
                "signature": fixed["class_signature_upper_bound"],
                "individual": fixed["individual_source_monomial_upper_bound"],
            },
        },
        "exact_convolution_partitions_the_parent_multiplicity": {
            "passed": sweep["registered_checks"][
                "exact_convolution_partitions_parent_wave_multiplicity"
            ],
            "threshold": "compatible multiplicity sum equals 629841280 exactly",
            "value": sweep["compatible_original_monomial_count"],
        },
        "targeted_outward_classification_and_witness_protocol_pass": {
            "passed": sweep["registered_passed"],
            "threshold": "exclusive outward classification and exact witnesses",
            "value": sweep["registered_checks"],
        },
        "strict_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(len(value) == 64 for value in (input_digest, refinement_digest, sweep_digest))
                and runner["filename"]
                == "q011cb_degree34_second_overlap_refinement.py"
                and (minimum is not None or not sweep["separated_comparison_exists"])
                and (first_overlap is None or first_overlap["relation"] == "overlap")
            ),
            "threshold": "three section digests, exact witnesses and runner metadata",
            "value": {
                "input": input_digest,
                "refinement": refinement_digest,
                "sweep": sweep_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    overlap_count = sweep["distinct_relation_counts"]["overlap"]
    resolved = bool(
        validity_passed
        and overlap_count == 0
        and minimum_outward_positive
        and minimum_exact_positive
    )
    persistent = validity_passed and overlap_count > 0
    diagnostic_gates = {
        "only_the_registered_parent_witness_family_is_refined": {
            "passed": bool(
                not sweep["other_parent_targets_recomputed"]
                and not sweep["other_parent_overlap_signatures_recomputed"]
                and not sweep["aggregate_972_recomputed"]
            ),
            "threshold": "one parent signature, one target and no aggregate 972",
            "value": PARENT_AGGREGATE_INDEX,
        },
        "every_compatible_refined_signature_is_classified": {
            "passed": bool(
                sum(sweep["distinct_relation_counts"].values())
                == sweep["distinct_comparison_count"]
            ),
            "threshold": "every compatible signature has exactly one relation",
            "value": sweep["distinct_relation_counts"],
        },
        "registered_resolution_or_persistence_stopping_rule_is_applied": {
            "passed": resolved or persistent,
            "threshold": "zero overlap with positive minima, or a retained first overlap",
            "value": {
                "overlap": overlap_count,
                "minimum_outward_positive": minimum_outward_positive,
                "minimum_exact_positive": minimum_exact_positive,
            },
        },
        "scientific_boundary_is_preserved": {
            "passed": True,
            "threshold": "no aggregate-wide, degree-34, resonance or SSM claim",
            "value": "certified 2--33 and 91+, missing 34--90",
        },
    }
    refinement_outcome = (
        "resolved" if resolved else "persistent" if persistent else "inconclusive"
    )
    classification = (
        RESOLVED_CLASSIFICATION
        if resolved
        else PERSISTENT_CLASSIFICATION
        if persistent
        else INCONCLUSIVE_CLASSIFICATION
    )
    cycle = {
        "question": (
            "Does the registered nine-class blockwise partition strictly separate every "
            "compatible refinement of aggregate 2340's first coalesced overlap witness?"
        ),
        **input_sections,
        **refinement_sections,
        **sweep_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "refinement_input_digest_sha256": refinement_digest,
        "targeted_sweep_digest_sha256": sweep_digest,
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
        "actual_resonance_outcome": (
            "not_established" if validity_passed else "inconclusive"
        ),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "second_q011bx_aggregate_first_overlap_is_resolved_by_registered_partition": (
            resolved
        ),
        "second_q011bx_aggregate_first_overlap_persists_under_registered_partition": (
            persistent
        ),
        "second_q011bx_aggregate_is_fully_audited": False,
        "remaining_parent_coalesced_overlaps_are_audited": False,
        "q011ca_component_safe_phase_resolution_is_preserved": True,
        "q011bz_interval_inert_diagnostic_is_preserved": True,
        "q011by_persistent_diagnostic_is_preserved": True,
        "q011bx_degree_thirty_four_sufficient_certificate_remains_rejected": True,
        "degree_thirty_four_external_nonresonance_is_certified": False,
        "an_actual_degree_thirty_four_external_resonance_is_established": False,
        "certified_external_nonresonance_degrees": list(range(2, 34)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(34, 91)),
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This diagnostic concerns only the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf, degree-34 parent aggregate 2340, its lexicographically first "
        "coalesced overlap signature, the registered nine-class blockwise partition and "
        "target block=7;center=44. It does not audit the other 31 parent coalesced "
        "overlaps, the other 15 targets, aggregate 2340 as a whole, other aggregate 972 "
        "signatures or the full degree-34 sweep. It leaves the Q011bx rejection, Q011by "
        "persistence, Q011bz interval-inert result, Q011ca phase resolution, certified "
        "degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and makes no claim "
        "about an actual resonance, degree-34 nonresonance, all-order nonresonance, "
        "higher graph smoothness, SSM existence or uniqueness, normal attraction, a "
        "basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cc to audit the next coalesced overlap witness in Q011bx "
        "aggregate 2340."
        if resolved
        else (
            "Preregister Q011cc to split only the first persistent Q011cb refined "
            "witness into individual source discs."
        )
        if persistent
        else "Repair only the first Q011cb validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011cb cycle failed strict serialization or digest")
    return cycle


def run_q011cb_study() -> dict[str, Any]:
    started = perf_counter()
    cycle = run_degree_thirty_four_second_overlap_refinement()
    elapsed = perf_counter() - started
    sweep = cycle["targeted_blockwise_refinement_sweep"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "nine exact registered blockwise classes",
            "product_enclosure": "outward-rounded binary64 hierarchical products",
            "fourier_multiplicity": "exact int64 cyclic convolution",
            "target_comparisons": "one fixed target disc without folding",
            "full_individual_source_monomial_list_retained": False,
            "full_classification_matrix_retained": False,
            "convolution_call_count": sweep["convolution_call_count"],
            "peak_live_signature_count": sweep[
                "maximum_live_combined_signature_count"
            ],
            "elapsed_seconds": elapsed,
        },
        "mathematical_scope": {
            "diagnostic": "second aggregate first-overlap blockwise refinement",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "target_identifier": TARGET_IDENTIFIER,
            "other_parent_coalesced_overlaps_audited": False,
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
    result = run_q011cb_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
