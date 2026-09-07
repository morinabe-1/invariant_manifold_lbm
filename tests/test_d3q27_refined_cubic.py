"""Q012f2 checks before the exhaustive run, including fail-closed archival paths."""

import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_cubic as cubic
from research import d3q27_exact_residual as exact
from research import d3q27_refined_cubic as refined
from research import q012f2_d3q27_refined_cubic as runner


def test_sealed_exact_inputs_and_registered_controls():
    assert runner.input_audit()["passed"]
    control = runner.controls()
    assert control["passed"]
    assert len(control["results"]["exact_arithmetic"]["records"]) == 10


@pytest.fixture(scope="module", params=(17, 33, 65))
def witness(request):
    size = request.param
    model, rebuild, old, proofs = runner.fresh_input(size)
    assert rebuild["passed"]
    context = cubic.build_context(model)
    row, fibers = runner.case(context, 0, old, proofs, exact.audit_integer)
    return size, context, old, proofs, row, fibers


def test_actual_first_case_preserves_old_values_and_independent_exact_proof(witness):
    size, context, old, proofs, row, fibers = witness
    independent, copied = runner.case(context, 0, old, proofs, exact.audit_gmp)
    assert independent == row
    for key in fibers:
        np.testing.assert_array_equal(copied[key], fibers[key])
    assert row["previous_match"]["passed"]
    if size == 65:
        assert row["previous_match"]["checks"]["q012f1a_exact_proof"]
    assert row["passed"] and all(row["candidate_gates"].values())
    assert [r["iteration"] for r in row["refinement_history"]] == [0, 1, 2, 3]
    assert all(r["correction_norm"] >= 0 for r in row["refinement_history"][:3])
    assert "correction_norm" not in row["refinement_history"][3]
    assert fibers["forcing"].shape == fibers["response"].shape == (4, 27)
    assert fibers["reduced"].shape == (4, 4)


def synthetic_gate_inputs():
    return (
        {
            "status": "nonsingular_practical",
            "numerical_rank": 2,
            "operator_dimension": 2,
            "condition_number": 10,
            "backend": {"passed": True},
        },
        {"full_relative_residual": 0.0, "structural_error": 0.0},
        {"gates": {k: True for k in exact.EXACT_GATES}},
    )


@pytest.mark.parametrize(
    "status", ["singular_compatible", "singular_incompatible", "nonsingular_ill_conditioned"]
)
def test_exact_zero_residual_does_not_accept_bad_rank_or_condition(status):
    reference, current, proof = synthetic_gate_inputs()
    reference["status"] = status
    assert not all(refined.candidate_gates(reference, current, proof).values())


@pytest.mark.parametrize(
    "gate", ["rank", "condition", "backend", "full", "structure", *exact.EXACT_GATES]
)
def test_each_candidate_gate_is_required(gate):
    reference, current, proof = synthetic_gate_inputs()
    if gate == "rank":
        reference["numerical_rank"] = 1
    elif gate == "condition":
        reference["condition_number"] = np.nextafter(1e8, np.inf)
    elif gate == "backend":
        reference["backend"]["passed"] = False
    elif gate == "full":
        current["full_relative_residual"] = np.nextafter(1e-9, np.inf)
    elif gate == "structure":
        current["structural_error"] = np.nextafter(5e-12, np.inf)
    else:
        proof["gates"][gate] = False
    assert not all(refined.candidate_gates(reference, current, proof).values())


