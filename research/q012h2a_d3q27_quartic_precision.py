"""Q012h2a: full fixed-pilot precision diagnosis, never H2/H3 acceptance."""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from time import perf_counter

import gmpy2 as mp
import numpy as np

from research import d3q27_quartic_forcing_audit as old_diagnostic
from research import d3q27_quartic_mp_validation as validation
from research import q012h2_d3q27_quartic_forcing as parent

ROOT = parent.ROOT
MODULE = "research.q012h2a_d3q27_quartic_precision"
OUTPUT = ROOT / "research/artifacts/q012h2a_d3q27_quartic_precision.json"
PARENT_SHA = "b2ec4ed701a677c6ddbca1016b45c3de3d4861ee9c20d98592bfb262e3d58df6"
DIAGNOSTIC_SHA = "6f6c72eef1f8d93f6083ae0e88ce52a205daacad880e163df46bb913600004a3"
PREREG = "docs/D3Q27_QUARTIC_FORCING_PRECISION.md"
PREREG_COMMIT = "4ffbbb06105531ebfc4d031686666fa63cbdfce4"
TESTS = ("tests/test_d3q27_quartic_mp.py", "tests/test_q012h2a_d3q27_quartic_precision.py")
FILES = (
    "research/d3q27_quartic_mp.py",
    "research/d3q27_quartic_mp_numbers.py",
    "research/d3q27_quartic_mp_reference.py",
    "research/d3q27_quartic_mp_validation.py",
    "research/q012h2a_d3q27_quartic_precision.py",
    *TESTS,
)
BOUNDARY = "arithmetic of frozen rounded Taylor inputs only; no H2 solve, full H3, quartic chart, amplitude repair, SSM or TT advantage"
common, oracle, archive = parent.common, parent.oracle, parent.archive
inputs, resources, selection = parent.inputs, parent.resources, parent.selection
require, same, paths = parent.require, parent.same, parent.paths


def metadata():
    prefix = oracle.git_bytes("show", f"{PREREG_COMMIT}:{PREREG}").decode("utf-8")
    require(
        (ROOT / PREREG).read_text(encoding="utf-8").startswith(prefix),
        "frozen preregistration prefix changed",
    )
    return {
        "files": {name: oracle.normalized_sha((ROOT / name).read_bytes()) for name in FILES},
        "parent_source": parent.metadata(),
        "parent_sha256": PARENT_SHA,
        "diagnostic_sha256": DIAGNOSTIC_SHA,
        "preregistration": {
            "file": PREREG,
            "commit": PREREG_COMMIT,
            "prefix_sha256": oracle.normalized_sha(prefix.encode()),
        },
        "GMP_runtime": {
            "gmpy2": mp.version(),
            "GMP": mp.mp_version(),
            "MPFR": mp.mpfr_version(),
            "MPC": mp.mpc_version(),
        },
    }


def read_parent():
    require(archive.file_sha(parent.OUTPUT) == PARENT_SHA, "original H1 manifest changed")
    path = parent.OUTPUT.with_name("q012h2_d3q27_quartic_forcing_diagnostics.json")
    require(archive.file_sha(path) == DIAGNOSTIC_SHA, "original full-column diagnostic changed")
    result, diagnostic = common.read_json(parent.OUTPUT), common.read_json(path)
    common.unseal(result)
    common.unseal(diagnostic)
    oracle.verify_source_commit(diagnostic["source_commit"], diagnostic["source"])
    require(same(result["source"], parent.metadata()), "old scientific source/runtime changed")
    require(
        not result["decision"]["h1_passed"]
        and [g["summary"]["failed_columns"] for g in diagnostic["grids"]] == [182, 174, 158],
        "old H1 failure identity differs",
    )
    return result, diagnostic


