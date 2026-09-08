"""Persistence and validity controls; no acceptance of the full Q012h2 pilot."""

import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from research import q012h2_d3q27_quartic_selection as r


def test_multidimensional_numeric_archive_roundtrip_is_exclusive_and_readonly(tmp_path):
    path = tmp_path / "arrays.npz"
    values = {
        "matrix": np.arange(24, dtype=np.float64).reshape(2, 3, 4),
        "complex": np.array([1 + 2j, -3j]),
        "integer": np.array([1, 5], dtype=np.int64),
    }
    record = r.save_arrays(path, values)
    before = path.read_bytes()
    loaded = r.load_arrays(path, record)
    assert set(loaded) == set(values)
    assert all(
        np.array_equal(values[k], loaded[k]) and not loaded[k].flags.writeable for k in values
    )
    with pytest.raises(FileExistsError):
        r.save_arrays(path, values)
    assert path.read_bytes() == before


@pytest.mark.parametrize("mutation", ("filename", "bytes", "sha256", "array_sha", "shape", "keys"))
def test_changed_saved_entry_metadata_is_rejected(tmp_path, mutation):
    path = tmp_path / "arrays.npz"
    record = r.save_arrays(path, {"scores": np.array([1.0, 2.0, 3.0])})
    changed = deepcopy(record)
    if mutation in ("filename", "sha256"):
        changed[mutation] = "wrong"
    elif mutation == "bytes":
        changed[mutation] += 1
    elif mutation == "array_sha":
        changed["arrays"]["scores"]["sha256"] = "wrong"
    elif mutation == "shape":
        changed["arrays"]["scores"]["shape"] = [1, 3]
    else:
        changed["arrays"]["extra"] = changed["arrays"]["scores"]
    with pytest.raises(ValueError):
        r.load_arrays(path, changed)


@pytest.mark.parametrize(
    "value",
    (
        np.array([float("nan")]),
        np.array([float("inf")]),
        np.array([{}], dtype=object),
        np.array([1.0], dtype=np.float32),
    ),
)
def test_nonfinite_or_pickle_like_arrays_are_rejected_before_writing(tmp_path, value):
    path = tmp_path / "bad.npz"
    with pytest.raises(ValueError):
        r.save_arrays(path, {"value": value})
    assert not path.exists()


def test_full_distance_comparison_detects_last_entry_and_does_not_relax_floor():
    left = np.full(r.selection.TUPLE_COUNT, 0.125)
    right = left.copy()
    assert r.comparison(left, right)["passed"]
    right[-1] += 2e-13
    value = r.comparison(left, right)
    assert not value["passed"] and value["maximum_difference_ordinal"] == len(left) - 1
    with pytest.raises(ValueError):
        r.comparison(left[:-1], right[:-1])


def test_paths_keep_known_output_directory_and_reject_unregistered_cases(tmp_path):
    output = tmp_path / "selection.json"
    assert r.paths(output, 65, "worker") == (
        tmp_path / "selection_n65_worker.json",
        tmp_path / "selection_n65_worker.npz",
    )
    for size, route in ((16, "worker"), (17, "other"), (True, "primary")):
        with pytest.raises(ValueError):
            r.paths(output, size, route)


def test_empty_receipts_and_partial_audits_never_create_selection():
    with pytest.raises(ValueError):
        r.validate_execution(Path("unused.json"), [])
    for audits in ([], [{"size": 17, "passed": True}]):
        with pytest.raises(ValueError):
            r.build_selection(audits)


def test_existing_output_is_not_overwritten_or_used_as_success(tmp_path, monkeypatch):
    output = tmp_path / "already.json"
    r.common.save_exclusive(output, {"user": "preserve"})
    before = output.read_bytes()

    def forbidden(*args, **kwargs):
        raise AssertionError("should reject existing output before any computation")

    monkeypatch.setattr(r, "metadata", forbidden)
    with pytest.raises(ValueError, match="existing"):
        r.execute(output)
    assert output.read_bytes() == before