def test_streaming_archive_is_deterministic_lossless_and_nonoverwriting(tmp_path):
    rows = [{"ordinal": 0, "value": 1 / 3}, {"ordinal": 1, "passed": False, "condition": None}]
    archives = []
    for name in ("first", "second"):
        with refined.RecordWriter(tmp_path / (name + ".jsonl.gz")) as writer:
            with pytest.raises(ValueError, match="close"):
                writer.metadata()
            for row in rows:
                writer.append(row)
            with pytest.raises(ValueError):
                writer.append({"nonfinite": float("nan")})
        archives.append(writer.metadata())
        assert writer.count == 2
        assert list(refined.iter_records(writer.path)) == rows
    assert all(a["roundtrip_passed"] for a in archives)
    assert archives[0]["sha256"] == archives[1]["sha256"]
    assert archives[0]["records_digest_sha256"] == archives[1]["records_digest_sha256"]
    with pytest.raises(FileExistsError), refined.RecordWriter(tmp_path / "first.jsonl.gz"):
        pass


def test_streaming_archive_remains_readable_after_execution_exception(tmp_path):
    path = tmp_path / "failed.jsonl.gz"
    with pytest.raises(RuntimeError), refined.RecordWriter(path) as writer:
        writer.append({"ordinal": 0, "passed": False})
        raise RuntimeError("manufactured late failure")
    assert writer.metadata()["roundtrip_passed"]
    assert list(refined.iter_records(path)) == [{"ordinal": 0, "passed": False}]


def test_sparse_npz_is_finite_nonpickled_and_nonoverwriting(tmp_path):
    arrays = {"input_triples": np.zeros((2, 3), dtype=np.int64), "response": np.array([[1 + 2j]])}
    path = tmp_path / "fibers.npz"
    meta = refined.save_fibers(path, arrays)
    assert meta["roundtrip_passed"]
    with np.load(path, allow_pickle=False) as saved:
        for key, value in arrays.items():
            np.testing.assert_array_equal(saved[key], value)
    with pytest.raises(FileExistsError):
        refined.save_fibers(path, arrays)
    for name, value in (("object", np.array([{}], dtype=object)), ("nan", np.array([np.nan + 0j]))):
        target = tmp_path / (name + ".npz")
        with pytest.raises(ValueError):
            refined.save_fibers(target, {"invalid": value})
        assert not target.exists()


def test_summary_has_exact_order_and_does_not_skip_failure(witness):
    _, _, _, _, row, _ = witness
    bad = deepcopy(row)
    bad["ordinal"] = 1
    bad["candidate_gates"]["full_population_equation"] = False
    bad["refined"]["full_relative_residual"] = 1e-8
    bad["passed"] = False
    summary = refined.summarize([row, bad])
    assert summary["completed_count"] == 2 and summary["product_dimension_sum"] == 8
    assert summary["candidate_failed_ordinals"] == [1]
    assert not summary["coverage_passed"] and not summary["all_candidates_passed"]
    assert summary["worst_cases"]["full_residual"] == bad
    duplicate = refined.summarize([row, row])
    assert not duplicate["coverage_passed"]
    incomplete = refined.summarize(
        [row, {"ordinal": 1, "execution_error": {"type": "RuntimeError"}, "passed": False}]
    )
    assert incomplete["completed_count"] == 1 and incomplete["record_count"] == 2
    assert not incomplete["coverage_passed"]


def test_late_failure_preserves_full_existing_records_without_accepting_them(
    witness, tmp_path, monkeypatch
):
    _, _, _, _, row, _ = witness
    paths = runner.paths_for_grid(tmp_path / "result.json", 17)
    with refined.RecordWriter(paths["records"]) as writer:
        writer.append(row)
    before = refined.file_hash(paths["records"])

    def fail(*_):
        raise ValueError("manufactured verification failure")

    monkeypatch.setattr(runner, "scan_grid", fail)
    result = runner.guarded_scan_grid(17, paths)
    assert result["execution_error"]["type"] == "ValueError"
    assert result["summary"]["completed_count"] == 1
    assert result["record_archive"]["sha256"] == before
    assert result["replay_records"] == [row]
    assert not result["finite"] and not result["saved_summary_equal"]


