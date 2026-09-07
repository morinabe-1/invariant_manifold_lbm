"""Q012c1: viscosity-preserving damping, full quadratic replay and normal ordering."""

from __future__ import annotations

import argparse
import copy
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from research import d3q27 as d3
from research import d3q27_damping as damping
from research import d3q27_quadratic as quadratic
from research import d3q27_spectra as spectra
from research import q012a_d3q27_foundation as q012a
from research import q012b_d3q27_spectral as q012b
from research import q012c_d3q27_preflight as q012c
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

GRID_SIZES = q012c.GRID_SIZES
OMEGAS = q012c.OMEGAS
CONFIGURATIONS = ((1, 0.0),) + tuple((p, e) for p in damping.POWERS for e in damping.ETAS)
Q012C_ARTIFACT_SHA256 = "3dc9da853cbea183546d5646916e50828faaa89156ca217d16e1b6dc68cf886d"
Q012C_RESULT_SHA256 = "79a17890a273ca26ab297a8c98a0fe550b8eae1fedc74f3a2452c836f39b3863"
Q012C_PATH = q012a.ARTIFACT_DIRECTORY / "q012c_d3q27_preflight.json"
HELPERS = (
    ("lattice", d3),
    ("spectra", spectra),
    ("quadratic", quadratic),
    ("foundation_runner", q012a),
    ("spectral_runner", q012b),
    ("preflight_runner", q012c),
    ("damping", damping),
)


def input_audit() -> dict[str, Any]:
    artifact = json.loads(Q012C_PATH.read_text(encoding="utf-8"))
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    checks = {
        "artifact_seal": _file_sha256(Q012C_PATH) == Q012C_ARTIFACT_SHA256,
        "result_digest": q012a._digest(cycle) == digest == Q012C_RESULT_SHA256,
        "runner_seal": _file_sha256(Path(q012c.__file__)) == artifact["runner_source"]["sha256"],
        "prior_valid_rejection_preserved": artifact["study_gate"] == "passed"
        and artifact["scientific_outcome"] == "rejected"
        and len(cycle["validity_gates"]) == 8
        and all(cycle["validity_gates"].values())
        and cycle["selected_family"] is None
        and not any(f["jointly_viable"] for f in cycle["families"]),
        "prior_prerequisites_still_sealed": q012c.input_audit()["passed"],
    }
    for name, module in HELPERS[:5]:
        checks[name + "_source_seal"] = (
            _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
        )
    return {"filename": Q012C_PATH.name, "checks": checks, "passed": all(checks.values())}


def prior_baselines() -> dict[tuple[int, float], dict]:
    artifact = json.loads(Q012C_PATH.read_text(encoding="utf-8"))
    return {(r["size"], r["omega"]): r for r in artifact["cycle"]["conditions"] if r["shell"] == 3}


def condition_cycle(
    context: damping.CoefficientContext,
    power: int,
    eta: float,
    controls: dict[str, Any],
    prior: dict | None = None,
) -> dict[str, Any]:
    screen = q012c.pack_pairs(damping.coefficient_screen(context, eta, power))
    normal = quadratic.normal_ordering(damping.scaled_grid(context.grid, eta, power), 3)
    baseline = None
    if eta == 0:
        baseline = {
            "all_pair_metrics_equal": prior is not None
            and all(screen.get(key) == value for key, value in prior["coefficient_screen"].items()),
            "normal_inventory_equal": prior is not None and normal == prior["normal_ordering"],
        }
        baseline["passed"] = all(baseline.values())
        map_gate = hydro_gate = hessian_gate = True
    else:
        map_records = [
            r for r in controls["map"]["records"] if (r["power"], r["eta"]) == (power, eta)
        ]
        hydro_records = [
            r
            for r in controls["hydrodynamics"]["records"]
            if (r["power"], r["eta"], r["omega"]) == (power, eta, context.omega)
        ]
        hessian_records = [
            r for r in controls["hessian"]["records"] if (r["power"], r["eta"]) == (power, eta)
        ]
        map_gate = len(map_records) == 1 and all(r["passed"] for r in map_records)
        hydro_gate = len(hydro_records) == 4 and all(r["passed"] for r in hydro_records)
        hessian_gate = len(hessian_records) == 1 and all(r["passed"] for r in hessian_records)
    return {
        "size": context.size,
        "omega": context.omega,
        "power": power,
        "eta": eta,
        "map": "unmodified BGK baseline" if eta == 0 else f"post-stream (I-eta D^{power}) BGK",
        "real_coordinate_count": 104,
        "coefficient_screen": screen,
        "normal_ordering": normal,
        "baseline_reproduction": baseline,
        "map_control_passed": map_gate,
        "hydrodynamic_control_passed": hydro_gate,
        "hessian_control_passed": hessian_gate,
        "jointly_prequalified": screen["coefficient_prequalified"]
        and normal["normal_ordering_prequalified"]
        and map_gate
        and hydro_gate
        and hessian_gate,
    }


