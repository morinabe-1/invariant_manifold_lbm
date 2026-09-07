"""Prepare fixed matrices, independently verify exact residuals, and seal Q012f1a."""

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
from research import d3q27_exact_residual as exact
from research import q012a_d3q27_foundation as q012a
from research import q012f1_d3q27_cubic_precision as previous
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012f1_d3q27_cubic_precision.json"
PRIOR_SHA = "5bc0db745c8846196feec53bcbacddc069b8b257e5bcb89503b7b41e44c403a7"
PRIOR_DIGEST = "2137462ad6c2a67c6310dfc428b9c92ae06db85129b23c2c21adae715206c5f1"
HELPERS = previous.HELPERS + (("precision_runner", previous), ("exact_residual", exact))


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def input_audit():
    old = read_json(PRIOR_PATH)
    cycle = dict(old["cycle"])
    digest = cycle.pop("result_digest_sha256")
    checks = {
        "previous_input_chain": previous.input_audit()["passed"],
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA,
        "cycle_digest": q012a._digest(cycle) == digest == PRIOR_DIGEST,
        "valid_rejection": old["study_gate"] == "passed"
        and old["scientific_outcome"] == "rejected"
        and all(cycle["validity_gates"].values()),
        "package_source": old["source"] == source_metadata(),
        "runner_source": old["runner_source"]["sha256"] == _file_sha256(Path(previous.__file__)),
        "selection": previous.selection() == cycle["selection"],
    }
    for name, module in previous.HELPERS:
        checks[name + "_source"] = (
            _file_sha256(Path(module.__file__)) == old["helper_sources"][name]["sha256"]
        )
    for grid in cycle["grids"]:
        meta = grid["record_archive"]
        path = PRIOR_PATH.parent / meta["filename"]
        checks[f"archive_{grid['size']}"] = sha256(path.read_bytes()).hexdigest() == meta["sha256"]
    replay = previous.replay_audit(
        PRIOR_PATH.parent / cycle["independent_replay"]["filename"],
        cycle["input_audit"],
        cycle["selection"],
        cycle["grids"],
        old,
    )
    checks["independent_previous_replay"] = (
        replay == cycle["independent_replay"] and replay["passed"]
    )
    return {"checks": checks, "passed": all(checks.values())}


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


def rebuild_case(context, ordinal, prior):
    jet = cubic.solve_triple(context, ordinal)
    a, d, f, sector = precision.problem(context, ordinal, jet)
    solutions, history = precision.structured_solutions(a, d, f)
    x = solutions["refined"]
    r64 = a @ x - x @ d + f
    r128 = precision.residual_mpc(a, d, f, x)
    denominator = max(exact.FLOOR, float(np.linalg.norm(f)))
    arrays = dict(zip(exact.ARRAY_NAMES, (a, d, f, x, r64, r128), strict=True))
    refined = prior["solvers"]["refined"]
    checks = {
        "original_cubic_record": jet.record == prior["original_record"],
        "history": history == prior["refinement_history"],
        "refined_solution": chart.array_metadata(x) == refined["arrays"]["external_solution"],
        "population_response": chart.array_metadata(sector.basis @ x)
        == refined["arrays"]["population_response"],
        "legacy_residual": float(np.linalg.norm(r64) / denominator)
        == refined["external_relative_residual"],
        "mp128_residual": float(np.linalg.norm(r128) / denominator)
        == refined["mp128_relative_residual"],
        "prior_rank_and_structure": prior["original_record"]["status"] == "nonsingular_practical"
        and refined["full_relative_residual"] <= 1e-9
        and refined["structural_error"] <= 5e-12,
    }
    for key, value in (
        ("external_dynamics", a),
        ("input_dynamics", d),
        ("external_forcing", f),
        ("forcing", jet.forcing),
    ):
        checks[key] = chart.array_metadata(value) == prior["problem_arrays"][key]
    return arrays, denominator, {"checks": checks, "passed": all(checks.values())}


