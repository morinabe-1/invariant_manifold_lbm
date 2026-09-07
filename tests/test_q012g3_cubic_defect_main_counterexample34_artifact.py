"""One main counterexample: reproduce the old H4 failure, not repair or relabel it."""

from copy import deepcopy
from math import fsum, log
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

OUTPUT = Path("research/artifacts/q012g3_d3q27_cubic_defect.json")
SHA = "49f71e876eb782e43086700fc777792df55d25303a9dd936588e4b44cbab6341"
SOURCE_DIGEST = "c7001e41d3ef7541d5f2c863a7fba714f95b0dc7a78f434555fdcf3f09f5e38a"
WORKER_OUTPUT = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay.json")
WORKER_SHA = "92061894ea332780273f3866816a1c1fb0784da842223d855e786c811031e1d8"


@pytest.fixture(scope="module")
def completed():
    schedule = next(
        s
        for s in runner.evidence.direction_schedule(worker=False)
        if s["kind"] == "order" and s["direction_index"] == 34
    )
    path = runner.direction_path(OUTPUT, 65, schedule)
    assert runner._file_sha256(path) == SHA
    saved = runner.read_json(path)
    assert saved["process_id"] == 35240 and saved["size"] == 65
    assert saved["source_digest_sha256"] == runner.source_digest(runner.metadata()) == SOURCE_DIGEST
    assert saved["direction_digest_sha256"] == runner.digest(saved["direction"])
    assert runner._all_numeric_values_finite(saved)
    assert runner._file_sha256(runner.prior.PARENT_PATH) == runner.prior.PARENT_SHA
    assert runner._file_sha256(runner.PRIOR_PATH) == runner.INPUT_SEALS[runner.PRIOR_PATH]
    originals, conserved, fits = runner.maps(
        runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"][2],
        runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"][2],
    )
    return saved, schedule, originals, conserved, fits[34]


def audit(row, completed):
    _, schedule, originals, conserved, fit = completed
    return runner.evidence.validate_direction(
        row, schedule, originals, fit, conserved, size=65, worker=False
    )


def slope(values):
    x, y = list(map(log, runner.parent.AMPLITUDES)), list(map(log, values))
    mx, my = fsum(x) / 4, fsum(y) / 4
    return fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / fsum(
        (a - mx) ** 2 for a in x
    )


def test_all_four_main_cases_and_applicable_gates(completed):
    row = completed[0]["direction"]
    assert audit(row, completed) == {
        "passed": True,
        "cases": 4,
        "profiles": 2,
        "original_fields": 24,
        "original_defects": 8,
        "independent_vector_comparisons": 0,
    }
    assert runner.evidence.direction_gates(row, worker=False) == {
        "all_gram_comparisons_passed": True,
        "independent_vectors_passed": None,
        "worker_both_arm_reconstruction_passed": None,
        "H1": True,
        "H2": None,
        "H3": True,
    }


def test_primary_scientific_record_matches_sealed_independent_worker(completed):
    saved, schedule, *_ = completed
    worker_path = runner.direction_path(WORKER_OUTPUT, 65, schedule)
    assert runner._file_sha256(worker_path) == WORKER_SHA
    worker = runner.read_json(worker_path)
    assert worker["process_id"] == 27060 != saved["process_id"]
    assert worker["size"] == 65 and worker["source_digest_sha256"] == SOURCE_DIGEST
    assert worker["direction_digest_sha256"] == runner.digest(worker["direction"])
    assert runner.evidence.primary_record(saved["direction"]) == runner.evidence.primary_record(
        worker["direction"]
    )
    assert all(
        set(model["samples"]) == {"primary"}
        for case in saved["direction"]["cases"]
        for model in case["models"].values()
    )


def test_failed_h4_and_the_measured_slopes_are_preserved(completed):
    row = completed[0]["direction"]
    fit = row["fit_prediction"]
    assert fit["original_fit"]["passed"] is False
    assert fit["predicted_original_H4_predicate"] is False
    assert fit["original_H4_predicate_matches"] and fit["H3_passed"]
    assert fit["original_fit"]["slopes"]["3"] == 4.103841695537577
    assert fit["predicted_slopes"]["3"] == 4.103894349187252
    for degree in ("2", "3"):
        predicted = slope(
            [c["models"][degree]["samples"]["primary"]["P9_norm"] for c in row["cases"]]
        )
        original = slope([c["original"]["models"][degree]["defect_norm"] for c in row["cases"]])
        assert abs(predicted - fit["predicted_slopes"][degree]) < 1e-12
        assert abs(original - fit["original_fit"]["slopes"][degree]) < 1e-12
        assert abs(predicted - original) <= 0.01
    smallest = row["cases"][-1]["models"]
    ratio = (
        smallest["3"]["samples"]["primary"]["P9_norm"]
        / smallest["2"]["samples"]["primary"]["P9_norm"]
    )
    old_ratio = fit["original_fit"]["smallest_amplitude_ratio"]
    assert old_ratio == 0.0801557831453807
    assert ratio == fit["smallest_amplitude_ratio"] == 0.08014626737054589
    assert abs(ratio - old_ratio) / old_ratio <= 0.01


def test_higher_defect_terms_reproduce_the_finite_window_slope(completed):
    row = completed[0]["direction"]
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
    # Every truncation refers to the same W3 defect, not to a new W4/W6/W9.


def test_all_52_primary_gram_truncations_with_compensated_sums(completed):
    compared = 0
    for case in completed[0]["direction"]["cases"]:
        for model in case["models"].values():
            assert set(model["samples"]) == {"primary"}
            sample = model["samples"]["primary"]
            weighted = sample["weighted_gram"]
            for truncation in sample["truncations"]:
                n = truncation["degree"] + 1
                value = fsum(weighted[i][j] for i in range(n) for j in range(n))
                assert value >= 0
                assert (
                    abs(value - truncation["direct_norm_squared"]) <= truncation["gram_tolerance"]
                )
                compared += 1
    assert compared == 52


@pytest.mark.parametrize(
    "damage", ["old_H4", "predicted_H4", "missing_C9", "last_case", "last_coordinate"]
)
def test_relabelling_and_missing_main_evidence_are_rejected(completed, damage):
    row = deepcopy(completed[0]["direction"])
    if damage == "old_H4":
        row["fit_prediction"]["original_fit"]["passed"] = True
    elif damage == "predicted_H4":
        row["fit_prediction"]["predicted_original_H4_predicate"] = True
    elif damage == "missing_C9":
        row["profiles"]["3"]["primary"]["defect_coefficients"].pop()
    elif damage == "last_case":
        row["cases"].pop()
    else:
        row["cases"][-1]["models"]["3"]["samples"]["primary"]["reconstructed_reduced_coordinates"][
            -1
        ] += 1
    with pytest.raises(runner.ERRORS):
        audit(row, completed)
