"""Sealed Q007t full-map population positivity for the larger Q007s tube."""

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
BASE_RADIUS = Fraction(9, 10**19)
NORMAL_RADIUS = Fraction(5, 10**12)
Q007S_ARTIFACT = "q007s_finite_tube_enlargement.json"
REGISTERED_Q007S_ARTIFACT_SHA256 = (
    "7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292"
)
REGISTERED_Q007S_RUNNER_SHA256 = (
    "6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e"
)
REGISTERED_CANDIDATE_DIGEST = (
    "91fcc70355acfc4b7163c951227188960ef275408b06a678d45d5e4ec4c85300"
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


def _load_registered_q007s(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007S_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha256 = _file_sha256(artifact_path)
    runner_path = Path(__file__).resolve().with_name(
        "q007s_finite_tube_enlargement.py"
    )
    observed_runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    scope = payload.get("mathematical_scope", {})
    cycle = payload.get("cycle", {})
    selection = cycle.get("selection", {})
    selected = selection.get("selected_candidate", {})
    selected_gates = selected.get("gates", {})
    theorem = cycle.get("theorem_consequence", {})
    upstream = cycle.get("input_artifact", {})
    digest = cycle.get("candidate_grid_audit", {}).get(
        "canonical_candidate_digest_sha256"
    )
    selected_base = (
        _fraction_from_record(selected["base_radius"])
        if selected.get("base_radius")
        else None
    )
    selected_normal = (
        _fraction_from_record(selected["normal_radius"])
        if selected.get("normal_radius")
        else None
    )
    scope_match = bool(
        scope.get("diagnostic") == "rational finite-tube enlargement certificate"
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == OMEGA
        and float(scope.get("eta", np.nan)) == ETA
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and scope.get("manifold") == "Q007o exact graph-gauge manifold"
        and scope.get("norm")
        == "Q007p Fourier external-coordinate block-sum l1"
        and scope.get("candidate_grid") == "9 base radii by 99 normal radii"
        and scope.get("selection")
        == "lexicographically maximize base then normal radius"
    )
    theorem_matches = bool(len(theorem) == 4 and all(theorem.values()))
    selected_matches = bool(
        selected_base == BASE_RADIUS
        and selected_normal == NORMAL_RADIUS
        and selected.get("passed")
        and len(selected_gates) == 6
        and all(selected_gates.values())
        and selection.get("selection_boundary_reproduced")
    )
    record = {
        "filename": Q007S_ARTIFACT,
        "registered_sha256": REGISTERED_Q007S_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha256,
        "sha256_matches": (
            observed_artifact_sha256 == REGISTERED_Q007S_ARTIFACT_SHA256
        ),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": scope_match,
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "validity_gate_count": len(cycle.get("validity_gates", {})),
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload, "hypothesis_gates"
        ),
        "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
        "theorem_consequence_count": len(theorem),
        "all_theorem_consequences_true": theorem_matches,
        "canonical_candidate_digest": digest,
        "canonical_candidate_digest_matches": (
            digest == REGISTERED_CANDIDATE_DIGEST
        ),
        "selected_candidate_matches": selected_matches,
        "transitive_q007p_input_passed": upstream.get("passed", False),
        "transitive_q007p_filename": upstream.get("filename"),
        "transitive_q007p_sha256": upstream.get("sha256"),
        "registered_runner_sha256": REGISTERED_Q007S_RUNNER_SHA256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "observed_runner_sha256": observed_runner_sha256,
        "runner_sha_matches": bool(
            artifact_runner_sha256 == REGISTERED_Q007S_RUNNER_SHA256
            and observed_runner_sha256 == REGISTERED_Q007S_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and record["validity_gate_count"] == 6
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"] == 5
        and record["all_hypothesis_gates_pass"]
        and theorem_matches
        and record["canonical_candidate_digest_matches"]
        and selected_matches
        and record["transitive_q007p_input_passed"]
        and record["runner_sha_matches"]
    )
    return payload, record


def _load_transitive_q007p(
    directory: Path,
    q007s: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    registered = q007s["cycle"]["input_artifact"]
    filename = str(registered["filename"])
    artifact_path = directory / filename
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_sha256 = _file_sha256(artifact_path)
    passed = bool(
        registered["passed"]
        and observed_sha256 == registered["sha256"]
        and observed_sha256 == registered["registered_sha256"]
        and payload.get("source") == source_metadata()
        and payload.get("schema_version") == 1
        and payload.get("study_gate") == "passed"
        and payload.get("scientific_outcome") == "accepted"
    )
    return payload, {
        "filename": filename,
        "registered_by_q007s_sha256": registered["sha256"],
        "observed_sha256": observed_sha256,
        "sha256_matches": observed_sha256 == registered["sha256"],
        "source_match": payload.get("source") == source_metadata(),
        "passed": passed,
    }


def _weight_audit() -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    weights = tuple(Fraction(weight) for weight in WEIGHTS)
    counts = Counter(weights)
    class_assignment = bool(
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
    all_positive = all(weight > 0 for weight in weights)
    passed = bool(
        len(weights) == 9
        and class_assignment
        and multiplicities_match
        and weight_sum == 1
        and minimum == Fraction(1, 36)
        and all_positive
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
            for weight, multiplicity in sorted(counts.items(), reverse=True)
        ],
        "weight_sum": _fraction_record(weight_sum),
        "minimum_weight": _fraction_record(minimum),
        "maximum_weight": _fraction_record(maximum),
        "velocity_class_assignment_exact": class_assignment,
        "multiplicities_match": multiplicities_match,
        "all_weights_strictly_positive": all_positive,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "weight_sum": weight_sum,
        "minimum_weight": minimum,
        "maximum_weight": maximum,
        "passed": passed,
    }
    return serializable, exact


def _wiener_triangle_audit(
    q007s: dict[str, Any],
    q007p: dict[str, Any],
    transitive_record: dict[str, Any],
) -> dict[str, Any]:
    q007p_cycle = q007p["cycle"]
    coordinates = q007p_cycle["external_coordinate_certification"]
    global_norm = q007p_cycle["global_conversion_and_linear_bounds"]
    structural = q007p_cycle["structural_audit"]
    wave_count = int(coordinates["represented_wave_count"])
    norm_definition = global_norm["norm_definition"]
    real_constraint = structural["real_state_constraint"]
    q007s_norm = q007s["mathematical_scope"]["norm"]
    norm_match = bool(
        q007s_norm == "Q007p Fourier external-coordinate block-sum l1"
        and "block-sum external-coordinate l1" in norm_definition
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
        "q007s_norm": q007s_norm,
        "transitive_q007p_norm_definition": norm_definition,
        "transitive_q007p_real_state_constraint": real_constraint,
        "transitive_q007p_artifact": transitive_record,
        "norm_definition_match": norm_match,
        "passed": bool(
            transitive_record["passed"]
            and wave_count == SIZE * SIZE
            and norm_match
        ),
    }


def run_larger_tube_population_positivity_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007s, input_record = _load_registered_q007s(directory)
    q007p, transitive_record = _load_transitive_q007p(directory, q007s)
    weight_section, weight_exact = _weight_audit()
    wiener_section = _wiener_triangle_audit(
        q007s,
        q007p,
        transitive_record,
    )
    q007s_cycle = q007s["cycle"]
    selection = q007s_cycle["selection"]
    selected = selection["selected_candidate"]
    theorem = q007s_cycle["theorem_consequence"]
    constants = q007s_cycle["constant_reuse_audit"]["constants"]

    base_radius = _fraction_from_record(selected["base_radius"])
    normal_radius = _fraction_from_record(selected["normal_radius"])
    chart_radius = _fraction_from_record(selected["chart_radius"])
    state_radius = _fraction_from_record(selected["state_radius"])
    synthesis = _fraction_from_record(constants["synthesis"])
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
    candidate_gates = selected["gates"]
    forward_invariance = bool(
        theorem["selected_registered_tube_forward_invariant"]
    )
    tube_reuse = {
        "base_modal_l1_radius": _fraction_record(base_radius),
        "normal_coordinate_radius": _fraction_record(normal_radius),
        "chart_radius_at_base_upper": _fraction_record(chart_radius),
        "synthesis_to_wiener_l1_upper": _fraction_record(synthesis),
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "state_radius_identity": "x_* = w(r) + K_s zeta",
        "state_radius_reproduced_exactly": state_radius_reproduced,
        "selected_candidate_gates": candidate_gates,
        "all_selected_candidate_gates_pass": bool(
            len(candidate_gates) == 6 and all(candidate_gates.values())
        ),
        "q007s_forward_invariance": forward_invariance,
        "q007s_normal_contraction": theorem[
            "selected_registered_tube_uniformly_normal_contracting"
        ],
        "q007s_strict_normal_domination": theorem[
            "selected_registered_tube_strictly_normally_dominating"
        ],
        "q007s_both_radii_enlarged": theorem[
            "both_registered_tube_radii_strictly_enlarged"
        ],
        "passed": bool(
            base_radius == BASE_RADIUS
            and normal_radius == NORMAL_RADIUS
            and state_radius_reproduced
            and selected["passed"]
            and len(candidate_gates) == 6
            and all(candidate_gates.values())
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
            "Q007s maps the selected registered tube into itself, so the same "
            "lower bounds apply inductively at every full-map sampling time"
        ),
    }

    serializable_sections = {
        "input_artifact": input_record,
        "d2q9_weight_audit": weight_section,
        "wiener_triangle_audit": wiener_section,
        "q007s_tube_reuse": tube_reuse,
        "positivity_bounds": positivity,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_q007s_input": {
            "passed": input_record["passed"],
            "threshold": (
                "Q007s artifact/runner SHA, source, scope, six validity gates, "
                "five hypothesis gates, four theorem flags, and candidate "
                "digest match"
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
                "transitive_q007p_input": transitive_record["passed"],
            },
        },
        "q007s_selected_tube_bound_reused": {
            "passed": tube_reuse["passed"],
            "threshold": (
                "x_*, r, zeta, six candidate gates, and four Q007s theorem "
                "flags reproduce exactly"
            ),
            "value": {
                "state_radius_reproduced": state_radius_reproduced,
                "forward_invariance": forward_invariance,
                "candidate_gates": candidate_gates,
            },
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all exact bounds are finite and strict JSON serializable",
            "value": finite_strict_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
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
                "the selected Q007s tube is forward invariant and the same "
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
        classification = "registered Q007t population-positivity audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered Q007s larger tube lies in the strictly positive "
            "population cone at every full-map iterate"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered Q007s larger tube did not certify strict population "
            "positivity"
        )

    return {
        "question": (
            "Does the larger Q007s Wiener tube lie strictly inside the "
            "physical D2Q9 population cone at every full-map sampling time?"
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
        "q007s_tube_reuse": tube_reuse,
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
            "in the fixed Q007s selected tube. It does not certify positivity "
            "after equilibrium evaluation, collision, streaming, or filter "
            "stages; Q007r stagewise positivity remains sealed to the old "
            "Q007p tube. It also does not certify entropy, monotonicity, a "
            "maximum principle, IEEE-754 roundoff, a continuously optimal "
            "tube, a global basin, grid-uniformity, a continuum limit, Q007c1 "
            "finite-amplitude performance, or Q007d Euclidean contraction."
        ),
        "preserved_prior_outcomes": {
            "q007s_normal_attraction_acceptance_changed": False,
            "q007q_old_tube_positivity_acceptance_changed": False,
            "q007r_old_tube_stagewise_positivity_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, separately test exact equilibrium, collision, "
            "streaming, and filter-stage positivity on this same larger tube."
        ),
    }


def run_q007t_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_larger_tube_population_positivity_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational larger-tube population-positivity certificate",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "sampling_times": "full one-step map input/output only",
            "claim": (
                "strict D2Q9 population and density positivity on the fixed "
                "Q007s selected tube only; no stagewise, entropy, continuous-"
                "optimum, grid-uniform, or continuum claim"
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
    result = run_q007t_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