def save_arrays(path, arrays):
    if not arrays or not all(
        np.asarray(value).dtype in (np.dtype("float64"), np.dtype("complex128"))
        and np.all(np.isfinite(value))
        for value in arrays.values()
    ):
        raise ValueError("only nonempty finite binary64 array collections can be archived")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as target:
        np.savez_compressed(target, **arrays)
    entries = {key: chart.array_metadata(value) for key, value in arrays.items()}
    with np.load(path, allow_pickle=False) as saved:
        equal = set(saved.files) == set(entries) and all(
            chart.array_metadata(saved[k]) == v for k, v in entries.items()
        )
    return {
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "entries": entries,
        "roundtrip_passed": equal,
    }


def write_json(path, value):
    serialized = json.dumps(value, allow_nan=False, separators=(",", ":")) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as target:
        target.write(serialized)


def prepare(path, progress=None):
    inputs = input_audit()
    controls = exact.known_controls()
    if not inputs["passed"] or not controls["passed"]:
        raise ValueError("input or exact control failed; preparation was not started")
    old = read_json(PRIOR_PATH)
    grid = next(g for g in old["cycle"]["grids"] if g["size"] == 65)
    old_rows = previous.previous.read_records(
        PRIOR_PATH.parent / grid["record_archive"]["filename"]
    )
    models, rebuild = previous.build_inputs(65)
    contexts = {name: cubic.build_context(model) for name, model in models.items()}
    rows, arrays = [], {}
    for index, old_row in enumerate(old_rows):
        ordinal = old_row["ordinal"]
        for variant in precision.INPUTS:
            values, denominator, audit = rebuild_case(
                contexts[variant], ordinal, old_row["inputs"][variant]
            )
            prefix = f"o{ordinal:05d}_{variant}"
            keys = {name: prefix + "_" + name for name in exact.ARRAY_NAMES}
            arrays.update({keys[name]: value for name, value in values.items()})
            proof = exact.audit_gmp(*(values[name] for name in exact.ARRAY_NAMES), denominator)
            rows.append(
                {
                    "ordinal": ordinal,
                    "input": variant,
                    "array_keys": keys,
                    "stored_denominator": denominator,
                    "reconstruction": audit,
                    "prior_legacy_gate": old_row["inputs"][variant]["solvers"]["refined"][
                        "external_relative_residual"
                    ]
                    <= exact.TOLERANCE,
                    "proof": proof,
                }
            )
        if progress is not None and (index + 1) % 16 == 0:
            progress(
                {
                    "phase": "exact_gmp_residuals",
                    "completed_triples": index + 1,
                    "total_triples": len(old_rows),
                }
            )
    archive = save_arrays(path.with_suffix(".npz"), arrays)
    core = {
        "input_audit": inputs,
        "controls": controls,
        "size": 65,
        "real_coordinates": 104,
        "selection": old["cycle"]["selection"],
        "quadratic_rebuild_equal": rebuild == grid["input_rebuild"],
        "quadratic_rebuild_digest": q012a._digest(rebuild),
        "array_archive": archive,
        "records": rows,
        "records_digest_sha256": q012a._digest(rows),
    }
    core["result_digest_sha256"] = q012a._digest(core)
    return {**metadata(), "kind": "Q012f1a fixed-matrix GMP preparation", "core": core}


def prepared_audit(path, prepared=None):
    prepared = read_json(path) if prepared is None else prepared
    core = dict(prepared["core"])
    digest = core.pop("result_digest_sha256")
    current = metadata()
    meta = core["array_archive"]
    if Path(meta["filename"]).name != meta["filename"]:
        raise ValueError("the NPZ must be a sibling artifact")
    archive = path.parent / meta["filename"]
    with np.load(archive, allow_pickle=False) as saved:
        array_match = set(saved.files) == set(meta["entries"]) and all(
            chart.array_metadata(saved[k]) == v for k, v in meta["entries"].items()
        )
    checks = {
        "kind": prepared["kind"] == "Q012f1a fixed-matrix GMP preparation",
        "source_identity": all(
            prepared[k] == current[k] for k in ("source", "runner_source", "helper_sources")
        ),
        "core_digest": q012a._digest(core) == digest,
        "records_digest": q012a._digest(core["records"]) == core["records_digest_sha256"],
        "npz_seal": sha256(archive.read_bytes()).hexdigest() == meta["sha256"]
        and archive.stat().st_size == meta["bytes"],
        "npz_entries": array_match,
        "input_audit": core["input_audit"] == input_audit() and core["input_audit"]["passed"],
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "checks": checks,
        "passed": all(checks.values()),
    }


