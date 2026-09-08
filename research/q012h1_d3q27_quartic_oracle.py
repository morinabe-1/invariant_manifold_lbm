"""Registered Q012h1 full oracle: exclusive archives and actual worker receipts.

No real-LBM quartic solve or SSM/TT claim. A partial archive is never resumed,
overwritten, or accepted. Audits rebuild every scientific entry from sources.
"""

import argparse
import json
import os
import platform
import re
import subprocess
import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

import gmpy2
import numpy as np
import scipy

from research import d3q27_quartic_archive as storage
from research import d3q27_quartic_records as records
from research import d3q27_quartic_solve as solve
from research import q012h0_d3q27_quartic_census as census

ROOT = Path(__file__).resolve().parents[1]
MODULE = "research.q012h1_d3q27_quartic_oracle"
PARENT = ROOT / "research/artifacts/q012h0_d3q27_quartic_census.json"
PARENT_SHA = "4c7c20a6dbde1aa8c9e7317a7b7750c000d81e429759af51ddfebc836064a0d8"
DEFAULT_OUTPUT = PARENT.with_name("q012h1_d3q27_quartic_oracle.json")
PREREG_COMMIT = "a345ec7d61d956b701c941606f7d175f3ca42c9e"
PREREG_PATH = "docs/D3Q27_QUARTIC_ORACLE.md"
CONTROL_TESTS = tuple(
    "tests/test_d3q27_quartic_" + name + ".py" for name in ("operator", "jets", "fraction", "solve")
)
SOURCE_FILES = tuple(
    "research/d3q27_quartic_" + name + ".py"
    for name in ("operator", "reference", "jets", "fraction", "solve", "records", "archive")
) + (
    "research/q012h1_d3q27_quartic_oracle.py",
    *CONTROL_TESTS,
    "tests/test_d3q27_quartic_records.py",
    "tests/test_d3q27_quartic_archive.py",
    "tests/test_q012h1_d3q27_quartic_oracle.py",
)
BOUNDARY = (
    "Artificial quartic operator/forcing/known-solution oracle only; "
    "no real-LBM quartic chart, finite-amplitude improvement, SSM existence or TT advantage."
)
require, same = census.require, census.same


def configuration():
    return {
        "operator_cases": 1120,
        "symmetric_columns": 4482,
        "forcing_cases": 4,
        "forcing_columns": 1320,
        "operator_inventory": [[list(d), list(g), p] for d, g, p in records.OPERATOR_CASES],
        "forcing_inventory": [list(c) for c in records.FORCING_CASES],
        "fixed_conservation_leaf": "mass and three momenta fixed; four artificial coordinates zero",
        "later_real_lbm": {"sizes": [17, 33, 65], "blocks": 78, "coordinates": 104},
    }


def normalized_sha(content):
    return sha256(content.replace(b"\r\n", b"\n")).hexdigest()


def git_bytes(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def metadata():
    prereg = git_bytes("show", f"{PREREG_COMMIT}:{PREREG_PATH}").replace(b"\r\n", b"\n")
    require(
        (ROOT / PREREG_PATH).read_bytes().replace(b"\r\n", b"\n").startswith(prereg),
        "preregistration was changed instead of appending a dated result",
    )
    return {
        "files": {name: normalized_sha((ROOT / name).read_bytes()) for name in SOURCE_FILES},
        "prior_source": census.metadata(),
        "preregistration_sha256": normalized_sha(prereg),
        "runtime": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "gmpy2": gmpy2.version(),
        },
    }


def verify_source_commit(commit, source):
    require(type(commit) is str and re.fullmatch(r"[0-9a-f]{40}", commit), "invalid source commit")
    for name, checksum in source["files"].items():
        require(
            normalized_sha(git_bytes("show", f"{commit}:{name}")) == checksum,
            "scientific source differs from its recorded commit",
        )


def parent_audit():
    require(census.prior._file_sha256(PARENT) == PARENT_SHA, "Q012h0 parent changed")
    decision = census.audit_manifest(PARENT)
    require(
        decision["study_gate"] == "passed" and decision["scientific_outcome"] == "accepted",
        "full Q012h0 parent audit did not pass",
    )
    return {"filename": PARENT.name, "sha256": PARENT_SHA, "decision": decision}


def child_path(output, route):
    require(route in ("primary", "worker"), "registered route required")
    return Path(output).with_name(Path(output).stem + "_" + route + ".zip")


