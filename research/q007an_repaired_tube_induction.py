"""Sealed Q007an repaired MPFR-85 self-map and induction audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

import research.q007ag_tube_radius_propagation as q007ag
import research.q007ai_propagated_tube_stagewise_positivity as q007ai
import research.q007al_propagated_tube_mpfr85_bridge as q007al
import research.q007am_propagated_tube_distributed_repair as q007am
import research.q007x_mpfr_fixed_leaf as q007x
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
BASE_RADIUS = Fraction(9, 10**17)
NORMAL_RADIUS = Fraction(5, 10**11)

REGISTERED_INPUTS = {
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
    "q007ai": {
        "filename": "q007ai_propagated_tube_stagewise_positivity.json",
        "module": q007ai,
        "artifact_sha256": (
            "3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804"
        ),
        "runner_sha256": (
            "3235b2dc31445e5912f2aaf7fc080e8295035801ade9b27d3f683d34da61173d"
        ),
        "classification": (
            "registered Q007ag propagated tube is population-positive at "
            "every exact BGK, streaming, and filter stage"
        ),
        "diagnostic": (
            "rational propagated-tube exact stagewise-positivity certificate"
        ),
        "conservation": "fixed global mass and momentum leaf",
        "validity_count": 6,
        "hypothesis_count": 5,
        "digests": {
            "input_digest_sha256": (
                "0dff47e8b0ed6e9b87cb73e6dea20192088495b51283c57b9d58630b7344c6a3"
            ),
            "result_digest_sha256": (
                "c101313957c738ccee9fd3d7f1ed36b77c6f3dad4e1130651f5be4d8757ef18a"
            ),
        },
    },
    "q007al": {
        "filename": "q007al_propagated_tube_mpfr85_bridge.json",
        "module": q007al,
        "artifact_sha256": (
            "bf1a2d9959f24cfc83a4efb2926ec76d9ced97755846ee310490585940d8dcf5"
        ),
        "runner_sha256": (
            "b82e03145e0c7f1c20b1d1345b87acbae5ce526b732969c391b88141118dfd8e"
        ),
        "classification": (
            "registered MPFR-85 backend realizes the Q007ag one-step "
            "arithmetic and complement-coordinate error budgets"
        ),
        "diagnostic": (
            "propagated-tube concrete MPFR-85 one-step arithmetic and "
            "complement-coordinate budget bridge"
        ),
        "conservation": (
            "fixed-leaf exact-map reference with rounded conservation "
            "defects retained as a non-hypothesis diagnostic"
        ),
        "validity_count": 8,
        "hypothesis_count": 5,
        "digests": {
            "input_digest_sha256": q007am.REGISTERED_Q007AL_DIGESTS["input"],
            "candidate_digest_sha256": q007am.REGISTERED_Q007AL_DIGESTS[
                "candidate"
            ],
            "probe_digest_sha256": q007am.REGISTERED_Q007AL_DIGESTS["probe"],
            "trace_digest_sha256": q007am.REGISTERED_Q007AL_DIGESTS["trace"],
            "campaign_result_digest_sha256": q007am.REGISTERED_Q007AL_DIGESTS[
                "campaign_result"
            ],
            "result_digest_sha256": q007am.REGISTERED_Q007AL_DIGESTS["result"],
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
}

REGISTERED_FLOATS = {
    "base_radius": 9e-17,
    "normal_radius": 5e-11,
    "base_margin": 4.978814700017615e-20,
    "normal_margin": 9.144951058528087e-13,
    "base_error": 1.1581233824834727e-21,
    "normal_error": 2.2935127565743277e-20,
    "base_headroom": 4.863002361769267e-20,
    "normal_headroom": 9.144950829176811e-13,
    "base_margin_utilization": 0.02326102601246388,
    "normal_margin_utilization": 2.5079552005207522e-8,
    "exact_minimum_stage_lower": 0.027777777320468006,
    "mpfr_minimum_stage_lower": 0.027777777145968227,
    "repaired_diagonal_binade_lower": 0.015625,
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
    registered = REGISTERED_INPUTS[name]
    common = bool(
        scope.get("diagnostic") == registered["diagnostic"]
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega")) == 1.5
        and float(scope.get("eta")) == 0.01
        and scope.get("conservation_treatment") == registered["conservation"]
        and scope.get("manifold") == "Q007ae exact graph-gauge manifold"
        and scope.get("norm")
        == "Q007p Fourier external-coordinate block-sum l1"
    )
    if name == "q007ag":
        return common
    radii = bool(
        float(scope.get("base_modal_l1_radius")) == 9e-17
        and float(scope.get("normal_coordinate_radius")) == 5e-11
    )
    if name == "q007am":
        return bool(
            common
            and radii
            and scope.get("repair_lattice")
            == "four diagonal populations on h=2^-90"
        )
    return bool(common and radii)


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
            "runner_sha256_matches": runner_sha == registered["runner_sha256"],
            "artifact_runner_sha256": payload.get("runner_source", {}).get(
                "sha256"
            ),
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
            "all_validity_gates_pass": _all_gates_pass(cycle, "validity_gates"),
            "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
            "registered_hypothesis_gate_count": registered["hypothesis_count"],
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
    fresh_cycles = {
        "q007ag": q007ag.run_tube_radius_propagation_audit(directory),
        "q007ai": q007ai.run_propagated_tube_stagewise_positivity_audit(
            directory
        ),
        "q007am": q007am.run_propagated_tube_distributed_repair_audit(
            directory
        ),
    }
    records: dict[str, dict[str, Any]] = {}
    for name, fresh in fresh_cycles.items():
        stored = payloads[name]["cycle"]
        records[name] = {
            "stored_cycle_reproduced_exactly": fresh == stored,
            "validity_gate_count": len(fresh["validity_gates"]),
            "all_validity_gates_pass": _all_gates_pass(fresh, "validity_gates"),
            "hypothesis_gate_count": len(fresh["hypothesis_gates"]),
            "all_hypothesis_gates_pass": _all_gates_pass(
                fresh, "hypothesis_gates"
            ),
            "result_digest_sha256": fresh["result_digest_sha256"],
            "passed": bool(
                fresh == stored
                and _all_gates_pass(fresh, "validity_gates")
                and _all_gates_pass(fresh, "hypothesis_gates")
                and fresh["study_validity"] == "passed"
                and fresh["hypothesis_outcome"] == "accepted"
            ),
        }
    am = fresh_cycles["q007am"]
    nested = {
        "q007al_stored_cycle_reproduced_exactly": am["q007al_reproduction"][
            "stored_cycle_reproduced_exactly"
        ],
        "q007al_digests_match": am["q007al_reproduction"]["digests_match"],
        "q007al_passed": am["q007al_reproduction"]["passed"],
        "q007y_stored_cycle_reproduced_exactly": am["q007y_reproduction"][
            "stored_cycle_reproduced_exactly"
        ],
        "q007y_passed": am["q007y_reproduction"]["passed"],
    }
    nested["passed"] = all(nested.values())
    return {
        "cycles": records,
        "q007am_nested_reproductions": nested,
        "passed": bool(
            all(record["passed"] for record in records.values())
            and nested["passed"]
        ),
    }


def _scope_alignment(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ag = payloads["q007ag"]["cycle"]
    ai = payloads["q007ai"]["cycle"]
    al = payloads["q007al"]["cycle"]
    am = payloads["q007am"]["cycle"]
    selected = ag["selection"]["selected_candidate"]
    ag_base = _fraction_from_record(selected["base_radius"])
    ag_normal = _fraction_from_record(selected["normal_radius"])
    ai_base = _fraction_from_record(ai["registered_parameters"]["base_radius"])
    ai_normal = _fraction_from_record(
        ai["registered_parameters"]["normal_radius"]
    )
    al_probes = al["probe_registration"]["probes"]
    al_probe_radii = {
        _fraction_from_record(probe["registered_component_radius"])
        for probe in al_probes
    }
    target = am["registered_parameters"]["target_conserved"]
    target_exact = tuple(
        _fraction_from_record(target[name])
        for name in ("mass", "momentum_x", "momentum_y")
    )
    radius_alignment = bool(
        ag_base == BASE_RADIUS
        and ai_base == BASE_RADIUS
        and ag_normal == NORMAL_RADIUS
        and ai_normal == NORMAL_RADIUS
        and len(al_probe_radii) == 1
    )
    common_scope = all(
        payloads[name]["mathematical_scope"].get("construction_grid")
        == [SIZE, SIZE]
        and float(payloads[name]["mathematical_scope"].get("omega")) == 1.5
        and float(payloads[name]["mathematical_scope"].get("eta")) == 0.01
        for name in payloads
    )
    repair = am["registered_parameters"]
    repair_alignment = bool(
        repair["size"] == SIZE
        and repair["wave_count"] == WAVE_COUNT
        and repair["precision_bits"] == PRECISION_BITS
        and _fraction_from_record(repair["repair_quantum"])
        == q007y.REPAIR_QUANTUM
        and repair["diagonal_populations"] == list(q007y.DIAGONAL_POPULATIONS)
        and target_exact == q007y.TARGET_CONSERVED
        and repair["distribution"] == "Python divmod over 289 row-major sites"
    )
    coordinate_alignment = bool(
        all(
            payloads[name]["mathematical_scope"].get("manifold")
            == "Q007ae exact graph-gauge manifold"
            and payloads[name]["mathematical_scope"].get("norm")
            == "Q007p Fourier external-coordinate block-sum l1"
            for name in payloads
        )
    )
    passed = bool(
        radius_alignment
        and common_scope
        and repair_alignment
        and coordinate_alignment
    )
    return {
        "base_radius": _fraction_record(ag_base),
        "normal_radius": _fraction_record(ag_normal),
        "q007al_probe_component_radius_count": len(al_probe_radii),
        "q007al_probe_component_radius": _fraction_record(
            next(iter(al_probe_radii)) if len(al_probe_radii) == 1 else Fraction(0)
        ),
        "target_conserved": {
            name: _fraction_record(value)
            for name, value in zip(
                ("mass", "momentum_x", "momentum_y"),
                target_exact,
                strict=True,
            )
        },
        "radius_alignment": radius_alignment,
        "common_grid_omega_eta": common_scope,
        "coordinate_manifold_and_norm_alignment": coordinate_alignment,
        "repair_backend_target_and_distribution_alignment": repair_alignment,
        "passed": passed,
    }


def _self_map_composition(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ag = payloads["q007ag"]["cycle"]
    am = payloads["q007am"]["cycle"]
    selected = ag["selection"]["selected_candidate"]
    bound = am["tube_wide_repair_bound"]

    base_radius = _fraction_from_record(selected["base_radius"])
    normal_radius = _fraction_from_record(selected["normal_radius"])
    base_image = _fraction_from_record(selected["base_image"])
    normal_contraction = _fraction_from_record(selected["normal_contraction"])
    normal_image = normal_radius * normal_contraction
    ag_base_margin = _fraction_from_record(
        selected["strict_margins"]["base_forward_invariance"]
    )
    ag_normal_margin = _fraction_from_record(
        selected["strict_margins"]["normal_tube_forward_invariance"]
    )
    am_base_margin = _fraction_from_record(bound["base_margin"])
    am_normal_margin = _fraction_from_record(bound["normal_margin"])
    base_error = _fraction_from_record(bound["base_coordinate_error_upper"])
    normal_error = _fraction_from_record(
        bound["normal_coordinate_error_upper"]
    )
    repaired_base_image = base_image + base_error
    repaired_normal_image = normal_image + normal_error
    base_headroom = base_radius - repaired_base_image
    normal_headroom = normal_radius - repaired_normal_image
    identities = {
        "q007ag_base_margin_is_radius_minus_exact_image": (
            base_radius - base_image == ag_base_margin
        ),
        "q007ag_normal_margin_is_radius_minus_exact_image": (
            normal_radius - normal_image == ag_normal_margin
        ),
        "q007ag_and_q007am_base_margins_match": (
            ag_base_margin == am_base_margin
        ),
        "q007ag_and_q007am_normal_margins_match": (
            ag_normal_margin == am_normal_margin
        ),
        "repaired_base_image_is_exact_image_plus_error": (
            repaired_base_image == base_image + base_error
        ),
        "repaired_normal_image_is_exact_image_plus_error": (
            repaired_normal_image == normal_image + normal_error
        ),
        "base_headroom_is_margin_minus_error": (
            base_headroom == ag_base_margin - base_error
        ),
        "normal_headroom_is_margin_minus_error": (
            normal_headroom == ag_normal_margin - normal_error
        ),
    }
    observed_floats = {
        "base_radius": float(base_radius),
        "normal_radius": float(normal_radius),
        "base_margin": float(ag_base_margin),
        "normal_margin": float(ag_normal_margin),
        "base_error": float(base_error),
        "normal_error": float(normal_error),
        "base_headroom": float(base_headroom),
        "normal_headroom": float(normal_headroom),
        "base_margin_utilization": float(base_error / ag_base_margin),
        "normal_margin_utilization": float(normal_error / ag_normal_margin),
    }
    base_reentry = repaired_base_image < base_radius
    normal_reentry = repaired_normal_image < normal_radius
    coarse_bound_preserved = bool(
        not bound["triangle_bound_uses_center_cancellation"]
        and not bound["triangle_bound_uses_spatial_fourier_phase"]
        and not bound["q007z_selected_wave_bound_used"]
    )
    passed = bool(
        all(identities.values())
        and observed_floats
        == {key: REGISTERED_FLOATS[key] for key in observed_floats}
        and bound["base_reentry_budget_passed"]
        and bound["normal_reentry_budget_passed"]
        and base_reentry
        and normal_reentry
        and coarse_bound_preserved
    )
    return {
        "base_radius": _fraction_record(base_radius),
        "normal_radius": _fraction_record(normal_radius),
        "exact_base_image_upper": _fraction_record(base_image),
        "exact_normal_image_upper": _fraction_record(normal_image),
        "q007ag_base_margin": _fraction_record(ag_base_margin),
        "q007ag_normal_margin": _fraction_record(ag_normal_margin),
        "q007am_base_margin": _fraction_record(am_base_margin),
        "q007am_normal_margin": _fraction_record(am_normal_margin),
        "repair_aware_base_error_upper": _fraction_record(base_error),
        "repair_aware_normal_error_upper": _fraction_record(normal_error),
        "repaired_base_image_upper": _fraction_record(repaired_base_image),
        "repaired_normal_image_upper": _fraction_record(repaired_normal_image),
        "base_headroom": _fraction_record(base_headroom),
        "normal_headroom": _fraction_record(normal_headroom),
        "base_margin_utilization": _fraction_record(
            base_error / ag_base_margin
        ),
        "normal_margin_utilization": _fraction_record(
            normal_error / ag_normal_margin
        ),
        "arithmetic_identities": identities,
        "all_arithmetic_identities_pass": all(identities.values()),
        "registered_float_values": {
            key: REGISTERED_FLOATS[key] for key in observed_floats
        },
        "observed_float_values": observed_floats,
        "registered_float_values_match": (
            observed_floats
            == {key: REGISTERED_FLOATS[key] for key in observed_floats}
        ),
        "base_strict_reentry": base_reentry,
        "normal_strict_reentry": normal_reentry,
        "triangle_bound_uses_center_cancellation": bound[
            "triangle_bound_uses_center_cancellation"
        ],
        "triangle_bound_uses_spatial_fourier_phase": bound[
            "triangle_bound_uses_spatial_fourier_phase"
        ],
        "q007z_selected_wave_bound_used": bound[
            "q007z_selected_wave_bound_used"
        ],
        "coarse_q007am_bound_preserved": coarse_bound_preserved,
        "passed": passed,
    }


def _stage_composition(payloads: dict[str, dict[str, Any]]) -> dict[str, Any]:
    ai = payloads["q007ai"]["cycle"]
    al = payloads["q007al"]["cycle"]
    am = payloads["q007am"]["cycle"]
    ai_bounds = ai["stage_bounds"]
    exact_lowers = {
        name: _fraction_from_record(ai_bounds[key])
        for name, key in {
            "equilibrium": "equilibrium_population_lower",
            "post_collision": "post_collision_population_lower",
            "post_streaming": "post_streaming_population_lower",
            "post_filter": "post_filter_population_lower",
        }.items()
    }
    exact_minimum = min(exact_lowers.values())
    candidate = al["ideal_p85_certificate"]["candidate"]
    mpfr_minimum = _fraction_from_record(candidate["minimum_stage_lower"])
    post = am["tube_wide_repair_bound"]["post_filter"]
    correction = _fraction_from_record(post["maximum_site_correction_upper"])
    diagonal_lowers = {
        str(record["population"]): (
            _fraction_from_record(record["computed_lower"]) - correction
        )
        for record in post["population_records"]
        if record["population"] in q007y.DIAGONAL_POPULATIONS
    }
    repaired_diagonal_minimum = min(diagonal_lowers.values())
    ai_theorem = ai["theorem_consequence"]
    registered_exact_stage_flags = (
        "equilibrium_evaluation_population_strictly_positive",
        "post_collision_population_strictly_positive",
        "post_streaming_population_strictly_positive",
        "post_filter_population_strictly_positive",
        "all_iterates_exact_stagewise_population_strictly_positive",
    )
    exact_stage_passed = bool(
        all(ai_theorem[name] for name in registered_exact_stage_flags)
        and not ai_theorem["new_tube_binary64_stage_enclosure_certified"]
        and exact_minimum > 0
        and float(exact_minimum)
        == REGISTERED_FLOATS["exact_minimum_stage_lower"]
    )
    mpfr_stage_passed = bool(
        candidate["one_step_stage_positivity_passed"]
        and candidate["operation_counts_match"]
        and mpfr_minimum > 0
        and float(mpfr_minimum)
        == REGISTERED_FLOATS["mpfr_minimum_stage_lower"]
    )
    repaired_stage_passed = bool(
        post["repaired_diagonal_binade_and_positivity_passed"]
        and post["passed"]
        and repaired_diagonal_minimum >= q007y.DIAGONAL_BIN_LOWER
        and float(q007y.DIAGONAL_BIN_LOWER)
        == REGISTERED_FLOATS["repaired_diagonal_binade_lower"]
    )
    passed = bool(
        exact_stage_passed and mpfr_stage_passed and repaired_stage_passed
    )
    return {
        "exact_stage_population_lowers": {
            name: _fraction_record(value) for name, value in exact_lowers.items()
        },
        "exact_minimum_stage_lower": _fraction_record(exact_minimum),
        "mpfr_minimum_stage_lower": _fraction_record(mpfr_minimum),
        "postfilter_maximum_site_repair_upper": _fraction_record(correction),
        "repaired_diagonal_population_lowers": {
            name: _fraction_record(value)
            for name, value in diagonal_lowers.items()
        },
        "repaired_diagonal_minimum_lower": _fraction_record(
            repaired_diagonal_minimum
        ),
        "registered_diagonal_binade_lower": _fraction_record(
            q007y.DIAGONAL_BIN_LOWER
        ),
        "q007ai_exact_all_iterate_stagewise_positivity": exact_stage_passed,
        "q007al_mpfr85_tube_wide_stage_positivity": mpfr_stage_passed,
        "q007am_postfilter_repair_binade_and_positivity": (
            repaired_stage_passed
        ),
        "passed": passed,
    }


def _repair_identity_and_closure(
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    solution = q007y.solve_diagonal_repair_units(0, 0, 0)
    distributions = {
        str(population): list(
            q007y.balanced_unit_distribution(units, WAVE_COUNT)
        )
        for population, units in zip(
            q007y.DIAGONAL_POPULATIONS,
            solution.diagonal_units,
            strict=True,
        )
    }
    zero_solver = bool(
        solution.free_unit == 0
        and solution.diagonal_units == (0, 0, 0, 0)
        and all(all(unit == 0 for unit in values) for values in distributions.values())
    )

    al = payloads["q007al"]["cycle"]
    probe_radius = _fraction_from_record(
        al["probe_registration"]["probes"][0]["registered_component_radius"]
    )
    probe_audit, probes = q007x._probe_registration_audit(probe_radius)
    first_name, exact_input = probes[0]
    concrete = q007y.backend.MPFRD2Q9Backend()
    encoded, _ = concrete.encode_fraction_state(exact_input)
    repaired_once, first_audit = q007y.repair_conserved_state(encoded)
    repaired_twice, second_audit = q007y.repair_conserved_state(repaired_once)
    once_exact = q007x._mpfr_to_fraction_array(repaired_once)
    twice_exact = q007x._mpfr_to_fraction_array(repaired_twice)
    witness_unchanged = np.array_equal(once_exact, twice_exact)
    second_zero = bool(
        all(value == 0 for value in second_audit["requested_units"].values())
        and second_audit["solution"]["free_unit"] == 0
        and second_audit["solution"]["diagonal_units"] == [0, 0, 0, 0]
        and _fraction_from_record(second_audit["maximum_component_correction"])
        == 0
    )
    generic_identity = bool(
        zero_solver
        and q007y._global_conserved_mpfr(repaired_once)
        == q007y.TARGET_CONSERVED
        and second_zero
        and witness_unchanged
    )

    am = payloads["q007am"]["cycle"]
    campaign = am["finite_campaign"]
    bound = am["tube_wide_repair_bound"]
    output_closure = bool(
        campaign["summary"]["all_output_repairs_conserve"]
        and campaign["summary"]["all_repairs_solve_and_add_exactly"]
        and bound["repair_map_well_defined_on_registered_component_tube"]
        and bound["post_filter"]["repaired_diagonal_binade_and_positivity_passed"]
    )
    mpfr_representability = bool(
        all(value.precision == PRECISION_BITS for value in repaired_twice.flat)
        and second_audit["operations_exact_and_positive"]
        and second_audit["dangerous_flags_clear"]
    )
    passed = bool(
        probe_audit["passed"]
        and first_audit["passed"]
        and second_audit["passed"]
        and generic_identity
        and output_closure
        and mpfr_representability
    )
    return {
        "generic_zero_defect_argument": {
            "exact_mpfr_conserved_sum_uses_fraction_conversion": True,
            "zero_defect_requested_units": [0, 0, 0],
            "zero_solution_free_unit": solution.free_unit,
            "zero_solution_diagonal_units": list(solution.diagonal_units),
            "all_balanced_distribution_units_zero": all(
                all(unit == 0 for unit in values)
                for values in distributions.values()
            ),
            "passed": zero_solver,
        },
        "finite_idempotence_witness": {
            "probe_name": first_name,
            "probe_registration_passed": probe_audit["passed"],
            "first_repair_passed": first_audit["passed"],
            "second_requested_units": second_audit["requested_units"],
            "second_solution_diagonal_units": second_audit["solution"][
                "diagonal_units"
            ],
            "second_maximum_component_correction": second_audit[
                "maximum_component_correction"
            ],
            "state_unchanged_exactly": witness_unchanged,
            "second_repair_passed": second_audit["passed"],
            "passed": bool(
                probe_audit["passed"]
                and first_audit["passed"]
                and second_audit["passed"]
                and second_zero
                and witness_unchanged
            ),
        },
        "input_repair_is_identity_on_exact_fixed_leaf": generic_identity,
        "postfilter_repair_restores_exact_fixed_leaf_tube_wide": output_closure,
        "repair_output_remains_mpfr85_representable": mpfr_representability,
        "passed": passed,
    }


def run_repaired_tube_induction_audit(
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
    composition = _self_map_composition(payloads)
    stages = _stage_composition(payloads)
    repair = _repair_identity_and_closure(payloads)

    registered_parameters = {
        "size": SIZE,
        "wave_count": WAVE_COUNT,
        "precision_bits": PRECISION_BITS,
        "base_radius": _fraction_record(BASE_RADIUS),
        "normal_radius": _fraction_record(NORMAL_RADIUS),
        "target_conserved": {
            name: _fraction_record(value)
            for name, value in zip(
                ("mass", "momentum_x", "momentum_y"),
                q007y.TARGET_CONSERVED,
                strict=True,
            )
        },
        "repair_quantum": _fraction_record(q007y.REPAIR_QUANTUM),
        "diagonal_populations": list(q007y.DIAGONAL_POPULATIONS),
        "sampling_map": "postfilter repair after sealed MPFR-85 BGK/stream/filter",
        "initial_condition": (
            "already encoded and repaired MPFR-85 fixed-leaf state inside "
            "the registered Q007ag tube"
        ),
    }
    input_digest = _canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "registered_parameters": registered_parameters,
        }
    )
    composition_sections = {
        "fresh_reproductions": reproductions,
        "scope_alignment": alignment,
        "self_map_composition": composition,
        "stage_composition": stages,
        "repair_identity_and_closure": repair,
    }
    composition_digest = _canonical_json_sha256(composition_sections)
    strict_json = bool(
        _all_numeric_values_finite(composition_sections)
        and _strict_json_serializable(composition_sections)
    )
    digests_reproducible = bool(
        input_digest
        == _canonical_json_sha256(
            {
                "input_artifacts": input_records,
                "registered_parameters": registered_parameters,
            }
        )
        and composition_digest == _canonical_json_sha256(composition_sections)
    )

    input_passed = all(record["passed"] for record in input_records.values())
    validity_gates = {
        "sealed_artifacts_sources_scopes_outcomes_gates_and_digests": {
            "passed": input_passed,
            "threshold": (
                "all four artifact/runner SHA values, source/scope records, "
                "accepted outcomes, gate counts, and digests match"
            ),
            "value": input_passed,
        },
        "fresh_upstream_cycles_and_nested_reproductions": {
            "passed": reproductions["passed"],
            "threshold": (
                "Q007ag, Q007ai, and Q007am replay exactly and Q007am's "
                "nested Q007al/Q007y reproductions pass"
            ),
            "value": reproductions["passed"],
        },
        "tube_coordinates_backend_target_and_repair_align": {
            "passed": alignment["passed"],
            "threshold": (
                "radii, fixed leaf, graph/external coordinates, backend, "
                "repair lattice, and distribution agree"
            ),
            "value": alignment["passed"],
        },
        "exact_margin_and_triangle_composition": {
            "passed": composition["passed"],
            "threshold": (
                "Q007ag margins equal Q007am margins and both repaired image "
                "bounds retain strict positive headroom"
            ),
            "value": composition["passed"],
        },
        "exact_mpfr_and_repaired_stage_positivity_align": {
            "passed": stages["passed"],
            "threshold": (
                "Q007ai exact, Q007al MPFR-85, and Q007am repaired stage "
                "lower bounds are positive on the same box"
            ),
            "value": stages["passed"],
        },
        "input_identity_output_fixed_leaf_and_mpfr_closure": {
            "passed": repair["passed"],
            "threshold": (
                "zero-defect repair is identity and output repair restores "
                "the exact fixed leaf in MPFR-85"
            ),
            "value": repair["passed"],
        },
        "finite_strict_json_and_digests": {
            "passed": bool(strict_json and digests_reproducible),
            "threshold": (
                "all records are finite strict JSON and input/composition "
                "digests reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproducible": digests_reproducible,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    ag = payloads["q007ag"]["cycle"]
    al = payloads["q007al"]["cycle"]
    am = payloads["q007am"]["cycle"]
    exact_interior = bool(
        ag["theorem_consequence"]["selected_registered_tube_forward_invariant"]
        and composition["q007ag_base_margin"]["float"] > 0
        and composition["q007ag_normal_margin"]["float"] > 0
    )
    raw_mpfr = bool(
        al["ideal_p85_certificate"]["candidate"][
            "one_step_stage_positivity_passed"
        ]
        and stages["q007al_mpfr85_tube_wide_stage_positivity"]
    )
    repair_closure = bool(
        am["theorem_consequence"][
            "distributed_repair_is_defined_on_q007ag_component_tube"
        ]
        and repair["input_repair_is_identity_on_exact_fixed_leaf"]
        and repair["postfilter_repair_restores_exact_fixed_leaf_tube_wide"]
        and repair["repair_output_remains_mpfr85_representable"]
    )
    base_reentry = composition["base_strict_reentry"]
    normal_reentry = composition["normal_strict_reentry"]
    one_step_self_map = bool(
        validity_passed
        and exact_interior
        and raw_mpfr
        and repair_closure
        and base_reentry
        and normal_reentry
        and stages["passed"]
    )
    induction = bool(
        one_step_self_map
        and repair["input_repair_is_identity_on_exact_fixed_leaf"]
        and repair["repair_output_remains_mpfr85_representable"]
    )
    hypothesis_gates = {
        "q007ag_exact_map_enters_strict_tube_interior": {
            "passed": bool(validity_passed and exact_interior),
            "threshold": "exact image retains both registered strict margins",
            "value": exact_interior,
        },
        "q007al_mpfr85_raw_map_is_defined_and_stage_positive": {
            "passed": bool(validity_passed and raw_mpfr),
            "threshold": (
                "the tube-wide MPFR-85 raw map has positive population at "
                "every internal stage"
            ),
            "value": raw_mpfr,
        },
        "q007am_repair_restores_fixed_leaf_positive_mpfr85_output": {
            "passed": bool(validity_passed and repair_closure),
            "threshold": (
                "the repair is tube-wide, exact, same-binade positive, and "
                "returns an MPFR-85 fixed-leaf state"
            ),
            "value": repair_closure,
        },
        "repair_aware_base_coordinate_strictly_reenters": {
            "passed": bool(validity_passed and base_reentry),
            "threshold": "repair-aware base error is below exact base margin",
            "value": base_reentry,
        },
        "repair_aware_normal_coordinate_strictly_reenters": {
            "passed": bool(validity_passed and normal_reentry),
            "threshold": (
                "repair-aware normal error is below exact normal margin"
            ),
            "value": normal_reentry,
        },
        "repaired_mpfr85_sampling_map_is_one_step_tube_self_map": {
            "passed": one_step_self_map,
            "threshold": "the preceding five hypotheses compose",
            "value": one_step_self_map,
        },
        "repaired_mpfr85_fixed_leaf_tube_induction_closes": {
            "passed": induction,
            "threshold": (
                "identity input repair plus the one-step self-map closes "
                "mathematical induction"
            ),
            "value": induction,
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())

    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007an repaired-tube induction audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "coarse repair certificate closes the Q007ag repaired MPFR-85 "
            "fixed-leaf tube induction"
        )
    elif not base_reentry or not normal_reentry:
        outcome = "not_certified"
        classification = (
            "Q007am one-step budgets do not compose with the Q007ag exact "
            "margins"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered repaired MPFR-85 map does not close the Q007ag tube "
            "induction"
        )

    result_sections = {
        **composition_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = _canonical_json_sha256(result_sections)
    return {
        "question": (
            "Do the sealed exact invariance, MPFR-85 stage enclosure, and "
            "distributed repair budgets compose into a conditional all-iterate "
            "self-map of the Q007ag fixed-leaf tube?"
        ),
        "registered_parameters": registered_parameters,
        "input_artifacts": input_records,
        **composition_sections,
        "input_digest_sha256": input_digest,
        "composition_digest_sha256": composition_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "input_repair_is_identity_on_registered_fixed_leaf": bool(
                hypotheses_passed
            ),
            "registered_repaired_mpfr85_map_is_q007ag_tube_self_map": bool(
                hypotheses_passed
            ),
            "sampling_times_preserve_exact_mass_and_momentum": bool(
                hypotheses_passed
            ),
            "conditional_all_iterate_repaired_mpfr85_q007ag_tube_invariance": (
                bool(hypotheses_passed)
            ),
            "conditional_all_iterate_mpfr85_internal_stage_positivity": bool(
                hypotheses_passed
            ),
            "arbitrary_exact_state_initialization_interior_certified": False,
            "same_initial_q007ag_forward_shadowing_certified": False,
        },
        "claim_boundary": (
            "The induction is conditional on an already encoded and repaired "
            "MPFR-85 state lying in the fixed-mass/fixed-momentum Q007ag tube. "
            "It certifies sampling-time fixed-leaf conservation, strict tube "
            "re-entry, and internal-stage positivity for the sealed 17x17 "
            "backend and row-major repair. The four probes are implementation "
            "regressions, not a tube sampling proof; the induction uses the "
            "tube-wide exact-rational upstream bounds. It does not certify an "
            "arbitrary exact-state initialization interior, same-initial "
            "shadowing or trajectory error, performance, GPU or parallel "
            "reduction behavior, another grid or MPFR build, grid-uniformity, "
            "a continuum limit, or D3Q27. The Q007z old-tube induction and "
            "Q007am one-step-only theorem remain unchanged in their scopes."
        ),
        "preserved_prior_outcomes": {
            "q007z_old_tube_selected_wave_induction_changed": False,
            "q007am_one_step_claim_boundary_changed": False,
            "q007al_one_step_bridge_claim_boundary_changed": False,
            "q007aj_binary64_reentry_rejection_changed": False,
            "q007ag_exact_tube_acceptance_changed": False,
            "q007ai_exact_stagewise_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister Q007ao to certify an exact-state "
            "initialization interior whose componentwise MPFR-85 encoding and "
            "input repair enter the Q007ag repaired tube; keep same-initial "
            "shadowing separate."
        ),
    }


def run_q007an_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_repaired_tube_induction_audit(artifact_directory)
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
                "conditional all-iterate repaired MPFR-85 self-map of the "
                "propagated fixed-leaf tube"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(q007y.backend.EXACT_OMEGA),
            "eta": float(q007y.backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "post-filter repair"
            ),
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "repair_lattice": "four diagonal populations on h=2^-90",
            "rounding_model": (
                "sealed Q007x gmpy2 2.3.1 / MPFR 4.2.2 nearest-even backend"
            ),
            "initial_condition": (
                "already encoded and repaired MPFR-85 state in the Q007ag "
                "fixed-leaf tube"
            ),
            "claim": (
                "conditional all-iterate sampling-time tube invariance and "
                "internal-stage positivity, excluding initialization and "
                "shadowing"
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
    result = run_q007an_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
