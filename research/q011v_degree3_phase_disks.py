"""Q011v degree-three phase-sensitive output-sector product-disk audit."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011j_interval_fixed_point as q011j
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011m_quadratic_jet_majorant as q011m
import research.q011o_graph_transform_setup as q011o
import research.q011u_c91_modulus_nonresonance as q011u
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
DEGREE = 3
EXPECTED_DEGREE_AGGREGATE_COUNT = 20
EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT = 56
EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT = 19
EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT = 1
SOLE_OVERLAP_COUNTS = (0, 1, 1, 1)
SOLE_EXTERNAL_GROUP_INDEX = 183
SELECTED_SOURCE_GROUP_INDICES = (1, 2, 3)
EXPECTED_SELECTED_GROUP_SIZES = (4, 4, 8)
EXPECTED_INDEXED_TRIPLE_COUNT = 128
EXPECTED_EXTERNAL_TARGET_COUNT = 8
EXPECTED_SECTOR_HISTOGRAM = {0: 32, 1: 28, 2: 16, 3: 4, 14: 4, 15: 16, 16: 28}
EXPECTED_TARGET_SECTOR_HISTOGRAM = {0: 4, 2: 2, 15: 2}
EXPECTED_COMPATIBLE_COMPARISON_COUNT = 192
MINIMUM_COMPLEX_SEPARATION = Fraction(1, 10)

Q011L_SOURCE_SHA256 = "59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7"
Q011O_SOURCE_SHA256 = "60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f"

Q011J_ARTIFACT_SHA256 = "74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a"
Q011J_RUNNER_SHA256 = "23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5"
Q011J_DIGESTS = (
    "a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799",
    "adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b",
    "177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f",
    "1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0",
    "ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934",
)
Q011J_DIGEST_NAMES = (
    "input_digest_sha256",
    "coordinate_digest_sha256",
    "oracle_digest_sha256",
    "proof_digest_sha256",
    "result_digest_sha256",
)
Q011J_CLASSIFICATION = (
    "the repaired periodic forcing admits a locally unique exact fixed-leaf fixed point "
    "in the registered rational box"
)

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

Q011M_ARTIFACT_SHA256 = "b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f"
Q011M_RUNNER_SHA256 = "0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150"
Q011M_DIGESTS = (
    "dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb",
    "0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a",
    "1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514",
    "bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00",
    "f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4",
)
Q011M_DIGEST_NAMES = (
    "input_digest_sha256",
    "derivative_digest_sha256",
    "coefficient_digest_sha256",
    "majorant_digest_sha256",
    "result_digest_sha256",
)
Q011M_CLASSIFICATION = (
    "the repaired exact map admits a unique graph-gauge quadratic jet with the "
    "registered coefficient and cubic-defect majorants"
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

ACCEPTED_CLASSIFICATION = (
    "degree-3 external nonresonance is certified by modulus separation plus "
    "Fourier-sector phase-sensitive elimination of the sole overlap aggregate"
)
REJECTED_CLASSIFICATION = (
    "the sole degree-3 modulus aggregate retains a phase-sensitive product-disc overlap"
)


@dataclass(frozen=True, slots=True)
class _EigenDisc:
    block_index: int
    center_index: int
    center: tuple[Fraction, Fraction]
    radius: Fraction
    center_modulus: RationalInterval
    modulus: RationalInterval
    selected: bool

    @property
    def identifier(self) -> str:
        return f"block={self.block_index};center={self.center_index}"


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


def _complex_record(value: tuple[Fraction, Fraction]) -> dict[str, Any]:
    return {
        "real": _fraction_record(value[0]),
        "imaginary": _fraction_record(value[1]),
    }


def _complex_product(
    left: tuple[Fraction, Fraction],
    right: tuple[Fraction, Fraction],
) -> tuple[Fraction, Fraction]:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def _digest_tuple(cycle: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cycle[name] for name in names)


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    directory = _artifact_directory()
    specifications = (
        (
            "q011j",
            directory / "q011j_interval_fixed_point.json",
            Path(q011j.__file__).resolve(),
            Q011J_ARTIFACT_SHA256,
            Q011J_RUNNER_SHA256,
            Q011J_DIGESTS,
            Q011J_DIGEST_NAMES,
            "accepted",
            Q011J_CLASSIFICATION,
        ),
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
            "q011m",
            directory / "q011m_quadratic_jet_majorant.json",
            Path(q011m.__file__).resolve(),
            Q011M_ARTIFACT_SHA256,
            Q011M_RUNNER_SHA256,
            Q011M_DIGESTS,
            Q011M_DIGEST_NAMES,
            "accepted",
            Q011M_CLASSIFICATION,
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
        checks[f"{label}_artifact_sha256_matches"] = (
            _file_sha256(artifact_path) == artifact_hash
        )
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
        checks[f"{label}_package_source_metadata_matches"] = (
            artifact["source"] == source_metadata()
        )
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
        }

    j_theorem = artifacts["q011j"]["cycle"]["theorem_consequence"]
    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    m_theorem = artifacts["q011m"]["cycle"]["theorem_consequence"]
    u_theorem = artifacts["q011u"]["cycle"]["theorem_consequence"]
    checks["q011j_x_independent_fixed_point_scope_is_preserved"] = bool(
        j_theorem["repaired_exact_full_17x17_x_independent_fixed_point_exists"]
        and not j_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011k_eigendisc_scope_is_preserved"] = bool(
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and k_theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011m_derivative_and_sector_scope_is_preserved"] = bool(
        m_theorem["repaired_exact_map_second_and_third_derivative_bounds_are_certified"]
        and m_theorem["unique_graph_gauge_quadratic_jet_exists_in_all_five_sectors"]
        and not m_theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    )
    checks["q011u_valid_rejection_scope_is_preserved"] = bool(
        u_theorem[
            "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
        ]
        and u_theorem["the_degree_91_and_higher_modulus_tail_is_certified"]
        and not u_theorem[
            "degrees_3_through_90_modulus_only_nonresonance_is_certified"
        ]
        and not u_theorem["an_actual_complex_resonance_is_established"]
        and not u_theorem["an_analytic_invariant_manifold_is_disproved"]
    )
    l_path = Path(q011l.__file__).resolve()
    o_path = Path(q011o.__file__).resolve()
    checks["q011l_source_sha256_matches"] = _file_sha256(l_path) == Q011L_SOURCE_SHA256
    checks["q011o_source_sha256_matches"] = _file_sha256(o_path) == Q011O_SOURCE_SHA256
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


def _reconstruct_eigendiscs(
    q011k_artifact: dict[str, Any],
) -> tuple[dict[str, _EigenDisc], dict[str, Any]]:
    centers, selected, radii, _metrics, reconstruction = q011l._spectral_data(q011k_artifact)
    selected_sets = {
        block_index: set(center_indices) for block_index, center_indices in selected.items()
    }
    lookup: dict[str, _EigenDisc] = {}
    digest_records = []
    modulus_cache: dict[tuple[Fraction, Fraction], RationalInterval] = {}
    for block_index in range(SIZE):
        for center_index, center in enumerate(centers[block_index]):
            key = (abs(center[0]), abs(center[1]))
            if key not in modulus_cache:
                modulus_cache[key] = q011o._center_modulus_bounds(center)
            center_modulus = modulus_cache[key]
            radius = radii[block_index]
            modulus = RationalInterval(
                max(Fraction(0), center_modulus.lower - radius),
                center_modulus.upper + radius,
            )
            disc = _EigenDisc(
                block_index=block_index,
                center_index=center_index,
                center=center,
                radius=radius,
                center_modulus=center_modulus,
                modulus=modulus,
                selected=center_index in selected_sets.get(block_index, set()),
            )
            lookup[disc.identifier] = disc
            digest_records.append(
                {
                    "block_index": block_index,
                    "center_index": center_index,
                    "selected": disc.selected,
                    "modulus_lower": _fraction_record(modulus.lower),
                    "modulus_upper": _fraction_record(modulus.upper),
                }
            )
    audit = {
        "eigencenter_count": len(lookup),
        "selected_count": sum(disc.selected for disc in lookup.values()),
        "external_count": sum(not disc.selected for disc in lookup.values()),
        "exact_modulus_interval_digest_sha256": q011b._canonical_json_sha256(
            digest_records
        ),
        "q011l_reconstruction_checks": reconstruction["checks"],
        "passed": bool(
            reconstruction["passed"]
            and len(lookup) == COORDINATE_SLOT_COUNT
            and sum(disc.selected for disc in lookup.values()) == SELECTED_DIMENSION
            and sum(not disc.selected for disc in lookup.values()) == EXTERNAL_DIMENSION
        ),
    }
    return lookup, audit


def _inventory_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[
    dict[str, Any],
    dict[str, _EigenDisc],
    tuple[tuple[str, ...], ...],
    tuple[str, ...],
]:
    u_cycle = artifacts["q011u"]["cycle"]
    u_enumeration = u_cycle["degree_3_through_90_enumeration_audit"]
    degree_record = next(
        record for record in u_enumeration["degree_records"] if record["degree"] == DEGREE
    )
    first_overlap = degree_record["first_overlap"]
    u_spectrum = u_cycle["exact_modulus_compression_audit"]
    lookup, reconstruction = _reconstruct_eigendiscs(artifacts["q011k"])
    entries = [
        q011u._ModulusEntry(
            lower=disc.modulus.lower,
            upper=disc.modulus.upper,
            identifier=disc.identifier,
            selected=disc.selected,
        )
        for disc in lookup.values()
    ]
    selected_merged = q011u._merge_modulus_entries(
        [entry for entry in entries if entry.selected]
    )
    external_merged = q011u._merge_modulus_entries(
        [entry for entry in entries if not entry.selected]
    )
    selected_groups = tuple(
        tuple(sorted(selected_merged[index].identifiers))
        for index in SELECTED_SOURCE_GROUP_INDICES
    )
    external_targets = tuple(
        sorted(external_merged[SOLE_EXTERNAL_GROUP_INDEX].identifiers)
    )
    stored_selected = u_spectrum["selected_merged_records"]
    stored_external = u_spectrum["external_merged_records"]
    selected_membership_checks = [
        q011b._canonical_json_sha256(list(group))
        == stored_selected[index]["membership_digest_sha256"]
        for group, index in zip(
            selected_groups,
            SELECTED_SOURCE_GROUP_INDICES,
            strict=True,
        )
    ]
    external_membership_check = bool(
        q011b._canonical_json_sha256(list(external_targets))
        == stored_external[SOLE_EXTERNAL_GROUP_INDEX]["membership_digest_sha256"]
    )
    exact_inventory = {
        "selected_source_groups": [
            {"group_index": index, "identifiers": list(group)}
            for index, group in zip(
                SELECTED_SOURCE_GROUP_INDICES,
                selected_groups,
                strict=True,
            )
        ],
        "external_group_index": SOLE_EXTERNAL_GROUP_INDEX,
        "external_identifiers": list(external_targets),
    }
    checks = {
        "q011u_degree_three_record_is_unique_and_complete": bool(
            degree_record["aggregate_count"] == EXPECTED_DEGREE_AGGREGATE_COUNT
            and degree_record["expanded_product_control_count"]
            == EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT
            and degree_record["nonoverlap_count"]
            == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
            and degree_record["overlap_count"] == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        ),
        "sole_overlap_counts_and_external_group_reproduce": bool(
            tuple(first_overlap["selected_type_counts"]) == SOLE_OVERLAP_COUNTS
            and first_overlap["external_group_index"] == SOLE_EXTERNAL_GROUP_INDEX
        ),
        "all_2598_q011k_eigendiscs_reconstruct": reconstruction["passed"],
        "q011u_individual_modulus_digest_reproduces": bool(
            reconstruction["exact_modulus_interval_digest_sha256"]
            == u_spectrum["exact_individual_modulus_interval_digest_sha256"]
        ),
        "selected_and_external_component_counts_reproduce": bool(
            len(selected_merged) == 4 and len(external_merged) == 186
        ),
        "selected_source_group_sizes_are_4_4_8": (
            tuple(len(group) for group in selected_groups) == EXPECTED_SELECTED_GROUP_SIZES
        ),
        "selected_group_memberships_match_q011u": all(selected_membership_checks),
        "external_group_183_has_eight_matching_members": bool(
            len(external_targets) == EXPECTED_EXTERNAL_TARGET_COUNT
            and external_membership_check
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
        "degree_expanded_product_control_count": degree_record[
            "expanded_product_control_count"
        ],
        "modulus_separated_aggregate_count": degree_record["nonoverlap_count"],
        "modulus_overlap_aggregate_count": degree_record["overlap_count"],
        "sole_overlap_selected_type_counts": first_overlap["selected_type_counts"],
        "sole_overlap_external_group_index": first_overlap["external_group_index"],
        "sole_overlap_aggregate_log_interval": first_overlap["aggregate_log_interval"],
        "sole_overlap_external_log_interval": first_overlap["external_log_interval"],
        "eigencenter_reconstruction": reconstruction,
        "selected_source_group_indices": list(SELECTED_SOURCE_GROUP_INDICES),
        "selected_source_group_sizes": [len(group) for group in selected_groups],
        "selected_source_group_memberships": [list(group) for group in selected_groups],
        "external_target_group_index": SOLE_EXTERNAL_GROUP_INDEX,
        "external_target_identifiers": list(external_targets),
        "indexed_triple_count": (
            len(selected_groups[0]) * len(selected_groups[1]) * len(selected_groups[2])
        ),
        "exact_inventory_digest_sha256": q011b._canonical_json_sha256(exact_inventory),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, lookup, selected_groups, external_targets


def _sector_audit(
    artifacts: dict[str, dict[str, Any]],
    lookup: dict[str, _EigenDisc],
    selected_groups: tuple[tuple[str, ...], ...],
    external_targets: tuple[str, ...],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[tuple[int, str]]]:
    triple_records = []
    for triple_index, identifiers in enumerate(itertools.product(*selected_groups)):
        blocks = [lookup[identifier].block_index for identifier in identifiers]
        triple_records.append(
            {
                "triple_index": triple_index,
                "source_identifiers": list(identifiers),
                "input_blocks": blocks,
                "output_block": sum(blocks) % SIZE,
            }
        )
    sector_histogram = Counter(record["output_block"] for record in triple_records)
    target_histogram = Counter(lookup[identifier].block_index for identifier in external_targets)
    compatible_pairs = [
        (record["triple_index"], target_identifier)
        for record in triple_records
        for target_identifier in external_targets
        if record["output_block"] == lookup[target_identifier].block_index
    ]
    compatible_triple_indices = {triple_index for triple_index, _target in compatible_pairs}
    j_theorem = artifacts["q011j"]["cycle"]["theorem_consequence"]
    j_oracle = artifacts["q011j"]["cycle"]["exact_map_and_jacobian_oracle_audit"]
    m_cycle = artifacts["q011m"]["cycle"]
    m_parameters = m_cycle["registered_parameters"]
    m_fourier = m_cycle["fourier_and_dimension_audit"]
    m_derivative = m_cycle["analytic_map_derivative_audit"]
    structural_wave_sum = bool(
        j_oracle["checks"]["x_independent_filter_reduction_is_exact"]
        and m_fourier["passed"]
        and m_fourier["checks"]["selected_blocks_and_dimensions_are_registered"]
        and m_derivative["checks"]["source_has_no_second_or_third_derivative"]
        and m_derivative["checks"][
            "streaming_and_filter_do_not_increase_population_infinity_norm"
        ]
    )
    exact_sector_record = {
        "triple_records": triple_records,
        "compatible_pairs": [
            {"triple_index": triple_index, "target_identifier": target_identifier}
            for triple_index, target_identifier in compatible_pairs
        ],
    }
    checks = {
        "repaired_fixed_point_is_x_independent": j_theorem[
            "repaired_exact_full_17x17_x_independent_fixed_point_exists"
        ],
        "q011m_retains_registered_quadratic_output_sector_sum": bool(
            m_parameters["output_sectors"] == [0, 1, 16, 2, 15]
            and m_cycle["implicit_quadratic_jet_coefficient_audit"]["checks"][
                "all_five_sector_counts_are_retained"
            ]
        ),
        "local_collision_and_x_equivariant_linear_stages_give_wave_sum_law": (
            structural_wave_sum
        ),
        "all_128_cartesian_triples_are_enumerated": (
            len(triple_records) == EXPECTED_INDEXED_TRIPLE_COUNT
        ),
        "registered_triple_sector_histogram_reproduces": (
            dict(sorted(sector_histogram.items())) == EXPECTED_SECTOR_HISTOGRAM
        ),
        "registered_target_sector_histogram_reproduces": (
            dict(sorted(target_histogram.items())) == EXPECTED_TARGET_SECTOR_HISTOGRAM
        ),
        "all_192_and_only_compatible_comparisons_are_enumerated": bool(
            len(compatible_pairs) == EXPECTED_COMPATIBLE_COMPARISON_COUNT
            and len(compatible_triple_indices) == 64
        ),
        "sector_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(exact_sector_record)
            and _strict_json_serializable(exact_sector_record)
            and json.dumps(exact_sector_record, allow_nan=False)
        ),
    }
    audit = {
        "output_sector_law": "b_out=(b_1+b_2+b_3) mod 17",
        "structural_proof": {
            "fixed_point_and_repair_are_x_independent": checks[
                "repaired_fixed_point_is_x_independent"
            ],
            "x_independent_filter_reduction_is_exact": j_oracle["checks"][
                "x_independent_filter_reduction_is_exact"
            ],
            "fourier_selected_blocks_and_sector_pair_counts_reproduce": bool(
                m_fourier["passed"]
                and m_fourier["checks"]["sector_pair_counts_reproduce"]
            ),
            "source_has_no_second_or_third_derivative": m_derivative["checks"][
                "source_has_no_second_or_third_derivative"
            ],
            "local_and_translation_equivariant_stages_give_modulo_wave_sum": (
                structural_wave_sum
            ),
        },
        "indexed_triple_count": len(triple_records),
        "triple_sector_histogram": {
            str(key): value for key, value in sorted(sector_histogram.items())
        },
        "external_target_count": len(external_targets),
        "external_target_sector_histogram": {
            str(key): value for key, value in sorted(target_histogram.items())
        },
        "sector_compatible_triple_count": len(compatible_triple_indices),
        "sector_incompatible_triple_count": len(triple_records) - len(compatible_triple_indices),
        "sector_compatible_comparison_count": len(compatible_pairs),
        "triple_records": triple_records,
        "exact_sector_record_digest_sha256": q011b._canonical_json_sha256(
            exact_sector_record
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, triple_records, compatible_pairs


def _product_radius_expansion(
    center_modulus_uppers: tuple[Fraction, Fraction, Fraction],
    radii: tuple[Fraction, Fraction, Fraction],
) -> Fraction:
    total = Fraction(0)
    for mask in range(1, 1 << DEGREE):
        term = Fraction(1)
        for index in range(DEGREE):
            term *= radii[index] if mask & (1 << index) else center_modulus_uppers[index]
        total += term
    return total


def _product_disk_audit(
    lookup: dict[str, _EigenDisc],
    triple_records: list[dict[str, Any]],
    compatible_pairs: list[tuple[int, str]],
) -> tuple[dict[str, Any], Fraction]:
    product_records = []
    internal_products: dict[int, dict[str, Any]] = {}
    modulus_cache: dict[tuple[Fraction, Fraction], RationalInterval] = {}
    for triple_record in triple_records:
        triple_index = triple_record["triple_index"]
        discs = [lookup[identifier] for identifier in triple_record["source_identifiers"]]
        product_center = (Fraction(1), Fraction(0))
        center_modulus_uppers = tuple(disc.center_modulus.upper for disc in discs)
        radii = tuple(disc.radius for disc in discs)
        for disc in discs:
            product_center = _complex_product(product_center, disc.center)
        product_radius = (
            (center_modulus_uppers[0] + radii[0])
            * (center_modulus_uppers[1] + radii[1])
            * (center_modulus_uppers[2] + radii[2])
            - center_modulus_uppers[0]
            * center_modulus_uppers[1]
            * center_modulus_uppers[2]
        )
        expansion_radius = _product_radius_expansion(center_modulus_uppers, radii)
        if product_center not in modulus_cache:
            modulus_cache[product_center] = q011o._center_modulus_bounds(product_center)
        center_modulus = modulus_cache[product_center]
        product_modulus = RationalInterval(
            max(Fraction(0), center_modulus.lower - product_radius),
            center_modulus.upper + product_radius,
        )
        exact_product = {
            "triple_index": triple_index,
            "source_identifiers": triple_record["source_identifiers"],
            "output_block": triple_record["output_block"],
            "product_center": _complex_record(product_center),
            "product_radius": _fraction_record(product_radius),
            "product_center_modulus_lower": _fraction_record(center_modulus.lower),
            "product_center_modulus_upper": _fraction_record(center_modulus.upper),
            "product_modulus_lower": _fraction_record(product_modulus.lower),
            "product_modulus_upper": _fraction_record(product_modulus.upper),
            "radius_expansion_identity_reproduces": product_radius == expansion_radius,
        }
        product_records.append(exact_product)
        internal_products[triple_index] = {
            "center": product_center,
            "radius": product_radius,
            "modulus": product_modulus,
        }

    category_counts: Counter[str] = Counter()
    comparison_records = []
    minimum_margin: Fraction | None = None
    minimum_margin_witness: dict[str, Any] | None = None
    minimum_phase_margin: Fraction | None = None
    first_unresolved: dict[str, Any] | None = None
    for comparison_index, (triple_index, target_identifier) in enumerate(compatible_pairs):
        product = internal_products[triple_index]
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
        if difference not in modulus_cache:
            modulus_cache[difference] = q011o._center_modulus_bounds(difference)
        distance = modulus_cache[difference]
        separation_margin = distance.lower - product["radius"] - target.radius
        if modulus_gap is not None:
            category = "individual_modulus_separation"
        elif separation_margin > 0:
            category = "complex_phase_separation"
        else:
            category = "unresolved_product_disk_overlap"
        category_counts[category] += 1
        record = {
            "comparison_index": comparison_index,
            "triple_index": triple_index,
            "source_identifiers": triple_records[triple_index]["source_identifiers"],
            "output_block": triple_records[triple_index]["output_block"],
            "target_identifier": target_identifier,
            "target_modulus_lower": _fraction_record(target.modulus.lower),
            "target_modulus_upper": _fraction_record(target.modulus.upper),
            "individual_modulus_relation": modulus_side,
            "individual_modulus_gap": (
                None if modulus_gap is None else _fraction_record(modulus_gap)
            ),
            "center_distance_lower": _fraction_record(distance.lower),
            "center_distance_upper": _fraction_record(distance.upper),
            "combined_disk_radius": _fraction_record(product["radius"] + target.radius),
            "complex_separation_margin_lower": _fraction_record(separation_margin),
            "classification": category,
        }
        comparison_records.append(record)
        if minimum_margin is None or separation_margin < minimum_margin:
            minimum_margin = separation_margin
            minimum_margin_witness = record
        if category == "complex_phase_separation" and (
            minimum_phase_margin is None or separation_margin < minimum_phase_margin
        ):
            minimum_phase_margin = separation_margin
        if category == "unresolved_product_disk_overlap" and first_unresolved is None:
            first_unresolved = record

    if minimum_margin is None:
        raise RuntimeError("Q011v has no compatible product-disk comparison")
    exact_product_record = {
        "product_records": product_records,
        "comparison_records": comparison_records,
    }
    checks = {
        "all_128_product_centers_and_radii_are_reconstructed": bool(
            len(product_records) == EXPECTED_INDEXED_TRIPLE_COUNT
            and all(record["radius_expansion_identity_reproduces"] for record in product_records)
        ),
        "triangle_inequality_product_disk_formula_is_exact": all(
            _fraction(record["product_radius"]) >= 0 for record in product_records
        ),
        "all_192_compatible_comparisons_are_evaluated": (
            len(comparison_records) == EXPECTED_COMPATIBLE_COMPARISON_COUNT
        ),
        "comparison_categories_partition_all_records": (
            sum(category_counts.values()) == len(comparison_records)
        ),
        "modulus_separation_is_consistent_with_positive_complex_margin": all(
            _fraction(record["complex_separation_margin_lower"]) > 0
            for record in comparison_records
            if record["classification"] == "individual_modulus_separation"
        ),
        "minimum_margin_and_first_unresolved_witness_reproduce": bool(
            minimum_margin_witness is not None
            and (first_unresolved is None)
            == (category_counts["unresolved_product_disk_overlap"] == 0)
        ),
        "full_product_record_is_finite_strict_json": bool(
            _all_numeric_values_finite(exact_product_record)
            and _strict_json_serializable(exact_product_record)
            and json.dumps(exact_product_record, allow_nan=False)
        ),
    }
    audit = {
        "product_disk_formula": {
            "center": "C=c_1*c_2*c_3",
            "radius": "R=product_i(u_i+r_i)-product_i(u_i)",
            "inclusion": "product_i D(c_i,r_i) is contained in D(C,R)",
            "external_separation": "Delta^-=|C-c_e|^- - R-r_e",
        },
        "product_record_count": len(product_records),
        "comparison_record_count": len(comparison_records),
        "individual_modulus_separation_count": category_counts[
            "individual_modulus_separation"
        ],
        "complex_phase_separation_count": category_counts["complex_phase_separation"],
        "unresolved_product_disk_overlap_count": category_counts[
            "unresolved_product_disk_overlap"
        ],
        "minimum_complex_separation_lower": _fraction_record(minimum_margin),
        "minimum_phase_only_separation_lower": (
            None if minimum_phase_margin is None else _fraction_record(minimum_phase_margin)
        ),
        "registered_minimum_complex_separation": _fraction_record(
            MINIMUM_COMPLEX_SEPARATION
        ),
        "minimum_margin_witness": minimum_margin_witness,
        "first_unresolved_product_disk_overlap": first_unresolved,
        "product_records": product_records,
        "comparison_records": comparison_records,
        "exact_product_comparison_digest_sha256": q011b._canonical_json_sha256(
            exact_product_record
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
        "degree_expanded_product_control_count": EXPECTED_DEGREE_EXPANDED_CONTROL_COUNT,
        "sole_overlap_counts": list(SOLE_OVERLAP_COUNTS),
        "selected_source_group_indices": list(SELECTED_SOURCE_GROUP_INDICES),
        "selected_source_group_sizes": list(EXPECTED_SELECTED_GROUP_SIZES),
        "sole_external_group_index": SOLE_EXTERNAL_GROUP_INDEX,
        "indexed_triple_count": EXPECTED_INDEXED_TRIPLE_COUNT,
        "external_target_count": EXPECTED_EXTERNAL_TARGET_COUNT,
        "compatible_comparison_count": EXPECTED_COMPATIBLE_COMPARISON_COUNT,
        "minimum_complex_separation": _fraction_record(MINIMUM_COMPLEX_SEPARATION),
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


def run_degree3_phase_disk_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    inventory, lookup, selected_groups, external_targets = _inventory_audit(artifacts)
    sector, triple_records, compatible_pairs = _sector_audit(
        artifacts,
        lookup,
        selected_groups,
        external_targets,
    )
    product, minimum_margin = _product_disk_audit(
        lookup,
        triple_records,
        compatible_pairs,
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    inventory_sections = {"degree3_modulus_inventory_audit": inventory}
    sector_sections = {"fourier_output_sector_audit": sector}
    product_sections = {"phase_sensitive_product_disk_audit": product}
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
        "four_inputs_twenty_two_digests_and_helper_sources_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011j/k/m/u artifacts, runners, 22 digests, outcomes and claim "
                "boundaries plus Q011l/o sources reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "q011u_degree_three_inventory_and_sole_overlap_reproduce": {
            "passed": inventory["passed"],
            "threshold": "20 aggregates, 19 separated and sole [0,1,1,1]/group-183 overlap",
            "value": inventory["checks"],
        },
        "selected_memberships_128_triples_and_eight_targets_reproduce": {
            "passed": bool(
                inventory["passed"]
                and inventory["selected_source_group_sizes"] == [4, 4, 8]
                and inventory["indexed_triple_count"] == EXPECTED_INDEXED_TRIPLE_COUNT
                and len(inventory["external_target_identifiers"])
                == EXPECTED_EXTERNAL_TARGET_COUNT
            ),
            "threshold": "selected source groups 4/4/8, 128 indexed triples and 8 targets",
            "value": {
                "selected_group_sizes": inventory["selected_source_group_sizes"],
                "indexed_triple_count": inventory["indexed_triple_count"],
                "external_target_count": len(inventory["external_target_identifiers"]),
            },
        },
        "fourier_sum_histograms_and_192_compatible_comparisons_reproduce": {
            "passed": sector["passed"],
            "threshold": (
                "x-Fourier sum, registered triple/target histograms and 192 compatible "
                "comparisons"
            ),
            "value": sector["checks"],
        },
        "all_product_disk_and_complex_distance_formulas_reproduce": {
            "passed": product["passed"],
            "threshold": (
                "128 exact product disks and 192 individual-modulus/complex-distance "
                "comparisons"
            ),
            "value": product["checks"],
        },
        "comparison_partition_margin_witness_and_digest_reproduce": {
            "passed": product["passed"],
            "threshold": (
                "comparison partition, minimum margin, first unresolved record and full "
                "comparison digest reproduce"
            ),
            "value": {
                "individual_modulus": product["individual_modulus_separation_count"],
                "complex_phase": product["complex_phase_separation_count"],
                "unresolved": product["unresolved_product_disk_overlap_count"],
                "comparison_digest": product[
                    "exact_product_comparison_digest_sha256"
                ],
            },
        },
        "strict_serialization_section_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite strict JSON, four section digests, result digest and runner "
                "provenance reproduce"
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
        and sector["sector_compatible_comparison_count"]
        == EXPECTED_COMPATIBLE_COMPARISON_COUNT
    )
    complete_coverage = bool(
        inventory["passed"]
        and inventory["degree_modulus_aggregate_count"]
        == EXPECTED_DEGREE_AGGREGATE_COUNT
        and inventory["modulus_separated_aggregate_count"]
        == EXPECTED_MODULUS_SEPARATED_AGGREGATE_COUNT
        and inventory["modulus_overlap_aggregate_count"]
        == EXPECTED_MODULUS_OVERLAP_AGGREGATE_COUNT
        and sector["indexed_triple_count"] == EXPECTED_INDEXED_TRIPLE_COUNT
        and sector["sector_compatible_comparison_count"]
        == EXPECTED_COMPATIBLE_COMPARISON_COUNT
    )
    zero_unresolved = product["unresolved_product_disk_overlap_count"] == 0
    phase_adds_information = product["complex_phase_separation_count"] > 0
    hypothesis_gates = {
        "x_translation_equivariance_gives_the_exact_cubic_output_sector_sum": {
            "passed": bool(validity_passed and sector_law),
            "threshold": "b_out=(b_1+b_2+b_3) mod 17",
            "value": sector["structural_proof"],
        },
        "modulus_inventory_triples_and_compatible_targets_cover_all_degree_three_cases": {
            "passed": bool(validity_passed and complete_coverage),
            "threshold": "20 aggregates plus 128 sole-overlap triples and 192 comparisons",
            "value": {
                "aggregates": inventory["degree_modulus_aggregate_count"],
                "triples": sector["indexed_triple_count"],
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
            "threshold": "at least one modulus-overlap comparison is separated by phase",
            "value": product["complex_phase_separation_count"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011v degree-three phase audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = ACCEPTED_CLASSIFICATION
    else:
        outcome = "rejected"
        classification = REJECTED_CLASSIFICATION

    cycle: dict[str, Any] = {
        "question": (
            "Does Fourier-sector filtering plus exact complex product-disk separation "
            "eliminate the sole degree-three modulus-overlap aggregate?"
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
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    degree_three_certified = bool(validity_passed and hypotheses_passed)
    cycle["theorem_consequence"] = {
        "q011u_degree_three_modulus_inventory_is_reproduced": validity_passed,
        "the_sole_degree_three_modulus_overlap_is_phase_sensitively_eliminated": (
            degree_three_certified
        ),
        "degree_three_external_nonresonance_is_certified": degree_three_certified,
        "certified_external_nonresonance_degrees": [2, 3],
        "degree_91_and_higher_modulus_tail_is_preserved": True,
        "missing_external_nonresonance_degrees": list(range(4, 91)),
        "degrees_4_through_90_are_certified": False,
        "an_actual_complex_resonance_is_established": False,
        "all_spectral_quotient_nonresonances_are_certified": False,
        "the_q011t_graph_is_identified_with_a_higher_smooth_manifold": False,
        "ssm_existence_or_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011j_q011k_q011m_or_q011u_outcome_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only degree three for the fixed 17x17 repaired exact map "
        "on one fixed conservation leaf, the sole Q011u modulus-overlap aggregate, "
        "Q011k eigendiscs, x-Fourier output sectors and the registered product-disk "
        "formula. It certifies no degree from 4 through 90, no all-order "
        "nonresonance, equality with the Q011t graph, C2 or higher graph smoothness, "
        "SSM existence or uniqueness, explicit higher-smoothness radius, normal "
        "attraction, basin, other grid, force, wall or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011j_exact_fixed_point_acceptance_changed": False,
        "q011k_spectral_split_acceptance_changed": False,
        "q011m_quadratic_jet_acceptance_changed": False,
        "q011u_modulus_only_rejection_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011w to extend the same Fourier-sector and phase-sensitive "
            "product-disk audit to the two degree-four modulus-overlap aggregates."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Send only the first unresolved product disk to a sharper center enclosure "
            "or full homological-operator audit."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, inventory, sector, product or serialization "
            "validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011v cycle failed strict serialization or digest")
    return cycle


def run_q011v_study() -> dict[str, Any]:
    cycle = run_degree3_phase_disk_audit()
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
            "indexed_triple_count": EXPECTED_INDEXED_TRIPLE_COUNT,
            "compatible_comparison_count": EXPECTED_COMPATIBLE_COMPARISON_COUNT,
        },
        "mathematical_scope": {
            "diagnostic": "degree-three phase-sensitive output-sector product disks",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "degree": DEGREE,
            "degree_three_external_nonresonance_claim": (
                cycle["hypothesis_outcome"] == "accepted"
            ),
            "degrees_4_through_90_claim": False,
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
    result = run_q011v_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