def test_empty_or_partial_three_grid_evidence_is_inconclusive():
    validity, hypotheses, outcome = runner.decision(
        {"passed": True}, {"passed": True}, [], {"passed": False}
    )
    assert not all(validity.values()) and not any(hypotheses.values())
    assert outcome == "inconclusive"


def test_mathematical_failure_and_incomplete_coverage_are_distinct():
    grids = [
        {
            "size": size,
            "input_rebuild": {"passed": True},
            "finite": True,
            "summary": {
                "coverage_passed": True,
                "all_candidates_passed": True,
                "previous_selected_count": 324,
                "previous_selected_failures": 0,
                "mp128_agreement_failures": 0,
            },
            "record_archive": {"roundtrip_passed": True},
            "saved_summary_equal": True,
            "fiber_archive": {"roundtrip_passed": True},
            "directional_forcing": {"passed": True},
            "sealed_paired_full_forcing_equal": True,
            "conjugacy": {"coverage": True, "passed": True},
        }
        for size in (17, 33, 65)
    ]
    evaluate = lambda: runner.decision({"passed": True}, {"passed": True}, grids, {"passed": True})
    assert evaluate()[2] == "accepted"
    grids[2]["summary"]["all_candidates_passed"] = False
    validity, hypotheses, outcome = evaluate()
    assert all(validity.values()) and not hypotheses["H1_all_three_grid_refined_candidates_pass"]
    assert outcome == "rejected"
    grids[2]["conjugacy"]["coverage"] = False
    assert evaluate()[2] == "inconclusive"


def test_corrupt_partial_archive_is_retained_but_not_accepted(tmp_path, monkeypatch):
    paths = runner.paths_for_grid(tmp_path / "result.json", 17)
    paths["records"].write_bytes(b"corrupt partial record archive")

    def fail(*_):
        raise ValueError("manufactured interruption")

    monkeypatch.setattr(runner, "scan_grid", fail)
    result = runner.guarded_scan_grid(17, paths)
    assert result["recovery_error"] is not None
    assert result["record_archive"] is None and not result["finite"]
    assert paths["records"].read_bytes() == b"corrupt partial record archive"


def test_scan_records_execution_failure_without_zero_filling_unexecuted_fibers(
    witness, tmp_path, monkeypatch
):
    size, context, old, proofs, row, fibers = witness
    monkeypatch.setattr(
        runner, "fresh_input", lambda _: (context.model, {"passed": True}, old, proofs)
    )

    def fail_second(_context, ordinal, *_):
        if ordinal:
            raise np.linalg.LinAlgError("manufactured unexpected backend failure")
        return row, fibers

    monkeypatch.setattr(runner, "case", fail_second)
    paths = runner.paths_for_grid(tmp_path / "partial.json", size)
    result = runner.scan_grid(size, paths)
    assert result["summary"]["completed_count"] == 1
    assert result["summary"]["record_count"] == 2
    assert not result["summary"]["coverage_passed"]
    assert result["saved_summary_equal"] and result["record_archive"]["roundtrip_passed"]
    assert result["conjugacy"] is None and result["directional_forcing"] is None
    records = list(refined.iter_records(paths["records"]))
    assert records[0] == row and records[1]["execution_error"]["type"] == "LinAlgError"
    with np.load(paths["fibers"], allow_pickle=False) as saved:
        assert saved["response"].shape == (4, 27)
        np.testing.assert_array_equal(saved["response"], fibers["response"])


def test_partial_output_and_sibling_escape_are_refused(tmp_path):
    output = tmp_path / "study.json"
    partial = runner.paths_for_grid(output, 33)["fibers"]
    partial.write_bytes(b"preserved")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.q012f2_d3q27_refined_cubic",
            "--output",
            str(output),
            "--replay",
            str(tmp_path / "worker.json"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2 and "not overwritten" in result.stderr
    assert partial.read_bytes() == b"preserved" and not output.exists()
    with pytest.raises(ValueError):
        runner.sibling(Path("directory"), "../escaped.npz")
