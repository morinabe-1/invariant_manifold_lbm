"""Sealed Q007ao propagated-tube initialization-interior audit."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007ag_tube_radius_propagation as q007ag
import research.q007am_propagated_tube_distributed_repair as q007am
import research.q007an_repaired_tube_induction as q007an
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
OUTER_BASE_RADIUS = Fraction(9, 10**17)
OUTER_NORMAL_RADIUS = Fraction(5, 10**11)
INITIAL_BASE_RADIUS = Fraction(89_998, 10**21)
INITIAL_NORMAL_RADIUS = Fraction(4_999_999_999, 10**20)
BASE_INWARD_MARGIN = OUTER_BASE_RADIUS - INITIAL_BASE_RADIUS
NORMAL_INWARD_MARGIN = OUTER_NORMAL_RADIUS - INITIAL_NORMAL_RADIUS

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
    "q007an": {
        "filename": "q007an_repaired_tube_induction.json",
        "module": q007an,
        "artifact_sha256": (
            "dd28dc89f2096252db80e2ad7461ebdf71bb757e879b8657df01da766849ebdb"
        ),
        "runner_sha256": (
            "bacf2eca47348ebbb5f5fbfe739f3239ebdb49eedc0d615efc144eb113b5f1bf"
        ),
        "classification": (
            "coarse repair certificate closes the Q007ag repaired MPFR-85 "
            "fixed-leaf tube induction"
        ),
        "diagnostic": (
            "conditional all-iterate repaired MPFR-85 self-map of the "
            "propagated fixed-leaf tube"
        ),
        "conservation": (
            "fixed global mass and momentum leaf with exact diagonal "
            "post-filter repair"
        ),
        "validity_count": 7,
        "hypothesis_count": 7,
        "digests": {
            "input_digest_sha256": (
                "7d93718b4e8375ea3983c37042d0aaedc98f4a16a329687afa69f75511e29657"
            ),
            "composition_digest_sha256": (
                "7ce1bde2ddc99ace52610c1a814a65dada1711baf048ec5410241ce497f809d7"
            ),
            "result_digest_sha256": (
                "80bae2065ec27d22c7e5a392f764e422ef57d521e0848d6c9eae3e0ed07e8bf7"
            ),
        },
    },
}

REGISTERED_FLOATS = {
    "outer_base_radius": 9e-17,
    "initial_base_radius": 8.9998e-17,
    "base_inward_margin": 2e-21,
    "outer_normal_radius": 5e-11,
    "initial_normal_radius": 4.999999999e-11,
    "normal_inward_margin": 1e-20,
    "raw_encoding_wiener_upper": 7.470474916829075e-24,
    "repair_wiener_upper": 1.2452407121655381e-23,
    "total_encoding_repair_wiener_upper": 1.9922882038484456e-23,
    "selected_analysis_upper": 1.5106842091904618,
    "external_analysis_upper": 29.917136268364473,
    "chart_derivative_upper": 1.0398158027969315e-14,
    "base_coordinate_increment_upper": 3.009718329710275e-23,
    "base_headroom": 1.9699028167028972e-21,
    "base_margin_utilization": 0.015048591648551374,
    "direct_external_coordinate_increment_upper": 5.960355768038905e-22,
    "graph_shift_external_coordinate_increment_upper": 9.362725402249564e-36,
    "normal_coordinate_increment_upper": 5.960355768038998e-22,
    "normal_headroom": 9.4039644231961e-21,
    "normal_margin_utilization": 0.05960355768038998,
    "tight_base_initialization_radius": 8.99999699028167e-17,
    "tight_normal_initialization_radius": 4.9999999999403966e-11,
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
        and scope.get("manifold") == "Q007ae exact graph-gauge manifold"
        and scope.get("norm")
        == "Q007p Fourier external-coordinate block-sum l1"
    )
    if name == "q007ag":
        return common
    return bool(
        common
        and float(scope.get("base_modal_l1_radius")) == 9e-17
        and float(scope.get("normal_coordinate_radius")) == 5e-11
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


def _fresh_q007an_reproduction(
    directory: Path,
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    fresh = q007an.run_repaired_tube_induction_audit(directory)
    stored = payloads["q007an"]["cycle"]
    nested = fresh["fresh_reproductions"]
    theorem = fresh["theorem_consequence"]
    passed = bool(
        fresh == stored
        and _all_gates_pass(fresh, "validity_gates")
        and _all_gates_pass(fresh, "hypothesis_gates")
        and fresh["study_validity"] == "passed"
        and fresh["hypothesis_outcome"] == "accepted"
        and nested["passed"]
        and theorem[
            "conditional_all_iterate_repaired_mpfr85_q007ag_tube_invariance"
        ]
        and theorem[
            "conditional_all_iterate_mpfr85_internal_stage_positivity"
        ]
        and not theorem[
            "arbitrary_exact_state_initialization_interior_certified"
        ]
        and not theorem[
            "same_initial_q007ag_forward_shadowing_certified"
        ]
    )
    return {
        "stored_cycle_reproduced_exactly": fresh == stored,
        "validity_gate_count": len(fresh["validity_gates"]),
        "all_validity_gates_pass": _all_gates_pass(
            fresh, "validity_gates"
        ),
        "hypothesis_gate_count": len(fresh["hypothesis_gates"]),
        "all_hypothesis_gates_pass": _all_gates_pass(
            fresh, "hypothesis_gates"
        ),
        "nested_fresh_reproductions_pass": nested["passed"],
        "nested_cycle_names": sorted(nested["cycles"]),
        "q007am_nested_reproductions_pass": nested[
            "q007am_nested_reproductions"
        ]["passed"],
        "conditional_tube_induction_ready": theorem[
            "conditional_all_iterate_repaired_mpfr85_q007ag_tube_invariance"
        ],
        "conditional_stage_positivity_ready": theorem[
            "conditional_all_iterate_mpfr85_internal_stage_positivity"
        ],
        "initialization_was_not_already_certified": not theorem[
            "arbitrary_exact_state_initialization_interior_certified"
        ],
        "shadowing_was_not_already_certified": not theorem[
            "same_initial_q007ag_forward_shadowing_certified"
        ],
        "input_digest_sha256": fresh["input_digest_sha256"],
        "composition_digest_sha256": fresh[
            "composition_digest_sha256"
        ],
        "result_digest_sha256": fresh["result_digest_sha256"],
        "passed": passed,
    }


def _scope_alignment(
    payloads: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    ag = payloads["q007ag"]["cycle"]
    am = payloads["q007am"]["cycle"]
    an = payloads["q007an"]["cycle"]
    selected = ag["selection"]["selected_candidate"]
    am_parameters = am["registered_parameters"]
    an_parameters = an["registered_parameters"]
    outer_base = _fraction_from_record(selected["base_radius"])
    outer_normal = _fraction_from_record(selected["normal_radius"])
    analytic_radius = _fraction_from_record(
        ag["constant_update_audit"]["new_rho"]
    )
    am_target = {
        name: _fraction_from_record(record)
        for name, record in am_parameters["target_conserved"].items()
    }
    an_target = {
        name: _fraction_from_record(record)
        for name, record in an_parameters["target_conserved"].items()
    }
    target = {
        "mass": Fraction(WAVE_COUNT),
        "momentum_x": Fraction(0),
        "momentum_y": Fraction(0),
    }
    radius_alignment = bool(
        outer_base == OUTER_BASE_RADIUS
        and outer_normal == OUTER_NORMAL_RADIUS
        and _fraction_from_record(an_parameters["base_radius"])
        == OUTER_BASE_RADIUS
        and _fraction_from_record(an_parameters["normal_radius"])
        == OUTER_NORMAL_RADIUS
    )
    inner_scaling = bool(
        INITIAL_BASE_RADIUS == 100 * Fraction(89_998, 10**23)
        and INITIAL_NORMAL_RADIUS
        == 10 * Fraction(4_999_999_999, 10**21)
    )
    strict_subset = bool(
        0 <= INITIAL_BASE_RADIUS < OUTER_BASE_RADIUS < analytic_radius
        and 0 <= INITIAL_NORMAL_RADIUS < OUTER_NORMAL_RADIUS
    )
    target_alignment = bool(am_target == target and an_target == target)
    repair_alignment = bool(
        _fraction_from_record(am_parameters["repair_quantum"])
        == q007y.REPAIR_QUANTUM
        and _fraction_from_record(an_parameters["repair_quantum"])
        == q007y.REPAIR_QUANTUM
        and am_parameters["diagonal_populations"]
        == list(q007y.DIAGONAL_POPULATIONS)
        and an_parameters["diagonal_populations"]
        == list(q007y.DIAGONAL_POPULATIONS)
    )
    passed = bool(
        radius_alignment
        and inner_scaling
        and strict_subset
        and target_alignment
        and repair_alignment
        and selected["passed"]
        and all(selected["gates"].values())
    )
    return {
        "outer_base_radius": _fraction_record(outer_base),
        "outer_normal_radius": _fraction_record(outer_normal),
        "initial_base_radius": _fraction_record(INITIAL_BASE_RADIUS),
        "initial_normal_radius": _fraction_record(INITIAL_NORMAL_RADIUS),
        "base_inward_margin": _fraction_record(BASE_INWARD_MARGIN),
        "normal_inward_margin": _fraction_record(NORMAL_INWARD_MARGIN),
        "analytic_base_radius": _fraction_record(analytic_radius),
        "old_q007aa_radius_scaling": {
            "base_factor": 100,
            "normal_factor": 10,
            "passed": inner_scaling,
        },
        "fixed_leaf_target": {
            name: _fraction_record(value) for name, value in target.items()
        },
        "radius_alignment": radius_alignment,
        "registered_inner_set_is_strict_subset": strict_subset,
        "fixed_leaf_target_alignment": target_alignment,
        "repair_lattice_and_distribution_alignment": repair_alignment,
        "passed": passed,
    }


def _exact_input_constants(
    payloads: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    ag = payloads["q007ag"]["cycle"]
    am = payloads["q007am"]["cycle"]
    an = payloads["q007an"]["cycle"]
    selected = ag["selection"]["selected_candidate"]
    repair_bound = am["tube_wide_repair_bound"]
    input_bound = repair_bound["input_encoding"]
    raw = _fraction_from_record(input_bound["mass_defect_upper"])
    momentum_x = _fraction_from_record(
        input_bound["momentum_x_defect_upper"]
    )
    momentum_y = _fraction_from_record(
        input_bound["momentum_y_defect_upper"]
    )
    repair = _fraction_from_record(input_bound["repair_l1_upper"])
    total = raw + repair
    selected_analysis = _fraction_from_record(
        repair_bound["selected_analysis_upper"]
    )
    external_analysis = _fraction_from_record(
        repair_bound["external_analysis_upper"]
    )
    chart_derivative = _fraction_from_record(
        selected["chart_derivative"]
    )
    population_error_sum = sum(
        (
            _fraction_from_record(record["component_error_upper"])
            for record in input_bound["population_records"]
        ),
        Fraction(0),
    )
    repair_ready = bool(
        input_bound["passed"]
        and input_bound["all_raw_population_binades_pass"]
        and input_bound[
            "all_population_lattices_contain_repair_quantum"
        ]
        and input_bound["non_diagonal_lattice_units_even"]
        and input_bound["target_parity_compatible"]
        and input_bound[
            "repaired_diagonal_binade_and_positivity_passed"
        ]
        and repair_bound[
            "repair_map_well_defined_on_registered_component_tube"
        ]
        and am["theorem_consequence"][
            "distributed_repair_is_defined_on_q007ag_component_tube"
        ]
    )
    induction_ready = bool(
        an["hypothesis_outcome"] == "accepted"
        and an["theorem_consequence"][
            "conditional_all_iterate_repaired_mpfr85_q007ag_tube_invariance"
        ]
        and an["theorem_consequence"][
            "conditional_all_iterate_mpfr85_internal_stage_positivity"
        ]
    )
    observed_floats = {
        "raw_encoding_wiener_upper": float(raw),
        "repair_wiener_upper": float(repair),
        "total_encoding_repair_wiener_upper": float(total),
        "selected_analysis_upper": float(selected_analysis),
        "external_analysis_upper": float(external_analysis),
        "chart_derivative_upper": float(chart_derivative),
    }
    registered_floats = {
        key: REGISTERED_FLOATS[key] for key in observed_floats
    }
    arithmetic = {
        "raw_wiener_is_wave_count_times_population_error_sum": (
            raw == WAVE_COUNT * population_error_sum
        ),
        "repair_is_mass_momentum_plus_two_quanta": (
            repair
            == raw
            + momentum_x
            + momentum_y
            + 2 * q007y.REPAIR_QUANTUM
        ),
        "total_is_raw_plus_repair": total == raw + repair,
        "analysis_constants_match_q007am": bool(
            selected_analysis
            == _fraction_from_record(
                repair_bound["selected_analysis_upper"]
            )
            and external_analysis
            == _fraction_from_record(
                repair_bound["external_analysis_upper"]
            )
        ),
        "chart_derivative_matches_q007ag_selected_candidate": bool(
            chart_derivative
            == _fraction_from_record(selected["chart_derivative"])
        ),
    }
    passed = bool(
        all(arithmetic.values())
        and observed_floats == registered_floats
        and repair_ready
        and induction_ready
    )
    exact: dict[str, Fraction | bool] = {
        "raw": raw,
        "repair": repair,
        "total": total,
        "selected_analysis": selected_analysis,
        "external_analysis": external_analysis,
        "chart_derivative": chart_derivative,
        "repair_ready": repair_ready,
        "induction_ready": induction_ready,
    }
    return {
        "raw_encoding_wiener_upper": _fraction_record(raw),
        "momentum_x_defect_upper": _fraction_record(momentum_x),
        "momentum_y_defect_upper": _fraction_record(momentum_y),
        "repair_wiener_upper": _fraction_record(repair),
        "total_encoding_repair_wiener_upper": _fraction_record(total),
        "selected_analysis_upper": _fraction_record(selected_analysis),
        "external_analysis_upper": _fraction_record(external_analysis),
        "chart_derivative_upper": _fraction_record(chart_derivative),
        "repair_quantum": _fraction_record(q007y.REPAIR_QUANTUM),
        "input_maximum_site_correction_upper": input_bound[
            "maximum_site_correction_upper"
        ],
        "repair_input_bound_passed": input_bound["passed"],
        "repair_is_tube_wide_lattice_defined_positive_and_exact": (
            repair_ready
        ),
        "q007an_conditional_induction_ready": induction_ready,
        "coarse_bound_uses_center_cancellation": False,
        "coarse_bound_uses_spatial_fourier_phase": False,
        "q007z_selected_wave_bound_used": False,
        "arithmetic_identities": arithmetic,
        "all_arithmetic_identities_pass": all(arithmetic.values()),
        "registered_float_values": registered_floats,
        "observed_float_values": observed_floats,
        "registered_float_values_match": (
            observed_floats == registered_floats
        ),
        "passed": passed,
    }, exact


def _initialization_bound(
    exact: dict[str, Fraction | bool],
) -> dict[str, Any]:
    raw = exact["raw"]
    repair = exact["repair"]
    total = exact["total"]
    selected_analysis = exact["selected_analysis"]
    external_analysis = exact["external_analysis"]
    chart_derivative = exact["chart_derivative"]
    assert all(
        isinstance(value, Fraction)
        for value in (
            raw,
            repair,
            total,
            selected_analysis,
            external_analysis,
            chart_derivative,
        )
    )
    base_increment = selected_analysis * total
    direct_external = external_analysis * total
    graph_shift = (
        external_analysis * chart_derivative * base_increment
    )
    normal_increment = direct_external + graph_shift
    encoded_base = INITIAL_BASE_RADIUS + base_increment
    encoded_normal = INITIAL_NORMAL_RADIUS + normal_increment
    tight_base = OUTER_BASE_RADIUS - base_increment
    tight_normal = OUTER_NORMAL_RADIUS - normal_increment
    base_headroom = BASE_INWARD_MARGIN - base_increment
    normal_headroom = NORMAL_INWARD_MARGIN - normal_increment
    observed_floats = {
        "outer_base_radius": float(OUTER_BASE_RADIUS),
        "initial_base_radius": float(INITIAL_BASE_RADIUS),
        "base_inward_margin": float(BASE_INWARD_MARGIN),
        "outer_normal_radius": float(OUTER_NORMAL_RADIUS),
        "initial_normal_radius": float(INITIAL_NORMAL_RADIUS),
        "normal_inward_margin": float(NORMAL_INWARD_MARGIN),
        "base_coordinate_increment_upper": float(base_increment),
        "base_headroom": float(base_headroom),
        "base_margin_utilization": float(
            base_increment / BASE_INWARD_MARGIN
        ),
        "direct_external_coordinate_increment_upper": float(
            direct_external
        ),
        "graph_shift_external_coordinate_increment_upper": float(
            graph_shift
        ),
        "normal_coordinate_increment_upper": float(normal_increment),
        "normal_headroom": float(normal_headroom),
        "normal_margin_utilization": float(
            normal_increment / NORMAL_INWARD_MARGIN
        ),
        "tight_base_initialization_radius": float(tight_base),
        "tight_normal_initialization_radius": float(tight_normal),
    }
    registered_floats = {
        key: REGISTERED_FLOATS[key] for key in observed_floats
    }
    arithmetic = {
        "total_is_raw_plus_repair": total == raw + repair,
        "base_increment_is_analysis_times_total_wiener": (
            base_increment == selected_analysis * total
        ),
        "normal_increment_includes_direct_and_graph_shift": (
            normal_increment
            == external_analysis
            * (total + chart_derivative * base_increment)
        ),
        "base_margin_is_outer_minus_inner": (
            BASE_INWARD_MARGIN
            == OUTER_BASE_RADIUS - INITIAL_BASE_RADIUS
        ),
        "normal_margin_is_outer_minus_inner": (
            NORMAL_INWARD_MARGIN
            == OUTER_NORMAL_RADIUS - INITIAL_NORMAL_RADIUS
        ),
        "tight_radii_are_outer_minus_increment": bool(
            tight_base == OUTER_BASE_RADIUS - base_increment
            and tight_normal == OUTER_NORMAL_RADIUS - normal_increment
        ),
    }
    base_passed = base_increment < BASE_INWARD_MARGIN
    normal_passed = normal_increment < NORMAL_INWARD_MARGIN
    membership = bool(
        encoded_base < OUTER_BASE_RADIUS
        and encoded_normal < OUTER_NORMAL_RADIUS
    )
    passed = bool(
        all(arithmetic.values())
        and observed_floats == registered_floats
        and base_passed
        and normal_passed
        and membership
    )
    return {
        "arithmetic": "exact fractions.Fraction",
        "outer_base_radius": _fraction_record(OUTER_BASE_RADIUS),
        "initial_base_radius": _fraction_record(INITIAL_BASE_RADIUS),
        "base_inward_margin": _fraction_record(BASE_INWARD_MARGIN),
        "outer_normal_radius": _fraction_record(OUTER_NORMAL_RADIUS),
        "initial_normal_radius": _fraction_record(INITIAL_NORMAL_RADIUS),
        "normal_inward_margin": _fraction_record(NORMAL_INWARD_MARGIN),
        "raw_encoding_wiener_upper": _fraction_record(raw),
        "repair_wiener_upper": _fraction_record(repair),
        "total_encoding_repair_wiener_upper": _fraction_record(total),
        "base_coordinate_increment_upper": _fraction_record(base_increment),
        "direct_external_coordinate_increment_upper": _fraction_record(
            direct_external
        ),
        "graph_shift_external_coordinate_increment_upper": _fraction_record(
            graph_shift
        ),
        "normal_coordinate_increment_upper": _fraction_record(
            normal_increment
        ),
        "encoded_repaired_base_radius_upper": _fraction_record(
            encoded_base
        ),
        "encoded_repaired_normal_radius_upper": _fraction_record(
            encoded_normal
        ),
        "tight_base_initialization_radius": _fraction_record(tight_base),
        "tight_normal_initialization_radius": _fraction_record(
            tight_normal
        ),
        "base_headroom": _fraction_record(base_headroom),
        "normal_headroom": _fraction_record(normal_headroom),
        "base_inward_margin_utilization": _fraction_record(
            base_increment / BASE_INWARD_MARGIN
        ),
        "normal_inward_margin_utilization": _fraction_record(
            normal_increment / NORMAL_INWARD_MARGIN
        ),
        "formulae": {
            "total_physical_error": "E_W=E_raw+E_rep",
            "base_increment": "epsilon_a=K_L*E_W",
            "normal_increment": (
                "epsilon_z=K_a*(E_W+dH(r)*epsilon_a)"
            ),
        },
        "arithmetic_identities": arithmetic,
        "all_arithmetic_identities_pass": all(arithmetic.values()),
        "registered_float_values": registered_floats,
        "observed_float_values": observed_floats,
        "registered_float_values_match": (
            observed_floats == registered_floats
        ),
        "base_inward_margin_passed": base_passed,
        "normal_inward_margin_passed": normal_passed,
        "encoded_repaired_membership_passed": membership,
        "passed": passed,
    }


def run_initialization_interior_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    reproduction = _fresh_q007an_reproduction(directory, payloads)
    alignment = _scope_alignment(payloads)
    constants, exact = _exact_input_constants(payloads)
    bound = _initialization_bound(exact)

    registered_parameters = {
        "size": SIZE,
        "wave_count": WAVE_COUNT,
        "precision_bits": PRECISION_BITS,
        "outer_base_radius": _fraction_record(OUTER_BASE_RADIUS),
        "outer_normal_radius": _fraction_record(OUTER_NORMAL_RADIUS),
        "initial_base_radius": _fraction_record(INITIAL_BASE_RADIUS),
        "initial_normal_radius": _fraction_record(INITIAL_NORMAL_RADIUS),
        "base_inward_margin": _fraction_record(BASE_INWARD_MARGIN),
        "normal_inward_margin": _fraction_record(NORMAL_INWARD_MARGIN),
        "target_conserved": {
            name: _fraction_record(value)
            for name, value in (
                ("mass", Fraction(WAVE_COUNT)),
                ("momentum_x", Fraction(0)),
                ("momentum_y", Fraction(0)),
            )
        },
        "encoding": "componentwise MPFR-85 round-to-nearest",
        "repair_quantum": _fraction_record(q007y.REPAIR_QUANTUM),
        "diagonal_populations": list(q007y.DIAGONAL_POPULATIONS),
        "repair_distribution": "Python divmod over 289 row-major sites",
        "selected_wave_certificate_used": False,
    }
    input_digest = _canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "registered_parameters": registered_parameters,
        }
    )
    bound_sections = {
        "fresh_q007an_reproduction": reproduction,
        "scope_alignment": alignment,
        "exact_input_constants": constants,
        "initialization_bound": bound,
    }
    bound_digest = _canonical_json_sha256(bound_sections)
    strict_json = bool(
        _all_numeric_values_finite(bound_sections)
        and _strict_json_serializable(bound_sections)
    )
    digest_reproduction = bool(
        input_digest
        == _canonical_json_sha256(
            {
                "input_artifacts": input_records,
                "registered_parameters": registered_parameters,
            }
        )
        and bound_digest == _canonical_json_sha256(bound_sections)
    )
    input_passed = all(
        record["passed"] for record in input_records.values()
    )
    repair_ready = bool(exact["repair_ready"])
    induction_ready = bool(exact["induction_ready"])
    validity_gates = {
        "sealed_inputs_sources_scopes_outcomes_gates_and_digests": {
            "passed": input_passed,
            "threshold": (
                "Q007ag/Q007am/Q007an artifact and runner SHA values, "
                "source/scope, accepted outcomes, gate counts, and digests "
                "match"
            ),
            "value": input_passed,
        },
        "fresh_q007an_and_transitive_upstream_reproduction": {
            "passed": reproduction["passed"],
            "threshold": (
                "Q007an replays exactly with all transitive Q007ag/Q007ai/"
                "Q007al/Q007am/Q007y reproductions"
            ),
            "value": reproduction["passed"],
        },
        "fixed_leaf_outer_tube_coordinates_backend_and_repair_align": {
            "passed": alignment["passed"],
            "threshold": (
                "fixed leaf, outer/inner radii, graph/external coordinates, "
                "MPFR backend, and repair distribution align"
            ),
            "value": alignment["passed"],
        },
        "q007am_input_encoding_and_repair_bound_reproduced": {
            "passed": constants["passed"],
            "threshold": (
                "Q007am input rounding and repair bounds, transform "
                "constants, lattice, positivity, and exact fixed-leaf "
                "restoration reproduce"
            ),
            "value": constants["passed"],
        },
        "exact_coordinate_increment_arithmetic_reproduced": {
            "passed": bool(
                bound["all_arithmetic_identities_pass"]
                and bound["registered_float_values_match"]
            ),
            "threshold": (
                "base/direct-external/graph-shift formulae and registered "
                "inner margins reproduce with exact rational arithmetic"
            ),
            "value": {
                "arithmetic": bound[
                    "all_arithmetic_identities_pass"
                ],
                "registered_floats": bound[
                    "registered_float_values_match"
                ],
            },
        },
        "encoded_repaired_state_strictly_enters_q007ag_tube": {
            "passed": bound["passed"],
            "threshold": (
                "encoded/repaired base and normal radii remain strictly "
                "below the Q007ag outer radii"
            ),
            "value": bound["passed"],
        },
        "finite_strict_json_and_digests": {
            "passed": bool(strict_json and digest_reproduction),
            "threshold": (
                "all records are finite strict JSON and input/bound "
                "digests reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests_reproducible": digest_reproduction,
            },
        },
    }
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )
    strict_inner = alignment["registered_inner_set_is_strict_subset"]
    base_passed = bound["base_inward_margin_passed"]
    normal_passed = bound["normal_inward_margin_passed"]
    membership = bound["encoded_repaired_membership_passed"]
    initialized_induction = bool(
        validity_passed
        and strict_inner
        and repair_ready
        and base_passed
        and normal_passed
        and membership
        and induction_ready
    )
    hypothesis_gates = {
        "registered_exact_state_inner_set_is_strict_subset": {
            "passed": bool(validity_passed and strict_inner),
            "threshold": (
                "the preregistered exact-state coordinate set is a strict "
                "subset of the Q007ag tube and analytic base radius"
            ),
            "value": strict_inner,
        },
        "mpfr85_input_repair_is_tube_wide_exact_positive_and_representable": {
            "passed": bool(validity_passed and repair_ready),
            "threshold": (
                "componentwise encoding repair is lattice-defined, "
                "positive, exact fixed-leaf restoring, and MPFR-85 "
                "representable"
            ),
            "value": repair_ready,
        },
        "base_encoding_repair_increment_fits_inward_margin": {
            "passed": bool(validity_passed and base_passed),
            "threshold": "epsilon_a < r-r0",
            "value": base_passed,
        },
        "normal_encoding_repair_increment_fits_inward_margin": {
            "passed": bool(validity_passed and normal_passed),
            "threshold": "epsilon_z < zeta-zeta0 including graph shift",
            "value": normal_passed,
        },
        "encoded_repaired_initial_state_enters_q007ag_tube": {
            "passed": bool(validity_passed and membership),
            "threshold": (
                "both encoded/repaired coordinate radii are strictly "
                "inside the Q007ag tube"
            ),
            "value": membership,
        },
        "exact_state_initialization_closes_q007an_induction": {
            "passed": initialized_induction,
            "threshold": (
                "initial membership composes with the sealed Q007an "
                "conditional induction"
            ),
            "value": initialized_induction,
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered Q007ao initialization-interior audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered propagated-tube exact-state interior survives "
            "MPFR-85 encoding and repair"
        )
    elif not base_passed or not normal_passed:
        outcome = "not_certified"
        classification = (
            "registered Q007ao initialization interior is too shallow for "
            "encoding and repair"
        )
    else:
        outcome = "not_certified"
        classification = (
            "exact-state initialization does not connect to the Q007an "
            "repaired induction"
        )

    result_sections = {
        **bound_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = _canonical_json_sha256(result_sections)
    return {
        "question": (
            "Does componentwise MPFR-85 encoding followed by the sealed "
            "row-major repair send the preregistered exact-state inner set "
            "strictly into the Q007ag repaired fixed-leaf tube?"
        ),
        "registered_parameters": registered_parameters,
        "input_artifacts": input_records,
        **bound_sections,
        "input_digest_sha256": input_digest,
        "bound_digest_sha256": bound_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_exact_state_inner_set_is_certified": bool(
                hypotheses_passed
            ),
            "initial_encoding_and_repair_enter_q007ag_tube": bool(
                hypotheses_passed
            ),
            "initial_repair_restores_exact_fixed_leaf": bool(
                hypotheses_passed
            ),
            "all_iterate_repaired_mpfr85_q007ag_tube_invariance_from_inner_set": (
                bool(hypotheses_passed)
            ),
            "all_iterate_mpfr85_internal_stage_positivity_from_inner_set": (
                bool(hypotheses_passed)
            ),
            "arbitrary_q007ag_boundary_state_initialization_certified": False,
            "same_initial_q007ag_forward_shadowing_certified": False,
        },
        "claim_boundary": (
            "The certificate applies only to exact fixed-leaf states in the "
            "preregistered strict inner graph/external-coordinate set on the "
            "sealed 17x17 model. It uses componentwise MPFR-85 "
            "round-to-nearest and the Q007y row-major h=2^-90 repair, then "
            "composes membership with Q007an. The coarse bound uses no "
            "center cancellation, spatial Fourier phase, or Q007z "
            "selected-wave result. It does not certify arbitrary Q007ag "
            "boundary states, arbitrary exact physical states, same-initial "
            "shadowing or trajectory error, performance, GPU or parallel "
            "reduction behavior, another grid or MPFR build, grid "
            "uniformity, a continuum limit, or D3Q27."
        ),
        "preserved_prior_outcomes": {
            "q007aa_old_tube_initialization_changed": False,
            "q007an_conditional_induction_changed": False,
            "q007am_one_step_repair_result_changed": False,
            "q007z_selected_wave_result_changed": False,
            "q007aj_binary64_reentry_rejection_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q010_tt_cost_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister Q007ap to transfer the Q007ab "
            "fixed-coordinate contraction and local-defect bound to the "
            "Q007ag tube and Q007ao initial set for same-initial repaired-"
            "MPFR forward shadowing."
        ),
    }


def run_q007ao_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_initialization_interior_audit(artifact_directory)
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
                "propagated-tube exact-state MPFR-85 encoding and "
                "conservation-repair initialization-interior certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(q007y.backend.EXACT_OMEGA),
            "eta": float(q007y.backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "input repair"
            ),
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "outer_base_modal_l1_radius": float(OUTER_BASE_RADIUS),
            "outer_normal_coordinate_radius": float(
                OUTER_NORMAL_RADIUS
            ),
            "initial_base_modal_l1_radius": float(
                INITIAL_BASE_RADIUS
            ),
            "initial_normal_coordinate_radius": float(
                INITIAL_NORMAL_RADIUS
            ),
            "repair_lattice": "four diagonal populations on h=2^-90",
            "rounding_model": (
                "sealed Q007x gmpy2 2.3.1 / MPFR 4.2.2 nearest-even backend"
            ),
            "claim": (
                "strict initialization interior composed with Q007an "
                "all-iterate invariance, excluding same-initial shadowing"
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
    result = run_q007ao_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
