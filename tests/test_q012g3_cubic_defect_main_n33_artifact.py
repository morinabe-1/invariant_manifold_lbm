"""Close the second main grid, preserving counterexamples outside the replay subset."""

from copy import deepcopy
from math import fsum, log
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

OUTPUT = Path("research/artifacts/q012g3_d3q27_cubic_defect.json")
PATH = runner.parent.grid_path(OUTPUT, 33)
SHA = "ba2976127868ae834dbe17f183b34ddf8ef0bc0d0ea1cbd3579ae43cece9adff"
GRID_DIGEST = "6620536a216d25d44c20e3180b830de501d913b25e074ed4d68794f62fbf3789"
SOURCE_DIGEST = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"
WORKER_PATH = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay_n33.json")
WORKER_SHA = "777559e4ffebb723f3dd5b3c42880bb06ea137711a8babac8f011c1039be0c23"


@pytest.fixture(scope="module")
def completed():
    assert runner._file_sha256(PATH) == SHA
    saved = runner.read_json(PATH)
    assert saved["process_id"] == 35240 and saved["worker"] is False
    assert saved["source_digest_sha256"] == runner.source_digest(runner.metadata()) == SOURCE_DIGEST
    assert saved["grid_digest_sha256"] == runner.digest(saved["grid"]) == GRID_DIGEST
    assert runner._file_sha256(runner.prior.PARENT_PATH) == runner.prior.PARENT_SHA
    assert runner._file_sha256(runner.PRIOR_PATH) == runner.INPUT_SEALS[runner.PRIOR_PATH]
    old = runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"][1]
    conserved = runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"][1]
    assert old["size"] == conserved["size"] == saved["grid"]["size"] == 33
    return saved, old, conserved


def test_full_320_case_grid_and_all_applicable_gates(completed):
    saved, old, conserved = completed
    audit = runner.audit_grid(saved["grid"], old, conserved, worker=False)
    assert audit == saved["full_saved_audit"] and audit["passed"]
    assert {k: v for k, v in audit.items() if k != "direction_gates"} == {
        "passed": True,
        "cases": 320,
        "profiles": 192,
        "original_fields": 1920,
        "original_defects": 640,
        "independent_vector_comparisons": 0,
    }
    assert len(audit["direction_gates"]) == 96
    assert all(
        all(v is True for v in gate.values() if v is not None) for gate in audit["direction_gates"]
    )


def test_all_96_child_seals_headers_and_contents(completed):
    saved, _, _ = completed
    assert len(saved["direction_artifacts"]) == len(saved["grid"]["directions"]) == 96
    for entry, row in zip(saved["direction_artifacts"], saved["grid"]["directions"], strict=True):
        path = runner.direction_path(OUTPUT, 33, row["schedule"])
        assert entry["filename"] == path.name and entry["sha256"] == runner._file_sha256(path)
        child = runner.read_json(path)
        assert child["direction"] == row and child["direction_digest_sha256"] == runner.digest(row)
        assert child["process_id"] == saved["process_id"] and child["size"] == 33
        assert child["source_digest_sha256"] == SOURCE_DIGEST
        assert child["generated_at_utc"] == saved["generated_at_utc"]
        assert runner._all_numeric_values_finite(child)


def test_all_64_worker_cases_match_main_primary_records(completed):
    saved, _, _ = completed
    assert runner._file_sha256(WORKER_PATH) == WORKER_SHA
    worker = runner.read_json(WORKER_PATH)
    assert worker["worker"] is True and worker["process_id"] != saved["process_id"]
    assert worker["source_digest_sha256"] == SOURCE_DIGEST
    selected = {
        (s["kind"], s["direction_index"]) for s in runner.evidence.direction_schedule(worker=True)
    }
    main = [
        row
        for row in saved["grid"]["directions"]
        if (row["schedule"]["kind"], row["schedule"]["direction_index"]) in selected
    ]
    assert len(main) == len(worker["grid"]["directions"]) == 21
    assert sum(len(row["cases"]) for row in main) == 64
    for actual, expected in zip(main, worker["grid"]["directions"], strict=True):
        assert runner.evidence.primary_record(actual) == runner.evidence.primary_record(expected)


def closed_slope(values):
    x, y = list(map(log, runner.parent.AMPLITUDES)), list(map(log, values))
    mx, my = fsum(x) / 4, fsum(y) / 4
    return fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / fsum(
        (a - mx) ** 2 for a in x
    )


def test_all_64_generic_fits_with_independent_least_squares(completed):
    saved, _, _ = completed
    rows = [r for r in saved["grid"]["directions"] if r["schedule"]["kind"] == "order"]
    assert [r["schedule"]["direction_index"] for r in rows] == list(range(64))
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
        assert prediction["original_fit"]["passed"] is True
        assert prediction["predicted_original_H4_predicate"] is True
    assert max(max(r["fit_prediction"]["slope_absolute_errors"].values()) for r in rows) == (
        0.00017371130414334246
    )
    assert max(r["fit_prediction"]["ratio_relative_error"] for r in rows) == 0.00039331366732360686


