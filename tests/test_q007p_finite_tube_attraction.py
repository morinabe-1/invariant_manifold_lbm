from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007p_finite_tube_attraction as q007p
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007p_artifact() -> dict:
    artifact_path = (
        Path(q007p.__file__).resolve().parent
        / "artifacts"
        / "q007p_finite_tube_attraction.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007p_accepts_the_registered_finite_tube(q007p_artifact) -> None:
    cycle = q007p_artifact["cycle"]
    majorant = cycle["finite_tube_majorant"]

    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered fixed-leaf tube is uniformly normally attracting "
        "in the external-coordinate norm"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert _fraction(majorant["base_modal_l1_radius"]) == Fraction(1, 10**19)
    assert _fraction(majorant["normal_coordinate_radius"]) == Fraction(
        1, 10**20
    )
    assert _fraction(majorant["analytic_chart_radius"]) == Fraction(1, 10**18)
    assert _fraction(majorant["base_image_modal_l1_upper"]) < Fraction(
        1, 10**19
    )
    assert _fraction(majorant["normal_fiber_contraction_upper"]) < Fraction(
        99, 100
    )
    assert _fraction(majorant["tangent_conorm_lower"]) > 0
    assert _fraction(majorant["normal_domination_ratio_upper"]) < Fraction(
        999, 1000
    )
    assert all(
        cycle["theorem_consequence"].values()
    )


def test_q007p_reconstructs_every_external_coordinate_block(
    q007p_artifact,
) -> None:
    coordinates = q007p_artifact["cycle"][
        "external_coordinate_certification"
    ]
    nonselected = coordinates["nonselected_representative_records"]
    selected = coordinates["selected_representative_records"]

    assert len(nonselected) == q007p.NONSELECTED_REPRESENTATIVE_COUNT == 70
    assert len(selected) == q007p.SELECTED_REPRESENTATIVE_COUNT == 2
    assert coordinates["represented_wave_count"] == q007p.TOTAL_WAVE_COUNT == 289
    assert coordinates["external_complex_dimension"] == 2574
    assert coordinates["represented_wave_count_formula"] == "70*4 + 2*4 + 1"
    assert coordinates["external_complex_dimension_formula"] == (
        "70*4*9 + 2*4*6 + 6"
    )
    assert coordinates["q007o_selected_certificates_reproduced_exactly"]
    assert all(
        record["q007h1_proof_digest_matches"]
        and record["coordinate_certificate_passed"]
        and record["selected_count"] == 0
        and record["excluded_count"] == 9
        and record["orbit_member_count"] == 4
        and _fraction(record["coordinate_defect_l1_upper"])
        < q007p.MAXIMUM_COORDINATE_DEFECT
        for record in nonselected
    )
    assert all(
        record["q007h1_proof_digest_matches"]
        and record["q007o_certificate_reproduced"]
        and record["coordinate_certificate_passed"]
        and record["coordinate_dimension"] == 6
        and record["orbit_member_count"] == 4
        for record in selected
    )


def test_q007p_global_constants_are_exact_blockwise_maxima(
    q007p_artifact,
) -> None:
    cycle = q007p_artifact["cycle"]
    coordinates = cycle["external_coordinate_certification"]
    bounds = cycle["global_conversion_and_linear_bounds"]
    nonselected = coordinates["nonselected_representative_records"]
    selected = coordinates["selected_representative_records"]
    zero = Fraction(1, 2)

    linear_values = [
        _fraction(record["linear_external_contraction_upper"])
        for record in (*nonselected, *selected)
    ] + [zero]
    synthesis_values = [
        _fraction(record["synthesis_l1_upper"])
        for record in nonselected
    ] + [
        _fraction(record["external_basis_l1_upper"]) for record in selected
    ] + [Fraction(1)]
    analysis_values = [
        _fraction(record["coordinate_inverse_l1_upper"])
        for record in nonselected
    ] + [
        _fraction(record["analysis_l1_upper"]) for record in selected
    ] + [Fraction(1)]
    selected_left_values = [
        _fraction(record["selected_analysis_l1_upper"])
        for record in selected
    ]

    assert _fraction(bounds["linear_external_contraction_upper"]) == max(
        linear_values
    )
    assert _fraction(bounds["synthesis_to_wiener_l1_upper"]) == max(
        synthesis_values
    )
    assert _fraction(bounds["analysis_from_wiener_l1_upper"]) == max(
        analysis_values
    )
    assert _fraction(bounds["selected_left_operator_l1_upper"]) == max(
        selected_left_values
    )
    assert _fraction(bounds["synthesis_to_wiener_l1_upper"]) <= Fraction(4)
    assert _fraction(bounds["analysis_from_wiener_l1_upper"]) <= Fraction(40)
    assert _fraction(bounds["selected_left_operator_l1_upper"]) <= Fraction(2)


def test_q007p_majorant_reconstructs_exactly_from_saved_fractions(
    q007p_artifact,
) -> None:
    cycle = q007p_artifact["cycle"]
    bounds = cycle["global_conversion_and_linear_bounds"]
    majorant = cycle["finite_tube_majorant"]
    coefficients = {
        name: _fraction(record)
        for name, record in majorant[
            "working_coefficients_reused_from_q007n"
        ].items()
    }
    r = _fraction(majorant["base_modal_l1_radius"])
    zeta = _fraction(majorant["normal_coordinate_radius"])
    rho = _fraction(majorant["analytic_chart_radius"])
    tau = _fraction(majorant["correction_pair_radius_tau"])
    selected_radius = _fraction(majorant["selected_spectral_radius_upper"])
    selected_minimum = _fraction(majorant["selected_minimum_modulus_lower"])
    q0 = _fraction(bounds["linear_external_contraction_upper"])
    synthesis = _fraction(bounds["synthesis_to_wiener_l1_upper"])
    analysis = _fraction(bounds["analysis_from_wiener_l1_upper"])
    selected_left = _fraction(bounds["selected_left_operator_l1_upper"])

    chart = coefficients["c_v"] * r + tau + sum(
        coefficients[f"h{degree}"] * r**degree for degree in (2, 3, 4)
    )
    reduced = selected_radius * r + tau / coefficients["c_v"] + sum(
        coefficients[f"g{degree}"] * r**degree for degree in (2, 3, 4)
    )
    state = chart + synthesis * zeta
    nonlinear_derivative = (
        q007p.NONLINEAR_MAJORANT_CONSTANT
        * state
        * (2 - state)
        / (1 - state) ** 2
    )
    base_image = reduced + selected_left * nonlinear_derivative * synthesis * zeta
    chart_derivative = tau / (rho - base_image) + sum(
        degree * coefficients[f"h{degree}"] * base_image ** (degree - 1)
        for degree in (2, 3, 4)
    )
    reduced_derivative = tau / (coefficients["c_v"] * (rho - r)) + sum(
        degree * coefficients[f"g{degree}"] * r ** (degree - 1)
        for degree in (2, 3, 4)
    )
    normal = q0 + analysis * synthesis * nonlinear_derivative * (
        1 + selected_left * chart_derivative
    )
    tangent = selected_minimum - reduced_derivative
    domination = normal / tangent

    assert _fraction(majorant["chart_radius_at_base_upper"]) == chart
    assert _fraction(majorant["reduced_radius_at_base_upper"]) == reduced
    assert _fraction(majorant["tube_state_wiener_l1_upper"]) == state
    assert _fraction(
        majorant["nonlinear_derivative_at_tube_state_upper"]
    ) == nonlinear_derivative
    assert _fraction(majorant["base_image_modal_l1_upper"]) == base_image
    assert _fraction(
        majorant["chart_derivative_at_base_image_upper"]
    ) == chart_derivative
    assert _fraction(
        majorant["reduced_derivative_at_base_upper"]
    ) == reduced_derivative
    assert _fraction(majorant["normal_fiber_contraction_upper"]) == normal
    assert _fraction(majorant["tangent_conorm_lower"]) == tangent
    assert _fraction(majorant["normal_domination_ratio_upper"]) == domination


def test_q007p_records_provenance_structure_and_claim_boundary(
    q007p_artifact,
) -> None:
    cycle = q007p_artifact["cycle"]
    runner_path = Path(q007p.__file__).resolve()

    assert q007p_artifact["schema_version"] == 1
    assert q007p_artifact["source"] == source_metadata()
    assert q007p_artifact["runner_source"] == {
        "filename": "q007p_finite_tube_attraction.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert all(record["passed"] for record in cycle["input_artifacts"].values())
    assert {
        name: record["sha256"]
        for name, record in cycle["input_artifacts"].items()
    } == q007p.REGISTERED_INPUT_SHA256
    assert cycle["structural_audit"]["zero_wave"]["passed"]
    assert cycle["structural_audit"]["external_linear_splitting"]["passed"]
    assert cycle["structural_audit"]["c4_norm_invariance"]["passed"]
    assert "not a Euclidean contraction result" in cycle["claim_boundary"]
    assert "Q007c1" in cycle["claim_boundary"]
    json.dumps(q007p_artifact, allow_nan=False)