def resource_samples(final="after_saved_readback"):
    row = {
        "working_set_bytes": 10,
        "peak_working_set_bytes": 20,
        "private_commit_bytes": 30,
        "peak_private_commit_bytes": 40,
        "available_physical_bytes": 5 * r.resources.GIB,
        "total_physical_bytes": 16 * r.resources.GIB,
        "free_disk_bytes": 8 * r.resources.GIB,
        "new_file_bytes": 100,
        "wall_seconds": 0.0,
        "stage": "process_start",
    }
    row["checks"] = r.resources.limit_checks(row, 0.0, 100)
    return [row, {**row, "stage": final, "wall_seconds": 1.0}]


@pytest.mark.parametrize(
    "mutation",
    (
        "missing_start",
        "missing_end",
        "low_start_ram",
        "false_peak",
        "decreasing_peak",
        "negative_bytes",
        "stale_checks",
        "time",
        "payload_as_peak",
    ),
)
def test_saved_resource_claims_require_actual_consistent_counter_fields(mutation):
    rows = resource_samples()
    r.validate_resources(rows)
    if mutation == "missing_start":
        rows[0]["stage"] = "late"
    elif mutation == "missing_end":
        rows.pop()
    elif mutation == "low_start_ram":
        rows[0]["available_physical_bytes"] = r.resources.GIB
    elif mutation == "false_peak":
        rows[1]["peak_private_commit_bytes"] = 2
    elif mutation == "decreasing_peak":
        rows[1]["peak_private_commit_bytes"] = 39
    elif mutation == "negative_bytes":
        rows[1]["new_file_bytes"] = -1
    elif mutation == "stale_checks":
        rows[1]["checks"] = {**rows[1]["checks"], "new_disk": False}
    elif mutation == "time":
        rows[1]["wall_seconds"] = -1.0
    else:
        rows[1]["peak_working_set_bytes"] = 0
    with pytest.raises(ValueError):
        r.validate_resources(rows)


def test_failure_persists_raw_prefix_and_resource_evidence_without_acceptance(tmp_path):
    output = tmp_path / "selection.json"
    error = r.resources.ResourceLimitError("test cap", resource_samples())
    error.partial_distances = np.array([1.0, 0.5, 0.125])
    r.record_failure(output, error, 17, "primary")
    path = tmp_path / "selection_n17_primary_failure.json"
    value = r.common.read_json(path)
    r.common.unseal(value)
    assert value["decision"]["passed"] is False
    assert value["decision"]["q012h2_outcome"] == "inconclusive"
    assert value["resource_records"] == error.resource_records
    assert value["partial"]["completed_prefix_tuples"] == 3
    array_path = tmp_path / value["partial"]["filename"]
    assert np.array_equal(np.load(array_path, allow_pickle=False), error.partial_distances)
    before = path.read_bytes()
    r.record_failure(output, RuntimeError("later"), 17, "primary")
    assert path.read_bytes() == before


@pytest.mark.parametrize("kind", ("failed_exit", "wrong_pid", "missing_receipt"))
def test_child_process_failure_cannot_be_relabelled_as_completion(tmp_path, monkeypatch, kind):
    class Process:
        pid = 1234
        returncode = 1 if kind == "failed_exit" else 0

        def communicate(self):
            if kind == "missing_receipt":
                return "{}", None
            return '{"process_id": 99}', None

    monkeypatch.setattr(r.subprocess, "Popen", lambda *args, **kwargs: Process())
    with pytest.raises((ValueError, KeyError)):
        r.call_child(tmp_path / "selection.json", 17, "primary")


def test_current_preregistration_and_parent_source_are_unchanged():
    source = r.metadata()
    assert set(source["files"]) == set(r.SOURCE_FILES)
    assert r.parent_state()["sha256"] == r.PARENT_SHA


@pytest.mark.parametrize("configured", (False, True))
def test_standalone_import_preserves_inherited_numerical_runtime(configured):
    names = ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS")
    environment = dict(os.environ)
    for index, name in enumerate(names):
        environment.pop(name, None)
        if configured:
            environment[name] = str(index + 2)
    code = (
        "import os; "
        f"names={names!r}; before={{k:os.environ.get(k) for k in names}}; "
        "from research import q012h2_d3q27_quartic_selection; "
        "after={k:os.environ.get(k) for k in names}; assert before==after,(before,after)"
    )
    result = subprocess.run(
        [sys.executable, "-W", "error", "-c", code],
        cwd=r.ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
