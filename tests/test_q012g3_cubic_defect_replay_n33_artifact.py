"""Closed second worker grid: preserve real counterexamples without a main verdict."""

from copy import deepcopy
from math import fsum, log
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

OUTPUT = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay.json")
PATH = runner.parent.grid_path(OUTPUT, 33)
SHA = "777559e4ffebb723f3dd5b3c42880bb06ea137711a8babac8f011c1039be0c23"
GRID_DIGEST = "07662bf8c2765e9c8ba631402f941b2b9ad9c782cea664b8a1f1a61e9089977b"
SOURCE_DIGEST = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"


@pytest.fixture(scope="module")
def completed():
    assert runner._file_sha256(PATH) == SHA
    saved = runner.read_json(PATH)
    assert saved["process_id"] == 27060 and saved["worker"] is True
    assert saved["source_digest_sha256"] == runner.source_digest(runner.metadata()) == SOURCE_DIGEST
    assert saved["grid_digest_sha256"] == runner.digest(saved["grid"]) == GRID_DIGEST
    assert runner._file_sha256(runner.prior.PARENT_PATH) == runner.prior.PARENT_SHA
    assert runner._file_sha256(runner.PRIOR_PATH) == runner.INPUT_SEALS[runner.PRIOR_PATH]
    old = runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"][1]
    conserved = runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"][1]
    assert old["size"] == conserved["size"] == saved["grid"]["size"] == 33
    return saved, old, conserved


def test_full_registered_grid_and_all_applicable_gates(completed):
    saved, old, conserved = completed
    audit = runner.audit_grid(saved["grid"], old, conserved, worker=True)
    assert audit == saved["full_saved_audit"] and audit["passed"]
    assert {k: v for k, v in audit.items() if k != "direction_gates"} == {
        "passed": True,
        "cases": 64,
        "profiles": 42,
        "original_fields": 384,
        "original_defects": 128,
        "independent_vector_comparisons": 1533,
    }
    assert len(audit["direction_gates"]) == 21
    assert all(
        all(v is True for v in gate.values() if v is not None) for gate in audit["direction_gates"]
    )


def test_all_direction_artifact_bytes_and_headers(completed):
    saved, _, _ = completed
    assert len(saved["direction_artifacts"]) == len(saved["grid"]["directions"]) == 21
    for entry, row in zip(saved["direction_artifacts"], saved["grid"]["directions"], strict=True):
        path = runner.direction_path(OUTPUT, 33, row["schedule"])
        assert entry["filename"] == path.name and entry["sha256"] == runner._file_sha256(path)
        child = runner.read_json(path)
        assert child["direction"] == row and child["direction_digest_sha256"] == runner.digest(row)
        assert child["process_id"] == saved["process_id"] and child["size"] == 33
        assert child["source_digest_sha256"] == SOURCE_DIGEST
        assert child["generated_at_utc"] == saved["generated_at_utc"]
        assert runner._all_numeric_values_finite(child)


def closed_slope(values):
    x, y = list(map(log, runner.parent.AMPLITUDES)), list(map(log, values))
    mx, my = fsum(x) / 4, fsum(y) / 4
    return fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / fsum(
        (a - mx) ** 2 for a in x
    )


def test_all_generic_slopes_and_smallest_ratios_from_saved_norms(completed):
    saved, _, _ = completed
    rows = [r for r in saved["grid"]["directions"] if r["schedule"]["kind"] == "order"]
    assert len(rows) == 11
    for row in rows:
        prediction = row["fit_prediction"]
        for d in ("2", "3"):
            measured = closed_slope(
                [c["models"][d]["samples"]["primary"]["P9_norm"] for c in row["cases"]]
            )
            original = closed_slope(
                [c["original"]["models"][d]["defect_norm"] for c in row["cases"]]
            )
            assert abs(measured - prediction["predicted_slopes"][d]) < 1e-12
            assert abs(original - prediction["original_fit"]["slopes"][d]) < 1e-12
            assert abs(measured - original) <= 0.01
        smallest = row["cases"][-1]["models"]
        ratio = (
            smallest["3"]["samples"]["primary"]["P9_norm"]
            / smallest["2"]["samples"]["primary"]["P9_norm"]
        )
        old_ratio = prediction["original_fit"]["smallest_amplitude_ratio"]
        assert ratio == prediction["smallest_amplitude_ratio"]
        assert abs(ratio - old_ratio) / old_ratio <= 0.01
        assert prediction["H3_passed"] and prediction["original_H4_predicate_matches"]


