"""Registration, resolution, persistence, and replay tests using synthetic records."""

from copy import deepcopy
from dataclasses import dataclass
from types import SimpleNamespace

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_chart as quadratic
from research import d3q27_cubic_chart as chart
from research import q012g_d3q27_cubic_chart as runner


def test_exact_preregistered_schedule_and_worker_subset():
    main = list(runner.case_specifications())
    worker = list(runner.case_specifications(worker=True))
    assert len(main) == 416 and len(worker) == 48
    assert {
        kind: sum(r["kind"] == kind for r in main) for kind in ("order", "special", "amplitude")
    } == {
        "order": 256,
        "special": 96,
        "amplitude": 64,
    }
    assert worker == [
        r for r in main if r["kind"] in ("order", "amplitude") and r["direction_index"] < 8
    ]
    assert 3 * len(worker) == 144
    assert len({tuple(r["a"]) for r in main}) == len(main)
    for row in main:
        np.testing.assert_allclose(np.linalg.norm(row["a"]), row["amplitude"], rtol=3e-16)
    assert runner.coverage({"records": main}, worker=False)
    assert not runner.coverage({"records": main[::-1]}, worker=False)
    damaged = deepcopy(main)
    damaged[0]["a"][0] += 1e-10
    assert not runner.coverage({"records": damaged}, worker=False)


class AnalyticCaseModel:
    """NOT the D3Q27 candidate: a conservative scalar test for runner bookkeeping."""

    def __init__(self):
        self.quadratic = SimpleNamespace(size=1, base=d3.WEIGHTS.reshape(1, 1, 1, 27).copy())
        self.kinetic = np.zeros(27)
        self.kinetic[:3] = (1, -2, 1)  # Zero mass and all three zero momenta.

    def embed_with_audit(self, a, *, degree):
        value = self.quadratic.base + a[0] * self.kinetic
        return value, {"passed": True, "imaginary_norm": 0.0}

    def reduced_with_audit(self, a, *, degree):
        result = 0.5 * a.copy()
        result[0] += a[0] ** (degree + 1)
        return result, {"cubic_realification": None}


def test_full_map_case_records_both_models_and_conservation(monkeypatch):
    model = AnalyticCaseModel()
    monkeypatch.setattr(runner.physical, "map_step", lambda q, w: q.base + 0.5 * (w - q.base))
    a = np.zeros(104)
    a[0] = 0.001
    row = runner.physical_case(
        model, {"kind": "amplitude", "direction_index": 0, "amplitude": 0.001, "a": a.tolist()}
    )
    assert row["finite"] and row["resolved"] and row["amplitude_passed"]
    assert abs(row["cubic_to_quadratic_defect_ratio"] - 0.001) < 2e-9
    for degree in (2, 3):
        measured = row["models"][str(degree)]
        assert measured["status"] == "computed" and measured["positive"]
        assert set(measured["fields"]) == {"W", "Phi_W", "W_R"}
        assert measured["maximum_site_average_conservation_error"] <= 5e-13
        np.testing.assert_allclose(
            measured["defect_norm"], np.sqrt(6) * 0.001 ** (degree + 1), rtol=3e-6
        )
        assert measured["fields"]["W"]["perturbation_norm"] != row["amplitude"]
        assert all(len(value["array"]["sha256"]) == 64 for value in measured["fields"].values())


def test_floor_and_exceptions_are_not_replaced_by_zero_success(monkeypatch):
    model = AnalyticCaseModel()
    monkeypatch.setattr(runner.physical, "map_step", lambda q, w: q.base + 0.5 * (w - q.base))
    spec = {
        "kind": "amplitude",
        "direction_index": 0,
        "amplitude": 0.0,
        "a": np.zeros(104).tolist(),
    }
    zero = runner.physical_case(model, spec)
    assert zero["finite"] and not zero["resolved"] and not zero["amplitude_passed"]
    assert zero["cubic_to_quadratic_defect_ratio"] is None

    def fail(q, w):
        raise ValueError("intentional full-map failure")

    monkeypatch.setattr(runner.physical, "map_step", fail)
    row = runner.physical_case(model, spec)
    assert not row["finite"] and not row["resolved"]
    for data in row["models"].values():
        assert data["status"] == "error" and data["error"] == "intentional full-map failure"
        assert "defect_norm" not in data


