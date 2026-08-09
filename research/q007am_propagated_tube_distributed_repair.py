"""Sealed Q007am distributed fixed-leaf repair audit on the Q007ag tube."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007al_propagated_tube_mpfr85_bridge as q007al
import research.q007w_ideal_precision_threshold as q007w
import research.q007y_distributed_conservation_repair as q007y
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
    "q007al": {
        "filename": "q007al_propagated_tube_mpfr85_bridge.json",
        "module": q007al,
        "artifact_sha256": (
            "bf1a2d9959f24cfc83a4efb2926ec76d9ced97755846ee310490585940d8dcf5"
        ),
        "runner_sha256": (
            "b82e03145e0c7f1c20b1d1345b87acbae5ce526b732969c391b88141118dfd8e"
        ),
        "diagnostic": (
            "propagated-tube concrete MPFR-85 one-step arithmetic and "
            "complement-coordinate budget bridge"
        ),
        "classification": (
            "registered MPFR-85 backend realizes the Q007ag one-step arithmetic "
            "and complement-coordinate error budgets"
        ),
        "outcome": "accepted",
        "validity_count": 8,
        "hypothesis_count": 5,
    },
    "q007y": {
        "filename": "q007y_distributed_conservation_repair.json",
        "module": q007y,
        "artifact_sha256": (
            "a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648"
        ),
        "runner_sha256": (
            "ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811"
        ),
        "diagnostic": (
            "distributed dyadic fixed-leaf repair and repair-aware "
            "Wiener-budget audit"
        ),
        "classification": (
            "distributed MPFR-85 repair restores the registered fixed-leaf "
            "probes but not the Q007w tube-wide base budget"
        ),
        "outcome": "not_certified",
        "validity_count": 8,
        "hypothesis_count": 7,
    },
}
REGISTERED_Q007AL_DIGESTS = {
    "input": "e14b6251a0f5da2ad4c73c1b08c5e21205e99749917f3f78228de6bb12b13738",
    "candidate": "7b63d94121aea24e589ed3e7b221e154705f42df37c4c603c3f99a4a3b1799c0",
    "probe": "a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329",
    "trace": "49ce9b304b4b6a07fdf7d7baed6c9118a97c5a08e489e3aa5eacde28662c2351",
    "campaign_result": (
        "edbfbe317f2254f3d6a628608a19b4986f7ea308cae889d19ce470f31234dad5"
    ),
    "result": "a46f4850d57b0e7d503177205c2cb3d1ed91679cc4c13b9ef31382dbd7bdcd06",
}
REGISTERED_Q007Y_PROBE_DIGEST = (
    "a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329"
)
REGISTERED_Q007Y_FINITE_RESULT_DIGEST = (
    "f47bb30b0e2280d339a40b196d1ca3dcb84f94b9e8de087bbff215d07a220fe6"
)
EXPECTED_Q007Y_FAILED_HYPOTHESES = [
    "repair_aware_base_budget_closes",
    "repaired_fixed_leaf_all_iterate_induction_closes",
]
EXPECTED_FINITE_SUMMARY = {
    "all_input_repairs_conserve": True,
    "all_exact_maps_preserve_leaf": True,
    "all_output_repairs_conserve": True,
    "all_repairs_solve_and_add_exactly": True,
    "all_backend_operation_domains_pass": True,
    "all_finite_stage_bounds_and_positivity_pass": True,
    "all_streaming_steps_conserve": True,
}
REGISTERED_SOURCE_SHA256 = {
    "backend": "25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc",
    "pyproject": "97e8ed6af7906243a656191f96c80b8f7c1ef4b737587c888092c476be508d94",
    "d2q9": "6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53",
    "filter": "5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea",
    "repair": "ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811",
}
REGISTERED_NEW_TUBE_FLOATS = {
    "input_repair_l1_upper": 1.2452407121655381e-23,
    "input_maximum_site_correction_upper": 4.362085261510107e-26,
    "raw_wiener_error_upper": 2.7067398403858536e-22,
    "repair_wiener_addition_upper": 4.959477728036884e-22,
    "repaired_wiener_error_upper": 7.666217568422737e-22,
    "repaired_to_raw_ratio": 2.8322698229209555,
    "base_coordinate_error_upper": 1.1581233824834727e-21,
    "base_margin": 4.978814700017615e-20,
    "base_margin_utilization": 0.02326102601246388,
    "normal_coordinate_error_upper": 2.2935127565743277e-20,
    "normal_margin": 9.144951058528087e-13,
    "normal_margin_utilization": 2.5079552005207522e-08,
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
    common = bool(
        scope.get("diagnostic") == REGISTERED_INPUTS[name]["diagnostic"]
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega")) == 1.5
        and float(scope.get("eta")) == 0.01
    )
    if name == "q007al":
        return bool(
            common
            and scope.get("manifold") == "Q007ae exact graph-gauge manifold"
            and scope.get("norm")
            == "Q007p Fourier external-coordinate block-sum l1"
            and float(scope.get("base_modal_l1_radius")) == 9e-17
            and float(scope.get("normal_coordinate_radius")) == 5e-11
            and scope.get("rounding_model")
            == "gmpy2 2.3.1 with MPFR 4.2.2 round-to-nearest ties-to-even"
        )
    return bool(
        common
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf with exact diagonal post-stage repair"
        and scope.get("repair_lattice") == "four diagonal populations on h=2^-90"
        and scope.get("rounding_model")
        == "sealed Q007x gmpy2 2.3.1 / MPFR 4.2.2 nearest-even backend"
    )


def _outcome_matches(name: str, cycle: dict[str, Any]) -> bool:
    hypotheses = cycle.get("hypothesis_gates", {})
    failed = [key for key, gate in hypotheses.items() if not gate.get("passed", False)]
    if name == "q007al":
        return bool(
            cycle.get("study_validity") == "passed"
            and cycle.get("hypothesis_outcome") == "accepted"
            and not failed
        )
    return bool(
        cycle.get("study_validity") == "passed"
        and cycle.get("hypothesis_outcome") == "not_certified"
        and failed == EXPECTED_Q007Y_FAILED_HYPOTHESES
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


def _q007al_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    stored = payload["cycle"]
    replayed = q007al.run_propagated_tube_mpfr85_bridge_audit(directory)
    observed_digests = {
        "input": stored.get("input_digest_sha256"),
        "candidate": stored.get("candidate_digest_sha256"),
        "probe": stored.get("probe_digest_sha256"),
        "trace": stored.get("trace_digest_sha256"),
        "campaign_result": stored.get("campaign_result_digest_sha256"),
        "result": stored.get("result_digest_sha256"),
    }
    candidate = stored["ideal_p85_certificate"]["candidate"]
    conservation = stored["conservation_diagnostic"]
    conservation_match = bool(
        not conservation["all_encodings_conserve"]
        and not conservation["all_collisions_conserve"]
        and conservation["all_streaming_conserves"]
        and not conservation["all_filters_conserve"]
        and not conservation["all_full_steps_conserve"]
        and not conservation["fixed_leaf_closure_certified"]
    )
    passed = bool(
        replayed == stored
        and observed_digests == REGISTERED_Q007AL_DIGESTS
        and len(stored["validity_gates"]) == 8
        and _all_gates_pass(stored, "validity_gates")
        and len(stored["hypothesis_gates"]) == 5
        and _all_gates_pass(stored, "hypothesis_gates")
        and candidate["precision_bits"] == PRECISION_BITS
        and candidate["passed"]
        and stored["source_audit"]["passed"]
        and stored["context_audit"]["passed"]
        and stored["probe_registration"]["passed"]
        and conservation_match
        and stored["scientific_classification"]
        == REGISTERED_INPUTS["q007al"]["classification"]
    )
    section = {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "observed_digests": observed_digests,
        "registered_digests": REGISTERED_Q007AL_DIGESTS,
        "digests_match": observed_digests == REGISTERED_Q007AL_DIGESTS,
        "validity_gate_count": len(stored["validity_gates"]),
        "all_validity_gates_pass": _all_gates_pass(stored, "validity_gates"),
        "hypothesis_gate_count": len(stored["hypothesis_gates"]),
        "all_hypothesis_gates_pass": _all_gates_pass(stored, "hypothesis_gates"),
        "p85_candidate_passed": candidate["passed"],
        "source_context_and_probes_passed": bool(
            stored["source_audit"]["passed"]
            and stored["context_audit"]["passed"]
            and stored["probe_registration"]["passed"]
        ),
        "registered_conservation_nonclosure_reproduced": conservation_match,
        "passed": passed,
    }

    certificate = stored["ideal_p85_certificate"]
    raw_wiener = _fraction_from_record(candidate["wiener_error_upper"])
    base_error = _fraction_from_record(candidate["base_coordinate_error_upper"])
    normal_error = _fraction_from_record(candidate["normal_coordinate_error_upper"])
    probe_radii = {
        _fraction_from_record(probe["registered_component_radius"])
        for probe in stored["probe_registration"]["probes"]
    }
    state_radius = next(iter(probe_radii)) if len(probe_radii) == 1 else Fraction(0)
    exact = {
        "state_radius": state_radius,
        "selected_analysis": base_error / raw_wiener,
        "external_analysis": normal_error / raw_wiener,
        "base_margin": _fraction_from_record(certificate["base_margin"]),
        "normal_margin": _fraction_from_record(certificate["normal_margin"]),
        "stored_p85_candidate": candidate,
        "probe_radius_count": len(probe_radii),
    }
    return section, exact


def _q007y_reproduction(
    directory: Path,
    payload: dict[str, Any],
) -> dict[str, Any]:
    stored = payload["cycle"]
    replayed = q007y.run_distributed_repair_audit(directory)
    hypotheses = stored["hypothesis_gates"]
    failed = [name for name, gate in hypotheses.items() if not gate.get("passed", False)]
    tube = stored["tube_wide_repair_bound"]
    campaign = stored["finite_campaign"]
    old_values = {
        "base_margin_utilization": float(
            _fraction_from_record(tube["base_margin_utilization"])
        ),
        "normal_margin_utilization": float(
            _fraction_from_record(tube["normal_margin_utilization"])
        ),
    }
    passed = bool(
        replayed == stored
        and len(stored["validity_gates"]) == 8
        and _all_gates_pass(stored, "validity_gates")
        and len(hypotheses) == 7
        and failed == EXPECTED_Q007Y_FAILED_HYPOTHESES
        and old_values
        == {
            "base_margin_utilization": 2.326054260951996,
            "normal_margin_utilization": 2.507922842743146e-7,
        }
        and stored["probe_registration"]["probe_digest_sha256"]
        == REGISTERED_Q007Y_PROBE_DIGEST
        and campaign["result_digest_sha256"]
        == REGISTERED_Q007Y_FINITE_RESULT_DIGEST
        and campaign["summary"] == EXPECTED_FINITE_SUMMARY
        and campaign["passed"]
        and stored["input_audit"]["passed"]
        and stored["scientific_classification"]
        == REGISTERED_INPUTS["q007y"]["classification"]
    )
    return {
        "stored_cycle_reproduced_exactly": replayed == stored,
        "validity_gate_count": len(stored["validity_gates"]),
        "all_validity_gates_pass": _all_gates_pass(stored, "validity_gates"),
        "hypothesis_gate_count": len(hypotheses),
        "failed_hypothesis_names": failed,
        "old_tube_utilizations": old_values,
        "probe_digest_sha256": stored["probe_registration"]["probe_digest_sha256"],
        "probe_digest_matches": (
            stored["probe_registration"]["probe_digest_sha256"]
            == REGISTERED_Q007Y_PROBE_DIGEST
        ),
        "finite_result_digest_sha256": campaign["result_digest_sha256"],
        "finite_result_digest_matches": (
            campaign["result_digest_sha256"] == REGISTERED_Q007Y_FINITE_RESULT_DIGEST
        ),
        "finite_summary": campaign["summary"],
        "input_audit_passed": stored["input_audit"]["passed"],
        "passed": passed,
    }


def _q007x_exact(exact: dict[str, Any]) -> dict[str, Any]:
    candidate = exact["stored_p85_candidate"]
    return {
        "state_radius": exact["state_radius"],
        "base_margin": exact["base_margin"],
        "normal_margin": exact["normal_margin"],
        "base_error": _fraction_from_record(candidate["base_coordinate_error_upper"]),
        "normal_error": _fraction_from_record(candidate["normal_coordinate_error_upper"]),
        "stage_error_bounds": {
            name: _fraction_from_record(stage["maximum_component_error"])
            for name, stage in candidate["stage_bounds"].items()
        },
        "stage_population_lowers": {
            name: _fraction_from_record(stage["population_lower"])
            for name, stage in candidate["stage_bounds"].items()
        },
        "rounded_constants": candidate["rounded_constants"],
        "registered_operation_counts": candidate["operation_counts"],
    }


def _new_tube_repair_bound(exact: dict[str, Any]) -> dict[str, Any]:
    fresh, fresh_exact = q007w._evaluate_precision(
        PRECISION_BITS,
        exact["state_radius"],
        exact["selected_analysis"],
        exact["external_analysis"],
        exact["base_margin"],
        exact["normal_margin"],
    )
    stored = exact["stored_p85_candidate"]
    input_bound = q007y._tube_stage_repair_bound("input_encoding", fresh_exact["inputs"])
    postfilter_bound = q007y._tube_stage_repair_bound(
        "post_filter",
        fresh_exact["filtered"],
    )
    raw_wiener = _fraction_from_record(postfilter_bound["mass_defect_upper"])
    repair_wiener = _fraction_from_record(postfilter_bound["repair_l1_upper"])
    repaired_wiener = raw_wiener + repair_wiener
    base_error = exact["selected_analysis"] * repaired_wiener
    normal_error = exact["external_analysis"] * repaired_wiener
    observed_floats = {
        "input_repair_l1_upper": float(
            _fraction_from_record(input_bound["repair_l1_upper"])
        ),
        "input_maximum_site_correction_upper": float(
            _fraction_from_record(input_bound["maximum_site_correction_upper"])
        ),
        "raw_wiener_error_upper": float(raw_wiener),
        "repair_wiener_addition_upper": float(repair_wiener),
        "repaired_wiener_error_upper": float(repaired_wiener),
        "repaired_to_raw_ratio": float(repaired_wiener / raw_wiener),
        "base_coordinate_error_upper": float(base_error),
        "base_margin": float(exact["base_margin"]),
        "base_margin_utilization": float(base_error / exact["base_margin"]),
        "normal_coordinate_error_upper": float(normal_error),
        "normal_margin": float(exact["normal_margin"]),
        "normal_margin_utilization": float(normal_error / exact["normal_margin"]),
    }
    momentum_x = _fraction_from_record(postfilter_bound["momentum_x_defect_upper"])
    momentum_y = _fraction_from_record(postfilter_bound["momentum_y_defect_upper"])
    arithmetic_identities = {
        "raw_matches_fresh_p85_wiener": (
            raw_wiener == _fraction_from_record(fresh["wiener_error_upper"])
        ),
        "repair_is_mass_momentum_plus_two_quanta": (
            repair_wiener
            == raw_wiener + momentum_x + momentum_y + 2 * q007y.REPAIR_QUANTUM
        ),
        "total_is_raw_plus_repair": repaired_wiener == raw_wiener + repair_wiener,
        "base_error_uses_registered_analysis": (
            base_error == exact["selected_analysis"] * repaired_wiener
        ),
        "normal_error_uses_registered_analysis": (
            normal_error == exact["external_analysis"] * repaired_wiener
        ),
    }
    structural_passed = bool(
        fresh == stored
        and exact["probe_radius_count"] == 1
        and input_bound["passed"]
        and postfilter_bound["passed"]
        and observed_floats == REGISTERED_NEW_TUBE_FLOATS
        and all(arithmetic_identities.values())
    )
    return {
        "fresh_p85_candidate_reproduced_exactly": fresh == stored,
        "fresh_p85_candidate_digest_sha256": _canonical_json_sha256(fresh),
        "input_encoding": input_bound,
        "post_filter": postfilter_bound,
        "raw_wiener_error_upper": _fraction_record(raw_wiener),
        "repair_wiener_addition_upper": _fraction_record(repair_wiener),
        "repaired_wiener_error_upper": _fraction_record(repaired_wiener),
        "repair_addition_to_raw_ratio": _fraction_record(repair_wiener / raw_wiener),
        "repaired_to_raw_ratio": _fraction_record(repaired_wiener / raw_wiener),
        "selected_analysis_upper": _fraction_record(exact["selected_analysis"]),
        "external_analysis_upper": _fraction_record(exact["external_analysis"]),
        "base_coordinate_error_upper": _fraction_record(base_error),
        "base_margin": _fraction_record(exact["base_margin"]),
        "base_margin_utilization": _fraction_record(base_error / exact["base_margin"]),
        "base_reentry_budget_passed": base_error < exact["base_margin"],
        "normal_coordinate_error_upper": _fraction_record(normal_error),
        "normal_margin": _fraction_record(exact["normal_margin"]),
        "normal_margin_utilization": _fraction_record(
            normal_error / exact["normal_margin"]
        ),
        "normal_reentry_budget_passed": normal_error < exact["normal_margin"],
        "registered_float_values": REGISTERED_NEW_TUBE_FLOATS,
        "observed_float_values": observed_floats,
        "registered_float_values_match": observed_floats == REGISTERED_NEW_TUBE_FLOATS,
        "arithmetic_identities": arithmetic_identities,
        "all_arithmetic_identities_pass": all(arithmetic_identities.values()),
        "triangle_bound_uses_center_cancellation": False,
        "triangle_bound_uses_spatial_fourier_phase": False,
        "q007z_selected_wave_bound_used": False,
        "repair_map_well_defined_on_registered_component_tube": bool(
            input_bound["passed"] and postfilter_bound["passed"]
        ),
        "passed": structural_passed,
    }


def _finite_campaign_regression(
    old_cycle: dict[str, Any],
    campaign: dict[str, Any],
) -> dict[str, Any]:
    old_campaign = old_cycle["finite_campaign"]
    old_by_name = {record["name"]: record for record in old_campaign["probes"]}
    new_by_name = {record["name"]: record for record in campaign["probes"]}
    names_match = list(new_by_name) == list(old_by_name)
    exact_sections = (
        "input_encoding_error",
        "input_repair",
        "backend_operation_domain",
        "output_repair",
        "conservation",
    )
    exact_sections_match = bool(
        names_match
        and all(
            all(new_by_name[name][key] == old_by_name[name][key] for key in exact_sections)
            for name in old_by_name
        )
    )
    observed_fields = (
        "maximum_observed_component_error",
        "maximum_error_index",
        "minimum_mpfr_population",
        "stage_digest_sha256",
    )
    raw_stages_match = bool(
        names_match
        and all(
            all(
                all(
                    new_by_name[name]["raw_stage_comparisons"][stage][field]
                    == old_by_name[name]["raw_stage_comparisons"][stage][field]
                    for field in observed_fields
                )
                for stage in old_by_name[name]["raw_stage_comparisons"]
            )
            for name in old_by_name
        )
    )
    repaired_outputs_match = bool(
        names_match
        and all(
            all(
                new_by_name[name]["repaired_output_comparison"][field]
                == old_by_name[name]["repaired_output_comparison"][field]
                for field in observed_fields
            )
            for name in old_by_name
        )
    )
    distribution_digests_match = bool(
        names_match
        and all(
            new_by_name[name][stage]["distribution_digest_sha256"]
            == old_by_name[name][stage]["distribution_digest_sha256"]
            for name in old_by_name
            for stage in ("input_repair", "output_repair")
        )
    )
    summary_matches = campaign["summary"] == EXPECTED_FINITE_SUMMARY
    passed = bool(
        names_match
        and exact_sections_match
        and raw_stages_match
        and repaired_outputs_match
        and distribution_digests_match
        and summary_matches
    )
    return {
        "probe_names_match": names_match,
        "exact_repair_operation_and_conservation_sections_match": exact_sections_match,
        "raw_observed_stage_records_match": raw_stages_match,
        "repaired_output_observed_records_match": repaired_outputs_match,
        "distribution_digests_match": distribution_digests_match,
        "summary": campaign["summary"],
        "registered_summary": EXPECTED_FINITE_SUMMARY,
        "summary_matches": summary_matches,
        "passed": passed,
    }


def run_propagated_tube_distributed_repair_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    q007al_section, exact = _q007al_reproduction(directory, payloads["q007al"])
    q007y_section = _q007y_reproduction(directory, payloads["q007y"])
    q007x_exact = _q007x_exact(exact)

    source_audit = q007y.q007x._source_audit(q007x_exact)
    context_audit = q007y.q007x._context_audit()
    probe_audit, probes = q007y.q007x._probe_registration_audit(
        q007x_exact["state_radius"]
    )
    repair_bound = _new_tube_repair_bound(exact)
    finite_campaign = q007y._finite_campaign(probes, q007x_exact)
    finite_regression = _finite_campaign_regression(
        payloads["q007y"]["cycle"],
        finite_campaign,
    )

    repository = Path(__file__).resolve().parents[1]
    source_sha = {
        "backend": source_audit["files"]["backend"]["sha256"],
        "pyproject": source_audit["files"]["pyproject"]["sha256"],
        "d2q9": source_audit["files"]["d2q9"]["sha256"],
        "filter": source_audit["files"]["filter"]["sha256"],
        "repair": _file_sha256(Path(q007y.__file__).resolve()),
    }
    source_registration = {
        "registered_sha256": REGISTERED_SOURCE_SHA256,
        "observed_sha256": source_sha,
        "sha256_match": source_sha == REGISTERED_SOURCE_SHA256,
        "repair_source_path": str(Path(q007y.__file__).resolve().relative_to(repository)),
        "passed": bool(source_audit["passed"] and source_sha == REGISTERED_SOURCE_SHA256),
    }

    registered_parameters = {
        "size": SIZE,
        "wave_count": WAVE_COUNT,
        "precision_bits": PRECISION_BITS,
        "repair_quantum": _fraction_record(q007y.REPAIR_QUANTUM),
        "diagonal_populations": list(q007y.DIAGONAL_POPULATIONS),
        "diagonal_binade": {
            "lower": _fraction_record(q007y.DIAGONAL_BIN_LOWER),
            "upper": _fraction_record(q007y.DIAGONAL_BIN_UPPER),
        },
        "target_conserved": q007y._conserved_record(q007y.TARGET_CONSERVED),
        "solver_objective": [
            "sum_abs_diagonal_units",
            "max_abs_diagonal_units",
            "abs_free_unit",
            "free_unit",
        ],
        "distribution": "Python divmod over 289 row-major sites",
        "probe_names": list(q007y.q007x.PROBE_NAMES),
        "selected_wave_certificate_used": False,
    }
    input_digest_sha256 = _canonical_json_sha256(
        {
            "registered_parameters": registered_parameters,
            "input_artifacts": input_records,
            "registered_q007al_digests": REGISTERED_Q007AL_DIGESTS,
            "registered_q007y_probe_digest": REGISTERED_Q007Y_PROBE_DIGEST,
            "registered_q007y_finite_result_digest": (
                REGISTERED_Q007Y_FINITE_RESULT_DIGEST
            ),
            "registered_source_sha256": REGISTERED_SOURCE_SHA256,
            "registered_new_tube_floats": REGISTERED_NEW_TUBE_FLOATS,
        }
    )
    result_digest_sha256 = _canonical_json_sha256(
        {
            "q007al_reproduction": q007al_section,
            "q007y_reproduction": q007y_section,
            "source_registration": source_registration,
            "context_audit": context_audit,
            "probe_registration": probe_audit,
            "tube_wide_repair_bound": repair_bound,
            "finite_campaign": finite_campaign,
            "finite_campaign_regression": finite_regression,
        }
    )
    digest_records = {
        "input_digest_sha256": input_digest_sha256,
        "probe_digest_sha256": probe_audit["probe_digest_sha256"],
        "finite_result_digest_sha256": finite_campaign["result_digest_sha256"],
        "result_digest_sha256": result_digest_sha256,
    }
    serializable_sections = {
        "input_artifacts": input_records,
        "q007al_reproduction": q007al_section,
        "q007y_reproduction": q007y_section,
        "source_registration": source_registration,
        "context_audit": context_audit,
        "probe_registration": probe_audit,
        "tube_wide_repair_bound": repair_bound,
        "finite_campaign": finite_campaign,
        "finite_campaign_regression": finite_regression,
        **digest_records,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    all_digests_present = all(
        isinstance(value, str) and len(value) == 64 for value in digest_records.values()
    )

    source_context_probe_passed = bool(
        source_registration["passed"]
        and context_audit["passed"]
        and probe_audit["passed"]
        and probe_audit["probe_digest_sha256"] == REGISTERED_Q007Y_PROBE_DIGEST
    )
    repair_integer_lattice_passed = bool(
        repair_bound["input_encoding"]["passed"]
        and repair_bound["post_filter"]["passed"]
        and all(
            probe[stage]["solver_and_distribution_passed"]
            for probe in finite_campaign["probes"]
            for stage in ("input_repair", "output_repair")
        )
    )
    repair_operations_passed = finite_campaign["summary"][
        "all_repairs_solve_and_add_exactly"
    ]
    backend_stage_passed = bool(
        finite_campaign["summary"]["all_backend_operation_domains_pass"]
        and finite_campaign["summary"][
            "all_finite_stage_bounds_and_positivity_pass"
        ]
    )
    conservation_passed = bool(
        finite_campaign["summary"]["all_input_repairs_conserve"]
        and finite_campaign["summary"]["all_exact_maps_preserve_leaf"]
        and finite_campaign["summary"]["all_output_repairs_conserve"]
        and finite_campaign["summary"]["all_streaming_steps_conserve"]
    )
    validity_gates = {
        "sealed_inputs_source_scope_and_outcomes": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": (
                "Q007al/Q007y artifact and runner SHA, source, scope, schema, "
                "classifications, validity, and registered outcomes match"
            ),
            "value": {
                "passing_input_count": sum(
                    record["passed"] for record in input_records.values()
                ),
                "expected_input_count": len(input_records),
            },
        },
        "q007al_mpfr85_bridge_exactly_reproduced": {
            "passed": q007al_section["passed"],
            "threshold": (
                "stored cycle, six digests, all 8+5 gates, p=85 candidate, "
                "trace/context/source, and conservation diagnosis reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007al_section[
                    "stored_cycle_reproduced_exactly"
                ],
                "digests_match": q007al_section["digests_match"],
                "conservation_nonclosure": q007al_section[
                    "registered_conservation_nonclosure_reproduced"
                ],
            },
        },
        "q007y_old_repair_result_exactly_reproduced": {
            "passed": q007y_section["passed"],
            "threshold": (
                "stored cycle, all 8 validity gates, 5-pass/2-fail hypotheses, "
                "old bounds, solver/distribution, probe and finite digests reproduce"
            ),
            "value": {
                "stored_cycle_reproduced_exactly": q007y_section[
                    "stored_cycle_reproduced_exactly"
                ],
                "failed_hypotheses": q007y_section["failed_hypothesis_names"],
                "probe_digest_matches": q007y_section["probe_digest_matches"],
                "finite_result_digest_matches": q007y_section[
                    "finite_result_digest_matches"
                ],
            },
        },
        "registered_sources_context_and_probes": {
            "passed": source_context_probe_passed,
            "threshold": (
                "backend/repair/pyproject/D2Q9/filter SHA, MPFR context, and "
                "all four registered new-box probes match"
            ),
            "value": {
                "sources": source_registration["passed"],
                "context": context_audit["passed"],
                "probes": probe_audit["passed"],
            },
        },
        "new_tube_exact_repair_bound": {
            "passed": repair_bound["passed"],
            "threshold": (
                "fresh p=85 candidate, registered floats, binade/lattice/"
                "parity, and E_total=E_raw+E_rep identities reproduce exactly"
            ),
            "value": {
                "fresh_candidate": repair_bound[
                    "fresh_p85_candidate_reproduced_exactly"
                ],
                "registered_floats": repair_bound["registered_float_values_match"],
                "arithmetic_identities": repair_bound[
                    "all_arithmetic_identities_pass"
                ],
            },
        },
        "finite_integer_solver_distribution_and_operations": {
            "passed": bool(
                repair_integer_lattice_passed
                and repair_operations_passed
                and finite_regression["passed"]
            ),
            "threshold": (
                "all four probes pass the integer solver, balanced distribution, "
                "exact repair operations, operation domain, and old observed-record regression"
            ),
            "value": {
                "integer_lattice": repair_integer_lattice_passed,
                "repair_operations": repair_operations_passed,
                "finite_regression": finite_regression["passed"],
            },
        },
        "finite_conservation_stage_bounds_and_positivity": {
            "passed": bool(
                finite_campaign["passed"]
                and conservation_passed
                and backend_stage_passed
            ),
            "threshold": (
                "all repaired inputs/outputs exactly equal target conserved "
                "quantities and every raw/repaired stage bound and positivity gate passes"
            ),
            "value": {
                "campaign": finite_campaign["passed"],
                "conservation": conservation_passed,
                "stage_bounds_and_domain": backend_stage_passed,
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": bool(finite_strict_json and all_digests_present),
            "threshold": (
                "all records are finite strict JSON and canonical input, "
                "probe, finite-result, and result digests exist"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "all_digests_present": all_digests_present,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    input_conservation = finite_campaign["summary"]["all_input_repairs_conserve"]
    output_conservation = finite_campaign["summary"]["all_output_repairs_conserve"]
    finite_repairs = bool(repair_operations_passed and backend_stage_passed)
    tube_defined = repair_bound["repair_map_well_defined_on_registered_component_tube"]
    normal_passed = repair_bound["normal_reentry_budget_passed"]
    base_passed = repair_bound["base_reentry_budget_passed"]
    hypothesis_gates = {
        "repaired_encoding_restores_fixed_leaf_probes": {
            "passed": bool(validity_passed and input_conservation),
            "threshold": "all four repaired inputs equal target M/Px/Py exactly",
            "value": input_conservation,
        },
        "repaired_postfilter_restores_fixed_leaf_probes": {
            "passed": bool(validity_passed and output_conservation),
            "threshold": (
                "all four repaired post-filter outputs equal target M/Px/Py exactly"
            ),
            "value": output_conservation,
        },
        "finite_repairs_are_exact_positive_and_enclosed": {
            "passed": bool(validity_passed and finite_repairs),
            "threshold": (
                "every finite repair is exact, positive, binade-safe, and "
                "inside the Q007al component bounds"
            ),
            "value": finite_repairs,
        },
        "repair_map_is_defined_on_new_component_tube": {
            "passed": bool(validity_passed and tube_defined),
            "threshold": (
                "lattice, parity, binade, and worst-case site correction prove "
                "the repair is defined throughout the new registered component tube"
            ),
            "value": tube_defined,
        },
        "repair_aware_normal_budget_closes": {
            "passed": bool(validity_passed and normal_passed),
            "threshold": "repair-aware normal error is strictly below the Q007ag margin",
            "value": normal_passed,
        },
        "repair_aware_base_budget_closes": {
            "passed": bool(validity_passed and base_passed),
            "threshold": "repair-aware base error is strictly below the Q007ag margin",
            "value": base_passed,
        },
        "fixed_leaf_closure_and_both_one_step_budgets_coexist": {
            "passed": False,
            "threshold": "all six preceding hypotheses pass simultaneously",
            "value": False,
        },
    }
    first_six_pass = all(
        gate["passed"]
        for name, gate in hypothesis_gates.items()
        if name != "fixed_leaf_closure_and_both_one_step_budgets_coexist"
    )
    combined_passed = bool(validity_passed and first_six_pass)
    hypothesis_gates["fixed_leaf_closure_and_both_one_step_budgets_coexist"][
        "passed"
    ] = combined_passed
    hypothesis_gates["fixed_leaf_closure_and_both_one_step_budgets_coexist"][
        "value"
    ] = combined_passed
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())

    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007am propagated-tube repair audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "distributed MPFR-85 repair restores the Q007ag fixed leaf and "
            "fits both registered one-step budgets"
        )
    elif all(
        hypothesis_gates[name]["passed"]
        for name in (
            "repaired_encoding_restores_fixed_leaf_probes",
            "repaired_postfilter_restores_fixed_leaf_probes",
            "finite_repairs_are_exact_positive_and_enclosed",
            "repair_map_is_defined_on_new_component_tube",
            "repair_aware_normal_budget_closes",
        )
    ) and not hypothesis_gates["repair_aware_base_budget_closes"]["passed"]:
        outcome = "not_certified"
        classification = (
            "distributed MPFR-85 repair restores the Q007ag fixed leaf but "
            "not its base budget"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered distributed MPFR-85 repair does not close the Q007ag "
            "one-step budgets"
        )

    return {
        "question": (
            "Does the unchanged Q007y distributed dyadic repair restore the "
            "MPFR-85 fixed leaf on the propagated Q007ag component tube while "
            "its coarse repair-aware error fits both registered margins?"
        ),
        "registered_parameters": registered_parameters,
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_finite_input_repairs_restore_exact_fixed_leaf": bool(
                hypotheses_passed
            ),
            "registered_finite_output_repairs_restore_exact_fixed_leaf": bool(
                hypotheses_passed
            ),
            "distributed_repair_is_defined_on_q007ag_component_tube": bool(
                hypotheses_passed
            ),
            "repair_aware_base_and_normal_budgets_fit_q007ag_margins": bool(
                hypotheses_passed
            ),
            "q007ag_repaired_mpfr85_tube_self_map_certified": False,
            "all_iterate_repaired_mpfr85_q007ag_invariance_certified": False,
            "same_initial_q007ag_shadowing_certified": False,
        },
        "claim_boundary": (
            "Acceptance covers only the fixed MPFR-85 backend, the unchanged "
            "Q007y distributed diagonal repair, the Q007ag component box, and "
            "the Q007al p=85 paired-error model. It establishes fixed-leaf "
            "repair feasibility and separate one-step base/normal arithmetic "
            "budgets. Finite probes are implementation regressions, not a tube "
            "sampling proof. The coarse bound uses no center cancellation, "
            "spatial Fourier phase, or Q007z selected-wave result. This gate "
            "does not compose the budgets with exact Q007ag invariance into a "
            "tube self-map theorem, all-iterate induction, exact-state "
            "initialization interior, or same-initial shadowing. Other targets, "
            "repair lattices, distributions, parallel reductions, MPFR builds, "
            "GPU/compiler behavior, performance, grid uniformity, and a "
            "continuum limit are not certified."
        ),
        "preserved_prior_outcomes": {
            "q007y_old_tube_mixed_result_changed": False,
            "q007z_old_tube_selected_wave_acceptance_changed": False,
            "q007al_mpfr85_bridge_acceptance_changed": False,
            "q007ag_exact_tube_acceptance_changed": False,
            "q007ai_exact_stagewise_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007af_external_disc_obstruction_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister Q007an to compose exact Q007ag tube "
            "invariance, stage positivity, and the Q007am repair-aware budgets "
            "into an all-iterate theorem for already-repaired MPFR-85 states; "
            "keep initialization and same-initial shadowing separate."
        ),
    }


def run_q007am_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_propagated_tube_distributed_repair_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": {
            **runtime_metadata(),
            **q007y.backend.backend_runtime_metadata(),
        },
        "mathematical_scope": {
            "diagnostic": (
                "propagated-tube distributed dyadic fixed-leaf repair and "
                "one-step repair-aware budget audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(q007y.backend.EXACT_OMEGA),
            "eta": float(q007y.backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "input and post-stage repair"
            ),
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "base_modal_l1_radius": 9e-17,
            "normal_coordinate_radius": 5e-11,
            "repair_lattice": "four diagonal populations on h=2^-90",
            "rounding_model": (
                "sealed Q007x gmpy2 2.3.1 / MPFR 4.2.2 nearest-even backend"
            ),
            "claim": (
                "fixed-leaf repair feasibility and separate coarse one-step "
                "base/normal budgets, excluding tube self-map induction"
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
    result = run_q007am_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
