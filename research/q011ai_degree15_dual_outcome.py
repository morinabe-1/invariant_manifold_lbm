"""Q011ai degree-fifteen dual-outcome outward-dyadic certificate."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011ah_degree14_batched_dyadic as q011ah
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

q011ag = q011ah.q011ag
q011af = q011ah.q011af
q011b = q011ah.q011b
q011u = q011ah.q011u
q011z = q011ah.q011z

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
DEGREE = 15
EXPECTED_DEGREE_AGGREGATE_COUNT = 816
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 15_504
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 713
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 103
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_EXTERNAL_GROUP_INDICES = (152, 153, 154, 156, 157, 158, 159, 162, 165, 167)
EXPECTED_EXTERNAL_GROUP_SIZES = {
    152: 8,
    153: 8,
    154: 16,
    156: 8,
    157: 8,
    158: 4,
    159: 8,
    162: 8,
    165: 4,
    167: 8,
}
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 80
EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT = 104
EXPECTED_RELEVANT_IDENTIFIER_COUNT = 144
EXPECTED_UNIQUE_CENTER_MODULUS_EVALUATION_COUNT = 83
EXPECTED_MODULUS_CLASS_COUNTS = (4, 2, 3, 6)

EXPECTED_INDEXED_MONOMIAL_COUNT = 2_813_485_588
EXPECTED_SIGNATURE_COUNT = 12_188_436
EXPECTED_COMPATIBLE_SIGNATURE_COUNT = 10_399_739
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 529_597_352
EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT = 2_283_888_236
EXPECTED_WEIGHTED_COMPARISON_COUNT = 1_103_228_296
EXPECTED_DISTINCT_COMPARISON_COUNT = 61_611_952
EXPECTED_WEIGHTED_RELATIONS = {
    "product_below_target": 669_413_248,
    "target_below_product": 433_815_048,
}
EXPECTED_DISTINCT_RELATIONS = {
    "product_below_target": 37_189_092,
    "target_below_product": 24_422_860,
}
EXPECTED_GROUP_SIGNATURE_RECORD_COUNT = 42_095
EXPECTED_COEFFICIENT_MATRIX_COUNT = 383
EXPECTED_BOUND_MATRIX_COUNT = 103
EXPECTED_CLASSIFICATION_MATRIX_COUNT = 816
EXPECTED_MAXIMUM_WAVE_COEFFICIENT = 839
EXPECTED_MAXIMUM_CRUDE_INT64_DOT_PRODUCT_BOUND = 6_528
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 532_224
EXPECTED_EXACT_REFINEMENT_CANDIDATE_COUNT = 16
EXPECTED_EXACT_MINIMUM_TIE_COUNT = 2

UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
LEGACY_MINIMUM_CERTIFIED_GAP = Fraction(5, 10**6)
EXPECTED_CERTIFIED_MINIMUM_HEX = "0x1.3a13a8193ffffp-18"
EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX = "0x1.7b351910fffffp-18"
EXPECTED_EXACT_MINIMUM_FLOAT_HEX = "0x1.3a13a821564eap-18"
EXPECTED_EXACT_MINIMUM_DIGEST = "3b4297b1c4892d5f0699ad8382a514d5121410b6ba41905084849c6f03118dee"
EXPECTED_EXACT_CANDIDATE_DIGEST = "94c950b8e748257792fe14563ea29b4c5e42eece2262374fb67b15076febd5dd"

EXPECTED_INVENTORY_DIGEST = "b9689962ea60817e439df5010316829ac11e1aa35be2a2c772cc8c3bc3593683"
EXPECTED_UNIFORM_RECORD_DIGEST = "8b831db61f0fe21988bdcdc5efe0c19d0b176aaa3a4acf8c214bae2050359ae0"
EXPECTED_COUNT_VECTOR_DIGEST = "827f22787b76507f734f578a34cefb6d697aa8ec4b534a59e24529435473c4a5"
EXPECTED_AGGREGATE_RECORD_DIGEST = (
    "7e9ac281c20ba8f2f98a48f95219d7b1a80e9a7cfaa66d1deea1bb33b23863cf"
)
EXPECTED_CLASS_MEMBERSHIP_DIGEST = q011ag.EXPECTED_CLASS_MEMBERSHIP_DIGEST
EXPECTED_OUTWARD_BASE_DIGEST = q011ag.EXPECTED_OUTWARD_BASE_DIGEST
EXPECTED_FACTORIZATION_DIGEST = "8a5389a579b55e86c7587fb7b7d8bd47d12eb815181d3a5c49324615ef47e559"
EXPECTED_WAVE_HISTOGRAM_DIGEST = "bf96f1ac176f2f80416a1557a00c439e80cdf7ba5f55d633231e36571b5ab12b"
EXPECTED_COEFFICIENT_MATRIX_DIGEST = (
    "9800aa1785efe3f08787070bee633a2790cc0bf46ae10a6bf6b995254c41bac8"
)
EXPECTED_DYADIC_BOUND_DIGEST = "a72ba6becfe0c66e54099e9fd292a2c6eb47326f8ac7d09e92e4e810475d0ab3"
EXPECTED_CLASSIFICATION_MATRIX_DIGEST = (
    "13f31639cb94b045eb21d83f969d4d24799d9f3f4e5371fa5efd098f467bf157"
)
EXPECTED_COMPACT_PILOT_DIGEST = "d535a14d207e038b9e7b883262a3371217b6428bbd4207861932e72f2d3d5513"

Q011AH_ARTIFACT_SHA256 = "eb44d70634db37d392829d597495595fc334d6ff448d597856d4558f34cc6510"
Q011AH_RUNNER_SHA256 = "af63c12025be0f2364d572065b073d3daafe8c7c1fcc0439365931afbc822d6d"
Q011AH_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "compression_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)
Q011AH_DIGESTS = (
    "f9b56d7c946e87637efb31736eeccb12bfba8649dc174eb625f461fe9fd07be1",
    "84470f689b8d102fa3710a392444a7624ff00b6e5581be767155b27069693d80",
    "8968069139fcfa41bed5128d8f561afd3f68eab2bd48035243d2b7736951345b",
    "370e36d8d088b6e4900c312ff16dc7656f250f1b67420d729936ad88ac971558",
    "f16b601ad207edd7b9bf19152385d304148a1b9f767ab1d087af039ef49177fa",
)

PRIMARY_ACCEPTED_CLASSIFICATION = (
    "degree-15 external nonresonance is certified by strict outward-dyadic separation"
)
LEGACY_MARGIN_REJECTED_CLASSIFICATION = (
    "the legacy 5e-6 certified-margin benchmark is rejected at degree 15"
)
COMBINED_ACCEPTED_CLASSIFICATION = (
    f"{PRIMARY_ACCEPTED_CLASSIFICATION}; {LEGACY_MARGIN_REJECTED_CLASSIFICATION}"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-15 outward-dyadic indexed-modulus product "
    "remains inseparable from an external target"
)

COUNT_VECTOR_KEYS = (
    "aggregate_original_monomial_counts",
    "aggregate_modulus_signature_counts",
    "aggregate_compatible_modulus_signature_counts",
    "aggregate_compatible_original_monomial_counts",
    "aggregate_weighted_comparison_counts",
    "aggregate_distinct_comparison_counts",
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
    prior, artifacts = q011ah._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ah_degree14_batched_dyadic.json"
    runner_path = Path(q011ah.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AH_DIGEST_NAMES)
    checks = {
        "q011ah_twelve_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"] and prior["direct_digest_count"] == 63 and all(prior["checks"].values())
        ),
        "q011ah_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011AH_ARTIFACT_SHA256),
        "q011ah_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AH_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AH_RUNNER_SHA256
        ),
        "q011ah_digests_match": digests == Q011AH_DIGESTS,
        "q011ah_registered_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["scientific_classification"] == q011ah.ACCEPTED_CLASSIFICATION
        ),
        "q011ah_degree_fourteen_scope_is_preserved": bool(
            cycle["theorem_consequence"]["degree_fourteen_external_nonresonance_is_certified"]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == list(range(2, 15))
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(15, 91))
            and not cycle["theorem_consequence"]["ssm_existence_or_uniqueness_is_certified"]
        ),
        "q011ah_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ah_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ah_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "sixty_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 68
        ),
    }
    artifacts["q011ah"] = artifact
    audit = {
        "prior_q011ah_sealed_input_audit": prior,
        "q011ah": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AH_DIGEST_NAMES),
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
    external_indices = tuple(record["external_group_indices"][0] for record in overlap_records)
    external_target_groups = tuple(
        tuple(sorted(external_merged[index].identifiers)) for index in external_indices
    )
    stored_selected = stored_spectrum["selected_merged_records"]
    stored_external = stored_spectrum["external_merged_records"]
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
                zip(external_indices, external_target_groups, strict=True)
            )
        ],
    }
    exact_digest = q011b._canonical_json_sha256(exact_inventory)
    first_overlap = degree_record["first_overlap"]
    checks = {
        "q011u_old_modulus_spectrum_reconstructs_exactly": bool(
            reconstructed["passed"] and reconstructed == stored_spectrum
        ),
        "q011u_degree_fifteen_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_103_overlaps_have_one_registered_external_group": bool(
            len(overlap_records) == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
            and all(len(record["external_group_indices"]) == 1 for record in overlap_records)
            and tuple(sorted(set(external_indices))) == EXPECTED_EXTERNAL_GROUP_INDICES
            and tuple(first_overlap["selected_type_counts"])
            == tuple(overlap_records[0]["selected_type_counts"])
            and first_overlap["external_group_index"] == external_indices[0]
        ),
        "selected_source_memberships_and_sizes_reproduce": bool(
            tuple(len(group) for group in selected_groups) == EXPECTED_SELECTED_GROUP_SIZES
            and all(
                q011b._canonical_json_sha256(list(group))
                == stored_selected[index]["membership_digest_sha256"]
                for index, group in enumerate(selected_groups)
            )
        ),
        "external_target_memberships_sizes_and_union_reproduce": bool(
            all(
                len(group) == EXPECTED_EXTERNAL_GROUP_SIZES[external_index]
                and q011b._canonical_json_sha256(list(group))
                == stored_external[external_index]["membership_digest_sha256"]
                for group, external_index in zip(
                    external_target_groups, external_indices, strict=True
                )
            )
            and len(set().union(*map(set, external_target_groups)))
            == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
        ),
        "old_degree_fourteen_certificate_is_preserved": artifacts["q011ah"]["cycle"][
            "theorem_consequence"
        ]["degree_fourteen_external_nonresonance_is_certified"],
        "registered_exact_inventory_digest_reproduces": exact_digest == EXPECTED_INVENTORY_DIGEST,
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
        "external_group_indices": list(external_indices),
        "unique_external_group_indices": sorted(set(external_indices)),
        "external_target_groups": [
            {
                "aggregate_index": index,
                "external_group_index": external_indices[index],
                "identifiers": list(group),
            }
            for index, group in enumerate(external_target_groups)
        ],
        "unique_external_target_count": len(set().union(*map(set, external_target_groups))),
        "old_spectrum_digest_sha256": q011b._canonical_json_sha256(reconstructed),
        "exact_inventory_digest_sha256": exact_digest,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, selected_groups, external_target_groups, tuple(overlap_records)


def _uniform_envelope_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
    overlap_records: tuple[dict[str, Any], ...],
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
            for record in overlap_records
            for group_index, multiplicity in enumerate(record["selected_type_counts"])
            if multiplicity > 0
        }
    )
    selected_identifiers = set().union(
        *(set(selected_groups[index]) for index in active_group_indices)
    )
    external_identifiers = set().union(*map(set, external_target_groups))
    directly_relevant = selected_identifiers | external_identifiers
    prior_records = {
        record["identifier"]: record
        for record in artifacts["q011ah"]["cycle"]["uniform_refined_envelope_audit"][
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
    external_indices = tuple(record["external_group_indices"][0] for record in overlap_records)
    expected_new_identifiers = set().union(
        *(
            set(group)
            for group, external_index in zip(external_target_groups, external_indices, strict=True)
            if external_index in (152, 153, 154)
        )
    ) - set(prior_records)
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
        "all_104_direct_and_144_monotone_identifiers_have_uniform_intervals": bool(
            len(lookup) == EXPECTED_RELEVANT_IDENTIFIER_COUNT
            and set(lookup) == directly_relevant | set(prior_records)
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
        "all_q011ah_112_uniform_records_are_preserved_exactly": bool(
            len(prior_records) == 112
            and set(prior_records).issubset(current_records)
            and all(
                current_records[identifier] == record
                for identifier, record in prior_records.items()
            )
        ),
        "only_thirty_two_group_152_153_154_records_are_added": bool(
            len(new_identifiers) == 32 and new_identifiers == expected_new_identifiers
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
        "active_selected_group_indices": active_group_indices,
        "uniform_radius": _fraction_record(UNIFORM_REFINED_RADIUS),
        "uniform_radius_formula": "rho=1/20,000,000=5e-8",
        "maximum_transformed_residual_radius": _fraction_record(theta[maximum_theta_block]),
        "maximum_theta_block": maximum_theta_block,
        "minimum_q011k_old_radius": _fraction_record(old_radii[minimum_old_radius_block]),
        "minimum_old_radius_block": minimum_old_radius_block,
        "directly_relevant_identifier_count": len(directly_relevant),
        "relevant_identifier_count": len(lookup),
        "unique_center_modulus_evaluation_count": len(modulus_cache),
        "new_group_152_153_154_identifiers": sorted(new_identifiers),
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


def _q011ah_oracle_audit(
    artifacts: dict[str, dict[str, Any]],
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> dict[str, Any]:
    cycle = artifacts["q011ah"]["cycle"]
    inventory = cycle["degree14_modulus_inventory_audit"]
    overlap_counts = tuple(
        tuple(record["selected_type_counts"]) for record in inventory["overlap_records"]
    )
    target_groups = tuple(
        tuple(record["identifiers"]) for record in inventory["external_target_groups"]
    )
    audit = q011ag._batched_audit(
        classes,
        lookup,
        overlap_counts,
        target_groups,
        collect_registered_digests=False,
        exact_refinement=False,
    )
    product = cycle["outward_dyadic_product_audit"]
    compression = cycle["batched_fourier_multiplicity_audit"]
    checks = {
        "all_registered_q011ah_counts_reproduce": bool(
            audit["original_monomial_count"]
            == compression["original_monomial_count"]
            == 893_043_240
            and audit["modulus_signature_count"]
            == compression["modulus_signature_count"]
            == 4_091_730
            and audit["compatible_modulus_signature_count"]
            == compression["compatible_modulus_signature_count"]
            == 3_543_001
            and audit["compatible_original_monomial_count"]
            == compression["compatible_original_monomial_count"]
            == 152_292_218
            and audit["weighted_comparison_count"]
            == product["weighted_comparison_count"]
            == 310_135_908
            and audit["distinct_comparison_count"]
            == product["distinct_comparison_count"]
            == 21_891_420
        ),
        "weighted_and_distinct_relations_reproduce": bool(
            audit["weighted_relation_counts"] == product["weighted_relation_counts"]
            and audit["distinct_relation_counts"] == product["distinct_relation_counts"]
        ),
        "outward_oracle_has_no_unresolved_comparison": bool(
            audit["weighted_relation_counts"]["overlap"] == 0
            and audit["distinct_relation_counts"]["overlap"] == 0
        ),
        "registered_outward_oracle_minimum_and_witness_reproduce": bool(
            audit["minimum_certified_gap_lower"]["binary64_hex"]
            == EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX
            and audit["minimum_certified_gap_witness"]["aggregate_index"] == 5
            and audit["minimum_certified_gap_witness"]["selected_type_counts"] == [0, 4, 2, 8]
            and audit["minimum_certified_gap_witness"]["target_identifier"] == "block=14;center=146"
        ),
        "oracle_arithmetic_contract_is_valid": bool(
            audit["all_group_and_pair_bounds_contain_exact_fraction_products"]
            and audit["all_product_bound_arrays_are_finite"]
            and audit["all_product_bound_arrays_are_nonnegative_and_ordered"]
            and audit["integer_matrix_arithmetic_is_exact_without_overflow"]
        ),
    }
    return {
        "degree": 14,
        "original_monomial_count": audit["original_monomial_count"],
        "modulus_signature_count": audit["modulus_signature_count"],
        "compatible_modulus_signature_count": audit["compatible_modulus_signature_count"],
        "compatible_original_monomial_count": audit["compatible_original_monomial_count"],
        "weighted_comparison_count": audit["weighted_comparison_count"],
        "distinct_comparison_count": audit["distinct_comparison_count"],
        "weighted_relation_counts": audit["weighted_relation_counts"],
        "distinct_relation_counts": audit["distinct_relation_counts"],
        "minimum_certified_gap_lower": audit["minimum_certified_gap_lower"],
        "minimum_certified_gap_witness": audit["minimum_certified_gap_witness"],
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
        "count_vector_digest_sha256": EXPECTED_COUNT_VECTOR_DIGEST,
        "uniform_radius": _fraction_record(UNIFORM_REFINED_RADIUS),
        "legacy_minimum_certified_gap": _fraction_record(LEGACY_MINIMUM_CERTIFIED_GAP),
        "replacement_margin_threshold": None,
        "primary_gate_uses_strict_positive_separation_not_legacy_margin": True,
        "outward_rounding": (
            "exact Fraction endpoints converted outward; every positive "
            "multiply, subtract and add is followed by nextafter toward "
            "the required infinity"
        ),
        "primary_accepted_classification": PRIMARY_ACCEPTED_CLASSIFICATION,
        "legacy_margin_rejected_classification": LEGACY_MARGIN_REJECTED_CLASSIFICATION,
        "combined_accepted_classification": COMBINED_ACCEPTED_CLASSIFICATION,
        "rejected_classification": REJECTED_CLASSIFICATION,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "legacy_margin_outcome": cycle["legacy_margin_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "failed_hypothesis_order": cycle["failed_hypothesis_order"],
    }


def run_degree15_dual_outcome_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = _inventory_audit(
        artifacts
    )
    envelope, lookup = _uniform_envelope_audit(
        artifacts, selected_groups, external_target_groups, overlap_records
    )
    classes, class_records = q011ag._modulus_classes(selected_groups, lookup)
    class_digest = q011b._canonical_json_sha256(class_records)
    outward_bases = q011ag._outward_base_records(classes, lookup)
    outward_base_digest = q011b._canonical_json_sha256(outward_bases)
    oracle = _q011ah_oracle_audit(artifacts, classes, lookup)
    overlap_counts = tuple(tuple(record["selected_type_counts"]) for record in overlap_records)
    batched = q011ag._batched_audit(
        classes,
        lookup,
        overlap_counts,
        external_target_groups,
        collect_registered_digests=True,
        exact_refinement=True,
    )
    batched["class_membership_digest_sha256"] = class_digest
    batched["outward_base_digest_sha256"] = outward_base_digest
    exact = batched["exact_refinement_audit"]
    if exact is None:
        raise RuntimeError("Q011ai exact refinement was not run")
    count_vectors = {key: batched[key] for key in COUNT_VECTOR_KEYS}
    count_vector_digest = q011b._canonical_json_sha256(count_vectors)
    aggregate_record_digest = q011b._canonical_json_sha256(batched["aggregate_records"])

    compression_checks = {
        "selected_groups_partition_into_registered_modulus_classes": bool(
            tuple(len(group) for group in classes) == EXPECTED_MODULUS_CLASS_COUNTS
            and class_digest == EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "all_six_103_entry_count_vectors_reproduce": bool(
            all(
                len(count_vectors[key]) == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
                for key in COUNT_VECTOR_KEYS
            )
            and count_vector_digest == EXPECTED_COUNT_VECTOR_DIGEST
            and aggregate_record_digest == EXPECTED_AGGREGATE_RECORD_DIGEST
        ),
        "all_registered_totals_reproduce": bool(
            batched["original_monomial_count"] == EXPECTED_INDEXED_MONOMIAL_COUNT
            and batched["modulus_signature_count"] == EXPECTED_SIGNATURE_COUNT
            and batched["compatible_modulus_signature_count"] == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and batched["compatible_original_monomial_count"] == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and batched["incompatible_original_monomial_count"]
            == EXPECTED_INCOMPATIBLE_MONOMIAL_COUNT
            and batched["weighted_comparison_count"] == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and batched["distinct_comparison_count"] == EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
        "registered_factorization_and_wave_digests_reproduce": bool(
            batched["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_RECORD_COUNT
            and batched["factorization_digest_sha256"] == EXPECTED_FACTORIZATION_DIGEST
            and batched["aggregate_wave_histogram_digest_sha256"] == EXPECTED_WAVE_HISTOGRAM_DIGEST
        ),
        "q011ah_outward_dyadic_oracle_reproduces": oracle["passed"],
    }
    compression = {
        "compression_identity": {
            "modulus_class_definition": (
                "identical exact center-modulus interval within one selected source group"
            ),
            "factorization": (
                "exact group weak-composition polynomials, exact pair "
                "cyclic convolution and int64 target-sector matrix product"
            ),
            "count_vector_seal": (
                "six ordered 103-entry integer vectors sealed as one canonical JSON digest"
            ),
        },
        "selected_modulus_class_counts": [len(group) for group in classes],
        "selected_modulus_class_records": class_records,
        "class_membership_digest_sha256": class_digest,
        "q011ah_outward_dyadic_oracle": oracle,
        "count_vectors": count_vectors,
        "count_vector_digest_sha256": count_vector_digest,
        "aggregate_record_digest_sha256": aggregate_record_digest,
        "original_monomial_count": batched["original_monomial_count"],
        "modulus_signature_count": batched["modulus_signature_count"],
        "compatible_modulus_signature_count": batched["compatible_modulus_signature_count"],
        "compatible_original_monomial_count": batched["compatible_original_monomial_count"],
        "incompatible_original_monomial_count": batched["incompatible_original_monomial_count"],
        "weighted_comparison_count": batched["weighted_comparison_count"],
        "distinct_comparison_count": batched["distinct_comparison_count"],
        "group_signature_record_count": batched["group_signature_record_count"],
        "factorization_digest_sha256": batched["factorization_digest_sha256"],
        "aggregate_wave_histogram_digest_sha256": batched["aggregate_wave_histogram_digest_sha256"],
        "checks": compression_checks,
        "passed": all(compression_checks.values()),
    }
    product_checks = {
        "registered_outward_base_and_array_digests_reproduce": bool(
            outward_base_digest == EXPECTED_OUTWARD_BASE_DIGEST
            and batched["coefficient_matrix_record_count"] == EXPECTED_COEFFICIENT_MATRIX_COUNT
            and batched["coefficient_matrix_digest_sha256"] == EXPECTED_COEFFICIENT_MATRIX_DIGEST
            and batched["dyadic_bound_matrix_record_count"] == EXPECTED_BOUND_MATRIX_COUNT
            and batched["dyadic_bound_digest_sha256"] == EXPECTED_DYADIC_BOUND_DIGEST
            and batched["classification_matrix_record_count"]
            == EXPECTED_CLASSIFICATION_MATRIX_COUNT
            and batched["classification_matrix_digest_sha256"]
            == EXPECTED_CLASSIFICATION_MATRIX_DIGEST
            and batched["compact_pilot_digest_sha256"] == EXPECTED_COMPACT_PILOT_DIGEST
        ),
        "outward_arithmetic_contains_exact_products_without_overflow": bool(
            batched["all_group_and_pair_bounds_contain_exact_fraction_products"]
            and batched["all_product_bound_arrays_are_finite"]
            and batched["all_product_bound_arrays_are_nonnegative_and_ordered"]
            and batched["integer_matrix_arithmetic_is_exact_without_overflow"]
            and batched["maximum_wave_coefficient"] == EXPECTED_MAXIMUM_WAVE_COEFFICIENT
            and batched["maximum_crude_int64_dot_product_bound"]
            == EXPECTED_MAXIMUM_CRUDE_INT64_DOT_PRODUCT_BOUND
            and batched["maximum_live_signature_count"] == EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT
        ),
        "all_registered_relations_are_strict_and_unresolved_is_zero": bool(
            {
                key: value
                for key, value in batched["weighted_relation_counts"].items()
                if key != "overlap"
            }
            == EXPECTED_WEIGHTED_RELATIONS
            and {
                key: value
                for key, value in batched["distinct_relation_counts"].items()
                if key != "overlap"
            }
            == EXPECTED_DISTINCT_RELATIONS
            and batched["weighted_relation_counts"]["overlap"] == 0
            and batched["distinct_relation_counts"]["overlap"] == 0
        ),
        "registered_strictly_positive_lower_bound_reproduces": bool(
            batched["minimum_certified_gap_lower"]["binary64_hex"] == EXPECTED_CERTIFIED_MINIMUM_HEX
            and Fraction.from_float(batched["minimum_certified_gap_lower"]["float"]) > 0
        ),
        "all_16_near_candidates_refine_to_the_registered_exact_minimum": bool(
            exact["candidate_comparison_count"] == EXPECTED_EXACT_REFINEMENT_CANDIDATE_COUNT
            and exact["candidate_exact_record_digest_sha256"] == EXPECTED_EXACT_CANDIDATE_DIGEST
            and exact["exact_global_minimum_tie_count"] == EXPECTED_EXACT_MINIMUM_TIE_COUNT
            and float(q011z._fraction(exact["exact_global_minimum_gap"])).hex()
            == EXPECTED_EXACT_MINIMUM_FLOAT_HEX
            and exact["exact_global_minimum_gap_digest_sha256"] == EXPECTED_EXACT_MINIMUM_DIGEST
            and exact["all_other_aggregate_lower_bounds_exceed_the_exact_cutoff"]
            and exact["canonical_minimum_witness"]["aggregate_index"] == 31
            and exact["canonical_minimum_witness"]["target_identifier"] == "block=13;center=1"
            and exact["canonical_minimum_witness"]["wave_multiplicity"] == 3
        ),
        "legacy_5e_6_margin_benchmark_rejection_reproduces": bool(
            Fraction.from_float(batched["minimum_certified_gap_lower"]["float"])
            < LEGACY_MINIMUM_CERTIFIED_GAP
            and q011z._fraction(exact["exact_global_minimum_gap"]) < LEGACY_MINIMUM_CERTIFIED_GAP
        ),
    }
    legacy_margin = {
        "benchmark": _fraction_record(LEGACY_MINIMUM_CERTIFIED_GAP),
        "certified_lower_bound": batched["minimum_certified_gap_lower"],
        "exact_global_minimum_gap": exact["exact_global_minimum_gap"],
        "benchmark_satisfied": False,
        "outcome": "rejected",
        "classification": LEGACY_MARGIN_REJECTED_CLASSIFICATION,
        "replacement_margin_threshold_was_introduced": False,
        "registered_rejection_reproduced": product_checks[
            "legacy_5e_6_margin_benchmark_rejection_reproduces"
        ],
    }
    product_audit = {
        "outward_rounding_proof": {
            "endpoint_conversion": (
                "exact Fraction to nearest binary64, corrected by one "
                "nextafter when the nearest value is inward"
            ),
            "operation_enclosure": (
                "each positive multiply, subtract or add is followed by "
                "one nextafter toward the required infinity"
            ),
            "logical_consequence": (
                "strict separation of the outward product and target "
                "intervals implies strict separation of their exact Fraction subsets"
            ),
        },
        "outward_base_records": outward_bases,
        "outward_base_digest_sha256": outward_base_digest,
        "aggregate_records": batched["aggregate_records"],
        "aggregate_record_digest_sha256": aggregate_record_digest,
        "coefficient_matrix_record_count": batched["coefficient_matrix_record_count"],
        "coefficient_matrix_digest_sha256": batched["coefficient_matrix_digest_sha256"],
        "dyadic_bound_matrix_record_count": batched["dyadic_bound_matrix_record_count"],
        "dyadic_bound_digest_sha256": batched["dyadic_bound_digest_sha256"],
        "classification_matrix_record_count": batched["classification_matrix_record_count"],
        "classification_matrix_digest_sha256": batched["classification_matrix_digest_sha256"],
        "compact_pilot_digest_sha256": batched["compact_pilot_digest_sha256"],
        "weighted_comparison_count": batched["weighted_comparison_count"],
        "distinct_comparison_count": batched["distinct_comparison_count"],
        "weighted_relation_counts": batched["weighted_relation_counts"],
        "distinct_relation_counts": batched["distinct_relation_counts"],
        "minimum_certified_gap_lower": batched["minimum_certified_gap_lower"],
        "minimum_certified_gap_witness": batched["minimum_certified_gap_witness"],
        "exact_refinement_audit": exact,
        "legacy_margin_benchmark_audit": legacy_margin,
        "maximum_wave_coefficient": batched["maximum_wave_coefficient"],
        "maximum_crude_int64_dot_product_bound": batched["maximum_crude_int64_dot_product_bound"],
        "streaming_contract": batched["streaming_contract"],
        "checks": product_checks,
        "passed": all(product_checks.values()),
    }

    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    inventory_sections = {
        "degree15_modulus_inventory_audit": inventory,
        "uniform_refined_envelope_audit": envelope,
    }
    compression_sections = {"batched_fourier_multiplicity_audit": compression}
    product_sections = {"outward_dyadic_product_audit": product_audit}
    input_digest = q011b._canonical_json_sha256(input_sections)
    inventory_digest = q011b._canonical_json_sha256(inventory_sections)
    compression_digest = q011b._canonical_json_sha256(compression_sections)
    product_digest = q011b._canonical_json_sha256(product_sections)
    strict_payload = {
        **input_sections,
        **inventory_sections,
        **compression_sections,
        **product_sections,
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
        and compression_digest == q011b._canonical_json_sha256(compression_sections)
        and product_digest == q011b._canonical_json_sha256(product_sections)
    )
    coverage = bool(
        inventory["old_modulus_separated_aggregate_count"] + len(inventory["overlap_records"])
        == EXPECTED_DEGREE_AGGREGATE_COUNT
    )
    validity_gates = {
        "thirteen_artifacts_sixty_eight_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad/ae/af/ag/ah artifacts, runners, "
                "68 digests, outcomes, claim boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_fifteen_inventory_and_103_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "816 aggregates, 15504 controls, 713 separated and 103 registered overlaps"
            ),
            "value": inventory["checks"],
        },
        "uniform_radius_containment_and_144_monotone_moduli_reproduce": {
            "passed": envelope["passed"],
            "threshold": (
                "104 directly relevant intervals, a 144-record monotone "
                "envelope and exact preservation of all 112 Q011ah records"
            ),
            "value": envelope["checks"],
        },
        "modulus_classes_weak_compositions_and_q011ah_oracle_reproduce": {
            "passed": bool(compression["passed"] and oracle["passed"]),
            "threshold": (
                "4/2/3/6 exact modulus classes, disjoint weak-composition "
                "fibers and the Q011ah outward-dyadic oracle reproduce"
            ),
            "value": {
                "compression_checks": compression["checks"],
                "oracle_checks": oracle["checks"],
            },
        },
        "all_degree_fifteen_count_vectors_totals_and_digests_reproduce": {
            "passed": compression["passed"],
            "threshold": (
                "six 103-entry count vectors, all totals, aggregate records "
                "and registered canonical digests reproduce"
            ),
            "value": compression["checks"],
        },
        "all_registered_factor_and_array_digests_reproduce": {
            "passed": product_checks["registered_outward_base_and_array_digests_reproduce"],
            "threshold": (
                "42095 factor, 383 coefficient, 103 bound and 816 "
                "classification records reproduce their registered digests"
            ),
            "value": {
                "factorization_digest": batched["factorization_digest_sha256"],
                "coefficient_digest": batched["coefficient_matrix_digest_sha256"],
                "bound_digest": batched["dyadic_bound_digest_sha256"],
                "classification_digest": batched["classification_matrix_digest_sha256"],
            },
        },
        "outward_containment_finiteness_and_integer_exactness_reproduce": {
            "passed": product_checks["outward_arithmetic_contains_exact_products_without_overflow"],
            "threshold": (
                "outward containment, finite ordered bounds and exact "
                "nonoverflowing int64 Fourier coefficients reproduce"
            ),
            "value": {
                "maximum_wave_coefficient": batched["maximum_wave_coefficient"],
                "maximum_crude_int64_dot_product_bound": batched[
                    "maximum_crude_int64_dot_product_bound"
                ],
            },
        },
        "all_comparisons_positive_lower_bound_and_exact_refinement_reproduce": {
            "passed": bool(
                product_checks["all_registered_relations_are_strict_and_unresolved_is_zero"]
                and product_checks["registered_strictly_positive_lower_bound_reproduces"]
                and product_checks["all_16_near_candidates_refine_to_the_registered_exact_minimum"]
            ),
            "threshold": (
                "all 61611952 comparisons are outward-separated, the "
                "registered positive lower bound holds and 16 exact "
                "refinements give the registered two-way minimum tie"
            ),
            "value": product_checks,
        },
        "coverage_legacy_rejection_serialization_and_provenance_reproduce": {
            "passed": bool(
                coverage
                and product_checks["legacy_5e_6_margin_benchmark_rejection_reproduces"]
                and strict_json
                and digests_reproduce
            ),
            "threshold": (
                "713 old plus 103 full audits cover 816 aggregates, the "
                "legacy benchmark is rejected and strict JSON, section "
                "digests and runner provenance reproduce"
            ),
            "value": {
                "old_separated": inventory["old_modulus_separated_aggregate_count"],
                "compressed_overlap_audits": len(inventory["overlap_records"]),
                "legacy_margin": legacy_margin,
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    zero_unresolved = bool(
        product_audit["weighted_relation_counts"]["overlap"] == 0
        and product_audit["distinct_relation_counts"]["overlap"] == 0
    )
    hypothesis_gates = {
        "uniform_envelope_is_spectrally_valid_and_old_disc_contained": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": "all transformed-residual discs subset rho-discs subset Q011k discs",
            "value": envelope["checks"],
        },
        "multiplicity_compression_is_exact_and_q011ah_oracle_validated": {
            "passed": bool(validity_passed and compression["passed"] and oracle["passed"]),
            "threshold": (
                "exact fibers cover every original monomial and reproduce "
                "the Q011ah certificate under outward arithmetic"
            ),
            "value": compression["checks"],
        },
        "outward_products_contain_exact_products_without_integer_overflow": {
            "passed": bool(
                validity_passed
                and product_checks["outward_arithmetic_contains_exact_products_without_overflow"]
            ),
            "threshold": (
                "all exact product and target intervals are contained and "
                "all integer Fourier products are exact"
            ),
            "value": product_checks["outward_arithmetic_contains_exact_products_without_overflow"],
        },
        "all_representative_products_have_strict_outward_separation": {
            "passed": bool(validity_passed and zero_unresolved),
            "threshold": (
                "61611952 distinct outward separations cover 1103228296 "
                "weighted comparisons with zero unresolved overlap"
            ),
            "value": {
                "weighted_relations": product_audit["weighted_relation_counts"],
                "distinct_relations": product_audit["distinct_relation_counts"],
            },
        },
        "positive_margin_and_exact_global_minimum_reproduce": {
            "passed": bool(
                validity_passed
                and product_checks["registered_strictly_positive_lower_bound_reproduces"]
                and product_checks["all_16_near_candidates_refine_to_the_registered_exact_minimum"]
            ),
            "threshold": (
                "global certified lower bound is strictly positive and 16 "
                "exact candidates reproduce the registered global minimum"
            ),
            "value": {
                "certified_lower": product_audit["minimum_certified_gap_lower"],
                "exact_refinement": product_audit["exact_refinement_audit"],
            },
        },
        "degree_fifteen_nonresonance_follows_from_complete_partition": {
            "passed": bool(validity_passed and coverage and zero_unresolved),
            "threshold": (
                "713 old separations and 103 batched full audits imply "
                "degree-15 external nonresonance"
            ),
            "value": {
                "preserved_old_separations": inventory["old_modulus_separated_aggregate_count"],
                "batched_overlap_audits": len(inventory["overlap_records"]),
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    legacy_rejected = bool(
        validity_passed and product_checks["legacy_5e_6_margin_benchmark_rejection_reproduces"]
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011ai degree-fifteen dual-outcome audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = COMBINED_ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION
    legacy_outcome = "rejected" if legacy_rejected else "inconclusive"
    cycle: dict[str, Any] = {
        "question": (
            "Do exact Fourier multiplicities and outward-rounded dyadic "
            "product enclosures strictly separate all 103 degree-fifteen "
            "overlap aggregates, and does the legacy 5e-6 margin survive?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "inventory_digest_sha256": inventory_digest,
        "compression_digest_sha256": compression_digest,
        "product_digest_sha256": product_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name for name, gate in hypothesis_gates.items() if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "legacy_margin_outcome": legacy_outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    certified = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "uniform_transformed_residual_envelope_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "exact_fourier_multiplicity_and_outward_product_enclosure_is_certified": certified,
        "all_103_degree_fifteen_old_modulus_overlaps_are_eliminated": certified,
        "degree_fifteen_external_nonresonance_is_certified": certified,
        "legacy_5e_6_certified_margin_benchmark_is_satisfied": False,
        "legacy_5e_6_certified_margin_benchmark_is_rejected": legacy_rejected,
        "certified_external_nonresonance_degrees": (
            list(range(2, 16)) if certified else list(range(2, 15))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(16 if certified else 15, 91)),
        "degrees_16_through_90_are_certified": False,
        "complex_phase_was_required_for_degree_fifteen": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011ah_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree fifteen for the fixed 17x17 "
        "repaired exact map on one fixed conservation leaf, the 103 Q011u "
        "modulus-overlap aggregates, the Q011y transformed-residual "
        "enclosure, uniform rho=5e-8 discs, exact x-Fourier multiplicity "
        "polynomials, exact modulus-class fibers and outward-rounded dyadic "
        "product enclosures. Rejection of the legacy 5e-6 benchmark applies "
        "only to this fixed degree-fifteen envelope. It certifies no degree "
        "from 16 through 90, no all-order nonresonance, equality with the "
        "Q011t graph, C2 or higher graph smoothness, SSM existence or "
        "uniqueness, normal attraction, basin, other grid, force, wall or "
        "D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ah_degree_certificates_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011aj to audit degree 16 while retaining the "
            "legacy-margin rejection as a separate diagnostic."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Stop at the first outward-unresolved degree-fifteen product; "
            "the preregistration does not permit post-hoc exact rescue."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, envelope, oracle, "
            "factorization, outward-containment, digest or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ai cycle failed strict serialization or digest")
    return cycle


def run_q011ai_study() -> dict[str, Any]:
    cycle = run_degree15_dual_outcome_audit()
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
            "original_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
            "modulus_signature_count": EXPECTED_SIGNATURE_COUNT,
            "weighted_comparison_count": EXPECTED_WEIGHTED_COMPARISON_COUNT,
            "distinct_comparison_count": EXPECTED_DISTINCT_COMPARISON_COUNT,
            "exact_record_storage": (
                "ordered big-endian array digests, six count-vector seals, "
                "compact summaries and 16 exact near-minimum refinements"
            ),
        },
        "mathematical_scope": {
            "diagnostic": (
                "degree-fifteen exact Fourier-multiplicity, outward-dyadic "
                "nonresonance and legacy-margin dual outcome"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_fifteen_external_nonresonance_claim": (
                cycle["hypothesis_outcome"] == "accepted"
            ),
            "legacy_5e_6_margin_claim": False,
            "degrees_16_through_90_claim": False,
            "actual_complex_resonance_claim": False,
            "ssm_uniqueness_claim": False,
            "normal_attraction_claim": False,
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "legacy_margin_outcome": cycle["legacy_margin_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q011ai_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
