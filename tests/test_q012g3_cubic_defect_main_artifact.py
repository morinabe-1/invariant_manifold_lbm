"""Seal the full 960-case diagnosis without accepting or repairing the old W3 chart."""

from copy import deepcopy
from math import fsum, log
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

PATH = Path("research/artifacts/q012g3_d3q27_cubic_defect.json")
SHA = "40d5bbbee9a3a6c4c4330062a1eada7422567e478f2ae06b2c9851e409423a91"
EVIDENCE_DIGEST = "0a1288a65eb9211f26be17478b8425c39cff7481011c5ef2010081b6b698eee6"
SOURCE_DIGEST = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"
WORKER_PATH = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay.json")
WORKER_SHA = "546f99edfe101dccd770dcf559bf3a9394eec84c463c0e2b05895c11430f4628"
GRID_SEALS = {
    17: "e2edeec5e05da2e1d93694ac0c9c9b58f3b33da64edd022cfb9515b8cb92c43f",
    33: "ba2976127868ae834dbe17f183b34ddf8ef0bc0d0ea1cbd3579ae43cece9adff",
    65: "9f2fa6e80d3e2fcd9afe109fd6da8b0e9ea3b2c29bf1ec419b56299ced07b53a",
}


@pytest.fixture(scope="module")
def completed():
    assert runner._file_sha256(PATH) == SHA
    saved = runner.read_json(PATH)
    assert saved["evidence_digest_sha256"] == runner.digest(saved["evidence"]) == EVIDENCE_DIGEST
    assert runner.source_digest(saved) == runner.source_digest(runner.metadata()) == SOURCE_DIGEST
    assert saved["process_id"] == 35240
    assert runner._file_sha256(WORKER_PATH) == WORKER_SHA
    for size, sha in GRID_SEALS.items():
        assert runner._file_sha256(runner.parent.grid_path(PATH, size)) == sha
    old = runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"]
    conserved = runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"]
    # Fresh input-chain, every saved child, and the entire independent replay audit.
    audit = runner.audit_document(saved, PATH, old, conserved, worker=False)
    assert audit["passed"], audit
    return saved, old, conserved, audit


def test_full_960_cases_and_all_three_diagnostic_hypotheses(completed):
    saved, old, _, audit = completed
    assert {k: v for k, v in audit.items() if k != "grids"} == {
        "passed": True,
        "cases": 960,
        "profiles": 576,
        "independent_vector_comparisons": 0,
    }
    assert len(audit["grids"]) == 3
    for grid in audit["grids"]:
        assert {k: v for k, v in grid.items() if k != "direction_gates"} == {
            "passed": True,
            "cases": 320,
            "profiles": 192,
            "original_fields": 1920,
            "original_defects": 640,
            "independent_vector_comparisons": 0,
        }
        assert len(grid["direction_gates"]) == 96
        assert all(
            all(v is True for v in gate.values() if v is not None)
            for gate in grid["direction_gates"]
        )
    assert sum(g["original_fields"] for g in audit["grids"]) == 5760
    assert sum(g["original_defects"] for g in audit["grids"]) == 1920
    assert sum(len(g["records"]) for g in old) == 1248
    decision = saved["decision"]
    assert len(decision["validity_gates"]) == 10 and all(decision["validity_gates"].values())
    assert decision["hypothesis_gates"] == {"H1": True, "H2": True, "H3": True}
    assert decision["study_gate"] == "passed" and decision["scientific_outcome"] == "accepted"
    assert saved["claim_boundary"] == runner.BOUNDARY
    assert saved["source_unchanged_after"] and saved["inputs_unchanged_after"]
    assert saved["input_audit_after"] == saved["evidence"]["input_audit"]


def test_original_177_controls_are_sealed_and_actually_reported(completed):
    saved = completed[0]
    controls = saved["evidence"]["controls"]
    assert controls == {
        "test_sources": runner.control_seals(),
        "exit_code": 0,
        "passed_tests": 177,
        "sources_unchanged": True,
        "passed": True,
    }
    assert len(controls["test_sources"]) == 5
    assert "177 passed in 19.64s" in saved["control_execution_output"]["stdout"]
    assert saved["control_execution_output"]["stderr"] == ""
    # The control subprocess exit is recorded; the original main exit is not inferred here.