def audit_parent(*, full):
    original, diagnostic = read_parent()
    require(
        same(parent.audit_manifest(parent.OUTPUT, full=full), original["decision"]),
        "original full H1 audit differs",
    )
    rebuilt = old_diagnostic.audit(parent.OUTPUT)
    require(
        same(
            rebuilt,
            {k: v for k, v in diagnostic.items() if k not in ("source", "source_commit", "sha256")},
        ),
        "original all-column diagnostic differs",
    )
    return {
        "parent_sha256": PARENT_SHA,
        "diagnostic_sha256": DIAGNOSTIC_SHA,
        "columns": 5478,
        "failed_columns": 514,
        "full_fresh_entry_audit": full,
        "original_decision": original["decision"],
        "passed": True,
    }


def names(count):
    return (
        "header.json",
        *(name for i in range(count) for name in (f"tuple_{i:04d}.json", f"tuple_{i:04d}.npz")),
    )


def selected_groups():
    state = inputs.selection_state()
    return tuple(tuple(r["group"]) for r in state["selection"]["groups"])


def old_grid(size):
    original, _ = read_parent()
    return next(g for g in original["grids"] if g["size"] == size)


def mutations_for(witnesses, group, route):
    return tuple(
        name
        for name in parent.primary.MUTATIONS
        if route == "primary" and same(witnesses[name]["group"], group)
    )


def resource_output(output):
    """Count preserved failed attempts as part of the same diagnostic family."""
    output = Path(output)
    return output.with_name(OUTPUT.stem) if output.stem.startswith(OUTPUT.stem) else output


def total_bytes(output):
    output = resource_output(output)
    return sum(p.stat().st_size for p in output.parent.glob(output.stem + "*") if p.is_file())


def header_for(size, route, commit, source, loaded, groups):
    return {
        "stage": "Q012h2a",
        "scope": BOUNDARY,
        "size": size,
        "route": route,
        "process_id": os.getpid(),
        "source_commit": commit,
        "source": source,
        "lower_input": parent.static_lower_receipt(loaded),
        "groups": groups,
        "precisions": [128, 192],
        "parent_sha256": PARENT_SHA,
    }


def rebuild_entries(saved, data, groups, route, witnesses, guard, *, stage):
    for ordinal, group in enumerate(groups):
        mutations = mutations_for(witnesses, group, route)
        document, arrays = (
            saved.document(f"tuple_{ordinal:04d}.json"),
            saved.arrays(f"tuple_{ordinal:04d}.npz"),
        )
        validation.validate_payload(
            document, arrays, group, inputs.BLOCK_INDICES, 104, route, mutations
        )
        expected, values = validation.payload(data, group, inputs.BLOCK_INDICES, route, mutations)
        require(
            same(document, expected) and archive.arrays_equal(arrays, values),
            f"all saved entries differ at tuple {ordinal}",
        )
        guard.sample(f"{stage}_{ordinal}")
        if (ordinal + 1) % 50 == 0 or ordinal == len(groups) - 1:
            print(
                f"n{data.size} {route} {stage} {ordinal + 1}/{len(groups)}",
                file=sys.stderr,
                flush=True,
            )


def save_failure(path, error, *, size=None, route=None, completed=0, guard=None, partial=False):
    if not path.exists():
        # Do not replace missing child-start evidence with a later observation.
        try:
            observed = {
                "scope": "outer process after exception; not child-start evidence",
                **resources.counters(),
                "free_disk_bytes": shutil.disk_usage(path.parent).free,
            }
        except (OSError, RuntimeError) as observation_error:
            observed = {"unavailable": type(observation_error).__name__}
        common.save_exclusive(
            path,
            common.sealed(
                {
                    "stage": "Q012h2a incomplete",
                    "scope": BOUNDARY,
                    "process_id": os.getpid(),
                    "size": size,
                    "route": route,
                    "completed_tuple_prefix": completed,
                    "error_type": type(error).__name__,
                    "error": str(error),
                    "resources": guard.records
                    if guard is not None
                    else getattr(error, "resource_records", []),
                    "partial_archive_preserved": partial,
                    "outer_failure_observation": observed,
                    "q012h2a_outcome": "inconclusive",
                    "q012h2_outcome": "not_evaluated",
                }
            ),
        )


