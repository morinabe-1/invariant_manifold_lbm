"""Q012h1 runner contracts. Synthetic receipts never prove a scientific run."""

import io
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pytest

from research import d3q27_quartic_archive as storage
from research import q012h1_d3q27_quartic_oracle as q


@pytest.fixture
def synthetic(monkeypatch):
    source = {"unit_only": True}
    monkeypatch.setattr(q, "metadata", lambda: source)
    audit = {
        "source": source,
        "parent": {"unit_only": True},
        "children": {
            "primary": {
                "filename": "primary.zip",
                "sha256": "a" * 64,
                "bytes": 42,
                "process_id": 111,
                "route": "primary",
            },
            "worker": {
                "filename": "worker.zip",
                "sha256": "b" * 64,
                "bytes": 43,
                "process_id": 222,
                "route": "worker",
            },
        },
        "operators": [
            {
                "identity_equal": True,
                "independent_witnesses_equal": True,
                "H1": True,
                "H3": True,
                "uniform_1_over_24_detected": True,
            }
            for _ in range(1120)
        ],
        "forcing": [{"nonzero_and_mutation_coverage": True, "H2": True} for _ in range(4)],
        "coverage": {
            "operator_cases": 1120,
            "forcing_cases": 4,
            "symmetric_columns": 4482,
            "forcing_columns": 1320,
        },
        "full_entries_rebuilt": True,
        "negative_controls_passed": True,
    }
    control = {
        "tests": list(q.CONTROL_TESTS),
        "exit_code": 0,
        "stdout": "118 passed in 88.68s (0:01:28)\n",
        "stderr": "",
    }
    execution = {
        "process_id": 222,
        "exit_code": 0,
        "module": q.MODULE,
        "stdout": json.dumps(audit["children"]["worker"]),
        "stderr": "",
    }
    return audit, control, execution


def test_synthetic_complete_receipt_is_only_a_decision_contract(synthetic):
    result = q.decision(*synthetic)
    assert result["study_gate"] == "passed" and result["scientific_outcome"] == "accepted"


@pytest.mark.parametrize(
    "field,value",
    (
        ("exit_code", 1),
        ("exit_code", False),
        ("process_id", 111),
        ("process_id", True),
        ("module", "different.module"),
        ("stderr", "worker error"),
        ("stdout", "{}"),
    ),
)
def test_failed_or_fabricated_execution_is_inconclusive(synthetic, field, value):
    audit, control, execution = synthetic
    execution[field] = value
    result = q.decision(audit, control, execution)
    assert not result["validity_gates"]["independent_completed_process"]
    assert result["scientific_outcome"] == "inconclusive"


@pytest.mark.parametrize("count", (0, 1119))
def test_truncated_rows_cannot_hide_behind_full_summary_counts(synthetic, count):
    audit, control, execution = synthetic
    audit["operators"] = audit["operators"][:count]
    result = q.decision(audit, control, execution)
    assert not result["validity_gates"]["full_registered_coverage"]
    assert result["scientific_outcome"] == "inconclusive"


@pytest.mark.parametrize("change", ("forcing", "columns", "rebuild", "nonfinite", "source"))
def test_missing_coverage_forged_flags_and_source_drift_are_not_accepted(synthetic, change):
    audit, control, execution = synthetic
    if change == "forcing":
        audit["forcing"].pop()
    elif change == "columns":
        audit["coverage"]["symmetric_columns"] -= 1
    elif change == "rebuild":
        audit["full_entries_rebuilt"] = 1
    elif change == "nonfinite":
        audit["bad_number"] = np.nan
    else:
        audit["source"] = {"modified": True}
    assert q.decision(audit, control, execution)["scientific_outcome"] == "inconclusive"


@pytest.mark.parametrize("hypothesis", ("H1", "H2", "H3"))
def test_scientific_failure_remains_rejected_not_deleted_or_rescued(synthetic, hypothesis):
    audit, control, execution = synthetic
    audit["forcing" if hypothesis == "H2" else "operators"][-1][hypothesis] = False
    result = q.decision(audit, control, execution)
    assert result["study_gate"] == "passed" and result["scientific_outcome"] == "rejected"


