"""Run Q012f2 across all three grids, streaming complete exact-residual evidence."""

from __future__ import annotations

import argparse
import gzip
import json
import os
import zlib
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter, process_time

import numpy as np

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_cubic_precision as precision
from research import d3q27_exact_residual as exact
from research import d3q27_refined_cubic as refined
from research import q012a_d3q27_foundation as q012a
from research import q012f1a_d3q27_exact_residual as previous
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRECISION_RUNNER = previous.previous
ORIGINAL_RUNNER = PRECISION_RUNNER.previous
PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012f1a_d3q27_exact_residual.json"
PRIOR_SHA = "869831275160a5457e554fff6ed8750410ee734cff99d6c9349f90f38ccd42a4"
PRIOR_DIGEST = "5888cfa9b32aae39f05f9cb4db401cb02eff81b6c09f05753c1846014748fc31"
HELPERS = previous.HELPERS + (("exact_runner", previous), ("refined_cubic", refined))
ERRORS = (ArithmeticError, ValueError, RuntimeError, np.linalg.LinAlgError, MemoryError, OSError)


def read_json(path):
    return previous.read_json(path)


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


def sibling(directory, filename):
    if Path(filename).name != filename:
        raise ValueError("evidence archives must be sibling files")
    return directory / filename


def input_audit():
    old = read_json(PRIOR_PATH)
    cycle = dict(old["cycle"])
    digest = cycle.pop("result_digest_sha256")
    prepared_path = sibling(PRIOR_PATH.parent, cycle["prepared_audit"]["filename"])
    prepared = read_json(prepared_path)
    pa = previous.prepared_audit(prepared_path, prepared)
    replay = previous.replay_audit(
        sibling(PRIOR_PATH.parent, cycle["independent_replay"]["filename"]),
        prepared_path,
        prepared,
        old,
    )
    checks = {
        "previous_input_chain": previous.input_audit()["passed"],
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA,
        "cycle_digest": q012a._digest(cycle) == digest == PRIOR_DIGEST,
        "exact_diagnosis_accepted": old["study_gate"] == "passed"
        and old["scientific_outcome"] == "accepted"
        and all(cycle["validity_gates"].values())
        and all(cycle["hypothesis_gates"].values()),
        "package_source": old["source"] == source_metadata(),
        "runner_source": old["runner_source"]["sha256"] == _file_sha256(Path(previous.__file__)),
        "prepared_exact_evidence": pa == cycle["prepared_audit"] and pa["passed"],
        "independent_exact_evidence": replay == cycle["independent_replay"] and replay["passed"],
    }
    for name, module in previous.HELPERS:
        checks[name + "_source"] = old["helper_sources"][name]["sha256"] == _file_sha256(
            Path(module.__file__)
        )
    return {"checks": checks, "passed": all(checks.values())}


def controls():
    results = {
        "cubic_and_resonant": ORIGINAL_RUNNER.manufactured_controls(),
        "fixed_refinement": precision.known_controls(),
        "exact_arithmetic": exact.known_controls(),
    }
    return {"results": results, "passed": all(r["passed"] for r in results.values())}


def old_grid(size):
    old = read_json(previous.PRIOR_PATH)
    return next(g for g in old["cycle"]["grids"] if g["size"] == size)


def fresh_input(size):
    models, rebuild = PRECISION_RUNNER.build_inputs(size)
    grid = old_grid(size)
    rows = ORIGINAL_RUNNER.read_records(
        sibling(previous.PRIOR_PATH.parent, grid["record_archive"]["filename"])
    )
    checks = {
        "sealed_rebuild_equal": rebuild == grid["input_rebuild"],
        "raw_sealed_equal": rebuild["raw_sealed_equal"],
        "paired_input": rebuild["paired_input"]["passed"],
        "paired_quadratic_equations": rebuild["paired_quadratic_equations"]["passed"]
        and rebuild["paired_quadratic_equations"]["forcing_unchanged"],
    }
    old_exact = {}
    if size == 65:
        result = read_json(PRIOR_PATH)
        prepared = read_json(
            sibling(PRIOR_PATH.parent, result["cycle"]["prepared_audit"]["filename"])
        )
        old_exact = {
            r["ordinal"]: r["proof"] for r in prepared["core"]["records"] if r["input"] == "paired"
        }
    return (
        models["paired"],
        {
            "rebuild": rebuild,
            "checks": checks,
            "passed": all(checks.values()),
        },
        {r["ordinal"]: r["inputs"]["paired"] for r in rows},
        old_exact,
    )