def run_grid(output, size, route):
    record_path, zip_path = paths(output, size, route)
    failure = record_path.with_name(record_path.stem + "_failure.json")
    require(not any(p.exists() for p in (record_path, zip_path, failure)), "existing grid output")
    guard, completed = None, 0
    try:
        guard = resources.Guard(resource_output(output))
        source = metadata()
        commit = oracle.git_bytes("rev-parse", "HEAD").decode().strip()
        oracle.verify_source_commit(commit, source)
        groups, original = selected_groups(), old_grid(size)
        data, originals, loaded = inputs.load(size, sample=guard.sample)
        previous, _ = parent.read_grid(parent.OUTPUT, size, route)
        require(
            same(
                parent.static_lower_receipt(loaded),
                parent.static_lower_receipt(previous["lower_input"]),
            ),
            "original/fresh full lower input differs",
        )
        header = header_for(size, route, commit, source, loaded, groups)
        start = perf_counter()
        with archive.Archive(zip_path, "x", names(len(groups))) as saved:
            saved.put_document("header.json", header)
            for ordinal, group in enumerate(groups):
                mutations = mutations_for(original["negative_controls"], group, route)
                document, arrays = validation.payload(
                    data, group, inputs.BLOCK_INDICES, route, mutations
                )
                validation.validate_payload(
                    document, arrays, group, inputs.BLOCK_INDICES, 104, route, mutations
                )
                saved.put_document(f"tuple_{ordinal:04d}.json", document)
                saved.put_arrays(f"tuple_{ordinal:04d}.npz", arrays)
                completed += 1
                guard.sample(f"written_tuple_{ordinal}")
                if completed % 25 == 0 or completed == len(groups):
                    print(
                        f"n{size} {route} written {completed}/{len(groups)}",
                        file=sys.stderr,
                        flush=True,
                    )
        calculation_seconds = perf_counter() - start
        guard.sample("archive_closed")
        start = perf_counter()
        with archive.Archive(zip_path, "r", names(len(groups))) as saved:
            require(same(saved.document("header.json"), header), "saved header differs")
            rebuild_entries(
                saved,
                data,
                groups,
                route,
                original["negative_controls"],
                guard,
                stage="rebuilt_saved_tuple",
            )
        rebuild_seconds = perf_counter() - start
        parent.recheck_lower(data, originals, loaded)
        require(same(source, metadata()), "scientific source/runtime changed")
        guard.sample("all_saved_entries_rebuilt_and_input_rehashed")
        record = common.sealed(
            {
                "schema": "Q012h2a grid v1",
                "scope": BOUNDARY,
                "size": size,
                "route": route,
                "source": source,
                "source_commit": commit,
                "process_id": os.getpid(),
                "lower_input": loaded,
                "groups": 698,
                "columns": 1826,
                "precisions": [128, 192],
                "archive": {
                    "filename": zip_path.name,
                    "bytes": zip_path.stat().st_size,
                    "sha256": archive.file_sha(zip_path),
                },
                "calculation_and_write_seconds": calculation_seconds,
                "full_saved_entry_rebuild_seconds": rebuild_seconds,
                "resources": guard.records,
                "q012h2_outcome": "not_evaluated",
            }
        )
        common.save_exclusive(record_path, record)
        require(same(common.read_json(record_path), record), "grid record readback differs")
        guard.sample("grid_record_saved_and_read_back")
        return {
            "process_id": os.getpid(),
            "filename": record_path.name,
            "sha256": archive.file_sha(record_path),
            "completion_resources": guard.records[-1],
        }
    except Exception as error:
        save_failure(
            failure,
            error,
            size=size,
            route=route,
            completed=completed,
            guard=guard,
            partial=zip_path.exists(),
        )
        raise


