"""Q012h0: full structural census with independent processes and readback.

Only integer combinatorics, fresh spectral frames, and array payloads are
evaluated. No quartic forcing/operator solve, RSS forecast, or TT claim.
All output files are exclusive; a prior partial run is never overwritten.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
from datetime import UTC, datetime
from hashlib import sha256
from itertools import product
from pathlib import Path
from time import perf_counter

from research import d3q27_chart as chart
from research import d3q27_quartic_census as census
from research import q012g3_d3q27_cubic_defect as prior

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "research/artifacts/q012g3_d3q27_cubic_defect.json"
PARENT_SHA = "40d5bbbee9a3a6c4c4330062a1eada7422567e478f2ae06b2c9851e409423a91"
PRIOR_SOURCE_SHA = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"
DEFAULT_OUTPUT = PARENT.with_name("q012h0_d3q27_quartic_census.json")
MODULE = "research.q012h0_d3q27_quartic_census"
SIZES = (17, 33, 65)
DEGREES = (2, 3, 4)
CONTROL_TEST = "tests/test_d3q27_quartic_census.py"
SOURCE_FILES = (
    "research/d3q27_quartic_census.py",
    "research/q012h0_d3q27_quartic_census.py",
    CONTROL_TEST,
    "tests/test_q012h0_d3q27_quartic_census.py",
)
BOUNDARY = (
    "Structural census and uncompressed array payload only; no quartic coefficients, "
    "rank, conditioning, solve/RSS feasibility, residual improvement, "
    "SSM existence or TT advantage."
)
ROUTE_FIELDS = {
    "schema",
    "method",
    "scope",
    "config",
    "source",
    "source_after",
    "input",
    "input_after",
    "process_id",
    "created_utc",
    "census_wall_seconds",
    "inventory",
    "frames",
    "degrees",
    "sha256",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return sha256(raw).hexdigest()


def same(left, right):
    """Exact JSON types as well as values: True, 1, and 1.0 are not interchangeable."""
    return digest(left) == digest(right)


def finite(value):
    if isinstance(value, dict):
        return all(finite(v) for v in value.values())
    if isinstance(value, list):
        return all(finite(v) for v in value)
    return math.isfinite(value) if isinstance(value, float) else True


def sealed(document):
    require("sha256" not in document, "document already sealed")
    return {**document, "sha256": digest(document)}


def unseal(document):
    require(isinstance(document, dict) and "sha256" in document, "missing document seal")
    core = {k: v for k, v in document.items() if k != "sha256"}
    require(
        finite(core) and digest(core) == document["sha256"], "document seal or finiteness failed"
    )
    return core


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = value
        return result

    with Path(path).open(encoding="utf-8") as stream:
        value = json.load(stream, object_pairs_hook=unique)
    require(finite(value), "nonfinite JSON data")
    return value


def save_exclusive(path, document):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")
    require(same(read_json(path), document), "serialized content differs")


def config():
    return {
        "sizes": list(SIZES),
        "degrees": list(DEGREES),
        "omega": 1.5,
        "eta": 0.02,
        "power": 2,
        "block_count": 78,
        "coordinate_count": 104,
        "fixed_conservation_leaf": "mass and all three momenta fixed",
        "chunk_columns": 65536,
    }


def metadata():
    previous = prior.source_digest(prior.metadata())
    require(previous == PRIOR_SOURCE_SHA, "prior scientific sources changed")
    return {
        "prior_source_sha256": previous,
        "files": {name: prior._file_sha256(ROOT / name) for name in SOURCE_FILES},
    }


def input_state():
    checksum = prior._file_sha256(PARENT)
    require(checksum == PARENT_SHA, "Q012g3 artifact changed")
    saved = read_json(PARENT)
    require(prior.source_digest(saved) == PRIOR_SOURCE_SHA, "prior artifact source differs")
    require(prior.source_equal(saved, prior.metadata()), "prior artifact/current source mismatch")
    decision = saved["decision"]
    require(
        decision["study_gate"] == "passed" and decision["scientific_outcome"] == "accepted",
        "Q012g3 diagnosis was not accepted",
    )
    require(
        all(v is True for v in decision["validity_gates"].values())
        and all(v is True for v in decision["hypothesis_gates"].values()),
        "prior gate inconsistency",
    )
    return {
        "filename": PARENT.name,
        "sha256": checksum,
        "source_sha256": PRIOR_SOURCE_SHA,
        "decision": decision,
    }


def expected_inventory():
    return census.inventory(
        census.Block(wave, label, dimension)
        for wave in product((-1, 0, 1), repeat=3)
        if any(wave)
        for label, dimension in (("shear", 2), ("acoustic_plus", 1), ("acoustic_minus", 1))
    )


def fresh_frames():
    require(
        (chart.OMEGA, chart.ETA, chart.POWER, chart.DIMENSION) == (1.5, 0.02, 2, 104),
        "registered chart parameters changed",
    )
    expected = expected_inventory()
    rows = []
    for size in SIZES:
        frames, audit = chart.paired_frames(size, 1.5)
        blocks = [
            census.Block(b.wave, b.label, b.basis.shape[1])
            for wave in sorted(frames)
            for b in frames[wave].blocks
        ]
        observed = census.inventory(blocks)
        require(
            same(observed, expected) and audit["passed"] is True and finite(audit),
            "fresh paired frame/inventory failed",
        )
        rows.append({"size": size, "inventory": observed, "audit": audit})
    return rows


def degree_record(blocks, degree, joint, coordinates):
    coverage = census.coverage(joint, blocks, degree)
    grids = []
    for size in SIZES:
        sectors = census.sector_summary(joint, blocks, degree, size)
        payload = census.payload(
            degree,
            sum(b.dimension for b in blocks),
            coverage["coordinate_columns"],
            size,
            sectors["operator_dimension_histogram"],
            config()["chunk_columns"],
        )
        grids.append({"size": size, "sectors": sectors, "payload": payload})
    return {
        "degree": degree,
        "joint": census.joint_records(joint),
        "coordinates": census.coordinate_records(coordinates),
        "coverage": coverage,
        "grids": grids,
        "all_three_grids_sparse_payload_bytes": sum(
            g["payload"]["sparse_payload_bytes"] for g in grids
        ),
    }


def count_degree(blocks, degree, method):
    require(method in ("enumeration", "generating_functions"), "unknown counting method")
    if method == "enumeration":
        joint = census.enumerate_joint(blocks, degree)
        coordinates = census.weighted_coordinates(joint)
    else:
        joint = census.block_generating_function(blocks, degree)
        coordinates = census.coordinate_generating_function(blocks, degree)
    return degree_record(blocks, degree, joint, coordinates)


def build_route(method):
    start = perf_counter()
    source, parent = metadata(), input_state()
    frames = fresh_frames()
    blocks = census.restore_inventory(frames[0]["inventory"])
    records = [count_degree(blocks, d, method) for d in DEGREES]
    after, input_after = metadata(), input_state()
    require(
        same(source, after) and same(parent, input_after), "source or input changed during counting"
    )
    return sealed(
        {
            "schema": "Q012h0 route v1",
            "method": method,
            "scope": BOUNDARY,
            "config": config(),
            "source": source,
            "source_after": after,
            "input": parent,
            "input_after": input_after,
            "process_id": os.getpid(),
            "created_utc": datetime.now(UTC).isoformat(),
            "census_wall_seconds": perf_counter() - start,
            "inventory": census.inventory(blocks),
            "frames": frames,
            "degrees": records,
        }
    )


def audit_route(saved, method):
    unseal(saved)
    require(set(saved) == ROUTE_FIELDS, "route fields differ")
    require(
        saved["schema"] == "Q012h0 route v1" and saved["method"] == method,
        "route schema or method differs",
    )
    require(saved["scope"] == BOUNDARY and same(saved["config"], config()), "scope/config differs")
    require(
        same(saved["source"], saved["source_after"]) and same(saved["source"], metadata()),
        "route source mismatch",
    )
    require(
        same(saved["input"], saved["input_after"]) and same(saved["input"], input_state()),
        "route input mismatch",
    )
    require(census.positive_integer(saved["process_id"]), "invalid route process id")
    require(
        type(saved["census_wall_seconds"]) is float and saved["census_wall_seconds"] > 0,
        "invalid measured census time",
    )
    stamp = datetime.fromisoformat(saved["created_utc"])
    require(
        stamp.utcoffset() is not None and stamp.utcoffset().total_seconds() == 0,
        "route timestamp must be UTC",
    )
    require(same(saved["inventory"], expected_inventory()), "registered inventory incomplete")
    require(same(saved["frames"], fresh_frames()), "fresh frame readback differs")
    blocks = census.restore_inventory(saved["inventory"])
    require(
        same([row["degree"] for row in saved["degrees"]], list(DEGREES)), "degree coverage differs"
    )
    for row in saved["degrees"]:
        joint = census.parse_joint(row["joint"])
        coordinates = census.parse_coordinates(row["coordinates"])
        rebuilt = degree_record(blocks, row["degree"], joint, coordinates)
        require(same(row, rebuilt), "sector/payload/coverage readback differs")
        require(
            same(row, count_degree(blocks, row["degree"], method)), "recomputed histogram differs"
        )
    return {
        "passed": True,
        "degrees": list(DEGREES),
        "sizes": list(SIZES),
        "all_histogram_bins_recomputed": True,
        "fresh_frames_recomputed": True,
    }


def controls():
    before = prior._file_sha256(ROOT / CONTROL_TEST)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-W", "error", CONTROL_TEST],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    matches = re.findall(r"(?:^|\s)(\d+) passed(?:\s|,)", result.stdout)
    count = int(matches[-1]) if matches else None
    after = prior._file_sha256(ROOT / CONTROL_TEST)
    return {
        "filename": CONTROL_TEST,
        "source_before": before,
        "source_after": after,
        "exit_code": result.returncode,
        "passed_tests": count,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def controls_passed(record, source):
    if set(record) != {
        "filename",
        "source_before",
        "source_after",
        "exit_code",
        "passed_tests",
        "stdout",
        "stderr",
    }:
        return False
    matches = re.findall(r"(?:^|\s)(\d+) passed(?:\s|,)", record["stdout"])
    return (
        record["filename"] == CONTROL_TEST
        and type(record["exit_code"]) is int
        and record["exit_code"] == 0
        and type(record["passed_tests"]) is int
        and record["passed_tests"] == 127
        and matches == ["127"]
        and record["stderr"] == ""
        and record["source_before"] == record["source_after"] == source["files"][CONTROL_TEST]
    )


def child_path(output, method):
    suffix = "primary" if method == "enumeration" else "worker"
    return output.with_name(output.stem + "_" + suffix + ".json")


def route_receipt(path, saved):
    return {
        "filename": path.name,
        "sha256": prior._file_sha256(path),
        "process_id": saved["process_id"],
        "method": saved["method"],
    }


def spawn_worker(path):
    argument = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
    process = subprocess.Popen(
        [sys.executable, "-W", "error", "-m", MODULE, "--worker", "--output", argument],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    stdout, stderr = process.communicate()
    return {
        "process_id": process.pid,
        "exit_code": process.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "module": MODULE,
    }


def comparisons(primary, worker):
    require(
        same([r["degree"] for r in primary["degrees"]], list(DEGREES))
        and same([r["degree"] for r in worker["degrees"]], list(DEGREES)),
        "comparison requires every registered degree",
    )
    rows = []
    for a, b in zip(primary["degrees"], worker["degrees"], strict=True):
        weighted = census.coordinate_records(
            census.weighted_coordinates(census.parse_joint(b["joint"]))
        )
        rows.append(
            {
                "degree": a["degree"],
                "joint_histogram_equal": same(a["joint"], b["joint"]),
                "coordinate_histogram_equal": same(a["coordinates"], b["coordinates"])
                and same(b["coordinates"], weighted),
                "grid_summaries_equal": same(a["grids"], b["grids"]),
                "all_three_grids_non_aliasing": all(
                    g["sectors"]["non_aliasing"] for g in a["grids"] + b["grids"]
                ),
            }
        )
    return rows


def decision(primary, worker, control_record, execution, audits):
    compared = comparisons(primary, worker)
    validity = {
        "sealed_sources_and_input": primary["source"] == worker["source"] == metadata()
        and primary["input"] == worker["input"] == input_state(),
        "artificial_controls": controls_passed(control_record, primary["source"]),
        "fresh_frames": all(
            f["audit"]["passed"] for route in (primary, worker) for f in route["frames"]
        ),
        "full_registered_coverage": all(
            r["coverage"]["passed"] for route in (primary, worker) for r in route["degrees"]
        ),
        "finite_evidence": finite(primary) and finite(worker),
        "independent_completed_process": set(execution)
        == {"process_id", "exit_code", "stdout", "stderr", "module"}
        and type(execution["exit_code"]) is int
        and execution["exit_code"] == 0
        and census.positive_integer(execution["process_id"])
        and execution["process_id"] == worker["process_id"] != primary["process_id"]
        and execution["module"] == MODULE
        and execution["stderr"] == "",
        "saved_children_recomputed": set(audits) == {"enumeration", "generating_functions"}
        and all(audit["passed"] is True for audit in audits.values()),
    }
    hypotheses = {
        "H1": all(row["joint_histogram_equal"] for row in compared),
        "H2": all(row["coordinate_histogram_equal"] for row in compared),
        "H3": all(
            row["grid_summaries_equal"] and row["all_three_grids_non_aliasing"] for row in compared
        ),
    }
    valid = all(validity.values())
    return {
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_gate": "passed" if valid else "failed",
        "scientific_outcome": "inconclusive"
        if not valid
        else "accepted"
        if all(hypotheses.values())
        else "rejected",
    }


def summary(primary):
    return [
        {
            "degree": row["degree"],
            "coverage": row["coverage"],
            "grids": [
                {
                    "size": g["size"],
                    "raw_support_count": g["sectors"]["raw_support_count"],
                    "maximum_operator_dimension": g["payload"]["maximum_operator_dimension"],
                    "sparse_payload_bytes": g["payload"]["sparse_payload_bytes"],
                    "physical_ordered_real_W_bytes": g["payload"]["physical_ordered_real_W_bytes"],
                    "physical_symmetric_real_W_bytes": g["payload"][
                        "physical_symmetric_real_W_bytes"
                    ],
                    "full_solver_resource_feasibility": None,
                }
                for g in row["grids"]
            ],
            "all_three_grids_sparse_payload_bytes": row["all_three_grids_sparse_payload_bytes"],
        }
        for row in primary["degrees"]
    ]


def manifest(output, primary, worker, control_record, execution, audits):
    return sealed(
        {
            "schema": "Q012h0 manifest v1",
            "scope": BOUNDARY,
            "config": config(),
            "source": primary["source"],
            "source_after": metadata(),
            "input": primary["input"],
            "input_after": input_state(),
            "process_id": primary["process_id"],
            "controls": control_record,
            "worker_execution": execution,
            "children": {
                method: route_receipt(child_path(output, method), doc)
                for method, doc in (("enumeration", primary), ("generating_functions", worker))
            },
            "readback_audits": audits,
            "comparisons": comparisons(primary, worker),
            "summary": summary(primary),
            "decision": decision(primary, worker, control_record, execution, audits),
        }
    )


def audit_manifest(output):
    output = Path(output).resolve()
    require(
        not output.with_name(output.stem + "_failure.json").exists(),
        "execution failure marker exists",
    )
    saved = read_json(output)
    unseal(saved)
    require(saved["schema"] == "Q012h0 manifest v1", "not a completed census manifest")
    docs, audits = {}, {}
    for method in ("enumeration", "generating_functions"):
        path = child_path(output, method)
        doc = read_json(path)
        require(
            same(saved["children"][method], route_receipt(path, doc)),
            "child file seal/receipt differs",
        )
        audits[method] = audit_route(doc, method)
        docs[method] = doc
    receipt = json.loads(saved["worker_execution"]["stdout"])
    require(
        same(receipt, saved["children"]["generating_functions"]), "worker stdout receipt differs"
    )
    expected = manifest(
        output,
        docs["enumeration"],
        docs["generating_functions"],
        saved["controls"],
        saved["worker_execution"],
        audits,
    )
    require(same(saved, expected), "manifest content or derived decision differs")
    return saved["decision"]


def execute(output):
    output = Path(output).resolve()
    require(output.suffix == ".json", "output must end in .json")
    paths = (output, child_path(output, "enumeration"), child_path(output, "generating_functions"))
    failure_path = output.with_name(output.stem + "_failure.json")
    require(
        not any(path.exists() for path in (*paths, failure_path)),
        "existing output or partial run; choose a new path",
    )
    stage = "input/source preflight"
    control_record, execution = None, None
    try:
        source_before, input_before = metadata(), input_state()
        stage = "artificial controls"
        control_record = controls()
        require(controls_passed(control_record, source_before), "artificial controls failed")
        stage = "independent worker"
        execution = spawn_worker(paths[2])
        require(
            execution["exit_code"] == 0, "worker did not exit successfully: " + execution["stderr"]
        )
        worker = read_json(paths[2])
        require(
            same(json.loads(execution["stdout"]), route_receipt(paths[2], worker)),
            "worker receipt differs",
        )
        require(
            execution["process_id"] == worker["process_id"] != os.getpid(),
            "worker process not independent",
        )
        worker_audit = audit_route(worker, "generating_functions")
        stage = "primary enumeration"
        primary = build_route("enumeration")
        save_exclusive(paths[1], primary)
        primary = read_json(paths[1])
        primary_audit = audit_route(primary, "enumeration")
        require(
            same(metadata(), source_before) and same(input_state(), input_before),
            "run seals changed",
        )
        stage = "manifest and final readback"
        result = manifest(
            output,
            primary,
            worker,
            control_record,
            execution,
            {"enumeration": primary_audit, "generating_functions": worker_audit},
        )
        save_exclusive(output, result)
        require(audit_manifest(output) == result["decision"], "final readback decision differs")
        return result
    except Exception as error:
        failure = sealed(
            {
                "schema": "Q012h0 incomplete execution v1",
                "scope": BOUNDARY,
                "stage": stage,
                "error": f"{type(error).__name__}: {error}",
                "process_id": os.getpid(),
                "config": config(),
                "controls": control_record,
                "worker_execution": execution,
                "decision": {"study_gate": "failed", "scientific_outcome": "inconclusive"},
            }
        )
        # A final-readback failure must not leave its positive manifest unqualified.
        save_exclusive(failure_path, failure)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--worker", action="store_true")
    group.add_argument("--audit-only", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if args.worker:
        require(not output.exists(), "worker output already exists")
        result = build_route("generating_functions")
        save_exclusive(output, result)
        audit_route(read_json(output), "generating_functions")
        print(json.dumps(route_receipt(output, result)), flush=True)
    elif args.audit_only:
        result = audit_manifest(output)
        print(json.dumps(result), flush=True)
        if result["study_gate"] != "passed":
            raise SystemExit(1)
    else:
        result = execute(output)
        print(
            json.dumps(
                {
                    "output": output.name,
                    "sha256": prior._file_sha256(output),
                    "decision": result["decision"],
                }
            ),
            flush=True,
        )
        if result["decision"]["study_gate"] != "passed":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