def previous_match(row, old, old_exact):
    # Old 128/192 comparisons are retained upstream; this study checks exact arithmetic instead.
    checks = {
        "paired_svd_reference": row["paired_svd_reference"] == old["original_record"],
        "problem_arrays": row["problem_arrays"] == old["problem_arrays"],
        "fixed_refinement_history": row["refinement_history"] == old["refinement_history"],
        "refined_fields": row["refined"]
        == {k: v for k, v in old["solvers"]["refined"].items() if k != "precision_crosscheck"},
    }
    if old_exact is not None:
        checks["q012f1a_exact_proof"] = row["exact_residual"] == old_exact
    return {"checks": checks, "passed": all(checks.values())}


def case(context, ordinal, old_rows, old_exact, kernel):
    row, fibers = refined.solve_case(context, ordinal, kernel)
    row["previous_match"] = (
        previous_match(row, old_rows[ordinal], old_exact.get(ordinal))
        if ordinal in old_rows
        else None
    )
    return row, fibers


def paths_for_grid(output, size):
    stem = output.stem + f"_n{size}"
    return {
        "result": output.with_name(stem + ".json"),
        "records": output.with_name(stem + ".jsonl.gz"),
        "fibers": output.with_name(stem + ".npz"),
    }


def scan_grid(size, paths, progress=None):
    started, cpu_started = perf_counter(), process_time()
    model, rebuild, old_rows, old_exact = fresh_input(size)
    if not rebuild["passed"]:
        raise ValueError("paired quadratic input rebuild failed before cubic scan")
    context = cubic.build_context(model)
    triples = np.zeros((cubic.COLUMN_COUNT, 3), dtype=np.int64)
    waves = np.zeros_like(triples)
    fields = {
        k: np.zeros((cubic.COLUMN_COUNT, dimension), dtype=complex)
        for k, dimension in (("forcing", 27), ("response", 27), ("reduced", 4))
    }
    summary, witness, offset = refined.Summary(), [], 0
    with refined.RecordWriter(paths["records"]) as writer:
        for ordinal in range(cubic.TRIPLE_COUNT):
            try:
                row, fibers = case(context, ordinal, old_rows, old_exact, exact.audit_integer)
                if not _all_numeric_values_finite(row) or not all(
                    np.all(np.isfinite(fibers[k])) for k in fields
                ):
                    raise ValueError("nonfinite cubic evidence")
                stop = offset + len(fibers["triples"])
                triples[offset:stop], waves[offset:stop] = fibers["triples"], fibers["wave"]
                for key, value in fields.items():
                    value[offset:stop] = fibers[key]
                offset = stop
            except ERRORS as error:
                row = {
                    "ordinal": ordinal,
                    "execution_error": {"type": type(error).__name__, "message": str(error)},
                    "passed": False,
                }
                writer.append(row)
                summary.add(row)
                break
            writer.append(row)
            summary.add(row)
            if ordinal in old_rows:
                witness.append(row)
            if progress is not None and (ordinal + 1) % 1024 == 0:
                progress(
                    {
                        "phase": "all_refined_triples",
                        "size": size,
                        "completed": ordinal + 1,
                        "total": cubic.TRIPLE_COUNT,
                        "candidate_failures": len(summary.failed_ordinals),
                        "legacy_failures": len(summary.legacy_failed_ordinals),
                        "elapsed_seconds": perf_counter() - started,
                    }
                )
    computed = summary.result()
    archive = writer.metadata()
    restored = refined.summarize(refined.iter_records(paths["records"]))
    values = {
        "input_triples": triples[:offset],
        "output_waves": waves[:offset],
        **{k: v[:offset] for k, v in fields.items()},
    }
    fiber_archive = refined.save_fibers(paths["fibers"], values)
    conjugacy = direction = None
    forcing_equal = False
    if computed["coverage_passed"]:
        conjugacy = cubic.conjugacy_audit(model, triples, waves, fields)
        direction = cubic.directional_audit(model, triples, waves, fields["forcing"], progress)
        forcing = {
            "arrays": {
                k: chart.array_metadata(values[k])
                for k in ("input_triples", "output_waves", "forcing")
            },
            "directional": direction,
        }
        forcing_equal = forcing == old_grid(size)["full_forcing"]["paired"]
    result = {
        "size": size,
        "input_rebuild": rebuild,
        "summary": computed,
        "record_archive": archive,
        "saved_summary_equal": computed == restored,
        "fiber_archive": fiber_archive,
        "conjugacy": conjugacy,
        "directional_forcing": direction,
        "sealed_paired_full_forcing_equal": forcing_equal,
        "replay_records": witness,
        "finite": computed["finite"] and all(bool(np.all(np.isfinite(v))) for v in values.values()),
        "cost": {
            "wall_seconds": perf_counter() - started,
            "cpu_seconds": process_time() - cpu_started,
            "record_archive_bytes": archive["bytes"],
            "fiber_archive_bytes": fiber_archive["bytes"],
        },
    }
    if progress is not None:
        progress(
            {
                "phase": "grid_complete",
                "size": size,
                "completed": computed["completed_count"],
                "candidate_failures": computed["candidate_failed_count"],
                "legacy_failures": computed["legacy_failed_count"],
                "conjugacy_passed": conjugacy is not None and conjugacy["passed"],
            }
        )
    return result


