"""Recompute every Q012f1a exact decision and independently replay its saved matrices."""

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_exact_residual as exact
from research import q012a_d3q27_foundation as q012a
from research import q012f1a_d3q27_exact_residual as runner
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = q012a.ARTIFACT_DIRECTORY / "q012f1a_d3q27_exact_residual.json"
PREPARED = PATH.with_name("q012f1a_d3q27_exact_residual_prepared.json")
REPLAY = PATH.with_name("q012f1a_d3q27_exact_residual_replay.json")


@pytest.fixture(scope="module")
def artifact():
    return runner.read_json(PATH)


@pytest.fixture(scope="module")
def prepared():
    return runner.read_json(PREPARED)


def test_sealed_result_inputs_and_retained_previous_rejections(artifact):
    assert _file_sha256(PATH) == "869831275160a5457e554fff6ed8750410ee734cff99d6c9349f90f38ccd42a4"
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert artifact["source"] == source_metadata()
    assert _file_sha256(Path(runner.__file__)) == artifact["runner_source"]["sha256"]
    for name, module in runner.HELPERS:
        assert _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
    assert runner.input_audit()["passed"]
    old = runner.read_json(runner.PRIOR_PATH)
    assert old["study_gate"] == "passed" and old["scientific_outcome"] == "rejected"
    assert not any(old["cycle"]["hypothesis_gates"].values())
    assert runner.previous.prior_artifact()["scientific_outcome"] == "rejected"
    assert _all_numeric_values_finite(artifact)


def test_complete_preparation_and_separate_integer_worker(artifact, prepared):
    cycle, core = artifact["cycle"], prepared["core"]
    audit = runner.prepared_audit(PREPARED, prepared)
    assert audit == cycle["prepared_audit"] and audit["passed"]
    replay = runner.replay_audit(REPLAY, PREPARED, prepared, artifact)
    assert replay == cycle["independent_replay"] and replay["passed"]
    assert replay["worker_process_id"] != prepared["process_id"]
    assert core["size"] == 65 and core["real_coordinates"] == 104
    assert core["selection"] == runner.previous.selection()
    assert [(r["ordinal"], r["input"]) for r in core["records"]] == [
        (o, variant) for o in core["selection"]["ordinals"] for variant in ("raw", "paired")
    ]
    assert len(core["records"]) == 648
    assert q012a._digest(core["records"]) == core["records_digest_sha256"]
    assert core["quadratic_rebuild_equal"]
    assert all(r["reconstruction"]["passed"] for r in core["records"])
    assert all(all(r["reconstruction"]["checks"].values()) for r in core["records"])
    assert core["controls"] == exact.known_controls()
    assert _all_numeric_values_finite(prepared)


def test_all_3888_npz_entries_are_nonpickled_finite_and_byte_sealed(prepared):
    core = prepared["core"]
    archive = core["array_archive"]
    path = PREPARED.parent / archive["filename"]
    assert sha256(path.read_bytes()).hexdigest() == archive["sha256"]
    assert path.stat().st_size == archive["bytes"]
    keys = [key for row in core["records"] for key in row["array_keys"].values()]
    assert len(keys) == len(set(keys)) == len(archive["entries"]) == 3888
    with np.load(path, allow_pickle=False) as saved:
        assert set(saved.files) == set(keys)
        for key in keys:
            value = saved[key]
            assert value.dtype == np.dtype("complex128")
            assert np.all(np.isfinite(value))
            assert chart.array_metadata(value) == archive["entries"][key]


def fraction(pair):
    return Fraction(int(pair[0]), int(pair[1]))


@pytest.mark.parametrize("variant,count", [("raw", 20), ("paired", 17)])
def test_exact_inequalities_keep_all_legacy_failures(variant, count, prepared, artifact):
    rows = [r for r in prepared["core"]["records"] if r["input"] == variant]
    old = runner.read_json(runner.PRIOR_PATH)
    meta = next(g for g in old["cycle"]["grids"] if g["size"] == 65)
    prior = runner.previous.previous.read_records(PATH.parent / meta["record_archive"]["filename"])
    expected_failed = [
        r["ordinal"]
        for r in prior
        if r["inputs"][variant]["solvers"]["refined"]["external_relative_residual"] > 1e-10
    ]
    tolerance2 = Fraction.from_float(1e-10) ** 2
    floor2 = Fraction.from_float(1e-14) ** 2
    for row in rows:
        proof = row["proof"]
        norms = {key: fraction(value) for key, value in proof["norms_squared"].items()}
        assert all(value >= 0 for value in norms.values())
        stored2 = Fraction.from_float(row["stored_denominator"]) ** 2
        exact2 = max(floor2, norms["forcing_norm_squared"])
        decimal2 = max(Fraction(1, 10**28), norms["forcing_norm_squared"])
        assert stored2 == fraction(proof["stored_denominator_squared"])
        assert exact2 == fraction(proof["exact_denominator_squared"])
        assert decimal2 == fraction(proof["decimal_denominator_squared"])
        assert tolerance2 == fraction(proof["binary_tolerance_squared"])
        rr = norms["exact_residual_norm_squared"]
        gates = {
            "legacy": proof["legacy_relative_residual"] <= 1e-10,
            "rounded_vector_exact_norm": norms["rounded_residual_norm_squared"]
            <= tolerance2 * stored2,
            "exact_residual_stored_denominator": rr <= tolerance2 * stored2,
            "exact_residual_exact_denominator": rr <= tolerance2 * exact2,
            "exact_decimal_constants": rr <= Fraction(1, 10**20) * decimal2,
        }
        assert gates == proof["gates"]
        assert all(gates[k] for k in exact.EXACT_GATES)
        assert gates["legacy"] == row["prior_legacy_gate"] == gates["rounded_vector_exact_norm"]
        assert proof["evaluation_only_mismatch"] == (row["ordinal"] in expected_failed)
        assert proof["mp128_agrees"] == (
            norms["evaluation128_error_squared"] <= Fraction(1, 10**48) * exact2
        )
        assert proof["mp128_agrees"]
    observed = [r["ordinal"] for r in rows if r["proof"]["evaluation_only_mismatch"]]
    assert observed == expected_failed and len(observed) == count
    assert artifact["cycle"]["summary"][variant]["evaluation_only_mismatch_ordinals"] == observed


