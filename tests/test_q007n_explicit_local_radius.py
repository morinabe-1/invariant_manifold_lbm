from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007n_explicit_local_radius as q007n
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007n_artifact() -> dict:
    artifact_path = (
        Path(q007n.__file__).resolve().parent
        / "artifacts"
        / "q007n_explicit_local_radius.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007n_certifies_the_largest_registered_modal_radius(
    q007n_artifact,
) -> None:
    cycle = q007n_artifact["cycle"]
    search = cycle["radius_search"]
    selected = search["selected_candidate"]
    previous = search["previous_larger_candidate"]

    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered quartic-centered contraction gives an explicit "
        "fixed-leaf local radius"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert search["candidate_count"] == len(q007n.CANDIDATE_EXPONENTS) == 119
    assert search["passing_candidate_count"] == 46
    assert selected["candidate_exponent"] == 75
    assert selected["modal_radius_decimal"] == "1e-75"
    assert selected["passed"]
    assert selected["is_largest_passing_registered_candidate"]
    assert previous["candidate_exponent"] == 74
    assert not previous["passed"]
    passing_exponents = [
        record["candidate_exponent"]
        for record in search["records"]
        if record["passed"]
    ]
    assert passing_exponents == list(range(75, 121))


def test_q007n_boundary_certificate_satisfies_the_exact_radii_inequality(
    q007n_artifact,
) -> None:
    boundary = q007n_artifact["cycle"]["radius_search"][
        "exact_boundary_certificate"
    ]
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


def test_q007n_records_the_registered_all_degree_inverse_and_majorants(
    q007n_artifact,
) -> None:
    cycle = q007n_artifact["cycle"]
    inverse = cycle["spectral_separation_and_inverse"]
    coefficients = cycle["coefficient_reproduction_and_norms"]
    structure = cycle["structural_majorant_audit"]

    raw_gap = _fraction(inverse["raw_uniform_absolute_gap_lower"])
    working_gap = _fraction(inverse["working_uniform_absolute_gap_lower"])
    assert 0 < working_gap <= raw_gap
    assert inverse["pair_homological_inverse_upper"]["float"] > 1.0e70
    assert inverse[
        "maximum_representative_eigenvector_infinity_norm_upper"
    ]["float"] < 9.0
    assert inverse["maximum_augmented_entry_absolute_upper"]["float"] < 2.0
    assert inverse["representative_proof_reconstruction"][
        "proof_digest_mismatch_count"
    ] == 0
    assert coefficients["matches"]
    assert coefficients["all_coefficients_finite"]
    assert coefficients["majorant_outward_decimal_grid_digits"] == 80
    assert len(coefficients["degree_records"]) == 3
    assert all(
        record["working_chart_operator_norm_upper"]["float"] > 0
        and record["working_reduced_operator_norm_upper"]["float"] > 0
        for record in coefficients["degree_records"]
    )
    assert _fraction(structure["nonlinear_majorant_constant"]) == Fraction(
        21, 2
    )
    assert structure["collision_conserves_three_moments_exactly"]
    assert structure["passed"]


def test_q007n_records_input_and_runner_provenance(q007n_artifact) -> None:
    cycle = q007n_artifact["cycle"]
    runner_path = Path(q007n.__file__).resolve()

    assert q007n_artifact["schema_version"] == 1
    assert q007n_artifact["source"] == source_metadata()
    assert q007n_artifact["runner_source"] == {
        "filename": "q007n_explicit_local_radius.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert q007n_artifact["study_gate"] == "passed"
    assert q007n_artifact["scientific_outcome"] == "accepted"
    assert all(record["passed"] for record in cycle["input_artifacts"].values())
    assert {
        name: record["sha256"]
        for name, record in cycle["input_artifacts"].items()
    } == q007n.REGISTERED_INPUT_SHA256
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert "not an optimal radius" in cycle["claim_boundary"]
    assert "finite-ball normal attraction" in cycle["claim_boundary"]
    json.dumps(q007n_artifact, allow_nan=False)
