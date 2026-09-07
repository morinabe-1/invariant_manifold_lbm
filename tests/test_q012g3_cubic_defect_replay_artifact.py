"""Full independent worker readback; this is not the 960-case main verdict."""

from copy import deepcopy
from math import fsum
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

PATH = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay.json")
SHA = "546f99edfe101dccd770dcf559bf3a9394eec84c463c0e2b05895c11430f4628"
EVIDENCE_DIGEST = "06332e8070f549040a49c70a558dd562034ba31d58c0ec47ff46bfca5fbd624b"
SOURCE_DIGEST = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"
GRID_SEALS = {
    17: "273ce8b5ee72e9220d935e147d96ba0f412abf7364d8ded5b51fdd2dc4349329",
    33: "777559e4ffebb723f3dd5b3c42880bb06ea137711a8babac8f011c1039be0c23",
    65: "4e08f3440d38930b3f35edef5a22b6c5ed93d529ffe73e0922e78b0d7ee89de2",
}


@pytest.fixture(scope="module")
def completed():
    assert runner._file_sha256(PATH) == SHA
    saved = runner.read_json(PATH)
    assert saved["evidence_digest_sha256"] == runner.digest(saved["evidence"]) == EVIDENCE_DIGEST
    assert runner.source_digest(saved) == runner.source_digest(runner.metadata()) == SOURCE_DIGEST
    assert saved["process_id"] == 27060
    for size, sha in GRID_SEALS.items():
        assert runner._file_sha256(runner.parent.grid_path(PATH, size)) == sha
    old = runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"]
    conserved = runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"]
    # This performs the fresh full input-chain audit and all saved-child checks.
    audit = runner.audit_document(saved, PATH, old, conserved, worker=True)
    assert audit["passed"], audit
    return saved, old, conserved, audit


def test_full_192_cases_and_worker_only_boundary(completed):
    saved, _, _, audit = completed
    assert {k: v for k, v in audit.items() if k != "grids"} == {
        "passed": True,
        "cases": 192,
        "profiles": 126,
        "independent_vector_comparisons": 4599,
    }
    assert len(audit["grids"]) == 3
    assert sum(g["original_fields"] for g in audit["grids"]) == 1152
    assert sum(g["original_defects"] for g in audit["grids"]) == 384
    decision = saved["decision"]
    assert len(decision["validity_gates"]) == 10 and all(decision["validity_gates"].values())
    assert decision["hypothesis_gates"] == {"H1": True, "H2": True, "H3": True}
    assert decision["study_gate"] == "passed"
    assert decision["scientific_outcome"] == "worker_only"
    assert saved["source_unchanged_after"] and saved["inputs_unchanged_after"]
    controls = saved["evidence"]["controls"]
    assert controls["passed_tests"] == 177 and controls["exit_code"] == 0
    assert controls["test_sources"] == runner.control_seals()
    assert "177 passed" in saved["control_execution_output"]["stdout"]
    assert saved["control_execution_output"]["stderr"] == ""


def test_all_63_direction_seals_and_shared_headers(completed):
    saved = completed[0]
    count = 0
    for grid in saved["evidence"]["grids"]:
        child = runner.read_json(runner.parent.grid_path(PATH, grid["size"]))
        assert child["grid"] == grid
        assert len(child["direction_artifacts"]) == len(grid["directions"]) == 21
        for row, seal in zip(grid["directions"], child["direction_artifacts"], strict=True):
            path = runner.direction_path(PATH, grid["size"], row["schedule"])
            assert seal["filename"] == path.name and seal["sha256"] == runner._file_sha256(path)
            record = runner.read_json(path)
            assert record["direction"] == row
            assert record["direction_digest_sha256"] == runner.digest(row)
            assert all(record[k] == v for k, v in runner.header(saved).items())
            count += 1
    assert count == 63


def test_original_failures_are_preserved_across_all_three_grids(completed):
    half_failures, worsenings, generic_failures = [], [], []
    counts = {"order": 0, "amplitude": 0}
    for grid in completed[0]["evidence"]["grids"]:
        for row in grid["directions"]:
            kind = row["schedule"]["kind"]
            counts[kind] += 1
            if kind == "order":
                fit = row["fit_prediction"]
                assert fit["predicted_original_H4_predicate"] is fit["original_fit"]["passed"]
                assert fit["H3_passed"]
                if not fit["original_fit"]["passed"]:
                    generic_failures.append((grid["size"], row["schedule"]["direction_index"]))
                continue
            for case in row["cases"]:
                original, prediction = case["original"], case["holdout_prediction"]
                a, b = (case["models"][str(d)]["samples"]["primary"] for d in (2, 3))
                ratio = b["P9_norm"] / a["P9_norm"]
                old_ratio = original["cubic_to_quadratic_defect_ratio"]
                assert prediction["predicted_ratio"] == ratio
                assert (ratio <= 0.5) == (old_ratio <= 0.5)
                assert (ratio > 1) == (old_ratio > 1)
                assert prediction["original_composite_H5"] is original["amplitude_passed"]
                assert prediction["H2_passed"]
                for sample in (a, b):
                    assert sample["raw_resolved"] and sample["P9_vector_passed"]
                    assert sample["P9_vector_difference_norm"] <= 1e-3 * sample["raw_defect_norm"]
                key = (grid["size"], original["direction_index"], original["amplitude"])
                if ratio > 0.5:
                    half_failures.append(key)
                if ratio > 1:
                    worsenings.append(key)
    assert counts == {"order": 33, "amplitude": 30}
    assert generic_failures == [(65, 34), (65, 51), (65, 52)]
    assert len(half_failures) == 29 and len(worsenings) == 14
    assert [(i, a) for n, i, a in half_failures if n == 65 and a == 0.008] == [
        (i, 0.008) for i in (0, 1, 2, 3, 4, 5, 7, 16, 21)
    ]
    assert [(i, a) for n, i, a in worsenings if n == 65] == [
        (i, 0.032) for i in (0, 1, 2, 3, 4, 5, 6, 7, 16, 21)
    ]


