"""Q011af degree-twelve Fourier-multiplicity compressed certificate."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from collections.abc import Iterator
from datetime import UTC, datetime
from fractions import Fraction
from math import comb, prod
from pathlib import Path
from typing import Any

import research.q011ae_degree11_streaming_modulus as q011ae
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
DEGREE = 12
EXPECTED_DEGREE_AGGREGATE_COUNT = 455
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 6188
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 426
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 29
OVERLAP_COUNTS = (
    (0, 4, 0, 8),
    (0, 4, 1, 7),
    (0, 6, 1, 5),
    (0, 6, 2, 4),
    (0, 6, 3, 3),
    (2, 7, 2, 1),
    (2, 7, 3, 0),
    (3, 6, 0, 3),
    (3, 6, 1, 2),
    (3, 6, 2, 1),
    (3, 6, 3, 0),
    (3, 9, 0, 0),
    (4, 5, 0, 3),
    (4, 5, 1, 2),
    (4, 5, 2, 1),
    (4, 5, 3, 0),
    (4, 8, 0, 0),
    (5, 4, 0, 3),
    (5, 4, 1, 2),
    (5, 4, 2, 1),
    (5, 4, 3, 0),
    (6, 3, 0, 3),
    (6, 3, 1, 2),
    (9, 1, 0, 2),
    (9, 1, 1, 1),
    (9, 1, 2, 0),
    (10, 0, 0, 2),
    (10, 0, 1, 1),
    (10, 0, 2, 0),
)
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXTERNAL_GROUP_INDICES = (
    167,
    167,
    165,
    165,
    165,
    162,
    162,
    162,
    162,
    162,
    162,
    159,
    162,
    162,
    162,
    162,
    159,
    162,
    162,
    162,
    162,
    162,
    162,
    161,
    161,
    161,
    161,
    161,
    161,
)
EXPECTED_EXTERNAL_TARGET_COUNTS = (
    8,
    8,
    4,
    4,
    4,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
    8,
)
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 36
EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT = 60
EXPECTED_RELEVANT_IDENTIFIER_COUNT = 92
EXPECTED_MODULUS_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_MONOMIAL_COUNTS = (
    225225,
    480480,
    266112,
    277200,
    201600,
    345600,
    86400,
    1209600,
    1451520,
    806400,
    201600,
    26400,
    2217600,
    2661120,
    1478400,
    369600,
    54450,
    3326400,
    3991680,
    2217600,
    554400,
    4118400,
    4942080,
    1647360,
    1464320,
    457600,
    700128,
    622336,
    194480,
)
EXPECTED_INDEXED_MONOMIAL_COUNT = 36_596_091
EXPECTED_SIGNATURE_COUNTS = (
    6435,
    11880,
    5292,
    5292,
    3920,
    2880,
    800,
    7840,
    8820,
    5040,
    1400,
    200,
    11760,
    13230,
    7560,
    2100,
    315,
    15680,
    17640,
    10080,
    2800,
    18816,
    21168,
    9240,
    7920,
    2640,
    6006,
    5148,
    1716,
)
EXPECTED_SIGNATURE_COUNT = 213_618
EXPECTED_COMPATIBLE_SIGNATURE_COUNTS = (
    3355,
    6040,
    2576,
    2548,
    1904,
    2880,
    800,
    7840,
    8820,
    5040,
    1400,
    200,
    11760,
    13230,
    7560,
    2100,
    315,
    15680,
    17640,
    10080,
    2800,
    18816,
    21168,
    5720,
    4400,
    1760,
    3718,
    2860,
    1144,
)
EXPECTED_COMPATIBLE_SIGNATURE_COUNT = 184_154
EXPECTED_COMPATIBLE_MONOMIAL_COUNTS = (
    51925,
    111564,
    40304,
    41944,
    30640,
    66496,
    16616,
    218960,
    262200,
    145840,
    36560,
    3920,
    381840,
    456260,
    253960,
    63940,
    8440,
    556608,
    664176,
    369856,
    93376,
    688272,
    821456,
    512720,
    411360,
    153520,
    210276,
    168664,
    62972,
)
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 6_904_665
EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT = 29_691_426
EXPECTED_WEIGHTED_COMPARISON_COUNTS = (
    150780,
    325168,
    80608,
    83888,
    61280,
    132992,
    33232,
    437920,
    524400,
    291680,
    73120,
    14880,
    763680,
    912520,
    507920,
    127880,
    32500,
    1113216,
    1328352,
    739712,
    186752,
    1376544,
    1642912,
    1025440,
    822720,
    307040,
    420552,
    337328,
    125944,
)
EXPECTED_WEIGHTED_COMPARISON_COUNT = 13_980_960
EXPECTED_DISTINCT_COMPARISON_COUNTS = (
    26840,
    48320,
    10304,
    10192,
    7616,
    16640,
    4480,
    44800,
    51520,
    29120,
    7840,
    1600,
    67200,
    77280,
    43680,
    11760,
    2520,
    89600,
    103040,
    58240,
    15680,
    107520,
    123648,
    45760,
    35200,
    14080,
    29744,
    22880,
    9152,
)
EXPECTED_DISTINCT_COMPARISON_COUNT = 1_116_256
EXPECTED_CLASS_MEMBERSHIP_DIGEST = (
    "269187f8489521c7e37ae8a91669b9dc020ac10d4ef1d42272bb636fa7bc9b8c"
)
EXPECTED_WAVE_HISTOGRAM_DIGEST = (
    "c40e7b6d9941f7c7c2836b9720c4a577f56d529591c01af3f3c732ba4ed10171"
)
EXPECTED_SIGNATURE_RECORD_DIGEST = (
    "d03f1a33f561698d1fca3ca62e929ffc1cef686ff3838e41359b9adf24471432"
)
Q011AE_ORACLE_SIGNATURE_COUNTS = (
    2772,
    4536,
    1008,
    960,
    480,
    1470,
    735,
    2016,
    1008,
    2520,
    1260,
    660,
    572,
    364,
)
Q011AE_ORACLE_COMPATIBLE_SIGNATURE_COUNTS = (
    1296,
    2208,
    544,
    960,
    480,
    1470,
    735,
    2016,
    1008,
    2520,
    1260,
    0,
    0,
    0,
)
UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
MINIMUM_MODULUS_GAP = Fraction(5, 10**6)

Q011AE_ARTIFACT_SHA256 = "7da61f31c9a00017c2ab0665bb58b75b157f4b7f0ffad1194f07cac4ed51ff71"
Q011AE_RUNNER_SHA256 = "2bc97a29a1ae73924a61059c7f1de7b96e35b325479874cf28325946aa7e4286"
Q011AE_DIGESTS = (
    "c3a18a891f037c01134871aa876441df4c56bb6ce2b1657420b54fa0ae72fc99",
    "261284bc4cd18048228af34a1897ba00b89b930fd118afc3f7ce4dba77bf380d",
    "afeea956028309574d5f23c5a8da10c427b981bf7d54c8194265f75de8370d11",
    "40024743d9a6e193461dc5a7eb7821356b14da2a54793d126afe9b8ec2e58921",
    "90223809a06a85733d36c53b7278c9ba36e83ce2bc49a87b090945b26a638560",
)
Q011AE_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "sector_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)

ACCEPTED_CLASSIFICATION = (
    "degree-12 external nonresonance is certified by exact Fourier-multiplicity "
    "compression and the contained uniform refined-envelope products"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-12 multiplicity-compressed indexed-modulus product "
    "remains inseparable from an external target"
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
    prior_audit, artifacts = q011ae._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ae_degree11_streaming_modulus.json"
    runner_path = Path(q011ae.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digest_tuple = q011z._digest_tuple(cycle, Q011AE_DIGEST_NAMES)
    checks = {
        "q011ae_nine_prior_artifacts_and_helpers_reproduce": bool(
            prior_audit["passed"]
            and prior_audit["direct_digest_count"] == 48
            and all(prior_audit["checks"].values())
        ),
        "q011ae_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011AE_ARTIFACT_SHA256),
        "q011ae_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AE_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AE_RUNNER_SHA256
        ),
        "q011ae_digests_match": digest_tuple == Q011AE_DIGESTS,
        "q011ae_registered_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["scientific_classification"] == q011ae.ACCEPTED_CLASSIFICATION
        ),
        "q011ae_degree_eleven_scope_is_preserved": bool(
            cycle["theorem_consequence"]["degree_eleven_external_nonresonance_is_certified"]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == list(range(2, 12))
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(12, 91))
            and not cycle["theorem_consequence"]["ssm_existence_or_uniqueness_is_certified"]
        ),
        "q011ae_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ae_package_source_metadata_matches": (artifact["source"] == source_metadata()),
        "q011ae_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "fifty_three_direct_digests_are_sealed": bool(
            prior_audit["direct_digest_count"] + len(digest_tuple) == 53
        ),
    }
    artifacts["q011ae"] = artifact
    audit = {
        "prior_q011ae_sealed_input_audit": prior_audit,
        "q011ae": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AE_DIGEST_NAMES),
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
        "q011u_degree_twelve_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_twenty_nine_overlap_tuples_and_external_groups_reproduce": bool(
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
        "old_degree_eleven_certificate_is_preserved": artifacts["q011ae"]["cycle"][
            "theorem_consequence"
        ]["degree_eleven_external_nonresonance_is_certified"],
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
        for record in artifacts["q011ae"]["cycle"]["uniform_refined_envelope_audit"][
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
        "all_60_direct_and_92_monotone_identifiers_have_uniform_modulus_intervals": bool(
            len(lookup) == EXPECTED_RELEVANT_IDENTIFIER_COUNT
            and set(lookup) == directly_relevant_identifiers | set(prior_records)
            and len(directly_relevant_identifiers)
            == EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT
            and len(selected_identifiers) == SELECTED_DIMENSION
            and len(external_identifiers) == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
            and selected_identifiers.isdisjoint(external_identifiers)
            and len(modulus_cache) == 56
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
        "all_q011ae_84_uniform_records_are_preserved_exactly": bool(
            len(prior_records) == 84
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


def _weak_compositions(total: int, part_count: int) -> Iterator[tuple[int, ...]]:
    if total < 0 or part_count < 1:
        raise ValueError("weak-composition arguments must be nonnegative and nonempty")
    if part_count == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for remainder in _weak_compositions(total - first, part_count - 1):
            yield (first, *remainder)


def _cyclic_convolution(left: Counter[int], right: Counter[int]) -> Counter[int]:
    result: Counter[int] = Counter()
    for left_wave, left_count in left.items():
        for right_wave, right_count in right.items():
            result[(left_wave + right_wave) % SIZE] += left_count * right_count
    return result


def _modulus_classes(
    selected_groups: tuple[tuple[str, ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> tuple[tuple[tuple[tuple[str, ...], ...], ...], list[dict[str, Any]]]:
    grouped: list[tuple[tuple[str, ...], ...]] = []
    records: list[dict[str, Any]] = []
    for group_index, group in enumerate(selected_groups):
        by_modulus: dict[tuple[Fraction, Fraction], list[str]] = {}
        for identifier in group:
            disc = lookup[identifier]
            key = (disc.center_modulus.lower, disc.center_modulus.upper)
            by_modulus.setdefault(key, []).append(identifier)
        classes = tuple(tuple(identifiers) for identifiers in by_modulus.values())
        grouped.append(classes)
        for class_index, identifiers in enumerate(classes):
            disc = lookup[identifiers[0]]
            records.append(
                {
                    "selected_group_index": group_index,
                    "modulus_class_index": class_index,
                    "identifiers": list(identifiers),
                    "center_modulus_lower": q011z._exact_fraction_record(
                        disc.center_modulus.lower
                    ),
                    "center_modulus_upper": q011z._exact_fraction_record(
                        disc.center_modulus.upper
                    ),
                }
            )
    return tuple(grouped), records


def _group_signature_records(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    group_index: int,
    source_count: int,
) -> tuple[tuple[tuple[int, ...], Counter[int]], ...]:
    records = []
    for class_counts in _weak_compositions(
        source_count, len(classes[group_index])
    ):
        wave_multiplicities: Counter[int] = Counter({0: 1})
        for class_count, identifiers in zip(
            class_counts, classes[group_index], strict=True
        ):
            within_class: Counter[int] = Counter()
            for allocation in _weak_compositions(
                class_count, len(identifiers)
            ):
                wave = sum(
                    multiplicity * q011z._identifier_indices(identifier)[0]
                    for multiplicity, identifier in zip(
                        allocation, identifiers, strict=True
                    )
                ) % SIZE
                within_class[wave] += 1
            wave_multiplicities = _cyclic_convolution(
                wave_multiplicities, within_class
            )
        records.append((class_counts, wave_multiplicities))
    return tuple(records)


def _combined_wave_multiplicities(
    parts: tuple[tuple[tuple[int, ...], Counter[int]], ...],
) -> Counter[int]:
    wave_multiplicities: Counter[int] = Counter({0: 1})
    for _, group_wave_multiplicities in parts:
        wave_multiplicities = _cyclic_convolution(
            wave_multiplicities, group_wave_multiplicities
        )
    return wave_multiplicities


def _signature_fiber_multiplicity(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    class_counts: tuple[tuple[int, ...], ...],
) -> int:
    multiplicity = 1
    for group_classes, group_counts in zip(classes, class_counts, strict=True):
        for identifiers, count in zip(group_classes, group_counts, strict=True):
            multiplicity *= comb(
                count + len(identifiers) - 1, len(identifiers) - 1
            )
    return multiplicity


def _group_wave_witnesses(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    group_index: int,
    class_counts: tuple[int, ...],
) -> dict[int, tuple[str, ...]]:
    witnesses: dict[int, tuple[str, ...]] = {0: ()}
    for class_count, identifiers in zip(
        class_counts, classes[group_index], strict=True
    ):
        within_class: dict[int, tuple[str, ...]] = {}
        for allocation in _weak_compositions(class_count, len(identifiers)):
            wave = sum(
                multiplicity * q011z._identifier_indices(identifier)[0]
                for multiplicity, identifier in zip(
                    allocation, identifiers, strict=True
                )
            ) % SIZE
            source = tuple(
                sorted(
                    identifier
                    for multiplicity, identifier in zip(
                        allocation, identifiers, strict=True
                    )
                    for _ in range(multiplicity)
                )
            )
            if wave not in within_class or source < within_class[wave]:
                within_class[wave] = source
        convolved: dict[int, tuple[str, ...]] = {}
        for left_wave, left_source in witnesses.items():
            for right_wave, right_source in within_class.items():
                wave = (left_wave + right_wave) % SIZE
                source = tuple(sorted((*left_source, *right_source)))
                if wave not in convolved or source < convolved[wave]:
                    convolved[wave] = source
        witnesses = convolved
    return witnesses


def _source_witness_for_signature(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    class_counts: tuple[tuple[int, ...], ...],
    output_block: int,
) -> tuple[str, ...]:
    group_witnesses = [
        _group_wave_witnesses(classes, group_index, counts)
        for group_index, counts in enumerate(class_counts)
    ]
    best: tuple[str, ...] | None = None
    for choices in itertools.product(
        *(tuple(witnesses.items()) for witnesses in group_witnesses)
    ):
        if sum(wave for wave, _ in choices) % SIZE != output_block:
            continue
        source = tuple(identifier for _, group_source in choices for identifier in group_source)
        if best is None or source < best:
            best = source
    if best is None:
        raise RuntimeError("compressed signature has no requested Fourier witness")
    return best


def _q011ae_compression_oracle_audit(
    artifacts: dict[str, dict[str, Any]],
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    group_signature_cache: dict[
        tuple[int, int], tuple[tuple[tuple[int, ...], Counter[int]], ...]
    ],
) -> dict[str, Any]:
    cycle = artifacts["q011ae"]["cycle"]
    prior_inventory = cycle["degree11_modulus_inventory_audit"]
    prior_sector = cycle["fourier_output_sector_audit"]
    target_groups = tuple(
        tuple(record["identifiers"])
        for record in prior_inventory["external_target_groups"]
    )
    signature_counts = []
    compatible_signature_counts = []
    monomial_counts = []
    compatible_monomial_counts = []
    comparison_counts = []
    histograms = []
    for aggregate_index, counts in enumerate(q011ae.OVERLAP_COUNTS):
        target_histogram = Counter(
            q011z._identifier_indices(identifier)[0]
            for identifier in target_groups[aggregate_index]
        )
        histogram: Counter[int] = Counter()
        signature_count = 0
        compatible_signature_count = 0
        monomial_count = 0
        compatible_monomial_count = 0
        comparison_count = 0
        pools = []
        for group_index, count in enumerate(counts):
            key = (group_index, count)
            if key not in group_signature_cache:
                group_signature_cache[key] = _group_signature_records(
                    classes, group_index, count
                )
            pools.append(group_signature_cache[key])
        for parts in itertools.product(*pools):
            signature_count += 1
            wave_multiplicities = _combined_wave_multiplicities(parts)
            histogram.update(wave_multiplicities)
            fiber_count = sum(wave_multiplicities.values())
            monomial_count += fiber_count
            active_blocks = [
                block for block in target_histogram if wave_multiplicities[block]
            ]
            if active_blocks:
                compatible_signature_count += 1
            compatible_monomial_count += sum(
                wave_multiplicities[block] for block in active_blocks
            )
            comparison_count += sum(
                wave_multiplicities[block] * target_histogram[block]
                for block in active_blocks
            )
        signature_counts.append(signature_count)
        compatible_signature_counts.append(compatible_signature_count)
        monomial_counts.append(monomial_count)
        compatible_monomial_counts.append(compatible_monomial_count)
        comparison_counts.append(comparison_count)
        histograms.append(
            {str(key): value for key, value in sorted(histogram.items())}
        )

    compact_record = {
        "aggregate_signature_counts": signature_counts,
        "aggregate_compatible_signature_counts": compatible_signature_counts,
        "aggregate_monomial_counts": monomial_counts,
        "aggregate_compatible_monomial_counts": compatible_monomial_counts,
        "aggregate_comparison_counts": comparison_counts,
        "aggregate_wave_histograms": histograms,
    }
    checks = {
        "q011ae_full_stream_artifact_is_accepted": bool(
            artifacts["q011ae"]["scientific_outcome"] == "accepted"
            and prior_sector["passed"]
        ),
        "all_fourteen_monomial_counts_reproduce": (
            monomial_counts == prior_sector["aggregate_monomial_counts"]
        ),
        "all_fourteen_wave_histograms_reproduce": (
            histograms == prior_sector["aggregate_sector_histograms"]
        ),
        "compatible_monomial_counts_reproduce": bool(
            compatible_monomial_counts
            == prior_sector["aggregate_sector_compatible_monomial_counts"]
            and sum(compatible_monomial_counts)
            == prior_sector["sector_compatible_monomial_count"]
            and sum(monomial_counts) - sum(compatible_monomial_counts)
            == prior_sector["sector_incompatible_monomial_count"]
        ),
        "weighted_comparison_counts_reproduce": bool(
            comparison_counts
            == prior_sector["aggregate_compatible_comparison_counts"]
            and sum(comparison_counts)
            == prior_sector["sector_compatible_comparison_count"]
        ),
        "registered_oracle_signature_counts_reproduce": bool(
            tuple(signature_counts) == Q011AE_ORACLE_SIGNATURE_COUNTS
            and tuple(compatible_signature_counts)
            == Q011AE_ORACLE_COMPATIBLE_SIGNATURE_COUNTS
            and sum(signature_counts) == 20_361
            and sum(compatible_signature_counts) == 14_497
        ),
        "oracle_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(compact_record)
            and _strict_json_serializable(compact_record)
            and json.dumps(compact_record, allow_nan=False)
        ),
    }
    return {
        **compact_record,
        "full_stream_monomial_record_count": prior_sector[
            "indexed_monomial_count"
        ],
        "full_stream_comparison_record_count": prior_sector[
            "sector_compatible_comparison_count"
        ],
        "compact_oracle_digest_sha256": q011b._canonical_json_sha256(
            compact_record
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _compressed_sector_product_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
    overlap_records: tuple[dict[str, Any], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> tuple[dict[str, Any], dict[str, Any], Fraction]:
    classes, class_records = _modulus_classes(selected_groups, lookup)
    group_signature_cache: dict[
        tuple[int, int], tuple[tuple[tuple[int, ...], Counter[int]], ...]
    ] = {}
    oracle = _q011ae_compression_oracle_audit(
        artifacts, classes, group_signature_cache
    )
    signature_framer = q011z._FramedRecordDigest(
        "Q011af/degree12-modulus-signature/v1"
    )
    pair_framer = q011z._FramedRecordDigest(
        "Q011af/degree12-compatible-signature-target/v1"
    )
    product_framer = q011z._FramedRecordDigest(
        "Q011af/exact-compressed-modulus-product/v1"
    )
    comparison_framer = q011z._FramedRecordDigest(
        "Q011af/exact-compressed-modulus-comparison/v1"
    )

    target_histograms = [
        Counter(
            q011z._identifier_indices(identifier)[0]
            for identifier in target_group
        )
        for target_group in external_target_groups
    ]
    targets_by_block = []
    for target_group in external_target_groups:
        block_lookup: dict[int, list[str]] = {}
        for identifier in target_group:
            block = q011z._identifier_indices(identifier)[0]
            block_lookup.setdefault(block, []).append(identifier)
        targets_by_block.append(
            {
                block: tuple(identifiers)
                for block, identifiers in block_lookup.items()
            }
        )

    signature_counts: list[int] = []
    compatible_signature_counts: list[int] = []
    monomial_counts: list[int] = []
    compatible_monomial_counts: list[int] = []
    weighted_comparison_counts: list[int] = []
    distinct_comparison_counts: list[int] = []
    sector_histograms: list[Counter[int]] = []
    boundary_records: list[dict[str, Any]] = []
    aggregate_weighted_counts = [Counter() for _ in OVERLAP_COUNTS]
    aggregate_distinct_counts = [Counter() for _ in OVERLAP_COUNTS]
    aggregate_minima: list[Fraction | None] = [None] * len(OVERLAP_COUNTS)
    aggregate_minimum_raw: list[dict[str, Any] | None] = [None] * len(
        OVERLAP_COUNTS
    )
    weighted_relation_counts: Counter[str] = Counter()
    distinct_relation_counts: Counter[str] = Counter()
    minimum_gap: Fraction | None = None
    minimum_raw: dict[str, Any] | None = None
    first_unresolved: dict[str, Any] | None = None
    signature_index = 0
    distinct_comparison_index = 0
    compatible_signature_count = 0
    original_monomial_count = 0
    compatible_monomial_count = 0
    weighted_comparison_count = 0
    weighted_separated_count = 0
    weighted_unresolved_count = 0
    distinct_separated_count = 0
    distinct_unresolved_count = 0
    fiber_multiplicities_exact = True
    radii_nonnegative = True
    intervals_ordered = True

    for aggregate_index, overlap in enumerate(overlap_records):
        counts = tuple(overlap["selected_type_counts"])
        pools = []
        for group_index, count in enumerate(counts):
            key = (group_index, count)
            if key not in group_signature_cache:
                group_signature_cache[key] = _group_signature_records(
                    classes, group_index, count
                )
            pools.append(group_signature_cache[key])
        aggregate_signature_start = signature_index
        aggregate_compatible_signature_start = compatible_signature_count
        aggregate_monomial_start = original_monomial_count
        aggregate_compatible_monomial_start = compatible_monomial_count
        aggregate_weighted_comparison_start = weighted_comparison_count
        aggregate_distinct_comparison_start = distinct_comparison_index
        histogram: Counter[int] = Counter()
        first_signature: dict[str, Any] | None = None
        last_signature: dict[str, Any] | None = None

        for parts in itertools.product(*pools):
            class_counts = tuple(part[0] for part in parts)
            wave_multiplicities = _combined_wave_multiplicities(parts)
            fiber_multiplicity = sum(wave_multiplicities.values())
            expected_fiber_multiplicity = _signature_fiber_multiplicity(
                classes, class_counts
            )
            fiber_multiplicities_exact = bool(
                fiber_multiplicities_exact
                and fiber_multiplicity == expected_fiber_multiplicity
            )
            signature_record = {
                "signature_index": signature_index,
                "aggregate_index": aggregate_index,
                "selected_type_counts": list(counts),
                "source_modulus_class_counts": [
                    list(group_counts) for group_counts in class_counts
                ],
                "wave_multiplicities": {
                    str(key): value
                    for key, value in sorted(wave_multiplicities.items())
                },
                "original_monomial_multiplicity": fiber_multiplicity,
            }
            signature_framer.update(signature_record)
            histogram.update(wave_multiplicities)
            original_monomial_count += fiber_multiplicity
            if first_signature is None:
                first_signature = signature_record
            last_signature = signature_record

            active_blocks = [
                block
                for block in targets_by_block[aggregate_index]
                if wave_multiplicities[block]
            ]
            if active_blocks:
                compatible_signature_count += 1
                compatible_weight = sum(
                    wave_multiplicities[block] for block in active_blocks
                )
                compatible_monomial_count += compatible_weight
                center_lower_product = Fraction(1)
                center_upper_product = Fraction(1)
                full_upper_product = Fraction(1)
                for group_index, group_counts in enumerate(class_counts):
                    for class_count, identifiers in zip(
                        group_counts, classes[group_index], strict=True
                    ):
                        disc = lookup[identifiers[0]]
                        for _ in range(class_count):
                            center_lower_product *= disc.center_modulus.lower
                            center_upper_product *= disc.center_modulus.upper
                            full_upper_product *= (
                                disc.center_modulus.upper
                                + UNIFORM_REFINED_RADIUS
                            )
                product_radius = full_upper_product - center_upper_product
                product_modulus = RationalInterval(
                    max(
                        Fraction(0),
                        center_lower_product - product_radius,
                    ),
                    center_upper_product + product_radius,
                )
                radii_nonnegative = bool(
                    radii_nonnegative and product_radius >= 0
                )
                intervals_ordered = bool(
                    intervals_ordered
                    and 0 <= product_modulus.lower <= product_modulus.upper
                )
                product_framer.update(
                    {
                        "signature_index": signature_index,
                        "aggregate_index": aggregate_index,
                        "source_modulus_class_counts": [
                            list(group_counts)
                            for group_counts in class_counts
                        ],
                        "compatible_monomial_multiplicity": compatible_weight,
                        "center_modulus_lower_product": (
                            q011z._exact_fraction_record(
                                center_lower_product
                            )
                        ),
                        "center_modulus_upper_product": (
                            q011z._exact_fraction_record(
                                center_upper_product
                            )
                        ),
                        "uniform_product_radius": (
                            q011z._exact_fraction_record(product_radius)
                        ),
                        "product_modulus_lower": (
                            q011z._exact_fraction_record(
                                product_modulus.lower
                            )
                        ),
                        "product_modulus_upper": (
                            q011z._exact_fraction_record(
                                product_modulus.upper
                            )
                        ),
                    }
                )
                for output_block in active_blocks:
                    wave_multiplicity = wave_multiplicities[output_block]
                    for target_identifier in targets_by_block[
                        aggregate_index
                    ][output_block]:
                        pair_framer.update(
                            {
                                "distinct_comparison_index": (
                                    distinct_comparison_index
                                ),
                                "signature_index": signature_index,
                                "aggregate_index": aggregate_index,
                                "output_block": output_block,
                                "wave_multiplicity": wave_multiplicity,
                                "target_identifier": target_identifier,
                            }
                        )
                        target = lookup[target_identifier]
                        if product_modulus.upper < target.modulus.lower:
                            gap = (
                                target.modulus.lower
                                - product_modulus.upper
                            )
                            relation = "product_below_target"
                            classification = (
                                "individual_modulus_separation"
                            )
                        elif target.modulus.upper < product_modulus.lower:
                            gap = (
                                product_modulus.lower
                                - target.modulus.upper
                            )
                            relation = "target_below_product"
                            classification = (
                                "individual_modulus_separation"
                            )
                        else:
                            gap = None
                            relation = "overlap"
                            classification = (
                                "unresolved_interval_overlap"
                            )

                        weighted_comparison_count += wave_multiplicity
                        aggregate_weighted_counts[aggregate_index][
                            classification
                        ] += wave_multiplicity
                        aggregate_distinct_counts[aggregate_index][
                            classification
                        ] += 1
                        weighted_relation_counts[relation] += (
                            wave_multiplicity
                        )
                        distinct_relation_counts[relation] += 1
                        weighted_separated_count += (
                            wave_multiplicity if gap is not None else 0
                        )
                        weighted_unresolved_count += (
                            wave_multiplicity if gap is None else 0
                        )
                        distinct_separated_count += int(gap is not None)
                        distinct_unresolved_count += int(gap is None)
                        comparison_framer.update(
                            {
                                "distinct_comparison_index": (
                                    distinct_comparison_index
                                ),
                                "signature_index": signature_index,
                                "aggregate_index": aggregate_index,
                                "output_block": output_block,
                                "wave_multiplicity": wave_multiplicity,
                                "target_identifier": target_identifier,
                                "product_modulus_lower": (
                                    q011z._exact_fraction_record(
                                        product_modulus.lower
                                    )
                                ),
                                "product_modulus_upper": (
                                    q011z._exact_fraction_record(
                                        product_modulus.upper
                                    )
                                ),
                                "target_modulus_lower": (
                                    q011z._exact_fraction_record(
                                        target.modulus.lower
                                    )
                                ),
                                "target_modulus_upper": (
                                    q011z._exact_fraction_record(
                                        target.modulus.upper
                                    )
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
                        raw = {
                            "aggregate_index": aggregate_index,
                            "selected_type_counts": list(counts),
                            "source_modulus_class_counts": class_counts,
                            "output_block": output_block,
                            "wave_multiplicity": wave_multiplicity,
                            "target_identifier": target_identifier,
                            "individual_modulus_relation": relation,
                            "modulus_gap": gap,
                        }
                        if gap is None:
                            if first_unresolved is None:
                                first_unresolved = raw
                        else:
                            if minimum_gap is None or gap < minimum_gap:
                                minimum_gap = gap
                                minimum_raw = raw
                            if (
                                aggregate_minima[aggregate_index] is None
                                or gap
                                < aggregate_minima[aggregate_index]
                            ):
                                aggregate_minima[aggregate_index] = gap
                                aggregate_minimum_raw[aggregate_index] = raw
                        distinct_comparison_index += 1
            signature_index += 1

        if first_signature is None or last_signature is None:
            raise RuntimeError("Q011af encountered an empty overlap aggregate")
        signature_counts.append(signature_index - aggregate_signature_start)
        compatible_signature_counts.append(
            compatible_signature_count
            - aggregate_compatible_signature_start
        )
        monomial_counts.append(
            original_monomial_count - aggregate_monomial_start
        )
        compatible_monomial_counts.append(
            compatible_monomial_count
            - aggregate_compatible_monomial_start
        )
        weighted_comparison_counts.append(
            weighted_comparison_count
            - aggregate_weighted_comparison_start
        )
        distinct_comparison_counts.append(
            distinct_comparison_index
            - aggregate_distinct_comparison_start
        )
        sector_histograms.append(histogram)
        boundary_records.append(
            {
                "aggregate_index": aggregate_index,
                "first_signature": first_signature,
                "last_signature": last_signature,
            }
        )

    if minimum_gap is None or minimum_raw is None:
        raise RuntimeError("Q011af has no separated compressed comparison")

    def completed_witness(raw: dict[str, Any]) -> dict[str, Any]:
        source_identifiers = _source_witness_for_signature(
            classes,
            raw["source_modulus_class_counts"],
            raw["output_block"],
        )
        return {
            "aggregate_index": raw["aggregate_index"],
            "selected_type_counts": raw["selected_type_counts"],
            "source_modulus_class_counts": [
                list(counts)
                for counts in raw["source_modulus_class_counts"]
            ],
            "source_identifiers": list(source_identifiers),
            "output_block": raw["output_block"],
            "wave_multiplicity": raw["wave_multiplicity"],
            "target_identifier": raw["target_identifier"],
            "individual_modulus_relation": raw[
                "individual_modulus_relation"
            ],
            "modulus_gap": _fraction_record(raw["modulus_gap"]),
        }

    minimum_witness = completed_witness(minimum_raw)
    aggregate_witnesses = [
        None if raw is None else completed_witness(raw)
        for raw in aggregate_minimum_raw
    ]
    unresolved_witness = (
        None
        if first_unresolved is None
        else {
            key: (
                [list(counts) for counts in value]
                if key == "source_modulus_class_counts"
                else value
            )
            for key, value in first_unresolved.items()
            if key != "modulus_gap"
        }
    )

    x_sector = artifacts["q011x"]["cycle"]["fourier_output_sector_audit"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    structural_wave_sum = bool(
        x_sector["passed"]
        and all(x_sector["structural_proof"].values())
        and u_theorem[
            "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
        ]
    )
    class_membership_digest = q011b._canonical_json_sha256(class_records)
    serialized_histograms = [
        {str(key): value for key, value in sorted(histogram.items())}
        for histogram in sector_histograms
    ]
    histogram_digest = q011b._canonical_json_sha256(
        serialized_histograms
    )
    target_serialized_histograms = [
        {str(key): value for key, value in sorted(histogram.items())}
        for histogram in target_histograms
    ]
    streaming_contract = {
        "algorithm": (
            "single pass over exact modulus-class count signatures; "
            "Fourier coefficients store original-monomial fiber "
            "multiplicities and only current combined signature, current "
            "product, compact histograms, boundaries, extrema, witnesses "
            "and four digest states are retained"
        ),
        "full_original_monomial_record_list_retained": False,
        "full_combined_signature_record_list_retained": False,
        "full_distinct_pair_record_list_retained": False,
        "full_product_record_list_retained": False,
        "full_comparison_record_list_retained": False,
        "peak_live_combined_signature_record_count": 1,
        "peak_live_product_record_count": 1,
        "retained_boundary_record_count": len(boundary_records) * 2,
        "group_signature_cache_record_count": sum(
            len(records) for records in group_signature_cache.values()
        ),
    }
    compression_compact_record = {
        "class_records": class_records,
        "boundary_records": boundary_records,
        "aggregate_signature_counts": signature_counts,
        "aggregate_compatible_signature_counts": (
            compatible_signature_counts
        ),
        "aggregate_monomial_counts": monomial_counts,
        "aggregate_compatible_monomial_counts": (
            compatible_monomial_counts
        ),
        "aggregate_weighted_comparison_counts": (
            weighted_comparison_counts
        ),
        "aggregate_distinct_comparison_counts": (
            distinct_comparison_counts
        ),
        "aggregate_wave_histograms": serialized_histograms,
        "target_wave_histograms": target_serialized_histograms,
        "class_membership_digest": class_membership_digest,
        "wave_histogram_digest": histogram_digest,
        "signature_digest": signature_framer.hexdigest(),
        "pair_digest": pair_framer.hexdigest(),
        "streaming_contract": streaming_contract,
        "q011ae_oracle_digest": oracle[
            "compact_oracle_digest_sha256"
        ],
    }
    compression_checks = {
        "translation_equivariance_and_c91_regular_map_give_duodecic_wave_sum": (
            structural_wave_sum
        ),
        "selected_groups_partition_into_registered_modulus_classes": bool(
            tuple(len(group_classes) for group_classes in classes)
            == EXPECTED_MODULUS_CLASS_COUNTS
            and all(
                tuple(
                    sorted(
                        identifier
                        for identifiers in group_classes
                        for identifier in identifiers
                    )
                )
                == selected_groups[group_index]
                for group_index, group_classes in enumerate(classes)
            )
            and class_membership_digest
            == EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "weak_compositions_give_exact_disjoint_fiber_multiplicities": bool(
            fiber_multiplicities_exact
            and tuple(signature_counts) == EXPECTED_SIGNATURE_COUNTS
            and all(
                signature_count
                == prod(
                    comb(
                        source_count + len(classes[group_index]) - 1,
                        len(classes[group_index]) - 1,
                    )
                    for group_index, source_count in enumerate(counts)
                )
                for counts, signature_count in zip(
                    OVERLAP_COUNTS, signature_counts, strict=True
                )
            )
        ),
        "all_original_monomial_counts_reproduce": bool(
            tuple(monomial_counts) == EXPECTED_MONOMIAL_COUNTS
            and original_monomial_count
            == EXPECTED_INDEXED_MONOMIAL_COUNT
            and all(
                count
                == q011z._monomial_count_for_counts(
                    selected_groups, counts
                )
                for count, counts in zip(
                    monomial_counts, OVERLAP_COUNTS, strict=True
                )
            )
        ),
        "registered_wave_histogram_digest_reproduces": bool(
            histogram_digest == EXPECTED_WAVE_HISTOGRAM_DIGEST
            and all(
                sum(histogram.values()) == monomial_counts[index]
                for index, histogram in enumerate(sector_histograms)
            )
        ),
        "compatible_signature_and_monomial_counts_reproduce": bool(
            tuple(compatible_signature_counts)
            == EXPECTED_COMPATIBLE_SIGNATURE_COUNTS
            and compatible_signature_count
            == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and tuple(compatible_monomial_counts)
            == EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
            and compatible_monomial_count
            == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and original_monomial_count - compatible_monomial_count
            == EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT
        ),
        "weighted_and_distinct_comparison_counts_reproduce": bool(
            tuple(weighted_comparison_counts)
            == EXPECTED_WEIGHTED_COMPARISON_COUNTS
            and weighted_comparison_count
            == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and tuple(distinct_comparison_counts)
            == EXPECTED_DISTINCT_COMPARISON_COUNTS
            and distinct_comparison_index
            == EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
        "q011ae_full_stream_oracle_reproduces_exactly": oracle["passed"],
        "registered_signature_stream_digest_reproduces": bool(
            signature_framer.count == EXPECTED_SIGNATURE_COUNT
            and signature_framer.hexdigest()
            == EXPECTED_SIGNATURE_RECORD_DIGEST
            and pair_framer.count
            == EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
        "compressed_streaming_contract_is_observed": bool(
            not streaming_contract[
                "full_original_monomial_record_list_retained"
            ]
            and not streaming_contract[
                "full_combined_signature_record_list_retained"
            ]
            and streaming_contract[
                "peak_live_combined_signature_record_count"
            ]
            == 1
        ),
        "compression_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(compression_compact_record)
            and _strict_json_serializable(compression_compact_record)
            and json.dumps(
                compression_compact_record, allow_nan=False
            )
        ),
    }
    compression_audit = {
        "compression_identity": {
            "modulus_class_definition": (
                "identical exact center-modulus interval within one "
                "selected source group"
            ),
            "fiber_coordinates": (
                "per-class counts plus exact cyclic Fourier "
                "multiplicity polynomial"
            ),
            "fiber_cardinality": (
                "coefficient sum equals the number of per-identifier "
                "weak compositions"
            ),
            "proof_implication": (
                "one strict signature-target interval separation "
                "covers every original monomial in that positive-"
                "multiplicity Fourier fiber"
            ),
        },
        "structural_proof": {
            "q011x_translation_equivariant_wave_sum_is_preserved": bool(
                x_sector["passed"]
                and all(x_sector["structural_proof"].values())
            ),
            "q011u_c91_regular_original_map_is_preserved": u_theorem[
                "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
            ],
            "twelve_fourier_characters_multiply_to_the_sum_character": True,
            "translation_equivariance_applies_at_duodecic_order": (
                structural_wave_sum
            ),
            "weak_composition_fibers_are_disjoint_and_exhaustive": (
                fiber_multiplicities_exact
            ),
        },
        "selected_modulus_class_counts": [
            len(group_classes) for group_classes in classes
        ],
        "selected_modulus_class_records": class_records,
        "class_membership_digest_sha256": class_membership_digest,
        "original_monomial_count": original_monomial_count,
        "aggregate_original_monomial_counts": monomial_counts,
        "modulus_signature_count": signature_index,
        "aggregate_modulus_signature_counts": signature_counts,
        "compatible_modulus_signature_count": (
            compatible_signature_count
        ),
        "aggregate_compatible_modulus_signature_counts": (
            compatible_signature_counts
        ),
        "compatible_original_monomial_count": (
            compatible_monomial_count
        ),
        "incompatible_original_monomial_count": (
            original_monomial_count - compatible_monomial_count
        ),
        "aggregate_compatible_original_monomial_counts": (
            compatible_monomial_counts
        ),
        "weighted_comparison_count": weighted_comparison_count,
        "aggregate_weighted_comparison_counts": (
            weighted_comparison_counts
        ),
        "distinct_comparison_count": distinct_comparison_index,
        "aggregate_distinct_comparison_counts": (
            distinct_comparison_counts
        ),
        "aggregate_wave_histograms": serialized_histograms,
        "aggregate_wave_histogram_digest_sha256": histogram_digest,
        "external_target_counts": [
            len(group) for group in external_target_groups
        ],
        "external_target_wave_histograms": (
            target_serialized_histograms
        ),
        "boundary_records": boundary_records,
        "q011ae_full_stream_compression_oracle": oracle,
        "streaming_contract": streaming_contract,
        "framed_exact_record_digests": {
            "algorithm": (
                "SHA-256 over domain and ordered records, each framed "
                "by an unsigned 8-byte big-endian UTF-8 "
                "canonical-JSON byte length"
            ),
            "signature_record_count": signature_framer.count,
            "signature_record_digest_sha256": (
                signature_framer.hexdigest()
            ),
            "distinct_pair_record_count": pair_framer.count,
            "distinct_pair_record_digest_sha256": (
                pair_framer.hexdigest()
            ),
        },
        "compact_compression_digest_sha256": (
            q011b._canonical_json_sha256(compression_compact_record)
        ),
        "checks": compression_checks,
        "passed": all(compression_checks.values()),
    }

    expected_global_source = [
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=1;center=151",
        "block=0;center=149",
        "block=1;center=152",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
    ]
    product_compact_record = {
        "aggregate_counts": [
            {
                "aggregate_index": index,
                "selected_type_counts": list(OVERLAP_COUNTS[index]),
                "external_group_index": EXTERNAL_GROUP_INDICES[index],
                "weighted_individual_modulus_separation_count": counts[
                    "individual_modulus_separation"
                ],
                "weighted_unresolved_interval_overlap_count": counts[
                    "unresolved_interval_overlap"
                ],
                "distinct_individual_modulus_separation_count": (
                    aggregate_distinct_counts[index][
                        "individual_modulus_separation"
                    ]
                ),
                "distinct_unresolved_interval_overlap_count": (
                    aggregate_distinct_counts[index][
                        "unresolved_interval_overlap"
                    ]
                ),
            }
            for index, counts in enumerate(aggregate_weighted_counts)
        ],
        "weighted_relation_counts": dict(
            sorted(weighted_relation_counts.items())
        ),
        "distinct_relation_counts": dict(
            sorted(distinct_relation_counts.items())
        ),
        "aggregate_minimum_gap_witnesses": aggregate_witnesses,
        "global_minimum_gap_witness": minimum_witness,
        "first_unresolved": unresolved_witness,
        "product_digest": product_framer.hexdigest(),
        "comparison_digest": comparison_framer.hexdigest(),
        "streaming_contract": streaming_contract,
    }
    product_checks = {
        "all_184154_and_only_compatible_signature_products_are_reconstructed": bool(
            product_framer.count
            == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and product_framer.count == compatible_signature_count
            and radii_nonnegative
            and intervals_ordered
        ),
        "uniform_triangle_inequality_product_formula_is_applied": bool(
            radii_nonnegative and intervals_ordered
        ),
        "all_1116256_distinct_comparisons_are_evaluated": bool(
            comparison_framer.count
            == EXPECTED_DISTINCT_COMPARISON_COUNT
            and pair_framer.count
            == EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
        "distinct_and_weighted_categories_partition_all_records": bool(
            distinct_separated_count + distinct_unresolved_count
            == EXPECTED_DISTINCT_COMPARISON_COUNT
            and weighted_separated_count + weighted_unresolved_count
            == EXPECTED_WEIGHTED_COMPARISON_COUNT
        ),
        "registered_weighted_relations_reproduce": bool(
            dict(weighted_relation_counts)
            == {
                "product_below_target": 7_676_904,
                "target_below_product": 6_304_056,
            }
            and dict(distinct_relation_counts)
            == {
                "product_below_target": 648_656,
                "target_below_product": 467_600,
            }
        ),
        "minimum_gap_and_witness_reproduce": bool(
            minimum_witness["aggregate_index"] == 3
            and minimum_witness["selected_type_counts"]
            == [0, 6, 2, 4]
            and minimum_witness["source_identifiers"]
            == expected_global_source
            and minimum_witness["output_block"] == 14
            and minimum_witness["target_identifier"]
            == "block=14;center=146"
            and minimum_witness["individual_modulus_relation"]
            == "product_below_target"
        ),
        "framed_product_record_counts_and_sha256_shapes_reproduce": bool(
            product_framer.count
            == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and comparison_framer.count
            == EXPECTED_DISTINCT_COMPARISON_COUNT
            and len(product_framer.hexdigest()) == 64
            and len(comparison_framer.hexdigest()) == 64
        ),
        "compressed_streaming_contract_is_observed": bool(
            not streaming_contract["full_product_record_list_retained"]
            and not streaming_contract[
                "full_comparison_record_list_retained"
            ]
            and streaming_contract[
                "peak_live_product_record_count"
            ]
            == 1
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
                "R=product_i(u_i+rho)-product_i(u_i), i=1..12"
            ),
            "product_interval": (
                "[max(0,product_i ell_i-R),product_i u_i+R]"
            ),
            "target_interval": "[max(0,ell_e-rho),u_e+rho]",
        },
        "compressed_product_record_count": product_framer.count,
        "distinct_comparison_record_count": comparison_framer.count,
        "weighted_comparison_count": weighted_comparison_count,
        "weighted_individual_modulus_separation_count": (
            weighted_separated_count
        ),
        "weighted_unresolved_interval_overlap_count": (
            weighted_unresolved_count
        ),
        "distinct_individual_modulus_separation_count": (
            distinct_separated_count
        ),
        "distinct_unresolved_interval_overlap_count": (
            distinct_unresolved_count
        ),
        "weighted_individual_modulus_relation_counts": dict(
            sorted(weighted_relation_counts.items())
        ),
        "distinct_individual_modulus_relation_counts": dict(
            sorted(distinct_relation_counts.items())
        ),
        "aggregate_category_counts": product_compact_record[
            "aggregate_counts"
        ],
        "aggregate_minimum_modulus_gaps": [
            _fraction_record(value) if value is not None else None
            for value in aggregate_minima
        ],
        "aggregate_minimum_gap_witnesses": aggregate_witnesses,
        "minimum_modulus_gap": _fraction_record(minimum_gap),
        "registered_minimum_modulus_gap": _fraction_record(
            MINIMUM_MODULUS_GAP
        ),
        "minimum_gap_witness": minimum_witness,
        "first_unresolved_interval_overlap": unresolved_witness,
        "streaming_contract": streaming_contract,
        "framed_exact_record_digests": {
            "algorithm": (
                "SHA-256 over domain and ordered records, each framed "
                "by an unsigned 8-byte big-endian UTF-8 "
                "canonical-JSON byte length"
            ),
            "exact_product_record_count": product_framer.count,
            "exact_product_record_digest_sha256": (
                product_framer.hexdigest()
            ),
            "exact_comparison_record_count": comparison_framer.count,
            "exact_comparison_record_digest_sha256": (
                comparison_framer.hexdigest()
            ),
        },
        "compact_product_digest_sha256": q011b._canonical_json_sha256(
            product_compact_record
        ),
        "checks": product_checks,
        "passed": all(product_checks.values()),
    }
    return compression_audit, product_audit, minimum_gap

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
        "selected_modulus_class_counts": list(EXPECTED_MODULUS_CLASS_COUNTS),
        "aggregate_monomial_counts": list(EXPECTED_MONOMIAL_COUNTS),
        "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
        "aggregate_modulus_signature_counts": list(EXPECTED_SIGNATURE_COUNTS),
        "modulus_signature_count": EXPECTED_SIGNATURE_COUNT,
        "aggregate_compatible_modulus_signature_counts": list(
            EXPECTED_COMPATIBLE_SIGNATURE_COUNTS
        ),
        "compatible_modulus_signature_count": (
            EXPECTED_COMPATIBLE_SIGNATURE_COUNT
        ),
        "aggregate_compatible_original_monomial_counts": list(
            EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
        ),
        "compatible_original_monomial_count": (
            EXPECTED_COMPATIBLE_MONOMIAL_COUNT
        ),
        "incompatible_original_monomial_count": (
            EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT
        ),
        "aggregate_weighted_comparison_counts": list(
            EXPECTED_WEIGHTED_COMPARISON_COUNTS
        ),
        "weighted_comparison_count": EXPECTED_WEIGHTED_COMPARISON_COUNT,
        "aggregate_distinct_comparison_counts": list(
            EXPECTED_DISTINCT_COMPARISON_COUNTS
        ),
        "distinct_comparison_count": EXPECTED_DISTINCT_COMPARISON_COUNT,
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
        "compression_digest_sha256": cycle["compression_digest_sha256"],
        "product_digest_sha256": cycle["product_digest_sha256"],
    }


def run_degree12_refined_modulus_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = (
        _inventory_audit(artifacts)
    )
    envelope, lookup = _uniform_envelope_audit(
        artifacts, selected_groups, external_target_groups
    )
    compression, product, minimum_gap = (
        _compressed_sector_product_audit(
            artifacts,
            selected_groups,
            external_target_groups,
            overlap_records,
            lookup,
        )
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    inventory_sections = {
        "degree12_modulus_inventory_audit": inventory,
        "uniform_refined_envelope_audit": envelope,
    }
    compression_sections = {
        "multiplicity_compression_audit": compression
    }
    product_sections = {
        "compressed_indexed_modulus_product_audit": product
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(
        inventory_sections
    )
    compression_digest = q011b._canonical_json_sha256(
        compression_sections
    )
    product_digest = q011b._canonical_json_sha256(product_sections)
    strict_payload = {
        **input_sections,
        **inventory_sections,
        **compression_sections,
        **product_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and inventory_digest
        == q011b._canonical_json_sha256(inventory_sections)
        and compression_digest
        == q011b._canonical_json_sha256(compression_sections)
        and product_digest
        == q011b._canonical_json_sha256(product_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    oracle = compression["q011ae_full_stream_compression_oracle"]
    validity_gates = {
        "ten_artifacts_fifty_three_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad/ae artifacts, runners, "
                "53 digests, outcomes, claim boundaries and Q011l/o "
                "sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_twelve_inventory_and_twenty_nine_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "455 aggregates, 6188 controls, 426 separated and "
                "twenty-nine registered overlaps"
            ),
            "value": inventory["checks"],
        },
        "uniform_radius_containment_and_92_monotone_moduli_reproduce": {
            "passed": envelope["passed"],
            "threshold": (
                "theta_b <= rho=5e-8 <= every old Q011k radius, 60 "
                "directly relevant intervals, a 92-record monotone "
                "envelope and exact preservation of all 84 Q011ae "
                "records"
            ),
            "value": envelope["checks"],
        },
        "modulus_classes_weak_compositions_and_q011ae_oracle_reproduce": {
            "passed": bool(
                oracle["passed"]
                and compression["checks"][
                    "selected_groups_partition_into_registered_modulus_classes"
                ]
                and compression["checks"][
                    "weak_compositions_give_exact_disjoint_fiber_multiplicities"
                ]
            ),
            "threshold": (
                "4/2/3/6 exact modulus classes, disjoint weak-"
                "composition fibers and the Q011ae full-stream oracle "
                "reproduce"
            ),
            "value": {
                "class_counts": compression[
                    "selected_modulus_class_counts"
                ],
                "oracle_checks": oracle["checks"],
            },
        },
        "all_original_monomials_signatures_histograms_and_weights_reproduce": {
            "passed": compression["passed"],
            "threshold": (
                "36596091 original monomials, 213618 signatures, "
                "registered wave histogram, 6904665 compatible "
                "multiplicity and weighted/distinct comparison counts "
                "reproduce"
            ),
            "value": compression["checks"],
        },
        "all_compressed_products_comparisons_and_strict_gaps_reproduce": {
            "passed": product["passed"],
            "threshold": (
                "184154 product signatures and 1116256 distinct "
                "comparisons represent all 13980960 weighted "
                "comparisons with strict gaps"
            ),
            "value": product["checks"],
        },
        "old_separations_and_compressed_audits_cover_all_455_aggregates": {
            "passed": bool(
                inventory["passed"]
                and compression["passed"]
                and product["passed"]
                and inventory["old_modulus_separated_aggregate_count"]
                + len(inventory["overlap_records"])
                == EXPECTED_DEGREE_AGGREGATE_COUNT
            ),
            "threshold": (
                "426 old-separated plus twenty-nine multiplicity-"
                "compressed full audits cover all 455 aggregates"
            ),
            "value": {
                "old_separated": inventory[
                    "old_modulus_separated_aggregate_count"
                ],
                "compressed_overlap_audits": len(
                    inventory["overlap_records"]
                ),
            },
        },
        "strict_serialization_section_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite compact strict JSON, four section digests, "
                "result digest and runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )
    complete_coverage = bool(
        inventory["passed"]
        and inventory["degree_modulus_aggregate_count"]
        == EXPECTED_DEGREE_AGGREGATE_COUNT
        and inventory["old_modulus_separated_aggregate_count"]
        == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
        and inventory["old_modulus_overlap_aggregate_count"]
        == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        and compression["original_monomial_count"]
        == EXPECTED_INDEXED_MONOMIAL_COUNT
        and compression["modulus_signature_count"]
        == EXPECTED_SIGNATURE_COUNT
        and compression["compatible_modulus_signature_count"]
        == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
        and compression["compatible_original_monomial_count"]
        == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
        and compression["weighted_comparison_count"]
        == EXPECTED_WEIGHTED_COMPARISON_COUNT
        and compression["distinct_comparison_count"]
        == EXPECTED_DISTINCT_COMPARISON_COUNT
    )
    zero_unresolved = bool(
        product["weighted_unresolved_interval_overlap_count"] == 0
        and product["distinct_unresolved_interval_overlap_count"] == 0
    )
    all_individual = bool(
        product["weighted_individual_modulus_separation_count"]
        == EXPECTED_WEIGHTED_COMPARISON_COUNT
        and product["distinct_individual_modulus_separation_count"]
        == EXPECTED_DISTINCT_COMPARISON_COUNT
    )
    hypothesis_gates = {
        "uniform_envelope_is_spectrally_valid_and_old_disc_contained": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": (
                "all transformed-residual discs subset rho-discs "
                "subset Q011k discs"
            ),
            "value": envelope["checks"],
        },
        "multiplicity_compression_is_exact_and_oracle_validated": {
            "passed": bool(
                validity_passed
                and compression["passed"]
                and oracle["passed"]
                and complete_coverage
            ),
            "threshold": (
                "disjoint modulus-signature fibers exactly cover all "
                "original monomials and reproduce the Q011ae full-"
                "stream oracle"
            ),
            "value": {
                "original_monomials": compression[
                    "original_monomial_count"
                ],
                "signatures": compression["modulus_signature_count"],
                "oracle_passed": oracle["passed"],
            },
        },
        "all_representative_products_have_individual_modulus_separation": {
            "passed": bool(
                validity_passed and zero_unresolved and all_individual
            ),
            "threshold": (
                "1116256 distinct separations cover 13980960 weighted "
                "comparisons with zero unresolved interval overlaps"
            ),
            "value": {
                "distinct_individual": product[
                    "distinct_individual_modulus_separation_count"
                ],
                "weighted_individual": product[
                    "weighted_individual_modulus_separation_count"
                ],
                "distinct_unresolved": product[
                    "distinct_unresolved_interval_overlap_count"
                ],
                "weighted_unresolved": product[
                    "weighted_unresolved_interval_overlap_count"
                ],
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
        "degree_twelve_external_nonresonance_follows_from_complete_partition": {
            "passed": bool(
                validity_passed
                and complete_coverage
                and zero_unresolved
                and all_individual
            ),
            "threshold": (
                "426 old separations and twenty-nine exact "
                "multiplicity-compressed product audits imply "
                "degree-12 external nonresonance"
            ),
            "value": {
                "preserved_old_separations": inventory[
                    "old_modulus_separated_aggregate_count"
                ],
                "compressed_overlap_aggregates": len(
                    inventory["overlap_records"]
                ),
            },
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q011af degree-twelve multiplicity-compressed "
            "audit is invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Does exact Fourier-multiplicity compression plus the "
            "contained uniform refined envelope give strict indexed-"
            "modulus separation for all twenty-nine degree-twelve "
            "overlap aggregates?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "inventory_digest_sha256": inventory_digest,
        "compression_digest_sha256": compression_digest,
        "product_digest_sha256": product_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name
            for name, gate in hypothesis_gates.items()
            if not gate["passed"]
        ],
        "study_validity": (
            "passed" if validity_passed else "failed"
        ),
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    degree_twelve_certified = bool(
        validity_passed and hypotheses_passed
    )
    cycle["theorem_consequence"] = {
        "uniform_transformed_residual_envelope_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "multiplicity_compression_is_exact_and_oracle_validated": bool(
            degree_twelve_certified and oracle["passed"]
        ),
        "all_twenty_nine_degree_twelve_old_modulus_overlaps_are_eliminated": (
            degree_twelve_certified
        ),
        "degree_twelve_external_nonresonance_is_certified": (
            degree_twelve_certified
        ),
        "certified_external_nonresonance_degrees": (
            list(range(2, 13))
            if degree_twelve_certified
            else list(range(2, 12))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(
            range(13 if degree_twelve_certified else 12, 91)
        ),
        "degrees_13_through_90_are_certified": False,
        "complex_phase_was_required_for_degree_twelve": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011ae_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree twelve for the fixed 17x17 "
        "repaired exact map on one fixed conservation leaf, the twenty-"
        "nine Q011u modulus-overlap aggregates, the Q011y transformed-"
        "residual enclosure, the uniform rho=5e-8 discs, exact "
        "x-Fourier multiplicity polynomials, exact modulus-class "
        "fibers and the indexed-modulus product formula. It certifies "
        "no degree from 13 through 90, no all-order nonresonance, "
        "equality with the Q011t graph, C2 or higher graph smoothness, "
        "SSM existence or uniqueness, normal attraction, basin, other "
        "grid, force, wall or D3Q27 result."
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
        "q011ae_degree_eleven_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011ag to audit degree 13 with the same exact "
            "Fourier-multiplicity compression."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Send only the first unresolved degree-twelve compressed "
            "signature product to an exact complex phase-sensitive "
            "product-disc comparison."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, envelope, "
            "compression-oracle, product, coverage or serialization "
            "validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(
            _result_digest_sections(cycle)
        )
    ):
        raise RuntimeError(
            "Q011af cycle failed strict serialization or digest"
        )
    return cycle

def run_q011af_study() -> dict[str, Any]:
    cycle = run_degree12_refined_modulus_audit()
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
            "original_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
            "modulus_signature_count": EXPECTED_SIGNATURE_COUNT,
            "compressed_product_signature_count": (
                EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            ),
            "weighted_comparison_count": (
                EXPECTED_WEIGHTED_COMPARISON_COUNT
            ),
            "distinct_comparison_count": (
                EXPECTED_DISTINCT_COMPARISON_COUNT
            ),
            "exact_record_storage": (
                "four framed SHA-256 streams plus compact histograms, "
                "boundaries, extrema and witnesses"
            ),
        },
        "mathematical_scope": {
            "diagnostic": (
                "degree-twelve exact Fourier-multiplicity compressed "
                "refined-envelope indexed-modulus products"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_twelve_external_nonresonance_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "degrees_13_through_90_claim": False,
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
    result = run_q011af_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
