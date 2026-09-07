"""Recompute Q012e decisions from sealed, including failed-amplitude, evidence."""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_amplitude as a
from research import d3q27_chart as chart
from research import q012a_d3q27_foundation as q012a
from research import q012e_d3q27_amplitude as runner
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = q012a.ARTIFACT_DIRECTORY / "q012e_d3q27_amplitude.json"
ARTIFACT_SHA256 = "880f6cb5d9f6e029c7e470a6f4dbd3feed5739342827bb0002f4c06d5ed580e5"


@pytest.fixture(scope="module")
def artifact():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_sources_digests_and_independent_four_case_replay(artifact):
    assert _file_sha256(PATH) == ARTIFACT_SHA256
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert artifact["source"] == source_metadata()
    assert _file_sha256(Path(runner.__file__)) == artifact["runner_source"]["sha256"]
    for name, module in runner.HELPERS:
        assert _file_sha256(Path(module.__file__)) == artifact["helper_sources"][name]["sha256"]
    assert runner.input_audit() == cycle["input_audit"]
    evidence = runner.replay_evidence(
        cycle["input_audit"], cycle["coefficient_rebuild"], cycle["records"]
    )
    replay = runner.replay_audit(
        PATH.parent / cycle["independent_replay"]["filename"], evidence, artifact
    )
    assert replay == cycle["independent_replay"]
    assert replay["passed"]
    assert len(evidence["records"]) == 4
    assert "four preregistered cases only" in replay["scope"]


def test_all_signed_amplitudes_and_independent_104_coordinate_directions(artifact):
    cycle = artifact["cycle"]
    assert len(cycle["records"]) == 224
    assert len(cycle["directions"]) == 16
    assert {a.case_key(r) for r in cycle["records"]} == {
        (group, i, value, sign)
        for group in a.SEEDS
        for i in range(8)
        for value in a.AMPLITUDES
        for sign in (1, -1)
    }
    for group, seed in a.SEEDS.items():
        directions = [r["direction"] for r in cycle["directions"] if r["group"] == group]
        np.testing.assert_array_equal(directions, chart.normalized_directions(seed, 8))
        assert np.all(np.asarray(directions) != 0)
    assert _all_numeric_values_finite(cycle)
    assert all(cycle["validity_gates"].values())


def test_trace_coverage_stops_and_metrics_recomputed(artifact):
    for case in artifact["cycle"]["records"]:
        t = case["trajectory"]
        trace = t["trace"]
        assert [r["step"] for r in trace] == list(range(len(trace)))
        assert trace[0]["population_error"] == trace[0]["linear_population_error"] == 0
        assert trace[0]["macro_error"] == trace[0]["linear_macro_error"] == 0
        assert t["execution_error"] is None
        if t["complete"]:
            assert len(trace) == 65 and t["stop_reason"] is None
        else:
            assert t["stop_reason"]["step"] == len(trace) - 1
            assert t["stop_reason"]["reason"] == "population_or_density_guard"
        for row in trace:
            failed_fields = [
                name
                for name in ("full", "quadratic")
                if row["observables"][name]["minimum_population"] <= 0
                or row["observables"][name]["minimum_density"] < 0.5
            ]
            if failed_fields:
                assert row is trace[-1] and failed_fields == t["stop_reason"]["fields"]
        maxima = {
            key: max(r[key] for r in trace)
            for key in (
                "population_error",
                "linear_population_error",
                "macro_error",
                "linear_macro_error",
            )
        }
        summary = t["summary"]
        for key, value in maxima.items():
            assert summary["maximum_" + key] == value
        assert summary["maximum_relative_population_error"] == a.ratio(
            maxima["population_error"],
            t["initial_population_perturbation_norm"],
            t["roundoff_floor"],
        )
        assert summary["maximum_relative_macro_error"] == a.ratio(
            maxima["macro_error"], t["initial_macro_perturbation_norm"], t["roundoff_floor"]
        )
        assert summary["quadratic_to_linear_maximum_error_ratio"] == a.ratio(
            maxima["population_error"], maxima["linear_population_error"], t["roundoff_floor"]
        )
        drift = (
            max(
                abs(v)
                for r in trace
                for name in ("full", "quadratic")
                for v in r["global_conservation_drift"][name]
            )
            / 17**3
        )
        assert summary["maximum_site_average_conservation_drift"] == drift
        assert a.usage_gates(t, case["one_step"]) == case["usage_gates"]
        assert all(case["usage_gates"].values()) == case["usage_passed"]


