"""Q012h2 H1 only: full fixed pilot, independent processes and full readback.

H2 solves and H3 including those solves are not implemented by this stage.
An H1 receipt must never promote itself to acceptance of Q012h2 or the goal.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from time import perf_counter

import numpy as np

from research import d3q27_cubic_chart as cubic
from research import d3q27_quartic_archive as archive
from research import d3q27_quartic_inputs as inputs
from research import d3q27_quartic_lbm as primary
from research import d3q27_quartic_physical as physical
from research import d3q27_quartic_polynomial as reference
from research import d3q27_quartic_resources as resources
from research import q012g_d3q27_cubic_chart as lower
from research import q012h2_d3q27_quartic_selection as selection

ROOT = Path(__file__).resolve().parents[1]
MODULE = "research.q012h2_d3q27_quartic_forcing"
OUTPUT = ROOT / "research/artifacts/q012h2_d3q27_quartic_forcing.json"
TESTS = ("tests/test_d3q27_quartic_lbm.py", "tests/test_q012h2_d3q27_quartic_forcing.py")
FILES = (
    "research/d3q27_quartic_lbm.py",
    "research/d3q27_quartic_polynomial.py",
    "research/d3q27_quartic_physical.py",
    "research/d3q27_quartic_inputs.py",
    "research/q012h2_d3q27_quartic_forcing.py",
    *TESTS,
)
BOUNDARY = "H1 forcing only; no H2 solve, complete H3 resource audit, full quartic chart, amplitude repair, SSM or TT advantage"
common, oracle = selection.common, selection.oracle
require, same = selection.require, selection.same


def metadata():
    return {
        "files": {name: oracle.normalized_sha((ROOT / name).read_bytes()) for name in FILES},
        "selection_source": selection.metadata(),
        "selection_sha256": inputs.SELECTION_SHA,
        "lower_source": {k: lower.metadata()[k] for k in lower.SOURCE_KEYS},
    }


def paths(output, size, route):
    require(
        size in (17, 33, 65) and route in ("primary", "worker"), "registered grid/route required"
    )
    return tuple(
        Path(output).with_name(f"{Path(output).stem}_n{size}_{route}{suffix}")
        for suffix in (".json", ".zip")
    )


def names(count, route):
    return (
        "header.json",
        *(f"tuple_{i:04d}.npz" for i in range(count)),
        *(("physical.npz",) if route == "worker" else ()),
    )


def tuple_arrays(data, group, route):
    if route == "worker":
        columns = reference.columns(group, inputs.BLOCK_INDICES)
        return {
            "keys": np.asarray([ids for ids, _ in columns], dtype=np.int64),
            **reference.group_forcing(data, group, inputs.BLOCK_INDICES),
        }
    require(route == "primary", "unknown forcing route")
    value = primary.block_product(data, group, inputs.BLOCK_INDICES)
    terms = primary.group_terms(data, value)
    return {
        "keys": np.asarray(value.keys, dtype=np.int64),
        "symmetric_basis": value.basis,
        "Taylor_factors": value.factors,
        "full_input_dynamics": value.full_dynamics,
        "input_dynamics": value.dynamics,
        "terms": terms.reshape(7 * 27, -1),
        "term_column_norms": np.linalg.norm(terms, axis=1),
        "forcing": primary.forcing(terms),
        "collision": terms[:4].sum(axis=0),
        "composition": terms[4:].sum(axis=0),
        **{
            f"without_{name}": primary.forcing(primary.group_terms(data, value, mutation=name))
            for name in primary.MUTATIONS
        },
    }


def physical_arrays(data, cases, sample):
    results = []
    for index, case in enumerate(cases):
        print(
            f"n{data.size} physical {index + 1}/{len(cases)} {case['slots']}",
            file=sys.stderr,
            flush=True,
        )
        result = physical.fourth_coefficient(data, case["slots"], sample=sample)
        results.append(result)
    return {
        "groups": np.asarray([c["group"] for c in cases], dtype=np.int64),
        "columns": np.asarray([c["column"] for c in cases], dtype=np.int64),
        "keys": np.asarray([c["slots"] for c in cases], dtype=np.int64),
        "scales": np.asarray([c["scale"] for c in cases], dtype=np.float64),
        "output_waves": np.asarray([r["output_wave"] for r in results], dtype=np.int64),
        "fft_counts": np.asarray(
            [r["fft_coefficients_inspected"] for r in results], dtype=np.int64
        ),
        "off_wave_norms": np.asarray(
            [r["off_wave_norm"] * c["scale"] for r, c in zip(results, cases, strict=True)]
        ),
        **{
            name: np.column_stack(
                [r[name] * c["scale"] for r, c in zip(results, cases, strict=True)]
            )
            for name in ("forcing", "collision", "composition")
        },
    }


def static_lower_receipt(value):
    return {
        key: item
        for key, item in value.items()
        if key not in ("fresh_rebuild_seconds", "cubic_load_and_audit_seconds")
    }


def recheck_lower(data, originals, loaded):
    require(
        same(inputs.fingerprint(data), loaded["lower_arrays"]),
        "lower Taylor coefficients changed during forcing",
    )
    expected = {k: v for k, v in loaded["fiber_load"].items() if k not in ("filename", "sha256")}
    require(same(cubic.validate_fibers(originals), expected), "original cubic arrays changed")


def resource_output(output):
    output = Path(output)
    return (
        output.with_name("q012h2_d3q27_quartic")
        if output.stem.startswith("q012h2_d3q27_quartic")
        else output
    )


def run_grid(output, size, route):
    record_path, zip_path = paths(output, size, route)
    failure = record_path.with_name(record_path.stem + "_failure.json")
    require(not any(p.exists() for p in (record_path, zip_path, failure)), "existing grid output")
    guard = None
    completed = 0
    try:
        # Include S0 files as well as this stage in the two-GiB experiment cap.
        guard = resources.Guard(resource_output(output))
        state = inputs.selection_state()
        source = metadata()
        commit = oracle.git_bytes("rev-parse", "HEAD").decode().strip()
        oracle.verify_source_commit(commit, source)
        groups = tuple(tuple(row["group"]) for row in state["selection"]["groups"])
        data, originals, loaded = inputs.load(size, sample=guard.sample)
        cases = physical.calibration_cases(groups, inputs.BLOCK_INDICES)
        header = {
            "stage": "Q012h2 H1",
            "scope": BOUNDARY,
            "source": source,
            "source_commit": commit,
            "size": size,
            "route": route,
            "process_id": os.getpid(),
            "selection_sha256": inputs.SELECTION_SHA,
            "lower_input": static_lower_receipt(loaded),
            "groups": groups,
        }
        start = perf_counter()
        with archive.Archive(zip_path, "x", names(len(groups), route)) as saved:
            saved.put_document("header.json", header)
            for ordinal, group in enumerate(groups):
                saved.put_arrays(f"tuple_{ordinal:04d}.npz", tuple_arrays(data, group, route))
                completed += 1
                guard.sample(f"written_tuple_{ordinal}")
                if completed % 25 == 0 or completed == len(groups):
                    print(f"n{size} {route} {completed}/{len(groups)}", file=sys.stderr, flush=True)
            if route == "worker":
                saved.put_arrays("physical.npz", physical_arrays(data, cases, guard.sample))
        calculation_write_seconds = perf_counter() - start
        guard.sample("archive_closed")
        start = perf_counter()
        with archive.Archive(zip_path, "r", names(len(groups), route)) as saved:
            require(same(saved.document("header.json"), header), "archive header differs")
            for ordinal, group in enumerate(groups):
                require(
                    archive.arrays_equal(
                        saved.arrays(f"tuple_{ordinal:04d}.npz"), tuple_arrays(data, group, route)
                    ),
                    f"saved tuple {ordinal} differs from complete rebuild",
                )
                guard.sample(f"rebuilt_saved_tuple_{ordinal}")
            if route == "worker":
                require(
                    archive.arrays_equal(
                        saved.arrays("physical.npz"), physical_arrays(data, cases, guard.sample)
                    ),
                    "saved physical coefficients differ from complete rebuild",
                )
        readback_seconds = perf_counter() - start
        recheck_lower(data, originals, loaded)
        require(same(source, metadata()), "source/runtime changed during grid run")
        guard.sample("all_saved_entries_rebuilt_and_input_rehashed")
        record = common.sealed(
            {
                "schema": "Q012h2 H1 grid v1",
                "scope": BOUNDARY,
                "size": size,
                "route": route,
                "process_id": os.getpid(),
                "source": source,
                "source_commit": commit,
                "lower_input": loaded,
                "groups": len(groups),
                "columns": 1826,
                "archive": {
                    "filename": zip_path.name,
                    "bytes": zip_path.stat().st_size,
                    "sha256": archive.file_sha(zip_path),
                },
                "calculation_and_write_seconds": calculation_write_seconds,
                "full_saved_entry_rebuild_seconds": readback_seconds,
                "resources": guard.records,
                "q012h2_outcome": "not_evaluated",
            }
        )
        common.save_exclusive(record_path, record)
        guard.sample("grid_record_saved_and_read_back")
        return {
            "process_id": os.getpid(),
            "filename": record_path.name,
            "sha256": archive.file_sha(record_path),
            "completion_resources": guard.records[-1],
        }
    except Exception as error:
        failure = record_path.with_name(record_path.stem + "_failure.json")
        if not failure.exists():
            common.save_exclusive(
                failure,
                common.sealed(
                    {
                        "stage": "Q012h2 H1 incomplete",
                        "scope": BOUNDARY,
                        "size": size,
                        "route": route,
                        "process_id": os.getpid(),
                        "completed_tuple_prefix": completed,
                        "error_type": type(error).__name__,
                        "error": str(error),
                        "resources": guard.records
                        if guard is not None
                        else getattr(error, "resource_records", []),
                        "q012h2_outcome": "inconclusive",
                        "partial_archive_preserved": zip_path.exists(),
                    }
                ),
            )
        raise


def read_grid(output, size, route):
    record_path, zip_path = paths(output, size, route)
    require(
        not record_path.with_name(record_path.stem + "_failure.json").exists(),
        "grid has incomplete marker",
    )
    row = common.read_json(record_path)
    common.unseal(row)
    require(
        row["schema"] == "Q012h2 H1 grid v1"
        and row["scope"] == BOUNDARY
        and row["size"] == size
        and row["route"] == route
        and row["groups"] == 698
        and row["columns"] == 1826
        and row["q012h2_outcome"] == "not_evaluated",
        "grid identity/coverage differs",
    )
    require(same(row["source"], metadata()), "grid source changed")
    oracle.verify_source_commit(row["source_commit"], row["source"])
    require(
        row["archive"]
        == {
            "filename": zip_path.name,
            "bytes": zip_path.stat().st_size,
            "sha256": archive.file_sha(zip_path),
        },
        "saved archive seal differs",
    )
    selection.validate_resources(row["resources"], "all_saved_entries_rebuilt_and_input_rehashed")
    return row, zip_path


def column_errors(actual, expected):
    require(
        actual.shape == expected.shape
        and actual.ndim == 2
        and actual.shape[0] == 27
        and actual.shape[1] > 0
        and np.isfinite(actual).all()
        and np.isfinite(expected).all(),
        "full finite matching columns required",
    )
    return np.linalg.norm(actual - expected, axis=0) / np.maximum(
        1e-14, np.linalg.norm(expected, axis=0)
    )


def compare_grid(output, size, groups):
    main, path = read_grid(output, size, "primary")
    worker, other_path = read_grid(output, size, "worker")
    require(main["process_id"] != worker["process_id"], "independent process missing")
    require(
        same(
            static_lower_receipt(main["lower_input"]), static_lower_receipt(worker["lower_input"])
        ),
        "primary and independent lower inputs differ",
    )
    columns, comparisons, nonzero = 0, [], np.zeros(7, dtype=np.int64)
    witnesses = {name: None for name in primary.MUTATIONS}
    expected_physical = physical.calibration_cases(groups, inputs.BLOCK_INDICES)
    with (
        archive.Archive(path, "r", names(len(groups), "primary")) as a,
        archive.Archive(other_path, "r", names(len(groups), "worker")) as b,
    ):
        for saved, row in ((a, main), (b, worker)):
            header = saved.document("header.json")
            require(
                same(header["groups"], groups)
                and same(header["source"], row["source"])
                and header["process_id"] == row["process_id"]
                and header["size"] == size
                and header["route"] == row["route"]
                and header["scope"] == BOUNDARY
                and same(header["lower_input"], static_lower_receipt(row["lower_input"])),
                "grid archive header differs from receipt",
            )
        for ordinal, group in enumerate(groups):
            left, right = a.arrays(f"tuple_{ordinal:04d}.npz"), b.arrays(f"tuple_{ordinal:04d}.npz")
            keys = np.asarray(
                [ids for ids, _ in reference.columns(group, inputs.BLOCK_INDICES)], dtype=np.int64
            )
            require(
                np.array_equal(left["keys"], keys) and np.array_equal(right["keys"], keys),
                "full mixed column coverage differs",
            )
            columns += len(keys)
            terms = left["terms"].reshape(7, 27, len(keys))
            require(
                np.array_equal(np.linalg.norm(terms, axis=1), left["term_column_norms"]),
                "saved group norm differs",
            )
            require(
                np.array_equal(primary.forcing(terms), left["forcing"]),
                "saved F4 does not equal seven groups",
            )
            nonzero += np.count_nonzero(left["term_column_norms"] != 0, axis=1)
            errors = {
                name: column_errors(left[name], right[name]).tolist()
                for name in ("forcing", "collision", "composition")
            }
            comparisons.append({"group": group, "column_errors": errors})
            for mutation in primary.MUTATIONS:
                wrong = left[f"without_{mutation}"]
                error = column_errors(wrong, right["forcing"])
                changed = np.linalg.norm(wrong - right["forcing"], axis=0)
                observable = np.flatnonzero(
                    (error > 1e-8)
                    & (changed > 1e-14)
                    & (np.linalg.norm(right["forcing"], axis=0) > 1e-14)
                )
                if witnesses[mutation] is None and len(observable):
                    j = int(observable[0])
                    witnesses[mutation] = {
                        "group": group,
                        "column": j,
                        "relative_error": float(error[j]),
                        "difference_norm": float(changed[j]),
                    }
        require(columns == 1826, "incomplete fixed-pilot column count")
        p = b.arrays("physical.npz")
        for key, expected in (
            ("groups", [r["group"] for r in expected_physical]),
            ("columns", [r["column"] for r in expected_physical]),
            ("keys", [r["slots"] for r in expected_physical]),
            ("scales", [r["scale"] for r in expected_physical]),
        ):
            require(
                np.array_equal(p[key], np.asarray(expected)),
                "physical calibration selection differs",
            )
        physics = []
        for index, case in enumerate(expected_physical):
            ordinal = groups.index(case["group"])
            left = a.arrays(f"tuple_{ordinal:04d}.npz")
            expected = left["forcing"][:, case["column"]]
            error = float(
                np.hypot(
                    np.linalg.norm(p["forcing"][:, index] - expected), p["off_wave_norms"][index]
                )
                / max(1e-14, np.linalg.norm(p["forcing"][:, index]))
            )
            require(p["fft_counts"][index] == 27 * size**3, "not every FFT output was inspected")
            require(
                np.array_equal(
                    p["output_waves"][index], selection.selection.group_wave(case["group"])
                ),
                "physical output wave differs",
            )
            physics.append(
                {
                    "group": case["group"],
                    "column": case["column"],
                    "relative_with_leakage": error,
                    "off_wave_norm": float(p["off_wave_norms"][index]),
                    "passed": error <= 1e-8,
                }
            )
    passed = (
        all(max(c["column_errors"]["forcing"]) <= 1e-8 for c in comparisons)
        and all(c["passed"] for c in physics)
        and all(w is not None for w in witnesses.values())
    )
    return {
        "size": size,
        "groups": len(groups),
        "columns": columns,
        "comparisons": comparisons,
        "term_names": list(primary.TERM_NAMES),
        "exact_nonzero_column_counts": nonzero.tolist(),
        "exact_zero_column_counts": (columns - nonzero).tolist(),
        "negative_controls": witnesses,
        "physical": physics,
        "h1_passed": passed,
        "q012h2_outcome": "not_evaluated",
    }


def call_child(output, size, route):
    process = subprocess.Popen(
        [
            sys.executable,
            "-u",
            "-W",
            "error",
            "-m",
            MODULE,
            "--output",
            str(output),
            "--grid",
            str(size),
            "--route",
            route,
        ],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        text=True,
    )
    stdout, _ = process.communicate()
    require(
        process.returncode == 0,
        f"grid {size}/{route} process {process.pid} exited {process.returncode}",
    )
    receipt = json.loads(stdout)
    require(receipt["process_id"] == process.pid, "actual process PID differs")
    return {"process_id": process.pid, "exit_code": process.returncode, "receipt": receipt}


def verify_execution(output, rows):
    require(len(rows) == 6, "all six actual grid processes required")
    for item, (size, route) in zip(
        rows, ((n, r) for n in (17, 33, 65) for r in ("primary", "worker")), strict=True
    ):
        path, _ = paths(output, size, route)
        row, _ = read_grid(output, size, route)
        require(
            type(item["exit_code"]) is int
            and item["exit_code"] == 0
            and item["process_id"] == row["process_id"] == item["receipt"]["process_id"]
            and item["receipt"]["filename"] == path.name
            and item["receipt"]["sha256"] == archive.file_sha(path),
            "execution evidence differs",
        )
        selection.validate_resources(
            row["resources"] + [item["receipt"]["completion_resources"]],
            "grid_record_saved_and_read_back",
        )


def execute(output):
    output = Path(output)
    require(
        not any(output.parent.glob(output.stem + "*")),
        "existing output or partial run; choose a new path",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    source = metadata()
    commit = oracle.git_bytes("rev-parse", "HEAD").decode().strip()
    oracle.verify_source_commit(commit, source)
    state = inputs.selection_state(full=True)
    print("Full S0 and parent audits passed", file=sys.stderr, flush=True)
    lower_audit = lower.input_audit()
    require(lower_audit["passed"], "full lower source/artifact chain audit failed")
    controls = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-W", "error", *TESTS],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    require(
        controls.returncode == 0,
        "forcing implementation controls failed: " + controls.stdout + controls.stderr,
    )
    groups = tuple(tuple(r["group"]) for r in state["selection"]["groups"])
    execution = []
    comparisons = []
    for size in (17, 33, 65):
        for route in ("primary", "worker"):
            execution.append(call_child(output, size, route))
        comparisons.append(compare_grid(output, size, groups))
    verify_execution(output, execution)
    require(
        same(source, metadata()) and same(state, inputs.selection_state()),
        "final input/source differs",
    )
    decision = {
        "stage": "H1_forcing_only",
        "h1_passed": all(r["h1_passed"] for r in comparisons),
        "q012h2_outcome": "not_evaluated",
        "H2": "not_evaluated",
        "H3_with_solves": "not_evaluated",
    }
    result = common.sealed(
        {
            "schema": "Q012h2 H1 v1",
            "scope": BOUNDARY,
            "source": source,
            "source_commit": commit,
            "lower_audit": lower_audit,
            "controls": {
                "exit_code": controls.returncode,
                "stdout": controls.stdout,
                "stderr": controls.stderr,
            },
            "execution": execution,
            "grids": comparisons,
            "decision": decision,
        }
    )
    common.save_exclusive(output, result)
    require(
        same(audit_manifest(output, full=False), decision), "final full saved comparison differs"
    )
    return decision


def audit_saved_grid(output, size, route):
    """Fresh full input and every saved numerical entry, in a read-only process."""
    guard = resources.Guard(resource_output(output))
    row, path = read_grid(output, size, route)
    state = inputs.selection_state()
    groups = tuple(tuple(r["group"]) for r in state["selection"]["groups"])
    data, originals, loaded = inputs.load(size, sample=guard.sample)
    require(
        same(static_lower_receipt(loaded), static_lower_receipt(row["lower_input"])),
        "fresh audited lower input differs from saved input",
    )
    with archive.Archive(path, "r", names(len(groups), route)) as saved:
        for ordinal, group in enumerate(groups):
            require(
                archive.arrays_equal(
                    saved.arrays(f"tuple_{ordinal:04d}.npz"), tuple_arrays(data, group, route)
                ),
                f"fresh saved-entry audit differs at tuple {ordinal}",
            )
            guard.sample(f"fresh_audit_tuple_{ordinal}")
        if route == "worker":
            cases = physical.calibration_cases(groups, inputs.BLOCK_INDICES)
            require(
                archive.arrays_equal(
                    saved.arrays("physical.npz"), physical_arrays(data, cases, guard.sample)
                ),
                "fresh physical readback differs",
            )
    recheck_lower(data, originals, loaded)
    require(
        same(row["source"], metadata()) and archive.file_sha(path) == row["archive"]["sha256"],
        "saved source or archive changed during audit",
    )
    guard.sample("fresh_read_only_full_audit_complete")
    return {
        "process_id": os.getpid(),
        "size": size,
        "route": route,
        "groups": 698,
        "columns": 1826,
        "passed": True,
        "resources": guard.records,
    }


def audit_manifest(output, *, full=True):
    output = Path(output)
    require(
        not output.with_name(output.stem + "_failure.json").exists(), "incomplete manifest marker"
    )
    row = common.read_json(output)
    common.unseal(row)
    require(
        row["schema"] == "Q012h2 H1 v1"
        and row["scope"] == BOUNDARY
        and same(row["source"], metadata()),
        "H1 manifest identity or source differs",
    )
    oracle.verify_source_commit(row["source_commit"], row["source"])
    require(
        row["controls"]["exit_code"] == 0
        and re.search(r"\b\d+ passed\b", row["controls"]["stdout"]),
        "successful implementation controls missing",
    )
    state = inputs.selection_state(full=full)
    if full:
        require(
            same(row["lower_audit"], lower.input_audit()) and row["lower_audit"]["passed"],
            "full lower chain audit differs",
        )
    verify_execution(output, row["execution"])
    groups = tuple(tuple(r["group"]) for r in state["selection"]["groups"])
    comparisons = []
    for size in (17, 33, 65):
        if full:
            for route in ("primary", "worker"):
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-u",
                        "-W",
                        "error",
                        "-m",
                        MODULE,
                        "--output",
                        str(output),
                        "--grid",
                        str(size),
                        "--route",
                        route,
                        "--audit-only",
                    ],
                    cwd=ROOT,
                    stdout=subprocess.PIPE,
                    text=True,
                )
                stdout, _ = process.communicate()
                require(
                    process.returncode == 0,
                    f"fresh grid audit process {process.pid} exited {process.returncode}",
                )
                receipt = json.loads(stdout)
                require(
                    receipt["process_id"] == process.pid and receipt["passed"] is True,
                    "fresh audit PID or result differs",
                )
                selection.validate_resources(
                    receipt["resources"], "fresh_read_only_full_audit_complete"
                )
        comparisons.append(compare_grid(output, size, groups))
    require(same(row["grids"], comparisons), "saved all-column comparisons differ")
    expected = {
        "stage": "H1_forcing_only",
        "h1_passed": all(r["h1_passed"] for r in comparisons),
        "q012h2_outcome": "not_evaluated",
        "H2": "not_evaluated",
        "H3_with_solves": "not_evaluated",
    }
    require(
        same(row["decision"], expected) and same(row["source"], metadata()),
        "H1-only decision changed",
    )
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--grid", type=int, choices=(17, 33, 65))
    parser.add_argument("--route", choices=("primary", "worker"))
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if (args.grid is None) != (args.route is None):
        parser.error("grid and route must be supplied together")
    if (
        not args.audit_only
        and args.grid is None
        and any(args.output.parent.glob(args.output.stem + "*"))
    ):
        parser.error("existing output or partial run; use --audit-only or a new path")
    try:
        if args.audit_only:
            result = (
                audit_manifest(args.output)
                if args.grid is None
                else audit_saved_grid(args.output, args.grid, args.route)
            )
        else:
            result = (
                execute(args.output)
                if args.grid is None
                else run_grid(args.output, args.grid, args.route)
            )
        print(json.dumps(result, allow_nan=False), flush=True)
    except Exception as error:
        if args.grid is None and not args.audit_only and not args.output.exists():
            path = args.output.with_name(args.output.stem + "_failure.json")
            if not path.exists():
                common.save_exclusive(
                    path,
                    common.sealed(
                        {
                            "stage": "Q012h2 H1 incomplete",
                            "scope": BOUNDARY,
                            "process_id": os.getpid(),
                            "error_type": type(error).__name__,
                            "error": str(error),
                            "q012h2_outcome": "inconclusive",
                        }
                    ),
                )
        raise


if __name__ == "__main__":
    main()
