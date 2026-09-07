"""Execution plumbing with explicitly synthetic 7/9/11 grids and two coordinates.

No registered 17/33/65 chart is constructed here. Tests injecting inputs, norms,
process IDs or failures exercise the protocol, not independent physical evidence.
"""

from __future__ import annotations

import json
import subprocess
import sys
from copy import deepcopy

import pytest

from research import q012g3_d3q27_cubic_defect as runner
from tests import test_d3q27_defect_evidence as toy_evidence
from tests.test_d3q27_cubic_defect import ToyChart


@pytest.fixture(scope="module")
def worlds():
    result = {}
    with pytest.MonkeyPatch.context() as patch:
        for size in (7, 9, 11):
            patch.setattr(toy_evidence, "ToyChart", lambda n=size: ToyChart(n))
            source = toy_evidence.toy_rows.__wrapped__()
            originals = [r for kind in ("order", "amplitude") for r in source[kind][1].values()]
            conserved = [
                {
                    "specification": r["specification"],
                    "models": source["amplitude"][3][runner.evidence.case_key(r["specification"])][
                        "models"
                    ],
                }
                for r in source["amplitude"][0]["cases"]
            ]
            rebuilt = {"input_rebuild": {"passed": True}, "fiber_load": {"passed": True}}
            result[size] = {
                "old": {
                    "size": size,
                    **rebuilt,
                    "records": originals,
                    "generic_fits": [source["order"][2]],
                },
                "conserved": {"size": size, "records": conserved},
                "schedule": [source[k][0]["schedule"] for k in ("order", "amplitude")],
                "rebuilt": rebuilt,
                "source": source,
            }
    return result


@pytest.fixture
def world(worlds, monkeypatch):
    current = runner.metadata()
    current["process_id"] = 71001
    original_read = runner.read_json
    original_validate = runner.evidence.validate_direction
    old_grids = [worlds[s]["old"] for s in (7, 9, 11)]
    conserved_grids = [worlds[s]["conserved"] for s in (7, 9, 11)]
    inputs = {"passed": True, "synthetic_fixture": "not a physical input audit"}
    control = {
        "test_sources": runner.control_seals(),
        "exit_code": 0,
        "passed_tests": 177,
        "sources_unchanged": True,
        "passed": True,
    }

    def read(path):
        if path == runner.prior.PARENT_PATH:
            return {"cycle": {"grids": old_grids}}
        if path == runner.PRIOR_PATH:
            return {"evidence": {"grids": conserved_grids}}
        return original_read(path)

    def validate(*args, **kwargs):
        return original_validate(*args, **kwargs, dimension=2)

    def old_case(model, spec):
        return deepcopy(
            next(
                r
                for r in worlds[model.quadratic.size]["old"]["records"]
                if runner.evidence.case_key(r) == runner.evidence.case_key(spec)
            )
        )

    monkeypatch.setattr(runner, "SIZES", (7, 9, 11))
    monkeypatch.setattr(runner, "metadata", lambda: deepcopy(current))
    monkeypatch.setattr(runner, "input_audit", lambda: deepcopy(inputs))
    monkeypatch.setattr(
        runner,
        "controls",
        lambda: (deepcopy(control), {"stdout": "177 passed (synthetic fixture)", "stderr": ""}),
    )
    monkeypatch.setattr(runner, "read_json", read)
    monkeypatch.setattr(
        runner.evidence, "direction_schedule", lambda **kwargs: deepcopy(worlds[7]["schedule"])
    )
    monkeypatch.setattr(runner.evidence, "validate_direction", validate)
    monkeypatch.setattr(
        runner.parent,
        "fresh_model",
        lambda size: (
            ToyChart(size),
            {},
            deepcopy(worlds[size]["rebuilt"]),
            {"synthetic_input_seconds": 0.0},
        ),
    )
    monkeypatch.setattr(runner.parent, "physical_case", old_case)
    return {
        "worlds": worlds,
        "current": current,
        "inputs": inputs,
        "control": control,
        "old": old_grids,
        "conserved": conserved_grids,
    }


def audit(saved, path, world, *, worker):
    return runner.audit_document(saved, path, world["old"], world["conserved"], worker=worker)