def synthetic_records():
    result = []
    for spec in runner.case_specifications():
        t = spec["amplitude"]
        result.append(
            {
                **spec,
                "finite": True,
                "resolved": True,
                "roundoff_floor": 1e-30,
                "models": {str(d): {"defect_norm": t ** (d + 1)} for d in (2, 3)},
                "cubic_to_quadratic_defect_ratio": t,
                "amplitude_passed": True if spec["kind"] == "amplitude" else None,
            }
        )
    return result


def test_orders_preserve_all_directions_and_withhold_unresolved_special_slopes():
    records = synthetic_records()
    fits = runner.fits(records)
    assert len(fits) == 64 and all(r["passed"] for r in fits)
    assert all(
        abs(r["slopes"]["2"] - 3) < 1e-12 and abs(r["slopes"]["3"] - 4) < 1e-12 for r in fits
    )
    special = runner.fits(records, special=True)
    assert len(special) == 24 and all(r["passed"] is None for r in special)
    records[0]["resolved"] = False
    fits = runner.fits(records)
    assert fits[0]["slopes"] == {"2": None, "3": None} and not fits[0]["passed"]
    special_row = next(r for r in records if r["kind"] == "special")
    special_row["resolved"] = False
    assert runner.fits(records, special=True)[0]["slopes"] == {"2": None, "3": None}
    assert not runner.fits(records[1:])[0]["complete"]


def synthetic_diagnostics():
    generic = quadratic.normalized_directions(chart.EVALUATION_SEED, 8).tolist()
    repeated = {
        "status": "computed",
        "passed": True,
        "seed": chart.EVALUATION_SEED,
        "directions": generic,
        "records": [{"direction_index": i} for i in range(8)],
    }
    return {
        "evaluation": deepcopy(repeated),
        "physical_structure": {
            **deepcopy(repeated),
            "structure_passed": True,
            "physics_passed": True,
        },
        "homogeneity": {
            "status": "computed",
            "passed": True,
            "seed": chart.EVALUATION_SEED,
            "generic_directions": generic,
            "records": [
                {"kind": k, "direction_index": i}
                for k, count in (("generic", 8), ("coordinate_axis", 104))
                for i in range(count)
            ],
        },
        "symmetry": {
            "status": "computed",
            "passed": True,
            "seed": runner.SYMMETRY_SEED,
            "directions": quadratic.normalized_directions(runner.SYMMETRY_SEED, 4).tolist(),
            "records": [
                {"direction_index": i, "rotation_index": j, "rotation": r.tolist()}
                for i in range(4)
                for j, r in enumerate(d3.cubic_symmetries())
            ],
        },
        "timing": {
            "status": "computed",
            "valid": True,
            "seed": runner.COST_SEED,
            "amplitude": 0.008,
            "directions": quadratic.normalized_directions(runner.COST_SEED, 8).tolist(),
            "warmups": [
                {"repetition": r, "method": method} for r in range(3) for method in runner.METHODS
            ],
            "records": [
                {"repetition": r, "direction_index": i, "method": method}
                for r in range(11)
                for i in range(8)
                for method in (runner.METHODS if r % 2 == 0 else runner.METHODS[::-1])
            ],
        },
    }


def synthetic_grids():
    records = synthetic_records()
    return [
        {
            "size": n,
            "input_rebuild": {"passed": True},
            "fiber_load": {"passed": True},
            "records": deepcopy(records),
            "roundtrip_passed": True,
            **synthetic_diagnostics(),
            "generic_fits": runner.fits(records),
            "special_fits": runner.fits(records, special=True),
        }
        for n in (17, 33, 65)
    ]