def test_all_64_holdouts_keep_32_half_failures_and_five_worsenings(completed):
    saved, _, _ = completed
    cases = [
        c
        for r in saved["grid"]["directions"]
        if r["schedule"]["kind"] == "amplitude"
        for c in r["cases"]
    ]
    assert len(cases) == 64
    half_failures, worsenings = [], []
    for case in cases:
        old, prediction = case["original"], case["holdout_prediction"]
        a, b = (case["models"][str(d)]["samples"]["primary"] for d in (2, 3))
        ratio = b["P9_norm"] / a["P9_norm"]
        old_ratio = old["cubic_to_quadratic_defect_ratio"]
        assert prediction["predicted_ratio"] == ratio
        assert (ratio <= 0.5) == (old_ratio <= 0.5) and (ratio > 1) == (old_ratio > 1)
        assert prediction["original_composite_H5"] == old["amplitude_passed"]
        assert old["amplitude_passed"] is (old["amplitude"] == 0.008)
        assert prediction["H2_passed"]
        for sample in (a, b):
            assert sample["raw_resolved"] and sample["P9_vector_passed"]
            assert sample["P9_vector_difference_norm"] <= 1e-3 * sample["raw_defect_norm"]
        if ratio > 0.5:
            half_failures.append((old["direction_index"], old["amplitude"]))
        if ratio > 1:
            worsenings.append((old["direction_index"], old["amplitude"]))
    assert half_failures == [(i, 0.032) for i in range(32)]
    assert worsenings == [(i, 0.032) for i in (2, 4, 7, 16, 23)]
    worst = max(cases, key=lambda c: c["original"]["cubic_to_quadratic_defect_ratio"])
    assert worst["original"]["direction_index"] == 16
    assert worst["original"]["cubic_to_quadratic_defect_ratio"] == 1.316172134164264
    assert worst["holdout_prediction"]["predicted_ratio"] == 1.3161721341163626


def test_counterexample23_outside_worker_needs_more_than_the_leading_vector(completed):
    saved, _, _ = completed
    row = next(
        r
        for r in saved["grid"]["directions"]
        if r["schedule"]["kind"] == "amplitude" and r["schedule"]["direction_index"] == 23
    )
    assert row["schedule"] not in runner.evidence.direction_schedule(worker=True)
    case = row["cases"][-1]
    assert case["specification"]["amplitude"] == 0.032
    assert case["original"]["cubic_to_quadratic_defect_ratio"] == 1.1349501394251245
    assert case["holdout_prediction"]["predicted_ratio"] == 1.1349501393864596
    assert case["holdout_prediction"]["H2_passed"]
    assert case["holdout_prediction"]["original_composite_H5"] is False
    sample = case["models"]["3"]["samples"]["primary"]
    errors = {t["degree"]: t["relative_vector_error"] for t in sample["truncations"]}
    assert errors[4] == 0.412617433263631
    assert errors[6] == 9.259700967342776e-5
    assert errors[9] == 1.1068671250188703e-9
    assert errors[4] > 1e-3 > errors[6] > errors[9]
    # These are truncations of the same W3 defect, not new W4/W6/W9 charts.


def test_all_4160_gram_truncations_with_compensated_sums(completed):
    saved, _, _ = completed
    compared = 0
    for row in saved["grid"]["directions"]:
        for case in row["cases"]:
            for data in case["models"].values():
                assert set(data["samples"]) == {"primary"}
                for truncation in data["samples"]["primary"]["truncations"]:
                    weighted = data["samples"]["primary"]["weighted_gram"]
                    n = truncation["degree"] + 1
                    value = fsum(weighted[i][j] for i in range(n) for j in range(n))
                    assert value >= 0
                    assert (
                        abs(value - truncation["direct_norm_squared"])
                        <= truncation["gram_tolerance"]
                    )
                    compared += 1
    assert compared == 4160


def test_summary_counts_failures_and_maxima_from_all_640_samples(completed):
    saved, _, _ = completed
    report = runner.summary([saved["grid"]])
    assert report["counts"] == {"directions": 96, "cases": 320, "profiles": 192}
    assert report["failure_counts"] == {
        k: 0 for k in ("incomplete", "H1", "H2", "H3", "Gram", "independent")
    }
    samples = [
        m["samples"]["primary"]
        for r in saved["grid"]["directions"]
        for c in r["cases"]
        for m in c["models"].values()
    ]
    assert len(samples) == 640
    for name, record in report["maximum_reconstruction_error"].items():
        assert record["error_norm"] == max(s["reconstruction_errors"][name] for s in samples)
        assert record["error_norm"] <= record["roundoff_floor"]
    maximum = report["maximum_reconstruction_error"]["Phi_reconstructed"]
    assert maximum["direction_index"] == 9 and maximum["kind"] == "amplitude"
    assert maximum["degree"] == 2 and maximum["amplitude"] == 0.008
    assert maximum["error_norm"] == 1.5381118046148136e-14
    assert maximum["roundoff_floor"] == 1.4882165908113665e-12


@pytest.mark.parametrize(
    "damage", ["omit_counterexample23", "legacy_H5", "ratio", "C9", "tail", "last_R"]
)
def test_counterexample_and_last_component_damage_is_rejected(completed, damage):
    saved, old, conserved = completed
    grid = deepcopy(saved["grid"])
    row23 = next(
        r
        for r in grid["directions"]
        if r["schedule"]["kind"] == "amplitude" and r["schedule"]["direction_index"] == 23
    )
    last = grid["directions"][-1]
    if damage == "omit_counterexample23":
        grid["directions"].remove(row23)
    elif damage == "legacy_H5":
        row23["cases"][-1]["holdout_prediction"]["original_composite_H5"] = True
    elif damage == "ratio":
        row23["cases"][-1]["holdout_prediction"]["predicted_ratio"] = 0.1
    elif damage == "C9":
        last["profiles"]["3"]["primary"]["defect_coefficients"].pop()
    elif damage == "tail":
        last["cases"][-1]["models"]["3"]["samples"]["primary"]["tail_norm"] += 1
    else:
        last["cases"][-1]["models"]["3"]["samples"]["primary"]["reconstructed_reduced_coordinates"][
            -1
        ] += 1
    assert not runner.audit_grid(grid, old, conserved, worker=False)["passed"]
