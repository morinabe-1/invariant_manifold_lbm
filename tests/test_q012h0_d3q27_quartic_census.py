"""Q012h0 runner controls, including a full-scope temporary subprocess run."""

import json
import os
import subprocess
import sys
from copy import deepcopy
from itertools import product

import pytest

from research import q012h0_d3q27_quartic_census as r


def reseal(document):
    return r.sealed({k: v for k, v in document.items() if k != "sha256"})


@pytest.fixture(scope="module")
def complete(tmp_path_factory):
    output = tmp_path_factory.mktemp("q012h0-full-controls") / "census.json"
    process = subprocess.Popen(
        [sys.executable, "-W", "error", "-m", r.MODULE, "--output", str(output)],
        cwd=r.ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
    )
    stdout, stderr = process.communicate()
    assert process.returncode == 0, (stdout, stderr)
    assert stderr == ""
    saved = r.read_json(output)
    primary = r.read_json(r.child_path(output, "enumeration"))
    worker = r.read_json(r.child_path(output, "generating_functions"))
    receipt = json.loads(stdout)
    assert receipt["sha256"] == r.prior._file_sha256(output)
    assert receipt["decision"] == saved["decision"]
    assert primary["process_id"] == process.pid != worker["process_id"]
    assert worker["process_id"] == saved["worker_execution"]["process_id"]
    return output, saved, primary, worker


def test_registered_inventory_and_input_are_not_narrowed():
    config = r.config()
    assert config["sizes"] == [17, 33, 65] and config["degrees"] == [2, 3, 4]
    assert (config["omega"], config["eta"], config["power"]) == (1.5, 0.02, 2)
    rows = r.expected_inventory()
    assert len(rows) == config["block_count"] == 78
    assert sum(row["dimension"] for row in rows) == config["coordinate_count"] == 104
    waves = [wave for wave in product((-1, 0, 1), repeat=3) if any(wave)]
    assert {tuple(row["wave"]) for row in rows} == set(waves)
    for wave in waves:
        assert [(row["label"], row["dimension"]) for row in rows if tuple(row["wave"]) == wave] == [
            ("shear", 2),
            ("acoustic_plus", 1),
            ("acoustic_minus", 1),
        ]
    source, parent = r.metadata(), r.input_state()
    assert source["prior_source_sha256"] == parent["source_sha256"] == r.PRIOR_SOURCE_SHA
    assert parent["sha256"] == r.PARENT_SHA
    assert parent["decision"]["scientific_outcome"] == "accepted"


@pytest.mark.parametrize("constant", ("PARENT_SHA", "PRIOR_SOURCE_SHA"))
def test_changed_source_or_parent_seal_is_rejected(monkeypatch, constant):
    monkeypatch.setattr(r, constant, "0" * 64)
    with pytest.raises(ValueError):
        r.input_state() if constant == "PARENT_SHA" else r.metadata()


def test_fresh_frame_cannot_silently_drop_a_wave(monkeypatch):
    original = r.chart.paired_frames

    def missing(size, omega):
        frames, audit = original(size, omega)
        frames.pop(next(iter(frames)))
        return frames, audit

    monkeypatch.setattr(r.chart, "paired_frames", missing)
    with pytest.raises(ValueError, match="inventory"):
        r.fresh_frames()


def test_exact_json_types_and_exclusive_writes(tmp_path):
    assert not r.same({"n": 1}, {"n": 1.0})
    assert not r.same({"n": 1}, {"n": True})
    path = tmp_path / "data.json"
    saved = r.sealed({"numbers": [2, 3, 4], "scope": r.BOUNDARY})
    r.save_exclusive(path, saved)
    original = path.read_bytes()
    assert r.unseal(r.read_json(path))["numbers"] == [2, 3, 4]
    with pytest.raises(FileExistsError):
        r.save_exclusive(path, {"changed": True})
    assert path.read_bytes() == original


@pytest.mark.parametrize("text", ('{"a": 1, "a": 2}', '{"a": NaN}', '{"a": Infinity}'))
def test_ambiguous_or_nonfinite_json_is_rejected(tmp_path, text):
    path = tmp_path / "bad.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        r.read_json(path)


