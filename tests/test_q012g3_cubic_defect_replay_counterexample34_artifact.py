"""One registered counterexample only: preserve H4 failure while auditing H3 replay."""

from copy import deepcopy
from math import fsum, log
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

OUTPUT = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay.json")
SHA = "92061894ea332780273f3866816a1c1fb0784da842223d855e786c811031e1d8"
SOURCE_DIGEST = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"


@pytest.fixture(scope="module")
def completed():
    schedule = next(
        x
        for x in runner.evidence.direction_schedule(worker=True)
        if x["kind"] == "order" and x["direction_index"] == 34
    )
    path = runner.direction_path(OUTPUT, 65, schedule)
    assert runner._file_sha256(path) == SHA
    saved = runner.read_json(path)
    row = saved["direction"]
    assert saved["process_id"] == 27060 and saved["size"] == 65
    assert saved["source_digest_sha256"] == runner.source_digest(runner.metadata()) == SOURCE_DIGEST
    assert saved["direction_digest_sha256"] == runner.digest(row)
    assert runner._file_sha256(runner.prior.PARENT_PATH) == runner.prior.PARENT_SHA
    assert runner._file_sha256(runner.PRIOR_PATH) == runner.INPUT_SEALS[runner.PRIOR_PATH]
    original, conserved, fits = runner.maps(
        runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"][2],
        runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"][2],
    )
    return row, schedule, original, conserved, fits[34]


def audit(row, completed):
    _, schedule, original, conserved, fit = completed
    return runner.evidence.validate_direction(
        row, schedule, original, fit, conserved, size=65, worker=True
    )


def slope(values):
    x, y = list(map(log, runner.parent.AMPLITUDES)), list(map(log, values))
    mx, my = fsum(x) / 4, fsum(y) / 4
    return fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / fsum(
        (a - mx) ** 2 for a in x
    )


def test_all_four_cases_and_73_independent_comparisons(completed):
    row = completed[0]
    assert audit(row, completed) == {
        "passed": True,
        "cases": 4,
        "profiles": 2,
        "original_fields": 24,
        "original_defects": 8,
        "independent_vector_comparisons": 73,
    }
    assert runner.evidence.direction_gates(row, worker=True) == {
        "all_gram_comparisons_passed": True,
        "independent_vectors_passed": True,
        "worker_both_arm_reconstruction_passed": True,
        "H1": True,
        "H2": None,
        "H3": True,
    }


def test_the_old_failed_h4_is_not_relabelled_as_a_success(completed):
    row = completed[0]
    fit = row["fit_prediction"]
    assert fit["original_fit"]["passed"] is False
    assert fit["predicted_original_H4_predicate"] is False
    assert fit["original_H4_predicate_matches"] and fit["H3_passed"]
    assert fit["original_fit"]["slopes"]["3"] == 4.103841695537577
    assert fit["predicted_slopes"]["3"] == 4.103894349187252
    for d in ("2", "3"):
        measured = slope([c["models"][d]["samples"]["primary"]["P9_norm"] for c in row["cases"]])
        original = slope([c["original"]["models"][d]["defect_norm"] for c in row["cases"]])
        assert abs(measured - fit["predicted_slopes"][d]) < 1e-12
        assert abs(original - fit["original_fit"]["slopes"][d]) < 1e-12
        assert abs(measured - original) <= 0.01
    assert fit["ratio_relative_error"] <= 0.01


def test_all_truncated_defect_slopes_are_descriptive_not_new_chart_orders(completed):
    row = completed[0]
    expected = {
        4: 3.9999999998584626,
        5: 4.077688458854748,
        6: 4.1038942623554435,
        7: 4.1038943491498046,
        8: 4.103894349184237,
        9: 4.103894349187255,
    }
    for degree, reference in expected.items():
        norms = [
            next(
                t["norm"]
                for t in c["models"]["3"]["samples"]["primary"]["truncations"]
                if t["degree"] == degree
            )
            for c in row["cases"]
        ]
        assert all(
            v > c["original"]["roundoff_floor"] for v, c in zip(norms, row["cases"], strict=True)
        )
        assert abs(slope(norms) - reference) < 1e-12


def test_all_104_gram_truncation_norms_with_compensated_sums(completed):
    compared = 0
    for case in completed[0]["cases"]:
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
                    compared += 1
    assert compared == 104


@pytest.mark.parametrize(
    "damage", ["old_H4", "predicted_H4", "missing_C9", "last_case", "last_coordinate"]
)
def test_counterexample_relabelling_and_missing_evidence_are_rejected(completed, damage):
    row = deepcopy(completed[0])
    if damage == "old_H4":
        row["fit_prediction"]["original_fit"]["passed"] = True
    elif damage == "predicted_H4":
        row["fit_prediction"]["predicted_original_H4_predicate"] = True
    elif damage == "missing_C9":
        row["profiles"]["3"]["independent"]["defect_coefficients"].pop()
    elif damage == "last_case":
        row["cases"].pop()
    else:
        row["cases"][-1]["models"]["3"]["samples"]["independent"][
            "reconstructed_reduced_coordinates"
        ][-1] += 1
    with pytest.raises(runner.ERRORS):
        audit(row, completed)