def read_grid(output, size, route):
    record_path, zip_path = paths(output, size, route)
    require(
        not record_path.with_name(record_path.stem + "_failure.json").exists(),
        "incomplete grid marker",
    )
    row = common.read_json(record_path)
    common.unseal(row)
    require(
        row["schema"] == "Q012h2a grid v1"
        and row["scope"] == BOUNDARY
        and row["size"] == size
        and row["route"] == route
        and row["groups"] == 698
        and row["columns"] == 1826
        and row["precisions"] == [128, 192]
        and type(row["process_id"]) is int
        and row["process_id"] > 0
        and row["q012h2_outcome"] == "not_evaluated",
        "grid identity/coverage differs",
    )
    require(same(row["source"], metadata()), "new source/runtime changed")
    oracle.verify_source_commit(row["source_commit"], row["source"])
    require(
        row["archive"]
        == {
            "filename": zip_path.name,
            "bytes": zip_path.stat().st_size,
            "sha256": archive.file_sha(zip_path),
        },
        "grid archive seal differs",
    )
    selection.validate_resources(row["resources"], "all_saved_entries_rebuilt_and_input_rehashed")
    return row, zip_path


def check_header(header, row, groups):
    expected = {
        "stage": "Q012h2a",
        "scope": BOUNDARY,
        "size": row["size"],
        "route": row["route"],
        "process_id": row["process_id"],
        "source_commit": row["source_commit"],
        "source": row["source"],
        "lower_input": parent.static_lower_receipt(row["lower_input"]),
        "groups": groups,
        "precisions": [128, 192],
        "parent_sha256": PARENT_SHA,
    }
    require(same(header, expected), "grid archive header differs")


def compare_grid(output, size, groups):
    left_row, left_path = read_grid(output, size, "primary")
    right_row, right_path = read_grid(output, size, "worker")
    require(
        left_row["process_id"] != right_row["process_id"], "independent arithmetic process missing"
    )
    require(
        same(
            parent.static_lower_receipt(left_row["lower_input"]),
            parent.static_lower_receipt(right_row["lower_input"]),
        ),
        "arithmetic inputs differ",
    )
    old_a, old_path_a = parent.read_grid(parent.OUTPUT, size, "primary")
    old_b, old_path_b = parent.read_grid(parent.OUTPUT, size, "worker")
    for new, old in ((left_row, old_a), (right_row, old_b)):
        require(
            same(
                parent.static_lower_receipt(new["lower_input"]),
                parent.static_lower_receipt(old["lower_input"]),
            ),
            "original full lower input differs",
        )
    original = old_grid(size)
    comparisons, witnesses, physics = [], {}, []
    with (
        archive.Archive(left_path, "r", names(698)) as a,
        archive.Archive(right_path, "r", names(698)) as b,
        archive.Archive(old_path_a, "r", parent.names(698, "primary")) as oa,
        archive.Archive(old_path_b, "r", parent.names(698, "worker")) as ob,
    ):
        check_header(a.document("header.json"), left_row, groups)
        check_header(b.document("header.json"), right_row, groups)
        for ordinal, group in enumerate(groups):
            aa, bb = a.arrays(f"tuple_{ordinal:04d}.npz"), b.arrays(f"tuple_{ordinal:04d}.npz")
            mutations = mutations_for(original["negative_controls"], group, "primary")
            main, wrong = validation.validate_payload(
                a.document(f"tuple_{ordinal:04d}.json"),
                aa,
                group,
                inputs.BLOCK_INDICES,
                104,
                "primary",
                mutations,
            )
            other, _ = validation.validate_payload(
                b.document(f"tuple_{ordinal:04d}.json"),
                bb,
                group,
                inputs.BLOCK_INDICES,
                104,
                "worker",
            )
            comparison = validation.compare_columns(
                group,
                main,
                other,
                aa,
                bb,
                oa.arrays(f"tuple_{ordinal:04d}.npz"),
                ob.arrays(f"tuple_{ordinal:04d}.npz"),
            )
            require(
                same(
                    comparison["original_binary64_errors"],
                    original["comparisons"][ordinal]["column_errors"],
                ),
                "original all-column errors changed",
            )
            comparisons.append(comparison)
            for mutation in mutations:
                witnesses[mutation] = validation.mutation_witness(
                    wrong[mutation], other[192]["forcing"], original["negative_controls"][mutation]
                )
        physical = ob.arrays("physical.npz")
        cases = parent.physical.calibration_cases(groups, inputs.BLOCK_INDICES)
        for name, expected in (
            ("groups", [r["group"] for r in cases]),
            ("columns", [r["column"] for r in cases]),
            ("keys", [r["slots"] for r in cases]),
            ("scales", [r["scale"] for r in cases]),
        ):
            require(
                np.array_equal(physical[name], np.asarray(expected)),
                "fixed physical selection differs",
            )
        for index, case in enumerate(cases):
            ordinal = groups.index(case["group"])
            require(
                physical["fft_counts"][index] == 27 * size**3
                and np.array_equal(
                    physical["output_waves"][index], selection.selection.group_wave(case["group"])
                ),
                "full physical Fourier leakage coverage differs",
            )
            errors = {}
            for route, saved in (("primary", a), ("worker", b)):
                expected = saved.arrays(f"tuple_{ordinal:04d}.npz")["rounded192_forcing"][
                    :, case["column"]
                ]
                errors[route] = float(
                    np.hypot(
                        np.linalg.norm(physical["forcing"][:, index] - expected),
                        physical["off_wave_norms"][index],
                    )
                    / max(1e-14, np.linalg.norm(physical["forcing"][:, index]))
                )
            physics.append(
                {
                    "group": list(case["group"]),
                    "column": case["column"],
                    "relative_with_leakage": errors,
                    "off_wave_norm": float(physical["off_wave_norms"][index]),
                    "passed": all(v <= 1e-8 for v in errors.values()),
                }
            )
    return {
        "size": size,
        "groups": 698,
        "columns": 1826,
        "comparisons": comparisons,
        "physical": physics,
        "negative_controls": witnesses,
        "summary": validation.summarize(comparisons, physics, witnesses),
    }


