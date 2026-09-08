"""Q012h2 stage S0, with sealed full scans and actual sequential processes.

This runner intentionally has no forcing or coefficient solver. A successful
selection receipt leaves Q012h2 H1/H2/H3, the full chart and the goal unfinished.
"""

import argparse
import json
import os
import re
import subprocess
import sys
from itertools import product
from pathlib import Path

# Per-process numerical runtime configuration, not persistent machine settings.
for _variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_variable] = "1"

import numpy as np

from research import d3q27_chart as chart
from research import d3q27_quartic_archive as storage
from research import d3q27_quartic_resources as resources
from research import d3q27_quartic_selection as selection
from research import d3q27_quartic_selection_reference as reference
from research import q012h0_d3q27_quartic_census as common
from research import q012h1_d3q27_quartic_oracle as oracle

ROOT = Path(__file__).resolve().parents[1]
MODULE = "research.q012h2_d3q27_quartic_selection"
PARENT = ROOT / "research/artifacts/q012h1_d3q27_quartic_oracle.json"
PARENT_SHA = "fb70d3b9f8e75505b337c7eaf75db084b3fcce733170069069af8284acd66682"
DEFAULT_OUTPUT = PARENT.with_name("q012h2_d3q27_quartic_selection.json")
PREREG_COMMIT = "1db06d0b9056742e53e228f5ba4e5d9a34b02cd3"
PREREG_PATH = "docs/D3Q27_QUARTIC_PILOT.md"
CONTROL_TESTS = (
    "tests/test_d3q27_quartic_selection.py",
    "tests/test_d3q27_quartic_resources.py",
    "tests/test_q012h2_d3q27_quartic_selection.py",
)
SOURCE_FILES = (
    "research/d3q27_quartic_selection.py",
    "research/d3q27_quartic_selection_reference.py",
    "research/d3q27_quartic_resources.py",
    "research/q012h2_d3q27_quartic_selection.py",
    *CONTROL_TESTS,
)
BOUNDARY = (
    "S0 binary64 spectral-distance selection only, sharing rounded spectral inputs; "
    "not a quartic forcing/solve, rank certificate, full-resource forecast, "
    "finite-amplitude improvement, SSM existence or TT advantage."
)
require, same = common.require, common.same


def metadata():
    prereg = oracle.git_bytes("show", f"{PREREG_COMMIT}:{PREREG_PATH}").replace(b"\r\n", b"\n")
    require(
        (ROOT / PREREG_PATH).read_bytes().replace(b"\r\n", b"\n").startswith(prereg),
        "Q012h2 preregistration changed",
    )
    return {
        "files": {name: oracle.normalized_sha((ROOT / name).read_bytes()) for name in SOURCE_FILES},
        "prior_source": oracle.metadata(),
        "preregistration_sha256": oracle.normalized_sha(prereg),
        "thread_environment": {
            name: os.environ.get(name)
            for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
        },
    }


def parent_state(full=False):
    require(oracle.normalized_sha(PARENT.read_bytes()) == PARENT_SHA, "Q012h1 parent changed")
    value = common.read_json(PARENT)
    common.unseal(value)
    require(same(value["audit"]["source"], oracle.metadata()), "parent source mismatch")
    if full:
        require(same(value["decision"], oracle.audit_manifest(PARENT)), "full parent audit differs")
    require(
        value["decision"]["study_gate"] == "passed"
        and value["decision"]["scientific_outcome"] == "accepted",
        "parent not accepted",
    )
    return {"filename": PARENT.name, "sha256": PARENT_SHA, "decision": value["decision"]}


def paths(output, size, route):
    require(
        type(size) is int and size in selection.SIZES and route in ("primary", "worker"),
        "registered grid and route required",
    )
    stem = f"{Path(output).stem}_n{size}_{route}"
    return tuple(Path(output).with_name(stem + suffix) for suffix in (".json", ".npz"))


def save_arrays(path, arrays):
    require(isinstance(arrays, dict) and bool(arrays), "nonempty array mapping required")
    for key, value in arrays.items():
        require(
            type(key) is str
            and key.isidentifier()
            and isinstance(value, np.ndarray)
            and value.dtype in (np.dtype("int64"), np.dtype("float64"), np.dtype("complex128"))
            and value.size > 0
            and np.isfinite(value).all(),
            "invalid numerical array",
        )
    with Path(path).open("xb") as stream:
        np.savez_compressed(stream, **arrays)
    return {
        "filename": Path(path).name,
        "bytes": Path(path).stat().st_size,
        "sha256": storage.file_sha(path),
        "arrays": {name: chart.array_metadata(value) for name, value in arrays.items()},
    }


