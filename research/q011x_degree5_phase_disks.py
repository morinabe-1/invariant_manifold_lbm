"""Q011x degree-five phase-sensitive output-sector product-disk audit."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011o_graph_transform_setup as q011o
import research.q011u_c91_modulus_nonresonance as q011u
import research.q011v_degree3_phase_disks as q011v
import research.q011w_degree4_phase_disks as q011w
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
DEGREE = 5
EXPECTED_DEGREE_AGGREGATE_COUNT = 56
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 252
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 54
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 2
OVERLAP_COUNTS = ((0, 3, 1, 1), (0, 4, 1, 0))
EXTERNAL_GROUP_INDICES = (178, 177)
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_EXTERNAL_TARGET_COUNTS = (4, 8)
EXPECTED_MONOMIAL_COUNTS = (640, 140)
EXPECTED_INDEXED_MONOMIAL_COUNT = 780
EXPECTED_SECTOR_HISTOGRAMS = (
    {0: 96, 1: 92, 2: 80, 3: 60, 4: 32, 5: 8, 12: 8, 13: 32, 14: 60, 15: 80, 16: 92},
    {0: 18, 1: 17, 2: 16, 3: 13, 4: 10, 5: 5, 12: 5, 13: 10, 14: 13, 15: 16, 16: 17},
)
EXPECTED_TARGET_SECTOR_HISTOGRAMS = ({2: 2, 15: 2}, {0: 4, 3: 2, 14: 2})
EXPECTED_COMPARISON_COUNTS = (320, 124)
EXPECTED_COMPATIBLE_COMPARISON_COUNT = 444
MINIMUM_COMPLEX_SEPARATION = Fraction(1, 10)

Q011W_ARTIFACT_SHA256 = "6e0b0a166b6a5f4f915cf6ba4a46c699a26c63faf92dc92388502a2244fe0b9c"
Q011W_RUNNER_SHA256 = "288a12d72f90f6df1f79a8e5f02d527d317f9a4a9828ebbcdf0cc58008b56247"
Q011W_DIGESTS = (
    "ed3eea9c2a0f5c07de59dbddb0579b2dbb36e15409c3372729efc1e0d65c7a8d",
    "51c97d78b13ba2d9e787f833fe0f3c805848723710096da566f569c2fd301416",
    "369ef47a86630f84d96033539d3a7a7e94b34a45a95a15cef6bde71174eaa455",
    "182672f831dd715402b4f52ab9aa2628ff9eba09a3c4a8de07d32a10bf736476",
    "4681053a49eb583faa30d94d44e39d0ebfb1d00091ad7447ae086f21fd5d94d3",
)
Q011W_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "sector_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)

ACCEPTED_CLASSIFICATION = (
    "degree-5 external nonresonance is certified by indexed modulus refinement "
    "and Fourier-sector phase-sensitive product disks for both overlap aggregates"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-5 modulus aggregate retains a phase-sensitive product-disc overlap"
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


def _digest_tuple(cycle: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cycle[name] for name in names)


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    directory = _artifact_directory()
    specifications = (
        (
            "q011k",
            directory / "q011k_interval_spectral_split.json",
            Path(q011k.__file__).resolve(),
            q011w.Q011K_ARTIFACT_SHA256,
            q011w.Q011K_RUNNER_SHA256,
            q011w.Q011K_DIGESTS,
            q011w.Q011K_DIGEST_NAMES,
            "accepted",
            q011w.Q011K_CLASSIFICATION,
        ),
        (
            "q011u",
            directory / "q011u_c91_modulus_nonresonance.json",
            Path(q011u.__file__).resolve(),
            q011w.Q011U_ARTIFACT_SHA256,
            q011w.Q011U_RUNNER_SHA256,
            q011w.Q011U_DIGESTS,
            q011w.Q011U_DIGEST_NAMES,
            "rejected",
            q011w.Q011U_CLASSIFICATION,
        ),
        (
            "q011v",
            directory / "q011v_degree3_phase_disks.json",
            Path(q011v.__file__).resolve(),
            q011w.Q011V_ARTIFACT_SHA256,
            q011w.Q011V_RUNNER_SHA256,
            q011w.Q011V_DIGESTS,
            q011w.Q011V_DIGEST_NAMES,
            "accepted",
            q011v.ACCEPTED_CLASSIFICATION,
        ),
        (
            "q011w",
            directory / "q011w_degree4_phase_disks.json",
            Path(q011w.__file__).resolve(),
            Q011W_ARTIFACT_SHA256,
            Q011W_RUNNER_SHA256,
            Q011W_DIGESTS,
            Q011W_DIGEST_NAMES,
            "accepted",
            q011w.ACCEPTED_CLASSIFICATION,
        ),
    )
    artifacts: dict[str, dict[str, Any]] = {}
    records: dict[str, Any] = {}
    checks: dict[str, bool] = {}
    for (
        label,
        artifact_path,
        runner_path,
        artifact_hash,
        runner_hash,
        expected_digests,
        digest_names,
        expected_outcome,
        classification,
    ) in specifications:
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        cycle = artifact["cycle"]
        digests = _digest_tuple(cycle, digest_names)
        artifacts[label] = artifact
        checks[f"{label}_artifact_sha256_matches"] = _file_sha256(artifact_path) == artifact_hash
        checks[f"{label}_runner_sha256_matches"] = bool(
            _file_sha256(runner_path) == runner_hash
            and artifact["runner_source"]["sha256"] == runner_hash
        )
        checks[f"{label}_digests_match"] = digests == expected_digests
        checks[f"{label}_registered_outcome_reproduces"] = bool(
            cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == expected_outcome
            and cycle["scientific_classification"] == classification
        )
        checks[f"{label}_package_source_metadata_matches"] = artifact["source"] == source_metadata()
        checks[f"{label}_artifact_is_strict_finite_json"] = bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        )
        records[label] = {
            "filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_sha256": _file_sha256(runner_path),
            "digests": list(digests),
            "study_validity": cycle["study_validity"],
            "hypothesis_outcome": cycle["hypothesis_outcome"],
            "scientific_classification": cycle["scientific_classification"],
            "claim_boundary": cycle["claim_boundary"],
        }

    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    v_theorem = artifacts["q011v"]["cycle"]["theorem_consequence"]
    w_theorem = artifacts["q011w"]["cycle"]["theorem_consequence"]
    checks["q011k_eigendisc_scope_is_preserved"] = bool(
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011u_c91_tail_and_valid_rejection_scope_is_preserved"] = bool(
        u_theorem["a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"]
        and u_theorem["the_degree_91_and_higher_modulus_tail_is_certified"]
        and not u_theorem["an_actual_complex_resonance_is_established"]
    )
    checks["q011v_degree_three_certificate_is_preserved"] = bool(
        v_theorem["degree_three_external_nonresonance_is_certified"]
        and not v_theorem["ssm_existence_or_uniqueness_is_certified"]
    )
    checks["q011w_degree_four_certificate_and_boundary_are_preserved"] = bool(
        w_theorem["degree_four_external_nonresonance_is_certified"]
        and w_theorem["certified_external_nonresonance_degrees"] == [2, 3, 4]
        and w_theorem["missing_external_nonresonance_degrees"] == list(range(5, 91))
        and not w_theorem["degrees_5_through_90_are_certified"]
        and not w_theorem["ssm_existence_or_uniqueness_is_certified"]
    )
    l_path = Path(q011l.__file__).resolve()
    o_path = Path(q011o.__file__).resolve()
    checks["q011l_source_sha256_matches"] = _file_sha256(l_path) == q011w.Q011L_SOURCE_SHA256
    checks["q011o_source_sha256_matches"] = _file_sha256(o_path) == q011w.Q011O_SOURCE_SHA256
    checks["twenty_two_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 22
    )
    audit = {
        **records,
        "helper_sources": {
            "q011l": {"filename": l_path.name, "sha256": _file_sha256(l_path)},
            "q011o": {"filename": o_path.name, "sha256": _file_sha256(o_path)},
        },
        "direct_digest_count": 22,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _inventory_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, q011v._EigenDisc],
    tuple[tuple[str, ...], ...],
    tuple[tuple[str, ...], ...],
    tuple[dict[str, Any], ...],
]:
    u_cycle = artifacts["q011u"]["cycle"]
    u_enumeration = u_cycle["degree_3_through_90_enumeration_audit"]
    degree_record = next(
        record for record in u_enumeration["degree_records"] if record["degree"] == DEGREE
    )
    u_spectrum = u_cycle["exact_modulus_compression_audit"]
    u_logs = u_cycle["rational_log_enclosure_audit"]
    lookup, reconstruction = q011v._reconstruct_eigendiscs(artifacts["q011k"])
    entries = [
        q011u._ModulusEntry(
            lower=disc.modulus.lower,
            upper=disc.modulus.upper,
            identifier=disc.identifier,
            selected=disc.selected,
        )
        for disc in lookup.values()
    ]
    selected_merged = q011u._merge_modulus_entries([entry for entry in entries if entry.selected])
    external_merged = q011u._merge_modulus_entries(
        [entry for entry in entries if not entry.selected]
    )
    selected_groups = tuple(tuple(sorted(component.identifiers)) for component in selected_merged)
    external_target_groups = tuple(
        tuple(sorted(external_merged[index].identifiers)) for index in EXTERNAL_GROUP_INDICES
    )

    selected_logs = tuple(
        q011w._scaled_log_pair(record) for record in u_logs["selected_log_records"]
    )
    external_logs = tuple(
        q011w._scaled_log_pair(record) for record in u_logs["external_log_records"]
    )
    overlap_records = []
    for counts in q011w._count_tuples(DEGREE):
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
                        q011u._ScaledLogInterval(
                            aggregate_lower,
                            aggregate_upper,
                        )
                    ),
                    "external_group_indices": external_indices,
                    "external_log_intervals": [
                        q011u._scaled_log_record(q011u._ScaledLogInterval(*external_logs[index]))
                        for index in external_indices
                    ],
                }
            )

    stored_selected = u_spectrum["selected_merged_records"]
    stored_external = u_spectrum["external_merged_records"]
    selected_membership_checks = [
        q011v.q011b._canonical_json_sha256(list(group))
        == stored_selected[index]["membership_digest_sha256"]
        for index, group in enumerate(selected_groups)
    ]
    external_membership_checks = [
        q011v.q011b._canonical_json_sha256(list(group))
        == stored_external[external_index]["membership_digest_sha256"]
        for group, external_index in zip(
            external_target_groups,
            EXTERNAL_GROUP_INDICES,
            strict=True,
        )
    ]
    first_overlap = degree_record["first_overlap"]
    exact_inventory = {
        "selected_source_groups": [
            {"group_index": index, "identifiers": list(group)}
            for index, group in enumerate(selected_groups)
        ],
        "overlap_records": overlap_records,
        "external_target_groups": [
            {
                "external_group_index": external_index,
                "identifiers": list(group),
            }
            for external_index, group in zip(
                EXTERNAL_GROUP_INDICES,
                external_target_groups,
                strict=True,
            )
        ],
    }
    checks = {
        "q011u_degree_five_record_is_unique_and_complete": bool(
            degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "both_overlap_count_tuples_and_external_groups_reproduce": bool(
            tuple(tuple(record["selected_type_counts"]) for record in overlap_records)
            == OVERLAP_COUNTS
            and tuple(record["external_group_indices"][0] for record in overlap_records)
            == EXTERNAL_GROUP_INDICES
            and all(len(record["external_group_indices"]) == 1 for record in overlap_records)
            and tuple(first_overlap["selected_type_counts"]) == OVERLAP_COUNTS[0]
            and first_overlap["external_group_index"] == EXTERNAL_GROUP_INDICES[0]
        ),
        "all_2598_q011k_eigendiscs_reconstruct": reconstruction["passed"],
        "q011u_individual_modulus_digest_reproduces": bool(
            reconstruction["exact_modulus_interval_digest_sha256"]
            == u_spectrum["exact_individual_modulus_interval_digest_sha256"]
        ),
        "selected_and_external_component_counts_reproduce": bool(
            len(selected_merged) == 4 and len(external_merged) == 186
        ),
        "selected_source_group_sizes_are_8_4_4_8": (
            tuple(len(group) for group in selected_groups) == EXPECTED_SELECTED_GROUP_SIZES
        ),
        "all_selected_group_memberships_match_q011u": all(selected_membership_checks),
        "external_groups_178_and_177_have_registered_memberships": bool(
            tuple(len(group) for group in external_target_groups) == EXPECTED_EXTERNAL_TARGET_COUNTS
            and all(external_membership_checks)
        ),
        "inventory_is_finite_strict_json": bool(
            _all_numeric_values_finite(exact_inventory)
            and _strict_json_serializable(exact_inventory)
            and json.dumps(exact_inventory, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "degree_modulus_aggregate_count": degree_record["aggregate_count"],
        "degree_expanded_product_control_count": degree_record["expanded_product_control_count"],
        "modulus_separated_aggregate_count": degree_record["nonoverlap_count"],
        "modulus_overlap_aggregate_count": degree_record["overlap_count"],
        "overlap_records": overlap_records,
        "eigencenter_reconstruction": reconstruction,
        "selected_source_group_sizes": [len(group) for group in selected_groups],
        "selected_source_group_memberships": [list(group) for group in selected_groups],
        "external_target_groups": exact_inventory["external_target_groups"],
        "exact_inventory_digest_sha256": q011v.q011b._canonical_json_sha256(exact_inventory),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        lookup,
        selected_groups,
        external_target_groups,
        tuple(overlap_records),
    )


def _sector_audit(
    artifacts: dict[str, dict[str, Any]],
    lookup: dict[str, q011v._EigenDisc],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
    overlap_records: tuple[dict[str, Any], ...],
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[tuple[int, str]],
]:
    monomial_records: list[dict[str, Any]] = []
    monomial_counts = []
    for aggregate_index, overlap in enumerate(overlap_records):
        counts = tuple(overlap["selected_type_counts"])
        choices = [
            tuple(itertools.combinations_with_replacement(group, count))
            for group, count in zip(selected_groups, counts, strict=True)
        ]
        aggregate_count = 0
        for parts in itertools.product(*choices):
            identifiers = tuple(itertools.chain.from_iterable(parts))
            blocks = [lookup[identifier].block_index for identifier in identifiers]
            monomial_records.append(
                {
                    "monomial_index": len(monomial_records),
                    "aggregate_index": aggregate_index,
                    "selected_type_counts": list(counts),
                    "source_identifiers": list(identifiers),
                    "input_blocks": blocks,
                    "output_block": sum(blocks) % SIZE,
                }
            )
            aggregate_count += 1
        monomial_counts.append(aggregate_count)

    sector_histograms = [
        Counter(
            record["output_block"]
            for record in monomial_records
            if record["aggregate_index"] == aggregate_index
        )
        for aggregate_index in range(len(overlap_records))
    ]
    target_histograms = [
        Counter(lookup[identifier].block_index for identifier in target_group)
        for target_group in external_target_groups
    ]
    compatible_pairs = [
        (record["monomial_index"], target_identifier)
        for record in monomial_records
        for target_identifier in external_target_groups[record["aggregate_index"]]
        if record["output_block"] == lookup[target_identifier].block_index
    ]
    comparison_counts = [
        sum(
            1
            for monomial_index, _target in compatible_pairs
            if monomial_records[monomial_index]["aggregate_index"] == aggregate_index
        )
        for aggregate_index in range(len(overlap_records))
    ]
    compatible_monomial_indices = {monomial_index for monomial_index, _target in compatible_pairs}

    w_sector = artifacts["q011w"]["cycle"]["fourier_output_sector_audit"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    structural_wave_sum = bool(
        w_sector["passed"]
        and all(w_sector["structural_proof"].values())
        and u_theorem[
            "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
        ]
    )
    exact_sector_record = {
        "monomial_records": monomial_records,
        "compatible_pairs": [
            {
                "monomial_index": monomial_index,
                "target_identifier": target_identifier,
            }
            for monomial_index, target_identifier in compatible_pairs
        ],
    }
    checks = {
        "translation_equivariance_and_c91_regular_map_give_quintic_wave_sum": (structural_wave_sum),
        "combination_with_replacement_counts_reproduce": bool(
            tuple(monomial_counts) == EXPECTED_MONOMIAL_COUNTS
            and all(
                count == q011w._monomial_count_for_counts(selected_groups, counts)
                for count, counts in zip(
                    monomial_counts,
                    OVERLAP_COUNTS,
                    strict=True,
                )
            )
        ),
        "all_780_and_only_degree_five_overlap_monomials_are_enumerated": bool(
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
        "all_444_and_only_compatible_comparisons_are_enumerated": bool(
            tuple(comparison_counts) == EXPECTED_COMPARISON_COUNTS
            and len(compatible_pairs) == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "sector_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(exact_sector_record)
            and _strict_json_serializable(exact_sector_record)
            and json.dumps(exact_sector_record, allow_nan=False)
        ),
    }
    audit = {
        "output_sector_law": "b_out=(b_1+b_2+b_3+b_4+b_5) mod 17",
        "structural_proof": {
            "q011w_translation_equivariant_wave_sum_is_preserved": bool(
                w_sector["passed"] and all(w_sector["structural_proof"].values())
            ),
            "q011u_c91_regular_original_map_is_preserved": u_theorem[
                "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
            ],
            "translation_equivariance_applies_at_quintic_order": (structural_wave_sum),
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
        "monomial_records": monomial_records,
        "compatible_pairs": exact_sector_record["compatible_pairs"],
        "exact_sector_record_digest_sha256": q011v.q011b._canonical_json_sha256(
            exact_sector_record
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, monomial_records, compatible_pairs


def _product_disk_audit(
    lookup: dict[str, q011v._EigenDisc],
    monomial_records: list[dict[str, Any]],
    compatible_pairs: list[tuple[int, str]],
) -> tuple[dict[str, Any], Fraction]:
    product_framer = q011w._FramedRecordDigest("Q011x/exact-product-record/v1")
    comparison_framer = q011w._FramedRecordDigest("Q011x/exact-comparison-record/v1")
    modulus_cache: dict[tuple[Fraction, Fraction], RationalInterval] = {}
    internal_products: dict[int, dict[str, Any]] = {}
    radius_identities_hold = True

    for monomial in monomial_records:
        discs = [lookup[identifier] for identifier in monomial["source_identifiers"]]
        product_center = (Fraction(1), Fraction(0))
        for disc in discs:
            product_center = q011v._complex_product(product_center, disc.center)
        center_modulus_uppers = tuple(disc.center_modulus.upper for disc in discs)
        radii = tuple(disc.radius for disc in discs)
        upper_product = Fraction(1)
        center_upper_product = Fraction(1)
        for upper, radius in zip(center_modulus_uppers, radii, strict=True):
            upper_product *= upper + radius
            center_upper_product *= upper
        product_radius = upper_product - center_upper_product
        expansion_radius = q011w._product_radius_expansion(
            center_modulus_uppers,
            radii,
        )
        radius_identities_hold = bool(radius_identities_hold and product_radius == expansion_radius)
        center_modulus = q011w._cached_center_modulus(
            modulus_cache,
            product_center,
        )
        product_modulus = RationalInterval(
            max(Fraction(0), center_modulus.lower - product_radius),
            center_modulus.upper + product_radius,
        )
        product_framer.update(
            {
                "monomial_index": monomial["monomial_index"],
                "product_center": q011w._exact_complex_record(product_center),
                "product_radius": q011w._exact_fraction_record(product_radius),
                "product_center_modulus_lower": q011w._exact_fraction_record(center_modulus.lower),
                "product_center_modulus_upper": q011w._exact_fraction_record(center_modulus.upper),
                "product_modulus_lower": q011w._exact_fraction_record(product_modulus.lower),
                "product_modulus_upper": q011w._exact_fraction_record(product_modulus.upper),
                "radius_expansion_identity_reproduces": (product_radius == expansion_radius),
            }
        )
        internal_products[monomial["monomial_index"]] = {
            "center": product_center,
            "radius": product_radius,
            "modulus": product_modulus,
        }

    category_counts: Counter[str] = Counter()
    aggregate_category_counts = [Counter() for _ in OVERLAP_COUNTS]
    compact_comparison_records = []
    minimum_margin: Fraction | None = None
    minimum_margin_witness: dict[str, Any] | None = None
    minimum_phase_margin: Fraction | None = None
    minimum_phase_witness: dict[str, Any] | None = None
    first_unresolved: dict[str, Any] | None = None
    modulus_separation_has_positive_complex_margin = True

    for comparison_index, (monomial_index, target_identifier) in enumerate(compatible_pairs):
        monomial = monomial_records[monomial_index]
        product = internal_products[monomial_index]
        target = lookup[target_identifier]
        product_modulus = product["modulus"]
        modulus_gap: Fraction | None
        if product_modulus.upper < target.modulus.lower:
            modulus_gap = target.modulus.lower - product_modulus.upper
            modulus_side = "product_below_target"
        elif target.modulus.upper < product_modulus.lower:
            modulus_gap = product_modulus.lower - target.modulus.upper
            modulus_side = "target_below_product"
        else:
            modulus_gap = None
            modulus_side = "overlap"

        difference = (
            product["center"][0] - target.center[0],
            product["center"][1] - target.center[1],
        )
        distance = q011w._cached_center_modulus(modulus_cache, difference)
        separation_margin = distance.lower - product["radius"] - target.radius
        if modulus_gap is not None:
            classification = "individual_modulus_separation"
            modulus_separation_has_positive_complex_margin = bool(
                modulus_separation_has_positive_complex_margin and separation_margin > 0
            )
        elif separation_margin > 0:
            classification = "complex_phase_separation"
        else:
            classification = "unresolved_product_disk_overlap"

        category_counts[classification] += 1
        aggregate_category_counts[monomial["aggregate_index"]][classification] += 1
        compact_record = {
            "comparison_index": comparison_index,
            "monomial_index": monomial_index,
            "aggregate_index": monomial["aggregate_index"],
            "target_identifier": target_identifier,
            "individual_modulus_relation": modulus_side,
            "classification": classification,
        }
        compact_comparison_records.append(compact_record)
        comparison_framer.update(
            {
                **compact_record,
                "individual_modulus_gap": (
                    None if modulus_gap is None else q011w._exact_fraction_record(modulus_gap)
                ),
                "target_modulus_lower": q011w._exact_fraction_record(target.modulus.lower),
                "target_modulus_upper": q011w._exact_fraction_record(target.modulus.upper),
                "center_distance_lower": q011w._exact_fraction_record(distance.lower),
                "center_distance_upper": q011w._exact_fraction_record(distance.upper),
                "combined_disk_radius": q011w._exact_fraction_record(
                    product["radius"] + target.radius
                ),
                "complex_separation_margin_lower": (
                    q011w._exact_fraction_record(separation_margin)
                ),
            }
        )

        if minimum_margin is None or separation_margin < minimum_margin:
            minimum_margin = separation_margin
            minimum_margin_witness = q011w._margin_witness(
                monomial,
                target_identifier,
                classification,
                separation_margin,
            )
        if classification == "complex_phase_separation" and (
            minimum_phase_margin is None or separation_margin < minimum_phase_margin
        ):
            minimum_phase_margin = separation_margin
            minimum_phase_witness = q011w._margin_witness(
                monomial,
                target_identifier,
                classification,
                separation_margin,
            )
        if classification == "unresolved_product_disk_overlap" and first_unresolved is None:
            first_unresolved = q011w._margin_witness(
                monomial,
                target_identifier,
                classification,
                separation_margin,
            )

    if minimum_margin is None:
        raise RuntimeError("Q011x has no sector-compatible product-disk comparison")
    compact_record = {
        "comparison_records": compact_comparison_records,
        "minimum_margin_witness": minimum_margin_witness,
        "minimum_phase_witness": minimum_phase_witness,
        "first_unresolved": first_unresolved,
    }
    framed_digests = {
        "algorithm": (
            "SHA-256 over domain and ordered records, each framed by an unsigned "
            "8-byte big-endian UTF-8 canonical-JSON byte length"
        ),
        "exact_product_record_count": product_framer.count,
        "exact_product_record_digest_sha256": product_framer.hexdigest(),
        "exact_comparison_record_count": comparison_framer.count,
        "exact_comparison_record_digest_sha256": comparison_framer.hexdigest(),
    }
    checks = {
        "all_780_product_centers_and_radii_are_reconstructed": bool(
            product_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
            and len(internal_products) == EXPECTED_INDEXED_MONOMIAL_COUNT
            and radius_identities_hold
        ),
        "triangle_inequality_product_disk_formula_is_exact": bool(
            radius_identities_hold
            and all(product["radius"] >= 0 for product in internal_products.values())
        ),
        "all_444_compatible_comparisons_are_evaluated": (
            comparison_framer.count == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "comparison_categories_partition_all_records": (
            sum(category_counts.values()) == len(compact_comparison_records)
        ),
        "modulus_separation_is_consistent_with_positive_complex_margin": (
            modulus_separation_has_positive_complex_margin
        ),
        "minimum_margin_and_first_unresolved_witness_reproduce": bool(
            minimum_margin_witness is not None
            and (first_unresolved is None)
            == (category_counts["unresolved_product_disk_overlap"] == 0)
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
        "product_disk_formula": {
            "center": "C=product_i(c_i), i=1..5",
            "radius": "R=product_i(u_i+r_i)-product_i(u_i), i=1..5",
            "inclusion": "product_i D(c_i,r_i) is contained in D(C,R)",
            "external_separation": "Delta^-=|C-c_e|^- - R-r_e",
        },
        "serialization_policy": (
            "compact source/target/classification records are stored; every exact "
            "rational product and comparison record is committed by framed digest"
        ),
        "product_record_count": product_framer.count,
        "comparison_record_count": comparison_framer.count,
        "individual_modulus_separation_count": category_counts["individual_modulus_separation"],
        "complex_phase_separation_count": category_counts["complex_phase_separation"],
        "unresolved_product_disk_overlap_count": category_counts["unresolved_product_disk_overlap"],
        "aggregate_category_counts": [
            {
                "aggregate_index": index,
                "selected_type_counts": list(OVERLAP_COUNTS[index]),
                "external_group_index": EXTERNAL_GROUP_INDICES[index],
                "individual_modulus_separation_count": counts["individual_modulus_separation"],
                "complex_phase_separation_count": counts["complex_phase_separation"],
                "unresolved_product_disk_overlap_count": counts["unresolved_product_disk_overlap"],
            }
            for index, counts in enumerate(aggregate_category_counts)
        ],
        "minimum_complex_separation_lower": _fraction_record(minimum_margin),
        "minimum_phase_only_separation_lower": (
            None if minimum_phase_margin is None else _fraction_record(minimum_phase_margin)
        ),
        "registered_minimum_complex_separation": _fraction_record(MINIMUM_COMPLEX_SEPARATION),
        "minimum_margin_witness": minimum_margin_witness,
        "minimum_phase_witness": minimum_phase_witness,
        "first_unresolved_product_disk_overlap": first_unresolved,
        "comparison_records": compact_comparison_records,
        "framed_exact_record_digests": framed_digests,
        "compact_product_comparison_digest_sha256": (
            q011v.q011b._canonical_json_sha256(compact_record)
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, minimum_margin


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
        "aggregate_monomial_counts": list(EXPECTED_MONOMIAL_COUNTS),
        "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
        "aggregate_compatible_comparison_counts": list(EXPECTED_COMPARISON_COUNTS),
        "compatible_comparison_count": EXPECTED_COMPATIBLE_COMPARISON_COUNT,
        "minimum_complex_separation": _fraction_record(MINIMUM_COMPLEX_SEPARATION),
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


def run_degree5_phase_disk_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        inventory,
        lookup,
        selected_groups,
        external_target_groups,
        overlap_records,
    ) = _inventory_audit(artifacts)
    sector, monomial_records, compatible_pairs = _sector_audit(
        artifacts,
        lookup,
        selected_groups,
        external_target_groups,
        overlap_records,
    )
    product, minimum_margin = _product_disk_audit(
        lookup,
        monomial_records,
        compatible_pairs,
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    inventory_sections = {"degree5_modulus_inventory_audit": inventory}
    sector_sections = {"fourier_output_sector_audit": sector}
    product_sections = {"phase_sensitive_product_disk_audit": product}
    input_digest = q011v.q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011v.q011b._canonical_json_sha256(inventory_sections)
    sector_digest = q011v.q011b._canonical_json_sha256(sector_sections)
    product_digest = q011v.q011b._canonical_json_sha256(product_sections)
    strict_payload = {
        **input_sections,
        **inventory_sections,
        **sector_sections,
        **product_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011v.q011b._canonical_json_sha256(input_sections)
        and inventory_digest == q011v.q011b._canonical_json_sha256(inventory_sections)
        and sector_digest == q011v.q011b._canonical_json_sha256(sector_sections)
        and product_digest == q011v.q011b._canonical_json_sha256(product_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "four_inputs_twenty_two_digests_and_helper_sources_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/v/w artifacts, runners, 22 digests, outcomes and "
                "claim boundaries plus Q011l/o sources reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_five_inventory_and_both_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": ("56 aggregates, 54 separated, [0,3,1,1]/178 and [0,4,1,0]/177 overlaps"),
            "value": inventory["checks"],
        },
        "memberships_640_140_monomials_and_targets_reproduce": {
            "passed": bool(
                inventory["passed"]
                and inventory["selected_source_group_sizes"] == list(EXPECTED_SELECTED_GROUP_SIZES)
                and sector["aggregate_monomial_counts"] == list(EXPECTED_MONOMIAL_COUNTS)
                and sector["external_target_counts"] == list(EXPECTED_EXTERNAL_TARGET_COUNTS)
            ),
            "threshold": (
                "selected groups 8/4/4/8, 640+140 commutative monomials and 4+8 external targets"
            ),
            "value": {
                "selected_group_sizes": inventory["selected_source_group_sizes"],
                "aggregate_monomial_counts": sector["aggregate_monomial_counts"],
                "external_target_counts": sector["external_target_counts"],
            },
        },
        "fourier_sum_histograms_and_444_compatible_comparisons_reproduce": {
            "passed": sector["passed"],
            "threshold": (
                "quintic x-Fourier sum, registered monomial/target "
                "histograms and 320+124 compatible comparisons"
            ),
            "value": sector["checks"],
        },
        "all_product_disk_and_complex_distance_formulas_reproduce": {
            "passed": product["passed"],
            "threshold": (
                "780 exact product disks and 444 exact "
                "individual-modulus/complex-distance comparisons"
            ),
            "value": product["checks"],
        },
        "partition_margin_witness_and_framed_digests_reproduce": {
            "passed": product["passed"],
            "threshold": (
                "comparison partition, minimum margin, first unresolved and "
                "both framed exact-record digests reproduce"
            ),
            "value": {
                "individual_modulus": product["individual_modulus_separation_count"],
                "complex_phase": product["complex_phase_separation_count"],
                "unresolved": product["unresolved_product_disk_overlap_count"],
                "framed_digests": product["framed_exact_record_digests"],
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

    sector_law = bool(
        sector["passed"]
        and all(sector["structural_proof"].values())
        and sector["sector_compatible_comparison_count"] == EXPECTED_COMPATIBLE_COMPARISON_COUNT
    )
    complete_coverage = bool(
        inventory["passed"]
        and inventory["degree_modulus_aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
        and inventory["modulus_separated_aggregate_count"]
        == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
        and inventory["modulus_overlap_aggregate_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        and sector["indexed_monomial_count"] == EXPECTED_INDEXED_MONOMIAL_COUNT
        and sector["sector_compatible_comparison_count"] == EXPECTED_COMPATIBLE_COMPARISON_COUNT
    )
    zero_unresolved = product["unresolved_product_disk_overlap_count"] == 0
    phase_adds_information = product["complex_phase_separation_count"] > 0
    hypothesis_gates = {
        "x_translation_equivariance_gives_the_exact_quintic_output_sector_sum": {
            "passed": bool(validity_passed and sector_law),
            "threshold": "b_out=(b_1+b_2+b_3+b_4+b_5) mod 17",
            "value": sector["structural_proof"],
        },
        "inventory_monomials_and_targets_cover_all_degree_five_cases": {
            "passed": bool(validity_passed and complete_coverage),
            "threshold": (
                "56 aggregates plus 780 overlap monomials and 444 sector-compatible comparisons"
            ),
            "value": {
                "aggregates": inventory["degree_modulus_aggregate_count"],
                "monomials": sector["indexed_monomial_count"],
                "comparisons": sector["sector_compatible_comparison_count"],
            },
        },
        "all_compatible_product_disks_are_strictly_separated": {
            "passed": bool(validity_passed and zero_unresolved),
            "threshold": "zero unresolved complex product-disc overlaps",
            "value": product["unresolved_product_disk_overlap_count"],
        },
        "minimum_complex_separation_fits_the_registered_robust_margin": {
            "passed": bool(
                validity_passed and zero_unresolved and minimum_margin >= MINIMUM_COMPLEX_SEPARATION
            ),
            "threshold": "minimum exact complex separation lower >=0.1",
            "value": product["minimum_complex_separation_lower"],
        },
        "complex_phase_strictly_resolves_at_least_one_modulus_overlap": {
            "passed": bool(validity_passed and phase_adds_information),
            "threshold": (
                "at least one indexed modulus-overlap comparison is separated by complex phase"
            ),
            "value": product["complex_phase_separation_count"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011x degree-five phase audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Do indexed modulus refinement, Fourier-sector filtering and "
            "exact complex product disks eliminate both degree-five "
            "modulus-overlap aggregates?"
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
    cycle["result_digest_sha256"] = q011v.q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    degree_five_certified = bool(validity_passed and hypotheses_passed)
    certified_degrees = [2, 3, 4, 5] if degree_five_certified else [2, 3, 4]
    missing_start = 6 if degree_five_certified else 5
    cycle["theorem_consequence"] = {
        "q011u_degree_five_modulus_inventory_is_reproduced": validity_passed,
        "both_degree_five_modulus_overlaps_are_eliminated": (degree_five_certified),
        "degree_five_external_nonresonance_is_certified": degree_five_certified,
        "certified_external_nonresonance_degrees": certified_degrees,
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(missing_start, 91)),
        "degrees_6_through_90_are_certified": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_q011u_q011v_or_q011w_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree five for the fixed 17x17 repaired "
        "exact map on one fixed conservation leaf, the two Q011u "
        "modulus-overlap aggregates, Q011k eigendiscs, x-Fourier output "
        "sectors and the registered product-disk formula. It certifies no "
        "degree from 6 through 90, no all-order nonresonance, equality with "
        "the Q011t graph, C2 or higher graph smoothness, SSM existence or "
        "uniqueness, explicit higher-smoothness radius, normal attraction, "
        "basin, other grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011v_degree_three_acceptance_changed": False,
        "q011w_degree_four_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011y to extend the indexed Fourier-sector and "
            "phase-sensitive product-disk audit to the three degree-six "
            "modulus-overlap aggregates."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Send only the first unresolved degree-five product disk to a "
            "sharper center enclosure or full homological-operator audit."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, sector, product or "
            "serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011v.q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011x cycle failed strict serialization or digest")
    return cycle


def run_q011x_study() -> dict[str, Any]:
    cycle = run_degree5_phase_disk_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "floating_point_used_for_gate_decisions": False,
            "eigencenter_count": COORDINATE_SLOT_COUNT,
            "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
            "compatible_comparison_count": (EXPECTED_COMPATIBLE_COMPARISON_COUNT),
            "exact_record_storage": "framed SHA-256 plus compact records",
        },
        "mathematical_scope": {
            "diagnostic": ("degree-five phase-sensitive output-sector product disks"),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_five_external_nonresonance_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "degrees_6_through_90_claim": False,
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
    result = run_q011x_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