def guarded_scan_grid(size, paths, progress=None):
    try:
        return scan_grid(size, paths, progress)
    except ERRORS as error:
        archive, summary, witness = None, refined.Summary(), []
        recovery_error = None
        if paths["records"].exists():
            digest = refined.sha256()
            try:
                for row in refined.iter_records(paths["records"]):
                    digest.update(refined.record_line(row))
                    summary.add(row)
                    if row.get("previous_match") is not None:
                        witness.append(row)
                archive = {
                    "filename": paths["records"].name,
                    "bytes": paths["records"].stat().st_size,
                    "sha256": refined.file_hash(paths["records"]),
                    "record_count": summary.records,
                    "records_digest_sha256": digest.hexdigest(),
                    "roundtrip_passed": False,
                }
            except ERRORS + (EOFError, gzip.BadGzipFile, zlib.error) as recovery:
                recovery_error = {"type": type(recovery).__name__, "message": str(recovery)}
        return {
            "size": size,
            "execution_error": {"type": type(error).__name__, "message": str(error)},
            "recovery_error": recovery_error,
            "input_rebuild": {"passed": False},
            "summary": summary.result(),
            "record_archive": archive,
            "saved_summary_equal": False,
            "fiber_archive": None,
            "conjugacy": None,
            "directional_forcing": None,
            "sealed_paired_full_forcing_equal": False,
            "replay_records": witness,
            "finite": False,
        }


def worker(progress=None):
    current, inputs, control = metadata(), input_audit(), controls()
    if not inputs["passed"] or not control["passed"]:
        raise ValueError("sealed inputs or controls failed before independent worker")
    ordinals = PRECISION_RUNNER.selection()["ordinals"]
    grids = []
    for size in cubic.SIZES:
        model, rebuild, old_rows, old_exact = fresh_input(size)
        context = cubic.build_context(model)
        rows = []
        for index, ordinal in enumerate(ordinals):
            row, _ = case(context, ordinal, old_rows, old_exact, exact.audit_gmp)
            rows.append(row)
            if progress is not None and (index + 1) % 64 == 0:
                progress(
                    {
                        "phase": "independent_fresh_gmp",
                        "size": size,
                        "completed": index + 1,
                        "total": len(ordinals),
                    }
                )
        grids.append({"size": size, "input_rebuild": rebuild, "records": rows})
    evidence = {"input_audit": inputs, "controls": control, "ordinals": ordinals, "grids": grids}
    return {
        **current,
        "kind": "Q012f2 independent fresh 972-case GMP worker",
        "evidence": evidence,
        "evidence_digest_sha256": q012a._digest(evidence),
    }


def replay_audit(path, inputs, control, grids, current):
    worker_result = read_json(path)
    expected = {
        "input_audit": inputs,
        "controls": control,
        "ordinals": PRECISION_RUNNER.selection()["ordinals"],
        "grids": [
            {"size": g["size"], "input_rebuild": g["input_rebuild"], "records": g["replay_records"]}
            for g in grids
        ],
    }
    checks = {
        "kind": worker_result["kind"] == "Q012f2 independent fresh 972-case GMP worker",
        "separate_process": worker_result["process_id"] != current["process_id"],
        "source_identity": all(
            worker_result[k] == current[k] for k in ("source", "runner_source", "helper_sources")
        ),
        "evidence_digest": q012a._digest(worker_result["evidence"])
        == worker_result["evidence_digest_sha256"],
        "full_registered_972_witnesses": len(grids) == 3
        and len(expected["ordinals"]) == 324
        and [g["size"] for g in grids] == list(cubic.SIZES)
        and all([r["ordinal"] for r in g["replay_records"]] == expected["ordinals"] for g in grids),
        "all_fresh_values_and_exact_proofs_equal": worker_result["evidence"] == expected,
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "checks": checks,
        "passed": all(checks.values()),
        "worker_process_id": worker_result["process_id"],
        "evidence_digest_sha256": worker_result["evidence_digest_sha256"],
        "scope": "fresh quadratic inputs and 324 selected triples per grid, 972 total; GMP versus integer residuals; not exhaustive separate-process replay",
    }


