"""Sealed Q007q population-positivity certificate for the Q007p tube."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    VELOCITIES,
    WEIGHTS,
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_COMPLEX_DIMENSION = 24
EXTERNAL_COMPLEX_DIMENSION = 2574
BASE_RADIUS = Fraction(1, 10**19)
NORMAL_RADIUS = Fraction(1, 10**20)
Q007P_ARTIFACT = "q007p_finite_tube_attraction.json"
REGISTERED_Q007P_ARTIFACT_SHA256 = (
    "a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751"
)
REGISTERED_Q007P_RUNNER_SHA256 = (
    "23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a"
)
EXPECTED_WEIGHT_MULTIPLICITIES = {
    Fraction(4, 9): 1,
    Fraction(1, 9): 4,
    Fraction(1, 36): 4,
}


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
        scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == OMEGA
        and float(scope.get("eta", np.nan)) == ETA
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and scope.get("selected_real_dimension")
        == SELECTED_COMPLEX_DIMENSION
        and scope.get("external_complex_dimension")
        == EXTERNAL_COMPLEX_DIMENSION
        and float(scope.get("base_modal_l1_radius", np.nan))
        == float(BASE_RADIUS)
        and float(scope.get("normal_coordinate_radius", np.nan))
        == float(NORMAL_RADIUS)
    )
    theorem = payload.get("cycle", {}).get("theorem_consequence", {})
    theorem_flags_match = bool(len(theorem) == 4 and all(theorem.values()))
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
        and record["all_validity_gates_pass"]
        and record["all_hypothesis_gates_pass"]
        and theorem_flags_match
        and record["runner_sha_matches"]
    )
    return payload, record


def _weight_audit() -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    weights = tuple(Fraction(weight) for weight in WEIGHTS)
    counts = Counter(weights)
    rest_matches = bool(
        len(VELOCITIES) == 9
        and all(
            weight
            == (
                Fraction(4, 9)
                if cx == 0 and cy == 0
                else Fraction(1, 9)
                if cx * cx + cy * cy == 1
                else Fraction(1, 36)
            )
            for (cx, cy), weight in zip(VELOCITIES, weights, strict=True)
        )
    )
    weight_sum = sum(weights, Fraction(0))
    minimum = min(weights)
    maximum = max(weights)
    multiplicities_match = dict(counts) == EXPECTED_WEIGHT_MULTIPLICITIES
    passed = bool(
        len(weights) == 9
        and rest_matches
        and multiplicities_match
        and weight_sum == 1
        and minimum == Fraction(1, 36)
        and all(weight > 0 for weight in weights)
    )
    serializable = {
        "velocity_weight_records": [
            {
                "velocity": [int(cx), int(cy)],
                "weight": _fraction_record(weight),
            }
            for (cx, cy), weight in zip(VELOCITIES, weights, strict=True)
        ],
        "population_count": len(weights),
        "rest_axis_diagonal_multiplicity": [1, 4, 4],
        "registered_weight_multiplicities": [
            {
                "weight": _fraction_record(weight),
                "multiplicity": multiplicity,
            }
            for weight, multiplicity in EXPECTED_WEIGHT_MULTIPLICITIES.items()
        ],
        "observed_weight_multiplicities": [
            {
                "weight": _fraction_record(weight),
                "multiplicity": multiplicity,
            }
            for weight, multiplicity in sorted(
                counts.items(), reverse=True
            )
        ],
        "weight_sum": _fraction_record(weight_sum),
        "minimum_weight": _fraction_record(minimum),
        "maximum_weight": _fraction_record(maximum),
        "velocity_class_assignment_exact": rest_matches,
        "multiplicities_match": multiplicities_match,
        "all_weights_strictly_positive": all(weight > 0 for weight in weights),
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "weight_sum": weight_sum,
        "minimum_weight": minimum,
        "maximum_weight": maximum,
        "passed": passed,
    }
    return serializable, exact


def _wiener_triangle_audit(q007p: dict[str, Any]) -> dict[str, Any]:
    cycle = q007p["cycle"]
    coordinates = cycle["external_coordinate_certification"]
    global_norm = cycle["global_conversion_and_linear_bounds"]
    structural = cycle["structural_audit"]
    wave_count = int(coordinates["represented_wave_count"])
    norm_definition = global_norm["norm_definition"]
    real_constraint = structural["real_state_constraint"]
    norm_match = bool(
        "block-sum external-coordinate l1" in norm_definition
        and "physical population l1 at zero wave" in norm_definition
        and "real conjugacy subspace" in real_constraint
    )
    return {
        "construction_grid": [SIZE, SIZE],
        "fourier_wave_count": wave_count,
        "expected_fourier_wave_count": SIZE * SIZE,
        "inverse_fourier_convention": (
            "delta f_i(x) = sum_k delta f_hat[k,i] exp(i k dot x)"
        ),
        "phase_modulus_identity": "|exp(i k dot x)| = 1",
        "component_triangle_inequality": (
            "max_(x,i) |delta f_i(x)| <= max_i sum_k "
            "|delta f_hat[k,i]| <= sum_(k,i) |delta f_hat[k,i]|"
        ),
        "q007p_norm_definition": norm_definition,
        "q007p_real_state_constraint": real_constraint,
        "norm_definition_match": norm_match,
        "passed": bool(wave_count == SIZE * SIZE and norm_match),
    }


def run_population_positivity_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007p, input_record = _load_registered_q007p(directory)
    weight_section, weight_exact = _weight_audit()
    wiener_section = _wiener_triangle_audit(q007p)
    q007p_cycle = q007p["cycle"]
    majorant = q007p_cycle["finite_tube_majorant"]
    registered = q007p_cycle["registered_parameters"]
    theorem = q007p_cycle["theorem_consequence"]

    state_radius = _fraction_from_record(
        majorant["tube_state_wiener_l1_upper"]
    )
    chart_radius = _fraction_from_record(
        majorant["chart_radius_at_base_upper"]
    )
    synthesis = _fraction_from_record(
        q007p_cycle["global_conversion_and_linear_bounds"][
            "synthesis_to_wiener_l1_upper"
        ]
    )
    base_radius = _fraction_from_record(registered["base_radius"])
    normal_radius = _fraction_from_record(registered["normal_radius"])
    minimum_weight = weight_exact["minimum_weight"]
    maximum_weight = weight_exact["maximum_weight"]
    assert isinstance(minimum_weight, Fraction)
    assert isinstance(maximum_weight, Fraction)
    density_lower = 1 - state_radius
    population_lower = minimum_weight - state_radius
    population_upper = maximum_weight + state_radius
    state_radius_reproduced = bool(
        state_radius == chart_radius + synthesis * normal_radius
    )
    tube_reuse = {
        "base_modal_l1_radius": _fraction_record(base_radius),
        "normal_coordinate_radius": _fraction_record(normal_radius),
        "chart_radius_at_base_upper": _fraction_record(chart_radius),
        "synthesis_to_wiener_l1_upper": _fraction_record(synthesis),
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "state_radius_identity": "x_* = w(r) + K_s zeta",
        "state_radius_reproduced_exactly": state_radius_reproduced,
        "q007p_forward_invariance": theorem[
            "registered_tube_forward_invariant"
        ],
        "q007p_normal_contraction": theorem[
            "uniform_one_step_normal_fiber_contraction"
        ],
        "q007p_strict_normal_domination": theorem[
            "strict_normal_domination"
        ],
        "q007p_exact_manifold_identification": theorem[
            "identified_with_q007o_exact_manifold"
        ],
        "passed": bool(
            base_radius == BASE_RADIUS
            and normal_radius == NORMAL_RADIUS
            and state_radius_reproduced
            and len(theorem) == 4
            and all(theorem.values())
        ),
    }
    positivity = {
        "rest_equilibrium": "f_i^* = w_i at rho=1 and u=0",
        "tube_population_deviation_linf_upper": _fraction_record(state_radius),
        "minimum_rest_population": _fraction_record(minimum_weight),
        "maximum_rest_population": _fraction_record(maximum_weight),
        "registered_population_lower": _fraction_record(population_lower),
        "registered_population_upper": _fraction_record(population_upper),
        "registered_density_lower": _fraction_record(density_lower),
        "population_lower_formula": "p_* = 1/36 - x_*",
        "density_lower_formula": "d_* = 1 - x_*",
        "forward_iteration_deduction": (
            "Q007p maps the registered tube into itself, so the same lower "
            "bounds apply inductively at every full-map sampling time"
        ),
    }

    serializable_sections = {
        "input_artifact": input_record,
        "d2q9_weight_audit": weight_section,
        "wiener_triangle_audit": wiener_section,
        "q007p_tube_reuse": tube_reuse,
        "positivity_bounds": positivity,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_q007p_input": {
            "passed": input_record["passed"],
            "threshold": (
                "Q007p artifact/runner SHA, source, scope, all gates, and "
                "four theorem flags match"
            ),
            "value": input_record["passed"],
        },
        "exact_d2q9_weight_table": {
            "passed": weight_section["passed"],
            "threshold": (
                "nine weights have 1/4/4 multiplicities, sum one, minimum "
                "1/36, and are all strictly positive"
            ),
            "value": {
                "count": weight_section["population_count"],
                "sum": weight_section["weight_sum"]["float"],
                "minimum": weight_section["minimum_weight"]["float"],
            },
        },
        "fourier_wiener_triangle_inequality": {
            "passed": wiener_section["passed"],
            "threshold": (
                "289 phases have unit modulus and the registered block-sum "
                "Wiener norm bounds every physical population component"
            ),
            "value": {
                "wave_count": wiener_section["fourier_wave_count"],
                "norm_definition_match": wiener_section[
                    "norm_definition_match"
                ],
            },
        },
        "q007p_tube_bound_reused": {
            "passed": tube_reuse["passed"],
            "threshold": (
                "x_*, r, zeta, and all Q007p forward-invariance theorem "
                "flags reproduce exactly"
            ),
            "value": {
                "state_radius_reproduced": state_radius_reproduced,
                "forward_invariance": tube_reuse[
                    "q007p_forward_invariance"
                ],
            },
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all exact bounds are finite and strict JSON serializable",
            "value": finite_strict_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    forward_invariance = bool(theorem["registered_tube_forward_invariant"])
    hypothesis_gates = {
        "density_strictly_positive": {
            "passed": density_lower > 0,
            "threshold": "d_* = 1 - x_* > 0",
            "value": float(density_lower),
        },
        "all_populations_strictly_positive": {
            "passed": population_lower > 0,
            "threshold": "p_* = 1/36 - x_* > 0",
            "value": float(population_lower),
        },
        "full_map_forward_positivity": {
            "passed": bool(forward_invariance and population_lower > 0),
            "threshold": (
                "the registered tube is forward invariant and the same "
                "strict population lower applies to every full-map iterate"
            ),
            "value": {
                "forward_invariance": forward_invariance,
                "population_lower": float(population_lower),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007q population-positivity audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered Q007p tube lies in the strictly positive population "
            "cone at every full-map iterate"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered Q007p tube did not certify strict population positivity"
        )

    return {
        "question": (
            "Does the Q007p Wiener tube lie strictly inside the physical "
            "D2Q9 population cone at every full-map sampling time?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "base_radius": _fraction_record(BASE_RADIUS),
            "normal_radius": _fraction_record(NORMAL_RADIUS),
            "rest_density": _fraction_record(Fraction(1)),
            "rest_velocity": [0, 0],
        },
        "input_artifact": input_record,
        "d2q9_weight_audit": weight_section,
        "wiener_triangle_audit": wiener_section,
        "q007p_tube_reuse": tube_reuse,
        "positivity_bounds": positivity,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_tube_population_strictly_positive": hypotheses_passed,
            "registered_tube_density_strictly_positive": hypotheses_passed,
            "all_full_map_iterates_population_strictly_positive": (
                hypotheses_passed
            ),
        },
        "claim_boundary": (
            "This certifies strict population and density positivity only at "
            "the input/output times of the full one-step map for real states "
            "in the fixed Q007p tube. It does not certify positivity after "
            "collision, streaming, or internal filter stages, nor entropy, "
            "monotonicity, a maximum principle, a larger tube, a global "
            "basin, grid-uniformity, a continuum limit, Q007c1 finite-"
            "amplitude performance, or Q007d Euclidean contraction."
        ),
        "preserved_prior_outcomes": {
            "q007p_normal_attraction_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, keep the tiny Q007p tube fixed and treat any "
            "stagewise-positivity or larger-domain question as a separate gate."
        ),
    }


def run_q007q_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_population_positivity_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational population-positivity certificate",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "sampling_times": "full one-step map input/output only",
            "claim": (
                "strict D2Q9 population and density positivity on the fixed "
                "Q007p tube only; no stagewise, entropy, larger-domain, "
                "grid-uniform, or continuum claim"
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
    result = run_q007q_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
