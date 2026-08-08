from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007o_external_complement_radius as q007o
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007o_artifact() -> dict:
    artifact_path = (
        Path(q007o.__file__).resolve().parent
        / "artifacts"
        / "q007o_external_complement_radius.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007o_accepts_the_registered_resolvent_refinement(
    q007o_artifact,
) -> None:
    cycle = q007o_artifact["cycle"]
    search = cycle["radius_comparison"]["refined_radius_search"]
    selected = search["selected_candidate"]
    previous = search["previous_larger_candidate"]

    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "exact external-complement resolvent strictly sharpens the "
        "registered explicit radius"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert search["candidate_count"] == len(q007o.CANDIDATE_EXPONENTS) == 119
    assert search["passing_candidate_count"] == 103
    assert selected["candidate_exponent"] == 18
    assert selected["modal_radius_decimal"] == "1e-18"
    assert selected["passed"]
    assert selected["is_largest_passing_registered_candidate"]
    assert previous["candidate_exponent"] == 17
    assert not previous["passed"]
    assert cycle["radius_comparison"][
        "q007n_candidate_passes_with_refined_inverse"
    ]


def test_q007o_certifies_both_external_coordinate_systems(
    q007o_artifact,
) -> None:
    refinement = q007o_artifact["cycle"][
        "external_complement_inverse_refinement"
    ]
    gap = _fraction(refinement["all_degree_gap_lower_reused_from_q007n"])
    records = refinement["representative_records"]

    assert [record["wave_index"] for record in records] == [[1, 0], [1, 1]]
    assert [record["q007h1_source_wave_index"] for record in records] == [
        [-1, 0],
        [-1, -1],
    ]
    assert [record["selector_rows"] for record in records] == [
        [0, 1, 2, 3, 7, 8],
        [0, 1, 2, 3, 4, 5],
    ]
    for record in records:
        defect = _fraction(record["coordinate_defect_l1_upper"])
        gamma = _fraction(record["representation_perturbation_gamma"])
        margin = _fraction(record["all_degree_gap_margin"])
        chart = _fraction(record["chart_internal_inverse_l1_upper"])
        reduced = _fraction(record["weighted_reduced_inverse_upper"])
        pair = _fraction(record["pair_internal_inverse_upper"])

        assert record["q007h1_proof_digest_matches"]
        assert record["selected_count"] == 3
        assert record["external_count"] == 6
        assert defect < Fraction(1, 10**8)
        assert gamma < gap / 2
        assert margin == gap - gamma > 0
        assert pair == max(chart, reduced)
        assert record["coordinate_certificate_passed"]


def test_q007o_inverse_improvement_is_exact_and_external_limited(
    q007o_artifact,
) -> None:
    refinement = q007o_artifact["cycle"][
        "external_complement_inverse_refinement"
    ]
    representative_pair_bounds = [
        _fraction(record["pair_internal_inverse_upper"])
        for record in refinement["representative_records"]
    ]
    raw_internal = _fraction(refinement["raw_internal_pair_inverse_upper"])
    working_internal = _fraction(
        refinement["working_internal_pair_inverse_upper"]
    )
    external = _fraction(refinement["q007n_external_inverse_upper"])
    zero = _fraction(refinement["q007n_zero_inverse_upper"])
    raw_total = _fraction(refinement["raw_total_pair_inverse_upper"])
    working_total = _fraction(refinement["working_total_pair_inverse_upper"])
    old = _fraction(refinement["q007n_pair_inverse_upper"])
    reduction_factor = _fraction(
        refinement["pair_inverse_upper_reduction_factor"]
    )

    assert raw_internal == max(representative_pair_bounds)
    assert raw_internal <= working_internal <= Fraction(10**14)
    assert raw_total == max(raw_internal, external, zero) == external
    assert raw_total <= working_total < old
    assert reduction_factor == old / working_total
    assert reduction_factor >= Fraction(10**40)


def test_q007o_boundary_satisfies_the_exact_radii_inequality(
    q007o_artifact,
) -> None:
    boundary = q007o_artifact["cycle"]["radius_comparison"][
        "refined_radius_search"
    ]["exact_boundary_certificate"]
    selected = boundary["selected"]
    previous = boundary["previous_larger"]

    y_bound = _fraction(selected["y_bound"])
    tau = _fraction(selected["correction_radius"])
    contraction = _fraction(selected["contraction_bound"])
    margin = _fraction(selected["radii_margin"])
    assert y_bound > 0
    assert tau == 2 * y_bound
    assert contraction < Fraction(1, 2)
    assert margin == tau - (y_bound + contraction * tau)
    assert margin > 0
    assert _fraction(selected["density_buffer"]) > 0
    assert _fraction(selected["reduced_range_buffer"]) > 0
    assert selected["passed"]

    previous_contraction = _fraction(previous["contraction_bound"])
    previous_margin = _fraction(previous["radii_margin"])
    assert previous_contraction > Fraction(1, 2)
    assert previous_margin < 0
    assert not previous["passed"]


def test_q007o_reuses_q007n_and_records_runner_provenance(
    q007o_artifact,
) -> None:
    cycle = q007o_artifact["cycle"]
    runner_path = Path(q007o.__file__).resolve()

    assert q007o_artifact["schema_version"] == 1
    assert q007o_artifact["source"] == source_metadata()
    assert q007o_artifact["runner_source"] == {
        "filename": "q007o_external_complement_radius.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert all(record["passed"] for record in cycle["input_artifacts"].values())
    assert {
        name: record["sha256"]
        for name, record in cycle["input_artifacts"].items()
    } == q007o.REGISTERED_INPUT_SHA256
    reuse = cycle["q007n_reuse_audit"]
    assert reuse["old_119_candidate_records_reproduced_exactly"]
    assert reuse["candidate_exponents_match"]
    assert reuse["candidate_count_match"]
    assert reuse["only_pair_inverse_changed_in_new_scan"]
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert "not an optimal radius" in cycle["claim_boundary"]
    assert "finite-ball normal attraction" in cycle["claim_boundary"]
    json.dumps(q007o_artifact, allow_nan=False)
