"""Implementation/input/negative controls; no formal H1 pilot acceptance here."""

from copy import deepcopy
from itertools import combinations_with_replacement
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from research import d3q27_quartic_inputs as inputs
from research import d3q27_quartic_lbm as lbm
from research import q012h2_d3q27_quartic_forcing as run


def test_actual_fixed_selection_is_committed_and_complete():
    value = inputs.selection_state()
    rows = value["selection"]["groups"]
    assert len(rows) == 698 and sum(r["columns"] for r in rows) == 1826
    assert sorted(i for block in inputs.BLOCK_INDICES for i in block) == list(range(104))
    assert max(r["operator_dimension"] for r in rows) == 432


def test_fixed_selection_seal_cannot_be_replaced(monkeypatch):
    monkeypatch.setattr(inputs, "SELECTION_SHA", "0" * 64)
    with pytest.raises(ValueError, match="S0 artifact changed"):
        inputs.selection_state()


def test_grid_and_route_paths_are_explicit(tmp_path):
    a, b = run.paths(tmp_path / "pilot.json", 33, "worker")
    assert a.name == "pilot_n33_worker.json" and b.name == "pilot_n33_worker.zip"
    with pytest.raises(ValueError):
        run.paths(a, 16, "worker")
    with pytest.raises(ValueError):
        run.paths(a, 17, "missing")


def test_scoped_resources_cover_default_s0_and_custom_outputs():
    assert run.resource_output(run.OUTPUT).name == "q012h2_d3q27_quartic"
    assert run.resource_output(Path("replays/custom.json")) == Path("replays/custom.json")


def test_archive_names_enforce_all_tuples_and_physical():
    for route, count in (("primary", 699), ("worker", 700)):
        names = run.names(698, route)
        assert len(names) == len(set(names)) == count
        assert "tuple_0697.npz" in names and "tuple_0698.npz" not in names
        assert ("physical.npz" in names) == (route == "worker")


@pytest.mark.parametrize("kind", ["shape", "nonfinite", "empty", "population"])
def test_column_error_requires_full_finite_matching_vectors(kind):
    left = np.zeros((27, 3), dtype=complex)
    right = left.copy()
    if kind == "shape":
        left = left[:, :-1]
    elif kind == "nonfinite":
        left[-1, -1] = np.nan
    elif kind == "empty":
        left, right = left[:, :0], right[:, :0]
    else:
        left, right = left[:-1], right[:-1]
    with pytest.raises(ValueError):
        run.column_errors(left, right)


def test_relative_floor_does_not_hide_small_nonzero_columns():
    reference = np.zeros((27, 2), dtype=complex)
    actual = reference.copy()
    actual[-1] = [1e-22, 1e-21]
    np.testing.assert_allclose(run.column_errors(actual, reference), [1e-8, 1e-7], rtol=1e-15)


def test_recheck_uses_actual_flat_fiber_audit_schema(monkeypatch):
    # load_fibers returns filename/sha256 plus audit fields, not a 'validation' object.
    validation = {"entries": {"response": "saved"}, "complete_monomials": 192920, "passed": True}
    loaded = {
        "lower_arrays": {"dimension": 104},
        "fiber_load": {"filename": "fiber.npz", "sha256": "seal", **validation},
    }
    monkeypatch.setattr(inputs, "fingerprint", lambda _: {"dimension": 104})
    monkeypatch.setattr(run.cubic, "validate_fibers", lambda _: validation)
    run.recheck_lower(None, None, loaded)
    changed = deepcopy(loaded)
    changed["fiber_load"]["entries"]["response"] = "different"
    with pytest.raises(ValueError, match="original cubic"):
        run.recheck_lower(None, None, changed)
    changed = deepcopy(loaded)
    changed["lower_arrays"]["dimension"] = 4
    with pytest.raises(ValueError, match="lower Taylor"):
        run.recheck_lower(None, None, changed)


def test_only_timing_is_excluded_from_paired_input_identity():
    values = {
        "fresh_rebuild_seconds": 2.0,
        "cubic_load_and_audit_seconds": 3.0,
        "size": 17,
        "lower_arrays": {"dimension": 104},
        "passed": True,
    }
    assert run.static_lower_receipt(values) == {
        "size": 17,
        "lower_arrays": {"dimension": 104},
        "passed": True,
    }