def test_synthetic_decision_has_a_fully_exercised_acceptance_path():
    grids = synthetic_grids()
    validity, hypotheses, resolved, outcome = runner.decision(
        {"passed": True}, {"passed": True}, grids, {"passed": True}, True
    )
    assert (
        all(validity.values()) and all(hypotheses.values()) and resolved and outcome == "accepted"
    )
    grids[2]["symmetry"]["passed"] = False
    validity, hypotheses, resolved, outcome = runner.decision(
        {"passed": True}, {"passed": True}, grids, {"passed": True}, True
    )
    assert all(validity.values()) and resolved and outcome == "rejected"
    assert not hypotheses["H2_all_48_cubic_symmetries"]


@pytest.mark.parametrize(
    "mutation",
    (
        "missing_case",
        "missing_symmetry",
        "missing_axis",
        "missing_timing",
        "unresolved",
        "stale_fit",
        "nonfinite",
        "failed_roundtrip",
        "failed_source",
        "failed_replay",
    ),
)
def test_missing_and_unresolved_evidence_cannot_certify_the_study(mutation):
    grids = synthetic_grids()
    replay, source = {"passed": True}, True
    if mutation == "missing_case":
        grids[0]["records"].pop()
    elif mutation == "missing_symmetry":
        grids[0]["symmetry"]["records"].pop()
    elif mutation == "missing_axis":
        grids[0]["homogeneity"]["records"].pop()
    elif mutation == "missing_timing":
        grids[0]["timing"]["records"].pop()
    elif mutation == "unresolved":
        grids[0]["records"][0]["resolved"] = False
        grids[0]["generic_fits"] = runner.fits(grids[0]["records"])
    elif mutation == "stale_fit":
        grids[0]["generic_fits"][0]["slopes"]["3"] = 4.01
    elif mutation == "nonfinite":
        grids[0]["records"][0]["unrelated_numeric_evidence"] = np.nan
    elif mutation == "failed_roundtrip":
        grids[0]["roundtrip_passed"] = False
    elif mutation == "failed_source":
        source = False
    else:
        replay["passed"] = False
    _, _, _, outcome = runner.decision({"passed": True}, {"passed": True}, grids, replay, source)
    assert outcome == "inconclusive"


def test_replay_compares_every_selected_value_and_does_not_accept_missing_rows(tmp_path):
    grids, current = synthetic_grids(), runner.metadata()
    worker_grids = []
    for grid in grids:
        rows = [
            r
            for r in grid["records"]
            if r["kind"] in ("order", "amplitude") and r["direction_index"] < 8
        ]
        worker_grids.append(
            {
                "size": grid["size"],
                "input_rebuild": grid["input_rebuild"],
                "fiber_load": grid["fiber_load"],
                "records": rows,
            }
        )
    evidence = {
        "input_audit": {"passed": True},
        "controls": {"passed": True},
        "grids": worker_grids,
    }

    def saved_document(core):
        return {
            **current,
            "process_id": current["process_id"] + 1,
            "kind": "Q012g independent 144-case full-map worker",
            "evidence": core,
            "evidence_digest_sha256": runner.foundation._digest(core),
            "source_unchanged_after": True,
        }

    path = tmp_path / "worker.json"
    runner.prior.previous.write_json(path, saved_document(evidence))
    assert runner.worker_readiness(
        saved_document(evidence), current, {"passed": True}, {"passed": True}
    )
    assert runner.replay_audit(path, {"passed": True}, {"passed": True}, grids, current)["passed"]
    # Rehashing deliberately corrupted output must not repair a missing witness.
    missing = deepcopy(evidence)
    missing["grids"][2]["records"].pop()
    assert not runner.worker_readiness(
        saved_document(missing), current, {"passed": True}, {"passed": True}
    )
    missing_path = tmp_path / "missing.json"
    runner.prior.previous.write_json(missing_path, saved_document(missing))
    audit = runner.replay_audit(missing_path, {"passed": True}, {"passed": True}, grids, current)
    assert not audit["passed"] and not audit["checks"]["complete_144_cases"]
    changed = deepcopy(evidence)
    changed["grids"][0]["records"][0]["models"]["3"]["defect_norm"] *= 1.0001
    changed_path = tmp_path / "changed.json"
    runner.prior.previous.write_json(changed_path, saved_document(changed))
    audit = runner.replay_audit(changed_path, {"passed": True}, {"passed": True}, grids, current)
    assert audit["checks"]["complete_144_cases"] and not audit["passed"]