@pytest.fixture
def completed_worker(world, tmp_path):
    path = tmp_path / "synthetic_worker.json"
    result, readback = runner.run(path, worker=True)
    assert readback["passed"]
    return path, result, readback


def test_full_synthetic_worker_primary_and_independent_fields(world, completed_worker):
    path, result, readback = completed_worker
    assert result["decision"]["study_gate"] == "passed"
    assert result["decision"]["scientific_outcome"] == "worker_only"
    assert readback["cases"] == 18 and readback["profiles"] == 12
    assert readback["independent_vector_comparisons"] == 438
    assert result["summary"]["counts"] == {"directions": 6, "cases": 18, "profiles": 12}
    assert not any(result["summary"]["failures"].values())
    assert audit(runner.read_json(path), path, world, worker=True) == readback


def test_full_synthetic_main_replays_primary_records_and_every_saved_child(
    world, completed_worker, tmp_path
):
    witness, _, _ = completed_worker
    world["current"]["process_id"] += (
        1  # Protocol fixture; formal execution uses real separate processes.
    )
    path = tmp_path / "synthetic_main.json"
    result, readback = runner.run(path, worker=False, replay_path=witness)
    assert readback["passed"] and result["decision"]["scientific_outcome"] == "accepted"
    assert result["independent_replay"]["passed"]
    assert all(
        r["all_primary_scientific_records_equal"]
        for r in result["independent_replay"]["main_correspondence"]
    )
    assert len(list(tmp_path.glob("synthetic_main_n*.json"))) == 9
    assert audit(runner.read_json(path), path, world, worker=False)["passed"]
    altered = deepcopy(result)
    altered["independent_replay"]["main_correspondence"][-1][
        "all_primary_scientific_records_equal"
    ] = False
    assert not audit(altered, path, world, worker=False)["passed"]


@pytest.mark.parametrize(
    "bad",
    [
        "same_process",
        "missing_replay",
        "worker_with_replay",
        "failed_worker",
        "different_directory",
    ],
)
def test_main_cannot_start_without_a_ready_separate_worker(
    world, completed_worker, tmp_path, monkeypatch, bad
):
    witness, result, _ = completed_worker

    def forbidden(*args, **kwargs):
        raise AssertionError("physical work started before readiness")

    monkeypatch.setattr(runner.parent, "fresh_model", forbidden)
    if bad == "failed_worker":
        result["decision"]["study_gate"] = "failed"
        witness.write_text(json.dumps(result), encoding="utf-8")
        world["current"]["process_id"] += 1
    with pytest.raises(ValueError):
        runner.run(
            tmp_path / "elsewhere" / "forbidden.json"
            if bad == "different_directory"
            else tmp_path / "forbidden.json",
            worker=bad == "worker_with_replay",
            replay_path=None if bad == "missing_replay" else witness,
        )


@pytest.mark.parametrize("bad", ["whole_record", "field", "defect", "exact_holdout", "direction"])
def test_original_mismatch_is_preserved_with_its_location(world, monkeypatch, bad):
    w = world["worlds"][7]
    kind = "amplitude" if bad == "exact_holdout" else "order"
    spec = deepcopy(next(s for s in w["schedule"] if s["kind"] == kind))
    originals, conserved, fits = runner.maps(w["old"], w["conserved"])
    originals, conserved = deepcopy(originals), deepcopy(conserved)
    if bad == "whole_record":
        originals[runner.evidence.case_key(spec["specifications"][0])]["finite"] = False
    elif bad in ("field", "defect"):
        original_fields = runner.original_fields

        def changed(model, s, degree, old):
            old = deepcopy(old)
            if bad == "field":
                old["fields"]["W_R"]["array"]["sha256"] = "0" * 64
            else:
                old["defect_array"]["sha256"] = "0" * 64
            return original_fields(model, s, degree, old)

        monkeypatch.setattr(runner, "original_fields", changed)
    elif bad == "exact_holdout":
        conserved[runner.evidence.case_key(spec["specifications"][0])]["models"]["2"]["fields"] = {}
    else:
        spec["direction"][-1] += 0.01
    row, _ = runner.diagnose_direction(
        ToyChart(), spec, originals, fits.get(3), conserved, worker=True
    )
    assert row["status"] == "error" and row["failure_location"]
    assert row["cases"] and row["cases"][0]["original"]


