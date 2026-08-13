"""Q011cc individual-disc partition audit for the first Q011cb witness."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011bz_degree34_individual_partition_audit as q011bz
import research.q011cb_degree34_second_overlap_refinement as q011cb
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ag = q011cb.q011ag
q011b = q011cb.q011b
q011z = q011cb.q011z

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
SELECTED_COUNTS = (13, 9, 5, 7)
TARGET_IDENTIFIER = "block=7;center=44"
OUTPUT_BLOCK = 7
PARENT_CLASS_COUNTS = (
    (0, 0, 0, 13),
    (0, 9),
    (5,),
    (0, 7),
)
OCCUPIED_SPEC = ((0, 3, 13), (1, 1, 9), (2, 0, 5), (3, 1, 7))
EXPECTED_IDENTIFIER_ORDER = (
    "block=16;center=145",
    "block=1;center=145",
    "block=16;center=151",
    "block=1;center=151",
    "block=16;center=152",
    "block=1;center=152",
    "block=16;center=149",
    "block=1;center=149",
)
EXPECTED_SOURCE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 7)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 9, 0, 5, 5, 2)
EXPECTED_LAST_COMPATIBLE_COUNTS = (13, 0, 9, 0, 0, 5, 0, 7)
EXPECTED_PARENT_ALLOCATION_INDEX = 6672
EXPECTED_PARENT_COMPATIBLE_INDEX = 381
EXPECTED_ALLOCATION_COUNT = 6720
EXPECTED_COMPATIBLE_COUNT = 382

EXPECTED_OCCUPIED_INTERVAL_DIGESTS = (
    "53f9a306265ffcbfa83c64089e6418ab895037a3dad6a6fe85ba15dab18c8825",
    "2761f9c8d8e92b66d0c8a3e85affc78cda4e1ac98c2beeed7705224145571402",
    "39747a3474ada699010196f508500971e97451f666025e46bbbc68233ef1d86a",
    "66a6c269ac137479694f186884d49ca3a4d11070e69132bab822391a557075d8",
)
EXPECTED_OCCUPIED_RECORD_DIGEST = (
    "db25c2fa05b348a4b97fad4206b748c1e1b02b0b9778c7f3ccf705dfe9e7af32"
)
EXPECTED_IDENTIFIER_ORDER_DIGEST = (
    "6f192e02004d04c2feb0061b170f040086759cb31f00f907d9037063b2d9ec69"
)
EXPECTED_ALLOCATION_DIGEST = (
    "44ba5fda9f1d5c7512d2008e655865d4b2e8f04698e196093067d887952d110f"
)
EXPECTED_COMPATIBLE_DIGEST = (
    "ddb8dd5db8780f285cca94fbc0c1b57f540259841a03631b211d8605becc5b60"
)

EXPECTED_PARENT_WAVE_MULTIPLICITY = 382
EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY = 0
EXPECTED_PARENT_INTERSECTION_WIDTH_HEX = "0x1.9d49c4083b31ep-32"
EXPECTED_PARENT_CENTER_RELATION = "target_below_product"
EXPECTED_PARENT_CENTER_GAP_HEX = "0x1.3aa0404d55937p-28"
EXPECTED_PARENT_WITNESS_DIGEST = (
    "de9435001e9603c4488945d9077e45abfa30e1c267271a27ae41d01b84993442"
)

Q011CB_ARTIFACT_SHA256 = (
    "9e191ead642e398ccd013c783b0ddeae78e6e7e4c3bf443e08bd64c9e826aa5b"
)
Q011CB_RUNNER_SHA256 = (
    "d7828cb2aef583ff82bd421212837534169ba42ad1962961cf0003e9f812b085"
)
Q011CB_DIGEST_NAMES = (
    "input_digest_sha256",
    "refinement_input_digest_sha256",
    "targeted_sweep_digest_sha256",
    "result_digest_sha256",
)
Q011CB_DIGESTS = (
    "cee7e83699027ea5d12ba79b05e06d19c1a8bff5400d06807d52b1f4ac9f4f1e",
    "bdd175e1b065849077bcb15ab16f2cb2dd0011308a4a8c7748ba7c10d88278cc",
    "0dd5d08276fd5f4246a912ace617e4b6ec72007e3994b508d13d875917a40924",
    "eb5011b3a2767f9618bc71c31c1cb889a0a108f819592a6a8addc169abe855e5",
)

INERT_CLASSIFICATION = (
    "the individual-disc partition is interval-inert for the first Q011cb witness"
)
RESOLVED_CLASSIFICATION = "the first Q011cb witness is resolved by individual partition"
EFFECTIVE_PERSISTENT_CLASSIFICATION = (
    "the individual-disc partition changes intervals but the first Q011cb witness "
    "persists"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011cc individual-disc partition audit is inconclusive"


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
    return q011bz._interval_record(lower, upper)


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011cb._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011cb_degree34_second_overlap_refinement.json"
    )
    runner_path = Path(q011cb.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    sweep = cycle["targeted_blockwise_refinement_sweep"]
    theorem = cycle["theorem_consequence"]
    witness = sweep["first_unresolved_witness"]
    digests = tuple(cycle[name] for name in Q011CB_DIGEST_NAMES)
    checks = {
        "q011cb_fifty_eight_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 58
            and prior["direct_digest_count"] == 274
            and len(artifacts) == 58
            and all(prior["checks"].values())
        ),
        "q011cb_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CB_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CB_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CB_RUNNER_SHA256
        ),
        "q011cb_section_digests_match": digests == Q011CB_DIGESTS,
        "q011cb_valid_persistent_outcome_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "persistent"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "second_q011bx_aggregate_first_overlap_persists_under_registered_partition"
            ]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"]
            == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"]
            == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011cb_registered_sweep_and_first_witness_reproduce": bool(
            sweep["modulus_signature_count"] == 44_800
            and sweep["compatible_modulus_signature_count"] == 44_800
            and sweep["distinct_relation_counts"]
            == {
                "product_below_target": 0,
                "target_below_product": 0,
                "overlap": 44_800,
            }
            and witness["wave_multiplicity"] == EXPECTED_PARENT_WAVE_MULTIPLICITY
            and witness["witness_digest_sha256"] == EXPECTED_PARENT_WITNESS_DIGEST
        ),
        "q011cb_parent_witness_identity_reproduces": bool(
            witness["aggregate_index"] == LOCAL_AGGREGATE_INDEX
            and tuple(witness["selected_type_counts"]) == SELECTED_COUNTS
            and tuple(tuple(group) for group in witness["class_counts"])
            == PARENT_CLASS_COUNTS
            and witness["target_identifier"] == TARGET_IDENTIFIER
            and witness["output_block"] == OUTPUT_BLOCK
            and witness["left_index"] == 0
            and witness["right_index"] == 0
            and witness["wave_multiplicity"] == EXPECTED_PARENT_WAVE_MULTIPLICITY
            and witness["block_zero_multiplicity"]
            == EXPECTED_PARENT_BLOCK_ZERO_MULTIPLICITY
            and len(witness["source_identifiers"]) == DEGREE
            and witness["relation"] == "overlap"
            and witness["intersection_interval"]["width_hex"]
            == EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
            and witness["center_only_diagnostic"]["relation"]
            == EXPECTED_PARENT_CENTER_RELATION
            and witness["center_only_diagnostic"]["gap_hex"]
            == EXPECTED_PARENT_CENTER_GAP_HEX
            and witness["witness_digest_sha256"] == EXPECTED_PARENT_WITNESS_DIGEST
        ),
        "q011cb_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "two_hundred_seventy_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 278
        ),
    }
    artifacts["q011cb"] = artifact
    return (
        {
            "prior_q011cb_sealed_input_audit": prior,
            "q011cb": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CB_DIGEST_NAMES),
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
    for count_16_145 in range(14):
        for count_16_151 in range(10):
            for count_16_152 in range(6):
                for count_16_149 in range(8):
                    counts = [
                        count_16_145,
                        13 - count_16_145,
                        count_16_151,
                        9 - count_16_151,
                        count_16_152,
                        5 - count_16_152,
                        count_16_149,
                        7 - count_16_149,
                    ]
                    output_block = (
                        sum(
                            count * q011z._identifier_indices(identifier)[0]
                            for count, identifier in zip(
                                counts, identifier_order, strict=True
                            )
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
    fixed, classes, lookup = q011cb._fixed_refinement_input_audit(artifacts)
    parent = artifacts["q011cb"]["cycle"]["targeted_blockwise_refinement_sweep"][
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
            "modulus_lower": q011z._exact_fraction_record(
                representative.modulus.lower
            ),
            "modulus_upper": q011z._exact_fraction_record(
                representative.modulus.upper
            ),
        }
        occupied_records.append(
            {
                "group_index": group_index,
                "class_index": class_index,
                "source_count": source_count,
                "identifiers": list(identifiers),
                "common_interval_digest_sha256": q011b._canonical_json_sha256(
                    interval
                ),
                "all_member_intervals_equal": all(
                    lookup[identifier].center_modulus
                    == representative.center_modulus
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
    parent_counts = tuple(
        source_frequencies[identifier] for identifier in identifier_order
    )
    parent_allocation_index = next(
        index
        for index, record in enumerate(allocations)
        if tuple(record["individual_counts"]) == parent_counts
    )
    parent_compatible_index = next(
        index
        for index, record in enumerate(compatible)
        if tuple(record["individual_counts"]) == parent_counts
    )
    occupied_digest = q011b._canonical_json_sha256(occupied_records)
    identifier_digest = q011b._canonical_json_sha256(identifier_order)
    allocation_digest = q011b._canonical_json_sha256(allocations)
    compatible_digest = q011b._canonical_json_sha256(list(compatible))
    checks = {
        "q011cb_fixed_refinement_reconstructs": bool(
            fixed["passed"]
            and all(fixed["checks"].values())
            and fixed["refined_class_counts"] == [4, 2, 1, 2]
        ),
        "parent_class_signature_sources_and_multiplicity_reproduce": bool(
            tuple(tuple(group) for group in parent["class_counts"])
            == PARENT_CLASS_COUNTS
            and len(parent["source_identifiers"]) == DEGREE
            and parent_counts == EXPECTED_SOURCE_COUNTS
            and parent["wave_multiplicity"] == EXPECTED_PARENT_WAVE_MULTIPLICITY
            and parent_allocation_index == EXPECTED_PARENT_ALLOCATION_INDEX
            and parent_compatible_index == EXPECTED_PARENT_COMPATIBLE_INDEX
        ),
        "occupied_classes_and_common_intervals_reproduce": bool(
            tuple(
                record["common_interval_digest_sha256"]
                for record in occupied_records
            )
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
            and len(compatible) == parent["wave_multiplicity"]
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
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
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
        "parent_witness_compatible_index": parent_compatible_index,
        "compatible_allocations_exactly_partition_parent_wave_multiplicity": (
            len(compatible) == parent["wave_multiplicity"]
        ),
        "other_q011cb_refined_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "other_parent_overlap_signatures_recomputed": False,
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


def _binary64_relation_and_gap(
    product_lower: Fraction,
    product_upper: Fraction,
    target_lower: Fraction,
    target_upper: Fraction,
) -> tuple[str, float]:
    product_below_gap = q011ag._down_subtract(
        q011ag._fraction_lower(target_lower), q011ag._fraction_upper(product_upper)
    )
    target_below_gap = q011ag._down_subtract(
        q011ag._fraction_lower(product_lower), q011ag._fraction_upper(target_upper)
    )
    if product_below_gap > 0:
        return "product_below_target", product_below_gap
    if target_below_gap > 0:
        return "target_below_product", target_below_gap
    return "overlap", 0.0


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
    target_record = _interval_record(target.modulus.lower, target.modulus.upper)
    center_target_record = _interval_record(
        target.center_modulus.lower, target.center_modulus.upper
    )
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
            exact_gap = target_lower - product_upper
            intersection = None
        elif target_upper < product_lower:
            relation = "target_below_product"
            exact_gap = product_lower - target_upper
            intersection = None
        else:
            relation = "overlap"
            exact_gap = Fraction(0)
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
        binary64_relation, binary64_gap = _binary64_relation_and_gap(
            product_lower, product_upper, target_lower, target_upper
        )
        exact_relations[relation] += 1
        binary64_relations[binary64_relation] += 1
        records.append(
            {
                "compatible_allocation_index": allocation_index,
                "individual_counts": counts,
                "degree": sum(counts),
                "output_block": allocation["output_block"],
                "exact_relation": relation,
                "binary64_outward_relation": binary64_relation,
                "exact_gap_positive": exact_gap > 0,
                "exact_gap_hex": float(exact_gap).hex(),
                "binary64_outward_gap_positive": binary64_gap > 0,
                "binary64_outward_gap_hex": binary64_gap.hex(),
                "product_interval_digest_sha256": q011b._canonical_json_sha256(
                    product
                ),
                "center_product_interval_digest_sha256": (
                    q011b._canonical_json_sha256(center)
                ),
                "target_interval_digest_sha256": q011b._canonical_json_sha256(
                    target_record
                ),
                "intersection_width_hex": (
                    intersection["width_hex"] if intersection is not None else None
                ),
                "center_only_relation": center_relation,
                "center_only_gap_hex": float(center_gap).hex(),
                "product_equals_parent": product == parent_product,
                "center_product_equals_parent": center == parent_center,
                "target_equals_parent": bool(
                    target_record == parent_target
                    and center_target_record == parent_center_target
                ),
                "intersection_equals_parent": intersection == parent_intersection,
                "center_diagnostic_equals_parent": bool(
                    center_relation == parent_center_diagnostic["relation"]
                    and q011z._exact_fraction_record(center_gap)
                    == parent_center_diagnostic["gap"]
                    and float(center_gap).hex()
                    == parent_center_diagnostic["gap_hex"]
                ),
            }
        )
    relation_order = ("product_below_target", "target_below_product", "overlap")
    exact_relation_counts = {
        relation: exact_relations[relation] for relation in relation_order
    }
    binary64_relation_counts = {
        relation: binary64_relations[relation] for relation in relation_order
    }
    all_parent_equal = all(
        record["product_equals_parent"]
        and record["center_product_equals_parent"]
        and record["target_equals_parent"]
        and record["intersection_equals_parent"]
        and record["center_diagnostic_equals_parent"]
        for record in records
    )
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
        "exact_relation_partition_is_exclusive_and_complete": (
            sum(exact_relation_counts.values()) == EXPECTED_COMPATIBLE_COUNT
        ),
        "binary64_relation_partition_is_exclusive_and_complete": (
            sum(binary64_relation_counts.values()) == EXPECTED_COMPATIBLE_COUNT
        ),
        "all_exact_and_binary64_relations_agree": bool(
            exact_relation_counts == binary64_relation_counts
            and all(
                record["exact_relation"] == record["binary64_outward_relation"]
                for record in records
            )
        ),
        "all_strict_gap_flags_match_relations": all(
            (
                record["exact_gap_positive"]
                and record["binary64_outward_gap_positive"]
            )
            == (record["exact_relation"] != "overlap")
            for record in records
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
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "target_identifier": TARGET_IDENTIFIER,
        "compatible_allocation_count": len(records),
        "exact_relation_counts": exact_relation_counts,
        "binary64_outward_relation_counts": binary64_relation_counts,
        "all_product_target_intersection_and_center_records_equal_parent": (
            all_parent_equal
        ),
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
        "allocation_classification_record_digest_sha256": (
            q011b._canonical_json_sha256(records)
        ),
        "first_allocation_record": records[0],
        "last_allocation_record": records[-1],
        "full_allocation_target_matrix_retained": False,
        "other_q011cb_refined_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "complex_phase_product_evaluated": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "selected_type_counts": list(SELECTED_COUNTS),
        "target_identifier": TARGET_IDENTIFIER,
        "output_block": OUTPUT_BLOCK,
        "parent_class_counts": [list(group) for group in PARENT_CLASS_COUNTS],
        "occupied_spec": [list(record) for record in OCCUPIED_SPEC],
        "singleton_identifier_order": list(EXPECTED_IDENTIFIER_ORDER),
        "full_allocation_count": EXPECTED_ALLOCATION_COUNT,
        "compatible_allocation_count": EXPECTED_COMPATIBLE_COUNT,
        "other_q011cb_refined_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
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


def run_degree_thirty_four_second_individual_partition_audit() -> dict[str, Any]:
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
        "q011cb_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "59 artifacts and 278 direct digests reproduce",
            "value": sealed["checks"],
        },
        "registered_parent_witness_reproduces": {
            "passed": sealed["checks"]["q011cb_parent_witness_identity_reproduces"],
            "threshold": "class counts, 382 multiplicity, exact intersection and digest",
            "value": parent["witness_digest_sha256"],
        },
        "occupied_classes_singletons_and_common_intervals_reproduce": {
            "passed": bool(
                fixed["checks"]["occupied_classes_and_common_intervals_reproduce"]
                and fixed["checks"]["singleton_identifier_order_reproduces"]
            ),
            "threshold": "four occupied pairs, eight identifiers and equal intervals",
            "value": fixed["occupied_class_records"],
        },
        "registered_allocation_inventory_reproduces": {
            "passed": bool(
                fixed["checks"]["full_allocation_inventory_reproduces"]
                and fixed["checks"]["compatible_allocation_inventory_reproduces"]
            ),
            "threshold": "6720 total and 382 output-block-7 compatible allocations",
            "value": {
                "full": fixed["full_allocation_count"],
                "compatible": fixed["compatible_allocation_count"],
            },
        },
        "all_count_degree_and_output_constraints_close": {
            "passed": bool(
                fixed[
                    "compatible_allocations_exactly_partition_parent_wave_multiplicity"
                ]
                and partition["checks"]["all_degree_and_output_block_constraints_close"]
            ),
            "threshold": "382 unit allocations, degree 34 and output block 7",
            "value": partition["compatible_allocation_count"],
        },
        "all_exact_interval_and_classification_invariants_pass": {
            "passed": partition["passed"],
            "threshold": "exact/outward exclusive relations and strict finite records",
            "value": partition["checks"],
        },
        "strict_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                len(input_digest) == len(partition_digest) == len(allocation_digest) == 64
                and runner["filename"]
                == "q011cc_degree34_second_individual_partition_audit.py"
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
    all_parent_equal = partition[
        "all_product_target_intersection_and_center_records_equal_parent"
    ]
    exact_counts = partition["exact_relation_counts"]
    binary_counts = partition["binary64_outward_relation_counts"]
    strict_count = (
        exact_counts["product_below_target"] + exact_counts["target_below_product"]
    )
    all_overlap = bool(
        exact_counts["overlap"] == EXPECTED_COMPATIBLE_COUNT
        and binary_counts == exact_counts
    )
    all_strict = bool(
        strict_count == EXPECTED_COMPATIBLE_COUNT
        and binary_counts["overlap"] == 0
        and all(
            record["exact_gap_positive"]
            and record["binary64_outward_gap_positive"]
            for record in partition["allocation_classification_records"]
        )
    )
    inert = validity_passed and all_parent_equal and all_overlap
    resolved = validity_passed and all_strict
    effective_persistent = bool(
        validity_passed
        and not inert
        and not resolved
        and exact_counts["overlap"] > 0
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
        "only_the_registered_q011cb_signature_is_refined": {
            "passed": bool(
                not fixed["other_q011cb_refined_signatures_recomputed"]
                and not fixed["other_parent_targets_recomputed"]
                and not fixed["other_parent_overlap_signatures_recomputed"]
            ),
            "threshold": "one Q011cb signature, one target and no other aggregate",
            "value": fixed["parent_class_counts"],
        },
        "parent_interval_comparison_is_complete": {
            "passed": bool(
                len(partition["allocation_classification_records"])
                == EXPECTED_COMPATIBLE_COUNT
                and all(
                    isinstance(record["product_equals_parent"], bool)
                    and isinstance(record["intersection_equals_parent"], bool)
                    for record in partition["allocation_classification_records"]
                )
            ),
            "threshold": "382 complete parent-comparison records",
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
            "Does splitting the first Q011cb persistent blockwise signature into eight "
            "singleton identifiers change any compatible exact product interval or "
            "classification?"
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
        "individual_partition_is_interval_inert_for_first_q011cb_witness": inert,
        "first_q011cb_witness_is_resolved_by_individual_partition": resolved,
        "individual_partition_changes_intervals_but_first_q011cb_witness_persists": (
            effective_persistent
        ),
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
        "This diagnostic concerns only the first Q011cb persistent refined signature, "
        "its 382 output-block-7 singleton allocations and target block=7;center=44 for "
        "the fixed 17x17 repaired exact map on one fixed conservation leaf. It proves "
        "only whether identifier relabeling changes the existing modulus intervals. It "
        "does not evaluate complex phase, the other 44799 Q011cb refined signatures, "
        "the other 31 parent coalesced overlaps, other targets, aggregate 2340 as a "
        "whole or aggregate 972. It leaves the Q011bx rejection, Q011by persistence, "
        "Q011bz partition-inert result, Q011ca phase resolution, Q011cb persistence, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about an actual resonance, degree-34 nonresonance, all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011cd to expand only the 382 registered wave allocations into "
        "component-safe complex phase discs."
        if inert
        else "Preregister Q011cd for the next Q011cb refined overlap."
        if resolved
        else "Preregister Q011cd to apply component-safe complex phase discs only to "
        "the first remaining individual overlap."
        if effective_persistent
        else "Repair only the first Q011cc validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011cc cycle failed strict serialization or digest")
    return cycle


def run_q011cc_study() -> dict[str, Any]:
    cycle = run_degree_thirty_four_second_individual_partition_audit()
    partition = cycle["individual_allocation_interval_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "source_partition": "eight registered singleton identifiers",
            "product_enclosure": "exact rational blockwise modulus interval",
            "fourier_compatibility": "exact identifier block sum modulo 17",
            "target_comparisons": partition["compatible_allocation_count"],
            "full_allocation_target_matrix_retained": False,
            "complex_phase_product_evaluated": False,
        },
        "mathematical_scope": {
            "diagnostic": "first Q011cb witness individual-disc partition invariance",
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
    result = run_q011cc_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