def integer_worker(path, progress=None):
    prepared = read_json(path)
    audit = prepared_audit(path, prepared)
    if not audit["passed"]:
        raise ValueError("prepared input failed; independent integer audit was not started")
    core = prepared["core"]
    rows = []
    with np.load(path.parent / core["array_archive"]["filename"], allow_pickle=False) as saved:
        for index, row in enumerate(core["records"]):
            arrays = [saved[row["array_keys"][name]] for name in exact.ARRAY_NAMES]
            proof = exact.audit_integer(*arrays, row["stored_denominator"])
            rows.append({"ordinal": row["ordinal"], "input": row["input"], "proof": proof})
            if progress is not None and (index + 1) % 64 == 0:
                progress(
                    {
                        "phase": "independent_integer_residuals",
                        "completed_cases": index + 1,
                        "total_cases": len(core["records"]),
                    }
                )
    evidence = {
        "prepared_sha256": _file_sha256(path),
        "npz_sha256": core["array_archive"]["sha256"],
        "records": rows,
    }
    return {
        **metadata(),
        "kind": "Q012f1a full independent integer audit",
        "prepared_audit": audit,
        "evidence": evidence,
        "evidence_digest_sha256": q012a._digest(evidence),
    }


def replay_audit(path, prepared_path, prepared, current):
    worker = read_json(path)
    core = prepared["core"]
    expected = {
        "prepared_sha256": _file_sha256(prepared_path),
        "npz_sha256": core["array_archive"]["sha256"],
        "records": [{k: row[k] for k in ("ordinal", "input", "proof")} for row in core["records"]],
    }
    checks = {
        "kind": worker["kind"] == "Q012f1a full independent integer audit",
        "separate_process": worker["process_id"] != prepared["process_id"],
        "source_identity": all(
            worker[k] == prepared[k] == current[k]
            for k in ("source", "runner_source", "helper_sources")
        ),
        "prepared_input": worker["prepared_audit"] == prepared_audit(prepared_path, prepared)
        and worker["prepared_audit"]["passed"],
        "evidence_digest": q012a._digest(worker["evidence"]) == worker["evidence_digest_sha256"],
        "all_648_proofs_equal": worker["evidence"] == expected and len(expected["records"]) == 648,
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "checks": checks,
        "passed": all(checks.values()),
        "worker_process_id": worker["process_id"],
        "evidence_digest_sha256": worker["evidence_digest_sha256"],
        "scope": "all 648 saved rounded matrix problems; independent exact arithmetic, not a separate LBM solve rebuild",
    }


def summarize(rows):
    summaries = {}
    for variant in precision.INPUTS:
        subset = [r for r in rows if r["input"] == variant]
        worst = max(
            subset,
            key=lambda r: (
                exact.rational(r["proof"]["norms_squared"]["exact_residual_norm_squared"])
                / exact.rational(r["proof"]["exact_denominator_squared"])
            ),
        )
        summaries[variant] = {
            "count": len(subset),
            "gate_failure_counts": {
                key: sum(not r["proof"]["gates"][key] for r in subset)
                for key in subset[0]["proof"]["gates"]
            },
            "evaluation_only_mismatch_ordinals": [
                r["ordinal"] for r in subset if r["proof"]["evaluation_only_mismatch"]
            ],
            "mp128_agreement_failure_count": sum(not r["proof"]["mp128_agrees"] for r in subset),
            "worst_exact_case": worst,
            "maximum_legacy_relative_residual": max(
                r["proof"]["legacy_relative_residual"] for r in subset
            ),
            "maximum_relative_evaluation64_error": max(
                r["proof"]["approximate_relative_norms"]["evaluation64_error"] for r in subset
            ),
            "maximum_relative_evaluation128_error": max(
                r["proof"]["approximate_relative_norms"]["evaluation128_error"] for r in subset
            ),
        }
    return summaries