def test_primary_tail_buffers_are_released_only_after_all_primary_samples(world, monkeypatch):
    comparison, tail = runner.defect.compare_profiles, runner.defect.LocalExpansion.tail
    observed = []

    def compare(a, b):
        assert a.local.remainder == ()
        assert len(b.local.remainder) == 10 + b.degree
        observed.append(a.degree)
        return comparison(a, b)

    def evaluate_tail(self, *args, **kwargs):
        assert len(self.remainder) > 0
        return tail(self, *args, **kwargs)

    monkeypatch.setattr(runner.defect, "compare_profiles", compare)
    monkeypatch.setattr(runner.defect.LocalExpansion, "tail", evaluate_tail)
    w = world["worlds"][7]
    originals, conserved, fits = runner.maps(w["old"], w["conserved"])
    row, _ = runner.diagnose_direction(
        ToyChart(), w["schedule"][0], originals, fits[3], conserved, worker=True
    )
    assert row["status"] == "computed" and observed == [2, 3]


@pytest.mark.parametrize(
    "bad",
    [
        "last_grid",
        "last_direction",
        "last_case",
        "profile",
        "summary",
        "decision",
        "source",
        "input",
        "controls",
        "last_child",
        "direction_child",
    ],
)
def test_complete_saved_audit_rejects_omissions_and_end_of_artifact_damage(
    world, completed_worker, bad
):
    path, original, _ = completed_worker
    saved = deepcopy(original)
    if bad == "last_grid":
        saved["evidence"]["grids"].pop()
    elif bad == "last_direction":
        saved["evidence"]["grids"][-1]["directions"].pop()
    elif bad == "last_case":
        saved["evidence"]["grids"][-1]["directions"][-1]["cases"].pop()
    elif bad == "profile":
        saved["evidence"]["grids"][-1]["directions"][-1]["profiles"]["3"]["primary"]["local"][
            "remainder"
        ].pop()
    elif bad == "summary":
        saved["summary"]["counts"]["cases"] -= 1
    elif bad == "decision":
        saved["decision"]["scientific_outcome"] = "accepted"
    elif bad == "source":
        saved["runner_source"]["sha256"] = "0" * 64
    elif bad == "input":
        saved["input_audit_after"] = {"passed": True}
    elif bad == "controls":
        saved["evidence"]["controls"]["passed_tests"] = 176
    elif bad == "last_child":
        saved["grid_artifacts"][-1]["sha256"] = "0" * 64
    else:
        grid = saved["evidence"]["grids"][-1]
        child = runner.direction_path(path, grid["size"], grid["directions"][-1]["schedule"])
        value = runner.read_json(child)
        value["direction"]["cases"][-1]["models"]["3"]["samples"]["primary"]["tail_norm"] += 1
        child.write_text(json.dumps(value), encoding="utf-8")
    saved["evidence_digest_sha256"] = runner.digest(saved["evidence"])
    assert not audit(saved, path, world, worker=True)["passed"]


def test_existing_full_or_partial_outputs_are_never_overwritten(world, completed_worker, tmp_path):
    path, _, _ = completed_worker
    before = path.read_bytes()
    with pytest.raises(ValueError):
        runner.run(path, worker=True)
    assert path.read_bytes() == before
    output = tmp_path / "partial.json"
    child = runner.direction_path(output, 11, world["worlds"][11]["schedule"][-1])
    child.write_text("existing partial evidence", encoding="utf-8")
    with pytest.raises(ValueError):
        runner.run(output, worker=True)
    assert child.read_text(encoding="utf-8") == "existing partial evidence"
    with pytest.raises(FileExistsError):
        runner.save_new(child, {"replacement": True})


def test_partial_direction_failure_is_saved_and_campaign_is_inconclusive(
    world, tmp_path, monkeypatch
):
    original = runner.defect.build_profile

    def fail_on_cubic(model, u, degree, **kwargs):
        if model.quadratic.size == 11 and degree == 3:
            raise ValueError("synthetic late profile failure")
        return original(model, u, degree, **kwargs)

    monkeypatch.setattr(runner.defect, "build_profile", fail_on_cubic)
    path = tmp_path / "failed.json"
    result, readback = runner.run(path, worker=True)
    assert not readback["passed"] and result["decision"]["scientific_outcome"] == "inconclusive"
    assert len(result["summary"]["failures"]["incomplete"]) == 2
    row = result["evidence"]["grids"][-1]["directions"][-1]
    assert row["profiles"]["2"] and row["cases"][-1]["models"]["2"]
    assert row["failure_location"] == "degree=3/primary_profile"
    assert runner.direction_path(path, 11, row["schedule"]).exists()


