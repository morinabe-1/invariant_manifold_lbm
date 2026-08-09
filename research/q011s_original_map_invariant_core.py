"""Q011s original-map forward-invariant Lipschitz core audit."""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011k_interval_spectral_split as q011k
import research.q011l_interval_homological_inverse as q011l
import research.q011o_graph_transform_setup as q011o
import research.q011q_real_frame_setup as q011q
import research.q011r_nonlinear_graph_transform as q011r
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
SELECTED_BLOCKS = (0, 1, 16)
SELECTED_DIMENSIONS = {0: 6, 1: 9, 16: 9}
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574
FIXED_LEAF_DIMENSION = 2598

SELECTED_OPERATOR_CAP = Fraction(993, 1000)
FIXED_GRAPH_SLOPE_CAP = Fraction(999, 1000)
PHYSICAL_DISPLACEMENT_CAP = Fraction(1, 10**11)
SELECTED_IMAGE_RATIO_CAP = Fraction(999, 1000)
EXTERNAL_IMAGE_RATIO_CAP = Fraction(999, 1000)
POPULATION_FLOOR = Fraction(1, 50)
DENSITY_FLOOR = Fraction(99, 100)
MINIMUM_CORE_SCALE = Fraction(1, 16)
SCALE_CANDIDATES = tuple(Fraction(1, 2**power) for power in range(11))

Q011K_ARTIFACT_SHA256 = (
    "8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a"
)
Q011K_RUNNER_SHA256 = (
    "d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07"
)
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

Q011L_ARTIFACT_SHA256 = (
    "2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a"
)
Q011L_RUNNER_SHA256 = (
    "59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7"
)
Q011L_DIGESTS = (
    "1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011",
    "a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3",
    "694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377",
    "14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915",
    "c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45",
)
Q011L_DIGEST_NAMES = (
    "input_digest_sha256",
    "graph_digest_sha256",
    "pair_digest_sha256",
    "homological_digest_sha256",
    "result_digest_sha256",
)
Q011L_CLASSIFICATION = (
    "the exact repaired selected/external split has a rigorously bounded "
    "quadratic homological inverse in the registered quotient norm"
)

Q011Q_ARTIFACT_SHA256 = (
    "776be2af80fdbb867fd72eb3c0bdfe82ca30f5fa50bc9436818df5c7f87e676d"
)
Q011Q_RUNNER_SHA256 = (
    "83031650f7ecd54adb048a74ace2df96068317531aeb84fb57b9f797b9e33f67"
)
Q011Q_DIGESTS = (
    "c9e57c60fe678901c5502bf163d7317c06fedb35322e8591e741c330969829b5",
    "583a28e1453b75700d0674bf090c4f8c0652d7538f84bef7c8ea7e09415db54e",
    "1210f4d2c85d4a0cad9978531b297b5e493bac5f8d54d5eafa6ee7a5a68a6d7b",
    "ec52daadd80261b9e94672beb979fd5f01e4f1c4bc0e63090a0cccbb90cda26b",
    "274ddd32b50000c953c623285993ba533651a720c6dc79ae693a0e24a3f623ae",
)
Q011Q_DIGEST_NAMES = (
    "input_digest_sha256",
    "conjugation_digest_sha256",
    "frame_digest_sha256",
    "setup_digest_sha256",
    "result_digest_sha256",
)
Q011Q_CLASSIFICATION = (
    "the repaired fixed-leaf split admits a certified real-frame "
    "localized graph-transform setup"
)