def call_child(output, size, route, *, audit=False):
    command = [
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
    ]
    if audit:
        command.append("--audit-only")
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, text=True)
    stdout, _ = process.communicate()
    require(
        process.returncode == 0,
        f"grid {size}/{route} process {process.pid} exited {process.returncode}",
    )
    receipt = json.loads(stdout)
    require(receipt["process_id"] == process.pid, "actual child PID differs")
    return {"process_id": process.pid, "exit_code": process.returncode, "receipt": receipt}


def verify_execution(output, execution):
    require(
        len(execution) == 6 and len({e["process_id"] for e in execution}) == 6,
        "six distinct actual grid processes required",
    )
    for item, (size, route) in zip(
        execution, ((n, r) for n in (17, 33, 65) for r in ("primary", "worker")), strict=True
    ):
        path, _ = paths(output, size, route)
        row, _ = read_grid(output, size, route)
        receipt = item["receipt"]
        require(
            type(item["exit_code"]) is int
            and item["exit_code"] == 0
            and item["process_id"] == row["process_id"] == receipt["process_id"]
            and receipt["filename"] == path.name
            and receipt["sha256"] == archive.file_sha(path),
            "actual execution evidence differs",
        )
        selection.validate_resources(
            row["resources"] + [receipt["completion_resources"]], "grid_record_saved_and_read_back"
        )