def table_filename(size: int, omega: float, power: int, eta: float) -> str:
    return f"n{size}_w{omega:g}_p{power}_eta{eta:g}".replace(".", "p") + ".json"


def write_table(directory: Path, cycle: dict[str, Any]) -> dict[str, Any]:
    directory.mkdir(parents=True, exist_ok=True)
    filename = table_filename(cycle["size"], cycle["omega"], cycle["power"], cycle["eta"])
    digest = q012a._digest(cycle)
    artifact = {"schema_version": 1, "cycle": cycle, "result_digest_sha256": digest}
    path = directory / filename
    path.write_text(
        json.dumps(artifact, allow_nan=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    summary = {key: value for key, value in cycle.items() if key != "coefficient_screen"}
    summary["coefficient_screen"] = {
        key: value
        for key, value in cycle["coefficient_screen"].items()
        if key not in ("pair_columns", "pair_rows")
    }
    return {
        **summary,
        "table": {
            "filename": filename,
            "sha256": _file_sha256(path),
            "result_digest_sha256": digest,
        },
    }


def classify_families(conditions: list[dict]) -> tuple[list[dict], dict | None]:
    families = []
    for power in damping.POWERS:
        for eta in damping.ETAS:
            for omega in OMEGAS:
                rows = [
                    r
                    for r in conditions
                    if (r["power"], r["eta"], r["omega"]) == (power, eta, omega)
                ]
                coverage = len(rows) == 3 and sorted(r["size"] for r in rows) == list(GRID_SIZES)
                families.append(
                    {
                        "power": power,
                        "eta": eta,
                        "omega": omega,
                        "real_coordinate_count": 104,
                        "leading_viscosity_preserved": power == 2,
                        "coefficient_all_grids": coverage
                        and all(r["coefficient_screen"]["coefficient_prequalified"] for r in rows),
                        "normal_ordering_all_grids": coverage
                        and all(r["normal_ordering"]["normal_ordering_prequalified"] for r in rows),
                        "jointly_viable": coverage and all(r["jointly_prequalified"] for r in rows),
                    }
                )
    candidates = [f for f in families if f["power"] == 2 and f["jointly_viable"]]
    chosen = (
        None
        if not candidates
        else copy.deepcopy(min(candidates, key=lambda f: (f["eta"], f["omega"])))
    )
    return families, chosen


def replay_family(
    chosen: dict | None,
    conditions: list[dict],
    controls: dict,
    progress: Callable[[dict], None] | None,
) -> dict[str, Any]:
    configuration = (
        {"power": 2, "eta": 0.05, "omega": 1.2}
        if chosen is None
        else {key: chosen[key] for key in ("power", "eta", "omega")}
    )
    records = []
    for size in GRID_SIZES:
        # Fresh frames, sectors, full grid and ALL 3,081 solves. No result cache.
        context = damping.build_context(size, configuration["omega"])
        cycle = condition_cycle(context, configuration["power"], configuration["eta"], controls)
        original = [
            r
            for r in conditions
            if (r["size"], r["omega"], r["power"], r["eta"])
            == (size, configuration["omega"], configuration["power"], configuration["eta"])
        ]
        digest = q012a._digest(cycle)
        record = {
            "size": size,
            "pair_count": cycle["coefficient_screen"]["pair_count"],
            "result_digest_sha256": digest,
            "passed": context.frame_audit["passed"]
            and len(original) == 1
            and digest == original[0]["table"]["result_digest_sha256"],
        }
        records.append(record)
        if progress is not None:
            progress({"phase": "independent_family_replay", **configuration, **record})
    return {
        "scope": "three fresh grids for chosen family or preregistered fixed control; not all 108 conditions rerun",
        "configuration": configuration,
        "records": records,
        "passed": len(records) == 3 and all(r["passed"] for r in records),
    }


def run_study(directory: Path, progress: Callable[[dict], None] | None = None) -> dict[str, Any]:
    inputs = input_audit()
    controls, frames_evidence, conditions, replay = {}, [], [], None
    numerical_failure = None
    if inputs["passed"]:
        controls = {
            "map": damping.map_controls(),
            "hydrodynamics": damping.hydrodynamic_controls(),
            "hessian": damping.hessian_controls(),
            "direct_grid": damping.direct_grid_control(),
        }
        if progress is not None:
            progress(
                {
                    "phase": "independent_controls",
                    "gates": {key: value["passed"] for key, value in controls.items()},
                }
            )
        if all(control["passed"] for control in controls.values()):
            baselines = prior_baselines()
            for size in GRID_SIZES:
                for omega in OMEGAS:
                    context = damping.build_context(size, omega)
                    frames_evidence.append({"size": size, "omega": omega, **context.frame_audit})
                    for power, eta in CONFIGURATIONS:
                        try:
                            cycle = condition_cycle(
                                context,
                                power,
                                eta,
                                controls,
                                baselines[size, omega] if eta == 0 else None,
                            )
                        except damping.HomologicalSvdFailure as error:
                            numerical_failure = error.evidence
                            if progress is not None:
                                progress(
                                    {
                                        "phase": "numerical_obstruction",
                                        "completed_conditions": len(conditions),
                                        "size": size,
                                        "omega": omega,
                                        "power": power,
                                        "eta": eta,
                                        "diagnostics": numerical_failure["diagnostics"],
                                    }
                                )
                            break
                        condition = write_table(directory, cycle)
                        conditions.append(condition)
                        if progress is not None:
                            screen = condition["coefficient_screen"]
                            progress(
                                {
                                    "phase": "campaign",
                                    "completed": len(conditions),
                                    "total": 108,
                                    "size": size,
                                    "omega": omega,
                                    "power": power,
                                    "eta": eta,
                                    "statuses": screen["status_counts"],
                                    "residual_only_failures": screen["residual_only_failure_count"],
                                    "normal_gap": condition["normal_ordering"][
                                        "normal_modulus_gap"
                                    ],
                                    "jointly_prequalified": condition["jointly_prequalified"],
                                }
                            )
                    if numerical_failure is not None:
                        break
                if numerical_failure is not None:
                    break
    families, chosen = classify_families(conditions)
    coverage = len(conditions) == 108 and {
        (r["size"], r["omega"], r["power"], r["eta"]) for r in conditions
    } == {(n, w, p, e) for n in GRID_SIZES for w in OMEGAS for p, e in CONFIGURATIONS}
    if coverage:
        replay = replay_family(chosen, conditions, controls, progress)
    baseline_records = [r for r in conditions if r["eta"] == 0]
    gates = {
        "sealed_inputs": inputs["passed"],
        "registered_108_conditions": coverage,
        "independent_map_hydrodynamic_hessian_grid_controls": len(controls) == 4
        and all(control["passed"] for control in controls.values()),
        "baseline_all_pair_reproduction": len(baseline_records) == 12
        and all(r["baseline_reproduction"]["passed"] for r in baseline_records),
        "cluster_frame_structure": len(frames_evidence) == 12
        and all(r["passed"] for r in frames_evidence),
        "every_pair_and_fixed_leaf_dimension": coverage
        and all(
            r["coefficient_screen"]["coverage_passed"] and r["normal_ordering"]["coverage_passed"]
            for r in conditions
        ),
        "coefficient_structure": coverage
        and all(r["coefficient_screen"]["maximum_structural_error"] <= 5e-12 for r in conditions),
        "independent_three_grid_family_replay": replay is not None and replay["passed"],
        "finite_evidence": _all_numeric_values_finite(
            (controls, frames_evidence, conditions, replay, numerical_failure)
        ),
    }
    outcome = (
        "inconclusive"
        if not all(gates.values())
        else "accepted"
        if chosen is not None
        else "rejected"
    )
    cycle = {
        "question": "Can post-stream biharmonic damping preserve leading viscosity and repair all 104-coordinate quadratic/normal-ordering gates?",
        "map": "modified D3Q27 BGK on a fixed four-conservation leaf; unmodified baseline rejection retained",
        "input_audit": inputs,
        "controls": controls,
        "frame_audits": frames_evidence,
        "conditions": conditions,
        "families": families,
        "selected_family": chosen,
        "independent_replay": replay,
        "numerical_failure": numerical_failure,
        "validity_gates": gates,
        "study_validity": "passed" if all(gates.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite-degree/sample prequalification of a modified map only; no SSM existence, uniqueness, nonlinear normal attraction, global positivity, TT advantage or unmodified BGK reduction",
        "next_question": "Q012d: dense quadratic W/R for the explicitly selected modified map"
        if outcome == "accepted"
        else "Separate persistent coefficient precision/resonance and normal-ordering failures before preregistering a new repair",
    }
    cycle["result_digest_sha256"] = q012a._digest(cycle)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "runner_source": {"filename": Path(__file__).name, "sha256": _file_sha256(Path(__file__))},
        "helper_sources": {
            name: {
                "filename": Path(module.__file__).name,
                "sha256": _file_sha256(Path(module.__file__)),
            }
            for name, module in HELPERS
        },
        "table_directory": directory.name,
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_study(
        args.output.with_suffix(""), lambda record: print(json.dumps(record), flush=True)
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, allow_nan=False, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "study_gate": result["study_gate"],
                "scientific_outcome": result["scientific_outcome"],
                "selected_family": result["cycle"]["selected_family"],
            }
        )
    )
    if result["study_gate"] != "passed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
