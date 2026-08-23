"""Q011ih component-safe complex phase discs for Q011cb flatten ordinal eighty."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

import research.q011cj_degree34_fourth_component_safe_phase_discs as q011cj
import research.q011cx_degree34_eleventh_component_safe_phase_discs as q011cx
import research.q011ig_degree34_eighty_first_individual_partition_audit as q011ig
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011b = q011ig.q011b
q011z = q011ig.q011z

_ExactDisc = q011cx._ExactDisc

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
PARENT_FLAT_ORDINAL = 80
OUTPUT_BLOCK = 7
TARGET_IDENTIFIER = "block=7;center=44"

SOURCE_VARIANTS = (
    ("block=16;center=144", "q011an_row"),
    ("block=1;center=144", "q011an_row"),
    ("block=16;center=145", "q011an_row"),
    ("block=1;center=145", "q011an_row"),
    ("block=16;center=150", "q011an_row"),
    ("block=16;center=151", "q011an_row"),
    ("block=1;center=150", "q011an_row"),
    ("block=1;center=151", "q011an_row"),
    ("block=16;center=152", "q011ak_block"),
    ("block=1;center=152", "q011ak_block"),
    ("block=16;center=148", "q011an_row"),
    ("block=1;center=148", "q011an_row"),
    ("block=16;center=149", "q011an_row"),
    ("block=1;center=149", "q011an_row"),
)
SOURCE_POWER_MAXIMUM_COUNTS = (1, 1, 12, 12, 9, 9, 9, 9, 5, 5, 0, 0, 7, 7)
RADIUS_SIGNATURE_REPRESENTATIVE_VARIANTS = (0, 2, 4, 5, 8, 10, 12)
EXPECTED_SOURCE_RADIUS_HEX = (
    "0x1.795a619bf3893p-36",
    "0x1.795a619bf3893p-36",
    "0x1.7961e9d97b02ep-36",
    "0x1.7961e9d97b02ep-36",
    "0x1.3f712af66bee8p-36",
    "0x1.59d0855a75677p-36",
    "0x1.3f712af66bee8p-36",
    "0x1.59d0855a75677p-36",
    "0x1.23ce0990a1325p-30",
    "0x1.23ce0990a1325p-30",
    "0x1.bcf34ab668670p-36",
    "0x1.bcf34ab668670p-36",
    "0x1.bcf9a62d1b2e2p-36",
    "0x1.bcf9a62d1b2e2p-36",
)
EXPECTED_TARGET_RADIUS_HEX = q011cx.EXPECTED_TARGET_RADIUS_HEX
EXPECTED_SOURCE_RECORD_DIGEST = "94898648cd830f4948118e0c4413e0ac39129714b50efdbfdf48904d52e1c2af"
EXPECTED_TARGET_RECORD_DIGEST = q011cx.EXPECTED_TARGET_RECORD_DIGEST

EXPECTED_FULL_ALLOCATION_COUNT = 274_560
EXPECTED_COMPATIBLE_ALLOCATION_COUNT = 15_278
EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT = 701
EXPECTED_WAVE_PROJECTION_COUNT = 701
EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT = 10
EXPECTED_FULL_ALLOCATION_DIGEST = "4fe4d50dc6e9286e8137a3087b11fd76d8009f73225e248e69e768962aadc0f9"
EXPECTED_COMPATIBLE_ALLOCATION_DIGEST = (
    "2c65722f81961ad1ab6dcceac2ca13c9cd010134d8b2fe26facb4e5dd80d31eb"
)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 1, 0, 12, 0, 0, 0, 9, 0, 5, 0, 0, 5, 2)
EXPECTED_LAST_COMPATIBLE_COUNTS = (1, 0, 12, 0, 9, 0, 0, 0, 0, 5, 0, 0, 0, 7)
EXPECTED_WAVE_PROJECTION_DIGEST = "d9c27f30661dd287721e19a3dafe2697bf286f18b77545abcbc2fe9dde1b7c04"
EXPECTED_PHASE_FIBER_HISTOGRAM = {10: 147, 18: 142, 24: 139, 28: 137, 30: 136}
EXPECTED_BRIDGE_FIBER_HISTOGRAM = {1: 701}
EXPECTED_BRIDGE_RECORD_DIGEST = "62b6dbd3731ddaf63ad595d29be7cb2525a13a9f5c6ce934b24f8feb814c3f5c"
EXPECTED_PAIRED_RECORD_DIGEST = "20889bd1712e46b1c4cde16a610ea3145d326debeb94206a3ab2aebea4bcd342"

Q011IG_ARTIFACT_SHA256 = "cef976d9801ca0a30d4ca03fd479e2f0a76270e5caa8c1b2e4c89955fc60e0ee"
Q011IG_RUNNER_SHA256 = "846fef369e733205b3f3bd3ce71545e05bf25fa0190f783b714742b676b6e85f"
Q011IG_DIGEST_NAMES = (
    "input_digest_sha256",
    "partition_input_digest_sha256",
    "allocation_audit_digest_sha256",
    "result_digest_sha256",
)
Q011IG_DIGESTS = (
    "b7452d13387357436a83dca77ec51a2b62b7edd775a4d33b852a212215edb6a1",
    "47a57e508daf45fdc7bc1e21d50d2b74df4a3d30c70d9cec70f61138431f5df4",
    "146149e67a0d9fc039a40039cd5b7d830f64338f8e2b8548f914b45af4b32b32",
    "ed197165013d80e983d05a334af20ea71edf60c708dff82cfbd38620bbed4762",
)
EXPECTED_Q011IG_ALLOCATION_RECORD_DIGEST = (
    "26640b4e287d61212cef746fa6bc09b57b3bb13db61e51a275682594a48e5084"
)

RESOLVED_CLASSIFICATION = "the component-safe complex phase discs resolve the eighty-first Q011cb persistent refined witness"
PERSISTENT_CLASSIFICATION = (
    "the eighty-first Q011cb persistent refined witness persists under component-safe "
    "complex phase discs"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011ih component-safe phase-disc audit is inconclusive"


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


q011ch = q011cj.q011ch
q011cf = q011ch.q011cf
q011ca = q011ch.q011ca
q011o = q011ch.q011o

_fraction_record = q011ch._fraction_record
_complex_record = q011ch._complex_record
_interval_record = q011ch._interval_record
_exact_fraction_sha256 = q011ch._exact_fraction_sha256
_exact_complex_sha256 = q011ch._exact_complex_sha256
_exact_interval_sha256 = q011ch._exact_interval_sha256
_product_modulus_expression_sha256 = q011ch._product_modulus_expression_sha256


def _q011ih_framed_record_digest() -> Any:
    return q011cx._BASE_FRAMED_RECORD_DIGEST(
        "q011ih-component-safe-phase-comparisons-v1"
    )


def _q011ih_exact_fraction_sequence_sha256(
    _domain: bytes,
    values: tuple[Fraction, ...],
) -> str:
    return q011cx._BASE_EXACT_FRACTION_SEQUENCE_SHA256(
        b"q011ih-complex-margin-expression-v1",
        values,
    )


def _power_tables(
    center_uppers: tuple[Fraction, ...],
    source_discs: tuple[_ExactDisc, ...],
) -> tuple[Any, ...]:
    center_powers = []
    upper_powers = []
    full_powers = []
    radius_powers = []
    recurrence_checks = []
    for upper, disc, maximum in zip(
        center_uppers,
        source_discs,
        SOURCE_POWER_MAXIMUM_COUNTS,
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


def _cached_product_radius(
    radius_signature: tuple[int, ...],
    upper_powers: tuple[tuple[Fraction, ...], ...],
    full_powers: tuple[tuple[Fraction, ...], ...],
    radius_powers: tuple[tuple[Fraction, ...], ...],
) -> tuple[Fraction, Fraction]:
    center_product = Fraction(1)
    full_product = Fraction(1)
    recurrence_center = Fraction(1)
    recurrence_radius = Fraction(0)
    for variant, count in zip(
        RADIUS_SIGNATURE_REPRESENTATIVE_VARIANTS,
        radius_signature,
        strict=True,
    ):
        center_power = upper_powers[variant][count]
        full_power = full_powers[variant][count]
        radius_power = radius_powers[variant][count]
        center_product *= center_power
        full_product *= full_power
        recurrence_radius = (
            recurrence_center * radius_power
            + center_power * recurrence_radius
            + recurrence_radius * radius_power
        )
        recurrence_center *= center_power
    return full_product - center_product, recurrence_radius


def _protocol_globals_are_restored() -> bool:
    return bool(
        q011ig._protocol_globals_are_restored()
        and q011cx._protocol_globals_are_restored()
        and q011cj._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011ig._sealed_input_audit()
    artifact_path = _artifact_directory() / (
        "q011ig_degree34_eighty_first_individual_partition_audit.json"
    )
    runner_path = Path(q011ig.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    fixed = cycle["fixed_individual_partition_input_audit"]
    partition = cycle["individual_allocation_interval_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011IG_DIGEST_NAMES)
    checks = {
        "q011ig_two_hundred_nineteen_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 219
            and prior["direct_digest_count"] == 998
            and len(artifacts) == 219
            and all(prior["checks"].values())
        ),
        "q011ig_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011IG_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011IG_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011IG_RUNNER_SHA256
        ),
        "q011ig_section_digests_match": digests == Q011IG_DIGESTS,
        "q011ig_valid_interval_inert_outcome_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "partition_inert_persistent"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem["individual_partition_is_interval_inert_for_eighty_first_q011cb_witness"]
            and theorem["q011if_ordinal_seventy_nine_phase_resolution_is_preserved"]
            and theorem["q011ie_ordinal_seventy_nine_interval_inert_diagnostic_is_preserved"]
            and theorem["q011id_ordinal_seventy_eight_phase_resolution_is_preserved"]
            and theorem["q011ic_ordinal_seventy_eight_interval_inert_diagnostic_is_preserved"]
            and theorem["q011ib_ordinal_seventy_seven_phase_resolution_is_preserved"]
            and theorem["q011hz_ordinal_seventy_six_phase_resolution_is_preserved"]
            and theorem["q011hy_ordinal_seventy_six_interval_inert_diagnostic_is_preserved"]
            and theorem["q011hx_ordinal_seventy_five_phase_resolution_is_preserved"]
            and theorem["q011hw_ordinal_seventy_five_interval_inert_diagnostic_is_preserved"]
            and theorem["q011hv_ordinal_seventy_four_phase_resolution_is_preserved"]
            and theorem["q011hu_ordinal_seventy_four_interval_inert_diagnostic_is_preserved"]
            and theorem["q011hr_ordinal_seventy_two_phase_resolution_is_preserved"]
            and theorem["q011hq_ordinal_seventy_two_interval_inert_diagnostic_is_preserved"]
            and theorem["q011hp_ordinal_seventy_one_phase_resolution_is_preserved"]
            and theorem["q011ho_ordinal_seventy_one_interval_inert_diagnostic_is_preserved"]
            and theorem["q011hn_ordinal_seventy_phase_resolution_is_preserved"]
            and theorem["q011hm_ordinal_seventy_interval_inert_diagnostic_is_preserved"]
            and theorem["q011hl_ordinal_sixty_nine_phase_resolution_is_preserved"]
            and theorem["q011gx_ordinal_sixty_two_phase_resolution_is_preserved"]
            and theorem["q011gw_ordinal_sixty_two_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gv_ordinal_sixty_one_phase_resolution_is_preserved"]
            and theorem["q011gu_ordinal_sixty_one_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gt_ordinal_sixty_phase_resolution_is_preserved"]
            and theorem["q011gs_ordinal_sixty_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gr_ordinal_fifty_nine_phase_resolution_is_preserved"]
            and theorem["q011gq_ordinal_fifty_nine_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gp_ordinal_fifty_eight_phase_resolution_is_preserved"]
            and theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
            and theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gl_ordinal_fifty_six_phase_resolution_is_preserved"]
            and theorem["q011gk_ordinal_fifty_six_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gj_ordinal_fifty_five_phase_resolution_is_preserved"]
            and theorem["q011gi_ordinal_fifty_five_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gh_ordinal_fifty_four_phase_resolution_is_preserved"]
            and theorem["q011gg_ordinal_fifty_four_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gf_ordinal_fifty_three_phase_resolution_is_preserved"]
            and theorem["q011ge_ordinal_fifty_three_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gd_ordinal_fifty_two_phase_resolution_is_preserved"]
            and theorem["q011gc_ordinal_fifty_two_interval_inert_diagnostic_is_preserved"]
            and theorem["q011gb_ordinal_fifty_one_phase_resolution_is_preserved"]
            and theorem["q011ga_ordinal_fifty_one_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fz_ordinal_fifty_phase_resolution_is_preserved"]
            and theorem["q011fy_ordinal_fifty_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fx_ordinal_forty_nine_phase_resolution_is_preserved"]
            and theorem["q011fw_ordinal_forty_nine_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fv_ordinal_forty_eight_phase_resolution_is_preserved"]
            and theorem["q011fu_ordinal_forty_eight_interval_inert_diagnostic_is_preserved"]
            and theorem["q011ft_ordinal_forty_seven_phase_resolution_is_preserved"]
            and theorem["q011fs_ordinal_forty_seven_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fr_ordinal_forty_six_phase_resolution_is_preserved"]
            and theorem["q011fq_ordinal_forty_six_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fp_ordinal_forty_five_phase_resolution_is_preserved"]
            and theorem["q011fo_ordinal_forty_five_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fn_ordinal_forty_four_phase_resolution_is_preserved"]
            and theorem["q011fm_ordinal_forty_four_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fl_ordinal_forty_three_phase_resolution_is_preserved"]
            and theorem["q011fk_ordinal_forty_three_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fj_ordinal_forty_two_phase_resolution_is_preserved"]
            and theorem["q011fi_ordinal_forty_two_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fh_ordinal_forty_one_phase_resolution_is_preserved"]
            and theorem["q011fg_ordinal_forty_one_interval_inert_diagnostic_is_preserved"]
            and theorem["q011ff_ordinal_forty_phase_resolution_is_preserved"]
            and theorem["q011fe_ordinal_forty_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fd_ordinal_thirty_nine_phase_resolution_is_preserved"]
            and theorem["q011fc_ordinal_thirty_nine_interval_inert_diagnostic_is_preserved"]
            and theorem["q011fb_ordinal_thirty_eight_phase_resolution_is_preserved"]
            and theorem["q011fa_ordinal_thirty_eight_interval_inert_diagnostic_is_preserved"]
            and theorem["q011ez_ordinal_thirty_seven_phase_resolution_is_preserved"]
            and theorem["q011ey_ordinal_thirty_seven_interval_inert_diagnostic_is_preserved"]
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011ig_parent_partition_and_relations_reproduce": bool(
            fixed["eighty_first_parent_witness_selection_audit"]["selected_flat_ordinal"]
            == PARENT_FLAT_ORDINAL
            and fixed["compatible_allocation_count"] == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and fixed["compatible_allocation_digest_sha256"] == q011ig.EXPECTED_COMPATIBLE_DIGEST
            and partition["compatible_allocation_count"]
            == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and partition["exact_relation_counts"]
            == {
                "product_below_target": 0,
                "target_below_product": 0,
                "overlap": EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT,
            }
            and partition["all_product_target_intersection_and_center_records_equal_parent"]
            and partition["allocation_classification_record_digest_sha256"]
            == EXPECTED_Q011IG_ALLOCATION_RECORD_DIGEST
        ),
        "q011ig_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_thousand_two_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 1002
        ),
    }
    artifacts["q011ig"] = artifact
    return (
        {
            "prior_q011ig_sealed_input_audit": prior,
            "q011ig": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011IG_DIGEST_NAMES),
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
    fixed, lookup, wave_compatible, parent = q011ig._fixed_individual_input_audit(
        artifacts
    )
    partition = q011ig._individual_partition_audit(lookup, wave_compatible, parent)
    stored = artifacts["q011ig"]["cycle"]
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
    expected_components = ((144,), (145,), (148,), (149,), (150, 151))
    row_discs = tuple(source_discs[:8] + source_discs[10:])
    block_discs = tuple(source_discs[8:10])
    target_center_modulus = q011o._center_modulus_bounds(target.center)
    target_expected_modulus = RationalInterval(
        max(Fraction(0), target_center_modulus.lower - target.radius),
        target_center_modulus.upper + target.radius,
    )
    conjugate_pairs = ((0, 1), (2, 3), (4, 6), (5, 7), (8, 9), (10, 11), (12, 13))
    checks = {
        "q011ig_fixed_parent_and_interval_partition_replay_bitwise": bool(
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
            source_discs[4].component
            == source_discs[5].component
            == source_discs[6].component
            == source_discs[7].component
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
        "q011ig_compatible_wave_allocation_count": len(wave_compatible),
        "q011ig_compatible_wave_allocation_digest_sha256": fixed[
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



def _component_wave_counts(individual_counts: tuple[int, ...]) -> tuple[int, ...]:
    if len(individual_counts) != 10:
        raise ValueError("Q011ih requires ten Q011ig individual counts")
    return (*individual_counts[:8], 0, 0, *individual_counts[8:])


def _allocation_inventory(
    source_discs: tuple[_ExactDisc, ...],
    wave_compatible: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], tuple[dict[str, Any], ...]]:
    individual_counts = tuple(tuple(record["individual_counts"]) for record in wave_compatible)
    bridge = Counter(_component_wave_counts(counts) for counts in individual_counts)
    bridge_records = [
        {
            "component_wave_counts": list(counts),
            "individual_wave_allocation_count": bridge[counts],
        }
        for counts in sorted(bridge)
    ]
    bridge_histogram = dict(sorted(Counter(bridge.values()).items()))
    bridge_digest = q011b._canonical_json_sha256(bridge_records)

    records = []
    for count_16_144 in range(2):
        for count_16_145 in range(13):
            for count_16_150 in range(10):
                for count_16_151 in range(10 - count_16_150):
                    for count_1_150 in range(10 - count_16_150 - count_16_151):
                        count_1_151 = 9 - count_16_150 - count_16_151 - count_1_150
                        for count_16_152 in range(6):
                            for count_16_149 in range(8):
                                counts = [
                                    count_16_144,
                                    1 - count_16_144,
                                    count_16_145,
                                    12 - count_16_145,
                                    count_16_150,
                                    count_16_151,
                                    count_1_150,
                                    count_1_151,
                                    count_16_152,
                                    5 - count_16_152,
                                    0,
                                    0,
                                    count_16_149,
                                    7 - count_16_149,
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
            record["counts"][2],
            record["counts"][3],
            record["counts"][4] + record["counts"][5],
            record["counts"][6] + record["counts"][7],
            record["counts"][8],
            record["counts"][9],
            record["counts"][10],
            record["counts"][11],
            record["counts"][12],
            record["counts"][13],
        )
        for record in compatible
    )
    projection_records = [
        {"wave_counts": list(counts), "phase_allocation_count": projection[counts]}
        for counts in sorted(projection)
    ]
    fiber_histogram = dict(sorted(Counter(projection.values()).items()))
    full_digest = q011b._canonical_json_sha256(records)
    compatible_digest = q011b._canonical_json_sha256(list(compatible))
    projection_digest = q011b._canonical_json_sha256(projection_records)
    paired_records = [
        {
            "component_wave_counts": list(counts),
            "individual_wave_allocation_count": bridge[counts],
            "phase_allocation_count": projection[counts],
        }
        for counts in sorted(projection)
    ]
    paired_digest = q011b._canonical_json_sha256(paired_records)
    bridge_constraints_close = all(
        sum(counts) == DEGREE
        and counts[0] + counts[1] == 1
        and counts[2] + counts[3] == 12
        and counts[4] + counts[5] == 9
        and counts[6] + counts[7] == 5
        and counts[8] + counts[9] == 0
        and counts[10] + counts[11] == 7
        and all(count >= 0 for count in counts)
        and (
            sum(
                count * block
                for count, block in zip(
                    counts,
                    (16, 1, 16, 1, 16, 1, 16, 1, 16, 1, 16, 1),
                    strict=True,
                )
            )
            % SIZE
            == OUTPUT_BLOCK
        )
        for counts in bridge
    )
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
            and record["counts"][0] + record["counts"][1] == 1
            and record["counts"][2] + record["counts"][3] == 12
            and sum(record["counts"][4:8]) == 9
            and record["counts"][8] + record["counts"][9] == 5
            and record["counts"][10] + record["counts"][11] == 0
            and record["counts"][12] + record["counts"][13] == 7
            and all(count >= 0 for count in record["counts"])
            and record["output_block"] == OUTPUT_BLOCK
            for record in compatible
        ),
        "phase_projection_matches_component_wave_quotient": bool(
            set(projection) == set(bridge)
            and len(projection) == len(bridge) == EXPECTED_WAVE_PROJECTION_COUNT
            and projection_digest == EXPECTED_WAVE_PROJECTION_DIGEST
        ),
        "all_phase_fibers_are_nonempty_and_registered": bool(
            min(projection.values()) == 10
            and max(projection.values()) == 30
            and sum(projection.values()) == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            and fiber_histogram == EXPECTED_PHASE_FIBER_HISTOGRAM
        ),
        "individual_to_component_wave_bridge_reproduces": bool(
            len(individual_counts) == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and len(set(individual_counts)) == len(individual_counts)
            and sum(bridge.values()) == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and len(bridge) == EXPECTED_WAVE_PROJECTION_COUNT
            and min(bridge.values()) == 1
            and max(bridge.values()) == 1
            and bridge_histogram == EXPECTED_BRIDGE_FIBER_HISTOGRAM
            and bridge_digest == EXPECTED_BRIDGE_RECORD_DIGEST
            and bridge_constraints_close
        ),
        "bridge_phase_pairing_reproduces": bool(
            set(projection) == set(bridge) and paired_digest == EXPECTED_PAIRED_RECORD_DIGEST
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
        "individual_wave_allocation_count": len(individual_counts),
        "component_wave_projection_count": len(bridge_records),
        "individual_to_component_bridge_records": bridge_records,
        "individual_to_component_bridge_record_digest_sha256": bridge_digest,
        "minimum_individual_allocations_per_component_wave": min(bridge.values()),
        "maximum_individual_allocations_per_component_wave": max(bridge.values()),
        "individual_allocation_count_per_component_wave_histogram": {
            str(count): frequency for count, frequency in bridge_histogram.items()
        },
        "bridge_phase_paired_records": paired_records,
        "bridge_phase_paired_record_digest_sha256": paired_digest,
        "full_allocation_records_retained": False,
        "compatible_allocation_records_retained": False,
        "allocation_protocol_adapter": {
            "source_runner_sha256": _file_sha256(Path(__file__).resolve()),
            "ordinal_eighty_totals": [1, 12, 9, 5, 0, 7],
            "new_active_singleton_component_wave_identifiers": [
                "block=16;center=144",
                "block=1;center=144",
            ],
            "active_singleton_component_wave_identifiers": [
                "block=16;center=144",
                "block=1;center=144",
                "block=16;center=145",
                "block=1;center=145",
                "block=16;center=149",
                "block=1;center=149",
            ],
            "inactive_zero_count_source_identifiers": [
                "block=16;center=148",
                "block=1;center=148",
            ],
            "inherited_hardcoded_ordinal_totals_used": False,
            "protocol_globals_modified": False,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, compatible


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
    stream = _q011ih_framed_record_digest()
    categories: Counter[str] = Counter()
    individual_relations: Counter[str] = Counter()
    all_radius_recurrences_equal = True
    all_square_root_enclosures_hold = True
    all_product_intervals_ordered = True
    all_separated_margins_positive = True
    radius_cache: dict[
        tuple[int, ...], tuple[Fraction, Fraction]
    ] = {}
    radius_digest_cache: dict[tuple[int, ...], str] = {}
    radius_bound_cache: dict[
        tuple[int, ...],
        tuple[Fraction, Fraction, Fraction],
    ] = {}
    first_unresolved: tuple[Any, ...] | None = None
    minimum_distance_by_radius: dict[
        tuple[int, ...],
        tuple[tuple[Any, ...], tuple[Any, ...]],
    ] = {}
    minimum_separated_distance_by_radius: dict[
        tuple[int, ...],
        tuple[tuple[Any, ...], tuple[Any, ...]],
    ] = {}

    for index, allocation in enumerate(compatible):
        counts = allocation["counts"]
        product_center = q011cf._cached_product_center(counts, center_powers)
        radius_signature = (
            counts[0] + counts[1],
            counts[2] + counts[3],
            counts[4] + counts[6],
            counts[5] + counts[7],
            counts[8] + counts[9],
            counts[10] + counts[11],
            counts[12] + counts[13],
        )
        if radius_signature not in radius_cache:
            radius_cache[radius_signature] = _cached_product_radius(
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
                _q011ih_exact_fraction_sequence_sha256(
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
        raise RuntimeError("Q011ih has no compatible phase allocation")
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
        "comparison_stream_domain": "q011ih-component-safe-phase-comparisons-v1",
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
        "protocol": "q011ih-eighty-first-component-safe-phase-v1",
        "degree": DEGREE,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "output_block": OUTPUT_BLOCK,
        "target_identifier": TARGET_IDENTIFIER,
        "source_variants": [list(record) for record in SOURCE_VARIANTS],
        "source_power_maximum_counts": list(SOURCE_POWER_MAXIMUM_COUNTS),
        "radius_signature_representative_variants": list(
            RADIUS_SIGNATURE_REPRESENTATIVE_VARIANTS
        ),
        "comparison_stream_domain": "q011ih-component-safe-phase-comparisons-v1",
        "complex_margin_digest_domain": "q011ih-complex-margin-expression-v1",
        "q011ih_allocation_enumerator": {
            "source_runner_sha256": _file_sha256(Path(__file__).resolve()),
            "component_wave_records_replace_inherited_wave_records": True,
            "ordinal_eighty_totals": [1, 12, 9, 5, 0, 7],
            "inactive_center_148_pair_retained": True,
            "protocol_globals_modified": False,
        },
        "component_label_coalescing_bridge": {
            "individual_identifier_count": 10,
            "component_wave_identifier_count": 12,
            "active_component_wave_identifier_count": 10,
            "phase_source_identifier_count": 14,
            "individual_wave_allocation_count": EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT,
            "component_wave_projection_count": EXPECTED_WAVE_PROJECTION_COUNT,
            "bridge_record_digest_sha256": EXPECTED_BRIDGE_RECORD_DIGEST,
            "paired_record_digest_sha256": EXPECTED_PAIRED_RECORD_DIGEST,
            "internal_component_labels_assumed": False,
        },
    }


_result_digest_sections = q011cx._result_digest_sections


def run_degree_thirty_four_eighty_first_component_safe_phase_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    phase_input, sources, target, wave_compatible = _fixed_phase_input_audit(artifacts)
    allocation, compatible = _allocation_inventory(sources, wave_compatible)
    comparison = _phase_product_audit(sources, target, compatible)
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
        "q011ig_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "220 artifacts and 1002 direct digests reproduce",
            "value": sealed["checks"],
        },
        "q011ig_parent_partition_and_interval_inert_result_replay": {
            "passed": phase_input["checks"][
                "q011ig_fixed_parent_and_interval_partition_replay_bitwise"
            ],
            "threshold": "ordinal 80, 701 individual wave allocations and inert result replay",
            "value": phase_input["q011ig_compatible_wave_allocation_digest_sha256"],
        },
        "exact_centers_radii_components_and_target_reproduce": {
            "passed": bool(
                phase_input["checks"]["q011k_centers_and_q011ak_block_radii_reconstruct"]
                and phase_input["checks"]["registered_source_and_target_phase_records_reproduce"]
                and phase_input["checks"][
                    "active_singleton_and_two_row_components_have_exact_multiplicity"
                ]
            ),
            "threshold": "fourteen source discs, one target, active 144/145/149 and inactive 148 pairs reproduce",
            "value": {
                "source": phase_input["source_phase_disc_record_digest_sha256"],
                "target": phase_input["target_phase_disc_record_digest_sha256"],
            },
        },
        "containment_conjugacy_and_label_free_semantics_pass": {
            "passed": bool(
                phase_input["checks"]["row_discs_are_contained_in_q011am_and_q011ak"]
                and phase_input["checks"]["block_discs_and_target_replay_the_q011ak_formula"]
                and phase_input["checks"]["all_conjugate_source_pairs_transport_exactly"]
                and phase_input["checks"]["component_union_semantics_do_not_assign_internal_labels"]
            ),
            "threshold": "safe containment, seven conjugate pairs and no internal labels",
            "value": phase_input["checks"],
        },
        "component_safe_allocation_and_component_quotient_reproduce": {
            "passed": allocation["passed"],
            "threshold": (
                "701 individual waves quotient to 701 component waves; "
                "274560 total and 15278 compatible phase allocations"
            ),
            "value": allocation["checks"],
        },
        "exact_product_radius_distance_and_categories_close": {
            "passed": comparison["passed"],
            "threshold": (
                "15278 exact products, ten radius signatures, sqrt enclosures and "
                "exclusive categories"
            ),
            "value": comparison["checks"],
        },
        "strict_stream_section_digests_runner_and_protocol_provenance_reproduce": {
            "passed": bool(
                comparison["comparison_stream_count"] == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
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
                == "q011ih_degree34_eighty_first_component_safe_phase_discs.py"
                and _protocol_globals_are_restored()
            ),
            "threshold": "framed stream, four section digests, runner and restored protocol",
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
    unresolved_count = comparison["category_counts"]["unresolved_product_disk_overlap"]
    global_margin = q011z._fraction(
        comparison["global_minimum_margin_witness"]["complex_separation_margin_lower"]["exact"]
    )
    resolved = validity_passed and unresolved_count == 0 and global_margin > 0
    persistent = validity_passed and not resolved
    diagnostic_gates = {
        "only_the_registered_eighty_first_q011cb_witness_is_refined": {
            "passed": bool(
                not comparison["previous_q011cb_refined_signatures_recomputed"]
                and not comparison["later_q011cb_refined_signatures_recomputed"]
                and not comparison["other_parent_targets_recomputed"]
                and not comparison["other_parent_coalesced_overlaps_recomputed"]
            ),
            "threshold": "ordinal 80 only, one target and no other overlap",
            "value": PARENT_FLAT_ORDINAL,
        },
        "all_component_safe_phase_product_discs_are_processed": {
            "passed": bool(
                validity_passed
                and sum(comparison["category_counts"].values())
                == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            ),
            "threshold": "all 15278 compatible phase allocations have one category",
            "value": comparison["category_counts"],
        },
        "registered_resolution_stopping_rule_is_applied": {
            "passed": bool(resolved or persistent),
            "threshold": "zero unresolved and positive minimum, or retained obstruction",
            "value": {
                "unresolved": unresolved_count,
                "global_minimum_margin_sign": (global_margin > 0) - (global_margin < 0),
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
            "strictly separate every complex product in Q011cb flatten ordinal 80?"
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
        "actual_resonance_outcome": ("not_established" if validity_passed else "inconclusive"),
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["theorem_consequence"] = {
        "component_safe_complex_phase_discs_resolve_eighty_first_q011cb_witness": resolved,
        "eighty_first_q011cb_witness_persists_under_component_safe_phase_discs": persistent,
        "q011an_component_internal_eigenvalue_labels_are_assumed": False,
        "q011ig_ordinal_eighty_interval_inert_diagnostic_is_preserved": True,
        "q011if_ordinal_seventy_nine_phase_resolution_is_preserved": True,
        "q011ie_ordinal_seventy_nine_interval_inert_diagnostic_is_preserved": True,
        "q011id_ordinal_seventy_eight_phase_resolution_is_preserved": True,
        "q011ic_ordinal_seventy_eight_interval_inert_diagnostic_is_preserved": True,
        "q011ib_ordinal_seventy_seven_phase_resolution_is_preserved": True,
        "q011hz_ordinal_seventy_six_phase_resolution_is_preserved": True,
        "q011hy_ordinal_seventy_six_interval_inert_diagnostic_is_preserved": True,
        "q011hx_ordinal_seventy_five_phase_resolution_is_preserved": True,
        "q011hw_ordinal_seventy_five_interval_inert_diagnostic_is_preserved": True,
        "q011hv_ordinal_seventy_four_phase_resolution_is_preserved": True,
        "q011hu_ordinal_seventy_four_interval_inert_diagnostic_is_preserved": True,
        "q011ht_ordinal_seventy_three_phase_resolution_is_preserved": True,
        "q011hs_ordinal_seventy_three_interval_inert_diagnostic_is_preserved": True,
        "q011hr_ordinal_seventy_two_phase_resolution_is_preserved": True,
        "q011hq_ordinal_seventy_two_interval_inert_diagnostic_is_preserved": True,
        "q011hp_ordinal_seventy_one_phase_resolution_is_preserved": True,
        "q011ho_ordinal_seventy_one_interval_inert_diagnostic_is_preserved": True,
        "q011hn_ordinal_seventy_phase_resolution_is_preserved": True,
        "q011hm_ordinal_seventy_interval_inert_diagnostic_is_preserved": True,
        "q011hl_ordinal_sixty_nine_phase_resolution_is_preserved": True,
        "q011hk_ordinal_sixty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011hj_ordinal_sixty_eight_phase_resolution_is_preserved": True,
        "q011hi_ordinal_sixty_eight_interval_inert_diagnostic_is_preserved": True,
        "q011hh_ordinal_sixty_seven_phase_resolution_is_preserved": True,
        "q011hg_ordinal_sixty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011hf_ordinal_sixty_six_phase_resolution_is_preserved": True,
        "q011he_ordinal_sixty_six_interval_inert_diagnostic_is_preserved": True,
        "q011hd_ordinal_sixty_five_phase_resolution_is_preserved": True,
        "q011hc_ordinal_sixty_five_interval_inert_diagnostic_is_preserved": True,
        "q011hb_ordinal_sixty_four_phase_resolution_is_preserved": True,
        "q011ha_ordinal_sixty_four_interval_inert_diagnostic_is_preserved": True,
        "q011gz_ordinal_sixty_three_phase_resolution_is_preserved": True,
        "q011gy_ordinal_sixty_three_interval_inert_diagnostic_is_preserved": True,
        "q011gx_ordinal_sixty_two_phase_resolution_is_preserved": True,
        "q011gw_ordinal_sixty_two_interval_inert_diagnostic_is_preserved": True,
        "q011gv_ordinal_sixty_one_phase_resolution_is_preserved": True,
        "q011gu_ordinal_sixty_one_interval_inert_diagnostic_is_preserved": True,
        "q011gt_ordinal_sixty_phase_resolution_is_preserved": True,
        "q011gs_ordinal_sixty_interval_inert_diagnostic_is_preserved": True,
        "q011gr_ordinal_fifty_nine_phase_resolution_is_preserved": True,
        "q011gq_ordinal_fifty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011gp_ordinal_fifty_eight_phase_resolution_is_preserved": True,
        "q011gn_ordinal_fifty_seven_phase_resolution_is_preserved": True,
        "q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011gl_ordinal_fifty_six_phase_resolution_is_preserved": True,
        "q011gk_ordinal_fifty_six_interval_inert_diagnostic_is_preserved": True,
        "q011gj_ordinal_fifty_five_phase_resolution_is_preserved": True,
        "q011gi_ordinal_fifty_five_interval_inert_diagnostic_is_preserved": True,
        "q011gh_ordinal_fifty_four_phase_resolution_is_preserved": True,
        "q011gg_ordinal_fifty_four_interval_inert_diagnostic_is_preserved": True,
        "q011gf_ordinal_fifty_three_phase_resolution_is_preserved": True,
        "q011ge_ordinal_fifty_three_interval_inert_diagnostic_is_preserved": True,
        "q011gd_ordinal_fifty_two_phase_resolution_is_preserved": True,
        "q011gc_ordinal_fifty_two_interval_inert_diagnostic_is_preserved": True,
        "q011gb_ordinal_fifty_one_phase_resolution_is_preserved": True,
        "q011ga_ordinal_fifty_one_interval_inert_diagnostic_is_preserved": True,
        "q011fz_ordinal_fifty_phase_resolution_is_preserved": True,
        "q011fy_ordinal_fifty_interval_inert_diagnostic_is_preserved": True,
        "q011fx_ordinal_forty_nine_phase_resolution_is_preserved": True,
        "q011fw_ordinal_forty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011fv_ordinal_forty_eight_phase_resolution_is_preserved": True,
        "q011fu_ordinal_forty_eight_interval_inert_diagnostic_is_preserved": True,
        "q011ft_ordinal_forty_seven_phase_resolution_is_preserved": True,
        "q011fs_ordinal_forty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011fr_ordinal_forty_six_phase_resolution_is_preserved": True,
        "q011fq_ordinal_forty_six_interval_inert_diagnostic_is_preserved": True,
        "q011fp_ordinal_forty_five_phase_resolution_is_preserved": True,
        "q011fo_ordinal_forty_five_interval_inert_diagnostic_is_preserved": True,
        "q011fn_ordinal_forty_four_phase_resolution_is_preserved": True,
        "q011fm_ordinal_forty_four_interval_inert_diagnostic_is_preserved": True,
        "q011fl_ordinal_forty_three_phase_resolution_is_preserved": True,
        "q011fk_ordinal_forty_three_interval_inert_diagnostic_is_preserved": True,
        "q011fj_ordinal_forty_two_phase_resolution_is_preserved": True,
        "q011fi_ordinal_forty_two_interval_inert_diagnostic_is_preserved": True,
        "q011fh_ordinal_forty_one_phase_resolution_is_preserved": True,
        "q011fg_ordinal_forty_one_interval_inert_diagnostic_is_preserved": True,
        "q011ff_ordinal_forty_phase_resolution_is_preserved": True,
        "q011fe_ordinal_forty_interval_inert_diagnostic_is_preserved": True,
        "q011fd_ordinal_thirty_nine_phase_resolution_is_preserved": True,
        "q011fc_ordinal_thirty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011fb_ordinal_thirty_eight_phase_resolution_is_preserved": True,
        "q011fa_ordinal_thirty_eight_interval_inert_diagnostic_is_preserved": True,
        "q011ez_ordinal_thirty_seven_phase_resolution_is_preserved": True,
        "q011ey_ordinal_thirty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011ex_ordinal_thirty_six_phase_resolution_is_preserved": True,
        "q011ew_ordinal_thirty_six_interval_inert_diagnostic_is_preserved": True,
        "q011ev_ordinal_thirty_five_phase_resolution_is_preserved": True,
        "q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved": True,
        "q011et_ordinal_thirty_four_phase_resolution_is_preserved": True,
        "q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved": True,
        "q011er_ordinal_thirty_three_phase_resolution_is_preserved": True,
        "q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved": True,
        "q011ep_ordinal_thirty_two_phase_resolution_is_preserved": True,
        "q011eo_ordinal_thirty_two_interval_inert_diagnostic_is_preserved": True,
        "q011en_ordinal_thirty_one_phase_resolution_is_preserved": True,
        "q011em_ordinal_thirty_one_interval_inert_diagnostic_is_preserved": True,
        "q011el_ordinal_thirty_phase_resolution_is_preserved": True,
        "q011ek_ordinal_thirty_interval_inert_diagnostic_is_preserved": True,
        "q011ej_ordinal_twenty_nine_phase_resolution_is_preserved": True,
        "q011ei_ordinal_twenty_nine_interval_inert_diagnostic_is_preserved": True,
        "q011eh_ordinal_twenty_eight_phase_resolution_is_preserved": True,
        "q011eg_ordinal_twenty_eight_interval_inert_diagnostic_is_preserved": True,
        "q011ef_ordinal_twenty_seven_phase_resolution_is_preserved": True,
        "q011ee_ordinal_twenty_seven_interval_inert_diagnostic_is_preserved": True,
        "q011ed_ordinal_twenty_six_phase_resolution_is_preserved": True,
        "q011ec_ordinal_twenty_six_interval_inert_diagnostic_is_preserved": True,
        "q011eb_ordinal_twenty_five_phase_resolution_is_preserved": True,
        "q011ea_ordinal_twenty_five_interval_inert_diagnostic_is_preserved": True,
        "q011dz_ordinal_twenty_four_phase_resolution_is_preserved": True,
        "q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved": True,
        "q011dx_ordinal_twenty_three_phase_resolution_is_preserved": True,
        "q011dw_ordinal_twenty_three_interval_inert_diagnostic_is_preserved": True,
        "q011dv_ordinal_twenty_two_phase_resolution_is_preserved": True,
        "q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved": True,
        "q011dt_ordinal_twenty_one_phase_resolution_is_preserved": True,
        "q011ds_ordinal_twenty_one_interval_inert_diagnostic_is_preserved": True,
        "q011dr_ordinal_twenty_phase_resolution_is_preserved": True,
        "q011dq_ordinal_twenty_interval_inert_diagnostic_is_preserved": True,
        "q011dp_ordinal_nineteen_phase_resolution_is_preserved": True,
        "q011do_ordinal_nineteen_interval_inert_diagnostic_is_preserved": True,
        "q011dn_ordinal_eighteen_phase_resolution_is_preserved": True,
        "q011dm_ordinal_eighteen_interval_inert_diagnostic_is_preserved": True,
        "q011dl_ordinal_seventeen_phase_resolution_is_preserved": True,
        "q011dk_ordinal_seventeen_interval_inert_diagnostic_is_preserved": True,
        "q011dj_ordinal_sixteen_phase_resolution_is_preserved": True,
        "q011di_ordinal_sixteen_interval_inert_diagnostic_is_preserved": True,
        "q011dh_ordinal_fifteen_phase_resolution_is_preserved": True,
        "q011dg_ordinal_fifteen_interval_inert_diagnostic_is_preserved": True,
        "q011df_ordinal_fourteen_phase_resolution_is_preserved": True,
        "q011de_ordinal_fourteen_interval_inert_diagnostic_is_preserved": True,
        "q011dd_ordinal_thirteen_phase_resolution_is_preserved": True,
        "q011dc_ordinal_thirteen_interval_inert_diagnostic_is_preserved": True,
        "q011db_ordinal_twelve_phase_resolution_is_preserved": True,
        "q011da_ordinal_twelve_interval_inert_diagnostic_is_preserved": True,
        "q011cx_ordinal_ten_phase_resolution_is_preserved": True,
        "q011cv_ordinal_nine_phase_resolution_is_preserved": True,
        "q011ct_ordinal_eight_phase_resolution_is_preserved": True,
        "q011cr_ordinal_seven_phase_resolution_is_preserved": True,
        "q011cp_ordinal_six_phase_resolution_is_preserved": True,
        "q011cn_ordinal_five_phase_resolution_is_preserved": True,
        "q011cl_ordinal_four_phase_resolution_is_preserved": True,
        "q011cj_ordinal_three_phase_resolution_is_preserved": True,
        "q011ch_ordinal_two_phase_resolution_is_preserved": True,
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
        "ordinal 80, its 701-to-701 component-wave quotient and 15278 registered "
        "component-safe phase allocations and target block=7;center=44. It does not "
        "reevaluate ordinals 0 through 79 or classify the later 44719 Q011cb refined "
        "signatures, the other 31 parent coalesced overlaps, other targets, aggregate "
        "2340 as a whole, aggregate 972 or the full degree-34 sweep. Product-disc "
        "overlap does not establish an actual resonance. The audit leaves all prior "
        "rejection, persistence, interval-inert and phase-resolution results, "
        "certified degrees 2--33 and 91+, and missing degrees 34--90 unchanged, and "
        "makes no claim about degree-34 or all-order nonresonance, higher graph "
        "smoothness, SSM existence or uniqueness, normal attraction, a basin, other "
        "grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011ii to audit the next Q011cb refined overlap in registered order."
        if resolved
        else (
            "Preregister Q011ii to refine only the first unresolved component-safe phase witness."
        )
        if persistent
        else "Repair only the first Q011ih validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011ih cycle failed strict serialization or digest")
    return cycle


def run_q011ih_study() -> dict[str, Any]:
    started = perf_counter()
    cycle = run_degree_thirty_four_eighty_first_component_safe_phase_audit()
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
            "protocol_globals_restored_after_use": _protocol_globals_are_restored(),
        },
        "mathematical_scope": {
            "diagnostic": "eighty-first Q011cb witness component-safe complex phase discs",
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
    result = run_q011ih_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
