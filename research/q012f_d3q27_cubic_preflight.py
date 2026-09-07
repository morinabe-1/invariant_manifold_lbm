"""Q012f exhaustive cubic preflight with compressed, complete record evidence."""

from __future__ import annotations

import argparse
import gzip
import json
import os
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import numpy as np
from scipy.linalg import solve_sylvester

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_damping as damping
from research import d3q27_svd_fallback as fallback
from research import q012a_d3q27_foundation as q012a
from research import q012d_d3q27_quadratic_chart as classifier
from research import q012e_d3q27_amplitude as previous
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PRIOR_PATH = q012a.ARTIFACT_DIRECTORY / "q012e_d3q27_amplitude.json"
PRIOR_SHA256 = "880f6cb5d9f6e029c7e470a6f4dbd3feed5739342827bb0002f4c06d5ed580e5"
PRIOR_RESULT = "c1e725cbf2372586c3dfa394db30d1f510b4e6c3e1e1d4e5d84f4fac4d5d4031"
HELPERS = previous.HELPERS + (("amplitude_runner", previous), ("cubic", cubic))


def prior_artifact() -> dict:
    return json.loads(PRIOR_PATH.read_text(encoding="utf-8"))


def input_audit() -> dict:
    old = prior_artifact()
    cycle = dict(old["cycle"])
    digest = cycle.pop("result_digest_sha256")
    evidence = previous.replay_evidence(
        cycle["input_audit"], cycle["coefficient_rebuild"], cycle["records"]
    )
    replay = previous.replay_audit(
        PRIOR_PATH.parent / cycle["independent_replay"]["filename"], evidence, old
    )
    checks = {
        "previous_input_chain": previous.input_audit()["passed"],
        "artifact_seal": _file_sha256(PRIOR_PATH) == PRIOR_SHA256,
        "result_digest": q012a._digest(cycle) == digest == PRIOR_RESULT,
        "package_source": old["source"] == source_metadata(),
        "runner_source": _file_sha256(Path(previous.__file__)) == old["runner_source"]["sha256"],
        "independent_previous_replay": replay == cycle["independent_replay"] and replay["passed"],
        "finite_sample_acceptance_retained": old["study_gate"]
        == cycle["study_validity"]
        == "passed"
        and old["scientific_outcome"] == cycle["scientific_outcome"] == "accepted"
        and all(cycle["validity_gates"].values())
        and all(cycle["hypothesis_gates"].values())
        and cycle["selection"]["calibration_prefix"] == [0.008, 0.032],
    }
    for name, module in previous.HELPERS:
        checks[name + "_source_seal"] = (
            _file_sha256(Path(module.__file__)) == old["helper_sources"][name]["sha256"]
        )
    return {"filename": PRIOR_PATH.name, "checks": checks, "passed": all(checks.values())}


def metadata() -> dict:
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


def fresh_model(size: int) -> tuple[chart.QuadraticChart, dict]:
    model = chart.build_chart(size=size)
    arrays = {name: chart.array_metadata(value) for name, value in model.archive_arrays().items()}
    old = prior_artifact()["cycle"]["coefficient_rebuild"]["arrays"]
    original_match = None if size != 17 else arrays == old
    audit = {key: value for key, value in model.construction.items() if key != "pair_records"}
    passed = (
        model.construction["frame_audit"]["passed"]
        and model.construction["coverage_passed"]
        and model.construction["coefficient_passed"]
        and original_match is not False
    )
    return model, {
        "size": size,
        "arrays": arrays,
        "sealed_17_arrays_equal": original_match,
        "quadratic_construction": audit,
        "passed": passed,
    }


