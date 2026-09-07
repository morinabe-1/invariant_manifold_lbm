"""Synthetic campaign, persistence, tamper and serial-worker controls for Q012g1."""

from copy import deepcopy
from fractions import Fraction
from types import SimpleNamespace

import numpy as np
import pytest

from research import d3q27_conservation_audit as exact
from research import q012g1_d3q27_conservation as runner


class AnalyticCaseModel:
    """A tiny arithmetic control, NOT a nonzero-wave LBM candidate."""

    def __init__(self):
        self.quadratic = SimpleNamespace(
            size=1, base=runner.parent.d3.WEIGHTS.reshape(1, 1, 1, 27).copy()
        )
        self.kinetic = np.zeros(27)
        self.kinetic[:3] = (1, -2, 1)

    def embed_with_audit(self, a, *, degree):
        return self.quadratic.base + a[0] * self.kinetic, {"passed": True, "imaginary_norm": 0.0}

    def reduced_with_audit(self, a, *, degree):
        result = 0.5 * a.copy()
        result[0] += a[0] ** (degree + 1)
        return result, {"cubic_realification": None}

    def embed(self, a, *, degree):
        return self.embed_with_audit(a, degree=degree)[0]

    def reduced(self, a, *, degree):
        return self.reduced_with_audit(a, degree=degree)[0]


def test_exact_registered_full_scope_and_independent_subset():
    main, worker = runner.specifications(), runner.specifications(worker=True)
    assert len(main) == 64 and len(worker) == 16
    assert worker == [s for s in main if s["direction_index"] < 8]
    assert all(s["kind"] == "amplitude" for s in main)
    assert [(s["direction_index"], s["amplitude"]) for s in main] == [
        (i, a) for i in range(32) for a in (0.008, 0.032)
    ]
    assert len(main) * 3 * 6 == 1152 and len(main) * 3 * 24 == 4608
    assert len(worker) * 3 * 6 == 288 and len(worker) * 3 * 24 == 1152
    assert runner.SIZES == (17, 33, 65)


@pytest.fixture
def synthetic(monkeypatch):
    model = AnalyticCaseModel()
    monkeypatch.setattr(
        runner.parent.physical, "map_step", lambda q, w: q.base + 0.5 * (w - q.base)
    )
    specs = runner.specifications()[:2]
    originals = [runner.parent.physical_case(model, s) for s in specs]
    baseline = exact.baseline_record(model.quadratic.base, backend="integer")
    return model, specs, originals, baseline


def test_diagnosis_repeats_original_before_each_fresh_field_and_matches_both_backends(
    synthetic, monkeypatch
):
    model, specs, originals, baseline = synthetic
    original_case, regenerate = runner.parent.physical_case, runner.regenerate
    events = []

    def physical(m, spec):
        events.append("old_case")
        return original_case(m, spec)

    def fresh(m, a, degree, name):
        events.append((degree, name))
        return regenerate(m, a, degree, name)

    monkeypatch.setattr(runner.parent, "physical_case", physical)
    monkeypatch.setattr(runner, "regenerate", fresh)
    first = runner.diagnose_case(model, specs[0], originals[0], baseline, backend="integer")
    assert events == ["old_case"] + [(d, name) for d in (2, 3) for name in runner.FIELDS]
    second = runner.diagnose_case(model, specs[0], originals[0], baseline, backend="gmp")
    assert first == second and first["status"] == "computed"
    runner.validate_case(first, originals[0], baseline)
    for data in first["models"].values():
        assert set(data["fields"]) == {"W", "Phi_W", "W_R"}
        for name, components in data["comparisons"].items():
            assert len(components) == 4
            for c in components:
                terms = {k: exact.decode(v) for k, v in c["terms"].items()}
                total = (
                    terms["exact_field_error"]
                    + terms["sum_rounding_A"]
                    + terms["sum_rounding_minus_B"]
                    + terms["sub_rounding"]
                    + terms["mean_rounding"]
                )
                assert total == Fraction.from_float(c["legacy_site_average_error"])
                assert (c["base_only_counterfactual"] is None) == (name == "Phi_conservation")


def test_original_case_mismatch_prevents_any_explanatory_replacement(synthetic, monkeypatch):
    model, specs, originals, baseline = synthetic
    old = deepcopy(originals[0])
    old["models"]["2"]["defect_norm"] += 1e-10
    monkeypatch.setattr(
        runner,
        "regenerate",
        lambda *args: pytest.fail("a mismatched original must not be diagnosed"),
    )
    row = runner.diagnose_case(model, specs[0], old, baseline, backend="integer")
    assert row["status"] == "error" and row["failure_location"] == "original_case_replay"
    assert not row["original_record_reproduced"] and row["models"] == {}
    assert row["original"] == originals[0]