def test_all_288_child_seals_and_full_saved_grid_audits(completed):
    saved, _, _, audit = completed
    count = 0
    for grid, grid_audit in zip(saved["evidence"]["grids"], audit["grids"], strict=True):
        child = runner.read_json(runner.parent.grid_path(PATH, grid["size"]))
        assert child["grid"] == grid and child["full_saved_audit"] == grid_audit
        assert child["worker"] is False
        assert len(child["direction_artifacts"]) == len(grid["directions"]) == 96
        for row, seal in zip(grid["directions"], child["direction_artifacts"], strict=True):
            path = runner.direction_path(PATH, grid["size"], row["schedule"])
            assert seal["filename"] == path.name and seal["sha256"] == runner._file_sha256(path)
            record = runner.read_json(path)
            assert record["direction"] == row
            assert record["direction_digest_sha256"] == runner.digest(row)
            assert all(record[k] == v for k, v in runner.header(saved).items())
            count += 1
    assert count == 288


def test_all_192_replay_cases_match_main_with_4599_worker_comparisons(completed):
    saved = completed[0]
    replay = saved["independent_replay"]
    assert replay["passed"] and all(replay["checks"].values())
    assert replay["filename"] == WORKER_PATH.name and replay["sha256"] == WORKER_SHA
    assert replay["worker_process_id"] == 27060 != saved["process_id"]
    worker = runner.read_json(WORKER_PATH)
    worker_audit = replay["full_saved_audit"]
    assert worker_audit["cases"] == 192 and worker_audit["profiles"] == 126
    assert worker_audit["independent_vector_comparisons"] == 4599
    assert worker["decision"]["scientific_outcome"] == "worker_only"
    selected = {
        (s["kind"], s["direction_index"]) for s in runner.evidence.direction_schedule(worker=True)
    }
    count = 0
    for main, other, comparison in zip(
        saved["evidence"]["grids"],
        worker["evidence"]["grids"],
        replay["main_correspondence"],
        strict=True,
    ):
        assert main["size"] == other["size"] == comparison["size"]
        assert comparison["all_primary_scientific_records_equal"]
        rows = [
            r
            for r in main["directions"]
            if (r["schedule"]["kind"], r["schedule"]["direction_index"]) in selected
        ]
        assert len(rows) == len(other["directions"]) == 21
        assert sum(len(r["cases"]) for r in rows) == 64
        for actual, expected in zip(rows, other["directions"], strict=True):
            assert runner.evidence.primary_record(actual) == runner.evidence.primary_record(
                expected
            )
            count += len(actual["cases"])
    assert count == 192  # Not all 960 cases independently recomputed by the second formula.


def slope(values):
    x, y = list(map(log, runner.parent.AMPLITUDES)), list(map(log, values))
    mx, my = fsum(x) / 4, fsum(y) / 4
    return fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / fsum(
        (a - mx) ** 2 for a in x
    )


def test_all_192_generic_fits_with_independent_ols_and_original_h4(completed):
    count, failures = 0, []
    for grid in completed[0]["evidence"]["grids"]:
        rows = [r for r in grid["directions"] if r["schedule"]["kind"] == "order"]
        assert [r["schedule"]["direction_index"] for r in rows] == list(range(64))
        for row in rows:
            fit = row["fit_prediction"]
            measured = {}
            for degree in ("2", "3"):
                values = [
                    c["models"][degree]["samples"]["primary"]["P9_norm"] for c in row["cases"]
                ]
                assert all(
                    v > c["original"]["roundoff_floor"]
                    for v, c in zip(values, row["cases"], strict=True)
                )
                measured[degree] = slope(values)
                original = slope(
                    [c["original"]["models"][degree]["defect_norm"] for c in row["cases"]]
                )
                assert abs(measured[degree] - fit["predicted_slopes"][degree]) < 1e-12
                assert abs(original - fit["original_fit"]["slopes"][degree]) < 1e-12
                assert abs(measured[degree] - original) <= 0.01
            smallest = row["cases"][-1]["models"]
            ratio = (
                smallest["3"]["samples"]["primary"]["P9_norm"]
                / smallest["2"]["samples"]["primary"]["P9_norm"]
            )
            old_ratio = fit["original_fit"]["smallest_amplitude_ratio"]
            assert ratio == fit["smallest_amplitude_ratio"]
            assert abs(ratio - old_ratio) / old_ratio <= 0.01
            predicted_h4 = (
                2.9 <= measured["2"] <= 3.1 and 3.9 <= measured["3"] <= 4.1 and ratio <= 0.1
            )
            assert predicted_h4 is fit["predicted_original_H4_predicate"]
            assert predicted_h4 is fit["original_fit"]["passed"]
            assert fit["H3_passed"] and fit["original_H4_predicate_matches"]
            if not predicted_h4:
                failures.append((grid["size"], row["schedule"]["direction_index"]))
            count += 1
    assert count == 192 and failures == [(65, 34), (65, 51), (65, 52)]


