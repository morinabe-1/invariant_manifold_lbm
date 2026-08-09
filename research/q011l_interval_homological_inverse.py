"""Q011l rigorous invariant-graph and quadratic homological inverse proof."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011k_interval_spectral_split as q011k
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

ExactComplex = tuple[Fraction, Fraction]

SIZE = 17
SELECTED_BLOCKS = (0, 1, 16)
OUTPUT_SECTORS = (0, 1, 16, 2, 15)
SELECTED_DIMENSIONS = {0: 6, 1: 9, 16: 9}
EXTERNAL_DIMENSIONS = {0: 144, 1: 144, 16: 144, 2: 153, 15: 153}
EXPECTED_SECTOR_PAIR_COUNTS = {0: 102, 1: 54, 16: 54, 2: 45, 15: 45}
EXPECTED_SELECTED_COUNT = 24
EXPECTED_PAIR_COUNT = 300
EXPECTED_EXTERNAL_COMPARISON_COUNT = 44_010
EXPECTED_UNSAFE_PAIR_INDICES = (11, 19, 33, 43, 56, 64, 76, 86)

MAXIMUM_GRAPH_RADIUS = Fraction(1, 10**4)
MAXIMUM_GRAPH_UTILIZATION = Fraction(9, 10)
MAXIMUM_GRAPH_CONTRACTION = Fraction(9, 10)
MINIMUM_BASE_HOMOLOGICAL_DISTANCE = Fraction(1, 10**5)
MAXIMUM_NEUMANN_QUOTIENT = Fraction(1, 10)
MAXIMUM_COORDINATE_INVERSE_BOUND = Fraction(10**5)
MAXIMUM_AMBIENT_INVERSE_BOUND = Fraction(10**7)

Q011K_ARTIFACT_SHA256 = "8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a"
Q011K_RUNNER_SHA256 = "d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07"
Q011K_DIGESTS = (
    "f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2",
    "f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc",
    "7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8",
    "1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4",
    "2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e",
)
Q011K_CLASSIFICATION = (
    "the exact repaired fixed point has a rigorously stable and quadratically "
    "nonresonant selected/external spectral split"
)
Q011D_ARTIFACT_SHA256 = "c3acb9b7acc6e3121cb6e48a04bb060b5c95d7b128fe15fb11b67ee456337fd0"
Q011D_RUNNER_SHA256 = "815fe7e0101cc05cc44fcb224534762f0ef7625f8c9604ff0a822c13171a617d"
Q011D_DIGESTS = (
    "ee2713e8169ea0f475ddee1b1233964ba40739d2276b78db3fff5410158dd2f8",
    "7208875ff95f3a768e4b822cf9be854228d6664800dfc69218c0e6a030a0c63e",
    "f9caee5b591e74b40b497ca7eb8244f1bbaeba71d239684c47d8215c46c2fb0b",
    "feb864e2725e0cf726b43c443bb48b53f34ba0ac54693bb97a2b986f598a1414",
    "a6941371e54a5e4d4abbea2f835196ddd7cce35c7c266ce399020764ed5b9dd7",
)
Q011D_CLASSIFICATION = (
    "the forced quadratic external homological family is numerically "
    "nonresonant and solvable"
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


def _fraction(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _exact_float(value: float) -> Fraction:
    return Fraction.from_float(float(value))


def _exact_complex(record: dict[str, Any], *, conjugate: bool = False) -> ExactComplex:
    imaginary = _exact_float(record["imag"])
    return (_exact_float(record["real"]), -imaginary if conjugate else imaginary)


def _complex_product(left: ExactComplex, right: ExactComplex) -> ExactComplex:
    ar, ai = left
    br, bi = right
    return (ar * br - ai * bi, ar * bi + ai * br)


def _component_distance(left: ExactComplex, right: ExactComplex) -> Fraction:
    return max(abs(left[0] - right[0]), abs(left[1] - right[1]))


def _complex_l1(value: ExactComplex) -> Fraction:
    return abs(value[0]) + abs(value[1])


def _exact_complex_record(value: ExactComplex) -> dict[str, Any]:
    return {"real": _fraction_record(value[0]), "imag": _fraction_record(value[1])}


def _sealed_input_audit() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    directory = _artifact_directory()
    q011k_path = directory / "q011k_interval_spectral_split.json"
    q011d_path = directory / "q011d_forced_quadratic_homological.json"
    q011k_runner = Path(q011k.__file__).resolve()
    q011d_runner = Path(__file__).resolve().parent / "q011d_forced_quadratic_homological.py"
    q011k_artifact = json.loads(q011k_path.read_text(encoding="utf-8"))
    q011d_artifact = json.loads(q011d_path.read_text(encoding="utf-8"))
    k_cycle = q011k_artifact["cycle"]
    d_cycle = q011d_artifact["cycle"]
    k_digests = tuple(
        k_cycle[name]
        for name in (
            "input_digest_sha256",
            "root_digest_sha256",
            "block_digest_sha256",
            "proof_digest_sha256",
            "result_digest_sha256",
        )
    )
    d_digests = tuple(
        d_cycle[name]
        for name in (
            "input_digest_sha256",
            "linear_split_digest_sha256",
            "pair_family_digest_sha256",
            "sector_probe_digest_sha256",
            "result_digest_sha256",
        )
    )
    k_theorem = k_cycle["theorem_consequence"]
    d_parameters = d_cycle["registered_parameters"]
    d_blocks = d_cycle["external_homological_block_audit"]
    checks = {
        "q011k_artifact_sha256_matches": _file_sha256(q011k_path) == Q011K_ARTIFACT_SHA256,
        "q011k_runner_sha256_matches": _file_sha256(q011k_runner) == Q011K_RUNNER_SHA256,
        "q011k_digests_match": k_digests == Q011K_DIGESTS,
        "q011k_accepted_outcome_reproduces": (
            k_cycle["study_validity"] == "passed"
            and k_cycle["hypothesis_outcome"] == "accepted"
            and k_cycle["scientific_classification"] == Q011K_CLASSIFICATION
            and all(gate["passed"] for gate in k_cycle["validity_gates"].values())
            and all(gate["passed"] for gate in k_cycle["hypothesis_gates"].values())
        ),
        "q011k_claim_boundary_is_preserved": (
            k_theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
            and not k_theorem["nonnormal_homological_inverse_is_certified"]
            and not k_theorem["forced_ssm_exists_or_is_unique"]
            and not k_theorem["nonlinear_normal_attraction_is_certified"]
        ),
        "q011d_artifact_sha256_matches": _file_sha256(q011d_path) == Q011D_ARTIFACT_SHA256,
        "q011d_runner_sha256_matches": _file_sha256(q011d_runner) == Q011D_RUNNER_SHA256,
        "q011d_digests_match": d_digests == Q011D_DIGESTS,
        "q011d_accepted_outcome_reproduces": (
            d_cycle["study_validity"] == "passed"
            and d_cycle["hypothesis_outcome"] == "accepted"
            and d_cycle["scientific_classification"] == Q011D_CLASSIFICATION
        ),
        "q011d_pair_and_sector_calibration_reproduces": (
            d_parameters["expected_pair_count"] == EXPECTED_PAIR_COUNT
            and d_parameters["expected_sector_pair_counts"]
            == {str(key): value for key, value in EXPECTED_SECTOR_PAIR_COUNTS.items()}
            and d_parameters["external_sector_dimensions"]
            == {str(key): value for key, value in EXTERNAL_DIMENSIONS.items()}
            and d_blocks["block_count"] == EXPECTED_PAIR_COUNT
            and d_blocks["numerically_singular_block_count"] == 0
        ),
        "package_source_metadata_matches": (
            q011k_artifact["source"] == source_metadata()
            and q011d_artifact["source"] == source_metadata()
        ),
    }
    audit = {
        "q011k": {
            "artifact_filename": q011k_path.name,
            "artifact_sha256": _file_sha256(q011k_path),
            "runner_filename": q011k_runner.name,
            "runner_sha256": _file_sha256(q011k_runner),
            "digests": list(k_digests),
            "study_validity": k_cycle["study_validity"],
            "hypothesis_outcome": k_cycle["hypothesis_outcome"],
            "scientific_classification": k_cycle["scientific_classification"],
        },
        "q011d": {
            "artifact_filename": q011d_path.name,
            "artifact_sha256": _file_sha256(q011d_path),
            "runner_filename": q011d_runner.name,
            "runner_sha256": _file_sha256(q011d_runner),
            "digests": list(d_digests),
            "study_validity": d_cycle["study_validity"],
            "hypothesis_outcome": d_cycle["hypothesis_outcome"],
            "scientific_classification": d_cycle["scientific_classification"],
            "numerical_minimum_singular_value": d_blocks["minimum_operator_singular_value"],
            "numerical_maximum_condition_number": d_blocks["maximum_operator_condition_number"],
        },
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, q011k_artifact, q011d_artifact


def _spectral_data(
    q011k_artifact: dict[str, Any],
) -> tuple[
    dict[int, list[ExactComplex]],
    dict[int, tuple[int, ...]],
    dict[int, Fraction],
    dict[int, dict[str, Fraction]],
    dict[str, Any],
]:
    cycle = q011k_artifact["cycle"]
    proof_records = {
        int(record["block_index"]): record
        for record in cycle["dual_precision_bauer_fike_audit"][
            "representative_block_records"
        ]
    }
    centers: dict[int, list[ExactComplex]] = {}
    radii: dict[int, Fraction] = {}
    metrics: dict[int, dict[str, Fraction]] = {}
    for block_index in range(SIZE):
        representative = block_index if block_index <= 8 else SIZE - block_index
        record = proof_records[representative]
        conjugate = block_index > 8
        centers[block_index] = [
            _exact_complex(value, conjugate=conjugate)
            for value in record["eigenvalue_centers"]
        ]
        primary = record["primary_precision_proof"]
        beta = _fraction(primary["certified_inverse_infinity_norm_upper"])
        residual = _fraction(primary["family_eigendecomposition_residual_infinity_upper"])
        metrics[block_index] = {
            "beta": beta,
            "family_residual": residual,
            "theta": beta * residual,
            "vector_norm": _fraction(primary["vector_infinity_norm_upper"]),
        }
        radii[block_index] = _fraction(primary["bauer_fike_radius_upper"])
    selected = {
        int(record["block_index"]): tuple(int(index) for index in record["selected_center_indices"])
        for record in cycle["selected_external_split_audit"]["matching_records"]
    }
    exact_records = []
    for block_index in range(SIZE):
        exact_records.append(
            {
                "block_index": block_index,
                "representative_block": block_index if block_index <= 8 else SIZE - block_index,
                "conjugated": block_index > 8,
                "dimension": len(centers[block_index]),
                "center_digest_sha256": q011b._canonical_json_sha256(
                    [_exact_complex_record(value) for value in centers[block_index]]
                ),
                "bauer_fike_radius_upper": _fraction_record(radii[block_index]),
                "beta_upper": _fraction_record(metrics[block_index]["beta"]),
                "family_residual_upper": _fraction_record(
                    metrics[block_index]["family_residual"]
                ),
                "transformed_perturbation_upper": _fraction_record(
                    metrics[block_index]["theta"]
                ),
            }
        )
    checks = {
        "all_seventeen_blocks_are_reconstructed": (
            sorted(centers) == list(range(SIZE))
            and len(centers[0]) == 150
            and all(len(centers[index]) == 153 for index in range(1, SIZE))
        ),
        "selected_dimensions_are_registered": (
            {index: len(value) for index, value in selected.items()} == SELECTED_DIMENSIONS
        ),
        "all_exact_upper_bounds_are_positive": all(
            metrics[index][name] > 0
            for index in range(SIZE)
            for name in ("beta", "family_residual", "theta", "vector_norm")
        ),
        "conjugate_centers_and_bounds_transport_exactly": all(
            centers[index]
            == [(real, -imaginary) for real, imaginary in centers[SIZE - index]]
            and radii[index] == radii[SIZE - index]
            and metrics[index] == metrics[SIZE - index]
            for index in range(9, SIZE)
        ),
    }
    audit = {
        "block_count": len(centers),
        "selected_block_dimensions": {
            str(key): len(value) for key, value in selected.items()
        },
        "transformed_coordinate_identity": (
            "M=V^{-1}AV=Lambda+F with ||F||_inf <= beta*||AV-VLambda||_inf"
        ),
        "block_records": exact_records,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return centers, selected, radii, metrics, audit


def _graph_audit(
    centers: dict[int, list[ExactComplex]],
    selected: dict[int, tuple[int, ...]],
    metrics: dict[int, dict[str, Fraction]],
) -> tuple[dict[int, dict[str, Fraction]], dict[str, Any]]:
    exact: dict[int, dict[str, Fraction]] = {}
    records = []
    for block_index in SELECTED_BLOCKS:
        selected_indices = selected[block_index]
        selected_set = frozenset(selected_indices)
        external_indices = tuple(
            index for index in range(len(centers[block_index])) if index not in selected_set
        )
        gap: Fraction | None = None
        witness: dict[str, int] | None = None
        for external_index in external_indices:
            for selected_index in selected_indices:
                distance = _component_distance(
                    centers[block_index][external_index],
                    centers[block_index][selected_index],
                )
                if gap is None or distance < gap:
                    gap = distance
                    witness = {
                        "external_center_index": external_index,
                        "selected_center_index": selected_index,
                    }
        if gap is None or witness is None or gap <= 0:
            raise RuntimeError(f"block {block_index} has no positive graph gap")
        theta = metrics[block_index]["theta"]
        h_value = theta / gap
        radius = 2 * h_value
        self_map_bound = h_value * (1 + 2 * radius + radius * radius)
        self_map_utilization = self_map_bound / radius
        contraction = h_value * (2 + 2 * radius)
        eta = theta * (1 + radius)
        identification_margin = gap - 2 * eta
        exact[block_index] = {
            "gap": gap,
            "theta": theta,
            "h": h_value,
            "radius": radius,
            "self_map_bound": self_map_bound,
            "self_map_utilization": self_map_utilization,
            "contraction": contraction,
            "eta": eta,
            "identification_margin": identification_margin,
        }
        checks = {
            "selected_and_external_counts_match": (
                len(selected_indices) == SELECTED_DIMENSIONS[block_index]
                and len(external_indices) == EXTERNAL_DIMENSIONS[block_index]
            ),
            "gap_is_strictly_positive": gap > 0,
            "registered_radius_formula_reproduces": radius == 2 * theta / gap,
            "riccati_ball_is_a_self_map": self_map_bound <= radius,
            "riccati_map_is_a_strict_contraction": contraction < 1,
            "quotient_perturbation_formula_reproduces": eta == theta * (1 + radius),
            "graph_spectra_remain_in_the_registered_center_split": (
                identification_margin > 0
            ),
        }
        records.append(
            {
                "block_index": block_index,
                "selected_dimension": len(selected_indices),
                "external_dimension": len(external_indices),
                "minimum_diagonal_component_gap": _fraction_record(gap),
                "minimum_gap_witness": witness,
                "transformed_perturbation_upper": _fraction_record(theta),
                "sylvester_base_inverse_upper": _fraction_record(1 / gap),
                "h_upper": _fraction_record(h_value),
                "graph_radius_upper": _fraction_record(radius),
                "self_map_bound_upper": _fraction_record(self_map_bound),
                "self_map_utilization_upper": _fraction_record(self_map_utilization),
                "contraction_upper": _fraction_record(contraction),
                "selected_and_external_perturbation_upper": _fraction_record(eta),
                "selected_external_identification_margin_lower": _fraction_record(
                    identification_margin
                ),
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    maximum_radius_record = max(
        records, key=lambda record: _fraction(record["graph_radius_upper"])
    )
    maximum_utilization_record = max(
        records, key=lambda record: _fraction(record["self_map_utilization_upper"])
    )
    maximum_contraction_record = max(
        records, key=lambda record: _fraction(record["contraction_upper"])
    )
    checks = {
        "all_three_selected_blocks_are_complete": (
            [record["block_index"] for record in records] == list(SELECTED_BLOCKS)
        ),
        "all_riccati_certificates_pass": all(record["passed"] for record in records),
        "all_graph_values_are_finite": _all_numeric_values_finite(records),
    }
    audit = {
        "graph_blocks": list(SELECTED_BLOCKS),
        "graph_norm": "matrix infinity norm (maximum external-row absolute sum)",
        "graph_radius_formula": "r_G = 2 theta / g",
        "riccati_self_map_formula": "h * (1 + 2 r_G + r_G^2)",
        "riccati_contraction_formula": "h * (2 + 2 r_G)",
        "block_records": records,
        "maximum_graph_radius_upper": maximum_radius_record["graph_radius_upper"],
        "maximum_graph_radius_block": maximum_radius_record["block_index"],
        "maximum_self_map_utilization_upper": maximum_utilization_record[
            "self_map_utilization_upper"
        ],
        "maximum_self_map_utilization_block": maximum_utilization_record["block_index"],
        "maximum_contraction_upper": maximum_contraction_record["contraction_upper"],
        "maximum_contraction_block": maximum_contraction_record["block_index"],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return exact, audit


def _selected_entries(
    centers: dict[int, list[ExactComplex]],
    selected: dict[int, tuple[int, ...]],
) -> list[tuple[int, int, ExactComplex]]:
    return [
        (block_index, center_index, centers[block_index][center_index])
        for block_index in sorted(selected)
        for center_index in selected[block_index]
    ]


def _pair_and_full_space_audit(
    centers: dict[int, list[ExactComplex]],
    selected: dict[int, tuple[int, ...]],
    radii: dict[int, Fraction],
    q011k_artifact: dict[str, Any],
) -> tuple[dict[int, list[dict[str, Any]]], dict[str, Any], dict[str, Any]]:
    selected_entries = _selected_entries(centers, selected)
    pairs_by_sector: dict[int, list[dict[str, Any]]] = {sector: [] for sector in OUTPUT_SECTORS}
    exact_pair_records = []
    compact_pair_records = []
    unsafe_records = []
    external_comparison_count = 0
    stored_pairs = q011k_artifact["cycle"]["quadratic_spectral_nonresonance_audit"][
        "pair_records"
    ]
    pair_index = 0
    for left_position, (left_block, left_index, left_center) in enumerate(selected_entries):
        for right_block, right_index, right_center in selected_entries[left_position:]:
            output = (left_block + right_block) % SIZE
            product = _complex_product(left_center, right_center)
            selected_output = frozenset(selected.get(output, ()))
            external_indices = tuple(
                index for index in range(len(centers[output])) if index not in selected_output
            )
            minimum: Fraction | None = None
            witness = -1
            for external_index in external_indices:
                distance = _component_distance(product, centers[output][external_index])
                external_comparison_count += 1
                if minimum is None or distance < minimum:
                    minimum = distance
                    witness = external_index
            if minimum is None:
                raise RuntimeError("quadratic sector has no external center")
            stored = stored_pairs[pair_index]
            ordering_matches = (
                stored["pair_index"] == pair_index
                and stored["left"]
                == {"block_index": left_block, "center_index": left_index}
                and stored["right"]
                == {"block_index": right_block, "center_index": right_index}
                and stored["output_block_index"] == output
            )
            record = {
                "pair_index": pair_index,
                "left": {"block_index": left_block, "center_index": left_index},
                "right": {"block_index": right_block, "center_index": right_index},
                "output_sector": output,
                "product": product,
                "minimum_base_external_distance": minimum,
                "minimum_external_center_index": witness,
                "external_comparison_count": len(external_indices),
                "q011k_ordering_matches": ordering_matches,
            }
            pairs_by_sector[output].append(record)
            exact_pair_records.append(
                {
                    "pair_index": pair_index,
                    "left": record["left"],
                    "right": record["right"],
                    "output_sector": output,
                    "product_center": _exact_complex_record(product),
                    "minimum_base_external_distance": _fraction_record(minimum),
                    "minimum_external_center_index": witness,
                    "external_comparison_count": len(external_indices),
                }
            )
            compact_pair_records.append(
                {
                    "pair_index": pair_index,
                    "left": record["left"],
                    "right": record["right"],
                    "output_sector": output,
                    "product_center": {"real": float(product[0]), "imag": float(product[1])},
                    "minimum_base_external_distance": float(minimum),
                    "minimum_external_center_index": witness,
                    "external_comparison_count": len(external_indices),
                    "q011k_ordering_matches": ordering_matches,
                }
            )

            if selected_output:
                left_modulus = q011k._center_modulus_bounds(
                    complex(float(left_center[0]), float(left_center[1]))
                ).upper
                right_modulus = q011k._center_modulus_bounds(
                    complex(float(right_center[0]), float(right_center[1]))
                ).upper
                product_radius = (
                    left_modulus * radii[right_block]
                    + right_modulus * radii[left_block]
                    + radii[left_block] * radii[right_block]
                )
                selected_margin: Fraction | None = None
                selected_witness = -1
                for selected_index in sorted(selected_output):
                    margin = (
                        _component_distance(product, centers[output][selected_index])
                        - product_radius
                        - radii[output]
                    )
                    if selected_margin is None or margin < selected_margin:
                        selected_margin = margin
                        selected_witness = selected_index
                if selected_margin is not None and selected_margin <= 0:
                    unsafe_records.append(
                        {
                            "pair_index": pair_index,
                            "output_sector": output,
                            "selected_center_index": selected_witness,
                            "selected_disc_margin_upper_test": _fraction_record(selected_margin),
                            "product_disc_radius_upper": _fraction_record(product_radius),
                        }
                    )
            pair_index += 1

    numpy_centers = {
        block: np.asarray(
            [complex(float(real), float(imaginary)) for real, imaginary in values],
            dtype=np.complex128,
        )
        for block, values in centers.items()
    }
    reproduced_q011k = q011k._quadratic_nonresonance_audit(
        numpy_centers,
        radii,
        selected,
    )
    source_quadratic = q011k_artifact["cycle"]["quadratic_spectral_nonresonance_audit"]
    pair_checks = {
        "selected_count_is_twenty_four": len(selected_entries) == EXPECTED_SELECTED_COUNT,
        "all_three_hundred_pairs_are_complete": pair_index == EXPECTED_PAIR_COUNT,
        "all_q011k_pair_ordering_matches": all(
            record["q011k_ordering_matches"] for record in compact_pair_records
        ),
        "sector_pair_counts_are_registered": (
            {sector: len(records) for sector, records in pairs_by_sector.items()}
            == EXPECTED_SECTOR_PAIR_COUNTS
        ),
        "external_comparison_count_is_registered": (
            external_comparison_count == EXPECTED_EXTERNAL_COMPARISON_COUNT
        ),
        "q011k_exact_pair_digest_reproduces": (
            reproduced_q011k["exact_pair_digest_sha256"]
            == source_quadratic["exact_pair_digest_sha256"]
        ),
    }
    pair_audit = {
        "selected_count": len(selected_entries),
        "unordered_pair_count": pair_index,
        "sector_pair_counts": {
            str(sector): len(records) for sector, records in pairs_by_sector.items()
        },
        "external_comparison_count": external_comparison_count,
        "pair_records": compact_pair_records,
        "exact_base_pair_digest_sha256": q011b._canonical_json_sha256(exact_pair_records),
        "reproduced_q011k_exact_pair_digest_sha256": reproduced_q011k[
            "exact_pair_digest_sha256"
        ],
        "checks": pair_checks,
        "passed": all(pair_checks.values()),
    }
    unsafe_indices = tuple(record["pair_index"] for record in unsafe_records)
    unsafe_checks = {
        "all_pairs_were_audited": pair_index == EXPECTED_PAIR_COUNT,
        "unsafe_pair_count_is_registered": len(unsafe_records) == len(EXPECTED_UNSAFE_PAIR_INDICES),
        "unsafe_pair_indices_are_registered": unsafe_indices == EXPECTED_UNSAFE_PAIR_INDICES,
        "every_registered_unsafe_margin_is_nonpositive": all(
            _fraction(record["selected_disc_margin_upper_test"]) <= 0
            for record in unsafe_records
        ),
    }
    unsafe_audit = {
        "interpretation": (
            "These products cannot be certified by a full-space resolvent because their "
            "Q011k product discs overlap selected output discs; none is removed from the "
            "external-quotient proof."
        ),
        "unsafe_pair_count": len(unsafe_records),
        "unsafe_pair_indices": list(unsafe_indices),
        "unsafe_pair_records": unsafe_records,
        "checks": unsafe_checks,
        "passed": all(unsafe_checks.values()),
    }
    return pairs_by_sector, pair_audit, unsafe_audit


def _homological_audit(
    centers: dict[int, list[ExactComplex]],
    selected: dict[int, tuple[int, ...]],
    metrics: dict[int, dict[str, Fraction]],
    graphs: dict[int, dict[str, Fraction]],
    pairs_by_sector: dict[int, list[dict[str, Any]]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    selected_entries = _selected_entries(centers, selected)
    selected_center_l1_upper = max(_complex_l1(value) for _, _, value in selected_entries)
    selected_perturbation_upper = max(graphs[index]["eta"] for index in SELECTED_BLOCKS)
    pair_action_perturbation = (
        2 * selected_center_l1_upper * selected_perturbation_upper
        + selected_perturbation_upper * selected_perturbation_upper
    )
    symmetric_checks = {
        "selected_count_is_registered": len(selected_entries) == EXPECTED_SELECTED_COUNT,
        "selected_perturbation_is_graph_derived": (
            selected_perturbation_upper == max(graphs[index]["eta"] for index in SELECTED_BLOCKS)
        ),
        "unscaled_symmetric_product_bound_is_exact": (
            pair_action_perturbation
            == 2 * selected_center_l1_upper * selected_perturbation_upper
            + selected_perturbation_upper**2
        ),
    }
    symmetric_audit = {
        "basis": "unscaled lexicographic monomials a_i a_j for i <= j",
        "selected_dimension": len(selected_entries),
        "symmetric_dimension": EXPECTED_PAIR_COUNT,
        "selected_center_complex_l1_upper": _fraction_record(selected_center_l1_upper),
        "selected_dynamics_perturbation_upper": _fraction_record(
            selected_perturbation_upper
        ),
        "symmetric_product_action_perturbation_upper": _fraction_record(
            pair_action_perturbation
        ),
        "bound_formula": "kappa = 2 L eta_S + eta_S^2",
        "checks": symmetric_checks,
        "passed": all(symmetric_checks.values()),
    }

    sector_records = []
    exact_sector_records = []
    for sector in OUTPUT_SECTORS:
        pairs = pairs_by_sector[sector]
        minimum_record = min(
            pairs,
            key=lambda record: record["minimum_base_external_distance"],
        )
        base_distance = minimum_record["minimum_base_external_distance"]
        if sector in graphs:
            external_perturbation = graphs[sector]["eta"]
            graph_radius = graphs[sector]["radius"]
        else:
            external_perturbation = metrics[sector]["theta"]
            graph_radius = Fraction(0)
        total_perturbation = external_perturbation + pair_action_perturbation
        neumann_quotient = total_perturbation / base_distance
        margin = base_distance - total_perturbation
        coordinate_inverse = 1 / margin
        ambient_inverse = (
            metrics[sector]["vector_norm"]
            * (1 + graph_radius)
            * metrics[sector]["beta"]
            * coordinate_inverse
        )
        checks = {
            "pair_count_matches_registered_sector": (
                len(pairs) == EXPECTED_SECTOR_PAIR_COUNTS[sector]
            ),
            "external_dimension_is_registered": (
                len(centers[sector]) - len(selected.get(sector, ()))
                == EXTERNAL_DIMENSIONS[sector]
            ),
            "base_distance_is_strictly_positive": base_distance > 0,
            "neumann_margin_is_strictly_positive": margin > 0,
            "coordinate_inverse_formula_reproduces": coordinate_inverse == 1 / margin,
            "ambient_lift_formula_reproduces": (
                ambient_inverse
                == metrics[sector]["vector_norm"]
                * (1 + graph_radius)
                * metrics[sector]["beta"]
                * coordinate_inverse
            ),
        }
        exact_record = {
            "output_sector": sector,
            "external_dimension": EXTERNAL_DIMENSIONS[sector],
            "pair_dimension": len(pairs),
            "base_distance": _fraction_record(base_distance),
            "external_perturbation": _fraction_record(external_perturbation),
            "pair_action_perturbation": _fraction_record(pair_action_perturbation),
            "total_perturbation": _fraction_record(total_perturbation),
            "neumann_quotient": _fraction_record(neumann_quotient),
            "neumann_margin": _fraction_record(margin),
            "coordinate_inverse": _fraction_record(coordinate_inverse),
            "ambient_inverse": _fraction_record(ambient_inverse),
            "witness": {
                "pair_index": minimum_record["pair_index"],
                "external_center_index": minimum_record["minimum_external_center_index"],
            },
        }
        exact_sector_records.append(exact_record)
        sector_records.append({**exact_record, "checks": checks, "passed": all(checks.values())})

    maximum_neumann = max(
        sector_records, key=lambda record: _fraction(record["neumann_quotient"])
    )
    maximum_coordinate = max(
        sector_records, key=lambda record: _fraction(record["coordinate_inverse"])
    )
    maximum_ambient = max(
        sector_records, key=lambda record: _fraction(record["ambient_inverse"])
    )
    minimum_distance = min(
        sector_records, key=lambda record: _fraction(record["base_distance"])
    )
    checks = {
        "all_five_sector_operators_are_complete": (
            [record["output_sector"] for record in sector_records] == list(OUTPUT_SECTORS)
        ),
        "all_sector_structural_checks_pass": all(record["passed"] for record in sector_records),
        "all_sector_values_are_finite": _all_numeric_values_finite(sector_records),
    }
    audit = {
        "operator": "H_q(Z) = E_q Z - Z K_q(S)",
        "operator_norm": (
            "matrix infinity norm: maximum external-row sum over pair columns"
        ),
        "sector_order": list(OUTPUT_SECTORS),
        "sector_records": sector_records,
        "minimum_base_distance": minimum_distance["base_distance"],
        "minimum_base_distance_sector": minimum_distance["output_sector"],
        "minimum_base_distance_witness": minimum_distance["witness"],
        "maximum_neumann_quotient_upper": maximum_neumann["neumann_quotient"],
        "maximum_neumann_quotient_sector": maximum_neumann["output_sector"],
        "maximum_coordinate_inverse_bound": maximum_coordinate["coordinate_inverse"],
        "maximum_coordinate_inverse_sector": maximum_coordinate["output_sector"],
        "maximum_ambient_lifted_inverse_bound": maximum_ambient["ambient_inverse"],
        "maximum_ambient_lifted_inverse_sector": maximum_ambient["output_sector"],
        "exact_sector_digest_sha256": q011b._canonical_json_sha256(exact_sector_records),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return symmetric_audit, audit


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "selected_blocks": list(SELECTED_BLOCKS),
        "output_sectors": list(OUTPUT_SECTORS),
        "selected_dimensions": {str(key): value for key, value in SELECTED_DIMENSIONS.items()},
        "external_dimensions": {str(key): value for key, value in EXTERNAL_DIMENSIONS.items()},
        "expected_selected_count": EXPECTED_SELECTED_COUNT,
        "expected_pair_count": EXPECTED_PAIR_COUNT,
        "expected_sector_pair_counts": {
            str(key): value for key, value in EXPECTED_SECTOR_PAIR_COUNTS.items()
        },
        "expected_external_comparison_count": EXPECTED_EXTERNAL_COMPARISON_COUNT,
        "expected_unsafe_pair_indices": list(EXPECTED_UNSAFE_PAIR_INDICES),
        "maximum_graph_radius": _fraction_record(MAXIMUM_GRAPH_RADIUS),
        "maximum_graph_utilization": _fraction_record(MAXIMUM_GRAPH_UTILIZATION),
        "maximum_graph_contraction": _fraction_record(MAXIMUM_GRAPH_CONTRACTION),
        "minimum_base_homological_distance": _fraction_record(
            MINIMUM_BASE_HOMOLOGICAL_DISTANCE
        ),
        "maximum_neumann_quotient": _fraction_record(MAXIMUM_NEUMANN_QUOTIENT),
        "maximum_coordinate_inverse_bound": _fraction_record(
            MAXIMUM_COORDINATE_INVERSE_BOUND
        ),
        "maximum_ambient_inverse_bound": _fraction_record(MAXIMUM_AMBIENT_INVERSE_BOUND),
        "complex_distance_lower": "max(|Re|, |Im|) on exact dyadic point differences",
        "selected_modulus_upper": "|Re| + |Im| on exact dyadic centers",
        "graph_radius_formula": "2 theta / selected-external diagonal component gap",
        "symmetric_basis": "unscaled lexicographic i <= j",
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "graph_digest_sha256": cycle["graph_digest_sha256"],
        "pair_digest_sha256": cycle["pair_digest_sha256"],
        "homological_digest_sha256": cycle["homological_digest_sha256"],
    }


def run_interval_homological_inverse_audit() -> dict[str, Any]:
    sealed, q011k_artifact, _q011d_artifact = _sealed_input_audit()
    centers, selected, radii, metrics, spectral = _spectral_data(q011k_artifact)
    graph_exact, graph = _graph_audit(centers, selected, metrics)
    pairs_by_sector, pair_audit, unsafe_audit = _pair_and_full_space_audit(
        centers,
        selected,
        radii,
        q011k_artifact,
    )
    symmetric, homological = _homological_audit(
        centers,
        selected,
        metrics,
        graph_exact,
        pairs_by_sector,
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    graph_sections = {
        "exact_eigencoordinate_residual_audit": spectral,
        "selected_invariant_graph_audit": graph,
    }
    pair_sections = {
        "quadratic_pair_family_audit": pair_audit,
        "full_space_substitution_obstruction_audit": unsafe_audit,
    }
    homological_sections = {
        "symmetric_product_perturbation_audit": symmetric,
        "sector_homological_inverse_audit": homological,
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    graph_digest = q011b._canonical_json_sha256(graph_sections)
    pair_digest = q011b._canonical_json_sha256(pair_sections)
    homological_digest = q011b._canonical_json_sha256(homological_sections)
    strict_payload = {
        **input_sections,
        **graph_sections,
        **pair_sections,
        **homological_sections,
        "runner_source": runner,
    }
    digests_reproduce = (
        input_digest == q011b._canonical_json_sha256(input_sections)
        and graph_digest == q011b._canonical_json_sha256(graph_sections)
        and pair_digest == q011b._canonical_json_sha256(pair_sections)
        and homological_digest == q011b._canonical_json_sha256(homological_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "q011k_and_q011d_inputs_and_claim_boundaries_are_sealed": {
            "passed": sealed["passed"],
            "threshold": "both artifact/runner hashes, ten digests, accepted outcomes and claim boundaries reproduce",
            "value": sealed["checks"],
        },
        "exact_eigencoordinate_perturbation_bounds_are_complete": {
            "passed": spectral["passed"],
            "threshold": "17 exact dyadic center families and theta=beta*r bounds reconstruct with conjugate transport",
            "value": spectral["checks"],
        },
        "all_selected_invariant_graph_certificates_are_complete": {
            "passed": graph["passed"],
            "threshold": "blocks 0/1/16 have exact positive gaps and rigorous Riccati self-map/contraction records",
            "value": graph["checks"],
        },
        "full_space_substitution_obstruction_is_reproduced": {
            "passed": unsafe_audit["passed"],
            "threshold": "all 300 pairs audited and unsafe selected-overlap indices equal the registered eight",
            "value": unsafe_audit["checks"],
        },
        "all_quadratic_pairs_and_external_comparisons_are_complete": {
            "passed": pair_audit["passed"],
            "threshold": "24 selected centers, 300 ordered pairs, registered sector counts and 44010 comparisons reproduce",
            "value": pair_audit["checks"],
        },
        "all_symmetric_and_sector_homological_bounds_are_complete": {
            "passed": bool(symmetric["passed"] and homological["passed"]),
            "threshold": "unscaled symmetric-product perturbation and five full sector Sylvester operators are exact",
            "value": {
                "symmetric": symmetric["checks"],
                "homological": homological["checks"],
            },
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": "finite strict JSON, four section digests and runner provenance reproduce",
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    graph_radius = _fraction(graph["maximum_graph_radius_upper"])
    graph_utilization = _fraction(graph["maximum_self_map_utilization_upper"])
    graph_contraction = _fraction(graph["maximum_contraction_upper"])
    base_distance = _fraction(homological["minimum_base_distance"])
    neumann_quotient = _fraction(homological["maximum_neumann_quotient_upper"])
    coordinate_inverse = _fraction(homological["maximum_coordinate_inverse_bound"])
    ambient_inverse = _fraction(homological["maximum_ambient_lifted_inverse_bound"])
    hypothesis_gates = {
        "selected_graph_radii_and_contractions_are_within_registered_caps": {
            "passed": bool(
                validity_passed
                and graph_radius <= MAXIMUM_GRAPH_RADIUS
                and graph_utilization <= MAXIMUM_GRAPH_UTILIZATION
                and graph_contraction <= MAXIMUM_GRAPH_CONTRACTION
            ),
            "threshold": "maximum graph radius <=1e-4 and self-map utilization/contraction <=0.9",
            "value": {
                "maximum_graph_radius": graph["maximum_graph_radius_upper"],
                "maximum_self_map_utilization": graph[
                    "maximum_self_map_utilization_upper"
                ],
                "maximum_contraction": graph["maximum_contraction_upper"],
            },
        },
        "all_base_homological_distances_exceed_the_registered_floor": {
            "passed": bool(validity_passed and base_distance >= MINIMUM_BASE_HOMOLOGICAL_DISTANCE),
            "threshold": "minimum exact diagonal component distance across five sectors >=1e-5",
            "value": homological["minimum_base_distance"],
        },
        "all_sector_neumann_quotients_are_within_the_registered_cap": {
            "passed": bool(validity_passed and neumann_quotient <= MAXIMUM_NEUMANN_QUOTIENT),
            "threshold": "maximum (external plus pair-action perturbation)/base distance <=0.1",
            "value": homological["maximum_neumann_quotient_upper"],
        },
        "all_coordinate_homological_inverse_bounds_are_within_the_registered_cap": {
            "passed": bool(
                validity_passed and coordinate_inverse <= MAXIMUM_COORDINATE_INVERSE_BOUND
            ),
            "threshold": "maximum five-sector quotient-coordinate inverse infinity norm <=1e5",
            "value": homological["maximum_coordinate_inverse_bound"],
        },
        "all_ambient_lifted_inverse_bounds_are_within_the_registered_cap": {
            "passed": bool(validity_passed and ambient_inverse <= MAXIMUM_AMBIENT_INVERSE_BOUND),
            "threshold": "maximum ambient fixed-leaf lifted inverse infinity norm <=1e7",
            "value": homological["maximum_ambient_lifted_inverse_bound"],
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011l invariant-graph and homological proof is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the exact repaired selected/external split has a rigorously bounded "
            "quadratic homological inverse in the registered quotient norm"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered invariant-graph and Neumann bounds do not certify "
            "the repaired quadratic homological inverse"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Does the Q011k exact repaired selected/external split admit rigorous "
            "invariant graphs and bounded full-sector quadratic homological inverses?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "graph_digest_sha256": graph_digest,
        "pair_digest_sha256": pair_digest,
        "homological_digest_sha256": homological_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "exact_selected_invariant_graphs_are_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "all_five_quadratic_sector_homological_operators_are_invertible": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_coordinate_inverse_bound_is_rigorous": bool(
            validity_passed and hypotheses_passed
        ),
        "registered_ambient_lifted_inverse_bound_is_rigorous": bool(
            validity_passed and hypotheses_passed
        ),
        "full_space_resolvent_substitution_is_valid_for_all_pairs": False,
        "raw_q011b_map_is_certified": False,
        "q011d_or_q011e_raw_coefficients_transfer_to_repaired_map": False,
        "repaired_quadratic_jet_or_coefficients_are_certified": False,
        "forced_ssm_exists_or_is_unique": False,
        "nonlinear_normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This computer-assisted proof concerns the unique x-independent fixed point "
        "of the fixed 17x17 periodic repaired exact map, the Q011k-designated selected "
        "cluster, its exact invariant graphs in registered dyadic eigencoordinates, and "
        "five quadratic external-quotient homological operators in the registered matrix "
        "infinity norm. It does not make the Q011c2 amplitude path rigorous, label "
        "individual branches, certify the raw Q011b map, transfer Q011d--Q011h raw-map "
        "coefficients, construct a repaired quadratic jet or chart, certify higher-order "
        "nonresonance, prove a forced SSM, nonlinear normal attraction or a basin, or "
        "cover another grid, force, wall boundary, or D3Q27. The inverse bound is not an "
        "SSM existence or normal-attraction theorem."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_acceptance_changed": False,
        "q011d_numerical_homological_acceptance_changed": False,
        "q011e_through_q011h_raw_map_results_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011m for an exact interval/analytic repaired quadratic jet and "
            "a coefficient/residual majorant composed with the Q011l inverse bound."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Localize the first graph or sector witness and replace the diagonal-center "
            "Neumann majorant by a verified block inverse or Schur-Sylvester solve without "
            "changing the registered Q011l thresholds."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, exact reconstruction, graph, pair, sector or "
            "serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011l cycle failed strict serialization or digest")
    return cycle


def run_q011l_study() -> dict[str, Any]:
    cycle = run_interval_homological_inverse_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "exact_scalar_type": "fractions.Fraction",
            "input_upper_bounds": "Q011k 256-bit outward MPFR records parsed as exact fractions",
            "complex_centers": "binary64 real/imaginary parts parsed as exact dyadic fractions",
            "floating_point_used_for_proof_decisions": False,
        },
        "mathematical_scope": {
            "diagnostic": (
                "rigorous selected invariant graph and five-sector quadratic external "
                "homological inverse certificate"
            ),
            "grid": [SIZE, SIZE],
            "x_independent_fixed_point": True,
            "fixed_conservation_leaf": True,
            "exact_rational_repaired_map": True,
            "quadratic_order_only": True,
            "claim": "registered quotient and ambient-lifted inverse infinity norms only",
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
    result = run_q011l_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
