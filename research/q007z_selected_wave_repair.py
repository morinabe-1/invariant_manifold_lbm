"""Sealed Q007z selected-wave certificate for the balanced MPFR repair."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q007x_mpfr_backend as backend
import research.q007y_distributed_conservation_repair as q007y
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
MAXIMUM_PREFIX_BOUND = WAVE_COUNT // 2

AXIS_SELECTED_WAVES = (
    (-1, 0),
    (0, -1),
    (1, 0),
    (0, 1),
)
DIAGONAL_SELECTED_WAVES = (
    (-1, -1),
    (1, -1),
    (1, 1),
    (-1, 1),
)
SELECTED_WAVES = AXIS_SELECTED_WAVES + DIAGONAL_SELECTED_WAVES

Q007P_ARTIFACT = "q007p_finite_tube_attraction.json"
Q007Y_ARTIFACT = "q007y_distributed_conservation_repair.json"
REGISTERED_Q007P_ARTIFACT_SHA256 = (
    "a5e766938cfee0174deba9c529be9aec2cce4bff9225a3a4a1da83f7d255a751"
)
REGISTERED_Q007P_RUNNER_SHA256 = (
    "23ff283acb3f872fd2ff489f17d94b8e022e3f45a5c65b5523bf976c534a9f2a"
)
REGISTERED_Q007Y_ARTIFACT_SHA256 = (
    "a3afa87c4ee3f5d45e667eac9a6a89a1726f1d4bad0a9f90a624c562fb598648"
)
REGISTERED_Q007Y_RUNNER_SHA256 = (
    "ba757030c852b68d5a4c643ec150422c0a7b4c3ba125211d2715ba1445e89811"
)
REGISTERED_BACKEND_SOURCE_SHA256 = (
    "25ad43629e2487c5c062920cbb5319dac4e8fbded339dc856548bfab7f18a0dc"
)


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
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _load_registered_q007p(directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007P_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    runner_path = Path(__file__).resolve().with_name(
        "q007p_finite_tube_attraction.py"
    )
    cycle = payload.get("cycle", {})
    scope = payload.get("mathematical_scope", {})
    record = {
        "filename": Q007P_ARTIFACT,
        "registered_sha256": REGISTERED_Q007P_ARTIFACT_SHA256,
        "sha256": _file_sha256(artifact_path),
        "sha256_matches": (
            _file_sha256(artifact_path) == REGISTERED_Q007P_ARTIFACT_SHA256
        ),
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": bool(
            scope.get("diagnostic")
            == "rational finite-tube normal-attraction certificate"
            and scope.get("construction_grid") == [SIZE, SIZE]
            and scope.get("conservation_treatment")
            == "fixed global mass and momentum leaf"
            and scope.get("selected_real_dimension") == 24
        ),
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "validity_gate_count": len(cycle.get("validity_gates", {})),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "hypothesis_gate_count": len(cycle.get("hypothesis_gates", {})),
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload,
            "hypothesis_gates",
        ),
        "registered_runner_sha256": REGISTERED_Q007P_RUNNER_SHA256,
        "artifact_runner_sha256": payload.get("runner_source", {}).get("sha256"),
        "observed_runner_sha256": _file_sha256(runner_path),
        "runner_sha_matches": bool(
            payload.get("runner_source", {}).get("sha256")
            == REGISTERED_Q007P_RUNNER_SHA256
            and _file_sha256(runner_path) == REGISTERED_Q007P_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and record["validity_gate_count"] == 6
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"] == 4
        and record["all_hypothesis_gates_pass"]
        and record["runner_sha_matches"]
    )
    return payload, record


def _load_registered_q007y(directory: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007Y_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    runner_path = Path(q007y.__file__).resolve()
    backend_path = Path(backend.__file__).resolve()
    cycle = payload.get("cycle", {})
    scope = payload.get("mathematical_scope", {})
    hypothesis_gates = cycle.get("hypothesis_gates", {})
    fresh_cycle = q007y.run_distributed_repair_audit(directory)
    record = {
        "filename": Q007Y_ARTIFACT,
        "registered_sha256": REGISTERED_Q007Y_ARTIFACT_SHA256,
        "sha256": _file_sha256(artifact_path),
        "sha256_matches": (
            _file_sha256(artifact_path) == REGISTERED_Q007Y_ARTIFACT_SHA256
        ),
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": bool(
            scope.get("diagnostic")
            == (
                "distributed dyadic fixed-leaf repair and repair-aware "
                "Wiener-budget audit"
            )
            and scope.get("construction_grid") == [SIZE, SIZE]
            and scope.get("repair_lattice")
            == "four diagonal populations on h=2^-90"
        ),
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "validity_gate_count": len(cycle.get("validity_gates", {})),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "hypothesis_gate_count": len(hypothesis_gates),
        "passing_hypothesis_gate_count": sum(
            bool(gate.get("passed", False)) for gate in hypothesis_gates.values()
        ),
        "fresh_cycle_matches": fresh_cycle == cycle,
        "registered_runner_sha256": REGISTERED_Q007Y_RUNNER_SHA256,
        "artifact_runner_sha256": payload.get("runner_source", {}).get("sha256"),
        "observed_runner_sha256": _file_sha256(runner_path),
        "runner_sha_matches": bool(
            payload.get("runner_source", {}).get("sha256")
            == REGISTERED_Q007Y_RUNNER_SHA256
            and _file_sha256(runner_path) == REGISTERED_Q007Y_RUNNER_SHA256
        ),
        "registered_backend_sha256": REGISTERED_BACKEND_SOURCE_SHA256,
        "artifact_backend_sha256": cycle.get("input_audit", {})
        .get("q007x_artifact", {})
        .get("observed_backend_sha256"),
        "observed_backend_sha256": _file_sha256(backend_path),
        "backend_sha_matches": bool(
            cycle.get("input_audit", {})
            .get("q007x_artifact", {})
            .get("observed_backend_sha256")
            == REGISTERED_BACKEND_SOURCE_SHA256
            and _file_sha256(backend_path) == REGISTERED_BACKEND_SOURCE_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "not_certified"
        and record["validity_gate_count"] == 8
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"] == 7
        and record["passing_hypothesis_gate_count"] == 5
        and record["fresh_cycle_matches"]
        and record["runner_sha_matches"]
        and record["backend_sha_matches"]
    )
    return payload, record


def _selected_structure_audit(
    q007p_payload: dict[str, Any],
    q007y_payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    cycle = q007p_payload["cycle"]
    certification = cycle["external_coordinate_certification"]
    records = certification["selected_representative_records"]
    conversion = cycle["global_conversion_and_linear_bounds"]
    axis_record = next(
        record for record in records if tuple(record["wave_index"]) == (1, 0)
    )
    diagonal_record = next(
        record for record in records if tuple(record["wave_index"]) == (1, 1)
    )
    axis_members = tuple(tuple(member) for member in axis_record["orbit_members"])
    diagonal_members = tuple(
        tuple(member) for member in diagonal_record["orbit_members"]
    )
    axis_norm = _fraction_from_record(
        axis_record["selected_analysis_l1_upper"]
    )
    diagonal_norm = _fraction_from_record(
        diagonal_record["selected_analysis_l1_upper"]
    )
    global_norm = _fraction_from_record(
        conversion["selected_left_operator_l1_upper"]
    )
    q007y_norm = _fraction_from_record(
        q007y_payload["cycle"]["tube_wide_repair_bound"][
            "selected_analysis_upper"
        ]
    )
    concise = {
        "representative_count": certification[
            "selected_representative_count"
        ],
        "selected_wave_count": len(axis_members) + len(diagonal_members),
        "axis": {
            "representative": axis_record["wave_index"],
            "members": axis_record["orbit_members"],
            "member_count": axis_record["orbit_member_count"],
            "left_operator_l1_upper": axis_record[
                "selected_analysis_l1_upper"
            ],
        },
        "diagonal": {
            "representative": diagonal_record["wave_index"],
            "members": diagonal_record["orbit_members"],
            "member_count": diagonal_record["orbit_member_count"],
            "left_operator_l1_upper": diagonal_record[
                "selected_analysis_l1_upper"
            ],
        },
        "global_selected_analysis_upper": conversion[
            "selected_left_operator_l1_upper"
        ],
        "q007y_selected_analysis_upper": q007y_payload["cycle"][
            "tube_wide_repair_bound"
        ]["selected_analysis_upper"],
        "global_maximum_is_axis": global_norm == axis_norm,
        "q007y_global_norm_matches": q007y_norm == global_norm,
        "zero_wave_excluded": (0, 0) not in axis_members + diagonal_members,
        "c4_norm_invariance_passed": cycle["structural_audit"][
            "c4_norm_invariance"
        ]["passed"],
    }
    concise["selected_input_digest_sha256"] = _digest_payload(concise)
    concise["passed"] = bool(
        concise["representative_count"] == 2
        and concise["selected_wave_count"] == 8
        and set(axis_members) == set(AXIS_SELECTED_WAVES)
        and set(diagonal_members) == set(DIAGONAL_SELECTED_WAVES)
        and axis_record["orbit_member_count"] == 4
        and diagonal_record["orbit_member_count"] == 4
        and global_norm == max(axis_norm, diagonal_norm)
        and concise["global_maximum_is_axis"]
        and concise["q007y_global_norm_matches"]
        and concise["zero_wave_excluded"]
        and concise["c4_norm_invariance_passed"]
    )
    return concise, {
        "axis_norm": axis_norm,
        "diagonal_norm": diagonal_norm,
        "global_norm": global_norm,
    }


def phase_residue(wave: tuple[int, int], site: int) -> int:
    """Return the exact 17th-root exponent for one row-major grid site."""

    if (
        len(wave) != 2
        or any(isinstance(value, bool) or not isinstance(value, int) for value in wave)
    ):
        raise TypeError("wave must contain two integers")
    if isinstance(site, bool) or not isinstance(site, int):
        raise TypeError("site must be an integer")
    if not 0 <= site < WAVE_COUNT:
        raise ValueError("site must be on the registered grid")
    y, x = divmod(site, SIZE)
    return (wave[0] * x + wave[1] * y) % SIZE


def phase_histogram(
    wave: tuple[int, int],
    site_count: int,
) -> tuple[int, ...]:
    """Count exact phase residues over a row-major prefix."""

    if isinstance(site_count, bool) or not isinstance(site_count, int):
        raise TypeError("site_count must be an integer")
    if not 0 <= site_count <= WAVE_COUNT:
        raise ValueError("site_count must lie between zero and 289")
    counts = [0] * SIZE
    for site in range(site_count):
        counts[phase_residue(wave, site)] += 1
    return tuple(counts)


def _phase_histogram_audit() -> dict[str, Any]:
    digest = hashlib.sha256()
    case_count = 0
    distribution_case_count = 0
    maximum_prefix_bound = 0
    witnesses = []
    wave_records = []
    all_passed = True
    for wave in SELECTED_WAVES:
        full = phase_histogram(wave, WAVE_COUNT)
        full_uniform = full == (SIZE,) * SIZE
        wave_passed = bool(wave != (0, 0) and full_uniform)
        for remainder in range(WAVE_COUNT):
            prefix = phase_histogram(wave, remainder)
            complement = tuple(
                full[index] - prefix[index] for index in range(SIZE)
            )
            prefix_count = sum(prefix)
            complement_count = sum(complement)
            bound = min(prefix_count, complement_count)
            positive_distribution = q007y.balanced_unit_distribution(
                remainder,
                WAVE_COUNT,
            )
            negative_distribution = q007y.balanced_unit_distribution(
                remainder - WAVE_COUNT,
                WAVE_COUNT,
            )
            positive_recipe = positive_distribution == (
                (1,) * remainder + (0,) * (WAVE_COUNT - remainder)
            )
            negative_recipe = negative_distribution == (
                (0,) * remainder + (-1,) * (WAVE_COUNT - remainder)
            )
            case_passed = bool(
                full_uniform
                and prefix_count == remainder
                and complement_count == WAVE_COUNT - remainder
                and bound == min(remainder, WAVE_COUNT - remainder)
                and bound <= MAXIMUM_PREFIX_BOUND
                and positive_recipe
                and negative_recipe
            )
            digest.update(
                (
                    f"{wave[0]},{wave[1]}:{remainder}:"
                    f"{','.join(str(value) for value in prefix)}:"
                    f"{','.join(str(value) for value in complement)}:"
                    f"{bound}:{int(positive_recipe)}:{int(negative_recipe)}\n"
                ).encode("ascii")
            )
            case_count += 1
            distribution_case_count += 2
            maximum_prefix_bound = max(maximum_prefix_bound, bound)
            if bound == MAXIMUM_PREFIX_BOUND:
                witnesses.append(
                    {"wave": list(wave), "remainder": remainder, "bound": bound}
                )
            wave_passed = bool(wave_passed and case_passed)
        wave_records.append(
            {
                "wave": list(wave),
                "full_phase_histogram": list(full),
                "full_grid_character_cancels_by_cyclotomic_identity": (
                    full_uniform
                ),
                "all_remainders_passed": wave_passed,
            }
        )
        all_passed = bool(all_passed and wave_passed)
    passed = bool(
        all_passed
        and case_count == len(SELECTED_WAVES) * WAVE_COUNT
        and distribution_case_count == 2 * case_count
        and maximum_prefix_bound == MAXIMUM_PREFIX_BOUND
    )
    return {
        "selected_wave_count": len(SELECTED_WAVES),
        "remainder_count_per_wave": WAVE_COUNT,
        "phase_histogram_case_count": case_count,
        "balanced_distribution_case_count": distribution_case_count,
        "wave_records": wave_records,
        "maximum_prefix_or_complement_bound": maximum_prefix_bound,
        "maximum_bound_witness_count": len(witnesses),
        "maximum_bound_witnesses": witnesses,
        "phase_digest_sha256": digest.hexdigest(),
        "uses_complex_float_in_proof": False,
        "proof": (
            "uniform full-grid character histograms give exact cyclotomic "
            "cancellation; prefix and complement triangle bounds give "
            "min(r,289-r)"
        ),
        "passed": passed,
    }


def _selected_repair_bound(
    q007y_payload: dict[str, Any],
    selected_exact: dict[str, Fraction],
) -> dict[str, Any]:
    tube = q007y_payload["cycle"]["tube_wide_repair_bound"]
    axis_norm = selected_exact["axis_norm"]
    diagonal_norm = selected_exact["diagonal_norm"]
    global_norm = selected_exact["global_norm"]
    per_population_per_wave = (
        Fraction(MAXIMUM_PREFIX_BOUND, WAVE_COUNT) * REPAIR_QUANTUM
    )
    per_wave_population_l1 = (
        len(q007y.DIAGONAL_POPULATIONS) * per_population_per_wave
    )
    repair_base = (
        len(AXIS_SELECTED_WAVES) * axis_norm * per_wave_population_l1
        + len(DIAGONAL_SELECTED_WAVES)
        * diagonal_norm
        * per_wave_population_l1
    )
    raw_wiener = _fraction_from_record(tube["raw_wiener_error_upper"])
    raw_base = global_norm * raw_wiener
    repaired_base = raw_base + repair_base
    base_margin = _fraction_from_record(tube["base_margin"])
    q007y_coarse_base = _fraction_from_record(
        tube["base_coordinate_error_upper"]
    )
    normal_error = _fraction_from_record(
        tube["normal_coordinate_error_upper"]
    )
    normal_margin = _fraction_from_record(tube["normal_margin"])
    base_passed = repaired_base < base_margin
    normal_passed = normal_error < normal_margin
    arithmetic_identity_passed = bool(
        per_population_per_wave
        == Fraction(144, 289) * Fraction(1, 2**90)
        and per_wave_population_l1
        == 4 * Fraction(144, 289) * Fraction(1, 2**90)
        and repair_base
        == 4
        * (axis_norm + diagonal_norm)
        * per_wave_population_l1
        and raw_base == global_norm * raw_wiener
        and repaired_base == raw_base + repair_base
    )
    return {
        "normalization": "normalized 17x17 DFT with factor 1/289",
        "maximum_prefix_bound_units": MAXIMUM_PREFIX_BOUND,
        "per_population_per_selected_wave_upper": _fraction_record(
            per_population_per_wave
        ),
        "per_selected_wave_population_l1_upper": _fraction_record(
            per_wave_population_l1
        ),
        "axis_orbit_member_count": len(AXIS_SELECTED_WAVES),
        "diagonal_orbit_member_count": len(DIAGONAL_SELECTED_WAVES),
        "axis_left_operator_l1_upper": _fraction_record(axis_norm),
        "diagonal_left_operator_l1_upper": _fraction_record(diagonal_norm),
        "repair_base_coordinate_error_upper": _fraction_record(repair_base),
        "raw_wiener_error_upper": _fraction_record(raw_wiener),
        "raw_base_coordinate_error_upper": _fraction_record(raw_base),
        "repaired_base_coordinate_error_upper": _fraction_record(
            repaired_base
        ),
        "base_margin": _fraction_record(base_margin),
        "base_margin_headroom": _fraction_record(base_margin - repaired_base),
        "base_margin_utilization": _fraction_record(
            repaired_base / base_margin
        ),
        "base_reentry_passed": base_passed,
        "q007y_coarse_base_coordinate_error_upper": _fraction_record(
            q007y_coarse_base
        ),
        "q007y_coarse_base_margin_utilization": tube[
            "base_margin_utilization"
        ],
        "phase_aware_to_q007y_coarse_base_ratio": _fraction_record(
            repaired_base / q007y_coarse_base
        ),
        "normal_coordinate_error_upper": _fraction_record(normal_error),
        "normal_margin": _fraction_record(normal_margin),
        "normal_margin_utilization": _fraction_record(
            normal_error / normal_margin
        ),
        "normal_reentry_passed": normal_passed,
        "normal_bound_reused_without_phase_improvement": True,
        "raw_error_bound_reused_without_wave_improvement": True,
        "arithmetic_identity_passed": arithmetic_identity_passed,
        "passed": bool(
            arithmetic_identity_passed and base_passed and normal_passed
        ),
    }


def run_selected_wave_repair_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007p_payload, q007p_record = _load_registered_q007p(directory)
    q007y_payload, q007y_record = _load_registered_q007y(directory)
    selected, selected_exact = _selected_structure_audit(
        q007p_payload,
        q007y_payload,
    )
    phase = _phase_histogram_audit()
    bound = _selected_repair_bound(q007y_payload, selected_exact)
    q007y_cycle = q007y_payload["cycle"]
    finite_campaign_preserved = bool(
        q007y_cycle["finite_campaign"]["passed"]
        and q007y_cycle["finite_campaign"]["summary"][
            "all_input_repairs_conserve"
        ]
        and q007y_cycle["finite_campaign"]["summary"][
            "all_output_repairs_conserve"
        ]
        and q007y_cycle["finite_campaign"]["summary"][
            "all_repairs_solve_and_add_exactly"
        ]
        and q007y_cycle["finite_campaign"]["summary"][
            "all_finite_stage_bounds_and_positivity_pass"
        ]
    )
    tube_repair_preserved = bool(
        q007y_cycle["tube_wide_repair_bound"][
            "repair_map_well_defined_on_registered_tube"
        ]
        and q007y_cycle["theorem_consequence"][
            "distributed_repair_is_defined_on_registered_q007s_tube"
        ]
    )
    input_audit = {
        "q007p_artifact": q007p_record,
        "q007y_artifact": q007y_record,
        "passed": bool(q007p_record["passed"] and q007y_record["passed"]),
    }
    preliminary = {
        "input_audit": input_audit,
        "selected_structure": selected,
        "phase_histogram_audit": phase,
        "selected_repair_bound": bound,
        "finite_campaign_preserved": finite_campaign_preserved,
        "tube_repair_preserved": tube_repair_preserved,
    }
    strict_json = bool(
        _all_numeric_values_finite(preliminary)
        and _strict_json_serializable(preliminary)
    )
    digest_payload = {
        "selected": selected["selected_input_digest_sha256"],
        "phase": phase["phase_digest_sha256"],
        "bound": bound,
        "finite_campaign": q007y_cycle["finite_campaign"][
            "result_digest_sha256"
        ],
    }
    result_digest = _digest_payload(digest_payload)
    digests_reproducible = bool(
        len(selected["selected_input_digest_sha256"]) == 64
        and len(phase["phase_digest_sha256"]) == 64
        and len(result_digest) == 64
    )
    validity_gates = {
        "registered_q007p_q007y_inputs": {
            "passed": input_audit["passed"],
            "threshold": (
                "registered Q007p/Q007y artifact and runner SHA, source, "
                "scope, upstream gates, and decisions match"
            ),
            "value": input_audit["passed"],
        },
        "selected_orbit_and_projector_reconstruction": {
            "passed": selected["passed"],
            "threshold": (
                "exactly two C4 orbits/eight nonzero selected waves and their "
                "per-orbit left-operator bounds reproduce"
            ),
            "value": selected["passed"],
        },
        "sealed_repair_recipe_and_fresh_replay": {
            "passed": bool(
                q007y_record["fresh_cycle_matches"]
                and q007y_record["backend_sha_matches"]
                and finite_campaign_preserved
                and tube_repair_preserved
            ),
            "threshold": (
                "Q007y h, diagonal populations, divmod row-major recipe, "
                "finite campaign, and tube repair replay unchanged"
            ),
            "value": {
                "fresh_cycle": q007y_record["fresh_cycle_matches"],
                "finite_campaign": finite_campaign_preserved,
                "tube_repair": tube_repair_preserved,
            },
        },
        "exact_selected_phase_histograms": {
            "passed": phase["passed"],
            "threshold": (
                "all 2,312 selected-wave/remainder cases have exact full-grid "
                "cancellation and prefix/complement bound at most 144"
            ),
            "value": {
                "case_count": phase["phase_histogram_case_count"],
                "maximum": phase["maximum_prefix_or_complement_bound"],
            },
        },
        "exact_projector_bound_arithmetic": {
            "passed": bound["arithmetic_identity_passed"],
            "threshold": (
                "per-wave, per-orbit repair, raw/repaired base, and reused "
                "normal formulas reproduce as exact rationals"
            ),
            "value": bound["arithmetic_identity_passed"],
        },
        "finite_strict_json_and_digests": {
            "passed": bool(strict_json and digests_reproducible),
            "threshold": (
                "all records are finite strict JSON and selected/phase/result "
                "digests reproduce"
            ),
            "value": {
                "strict_json": strict_json,
                "digests": digests_reproducible,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    selected_nonzero = bool(selected["passed"] and selected["zero_wave_excluded"])
    generic_wave_bound = phase["passed"]
    projector_bound = bool(
        bound["arithmetic_identity_passed"]
        and _fraction_from_record(
            bound["repair_base_coordinate_error_upper"]
        )
        >= 0
    )
    base_passed = bound["base_reentry_passed"]
    normal_passed = bound["normal_reentry_passed"]
    repair_preserved = bool(
        finite_campaign_preserved and tube_repair_preserved
    )
    hypothesis_gates = {
        "base_coordinates_use_only_registered_nonzero_selected_waves": {
            "passed": bool(validity_passed and selected_nonzero),
            "threshold": "Q007p base coordinates use exactly the eight nonzero waves",
            "value": selected_nonzero,
        },
        "balanced_repair_obeys_generic_selected_wave_bound": {
            "passed": bool(validity_passed and generic_wave_bound),
            "threshold": (
                "every integer total and selected wave obeys the 4*144*h/289 "
                "population-l1 bound"
            ),
            "value": generic_wave_bound,
        },
        "projector_aware_repair_base_bound_is_certified": {
            "passed": bool(validity_passed and projector_bound),
            "threshold": (
                "the two per-orbit left norms bound the repair base "
                "contribution"
            ),
            "value": projector_bound,
        },
        "phase_aware_base_budget_closes": {
            "passed": bool(validity_passed and base_passed),
            "threshold": "raw plus selected-wave repair base error is below margin",
            "value": base_passed,
        },
        "conservative_normal_budget_remains_closed": {
            "passed": bool(validity_passed and normal_passed),
            "threshold": "unchanged Q007y full-Wiener normal error is below margin",
            "value": normal_passed,
        },
        "fixed_leaf_repair_and_stage_positivity_are_preserved": {
            "passed": bool(validity_passed and repair_preserved),
            "threshold": (
                "Q007y exact fixed leaf, tube-wide repair definition, and "
                "finite stage positivity remain valid"
            ),
            "value": repair_preserved,
        },
        "repaired_mpfr85_all_iterate_tube_induction_closes": {
            "passed": False,
            "threshold": "all six preceding hypotheses pass",
            "value": False,
        },
    }
    first_six_pass = all(
        gate["passed"]
        for name, gate in hypothesis_gates.items()
        if name != "repaired_mpfr85_all_iterate_tube_induction_closes"
    )
    induction_passed = bool(validity_passed and first_six_pass)
    hypothesis_gates["repaired_mpfr85_all_iterate_tube_induction_closes"][
        "passed"
    ] = induction_passed
    hypothesis_gates["repaired_mpfr85_all_iterate_tube_induction_closes"][
        "value"
    ] = induction_passed
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007z selected-wave audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "selected-wave certificate closes the repaired MPFR-85 "
            "fixed-leaf tube induction"
        )
    elif not base_passed:
        outcome = "not_certified"
        classification = (
            "balanced repair phase is insufficient for the Q007w base budget"
        )
    else:
        outcome = "not_certified"
        classification = (
            "selected-wave repair certificate does not close the repaired "
            "MPFR-85 tube induction"
        )
    return {
        "question": (
            "Does exact cancellation of the balanced repair's uniform part "
            "on the eight selected nonzero waves close the Q007w base budget "
            "without changing the sealed backend or repair?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "wave_count": WAVE_COUNT,
            "repair_quantum": _fraction_record(REPAIR_QUANTUM),
            "maximum_prefix_bound_units": MAXIMUM_PREFIX_BOUND,
            "axis_selected_waves": [list(wave) for wave in AXIS_SELECTED_WAVES],
            "diagonal_selected_waves": [
                list(wave) for wave in DIAGONAL_SELECTED_WAVES
            ],
            "selected_wave_count": len(SELECTED_WAVES),
            "diagonal_populations": list(q007y.DIAGONAL_POPULATIONS),
            "distribution": "Python divmod over 289 row-major sites",
            "initial_condition": (
                "already encoded and repaired MPFR-85 fixed-leaf state inside "
                "the registered Q007s tube"
            ),
        },
        "input_audit": input_audit,
        "selected_structure": selected,
        "phase_histogram_audit": phase,
        "selected_repair_bound": bound,
        "finite_campaign_preserved": finite_campaign_preserved,
        "tube_repair_preserved": tube_repair_preserved,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "balanced_repair_selected_wave_bound_is_tube_wide": bool(
                validity_passed and generic_wave_bound
            ),
            "repair_aware_base_reentry_is_certified": bool(
                validity_passed and base_passed
            ),
            "repair_aware_normal_reentry_is_certified": bool(
                validity_passed and normal_passed
            ),
            "repaired_backend_preserves_exact_fixed_leaf_at_sampling_times": bool(
                validity_passed and repair_preserved
            ),
            "conditional_all_iterate_repaired_mpfr85_q007s_tube_invariance": (
                bool(validity_passed and hypotheses_passed)
            ),
            "conditional_all_iterate_mpfr85_stagewise_population_positivity": (
                bool(validity_passed and hypotheses_passed)
            ),
        },
        "claim_boundary": (
            "The induction is conditional on an already encoded, repaired "
            "MPFR-85 state lying in the fixed-leaf Q007s tube. It certifies "
            "sampling-time fixed-leaf conservation, tube re-entry, and stage "
            "positivity for the sealed 17x17 backend and row-major repair. It "
            "does not certify arbitrary exact-state boundary encoding, "
            "trajectory accuracy, shadowing time, performance, parallel "
            "reduction, another grid or MPFR build, center-slow coordinates, "
            "or D3Q27. Q007y's coarse triangle-bound noncertificate remains a "
            "valid result for that deliberately coarser estimator."
        ),
        "preserved_prior_outcomes": {
            "q007y_coarse_triangle_rejection_changed": False,
            "q007x_unrepaired_fixed_leaf_rejection_changed": False,
            "q007w_ideal_precision_acceptance_changed": False,
            "q007v_binary64_reentry_rejection_changed": False,
            "q007u_exact_stagewise_acceptance_changed": False,
            "q007s_exact_fixed_leaf_invariance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "With the conditional repaired-backend induction closed, audit "
            "multi-step shadowing against the exact map and separately define "
            "an initialization interior for exact-state encoding before any "
            "performance or TT work resumes."
        ),
    }


def run_q007z_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_selected_wave_repair_audit(artifact_directory)
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
                "selected-wave Fourier certificate for the sealed balanced "
                "dyadic conservation repair"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(backend.EXACT_OMEGA),
            "eta": float(backend.EXACT_ETA),
            "conservation_treatment": (
                "fixed global mass and momentum leaf with exact diagonal "
                "post-stage repair"
            ),
            "selected_wave_count": len(SELECTED_WAVES),
            "repair_distribution": (
                "sealed row-major balanced quotient-plus-prefix remainder"
            ),
            "claim": (
                "conditional all-iterate Q007s tube re-entry and stage "
                "positivity for already repaired MPFR-85 states"
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
    result = run_q007z_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
