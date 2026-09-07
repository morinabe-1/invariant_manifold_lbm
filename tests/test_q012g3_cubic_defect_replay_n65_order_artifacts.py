"""Closed generic worker subset, not the full N65 grid or main campaign."""

from copy import deepcopy
from math import fsum, log
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

OUTPUT = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay.json")
SOURCE_DIGEST = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"
SEALS = {
    0: "22f4385d1f3c5f89e46ea51da5638f515cc37088c1bba9700ce9639d1307da3a",
    1: "caf010e2b022f233c4c6b8e25a0852dc42adeb32fe15191d9d80cff90a8b24fb",
    2: "6a2957cf181644f5ff22c68d2690bbe82c3ac58d7777f3612b5d2586b302a0f0",
    3: "d40ccf580779c16a8cd62a69a1249b58f11908042e1edac5eedf49e08e2b6c98",
    4: "06702c09bd5deb721b78635dc3d702606a00caa934e8f50555a594a5463ffdca",
    5: "c66b1ebe4b904e13400d34c784042acbeb8ac6c035124badb42690bc96e69cc4",
    6: "e4280987279e269dfe46f644fd007d68973c8314696379bafd33afced61f9b8f",
    7: "eea7a1468143025b84557f56630cea13f9faa22d1fb80f942910cfed5724a27f",
    34: "92061894ea332780273f3866816a1c1fb0784da842223d855e786c811031e1d8",
    51: "a2561c03fdd7005f4ced690272337a6d73def933a5ce9702d9e972aaa943fc87",
    52: "8ed0d85bcddb664b7faaa640bc1339f73cafaccbbf7bdf994aa482028736ba29",
}


@pytest.fixture(scope="module")
def completed():
    schedules = {
        s["direction_index"]: s
        for s in runner.evidence.direction_schedule(worker=True)
        if s["kind"] == "order"
    }
    assert list(schedules) == list(SEALS)
    assert runner.source_digest(runner.metadata()) == SOURCE_DIGEST
    assert runner._file_sha256(runner.prior.PARENT_PATH) == runner.prior.PARENT_SHA
    assert runner._file_sha256(runner.PRIOR_PATH) == runner.INPUT_SEALS[runner.PRIOR_PATH]
    original, conserved, fits = runner.maps(
        runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"][2],
        runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"][2],
    )
    rows = {}
    for index, schedule in schedules.items():
        path = runner.direction_path(OUTPUT, 65, schedule)
        assert runner._file_sha256(path) == SEALS[index]
        saved = runner.read_json(path)
        assert saved["size"] == 65 and saved["process_id"] == 27060
        assert saved["source_digest_sha256"] == SOURCE_DIGEST
        assert saved["direction_digest_sha256"] == runner.digest(saved["direction"])
        rows[index] = saved["direction"]
    return rows, schedules, original, conserved, fits


def audit(rows, completed):
    _, schedules, original, conserved, fits = completed
    assert list(rows) == list(schedules)
    totals = dict.fromkeys(
        (
            "cases",
            "profiles",
            "original_fields",
            "original_defects",
            "independent_vector_comparisons",
        ),
        0,
    )
    for index, row in rows.items():
        result = runner.evidence.validate_direction(
            row, schedules[index], original, fits[index], conserved, size=65, worker=True
        )
        assert result["passed"]
        for key in totals:
            totals[key] += result[key]
    return totals


def slope(values):
    x, y = list(map(log, runner.parent.AMPLITUDES)), list(map(log, values))
    mx, my = fsum(x) / 4, fsum(y) / 4
    return fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / fsum(
        (a - mx) ** 2 for a in x
    )


def test_all_registered_generic_worker_directions_and_gates(completed):
    rows = completed[0]
    assert audit(rows, completed) == {
        "cases": 44,
        "profiles": 22,
        "original_fields": 264,
        "original_defects": 88,
        "independent_vector_comparisons": 803,
    }
    for row in rows.values():
        assert runner.evidence.direction_gates(row, worker=True) == {
            "all_gram_comparisons_passed": True,
            "independent_vectors_passed": True,
            "worker_both_arm_reconstruction_passed": True,
            "H1": True,
            "H2": None,
            "H3": True,
        }


