"""Immutable real H1 evidence: complete rejected comparison, not acceptance."""

from copy import deepcopy

import pytest

from research import d3q27_quartic_forcing_audit as diagnostic
from research import q012h2_d3q27_quartic_forcing as run

PARENT_SHA = "b2ec4ed701a677c6ddbca1016b45c3de3d4861ee9c20d98592bfb262e3d58df6"
DIAGNOSTIC_SHA = "6f6c72eef1f8d93f6083ae0e88ce52a205daacad880e163df46bb913600004a3"


@pytest.fixture(scope="module")
def saved():
    assert run.archive.file_sha(run.OUTPUT) == PARENT_SHA
    value = run.common.read_json(run.OUTPUT)
    run.common.unseal(value)
    return value


@pytest.fixture(scope="module")
def report():
    path = run.OUTPUT.with_name("q012h2_d3q27_quartic_forcing_diagnostics.json")
    assert run.archive.file_sha(path) == DIAGNOSTIC_SHA
    value = run.common.read_json(path)
    run.common.unseal(value)
    run.oracle.verify_source_commit(value["source_commit"], value["source"])
    return value


def test_real_full_column_compensated_rebuild(report):
    rebuilt = diagnostic.audit(run.OUTPUT)
    assert run.same(
        rebuilt, {k: v for k, v in report.items() if k not in ("source", "source_commit", "sha256")}
    )
    assert rebuilt["columns"] == 5478


def test_every_original_failure_is_retained(saved, report):
    assert [g["summary"]["failed_columns"] for g in report["grids"]] == [182, 174, 158]
    assert sum(g["summary"]["failed_columns"] for g in report["grids"]) == 514
    assert [g["summary"]["failed_at_or_above_floor_columns"] for g in report["grids"]] == [8, 0, 0]
    assert not saved["decision"]["h1_passed"]
    assert saved["decision"]["q012h2_outcome"] == "not_evaluated"
    assert saved["decision"]["H2"] == saved["decision"]["H3_with_solves"] == "not_evaluated"


@pytest.mark.parametrize("size", [17, 33, 65])
def test_all_saved_columns_and_physics_rebuild(size, saved):
    state = run.inputs.selection_state()
    groups = tuple(tuple(r["group"]) for r in state["selection"]["groups"])
    rebuilt = run.compare_grid(run.OUTPUT, size, groups)
    original = next(g for g in saved["grids"] if g["size"] == size)
    assert run.same(rebuilt, original)
    assert len(original["physical"]) == 20 and all(r["passed"] for r in original["physical"])
    assert all(original["negative_controls"][name] is not None for name in run.primary.MUTATIONS)


def test_all_six_actual_process_receipts_and_resource_sequences(saved):
    run.verify_execution(run.OUTPUT, saved["execution"])
    assert len({r["process_id"] for r in saved["execution"]}) == 6
    assert all(r["exit_code"] == 0 for r in saved["execution"])
    assert all(
        r["receipt"]["completion_resources"]["peak_private_commit_bytes"] <= 3 * 1024**3
        for r in saved["execution"]
    )


def test_invented_execution_exit_cannot_reuse_valid_scientific_arrays(saved):
    wrong = deepcopy(saved["execution"])
    wrong[-1]["exit_code"] = 1
    with pytest.raises(ValueError, match="execution evidence"):
        run.verify_execution(run.OUTPUT, wrong)


def test_complete_saved_comparison_cannot_be_called_full_quartic_success(saved):
    assert run.same(run.audit_manifest(run.OUTPUT, full=False), saved["decision"])
    assert all(not g["h1_passed"] and g["columns"] == 1826 for g in saved["grids"])