def load_arrays(path, expected):
    path = Path(path)
    require(set(expected) == {"filename", "bytes", "sha256", "arrays"}, "archive fields differ")
    require(
        path.name == expected["filename"]
        and path.stat().st_size == expected["bytes"]
        and storage.file_sha(path) == expected["sha256"],
        "archive bytes/checksum differ",
    )
    with np.load(path, allow_pickle=False) as data:
        require(
            len(set(data.files)) == len(data.files) and set(data.files) == set(expected["arrays"]),
            "archive array coverage differs",
        )
        arrays = {name: data[name] for name in data.files}
    for name, value in arrays.items():
        require(
            value.dtype in (np.dtype("int64"), np.dtype("float64"), np.dtype("complex128"))
            and np.isfinite(value).all()
            and same(chart.array_metadata(value), expected["arrays"][name]),
            "array metadata or values differ",
        )
        value.setflags(write=False)
    return arrays


def comparison(primary, worker):
    require(
        primary.dtype == worker.dtype == np.dtype("float64")
        and primary.shape == worker.shape == (selection.TUPLE_COUNT,)
        and np.isfinite(primary).all()
        and np.isfinite(worker).all()
        and (primary >= 0).all()
        and (worker >= 0).all(),
        "full finite scores required",
    )
    error = np.abs(primary - worker)
    index = int(np.argmax(error))
    return {
        "columns_compared": len(error),
        "maximum_absolute_difference": float(error[index]),
        "maximum_difference_ordinal": index,
        "passed": bool(np.all(error <= 1e-13)),
    }


def validate_resources(samples, final_stage="after_saved_readback"):
    require(
        isinstance(samples, list)
        and len(samples) >= 2
        and samples[0]["stage"] == "process_start"
        and samples[-1]["stage"] == final_stage,
        "complete resource start/end required",
    )
    require(
        samples[0]["available_physical_bytes"] >= 4 * resources.GIB
        and samples[0]["free_disk_bytes"] >= 6 * resources.GIB,
        "start resources failed",
    )
    previous = {"wall_seconds": -1.0, "peak_working_set_bytes": 0, "peak_private_commit_bytes": 0}
    for sample in samples:
        numeric = [key for key in sample if key.endswith("bytes")]
        require(
            all(type(sample[key]) is int and sample[key] >= 0 for key in numeric),
            "invalid measured byte count",
        )
        require(
            0 < sample["working_set_bytes"] <= sample["peak_working_set_bytes"]
            and 0 < sample["private_commit_bytes"] <= sample["peak_private_commit_bytes"]
            and 0 <= sample["available_physical_bytes"] <= sample["total_physical_bytes"],
            "OS counter semantics differ",
        )
        checks = resources.limit_checks(sample, sample["wall_seconds"], sample["new_file_bytes"])
        require(
            same(sample["checks"], checks)
            and all(checks.values())
            and all(sample[key] >= previous[key] for key in previous),
            "resource checks or sequence differ",
        )
        previous = {key: sample[key] for key in previous}


def read_record(output, size, route):
    record_path, array_path = paths(output, size, route)
    require(
        not record_path.with_name(record_path.stem + "_failure.json").exists(),
        "grid failure marker exists",
    )
    row = common.read_json(record_path)
    common.unseal(row)
    expected = {
        "schema",
        "scope",
        "size",
        "route",
        "source",
        "source_commit",
        "parent",
        "process_id",
        "archive",
        "bins",
        "checks",
        "resources",
        "sha256",
    }
    require(
        set(row) == expected
        and row["schema"] == "Q012h2 S0 grid v1"
        and row["scope"] == BOUNDARY
        and row["size"] == size
        and row["route"] == route,
        "grid record identity differs",
    )
    require(type(row["process_id"]) is int and row["process_id"] > 0, "invalid process id")
    require(
        same(row["source"], metadata()) and same(row["parent"], parent_state()), "grid seals differ"
    )
    oracle.verify_source_commit(row["source_commit"], row["source"])
    validate_resources(row["resources"])
    arrays = load_arrays(array_path, row["archive"])
    require(
        set(arrays)
        == ((selection.SPECTRAL_KEYS | {"distances"}) if route == "primary" else {"distances"}),
        "registered route array coverage differs",
    )
    require(row["resources"][-1]["stage"] == "after_saved_readback", "resource end missing")
    return row, arrays


def progress_callback(guard, route, size):
    def progress(count):
        if count % (16 * selection.CHUNK_SIZE) == 0 or count == selection.TUPLE_COUNT:
            guard.sample(f"{route}_distance_{count}")
            print(f"n{size} {route}: {count}/{selection.TUPLE_COUNT}", file=sys.stderr, flush=True)

    return progress


