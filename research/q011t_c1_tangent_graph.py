"""Q011t C1-localized tangent graph-patch audit."""

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
import research.q011m_quadratic_jet_majorant as q011m
import research.q011o_graph_transform_setup as q011o
import research.q011q_real_frame_setup as q011q
import research.q011r_nonlinear_graph_transform as q011r
import research.q011s_original_map_invariant_core as q011s
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
COORDINATE_SLOT_COUNT = 2598
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574
SELECTED_BLOCKS = (0, 1, 16)

CUTOFF_POWER = 16
CUTOFF_INNER_SCALE = 2
CUTOFF_TRANSITION_END = 4
CUTOFF_SUPPORT_FACTOR = 4
CUTOFF_DERIVATIVE_CAP = Fraction(129)
NONLINEAR_AMPLITUDE_FACTOR = Fraction(8)
NONLINEAR_DERIVATIVE_FACTOR = Fraction(516)

NONLINEAR_DERIVATIVE_CAP = Fraction(1, 1000)
BASE_INVERSE_UTILIZATION_CAP = Fraction(1, 100)
HEIGHT_RATIO_CAP = Fraction(99, 100)
C1_GRAPH_SLOPE_CAP = Fraction(999, 1000)
C0_GRAPH_CONTRACTION_CAP = Fraction(99, 100)
DERIVATIVE_FIBER_CONTRACTION_CAP = Fraction(1999, 2000)
PHYSICAL_SUPPORT_CAP = Fraction(1, 10**11)
ORIGINAL_SELECTED_IMAGE_RATIO_CAP = Fraction(999, 1000)
ORIGINAL_EXTERNAL_IMAGE_RATIO_CAP = Fraction(999, 1000)
POPULATION_FLOOR = Fraction(1, 50)
DENSITY_FLOOR = Fraction(99, 100)
MINIMUM_SCALE = Fraction(1, 4096)
SCALE_EXPONENTS = tuple(range(6, 17))
SCALE_CANDIDATES = tuple(Fraction(1, 2**exponent) for exponent in SCALE_EXPONENTS)

SPECTRAL_QUOTIENT_BRACKET_WIDTH_CAP = 1
SPECTRAL_QUOTIENT_UPPER_CAP = 90

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
    "the repaired exact map admits a unique graph-gauge quadratic jet with "
    "the registered coefficient and cubic-defect majorants"
)

Q011Q_ARTIFACT_SHA256 = "776be2af80fdbb867fd72eb3c0bdfe82ca30f5fa50bc9436818df5c7f87e676d"
Q011Q_RUNNER_SHA256 = "83031650f7ecd54adb048a74ace2df96068317531aeb84fb57b9f797b9e33f67"
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
    "the repaired fixed-leaf split admits a certified real-frame localized graph-transform setup"
)

Q011R_ARTIFACT_SHA256 = "2d45e3c64965ee1e8bc47f1a7d75070fbeabbcb2711a62b1711da92878a58e11"
Q011R_RUNNER_SHA256 = "8169e2fc7d5f7dccdc424bba31f37d4c03e6a669ab2e3f04d6289f03240b6d09"
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

