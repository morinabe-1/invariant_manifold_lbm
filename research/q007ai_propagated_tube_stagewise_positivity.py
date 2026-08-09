"""Q007ai exact stagewise positivity on the propagated Q007ag tube.

The sealed Q007ah full-map certificate supplies the exact Q007ag tube state
bound and forward invariance.  The sealed Q007u old-tube stagewise result is
freshly replayed as a regression oracle.  Exact D2Q9 linear/nonlinear
majorants, periodic streaming permutations, and the convex five-point filter
are then evaluated at the propagated tube bound.  IEEE-754 roundoff remains
outside this gate.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

import research.q007ah_propagated_tube_population_positivity as q007ah
import research.q007u_larger_tube_stagewise_positivity as q007u
from ttim_lbm import checkerboard_filter, d2q9
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = Fraction(3, 2)
ETA = Fraction(1, 100)
BASE_RADIUS = Fraction(9, 10**17)
NORMAL_RADIUS = Fraction(5, 10**11)

EXPECTED_STATE_RADIUS_FLOAT = 1.4441361143956586e-10
EXPECTED_DENSITY_BUFFER_FLOAT = 0.9999999998555864
EXPECTED_EQUILIBRIUM_NONLINEAR_FLOAT = 1.459870382042079e-19
EXPECTED_COLLISION_NONLINEAR_FLOAT = 2.1898055730631184e-19
EXPECTED_EQUILIBRIUM_DEVIATION_FLOAT = 3.1289615826504644e-10
EXPECTED_COLLISION_DEVIATION_FLOAT = 4.5730976977760583e-10
EXPECTED_EQUILIBRIUM_LOWER_FLOAT = 0.02777777746488162
EXPECTED_COLLISION_LOWER_FLOAT = 0.027777777320468006

REGISTERED_Q007AH_DIGESTS = {
    "input": (
        "6d7bd69b5c90ff7dbabd5193a4536809f4b79eef36a41fb288ab7caec44321b4"
    ),
    "result": (
        "caea5280667e909f17922260ef0d78998b6a8b374cd048b4b3e526185f040921"
    ),
}

REGISTERED_INPUTS = {
    "q007ah": {
        "module": q007ah,
        "filename": "q007ah_propagated_tube_population_positivity.json",
        "artifact_sha256": (
            "cab5ecc090b794a21a21fded8e5c503eca40be2bbc6502767c29844ba8209fa9"
        ),
        "runner_sha256": (
            "f29a974f0219af1767140e977775aa95dcf22b41a36de7a97bb553d540968d27"
        ),
        "diagnostic": (
            "rational propagated-tube population-positivity certificate"
        ),
        "classification": (
            "registered Q007ag propagated tube lies in the strictly positive "
            "population cone at every full-map iterate"
        ),
        "validity_gate_count": 6,
        "hypothesis_gate_count": 3,
        "theorem_consequence_count": 4,
    },
    "q007u": {
        "module": q007u,
        "filename": "q007u_larger_tube_stagewise_positivity.json",
        "artifact_sha256": (
            "b568fc304fd939121dd52543f316cb571ae6f4be4f4f664c68fe1c749b566c55"
        ),
        "runner_sha256": (
            "56fc99f1f381e97e70710c7da0cee8d1262d0c10190cf617316f822d1eb29014"
        ),
        "diagnostic": (
            "rational larger-tube exact stagewise-positivity certificate"
        ),
        "classification": (
            "registered Q007s larger tube is population-positive at every "
            "exact BGK, streaming, and filter stage"
        ),
        "validity_gate_count": 6,
        "hypothesis_gate_count": 5,
        "theorem_consequence_count": 5,
    },
}

REGISTERED_IMPLEMENTATIONS = {
    "d2q9": {
        "module": d2q9,
        "path": "src/ttim_lbm/d2q9.py",
        "sha256": (
            "6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53"
        ),
    },
    "checkerboard_filter": {
        "module": checkerboard_filter,
        "path": "src/ttim_lbm/checkerboard_filter.py",
        "sha256": (
            "5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea"
        ),
    },
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
        and float(scope.get("omega", np.nan)) == float(OMEGA)
        and float(scope.get("eta", np.nan)) == float(ETA)
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
    theorem = cycle.get("theorem_consequence", {})
    if name == "q007ah":
        theorem_flags_match = bool(
            theorem.get(
                "registered_q007ag_tube_population_strictly_positive"
            )
            and theorem.get(
                "registered_q007ag_tube_density_strictly_positive"
            )
            and theorem.get(
                "all_full_map_iterates_population_strictly_positive"
            )
            and not theorem.get(
                "registered_q007ag_tube_stagewise_positivity_certified"
            )
            and len(theorem) == 4
        )
    else:
        theorem_flags_match = bool(
            len(theorem) == registered["theorem_consequence_count"]
            and all(theorem.values())
        )
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
        "registered_validity_gate_count": registered["validity_gate_count"],
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
        "registered_hypothesis_gate_count": registered[
            "hypothesis_gate_count"
        ],
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload,
            "hypothesis_gates",
        ),
        "theorem_consequence_count": len(theorem),
        "registered_theorem_consequence_count": registered[
            "theorem_consequence_count"
        ],
        "theorem_flags_match": theorem_flags_match,
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
        and record["validity_gate_count"]
        == record["registered_validity_gate_count"]
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"]
        == record["registered_hypothesis_gate_count"]
        and record["all_hypothesis_gates_pass"]
        and record["theorem_consequence_count"]
        == record["registered_theorem_consequence_count"]
        and theorem_flags_match
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


def _implementation_source_audit() -> dict[str, Any]:
    records: dict[str, Any] = {}
    for name, registered in REGISTERED_IMPLEMENTATIONS.items():
        module = registered["module"]
        path = Path(module.__file__).resolve()
        observed = _file_sha256(path)
        records[name] = {
            "path": registered["path"],
            "sha256": observed,
            "registered_sha256": registered["sha256"],
            "passed": observed == registered["sha256"],
        }
    return {
        "records": records,
        "matching_source_count": sum(
            record["passed"] for record in records.values()
        ),
        "expected_source_count": len(records),
        "all_registered_implementation_sha256_match": all(
            record["passed"] for record in records.values()
        ),
    }


def _q007ah_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    stored_cycle = payload["cycle"]
    fresh_cycle = q007ah.run_propagated_tube_population_positivity_audit(
        directory
    )
    tube = stored_cycle["q007ag_tube_reuse"]
    bounds = stored_cycle["positivity_bounds"]
    theorem = stored_cycle["theorem_consequence"]
    base_radius = _fraction_from_record(tube["base_modal_l1_radius"])
    normal_radius = _fraction_from_record(tube["normal_coordinate_radius"])
    chart_radius = _fraction_from_record(tube["chart_radius_at_base_upper"])
    synthesis = _fraction_from_record(
        tube["synthesis_to_wiener_l1_upper"]
    )
    state_radius = _fraction_from_record(
        tube["tube_state_wiener_l1_upper"]
    )
    population_lower = _fraction_from_record(
        bounds["registered_population_lower"]
    )
    observed_digests = {
        "input": stored_cycle.get("input_digest_sha256"),
        "result": stored_cycle.get("result_digest_sha256"),
    }
    state_identity = state_radius == chart_radius + synthesis * normal_radius
    candidate_gates = tube["selected_candidate_gates"]
    forward_invariance = bool(tube["q007ag_forward_invariance"])
    passed = bool(
        stored_cycle == fresh_cycle
        and observed_digests == REGISTERED_Q007AH_DIGESTS
        and base_radius == BASE_RADIUS
        and normal_radius == NORMAL_RADIUS
        and state_identity
        and population_lower == Fraction(1, 36) - state_radius
        and len(candidate_gates) == 6
        and all(candidate_gates.values())
        and forward_invariance
        and tube["passed"]
        and theorem[
            "registered_q007ag_tube_population_strictly_positive"
        ]
        and theorem["all_full_map_iterates_population_strictly_positive"]
        and not theorem[
            "registered_q007ag_tube_stagewise_positivity_certified"
        ]
    )
    serializable = {
        "stored_cycle_reproduced_exactly": stored_cycle == fresh_cycle,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007AH_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007AH_DIGESTS,
        "base_modal_l1_radius": _fraction_record(base_radius),
        "normal_coordinate_radius": _fraction_record(normal_radius),
        "chart_radius_at_base_upper": _fraction_record(chart_radius),
        "synthesis_to_wiener_l1_upper": _fraction_record(synthesis),
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "q007ah_full_map_population_lower": _fraction_record(
            population_lower
        ),
        "state_radius_identity": "x_ag = w(r_ag) + K_s zeta_ag",
        "state_radius_reproduced_exactly": state_identity,
        "selected_candidate_gates": candidate_gates,
        "all_selected_candidate_gates_pass": bool(
            len(candidate_gates) == 6 and all(candidate_gates.values())
        ),
        "q007ag_forward_invariance": forward_invariance,
        "theorem_consequence": theorem,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "base_radius": base_radius,
        "normal_radius": normal_radius,
        "state_radius": state_radius,
        "full_map_population_lower": population_lower,
        "forward_invariance": forward_invariance,
        "passed": passed,
    }
    return serializable, exact


def _q007u_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    stored_cycle = payload["cycle"]
    fresh_cycle = q007u.run_larger_tube_stagewise_positivity_audit(directory)
    linear = stored_cycle["linear_operator_audit"]
    nonlinear = stored_cycle["nonlinear_majorant_audit"]
    structure = stored_cycle["stage_structure_audit"]
    bounds = stored_cycle["stage_bounds"]
    state_radius = _fraction_from_record(
        bounds["input_state_wiener_l1_upper"]
    )
    equilibrium_deviation = (
        Fraction(13, 6) * state_radius
        + 7 * state_radius**2 / (1 - state_radius)
    )
    collision_deviation = (
        Fraction(19, 6) * state_radius
        + Fraction(21, 2) * state_radius**2 / (1 - state_radius)
    )
    exact_bounds_reproduced = bool(
        _fraction_from_record(
            bounds["equilibrium_deviation_wiener_l1_upper"]
        )
        == equilibrium_deviation
        and _fraction_from_record(
            bounds["post_collision_deviation_wiener_l1_upper"]
        )
        == collision_deviation
        and _fraction_from_record(bounds["equilibrium_population_lower"])
        == Fraction(1, 36) - equilibrium_deviation
        and _fraction_from_record(bounds["post_collision_population_lower"])
        == Fraction(1, 36) - collision_deviation
        and _fraction_from_record(bounds["post_streaming_population_lower"])
        == Fraction(1, 36) - collision_deviation
        and _fraction_from_record(bounds["post_filter_population_lower"])
        == Fraction(1, 36) - collision_deviation
    )
    passed = bool(
        stored_cycle == fresh_cycle
        and linear["passed"]
        and nonlinear["passed"]
        and structure["passed"]
        and stored_cycle["q007s_tube_reuse"]["passed"]
        and exact_bounds_reproduced
        and len(stored_cycle["validity_gates"]) == 6
        and all(
            gate["passed"]
            for gate in stored_cycle["validity_gates"].values()
        )
        and len(stored_cycle["hypothesis_gates"]) == 5
        and all(
            gate["passed"]
            for gate in stored_cycle["hypothesis_gates"].values()
        )
        and len(stored_cycle["theorem_consequence"]) == 5
        and all(stored_cycle["theorem_consequence"].values())
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
        "theorem_consequence": stored_cycle["theorem_consequence"],
        "linear_operator_audit_passed": linear["passed"],
        "nonlinear_majorant_audit_passed": nonlinear["passed"],
        "stage_structure_audit_passed": structure["passed"],
        "old_tube_reuse_passed": stored_cycle["q007s_tube_reuse"][
            "passed"
        ],
        "old_exact_stage_bounds_reproduced": exact_bounds_reproduced,
        "passed": passed,
    }


def run_propagated_tube_stagewise_positivity_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    implementation_audit = _implementation_source_audit()
    q007ah_reproduction, q007ah_exact = _q007ah_reproduction(
        directory,
        payloads["q007ah"],
    )
    q007u_reproduction = _q007u_reproduction(
        directory,
        payloads["q007u"],
    )
    linear_section, linear_exact = q007u._linear_operator_audit()
    state_radius = q007ah_exact["state_radius"]
    assert isinstance(state_radius, Fraction)
    nonlinear_section, nonlinear_exact = q007u._nonlinear_majorant_audit(
        state_radius
    )
    structure = q007u._stage_structure_audit()

    equilibrium_linear_norm = linear_exact["equilibrium_linear_norm"]
    collision_linear_norm = linear_exact["collision_linear_norm"]
    equilibrium_nonlinear = nonlinear_exact["equilibrium_nonlinear"]
    collision_nonlinear = nonlinear_exact["collision_nonlinear"]
    density_buffer = nonlinear_exact["density_buffer"]
    assert isinstance(equilibrium_linear_norm, Fraction)
    assert isinstance(collision_linear_norm, Fraction)
    assert isinstance(equilibrium_nonlinear, Fraction)
    assert isinstance(collision_nonlinear, Fraction)
    assert isinstance(density_buffer, Fraction)

    minimum_weight = Fraction(1, 36)
    equilibrium_deviation = (
        equilibrium_linear_norm * state_radius + equilibrium_nonlinear
    )
    collision_deviation = (
        collision_linear_norm * state_radius + collision_nonlinear
    )
    equilibrium_lower = minimum_weight - equilibrium_deviation
    collision_lower = minimum_weight - collision_deviation
    stream_lower = collision_lower
    filter_lower = collision_lower
    full_map_lower = q007ah_exact["full_map_population_lower"]
    forward_invariance = bool(q007ah_exact["forward_invariance"])
    assert isinstance(full_map_lower, Fraction)

    preregistered_float_values_match = bool(
        float(state_radius) == EXPECTED_STATE_RADIUS_FLOAT
        and float(density_buffer) == EXPECTED_DENSITY_BUFFER_FLOAT
        and float(equilibrium_nonlinear)
        == EXPECTED_EQUILIBRIUM_NONLINEAR_FLOAT
        and float(collision_nonlinear)
        == EXPECTED_COLLISION_NONLINEAR_FLOAT
        and float(equilibrium_deviation)
        == EXPECTED_EQUILIBRIUM_DEVIATION_FLOAT
        and float(collision_deviation)
        == EXPECTED_COLLISION_DEVIATION_FLOAT
        and float(equilibrium_lower) == EXPECTED_EQUILIBRIUM_LOWER_FLOAT
        and float(collision_lower) == EXPECTED_COLLISION_LOWER_FLOAT
    )
    tube_reuse = {
        "base_modal_l1_radius": q007ah_reproduction[
            "base_modal_l1_radius"
        ],
        "normal_coordinate_radius": q007ah_reproduction[
            "normal_coordinate_radius"
        ],
        "tube_state_wiener_l1_upper": q007ah_reproduction[
            "tube_state_wiener_l1_upper"
        ],
        "q007ah_full_map_population_lower": q007ah_reproduction[
            "q007ah_full_map_population_lower"
        ],
        "selected_candidate_gates": q007ah_reproduction[
            "selected_candidate_gates"
        ],
        "all_selected_candidate_gates_pass": q007ah_reproduction[
            "all_selected_candidate_gates_pass"
        ],
        "q007ag_forward_invariance": forward_invariance,
        "state_radius_reproduced_exactly": q007ah_reproduction[
            "state_radius_reproduced_exactly"
        ],
        "passed": q007ah_reproduction["passed"],
    }
    stage_bounds = {
        "input_state_wiener_l1_upper": _fraction_record(state_radius),
        "minimum_rest_population": _fraction_record(minimum_weight),
        "q007ah_input_population_lower": _fraction_record(full_map_lower),
        "density_denominator_lower": _fraction_record(density_buffer),
        "equilibrium_nonlinear_remainder_upper": _fraction_record(
            equilibrium_nonlinear
        ),
        "collision_nonlinear_remainder_upper": _fraction_record(
            collision_nonlinear
        ),
        "equilibrium_deviation_wiener_l1_upper": _fraction_record(
            equilibrium_deviation
        ),
        "equilibrium_population_lower": _fraction_record(equilibrium_lower),
        "post_collision_deviation_wiener_l1_upper": _fraction_record(
            collision_deviation
        ),
        "post_collision_population_lower": _fraction_record(collision_lower),
        "post_streaming_population_lower": _fraction_record(stream_lower),
        "post_filter_population_lower": _fraction_record(filter_lower),
        "q007ah_full_map_output_population_lower": _fraction_record(
            full_map_lower
        ),
        "equilibrium_deviation_formula": (
            "(13/6)*x_ag + 7*x_ag^2/(1-x_ag)"
        ),
        "collision_deviation_formula": (
            "(19/6)*x_ag + (21/2)*x_ag^2/(1-x_ag)"
        ),
        "streaming_lower_identity": "p_stream = p_coll",
        "filter_lower_identity": "p_filter = p_coll",
        "preregistered_float_values": {
            "state_radius": EXPECTED_STATE_RADIUS_FLOAT,
            "density_buffer": EXPECTED_DENSITY_BUFFER_FLOAT,
            "equilibrium_nonlinear": (
                EXPECTED_EQUILIBRIUM_NONLINEAR_FLOAT
            ),
            "collision_nonlinear": EXPECTED_COLLISION_NONLINEAR_FLOAT,
            "equilibrium_deviation": EXPECTED_EQUILIBRIUM_DEVIATION_FLOAT,
            "collision_deviation": EXPECTED_COLLISION_DEVIATION_FLOAT,
            "equilibrium_population_lower": (
                EXPECTED_EQUILIBRIUM_LOWER_FLOAT
            ),
            "collision_population_lower": EXPECTED_COLLISION_LOWER_FLOAT,
        },
        "preregistered_float_values_match": (
            preregistered_float_values_match
        ),
    }

    input_digest_payload = {
        "artifacts": {
            name: {
                "artifact_sha256": record["artifact_sha256"],
                "runner_sha256": record["runner_sha256"],
                "scientific_classification": record[
                    "scientific_classification"
                ],
                "passed": record["passed"],
            }
            for name, record in input_records.items()
        },
        "implementations": {
            name: {
                "sha256": record["sha256"],
                "passed": record["passed"],
            }
            for name, record in implementation_audit["records"].items()
        },
    }
    input_digest_sha256 = _canonical_json_sha256(input_digest_payload)
    result_digest_payload = {
        "tube_reuse": tube_reuse,
        "linear_operator_audit": linear_section,
        "nonlinear_majorant_audit": nonlinear_section,
        "stage_structure_audit": structure,
        "stage_bounds": stage_bounds,
        "q007u_old_exact_stage_bounds_reproduced": q007u_reproduction[
            "old_exact_stage_bounds_reproduced"
        ],
    }
    result_digest_sha256 = _canonical_json_sha256(result_digest_payload)

    serializable_sections = {
        "input_artifacts": input_records,
        "implementation_source_audit": implementation_audit,
        "q007ah_exact_reproduction": q007ah_reproduction,
        "q007u_oracle_reproduction": q007u_reproduction,
        "linear_operator_audit": linear_section,
        "nonlinear_majorant_audit": nonlinear_section,
        "stage_structure_audit": structure,
        "q007ag_tube_reuse": tube_reuse,
        "stage_bounds": stage_bounds,
        "input_digest_sha256": input_digest_sha256,
        "result_digest_sha256": result_digest_sha256,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "sealed_inputs_and_implementations": {
            "passed": bool(
                all(record["passed"] for record in input_records.values())
                and implementation_audit[
                    "all_registered_implementation_sha256_match"
                ]
            ),
            "threshold": (
                "Q007ah/Q007u artifact and runner SHA, source, scope, "
                "accepted gates plus D2Q9/filter implementation SHA match"
            ),
            "value": {
                "artifact_input_count": sum(
                    record["passed"] for record in input_records.values()
                ),
                "artifact_input_expected": len(input_records),
                "implementation_count": implementation_audit[
                    "matching_source_count"
                ],
                "implementation_expected": implementation_audit[
                    "expected_source_count"
                ],
            },
        },
        "q007ah_selected_tube_exactly_reproduced": {
            "passed": q007ah_reproduction["passed"],
            "threshold": (
                "Q007ah fresh cycle, two digests, selected tube, state "
                "identity, positivity bound, and forward invariance reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007ah_reproduction[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007ah_reproduction["digests_match"],
                "state_radius_reproduced_exactly": q007ah_reproduction[
                    "state_radius_reproduced_exactly"
                ],
            },
        },
        "q007u_old_stagewise_oracle_reproduced": {
            "passed": q007u_reproduction["passed"],
            "threshold": (
                "Q007u fresh cycle, six validity gates, five hypothesis "
                "gates, five theorem flags, operator/majorant/structure, and "
                "old exact stage bounds reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007u_reproduction[
                    "stored_cycle_reproduced_exactly"
                ],
                "old_exact_stage_bounds_reproduced": q007u_reproduction[
                    "old_exact_stage_bounds_reproduced"
                ],
            },
        },
        "exact_linear_stage_operators": {
            "passed": linear_section["passed"],
            "threshold": (
                "exact P=EM and C=(1-omega)I+omega EM reproduce the rational "
                "map with induced l1 norms 13/6 and 19/6"
            ),
            "value": {
                "equilibrium_norm": float(equilibrium_linear_norm),
                "collision_norm": float(collision_linear_norm),
            },
        },
        "nonlinear_majorant_and_stage_structure": {
            "passed": bool(
                nonlinear_section["passed"] and structure["passed"]
            ),
            "threshold": (
                "nonlinear constants 7 and 21/2, positive density buffer, "
                "nine streaming bijections, exact convex filter, and wrapped "
                "composition reproduce"
            ),
            "value": {
                "nonlinear_majorant": nonlinear_section["passed"],
                "stage_structure": structure["passed"],
                "streaming_permutations": structure[
                    "streaming_population_permutation_count"
                ],
                "filter_sum": structure["filter_coefficient_sum"]["float"],
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": bool(
                finite_strict_json and preregistered_float_values_match
            ),
            "threshold": (
                "all exact bounds are finite strict JSON, preregistered "
                "display values match, and canonical input/result digests "
                "are emitted"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "preregistered_float_values_match": (
                    preregistered_float_values_match
                ),
                "input_digest_sha256": input_digest_sha256,
                "result_digest_sha256": result_digest_sha256,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    hypothesis_gates = {
        "equilibrium_evaluation_positive": {
            "passed": equilibrium_lower > 0,
            "threshold": "p_eq = 1/36 - e_ag > 0",
            "value": float(equilibrium_lower),
        },
        "post_collision_positive": {
            "passed": collision_lower > 0,
            "threshold": "p_coll = 1/36 - c_ag > 0",
            "value": float(collision_lower),
        },
        "post_streaming_positive": {
            "passed": bool(
                structure["all_streaming_maps_bijective"] and stream_lower > 0
            ),
            "threshold": (
                "population-wise streaming permutations preserve p_coll"
            ),
            "value": float(stream_lower),
        },
        "post_filter_positive": {
            "passed": bool(
                structure["all_filter_coefficients_nonnegative"]
                and _fraction_from_record(
                    structure["filter_coefficient_sum"]
                )
                == 1
                and filter_lower > 0
            ),
            "threshold": "the exact five-point convex filter preserves p_coll",
            "value": float(filter_lower),
        },
        "all_iterate_stagewise_positive": {
            "passed": bool(
                forward_invariance
                and equilibrium_lower > 0
                and collision_lower > 0
                and structure["passed"]
            ),
            "threshold": (
                "Q007ag forward invariance reapplies all four exact stage "
                "bounds at every one-step iterate"
            ),
            "value": {
                "forward_invariance": forward_invariance,
                "minimum_stage_lower": float(
                    min(
                        equilibrium_lower,
                        collision_lower,
                        stream_lower,
                        filter_lower,
                    )
                ),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q007ai propagated-tube stagewise audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered Q007ag propagated tube is population-positive at "
            "every exact BGK, streaming, and filter stage"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered Q007ag propagated tube did not certify exact "
            "stagewise population positivity"
        )

    return {
        "question": (
            "Is every exact equilibrium, BGK collision, streaming, and "
            "filter-stage population positive on the Q007ag propagated tube?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": _fraction_record(OMEGA),
            "eta": _fraction_record(ETA),
            "base_radius": _fraction_record(BASE_RADIUS),
            "normal_radius": _fraction_record(NORMAL_RADIUS),
        },
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "equilibrium_evaluation_population_strictly_positive": (
                hypotheses_passed
            ),
            "post_collision_population_strictly_positive": hypotheses_passed,
            "post_streaming_population_strictly_positive": hypotheses_passed,
            "post_filter_population_strictly_positive": hypotheses_passed,
            "all_iterates_exact_stagewise_population_strictly_positive": (
                hypotheses_passed
            ),
            "new_tube_binary64_stage_enclosure_certified": False,
        },
        "claim_boundary": (
            "This certifies strict population positivity for the exact "
            "mathematical equilibrium evaluation, BGK collision output, "
            "periodic streaming output, and five-point filter output on the "
            "fixed Q007ag selected tube at every iterate. It does not enclose "
            "NumPy or IEEE-754 intermediate additions, multiplications, "
            "divisions, or implementation constants; binary64 remains a "
            "separate Q007aj gate. It also does not certify entropy, "
            "monotonicity, a maximum principle, Q007v--Q007ab finite-"
            "precision induction, a continuously optimal tube, a global "
            "basin, grid uniformity, or a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007ah_full_map_positivity_acceptance_changed": False,
            "q007ag_normal_attraction_acceptance_changed": False,
            "q007u_old_tube_stagewise_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007af_external_disc_obstruction_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister Q007aj current binary64 one-step stage "
            "enclosure on this same Q007ag tube; do not extend all-iterate "
            "finite-precision induction yet."
        ),
    }


def run_q007ai_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_propagated_tube_stagewise_positivity_audit(
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
                "rational propagated-tube exact stagewise-positivity "
                "certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(OMEGA),
            "eta": float(ETA),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "stages": [
                "equilibrium evaluation",
                "BGK collision output",
                "periodic streaming output",
                "five-point filter output",
            ],
            "arithmetic_scope": (
                "exact mathematical map; no IEEE-754 intermediate roundoff "
                "enclosure"
            ),
            "claim": (
                "strict D2Q9 population positivity at every exact internal "
                "one-step stage on the fixed Q007ag selected tube only"
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
    result = run_q007ai_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
