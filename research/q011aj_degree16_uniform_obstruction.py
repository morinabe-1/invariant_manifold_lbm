"""Q011aj degree-sixteen first uniform-envelope obstruction certificate."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from math import inf
from pathlib import Path
from typing import Any

import numpy as np

import research.q011ai_degree15_dual_outcome as q011ai
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

q011ag = q011ai.q011ag
q011b = q011ai.q011b
q011u = q011ai.q011u
q011z = q011ai.q011z

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
DEGREE = 16
EXPECTED_DEGREE_AGGREGATE_COUNT = 969
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 20_349
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 815
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 154
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_EXTERNAL_GROUP_INDICES = (
    148,
    151,
    152,
    153,
    154,
    155,
    156,
    157,
    159,
    162,
    165,
    166,
    167,
)
EXPECTED_MULTI_TARGET_AGGREGATE_INDEX = 73
EXPECTED_MULTI_TARGET_COUNTS = (4, 6, 2, 4)
EXPECTED_MULTI_TARGET_EXTERNAL_GROUPS = (156, 157)
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 136
EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT = 160
EXPECTED_RELEVANT_IDENTIFIER_COUNT = 204
EXPECTED_NEW_IDENTIFIER_COUNT = 60
EXPECTED_UNIQUE_CENTER_MODULUS_EVALUATION_COUNT = 114
EXPECTED_MODULUS_CLASS_COUNTS = (4, 2, 3, 6)

UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
EXPECTED_INVENTORY_DIGEST = "63d3e8edb49292d7674037800525c53f590ec78cfc9163acb09bb91c0fc108c1"
EXPECTED_UNIFORM_RECORD_DIGEST = (
    "bad945dbf84eeba3d5f54f9fa4938c7b15c1d918f83ffdc7252e7a6b8267c204"
)
EXPECTED_PREFIX_COUNT = 100
EXPECTED_PREFIX_DIGEST = "2ae58d4e4bb63a68733c23beae78037faa3aaf3f57549028a76808183e35ed91"
EXPECTED_OBSTRUCTION_AGGREGATE_INDEX = 99
EXPECTED_OBSTRUCTION_COUNTS = (5, 6, 4, 1)
EXPECTED_OBSTRUCTION_EXTERNAL_GROUPS = (155,)
EXPECTED_OBSTRUCTION_TARGETS = (
    "block=11;center=3",
    "block=11;center=4",
    "block=6;center=3",
    "block=6;center=4",
)
EXPECTED_OBSTRUCTION_SIGNATURE_COUNT = 35_280
EXPECTED_OBSTRUCTION_COMPATIBLE_MONOMIAL_COUNT = 1_732_864
EXPECTED_OBSTRUCTION_WEIGHTED_COMPARISON_COUNT = 3_465_728
EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT = 141_120
EXPECTED_OBSTRUCTION_DIGEST = (
    "448da50fd34eae26d2b1e01c753af0cd901bb2a849ccfca2a05ab73f564a3cd6"
)
EXPECTED_MAXIMUM_WAVE_COEFFICIENT = 1_142
EXPECTED_MAXIMUM_CRUDE_INT64_DOT_PRODUCT_BOUND = 7_140
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 900_900

EXPECTED_CENTER_THREE_MINIMUM_HEX = "0x1.1894daaffffffp-25"
EXPECTED_CENTER_FOUR_MINIMUM_HEX = "0x1.1894d72ffffffp-25"
EXPECTED_CENTER_RECORD_DIGEST = (
    "da33cde69a774719bed414e8b79b1f3ffd2c6086e96e0ae770cba52000854b4b"
)
EXPECTED_EXACT_CENTER_CANDIDATE_COUNT = 28
EXPECTED_EXACT_CENTER_CANDIDATE_DIGEST = (
    "7abedfc2fbd68b92baf6df17427e19846d608289974dafb972ce2b664427950b"
)
EXPECTED_EXACT_CENTER_MINIMUM_HEX = "0x1.1894d8f4a9740p-25"
EXPECTED_EXACT_CENTER_MINIMUM_TIE_COUNT = 2
EXPECTED_CANONICAL_CLASS_COUNTS = (
    (5, 0, 0, 0),
    (0, 6),
    (0, 0, 4),
    (0, 0, 0, 1, 0, 0),
)
EXPECTED_CANONICAL_SOURCE_IDENTIFIERS = (
    "block=16;center=142",
    "block=16;center=142",
    "block=1;center=142",
    "block=1;center=142",
    "block=1;center=142",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=151",
    "block=1;center=152",
    "block=1;center=152",
    "block=1;center=152",
    "block=1;center=152",
    "block=0;center=147",
)
EXPECTED_UNIFORM_INTERSECTION_BASE_WIDTH = Fraction(1, 10**7)
EXPECTED_UNIFORM_INTERSECTION_WIDTH_HEX = "0x1.ad7f29abcaf48p-24"
EXPECTED_UNIFORM_INTERSECTION_EXCESS_HEX = "0x1.bff2ee48e0530p-333"
EXPECTED_UNIFORM_INTERSECTION_EXCESS_DIGEST = (
    "013784fb645298711cabed645e63cc80fa9d5ee661185a111165158ea6d29b42"
)
EXPECTED_WITNESS_DIGEST = "c570b77d2ce20ea1057f36e59e5e1152982af74aaef2f984f85495003e61f57a"

Q011AI_ARTIFACT_SHA256 = "3df99d9517f25730ca00d4fc1c500a4b0fe1dd03c7812477463f9d6d19ced3e3"
Q011AI_RUNNER_SHA256 = "48fb083497a50b6ba6e3e3de1557a231bb53901acaec25b17806c0c96404187b"
Q011AI_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "compression_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)
Q011AI_DIGESTS = (
    "54f599a25c3bde94887c47f93f926e79798151877548f0ea98c29d73d0c67c0e",
    "14b04d7d05d719e112661f69009224169e9722626991f11ebd43aa456c2043a5",
    "7d74819f4cfcd5a00ce04e3e55c086dd7a88035ca2ba7b09a387988514b89225",
    "2b4fd586a9f478df3e9f4f007badceca293b0658388e9cde2a2d60e2a8d3adcf",
    "7981bff291a3aa5b5c518b189047c80fb73711bb2c6dd23aad55668ef96eda91",
)

UNIFORM_CERTIFICATE_REJECTED_CLASSIFICATION = (
    "the degree-16 uniform-rho external nonresonance certificate is rejected "
    "at the first fully unresolved aggregate"
)
ACTUAL_RESONANCE_NOT_ESTABLISHED_CLASSIFICATION = (
    "an actual degree-16 complex resonance is not established; all center-only "
    "comparisons at the obstruction are separated"
)
COMBINED_CLASSIFICATION = (
    f"{UNIFORM_CERTIFICATE_REJECTED_CLASSIFICATION}; "
    f"{ACTUAL_RESONANCE_NOT_ESTABLISHED_CLASSIFICATION}"
)


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011ai._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ai_degree15_dual_outcome.json"
    runner_path = Path(q011ai.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AI_DIGEST_NAMES)
    checks = {
        "q011ai_thirteen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 68
            and all(prior["checks"].values())
        ),
        "q011ai_artifact_sha256_matches": _file_sha256(artifact_path)
        == Q011AI_ARTIFACT_SHA256,
        "q011ai_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AI_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AI_RUNNER_SHA256
        ),
        "q011ai_digests_match": digests == Q011AI_DIGESTS,
        "q011ai_registered_dual_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and artifact["legacy_margin_outcome"] == "rejected"
            and cycle["scientific_classification"] == q011ai.COMBINED_ACCEPTED_CLASSIFICATION
        ),
        "q011ai_degree_fifteen_scope_is_preserved": bool(
            cycle["theorem_consequence"][
                "degree_fifteen_external_nonresonance_is_certified"
            ]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == list(range(2, 16))
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(16, 91))
            and not cycle["theorem_consequence"]["ssm_existence_or_uniqueness_is_certified"]
        ),
        "q011ai_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ai_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ai_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "seventy_three_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 73
        ),
    }
    artifacts["q011ai"] = artifact
    audit = {
        "prior_q011ai_sealed_input_audit": prior,
        "q011ai": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AI_DIGEST_NAMES),
            "digests": list(digests),
            "scientific_classification": cycle["scientific_classification"],
        },
        "direct_digest_count": prior["direct_digest_count"] + len(digests),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _inventory_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[tuple[str, ...], ...],
    tuple[tuple[str, ...], ...],
    tuple[dict[str, Any], ...],
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
    logs = u_cycle["rational_log_enclosure_audit"]
    selected_logs = tuple(q011z._scaled_log_pair(record) for record in logs["selected_log_records"])
    external_logs = tuple(q011z._scaled_log_pair(record) for record in logs["external_log_records"])
    overlap_records: list[dict[str, Any]] = []
    external_target_groups: list[tuple[str, ...]] = []
    for counts in q011z._count_tuples(DEGREE):
        aggregate_lower = sum(
            count * interval[0]
            for count, interval in zip(counts, selected_logs, strict=True)
        )
        aggregate_upper = sum(
            count * interval[1]
            for count, interval in zip(counts, selected_logs, strict=True)
        )
        external_indices = [
            index
            for index, (lower, upper) in enumerate(external_logs)
            if lower <= aggregate_upper and upper >= aggregate_lower
        ]
        if not external_indices:
            continue
        identifiers = tuple(
            sorted(
                set().union(
                    *(set(external_merged[index].identifiers) for index in external_indices)
                )
            )
        )
        overlap_records.append(
            {
                "selected_type_counts": list(counts),
                "aggregate_log_interval": q011u._scaled_log_record(
                    q011u._ScaledLogInterval(aggregate_lower, aggregate_upper)
                ),
                "external_group_indices": external_indices,
                "external_log_intervals": [
                    q011u._scaled_log_record(q011u._ScaledLogInterval(*external_logs[index]))
                    for index in external_indices
                ],
            }
        )
        external_target_groups.append(identifiers)
    external_index_groups = tuple(
        tuple(record["external_group_indices"]) for record in overlap_records
    )
    exact_inventory = {
        "selected_source_groups": [
            {"group_index": index, "identifiers": list(group)}
            for index, group in enumerate(selected_groups)
        ],
        "overlap_records": overlap_records,
        "external_target_groups": [
            {
                "aggregate_index": aggregate_index,
                "external_group_indices": list(external_indices),
                "identifiers": list(group),
            }
            for aggregate_index, (external_indices, group) in enumerate(
                zip(external_index_groups, external_target_groups, strict=True)
            )
        ],
    }
    exact_digest = q011b._canonical_json_sha256(exact_inventory)
    multi = [
        index for index, indices in enumerate(external_index_groups) if len(indices) > 1
    ]
    stored_selected = stored_spectrum["selected_merged_records"]
    stored_external = stored_spectrum["external_merged_records"]
    unique_external_indices = tuple(
        sorted({index for indices in external_index_groups for index in indices})
    )
    first_overlap = degree_record["first_overlap"]
    checks = {
        "q011u_old_modulus_spectrum_reconstructs_exactly": bool(
            reconstructed["passed"] and reconstructed == stored_spectrum
        ),
        "q011u_degree_sixteen_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"]
            == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_154_overlaps_and_external_groups_reproduce": bool(
            len(overlap_records) == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
            and all(len(indices) in (1, 2) for indices in external_index_groups)
            and unique_external_indices == EXPECTED_EXTERNAL_GROUP_INDICES
            and tuple(first_overlap["selected_type_counts"])
            == tuple(overlap_records[0]["selected_type_counts"])
            and first_overlap["external_group_index"] == external_index_groups[0][0]
        ),
        "exactly_one_registered_multi_target_overlap_reproduces": bool(
            multi == [EXPECTED_MULTI_TARGET_AGGREGATE_INDEX]
            and tuple(
                overlap_records[EXPECTED_MULTI_TARGET_AGGREGATE_INDEX]["selected_type_counts"]
            )
            == EXPECTED_MULTI_TARGET_COUNTS
            and external_index_groups[EXPECTED_MULTI_TARGET_AGGREGATE_INDEX]
            == EXPECTED_MULTI_TARGET_EXTERNAL_GROUPS
        ),
        "selected_source_memberships_and_sizes_reproduce": bool(
            tuple(len(group) for group in selected_groups) == EXPECTED_SELECTED_GROUP_SIZES
            and all(
                q011b._canonical_json_sha256(list(group))
                == stored_selected[index]["membership_digest_sha256"]
                for index, group in enumerate(selected_groups)
            )
        ),
        "all_external_memberships_and_target_unions_reproduce": bool(
            all(
                q011b._canonical_json_sha256(
                    sorted(external_merged[external_index].identifiers)
                )
                == stored_external[external_index]["membership_digest_sha256"]
                for external_index in unique_external_indices
            )
            and len(set().union(*map(set, external_target_groups)))
            == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
        ),
        "q011ai_degree_fifteen_certificate_is_preserved": artifacts["q011ai"]["cycle"][
            "theorem_consequence"
        ]["degree_fifteen_external_nonresonance_is_certified"],
        "registered_exact_inventory_digest_reproduces": exact_digest
        == EXPECTED_INVENTORY_DIGEST,
        "inventory_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(exact_inventory)
            and _strict_json_serializable(exact_inventory)
            and json.dumps(exact_inventory, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "degree_modulus_aggregate_count": degree_record["aggregate_count"],
        "degree_expanded_product_control_count": degree_record[
            "expanded_product_control_count"
        ],
        "old_modulus_separated_aggregate_count": degree_record["nonoverlap_count"],
        "old_modulus_overlap_aggregate_count": degree_record["overlap_count"],
        "overlap_records": overlap_records,
        "selected_source_group_sizes": [len(group) for group in selected_groups],
        "selected_source_group_memberships": [list(group) for group in selected_groups],
        "unique_external_group_indices": list(unique_external_indices),
        "multi_target_aggregate_indices": multi,
        "external_target_groups": exact_inventory["external_target_groups"],
        "unique_external_target_count": len(
            set().union(*map(set, external_target_groups))
        ),
        "old_spectrum_digest_sha256": q011b._canonical_json_sha256(reconstructed),
        "exact_inventory_digest_sha256": exact_digest,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, selected_groups, tuple(external_target_groups), tuple(overlap_records)


def _uniform_envelope_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
) -> tuple[dict[str, Any], dict[str, q011z._UniformDisc]]:
    centers, selected, old_radii, metrics, reconstruction = q011z.q011l._spectral_data(
        artifacts["q011k"]
    )
    y_cycle = artifacts["q011y"]["cycle"]
    y_radius = y_cycle["exact_radius_refinement_audit"]
    y_containment = y_cycle["all_eigendisc_containment_audit"]
    theta = {block: metrics[block]["theta"] for block in range(SIZE)}
    maximum_theta_block = max(range(SIZE), key=theta.__getitem__)
    minimum_old_radius_block = min(range(SIZE), key=old_radii.__getitem__)
    selected_identifiers = set().union(*map(set, selected_groups))
    external_identifiers = set().union(*map(set, external_target_groups))
    directly_relevant = selected_identifiers | external_identifiers
    prior_records = {
        record["identifier"]: record
        for record in artifacts["q011ai"]["cycle"]["uniform_refined_envelope_audit"][
            "uniform_disc_records"
        ]
    }
    relevant_identifiers = sorted(directly_relevant | set(prior_records))
    selected_sets = {block: frozenset(indices) for block, indices in selected.items()}
    modulus_cache: dict[tuple[Fraction, Fraction], RationalInterval] = {}
    lookup: dict[str, q011z._UniformDisc] = {}
    records = []
    for identifier in relevant_identifiers:
        block, center_index = q011z._identifier_indices(identifier)
        center = centers[block][center_index]
        key = (abs(center[0]), abs(center[1]))
        if key not in modulus_cache:
            modulus_cache[key] = q011z.q011o._center_modulus_bounds(center)
        center_modulus = modulus_cache[key]
        modulus = RationalInterval(
            max(Fraction(0), center_modulus.lower - UNIFORM_REFINED_RADIUS),
            center_modulus.upper + UNIFORM_REFINED_RADIUS,
        )
        disc = q011z._UniformDisc(
            identifier=identifier,
            block_index=block,
            center_index=center_index,
            center_modulus=center_modulus,
            modulus=modulus,
        )
        lookup[identifier] = disc
        records.append(
            {
                "identifier": identifier,
                "block_index": block,
                "center_index": center_index,
                "selected": center_index in selected_sets.get(block, frozenset()),
                "center_modulus_lower": q011z._exact_fraction_record(center_modulus.lower),
                "center_modulus_upper": q011z._exact_fraction_record(center_modulus.upper),
                "uniform_modulus_lower": q011z._exact_fraction_record(modulus.lower),
                "uniform_modulus_upper": q011z._exact_fraction_record(modulus.upper),
            }
        )
    current_records = {record["identifier"]: record for record in records}
    new_identifiers = set(current_records) - set(prior_records)
    record_digest = q011b._canonical_json_sha256(records)
    checks = {
        "q011l_reconstructs_all_seventeen_blocks": reconstruction["passed"],
        "q011y_registered_maximum_theta_reproduces": bool(
            theta[maximum_theta_block] == q011z._fraction(y_radius["maximum_refined_radius_upper"])
            and maximum_theta_block in (4, 13)
            and y_radius["passed"]
        ),
        "all_theta_discs_are_contained_in_the_uniform_envelope": all(
            0 < theta[block] <= UNIFORM_REFINED_RADIUS for block in range(SIZE)
        ),
        "all_uniform_discs_are_contained_in_q011k_discs": all(
            UNIFORM_REFINED_RADIUS <= old_radii[block] for block in range(SIZE)
        ),
        "q011y_all_2598_containment_and_stability_is_preserved": bool(
            y_containment["passed"]
            and y_containment["eigendisc_count"] == COORDINATE_SLOT_COUNT
            and y_cycle["theorem_consequence"][
                "transformed_residual_eigendisc_inclusion_is_certified"
            ]
        ),
        "all_160_direct_and_204_monotone_identifiers_have_uniform_intervals": bool(
            len(lookup) == EXPECTED_RELEVANT_IDENTIFIER_COUNT
            and len(directly_relevant) == EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT
            and len(selected_identifiers) == SELECTED_DIMENSION
            and len(external_identifiers) == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
            and selected_identifiers.isdisjoint(external_identifiers)
            and len(modulus_cache) == EXPECTED_UNIQUE_CENTER_MODULUS_EVALUATION_COUNT
        ),
        "source_and_target_roles_reproduce": bool(
            all(
                disc.center_index in selected_sets.get(disc.block_index, frozenset())
                for identifier, disc in lookup.items()
                if identifier in selected_identifiers
            )
            and all(
                disc.center_index not in selected_sets.get(disc.block_index, frozenset())
                for identifier, disc in lookup.items()
                if identifier in external_identifiers
            )
        ),
        "all_q011ai_144_uniform_records_are_preserved_exactly": bool(
            len(prior_records) == 144
            and set(prior_records).issubset(current_records)
            and all(current_records[identifier] == record for identifier, record in prior_records.items())
        ),
        "exactly_sixty_new_external_records_are_added": bool(
            len(new_identifiers) == EXPECTED_NEW_IDENTIFIER_COUNT
            and new_identifiers == external_identifiers - set(prior_records)
        ),
        "registered_uniform_record_digest_reproduces": record_digest
        == EXPECTED_UNIFORM_RECORD_DIGEST,
        "uniform_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    audit = {
        "active_selected_group_indices": list(range(len(selected_groups))),
        "uniform_radius": _fraction_record(UNIFORM_REFINED_RADIUS),
        "uniform_radius_formula": "rho=1/20,000,000=5e-8",
        "maximum_transformed_residual_radius": _fraction_record(theta[maximum_theta_block]),
        "maximum_theta_block": maximum_theta_block,
        "minimum_q011k_old_radius": _fraction_record(old_radii[minimum_old_radius_block]),
        "minimum_old_radius_block": minimum_old_radius_block,
        "directly_relevant_identifier_count": len(directly_relevant),
        "relevant_identifier_count": len(lookup),
        "unique_center_modulus_evaluation_count": len(modulus_cache),
        "new_external_identifiers": sorted(new_identifiers),
        "uniform_disc_records": records,
        "uniform_record_digest_sha256": record_digest,
        "containment_chain": (
            "spectrum subset union D(c_j,theta_b) subset union D(c_j,rho) "
            "subset union D(c_j,r_old,b)"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup


def _relation_counts(counter: Counter[str]) -> dict[str, int]:
    return {
        "overlap": counter["overlap"],
        "product_below_target": counter["product_below_target"],
        "target_below_product": counter["target_below_product"],
    }


def _first_uniform_obstruction_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_index_groups: tuple[tuple[int, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
) -> tuple[dict[str, Any], tuple[int, ...], tuple[str, ...]]:
    group_cache: dict[tuple[int, int], tuple[q011ag._GroupSignature, ...]] = {}

    def group_pool(group_index: int, count: int) -> tuple[q011ag._GroupSignature, ...]:
        key = (group_index, count)
        if key not in group_cache:
            group_cache[key] = q011ag._group_signature(classes, lookup, group_index, count)
        return group_cache[key]

    prefix_records = []
    maximum_wave_coefficient = 0
    maximum_crude_bound = 0
    maximum_live_signature_count = 0
    all_arrays_finite = True
    all_bounds_ordered = True
    obstruction_counts: tuple[int, ...] | None = None
    obstruction_targets: tuple[str, ...] | None = None
    for aggregate_index, (counts, external_indices, target_group) in enumerate(
        zip(overlap_counts, external_index_groups, external_target_groups, strict=True)
    ):
        group_pools = tuple(
            group_pool(group_index, count) for group_index, count in enumerate(counts)
        )
        left = q011ag._pair_signatures(group_pools[0], group_pools[1])
        right = q011ag._pair_signatures(group_pools[2], group_pools[3])
        left_wave = np.stack([record.wave for record in left])
        right_wave = np.stack([record.wave for record in right])
        product_lower, product_upper = q011ag._product_bound_matrices(left, right)
        signature_count = len(left) * len(right)
        maximum_live_signature_count = max(maximum_live_signature_count, signature_count)
        all_arrays_finite = bool(
            all_arrays_finite
            and np.isfinite(product_lower).all()
            and np.isfinite(product_upper).all()
        )
        all_bounds_ordered = bool(
            all_bounds_ordered
            and np.all(product_lower >= 0)
            and np.all(product_lower <= product_upper)
        )
        compatible = np.zeros(product_lower.shape, dtype=bool)
        compatible_monomial_count = 0
        weighted_comparison_count = 0
        distinct_comparison_count = 0
        weighted_relations: Counter[str] = Counter()
        distinct_relations: Counter[str] = Counter()
        for output_block, target_identifiers in q011ag._target_groups_by_block(
            target_group
        ).items():
            wave_matrix, crude_bound = q011ag._wave_matrix(
                left_wave, right_wave, output_block
            )
            maximum_crude_bound = max(maximum_crude_bound, crude_bound)
            maximum_wave_coefficient = max(
                maximum_wave_coefficient, int(wave_matrix.max(initial=0))
            )
            active = wave_matrix > 0
            compatible |= active
            compatible_monomial_count += int(wave_matrix.sum())
            weighted_comparison_count += int(wave_matrix.sum()) * len(target_identifiers)
            distinct_comparison_count += int(active.sum()) * len(target_identifiers)
            for target_identifier in target_identifiers:
                target = lookup[target_identifier]
                product_below = active & (
                    q011ag._down_subtract(
                        q011ag._fraction_lower(target.modulus.lower), product_upper
                    )
                    > 0
                )
                target_below = active & (
                    q011ag._down_subtract(
                        product_lower, q011ag._fraction_upper(target.modulus.upper)
                    )
                    > 0
                )
                unresolved = active & ~(product_below | target_below)
                for relation, mask in (
                    ("product_below_target", product_below),
                    ("target_below_product", target_below),
                    ("overlap", unresolved),
                ):
                    weighted_relations[relation] += int(wave_matrix[mask].sum())
                    distinct_relations[relation] += int(mask.sum())
        record = {
            "aggregate_index": aggregate_index,
            "selected_type_counts": list(counts),
            "external_group_indices": list(external_indices),
            "target_identifier_count": len(target_group),
            "modulus_signature_count": signature_count,
            "compatible_modulus_signature_count": int(compatible.sum()),
            "compatible_original_monomial_count": compatible_monomial_count,
            "weighted_comparison_count": weighted_comparison_count,
            "distinct_comparison_count": distinct_comparison_count,
            "weighted_relation_counts": _relation_counts(weighted_relations),
            "distinct_relation_counts": _relation_counts(distinct_relations),
            "has_outward_separated_comparison": bool(
                distinct_relations["product_below_target"]
                + distinct_relations["target_below_product"]
            ),
        }
        prefix_records.append(record)
        if not record["has_outward_separated_comparison"]:
            obstruction_counts = counts
            obstruction_targets = target_group
            break
    if obstruction_counts is None or obstruction_targets is None:
        raise RuntimeError("Q011aj found no fully unresolved uniform-envelope aggregate")
    prefix_digest = q011b._canonical_json_sha256(prefix_records)
    obstruction_record = prefix_records[-1]
    obstruction_digest = q011b._canonical_json_sha256(obstruction_record)
    checks = {
        "registered_first_hundred_record_prefix_reproduces": bool(
            len(prefix_records) == EXPECTED_PREFIX_COUNT
            and prefix_digest == EXPECTED_PREFIX_DIGEST
        ),
        "indices_zero_through_ninety_eight_have_a_separated_comparison": all(
            record["has_outward_separated_comparison"] for record in prefix_records[:-1]
        ),
        "index_ninety_nine_is_the_first_fully_unresolved_aggregate": bool(
            obstruction_record["aggregate_index"] == EXPECTED_OBSTRUCTION_AGGREGATE_INDEX
            and tuple(obstruction_record["selected_type_counts"])
            == EXPECTED_OBSTRUCTION_COUNTS
            and tuple(obstruction_record["external_group_indices"])
            == EXPECTED_OBSTRUCTION_EXTERNAL_GROUPS
            and tuple(obstruction_targets) == EXPECTED_OBSTRUCTION_TARGETS
            and not obstruction_record["has_outward_separated_comparison"]
        ),
        "registered_obstruction_counts_and_digest_reproduce": bool(
            obstruction_record["modulus_signature_count"]
            == EXPECTED_OBSTRUCTION_SIGNATURE_COUNT
            and obstruction_record["compatible_modulus_signature_count"]
            == EXPECTED_OBSTRUCTION_SIGNATURE_COUNT
            and obstruction_record["compatible_original_monomial_count"]
            == EXPECTED_OBSTRUCTION_COMPATIBLE_MONOMIAL_COUNT
            and obstruction_record["weighted_comparison_count"]
            == EXPECTED_OBSTRUCTION_WEIGHTED_COMPARISON_COUNT
            and obstruction_record["distinct_comparison_count"]
            == EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT
            and obstruction_record["weighted_relation_counts"]
            == {
                "overlap": EXPECTED_OBSTRUCTION_WEIGHTED_COMPARISON_COUNT,
                "product_below_target": 0,
                "target_below_product": 0,
            }
            and obstruction_record["distinct_relation_counts"]
            == {
                "overlap": EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT,
                "product_below_target": 0,
                "target_below_product": 0,
            }
            and obstruction_digest == EXPECTED_OBSTRUCTION_DIGEST
        ),
        "registered_resource_bounds_reproduce": bool(
            maximum_wave_coefficient == EXPECTED_MAXIMUM_WAVE_COEFFICIENT
            and maximum_crude_bound == EXPECTED_MAXIMUM_CRUDE_INT64_DOT_PRODUCT_BOUND
            and maximum_live_signature_count == EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT
            and maximum_crude_bound < np.iinfo(np.int64).max
        ),
        "all_outward_arrays_are_finite_nonnegative_and_ordered": bool(
            all_arrays_finite and all_bounds_ordered
        ),
    }
    audit = {
        "stopping_rule": (
            "scan lexicographic overlap aggregates and stop at the first aggregate "
            "with zero product-below-target and zero target-below-product comparisons"
        ),
        "scanned_prefix_count": len(prefix_records),
        "prefix_records": prefix_records,
        "prefix_digest_sha256": prefix_digest,
        "first_fully_unresolved_aggregate": obstruction_record,
        "first_obstruction_record_digest_sha256": obstruction_digest,
        "maximum_wave_coefficient": maximum_wave_coefficient,
        "maximum_crude_int64_dot_product_bound": maximum_crude_bound,
        "maximum_live_signature_count": maximum_live_signature_count,
        "streaming_contract": {
            "full_degree_sixteen_monomial_list_retained": False,
            "full_degree_sixteen_signature_list_retained": False,
            "scan_stops_after_first_fully_unresolved_aggregate": True,
            "peak_live_combined_signature_count": maximum_live_signature_count,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, obstruction_counts, obstruction_targets


def _exact_center_product_interval(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    class_counts: tuple[tuple[int, ...], ...],
) -> RationalInterval:
    lower = Fraction(1)
    upper = Fraction(1)
    for group_index, group_counts in enumerate(class_counts):
        for count, identifiers in zip(
            group_counts, classes[group_index], strict=True
        ):
            disc = lookup[identifiers[0]]
            lower *= disc.center_modulus.lower**count
            upper *= disc.center_modulus.upper**count
    return RationalInterval(lower, upper)


def _center_counterdiagnostic_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    counts: tuple[int, ...],
    target_group: tuple[str, ...],
) -> dict[str, Any]:
    group_pools = tuple(
        q011ag._group_signature(classes, lookup, group_index, count)
        for group_index, count in enumerate(counts)
    )
    left = q011ag._pair_signatures(group_pools[0], group_pools[1])
    right = q011ag._pair_signatures(group_pools[2], group_pools[3])
    left_wave = np.stack([record.wave for record in left])
    right_wave = np.stack([record.wave for record in right])
    center_lower = np.nextafter(
        np.multiply.outer(
            np.array([record.bounds[0] for record in left]),
            np.array([record.bounds[0] for record in right]),
        ),
        -inf,
    )
    center_upper = np.nextafter(
        np.multiply.outer(
            np.array([record.bounds[2] for record in left]),
            np.array([record.bounds[2] for record in right]),
        ),
        inf,
    )
    center_records = []
    raw_minima = []
    for target_identifier in target_group:
        output_block = q011z._identifier_indices(target_identifier)[0]
        wave_matrix, _ = q011ag._wave_matrix(left_wave, right_wave, output_block)
        active = wave_matrix > 0
        target = lookup[target_identifier].center_modulus
        product_below_gap = q011ag._down_subtract(
            q011ag._fraction_lower(target.lower), center_upper
        )
        target_below_gap = q011ag._down_subtract(
            center_lower, q011ag._fraction_upper(target.upper)
        )
        product_below = active & (product_below_gap > 0)
        target_below = active & (target_below_gap > 0)
        unresolved = active & ~(product_below | target_below)
        gaps = np.where(
            product_below,
            product_below_gap,
            np.where(target_below, target_below_gap, inf),
        )
        flat_index = int(gaps.argmin())
        left_index, right_index = map(int, np.unravel_index(flat_index, gaps.shape))
        relation = (
            "product_below_target"
            if product_below[left_index, right_index]
            else "target_below_product"
        )
        class_counts = q011ag._signature_counts(left, right, left_index, right_index)
        center_records.append(
            {
                "target_identifier": target_identifier,
                "active_distinct": int(active.sum()),
                "active_weighted": int(wave_matrix.sum()),
                "product_below_distinct": int(product_below.sum()),
                "target_below_distinct": int(target_below.sum()),
                "overlap_distinct": int(unresolved.sum()),
                "minimum_outward_gap_hex": float(gaps[left_index, right_index]).hex(),
                "minimum_outward_witness_class_counts": [
                    list(group) for group in class_counts
                ],
                "minimum_outward_witness_wave": int(
                    wave_matrix[left_index, right_index]
                ),
                "minimum_outward_witness_relation": relation,
            }
        )
        raw_minima.append(
            (
                float(gaps[left_index, right_index]),
                target_identifier,
                output_block,
                left_index,
                right_index,
                int(wave_matrix[left_index, right_index]),
                relation,
                class_counts,
            )
        )
    center_record_digest = q011b._canonical_json_sha256(center_records)
    raw_minima.sort(key=lambda record: (record[0], record[1], record[3], record[4]))
    _, initial_target_identifier, _, _, _, _, initial_relation, initial_counts = raw_minima[0]
    initial_product = _exact_center_product_interval(classes, lookup, initial_counts)
    initial_target = lookup[initial_target_identifier].center_modulus
    initial_exact_gap = (
        initial_target.lower - initial_product.upper
        if initial_relation == "product_below_target"
        else initial_product.lower - initial_target.upper
    )
    cutoff = q011ag._fraction_upper(initial_exact_gap)
    candidates = []
    product_cache: dict[tuple[tuple[int, ...], ...], RationalInterval] = {}
    for target_identifier in target_group:
        output_block = q011z._identifier_indices(target_identifier)[0]
        wave_matrix, _ = q011ag._wave_matrix(left_wave, right_wave, output_block)
        active = wave_matrix > 0
        target = lookup[target_identifier].center_modulus
        product_below_gap = q011ag._down_subtract(
            q011ag._fraction_lower(target.lower), center_upper
        )
        target_below_gap = q011ag._down_subtract(
            center_lower, q011ag._fraction_upper(target.upper)
        )
        for relation, gaps, mask in (
            (
                "product_below_target",
                product_below_gap,
                active & (product_below_gap > 0),
            ),
            (
                "target_below_product",
                target_below_gap,
                active & (target_below_gap > 0),
            ),
        ):
            for left_raw, right_raw in zip(
                *np.nonzero(mask & (gaps <= cutoff)), strict=True
            ):
                left_index = int(left_raw)
                right_index = int(right_raw)
                class_counts = q011ag._signature_counts(
                    left, right, left_index, right_index
                )
                if class_counts not in product_cache:
                    product_cache[class_counts] = _exact_center_product_interval(
                        classes, lookup, class_counts
                    )
                product = product_cache[class_counts]
                exact_gap = (
                    target.lower - product.upper
                    if relation == "product_below_target"
                    else product.lower - target.upper
                )
                candidates.append(
                    {
                        "target_identifier": target_identifier,
                        "output_block": output_block,
                        "left_index": left_index,
                        "right_index": right_index,
                        "wave_multiplicity": int(wave_matrix[left_index, right_index]),
                        "relation": relation,
                        "class_counts": [list(group) for group in class_counts],
                        "outward_gap_hex": float(gaps[left_index, right_index]).hex(),
                        "exact_gap": q011z._exact_fraction_record(exact_gap),
                    }
                )
    exact_candidate_digest = q011b._canonical_json_sha256(candidates)
    exact_minimum = min(q011z._fraction(record["exact_gap"]) for record in candidates)
    ties = [
        record
        for record in candidates
        if q011z._fraction(record["exact_gap"]) == exact_minimum
    ]
    canonical = ties[0]
    canonical_counts = tuple(tuple(group) for group in canonical["class_counts"])
    source_identifiers = q011ai.q011af._source_witness_for_signature(
        classes, canonical_counts, canonical["output_block"]
    )
    uniform_product = q011ag._exact_product_interval(classes, lookup, canonical_counts)
    uniform_target = lookup[canonical["target_identifier"]].modulus
    intersection_lower = max(uniform_product.lower, uniform_target.lower)
    intersection_upper = min(uniform_product.upper, uniform_target.upper)
    intersection_width = intersection_upper - intersection_lower
    intersection_excess = intersection_width - EXPECTED_UNIFORM_INTERSECTION_BASE_WIDTH
    witness = {
        "canonical_center_minimum": canonical,
        "exact_center_minimum": q011z._exact_fraction_record(exact_minimum),
        "exact_center_minimum_hex": float(exact_minimum).hex(),
        "exact_center_minimum_tie_count": len(ties),
        "candidate_count": len(candidates),
        "source_identifiers": list(source_identifiers),
        "uniform_product_interval": {
            "lower": q011z._exact_fraction_record(uniform_product.lower),
            "upper": q011z._exact_fraction_record(uniform_product.upper),
        },
        "uniform_target_interval": {
            "lower": q011z._exact_fraction_record(uniform_target.lower),
            "upper": q011z._exact_fraction_record(uniform_target.upper),
        },
        "uniform_intersection_interval": {
            "lower": q011z._exact_fraction_record(intersection_lower),
            "upper": q011z._exact_fraction_record(intersection_upper),
            "width": q011z._exact_fraction_record(intersection_width),
            "width_hex": float(intersection_width).hex(),
        },
    }
    witness_digest = q011b._canonical_json_sha256(witness)
    checks = {
        "all_four_target_center_records_are_strictly_separated": bool(
            len(center_records) == 4
            and all(record["active_distinct"] == 35_280 for record in center_records)
            and all(record["product_below_distinct"] == 35_280 for record in center_records)
            and all(record["target_below_distinct"] == 0 for record in center_records)
            and all(record["overlap_distinct"] == 0 for record in center_records)
        ),
        "registered_center_minima_and_digest_reproduce": bool(
            center_records[0]["minimum_outward_gap_hex"]
            == EXPECTED_CENTER_THREE_MINIMUM_HEX
            and center_records[1]["minimum_outward_gap_hex"]
            == EXPECTED_CENTER_FOUR_MINIMUM_HEX
            and center_records[2]["minimum_outward_gap_hex"]
            == EXPECTED_CENTER_THREE_MINIMUM_HEX
            and center_records[3]["minimum_outward_gap_hex"]
            == EXPECTED_CENTER_FOUR_MINIMUM_HEX
            and center_record_digest == EXPECTED_CENTER_RECORD_DIGEST
        ),
        "registered_exact_candidates_and_minimum_reproduce": bool(
            len(candidates) == EXPECTED_EXACT_CENTER_CANDIDATE_COUNT
            and exact_candidate_digest == EXPECTED_EXACT_CENTER_CANDIDATE_DIGEST
            and float(exact_minimum).hex() == EXPECTED_EXACT_CENTER_MINIMUM_HEX
            and len(ties) == EXPECTED_EXACT_CENTER_MINIMUM_TIE_COUNT
            and exact_minimum > 0
        ),
        "canonical_center_witness_reproduces": bool(
            canonical["target_identifier"] == "block=11;center=4"
            and canonical["output_block"] == 11
            and canonical["left_index"] == 385
            and canonical["right_index"] == 2
            and canonical["wave_multiplicity"] == 6
            and canonical["relation"] == "product_below_target"
            and canonical_counts == EXPECTED_CANONICAL_CLASS_COUNTS
            and tuple(source_identifiers) == EXPECTED_CANONICAL_SOURCE_IDENTIFIERS
        ),
        "canonical_uniform_intersection_is_strictly_positive_and_registered": bool(
            intersection_lower <= intersection_upper
            and intersection_width > EXPECTED_UNIFORM_INTERSECTION_BASE_WIDTH
            and float(intersection_width).hex()
            == EXPECTED_UNIFORM_INTERSECTION_WIDTH_HEX
            and float(intersection_excess).hex()
            == EXPECTED_UNIFORM_INTERSECTION_EXCESS_HEX
            and q011b._canonical_json_sha256(
                q011z._exact_fraction_record(intersection_excess)
            )
            == EXPECTED_UNIFORM_INTERSECTION_EXCESS_DIGEST
            and witness_digest == EXPECTED_WITNESS_DIGEST
        ),
    }
    return {
        "diagnostic_scope": (
            "center-modulus rational intervals only; disc radii are deliberately "
            "removed and this is not an actual-spectrum nonresonance certificate"
        ),
        "center_target_records": center_records,
        "center_target_record_digest_sha256": center_record_digest,
        "exact_candidate_records": candidates,
        "exact_candidate_record_digest_sha256": exact_candidate_digest,
        "exact_center_minimum": q011z._exact_fraction_record(exact_minimum),
        "exact_center_minimum_hex": float(exact_minimum).hex(),
        "exact_center_minimum_tie_count": len(ties),
        "uniform_intersection_witness": witness,
        "uniform_intersection_witness_digest_sha256": witness_digest,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "grid": [SIZE, SIZE],
        "fixed_conservation_leaf": True,
        "degree": DEGREE,
        "degree_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "degree_expanded_product_control_count": EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT,
        "overlap_inventory_digest_sha256": EXPECTED_INVENTORY_DIGEST,
        "uniform_record_digest_sha256": EXPECTED_UNIFORM_RECORD_DIGEST,
        "uniform_radius": _fraction_record(UNIFORM_REFINED_RADIUS),
        "first_obstruction_prefix_digest_sha256": EXPECTED_PREFIX_DIGEST,
        "first_obstruction_record_digest_sha256": EXPECTED_OBSTRUCTION_DIGEST,
        "center_record_digest_sha256": EXPECTED_CENTER_RECORD_DIGEST,
        "exact_center_candidate_digest_sha256": EXPECTED_EXACT_CENTER_CANDIDATE_DIGEST,
        "uniform_intersection_witness_digest_sha256": EXPECTED_WITNESS_DIGEST,
        "uniform_certificate_rejected_classification": (
            UNIFORM_CERTIFICATE_REJECTED_CLASSIFICATION
        ),
        "actual_resonance_not_established_classification": (
            ACTUAL_RESONANCE_NOT_ESTABLISHED_CLASSIFICATION
        ),
        "combined_classification": COMBINED_CLASSIFICATION,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "failed_hypothesis_order": cycle["failed_hypothesis_order"],
    }


def run_degree16_uniform_obstruction_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = _inventory_audit(
        artifacts
    )
    envelope, lookup = _uniform_envelope_audit(
        artifacts, selected_groups, external_target_groups
    )
    classes, class_records = q011ag._modulus_classes(selected_groups, lookup)
    class_digest = q011b._canonical_json_sha256(class_records)
    outward_base_records = q011ag._outward_base_records(classes, lookup)
    outward_base_digest = q011b._canonical_json_sha256(outward_base_records)
    overlap_counts = tuple(
        tuple(record["selected_type_counts"]) for record in overlap_records
    )
    external_index_groups = tuple(
        tuple(record["external_group_indices"]) for record in overlap_records
    )
    obstruction, obstruction_counts, obstruction_targets = _first_uniform_obstruction_audit(
        classes,
        lookup,
        overlap_counts,
        external_index_groups,
        external_target_groups,
    )
    center = _center_counterdiagnostic_audit(
        classes, lookup, obstruction_counts, obstruction_targets
    )
    compression_checks = {
        "selected_groups_partition_into_registered_modulus_classes": bool(
            tuple(len(group) for group in classes) == EXPECTED_MODULUS_CLASS_COUNTS
            and class_digest == q011ai.EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "uniform_outward_base_records_reproduce": (
            outward_base_digest == q011ai.EXPECTED_OUTWARD_BASE_DIGEST
        ),
        "factorization_and_integer_arithmetic_checks_pass": bool(
            obstruction["checks"]["registered_resource_bounds_reproduce"]
            and obstruction["checks"][
                "all_outward_arrays_are_finite_nonnegative_and_ordered"
            ]
        ),
    }
    compression = {
        "selected_modulus_class_counts": [len(group) for group in classes],
        "selected_modulus_class_records": class_records,
        "class_membership_digest_sha256": class_digest,
        "outward_base_records": outward_base_records,
        "outward_base_digest_sha256": outward_base_digest,
        "checks": compression_checks,
        "passed": all(compression_checks.values()),
    }

    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    inventory_sections = {
        "degree16_modulus_inventory_audit": inventory,
        "uniform_refined_envelope_audit": envelope,
    }
    obstruction_sections = {
        "fourier_modulus_compression_audit": compression,
        "first_uniform_envelope_obstruction_audit": obstruction,
    }
    center_sections = {"center_only_counterdiagnostic_audit": center}
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(inventory_sections)
    obstruction_digest = q011b._canonical_json_sha256(obstruction_sections)
    center_digest = q011b._canonical_json_sha256(center_sections)
    strict_payload = {
        **input_sections,
        **inventory_sections,
        **obstruction_sections,
        **center_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and inventory_digest == q011b._canonical_json_sha256(inventory_sections)
        and obstruction_digest == q011b._canonical_json_sha256(obstruction_sections)
        and center_digest == q011b._canonical_json_sha256(center_sections)
    )
    validity_gates = {
        "fourteen_artifacts_seventy_three_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad/ae/af/ag/ah/ai artifacts, runners, "
                "73 digests, outcomes, boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "degree_sixteen_inventory_and_154_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": "969 aggregates, 20349 controls, 815 old separations and 154 overlaps",
            "value": inventory["checks"],
        },
        "multi_target_union_reproduces": {
            "passed": inventory["checks"][
                "exactly_one_registered_multi_target_overlap_reproduces"
            ],
            "threshold": "aggregate 73 uses the union of external groups 156 and 157",
            "value": inventory["multi_target_aggregate_indices"],
        },
        "uniform_radius_containment_and_204_monotone_records_reproduce": {
            "passed": envelope["passed"],
            "threshold": (
                "160 direct intervals, 204 monotone records and exact preservation "
                "of all 144 Q011ai records"
            ),
            "value": envelope["checks"],
        },
        "modulus_classes_factorization_and_integer_exactness_reproduce": {
            "passed": compression["passed"],
            "threshold": (
                "4/2/3/6 exact modulus classes, outward bases, finite ordered "
                "products and nonoverflowing int64 coefficients reproduce"
            ),
            "value": compression["checks"],
        },
        "registered_first_obstruction_prefix_reproduces": {
            "passed": bool(
                obstruction["checks"]["registered_first_hundred_record_prefix_reproduces"]
                and obstruction["checks"]["registered_resource_bounds_reproduce"]
            ),
            "threshold": "the registered 100-record prefix and resource maxima reproduce",
            "value": obstruction["checks"],
        },
        "registered_index_ninety_nine_obstruction_reproduces": {
            "passed": bool(
                obstruction["checks"][
                    "index_ninety_nine_is_the_first_fully_unresolved_aggregate"
                ]
                and obstruction["checks"][
                    "registered_obstruction_counts_and_digest_reproduce"
                ]
            ),
            "threshold": "all registered relation counts and the obstruction digest reproduce",
            "value": obstruction["first_fully_unresolved_aggregate"],
        },
        "center_only_exact_counterdiagnostic_reproduces": {
            "passed": center["passed"],
            "threshold": (
                "141120 center comparisons, 28 exact candidates, a two-way "
                "positive minimum tie and the registered witness reproduce"
            ),
            "value": center["checks"],
        },
        "uniform_intersection_serialization_digests_and_provenance_reproduce": {
            "passed": bool(
                center["checks"][
                    "canonical_uniform_intersection_is_strictly_positive_and_registered"
                ]
                and strict_json
                and digests_reproduce
            ),
            "threshold": (
                "the exact uniform intersection is positive and strict JSON, "
                "section digests and runner provenance reproduce"
            ),
            "value": {
                "witness_digest": center["uniform_intersection_witness_digest_sha256"],
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "uniform_envelope_is_spectrally_valid_and_old_disc_contained": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": "all Q011y discs subset rho-discs subset Q011k discs",
            "value": envelope["checks"],
        },
        "multi_target_inventory_and_fourier_multiplicity_are_exact": {
            "passed": bool(validity_passed and inventory["passed"] and compression["passed"]),
            "threshold": "all target unions and exact Fourier fibers are complete",
            "value": {"inventory": inventory["checks"], "compression": compression["checks"]},
        },
        "index_ninety_nine_is_the_first_fully_unresolved_aggregate": {
            "passed": bool(
                validity_passed
                and obstruction["checks"][
                    "indices_zero_through_ninety_eight_have_a_separated_comparison"
                ]
                and obstruction["checks"][
                    "index_ninety_nine_is_the_first_fully_unresolved_aggregate"
                ]
            ),
            "threshold": "indices 0--98 have separation and index 99 has none",
            "value": obstruction["checks"],
        },
        "all_index_ninety_nine_uniform_comparisons_overlap": {
            "passed": bool(
                validity_passed
                and obstruction["first_fully_unresolved_aggregate"][
                    "distinct_relation_counts"
                ]["overlap"]
                == EXPECTED_OBSTRUCTION_DISTINCT_COMPARISON_COUNT
            ),
            "threshold": "all 141120 distinct uniform comparisons overlap",
            "value": obstruction["first_fully_unresolved_aggregate"][
                "distinct_relation_counts"
            ],
        },
        "canonical_exact_uniform_intersection_is_positive": {
            "passed": bool(
                validity_passed
                and center["checks"][
                    "canonical_uniform_intersection_is_strictly_positive_and_registered"
                ]
            ),
            "threshold": "the exact registered uniform intersection has positive width",
            "value": center["uniform_intersection_witness"][
                "uniform_intersection_interval"
            ],
        },
        "all_center_only_comparisons_are_strict_with_positive_exact_minimum": {
            "passed": bool(
                validity_passed
                and center["checks"][
                    "all_four_target_center_records_are_strictly_separated"
                ]
                and center["checks"][
                    "registered_exact_candidates_and_minimum_reproduce"
                ]
            ),
            "threshold": "all 141120 center comparisons separate with a positive exact minimum",
            "value": center["checks"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed or not hypotheses_passed:
        hypothesis_outcome = "inconclusive"
        actual_resonance_outcome = "inconclusive"
        classification = "registered Q011aj degree-sixteen obstruction audit is invalid"
    else:
        hypothesis_outcome = "rejected"
        actual_resonance_outcome = "not_established"
        classification = COMBINED_CLASSIFICATION
    cycle: dict[str, Any] = {
        "question": (
            "Where does the degree-sixteen uniform-rho outward certificate first "
            "become fully unresolved, and do center-only intervals establish a resonance?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "inventory_digest_sha256": inventory_digest,
        "obstruction_digest_sha256": obstruction_digest,
        "center_digest_sha256": center_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": hypothesis_outcome,
        "actual_resonance_outcome": actual_resonance_outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    registered_rejection = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "uniform_transformed_residual_envelope_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "degree_sixteen_uniform_rho_external_nonresonance_certificate_is_rejected": (
            registered_rejection
        ),
        "first_fully_unresolved_aggregate_is_certified": registered_rejection,
        "center_only_obstruction_comparisons_are_separated": registered_rejection,
        "center_only_separation_is_an_actual_spectrum_certificate": False,
        "an_actual_degree_sixteen_complex_resonance_is_established": False,
        "degree_sixteen_external_nonresonance_is_certified": False,
        "certified_external_nonresonance_degrees": list(range(2, 16)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(16, 91)),
        "degrees_16_through_90_are_certified": False,
        "legacy_5e_6_margin_rejection_is_preserved": True,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011ai_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree sixteen for the fixed 17x17 repaired exact "
        "map on one fixed conservation leaf, the 154 Q011u modulus-overlap aggregates, "
        "the Q011y transformed-residual enclosure, uniform rho=5e-8 discs, exact "
        "x-Fourier multiplicities and outward-rounded dyadic products. The center-only "
        "counterdiagnostic deliberately removes certified eigendisc radii and is not an "
        "actual-spectrum nonresonance certificate. It establishes no actual complex "
        "resonance, degree-sixteen nonresonance, degree from 17 through 90, all-order "
        "nonresonance, C2 or higher graph smoothness, SSM existence or uniqueness, "
        "normal attraction, basin, other grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ai_certificates_and_diagnostics_changed": False,
    }
    if registered_rejection:
        cycle["next_change"] = (
            "Preregister Q011ak to replace uniform rho by the Q011y blockwise "
            "transformed-residual radii and first re-audit the registered obstruction."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, multi-target, envelope, "
            "factorization, stopping-prefix, exact-witness or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011aj cycle failed strict serialization or digest")
    return cycle


def run_q011aj_study() -> dict[str, Any]:
    cycle = run_degree16_uniform_obstruction_audit()
    obstruction = cycle["first_uniform_envelope_obstruction_audit"][
        "first_fully_unresolved_aggregate"
    ]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_input_scalar_type": "fractions.Fraction",
            "proof_enclosure_type": "outward-rounded IEEE-754 binary64",
            "fourier_coefficient_type": "numpy.int64 with registered overflow bound",
            "floating_point_used_for_gate_decisions": True,
            "floating_point_gate_is_rigorous_interval_logic": True,
            "scanned_overlap_aggregate_count": EXPECTED_PREFIX_COUNT,
            "first_obstruction_weighted_comparison_count": obstruction[
                "weighted_comparison_count"
            ],
            "first_obstruction_distinct_comparison_count": obstruction[
                "distinct_comparison_count"
            ],
            "exact_record_storage": (
                "ordered prefix records, canonical digests and 28 exact "
                "center-gap refinements with one exact uniform-intersection witness"
            ),
        },
        "mathematical_scope": {
            "diagnostic": (
                "degree-sixteen first uniform-envelope obstruction and center-only "
                "counterdiagnostic"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "uniform_rho_certificate_claim": False,
            "degree_sixteen_external_nonresonance_claim": False,
            "actual_complex_resonance_claim": False,
            "degrees_17_through_90_claim": False,
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
    result = run_q011aj_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
