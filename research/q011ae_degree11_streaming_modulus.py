"""Q011ae degree-eleven uniform refined-envelope indexed-modulus certificate."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011ad_degree10_refined_modulus as q011ad
import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011u_c91_modulus_nonresonance as q011u
import research.q011z_degree6_refined_modulus as q011z
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574
DEGREE = 11
EXPECTED_DEGREE_AGGREGATE_COUNT = 364
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 4368
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 350
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 14
OVERLAP_COUNTS = (
    (0, 5, 0, 6),
    (0, 5, 1, 5),
    (0, 7, 2, 2),
    (3, 7, 0, 1),
    (3, 7, 1, 0),
    (4, 6, 0, 1),
    (4, 6, 1, 0),
    (5, 5, 0, 1),
    (5, 5, 1, 0),
    (6, 4, 0, 1),
    (6, 4, 1, 0),
    (9, 2, 0, 0),
    (10, 1, 0, 0),
    (11, 0, 0, 0),
)
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXTERNAL_GROUP_INDICES = (167, 167, 165, 162, 162, 162, 162, 162, 162, 162, 162, 161, 161, 161)
EXPECTED_EXTERNAL_TARGET_COUNTS = (8, 8, 4, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8)
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 28
EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT = 52
EXPECTED_RELEVANT_IDENTIFIER_COUNT = 84
EXPECTED_MONOMIAL_COUNTS = (
    96096,
    177408,
    43200,
    115200,
    57600,
    221760,
    110880,
    354816,
    177408,
    480480,
    240240,
    114400,
    77792,
    31824,
)
EXPECTED_INDEXED_MONOMIAL_COUNT = 2_299_104
EXPECTED_COMPATIBLE_MONOMIAL_COUNTS = (
    21824,
    41168,
    6408,
    22560,
    11280,
    40900,
    20450,
    62560,
    31280,
    83088,
    41544,
    0,
    0,
    0,
)
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 383_062
EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT = 1_916_042
EXPECTED_SECTOR_HISTOGRAMS = (
    {0: 9408, 1: 9394, 2: 8560, 3: 7714, 4: 6208, 5: 4808, 6: 3210, 7: 2048, 8: 1402, 9: 1402, 10: 2048, 11: 3210, 12: 4808, 13: 6208, 14: 7714, 15: 8560, 16: 9394},
    {0: 17776, 1: 17380, 2: 16192, 3: 14260, 4: 11696, 5: 8752, 6: 5828, 7: 3480, 8: 2228, 9: 2228, 10: 3480, 11: 5828, 12: 8752, 13: 11696, 14: 14260, 15: 16192, 16: 17380},
    {0: 3464, 1: 3572, 2: 3288, 3: 3204, 4: 2760, 5: 2468, 6: 1904, 7: 1506, 8: 1166, 9: 1166, 10: 1506, 11: 1904, 12: 2468, 13: 2760, 14: 3204, 15: 3288, 16: 3572},
    {0: 9280, 1: 9040, 2: 8800, 3: 8080, 4: 7360, 5: 6160, 6: 5280, 7: 4320, 8: 3920, 9: 3920, 10: 4320, 11: 5280, 12: 6160, 13: 7360, 14: 8080, 15: 8800, 16: 9040},
    {0: 4640, 1: 4520, 2: 4400, 3: 4040, 4: 3680, 5: 3080, 6: 2640, 7: 2160, 8: 1960, 9: 1960, 10: 2160, 11: 2640, 12: 3080, 13: 3680, 14: 4040, 15: 4400, 16: 4520},
    {0: 19360, 1: 18700, 2: 18040, 3: 16060, 4: 14080, 5: 11410, 6: 9230, 7: 7310, 8: 6370, 9: 6370, 10: 7310, 11: 9230, 12: 11410, 13: 14080, 14: 16060, 15: 18040, 16: 18700},
    {0: 9680, 1: 9350, 2: 9020, 3: 8030, 4: 7040, 5: 5705, 6: 4615, 7: 3655, 8: 3185, 9: 3185, 10: 3655, 11: 4615, 12: 5705, 13: 7040, 14: 8030, 15: 9020, 16: 9350},
    {0: 33088, 1: 31504, 2: 29920, 3: 26064, 4: 22208, 5: 17648, 6: 13760, 7: 10688, 8: 9072, 9: 9072, 10: 10688, 11: 13760, 12: 17648, 13: 22208, 14: 26064, 15: 29920, 16: 31504},
    {0: 16544, 1: 15752, 2: 14960, 3: 13032, 4: 11104, 5: 8824, 6: 6880, 7: 5344, 8: 4536, 9: 4536, 10: 5344, 11: 6880, 12: 8824, 13: 11104, 14: 13032, 15: 14960, 16: 15752},
    {0: 45760, 1: 43504, 2: 41248, 3: 35600, 4: 29952, 5: 23572, 6: 18032, 7: 13860, 8: 11592, 9: 11592, 10: 13860, 11: 18032, 12: 23572, 13: 29952, 14: 35600, 15: 41248, 16: 43504},
    {0: 22880, 1: 21752, 2: 20624, 3: 17800, 4: 14976, 5: 11786, 6: 9016, 7: 6930, 8: 5796, 9: 5796, 10: 6930, 11: 9016, 12: 11786, 13: 14976, 14: 17800, 15: 20624, 16: 21752},
    {1: 18760, 3: 16200, 5: 11820, 6: 660, 7: 6900, 8: 2860, 9: 2860, 10: 6900, 11: 660, 12: 11820, 14: 16200, 16: 18760},
    {1: 12152, 3: 10680, 5: 8100, 6: 572, 7: 5060, 8: 2332, 9: 2332, 10: 5060, 11: 572, 12: 8100, 14: 10680, 16: 12152},
    {1: 4704, 3: 4200, 5: 3300, 6: 364, 7: 2200, 8: 1144, 9: 1144, 10: 2200, 11: 364, 12: 3300, 14: 4200, 16: 4704},
)
EXPECTED_TARGET_SECTOR_HISTOGRAMS = (
    {0: 4, 4: 2, 13: 2},
    {0: 4, 4: 2, 13: 2},
    {3: 2, 14: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {4: 2, 8: 2, 9: 2, 13: 2},
    {2: 2, 4: 2, 13: 2, 15: 2},
    {2: 2, 4: 2, 13: 2, 15: 2},
    {2: 2, 4: 2, 13: 2, 15: 2},
)
EXPECTED_COMPARISON_COUNTS = (
    62464,
    117888,
    12816,
    45120,
    22560,
    81800,
    40900,
    125120,
    62560,
    166176,
    83088,
    0,
    0,
    0,
)
EXPECTED_COMPATIBLE_COMPARISON_COUNT = 820_492
UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
MINIMUM_MODULUS_GAP = Fraction(5, 10**6)

Q011AD_ARTIFACT_SHA256 = "dfdee641924a9e3cb6cbea57c23e54a9438f86aa3fc6c540f0d613ff1add340c"
Q011AD_RUNNER_SHA256 = "666b33f38e773efda70d498c7e4068d108630be31f4be52a64f0640122f95d3b"
Q011AD_DIGESTS = (
    "7dd67186b06547d59e08f531192d3c1a58183a5f92121f9567f9aca5ce28303f",
    "bd9537e8b182fde2ccbd3ff3ae347d85eba673ed93c3e21451069ff1f8b9cac1",
    "440afad1b33c896451a458b62855a71269c1cbef728ea3ecb5b9a75a3fa71d6f",
    "29fea1d86fdd06b124df677e3b4cf02a4828355e63e91a7cc14ece63c03c524d",
    "e3618fed4c565e76e59653b7affc86c045a617fc463666c7dc468aba302a05f9",
)
Q011AD_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "sector_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)

ACCEPTED_CLASSIFICATION = (
    "degree-11 external nonresonance is certified by the contained uniform "
    "transformed-residual envelope, exact Fourier sectors and streamed "
    "indexed-modulus products"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-11 streamed indexed-modulus product remains "
    "inseparable from an external target"
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
    prior_audit, artifacts = q011ad._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ad_degree10_refined_modulus.json"
    runner_path = Path(q011ad.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digest_tuple = q011z._digest_tuple(cycle, Q011AD_DIGEST_NAMES)
    checks = {
        "q011ad_eight_prior_artifacts_and_helpers_reproduce": bool(
            prior_audit["passed"]
            and prior_audit["direct_digest_count"] == 43
            and all(prior_audit["checks"].values())
        ),
        "q011ad_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011AD_ARTIFACT_SHA256),
        "q011ad_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AD_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AD_RUNNER_SHA256
        ),
        "q011ad_digests_match": digest_tuple == Q011AD_DIGESTS,
        "q011ad_registered_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["scientific_classification"] == q011ad.ACCEPTED_CLASSIFICATION
        ),
        "q011ad_degree_ten_scope_is_preserved": bool(
            cycle["theorem_consequence"]["degree_ten_external_nonresonance_is_certified"]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == list(range(2, 11))
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(11, 91))
            and not cycle["theorem_consequence"]["ssm_existence_or_uniqueness_is_certified"]
        ),
        "q011ad_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ad_package_source_metadata_matches": (artifact["source"] == source_metadata()),
        "q011ad_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "forty_eight_direct_digests_are_sealed": bool(
            prior_audit["direct_digest_count"] + len(digest_tuple) == 48
        ),
    }
    artifacts["q011ad"] = artifact
    audit = {
        "prior_q011ad_sealed_input_audit": prior_audit,
        "q011ad": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AD_DIGEST_NAMES),
            "digests": list(digest_tuple),
            "scientific_classification": cycle["scientific_classification"],
        },
        "direct_digest_count": prior_audit["direct_digest_count"] + len(digest_tuple),
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
    reconstructed_spectrum, selected_merged, external_merged = q011u._spectral_compression_audit(
        {"q011k": artifacts["q011k"]}
    )
    selected_groups = tuple(tuple(sorted(component.identifiers)) for component in selected_merged)
    external_target_groups = tuple(
        tuple(sorted(external_merged[index].identifiers)) for index in EXTERNAL_GROUP_INDICES
    )
    enumeration = u_cycle["degree_3_through_90_enumeration_audit"]
    degree_records = [
        record for record in enumeration["degree_records"] if record["degree"] == DEGREE
    ]
    degree_record = degree_records[0]
    log_audit = u_cycle["rational_log_enclosure_audit"]
    selected_logs = tuple(
        q011z._scaled_log_pair(record) for record in log_audit["selected_log_records"]
    )
    external_logs = tuple(
        q011z._scaled_log_pair(record) for record in log_audit["external_log_records"]
    )
    overlap_records = []
    for counts in q011z._count_tuples(DEGREE):
        aggregate_lower = sum(
            count * interval[0] for count, interval in zip(counts, selected_logs, strict=True)
        )
        aggregate_upper = sum(
            count * interval[1] for count, interval in zip(counts, selected_logs, strict=True)
        )
        external_indices = [
            index
            for index, (lower, upper) in enumerate(external_logs)
            if lower <= aggregate_upper and upper >= aggregate_lower
        ]
        if external_indices:
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

    stored_selected = stored_spectrum["selected_merged_records"]
    stored_external = stored_spectrum["external_merged_records"]
    selected_membership_checks = [
        q011b._canonical_json_sha256(list(group))
        == stored_selected[index]["membership_digest_sha256"]
        for index, group in enumerate(selected_groups)
    ]
    external_membership_checks = [
        q011b._canonical_json_sha256(list(group))
        == stored_external[external_index]["membership_digest_sha256"]
        for group, external_index in zip(
            external_target_groups, EXTERNAL_GROUP_INDICES, strict=True
        )
    ]
    exact_inventory = {
        "selected_source_groups": [
            {"group_index": index, "identifiers": list(group)}
            for index, group in enumerate(selected_groups)
        ],
        "overlap_records": overlap_records,
        "external_target_groups": [
            {
                "aggregate_index": aggregate_index,
                "external_group_index": external_index,
                "identifiers": list(group),
            }
            for aggregate_index, (external_index, group) in enumerate(
                zip(EXTERNAL_GROUP_INDICES, external_target_groups, strict=True)
            )
        ],
    }
    first_overlap = degree_record["first_overlap"]
    checks = {
        "q011u_old_modulus_spectrum_reconstructs_exactly": bool(
            reconstructed_spectrum["passed"] and reconstructed_spectrum == stored_spectrum
        ),
        "q011u_degree_eleven_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_fourteen_overlap_tuples_and_external_groups_reproduce": bool(
            tuple(tuple(record["selected_type_counts"]) for record in overlap_records)
            == OVERLAP_COUNTS
            and tuple(record["external_group_indices"][0] for record in overlap_records)
            == EXTERNAL_GROUP_INDICES
            and all(len(record["external_group_indices"]) == 1 for record in overlap_records)
            and tuple(first_overlap["selected_type_counts"]) == OVERLAP_COUNTS[0]
            and first_overlap["external_group_index"] == EXTERNAL_GROUP_INDICES[0]
        ),
        "selected_source_memberships_and_sizes_reproduce": bool(
            tuple(len(group) for group in selected_groups) == EXPECTED_SELECTED_GROUP_SIZES
            and all(selected_membership_checks)
        ),
        "external_target_memberships_and_sizes_reproduce": bool(
            tuple(len(group) for group in external_target_groups) == EXPECTED_EXTERNAL_TARGET_COUNTS
            and len(set().union(*map(set, external_target_groups)))
            == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
            and all(external_membership_checks)
        ),
        "old_degree_ten_certificate_is_preserved": artifacts["q011ad"]["cycle"][
            "theorem_consequence"
        ]["degree_ten_external_nonresonance_is_certified"],
        "inventory_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(exact_inventory)
            and _strict_json_serializable(exact_inventory)
            and json.dumps(exact_inventory, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "degree_modulus_aggregate_count": degree_record["aggregate_count"],
        "degree_expanded_product_control_count": degree_record["expanded_product_control_count"],
        "old_modulus_separated_aggregate_count": degree_record["nonoverlap_count"],
        "old_modulus_overlap_aggregate_count": degree_record["overlap_count"],
        "overlap_records": overlap_records,
        "selected_source_group_sizes": [len(group) for group in selected_groups],
        "selected_source_group_memberships": [list(group) for group in selected_groups],
        "external_target_groups": [
            {
                "aggregate_index": index,
                "external_group_index": EXTERNAL_GROUP_INDICES[index],
                "identifiers": list(group),
            }
            for index, group in enumerate(external_target_groups)
        ],
        "unique_external_target_count": len(set().union(*map(set, external_target_groups))),
        "old_spectrum_digest_sha256": q011b._canonical_json_sha256(reconstructed_spectrum),
        "exact_inventory_digest_sha256": q011b._canonical_json_sha256(exact_inventory),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, selected_groups, external_target_groups, tuple(overlap_records)


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
    active_group_indices = sorted(
        {
            group_index
            for counts in OVERLAP_COUNTS
            for group_index, multiplicity in enumerate(counts)
            if multiplicity > 0
        }
    )
    selected_identifiers = set().union(
        *(set(selected_groups[index]) for index in active_group_indices)
    )
    external_identifiers = set().union(*map(set, external_target_groups))
    directly_relevant_identifiers = selected_identifiers | external_identifiers
    prior_records = {
        record["identifier"]: record
        for record in artifacts["q011ad"]["cycle"]["uniform_refined_envelope_audit"][
            "uniform_disc_records"
        ]
    }
    relevant_identifiers = sorted(directly_relevant_identifiers | set(prior_records))
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
            max(
                Fraction(0),
                center_modulus.lower - UNIFORM_REFINED_RADIUS,
            ),
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
        "all_52_direct_and_84_monotone_identifiers_have_uniform_modulus_intervals": bool(
            len(lookup) == EXPECTED_RELEVANT_IDENTIFIER_COUNT
            and set(lookup) == directly_relevant_identifiers | set(prior_records)
            and len(directly_relevant_identifiers)
            == EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT
            and len(selected_identifiers) == SELECTED_DIMENSION
            and len(external_identifiers) == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
            and selected_identifiers.isdisjoint(external_identifiers)
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
        "all_q011ad_68_uniform_records_are_preserved_exactly": bool(
            len(prior_records) == 68
            and set(prior_records).issubset(current_records)
            and all(
                current_records[identifier] == record
                for identifier, record in prior_records.items()
            )
        ),
        "uniform_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    audit = {
        "active_selected_group_indices": active_group_indices,
        "uniform_radius": _fraction_record(UNIFORM_REFINED_RADIUS),
        "uniform_radius_formula": "rho=1/20,000,000=5e-8",
        "maximum_transformed_residual_radius": _fraction_record(theta[maximum_theta_block]),
        "maximum_theta_block": maximum_theta_block,
        "minimum_q011k_old_radius": _fraction_record(old_radii[minimum_old_radius_block]),
        "minimum_old_radius_block": minimum_old_radius_block,
        "directly_relevant_identifier_count": len(directly_relevant_identifiers),
        "relevant_identifier_count": len(lookup),
        "unique_center_modulus_evaluation_count": len(modulus_cache),
        "uniform_disc_records": records,
        "uniform_record_digest_sha256": q011b._canonical_json_sha256(records),
        "containment_chain": (
            "spectrum subset union D(c_j,theta_b) subset union D(c_j,rho) "
            "subset union D(c_j,r_old,b)"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup


def _streaming_sector_product_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
    overlap_records: tuple[dict[str, Any], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> tuple[dict[str, Any], dict[str, Any], Fraction]:
    monomial_framer = q011z._FramedRecordDigest("Q011ae/degree11-monomial/v1")
    pair_framer = q011z._FramedRecordDigest("Q011ae/degree11-compatible-pair/v1")
    product_framer = q011z._FramedRecordDigest("Q011ae/exact-modulus-product/v1")
    comparison_framer = q011z._FramedRecordDigest(
        "Q011ae/exact-modulus-comparison/v1"
    )

    target_histograms = [
        Counter(q011z._identifier_indices(identifier)[0] for identifier in target_group)
        for target_group in external_target_groups
    ]
    targets_by_block = []
    for target_group in external_target_groups:
        block_lookup: dict[int, list[str]] = {}
        for identifier in target_group:
            block = q011z._identifier_indices(identifier)[0]
            block_lookup.setdefault(block, []).append(identifier)
        targets_by_block.append(
            {block: tuple(identifiers) for block, identifiers in block_lookup.items()}
        )

    monomial_counts: list[int] = []
    compatible_monomial_counts: list[int] = []
    comparison_counts: list[int] = []
    sector_histograms: list[Counter[int]] = []
    boundary_records: list[dict[str, Any]] = []
    aggregate_counts = [Counter() for _ in OVERLAP_COUNTS]
    aggregate_minima: list[Fraction | None] = [None] * len(OVERLAP_COUNTS)
    aggregate_witnesses: list[dict[str, Any] | None] = [None] * len(OVERLAP_COUNTS)
    relation_counts: Counter[str] = Counter()
    minimum_gap: Fraction | None = None
    minimum_witness: dict[str, Any] | None = None
    first_unresolved: dict[str, Any] | None = None
    monomial_index = 0
    comparison_index = 0
    compatible_monomial_count = 0
    separated_count = 0
    unresolved_count = 0
    radii_nonnegative = True
    intervals_ordered = True

    for aggregate_index, overlap in enumerate(overlap_records):
        counts = tuple(overlap["selected_type_counts"])
        choices = [
            tuple(itertools.combinations_with_replacement(group, count))
            for group, count in zip(selected_groups, counts, strict=True)
        ]
        aggregate_start = monomial_index
        aggregate_compatible_start = compatible_monomial_count
        aggregate_comparison_start = comparison_index
        histogram: Counter[int] = Counter()
        first_monomial: dict[str, Any] | None = None
        last_monomial: dict[str, Any] | None = None
        for parts in itertools.product(*choices):
            identifiers = tuple(itertools.chain.from_iterable(parts))
            blocks = [q011z._identifier_indices(identifier)[0] for identifier in identifiers]
            output_block = sum(blocks) % SIZE
            monomial = {
                "monomial_index": monomial_index,
                "aggregate_index": aggregate_index,
                "selected_type_counts": list(counts),
                "source_identifiers": list(identifiers),
                "input_blocks": blocks,
                "output_block": output_block,
            }
            monomial_framer.update(monomial)
            histogram[output_block] += 1
            if first_monomial is None:
                first_monomial = monomial
            last_monomial = monomial

            matching_targets = targets_by_block[aggregate_index].get(output_block, ())
            if matching_targets:
                compatible_monomial_count += 1
                discs = [lookup[identifier] for identifier in identifiers]
                center_lower_product = Fraction(1)
                center_upper_product = Fraction(1)
                full_upper_product = Fraction(1)
                for disc in discs:
                    center_lower_product *= disc.center_modulus.lower
                    center_upper_product *= disc.center_modulus.upper
                    full_upper_product *= (
                        disc.center_modulus.upper + UNIFORM_REFINED_RADIUS
                    )
                product_radius = full_upper_product - center_upper_product
                product_modulus = RationalInterval(
                    max(Fraction(0), center_lower_product - product_radius),
                    center_upper_product + product_radius,
                )
                radii_nonnegative = radii_nonnegative and product_radius >= 0
                intervals_ordered = (
                    intervals_ordered
                    and 0 <= product_modulus.lower <= product_modulus.upper
                )
                product_framer.update(
                    {
                        "monomial_index": monomial_index,
                        "aggregate_index": aggregate_index,
                        "center_modulus_lower_product": (
                            q011z._exact_fraction_record(center_lower_product)
                        ),
                        "center_modulus_upper_product": (
                            q011z._exact_fraction_record(center_upper_product)
                        ),
                        "uniform_product_radius": (
                            q011z._exact_fraction_record(product_radius)
                        ),
                        "product_modulus_lower": (
                            q011z._exact_fraction_record(product_modulus.lower)
                        ),
                        "product_modulus_upper": (
                            q011z._exact_fraction_record(product_modulus.upper)
                        ),
                    }
                )
                for target_identifier in matching_targets:
                    pair_framer.update(
                        {
                            "comparison_index": comparison_index,
                            "monomial_index": monomial_index,
                            "aggregate_index": aggregate_index,
                            "target_identifier": target_identifier,
                        }
                    )
                    target = lookup[target_identifier]
                    if product_modulus.upper < target.modulus.lower:
                        gap = target.modulus.lower - product_modulus.upper
                        relation = "product_below_target"
                        classification = "individual_modulus_separation"
                    elif target.modulus.upper < product_modulus.lower:
                        gap = product_modulus.lower - target.modulus.upper
                        relation = "target_below_product"
                        classification = "individual_modulus_separation"
                    else:
                        gap = None
                        relation = "overlap"
                        classification = "unresolved_interval_overlap"

                    aggregate_counts[aggregate_index][classification] += 1
                    relation_counts[relation] += 1
                    separated_count += int(gap is not None)
                    unresolved_count += int(gap is None)
                    comparison_framer.update(
                        {
                            "comparison_index": comparison_index,
                            "monomial_index": monomial_index,
                            "aggregate_index": aggregate_index,
                            "target_identifier": target_identifier,
                            "product_modulus_lower": (
                                q011z._exact_fraction_record(product_modulus.lower)
                            ),
                            "product_modulus_upper": (
                                q011z._exact_fraction_record(product_modulus.upper)
                            ),
                            "target_modulus_lower": (
                                q011z._exact_fraction_record(target.modulus.lower)
                            ),
                            "target_modulus_upper": (
                                q011z._exact_fraction_record(target.modulus.upper)
                            ),
                            "individual_modulus_relation": relation,
                            "modulus_gap": (
                                None
                                if gap is None
                                else q011z._exact_fraction_record(gap)
                            ),
                            "classification": classification,
                        }
                    )
                    if gap is None:
                        if first_unresolved is None:
                            first_unresolved = {
                                "aggregate_index": aggregate_index,
                                "selected_type_counts": list(counts),
                                "source_identifiers": list(identifiers),
                                "output_block": output_block,
                                "target_identifier": target_identifier,
                            }
                    else:
                        witness = q011z._minimum_witness(
                            monomial, target_identifier, relation, gap
                        )
                        if minimum_gap is None or gap < minimum_gap:
                            minimum_gap = gap
                            minimum_witness = witness
                        if (
                            aggregate_minima[aggregate_index] is None
                            or gap < aggregate_minima[aggregate_index]
                        ):
                            aggregate_minima[aggregate_index] = gap
                            aggregate_witnesses[aggregate_index] = witness
                    comparison_index += 1
            monomial_index += 1

        if first_monomial is None or last_monomial is None:
            raise RuntimeError("Q011ae encountered an empty overlap aggregate")
        monomial_counts.append(monomial_index - aggregate_start)
        compatible_monomial_counts.append(
            compatible_monomial_count - aggregate_compatible_start
        )
        comparison_counts.append(comparison_index - aggregate_comparison_start)
        sector_histograms.append(histogram)
        boundary_records.append(
            {
                "aggregate_index": aggregate_index,
                "first_monomial": first_monomial,
                "last_monomial": last_monomial,
            }
        )

    if minimum_gap is None or minimum_witness is None:
        raise RuntimeError("Q011ae has no separated modulus comparison")

    x_sector = artifacts["q011x"]["cycle"]["fourier_output_sector_audit"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    structural_wave_sum = bool(
        x_sector["passed"]
        and all(x_sector["structural_proof"].values())
        and u_theorem[
            "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
        ]
    )
    selected_groups_are_disjoint_ordered_sets = bool(
        all(tuple(sorted(group)) == group and len(group) == len(set(group)) for group in selected_groups)
        and sum(len(group) for group in selected_groups)
        == len(set().union(*(set(group) for group in selected_groups)))
    )
    streaming_contract = {
        "algorithm": (
            "single pass over canonical combinations-with-replacement products; "
            "only the current monomial, current compatible product, compact "
            "histograms, boundary records, extrema, witnesses and four digest "
            "states are retained"
        ),
        "full_monomial_record_list_retained": False,
        "full_compatible_pair_record_list_retained": False,
        "full_product_record_list_retained": False,
        "full_comparison_record_list_retained": False,
        "peak_live_monomial_record_count": 1,
        "peak_live_product_record_count": 1,
        "retained_boundary_record_count": len(boundary_records) * 2,
    }
    sector_compact_record = {
        "boundary_records": boundary_records,
        "aggregate_sector_histograms": [
            dict(sorted(histogram.items())) for histogram in sector_histograms
        ],
        "target_sector_histograms": [
            dict(sorted(histogram.items())) for histogram in target_histograms
        ],
        "compatible_monomial_counts": compatible_monomial_counts,
        "comparison_counts": comparison_counts,
        "compatible_monomial_count": compatible_monomial_count,
        "framed_monomial_digest": monomial_framer.hexdigest(),
        "framed_pair_digest": pair_framer.hexdigest(),
        "streaming_contract": streaming_contract,
    }
    sector_checks = {
        "translation_equivariance_and_c91_regular_map_give_undecic_wave_sum": (
            structural_wave_sum
        ),
        "combination_with_replacement_counts_reproduce": bool(
            tuple(monomial_counts) == EXPECTED_MONOMIAL_COUNTS
            and all(
                count == q011z._monomial_count_for_counts(selected_groups, counts)
                for count, counts in zip(monomial_counts, OVERLAP_COUNTS, strict=True)
            )
        ),
        "canonical_cartesian_enumeration_is_injective_without_a_retained_set": (
            selected_groups_are_disjoint_ordered_sets
        ),
        "all_2299104_and_only_degree_eleven_overlap_monomials_are_enumerated": bool(
            monomial_index == EXPECTED_INDEXED_MONOMIAL_COUNT
            and monomial_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
        ),
        "registered_monomial_sector_histograms_reproduce": (
            tuple(dict(sorted(histogram.items())) for histogram in sector_histograms)
            == EXPECTED_SECTOR_HISTOGRAMS
        ),
        "registered_target_sector_histograms_reproduce": (
            tuple(dict(sorted(histogram.items())) for histogram in target_histograms)
            == EXPECTED_TARGET_SECTOR_HISTOGRAMS
        ),
        "compatible_and_incompatible_monomial_counts_reproduce": bool(
            tuple(compatible_monomial_counts) == EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
            and compatible_monomial_count == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and monomial_index - compatible_monomial_count
            == EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT
        ),
        "all_820492_and_only_compatible_comparisons_are_enumerated": bool(
            tuple(comparison_counts) == EXPECTED_COMPARISON_COUNTS
            and comparison_index == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "last_three_aggregates_are_exactly_fourier_empty": bool(
            compatible_monomial_counts[-3:] == [0, 0, 0]
            and comparison_counts[-3:] == [0, 0, 0]
        ),
        "framed_sector_record_counts_and_sha256_shapes_reproduce": bool(
            monomial_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
            and pair_framer.count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
            and len(monomial_framer.hexdigest()) == 64
            and len(pair_framer.hexdigest()) == 64
        ),
        "streaming_contract_is_observed": bool(
            not streaming_contract["full_monomial_record_list_retained"]
            and not streaming_contract["full_compatible_pair_record_list_retained"]
            and streaming_contract["peak_live_monomial_record_count"] == 1
        ),
        "sector_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(sector_compact_record)
            and _strict_json_serializable(sector_compact_record)
            and json.dumps(sector_compact_record, allow_nan=False)
        ),
    }
    sector_audit = {
        "output_sector_law": "b_out=(sum_i=1^11 b_i) mod 17",
        "structural_proof": {
            "q011x_translation_equivariant_wave_sum_is_preserved": bool(
                x_sector["passed"] and all(x_sector["structural_proof"].values())
            ),
            "q011u_c91_regular_original_map_is_preserved": u_theorem[
                "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
            ],
            "eleven_fourier_characters_multiply_to_the_sum_character": True,
            "translation_equivariance_applies_at_undecic_order": structural_wave_sum,
        },
        "indexed_monomial_count": monomial_index,
        "aggregate_monomial_counts": monomial_counts,
        "aggregate_sector_histograms": [
            {str(key): value for key, value in sorted(histogram.items())}
            for histogram in sector_histograms
        ],
        "external_target_counts": [len(group) for group in external_target_groups],
        "external_target_sector_histograms": [
            {str(key): value for key, value in sorted(histogram.items())}
            for histogram in target_histograms
        ],
        "aggregate_sector_compatible_monomial_counts": compatible_monomial_counts,
        "sector_compatible_monomial_count": compatible_monomial_count,
        "sector_incompatible_monomial_count": (
            monomial_index - compatible_monomial_count
        ),
        "aggregate_compatible_comparison_counts": comparison_counts,
        "sector_compatible_comparison_count": comparison_index,
        "fourier_empty_aggregate_indices": [
            index for index, count in enumerate(comparison_counts) if count == 0
        ],
        "boundary_records": boundary_records,
        "streaming_contract": streaming_contract,
        "framed_exact_record_digests": {
            "algorithm": (
                "SHA-256 over domain and ordered records, each framed by an "
                "unsigned 8-byte big-endian UTF-8 canonical-JSON byte length"
            ),
            "monomial_record_count": monomial_framer.count,
            "monomial_record_digest_sha256": monomial_framer.hexdigest(),
            "compatible_pair_record_count": pair_framer.count,
            "compatible_pair_record_digest_sha256": pair_framer.hexdigest(),
        },
        "compact_sector_digest_sha256": (
            q011b._canonical_json_sha256(sector_compact_record)
        ),
        "checks": sector_checks,
        "passed": all(sector_checks.values()),
    }

    expected_global_source = [
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=1;center=151",
        "block=1;center=152",
        "block=1;center=152",
        "block=0;center=147",
        "block=0;center=147",
    ]
    product_compact_record = {
        "aggregate_counts": [
            {
                "aggregate_index": index,
                "selected_type_counts": list(OVERLAP_COUNTS[index]),
                "external_group_index": EXTERNAL_GROUP_INDICES[index],
                "individual_modulus_separation_count": counts[
                    "individual_modulus_separation"
                ],
                "unresolved_interval_overlap_count": counts[
                    "unresolved_interval_overlap"
                ],
            }
            for index, counts in enumerate(aggregate_counts)
        ],
        "relation_counts": dict(sorted(relation_counts.items())),
        "aggregate_minimum_gap_witnesses": aggregate_witnesses,
        "global_minimum_gap_witness": minimum_witness,
        "first_unresolved": first_unresolved,
        "product_digest": product_framer.hexdigest(),
        "comparison_digest": comparison_framer.hexdigest(),
        "streaming_contract": streaming_contract,
    }
    product_checks = {
        "all_383062_and_only_fourier_compatible_products_are_reconstructed": bool(
            product_framer.count == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and product_framer.count == compatible_monomial_count
            and radii_nonnegative
            and intervals_ordered
        ),
        "uniform_triangle_inequality_product_formula_is_applied": bool(
            radii_nonnegative and intervals_ordered
        ),
        "all_820492_compatible_comparisons_are_evaluated": (
            comparison_framer.count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "comparison_categories_partition_all_records": (
            separated_count + unresolved_count
            == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "aggregate_comparison_counts_reproduce": tuple(
            counts["individual_modulus_separation"]
            + counts["unresolved_interval_overlap"]
            for counts in aggregate_counts
        )
        == EXPECTED_COMPARISON_COUNTS,
        "fourier_empty_aggregates_create_no_product_or_comparison": bool(
            compatible_monomial_counts[-3:] == [0, 0, 0]
            and comparison_counts[-3:] == [0, 0, 0]
            and aggregate_minima[-3:] == [None, None, None]
        ),
        "minimum_gap_and_witness_reproduce": bool(
            minimum_witness["aggregate_index"] == 2
            and minimum_witness["selected_type_counts"] == [0, 7, 2, 2]
            and minimum_witness["source_identifiers"] == expected_global_source
            and minimum_witness["output_block"] == 14
            and minimum_witness["target_identifier"] == "block=14;center=146"
            and minimum_witness["individual_modulus_relation"]
            == "product_below_target"
        ),
        "framed_product_record_counts_and_sha256_shapes_reproduce": bool(
            product_framer.count == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and comparison_framer.count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
            and len(product_framer.hexdigest()) == 64
            and len(comparison_framer.hexdigest()) == 64
        ),
        "streaming_contract_is_observed": bool(
            not streaming_contract["full_product_record_list_retained"]
            and not streaming_contract["full_comparison_record_list_retained"]
            and streaming_contract["peak_live_product_record_count"] == 1
        ),
        "compact_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(product_compact_record)
            and _strict_json_serializable(product_compact_record)
            and json.dumps(product_compact_record, allow_nan=False)
        ),
    }
    product_audit = {
        "uniform_product_modulus_formula": {
            "center_modulus": (
                "product_i ell_i <= |product_i c_i| <= product_i u_i"
            ),
            "radius": (
                "R=product_i(u_i+rho)-product_i(u_i), i=1..11"
            ),
            "product_interval": (
                "[max(0,product_i ell_i-R),product_i u_i+R]"
            ),
            "target_interval": "[max(0,ell_e-rho),u_e+rho]",
        },
        "compatible_product_record_count": product_framer.count,
        "product_record_count": product_framer.count,
        "fourier_incompatible_product_interval_count": 0,
        "comparison_record_count": comparison_framer.count,
        "individual_modulus_separation_count": separated_count,
        "unresolved_interval_overlap_count": unresolved_count,
        "individual_modulus_relation_counts": dict(sorted(relation_counts.items())),
        "aggregate_category_counts": product_compact_record["aggregate_counts"],
        "aggregate_minimum_modulus_gaps": [
            _fraction_record(value) if value is not None else None
            for value in aggregate_minima
        ],
        "aggregate_minimum_gap_witnesses": aggregate_witnesses,
        "minimum_modulus_gap": _fraction_record(minimum_gap),
        "registered_minimum_modulus_gap": _fraction_record(MINIMUM_MODULUS_GAP),
        "minimum_gap_witness": minimum_witness,
        "first_unresolved_interval_overlap": first_unresolved,
        "streaming_contract": streaming_contract,
        "framed_exact_record_digests": {
            "algorithm": (
                "SHA-256 over domain and ordered records, each framed by an "
                "unsigned 8-byte big-endian UTF-8 canonical-JSON byte length"
            ),
            "exact_product_record_count": product_framer.count,
            "exact_product_record_digest_sha256": product_framer.hexdigest(),
            "exact_comparison_record_count": comparison_framer.count,
            "exact_comparison_record_digest_sha256": comparison_framer.hexdigest(),
        },
        "compact_product_digest_sha256": (
            q011b._canonical_json_sha256(product_compact_record)
        ),
        "checks": product_checks,
        "passed": all(product_checks.values()),
    }
    return sector_audit, product_audit, minimum_gap

def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "coordinate_slot_count": COORDINATE_SLOT_COUNT,
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "degree": DEGREE,
        "degree_aggregate_count": EXPECTED_DEGREE_AGGREGATE_COUNT,
        "degree_expanded_product_control_count": (EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT),
        "overlap_counts": [list(counts) for counts in OVERLAP_COUNTS],
        "selected_source_group_sizes": list(EXPECTED_SELECTED_GROUP_SIZES),
        "external_group_indices": list(EXTERNAL_GROUP_INDICES),
        "external_target_counts": list(EXPECTED_EXTERNAL_TARGET_COUNTS),
        "unique_external_target_count": (EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT),
        "directly_relevant_identifier_count": (EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT),
        "relevant_identifier_count": EXPECTED_RELEVANT_IDENTIFIER_COUNT,
        "aggregate_monomial_counts": list(EXPECTED_MONOMIAL_COUNTS),
        "aggregate_sector_compatible_monomial_counts": list(
            EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
        ),
        "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
        "sector_compatible_monomial_count": (EXPECTED_COMPATIBLE_MONOMIAL_COUNT),
        "sector_incompatible_monomial_count": (EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT),
        "aggregate_compatible_comparison_counts": list(EXPECTED_COMPARISON_COUNTS),
        "compatible_comparison_count": (EXPECTED_COMPATIBLE_COMPARISON_COUNT),
        "streaming_product_interval_count": EXPECTED_COMPATIBLE_MONOMIAL_COUNT,
        "uniform_refined_radius": _fraction_record(UNIFORM_REFINED_RADIUS),
        "minimum_modulus_gap": _fraction_record(MINIMUM_MODULUS_GAP),
        "framed_record_digest_schema": 1,
        "floating_point_used_for_gate_decisions": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "inventory_digest_sha256": cycle["inventory_digest_sha256"],
        "sector_digest_sha256": cycle["sector_digest_sha256"],
        "product_digest_sha256": cycle["product_digest_sha256"],
    }


def run_degree11_refined_modulus_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = _inventory_audit(
        artifacts
    )
    envelope, lookup = _uniform_envelope_audit(
        artifacts, selected_groups, external_target_groups
    )
    sector, product, minimum_gap = _streaming_sector_product_audit(
        artifacts,
        selected_groups,
        external_target_groups,
        overlap_records,
        lookup,
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    inventory_sections = {
        "degree11_modulus_inventory_audit": inventory,
        "uniform_refined_envelope_audit": envelope,
    }
    sector_sections = {"fourier_output_sector_audit": sector}
    product_sections = {"indexed_modulus_product_audit": product}
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(inventory_sections)
    sector_digest = q011b._canonical_json_sha256(sector_sections)
    product_digest = q011b._canonical_json_sha256(product_sections)
    strict_payload = {
        **input_sections,
        **inventory_sections,
        **sector_sections,
        **product_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and inventory_digest == q011b._canonical_json_sha256(inventory_sections)
        and sector_digest == q011b._canonical_json_sha256(sector_sections)
        and product_digest == q011b._canonical_json_sha256(product_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    fourier_empty_count = len(sector["fourier_empty_aggregate_indices"])
    product_audited_overlap_count = sum(
        (
            record["individual_modulus_separation_count"]
            + record["unresolved_interval_overlap_count"]
        )
        > 0
        for record in product["aggregate_category_counts"]
    )
    validity_gates = {
        "nine_artifacts_forty_eight_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad artifacts, runners, 48 digests, "
                "outcomes, claim boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_eleven_inventory_and_fourteen_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "364 aggregates, 4368 controls, 350 separated and fourteen "
                "registered overlaps"
            ),
            "value": inventory["checks"],
        },
        "uniform_radius_containment_and_84_monotone_moduli_reproduce": {
            "passed": envelope["passed"],
            "threshold": (
                "theta_b <= rho=5e-8 <= every old Q011k radius, 52 directly "
                "relevant intervals, an 84-record monotone envelope and exact "
                "preservation of all 68 Q011ad records"
            ),
            "value": envelope["checks"],
        },
        "all_monomials_histograms_and_fourier_partitions_reproduce": {
            "passed": sector["passed"],
            "threshold": (
                "2299104 monomials, registered undecic histograms, 383062 "
                "compatible monomials and 820492 comparisons"
            ),
            "value": sector["checks"],
        },
        "streamed_products_comparisons_gaps_and_four_digests_reproduce": {
            "passed": product["passed"],
            "threshold": (
                "383062 compatible products and 820492 target comparisons "
                "stream through four framed digests with strict gaps"
            ),
            "value": product["checks"],
        },
        "old_separations_product_audits_and_fourier_empty_cases_cover_all_aggregates": {
            "passed": bool(
                inventory["passed"]
                and sector["passed"]
                and product["passed"]
                and inventory["old_modulus_separated_aggregate_count"]
                + product_audited_overlap_count
                + fourier_empty_count
                == EXPECTED_DEGREE_AGGREGATE_COUNT
                and product_audited_overlap_count == 11
                and fourier_empty_count == 3
            ),
            "threshold": (
                "350 old-separated plus eleven streamed-product and three "
                "Fourier-empty audits cover all 364 aggregates"
            ),
            "value": {
                "old_separated": inventory["old_modulus_separated_aggregate_count"],
                "streamed_product_overlaps": product_audited_overlap_count,
                "fourier_empty_overlaps": fourier_empty_count,
            },
        },
        "strict_serialization_section_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite compact strict JSON, four section digests, result "
                "digest and runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    complete_coverage = bool(
        inventory["passed"]
        and inventory["degree_modulus_aggregate_count"]
        == EXPECTED_DEGREE_AGGREGATE_COUNT
        and inventory["old_modulus_separated_aggregate_count"]
        == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
        and inventory["old_modulus_overlap_aggregate_count"]
        == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        and sector["indexed_monomial_count"] == EXPECTED_INDEXED_MONOMIAL_COUNT
        and sector["sector_compatible_monomial_count"]
        == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
        and sector["sector_incompatible_monomial_count"]
        == EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT
        and sector["sector_compatible_comparison_count"]
        == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        and product_audited_overlap_count == 11
        and fourier_empty_count == 3
    )
    zero_unresolved = product["unresolved_interval_overlap_count"] == 0
    all_individual = (
        product["individual_modulus_separation_count"]
        == EXPECTED_COMPATIBLE_COMPARISON_COUNT
    )
    hypothesis_gates = {
        "uniform_envelope_is_spectrally_valid_and_old_disc_contained": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": (
                "all transformed-residual discs subset rho-discs subset Q011k discs"
            ),
            "value": envelope["checks"],
        },
        "old_separation_fourier_empty_and_products_partition_all_cases": {
            "passed": bool(validity_passed and complete_coverage),
            "threshold": (
                "all 364 aggregates and 2299104 monomials partition into old "
                "separation, exact Fourier-empty and streamed indexed products"
            ),
            "value": {
                "aggregates": inventory["degree_modulus_aggregate_count"],
                "monomials": sector["indexed_monomial_count"],
                "streamed_products": product["compatible_product_record_count"],
                "fourier_empty_aggregates": fourier_empty_count,
            },
        },
        "all_compatible_products_have_individual_modulus_separation": {
            "passed": bool(validity_passed and zero_unresolved and all_individual),
            "threshold": (
                "820492 individual modulus separations and zero unresolved "
                "interval overlaps"
            ),
            "value": {
                "individual": product["individual_modulus_separation_count"],
                "unresolved": product["unresolved_interval_overlap_count"],
            },
        },
        "minimum_modulus_gap_fits_the_registered_robust_margin": {
            "passed": bool(
                validity_passed
                and zero_unresolved
                and minimum_gap >= MINIMUM_MODULUS_GAP
            ),
            "threshold": "minimum exact modulus gap >=5e-6",
            "value": product["minimum_modulus_gap"],
        },
        "degree_eleven_external_nonresonance_follows_from_complete_partition": {
            "passed": bool(
                validity_passed
                and complete_coverage
                and zero_unresolved
                and all_individual
            ),
            "threshold": (
                "350 old separations, eleven refined product audits and three "
                "Fourier-empty audits imply degree-11 external nonresonance"
            ),
            "value": {
                "preserved_old_separations": (
                    inventory["old_modulus_separated_aggregate_count"]
                ),
                "resolved_product_overlap_aggregates": product_audited_overlap_count,
                "fourier_empty_overlap_aggregates": fourier_empty_count,
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q011ae degree-eleven streaming refined-modulus audit is invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Do exact Fourier sectors and the contained uniform "
            "transformed-residual envelope give strict streamed "
            "indexed-modulus separation for all fourteen degree-eleven "
            "overlap aggregates?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "inventory_digest_sha256": inventory_digest,
        "sector_digest_sha256": sector_digest,
        "product_digest_sha256": product_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    degree_eleven_certified = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "uniform_transformed_residual_envelope_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "all_fourteen_degree_eleven_old_modulus_overlaps_are_eliminated": (
            degree_eleven_certified
        ),
        "eleven_overlaps_are_eliminated_by_streamed_indexed_products": bool(
            degree_eleven_certified and product_audited_overlap_count == 11
        ),
        "three_overlaps_are_eliminated_by_exact_fourier_structure": bool(
            degree_eleven_certified and fourier_empty_count == 3
        ),
        "degree_eleven_external_nonresonance_is_certified": (
            degree_eleven_certified
        ),
        "certified_external_nonresonance_degrees": (
            list(range(2, 12)) if degree_eleven_certified else list(range(2, 11))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(
            range(12 if degree_eleven_certified else 11, 91)
        ),
        "degrees_12_through_90_are_certified": False,
        "complex_phase_was_required_for_degree_eleven": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011ad_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree eleven for the fixed 17x17 repaired "
        "exact map on one fixed conservation leaf, the fourteen Q011u "
        "modulus-overlap aggregates, the Q011y transformed-residual "
        "enclosure, the uniform rho=5e-8 discs, exact x-Fourier sectors and "
        "the streamed indexed-modulus product formula. It certifies no "
        "degree from 12 through 90, no all-order nonresonance, equality with "
        "the Q011t graph, C2 or higher graph smoothness, SSM existence or "
        "uniqueness, normal attraction, basin, other grid, force, wall or "
        "D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_degree_five_acceptance_changed": False,
        "q011y_eigendisc_refinement_acceptance_changed": False,
        "q011z_degree_six_acceptance_changed": False,
        "q011aa_degree_seven_acceptance_changed": False,
        "q011ab_degree_eight_acceptance_changed": False,
        "q011ac_degree_nine_acceptance_changed": False,
        "q011ad_degree_ten_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011af to audit degree 12 with the same exact "
            "Fourier-first streaming discipline."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Send only the first unresolved degree-eleven streamed product "
            "to an exact complex phase-sensitive product-disc comparison."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, envelope, sector, "
            "streaming product, coverage or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ae cycle failed strict serialization or digest")
    return cycle

def run_q011ae_study() -> dict[str, Any]:
    cycle = run_degree11_refined_modulus_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "floating_point_used_for_gate_decisions": False,
            "old_eigencenter_count": COORDINATE_SLOT_COUNT,
            "uniform_directly_relevant_identifier_count": (
                EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT
            ),
            "uniform_relevant_identifier_count": (EXPECTED_RELEVANT_IDENTIFIER_COUNT),
            "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
            "streamed_compatible_product_count": (
                EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            ),
            "compatible_comparison_count": (EXPECTED_COMPATIBLE_COMPARISON_COUNT),
            "exact_record_storage": (
                "four framed SHA-256 streams plus compact histograms, "
                "boundaries, extrema and witnesses"
            ),
        },
        "mathematical_scope": {
            "diagnostic": (
                "degree-eleven exact-Fourier streaming refined-envelope "
                "indexed-modulus products"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_eleven_external_nonresonance_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "degrees_12_through_90_claim": False,
            "actual_complex_resonance_claim": False,
            "ssm_uniqueness_claim": False,
            "normal_attraction_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011ae_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