def test_all_192_holdouts_keep_81_half_failures_and_37_worsenings(completed):
    counts, half_failures, worsenings, legacy_passes = 0, [], [], {}
    for grid in completed[0]["evidence"]["grids"]:
        legacy_passes[grid["size"]] = 0
        for row in grid["directions"]:
            if row["schedule"]["kind"] != "amplitude":
                continue
            for case in row["cases"]:
                old, prediction = case["original"], case["holdout_prediction"]
                a, b = (case["models"][str(d)]["samples"]["primary"] for d in (2, 3))
                ratio = b["P9_norm"] / a["P9_norm"]
                old_ratio = old["cubic_to_quadratic_defect_ratio"]
                assert prediction["predicted_ratio"] == ratio
                assert (ratio <= 0.5) == (old_ratio <= 0.5) and (ratio > 1) == (old_ratio > 1)
                assert prediction["original_composite_H5"] is old["amplitude_passed"]
                assert prediction["H2_passed"]
                for sample in (a, b):
                    assert sample["raw_resolved"] and sample["P9_vector_passed"]
                    assert sample["P9_vector_difference_norm"] <= 1e-3 * sample["raw_defect_norm"]
                key = (grid["size"], old["direction_index"], old["amplitude"])
                if ratio > 0.5:
                    half_failures.append(key)
                if ratio > 1:
                    worsenings.append(key)
                legacy_passes[grid["size"]] += old["amplitude_passed"]
                counts += 1
    assert counts == 192 and len(half_failures) == 81 and len(worsenings) == 37
    assert legacy_passes == {17: 64, 33: 32, 65: 0}
    assert [(i, a) for n, i, a in half_failures if n == 65 and a == 0.008] == [
        (i, 0.008) for i in (0, 1, 2, 3, 4, 5, 7, 9, 11, 12, 16, 18, 21, 23, 25, 28, 29)
    ]
    assert [(i, a) for n, i, a in worsenings if n == 65] == [(i, 0.032) for i in range(32)]
    assert [(i, a) for n, i, a in worsenings if n == 33] == [(i, 0.032) for i in (2, 4, 7, 16, 23)]


def direction(completed, kind, index):
    return next(
        r
        for r in completed[0]["evidence"]["grids"][2]["directions"]
        if r["schedule"]["kind"] == kind and r["schedule"]["direction_index"] == index
    )


def test_counterexamples51_and52_have_distinct_failure_causes(completed):
    fit51 = direction(completed, "order", 51)["fit_prediction"]
    fit52 = direction(completed, "order", 52)["fit_prediction"]
    assert fit51["predicted_slopes"]["3"] == 4.10242111001829
    assert fit51["smallest_amplitude_ratio"] == 0.06908204448486943
    assert fit51["predicted_slopes"]["3"] > 4.1 and fit51["smallest_amplitude_ratio"] < 0.1
    assert fit52["predicted_slopes"]["3"] == 4.018103036707387
    assert fit52["smallest_amplitude_ratio"] == 0.10292376971677472
    assert 3.9 < fit52["predicted_slopes"]["3"] < 4.1 and fit52["smallest_amplitude_ratio"] > 0.1
    for fit in (fit51, fit52):
        assert fit["H3_passed"] and fit["original_fit"]["passed"] is False
        assert fit["predicted_original_H4_predicate"] is False


def test_leading_ratio_is_not_the_full_half_or_legacy_composite_predicate(completed):
    row = direction(completed, "amplitude", 0)
    n3 = row["profiles"]["2"]["primary"]["defect_coefficients"][3]["norm"]
    n4 = row["profiles"]["3"]["primary"]["defect_coefficients"][4]["norm"]
    case = row["cases"][0]
    assert case["original"]["amplitude"] == 0.008
    assert 0.008 * n4 / n3 < 0.5 < case["holdout_prediction"]["predicted_ratio"]
    case6 = direction(completed, "amplitude", 6)["cases"][0]
    assert case6["holdout_prediction"]["predicted_ratio"] <= 0.5
    assert case6["holdout_prediction"]["original_composite_H5"] is False