def decision(inputs, control, grids, replay):
    complete = len(grids) == 3 and [g["size"] for g in grids] == list(cubic.SIZES)
    coverage = complete and all(
        g["summary"]["coverage_passed"]
        and g["conjugacy"] is not None
        and g["conjugacy"]["coverage"]
        for g in grids
    )
    validity = {
        "sealed_inputs": inputs["passed"],
        "registered_controls": control["passed"],
        "paired_quadratic_rebuilds": complete and all(g["input_rebuild"]["passed"] for g in grids),
        "full_246480_triples_and_578760_columns": coverage,
        "finite_evidence": complete
        and all(g["finite"] for g in grids)
        and _all_numeric_values_finite(grids),
        "complete_lossless_records": complete
        and all(
            g["record_archive"] is not None
            and g["record_archive"]["roundtrip_passed"]
            and g["saved_summary_equal"]
            for g in grids
        ),
        "complete_nonpickled_sparse_fibers": coverage
        and all(
            g["fiber_archive"] is not None and g["fiber_archive"]["roundtrip_passed"] for g in grids
        ),
        "independent_full_physical_forcing": coverage
        and all(
            g["directional_forcing"] is not None
            and g["directional_forcing"]["passed"]
            and g["sealed_paired_full_forcing_equal"]
            for g in grids
        ),
        "previous_972_selected_arms_unchanged": complete
        and all(
            g["summary"]["previous_selected_count"] == 324
            and g["summary"]["previous_selected_failures"] == 0
            for g in grids
        ),
        "mp128_matches_exact": coverage
        and all(g["summary"]["mp128_agreement_failures"] == 0 for g in grids),
        "independent_fresh_972_gmp_replay": replay["passed"],
    }
    hypotheses = {
        "H1_all_three_grid_refined_candidates_pass": coverage
        and all(g["summary"]["all_candidates_passed"] for g in grids),
        "H2_all_three_grid_full_cubic_real_structure": coverage
        and all(g["conjugacy"] is not None and g["conjugacy"]["passed"] for g in grids),
    }
    return validity, hypotheses, ORIGINAL_RUNNER.classifier.classify(validity, hypotheses, True)


def run_study(output, replay_path, progress=None):
    current, inputs, control = metadata(), input_audit(), controls()
    grids, grid_artifacts = [], []
    if inputs["passed"] and control["passed"]:
        for size in cubic.SIZES:
            paths = paths_for_grid(output, size)
            grid = guarded_scan_grid(size, paths, progress)
            grid["result_digest_sha256"] = q012a._digest(grid)
            value = {**metadata(), "kind": "Q012f2 complete grid evidence", "grid": grid}
            previous.write_json(paths["result"], value)
            grid_artifacts.append(
                {"filename": paths["result"].name, "sha256": _file_sha256(paths["result"])}
            )
            grids.append(grid)
    replay = replay_audit(replay_path, inputs, control, grids, current)
    validity, hypotheses, outcome = decision(inputs, control, grids, replay)
    cycle = {
        "protocol": "Q012f2 exhaustive paired/refined cubic preflight with exact residuals",
        "configuration": {
            "sizes": list(cubic.SIZES),
            "omega": chart.OMEGA,
            "eta": chart.ETA,
            "power": chart.POWER,
            "real_coordinates": 104,
            "triples_per_grid": cubic.TRIPLE_COUNT,
            "columns_per_grid": cubic.COLUMN_COUNT,
            "independent_replay_ordinals": PRECISION_RUNNER.selection()["ordinals"],
        },
        "input_audit": inputs,
        "controls": control,
        "grids": grids,
        "grid_artifacts": grid_artifacts,
        "independent_replay": replay,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite-degree full three-grid numerical coefficient preflight; exact residuals only for rounded external matrices; not a cubic evaluator, amplitude improvement, SSM existence, continuous-ball or grid-uniform radius, or TT advantage",
        "next_question": "Q012g real cubic W/R evaluation and degree-four residual tests"
        if outcome == "accepted"
        else "Classify all failed cubic families and diagnose the remaining mechanism",
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
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--worker-output", type=Path)
    targets.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    output = args.worker_output or args.output
    paths = [output]
    if args.output is not None:
        paths.extend(p for size in cubic.SIZES for p in paths_for_grid(output, size).values())
    if any(p.exists() for p in paths):
        parser.error("use fresh output paths; complete or partial evidence is not overwritten")
    if (args.output is not None) != (args.replay is not None):
        parser.error("--output requires --replay; --worker-output does not use --replay")
    progress = lambda row: print(json.dumps(row), flush=True)
    result = (
        worker(progress)
        if args.worker_output is not None
        else run_study(output, args.replay, progress)
    )
    previous.write_json(output, result)
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
