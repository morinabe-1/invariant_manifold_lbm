"""Q011by targeted refinement of the first Q011bx degree-thirty-four overlap."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from math import comb, prod
from pathlib import Path
from typing import Any

import numpy as np

import research.q011bx_degree34_coalesced_sweep as q011bx
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
q011as = q011bw.q011as
q011b = q011bx.q011b
q011z = q011bx.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 972
SELECTED_COUNTS = (4, 27, 3, 0)
TARGET_IDENTIFIER = "block=12;center=124"
PARENT_EXTERNAL_GROUP_INDICES = (71,)
EXPECTED_PARENT_TARGET_COUNT = 24
EXPECTED_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_CLASS_SIGNATURE_UPPER = 9_800
EXPECTED_INDIVIDUAL_MONOMIAL_UPPER = 26_796_000

EXPECTED_CLASS_RECORD_DIGEST = (
    "18076020b56f23f6a7a8c80411c7927e941fe2a15ef1f1c9ff708ec350196217"
)
EXPECTED_SELECTED_IDENTIFIER_DIGEST = (
    "53d431c0dfab5fa5a8f2769d450a18223a2d9a15640462e58b9c175cf53d58d6"
)
EXPECTED_SELECTED_RECORD_DIGEST = (
    "08f743e4d676429c3c7b3f1685d5d8faa93c524a827d09ac9e52649d64318377"
)
EXPECTED_TARGET_RECORD_DIGEST = (
    "6f76020e786af37cdac5aaf16d92617d36da55cceda814baaef6e0b9ababfc86"
)
EXPECTED_PARENT_TARGET_GROUP_DIGEST = (
    "000442ccf61d32032eec57cc430dc374dd0c89286edab9f773652ff170d9e1e7"
)
EXPECTED_FIRST_INTERSECTION_WIDTH_HEX = "0x1.570c9fb70fc7dp-28"
EXPECTED_FIRST_CENTER_GAP_HEX = "0x1.abbf5bfb5e7ccp-27"
EXPECTED_FIRST_WITNESS_DIGEST = (
    "ad3f2cb8d8ad0f75eacaec10b8ff606e709bc5ff037542ca612ecc97a40d8ce5"
)
EXPECTED_SOURCE_FREQUENCIES = {
    "block=16;center=142": 4,
    "block=16;center=150": 24,
    "block=1;center=150": 3,
    "block=1;center=152": 3,
}

RESOLVED_CLASSIFICATION = (
    "the first Q011bx overlap is resolved by the registered uncoalesced blockwise partition"
)
PERSISTENT_CLASSIFICATION = (
    "the first Q011bx overlap persists under the registered uncoalesced blockwise partition"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011by first-overlap refinement is inconclusive"

Q011BX_ARTIFACT_SHA256 = "01307870ef93c219009b56a77cff58ecf55fe32f987cd9365dc43122b04eb9e2"
Q011BX_RUNNER_SHA256 = "cfae443c9934a202c34e9455aaf6499d1bff636d3b45e617245426e9449e221d"
Q011BX_DIGEST_NAMES = (
    "input_digest_sha256",
    "preparation_digest_sha256",
    "sweep_digest_sha256",
    "result_digest_sha256",
)
Q011BX_DIGESTS = (
    "e69981e0c318bcc0f29f25a7c0e568db2f088841949b5a3a008ccabdc9f705a6",
    "7ea445c2c4d8297dc523e4543b37caba35daafc8cddb4625e39b4039d0cf467f",
    "4741be104eefef8eafc43ea13e221e23521dec80adf51969cc7d7a112241f9b9",
    "595044021e943ee98cdf00e6413da53a47db3e6ebb6aa823a03cf4069278170f",
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
    prior, artifacts = q011bx._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011bx_degree34_coalesced_sweep.json"
    runner_path = Path(q011bx.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    sweep = cycle["degree_thirty_four_block_support_coalesced_sweep"]
    theorem = cycle["theorem_consequence"]
    first = sweep["first_unresolved_witness"]
    digests = tuple(cycle[name] for name in Q011BX_DIGEST_NAMES)
    checks = {
        "q011bx_fifty_four_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 257
            and len(artifacts) == 54
            and all(prior["checks"].values())
        ),
        "q011bx_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011BX_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011BX_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011BX_RUNNER_SHA256
        ),
        "q011bx_section_digests_match": digests == Q011BX_DIGESTS,
        "q011bx_valid_rejection_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["registered_degree_thirty_four_sufficient_certificate_is_rejected"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011bx_two_unresolved_aggregates_reproduce": bool(
            sweep["remaining_overlap_aggregate_count"] == 2
            and sweep["remaining_overlap_aggregate_indices"] == [972, 2340]
            and sweep["distinct_relation_counts"]["overlap"] == 64
        ),
        "q011bx_first_witness_identity_reproduces": bool(
            first["aggregate_index"] == PARENT_AGGREGATE_INDEX
            and tuple(first["selected_type_counts"]) == SELECTED_COUNTS
            and first["target_identifier"] == TARGET_IDENTIFIER
            and first["output_block"] == 12
            and first["left_index"] == first["right_index"] == 0
            and first["wave_multiplicity"] == 341_000
            and first["relation"] == "overlap"
            and first["intersection_interval"]["width_hex"]
            == EXPECTED_FIRST_INTERSECTION_WIDTH_HEX
            and first["center_only_diagnostic"]["relation"] == "target_below_product"
            and first["center_only_diagnostic"]["gap_hex"] == EXPECTED_FIRST_CENTER_GAP_HEX
            and first["witness_digest_sha256"] == EXPECTED_FIRST_WITNESS_DIGEST
        ),
        "q011bx_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "two_hundred_sixty_one_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 261
        ),
    }
    artifacts["q011bx"] = artifact
    return (
        {
            "prior_q011bx_sealed_input_audit": prior,
            "q011bx": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011BX_DIGEST_NAMES),
                "digests": list(digests),
                "first_unresolved_witness": first,
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
    tuple[int, ...],
]:
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        external_indices,
        target_groups,
    ) = q011bw._degree_thirty_four_inventory_audit(artifacts)
    base, lookup, classes = q011bw.q011ap._degree_eighteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    coalescing, merged_classes, hull_lookup = q011as._coalesce_classes(classes, lookup)
    stored_bw = artifacts["q011bw"]["cycle"]
    stored_inventory = stored_bw["degree_thirty_four_inventory_audit"]
    stored_envelope = stored_bw["degree_thirty_four_envelope_audit"]
    active_records = base["final_disc_records"]
    records_by_identifier = {record["identifier"]: record for record in active_records}
    selected_identifiers = tuple(sorted(set().union(*map(set, selected_groups))))
    selected_records = [records_by_identifier[identifier] for identifier in selected_identifiers]
    target_record = records_by_identifier[TARGET_IDENTIFIER]
    class_record = [[list(members) for members in group] for group in classes]
    class_digest = q011b._canonical_json_sha256(class_record)
    selected_identifier_digest = q011b._canonical_json_sha256(list(selected_identifiers))
    selected_record_digest = q011b._canonical_json_sha256(selected_records)
    target_record_digest = q011b._canonical_json_sha256(target_record)
    parent_target_group = target_groups[PARENT_AGGREGATE_INDEX]
    parent_target_digest = q011b._canonical_json_sha256(list(parent_target_group))
    class_signature_upper = prod(
        comb(count + len(classes[group_index]) - 1, count)
        for group_index, count in enumerate(SELECTED_COUNTS)
    )
    individual_monomial_upper = prod(
        comb(count + len(selected_groups[group_index]) - 1, count)
        for group_index, count in enumerate(SELECTED_COUNTS)
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
    generic_checks = base["checks"]
    first = artifacts["q011bx"]["cycle"][
        "degree_thirty_four_block_support_coalesced_sweep"
    ]["first_unresolved_witness"]
    source_frequencies = dict(sorted(Counter(first["source_identifiers"]).items()))
    checks = {
        "degree_thirty_four_inventory_recomputes_bitwise": bool(
            inventory["passed"] and inventory == stored_inventory
        ),
        "generic_exact_disc_primitives_reconstruct": bool(
            generic_checks["q011k_centers_and_q011ak_block_radii_reconstruct"]
            and generic_checks["all_two_hundred_four_q011ak_formulas_replay_exactly"]
            and generic_checks["q011ao_reused_modulus_records_are_bitwise_identical"]
            and generic_checks["selected_and_target_intervals_are_q011u_contained"]
            and generic_checks["envelope_records_are_finite_strict_json"]
        ),
        "registered_fifteen_class_partition_reproduces": bool(
            tuple(map(len, classes)) == EXPECTED_CLASS_COUNTS
            and class_digest == EXPECTED_CLASS_RECORD_DIGEST
            and tuple(map(len, merged_classes)) == (1, 1, 2, 2)
            and coalescing["passed"]
            and coalescing["hull_record_digest_sha256"]
            == stored_envelope["source_hull_record_digest_sha256"]
            and coalescing["merged_class_membership_digest_sha256"]
            == stored_envelope["source_merged_membership_digest_sha256"]
        ),
        "selected_and_target_records_reproduce": bool(
            len(selected_identifiers) == EXPECTED_SELECTED_IDENTIFIER_COUNT
            and selected_identifier_digest == EXPECTED_SELECTED_IDENTIFIER_DIGEST
            and selected_record_digest == EXPECTED_SELECTED_RECORD_DIGEST
            and target_record_digest == EXPECTED_TARGET_RECORD_DIGEST
            and records_by_identifier[TARGET_IDENTIFIER] == target_record
        ),
        "parent_aggregate_target_membership_reproduces": bool(
            tuple(overlap_counts[PARENT_AGGREGATE_INDEX]) == SELECTED_COUNTS
            and tuple(external_indices[PARENT_AGGREGATE_INDEX])
            == PARENT_EXTERNAL_GROUP_INDICES
            and len(parent_target_group) == EXPECTED_PARENT_TARGET_COUNT
            and TARGET_IDENTIFIER in parent_target_group
            and parent_target_digest == EXPECTED_PARENT_TARGET_GROUP_DIGEST
        ),
        "first_witness_source_assignment_reproduces": source_frequencies
        == EXPECTED_SOURCE_FREQUENCIES,
        "original_classes_are_contained_in_registered_merged_hulls": (
            all_original_discs_contained
        ),
        "registered_combinatorial_bounds_reproduce": bool(
            class_signature_upper == EXPECTED_CLASS_SIGNATURE_UPPER
            and individual_monomial_upper == EXPECTED_INDIVIDUAL_MONOMIAL_UPPER
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
        "target_identifier": TARGET_IDENTIFIER,
        "parent_external_group_indices": list(PARENT_EXTERNAL_GROUP_INDICES),
        "parent_target_identifier_count": len(parent_target_group),
        "parent_target_group_digest_sha256": parent_target_digest,
        "selected_group_sizes": list(map(len, selected_groups)),
        "uncoalesced_class_counts": list(map(len, classes)),
        "uncoalesced_class_memberships": class_record,
        "uncoalesced_class_membership_digest_sha256": class_digest,
        "selected_identifier_digest_sha256": selected_identifier_digest,
        "selected_record_digest_sha256": selected_record_digest,
        "target_record_digest_sha256": target_record_digest,
        "first_witness_source_frequencies": source_frequencies,
        "uncoalesced_class_signature_upper_bound": class_signature_upper,
        "individual_source_monomial_upper_bound": individual_monomial_upper,
        "other_parent_targets_recomputed": False,
        "second_q011bx_overlap_recomputed": False,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, classes, lookup, tuple(external_indices[PARENT_AGGREGATE_INDEX])


def _targeted_uncoalesced_sweep(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    parent_external_indices: tuple[int, ...],
) -> dict[str, Any]:
    pools = q011am._HierarchicalPools(classes, lookup)
    left = pools.pair_pool(0, SELECTED_COUNTS[0], 1, SELECTED_COUNTS[1])
    right = pools.pair_pool(2, SELECTED_COUNTS[2], 3, SELECTED_COUNTS[3])
    left_wave = np.stack([record.wave for record in left])
    right_wave = np.stack([record.wave for record in right])
    product_lower, product_upper = q011ag._product_bound_matrices(left, right)
    wave_matrix, crude_bound = q011ag._wave_matrix(left_wave, right_wave, 12)
    active = wave_matrix > 0
    target = lookup[TARGET_IDENTIFIER]
    product_below_gap = q011ag._down_subtract(
        q011ag._fraction_lower(target.modulus.lower), product_upper
    )
    target_below_gap = q011ag._down_subtract(
        product_lower, q011ag._fraction_upper(target.modulus.upper)
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
        left_index, right_index = map(int, np.unravel_index(flat_index, unresolved.shape))
        first_raw = {
            "aggregate_index": 0,
            "selected_type_counts": list(SELECTED_COUNTS),
            "target_identifier": TARGET_IDENTIFIER,
            "output_block": 12,
            "left_index": left_index,
            "right_index": right_index,
            "wave_multiplicity": int(wave_matrix[left_index, right_index]),
            "relation": "overlap",
            "class_counts": [
                list(group)
                for group in q011ag._signature_counts(left, right, left_index, right_index)
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
        left_index, right_index = map(int, np.unravel_index(flat_index, candidates.shape))
        gap = float(candidates[left_index, right_index])
        key = (gap, TARGET_IDENTIFIER, left_index, right_index)
        raw = {
            "aggregate_index": 0,
            "selected_type_counts": list(SELECTED_COUNTS),
            "target_identifier": TARGET_IDENTIFIER,
            "output_block": 12,
            "left_index": left_index,
            "right_index": right_index,
            "wave_multiplicity": int(wave_matrix[left_index, right_index]),
            "relation": relation,
            "class_counts": [
                list(group)
                for group in q011ag._signature_counts(left, right, left_index, right_index)
            ],
            "outward_gap": gap,
        }
        if minimum is None or key < minimum[0]:
            minimum = (key, raw)

    first_witness = q011am._exact_witness(classes, lookup, first_raw) if first_raw else None
    minimum_witness = (
        q011am._exact_witness(classes, lookup, minimum[1]) if minimum is not None else None
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
    aggregate_record = {
        "aggregate_index": 0,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "external_group_indices": list(parent_external_indices),
        "target_identifier_count": 1,
        "original_monomial_count": original_monomials,
        "modulus_signature_count": signature_count,
        "compatible_modulus_signature_count": int(active.sum()),
        "compatible_original_monomial_count": int(wave_matrix[active].sum()),
        "weighted_comparison_count": int(wave_matrix[active].sum()),
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
            "output_block": 12,
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
            "output_block": 12,
            "target_identifier": TARGET_IDENTIFIER,
            "shape": list(codes.shape),
            "classification_sha256": q011b._array_sha256(codes),
        }
    ]
    sweep = {
        "degree": DEGREE,
        "audited_overlap_aggregate_count": 1,
        "fully_separated_overlap_aggregate_count": int(not unresolved.any()),
        "remaining_overlap_aggregate_count": int(unresolved.any()),
        "remaining_overlap_aggregate_indices": [0] if unresolved.any() else [],
        "original_monomial_count": original_monomials,
        "modulus_signature_count": signature_count,
        "compatible_modulus_signature_count": int(active.sum()),
        "compatible_original_monomial_count": int(wave_matrix[active].sum()),
        "weighted_comparison_count": int(wave_matrix[active].sum()),
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
        "streaming_contract": {
            "full_degree_thirty_four_monomial_list_retained": False,
            "full_classification_matrices_retained": False,
            "aggregate_summary_count": 1,
            "peak_live_combined_signature_count": signature_count,
            "hierarchical_class_power_cache_count": len(power_records),
            "group_pool_cache_count": len(pools.group_cache),
            "pair_pool_cache_count": len(pools.pair_cache),
        },
    }
    sweep["degree"] = DEGREE
    sweep["local_aggregate_index"] = 0
    sweep["parent_q011bx_aggregate_index"] = PARENT_AGGREGATE_INDEX
    minimum = sweep["global_minimum_separated_witness"]
    first_overlap = sweep["first_unresolved_witness"]
    exclusive_count = sum(sweep["distinct_relation_counts"].values())
    checks = {
        "one_registered_parent_relation_is_processed": bool(
            sweep["audited_overlap_aggregate_count"] == 1
            and len(sweep["aggregate_records"]) == 1
            and sweep["aggregate_records"][0]["selected_type_counts"]
            == list(SELECTED_COUNTS)
            and sweep["aggregate_records"][0]["target_identifier_count"] == 1
        ),
        "registered_signature_and_monomial_counts_reproduce": bool(
            sweep["modulus_signature_count"] == EXPECTED_CLASS_SIGNATURE_UPPER
            and sweep["original_monomial_count"] == EXPECTED_INDIVIDUAL_MONOMIAL_UPPER
        ),
        "all_integer_and_outward_interval_invariants_hold": bool(
            sweep["all_convolutions_nonnegative"]
            and sweep["all_convolution_fiber_sums_exact"]
            and sweep["all_product_bound_arrays_are_finite"]
            and sweep["all_product_bound_arrays_are_nonnegative_and_ordered"]
            and sweep["all_original_monomial_counts_match_multiset_coefficients"]
            and sweep["all_modulus_signature_counts_match_weak_compositions"]
            and sweep["maximum_fourier_crude_int64_bound"] < 2**63
            and sweep["maximum_convolution_crude_int64_bound"] < 2**63
        ),
        "classification_is_exclusive_and_complete": bool(
            exclusive_count == sweep["distinct_comparison_count"]
            and sum(sweep["weighted_relation_counts"].values())
            == sweep["weighted_comparison_count"]
        ),
        "stream_summaries_and_witness_protocol_are_present": bool(
            sweep["bound_matrix_record_count"] == 1
            and sweep["coefficient_matrix_record_count"] == 1
            and sweep["classification_matrix_record_count"] == 1
            and (minimum is not None or separated_count == 0)
            and (first_overlap is None or first_overlap["relation"] == "overlap")
        ),
        "targeted_sweep_is_finite_strict_json": bool(
            _all_numeric_values_finite(sweep)
            and _strict_json_serializable(sweep)
            and json.dumps(sweep, allow_nan=False)
        ),
    }
    return {**sweep, "registered_checks": checks, "registered_passed": all(checks.values())}


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "target_identifier": TARGET_IDENTIFIER,
        "source_partition_change": "six merged hulls to fifteen registered blockwise classes",
        "other_parent_targets_recomputed": False,
        "second_q011bx_overlap_recomputed": False,
        "target_folding_used": False,
        "post_observation_class_split_used": False,
        "full_monomial_list_retained": False,
        "full_classification_matrices_retained": False,
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


def run_degree_thirty_four_first_overlap_refinement() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    fixed, classes, lookup, parent_external_indices = _fixed_refinement_input_audit(artifacts)
    sweep = _targeted_uncoalesced_sweep(classes, lookup, parent_external_indices)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    refinement_sections = {"fixed_uncoalesced_refinement_input_audit": fixed}
    sweep_sections = {"targeted_uncoalesced_blockwise_sweep": sweep}
    input_digest = q011b._canonical_json_sha256(input_sections)
    refinement_digest = q011b._canonical_json_sha256(refinement_sections)
    sweep_digest = q011b._canonical_json_sha256(sweep_sections)
    minimum = sweep["global_minimum_separated_witness"]
    first_overlap = sweep["first_unresolved_witness"]
    minimum_outward_positive = bool(
        minimum and minimum["relation"] != "overlap" and minimum["outward_gap_lower"]["float"] > 0
    )
    minimum_exact_positive = bool(
        minimum and minimum["relation"] != "overlap" and q011z._fraction(minimum["exact_gap"]) > 0
    )
    validity_gates = {
        "q011bx_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "55 artifacts and 261 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_q011bx_first_witness_reproduces": {
            "passed": sealed["checks"]["q011bx_first_witness_identity_reproduces"],
            "threshold": "aggregate 972 first exact overlap witness and digest",
            "value": sealed["q011bx"]["first_unresolved_witness"]["witness_digest_sha256"],
        },
        "registered_fifteen_class_partition_and_records_reproduce": {
            "passed": fixed["passed"],
            "threshold": "24 selected records, one target and fifteen classes",
            "value": fixed["checks"],
        },
        "original_classes_are_contained_and_target_is_unchanged": {
            "passed": bool(
                fixed["checks"][
                    "original_classes_are_contained_in_registered_merged_hulls"
                ]
                and fixed["checks"]["selected_and_target_records_reproduce"]
            ),
            "threshold": "source refinement narrows hulls without changing target disc",
            "value": {
                "selected_record": fixed["selected_record_digest_sha256"],
                "target_record": fixed["target_record_digest_sha256"],
            },
        },
        "registered_combinatorial_work_bounds_reproduce": {
            "passed": fixed["checks"]["registered_combinatorial_bounds_reproduce"],
            "threshold": "9800 class signatures and 26796000 individual-source monomials",
            "value": {
                "signatures": fixed["uncoalesced_class_signature_upper_bound"],
                "monomials": fixed["individual_source_monomial_upper_bound"],
            },
        },
        "targeted_integer_outward_and_classification_invariants_pass": {
            "passed": sweep["registered_passed"],
            "threshold": "one target, exact convolutions and exclusive outward classifications",
            "value": sweep["registered_checks"],
        },
        "strict_section_digests_witness_and_runner_provenance_reproduce": {
            "passed": bool(
                len(input_digest) == len(refinement_digest) == len(sweep_digest) == 64
                and runner["filename"] == "q011by_degree34_first_overlap_refinement.py"
                and (
                    minimum is not None
                    or not sweep["separated_comparison_exists"]
                )
                and (first_overlap is None or first_overlap["relation"] == "overlap")
            ),
            "threshold": (
                "three section digests, exact overlap/separation witness protocol and "
                "runner metadata"
            ),
            "value": {
                "input": input_digest,
                "refinement": refinement_digest,
                "sweep": sweep_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    overlap_count = sweep["distinct_relation_counts"]["overlap"]
    diagnostic_gates = {
        "only_the_registered_first_relation_is_refined": {
            "passed": bool(
                fixed["parent_aggregate_index"] == PARENT_AGGREGATE_INDEX
                and fixed["target_identifier"] == TARGET_IDENTIFIER
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["second_q011bx_overlap_recomputed"]
            ),
            "threshold": "aggregate 972 and target block=12;center=124 only",
            "value": fixed,
        },
        "every_uncoalesced_subclass_comparison_is_strict": {
            "passed": overlap_count == 0,
            "threshold": "distinct overlap count equals zero",
            "value": sweep["distinct_relation_counts"],
        },
        "global_minimum_outward_and_exact_gaps_are_positive": {
            "passed": minimum_outward_positive and minimum_exact_positive,
            "threshold": "strictly positive outward and exact rational minimum gap",
            "value": {
                "outward": minimum.get("outward_gap_lower") if minimum else None,
                "exact_gap_hex": minimum.get("exact_gap_hex") if minimum else None,
            },
        },
        "q011bx_rejection_and_scientific_boundary_are_preserved": {
            "passed": True,
            "threshold": "no degree-34 certification or actual-resonance claim",
            "value": "certified 2--33 and 91+, missing 34--90",
        },
    }
    resolved = validity_passed and overlap_count == 0 and minimum_outward_positive and minimum_exact_positive
    persistent = validity_passed and overlap_count > 0
    refinement_outcome = "resolved" if resolved else "persistent" if persistent else "inconclusive"
    classification = (
        RESOLVED_CLASSIFICATION
        if resolved
        else PERSISTENT_CLASSIFICATION
        if persistent
        else INCONCLUSIVE_CLASSIFICATION
    )
    cycle = {
        "question": (
            "Does the registered fifteen-class blockwise source refinement strictly separate "
            "the first Q011bx overlap relation without changing its target disc?"
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
        "actual_resonance_outcome": "not_established",
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "first_q011bx_overlap_is_resolved_by_registered_partition": resolved,
        "first_q011bx_overlap_persists_under_registered_partition": persistent,
        "q011bx_degree_thirty_four_sufficient_certificate_remains_rejected": True,
        "degree_thirty_four_external_nonresonance_is_certified": False,
        "an_actual_degree_thirty_four_external_resonance_is_established": False,
        "certified_external_nonresonance_degrees": list(range(2, 34)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(34, 91)),
        "second_q011bx_overlap_is_audited": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This diagnostic concerns only Q011bx parent aggregate 972, selected counts "
        "[4,27,3,0], target block=12;center=124 and the registered fifteen-class "
        "blockwise source partition for the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf. It does not re-audit the other twenty-three parent targets or "
        "the second Q011bx overlap. It leaves the Q011bx rejection, certified degrees "
        "2--33 and 91+, and missing degrees 34--90 unchanged, and makes no claim about an "
        "actual resonance, degree-34 nonresonance, all-order nonresonance, higher graph "
        "smoothness, SSM existence or uniqueness, normal attraction, a basin, other grids, "
        "forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011bz to refine only Q011bx parent aggregate 2340, the second "
        "unresolved aggregate."
        if resolved
        else "Preregister Q011bz to split only the first persistent uncoalesced witness "
        "into individual source discs."
        if persistent
        else "Repair only the first Q011by validity failure before changing the partition."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011by cycle failed strict serialization or digest")
    return cycle


def run_q011by_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_first_overlap_refinement()
    sweep = cycle["targeted_uncoalesced_blockwise_sweep"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "fifteen exact registered blockwise classes",
            "product_enclosure": "outward-rounded binary64 hierarchical products",
            "fourier_multiplicity": "exact int64 cyclic convolution",
            "target_comparisons": "one fixed target disc without folding",
            "full_monomial_list_retained": False,
            "full_classification_matrices_retained": False,
            "convolution_call_count": sweep["convolution_call_count"],
            "peak_live_signature_count": sweep["maximum_live_combined_signature_count"],
        },
        "mathematical_scope": {
            "diagnostic": "degree-34 first-overlap uncoalesced blockwise refinement",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "target_identifier": TARGET_IDENTIFIER,
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
    result = run_q011by_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
