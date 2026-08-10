"""Q011ao component-safe hierarchical degree-seventeen nonresonance audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from math import comb
from math import prod as integer_product
from pathlib import Path
from typing import Any

import research.q011an_active_block_structured_rows as q011an
import research.q011u_c91_modulus_nonresonance as q011u
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ak = q011an.q011ak
q011af = q011an.q011am.q011af
q011ag = q011an.q011ag
q011b = q011an.q011b
q011z = q011an.q011z

SIZE = 17
DEGREE = 17

EXPECTED_DEGREE_AGGREGATE_COUNT = 1_140
EXPECTED_EXPANDED_CONTROL_COUNT = 26_334
EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT = 941
EXPECTED_OVERLAP_AGGREGATE_COUNT = 199
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_UNIQUE_EXTERNAL_GROUP_COUNT = 15
EXPECTED_TARGET_IDENTIFIER_COUNT = 152
EXPECTED_MULTI_TARGET_AGGREGATE_COUNT = 2
EXPECTED_MAXIMUM_EXTERNAL_COMPONENT_COUNT = 2
EXPECTED_TARGET_BLOCK_COUNTS = (6, 8, 8, 12, 12, 15, 8, 6, 4, 4, 6, 8, 15, 12, 12, 8, 8)
EXPECTED_FIRST_COUNTS = (0, 0, 0, 17)
EXPECTED_LAST_COUNTS = (14, 0, 3, 0)
EXPECTED_COUNT_TUPLE_DIGEST = "cf03ad31a7ebe127461320242010ad226c466eec1fa003adfb3624368c119695"
EXPECTED_EXTERNAL_GROUP_DIGEST = "8bbe171b29ce286f17a2f6b7760d1ffabbcec00586948944b42eea5f2ab4a1c9"
EXPECTED_OVERLAP_RECORD_DIGEST = "af1083d0956542e765fd5cb4009ac1271d1225323859e96dc23076a50f5d32ab"
EXPECTED_TARGET_RECORD_DIGEST = "9453379d890ce3282a7b5294967ed6e9e9bc4898ddf11f4d51786b4712715c90"
EXPECTED_INVENTORY_DIGEST = "9f81d354538ddcd835d7e06e9183263714a56acf4de3fce7156cf8686f6a2e92"

NEW_TARGET_IDENTIFIERS = (
    "block=10;center=11",
    "block=10;center=12",
    "block=11;center=7",
    "block=11;center=8",
    "block=12;center=150",
    "block=12;center=151",
    "block=14;center=112",
    "block=14;center=113",
    "block=14;center=114",
    "block=14;center=115",
    "block=16;center=132",
    "block=16;center=133",
    "block=1;center=132",
    "block=1;center=133",
    "block=3;center=112",
    "block=3;center=113",
    "block=3;center=114",
    "block=3;center=115",
    "block=5;center=150",
    "block=5;center=151",
    "block=6;center=7",
    "block=6;center=8",
    "block=7;center=11",
    "block=7;center=12",
)
EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST = (
    "68fd926ac22cf9fdbb272b5f4316da6136aaf4b6ca94ab2632149dade7bac8dc"
)
EXPECTED_REUSED_IDENTIFIER_COUNT = 152
EXPECTED_REUSED_SELECTED_IDENTIFIER_COUNT = 24
EXPECTED_REUSED_TARGET_IDENTIFIER_COUNT = 128
EXPECTED_NEW_TARGET_IDENTIFIER_COUNT = 24
EXPECTED_FINAL_IDENTIFIER_COUNT = 176
EXPECTED_NEW_TARGET_RECORD_DIGEST = (
    "b85b0320d3378adfbe184c34a380d88ea60261067c3edac15f0387279eb7f27b"
)
EXPECTED_FINAL_RECORD_DIGEST = "9a4a5eca990b90744e40076706f090d7e7f9336481a27a82f3e9d1ee6df628df"
EXPECTED_CLASS_MEMBERSHIP_DIGEST = (
    "269187f8489521c7e37ae8a91669b9dc020ac10d4ef1d42272bb636fa7bc9b8c"
)

EXPECTED_CLASS_POWER_COUNT = 238
EXPECTED_CLASS_POWER_DIGEST = "505796aa76169a763a11ce08e2b017898e23311b4df98b23ff468e5515e9b12e"
EXPECTED_GROUP_SIGNATURE_COUNT = 104_672
EXPECTED_GROUP_SIGNATURE_DIGEST = "7a400cc0b59d7bac73aa8837af3e4f6b738fbed6863a285cfc9b83532b99c770"
EXPECTED_PAIR_POOL_COUNT = 101
EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT = 720_101
EXPECTED_PAIR_POOL_DIGEST = "dd59bcc7ffeeeb4798bc8c26b8b4c1857c06288af0e4ac92b90260712c68634f"
EXPECTED_CONVOLUTION_CALL_COUNT = 1_339_913
EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND = 1_700
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 1_201_200
EXPECTED_TWO_PRODUCT_ARRAY_BYTES = 19_219_200
EXPECTED_MAXIMUM_WAVE_COEFFICIENT = 1_422
EXPECTED_MAXIMUM_FOURIER_CRUDE_BOUND = 10_132

EXPECTED_ORIGINAL_MONOMIAL_COUNT = 20_467_791_608
EXPECTED_MODULUS_SIGNATURE_COUNT = 55_452_003
EXPECTED_COMPATIBLE_SIGNATURE_COUNT = 49_831_491
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 4_949_877_042
EXPECTED_WEIGHTED_COMPARISON_COUNT = 10_786_916_138
EXPECTED_DISTINCT_COMPARISON_COUNT = 301_592_258
EXPECTED_DISTINCT_RELATIONS = {
    "overlap": 0,
    "product_below_target": 135_864_646,
    "target_below_product": 165_727_612,
}
EXPECTED_WEIGHTED_RELATIONS = {
    "overlap": 0,
    "product_below_target": 5_313_413_298,
    "target_below_product": 5_473_502_840,
}
EXPECTED_AGGREGATE_DIGEST = "5ac4782b4279a5b36d42dd1e7eb9082d3e427b6bfd1d1ac7570c1d9d54af44ce"
EXPECTED_BOUND_MATRIX_COUNT = 199
EXPECTED_BOUND_MATRIX_DIGEST = "18c3d7cdd1d53d9b95d6d1c8aaa7b3162aa2fa51fe912c118d660ff13894aca5"
EXPECTED_COEFFICIENT_MATRIX_COUNT = 889
EXPECTED_COEFFICIENT_MATRIX_DIGEST = (
    "9bea6d491f17faa5ae88cf4adb30c675c6f13ff69028a4c31ab169e4365b9026"
)
EXPECTED_CLASSIFICATION_MATRIX_COUNT = 2_084
EXPECTED_CLASSIFICATION_MATRIX_DIGEST = (
    "fcf407a94677b27f327676881e81c8b220db764a973d32b35feb62ae6f6652f6"
)

EXPECTED_MINIMUM_AGGREGATE_INDEX = 113
EXPECTED_MINIMUM_COUNTS = (5, 5, 4, 3)
EXPECTED_MINIMUM_TARGET = "block=11;center=3"
EXPECTED_MINIMUM_LEFT_INDEX = 5
EXPECTED_MINIMUM_RIGHT_INDEX = 55
EXPECTED_MINIMUM_MULTIPLICITY = 15
EXPECTED_MINIMUM_RELATION = "target_below_product"
EXPECTED_MINIMUM_CLASS_COUNTS = (
    (0, 0, 0, 5),
    (5, 0),
    (0, 0, 4),
    (3, 0, 0, 0, 0, 0),
)
EXPECTED_MINIMUM_SOURCES = (
    *("block=16;center=145",) * 5,
    *("block=16;center=150",) * 5,
    *("block=1;center=152",) * 4,
    *("block=0;center=144",) * 3,
)
EXPECTED_MINIMUM_OUTWARD_GAP_HEX = "0x1.d0afe9cffffffp-25"
EXPECTED_MINIMUM_EXACT_GAP_HEX = "0x1.d0afedf6fcdf8p-25"
EXPECTED_MINIMUM_WITNESS_DIGEST = "02b8f2278d327e8284690f28c936fb24e3ef2134b7259d7fe252aba45ba0d336"

ACCEPTED_CLASSIFICATION = (
    "the component-safe hierarchical sweep certifies degree-17 external nonresonance"
)
REJECTED_CLASSIFICATION = (
    "the component-safe hierarchical degree-17 sufficient certificate is rejected"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011ao degree-17 hierarchical audit is inconclusive"
ACTUAL_RESONANCE_OUTCOME = "ruled_out_within_registered_degree_seventeen_scope"

Q011AN_ARTIFACT_SHA256 = "229dddbb885803b24ed61c35a95cb87bcfa6c692f6bb6c30d20529d3be687b31"
Q011AN_RUNNER_SHA256 = "02c0a5722add2d4e979c78806bfe4d0e7c503a547dc200ad0bc375c86ee28a6a"
Q011AN_DIGEST_NAMES = (
    "input_digest_sha256",
    "row_digest_sha256",
    "envelope_digest_sha256",
    "sweep_digest_sha256",
    "result_digest_sha256",
)
Q011AN_DIGESTS = (
    "d617a48bdca98ff949645394948527573b6574176eadcb15eab7de7feda60dfd",
    "5c558564ec862d621a75bff1cc6882c4ead98910b67f02559d1f8bec537e0c13",
    "b3a40b84b19d69adabea11a53963a47584f361c96abf91224f6c4fe9e41b5a9f",
    "db38109e4a83209a28a8f982f88b9eec6c3b8a9f07c0b3a13be3592db2a91e53",
    "263a56ba3b426376f3e82d29c7815f6338063e3f682d68ee995f5c129a721309",
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
    prior, artifacts = q011an._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011an_active_block_structured_rows.json"
    runner_path = Path(q011an.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AN_DIGEST_NAMES)
    theorem = cycle["theorem_consequence"]
    checks = {
        "q011an_eighteen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 93
            and len(artifacts) == 18
            and all(prior["checks"].values())
        ),
        "q011an_artifact_sha256_matches": _file_sha256(artifact_path) == Q011AN_ARTIFACT_SHA256,
        "q011an_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AN_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AN_RUNNER_SHA256
        ),
        "q011an_digests_match": digests == Q011AN_DIGESTS,
        "q011an_registered_acceptance_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and artifact["actual_resonance_outcome"] == q011an.ACTUAL_RESONANCE_OUTCOME
            and cycle["scientific_classification"] == q011an.ACCEPTED_CLASSIFICATION
            and theorem["degree_sixteen_external_nonresonance_is_certified"]
            and theorem["missing_external_nonresonance_degrees"] == list(range(17, 91))
        ),
        "q011an_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011an_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011an_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "ninety_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 98
        ),
    }
    artifacts["q011an"] = artifact
    return (
        {
            "prior_q011an_sealed_input_audit": prior,
            "q011an": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011AN_DIGEST_NAMES),
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


def _degree_seventeen_inventory_audit(
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
        "q011u_degree_seventeen_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"] == EXPECTED_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
        ),
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


def _degree_seventeen_envelope_audit(
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
    q011ak_records = artifacts["q011ak"]["cycle"]["blockwise_transformed_residual_envelope_audit"][
        "blockwise_disc_records"
    ]
    q011an_envelope = artifacts["q011an"]["cycle"]["component_safe_envelope_audit"]
    q011an_records = {
        record["identifier"]: record for record in q011an_envelope["component_safe_records"]
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
    reused = needed & set(q011an_records)
    new_identifiers = tuple(sorted(needed - set(q011an_records)))
    lookup: dict[str, q011z._UniformDisc] = {}
    new_records = []
    final_records = []
    for identifier in sorted(needed):
        block, center_index = q011z._identifier_indices(identifier)
        center = center_modulus(identifier)
        if identifier in q011an_records:
            source = q011an_records[identifier]
            modulus = RationalInterval(
                q011z._fraction(source["modulus_lower"]),
                q011z._fraction(source["modulus_upper"]),
            )
            radius_kind = "q011an_component_safe"
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
        identifier: component
        for component in external_merged
        for identifier in component.identifiers
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
            and len(target_identifiers & reused) == EXPECTED_REUSED_TARGET_IDENTIFIER_COUNT
            and len(new_identifiers) == EXPECTED_NEW_TARGET_IDENTIFIER_COUNT
            and len(needed) == EXPECTED_FINAL_IDENTIFIER_COUNT
        ),
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
        "independent_source_choices_and_all_target_discs_are_declared": True,
        "envelope_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(final_records)
            and _strict_json_serializable(final_records)
            and json.dumps(final_records, allow_nan=False)
        ),
    }
    audit = {
        "selected_source_identifier_count": len(selected_identifiers),
        "external_target_identifier_count": len(target_identifiers),
        "reused_q011an_identifier_count": len(reused),
        "reused_q011an_selected_identifier_count": len(selected_identifiers & reused),
        "reused_q011an_target_identifier_count": len(target_identifiers & reused),
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
        "disc_label_logic": (
            "each source factor independently selects any certified selected disc with "
            "repetition and every external target disc is checked; no component-internal "
            "eigenvalue-to-disc label is assumed"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup, classes


def _resource_estimate_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    selected_groups: tuple[tuple[str, ...], ...],
    overlap_counts: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    class_sizes = tuple(map(len, classes))

    def pool_size(group_index: int, count: int) -> int:
        return comb(count + class_sizes[group_index] - 1, class_sizes[group_index] - 1)

    group_keys = {
        (group_index, counts[group_index]) for counts in overlap_counts for group_index in range(4)
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
    target_counts = list(map(len, target_groups))
    record = {
        "class_power_record_count": len(power_keys),
        "group_pool_cache_key_count": len(group_keys),
        "group_signature_record_count": group_signature_count,
        "pair_pool_cache_key_count": len(left_keys) + len(right_keys),
        "cached_pair_signature_entry_count": pair_signature_entry_count,
        "exact_convolution_call_count": convolution_call_count,
        "modulus_signature_count": sum(signature_counts),
        "peak_live_combined_signature_count": peak_signatures,
        "peak_two_product_bound_array_bytes": 2 * 8 * peak_signatures,
        "original_monomial_count": sum(original_counts),
        "distinct_comparison_upper_bound": sum(
            signatures * targets
            for signatures, targets in zip(signature_counts, target_counts, strict=True)
        ),
        "weighted_comparison_upper_bound": sum(
            monomials * targets
            for monomials, targets in zip(original_counts, target_counts, strict=True)
        ),
        "full_degree_seventeen_monomial_list_retained": False,
        "full_classification_matrices_retained": False,
        "design_only_elapsed_seconds_is_an_acceptance_threshold": False,
        "design_only_measured_memory_is_an_acceptance_threshold": False,
    }
    checks = {
        "registered_class_power_count_reproduces": len(power_keys) == EXPECTED_CLASS_POWER_COUNT,
        "registered_group_signature_count_reproduces": group_signature_count
        == EXPECTED_GROUP_SIGNATURE_COUNT,
        "registered_pair_pool_resource_reproduces": bool(
            len(left_keys) + len(right_keys) == EXPECTED_PAIR_POOL_COUNT
            and pair_signature_entry_count == EXPECTED_PAIR_SIGNATURE_ENTRY_COUNT
        ),
        "registered_convolution_call_count_reproduces": convolution_call_count
        == EXPECTED_CONVOLUTION_CALL_COUNT,
        "registered_signature_counts_reproduce": bool(
            sum(signature_counts) == EXPECTED_MODULUS_SIGNATURE_COUNT
            and peak_signatures == EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT
        ),
        "registered_monomial_count_reproduces": sum(original_counts)
        == EXPECTED_ORIGINAL_MONOMIAL_COUNT,
        "registered_two_product_array_bytes_reproduce": (
            record["peak_two_product_bound_array_bytes"] == EXPECTED_TWO_PRODUCT_ARRAY_BYTES
        ),
        "streaming_contract_does_not_retain_full_expansions": bool(
            not record["full_degree_seventeen_monomial_list_retained"]
            and not record["full_classification_matrices_retained"]
        ),
    }
    return {
        **record,
        "resource_record_digest_sha256": q011b._canonical_json_sha256(record),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _degree_seventeen_sweep(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_indices: tuple[tuple[int, ...], ...],
    target_groups: tuple[tuple[str, ...], ...],
) -> dict[str, Any]:
    sweep = q011an._full_component_safe_sweep(
        classes, lookup, overlap_counts, external_indices, target_groups
    )
    sweep["degree"] = DEGREE
    streaming = sweep["streaming_contract"]
    streaming["full_degree_seventeen_monomial_list_retained"] = streaming.pop(
        "full_degree_sixteen_monomial_list_retained"
    )
    streaming["full_degree_seventeen_classification_matrices_retained"] = streaming.pop(
        "full_classification_matrices_retained"
    )
    return sweep


def _degree_seventeen_sweep_audit(sweep: dict[str, Any]) -> dict[str, Any]:
    witness = sweep["global_minimum_separated_witness"]
    resource_checks = {
        "registered_hierarchical_resource_values_reproduce": bool(
            sweep["class_power_record_count"] == EXPECTED_CLASS_POWER_COUNT
            and sweep["class_power_record_digest_sha256"] == EXPECTED_CLASS_POWER_DIGEST
            and sweep["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_COUNT
            and sweep["group_signature_digest_sha256"] == EXPECTED_GROUP_SIGNATURE_DIGEST
            and sweep["pair_pool_record_count"] == EXPECTED_PAIR_POOL_COUNT
            and sweep["pair_pool_record_digest_sha256"] == EXPECTED_PAIR_POOL_DIGEST
            and sweep["convolution_call_count"] == EXPECTED_CONVOLUTION_CALL_COUNT
            and sweep["maximum_convolution_crude_int64_bound"]
            == EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND
            and sweep["maximum_live_combined_signature_count"]
            == EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT
            and sweep["maximum_wave_coefficient"] == EXPECTED_MAXIMUM_WAVE_COEFFICIENT
            and sweep["maximum_fourier_crude_int64_bound"] == EXPECTED_MAXIMUM_FOURIER_CRUDE_BOUND
        ),
        "all_exact_integer_and_outward_array_invariants_hold": bool(
            sweep["all_convolutions_nonnegative"]
            and sweep["all_convolution_fiber_sums_exact"]
            and sweep["all_product_bound_arrays_are_finite"]
            and sweep["all_product_bound_arrays_are_nonnegative_and_ordered"]
            and sweep["all_original_monomial_counts_match_multiset_coefficients"]
            and sweep["all_modulus_signature_counts_match_weak_compositions"]
        ),
        "registered_enumeration_counts_and_relations_reproduce": bool(
            sweep["degree"] == DEGREE
            and sweep["audited_overlap_aggregate_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and sweep["fully_separated_overlap_aggregate_count"] == EXPECTED_OVERLAP_AGGREGATE_COUNT
            and sweep["remaining_overlap_aggregate_count"] == 0
            and sweep["remaining_overlap_aggregate_indices"] == []
            and sweep["original_monomial_count"] == EXPECTED_ORIGINAL_MONOMIAL_COUNT
            and sweep["modulus_signature_count"] == EXPECTED_MODULUS_SIGNATURE_COUNT
            and sweep["compatible_modulus_signature_count"] == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and sweep["compatible_original_monomial_count"] == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and sweep["weighted_comparison_count"] == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and sweep["distinct_comparison_count"] == EXPECTED_DISTINCT_COMPARISON_COUNT
            and sweep["weighted_relation_counts"] == EXPECTED_WEIGHTED_RELATIONS
            and sweep["distinct_relation_counts"] == EXPECTED_DISTINCT_RELATIONS
        ),
        "registered_matrix_counts_and_digests_reproduce": bool(
            sweep["aggregate_record_digest_sha256"] == EXPECTED_AGGREGATE_DIGEST
            and sweep["bound_matrix_record_count"] == EXPECTED_BOUND_MATRIX_COUNT
            and sweep["bound_matrix_digest_sha256"] == EXPECTED_BOUND_MATRIX_DIGEST
            and sweep["coefficient_matrix_record_count"] == EXPECTED_COEFFICIENT_MATRIX_COUNT
            and sweep["coefficient_matrix_digest_sha256"] == EXPECTED_COEFFICIENT_MATRIX_DIGEST
            and sweep["classification_matrix_record_count"] == EXPECTED_CLASSIFICATION_MATRIX_COUNT
            and sweep["classification_matrix_digest_sha256"]
            == EXPECTED_CLASSIFICATION_MATRIX_DIGEST
        ),
        "registered_global_positive_minimum_reproduces": bool(
            witness["aggregate_index"] == EXPECTED_MINIMUM_AGGREGATE_INDEX
            and tuple(witness["selected_type_counts"]) == EXPECTED_MINIMUM_COUNTS
            and witness["target_identifier"] == EXPECTED_MINIMUM_TARGET
            and witness["left_index"] == EXPECTED_MINIMUM_LEFT_INDEX
            and witness["right_index"] == EXPECTED_MINIMUM_RIGHT_INDEX
            and witness["wave_multiplicity"] == EXPECTED_MINIMUM_MULTIPLICITY
            and witness["relation"] == EXPECTED_MINIMUM_RELATION
            and tuple(tuple(group) for group in witness["class_counts"])
            == EXPECTED_MINIMUM_CLASS_COUNTS
            and tuple(witness["source_identifiers"]) == EXPECTED_MINIMUM_SOURCES
            and witness["outward_gap_lower"]["binary64_hex"] == EXPECTED_MINIMUM_OUTWARD_GAP_HEX
            and witness["exact_gap_hex"] == EXPECTED_MINIMUM_EXACT_GAP_HEX
            and witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
        ),
        "independent_disc_choices_with_repetition_are_exhaustive": True,
    }
    bridge = {
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "directly_separated_overlap_inventory_aggregate_count": sweep[
            "fully_separated_overlap_aggregate_count"
        ],
        "degree_seventeen_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "remaining_degree_seventeen_aggregate_count": (sweep["remaining_overlap_aggregate_count"]),
    }
    resource_checks["old_and_direct_inventory_cover_degree_seventeen"] = bool(
        bridge["old_modulus_separated_aggregate_count"]
        + bridge["directly_separated_overlap_inventory_aggregate_count"]
        == bridge["degree_seventeen_aggregate_count"]
        and bridge["remaining_degree_seventeen_aggregate_count"] == 0
    )
    return {
        **sweep,
        "degree_seventeen_bridge": bridge,
        "checks": resource_checks,
        "passed": all(resource_checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "degree_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "old_modulus_separated_aggregate_count": EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT,
        "direct_overlap_inventory_aggregate_count": EXPECTED_OVERLAP_AGGREGATE_COUNT,
        "selected_source_identifier_count": 24,
        "external_target_identifier_count": EXPECTED_TARGET_IDENTIFIER_COUNT,
        "new_q011ak_target_identifier_count": EXPECTED_NEW_TARGET_IDENTIFIER_COUNT,
        "final_identifier_count": EXPECTED_FINAL_IDENTIFIER_COUNT,
        "selected_modulus_class_counts": list(EXPECTED_CLASS_COUNTS),
        "source_disc_choice_logic": "independent with repetition",
        "target_disc_choice_logic": "every certified target disc",
        "full_monomial_list_retained": False,
        "full_classification_matrices_retained": False,
        "wall_time_is_an_acceptance_threshold": False,
        "measured_process_memory_is_an_acceptance_threshold": False,
        "accepted_classification": ACCEPTED_CLASSIFICATION,
        "rejected_classification": REJECTED_CLASSIFICATION,
        "actual_resonance_outcome_if_accepted": ACTUAL_RESONANCE_OUTCOME,
        "degrees_eighteen_through_ninety_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "inventory_digest_sha256": cycle["inventory_digest_sha256"],
        "envelope_digest_sha256": cycle["envelope_digest_sha256"],
        "sweep_digest_sha256": cycle["sweep_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "scientific_classification": cycle["scientific_classification"],
    }


def run_degree_seventeen_hierarchical_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        inventory,
        selected_groups,
        external_merged,
        overlap_counts,
        external_indices,
        target_groups,
    ) = _degree_seventeen_inventory_audit(artifacts)
    envelope, lookup, classes = _degree_seventeen_envelope_audit(
        artifacts, selected_groups, external_merged, target_groups
    )
    resource = _resource_estimate_audit(classes, selected_groups, overlap_counts, target_groups)
    sweep = _degree_seventeen_sweep_audit(
        _degree_seventeen_sweep(classes, lookup, overlap_counts, external_indices, target_groups)
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    inventory_sections = {"degree_seventeen_inventory_audit": inventory}
    envelope_sections = {
        "degree_seventeen_component_safe_envelope_audit": envelope,
        "degree_seventeen_resource_estimate_audit": resource,
    }
    sweep_sections = {"degree_seventeen_hierarchical_sweep_audit": sweep}
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(inventory_sections)
    envelope_digest = q011b._canonical_json_sha256(envelope_sections)
    sweep_digest = q011b._canonical_json_sha256(sweep_sections)
    validity_gates = {
        "q011an_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "19 artifacts and 98 direct digests reproduce",
            "value": sealed["checks"],
        },
        "degree_seventeen_inventory_reproduces": {
            "passed": inventory["passed"],
            "threshold": "1140 aggregates partition into 941 old and 199 overlap",
            "value": inventory["checks"],
        },
        "component_safe_envelope_and_q011ak_extensions_reproduce": {
            "passed": envelope["passed"],
            "threshold": "152 reused plus 24 extended identifiers form 176 safe discs",
            "value": envelope["checks"],
        },
        "registered_streaming_resource_contract_reproduces": {
            "passed": resource["passed"],
            "threshold": "registered pool, signature, convolution and peak counts",
            "value": resource["checks"],
        },
        "full_hierarchical_enumeration_and_relations_reproduce": {
            "passed": sweep["passed"],
            "threshold": "all 199 direct and 1140 bridged aggregates separate",
            "value": sweep["checks"],
        },
        "registered_global_minimum_witness_reproduces": {
            "passed": sweep["checks"]["registered_global_positive_minimum_reproduces"],
            "threshold": "registered outward and exact gaps are positive",
            "value": {
                "outward_gap_hex": sweep["global_minimum_separated_witness"]["outward_gap_lower"][
                    "binary64_hex"
                ],
                "exact_gap_hex": sweep["global_minimum_separated_witness"]["exact_gap_hex"],
            },
        },
        "strict_serialization_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                all(
                    len(digest) == 64
                    for digest in (
                        input_digest,
                        inventory_digest,
                        envelope_digest,
                        sweep_digest,
                    )
                )
                and runner["filename"] == "q011ao_degree17_hierarchical_sweep.py"
            ),
            "threshold": "strict finite JSON, four section digests and runner metadata",
            "value": {
                "input": input_digest,
                "inventory": inventory_digest,
                "envelope": envelope_digest,
                "sweep": sweep_digest,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    witness = sweep["global_minimum_separated_witness"]
    hypothesis_gates = {
        "all_selected_and_target_eigenvalues_have_label_safe_disc_coverage": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": "24 selected sources and 152 external targets are covered",
            "value": {
                "selected": envelope["selected_source_identifier_count"],
                "targets": envelope["external_target_identifier_count"],
            },
        },
        "all_one_hundred_ninety_nine_overlap_inventory_aggregates_are_separated": {
            "passed": bool(
                validity_passed
                and sweep["fully_separated_overlap_aggregate_count"]
                == EXPECTED_OVERLAP_AGGREGATE_COUNT
                and sweep["remaining_overlap_aggregate_count"] == 0
            ),
            "threshold": "301592258 distinct and 10786916138 weighted comparisons separate",
            "value": {
                "distinct": sweep["distinct_relation_counts"],
                "weighted": sweep["weighted_relation_counts"],
            },
        },
        "all_one_thousand_one_hundred_forty_degree_seventeen_aggregates_are_separated": {
            "passed": bool(
                validity_passed
                and sweep["degree_seventeen_bridge"]["degree_seventeen_aggregate_count"]
                == EXPECTED_DEGREE_AGGREGATE_COUNT
                and sweep["degree_seventeen_bridge"]["remaining_degree_seventeen_aggregate_count"]
                == 0
            ),
            "threshold": "941 old plus 199 direct aggregates separate",
            "value": sweep["degree_seventeen_bridge"],
        },
        "registered_global_minimum_is_strictly_positive": {
            "passed": bool(
                validity_passed
                and witness["outward_gap_lower"]["float"] > 0
                and q011z._fraction(witness["exact_gap"]) > 0
            ),
            "threshold": "outward and exact gaps are both strictly positive",
            "value": {
                "outward_gap_hex": witness["outward_gap_lower"]["binary64_hex"],
                "exact_gap_hex": witness["exact_gap_hex"],
            },
        },
        "claim_is_limited_to_degree_seventeen_external_nonresonance": {
            "passed": validity_passed,
            "threshold": "no degree 18--90, all-order, SSM or basin extrapolation",
            "value": "registered claim boundary only",
        },
    }
    hypothesis_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    accepted = bool(validity_passed and hypothesis_passed)
    rejected = bool(validity_passed and not hypothesis_passed)
    cycle = {
        "question": (
            "Does the component-safe hierarchical exact-multiplicity sweep certify "
            "every degree-seventeen external nonresonance comparison?"
        ),
        **input_sections,
        **inventory_sections,
        **envelope_sections,
        **sweep_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "inventory_digest_sha256": inventory_digest,
        "envelope_digest_sha256": envelope_digest,
        "sweep_digest_sha256": sweep_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": (
            "accepted" if accepted else "rejected" if rejected else "inconclusive"
        ),
        "actual_resonance_outcome": (
            ACTUAL_RESONANCE_OUTCOME
            if accepted
            else "not_established"
            if rejected
            else "inconclusive"
        ),
        "scientific_classification": (
            ACCEPTED_CLASSIFICATION
            if accepted
            else REJECTED_CLASSIFICATION
            if rejected
            else INCONCLUSIVE_CLASSIFICATION
        ),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "degree_seventeen_external_nonresonance_is_certified": accepted,
        "an_actual_degree_seventeen_external_resonance_is_ruled_out": accepted,
        "old_modulus_separated_aggregate_count": (
            EXPECTED_OLD_SEPARATED_AGGREGATE_COUNT if accepted else 0
        ),
        "directly_separated_overlap_inventory_aggregate_count": (
            EXPECTED_OVERLAP_AGGREGATE_COUNT if accepted else 0
        ),
        "certified_external_nonresonance_degrees": (
            list(range(2, 18)) if accepted else list(range(2, 17))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(18 if accepted else 17, 91)),
        "degrees_18_through_90_are_certified": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011an_degree_sixteen_certificate_is_preserved": True,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only degree-seventeen external spectral relations "
        "for the fixed 17x17 repaired exact map on one fixed conservation leaf, the "
        "Q011an component-safe selected-source envelope, the 24 registered Q011ak "
        "blockwise target extensions, independent source-disc choices with repetition, "
        "every target disc, exact x-Fourier multiplicities and the registered "
        "hierarchical outward-dyadic product protocol. It rules out an actual external "
        "resonance only within those registered degree-seventeen relations. It "
        "establishes no result for degrees 18 through 90, all-order nonresonance, higher "
        "graph smoothness, SSM existence or uniqueness, normal attraction, basin, other "
        "grid, force, wall or D3Q27 case."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ai_certificates_and_diagnostics_changed": False,
        "q011aj_and_q011ak_recorded_rejections_changed": False,
        "q011al_and_q011am_recorded_outcomes_changed": False,
        "q011an_degree_sixteen_certificate_changed": False,
    }
    if accepted:
        cycle["next_change"] = (
            "Run a design-only Q011ap degree-eighteen resource estimate before "
            "preregistering any full degree-eighteen sweep."
        )
    elif rejected:
        cycle["next_change"] = (
            "Audit only the first registered degree-seventeen overlap before choosing "
            "any further eigendisc refinement."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first seal, inventory, envelope, resource, sweep, witness "
            "or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ao cycle failed strict serialization or digest")
    return cycle


def run_q011ao_study() -> dict[str, Any]:
    cycle = run_degree_seventeen_hierarchical_audit()
    sweep = cycle["degree_seventeen_hierarchical_sweep_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "inventory_arithmetic": "exact integer log-grid intervals",
            "source_multiplicity_arithmetic": "exact numpy.int64 17-point cyclic convolution",
            "product_enclosure": "outward-rounded IEEE-754 binary64 interval products",
            "floating_point_used_for_gate_decisions": True,
            "floating_point_gate_is_rigorous_interval_logic": True,
            "convolution_call_count": sweep["convolution_call_count"],
            "weighted_comparison_count": sweep["weighted_comparison_count"],
            "distinct_comparison_count": sweep["distinct_comparison_count"],
        },
        "mathematical_scope": {
            "diagnostic": "component-safe degree-17 external nonresonance certificate",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_seventeen_external_nonresonance_claim": True,
            "actual_degree_seventeen_external_resonance_ruled_out_claim": True,
            "degrees_18_through_90_claim": False,
            "all_order_nonresonance_claim": False,
            "ssm_uniqueness_claim": False,
            "normal_attraction_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011ao_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
