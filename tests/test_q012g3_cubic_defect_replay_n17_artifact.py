"""Closed first grid only: not the full 192-case worker or 960-case main verdict."""

from copy import deepcopy
from math import fsum, log
from pathlib import Path

import pytest

from research import q012g3_d3q27_cubic_defect as runner

OUTPUT = Path("research/artifacts/q012g3_d3q27_cubic_defect_replay.json")
PATH = runner.parent.grid_path(OUTPUT, 17)
SHA = "273ce8b5ee72e9220d935e147d96ba0f412abf7364d8ded5b51fdd2dc4349329"
GRID_DIGEST = "09c0743605aa4ffb85264fafd3eeda8343afc332aa97d41748a8ddba0e0cbb4c"
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
    old = runner.read_json(runner.prior.PARENT_PATH)["cycle"]["grids"][0]
    conserved = runner.read_json(runner.PRIOR_PATH)["evidence"]["grids"][0]
    return saved, old, conserved


def test_all_64_cases_42_profiles_and_1533_full_vector_comparisons(completed):
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


def test_all_21_direction_artifacts_match_the_saved_grid(completed):
    saved, _, _ = completed
    assert len(saved["direction_artifacts"]) == len(saved["grid"]["directions"]) == 21
    for entry, row in zip(saved["direction_artifacts"], saved["grid"]["directions"], strict=True):
        path = runner.direction_path(OUTPUT, 17, row["schedule"])
        assert entry["filename"] == path.name and entry["sha256"] == runner._file_sha256(path)
        child = runner.read_json(path)
        assert child["direction"] == row and child["direction_digest_sha256"] == runner.digest(row)
        assert child["process_id"] == saved["process_id"] and child["size"] == 17
        assert child["source_digest_sha256"] == SOURCE_DIGEST
        assert child["generated_at_utc"] == saved["generated_at_utc"]
        assert runner._all_numeric_values_finite(child)


def slope(values):
    x, y = list(map(log, runner.parent.AMPLITUDES)), list(map(log, values))
    mx, my = fsum(x) / 4, fsum(y) / 4
    return fsum((a - mx) * (b - my) for a, b in zip(x, y, strict=True)) / fsum(
        (a - mx) ** 2 for a in x
    )


def test_all_11_generic_fits_with_independent_closed_least_squares(completed):
    saved, _, _ = completed
    rows = [r for r in saved["grid"]["directions"] if r["schedule"]["kind"] == "order"]
    assert len(rows) == 11
    for row in rows:
        prediction = row["fit_prediction"]
        for d in ("2", "3"):
            samples = [c["models"][d]["samples"]["primary"] for c in row["cases"]]
            measured = slope([s["P9_norm"] for s in samples])
            assert abs(measured - prediction["predicted_slopes"][d]) < 1e-12
            original = slope([c["original"]["models"][d]["defect_norm"] for c in row["cases"]])
            assert abs(original - prediction["original_fit"]["slopes"][d]) < 1e-12
            assert abs(measured - original) <= 0.01
        smallest = row["cases"][-1]["models"]
        ratio = (
            smallest["3"]["samples"]["primary"]["P9_norm"]
            / smallest["2"]["samples"]["primary"]["P9_norm"]
        )
        assert ratio == prediction["smallest_amplitude_ratio"]
        assert prediction["H3_passed"] and prediction["original_H4_predicate_matches"]


def test_all_20_holdouts_preserve_vector_accuracy_and_defect_only_predicates(completed):
    saved, _, _ = completed
    cases = [
        c
        for r in saved["grid"]["directions"]
        if r["schedule"]["kind"] == "amplitude"
        for c in r["cases"]
    ]
    assert len(cases) == 20
    for case in cases:
        prediction = case["holdout_prediction"]
        a, b = (case["models"][str(d)]["samples"]["primary"] for d in (2, 3))
        ratio = b["P9_norm"] / a["P9_norm"]
        old = case["original"]["cubic_to_quadratic_defect_ratio"]
        assert prediction["predicted_ratio"] == ratio
        assert (ratio <= 0.5) == (old <= 0.5) and (ratio > 1) == (old > 1)
        for sample in (a, b):
            assert sample["raw_resolved"]
            assert sample["P9_vector_difference_norm"] <= 1e-3 * sample["raw_defect_norm"]
        assert prediction["H2_passed"]
        assert prediction["original_composite_H5"] == case["original"]["amplitude_passed"]


def test_gram_norms_with_fsum_instead_of_matrix_multiplication(completed):
    saved, _, _ = completed
    compared = 0
    for row in saved["grid"]["directions"]:
        for case in row["cases"]:
            for d, data in case["models"].items():
                for arm, sample in data["samples"].items():
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
                    assert len(row["profiles"][d][arm]["gram"]) == 10
    assert compared == 1664  # 64 cases * 2 arms * (7 quadratic + 6 cubic truncations).


@pytest.mark.parametrize(
    "damage", ["last_case", "C9_comparison", "tail", "exact_field", "fit", "H2"]
)
def test_last_case_and_coefficient_damage_cannot_survive_the_full_grid_audit(completed, damage):
    saved, old, conserved = completed
    grid = deepcopy(saved["grid"])
    direction = grid["directions"][-1]
    case = direction["cases"][-1]
    if damage == "last_case":
        direction["cases"].pop()
    elif damage == "C9_comparison":
        direction["profiles"]["3"]["comparison"]["rows"][-1]["passed"] = False
    elif damage == "tail":
        case["models"]["3"]["samples"]["independent"]["tail_norm"] += 1
    elif damage == "exact_field":
        case["models"]["3"]["conservation_fields"]["W_R"]["population_sums"][-1]["numerator"] = "0"
    elif damage == "fit":
        grid["directions"][10]["fit_prediction"]["predicted_slopes"]["3"] += 0.001
    else:
        case["holdout_prediction"]["H2_passed"] = False
    assert not runner.audit_grid(grid, old, conserved, worker=True)["passed"]
