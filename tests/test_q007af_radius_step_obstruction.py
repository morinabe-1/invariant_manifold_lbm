from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007af_radius_step_obstruction as q007af
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007af_cycle() -> dict:
    return q007af.run_radius_step_obstruction_audit()


def test_q007af_reproduces_all_sealed_inputs_and_q007ae_boundary(
    q007af_cycle: dict,
) -> None:
    inputs = q007af_cycle["input_artifacts"]
    implementations = q007af_cycle["implementation_source_audit"]
    reproduction = q007af_cycle["majorant_reproduction_audit"]

    assert set(inputs) == {"q007n", "q007ad", "q007ae"}
    assert all(record["passed"] for record in inputs.values())
    assert implementations[
        "all_registered_implementation_sha256_match"
    ]
    assert reproduction["working_coefficient_count"] == 13
    assert reproduction["all_working_coefficients_positive"]
    assert reproduction["inverse_ordering_reproduced"]
    assert reproduction["q007ae_candidate_count"] == 119
    assert reproduction[
        "q007ae_candidate_records_reproduced_exactly"
    ]
    assert reproduction["q007ae_radius_boundary_reproduced"]


def test_q007af_brackets_the_1e_minus_15_inverse_threshold_exactly(
    q007af_cycle: dict,
) -> None:
    threshold = q007af_cycle["integer_inverse_threshold_audit"]
    passing = threshold["passing_endpoint"]["candidate_record"]
    failing = threshold["failing_endpoint"]["candidate_record"]

    assert threshold["complete"]
    assert threshold["registered_bracket_reproduced"]
    assert threshold["bisection_iteration_count"] == 44
    assert threshold["maximum_passing_integer_inverse"] == (
        q007af.REGISTERED_PASSING_INVERSE
    )
    assert threshold["minimum_failing_integer_inverse"] == (
        q007af.REGISTERED_FAILING_INVERSE
    )
    assert threshold["final_integer_width"] == 1
    assert passing["modal_radius_decimal"] == "1e-15"
    assert passing["passed"]
    assert failing["modal_radius_decimal"] == "1e-15"
    assert not failing["passed"]


def test_q007af_proves_the_larger_inverse_half_line_fails(
    q007af_cycle: dict,
) -> None:
    monotonicity = q007af_cycle["monotonicity_audit"]

    assert monotonicity["passed"]
    assert monotonicity["structural_signs_passed"]
    assert monotonicity["endpoint_domains_positive"]
    assert all(monotonicity["endpoint_derivative_formula_matches"])
    assert all(monotonicity["endpoint_radii_identity_matches"])
    assert monotonicity["contraction_crosses_one_half"]
    assert _fraction(
        monotonicity["passing_contraction_bound"]
    ) < Fraction(1, 2)
    assert _fraction(
        monotonicity["failing_contraction_bound"]
    ) > Fraction(1, 2)
    assert _fraction(monotonicity["passing_radii_margin"]) > 0
    assert _fraction(monotonicity["failing_radii_margin"]) < 0
    assert monotonicity[
        "all_inverse_at_or_above_failing_endpoint_fail"
    ]


def test_q007af_derives_the_strictly_necessary_external_gap(
    q007af_cycle: dict,
) -> None:
    gap = q007af_cycle["required_external_gap_audit"]
    beta = _fraction(gap["q007n_working_beta_maximum"])
    required = _fraction(gap["necessary_external_gap_lower"])

    assert required == (
        81 * beta / q007af.REGISTERED_FAILING_INVERSE
    )
    assert _fraction(gap["raw_inverse_at_necessary_gap"]) == (
        q007af.REGISTERED_FAILING_INVERSE
    )
    assert _fraction(gap["working_inverse_at_necessary_gap"]) == (
        q007af.REGISTERED_FAILING_INVERSE
    )
    assert gap["integer_endpoint_is_fixed_by_decimal_rounding"]
    assert gap["necessary_external_gap_lower"]["float"] == pytest.approx(
        2.546402442702229e-8
    )


def test_q007af_sealed_witness_obstructs_the_required_gap(
    q007af_cycle: dict,
) -> None:
    witness = q007af_cycle["witness_obstruction_audit"]
    required = _fraction(witness["required_gap_lower"])
    allowable = _fraction(witness["allowable_gap_upper"])
    ratio = _fraction(witness["witness_to_required_gap_ratio"])
    inverse_ratio = _fraction(
        witness["optimistic_inverse_to_failing_endpoint_ratio"]
    )

    assert witness["witness_identity_matches"]
    assert witness["counts_sum_to_degree"]
    assert witness["center_distance_squared_reproduced"]
    assert witness["stored_allowable_gap_lower_reproduced"]
    assert _fraction(witness["sqrt_enclosure_width"]) == Fraction(
        1, 10**100
    )
    assert allowable < required
    assert ratio < q007af.MAXIMUM_WITNESS_TO_REQUIRED_RATIO
    assert _fraction(witness["absolute_gap_shortfall"]) > (
        q007af.MINIMUM_GAP_SHORTFALL
    )
    assert witness["required_gap_fails_even_without_threshold_rounding"]
    assert _fraction(witness["exact_required_gap_squared_margin"]) < 0
    assert inverse_ratio > q007af.MINIMUM_OPTIMISTIC_INVERSE_RATIO
    assert witness["single_witness_obstructs_required_uniform_gap"]
    assert not witness["full_phase_reenumeration_needed"]


def test_q007af_accepts_only_the_certificate_family_obstruction(
    q007af_cycle: dict,
) -> None:
    assert q007af_cycle["study_validity"] == "passed"
    assert q007af_cycle["hypothesis_outcome"] == "accepted"
    assert q007af_cycle["scientific_classification"] == (
        "sealed external phase-disc family cannot certify the "
        "1e-15 radius step"
    )
    assert len(q007af_cycle["validity_gates"]) == 6
    assert all(
        gate["passed"]
        for gate in q007af_cycle["validity_gates"].values()
    )
    assert len(q007af_cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"]
        for gate in q007af_cycle["hypothesis_gates"].values()
    )
    consequence = q007af_cycle["theorem_consequence"]
    assert consequence[
        "sealed_q007ad_disc_family_obstructs_1e_minus_15"
    ]
    assert consequence["q007ae_explicit_radius_1e_minus_16_preserved"]
    assert not consequence["true_analytic_radius_upper_bound_proved"]
    assert not consequence[
        "alternative_norm_or_spectral_certificate_excluded"
    ]
    assert not consequence[
        "q007p_through_q007ab_tube_constants_enlarged"
    ]


def test_q007af_artifact_reproduces_the_accepted_obstruction(
    q007af_cycle: dict,
) -> None:
    runner_path = Path(q007af.__file__).resolve()
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q007af_radius_step_obstruction.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "a686526552c33f5f1f01a9f1d9c49036d1c9491a2092b07ac8c8621a33d4ada1"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007af_radius_step_obstruction.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert artifact["cycle"] == q007af_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert q007af_cycle["input_digest_sha256"] == (
        "6cfeabe16a18fdb6de08e67c575a0b0db2f3ab1341c35c434faff100fd959255"
    )
    assert q007af_cycle["result_digest_sha256"] == (
        "3d210cf25513e373ac6a2e7a276163998a602c529878f3c95f085c9e0625bfdd"
    )
    assert q007af_cycle["integer_inverse_threshold_audit"][
        "bisection_decision_digest_sha256"
    ] == "24b0e993f676082579158cfeddfe74009161d72412bf228f715baa396246c31b"