def test_gram_rational_identity_and_nontrivial_tail(artifact):
    resolved_tail_count = 0
    for case in artifact["cycle"]["records"]:
        row = case["one_step"]
        if not row["in_domain"]:
            assert row["minimum_density"] <= 0 and row["identity_passed"] is None
            continue
        gram = np.array(row["term_gram"])
        np.testing.assert_allclose(gram, gram.T, atol=0)
        np.testing.assert_allclose(np.diag(gram), np.asarray(row["term_norms"]) ** 2, rtol=2e-13)
        predicted_norm = np.sqrt(max(0, gram.sum()))
        assert abs(predicted_norm - row["defect_norm"]) <= row["roundoff_budget"]
        assert row["identity_passed"] == (row["tail_prediction_error"] <= row["roundoff_budget"])
        if row["term_norms"][-1] > 100 * row["roundoff_budget"]:
            resolved_tail_count += 1
            assert (
                abs(row["quartic_prediction_error"] - row["term_norms"][-1])
                <= row["roundoff_budget"]
            )
    assert resolved_tail_count > 0


def test_selection_never_reuses_holdout_or_omits_failed_amplitudes(artifact):
    cycle = artifact["cycle"]
    inventory = {group: a.amplitude_inventory(cycle["records"], group) for group in a.SEEDS}
    assert inventory == cycle["amplitude_inventory"]
    prefix = a.select_prefix(inventory["calibration"])
    assert prefix == [0.008, 0.032]
    boundary = [r for r in cycle["records"] if r["amplitude"] == 0.128]
    assert sum(r["usage_passed"] for r in boundary) == 2
    assert all(r["group"] == "holdout" for r in boundary if r["usage_passed"])
    assert all(
        [k for k, v in r["usage_gates"].items() if not v]
        == ["improvement_over_same_initial_linear"]
        for r in boundary
        if not r["usage_passed"]
    )
    assert sum(r["trajectory"]["complete"] for r in cycle["records"]) == 128
    assert sum(len(r["trajectory"]["trace"]) for r in cycle["records"]) == 8416
    assert cycle["selection"]["calibration_prefix"] == prefix
    assert cycle["selection"]["selected_amplitude"] == (prefix[-1] if prefix else None)
    holdout_pass = bool(prefix) and all(
        row["passed"] for row in inventory["holdout"] if row["amplitude"] in prefix
    )
    assert cycle["selection"]["holdout_passed"] == holdout_pass
    hypotheses = {
        "rational_decomposition": all(
            r["one_step"]["identity_passed"] for r in cycle["records"] if r["one_step"]["in_domain"]
        ),
        "nonempty_calibration_prefix": bool(prefix),
        "selected_prefix_holdout": holdout_pass,
    }
    assert hypotheses == cycle["hypothesis_gates"]
    assert (
        runner.prior.classify(cycle["validity_gates"], hypotheses, True)
        == cycle["scientific_outcome"]
        == artifact["scientific_outcome"]
    )


def test_fresh_all_arrays_and_two_full_cases_reproduce(artifact):
    model, rebuild = runner.fresh_chart()
    cycle = artifact["cycle"]
    assert rebuild == cycle["coefficient_rebuild"]
    for group, index, value, sign in (a.REPLAY_CASES[0], a.REPLAY_CASES[3]):
        terms = a.path_terms(model, chart.normalized_directions(a.SEEDS[group], 8)[index])
        direction = next(
            r for r in cycle["directions"] if (r["group"], r["direction_index"]) == (group, index)
        )
        assert direction["coefficient_audit"] == terms.audit
        expected = next(r for r in cycle["records"] if a.case_key(r) == (group, index, value, sign))
        assert a.evaluate_case(model, terms, group, index, value, sign) == expected


def test_cli_refuses_to_overwrite_sealed_evidence():
    before = _file_sha256(PATH)
    completed = subprocess.run(
        [sys.executable, "-m", "research.q012e_d3q27_amplitude", "--worker-output", str(PATH)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 2
    assert "sealed evidence is not overwritten" in completed.stderr
    assert _file_sha256(PATH) == before