def test_grid_persistence_is_full_roundtrip_and_never_overwrites(tmp_path):
    path = tmp_path / "grid.json"
    grid = synthetic_grids()[0]
    metadata = runner.write_grid(path, grid, runner.metadata())
    restored = runner.prior.read_json(path)
    assert metadata["roundtrip_passed"] and restored["grid"] == grid
    assert restored["grid_digest_sha256"] == runner.foundation._digest(grid)
    with pytest.raises(FileExistsError):
        runner.write_grid(path, {"size": 65}, runner.metadata())


def test_all_timing_calls_and_order_are_registered_without_using_them_as_a_speed_gate(monkeypatch):
    calls = []

    class Fake:
        quadratic = SimpleNamespace(size=17)

        def embed(self, a):
            return a.copy()

    def fake_call(model, method, a, phi_input):
        calls.append(method)
        return a.copy()

    monkeypatch.setattr(runner, "timed_call", fake_call)
    result = runner.timing_study(Fake())
    assert result["valid"] and len(result["warmups"]) == 15 and len(result["records"]) == 440
    assert len(calls) == 455 and all(r["same_output"] for r in result["records"])
    diagnostic = synthetic_diagnostics()
    diagnostic["timing"] = {"status": "computed", **result}
    assert runner.diagnostic_coverage(diagnostic)
    assert set(result["median_wall_seconds"]) == set(runner.METHODS)


def test_reachable_numpy_buffers_are_deduplicated_without_claiming_total_RSS():
    @dataclass
    class QuadraticBuffers:
        values: np.ndarray
        view: np.ndarray

    raw = np.arange(12, dtype=float)
    q = QuadraticBuffers(raw, raw[::2])
    model = object.__new__(chart.CubicChart)
    model.quadratic = q
    model.waves = np.ones((3, 3), dtype=np.int64)
    inventory = runner.buffer_inventory(model, {"same": raw[:6]})
    assert inventory["bytes"] == raw.nbytes + model.waves.nbytes
    assert inventory["unique_buffers"] == 2
    assert inventory["groups"]["original_cubic_archives"]["bytes_added"] == 0


def test_partial_diagnostic_rows_and_failure_location_are_retained():
    def evaluation_controls():
        records = [{"direction_index": i, "passed": True} for i in range(2)]
        index = len(records)
        raise ValueError(f"intentional failure in direction {index}")

    result = runner.guarded(evaluation_controls)
    assert result["status"] == "error" and result["phase"] == "evaluation_controls"
    assert result["failed_context"] == {"index": 2}
    assert len(result["partial_records"]) == 2 and result["partial_records_finite"]
    assert "passed" not in result


def test_new_runner_preserves_all_old_seals_and_retains_nontrivial_controls():
    audit = runner.input_audit()
    assert audit["passed"] and len(audit["archives"]) == 3
    assert audit["replay"]["passed"]
    controls = runner.controls()
    assert controls["passed"]
    assert controls["results"]["manufactured_graph_evaluation"]["passed"]
    assert controls["results"]["retained_homological_controls"]["passed"]