def seal(prepared_path, replay_path):
    prepared = read_json(prepared_path)
    audit = prepared_audit(prepared_path, prepared)
    core = prepared["core"]
    current = metadata()
    replay = replay_audit(replay_path, prepared_path, prepared, current)
    rows = core["records"]
    expected_order = [(o, v) for o in core["selection"]["ordinals"] for v in precision.INPUTS]
    validity = {
        "sealed_preparation_and_inputs": audit["passed"],
        "known_controls": core["controls"]["passed"],
        "all_648_cases": len(rows) == 648
        and [(r["ordinal"], r["input"]) for r in rows] == expected_order,
        "all_matrices_and_solutions_rebuilt": core["quadratic_rebuild_equal"]
        and all(r["reconstruction"]["passed"] for r in rows),
        "legacy_decisions_reproduced": all(
            r["proof"]["gates"]["legacy"] == r["prior_legacy_gate"] for r in rows
        ),
        "npz_roundtrip": core["array_archive"]["roundtrip_passed"],
        "finite_evidence": _all_numeric_values_finite(core),
        "independent_integer_full_replay": replay["passed"],
        "mp128_matches_exact_to_registered_accuracy": all(r["proof"]["mp128_agrees"] for r in rows),
    }
    summary = summarize(rows)
    hypotheses = {
        "H1_all_648_exact_residuals_pass": all(
            all(r["proof"]["gates"][k] for k in exact.EXACT_GATES) for r in rows
        ),
        "H2_original_37_failures_are_residual_evaluation_mismatches": all(
            r["proof"]["evaluation_only_mismatch"] == (not r["prior_legacy_gate"]) for r in rows
        )
        and [len(summary[v]["evaluation_only_mismatch_ordinals"]) for v in precision.INPUTS]
        == [20, 17],
    }
    outcome = previous.previous.classifier.classify(validity, hypotheses, True)
    cycle = {
        "protocol": "Q012f1a exact residuals of fixed rounded external equations",
        "prepared_audit": audit,
        "independent_replay": replay,
        "summary": summary,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "prepared_result_digest": core["result_digest_sha256"],
        "claim_boundary": "exact residual certification only for 648 rounded external equations; original Q012f/Q012f1 rejections unchanged; no exact LBM symbol, full cubic prequalification, manifold existence, or amplitude improvement",
        "next_question": "Q012f2 full three-grid paired/refined cubic preflight with verified residual evaluation"
        if outcome == "accepted"
        else "Diagnose remaining exact residual failures without relaxing the sealed gates",
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
    group.add_argument("--prepare-output", type=Path)
    group.add_argument("--worker-output", type=Path)
    group.add_argument("--output", type=Path)
    parser.add_argument("--prepared", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    path = args.prepare_output or args.worker_output or args.output
    if path.exists() or (args.prepare_output is not None and path.with_suffix(".npz").exists()):
        parser.error("use fresh paths; sealed evidence is not overwritten")
    if args.prepare_output is not None and (args.prepared is not None or args.replay is not None):
        parser.error("preparation does not consume prepared or replay inputs")
    if args.worker_output is not None and (args.prepared is None or args.replay is not None):
        parser.error("worker requires --prepared only")
    if args.output is not None and (args.prepared is None or args.replay is None):
        parser.error("sealing requires --prepared and --replay")
    progress = lambda row: print(json.dumps(row), flush=True)
    if args.prepare_output is not None:
        result = prepare(path, progress)
    elif args.worker_output is not None:
        result = integer_worker(args.prepared, progress)
    else:
        result = seal(args.prepared, args.replay)
    write_json(path, result)
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
