"""Q011aa degree-seven uniform refined-envelope indexed-modulus certificate."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

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
DEGREE = 7
EXPECTED_DEGREE_AGGREGATE_COUNT = 120
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 792
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 115
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 5
OVERLAP_COUNTS = (
    (0, 1, 1, 5),
    (0, 1, 2, 4),
    (0, 2, 0, 5),
    (0, 2, 1, 4),
    (0, 2, 2, 3),
)
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXTERNAL_GROUP_INDICES = (178, 178, 177, 177, 177)
EXPECTED_EXTERNAL_TARGET_COUNTS = (4, 4, 8, 8, 8)
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 12
EXPECTED_MONOMIAL_COUNTS = (12672, 13200, 7920, 13200, 12000)
EXPECTED_INDEXED_MONOMIAL_COUNT = 58992
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 16878
EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT = 42114
EXPECTED_SECTOR_HISTOGRAMS = (
    {
        0: 2192,
        1: 2008,
        2: 1520,
        3: 944,
        4: 488,
        5: 204,
        6: 64,
        7: 12,
        10: 12,
        11: 64,
        12: 204,
        13: 488,
        14: 944,
        15: 1520,
        16: 2008,
    },
    {
        0: 2320,
        1: 2138,
        2: 1588,
        3: 982,
        4: 480,
        5: 190,
        6: 52,
        7: 10,
        10: 10,
        11: 52,
        12: 190,
        13: 480,
        14: 982,
        15: 1588,
        16: 2138,
    },
    {
        0: 1240,
        1: 1144,
        2: 944,
        3: 644,
        4: 356,
        5: 174,
        6: 60,
        7: 18,
        10: 18,
        11: 60,
        12: 174,
        13: 356,
        14: 644,
        15: 944,
        16: 1144,
    },
    {
        0: 2120,
        1: 1975,
        2: 1590,
        3: 1065,
        4: 572,
        5: 245,
        6: 78,
        7: 15,
        10: 15,
        11: 78,
        12: 245,
        13: 572,
        14: 1065,
        15: 1590,
        16: 1975,
    },
    {
        0: 1952,
        1: 1808,
        2: 1452,
        3: 966,
        4: 512,
        5: 214,
        6: 60,
        7: 12,
        10: 12,
        11: 60,
        12: 214,
        13: 512,
        14: 966,
        15: 1452,
        16: 1808,
    },
)
EXPECTED_TARGET_SECTOR_HISTOGRAMS = (
    {2: 2, 15: 2},
    {2: 2, 15: 2},
    {0: 4, 3: 2, 14: 2},
    {0: 4, 3: 2, 14: 2},
    {0: 4, 3: 2, 14: 2},
)
EXPECTED_COMPARISON_COUNTS = (6080, 6352, 7536, 12740, 11672)
EXPECTED_COMPATIBLE_COMPARISON_COUNT = 44380
UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
MINIMUM_MODULUS_GAP = Fraction(5, 10**6)

Q011Z_ARTIFACT_SHA256 = "bd435ceea3795475f6b17619e13626ba936f8fcbd15da749a39a4e2b034a4e23"
Q011Z_RUNNER_SHA256 = "6e6d7327e4b85b307098203fe882434bf77f3920a1da7323b1c89d118df3ae87"
Q011Z_DIGESTS = (
    "394728b15820900b642776843b96b7383b31fec27bede2274d97ee9c635054bb",
    "46248ce31e7e04039eb9eb1788d42f04d19dd949b026a921e61812ab3d37e8cc",
    "b172439520fa25bba82fa936564ebc0ae51763a57006cb279d1e3fe9f0ed0a3c",
    "148acb302034412498638201703eee8722f90afa093adcf6215094170e4a8c1e",
    "a695e5c632e6dda8114377f33824ca6b234ebadae7c25d6b8aa1c3d3774c4aff",
)
Q011Z_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "sector_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)

ACCEPTED_CLASSIFICATION = (
    "degree-7 external nonresonance is certified by the contained uniform "
    "transformed-residual envelope and exact Fourier-sector indexed-modulus products"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-7 refined indexed-modulus product remains "
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
    prior_audit, artifacts = q011z._sealed_input_audit()
    directory = _artifact_directory()
    artifact_path = directory / "q011z_degree6_refined_modulus.json"
    runner_path = Path(q011z.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digest_tuple = q011z._digest_tuple(cycle, Q011Z_DIGEST_NAMES)
    checks = {
        "q011z_four_prior_artifacts_and_helpers_reproduce": bool(
            prior_audit["passed"]
            and prior_audit["direct_digest_count"] == 23
            and all(prior_audit["checks"].values())
        ),
        "q011z_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011Z_ARTIFACT_SHA256),
        "q011z_runner_sha256_matches": (
            _file_sha256(runner_path) == Q011Z_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011Z_RUNNER_SHA256
        ),
        "q011z_digests_match": digest_tuple == Q011Z_DIGESTS,
        "q011z_registered_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["scientific_classification"] == q011z.ACCEPTED_CLASSIFICATION
        ),
        "q011z_degree_six_scope_is_preserved": bool(
            cycle["theorem_consequence"]["degree_six_external_nonresonance_is_certified"]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == [2, 3, 4, 5, 6]
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(7, 91))
            and not cycle["theorem_consequence"]["ssm_existence_or_uniqueness_is_certified"]
        ),
        "q011z_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011z_package_source_metadata_matches": (artifact["source"] == source_metadata()),
        "q011z_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "twenty_eight_direct_digests_are_sealed": bool(
            prior_audit["direct_digest_count"] + len(digest_tuple) == 28
        ),
    }
    artifacts["q011z"] = artifact
    audit = {
        "prior_q011z_sealed_input_audit": prior_audit,
        "q011z": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011Z_DIGEST_NAMES),
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
        "q011u_degree_seven_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_five_overlap_tuples_and_external_groups_reproduce": bool(
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
        "old_degree_six_certificate_is_preserved": artifacts["q011z"]["cycle"][
            "theorem_consequence"
        ]["degree_six_external_nonresonance_is_certified"],
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
    audit, lookup = q011z._uniform_envelope_audit(
        artifacts, selected_groups, external_target_groups
    )
    active_group_indices = sorted(
        {
            group_index
            for counts in OVERLAP_COUNTS
            for group_index, multiplicity in enumerate(counts)
            if multiplicity > 0
        }
    )
    external_identifiers = set().union(*map(set, external_target_groups))
    selected_identifiers = set().union(
        *(set(selected_groups[index]) for index in active_group_indices)
    )
    checks = {
        **audit["checks"],
        "degree_seven_active_groups_and_relevant_identifiers_reproduce": bool(
            active_group_indices == [1, 2, 3]
            and len(selected_identifiers) == 16
            and len(external_identifiers) == 12
            and selected_identifiers.isdisjoint(external_identifiers)
            and set(lookup) == selected_identifiers | external_identifiers
            and len(lookup) == 28
        ),
        "q011z_uniform_envelope_is_reused_without_widening": bool(
            artifacts["q011z"]["cycle"]["theorem_consequence"][
                "uniform_transformed_residual_envelope_is_certified"
            ]
            and audit["uniform_radius"] == _fraction_record(UNIFORM_REFINED_RADIUS)
            and audit["uniform_record_digest_sha256"]
            == artifacts["q011z"]["cycle"]["uniform_refined_envelope_audit"][
                "uniform_record_digest_sha256"
            ]
        ),
    }
    result = {
        **audit,
        "degree_seven_active_selected_group_indices": active_group_indices,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return result, lookup


def _sector_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
    overlap_records: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[tuple[int, str]]]:
    monomial_framer = q011z._FramedRecordDigest("Q011aa/degree7-monomial/v1")
    pair_framer = q011z._FramedRecordDigest("Q011aa/degree7-compatible-pair/v1")
    monomial_records: list[dict[str, Any]] = []
    monomial_counts = []
    boundary_records = []
    for aggregate_index, overlap in enumerate(overlap_records):
        counts = tuple(overlap["selected_type_counts"])
        choices = [
            tuple(itertools.combinations_with_replacement(group, count))
            for group, count in zip(selected_groups, counts, strict=True)
        ]
        aggregate_start = len(monomial_records)
        for parts in itertools.product(*choices):
            identifiers = tuple(itertools.chain.from_iterable(parts))
            blocks = [q011z._identifier_indices(identifier)[0] for identifier in identifiers]
            record = {
                "monomial_index": len(monomial_records),
                "aggregate_index": aggregate_index,
                "selected_type_counts": list(counts),
                "source_identifiers": list(identifiers),
                "input_blocks": blocks,
                "output_block": sum(blocks) % SIZE,
            }
            monomial_records.append(record)
            monomial_framer.update(record)
        monomial_counts.append(len(monomial_records) - aggregate_start)
        boundary_records.append(
            {
                "aggregate_index": aggregate_index,
                "first_monomial": monomial_records[aggregate_start],
                "last_monomial": monomial_records[-1],
            }
        )

    sector_histograms = [
        Counter(
            record["output_block"]
            for record in monomial_records
            if record["aggregate_index"] == aggregate_index
        )
        for aggregate_index in range(len(overlap_records))
    ]
    target_histograms = [
        Counter(q011z._identifier_indices(identifier)[0] for identifier in target_group)
        for target_group in external_target_groups
    ]
    compatible_pairs: list[tuple[int, str]] = []
    comparison_counts = [0] * len(overlap_records)
    compatible_monomial_indices: set[int] = set()
    for record in monomial_records:
        aggregate_index = record["aggregate_index"]
        for target_identifier in external_target_groups[aggregate_index]:
            if record["output_block"] != q011z._identifier_indices(target_identifier)[0]:
                continue
            pair = (record["monomial_index"], target_identifier)
            compatible_pairs.append(pair)
            pair_framer.update(
                {
                    "comparison_index": len(compatible_pairs) - 1,
                    "monomial_index": pair[0],
                    "aggregate_index": aggregate_index,
                    "target_identifier": target_identifier,
                }
            )
            comparison_counts[aggregate_index] += 1
            compatible_monomial_indices.add(record["monomial_index"])

    x_sector = artifacts["q011x"]["cycle"]["fourier_output_sector_audit"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    structural_wave_sum = bool(
        x_sector["passed"]
        and all(x_sector["structural_proof"].values())
        and u_theorem[
            "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
        ]
    )
    compact_record = {
        "boundary_records": boundary_records,
        "aggregate_sector_histograms": [
            dict(sorted(histogram.items())) for histogram in sector_histograms
        ],
        "target_sector_histograms": [
            dict(sorted(histogram.items())) for histogram in target_histograms
        ],
        "comparison_counts": comparison_counts,
        "compatible_monomial_count": len(compatible_monomial_indices),
        "framed_monomial_digest": monomial_framer.hexdigest(),
        "framed_pair_digest": pair_framer.hexdigest(),
    }
    checks = {
        "translation_equivariance_and_c91_regular_map_give_septic_wave_sum": (structural_wave_sum),
        "combination_with_replacement_counts_reproduce": bool(
            tuple(monomial_counts) == EXPECTED_MONOMIAL_COUNTS
            and all(
                count == q011z._monomial_count_for_counts(selected_groups, counts)
                for count, counts in zip(monomial_counts, OVERLAP_COUNTS, strict=True)
            )
        ),
        "all_58992_and_only_degree_seven_overlap_monomials_are_enumerated": bool(
            len(monomial_records) == EXPECTED_INDEXED_MONOMIAL_COUNT
            and len(
                {
                    (
                        record["aggregate_index"],
                        tuple(record["source_identifiers"]),
                    )
                    for record in monomial_records
                }
            )
            == EXPECTED_INDEXED_MONOMIAL_COUNT
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
            len(compatible_monomial_indices) == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and len(monomial_records) - len(compatible_monomial_indices)
            == EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT
        ),
        "all_44380_and_only_compatible_comparisons_are_enumerated": bool(
            tuple(comparison_counts) == EXPECTED_COMPARISON_COUNTS
            and len(compatible_pairs) == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "framed_record_counts_and_sha256_shapes_reproduce": bool(
            monomial_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
            and pair_framer.count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
            and len(monomial_framer.hexdigest()) == 64
            and len(pair_framer.hexdigest()) == 64
        ),
        "sector_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(compact_record)
            and _strict_json_serializable(compact_record)
            and json.dumps(compact_record, allow_nan=False)
        ),
    }
    audit = {
        "output_sector_law": ("b_out=(b_1+b_2+b_3+b_4+b_5+b_6+b_7) mod 17"),
        "structural_proof": {
            "q011x_translation_equivariant_wave_sum_is_preserved": bool(
                x_sector["passed"] and all(x_sector["structural_proof"].values())
            ),
            "q011u_c91_regular_original_map_is_preserved": u_theorem[
                "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
            ],
            "seven_fourier_characters_multiply_to_the_sum_character": True,
            "translation_equivariance_applies_at_septic_order": (structural_wave_sum),
        },
        "indexed_monomial_count": len(monomial_records),
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
        "sector_compatible_monomial_count": len(compatible_monomial_indices),
        "sector_incompatible_monomial_count": (
            len(monomial_records) - len(compatible_monomial_indices)
        ),
        "aggregate_compatible_comparison_counts": comparison_counts,
        "sector_compatible_comparison_count": len(compatible_pairs),
        "boundary_records": boundary_records,
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
        "compact_sector_digest_sha256": q011b._canonical_json_sha256(compact_record),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, monomial_records, compatible_pairs


def _product_audit(
    lookup: dict[str, q011z._UniformDisc],
    monomial_records: list[dict[str, Any]],
    compatible_pairs: list[tuple[int, str]],
) -> tuple[dict[str, Any], Fraction]:
    product_framer = q011z._FramedRecordDigest("Q011aa/exact-modulus-product/v1")
    comparison_framer = q011z._FramedRecordDigest("Q011aa/exact-modulus-comparison/v1")
    internal_products: list[dict[str, Any]] = []
    radii_nonnegative = True
    intervals_ordered = True
    for monomial in monomial_records:
        discs = [lookup[identifier] for identifier in monomial["source_identifiers"]]
        center_lower_product = Fraction(1)
        center_upper_product = Fraction(1)
        full_upper_product = Fraction(1)
        for disc in discs:
            center_lower_product *= disc.center_modulus.lower
            center_upper_product *= disc.center_modulus.upper
            full_upper_product *= disc.center_modulus.upper + UNIFORM_REFINED_RADIUS
        product_radius = full_upper_product - center_upper_product
        modulus = RationalInterval(
            max(Fraction(0), center_lower_product - product_radius),
            center_upper_product + product_radius,
        )
        radii_nonnegative = radii_nonnegative and product_radius >= 0
        intervals_ordered = intervals_ordered and 0 <= modulus.lower <= modulus.upper
        internal_products.append({"radius": product_radius, "modulus": modulus})
        product_framer.update(
            {
                "monomial_index": monomial["monomial_index"],
                "aggregate_index": monomial["aggregate_index"],
                "center_modulus_lower_product": (
                    q011z._exact_fraction_record(center_lower_product)
                ),
                "center_modulus_upper_product": (
                    q011z._exact_fraction_record(center_upper_product)
                ),
                "uniform_product_radius": q011z._exact_fraction_record(product_radius),
                "product_modulus_lower": q011z._exact_fraction_record(modulus.lower),
                "product_modulus_upper": q011z._exact_fraction_record(modulus.upper),
            }
        )

    separated_count = 0
    unresolved_count = 0
    relation_counts: Counter[str] = Counter()
    aggregate_counts = [Counter() for _ in OVERLAP_COUNTS]
    minimum_gap: Fraction | None = None
    minimum_witness: dict[str, Any] | None = None
    aggregate_minima: list[Fraction | None] = [None] * len(OVERLAP_COUNTS)
    aggregate_witnesses: list[dict[str, Any] | None] = [None] * len(OVERLAP_COUNTS)
    first_unresolved: dict[str, Any] | None = None
    for comparison_index, (
        monomial_index,
        target_identifier,
    ) in enumerate(compatible_pairs):
        monomial = monomial_records[monomial_index]
        product = internal_products[monomial_index]
        target = lookup[target_identifier]
        product_modulus = product["modulus"]
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
        aggregate_index = monomial["aggregate_index"]
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
                "product_modulus_lower": q011z._exact_fraction_record(product_modulus.lower),
                "product_modulus_upper": q011z._exact_fraction_record(product_modulus.upper),
                "target_modulus_lower": q011z._exact_fraction_record(target.modulus.lower),
                "target_modulus_upper": q011z._exact_fraction_record(target.modulus.upper),
                "individual_modulus_relation": relation,
                "modulus_gap": (None if gap is None else q011z._exact_fraction_record(gap)),
                "classification": classification,
            }
        )
        if gap is None:
            if first_unresolved is None:
                first_unresolved = {
                    "aggregate_index": aggregate_index,
                    "selected_type_counts": monomial["selected_type_counts"],
                    "source_identifiers": monomial["source_identifiers"],
                    "output_block": monomial["output_block"],
                    "target_identifier": target_identifier,
                }
            continue
        witness = q011z._minimum_witness(monomial, target_identifier, relation, gap)
        if minimum_gap is None or gap < minimum_gap:
            minimum_gap = gap
            minimum_witness = witness
        if aggregate_minima[aggregate_index] is None or gap < aggregate_minima[aggregate_index]:
            aggregate_minima[aggregate_index] = gap
            aggregate_witnesses[aggregate_index] = witness

    if minimum_gap is None or minimum_witness is None:
        raise RuntimeError("Q011aa has no separated modulus comparison")
    expected_global_source = [
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=152",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
        "block=0;center=147",
    ]
    compact_record = {
        "aggregate_counts": [
            {
                "aggregate_index": index,
                "selected_type_counts": list(OVERLAP_COUNTS[index]),
                "external_group_index": EXTERNAL_GROUP_INDICES[index],
                "individual_modulus_separation_count": counts["individual_modulus_separation"],
                "unresolved_interval_overlap_count": counts["unresolved_interval_overlap"],
            }
            for index, counts in enumerate(aggregate_counts)
        ],
        "relation_counts": dict(sorted(relation_counts.items())),
        "aggregate_minimum_gap_witnesses": aggregate_witnesses,
        "global_minimum_gap_witness": minimum_witness,
        "first_unresolved": first_unresolved,
        "product_digest": product_framer.hexdigest(),
        "comparison_digest": comparison_framer.hexdigest(),
    }
    checks = {
        "all_58992_product_modulus_intervals_are_reconstructed": bool(
            product_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
            and len(internal_products) == EXPECTED_INDEXED_MONOMIAL_COUNT
            and radii_nonnegative
            and intervals_ordered
        ),
        "uniform_triangle_inequality_product_formula_is_applied": bool(
            radii_nonnegative and intervals_ordered
        ),
        "all_44380_compatible_comparisons_are_evaluated": (
            comparison_framer.count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "comparison_categories_partition_all_records": (
            separated_count + unresolved_count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "aggregate_comparison_counts_reproduce": tuple(
            counts["individual_modulus_separation"] + counts["unresolved_interval_overlap"]
            for counts in aggregate_counts
        )
        == EXPECTED_COMPARISON_COUNTS,
        "minimum_gap_and_witness_reproduce": bool(
            minimum_witness["aggregate_index"] == 3
            and minimum_witness["source_identifiers"] == expected_global_source
            and minimum_witness["target_identifier"] == "block=14;center=143"
            and minimum_witness["individual_modulus_relation"] == "product_below_target"
        ),
        "framed_exact_record_counts_and_sha256_shapes_reproduce": bool(
            product_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
            and comparison_framer.count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
            and len(product_framer.hexdigest()) == 64
            and len(comparison_framer.hexdigest()) == 64
        ),
        "compact_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(compact_record)
            and _strict_json_serializable(compact_record)
            and json.dumps(compact_record, allow_nan=False)
        ),
    }
    audit = {
        "uniform_product_modulus_formula": {
            "center_modulus": ("product_i ell_i <= |product_i c_i| <= product_i u_i"),
            "radius": ("R=product_i(u_i+rho)-product_i(u_i), i=1..7"),
            "product_interval": ("[max(0,product_i ell_i-R),product_i u_i+R]"),
            "target_interval": "[max(0,ell_e-rho),u_e+rho]",
        },
        "product_record_count": product_framer.count,
        "comparison_record_count": comparison_framer.count,
        "individual_modulus_separation_count": separated_count,
        "unresolved_interval_overlap_count": unresolved_count,
        "individual_modulus_relation_counts": dict(sorted(relation_counts.items())),
        "aggregate_category_counts": compact_record["aggregate_counts"],
        "aggregate_minimum_modulus_gaps": [
            _fraction_record(value) if value is not None else None for value in aggregate_minima
        ],
        "aggregate_minimum_gap_witnesses": aggregate_witnesses,
        "minimum_modulus_gap": _fraction_record(minimum_gap),
        "registered_minimum_modulus_gap": _fraction_record(MINIMUM_MODULUS_GAP),
        "minimum_gap_witness": minimum_witness,
        "first_unresolved_interval_overlap": first_unresolved,
        "framed_exact_record_digests": {
            "algorithm": (
                "SHA-256 over domain and ordered records, each framed by an "
                "unsigned 8-byte big-endian UTF-8 canonical-JSON byte length"
            ),
            "exact_product_record_count": product_framer.count,
            "exact_product_record_digest_sha256": (product_framer.hexdigest()),
            "exact_comparison_record_count": comparison_framer.count,
            "exact_comparison_record_digest_sha256": (comparison_framer.hexdigest()),
        },
        "compact_product_digest_sha256": q011b._canonical_json_sha256(compact_record),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, minimum_gap


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
        "aggregate_monomial_counts": list(EXPECTED_MONOMIAL_COUNTS),
        "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
        "sector_compatible_monomial_count": (EXPECTED_COMPATIBLE_MONOMIAL_COUNT),
        "sector_incompatible_monomial_count": (EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT),
        "aggregate_compatible_comparison_counts": list(EXPECTED_COMPARISON_COUNTS),
        "compatible_comparison_count": (EXPECTED_COMPATIBLE_COMPARISON_COUNT),
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


def run_degree7_refined_modulus_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = _inventory_audit(
        artifacts
    )
    envelope, lookup = _uniform_envelope_audit(artifacts, selected_groups, external_target_groups)
    sector, monomial_records, compatible_pairs = _sector_audit(
        artifacts,
        selected_groups,
        external_target_groups,
        overlap_records,
    )
    product, minimum_gap = _product_audit(lookup, monomial_records, compatible_pairs)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    inventory_sections = {
        "degree7_modulus_inventory_audit": inventory,
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
    validity_gates = {
        "five_artifacts_twenty_eight_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z artifacts, runners, 28 digests, outcomes, "
                "claim boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_seven_inventory_and_five_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "120 aggregates, 792 controls, 115 separated and five registered overlaps"
            ),
            "value": inventory["checks"],
        },
        "uniform_radius_containment_and_relevant_moduli_reproduce": {
            "passed": envelope["passed"],
            "threshold": (
                "theta_b <= rho=5e-8 <= every old Q011k radius and 28 relevant intervals"
            ),
            "value": envelope["checks"],
        },
        "memberships_monomials_histograms_and_comparisons_reproduce": {
            "passed": sector["passed"],
            "threshold": (
                "8/4/4/8 groups, 58992 monomials, registered septic "
                "histograms and 44380 comparisons"
            ),
            "value": sector["checks"],
        },
        "all_product_target_intervals_and_strict_gaps_reproduce": {
            "passed": product["passed"],
            "threshold": ("58992 exact uniform product intervals and 44380 target comparisons"),
            "value": product["checks"],
        },
        "old_separations_and_five_full_audits_cover_all_120_aggregates": {
            "passed": bool(
                inventory["passed"]
                and sector["passed"]
                and product["passed"]
                and inventory["old_modulus_separated_aggregate_count"]
                + len(inventory["overlap_records"])
                == EXPECTED_DEGREE_AGGREGATE_COUNT
            ),
            "threshold": ("115 old-separated plus five fully indexed overlap aggregates"),
            "value": {
                "old_separated": inventory["old_modulus_separated_aggregate_count"],
                "fully_indexed_overlaps": len(inventory["overlap_records"]),
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
        and inventory["degree_modulus_aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
        and inventory["old_modulus_separated_aggregate_count"]
        == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
        and inventory["old_modulus_overlap_aggregate_count"]
        == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        and sector["indexed_monomial_count"] == EXPECTED_INDEXED_MONOMIAL_COUNT
        and sector["sector_compatible_comparison_count"] == EXPECTED_COMPATIBLE_COMPARISON_COUNT
    )
    zero_unresolved = product["unresolved_interval_overlap_count"] == 0
    all_individual = (
        product["individual_modulus_separation_count"] == EXPECTED_COMPATIBLE_COMPARISON_COUNT
    )
    hypothesis_gates = {
        "uniform_envelope_is_spectrally_valid_and_old_disc_contained": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": ("all transformed-residual discs subset rho-discs subset Q011k discs"),
            "value": envelope["checks"],
        },
        "inventory_monomials_and_targets_cover_all_degree_seven_cases": {
            "passed": bool(validity_passed and complete_coverage),
            "threshold": (
                "120 aggregates plus 58992 overlap monomials and 44380 compatible comparisons"
            ),
            "value": {
                "aggregates": inventory["degree_modulus_aggregate_count"],
                "monomials": sector["indexed_monomial_count"],
                "comparisons": sector["sector_compatible_comparison_count"],
            },
        },
        "all_compatible_products_have_individual_modulus_separation": {
            "passed": bool(validity_passed and zero_unresolved and all_individual),
            "threshold": (
                "44380 individual modulus separations and zero unresolved interval overlaps"
            ),
            "value": {
                "individual": product["individual_modulus_separation_count"],
                "unresolved": product["unresolved_interval_overlap_count"],
            },
        },
        "minimum_modulus_gap_fits_the_registered_robust_margin": {
            "passed": bool(
                validity_passed and zero_unresolved and minimum_gap >= MINIMUM_MODULUS_GAP
            ),
            "threshold": "minimum exact modulus gap >=5e-6",
            "value": product["minimum_modulus_gap"],
        },
        "degree_seven_external_nonresonance_follows_from_complete_partition": {
            "passed": bool(
                validity_passed and complete_coverage and zero_unresolved and all_individual
            ),
            "threshold": ("115 preserved Q011u separations plus all five refined overlap audits"),
            "value": {
                "preserved_old_separations": inventory["old_modulus_separated_aggregate_count"],
                "resolved_overlap_aggregates": len(product["aggregate_category_counts"]),
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011aa degree-seven refined-modulus audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Does the contained uniform transformed-residual envelope give "
            "strict indexed-modulus separation for every Fourier-compatible "
            "comparison in all five degree-seven overlap aggregates?"
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
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    degree_seven_certified = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "uniform_transformed_residual_envelope_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "all_five_degree_seven_old_modulus_overlaps_are_eliminated": (degree_seven_certified),
        "degree_seven_external_nonresonance_is_certified": (degree_seven_certified),
        "certified_external_nonresonance_degrees": (
            [2, 3, 4, 5, 6, 7] if degree_seven_certified else [2, 3, 4, 5, 6]
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(
            range(8 if degree_seven_certified else 7, 91)
        ),
        "degrees_8_through_90_are_certified": False,
        "complex_phase_was_required_for_degree_seven": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": (False),
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_q011u_q011x_q011y_or_q011z_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree seven for the fixed 17x17 repaired "
        "exact map on one fixed conservation leaf, the five Q011u "
        "modulus-overlap aggregates, the Q011y transformed-residual "
        "enclosure, the uniform rho=5e-8 discs, x-Fourier sectors and the "
        "registered indexed-modulus product formula. It certifies no degree "
        "from 8 through 90, no all-order nonresonance, equality with the "
        "Q011t graph, C2 or higher graph smoothness, SSM existence or "
        "uniqueness, normal attraction, basin, other grid, force, wall or "
        "D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_degree_five_acceptance_changed": False,
        "q011y_eigendisc_refinement_acceptance_changed": False,
        "q011z_degree_six_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011ab to audit the degree-eight modulus-overlap "
            "aggregates using the same contained uniform envelope."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Send only the first unresolved degree-seven indexed product to "
            "an exact complex phase-sensitive product-disc comparison."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, envelope, sector, "
            "product, coverage or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011aa cycle failed strict serialization or digest")
    return cycle


def run_q011aa_study() -> dict[str, Any]:
    cycle = run_degree7_refined_modulus_audit()
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
            "uniform_relevant_identifier_count": 28,
            "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
            "compatible_comparison_count": (EXPECTED_COMPATIBLE_COMPARISON_COUNT),
            "exact_record_storage": ("framed SHA-256 plus compact extrema and witnesses"),
        },
        "mathematical_scope": {
            "diagnostic": ("degree-seven uniform refined-envelope indexed-modulus products"),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_seven_external_nonresonance_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "degrees_8_through_90_claim": False,
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
    result = run_q011aa_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
