"""Q011ak degree-sixteen blockwise-radius obstruction re-audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import research.q011aj_degree16_uniform_obstruction as q011aj
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ag = q011aj.q011ag
q011ai = q011aj.q011ai
q011b = q011aj.q011b
q011z = q011aj.q011z
q011af = q011ai.q011af

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
DEGREE = 16
OBSTRUCTION_AGGREGATE_INDEX = 99
EXPECTED_OBSTRUCTION_COUNTS = (5, 6, 4, 1)
EXPECTED_OBSTRUCTION_TARGETS = (
    "block=11;center=3",
    "block=11;center=4",
    "block=6;center=3",
    "block=6;center=4",
)
EXPECTED_MODULUS_SIGNATURE_COUNT = 35_280
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 1_732_864
EXPECTED_WEIGHTED_COMPARISON_COUNT = 3_465_728
EXPECTED_DISTINCT_COMPARISON_COUNT = 141_120
EXPECTED_WEIGHTED_RELATIONS = {
    "overlap": 2_801_440,
    "product_below_target": 664_288,
    "target_below_product": 0,
}
EXPECTED_DISTINCT_RELATIONS = {
    "overlap": 125_440,
    "product_below_target": 15_680,
    "target_below_product": 0,
}
EXPECTED_BLOCK_ZERO_HISTOGRAM = {
    "0": {
        "product_below_target_distinct": 3_136,
        "product_below_target_weighted": 440_736,
        "target_below_product_distinct": 0,
        "target_below_product_weighted": 0,
        "overlap_distinct": 0,
        "overlap_weighted": 0,
    },
    "1": {
        "product_below_target_distinct": 12_544,
        "product_below_target_weighted": 223_552,
        "target_below_product_distinct": 0,
        "target_below_product_weighted": 0,
        "overlap_distinct": 0,
        "overlap_weighted": 0,
    },
    "2": {
        "product_below_target_distinct": 0,
        "product_below_target_weighted": 0,
        "target_below_product_distinct": 0,
        "target_below_product_weighted": 0,
        "overlap_distinct": 21_952,
        "overlap_weighted": 1_479_552,
    },
    "3": {
        "product_below_target_distinct": 0,
        "product_below_target_weighted": 0,
        "target_below_product_distinct": 0,
        "target_below_product_weighted": 0,
        "overlap_distinct": 31_360,
        "overlap_weighted": 176_064,
    },
    "4": {
        "product_below_target_distinct": 0,
        "product_below_target_weighted": 0,
        "target_below_product_distinct": 0,
        "target_below_product_weighted": 0,
        "overlap_distinct": 40_768,
        "overlap_weighted": 1_114_464,
    },
    "5": {
        "product_below_target_distinct": 0,
        "product_below_target_weighted": 0,
        "target_below_product_distinct": 0,
        "target_below_product_weighted": 0,
        "overlap_distinct": 31_360,
        "overlap_weighted": 31_360,
    },
}

EXPECTED_ACTIVE_RADIUS_HEX = {
    0: "0x1.5cbff506e79d2p-26",
    1: "0x1.23ce0990a1325p-30",
    6: "0x1.55edd7894e3b9p-30",
    11: "0x1.55edd7894e3b9p-30",
    16: "0x1.23ce0990a1325p-30",
}
EXPECTED_RADIUS_RECORD_DIGEST = (
    "7f84ce4de99178837aaba056d2307db67836892da1af1adc71684df4d5f1a657"
)
EXPECTED_BLOCKWISE_RECORD_DIGEST = (
    "e68a8508c788f89507e9a2561e553273f1a204afc3525eb09b9288b2511b3bc3"
)
EXPECTED_CLASS_MEMBERSHIP_DIGEST = (
    "269187f8489521c7e37ae8a91669b9dc020ac10d4ef1d42272bb636fa7bc9b8c"
)
EXPECTED_CLASS_COUNTS = (4, 2, 3, 6)
EXPECTED_BLOCK_ZERO_HISTOGRAM_DIGEST = (
    "991722ecf3c09311416490d62fbb83e2dc7b59b755df8c5ae9816627435adb10"
)
EXPECTED_MINIMUM_SEPARATED_GAP_HEX = "0x1.0c512ffffffffp-29"
EXPECTED_MINIMUM_SEPARATED_CLASS_COUNTS = (
    (5, 0, 0, 0),
    (0, 6),
    (0, 0, 4),
    (0, 0, 0, 1, 0, 0),
)
EXPECTED_MINIMUM_SEPARATED_WITNESS_DIGEST = (
    "789780dd85bbfec2d8bc9e45848f77052537450c734ac7583fca6abc973daa01"
)
EXPECTED_FIRST_UNRESOLVED_CLASS_COUNTS = (
    (0, 0, 0, 5),
    (0, 6),
    (0, 1, 3),
    (0, 0, 0, 1, 0, 0),
)
EXPECTED_FIRST_UNRESOLVED_SOURCES = (
    "block=16;center=145",
    "block=16;center=145",
    "block=16;center=145",
    "block=16;center=145",
    "block=16;center=145",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=16;center=151",
    "block=1;center=151",
    "block=0;center=149",
    "block=1;center=152",
    "block=1;center=152",
    "block=1;center=152",
    "block=0;center=147",
)
EXPECTED_FIRST_UNRESOLVED_CENTER_GAP_HEX = "0x1.192690bd0e92ap-25"
EXPECTED_FIRST_UNRESOLVED_INTERSECTION_WIDTH_HEX = "0x1.55edd7894e3b9p-29"
EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST = (
    "11dcbfc6e4481ee8faf680cacbb49ac7383904e262b2d74728b86cb2620c94da"
)
EXPECTED_OBSTRUCTION_RECORD_DIGEST = (
    "e618ddd470f114bcb4e7d6744c45d56b14b46b3a4b135cb1a2452afe9cf33dfc"
)

Q011AJ_ARTIFACT_SHA256 = "6dae03177982dbf2fee7d84439a78775fb5b89aef23b3f4cec57b5f45b997ec7"
Q011AJ_RUNNER_SHA256 = "d87c6733613d803c9ea58d63d861659637e5ad9d57e061d962795be523336bfe"
Q011AJ_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "obstruction_digest_sha256",
    "center_digest_sha256",
    "result_digest_sha256",
)
Q011AJ_DIGESTS = (
    "4847b8b335a5fcb3fd22924c7439067503753fc8657fa38bcea9a11b8d1d7111",
    "6043ab6444ad176f4624daccc5c4cdf712932c9c02e95dda2b2995afefbc741a",
    "e73117b4bbdf98c477428657cc8d31c883558f4f7d21ddb992b16dab83cc354e",
    "fee1cfab83e977e8f549945012496526a4e6731059bddb0975559de01397d155",
    "a1415d0597ca649014dbaf6b79a8a0e9bc72b3e19794ab298090e93c304565fc",
)

BLOCKWISE_CERTIFICATE_REJECTED_CLASSIFICATION = (
    "the Q011y blockwise-radius degree-16 certificate remains unresolved "
    "at the registered obstruction"
)
ACTUAL_RESONANCE_NOT_ESTABLISHED_CLASSIFICATION = (
    "an actual degree-16 complex resonance is not established; the remaining "
    "blockwise eigendisc overlaps are enclosure failures only"
)
COMBINED_CLASSIFICATION = (
    f"{BLOCKWISE_CERTIFICATE_REJECTED_CLASSIFICATION}; "
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
    prior, artifacts = q011aj._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011aj_degree16_uniform_obstruction.json"
    runner_path = Path(q011aj.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AJ_DIGEST_NAMES)
    checks = {
        "q011aj_fourteen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["direct_digest_count"] == 73
            and all(prior["checks"].values())
        ),
        "q011aj_artifact_sha256_matches": (
            _file_sha256(artifact_path) == Q011AJ_ARTIFACT_SHA256
        ),
        "q011aj_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AJ_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AJ_RUNNER_SHA256
        ),
        "q011aj_digests_match": digests == Q011AJ_DIGESTS,
        "q011aj_registered_dual_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "rejected"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["scientific_classification"] == q011aj.COMBINED_CLASSIFICATION
        ),
        "q011aj_degree_sixteen_scope_is_preserved": bool(
            cycle["theorem_consequence"][
                "degree_sixteen_uniform_rho_external_nonresonance_certificate_is_rejected"
            ]
            and not cycle["theorem_consequence"][
                "degree_sixteen_external_nonresonance_is_certified"
            ]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == list(range(2, 16))
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(16, 91))
        ),
        "q011aj_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011aj_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011aj_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "seventy_eight_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 78
        ),
    }
    artifacts["q011aj"] = artifact
    audit = {
        "prior_q011aj_sealed_input_audit": prior,
        "q011aj": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AJ_DIGEST_NAMES),
            "digests": list(digests),
            "scientific_classification": cycle["scientific_classification"],
        },
        "direct_digest_count": prior["direct_digest_count"] + len(digests),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _registered_obstruction_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[tuple[str, ...], ...],
    tuple[str, ...],
]:
    reconstructed, selected_groups, target_groups, overlap_records = q011aj._inventory_audit(
        artifacts
    )
    stored = artifacts["q011aj"]["cycle"]["degree16_modulus_inventory_audit"]
    uniform, _ = q011aj._uniform_envelope_audit(
        artifacts, selected_groups, target_groups
    )
    stored_uniform = artifacts["q011aj"]["cycle"]["uniform_refined_envelope_audit"]
    obstruction_record = overlap_records[OBSTRUCTION_AGGREGATE_INDEX]
    targets = target_groups[OBSTRUCTION_AGGREGATE_INDEX]
    stored_obstruction = artifacts["q011aj"]["cycle"][
        "first_uniform_envelope_obstruction_audit"
    ]["first_fully_unresolved_aggregate"]
    checks = {
        "q011aj_degree_sixteen_inventory_reconstructs_exactly": bool(
            reconstructed["passed"]
            and reconstructed == stored
            and q011b._canonical_json_sha256(reconstructed)
            == q011b._canonical_json_sha256(stored)
        ),
        "q011aj_uniform_envelope_reconstructs_exactly": bool(
            uniform["passed"]
            and uniform == stored_uniform
            and uniform["uniform_record_digest_sha256"]
            == q011aj.EXPECTED_UNIFORM_RECORD_DIGEST
        ),
        "registered_obstruction_index_counts_and_targets_reproduce": bool(
            tuple(obstruction_record["selected_type_counts"])
            == EXPECTED_OBSTRUCTION_COUNTS
            and tuple(obstruction_record["external_group_indices"])
            == q011aj.EXPECTED_OBSTRUCTION_EXTERNAL_GROUPS
            and targets == EXPECTED_OBSTRUCTION_TARGETS
        ),
        "q011aj_uniform_obstruction_counts_reproduce": bool(
            stored_obstruction["aggregate_index"] == OBSTRUCTION_AGGREGATE_INDEX
            and stored_obstruction["modulus_signature_count"]
            == EXPECTED_MODULUS_SIGNATURE_COUNT
            and stored_obstruction["compatible_original_monomial_count"]
            == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and stored_obstruction["weighted_comparison_count"]
            == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and stored_obstruction["distinct_comparison_count"]
            == EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
    }
    audit = {
        "aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
        "selected_type_counts": list(obstruction_record["selected_type_counts"]),
        "external_group_indices": list(obstruction_record["external_group_indices"]),
        "target_identifiers": list(targets),
        "selected_source_group_sizes": [len(group) for group in selected_groups],
        "q011aj_inventory_digest_sha256": q011b._canonical_json_sha256(stored),
        "q011aj_uniform_envelope_digest_sha256": q011b._canonical_json_sha256(
            stored_uniform
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, selected_groups, targets


def _blockwise_envelope_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
) -> tuple[
    dict[str, Any],
    dict[str, q011z._UniformDisc],
    dict[int, Fraction],
]:
    centers, selected, old_radii, metrics, reconstruction = q011z.q011l._spectral_data(
        artifacts["q011k"]
    )
    theta = {block: metrics[block]["theta"] for block in range(SIZE)}
    uniform_records = q011aj._uniform_envelope_audit(
        artifacts,
        selected_groups,
        tuple(
            tuple(record["identifiers"])
            for record in artifacts["q011aj"]["cycle"][
                "degree16_modulus_inventory_audit"
            ]["external_target_groups"]
        ),
    )[0]["uniform_disc_records"]
    selected_sets = {block: frozenset(indices) for block, indices in selected.items()}
    radius_records = []
    for block in range(SIZE):
        radius_records.append(
            {
                "block_index": block,
                "conjugate_representative_block": min(block, SIZE - block),
                "transformed_residual_radius_upper": q011z._exact_fraction_record(
                    theta[block]
                ),
                "transformed_residual_radius_binary64_hex": float(theta[block]).hex(),
                "q011k_old_radius_upper": q011z._exact_fraction_record(
                    old_radii[block]
                ),
                "contained_in_uniform_envelope": (
                    theta[block] <= q011aj.UNIFORM_REFINED_RADIUS
                ),
                "contained_in_q011k_eigendisc": theta[block] <= old_radii[block],
            }
        )
    radius_digest = q011b._canonical_json_sha256(radius_records)

    lookup: dict[str, q011z._UniformDisc] = {}
    records = []
    for uniform_record in uniform_records:
        identifier = uniform_record["identifier"]
        block, center_index = q011z._identifier_indices(identifier)
        center = centers[block][center_index]
        center_modulus = q011z.q011o._center_modulus_bounds(center)
        modulus = RationalInterval(
            max(Fraction(0), center_modulus.lower - theta[block]),
            center_modulus.upper + theta[block],
        )
        uniform_lower = q011z._fraction(uniform_record["uniform_modulus_lower"])
        uniform_upper = q011z._fraction(uniform_record["uniform_modulus_upper"])
        contained = bool(
            modulus.lower >= uniform_lower and modulus.upper <= uniform_upper
        )
        lookup[identifier] = q011z._UniformDisc(
            identifier=identifier,
            block_index=block,
            center_index=center_index,
            center_modulus=center_modulus,
            modulus=modulus,
        )
        records.append(
            {
                "identifier": identifier,
                "block_index": block,
                "center_index": center_index,
                "selected": center_index
                in selected_sets.get(block, frozenset()),
                "transformed_residual_radius_upper": q011z._exact_fraction_record(
                    theta[block]
                ),
                "center_modulus_lower": q011z._exact_fraction_record(
                    center_modulus.lower
                ),
                "center_modulus_upper": q011z._exact_fraction_record(
                    center_modulus.upper
                ),
                "blockwise_modulus_lower": q011z._exact_fraction_record(
                    modulus.lower
                ),
                "blockwise_modulus_upper": q011z._exact_fraction_record(
                    modulus.upper
                ),
                "uniform_modulus_lower": uniform_record["uniform_modulus_lower"],
                "uniform_modulus_upper": uniform_record["uniform_modulus_upper"],
                "contained_in_uniform_envelope": contained,
            }
        )
    record_digest = q011b._canonical_json_sha256(records)
    unique_centers = {
        (disc.center_modulus.lower, disc.center_modulus.upper)
        for disc in lookup.values()
    }
    checks = {
        "q011l_reconstructs_all_seventeen_blocks": bool(
            reconstruction["passed"]
            and len(centers) == SIZE
            and sum(len(block) for block in centers.values()) == COORDINATE_SLOT_COUNT
        ),
        "all_seventeen_theta_identities_are_exact_and_positive": all(
            theta[block]
            == metrics[block]["beta"] * metrics[block]["family_residual"]
            and theta[block] > 0
            for block in range(SIZE)
        ),
        "conjugate_block_radii_transport_exactly": all(
            theta[block] == theta[SIZE - block] for block in range(9, SIZE)
        ),
        "registered_active_radius_hex_values_reproduce": all(
            float(theta[block]).hex() == expected
            for block, expected in EXPECTED_ACTIVE_RADIUS_HEX.items()
        ),
        "registered_seventeen_radius_records_reproduce": bool(
            len(radius_records) == SIZE
            and radius_digest == EXPECTED_RADIUS_RECORD_DIGEST
        ),
        "all_blockwise_radii_are_contained_in_uniform_and_q011k_discs": all(
            record["contained_in_uniform_envelope"]
            and record["contained_in_q011k_eigendisc"]
            for record in radius_records
        ),
        "all_204_blockwise_identifier_records_reproduce": bool(
            len(records) == q011aj.EXPECTED_RELEVANT_IDENTIFIER_COUNT
            and len(lookup) == q011aj.EXPECTED_RELEVANT_IDENTIFIER_COUNT
            and len(unique_centers) == q011aj.EXPECTED_UNIQUE_CENTER_MODULUS_EVALUATION_COUNT
            and record_digest == EXPECTED_BLOCKWISE_RECORD_DIGEST
        ),
        "every_blockwise_interval_is_contained_in_its_uniform_interval": all(
            record["contained_in_uniform_envelope"] for record in records
        ),
        "blockwise_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    audit = {
        "radius_formula": "theta_b = beta_b * ||A_b V_b - V_b D_b||_infinity",
        "radius_records": radius_records,
        "radius_record_digest_sha256": radius_digest,
        "active_radius_binary64_hex": {
            str(block): float(theta[block]).hex()
            for block in EXPECTED_ACTIVE_RADIUS_HEX
        },
        "identifier_record_count": len(records),
        "unique_center_modulus_evaluation_count": len(unique_centers),
        "blockwise_disc_records": records,
        "blockwise_record_digest_sha256": record_digest,
        "containment_chain": (
            "spectrum subset union D(c_j,theta_block(j)) subset union "
            "D(c_j,rho) subset union D(c_j,r_old,block(j))"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup, theta


def _blockwise_group_signature(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    group_index: int,
    source_count: int,
) -> tuple[q011ag._GroupSignature, ...]:
    result = []
    for class_counts, wave_counter in q011af._group_signature_records(
        classes, group_index, source_count
    ):
        center_lower_exact = Fraction(1)
        center_upper_exact = Fraction(1)
        full_upper_exact = Fraction(1)
        bounds = [np.float64(1.0)] * 4
        for count, identifiers in zip(
            class_counts, classes[group_index], strict=True
        ):
            disc = lookup[identifiers[0]]
            factors = (
                q011ag._fraction_lower(disc.center_modulus.lower),
                q011ag._fraction_lower(disc.center_modulus.upper),
                q011ag._fraction_upper(disc.center_modulus.upper),
                q011ag._fraction_upper(disc.modulus.upper),
            )
            for _ in range(count):
                bounds[0] = q011ag._down_multiply(bounds[0], factors[0])
                bounds[1] = q011ag._down_multiply(bounds[1], factors[1])
                bounds[2] = q011ag._up_multiply(bounds[2], factors[2])
                bounds[3] = q011ag._up_multiply(bounds[3], factors[3])
            center_lower_exact *= disc.center_modulus.lower**count
            center_upper_exact *= disc.center_modulus.upper**count
            full_upper_exact *= disc.modulus.upper**count
        exact = (center_lower_exact, center_upper_exact, full_upper_exact)
        if not (
            Fraction.from_float(float(bounds[0])) <= exact[0]
            and Fraction.from_float(float(bounds[1])) <= exact[1]
            and Fraction.from_float(float(bounds[2])) >= exact[1]
            and Fraction.from_float(float(bounds[3])) >= exact[2]
        ):
            raise RuntimeError("Q011ak group outward interval lost containment")
        wave = np.array(
            [wave_counter[index] for index in range(SIZE)], dtype=np.int64
        )
        result.append(
            q011ag._GroupSignature(
                class_counts=class_counts,
                wave=wave,
                bounds=(bounds[0], bounds[1], bounds[2], bounds[3]),
                exact=exact,
                fiber_multiplicity=sum(wave_counter.values()),
            )
        )
    return tuple(result)


def _block_zero_multiplicity(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    class_counts: tuple[tuple[int, ...], ...],
) -> int:
    total = 0
    for group_classes, group_counts in zip(classes, class_counts, strict=True):
        for identifiers, count in zip(group_classes, group_counts, strict=True):
            blocks = {q011z._identifier_indices(identifier)[0] for identifier in identifiers}
            if blocks == {0}:
                total += count
            elif 0 in blocks:
                raise RuntimeError("Q011ak modulus class mixes block zero and nonzero blocks")
    return total


def _exact_blockwise_product_interval(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    class_counts: tuple[tuple[int, ...], ...],
) -> tuple[RationalInterval, RationalInterval]:
    center_lower = Fraction(1)
    center_upper = Fraction(1)
    full_upper = Fraction(1)
    for group_classes, group_counts in zip(classes, class_counts, strict=True):
        for identifiers, count in zip(group_classes, group_counts, strict=True):
            disc = lookup[identifiers[0]]
            center_lower *= disc.center_modulus.lower**count
            center_upper *= disc.center_modulus.upper**count
            full_upper *= disc.modulus.upper**count
    radius = full_upper - center_upper
    return (
        RationalInterval(max(Fraction(0), center_lower - radius), full_upper),
        RationalInterval(center_lower, center_upper),
    )


def _witness_record(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    *,
    target_identifier: str,
    output_block: int,
    left_index: int,
    right_index: int,
    wave_multiplicity: int,
    relation: str,
    class_counts: tuple[tuple[int, ...], ...],
    outward_gap: float | None = None,
) -> dict[str, Any]:
    source_identifiers = q011af._source_witness_for_signature(
        classes, class_counts, output_block
    )
    product, center_product = _exact_blockwise_product_interval(
        classes, lookup, class_counts
    )
    target_disc = lookup[target_identifier]
    target = target_disc.modulus
    target_center = target_disc.center_modulus
    if center_product.upper < target_center.lower:
        center_gap = target_center.lower - center_product.upper
    else:
        center_gap = center_product.lower - target_center.upper
    intersection_lower = max(product.lower, target.lower)
    intersection_upper = min(product.upper, target.upper)
    intersection_width = intersection_upper - intersection_lower
    record = {
        "block_zero_multiplicity": _block_zero_multiplicity(
            classes, class_counts
        ),
        "target_identifier": target_identifier,
        "output_block": output_block,
        "left_index": left_index,
        "right_index": right_index,
        "wave_multiplicity": wave_multiplicity,
        "relation": relation,
        "class_counts": [list(group) for group in class_counts],
        "source_identifiers": list(source_identifiers),
        "center_gap": q011z._exact_fraction_record(center_gap),
        "center_gap_hex": float(center_gap).hex(),
        "blockwise_product_interval": {
            "lower": q011z._exact_fraction_record(product.lower),
            "upper": q011z._exact_fraction_record(product.upper),
        },
        "blockwise_target_interval": {
            "lower": q011z._exact_fraction_record(target.lower),
            "upper": q011z._exact_fraction_record(target.upper),
        },
        "intersection_interval": {
            "lower": q011z._exact_fraction_record(intersection_lower),
            "upper": q011z._exact_fraction_record(intersection_upper),
            "width": q011z._exact_fraction_record(intersection_width),
            "width_hex": float(intersection_width).hex(),
        },
    }
    if outward_gap is not None:
        record["outward_gap_hex"] = outward_gap.hex()
    return record


def _empty_histogram() -> dict[str, dict[str, int]]:
    return {
        str(index): {
            "product_below_target_distinct": 0,
            "product_below_target_weighted": 0,
            "target_below_product_distinct": 0,
            "target_below_product_weighted": 0,
            "overlap_distinct": 0,
            "overlap_weighted": 0,
        }
        for index in range(6)
    }


def _blockwise_obstruction_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    target_group: tuple[str, ...],
) -> dict[str, Any]:
    group_pools = tuple(
        _blockwise_group_signature(classes, lookup, group_index, count)
        for group_index, count in enumerate(EXPECTED_OBSTRUCTION_COUNTS)
    )
    left = q011ag._pair_signatures(group_pools[0], group_pools[1])
    right = q011ag._pair_signatures(group_pools[2], group_pools[3])
    left_wave = np.stack([record.wave for record in left])
    right_wave = np.stack([record.wave for record in right])
    product_lower, product_upper = q011ag._product_bound_matrices(left, right)

    left_zero = np.array(
        [
            _block_zero_multiplicity(
                classes,
                (
                    *record.class_counts,
                    tuple(0 for _ in classes[2]),
                    tuple(0 for _ in classes[3]),
                ),
            )
            for record in left
        ],
        dtype=np.int64,
    )
    right_zero = np.array(
        [
            _block_zero_multiplicity(
                classes,
                (
                    tuple(0 for _ in classes[0]),
                    tuple(0 for _ in classes[1]),
                    *record.class_counts,
                ),
            )
            for record in right
        ],
        dtype=np.int64,
    )
    block_zero_matrix = np.add.outer(left_zero, right_zero)

    histogram = _empty_histogram()
    relations: Counter[str] = Counter()
    compatible = np.zeros(product_lower.shape, dtype=bool)
    compatible_monomial_count = 0
    weighted_comparison_count = 0
    distinct_comparison_count = 0
    maximum_wave_coefficient = 0
    maximum_crude_bound = 0
    all_arrays_finite = bool(
        np.isfinite(product_lower).all() and np.isfinite(product_upper).all()
    )
    all_bounds_ordered = bool(
        np.all(product_lower >= 0) and np.all(product_lower <= product_upper)
    )
    first_unresolved: tuple[Any, ...] | None = None
    minimum_separated: tuple[Any, ...] | None = None

    target_blocks = q011ag._target_groups_by_block(target_group)
    for output_block, target_identifiers in target_blocks.items():
        wave_matrix, crude_bound = q011ag._wave_matrix(
            left_wave, right_wave, output_block
        )
        active = wave_matrix > 0
        compatible |= active
        compatible_monomial_count += int(wave_matrix.sum())
        maximum_wave_coefficient = max(
            maximum_wave_coefficient, int(wave_matrix.max(initial=0))
        )
        maximum_crude_bound = max(maximum_crude_bound, crude_bound)
        weighted_comparison_count += int(wave_matrix.sum()) * len(target_identifiers)
        distinct_comparison_count += int(active.sum()) * len(target_identifiers)
        for target_identifier in target_identifiers:
            target = lookup[target_identifier]
            product_below_gap = q011ag._down_subtract(
                q011ag._fraction_lower(target.modulus.lower), product_upper
            )
            target_below_gap = q011ag._down_subtract(
                product_lower, q011ag._fraction_upper(target.modulus.upper)
            )
            product_below = active & (product_below_gap > 0)
            target_below = active & (target_below_gap > 0)
            unresolved = active & ~(product_below | target_below)
            for relation, mask, gaps in (
                ("product_below_target", product_below, product_below_gap),
                ("target_below_product", target_below, target_below_gap),
                ("overlap", unresolved, None),
            ):
                relations[f"{relation}_distinct"] += int(mask.sum())
                relations[f"{relation}_weighted"] += int(wave_matrix[mask].sum())
                for multiplicity in range(6):
                    submask = mask & (block_zero_matrix == multiplicity)
                    histogram[str(multiplicity)][f"{relation}_distinct"] += int(
                        submask.sum()
                    )
                    histogram[str(multiplicity)][f"{relation}_weighted"] += int(
                        wave_matrix[submask].sum()
                    )
                for left_raw, right_raw in zip(*np.nonzero(mask), strict=True):
                    left_index = int(left_raw)
                    right_index = int(right_raw)
                    class_counts = q011ag._signature_counts(
                        left, right, left_index, right_index
                    )
                    if relation == "overlap":
                        key = (
                            int(block_zero_matrix[left_index, right_index]),
                            target_identifier,
                            left_index,
                            right_index,
                        )
                        if first_unresolved is None or key < first_unresolved[0]:
                            first_unresolved = (
                                key,
                                target_identifier,
                                output_block,
                                left_index,
                                right_index,
                                int(wave_matrix[left_index, right_index]),
                                class_counts,
                            )
                    else:
                        if gaps is None:
                            raise RuntimeError("Q011ak separated relation has no gap")
                        gap = float(gaps[left_index, right_index])
                        key = (gap, target_identifier, left_index, right_index)
                        if minimum_separated is None or key < minimum_separated[0]:
                            minimum_separated = (
                                key,
                                target_identifier,
                                output_block,
                                left_index,
                                right_index,
                                int(wave_matrix[left_index, right_index]),
                                relation,
                                class_counts,
                            )

    if first_unresolved is None or minimum_separated is None:
        raise RuntimeError("Q011ak did not reproduce both registered outcomes")
    (
        _,
        minimum_target,
        minimum_block,
        minimum_left,
        minimum_right,
        minimum_wave,
        minimum_relation,
        minimum_counts,
    ) = minimum_separated
    minimum_witness = _witness_record(
        classes,
        lookup,
        target_identifier=minimum_target,
        output_block=minimum_block,
        left_index=minimum_left,
        right_index=minimum_right,
        wave_multiplicity=minimum_wave,
        relation=minimum_relation,
        class_counts=minimum_counts,
        outward_gap=minimum_separated[0][0],
    )
    (
        _,
        unresolved_target,
        unresolved_block,
        unresolved_left,
        unresolved_right,
        unresolved_wave,
        unresolved_counts,
    ) = first_unresolved
    unresolved_witness = _witness_record(
        classes,
        lookup,
        target_identifier=unresolved_target,
        output_block=unresolved_block,
        left_index=unresolved_left,
        right_index=unresolved_right,
        wave_multiplicity=unresolved_wave,
        relation="overlap",
        class_counts=unresolved_counts,
    )
    histogram_digest = q011b._canonical_json_sha256(histogram)
    minimum_digest = q011b._canonical_json_sha256(minimum_witness)
    unresolved_digest = q011b._canonical_json_sha256(unresolved_witness)
    weighted_relations = {
        relation: relations[f"{relation}_weighted"]
        for relation in ("overlap", "product_below_target", "target_below_product")
    }
    distinct_relations = {
        relation: relations[f"{relation}_distinct"]
        for relation in ("overlap", "product_below_target", "target_below_product")
    }
    record = {
        "aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
        "selected_type_counts": list(EXPECTED_OBSTRUCTION_COUNTS),
        "target_identifiers": list(target_group),
        "modulus_signature_count": len(left) * len(right),
        "weighted_comparison_count": weighted_comparison_count,
        "distinct_comparison_count": distinct_comparison_count,
        "weighted_relation_counts": weighted_relations,
        "distinct_relation_counts": distinct_relations,
        "block_zero_multiplicity_histogram": histogram,
        "block_zero_multiplicity_histogram_digest_sha256": histogram_digest,
        "minimum_separated_outward_witness": minimum_witness,
        "minimum_separated_outward_witness_digest_sha256": minimum_digest,
        "first_unresolved_witness": unresolved_witness,
        "first_unresolved_witness_digest_sha256": unresolved_digest,
    }
    record_digest = q011b._canonical_json_sha256(record)
    minimum_counts_tuple = tuple(
        tuple(group) for group in minimum_witness["class_counts"]
    )
    unresolved_counts_tuple = tuple(
        tuple(group) for group in unresolved_witness["class_counts"]
    )
    unresolved_width = q011z._fraction(
        unresolved_witness["intersection_interval"]["width"]
    )
    histogram_boundary = bool(
        all(
            histogram[str(index)]["product_below_target_distinct"] > 0
            and histogram[str(index)]["target_below_product_distinct"] == 0
            and histogram[str(index)]["overlap_distinct"] == 0
            for index in (0, 1)
        )
        and all(
            histogram[str(index)]["product_below_target_distinct"] == 0
            and histogram[str(index)]["target_below_product_distinct"] == 0
            and histogram[str(index)]["overlap_distinct"] > 0
            for index in range(2, 6)
        )
    )
    checks = {
        "registered_signature_and_fourier_counts_reproduce": bool(
            len(left) * len(right) == EXPECTED_MODULUS_SIGNATURE_COUNT
            and int(compatible.sum()) == EXPECTED_MODULUS_SIGNATURE_COUNT
            and compatible_monomial_count == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
            and weighted_comparison_count == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and distinct_comparison_count == EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
        "registered_blockwise_relation_counts_reproduce": bool(
            weighted_relations == EXPECTED_WEIGHTED_RELATIONS
            and distinct_relations == EXPECTED_DISTINCT_RELATIONS
        ),
        "registered_block_zero_histogram_and_boundary_reproduce": bool(
            histogram == EXPECTED_BLOCK_ZERO_HISTOGRAM
            and histogram_digest == EXPECTED_BLOCK_ZERO_HISTOGRAM_DIGEST
            and histogram_boundary
        ),
        "minimum_separated_outward_witness_reproduces": bool(
            minimum_witness["block_zero_multiplicity"] == 1
            and minimum_witness["target_identifier"] == "block=11;center=4"
            and minimum_witness["left_index"] == 385
            and minimum_witness["right_index"] == 2
            and minimum_witness["wave_multiplicity"] == 6
            and minimum_witness["relation"] == "product_below_target"
            and minimum_witness["outward_gap_hex"]
            == EXPECTED_MINIMUM_SEPARATED_GAP_HEX
            and minimum_counts_tuple == EXPECTED_MINIMUM_SEPARATED_CLASS_COUNTS
            and tuple(minimum_witness["source_identifiers"])
            == q011aj.EXPECTED_CANONICAL_SOURCE_IDENTIFIERS
            and minimum_digest == EXPECTED_MINIMUM_SEPARATED_WITNESS_DIGEST
        ),
        "first_unresolved_exact_witness_reproduces": bool(
            unresolved_witness["block_zero_multiplicity"] == 2
            and unresolved_witness["target_identifier"] == "block=11;center=3"
            and unresolved_witness["left_index"] == 0
            and unresolved_witness["right_index"] == 8
            and unresolved_witness["wave_multiplicity"] == 14
            and unresolved_witness["relation"] == "overlap"
            and unresolved_counts_tuple == EXPECTED_FIRST_UNRESOLVED_CLASS_COUNTS
            and tuple(unresolved_witness["source_identifiers"])
            == EXPECTED_FIRST_UNRESOLVED_SOURCES
            and unresolved_witness["center_gap_hex"]
            == EXPECTED_FIRST_UNRESOLVED_CENTER_GAP_HEX
            and unresolved_witness["intersection_interval"]["width_hex"]
            == EXPECTED_FIRST_UNRESOLVED_INTERSECTION_WIDTH_HEX
            and unresolved_width > 0
            and unresolved_digest == EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST
        ),
        "registered_aggregate_record_digest_reproduces": (
            record_digest == EXPECTED_OBSTRUCTION_RECORD_DIGEST
        ),
        "all_outward_arrays_are_finite_nonnegative_and_ordered": bool(
            all_arrays_finite and all_bounds_ordered
        ),
        "fourier_int64_bound_is_safe": maximum_crude_bound < np.iinfo(np.int64).max,
    }
    return {
        "registered_obstruction_record": record,
        "registered_obstruction_record_digest_sha256": record_digest,
        "compatible_modulus_signature_count": int(compatible.sum()),
        "compatible_original_monomial_count": compatible_monomial_count,
        "maximum_wave_coefficient": maximum_wave_coefficient,
        "maximum_crude_int64_dot_product_bound": maximum_crude_bound,
        "comparison_semantics": (
            "remaining interval overlap is an enclosure failure and is not evidence "
            "of an actual complex resonance"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _compression_audit(
    selected_groups: tuple[tuple[str, ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    theta: dict[int, Fraction],
) -> tuple[
    dict[str, Any],
    tuple[tuple[tuple[str, ...], ...], ...],
]:
    classes, class_records = q011ag._modulus_classes(selected_groups, lookup)
    class_digest = q011b._canonical_json_sha256(class_records)
    class_radius_records = []
    class_radii_constant = True
    outward_records = []
    outward_containment = True
    for group_index, group_classes in enumerate(classes):
        for class_index, identifiers in enumerate(group_classes):
            radii = {
                theta[q011z._identifier_indices(identifier)[0]]
                for identifier in identifiers
            }
            class_radii_constant = class_radii_constant and len(radii) == 1
            if len(radii) != 1:
                raise RuntimeError("Q011ak class has nonconstant blockwise radii")
            disc = lookup[identifiers[0]]
            radius = next(iter(radii))
            full_upper = q011ag._fraction_upper(disc.modulus.upper)
            outward_containment = bool(
                outward_containment
                and Fraction.from_float(float(full_upper)) >= disc.modulus.upper
            )
            class_radius_records.append(
                {
                    "selected_group_index": group_index,
                    "modulus_class_index": class_index,
                    "identifiers": list(identifiers),
                    "blockwise_radius": q011z._exact_fraction_record(radius),
                }
            )
            outward_records.append(
                {
                    "selected_group_index": group_index,
                    "modulus_class_index": class_index,
                    "identifier": identifiers[0],
                    "center_lower_outward_hex": float(
                        q011ag._fraction_lower(disc.center_modulus.lower)
                    ).hex(),
                    "center_upper_lower_outward_hex": float(
                        q011ag._fraction_lower(disc.center_modulus.upper)
                    ).hex(),
                    "center_upper_upper_outward_hex": float(
                        q011ag._fraction_upper(disc.center_modulus.upper)
                    ).hex(),
                    "blockwise_full_factor_upper_outward_hex": float(full_upper).hex(),
                }
            )
    checks = {
        "registered_modulus_classes_and_membership_digest_reproduce": bool(
            tuple(len(group) for group in classes) == EXPECTED_CLASS_COUNTS
            and class_digest == EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "every_modulus_class_has_one_exact_blockwise_radius": class_radii_constant,
        "all_blockwise_outward_bases_contain_the_exact_factors": outward_containment,
        "class_and_outward_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(class_radius_records)
            and _all_numeric_values_finite(outward_records)
            and _strict_json_serializable(class_radius_records)
            and _strict_json_serializable(outward_records)
        ),
    }
    audit = {
        "selected_modulus_class_counts": [len(group) for group in classes],
        "selected_modulus_class_records": class_records,
        "class_membership_digest_sha256": class_digest,
        "class_radius_records": class_radius_records,
        "class_radius_record_digest_sha256": q011b._canonical_json_sha256(
            class_radius_records
        ),
        "blockwise_outward_base_records": outward_records,
        "blockwise_outward_base_digest_sha256": q011b._canonical_json_sha256(
            outward_records
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, classes


def _registered_parameters() -> dict[str, Any]:
    return {
        "grid": [SIZE, SIZE],
        "fixed_conservation_leaf": True,
        "degree": DEGREE,
        "obstruction_aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
        "obstruction_counts": list(EXPECTED_OBSTRUCTION_COUNTS),
        "obstruction_targets": list(EXPECTED_OBSTRUCTION_TARGETS),
        "q011aj_artifact_sha256": Q011AJ_ARTIFACT_SHA256,
        "q011aj_runner_sha256": Q011AJ_RUNNER_SHA256,
        "radius_record_digest_sha256": EXPECTED_RADIUS_RECORD_DIGEST,
        "blockwise_record_digest_sha256": EXPECTED_BLOCKWISE_RECORD_DIGEST,
        "block_zero_histogram_digest_sha256": EXPECTED_BLOCK_ZERO_HISTOGRAM_DIGEST,
        "minimum_separated_witness_digest_sha256": (
            EXPECTED_MINIMUM_SEPARATED_WITNESS_DIGEST
        ),
        "first_unresolved_witness_digest_sha256": (
            EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST
        ),
        "obstruction_record_digest_sha256": EXPECTED_OBSTRUCTION_RECORD_DIGEST,
        "blockwise_certificate_rejected_classification": (
            BLOCKWISE_CERTIFICATE_REJECTED_CLASSIFICATION
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


def run_degree16_blockwise_obstruction_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    obstruction_input, selected_groups, target_group = (
        _registered_obstruction_input_audit(artifacts)
    )
    envelope, lookup, theta = _blockwise_envelope_audit(
        artifacts, selected_groups
    )
    compression, classes = _compression_audit(selected_groups, lookup, theta)
    obstruction = _blockwise_obstruction_audit(classes, lookup, target_group)

    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    radius_sections = {
        "blockwise_transformed_residual_radius_audit": {
            "radius_formula": envelope["radius_formula"],
            "radius_records": envelope["radius_records"],
            "radius_record_digest_sha256": envelope["radius_record_digest_sha256"],
            "active_radius_binary64_hex": envelope["active_radius_binary64_hex"],
            "checks": {
                key: value
                for key, value in envelope["checks"].items()
                if "radius" in key
                or key
                in {
                    "q011l_reconstructs_all_seventeen_blocks",
                    "conjugate_block_radii_transport_exactly",
                }
            },
        }
    }
    interval_sections = {
        "registered_obstruction_input_audit": obstruction_input,
        "blockwise_transformed_residual_envelope_audit": {
            key: value
            for key, value in envelope.items()
            if key not in {"radius_records", "radius_record_digest_sha256"}
        },
        "blockwise_fourier_modulus_compression_audit": compression,
    }
    obstruction_sections = {"registered_blockwise_obstruction_audit": obstruction}
    input_digest = q011b._canonical_json_sha256(input_sections)
    radius_digest = q011b._canonical_json_sha256(radius_sections)
    interval_digest = q011b._canonical_json_sha256(interval_sections)
    obstruction_digest = q011b._canonical_json_sha256(obstruction_sections)
    strict_payload = {
        **input_sections,
        **radius_sections,
        **interval_sections,
        **obstruction_sections,
        "runner_source": runner,
    }
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and radius_digest == q011b._canonical_json_sha256(radius_sections)
        and interval_digest == q011b._canonical_json_sha256(interval_sections)
        and obstruction_digest == q011b._canonical_json_sha256(obstruction_sections)
    )
    obstruction_record = obstruction["registered_obstruction_record"]
    unresolved_width = q011z._fraction(
        obstruction_record["first_unresolved_witness"]["intersection_interval"][
            "width"
        ]
    )
    validity_gates = {
        "fifteen_artifacts_seventy_eight_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad/ae/af/ag/ah/ai/aj artifacts, "
                "runners, 78 digests, outcomes, boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "seventeen_exact_block_radii_and_conjugate_transport_reproduce": {
            "passed": bool(
                envelope["checks"]["all_seventeen_theta_identities_are_exact_and_positive"]
                and envelope["checks"]["conjugate_block_radii_transport_exactly"]
                and envelope["checks"]["registered_seventeen_radius_records_reproduce"]
            ),
            "threshold": "17 exact theta records, conjugate transport and the radius digest",
            "value": envelope["active_radius_binary64_hex"],
        },
        "two_hundred_four_blockwise_intervals_and_containment_reproduce": {
            "passed": bool(envelope["passed"] and obstruction_input["passed"]),
            "threshold": (
                "204 blockwise intervals are contained in the Q011aj uniform "
                "and Q011k eigendiscs"
            ),
            "value": envelope["checks"],
        },
        "modulus_classes_radii_and_outward_arithmetic_reproduce": {
            "passed": bool(
                compression["passed"]
                and obstruction["checks"][
                    "all_outward_arrays_are_finite_nonnegative_and_ordered"
                ]
                and obstruction["checks"]["fourier_int64_bound_is_safe"]
            ),
            "threshold": (
                "4/2/3/6 classes have constant exact radii and outward finite "
                "nonoverflowing arithmetic"
            ),
            "value": compression["checks"],
        },
        "registered_obstruction_counts_relations_and_digest_reproduce": {
            "passed": bool(
                obstruction["checks"][
                    "registered_signature_and_fourier_counts_reproduce"
                ]
                and obstruction["checks"][
                    "registered_blockwise_relation_counts_reproduce"
                ]
                and obstruction["checks"][
                    "registered_aggregate_record_digest_reproduces"
                ]
            ),
            "threshold": (
                "all signature, monomial, comparison, relation counts and the "
                "registered aggregate digest reproduce"
            ),
            "value": obstruction_record["distinct_relation_counts"],
        },
        "block_zero_histogram_and_registered_boundary_reproduce": {
            "passed": obstruction["checks"][
                "registered_block_zero_histogram_and_boundary_reproduce"
            ],
            "threshold": "multiplicities 0/1 separate and 2--5 overlap",
            "value": obstruction_record["block_zero_multiplicity_histogram"],
        },
        "both_witnesses_serialization_digests_and_provenance_reproduce": {
            "passed": bool(
                obstruction["checks"][
                    "minimum_separated_outward_witness_reproduces"
                ]
                and obstruction["checks"][
                    "first_unresolved_exact_witness_reproduces"
                ]
                and strict_json
                and digests_reproduce
            ),
            "threshold": (
                "both registered witnesses, strict JSON, section digests and "
                "runner provenance reproduce"
            ),
            "value": {
                "minimum_separated_witness_digest": obstruction_record[
                    "minimum_separated_outward_witness_digest_sha256"
                ],
                "first_unresolved_witness_digest": obstruction_record[
                    "first_unresolved_witness_digest_sha256"
                ],
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "blockwise_eigendiscs_are_spectrally_valid_and_contained": {
            "passed": bool(validity_passed and envelope["passed"]),
            "threshold": "Q011y blockwise discs subset uniform discs subset Q011k discs",
            "value": envelope["checks"],
        },
        "all_registered_comparisons_are_classified_exactly_once": {
            "passed": bool(
                validity_passed
                and sum(obstruction_record["distinct_relation_counts"].values())
                == EXPECTED_DISTINCT_COMPARISON_COUNT
                and sum(obstruction_record["weighted_relation_counts"].values())
                == EXPECTED_WEIGHTED_COMPARISON_COUNT
            ),
            "threshold": "141120 distinct and 3465728 weighted comparisons",
            "value": {
                "distinct": obstruction_record["distinct_relation_counts"],
                "weighted": obstruction_record["weighted_relation_counts"],
            },
        },
        "fifteen_thousand_six_hundred_eighty_comparisons_separate": {
            "passed": bool(
                validity_passed
                and obstruction_record["distinct_relation_counts"][
                    "product_below_target"
                ]
                == 15_680
                and obstruction_record["minimum_separated_outward_witness"][
                    "outward_gap_hex"
                ]
                == EXPECTED_MINIMUM_SEPARATED_GAP_HEX
            ),
            "threshold": "15680 distinct comparisons have a positive outward gap",
            "value": obstruction_record["minimum_separated_outward_witness"],
        },
        "one_hundred_twenty_five_thousand_four_hundred_forty_comparisons_overlap": {
            "passed": bool(
                validity_passed
                and obstruction_record["distinct_relation_counts"]["overlap"]
                == 125_440
            ),
            "threshold": "125440 distinct comparisons remain interval overlaps",
            "value": obstruction_record["distinct_relation_counts"],
        },
        "block_zero_multiplicity_boundary_reproduces": {
            "passed": bool(
                validity_passed
                and obstruction["checks"][
                    "registered_block_zero_histogram_and_boundary_reproduce"
                ]
            ),
            "threshold": "block-zero multiplicities 0/1 separate and 2--5 overlap",
            "value": obstruction_record["block_zero_multiplicity_histogram"],
        },
        "first_unresolved_exact_intersection_is_positive": {
            "passed": bool(
                validity_passed
                and unresolved_width > 0
                and obstruction["checks"][
                    "first_unresolved_exact_witness_reproduces"
                ]
            ),
            "threshold": "the registered exact blockwise interval intersection is positive",
            "value": obstruction_record["first_unresolved_witness"][
                "intersection_interval"
            ],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed or not hypotheses_passed:
        hypothesis_outcome = "inconclusive"
        actual_resonance_outcome = "inconclusive"
        classification = "registered Q011ak blockwise obstruction audit is invalid"
    else:
        hypothesis_outcome = "rejected"
        actual_resonance_outcome = "not_established"
        classification = COMBINED_CLASSIFICATION
    cycle: dict[str, Any] = {
        "question": (
            "Do the Q011y blockwise transformed-residual radii clear the "
            "registered degree-sixteen obstruction?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "radius_digest_sha256": radius_digest,
        "interval_digest_sha256": interval_digest,
        "obstruction_digest_sha256": obstruction_digest,
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
        "q011y_blockwise_transformed_residual_enclosure_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "blockwise_radius_strictly_improves_the_registered_uniform_obstruction": (
            registered_rejection
        ),
        "degree_sixteen_blockwise_radius_certificate_is_rejected_at_the_registered_obstruction": (
            registered_rejection
        ),
        "block_zero_multiplicity_boundary_is_certified_for_this_aggregate": (
            registered_rejection
        ),
        "remaining_blockwise_overlaps_are_actual_resonances": False,
        "an_actual_degree_sixteen_complex_resonance_is_established": False,
        "degree_sixteen_external_nonresonance_is_certified": False,
        "certified_external_nonresonance_degrees": list(range(2, 16)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(16, 91)),
        "degrees_16_through_90_are_certified": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011aj_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the Q011aj aggregate-index-99 obstruction at "
        "degree sixteen for the fixed 17x17 repaired exact map on one fixed "
        "conservation leaf, the Q011y blockwise transformed-residual radii, exact "
        "x-Fourier multiplicities and outward-rounded dyadic product enclosures. "
        "Remaining enclosure overlap is not an actual complex resonance. It "
        "establishes no result for the other degree-sixteen aggregates, degree-sixteen "
        "external nonresonance, degrees 17 through 90, all-order nonresonance, higher "
        "graph smoothness, SSM existence or uniqueness, normal attraction, basin, "
        "other grid, force, wall or D3Q27 setting."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ai_certificates_and_diagnostics_changed": False,
        "q011aj_uniform_obstruction_outcome_changed": False,
    }
    if registered_rejection:
        cycle["next_change"] = (
            "Preregister Q011al to focus on the block-zero-containing unresolved "
            "fibers and test identifier- or eigenpair-specific contained eigendiscs "
            "in place of the block-common theta_0 radius."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first seal, radius, interval, class, Fourier, histogram, "
            "witness or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ak cycle failed strict serialization or digest")
    return cycle


def run_q011ak_study() -> dict[str, Any]:
    cycle = run_degree16_blockwise_obstruction_audit()
    obstruction = cycle["registered_blockwise_obstruction_audit"]
    record = obstruction["registered_obstruction_record"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_input_scalar_type": "fractions.Fraction",
            "proof_enclosure_type": "outward-rounded IEEE-754 binary64",
            "fourier_coefficient_type": "numpy.int64 with checked crude bound",
            "floating_point_used_for_gate_decisions": True,
            "floating_point_gate_is_rigorous_interval_logic": True,
            "registered_weighted_comparison_count": record[
                "weighted_comparison_count"
            ],
            "registered_distinct_comparison_count": record[
                "distinct_comparison_count"
            ],
            "exact_record_storage": (
                "17 exact block radii, 204 exact blockwise interval records, an exact "
                "block-zero histogram and two exact source/target witnesses"
            ),
        },
        "mathematical_scope": {
            "diagnostic": "degree-sixteen registered-obstruction blockwise-radius re-audit",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "aggregate_index": OBSTRUCTION_AGGREGATE_INDEX,
            "blockwise_radius_certificate_claim": False,
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
    result = run_q011ak_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