def test_rejected_H2_is_scientific_failure_not_incomplete_evidence(world, tmp_path, monkeypatch):
    original = runner.defect.sample_diagnostics

    def inaccurate(profile, t, fields):
        value = original(profile, t, fields)
        value["P9_vector_difference_norm"] = 0.01 * value["raw_defect_norm"]
        value["P9_vector_relative_error"] = (
            value["P9_vector_difference_norm"] / value["raw_defect_norm"]
        )
        value["P9_vector_passed"] = False
        return value

    monkeypatch.setattr(runner.defect, "sample_diagnostics", inaccurate)
    witness = tmp_path / "bad_prediction_worker.json"
    worker, checked = runner.run(witness, worker=True)
    assert checked["passed"] and worker["decision"]["study_gate"] == "passed"
    assert not worker["decision"]["hypothesis_gates"]["H2"]
    world["current"]["process_id"] += 1
    result, checked = runner.run(
        tmp_path / "bad_prediction_main.json", worker=False, replay_path=witness
    )
    assert checked["passed"] and result["decision"]["study_gate"] == "passed"
    assert result["decision"]["scientific_outcome"] == "rejected"
    assert result["summary"]["failure_counts"]["H2"] == 6


def test_changed_inputs_after_physical_work_cannot_pass(world, tmp_path, monkeypatch):
    calls = []

    def changing():
        calls.append(1)
        return world["inputs"] if len(calls) == 1 else {"passed": True, "changed": True}

    monkeypatch.setattr(runner, "input_audit", changing)
    result, checked = runner.run(tmp_path / "changed_input.json", worker=True)
    assert not checked["passed"] and not result["inputs_unchanged_after"]
    assert result["decision"]["scientific_outcome"] == "inconclusive"


def test_nonfinite_failure_values_are_explicit_tags_not_zero_or_null():
    value = runner.nonfinite_tags(
        {"bad": [float("nan"), float("inf"), float("-inf")], "good": 0.125}
    )
    assert value == {
        "bad": [
            {"nonfinite_float": "nan"},
            {"nonfinite_float": "inf"},
            {"nonfinite_float": "-inf"},
        ],
        "good": 0.125,
    }
    json.dumps(value, allow_nan=False)


@pytest.mark.parametrize(
    "count,exit_code,passed", [(177, 0, True), (176, 0, False), (177, 1, False), (0, 0, False)]
)
def test_control_execution_requires_all_177_tests_and_success(
    monkeypatch, count, exit_code, passed
):
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *a, **k: subprocess.CompletedProcess(
            a[0], exit_code, stdout=f"{count} passed in 1s", stderr=""
        ),
    )
    control, raw = runner.controls()
    assert control["passed"] is passed and str(count) in raw["stdout"]


def test_execution_lock_is_held_by_os_and_released_after_exception(tmp_path):
    path = tmp_path / "execution.lock"
    script = "from pathlib import Path; from research.q012g3_d3q27_cubic_defect import execution_lock;\nwith execution_lock(Path(__import__('sys').argv[1])): print('acquired')"
    with pytest.raises(RuntimeError), runner.execution_lock(path):
        p = subprocess.run(
            [sys.executable, "-c", script, str(path)],
            cwd=runner.ROOT,
            capture_output=True,
            check=False,
        )
        assert p.returncode != 0
        raise RuntimeError("release the OS lock")
    p = subprocess.run(
        [sys.executable, "-c", script, str(path)], cwd=runner.ROOT, capture_output=True, check=False
    )
    assert p.returncode == 0 and b"acquired" in p.stdout


def test_frozen_real_inputs_are_still_accepted_without_building_a_new_chart():
    result = runner.input_audit()
    assert result["passed"] and all(result["checks"].values())
    assert result["conservation_saved_audit"]["cases"] == 192
    assert result["conservation_replay"]["passed"]
