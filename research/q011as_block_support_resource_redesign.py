"""Q011as block-support hull coalescing resource redesign audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011ar_degree19_resource_estimate as q011ar
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011aq = q011ar.q011aq
q011ap = q011ar.q011ap
q011an = q011ap.q011ao.q011an
q011b = q011ar.q011b
q011z = q011ar.q011z

SIZE = 17
DEGREE = 19

EXPECTED_OLD_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_MERGED_CLASS_COUNTS = (1, 1, 2, 2)
EXPECTED_MERGED_CLASS_RECORD_COUNT = 6
EXPECTED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_TARGET_IDENTIFIER_COUNT = 160
EXPECTED_HULL_RECORD_DIGEST = "f54f1a1f70d953b4c1255e9f9627d7ca43229a3d1e26c11b716d23fd56ea1eb6"
EXPECTED_MERGED_MEMBERSHIP_DIGEST = (
    "975ebf1077279cbfcc6fd46e5a34fcd67260ff953a718eb51985794314fcd8b8"
)
EXPECTED_MAXIMUM_WIDTH_INFLATION_FLOAT = 1.195361864035176

EXPECTED_DEGREE_EIGHTEEN_AGGREGATE_COUNT = 1_330
EXPECTED_DEGREE_EIGHTEEN_OLD_SEPARATED_COUNT = 1_078
EXPECTED_DEGREE_EIGHTEEN_DIRECT_COUNT = 252
EXPECTED_D18_ORIGINAL_MONOMIAL_COUNT = 50_931_347_136
EXPECTED_D18_MODULUS_SIGNATURE_COUNT = 6_075
EXPECTED_D18_COMPATIBLE_SIGNATURE_COUNT = 5_624
EXPECTED_D18_COMPATIBLE_MONOMIAL_COUNT = 12_958_923_958
EXPECTED_D18_WEIGHTED_COMPARISON_COUNT = 29_855_319_268
EXPECTED_D18_DISTINCT_COMPARISON_COUNT = 43_852
EXPECTED_D18_WEIGHTED_RELATIONS = {
    "overlap": 0,
    "product_below_target": 13_265_995_204,
    "target_below_product": 16_589_324_064,
}
EXPECTED_D18_DISTINCT_RELATIONS = {
    "overlap": 0,
    "product_below_target": 16_052,
    "target_below_product": 27_800,
}
EXPECTED_D18_AGGREGATE_DIGEST = "4271488242a182334f98b4feb09e1412713188a4d33eeec2b96affab872fd25f"
EXPECTED_D18_CLASS_POWER_COUNT = 101
EXPECTED_D18_CLASS_POWER_DIGEST = "cf851eb0cac9980e2b16492eae42b76b60ba20cddbbc2b768b182bc604f5add7"
EXPECTED_D18_GROUP_SIGNATURE_COUNT = 357
EXPECTED_D18_GROUP_SIGNATURE_DIGEST = (
    "fde3cced34e80b67ae59000672277a76d61ddd1162f9e42d3efc28cf9f992645"
)
EXPECTED_D18_PAIR_POOL_COUNT = 125
EXPECTED_D18_PAIR_POOL_DIGEST = "9cd018d7219fb1c277a84f59a81041ff14e5a393defc834283b02254bfe7c163"
EXPECTED_D18_BOUND_DIGEST = "74fc0328e9b81323cbf198cf8f28e4b537061f1280c938e8dc0242d51caecd61"
EXPECTED_D18_COEFFICIENT_DIGEST = (
    "cbfce79b2fa3a8e7122b0d78d79e30a8546dd0b5fb7a9eb04eb35b174eccfdd6"
)
EXPECTED_D18_CLASSIFICATION_DIGEST = (
    "dbe334676778f799ac428cffd40ab16dc1a510e311d9f8d20725035edb4beded"
)
EXPECTED_D18_PEAK_SIGNATURE_COUNT = 84
EXPECTED_D18_CONVOLUTION_COUNT = 3_001
EXPECTED_D18_MINIMUM_OUTWARD_HEX = "0x1.39c56bbbfffffp-23"
EXPECTED_D18_MINIMUM_EXACT_HEX = "0x1.39c56ce0be4a4p-23"
EXPECTED_D18_MINIMUM_WITNESS_DIGEST = (
    "9e7f6b4014a2082bf716ffe6b20b20311f50e079625d235ab73f879a6337bb28"
)

EXPECTED_CLASS_POWER_COUNT = 102
EXPECTED_CLASS_POWER_KEY_DIGEST = (
    "2c68abef66862131e1c334bd36f6354a82ea36a6027faba4c2274fd2409d450c"
)
EXPECTED_GROUP_POOL_KEY_COUNT = 66
EXPECTED_GROUP_POOL_KEY_DIGEST = (
    "8749302ce7d5e76cf4f6e2080f18b8747c74c4c5c336d33fd4d163fb101dc1d1"
)
EXPECTED_PAIR_POOL_KEY_COUNT = 140
EXPECTED_PAIR_POOL_KEY_DIGEST = (
    "343b3ff58a70c485ce89830ff12f4a501ca8c122525f8a25b5bbe0e2531b0d68"
)
EXPECTED_GROUP_SIGNATURE_COUNT = 372
EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT = 3_163
EXPECTED_CONVOLUTION_CALL_COUNT = 3_877
EXPECTED_MODULUS_SIGNATURE_COUNT = 8_056
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 90
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 1_440
EXPECTED_ORIGINAL_MONOMIAL_COUNT = 107_797_786_672
EXPECTED_MAXIMUM_AGGREGATE_MONOMIAL_COUNT = 2_038_608_000
EXPECTED_SAFE_INT64_CRUDE_BOUND = 34_656_336_000
EXPECTED_DISTINCT_COMPARISON_UPPER_BOUND = 80_256
EXPECTED_WEIGHTED_COMPARISON_UPPER_BOUND = 1_124_800_752_224
EXPECTED_RESOURCE_RECORD_DIGEST = (
    "aea8bd1f3bf0dceabb1cf4ba020a066e7d85fb4ae8f8c3857d3b69abac729233"
)
EXPECTED_DOUBLE_SAFETY_SECONDS = Fraction(1_342_185_669, 18_045_245_000)
EXPECTED_PROCESS_MEMORY_SAFETY_BYTES = 183_970

RESOURCE_LIMITS = dict(q011ar.RESOURCE_LIMITS)
GO_DECISION = "go_for_degree_nineteen_coalesced_preregistration"
STOP_DECISION = "stop_before_degree_nineteen_coalesced_full_sweep"
INCONCLUSIVE_DECISION = "inconclusive_resource_redesign"
SCIENTIFIC_OUTCOME = "not_evaluated"
ACTUAL_RESONANCE_OUTCOME = "not_evaluated"

Q011AR_ARTIFACT_SHA256 = "8e0f2cca4c4db357587595ba315aa4fa84121c358e988f4cdcadc8720621e67a"
Q011AR_RUNNER_SHA256 = "4a3faebafd0404f449e1410e98a25bce659a2c4c80c641bdbd642bbd487443aa"
Q011AR_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "envelope_digest_sha256",
    "resource_digest_sha256",
    "result_digest_sha256",
)
Q011AR_DIGESTS = (
    "2be0835736f234a9df83af63fd836aca5196eb6b4e8c54dc86d72723b7b995f6",
    "9fd64f430ca0f5231e97ec13338aaaf037909d35c2e5a294ed6246d4f87f8848",
    "b33a4d036c244ed17fb5b708307759883439eef6172e473303fc4ea726c0a70c",
    "c93fb9cb96a91474cbba67aad1b12ad699fd189c537a4ac54305a1b3daf0f328",
    "2823bb2101e57bfd277e18e621c17ef850488ec5743083a10f8246e5e61d8f27",
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


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011ar._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ar_degree19_resource_estimate.json"
    runner_path = Path(q011ar.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AR_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    checks = {
        "q011ar_twenty_two_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 112
            and len(artifacts) == 22
            and all(prior["checks"].values())
        ),
        "q011ar_artifact_sha256_matches": _file_sha256(artifact_path)
        == Q011AR_ARTIFACT_SHA256,
        "q011ar_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AR_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AR_RUNNER_SHA256
        ),
        "q011ar_digests_match": digests == Q011AR_DIGESTS,
        "q011ar_registered_stop_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["resource_decision"] == q011ar.STOP_DECISION
            and artifact["scientific_outcome"] == q011ar.SCIENTIFIC_OUTCOME
            and artifact["actual_resonance_outcome"] == q011ar.ACTUAL_RESONANCE_OUTCOME
            and cycle["failed_validity_order"] == []
            and len(cycle["failed_resource_limit_order"]) == 6
            and theorem["q011aq_degree_eighteen_certificate_is_preserved"]
            and theorem["missing_external_nonresonance_degrees"] == list(range(19, 91))
        ),
        "q011ar_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ar_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ar_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_hundred_seventeen_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 117
        ),
    }
    artifacts["q011ar"] = artifact
    return (
        {
            "prior_q011ar_sealed_input_audit": prior,
            "q011ar": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AR_DIGEST_NAMES),
                "digests": list(digests),
                "resource_decision": cycle["resource_decision"],
                "scientific_outcome": cycle["scientific_outcome"],
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _support_key(identifiers: tuple[str, ...]) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted(Counter(q011z._identifier_indices(identifier)[0] for identifier in identifiers).items())
    )


def _coalesce_classes(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> tuple[
    dict[str, Any],
    tuple[tuple[tuple[str, ...], ...], ...],
    dict[str, q011z._UniformDisc],
]:
    merged_classes: list[tuple[tuple[str, ...], ...]] = []
    hull_lookup = dict(lookup)
    hull_records: list[dict[str, Any]] = []
    support_partition_exact = True
    containment = True
    selected_identifiers = set().union(
        *(set(identifiers) for group in classes for identifiers in group)
    )
    for group_index, group_classes in enumerate(classes):
        buckets: dict[tuple[tuple[int, int], ...], list[tuple[int, tuple[str, ...]]]] = (
            defaultdict(list)
        )
        for class_index, identifiers in enumerate(group_classes):
            buckets[_support_key(identifiers)].append((class_index, identifiers))
        merged_group: list[tuple[str, ...]] = []
        for merged_index, (support, members) in enumerate(sorted(buckets.items())):
            identifiers = tuple(
                sorted(identifier for _index, old_class in members for identifier in old_class)
            )
            discs = [lookup[identifier] for identifier in identifiers]
            center = RationalInterval(
                min(disc.center_modulus.lower for disc in discs),
                max(disc.center_modulus.upper for disc in discs),
            )
            modulus = RationalInterval(
                min(disc.modulus.lower for disc in discs),
                max(disc.modulus.upper for disc in discs),
            )
            old_widths = [
                lookup[old_class[0]].modulus.upper - lookup[old_class[0]].modulus.lower
                for _index, old_class in members
            ]
            maximum_old_width = max(old_widths)
            merged_width = modulus.upper - modulus.lower
            for class_index, old_class in members:
                support_partition_exact = bool(
                    support_partition_exact and _support_key(old_class) == support
                )
                del class_index
            for identifier in identifiers:
                old = lookup[identifier]
                containment = bool(
                    containment
                    and center.lower <= old.center_modulus.lower
                    and center.upper >= old.center_modulus.upper
                    and modulus.lower <= old.modulus.lower
                    and modulus.upper >= old.modulus.upper
                )
                hull_lookup[identifier] = q011z._UniformDisc(
                    identifier=identifier,
                    block_index=old.block_index,
                    center_index=old.center_index,
                    center_modulus=center,
                    modulus=modulus,
                )
            merged_group.append(identifiers)
            hull_records.append(
                {
                    "selected_group_index": group_index,
                    "merged_class_index": merged_index,
                    "per_old_class_block_support": [list(item) for item in support],
                    "old_class_indices": [class_index for class_index, _old in members],
                    "old_class_count": len(members),
                    "identifiers": list(identifiers),
                    "identifier_count": len(identifiers),
                    "center_modulus_lower": q011z._exact_fraction_record(center.lower),
                    "center_modulus_upper": q011z._exact_fraction_record(center.upper),
                    "modulus_lower": q011z._exact_fraction_record(modulus.lower),
                    "modulus_upper": q011z._exact_fraction_record(modulus.upper),
                    "maximum_original_modulus_width": q011z._exact_fraction_record(
                        maximum_old_width
                    ),
                    "merged_modulus_width": q011z._exact_fraction_record(merged_width),
                    "width_inflation_ratio": _fraction_record(
                        merged_width / maximum_old_width
                    ),
                }
            )
        merged_classes.append(tuple(merged_group))
    merged = tuple(merged_classes)
    merged_identifiers = [
        identifier for group in merged for identifiers in group for identifier in identifiers
    ]
    hull_digest = q011b._canonical_json_sha256(hull_records)
    membership_digest = q011b._canonical_json_sha256(
        [[list(identifiers) for identifiers in group] for group in merged]
    )
    maximum_inflation = max(
        record["width_inflation_ratio"]["float"] for record in hull_records
    )
    checks = {
        "registered_old_and_merged_class_counts_reproduce": bool(
            tuple(map(len, classes)) == EXPECTED_OLD_CLASS_COUNTS
            and tuple(map(len, merged)) == EXPECTED_MERGED_CLASS_COUNTS
        ),
        "support_key_partition_is_deterministic": support_partition_exact,
        "selected_identifier_partition_is_exact": bool(
            len(merged_identifiers) == len(set(merged_identifiers))
            == EXPECTED_SELECTED_IDENTIFIER_COUNT
            and set(merged_identifiers) == selected_identifiers
        ),
        "every_old_disc_is_contained_in_its_exact_hull": containment,
        "registered_hull_and_membership_digests_reproduce": bool(
            len(hull_records) == EXPECTED_MERGED_CLASS_RECORD_COUNT
            and hull_digest == EXPECTED_HULL_RECORD_DIGEST
            and membership_digest == EXPECTED_MERGED_MEMBERSHIP_DIGEST
            and maximum_inflation == EXPECTED_MAXIMUM_WIDTH_INFLATION_FLOAT
        ),
        "hull_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(hull_records)
            and _strict_json_serializable(hull_records)
            and json.dumps(hull_records, allow_nan=False)
        ),
    }
    audit = {
        "old_class_counts": list(map(len, classes)),
        "merged_class_counts": list(map(len, merged)),
        "selected_identifier_count": len(merged_identifiers),
        "merged_class_record_count": len(hull_records),
        "hull_records": hull_records,
        "hull_record_digest_sha256": hull_digest,
        "merged_class_memberships": [
            [list(identifiers) for identifiers in group] for group in merged
        ],
        "merged_class_membership_digest_sha256": membership_digest,
        "maximum_width_inflation_ratio": maximum_inflation,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, merged, hull_lookup


def _degree_nineteen_coalescing_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[tuple[tuple[str, ...], ...], ...],
    dict[str, q011z._UniformDisc],
    tuple[tuple[str, ...], ...],
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
    ) = q011ar._degree_nineteen_inventory_audit(artifacts)
    envelope, lookup, classes = q011ar._degree_nineteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    coalescing, merged, hull_lookup = _coalesce_classes(classes, lookup)
    selected_identifiers = set().union(*map(set, selected_groups))
    target_identifiers = set().union(*map(set, target_groups))
    target_unchanged = all(hull_lookup[identifier] == lookup[identifier] for identifier in target_identifiers)
    checks = {
        "q011ar_degree_nineteen_inventory_reconstructs": inventory["passed"],
        "q011ar_degree_nineteen_envelope_reconstructs": envelope["passed"],
        "registered_block_support_coalescing_reconstructs": coalescing["passed"],
        "source_and_target_identifier_partition_is_preserved": bool(
            len(selected_identifiers) == EXPECTED_SELECTED_IDENTIFIER_COUNT
            and len(target_identifiers) == EXPECTED_TARGET_IDENTIFIER_COUNT
            and not (selected_identifiers & target_identifiers)
            and target_unchanged
        ),
        "degree_nineteen_relations_are_not_evaluated": True,
    }
    audit = {
        "degree": DEGREE,
        "degree_aggregate_count": inventory["degree_aggregate_count"],
        "old_modulus_separated_aggregate_count": inventory[
            "old_modulus_separated_aggregate_count"
        ],
        "direct_overlap_aggregate_count": inventory["old_modulus_overlap_aggregate_count"],
        "inventory_digest_sha256": inventory["exact_inventory_digest_sha256"],
        "envelope_digest_sha256": envelope["final_disc_record_digest_sha256"],
        "target_identifier_count": len(target_identifiers),
        "target_lookup_changed": not target_unchanged,
        "product_target_relation_evaluation_count": 0,
        "block_support_hull_coalescing_audit": coalescing,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        merged,
        hull_lookup,
        selected_groups,
        overlap_counts,
        external_indices,
        target_groups,
    )


def _degree_eighteen_regression_audit(
    artifacts: dict[str, dict[str, Any]],
    degree_nineteen_coalescing: dict[str, Any],
) -> dict[str, Any]:
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        external_indices,
        target_groups,
    ) = q011ap._degree_eighteen_inventory_audit(artifacts)
    envelope, lookup, classes = q011ap._degree_eighteen_envelope_inventory_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    coalescing, merged, hull_lookup = _coalesce_classes(classes, lookup)
    sweep = dict(
        q011an._full_component_safe_sweep(
            merged, hull_lookup, overlap_counts, external_indices, target_groups
        )
    )
    sweep["degree"] = 18
    minimum = sweep["global_minimum_separated_witness"]
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
        "degree_eighteen_inputs_and_same_coalescing_reconstruct": bool(
            inventory["passed"]
            and envelope["passed"]
            and coalescing["passed"]
            and coalescing["hull_records"]
            == degree_nineteen_coalescing["block_support_hull_coalescing_audit"][
                "hull_records"
            ]
            and coalescing["merged_class_memberships"]
            == degree_nineteen_coalescing["block_support_hull_coalescing_audit"][
                "merged_class_memberships"
            ]
        ),
        "registered_degree_eighteen_workload_reproduces": bool(
            sweep["original_monomial_count"] == EXPECTED_D18_ORIGINAL_MONOMIAL_COUNT
            and sweep["modulus_signature_count"] == EXPECTED_D18_MODULUS_SIGNATURE_COUNT
            and sweep["compatible_modulus_signature_count"]
            == EXPECTED_D18_COMPATIBLE_SIGNATURE_COUNT
            and sweep["compatible_original_monomial_count"]
            == EXPECTED_D18_COMPATIBLE_MONOMIAL_COUNT
            and sweep["weighted_comparison_count"] == EXPECTED_D18_WEIGHTED_COMPARISON_COUNT
            and sweep["distinct_comparison_count"] == EXPECTED_D18_DISTINCT_COMPARISON_COUNT
        ),
        "all_degree_eighteen_relations_remain_separated": bool(
            sweep["audited_overlap_aggregate_count"] == EXPECTED_DEGREE_EIGHTEEN_DIRECT_COUNT
            and sweep["fully_separated_overlap_aggregate_count"]
            == EXPECTED_DEGREE_EIGHTEEN_DIRECT_COUNT
            and sweep["remaining_overlap_aggregate_count"] == 0
            and sweep["first_unresolved_witness"] is None
            and sweep["weighted_relation_counts"] == EXPECTED_D18_WEIGHTED_RELATIONS
            and sweep["distinct_relation_counts"] == EXPECTED_D18_DISTINCT_RELATIONS
            and EXPECTED_DEGREE_EIGHTEEN_OLD_SEPARATED_COUNT
            + sweep["fully_separated_overlap_aggregate_count"]
            == EXPECTED_DEGREE_EIGHTEEN_AGGREGATE_COUNT
        ),
        "registered_degree_eighteen_factorization_digests_reproduce": bool(
            sweep["aggregate_record_digest_sha256"] == EXPECTED_D18_AGGREGATE_DIGEST
            and sweep["class_power_record_count"] == EXPECTED_D18_CLASS_POWER_COUNT
            and sweep["class_power_record_digest_sha256"] == EXPECTED_D18_CLASS_POWER_DIGEST
            and sweep["group_signature_record_count"] == EXPECTED_D18_GROUP_SIGNATURE_COUNT
            and sweep["group_signature_digest_sha256"]
            == EXPECTED_D18_GROUP_SIGNATURE_DIGEST
            and sweep["pair_pool_record_count"] == EXPECTED_D18_PAIR_POOL_COUNT
            and sweep["pair_pool_record_digest_sha256"] == EXPECTED_D18_PAIR_POOL_DIGEST
        ),
        "registered_degree_eighteen_matrix_digests_reproduce": bool(
            sweep["bound_matrix_digest_sha256"] == EXPECTED_D18_BOUND_DIGEST
            and sweep["coefficient_matrix_digest_sha256"]
            == EXPECTED_D18_COEFFICIENT_DIGEST
            and sweep["classification_matrix_digest_sha256"]
            == EXPECTED_D18_CLASSIFICATION_DIGEST
        ),
        "registered_degree_eighteen_resources_and_invariants_reproduce": bool(
            sweep["maximum_live_combined_signature_count"]
            == EXPECTED_D18_PEAK_SIGNATURE_COUNT
            and sweep["convolution_call_count"] == EXPECTED_D18_CONVOLUTION_COUNT
            and all_invariants
        ),
        "registered_degree_eighteen_minimum_witness_reproduces": bool(
            minimum["outward_gap_lower"]["binary64_hex"]
            == EXPECTED_D18_MINIMUM_OUTWARD_HEX
            and minimum["exact_gap_hex"] == EXPECTED_D18_MINIMUM_EXACT_HEX
            and minimum["witness_digest_sha256"] == EXPECTED_D18_MINIMUM_WITNESS_DIGEST
        ),
        "degree_eighteen_regression_is_finite_strict_json": bool(
            _all_numeric_values_finite(sweep)
            and _strict_json_serializable(sweep)
            and json.dumps(sweep, allow_nan=False)
        ),
    }
    return {
        "known_certificate_degree": 18,
        "old_modulus_separated_aggregate_count": EXPECTED_DEGREE_EIGHTEEN_OLD_SEPARATED_COUNT,
        "direct_regression_sweep": sweep,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _degree_nineteen_resource_audit(
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
        "streaming_design_does_not_evaluate_degree_nineteen_relations": bool(
            not record["full_degree_nineteen_monomial_list_retained"]
            and not record["product_bound_matrix_constructed"]
            and not record["fourier_coefficient_matrix_constructed"]
            and not record["classification_matrix_constructed"]
            and record["product_target_relation_evaluation_count"] == 0
        ),
        "registered_variable_work_projection_reproduces": bool(
            projection["wall_time_double_safety_upper_seconds"]
            == _fraction_record(EXPECTED_DOUBLE_SAFETY_SECONDS)
            and projection["process_memory_one_point_five_safety_upper_bytes"]
            == EXPECTED_PROCESS_MEMORY_SAFETY_BYTES
            and not projection["projection_is_a_scientific_acceptance_threshold"]
        ),
        "q011ap_absolute_resource_limits_are_preserved": RESOURCE_LIMITS
        == q011ap.RESOURCE_LIMITS
        == q011ar.RESOURCE_LIMITS,
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
        "old_class_counts": list(EXPECTED_OLD_CLASS_COUNTS),
        "merged_class_counts": list(EXPECTED_MERGED_CLASS_COUNTS),
        "coalescing_key": "selected group plus exact wave-block multiplicity tuple",
        "source_hull": "exact rational endpoint min/max hull",
        "target_identifiers_merged_or_removed": False,
        "conjugate_target_folding_used": False,
        "degree_nineteen_relations_evaluated": False,
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
        "coalescing_digest_sha256": cycle["coalescing_digest_sha256"],
        "regression_digest_sha256": cycle["regression_digest_sha256"],
        "resource_digest_sha256": cycle["resource_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "resource_feasibility_gates": cycle["resource_feasibility_gates"],
        "study_validity": cycle["study_validity"],
        "resource_decision": cycle["resource_decision"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_block_support_resource_redesign_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        coalescing,
        merged_classes,
        _hull_lookup,
        selected_groups,
        overlap_counts,
        _external_indices,
        target_groups,
    ) = _degree_nineteen_coalescing_input_audit(artifacts)
    regression = _degree_eighteen_regression_audit(artifacts, coalescing)
    resource = _degree_nineteen_resource_audit(
        merged_classes, selected_groups, overlap_counts, target_groups
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    coalescing_sections = {"degree_nineteen_coalescing_input_audit": coalescing}
    regression_sections = {"degree_eighteen_coalesced_regression_audit": regression}
    resource_sections = {"degree_nineteen_coalesced_resource_audit": resource}
    input_digest = q011b._canonical_json_sha256(input_sections)
    coalescing_digest = q011b._canonical_json_sha256(coalescing_sections)
    regression_digest = q011b._canonical_json_sha256(regression_sections)
    resource_digest = q011b._canonical_json_sha256(resource_sections)
    validity_gates = {
        "q011ar_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "23 artifacts and 117 direct digests reproduce",
            "value": sealed["checks"],
        },
        "deterministic_block_support_hull_coalescing_reproduces": {
            "passed": coalescing["passed"],
            "threshold": "six hull classes contain all 24 selected discs and preserve targets",
            "value": coalescing["checks"],
        },
        "known_degree_eighteen_certificate_regression_passes": {
            "passed": regression["passed"],
            "threshold": "all 252 direct degree-18 aggregates remain strictly separated",
            "value": regression["checks"],
        },
        "degree_nineteen_design_only_resource_contract_reproduces": {
            "passed": resource["passed"],
            "threshold": "registered exact counts, unchanged limits and zero relations reproduce",
            "value": resource["checks"],
        },
        "strict_serialization_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(
                    len(digest) == 64
                    for digest in (
                        input_digest,
                        coalescing_digest,
                        regression_digest,
                        resource_digest,
                    )
                )
                and runner["filename"] == "q011as_block_support_resource_redesign.py"
            ),
            "threshold": "strict finite JSON, four section digests and runner metadata",
            "value": {
                "input": input_digest,
                "coalescing": coalescing_digest,
                "regression": regression_digest,
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
        "calibrated_double_wall_work_upper_is_within_limit": {
            "passed": projection["wall_time_double_safety_upper_seconds"]["float"]
            <= RESOURCE_LIMITS["wall_time_double_safety_upper_seconds"],
            "threshold": RESOURCE_LIMITS["wall_time_double_safety_upper_seconds"],
            "value": projection["wall_time_double_safety_upper_seconds"],
        },
        "calibrated_process_memory_variable_upper_is_within_limit": {
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
            "Does deterministic block-support source-disc hull coalescing preserve the "
            "known degree-eighteen certificate and fit every unchanged degree-nineteen "
            "resource limit without evaluating a degree-nineteen relation?"
        ),
        **input_sections,
        **coalescing_sections,
        **regression_sections,
        **resource_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "coalescing_digest_sha256": coalescing_digest,
        "regression_digest_sha256": regression_digest,
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
        "block_support_hull_coalescing_is_resource_supported_for_preregistration": decision
        == GO_DECISION,
        "known_degree_eighteen_certificate_is_preserved_by_regression": regression["passed"],
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
        "This redesign audit concerns deterministic selected-source block-support hull "
        "coalescing, a regression of the already certified degree-eighteen relations, and "
        "design-only degree-nineteen resource counts for the fixed 17x17 repaired exact map "
        "on one fixed conservation leaf. It keeps all degree-nineteen targets but constructs "
        "no degree-nineteen product-bound, Fourier coefficient or classification matrix and "
        "evaluates no degree-nineteen product-target relation. It therefore certifies no "
        "degree-nineteen external nonresonance, actual resonance, minimum gap, higher graph "
        "smoothness, SSM uniqueness, attraction or basin."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011aq_degree_eighteen_certificate_changed": False,
        "certified_degrees_two_through_eighteen_changed": False,
        "degree_91_and_higher_tail_changed": False,
        "q011ar_stop_for_the_uncoalesced_representation_changed": False,
    }
    cycle["next_change"] = (
        "Preregister the Q011at degree-nineteen block-support-coalesced full sweep before "
        "evaluating any degree-nineteen product-target relation."
        if decision == GO_DECISION
        else "Redesign only the first failed coalesced resource dimension before any "
        "degree-nineteen full sweep."
        if decision == STOP_DECISION
        else "Repair only the first Q011as validity failure before changing the redesign."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011as cycle failed strict serialization or digest")
    return cycle


def run_q011as_study() -> dict[str, Any]:
    cycle = run_block_support_resource_redesign_audit()
    resource = cycle["degree_nineteen_coalesced_resource_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "hull_arithmetic": "exact rational min/max endpoint hull",
            "degree_eighteen_regression_product_enclosure": (
                "outward-rounded binary64 with exact rational witness replay"
            ),
            "degree_nineteen_resource_arithmetic": (
                "exact integer combinatorics and rational variable-work projections"
            ),
            "degree_nineteen_product_enclosure": "not constructed",
            "degree_nineteen_fourier_coefficient_matrices": "not constructed",
            "degree_nineteen_relation_classification": "not evaluated",
            "exact_convolution_call_count_if_degree_nineteen_full_sweep_runs": resource[
                "exact_convolution_call_count"
            ],
            "peak_live_signature_count_if_degree_nineteen_full_sweep_runs": resource[
                "peak_live_combined_signature_count"
            ],
        },
        "mathematical_scope": {
            "diagnostic": "block-support hull coalescing resource redesign",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "design_degree": DEGREE,
            "known_regression_degree": 18,
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
    result = run_q011as_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