@pytest.mark.parametrize(
    "stdout",
    (
        "",
        "117 passed in 1.0s\n",
        "118 passed, 1 failed in 1.0s\n",
        "118 passed in 1.0s\n118 passed in 1.0s\n",
    ),
)
def test_controls_need_the_complete_unambiguous_success_summary(synthetic, stdout):
    _, control, _ = synthetic
    control["stdout"] = stdout
    assert not q.controls_passed(control)


@pytest.mark.parametrize("mutation", ("last_row", "receipt", "decision", "extra"))
def test_resealed_manifest_tampering_fails_fresh_reconstruction(
    tmp_path, monkeypatch, synthetic, mutation
):
    audit, control, execution = synthetic
    monkeypatch.setattr(q, "audit_children", lambda path: deepcopy(audit))
    saved = q.manifest(audit, control, execution)
    altered = deepcopy(saved)
    altered.pop("sha256")
    if mutation == "last_row":
        altered["audit"]["operators"][-1]["H3"] = False
    elif mutation == "receipt":
        altered["worker_execution"]["process_id"] = 333
    elif mutation == "decision":
        altered["decision"]["scientific_outcome"] = "rejected"
    else:
        altered["undeclared"] = 1
    path = tmp_path / "manifest.json"
    q.census.save_exclusive(path, q.census.sealed(altered))
    with pytest.raises(ValueError, match="differs"):
        q.audit_manifest(path)


@pytest.mark.parametrize("suffix", (".json", "_primary.zip", "_worker.zip", "_failure.json"))
def test_existing_or_partial_run_is_not_overwritten(tmp_path, monkeypatch, suffix):
    output = tmp_path / "run.json"
    existing = tmp_path / ("run" + suffix)
    existing.touch()
    monkeypatch.setattr(q, "metadata", lambda: pytest.fail("preflight ran despite old output"))
    with pytest.raises(ValueError, match="existing"):
        q.execute(output)
    assert existing.read_bytes() == b""
    assert list(tmp_path.iterdir()) == [existing]


def test_failed_preflight_leaves_an_explicit_inconclusive_marker(tmp_path, monkeypatch):
    monkeypatch.setattr(q, "metadata", lambda: (_ for _ in ()).throw(ValueError("changed source")))
    output = tmp_path / "run.json"
    with pytest.raises(ValueError, match="changed source"):
        q.execute(output)
    saved = q.census.read_json(tmp_path / "run_failure.json")
    q.census.unseal(saved)
    assert saved["stage"] == "source and parent preflight"
    assert saved["decision"]["scientific_outcome"] == "inconclusive"
    assert not output.exists()


def test_spawn_uses_actual_process_fields_and_the_registered_module(monkeypatch, tmp_path):
    observed = {}

    class Process:
        pid, returncode = 4521, 7

        def __init__(self, args, **kwargs):
            observed.update(args=args, kwargs=kwargs)

        def communicate(self):
            return "captured output", "captured error"

    monkeypatch.setattr(q.subprocess, "Popen", Process)
    result = q.spawn_worker(tmp_path / "run.json")
    assert result["process_id"] == 4521 and result["exit_code"] == 7
    assert result["stdout"] == "captured output" and result["stderr"] == "captured error"
    assert observed["args"][1:5] == ["-W", "error", "-m", q.MODULE]
    assert observed["kwargs"]["cwd"] == q.ROOT


@pytest.fixture
def one_case_archives(tmp_path, monkeypatch):
    """A persistence control with incomplete coverage, never an accepted study."""
    monkeypatch.setattr(q.records, "OPERATOR_CASES", (((1, 1, 1, 1), (0, 1, 2, 3), 23),))
    monkeypatch.setattr(q.records, "FORCING_CASES", ())
    monkeypatch.setattr(q, "metadata", lambda: {"unit_only": True})
    monkeypatch.setattr(q, "parent_audit", lambda: {"unit_only": True})
    monkeypatch.setattr(q, "verify_source_commit", lambda *args: None)
    output = tmp_path / "unit_only.json"
    q.build_primary(q.child_path(output, "primary"), q.metadata(), q.parent_audit())
    q.build_worker(q.child_path(output, "worker"), q.child_path(output, "primary"))
    return output