def manufactured_controls() -> dict:
    rng = np.random.default_rng(2026090721)
    records = []
    base = np.array([[0.74 * np.exp(0.21j), 0.035j], [0, 0.68 * np.exp(-0.31j)]])
    output = np.array([[0.19, 0.07j], [0, 0.24]], dtype=complex)
    for groups in ((0, 1, 2), (0, 0, 1), (0, 1, 1), (0, 0, 0)):
        symmetric, _, _ = cubic.symmetric_product(groups, (2, 2, 2))
        matrices = [base * (1 - 0.05 * group) for group in groups]
        full = np.kron(matrices[2], np.kron(matrices[1], matrices[0]))
        inputs = symmetric.T @ full @ symmetric
        known = rng.standard_normal((2, len(inputs))) + 1j * rng.standard_normal((2, len(inputs)))
        forcing = known @ inputs - output @ known
        solution, solve, backend = fallback.solve_with_fallback(output, inputs, forcing)
        sylvester = solve_sylvester(output, -inputs, -forcing)
        errors = {
            "known_solution": damping.relative_error(solution, known),
            "independent_sylvester": damping.relative_error(solution, sylvester),
            "symmetric_invariance": float(np.linalg.norm(full @ symmetric - symmetric @ inputs)),
        }
        records.append(
            {
                "groups": list(groups),
                "product_dimension": len(inputs),
                "errors": errors,
                "solve": solve,
                "backend": backend,
                "passed": solve["passed"] and backend["passed"] and max(errors.values()) <= 1e-11,
            }
        )
    negative = []
    for name, delta, forcing in (
        ("singular_compatible", 0.0, [0, 1]),
        ("singular_incompatible", 0.0, [1, 0]),
        ("nonsingular_ill_conditioned", 1e-11, [1, 1]),
    ):
        _solution, solve, backend = fallback.solve_with_fallback(
            np.diag([0.7**3 + delta, 0.2]), np.array([[0.7**3]]), np.asarray(forcing)[:, None]
        )
        negative.append(
            {
                "expected": name,
                "solve": solve,
                "backend": backend,
                "passed": solve["status"] == name
                and not solve["passed"]
                and not backend["fallback"],
            }
        )
    return {
        "records": records,
        "negative_controls": negative,
        "passed": all(r["passed"] for r in records + negative),
    }