def execute_grid(output, size, route):
    record_path, array_path = paths(output, size, route)
    require(
        not record_path.exists() and not array_path.exists(), "existing grid or partial archive"
    )
    guard = resources.Guard(output)
    try:
        return _execute_grid(output, size, route, guard)
    except Exception as error:
        if not hasattr(error, "resource_records"):
            error.resource_records = list(guard.records)
        raise


def _execute_grid(output, size, route, guard):
    record_path, array_path = paths(output, size, route)
    source, parent = metadata(), parent_state()
    commit = oracle.git_bytes("rev-parse", "HEAD").decode().strip()
    oracle.verify_source_commit(commit, source)
    guard.sample("after_source_and_parent")
    if route == "primary":
        arrays, audit = selection.spectral_inputs(size)
        guard.sample("after_all_spectral_inputs")
        distances = selection.scan(arrays, progress_callback(guard, route, size))
        archived = save_arrays(array_path, {**arrays, "distances": distances})
        bins = selection.bin_summary(distances)
        checks = {
            "spectral": audit,
            "independent_population_symbol": reference.direct_input_audit(arrays, size),
        }
        require(
            checks["independent_population_symbol"]["passed"], "independent symbol audit failed"
        )
        arrays = {**arrays, "distances": distances}
    else:
        primary, arrays = read_record(output, size, "primary")
        scores = arrays.pop("distances")
        selection.validate_spectra(arrays)
        guard.sample("after_all_primary_input_readback")
        direct = reference.direct_input_audit(arrays, size)
        require(direct["passed"], "worker population-symbol audit failed")
        distances = reference.scan(arrays, progress_callback(guard, route, size))
        archived = save_arrays(array_path, {"distances": distances})
        bins = reference.bin_summary(scores)
        require(same(bins, primary["bins"]), "independent full-bin audit differs")
        compared = comparison(scores, distances)
        require(compared["passed"], "independent full-distance audit failed")
        checks = {
            "primary_archive_sha256": primary["archive"]["sha256"],
            "independent_population_symbol": direct,
            "comparison": compared,
            "independent_own_score_bins": reference.bin_summary(distances),
        }
        arrays = {"distances": distances}
    guard.sample("after_full_scan_and_reduction")
    reread = load_arrays(array_path, archived)
    require(all(np.array_equal(arrays[k], reread[k]) for k in arrays), "saved arrays differ")
    guard.sample("after_saved_readback")
    require(
        same(source, metadata()) and same(parent, parent_state()), "grid source or parent changed"
    )
    row = common.sealed(
        {
            "schema": "Q012h2 S0 grid v1",
            "scope": BOUNDARY,
            "size": size,
            "route": route,
            "source": source,
            "source_commit": commit,
            "parent": parent,
            "process_id": os.getpid(),
            "archive": archived,
            "bins": bins,
            "checks": checks,
            "resources": guard.records,
        }
    )
    common.save_exclusive(record_path, row)
    guard.sample("after_grid_record_readback")
    return {
        "process_id": os.getpid(),
        "filename": record_path.name,
        "sha256": storage.file_sha(record_path),
        "completion_resources": guard.records[-1],
    }


def audit_grid(output, size):
    guard = resources.Guard(output)
    primary, arrays = read_record(output, size, "primary")
    worker, other = read_record(output, size, "worker")
    require(primary["process_id"] != worker["process_id"], "same primary and worker process")
    scores = arrays.pop("distances")
    fresh, frame_audit = selection.spectral_inputs(size)
    require(
        all(np.array_equal(arrays[k], fresh[k]) for k in fresh),
        "fresh spectral matrix entries differ",
    )
    direct = reference.direct_input_audit(fresh, size)
    require(direct["passed"], "fresh population-symbol audit failed")
    require(
        same(primary["checks"], {"spectral": frame_audit, "independent_population_symbol": direct}),
        "primary spectral diagnostics differ",
    )
    del fresh
    guard.sample("after_full_input_rebuild")
    rebuilt = selection.scan(arrays, progress_callback(guard, "audit_primary", size))
    require(np.array_equal(scores, rebuilt), "saved primary distances differ from full rebuild")
    primary_bins = selection.bin_summary(rebuilt)
    del rebuilt
    require(
        same(primary["bins"], primary_bins) and same(worker["bins"], reference.bin_summary(scores)),
        "saved bins differ from full rebuild",
    )
    rebuilt_worker = reference.scan(arrays, progress_callback(guard, "audit_worker", size))
    require(
        np.array_equal(other["distances"], rebuilt_worker),
        "saved worker distances differ from full rebuild",
    )
    compared = comparison(scores, rebuilt_worker)
    require(compared["passed"], "fresh full-distance comparison failed")
    expected_checks = {
        "primary_archive_sha256": primary["archive"]["sha256"],
        "independent_population_symbol": direct,
        "comparison": compared,
        "independent_own_score_bins": reference.bin_summary(rebuilt_worker),
    }
    require(same(worker["checks"], expected_checks), "worker checks differ from fresh computation")
    for route, original in (("primary", primary), ("worker", worker)):
        record_path, array_path = paths(output, size, route)
        require(
            same(common.read_json(record_path), original)
            and storage.file_sha(array_path) == original["archive"]["sha256"],
            "saved inputs changed during full readback audit",
        )
    guard.sample("after_saved_readback")
    records = {r: storage.file_sha(paths(output, size, r)[0]) for r in ("primary", "worker")}
    return {
        "size": size,
        "passed": True,
        "comparison": compared,
        "bins": primary_bins,
        "record_sha256": records,
        "process_id": os.getpid(),
        "resources": guard.records,
    }


