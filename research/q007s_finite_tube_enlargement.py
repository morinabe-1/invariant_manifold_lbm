"""Sealed Q007s rational-grid enlargement of the Q007p finite tube."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_REAL_DIMENSION = 24
EXTERNAL_COMPLEX_DIMENSION = 2574
Q007P_ARTIFACT = "q007p_finite_tube_attraction.json"
REGISTERED_Q007P_ARTIFACT_SHA256 = (
    "a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751"
)
REGISTERED_Q007P_RUNNER_SHA256 = (
    "23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a"
)
CONTROL_BASE_RADIUS = Fraction(1, 10**19)
CONTROL_NORMAL_RADIUS = Fraction(1, 10**20)
ANALYTIC_RADIUS = Fraction(1, 10**18)
NONLINEAR_DERIVATIVE_CONSTANT = Fraction(21, 2)
MAXIMUM_NORMAL_CONTRACTION = Fraction(99, 100)
MAXIMUM_DOMINATION_RATIO = Fraction(999, 1000)
EXPECTED_BASE_COUNT = 9
EXPECTED_NORMAL_COUNT = 99
EXPECTED_CANDIDATE_COUNT = 891

ExactCandidate = dict[str, Any]


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _fraction_from_record(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _optional_fraction_record(value: Fraction | None) -> dict[str, Any] | None:
    return None if value is None else _fraction_record(value)


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _load_registered_q007p(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007P_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha256 = _file_sha256(artifact_path)
    runner_path = Path(__file__).resolve().with_name(
        "q007p_finite_tube_attraction.py"
    )
    observed_runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    scope = payload.get("mathematical_scope", {})
    scope_match = bool(
        scope.get("diagnostic")
        == "rational finite-tube normal-attraction certificate"
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == OMEGA
        and float(scope.get("eta", np.nan)) == ETA
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and scope.get("selected_real_dimension") == SELECTED_REAL_DIMENSION
        and scope.get("external_complex_dimension")
        == EXTERNAL_COMPLEX_DIMENSION
        and float(scope.get("base_modal_l1_radius", np.nan))
        == float(CONTROL_BASE_RADIUS)
        and float(scope.get("normal_coordinate_radius", np.nan))
        == float(CONTROL_NORMAL_RADIUS)
    )
    theorem = payload.get("cycle", {}).get("theorem_consequence", {})
    theorem_flags_match = bool(len(theorem) == 4 and all(theorem.values()))
    inputs = payload.get("cycle", {}).get("input_artifacts", {})
    upstream_inputs_pass = bool(inputs) and all(
        record.get("passed", False) for record in inputs.values()
    )
    record = {
        "filename": Q007P_ARTIFACT,
        "registered_sha256": REGISTERED_Q007P_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha256,
        "sha256_matches": (
            observed_artifact_sha256 == REGISTERED_Q007P_ARTIFACT_SHA256
        ),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": scope_match,
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "all_upstream_inputs_pass": upstream_inputs_pass,
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload, "hypothesis_gates"
        ),
        "theorem_consequence_count": len(theorem),
        "all_theorem_consequences_true": theorem_flags_match,
        "registered_runner_sha256": REGISTERED_Q007P_RUNNER_SHA256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "observed_runner_sha256": observed_runner_sha256,
        "runner_sha_matches": bool(
            artifact_runner_sha256 == REGISTERED_Q007P_RUNNER_SHA256
            and observed_runner_sha256 == REGISTERED_Q007P_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and upstream_inputs_pass
        and record["all_validity_gates_pass"]
        and record["all_hypothesis_gates_pass"]
        and theorem_flags_match
        and record["runner_sha_matches"]
    )
    return payload, record


def _extract_constants(
    q007p: dict[str, Any],
) -> tuple[dict[str, Fraction], dict[str, Any]]:
    cycle = q007p["cycle"]
    majorant = cycle["finite_tube_majorant"]
    bounds = cycle["global_conversion_and_linear_bounds"]
    registered = cycle["registered_parameters"]
    coefficients = {
        name: _fraction_from_record(record)
        for name, record in majorant[
            "working_coefficients_reused_from_q007n"
        ].items()
    }
    constants = {
        **coefficients,
        "rho": _fraction_from_record(majorant["analytic_chart_radius"]),
        "tau": _fraction_from_record(majorant["correction_pair_radius_tau"]),
        "selected_radius": _fraction_from_record(
            majorant["selected_spectral_radius_upper"]
        ),
        "selected_minimum": _fraction_from_record(
            majorant["selected_minimum_modulus_lower"]
        ),
        "nonlinear_constant": _fraction_from_record(
            majorant["nonlinear_derivative_majorant_constant"]
        ),
        "q0": _fraction_from_record(
            bounds["linear_external_contraction_upper"]
        ),
        "synthesis": _fraction_from_record(
            bounds["synthesis_to_wiener_l1_upper"]
        ),
        "analysis": _fraction_from_record(
            bounds["analysis_from_wiener_l1_upper"]
        ),
        "selected_analysis": _fraction_from_record(
            bounds["selected_left_operator_l1_upper"]
        ),
        "normal_cap": _fraction_from_record(
            registered["maximum_normal_contraction"]
        ),
        "domination_cap": _fraction_from_record(
            registered["maximum_domination_ratio"]
        ),
    }
    expected_formula_names = {
        "c_v",
        "h2",
        "h3",
        "h4",
        "g2",
        "g3",
        "g4",
    }
    expected_box_audit_names = {
        "h2_box",
        "h3_box",
        "h4_box",
        "g2_box",
        "g3_box",
        "g4_box",
    }
    expected_saved_names = expected_formula_names | expected_box_audit_names
    reuse = cycle["majorant_reuse_audit"]
    passed = bool(
        set(coefficients) == expected_saved_names
        and constants["rho"] == ANALYTIC_RADIUS
        and constants["nonlinear_constant"]
        == NONLINEAR_DERIVATIVE_CONSTANT
        and constants["normal_cap"] == MAXIMUM_NORMAL_CONTRACTION
        and constants["domination_cap"] == MAXIMUM_DOMINATION_RATIO
        and all(reuse.values())
        and constants["c_v"] > 0
        and constants["tau"] > 0
        and constants["selected_radius"] > 0
        and constants["selected_minimum"] > 0
        and constants["q0"] > 0
        and constants["synthesis"] > 0
        and constants["analysis"] > 0
        and constants["selected_analysis"] > 0
    )
    audit = {
        "source": "sealed Q007p finite-tube majorant records",
        "coefficient_names": sorted(coefficients),
        "coefficient_count": len(coefficients),
        "formula_coefficient_names": sorted(expected_formula_names),
        "box_audit_coefficient_names": sorted(expected_box_audit_names),
        "constants": {
            name: _fraction_record(value)
            for name, value in constants.items()
        },
        "q007p_majorant_reuse_flags": reuse,
        "all_q007p_majorant_reuse_flags_true": all(reuse.values()),
        "passed": passed,
    }
    return constants, audit


def _polynomial_value(
    constants: dict[str, Fraction],
    prefix: str,
    radius: Fraction,
) -> Fraction:
    return sum(
        (constants[f"{prefix}{degree}"] * radius**degree for degree in (2, 3, 4)),
        Fraction(0),
    )


def _polynomial_derivative(
    constants: dict[str, Fraction],
    prefix: str,
    radius: Fraction,
) -> Fraction:
    return sum(
        (
            degree
            * constants[f"{prefix}{degree}"]
            * radius ** (degree - 1)
            for degree in (2, 3, 4)
        ),
        Fraction(0),
    )


def _evaluate_candidate(
    base_radius: Fraction,
    normal_radius: Fraction,
    constants: dict[str, Fraction],
) -> ExactCandidate:
    rho = constants["rho"]
    tau = constants["tau"]
    c_v = constants["c_v"]
    chart_radius = (
        c_v * base_radius
        + tau
        + _polynomial_value(constants, "h", base_radius)
    )
    reduced_radius = (
        constants["selected_radius"] * base_radius
        + tau / c_v
        + _polynomial_value(constants, "g", base_radius)
    )
    state_radius = chart_radius + constants["synthesis"] * normal_radius
    analytic_base_domain = bool(0 < base_radius < rho)
    state_domain = bool(0 <= state_radius < 1)

    nonlinear_derivative: Fraction | None = None
    base_image: Fraction | None = None
    chart_derivative: Fraction | None = None
    reduced_derivative: Fraction | None = None
    normal_contraction: Fraction | None = None
    tangent_conorm: Fraction | None = None
    domination_ratio: Fraction | None = None
    if state_domain:
        nonlinear_derivative = (
            constants["nonlinear_constant"]
            * state_radius
            * (2 - state_radius)
            / (1 - state_radius) ** 2
        )
        base_image = (
            reduced_radius
            + constants["selected_analysis"]
            * nonlinear_derivative
            * constants["synthesis"]
            * normal_radius
        )
    if analytic_base_domain:
        reduced_derivative = (
            _polynomial_derivative(constants, "g", base_radius)
            + tau / (c_v * (rho - base_radius))
        )
        tangent_conorm = constants["selected_minimum"] - reduced_derivative
    if base_image is not None and base_image < rho:
        chart_derivative = (
            _polynomial_derivative(constants, "h", base_image)
            + tau / (rho - base_image)
        )
    if nonlinear_derivative is not None and chart_derivative is not None:
        normal_contraction = (
            constants["q0"]
            + constants["analysis"]
            * constants["synthesis"]
            * nonlinear_derivative
            * (
                1
                + constants["selected_analysis"] * chart_derivative
            )
        )
    if (
        normal_contraction is not None
        and tangent_conorm is not None
        and tangent_conorm > 0
    ):
        domination_ratio = normal_contraction / tangent_conorm

    base_forward = bool(base_image is not None and base_image < base_radius)
    normal_contracting = bool(
        normal_contraction is not None
        and normal_contraction < constants["normal_cap"]
        and normal_contraction * normal_radius < normal_radius
    )
    tangent_invertible = bool(
        tangent_conorm is not None and tangent_conorm > 0
    )
    normally_dominating = bool(
        domination_ratio is not None
        and domination_ratio < constants["domination_cap"]
    )
    gates = {
        "analytic_base_domain": analytic_base_domain,
        "population_wiener_domain": state_domain,
        "base_forward_invariance": base_forward,
        "normal_contraction": normal_contracting,
        "tangent_invertibility": tangent_invertible,
        "strict_normal_domination": normally_dominating,
    }
    passed = all(gates.values())
    margins = {
        "analytic_base": rho - base_radius,
        "population_wiener": 1 - state_radius,
        "base_forward_invariance": (
            None if base_image is None else base_radius - base_image
        ),
        "normal_contraction_to_cap": (
            None
            if normal_contraction is None
            else constants["normal_cap"] - normal_contraction
        ),
        "normal_tube_forward_invariance": (
            None
            if normal_contraction is None
            else normal_radius - normal_contraction * normal_radius
        ),
        "tangent_invertibility": tangent_conorm,
        "domination_to_cap": (
            None
            if domination_ratio is None
            else constants["domination_cap"] - domination_ratio
        ),
        "domination_to_one": (
            None if domination_ratio is None else 1 - domination_ratio
        ),
    }
    return {
        "base_radius": base_radius,
        "normal_radius": normal_radius,
        "chart_radius": chart_radius,
        "reduced_radius": reduced_radius,
        "state_radius": state_radius,
        "nonlinear_derivative": nonlinear_derivative,
        "base_image": base_image,
        "chart_derivative": chart_derivative,
        "reduced_derivative": reduced_derivative,
        "normal_contraction": normal_contraction,
        "tangent_conorm": tangent_conorm,
        "domination_ratio": domination_ratio,
        "gates": gates,
        "margins": margins,
        "passed": passed,
    }


def _candidate_exact_record(candidate: ExactCandidate) -> dict[str, Any]:
    fraction_fields = (
        "base_radius",
        "normal_radius",
        "chart_radius",
        "reduced_radius",
        "state_radius",
        "nonlinear_derivative",
        "base_image",
        "chart_derivative",
        "reduced_derivative",
        "normal_contraction",
        "tangent_conorm",
        "domination_ratio",
    )
    return {
        **{
            name: _optional_fraction_record(candidate[name])
            for name in fraction_fields
        },
        "gates": candidate["gates"],
        "strict_margins": {
            name: _optional_fraction_record(value)
            for name, value in candidate["margins"].items()
        },
        "failed_gate_names": [
            name for name, passed in candidate["gates"].items() if not passed
        ],
        "passed": candidate["passed"],
    }


def _candidate_summary(candidate: ExactCandidate) -> dict[str, Any]:
    def optional_float(value: Fraction | None) -> float | None:
        return None if value is None else float(value)

    return {
        "base_radius": float(candidate["base_radius"]),
        "normal_radius": float(candidate["normal_radius"]),
        "state_radius_upper": float(candidate["state_radius"]),
        "base_forward_margin": optional_float(
            candidate["margins"]["base_forward_invariance"]
        ),
        "normal_contraction_upper": optional_float(
            candidate["normal_contraction"]
        ),
        "tangent_conorm_lower": optional_float(candidate["tangent_conorm"]),
        "domination_ratio_upper": optional_float(
            candidate["domination_ratio"]
        ),
        "failed_gate_names": [
            name for name, passed in candidate["gates"].items() if not passed
        ],
        "passed": candidate["passed"],
    }


def _canonical_fraction(value: Fraction | None) -> list[str] | None:
    if value is None:
        return None
    return [hex(value.numerator), hex(value.denominator)]


def _candidate_digest(candidates: list[ExactCandidate]) -> str:
    canonical = [
        {
            "r": _canonical_fraction(candidate["base_radius"]),
            "z": _canonical_fraction(candidate["normal_radius"]),
            "x": _canonical_fraction(candidate["state_radius"]),
            "a": _canonical_fraction(candidate["base_image"]),
            "q": _canonical_fraction(candidate["normal_contraction"]),
            "m": _canonical_fraction(candidate["tangent_conorm"]),
            "g": _canonical_fraction(candidate["domination_ratio"]),
            "gates": candidate["gates"],
            "passed": candidate["passed"],
        }
        for candidate in candidates
    ]
    encoded = json.dumps(
        canonical,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _registered_grids() -> tuple[list[Fraction], list[Fraction]]:
    base_radii = [Fraction(mantissa, 10**19) for mantissa in range(1, 10)]
    normal_radii = sorted(
        {
            Fraction(mantissa, 10**exponent)
            for exponent in range(10, 21)
            for mantissa in range(1, 10)
        }
    )
    return base_radii, normal_radii


def _control_reproduction(
    control: ExactCandidate,
    q007p: dict[str, Any],
) -> dict[str, Any]:
    majorant = q007p["cycle"]["finite_tube_majorant"]
    field_map = {
        "base_radius": "base_modal_l1_radius",
        "normal_radius": "normal_coordinate_radius",
        "chart_radius": "chart_radius_at_base_upper",
        "reduced_radius": "reduced_radius_at_base_upper",
        "state_radius": "tube_state_wiener_l1_upper",
        "nonlinear_derivative": "nonlinear_derivative_at_tube_state_upper",
        "base_image": "base_image_modal_l1_upper",
        "chart_derivative": "chart_derivative_at_base_image_upper",
        "reduced_derivative": "reduced_derivative_at_base_upper",
        "normal_contraction": "normal_fiber_contraction_upper",
        "tangent_conorm": "tangent_conorm_lower",
        "domination_ratio": "normal_domination_ratio_upper",
    }
    field_matches = {
        candidate_name: (
            control[candidate_name]
            == _fraction_from_record(majorant[artifact_name])
        )
        for candidate_name, artifact_name in field_map.items()
    }
    margin_map = {
        "population_wiener": "density",
        "analytic_base": "analytic_base",
        "base_forward_invariance": "base_forward_invariance",
        "normal_contraction_to_cap": "normal_contraction_to_registered_cap",
        "normal_tube_forward_invariance": "normal_tube_forward_invariance",
        "tangent_invertibility": "tangent_invertibility",
        "domination_to_cap": "domination_to_registered_cap",
        "domination_to_one": "domination_to_one",
    }
    saved_margins = majorant["strict_margins"]
    margin_matches = {
        candidate_name: (
            control["margins"][candidate_name]
            == _fraction_from_record(saved_margins[artifact_name])
        )
        for candidate_name, artifact_name in margin_map.items()
    }
    passed = bool(
        control["passed"]
        and all(field_matches.values())
        and all(margin_matches.values())
    )
    return {
        "control_candidate": _candidate_exact_record(control),
        "field_matches": field_matches,
        "margin_matches": margin_matches,
        "all_fields_match": all(field_matches.values()),
        "all_margins_match": all(margin_matches.values()),
        "passed": passed,
    }


def _slice_records(
    candidates: list[ExactCandidate],
    base_radii: list[Fraction],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for base_radius in base_radii:
        slice_candidates = [
            candidate
            for candidate in candidates
            if candidate["base_radius"] == base_radius
        ]
        passing = [candidate for candidate in slice_candidates if candidate["passed"]]
        largest = (
            None
            if not passing
            else max(passing, key=lambda candidate: candidate["normal_radius"])
        )
        larger = (
            []
            if largest is None
            else [
                candidate
                for candidate in slice_candidates
                if candidate["normal_radius"] > largest["normal_radius"]
            ]
        )
        first_larger = (
            None
            if not larger
            else min(larger, key=lambda candidate: candidate["normal_radius"])
        )
        records.append(
            {
                "base_radius": _fraction_record(base_radius),
                "candidate_count": len(slice_candidates),
                "passing_count": len(passing),
                "largest_passing_normal_radius": (
                    None
                    if largest is None
                    else _fraction_record(largest["normal_radius"])
                ),
                "first_larger_registered_candidate": (
                    None
                    if first_larger is None
                    else _candidate_exact_record(first_larger)
                ),
                "all_larger_registered_normal_candidates_fail": all(
                    not candidate["passed"] for candidate in larger
                ),
            }
        )
    return records


def run_finite_tube_enlargement_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007p, input_record = _load_registered_q007p(directory)
    constants, constants_audit = _extract_constants(q007p)
    base_radii, normal_radii = _registered_grids()
    candidates = [
        _evaluate_candidate(base_radius, normal_radius, constants)
        for base_radius in base_radii
        for normal_radius in normal_radii
    ]
    control = next(
        candidate
        for candidate in candidates
        if candidate["base_radius"] == CONTROL_BASE_RADIUS
        and candidate["normal_radius"] == CONTROL_NORMAL_RADIUS
    )
    control_reproduction = _control_reproduction(control, q007p)
    passing = [candidate for candidate in candidates if candidate["passed"]]
    selected = (
        None
        if not passing
        else max(
            passing,
            key=lambda candidate: (
                candidate["base_radius"],
                candidate["normal_radius"],
            ),
        )
    )
    digest = _candidate_digest(candidates)
    slices = _slice_records(candidates, base_radii)
    unique_grid = bool(
        len(base_radii) == len(set(base_radii)) == EXPECTED_BASE_COUNT
        and len(normal_radii) == len(set(normal_radii)) == EXPECTED_NORMAL_COUNT
        and len(candidates) == EXPECTED_CANDIDATE_COUNT
        and len(
            {
                (candidate["base_radius"], candidate["normal_radius"])
                for candidate in candidates
            }
        )
        == EXPECTED_CANDIDATE_COUNT
    )
    summaries = [_candidate_summary(candidate) for candidate in candidates]
    grid_audit = {
        "base_grid_formula": "m*10^-19 for m=1,...,9",
        "normal_grid_formula": "m*10^-e for e=10,...,20 and m=1,...,9",
        "base_radius_count": len(base_radii),
        "normal_radius_count": len(normal_radii),
        "candidate_count": len(candidates),
        "expected_candidate_count": EXPECTED_CANDIDATE_COUNT,
        "unique_cartesian_product": unique_grid,
        "control_candidate_present": any(
            candidate["base_radius"] == CONTROL_BASE_RADIUS
            and candidate["normal_radius"] == CONTROL_NORMAL_RADIUS
            for candidate in candidates
        ),
        "decision_arithmetic": "exact fractions.Fraction signs only",
        "canonical_digest_fraction_encoding": (
            "[hex numerator, hex denominator] with sorted compact JSON keys"
        ),
        "selection_rule": (
            "lexicographically maximize base radius, then normal radius, "
            "among passing candidates"
        ),
        "canonical_candidate_digest_sha256": digest,
        "candidate_summaries": summaries,
        "base_slice_boundaries": slices,
        "passed": unique_grid,
    }

    if selected is None:
        larger_normal_boundary = False
        larger_base_boundary = False
        selected_record = None
        base_improvement: Fraction | None = None
        normal_improvement: Fraction | None = None
    else:
        larger_normal = [
            candidate
            for candidate in candidates
            if candidate["base_radius"] == selected["base_radius"]
            and candidate["normal_radius"] > selected["normal_radius"]
        ]
        larger_base = [
            candidate
            for candidate in candidates
            if candidate["base_radius"] > selected["base_radius"]
        ]
        larger_normal_boundary = all(
            not candidate["passed"] for candidate in larger_normal
        )
        larger_base_boundary = all(
            not candidate["passed"] for candidate in larger_base
        )
        selected_record = _candidate_exact_record(selected)
        base_improvement = selected["base_radius"] / CONTROL_BASE_RADIUS
        normal_improvement = selected["normal_radius"] / CONTROL_NORMAL_RADIUS

    selection = {
        "passing_candidate_count": len(passing),
        "selected_candidate": selected_record,
        "base_radius_improvement_factor": _optional_fraction_record(
            base_improvement
        ),
        "normal_radius_improvement_factor": _optional_fraction_record(
            normal_improvement
        ),
        "all_larger_normals_on_selected_slice_fail_or_absent": (
            larger_normal_boundary
        ),
        "all_larger_base_slices_fail_or_absent": larger_base_boundary,
        "selection_boundary_reproduced": bool(
            selected is not None
            and larger_normal_boundary
            and larger_base_boundary
        ),
    }
    serializable_sections = {
        "input_artifact": input_record,
        "constant_reuse_audit": constants_audit,
        "control_reproduction": control_reproduction,
        "candidate_grid_audit": grid_audit,
        "selection": selection,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_q007p_input": {
            "passed": input_record["passed"],
            "threshold": (
                "Q007p artifact/runner SHA, source, scope, all upstream "
                "inputs, all gates, and four theorem flags match"
            ),
            "value": input_record["passed"],
        },
        "exact_majorant_constants_reused": {
            "passed": constants_audit["passed"],
            "threshold": (
                "rho, tau, seven jet constants, four coordinate constants, "
                "spectral bounds, nonlinear constant, and caps reuse Q007p"
            ),
            "value": constants_audit["passed"],
        },
        "q007p_control_reproduced": {
            "passed": control_reproduction["passed"],
            "threshold": (
                "all Q007p control values and eight strict margins reproduce "
                "exactly at r=1e-19 and zeta=1e-20"
            ),
            "value": control_reproduction["passed"],
        },
        "registered_grid_complete": {
            "passed": grid_audit["passed"],
            "threshold": "9 unique base by 99 unique normal radii give 891 candidates",
            "value": {
                "base": len(base_radii),
                "normal": len(normal_radii),
                "candidate": len(candidates),
            },
        },
        "exact_decisions_and_selection": {
            "passed": bool(
                len(digest) == 64
                and len(summaries) == EXPECTED_CANDIDATE_COUNT
                and grid_audit["decision_arithmetic"]
                == "exact fractions.Fraction signs only"
                and selection["selection_boundary_reproduced"]
            ),
            "threshold": (
                "all candidate gates use exact Fraction signs and the fixed "
                "lexicographic selection boundary is reproduced"
            ),
            "value": {
                "digest": digest,
                "selection_boundary": selection[
                    "selection_boundary_reproduced"
                ],
            },
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all saved values are finite and strict JSON serializable",
            "value": finite_strict_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    control_passed = bool(control["passed"])
    candidate_exists = selected is not None
    both_enlarged = bool(
        selected is not None
        and selected["base_radius"] > CONTROL_BASE_RADIUS
        and selected["normal_radius"] > CONTROL_NORMAL_RADIUS
    )
    boundary_passed = bool(
        selection["selection_boundary_reproduced"]
    )
    selected_all_gates = bool(
        selected is not None and selected["passed"] and all(selected["gates"].values())
    )
    hypothesis_gates = {
        "q007p_control_passes": {
            "passed": control_passed,
            "threshold": "the sealed Q007p control candidate passes",
            "value": control_passed,
        },
        "passing_candidate_exists": {
            "passed": candidate_exists,
            "threshold": "at least one of 891 registered candidates passes",
            "value": len(passing),
        },
        "both_radii_strictly_enlarged": {
            "passed": both_enlarged,
            "threshold": "selected r>1e-19 and selected zeta>1e-20",
            "value": {
                "base_improvement": (
                    None if base_improvement is None else float(base_improvement)
                ),
                "normal_improvement": (
                    None
                    if normal_improvement is None
                    else float(normal_improvement)
                ),
            },
        },
        "registered_selection_boundary": {
            "passed": boundary_passed,
            "threshold": (
                "larger normals on the selected base slice and larger base "
                "slices all fail or are absent"
            ),
            "value": selection["selection_boundary_reproduced"],
        },
        "selected_candidate_strictly_passes": {
            "passed": selected_all_gates,
            "threshold": "the selected candidate passes all six exact candidate gates",
            "value": (
                None if selected is None else selected["gates"]
            ),
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007s finite-tube enlargement audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered exact-manifold tube enlarged on the fixed rational "
            "candidate grid"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered rational grid did not enlarge both finite-tube radii"
        )

    return {
        "question": (
            "Can the exact Q007p tube be enlarged in both base and normal "
            "radius on the fixed rational candidate grid?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "control_base_radius": _fraction_record(CONTROL_BASE_RADIUS),
            "control_normal_radius": _fraction_record(CONTROL_NORMAL_RADIUS),
            "base_mantissas": list(range(1, 10)),
            "base_decimal_exponent": -19,
            "normal_mantissas": list(range(1, 10)),
            "normal_decimal_exponents": list(range(-20, -9)),
            "candidate_count": EXPECTED_CANDIDATE_COUNT,
            "selection_rule": "maximize base radius, then normal radius",
        },
        "input_artifact": input_record,
        "constant_reuse_audit": constants_audit,
        "control_reproduction": control_reproduction,
        "candidate_grid_audit": grid_audit,
        "selection": selection,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "selected_registered_tube_forward_invariant": hypotheses_passed,
            "selected_registered_tube_uniformly_normal_contracting": (
                hypotheses_passed
            ),
            "selected_registered_tube_strictly_normally_dominating": (
                hypotheses_passed
            ),
            "both_registered_tube_radii_strictly_enlarged": hypotheses_passed,
        },
        "claim_boundary": (
            "This certifies only the lexicographically selected point on the "
            "fixed 9-by-99 rational grid for the fixed 17x17 map, conservation "
            "leaf, exact manifold, and external-coordinate norm. It is not a "
            "continuous optimum, maximum possible tube, Euclidean or grid-"
            "uniform attraction result, global basin, or continuum limit. "
            "Q007q/Q007r positivity remains sealed to the old tube, and the "
            "Q007c1 finite-amplitude and Q007d Euclidean rejections are unchanged."
        ),
        "preserved_prior_outcomes": {
            "q007q_old_tube_positivity_acceptance_changed": False,
            "q007r_old_tube_stagewise_positivity_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, separately test population and stagewise positivity "
            "on the selected larger tube without changing this attraction result."
        ),
    }


def run_q007s_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_finite_tube_enlargement_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational finite-tube enlargement certificate",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold": "Q007o exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "candidate_grid": "9 base radii by 99 normal radii",
            "selection": "lexicographically maximize base then normal radius",
            "claim": (
                "forward invariance, one-step normal contraction, and strict "
                "normal domination for one selected registered tube only"
            ),
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
    result = run_q007s_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
