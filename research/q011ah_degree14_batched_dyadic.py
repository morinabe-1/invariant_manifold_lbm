"""Q011ah degree-fourteen batched outward-dyadic certificate."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011ag_degree13_batched_dyadic as q011ag
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

q011af = q011ag.q011af
q011b = q011ag.q011b
q011u = q011ag.q011u
q011z = q011ag.q011z


def _ints(values: str) -> tuple[int, ...]:
    return tuple(int(value) for value in values.split())


SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
DEGREE = 14
EXPECTED_DEGREE_AGGREGATE_COUNT = 680
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 11_628
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 617
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 63
EXPECTED_SELECTED_GROUP_SIZES = (8, 4, 4, 8)
OVERLAP_COUNTS = (
    (0, 2, 0, 12),
    (0, 2, 1, 11),
    (0, 2, 2, 10),
    (0, 4, 0, 10),
    (0, 4, 1, 9),
    (0, 4, 2, 8),
    (0, 4, 3, 7),
    (2, 5, 2, 5),
    (2, 5, 3, 4),
    (2, 5, 4, 3),
    (2, 5, 5, 2),
    (2, 5, 6, 1),
    (2, 5, 7, 0),
    (3, 4, 0, 7),
    (3, 4, 1, 6),
    (3, 4, 2, 5),
    (3, 4, 3, 4),
    (3, 4, 4, 3),
    (3, 4, 5, 2),
    (3, 4, 6, 1),
    (3, 4, 7, 0),
    (3, 7, 0, 4),
    (3, 7, 1, 3),
    (3, 7, 2, 2),
    (3, 7, 3, 1),
    (3, 7, 4, 0),
    (4, 3, 0, 7),
    (4, 3, 1, 6),
    (4, 3, 2, 5),
    (4, 3, 3, 4),
    (4, 3, 4, 3),
    (4, 3, 5, 2),
    (4, 3, 6, 1),
    (4, 3, 7, 0),
    (4, 6, 0, 4),
    (4, 6, 1, 3),
    (4, 8, 2, 0),
    (5, 2, 0, 7),
    (5, 2, 1, 6),
    (5, 2, 2, 5),
    (5, 2, 3, 4),
    (5, 2, 4, 3),
    (5, 2, 5, 2),
    (5, 2, 6, 1),
    (5, 2, 7, 0),
    (5, 7, 0, 2),
    (5, 7, 1, 1),
    (5, 7, 2, 0),
    (6, 1, 0, 7),
    (6, 1, 1, 6),
    (6, 1, 2, 5),
    (6, 6, 0, 2),
    (6, 6, 1, 1),
    (6, 6, 2, 0),
    (7, 5, 0, 2),
    (7, 5, 1, 1),
    (7, 5, 2, 0),
    (8, 0, 6, 0),
    (8, 4, 0, 2),
    (8, 4, 1, 1),
    (8, 4, 2, 0),
    (9, 1, 2, 2),
    (9, 1, 3, 1),
)
EXTERNAL_GROUP_INDICES = _ints(
    """
    167 167 167 165 165 165 165 162 162 162 162 162 162 162 162 162
    162 162 162 162 162 159 159 159 159 159 162 162 162 162 162 162
    162 162 159 159 157 162 162 162 162 162 162 162 162 156 156 156
    162 162 162 156 156 156 156 156 156 161 156 156 156 158 158
    """
)
EXPECTED_EXTERNAL_TARGET_COUNTS = tuple(
    4 if index in (158, 165) else 8 for index in EXTERNAL_GROUP_INDICES
)
EXPECTED_UNIQUE_EXTERNAL_TARGET_COUNT = 56
EXPECTED_DIRECTLY_RELEVANT_IDENTIFIER_COUNT = 80
EXPECTED_RELEVANT_IDENTIFIER_COUNT = 112
EXPECTED_UNIQUE_CENTER_MODULUS_EVALUATION_COUNT = 67
EXPECTED_MODULUS_CLASS_COUNTS = (4, 2, 3, 6)

EXPECTED_MONOMIAL_COUNTS = _ints(
    """
    503880 1272960 1944800 680680 1601600 2252250 2402400 15966720
    13305600 8467200 4064256 1354752 241920 14414400 28828800 33264000
    27720000 17640000 8467200 2822400 504000 4752000 6912000 5184000
    2304000 504000 22651200 45302400 52272000 43560000 27720000 13305600
    4435200 792000 9147600 13305600 544500 27181440 54362880 62726400
    52272000 33264000 15966720 5322240 950400 3421440 3041280 950400
    23557248 47114496 54362880 5189184 4612608 1441440 6918912 6150144
    1921920 540540 8108100 7207200 2252250 16473600 7321600
    """
)
EXPECTED_SIGNATURE_COUNTS = _ints(
    """
    18564 39312 54054 15015 30030 38610 39600 90720 75600 50400 26460
    10080 2160 79200 138600 151200 126000 84000 44100 16800 3600 20160
    26880 20160 9600 2400 110880 194040 211680 176400 117600 61740
    23520 5040 30870 41160 1890 133056 232848 254016 211680 141120
    74088 28224 6048 9408 8064 2688 133056 232848 254016 12348 10584
    3528 15120 12960 4320 4620 17325 14850 4950 55440 26400
    """
)
EXPECTED_COMPATIBLE_SIGNATURE_COUNTS = _ints(
    """
    9636 20028 27486 7335 14890 19075 19640 80640 67200 44400 22860
    8400 1680 67200 121800 134400 112000 74000 38100 14000 2800 20160
    26880 20160 9600 2400 94080 170520 188160 156800 103600 53340 19600
    3920 30870 41160 1890 112896 204624 225792 188160 124320 64008
    23520 4704 9408 8064 2688 112896 204624 225792 12348 10584 3528
    15120 12960 4320 2970 17325 14850 4950 55440 26400
    """
)
EXPECTED_COMPATIBLE_MONOMIAL_COUNTS = _ints(
    """
    111460 286160 443468 102190 244780 347546 373184 2730176 2272888
    1456320 708920 241280 44008 2422080 4754880 5427840 4517680 2898400
    1414800 483200 88640 882480 1290080 965200 429440 92800 3729440
    7309440 8337280 6938500 4454480 2177380 744920 137040 1718860
    2510300 125070 4496192 8816112 10057888 8370464 5372736 2625376
    897904 165080 865408 775040 238944 4000768 7860592 8976544 1324488
    1187056 365480 1776480 1592768 490048 157520 2088750 1872740
    576190 2874800 1254240
    """
)
EXPECTED_WEIGHTED_COMPARISON_COUNTS = _ints(
    """
    324728 838600 1305920 204380 489560 695092 746368 5460352 4545776
    2912640 1417840 482560 88016 4844160 9509760 10855680 9035360
    5796800 2829600 966400 177280 2525920 3660160 2758240 1217600
    269920 7458880 14618880 16674560 13877000 8908960 4354760 1489840
    274080 5006760 7251400 250140 8992384 17632224 20115776 16740928
    10745472 5250752 1795808 330160 1730816 1550080 477888 8001536
    15721184 17953088 2648976 2374112 730960 3552960 3185536 980096
    315040 4177500 3745480 1152380 4257840 1852960
    """
)
EXPECTED_DISTINCT_COMPARISON_COUNTS = _ints(
    """
    71052 150672 208848 29340 59560 76300 78560 506880 422880 280320
    145920 54720 11040 430400 773600 844800 704800 467200 243200 91200
    18400 103040 138240 104960 48640 12160 602560 1083040 1182720
    986720 654080 340480 127680 25760 157780 211680 10080 723072
    1299648 1419264 1184064 784896 408576 153216 30912 57344 50176
    16128 723072 1299648 1419264 75264 65856 21168 92160 80640 25920
    22440 105600 92400 29700 170720 80960
    """
)

EXPECTED_INDEXED_MONOMIAL_COUNT = 893_043_240
EXPECTED_SIGNATURE_COUNT = 4_091_730
EXPECTED_COMPATIBLE_SIGNATURE_COUNT = 3_543_001
EXPECTED_COMPATIBLE_MONOMIAL_COUNT = 152_292_218
EXPECTED_WEIGHTED_COMPARISON_COUNT = 310_135_908
EXPECTED_DISTINCT_COMPARISON_COUNT = 21_891_420
EXPECTED_WEIGHTED_RELATIONS = {
    "product_below_target": 204_194_352,
    "target_below_product": 105_941_556,
}
EXPECTED_DISTINCT_RELATIONS = {
    "product_below_target": 14_247_584,
    "target_below_product": 7_643_836,
}
EXPECTED_GROUP_SIGNATURE_RECORD_COUNT = 19_440
EXPECTED_COEFFICIENT_MATRIX_COUNT = 232
EXPECTED_BOUND_MATRIX_COUNT = 63
EXPECTED_CLASSIFICATION_MATRIX_COUNT = 480
EXPECTED_MAXIMUM_WAVE_COEFFICIENT = 548
EXPECTED_MAXIMUM_LIVE_SIGNATURE_COUNT = 254_016
EXPECTED_EXACT_REFINEMENT_CANDIDATE_COUNT = 278
EXPECTED_EXACT_MINIMUM_TIE_COUNT = 2

UNIFORM_REFINED_RADIUS = Fraction(5, 10**8)
MINIMUM_CERTIFIED_GAP = Fraction(5, 10**6)
EXPECTED_CERTIFIED_MINIMUM_HEX = "0x1.7b351910fffffp-18"
EXPECTED_ORACLE_CERTIFIED_MINIMUM_HEX = "0x1.84c3ca21dffffp-18"
EXPECTED_EXACT_MINIMUM_FLOAT_HEX = "0x1.7b3519192bcd2p-18"
EXPECTED_EXACT_MINIMUM_DIGEST = "ac40d9d8023786f5ff921cc045db0b0cc03a041ddc8a768d701c85a92e041664"
EXPECTED_EXACT_CANDIDATE_DIGEST = "b0b3a98eed00d21106b53e6493bbd26d5f5384fe718309d49122b29013de66f8"

EXPECTED_INVENTORY_DIGEST = "3ef339e30f7a2a531d4dc83e83a4d5f33d505a23e41d3cc29c7b41afa206e1b6"
EXPECTED_UNIFORM_RECORD_DIGEST = "4d1402e2a71c2de26fa35d9fac739a0258b35b0a2873a95148fe5be4454b6ac3"
EXPECTED_CLASS_MEMBERSHIP_DIGEST = q011ag.EXPECTED_CLASS_MEMBERSHIP_DIGEST
EXPECTED_OUTWARD_BASE_DIGEST = q011ag.EXPECTED_OUTWARD_BASE_DIGEST
EXPECTED_FACTORIZATION_DIGEST = "d9864e1c230c64a4d14263d73c2cbdfea4168a11d5bf45515d1ea96b166c0e65"
EXPECTED_WAVE_HISTOGRAM_DIGEST = "0e7c21a64e13b5467662d4897685b4e0c1dfb5fdc471ff25401ec91eb24d00cc"
EXPECTED_COEFFICIENT_MATRIX_DIGEST = (
    "ca3e91f4842a3ce7fab87bd07d24558875b58ad24423257750cf4dda777af13b"
)
EXPECTED_DYADIC_BOUND_DIGEST = "27089bc09c64fef366f04422eb8878d769ab450ff96325f6875c5636ef88378e"
EXPECTED_CLASSIFICATION_MATRIX_DIGEST = (
    "37ae2ecb609f79883ad3cab5355b2e5885612cb07ca8e3131c4df10d9755ea59"
)
EXPECTED_COMPACT_PILOT_DIGEST = "e473b5893927b2bf87665caa358f2a567caf608b8da715e9fd348a34a90c5bd0"

Q011AG_ARTIFACT_SHA256 = "76c162133c228aecf988fb121dafc86c1dfae5c44cab465772534d2c863393fb"
Q011AG_RUNNER_SHA256 = "cf27aba440b291ebfba5f020a1cf77537335520cfdc9490290de836069cfd11f"
Q011AG_DIGEST_NAMES = (
    "input_digest_sha256",
    "inventory_digest_sha256",
    "compression_digest_sha256",
    "product_digest_sha256",
    "result_digest_sha256",
)
Q011AG_DIGESTS = (
    "8a6156a2667469bd0c0666a344e79a04cbc761a3ab0bb134e0853baf6c432aa9",
    "a901dedf2014c6d6738160890b09bc55118724324b6624494971c1688550f0d7",
    "f117716264aac394b4e2de41bbbf5a0f5868a55bd3c12cc2f00afe4c87181e95",
    "2b4b4d8315017fd162dcbf5aebeb4fd7c5c33ec34280564a36a9d8149f9a28f8",
    "ebee85b19911947316a3aacf6710e928433e4d155bfc9620b1119003a34faab3",
)

ACCEPTED_CLASSIFICATION = (
    "degree-14 external nonresonance is certified by exact Fourier "
    "multiplicities and outward-rounded dyadic product enclosures"
)
REJECTED_CLASSIFICATION = (
    "at least one degree-14 outward-dyadic indexed-modulus product "
    "remains inseparable from an external target"
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
    prior, artifacts = q011ag._sealed_input_audit()
    artifact_path = _artifact_directory() / "q011ag_degree13_batched_dyadic.json"
    runner_path = Path(q011ag.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    digests = tuple(cycle[name] for name in Q011AG_DIGEST_NAMES)
    checks = {
        "q011ag_eleven_prior_artifacts_and_helpers_reproduce": bool(
            prior["passed"] and prior["direct_digest_count"] == 58 and all(prior["checks"].values())
        ),
        "q011ag_artifact_sha256_matches": (_file_sha256(artifact_path) == Q011AG_ARTIFACT_SHA256),
        "q011ag_runner_sha256_matches": bool(
            _file_sha256(runner_path) == Q011AG_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011AG_RUNNER_SHA256
        ),
        "q011ag_digests_match": digests == Q011AG_DIGESTS,
        "q011ag_registered_outcome_reproduces": bool(
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["scientific_classification"] == q011ag.ACCEPTED_CLASSIFICATION
        ),
        "q011ag_degree_thirteen_scope_is_preserved": bool(
            cycle["theorem_consequence"]["degree_thirteen_external_nonresonance_is_certified"]
            and cycle["theorem_consequence"]["certified_external_nonresonance_degrees"]
            == list(range(2, 14))
            and cycle["theorem_consequence"]["missing_external_nonresonance_degrees"]
            == list(range(14, 91))
            and not cycle["theorem_consequence"]["ssm_existence_or_uniqueness_is_certified"]
        ),
        "q011ag_claim_boundary_is_present": bool(cycle["claim_boundary"]),
        "q011ag_package_source_metadata_matches": artifact["source"] == source_metadata(),
        "q011ag_artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact)
            and _strict_json_serializable(artifact)
            and json.dumps(artifact, allow_nan=False)
        ),
        "sixty_three_direct_digests_are_sealed": (
            prior["direct_digest_count"] + len(digests) == 63
        ),
    }
    artifacts["q011ag"] = artifact
    audit = {
        "prior_q011ag_sealed_input_audit": prior,
        "q011ag": {
            "artifact_filename": artifact_path.name,
            "artifact_sha256": _file_sha256(artifact_path),
            "runner_filename": runner_path.name,
            "runner_sha256": _file_sha256(runner_path),
            "digest_names": list(Q011AG_DIGEST_NAMES),
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
        "q011u_degree_fourteen_record_is_unique_and_complete": bool(
            len(degree_records) == 1
            and degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"] == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "all_sixty_three_overlap_tuples_and_external_groups_reproduce": bool(
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
        "old_degree_thirteen_certificate_is_preserved": artifacts["q011ag"]["cycle"][
            "theorem_consequence"
        ]["degree_thirteen_external_nonresonance_is_certified"],
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
        for record in artifacts["q011ag"]["cycle"]["uniform_refined_envelope_audit"][
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
            if external_index in (157, 158)
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
        "all_80_direct_and_112_monotone_identifiers_have_uniform_intervals": bool(
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
        "all_q011ag_100_uniform_records_are_preserved_exactly": bool(
            len(prior_records) == 100
            and set(prior_records).issubset(current_records)
            and all(
                current_records[identifier] == record
                for identifier, record in prior_records.items()
            )
        ),
        "only_twelve_group_157_158_records_are_added": bool(
            len(new_identifiers) == 12 and new_identifiers == expected_new_identifiers
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
        "new_group_157_158_identifiers": sorted(new_identifiers),
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


def _q011ag_oracle_audit(
    artifacts: dict[str, dict[str, Any]],
    classes: tuple[tuple[tuple[str, ...], ...], ...],
    lookup: dict[str, q011z._UniformDisc],
) -> dict[str, Any]:
    cycle = artifacts["q011ag"]["cycle"]
    inventory = cycle["degree13_modulus_inventory_audit"]
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
        "all_registered_q011ag_counts_reproduce": bool(
            audit["original_monomial_count"]
            == compression["original_monomial_count"]
            == 218_102_520
            and audit["modulus_signature_count"]
            == compression["modulus_signature_count"]
            == 1_116_561
            and audit["compatible_modulus_signature_count"]
            == compression["compatible_modulus_signature_count"]
            == 1_004_653
            and audit["compatible_original_monomial_count"]
            == compression["compatible_original_monomial_count"]
            == 38_119_852
            and audit["weighted_comparison_count"]
            == product["weighted_comparison_count"]
            == 77_400_104
            and audit["distinct_comparison_count"]
            == product["distinct_comparison_count"]
            == 6_290_384
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
            and audit["minimum_certified_gap_witness"]["aggregate_index"] == 4
            and audit["minimum_certified_gap_witness"]["selected_type_counts"] == [0, 5, 2, 6]
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
        "degree": 13,
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


def run_degree14_batched_dyadic_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, selected_groups, external_target_groups, overlap_records = _inventory_audit(
        artifacts
    )
    envelope, lookup = _uniform_envelope_audit(artifacts, selected_groups, external_target_groups)
    classes, class_records = q011ag._modulus_classes(selected_groups, lookup)
    class_digest = q011b._canonical_json_sha256(class_records)
    outward_bases = q011ag._outward_base_records(classes, lookup)
    outward_base_digest = q011b._canonical_json_sha256(outward_bases)
    oracle = _q011ag_oracle_audit(artifacts, classes, lookup)
    batched = q011ag._batched_audit(
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
        raise RuntimeError("Q011ah exact refinement was not run")

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
        "q011ag_outward_dyadic_oracle_reproduces": oracle["passed"],
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
        "q011ag_outward_dyadic_oracle": oracle,
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
        "all_278_near_candidates_refine_to_the_registered_exact_minimum": bool(
            exact["candidate_comparison_count"] == EXPECTED_EXACT_REFINEMENT_CANDIDATE_COUNT
            and exact["candidate_exact_record_digest_sha256"] == EXPECTED_EXACT_CANDIDATE_DIGEST
            and exact["exact_global_minimum_tie_count"] == EXPECTED_EXACT_MINIMUM_TIE_COUNT
            and float(q011z._fraction(exact["exact_global_minimum_gap"])).hex()
            == EXPECTED_EXACT_MINIMUM_FLOAT_HEX
            and exact["exact_global_minimum_gap_digest_sha256"] == EXPECTED_EXACT_MINIMUM_DIGEST
            and exact["all_other_aggregate_lower_bounds_exceed_the_exact_cutoff"]
            and exact["canonical_minimum_witness"]["aggregate_index"] == 5
            and exact["canonical_minimum_witness"]["target_identifier"] == "block=14;center=146"
            and exact["canonical_minimum_witness"]["wave_multiplicity"] == 2
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
                "intervals implies strict separation of their exact Fraction subsets"
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
    input_sections = {"registered_parameters": registered, "sealed_input_audit": sealed}
    inventory_sections = {
        "degree14_modulus_inventory_audit": inventory,
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
        "twelve_artifacts_sixty_three_digests_and_helpers_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/u/x/y/z/aa/ab/ac/ad/ae/af/ag artifacts, runners, "
                "63 digests, outcomes, claim boundaries and Q011l/o sources reproduce"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_fourteen_inventory_and_sixty_three_overlaps_reproduce": {
            "passed": inventory["passed"],
            "threshold": (
                "680 aggregates, 11628 controls, 617 separated and 63 registered overlaps"
            ),
            "value": inventory["checks"],
        },
        "uniform_radius_containment_and_112_monotone_moduli_reproduce": {
            "passed": envelope["passed"],
            "threshold": (
                "80 directly relevant intervals, a 112-record monotone "
                "envelope and exact preservation of all 100 Q011ag records"
            ),
            "value": envelope["checks"],
        },
        "modulus_classes_weak_compositions_and_q011ag_oracle_reproduce": {
            "passed": bool(compression["passed"] and oracle["passed"]),
            "threshold": (
                "4/2/3/6 exact modulus classes, disjoint weak-composition "
                "fibers and the Q011ag outward-dyadic oracle reproduce"
            ),
            "value": {
                "compression_checks": compression["checks"],
                "oracle_checks": oracle["checks"],
            },
        },
        "all_degree_fourteen_multiplicities_and_counts_reproduce": {
            "passed": compression["passed"],
            "threshold": (
                "893043240 monomials, 4091730 signatures and all "
                "compatible weighted/distinct counts reproduce"
            ),
            "value": compression["checks"],
        },
        "all_registered_factor_and_array_digests_reproduce": {
            "passed": product_checks["registered_outward_base_and_array_digests_reproduce"],
            "threshold": (
                "19440 factor, 232 coefficient, 63 bound and 480 "
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
                and product_checks["all_278_near_candidates_refine_to_the_registered_exact_minimum"]
            ),
            "threshold": (
                "all 21891420 comparisons are outward-separated, the "
                "registered lower bound holds and 278 exact refinements "
                "give the registered two-way minimum tie"
            ),
            "value": product_checks,
        },
        "coverage_serialization_section_digests_and_runner_reproduce": {
            "passed": bool(coverage and strict_json and digests_reproduce),
            "threshold": (
                "617 old plus 63 full audits cover 680 aggregates and "
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
            "threshold": "all transformed-residual discs subset rho-discs subset Q011k discs",
            "value": envelope["checks"],
        },
        "multiplicity_compression_is_exact_and_q011ag_oracle_validated": {
            "passed": bool(validity_passed and compression["passed"] and oracle["passed"]),
            "threshold": (
                "exact fibers cover every original monomial and reproduce "
                "the Q011ag certificate under outward arithmetic"
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
                "21891420 distinct outward separations cover 310135908 "
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
                and product_checks["all_278_near_candidates_refine_to_the_registered_exact_minimum"]
            ),
            "threshold": (
                "global certified lower bound >=5e-6 and 278 exact "
                "candidates reproduce the registered global minimum"
            ),
            "value": {
                "certified_lower": product_audit["minimum_certified_gap_lower"],
                "exact_refinement": product_audit["exact_refinement_audit"],
            },
        },
        "degree_fourteen_nonresonance_follows_from_complete_partition": {
            "passed": bool(validity_passed and coverage and zero_unresolved),
            "threshold": (
                "617 old separations and 63 batched full audits imply "
                "degree-14 external nonresonance"
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
        classification = "registered Q011ah degree-fourteen batched audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION
    cycle: dict[str, Any] = {
        "question": (
            "Do exact Fourier multiplicities and outward-rounded dyadic "
            "product enclosures strictly separate all sixty-three "
            "degree-fourteen overlap aggregates?"
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
        "exact_fourier_multiplicity_and_outward_product_enclosure_is_certified": certified,
        "all_sixty_three_degree_fourteen_old_modulus_overlaps_are_eliminated": certified,
        "degree_fourteen_external_nonresonance_is_certified": certified,
        "certified_external_nonresonance_degrees": (
            list(range(2, 15)) if certified else list(range(2, 14))
        ),
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(15 if certified else 14, 91)),
        "degrees_15_through_90_are_certified": False,
        "complex_phase_was_required_for_degree_fourteen": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_through_q011ag_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree fourteen for the fixed 17x17 "
        "repaired exact map on one fixed conservation leaf, the sixty-three "
        "Q011u modulus-overlap aggregates, the Q011y transformed-residual "
        "enclosure, uniform rho=5e-8 discs, exact x-Fourier multiplicity "
        "polynomials, exact modulus-class fibers and outward-rounded dyadic "
        "product enclosures. It certifies no degree from 15 through 90, no "
        "all-order nonresonance, equality with the Q011t graph, C2 or higher "
        "graph smoothness, SSM existence or uniqueness, normal attraction, "
        "basin, other grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
        "q011x_through_q011ag_degree_certificates_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011ai to audit degree 15 with the same exact "
            "Fourier multiplicities and outward-dyadic batching."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Stop at the first outward-unresolved degree-fourteen product; "
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
        raise RuntimeError("Q011ah cycle failed strict serialization or digest")
    return cycle


def run_q011ah_study() -> dict[str, Any]:
    cycle = run_degree14_batched_dyadic_audit()
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
                "278 exact near-minimum refinements"
            ),
        },
        "mathematical_scope": {
            "diagnostic": (
                "degree-fourteen exact Fourier-multiplicity and outward-"
                "dyadic refined-envelope indexed-modulus products"
            ),
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_fourteen_external_nonresonance_claim": (
                cycle["hypothesis_outcome"] == "accepted"
            ),
            "degrees_15_through_90_claim": False,
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
    result = run_q011ah_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
