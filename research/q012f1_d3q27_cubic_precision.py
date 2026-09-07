"""Q012f1 factorial diagnosis with complete selected records and independent replay."""

from __future__ import annotations

import argparse
import json
import os
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import numpy as np

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_cubic_precision as precision
from research import d3q27_damping as damping
from research import q012a_d3q27_foundation as q012a
from research import q012f_d3q27_cubic_preflight as previous
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012f_d3q27_cubic_preflight.json"
PRIOR_SHA = "d3b778ed339c9629dbac57264291aceb32c795a1e6d12e3becb20cf333c57089"
PRIOR_DIGEST = "42208f4a8a6c7d585273ae8d925a6d966cc68e568f08a835ab7f941a41668b34"
HELPERS = previous.HELPERS + (("cubic_runner", previous), ("precision", precision))


def prior_artifact():
    return json.loads(PRIOR_PATH.read_text(encoding="utf-8"))


def input_audit():
    old = prior_artifact()
    cycle = dict(old["cycle"])
    digest = cycle.pop("result_digest_sha256")
    checks = {
        "input_chain": previous.input_audit()["passed"],
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA,
        "cycle_digest": q012a._digest(cycle) == digest == PRIOR_DIGEST,
        "package_source": old["source"] == source_metadata(),
        "runner_source": old["runner_source"]["sha256"] == _file_sha256(Path(previous.__file__)),
        "valid_rejection_retained": old["scientific_outcome"] == "rejected"
        and all(cycle["validity_gates"].values()),
    }
    for name, module in previous.HELPERS:
        checks[name + "_source"] = old["helper_sources"][name]["sha256"] == _file_sha256(
            Path(module.__file__)
        )
    for grid in cycle["grids"]:
        archive = grid["record_archive"]
        path = PRIOR_PATH.parent / archive["filename"]
        checks[f"n{grid['size']}_archive"] = (
            sha256(path.read_bytes()).hexdigest() == archive["sha256"]
            and path.stat().st_size == archive["bytes"]
        )
    checks["previous_replay"] = (
        previous.replay_audit(
            PRIOR_PATH.parent / cycle["independent_replay"]["filename"],
            cycle["input_audit"],
            cycle["grids"],
            old,
        )
        == cycle["independent_replay"]
    )
    return {"checks": checks, "passed": all(checks.values())}


def selection():
    old = prior_artifact()
    last = next(g for g in old["cycle"]["grids"] if g["size"] == 65)
    return precision.selection(
        old, previous.read_records(PRIOR_PATH.parent / last["record_archive"]["filename"])
    )


def metadata():
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "process_id": os.getpid(),
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
    }


def build_inputs(size):
    raw, raw_audit = previous.fresh_model(size)
    old = next(g for g in prior_artifact()["cycle"]["grids"] if g["size"] == size)
    paired, projected = precision.paired_input(raw)
    quadratic = precision.quadratic_audit(paired)
    return {"raw": raw, "paired": paired}, {
        "raw_rebuild": raw_audit,
        "raw_sealed_equal": raw_audit == old["quadratic_rebuild"],
        "paired_input": projected,
        "paired_quadratic_equations": quadratic,
    }


def row_summary(rows):
    result = {}
    for variant in precision.INPUTS:
        result[variant] = {}
        for solver in precision.SOLVERS:
            items = [r["inputs"][variant]["solvers"][solver] for r in rows]
            result[variant][solver] = {
                "count": len(items),
                "failed_count": sum(not r["passed"] for r in items),
                "maximum_external_residual": max(
                    (r["external_relative_residual"] for r in items), default=0.0
                ),
                "maximum_mp128_residual": max(
                    (r["mp128_relative_residual"] for r in items), default=0.0
                ),
                "maximum_full_residual": max(
                    (r["full_relative_residual"] for r in items), default=0.0
                ),
                "maximum_structural_error": max(
                    (r["structural_error"] for r in items), default=0.0
                ),
                "passed": bool(items) and all(r["passed"] for r in items),
            }
    return result


