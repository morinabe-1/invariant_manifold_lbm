"""Q011ch component-safe complex phase discs for Q011cb flatten ordinal two."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

import research.q011ca_degree34_component_safe_phase_discs as q011ca
import research.q011cf_degree34_next_component_safe_phase_discs as q011cf
import research.q011cg_degree34_third_individual_partition_audit as q011cg
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011cg.q011b
q011z = q011cg.q011z
q011o = q011ca.q011o

ExactComplex = tuple[Fraction, Fraction]
_ExactDisc = q011cf._ExactDisc
_FramedRecordDigest = q011cf._FramedRecordDigest

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
PARENT_FLAT_ORDINAL = 2
OUTPUT_BLOCK = 7
TARGET_IDENTIFIER = "block=7;center=44"

SOURCE_VARIANTS = q011cf.SOURCE_VARIANTS
EXPECTED_SOURCE_RADIUS_HEX = q011cf.EXPECTED_SOURCE_RADIUS_HEX
EXPECTED_TARGET_RADIUS_HEX = q011cf.EXPECTED_TARGET_RADIUS_HEX
EXPECTED_SOURCE_RECORD_DIGEST = q011cf.EXPECTED_SOURCE_RECORD_DIGEST
EXPECTED_TARGET_RECORD_DIGEST = q011cf.EXPECTED_TARGET_RECORD_DIGEST

EXPECTED_FULL_ALLOCATION_COUNT = 332_640
EXPECTED_COMPATIBLE_ALLOCATION_COUNT = 18_718
EXPECTED_WAVE_PROJECTION_COUNT = 852
EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT = 10
EXPECTED_FULL_ALLOCATION_DIGEST = (
    "3ec75e818c2fddf04cf9f6a9ea6847553ab6fd6dbd0d58088631923e9f647619"
)
EXPECTED_COMPATIBLE_ALLOCATION_DIGEST = (
    "bdcbb44f66d1d0dbcd818dbf280ef60f762d29528932875d25f60d03ab168671"
)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 13, 0, 0, 0, 9, 0, 5, 0, 2, 5, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = (13, 0, 9, 0, 0, 0, 0, 5, 0, 2, 0, 5)
EXPECTED_WAVE_PROJECTION_DIGEST = (
    "629cf594b5adbb8f10c66daf11f6bff80d91c667a7d4f641f164a804ca96e5e2"
)
EXPECTED_PHASE_FIBER_HISTOGRAM = {10: 173, 18: 169, 24: 169, 28: 170, 30: 171}

Q011CG_ARTIFACT_SHA256 = "ba8189bc52e59644298b9e9587d7468c5035f861667b9e2847522b9e4ce4d32e"
Q011CG_RUNNER_SHA256 = "2b3891a48840d62fa227a95aa6ed13e102056751d59ac969bc9e5a73d9e98600"
Q011CG_DIGEST_NAMES = (
    "input_digest_sha256",
    "partition_input_digest_sha256",
    "allocation_audit_digest_sha256",
    "result_digest_sha256",
)
Q011CG_DIGESTS = (
    "3a9bf134093d72dfa3a9fce972eea9213f5d2221c8a96796849dc714efd16e04",
    "b675a240f2d7d8ec553ba905dc69104d1ab580cd7ad582044e62be4bc31bee38",
    "30167e3024dc9dd61b70a72bc45426cc702ac47d251954ecf68f8a19532a0f88",
    "f99176bee9bec4e82530ce33227a1950949986f83112f5eca9cd917b03af1d15",
)
EXPECTED_Q011CG_ALLOCATION_RECORD_DIGEST = (
    "b3b578822153dac0f180c7a341aeb744bcd054ac680de3cac336a19c03fedc87"
)

RESOLVED_CLASSIFICATION = (
    "the component-safe complex phase discs resolve the third Q011cb persistent "
    "refined witness"
)
PERSISTENT_CLASSIFICATION = (
    "the third Q011cb persistent refined witness persists under component-safe "
    "complex phase discs"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011ch component-safe phase-disc audit is inconclusive"


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


_fraction_record = q011cf._fraction_record
_complex_record = q011cf._complex_record
_interval_record = q011cf._interval_record
_signed_fraction_record = q011cf._signed_fraction_record
_exact_fraction_sha256 = q011cf._exact_fraction_sha256
_exact_complex_sha256 = q011cf._exact_complex_sha256
_exact_interval_sha256 = q011cf._exact_interval_sha256
_exact_fraction_sequence_sha256 = q011cf._exact_fraction_sequence_sha256
_product_modulus_expression_sha256 = q011cf._product_modulus_expression_sha256


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011cg._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011cg_degree34_third_individual_partition_audit.json"
    )
    runner_path = Path(q011cg.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    fixed = cycle["fixed_individual_partition_input_audit"]
    partition = cycle["individual_allocation_interval_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011CG_DIGEST_NAMES)
    checks = {
        "q011cg_sixty_three_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 63
            and prior["direct_digest_count"] == 296
            and len(artifacts) == 63
            and all(prior["checks"].values())
        ),
        "q011cg_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011CG_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011CG_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011CG_RUNNER_SHA256
        ),
        "q011cg_section_digests_match": digests == Q011CG_DIGESTS,
        "q011cg_valid_interval_inert_outcome_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "partition_inert_persistent"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "individual_partition_is_interval_inert_for_third_q011cb_witness"
            ]
            and theorem["q011cf_ordinal_one_phase_resolution_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011cg_parent_partition_and_relations_reproduce": bool(
            fixed["third_parent_witness_selection_audit"]["selected_flat_ordinal"]
            == PARENT_FLAT_ORDINAL
            and fixed["compatible_allocation_count"] == EXPECTED_WAVE_PROJECTION_COUNT
            and fixed["compatible_allocation_digest_sha256"]
            == q011cg.EXPECTED_COMPATIBLE_DIGEST
            and partition["compatible_allocation_count"]
            == EXPECTED_WAVE_PROJECTION_COUNT
            and partition["exact_relation_counts"]
            == {
                "product_below_target": 0,
                "target_below_product": 0,
                "overlap": EXPECTED_WAVE_PROJECTION_COUNT,
            }
            and partition[
                "all_product_target_intersection_and_center_records_equal_parent"
            ]
            and partition["allocation_classification_record_digest_sha256"]
            == EXPECTED_Q011CG_ALLOCATION_RECORD_DIGEST
        ),
        "q011cg_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "three_hundred_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 300
        ),
    }
    artifacts["q011cg"] = artifact
    return (
        {
            "prior_q011cg_sealed_input_audit": prior,
            "q011cg": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011CG_DIGEST_NAMES),
                "digests": list(digests),
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _fixed_phase_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[_ExactDisc, ...],
    _ExactDisc,
    tuple[dict[str, Any], ...],
]:
    fixed, lookup, wave_compatible, parent = q011cg._fixed_individual_input_audit(
        artifacts
    )
    partition = q011cg._individual_partition_audit(lookup, wave_compatible, parent)
    stored = artifacts["q011cg"]["cycle"]
    centers, _, _, _, reconstruction = q011z.q011l._spectral_data(artifacts["q011k"])
    q011an_envelope = artifacts["q011an"]["cycle"]["component_safe_envelope_audit"]
    q011an_records = {
        record["identifier"]: record
        for record in q011an_envelope["component_safe_records"]
    }
    q011ak_envelope = artifacts["q011ak"]["cycle"][
        "blockwise_transformed_residual_envelope_audit"
    ]
    q011ak_records = {
        record["identifier"]: record
        for record in q011ak_envelope["blockwise_disc_records"]
    }
    radii = q011ca._radius_by_block(artifacts)
    source_discs = []
    source_records = []
    for identifier, radius_kind in SOURCE_VARIANTS:
        block, center_index = q011z._identifier_indices(identifier)
        source = q011an_records[identifier]
        radius = (
            q011z._fraction(source["row_radius_upper"])
            if radius_kind == "q011an_row"
            else radii[block]
        )
        component = (
            tuple(source["gershgorin_component_center_indices"])
            if radius_kind == "q011an_row"
            else None
        )
        disc = _ExactDisc(
            identifier=identifier,
            block_index=block,
            center_index=center_index,
            center=centers[block][center_index],
            radius_kind=radius_kind,
            radius=radius,
            component=component,
        )
        source_discs.append(disc)
        source_records.append(
            {
                "identifier": identifier,
                "block_index": block,
                "center_index": center_index,
                "center": _complex_record(disc.center),
                "radius_kind": radius_kind,
                "radius": _fraction_record(radius),
                "gershgorin_component_center_indices": (
                    list(component) if component is not None else None
                ),
            }
        )
    target_block, target_center_index = q011z._identifier_indices(TARGET_IDENTIFIER)
    target = _ExactDisc(
        identifier=TARGET_IDENTIFIER,
        block_index=target_block,
        center_index=target_center_index,
        center=centers[target_block][target_center_index],
        radius_kind="q011ak_block",
        radius=radii[target_block],
        component=None,
    )
    target_record = {
        "identifier": TARGET_IDENTIFIER,
        "block_index": target.block_index,
        "center_index": target.center_index,
        "center": _complex_record(target.center),
        "radius_kind": target.radius_kind,
        "radius": _fraction_record(target.radius),
    }
    source_digest = q011b._canonical_json_sha256(source_records)
    target_digest = q011b._canonical_json_sha256(target_record)
    memberships = q011ca._component_memberships(artifacts["q011an"])
    expected_components = ((145,), (148,), (149,), (150, 151))
    row_discs = tuple(source_discs[:6] + source_discs[8:])
    block_discs = tuple(source_discs[6:8])
    target_center_modulus = q011o._center_modulus_bounds(target.center)
    target_expected_modulus = RationalInterval(
        max(Fraction(0), target_center_modulus.lower - target.radius),
        target_center_modulus.upper + target.radius,
    )
    conjugate_pairs = ((0, 1), (2, 4), (3, 5), (6, 7), (8, 9), (10, 11))
    checks = {
        "q011cg_fixed_parent_and_interval_partition_replay_bitwise": bool(
            fixed == stored["fixed_individual_partition_input_audit"]
            and partition == stored["individual_allocation_interval_audit"]
            and fixed["passed"]
            and partition["passed"]
        ),
        "q011k_centers_and_q011ak_block_radii_reconstruct": bool(
            reconstruction["passed"]
            and q011ak_envelope["passed"]
            and set(radii) == set(range(SIZE))
            and len(q011ak_envelope["blockwise_disc_records"]) == 204
        ),
        "registered_source_and_target_phase_records_reproduce": bool(
            tuple(float(disc.radius).hex() for disc in source_discs)
            == EXPECTED_SOURCE_RADIUS_HEX
            and float(target.radius).hex() == EXPECTED_TARGET_RADIUS_HEX
            and source_digest == EXPECTED_SOURCE_RECORD_DIGEST
            and target_digest == EXPECTED_TARGET_RECORD_DIGEST
        ),
        "active_singleton_and_two_row_components_have_exact_multiplicity": bool(
            memberships[1] == memberships[16]
            and all(component in memberships[1] for component in expected_components)
            and all(
                disc.component
                == (
                    (150, 151)
                    if disc.center_index in (150, 151)
                    else (disc.center_index,)
                )
                for disc in row_discs
            )
            and artifacts["q011an"]["cycle"]["active_block_structured_row_audit"][
                "passed"
            ]
        ),
        "row_discs_are_contained_in_q011am_and_q011ak": bool(
            q011an_envelope["passed"]
            and all(
                q011an_records[disc.identifier][
                    "contained_in_q011am_hybrid_interval"
                ]
                and q011an_records[disc.identifier][
                    "contained_in_q011ak_blockwise_interval"
                ]
                for disc in row_discs
            )
        ),
        "block_discs_and_target_replay_the_q011ak_formula": bool(
            all(
                disc.identifier in q011ak_records
                and q011z._fraction(
                    q011ak_records[disc.identifier][
                        "transformed_residual_radius_upper"
                    ]
                )
                == disc.radius
                for disc in block_discs
            )
            and lookup[TARGET_IDENTIFIER].center_modulus == target_center_modulus
            and lookup[TARGET_IDENTIFIER].modulus == target_expected_modulus
        ),
        "all_conjugate_source_pairs_transport_exactly": all(
            source_discs[left].center
            == (source_discs[right].center[0], -source_discs[right].center[1])
            and source_discs[left].radius == source_discs[right].radius
            and source_discs[left].component == source_discs[right].component
            for left, right in conjugate_pairs
        ),
        "component_union_semantics_do_not_assign_internal_labels": bool(
            source_discs[2].component
            == source_discs[3].component
            == source_discs[4].component
            == source_discs[5].component
            == (150, 151)
        ),
        "fixed_phase_input_is_finite_strict_json": bool(
            _all_numeric_values_finite(source_records)
            and _strict_json_serializable(source_records)
            and json.dumps(
                {"sources": source_records, "target": target_record},
                allow_nan=False,
            )
        ),
    }
    audit = {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "target_identifier": TARGET_IDENTIFIER,
        "source_variant_count": len(source_discs),
        "source_phase_disc_records": source_records,
        "source_phase_disc_record_digest_sha256": source_digest,
        "source_radius_binary64_hex": [
            float(disc.radius).hex() for disc in source_discs
        ],
        "target_phase_disc_record": target_record,
        "target_phase_disc_record_digest_sha256": target_digest,
        "target_radius_binary64_hex": float(target.radius).hex(),
        "active_component_memberships_by_block": {
            str(block): [list(component) for component in memberships[block]]
            for block in (1, 16)
        },
        "q011cg_compatible_wave_allocation_count": len(wave_compatible),
        "q011cg_compatible_wave_allocation_digest_sha256": fixed[
            "compatible_allocation_digest_sha256"
        ],
        "label_semantics": (
            "each factor independently selects a row disc from its isolated component "
            "union; no component-internal eigenvalue label is assigned"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, tuple(source_discs), target, wave_compatible


def _allocation_inventory(
    source_discs: tuple[_ExactDisc, ...],
    wave_compatible: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    records = []
    for count_16_145 in range(14):
        for count_16_150 in range(10):
            for count_16_151 in range(10 - count_16_150):
                for count_1_150 in range(10 - count_16_150 - count_16_151):
                    count_1_151 = 9 - count_16_150 - count_16_151 - count_1_150
                    for count_16_152 in range(6):
                        for count_16_148 in range(3):
                            for count_16_149 in range(6):
                                counts = [
                                    count_16_145,
                                    13 - count_16_145,
                                    count_16_150,
                                    count_16_151,
                                    count_1_150,
                                    count_1_151,
                                    count_16_152,
                                    5 - count_16_152,
                                    count_16_148,
                                    2 - count_16_148,
                                    count_16_149,
                                    5 - count_16_149,
                                ]
                                output_block = (
                                    sum(
                                        count * disc.block_index
                                        for count, disc in zip(
                                            counts,
                                            source_discs,
                                            strict=True,
                                        )
                                    )
                                    % SIZE
                                )
                                records.append(
                                    {
                                        "counts": counts,
                                        "output_block": output_block,
                                        "compatible": output_block == OUTPUT_BLOCK,
                                    }
                                )
    compatible = tuple(record for record in records if record["compatible"])
    projection = Counter(
        (
            record["counts"][0],
            record["counts"][1],
            record["counts"][2] + record["counts"][3],
            record["counts"][4] + record["counts"][5],
            record["counts"][6],
            record["counts"][7],
            record["counts"][8],
            record["counts"][9],
            record["counts"][10],
            record["counts"][11],
        )
        for record in compatible
    )
    projection_records = [
        {"wave_counts": list(counts), "phase_allocation_count": projection[counts]}
        for counts in sorted(projection)
    ]
    wave_counts = {tuple(record["individual_counts"]) for record in wave_compatible}
    fiber_histogram = dict(sorted(Counter(projection.values()).items()))
    full_digest = q011b._canonical_json_sha256(records)
    compatible_digest = q011b._canonical_json_sha256(list(compatible))
    projection_digest = q011b._canonical_json_sha256(projection_records)
    checks = {
        "full_component_safe_allocation_inventory_reproduces": bool(
            len(records) == EXPECTED_FULL_ALLOCATION_COUNT
            and full_digest == EXPECTED_FULL_ALLOCATION_DIGEST
        ),
        "compatible_component_safe_allocation_inventory_reproduces": bool(
            len(compatible) == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            and compatible_digest == EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
            and tuple(compatible[0]["counts"]) == EXPECTED_FIRST_COMPATIBLE_COUNTS
            and tuple(compatible[-1]["counts"]) == EXPECTED_LAST_COMPATIBLE_COUNTS
        ),
        "all_count_degree_and_wave_constraints_close": all(
            sum(record["counts"]) == DEGREE
            and record["counts"][0] + record["counts"][1] == 13
            and sum(record["counts"][2:6]) == 9
            and record["counts"][6] + record["counts"][7] == 5
            and record["counts"][8] + record["counts"][9] == 2
            and record["counts"][10] + record["counts"][11] == 5
            and all(count >= 0 for count in record["counts"])
            and record["output_block"] == OUTPUT_BLOCK
            for record in compatible
        ),
        "projection_matches_all_q011cg_wave_allocations": bool(
            set(projection) == wave_counts
            and len(projection) == len(wave_counts) == EXPECTED_WAVE_PROJECTION_COUNT
            and projection_digest == EXPECTED_WAVE_PROJECTION_DIGEST
        ),
        "all_phase_fibers_are_nonempty_and_registered": bool(
            min(projection.values()) == 10
            and max(projection.values()) == 30
            and sum(projection.values()) == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            and fiber_histogram == EXPECTED_PHASE_FIBER_HISTOGRAM
        ),
        "allocation_summary_is_finite_strict_json": bool(
            _all_numeric_values_finite(projection_records)
            and _strict_json_serializable(projection_records)
            and json.dumps(projection_records, allow_nan=False)
        ),
    }
    audit = {
        "source_variant_order": [disc.identifier for disc in source_discs],
        "full_allocation_count": len(records),
        "full_allocation_digest_sha256": full_digest,
        "compatible_allocation_count": len(compatible),
        "compatible_allocation_digest_sha256": compatible_digest,
        "first_compatible_counts": compatible[0]["counts"],
        "last_compatible_counts": compatible[-1]["counts"],
        "wave_projection_count": len(projection_records),
        "wave_projection_records": projection_records,
        "wave_projection_record_digest_sha256": projection_digest,
        "minimum_phase_allocations_per_wave": min(projection.values()),
        "maximum_phase_allocations_per_wave": max(projection.values()),
        "phase_allocation_count_per_wave_histogram": {
            str(count): frequency for count, frequency in fiber_histogram.items()
        },
        "full_allocation_records_retained": False,
        "compatible_allocation_records_retained": False,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, compatible


def _power_tables(
    center_uppers: tuple[Fraction, ...],
    source_discs: tuple[_ExactDisc, ...],
) -> tuple[
    tuple[tuple[ExactComplex, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    tuple[tuple[Fraction, ...], ...],
    bool,
]:
    maximum_counts = (13, 13, 9, 9, 9, 9, 5, 5, 2, 2, 5, 5)
    center_powers = []
    upper_powers = []
    full_powers = []
    radius_powers = []
    recurrence_checks = []
    for upper, disc, maximum in zip(
        center_uppers,
        source_discs,
        maximum_counts,
        strict=True,
    ):
        disc_center_powers = []
        disc_upper_powers = []
        disc_full_powers = []
        disc_radius_powers = []
        recurrence_center = Fraction(1)
        recurrence_radius = Fraction(0)
        for count in range(maximum + 1):
            center_power = q011ca._complex_power(disc.center, count)
            upper_power = upper**count
            full_power = (upper + disc.radius) ** count
            closed_radius = full_power - upper_power
            if count:
                recurrence_radius = (
                    recurrence_center * disc.radius
                    + upper * recurrence_radius
                    + recurrence_radius * disc.radius
                )
                recurrence_center *= upper
            recurrence_checks.append(
                recurrence_center == upper_power and recurrence_radius == closed_radius
            )
            disc_center_powers.append(center_power)
            disc_upper_powers.append(upper_power)
            disc_full_powers.append(full_power)
            disc_radius_powers.append(recurrence_radius)
        center_powers.append(tuple(disc_center_powers))
        upper_powers.append(tuple(disc_upper_powers))
        full_powers.append(tuple(disc_full_powers))
        radius_powers.append(tuple(disc_radius_powers))
    return (
        tuple(center_powers),
        tuple(upper_powers),
        tuple(full_powers),
        tuple(radius_powers),
        all(recurrence_checks),
    )


def _phase_product_audit(
    source_discs: tuple[_ExactDisc, ...],
    target: _ExactDisc,
    compatible: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    source_center_moduli = tuple(
        q011o._center_modulus_bounds(disc.center) for disc in source_discs
    )
    center_uppers = tuple(interval.upper for interval in source_center_moduli)
    (
        center_powers,
        upper_powers,
        full_powers,
        radius_powers,
        power_table_recurrences_exact,
    ) = _power_tables(center_uppers, source_discs)
    target_center_modulus = q011o._center_modulus_bounds(target.center)
    target_modulus = RationalInterval(
        max(Fraction(0), target_center_modulus.lower - target.radius),
        target_center_modulus.upper + target.radius,
    )
    stream = _FramedRecordDigest("q011ch-component-safe-phase-comparisons-v1")
    categories: Counter[str] = Counter()
    individual_relations: Counter[str] = Counter()
    all_radius_recurrences_equal = True
    all_square_root_enclosures_hold = True
    all_product_intervals_ordered = True
    all_separated_margins_positive = True
    radius_cache: dict[
        tuple[int, int, int, int, int, int], tuple[Fraction, Fraction]
    ] = {}
    radius_digest_cache: dict[tuple[int, int, int, int, int, int], str] = {}
    radius_bound_cache: dict[
        tuple[int, int, int, int, int, int],
        tuple[Fraction, Fraction, Fraction],
    ] = {}
    first_unresolved: tuple[Any, ...] | None = None
    minimum_distance_by_radius: dict[
        tuple[int, int, int, int, int, int],
        tuple[tuple[Any, ...], tuple[Any, ...]],
    ] = {}
    minimum_separated_distance_by_radius: dict[
        tuple[int, int, int, int, int, int],
        tuple[tuple[Any, ...], tuple[Any, ...]],
    ] = {}

    for index, allocation in enumerate(compatible):
        counts = allocation["counts"]
        product_center = q011cf._cached_product_center(counts, center_powers)
        radius_signature = (
            counts[0] + counts[1],
            counts[2] + counts[4],
            counts[3] + counts[5],
            counts[6] + counts[7],
            counts[8] + counts[9],
            counts[10] + counts[11],
        )
        if radius_signature not in radius_cache:
            radius_cache[radius_signature] = q011cf._cached_product_radius(
                radius_signature,
                upper_powers,
                full_powers,
                radius_powers,
            )
            radius_digest_cache[radius_signature] = _exact_fraction_sha256(
                radius_cache[radius_signature][0]
            )
            radius = radius_cache[radius_signature][0]
            radius_bound_cache[radius_signature] = (
                radius + target.radius,
                target_modulus.lower - radius,
                target_modulus.upper + radius,
            )
        product_radius, recurrence_radius = radius_cache[radius_signature]
        combined_radius, product_below_threshold, target_below_threshold = (
            radius_bound_cache[radius_signature]
        )
        all_radius_recurrences_equal = bool(
            all_radius_recurrences_equal and product_radius == recurrence_radius
        )
        center_modulus = q011o._center_modulus_bounds(product_center)
        difference = (
            product_center[0] - target.center[0],
            product_center[1] - target.center[1],
        )
        center_distance = q011o._center_modulus_bounds(difference)
        squared_distance = difference[0] ** 2 + difference[1] ** 2
        all_square_root_enclosures_hold = bool(
            all_square_root_enclosures_hold
            and center_modulus.lower**2
            <= product_center[0] ** 2 + product_center[1] ** 2
            <= center_modulus.upper**2
            and center_distance.lower**2 <= squared_distance <= center_distance.upper**2
        )
        all_product_intervals_ordered = bool(
            all_product_intervals_ordered
            and product_radius >= 0
            and center_modulus.lower <= center_modulus.upper
        )
        if center_modulus.upper < product_below_threshold:
            individual_relation = "product_below_target"
        elif target_below_threshold < center_modulus.lower:
            individual_relation = "target_below_product"
        else:
            individual_relation = "overlap"
        if center_distance.lower > combined_radius:
            margin_sign = 1
        elif center_distance.lower == combined_radius:
            margin_sign = 0
        else:
            margin_sign = -1
        margin_positive = margin_sign > 0
        if individual_relation != "overlap":
            classification = "individual_modulus_separation"
        elif margin_positive:
            classification = "complex_phase_separation"
        else:
            classification = "unresolved_product_disk_overlap"
        all_separated_margins_positive = bool(
            all_separated_margins_positive
            and (classification == "unresolved_product_disk_overlap" or margin_positive)
        )
        categories[classification] += 1
        individual_relations[individual_relation] += 1
        exact_digests = {
            "product_center_digest_sha256": _exact_complex_sha256(product_center),
            "product_radius_digest_sha256": radius_digest_cache[radius_signature],
            "product_center_modulus_digest_sha256": _exact_interval_sha256(
                center_modulus
            ),
            "product_modulus_expression_digest_sha256": (
                _product_modulus_expression_sha256(center_modulus, product_radius)
            ),
            "center_distance_digest_sha256": _exact_interval_sha256(center_distance),
            "complex_margin_expression_digest_sha256": (
                _exact_fraction_sequence_sha256(
                    b"q011ch-complex-margin-expression-v1",
                    (center_distance.lower, product_radius, target.radius),
                )
            ),
        }
        stream_record = {
            "compatible_allocation_index": index,
            "counts": counts,
            "degree": sum(counts),
            "output_block": allocation["output_block"],
            **exact_digests,
            "complex_margin_sign": margin_sign,
            "individual_modulus_relation": individual_relation,
            "classification": classification,
        }
        stream.update(stream_record)
        witness_data = (
            index,
            allocation,
            product_center,
            product_radius,
            center_modulus,
            target,
            target_modulus,
            center_distance,
            individual_relation,
            classification,
        )
        distance_key = (center_distance.lower, tuple(counts), index)
        current = minimum_distance_by_radius.get(radius_signature)
        if current is None or distance_key < current[0]:
            minimum_distance_by_radius[radius_signature] = (
                distance_key,
                witness_data,
            )
        if classification != "unresolved_product_disk_overlap":
            separated = minimum_separated_distance_by_radius.get(radius_signature)
            if separated is None or distance_key < separated[0]:
                minimum_separated_distance_by_radius[radius_signature] = (
                    distance_key,
                    witness_data,
                )
        elif first_unresolved is None:
            first_unresolved = witness_data

    if not minimum_distance_by_radius:
        raise RuntimeError("Q011ch has no compatible phase allocation")
    global_minimum_data = min(
        (record[1] for record in minimum_distance_by_radius.values()),
        key=lambda data: (
            q011cf._comparison_margin(data),
            tuple(data[1]["counts"]),
            data[0],
        ),
    )
    global_minimum_witness = q011cf._materialize_comparison_witness(
        global_minimum_data
    )
    minimum_separated_data = (
        min(
            (record[1] for record in minimum_separated_distance_by_radius.values()),
            key=lambda data: (
                q011cf._comparison_margin(data),
                tuple(data[1]["counts"]),
                data[0],
            ),
        )
        if minimum_separated_distance_by_radius
        else None
    )
    minimum_separated_witness = (
        q011cf._materialize_comparison_witness(minimum_separated_data)
        if minimum_separated_data is not None
        else None
    )
    first_unresolved_witness = (
        q011cf._materialize_comparison_witness(first_unresolved)
        if first_unresolved is not None
        else None
    )
    category_counts = {
        name: categories[name]
        for name in (
            "individual_modulus_separation",
            "complex_phase_separation",
            "unresolved_product_disk_overlap",
        )
    }
    relation_counts = {
        name: individual_relations[name]
        for name in ("product_below_target", "target_below_product", "overlap")
    }
    checks = {
        "all_registered_phase_allocations_are_processed": bool(
            stream.count == len(compatible) == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
        ),
        "all_count_degree_and_output_constraints_close": all(
            sum(record["counts"]) == DEGREE
            and record["output_block"] == OUTPUT_BLOCK
            for record in compatible
        ),
        "closed_product_radius_equals_one_factor_recurrence_exactly": bool(
            power_table_recurrences_exact
            and all_radius_recurrences_equal
            and len(radius_cache) == EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT
        ),
        "all_center_and_distance_square_root_enclosures_hold": (
            all_square_root_enclosures_hold
        ),
        "all_product_discs_are_nonnegative_and_ordered": (
            all_product_intervals_ordered
        ),
        "classification_is_exclusive_complete_and_strict_when_separated": bool(
            sum(category_counts.values()) == len(compatible)
            and sum(relation_counts.values()) == len(compatible)
            and all_separated_margins_positive
        ),
        "stream_and_exact_witnesses_are_finite_strict_json": bool(
            stream.count == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            and len(stream.hexdigest()) == 64
            and _all_numeric_values_finite(global_minimum_witness)
            and _strict_json_serializable(global_minimum_witness)
            and json.dumps(
                {
                    "global_minimum": global_minimum_witness,
                    "minimum_separated": minimum_separated_witness,
                    "first_unresolved": first_unresolved_witness,
                },
                allow_nan=False,
            )
        ),
    }
    return {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "target_identifier": TARGET_IDENTIFIER,
        "compatible_phase_allocation_count": len(compatible),
        "category_counts": category_counts,
        "individual_modulus_relation_counts": relation_counts,
        "comparison_stream_domain": "q011ch-component-safe-phase-comparisons-v1",
        "comparison_stream_count": stream.count,
        "comparison_stream_digest_sha256": stream.hexdigest(),
        "unique_product_radius_count": len(radius_cache),
        "global_minimum_margin_witness": global_minimum_witness,
        "minimum_separated_witness": minimum_separated_witness,
        "first_unresolved_witness": first_unresolved_witness,
        "target_center_modulus_interval": _interval_record(target_center_modulus),
        "target_modulus_interval": _interval_record(target_modulus),
        "full_comparison_records_retained": False,
        "previous_q011cb_refined_signatures_recomputed": False,
        "later_q011cb_refined_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "other_parent_coalesced_overlaps_recomputed": False,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "output_block": OUTPUT_BLOCK,
        "target_identifier": TARGET_IDENTIFIER,
        "source_variants": [list(record) for record in SOURCE_VARIANTS],
        "full_component_safe_allocation_count": EXPECTED_FULL_ALLOCATION_COUNT,
        "compatible_component_safe_allocation_count": (
            EXPECTED_COMPATIBLE_ALLOCATION_COUNT
        ),
        "wave_projection_count": EXPECTED_WAVE_PROJECTION_COUNT,
        "unique_product_radius_count": EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT,
        "complex_product_radius_formula": (
            "prod(center_modulus_upper + radius)^count - "
            "prod(center_modulus_upper)^count"
        ),
        "previous_q011cb_refined_signatures_recomputed": False,
        "later_q011cb_refined_signatures_recomputed": False,
        "other_parent_targets_recomputed": False,
        "other_parent_coalesced_overlaps_recomputed": False,
        "degree_thirty_four_nonresonance_claimed": False,
        "actual_resonance_claimed": False,
        "all_order_nonresonance_claimed": False,
        "ssm_existence_or_uniqueness_claimed": False,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "input_digest_sha256": cycle["input_digest_sha256"],
        "phase_input_digest_sha256": cycle["phase_input_digest_sha256"],
        "allocation_digest_sha256": cycle["allocation_digest_sha256"],
        "phase_comparison_digest_sha256": cycle["phase_comparison_digest_sha256"],
        "validity_gates": cycle["validity_gates"],
        "diagnostic_gates": cycle["diagnostic_gates"],
        "study_validity": cycle["study_validity"],
        "refinement_outcome": cycle["refinement_outcome"],
        "diagnostic_classification": cycle["diagnostic_classification"],
        "scientific_outcome": cycle["scientific_outcome"],
        "actual_resonance_outcome": cycle["actual_resonance_outcome"],
    }


def run_degree_thirty_four_third_component_safe_phase_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    phase_input, source_discs, target, wave_compatible = _fixed_phase_input_audit(
        artifacts
    )
    allocation, compatible = _allocation_inventory(source_discs, wave_compatible)
    comparison = _phase_product_audit(source_discs, target, compatible)
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    phase_input_sections = {"fixed_component_safe_phase_input_audit": phase_input}
    allocation_sections = {"component_safe_phase_allocation_audit": allocation}
    comparison_sections = {"complex_phase_product_disc_audit": comparison}
    input_digest = q011b._canonical_json_sha256(input_sections)
    phase_input_digest = q011b._canonical_json_sha256(phase_input_sections)
    allocation_digest = q011b._canonical_json_sha256(allocation_sections)
    comparison_digest = q011b._canonical_json_sha256(comparison_sections)
    validity_gates = {
        "q011cg_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "64 artifacts and 300 direct digests reproduce",
            "value": sealed["checks"],
        },
        "q011cg_parent_partition_and_interval_inert_result_replay": {
            "passed": phase_input["checks"][
                "q011cg_fixed_parent_and_interval_partition_replay_bitwise"
            ],
            "threshold": "ordinal 2, 852 wave allocations and inert result replay",
            "value": phase_input[
                "q011cg_compatible_wave_allocation_digest_sha256"
            ],
        },
        "exact_centers_radii_components_and_target_reproduce": {
            "passed": bool(
                phase_input["checks"][
                    "q011k_centers_and_q011ak_block_radii_reconstruct"
                ]
                and phase_input["checks"][
                    "registered_source_and_target_phase_records_reproduce"
                ]
                and phase_input["checks"][
                    "active_singleton_and_two_row_components_have_exact_multiplicity"
                ]
            ),
            "threshold": "twelve source discs, one target and components reproduce",
            "value": {
                "source": phase_input["source_phase_disc_record_digest_sha256"],
                "target": phase_input["target_phase_disc_record_digest_sha256"],
            },
        },
        "containment_conjugacy_and_label_free_semantics_pass": {
            "passed": bool(
                phase_input["checks"][
                    "row_discs_are_contained_in_q011am_and_q011ak"
                ]
                and phase_input["checks"][
                    "block_discs_and_target_replay_the_q011ak_formula"
                ]
                and phase_input["checks"][
                    "all_conjugate_source_pairs_transport_exactly"
                ]
                and phase_input["checks"][
                    "component_union_semantics_do_not_assign_internal_labels"
                ]
            ),
            "threshold": "safe containment, six conjugate pairs and no internal labels",
            "value": phase_input["checks"],
        },
        "component_safe_allocation_and_wave_projection_reproduce": {
            "passed": allocation["passed"],
            "threshold": "332640 total, 18718 compatible and 852 nonempty wave fibers",
            "value": allocation["checks"],
        },
        "exact_product_radius_distance_and_categories_close": {
            "passed": comparison["passed"],
            "threshold": (
                "18718 exact products, ten radius signatures, sqrt enclosures and "
                "exclusive categories"
            ),
            "value": comparison["checks"],
        },
        "strict_stream_section_digests_and_runner_provenance_reproduce": {
            "passed": bool(
                comparison["comparison_stream_count"]
                == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
                and all(
                    len(value) == 64
                    for value in (
                        input_digest,
                        phase_input_digest,
                        allocation_digest,
                        comparison_digest,
                        comparison["comparison_stream_digest_sha256"],
                    )
                )
                and runner["filename"]
                == "q011ch_degree34_third_component_safe_phase_discs.py"
            ),
            "threshold": "framed stream, four section digests and runner metadata",
            "value": {
                "input": input_digest,
                "phase_input": phase_input_digest,
                "allocation": allocation_digest,
                "comparison": comparison_digest,
                "stream": comparison["comparison_stream_digest_sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    unresolved_count = comparison["category_counts"][
        "unresolved_product_disk_overlap"
    ]
    global_margin = q011z._fraction(
        comparison["global_minimum_margin_witness"][
            "complex_separation_margin_lower"
        ]["exact"]
    )
    resolved = validity_passed and unresolved_count == 0 and global_margin > 0
    persistent = validity_passed and not resolved
    diagnostic_gates = {
        "only_the_registered_third_q011cb_witness_is_refined": {
            "passed": bool(
                not comparison["previous_q011cb_refined_signatures_recomputed"]
                and not comparison["later_q011cb_refined_signatures_recomputed"]
                and not comparison["other_parent_targets_recomputed"]
                and not comparison["other_parent_coalesced_overlaps_recomputed"]
            ),
            "threshold": "ordinal 2 only, one target and no other overlap",
            "value": PARENT_FLAT_ORDINAL,
        },
        "all_component_safe_phase_product_discs_are_processed": {
            "passed": bool(
                validity_passed
                and sum(comparison["category_counts"].values())
                == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            ),
            "threshold": "all 18718 compatible phase allocations have one category",
            "value": comparison["category_counts"],
        },
        "registered_resolution_stopping_rule_is_applied": {
            "passed": bool(resolved or persistent),
            "threshold": "zero unresolved and positive minimum, or a retained obstruction",
            "value": {
                "unresolved": unresolved_count,
                "global_minimum_margin_sign": (global_margin > 0)
                - (global_margin < 0),
            },
        },
        "scientific_boundary_is_preserved": {
            "passed": True,
            "threshold": "no degree-34, actual-resonance, all-order or SSM claim",
            "value": "certified 2--33 and 91+, missing 34--90",
        },
    }
    refinement_outcome = (
        "component_safe_phase_resolved"
        if resolved
        else "component_safe_phase_persistent"
        if persistent
        else "inconclusive"
    )
    classification = (
        RESOLVED_CLASSIFICATION
        if resolved
        else PERSISTENT_CLASSIFICATION
        if persistent
        else INCONCLUSIVE_CLASSIFICATION
    )
    cycle = {
        "question": (
            "Do label-free Q011an component-row unions and Q011ak block discs "
            "strictly separate every complex product in Q011cb flatten ordinal 2?"
        ),
        **input_sections,
        **phase_input_sections,
        **allocation_sections,
        **comparison_sections,
        "runner_source": runner,
        "input_digest_sha256": input_digest,
        "phase_input_digest_sha256": phase_input_digest,
        "allocation_digest_sha256": allocation_digest,
        "phase_comparison_digest_sha256": comparison_digest,
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
        "actual_resonance_outcome": (
            "not_established" if validity_passed else "inconclusive"
        ),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "component_safe_complex_phase_discs_resolve_third_q011cb_witness": resolved,
        "third_q011cb_witness_persists_under_component_safe_phase_discs": persistent,
        "q011an_component_internal_eigenvalue_labels_are_assumed": False,
        "q011cg_interval_inert_diagnostic_is_preserved": True,
        "q011cf_ordinal_one_phase_resolution_is_preserved": True,
        "q011cd_ordinal_zero_phase_resolution_is_preserved": True,
        "q011cb_persistent_diagnostic_is_preserved": True,
        "q011ca_first_family_phase_resolution_is_preserved": True,
        "q011bx_degree_thirty_four_sufficient_certificate_remains_rejected": True,
        "degree_thirty_four_external_nonresonance_is_certified": False,
        "an_actual_degree_thirty_four_external_resonance_is_established": False,
        "certified_external_nonresonance_degrees": list(range(2, 34)),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(34, 91)),
        "all_spectral_quotient_nonresonances_are_certified": False,
        "ssm_existence_or_uniqueness_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This certificate concerns only the fixed 17x17 repaired exact map on one "
        "fixed conservation leaf, degree-34 parent aggregate 2340, Q011cb flatten "
        "ordinal 2, its 18718 registered component-safe phase allocations and target "
        "block=7;center=44. It does not reevaluate ordinals 0 or 1 or classify the "
        "later 44797 Q011cb refined signatures, the other 31 parent coalesced "
        "overlaps, other targets, aggregate 2340 as a whole, aggregate 972 or the "
        "full degree-34 sweep. Product-disc overlap does not establish an actual "
        "resonance. The audit leaves all prior rejection, persistence, interval-inert "
        "and phase-resolution results, certified degrees 2--33 and 91+, and missing "
        "degrees 34--90 unchanged, and makes no claim about degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011ci to audit the next Q011cb refined overlap in registered order."
        if resolved
        else (
            "Preregister Q011ci to refine only the first unresolved component-safe "
            "phase witness."
        )
        if persistent
        else "Repair only the first Q011ch validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ch cycle failed strict serialization or digest")
    return cycle


def run_q011ch_study() -> dict[str, Any]:
    started = perf_counter()
    cycle = run_degree_thirty_four_third_component_safe_phase_audit()
    elapsed = perf_counter() - started
    comparison = cycle["complex_phase_product_disc_audit"]
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_input_scalar_type": "fractions.Fraction",
            "center_distance_enclosure": "integer-isqrt rational bounds via Q011o",
            "product_disc_radius": "exact rational closed form and factor recurrence",
            "fourier_compatibility": "exact block-index sum modulo 17",
            "target_comparisons": comparison["compatible_phase_allocation_count"],
            "full_comparison_records_retained": False,
            "elapsed_seconds": elapsed,
            "floating_point_used_for_gate_decisions": False,
        },
        "mathematical_scope": {
            "diagnostic": "third Q011cb witness component-safe complex phase discs",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "parent_aggregate_index": PARENT_AGGREGATE_INDEX,
            "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
            "target_identifier": TARGET_IDENTIFIER,
            "component_internal_eigenvalue_labels_assumed": False,
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
    result = run_q011ch_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
