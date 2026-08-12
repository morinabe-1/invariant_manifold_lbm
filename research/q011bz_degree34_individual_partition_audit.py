"""Q011bz individual-disc partition audit for the first Q011by witness."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011by_degree34_first_overlap_refinement as q011by
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ag = q011by.q011ag
q011b = q011by.q011b
q011z = q011by.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 972
TARGET_IDENTIFIER = "block=12;center=124"
OUTPUT_BLOCK = 12
PARENT_CLASS_COUNTS = (
    (0, 0, 0, 4),
    (0, 27),
    (0, 0, 3),
    (0, 0, 0, 0, 0, 0),
)
OCCUPIED_SPEC = ((0, 3, 4), (1, 1, 27), (2, 2, 3))
EXPECTED_IDENTIFIER_ORDER = (
    "block=16;center=145",
    "block=1;center=145",
    "block=16;center=151",
    "block=1;center=151",
    "block=16;center=152",
    "block=1;center=152",
)
EXPECTED_SOURCE_COUNTS = (4, 0, 24, 3, 0, 3)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 4, 8, 19, 3, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = (4, 0, 24, 3, 0, 3)
EXPECTED_PARENT_ALLOCATION_INDEX = 544
EXPECTED_ALLOCATION_COUNT = 560
EXPECTED_COMPATIBLE_COUNT = 39

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = (
    "87f8ae203a204ffc825fee77ebaf24df993a7e50ac10886aa907322591f33a57"
)
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "56c6c30ea98827b3c8f8f71454333e46856e37546fe3b280e314ab646c13c143"
)
EXPECTED_ALLOCATION_DIGEST = (
    "dff3c7109b0970d2628a74fb13c6ec0fb9eb243d569f83f6403219cec8be2eba"
)
EXPECTED_COMPATIBLE_DIGEST = (
    "6bfa283ad5e2195ded454e0406203060aa968ec9a1a03b2e4d07a7b1f9fe9465"
)

EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.3a21ae03356a4p-28"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.b808da9a742c2p-27"
EXPECTED_PARENT_WITNESS_DIGEST = (
    "8137019a4a58e788c37a789b4e69533eef687941ac14ac8f8bb58acf568d9f69"
)

Q011BY_ARTIFACT_SHA256 = "f3bae947808b5417ca784d29a457697e25c2f06216887e2396828bea8fb66064"
Q011BY_RUNNER_SHA256 = "34c251bb967561ab48f301df5ff872962c5cac8ac670b80595d3a5f60e4bb9cd"
Q011BY_DIGEST_NAMES = (
    "input_digest_sha256",
    "refinement_input_digest_sha256",
    "targeted_sweep_digest_sha256",
    "result_digest_sha256",
)
Q011BY_DIGESTS = (
    "9b44a32d229109b82f988030c9deaaa47c306ec8464fe9e920bf241b64bfdd05",
    "45438704eb7c67a2f532507b17642a7d9e4a35e2313f2eace27fee647c52a22c",
    "17a7eb73c45a30f9bd7bc4e4c00306483934000e1a0ac402e1dec481d2fb0b30",
    "81b6ad97a518722a9cc139d64d8938439470d98e14856df1873c6b45176b7fc1",
)

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the first Q011by witness"
)
RESOLVED_CLASSIFICATION = "the first Q011by witness is resolved by individual partition"
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the first Q011by witness persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011bz individual-disc partition audit is inconclusive"


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _interval_record(lower: Fraction, upper: Fraction) -> dict[str, Any]:
    return {
        "lower": q011z._exact_fraction_record(lower),
        "upper": q011z._exact_fraction_record(upper),
    }


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011by._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011by_degree34_first_overlap_refinement.json"
    runner_path = Path(q011by.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    sweep = cycle["targeted_uncoalesced_blockwise_sweep"]
    theorem = cycle["theorem_consequence"]
    witness = sweep["first_unresolved_witness"]
    digests = tuple(cycle[name] for name in Q011BY_DIGEST_NAMES)
    checks = {
        "q011by_fifty_five_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 55
            and prior["direct_digest_count"] == 261
            and len(artifacts) == 55
            and all(prior["checks"].values())
        ),
        "q011by_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011BY_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011BY_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011BY_RUNNER_SHA256
        ),
        "q011by_section_digests_match": digests == Q011BY_DIGESTS,
        "q011by_valid_persistent_outcome_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "persistent"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["first_q011bx_overlap_persists_under_registered_partition"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011by_parent_witness_identity_reproduces": bool(
            tuple(tuple(group) for group in witness["class_counts"])
            == PARENT_CLASS_COUNTS
            and witness["target_identifier"] == TARGET_IDENTIFIER
            and witness["output_block"] == OUTPUT_BLOCK
            and len(witness["source_identifiers"]) == DEGREE
            and witness["relation"] == "overlap"
            and witness["intersection_interval"]["width_hex"]
            == EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
            and witness["center_only_diagnostic"]["relation"]
            == "target_below_product"
            and witness["center_only_diagnostic"]["gap_hex"]
            == EXPECTED_PARENT_CENTER_GAP_HEX
            and witness["witness_digest_sha256"] == EXPECTED_PARENT_WITNESS_DIGEST
        ),
        "q011by_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "two_hundred_sixty_five_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 265
        ),
    }
    artifacts["q011by"] = artifact
    return (
        {
            "prior_q011by_sealed_input_audit": prior,
            "q011by": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011BY_DIGEST_NAMES),
                "digests": list(digests),
                "parent_witness": witness,
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _allocation_inventory(identifier_order: tuple[str, ...]) -> list[dict[str, Any]]:
    records = []
    for count_16_145 in range(5):
        for count_16_151 in range(28):
            for count_16_152 in range(4):
                counts = [
                    count_16_145,
                    4 - count_16_145,
                    count_16_151,
                    27 - count_16_151,
                    count_16_152,
                    3 - count_16_152,
                ]
                output_block = (
                    sum(
                        count * q011z._identifier_indices(identifier)[0]
                        for count, identifier in zip(counts, identifier_order, strict=True)
                    )
                    % SIZE
                )
                records.append(
                    {
                        "individual_counts": counts,
                        "output_block": output_block,
                        "compatible": output_block == OUTPUT_BLOCK,
                    }
                )
    return records


def _fixed_individual_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    tuple[dict[str, Any], ...],
    dict[str, Any],
]:
    fixed, classes, lookup, _external = q011by._fixed_refinement_input_audit(artifacts)
    parent = artifacts["q011by"]["cycle"]["targeted_uncoalesced_blockwise_sweep"][
        "first_unresolved_witness"
    ]
    occupied_records = []
    identifier_order: list[str] = []
    for group_index, class_index, source_count in OCCUPIED_SPEC:
        identifiers = tuple(classes[group_index][class_index])
        representative = lookup[identifiers[0]]
        interval = {
            "center_lower": q011z._exact_fraction_record(
                representative.center_modulus.lower
            ),
            "center_upper": q011z._exact_fraction_record(
                representative.center_modulus.upper
            ),
            "modulus_lower": q011z._exact_fraction_record(representative.modulus.lower),
            "modulus_upper": q011z._exact_fraction_record(representative.modulus.upper),
        }
        occupied_records.append(
            {
                "group_index": group_index,
                "class_index": class_index,
                "source_count": source_count,
                "identifiers": list(identifiers),
                "common_interval_digest_sha256": q011b._canonical_json_sha256(interval),
                "all_member_intervals_equal": all(
                    lookup[identifier].center_modulus == representative.center_modulus
                    and lookup[identifier].modulus == representative.modulus
                    for identifier in identifiers
                ),
            }
        )
        identifier_order.extend(identifiers)
    identifier_order_tuple = tuple(identifier_order)
    allocations = _allocation_inventory(identifier_order_tuple)
    compatible = tuple(record for record in allocations if record["compatible"])
    source_frequencies = Counter(parent["source_identifiers"])
    parent_counts = tuple(source_frequencies[identifier] for identifier in identifier_order)
    parent_allocation_index = next(
        index
        for index, record in enumerate(allocations)
        if tuple(record["individual_counts"]) == parent_counts
    )
    occupied_digest = q011b._canonical_json_sha256(occupied_records)
    identifier_digest = q011b._canonical_json_sha256(identifier_order)
    allocation_digest = q011b._canonical_json_sha256(allocations)
    compatible_digest = q011b._canonical_json_sha256(list(compatible))
    checks = {
        "q011by_fixed_partition_reconstructs": bool(
            fixed["passed"]
            and all(fixed["checks"].values())
            and fixed["uncoalesced_class_counts"] == [4, 2, 3, 6]
        ),
        "parent_class_signature_and_sources_reproduce": bool(
            tuple(tuple(group) for group in parent["class_counts"]) == PARENT_CLASS_COUNTS
            and len(parent["source_identifiers"]) == DEGREE
            and parent_counts == EXPECTED_SOURCE_COUNTS
            and parent_allocation_index == EXPECTED_PARENT_ALLOCATION_INDEX
        ),
        "occupied_classes_and_common_intervals_reproduce": bool(
            tuple(record["common_interval_digest_sha256"] for record in occupied_records)
            == EXPECTED_OCCUPIED_INTERVAL_DIGESTS
            and all(record["all_member_intervals_equal"] for record in occupied_records)
            and occupied_digest == EXPECTED_OCCUPIED_RECORD_DIGEST
        ),
        "singleton_identifier_order_reproduces": bool(
            identifier_order_tuple == EXPECTED_IDENTIFIER_ORDER
            and identifier_digest == EXPECTED_IDENTIFIER_ORDER_DIGEST
        ),
        "full_allocation_inventory_reproduces": bool(
            len(allocations) == EXPECTED_ALLOCATION_COUNT
            and allocation_digest == EXPECTED_ALLOCATION_DIGEST
            and all(
                sum(record["individual_counts"]) == DEGREE
                and all(count >= 0 for count in record["individual_counts"])
                for record in allocations
            )
        ),
        "compatible_allocation_inventory_reproduces": bool(
            len(compatible) == EXPECTED_COMPATIBLE_COUNT
            and compatible_digest == EXPECTED_COMPATIBLE_DIGEST
            and tuple(compatible[0]["individual_counts"])
            == EXPECTED_FIRST_COMPATIBLE_COUNTS
            and tuple(compatible[-1]["individual_counts"])
            == EXPECTED_LAST_COMPATIBLE_COUNTS
            and all(record["output_block"] == OUTPUT_BLOCK for record in compatible)
        ),
        "fixed_input_is_finite_strict_json": bool(
            _all_numeric_values_finite(occupied_records)
            and _strict_json_serializable(occupied_records)
            and json.dumps(occupied_records, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "target_identifier": TARGET_IDENTIFIER,
        "output_block": OUTPUT_BLOCK,
        "parent_class_counts": [list(group) for group in PARENT_CLASS_COUNTS],
        "occupied_class_records": occupied_records,
        "occupied_class_record_digest_sha256": occupied_digest,
        "singleton_identifier_order": identifier_order,
        "singleton_identifier_order_digest_sha256": identifier_digest,
        "full_allocation_count": len(allocations),
        "full_allocation_digest_sha256": allocation_digest,
        "compatible_allocation_count": len(compatible),
        "compatible_allocation_digest_sha256": compatible_digest,
        "first_compatible_counts": compatible[0]["individual_counts"],
        "last_compatible_counts": compatible[-1]["individual_counts"],
        "parent_witness_individual_counts": list(parent_counts),
        "parent_witness_allocation_index": parent_allocation_index,
        "other_parent_class_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "second_q011bx_overlap_recomputed": False,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup, compatible, parent


def _exact_product_records(
    lookup: dict[str, q011z._UniformDisc],
    counts: list[int],
) -> tuple[dict[str, Any], dict[str, Any]]:
    center_lower = Fraction(1)
    center_upper = Fraction(1)
    full_upper = Fraction(1)
    for count, identifier in zip(counts, EXPECTED_IDENTIFIER_ORDER, strict=True):
        disc = lookup[identifier]
        center_lower *= disc.center_modulus.lower**count
        center_upper *= disc.center_modulus.upper**count
        full_upper *= disc.modulus.upper**count
    radius = full_upper - center_upper
    product_lower = max(Fraction(0), center_lower - radius)
    return (
        _interval_record(product_lower, full_upper),
        _interval_record(center_lower, center_upper),
    )


def _binary64_relation(
    product_lower: Fraction,
    product_upper: Fraction,
    target_lower: Fraction,
    target_upper: Fraction,
) -> str:
    product_below_gap = q011ag._down_subtract(
        q011ag._fraction_lower(target_lower), q011ag._fraction_upper(product_upper)
    )
    target_below_gap = q011ag._down_subtract(
        q011ag._fraction_lower(product_lower), q011ag._fraction_upper(target_upper)
    )
    if product_below_gap > 0:
        return "product_below_target"
    if target_below_gap > 0:
        return "target_below_product"
    return "overlap"


def _individual_partition_audit(
    lookup: dict[str, q011z._UniformDisc],
    compatible: tuple[dict[str, Any], ...],
    parent: dict[str, Any],
) -> dict[str, Any]:
    target = lookup[TARGET_IDENTIFIER]
    parent_product = parent["hybrid_product_interval"]
    parent_center = parent["center_product_interval"]
    parent_target = parent["hybrid_target_interval"]
    parent_center_target = parent["center_target_interval"]
    parent_intersection = parent["intersection_interval"]
    parent_center_diagnostic = parent["center_only_diagnostic"]
    records = []
    exact_relations: Counter[str] = Counter()
    binary64_relations: Counter[str] = Counter()
    for allocation_index, allocation in enumerate(compatible):
        counts = allocation["individual_counts"]
        product, center = _exact_product_records(lookup, counts)
        product_lower = q011z._fraction(product["lower"])
        product_upper = q011z._fraction(product["upper"])
        target_lower = target.modulus.lower
        target_upper = target.modulus.upper
        if product_upper < target_lower:
            relation = "product_below_target"
            intersection = None
        elif target_upper < product_lower:
            relation = "target_below_product"
            intersection = None
        else:
            relation = "overlap"
            lower = max(product_lower, target_lower)
            upper = min(product_upper, target_upper)
            intersection = {
                **_interval_record(lower, upper),
                "width": q011z._exact_fraction_record(upper - lower),
                "width_hex": float(upper - lower).hex(),
            }
        center_lower = q011z._fraction(center["lower"])
        center_upper = q011z._fraction(center["upper"])
        if center_upper < target.center_modulus.lower:
            center_relation = "product_below_target"
            center_gap = target.center_modulus.lower - center_upper
        elif target.center_modulus.upper < center_lower:
            center_relation = "target_below_product"
            center_gap = center_lower - target.center_modulus.upper
        else:
            center_relation = "overlap"
            center_gap = Fraction(0)
        binary64_relation = _binary64_relation(
            product_lower, product_upper, target_lower, target_upper
        )
        exact_relations[relation] += 1
        binary64_relations[binary64_relation] += 1
        record = {
            "compatible_allocation_index": allocation_index,
            "individual_counts": counts,
            "degree": sum(counts),
            "output_block": allocation["output_block"],
            "exact_relation": relation,
            "binary64_outward_relation": binary64_relation,
            "product_interval_digest_sha256": q011b._canonical_json_sha256(product),
            "center_product_interval_digest_sha256": q011b._canonical_json_sha256(
                center
            ),
            "target_interval_digest_sha256": q011b._canonical_json_sha256(
                _interval_record(target_lower, target_upper)
            ),
            "intersection_width_hex": (
                intersection["width_hex"] if intersection is not None else None
            ),
            "center_only_relation": center_relation,
            "center_only_gap_hex": float(center_gap).hex(),
            "product_equals_parent": product == parent_product,
            "center_product_equals_parent": center == parent_center,
            "target_equals_parent": (
                _interval_record(target_lower, target_upper) == parent_target
                and _interval_record(
                    target.center_modulus.lower, target.center_modulus.upper
                )
                == parent_center_target
            ),
            "intersection_equals_parent": intersection == parent_intersection,
            "center_diagnostic_equals_parent": bool(
                center_relation == parent_center_diagnostic["relation"]
                and q011z._exact_fraction_record(center_gap)
                == parent_center_diagnostic["gap"]
                and float(center_gap).hex() == parent_center_diagnostic["gap_hex"]
            ),
        }
        records.append(record)
    exact_relation_counts = {
        relation: exact_relations[relation]
        for relation in ("product_below_target", "target_below_product", "overlap")
    }
    binary64_relation_counts = {
        relation: binary64_relations[relation]
        for relation in ("product_below_target", "target_below_product", "overlap")
    }
    checks = {
        "all_registered_compatible_allocations_are_processed": bool(
            len(records) == EXPECTED_COMPATIBLE_COUNT
            and [record["compatible_allocation_index"] for record in records]
            == list(range(EXPECTED_COMPATIBLE_COUNT))
        ),
        "all_degree_and_output_block_constraints_close": all(
            record["degree"] == DEGREE and record["output_block"] == OUTPUT_BLOCK
            for record in records
        ),
        "all_exact_product_and_target_intervals_equal_parent": all(
            record["product_equals_parent"]
            and record["center_product_equals_parent"]
            and record["target_equals_parent"]
            for record in records
        ),
        "all_exact_intersections_and_center_diagnostics_equal_parent": all(
            record["intersection_equals_parent"]
            and record["center_diagnostic_equals_parent"]
            for record in records
        ),
        "all_exact_and_binary64_classifications_remain_overlap": bool(
            exact_relation_counts
            == {
                "product_below_target": 0,
                "target_below_product": 0,
                "overlap": EXPECTED_COMPATIBLE_COUNT,
            }
            and binary64_relation_counts == exact_relation_counts
        ),
        "allocation_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    return {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "target_identifier": TARGET_IDENTIFIER,
        "compatible_allocation_count": len(records),
        "exact_relation_counts": exact_relation_counts,
        "binary64_outward_relation_counts": binary64_relation_counts,
        "parent_product_interval_digest_sha256": q011b._canonical_json_sha256(
            parent_product
        ),
        "parent_target_interval_digest_sha256": q011b._canonical_json_sha256(
            parent_target
        ),
        "parent_intersection_interval_digest_sha256": q011b._canonical_json_sha256(
            parent_intersection
        ),
        "allocation_classification_records": records,
        "allocation_classification_record_digest_sha256": q011b._canonical_json_sha256(
            records
        ),
        "first_allocation_record": records[0],
        "last_allocation_record": records[-1],
        "full_allocation_target_matrix_retained": False,
        "other_parent_class_signatures_recomputed": False,
        "complex_phase_product_evaluated": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "target_identifier": TARGET_IDENTIFIER,
        "output_block": OUTPUT_BLOCK,
        "parent_class_counts": [list(group) for group in PARENT_CLASS_COUNTS],
        "occupied_spec": [list(record) for record in OCCUPIED_SPEC],
        "singleton_identifier_order": list(EXPECTED_IDENTIFIER_ORDER),
        "full_allocation_count": EXPECTED_ALLOCATION_COUNT,
        "compatible_allocation_count": EXPECTED_COMPATIBLE_COUNT,
        "other_parent_class_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "second_q011bx_overlap_recomputed": False,
        "complex_phase_product_evaluated": False,
        "degree_thirty_four_nonresonance_claimed": False,
        "actual_resonance_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "partition_input_digest_sha256": cycle["partition_input_digest_sha256"],
        "allocation_audit_digest_sha256": cycle["allocation_audit_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "diagnostic_gates": cycle["diagnostic_gates"],
        "study_validity": cycle["study_validity"],
        "refinement_outcome": cycle["refinement_outcome"],
        "diagnostic_classification": cycle["diagnostic_classification"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_degree_thirty_four_individual_partition_audit() -> dict[str, Any]:
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
    validity_gates = {
        "q011by_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "56 artifacts and 265 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_parent_witness_reproduces": {
            "passed": sealed["checks"]["q011by_parent_witness_identity_reproduces"],
            "threshold": "class counts, 34 sources, exact intersection and witness digest",
            "value": parent["witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "three occupied pairs, six identifiers and exact equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "560 total and 39 output-block-12 compatible allocations",
            "value": {
                "full": fixed["full_allocation_count"],
                "compatible": fixed["compatible_allocation_count"],
            },
        },
        "all_count_degree_and_output_constraints_close": {
            "passed": partition["checks"]["all_degree_and_output_block_constraints_close"],
            "threshold": "nonnegative degree 34 and output block 12 for all 39 allocations",
            "value": partition["compatible_allocation_count"],
        },
        "all_exact_interval_and_classification_invariants_pass": {
            "passed": partition["passed"],
            "threshold": "parent-equal products, targets, intersections and exclusive relations",
            "value": partition["checks"],
        },
        "strict_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                len(input_digest) == len(partition_digest) == len(allocation_digest) == 64
                and runner["filename"] == "q011bz_degree34_individual_partition_audit.py"
                and partition["first_allocation_record"] is not None
                and partition["last_allocation_record"] is not None
            ),
            "threshold": "three section digests, endpoint records and runner metadata",
            "value": {
                "input": input_digest,
                "partition": partition_digest,
                "allocation": allocation_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    all_parent_equal = bool(
        partition["checks"]["all_exact_product_and_target_intervals_equal_parent"]
        and partition["checks"][
            "all_exact_intersections_and_center_diagnostics_equal_parent"
        ]
    )
    all_overlap = partition["checks"][
        "all_exact_and_binary64_classifications_remain_overlap"
    ]
    strict_count = (
        partition["exact_relation_counts"]["product_below_target"]
        + partition["exact_relation_counts"]["target_below_product"]
    )
    diagnostic_gates = {
        "only_the_registered_parent_signature_is_refined": {
            "passed": bool(
                not fixed["other_parent_class_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["second_q011bx_overlap_recomputed"]
            ),
            "threshold": "one parent signature, one target and no other aggregate",
            "value": fixed["parent_class_counts"],
        },
        "singleton_partition_is_exactly_interval_inert": {
            "passed": all_parent_equal,
            "threshold": "all 39 product, target, intersection and center records equal parent",
            "value": partition["checks"],
        },
        "all_individual_allocations_remain_overlap": {
            "passed": all_overlap and strict_count == 0,
            "threshold": "39 exact and binary64 overlaps, zero strict comparisons",
            "value": partition["exact_relation_counts"],
        },
        "scientific_boundary_is_preserved": {
            "passed": True,
            "threshold": "no phase, degree-34, actual-resonance or SSM claim",
            "value": "certified 2--33 and 91+, missing 34--90",
        },
    }
    inert = validity_passed and all_parent_equal and all_overlap and strict_count == 0
    resolved = validity_passed and not all_parent_equal and strict_count == EXPECTED_COMPATIBLE_COUNT
    effective_persistent = validity_passed and not all_parent_equal and not resolved
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
    cycle = {
        "question": (
            "Does splitting the first Q011by persistent class signature into six singleton "
            "identifiers change any compatible exact product interval or classification?"
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
        "actual_resonance_outcome": "not_established",
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "individual_partition_is_interval_inert_for_first_q011by_witness": inert,
        "first_q011by_witness_is_resolved_by_individual_partition": resolved,
        "q011by_persistent_diagnostic_is_preserved": True,
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
        "This diagnostic concerns only the first Q011by persistent class signature, its "
        "thirty-nine output-block-12 singleton allocations and target "
        "block=12;center=124 for the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf. It proves only whether identifier relabeling changes the existing "
        "modulus intervals. It does not evaluate complex phase, the other 9799 Q011by class "
        "signatures, other targets or aggregate 2340. It leaves the Q011bx rejection, Q011by "
        "persistence, certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, "
        "and makes no claim about an actual resonance, degree-34 nonresonance, all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011ca to apply complex phase eigendisc products only to the registered "
        "thirty-nine singleton allocations."
        if inert
        else "Preregister the smallest effective changed allocation refinement."
        if validity_passed
        else "Repair only the first Q011bz validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011bz cycle failed strict serialization or digest")
    return cycle


def run_q011bz_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "six registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "full_allocation_target_matrix_retained": False,
            "complex_phase_product_evaluated": False,
        },
        "mathematical_scope": {
            "diagnostic": "first Q011by witness individual-disc partition invariance",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "target_identifier": TARGET_IDENTIFIER,
            "complex_phase_claim": False,
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
    result = run_q011bz_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
