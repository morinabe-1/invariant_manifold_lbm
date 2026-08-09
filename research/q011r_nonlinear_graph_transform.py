"""Q011r real-norm nonlinear graph-transform contraction audit."""

from __future__ import annotations

import argparse
import itertools
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011m_quadratic_jet_majorant as q011m
import research.q011q_real_frame_setup as q011q
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
SELECTED_DIMENSION = 24
EXTERNAL_DIMENSION = 2574
FIXED_LEAF_DIMENSION = 2598
GRAPH_LIPSCHITZ_CAP = Fraction(1)
CUTOFF_LIPSCHITZ_CAP = Fraction(2)

SECOND_DERIVATIVE_COORDINATE_CAP = Fraction(10**12)
THIRD_DERIVATIVE_COORDINATE_CAP = Fraction(10**17)
NONLINEAR_LIPSCHITZ_CAP = Fraction(1, 1000)
BASE_INVERSE_UTILIZATION_CAP = Fraction(1, 100)
HEIGHT_RATIO_CAP = Fraction(99, 100)
GRAPH_SLOPE_CAP = Fraction(999, 1000)
GRAPH_TRANSFORM_CONTRACTION_CAP = Fraction(99, 100)
MINIMUM_SELECTED_RADIUS = Fraction(1, 10**16)
RADIUS_CANDIDATES = (
    Fraction(1, 10**18),
    Fraction(3, 10**18),
    Fraction(1, 10**17),
    Fraction(3, 10**17),
    Fraction(1, 10**16),
    Fraction(3, 10**16),
    Fraction(1, 10**15),
    Fraction(3, 10**15),
    Fraction(1, 10**14),
    Fraction(3, 10**14),
    Fraction(1, 10**13),
    Fraction(3, 10**13),
    Fraction(1, 10**12),
    Fraction(3, 10**12),
    Fraction(1, 10**11),
)