def test_all_holdouts_reproduce_ten_half_failures_and_four_worsenings(completed):
    saved, _, _ = completed
    cases = [
        c
        for r in saved["grid"]["directions"]
        if r["schedule"]["kind"] == "amplitude"
        for c in r["cases"]
    ]
    assert len(cases) == 20
    half_failures, worsenings = [], []
    for case in cases:
        old, prediction = case["original"], case["holdout_prediction"]
        a, b = (case["models"][str(d)]["samples"]["primary"] for d in (2, 3))
        ratio = b["P9_norm"] / a["P9_norm"]
        old_ratio = old["cubic_to_quadratic_defect_ratio"]
        assert prediction["predicted_ratio"] == ratio
        assert (ratio <= 0.5) == (old_ratio <= 0.5) and (ratio > 1) == (old_ratio > 1)
        assert prediction["original_composite_H5"] == old["amplitude_passed"]
        assert prediction["H2_passed"]
        for sample in (a, b):
            assert sample["raw_resolved"] and sample["P9_vector_passed"]
            assert sample["P9_vector_difference_norm"] <= 1e-3 * sample["raw_defect_norm"]
        if ratio > 0.5:
            assert old["amplitude"] == 0.032 and old["amplitude_passed"] is False
            half_failures.append(old["direction_index"])
        if ratio > 1:
            worsenings.append(old["direction_index"])
    assert half_failures == [0, 1, 2, 3, 4, 5, 6, 7, 16, 21]
    assert worsenings == [2, 4, 7, 16]
    worst = max(cases, key=lambda c: c["original"]["cubic_to_quadratic_defect_ratio"])
    assert worst["original"]["direction_index"] == 16
    assert worst["original"]["cubic_to_quadratic_defect_ratio"] == 1.316172134164264
    assert worst["holdout_prediction"]["predicted_ratio"] > 1


def test_all_gram_truncations_with_compensated_sums(completed):
    saved, _, _ = completed
    compared = 0
    for row in saved["grid"]["directions"]:
        for case in row["cases"]:
            for data in case["models"].values():
                for sample in data["samples"].values():
                    weighted = sample["weighted_gram"]
                    for truncation in sample["truncations"]:
                        n = truncation["degree"] + 1
                        value = fsum(weighted[i][j] for i in range(n) for j in range(n))
                        assert value >= 0
                        assert (
                            abs(value - truncation["direct_norm_squared"])
                            <= truncation["gram_tolerance"]
                        )
                        compared += 1
    assert compared == 1664


def test_full_summary_counts_failures_and_reconstruction_maxima(completed):
    saved, _, _ = completed
    report = runner.summary([saved["grid"]])
    assert report["counts"] == {"directions": 21, "cases": 64, "profiles": 42}
    assert report["failure_counts"] == {
        k: 0 for k in ("incomplete", "H1", "H2", "H3", "Gram", "independent")
    }
    samples = [
        s
        for r in saved["grid"]["directions"]
        for c in r["cases"]
        for m in c["models"].values()
        for s in m["samples"].values()
    ]
    assert len(samples) == 256
    for name, record in report["maximum_reconstruction_error"].items():
        assert record["error_norm"] == max(s["reconstruction_errors"][name] for s in samples)
        assert record["error_norm"] <= record["roundoff_floor"]


@pytest.mark.parametrize(
    "damage", ["omit_worst_direction", "relabel_legacy_H5", "unearned_H2", "tail", "last_R_value"]
)
def test_real_counterexample_and_last_component_damage_is_rejected(completed, damage):
    saved, old, conserved = completed
    grid = deepcopy(saved["grid"])
    worst = next(
        r
        for r in grid["directions"]
        if r["schedule"]["kind"] == "amplitude" and r["schedule"]["direction_index"] == 16
    )
    case = worst["cases"][-1]
    if damage == "omit_worst_direction":
        grid["directions"].remove(worst)
    elif damage == "relabel_legacy_H5":
        case["holdout_prediction"]["original_composite_H5"] = True
    elif damage == "unearned_H2":
        case["holdout_prediction"]["predicted_ratio"] = 0.1
    elif damage == "tail":
        case["models"]["3"]["samples"]["independent"]["tail_norm"] += 1
    else:
        case["models"]["3"]["samples"]["independent"]["reconstructed_reduced_coordinates"][-1] += 1
    assert not runner.audit_grid(grid, old, conserved, worker=True)["passed"]
