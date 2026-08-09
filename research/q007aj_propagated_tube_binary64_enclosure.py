"""Sealed Q007aj binary64 enclosure on the Q007ag propagated tube."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007ag_tube_radius_propagation as q007ag
import research.q007ai_propagated_tube_stagewise_positivity as q007ai
import research.q007v_binary64_stage_enclosure as q007v
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
WAVE_COUNT = SIZE * SIZE
OMEGA = Fraction(3, 2)
ETA = Fraction(1, 100)
BASE_RADIUS = Fraction(9, 10**17)
NORMAL_RADIUS = Fraction(5, 10**11)
UNIT_ROUNDOFF = Fraction(1, 2**53)
SUBNORMAL_FALLBACK = Fraction(1, 2**1075)

REGISTERED_Q007AG_DIGESTS = {
    "input": "262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613",
    "candidate": ("a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408"),
    "result": "6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43",
}
REGISTERED_Q007AI_DIGESTS = {
    "input": "0dff47e8b0ed6e9b87cb73e6dea20192088495b51283c57b9d58630b7344c6a3",
    "result": "c101313957c738ccee9fd3d7f1ed36b77c6f3dad4e1130651f5be4d8757ef18a",
}
REGISTERED_INPUTS = {
    "q007ag": {
        "filename": "q007ag_tube_radius_propagation.json",
        "module": q007ag,
        "artifact_sha256": ("5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200"),
        "runner_sha256": ("bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0"),
        "diagnostic": ("analytic-radius-propagated rational finite-tube enlargement certificate"),
        "classification": (
            "Q007ae analytic radius enlarges the registered external-coordinate tube"
        ),
        "outcome": "accepted",
        "validity_count": 6,
        "hypothesis_count": 5,
    },
    "q007ai": {
        "filename": "q007ai_propagated_tube_stagewise_positivity.json",
        "module": q007ai,
        "artifact_sha256": ("3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804"),
        "runner_sha256": ("3235b2dc31445e5912f2aaf7fc080e8295035801ade9b27d3f683d34da61173d"),
        "diagnostic": ("rational propagated-tube exact stagewise-positivity certificate"),
        "classification": (
            "registered Q007ag propagated tube is population-positive at "
            "every exact BGK, streaming, and filter stage"
        ),
        "outcome": "accepted",
        "validity_count": 6,
        "hypothesis_count": 5,
    },
    "q007v": {
        "filename": "q007v_binary64_stage_enclosure.json",
        "module": q007v,
        "artifact_sha256": ("c4c1c45941a6f6ac302691efd8e795e431f6acc1fa4f4629cb0c7a0afac3c0a5"),
        "runner_sha256": ("a0d3cea0fcae8a627f4a96db56d46727589411b2557e2aa91433569576a0575c"),
        "diagnostic": ("rational binary64 stage-roundoff enclosure and tube-reentry audit"),
        "classification": (
            "binary64 one-step stages remain positive, but the registered "
            "Q007s tube is not certified roundoff-invariant"
        ),
        "outcome": "not_certified",
        "validity_count": 7,
        "hypothesis_count": 6,
    },
}

REGISTERED_D2Q9_SOURCE_SHA256 = q007v.REGISTERED_D2Q9_SOURCE_SHA256
REGISTERED_FILTER_SOURCE_SHA256 = q007v.REGISTERED_FILTER_SOURCE_SHA256
EXPECTED_OPERATION_COUNTS = q007v.EXPECTED_OPERATION_COUNTS
EXPECTED_STATE_RADIUS_FLOAT = 1.4441361143956586e-10
EXPECTED_BASE_MARGIN_FLOAT = 4.978814700017615e-20
EXPECTED_NORMAL_MARGIN_FLOAT = 9.144951058528087e-13


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


def _all_gates_pass(cycle: dict[str, Any], key: str) -> bool:
    gates = cycle.get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _scope_matches(name: str, payload: dict[str, Any]) -> bool:
    scope = payload.get("mathematical_scope", {})
    registration = REGISTERED_INPUTS[name]
    common = bool(
        scope.get("diagnostic") == registration["diagnostic"]
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega")) == float(OMEGA)
        and float(scope.get("eta")) == float(ETA)
        and scope.get("conservation_treatment") == "fixed global mass and momentum leaf"
    )
    if name == "q007ag":
        return bool(
            common
            and scope.get("manifold") == "Q007ae exact graph-gauge manifold"
            and scope.get("norm") == "Q007p Fourier external-coordinate block-sum l1"
        )
    if name == "q007ai":
        return bool(
            common
            and float(scope.get("base_modal_l1_radius")) == float(BASE_RADIUS)
            and float(scope.get("normal_coordinate_radius")) == float(NORMAL_RADIUS)
            and scope.get("arithmetic_scope")
            == "exact mathematical map; no IEEE-754 intermediate roundoff enclosure"
        )
    return bool(
        common
        and float(scope.get("base_modal_l1_radius")) == float(q007v.BASE_RADIUS)
        and float(scope.get("normal_coordinate_radius")) == float(q007v.NORMAL_RADIUS)
        and scope.get("rounding_model")
        == (
            "IEEE-754 binary64 round-to-nearest ties-to-even with u=2^-53 "
            "and absolute subnormal fallback h=2^-1075"
        )
    )


def _registered_outcome_matches(name: str, cycle: dict[str, Any]) -> bool:
    if name != "q007v":
        return bool(
            cycle.get("study_validity") == "passed"
            and cycle.get("hypothesis_outcome") == "accepted"
        )
    return bool(
        cycle.get("study_validity") == "passed"
        and cycle.get("one_step_outcome") == "accepted"
        and cycle.get("robust_reentry_outcome") == "not_certified"
        and cycle.get("hypothesis_outcome") == "not_certified"
    )


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    for name, registration in REGISTERED_INPUTS.items():
        artifact_path = directory / str(registration["filename"])
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        payloads[name] = payload
        cycle = payload.get("cycle", {})
        module = registration["module"]
        runner_path = Path(module.__file__).resolve()
        artifact_sha = _file_sha256(artifact_path)
        runner_sha = _file_sha256(runner_path)
        validity_count = len(cycle.get("validity_gates", {}))
        hypothesis_count = len(cycle.get("hypothesis_gates", {}))
        record = {
            "filename": registration["filename"],
            "registered_sha256": registration["artifact_sha256"],
            "sha256": artifact_sha,
            "sha256_matches": artifact_sha == registration["artifact_sha256"],
            "runner_filename": runner_path.name,
            "registered_runner_sha256": registration["runner_sha256"],
            "runner_sha256": runner_sha,
            "runner_sha256_matches": runner_sha == registration["runner_sha256"],
            "artifact_runner_sha256": payload.get("runner_source", {}).get("sha256"),
            "artifact_runner_sha256_matches": payload.get("runner_source", {}).get("sha256")
            == registration["runner_sha256"],
            "schema_version_matches": payload.get("schema_version") == 1,
            "source_matches": payload.get("source") == source_metadata(),
            "scope_matches": _scope_matches(name, payload),
            "study_gate_matches": payload.get("study_gate") == "passed",
            "scientific_outcome": payload.get("scientific_outcome"),
            "scientific_outcome_matches": payload.get("scientific_outcome")
            == registration["outcome"],
            "scientific_classification": cycle.get("scientific_classification"),
            "classification_matches": cycle.get("scientific_classification")
            == registration["classification"],
            "validity_gate_count": validity_count,
            "registered_validity_gate_count": registration["validity_count"],
            "all_validity_gates_pass": _all_gates_pass(cycle, "validity_gates"),
            "hypothesis_gate_count": hypothesis_count,
            "registered_hypothesis_gate_count": registration["hypothesis_count"],
            "registered_outcome_matches": _registered_outcome_matches(name, cycle),
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["runner_sha256_matches"]
            and record["artifact_runner_sha256_matches"]
            and record["schema_version_matches"]
            and record["source_matches"]
            and record["scope_matches"]
            and record["study_gate_matches"]
            and record["scientific_outcome_matches"]
            and record["classification_matches"]
            and validity_count == registration["validity_count"]
            and record["all_validity_gates_pass"]
            and hypothesis_count == registration["hypothesis_count"]
            and record["registered_outcome_matches"]
        )
        records[name] = record
    return payloads, records


def _q007ag_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    stored = payload["cycle"]
    replayed = q007ag.run_tube_radius_propagation_audit(directory)
    selected = stored["selection"]["selected_candidate"]
    margins = selected["strict_margins"]
    state_radius = _fraction_from_record(selected["state_radius"])
    base_radius = _fraction_from_record(selected["base_radius"])
    normal_radius = _fraction_from_record(selected["normal_radius"])
    base_margin = _fraction_from_record(margins["base_forward_invariance"])
    normal_margin = _fraction_from_record(margins["normal_tube_forward_invariance"])
    observed_digests = {
        "input": stored.get("input_digest_sha256"),
        "candidate": stored.get("candidate_digest_sha256"),
        "result": stored.get("result_digest_sha256"),
    }
    selected_gates = selected.get("gates", {})
    theorem = stored.get("theorem_consequence", {})
    passed = bool(
        replayed == stored
        and observed_digests == REGISTERED_Q007AG_DIGESTS
        and len(stored.get("validity_gates", {})) == 6
        and _all_gates_pass(stored, "validity_gates")
        and len(stored.get("hypothesis_gates", {})) == 5
        and _all_gates_pass(stored, "hypothesis_gates")
        and len(selected_gates) == 6
        and all(selected_gates.values())
        and selected.get("passed")
        and base_radius == BASE_RADIUS
        and normal_radius == NORMAL_RADIUS
        and state_radius > 0
        and base_margin > 0
        and normal_margin > 0
        and stored["constant_update_audit"]["only_rho_and_tau_changed"]
        and theorem.get("selected_registered_tube_forward_invariant")
        and theorem.get("selected_registered_tube_uniformly_normal_contracting")
        and theorem.get("selected_registered_tube_strictly_normally_dominating")
    )
    section = {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007AG_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007AG_DIGESTS,
        "base_modal_l1_radius": selected["base_radius"],
        "normal_coordinate_radius": selected["normal_radius"],
        "tube_state_wiener_l1_upper": selected["state_radius"],
        "selected_candidate_gates": selected_gates,
        "all_selected_candidate_gates_pass": bool(
            len(selected_gates) == 6 and all(selected_gates.values())
        ),
        "base_forward_invariance_margin": margins["base_forward_invariance"],
        "normal_tube_forward_invariance_margin": margins["normal_tube_forward_invariance"],
        "only_rho_and_tau_changed_from_q007s": stored["constant_update_audit"][
            "only_rho_and_tau_changed"
        ],
        "theorem_consequence": theorem,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "state_radius": state_radius,
        "base_margin": base_margin,
        "normal_margin": normal_margin,
        "only_rho_and_tau_changed": stored["constant_update_audit"]["only_rho_and_tau_changed"],
        "passed": passed,
    }
    return section, exact


def _q007ai_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    stored = payload["cycle"]
    replayed = q007ai.run_propagated_tube_stagewise_positivity_audit(directory)
    bounds = stored["stage_bounds"]
    observed_digests = {
        "input": stored.get("input_digest_sha256"),
        "result": stored.get("result_digest_sha256"),
    }
    state_radius = _fraction_from_record(bounds["input_state_wiener_l1_upper"])
    stage_lowers = {
        "equilibrium": _fraction_from_record(bounds["equilibrium_population_lower"]),
        "post_collision": _fraction_from_record(bounds["post_collision_population_lower"]),
        "post_streaming": _fraction_from_record(bounds["post_streaming_population_lower"]),
        "post_filter": _fraction_from_record(bounds["post_filter_population_lower"]),
    }
    theorem = stored.get("theorem_consequence", {})
    expected_true_theorems = {
        key: value
        for key, value in theorem.items()
        if key != "new_tube_binary64_stage_enclosure_certified"
    }
    passed = bool(
        replayed == stored
        and observed_digests == REGISTERED_Q007AI_DIGESTS
        and len(stored.get("validity_gates", {})) == 6
        and _all_gates_pass(stored, "validity_gates")
        and len(stored.get("hypothesis_gates", {})) == 5
        and _all_gates_pass(stored, "hypothesis_gates")
        and state_radius > 0
        and all(value > 0 for value in stage_lowers.values())
        and all(expected_true_theorems.values())
        and not theorem.get("new_tube_binary64_stage_enclosure_certified")
    )
    section = {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007AI_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007AI_DIGESTS,
        "tube_state_wiener_l1_upper": bounds["input_state_wiener_l1_upper"],
        "exact_stage_population_lowers": {
            name: _fraction_record(value) for name, value in stage_lowers.items()
        },
        "all_exact_stage_population_lowers_positive": all(
            value > 0 for value in stage_lowers.values()
        ),
        "theorem_consequence": theorem,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "state_radius": state_radius,
        "passed": passed,
    }
    return section, exact


def _q007v_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    stored = payload["cycle"]
    replayed = q007v.run_binary64_stage_enclosure_audit(directory)
    reuse = stored["sealed_bound_reuse"]
    selected_analysis = _fraction_from_record(reuse["selected_analysis_from_wiener_l1_upper"])
    external_analysis = _fraction_from_record(reuse["external_analysis_from_wiener_l1_upper"])
    hypotheses = stored.get("hypothesis_gates", {})
    old_positive_gates = {
        key: gate for key, gate in hypotheses.items() if key != "roundoff_robust_q007s_tube_reentry"
    }
    theorem = stored.get("theorem_consequence", {})
    passed = bool(
        replayed == stored
        and len(stored.get("validity_gates", {})) == 7
        and _all_gates_pass(stored, "validity_gates")
        and len(hypotheses) == 6
        and len(old_positive_gates) == 5
        and all(gate["passed"] for gate in old_positive_gates.values())
        and not hypotheses["roundoff_robust_q007s_tube_reentry"]["passed"]
        and stored.get("one_step_outcome") == "accepted"
        and stored.get("robust_reentry_outcome") == "not_certified"
        and stored.get("hypothesis_outcome") == "not_certified"
        and stored["binary64_model_audit"]["passed"]
        and stored["primitive_interval_audit"]["passed"]
        and stored["paired_stage_enclosure"]["operation_counts_match"]
        and stored["paired_stage_enclosure"]["operation_counts"] == EXPECTED_OPERATION_COUNTS
        and stored["implementation_source_audit"]["passed"]
        and stored["deterministic_implementation_replay"]["passed"]
        and selected_analysis > 0
        and external_analysis > 0
        and theorem["one_step_binary64_stagewise_population_strictly_positive"]
        and not theorem["all_iterate_roundoff_robust_q007s_tube_invariance"]
    )
    section = {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "validity_gate_count": len(stored.get("validity_gates", {})),
        "all_validity_gates_pass": _all_gates_pass(stored, "validity_gates"),
        "hypothesis_gate_count": len(hypotheses),
        "old_one_step_positive_gate_count": sum(
            gate["passed"] for gate in old_positive_gates.values()
        ),
        "old_roundoff_reentry_rejected": not hypotheses["roundoff_robust_q007s_tube_reentry"][
            "passed"
        ],
        "old_one_step_outcome": stored.get("one_step_outcome"),
        "old_robust_reentry_outcome": stored.get("robust_reentry_outcome"),
        "binary64_model_reproduced": stored["binary64_model_audit"]["passed"],
        "primitive_interval_arithmetic_reproduced": stored["primitive_interval_audit"]["passed"],
        "operation_counts": stored["paired_stage_enclosure"]["operation_counts"],
        "operation_counts_match": stored["paired_stage_enclosure"]["operation_counts_match"],
        "implementation_source_audit_reproduced": stored["implementation_source_audit"]["passed"],
        "deterministic_replay_reproduced": stored["deterministic_implementation_replay"]["passed"],
        "selected_analysis_from_wiener_l1_upper": reuse["selected_analysis_from_wiener_l1_upper"],
        "external_analysis_from_wiener_l1_upper": reuse["external_analysis_from_wiener_l1_upper"],
        "theorem_consequence": theorem,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "selected_analysis": selected_analysis,
        "external_analysis": external_analysis,
        "passed": passed,
    }
    return section, exact


def _implementation_source_audit(
    q007ai_payload: dict[str, Any],
) -> dict[str, Any]:
    audit = q007v._implementation_source_audit(q007ai_payload)
    audit["q007ai_stage_order_match"] = audit.pop("q007u_stage_order_match")
    return audit


def run_propagated_tube_binary64_enclosure_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory() if artifact_directory is None else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    q007ag_section, q007ag_exact = _q007ag_reproduction(directory, payloads["q007ag"])
    q007ai_section, q007ai_exact = _q007ai_reproduction(directory, payloads["q007ai"])
    q007v_section, q007v_exact = _q007v_reproduction(directory, payloads["q007v"])

    state_radius = q007ai_exact["state_radius"]
    q007ag_state_radius = q007ag_exact["state_radius"]
    selected_analysis = q007v_exact["selected_analysis"]
    external_analysis = q007v_exact["external_analysis"]
    base_margin = q007ag_exact["base_margin"]
    normal_margin = q007ag_exact["normal_margin"]
    assert isinstance(state_radius, Fraction)
    assert isinstance(q007ag_state_radius, Fraction)
    assert isinstance(selected_analysis, Fraction)
    assert isinstance(external_analysis, Fraction)
    assert isinstance(base_margin, Fraction)
    assert isinstance(normal_margin, Fraction)

    paired_section, paired_exact = q007v._paired_stage_enclosure(state_radius)
    binary64_section = q007v._binary64_model_audit()
    primitive_section = q007v._primitive_interval_audit()
    source_section = _implementation_source_audit(payloads["q007ai"])
    replay_section = q007v._deterministic_implementation_replay(paired_section)
    reentry_section, reentry_exact = q007v._roundoff_reentry_audit(
        paired_exact["filtered"],
        {
            "selected_analysis": selected_analysis,
            "external_analysis": external_analysis,
            "base_margin": base_margin,
            "normal_margin": normal_margin,
        },
    )

    state_identity = state_radius == q007ag_state_radius
    preregistered_values_match = bool(
        float(state_radius) == EXPECTED_STATE_RADIUS_FLOAT
        and float(base_margin) == EXPECTED_BASE_MARGIN_FLOAT
        and float(normal_margin) == EXPECTED_NORMAL_MARGIN_FLOAT
    )
    cross_input_section = {
        "q007ag_state_wiener_l1_upper": _fraction_record(q007ag_state_radius),
        "q007ai_state_wiener_l1_upper": _fraction_record(state_radius),
        "state_radii_match_exactly": state_identity,
        "base_modal_l1_radius": _fraction_record(BASE_RADIUS),
        "normal_coordinate_radius": _fraction_record(NORMAL_RADIUS),
        "selected_analysis_from_wiener_l1_upper": _fraction_record(selected_analysis),
        "external_analysis_from_wiener_l1_upper": _fraction_record(external_analysis),
        "base_forward_invariance_margin": _fraction_record(base_margin),
        "normal_tube_forward_invariance_margin": _fraction_record(normal_margin),
        "only_rho_and_tau_changed_from_q007s": q007ag_exact["only_rho_and_tau_changed"],
        "preregistered_float_values": {
            "state_radius": EXPECTED_STATE_RADIUS_FLOAT,
            "base_margin": EXPECTED_BASE_MARGIN_FLOAT,
            "normal_margin": EXPECTED_NORMAL_MARGIN_FLOAT,
        },
        "preregistered_float_values_match": preregistered_values_match,
        "passed": bool(
            state_identity
            and selected_analysis > 0
            and external_analysis > 0
            and base_margin > 0
            and normal_margin > 0
            and q007ag_exact["only_rho_and_tau_changed"]
            and preregistered_values_match
        ),
    }

    maximum_finite = _fraction_from_record(binary64_section["maximum_finite"])
    minimum_divisor = paired_exact["minimum_divisor"]
    maximum_intermediate = paired_exact["maximum_intermediate_magnitude"]
    assert isinstance(minimum_divisor, Fraction)
    assert isinstance(maximum_intermediate, Fraction)
    arithmetic_passed = bool(
        q007v_section["passed"]
        and binary64_section["passed"]
        and primitive_section["passed"]
        and paired_exact["operation_counts_match"]
        and minimum_divisor > 0
        and maximum_intermediate < maximum_finite
    )

    registered_parameters = {
        "size": SIZE,
        "wave_count": WAVE_COUNT,
        "omega": _fraction_record(OMEGA),
        "eta": _fraction_record(ETA),
        "base_radius": _fraction_record(BASE_RADIUS),
        "normal_radius": _fraction_record(NORMAL_RADIUS),
        "unit_roundoff": _fraction_record(UNIT_ROUNDOFF),
        "subnormal_fallback": _fraction_record(SUBNORMAL_FALLBACK),
        "operation_counts": EXPECTED_OPERATION_COUNTS,
    }
    input_digest_sha256 = _canonical_json_sha256(
        {
            "registered_parameters": registered_parameters,
            "input_artifacts": input_records,
            "registered_q007ag_digests": REGISTERED_Q007AG_DIGESTS,
            "registered_q007ai_digests": REGISTERED_Q007AI_DIGESTS,
            "implementation_source_audit": source_section,
        }
    )
    result_digest_sha256 = _canonical_json_sha256(
        {
            "q007ag_exact_reproduction": q007ag_section,
            "q007ai_exact_reproduction": q007ai_section,
            "q007v_oracle_reproduction": q007v_section,
            "cross_input_consistency": cross_input_section,
            "paired_stage_enclosure": paired_section,
            "roundoff_reentry_audit": reentry_section,
        }
    )
    serializable_sections = {
        "input_artifacts": input_records,
        "q007ag_exact_reproduction": q007ag_section,
        "q007ai_exact_reproduction": q007ai_section,
        "q007v_oracle_reproduction": q007v_section,
        "cross_input_consistency": cross_input_section,
        "binary64_model_audit": binary64_section,
        "primitive_interval_audit": primitive_section,
        "implementation_source_audit": source_section,
        "paired_stage_enclosure": paired_section,
        "deterministic_implementation_replay": replay_section,
        "roundoff_reentry_audit": reentry_section,
        "input_digest_sha256": input_digest_sha256,
        "result_digest_sha256": result_digest_sha256,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "sealed_inputs_source_scope_and_outcomes": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": (
                "Q007ag/Q007ai/Q007v artifact and runner SHA, source, scope, "
                "schema, classifications, validity, and split outcomes match"
            ),
            "value": {
                "passing_input_count": sum(record["passed"] for record in input_records.values()),
                "expected_input_count": len(input_records),
            },
        },
        "q007ag_selected_tube_exactly_reproduced": {
            "passed": q007ag_section["passed"],
            "threshold": (
                "stored cycle, three digests, selected radii, six gates, "
                "strict margins, and forward-invariance theorem reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007ag_section[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007ag_section["digests_match"],
                "all_selected_candidate_gates_pass": q007ag_section[
                    "all_selected_candidate_gates_pass"
                ],
            },
        },
        "q007ai_exact_stage_oracle_reproduced": {
            "passed": q007ai_section["passed"],
            "threshold": (
                "stored cycle, two digests, exact new-tube stage bounds, all "
                "accepted gates, and all-iterate exact theorem reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007ai_section[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007ai_section["digests_match"],
                "all_exact_stage_population_lowers_positive": q007ai_section[
                    "all_exact_stage_population_lowers_positive"
                ],
            },
        },
        "q007v_oracle_and_binary64_engine_reproduced": {
            "passed": arithmetic_passed,
            "threshold": (
                "old split outcome, binary64 model, Fraction primitives, "
                "registered operation counts, positive divisors, and finite "
                "intermediates reproduce"
            ),
            "value": {
                "old_oracle_reproduced": q007v_section["passed"],
                "binary64_model": binary64_section["passed"],
                "primitive_intervals": primitive_section["passed"],
                "operation_counts_match": paired_exact["operation_counts_match"],
                "minimum_divisor": float(minimum_divisor),
                "maximum_intermediate": float(maximum_intermediate),
            },
        },
        "current_sources_and_new_tube_replay": {
            "passed": bool(source_section["passed"] and replay_section["passed"]),
            "threshold": (
                "registered D2Q9/filter source operations and stage order "
                "match, and the float64 rest replay lies in every new bound"
            ),
            "value": {
                "source_schedule": source_section["passed"],
                "new_tube_replay": replay_section["passed"],
            },
        },
        "cross_input_exact_consistency": {
            "passed": cross_input_section["passed"],
            "threshold": (
                "Q007ag/Q007ai state radii agree exactly, Q007v analysis "
                "bounds and Q007ag margins are positive, and only rho/tau "
                "changed from Q007s"
            ),
            "value": {
                "state_radii_match_exactly": state_identity,
                "preregistered_float_values_match": (preregistered_values_match),
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": finite_strict_json,
            "threshold": (
                "all bounds are finite strict JSON and canonical input/result digests are emitted"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest_sha256,
                "result_digest_sha256": result_digest_sha256,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    stages = paired_section["stages"]
    stage_lowers = {
        name: _fraction_from_record(stage["binary64_population_lower"])
        for name, stage in stages.items()
    }
    equilibrium_positive = stage_lowers["equilibrium"] > 0
    collision_positive = stage_lowers["post_collision"] > 0
    streaming_positive = bool(
        source_section["streaming_is_population_permutation_without_arithmetic"]
        and stages["post_streaming"] == stages["post_collision"]
        and stage_lowers["post_streaming"] > 0
    )
    filter_positive = stage_lowers["post_filter"] > 0
    one_step_positive = bool(
        equilibrium_positive and collision_positive and streaming_positive and filter_positive
    )
    base_reentry = bool(reentry_exact["base_pass"])
    normal_reentry = bool(reentry_exact["normal_pass"])
    robust_reentry = bool(base_reentry and normal_reentry)
    hypothesis_gates = {
        "binary64_equilibrium_positive": {
            "passed": equilibrium_positive,
            "threshold": "new-tube binary64 equilibrium lower > 0",
            "value": float(stage_lowers["equilibrium"]),
        },
        "binary64_post_collision_positive": {
            "passed": collision_positive,
            "threshold": "new-tube binary64 post-collision lower > 0",
            "value": float(stage_lowers["post_collision"]),
        },
        "streaming_preserves_binary64_lower": {
            "passed": streaming_positive,
            "threshold": (
                "population-wise np.roll performs no arithmetic and preserves "
                "the post-collision lower"
            ),
            "value": float(stage_lowers["post_streaming"]),
        },
        "binary64_post_filter_positive": {
            "passed": filter_positive,
            "threshold": "new-tube binary64 post-filter lower > 0",
            "value": float(stage_lowers["post_filter"]),
        },
        "one_step_binary64_stage_positivity": {
            "passed": one_step_positive,
            "threshold": "all four registered new-tube stage lowers are positive",
            "value": {name: float(value) for name, value in stage_lowers.items()},
        },
        "base_coordinate_roundoff_reentry": {
            "passed": base_reentry,
            "threshold": "epsilon_B is strictly below the Q007ag base margin",
            "value": {
                "coordinate_error_upper": reentry_section["base_coordinate_error_upper"]["float"],
                "strict_margin": reentry_section["base_forward_invariance_margin"]["float"],
                "margin_utilization": reentry_section["base_margin_utilization"]["float"],
            },
        },
        "normal_coordinate_roundoff_reentry": {
            "passed": normal_reentry,
            "threshold": "epsilon_N is strictly below the Q007ag normal margin",
            "value": {
                "coordinate_error_upper": reentry_section["normal_coordinate_error_upper"]["float"],
                "strict_margin": reentry_section["normal_tube_forward_invariance_margin"]["float"],
                "margin_utilization": reentry_section["normal_margin_utilization"]["float"],
            },
        },
    }
    all_hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    one_step_certified = validity_passed and one_step_positive
    robust_reentry_certified = validity_passed and robust_reentry
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007aj propagated-tube binary64 enclosure audit invalid"
    elif all_hypotheses_passed:
        outcome = "accepted"
        classification = (
            "binary64 stage positivity and roundoff-robust Q007ag tube invariance certified"
        )
    elif one_step_certified:
        outcome = "not_certified"
        classification = (
            "binary64 one-step stages remain positive, but the registered "
            "Q007ag tube is not certified roundoff-invariant"
        )
    else:
        outcome = "not_certified"
        classification = (
            "binary64 stage positivity is not certified on the registered Q007ag input tube"
        )

    return {
        "question": (
            "Does the registered Fraction-based binary64 enclosure preserve "
            "every one-step stage lower and fit inside the Q007ag base and "
            "normal re-entry margins?"
        ),
        "registered_parameters": registered_parameters,
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "one_step_outcome": ("accepted" if one_step_certified else "not_certified"),
        "base_reentry_outcome": (
            "accepted" if validity_passed and base_reentry else "not_certified"
        ),
        "normal_reentry_outcome": (
            "accepted" if validity_passed and normal_reentry else "not_certified"
        ),
        "robust_reentry_outcome": ("accepted" if robust_reentry_certified else "not_certified"),
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "binary64_equilibrium_population_strictly_positive": (
                one_step_certified and equilibrium_positive
            ),
            "binary64_post_collision_population_strictly_positive": (
                one_step_certified and collision_positive
            ),
            "binary64_post_streaming_population_strictly_positive": (
                one_step_certified and streaming_positive
            ),
            "binary64_post_filter_population_strictly_positive": (
                one_step_certified and filter_positive
            ),
            "one_step_binary64_stagewise_population_strictly_positive": (one_step_certified),
            "roundoff_robust_base_coordinate_reentry": bool(validity_passed and base_reentry),
            "roundoff_robust_normal_coordinate_reentry": bool(validity_passed and normal_reentry),
            "all_iterate_roundoff_robust_q007ag_tube_invariance": (all_hypotheses_passed),
            "all_iterate_binary64_stagewise_population_strictly_positive": (all_hypotheses_passed),
        },
        "claim_boundary": (
            "A passed one-step result applies only to correctly rounded "
            "binary64 encodings of exact real states in the fixed Q007ag "
            "component box, under the registered NumPy source and round-to-"
            "nearest operation order. The box conservatively ignores the "
            "fixed-leaf constraints. If either re-entry decision is not "
            "certified, the one-step conclusion is not iterated. Re-entry "
            "failure is neither a counterexample nor an observed tube escape; "
            "it only says this fixed worst-case enclosure exceeds a strict "
            "margin. This excludes nonstandard rounding, FTZ/DAZ, GPU kernels, "
            "BLAS changes, compiler fast-math, entropy, monotonicity, a maximum "
            "principle, a continuous optimum, a global basin, grid uniformity, "
            "and a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007ag_tube_acceptance_changed": False,
            "q007ai_exact_stagewise_acceptance_changed": False,
            "q007v_old_tube_mixed_result_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007af_external_disc_obstruction_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If either re-entry gate fails, preregister Q007ak to decompose "
            "the obstruction into strict margins, analysis norms, Wiener "
            "lifting, and local roundoff accumulation; do not iterate this "
            "one-step certificate or begin MPFR/repair/shadowing extensions."
        ),
    }


def run_q007aj_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_propagated_tube_binary64_enclosure_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "rational propagated-tube binary64 stage-roundoff enclosure and tube-reentry audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(OMEGA),
            "eta": float(ETA),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "input_encoding": (
                "correctly rounded binary64 encoding of an exact real Q007ag tube state"
            ),
            "rounding_model": (
                "IEEE-754 binary64 round-to-nearest ties-to-even with u=2^-53 "
                "and absolute subnormal fallback h=2^-1075"
            ),
            "claim": (
                "separate one-step internal-stage positivity, base re-entry, "
                "and normal re-entry decisions for the registered current "
                "implementation only"
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
    result = run_q007aj_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