def test_changed_field_is_not_summed_and_partial_evidence_survives(synthetic, monkeypatch):
    model, specs, originals, baseline = synthetic
    regenerate = runner.regenerate

    def changed(m, a, degree, name):
        field = regenerate(m, a, degree, name)
        if name == "Phi_W":
            field[0, 0, 0, 0] = np.nextafter(field[0, 0, 0, 0], np.inf)
        return field

    monkeypatch.setattr(runner, "regenerate", changed)
    row = runner.diagnose_case(model, specs[0], originals[0], baseline, backend="integer")
    assert row["status"] == "error" and row["failure_location"] == "degree=2/field=Phi_W"
    assert row["original_record_reproduced"]
    fields = row["models"]["2"]["fields"]
    assert "population_sums" in fields["W"]
    assert set(fields["Phi_W"]) == {"observed_array"} and "W_R" not in fields
    assert "3" not in row["models"]


@pytest.fixture
def tiny_grid(synthetic, monkeypatch):
    model, specs, originals, baseline = synthetic
    monkeypatch.setattr(runner, "SIZES", (1,))
    monkeypatch.setattr(runner, "specifications", lambda **kwargs: specs)
    inputs = {"input_rebuild": {"passed": True}, "fiber_load": {"passed": True}}
    monkeypatch.setattr(runner.parent, "fresh_model", lambda size: (model, {}, inputs, {}))
    previous = {"size": 1, **inputs, "records": originals}
    grid = runner.grid_campaign(1, previous, worker=False)
    assert grid["status"] == "computed"
    assert grid["baseline"] == baseline
    assert runner.audit_grid(grid, previous, worker=False)["passed"]
    return grid, previous


@pytest.mark.parametrize(
    "damage",
    [
        "missing_case",
        "reordered",
        "missing_field",
        "field_hash",
        "canonical",
        "comparison",
        "gate",
        "counterfactual",
        "missing_control",
        "control_sum",
        "analytic",
        "fresh_input",
    ],
)
def test_complete_grid_audit_rejects_each_kind_of_tamper(tiny_grid, damage):
    original, previous = tiny_grid
    grid = deepcopy(original)
    if damage == "missing_case":
        grid["records"].pop()
    elif damage == "reordered":
        grid["records"].reverse()
    elif damage == "missing_field":
        del grid["records"][0]["models"]["3"]["fields"]["W_R"]
    elif damage == "field_hash":
        grid["records"][0]["models"]["3"]["fields"]["W_R"]["array"]["sha256"] = "0" * 64
    elif damage == "canonical":
        grid["records"][0]["models"]["2"]["fields"]["W"]["population_sums"][0]["denominator"] = "01"
    elif damage == "comparison":
        grid["records"][0]["models"]["2"]["comparisons"]["W_leaf"][0]["terms"]["sum_rounding"] = (
            exact.encode(Fraction(0))
        )
        grid["records"][0]["models"]["2"]["comparisons"]["W_leaf"][0]["terms"][
            "exact_field_error"
        ] = exact.encode(Fraction(1))
    elif damage == "gate":
        c = grid["records"][0]["models"]["2"]["comparisons"]["W_leaf"][0]
        c["exact_field_error_passed"] = not c["exact_field_error_passed"]
    elif damage == "counterfactual":
        grid["records"][0]["models"]["2"]["comparisons"]["Phi_conservation"][0][
            "base_only_counterfactual"
        ] = {"passed": True}
    elif damage == "missing_control":
        grid["negative_controls"]["records"].pop()
    elif damage == "control_sum":
        grid["negative_controls"]["records"][0]["actual_site_average_change"][0] = exact.encode(
            Fraction(0)
        )
    elif damage == "analytic":
        grid["baseline"]["analytic_conserved_sums"][0] = exact.encode(Fraction(0))
    else:
        grid["fiber_load"]["passed"] = False
    result = runner.audit_grid(grid, previous, worker=False)
    assert not result["passed"] and result["failure_location"]


def worker_document(path, grid, previous):
    current = runner.metadata()
    entry = runner.saved_grid(
        runner.parent.grid_path(path, 1), grid, current, previous, worker=True
    )
    evidence = {
        "input_audit": {"passed": True},
        "artificial_controls": exact.artificial_controls(),
        "grids": [grid],
    }
    doc = {
        **current,
        "kind": runner.WORKER_KIND,
        "backend": "gmp",
        "evidence": evidence,
        "evidence_digest_sha256": runner.digest(evidence),
        "grid_artifacts": [entry],
        "source_unchanged_after": True,
        "summary": runner.summary([grid]),
    }
    runner.write_json(path, doc)
    return doc


def test_full_save_readback_and_separate_gmp_replay(tiny_grid, tmp_path):
    grid, previous = tiny_grid
    path = tmp_path / "worker.json"
    doc = worker_document(path, grid, previous)
    audit = runner.audit_document(runner.read_json(path), path, [previous], worker=True)
    assert audit["passed"] and (
        audit["cases"],
        audit["fields"],
        audit["component_comparisons"],
    ) == (2, 12, 48)
    current = {**runner.metadata(), "process_id": doc["process_id"] + 1}
    inputs, controls = doc["evidence"]["input_audit"], doc["evidence"]["artificial_controls"]
    replay = runner.replay_audit(doc, path, current, inputs, controls, [grid], [previous])
    assert replay["passed"]
    assert not runner.worker_readiness(doc, path, doc, inputs, controls, [previous])["passed"]
    with pytest.raises(FileExistsError):
        runner.write_json(path, doc)


