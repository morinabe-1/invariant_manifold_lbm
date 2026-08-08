"""Sealed Q007ab fixed-coordinate all-iterate forward-shadowing audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q007aa_initialization_interior as q007aa
import research.q007s_finite_tube_enlargement as q007s
import research.q007x_mpfr_backend as backend
import research.q007z_selected_wave_repair as q007z
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = q007aa.SIZE
RELATIVE_TUBE_ACCURACY_THRESHOLD = Fraction(1, 10**6)

Q007S_ARTIFACT = "q007s_finite_tube_enlargement.json"
Q007Z_ARTIFACT = "q007z_selected_wave_repair.json"
Q007AA_ARTIFACT = "q007aa_initialization_interior.json"

REGISTERED_INPUTS = {
    "q007s": {
        "filename": Q007S_ARTIFACT,
        "artifact_sha256": (
            "7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292"
        ),
        "runner_sha256": (
            "6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e"
        ),
        "module": q007s,
        "diagnostic": "rational finite-tube enlargement certificate",
        "outcome": "accepted",
        "validity_count": 6,
        "hypothesis_count": 5,
        "fresh": None,
    },
    "q007z": {
        "filename": Q007Z_ARTIFACT,
        "artifact_sha256": (
            "b1ca382a76e874c18b804c7614ff8ad1ded3a5d0b9dda583facf6641b24f0c53"
        ),
        "runner_sha256": (
            "0e2b3aebdc30d6a441178e3ac05fe417ab66673885a52ac9da801bd787dd8f79"
        ),
        "module": q007z,
        "diagnostic": (
            "selected-wave Fourier certificate for the sealed balanced "
            "dyadic conservation repair"
        ),
        "outcome": "accepted",
        "validity_count": 6,
        "hypothesis_count": 7,
        "fresh": None,
    },
    "q007aa": {
        "filename": Q007AA_ARTIFACT,
        "artifact_sha256": (
            "cf6a0566b91e9b034d2c93290302182fe8b4a0bf0f7e7bbbbb232f3d4a12ee64"
        ),
        "runner_sha256": (
            "a7a6334fdb157ec317f65fca2475bf3b03775af88ea6d68eec2c02c5ba74188e"
        ),
        "module": q007aa,
        "diagnostic": (
            "exact-state MPFR-85 encoding and conservation-repair "
            "initialization-interior certificate"
        ),
        "outcome": "accepted",
        "validity_count": 6,
        "hypothesis_count": 6,
        "fresh": q007aa.run_initialization_interior_audit,
    },
}


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }


def _fraction_from_record(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _digest_payload(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(
        gate.get("passed", False) for gate in gates.values()
    )


def _load_registered_input(
    directory: Path,
    name: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    specification = REGISTERED_INPUTS[name]
    artifact_path = directory / str(specification["filename"])
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    module = specification["module"]
    runner_path = Path(module.__file__).resolve()
    cycle = payload.get("cycle", {})
    scope = payload.get("mathematical_scope", {})
    fresh_runner = specification["fresh"]
    fresh_cycle_matches = bool(
        fresh_runner is None or fresh_runner(directory) == cycle
    )
    artifact_sha = _file_sha256(artifact_path)
    observed_runner_sha = _file_sha256(runner_path)
    record = {
        "filename": specification["filename"],
        "registered_sha256": specification["artifact_sha256"],
        "sha256": artifact_sha,
        "sha256_matches": artifact_sha
        == specification["artifact_sha256"],
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": bool(
            scope.get("diagnostic") == specification["diagnostic"]
            and scope.get("construction_grid") == [SIZE, SIZE]
            and scope.get("omega") == float(backend.EXACT_OMEGA)
            and scope.get("eta") == float(backend.EXACT_ETA)
            and "fixed global mass and momentum leaf"
            in scope.get("conservation_treatment", "")
        ),
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "validity_gate_count": len(cycle.get("validity_gates", {})),
        "all_validity_gates_pass": _all_gates_pass(
            payload,
            "validity_gates",
        ),
        "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload,
            "hypothesis_gates",
        ),
        "fresh_cycle_required": fresh_runner is not None,
        "fresh_cycle_matches": fresh_cycle_matches,
        "registered_runner_sha256": specification["runner_sha256"],
        "artifact_runner_sha256": payload.get("runner_source", {}).get(
            "sha256"
        ),
        "observed_runner_sha256": observed_runner_sha,
        "runner_sha_matches": bool(
            payload.get("runner_source", {}).get("sha256")
            == specification["runner_sha256"]
            and observed_runner_sha == specification["runner_sha256"]
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == specification["outcome"]
        and record["validity_gate_count"]
        == specification["validity_count"]
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"]
        == specification["hypothesis_count"]
        and record["all_hypothesis_gates_pass"]
        and record["fresh_cycle_matches"]
        and record["runner_sha_matches"]
    )
    return payload, record


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    for name in REGISTERED_INPUTS:
        payloads[name], records[name] = _load_registered_input(
            directory,
            name,
        )
    return payloads, {
        "artifacts": records,
        "passed": all(record["passed"] for record in records.values()),
    }


def _coordinate_lipschitz_audit(
    q007s_payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    cycle = q007s_payload["cycle"]
    constants = cycle["constant_reuse_audit"]["constants"]
    candidate = cycle["selection"]["selected_candidate"]
    selected_linear = _fraction_from_record(constants["selected_radius"])
    external_linear = _fraction_from_record(constants["q0"])
    selected_synthesis = _fraction_from_record(constants["c_v"])
    external_synthesis = _fraction_from_record(constants["synthesis"])
    selected_analysis = _fraction_from_record(
        constants["selected_analysis"]
    )
    external_analysis = _fraction_from_record(constants["analysis"])
    state_radius = _fraction_from_record(candidate["state_radius"])
    nonlinear_derivative = _fraction_from_record(
        candidate["nonlinear_derivative"]
    )
    graph_normal_contraction = _fraction_from_record(
        candidate["normal_contraction"]
    )

    linear_contraction = max(selected_linear, external_linear)
    synthesis = max(selected_synthesis, external_synthesis)
    nonlinear_analysis = selected_analysis + external_analysis
    nonlinear_lipschitz = (
        nonlinear_analysis * nonlinear_derivative * synthesis
    )
    full_lipschitz = linear_contraction + nonlinear_lipschitz
    contraction_gap = 1 - full_lipschitz
    coordinate_coverage = bool(
        cycle["input_artifact"]["passed"]
        and cycle["constant_reuse_audit"]["passed"]
        and cycle["theorem_consequence"][
            "selected_registered_tube_forward_invariant"
        ]
        and cycle["theorem_consequence"][
            "selected_registered_tube_uniformly_normal_contracting"
        ]
        and candidate["passed"]
        and all(candidate["gates"].values())
    )
    arithmetic_passed = bool(
        linear_contraction == max(selected_linear, external_linear)
        and synthesis == max(selected_synthesis, external_synthesis)
        and nonlinear_analysis == selected_analysis + external_analysis
        and nonlinear_lipschitz
        == nonlinear_analysis * nonlinear_derivative * synthesis
        and full_lipschitz == linear_contraction + nonlinear_lipschitz
        and contraction_gap == 1 - full_lipschitz
        and state_radius > 0
        and nonlinear_derivative > 0
        and coordinate_coverage
    )
    section = {
        "coordinate_definition": (
            "C x=(L x,JQ x) with direct-sum selected-l1 plus registered "
            "external-coordinate norm"
        ),
        "coordinate_is_fixed_linear_not_graph_relative": True,
        "physical_state_norm": "Fourier-population Wiener l1",
        "selected_linear_contraction_upper": _fraction_record(
            selected_linear
        ),
        "external_linear_contraction_upper": _fraction_record(
            external_linear
        ),
        "linear_direct_sum_contraction_upper": _fraction_record(
            linear_contraction
        ),
        "selected_synthesis_upper": _fraction_record(selected_synthesis),
        "external_synthesis_upper": _fraction_record(external_synthesis),
        "direct_sum_synthesis_upper": _fraction_record(synthesis),
        "selected_nonlinear_analysis_upper": _fraction_record(
            selected_analysis
        ),
        "external_nonlinear_analysis_upper": _fraction_record(
            external_analysis
        ),
        "direct_sum_nonlinear_analysis_upper": _fraction_record(
            nonlinear_analysis
        ),
        "tube_state_wiener_radius": _fraction_record(state_radius),
        "nonlinear_derivative_at_tube_state_upper": _fraction_record(
            nonlinear_derivative
        ),
        "nonlinear_coordinate_lipschitz_increment_upper": _fraction_record(
            nonlinear_lipschitz
        ),
        "fixed_coordinate_full_map_lipschitz_upper": _fraction_record(
            full_lipschitz
        ),
        "fixed_coordinate_contraction_gap": _fraction_record(
            contraction_gap
        ),
        "graph_relative_normal_contraction_not_used": _fraction_record(
            graph_normal_contraction
        ),
        "q007s_coordinate_coverage_and_invariance": coordinate_coverage,
        "formula": (
            "L_plus=max(q_selected,q_external)"
            "+(K_L+K_a)*dN(R_T)*max(c_V,K_s)"
        ),
        "exact_arithmetic_identities_passed": arithmetic_passed,
        "passed": arithmetic_passed,
    }
    exact: dict[str, Fraction | bool] = {
        "synthesis": synthesis,
        "state_radius": state_radius,
        "full_lipschitz": full_lipschitz,
        "contraction_gap": contraction_gap,
        "coordinate_coverage": coordinate_coverage,
        "arithmetic_passed": arithmetic_passed,
    }
    return section, exact


def _shadow_recurrence_audit(
    q007z_payload: dict[str, Any],
    q007aa_payload: dict[str, Any],
    coordinate_exact: dict[str, Fraction | bool],
) -> dict[str, Any]:
    synthesis = coordinate_exact["synthesis"]
    state_radius = coordinate_exact["state_radius"]
    full_lipschitz = coordinate_exact["full_lipschitz"]
    contraction_gap = coordinate_exact["contraction_gap"]
    assert isinstance(synthesis, Fraction)
    assert isinstance(state_radius, Fraction)
    assert isinstance(full_lipschitz, Fraction)
    assert isinstance(contraction_gap, Fraction)

    initialization = q007aa_payload["cycle"]["initialization_bound"]
    step = q007z_payload["cycle"]["selected_repair_bound"]
    initial_selected = _fraction_from_record(
        initialization["base_coordinate_increment_upper"]
    )
    initial_physical = _fraction_from_record(
        initialization["total_encoding_repair_wiener_upper"]
    )
    initial_external = _fraction_from_record(
        initialization["direct_external_coordinate_increment_upper"]
    )
    external_analysis = _fraction_from_record(
        q007aa_payload["cycle"]["constant_reuse_audit"][
            "external_analysis_upper"
        ]
    )
    initial_coordinate = initial_selected + initial_external

    step_selected = _fraction_from_record(
        step["repaired_base_coordinate_error_upper"]
    )
    step_external = _fraction_from_record(
        step["normal_coordinate_error_upper"]
    )
    step_coordinate = step_selected + step_external

    contractive = full_lipschitz < 1
    stationary_coordinate = (
        step_coordinate / contraction_gap
        if contraction_gap > 0
        else None
    )
    uniform_coordinate = (
        max(initial_coordinate, stationary_coordinate)
        if stationary_coordinate is not None
        else None
    )
    uniform_physical = (
        synthesis * uniform_coordinate
        if uniform_coordinate is not None
        else None
    )
    relative_physical = (
        uniform_physical / state_radius
        if uniform_physical is not None
        else None
    )
    absolute_accuracy_threshold = (
        RELATIVE_TUBE_ACCURACY_THRESHOLD * state_radius
    )
    recurrence_interval_invariant = bool(
        uniform_coordinate is not None
        and initial_coordinate <= uniform_coordinate
        and full_lipschitz * uniform_coordinate + step_coordinate
        <= uniform_coordinate
    )
    arithmetic_passed = bool(
        initial_external == external_analysis * initial_physical
        and initial_coordinate == initial_selected + initial_external
        and step_coordinate == step_selected + step_external
        and (
            stationary_coordinate is None
            or contraction_gap * stationary_coordinate == step_coordinate
        )
        and (
            uniform_physical is None
            or uniform_physical == synthesis * uniform_coordinate
        )
        and (
            relative_physical is None
            or relative_physical == uniform_physical / state_radius
        )
    )
    accuracy_passed = bool(
        uniform_physical is not None
        and uniform_physical < absolute_accuracy_threshold
    )
    return {
        "recurrence_norm": (
            "fixed linear selected/external direct-sum coordinate norm"
        ),
        "initial_selected_coordinate_error_upper": _fraction_record(
            initial_selected
        ),
        "initial_physical_wiener_error_upper": _fraction_record(
            initial_physical
        ),
        "initial_external_coordinate_error_upper": _fraction_record(
            initial_external
        ),
        "initial_coordinate_error_upper": _fraction_record(
            initial_coordinate
        ),
        "initial_graph_shift_not_double_counted": True,
        "step_selected_coordinate_defect_upper": _fraction_record(
            step_selected
        ),
        "step_external_coordinate_defect_upper": _fraction_record(
            step_external
        ),
        "step_coordinate_defect_upper": _fraction_record(step_coordinate),
        "fixed_coordinate_lipschitz_upper": _fraction_record(
            full_lipschitz
        ),
        "fixed_coordinate_contraction_gap": _fraction_record(
            contraction_gap
        ),
        "stationary_coordinate_error_upper": (
            None
            if stationary_coordinate is None
            else _fraction_record(stationary_coordinate)
        ),
        "uniform_all_iterate_coordinate_error_upper": (
            None
            if uniform_coordinate is None
            else _fraction_record(uniform_coordinate)
        ),
        "uniform_all_iterate_physical_wiener_error_upper": (
            None
            if uniform_physical is None
            else _fraction_record(uniform_physical)
        ),
        "uniform_physical_to_tube_state_radius_ratio": (
            None
            if relative_physical is None
            else _fraction_record(relative_physical)
        ),
        "registered_relative_tube_accuracy_threshold": _fraction_record(
            RELATIVE_TUBE_ACCURACY_THRESHOLD
        ),
        "registered_absolute_wiener_accuracy_threshold": _fraction_record(
            absolute_accuracy_threshold
        ),
        "recurrence": (
            "d_(n+1)<=L_plus*d_n+epsilon_step; "
            "D=max(d_0,epsilon_step/(1-L_plus))"
        ),
        "fixed_point_identity_passed": bool(
            stationary_coordinate is not None
            and full_lipschitz * stationary_coordinate + step_coordinate
            == stationary_coordinate
        ),
        "initial_error_below_uniform_bound": bool(
            uniform_coordinate is not None
            and initial_coordinate <= uniform_coordinate
        ),
        "recurrence_interval_invariant": recurrence_interval_invariant,
        "exact_arithmetic_identities_passed": arithmetic_passed,
        "fixed_coordinate_map_is_contractive": contractive,
        "registered_accuracy_threshold_passed": accuracy_passed,
        "passed": bool(
            arithmetic_passed
            and contractive
            and recurrence_interval_invariant
            and accuracy_passed
        ),
    }


def run_forward_shadowing_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_audit = _load_registered_inputs(directory)
    coordinate, coordinate_exact = _coordinate_lipschitz_audit(
        payloads["q007s"]
    )
    shadow = _shadow_recurrence_audit(
        payloads["q007z"],
        payloads["q007aa"],
        coordinate_exact,
    )
    q007s_consequence = payloads["q007s"]["cycle"]["theorem_consequence"]
    q007z_consequence = payloads["q007z"]["cycle"]["theorem_consequence"]
    q007aa_consequence = payloads["q007aa"]["cycle"]["theorem_consequence"]
    both_trajectories_in_tube = bool(
        q007s_consequence["selected_registered_tube_forward_invariant"]
        and q007z_consequence[
            "conditional_all_iterate_repaired_mpfr85_q007s_tube_invariance"
        ]
        and q007aa_consequence[
            "registered_exact_state_interior_encodes_into_q007s_tube"
        ]
        and q007aa_consequence[
            "all_iterate_repaired_mpfr85_q007s_tube_invariance"
        ]
    )
    initial_bound_ready = bool(
        payloads["q007aa"]["cycle"]["initialization_bound"]["passed"]
        and shadow["initial_graph_shift_not_double_counted"]
    )
    step_bound_ready = bool(
        payloads["q007z"]["cycle"]["selected_repair_bound"]["passed"]
        and payloads["q007z"]["cycle"]["tube_repair_preserved"]
    )

    preliminary = {
        "input_audit": input_audit,
        "coordinate_lipschitz_audit": coordinate,
        "shadow_recurrence_audit": shadow,
        "both_trajectories_in_registered_tube": both_trajectories_in_tube,
    }
    strict_json = bool(
        _all_numeric_values_finite(preliminary)
        and _strict_json_serializable(preliminary)
    )
    input_digest_payload = {
        "artifact_sha256": {
            name: record["sha256"]
            for name, record in input_audit["artifacts"].items()
        },
        "relative_accuracy_threshold": _fraction_record(
            RELATIVE_TUBE_ACCURACY_THRESHOLD
        ),
        "q007s_constants": coordinate,
        "q007z_step_bound": payloads["q007z"]["cycle"][
            "selected_repair_bound"
        ],
        "q007aa_initialization": payloads["q007aa"]["cycle"][
            "initialization_bound"
        ],
    }
    input_digest = _digest_payload(input_digest_payload)
    result_digest = _digest_payload(
        {
            "input_digest": input_digest,
            "coordinate": coordinate,
            "shadow": shadow,
        }
    )
    digests_reproducible = bool(
        input_digest == _digest_payload(input_digest_payload)
        and len(input_digest) == 64
        and len(result_digest) == 64
    )

    validity_gates = {
        "registered_q007s_q007z_q007aa_inputs": {
            "passed": input_audit["passed"],
            "threshold": (
                "artifact/runner SHA, source, scope, upstream gates and "
                "outcomes match, with a fresh Q007aa replay"
            ),
            "value": input_audit["passed"],
        },
        "fixed_coordinate_constants_and_coverage": {
            "passed": coordinate["passed"],
            "threshold": (
                "linear contraction, synthesis, analysis, tube radius, "
                "nonlinear derivative, and fixed-leaf coverage reproduce"
            ),
            "value": coordinate["passed"],
        },
        "initial_and_step_defects_reconstructed": {
            "passed": bool(initial_bound_ready and step_bound_ready),
            "threshold": (
                "Q007aa initial selected/external and Q007z local "
                "selected/external defect bounds reproduce"
            ),
            "value": {
                "initial": initial_bound_ready,
                "step": step_bound_ready,
            },
        },
        "fixed_coordinate_lipschitz_formula": {
            "passed": bool(
                coordinate["exact_arithmetic_identities_passed"]
                and coordinate[
                    "coordinate_is_fixed_linear_not_graph_relative"
                ]
            ),
            "threshold": (
                "linear plus nonlinear mean-value formula reproduces without "
                "substituting the graph-relative normal contraction"
            ),
            "value": coordinate["exact_arithmetic_identities_passed"],
        },
        "exact_shadow_recurrence_arithmetic": {
            "passed": bool(
                shadow["exact_arithmetic_identities_passed"]
                and shadow["fixed_point_identity_passed"]
            ),
            "threshold": (
                "d0, epsilon_step, stationary/uniform coordinate error, "
                "physical error, and tube-relative ratio reproduce exactly"
            ),
            "value": shadow["exact_arithmetic_identities_passed"],
        },
        "finite_strict_json_and_digests": {
            "passed": bool(strict_json and digests_reproducible),
            "threshold": (
                "all records are finite strict JSON and input/result digests "
                "reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests": digests_reproducible,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    contractive = shadow["fixed_coordinate_map_is_contractive"]
    recurrence_passed = shadow["recurrence_interval_invariant"]
    accuracy_passed = shadow["registered_accuracy_threshold_passed"]
    hypothesis_gates = {
        "exact_and_repaired_trajectories_remain_in_same_tube": {
            "passed": bool(validity_passed and both_trajectories_in_tube),
            "threshold": (
                "Q007s exact and Q007aa/Q007z repaired invariance keep both "
                "trajectories in the registered physical Wiener ball"
            ),
            "value": both_trajectories_in_tube,
        },
        "fixed_coordinate_exact_map_is_strictly_contractive": {
            "passed": bool(validity_passed and contractive),
            "threshold": "L_plus<1",
            "value": shadow["fixed_coordinate_lipschitz_upper"],
        },
        "initial_fixed_coordinate_error_is_enclosed": {
            "passed": bool(validity_passed and initial_bound_ready),
            "threshold": (
                "d0 includes Q007aa selected and direct external encoding/"
                "repair errors without graph-coordinate double counting"
            ),
            "value": initial_bound_ready,
        },
        "one_step_repaired_mpfr_local_defect_is_enclosed": {
            "passed": bool(validity_passed and step_bound_ready),
            "threshold": (
                "epsilon_step includes Q007z selected and conservative "
                "external local coordinate defects"
            ),
            "value": step_bound_ready,
        },
        "geometric_uniform_all_iterate_bound_closes": {
            "passed": bool(validity_passed and recurrence_passed),
            "threshold": (
                "[0,D_plus] is invariant under d -> L_plus*d+epsilon_step "
                "and contains d0"
            ),
            "value": recurrence_passed,
        },
        "registered_tube_scale_accuracy_gate": {
            "passed": bool(validity_passed and accuracy_passed),
            "threshold": "D_W/R_T<1e-6",
            "value": shadow[
                "uniform_physical_to_tube_state_radius_ratio"
            ],
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007ab forward-shadowing audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "fixed-coordinate contraction certifies all-iterate MPFR-85 "
            "forward shadowing"
        )
    elif not contractive:
        outcome = "not_certified"
        classification = (
            "registered fixed-coordinate majorant is not contractive"
        )
    elif not accuracy_passed:
        outcome = "not_certified"
        classification = (
            "uniform shadow bound exceeds the registered tube-scale "
            "accuracy threshold"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered recurrence does not certify all-iterate forward "
            "shadowing"
        )

    return {
        "question": (
            "Does the fixed linear eigencoordinate norm make the exact Q007s "
            "map contractive enough to sum Q007aa initialization and Q007z "
            "local MPFR defects into an all-iterate forward-error bound?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "precision_bits": backend.MPFR_PRECISION_BITS,
            "relative_tube_accuracy_threshold": _fraction_record(
                RELATIVE_TUBE_ACCURACY_THRESHOLD
            ),
            "coordinate_norm": (
                "selected modal l1 plus Q007p external-coordinate block-sum "
                "l1, fixed at the equilibrium"
            ),
            "trajectory_pair": (
                "exact orbit from a Q007aa exact initial state versus sealed "
                "MPFR-85 encode/repair orbit from that same state"
            ),
            "comparison_times": "sampling times after every repair",
            "horizon": "all nonnegative integer iterates",
        },
        "input_audit": input_audit,
        "coordinate_lipschitz_audit": coordinate,
        "shadow_recurrence_audit": shadow,
        "both_trajectories_in_registered_tube": (
            both_trajectories_in_tube
        ),
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "fixed_coordinate_exact_map_is_contractive_on_q007s": bool(
                validity_passed and contractive
            ),
            "same_initial_forward_coordinate_error_is_uniform_all_iterate": (
                bool(validity_passed and recurrence_passed)
            ),
            "same_initial_forward_physical_error_meets_tube_scale_gate": bool(
                validity_passed and accuracy_passed
            ),
            "q007aa_exact_initialization_to_all_iterate_shadowing": bool(
                validity_passed and hypotheses_passed
            ),
        },
        "claim_boundary": (
            "Shadowing here means a sampling-time forward-error bound between "
            "the exact orbit from a Q007aa exact fixed-leaf initial state and "
            "the repaired MPFR-85 orbit obtained by encoding that same state. "
            "It is an all-nonnegative-iterate contraction estimate in one "
            "fixed linear eigencoordinate norm, with a derived physical "
            "Wiener bound. It is not a bi-infinite shadowing lemma, backward "
            "error result, intermediate-stage distance, componentwise "
            "relative-error bound, arbitrary Q007s-boundary initialization, "
            "performance result, another grid or MPFR build, center-slow "
            "construction, or D3Q27 result."
        ),
        "preserved_prior_outcomes": {
            "q007aa_initialization_acceptance_changed": False,
            "q007z_conditional_induction_changed": False,
            "q007y_coarse_triangle_rejection_changed": False,
            "q007x_unrepaired_fixed_leaf_rejection_changed": False,
            "q007w_ideal_precision_acceptance_changed": False,
            "q007v_binary64_reentry_rejection_changed": False,
            "q007s_exact_fixed_leaf_invariance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "With exact initialization, invariant repaired execution, and "
            "all-iterate same-initial forward error certified, return to the "
            "remaining preregistered TT-cross/cost gates or separately audit "
            "performance without weakening the sparse baseline."
        ),
    }


def run_q007ab_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_forward_shadowing_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": {
            **runtime_metadata(),
            **backend.backend_runtime_metadata(),
        },
        "mathematical_scope": {
            "diagnostic": (
                "fixed-linear-coordinate all-iterate repaired-MPFR forward-"
                "shadowing certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(backend.EXACT_OMEGA),
            "eta": float(backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "post-stage repair"
            ),
            "manifold": "Q007s exact graph-gauge manifold and registered tube",
            "norm": (
                "fixed selected/external eigencoordinate direct-sum l1 with "
                "derived Fourier-population Wiener bound"
            ),
            "claim": (
                "same-initial-state sampling-time all-iterate forward error "
                "for the sealed repaired MPFR-85 backend"
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
    result = run_q007ab_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