def names(route):
    require(route in ("primary", "worker"), "registered route required")
    result = ["header.json", "footer.json", "negatives.json"]
    for ordinal in range(len(records.OPERATOR_CASES)):
        result.append(f"operator/{ordinal:04d}.json")
        if route == "primary":
            result.append(f"operator/{ordinal:04d}.npz")
    result.extend(f"forcing/{p}_{r}.json" for p, r in records.FORCING_CASES)
    return tuple(result)


def header(route, source, parent, primary=None):
    commit = git_bytes("rev-parse", "HEAD").decode().strip()
    verify_source_commit(commit, source)
    return {
        "schema": "Q012h1 archive v1",
        "route": route,
        "scope": BOUNDARY,
        "configuration": configuration(),
        "source": source,
        "source_commit": commit,
        "parent": parent,
        "process_id": os.getpid(),
        "created_utc": datetime.now(UTC).isoformat(),
        "primary_sha256": storage.file_sha(primary) if primary is not None else None,
    }


def build_primary(path, source, parent):
    with storage.Archive(path, "x", names("primary")) as archive:
        archive.put_document("header.json", header("primary", source, parent))
        for ordinal, case in enumerate(records.OPERATOR_CASES):
            record, arrays = records.main_operator(case)
            archive.put_document(f"operator/{ordinal:04d}.json", record)
            archive.put_arrays(f"operator/{ordinal:04d}.npz", arrays)
            if (ordinal + 1) % 70 == 0:
                print(
                    json.dumps({"stage": "primary operators", "completed": ordinal + 1}), flush=True
                )
        for case in records.FORCING_CASES:
            archive.put_document(f"forcing/{case[0]}_{case[1]}.json", records.main_forcing(case))
        archive.put_document("negatives.json", solve.negative_controls())
        archive.put_document(
            "footer.json", {"source": metadata(), "parent": parent_audit(), "primary_sha256": None}
        )


def build_worker(path, primary):
    source, parent = metadata(), parent_audit()
    with storage.Archive(primary, "r", names("primary")) as main:
        check_header(main, "primary", source, parent)
        with storage.Archive(path, "x", names("worker")) as archive:
            archive.put_document("header.json", header("worker", source, parent, primary))
            for ordinal, case in enumerate(records.OPERATOR_CASES):
                arrays = main.arrays(f"operator/{ordinal:04d}.npz")
                archive.put_document(
                    f"operator/{ordinal:04d}.json", records.reference_operator(case, arrays)
                )
            for case in records.FORCING_CASES:
                archive.put_document(
                    f"forcing/{case[0]}_{case[1]}.json", records.reference_forcing(case)
                )
            archive.put_document("negatives.json", {"cases": records.reference_negatives()})
            archive.put_document(
                "footer.json",
                {
                    "source": metadata(),
                    "parent": parent_audit(),
                    "primary_sha256": storage.file_sha(primary),
                },
            )


def check_header(archive, route, source, parent, primary_sha=None):
    start, end = archive.document("header.json"), archive.document("footer.json")
    require(
        set(start)
        == {
            "schema",
            "route",
            "scope",
            "configuration",
            "source",
            "source_commit",
            "parent",
            "process_id",
            "created_utc",
            "primary_sha256",
        },
        "header schema",
    )
    require(
        start["schema"] == "Q012h1 archive v1"
        and start["route"] == route
        and start["scope"] == BOUNDARY,
        "archive kind/scope mismatch",
    )
    require(
        same(start["configuration"], configuration())
        and same(start["source"], source)
        and same(start["parent"], parent),
        "archive configuration/source/parent mismatch",
    )
    require(type(start["process_id"]) is int and start["process_id"] > 0, "invalid process ID")
    require(
        datetime.fromisoformat(start["created_utc"]).utcoffset().total_seconds() == 0,
        "UTC creation timestamp required",
    )
    require(
        start["primary_sha256"] == primary_sha
        and same(end, {"source": source, "parent": parent, "primary_sha256": primary_sha}),
        "archive seals changed",
    )
    verify_source_commit(start["source_commit"], source)
    return start


def receipt(path, start):
    return {
        "filename": Path(path).name,
        "sha256": storage.file_sha(path),
        "bytes": Path(path).stat().st_size,
        "process_id": start["process_id"],
        "route": start["route"],
    }