def test_real_numeric_archive_rebuilds_but_incomplete_scope_cannot_pass(one_case_archives):
    audit = q.audit_children(one_case_archives)
    assert (
        audit["full_entries_rebuilt"]
        and audit["operators"][0]["H1"]
        and audit["operators"][0]["H3"]
    )
    assert audit["coverage"] == {
        "operator_cases": 1,
        "forcing_cases": 0,
        "symmetric_columns": 1,
        "forcing_columns": 0,
    }
    result = q.decision(audit, {}, {"stdout": "{}"})
    assert result["scientific_outcome"] == "inconclusive"


def rewrite_test_zip(path, replace):
    """Mutate only test-created archives, including recalculated entry seals."""
    with ZipFile(path) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    entries.update(replace)
    replacement = Path(path).with_suffix(".replacement.zip")
    with ZipFile(replacement, "x") as archive:
        for name, value in entries.items():
            archive.writestr(name, value)
    replacement.replace(path)


@pytest.mark.parametrize("target", ("record", "array", "reference"))
def test_resealed_last_entry_tampering_is_rejected(one_case_archives, target):
    output = one_case_archives
    primary, worker = q.child_path(output, "primary"), q.child_path(output, "worker")
    path = worker if target == "reference" else primary
    with storage.Archive(
        path, "r", q.names("worker" if target == "reference" else "primary")
    ) as archive:
        if target == "array":
            arrays = archive.arrays("operator/0000.npz")
            arrays["refined"][-1, -1] += 0.01
            stream = io.BytesIO()
            np.savez(stream, **arrays)
            replace = {"operator/0000.npz": stream.getvalue()}
        else:
            row = archive.document("operator/0000.json")
            row["external_dimension"] = 27
            replace = {"operator/0000.json": json.dumps(q.census.sealed(row)).encode()}
    rewrite_test_zip(path, replace)
    if target != "reference":
        with storage.Archive(worker, "r", q.names("worker")) as archive:
            changed = {}
            for name in ("header.json", "footer.json"):
                doc = archive.document(name)
                doc["primary_sha256"] = storage.file_sha(primary)
                changed[name] = json.dumps(q.census.sealed(doc)).encode()
        rewrite_test_zip(worker, changed)
    with pytest.raises(ValueError, match="reconstruction differs"):
        q.audit_children(output)


def test_recorded_commit_must_contain_the_exact_source():
    commit = q.git_bytes("rev-parse", "HEAD").decode().strip()
    source = {"files": {"README.md": q.normalized_sha(q.git_bytes("show", f"{commit}:README.md"))}}
    q.verify_source_commit(commit, source)
    with pytest.raises(ValueError, match="differs"):
        q.verify_source_commit(commit, {"files": {"README.md": "0" * 64}})
    with pytest.raises(ValueError, match="invalid"):
        q.verify_source_commit("not-a-commit", source)


def test_registered_entry_inventory_is_exact():
    assert len(q.names("primary")) == 2247
    assert len(q.names("worker")) == 1127
    assert all(len(set(q.names(route))) == len(q.names(route)) for route in ("primary", "worker"))


def test_archive_change_during_audit_is_detected(one_case_archives, monkeypatch):
    target = q.child_path(one_case_archives, "worker")
    original = storage.file_sha
    calls = 0

    def changed(path):
        nonlocal calls
        if Path(path) == target:
            calls += 1
            if calls > 1:
                return "0" * 64
        return original(path)

    monkeypatch.setattr(storage, "file_sha", changed)
    with pytest.raises(ValueError, match="archive bytes changed"):
        q.audit_children(one_case_archives)


@pytest.mark.parametrize("altered", ("source", "parent", "process_id", "configuration"))
def test_resealed_header_mutations_fail_preflight(one_case_archives, altered):
    primary = q.child_path(one_case_archives, "primary")
    with storage.Archive(primary, "r", q.names("primary")) as archive:
        start = archive.document("header.json")
    start[altered] = True if altered == "process_id" else {"altered": True}
    rewrite_test_zip(primary, {"header.json": json.dumps(q.census.sealed(start)).encode()})
    with pytest.raises(ValueError):
        q.audit_children(one_case_archives)