@pytest.mark.parametrize(
    "damage", ["child", "digest", "summary", "backend", "source", "incomplete", "identity"]
)
def test_worker_readiness_does_not_trust_flags_or_summaries(tiny_grid, tmp_path, damage):
    grid, previous = tiny_grid
    path = tmp_path / "worker.json"
    doc = worker_document(path, grid, previous)
    current = {**runner.metadata(), "process_id": doc["process_id"] + 1}
    inputs, controls = (
        deepcopy(doc["evidence"]["input_audit"]),
        deepcopy(doc["evidence"]["artificial_controls"]),
    )
    if damage == "child":
        doc["grid_artifacts"][0]["sha256"] = "0" * 64
    elif damage == "digest":
        doc["evidence_digest_sha256"] = "0" * 64
    elif damage == "summary":
        doc["summary"]["legacy"]["failed_components"] += 1
    elif damage == "backend":
        doc["backend"] = "integer"
    elif damage == "source":
        doc["source_unchanged_after"] = False
    elif damage == "incomplete":
        doc["evidence"]["grids"][0]["records"].pop()
        doc["evidence_digest_sha256"] = runner.digest(doc["evidence"])
    else:
        doc["evidence"]["grids"][0]["records"][0]["models"]["2"]["comparisons"]["W_leaf"][0][
            "identity_exact"
        ] = False
        doc["evidence_digest_sha256"] = runner.digest(doc["evidence"])
    assert not runner.worker_readiness(doc, path, current, inputs, controls, [previous])["passed"]


def test_no_primary_physical_work_before_valid_completed_worker(tiny_grid, tmp_path, monkeypatch):
    _, previous = tiny_grid
    monkeypatch.setattr(runner, "input_audit", lambda: {"passed": True})
    monkeypatch.setattr(
        runner,
        "read_json",
        lambda p: {"cycle": {"grids": [previous]}} if p == runner.PARENT_PATH else {},
    )
    monkeypatch.setattr(runner, "worker_readiness", lambda *a: {"passed": False})
    monkeypatch.setattr(
        runner, "grid_campaign", lambda *a, **k: pytest.fail("must finish worker first")
    )
    with pytest.raises(ValueError, match="completed separately"):
        runner.run(tmp_path / "main.json", worker=False, replay_path=tmp_path / "worker.json")


def test_failed_grid_keeps_diagnostic_location(tiny_grid, monkeypatch):
    _, previous = tiny_grid

    def broken(size):
        raise ValueError("controlled failed rebuild")

    monkeypatch.setattr(runner.parent, "fresh_model", broken)
    grid = runner.grid_campaign(1, previous, worker=False)
    assert grid["status"] == "error" and grid["failure_location"] == "fresh_original_model"
    assert grid["records"] == [] and "baseline" not in grid
    assert not runner.audit_grid(grid, previous, worker=False)["passed"]


def test_hypothesis_requires_exact_and_sum_only_but_not_baseline_only(tiny_grid, monkeypatch):
    grid, _ = tiny_grid
    monkeypatch.setattr(runner, "SIZES", (17, 33, 65))
    monkeypatch.setattr(
        runner,
        "specifications",
        lambda **kwargs: [r["specification"] for r in grid["records"]] * 32,
    )
    grids = [
        {**deepcopy(grid), "size": s, "records": deepcopy(grid["records"] * 32)}
        for s in runner.SIZES
    ]
    files = [{"full_saved_audit": {"passed": True}, "roundtrip_passed": True}] * 3
    true = {"passed": True}
    # Deliberately synthetic decision bookkeeping: field/source audits are tested separately.
    for g in grids:
        for r in g["records"]:
            for data in r["models"].values():
                for entries in data["comparisons"].values():
                    for c in entries:
                        c["exact_field_error_passed"] = c["sum_only_counterfactual"]["passed"] = (
                            True
                        )
                        if c["base_only_counterfactual"] is not None:
                            c["base_only_counterfactual"]["passed"] = False
    validity, hypotheses, outcome = runner.decision(true, true, grids, files, true, True)
    assert all(validity.values()) and all(hypotheses.values()) and outcome == "accepted"
    c = grids[2]["records"][63]["models"]["3"]["comparisons"]["W_R_leaf"][3]
    c["exact_field_error_passed"] = False
    assert runner.decision(true, true, grids, files, true, True)[2] == "rejected"
    c["exact_field_error_passed"] = True
    c["sum_only_counterfactual"]["passed"] = False
    assert runner.decision(true, true, grids, files, true, True)[2] == "rejected"
    assert runner.decision(true, true, grids, files, {"passed": False}, True)[2] == "inconclusive"
    assert runner.decision(true, true, grids[:2], files, true, True)[2] == "inconclusive"
    assert runner.decision(true, true, [], [], true, True)[2] == "inconclusive"
