"""Sealed Q007aa exact-state encoding initialization-interior audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q007s_finite_tube_enlargement as q007s
import research.q007x_mpfr_backend as backend
import research.q007y_distributed_conservation_repair as q007y
import research.q007z_selected_wave_repair as q007z
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = q007y.SIZE
WAVE_COUNT = q007y.WAVE_COUNT
REPAIR_QUANTUM = q007y.REPAIR_QUANTUM

OUTER_BASE_RADIUS = Fraction(9, 10**19)
OUTER_NORMAL_RADIUS = Fraction(5, 10**12)
INITIAL_BASE_RADIUS = Fraction(89_998, 10**23)
INITIAL_NORMAL_RADIUS = Fraction(4_999_999_999, 10**21)
REGISTERED_BASE_INWARD_MARGIN = OUTER_BASE_RADIUS - INITIAL_BASE_RADIUS
REGISTERED_NORMAL_INWARD_MARGIN = (
    OUTER_NORMAL_RADIUS - INITIAL_NORMAL_RADIUS
)

Q007S_ARTIFACT = "q007s_finite_tube_enlargement.json"
Q007Y_ARTIFACT = "q007y_distributed_conservation_repair.json"
Q007Z_ARTIFACT = "q007z_selected_wave_repair.json"

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
        "passing_hypothesis_count": 5,
        "fresh": None,
    },
    "q007y": {
        "filename": Q007Y_ARTIFACT,
        "artifact_sha256": (
            "a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648"
        ),
        "runner_sha256": (
            "ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811"
        ),
        "module": q007y,
        "diagnostic": (
            "distributed dyadic fixed-leaf repair and repair-aware "
            "Wiener-budget audit"
        ),
        "outcome": "not_certified",
        "validity_count": 8,
        "hypothesis_count": 7,
        "passing_hypothesis_count": 5,
        "fresh": q007y.run_distributed_repair_audit,
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
        "passing_hypothesis_count": 7,
        "fresh": q007z.run_selected_wave_repair_audit,
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
    hypothesis_gates = cycle.get("hypothesis_gates", {})
    fresh_runner = specification["fresh"]
    fresh_cycle_matches = True
    if isinstance(fresh_runner, Callable):
        fresh_cycle_matches = fresh_runner(directory) == cycle
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
        "hypothesis_gate_count": len(hypothesis_gates),
        "passing_hypothesis_gate_count": sum(
            bool(gate.get("passed", False))
            for gate in hypothesis_gates.values()
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
        and record["passing_hypothesis_gate_count"]
        == specification["passing_hypothesis_count"]
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
    audit = {
        "artifacts": records,
        "passed": all(record["passed"] for record in records.values()),
    }
    return payloads, audit


def _exact_constants(
    payloads: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    q007s_cycle = payloads["q007s"]["cycle"]
    candidate = q007s_cycle["selection"]["selected_candidate"]
    constants = q007s_cycle["constant_reuse_audit"]["constants"]
    q007y_cycle = payloads["q007y"]["cycle"]
    input_bound = q007y_cycle["tube_wide_repair_bound"]["input_encoding"]
    q007z_cycle = payloads["q007z"]["cycle"]
    selected_bound = q007z_cycle["selected_repair_bound"]

    outer_base = _fraction_from_record(candidate["base_radius"])
    outer_normal = _fraction_from_record(candidate["normal_radius"])
    rho = _fraction_from_record(constants["rho"])
    tau = _fraction_from_record(constants["tau"])
    h2 = _fraction_from_record(constants["h2"])
    h3 = _fraction_from_record(constants["h3"])
    h4 = _fraction_from_record(constants["h4"])
    selected_analysis = _fraction_from_record(
        constants["selected_analysis"]
    )
    external_analysis = _fraction_from_record(constants["analysis"])
    registered_chart_derivative = _fraction_from_record(
        candidate["chart_derivative"]
    )
    raw_encoding = _fraction_from_record(input_bound["mass_defect_upper"])
    momentum_x = _fraction_from_record(
        input_bound["momentum_x_defect_upper"]
    )
    momentum_y = _fraction_from_record(
        input_bound["momentum_y_defect_upper"]
    )
    repair_physical = _fraction_from_record(input_bound["repair_l1_upper"])
    repair_selected = _fraction_from_record(
        selected_bound["repair_base_coordinate_error_upper"]
    )
    population_error_sum = sum(
        (
            _fraction_from_record(record["component_error_upper"])
            for record in input_bound["population_records"]
        ),
        Fraction(0),
    )
    selected_structure = q007z_cycle["selected_structure"]
    repair_ready = bool(
        input_bound["passed"]
        and input_bound["all_population_lattices_contain_repair_quantum"]
        and input_bound["target_parity_compatible"]
        and input_bound[
            "repaired_diagonal_binade_and_positivity_passed"
        ]
        and q007y_cycle["tube_wide_repair_bound"][
            "repair_map_well_defined_on_registered_tube"
        ]
    )
    conditional_induction = bool(
        all(q007z_cycle["theorem_consequence"].values())
        and q007z_cycle["hypothesis_outcome"] == "accepted"
    )
    arithmetic_passed = bool(
        outer_base == OUTER_BASE_RADIUS
        and outer_normal == OUTER_NORMAL_RADIUS
        and raw_encoding == WAVE_COUNT * population_error_sum
        and repair_physical
        == raw_encoding + momentum_x + momentum_y + 2 * REPAIR_QUANTUM
        and selected_bound["passed"]
        and selected_structure["selected_wave_count"] == 8
        and selected_structure["zero_wave_excluded"]
        and candidate["passed"]
        and all(candidate["gates"].values())
        and repair_ready
        and conditional_induction
    )
    exact: dict[str, Fraction | bool] = {
        "outer_base": outer_base,
        "outer_normal": outer_normal,
        "rho": rho,
        "tau": tau,
        "h2": h2,
        "h3": h3,
        "h4": h4,
        "selected_analysis": selected_analysis,
        "external_analysis": external_analysis,
        "registered_chart_derivative": registered_chart_derivative,
        "raw_encoding": raw_encoding,
        "momentum_x": momentum_x,
        "momentum_y": momentum_y,
        "repair_physical": repair_physical,
        "repair_selected": repair_selected,
        "repair_ready": repair_ready,
        "conditional_induction": conditional_induction,
        "arithmetic_passed": arithmetic_passed,
    }
    section = {
        "outer_base_radius": _fraction_record(outer_base),
        "outer_normal_radius": _fraction_record(outer_normal),
        "analytic_base_radius": _fraction_record(rho),
        "correction_pair_radius_tau": _fraction_record(tau),
        "h2": _fraction_record(h2),
        "h3": _fraction_record(h3),
        "h4": _fraction_record(h4),
        "selected_analysis_upper": _fraction_record(selected_analysis),
        "external_analysis_upper": _fraction_record(external_analysis),
        "registered_chart_derivative_upper": _fraction_record(
            registered_chart_derivative
        ),
        "input_raw_encoding_wiener_upper": _fraction_record(raw_encoding),
        "input_momentum_x_defect_upper": _fraction_record(momentum_x),
        "input_momentum_y_defect_upper": _fraction_record(momentum_y),
        "input_repair_physical_wiener_upper": _fraction_record(
            repair_physical
        ),
        "input_repair_selected_base_upper": _fraction_record(
            repair_selected
        ),
        "input_raw_wiener_formula_reproduced": (
            raw_encoding == WAVE_COUNT * population_error_sum
        ),
        "input_repair_l1_formula_reproduced": (
            repair_physical
            == raw_encoding + momentum_x + momentum_y + 2 * REPAIR_QUANTUM
        ),
        "q007y_tube_wide_input_repair_ready": repair_ready,
        "q007z_conditional_induction_ready": conditional_induction,
        "passed": arithmetic_passed,
    }
    return section, exact


def _initialization_bound(
    exact: dict[str, Fraction | bool],
) -> dict[str, Any]:
    outer_base = exact["outer_base"]
    outer_normal = exact["outer_normal"]
    rho = exact["rho"]
    tau = exact["tau"]
    h2 = exact["h2"]
    h3 = exact["h3"]
    h4 = exact["h4"]
    selected_analysis = exact["selected_analysis"]
    external_analysis = exact["external_analysis"]
    registered_chart_derivative = exact["registered_chart_derivative"]
    raw_encoding = exact["raw_encoding"]
    repair_physical = exact["repair_physical"]
    repair_selected = exact["repair_selected"]
    assert all(
        isinstance(value, Fraction)
        for value in (
            outer_base,
            outer_normal,
            rho,
            tau,
            h2,
            h3,
            h4,
            selected_analysis,
            external_analysis,
            registered_chart_derivative,
            raw_encoding,
            repair_physical,
            repair_selected,
        )
    )

    total_physical = raw_encoding + repair_physical
    raw_base = selected_analysis * raw_encoding
    base_increment = raw_base + repair_selected
    polynomial_derivative = (
        2 * h2 * outer_base
        + 3 * h3 * outer_base**2
        + 4 * h4 * outer_base**3
    )
    correction_derivative = tau / (rho - outer_base)
    chart_derivative = polynomial_derivative + correction_derivative
    direct_external = external_analysis * total_physical
    graph_shift_external = (
        external_analysis * chart_derivative * base_increment
    )
    normal_increment = direct_external + graph_shift_external
    tight_base_radius = outer_base - base_increment
    tight_normal_radius = outer_normal - normal_increment
    encoded_base_radius = INITIAL_BASE_RADIUS + base_increment
    encoded_normal_radius = INITIAL_NORMAL_RADIUS + normal_increment

    arithmetic_passed = bool(
        total_physical == raw_encoding + repair_physical
        and base_increment == raw_base + repair_selected
        and chart_derivative
        == 2 * h2 * outer_base
        + 3 * h3 * outer_base**2
        + 4 * h4 * outer_base**3
        + tau / (rho - outer_base)
        and normal_increment
        == external_analysis
        * (total_physical + chart_derivative * base_increment)
        and REGISTERED_BASE_INWARD_MARGIN
        == outer_base - INITIAL_BASE_RADIUS
        and REGISTERED_NORMAL_INWARD_MARGIN
        == outer_normal - INITIAL_NORMAL_RADIUS
    )
    base_passed = base_increment < REGISTERED_BASE_INWARD_MARGIN
    normal_passed = normal_increment < REGISTERED_NORMAL_INWARD_MARGIN
    line_segment_passed = bool(
        INITIAL_BASE_RADIUS + base_increment < outer_base < rho
    )
    membership_passed = bool(
        encoded_base_radius < outer_base
        and encoded_normal_radius < outer_normal
    )
    return {
        "arithmetic": "exact fractions.Fraction",
        "initial_base_radius": _fraction_record(INITIAL_BASE_RADIUS),
        "initial_normal_radius": _fraction_record(INITIAL_NORMAL_RADIUS),
        "registered_base_inward_margin": _fraction_record(
            REGISTERED_BASE_INWARD_MARGIN
        ),
        "registered_normal_inward_margin": _fraction_record(
            REGISTERED_NORMAL_INWARD_MARGIN
        ),
        "raw_encoding_wiener_upper": _fraction_record(raw_encoding),
        "repair_physical_wiener_upper": _fraction_record(repair_physical),
        "total_encoding_repair_wiener_upper": _fraction_record(
            total_physical
        ),
        "raw_base_coordinate_increment_upper": _fraction_record(raw_base),
        "repair_base_coordinate_increment_upper": _fraction_record(
            repair_selected
        ),
        "base_coordinate_increment_upper": _fraction_record(base_increment),
        "chart_polynomial_derivative_at_outer_base_upper": _fraction_record(
            polynomial_derivative
        ),
        "chart_correction_derivative_at_outer_base_upper": _fraction_record(
            correction_derivative
        ),
        "chart_derivative_at_outer_base_upper": _fraction_record(
            chart_derivative
        ),
        "chart_derivative_dominates_registered_value": (
            chart_derivative >= registered_chart_derivative
        ),
        "direct_external_coordinate_increment_upper": _fraction_record(
            direct_external
        ),
        "graph_shift_external_coordinate_increment_upper": _fraction_record(
            graph_shift_external
        ),
        "normal_coordinate_increment_upper": _fraction_record(
            normal_increment
        ),
        "tight_base_initialization_radius": _fraction_record(
            tight_base_radius
        ),
        "tight_normal_initialization_radius": _fraction_record(
            tight_normal_radius
        ),
        "encoded_repaired_base_radius_upper": _fraction_record(
            encoded_base_radius
        ),
        "encoded_repaired_normal_radius_upper": _fraction_record(
            encoded_normal_radius
        ),
        "base_inward_margin_utilization": _fraction_record(
            base_increment / REGISTERED_BASE_INWARD_MARGIN
        ),
        "normal_inward_margin_utilization": _fraction_record(
            normal_increment / REGISTERED_NORMAL_INWARD_MARGIN
        ),
        "base_headroom": _fraction_record(
            REGISTERED_BASE_INWARD_MARGIN - base_increment
        ),
        "normal_headroom": _fraction_record(
            REGISTERED_NORMAL_INWARD_MARGIN - normal_increment
        ),
        "formulae": {
            "total_physical_error": "E_W=E_raw+E_rep",
            "base_increment": "epsilon_a=K_L*E_raw+B_rep_selected",
            "chart_derivative": (
                "dH(r)=2*h2*r+3*h3*r^2+4*h4*r^3+tau/(rho-r)"
            ),
            "normal_increment": (
                "epsilon_z=K_a*(E_W+dH(r)*epsilon_a)"
            ),
        },
        "exact_arithmetic_identities_passed": arithmetic_passed,
        "base_inward_margin_passed": base_passed,
        "normal_inward_margin_passed": normal_passed,
        "base_line_segment_stays_in_outer_ball": line_segment_passed,
        "encoded_repaired_membership_passed": membership_passed,
        "passed": bool(
            arithmetic_passed
            and base_passed
            and normal_passed
            and line_segment_passed
            and membership_passed
        ),
    }


def run_initialization_interior_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_audit = _load_registered_inputs(directory)
    constants, exact = _exact_constants(payloads)
    bound = _initialization_bound(exact)
    q007y_cycle = payloads["q007y"]["cycle"]
    q007z_cycle = payloads["q007z"]["cycle"]

    input_repair_ready = bool(exact["repair_ready"])
    conditional_induction_ready = bool(exact["conditional_induction"])
    initial_subset = bool(
        0 <= INITIAL_BASE_RADIUS < OUTER_BASE_RADIUS
        and 0 <= INITIAL_NORMAL_RADIUS < OUTER_NORMAL_RADIUS
        and OUTER_BASE_RADIUS < exact["rho"]
    )
    preliminary = {
        "input_audit": input_audit,
        "constant_reuse_audit": constants,
        "initialization_bound": bound,
    }
    strict_json = bool(
        _all_numeric_values_finite(preliminary)
        and _strict_json_serializable(preliminary)
    )
    input_digest_payload = {
        "registered_artifact_sha256": {
            name: record["sha256"]
            for name, record in input_audit["artifacts"].items()
        },
        "initial_base_radius": _fraction_record(INITIAL_BASE_RADIUS),
        "initial_normal_radius": _fraction_record(INITIAL_NORMAL_RADIUS),
        "q007y_input_bound": q007y_cycle["tube_wide_repair_bound"][
            "input_encoding"
        ],
        "q007z_selected_repair_bound": q007z_cycle[
            "selected_repair_bound"
        ],
    }
    input_digest = _digest_payload(input_digest_payload)
    result_digest = _digest_payload(
        {
            "input_digest": input_digest,
            "constants": constants,
            "bound": bound,
        }
    )
    digests_reproducible = bool(
        input_digest == _digest_payload(input_digest_payload)
        and len(input_digest) == 64
        and len(result_digest) == 64
    )

    validity_gates = {
        "registered_q007s_q007y_q007z_inputs": {
            "passed": input_audit["passed"],
            "threshold": (
                "registered artifact/runner SHA, source, scope, upstream "
                "validity, outcomes, and required fresh replays match"
            ),
            "value": input_audit["passed"],
        },
        "exact_q007s_coordinate_constants_reused": {
            "passed": constants["passed"],
            "threshold": (
                "Q007s radii, analytic constants, coordinate norms, and "
                "selected candidate gates reproduce exactly"
            ),
            "value": constants["passed"],
        },
        "q007y_tube_wide_input_repair_replayed": {
            "passed": bool(
                input_audit["artifacts"]["q007y"]["fresh_cycle_matches"]
                and input_repair_ready
            ),
            "threshold": (
                "tube-wide input binade/lattice/parity/positivity and fresh "
                "Q007y replay match"
            ),
            "value": input_repair_ready,
        },
        "q007z_selected_repair_bound_replayed": {
            "passed": bool(
                input_audit["artifacts"]["q007z"]["fresh_cycle_matches"]
                and conditional_induction_ready
            ),
            "threshold": (
                "selected waves, phase bound, accepted Q007z induction, and "
                "fresh replay match"
            ),
            "value": conditional_induction_ready,
        },
        "exact_initialization_arithmetic": {
            "passed": bound["exact_arithmetic_identities_passed"],
            "threshold": (
                "E_W, epsilon_a, dH(r), epsilon_z, tight radii, and "
                "registered inward margins reproduce as exact rationals"
            ),
            "value": bound["exact_arithmetic_identities_passed"],
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
    base_passed = bound["base_inward_margin_passed"]
    normal_passed = bound["normal_inward_margin_passed"]
    membership_passed = bound["encoded_repaired_membership_passed"]
    hypothesis_gates = {
        "registered_initialization_tube_is_strict_inner_subset": {
            "passed": bool(validity_passed and initial_subset),
            "threshold": (
                "0<=r0<r<rho and 0<=zeta0<zeta for the preregistered radii"
            ),
            "value": initial_subset,
        },
        "input_repair_is_tube_wide_exact_fixed_leaf_and_positive": {
            "passed": bool(validity_passed and input_repair_ready),
            "threshold": (
                "Q007y input repair is lattice-defined, restores the target "
                "leaf exactly, and remains positive throughout Q007s"
            ),
            "value": input_repair_ready,
        },
        "base_encoding_increment_fits_registered_inward_margin": {
            "passed": bool(
                validity_passed
                and base_passed
                and bound["base_line_segment_stays_in_outer_ball"]
            ),
            "threshold": (
                "phase-aware epsilon_a is below Delta r and the chart "
                "segment stays in the outer base ball"
            ),
            "value": base_passed,
        },
        "normal_encoding_increment_fits_registered_inward_margin": {
            "passed": bool(validity_passed and normal_passed),
            "threshold": (
                "direct external plus graph-shift epsilon_z is below "
                "Delta zeta"
            ),
            "value": normal_passed,
        },
        "encoded_repaired_state_enters_q007s_tube": {
            "passed": bool(validity_passed and membership_passed),
            "threshold": (
                "r0+epsilon_a<r and zeta0+epsilon_z<zeta"
            ),
            "value": membership_passed,
        },
        "exact_state_initialization_closes_all_iterate_induction": {
            "passed": False,
            "threshold": (
                "the five preceding hypotheses and Q007z conditional "
                "induction all pass"
            ),
            "value": False,
        },
    }
    first_five_pass = all(
        gate["passed"]
        for name, gate in hypothesis_gates.items()
        if name
        != "exact_state_initialization_closes_all_iterate_induction"
    )
    induction_passed = bool(
        validity_passed
        and first_five_pass
        and conditional_induction_ready
    )
    hypothesis_gates[
        "exact_state_initialization_closes_all_iterate_induction"
    ]["passed"] = induction_passed
    hypothesis_gates[
        "exact_state_initialization_closes_all_iterate_induction"
    ]["value"] = induction_passed
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )

    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007aa initialization audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered exact-state interior survives MPFR-85 encoding and "
            "repair"
        )
    elif not base_passed or not normal_passed:
        outcome = "not_certified"
        classification = (
            "registered initialization interior is too shallow for encoding "
            "and repair"
        )
    else:
        outcome = "not_certified"
        classification = (
            "exact-state initialization does not connect to the repaired "
            "MPFR-85 tube induction"
        )

    return {
        "question": (
            "Does the preregistered exact fixed-leaf coordinate interior "
            "remain inside Q007s after componentwise MPFR-85 encoding and "
            "the sealed balanced conservation repair?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "wave_count": WAVE_COUNT,
            "precision_bits": backend.MPFR_PRECISION_BITS,
            "repair_quantum": _fraction_record(REPAIR_QUANTUM),
            "outer_base_radius": _fraction_record(OUTER_BASE_RADIUS),
            "outer_normal_radius": _fraction_record(OUTER_NORMAL_RADIUS),
            "initial_base_radius": _fraction_record(INITIAL_BASE_RADIUS),
            "initial_normal_radius": _fraction_record(
                INITIAL_NORMAL_RADIUS
            ),
            "base_inward_margin": _fraction_record(
                REGISTERED_BASE_INWARD_MARGIN
            ),
            "normal_inward_margin": _fraction_record(
                REGISTERED_NORMAL_INWARD_MARGIN
            ),
            "initial_exact_state": (
                "x=W(a)+Uz on M=289, Px=Py=0 with ||a||_1<=r0 and "
                "||z||_*<=zeta0"
            ),
        },
        "input_audit": input_audit,
        "constant_reuse_audit": constants,
        "initialization_bound": bound,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_exact_state_interior_encodes_into_q007s_tube": bool(
                validity_passed and membership_passed
            ),
            "initial_repair_restores_exact_fixed_leaf": bool(
                validity_passed and input_repair_ready
            ),
            "all_iterate_repaired_mpfr85_q007s_tube_invariance": bool(
                validity_passed and hypotheses_passed
            ),
            "all_iterate_mpfr85_stagewise_population_positivity": bool(
                validity_passed and hypotheses_passed
            ),
        },
        "claim_boundary": (
            "This certificate applies only to exact states on the fixed "
            "M=289, Px=Py=0 leaf whose Q007s graph-gauge coordinates lie in "
            "the preregistered r0/zeta0 interior, followed by the sealed "
            "componentwise MPFR-85 encoding and row-major balanced repair on "
            "17x17. It uses a full-Wiener external perturbation bound and a "
            "selected-wave base repair bound. It does not include arbitrary "
            "Q007s boundary states, states outside the fixed leaf, trajectory "
            "accuracy or shadowing time, performance, another grid or MPFR "
            "build, center-slow coordinates, or D3Q27."
        ),
        "preserved_prior_outcomes": {
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
            "With an exact-state initialization interior now explicit, "
            "preregister a multi-step MPFR-85 versus exact-map shadowing "
            "budget without changing the invariant-tube certificate."
        ),
    }


def run_q007aa_study(
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
            **backend.backend_runtime_metadata(),
        },
        "mathematical_scope": {
            "diagnostic": (
                "exact-state MPFR-85 encoding and conservation-repair "
                "initialization-interior certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(backend.EXACT_OMEGA),
            "eta": float(backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "post-encoding repair"
            ),
            "manifold": "Q007s exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "claim": (
                "connect a preregistered exact coordinate interior to the "
                "conditional Q007z all-iterate repaired-backend induction"
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
    result = run_q007aa_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