Q011R_ARTIFACT_SHA256 = (
    "2d45e3c64965ee1e8bc47f1a7d75070fbeabbcb2711a62b1711da92878a58e11"
)
Q011R_RUNNER_SHA256 = (
    "8169e2fc7d5f7dccdc424bba31f37d4c03e6a669ab2e3f04d6289f03240b6d09"
)
Q011R_DIGESTS = (
    "7e9fa7b147ede559cffd117b7a6b8592d2939774f9821494759bbf3d634badd2",
    "3b8fba9cd370521880be3d4b77a9e2fc715e67ac22dc78e631f96e0d71317191",
    "77f2ac35d83726d0868ab08dd7648aee26bed7b00a40fb1405df1e1f162e023b",
    "8d33d01931c42730b18778c674282e6870224336cca72f66e81b447178d32d79",
    "b0520673f844d3f94a735c27800ff40d025a9437b01899e3d400b3c3fe0661ea",
)
Q011R_DIGEST_NAMES = (
    "input_digest_sha256",
    "transport_digest_sha256",
    "graph_digest_sha256",
    "radius_digest_sha256",
    "result_digest_sha256",
)
Q011R_CLASSIFICATION = (
    "the registered real localized graph transform is a strict contraction "
    "at a certified finite radius"
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


def _digest_tuple(
    cycle: dict[str, Any], names: tuple[str, ...]
) -> tuple[str, ...]:
    return tuple(cycle[name] for name in names)


def _sealed_input_audit() -> tuple[
    dict[str, Any], dict[str, dict[str, Any]]
]:
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
            Q011K_CLASSIFICATION,
        ),
        (
            "q011l",
            directory / "q011l_interval_homological_inverse.json",
            Path(q011l.__file__).resolve(),
            Q011L_ARTIFACT_SHA256,
            Q011L_RUNNER_SHA256,
            Q011L_DIGESTS,
            Q011L_DIGEST_NAMES,
            Q011L_CLASSIFICATION,
        ),
        (
            "q011q",
            directory / "q011q_real_frame_setup.json",
            Path(q011q.__file__).resolve(),
            Q011Q_ARTIFACT_SHA256,
            Q011Q_RUNNER_SHA256,
            Q011Q_DIGESTS,
            Q011Q_DIGEST_NAMES,
            Q011Q_CLASSIFICATION,
        ),
        (
            "q011r",
            directory / "q011r_nonlinear_graph_transform.json",
            Path(q011r.__file__).resolve(),
            Q011R_ARTIFACT_SHA256,
            Q011R_RUNNER_SHA256,
            Q011R_DIGESTS,
            Q011R_DIGEST_NAMES,
            Q011R_CLASSIFICATION,
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
        checks[f"{label}_accepted_outcome_reproduces"] = bool(
            cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
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

    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    l_theorem = artifacts["q011l"]["cycle"]["theorem_consequence"]
    q_theorem = artifacts["q011q"]["cycle"]["theorem_consequence"]
    r_theorem = artifacts["q011r"]["cycle"]["theorem_consequence"]
    r_claim = artifacts["q011r"]["cycle"]["claim_boundary"]
    checks["q011k_spectral_claim_boundary_is_preserved"] = bool(
        k_theorem[
            "exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"
        ]
        and k_theorem[
            "q011c2_designated_selected_cluster_has_rigorous_dimension_24"
        ]
        and k_theorem["rigorous_external_dimension_is_2574"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011l_graph_and_inverse_claim_boundary_is_preserved"] = bool(
        l_theorem["exact_selected_invariant_graphs_are_certified"]
        and l_theorem[
            "all_five_quadratic_sector_homological_operators_are_invertible"
        ]
        and not l_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011q_real_setup_claim_boundary_is_preserved"] = bool(
        q_theorem[
            "fixed_leaf_real_coordinate_lift_and_inverse_are_certified"
        ]
        and q_theorem[
            "registered_same_norm_real_linear_domination_is_rigorous"
        ]
        and q_theorem["radial_cutoff_and_real_graph_space_are_type_correct"]
        and not q_theorem[
            "an_exact_local_invariant_manifold_or_ssm_is_certified"
        ]
    )
    checks["q011r_localized_fixed_graph_claim_boundary_is_preserved"] = bool(
        r_theorem[
            "a_unique_lipschitz_fixed_graph_for_the_localized_map_exists"
        ]
        and not r_theorem[
            "an_original_map_local_invariant_manifold_or_ssm_is_certified"
        ]
        and "only for the localized map" in r_claim
    )
    checks["twenty_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 20
    )
    audit = {
        **records,
        "direct_digest_count": 20,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _selected_linear_operator_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    k_artifact = artifacts["q011k"]
    l_cycle = artifacts["q011l"]["cycle"]
    q_cycle = artifacts["q011q"]["cycle"]
    centers, selected, _radii, metrics, spectral = q011l._spectral_data(
        k_artifact
    )
    graphs, graph_audit = q011l._graph_audit(centers, selected, metrics)

    records = []
    exact_center_records = []
    exact_block_records = []
    block_operator_values: dict[int, Fraction] = {}
    for block_index in SELECTED_BLOCKS:
        center_records = []
        for center_index in selected[block_index]:
            center = centers[block_index][center_index]
            interval = q011o._center_modulus_bounds(center)
            exact_record = {
                "block_index": block_index,
                "center_index": center_index,
                "center": q011l._exact_complex_record(center),
                "modulus_lower": _fraction_record(interval.lower),
                "modulus_upper": _fraction_record(interval.upper),
            }
            center_records.append(exact_record)
            exact_center_records.append(exact_record)
        witness = max(
            center_records,
            key=lambda record: _fraction(record["modulus_upper"]),
        )
        maximum_center = _fraction(witness["modulus_upper"])
        theta = metrics[block_index]["theta"]
        graph_radius = graphs[block_index]["radius"]
        quotient_residual = theta * (1 + graph_radius)
        operator_upper = maximum_center + quotient_residual
        block_operator_values[block_index] = operator_upper
        exact_block = {
            "block_index": block_index,
            "selected_dimension": len(center_records),
            "maximum_selected_center_modulus_upper": _fraction_record(
                maximum_center
            ),
            "maximum_selected_center_witness": witness["center_index"],
            "same_norm_transformed_residual_upper": _fraction_record(theta),
            "selected_graph_radius_upper": _fraction_record(graph_radius),
            "triangular_selected_residual_upper": _fraction_record(
                quotient_residual
            ),
            "selected_operator_norm_upper": _fraction_record(operator_upper),
        }
        checks = {
            "selected_dimension_is_registered": (
                len(center_records) == SELECTED_DIMENSIONS[block_index]
            ),
            "all_modulus_intervals_are_ordered": all(
                _fraction(record["modulus_lower"])
                <= _fraction(record["modulus_upper"])
                for record in center_records
            ),
            "maximum_center_modulus_formula_reproduces": (
                maximum_center
                == max(
                    _fraction(record["modulus_upper"])
                    for record in center_records
                )
            ),
            "same_norm_triangular_residual_formula_reproduces": (
                quotient_residual == theta * (1 + graph_radius)
            ),
            "selected_operator_formula_reproduces": (
                operator_upper == maximum_center + quotient_residual
            ),
        }
        exact_block_records.append(exact_block)
        records.append(
            {
                **exact_block,
                "center_records": center_records,
                "checks": checks,
                "passed": all(checks.values()),
            }
        )

    global_operator = max(block_operator_values.values())
    global_witness = max(
        block_operator_values, key=block_operator_values.__getitem__
    )
    q_linear = q_cycle["real_same_norm_linear_split_audit"]
    real_coupling = _fraction(
        q_linear["real_selected_external_coupling_upper"]
    )
    one_centers = [
        centers[1][center_index] for center_index in selected[1]
    ]
    sixteen_centers = [
        centers[16][center_index] for center_index in selected[16]
    ]
    checks = {
        "q011l_spectral_reconstruction_matches_artifact": (
            spectral == l_cycle["exact_eigencoordinate_residual_audit"]
        ),
        "q011l_graph_reconstruction_matches_artifact": (
            graph_audit == l_cycle["selected_invariant_graph_audit"]
        ),
        "all_three_selected_block_records_pass": all(
            record["passed"] for record in records
        ),
        "all_twenty_four_selected_centers_are_evaluated": (
            len(exact_center_records) == SELECTED_DIMENSION
        ),
        "selected_blocks_are_exactly_registered": (
            tuple(record["block_index"] for record in records)
            == SELECTED_BLOCKS
        ),
        "blocks_one_and_sixteen_are_exact_conjugates": bool(
            selected[1] == selected[16]
            and sixteen_centers
            == [(real, -imaginary) for real, imaginary in one_centers]
            and block_operator_values[1] == block_operator_values[16]
        ),
        "global_selected_operator_formula_reproduces": (
            global_operator == max(block_operator_values.values())
        ),
        "q011q_real_shear_preserves_zero_selected_diagonal": (
            _fraction(q_linear["zero_selected_operator_norm_upper"])
            == block_operator_values[0]
            and q_linear["real_operator_coordinate_identity"]
            == "R^(-1)[[S,B],[0,E]]R=[[S,S H+B-H E],[0,E]]"
        ),
        "q011q_real_coupling_is_used_directly": (
            real_coupling
            == _fraction(
                q_linear["real_selected_external_coupling_upper"]
            )
        ),
        "same_complex_absolute_row_sum_norm_is_used": (
            q_linear["operator_norm"]
            == (
                "complex-modulus block-sup norm restricted to the real fixed "
                "selected and external quotient spaces"
            )
        ),
        "eigenvalue_only_conorm_or_external_bounds_are_not_substituted": True,
    }
    audit = {
        "selected_blocks": list(SELECTED_BLOCKS),
        "selected_center_count": len(exact_center_records),
        "operator_norm": (
            "complex absolute row-sum induced by the global block-sup norm, "
            "restricted to the real fixed selected space"
        ),
        "selected_operator_formula": (
            "p_S,n=max selected center modulus upper+theta_n(1+r_G,n)"
        ),
        "block_records": records,
        "exact_selected_center_record_digest_sha256": (
            q011b._canonical_json_sha256(exact_center_records)
        ),
        "exact_selected_block_record_digest_sha256": (
            q011b._canonical_json_sha256(exact_block_records)
        ),
        "global_selected_operator_norm_upper": _fraction_record(
            global_operator
        ),
        "global_selected_operator_witness_block": global_witness,
        "real_selected_external_coupling_upper": _fraction_record(
            real_coupling
        ),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, {"p_S": global_operator, "b": real_coupling}


def _fixed_graph_core_data_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    q_cycle = artifacts["q011q"]["cycle"]
    r_cycle = artifacts["q011r"]["cycle"]
    q_coordinate = q_cycle["real_fixed_leaf_coordinate_audit"]
    q_linear = q_cycle["real_same_norm_linear_split_audit"]
    q_localization = q_cycle["real_localized_graph_space_audit"]
    r_transport = r_cycle["real_derivative_transport_audit"]
    r_graph = r_cycle["global_graph_transform_definition_audit"]
    r_campaign = r_cycle["graph_transform_radius_campaign_audit"]
    selected = r_campaign["selected_record"]
    if selected is None:
        raise RuntimeError("Q011r has no selected fixed-graph radius")

    radius = _fraction(selected["radius"])
    slope = _fraction(selected["graph_slope"])
    mu_2 = _fraction(
        r_transport["real_second_derivative_bilinear_upper"]
    )
    lift_norm = _fraction(q_coordinate["real_physical_lift_norm_upper"])
    coupling = _fraction(
        q_linear["real_selected_external_coupling_upper"]
    )
    root_population = _fraction(
        q_localization["root_population_floor_lower"]
    )
    root_density = _fraction(
        q_localization["root_density_floor_lower"]
    )
    checks = {
        "q011r_selected_radius_record_passes": bool(
            selected["passed"] and all(selected["checks"].values())
        ),
        "q011r_fixed_graph_exists_uniquely_for_the_localized_map": (
            r_cycle["theorem_consequence"][
                "a_unique_lipschitz_fixed_graph_for_the_localized_map_exists"
            ]
        ),
        "fixed_graph_origin_is_inherited_from_the_graph_space": bool(
            r_graph["real_graph_space"]["fixes_origin"]
            and r_graph["graph_transform"]["origin_is_fixed"]
        ),
        "fixed_graph_uniform_height_is_the_selected_radius": (
            radius == _fraction(r_campaign["selected_radius"])
        ),
        "fixed_graph_refined_slope_is_the_transform_image_bound": bool(
            slope == _fraction(selected["graph_slope"])
            and r_graph["graph_transform"]["slope_upper"]
            == "ell_rho=(q+delta_rho)/d_rho"
            and slope < 1
        ),
        "fixed_point_identity_gives_the_refined_slope": bool(
            r_cycle["theorem_consequence"][
                "the_nonlinear_graph_transform_is_a_self_map"
            ]
            and r_cycle["theorem_consequence"][
                "the_nonlinear_graph_transform_is_a_strict_contraction"
            ]
        ),
        "localized_fixed_graph_invariance_is_certified": bool(
            r_graph["base_inverse"][
                "global_bijection_follows_from_fixed_point_inverse"
            ]
            and r_graph["graph_transform"][
                "real_selected_and_external_spaces_are_preserved"
            ]
        ),
        "q011q_cutoff_is_identity_on_the_core_ball": bool(
            q_localization["cutoff"]["identity_on_core_ball"]
            and q_localization["localized_map"][
                "equals_original_map_on_core_ball"
            ]
        ),
        "q011q_real_dimensions_and_fixed_leaf_close": bool(
            q_coordinate["selected_real_dimension"] == SELECTED_DIMENSION
            and q_coordinate["external_real_dimension"]
            == EXTERNAL_DIMENSION
            and q_coordinate["total_fixed_leaf_real_dimension"]
            == FIXED_LEAF_DIMENSION
        ),
        "q011r_transport_uses_the_same_q011q_lift_and_coupling": bool(
            _fraction(
                r_transport["real_physical_lift_norm_upper"]
            )
            == lift_norm
            and _fraction(
                r_transport["real_selected_external_coupling_upper"]
            )
            == coupling
        ),
    }
    values = {
        "rho": radius,
        "ell": slope,
        "mu_2": mu_2,
        "K_L": lift_norm,
        "b": coupling,
        "root_population_floor": root_population,
        "root_density_floor": root_density,
    }
    audit = {
        "localized_fixed_graph": {
            "notation": "psi_*:S_R->E_R",
            "origin": "psi_*(0)=0",
            "uniform_height_upper": _fraction_record(radius),
            "refined_lipschitz_upper": _fraction_record(slope),
            "local_height_formula": "||psi_*(s)||<=ell_*||s||",
            "localized_invariance": (
                "F_rho(s,psi_*(s))=(u,psi_*(u))"
            ),
        },
        "core_transfer_data": {
            "real_second_derivative_bilinear_upper": _fraction_record(
                mu_2
            ),
            "real_physical_lift_norm_upper": _fraction_record(lift_norm),
            "real_selected_external_coupling_upper": _fraction_record(
                coupling
            ),
            "root_population_floor_lower": _fraction_record(
                root_population
            ),
            "root_density_floor_lower": _fraction_record(root_density),
        },
        "fixed_leaf_selected_real_dimension": SELECTED_DIMENSION,
        "fixed_leaf_external_real_dimension": EXTERNAL_DIMENSION,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, values


def _core_record(
    scale: Fraction,
    values: dict[str, Fraction],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    rho = values["rho"]
    radius = scale * rho
    slope = values["ell"]
    p_selected = values["p_S"]
    coupling = values["b"]
    mu_2 = values["mu_2"]
    lift_norm = values["K_L"]

    graph_height = slope * radius
    nonlinear_amplitude = Fraction(1, 2) * mu_2 * radius**2
    selected_ratio = (
        p_selected + coupling * slope + Fraction(1, 2) * mu_2 * radius
    )
    selected_image_radius = selected_ratio * radius
    external_ratio = slope * selected_ratio
    external_image_radius = external_ratio * radius
    input_physical = lift_norm * radius
    output_physical = lift_norm * selected_image_radius
    input_population = values["root_population_floor"] - input_physical
    input_density = values["root_density_floor"] - 9 * input_physical
    output_population = values["root_population_floor"] - output_physical
    output_density = values["root_density_floor"] - 9 * output_physical

    checks = {
        "scale_and_radius_formula_reproduce": radius == scale * rho,
        "fixed_graph_local_height_formula_reproduces": (
            graph_height == slope * radius
        ),
        "input_full_coordinate_radius_is_in_cutoff_core": bool(
            radius <= rho and graph_height <= radius
        ),
        "localized_and_original_maps_agree_on_input_patch": radius <= rho,
        "core_nonlinear_amplitude_formula_reproduces": (
            nonlinear_amplitude
            == Fraction(1, 2) * mu_2 * radius**2
        ),
        "selected_image_ratio_formula_reproduces": (
            selected_ratio
            == p_selected
            + coupling * slope
            + Fraction(1, 2) * mu_2 * radius
        ),
        "external_image_ratio_formula_reproduces": (
            external_ratio == slope * selected_ratio
        ),
        "selected_operator_fits_cap": (
            p_selected <= SELECTED_OPERATOR_CAP
        ),
        "fixed_graph_slope_fits_cap": (
            slope <= FIXED_GRAPH_SLOPE_CAP
        ),
        "selected_image_ratio_fits_cap": (
            selected_ratio <= SELECTED_IMAGE_RATIO_CAP
        ),
        "external_image_ratio_fits_cap": (
            external_ratio <= EXTERNAL_IMAGE_RATIO_CAP
        ),
        "one_step_full_image_is_in_same_core": bool(
            selected_ratio <= 1
            and external_ratio <= selected_ratio
            and selected_image_radius <= radius
        ),
        "input_physical_displacement_fits_cap": (
            input_physical <= PHYSICAL_DISPLACEMENT_CAP
        ),
        "output_physical_displacement_fits_cap": (
            output_physical <= PHYSICAL_DISPLACEMENT_CAP
        ),
        "input_population_and_density_floors_pass": bool(
            input_population >= POPULATION_FLOOR
            and input_density >= DENSITY_FLOOR
        ),
        "output_population_and_density_floors_pass": bool(
            output_population >= POPULATION_FLOOR
            and output_density >= DENSITY_FLOOR
        ),
        "forward_induction_stays_in_original_map_core": bool(
            selected_image_radius <= radius <= rho
        ),
    }
    exact = {
        "scale": scale,
        "radius": radius,
        "fixed_graph_height_upper": graph_height,
        "nonlinear_amplitude_upper": nonlinear_amplitude,
        "selected_image_ratio_upper": selected_ratio,
        "selected_image_radius_upper": selected_image_radius,
        "external_image_ratio_upper": external_ratio,
        "external_image_radius_upper": external_image_radius,
        "input_physical_displacement_upper": input_physical,
        "output_physical_displacement_upper": output_physical,
        "input_population_floor_lower": input_population,
        "input_density_floor_lower": input_density,
        "output_population_floor_lower": output_population,
        "output_density_floor_lower": output_density,
    }
    record = {
        name: _fraction_record(value) for name, value in exact.items()
    }
    record["checks"] = checks
    record["passed"] = all(checks.values())
    return record, exact


def _is_nondecreasing(values: list[Fraction]) -> bool:
    return all(left <= right for left, right in itertools.pairwise(values))


def _is_nonincreasing(values: list[Fraction]) -> bool:
    return all(left >= right for left, right in itertools.pairwise(values))


def _core_campaign_audit(
    values: dict[str, Fraction],
) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    exact_records: list[dict[str, Fraction]] = []
    for scale in SCALE_CANDIDATES:
        record, exact = _core_record(scale, values)
        records.append(record)
        exact_records.append(exact)

    passing_records = [record for record in records if record["passed"]]
    selected_record = (
        max(
            passing_records,
            key=lambda record: _fraction(record["radius"]),
        )
        if passing_records
        else None
    )
    selected_radius = (
        _fraction(selected_record["radius"])
        if selected_record is not None
        else None
    )
    larger_failures = sorted(
        (
            record
            for record in records
            if selected_radius is not None
            and _fraction(record["radius"]) > selected_radius
            and not record["passed"]
        ),
        key=lambda record: _fraction(record["radius"]),
    )
    first_failed_larger = larger_failures[0] if larger_failures else None
    first_failed_constraints = (
        [
            name
            for name, passed in first_failed_larger["checks"].items()
            if not passed
        ]
        if first_failed_larger is not None
        else []
    )

    ascending = sorted(
        exact_records, key=lambda record: record["radius"]
    )
    monotonicity_checks = {
        "selected_image_ratio_is_nondecreasing": _is_nondecreasing(
            [record["selected_image_ratio_upper"] for record in ascending]
        ),
        "external_image_ratio_is_nondecreasing": _is_nondecreasing(
            [record["external_image_ratio_upper"] for record in ascending]
        ),
        "input_physical_displacement_is_nondecreasing": _is_nondecreasing(
            [
                record["input_physical_displacement_upper"]
                for record in ascending
            ]
        ),
        "output_physical_displacement_is_nondecreasing": _is_nondecreasing(
            [
                record["output_physical_displacement_upper"]
                for record in ascending
            ]
        ),
        "all_population_and_density_floors_are_nonincreasing": bool(
            all(
                _is_nonincreasing([record[name] for record in ascending])
                for name in (
                    "input_population_floor_lower",
                    "input_density_floor_lower",
                    "output_population_floor_lower",
                    "output_density_floor_lower",
                )
            )
        ),
    }
    pass_flags = [record["passed"] for record in records]
    first_pass = (
        pass_flags.index(True) if any(pass_flags) else len(pass_flags)
    )
    exact_serialized = [
        {
            name: _fraction_record(value)
            for name, value in record.items()
        }
        for record in exact_records
    ]
    checks = {
        "all_eleven_registered_scales_are_present": (
            len(records) == len(SCALE_CANDIDATES) == 11
        ),
        "scales_are_strictly_decreasing": all(
            left > right
            for left, right in itertools.pairwise(SCALE_CANDIDATES)
        ),
        "all_core_records_use_exact_fraction_arithmetic": True,
        "all_record_formula_checks_pass": all(
            record["checks"][
                "scale_and_radius_formula_reproduce"
            ]
            and record["checks"][
                "fixed_graph_local_height_formula_reproduces"
            ]
            and record["checks"][
                "core_nonlinear_amplitude_formula_reproduces"
            ]
            and record["checks"][
                "selected_image_ratio_formula_reproduces"
            ]
            and record["checks"][
                "external_image_ratio_formula_reproduces"
            ]
            for record in records
        ),
        "passing_records_form_a_decreasing_radius_suffix": (
            pass_flags
            == [False] * first_pass + [True] * (len(records) - first_pass)
        ),
        "selected_radius_is_the_largest_passing_candidate": bool(
            selected_record is None
            or _fraction(selected_record["radius"])
            == max(
                _fraction(record["radius"])
                for record in passing_records
            )
        ),
        "first_larger_failure_is_recorded_when_present": bool(
            selected_record is None
            or selected_record is records[0]
            or (
                first_failed_larger is not None
                and first_failed_constraints
            )
        ),
        "all_registered_monotonicity_checks_pass": all(
            monotonicity_checks.values()
        ),
        "all_core_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    selected_proof = (
        {
            "input_graph_patch_is_in_cutoff_identity_core": selected_record[
                "checks"
            ]["input_full_coordinate_radius_is_in_cutoff_core"],
            "localized_and_original_maps_agree_on_the_patch": selected_record[
                "checks"
            ]["localized_and_original_maps_agree_on_input_patch"],
            "localized_fixed_graph_maps_into_itself": selected_record[
                "checks"
            ]["one_step_full_image_is_in_same_core"],
            "one_step_image_is_in_cutoff_identity_core": selected_record[
                "checks"
            ]["one_step_full_image_is_in_same_core"],
            "original_map_is_forward_invariant_by_induction": selected_record[
                "checks"
            ]["forward_induction_stays_in_original_map_core"],
            "backward_invariance_or_onto_is_used": False,
        }
        if selected_record is not None
        else None
    )
    return {
        "scale_candidates": [
            _fraction_record(scale) for scale in SCALE_CANDIDATES
        ],
        "core_formulas": {
            "base_radius": "r=sigma rho_*",
            "fixed_graph_height": "ell_* r",
            "selected_image_ratio": (
                "c_r=p_S+b ell_*+(mu_2/2)r"
            ),
            "external_image_ratio": "ell_* c_r",
            "input_physical_displacement": "K_L r",
            "output_physical_displacement": "K_L c_r r",
        },
        "core_records": records,
        "exact_core_record_digest_sha256": q011b._canonical_json_sha256(
            exact_serialized
        ),
        "monotonicity_checks": monotonicity_checks,
        "passing_scale_count": len(passing_records),
        "selected_scale": (
            selected_record["scale"]
            if selected_record is not None
            else None
        ),
        "selected_radius": (
            selected_record["radius"]
            if selected_record is not None
            else None
        ),
        "selected_record": selected_record,
        "first_failed_larger_radius": (
            first_failed_larger["radius"]
            if first_failed_larger is not None
            else None
        ),
        "first_failed_larger_constraints": first_failed_constraints,
        "selected_core_transfer_proof": selected_proof,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "selected_blocks": list(SELECTED_BLOCKS),
        "selected_block_dimensions": {
            str(key): value for key, value in SELECTED_DIMENSIONS.items()
        },
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
        "selected_operator_cap": _fraction_record(SELECTED_OPERATOR_CAP),
        "fixed_graph_slope_cap": _fraction_record(
            FIXED_GRAPH_SLOPE_CAP
        ),
        "input_output_physical_displacement_cap": _fraction_record(
            PHYSICAL_DISPLACEMENT_CAP
        ),
        "selected_image_ratio_cap": _fraction_record(
            SELECTED_IMAGE_RATIO_CAP
        ),
        "external_image_ratio_cap": _fraction_record(
            EXTERNAL_IMAGE_RATIO_CAP
        ),
        "population_floor": _fraction_record(POPULATION_FLOOR),
        "density_floor": _fraction_record(DENSITY_FLOOR),
        "minimum_core_scale": _fraction_record(MINIMUM_CORE_SCALE),
        "scale_candidates": [
            _fraction_record(scale) for scale in SCALE_CANDIDATES
        ],
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
        "linear_digest_sha256": cycle["linear_digest_sha256"],
        "graph_digest_sha256": cycle["graph_digest_sha256"],
        "core_digest_sha256": cycle["core_digest_sha256"],
    }


def run_original_map_invariant_core_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    linear, linear_values = _selected_linear_operator_audit(artifacts)
    graph, graph_values = _fixed_graph_core_data_audit(artifacts)
    values = {**linear_values, **graph_values}
    core = _core_campaign_audit(values)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    linear_sections = {
        "selected_linear_operator_audit": linear,
    }
    graph_sections = {
        "localized_fixed_graph_core_data_audit": graph,
    }
    core_sections = {
        "original_map_invariant_core_campaign_audit": core,
    }
    input_digest = q011b._canonical_json_sha256(input_sections)
    linear_digest = q011b._canonical_json_sha256(linear_sections)
    graph_digest = q011b._canonical_json_sha256(graph_sections)
    core_digest = q011b._canonical_json_sha256(core_sections)
    strict_payload = {
        **input_sections,
        **linear_sections,
        **graph_sections,
        **core_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and linear_digest == q011b._canonical_json_sha256(linear_sections)
        and graph_digest == q011b._canonical_json_sha256(graph_sections)
        and core_digest == q011b._canonical_json_sha256(core_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    selected = core["selected_record"]
    proof = core["selected_core_transfer_proof"]
    validity_gates = {
        "four_direct_inputs_and_twenty_digests_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/l/q/r artifacts, runners, twenty digests, outcomes "
                "and claim boundaries reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "all_selected_moduli_and_three_operator_bounds_reconstruct": {
            "passed": linear["passed"],
            "threshold": (
                "twenty-four selected centers and three same-norm "
                "selected operator bounds reproduce"
            ),
            "value": linear["checks"],
        },
        "real_shear_preserves_selected_diagonal_and_updates_coupling": {
            "passed": bool(
                linear["checks"][
                    "q011q_real_shear_preserves_zero_selected_diagonal"
                ]
                and linear["checks"][
                    "q011q_real_coupling_is_used_directly"
                ]
            ),
            "threshold": (
                "Q011q leaves S unchanged and supplies the real coupling b"
            ),
            "value": {
                "p_S": linear[
                    "global_selected_operator_norm_upper"
                ],
                "b": linear[
                    "real_selected_external_coupling_upper"
                ],
            },
        },
        "localized_fixed_graph_origin_height_slope_and_invariance_reproduce": {
            "passed": graph["passed"],
            "threshold": (
                "Q011r fixed graph has origin zero, height rho_*, refined "
                "slope ell_* and localized forward invariance"
            ),
            "value": graph["checks"],
        },
        "cutoff_equality_and_one_step_core_bounds_reproduce": {
            "passed": False,
            "threshold": (
                "input and one-step image remain in the cutoff identity "
                "core, so original and localized maps agree"
            ),
            "value": proof,
        },
        "all_eleven_exact_scales_and_monotonicity_reproduce": {
            "passed": core["passed"],
            "threshold": (
                "eleven Fraction scales, monotonicity, largest passing "
                "candidate and first larger failure reproduce"
            ),
            "value": core["checks"],
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite strict JSON, four section digests, result digest "
                "and runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    # The backward/onto flag is deliberately false and is not a required proof
    # premise.  Evaluate the five affirmative transfer statements explicitly.
    if proof is not None:
        validity_gates[
            "cutoff_equality_and_one_step_core_bounds_reproduce"
        ]["passed"] = all(
            proof[name]
            for name in (
                "input_graph_patch_is_in_cutoff_identity_core",
                "localized_and_original_maps_agree_on_the_patch",
                "localized_fixed_graph_maps_into_itself",
                "one_step_image_is_in_cutoff_identity_core",
                "original_map_is_forward_invariant_by_induction",
            )
        ) and not proof["backward_invariance_or_onto_is_used"]
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )

    selected_radius = (
        _fraction(core["selected_radius"])
        if core["selected_radius"] is not None
        else None
    )
    selected_scale = (
        _fraction(core["selected_scale"])
        if core["selected_scale"] is not None
        else None
    )
    linear_cap = bool(
        linear_values["p_S"] <= SELECTED_OPERATOR_CAP
        and linear["selected_center_count"] == SELECTED_DIMENSION
    )
    graph_ready = bool(
        graph["passed"]
        and graph_values["ell"] <= FIXED_GRAPH_SLOPE_CAP
        and graph_values["ell"] < 1
    )
    input_core = bool(
        selected is not None
        and selected_radius is not None
        and selected_scale is not None
        and selected_scale >= MINIMUM_CORE_SCALE
        and selected["checks"][
            "input_full_coordinate_radius_is_in_cutoff_core"
        ]
        and selected["checks"][
            "input_physical_displacement_fits_cap"
        ]
        and selected["checks"][
            "input_population_and_density_floors_pass"
        ]
    )
    output_core = bool(
        selected is not None
        and selected["checks"]["selected_image_ratio_fits_cap"]
        and selected["checks"]["external_image_ratio_fits_cap"]
        and selected["checks"]["one_step_full_image_is_in_same_core"]
        and selected["checks"][
            "output_physical_displacement_fits_cap"
        ]
        and selected["checks"][
            "output_population_and_density_floors_pass"
        ]
    )
    forward_invariance = bool(
        proof is not None
        and proof["localized_and_original_maps_agree_on_the_patch"]
        and proof["localized_fixed_graph_maps_into_itself"]
        and proof["original_map_is_forward_invariant_by_induction"]
        and not proof["backward_invariance_or_onto_is_used"]
    )
    hypothesis_gates = {
        "selected_operator_upper_fits_registered_cap": {
            "passed": bool(validity_passed and linear_cap),
            "threshold": "twenty-four-center same-norm p_S<=0.993",
            "value": linear[
                "global_selected_operator_norm_upper"
            ],
        },
        "localized_fixed_graph_data_are_usable_for_core_transfer": {
            "passed": bool(validity_passed and graph_ready),
            "threshold": (
                "rho_*>0, psi_*(0)=0 and refined ell_*<=0.999"
            ),
            "value": graph["localized_fixed_graph"],
        },
        "largest_passing_input_patch_has_registered_scale_and_buffer": {
            "passed": bool(validity_passed and input_core),
            "threshold": (
                "selected scale>=1/16 and input patch lies in cutoff "
                "identity core with physical buffer"
            ),
            "value": selected,
        },
        "one_step_full_image_has_strict_core_and_buffer_margins": {
            "passed": bool(validity_passed and output_core),
            "threshold": (
                "c_r<=0.999, ell_*c_r<=0.999 and output lies in the "
                "same core with physical buffer"
            ),
            "value": selected,
        },
        "original_exact_map_preserves_a_twenty_four_dimensional_graph_patch": {
            "passed": bool(validity_passed and forward_invariance),
            "threshold": (
                "original repaired exact map is forward invariant on a "
                "24-real-dimensional fixed-leaf Lipschitz graph patch"
            ),
            "value": proof,
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q011s original-map invariant-core audit is invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the original repaired exact map has a certified "
            "forward-invariant Lipschitz graph patch on the fixed "
            "conservation leaf"
        )
    else:
        outcome = "rejected"
        classification = (
            "the Q011r localized fixed graph does not remain in the cutoff "
            "core on the registered inner-radius grid"
        )

    cycle: dict[str, Any] = {
        "question": (
            "Does a registered inner patch of the Q011r localized fixed "
            "graph and its image remain in the cutoff identity core, so it "
            "is forward invariant for the original repaired exact map?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "linear_digest_sha256": linear_digest,
        "graph_digest_sha256": graph_digest,
        "core_digest_sha256": core_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "failed_hypothesis_order": [
            name
            for name, gate in hypothesis_gates.items()
            if not gate["passed"]
        ],
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    cycle["result_digest_sha256"] = q011b._canonical_json_sha256(
        _result_digest_sections(cycle)
    )
    cycle["theorem_consequence"] = {
        "the_selected_operator_upper_is_reconstructed_in_the_same_norm": bool(
            validity_passed and hypotheses_passed
        ),
        "the_q011r_fixed_graph_has_a_certified_cutoff_core_restriction": bool(
            validity_passed and hypotheses_passed
        ),
        "the_original_and_localized_maps_agree_on_the_graph_patch": bool(
            validity_passed and hypotheses_passed
        ),
        "the_original_map_has_a_forward_invariant_lipschitz_graph_patch": bool(
            validity_passed and hypotheses_passed
        ),
        "the_graph_patch_is_twenty_four_real_dimensional_on_the_fixed_leaf": bool(
            validity_passed and hypotheses_passed
        ),
        "all_forward_iterates_remain_in_the_certified_core": bool(
            validity_passed and hypotheses_passed
        ),
        "backward_invariance_or_onto_is_certified": False,
        "c1_or_higher_smoothness_is_certified": False,
        "origin_tangency_is_certified": False,
        "spectral_quotient_ssm_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_q011l_q011q_or_q011r_acceptance_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the fixed 17x17 repaired exact map on the "
        "fixed conservation leaf, the Q011r localized fixed graph, the "
        "twenty-four-dimensional selected real space and the eleven "
        "registered inner scales. It certifies a forward-invariant "
        "Lipschitz graph patch because that patch and every forward image "
        "remain in the cutoff identity core where the original and "
        "localized maps agree. It certifies no backward invariance, onto "
        "property, C1 or higher smoothness, origin tangency, "
        "spectral-quotient SSM uniqueness, normal attraction, basin, "
        "optimal or larger radius, other grid, force, wall boundary or "
        "D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011l_homological_inverse_acceptance_changed": False,
        "q011q_real_setup_acceptance_changed": False,
        "q011r_localized_graph_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011t to decide whether a C1 graph-transform "
            "space, origin derivative equation, selected tangency and "
            "spectral-quotient bounds upgrade this Lipschitz graph patch "
            "to a smooth invariant manifold or SSM claim."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Revise only the first failed selected-operator, fixed-graph "
            "slope, core-ratio or physical-buffer condition."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, linear reconstruction, "
            "fixed-graph data, core formula or serialization failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011s cycle failed strict serialization or digest")
    return cycle


def run_q011s_study() -> dict[str, Any]:
    cycle = run_original_map_invariant_core_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "floating_point_used_for_gate_decisions": False,
            "selected_center_count": SELECTED_DIMENSION,
            "scale_candidate_count": len(SCALE_CANDIDATES),
        },
        "mathematical_scope": {
            "diagnostic": "original-map forward-invariant Lipschitz core",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "selected_real_dimension": SELECTED_DIMENSION,
            "external_real_dimension": EXTERNAL_DIMENSION,
            "localized_fixed_graph_claim": True,
            "original_map_forward_invariant_lipschitz_patch_claim": (
                cycle["hypothesis_outcome"] == "accepted"
            ),
            "backward_invariance_claim": False,
            "smoothness_claim": False,
            "origin_tangency_claim": False,
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
    result = run_q011s_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
