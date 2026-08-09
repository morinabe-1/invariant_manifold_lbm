"""Sealed Q007ak factor audit for Q007ag roundoff re-entry failure."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007aj_propagated_tube_binary64_enclosure as q007aj
import research.q007w_ideal_precision_threshold as q007w
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

MINIMUM_PRECISION = 53
MAXIMUM_PRECISION = 128
REGISTERED_PRECISIONS = tuple(range(MINIMUM_PRECISION, MAXIMUM_PRECISION + 1))
EXPECTED_CANDIDATE_COUNT = 76
MINIMUM_NORMAL_EXPONENT = -1022

REGISTERED_Q007AJ_DIGESTS = {
    "input": "040bf7e2c62094ea66a4cf8a6190ea78e53745e30c70a3b3ce856a7e4d1c5284",
    "result": "517846a3a99f1e684f40c2ea6d5a8ae7b3db8c0849dae3097fc7f380f4eca923",
}
REGISTERED_Q007W_CANDIDATE_DIGEST = (
    "440a08dc36990d3e34edf1886fd7e47eacb4766c4a42352022897fd79dbb3ce2"
)
REGISTERED_INPUTS = {
    "q007aj": {
        "filename": "q007aj_propagated_tube_binary64_enclosure.json",
        "module": q007aj,
        "artifact_sha256": ("29b8cd320f40396cc24ae30b46e46eecc7e23564600284aeb916a90af3a1fd8e"),
        "runner_sha256": ("e91cd0740ca9d639f6eaeeea8ed71552a0323897f45eee50070f4c8cdf947ac5"),
        "diagnostic": (
            "rational propagated-tube binary64 stage-roundoff enclosure and tube-reentry audit"
        ),
        "classification": (
            "binary64 one-step stages remain positive, but the registered "
            "Q007ag tube is not certified roundoff-invariant"
        ),
        "outcome": "not_certified",
        "validity_count": 7,
        "hypothesis_count": 7,
    },
    "q007w": {
        "filename": "q007w_ideal_precision_threshold.json",
        "module": q007w,
        "artifact_sha256": ("bac362d9dca4a681387b986a5f5802278ef61a1a3bcf1a0f8577c7f3ab0a07af"),
        "runner_sha256": ("86dcc0a507e24216775650d5467d0ebf6e90eac0865190d0d5186e08afb7eac8"),
        "diagnostic": "rational ideal-binary precision-threshold certificate",
        "classification": (
            "registered ideal binary precision threshold restores "
            "roundoff-robust Q007s tube re-entry"
        ),
        "outcome": "accepted",
        "validity_count": 7,
        "hypothesis_count": 6,
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


def _all_gates_pass(cycle: dict[str, Any], key: str) -> bool:
    gates = cycle.get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _scope_matches(name: str, payload: dict[str, Any]) -> bool:
    scope = payload.get("mathematical_scope", {})
    if name == "q007aj":
        return bool(
            scope.get("diagnostic") == REGISTERED_INPUTS[name]["diagnostic"]
            and scope.get("construction_grid") == [17, 17]
            and float(scope.get("omega")) == 1.5
            and float(scope.get("eta")) == 0.01
            and scope.get("conservation_treatment") == "fixed global mass and momentum leaf"
            and scope.get("manifold") == "Q007ae exact graph-gauge manifold"
            and scope.get("norm") == "Q007p Fourier external-coordinate block-sum l1"
            and float(scope.get("base_modal_l1_radius")) == float(q007aj.BASE_RADIUS)
            and float(scope.get("normal_coordinate_radius")) == float(q007aj.NORMAL_RADIUS)
        )
    return bool(
        scope.get("diagnostic") == REGISTERED_INPUTS[name]["diagnostic"]
        and scope.get("construction_grid") == [17, 17]
        and float(scope.get("omega")) == 1.5
        and float(scope.get("eta")) == 0.01
        and scope.get("precision_candidates") == "all integer significand bits 53 through 128"
        and scope.get("rounding_model") == "ideal binary round-to-nearest ties-to-even"
    )


def _registered_outcome_matches(name: str, cycle: dict[str, Any]) -> bool:
    if name == "q007w":
        return bool(
            cycle.get("study_validity") == "passed"
            and cycle.get("hypothesis_outcome") == "accepted"
        )
    hypotheses = cycle.get("hypothesis_gates", {})
    failed = [key for key, gate in hypotheses.items() if not gate["passed"]]
    return bool(
        cycle.get("study_validity") == "passed"
        and cycle.get("one_step_outcome") == "accepted"
        and cycle.get("base_reentry_outcome") == "not_certified"
        and cycle.get("normal_reentry_outcome") == "not_certified"
        and cycle.get("robust_reentry_outcome") == "not_certified"
        and cycle.get("hypothesis_outcome") == "not_certified"
        and failed
        == [
            "base_coordinate_roundoff_reentry",
            "normal_coordinate_roundoff_reentry",
        ]
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
        artifact_runner_sha = payload.get("runner_source", {}).get("sha256")
        record = {
            "filename": registration["filename"],
            "registered_sha256": registration["artifact_sha256"],
            "sha256": artifact_sha,
            "sha256_matches": artifact_sha == registration["artifact_sha256"],
            "runner_filename": runner_path.name,
            "registered_runner_sha256": registration["runner_sha256"],
            "runner_sha256": runner_sha,
            "runner_sha256_matches": runner_sha == registration["runner_sha256"],
            "artifact_runner_sha256": artifact_runner_sha,
            "artifact_runner_sha256_matches": artifact_runner_sha == registration["runner_sha256"],
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
            "validity_gate_count": len(cycle.get("validity_gates", {})),
            "registered_validity_gate_count": registration["validity_count"],
            "all_validity_gates_pass": _all_gates_pass(cycle, "validity_gates"),
            "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
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
            and record["validity_gate_count"] == registration["validity_count"]
            and record["all_validity_gates_pass"]
            and record["hypothesis_gate_count"] == registration["hypothesis_count"]
            and record["registered_outcome_matches"]
        )
        records[name] = record
    return payloads, records


def _q007aj_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | int | bool]]:
    stored = payload["cycle"]
    replayed = q007aj.run_propagated_tube_binary64_enclosure_audit(directory)
    observed_digests = {
        "input": stored.get("input_digest_sha256"),
        "result": stored.get("result_digest_sha256"),
    }
    hypotheses = stored["hypothesis_gates"]
    failed_hypotheses = [name for name, gate in hypotheses.items() if not gate["passed"]]
    cross = stored["cross_input_consistency"]
    reentry = stored["roundoff_reentry_audit"]
    state_radius = _fraction_from_record(cross["q007ai_state_wiener_l1_upper"])
    selected_analysis = _fraction_from_record(cross["selected_analysis_from_wiener_l1_upper"])
    external_analysis = _fraction_from_record(cross["external_analysis_from_wiener_l1_upper"])
    base_margin = _fraction_from_record(cross["base_forward_invariance_margin"])
    normal_margin = _fraction_from_record(cross["normal_tube_forward_invariance_margin"])
    component_error = _fraction_from_record(reentry["component_forward_error_sum_upper"])
    wave_count = int(reentry["normalized_dft_wave_count"])
    base_utilization = _fraction_from_record(reentry["base_margin_utilization"])
    normal_utilization = _fraction_from_record(reentry["normal_margin_utilization"])
    stage_lowers = {
        name: _fraction_from_record(stage["binary64_population_lower"])
        for name, stage in stored["paired_stage_enclosure"]["stages"].items()
    }
    sources = stored["implementation_source_audit"]
    passed = bool(
        replayed == stored
        and observed_digests == REGISTERED_Q007AJ_DIGESTS
        and len(stored["validity_gates"]) == 7
        and _all_gates_pass(stored, "validity_gates")
        and len(hypotheses) == 7
        and failed_hypotheses
        == [
            "base_coordinate_roundoff_reentry",
            "normal_coordinate_roundoff_reentry",
        ]
        and stored["one_step_outcome"] == "accepted"
        and stored["base_reentry_outcome"] == "not_certified"
        and stored["normal_reentry_outcome"] == "not_certified"
        and all(value > 0 for value in stage_lowers.values())
        and state_radius > 0
        and selected_analysis > 0
        and external_analysis > 0
        and base_margin > 0
        and normal_margin > 0
        and component_error > 0
        and wave_count == q007aj.WAVE_COUNT == 289
        and base_utilization > 1
        and normal_utilization > 1
        and sources["d2q9_source"]["sha256"] == q007aj.REGISTERED_D2Q9_SOURCE_SHA256
        and sources["filter_source"]["sha256"] == q007aj.REGISTERED_FILTER_SOURCE_SHA256
    )
    section = {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007AJ_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007AJ_DIGESTS,
        "validity_gate_count": len(stored["validity_gates"]),
        "all_validity_gates_pass": _all_gates_pass(stored, "validity_gates"),
        "hypothesis_gate_count": len(hypotheses),
        "failed_hypothesis_names": failed_hypotheses,
        "one_step_outcome": stored["one_step_outcome"],
        "base_reentry_outcome": stored["base_reentry_outcome"],
        "normal_reentry_outcome": stored["normal_reentry_outcome"],
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "post_filter_component_error_sum": _fraction_record(component_error),
        "normalized_dft_wave_count": wave_count,
        "selected_analysis_upper": _fraction_record(selected_analysis),
        "external_analysis_upper": _fraction_record(external_analysis),
        "base_forward_invariance_margin": _fraction_record(base_margin),
        "normal_tube_forward_invariance_margin": _fraction_record(normal_margin),
        "base_margin_utilization": _fraction_record(base_utilization),
        "normal_margin_utilization": _fraction_record(normal_utilization),
        "binary64_stage_population_lowers": {
            name: _fraction_record(value) for name, value in stage_lowers.items()
        },
        "implementation_sources_match": bool(
            sources["d2q9_source"]["sha256"] == q007aj.REGISTERED_D2Q9_SOURCE_SHA256
            and sources["filter_source"]["sha256"] == q007aj.REGISTERED_FILTER_SOURCE_SHA256
        ),
        "passed": passed,
    }
    exact: dict[str, Fraction | int | bool] = {
        "state_radius": state_radius,
        "selected_analysis": selected_analysis,
        "external_analysis": external_analysis,
        "base_margin": base_margin,
        "normal_margin": normal_margin,
        "component_error": component_error,
        "wave_count": wave_count,
        "base_utilization": base_utilization,
        "normal_utilization": normal_utilization,
        "passed": passed,
    }
    return section, exact


def _q007w_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    stored = payload["cycle"]
    replayed = q007w.run_ideal_precision_threshold_audit(directory)
    selection = stored["selection"]
    campaign = stored["precision_campaign"]
    passed = bool(
        replayed == stored
        and len(stored["validity_gates"]) == 7
        and _all_gates_pass(stored, "validity_gates")
        and len(stored["hypothesis_gates"]) == 6
        and _all_gates_pass(stored, "hypothesis_gates")
        and selection["selected_precision_bits"] == 85
        and selection["previous_precision_candidate"]["precision_bits"] == 84
        and not selection["previous_precision_candidate"]["passed"]
        and selection["selected_candidate"]["passed"]
        and campaign["candidate_count"] == EXPECTED_CANDIDATE_COUNT
        and campaign["candidate_digest_sha256"] == REGISTERED_Q007W_CANDIDATE_DIGEST
        and campaign["coverage_match"]
        and campaign["all_monotonicity_checks_pass"]
        and campaign["all_candidate_domains_pass"]
        and stored["ties_to_even_audit"]["passed"]
        and stored["p53_control_audit"]["passed"]
    )
    return {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "validity_gate_count": len(stored["validity_gates"]),
        "all_validity_gates_pass": _all_gates_pass(stored, "validity_gates"),
        "hypothesis_gate_count": len(stored["hypothesis_gates"]),
        "all_hypothesis_gates_pass": _all_gates_pass(stored, "hypothesis_gates"),
        "old_selected_precision_bits": selection["selected_precision_bits"],
        "old_previous_precision_bits": selection["previous_precision_candidate"]["precision_bits"],
        "candidate_count": campaign["candidate_count"],
        "candidate_digest_sha256": campaign["candidate_digest_sha256"],
        "registered_candidate_digest_sha256": (REGISTERED_Q007W_CANDIDATE_DIGEST),
        "candidate_digest_matches": campaign["candidate_digest_sha256"]
        == REGISTERED_Q007W_CANDIDATE_DIGEST,
        "coverage_match": campaign["coverage_match"],
        "all_monotonicity_checks_pass": campaign["all_monotonicity_checks_pass"],
        "all_candidate_domains_pass": campaign["all_candidate_domains_pass"],
        "ties_to_even_control_passed": stored["ties_to_even_audit"]["passed"],
        "p53_q007v_control_passed": stored["p53_control_audit"]["passed"],
        "passed": passed,
    }


def _p53_q007aj_control(
    q007aj_payload: dict[str, Any],
    summary: dict[str, Any],
    exact: dict[str, Any],
) -> dict[str, Any]:
    cycle = q007aj_payload["cycle"]
    stored_stages = cycle["paired_stage_enclosure"]["stages"]
    stored_reentry = cycle["roundoff_reentry_audit"]
    stored_model = cycle["binary64_model_audit"]
    stage_pairs = {
        "equilibrium": exact["equilibria"],
        "post_collision": exact["collisions"],
        "post_streaming": exact["streamed"],
        "post_filter": exact["filtered"],
    }
    population_records_match = all(
        q007aj.q007v._quantity_record(quantity)
        == {key: value for key, value in stored.items() if key != "population"}
        for name, quantities in stage_pairs.items()
        for quantity, stored in zip(
            quantities,
            stored_stages[name]["population_records"],
            strict=True,
        )
    )
    stage_summaries_match = all(
        summary["stage_bounds"][name]["population_lower"]
        == stored_stages[name]["binary64_population_lower"]
        and summary["stage_bounds"][name]["population_upper"]
        == stored_stages[name]["binary64_population_upper"]
        and summary["stage_bounds"][name]["maximum_component_error"]
        == stored_stages[name]["maximum_component_forward_error_upper"]
        for name in stage_pairs
    )
    weight_constants_match = all(
        exact["weight_actuals"][index] == _fraction_from_record(record["binary64_dyadic"])
        for index, record in enumerate(stored_model["weight_constants"])
    )
    scalars = {record["name"]: record for record in stored_model["scalar_constants"]}
    filter_constants_match = bool(
        exact["eta_actual"] == _fraction_from_record(scalars["eta"]["binary64_dyadic"])
        and exact["center_actual"]
        == _fraction_from_record(scalars["filter_center"]["binary64_dyadic"])
        and exact["neighbour_actual"]
        == _fraction_from_record(scalars["filter_neighbour"]["binary64_dyadic"])
    )
    reentry_match = bool(
        summary["post_filter_component_error_sum"]
        == stored_reentry["component_forward_error_sum_upper"]
        and summary["wiener_error_upper"] == stored_reentry["wiener_error_upper"]
        and summary["base_coordinate_error_upper"] == stored_reentry["base_coordinate_error_upper"]
        and summary["normal_coordinate_error_upper"]
        == stored_reentry["normal_coordinate_error_upper"]
        and summary["base_margin_utilization"] == stored_reentry["base_margin_utilization"]
        and summary["normal_margin_utilization"] == stored_reentry["normal_margin_utilization"]
        and summary["one_step_stage_positivity_passed"]
        and not summary["base_reentry_passed"]
        and not summary["normal_reentry_passed"]
    )
    passed = bool(
        population_records_match
        and stage_summaries_match
        and weight_constants_match
        and filter_constants_match
        and reentry_match
        and summary["operation_counts"] == q007aj.EXPECTED_OPERATION_COUNTS
        and summary["operation_counts_match"]
    )
    return {
        "precision_bits": 53,
        "all_population_target_and_error_records_match": (population_records_match),
        "all_stage_summaries_match": stage_summaries_match,
        "weight_dyadics_match": weight_constants_match,
        "filter_scalar_dyadics_match": filter_constants_match,
        "all_reentry_quantities_match": reentry_match,
        "operation_counts": summary["operation_counts"],
        "operation_counts_match": summary["operation_counts_match"],
        "split_outcome_reproduced": bool(
            summary["one_step_stage_positivity_passed"]
            and not summary["base_reentry_passed"]
            and not summary["normal_reentry_passed"]
        ),
        "passed": passed,
    }


def _coordinate_factor_record(
    name: str,
    analysis: Fraction,
    wave_count: int,
    component_error: Fraction,
    margin: Fraction,
    stored_utilization: Fraction,
) -> dict[str, Any]:
    wave = Fraction(wave_count)
    coordinate_error = analysis * wave * component_error
    utilization = coordinate_error / margin
    maximum_component_error = margin / (analysis * wave)
    maximum_analysis = margin / (wave * component_error)
    maximum_wave_factor = margin / (analysis * component_error)
    minimum_margin = coordinate_error
    unit_wave_error = analysis * component_error
    unit_wave_utilization = unit_wave_error / margin
    unit_analysis_error = wave * component_error
    unit_analysis_utilization = unit_analysis_error / margin
    identities = {
        "stored_utilization": utilization == stored_utilization,
        "component_error_threshold": (maximum_component_error * analysis * wave == margin),
        "analysis_threshold": (maximum_analysis * wave * component_error == margin),
        "wave_threshold": (maximum_wave_factor * analysis * component_error == margin),
        "margin_threshold": minimum_margin == coordinate_error,
        "single_factor_improvement_component": (
            component_error / maximum_component_error == utilization
        ),
        "single_factor_improvement_analysis": (analysis / maximum_analysis == utilization),
        "single_factor_improvement_wave": (wave / maximum_wave_factor == utilization),
        "single_factor_improvement_margin": (minimum_margin / margin == utilization),
    }
    passed = bool(
        all(
            value > 0
            for value in (
                analysis,
                component_error,
                margin,
                coordinate_error,
                utilization,
                maximum_component_error,
                maximum_analysis,
                maximum_wave_factor,
                minimum_margin,
            )
        )
        and all(identities.values())
    )
    return {
        "coordinate": name,
        "analysis_upper": _fraction_record(analysis),
        "wave_lifting_factor": wave_count,
        "local_component_error_sum": _fraction_record(component_error),
        "strict_margin": _fraction_record(margin),
        "coordinate_error_upper": _fraction_record(coordinate_error),
        "margin_utilization": _fraction_record(utilization),
        "stored_margin_utilization": _fraction_record(stored_utilization),
        "maximum_local_component_error_at_boundary": _fraction_record(maximum_component_error),
        "maximum_analysis_factor_at_boundary": _fraction_record(maximum_analysis),
        "maximum_wave_factor_at_boundary": _fraction_record(maximum_wave_factor),
        "minimum_margin_at_boundary": _fraction_record(minimum_margin),
        "strict_single_factor_improvement_required": _fraction_record(utilization),
        "unit_wave_counterfactual": {
            "coordinate_error_upper": _fraction_record(unit_wave_error),
            "margin_utilization": _fraction_record(unit_wave_utilization),
            "strict_reentry_passed": unit_wave_utilization < 1,
        },
        "unit_analysis_counterfactual": {
            "coordinate_error_upper": _fraction_record(unit_analysis_error),
            "margin_utilization": _fraction_record(unit_analysis_utilization),
            "strict_reentry_passed": unit_analysis_utilization < 1,
        },
        "exact_identity_checks": identities,
        "all_exact_identity_checks_pass": all(identities.values()),
        "passed": passed,
    }


def _selection_for_gate(
    candidates: list[dict[str, Any]],
    key: str,
) -> dict[str, Any]:
    passing = [candidate for candidate in candidates if candidate[key]]
    selected = passing[0] if passing else None
    selected_precision = int(selected["precision_bits"]) if selected is not None else None
    previous = (
        candidates[selected_precision - MINIMUM_PRECISION - 1]
        if selected_precision is not None and selected_precision > MINIMUM_PRECISION
        else None
    )
    boundary = bool(
        selected is not None and previous is not None and selected[key] and not previous[key]
    )
    first_pass = bool(
        selected is None
        or selected_precision == min(int(candidate["precision_bits"]) for candidate in passing)
    )
    return {
        "gate": key,
        "passing_candidate_count": len(passing),
        "selected_precision_bits": selected_precision,
        "selected_candidate": selected,
        "previous_precision_candidate": previous,
        "first_pass_matches_selection": first_pass,
        "selection_boundary_reproduced": boundary,
    }


def run_reentry_factor_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory() if artifact_directory is None else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    q007aj_section, fixed = _q007aj_reproduction(directory, payloads["q007aj"])
    q007w_section = _q007w_reproduction(directory, payloads["q007w"])

    state_radius = fixed["state_radius"]
    selected_analysis = fixed["selected_analysis"]
    external_analysis = fixed["external_analysis"]
    base_margin = fixed["base_margin"]
    normal_margin = fixed["normal_margin"]
    component_error = fixed["component_error"]
    wave_count = fixed["wave_count"]
    base_stored_utilization = fixed["base_utilization"]
    normal_stored_utilization = fixed["normal_utilization"]
    assert isinstance(state_radius, Fraction)
    assert isinstance(selected_analysis, Fraction)
    assert isinstance(external_analysis, Fraction)
    assert isinstance(base_margin, Fraction)
    assert isinstance(normal_margin, Fraction)
    assert isinstance(component_error, Fraction)
    assert isinstance(wave_count, int)
    assert isinstance(base_stored_utilization, Fraction)
    assert isinstance(normal_stored_utilization, Fraction)

    base_factors = _coordinate_factor_record(
        "base",
        selected_analysis,
        wave_count,
        component_error,
        base_margin,
        base_stored_utilization,
    )
    normal_factors = _coordinate_factor_record(
        "normal",
        external_analysis,
        wave_count,
        component_error,
        normal_margin,
        normal_stored_utilization,
    )
    factor_audit = {
        "factorization_formula": "U_X = K_X * N * E_53 / m_X",
        "threshold_formulas": {
            "maximum_local_component_error": "m_X / (K_X * N)",
            "maximum_analysis_factor": "m_X / (N * E_53)",
            "maximum_wave_factor": "m_X / (K_X * E_53)",
            "minimum_margin": "K_X * N * E_53",
        },
        "strict_boundary_rule": "equality fails; strict re-entry requires utilization < 1",
        "coordinates": {
            "base": base_factors,
            "normal": normal_factors,
        },
        "all_factor_records_pass": bool(base_factors["passed"] and normal_factors["passed"]),
        "passed": bool(base_factors["passed"] and normal_factors["passed"]),
    }

    candidates: list[dict[str, Any]] = []
    exact_records: dict[int, dict[str, Any]] = {}
    for precision in REGISTERED_PRECISIONS:
        summary, exact = q007w._evaluate_precision(
            precision,
            state_radius,
            selected_analysis,
            external_analysis,
            base_margin,
            normal_margin,
        )
        candidates.append(summary)
        if precision == MINIMUM_PRECISION:
            exact_records[precision] = exact

    p53_control = _p53_q007aj_control(
        payloads["q007aj"],
        candidates[0],
        exact_records[MINIMUM_PRECISION],
    )
    base_selection = _selection_for_gate(candidates, "base_reentry_passed")
    normal_selection = _selection_for_gate(candidates, "normal_reentry_passed")
    joint_selection = _selection_for_gate(candidates, "passed")
    base_precision = base_selection["selected_precision_bits"]
    normal_precision = normal_selection["selected_precision_bits"]
    joint_precision = joint_selection["selected_precision_bits"]
    normal_selected = normal_selection["selected_candidate"]
    dominance = {
        "binary64_base_utilization_exceeds_normal": (
            base_stored_utilization > normal_stored_utilization
        ),
        "base_threshold_exceeds_normal_threshold": bool(
            base_precision is not None
            and normal_precision is not None
            and base_precision > normal_precision
        ),
        "joint_threshold_equals_base_threshold": bool(
            joint_precision is not None and joint_precision == base_precision
        ),
        "base_fails_at_normal_threshold": bool(
            normal_selected is not None and not normal_selected["base_reentry_passed"]
        ),
    }
    dominance["passed"] = all(dominance.values())

    precisions = [candidate["precision_bits"] for candidate in candidates]
    coverage_match = bool(
        precisions == list(REGISTERED_PRECISIONS)
        and len(set(precisions)) == len(REGISTERED_PRECISIONS)
        and len(candidates) == EXPECTED_CANDIDATE_COUNT
    )
    monotonicity = {
        key: q007w._nonincreasing(candidates, key)
        for key in (
            "post_filter_component_error_sum",
            "wiener_error_upper",
            "base_coordinate_error_upper",
            "normal_coordinate_error_upper",
            "base_margin_utilization",
            "normal_margin_utilization",
        )
    }
    monotonicity["stage_lowers_nondecreasing"] = q007w._stage_lowers_nondecreasing(candidates)
    monotonicity_passed = all(monotonicity.values())
    all_domains_pass = all(
        _fraction_from_record(candidate["minimum_density_divisor"]) > 0
        and _fraction_from_record(candidate["maximum_intermediate_magnitude"])
        < q007w._power_of_two(1024)
        and candidate["one_step_stage_positivity_passed"]
        and candidate["operation_counts_match"]
        and candidate["operation_counts"] == q007aj.EXPECTED_OPERATION_COUNTS
        for candidate in candidates
    )
    selections_pass = bool(
        all(
            selection["first_pass_matches_selection"] and selection["selection_boundary_reproduced"]
            for selection in (
                base_selection,
                normal_selection,
                joint_selection,
            )
        )
    )
    candidate_digest = q007w._candidate_digest(candidates)
    campaign = {
        "registered_precisions": list(REGISTERED_PRECISIONS),
        "candidate_count": len(candidates),
        "candidate_digest_sha256": candidate_digest,
        "candidate_digest_canonicalization": (
            "UTF-8 strict JSON, sorted keys, separators comma/colon"
        ),
        "coverage_match": coverage_match,
        "monotonicity_checks": monotonicity,
        "all_monotonicity_checks_pass": monotonicity_passed,
        "all_candidate_domains_pass": all_domains_pass,
        "candidates": candidates,
    }
    selection = {
        "base": base_selection,
        "normal": normal_selection,
        "joint": joint_selection,
        "dominance_audit": dominance,
        "all_selection_boundaries_reproduced": selections_pass,
        "passed": selections_pass,
    }

    registered_parameters = {
        "minimum_precision_bits": MINIMUM_PRECISION,
        "maximum_precision_bits": MAXIMUM_PRECISION,
        "candidate_count": EXPECTED_CANDIDATE_COUNT,
        "minimum_normal_exponent": MINIMUM_NORMAL_EXPONENT,
        "rounding_mode": "round-to-nearest ties-to-even",
        "normalized_dft_wave_count": wave_count,
        "operation_counts": q007aj.EXPECTED_OPERATION_COUNTS,
    }
    input_digest_sha256 = _canonical_json_sha256(
        {
            "registered_parameters": registered_parameters,
            "input_artifacts": input_records,
            "registered_q007aj_digests": REGISTERED_Q007AJ_DIGESTS,
            "registered_q007w_candidate_digest": (REGISTERED_Q007W_CANDIDATE_DIGEST),
        }
    )
    result_digest_sha256 = _canonical_json_sha256(
        {
            "q007aj_exact_reproduction": q007aj_section,
            "q007w_oracle_reproduction": q007w_section,
            "p53_q007aj_control": p53_control,
            "factor_audit": factor_audit,
            "selection": selection,
        }
    )
    serializable_sections = {
        "input_artifacts": input_records,
        "q007aj_exact_reproduction": q007aj_section,
        "q007w_oracle_reproduction": q007w_section,
        "p53_q007aj_control": p53_control,
        "factor_audit": factor_audit,
        "precision_campaign": campaign,
        "selection": selection,
        "input_digest_sha256": input_digest_sha256,
        "candidate_digest_sha256": candidate_digest,
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
                "Q007aj/Q007w artifact and runner SHA, source, scope, schema, "
                "classifications, validity, and registered outcomes match"
            ),
            "value": {
                "passing_input_count": sum(record["passed"] for record in input_records.values()),
                "expected_input_count": len(input_records),
            },
        },
        "q007aj_mixed_result_exactly_reproduced": {
            "passed": q007aj_section["passed"],
            "threshold": (
                "stored cycle, two digests, seven validity gates, five-pass "
                "two-fail hypotheses, stage bounds, and re-entry quantities "
                "reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007aj_section[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007aj_section["digests_match"],
                "failed_hypotheses": q007aj_section["failed_hypothesis_names"],
            },
        },
        "q007w_old_precision_oracle_exactly_reproduced": {
            "passed": q007w_section["passed"],
            "threshold": (
                "stored cycle, old 85-bit boundary, 76-candidate digest, all "
                "gates, ties-to-even, and p=53 Q007v control reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007w_section["stored_cycle_reproduced_exactly"],
                "selected_precision_bits": q007w_section["old_selected_precision_bits"],
                "candidate_digest_matches": q007w_section["candidate_digest_matches"],
            },
        },
        "p53_new_tube_control_exactly_reproduced": {
            "passed": p53_control["passed"],
            "threshold": (
                "p=53 reproduces every Q007aj target/error record, stage "
                "summary, operation count, re-entry quantity, and split outcome"
            ),
            "value": p53_control["passed"],
        },
        "exact_four_factor_identities": {
            "passed": factor_audit["passed"],
            "threshold": (
                "both coordinates exactly satisfy U=K*N*E/m and all four "
                "single-factor boundary identities with positive quantities"
            ),
            "value": {
                name: record["passed"] for name, record in factor_audit["coordinates"].items()
            },
        },
        "complete_monotone_campaign_and_boundaries": {
            "passed": bool(
                coverage_match and monotonicity_passed and all_domains_pass and selections_pass
            ),
            "threshold": (
                "all 76 integer precisions are unique, domain-safe, operation-"
                "matched, error-monotone, stage-positive, and all three first-"
                "pass boundaries reproduce"
            ),
            "value": {
                "coverage": coverage_match,
                "monotonicity": monotonicity_passed,
                "domains": all_domains_pass,
                "selection_boundaries": selections_pass,
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": finite_strict_json,
            "threshold": (
                "all records are finite strict JSON and canonical input, "
                "candidate, and result digests are emitted"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest_sha256,
                "candidate_digest_sha256": candidate_digest,
                "result_digest_sha256": result_digest_sha256,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    base_utilization = _fraction_from_record(base_factors["margin_utilization"])
    normal_utilization = _fraction_from_record(normal_factors["margin_utilization"])
    base_unit_wave = _fraction_from_record(
        base_factors["unit_wave_counterfactual"]["margin_utilization"]
    )
    normal_unit_wave = _fraction_from_record(
        normal_factors["unit_wave_counterfactual"]["margin_utilization"]
    )
    joint_previous = joint_selection["previous_precision_candidate"]
    all_stage_lowers_positive = all(
        candidate["one_step_stage_positivity_passed"] for candidate in candidates
    )
    hypothesis_gates = {
        "binary64_control_failure_reproduced": {
            "passed": bool(base_utilization > 1 and normal_utilization > 1),
            "threshold": "registered p=53 base and normal utilizations both exceed one",
            "value": {
                "base": float(base_utilization),
                "normal": float(normal_utilization),
            },
        },
        "four_factorization_identities_close": {
            "passed": factor_audit["passed"],
            "threshold": (
                "both utilization factorizations and four single-factor "
                "threshold identities close exactly"
            ),
            "value": factor_audit["all_factor_records_pass"],
        },
        "finite_minimal_base_precision": {
            "passed": bool(
                base_precision is not None and base_selection["selection_boundary_reproduced"]
            ),
            "threshold": "finite p_B passes and p_B-1 fails base re-entry",
            "value": base_precision,
        },
        "finite_minimal_normal_precision": {
            "passed": bool(
                normal_precision is not None and normal_selection["selection_boundary_reproduced"]
            ),
            "threshold": "finite p_N passes and p_N-1 fails normal re-entry",
            "value": normal_precision,
        },
        "finite_minimal_joint_precision": {
            "passed": bool(
                joint_precision is not None
                and base_precision is not None
                and normal_precision is not None
                and joint_precision == max(base_precision, normal_precision)
                and joint_selection["selection_boundary_reproduced"]
                and joint_previous is not None
                and not joint_previous["passed"]
                and all_stage_lowers_positive
            ),
            "threshold": (
                "finite p_* equals max(p_B,p_N), p_*-1 fails joint re-entry, "
                "and every registered stage lower remains positive"
            ),
            "value": joint_precision,
        },
        "base_coordinate_is_dominant": {
            "passed": dominance["passed"],
            "threshold": ("U_B>U_N, p_B>p_N, p_*=p_B, and base still fails at p_N"),
            "value": dominance,
        },
        "wave_only_counterfactual_separates_coordinates": {
            "passed": bool(base_unit_wave > 1 and normal_unit_wave < 1),
            "threshold": "U_B/289>1 while U_N/289<1",
            "value": {
                "base_unit_wave_utilization": float(base_unit_wave),
                "normal_unit_wave_utilization": float(normal_unit_wave),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007ak re-entry factor audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered factor audit isolates base re-entry as the dominant "
            "Q007ag binary64 obstruction"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered factor audit did not isolate a finite dominant Q007ag re-entry threshold"
        )

    return {
        "question": (
            "Which exact factor dominates the Q007ag binary64 re-entry failure, "
            "and what minimum ideal precision clears each strict margin?"
        ),
        "registered_parameters": registered_parameters,
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "q007aj_binary64_reentry_failure_exactly_factorized": (hypotheses_passed),
            "finite_minimum_base_precision_exists": hypotheses_passed,
            "finite_minimum_normal_precision_exists": hypotheses_passed,
            "finite_minimum_joint_precision_exists": hypotheses_passed,
            "base_coordinate_is_dominant_in_registered_enclosure": (hypotheses_passed),
            "unit_wave_counterfactual_clears_normal_not_base": (hypotheses_passed),
            "implemented_mpfr85_new_tube_reentry_certified": False,
        },
        "claim_boundary": (
            "This accepted diagnostic applies only to the fixed Q007aj "
            "component box and the Q007w ideal-binary operation model on the "
            "registered 53..128 integer campaign. The selected precisions are "
            "sufficient within this worst-case enclosure, not necessary "
            "hardware or trajectory escape thresholds. Unit-wave and unit-"
            "analysis counterfactuals do not construct a realizable norm or "
            "Fourier certificate. This excludes FTZ/DAZ, GPU or compiler "
            "behavior, an MPFR backend trace, fixed-leaf closure, repair, same-"
            "initial shadowing, continuous optimality, grid uniformity, and a "
            "continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007aj_binary64_mixed_result_changed": False,
            "q007w_old_tube_85bit_threshold_changed": False,
            "q007ag_tube_acceptance_changed": False,
            "q007ai_exact_stagewise_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007af_external_disc_obstruction_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted and the joint ideal threshold is at most 85 bits, "
            "preregister Q007al to replay the concrete MPFR-85 backend on the "
            "new tube; keep fixed-leaf closure and repair as later separate "
            "gates. If it exceeds 85 bits, preregister a higher precision first."
        ),
    }


def run_q007ak_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_reentry_factor_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "exact Q007ag roundoff re-entry factor decomposition and "
                "ideal-precision threshold certificate"
            ),
            "construction_grid": [17, 17],
            "omega": 1.5,
            "eta": 0.01,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "base_modal_l1_radius": float(q007aj.BASE_RADIUS),
            "normal_coordinate_radius": float(q007aj.NORMAL_RADIUS),
            "precision_candidates": ("all integer significand bits 53 through 128"),
            "rounding_model": "ideal binary round-to-nearest ties-to-even",
            "claim": (
                "exact margin/analysis/Wiener/local-error factorization and "
                "separate sufficient base, normal, and joint ideal-precision "
                "thresholds for the fixed Q007aj enclosure only"
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
    result = run_q007ak_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