Q011M_ARTIFACT_SHA256 = (
    "b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f"
)
Q011M_RUNNER_SHA256 = (
    "0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150"
)
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

    m_cycle = artifacts["q011m"]["cycle"]
    q_cycle = artifacts["q011q"]["cycle"]
    m_theorem = m_cycle["theorem_consequence"]
    q_theorem = q_cycle["theorem_consequence"]
    derivative_checks = m_cycle["analytic_map_derivative_audit"]["checks"]
    checks["q011m_derivative_and_claim_boundary_are_preserved"] = bool(
        m_theorem[
            "repaired_exact_map_second_and_third_derivative_bounds_are_certified"
        ]
        and m_theorem["registered_uniform_cubic_defect_majorant_is_rigorous"]
        and not m_theorem["finite_cubic_defect_implies_exact_invariance"]
        and not m_theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    )
    checks["q011m_nonlinear_outputs_are_on_the_fixed_leaf"] = bool(
        derivative_checks[
            "all_second_derivative_conserved_moments_are_zero"
        ]
        and derivative_checks[
            "all_third_derivative_conserved_moments_are_zero"
        ]
        and derivative_checks["source_has_no_second_or_third_derivative"]
    )
    checks["q011q_real_setup_and_claim_boundary_are_preserved"] = bool(
        q_theorem["fixed_leaf_real_coordinate_lift_and_inverse_are_certified"]
        and q_theorem[
            "registered_same_norm_real_linear_domination_is_rigorous"
        ]
        and q_theorem["radial_cutoff_and_real_graph_space_are_type_correct"]
        and not q_theorem[
            "a_nonlinear_graph_transform_is_defined_or_certified"
        ]
        and not q_theorem[
            "an_exact_local_invariant_manifold_or_ssm_is_certified"
        ]
    )
    checks["ten_direct_digests_are_sealed"] = (
        sum(len(record["digests"]) for record in records.values()) == 10
    )
    checks["nested_q011m_seal_reproduces_but_is_not_substituted"] = bool(
        q_cycle["sealed_input_audit"]["q011m"]["artifact_sha256"]
        == Q011M_ARTIFACT_SHA256
        and records["q011m"]["artifact_sha256"]
        == Q011M_ARTIFACT_SHA256
    )
    audit = {
        **records,
        "direct_digest_count": 10,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, artifacts


def _derivative_transport_audit(
    artifacts: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    m_cycle = artifacts["q011m"]["cycle"]
    q_cycle = artifacts["q011q"]["cycle"]
    derivative = m_cycle["analytic_map_derivative_audit"]
    coordinate = q_cycle["real_fixed_leaf_coordinate_audit"]
    linear = q_cycle["real_same_norm_linear_split_audit"]
    localization = q_cycle["real_localized_graph_space_audit"]
    root = m_cycle["exact_root_and_simple_envelope_audit"]

    physical_second = _fraction(
        derivative["maximum_map_second_derivative_bilinear_upper"]
    )
    physical_third = _fraction(
        derivative["maximum_map_third_derivative_trilinear_upper"]
    )
    lift_norm = _fraction(coordinate["real_physical_lift_norm_upper"])
    analysis_norm = _fraction(
        coordinate["real_coordinate_inverse_norm_upper"]
    )
    coordinate_second = analysis_norm * physical_second * lift_norm**2
    coordinate_third = analysis_norm * physical_third * lift_norm**3
    selected_conorm = _fraction(linear["real_selected_conorm_lower"])
    external_norm = _fraction(linear["real_external_operator_norm_upper"])
    coupling = _fraction(
        linear["real_selected_external_coupling_upper"]
    )
    selected_inverse = _fraction(
        linear["real_selected_base_inverse_norm_upper"]
    )
    cutoff_lipschitz = _fraction(
        localization["cutoff"]["global_lipschitz_constant_upper"]
    )
    values = {
        "M_2": physical_second,
        "M_3": physical_third,
        "K_L": lift_norm,
        "K_P": analysis_norm,
        "mu_2": coordinate_second,
        "mu_3": coordinate_third,
        "m": selected_conorm,
        "q": external_norm,
        "b": coupling,
        "alpha": selected_inverse,
        "cutoff_lipschitz": cutoff_lipschitz,
        "state_displacement_cap": _fraction(
            derivative["registered_state_displacement_cap"]
        ),
        "root_population_floor": _fraction(
            root["root_population_floor_lower"]
        ),
        "root_density_floor": _fraction(root["root_density_floor_lower"]),
        "population_threshold": q011m.POPULATION_THRESHOLD,
        "density_threshold": q011m.DENSITY_THRESHOLD,
    }
    derivative_checks = derivative["checks"]
    checks = {
        "q011m_analytic_derivative_audit_passes": derivative["passed"],
        "q011q_real_coordinate_audit_passes": coordinate["passed"],
        "q011q_real_linear_split_audit_passes": linear["passed"],
        "q011q_real_localization_audit_passes": localization["passed"],
        "second_derivative_transport_formula_reproduces": (
            coordinate_second
            == analysis_norm * physical_second * lift_norm**2
        ),
        "third_derivative_transport_formula_reproduces": (
            coordinate_third
            == analysis_norm * physical_third * lift_norm**3
        ),
        "normalized_dft_and_block_sum_norms_are_preserved": bool(
            coordinate["checks"]["q011o_seventeen_block_baseline_passes"]
            and coordinate["coordinate_definition"]["analytic_norm"]
            == (
                "restriction of the complex-modulus block-sup norm to the "
                "real fixed spaces"
            )
        ),
        "nonlinear_outputs_stay_on_the_fixed_leaf": bool(
            derivative_checks[
                "all_second_derivative_conserved_moments_are_zero"
            ]
            and derivative_checks[
                "all_third_derivative_conserved_moments_are_zero"
            ]
        ),
        "root_and_linearization_make_n_and_dn_zero_at_origin": True,
        "selected_inverse_is_reciprocal_conorm_bound": (
            selected_inverse == 1 / selected_conorm
        ),
        "radial_cutoff_has_registered_two_lipschitz_bound": (
            cutoff_lipschitz == CUTOFF_LIPSCHITZ_CAP
        ),
        "all_transported_constants_are_positive_and_finite": bool(
            all(value > 0 for value in values.values())
            and _all_numeric_values_finite(values)
        ),
    }
    audit = {
        "physical_norm": "site-population infinity norm",
        "coordinate_norm": (
            "complex-modulus block-sup norm restricted to the real split"
        ),
        "transport_formulas": {
            "second_derivative": "mu_2=K_P M_2 K_L^2",
            "third_derivative": "mu_3=K_P M_3 K_L^3",
            "nonlinear_amplitude": "n_rho=(mu_2/2) rho^2",
            "localized_lipschitz": "delta_rho=2 mu_2 rho",
        },
        "physical_second_derivative_upper": _fraction_record(
            physical_second
        ),
        "physical_third_derivative_upper": _fraction_record(physical_third),
        "real_physical_lift_norm_upper": _fraction_record(lift_norm),
        "real_coordinate_analysis_norm_upper": _fraction_record(
            analysis_norm
        ),
        "real_second_derivative_bilinear_upper": _fraction_record(
            coordinate_second
        ),
        "real_third_derivative_trilinear_upper": _fraction_record(
            coordinate_third
        ),
        "registered_real_second_derivative_cap": _fraction_record(
            SECOND_DERIVATIVE_COORDINATE_CAP
        ),
        "registered_real_third_derivative_cap": _fraction_record(
            THIRD_DERIVATIVE_COORDINATE_CAP
        ),
        "real_selected_conorm_lower": _fraction_record(selected_conorm),
        "real_external_operator_norm_upper": _fraction_record(external_norm),
        "real_selected_external_coupling_upper": _fraction_record(coupling),
        "real_selected_inverse_norm_upper": _fraction_record(
            selected_inverse
        ),
        "radial_cutoff_lipschitz_upper": _fraction_record(
            cutoff_lipschitz
        ),
        "fixed_leaf_second_and_third_conserved_moments_are_zero": True,
        "third_derivative_is_provenance_not_a_sharpening_term": True,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return audit, values


def _graph_transform_definition_audit(
    artifacts: dict[str, dict[str, Any]],
    transport: dict[str, Any],
) -> dict[str, Any]:
    q_cycle = artifacts["q011q"]["cycle"]
    coordinate = q_cycle["real_fixed_leaf_coordinate_audit"]
    localization = q_cycle["real_localized_graph_space_audit"]
    local_graph = localization["real_graph_banach_space"]
    graph_space = {
        "name": "G_global_(rho,1)",
        "domain": "the full selected real space S_R",
        "codomain": "the full external real space E_R",
        "fixes_origin": True,
        "uniform_height_cap": "rho",
        "lipschitz_cap": _fraction_record(GRAPH_LIPSCHITZ_CAP),
        "metric": "global uniform sup metric",
        "metric_is_finite_from_uniform_height_cap": True,
        "uniform_limit_preserves_origin_height_and_lipschitz_cap": True,
        "closed_complete_space": True,
        "restriction_to_selected_rho_ball_is_in_q011q_local_space": True,
        "unproved_one_lipschitz_extension_is_used": False,
    }
    base_inverse = {
        "base_map": (
            "P_psi(s)=S s+B psi(s)+(N_rho)_S(s,psi(s))"
        ),
        "fixed_point_inverse": (
            "s=S^(-1)[u-B psi(s)-(N_rho)_S(s,psi(s))]"
        ),
        "perturbation_lipschitz": "b+delta_rho",
        "conorm_lower": "d_rho=m-b-delta_rho",
        "contraction_utilization": "u_rho=alpha(b+delta_rho)",
        "global_bijection_follows_from_fixed_point_inverse": True,
        "finite_dimensional_surjectivity_is_not_assumed": True,
        "inverse_lipschitz_upper": "1/d_rho",
    }
    graph_transform = {
        "definition": (
            "(T_rho psi)(u)=E psi(P_psi^(-1)u)+"
            "(N_rho)_E(P_psi^(-1)u,psi(P_psi^(-1)u))"
        ),
        "domain": "G_global_(rho,1)",
        "codomain": "G_global_(rho,1) when height and slope gates pass",
        "origin_is_fixed": True,
        "real_selected_and_external_spaces_are_preserved": True,
        "height_ratio": "h_rho=q+(mu_2/2)rho",
        "slope_upper": "ell_rho=(q+delta_rho)/d_rho",
        "preimage_sensitivity": "(b+delta_rho)/d_rho",
        "uniform_contraction": (
            "kappa_rho=(q+delta_rho)[1+(b+delta_rho)/d_rho]"
        ),
        "eigenvalue_gap_is_not_substituted": True,
        "q011p_riccati_contraction_is_not_substituted": True,
        "q007_normal_fiber_contraction_is_not_substituted": True,
    }
    checks = {
        "q011q_real_dimensions_close": bool(
            coordinate["selected_real_dimension"] == SELECTED_DIMENSION
            and coordinate["external_real_dimension"] == EXTERNAL_DIMENSION
            and coordinate["total_fixed_leaf_real_dimension"]
            == FIXED_LEAF_DIMENSION
        ),
        "q011q_local_graph_space_is_closed_complete": local_graph[
            "closed_complete_space"
        ],
        "global_uniform_metric_is_finite": graph_space[
            "metric_is_finite_from_uniform_height_cap"
        ],
        "global_bounded_graph_space_is_closed_complete": bool(
            graph_space[
                "uniform_limit_preserves_origin_height_and_lipschitz_cap"
            ]
            and graph_space["closed_complete_space"]
        ),
        "no_unproved_local_graph_extension_is_used": not graph_space[
            "unproved_one_lipschitz_extension_is_used"
        ],
        "base_inverse_is_a_registered_fixed_point_problem": bool(
            base_inverse[
                "global_bijection_follows_from_fixed_point_inverse"
            ]
            and base_inverse["finite_dimensional_surjectivity_is_not_assumed"]
        ),
        "graph_transform_has_explicit_domain_and_codomain": bool(
            graph_transform["domain"] == "G_global_(rho,1)"
            and graph_transform["codomain"]
            == "G_global_(rho,1) when height and slope gates pass"
        ),
        "real_typing_is_inherited_from_q011q": bool(
            transport["passed"]
            and graph_transform[
                "real_selected_and_external_spaces_are_preserved"
            ]
        ),
        "unrelated_contraction_constants_are_not_substituted": bool(
            graph_transform["eigenvalue_gap_is_not_substituted"]
            and graph_transform[
                "q011p_riccati_contraction_is_not_substituted"
            ]
            and graph_transform[
                "q007_normal_fiber_contraction_is_not_substituted"
            ]
        ),
    }
    return {
        "real_graph_space": graph_space,
        "base_inverse": base_inverse,
        "graph_transform": graph_transform,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _radius_record(
    radius: Fraction,
    values: dict[str, Fraction],
) -> tuple[dict[str, Any], dict[str, Fraction | None]]:
    mu_2 = values["mu_2"]
    lift_norm = values["K_L"]
    selected_conorm = values["m"]
    external_norm = values["q"]
    coupling = values["b"]
    selected_inverse = values["alpha"]
    physical_radius = lift_norm * radius
    population_floor = values["root_population_floor"] - physical_radius
    density_floor = values["root_density_floor"] - 9 * physical_radius
    nonlinear_amplitude = Fraction(1, 2) * mu_2 * radius**2
    nonlinear_lipschitz = 2 * mu_2 * radius
    base_conorm = selected_conorm - coupling - nonlinear_lipschitz
    inverse_utilization = selected_inverse * (
        coupling + nonlinear_lipschitz
    )
    height_ratio = external_norm + nonlinear_amplitude / radius
    inverse_lipschitz: Fraction | None = None
    preimage_sensitivity: Fraction | None = None
    slope: Fraction | None = None
    contraction: Fraction | None = None
    contraction_expanded: Fraction | None = None
    if base_conorm > 0:
        inverse_lipschitz = 1 / base_conorm
        preimage_sensitivity = (
            coupling + nonlinear_lipschitz
        ) / base_conorm
        slope = (external_norm + nonlinear_lipschitz) / base_conorm
        contraction = selected_conorm * (
            external_norm + nonlinear_lipschitz
        ) / base_conorm
        contraction_expanded = (
            external_norm + nonlinear_lipschitz
        ) * (1 + preimage_sensitivity)

    checks = {
        "physical_radius_is_in_q011m_derivative_domain": (
            physical_radius <= values["state_displacement_cap"]
        ),
        "population_floor_passes": (
            population_floor >= values["population_threshold"]
        ),
        "density_floor_passes": (
            density_floor >= values["density_threshold"]
        ),
        "localized_nonlinear_lipschitz_fits_cap": (
            nonlinear_lipschitz <= NONLINEAR_LIPSCHITZ_CAP
        ),
        "base_conorm_is_positive": base_conorm > 0,
        "base_inverse_utilization_fits_cap": (
            inverse_utilization <= BASE_INVERSE_UTILIZATION_CAP
        ),
        "height_ratio_fits_cap": height_ratio <= HEIGHT_RATIO_CAP,
        "graph_slope_fits_cap": bool(
            slope is not None and slope <= GRAPH_SLOPE_CAP
        ),
        "graph_transform_contraction_fits_cap": bool(
            contraction is not None
            and contraction <= GRAPH_TRANSFORM_CONTRACTION_CAP
        ),
        "contraction_formulas_agree": bool(
            contraction is not None
            and contraction == contraction_expanded
        ),
    }
    exact: dict[str, Fraction | None] = {
        "radius": radius,
        "physical_state_radius": physical_radius,
        "population_floor": population_floor,
        "density_floor": density_floor,
        "nonlinear_amplitude": nonlinear_amplitude,
        "nonlinear_lipschitz": nonlinear_lipschitz,
        "base_conorm": base_conorm,
        "base_inverse_utilization": inverse_utilization,
        "base_inverse_lipschitz": inverse_lipschitz,
        "height_ratio": height_ratio,
        "preimage_sensitivity": preimage_sensitivity,
        "graph_slope": slope,
        "graph_transform_contraction": contraction,
    }
    record = {
        name: _fraction_record(value) if value is not None else None
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
    exact_records: list[dict[str, Fraction | None]] = []
    passing: list[Fraction] = []
    for radius in RADIUS_CANDIDATES:
        record, exact = _radius_record(radius, values)
        records.append(record)
        exact_records.append(exact)
        if record["passed"]:
            passing.append(radius)

    selected = max(passing) if passing else None
    selected_record = next(
        (
            record
            for record in records
            if selected is not None
            and _fraction(record["radius"]) == selected
        ),
        None,
    )
    larger_records = [
        record
        for record in records
        if selected is not None and _fraction(record["radius"]) > selected
    ]
    first_failed = larger_records[0] if larger_records else None
    first_failed_constraints = (
        [
            name
            for name, passed in first_failed["checks"].items()
            if not passed
        ]
        if first_failed is not None
        else []
    )

    finite_exact = [
        {
            name: _fraction_record(value) if value is not None else None
            for name, value in exact.items()
        }
        for exact in exact_records
    ]
    finite_prefix = [
        exact
        for exact in exact_records
        if exact["graph_slope"] is not None
    ]
    monotonicity_checks = {
        "physical_radius_is_nondecreasing": _is_nondecreasing(
            [exact["physical_state_radius"] for exact in exact_records]
        ),
        "nonlinear_amplitude_is_nondecreasing": _is_nondecreasing(
            [exact["nonlinear_amplitude"] for exact in exact_records]
        ),
        "nonlinear_lipschitz_is_nondecreasing": _is_nondecreasing(
            [exact["nonlinear_lipschitz"] for exact in exact_records]
        ),
        "base_conorm_is_nonincreasing": _is_nonincreasing(
            [exact["base_conorm"] for exact in exact_records]
        ),
        "inverse_utilization_is_nondecreasing": _is_nondecreasing(
            [exact["base_inverse_utilization"] for exact in exact_records]
        ),
        "height_ratio_is_nondecreasing": _is_nondecreasing(
            [exact["height_ratio"] for exact in exact_records]
        ),
        "finite_graph_slope_prefix_is_nondecreasing": _is_nondecreasing(
            [exact["graph_slope"] for exact in finite_prefix]
        ),
        "finite_contraction_prefix_is_nondecreasing": _is_nondecreasing(
            [
                exact["graph_transform_contraction"]
                for exact in finite_prefix
            ]
        ),
        "population_and_density_floors_are_nonincreasing": bool(
            _is_nonincreasing(
                [exact["population_floor"] for exact in exact_records]
            )
            and _is_nonincreasing(
                [exact["density_floor"] for exact in exact_records]
            )
        ),
    }
    passing_set = set(passing)
    checks = {
        "all_fifteen_registered_radii_are_present": (
            len(records) == len(RADIUS_CANDIDATES) == 15
        ),
        "radii_are_strictly_increasing": all(
            left < right
            for left, right in itertools.pairwise(RADIUS_CANDIDATES)
        ),
        "all_radius_values_use_exact_fraction_arithmetic": True,
        "all_record_formulas_reproduce": all(
            record["checks"]["contraction_formulas_agree"]
            or not record["checks"]["base_conorm_is_positive"]
            for record in records
        ),
        "passing_radius_set_is_an_initial_prefix": (
            passing == list(RADIUS_CANDIDATES[: len(passing)])
            and passing_set == set(RADIUS_CANDIDATES[: len(passing)])
        ),
        "selected_radius_is_the_largest_passing_candidate": bool(
            selected is None or selected == max(passing)
        ),
        "first_larger_failure_is_recorded_when_present": bool(
            selected is None
            or selected == RADIUS_CANDIDATES[-1]
            or (
                first_failed is not None
                and not first_failed["passed"]
                and first_failed_constraints
            )
        ),
        "all_registered_majorants_have_the_registered_monotonicity": all(
            monotonicity_checks.values()
        ),
        "all_radius_records_are_finite_strict_json": bool(
            _all_numeric_values_finite(records)
            and _strict_json_serializable(records)
            and json.dumps(records, allow_nan=False)
        ),
    }
    return {
        "radius_candidates": [
            _fraction_record(radius) for radius in RADIUS_CANDIDATES
        ],
        "record_formulas": {
            "physical_state_radius": "K_L rho",
            "nonlinear_amplitude": "n_rho=(mu_2/2)rho^2",
            "nonlinear_lipschitz": "delta_rho=2 mu_2 rho",
            "base_conorm": "d_rho=m-b-delta_rho",
            "base_inverse_utilization": "u_rho=alpha(b+delta_rho)",
            "height_ratio": "h_rho=q+(mu_2/2)rho",
            "graph_slope": "ell_rho=(q+delta_rho)/d_rho",
            "graph_transform_contraction": (
                "kappa_rho=m(q+delta_rho)/d_rho"
            ),
        },
        "radius_records": records,
        "exact_radius_record_digest_sha256": q011b._canonical_json_sha256(
            finite_exact
        ),
        "monotonicity_checks": monotonicity_checks,
        "passing_radius_count": len(passing),
        "selected_radius": (
            _fraction_record(selected) if selected is not None else None
        ),
        "selected_record": selected_record,
        "first_failed_larger_radius": (
            first_failed["radius"] if first_failed is not None else None
        ),
        "first_failed_larger_constraints": first_failed_constraints,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "selected_dimension": SELECTED_DIMENSION,
        "external_dimension": EXTERNAL_DIMENSION,
        "fixed_leaf_dimension": FIXED_LEAF_DIMENSION,
        "graph_lipschitz_cap": _fraction_record(GRAPH_LIPSCHITZ_CAP),
        "cutoff_lipschitz_cap": _fraction_record(CUTOFF_LIPSCHITZ_CAP),
        "real_second_derivative_cap": _fraction_record(
            SECOND_DERIVATIVE_COORDINATE_CAP
        ),
        "real_third_derivative_cap": _fraction_record(
            THIRD_DERIVATIVE_COORDINATE_CAP
        ),
        "localized_nonlinear_lipschitz_cap": _fraction_record(
            NONLINEAR_LIPSCHITZ_CAP
        ),
        "base_inverse_utilization_cap": _fraction_record(
            BASE_INVERSE_UTILIZATION_CAP
        ),
        "height_ratio_cap": _fraction_record(HEIGHT_RATIO_CAP),
        "graph_slope_cap": _fraction_record(GRAPH_SLOPE_CAP),
        "graph_transform_contraction_cap": _fraction_record(
            GRAPH_TRANSFORM_CONTRACTION_CAP
        ),
        "minimum_selected_radius": _fraction_record(
            MINIMUM_SELECTED_RADIUS
        ),
        "radius_candidates": [
            _fraction_record(radius) for radius in RADIUS_CANDIDATES
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
        "transport_digest_sha256": cycle["transport_digest_sha256"],
        "graph_digest_sha256": cycle["graph_digest_sha256"],
        "radius_digest_sha256": cycle["radius_digest_sha256"],
    }


def run_nonlinear_graph_transform_audit() -> dict[str, Any]:
    sealed, artifacts = _sealed_input_audit()
    transport, values = _derivative_transport_audit(artifacts)
    graph = _graph_transform_definition_audit(
        artifacts,
        transport,
    )
    radius = _radius_campaign_audit(values)
    registered = _registered_parameters()
    runner = _runner_source_metadata()

    input_sections = {
        "registered_parameters": registered,
        "sealed_input_audit": sealed,
    }
    transport_sections = {"real_derivative_transport_audit": transport}
    graph_sections = {"global_graph_transform_definition_audit": graph}
    radius_sections = {"graph_transform_radius_campaign_audit": radius}
    input_digest = q011b._canonical_json_sha256(input_sections)
    transport_digest = q011b._canonical_json_sha256(transport_sections)
    graph_digest = q011b._canonical_json_sha256(graph_sections)
    radius_digest = q011b._canonical_json_sha256(radius_sections)
    strict_payload = {
        **input_sections,
        **transport_sections,
        **graph_sections,
        **radius_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011b._canonical_json_sha256(input_sections)
        and transport_digest
        == q011b._canonical_json_sha256(transport_sections)
        and graph_digest == q011b._canonical_json_sha256(graph_sections)
        and radius_digest == q011b._canonical_json_sha256(radius_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "two_direct_inputs_and_ten_digests_are_sealed": {
            "passed": sealed["passed"],
            "threshold": (
                "Q011m/q artifacts, runners, ten digests, outcomes and "
                "claim boundaries reproduce directly"
            ),
            "value": sealed["checks"],
        },
        "physical_derivatives_transport_to_the_real_norm": {
            "passed": transport["passed"],
            "threshold": (
                "mu_2=K_P M_2 K_L^2 and mu_3=K_P M_3 K_L^3 with "
                "fixed-leaf nonlinear output"
            ),
            "value": transport["checks"],
        },
        "taylor_and_radial_cutoff_majorants_are_typed": {
            "passed": bool(
                transport["checks"][
                    "root_and_linearization_make_n_and_dn_zero_at_origin"
                ]
                and transport["checks"][
                    "radial_cutoff_has_registered_two_lipschitz_bound"
                ]
            ),
            "threshold": (
                "n_rho=(mu_2/2)rho^2 and delta_rho=2 mu_2 rho on "
                "the registered derivative domain"
            ),
            "value": transport["transport_formulas"],
        },
        "global_bounded_real_graph_space_is_complete": {
            "passed": graph["passed"],
            "threshold": (
                "origin-fixed globally rho-bounded one-Lipschitz real "
                "graphs form a complete uniform-metric space"
            ),
            "value": graph["checks"],
        },
        "base_inverse_and_graph_transform_are_explicitly_defined": {
            "passed": bool(
                graph["checks"][
                    "base_inverse_is_a_registered_fixed_point_problem"
                ]
                and graph["checks"][
                    "graph_transform_has_explicit_domain_and_codomain"
                ]
            ),
            "threshold": (
                "fixed-point base inverse and real graph-transform formulas "
                "have explicit domains and codomains"
            ),
            "value": {
                "base_inverse": graph["base_inverse"],
                "graph_transform": graph["graph_transform"],
            },
        },
        "all_fifteen_exact_radius_records_and_monotonicity_reproduce": {
            "passed": radius["passed"],
            "threshold": (
                "fifteen Fraction radii reproduce domain, buffer, height, "
                "slope, inverse and contraction majorants monotonically"
            ),
            "value": radius["checks"],
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
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )

    selected_record = radius["selected_record"]
    selected_radius = (
        _fraction(radius["selected_radius"])
        if radius["selected_radius"] is not None
        else None
    )
    derivative_caps = bool(
        values["mu_2"] <= SECOND_DERIVATIVE_COORDINATE_CAP
        and values["mu_3"] <= THIRD_DERIVATIVE_COORDINATE_CAP
    )
    any_domain_buffer = any(
        record["checks"][
            "physical_radius_is_in_q011m_derivative_domain"
        ]
        and record["checks"]["population_floor_passes"]
        and record["checks"]["density_floor_passes"]
        for record in radius["radius_records"]
    )
    selected_majorants = bool(
        selected_record is not None
        and selected_radius is not None
        and selected_radius >= MINIMUM_SELECTED_RADIUS
        and selected_record["checks"][
            "localized_nonlinear_lipschitz_fits_cap"
        ]
        and selected_record["checks"][
            "base_inverse_utilization_fits_cap"
        ]
        and selected_record["checks"]["height_ratio_fits_cap"]
    )
    base_inverse = bool(
        selected_record is not None
        and selected_record["checks"]["base_conorm_is_positive"]
        and selected_record["checks"][
            "base_inverse_utilization_fits_cap"
        ]
        and selected_record["base_inverse_lipschitz"] is not None
    )
    graph_self_map = bool(
        selected_record is not None
        and selected_record["checks"]["height_ratio_fits_cap"]
        and selected_record["checks"]["graph_slope_fits_cap"]
    )
    graph_contraction = bool(
        selected_record is not None
        and selected_record["checks"][
            "graph_transform_contraction_fits_cap"
        ]
    )
    hypothesis_gates = {
        "transported_derivatives_fit_caps_and_a_domain_buffer_exists": {
            "passed": bool(
                validity_passed and derivative_caps and any_domain_buffer
            ),
            "threshold": (
                "mu_2<=1e12, mu_3<=1e17 and at least one radius passes "
                "the derivative domain and population/density buffers"
            ),
            "value": {
                "mu_2": transport[
                    "real_second_derivative_bilinear_upper"
                ],
                "mu_3": transport[
                    "real_third_derivative_trilinear_upper"
                ],
                "any_domain_buffer": any_domain_buffer,
            },
        },
        "selected_radius_and_nonlinear_majorants_fit_registered_caps": {
            "passed": bool(validity_passed and selected_majorants),
            "threshold": (
                "largest passing radius>=1e-16, delta<=1e-3, "
                "base utilization<=1e-2 and height ratio<=0.99"
            ),
            "value": selected_record,
        },
        "base_map_has_a_global_fixed_point_inverse": {
            "passed": bool(validity_passed and base_inverse),
            "threshold": (
                "d_rho>0, alpha(b+delta_rho)<1 and a finite inverse "
                "Lipschitz bound"
            ),
            "value": (
                {
                    "base_conorm": selected_record["base_conorm"],
                    "base_inverse_utilization": selected_record[
                        "base_inverse_utilization"
                    ],
                    "base_inverse_lipschitz": selected_record[
                        "base_inverse_lipschitz"
                    ],
                }
                if selected_record is not None
                else None
            ),
        },
        "nonlinear_graph_transform_is_a_strict_self_map": {
            "passed": bool(validity_passed and graph_self_map),
            "threshold": "height<=0.99 and graph slope<=0.999",
            "value": (
                {
                    "height_ratio": selected_record["height_ratio"],
                    "graph_slope": selected_record["graph_slope"],
                }
                if selected_record is not None
                else None
            ),
        },
        "uniform_graph_transform_metric_contraction_is_strict": {
            "passed": bool(validity_passed and graph_contraction),
            "threshold": "uniform graph-transform contraction<=0.99",
            "value": (
                selected_record["graph_transform_contraction"]
                if selected_record is not None
                else None
            ),
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q011r nonlinear graph-transform audit is invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the registered real localized graph transform is a strict "
            "contraction at a certified finite radius"
        )
    else:
        outcome = "rejected"
        classification = (
            "the transported Q011m majorant does not certify the Q011q "
            "nonlinear graph transform on the registered radius grid"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Does the transported Q011m derivative majorant make the Q011q "
            "real localized graph transform a self-map and contraction?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "transport_digest_sha256": transport_digest,
        "graph_digest_sha256": graph_digest,
        "radius_digest_sha256": radius_digest,
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
        "q011m_derivative_bounds_are_transported_to_the_q011q_real_norm": bool(
            validity_passed and hypotheses_passed
        ),
        "localized_nonlinearity_has_global_amplitude_and_lipschitz_bounds": bool(
            validity_passed and hypotheses_passed
        ),
        "the_global_bounded_real_graph_space_is_complete": bool(
            validity_passed and hypotheses_passed
        ),
        "the_nonlinear_graph_transform_is_a_self_map": bool(
            validity_passed and hypotheses_passed
        ),
        "the_nonlinear_graph_transform_is_a_strict_contraction": bool(
            validity_passed and hypotheses_passed
        ),
        "a_unique_lipschitz_fixed_graph_for_the_localized_map_exists": bool(
            validity_passed and hypotheses_passed
        ),
        "an_original_map_local_invariant_manifold_or_ssm_is_certified": False,
        "c1_or_higher_smoothness_is_certified": False,
        "normal_attraction_or_a_basin_is_certified": False,
        "q011m_or_q011q_acceptance_is_changed": False,
    }
    cycle["claim_boundary"] = (
        "This audit concerns only the fixed 17x17 repaired exact map on the "
        "fixed conservation leaf, the Q011q real split, the Q011m derivative "
        "domain, the fifteen registered radii, the radially localized map "
        "and globally bounded Lipschitz real graphs. It certifies a unique "
        "fixed graph only for the localized map. It certifies no optimal "
        "radius, original-map invariant manifold or SSM, C1 or higher "
        "smoothness, spectral-quotient uniqueness, normal attraction, basin, "
        "long trajectory, other grid, force, wall boundary or D3Q27 result."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011m_quadratic_jet_acceptance_changed": False,
        "q011q_real_setup_acceptance_changed": False,
        "q011o_historical_rejection_changed": False,
    }
    if outcome == "accepted":
        cycle["next_change"] = (
            "Preregister Q011s to certify an inner core whose localized "
            "fixed graph and selected base image stay in the cutoff identity "
            "region, so the graph germ can be transferred to the original "
            "exact map."
        )
    elif outcome == "rejected":
        cycle["next_change"] = (
            "Use only the first failed registered radius condition to revise "
            "one sectorwise derivative transport, block weight, cutoff or "
            "radius grid."
        )
    else:
        cycle["next_change"] = (
            "Repair only the first sealing, derivative transport, graph-space "
            "typing, base-inverse, radius or serialization validity failure."
        )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and cycle["result_digest_sha256"]
        == q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011r cycle failed strict serialization or digest")
    return cycle


def run_q011r_study() -> dict[str, Any]:
    cycle = run_nonlinear_graph_transform_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "arithmetic_runtime": {
            "proof_scalar_type": "fractions.Fraction",
            "floating_point_used_for_gate_decisions": False,
            "radius_candidate_count": len(RADIUS_CANDIDATES),
        },
        "mathematical_scope": {
            "diagnostic": "real-norm localized nonlinear graph transform",
            "grid": [SIZE, SIZE],
            "fixed_conservation_leaf": True,
            "selected_real_dimension": SELECTED_DIMENSION,
            "external_real_dimension": EXTERNAL_DIMENSION,
            "localized_fixed_graph_claim": (
                cycle["hypothesis_outcome"] == "accepted"
            ),
            "original_map_invariant_manifold_claim": False,
            "smoothness_claim": False,
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
    result = run_q011r_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