def selected_campaign(size, ordinals, chosen, progress=None):
    models, rebuild = build_inputs(size)
    contexts = {name: cubic.build_context(model) for name, model in models.items()}
    old = next(g for g in prior_artifact()["cycle"]["grids"] if g["size"] == size)
    old_rows = previous.read_records(PRIOR_PATH.parent / old["record_archive"]["filename"])
    rows, triples, waves = [], [], []
    fields = {
        v: {s: {f: [] for f in ("forcing", "response", "reduced")} for s in precision.SOLVERS}
        for v in precision.INPUTS
    }
    for index, ordinal in enumerate(ordinals):
        entries, samples = {}, {}
        for variant in precision.INPUTS:
            entries[variant], samples[variant] = precision.solve_case(
                contexts[variant], ordinal, ordinal in chosen["replay_ordinals"]
            )
        same_operators = all(
            entries["raw"]["problem_arrays"][key] == entries["paired"]["problem_arrays"][key]
            for key in ("external_dynamics", "input_dynamics")
        )
        row = {
            "ordinal": ordinal,
            "inputs": entries,
            "identical_operators": same_operators,
            "original_record_equal": entries["raw"]["original_record"] == old_rows[ordinal],
            "input_effects": {
                solver: {
                    name: damping.relative_error(
                        samples["paired"]["fields"][solver][name],
                        samples["raw"]["fields"][solver][name],
                    )
                    for name in ("forcing", "response", "reduced")
                }
                for solver in precision.SOLVERS
            },
        }
        rows.append(row)
        triples.extend(samples["raw"]["triples"])
        waves.extend([samples["raw"]["wave"]] * len(samples["raw"]["triples"]))
        for variant in precision.INPUTS:
            assert np.array_equal(samples[variant]["triples"], samples["raw"]["triples"])
            for solver in precision.SOLVERS:
                for name in fields[variant][solver]:
                    fields[variant][solver][name].extend(samples[variant]["fields"][solver][name])
        if progress is not None and (index + 1) % 32 == 0:
            progress(
                {
                    "phase": "selected_cubic_diagnosis",
                    "size": size,
                    "completed": index + 1,
                    "total": len(ordinals),
                }
            )
    triples, waves = np.asarray(triples, dtype=np.int64), np.asarray(waves, dtype=np.int64)
    conjugacy = {variant: {} for variant in precision.INPUTS}
    for variant in precision.INPUTS:
        for solver in precision.SOLVERS:
            arrays = {name: np.asarray(data) for name, data in fields[variant][solver].items()}
            conjugacy[variant][solver] = precision.selected_conjugacy(
                triples, waves, arrays, models[variant].conjugate_indices
            )
            conjugacy[variant][solver]["arrays"] = {
                name: chart.array_metadata(value) for name, value in arrays.items()
            }
    result = {
        "size": size,
        "input_rebuild": rebuild,
        "records": rows,
        "summary": row_summary(rows),
        "conjugacy": conjugacy,
        "selection_arrays": {
            "triples": chart.array_metadata(triples),
            "waves": chart.array_metadata(waves),
        },
        "coverage": [r["ordinal"] for r in rows] == list(ordinals)
        and all(v[s]["coverage"] for v in conjugacy.values() for s in precision.SOLVERS),
    }
    return result, contexts


def worker(progress=None):
    inputs, chosen, grids = input_audit(), selection(), []
    if not inputs["passed"]:
        raise ValueError("sealed Q012f input audit failed; diagnosis was not started")
    for size in cubic.SIZES:
        result, _ = selected_campaign(size, chosen["replay_ordinals"], chosen, progress)
        grids.append({key: result[key] for key in ("size", "input_rebuild", "records")})
    evidence = {"input_audit": inputs, "selection_digest": chosen["digest_sha256"], "grids": grids}
    return {
        **metadata(),
        "kind": "Q012f1 independent conjugacy-closed replay",
        "evidence": evidence,
        "evidence_digest_sha256": q012a._digest(evidence),
    }


def replay_audit(path, inputs, chosen, grids, current):
    old = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "input_audit": inputs,
        "selection_digest": chosen["digest_sha256"],
        "grids": [
            {"size": g["size"], "input_rebuild": g["input_rebuild"], "records": g["replay_records"]}
            for g in grids
        ],
    }
    checks = {
        "kind": old["kind"] == "Q012f1 independent conjugacy-closed replay",
        "separate_process": old["process_id"] != current["process_id"],
        "sources": all(old[k] == current[k] for k in ("source", "runner_source", "helper_sources")),
        "digest": q012a._digest(old["evidence"]) == old["evidence_digest_sha256"],
        "all_values_equal": old["evidence"] == expected,
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "checks": checks,
        "passed": all(checks.values()),
        "evidence_digest_sha256": old["evidence_digest_sha256"],
        "worker_process_id": old["process_id"],
        "triples_per_grid": len(chosen["replay_ordinals"]),
        "scope": "registered conjugacy-closed subset; not all diagnosis triples",
    }