def call_child(output, size, route=None):
    args = [
        sys.executable,
        "-u",
        "-W",
        "error",
        "-m",
        MODULE,
        "--output",
        str(output),
        "--size",
        str(size),
    ]
    args.extend(("--route", route) if route else ("--audit-grid",))
    # stderr is inherited so progress remains visible; stdout contains one receipt.
    process = subprocess.Popen(args, cwd=ROOT, stdout=subprocess.PIPE, text=True)
    stdout, _ = process.communicate()
    require(process.returncode == 0, f"child {process.pid} exited {process.returncode}")
    receipt = json.loads(stdout)
    require(
        type(receipt) is dict and receipt["process_id"] == process.pid, "child receipt PID mismatch"
    )
    return {"process_id": process.pid, "exit_code": process.returncode, "receipt": receipt}


def validate_execution(output, execution):
    require(
        isinstance(execution, list) and len(execution) == 6,
        "six actual grid process receipts required",
    )
    for item, (size, route) in zip(
        execution, product(selection.SIZES, ("primary", "worker")), strict=True
    ):
        path, _ = paths(output, size, route)
        row = common.read_json(path)
        expected = {
            "process_id": row["process_id"],
            "filename": path.name,
            "sha256": storage.file_sha(path),
            "completion_resources": item["receipt"]["completion_resources"],
        }
        require(
            set(item) == {"process_id", "exit_code", "receipt"}
            and type(item["exit_code"]) is int
            and item["exit_code"] == 0
            and item["process_id"] == row["process_id"]
            and same(item["receipt"], expected),
            "execution receipt differs from actual grid record",
        )
        common.unseal(row)
        validate_resources(
            row["resources"] + [item["receipt"]["completion_resources"]],
            "after_grid_record_readback",
        )


def build_selection(audits):
    require(
        len(audits) == 3
        and [row["size"] for row in audits] == list(selection.SIZES)
        and all(row["passed"] is True for row in audits),
        "three fully audited grids required",
    )
    selected = selection.select_groups({row["size"]: row["bins"] for row in audits})
    require(max(row["operator_dimension"] for row in selected) == 432, "maximum operator omitted")
    return {
        "groups_per_grid": len(selected),
        "columns_per_grid": sum(row["columns"] for row in selected),
        "groups": selected,
    }