def test_full_scope_run_and_independent_saved_readback(complete):
    output, saved, primary, worker = complete
    decision = r.audit_manifest(output)
    assert decision == saved["decision"]
    assert decision["study_gate"] == "passed" and decision["scientific_outcome"] == "accepted"
    assert all(decision["validity_gates"].values()) and all(decision["hypothesis_gates"].values())
    assert saved["controls"]["passed_tests"] == 127 and saved["controls"]["exit_code"] == 0
    assert saved["worker_execution"]["exit_code"] == 0
    assert saved["process_id"] != os.getpid()
    assert len(saved["comparisons"]) == 3
    for route in (primary, worker):
        assert [frame["size"] for frame in route["frames"]] == [17, 33, 65]
        assert all(frame["audit"]["passed"] for frame in route["frames"])
        assert [row["degree"] for row in route["degrees"]] == [2, 3, 4]
        assert [
            (row["coverage"]["block_tuples"], row["coverage"]["coordinate_columns"])
            for row in route["degrees"][:2]
        ] == [(3081, 5460), (82160, 192920)]
        assert all(
            grid["payload"]["full_solver_resource_feasibility"] is None
            for row in route["degrees"]
            for grid in row["grids"]
        )
        assert "no quartic coefficients" in route["scope"]


@pytest.mark.parametrize(
    "damage",
    (
        "scope",
        "config",
        "source",
        "input",
        "inventory",
        "frame",
        "degree",
        "pid",
        "time",
        "coverage",
        "payload_type",
        "payload_value",
        "sector",
        "total",
        "joint",
        "coordinate",
    ),
)
def test_route_damage_is_rejected_even_after_resealing(complete, damage):
    _, _, primary, _ = complete
    changed = deepcopy(primary)
    if damage == "scope":
        changed["scope"] = "quartic solver certified"
    elif damage == "config":
        changed["config"]["sizes"][0] = 17.0
    elif damage == "source":
        changed["source_after"]["prior_source_sha256"] = "0" * 64
    elif damage == "input":
        changed["input_after"]["sha256"] = "0" * 64
    elif damage == "inventory":
        changed["inventory"].pop()
    elif damage == "frame":
        changed["frames"][0]["audit"]["passed"] = 1
    elif damage == "degree":
        changed["degrees"] = changed["degrees"][:2]
    elif damage == "pid":
        changed["process_id"] = True
    elif damage == "time":
        changed["census_wall_seconds"] = -1.0
    elif damage == "coverage":
        changed["degrees"][0]["coverage"]["coordinate_columns"] += 1
    elif damage.startswith("payload"):
        payload = changed["degrees"][0]["grids"][0]["payload"]
        value = payload["sparse_payload_bytes"]
        payload["sparse_payload_bytes"] = float(value) if damage == "payload_type" else value + 1
    elif damage == "sector":
        changed["degrees"][0]["grids"][0]["sectors"]["sectors"][0]["external_dimension"] = 27
    elif damage == "total":
        changed["degrees"][0]["all_three_grids_sparse_payload_bytes"] += 1
    elif damage == "joint":
        changed["degrees"][0]["joint"][0]["blocks"] += 1
    else:
        changed["degrees"][0]["coordinates"][0]["columns"] += 1
    with pytest.raises(ValueError):
        r.audit_route(reseal(changed), "enumeration")


def test_self_consistent_wave_forgery_requires_full_histogram_recomputation(complete):
    _, _, primary, _ = complete
    changed = deepcopy(primary)
    row = changed["degrees"][0]
    joint = r.census.parse_joint(row["joint"])
    key = max(joint)
    count = joint.pop(key)
    joint[(key[0] + 1, key[1], key[2], key[3])] = count
    blocks = r.census.restore_inventory(changed["inventory"])
    rebuilt = r.degree_record(blocks, 2, joint, r.census.weighted_coordinates(joint))
    assert rebuilt["coverage"]["passed"]
    changed["degrees"][0] = rebuilt
    with pytest.raises(ValueError, match="recomputed histogram"):
        r.audit_route(reseal(changed), "enumeration")