def test_worst_case_and_high_order_defect_contributions_are_reproduced(completed):
    case = direction(completed, "amplitude", 21)["cases"][-1]
    assert case["original"]["amplitude"] == 0.032
    assert case["original"]["cubic_to_quadratic_defect_ratio"] == 5.834017983080117
    assert case["holdout_prediction"]["predicted_ratio"] == 5.834017984274533
    assert case["holdout_prediction"]["original_composite_H5"] is False
    sample = case["models"]["3"]["samples"]["primary"]
    errors = {t["degree"]: t["relative_vector_error"] for t in sample["truncations"]}
    assert errors[4] == 0.9169766502506098
    assert errors[6] == 6.584932657101983e-5 and errors[9] < 4e-10
    assert sample["group_contribution_norms"][2] > sample["group_contribution_norms"][1]
    assert sample["tail_norm"] < 1e-14
    cross = 2 * fsum(sample["weighted_gram"][4][j] for j in range(5, 10))
    assert abs(cross - 1.0556511449794793e-9) < 1e-23
    # Degree 4/6/9 truncations of the existing W3 defect are not new charts.


def test_all_12480_gram_truncations_with_compensated_sums(completed):
    count = 0
    for grid in completed[0]["evidence"]["grids"]:
        for row in grid["directions"]:
            for case in row["cases"]:
                for model in case["models"].values():
                    assert set(model["samples"]) == {"primary"}
                    sample = model["samples"]["primary"]
                    for truncation in sample["truncations"]:
                        n = truncation["degree"] + 1
                        value = fsum(
                            sample["weighted_gram"][i][j] for i in range(n) for j in range(n)
                        )
                        assert value >= 0
                        assert (
                            abs(value - truncation["direct_norm_squared"])
                            <= truncation["gram_tolerance"]
                        )
                        count += 1
    assert count == 12480


def test_full_summary_and_all_1920_samples_reconstruction_maxima(completed):
    saved = completed[0]
    report = runner.summary(saved["evidence"]["grids"])
    assert report == saved["summary"]
    assert report["counts"] == {"directions": 288, "cases": 960, "profiles": 576}
    assert report["failure_counts"] == {
        k: 0 for k in ("incomplete", "H1", "H2", "H3", "Gram", "independent")
    }
    samples = [
        m["samples"]["primary"]
        for g in saved["evidence"]["grids"]
        for r in g["directions"]
        for c in r["cases"]
        for m in c["models"].values()
    ]
    assert len(samples) == 1920
    for key, maximum in report["maximum_reconstruction_error"].items():
        assert maximum["error_norm"] == max(s["reconstruction_errors"][key] for s in samples)
        assert maximum["error_norm"] <= maximum["roundoff_floor"]
    maximum = report["maximum_reconstruction_error"]["Phi_reconstructed"]
    assert maximum["size"] == 65 and maximum["kind"] == "order" and maximum["direction_index"] == 46
    assert maximum["degree"] == 3 and maximum["amplitude"] == 0.002
    assert maximum["error_norm"] == 4.244566574097749e-14
    assert maximum["roundoff_floor"] == 4.1140092794350784e-12


@pytest.mark.parametrize(
    "damage", ["omit51", "old_H4", "legacy_H5", "ratio", "C9", "tail", "last_coordinate"]
)
def test_last_grid_counterexamples_and_incomplete_evidence_are_rejected(completed, damage):
    saved, old, conserved, _ = completed
    grid = deepcopy(saved["evidence"]["grids"][2])
    order51 = next(
        r
        for r in grid["directions"]
        if r["schedule"]["kind"] == "order" and r["schedule"]["direction_index"] == 51
    )
    worst = next(
        r
        for r in grid["directions"]
        if r["schedule"]["kind"] == "amplitude" and r["schedule"]["direction_index"] == 21
    )
    last = grid["directions"][-1]
    if damage == "omit51":
        grid["directions"].remove(order51)
    elif damage == "old_H4":
        order51["fit_prediction"]["original_fit"]["passed"] = True
    elif damage == "legacy_H5":
        worst["cases"][-1]["holdout_prediction"]["original_composite_H5"] = True
    elif damage == "ratio":
        worst["cases"][-1]["holdout_prediction"]["predicted_ratio"] = 0.1
    elif damage == "C9":
        last["profiles"]["3"]["primary"]["defect_coefficients"].pop()
    elif damage == "tail":
        last["cases"][-1]["models"]["3"]["samples"]["primary"]["tail_norm"] += 1
    else:
        last["cases"][-1]["models"]["3"]["samples"]["primary"]["reconstructed_reduced_coordinates"][
            -1
        ] += 1
    assert not runner.audit_grid(grid, old[2], conserved[2], worker=False)["passed"]