def audit_children(output):
    """Rebuild every record and array, then recompute every cross-route comparison."""
    source, parent = metadata(), parent_audit()
    primary, worker = (child_path(output, route) for route in ("primary", "worker"))
    archive_seals = {path: storage.file_sha(path) for path in (primary, worker)}
    operator_comparisons, forcing_comparisons = [], []
    with storage.Archive(primary, "r", names("primary")) as main:
        with storage.Archive(worker, "r", names("worker")) as reference:
            primary_header = check_header(main, "primary", source, parent)
            worker_header = check_header(
                reference, "worker", source, parent, archive_seals[primary]
            )
            for ordinal, case in enumerate(records.OPERATOR_CASES):
                name = f"operator/{ordinal:04d}"
                row, arrays = main.document(name + ".json"), main.arrays(name + ".npz")
                fresh, fresh_arrays = records.main_operator(case)
                require(
                    same(row, fresh) and storage.arrays_equal(arrays, fresh_arrays),
                    f"primary full-entry reconstruction differs at operator {ordinal}",
                )
                other = reference.document(name + ".json")
                require(
                    same(other, records.reference_operator(case, arrays)),
                    f"reference full-entry reconstruction differs at operator {ordinal}",
                )
                operator_comparisons.append(records.compare_operator(row, arrays, other))
            for p, representation in records.FORCING_CASES:
                name = f"forcing/{p}_{representation}.json"
                row, other = main.document(name), reference.document(name)
                require(
                    same(row, records.main_forcing((p, representation))), "main forcing differs"
                )
                require(
                    same(other, records.reference_forcing((p, representation))),
                    "reference forcing differs",
                )
                forcing_comparisons.append(records.compare_forcing(row, other))
            negative, other_negative = (
                main.document("negatives.json"),
                reference.document("negatives.json"),
            )
            require(same(negative, solve.negative_controls()), "main negative controls differ")
            require(
                same(other_negative, {"cases": records.reference_negatives()}),
                "reference negatives differ",
            )
            expected = [
                "singular_compatible",
                "singular_incompatible",
                "nonsingular_ill_conditioned",
            ]
            negative_passed = (
                negative["passed"]
                and [r["observed"]["status"] for r in negative["cases"]] == expected
                and [r["status"] for r in other_negative["cases"]] == expected
                and all(not r["observed"]["passed"] for r in negative["cases"])
            )
    require(same(source, metadata()) and same(parent, parent_audit()), "audit seals changed")
    require(
        all(storage.file_sha(path) == checksum for path, checksum in archive_seals.items()),
        "archive bytes changed during full-entry audit",
    )
    return {
        "source": source,
        "parent": parent,
        "children": {
            "primary": receipt(primary, primary_header),
            "worker": receipt(worker, worker_header),
        },
        "operators": operator_comparisons,
        "forcing": forcing_comparisons,
        "negative_controls_passed": negative_passed,
        "coverage": {
            "operator_cases": len(operator_comparisons),
            "forcing_cases": len(forcing_comparisons),
            "symmetric_columns": sum(
                len(records.reference.substitute(d, g)["keys"])
                for d, g, _ in records.OPERATOR_CASES
            ),
            "forcing_columns": sum(330 for _ in records.FORCING_CASES),
        },
        "full_entries_rebuilt": True,
    }


def controls():
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-W", "error", *CONTROL_TESTS],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "tests": list(CONTROL_TESTS),
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def controls_passed(control):
    return (
        set(control) == {"tests", "exit_code", "stdout", "stderr"}
        and same(control["tests"], list(CONTROL_TESTS))
        and type(control["exit_code"]) is int
        and control["exit_code"] == 0
        and re.findall(r"(?:^|\s)(\d+) passed(?:\s|,)", control["stdout"]) == ["118"]
        and len(
            re.findall(r"(?m)^118 passed in \d+(?:\.\d+)?s(?: \([0-9:]+\))?\s*$", control["stdout"])
        )
        == 1
        and control["stderr"] == ""
    )