@pytest.mark.parametrize("damage", ("controls", "pid", "exit", "coverage", "audits"))
def test_invalid_execution_is_inconclusive_not_a_scientific_success(complete, damage):
    _, saved, primary, worker = complete
    p, w = deepcopy(primary), deepcopy(worker)
    control, execution, audits = (
        deepcopy(saved[k]) for k in ("controls", "worker_execution", "readback_audits")
    )
    if damage == "controls":
        control["passed_tests"] = 126
    elif damage == "pid":
        execution["process_id"] = w["process_id"] = p["process_id"]
    elif damage == "exit":
        execution["exit_code"] = 1
    elif damage == "coverage":
        p["degrees"][0]["coverage"]["passed"] = False
    else:
        audits = {}
    outcome = r.decision(p, w, control, execution, audits)
    assert outcome["study_gate"] == "failed" and outcome["scientific_outcome"] == "inconclusive"


def test_method_disagreement_is_a_scientific_rejection(complete):
    _, saved, primary, worker = complete
    changed = deepcopy(worker)
    changed["degrees"][0]["joint"][-1]["wave"][0] += 1
    outcome = r.decision(
        primary, changed, saved["controls"], saved["worker_execution"], saved["readback_audits"]
    )
    assert outcome["study_gate"] == "passed" and outcome["scientific_outcome"] == "rejected"
    assert not outcome["hypothesis_gates"]["H1"]


def test_no_vacuous_comparison(complete):
    _, _, primary, worker = complete
    p, w = deepcopy(primary), deepcopy(worker)
    p["degrees"] = w["degrees"] = []
    with pytest.raises(ValueError):
        r.comparisons(p, w)


def test_existing_outputs_are_not_reused_or_overwritten(complete, monkeypatch):
    output, _, _, _ = complete
    originals = {path: path.read_bytes() for path in output.parent.glob("*.json")}
    monkeypatch.setattr(
        r, "spawn_worker", lambda *args: pytest.fail("existing output triggered a worker")
    )
    with pytest.raises(ValueError, match="existing output"):
        r.execute(output)
    assert originals == {path: path.read_bytes() for path in output.parent.glob("*.json")}


@pytest.mark.parametrize("stage", ("controls", "worker"))
def test_failed_execution_is_preserved_and_cannot_be_restarted_in_place(
    tmp_path, monkeypatch, complete, stage
):
    _, saved, _, _ = complete
    output = tmp_path / "failed.json"
    control = deepcopy(saved["controls"])
    if stage == "controls":
        control["exit_code"] = 1
        control["stderr"] = "manufactured control failure"
    monkeypatch.setattr(r, "controls", lambda: control)
    monkeypatch.setattr(
        r,
        "spawn_worker",
        lambda path: {
            "process_id": 123,
            "exit_code": 9,
            "stdout": "",
            "stderr": "manufactured worker failure",
            "module": r.MODULE,
        },
    )
    with pytest.raises(ValueError):
        r.execute(output)
    failure_path = output.with_name(output.stem + "_failure.json")
    failure = r.read_json(failure_path)
    assert r.unseal(failure)["decision"] == {
        "study_gate": "failed",
        "scientific_outcome": "inconclusive",
    }
    assert failure["controls"] == control
    assert not output.exists()
    checksum = r.prior._file_sha256(failure_path)
    with pytest.raises(ValueError, match="existing output"):
        r.execute(output)
    assert r.prior._file_sha256(failure_path) == checksum


def test_manifest_damage_is_rejected_before_any_positive_report(tmp_path, complete):
    _, saved, _, _ = complete
    path = tmp_path / "changed.json"
    altered = deepcopy(saved)
    altered["summary"][0]["coverage"]["block_tuples"] += 1
    r.save_exclusive(path, altered)
    with pytest.raises(ValueError, match="seal"):
        r.audit_manifest(path)
    # Even a syntactically valid manifest must not ignore a failure sidecar.
    marker = path.with_name(path.stem + "_failure.json")
    r.save_exclusive(marker, {"failed": True})
    with pytest.raises(ValueError, match="failure marker"):
        r.audit_manifest(path)