@pytest.mark.parametrize("variant", ["raw", "paired"])
def test_fresh_integer_arithmetic_for_all_saved_cases(variant, prepared):
    core = prepared["core"]
    with np.load(PREPARED.parent / core["array_archive"]["filename"], allow_pickle=False) as saved:
        rows = [r for r in core["records"] if r["input"] == variant]
        assert len(rows) == 324
        for row in rows:
            arrays = [saved[row["array_keys"][k]] for k in exact.ARRAY_NAMES]
            assert exact.audit_integer(*arrays, row["stored_denominator"]) == row["proof"]


def test_fresh_worst_exact_case_for_both_inputs(artifact, prepared):
    models, rebuild = runner.previous.build_inputs(65)
    assert q012a._digest(rebuild) == prepared["core"]["quadratic_rebuild_digest"]
    old = runner.read_json(runner.PRIOR_PATH)
    meta = next(g for g in old["cycle"]["grids"] if g["size"] == 65)
    prior = runner.previous.previous.read_records(PATH.parent / meta["record_archive"]["filename"])
    prior = {r["ordinal"]: r for r in prior}
    for variant in ("raw", "paired"):
        row = artifact["cycle"]["summary"][variant]["worst_exact_case"]
        arrays, denominator, audit = runner.rebuild_case(
            cubic.build_context(models[variant]),
            row["ordinal"],
            prior[row["ordinal"]]["inputs"][variant],
        )
        assert audit == row["reconstruction"] and audit["passed"]
        assert denominator == row["stored_denominator"]
        assert all(
            chart.array_metadata(value)
            == prepared["core"]["array_archive"]["entries"][row["array_keys"][key]]
            for key, value in arrays.items()
        )
        assert exact.audit_gmp(*(arrays[k] for k in exact.ARRAY_NAMES), denominator) == row["proof"]


def test_full_seal_summary_and_decision_recomputed(artifact, prepared):
    result = runner.seal(PREPARED, REPLAY)
    assert result["cycle"] == artifact["cycle"]
    assert result["cycle"]["summary"] == runner.summarize(prepared["core"]["records"])
    assert all(result["cycle"]["validity_gates"].values())
    assert all(result["cycle"]["hypothesis_gates"].values())
    assert result["study_gate"] == "passed" and result["scientific_outcome"] == "accepted"
    failed = set().union(
        *(set(s["evaluation_only_mismatch_ordinals"]) for s in result["cycle"]["summary"].values())
    )
    assert len(failed) == 32


def test_changed_source_and_entry_metadata_are_not_accepted(prepared):
    changed = deepcopy(prepared)
    changed["runner_source"]["sha256"] = "0" * 64
    assert not runner.prepared_audit(PREPARED, changed)["passed"]
    changed = deepcopy(prepared)
    entry = next(iter(changed["core"]["array_archive"]["entries"].values()))
    entry["sha256"] = "0" * 64
    checks = runner.prepared_audit(PREPARED, changed)["checks"]
    assert not checks["core_digest"] and not checks["npz_entries"]


@pytest.mark.parametrize("change", ["missing_case", "same_process"])
def test_incomplete_or_same_process_replay_is_not_accepted(change, prepared, artifact, tmp_path):
    worker = runner.read_json(REPLAY)
    if change == "missing_case":
        worker["evidence"]["records"].pop()
        worker["evidence_digest_sha256"] = q012a._digest(worker["evidence"])
    else:
        worker["process_id"] = prepared["process_id"]
    path = tmp_path / "changed.json"
    runner.write_json(path, worker)
    result = runner.replay_audit(path, PREPARED, prepared, artifact)
    assert not result["passed"]
    assert not result["checks"][
        "all_648_proofs_equal" if change == "missing_case" else "separate_process"
    ]


def test_invalid_preparation_stops_integer_worker(monkeypatch):
    monkeypatch.setattr(runner, "prepared_audit", lambda *_: {"passed": False})
    with pytest.raises(ValueError, match="not started"):
        runner.integer_worker(PREPARED)
