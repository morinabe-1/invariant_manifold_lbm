"""OS-byte semantics and registered limits, including negative controls."""

import os

import numpy as np
import pytest

from research import d3q27_quartic_resources as r


@pytest.mark.skipif(os.name != "nt", reason="registered OS counters are Windows-specific")
def test_real_os_peaks_include_touched_arrays_and_are_not_payload_estimates():
    before = r.counters()
    data = np.ones(8 * 1024 * 1024, dtype=float)
    during = r.counters()
    assert data.sum() == len(data)
    assert during["peak_working_set_bytes"] >= during["working_set_bytes"] > 0
    assert during["peak_private_commit_bytes"] >= during["private_commit_bytes"] > 0
    assert during["private_commit_bytes"] > before["private_commit_bytes"]
    del data
    after = r.counters()
    assert after["peak_working_set_bytes"] >= during["peak_working_set_bytes"]
    assert after["peak_private_commit_bytes"] >= during["peak_private_commit_bytes"]
    assert 0 < after["available_physical_bytes"] <= after["total_physical_bytes"]


@pytest.mark.parametrize(
    "key", ("peak_working_set_bytes", "peak_private_commit_bytes", "seconds", "disk")
)
def test_each_registered_ceiling_has_an_independent_failure(key):
    values = {
        "peak_working_set_bytes": r.PEAK_LIMIT,
        "peak_private_commit_bytes": r.PEAK_LIMIT,
        "seconds": r.TIME_LIMIT,
        "disk": r.DISK_LIMIT,
    }
    assert all(r.limit_checks(values, values["seconds"], values["disk"]).values())
    values[key] += 1
    result = r.limit_checks(values, values["seconds"], values["disk"])
    assert sum(result.values()) == 3


def test_guard_requires_initial_available_ram_without_writing(tmp_path, monkeypatch):
    snapshot = {
        "peak_working_set_bytes": 10,
        "peak_private_commit_bytes": 20,
        "available_physical_bytes": 4 * r.GIB - 1,
    }
    monkeypatch.setattr(r, "counters", lambda: dict(snapshot))
    monkeypatch.setattr(r.shutil, "disk_usage", lambda _: type("Usage", (), {"free": 7 * r.GIB})())
    with pytest.raises(RuntimeError, match="starting"):
        r.Guard(tmp_path / "selection.json")
    assert list(tmp_path.iterdir()) == []


def test_guard_preserves_failure_measurement(tmp_path, monkeypatch):
    snapshot = {
        "peak_working_set_bytes": 10,
        "peak_private_commit_bytes": 20,
        "available_physical_bytes": 4 * r.GIB,
    }
    monkeypatch.setattr(r, "counters", lambda: dict(snapshot))
    monkeypatch.setattr(r.shutil, "disk_usage", lambda _: type("Usage", (), {"free": 7 * r.GIB})())
    guard = r.Guard(tmp_path / "selection.json")
    snapshot["peak_private_commit_bytes"] = r.PEAK_LIMIT + 1
    with pytest.raises(RuntimeError, match="ceiling"):
        guard.sample("allocation")
    assert not guard.records[-1]["checks"]["peak_private_commit"]
