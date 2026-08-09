"""Q011w degree-four phase-sensitive output-sector product-disk audit."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from collections.abc import Iterable
from datetime import UTC, datetime
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011o_graph_transform_setup as q011o
import research.q011u_c91_modulus_nonresonance as q011u
import research.q011v_degree3_phase_disks as q011v
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
DEGREE = 4
EXPECTED_DEGREE_AGGREGATE_COUNT = 35
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 126
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 33
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 2
OVERLAP_COUNTS = ((0, 0, 0, 4), (0, 0, 1, 3))
EXTERNAL_GROUP_INDEX = 183
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_MONOMIAL_COUNTS = (330, 480)
EXPECTED_INDEXED_MONOMIAL_COUNT = 810
EXPECTED_EXTERNAL_TARGET_COUNT = 8
EXPECTED_SECTOR_HISTOGRAMS = (
    {0: 84, 1: 64, 2: 38, 3: 16, 4: 5, 13: 5, 14: 16, 15: 38, 16: 64},
    {0: 124, 1: 100, 2: 54, 3: 20, 4: 4, 13: 4, 14: 20, 15: 54, 16: 100},
)
EXPECTED_TARGET_SECTOR_HISTOGRAM = {0: 4, 2: 2, 15: 2}
EXPECTED_COMPARISON_COUNTS = (488, 712)
EXPECTED_COMPATIBLE_COMPARISON_COUNT = 1200
MINIMUM_COMPLEX_SEPARATION = Fraction(1, 500)

Q011L_SOURCE_SHA256 = "59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7"
Q011O_SOURCE_SHA256 = "60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f"

Q011K_ARTIFACT_SHA256 = "8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a"
Q011K_RUNNER_SHA256 = "d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07"
Q011K_DIGESTS = (
    "f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2",
    "f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc",
    "7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8",
    "1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4",
    "2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e",
)
Q011K_DIGEST_NAMES = (
    "input_digest_sha256",
    "root_digest_sha256",
    "block_digest_sha256",
    "proof_digest_sha256",
    "result_digest_sha256",
)
Q011K_CLASSIFICATION = (
    "the exact repaired fixed point has a rigorously stable and quadratically "
    "nonresonant selected/external spectral split"
)

Q011U_ARTIFACT_SHA256 = "4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4"
Q011U_RUNNER_SHA256 = "fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e"
Q011U_DIGESTS = (
    "ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4",
    "55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94",
    "a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d",
    "10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5",
    "5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c",
    "307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6",
    "b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c",
)
Q011U_DIGEST_NAMES = (
    "input_digest_sha256",
    "cutoff_digest_sha256",
    "spectrum_digest_sha256",
    "log_digest_sha256",
    "enumeration_digest_sha256",
    "tail_digest_sha256",
    "result_digest_sha256",
)
Q011U_CLASSIFICATION = (
    "the C91 localization and degree-91 tail are certified, but modulus-only "
    "nonresonance through degree 90 is obstructed"
)

Q011V_ARTIFACT_SHA256 = "639afa89ccecadb428c4cb1c16a60ad7f788cc4786cdbb0ac2a5e681744bc663"
Q011V_RUNNER_SHA256 = "f9e7b0ffb353bc9f462616b42943860ecc4431b15176be7ca405c894d4d4a8cd"
Q011V_DIGESTS = (
    "10153049ce3cc7f50aa5a57ca6f4e8f92556bbefb3980e1d4c7dd61164aab470",
    "591e6261238ac2253b0e0f11aaa13ce8a0c78948780633ea890a824ea9c5ccba",
    "8988ade3f1fc974423040a2fe168904eb6610897f281e681387da7e3e2d3e919",
    "a93737bcf662b154fcbea83905d733628e1ae397f4f70265d811e7ce657665db",
    "1a2a83c6ae0d6f512a48f5f6d20e869abd0b69126504adbf5ba50054e1b749fc",
)
Q011V_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "sector_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)

ACCEPTED_CLASSIFICATION = (
    "degree-4 external nonresonance is certified by modulus separation plus "
    "Fourier-sector phase-sensitive elimination of both overlap aggregates"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-4 modulus aggregate retains a phase-sensitive product-disc overlap"
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


def _fraction(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _exact_fraction_record(value: Fraction) -> dict[str, str]:
    return {
        "numerator_base16": hex(value.numerator),
        "denominator_base16": hex(value.denominator),
    }


def _exact_complex_record(
    value: tuple[Fraction, Fraction],
) -> dict[str, dict[str, str]]:
    return {
        "real": _exact_fraction_record(value[0]),
        "imaginary": _exact_fraction_record(value[1]),
    }


class _FramedRecordDigest:
    """Hash a record sequence without retaining its large exact payload."""

    def __init__(self, domain: str) -> None:
        self._digest = hashlib.sha256()
        encoded_domain = domain.encode("utf-8")
        self._digest.update(len(encoded_domain).to_bytes(8, "big"))
        self._digest.update(encoded_domain)
        self.count = 0

    def update(self, record: dict[str, Any]) -> None:
        encoded = json.dumps(
            record,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        self._digest.update(len(encoded).to_bytes(8, "big"))
        self._digest.update(encoded)
        self.count += 1

    def hexdigest(self) -> str:
        return self._digest.hexdigest()


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    directory = _artifact_directory()
    specifications = (
        (
            "q011k",
            directory / "q011k_interval_spectral_split.json",
            Path(q011k.__file__).resolve(),
            Q011K_ARTIFACT_SHA256,
            Q011K_RUNNER_SHA256,
            Q011K_DIGESTS,
            Q011K_DIGEST_NAMES,
            "accepted",
            Q011K_CLASSIFICATION,
        ),
        (
            "q011u",
            directory / "q011u_c91_modulus_nonresonance.json",
            Path(q011u.__file__).resolve(),
            Q011U_ARTIFACT_SHA256,
            Q011U_RUNNER_SHA256,
            Q011U_DIGESTS,
            Q011U_DIGEST_NAMES,
            "rejected",
            Q011U_CLASSIFICATION,
        ),
        (
            "q011v",
            directory / "q011v_degree3_phase_disks.json",
            Path(q011v.__file__).resolve(),
            Q011V_ARTIFACT_SHA256,
            Q011V_RUNNER_SHA256,
            Q011V_DIGESTS,
            Q011V_DIGEST_NAMES,
            "accepted",
            q011v.ACCEPTED_CLASSIFICATION,
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
    checks["q011k_eigendisc_scope_is_preserved"] = bool(
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and k_theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011u_c91_tail_and_valid_rejection_scope_is_preserved"] = bool(
        u_theorem["a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"]
        and u_theorem["the_degree_91_and_higher_modulus_tail_is_certified"]
        and not u_theorem["degrees_3_through_90_modulus_only_nonresonance_is_certified"]
        and not u_theorem["an_actual_complex_resonance_is_established"]
    )
    checks["q011v_degree_three_certificate_and_boundary_are_preserved"] = bool(
        v_theorem["degree_three_external_nonresonance_is_certified"]
        and v_theorem["certified_external_nonresonance_degrees"] == [2, 3]
        and v_theorem["missing_external_nonresonance_degrees"] == list(range(4, 91))
        and not v_theorem["degrees_4_through_90_are_certified"]
        and not v_theorem["ssm_existence_or_uniqueness_is_certified"]
    )
    l_path = Path(q011l.__file__).resolve()
    o_path = Path(q011o.__file__).resolve()
    v_helpers = artifacts["q011v"]["cycle"]["sealed_input_audit"]["helper_sources"]
    checks["q011l_source_sha256_matches"] = bool(
        _file_sha256(l_path) == Q011L_SOURCE_SHA256
        and v_helpers["q011l"]["sha256"] == Q011L_SOURCE_SHA256
    )
    checks["q011o_source_sha256_matches"] = bool(
        _file_sha256(o_path) == Q011O_SOURCE_SHA256
        and v_helpers["q011o"]["sha256"] == Q011O_SOURCE_SHA256
    )
    checks["seventeen_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 17
    )
    audit = {
        **records,
        "helper_sources": {
            "q011l": {"filename": l_path.name, "sha256": _file_sha256(l_path)},
            "q011o": {"filename": o_path.name, "sha256": _file_sha256(o_path)},
        },
        "direct_digest_count": 17,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _count_tuples(degree: int) -> Iterable[tuple[int, int, int, int]]:
    for n0 in range(degree + 1):
        for n1 in range(degree - n0 + 1):
            for n2 in range(degree - n0 - n1 + 1):
                yield (n0, n1, n2, degree - n0 - n1 - n2)


def _scaled_log_pair(record: dict[str, Any]) -> tuple[int, int]:
    interval = record["log_interval"]
    return (
        int(interval["lower_scaled_integer"]),
        int(interval["upper_scaled_integer"]),
    )


def _inventory_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, q011v._EigenDisc],
    tuple[tuple[str, ...], ...],
    tuple[str, ...],
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
    external_targets = tuple(sorted(external_merged[EXTERNAL_GROUP_INDEX].identifiers))

    selected_logs = tuple(_scaled_log_pair(record) for record in u_logs["selected_log_records"])
    external_logs = tuple(_scaled_log_pair(record) for record in u_logs["external_log_records"])
    overlap_records = []
    for counts in _count_tuples(DEGREE):
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
        if not external_indices:
            continue
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

    stored_selected = u_spectrum["selected_merged_records"]
    stored_external = u_spectrum["external_merged_records"]
    selected_membership_checks = [
        q011v.q011b._canonical_json_sha256(list(group))
        == stored_selected[index]["membership_digest_sha256"]
        for index, group in enumerate(selected_groups)
    ]
    external_membership_check = bool(
        q011v.q011b._canonical_json_sha256(list(external_targets))
        == stored_external[EXTERNAL_GROUP_INDEX]["membership_digest_sha256"]
    )
    first_overlap = degree_record["first_overlap"]
    exact_inventory = {
        "selected_source_groups": [
            {"group_index": index, "identifiers": list(group)}
            for index, group in enumerate(selected_groups)
        ],
        "overlap_records": overlap_records,
        "external_group_index": EXTERNAL_GROUP_INDEX,
        "external_identifiers": list(external_targets),
    }
    checks = {
        "q011u_degree_four_record_is_unique_and_complete": bool(
            degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "both_overlap_count_tuples_and_external_groups_reproduce": bool(
            tuple(tuple(record["selected_type_counts"]) for record in overlap_records)
            == OVERLAP_COUNTS
            and all(
                record["external_group_indices"] == [EXTERNAL_GROUP_INDEX]
                for record in overlap_records
            )
            and tuple(first_overlap["selected_type_counts"]) == OVERLAP_COUNTS[0]
            and first_overlap["external_group_index"] == EXTERNAL_GROUP_INDEX
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
        "external_group_183_has_eight_matching_members": bool(
            len(external_targets) == EXPECTED_EXTERNAL_TARGET_COUNT and external_membership_check
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
        "external_target_group_index": EXTERNAL_GROUP_INDEX,
        "external_target_identifiers": list(external_targets),
        "exact_inventory_digest_sha256": q011v.q011b._canonical_json_sha256(exact_inventory),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        lookup,
        selected_groups,
        external_targets,
        tuple(overlap_records),
    )


def _monomial_count_for_counts(
    selected_groups: tuple[tuple[str, ...], ...],
    counts: tuple[int, int, int, int],
) -> int:
    total = 1
    for group, count in zip(selected_groups, counts, strict=True):
        if count:
            total *= comb(len(group) + count - 1, count)
    return total


def _sector_audit(
    artifacts: dict[str, dict[str, Any]],
    lookup: dict[str, q011v._EigenDisc],
    selected_groups: tuple[tuple[str, ...], ...],
    external_targets: tuple[str, ...],
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
    target_histogram = Counter(lookup[identifier].block_index for identifier in external_targets)
    compatible_pairs = [
        (record["monomial_index"], target_identifier)
        for record in monomial_records
        for target_identifier in external_targets
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

    v_sector = artifacts["q011v"]["cycle"]["fourier_output_sector_audit"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    structural_wave_sum = bool(
        v_sector["passed"]
        and all(v_sector["structural_proof"].values())
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
        "translation_equivariance_and_c91_regular_map_give_quartic_wave_sum": (structural_wave_sum),
        "combination_with_replacement_counts_reproduce": bool(
            tuple(monomial_counts) == EXPECTED_MONOMIAL_COUNTS
            and all(
                count == _monomial_count_for_counts(selected_groups, counts)
                for count, counts in zip(monomial_counts, OVERLAP_COUNTS, strict=True)
            )
        ),
        "all_810_and_only_degree_four_overlap_monomials_are_enumerated": bool(
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
        "registered_target_sector_histogram_reproduces": (
            dict(sorted(target_histogram.items())) == EXPECTED_TARGET_SECTOR_HISTOGRAM
        ),
        "all_1200_and_only_compatible_comparisons_are_enumerated": bool(
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
        "output_sector_law": "b_out=(b_1+b_2+b_3+b_4) mod 17",
        "structural_proof": {
            "q011v_translation_equivariant_wave_sum_is_preserved": bool(
                v_sector["passed"] and all(v_sector["structural_proof"].values())
            ),
            "q011u_c91_regular_original_map_is_preserved": u_theorem[
                "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
            ],
            "translation_equivariance_applies_at_quartic_order": structural_wave_sum,
        },
        "indexed_monomial_count": len(monomial_records),
        "aggregate_monomial_counts": monomial_counts,
        "aggregate_sector_histograms": [
            {str(key): value for key, value in sorted(histogram.items())}
            for histogram in sector_histograms
        ],
        "external_target_count": len(external_targets),
        "external_target_sector_histogram": {
            str(key): value for key, value in sorted(target_histogram.items())
        },
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


def _product_radius_expansion(
    center_modulus_uppers: tuple[Fraction, ...],
    radii: tuple[Fraction, ...],
) -> Fraction:
    total = Fraction(0)
    for mask in range(1, 1 << len(radii)):
        term = Fraction(1)
        for index in range(len(radii)):
            term *= radii[index] if mask & (1 << index) else center_modulus_uppers[index]
        total += term
    return total


def _cached_center_modulus(
    cache: dict[tuple[Fraction, Fraction], RationalInterval],
    value: tuple[Fraction, Fraction],
) -> RationalInterval:
    if value not in cache:
        cache[value] = q011o._center_modulus_bounds(value)
    return cache[value]


def _margin_witness(
    monomial: dict[str, Any],
    target_identifier: str,
    classification: str,
    margin: Fraction,
) -> dict[str, Any]:
    return {
        "monomial_index": monomial["monomial_index"],
        "aggregate_index": monomial["aggregate_index"],
        "selected_type_counts": monomial["selected_type_counts"],
        "source_identifiers": monomial["source_identifiers"],
        "output_block": monomial["output_block"],
        "target_identifier": target_identifier,
        "classification": classification,
        "complex_separation_margin_lower": _fraction_record(margin),
    }


def _product_disk_audit(
    lookup: dict[str, q011v._EigenDisc],
    monomial_records: list[dict[str, Any]],
    compatible_pairs: list[tuple[int, str]],
) -> tuple[dict[str, Any], Fraction]:
    product_framer = _FramedRecordDigest("Q011w/exact-product-record/v1")
    comparison_framer = _FramedRecordDigest("Q011w/exact-comparison-record/v1")
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
        expansion_radius = _product_radius_expansion(
            center_modulus_uppers,
            radii,
        )
        radius_identities_hold = bool(radius_identities_hold and product_radius == expansion_radius)
        center_modulus = _cached_center_modulus(modulus_cache, product_center)
        product_modulus = RationalInterval(
            max(Fraction(0), center_modulus.lower - product_radius),
            center_modulus.upper + product_radius,
        )
        product_framer.update(
            {
                "monomial_index": monomial["monomial_index"],
                "product_center": _exact_complex_record(product_center),
                "product_radius": _exact_fraction_record(product_radius),
                "product_center_modulus_lower": _exact_fraction_record(center_modulus.lower),
                "product_center_modulus_upper": _exact_fraction_record(center_modulus.upper),
                "product_modulus_lower": _exact_fraction_record(product_modulus.lower),
                "product_modulus_upper": _exact_fraction_record(product_modulus.upper),
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
        distance = _cached_center_modulus(modulus_cache, difference)
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
                    None if modulus_gap is None else _exact_fraction_record(modulus_gap)
                ),
                "target_modulus_lower": _exact_fraction_record(target.modulus.lower),
                "target_modulus_upper": _exact_fraction_record(target.modulus.upper),
                "center_distance_lower": _exact_fraction_record(distance.lower),
                "center_distance_upper": _exact_fraction_record(distance.upper),
                "combined_disk_radius": _exact_fraction_record(product["radius"] + target.radius),
                "complex_separation_margin_lower": _exact_fraction_record(separation_margin),
            }
        )

        if minimum_margin is None or separation_margin < minimum_margin:
            minimum_margin = separation_margin
            minimum_margin_witness = _margin_witness(
                monomial,
                target_identifier,
                classification,
                separation_margin,
            )
        if classification == "complex_phase_separation" and (
            minimum_phase_margin is None or separation_margin < minimum_phase_margin
        ):
            minimum_phase_margin = separation_margin
            minimum_phase_witness = _margin_witness(
                monomial,
                target_identifier,
                classification,
                separation_margin,
            )
        if classification == "unresolved_product_disk_overlap" and first_unresolved is None:
            first_unresolved = _margin_witness(
                monomial,
                target_identifier,
                classification,
                separation_margin,
            )

    if minimum_margin is None:
        raise RuntimeError("Q011w has no sector-compatible product-disk comparison")
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
        "all_810_product_centers_and_radii_are_reconstructed": bool(
            product_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
            and len(internal_products) == EXPECTED_INDEXED_MONOMIAL_COUNT
            and radius_identities_hold
        ),
        "triangle_inequality_product_disk_formula_is_exact": bool(
            radius_identities_hold
            and all(product["radius"] >= 0 for product in internal_products.values())
        ),
        "all_1200_compatible_comparisons_are_evaluated": (
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
            "center": "C=product_i(c_i), i=1..4",
            "radius": "R=product_i(u_i+r_i)-product_i(u_i), i=1..4",
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
        "external_group_index": EXTERNAL_GROUP_INDEX,
        "aggregate_monomial_counts": list(EXPECTED_MONOMIAL_COUNTS),
        "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
        "external_target_count": EXPECTED_EXTERNAL_TARGET_COUNT,
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


def run_degree4_phase_disk_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    (
        inventory,
        lookup,
        selected_groups,
        external_targets,
        overlap_records,
    ) = _inventory_audit(artifacts)
    sector, monomial_records, compatible_pairs = _sector_audit(
        artifacts,
        lookup,
        selected_groups,
        external_targets,
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
    inventory_sections = {"degree4_modulus_inventory_audit": inventory}
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
        "three_inputs_seventeen_digests_and_helper_sources_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/v artifacts, runners, 17 digests, outcomes and claim "
                "boundaries plus Q011l/o sources reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_four_inventory_and_both_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "35 aggregates, 33 separated, [0,0,0,4] and [0,0,1,3] "
                "overlaps with external group 183"
            ),
            "value": inventory["checks"],
        },
        "memberships_330_480_monomials_and_eight_targets_reproduce": {
            "passed": bool(
                inventory["passed"]
                and inventory["selected_source_group_sizes"] == list(EXPECTED_SELECTED_GROUP_SIZES)
                and sector["aggregate_monomial_counts"] == list(EXPECTED_MONOMIAL_COUNTS)
                and sector["indexed_monomial_count"] == EXPECTED_INDEXED_MONOMIAL_COUNT
                and len(inventory["external_target_identifiers"]) == EXPECTED_EXTERNAL_TARGET_COUNT
            ),
            "threshold": (
                "selected groups 8/4/4/8, 330+480 commutative monomials and 8 external targets"
            ),
            "value": {
                "selected_group_sizes": inventory["selected_source_group_sizes"],
                "aggregate_monomial_counts": sector["aggregate_monomial_counts"],
                "external_target_count": len(inventory["external_target_identifiers"]),
            },
        },
        "fourier_sum_histograms_and_1200_compatible_comparisons_reproduce": {
            "passed": sector["passed"],
            "threshold": (
                "quartic x-Fourier sum, registered monomial/target histograms "
                "and 488+712 compatible comparisons"
            ),
            "value": sector["checks"],
        },
        "all_product_disk_and_complex_distance_formulas_reproduce": {
            "passed": product["passed"],
            "threshold": (
                "810 exact product disks and 1200 exact "
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
        "x_translation_equivariance_gives_the_exact_quartic_output_sector_sum": {
            "passed": bool(validity_passed and sector_law),
            "threshold": "b_out=(b_1+b_2+b_3+b_4) mod 17",
            "value": sector["structural_proof"],
        },
        "inventory_monomials_and_targets_cover_all_degree_four_cases": {
            "passed": bool(validity_passed and complete_coverage),
            "threshold": (
                "35 aggregates plus 810 overlap monomials and 1200 sector-compatible comparisons"
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
            "threshold": "minimum exact complex separation lower >=1/500",
            "value": product["minimum_complex_separation_lower"],
        },
        "complex_phase_strictly_resolves_at_least_one_modulus_overlap": {
            "passed": bool(validity_passed and phase_adds_information),
            "threshold": ("at least one modulus-overlap comparison is separated by phase"),
            "value": product["complex_phase_separation_count"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011w degree-four phase audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Does Fourier-sector filtering plus exact complex product-disk "
            "separation eliminate both degree-four modulus-overlap aggregates?"
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
    degree_four_certified = bool(validity_passed and hypotheses_passed)
    certified_degrees = [2, 3, 4] if degree_four_certified else [2, 3]
    missing_start = 5 if degree_four_certified else 4
    cycle["theorem_consequence"] = {
        "q011u_degree_four_modulus_inventory_is_reproduced": validity_passed,
        "both_degree_four_modulus_overlaps_are_phase_sensitively_eliminated": (
            degree_four_certified
        ),
        "degree_four_external_nonresonance_is_certified": (degree_four_certified),
        "certified_external_nonresonance_degrees": certified_degrees,
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(missing_start, 91)),
        "degrees_5_through_90_are_certified": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_q011u_or_q011v_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree four for the fixed 17x17 repaired "
        "exact map on one fixed conservation leaf, the two Q011u "
        "modulus-overlap aggregates, Q011k eigendiscs, x-Fourier output "
        "sectors and the registered product-disk formula. It certifies no "
        "degree from 5 through 90, no all-order nonresonance, equality with "
        "the Q011t graph, C2 or higher graph smoothness, SSM existence or "
        "uniqueness, explicit higher-smoothness radius, normal attraction, "
        "basin, other grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011v_degree_three_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011x to extend the same Fourier-sector and "
            "phase-sensitive product-disk audit to the two degree-five "
            "modulus-overlap aggregates."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Send only the first unresolved degree-four product disk to a "
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
        raise RuntimeError("Q011w cycle failed strict serialization or digest")
    return cycle


def run_q011w_study() -> dict[str, Any]:
    cycle = run_degree4_phase_disk_audit()
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
            "diagnostic": ("degree-four phase-sensitive output-sector product disks"),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_four_external_nonresonance_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "degrees_5_through_90_claim": False,
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
    result = run_q011w_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