def spawn_worker(output):
    process = subprocess.Popen(
        [sys.executable, "-W", "error", "-m", MODULE, "--worker", "--output", str(output)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    stdout, stderr = process.communicate()
    return {
        "process_id": process.pid,
        "exit_code": process.returncode,
        "module": MODULE,
        "stdout": stdout,
        "stderr": stderr,
    }


def decision(audit, control, execution):
    children = audit["children"]
    completed = (
        set(execution) == {"process_id", "exit_code", "module", "stdout", "stderr"}
        and type(execution["exit_code"]) is int
        and execution["exit_code"] == 0
        and type(execution["process_id"]) is int
        and execution["process_id"]
        == children["worker"]["process_id"]
        != children["primary"]["process_id"]
        and execution["process_id"] > 0
        and execution["module"] == MODULE
        and execution["stderr"] == ""
    )
    try:
        completed &= same(json.loads(execution["stdout"]), children["worker"])
    except (ValueError, TypeError):
        completed = False
    validity = {
        "sealed_sources_and_parent": same(audit["source"], metadata()),
        "artificial_controls": controls_passed(control),
        "full_registered_coverage": len(audit["operators"]) == 1120
        and len(audit["forcing"]) == 4
        and same(
            audit["coverage"],
            {
                "operator_cases": 1120,
                "forcing_cases": 4,
                "symmetric_columns": 4482,
                "forcing_columns": 1320,
            },
        ),
        "independent_completed_process": completed,
        "full_saved_entries_rebuilt": audit["full_entries_rebuilt"] is True,
        "finite_evidence": census.finite(audit),
        "independent_numerical_witnesses": all(
            r["identity_equal"] and r["independent_witnesses_equal"] for r in audit["operators"]
        ),
        "nonzero_forcing_controls": all(
            r["nonzero_and_mutation_coverage"] for r in audit["forcing"]
        ),
    }
    hypotheses = {
        "H1": all(r["H1"] for r in audit["operators"])
        and any(r["uniform_1_over_24_detected"] for r in audit["operators"]),
        "H2": all(r["H2"] for r in audit["forcing"]),
        "H3": all(r["H3"] for r in audit["operators"]) and audit["negative_controls_passed"],
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


def manifest(audit, control, execution):
    return census.sealed(
        {
            "schema": "Q012h1 manifest v1",
            "scope": BOUNDARY,
            "configuration": configuration(),
            "audit": audit,
            "controls": control,
            "worker_execution": execution,
            "decision": decision(audit, control, execution),
        }
    )


def audit_manifest(output):
    output = Path(output).resolve()
    require(
        not output.with_name(output.stem + "_failure.json").exists(),
        "execution failure marker exists",
    )
    saved = census.read_json(output)
    census.unseal(saved)
    require(saved["schema"] == "Q012h1 manifest v1", "not a completed Q012h1 manifest")
    audited = audit_children(output)
    expected = manifest(audited, saved["controls"], saved["worker_execution"])
    require(same(saved, expected), "manifest content or derived decision differs")
    return expected["decision"]


def execute(output):
    output = Path(output).resolve()
    require(output.suffix == ".json", "output must be a JSON manifest")
    failure = output.with_name(output.stem + "_failure.json")
    require(
        not any(
            p.exists()
            for p in (output, failure, child_path(output, "primary"), child_path(output, "worker"))
        ),
        "existing output or partial run; choose a new path",
    )
    stage, control, execution = "source and parent preflight", None, None
    try:
        source, parent = metadata(), parent_audit()
        verify_source_commit(git_bytes("rev-parse", "HEAD").decode().strip(), source)
        stage = "artificial controls"
        control = controls()
        require(controls_passed(control), "artificial controls failed")
        output.parent.mkdir(parents=True, exist_ok=True)
        stage = "all primary operators and forcing"
        build_primary(child_path(output, "primary"), source, parent)
        stage = "independent worker"
        execution = spawn_worker(output)
        require(execution["exit_code"] == 0, "independent worker failed: " + execution["stderr"])
        stage = "full-entry saved audit"
        audit = audit_children(output)
        require(same(source, metadata()) and same(parent, audit["parent"]), "run seals changed")
        result = manifest(audit, control, execution)
        census.save_exclusive(output, result)
        # A fresh CLI audit repeats the expensive scientific reconstruction;
        # this immediate check verifies the actual persisted manifest bytes.
        require(same(census.read_json(output), result), "saved manifest differs")
        return result
    except Exception as error:
        census.save_exclusive(
            failure,
            census.sealed(
                {
                    "schema": "Q012h1 incomplete execution v1",
                    "stage": stage,
                    "error": f"{type(error).__name__}: {error}",
                    "controls": control,
                    "worker_execution": execution,
                    "process_id": os.getpid(),
                    "decision": {"study_gate": "failed", "scientific_outcome": "inconclusive"},
                }
            ),
        )
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
        path = child_path(output, "worker")
        build_worker(path, child_path(output, "primary"))
        with storage.Archive(path, "r", names("worker")) as archive:
            print(json.dumps(receipt(path, archive.document("header.json"))), flush=True)
    else:
        result = audit_manifest(output) if args.audit_only else execute(output)["decision"]
        print(json.dumps(result), flush=True)
        if result["study_gate"] != "passed":
            raise SystemExit(1)


if __name__ == "__main__":
    main()