def run_study(output_path, replay_path, progress=None):
    current, inputs, chosen = metadata(), input_audit(), selection()
    controls = precision.known_controls()
    if not inputs["passed"] or not controls["passed"]:
        raise ValueError("input or manufactured control failed; diagnosis was not started")
    grids = []
    for size in cubic.SIZES:
        grid, contexts = selected_campaign(size, chosen["ordinals"], chosen, progress)
        rows = grid.pop("records")
        archive = output_path.with_name(output_path.stem + f"_n{size}.jsonl.gz")
        grid["record_archive"] = previous.write_records(archive, rows)
        saved = previous.read_records(archive)
        grid["summary_recomputed"] = row_summary(saved) == grid["summary"]
        grid["replay_records"] = [r for r in rows if r["ordinal"] in chosen["replay_ordinals"]]
        grid["original_records_equal"] = all(r["original_record_equal"] for r in rows)
        grid["identical_operators"] = all(r["identical_operators"] for r in rows)
        grid["precision_crosschecks_passed"] = all(
            r["inputs"][v]["solvers"]["refined"]["precision_crosscheck"]["passed"]
            for r in grid["replay_records"]
            for v in precision.INPUTS
        )
        grid["original_failure_refined_failed"] = [
            r["ordinal"]
            for r in rows
            if r["ordinal"] in chosen["original_failure_ordinals"]
            and not r["inputs"]["raw"]["solvers"]["refined"]["passed"]
        ]
        grid["full_forcing"] = {
            v: precision.full_forcing_audit(contexts[v], progress) for v in precision.INPUTS
        }
        old = next(g for g in prior_artifact()["cycle"]["grids"] if g["size"] == size)
        grid["original_full_forcing_equal"] = all(
            grid["full_forcing"]["raw"]["arrays"][k] == old["coefficient_arrays"][k]
            for k in ("input_triples", "output_waves", "forcing")
        )
        grid["finite"] = _all_numeric_values_finite((rows, grid))
        grids.append(grid)
        if progress is not None:
            progress(
                {
                    "phase": "diagnosis_grid_complete",
                    "size": size,
                    "summary": grid["summary"],
                    "quadratic_paired_failed": grid["input_rebuild"]["paired_quadratic_equations"][
                        "failed_count"
                    ],
                    "refined_conjugacy": {
                        v: grid["conjugacy"][v]["refined"]["passed"] for v in precision.INPUTS
                    },
                }
            )
    replay = replay_audit(replay_path, inputs, chosen, grids, current)
    validity = {
        "sealed_inputs": inputs["passed"],
        "known_precision_controls": controls["passed"],
        "all_registered_grids_and_selected_triples": [g["size"] for g in grids] == list(cubic.SIZES)
        and all(g["coverage"] for g in grids),
        "input_rebuilds_and_projection": all(
            g["input_rebuild"]["raw_sealed_equal"]
            and g["input_rebuild"]["paired_input"]["passed"]
            and g["input_rebuild"]["paired_quadratic_equations"]["forcing_unchanged"]
            for g in grids
        ),
        "original_records_and_operators": all(
            g["original_records_equal"] and g["identical_operators"] for g in grids
        ),
        "full_independent_forcing": all(
            g["original_full_forcing_equal"]
            and all(v["directional"]["passed"] for v in g["full_forcing"].values())
            for g in grids
        ),
        "record_roundtrip_and_summary": all(
            g["record_archive"]["roundtrip_passed"] and g["summary_recomputed"] for g in grids
        ),
        "finite": all(g["finite"] for g in grids) and _all_numeric_values_finite(controls),
        "mp128_mp192_crosschecks": all(g["precision_crosschecks_passed"] for g in grids),
        "independent_replay": replay["passed"],
    }
    hypotheses = {
        "H1_precision_repairs_original_272_residual_failures": not grids[2][
            "original_failure_refined_failed"
        ],
        "H2_input_real_structure_is_separate": all(
            not g["conjugacy"]["raw"]["refined"]["fields"]["response"]["passed"] for g in grids[1:]
        )
        and all(g["conjugacy"]["paired"]["refined"]["passed"] for g in grids),
        "H3_paired_refined_candidate_passes_diagnosis": all(
            g["input_rebuild"]["paired_quadratic_equations"]["passed"]
            and g["summary"]["paired"]["refined"]["passed"]
            and g["conjugacy"]["paired"]["refined"]["passed"]
            for g in grids
        ),
    }
    outcome = previous.classifier.classify(validity, hypotheses, True)
    cycle = {
        "protocol": "Q012f1 fixed-map input/precision diagnosis; not full cubic prequalification",
        "input_audit": inputs,
        "selection": chosen,
        "controls": controls,
        "grids": grids,
        "independent_replay": replay,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "next_question": "Q012f2 full three-grid paired/refined cubic preflight"
        if outcome == "accepted"
        else "Diagnose remaining mechanisms without changing Q012f or Q012f1 gates",
        "claim_boundary": "selected-triple numerical diagnosis only; no full cubic acceptance, invariant manifold existence, amplitude improvement or TT advantage",
    }
    cycle["result_digest_sha256"] = q012a._digest(cycle)
    return {
        **current,
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--worker-output", type=Path)
    group.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    path = args.worker_output if args.worker_output is not None else args.output
    if path.exists() or any(
        path.with_name(path.stem + f"_n{n}.jsonl.gz").exists() for n in cubic.SIZES
    ):
        parser.error("use fresh paths; sealed evidence is not overwritten")
    if (args.output is not None) != (args.replay is not None):
        parser.error("--output requires --replay; --worker-output does not use --replay")
    progress = lambda row: print(json.dumps(row), flush=True)
    result = (
        worker(progress)
        if args.worker_output is not None
        else run_study(path, args.replay, progress)
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as target:
        target.write(json.dumps(result, allow_nan=False, separators=(",", ":")) + "\n")
    if args.output is not None:
        print(
            json.dumps(
                {
                    "study_gate": result["study_gate"],
                    "scientific_outcome": result["scientific_outcome"],
                    "validity": result["cycle"]["validity_gates"],
                    "hypotheses": result["cycle"]["hypothesis_gates"],
                }
            ),
            flush=True,
        )
        if result["study_gate"] != "passed":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