def test_primary_and_worker_payload_roundtrip_preserves_tail(tmp_path, monkeypatch):
    rng = np.random.default_rng(2026090813)
    n = 8
    indices = {
        d: np.array(list(combinations_with_replacement(range(n), d)), dtype=np.int64)
        for d in (2, 3)
    }
    draw = lambda shape: rng.standard_normal(shape) + 1j * rng.standard_normal(shape)
    data = lbm.TaylorData(
        size=17,
        omega=1.5,
        eta=0.02,
        power=2,
        waves=np.zeros((n, 3), dtype=np.int64),
        basis=draw((27, n)),
        linear=np.diag(np.linspace(0.4, 0.8, n)).astype(complex),
        indices=indices,
        h={d: draw((len(ids), 27)) for d, ids in indices.items()},
        g={d: draw((len(ids), n)) for d, ids in indices.items()},
    )
    monkeypatch.setattr(inputs, "BLOCK_INDICES", ((0, 1), (2, 3), (4, 5), (6, 7)))
    group = (0, 1, 2, 3)
    left, right = run.tuple_arrays(data, group, "primary"), run.tuple_arrays(data, group, "worker")
    assert left["forcing"].shape == (27, 16)
    assert max(run.column_errors(left["forcing"], right["forcing"])) < 1e-12
    filename = tmp_path / "payload.zip"
    with run.archive.Archive(filename, "x", ("main.npz", "worker.npz")) as saved:
        saved.put_arrays("main.npz", left)
        saved.put_arrays("worker.npz", right)
    with run.archive.Archive(filename, "r", ("main.npz", "worker.npz")) as saved:
        assert run.archive.arrays_equal(left, saved.arrays("main.npz"))
        changed = saved.arrays("worker.npz")
    changed["forcing"][-1, -1] += 1
    assert max(run.column_errors(left["forcing"], changed["forcing"])) > 1e-8


def test_resource_start_failure_is_retained_without_starting_forcing(tmp_path, monkeypatch):
    measurements = [{"stage": "process_start", "available_physical_bytes": 3 * 1024**3}]

    def fail(*args, **kwargs):
        raise run.resources.ResourceLimitError("insufficient starting memory", measurements)

    monkeypatch.setattr(run.resources, "Guard", fail)
    output = tmp_path / "pilot.json"
    with pytest.raises(run.resources.ResourceLimitError):
        run.run_grid(output, 17, "primary")
    saved = run.common.read_json(tmp_path / "pilot_n17_primary_failure.json")
    run.common.unseal(saved)
    assert saved["resources"] == measurements
    assert saved["completed_tuple_prefix"] == 0 and saved["q012h2_outcome"] == "inconclusive"
    assert not (tmp_path / "pilot_n17_primary.zip").exists()


def test_existing_output_is_not_overwritten(tmp_path):
    output = tmp_path / "pilot.json"
    record, _ = run.paths(output, 17, "primary")
    run.common.save_exclusive(record, {"user": "preserved"})
    before = record.read_bytes()
    with pytest.raises(ValueError, match="existing"):
        run.run_grid(output, 17, "primary")
    assert record.read_bytes() == before
    assert not (tmp_path / "pilot_n17_primary_failure.json").exists()


def test_false_actual_child_exit_is_not_success(tmp_path, monkeypatch):
    process = SimpleNamespace(pid=123, returncode=1, communicate=lambda: ("{}", None))
    monkeypatch.setattr(run.subprocess, "Popen", lambda *a, **kw: process)
    with pytest.raises(ValueError, match="exited 1"):
        run.call_child(tmp_path / "pilot.json", 17, "primary")


def test_fake_receipt_pid_is_not_actual_execution(tmp_path, monkeypatch):
    process = SimpleNamespace(
        pid=123, returncode=0, communicate=lambda: ('{"process_id":124}', None)
    )
    monkeypatch.setattr(run.subprocess, "Popen", lambda *a, **kw: process)
    with pytest.raises(ValueError, match="PID"):
        run.call_child(tmp_path / "pilot.json", 17, "primary")


def test_source_metadata_retains_original_scope():
    source = run.metadata()
    assert set(source["files"]) == set(run.FILES)
    assert source["selection_sha256"] == inputs.SELECTION_SHA
    assert source["selection_source"] == run.selection.metadata()
    assert "no H2 solve" in run.BOUNDARY
