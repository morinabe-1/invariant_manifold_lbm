"""Q007ah full-map population positivity on the propagated Q007ag tube.

The accepted Q007ag tube is reused without changing its exact Wiener state
bound.  The sealed Q007t old-tube certificate is replayed as a regression
oracle, while the D2Q9 weight table and Fourier-to-physical triangle bound
are reconstructed independently.  Only full-map input/output sampling times
are covered; stagewise positivity is deliberately left to Q007ai.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

import research.q007ag_tube_radius_propagation as q007ag
import research.q007p_finite_tube_attraction as q007p
import research.q007t_larger_tube_population_positivity as q007t
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
BASE_RADIUS = Fraction(9, 10**17)
NORMAL_RADIUS = Fraction(5, 10**11)
EXPECTED_STATE_RADIUS_FLOAT = 1.4441361143956586e-10
EXPECTED_POPULATION_LOWER_FLOAT = 0.027777777633364167
EXPECTED_DENSITY_LOWER_FLOAT = 0.9999999998555864
EXPECTED_POPULATION_UPPER_FLOAT = 0.44444444458885807

REGISTERED_Q007AG_DIGESTS = {
    "input": (
        "262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613"
    ),
    "candidate": (
        "a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408"
    ),
    "result": (
        "6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43"
    ),
}

REGISTERED_INPUTS = {
    "q007ag": {
        "module": q007ag,
        "filename": "q007ag_tube_radius_propagation.json",
        "artifact_sha256": (
            "5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200"
        ),
        "runner_sha256": (
            "bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0"
        ),
        "diagnostic": (
            "analytic-radius-propagated rational finite-tube enlargement "
            "certificate"
        ),
        "classification": (
            "Q007ae analytic radius enlarges the registered "
            "external-coordinate tube"
        ),
    },
    "q007t": {
        "module": q007t,
        "filename": "q007t_larger_tube_population_positivity.json",
        "artifact_sha256": (
            "2089d97aa19248cc17689f3e7a01e113540e5afc329ffa5cb3a4c511a43a8529"
        ),
        "runner_sha256": (
            "1e00281c71b5ea5d06fedcebd9bd483a73e6ec111388df20e8255ae3aefed877"
        ),
        "diagnostic": (
            "rational larger-tube population-positivity certificate"
        ),
        "classification": (
            "registered Q007s larger tube lies in the strictly positive "
            "population cone at every full-map iterate"
        ),
    },
    "q007p": {
        "module": q007p,
        "filename": "q007p_finite_tube_attraction.json",
        "artifact_sha256": (
            "a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751"
        ),
        "runner_sha256": (
            "23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a"
        ),
        "diagnostic": "rational finite-tube normal-attraction certificate",
        "classification": (
            "registered fixed-leaf tube is uniformly normally attracting "
            "in the external-coordinate norm"
        ),
    },
}

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


def _canonical_json_sha256(value: Any) -> str:
    serialized = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(serialized.encode("utf-8")).hexdigest()


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _common_scope_matches(payload: dict[str, Any]) -> bool:
    scope = payload.get("mathematical_scope", {})
    return bool(
        scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == OMEGA
        and float(scope.get("eta", np.nan)) == ETA
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
    )


def _load_registered_input(
    directory: Path,
    name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    registered = REGISTERED_INPUTS[name]
    artifact_path = directory / str(registered["filename"])
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    artifact_sha256 = _file_sha256(artifact_path)
    module = registered["module"]
    runner_path = Path(module.__file__).resolve()
    runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    cycle = payload.get("cycle", {})
    record = {
        "filename": registered["filename"],
        "artifact_sha256": artifact_sha256,
        "registered_artifact_sha256": registered["artifact_sha256"],
        "artifact_sha256_matches": (
            artifact_sha256 == registered["artifact_sha256"]
        ),
        "runner_filename": runner_path.name,
        "runner_sha256": runner_sha256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "registered_runner_sha256": registered["runner_sha256"],
        "runner_sha256_matches": bool(
            runner_sha256 == registered["runner_sha256"]
            and artifact_runner_sha256 == registered["runner_sha256"]
        ),
        "source_matches": payload.get("source") == source_metadata(),
        "common_scope_matches": _common_scope_matches(payload),
        "diagnostic_matches": (
            payload.get("mathematical_scope", {}).get("diagnostic")
            == registered["diagnostic"]
        ),
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "scientific_classification": cycle.get("scientific_classification"),
        "classification_matches": (
            cycle.get("scientific_classification")
            == registered["classification"]
        ),
        "validity_gate_count": len(cycle.get("validity_gates", {})),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload,
            "hypothesis_gates",
        ),
    }
    record["passed"] = bool(
        record["artifact_sha256_matches"]
        and record["runner_sha256_matches"]
        and record["source_matches"]
        and record["common_scope_matches"]
        and record["diagnostic_matches"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and record["classification_matches"]
        and record["all_validity_gates_pass"]
        and record["all_hypothesis_gates_pass"]
    )
    return payload, record


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    for name in REGISTERED_INPUTS:
        payload, record = _load_registered_input(directory, name)
        payloads[name] = payload
        records[name] = record
    return payloads, records


def _q007ag_reproduction(
    directory: Path,
    payload: dict[str, Any],
    q007p_payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    stored_cycle = payload["cycle"]
    fresh_cycle = q007ag.run_tube_radius_propagation_audit(directory)
    selected = stored_cycle["selection"]["selected_candidate"]
    theorem = stored_cycle["theorem_consequence"]
    base_radius = _fraction_from_record(selected["base_radius"])
    normal_radius = _fraction_from_record(selected["normal_radius"])
    chart_radius = _fraction_from_record(selected["chart_radius"])
    state_radius = _fraction_from_record(selected["state_radius"])
    synthesis = _fraction_from_record(
        q007p_payload["cycle"]["global_conversion_and_linear_bounds"][
            "synthesis_to_wiener_l1_upper"
        ]
    )
    state_identity = state_radius == chart_radius + synthesis * normal_radius
    observed_digests = {
        "input": stored_cycle.get("input_digest_sha256"),
        "candidate": stored_cycle.get("candidate_digest_sha256"),
        "result": stored_cycle.get("result_digest_sha256"),
    }
    expected_theorem = {
        "selected_registered_tube_forward_invariant": True,
        "selected_registered_tube_uniformly_normal_contracting": True,
        "selected_registered_tube_strictly_normally_dominating": True,
        "both_q007s_registered_tube_radii_strictly_enlarged": True,
        "new_tube_population_positivity_certified": False,
        "new_tube_stagewise_positivity_certified": False,
        "new_tube_binary64_or_mpfr_induction_certified": False,
    }
    candidate_gates = selected["gates"]
    passed = bool(
        stored_cycle == fresh_cycle
        and observed_digests == REGISTERED_Q007AG_DIGESTS
        and base_radius == BASE_RADIUS
        and normal_radius == NORMAL_RADIUS
        and state_identity
        and selected["passed"]
        and len(candidate_gates) == 6
        and all(candidate_gates.values())
        and theorem == expected_theorem
    )
    serializable = {
        "stored_cycle_reproduced_exactly": stored_cycle == fresh_cycle,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007AG_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007AG_DIGESTS,
        "base_modal_l1_radius": _fraction_record(base_radius),
        "normal_coordinate_radius": _fraction_record(normal_radius),
        "chart_radius_at_base_upper": _fraction_record(chart_radius),
        "synthesis_to_wiener_l1_upper": _fraction_record(synthesis),
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "state_radius_identity": "x_ag = w(r_ag) + K_s zeta_ag",
        "state_radius_reproduced_exactly": state_identity,
        "selected_candidate_gates": candidate_gates,
        "all_selected_candidate_gates_pass": bool(
            len(candidate_gates) == 6 and all(candidate_gates.values())
        ),
        "theorem_consequence": theorem,
        "expected_theorem_consequence": expected_theorem,
        "theorem_consequence_matches": theorem == expected_theorem,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "base_radius": base_radius,
        "normal_radius": normal_radius,
        "chart_radius": chart_radius,
        "synthesis": synthesis,
        "state_radius": state_radius,
        "forward_invariance": theorem[
            "selected_registered_tube_forward_invariant"
        ],
        "passed": passed,
    }
    return serializable, exact


def _q007t_oracle_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    stored_cycle = payload["cycle"]
    fresh_cycle = q007t.run_larger_tube_population_positivity_audit(directory)
    bounds = stored_cycle["positivity_bounds"]
    tube = stored_cycle["q007s_tube_reuse"]
    state_radius = _fraction_from_record(
        tube["tube_state_wiener_l1_upper"]
    )
    population_lower = _fraction_from_record(
        bounds["registered_population_lower"]
    )
    population_upper = _fraction_from_record(
        bounds["registered_population_upper"]
    )
    density_lower = _fraction_from_record(bounds["registered_density_lower"])
    exact_bounds_reproduced = bool(
        population_lower == Fraction(1, 36) - state_radius
        and population_upper == Fraction(4, 9) + state_radius
        and density_lower == 1 - state_radius
    )
    theorem = stored_cycle["theorem_consequence"]
    passed = bool(
        stored_cycle == fresh_cycle
        and stored_cycle["d2q9_weight_audit"]["passed"]
        and stored_cycle["wiener_triangle_audit"]["passed"]
        and tube["passed"]
        and exact_bounds_reproduced
        and len(stored_cycle["validity_gates"]) == 5
        and all(
            gate["passed"]
            for gate in stored_cycle["validity_gates"].values()
        )
        and len(stored_cycle["hypothesis_gates"]) == 3
        and all(
            gate["passed"]
            for gate in stored_cycle["hypothesis_gates"].values()
        )
        and len(theorem) == 3
        and all(theorem.values())
    )
    return {
        "stored_cycle_reproduced_exactly": stored_cycle == fresh_cycle,
        "validity_gate_count": len(stored_cycle["validity_gates"]),
        "all_validity_gates_pass": all(
            gate["passed"]
            for gate in stored_cycle["validity_gates"].values()
        ),
        "hypothesis_gate_count": len(stored_cycle["hypothesis_gates"]),
        "all_hypothesis_gates_pass": all(
            gate["passed"]
            for gate in stored_cycle["hypothesis_gates"].values()
        ),
        "theorem_consequence": theorem,
        "weight_table_passed": stored_cycle["d2q9_weight_audit"]["passed"],
        "wiener_triangle_audit_passed": stored_cycle[
            "wiener_triangle_audit"
        ]["passed"],
        "old_tube_reuse_passed": tube["passed"],
        "old_tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "old_registered_population_lower": _fraction_record(population_lower),
        "old_registered_population_upper": _fraction_record(population_upper),
        "old_registered_density_lower": _fraction_record(density_lower),
        "old_exact_bounds_reproduced": exact_bounds_reproduced,
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
        and maximum == Fraction(4, 9)
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
        "minimum": minimum,
        "maximum": maximum,
        "passed": passed,
    }
    return serializable, exact


def _wiener_triangle_audit(
    q007p_payload: dict[str, Any],
    q007p_record: dict[str, Any],
) -> dict[str, Any]:
    cycle = q007p_payload["cycle"]
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
        "transitive_q007p_norm_definition": norm_definition,
        "transitive_q007p_real_state_constraint": real_constraint,
        "norm_definition_match": norm_match,
        "transitive_q007p_input_passed": q007p_record["passed"],
        "passed": bool(
            q007p_record["passed"]
            and wave_count == SIZE * SIZE
            and norm_match
        ),
    }


def run_propagated_tube_population_positivity_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    q007ag_reproduction, q007ag_exact = _q007ag_reproduction(
        directory,
        payloads["q007ag"],
        payloads["q007p"],
    )
    q007t_reproduction = _q007t_oracle_reproduction(
        directory,
        payloads["q007t"],
    )
    weight_section, weight_exact = _weight_audit()
    wiener_section = _wiener_triangle_audit(
        payloads["q007p"],
        input_records["q007p"],
    )

    state_radius = q007ag_exact["state_radius"]
    minimum_weight = weight_exact["minimum"]
    maximum_weight = weight_exact["maximum"]
    assert isinstance(state_radius, Fraction)
    assert isinstance(minimum_weight, Fraction)
    assert isinstance(maximum_weight, Fraction)
    population_lower = minimum_weight - state_radius
    population_upper = maximum_weight + state_radius
    density_lower = 1 - state_radius
    forward_invariance = bool(q007ag_exact["forward_invariance"])

    tube_reuse = {
        "base_modal_l1_radius": q007ag_reproduction[
            "base_modal_l1_radius"
        ],
        "normal_coordinate_radius": q007ag_reproduction[
            "normal_coordinate_radius"
        ],
        "chart_radius_at_base_upper": q007ag_reproduction[
            "chart_radius_at_base_upper"
        ],
        "synthesis_to_wiener_l1_upper": q007ag_reproduction[
            "synthesis_to_wiener_l1_upper"
        ],
        "tube_state_wiener_l1_upper": q007ag_reproduction[
            "tube_state_wiener_l1_upper"
        ],
        "state_radius_identity": q007ag_reproduction[
            "state_radius_identity"
        ],
        "state_radius_reproduced_exactly": q007ag_reproduction[
            "state_radius_reproduced_exactly"
        ],
        "selected_candidate_gates": q007ag_reproduction[
            "selected_candidate_gates"
        ],
        "all_selected_candidate_gates_pass": q007ag_reproduction[
            "all_selected_candidate_gates_pass"
        ],
        "q007ag_forward_invariance": forward_invariance,
        "q007ag_normal_contraction": q007ag_reproduction[
            "theorem_consequence"
        ]["selected_registered_tube_uniformly_normal_contracting"],
        "q007ag_strict_normal_domination": q007ag_reproduction[
            "theorem_consequence"
        ]["selected_registered_tube_strictly_normally_dominating"],
        "q007ag_both_radii_enlarged": q007ag_reproduction[
            "theorem_consequence"
        ]["both_q007s_registered_tube_radii_strictly_enlarged"],
        "passed": q007ag_reproduction["passed"],
    }
    positivity = {
        "rest_equilibrium": "f_i^* = w_i at rho=1 and u=0",
        "tube_population_deviation_linf_upper": _fraction_record(
            state_radius
        ),
        "minimum_rest_population": _fraction_record(minimum_weight),
        "maximum_rest_population": _fraction_record(maximum_weight),
        "registered_population_lower": _fraction_record(population_lower),
        "registered_population_upper": _fraction_record(population_upper),
        "registered_density_lower": _fraction_record(density_lower),
        "population_lower_formula": "p_ag = 1/36 - x_ag",
        "density_lower_formula": "d_ag = 1 - x_ag",
        "forward_iteration_deduction": (
            "Q007ag maps the selected propagated tube into itself, so the "
            "same lower bounds apply inductively at every full-map sampling "
            "time"
        ),
        "preregistered_float_values": {
            "state_radius": EXPECTED_STATE_RADIUS_FLOAT,
            "population_lower": EXPECTED_POPULATION_LOWER_FLOAT,
            "density_lower": EXPECTED_DENSITY_LOWER_FLOAT,
            "population_upper": EXPECTED_POPULATION_UPPER_FLOAT,
        },
        "preregistered_float_values_match": bool(
            float(state_radius) == EXPECTED_STATE_RADIUS_FLOAT
            and float(population_lower) == EXPECTED_POPULATION_LOWER_FLOAT
            and float(density_lower) == EXPECTED_DENSITY_LOWER_FLOAT
            and float(population_upper) == EXPECTED_POPULATION_UPPER_FLOAT
        ),
    }

    input_digest_payload = {
        name: {
            "artifact_sha256": record["artifact_sha256"],
            "runner_sha256": record["runner_sha256"],
            "scientific_classification": record[
                "scientific_classification"
            ],
            "validity_gate_count": record["validity_gate_count"],
            "hypothesis_gate_count": record["hypothesis_gate_count"],
            "passed": record["passed"],
        }
        for name, record in input_records.items()
    }
    input_digest_sha256 = _canonical_json_sha256(input_digest_payload)
    result_digest_payload = {
        "q007ag_tube_reuse": tube_reuse,
        "positivity_bounds": positivity,
        "q007t_old_exact_bounds_reproduced": q007t_reproduction[
            "old_exact_bounds_reproduced"
        ],
        "weight_table_passed": weight_section["passed"],
        "wiener_triangle_passed": wiener_section["passed"],
    }
    result_digest_sha256 = _canonical_json_sha256(result_digest_payload)

    serializable_sections = {
        "input_artifacts": input_records,
        "q007ag_exact_reproduction": q007ag_reproduction,
        "q007t_oracle_reproduction": q007t_reproduction,
        "d2q9_weight_audit": weight_section,
        "wiener_triangle_audit": wiener_section,
        "q007ag_tube_reuse": tube_reuse,
        "positivity_bounds": positivity,
        "input_digest_sha256": input_digest_sha256,
        "result_digest_sha256": result_digest_sha256,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "sealed_inputs": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": (
                "Q007ag/Q007t/Q007p artifact and runner SHA, source, scope, "
                "schema, accepted outcome, and sealed classification match"
            ),
            "value": {
                name: record["passed"]
                for name, record in input_records.items()
            },
        },
        "q007ag_selected_tube_exactly_reproduced": {
            "passed": q007ag_reproduction["passed"],
            "threshold": (
                "Q007ag fresh cycle, three digests, selected radii, state "
                "identity, six candidate gates, and forward-invariance "
                "theorem reproduce exactly"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007ag_reproduction[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007ag_reproduction["digests_match"],
                "state_radius_reproduced_exactly": q007ag_reproduction[
                    "state_radius_reproduced_exactly"
                ],
            },
        },
        "q007t_old_population_oracle_reproduced": {
            "passed": q007t_reproduction["passed"],
            "threshold": (
                "Q007t fresh cycle, old weight/norm proof, exact positivity "
                "bounds, five validity gates, three hypothesis gates, and "
                "three theorem flags reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007t_reproduction[
                    "stored_cycle_reproduced_exactly"
                ],
                "old_exact_bounds_reproduced": q007t_reproduction[
                    "old_exact_bounds_reproduced"
                ],
            },
        },
        "exact_d2q9_weight_table": {
            "passed": weight_section["passed"],
            "threshold": (
                "nine exact weights have 1/4/4 multiplicities, sum one, "
                "minimum 1/36, maximum 4/9, and are all strictly positive"
            ),
            "value": {
                "count": weight_section["population_count"],
                "sum": weight_section["weight_sum"]["float"],
                "minimum": weight_section["minimum_weight"]["float"],
                "maximum": weight_section["maximum_weight"]["float"],
            },
        },
        "fourier_wiener_triangle_inequality": {
            "passed": wiener_section["passed"],
            "threshold": (
                "289 unit-modulus phases and the registered Q007p block-sum "
                "Wiener norm bound every physical population component"
            ),
            "value": {
                "wave_count": wiener_section["fourier_wave_count"],
                "norm_definition_match": wiener_section[
                    "norm_definition_match"
                ],
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": finite_strict_json,
            "threshold": (
                "all exact bounds are finite strict JSON and canonical "
                "input/result digests are emitted"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest_sha256,
                "result_digest_sha256": result_digest_sha256,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "density_strictly_positive": {
            "passed": density_lower > 0,
            "threshold": "d_ag = 1 - x_ag > 0",
            "value": float(density_lower),
        },
        "all_populations_strictly_positive": {
            "passed": population_lower > 0,
            "threshold": "p_ag = 1/36 - x_ag > 0",
            "value": float(population_lower),
        },
        "full_map_forward_positivity": {
            "passed": bool(forward_invariance and population_lower > 0),
            "threshold": (
                "the Q007ag tube is forward invariant and the same strict "
                "population lower applies to every full-map iterate"
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
        classification = "registered Q007ah population-positivity audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered Q007ag propagated tube lies in the strictly positive "
            "population cone at every full-map iterate"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered Q007ag propagated tube did not certify strict "
            "full-map population positivity"
        )

    return {
        "question": (
            "Does the propagated Q007ag Wiener tube lie strictly inside the "
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
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_q007ag_tube_population_strictly_positive": (
                hypotheses_passed
            ),
            "registered_q007ag_tube_density_strictly_positive": (
                hypotheses_passed
            ),
            "all_full_map_iterates_population_strictly_positive": (
                hypotheses_passed
            ),
            "registered_q007ag_tube_stagewise_positivity_certified": False,
        },
        "claim_boundary": (
            "This certifies strict population and density positivity only at "
            "the input/output times of the exact full one-step map for real "
            "states in the fixed Q007ag selected tube. It does not certify "
            "positivity after equilibrium evaluation, BGK collision, "
            "streaming, or filter stages; those remain a separate Q007ai "
            "gate. It also does not certify entropy, monotonicity, a maximum "
            "principle, IEEE-754 roundoff, Q007v--Q007ab finite-precision "
            "induction, a continuously optimal tube, a global basin, grid "
            "uniformity, or a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007ag_normal_attraction_acceptance_changed": False,
            "q007t_old_tube_positivity_acceptance_changed": False,
            "q007u_old_tube_stagewise_positivity_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007af_external_disc_obstruction_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister Q007ai exact equilibrium, collision, "
            "streaming, and filter-stage positivity on this same Q007ag tube."
        ),
    }


def run_q007ah_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_propagated_tube_population_positivity_audit(
        artifact_directory
    )
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "rational propagated-tube population-positivity certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "sampling_times": "full one-step map input/output only",
            "claim": (
                "strict D2Q9 population and density positivity on the fixed "
                "Q007ag selected tube only; no stagewise, finite-precision, "
                "continuous-optimum, grid-uniform, or continuum claim"
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
    result = run_q007ah_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
