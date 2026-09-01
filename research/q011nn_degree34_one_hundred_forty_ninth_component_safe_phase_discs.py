"""Q011nn component-safe complex phase discs for Q011cb flatten ordinal one hundred forty-eight."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

import research.q011jn_degree34_ninety_seventh_component_safe_phase_discs as q011jn
import research.q011nm_degree34_one_hundred_forty_ninth_individual_partition_audit as q011nm
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _strict_json_serializable,
)

q011ih = q011jn.q011ih
q011b = q011nm.q011b
q011z = q011nm.q011z

_ExactDisc = q011jn._ExactDisc

SIZE = 17
DEGREE = 34
PARENT_AGGREGATE_INDEX = 2340
LOCAL_AGGREGATE_INDEX = 0
PARENT_FLAT_ORDINAL = 148
OUTPUT_BLOCK = 7
TARGET_IDENTIFIER = "block=7;center=44"

SOURCE_VARIANTS = q011jn.SOURCE_VARIANTS
SOURCE_POWER_MAXIMUM_COUNTS = (1, 1, 12, 12, 9, 9, 9, 9, 5, 5, 4, 4, 3, 3)
RADIUS_SIGNATURE_REPRESENTATIVE_VARIANTS = q011jn.RADIUS_SIGNATURE_REPRESENTATIVE_VARIANTS
EXPECTED_SOURCE_RADIUS_HEX = q011jn.EXPECTED_SOURCE_RADIUS_HEX
EXPECTED_TARGET_RADIUS_HEX = q011jn.EXPECTED_TARGET_RADIUS_HEX
EXPECTED_SOURCE_RECORD_DIGEST = q011jn.EXPECTED_SOURCE_RECORD_DIGEST
EXPECTED_TARGET_RECORD_DIGEST = q011jn.EXPECTED_TARGET_RECORD_DIGEST

EXPECTED_FULL_ALLOCATION_COUNT = 686_400
EXPECTED_COMPATIBLE_ALLOCATION_COUNT = 37_940
EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT = 3_104
EXPECTED_WAVE_PROJECTION_COUNT = 1_729
EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT = 10
EXPECTED_FULL_ALLOCATION_DIGEST = "99633d4c8608369e1bacd9c9a6f33b081e19a5940f75565de228ec79d2fd31a8"
EXPECTED_COMPATIBLE_ALLOCATION_DIGEST = (
    "eed7bab31c4a886071fced0492633f4b775de51afcc31c651d2614795f4d9a7b"
)
EXPECTED_FIRST_COMPATIBLE_COUNTS = (0, 1, 0, 12, 0, 0, 0, 9, 0, 5, 2, 2, 3, 0)
EXPECTED_LAST_COMPATIBLE_COUNTS = (1, 0, 12, 0, 9, 0, 0, 0, 0, 5, 0, 4, 0, 3)
EXPECTED_WAVE_PROJECTION_DIGEST = "41078c7faa86d52a46b3aa2a648c91a6b466e354499833bb7ced8bf1d5a68e85"
EXPECTED_PHASE_FIBER_HISTOGRAM = {10: 354, 18: 343, 24: 341, 28: 344, 30: 347}
EXPECTED_BRIDGE_FIBER_HISTOGRAM = {1: 354, 2: 1_375}
EXPECTED_BRIDGE_RECORD_DIGEST = "6293fa7a81b43cb61040996d253413b1ef4ece0107f27c803efced0d4b048499"
EXPECTED_PAIRED_RECORD_DIGEST = "d62e5a1b6d4916457725c0eb65abaabcc4bd5021236f2f7a2808ebaac63e2cea"

Q011NM_ARTIFACT_SHA256 = "f65030fb8c265b556fa64729e62f02ab4bc69931521081e1174f31e9ae4aba7e"
Q011NM_RUNNER_SHA256 = "1759625baa7a26c7228df5a7f4a5124515fb5216ef279bc39509250a5e17af7d"
Q011NM_DIGEST_NAMES = (
    "input_digest_sha256",
    "partition_input_digest_sha256",
    "allocation_audit_digest_sha256",
    "result_digest_sha256",
)
Q011NM_DIGESTS = (
    "b19ebf5dfb306e28e357ba686bc728dc1ee2471e3a1107db24dbfed4f7a2fb13",
    "cbff52451036274dcc4b79444e81ebba9010765acafbe8c138b3237bc48777bc",
    "862a138a133d3ce0e97a16c29b1b493fcfec26c52166d91811d95cbebc25db92",
    "5a6504ef53e362177a50674136b0bc31a9dc52497ac017e522c0e79e8fe4413c",
)
EXPECTED_Q011NM_ALLOCATION_RECORD_DIGEST = (
    "d92d0f823a7da05a3523936243ef422ace8bb830467af9e9215300f814cc6300"
)
EXPECTED_Q011NM_ALLOCATION_STREAM_DIGEST = (
    "2acf4a209612016f1dde18973ff8928d24f9ab8dbc5757794bb88ad0939d014d"
)

RESOLVED_CLASSIFICATION = (
    "the component-safe complex phase discs resolve the one-hundred-forty-ninth "
    "Q011cb persistent refined witness"
)
PERSISTENT_CLASSIFICATION = (
    "the one-hundred-forty-ninth Q011cb persistent refined witness persists under "
    "component-safe complex phase discs"
)
INCONCLUSIVE_CLASSIFICATION = "the Q011nn component-safe phase-disc audit is inconclusive"

_Q011IH_PROTOCOL_NAMES = (
    "SOURCE_POWER_MAXIMUM_COUNTS",
    "EXPECTED_COMPATIBLE_ALLOCATION_COUNT",
    "EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT",
    "PARENT_FLAT_ORDINAL",
    "_q011ih_framed_record_digest",
    "_q011ih_exact_fraction_sequence_sha256",
)
_Q011IH_PROTOCOL_BASELINE = {name: getattr(q011ih, name) for name in _Q011IH_PROTOCOL_NAMES}


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _q011nn_framed_record_digest() -> Any:
    return q011ih.q011cx._BASE_FRAMED_RECORD_DIGEST("q011nn-component-safe-phase-comparisons-v1")


def _q011nn_exact_fraction_sequence_sha256(
    _domain: bytes,
    values: tuple[Fraction, ...],
) -> str:
    return q011ih.q011cx._BASE_EXACT_FRACTION_SEQUENCE_SHA256(
        b"q011nn-complex-margin-expression-v1",
        values,
    )


def _protocol_globals_are_restored() -> bool:
    return bool(
        all(getattr(q011ih, name) == value for name, value in _Q011IH_PROTOCOL_BASELINE.items())
        and q011ih._protocol_globals_are_restored()
        and q011jn._protocol_globals_are_restored()
        and q011nm._protocol_globals_are_restored()
    )


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011nm._sealed_input_audit()
    artifacts = dict(artifacts)
    artifact_path = _artifact_directory() / (
        "q011nm_degree34_one_hundred_forty_ninth_individual_partition_audit.json"
    )
    runner_path = Path(q011nm.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    fixed = cycle["fixed_individual_partition_input_audit"]
    partition = cycle["individual_allocation_interval_audit"]
    theorem = cycle["theorem_consequence"]
    digests = tuple(cycle[name] for name in Q011NM_DIGEST_NAMES)
    checks = {
        "q011nm_three_hundred_fifty_five_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"]
            and prior["artifact_count"] == 355
            and prior["direct_digest_count"] == 1_610
            and len(artifacts) == 355
            and all(prior["checks"].values())
        ),
        "q011nm_artifact_and_runner_sha256_match": bool(
            _file_sha256(artifact_path) == Q011NM_ARTIFACT_SHA256
            and _file_sha256(runner_path) == Q011NM_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011NM_RUNNER_SHA256
        ),
        "q011nm_section_digests_match": digests == Q011NM_DIGESTS,
        "q011nm_valid_interval_inert_outcome_and_boundary_reproduce": bool(
            artifact["study_gate"] == "passed"
            and artifact["refinement_outcome"] == "partition_inert_persistent"
            and artifact["scientific_outcome"] == "not_evaluated"
            and artifact["actual_resonance_outcome"] == "not_established"
            and cycle["failed_validity_order"] == []
            and theorem[
                "individual_partition_is_interval_inert_for_one_hundred_forty_ninth_q011cb_witness"
            ]
            and theorem[
                "q011nl_ordinal_one_hundred_forty_seven_phase_resolution_is_preserved"
            ]
            and theorem[
                "q011nk_ordinal_one_hundred_forty_seven_interval_inert_diagnostic_is_preserved"
            ]
            and all(
                value
                for name, value in theorem.items()
                if name.endswith("_is_preserved") and isinstance(value, bool)
            )
            and not theorem["degree_thirty_four_external_nonresonance_is_certified"]
            and theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
            and theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
            and bool(cycle["claim_boundary"])
        ),
        "q011nm_parent_partition_and_relations_reproduce": bool(
            fixed["one_hundred_forty_ninth_parent_witness_selection_audit"]["selected_flat_ordinal"]
            == PARENT_FLAT_ORDINAL
            and fixed["compatible_allocation_count"] == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and fixed["compatible_allocation_digest_sha256"] == q011nm.EXPECTED_COMPATIBLE_DIGEST
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
            == EXPECTED_Q011NM_ALLOCATION_RECORD_DIGEST
            and partition["allocation_classification_stream_digest_sha256"]
            == EXPECTED_Q011NM_ALLOCATION_STREAM_DIGEST
        ),
        "q011nm_artifact_is_finite_strict_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "one_thousand_six_hundred_fourteen_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 1_614
        ),
    }
    artifacts["q011nm"] = artifact
    return (
        {
            "prior_q011nm_sealed_input_audit": prior,
            "q011nm": {
                "artifact_filename": artifact_path.name,
                "artifact_sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "digest_names": list(Q011NM_DIGEST_NAMES),
                "digests": list(digests),
            },
            "artifact_count": len(artifacts),
            "direct_digest_count": prior["direct_digest_count"] + len(digests),
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifacts,
    )


def _complex_from_record(record: dict[str, Any]) -> tuple[Fraction, Fraction]:
    return q011jn._complex_from_record(record)


def _fixed_phase_input_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    tuple[_ExactDisc, ...],
    _ExactDisc,
    tuple[dict[str, Any], ...],
]:
    stored = artifacts["q011nm"]["cycle"]
    fixed = stored["fixed_individual_partition_input_audit"]
    partition = stored["individual_allocation_interval_audit"]
    wave_compatible = tuple(
        {
            "individual_counts": record["individual_counts"],
            "output_block": record["output_block"],
            "compatible": True,
        }
        for record in partition["allocation_classification_records"]
    )
    wave_digest = q011b._canonical_json_sha256(list(wave_compatible))
    q011jn_phase = artifacts["q011jn"]["cycle"]["fixed_component_safe_phase_input_audit"]
    source_records = q011jn_phase["source_phase_disc_records"]
    target_record = q011jn_phase["target_phase_disc_record"]
    source_discs = tuple(
        _ExactDisc(
            identifier=record["identifier"],
            block_index=record["block_index"],
            center_index=record["center_index"],
            center=_complex_from_record(record["center"]),
            radius_kind=record["radius_kind"],
            radius=q011z._fraction(record["radius"]),
            component=(
                tuple(record["gershgorin_component_center_indices"])
                if record["gershgorin_component_center_indices"] is not None
                else None
            ),
        )
        for record in source_records
    )
    target = _ExactDisc(
        identifier=target_record["identifier"],
        block_index=target_record["block_index"],
        center_index=target_record["center_index"],
        center=_complex_from_record(target_record["center"]),
        radius_kind=target_record["radius_kind"],
        radius=q011z._fraction(target_record["radius"]),
        component=None,
    )
    source_digest = q011b._canonical_json_sha256(source_records)
    target_digest = q011b._canonical_json_sha256(target_record)
    conjugate_pairs = ((0, 1), (2, 3), (4, 6), (5, 7), (8, 9), (10, 11), (12, 13))
    memberships = q011jn_phase["active_component_memberships_by_block"]
    active_indices = tuple(range(14))
    checks = {
        "q011nm_fixed_parent_replays_and_stored_interval_partition_is_inert": bool(
            fixed["passed"]
            and partition["passed"]
            and partition["all_product_target_intersection_and_center_records_equal_parent"]
            and partition["exact_relation_counts"]
            == {
                "product_below_target": 0,
                "target_below_product": 0,
                "overlap": EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT,
            }
        ),
        "sealed_q011jn_phase_records_reconstruct_exactly": bool(
            q011jn_phase["passed"]
            and all(q011jn_phase["checks"].values())
            and tuple(record["identifier"] for record in source_records)
            == tuple(identifier for identifier, _kind in SOURCE_VARIANTS)
            and tuple(float(disc.radius).hex() for disc in source_discs)
            == EXPECTED_SOURCE_RADIUS_HEX
            and float(target.radius).hex() == EXPECTED_TARGET_RADIUS_HEX
            and source_digest == EXPECTED_SOURCE_RECORD_DIGEST
            and target_digest == EXPECTED_TARGET_RECORD_DIGEST
        ),
        "registered_all_active_pairs_and_conjugacy_reproduce": bool(
            all(
                component in memberships[str(block)]
                for block in (1, 16)
                for component in ([144], [145], [148], [149], [150, 151])
            )
            and all(SOURCE_POWER_MAXIMUM_COUNTS[index] > 0 for index in active_indices)
            and all(
                source_discs[left].center
                == (source_discs[right].center[0], -source_discs[right].center[1])
                and source_discs[left].radius == source_discs[right].radius
                and source_discs[left].component == source_discs[right].component
                for left, right in conjugate_pairs
            )
        ),
        "component_union_semantics_do_not_assign_internal_labels": bool(
            source_discs[4].component
            == source_discs[5].component
            == source_discs[6].component
            == source_discs[7].component
            == (150, 151)
        ),
        "q011nm_wave_inventory_reconstructs": bool(
            len(wave_compatible) == EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT
            and fixed["compatible_allocation_digest_sha256"] == q011nm.EXPECTED_COMPATIBLE_DIGEST
            and wave_digest == q011nm.EXPECTED_COMPATIBLE_DIGEST
            and tuple(wave_compatible[0]["individual_counts"])
            == q011nm.EXPECTED_FIRST_COMPATIBLE_COUNTS
            and tuple(wave_compatible[-1]["individual_counts"])
            == q011nm.EXPECTED_LAST_COMPATIBLE_COUNTS
        ),
        "fixed_phase_input_is_finite_strict_json": bool(
            _all_numeric_values_finite(source_records)
            and _strict_json_serializable(source_records)
            and json.dumps({"sources": source_records, "target": target_record}, allow_nan=False)
        ),
    }
    audit = {
        "degree": DEGREE,
        "parent_q011bx_aggregate_index": PARENT_AGGREGATE_INDEX,
        "parent_q011cb_local_aggregate_index": LOCAL_AGGREGATE_INDEX,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "target_identifier": TARGET_IDENTIFIER,
        "canonical_source_variant_count": len(source_discs),
        "active_source_variant_count": len(active_indices),
        "inactive_zero_power_identifiers": [],
        "source_phase_disc_records": source_records,
        "source_phase_disc_record_digest_sha256": source_digest,
        "source_radius_binary64_hex": [float(disc.radius).hex() for disc in source_discs],
        "target_phase_disc_record": target_record,
        "target_phase_disc_record_digest_sha256": target_digest,
        "target_radius_binary64_hex": float(target.radius).hex(),
        "active_component_memberships_by_block": memberships,
        "q011nm_compatible_wave_allocation_count": len(wave_compatible),
        "q011nm_compatible_wave_allocation_digest_sha256": wave_digest,
        "wave_inventory_source": "sealed Q011nm allocation-classification records",
        "label_semantics": (
            "each active factor independently selects a row disc from its isolated "
            "component union; no component-internal eigenvalue label is assigned"
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, source_discs, target, wave_compatible


def _component_wave_counts(individual_counts: tuple[int, ...]) -> tuple[int, ...]:
    if len(individual_counts) != 14:
        raise ValueError("Q011nn requires fourteen Q011nm individual counts")
    return (
        *individual_counts[:4],
        individual_counts[4] + individual_counts[6],
        individual_counts[5] + individual_counts[7],
        *individual_counts[8:],
    )


def _phase_wave_counts(phase_counts: list[int]) -> tuple[int, ...]:
    if len(phase_counts) != 14:
        raise ValueError("Q011nn requires fourteen active canonical counts")
    return (
        *phase_counts[:4],
        phase_counts[4] + phase_counts[5],
        phase_counts[6] + phase_counts[7],
        *phase_counts[8:],
    )


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
                            for count_16_148 in range(5):
                                for count_16_149 in range(4):
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
                                        count_16_148,
                                        4 - count_16_148,
                                        count_16_149,
                                        3 - count_16_149,
                                    ]
                                    output_block = (
                                        sum(
                                            count * disc.block_index
                                            for count, disc in zip(
                                                counts, source_discs, strict=True
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
    projection = Counter(_phase_wave_counts(record["counts"]) for record in compatible)
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
        and counts[8] + counts[9] == 4
        and counts[10] + counts[11] == 3
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
            and record["counts"][10] + record["counts"][11] == 4
            and record["counts"][12] + record["counts"][13] == 3
            and all(count >= 0 for count in record["counts"])
            and record["output_block"] == OUTPUT_BLOCK
            for record in compatible
        ),
        "phase_projection_matches_active_component_wave_quotient": bool(
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
            and max(bridge.values()) == 2
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
    active_indices = tuple(range(14))
    audit = {
        "canonical_source_variant_order": [disc.identifier for disc in source_discs],
        "active_source_variant_order": [source_discs[index].identifier for index in active_indices],
        "inactive_zero_power_identifiers": [],
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
            "ordinal_one_hundred_forty_eight_active_totals": [1, 12, 9, 5, 4, 3],
            "canonical_zero_power_indices": [],
            "all_active_singleton_component_wave_pairs_are_active": True,
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
    replacements = {
        "SOURCE_POWER_MAXIMUM_COUNTS": SOURCE_POWER_MAXIMUM_COUNTS,
        "EXPECTED_COMPATIBLE_ALLOCATION_COUNT": EXPECTED_COMPATIBLE_ALLOCATION_COUNT,
        "EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT": EXPECTED_UNIQUE_PRODUCT_RADIUS_COUNT,
        "PARENT_FLAT_ORDINAL": PARENT_FLAT_ORDINAL,
        "_q011ih_framed_record_digest": _q011nn_framed_record_digest,
        "_q011ih_exact_fraction_sequence_sha256": _q011nn_exact_fraction_sequence_sha256,
    }
    try:
        for name, value in replacements.items():
            setattr(q011ih, name, value)
        audit = q011ih._phase_product_audit(source_discs, target, compatible)
    finally:
        for name, value in _Q011IH_PROTOCOL_BASELINE.items():
            setattr(q011ih, name, value)
    audit["comparison_stream_domain"] = "q011nn-component-safe-phase-comparisons-v1"
    return audit


def _registered_parameters() -> dict[str, Any]:
    return {
        "protocol": "q011nn-one-hundred-forty-ninth-component-safe-phase-v1",
        "degree": DEGREE,
        "parent_flat_ordinal": PARENT_FLAT_ORDINAL,
        "output_block": OUTPUT_BLOCK,
        "target_identifier": TARGET_IDENTIFIER,
        "source_variants": [list(record) for record in SOURCE_VARIANTS],
        "source_power_maximum_counts": list(SOURCE_POWER_MAXIMUM_COUNTS),
        "radius_signature_representative_variants": list(RADIUS_SIGNATURE_REPRESENTATIVE_VARIANTS),
        "comparison_stream_domain": "q011nn-component-safe-phase-comparisons-v1",
        "complex_margin_digest_domain": "q011nn-complex-margin-expression-v1",
        "q011nn_allocation_enumerator": {
            "source_runner_sha256": _file_sha256(Path(__file__).resolve()),
            "active_component_wave_records_replace_inherited_wave_records": True,
            "ordinal_one_hundred_forty_eight_active_totals": [1, 12, 9, 5, 4, 3],
            "inactive_zero_power_identifiers": [],
            "protocol_globals_modified": False,
        },
        "component_label_coalescing_bridge": {
            "individual_identifier_count": 14,
            "active_component_wave_identifier_count": 12,
            "canonical_phase_source_identifier_count": 14,
            "active_phase_source_identifier_count": 14,
            "individual_wave_allocation_count": EXPECTED_INDIVIDUAL_WAVE_ALLOCATION_COUNT,
            "component_wave_projection_count": EXPECTED_WAVE_PROJECTION_COUNT,
            "bridge_record_digest_sha256": EXPECTED_BRIDGE_RECORD_DIGEST,
            "paired_record_digest_sha256": EXPECTED_PAIRED_RECORD_DIGEST,
            "internal_component_labels_assumed": False,
        },
    }


_result_digest_sections = q011ih._result_digest_sections


def run_degree_thirty_four_one_hundred_forty_ninth_component_safe_phase_audit() -> dict[str, Any]:
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
        "q011nm_and_all_prior_proof_objects_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "356 artifacts and 1614 direct digests reproduce",
            "value": sealed["checks"],
        },
        "q011nm_parent_partition_and_interval_inert_result_replay": {
            "passed": phase_input["checks"][
                "q011nm_fixed_parent_replays_and_stored_interval_partition_is_inert"
            ],
            "threshold": "ordinal 148, 3104 individual wave allocations and inert result replay",
            "value": phase_input["q011nm_compatible_wave_allocation_digest_sha256"],
        },
        "exact_centers_radii_components_target_and_active_pairs_reproduce": {
            "passed": bool(
                phase_input["checks"]["sealed_q011jn_phase_records_reconstruct_exactly"]
                and phase_input["checks"][
                    "registered_all_active_pairs_and_conjugacy_reproduce"
                ]
            ),
            "threshold": (
                "fourteen canonical and active source discs plus one target reproduce"
            ),
            "value": {
                "source": phase_input["source_phase_disc_record_digest_sha256"],
                "target": phase_input["target_phase_disc_record_digest_sha256"],
            },
        },
        "containment_conjugacy_and_label_free_semantics_pass": {
            "passed": bool(
                phase_input["checks"]["sealed_q011jn_phase_records_reconstruct_exactly"]
                and phase_input["checks"]["component_union_semantics_do_not_assign_internal_labels"]
            ),
            "threshold": "sealed containment, seven conjugate pairs and no internal labels",
            "value": phase_input["checks"],
        },
        "component_safe_allocation_and_active_component_quotient_reproduce": {
            "passed": allocation["passed"],
            "threshold": (
                "3104 individual waves quotient to 1729 active component waves; "
                "686400 total and 37940 compatible phase allocations"
            ),
            "value": allocation["checks"],
        },
        "exact_product_radius_distance_and_categories_close": {
            "passed": comparison["passed"],
            "threshold": (
                "37940 exact products, ten radius signatures, sqrt enclosures and "
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
                == "q011nn_degree34_one_hundred_forty_ninth_component_safe_phase_discs.py"
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
        "only_the_registered_one_hundred_forty_ninth_q011cb_witness_is_refined": {
            "passed": bool(
                not comparison["previous_q011cb_refined_signatures_recomputed"]
                and not comparison["later_q011cb_refined_signatures_recomputed"]
                and not comparison["other_parent_targets_recomputed"]
                and not comparison["other_parent_coalesced_overlaps_recomputed"]
            ),
            "threshold": "ordinal 148 only, one target and no other overlap",
            "value": PARENT_FLAT_ORDINAL,
        },
        "all_component_safe_phase_product_discs_are_processed": {
            "passed": bool(
                validity_passed
                and sum(comparison["category_counts"].values())
                == EXPECTED_COMPATIBLE_ALLOCATION_COUNT
            ),
            "threshold": "all 37940 compatible phase allocations have one category",
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
            "strictly separate every complex product in Q011cb flatten ordinal 148?"
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
        "actual_resonance_outcome": "not_established" if validity_passed else "inconclusive",
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    prior_theorem = artifacts["q011nm"]["cycle"]["theorem_consequence"]
    cycle["theorem_consequence"] = {
        "component_safe_complex_phase_discs_resolve_one_hundred_forty_ninth_q011cb_witness": resolved,
        "one_hundred_forty_ninth_q011cb_witness_persists_under_component_safe_phase_discs": persistent,
        "q011an_component_internal_eigenvalue_labels_are_assumed": False,
        "q011nm_ordinal_one_hundred_forty_eight_interval_inert_diagnostic_is_preserved": True,
        **{name: value for name, value in prior_theorem.items() if name.endswith("_is_preserved")},
        "q011cb_persistent_diagnostic_is_preserved": True,
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
        "ordinal 148, its 3104-to-1729 active component-wave quotient and 37940 "
        "registered component-safe phase allocations and target block=7;center=44. "
        "All fourteen canonical source variants are active. It does not reevaluate "
        "ordinals 0 through 147 or classify the later 44651 "
        "Q011cb refined signatures, the other 31 parent coalesced overlaps, other "
        "targets, aggregate 2340 as a whole, aggregate 972 or the full degree-34 "
        "sweep. Product-disc overlap does not establish an actual resonance. The "
        "audit leaves all prior rejection, persistence, interval-inert and "
        "phase-resolution results, certified degrees 2--33 and 91+, and missing "
        "degrees 34--90 unchanged, and makes no claim about degree-34 or all-order "
        "nonresonance, higher graph smoothness, SSM existence or uniqueness, normal "
        "attraction, a basin, other grids, forcing, walls or D3Q27."
    )
    cycle["next_change"] = (
        "Preregister Q011no to audit flatten ordinal 149 in registered order."
        if resolved
        else (
            "Preregister Q011no to refine only the first unresolved component-safe phase witness."
        )
        if persistent
        else "Repair only the first Q011nn validity failure."
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and json.dumps(cycle, allow_nan=False)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
        and _protocol_globals_are_restored()
    ):
        raise RuntimeError("Q011nn cycle failed strict serialization or digest")
    return cycle


def run_q011nn_study() -> dict[str, Any]:
    started = perf_counter()
    cycle = run_degree_thirty_four_one_hundred_forty_ninth_component_safe_phase_audit()
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
            "diagnostic": "one-hundred-forty-ninth Q011cb witness component-safe complex phase discs",
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
    result = run_q011nn_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