def execute(output):
    require(
        not any(output.parent.glob(output.stem + "*")),
        "existing output/partial run; choose a new path",
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    source, parent = metadata(), parent_state(full=True)
    commit = oracle.git_bytes("rev-parse", "HEAD").decode().strip()
    oracle.verify_source_commit(commit, source)
    controls = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-W", "error", *CONTROL_TESTS],
        check=False,
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(controls.returncode == 0, "S0 controls failed: " + controls.stdout + controls.stderr)
    execution = []
    for size in selection.SIZES:
        for route in ("primary", "worker"):
            execution.append(call_child(output, size, route))
    audits = [call_child(output, size) for size in selection.SIZES]
    selected = build_selection([item["receipt"] for item in audits])
    validate_execution(output, execution)
    require(
        same(parent, parent_state(full=True)) and same(source, metadata()),
        "final source/parent mismatch",
    )
    result = common.sealed(
        {
            "schema": "Q012h2 S0 selection v1",
            "scope": BOUNDARY,
            "source": source,
            "source_commit": commit,
            "parent": parent,
            "controls": {
                "exit_code": controls.returncode,
                "stdout": controls.stdout,
                "stderr": controls.stderr,
            },
            "execution": execution,
            "audits": audits,
            "selection": selected,
            "decision": {
                "stage": "S0_selection_only",
                "passed": True,
                "q012h2_outcome": "not_evaluated",
            },
        }
    )
    common.save_exclusive(output, result)
    return result["decision"]


def audit_manifest(output):
    require(
        not output.with_name(output.stem + "_failure.json").exists(),
        "incomplete execution marker exists",
    )
    row = common.read_json(output)
    common.unseal(row)
    require(
        set(row)
        == {
            "schema",
            "scope",
            "source",
            "source_commit",
            "parent",
            "controls",
            "execution",
            "audits",
            "selection",
            "decision",
            "sha256",
        }
        and row["schema"] == "Q012h2 S0 selection v1"
        and row["scope"] == BOUNDARY,
        "selection manifest identity differs",
    )
    require(
        same(row["source"], metadata()) and same(row["parent"], parent_state(full=True)),
        "manifest seals differ",
    )
    oracle.verify_source_commit(row["source_commit"], row["source"])
    require(
        row["controls"]["exit_code"] == 0
        and re.search(r"\b\d+ passed\b", row["controls"]["stdout"]),
        "successful control tests missing",
    )
    validate_execution(output, row["execution"])
    require(len(row["audits"]) == 3, "audit receipts missing")
    fresh = []
    for size, saved in zip(selection.SIZES, row["audits"], strict=True):
        require(
            saved["exit_code"] == 0 and saved["receipt"]["process_id"] == saved["process_id"],
            "audit process receipt inconsistent",
        )
        validate_resources(saved["receipt"]["resources"])
        value = call_child(output, size)["receipt"]
        for key in ("size", "passed", "comparison", "bins", "record_sha256"):
            require(same(saved["receipt"][key], value[key]), "saved audit scientific fields differ")
        fresh.append(value)
    require(same(row["selection"], build_selection(fresh)), "saved pilot selection differs")
    decision = {"stage": "S0_selection_only", "passed": True, "q012h2_outcome": "not_evaluated"}
    require(same(row["decision"], decision), "S0-only decision was changed")
    require(same(row["source"], metadata()), "source changed during full audit")
    return decision


def record_failure(output, error, size=None, route=None):
    root = paths(output, size, route)[0] if route else output
    failure = root.with_name(root.stem + "_failure.json")
    if failure.exists() or (not route and output.exists()):
        return
    partial = getattr(error, "partial_distances", None)
    retained = None
    if isinstance(partial, np.ndarray) and partial.size:
        path = root.with_name(root.stem + "_partial.npy")
        with path.open("xb") as stream:
            np.save(stream, partial, allow_pickle=False)
        retained = {
            "filename": path.name,
            "completed_prefix_tuples": len(partial),
            "sha256": storage.file_sha(path),
            "array": chart.array_metadata(partial),
        }
    common.save_exclusive(
        failure,
        common.sealed(
            {
                "schema": "Q012h2 S0 incomplete v1",
                "process_id": os.getpid(),
                "size": size,
                "route": route,
                "error": f"{type(error).__name__}: {error}",
                "resource_records": getattr(error, "resource_records", []),
                "partial": retained,
                "decision": {
                    "stage": "S0_selection_only",
                    "passed": False,
                    "q012h2_outcome": "inconclusive",
                },
            }
        ),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--size", type=int, choices=selection.SIZES)
    parser.add_argument("--route", choices=("primary", "worker"))
    parser.add_argument("--audit-grid", action="store_true")
    parser.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    require(output.suffix == ".json", "JSON output path required")
    require(
        not (args.audit_only and (args.size or args.route or args.audit_grid)),
        "incompatible audit modes",
    )
    require(not (args.route and args.audit_grid), "incompatible grid modes")
    require((args.size is not None) == bool(args.route or args.audit_grid), "grid mode needs size")
    if not (args.route or args.audit_grid or args.audit_only):
        require(not any(output.parent.glob(output.stem + "*")), "existing output/partial run")
    try:
        if args.route:
            result = execute_grid(output, args.size, args.route)
        elif args.audit_grid:
            result = audit_grid(output, args.size)
        elif args.audit_only:
            result = audit_manifest(output)
        else:
            result = execute(output)
        print(json.dumps(result, allow_nan=False), flush=True)
    except Exception as error:
        if not (args.audit_grid or args.audit_only):
            record_failure(output, error, args.size, args.route)
        raise


if __name__ == "__main__":
    main()