def audit_saved_grid(output, size, route):
    guard = resources.Guard(resource_output(output))
    row, path = read_grid(output, size, route)
    groups, original = selected_groups(), old_grid(size)
    data, originals, loaded = inputs.load(size, sample=guard.sample)
    require(
        same(parent.static_lower_receipt(loaded), parent.static_lower_receipt(row["lower_input"])),
        "fresh full Taylor input differs",
    )
    with archive.Archive(path, "r", names(698)) as saved:
        check_header(saved.document("header.json"), row, groups)
        rebuild_entries(
            saved,
            data,
            groups,
            route,
            original["negative_controls"],
            guard,
            stage="fresh_audit_tuple",
        )
    parent.recheck_lower(data, originals, loaded)
    require(
        same(row["source"], metadata()) and archive.file_sha(path) == row["archive"]["sha256"],
        "source/archive changed during fresh audit",
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
        row["schema"] == "Q012h2a v1"
        and row["scope"] == BOUNDARY
        and same(row["source"], metadata()),
        "precision manifest identity/source differs",
    )
    oracle.verify_source_commit(row["source_commit"], row["source"])
    expected_parent = audit_parent(full=full)
    require(
        row["parent_audit"]["full_fresh_entry_audit"] is True
        and same(
            {k: v for k, v in row["parent_audit"].items() if k != "full_fresh_entry_audit"},
            {k: v for k, v in expected_parent.items() if k != "full_fresh_entry_audit"},
        ),
        "original full parent audit missing or changed",
    )
    require(
        row["controls"]["exit_code"] == 0
        and re.search(r"\b\d+ passed\b", row["controls"]["stdout"]),
        "successful arithmetic controls missing",
    )
    verify_execution(output, row["execution"])
    groups, comparisons, fresh = selected_groups(), [], []
    for size in (17, 33, 65):
        if full:
            for route in ("primary", "worker"):
                item = call_child(output, size, route, audit=True)
                receipt = item["receipt"]
                require(
                    receipt["passed"] is True
                    and receipt["size"] == size
                    and receipt["route"] == route
                    and receipt["groups"] == 698
                    and receipt["columns"] == 1826,
                    "fresh full-entry audit identity differs",
                )
                selection.validate_resources(
                    receipt["resources"], "fresh_read_only_full_audit_complete"
                )
                fresh.append(
                    {
                        "process_id": item["process_id"],
                        "exit_code": item["exit_code"],
                        "size": size,
                        "route": route,
                        "completion_resources": receipt["resources"][-1],
                    }
                )
        comparisons.append(compare_grid(output, size, groups))
    require(same(row["grids"], comparisons), "all saved diagnostics or classifications differ")
    expected = validation.decision(comparisons)
    require(
        same(row["decision"], expected) and same(row["source"], metadata()),
        "diagnostic-only decision changed",
    )
    require(total_bytes(output) <= resources.DISK_LIMIT, "all new diagnostic files exceed disk cap")
    return {"decision": expected, "fresh_execution": fresh}


def execute(output):
    output = Path(output)
    require(
        not any(output.parent.glob(output.stem + "*")),
        "existing output or partial run; use a new path",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    preflight = None
    try:
        source = metadata()
        commit = oracle.git_bytes("rev-parse", "HEAD").decode().strip()
        oracle.verify_source_commit(commit, source)
        # Snapshot before the expensive frozen parent audit. Every grid/route
        # still measures its own start and peaks with the unchanged Guard.
        preflight = resources.Guard(resource_output(output))
        parent_audit = audit_parent(full=True)
        print("Full original H1/514-failure audits passed", file=sys.stderr, flush=True)
        controls = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-W", "error", *TESTS],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        require(
            controls.returncode == 0,
            "arithmetic implementation controls failed: " + controls.stdout + controls.stderr,
        )
        groups, execution, comparisons = selected_groups(), [], []
        for size in (17, 33, 65):
            for route in ("primary", "worker"):
                execution.append(call_child(output, size, route))
            comparison = compare_grid(output, size, groups)
            comparisons.append(comparison)
            print(json.dumps({"size": size, **comparison["summary"]}), file=sys.stderr, flush=True)
        verify_execution(output, execution)
        require(same(source, metadata()), "source changed during execution")
        decision = validation.decision(comparisons)
        result = common.sealed(
            {
                "schema": "Q012h2a v1",
                "scope": BOUNDARY,
                "source": source,
                "source_commit": commit,
                "parent_audit": parent_audit,
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
            same(audit_manifest(output, full=False)["decision"], decision),
            "final saved decision differs",
        )
        return decision
    except Exception as error:
        save_failure(output.with_name(output.stem + "_failure.json"), error, guard=preflight)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--grid", type=int, choices=(17, 33, 65))
    parser.add_argument("--route", choices=("primary", "worker"))
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    if (args.grid is None) != (args.route is None):
        parser.error("grid and route must be supplied together")
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


if __name__ == "__main__":
    main()