def holdout(completed, index):
    return next(
        row
        for row in completed[0]["evidence"]["grids"][2]["directions"]
        if row["schedule"]["kind"] == "amplitude" and row["schedule"]["direction_index"] == index
    )


def test_leading_only_ratio_can_misclassify_the_half_predicate(completed):
    row = holdout(completed, 0)
    n3 = row["profiles"]["2"]["primary"]["defect_coefficients"][3]["norm"]
    n4 = row["profiles"]["3"]["primary"]["defect_coefficients"][4]["norm"]
    case = row["cases"][0]
    assert case["original"]["amplitude"] == 0.008
    assert 0.008 * n4 / n3 < 0.5 < case["holdout_prediction"]["predicted_ratio"]
    # Conversely, a passing defect ratio is not a passing legacy H5 composite.
    case6 = holdout(completed, 6)["cases"][0]
    assert case6["holdout_prediction"]["predicted_ratio"] <= 0.5
    assert case6["holdout_prediction"]["original_composite_H5"] is False


def test_worst_original_case_is_reproduced_not_repaired(completed):
    row = holdout(completed, 21)
    case = row["cases"][-1]
    assert case["original"]["amplitude"] == 0.032
    assert case["original"]["cubic_to_quadratic_defect_ratio"] == 5.834017983080117
    assert case["holdout_prediction"]["predicted_ratio"] == 5.834017984274533
    assert case["holdout_prediction"]["original_composite_H5"] is False
    sample = case["models"]["3"]["samples"]["primary"]
    truncations = {t["degree"]: t for t in sample["truncations"]}
    assert truncations[4]["relative_vector_error"] == 0.9169766502506098
    assert truncations[6]["relative_vector_error"] == 6.584932657101983e-5
    assert truncations[9]["relative_vector_error"] < 4e-10
    assert sample["group_contribution_norms"][2] > sample["group_contribution_norms"][1]
    assert sample["tail_norm"] < 1e-14
    cross = 2 * fsum(sample["weighted_gram"][4][j] for j in range(5, 10))
    assert abs(cross - 1.0556511449794793e-9) < 1e-23


def test_all_4992_gram_truncation_norms_with_compensated_sums(completed):
    count = 0
    for grid in completed[0]["evidence"]["grids"]:
        for row in grid["directions"]:
            for case in row["cases"]:
                for model in case["models"].values():
                    for sample in model["samples"].values():
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
    assert count == 4992


def test_full_summary_and_768_samples_reconstruction_maxima(completed):
    saved = completed[0]
    report = runner.summary(saved["evidence"]["grids"])
    assert report == saved["summary"]
    assert report["counts"] == {"directions": 63, "cases": 192, "profiles": 126}
    assert report["failure_counts"] == {
        k: 0 for k in ("incomplete", "H1", "H2", "H3", "Gram", "independent")
    }
    samples = [
        s
        for g in saved["evidence"]["grids"]
        for r in g["directions"]
        for c in r["cases"]
        for m in c["models"].values()
        for s in m["samples"].values()
    ]
    assert len(samples) == 768
    for key, maximum in report["maximum_reconstruction_error"].items():
        assert maximum["error_norm"] == max(s["reconstruction_errors"][key] for s in samples)
        assert maximum["error_norm"] <= maximum["roundoff_floor"]


@pytest.mark.parametrize(
    "damage", ["worst_direction", "legacy_H5", "ratio", "C9", "last_coordinate"]
)
def test_last_grid_counterexamples_and_missing_evidence_are_rejected(completed, damage):
    saved, old, conserved, _ = completed
    grid = deepcopy(saved["evidence"]["grids"][2])
    row = next(
        r
        for r in grid["directions"]
        if r["schedule"]["kind"] == "amplitude" and r["schedule"]["direction_index"] == 21
    )
    case = row["cases"][-1]
    if damage == "worst_direction":
        grid["directions"].remove(row)
    elif damage == "legacy_H5":
        case["holdout_prediction"]["original_composite_H5"] = True
    elif damage == "ratio":
        case["holdout_prediction"]["predicted_ratio"] = 0.1
    elif damage == "C9":
        row["profiles"]["3"]["independent"]["defect_coefficients"].pop()
    else:
        case["models"]["3"]["samples"]["independent"]["reconstructed_reduced_coordinates"][-1] += 1
    assert not runner.audit_grid(grid, old[2], conserved[2], worker=True)["passed"]
