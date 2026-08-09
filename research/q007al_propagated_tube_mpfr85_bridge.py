"""Sealed Q007al propagated-tube bridge to the concrete MPFR-85 backend."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007ak_reentry_factor_audit as q007ak
import research.q007w_ideal_precision_threshold as q007w
import research.q007x_mpfr_fixed_leaf as q007x
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
PRECISION_BITS = 85
EXPECTED_PROBE_COUNT = 4

REGISTERED_INPUTS = {
    "q007ak": {
        "filename": "q007ak_reentry_factor_audit.json",
        "module": q007ak,
        "artifact_sha256": (
            "aae6b560125cd29dad5b87bf20e9806ae26a5b1b6ae2ee9c055580042561cf7c"
        ),
        "runner_sha256": (
            "c8bb3f7a84d19d9ab2794d9a1c27334ecd53e62dabce7862343b51ef30cd29b1"
        ),
        "diagnostic": (
            "exact Q007ag roundoff re-entry factor decomposition and "
            "ideal-precision threshold certificate"
        ),
        "classification": (
            "registered factor audit isolates base re-entry as the dominant "
            "Q007ag binary64 obstruction"
        ),
        "outcome": "accepted",
        "validity_count": 7,
        "hypothesis_count": 7,
    },
    "q007x": {
        "filename": "q007x_mpfr_fixed_leaf.json",
        "module": q007x,
        "artifact_sha256": (
            "20ba483c4c627de015673a2f8873cc020a5c1a43ee48c7715121a00330e13566"
        ),
        "runner_sha256": (
            "de16e86ab365e6e64b15fd62ebdb442a54e05d4e4e529ae1e018299983d7491b"
        ),
        "diagnostic": "concrete MPFR-85 operation bridge and fixed-leaf closure audit",
        "classification": (
            "MPFR-85 realizes the Q007w one-step arithmetic bound but not "
            "the fixed conservation leaf"
        ),
        "outcome": "not_certified",
        "validity_count": 8,
        "hypothesis_count": 6,
    },
}
REGISTERED_Q007AK_DIGESTS = {
    "input": "333ce7e6b4537947808a369f1c218c2d930a11df4b826994df0947fa42489d46",
    "candidate": "eacc824a8f0fc891971c210883d05f7178e4fe5848ab3b2432dc94adf289e567",
    "result": "a4d10df4c1d6edd83488115d501af21ad6727dd6321e159e37b2b0e434858644",
}
REGISTERED_Q007X_DIGESTS = {
    "probe": "a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329",
    "trace": "49ce9b304b4b6a07fdf7d7baed6c9118a97c5a08e489e3aa5eacde28662c2351",
    "result": "12cb83a87895d50523c909ad314b9ad155ac507af73e05f1b28cfb2a65328c7d",
}
REGISTERED_SOURCE_SHA256 = {
    "backend": "25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc",
    "pyproject": "97e8ed6af7906243a656191f96c80b8f7c1ef4b737587c888092c476be508d94",
    "d2q9": "6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53",
    "filter": "5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea",
}
EXPECTED_Q007X_SUMMARY = {
    "all_traces_match": True,
    "all_operation_domains_pass": True,
    "all_stage_bounds_and_positivity_pass": True,
    "all_encodings_conserve": False,
    "all_collisions_conserve": False,
    "all_streaming_conserves": True,
    "all_filters_conserve": False,
    "all_full_steps_conserve": False,
    "context_restored": True,
}
EXPECTED_Q007X_FAILED_HYPOTHESES = [
    "componentwise_encoding_preserves_fixed_leaf",
    "collision_preserves_fixed_leaf",
    "streaming_and_filter_preserve_fixed_leaf",
    "fixed_leaf_all_iterate_induction_closes",
]


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
    common = bool(
        scope.get("diagnostic") == REGISTERED_INPUTS[name]["diagnostic"]
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega")) == 1.5
        and float(scope.get("eta")) == 0.01
    )
    if name == "q007ak":
        return bool(
            common
            and scope.get("conservation_treatment")
            == "fixed global mass and momentum leaf"
            and scope.get("manifold") == "Q007ae exact graph-gauge manifold"
            and scope.get("norm")
            == "Q007p Fourier external-coordinate block-sum l1"
            and float(scope.get("base_modal_l1_radius")) == 9e-17
            and float(scope.get("normal_coordinate_radius")) == 5e-11
            and scope.get("rounding_model")
            == "ideal binary round-to-nearest ties-to-even"
        )
    return bool(
        common
        and scope.get("conservation_treatment")
        == "exact global mass and momentum equality on the fixed leaf"
        and scope.get("rounding_model")
        == "gmpy2 2.3.1 with MPFR 4.2.2 round-to-nearest ties-to-even"
    )


def _outcome_matches(name: str, cycle: dict[str, Any]) -> bool:
    hypotheses = cycle.get("hypothesis_gates", {})
    failed = [key for key, gate in hypotheses.items() if not gate.get("passed", False)]
    if name == "q007ak":
        return bool(
            cycle.get("study_validity") == "passed"
            and cycle.get("hypothesis_outcome") == "accepted"
            and not failed
        )
    return bool(
        cycle.get("study_validity") == "passed"
        and cycle.get("hypothesis_outcome") == "not_certified"
        and failed == EXPECTED_Q007X_FAILED_HYPOTHESES
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
        runner_path = Path(registration["module"].__file__).resolve()
        cycle = payload.get("cycle", {})
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
            "artifact_runner_sha256_matches": (
                artifact_runner_sha == registration["runner_sha256"]
            ),
            "schema_version_matches": payload.get("schema_version") == 1,
            "source_matches": payload.get("source") == source_metadata(),
            "scope_matches": _scope_matches(name, payload),
            "study_gate_matches": payload.get("study_gate") == "passed",
            "scientific_outcome": payload.get("scientific_outcome"),
            "scientific_outcome_matches": (
                payload.get("scientific_outcome") == registration["outcome"]
            ),
            "scientific_classification": cycle.get("scientific_classification"),
            "classification_matches": (
                cycle.get("scientific_classification") == registration["classification"]
            ),
            "validity_gate_count": len(cycle.get("validity_gates", {})),
            "registered_validity_gate_count": registration["validity_count"],
            "all_validity_gates_pass": _all_gates_pass(cycle, "validity_gates"),
            "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
            "registered_hypothesis_gate_count": registration["hypothesis_count"],
            "registered_outcome_matches": _outcome_matches(name, cycle),
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


def _q007ak_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    stored = payload["cycle"]
    replayed = q007ak.run_reentry_factor_audit(directory)
    selection = stored["selection"]
    candidates = stored["precision_campaign"]["candidates"]
    p85_candidates = [
        candidate
        for candidate in candidates
        if candidate.get("precision_bits") == PRECISION_BITS
    ]
    p85_candidate = p85_candidates[0] if len(p85_candidates) == 1 else {}
    observed_digests = {
        "input": stored.get("input_digest_sha256"),
        "candidate": stored.get("candidate_digest_sha256"),
        "result": stored.get("result_digest_sha256"),
    }
    thresholds = {
        name: selection[name].get("selected_precision_bits")
        for name in ("base", "normal", "joint")
    }
    passed = bool(
        replayed == stored
        and observed_digests == REGISTERED_Q007AK_DIGESTS
        and len(stored["validity_gates"]) == 7
        and _all_gates_pass(stored, "validity_gates")
        and len(stored["hypothesis_gates"]) == 7
        and _all_gates_pass(stored, "hypothesis_gates")
        and thresholds == {"base": 79, "normal": 59, "joint": 79}
        and len(p85_candidates) == 1
        and p85_candidate.get("passed", False)
        and p85_candidate.get("base_reentry_passed", False)
        and p85_candidate.get("normal_reentry_passed", False)
        and p85_candidate.get("one_step_stage_positivity_passed", False)
        and stored["scientific_classification"]
        == REGISTERED_INPUTS["q007ak"]["classification"]
    )
    section = {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007AK_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007AK_DIGESTS,
        "validity_gate_count": len(stored["validity_gates"]),
        "all_validity_gates_pass": _all_gates_pass(stored, "validity_gates"),
        "hypothesis_gate_count": len(stored["hypothesis_gates"]),
        "all_hypothesis_gates_pass": _all_gates_pass(stored, "hypothesis_gates"),
        "selection_thresholds": thresholds,
        "p85_candidate_count": len(p85_candidates),
        "p85_candidate_passed": p85_candidate.get("passed", False),
        "passed": passed,
    }
    fixed = stored["q007aj_exact_reproduction"]
    exact = {
        "state_radius": _fraction_from_record(fixed["tube_state_wiener_l1_upper"]),
        "selected_analysis": _fraction_from_record(fixed["selected_analysis_upper"]),
        "external_analysis": _fraction_from_record(fixed["external_analysis_upper"]),
        "base_margin": _fraction_from_record(fixed["base_forward_invariance_margin"]),
        "normal_margin": _fraction_from_record(
            fixed["normal_tube_forward_invariance_margin"]
        ),
        "stored_p85_candidate": p85_candidate,
    }
    return section, exact


def _q007x_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    stored = payload["cycle"]
    replayed = q007x.run_mpfr_fixed_leaf_audit(directory)
    campaign = stored["backend_campaign"]
    observed_digests = {
        "probe": stored["probe_registration"].get("probe_digest_sha256"),
        "trace": campaign.get("aggregate_trace_digest_sha256"),
        "result": campaign.get("result_digest_sha256"),
    }
    hypotheses = stored["hypothesis_gates"]
    failed_hypotheses = [
        name for name, gate in hypotheses.items() if not gate.get("passed", False)
    ]
    passed = bool(
        replayed == stored
        and observed_digests == REGISTERED_Q007X_DIGESTS
        and len(stored["validity_gates"]) == 8
        and _all_gates_pass(stored, "validity_gates")
        and len(hypotheses) == 6
        and failed_hypotheses == EXPECTED_Q007X_FAILED_HYPOTHESES
        and campaign["probe_count"] == EXPECTED_PROBE_COUNT
        and campaign["summary"] == EXPECTED_Q007X_SUMMARY
        and stored["context_audit"]["passed"]
        and stored["source_audit"]["passed"]
        and stored["probe_registration"]["passed"]
        and stored["constant_algebra"]["passed"]
        and stored["scientific_classification"]
        == REGISTERED_INPUTS["q007x"]["classification"]
    )
    return {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007X_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007X_DIGESTS,
        "validity_gate_count": len(stored["validity_gates"]),
        "all_validity_gates_pass": _all_gates_pass(stored, "validity_gates"),
        "hypothesis_gate_count": len(hypotheses),
        "failed_hypothesis_names": failed_hypotheses,
        "registered_summary": campaign["summary"],
        "context_passed": stored["context_audit"]["passed"],
        "source_passed": stored["source_audit"]["passed"],
        "probe_registration_passed": stored["probe_registration"]["passed"],
        "constant_algebra_passed": stored["constant_algebra"]["passed"],
        "passed": passed,
    }


def _fresh_p85_certificate(exact: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    stored = exact["stored_p85_candidate"]
    fresh, _fresh_exact = q007w._evaluate_precision(
        PRECISION_BITS,
        exact["state_radius"],
        exact["selected_analysis"],
        exact["external_analysis"],
        exact["base_margin"],
        exact["normal_margin"],
    )
    stored_digest = _canonical_json_sha256(stored)
    fresh_digest = _canonical_json_sha256(fresh)
    base_error = _fraction_from_record(fresh["base_coordinate_error_upper"])
    normal_error = _fraction_from_record(fresh["normal_coordinate_error_upper"])
    minimum_stage_lower = _fraction_from_record(fresh["minimum_stage_lower"])
    passed = bool(
        fresh == stored
        and fresh_digest == stored_digest
        and fresh["precision_bits"] == PRECISION_BITS
        and PRECISION_BITS > 79
        and fresh["operation_counts_match"]
        and fresh["one_step_stage_positivity_passed"]
        and fresh["base_reentry_passed"]
        and fresh["normal_reentry_passed"]
        and fresh["passed"]
        and minimum_stage_lower > 0
        and base_error < exact["base_margin"]
        and normal_error < exact["normal_margin"]
    )
    record = {
        "precision_bits": PRECISION_BITS,
        "joint_threshold_bits": 79,
        "precision_exceeds_joint_threshold": PRECISION_BITS > 79,
        "stored_candidate_digest_sha256": stored_digest,
        "fresh_candidate_digest_sha256": fresh_digest,
        "candidate_digests_match": fresh_digest == stored_digest,
        "stored_candidate_reproduced_exactly": fresh == stored,
        "candidate": fresh,
        "base_margin": _fraction_record(exact["base_margin"]),
        "normal_margin": _fraction_record(exact["normal_margin"]),
        "strict_base_budget": base_error < exact["base_margin"],
        "strict_normal_budget": normal_error < exact["normal_margin"],
        "passed": passed,
    }
    q007x_exact = {
        "state_radius": exact["state_radius"],
        "base_margin": exact["base_margin"],
        "normal_margin": exact["normal_margin"],
        "base_error": base_error,
        "normal_error": normal_error,
        "stage_error_bounds": {
            name: _fraction_from_record(stage["maximum_component_error"])
            for name, stage in fresh["stage_bounds"].items()
        },
        "stage_population_lowers": {
            name: _fraction_from_record(stage["population_lower"])
            for name, stage in fresh["stage_bounds"].items()
        },
        "rounded_constants": fresh["rounded_constants"],
        "registered_operation_counts": fresh["operation_counts"],
    }
    return record, q007x_exact


def _conservation_regression(
    old_cycle: dict[str, Any],
    campaign: dict[str, Any],
) -> dict[str, Any]:
    old_campaign = old_cycle["backend_campaign"]
    old_by_name = {record["name"]: record for record in old_campaign["probes"]}
    new_by_name = {record["name"]: record for record in campaign["probes"]}
    names_match = list(new_by_name) == list(old_by_name)
    conservation_matches = bool(
        names_match
        and all(
            new_by_name[name]["conservation"] == old_by_name[name]["conservation"]
            for name in old_by_name
        )
    )
    observed_stage_fields = (
        "maximum_observed_component_error",
        "maximum_error_index",
        "minimum_mpfr_population",
        "stage_digest_sha256",
    )
    observed_stages_match = bool(
        names_match
        and all(
            all(
                all(
                    new_by_name[name]["stage_comparisons"][stage][field]
                    == old_by_name[name]["stage_comparisons"][stage][field]
                    for field in observed_stage_fields
                )
                for stage in old_by_name[name]["stage_comparisons"]
            )
            for name in old_by_name
        )
    )
    summary = campaign["summary"]
    summary_matches = summary == EXPECTED_Q007X_SUMMARY
    trace_digest_matches = bool(
        campaign["aggregate_trace_digest_sha256"] == REGISTERED_Q007X_DIGESTS["trace"]
    )
    passed = bool(
        names_match
        and conservation_matches
        and observed_stages_match
        and summary_matches
        and trace_digest_matches
    )
    return {
        "probe_names_match": names_match,
        "conservation_records_match_q007x": conservation_matches,
        "observed_stage_records_match_q007x": observed_stages_match,
        "summary": summary,
        "registered_summary": EXPECTED_Q007X_SUMMARY,
        "summary_matches": summary_matches,
        "aggregate_trace_digest_matches_q007x": trace_digest_matches,
        "fixed_leaf_closure_certified": False,
        "passed": passed,
    }


def run_propagated_tube_mpfr85_bridge_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    q007ak_section, exact = _q007ak_reproduction(directory, payloads["q007ak"])
    q007x_section = _q007x_reproduction(directory, payloads["q007x"])
    ideal_p85, q007x_exact = _fresh_p85_certificate(exact)

    source_audit = q007x._source_audit(q007x_exact)
    context_audit = q007x._context_audit()
    probe_audit, probes = q007x._probe_registration_audit(q007x_exact["state_radius"])
    concrete = q007x.backend.MPFRD2Q9Backend()
    constant_audit = q007x._constant_algebra_audit(concrete.constants, q007x_exact)
    campaign, conservation = q007x._backend_campaign(probes, q007x_exact)
    conservation_regression = _conservation_regression(
        payloads["q007x"]["cycle"],
        campaign,
    )

    registered_parameters = {
        "size": SIZE,
        "wave_count": WAVE_COUNT,
        "precision_bits": PRECISION_BITS,
        "joint_ideal_threshold_bits": 79,
        "omega": _fraction_record(q007x.backend.EXACT_OMEGA),
        "eta": _fraction_record(q007x.backend.EXACT_ETA),
        "probe_count": EXPECTED_PROBE_COUNT,
        "probe_names": list(q007x.PROBE_NAMES),
        "expected_construction_trace_count": q007x.EXPECTED_CONSTRUCTION_TRACE_COUNT,
        "expected_map_trace_per_site": q007x.EXPECTED_MAP_TRACE_PER_SITE,
        "expected_map_trace_count": q007x.EXPECTED_MAP_TRACE_COUNT,
        "expected_total_trace_per_probe": q007x.EXPECTED_TOTAL_TRACE_PER_PROBE,
        "registered_source_sha256": REGISTERED_SOURCE_SHA256,
    }
    input_digest_sha256 = _canonical_json_sha256(
        {
            "registered_parameters": registered_parameters,
            "input_artifacts": input_records,
            "registered_q007ak_digests": REGISTERED_Q007AK_DIGESTS,
            "registered_q007x_digests": REGISTERED_Q007X_DIGESTS,
        }
    )
    result_digest_sha256 = _canonical_json_sha256(
        {
            "q007ak_reproduction": q007ak_section,
            "q007x_reproduction": q007x_section,
            "ideal_p85_certificate": ideal_p85,
            "source_audit": source_audit,
            "context_audit": context_audit,
            "probe_registration": probe_audit,
            "constant_algebra": constant_audit,
            "backend_campaign": campaign,
            "conservation_regression": conservation_regression,
        }
    )
    digest_records = {
        "input_digest_sha256": input_digest_sha256,
        "candidate_digest_sha256": ideal_p85["fresh_candidate_digest_sha256"],
        "probe_digest_sha256": probe_audit["probe_digest_sha256"],
        "trace_digest_sha256": campaign["aggregate_trace_digest_sha256"],
        "campaign_result_digest_sha256": campaign["result_digest_sha256"],
        "result_digest_sha256": result_digest_sha256,
    }
    serializable_sections = {
        "input_artifacts": input_records,
        "q007ak_reproduction": q007ak_section,
        "q007x_reproduction": q007x_section,
        "ideal_p85_certificate": ideal_p85,
        "source_audit": source_audit,
        "context_audit": context_audit,
        "probe_registration": probe_audit,
        "constant_algebra": constant_audit,
        "backend_campaign": campaign,
        "conservation_regression": conservation_regression,
        **digest_records,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    all_digests_present = all(
        isinstance(value, str) and len(value) == 64 for value in digest_records.values()
    )

    trace_passed = campaign["summary"]["all_traces_match"]
    operation_passed = campaign["summary"]["all_operation_domains_pass"]
    stage_passed = campaign["summary"]["all_stage_bounds_and_positivity_pass"]
    context_restored = campaign["summary"]["context_restored"]
    source_context_constant_passed = bool(
        source_audit["passed"] and context_audit["passed"] and constant_audit["passed"]
    )
    validity_gates = {
        "sealed_inputs_source_scope_and_outcomes": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": (
                "Q007ak/Q007x artifact and runner SHA, source, scope, schema, "
                "classifications, validity, and registered outcomes match"
            ),
            "value": {
                "passing_input_count": sum(
                    record["passed"] for record in input_records.values()
                ),
                "expected_input_count": len(input_records),
            },
        },
        "q007ak_threshold_and_p85_exactly_reproduced": {
            "passed": q007ak_section["passed"],
            "threshold": (
                "stored cycle, three digests, all 7+7 gates, 79/59/79 "
                "boundaries, and the passing p=85 candidate reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007ak_section[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007ak_section["digests_match"],
                "selection_thresholds": q007ak_section["selection_thresholds"],
            },
        },
        "q007x_mixed_backend_result_exactly_reproduced": {
            "passed": q007x_section["passed"],
            "threshold": (
                "stored cycle, three digests, all 8 validity gates, 2-pass/"
                "4-fail hypotheses, runtime/source/trace/probes reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007x_section[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007x_section["digests_match"],
                "failed_hypotheses": q007x_section["failed_hypothesis_names"],
            },
        },
        "new_tube_ideal_p85_candidate_exactly_reproduced": {
            "passed": ideal_p85["passed"],
            "threshold": (
                "fresh p=85 candidate equals Q007ak exactly, exceeds the "
                "79-bit joint threshold, stays positive, and clears both margins"
            ),
            "value": {
                "candidate_reproduced": ideal_p85[
                    "stored_candidate_reproduced_exactly"
                ],
                "precision_exceeds_threshold": ideal_p85[
                    "precision_exceeds_joint_threshold"
                ],
            },
        },
        "registered_context_sources_and_constants": {
            "passed": source_context_constant_passed,
            "threshold": (
                "package/runtime/context, backend/pyproject/D2Q9/filter SHA, "
                "constant algebra, and operation order match"
            ),
            "value": {
                "source": source_audit["passed"],
                "context": context_audit["passed"],
                "constant_algebra": constant_audit["passed"],
            },
        },
        "registered_probes_trace_schedule_and_domain": {
            "passed": bool(
                probe_audit["passed"]
                and trace_passed
                and operation_passed
                and context_restored
            ),
            "threshold": (
                "all 4 probes fit the new box and all trace, count, domain, "
                "and context-restoration gates pass"
            ),
            "value": {
                "probe_registration": probe_audit["passed"],
                "trace": trace_passed,
                "operation_domain": operation_passed,
                "context_restored": context_restored,
            },
        },
        "concrete_stages_and_conservation_regression": {
            "passed": bool(stage_passed and conservation_regression["passed"]),
            "threshold": (
                "all concrete stage discrepancies fit the p=85 bounds with "
                "positive populations and the Q007x conservation diagnosis reproduces"
            ),
            "value": {
                "stages": stage_passed,
                "conservation_regression": conservation_regression["passed"],
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": bool(finite_strict_json and all_digests_present),
            "threshold": (
                "all records are finite strict JSON and canonical input, "
                "candidate, probe, trace, campaign-result, and result digests exist"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "all_digests_present": all_digests_present,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    semantic_bridge = bool(
        source_context_constant_passed and trace_passed and operation_passed
    )
    base_error = _fraction_from_record(
        ideal_p85["candidate"]["base_coordinate_error_upper"]
    )
    normal_error = _fraction_from_record(
        ideal_p85["candidate"]["normal_coordinate_error_upper"]
    )
    base_margin = _fraction_from_record(ideal_p85["base_margin"])
    normal_margin = _fraction_from_record(ideal_p85["normal_margin"])
    hypothesis_gates = {
        "mpfr85_realizes_registered_ideal_operation_semantics": {
            "passed": bool(validity_passed and semantic_bridge),
            "threshold": (
                "registered source/context/constants and every traced operation "
                "realize ideal p=85 nearest-even semantics"
            ),
            "value": semantic_bridge,
        },
        "all_registered_trace_count_and_domain_gates_pass": {
            "passed": bool(
                validity_passed
                and trace_passed
                and operation_passed
                and context_restored
            ),
            "threshold": (
                "all 4 probe construction/encoding/map traces, operation "
                "counts, domains, and context restoration pass"
            ),
            "value": {
                "trace": trace_passed,
                "operation_domain": operation_passed,
                "context_restored": context_restored,
            },
        },
        "all_concrete_stage_bounds_and_positivity_pass": {
            "passed": bool(validity_passed and stage_passed),
            "threshold": (
                "every concrete stage discrepancy is at most its p=85 upper "
                "and every concrete population is strictly positive"
            ),
            "value": stage_passed,
        },
        "ideal_p85_base_error_fits_q007ag_margin": {
            "passed": bool(validity_passed and base_error < base_margin),
            "threshold": "ideal p=85 base complement error is strictly below its margin",
            "value": {
                "error": float(base_error),
                "margin": float(base_margin),
            },
        },
        "ideal_p85_normal_error_fits_q007ag_margin": {
            "passed": bool(validity_passed and normal_error < normal_margin),
            "threshold": "ideal p=85 normal complement error is strictly below its margin",
            "value": {
                "error": float(normal_error),
                "margin": float(normal_margin),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007al propagated-tube MPFR-85 bridge invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered MPFR-85 backend realizes the Q007ag one-step arithmetic "
            "and complement-coordinate error budgets"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered MPFR-85 backend does not realize the Q007ag one-step "
            "arithmetic budget"
        )

    return {
        "question": (
            "Does the unchanged Q007x concrete MPFR-85 backend realize the "
            "Q007ak p=85 one-step stage and complement-coordinate error budgets "
            "on the propagated Q007ag component box?"
        ),
        "registered_parameters": registered_parameters,
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "concrete_backend_realizes_registered_mpfr85_semantics": bool(
                hypotheses_passed
            ),
            "concrete_backend_one_step_stages_are_enclosed_and_positive": bool(
                hypotheses_passed
            ),
            "ideal_p85_base_and_normal_error_budgets_fit_q007ag_margins": bool(
                hypotheses_passed
            ),
            "rounded_output_is_on_the_fixed_conservation_leaf": False,
            "actual_q007ag_tube_reentry_is_certified": False,
            "all_iterate_mpfr85_q007ag_tube_invariance_is_certified": False,
        },
        "conservation_diagnostic": {
            **conservation,
            "fixed_leaf_closure_certified": False,
            "acceptance_hypothesis": False,
        },
        "claim_boundary": (
            "Acceptance covers only the fixed MPFR source, context, constants, "
            "and operation schedule, the Q007ak one-step worst-case arithmetic "
            "budget on the Q007ag component box, and four registered finite-"
            "probe stage checks. The base/normal comparisons bound arithmetic "
            "error relative to the ideal exact-map output. Componentwise "
            "encoding, collision, and filter still fail exact global mass/"
            "momentum conservation, so actual rounded fixed-leaf membership, "
            "Q007ag tube re-entry, all-iterate induction, repair, same-initial "
            "shadowing, multi-step trajectories, performance, other MPFR builds, "
            "GPU/compiler behavior, grid uniformity, and a continuum limit are "
            "not certified. Finite probes are not a tube-wide sampling proof."
        ),
        "preserved_prior_outcomes": {
            "q007x_fixed_leaf_noncertificate_changed": False,
            "q007ak_precision_threshold_changed": False,
            "q007ag_tube_acceptance_changed": False,
            "q007ai_exact_stagewise_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007af_external_disc_obstruction_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister a new-tube conservation-exact repair "
            "whose own arithmetic cost fits the remaining Q007ag margins; do "
            "not infer fixed-leaf re-entry or all-iterate invariance yet."
        ),
    }


def run_q007al_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_propagated_tube_mpfr85_bridge_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": {
            **runtime_metadata(),
            **q007x.backend.backend_runtime_metadata(),
        },
        "mathematical_scope": {
            "diagnostic": (
                "propagated-tube concrete MPFR-85 one-step arithmetic and "
                "complement-coordinate budget bridge"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(q007x.backend.EXACT_OMEGA),
            "eta": float(q007x.backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed-leaf exact-map reference with rounded conservation "
                "defects retained as a non-hypothesis diagnostic"
            ),
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "base_modal_l1_radius": 9e-17,
            "normal_coordinate_radius": 5e-11,
            "input_encoding": (
                "Fraction to exact mpq to 85-bit MPFR componentwise rounding"
            ),
            "rounding_model": (
                "gmpy2 2.3.1 with MPFR 4.2.2 round-to-nearest ties-to-even"
            ),
            "claim": (
                "one-step concrete stage enclosure and ideal complement-error "
                "budget bridge only, excluding fixed-leaf closure and re-entry"
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
    result = run_q007al_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
