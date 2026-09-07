"""Q012c1a: separate exception-only SVD protocol for the full damping study."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from research import d3q27_damping as damping
from research import d3q27_quadratic as quadratic
from research import d3q27_svd_fallback as fallback
from research import q012a_d3q27_foundation as q012a
from research import q012c1_d3q27_damping as prior
from research import q012c_d3q27_preflight as q012c
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012c1_d3q27_damping.json"
PRIOR_SHA256 = "cc3410aafc0415f84ae1a263a3f3e18b043398bd38bf34332867ec2e0a4b5276"
PRIOR_RESULT = "89964f26704c5c312ebb286088bf758d0cf463b9bc46e6a176f79ae0a74a699e"
HELPERS = prior.HELPERS + (("damping_runner", prior), ("svd_fallback", fallback))


def prior_artifact() -> dict:
    return json.loads(PRIOR_PATH.read_text(encoding="utf-8"))


def input_audit() -> dict:
    artifact = prior_artifact()
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    checks = {
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA256,
        "result_digest": q012a._digest(cycle) == digest == PRIOR_RESULT,
        "runner_seal": _file_sha256(Path(prior.__file__)) == artifact["runner_source"]["sha256"],
        "prior_inconclusive_preserved": artifact["study_gate"] == "failed"
        and artifact["scientific_outcome"] == "inconclusive"
        and cycle["selected_family"] is None
        and len(cycle["conditions"]) == 4
        and cycle["numerical_failure"]["operator_dimension"] == 108,
        "prior_inputs_still_sealed": prior.input_audit()["passed"],
    }
    for name, module in prior.HELPERS:
        checks[name + "_source_seal"] = (
            _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
        )
    for row in cycle["conditions"]:
        table = row["table"]
        path = PRIOR_PATH.parent / artifact["table_directory"] / table["filename"]
        stored = json.loads(path.read_text(encoding="utf-8"))
        checks[table["filename"]] = (
            _file_sha256(path) == table["sha256"]
            and q012a._digest(stored["cycle"])
            == stored["result_digest_sha256"]
            == table["result_digest_sha256"]
        )
    return {"filename": PRIOR_PATH.name, "checks": checks, "passed": all(checks.values())}


def condition_cycle(
    context: damping.CoefficientContext,
    power: int,
    eta: float,
    controls: dict,
    baseline: dict | None,
    partials: dict,
) -> dict:
    screen, backend = fallback.coefficient_screen(context, eta, power)
    screen = q012c.pack_pairs(screen)
    normal = quadratic.normal_ordering(damping.scaled_grid(context.grid, eta, power), 3)
    baseline_reproduction = None
    if eta == 0:
        baseline_reproduction = {
            "all_pair_metrics_equal": baseline is not None
            and all(
                screen.get(key) == value for key, value in baseline["coefficient_screen"].items()
            ),
            "normal_inventory_equal": baseline is not None
            and normal == baseline["normal_ordering"],
        }
        baseline_reproduction["passed"] = all(baseline_reproduction.values())
        map_gate = hydro_gate = hessian_gate = True
    else:
        maps = [r for r in controls["map"]["records"] if (r["power"], r["eta"]) == (power, eta)]
        hydro = [
            r
            for r in controls["hydrodynamics"]["records"]
            if (r["power"], r["eta"], r["omega"]) == (power, eta, context.omega)
        ]
        hessian = [
            r for r in controls["hessian"]["records"] if (r["power"], r["eta"]) == (power, eta)
        ]
        map_gate = len(maps) == 1 and all(r["passed"] for r in maps)
        hydro_gate = len(hydro) == 4 and all(r["passed"] for r in hydro)
        hessian_gate = len(hessian) == 1 and all(r["passed"] for r in hessian)
    cycle = {
        "size": context.size,
        "omega": context.omega,
        "power": power,
        "eta": eta,
        "map": "unmodified BGK baseline" if eta == 0 else f"post-stream (I-eta D^{power}) BGK",
        "real_coordinate_count": 104,
        "coefficient_screen": screen,
        "normal_ordering": normal,
        "baseline_reproduction": baseline_reproduction,
        "map_control_passed": map_gate,
        "hydrodynamic_control_passed": hydro_gate,
        "hessian_control_passed": hessian_gate,
        "jointly_prequalified": screen["coefficient_prequalified"]
        and normal["normal_ordering_prequalified"]
        and map_gate
        and hydro_gate
        and hessian_gate,
    }
    key = context.size, context.omega, power, eta
    cycle["prior_partial_reproduction"] = (
        None if key not in partials else q012a._digest(cycle) == partials[key]
    )
    cycle["backend"] = backend
    return cycle


def write_table(directory: Path, cycle: dict) -> dict:
    summary = prior.write_table(directory, cycle)
    summary["backend"] = {
        key: value for key, value in summary["backend"].items() if key != "pair_drivers"
    }
    return summary


def replay_family(
    chosen: dict | None,
    conditions: list[dict],
    controls: dict,
    partials: dict,
    progress: Callable | None,
) -> dict:
    configuration = (
        {"power": 2, "eta": 0.05, "omega": 1.2}
        if chosen is None
        else {key: chosen[key] for key in ("power", "eta", "omega")}
    )
    records = []
    for size in prior.GRID_SIZES:
        context = damping.build_context(size, configuration["omega"])
        cycle = condition_cycle(
            context, configuration["power"], configuration["eta"], controls, None, partials
        )
        original = [
            r
            for r in conditions
            if r["size"] == size and all(r[key] == value for key, value in configuration.items())
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
        "scope": "three fresh grids, frames, spectra and all pair solves; not all 108 conditions rerun",
        "configuration": configuration,
        "records": records,
        "passed": len(records) == 3 and all(r["passed"] for r in records),
    }


def run_study(directory: Path, progress: Callable | None = None) -> dict:
    inputs = input_audit()
    controls, frames_evidence, conditions, replay = {}, [], [], None
    numerical_failure = None
    if inputs["passed"]:
        old = prior_artifact()["cycle"]
        partials = {
            (r["size"], r["omega"], r["power"], r["eta"]): r["table"]["result_digest_sha256"]
            for r in old["conditions"]
        }
        controls = {
            "backend": fallback.backend_controls(old["numerical_failure"]),
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
            baselines = prior.prior_baselines()
            for size in prior.GRID_SIZES:
                for omega in prior.OMEGAS:
                    context = damping.build_context(size, omega)
                    frames_evidence.append({"size": size, "omega": omega, **context.frame_audit})
                    for power, eta in prior.CONFIGURATIONS:
                        try:
                            cycle = condition_cycle(
                                context,
                                power,
                                eta,
                                controls,
                                baselines[size, omega] if eta == 0 else None,
                                partials,
                            )
                        except np.linalg.LinAlgError as error:
                            numerical_failure = {
                                "size": size,
                                "omega": omega,
                                "power": power,
                                "eta": eta,
                                "error": str(error),
                            }
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
                                    "fallbacks": condition["backend"]["fallback_count"],
                                    "coefficient": screen["coefficient_prequalified"],
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
    families, chosen = prior.classify_families(conditions)
    coverage = len(conditions) == 108 and {
        (r["size"], r["omega"], r["power"], r["eta"]) for r in conditions
    } == {
        (n, w, p, e)
        for n in prior.GRID_SIZES
        for w in prior.OMEGAS
        for p, e in prior.CONFIGURATIONS
    }
    if coverage:
        replay = replay_family(chosen, conditions, controls, partials, progress)
    baselines = [r for r in conditions if r["eta"] == 0]
    partial_checks = [
        r["prior_partial_reproduction"]
        for r in conditions
        if r["prior_partial_reproduction"] is not None
    ]
    gates = {
        "sealed_inputs": inputs["passed"],
        "registered_108_conditions": coverage,
        "independent_backend_controls": bool(controls) and controls["backend"]["passed"],
        "independent_map_hydrodynamic_hessian_grid_controls": len(controls) == 5
        and all(v["passed"] for v in controls.values()),
        "baseline_all_pair_reproduction": len(baselines) == 12
        and all(r["baseline_reproduction"]["passed"] for r in baselines),
        "prior_four_conditions_unchanged": len(partial_checks) == 4 and all(partial_checks),
        "cluster_frame_structure": len(frames_evidence) == 12
        and all(r["passed"] for r in frames_evidence),
        "every_pair_and_fixed_leaf_dimension": coverage
        and all(
            r["coefficient_screen"]["coverage_passed"] and r["normal_ordering"]["coverage_passed"]
            for r in conditions
        ),
        "coefficient_structure_and_backend_integrity": coverage
        and all(
            r["coefficient_screen"]["maximum_structural_error"] <= 5e-12 and r["backend"]["passed"]
            for r in conditions
        ),
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
        "protocol": "Q012c1a exception-only SVD fallback; Q012c1 remains inconclusive",
        "question": "Does viscosity-preserving damping pass the complete 104-coordinate preflight after a guarded SVD nonconvergence fallback?",
        "map": "modified fixed-leaf D3Q27 BGK; unmodified BGK rejection retained",
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
        "claim_boundary": "finite-degree/sample prequalification of a modified map; no existence, uniqueness, nonlinear normal attraction, global positivity, TT advantage or original BGK reduction",
        "next_question": "Q012d: dense quadratic W/R for selected modified map"
        if outcome == "accepted"
        else "Separate remaining coefficient and normal-ordering failures without loosening gates",
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
    result = run_study(args.output.with_suffix(""), lambda r: print(json.dumps(r), flush=True))
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
