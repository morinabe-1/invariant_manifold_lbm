"""Q011ag degree-thirteen batched outward-dyadic certificate."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from itertools import product
from math import inf
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

import research.q011af_degree12_compressed_modulus as q011af
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

q011b = q011af.q011b
q011u = q011af.q011u
q011z = q011af.q011z

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
DEGREE = 13
EXPECTED_DEGREE_AGGREGATE_COUNT = 560
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 8568
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 516
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 44
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
OVERLAP_COUNTS = (
    (0, 3, 0, 10),
    (0, 3, 1, 9),
    (0, 3, 2, 8),
    (0, 5, 1, 7),
    (0, 5, 2, 6),
    (0, 5, 3, 5),
    (2, 6, 2, 3),
    (2, 6, 3, 2),
    (2, 6, 4, 1),
    (2, 6, 5, 0),
    (3, 5, 0, 5),
    (3, 5, 1, 4),
    (3, 5, 2, 3),
    (3, 5, 3, 2),
    (3, 5, 4, 1),
    (3, 5, 5, 0),
    (3, 8, 0, 2),
    (3, 8, 1, 1),
    (3, 8, 2, 0),
    (4, 4, 0, 5),
    (4, 4, 1, 4),
    (4, 4, 2, 3),
    (4, 4, 3, 2),
    (4, 4, 4, 1),
    (4, 4, 5, 0),
    (4, 7, 0, 2),
    (4, 7, 1, 1),
    (5, 3, 0, 5),
    (5, 3, 1, 4),
    (5, 3, 2, 3),
    (5, 3, 3, 2),
    (5, 3, 4, 1),
    (5, 3, 5, 0),
    (5, 8, 0, 0),
    (6, 2, 0, 5),
    (6, 2, 1, 4),
    (6, 7, 0, 0),
    (7, 6, 0, 0),
    (8, 5, 0, 0),
    (9, 0, 0, 4),
    (9, 0, 1, 3),
    (9, 0, 2, 2),
    (9, 0, 3, 1),
    (9, 0, 4, 0),
)
EXTERNAL_GROUP_INDICES = (
    167,
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
    162,
    162,
    162,
    162,
    159,
    159,
    159,
    162,
    162,
    162,
    162,
    162,
    162,
    159,
    159,
    162,
    162,
    162,
    162,
    162,
    162,
    156,
    162,
    162,
    156,
    156,
    156,
    161,
    161,
    161,
    161,
    161,
)
EXPECTED_EXTERNAL_TARGET_COUNTS = (
    8,
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
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 44
EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT = 68
EXPECTED_RELEVANT_IDENTIFIER_COUNT = 100
EXPECTED_UNIQUE_CENTER_MODULUS_EVALUATION_COUNT = 60
EXPECTED_MODULUS_CLASS_COUNTS = (4, 2, 3, 6)

EXPECTED_MONOMIAL_COUNTS = (
    388960,
    915200,
    1287000,
    768768,
    960960,
    887040,
    3628800,
    2177280,
    846720,
    169344,
    5322240,
    8870400,
    8064000,
    4838400,
    1881600,
    376320,
    712800,
    633600,
    198000,
    9147600,
    15246000,
    13860000,
    8316000,
    3234000,
    646800,
    1425600,
    1267200,
    12545280,
    20908800,
    19008000,
    11404800,
    4435200,
    887040,
    130680,
    13590720,
    22651200,
    205920,
    288288,
    360360,
    3775200,
    5491200,
    4118400,
    1830400,
    400400,
)
EXPECTED_SIGNATURE_COUNTS = (
    12012,
    24024,
    30888,
    14256,
    16632,
    15120,
    23520,
    14700,
    6300,
    1470,
    30240,
    45360,
    40320,
    25200,
    10800,
    2520,
    3780,
    3240,
    1080,
    44100,
    66150,
    58800,
    36750,
    15750,
    3675,
    5880,
    5040,
    56448,
    84672,
    75264,
    47040,
    20160,
    4704,
    504,
    63504,
    95256,
    672,
    840,
    990,
    27720,
    36960,
    27720,
    13200,
    3300,
)
EXPECTED_COMPATIBLE_SIGNATURE_COUNTS = (
    5868,
    11912,
    15260,
    7248,
    8496,
    7680,
    23520,
    14700,
    6300,
    1470,
    30240,
    45360,
    40320,
    25200,
    10800,
    2520,
    3780,
    3240,
    1080,
    44100,
    66150,
    58800,
    36750,
    15750,
    3675,
    5880,
    5040,
    56448,
    84672,
    75264,
    47040,
    20160,
    4704,
    504,
    63504,
    95256,
    672,
    840,
    990,
    13420,
    18480,
    13420,
    6600,
    1540,
)
EXPECTED_COMPATIBLE_MONOMIAL_COUNTS = (
    87768,
    210080,
    298256,
    118040,
    149188,
    137824,
    653800,
    393832,
    154704,
    31608,
    918560,
    1512160,
    1370240,
    826080,
    325280,
    66560,
    132800,
    116160,
    37360,
    1519420,
    2497800,
    2261700,
    1364550,
    538500,
    110330,
    268380,
    235560,
    2058720,
    3383312,
    3063040,
    1848336,
    729760,
    149552,
    34184,
    2263560,
    3721756,
    55112,
    78200,
    98540,
    1021720,
    1536960,
    1128120,
    510640,
    101800,
)
EXPECTED_WEIGHTED_COMPARISON_COUNTS = (
    256176,
    616800,
    879472,
    236080,
    298376,
    275648,
    1307600,
    787664,
    309408,
    63216,
    1837120,
    3024320,
    2740480,
    1652160,
    650560,
    133120,
    357120,
    323840,
    97600,
    3038840,
    4995600,
    4523400,
    2729100,
    1077000,
    220660,
    733880,
    668240,
    4117440,
    6766624,
    6126080,
    3696672,
    1459520,
    299104,
    68368,
    4527120,
    7443512,
    110224,
    156400,
    197080,
    2043440,
    3073920,
    2256240,
    1021280,
    203600,
)
EXPECTED_DISTINCT_COMPARISON_COUNTS = (
    46768,
    95136,
    121936,
    28992,
    33984,
    30720,
    144480,
    90440,
    39200,
    9520,
    189120,
    277920,
    247680,
    155040,
    67200,
    16320,
    20880,
    18720,
    5760,
    275800,
    405300,
    361200,
    226100,
    98000,
    23800,
    32480,
    29120,
    353024,
    518784,
    462336,
    289408,
    125440,
    30464,
    4032,
    397152,
    583632,
    5376,
    6720,
    7920,
    102960,
    144320,
    104720,
    51040,
    11440,
)
EXPECTED_INDEXED_MONOMIAL_COUNT = 218_102_520
EXPECTED_SIGNATURE_COUNT = 1_116_561
EXPECTED_COMPATIBLE_SIGNATURE_COUNT = 1_004_653
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 38_119_852
EXPECTED_WEIGHTED_COMPARISON_COUNT = 77_400_104
EXPECTED_DISTINCT_COMPARISON_COUNT = 6_290_384
EXPECTED_WEIGHTED_RELATIONS = {
    "product_below_target": 47_068_304,
    "target_below_product": 30_331_800,
}
EXPECTED_DISTINCT_RELATIONS = {
    "product_below_target": 3_874_124,
    "target_below_product": 2_416_260,
}
EXPECTED_GROUP_SIGNATURE_RECORD_COUNT = 8_818
EXPECTED_COEFFICIENT_MATRIX_COUNT = 162
EXPECTED_BOUND_MATRIX_COUNT = 44
EXPECTED_CLASSIFICATION_MATRIX_COUNT = 340
EXPECTED_MAXIMUM_WAVE_COEFFICIENT = 213
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 95_256
EXPECTED_EXACT_REFINEMENT_CANDIDATE_COUNT = 138
EXPECTED_EXACT_MINIMUM_TIE_COUNT = 2

UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
MINIMUM_CERTIFIED_GAP = Fraction(5, 10**6)
EXPECTED_CERTIFIED_MINIMUM_HEX = "0x1.84c3ca21dffffp-18"
EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX = "0x1.8e52905bdffffp-18"
EXPECTED_EXACT_MINIMUM_FLOAT_HEX = "0x1.84c3ca2956e59p-18"
EXPECTED_EXACT_MINIMUM_DIGEST = "fba273196d34e29b081b5518868cfb2e7a1dd40de02b469063a03e6bf8a676ba"

EXPECTED_INVENTORY_DIGEST = "12352e39ce74b79ea327b5dbb032499d21c306d5d71ba7cd5d0e1779623e140a"
EXPECTED_UNIFORM_RECORD_DIGEST = "c75c93e6cb23a93d212e2b2664f0dc3a63db6d7278d377b30e640bbabc21e993"
EXPECTED_CLASS_MEMBERSHIP_DIGEST = (
    "269187f8489521c7e37ae8a91669b9dc020ac10d4ef1d42272bb636fa7bc9b8c"
)
EXPECTED_OUTWARD_BASE_DIGEST = "f616c74320ae94e2b9aaffa82cfbc33713bed2c336332e6c96a2ab8822b178b0"
EXPECTED_FACTORIZATION_DIGEST = "5bdff6f6766c77b7c73ddb20eeb26b8a047f242ace033aeef5a1c6c2a5c265a3"
EXPECTED_WAVE_HISTOGRAM_DIGEST = "c6d21cf776ced791c85e245edec778fc29725824ca02ab678bf7044697554308"
EXPECTED_COEFFICIENT_MATRIX_DIGEST = (
    "a1c0d42f8343a2ab8aff0b1f4c3e206adadf2384be87cb2015ebf89e6e4ac77a"
)
EXPECTED_DYADIC_BOUND_DIGEST = "5be6e793081de098f6fceae5abcdda061ced1ebdb11fd065d42c419763100515"
EXPECTED_CLASSIFICATION_MATRIX_DIGEST = (
    "daaf7c7a3e7a3e7427ee043f1d100485eca3d78718c3cb823dc0eaedfea7cdda"
)
EXPECTED_COMPACT_PILOT_DIGEST = "5afe9e14301d1e62a133766d71881062d0a56d03587e11993c0dac328efe9802"

Q011AF_ARTIFACT_SHA256 = "19f2ea8f23e91532ab6acfddc346409800983b17b916b6be0c27699e4b036555"
Q011AF_RUNNER_SHA256 = "b270b0c4c884d1243e4db55b1dcad57af4c2e72d2143400de9c7c72d263f3293"
Q011AF_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "compression_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)
Q011AF_DIGESTS = (
    "14a3b80b475f418cf9963555a4cabcea19875a0f3028ef023961c67081708718",
    "39f1a63ca73b22969c150c84224ae94761edc53481d7822f8dc63a7abca7e493",
    "b8845507a83e6778f70c192a00ba85a747b28edc9a1235a202d4214e3e66e502",
    "16140d16ff621d4915f1571ae535031629bffb4f19d8392c18a4e2ad47e206ab",
    "da02c8613dc60079b977ec7d3dedd8545c486c6d401e5d84d77e3df7ff9c8204",
)

ACCEPTED_CLASSIFICATION = (
    "degree-13 external nonresonance is certified by exact Fourier "
    "multiplicities and outward-rounded dyadic product enclosures"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-13 outward-dyadic indexed-modulus product "
    "remains inseparable from an external target"
)


@dataclass(frozen=True)
class _GroupSignature:
    class_counts: tuple[int, ...]
    wave: npt.NDArray[np.int64]
    bounds: tuple[np.float64, np.float64, np.float64, np.float64]
    exact: tuple[Fraction, Fraction, Fraction]
    fiber_multiplicity: int


@dataclass(frozen=True)
class _PairSignature:
    class_counts: tuple[tuple[int, ...], tuple[int, ...]]
    wave: npt.NDArray[np.int64]
    bounds: tuple[np.float64, np.float64, np.float64, np.float64]
    fiber_multiplicity: int


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _artifact_directory() -> Path:
    return Path(__file__).resolve().parent / "artifacts"


def _array_sha256(array: npt.NDArray[Any]) -> str:
    return q011b._array_sha256(np.ascontiguousarray(array))


def _fraction_lower(value: Fraction) -> np.float64:
    candidate = np.float64(float(value))
    if Fraction.from_float(float(candidate)) > value:
        candidate = np.nextafter(candidate, -inf)
    return candidate


def _fraction_upper(value: Fraction) -> np.float64:
    candidate = np.float64(float(value))
    if Fraction.from_float(float(candidate)) < value:
        candidate = np.nextafter(candidate, inf)
    return candidate


def _down_multiply(left: Any, right: Any) -> Any:
    return np.nextafter(np.multiply(left, right), -inf)


def _up_multiply(left: Any, right: Any) -> Any:
    return np.nextafter(np.multiply(left, right), inf)


def _down_subtract(left: Any, right: Any) -> Any:
    return np.nextafter(np.subtract(left, right), -inf)


def _up_subtract(left: Any, right: Any) -> Any:
    return np.nextafter(np.subtract(left, right), inf)


def _up_add(left: Any, right: Any) -> Any:
    return np.nextafter(np.add(left, right), inf)


def _float_record(value: float) -> dict[str, Any]:
    return {"float": float(value), "binary64_hex": float(value).hex()}


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    prior, artifacts = q011af._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011af_degree12_compressed_modulus.json"
    runner_path = Path(q011af.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AF_DIGEST_NAMES)
    checks = {
        "q011af_ten_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"] and prior["direct_digest_count"] == 53 and all(prior["checks"].values())
        ),
        "q011af_artifact_sha256_matches": _file_sha256(artifact_path) == Q011AF_ARTIFACT_SHA256,
        "q011af_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AF_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AF_RUNNER_SHA256
        ),
        "q011af_digests_match": digests == Q011AF_DIGESTS,
        "q011af_registered_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["scientific_classification"] == q011af.ACCEPTED_CLASSIFICATION
        ),
        "q011af_degree_twelve_scope_is_preserved": bool(
            cycle["theorem_consequence"]["degree_twelve_external_nonresonance_is_certified"]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == list(range(2, 13))
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(13, 91))
            and not cycle["theorem_consequence"]["ssm_existence_or_uniqueness_is_certified"]
        ),
        "q011af_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011af_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011af_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "fifty_eight_direct_digests_are_sealed": prior["direct_digest_count"] + len(digests) == 58,
    }
    artifacts["q011af"] = artifact
    audit = {
        "prior_q011af_sealed_input_audit": prior,
        "q011af": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AF_DIGEST_NAMES),
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
    external_target_groups = tuple(
        tuple(sorted(external_merged[index].identifiers)) for index in EXTERNAL_GROUP_INDICES
    )
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
                zip(EXTERNAL_GROUP_INDICES, external_target_groups, strict=True)
            )
        ],
    }
    exact_digest = q011b._canonical_json_sha256(exact_inventory)
    first_overlap = degree_record["first_overlap"]
    checks = {
        "q011u_old_modulus_spectrum_reconstructs_exactly": bool(
            reconstructed["passed"] and reconstructed == stored_spectrum
        ),
        "q011u_degree_thirteen_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_forty_four_overlap_tuples_and_external_groups_reproduce": bool(
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
            and all(
                q011b._canonical_json_sha256(list(group))
                == stored_selected[index]["membership_digest_sha256"]
                for index, group in enumerate(selected_groups)
            )
        ),
        "external_target_memberships_and_sizes_reproduce": bool(
            tuple(len(group) for group in external_target_groups) == EXPECTED_EXTERNAL_TARGET_COUNTS
            and len(set().union(*map(set, external_target_groups)))
            == EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT
            and all(
                q011b._canonical_json_sha256(list(group))
                == stored_external[external_index]["membership_digest_sha256"]
                for group, external_index in zip(
                    external_target_groups, EXTERNAL_GROUP_INDICES, strict=True
                )
            )
        ),
        "old_degree_twelve_certificate_is_preserved": artifacts["q011af"]["cycle"][
            "theorem_consequence"
        ]["degree_twelve_external_nonresonance_is_certified"],
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
        "external_target_groups": [
            {
                "aggregate_index": index,
                "external_group_index": EXTERNAL_GROUP_INDICES[index],
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
    directly_relevant = selected_identifiers | external_identifiers
    prior_records = {
        record["identifier"]: record
        for record in artifacts["q011af"]["cycle"]["uniform_refined_envelope_audit"][
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
    expected_new_identifiers = set().union(
        *(
            set(group)
            for group, external_index in zip(
                external_target_groups, EXTERNAL_GROUP_INDICES, strict=True
            )
            if external_index == 156
        )
    )
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
        "all_68_direct_and_100_monotone_identifiers_have_uniform_intervals": bool(
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
        "all_q011af_92_uniform_records_are_preserved_exactly": bool(
            len(prior_records) == 92
            and set(prior_records).issubset(current_records)
            and all(
                current_records[identifier] == record
                for identifier, record in prior_records.items()
            )
        ),
        "only_eight_group_156_records_are_added": bool(
            len(new_identifiers) == 8 and new_identifiers == expected_new_identifiers
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
        "new_group_156_identifiers": sorted(new_identifiers),
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


def _modulus_classes(
    selected_groups: tuple[tuple[str, ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> tuple[tuple[tuple[tuple[str, ...], ...], ...], list[dict[str, Any]]]:
    return q011af._modulus_classes(selected_groups, lookup)


def _group_signature(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    group_index: int,
    source_count: int,
) -> tuple[_GroupSignature, ...]:
    result = []
    for class_counts, wave_counter in q011af._group_signature_records(
        classes, group_index, source_count
    ):
        center_lower_exact = Fraction(1)
        center_upper_exact = Fraction(1)
        full_upper_exact = Fraction(1)
        bounds = [np.float64(1.0)] * 4
        for count, identifiers in zip(class_counts, classes[group_index], strict=True):
            disc = lookup[identifiers[0]]
            factors = (
                _fraction_lower(disc.center_modulus.lower),
                _fraction_lower(disc.center_modulus.upper),
                _fraction_upper(disc.center_modulus.upper),
                _fraction_upper(disc.center_modulus.upper + UNIFORM_REFINED_RADIUS),
            )
            for _ in range(count):
                bounds[0] = _down_multiply(bounds[0], factors[0])
                bounds[1] = _down_multiply(bounds[1], factors[1])
                bounds[2] = _up_multiply(bounds[2], factors[2])
                bounds[3] = _up_multiply(bounds[3], factors[3])
            center_lower_exact *= disc.center_modulus.lower**count
            center_upper_exact *= disc.center_modulus.upper**count
            full_upper_exact *= (disc.center_modulus.upper + UNIFORM_REFINED_RADIUS) ** count
        exact = (center_lower_exact, center_upper_exact, full_upper_exact)
        if not (
            Fraction.from_float(float(bounds[0])) <= exact[0]
            and Fraction.from_float(float(bounds[1])) <= exact[1]
            and Fraction.from_float(float(bounds[2])) >= exact[1]
            and Fraction.from_float(float(bounds[3])) >= exact[2]
        ):
            raise RuntimeError("Q011ag group outward interval lost containment")
        wave = np.array([wave_counter[index] for index in range(SIZE)], dtype=np.int64)
        result.append(
            _GroupSignature(
                class_counts=class_counts,
                wave=wave,
                bounds=(bounds[0], bounds[1], bounds[2], bounds[3]),
                exact=exact,
                fiber_multiplicity=sum(wave_counter.values()),
            )
        )
    return tuple(result)


def _pair_signatures(
    left: tuple[_GroupSignature, ...],
    right: tuple[_GroupSignature, ...],
) -> tuple[_PairSignature, ...]:
    records = []
    for left_record, right_record in product(left, right):
        left_counter = Counter(
            {index: int(value) for index, value in enumerate(left_record.wave) if value}
        )
        right_counter = Counter(
            {index: int(value) for index, value in enumerate(right_record.wave) if value}
        )
        wave_counter = q011af._cyclic_convolution(left_counter, right_counter)
        wave = np.array([wave_counter[index] for index in range(SIZE)], dtype=np.int64)
        bounds = (
            _down_multiply(left_record.bounds[0], right_record.bounds[0]),
            _down_multiply(left_record.bounds[1], right_record.bounds[1]),
            _up_multiply(left_record.bounds[2], right_record.bounds[2]),
            _up_multiply(left_record.bounds[3], right_record.bounds[3]),
        )
        exact = (
            left_record.exact[0] * right_record.exact[0],
            left_record.exact[1] * right_record.exact[1],
            left_record.exact[2] * right_record.exact[2],
        )
        if not (
            Fraction.from_float(float(bounds[0])) <= exact[0]
            and Fraction.from_float(float(bounds[1])) <= exact[1]
            and Fraction.from_float(float(bounds[2])) >= exact[1]
            and Fraction.from_float(float(bounds[3])) >= exact[2]
            and int(wave.sum()) == left_record.fiber_multiplicity * right_record.fiber_multiplicity
        ):
            raise RuntimeError("Q011ag pair factorization lost exactness")
        records.append(
            _PairSignature(
                class_counts=(
                    left_record.class_counts,
                    right_record.class_counts,
                ),
                wave=wave,
                bounds=bounds,
                fiber_multiplicity=int(wave.sum()),
            )
        )
    return tuple(records)


def _target_groups_by_block(
    target_group: tuple[str, ...],
) -> dict[int, list[str]]:
    result: dict[int, list[str]] = {}
    for identifier in target_group:
        block = q011z._identifier_indices(identifier)[0]
        result.setdefault(block, []).append(identifier)
    return result


def _product_bound_matrices(
    left: tuple[_PairSignature, ...],
    right: tuple[_PairSignature, ...],
) -> tuple[npt.NDArray[np.float64], npt.NDArray[np.float64]]:
    lower_center = np.nextafter(
        np.multiply.outer(
            np.array([record.bounds[0] for record in left]),
            np.array([record.bounds[0] for record in right]),
        ),
        -inf,
    )
    upper_center_lower = np.nextafter(
        np.multiply.outer(
            np.array([record.bounds[1] for record in left]),
            np.array([record.bounds[1] for record in right]),
        ),
        -inf,
    )
    upper_center_upper = np.nextafter(
        np.multiply.outer(
            np.array([record.bounds[2] for record in left]),
            np.array([record.bounds[2] for record in right]),
        ),
        inf,
    )
    full_upper = np.nextafter(
        np.multiply.outer(
            np.array([record.bounds[3] for record in left]),
            np.array([record.bounds[3] for record in right]),
        ),
        inf,
    )
    radius_upper = _up_subtract(full_upper, upper_center_lower)
    product_lower = np.maximum(0.0, _down_subtract(lower_center, radius_upper))
    product_upper = _up_add(upper_center_upper, radius_upper)
    return product_lower, product_upper


def _wave_matrix(
    left_wave: npt.NDArray[np.int64],
    right_wave: npt.NDArray[np.int64],
    output_block: int,
) -> tuple[npt.NDArray[np.int64], int]:
    crude_bound = SIZE * int(left_wave.max(initial=0)) * int(right_wave.max(initial=0))
    if crude_bound > np.iinfo(np.int64).max:
        raise OverflowError("Q011ag int64 Fourier dot-product bound failed")
    indices = np.array([(output_block - index) % SIZE for index in range(SIZE)])
    return left_wave @ right_wave[:, indices].T, crude_bound


def _exact_product_interval(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    class_counts: tuple[tuple[int, ...], ...],
) -> RationalInterval:
    center_lower = Fraction(1)
    center_upper = Fraction(1)
    full_upper = Fraction(1)
    for group_index, group_counts in enumerate(class_counts):
        for count, identifiers in zip(group_counts, classes[group_index], strict=True):
            disc = lookup[identifiers[0]]
            center_lower *= disc.center_modulus.lower**count
            center_upper *= disc.center_modulus.upper**count
            full_upper *= (disc.center_modulus.upper + UNIFORM_REFINED_RADIUS) ** count
    radius = full_upper - center_upper
    return RationalInterval(max(Fraction(0), center_lower - radius), full_upper)


def _signature_counts(
    left: tuple[_PairSignature, ...],
    right: tuple[_PairSignature, ...],
    left_index: int,
    right_index: int,
) -> tuple[tuple[int, ...], ...]:
    return (*left[left_index].class_counts, *right[right_index].class_counts)


def _batched_audit(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
    overlap_counts: tuple[tuple[int, ...], ...],
    external_target_groups: tuple[tuple[str, ...], ...],
    *,
    collect_registered_digests: bool,
    exact_refinement: bool,
) -> dict[str, Any]:
    group_cache: dict[tuple[int, int], tuple[_GroupSignature, ...]] = {}

    def group_pool(group_index: int, count: int) -> tuple[_GroupSignature, ...]:
        key = (group_index, count)
        if key not in group_cache:
            group_cache[key] = _group_signature(classes, lookup, group_index, count)
        return group_cache[key]

    coefficient_digest_records = []
    bound_digest_records = []
    classification_digest_records = []
    factorization_aggregates = []
    wave_histograms = []
    compact_summaries = []
    aggregate_records = []
    weighted_relations: Counter[str] = Counter()
    distinct_relations: Counter[str] = Counter()
    global_minimum = inf
    global_raw: dict[str, Any] | None = None
    maximum_wave_coefficient = 0
    maximum_crude_int64_bound = 0
    maximum_live_signature_count = 0
    all_arrays_finite = True
    all_bounds_ordered = True

    for aggregate_index, (counts, target_group) in enumerate(
        zip(overlap_counts, external_target_groups, strict=True)
    ):
        group_pools = tuple(
            group_pool(group_index, count) for group_index, count in enumerate(counts)
        )
        left = _pair_signatures(group_pools[0], group_pools[1])
        right = _pair_signatures(group_pools[2], group_pools[3])
        left_wave = np.stack([record.wave for record in left])
        right_wave = np.stack([record.wave for record in right])
        product_lower, product_upper = _product_bound_matrices(left, right)
        signature_count = len(left) * len(right)
        maximum_live_signature_count = max(maximum_live_signature_count, signature_count)
        all_arrays_finite = bool(
            all_arrays_finite
            and np.isfinite(product_lower).all()
            and np.isfinite(product_upper).all()
        )
        all_bounds_ordered = bool(
            all_bounds_ordered
            and np.all(product_lower >= 0)
            and np.all(product_lower <= product_upper)
        )
        if collect_registered_digests:
            bound_digest_records.append(
                {
                    "aggregate_index": aggregate_index,
                    "selected_type_counts": list(counts),
                    "shape": list(product_lower.shape),
                    "lower_sha256": _array_sha256(product_lower.astype(">f8")),
                    "upper_sha256": _array_sha256(product_upper.astype(">f8")),
                }
            )
            factorization_aggregates.append(
                {
                    "aggregate_index": aggregate_index,
                    "selected_type_counts": list(counts),
                    "left_pool_shape": [len(group_pools[0]), len(group_pools[1])],
                    "right_pool_shape": [len(group_pools[2]), len(group_pools[3])],
                    "combined_signature_count": signature_count,
                }
            )
        left_sum = left_wave.sum(axis=0)
        right_sum = right_wave.sum(axis=0)
        histogram = [
            int(
                sum(
                    int(left_sum[index]) * int(right_sum[(block - index) % SIZE])
                    for index in range(SIZE)
                )
            )
            for block in range(SIZE)
        ]
        wave_histograms.append(histogram)
        compatible = np.zeros(product_lower.shape, dtype=bool)
        compatible_monomial_count = 0
        weighted_comparison_count = 0
        distinct_comparison_count = 0
        aggregate_weighted: Counter[str] = Counter()
        aggregate_distinct: Counter[str] = Counter()
        aggregate_minimum = inf
        aggregate_raw: dict[str, Any] | None = None
        target_by_block = _target_groups_by_block(target_group)
        for output_block, target_identifiers in target_by_block.items():
            wave_matrix, crude_bound = _wave_matrix(left_wave, right_wave, output_block)
            maximum_crude_int64_bound = max(maximum_crude_int64_bound, crude_bound)
            maximum_wave_coefficient = max(
                maximum_wave_coefficient, int(wave_matrix.max(initial=0))
            )
            active = wave_matrix > 0
            compatible |= active
            compatible_monomial_count += int(wave_matrix.sum())
            weighted_comparison_count += int(wave_matrix.sum()) * len(target_identifiers)
            distinct_comparison_count += int(active.sum()) * len(target_identifiers)
            if collect_registered_digests:
                coefficient_digest_records.append(
                    {
                        "aggregate_index": aggregate_index,
                        "output_block": output_block,
                        "shape": list(wave_matrix.shape),
                        "coefficient_sha256": _array_sha256(wave_matrix.astype(">i8")),
                    }
                )
            for target_identifier in target_identifiers:
                target = lookup[target_identifier]
                product_below_gap = _down_subtract(
                    _fraction_lower(target.modulus.lower), product_upper
                )
                target_below_gap = _down_subtract(
                    product_lower, _fraction_upper(target.modulus.upper)
                )
                product_below = active & (product_below_gap > 0)
                target_below = active & (target_below_gap > 0)
                unresolved = active & ~(product_below | target_below)
                codes = np.zeros(wave_matrix.shape, dtype=np.uint8)
                codes[product_below] = 1
                codes[target_below] = 2
                codes[unresolved] = 3
                if collect_registered_digests:
                    classification_digest_records.append(
                        {
                            "aggregate_index": aggregate_index,
                            "output_block": output_block,
                            "target_identifier": target_identifier,
                            "shape": list(codes.shape),
                            "classification_sha256": _array_sha256(codes),
                        }
                    )
                for relation, mask in (
                    ("product_below_target", product_below),
                    ("target_below_product", target_below),
                    ("overlap", unresolved),
                ):
                    weighted = int(wave_matrix[mask].sum())
                    distinct = int(mask.sum())
                    weighted_relations[relation] += weighted
                    distinct_relations[relation] += distinct
                    aggregate_weighted[relation] += weighted
                    aggregate_distinct[relation] += distinct
                for relation, gaps, mask in (
                    ("product_below_target", product_below_gap, product_below),
                    ("target_below_product", target_below_gap, target_below),
                ):
                    if not mask.any():
                        continue
                    candidates = np.where(mask, gaps, inf)
                    flat_index = int(candidates.argmin())
                    gap = float(candidates.flat[flat_index])
                    if gap < aggregate_minimum:
                        left_index, right_index = np.unravel_index(flat_index, candidates.shape)
                        aggregate_minimum = gap
                        aggregate_raw = {
                            "aggregate_index": aggregate_index,
                            "selected_type_counts": list(counts),
                            "source_modulus_class_counts": _signature_counts(
                                left, right, left_index, right_index
                            ),
                            "output_block": output_block,
                            "wave_multiplicity": int(wave_matrix[left_index, right_index]),
                            "target_identifier": target_identifier,
                            "individual_modulus_relation": relation,
                            "certified_gap_lower": gap,
                        }
        if aggregate_raw is None:
            raise RuntimeError("Q011ag aggregate has no separated comparison")
        if aggregate_minimum < global_minimum:
            global_minimum = aggregate_minimum
            global_raw = aggregate_raw
        monomial_count = sum(record.fiber_multiplicity for record in left) * sum(
            record.fiber_multiplicity for record in right
        )
        record = {
            "aggregate_index": aggregate_index,
            "selected_type_counts": list(counts),
            "original_monomial_count": monomial_count,
            "modulus_signature_count": signature_count,
            "compatible_modulus_signature_count": int(compatible.sum()),
            "compatible_original_monomial_count": compatible_monomial_count,
            "weighted_comparison_count": weighted_comparison_count,
            "distinct_comparison_count": distinct_comparison_count,
            "weighted_relation_counts": {
                "product_below_target": aggregate_weighted["product_below_target"],
                "target_below_product": aggregate_weighted["target_below_product"],
                "overlap": aggregate_weighted["overlap"],
            },
            "distinct_relation_counts": {
                "product_below_target": aggregate_distinct["product_below_target"],
                "target_below_product": aggregate_distinct["target_below_product"],
                "overlap": aggregate_distinct["overlap"],
            },
            "minimum_certified_gap_lower": _float_record(aggregate_minimum),
            "minimum_witness": {
                **aggregate_raw,
                "source_modulus_class_counts": [
                    list(group_counts)
                    for group_counts in aggregate_raw["source_modulus_class_counts"]
                ],
                "certified_gap_lower": _float_record(aggregate_raw["certified_gap_lower"]),
            },
        }
        aggregate_records.append(record)
        compact_summaries.append(
            {
                "aggregate_index": aggregate_index,
                "compatible_signature_count": int(compatible.sum()),
            }
        )
    if global_raw is None:
        raise RuntimeError("Q011ag found no separated comparison")
    factor_records = []
    for (group_index, source_count), records in sorted(group_cache.items()):
        for record_index, record in enumerate(records):
            factor_records.append(
                {
                    "selected_group_index": group_index,
                    "source_count": source_count,
                    "group_signature_index": record_index,
                    "class_counts": list(record.class_counts),
                    "wave_coefficients": [int(value) for value in record.wave],
                }
            )
    factor_payload = {
        "group_signature_records": factor_records,
        "aggregate_factorizations": factorization_aggregates,
    }
    factor_digest = q011b._canonical_json_sha256(factor_payload)
    wave_histogram_digest = q011b._canonical_json_sha256(wave_histograms)
    coefficient_digest = q011b._canonical_json_sha256(coefficient_digest_records)
    bound_digest = q011b._canonical_json_sha256(bound_digest_records)
    classification_digest = q011b._canonical_json_sha256(classification_digest_records)
    compact_digest = q011b._canonical_json_sha256(
        {
            "histograms": wave_histograms,
            "summaries": compact_summaries,
            "factor_digest": factor_digest,
            "coefficient_digest": coefficient_digest,
            "bound_digest": bound_digest,
            "classification_digest": classification_digest,
        }
    )

    exact_audit: dict[str, Any] | None = None
    if exact_refinement:
        raw_counts = tuple(tuple(group) for group in global_raw["source_modulus_class_counts"])
        initial_product = _exact_product_interval(classes, lookup, raw_counts)
        initial_target = lookup[global_raw["target_identifier"]]
        if global_raw["individual_modulus_relation"] == "product_below_target":
            initial_exact_gap = initial_target.modulus.lower - initial_product.upper
        else:
            initial_exact_gap = initial_product.lower - initial_target.modulus.upper
        cutoff = _fraction_upper(initial_exact_gap)
        candidate_records = []
        exact_product_cache: dict[tuple[tuple[int, ...], ...], RationalInterval] = {}
        for aggregate_index, (counts, target_group) in enumerate(
            zip(overlap_counts, external_target_groups, strict=True)
        ):
            aggregate_lower = aggregate_records[aggregate_index]["minimum_certified_gap_lower"][
                "float"
            ]
            if aggregate_lower > cutoff:
                continue
            group_pools = tuple(
                group_pool(group_index, count) for group_index, count in enumerate(counts)
            )
            left = _pair_signatures(group_pools[0], group_pools[1])
            right = _pair_signatures(group_pools[2], group_pools[3])
            left_wave = np.stack([record.wave for record in left])
            right_wave = np.stack([record.wave for record in right])
            product_lower, product_upper = _product_bound_matrices(left, right)
            for output_block, target_identifiers in _target_groups_by_block(target_group).items():
                wave_matrix, _ = _wave_matrix(left_wave, right_wave, output_block)
                active = wave_matrix > 0
                for target_identifier in target_identifiers:
                    target = lookup[target_identifier]
                    product_below_gap = _down_subtract(
                        _fraction_lower(target.modulus.lower), product_upper
                    )
                    target_below_gap = _down_subtract(
                        product_lower, _fraction_upper(target.modulus.upper)
                    )
                    for relation, gaps, mask in (
                        (
                            "product_below_target",
                            product_below_gap,
                            active & (product_below_gap > 0),
                        ),
                        (
                            "target_below_product",
                            target_below_gap,
                            active & (target_below_gap > 0),
                        ),
                    ):
                        candidate_mask = mask & (gaps <= cutoff)
                        for left_index, right_index in zip(
                            *np.nonzero(candidate_mask), strict=True
                        ):
                            class_counts = _signature_counts(left, right, left_index, right_index)
                            if class_counts not in exact_product_cache:
                                exact_product_cache[class_counts] = _exact_product_interval(
                                    classes, lookup, class_counts
                                )
                            exact_product = exact_product_cache[class_counts]
                            if relation == "product_below_target":
                                exact_gap = target.modulus.lower - exact_product.upper
                            else:
                                exact_gap = exact_product.lower - target.modulus.upper
                            candidate_records.append(
                                {
                                    "aggregate_index": aggregate_index,
                                    "source_modulus_class_counts": [
                                        list(group) for group in class_counts
                                    ],
                                    "output_block": output_block,
                                    "wave_multiplicity": int(wave_matrix[left_index, right_index]),
                                    "target_identifier": target_identifier,
                                    "individual_modulus_relation": relation,
                                    "certified_gap_lower_hex": float(
                                        gaps[left_index, right_index]
                                    ).hex(),
                                    "exact_gap": q011z._exact_fraction_record(exact_gap),
                                }
                            )
        exact_minimum = min(q011z._fraction(record["exact_gap"]) for record in candidate_records)
        ties = [
            record
            for record in candidate_records
            if q011z._fraction(record["exact_gap"]) == exact_minimum
        ]
        canonical = ties[0]
        canonical_counts = tuple(tuple(group) for group in canonical["source_modulus_class_counts"])
        source = q011af._source_witness_for_signature(
            classes, canonical_counts, canonical["output_block"]
        )
        exact_records_digest = q011b._canonical_json_sha256(candidate_records)
        exact_minimum_record = q011z._exact_fraction_record(exact_minimum)
        exact_audit = {
            "cutoff_from_initial_exact_witness": q011z._exact_fraction_record(initial_exact_gap),
            "candidate_comparison_count": len(candidate_records),
            "candidate_exact_record_digest_sha256": exact_records_digest,
            "exact_global_minimum_gap": exact_minimum_record,
            "exact_global_minimum_gap_digest_sha256": q011b._canonical_json_sha256(
                exact_minimum_record
            ),
            "exact_global_minimum_tie_count": len(ties),
            "tie_target_identifiers": [record["target_identifier"] for record in ties],
            "canonical_minimum_witness": {
                **canonical,
                "source_identifiers": list(source),
            },
            "all_other_aggregate_lower_bounds_exceed_the_exact_cutoff": all(
                index == canonical["aggregate_index"]
                or record["minimum_certified_gap_lower"]["float"] > cutoff
                for index, record in enumerate(aggregate_records)
            ),
        }

    monomial_counts = tuple(record["original_monomial_count"] for record in aggregate_records)
    signature_counts = tuple(record["modulus_signature_count"] for record in aggregate_records)
    compatible_signature_counts = tuple(
        record["compatible_modulus_signature_count"] for record in aggregate_records
    )
    compatible_monomial_counts = tuple(
        record["compatible_original_monomial_count"] for record in aggregate_records
    )
    weighted_comparison_counts = tuple(
        record["weighted_comparison_count"] for record in aggregate_records
    )
    distinct_comparison_counts = tuple(
        record["distinct_comparison_count"] for record in aggregate_records
    )
    return {
        "aggregate_records": aggregate_records,
        "aggregate_original_monomial_counts": list(monomial_counts),
        "aggregate_modulus_signature_counts": list(signature_counts),
        "aggregate_compatible_modulus_signature_counts": list(compatible_signature_counts),
        "aggregate_compatible_original_monomial_counts": list(compatible_monomial_counts),
        "aggregate_weighted_comparison_counts": list(weighted_comparison_counts),
        "aggregate_distinct_comparison_counts": list(distinct_comparison_counts),
        "original_monomial_count": sum(monomial_counts),
        "modulus_signature_count": sum(signature_counts),
        "compatible_modulus_signature_count": sum(compatible_signature_counts),
        "compatible_original_monomial_count": sum(compatible_monomial_counts),
        "incompatible_original_monomial_count": sum(monomial_counts)
        - sum(compatible_monomial_counts),
        "weighted_comparison_count": sum(weighted_comparison_counts),
        "distinct_comparison_count": sum(distinct_comparison_counts),
        "weighted_relation_counts": {
            "product_below_target": weighted_relations["product_below_target"],
            "target_below_product": weighted_relations["target_below_product"],
            "overlap": weighted_relations["overlap"],
        },
        "distinct_relation_counts": {
            "product_below_target": distinct_relations["product_below_target"],
            "target_below_product": distinct_relations["target_below_product"],
            "overlap": distinct_relations["overlap"],
        },
        "minimum_certified_gap_lower": _float_record(global_minimum),
        "minimum_certified_gap_witness": {
            **global_raw,
            "source_modulus_class_counts": [
                list(group) for group in global_raw["source_modulus_class_counts"]
            ],
            "certified_gap_lower": _float_record(global_raw["certified_gap_lower"]),
        },
        "exact_refinement_audit": exact_audit,
        "group_signature_record_count": len(factor_records),
        "coefficient_matrix_record_count": len(coefficient_digest_records),
        "dyadic_bound_matrix_record_count": len(bound_digest_records),
        "classification_matrix_record_count": len(classification_digest_records),
        "maximum_wave_coefficient": maximum_wave_coefficient,
        "maximum_crude_int64_dot_product_bound": maximum_crude_int64_bound,
        "maximum_live_signature_count": maximum_live_signature_count,
        "all_group_and_pair_bounds_contain_exact_fraction_products": True,
        "all_product_bound_arrays_are_finite": all_arrays_finite,
        "all_product_bound_arrays_are_nonnegative_and_ordered": all_bounds_ordered,
        "integer_matrix_arithmetic_is_exact_without_overflow": bool(
            maximum_crude_int64_bound <= np.iinfo(np.int64).max
            and maximum_wave_coefficient <= np.iinfo(np.int64).max
        ),
        "class_membership_digest_sha256": None,
        "outward_base_digest_sha256": None,
        "factorization_digest_sha256": factor_digest,
        "aggregate_wave_histogram_digest_sha256": wave_histogram_digest,
        "coefficient_matrix_digest_sha256": coefficient_digest,
        "dyadic_bound_digest_sha256": bound_digest,
        "classification_matrix_digest_sha256": classification_digest,
        "compact_pilot_digest_sha256": compact_digest,
        "streaming_contract": {
            "algorithm": (
                "pair-factorized exact int64 cyclic Fourier matrices plus "
                "per-aggregate outward-rounded binary64 product bounds"
            ),
            "full_original_monomial_list_retained": False,
            "full_combined_signature_list_retained": False,
            "full_comparison_list_retained": False,
            "peak_live_combined_signature_count": maximum_live_signature_count,
            "retained_exact_refinement_candidate_count": (
                0 if exact_audit is None else exact_audit["candidate_comparison_count"]
            ),
        },
    }


def _outward_base_records(
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> list[dict[str, Any]]:
    records = []
    for group_index, group_classes in enumerate(classes):
        for class_index, identifiers in enumerate(group_classes):
            disc = lookup[identifiers[0]]
            records.append(
                {
                    "selected_group_index": group_index,
                    "modulus_class_index": class_index,
                    "identifier": identifiers[0],
                    "center_lower_outward_hex": float(
                        _fraction_lower(disc.center_modulus.lower)
                    ).hex(),
                    "center_upper_lower_outward_hex": float(
                        _fraction_lower(disc.center_modulus.upper)
                    ).hex(),
                    "center_upper_upper_outward_hex": float(
                        _fraction_upper(disc.center_modulus.upper)
                    ).hex(),
                    "full_factor_upper_outward_hex": float(
                        _fraction_upper(disc.center_modulus.upper + UNIFORM_REFINED_RADIUS)
                    ).hex(),
                }
            )
    return records


def _q011af_oracle_audit(
    artifacts: dict[str, dict[str, Any]],
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> dict[str, Any]:
    cycle = artifacts["q011af"]["cycle"]
    inventory = cycle["degree12_modulus_inventory_audit"]
    overlap_counts = tuple(
        tuple(record["selected_type_counts"]) for record in inventory["overlap_records"]
    )
    target_groups = tuple(
        tuple(record["identifiers"]) for record in inventory["external_target_groups"]
    )
    audit = _batched_audit(
        classes,
        lookup,
        overlap_counts,
        target_groups,
        collect_registered_digests=False,
        exact_refinement=False,
    )
    product = cycle["compressed_indexed_modulus_product_audit"]
    compression = cycle["multiplicity_compression_audit"]
    checks = {
        "all_registered_q011af_counts_reproduce": bool(
            audit["original_monomial_count"] == compression["original_monomial_count"] == 36_596_091
            and audit["modulus_signature_count"]
            == compression["modulus_signature_count"]
            == 213_618
            and audit["compatible_modulus_signature_count"]
            == compression["compatible_modulus_signature_count"]
            == 184_154
            and audit["compatible_original_monomial_count"]
            == compression["compatible_original_monomial_count"]
            == 6_904_665
            and audit["weighted_comparison_count"]
            == product["weighted_comparison_count"]
            == 13_980_960
            and audit["distinct_comparison_count"]
            == product["distinct_comparison_record_count"]
            == 1_116_256
        ),
        "weighted_and_distinct_relations_reproduce": bool(
            {
                key: value
                for key, value in audit["weighted_relation_counts"].items()
                if key != "overlap"
            }
            == product["weighted_individual_modulus_relation_counts"]
            and {
                key: value
                for key, value in audit["distinct_relation_counts"].items()
                if key != "overlap"
            }
            == product["distinct_individual_modulus_relation_counts"]
        ),
        "outward_oracle_has_no_unresolved_comparison": bool(
            audit["weighted_relation_counts"]["overlap"] == 0
            and audit["distinct_relation_counts"]["overlap"] == 0
        ),
        "registered_outward_oracle_minimum_and_witness_reproduce": bool(
            audit["minimum_certified_gap_lower"]["binary64_hex"]
            == EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX
            and audit["minimum_certified_gap_witness"]["aggregate_index"] == 3
            and audit["minimum_certified_gap_witness"]["selected_type_counts"] == [0, 6, 2, 4]
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
        "degree": 12,
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
        "degree_expanded_product_control_count": (EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT),
        "overlap_counts": [list(counts) for counts in OVERLAP_COUNTS],
        "external_group_indices": list(EXTERNAL_GROUP_INDICES),
        "uniform_radius": _fraction_record(UNIFORM_REFINED_RADIUS),
        "minimum_certified_gap": _fraction_record(MINIMUM_CERTIFIED_GAP),
        "outward_rounding": (
            "exact Fraction endpoints converted outward; every positive "
            "multiply, subtract and add is followed by nextafter toward "
            "the required infinity"
        ),
        "accepted_classification": ACCEPTED_CLASSIFICATION,
        "rejected_classification": REJECTED_CLASSIFICATION,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "failed_hypothesis_order": cycle["failed_hypothesis_order"],
    }


def run_degree13_batched_dyadic_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = _inventory_audit(
        artifacts
    )
    envelope, lookup = _uniform_envelope_audit(artifacts, selected_groups, external_target_groups)
    classes, class_records = _modulus_classes(selected_groups, lookup)
    class_digest = q011b._canonical_json_sha256(class_records)
    outward_bases = _outward_base_records(classes, lookup)
    outward_base_digest = q011b._canonical_json_sha256(outward_bases)
    oracle = _q011af_oracle_audit(artifacts, classes, lookup)
    batched = _batched_audit(
        classes,
        lookup,
        tuple(tuple(record["selected_type_counts"]) for record in overlap_records),
        external_target_groups,
        collect_registered_digests=True,
        exact_refinement=True,
    )
    batched["class_membership_digest_sha256"] = class_digest
    batched["outward_base_digest_sha256"] = outward_base_digest
    exact = batched["exact_refinement_audit"]
    if exact is None:
        raise RuntimeError("Q011ag exact refinement was not run")

    compression_checks = {
        "selected_groups_partition_into_registered_modulus_classes": bool(
            tuple(len(group) for group in classes) == EXPECTED_MODULUS_CLASS_COUNTS
            and class_digest == EXPECTED_CLASS_MEMBERSHIP_DIGEST
        ),
        "all_original_monomial_and_signature_counts_reproduce": bool(
            tuple(batched["aggregate_original_monomial_counts"]) == EXPECTED_MONOMIAL_COUNTS
            and batched["original_monomial_count"] == EXPECTED_INDEXED_MONOMIAL_COUNT
            and tuple(batched["aggregate_modulus_signature_counts"]) == EXPECTED_SIGNATURE_COUNTS
            and batched["modulus_signature_count"] == EXPECTED_SIGNATURE_COUNT
        ),
        "all_compatible_multiplicity_counts_reproduce": bool(
            tuple(batched["aggregate_compatible_modulus_signature_counts"])
            == EXPECTED_COMPATIBLE_SIGNATURE_COUNTS
            and batched["compatible_modulus_signature_count"] == EXPECTED_COMPATIBLE_SIGNATURE_COUNT
            and tuple(batched["aggregate_compatible_original_monomial_counts"])
            == EXPECTED_COMPATIBLE_MONOMIAL_COUNTS
            and batched["compatible_original_monomial_count"] == EXPECTED_COMPATIBLE_MONOMIAL_COUNT
        ),
        "all_weighted_and_distinct_comparison_counts_reproduce": bool(
            tuple(batched["aggregate_weighted_comparison_counts"])
            == EXPECTED_WEIGHTED_COMPARISON_COUNTS
            and batched["weighted_comparison_count"] == EXPECTED_WEIGHTED_COMPARISON_COUNT
            and tuple(batched["aggregate_distinct_comparison_counts"])
            == EXPECTED_DISTINCT_COMPARISON_COUNTS
            and batched["distinct_comparison_count"] == EXPECTED_DISTINCT_COMPARISON_COUNT
        ),
        "registered_factorization_and_wave_digests_reproduce": bool(
            batched["group_signature_record_count"] == EXPECTED_GROUP_SIGNATURE_RECORD_COUNT
            and batched["factorization_digest_sha256"] == EXPECTED_FACTORIZATION_DIGEST
            and batched["aggregate_wave_histogram_digest_sha256"] == EXPECTED_WAVE_HISTOGRAM_DIGEST
        ),
        "q011af_outward_dyadic_oracle_reproduces": oracle["passed"],
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
        },
        "selected_modulus_class_counts": [len(group) for group in classes],
        "selected_modulus_class_records": class_records,
        "class_membership_digest_sha256": class_digest,
        "q011af_outward_dyadic_oracle": oracle,
        "aggregate_original_monomial_counts": batched["aggregate_original_monomial_counts"],
        "original_monomial_count": batched["original_monomial_count"],
        "aggregate_modulus_signature_counts": batched["aggregate_modulus_signature_counts"],
        "modulus_signature_count": batched["modulus_signature_count"],
        "aggregate_compatible_modulus_signature_counts": batched[
            "aggregate_compatible_modulus_signature_counts"
        ],
        "compatible_modulus_signature_count": batched["compatible_modulus_signature_count"],
        "aggregate_compatible_original_monomial_counts": batched[
            "aggregate_compatible_original_monomial_counts"
        ],
        "compatible_original_monomial_count": batched["compatible_original_monomial_count"],
        "incompatible_original_monomial_count": batched["incompatible_original_monomial_count"],
        "aggregate_weighted_comparison_counts": batched["aggregate_weighted_comparison_counts"],
        "weighted_comparison_count": batched["weighted_comparison_count"],
        "aggregate_distinct_comparison_counts": batched["aggregate_distinct_comparison_counts"],
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
        "registered_certified_lower_bound_reproduces": bool(
            batched["minimum_certified_gap_lower"]["binary64_hex"] == EXPECTED_CERTIFIED_MINIMUM_HEX
            and Fraction.from_float(batched["minimum_certified_gap_lower"]["float"])
            >= MINIMUM_CERTIFIED_GAP
        ),
        "all_138_near_candidates_refine_to_the_registered_exact_minimum": bool(
            exact["candidate_comparison_count"] == EXPECTED_EXACT_REFINEMENT_CANDIDATE_COUNT
            and exact["exact_global_minimum_tie_count"] == EXPECTED_EXACT_MINIMUM_TIE_COUNT
            and float(q011z._fraction(exact["exact_global_minimum_gap"])).hex()
            == EXPECTED_EXACT_MINIMUM_FLOAT_HEX
            and exact["exact_global_minimum_gap_digest_sha256"] == EXPECTED_EXACT_MINIMUM_DIGEST
            and exact["all_other_aggregate_lower_bounds_exceed_the_exact_cutoff"]
            and exact["canonical_minimum_witness"]["target_identifier"] == "block=14;center=146"
            and exact["canonical_minimum_witness"]["wave_multiplicity"] == 3
        ),
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
                "intervals implies strict separation of their exact "
                "Fraction subsets"
            ),
        },
        "outward_base_records": outward_bases,
        "outward_base_digest_sha256": outward_base_digest,
        "aggregate_records": batched["aggregate_records"],
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
        "maximum_wave_coefficient": batched["maximum_wave_coefficient"],
        "maximum_crude_int64_dot_product_bound": batched["maximum_crude_int64_dot_product_bound"],
        "streaming_contract": batched["streaming_contract"],
        "checks": product_checks,
        "passed": all(product_checks.values()),
    }

    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    inventory_sections = {
        "degree13_modulus_inventory_audit": inventory,
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
        "eleven_artifacts_fifty_eight_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad/ae/af artifacts, runners, "
                "58 digests, outcomes, claim boundaries and Q011l/o "
                "sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_thirteen_inventory_and_forty_four_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "560 aggregates, 8568 controls, 516 separated and 44 registered overlaps"
            ),
            "value": inventory["checks"],
        },
        "uniform_radius_containment_and_100_monotone_moduli_reproduce": {
            "passed": envelope["passed"],
            "threshold": (
                "68 directly relevant intervals, a 100-record monotone "
                "envelope and exact preservation of all 92 Q011af records"
            ),
            "value": envelope["checks"],
        },
        "modulus_classes_weak_compositions_and_q011af_oracle_reproduce": {
            "passed": bool(compression["passed"] and oracle["passed"]),
            "threshold": (
                "4/2/3/6 exact modulus classes, disjoint weak-composition "
                "fibers and the Q011af outward-dyadic oracle reproduce"
            ),
            "value": {
                "compression_checks": compression["checks"],
                "oracle_checks": oracle["checks"],
            },
        },
        "all_degree_thirteen_multiplicities_and_counts_reproduce": {
            "passed": compression["passed"],
            "threshold": (
                "218102520 monomials, 1116561 signatures and all "
                "compatible weighted/distinct counts reproduce"
            ),
            "value": compression["checks"],
        },
        "all_registered_factor_and_array_digests_reproduce": {
            "passed": product_checks["registered_outward_base_and_array_digests_reproduce"],
            "threshold": (
                "8818 factor, 162 coefficient, 44 bound and 340 "
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
        "all_comparisons_lower_bound_and_exact_refinement_reproduce": {
            "passed": bool(
                product_checks["all_registered_relations_are_strict_and_unresolved_is_zero"]
                and product_checks["registered_certified_lower_bound_reproduces"]
                and product_checks["all_138_near_candidates_refine_to_the_registered_exact_minimum"]
            ),
            "threshold": (
                "all 6290384 comparisons are outward-separated, the "
                "registered lower bound holds and 138 exact refinements "
                "give the registered two-way minimum tie"
            ),
            "value": product_checks,
        },
        "coverage_serialization_section_digests_and_runner_reproduce": {
            "passed": bool(coverage and strict_json and digests_reproduce),
            "threshold": (
                "516 old plus 44 full audits cover 560 aggregates and "
                "strict JSON, section digests and runner provenance reproduce"
            ),
            "value": {
                "old_separated": inventory["old_modulus_separated_aggregate_count"],
                "compressed_overlap_audits": len(inventory["overlap_records"]),
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
            "threshold": ("all transformed-residual discs subset rho-discs subset Q011k discs"),
            "value": envelope["checks"],
        },
        "multiplicity_compression_is_exact_and_q011af_oracle_validated": {
            "passed": bool(validity_passed and compression["passed"] and oracle["passed"]),
            "threshold": (
                "exact fibers cover every original monomial and reproduce "
                "the Q011af exact certificate under outward arithmetic"
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
                "6290384 distinct outward separations cover 77400104 "
                "weighted comparisons with zero unresolved overlap"
            ),
            "value": {
                "weighted_relations": product_audit["weighted_relation_counts"],
                "distinct_relations": product_audit["distinct_relation_counts"],
            },
        },
        "certified_margin_and_exact_global_minimum_reproduce": {
            "passed": bool(
                validity_passed
                and product_checks["registered_certified_lower_bound_reproduces"]
                and product_checks["all_138_near_candidates_refine_to_the_registered_exact_minimum"]
            ),
            "threshold": (
                "global certified lower bound >=5e-6 and 138 exact "
                "candidates reproduce the registered global minimum"
            ),
            "value": {
                "certified_lower": product_audit["minimum_certified_gap_lower"],
                "exact_refinement": product_audit["exact_refinement_audit"],
            },
        },
        "degree_thirteen_nonresonance_follows_from_complete_partition": {
            "passed": bool(validity_passed and coverage and zero_unresolved),
            "threshold": (
                "516 old separations and 44 batched full audits imply "
                "degree-13 external nonresonance"
            ),
            "value": {
                "preserved_old_separations": inventory["old_modulus_separated_aggregate_count"],
                "batched_overlap_audits": len(inventory["overlap_records"]),
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011ag degree-thirteen batched audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION
    cycle: dict[str, Any] = {
        "question": (
            "Do exact Fourier multiplicities and outward-rounded dyadic "
            "product enclosures strictly separate all forty-four "
            "degree-thirteen overlap aggregates?"
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
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(_result_digest_sections(cycle))
    certified = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "uniform_transformed_residual_envelope_is_certified": bool(
            validity_passed and envelope["passed"]
        ),
        "exact_fourier_multiplicity_and_outward_product_enclosure_is_certified": bool(certified),
        "all_forty_four_degree_thirteen_old_modulus_overlaps_are_eliminated": bool(certified),
        "degree_thirteen_external_nonresonance_is_certified": certified,
        "certified_external_nonresonance_degrees": (
            list(range(2, 14)) if certified else list(range(2, 13))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(14 if certified else 13, 91)),
        "degrees_14_through_90_are_certified": False,
        "complex_phase_was_required_for_degree_thirteen": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011af_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree thirteen for the fixed 17x17 "
        "repaired exact map on one fixed conservation leaf, the forty-four "
        "Q011u modulus-overlap aggregates, the Q011y transformed-residual "
        "enclosure, uniform rho=5e-8 discs, exact x-Fourier multiplicity "
        "polynomials, exact modulus-class fibers and outward-rounded dyadic "
        "product enclosures. It certifies no degree from 14 through 90, no "
        "all-order nonresonance, equality with the Q011t graph, C2 or higher "
        "graph smoothness, SSM existence or uniqueness, normal attraction, "
        "basin, other grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011af_degree_certificates_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011ah to audit degree 14 with the same exact "
            "Fourier multiplicities and outward-dyadic batching."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Stop at the first outward-unresolved degree-thirteen product; "
            "the preregistration does not permit post-hoc exact rescue."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, envelope, oracle, "
            "factorization, outward-containment, digest or serialization "
            "validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011ag cycle failed strict serialization or digest")
    return cycle


def run_q011ag_study() -> dict[str, Any]:
    cycle = run_degree13_batched_dyadic_audit()
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
                "ordered big-endian array digests, compact summaries and "
                "138 exact near-minimum refinements"
            ),
        },
        "mathematical_scope": {
            "diagnostic": (
                "degree-thirteen exact Fourier-multiplicity and outward-"
                "dyadic refined-envelope indexed-modulus products"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_thirteen_external_nonresonance_claim": (
                cycle["hypothesis_outcome"] == "accepted"
            ),
            "degrees_14_through_90_claim": False,
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
    result = run_q011ag_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