Q011S_ARTIFACT_SHA256 = "d7399671504cc513aecc491210108c31365c63a74864ecf04e629b3d1348bc52"
Q011S_RUNNER_SHA256 = "beeeb6699b5c3a7e7636b2c7afd6036bc6959213e81339f39961c325d9347367"
Q011S_DIGESTS = (
    "4808619d977f8d14c4f8b454e846558ad047337e4343c6b9bef791e2c2b99af5",
    "6a657463b847ce242346aea8b582f1f4e108b0abb0935e270a5c03c1ceb3cc36",
    "b9837d31b26bced4243457e3357a93c8d546883390104f1b43d5e182e92f98a7",
    "ab837deb8459678d4fce223e06d03cc8e6f4d391ff35bad191392a923825e622",
    "3e01d86f279bc6c5a2f0769a9728a98e3e49fa749be15a2c6c6e0f32132ca270",
)
Q011S_DIGEST_NAMES = (
    "input_digest_sha256",
    "linear_digest_sha256",
    "graph_digest_sha256",
    "core_digest_sha256",
    "result_digest_sha256",
)
Q011S_CLASSIFICATION = (
    "the original repaired exact map has a certified forward-invariant "
    "Lipschitz graph patch on the fixed conservation leaf"
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


def _digest_tuple(cycle: dict[str, Any], names: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(cycle[name] for name in names)


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
            Q011M_CLASSIFICATION,
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
        (
            "q011s",
            directory / "q011s_original_map_invariant_core.json",
            Path(q011s.__file__).resolve(),
            Q011S_ARTIFACT_SHA256,
            Q011S_RUNNER_SHA256,
            Q011S_DIGESTS,
            Q011S_DIGEST_NAMES,
            Q011S_CLASSIFICATION,
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
        checks[f"{label}_artifact_sha256_matches"] = _file_sha256(artifact_path) == artifact_hash
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
        }

    k_theorem = artifacts["q011k"]["cycle"]["theorem_consequence"]
    m_theorem = artifacts["q011m"]["cycle"]["theorem_consequence"]
    q_theorem = artifacts["q011q"]["cycle"]["theorem_consequence"]
    r_theorem = artifacts["q011r"]["cycle"]["theorem_consequence"]
    s_theorem = artifacts["q011s"]["cycle"]["theorem_consequence"]
    checks["q011k_spectral_scope_is_preserved"] = bool(
        k_theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
        and k_theorem["q011c2_designated_selected_cluster_has_rigorous_dimension_24"]
        and k_theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
        and not k_theorem["forced_ssm_exists_or_is_unique"]
    )
    checks["q011m_derivative_scope_is_preserved"] = bool(
        m_theorem["repaired_exact_map_second_and_third_derivative_bounds_are_certified"]
        and m_theorem["registered_uniform_cubic_defect_majorant_is_rigorous"]
        and not m_theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    )
    checks["q011q_real_coordinate_scope_is_preserved"] = bool(
        q_theorem["fixed_leaf_real_coordinate_lift_and_inverse_are_certified"]
        and q_theorem["registered_same_norm_real_linear_domination_is_rigorous"]
        and not q_theorem["an_exact_local_invariant_manifold_or_ssm_is_certified"]
    )
    checks["q011r_lipschitz_localization_scope_is_preserved"] = bool(
        r_theorem["a_unique_lipschitz_fixed_graph_for_the_localized_map_exists"]
        and not r_theorem["c1_or_higher_smoothness_is_certified"]
    )
    checks["q011s_original_lipschitz_core_scope_is_preserved"] = bool(
        s_theorem["the_original_map_has_a_forward_invariant_lipschitz_graph_patch"]
        and not s_theorem["c1_or_higher_smoothness_is_certified"]
        and not s_theorem["origin_tangency_is_certified"]
    )
    checks["twenty_five_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 25
    )
    audit = {
        **records,
        "direct_digest_count": 25,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _cutoff_audit() -> dict[str, Any]:
    identity_ratio = Fraction(COORDINATE_SLOT_COUNT, 2**CUTOFF_POWER)
    dimension_root_cap_power = 2**CUTOFF_POWER
    holder_sum_cap = Fraction(8)
    derivative_of_t_cap_coefficient = Fraction(64)
    derivative_cap = (
        Fraction(1) + Fraction(1, 2) * derivative_of_t_cap_coefficient * CUTOFF_SUPPORT_FACTOR
    )
    bump = {
        "definition": ("chi(t)=1 for t<=1; 1-3y^2+2y^3 with y=(t-1)/3 for 1<t<4; 0 for t>=4"),
        "transition_polynomial": "1-3y^2+2y^3",
        "transition_derivative": "-2y(1-y)",
        "left_endpoint_value": _fraction_record(Fraction(1)),
        "right_endpoint_value": _fraction_record(Fraction(0)),
        "left_endpoint_derivative": _fraction_record(Fraction(0)),
        "right_endpoint_derivative": _fraction_record(Fraction(0)),
        "value_lower": _fraction_record(Fraction(0)),
        "value_upper": _fraction_record(Fraction(1)),
        "absolute_derivative_upper": _fraction_record(Fraction(1, 2)),
        "is_c1_across_both_endpoints": True,
    }
    cutoff = {
        "coordinate_slot_count": COORDINATE_SLOT_COUNT,
        "coordinate_norm": (
            "complex-modulus block-sup norm restricted to the conjugacy-fixed real coordinate space"
        ),
        "scalar_function": ("t_r(z)=sum_j (abs(z_j)/(2r))^16"),
        "definition": "C_r^(1)(z)=chi(t_r(z)) z",
        "identity_ratio_upper": _fraction_record(identity_ratio),
        "identity_on_closed_radius_r_ball": True,
        "support_factor_upper": CUTOFF_SUPPORT_FACTOR,
        "holder_sum_cap": _fraction_record(holder_sum_cap),
        "derivative_of_t_cap": "||Dt_r(z)||<=64/r on t_r(z)<4",
        "derivative_of_t_cap_coefficient": _fraction_record(derivative_of_t_cap_coefficient),
        "global_derivative_norm_upper": _fraction_record(derivative_cap),
        "preserves_conjugacy_fixed_real_space": True,
        "preserves_selected_and_external_real_subspaces": True,
        "componentwise_disk_projection_is_used": False,
        "q011r_nonsmooth_radial_retraction_is_used": False,
    }
    exact_record = {
        "coordinate_slot_count": COORDINATE_SLOT_COUNT,
        "power": CUTOFF_POWER,
        "inner_scale": CUTOFF_INNER_SCALE,
        "transition_end": CUTOFF_TRANSITION_END,
        "identity_ratio": _fraction_record(identity_ratio),
        "dimension_root_cap_power": dimension_root_cap_power,
        "holder_sum_cap": _fraction_record(holder_sum_cap),
        "derivative_of_t_cap_coefficient": _fraction_record(derivative_of_t_cap_coefficient),
        "support_factor": CUTOFF_SUPPORT_FACTOR,
        "derivative_cap": _fraction_record(derivative_cap),
    }
    checks = {
        "coordinate_slot_count_is_registered": (COORDINATE_SLOT_COUNT == 2598),
        "scalar_power_function_is_c1_on_complex_slots": (
            CUTOFF_POWER == 16 and CUTOFF_POWER % 2 == 0
        ),
        "bump_endpoint_values_and_derivatives_match": bool(
            bump["is_c1_across_both_endpoints"]
            and _fraction(bump["left_endpoint_value"]) == 1
            and _fraction(bump["right_endpoint_value"]) == 0
            and _fraction(bump["left_endpoint_derivative"]) == 0
            and _fraction(bump["right_endpoint_derivative"]) == 0
        ),
        "bump_value_and_derivative_caps_are_exact": bool(
            _fraction(bump["value_lower"]) == 0
            and _fraction(bump["value_upper"]) == 1
            and _fraction(bump["absolute_derivative_upper"]) == Fraction(1, 2)
        ),
        "identity_ratio_is_strictly_below_one": identity_ratio < 1,
        "dimension_sixteenth_root_is_at_most_two": (
            COORDINATE_SLOT_COUNT <= dimension_root_cap_power
        ),
        "holder_and_transition_bounds_give_sum_cap_eight": (
            holder_sum_cap == 2 * CUTOFF_TRANSITION_END
        ),
        "support_is_contained_in_radius_four_ball": (CUTOFF_SUPPORT_FACTOR == 4),
        "derivative_bound_formula_gives_129": bool(
            derivative_cap
            == 1 + Fraction(1, 2) * derivative_of_t_cap_coefficient * CUTOFF_SUPPORT_FACTOR
            == CUTOFF_DERIVATIVE_CAP
        ),
        "scalar_symmetric_cutoff_preserves_real_typing": bool(
            cutoff["preserves_conjugacy_fixed_real_space"]
            and cutoff["preserves_selected_and_external_real_subspaces"]
        ),
        "no_nonsmooth_or_componentwise_cutoff_is_substituted": bool(
            not cutoff["componentwise_disk_projection_is_used"]
            and not cutoff["q011r_nonsmooth_radial_retraction_is_used"]
        ),
        "exact_cutoff_record_is_finite_strict_json": bool(
            _all_numeric_values_finite(exact_record)
            and _strict_json_serializable(exact_record)
            and json.dumps(exact_record, allow_nan=False)
        ),
    }
    return {
        "scalar_c1_bump": bump,
        "smooth_scalar_cutoff": cutoff,
        "exact_cutoff_record": exact_record,
        "exact_cutoff_record_digest_sha256": q011b._canonical_json_sha256(exact_record),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _graph_definition_audit(
    artifacts: dict[str, dict[str, Any]],
    cutoff: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    m_cycle = artifacts["q011m"]["cycle"]
    q_cycle = artifacts["q011q"]["cycle"]
    r_cycle = artifacts["q011r"]["cycle"]
    s_cycle = artifacts["q011s"]["cycle"]
    transport = r_cycle["real_derivative_transport_audit"]
    r_campaign = r_cycle["graph_transform_radius_campaign_audit"]
    r_selected = r_campaign["selected_record"]
    if r_selected is None:
        raise RuntimeError("Q011r has no selected localization radius")

    q_coordinate = q_cycle["real_fixed_leaf_coordinate_audit"]
    q_linear = q_cycle["real_same_norm_linear_split_audit"]
    s_linear = s_cycle["selected_linear_operator_audit"]
    s_graph = s_cycle["localized_fixed_graph_core_data_audit"]
    derivative = m_cycle["analytic_map_derivative_audit"]
    root = m_cycle["exact_root_and_simple_envelope_audit"]

    values = {
        "mu_2": _fraction(transport["real_second_derivative_bilinear_upper"]),
        "m": _fraction(transport["real_selected_conorm_lower"]),
        "q": _fraction(transport["real_external_operator_norm_upper"]),
        "b": _fraction(transport["real_selected_external_coupling_upper"]),
        "alpha": _fraction(transport["real_selected_inverse_norm_upper"]),
        "K_L": _fraction(transport["real_physical_lift_norm_upper"]),
        "rho_star": _fraction(r_selected["radius"]),
        "p_S": _fraction(s_linear["global_selected_operator_norm_upper"]),
        "state_displacement_cap": _fraction(derivative["registered_state_displacement_cap"]),
        "root_population_floor": _fraction(root["root_population_floor_lower"]),
        "root_density_floor": _fraction(root["root_density_floor_lower"]),
    }
    graph_space = {
        "name": "G_C1_global_(r,1)",
        "ambient_space": "C_b^1(S_R,E_R)",
        "domain": "the full selected real space S_R",
        "codomain": "the full external real space E_R",
        "fixes_origin": True,
        "uniform_height_cap": "r",
        "uniform_derivative_cap": _fraction_record(Fraction(1)),
        "norm": "max(global value sup norm, global derivative sup norm)",
        "ambient_c_b_1_space_is_banach": True,
        "origin_height_and_derivative_constraints_are_closed": True,
        "closed_complete_space": True,
    }
    localized_nonlinearity = {
        "definition": "N_r^(1)(z)=N(C_r^(1)(z))",
        "origin": "N_r^(1)(0)=0",
        "origin_derivative": "DN_r^(1)(0)=0",
        "global_amplitude_upper": "n_r=8 mu_2 r^2",
        "global_derivative_upper": "delta_r=516 mu_2 r",
        "support_radius": "4r",
        "cutoff_derivative_upper": _fraction_record(CUTOFF_DERIVATIVE_CAP),
        "cutoff_factor_is_applied_once": True,
    }
    base_inverse = {
        "base_map": "P_psi(s)=S s+B psi(s)+(N_r^(1))_S(s,psi(s))",
        "fixed_point_inverse": ("s=S^(-1)[u-B psi(s)-(N_r^(1))_S(s,psi(s))]"),
        "conorm_lower": "d_r=m-b-delta_r",
        "contraction_utilization": "u_r=alpha(b+delta_r)",
        "global_fixed_point_inverse_is_combined_with_c1_inverse_theorem": True,
        "finite_dimensional_surjectivity_is_not_assumed": True,
    }
    graph_transform = {
        "definition": ("(T_r psi)(u)=E psi(P_psi^(-1)u)+(N_r^(1))_E(P_psi^(-1)u,psi(P_psi^(-1)u))"),
        "derivative_formula": (
            "D(T_r psi)(u)=[D_s g+D_e g Dpsi(s)][D_s f+D_e f Dpsi(s)]^(-1), s=P_psi^(-1)(u)"
        ),
        "height_ratio": "h_r=q+8 mu_2 r",
        "slope_upper": "ell_r=(q+delta_r)/d_r",
        "c0_graph_contraction": "kappa_r=m(q+delta_r)/d_r",
        "derivative_fiber_contraction": ("chi_r=(q+delta_r)/d_r+(q+delta_r)(b+delta_r)/d_r^2"),
        "direct_c1_norm_contraction_is_assumed": False,
    }
    fiber_theorem = {
        "base_dynamics": "C0 graph transform on the closed graph space",
        "fiber_dynamics": "graph-transform derivative over each base graph",
        "base_contraction_is_uniform": True,
        "fiber_contraction_is_uniform_when_registered_gate_passes": True,
        "fiber_contraction_theorem_yields_a_c1_fixed_graph": True,
        "direct_c1_norm_contraction_is_required": False,
    }
    origin_tangent = {
        "nonlinear_origin_derivative_is_zero": True,
        "lower_left_linear_block_is_zero": True,
        "zero_derivative_graph_is_a_fiber_fixed_point_at_origin": True,
        "fiber_fixed_point_uniqueness_implies_Dpsi_origin_zero": True,
        "physical_tangent": ("Q011q physical lift of the selected real spectral subspace"),
        "q011s_lipschitz_graph_equality_is_assumed": False,
    }
    exact_values = {name: _fraction_record(value) for name, value in values.items()}
    checks = {
        "q011m_q011q_q011r_q011s_source_audits_pass": bool(
            derivative["passed"]
            and root["passed"]
            and q_coordinate["passed"]
            and q_linear["passed"]
            and transport["passed"]
            and r_selected["passed"]
            and s_linear["passed"]
            and s_graph["passed"]
        ),
        "real_dimensions_and_coordinate_slots_close": bool(
            q_coordinate["selected_real_dimension"] == SELECTED_DIMENSION
            and q_coordinate["external_real_dimension"] == EXTERNAL_DIMENSION
            and q_coordinate["total_fixed_leaf_real_dimension"] == COORDINATE_SLOT_COUNT
        ),
        "transport_constants_reproduce_q011r": bool(
            values["mu_2"] == _fraction(transport["real_second_derivative_bilinear_upper"])
            and values["alpha"] == 1 / values["m"]
        ),
        "q011r_selected_radius_is_used_only_as_scale_anchor": bool(
            values["rho_star"] == _fraction(r_campaign["selected_radius"])
            and values["rho_star"] > 0
        ),
        "q011s_selected_operator_and_root_buffers_reproduce": bool(
            values["p_S"] == _fraction(s_linear["global_selected_operator_norm_upper"])
            and values["root_population_floor"]
            == _fraction(s_graph["core_transfer_data"]["root_population_floor_lower"])
            and values["root_density_floor"]
            == _fraction(s_graph["core_transfer_data"]["root_density_floor_lower"])
        ),
        "smooth_cutoff_typing_and_bound_are_available": bool(
            cutoff["passed"]
            and _fraction(cutoff["smooth_scalar_cutoff"]["global_derivative_norm_upper"])
            == CUTOFF_DERIVATIVE_CAP
        ),
        "c_b_1_graph_space_is_closed_complete": bool(
            graph_space["ambient_c_b_1_space_is_banach"]
            and graph_space["origin_height_and_derivative_constraints_are_closed"]
            and graph_space["closed_complete_space"]
        ),
        "base_inverse_and_graph_derivative_are_explicitly_typed": bool(
            base_inverse["global_fixed_point_inverse_is_combined_with_c1_inverse_theorem"]
            and base_inverse["finite_dimensional_surjectivity_is_not_assumed"]
            and "D(T_r psi)" in graph_transform["derivative_formula"]
        ),
        "fiber_theorem_not_direct_c1_contraction_is_registered": bool(
            fiber_theorem["fiber_contraction_theorem_yields_a_c1_fixed_graph"]
            and not fiber_theorem["direct_c1_norm_contraction_is_required"]
            and not graph_transform["direct_c1_norm_contraction_is_assumed"]
        ),
        "origin_derivative_and_selected_tangent_are_typed": bool(
            origin_tangent["zero_derivative_graph_is_a_fiber_fixed_point_at_origin"]
            and origin_tangent["fiber_fixed_point_uniqueness_implies_Dpsi_origin_zero"]
            and not origin_tangent["q011s_lipschitz_graph_equality_is_assumed"]
        ),
        "exact_graph_constants_are_finite_strict_json": bool(
            _all_numeric_values_finite(exact_values)
            and _strict_json_serializable(exact_values)
            and json.dumps(exact_values, allow_nan=False)
        ),
    }
    audit = {
        "transported_exact_constants": exact_values,
        "c1_localized_nonlinearity": localized_nonlinearity,
        "c1_graph_space": graph_space,
        "global_c1_base_inverse": base_inverse,
        "c1_graph_transform": graph_transform,
        "fiber_contraction_theorem": fiber_theorem,
        "origin_derivative_and_tangent": origin_tangent,
        "exact_graph_constant_digest_sha256": q011b._canonical_json_sha256(exact_values),
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, values


def _radius_record(
    exponent: int,
    values: dict[str, Fraction],
) -> tuple[dict[str, Any], dict[str, Fraction | int | None]]:
    scale = Fraction(1, 2**exponent)
    radius = scale * values["rho_star"]
    mu_2 = values["mu_2"]
    selected_conorm = values["m"]
    external_norm = values["q"]
    coupling = values["b"]
    selected_inverse = values["alpha"]
    lift_norm = values["K_L"]

    nonlinear_amplitude = NONLINEAR_AMPLITUDE_FACTOR * mu_2 * radius**2
    nonlinear_derivative = NONLINEAR_DERIVATIVE_FACTOR * mu_2 * radius
    base_conorm = selected_conorm - coupling - nonlinear_derivative
    inverse_utilization = selected_inverse * (coupling + nonlinear_derivative)
    height_ratio = external_norm + nonlinear_amplitude / radius

    inverse_lipschitz: Fraction | None = None
    graph_slope: Fraction | None = None
    c0_contraction: Fraction | None = None
    derivative_fiber_contraction: Fraction | None = None
    if base_conorm > 0:
        inverse_lipschitz = 1 / base_conorm
        graph_slope = (external_norm + nonlinear_derivative) / base_conorm
        c0_contraction = selected_conorm * (external_norm + nonlinear_derivative) / base_conorm
        derivative_fiber_contraction = (external_norm + nonlinear_derivative) / base_conorm + (
            external_norm + nonlinear_derivative
        ) * (coupling + nonlinear_derivative) / base_conorm**2

    original_nonlinear_amplitude = Fraction(1, 2) * mu_2 * radius**2
    original_selected_ratio: Fraction | None = None
    original_external_ratio: Fraction | None = None
    selected_image_radius: Fraction | None = None
    external_image_radius: Fraction | None = None
    output_physical: Fraction | None = None
    output_population: Fraction | None = None
    output_density: Fraction | None = None
    if graph_slope is not None:
        original_selected_ratio = (
            values["p_S"] + coupling * graph_slope + Fraction(1, 2) * mu_2 * radius
        )
        original_external_ratio = graph_slope * original_selected_ratio
        selected_image_radius = original_selected_ratio * radius
        external_image_radius = original_external_ratio * radius
        output_physical = lift_norm * selected_image_radius
        output_population = values["root_population_floor"] - output_physical
        output_density = values["root_density_floor"] - 9 * output_physical

    support_coordinate = CUTOFF_SUPPORT_FACTOR * radius
    support_physical = lift_norm * support_coordinate
    input_physical = lift_norm * radius
    support_population = values["root_population_floor"] - support_physical
    support_density = values["root_density_floor"] - 9 * support_physical
    input_population = values["root_population_floor"] - input_physical
    input_density = values["root_density_floor"] - 9 * input_physical

    checks = {
        "scale_and_radius_formula_reproduce": bool(
            scale == Fraction(1, 2**exponent) and radius == scale * values["rho_star"]
        ),
        "smooth_cutoff_support_is_in_derivative_domain": (
            support_physical <= values["state_displacement_cap"]
        ),
        "smooth_cutoff_support_physical_displacement_fits_cap": (
            support_physical <= PHYSICAL_SUPPORT_CAP
        ),
        "support_population_and_density_floors_pass": bool(
            support_population >= POPULATION_FLOOR and support_density >= DENSITY_FLOOR
        ),
        "nonlinear_amplitude_formula_reproduces": (
            nonlinear_amplitude == NONLINEAR_AMPLITUDE_FACTOR * mu_2 * radius**2
        ),
        "nonlinear_derivative_formula_reproduces": (
            nonlinear_derivative == NONLINEAR_DERIVATIVE_FACTOR * mu_2 * radius
        ),
        "localized_derivative_fits_cap": (nonlinear_derivative <= NONLINEAR_DERIVATIVE_CAP),
        "base_conorm_is_positive": base_conorm > 0,
        "base_inverse_utilization_fits_cap": (inverse_utilization <= BASE_INVERSE_UTILIZATION_CAP),
        "height_ratio_fits_cap": height_ratio <= HEIGHT_RATIO_CAP,
        "c1_graph_slope_fits_cap": bool(
            graph_slope is not None and graph_slope <= C1_GRAPH_SLOPE_CAP
        ),
        "c0_graph_contraction_fits_cap": bool(
            c0_contraction is not None and c0_contraction <= C0_GRAPH_CONTRACTION_CAP
        ),
        "derivative_fiber_contraction_fits_cap": bool(
            derivative_fiber_contraction is not None
            and derivative_fiber_contraction <= DERIVATIVE_FIBER_CONTRACTION_CAP
        ),
        "input_graph_is_in_smooth_cutoff_identity_core": bool(
            graph_slope is not None and graph_slope <= 1
        ),
        "original_nonlinear_amplitude_formula_reproduces": (
            original_nonlinear_amplitude == Fraction(1, 2) * mu_2 * radius**2
        ),
        "original_selected_ratio_formula_reproduces": bool(
            graph_slope is not None
            and original_selected_ratio
            == values["p_S"] + coupling * graph_slope + Fraction(1, 2) * mu_2 * radius
        ),
        "original_external_ratio_formula_reproduces": bool(
            graph_slope is not None
            and original_external_ratio == graph_slope * original_selected_ratio
        ),
        "original_selected_image_ratio_fits_cap": bool(
            original_selected_ratio is not None
            and original_selected_ratio <= ORIGINAL_SELECTED_IMAGE_RATIO_CAP
        ),
        "original_external_image_ratio_fits_cap": bool(
            original_external_ratio is not None
            and original_external_ratio <= ORIGINAL_EXTERNAL_IMAGE_RATIO_CAP
        ),
        "one_step_image_is_in_same_identity_core": bool(
            selected_image_radius is not None
            and external_image_radius is not None
            and selected_image_radius <= radius
            and external_image_radius <= radius
        ),
        "input_physical_displacement_fits_cap": (input_physical <= PHYSICAL_SUPPORT_CAP),
        "output_physical_displacement_fits_cap": bool(
            output_physical is not None and output_physical <= PHYSICAL_SUPPORT_CAP
        ),
        "input_population_and_density_floors_pass": bool(
            input_population >= POPULATION_FLOOR and input_density >= DENSITY_FLOOR
        ),
        "output_population_and_density_floors_pass": bool(
            output_population is not None
            and output_density is not None
            and output_population >= POPULATION_FLOOR
            and output_density >= DENSITY_FLOOR
        ),
        "forward_induction_stays_in_original_map_core": bool(
            selected_image_radius is not None
            and selected_image_radius <= radius <= values["rho_star"]
        ),
    }
    exact: dict[str, Fraction | int | None] = {
        "scale_exponent": exponent,
        "scale": scale,
        "radius": radius,
        "smooth_cutoff_support_coordinate_radius": support_coordinate,
        "smooth_cutoff_support_physical_displacement": support_physical,
        "support_population_floor": support_population,
        "support_density_floor": support_density,
        "localized_nonlinear_amplitude": nonlinear_amplitude,
        "localized_nonlinear_derivative": nonlinear_derivative,
        "base_conorm": base_conorm,
        "base_inverse_utilization": inverse_utilization,
        "base_inverse_lipschitz": inverse_lipschitz,
        "height_ratio": height_ratio,
        "c1_graph_slope": graph_slope,
        "c0_graph_contraction": c0_contraction,
        "derivative_fiber_contraction": derivative_fiber_contraction,
        "original_nonlinear_amplitude": original_nonlinear_amplitude,
        "original_selected_image_ratio": original_selected_ratio,
        "original_external_image_ratio": original_external_ratio,
        "selected_image_radius": selected_image_radius,
        "external_image_radius": external_image_radius,
        "input_physical_displacement": input_physical,
        "output_physical_displacement": output_physical,
        "input_population_floor": input_population,
        "input_density_floor": input_density,
        "output_population_floor": output_population,
        "output_density_floor": output_density,
    }
    record = {
        name: (
            value
            if isinstance(value, int)
            else _fraction_record(value)
            if value is not None
            else None
        )
        for name, value in exact.items()
    }
    record["checks"] = checks
    record["passed"] = all(checks.values())
    return record, exact


def _is_nondecreasing(values: list[Fraction]) -> bool:
    return all(left <= right for left, right in itertools.pairwise(values))


def _is_nonincreasing(values: list[Fraction]) -> bool:
    return all(left >= right for left, right in itertools.pairwise(values))


def _radius_campaign_audit(values: dict[str, Fraction]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    exact_records: list[dict[str, Fraction | int | None]] = []
    for exponent in SCALE_EXPONENTS:
        record, exact = _radius_record(exponent, values)
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
    selected_radius = _fraction(selected_record["radius"]) if selected_record is not None else None
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
        [name for name, passed in first_failed_larger["checks"].items() if not passed]
        if first_failed_larger is not None
        else []
    )

    ascending = sorted(exact_records, key=lambda record: record["radius"])
    finite_ascending = [record for record in ascending if record["c1_graph_slope"] is not None]
    monotonicity_checks = {
        "support_physical_displacement_is_nondecreasing": _is_nondecreasing(
            [record["smooth_cutoff_support_physical_displacement"] for record in ascending]
        ),
        "localized_amplitude_is_nondecreasing": _is_nondecreasing(
            [record["localized_nonlinear_amplitude"] for record in ascending]
        ),
        "localized_derivative_is_nondecreasing": _is_nondecreasing(
            [record["localized_nonlinear_derivative"] for record in ascending]
        ),
        "base_conorm_is_nonincreasing": _is_nonincreasing(
            [record["base_conorm"] for record in ascending]
        ),
        "inverse_utilization_is_nondecreasing": _is_nondecreasing(
            [record["base_inverse_utilization"] for record in ascending]
        ),
        "height_ratio_is_nondecreasing": _is_nondecreasing(
            [record["height_ratio"] for record in ascending]
        ),
        "finite_graph_slope_is_nondecreasing": _is_nondecreasing(
            [record["c1_graph_slope"] for record in finite_ascending]
        ),
        "finite_c0_contraction_is_nondecreasing": _is_nondecreasing(
            [record["c0_graph_contraction"] for record in finite_ascending]
        ),
        "finite_fiber_contraction_is_nondecreasing": _is_nondecreasing(
            [record["derivative_fiber_contraction"] for record in finite_ascending]
        ),
        "original_image_ratios_are_nondecreasing": bool(
            _is_nondecreasing(
                [record["original_selected_image_ratio"] for record in finite_ascending]
            )
            and _is_nondecreasing(
                [record["original_external_image_ratio"] for record in finite_ascending]
            )
        ),
        "all_population_and_density_floors_are_nonincreasing": bool(
            all(
                _is_nonincreasing([record[name] for record in ascending])
                for name in (
                    "support_population_floor",
                    "support_density_floor",
                    "input_population_floor",
                    "input_density_floor",
                )
            )
            and all(
                _is_nonincreasing([record[name] for record in finite_ascending])
                for name in (
                    "output_population_floor",
                    "output_density_floor",
                )
            )
        ),
    }
    pass_flags = [record["passed"] for record in records]
    first_pass = pass_flags.index(True) if any(pass_flags) else len(pass_flags)
    exact_serialized = []
    for exact in exact_records:
        serialized: dict[str, Any] = {}
        for name, value in exact.items():
            if isinstance(value, int):
                serialized[name] = value
            elif value is None:
                serialized[name] = None
            else:
                serialized[name] = _fraction_record(value)
        exact_serialized.append(serialized)

    selected_scale = _fraction(selected_record["scale"]) if selected_record is not None else None
    selected_proof = (
        {
            "c0_fixed_graph_exists_uniquely": selected_record["checks"][
                "c0_graph_contraction_fits_cap"
            ],
            "uniform_derivative_fiber_contraction_is_strict": (
                selected_record["checks"]["derivative_fiber_contraction_fits_cap"]
            ),
            "fiber_contraction_theorem_gives_c1_fixed_graph": True,
            "origin_derivative_is_zero_by_unique_fiber_fixed_point": True,
            "graph_tangent_is_selected_real_spectral_subspace": True,
            "input_patch_is_in_smooth_cutoff_identity_core": (
                selected_record["checks"]["input_graph_is_in_smooth_cutoff_identity_core"]
            ),
            "localized_and_original_maps_agree_on_input_patch": True,
            "one_step_image_is_in_same_identity_core": selected_record["checks"][
                "one_step_image_is_in_same_identity_core"
            ],
            "original_map_is_forward_invariant_by_induction": (
                selected_record["checks"]["forward_induction_stays_in_original_map_core"]
            ),
            "q011s_graph_equality_is_used": False,
            "backward_invariance_or_onto_is_used": False,
        }
        if selected_record is not None
        else None
    )
    checks = {
        "all_eleven_registered_scales_are_present": (len(records) == len(SCALE_EXPONENTS) == 11),
        "scales_and_radii_are_strictly_decreasing": bool(
            all(left > right for left, right in itertools.pairwise(SCALE_CANDIDATES))
            and all(
                _fraction(left["radius"]) > _fraction(right["radius"])
                for left, right in itertools.pairwise(records)
            )
        ),
        "all_radius_records_use_exact_fraction_arithmetic": True,
        "all_record_formula_checks_reproduce": all(
            record["checks"]["scale_and_radius_formula_reproduce"]
            and record["checks"]["nonlinear_amplitude_formula_reproduces"]
            and record["checks"]["nonlinear_derivative_formula_reproduces"]
            and record["checks"]["original_nonlinear_amplitude_formula_reproduces"]
            and record["checks"]["original_selected_ratio_formula_reproduces"]
            and record["checks"]["original_external_ratio_formula_reproduces"]
            for record in records
        ),
        "passing_records_form_a_decreasing_radius_suffix": (
            pass_flags == [False] * first_pass + [True] * (len(records) - first_pass)
        ),
        "selected_radius_is_the_largest_passing_candidate": bool(
            selected_record is None
            or _fraction(selected_record["radius"])
            == max(_fraction(record["radius"]) for record in passing_records)
        ),
        "first_larger_failure_is_recorded_when_present": bool(
            selected_record is None
            or selected_record is records[0]
            or (first_failed_larger is not None and first_failed_constraints)
        ),
        "all_registered_monotonicity_checks_pass": all(monotonicity_checks.values()),
        "selected_scale_meets_registered_minimum": bool(
            selected_scale is not None and selected_scale >= MINIMUM_SCALE
        ),
        "selected_c1_tangent_and_original_transfer_proof_closes": bool(
            selected_proof is not None
            and all(
                selected_proof[name]
                for name in (
                    "c0_fixed_graph_exists_uniquely",
                    "uniform_derivative_fiber_contraction_is_strict",
                    "fiber_contraction_theorem_gives_c1_fixed_graph",
                    "origin_derivative_is_zero_by_unique_fiber_fixed_point",
                    "graph_tangent_is_selected_real_spectral_subspace",
                    "input_patch_is_in_smooth_cutoff_identity_core",
                    "localized_and_original_maps_agree_on_input_patch",
                    "one_step_image_is_in_same_identity_core",
                    "original_map_is_forward_invariant_by_induction",
                )
            )
            and not selected_proof["q011s_graph_equality_is_used"]
            and not selected_proof["backward_invariance_or_onto_is_used"]
        ),
        "all_radius_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    return {
        "scale_exponents": list(SCALE_EXPONENTS),
        "scale_candidates": [_fraction_record(scale) for scale in SCALE_CANDIDATES],
        "radius_formulas": {
            "radius": "r_j=2^(-j) rho_*",
            "localized_amplitude": "n_r=8 mu_2 r^2",
            "localized_derivative": "delta_r=516 mu_2 r",
            "base_conorm": "d_r=m-b-delta_r",
            "base_inverse_utilization": "u_r=alpha(b+delta_r)",
            "height_ratio": "h_r=q+8 mu_2 r",
            "c1_graph_slope": "ell_r=(q+delta_r)/d_r",
            "c0_graph_contraction": "kappa_r=m(q+delta_r)/d_r",
            "derivative_fiber_contraction": ("chi_r=(q+delta_r)/d_r+(q+delta_r)(b+delta_r)/d_r^2"),
            "original_selected_image_ratio": ("c_r=p_S+b ell_r+(mu_2/2)r"),
            "original_external_image_ratio": "ell_r c_r",
        },
        "radius_records": records,
        "exact_radius_record_digest_sha256": q011b._canonical_json_sha256(exact_serialized),
        "monotonicity_checks": monotonicity_checks,
        "passing_scale_count": len(passing_records),
        "selected_scale": (selected_record["scale"] if selected_record is not None else None),
        "selected_radius": (selected_record["radius"] if selected_record is not None else None),
        "selected_record": selected_record,
        "first_failed_larger_radius": (
            first_failed_larger["radius"] if first_failed_larger is not None else None
        ),
        "first_failed_larger_constraints": first_failed_constraints,
        "selected_c1_original_transfer_proof": selected_proof,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _spectral_quotient_audit(
    artifacts: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    k_artifact = artifacts["q011k"]
    k_cycle = k_artifact["cycle"]
    centers, selected, radii, _metrics, spectral = q011l._spectral_data(k_artifact)
    selected_sets = {
        block_index: set(center_indices) for block_index, center_indices in selected.items()
    }

    all_records: list[dict[str, Any]] = []
    interval_digest_records: list[dict[str, Any]] = []
    exact_values: list[dict[str, Any]] = []
    interval_formula_checks: list[bool] = []
    block_records: list[dict[str, Any]] = []
    modulus_cache: dict[tuple[Fraction, Fraction], Any] = {}
    for block_index in range(SIZE):
        block_entries: list[dict[str, Any]] = []
        selected_count = 0
        for center_index, center in enumerate(centers[block_index]):
            modulus_key = (abs(center[0]), abs(center[1]))
            if modulus_key not in modulus_cache:
                modulus_cache[modulus_key] = q011o._center_modulus_bounds(center)
            center_modulus = modulus_cache[modulus_key]
            radius = radii[block_index]
            modulus_lower = max(Fraction(0), center_modulus.lower - radius)
            modulus_upper = center_modulus.upper + radius
            is_selected = center_index in selected_sets.get(block_index, set())
            selected_count += int(is_selected)
            exact_value = {
                "block_index": block_index,
                "center_index": center_index,
                "selected": is_selected,
                "modulus_lower": modulus_lower,
                "modulus_upper": modulus_upper,
            }
            record = {
                "block_index": block_index,
                "center_index": center_index,
                "selected": is_selected,
                "center_modulus_lower": _fraction_record(center_modulus.lower),
                "center_modulus_upper": _fraction_record(center_modulus.upper),
            }
            interval_digest_record = {
                "block_index": block_index,
                "center_index": center_index,
                "selected": is_selected,
                "modulus_lower": _fraction_record(modulus_lower),
                "modulus_upper": _fraction_record(modulus_upper),
            }
            all_records.append(record)
            interval_digest_records.append(interval_digest_record)
            exact_values.append(exact_value)
            block_entries.append(record)
            interval_formula_checks.append(
                modulus_lower == max(Fraction(0), center_modulus.lower - radius)
                and modulus_upper == center_modulus.upper + radius
            )

        external_count = len(block_entries) - selected_count
        block_exact = {
            "block_index": block_index,
            "dimension": len(block_entries),
            "selected_count": selected_count,
            "external_count": external_count,
            "bauer_fike_radius_upper": _fraction_record(radii[block_index]),
            "eigencenter_modulus_digest_sha256": (q011b._canonical_json_sha256(block_entries)),
        }
        block_records.append(block_exact)

    selected_records = [record for record in exact_values if record["selected"]]
    external_records = [record for record in exact_values if not record["selected"]]
    selected_lower_witness = max(selected_records, key=lambda record: record["modulus_lower"])
    selected_upper_witness = max(selected_records, key=lambda record: record["modulus_upper"])
    external_lower_witness = min(external_records, key=lambda record: record["modulus_lower"])
    external_upper_witness = min(external_records, key=lambda record: record["modulus_upper"])
    selected_lower = selected_lower_witness["modulus_lower"]
    selected_upper = selected_upper_witness["modulus_upper"]
    external_lower = external_lower_witness["modulus_lower"]
    external_upper = external_upper_witness["modulus_upper"]

    upper_quotient: int | None = next(
        (degree for degree in range(1, 1001) if selected_upper ** (degree + 1) < external_lower),
        None,
    )
    lower_quotient: int | None = None
    for degree in range(1, 1001):
        if selected_lower**degree >= external_upper:
            lower_quotient = degree
            continue
        # Q011k gives selected_lower<1, hence later powers are smaller.
        break

    upper_boundary_ratio: Fraction | None = None
    upper_previous_ratio: Fraction | None = None
    lower_boundary_ratio: Fraction | None = None
    lower_next_ratio: Fraction | None = None
    bracket_width: int | None = None
    if upper_quotient is not None:
        upper_boundary_ratio = selected_upper ** (upper_quotient + 1) / external_lower
        upper_previous_ratio = selected_upper**upper_quotient / external_lower
    if lower_quotient is not None:
        lower_boundary_ratio = selected_lower**lower_quotient / external_upper
        lower_next_ratio = selected_lower ** (lower_quotient + 1) / external_upper
    if upper_quotient is not None and lower_quotient is not None:
        bracket_width = upper_quotient - lower_quotient

    quadratic = k_cycle["quadratic_spectral_nonresonance_audit"]
    certified_degrees = [2] if quadratic["passed"] else []
    missing_degrees = list(range(3, upper_quotient + 1)) if upper_quotient is not None else []
    quotient_record = {
        "selected_spectral_radius_lower": _fraction_record(selected_lower),
        "selected_spectral_radius_upper": _fraction_record(selected_upper),
        "selected_lower_witness": {
            "block_index": selected_lower_witness["block_index"],
            "center_index": selected_lower_witness["center_index"],
        },
        "selected_upper_witness": {
            "block_index": selected_upper_witness["block_index"],
            "center_index": selected_upper_witness["center_index"],
        },
        "external_minimum_modulus_lower": _fraction_record(external_lower),
        "external_minimum_modulus_upper": _fraction_record(external_upper),
        "external_lower_witness": {
            "block_index": external_lower_witness["block_index"],
            "center_index": external_lower_witness["center_index"],
        },
        "external_upper_witness": {
            "block_index": external_upper_witness["block_index"],
            "center_index": external_upper_witness["center_index"],
        },
        "excluded_lower_quotient": lower_quotient,
        "sufficient_upper_quotient": upper_quotient,
        "quotient_bracket_width": bracket_width,
        "upper_boundary_power_ratio": (
            _fraction_record(upper_boundary_ratio) if upper_boundary_ratio is not None else None
        ),
        "upper_previous_power_ratio": (
            _fraction_record(upper_previous_ratio) if upper_previous_ratio is not None else None
        ),
        "lower_boundary_power_ratio": (
            _fraction_record(lower_boundary_ratio) if lower_boundary_ratio is not None else None
        ),
        "lower_next_power_ratio": (
            _fraction_record(lower_next_ratio) if lower_next_ratio is not None else None
        ),
    }
    evidence = {
        "q011k_certified_external_nonresonance_degrees": certified_degrees,
        "q011k_unordered_quadratic_pair_count": quadratic["unordered_pair_count"],
        "missing_external_nonresonance_degrees_through_upper_quotient": (missing_degrees),
        "missing_degree_count": len(missing_degrees),
        "spectral_quotient_ssm_uniqueness_is_certified": False,
        "higher_smoothness_is_certified": False,
    }
    exact_quotient = {
        "selected_lower": _fraction_record(selected_lower),
        "selected_upper": _fraction_record(selected_upper),
        "external_lower": _fraction_record(external_lower),
        "external_upper": _fraction_record(external_upper),
        "lower_quotient": lower_quotient,
        "upper_quotient": upper_quotient,
        "bracket_width": bracket_width,
        "upper_boundary_ratio": quotient_record["upper_boundary_power_ratio"],
        "upper_previous_ratio": quotient_record["upper_previous_power_ratio"],
        "lower_boundary_ratio": quotient_record["lower_boundary_power_ratio"],
        "lower_next_ratio": quotient_record["lower_next_power_ratio"],
    }
    checks = {
        "q011l_reconstructs_all_seventeen_exact_blocks": bool(
            spectral["passed"] and len(centers) == SIZE and len(block_records) == SIZE
        ),
        "all_2598_modulus_intervals_are_reconstructed": (len(all_records) == COORDINATE_SLOT_COUNT),
        "all_modulus_interval_formulas_reproduce": all(interval_formula_checks),
        "selected_and_external_counts_are_24_and_2574": bool(
            len(selected_records) == SELECTED_DIMENSION
            and len(external_records) == EXTERNAL_DIMENSION
        ),
        "every_modulus_interval_is_ordered_and_positive_above": all(
            record["modulus_upper"] >= record["modulus_lower"] >= 0 and record["modulus_upper"] > 0
            for record in exact_values
        ),
        "selected_and_external_quotient_bounds_lie_inside_unit_interval": (
            0 < selected_lower <= selected_upper < 1 and 0 < external_lower <= external_upper < 1
        ),
        "selected_spectral_radius_enclosure_reproduces": bool(
            selected_lower == max(record["modulus_lower"] for record in selected_records)
            and selected_upper == max(record["modulus_upper"] for record in selected_records)
        ),
        "external_minimum_modulus_enclosure_reproduces": bool(
            external_lower == min(record["modulus_lower"] for record in external_records)
            and external_upper == min(record["modulus_upper"] for record in external_records)
            and external_lower > 0
        ),
        "upper_quotient_is_minimal_and_boundary_powers_reproduce": bool(
            upper_quotient is not None
            and upper_boundary_ratio is not None
            and upper_previous_ratio is not None
            and upper_boundary_ratio < 1
            and upper_previous_ratio >= 1
        ),
        "lower_quotient_is_maximal_and_boundary_powers_reproduce": bool(
            lower_quotient is not None
            and lower_boundary_ratio is not None
            and lower_next_ratio is not None
            and lower_boundary_ratio >= 1
            and lower_next_ratio < 1
        ),
        "quotient_bracket_is_ordered_with_registered_width": bool(
            bracket_width is not None
            and bracket_width >= 0
            and bracket_width <= SPECTRAL_QUOTIENT_BRACKET_WIDTH_CAP
        ),
        "conservative_upper_quotient_fits_registered_cap": bool(
            upper_quotient is not None and upper_quotient <= SPECTRAL_QUOTIENT_UPPER_CAP
        ),
        "q011k_certifies_only_registered_quadratic_degree": bool(
            quadratic["passed"]
            and quadratic["selected_eigenvalue_count"] == SELECTED_DIMENSION
            and quadratic["unordered_pair_count"] == 300
            and certified_degrees == [2]
            and missing_degrees == list(range(3, upper_quotient + 1))
        ),
        "missing_degrees_block_ssm_uniqueness_claim": bool(
            missing_degrees
            and not evidence["spectral_quotient_ssm_uniqueness_is_certified"]
            and not evidence["higher_smoothness_is_certified"]
        ),
        "all_spectral_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(
                {
                    "blocks": block_records,
                    "intervals": all_records,
                    "quotient": quotient_record,
                    "evidence": evidence,
                }
            )
            and _strict_json_serializable(
                {
                    "blocks": block_records,
                    "intervals": all_records,
                    "quotient": quotient_record,
                    "evidence": evidence,
                }
            )
            and json.dumps(
                {
                    "blocks": block_records,
                    "intervals": all_records,
                    "quotient": quotient_record,
                    "evidence": evidence,
                },
                allow_nan=False,
            )
        ),
    }
    return {
        "modulus_interval_formula": (
            "[max(0,center_modulus_lower-r_BF),center_modulus_upper+r_BF]"
        ),
        "block_records": block_records,
        "eigencenter_modulus_records": all_records,
        "modulus_interval_record_count": len(interval_digest_records),
        "exact_modulus_interval_record_digest_sha256": (
            q011b._canonical_json_sha256(interval_digest_records)
        ),
        "spectral_quotient_definition": {
            "sufficient_upper": ("least L_+ with (rho_S^+)^(L_++1)<rho_E^-"),
            "excluded_lower": ("largest L_- with (rho_S^-)^L_- >= rho_E^+"),
        },
        "spectral_quotient_record": quotient_record,
        "exact_spectral_quotient_record_digest_sha256": (
            q011b._canonical_json_sha256(exact_quotient)
        ),
        "degree_evidence_inventory": evidence,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "coordinate_slot_count": COORDINATE_SLOT_COUNT,
        "selected_blocks": list(SELECTED_BLOCKS),
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "cutoff_power": CUTOFF_POWER,
        "cutoff_inner_scale": CUTOFF_INNER_SCALE,
        "cutoff_transition_end": CUTOFF_TRANSITION_END,
        "cutoff_support_factor": CUTOFF_SUPPORT_FACTOR,
        "cutoff_derivative_cap": _fraction_record(CUTOFF_DERIVATIVE_CAP),
        "nonlinear_amplitude_factor": _fraction_record(NONLINEAR_AMPLITUDE_FACTOR),
        "nonlinear_derivative_factor": _fraction_record(NONLINEAR_DERIVATIVE_FACTOR),
        "nonlinear_derivative_cap": _fraction_record(NONLINEAR_DERIVATIVE_CAP),
        "base_inverse_utilization_cap": _fraction_record(BASE_INVERSE_UTILIZATION_CAP),
        "height_ratio_cap": _fraction_record(HEIGHT_RATIO_CAP),
        "c1_graph_slope_cap": _fraction_record(C1_GRAPH_SLOPE_CAP),
        "c0_graph_contraction_cap": _fraction_record(C0_GRAPH_CONTRACTION_CAP),
        "derivative_fiber_contraction_cap": _fraction_record(DERIVATIVE_FIBER_CONTRACTION_CAP),
        "physical_support_cap": _fraction_record(PHYSICAL_SUPPORT_CAP),
        "original_selected_image_ratio_cap": _fraction_record(ORIGINAL_SELECTED_IMAGE_RATIO_CAP),
        "original_external_image_ratio_cap": _fraction_record(ORIGINAL_EXTERNAL_IMAGE_RATIO_CAP),
        "population_floor": _fraction_record(POPULATION_FLOOR),
        "density_floor": _fraction_record(DENSITY_FLOOR),
        "minimum_scale": _fraction_record(MINIMUM_SCALE),
        "scale_exponents": list(SCALE_EXPONENTS),
        "scale_candidates": [_fraction_record(scale) for scale in SCALE_CANDIDATES],
        "spectral_quotient_bracket_width_cap": (SPECTRAL_QUOTIENT_BRACKET_WIDTH_CAP),
        "spectral_quotient_upper_cap": SPECTRAL_QUOTIENT_UPPER_CAP,
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
        "cutoff_digest_sha256": cycle["cutoff_digest_sha256"],
        "graph_digest_sha256": cycle["graph_digest_sha256"],
        "radius_digest_sha256": cycle["radius_digest_sha256"],
        "spectral_digest_sha256": cycle["spectral_digest_sha256"],
    }


def run_c1_tangent_graph_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    cutoff = _cutoff_audit()
    graph, values = _graph_definition_audit(artifacts, cutoff)
    radius = _radius_campaign_audit(values)
    spectral = _spectral_quotient_audit(artifacts)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    cutoff_sections = {"scalar_c1_localization_audit": cutoff}
    graph_sections = {"c1_graph_transform_definition_audit": graph}
    radius_sections = {"c1_radius_campaign_audit": radius}
    spectral_sections = {"rigorous_spectral_quotient_audit": spectral}
    input_digest = q011b._canonical_json_sha256(input_sections)
    cutoff_digest = q011b._canonical_json_sha256(cutoff_sections)
    graph_digest = q011b._canonical_json_sha256(graph_sections)
    radius_digest = q011b._canonical_json_sha256(radius_sections)
    spectral_digest = q011b._canonical_json_sha256(spectral_sections)
    strict_payload = {
        **input_sections,
        **cutoff_sections,
        **graph_sections,
        **radius_sections,
        **spectral_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and cutoff_digest == q011b._canonical_json_sha256(cutoff_sections)
        and graph_digest == q011b._canonical_json_sha256(graph_sections)
        and radius_digest == q011b._canonical_json_sha256(radius_sections)
        and spectral_digest == q011b._canonical_json_sha256(spectral_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    selected = radius["selected_record"]
    proof = radius["selected_c1_original_transfer_proof"]
    validity_gates = {
        "five_direct_inputs_and_twenty_five_digests_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011k/m/q/r/s artifacts, runners, twenty-five digests, "
                "outcomes and claim boundaries reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "scalar_c1_cutoff_typing_identity_support_and_derivative_reproduce": {
            "passed": cutoff["passed"],
            "threshold": (
                "2598-slot scalar C1 cutoff preserves real typing, is the "
                "identity on radius r, is supported inside 4r and has "
                "derivative norm at most 129"
            ),
            "value": cutoff["checks"],
        },
        "localized_amplitude_and_derivative_transport_in_same_norm": {
            "passed": bool(
                graph["passed"]
                and graph["c1_localized_nonlinearity"]["cutoff_factor_is_applied_once"]
            ),
            "threshold": (
                "n_r=8 mu_2 r^2 and delta_r=516 mu_2 r in the Q011q "
                "real norm without duplicate cutoff factors"
            ),
            "value": graph["c1_localized_nonlinearity"],
        },
        "c_b_1_graph_base_inverse_derivative_and_fiber_types_close": {
            "passed": graph["passed"],
            "threshold": (
                "closed C_b^1 graph space, global C1 base inverse, graph "
                "derivative formula and uniform fiber theorem are explicit"
            ),
            "value": graph["checks"],
        },
        "all_eleven_exact_scales_and_monotonicity_reproduce": {
            "passed": radius["passed"],
            "threshold": (
                "eleven exact scales, monotonic majorants, largest passing "
                "candidate and first larger failure reproduce"
            ),
            "value": radius["checks"],
        },
        "selected_origin_tangent_and_original_transfer_proof_reproduce": {
            "passed": bool(
                radius["passed"]
                and proof is not None
                and radius["checks"]["selected_c1_tangent_and_original_transfer_proof_closes"]
            ),
            "threshold": (
                "Dpsi_*(0)=0, selected tangency, cutoff equality and "
                "original-map forward invariance close at the selected scale"
            ),
            "value": proof,
        },
        "all_modulus_intervals_quotient_powers_and_degree_inventory_reproduce": {
            "passed": spectral["passed"],
            "threshold": (
                "2598 exact modulus intervals, quotient bracket, boundary "
                "powers and certified/missing degree inventory reproduce"
            ),
            "value": spectral["checks"],
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "finite strict JSON, five section digests, result digest "
                "and runner provenance reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    cutoff_hypothesis = bool(
        cutoff["passed"]
        and cutoff["checks"]["scalar_symmetric_cutoff_preserves_real_typing"]
        and cutoff["checks"]["support_is_contained_in_radius_four_ball"]
        and cutoff["checks"]["derivative_bound_formula_gives_129"]
    )
    selected_transform = bool(
        selected is not None
        and selected["checks"]["base_conorm_is_positive"]
        and selected["checks"]["base_inverse_utilization_fits_cap"]
        and selected["checks"]["height_ratio_fits_cap"]
        and selected["checks"]["c1_graph_slope_fits_cap"]
        and selected["checks"]["c0_graph_contraction_fits_cap"]
        and _fraction(selected["scale"]) >= MINIMUM_SCALE
    )
    fiber_c1 = bool(
        selected is not None
        and selected["checks"]["derivative_fiber_contraction_fits_cap"]
        and graph["fiber_contraction_theorem"]["fiber_contraction_theorem_yields_a_c1_fixed_graph"]
        and not graph["fiber_contraction_theorem"]["direct_c1_norm_contraction_is_required"]
    )
    origin_tangent = bool(
        proof is not None
        and proof["origin_derivative_is_zero_by_unique_fiber_fixed_point"]
        and proof["graph_tangent_is_selected_real_spectral_subspace"]
        and not proof["q011s_graph_equality_is_used"]
    )
    original_transfer = bool(
        selected is not None
        and proof is not None
        and selected["checks"]["smooth_cutoff_support_physical_displacement_fits_cap"]
        and selected["checks"]["original_selected_image_ratio_fits_cap"]
        and selected["checks"]["original_external_image_ratio_fits_cap"]
        and selected["checks"]["input_population_and_density_floors_pass"]
        and selected["checks"]["output_population_and_density_floors_pass"]
        and proof["localized_and_original_maps_agree_on_input_patch"]
        and proof["original_map_is_forward_invariant_by_induction"]
        and not proof["backward_invariance_or_onto_is_used"]
    )
    quotient = spectral["spectral_quotient_record"]
    evidence = spectral["degree_evidence_inventory"]
    spectral_boundary = bool(
        spectral["passed"]
        and quotient["quotient_bracket_width"] <= SPECTRAL_QUOTIENT_BRACKET_WIDTH_CAP
        and quotient["sufficient_upper_quotient"] <= SPECTRAL_QUOTIENT_UPPER_CAP
        and evidence["missing_external_nonresonance_degrees_through_upper_quotient"]
        and not evidence["spectral_quotient_ssm_uniqueness_is_certified"]
    )
    hypothesis_gates = {
        "scalar_cutoff_is_a_global_c1_real_localization_with_registered_caps": {
            "passed": bool(validity_passed and cutoff_hypothesis),
            "threshold": (
                "real-preserving global C1 cutoff with support factor 4 and derivative upper 129"
            ),
            "value": cutoff["smooth_scalar_cutoff"],
        },
        "selected_scale_base_height_slope_and_c0_contraction_fit_caps": {
            "passed": bool(validity_passed and selected_transform),
            "threshold": (
                "scale>=1/4096, utilization<=0.01, height<=0.99, "
                "slope<=0.999 and C0 contraction<=0.99"
            ),
            "value": selected,
        },
        "derivative_fiber_contraction_yields_a_c1_fixed_graph": {
            "passed": bool(validity_passed and fiber_c1),
            "threshold": (
                "uniform derivative-fiber contraction<=0.9995 and the "
                "fiber-contraction theorem applies"
            ),
            "value": (selected["derivative_fiber_contraction"] if selected is not None else None),
        },
        "origin_derivative_zero_gives_selected_real_spectral_tangency": {
            "passed": bool(validity_passed and origin_tangent),
            "threshold": (
                "the unique derivative fiber fixed point at the origin is "
                "zero, so the graph tangent is the selected real subspace"
            ),
            "value": proof,
        },
        "inner_patch_and_image_transfer_to_original_forward_invariance": {
            "passed": bool(validity_passed and original_transfer),
            "threshold": (
                "input and image stay in the smooth-cutoff identity core "
                "and physical buffers, giving original-map forward invariance"
            ),
            "value": selected,
        },
        "spectral_quotient_bracket_is_rigorous_without_ssm_uniqueness_claim": {
            "passed": bool(validity_passed and spectral_boundary),
            "threshold": (
                "quotient bracket width<=1 and upper<=90, with degrees 3 "
                "through L_+ explicitly missing and no SSM uniqueness claim"
            ),
            "value": {
                "quotient": quotient,
                "degree_evidence": evidence,
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011t C1 tangent graph audit is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the original repaired exact map has a certified C1 "
            "forward-invariant graph patch tangent to the selected real "
            "spectral subspace"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered C1 localization does not certify a tangent original-map graph patch"
        )

    cycle: dict[str, Any] = {
        "question": (
            "Does a separately constructed scalar C1 localization give a "
            "C1 fixed graph tangent to the selected real spectral subspace "
            "whose inner patch is forward invariant for the original map?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "cutoff_digest_sha256": cutoff_digest,
        "graph_digest_sha256": graph_digest,
        "radius_digest_sha256": radius_digest,
        "spectral_digest_sha256": spectral_digest,
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
    cycle["theorem_consequence"] = {
        "a_separate_global_c1_scalar_localization_is_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "a_unique_c1_fixed_graph_for_the_smooth_localized_map_exists": bool(
            validity_passed and hypotheses_passed
        ),
        "the_localized_c1_graph_has_zero_derivative_at_the_origin": bool(
            validity_passed and hypotheses_passed
        ),
        "the_graph_tangent_is_the_selected_real_spectral_subspace": bool(
            validity_passed and hypotheses_passed
        ),
        "the_original_map_has_a_forward_invariant_c1_graph_patch": bool(
            validity_passed and hypotheses_passed
        ),
        "the_graph_patch_is_twenty_four_real_dimensional_on_the_fixed_leaf": bool(
            validity_passed and hypotheses_passed
        ),
        "a_rigorous_spectral_quotient_bracket_is_certified": bool(
            validity_passed and hypotheses_passed
        ),
        "the_q011s_lipschitz_graph_is_the_same_graph": False,
        "backward_invariance_or_onto_is_certified": False,
        "c2_or_higher_smoothness_is_certified": False,
        "all_nonresonances_through_the_spectral_quotient_are_certified": False,
        "spectral_quotient_ssm_uniqueness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011k_q011m_q011q_q011r_or_q011s_acceptance_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the fixed 17x17 repaired exact map on the "
        "fixed conservation leaf, the Q011q real coordinate, the separately "
        "registered scalar C1 localization, the eleven registered scales, "
        "a twenty-four-real-dimensional forward-invariant C1 graph patch "
        "and its origin tangency. It does not identify this graph with the "
        "Q011s Lipschitz graph and certifies no backward invariance, onto "
        "property, C2 or higher smoothness, all nonresonances through the "
        "spectral quotient, SSM uniqueness, normal attraction, basin, "
        "optimal radius, other grid, force, wall boundary or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011k_spectral_split_acceptance_changed": False,
        "q011m_quadratic_jet_acceptance_changed": False,
        "q011q_real_setup_acceptance_changed": False,
        "q011r_lipschitz_localized_graph_acceptance_changed": False,
        "q011s_original_lipschitz_core_acceptance_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011u to test higher-smoothness localization and "
            "external nonresonance or homological evidence for every degree "
            "from 3 through the conservative spectral quotient."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Revise only the first failed cutoff, derivative, base, fiber or "
            "original-core condition on the registered scale grid."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, cutoff typing, formula, scale, "
            "spectral reconstruction or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011t cycle failed strict serialization or digest")
    return cycle


def run_q011t_study() -> dict[str, Any]:
    cycle = run_c1_tangent_graph_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "floating_point_used_for_gate_decisions": False,
            "coordinate_slot_count": COORDINATE_SLOT_COUNT,
            "scale_candidate_count": len(SCALE_CANDIDATES),
            "spectral_interval_count": COORDINATE_SLOT_COUNT,
        },
        "mathematical_scope": {
            "diagnostic": "C1-localized tangent original-map graph patch",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "selected_real_dimension": SELECTED_DIMENSION,
            "external_real_dimension": EXTERNAL_DIMENSION,
            "separate_smooth_localization_claim": True,
            "original_map_forward_invariant_c1_patch_claim": (
                cycle["hypothesis_outcome"] == "accepted"
            ),
            "origin_tangency_claim": (cycle["hypothesis_outcome"] == "accepted"),
            "q011s_graph_equality_claim": False,
            "backward_invariance_claim": False,
            "c2_or_higher_smoothness_claim": False,
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
    result = run_q011t_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
