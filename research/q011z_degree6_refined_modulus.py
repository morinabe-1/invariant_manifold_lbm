"""Q011z degree-six uniform refined-envelope indexed-modulus certificate."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011o_graph_transform_setup as q011o
import research.q011u_c91_modulus_nonresonance as q011u
import research.q011x_degree5_phase_disks as q011x
import research.q011y_transformed_residual_eigendiscs as q011y
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
DEGREE = 6
EXPECTED_DEGREE_AGGREGATE_COUNT = 84
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 462
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 81
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 3
OVERLAP_COUNTS = ((0, 2, 1, 3), (0, 2, 2, 2), (0, 3, 1, 2))
EXTERNAL_GROUP_INDICES = (178, 178, 177)
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
EXPECTED_EXTERNAL_TARGET_COUNTS = (4, 4, 8)
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 12
EXPECTED_MONOMIAL_COUNTS = (4800, 3600, 2880)
EXPECTED_INDEXED_MONOMIAL_COUNT = 11280
EXPECTED_SECTOR_HISTOGRAMS = (
    {
        0: 820,
        1: 760,
        2: 600,
        3: 380,
        4: 178,
        5: 60,
        6: 12,
        11: 12,
        12: 60,
        13: 178,
        14: 380,
        15: 600,
        16: 760,
    },
    {
        0: 628,
        1: 560,
        2: 459,
        3: 278,
        4: 138,
        5: 42,
        6: 9,
        11: 9,
        12: 42,
        13: 138,
        14: 278,
        15: 459,
        16: 560,
    },
    {
        0: 420,
        1: 404,
        2: 348,
        3: 260,
        4: 150,
        5: 56,
        6: 12,
        11: 12,
        12: 56,
        13: 150,
        14: 260,
        15: 348,
        16: 404,
    },
)
EXPECTED_TARGET_SECTOR_HISTOGRAMS = (
    {2: 2, 15: 2},
    {2: 2, 15: 2},
    {0: 4, 3: 2, 14: 2},
)
EXPECTED_COMPARISON_COUNTS = (2400, 1836, 2720)
EXPECTED_COMPATIBLE_COMPARISON_COUNT = 6956
UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
MINIMUM_MODULUS_GAP = Fraction(5, 10**6)

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

Q011X_ARTIFACT_SHA256 = "11ef4d47f60840c4bc05c4056024e2af14b8339a8983b65dcb878bd355cfc328"
Q011X_RUNNER_SHA256 = "62712392faca2c154883edd93792f81e60ff975f6da16010aa3190ee44657a18"
Q011X_DIGESTS = (
    "9d13fa470f4c0bd8efa13868af90c6931025d7f3007e600c66af05bd0037a7ed",
    "717c4eadbd0e5f160a87de8846968933b8c5fbe604d769f215b6dcc65dacc955",
    "d31b7ea3cfcd7eca9d936cded13a1dc316e64dc2fc088bda745ea927d15ce52c",
    "add9d07725802c5fba84b68a207d5adc6f3f405a152a22f88059259f9a255222",
    "608bb3a7aee34a833e7980dbd18f4a3e641426966352126833f298e282437b31",
)
Q011X_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "sector_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)

Q011Y_ARTIFACT_SHA256 = "2886708898f634b3ff85587f3f4b9257d35e14f25b4e3b4524fd01f4c12a254a"
Q011Y_RUNNER_SHA256 = "0017ea849f518c69ce93a36db349bd8b18246b678fef9a54a48ae5f6f1acd187"
Q011Y_DIGESTS = (
    "a31fe1606f7be3931567ec63bbad3037d38a9a57eef43f73d7b8f9afc7523c03",
    "f3b9518fe67e85f0e701c4e6a97eac95db188ce85f813e358ddc0ecf85ba1ad5",
    "70919d4697068d7500609551a17325533e83f40bb2e309f5e98b3313a6a93ee5",
    "54e13cb993a0b99bc2d85dcf687d470cebe5692b4d10ab03865115230c53712c",
    "933d2841e5501bd48827ead0ea836fb54ebca7f42e36f8bc6228c3f7dcfaaa4b",
    "51d83bad9b0c2188c05b147f0075b5e7f05f3dea0dd291e0c282e9236914bff8",
)
Q011Y_DIGEST_NAMES = (
    "input_digest_sha256",
    "theorem_digest_sha256",
    "radius_digest_sha256",
    "containment_digest_sha256",
    "witness_digest_sha256",
    "result_digest_sha256",
)
Q011L_SOURCE_SHA256 = "59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7"
Q011O_SOURCE_SHA256 = "60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f"

ACCEPTED_CLASSIFICATION = (
    "degree-6 external nonresonance is certified by a contained uniform "
    "transformed-residual envelope and exact Fourier-sector indexed-modulus products"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-6 refined indexed-modulus product remains "
    "inseparable from an external target"
)


@dataclass(frozen=True)
class _UniformDisc:
    identifier: str
    block_index: int
    center_index: int
    center_modulus: RationalInterval
    modulus: RationalInterval


class _FramedRecordDigest:
    """Hash an ordered exact record stream without retaining its payload."""

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


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


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


def _digest_tuple(cycle: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cycle[name] for name in names)


def _identifier_indices(identifier: str) -> tuple[int, int]:
    block_text, center_text = identifier.split(";")
    return int(block_text.split("=")[1]), int(center_text.split("=")[1])


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


def _monomial_count_for_counts(
    selected_groups: tuple[tuple[str, ...], ...],
    counts: tuple[int, int, int, int],
) -> int:
    result = 1
    for group, count in zip(selected_groups, counts, strict=True):
        numerator = 1
        denominator = 1
        for index in range(1, count + 1):
            numerator *= len(group) + index - 1
            denominator *= index
        result *= numerator // denominator
    return result


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
            "q011x",
            directory / "q011x_degree5_phase_disks.json",
            Path(q011x.__file__).resolve(),
            Q011X_ARTIFACT_SHA256,
            Q011X_RUNNER_SHA256,
            Q011X_DIGESTS,
            Q011X_DIGEST_NAMES,
            "accepted",
            q011x.ACCEPTED_CLASSIFICATION,
        ),
        (
            "q011y",
            directory / "q011y_transformed_residual_eigendiscs.json",
            Path(q011y.__file__).resolve(),
            Q011Y_ARTIFACT_SHA256,
            Q011Y_RUNNER_SHA256,
            Q011Y_DIGESTS,
            Q011Y_DIGEST_NAMES,
            "accepted",
            q011y.ACCEPTED_CLASSIFICATION,
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
        checks[f"{label}_claim_boundary_is_present"] = bool(cycle["claim_boundary"])
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
    x_theorem = artifacts["q011x"]["cycle"]["theorem_consequence"]
    y_theorem = artifacts["q011y"]["cycle"]["theorem_consequence"]
    checks["q011k_stable_split_scope_is_preserved"] = bool(
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and k_theorem["selected_and_external_spectral_unions_do_not_exchange"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011u_inventory_tail_and_rejection_scope_are_preserved"] = bool(
        u_theorem["a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"]
        and u_theorem["the_degree_91_and_higher_modulus_tail_is_certified"]
        and not u_theorem["an_actual_complex_resonance_is_established"]
    )
    checks["q011x_degree_two_through_five_scope_is_preserved"] = bool(
        x_theorem["certified_external_nonresonance_degrees"] == [2, 3, 4, 5]
        and x_theorem["missing_external_nonresonance_degrees"] == list(range(6, 91))
        and not x_theorem["degrees_6_through_90_are_certified"]
    )
    checks["q011y_contained_refinement_and_boundary_are_preserved"] = bool(
        y_theorem["transformed_residual_eigendisc_inclusion_is_certified"]
        and y_theorem["all_refined_discs_are_contained_in_q011k_discs"]
        and not y_theorem["all_degree_six_external_nonresonances_are_certified"]
        and not y_theorem["ssm_existence_or_uniqueness_is_certified"]
    )
    l_path = Path(q011l.__file__).resolve()
    o_path = Path(q011o.__file__).resolve()
    checks["q011l_source_sha256_matches"] = _file_sha256(l_path) == Q011L_SOURCE_SHA256
    checks["q011o_source_sha256_matches"] = _file_sha256(o_path) == Q011O_SOURCE_SHA256
    checks["twenty_three_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 23
    )
    audit = {
        **records,
        "helper_sources": {
            "q011l": {"filename": l_path.name, "sha256": _file_sha256(l_path)},
            "q011o": {"filename": o_path.name, "sha256": _file_sha256(o_path)},
        },
        "direct_digest_count": 23,
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
    selected_logs = tuple(_scaled_log_pair(record) for record in log_audit["selected_log_records"])
    external_logs = tuple(_scaled_log_pair(record) for record in log_audit["external_log_records"])
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
            external_target_groups,
            EXTERNAL_GROUP_INDICES,
            strict=True,
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
        "q011u_degree_six_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_three_overlap_tuples_and_external_groups_reproduce": bool(
            tuple(tuple(record["selected_type_counts"]) for record in overlap_records)
            == OVERLAP_COUNTS
            and tuple(record["external_group_indices"][0] for record in overlap_records)
            == EXTERNAL_GROUP_INDICES
            and all(len(record["external_group_indices"]) == 1 for record in overlap_records)
            and tuple(first_overlap["selected_type_counts"]) == OVERLAP_COUNTS[0]
            and first_overlap["external_group_index"] == EXTERNAL_GROUP_INDICES[0]
        ),
        "selected_and_external_component_counts_reproduce": bool(
            len(selected_merged) == 4 and len(external_merged) == 186
        ),
        "selected_source_group_sizes_are_8_4_4_8": (
            tuple(len(group) for group in selected_groups) == EXPECTED_SELECTED_GROUP_SIZES
        ),
        "all_selected_group_memberships_match_q011u": all(selected_membership_checks),
        "external_groups_178_178_177_have_registered_memberships": bool(
            tuple(len(group) for group in external_target_groups) == EXPECTED_EXTERNAL_TARGET_COUNTS
            and len(set().union(*map(set, external_target_groups)))
            == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
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
        "old_modulus_separated_aggregate_count": degree_record["nonoverlap_count"],
        "old_modulus_overlap_aggregate_count": degree_record["overlap_count"],
        "overlap_records": overlap_records,
        "selected_source_group_sizes": [len(group) for group in selected_groups],
        "selected_source_group_memberships": [list(group) for group in selected_groups],
        "external_target_groups": exact_inventory["external_target_groups"],
        "unique_external_target_count": len(set().union(*map(set, external_target_groups))),
        "old_spectrum_digest_sha256": q011b._canonical_json_sha256(reconstructed_spectrum),
        "exact_inventory_digest_sha256": q011b._canonical_json_sha256(exact_inventory),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return (
        audit,
        selected_groups,
        external_target_groups,
        tuple(overlap_records),
    )


def _uniform_envelope_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
) -> tuple[dict[str, Any], dict[str, _UniformDisc]]:
    centers, selected, old_radii, metrics, reconstruction = q011l._spectral_data(artifacts["q011k"])
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
    relevant_identifiers = sorted(selected_identifiers | external_identifiers)
    selected_sets = {block: frozenset(indices) for block, indices in selected.items()}
    modulus_cache: dict[tuple[Fraction, Fraction], RationalInterval] = {}
    lookup: dict[str, _UniformDisc] = {}
    records = []
    for identifier in relevant_identifiers:
        block, center_index = _identifier_indices(identifier)
        center = centers[block][center_index]
        key = (abs(center[0]), abs(center[1]))
        if key not in modulus_cache:
            modulus_cache[key] = q011o._center_modulus_bounds(center)
        center_modulus = modulus_cache[key]
        modulus = RationalInterval(
            max(Fraction(0), center_modulus.lower - UNIFORM_REFINED_RADIUS),
            center_modulus.upper + UNIFORM_REFINED_RADIUS,
        )
        disc = _UniformDisc(
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
                "center_modulus_lower": _exact_fraction_record(center_modulus.lower),
                "center_modulus_upper": _exact_fraction_record(center_modulus.upper),
                "uniform_modulus_lower": _exact_fraction_record(modulus.lower),
                "uniform_modulus_upper": _exact_fraction_record(modulus.upper),
            }
        )
    checks = {
        "q011l_reconstructs_all_seventeen_blocks": reconstruction["passed"],
        "q011y_registered_maximum_theta_reproduces": bool(
            theta[maximum_theta_block] == _fraction(y_radius["maximum_refined_radius_upper"])
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
        "all_28_relevant_identifiers_have_uniform_modulus_intervals": bool(
            len(lookup) == 28
            and set(lookup) == selected_identifiers | external_identifiers
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


def _sector_audit(
    artifacts: dict[str, dict[str, Any]],
    selected_groups: tuple[tuple[str, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
    overlap_records: tuple[dict[str, Any], ...],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[tuple[int, str]]]:
    monomial_framer = _FramedRecordDigest("Q011z/degree6-monomial/v1")
    pair_framer = _FramedRecordDigest("Q011z/degree6-compatible-pair/v1")
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
            blocks = [_identifier_indices(identifier)[0] for identifier in identifiers]
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
        Counter(_identifier_indices(identifier)[0] for identifier in target_group)
        for target_group in external_target_groups
    ]
    compatible_pairs: list[tuple[int, str]] = []
    comparison_counts = [0] * len(overlap_records)
    compatible_monomial_indices: set[int] = set()
    for record in monomial_records:
        aggregate_index = record["aggregate_index"]
        for target_identifier in external_target_groups[aggregate_index]:
            if record["output_block"] != _identifier_indices(target_identifier)[0]:
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
        "framed_monomial_digest": monomial_framer.hexdigest(),
        "framed_pair_digest": pair_framer.hexdigest(),
    }
    checks = {
        "translation_equivariance_and_c91_regular_map_give_sextic_wave_sum": (structural_wave_sum),
        "combination_with_replacement_counts_reproduce": bool(
            tuple(monomial_counts) == EXPECTED_MONOMIAL_COUNTS
            and all(
                count == _monomial_count_for_counts(selected_groups, counts)
                for count, counts in zip(
                    monomial_counts,
                    OVERLAP_COUNTS,
                    strict=True,
                )
            )
        ),
        "all_11280_and_only_degree_six_overlap_monomials_are_enumerated": bool(
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
        "all_6956_and_only_compatible_comparisons_are_enumerated": bool(
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
        "output_sector_law": ("b_out=(b_1+b_2+b_3+b_4+b_5+b_6) mod 17"),
        "structural_proof": {
            "q011x_translation_equivariant_wave_sum_is_preserved": bool(
                x_sector["passed"] and all(x_sector["structural_proof"].values())
            ),
            "q011u_c91_regular_original_map_is_preserved": u_theorem[
                "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
            ],
            "six_fourier_characters_multiply_to_the_sum_character": True,
            "translation_equivariance_applies_at_sextic_order": structural_wave_sum,
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


def _minimum_witness(
    monomial: dict[str, Any],
    target_identifier: str,
    relation: str,
    gap: Fraction,
) -> dict[str, Any]:
    return {
        "aggregate_index": monomial["aggregate_index"],
        "selected_type_counts": monomial["selected_type_counts"],
        "source_identifiers": monomial["source_identifiers"],
        "output_block": monomial["output_block"],
        "target_identifier": target_identifier,
        "individual_modulus_relation": relation,
        "modulus_gap": _fraction_record(gap),
    }


def _product_audit(
    lookup: dict[str, _UniformDisc],
    monomial_records: list[dict[str, Any]],
    compatible_pairs: list[tuple[int, str]],
) -> tuple[dict[str, Any], Fraction]:
    product_framer = _FramedRecordDigest("Q011z/exact-modulus-product/v1")
    comparison_framer = _FramedRecordDigest("Q011z/exact-modulus-comparison/v1")
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
        internal_products.append(
            {
                "radius": product_radius,
                "modulus": modulus,
            }
        )
        product_framer.update(
            {
                "monomial_index": monomial["monomial_index"],
                "aggregate_index": monomial["aggregate_index"],
                "center_modulus_lower_product": _exact_fraction_record(center_lower_product),
                "center_modulus_upper_product": _exact_fraction_record(center_upper_product),
                "uniform_product_radius": _exact_fraction_record(product_radius),
                "product_modulus_lower": _exact_fraction_record(modulus.lower),
                "product_modulus_upper": _exact_fraction_record(modulus.upper),
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
    for comparison_index, (monomial_index, target_identifier) in enumerate(compatible_pairs):
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
                "product_modulus_lower": _exact_fraction_record(product_modulus.lower),
                "product_modulus_upper": _exact_fraction_record(product_modulus.upper),
                "target_modulus_lower": _exact_fraction_record(target.modulus.lower),
                "target_modulus_upper": _exact_fraction_record(target.modulus.upper),
                "individual_modulus_relation": relation,
                "modulus_gap": (None if gap is None else _exact_fraction_record(gap)),
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
        witness = _minimum_witness(monomial, target_identifier, relation, gap)
        if minimum_gap is None or gap < minimum_gap:
            minimum_gap = gap
            minimum_witness = witness
        if aggregate_minima[aggregate_index] is None or gap < aggregate_minima[aggregate_index]:
            aggregate_minima[aggregate_index] = gap
            aggregate_witnesses[aggregate_index] = witness

    if minimum_gap is None or minimum_witness is None:
        raise RuntimeError("Q011z has no separated modulus comparison")
    expected_global_source = [
        "block=16;center=151",
        "block=16;center=151",
        "block=16;center=151",
        "block=0;center=149",
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
        "all_11280_product_modulus_intervals_are_reconstructed": bool(
            product_framer.count == EXPECTED_INDEXED_MONOMIAL_COUNT
            and len(internal_products) == EXPECTED_INDEXED_MONOMIAL_COUNT
            and radii_nonnegative
            and intervals_ordered
        ),
        "uniform_triangle_inequality_product_formula_is_applied": bool(
            radii_nonnegative and intervals_ordered
        ),
        "all_6956_compatible_comparisons_are_evaluated": (
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
            minimum_witness["aggregate_index"] == 2
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
            "radius": ("R=product_i(u_i+rho)-product_i(u_i), i=1..6"),
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
            "exact_product_record_digest_sha256": product_framer.hexdigest(),
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
        "unique_external_target_count": EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT,
        "aggregate_monomial_counts": list(EXPECTED_MONOMIAL_COUNTS),
        "indexed_monomial_count": EXPECTED_INDEXED_MONOMIAL_COUNT,
        "aggregate_compatible_comparison_counts": list(EXPECTED_COMPARISON_COUNTS),
        "compatible_comparison_count": EXPECTED_COMPATIBLE_COMPARISON_COUNT,
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


def run_degree6_refined_modulus_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = _inventory_audit(
        artifacts
    )
    envelope, lookup = _uniform_envelope_audit(
        artifacts,
        selected_groups,
        external_target_groups,
    )
    sector, monomial_records, compatible_pairs = _sector_audit(
        artifacts,
        selected_groups,
        external_target_groups,
        overlap_records,
    )
    product, minimum_gap = _product_audit(
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
    inventory_sections = {
        "degree6_modulus_inventory_audit": inventory,
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
        "four_artifacts_twenty_three_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y artifacts, runners, 23 digests, outcomes, claim "
                "boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_six_inventory_and_three_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "84 aggregates, 462 controls, 81 separated and three registered overlaps"
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
                "8/4/4/8 groups, 11280 monomials, registered sextic histograms "
                "and 2400+1836+2720 comparisons"
            ),
            "value": sector["checks"],
        },
        "all_product_target_intervals_and_strict_gaps_reproduce": {
            "passed": product["passed"],
            "threshold": ("11280 exact uniform product intervals and 6956 target comparisons"),
            "value": product["checks"],
        },
        "old_separations_and_three_full_audits_cover_all_84_aggregates": {
            "passed": bool(
                inventory["passed"]
                and sector["passed"]
                and product["passed"]
                and inventory["old_modulus_separated_aggregate_count"]
                + len(inventory["overlap_records"])
                == EXPECTED_DEGREE_AGGREGATE_COUNT
            ),
            "threshold": "81 old-separated plus three fully indexed overlap aggregates",
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
        "inventory_monomials_and_targets_cover_all_degree_six_cases": {
            "passed": bool(validity_passed and complete_coverage),
            "threshold": (
                "84 aggregates plus 11280 overlap monomials and 6956 compatible comparisons"
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
                "6956 individual modulus separations and zero unresolved interval overlaps"
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
        "degree_six_external_nonresonance_follows_from_complete_partition": {
            "passed": bool(
                validity_passed and complete_coverage and zero_unresolved and all_individual
            ),
            "threshold": ("81 preserved Q011u separations plus all three refined overlap audits"),
            "value": {
                "preserved_old_separations": inventory["old_modulus_separated_aggregate_count"],
                "resolved_overlap_aggregates": len(product["aggregate_category_counts"]),
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011z degree-six refined-modulus audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Does a contained uniform transformed-residual envelope give "
            "strict indexed-modulus separation for every Fourier-compatible "
            "comparison in all three degree-six overlap aggregates?"
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
    degree_six_certified = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "uniform_transformed_residual_envelope_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "all_three_degree_six_old_modulus_overlaps_are_eliminated": (degree_six_certified),
        "degree_six_external_nonresonance_is_certified": degree_six_certified,
        "certified_external_nonresonance_degrees": (
            [2, 3, 4, 5, 6] if degree_six_certified else [2, 3, 4, 5]
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(7 if degree_six_certified else 6, 91)),
        "degrees_7_through_90_are_certified": False,
        "complex_phase_was_required_for_degree_six": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_q011u_q011x_or_q011y_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree six for the fixed 17x17 repaired "
        "exact map on one fixed conservation leaf, the three Q011u "
        "modulus-overlap aggregates, the Q011y transformed-residual "
        "enclosure, the uniform rho=5e-8 discs, x-Fourier sectors and the "
        "registered indexed-modulus product formula. It certifies no degree "
        "from 7 through 90, no all-order nonresonance, equality with the "
        "Q011t graph, C2 or higher graph smoothness, SSM existence or "
        "uniqueness, normal attraction, basin, other grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_degree_five_acceptance_changed": False,
        "q011y_eigendisc_refinement_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011aa to audit the degree-seven modulus-overlap "
            "aggregates using the same contained uniform envelope."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Send only the first unresolved degree-six indexed product to an "
            "exact complex phase-sensitive product-disc comparison."
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
        raise RuntimeError("Q011z cycle failed strict serialization or digest")
    return cycle


def run_q011z_study() -> dict[str, Any]:
    cycle = run_degree6_refined_modulus_audit()
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
            "compatible_comparison_count": EXPECTED_COMPATIBLE_COMPARISON_COUNT,
            "exact_record_storage": "framed SHA-256 plus compact extrema and witnesses",
        },
        "mathematical_scope": {
            "diagnostic": ("degree-six uniform refined-envelope indexed-modulus products"),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_six_external_nonresonance_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "degrees_7_through_90_claim": False,
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
    result = run_q011z_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