def read_records(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8") as source:
        return [json.loads(line) for line in source]


def record_digest(records: list[dict]) -> str:
    digest = sha256()
    for row in records:
        digest.update(
            (json.dumps(row, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n").encode(
                "utf-8"
            )
        )
    return digest.hexdigest()


def write_records(path: Path, records: list[dict]) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    with (
        path.open("xb") as target,
        gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as zipped,
    ):
        for row in records:
            zipped.write(
                (
                    json.dumps(row, sort_keys=True, allow_nan=False, separators=(",", ":")) + "\n"
                ).encode("utf-8")
            )
    restored = read_records(path)
    return {
        "filename": path.name,
        "bytes": path.stat().st_size,
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "record_count": len(records),
        "records_digest_sha256": record_digest(records),
        "roundtrip_passed": restored == records
        and record_digest(restored) == record_digest(records),
    }


def scan_grid(size: int, archive_path: Path, progress=None) -> dict:
    model, rebuild = fresh_model(size)
    context = cubic.build_context(model)
    records, offset = [], 0
    triples = np.zeros((cubic.COLUMN_COUNT, 3), dtype=np.int64)
    waves = np.zeros_like(triples)
    fields = {
        name: np.zeros((cubic.COLUMN_COUNT, dimension), dtype=complex)
        for name, dimension in (("forcing", 27), ("response", 27), ("reduced", 4))
    }
    for ordinal in range(cubic.TRIPLE_COUNT):
        try:
            jet = cubic.solve_triple(context, ordinal)
            records.append(jet.record)
            stop = offset + len(jet.factors)
            triples[offset:stop] = jet.input_triples
            waves[offset:stop] = jet.wave
            for name, value in fields.items():
                value[offset:stop] = (getattr(jet, name) * jet.factors).T
            offset = stop
        except (ArithmeticError, ValueError, RuntimeError, np.linalg.LinAlgError) as error:
            records.append(
                {
                    "ordinal": ordinal,
                    "execution_error": {"type": type(error).__name__, "message": str(error)},
                    "passed": False,
                }
            )
            break
        if progress is not None and (ordinal + 1) % 2048 == 0:
            progress(
                {
                    "phase": "cubic_triples",
                    "size": size,
                    "completed": ordinal + 1,
                    "total": cubic.TRIPLE_COUNT,
                    "last_passed": jet.record["passed"],
                }
            )
    summary = cubic.summarize_records(records)
    archive = write_records(archive_path, records)
    restored_summary = cubic.summarize_records(read_records(archive_path))
    conjugacy = (
        cubic.conjugacy_audit(model, triples, waves, fields) if summary["coverage_passed"] else None
    )
    direction = (
        cubic.directional_audit(model, triples, waves, fields["forcing"], progress)
        if summary["coverage_passed"]
        else None
    )
    array_info = {
        name: chart.array_metadata(value)
        for name, value in {
            "input_triples": triples[:offset],
            "output_waves": waves[:offset],
            **{name: value[:offset] for name, value in fields.items()},
        }.items()
    }
    result = {
        "size": size,
        "quadratic_rebuild": rebuild,
        "summary": summary,
        "record_archive": archive,
        "summary_recomputed_from_saved_rows": restored_summary == summary,
        "coefficient_arrays": array_info,
        "conjugacy": conjugacy,
        "directional_forcing": direction,
        "replay_records": [r for r in records if r["ordinal"] in cubic.REPLAY_ORDINALS],
        "finite": _all_numeric_values_finite(records)
        and all(bool(np.all(np.isfinite(value[:offset]))) for value in fields.values()),
    }
    if progress is not None:
        progress(
            {
                "phase": "grid_complete",
                "size": size,
                "completed": summary["completed_count"],
                "failed": summary["failed_count"],
                "all_solves_passed": summary["all_solves_passed"],
                "conjugacy_passed": conjugacy is not None and conjugacy["passed"],
                "independent_forcing_passed": direction is not None and direction["passed"],
            }
        )
    return result


def guarded_scan_grid(size: int, archive_path: Path, progress=None) -> dict:
    try:
        return scan_grid(size, archive_path, progress)
    except (
        ArithmeticError,
        ValueError,
        RuntimeError,
        np.linalg.LinAlgError,
        MemoryError,
        OSError,
    ) as error:
        # Retain any completed archive if a later validation cannot execute.
        rows = read_records(archive_path) if archive_path.exists() else []
        return {
            "size": size,
            "execution_error": {"type": type(error).__name__, "message": str(error)},
            "quadratic_rebuild": {"size": size, "passed": False},
            "summary": cubic.summarize_records(rows),
            "record_archive": None
            if not archive_path.exists()
            else {
                "filename": archive_path.name,
                "sha256": sha256(archive_path.read_bytes()).hexdigest(),
                "record_count": len(rows),
                "records_digest_sha256": record_digest(rows),
                "roundtrip_passed": False,
            },
            "summary_recomputed_from_saved_rows": False,
            "coefficient_arrays": {},
            "conjugacy": None,
            "directional_forcing": None,
            "replay_records": [r for r in rows if r["ordinal"] in cubic.REPLAY_ORDINALS],
            "finite": False,
        }


def worker(progress=None) -> dict:
    current, inputs, grids = metadata(), input_audit(), []
    if inputs["passed"]:
        for size in cubic.SIZES:
            model, rebuild = fresh_model(size)
            context = cubic.build_context(model)
            rows = [
                cubic.solve_triple(context, ordinal).record for ordinal in cubic.REPLAY_ORDINALS
            ]
            grids.append({"size": size, "quadratic_rebuild": rebuild, "records": rows})
            if progress is not None:
                progress({"phase": "independent_triple_replay", "size": size, "count": len(rows)})
    evidence = {"input_audit": inputs, "grids": grids}
    return {
        **current,
        "kind": "independent_48_triple_worker",
        "evidence": evidence,
        "evidence_digest_sha256": q012a._digest(evidence),
    }


def replay_audit(path: Path, inputs: dict, grids: list[dict], current: dict) -> dict:
    old = json.loads(path.read_text(encoding="utf-8"))
    expected = {
        "input_audit": inputs,
        "grids": [
            {
                "size": g["size"],
                "quadratic_rebuild": g["quadratic_rebuild"],
                "records": g["replay_records"],
            }
            for g in grids
        ],
    }
    checks = {
        "kind": old["kind"] == "independent_48_triple_worker",
        "separate_process": old["process_id"] != current["process_id"],
        "source_identity": all(
            old[key] == current[key] for key in ("source", "runner_source", "helper_sources")
        ),
        "evidence_digest": q012a._digest(old["evidence"]) == old["evidence_digest_sha256"],
        "registered_grids": [g["size"] for g in old["evidence"]["grids"]] == list(cubic.SIZES),
        "registered_ordinals": all(
            [r["ordinal"] for r in g["records"]] == list(cubic.REPLAY_ORDINALS)
            for g in old["evidence"]["grids"]
        ),
        "all_replay_values_equal": old["evidence"] == expected,
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "worker_process_id": old["process_id"],
        "evidence_digest_sha256": old["evidence_digest_sha256"],
        "checks": checks,
        "passed": all(checks.values()),
        "scope": "fresh quadratic charts and fixed 16 cubic triples on each of three grids; not full-triple replay",
    }


def run_study(output_path: Path, replay_path: Path, progress=None) -> dict:
    current, inputs, grids = metadata(), input_audit(), []
    controls = manufactured_controls()
    if inputs["passed"]:
        for size in cubic.SIZES:
            archive_path = output_path.with_name(output_path.stem + f"_n{size}.jsonl.gz")
            grids.append(guarded_scan_grid(size, archive_path, progress))
    replay = replay_audit(replay_path, inputs, grids, current)
    coverage = (
        len(grids) == 3
        and [g["size"] for g in grids] == list(cubic.SIZES)
        and all(
            g["summary"]["coverage_passed"]
            and g["conjugacy"] is not None
            and g["conjugacy"]["coverage"]
            for g in grids
        )
    )
    validity = {
        "sealed_input_chain": inputs["passed"],
        "known_cubic_controls": controls["passed"],
        "quadratic_input_rebuilds": len(grids) == 3
        and all(g["quadratic_rebuild"]["passed"] for g in grids),
        "full_246480_triples_and_578760_columns": coverage,
        "finite_evidence": _all_numeric_values_finite((grids, controls))
        and all(g["finite"] for g in grids),
        "saved_record_roundtrip_and_summary": len(grids) == 3
        and all(
            g["record_archive"] is not None
            and g["record_archive"]["roundtrip_passed"]
            and g["summary_recomputed_from_saved_rows"]
            for g in grids
        ),
        "independent_physical_forcing": coverage
        and all(g["directional_forcing"]["passed"] for g in grids),
        "independent_48_triple_replay": replay["passed"],
    }
    hypotheses = {
        "all_three_grid_cubic_solves": coverage
        and all(g["summary"]["all_solves_passed"] for g in grids),
        "full_cubic_real_structure": coverage and all(g["conjugacy"]["passed"] for g in grids),
    }
    outcome = classifier.classify(validity, hypotheses, True)
    cycle = {
        "protocol": "Q012f full cubic preflight; no removed coordinates or changed map",
        "configuration": {
            "sizes": list(cubic.SIZES),
            "omega": chart.OMEGA,
            "eta": chart.ETA,
            "power": chart.POWER,
            "real_coordinates": 104,
            "block_triples_per_grid": cubic.TRIPLE_COUNT,
            "symmetric_columns_per_grid": cubic.COLUMN_COUNT,
            "replay_ordinals": list(cubic.REPLAY_ORDINALS),
        },
        "input_audit": inputs,
        "manufactured_controls": controls,
        "grids": grids,
        "independent_replay": replay,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite-degree numerical prequalification only; no validated cubic evaluator, finite-amplitude improvement, SSM existence, continuous-ball or grid-uniform radius, or TT advantage",
        "next_question": "Q012g cubic evaluation and degree-four residual tests"
        if outcome == "accepted"
        else "Diagnose failed cubic preflight without changing the sealed three-grid protocol",
    }
    cycle["result_digest_sha256"] = q012a._digest(cycle)
    return {
        **current,
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    targets = parser.add_mutually_exclusive_group(required=True)
    targets.add_argument("--worker-output", type=Path)
    targets.add_argument("--output", type=Path)
    parser.add_argument("--replay", type=Path)
    args = parser.parse_args()
    path = args.worker_output if args.worker_output is not None else args.output
    if path.exists() or any(
        path.with_name(path.stem + f"_n{size}.jsonl.gz").exists() for size in cubic.SIZES
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
