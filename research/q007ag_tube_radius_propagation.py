"""Sealed Q007ag propagation of the Q007ae analytic radius to a finite tube.

The Q007p/Q007s finite-tube majorant is held fixed except for the analytic
chart radius and correction-pair bound, which are replaced by the accepted
Q007ae exact boundary.  A preregistered scaled rational grid is evaluated
with the unchanged Q007s exact candidate formula.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007ae_internal_phase_resolvent as q007ae
import research.q007af_radius_step_obstruction as q007af
import research.q007n_explicit_local_radius as q007n
import research.q007o_external_complement_radius as q007o
import research.q007p_finite_tube_attraction as q007p
import research.q007s_finite_tube_enlargement as q007s
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_REAL_DIMENSION = 24
EXTERNAL_COMPLEX_DIMENSION = 2574
EXPECTED_BASE_COUNT = 9
EXPECTED_NORMAL_COUNT = 99
EXPECTED_CANDIDATE_COUNT = 891
EXPECTED_PASSING_COUNT = 757
EXPECTED_OLD_PASSING_COUNT = 676
NEW_BASE_DECIMAL_EXPONENT = 17
EXPECTED_SELECTED_BASE_RADIUS = Fraction(9, 10**17)
EXPECTED_SELECTED_NORMAL_RADIUS = Fraction(5, 10**11)
EXPECTED_FIRST_LARGER_NORMAL_RADIUS = Fraction(6, 10**11)
EXPECTED_BASE_IMPROVEMENT = Fraction(100)
EXPECTED_NORMAL_IMPROVEMENT = Fraction(10)
EXPECTED_NEW_CANDIDATE_DIGEST = (
    "a7a6a8f605339b0e8ffd16a5d3190967cb7329771d322f8edc0a53bc4b45e408"
)
EXPECTED_OLD_CANDIDATE_DIGEST = (
    "91fcc70355acfc4b7163c951227188960ef275408b06a678d45d5e4ec4c85300"
)

REGISTERED_ARTIFACTS = {
    "q007p": {
        "filename": "q007p_finite_tube_attraction.json",
        "sha256": (
            "a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751"
        ),
        "runner_sha256": (
            "23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a"
        ),
        "classification": (
            "registered fixed-leaf tube is uniformly normally attracting "
            "in the external-coordinate norm"
        ),
    },
    "q007s": {
        "filename": "q007s_finite_tube_enlargement.json",
        "sha256": (
            "7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292"
        ),
        "runner_sha256": (
            "6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e"
        ),
        "classification": (
            "registered exact-manifold tube enlarged on the fixed rational "
            "candidate grid"
        ),
    },
    "q007ae": {
        "filename": "q007ae_internal_phase_resolvent.json",
        "sha256": (
            "c6d28bba13fcf831dfccaf03854072256f7e8ff1a241b54aaf84552dd06a2a55"
        ),
        "runner_sha256": (
            "f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600"
        ),
        "classification": (
            "phase-aware selected-output centers remove the internal "
            "resolvent bottleneck"
        ),
    },
    "q007af": {
        "filename": "q007af_radius_step_obstruction.json",
        "sha256": (
            "a686526552c33f5f1f01a9f1d9c49036d1c9491a2092b07ac8c8621a33d4ada1"
        ),
        "runner_sha256": (
            "819679b22d7552a3f247d7c3389a83890f56c60522154bdb5ea05d7eb77a48a4"
        ),
        "classification": (
            "sealed external phase-disc family cannot certify the "
            "1e-15 radius step"
        ),
    },
}

REGISTERED_IMPLEMENTATIONS = {
    "q007n": {
        "module": q007n,
        "path": "research/q007n_explicit_local_radius.py",
        "sha256": (
            "6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9"
        ),
    },
    "q007o": {
        "module": q007o,
        "path": "research/q007o_external_complement_radius.py",
        "sha256": (
            "d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7"
        ),
    },
    "q007p": {
        "module": q007p,
        "path": "research/q007p_finite_tube_attraction.py",
        "sha256": (
            "23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a"
        ),
    },
    "q007s": {
        "module": q007s,
        "path": "research/q007s_finite_tube_enlargement.py",
        "sha256": (
            "6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e"
        ),
    },
    "q007ae": {
        "module": q007ae,
        "path": "research/q007ae_internal_phase_resolvent.py",
        "sha256": (
            "f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600"
        ),
    },
    "q007af": {
        "module": q007af,
        "path": "research/q007af_radius_step_obstruction.py",
        "sha256": (
            "819679b22d7552a3f247d7c3389a83890f56c60522154bdb5ea05d7eb77a48a4"
        ),
    },
}

_ARTIFACT_MODULES = {
    "q007p": q007p,
    "q007s": q007s,
    "q007ae": q007ae,
    "q007af": q007af,
}

REGISTERED_Q007AE_DIGESTS = {
    "input": (
        "23fba479cfa07ec50721d9b05bcaf40a0ac04126497ff64b04785e1d20534e0e"
    ),
    "result": (
        "3e1792c5215952d9126bf5bd61409a2a0d72ebc12970ad1e4aaca481d4fcb687"
    ),
    "phase": (
        "4aea091076179e7ef8eb14c9c4828b41d6af3ef25665e5b2dbbf562acf692b3b"
    ),
    "selected_center": (
        "3cc524ebb82c3e375bf35d456f96be11fa5d124728873046ed59a7032a2058d7"
    ),
}
REGISTERED_Q007AF_DIGESTS = {
    "input": (
        "6cfeabe16a18fdb6de08e67c575a0b0db2f3ab1341c35c434faff100fd959255"
    ),
    "result": (
        "3d210cf25513e373ac6a2e7a276163998a602c529878f3c95f085c9e0625bfdd"
    ),
    "integer_bisection": (
        "24b0e993f676082579158cfeddfe74009161d72412bf228f715baa396246c31b"
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


def _common_scope_matches(payload: dict[str, Any]) -> bool:
    scope = payload.get("mathematical_scope", {})
    return bool(
        scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega")) == OMEGA
        and float(scope.get("eta")) == ETA
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
    )


def _digest_audit(name: str, cycle: dict[str, Any]) -> dict[str, Any]:
    if name == "q007s":
        observed = {
            "candidate": cycle.get("candidate_grid_audit", {}).get(
                "canonical_candidate_digest_sha256"
            )
        }
        registered = {"candidate": EXPECTED_OLD_CANDIDATE_DIGEST}
    elif name == "q007ae":
        observed = {
            "input": cycle.get("input_digest_sha256"),
            "result": cycle.get("result_digest_sha256"),
            "phase": cycle.get("phase_aware_separation_audit", {})
            .get("phase", {})
            .get("comparison_digest_sha256"),
            "selected_center": cycle.get(
                "phase_aware_separation_audit", {}
            ).get("selected_center_certificate_digest_sha256"),
        }
        registered = REGISTERED_Q007AE_DIGESTS
    elif name == "q007af":
        observed = {
            "input": cycle.get("input_digest_sha256"),
            "result": cycle.get("result_digest_sha256"),
            "integer_bisection": cycle.get(
                "integer_inverse_threshold_audit", {}
            ).get("bisection_decision_digest_sha256"),
        }
        registered = REGISTERED_Q007AF_DIGESTS
    else:
        observed = {}
        registered = {}
    return {
        "observed": observed,
        "registered": registered,
        "matches": observed == registered,
    }


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads = {}
    records = {}
    for name, registration in REGISTERED_ARTIFACTS.items():
        path = directory / registration["filename"]
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads[name] = payload
        cycle = payload.get("cycle", {})
        module_path = Path(_ARTIFACT_MODULES[name].__file__).resolve()
        observed_artifact_sha = _file_sha256(path)
        observed_runner_sha = _file_sha256(module_path)
        digest = _digest_audit(name, cycle)
        gates = cycle.get("validity_gates", {})
        hypotheses = cycle.get("hypothesis_gates", {})
        record = {
            "filename": path.name,
            "sha256": observed_artifact_sha,
            "registered_sha256": registration["sha256"],
            "sha256_matches": (
                observed_artifact_sha == registration["sha256"]
            ),
            "runner_filename": module_path.name,
            "runner_sha256": observed_runner_sha,
            "registered_runner_sha256": registration["runner_sha256"],
            "runner_sha256_matches": (
                observed_runner_sha == registration["runner_sha256"]
                and payload.get("runner_source", {}).get("sha256")
                == registration["runner_sha256"]
            ),
            "source_matches": payload.get("source") == source_metadata(),
            "scope_matches": _common_scope_matches(payload),
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "scientific_classification": cycle.get(
                "scientific_classification"
            ),
            "all_validity_gates_passed": bool(gates)
            and all(gate.get("passed", False) for gate in gates.values()),
            "all_hypothesis_gates_passed": bool(hypotheses)
            and all(
                gate.get("passed", False)
                for gate in hypotheses.values()
            ),
            "registered_digest_audit": digest,
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["runner_sha256_matches"]
            and record["source_matches"]
            and record["scope_matches"]
            and record["study_gate"] == "passed"
            and record["scientific_outcome"] == "accepted"
            and record["scientific_classification"]
            == registration["classification"]
            and record["all_validity_gates_passed"]
            and record["all_hypothesis_gates_passed"]
            and digest["matches"]
        )
        records[name] = record
    return payloads, records


def _implementation_source_audit() -> dict[str, Any]:
    records = {}
    for name, registration in REGISTERED_IMPLEMENTATIONS.items():
        path = Path(registration["module"].__file__).resolve()
        observed = _file_sha256(path)
        records[name] = {
            "path": registration["path"],
            "sha256": observed,
            "registered_sha256": registration["sha256"],
            "passed": observed == registration["sha256"],
        }
    return {
        "records": records,
        "all_registered_implementation_sha256_match": all(
            record["passed"] for record in records.values()
        ),
    }


def _reproduce_q007s(
    directory: Path,
    payloads: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], bool]:
    replayed = q007s.run_finite_tube_enlargement_audit(directory)
    stored = payloads["q007s"]["cycle"]
    replay_matches = replayed == stored
    selection = replayed["selection"]
    selected = selection["selected_candidate"]
    selected_matches = bool(
        selected is not None
        and _fraction_from_record(selected["base_radius"])
        == Fraction(9, 10**19)
        and _fraction_from_record(selected["normal_radius"])
        == Fraction(5, 10**12)
        and selected["passed"]
        and all(selected["gates"].values())
    )
    audit = {
        "stored_cycle_sha256": _canonical_json_sha256(stored),
        "replayed_cycle_sha256": _canonical_json_sha256(replayed),
        "stored_cycle_reproduced_exactly": replay_matches,
        "candidate_count": replayed["candidate_grid_audit"][
            "candidate_count"
        ],
        "passing_candidate_count": selection["passing_candidate_count"],
        "candidate_digest_sha256": replayed["candidate_grid_audit"][
            "canonical_candidate_digest_sha256"
        ],
        "registered_candidate_digest_sha256": (
            EXPECTED_OLD_CANDIDATE_DIGEST
        ),
        "selected_base_radius": selected["base_radius"],
        "selected_normal_radius": selected["normal_radius"],
        "selected_candidate_matches": selected_matches,
        "selection_boundary_reproduced": selection[
            "selection_boundary_reproduced"
        ],
    }
    passed = bool(
        replay_matches
        and audit["candidate_count"] == EXPECTED_CANDIDATE_COUNT
        and audit["passing_candidate_count"] == EXPECTED_OLD_PASSING_COUNT
        and audit["candidate_digest_sha256"]
        == EXPECTED_OLD_CANDIDATE_DIGEST
        and selected_matches
        and audit["selection_boundary_reproduced"]
    )
    audit["passed"] = passed
    return audit, passed


def _reproduce_q007ae_boundary(
    payloads: dict[str, dict[str, Any]],
    old_constants: dict[str, Fraction],
) -> tuple[
    dict[str, Any],
    dict[str, Fraction],
    bool,
]:
    q007ae_cycle = payloads["q007ae"]["cycle"]
    stored_scan = q007ae_cycle["radius_comparison"][
        "internal_phase_refined_radius_search"
    ]
    total_inverse = _fraction_from_record(
        q007ae_cycle["total_inverse_refinement"][
            "working_new_total_pair_inverse_upper"
        ]
    )
    coefficients = {
        name: value
        for name, value in old_constants.items()
        if name
        in {
            "c_v",
            "h2",
            "h3",
            "h4",
            "g2",
            "g3",
            "g4",
            "h2_box",
            "h3_box",
            "h4_box",
            "g2_box",
            "g3_box",
            "g4_box",
        }
    }
    reproduced_scan, _exact = q007o._radius_scan(
        coefficients,
        old_constants["selected_radius"],
        total_inverse,
    )
    records_match = reproduced_scan["records"] == stored_scan["records"]
    stored_selected = stored_scan["exact_boundary_certificate"]["selected"]
    new_rho = _fraction_from_record(stored_selected["radius"])
    new_tau = _fraction_from_record(stored_selected["correction_radius"])
    selected = reproduced_scan["selected_candidate"]
    previous = reproduced_scan["previous_larger_candidate"]
    boundary_matches = bool(
        selected is not None
        and previous is not None
        and selected["modal_radius_decimal"] == "1e-16"
        and selected["passed"]
        and previous["modal_radius_decimal"] == "1e-15"
        and not previous["passed"]
        and _fraction_from_record(
            reproduced_scan["exact_boundary_certificate"]["selected"][
                "radius"
            ]
        )
        == new_rho
        and _fraction_from_record(
            reproduced_scan["exact_boundary_certificate"]["selected"][
                "correction_radius"
            ]
        )
        == new_tau
    )
    audit = {
        "q007ae_total_inverse_upper": _fraction_record(total_inverse),
        "candidate_count": len(reproduced_scan["records"]),
        "stored_candidate_records_sha256": _canonical_json_sha256(
            stored_scan["records"]
        ),
        "reproduced_candidate_records_sha256": _canonical_json_sha256(
            reproduced_scan["records"]
        ),
        "candidate_records_reproduced_exactly": records_match,
        "selected_modal_radius_decimal": (
            None if selected is None else selected["modal_radius_decimal"]
        ),
        "previous_modal_radius_decimal": (
            None if previous is None else previous["modal_radius_decimal"]
        ),
        "selected_passed": bool(selected and selected["passed"]),
        "previous_passed": bool(previous and previous["passed"]),
        "new_analytic_radius": _fraction_record(new_rho),
        "new_correction_pair_radius_tau": _fraction_record(new_tau),
        "old_analytic_radius": _fraction_record(old_constants["rho"]),
        "old_correction_pair_radius_tau": _fraction_record(
            old_constants["tau"]
        ),
        "analytic_radius_improvement_factor": _fraction_record(
            new_rho / old_constants["rho"]
        ),
        "correction_radius_inflation_factor": _fraction_record(
            new_tau / old_constants["tau"]
        ),
        "boundary_reproduced": boundary_matches,
    }
    passed = bool(
        len(reproduced_scan["records"]) == len(q007n.CANDIDATE_EXPONENTS)
        and records_match
        and boundary_matches
        and new_rho == Fraction(1, 10**16)
        and new_tau > 0
        and new_rho / old_constants["rho"] == 100
    )
    audit["passed"] = passed
    return audit, {"rho": new_rho, "tau": new_tau}, passed


def _new_constants_audit(
    old_constants: dict[str, Fraction],
    boundary: dict[str, Fraction],
    old_audit: dict[str, Any],
    old_selected: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction], bool]:
    new_constants = dict(old_constants)
    new_constants.update(boundary)
    changed_names = sorted(
        name
        for name in old_constants
        if old_constants[name] != new_constants[name]
    )
    control_base = _fraction_from_record(old_selected["base_radius"])
    control_normal = _fraction_from_record(old_selected["normal_radius"])
    control = q007s._evaluate_candidate(
        control_base, control_normal, new_constants
    )
    audit = {
        "old_q007p_constant_audit_passed": old_audit["passed"],
        "constant_count": len(new_constants),
        "changed_constant_names": changed_names,
        "only_rho_and_tau_changed": changed_names == ["rho", "tau"],
        "old_rho": _fraction_record(old_constants["rho"]),
        "new_rho": _fraction_record(new_constants["rho"]),
        "old_tau": _fraction_record(old_constants["tau"]),
        "new_tau": _fraction_record(new_constants["tau"]),
        "unchanged_constants_sha256": _canonical_json_sha256(
            {
                name: _fraction_record(value)
                for name, value in old_constants.items()
                if name not in {"rho", "tau"}
            }
        ),
        "new_constant_control_candidate": q007s._candidate_exact_record(
            control
        ),
        "q007s_selected_control_passes_with_new_constants": control[
            "passed"
        ],
    }
    passed = bool(
        old_audit["passed"]
        and audit["only_rho_and_tau_changed"]
        and control["passed"]
        and all(control["gates"].values())
    )
    audit["passed"] = passed
    return audit, new_constants, passed


def _registered_grid() -> tuple[list[Fraction], list[Fraction]]:
    base_radii = [
        Fraction(mantissa, 10**NEW_BASE_DECIMAL_EXPONENT)
        for mantissa in range(1, 10)
    ]
    _old_bases, normal_radii = q007s._registered_grids()
    return base_radii, normal_radii


def _new_grid_audit(
    constants: dict[str, Fraction],
    old_selected: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], bool]:
    base_radii, normal_radii = _registered_grid()
    candidates = [
        q007s._evaluate_candidate(base_radius, normal_radius, constants)
        for base_radius in base_radii
        for normal_radius in normal_radii
    ]
    passing = [candidate for candidate in candidates if candidate["passed"]]
    selected = max(
        passing,
        key=lambda candidate: (
            candidate["base_radius"],
            candidate["normal_radius"],
        ),
    )
    digest = q007s._candidate_digest(candidates)
    selected_slice_larger = [
        candidate
        for candidate in candidates
        if candidate["base_radius"] == selected["base_radius"]
        and candidate["normal_radius"] > selected["normal_radius"]
    ]
    first_larger = min(
        selected_slice_larger,
        key=lambda candidate: candidate["normal_radius"],
    )
    larger_bases = [
        candidate
        for candidate in candidates
        if candidate["base_radius"] > selected["base_radius"]
    ]
    old_base = _fraction_from_record(old_selected["base_radius"])
    old_normal = _fraction_from_record(old_selected["normal_radius"])
    base_improvement = selected["base_radius"] / old_base
    normal_improvement = selected["normal_radius"] / old_normal
    unique_grid = bool(
        len(base_radii) == len(set(base_radii)) == EXPECTED_BASE_COUNT
        and len(normal_radii)
        == len(set(normal_radii))
        == EXPECTED_NORMAL_COUNT
        and len(candidates) == EXPECTED_CANDIDATE_COUNT
        and len(
            {
                (candidate["base_radius"], candidate["normal_radius"])
                for candidate in candidates
            }
        )
        == EXPECTED_CANDIDATE_COUNT
    )
    boundary = bool(
        selected["base_radius"] == EXPECTED_SELECTED_BASE_RADIUS
        and selected["normal_radius"]
        == EXPECTED_SELECTED_NORMAL_RADIUS
        and selected["passed"]
        and all(selected["gates"].values())
        and selected_slice_larger
        and all(not candidate["passed"] for candidate in selected_slice_larger)
        and not larger_bases
        and first_larger["normal_radius"]
        == EXPECTED_FIRST_LARGER_NORMAL_RADIUS
    )
    first_larger_failed = [
        name
        for name, passed in first_larger["gates"].items()
        if not passed
    ]
    boundary = bool(
        boundary
        and first_larger_failed == ["base_forward_invariance"]
    )
    summaries = [
        q007s._candidate_summary(candidate) for candidate in candidates
    ]
    grid_audit = {
        "base_grid_formula": "m*10^-17 for m=1,...,9",
        "normal_grid_formula": (
            "unique m*10^-e for m=1,...,9 and e=10,...,20"
        ),
        "base_radius_count": len(base_radii),
        "normal_radius_count": len(normal_radii),
        "candidate_count": len(candidates),
        "unique_cartesian_product": unique_grid,
        "decision_arithmetic": "exact fractions.Fraction signs only",
        "selection_rule": (
            "lexicographically maximize base radius, then normal radius, "
            "among passing candidates"
        ),
        "passing_candidate_count": len(passing),
        "registered_passing_candidate_count": EXPECTED_PASSING_COUNT,
        "canonical_candidate_digest_sha256": digest,
        "registered_candidate_digest_sha256": (
            EXPECTED_NEW_CANDIDATE_DIGEST
        ),
        "candidate_summaries": summaries,
        "base_slice_boundaries": q007s._slice_records(
            candidates, base_radii
        ),
    }
    selection = {
        "selected_candidate": q007s._candidate_exact_record(selected),
        "old_q007s_selected_base_radius": old_selected["base_radius"],
        "old_q007s_selected_normal_radius": old_selected["normal_radius"],
        "base_radius_improvement_factor": _fraction_record(
            base_improvement
        ),
        "normal_radius_improvement_factor": _fraction_record(
            normal_improvement
        ),
        "selected_slice_larger_candidate_count": len(
            selected_slice_larger
        ),
        "all_larger_normals_on_selected_slice_fail": all(
            not candidate["passed"]
            for candidate in selected_slice_larger
        ),
        "larger_base_candidate_count": len(larger_bases),
        "all_larger_bases_fail_or_absent": not larger_bases,
        "first_larger_normal_candidate": q007s._candidate_exact_record(
            first_larger
        ),
        "first_larger_normal_failed_gate_names": first_larger_failed,
        "registered_selection_boundary_reproduced": boundary,
    }
    passed = bool(
        unique_grid
        and len(passing) == EXPECTED_PASSING_COUNT
        and digest == EXPECTED_NEW_CANDIDATE_DIGEST
        and boundary
        and base_improvement == EXPECTED_BASE_IMPROVEMENT
        and normal_improvement == EXPECTED_NORMAL_IMPROVEMENT
    )
    grid_audit["passed"] = unique_grid
    selection["passed"] = passed
    return grid_audit, selection, passed


def run_tube_radius_propagation_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    implementation_audit = _implementation_source_audit()
    q007s_reproduction, q007s_reproduced = _reproduce_q007s(
        directory, payloads
    )
    old_constants, old_constant_audit = q007s._extract_constants(
        payloads["q007p"]
    )
    q007ae_boundary, boundary_values, q007ae_reproduced = (
        _reproduce_q007ae_boundary(payloads, old_constants)
    )
    old_selected = payloads["q007s"]["cycle"]["selection"][
        "selected_candidate"
    ]
    constant_update, new_constants, constants_passed = (
        _new_constants_audit(
            old_constants,
            boundary_values,
            old_constant_audit,
            old_selected,
        )
    )
    grid_audit, selection, grid_selection_passed = _new_grid_audit(
        new_constants, old_selected
    )
    selected = selection["selected_candidate"]

    registered_parameters = {
        "size": SIZE,
        "omega": OMEGA,
        "eta": ETA,
        "old_selected_base_radius": old_selected["base_radius"],
        "old_selected_normal_radius": old_selected["normal_radius"],
        "base_mantissas": list(range(1, 10)),
        "base_decimal_exponent": -NEW_BASE_DECIMAL_EXPONENT,
        "normal_mantissas": list(range(1, 10)),
        "normal_decimal_exponents": list(range(-20, -9)),
        "candidate_count": EXPECTED_CANDIDATE_COUNT,
        "expected_passing_count": EXPECTED_PASSING_COUNT,
        "expected_candidate_digest": EXPECTED_NEW_CANDIDATE_DIGEST,
        "expected_selected_base_radius": _fraction_record(
            EXPECTED_SELECTED_BASE_RADIUS
        ),
        "expected_selected_normal_radius": _fraction_record(
            EXPECTED_SELECTED_NORMAL_RADIUS
        ),
        "expected_first_larger_normal_radius": _fraction_record(
            EXPECTED_FIRST_LARGER_NORMAL_RADIUS
        ),
        "selection_rule": "maximize base radius, then normal radius",
    }
    input_digest = _canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "implementation_source_audit": implementation_audit,
            "registered_parameters": registered_parameters,
        }
    )
    result_sections = {
        "q007s_exact_reproduction": q007s_reproduction,
        "q007ae_radius_boundary_reproduction": q007ae_boundary,
        "constant_update_audit": constant_update,
        "scaled_candidate_grid_audit": grid_audit,
        "selection": selection,
    }
    result_digest = _canonical_json_sha256(result_sections)
    finite_strict_json = bool(
        _all_numeric_values_finite(result_sections)
        and _strict_json_serializable(result_sections)
    )

    input_passed = all(record["passed"] for record in input_records.values())
    implementation_passed = implementation_audit[
        "all_registered_implementation_sha256_match"
    ]
    validity_gates = {
        "sealed_artifacts_source_scope_outcomes_and_digests": {
            "passed": input_passed,
            "threshold": (
                "all four artifact/runner SHA values, common scope, "
                "accepted outcomes, classifications, gates, and sealed "
                "digests match"
            ),
            "value": {
                "accepted_input_count": sum(
                    record["passed"] for record in input_records.values()
                ),
                "expected_input_count": len(input_records),
            },
        },
        "sealed_implementation_sources": {
            "passed": implementation_passed,
            "threshold": "all six registered implementation SHA values match",
            "value": {
                "matching_source_count": sum(
                    record["passed"]
                    for record in implementation_audit["records"].values()
                ),
                "expected_source_count": len(
                    implementation_audit["records"]
                ),
            },
        },
        "q007s_old_grid_and_selection_reproduced": {
            "passed": q007s_reproduced,
            "threshold": (
                "old Q007s cycle, 891 candidates, 676 passes, digest, "
                "selected point, and selection boundary reproduce exactly"
            ),
            "value": {
                "candidate_count": q007s_reproduction[
                    "candidate_count"
                ],
                "passing_count": q007s_reproduction[
                    "passing_candidate_count"
                ],
                "cycle_match": q007s_reproduction[
                    "stored_cycle_reproduced_exactly"
                ],
            },
        },
        "q007ae_boundary_and_two_constant_update": {
            "passed": q007ae_reproduced and constants_passed,
            "threshold": (
                "all 119 Q007ae records and 1e-16 boundary reproduce; "
                "only rho/tau change and old Q007s selected control passes"
            ),
            "value": {
                "q007ae_reproduced": q007ae_reproduced,
                "changed_names": constant_update[
                    "changed_constant_names"
                ],
                "control_passed": constant_update[
                    "q007s_selected_control_passes_with_new_constants"
                ],
            },
        },
        "scaled_grid_complete_and_exactly_selected": {
            "passed": grid_audit["passed"]
            and grid_selection_passed,
            "threshold": (
                "9 unique base by 99 unique normal radii give 891 exact "
                "candidates with the registered selection boundary"
            ),
            "value": {
                "base_count": grid_audit["base_radius_count"],
                "normal_count": grid_audit["normal_radius_count"],
                "candidate_count": grid_audit["candidate_count"],
                "selection_boundary": selection[
                    "registered_selection_boundary_reproduced"
                ],
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": finite_strict_json,
            "threshold": (
                "all result sections are finite strict JSON and emit "
                "canonical input/candidate/result digests"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest,
                "candidate_digest_sha256": grid_audit[
                    "canonical_candidate_digest_sha256"
                ],
                "result_digest_sha256": result_digest,
            },
        },
    }
    study_validity = (
        "passed"
        if all(gate["passed"] for gate in validity_gates.values())
        else "failed"
    )

    selected_gates = selected["gates"]
    first_larger = selection["first_larger_normal_candidate"]
    hypothesis_gates = {
        "registered_passing_count_and_candidate_digest": {
            "passed": bool(
                grid_audit["passing_candidate_count"]
                == EXPECTED_PASSING_COUNT
                and grid_audit["canonical_candidate_digest_sha256"]
                == EXPECTED_NEW_CANDIDATE_DIGEST
            ),
            "threshold": (
                "757 candidates pass and the canonical digest matches "
                "the preregistered value"
            ),
            "value": {
                "passing_count": grid_audit[
                    "passing_candidate_count"
                ],
                "digest": grid_audit[
                    "canonical_candidate_digest_sha256"
                ],
            },
        },
        "registered_selected_candidate_strictly_passes": {
            "passed": bool(
                _fraction_from_record(selected["base_radius"])
                == EXPECTED_SELECTED_BASE_RADIUS
                and _fraction_from_record(selected["normal_radius"])
                == EXPECTED_SELECTED_NORMAL_RADIUS
                and selected["passed"]
                and all(selected_gates.values())
            ),
            "threshold": (
                "selected point is exactly (9e-17,5e-11) and all six "
                "candidate gates pass strictly"
            ),
            "value": {
                "base_radius": selected["base_radius"]["float"],
                "normal_radius": selected["normal_radius"]["float"],
                "gates": selected_gates,
            },
        },
        "both_q007s_tube_radii_strictly_enlarged": {
            "passed": bool(
                _fraction_from_record(
                    selection["base_radius_improvement_factor"]
                )
                == EXPECTED_BASE_IMPROVEMENT
                and _fraction_from_record(
                    selection["normal_radius_improvement_factor"]
                )
                == EXPECTED_NORMAL_IMPROVEMENT
            ),
            "threshold": (
                "base and normal improvement factors are exactly 100 and 10"
            ),
            "value": {
                "base": selection[
                    "base_radius_improvement_factor"
                ]["float"],
                "normal": selection[
                    "normal_radius_improvement_factor"
                ]["float"],
            },
        },
        "registered_selection_boundary": {
            "passed": bool(
                selection[
                    "registered_selection_boundary_reproduced"
                ]
                and selection[
                    "all_larger_normals_on_selected_slice_fail"
                ]
                and selection["all_larger_bases_fail_or_absent"]
                and _fraction_from_record(first_larger["normal_radius"])
                == EXPECTED_FIRST_LARGER_NORMAL_RADIUS
                and selection[
                    "first_larger_normal_failed_gate_names"
                ]
                == ["base_forward_invariance"]
            ),
            "threshold": (
                "all larger normals on the selected slice fail, no larger "
                "base is registered, and 6e-11 first fails only base "
                "forward invariance"
            ),
            "value": {
                "larger_normal_count": selection[
                    "selected_slice_larger_candidate_count"
                ],
                "larger_base_count": selection[
                    "larger_base_candidate_count"
                ],
                "first_larger_failed_gates": selection[
                    "first_larger_normal_failed_gate_names"
                ],
            },
        },
        "selected_normal_attraction_and_domination_strict": {
            "passed": bool(
                _fraction_from_record(selected["normal_contraction"])
                < q007s.MAXIMUM_NORMAL_CONTRACTION
                and _fraction_from_record(selected["tangent_conorm"]) > 0
                and _fraction_from_record(selected["domination_ratio"])
                < q007s.MAXIMUM_DOMINATION_RATIO
            ),
            "threshold": (
                "selected q<0.99, tangent conorm>0, and q/m_T<0.999"
            ),
            "value": {
                "normal_contraction": selected[
                    "normal_contraction"
                ]["float"],
                "tangent_conorm": selected["tangent_conorm"]["float"],
                "domination_ratio": selected[
                    "domination_ratio"
                ]["float"],
            },
        },
    }
    all_hypotheses = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if study_validity != "passed":
        outcome = "inconclusive"
        classification = (
            "analytic-radius tube-propagation audit invalid; prior Q007s "
            "tube remains unchanged"
        )
    elif all_hypotheses:
        outcome = "accepted"
        classification = (
            "Q007ae analytic radius enlarges the registered "
            "external-coordinate tube"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered scaled grid did not propagate the Q007ae "
            "analytic radius to both tube radii"
        )

    hypotheses_accepted = bool(
        study_validity == "passed" and all_hypotheses
    )
    return {
        "question": (
            "Does replacing only Q007p/Q007s rho and tau by the accepted "
            "Q007ae 1e-16 boundary strictly enlarge both Q007s tube radii "
            "on the preregistered scaled rational grid?"
        ),
        "registered_parameters": registered_parameters,
        "input_artifacts": input_records,
        "implementation_source_audit": implementation_audit,
        **result_sections,
        "input_digest_sha256": input_digest,
        "candidate_digest_sha256": grid_audit[
            "canonical_candidate_digest_sha256"
        ],
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": study_validity,
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "selected_registered_tube_forward_invariant": (
                hypotheses_accepted
            ),
            "selected_registered_tube_uniformly_normal_contracting": (
                hypotheses_accepted
            ),
            "selected_registered_tube_strictly_normally_dominating": (
                hypotheses_accepted
            ),
            "both_q007s_registered_tube_radii_strictly_enlarged": (
                hypotheses_accepted
            ),
            "new_tube_population_positivity_certified": False,
            "new_tube_stagewise_positivity_certified": False,
            "new_tube_binary64_or_mpfr_induction_certified": False,
        },
        "claim_boundary": (
            "An accepted result certifies only the lexicographically "
            "selected point on the fixed scaled 9-by-99 grid for the "
            "17x17 map, conservation leaf, exact graph-gauge manifold, "
            "and Q007p external-coordinate norm. It is not a continuous "
            "optimum, maximum tube, Euclidean or grid-uniform attraction "
            "result, global basin, or continuum limit. Q007t/Q007u "
            "positivity and Q007v--Q007ab binary64/MPFR/repair/shadowing "
            "remain sealed to the old Q007s tube."
        ),
        "preserved_prior_outcomes": {
            "q007t_old_tube_positivity_changed": False,
            "q007u_old_tube_stagewise_positivity_changed": False,
            "q007v_through_q007ab_old_tube_results_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007af_external_disc_obstruction_changed": False,
            "q010_sparse_cost_dominance_changed": False,
        },
        "next_change": (
            "If accepted, separately preregister exact population and "
            "stagewise positivity on the selected Q007ag tube. Do not "
            "extend binary64, MPFR repair, or forward-shadowing constants "
            "until those positivity gates pass."
        ),
    }


def run_q007ag_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_tube_radius_propagation_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "analytic-radius-propagated rational finite-tube "
                "enlargement certificate"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": (
                "fixed global mass and momentum leaf"
            ),
            "manifold": "Q007ae exact graph-gauge manifold",
            "norm": "Q007p Fourier external-coordinate block-sum l1",
            "candidate_grid": "9 scaled base radii by 99 normal radii",
            "selection": (
                "lexicographically maximize base then normal radius"
            ),
            "claim": (
                "forward invariance, one-step normal contraction, and "
                "strict normal domination for one selected registered "
                "tube only"
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
    result = run_q007ag_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