def test_independent_ols_and_all_three_old_failures_are_preserved(completed):
    rows = completed[0]
    for index, row in rows.items():
        fit = row["fit_prediction"]
        assert fit["original_fit"]["passed"] is (index not in (34, 51, 52))
        assert fit["predicted_original_H4_predicate"] is fit["original_fit"]["passed"]
        assert fit["original_H4_predicate_matches"] and fit["H3_passed"]
        for d in ("2", "3"):
            predicted = slope(
                [c["models"][d]["samples"]["primary"]["P9_norm"] for c in row["cases"]]
            )
            original = slope([c["original"]["models"][d]["defect_norm"] for c in row["cases"]])
            assert abs(predicted - fit["predicted_slopes"][d]) < 1e-12
            assert abs(original - fit["original_fit"]["slopes"][d]) < 1e-12
            assert abs(predicted - original) <= 0.01
        assert fit["ratio_relative_error"] <= 0.01


def test_direction_51_reproduces_slope_excess_with_higher_defect_degrees(completed):
    row = completed[0][51]
    fit = row["fit_prediction"]
    assert fit["original_fit"]["slopes"]["3"] == 4.102353999806372
    assert fit["predicted_slopes"]["3"] == 4.10242111001829
    for n, expected in ((4, 3.9999999992928137), (5, 4.083366963321555), (6, 4.102421242714545)):
        norms = [
            next(
                t["norm"]
                for t in c["models"]["3"]["samples"]["primary"]["truncations"]
                if t["degree"] == n
            )
            for c in row["cases"]
        ]
        assert all(
            v > c["original"]["roundoff_floor"] for v, c in zip(norms, row["cases"], strict=True)
        )
        assert abs(slope(norms) - expected) < 1e-12
    assert fit["original_fit"]["smallest_amplitude_ratio"] <= 0.1
    assert fit["smallest_amplitude_ratio"] <= 0.1


def test_direction_52_is_a_ratio_failure_not_a_slope_failure(completed):
    row = completed[0][52]
    fit = row["fit_prediction"]
    assert fit["original_fit"]["smallest_amplitude_ratio"] == 0.10292984357429616
    assert fit["smallest_amplitude_ratio"] == 0.10292376971677472
    assert fit["smallest_amplitude_ratio"] > 0.1
    for slopes in (fit["predicted_slopes"], fit["original_fit"]["slopes"]):
        assert 2.9 <= slopes["2"] <= 3.1 and 3.9 <= slopes["3"] <= 4.1
    n3 = row["profiles"]["2"]["primary"]["defect_coefficients"][3]["norm"]
    n4 = row["profiles"]["3"]["primary"]["defect_coefficients"][4]["norm"]
    leading_ratio = 0.001 * n4 / n3
    assert abs(leading_ratio - 0.10310158966562488) < 1e-15
    assert leading_ratio > 0.1
    # Leading norms are descriptive; do not replace the signed Gram sum with them.
    case = row["cases"][-1]
    direct_ratio = (
        case["models"]["3"]["samples"]["primary"]["P9_norm"]
        / case["models"]["2"]["samples"]["primary"]["P9_norm"]
    )
    assert direct_ratio == fit["smallest_amplitude_ratio"]
    assert direct_ratio != leading_ratio


def test_all_1144_gram_truncation_norms_with_compensated_sums(completed):
    count = 0
    for row in completed[0].values():
        for case in row["cases"]:
            for model in case["models"].values():
                for sample in model["samples"].values():
                    weighted = sample["weighted_gram"]
                    for truncation in sample["truncations"]:
                        n = truncation["degree"] + 1
                        value = fsum(weighted[i][j] for i in range(n) for j in range(n))
                        assert value >= 0
                        assert (
                            abs(value - truncation["direct_norm_squared"])
                            <= truncation["gram_tolerance"]
                        )
                        count += 1
    assert count == 1144


@pytest.mark.parametrize(
    "damage", ["missing_51", "old_H4_52", "ratio_52", "last_case_52", "missing_C9_51"]
)
def test_counterexamples_cannot_be_dropped_or_relabelled(completed, damage):
    rows = deepcopy(completed[0])
    if damage == "missing_51":
        rows.pop(51)
    elif damage == "old_H4_52":
        rows[52]["fit_prediction"]["original_fit"]["passed"] = True
    elif damage == "ratio_52":
        rows[52]["fit_prediction"]["smallest_amplitude_ratio"] = 0.09
    elif damage == "last_case_52":
        rows[52]["cases"].pop()
    else:
        rows[51]["profiles"]["3"]["independent"]["defect_coefficients"].pop()
    with pytest.raises(runner.ERRORS):
        audit(rows, completed)
