"""Sealed Q007ap propagated-tube same-initial forward-shadowing audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007ab_forward_shadowing as q007ab
import research.q007ag_tube_radius_propagation as q007ag
import research.q007am_propagated_tube_distributed_repair as q007am
import research.q007ao_initialization_interior as q007ao
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
RELATIVE_TUBE_ACCURACY_THRESHOLD = Fraction(1, 10**6)

REGISTERED_INPUTS = {
    "q007ab": {
        "filename": "q007ab_forward_shadowing.json",
        "module": q007ab,
        "artifact_sha256": (
            "3770e53e5fd169ea8ba16a568a1a1a3052afdd95d2779ba630c7ba7113bdc7ae"
        ),
        "runner_sha256": (
            "4958e1aa5140bdbd1a32ce074c77ce2739636a34f7da2531c792ec165401c01a"
        ),
        "classification": (
            "fixed-coordinate contraction certifies all-iterate MPFR-85 "
            "forward shadowing"
        ),
        "diagnostic": (
            "fixed-linear-coordinate all-iterate repaired-MPFR forward-"
            "shadowing certificate"
        ),
        "conservation": (
            "fixed global mass and momentum leaf with exact diagonal "
            "post-stage repair"
        ),
        "manifold": (
            "Q007s exact graph-gauge manifold and registered tube"
        ),
        "validity_count": 6,
        "hypothesis_count": 6,
        "digests": {
            "input_digest_sha256": (
                "83c98750b8a18aa98cae710fad0a4d2fa139428d791a085bdd086e39e435225f"
            ),
            "result_digest_sha256": (
                "268a5e2098011561c3bc521c845e6eb804692713502fbbd54c3b3106b8f9c014"
            ),
        },
    },
    "q007ag": {
        "filename": "q007ag_tube_radius_propagation.json",
        "module": q007ag,
        "artifact_sha256": (
            "5783df74abb4b6ec7d658fd7e3dd272cf100cd134783c31863d643fcd17d4200"
        ),
        "runner_sha256": (
            "bafd9a56d2d2ceb94acb709609bd710c9fff0f6c0bf543202fa411b9456fb6e0"
        ),
        "classification": (
            "Q007ae analytic radius enlarges the registered "
            "external-coordinate tube"
        ),
        "diagnostic": (
            "analytic-radius-propagated rational finite-tube enlargement "
            "certificate"
        ),
        "conservation": "fixed global mass and momentum leaf",
        "manifold": "Q007ae exact graph-gauge manifold",
        "validity_count": 6,
        "hypothesis_count": 5,
        "digests": {
            "input_digest_sha256": (
                "262cbeccacf858bd798de06f363635f15c78ff3d361b44bdd5850aeb90679613"
            ),
            "candidate_digest_sha256": (
                "a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408"
            ),
            "result_digest_sha256": (
                "6f52c6f1cfa618ca881439504f1bd5b46e45eb245670f1a2c6341669aa024f43"
            ),
        },
    },
    "q007am": {
        "filename": "q007am_propagated_tube_distributed_repair.json",
        "module": q007am,
        "artifact_sha256": (
            "3b1b6f3c839cec572d0279f41c158dfafa09088e5f8ee1c3eab84f5bd279b781"
        ),
        "runner_sha256": (
            "a0bdebc150c4c3ad055e1840b98196dee95bf967c417d17097f7a35579f2aa16"
        ),
        "classification": (
            "distributed MPFR-85 repair restores the Q007ag fixed leaf "
            "and fits both registered one-step budgets"
        ),
        "diagnostic": (
            "propagated-tube distributed dyadic fixed-leaf repair and "
            "one-step repair-aware budget audit"
        ),
        "conservation": (
            "fixed global mass and momentum leaf with exact diagonal input "
            "and post-stage repair"
        ),
        "manifold": "Q007ae exact graph-gauge manifold",
        "validity_count": 8,
        "hypothesis_count": 7,
        "digests": {
            "input_digest_sha256": (
                "f1a0dfd0b90cf354e9847cb076058fd241ab813a90bdee0bfdbafa9dfee17de5"
            ),
            "probe_digest_sha256": (
                "a7c4581ce3ac19b2de47f87a79e0eda8177bb7f6124b79254bf3c230ece5c329"
            ),
            "finite_result_digest_sha256": (
                "905b65f13ee01711f3b083a0bd93e44b32d0fc5201007fad77e99de03063ab6d"
            ),
            "result_digest_sha256": (
                "2217172b48bf86b987a316c9b8c14db6aaeceb3e50f304fa7fefb021c2fd5bd2"
            ),
        },
    },
    "q007ao": {
        "filename": "q007ao_initialization_interior.json",
        "module": q007ao,
        "artifact_sha256": (
            "c6262043848a479b90634fc8aa82dbd02bfcaea4bcb3467d240b956fd7602b8f"
        ),
        "runner_sha256": (
            "2cd4c852c2855b93efaeb618bc3b1cb488885375c69f11e2c7624f0ea84614f7"
        ),
        "classification": (
            "registered propagated-tube exact-state interior survives "
            "MPFR-85 encoding and repair"
        ),
        "diagnostic": (
            "propagated-tube exact-state MPFR-85 encoding and "
            "conservation-repair initialization-interior certificate"
        ),
        "conservation": (
            "fixed global mass and momentum leaf with exact diagonal "
            "input repair"
        ),
        "manifold": "Q007ae exact graph-gauge manifold",
        "validity_count": 7,
        "hypothesis_count": 6,
        "digests": {
            "input_digest_sha256": (
                "4793702239a7bc6252b71b5fff43cc68e78dcad1d1b9446db94544b85270deb3"
            ),
            "bound_digest_sha256": (
                "b747e0a635cf4d747728fd5447e613b62a0b951813634f8a98c9e80a17f3308a"
            ),
            "result_digest_sha256": (
                "6c2a41f2ff2d610d8f542cb132a50a678298098245063d54bcd2a38b6e6a8360"
            ),
        },
    },
}

REGISTERED_FLOATS = {
    "selected_linear_contraction_upper": 0.9920954673554099,
    "external_linear_contraction_upper": 0.981709835832552,
    "linear_direct_sum_contraction_upper": 0.9920954673554099,
    "selected_synthesis_upper": 2.7869014191713024,
    "external_synthesis_upper": 2.888267212368763,
    "direct_sum_synthesis_upper": 2.888267212368763,
    "selected_analysis_upper": 1.5106842091904618,
    "external_analysis_upper": 29.917136268364473,
    "direct_sum_analysis_upper": 31.427820477554935,
    "tube_state_wiener_radius": 1.4441361143956586e-10,
    "nonlinear_state_derivative_upper": 3.032685840887825e-9,
    "nonlinear_coordinate_lipschitz_increment_upper": (
        2.7528278762500916e-7
    ),
    "fixed_coordinate_full_map_lipschitz_upper": 0.9920957426381974,
    "fixed_coordinate_contraction_gap": 0.007904257361802534,
    "graph_relative_normal_contraction_not_used": 0.9817100978829438,
    "initial_selected_coordinate_error_upper": 3.009718329710275e-23,
    "initial_physical_wiener_error_upper": 1.9922882038484456e-23,
    "initial_external_coordinate_error_upper": 5.960355768038905e-22,
    "initial_coordinate_error_upper": 6.261327601009932e-22,
    "step_selected_coordinate_defect_upper": 1.1581233824834727e-21,
    "step_external_coordinate_defect_upper": 2.2935127565743277e-20,
    "step_coordinate_defect_upper": 2.4093250948226748e-20,
    "stationary_coordinate_error_upper": 3.0481359405954845e-18,
    "uniform_all_iterate_coordinate_error_upper": (
        3.0481359405954845e-18
    ),
    "uniform_all_iterate_physical_wiener_error_upper": (
        8.803831096064757e-18
    ),
    "uniform_physical_to_tube_state_radius_ratio": (
        6.096261293035372e-8
    ),
    "registered_absolute_wiener_accuracy_threshold": (
        1.4441361143956587e-16
    ),
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
    return bool(gates) and all(
        gate.get("passed", False) for gate in gates.values()
    )


def _scope_matches(name: str, payload: dict[str, Any]) -> bool:
    scope = payload.get("mathematical_scope", {})
    registered = REGISTERED_INPUTS[name]
    common = bool(
        scope.get("diagnostic") == registered["diagnostic"]
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega")) == 1.5
        and float(scope.get("eta")) == 0.01
        and scope.get("conservation_treatment")
        == registered["conservation"]
        and scope.get("manifold") == registered["manifold"]
    )
    if name == "q007ab":
        return bool(
            common
            and scope.get("norm")
            == (
                "fixed selected/external eigencoordinate direct-sum l1 "
                "with derived Fourier-population Wiener bound"
            )
        )
    if name == "q007ag":
        return bool(
            common
            and scope.get("norm")
            == "Q007p Fourier external-coordinate block-sum l1"
        )
    if name == "q007am":
        return bool(
            common
            and scope.get("norm")
            == "Q007p Fourier external-coordinate block-sum l1"
            and float(scope.get("base_modal_l1_radius")) == 9e-17
            and float(scope.get("normal_coordinate_radius")) == 5e-11
            and scope.get("repair_lattice")
            == "four diagonal populations on h=2^-90"
        )
    return bool(
        common
        and scope.get("norm")
        == "Q007p Fourier external-coordinate block-sum l1"
        and float(scope.get("outer_base_modal_l1_radius")) == 9e-17
        and float(scope.get("outer_normal_coordinate_radius")) == 5e-11
        and scope.get("repair_lattice")
        == "four diagonal populations on h=2^-90"
    )


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    for name, registered in REGISTERED_INPUTS.items():
        artifact_path = directory / str(registered["filename"])
        runner_path = Path(registered["module"].__file__).resolve()
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        payloads[name] = payload
        cycle = payload.get("cycle", {})
        observed_digests = {
            key: cycle.get(key) for key in registered["digests"]
        }
        artifact_sha = _file_sha256(artifact_path)
        runner_sha = _file_sha256(runner_path)
        record = {
            "filename": registered["filename"],
            "registered_artifact_sha256": registered["artifact_sha256"],
            "artifact_sha256": artifact_sha,
            "artifact_sha256_matches": (
                artifact_sha == registered["artifact_sha256"]
            ),
            "runner_filename": runner_path.name,
            "registered_runner_sha256": registered["runner_sha256"],
            "runner_sha256": runner_sha,
            "runner_sha256_matches": runner_sha
            == registered["runner_sha256"],
            "artifact_runner_sha256": payload.get(
                "runner_source", {}
            ).get("sha256"),
            "artifact_runner_sha256_matches": (
                payload.get("runner_source", {}).get("sha256")
                == registered["runner_sha256"]
            ),
            "schema_version_matches": payload.get("schema_version") == 1,
            "source_matches": payload.get("source") == source_metadata(),
            "scope_matches": _scope_matches(name, payload),
            "study_gate_matches": payload.get("study_gate") == "passed",
            "scientific_outcome_matches": (
                payload.get("scientific_outcome") == "accepted"
            ),
            "classification_matches": (
                cycle.get("scientific_classification")
                == registered["classification"]
            ),
            "validity_gate_count": len(cycle.get("validity_gates", {})),
            "registered_validity_gate_count": registered["validity_count"],
            "all_validity_gates_pass": _all_gates_pass(
                cycle, "validity_gates"
            ),
            "hypothesis_gate_count": len(
                cycle.get("hypothesis_gates", {})
            ),
            "registered_hypothesis_gate_count": (
                registered["hypothesis_count"]
            ),
            "all_hypothesis_gates_pass": _all_gates_pass(
                cycle, "hypothesis_gates"
            ),
            "registered_digests": registered["digests"],
            "observed_digests": observed_digests,
            "digests_match": observed_digests == registered["digests"],
        }
        record["passed"] = bool(
            record["artifact_sha256_matches"]
            and record["runner_sha256_matches"]
            and record["artifact_runner_sha256_matches"]
            and record["schema_version_matches"]
            and record["source_matches"]
            and record["scope_matches"]
            and record["study_gate_matches"]
            and record["scientific_outcome_matches"]
            and record["classification_matches"]
            and record["validity_gate_count"]
            == record["registered_validity_gate_count"]
            and record["all_validity_gates_pass"]
            and record["hypothesis_gate_count"]
            == record["registered_hypothesis_gate_count"]
            and record["all_hypothesis_gates_pass"]
            and record["digests_match"]
        )
        records[name] = record
    return payloads, records


def _fresh_reproductions(
    directory: Path,
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    fresh_ab = q007ab.run_forward_shadowing_audit(directory)
    fresh_ao = q007ao.run_initialization_interior_audit(directory)
    stored_ab = payloads["q007ab"]["cycle"]
    stored_ao = payloads["q007ao"]["cycle"]
    ab_passed = bool(
        fresh_ab == stored_ab
        and _all_gates_pass(fresh_ab, "validity_gates")
        and _all_gates_pass(fresh_ab, "hypothesis_gates")
        and fresh_ab["hypothesis_outcome"] == "accepted"
    )
    ao_nested = fresh_ao["fresh_q007an_reproduction"]
    ao_passed = bool(
        fresh_ao == stored_ao
        and _all_gates_pass(fresh_ao, "validity_gates")
        and _all_gates_pass(fresh_ao, "hypothesis_gates")
        and fresh_ao["hypothesis_outcome"] == "accepted"
        and ao_nested["passed"]
    )
    return {
        "q007ab": {
            "stored_cycle_reproduced_exactly": fresh_ab == stored_ab,
            "validity_gate_count": len(fresh_ab["validity_gates"]),
            "all_validity_gates_pass": _all_gates_pass(
                fresh_ab, "validity_gates"
            ),
            "hypothesis_gate_count": len(
                fresh_ab["hypothesis_gates"]
            ),
            "all_hypothesis_gates_pass": _all_gates_pass(
                fresh_ab, "hypothesis_gates"
            ),
            "input_digest_sha256": fresh_ab["input_digest_sha256"],
            "result_digest_sha256": fresh_ab["result_digest_sha256"],
            "passed": ab_passed,
        },
        "q007ao": {
            "stored_cycle_reproduced_exactly": fresh_ao == stored_ao,
            "validity_gate_count": len(fresh_ao["validity_gates"]),
            "all_validity_gates_pass": _all_gates_pass(
                fresh_ao, "validity_gates"
            ),
            "hypothesis_gate_count": len(
                fresh_ao["hypothesis_gates"]
            ),
            "all_hypothesis_gates_pass": _all_gates_pass(
                fresh_ao, "hypothesis_gates"
            ),
            "q007an_transitive_reproduction_pass": ao_nested["passed"],
            "q007an_nested_cycle_names": ao_nested[
                "nested_cycle_names"
            ],
            "input_digest_sha256": fresh_ao["input_digest_sha256"],
            "bound_digest_sha256": fresh_ao["bound_digest_sha256"],
            "result_digest_sha256": fresh_ao["result_digest_sha256"],
            "passed": ao_passed,
        },
        "passed": bool(ab_passed and ao_passed),
    }


def _scope_alignment(
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ab = payloads["q007ab"]["cycle"]
    ag = payloads["q007ag"]["cycle"]
    am = payloads["q007am"]["cycle"]
    ao = payloads["q007ao"]["cycle"]
    candidate = ag["selection"]["selected_candidate"]
    coordinate = ab["coordinate_lipschitz_audit"]
    exact_consequence = ag["theorem_consequence"]
    repaired_consequence = ao["theorem_consequence"]
    am_consequence = am["theorem_consequence"]
    coordinate_definition = bool(
        coordinate["coordinate_is_fixed_linear_not_graph_relative"]
        and coordinate["coordinate_definition"]
        == (
            "C x=(L x,JQ x) with direct-sum selected-l1 plus registered "
            "external-coordinate norm"
        )
    )
    constants_unchanged = bool(
        ag["constant_update_audit"]["only_rho_and_tau_changed"]
        and ag["constant_update_audit"]["changed_constant_names"]
        == ["rho", "tau"]
        and coordinate["exact_arithmetic_identities_passed"]
    )
    exact_trajectory_ready = bool(
        exact_consequence["selected_registered_tube_forward_invariant"]
        and candidate["passed"]
        and all(candidate["gates"].values())
    )
    repaired_trajectory_ready = bool(
        repaired_consequence[
            "initial_encoding_and_repair_enter_q007ag_tube"
        ]
        and repaired_consequence[
            "all_iterate_repaired_mpfr85_q007ag_tube_invariance_from_inner_set"
        ]
        and am_consequence[
            "distributed_repair_is_defined_on_q007ag_component_tube"
        ]
    )
    inner = ao["registered_parameters"]
    target = inner["target_conserved"]
    target_ready = bool(
        _fraction_from_record(target["mass"]) == WAVE_COUNT
        and _fraction_from_record(target["momentum_x"]) == 0
        and _fraction_from_record(target["momentum_y"]) == 0
    )
    radii_ready = bool(
        _fraction_from_record(inner["outer_base_radius"])
        == Fraction(9, 10**17)
        and _fraction_from_record(inner["outer_normal_radius"])
        == Fraction(5, 10**11)
        and _fraction_from_record(inner["initial_base_radius"])
        == q007ao.INITIAL_BASE_RADIUS
        and _fraction_from_record(inner["initial_normal_radius"])
        == q007ao.INITIAL_NORMAL_RADIUS
    )
    passed = bool(
        coordinate_definition
        and constants_unchanged
        and exact_trajectory_ready
        and repaired_trajectory_ready
        and target_ready
        and radii_ready
    )
    return {
        "coordinate_definition": coordinate["coordinate_definition"],
        "coordinate_is_fixed_linear_not_graph_relative": coordinate[
            "coordinate_is_fixed_linear_not_graph_relative"
        ],
        "comparison_times": "sampling times after every repair",
        "trajectory_pair": (
            "exact orbit and repaired MPFR-85 orbit initialized from the "
            "same Q007ao exact state"
        ),
        "only_rho_and_tau_changed_from_q007ab_constant_family": (
            constants_unchanged
        ),
        "exact_q007ag_trajectory_stays_in_tube": exact_trajectory_ready,
        "repaired_q007ao_trajectory_stays_in_tube": (
            repaired_trajectory_ready
        ),
        "fixed_leaf_target_alignment": target_ready,
        "outer_and_initial_radius_alignment": radii_ready,
        "passed": passed,
    }


def _coordinate_lipschitz_audit(
    payloads: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    old = payloads["q007ab"]["cycle"]["coordinate_lipschitz_audit"]
    candidate = payloads["q007ag"]["cycle"]["selection"][
        "selected_candidate"
    ]
    selected_linear = _fraction_from_record(
        old["selected_linear_contraction_upper"]
    )
    external_linear = _fraction_from_record(
        old["external_linear_contraction_upper"]
    )
    selected_synthesis = _fraction_from_record(
        old["selected_synthesis_upper"]
    )
    external_synthesis = _fraction_from_record(
        old["external_synthesis_upper"]
    )
    selected_analysis = _fraction_from_record(
        old["selected_nonlinear_analysis_upper"]
    )
    external_analysis = _fraction_from_record(
        old["external_nonlinear_analysis_upper"]
    )
    state_radius = _fraction_from_record(candidate["state_radius"])
    nonlinear_derivative = _fraction_from_record(
        candidate["nonlinear_derivative"]
    )
    graph_normal = _fraction_from_record(
        candidate["normal_contraction"]
    )
    linear = max(selected_linear, external_linear)
    synthesis = max(selected_synthesis, external_synthesis)
    analysis = selected_analysis + external_analysis
    nonlinear_lipschitz = analysis * nonlinear_derivative * synthesis
    full_lipschitz = linear + nonlinear_lipschitz
    gap = 1 - full_lipschitz
    observed_floats = {
        "selected_linear_contraction_upper": float(selected_linear),
        "external_linear_contraction_upper": float(external_linear),
        "linear_direct_sum_contraction_upper": float(linear),
        "selected_synthesis_upper": float(selected_synthesis),
        "external_synthesis_upper": float(external_synthesis),
        "direct_sum_synthesis_upper": float(synthesis),
        "selected_analysis_upper": float(selected_analysis),
        "external_analysis_upper": float(external_analysis),
        "direct_sum_analysis_upper": float(analysis),
        "tube_state_wiener_radius": float(state_radius),
        "nonlinear_state_derivative_upper": float(
            nonlinear_derivative
        ),
        "nonlinear_coordinate_lipschitz_increment_upper": float(
            nonlinear_lipschitz
        ),
        "fixed_coordinate_full_map_lipschitz_upper": float(
            full_lipschitz
        ),
        "fixed_coordinate_contraction_gap": float(gap),
        "graph_relative_normal_contraction_not_used": float(
            graph_normal
        ),
    }
    registered_floats = {
        key: REGISTERED_FLOATS[key] for key in observed_floats
    }
    arithmetic = {
        "linear_is_maximum_of_selected_and_external": (
            linear == max(selected_linear, external_linear)
        ),
        "synthesis_is_maximum_of_selected_and_external": (
            synthesis == max(selected_synthesis, external_synthesis)
        ),
        "analysis_is_sum_of_selected_and_external": (
            analysis == selected_analysis + external_analysis
        ),
        "nonlinear_increment_uses_new_tube_derivative": (
            nonlinear_lipschitz
            == analysis * nonlinear_derivative * synthesis
        ),
        "full_lipschitz_is_linear_plus_nonlinear": (
            full_lipschitz == linear + nonlinear_lipschitz
        ),
        "gap_is_one_minus_full_lipschitz": (
            gap == 1 - full_lipschitz
        ),
    }
    passed = bool(
        old["passed"]
        and all(arithmetic.values())
        and observed_floats == registered_floats
        and state_radius > 0
        and nonlinear_derivative > 0
    )
    exact: dict[str, Fraction | bool] = {
        "synthesis": synthesis,
        "external_analysis": external_analysis,
        "state_radius": state_radius,
        "full_lipschitz": full_lipschitz,
        "contraction_gap": gap,
        "passed": passed,
    }
    return {
        "coordinate_definition": old["coordinate_definition"],
        "coordinate_is_fixed_linear_not_graph_relative": True,
        "physical_state_norm": old["physical_state_norm"],
        "selected_linear_contraction_upper": _fraction_record(
            selected_linear
        ),
        "external_linear_contraction_upper": _fraction_record(
            external_linear
        ),
        "linear_direct_sum_contraction_upper": _fraction_record(linear),
        "selected_synthesis_upper": _fraction_record(
            selected_synthesis
        ),
        "external_synthesis_upper": _fraction_record(
            external_synthesis
        ),
        "direct_sum_synthesis_upper": _fraction_record(synthesis),
        "selected_nonlinear_analysis_upper": _fraction_record(
            selected_analysis
        ),
        "external_nonlinear_analysis_upper": _fraction_record(
            external_analysis
        ),
        "direct_sum_nonlinear_analysis_upper": _fraction_record(
            analysis
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
        "fixed_coordinate_contraction_gap": _fraction_record(gap),
        "graph_relative_normal_contraction_not_used": _fraction_record(
            graph_normal
        ),
        "old_q007ab_coordinate_formula_reproduced": old[
            "exact_arithmetic_identities_passed"
        ],
        "only_q007ag_state_radius_and_nonlinear_derivative_substituted": True,
        "formula": (
            "L_plus=max(q_selected,q_external)"
            "+(K_L+K_a)*dN(R_T)*max(c_V,K_s)"
        ),
        "arithmetic_identities": arithmetic,
        "all_arithmetic_identities_pass": all(arithmetic.values()),
        "registered_float_values": registered_floats,
        "observed_float_values": observed_floats,
        "registered_float_values_match": (
            observed_floats == registered_floats
        ),
        "passed": passed,
    }, exact


def _defect_audit(
    payloads: dict[str, dict[str, Any]],
    coordinate_exact: dict[str, Fraction | bool],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    initialization = payloads["q007ao"]["cycle"]["initialization_bound"]
    step = payloads["q007am"]["cycle"]["tube_wide_repair_bound"]
    external_analysis = coordinate_exact["external_analysis"]
    assert isinstance(external_analysis, Fraction)
    initial_selected = _fraction_from_record(
        initialization["base_coordinate_increment_upper"]
    )
    initial_physical = _fraction_from_record(
        initialization["total_encoding_repair_wiener_upper"]
    )
    initial_external = _fraction_from_record(
        initialization["direct_external_coordinate_increment_upper"]
    )
    initial_coordinate = initial_selected + initial_external
    graph_shift = _fraction_from_record(
        initialization[
            "graph_shift_external_coordinate_increment_upper"
        ]
    )
    step_selected = _fraction_from_record(
        step["base_coordinate_error_upper"]
    )
    step_external = _fraction_from_record(
        step["normal_coordinate_error_upper"]
    )
    step_coordinate = step_selected + step_external
    observed_floats = {
        "initial_selected_coordinate_error_upper": float(
            initial_selected
        ),
        "initial_physical_wiener_error_upper": float(initial_physical),
        "initial_external_coordinate_error_upper": float(
            initial_external
        ),
        "initial_coordinate_error_upper": float(initial_coordinate),
        "step_selected_coordinate_defect_upper": float(step_selected),
        "step_external_coordinate_defect_upper": float(step_external),
        "step_coordinate_defect_upper": float(step_coordinate),
    }
    registered_floats = {
        key: REGISTERED_FLOATS[key] for key in observed_floats
    }
    arithmetic = {
        "initial_external_is_analysis_times_physical": (
            initial_external == external_analysis * initial_physical
        ),
        "initial_coordinate_is_selected_plus_external": (
            initial_coordinate == initial_selected + initial_external
        ),
        "step_coordinate_is_selected_plus_external": (
            step_coordinate == step_selected + step_external
        ),
        "graph_shift_is_positive_membership_term": graph_shift > 0,
    }
    initial_ready = bool(
        initialization["passed"]
        and payloads["q007ao"]["cycle"]["theorem_consequence"][
            "initial_encoding_and_repair_enter_q007ag_tube"
        ]
    )
    step_ready = bool(
        step["passed"]
        and step["base_reentry_budget_passed"]
        and step["normal_reentry_budget_passed"]
        and payloads["q007am"]["cycle"]["theorem_consequence"][
            "repair_aware_base_and_normal_budgets_fit_q007ag_margins"
        ]
    )
    passed = bool(
        initial_ready
        and step_ready
        and all(arithmetic.values())
        and observed_floats == registered_floats
    )
    exact: dict[str, Fraction | bool] = {
        "initial_coordinate": initial_coordinate,
        "step_coordinate": step_coordinate,
        "initial_ready": initial_ready,
        "step_ready": step_ready,
        "passed": passed,
    }
    return {
        "coordinate_norm": (
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
        "initial_graph_shift_membership_upper_not_added": _fraction_record(
            graph_shift
        ),
        "initial_graph_shift_not_double_counted": True,
        "step_selected_coordinate_defect_upper": _fraction_record(
            step_selected
        ),
        "step_external_coordinate_defect_upper": _fraction_record(
            step_external
        ),
        "step_coordinate_defect_upper": _fraction_record(
            step_coordinate
        ),
        "q007ao_initial_bound_ready": initial_ready,
        "q007am_step_bound_ready": step_ready,
        "arithmetic_identities": arithmetic,
        "all_arithmetic_identities_pass": all(arithmetic.values()),
        "registered_float_values": registered_floats,
        "observed_float_values": observed_floats,
        "registered_float_values_match": (
            observed_floats == registered_floats
        ),
        "passed": passed,
    }, exact


def _recurrence_audit(
    coordinate_exact: dict[str, Fraction | bool],
    defect_exact: dict[str, Fraction | bool],
) -> dict[str, Any]:
    synthesis = coordinate_exact["synthesis"]
    state_radius = coordinate_exact["state_radius"]
    full_lipschitz = coordinate_exact["full_lipschitz"]
    gap = coordinate_exact["contraction_gap"]
    initial_coordinate = defect_exact["initial_coordinate"]
    step_coordinate = defect_exact["step_coordinate"]
    assert all(
        isinstance(value, Fraction)
        for value in (
            synthesis,
            state_radius,
            full_lipschitz,
            gap,
            initial_coordinate,
            step_coordinate,
        )
    )
    stationary = step_coordinate / gap if gap > 0 else None
    uniform = (
        max(initial_coordinate, stationary)
        if stationary is not None
        else None
    )
    physical = synthesis * uniform if uniform is not None else None
    ratio = (
        physical / state_radius if physical is not None else None
    )
    absolute_threshold = (
        RELATIVE_TUBE_ACCURACY_THRESHOLD * state_radius
    )
    recurrence_invariant = bool(
        uniform is not None
        and initial_coordinate <= uniform
        and full_lipschitz * uniform + step_coordinate <= uniform
    )
    fixed_point = bool(
        stationary is not None
        and full_lipschitz * stationary + step_coordinate
        == stationary
    )
    accuracy = bool(
        physical is not None and physical < absolute_threshold
    )
    observed_floats = {
        "stationary_coordinate_error_upper": (
            None if stationary is None else float(stationary)
        ),
        "uniform_all_iterate_coordinate_error_upper": (
            None if uniform is None else float(uniform)
        ),
        "uniform_all_iterate_physical_wiener_error_upper": (
            None if physical is None else float(physical)
        ),
        "uniform_physical_to_tube_state_radius_ratio": (
            None if ratio is None else float(ratio)
        ),
        "registered_absolute_wiener_accuracy_threshold": float(
            absolute_threshold
        ),
    }
    registered_floats = {
        key: REGISTERED_FLOATS[key] for key in observed_floats
    }
    arithmetic = {
        "stationary_is_step_over_contraction_gap": bool(
            stationary is not None and gap * stationary == step_coordinate
        ),
        "uniform_is_maximum_of_initial_and_stationary": bool(
            uniform is not None
            and stationary is not None
            and uniform == max(initial_coordinate, stationary)
        ),
        "physical_is_synthesis_times_coordinate": bool(
            physical is not None and physical == synthesis * uniform
        ),
        "relative_is_physical_over_state_radius": bool(
            ratio is not None and ratio == physical / state_radius
        ),
        "absolute_threshold_is_relative_times_state_radius": (
            absolute_threshold
            == RELATIVE_TUBE_ACCURACY_THRESHOLD * state_radius
        ),
    }
    passed = bool(
        all(arithmetic.values())
        and observed_floats == registered_floats
        and full_lipschitz < 1
        and fixed_point
        and recurrence_invariant
        and accuracy
    )
    return {
        "recurrence_norm": (
            "fixed linear selected/external direct-sum coordinate norm"
        ),
        "initial_coordinate_error_upper": _fraction_record(
            initial_coordinate
        ),
        "step_coordinate_defect_upper": _fraction_record(step_coordinate),
        "fixed_coordinate_lipschitz_upper": _fraction_record(
            full_lipschitz
        ),
        "fixed_coordinate_contraction_gap": _fraction_record(gap),
        "stationary_coordinate_error_upper": (
            None if stationary is None else _fraction_record(stationary)
        ),
        "uniform_all_iterate_coordinate_error_upper": (
            None if uniform is None else _fraction_record(uniform)
        ),
        "direct_sum_synthesis_upper": _fraction_record(synthesis),
        "uniform_all_iterate_physical_wiener_error_upper": (
            None if physical is None else _fraction_record(physical)
        ),
        "tube_state_wiener_radius": _fraction_record(state_radius),
        "uniform_physical_to_tube_state_radius_ratio": (
            None if ratio is None else _fraction_record(ratio)
        ),
        "registered_relative_tube_accuracy_threshold": _fraction_record(
            RELATIVE_TUBE_ACCURACY_THRESHOLD
        ),
        "registered_absolute_wiener_accuracy_threshold": _fraction_record(
            absolute_threshold
        ),
        "recurrence": (
            "d_(n+1)<=L_plus*d_n+epsilon_step; "
            "D=max(d_0,epsilon_step/(1-L_plus))"
        ),
        "fixed_coordinate_map_is_contractive": full_lipschitz < 1,
        "fixed_point_identity_passed": fixed_point,
        "initial_error_below_uniform_bound": bool(
            uniform is not None and initial_coordinate <= uniform
        ),
        "recurrence_interval_invariant": recurrence_invariant,
        "registered_accuracy_threshold_passed": accuracy,
        "arithmetic_identities": arithmetic,
        "all_arithmetic_identities_pass": all(arithmetic.values()),
        "registered_float_values": registered_floats,
        "observed_float_values": observed_floats,
        "registered_float_values_match": (
            observed_floats == registered_floats
        ),
        "passed": passed,
    }


def run_forward_shadowing_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    reproductions = _fresh_reproductions(directory, payloads)
    alignment = _scope_alignment(payloads)
    coordinate, coordinate_exact = _coordinate_lipschitz_audit(payloads)
    defects, defect_exact = _defect_audit(payloads, coordinate_exact)
    recurrence = _recurrence_audit(coordinate_exact, defect_exact)

    registered_parameters = {
        "size": SIZE,
        "wave_count": WAVE_COUNT,
        "precision_bits": PRECISION_BITS,
        "relative_tube_accuracy_threshold": _fraction_record(
            RELATIVE_TUBE_ACCURACY_THRESHOLD
        ),
        "coordinate_norm": (
            "selected modal l1 plus Q007p external-coordinate block-sum "
            "l1, fixed at the equilibrium"
        ),
        "trajectory_pair": (
            "exact orbit from a Q007ao exact initial state versus sealed "
            "MPFR-85 encode/repair orbit from that same state"
        ),
        "comparison_times": "sampling times after every repair",
        "horizon": "all nonnegative integer iterates",
    }
    input_digest = _canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "registered_parameters": registered_parameters,
        }
    )
    recurrence_sections = {
        "fresh_reproductions": reproductions,
        "scope_alignment": alignment,
        "coordinate_lipschitz_audit": coordinate,
        "defect_audit": defects,
        "shadow_recurrence_audit": recurrence,
    }
    recurrence_digest = _canonical_json_sha256(recurrence_sections)
    strict_json = bool(
        _all_numeric_values_finite(recurrence_sections)
        and _strict_json_serializable(recurrence_sections)
    )
    digests_reproduce = bool(
        input_digest
        == _canonical_json_sha256(
            {
                "input_artifacts": input_records,
                "registered_parameters": registered_parameters,
            }
        )
        and recurrence_digest
        == _canonical_json_sha256(recurrence_sections)
    )
    input_passed = all(
        record["passed"] for record in input_records.values()
    )
    validity_gates = {
        "sealed_inputs_sources_scopes_outcomes_gates_and_digests": {
            "passed": input_passed,
            "threshold": (
                "Q007ab/Q007ag/Q007am/Q007ao artifact and runner SHA "
                "values, source/scope, accepted outcomes, gate counts, and "
                "digests match"
            ),
            "value": input_passed,
        },
        "fresh_q007ab_q007ao_and_transitive_reproductions": {
            "passed": reproductions["passed"],
            "threshold": (
                "Q007ab and Q007ao replay exactly and Q007ao's transitive "
                "Q007an/upstream reproduction passes"
            ),
            "value": reproductions["passed"],
        },
        "fixed_coordinate_tube_backend_trajectory_alignment": {
            "passed": alignment["passed"],
            "threshold": (
                "fixed coordinate definition, constant family, fixed leaf, "
                "tube, backend, repair, and trajectory times align"
            ),
            "value": alignment["passed"],
        },
        "new_tube_fixed_coordinate_lipschitz_formula": {
            "passed": coordinate["passed"],
            "threshold": (
                "Q007ab invariant constants plus Q007ag state radius and "
                "nonlinear derivative reproduce the registered fixed-"
                "coordinate Lipschitz bound"
            ),
            "value": coordinate["passed"],
        },
        "initial_and_local_fixed_coordinate_defects": {
            "passed": defects["passed"],
            "threshold": (
                "Q007ao initial and Q007am one-step defects reproduce "
                "without graph-shift double counting"
            ),
            "value": defects["passed"],
        },
        "exact_geometric_recurrence_arithmetic": {
            "passed": recurrence["passed"],
            "threshold": (
                "stationary/uniform coordinate error, physical synthesis, "
                "tube ratio, and fixed-point identity reproduce exactly"
            ),
            "value": recurrence["passed"],
        },
        "finite_strict_json_and_digests": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": (
                "all records are finite strict JSON and input/recurrence "
                "digests reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproducible": digests_reproduce,
            },
        },
    }
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )
    both_in_tube = bool(
        alignment["exact_q007ag_trajectory_stays_in_tube"]
        and alignment["repaired_q007ao_trajectory_stays_in_tube"]
    )
    contractive = recurrence["fixed_coordinate_map_is_contractive"]
    initial_ready = defects["q007ao_initial_bound_ready"]
    step_ready = defects["q007am_step_bound_ready"]
    recurrence_ready = recurrence["recurrence_interval_invariant"]
    accuracy = recurrence["registered_accuracy_threshold_passed"]
    hypothesis_gates = {
        "exact_and_repaired_trajectories_remain_in_q007ag_tube": {
            "passed": bool(validity_passed and both_in_tube),
            "threshold": (
                "Q007ag exact and Q007ao/Q007an repaired invariance keep "
                "both trajectories in the same registered tube"
            ),
            "value": both_in_tube,
        },
        "fixed_coordinate_exact_map_is_strictly_contractive": {
            "passed": bool(validity_passed and contractive),
            "threshold": "L_plus<1",
            "value": recurrence[
                "fixed_coordinate_lipschitz_upper"
            ],
        },
        "initial_fixed_coordinate_error_is_enclosed": {
            "passed": bool(validity_passed and initial_ready),
            "threshold": (
                "d0 includes Q007ao selected and direct external errors "
                "without graph-shift double counting"
            ),
            "value": initial_ready,
        },
        "one_step_repaired_mpfr_local_defect_is_enclosed": {
            "passed": bool(validity_passed and step_ready),
            "threshold": (
                "epsilon_step includes Q007am base and external local "
                "coordinate defects"
            ),
            "value": step_ready,
        },
        "geometric_uniform_all_iterate_bound_closes": {
            "passed": bool(validity_passed and recurrence_ready),
            "threshold": (
                "[0,D] is invariant under d -> L_plus*d+epsilon_step and "
                "contains d0"
            ),
            "value": recurrence_ready,
        },
        "registered_tube_scale_accuracy_gate": {
            "passed": bool(validity_passed and accuracy),
            "threshold": "D_W/R_T<1e-6",
            "value": recurrence[
                "uniform_physical_to_tube_state_radius_ratio"
            ],
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q007ap propagated-tube shadowing audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "propagated-tube fixed-coordinate contraction certifies "
            "all-iterate MPFR-85 forward shadowing"
        )
    elif not contractive:
        outcome = "not_certified"
        classification = (
            "registered propagated-tube fixed-coordinate majorant is not "
            "contractive"
        )
    elif not accuracy:
        outcome = "not_certified"
        classification = (
            "uniform propagated-tube shadow bound exceeds the registered "
            "accuracy threshold"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered propagated-tube recurrence does not certify "
            "all-iterate forward shadowing"
        )

    result_sections = {
        **recurrence_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = _canonical_json_sha256(result_sections)
    return {
        "question": (
            "Does the fixed linear eigencoordinate norm make the exact "
            "Q007ag map contractive enough to sum Q007ao initialization "
            "and Q007am local repaired-MPFR defects into an all-iterate "
            "same-initial forward-error bound?"
        ),
        "registered_parameters": registered_parameters,
        "input_artifacts": input_records,
        **recurrence_sections,
        "input_digest_sha256": input_digest,
        "recurrence_digest_sha256": recurrence_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "fixed_coordinate_exact_map_is_contractive_on_q007ag": bool(
                validity_passed and contractive
            ),
            "same_initial_forward_coordinate_error_is_uniform_all_iterate": (
                bool(validity_passed and recurrence_ready)
            ),
            "same_initial_forward_physical_error_meets_tube_scale_gate": (
                bool(validity_passed and accuracy)
            ),
            "q007ao_exact_initialization_to_all_iterate_shadowing": bool(
                validity_passed and hypotheses_passed
            ),
            "bi_infinite_shadowing_certified": False,
            "intermediate_stage_distance_certified": False,
            "arbitrary_q007ag_boundary_initialization_certified": False,
        },
        "claim_boundary": (
            "Shadowing here is a sampling-time forward-error bound between "
            "the exact orbit from a Q007ao exact fixed-leaf initial state "
            "and the repaired MPFR-85 orbit obtained by encoding that same "
            "state. It holds for all nonnegative iterates in one fixed "
            "linear eigencoordinate norm, with a derived physical Wiener "
            "bound. It is not a bi-infinite shadowing lemma, backward-error "
            "result, intermediate-stage distance, componentwise relative-"
            "error bound, arbitrary Q007ag-boundary initialization, "
            "performance result, another grid or MPFR build, GPU or "
            "parallel-reduction result, grid-uniform or continuum result, "
            "or D3Q27 result."
        ),
        "preserved_prior_outcomes": {
            "q007ab_old_tube_shadowing_changed": False,
            "q007ao_initialization_acceptance_changed": False,
            "q007an_conditional_induction_changed": False,
            "q007am_one_step_repair_result_changed": False,
            "q007z_selected_wave_result_changed": False,
            "q007aj_binary64_reentry_rejection_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted, close the propagated-tube finite-precision chain. "
            "Keep Q009 TT-cross held by Q008c/Q010, and preregister either "
            "Q011 boundary/forcing or a separate alternative-norm "
            "certificate before proceeding."
        ),
    }


def run_q007ap_study(
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
            **q007y.backend.backend_runtime_metadata(),
        },
        "mathematical_scope": {
            "diagnostic": (
                "propagated-tube fixed-linear-coordinate all-iterate "
                "same-initial repaired-MPFR forward-shadowing certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(q007y.backend.EXACT_OMEGA),
            "eta": float(q007y.backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "input and post-filter repair"
            ),
            "manifold": (
                "Q007ae exact graph-gauge manifold and Q007ag registered "
                "tube"
            ),
            "norm": (
                "fixed selected/external eigencoordinate direct-sum l1 "
                "with derived Fourier-population Wiener bound"
            ),
            "outer_base_modal_l1_radius": 9e-17,
            "outer_normal_coordinate_radius": 5e-11,
            "initial_base_modal_l1_radius": float(
                q007ao.INITIAL_BASE_RADIUS
            ),
            "initial_normal_coordinate_radius": float(
                q007ao.INITIAL_NORMAL_RADIUS
            ),
            "repair_lattice": "four diagonal populations on h=2^-90",
            "rounding_model": (
                "sealed Q007x gmpy2 2.3.1 / MPFR 4.2.2 nearest-even backend"
            ),
            "claim": (
                "same-initial-state sampling-time all-iterate forward "
                "error for the sealed repaired MPFR-85 backend"
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
    result = run_q007ap_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
