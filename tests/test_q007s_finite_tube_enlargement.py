from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007s_finite_tube_enlargement as q007s
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007s_artifact() -> dict:
    artifact_path = (
        Path(q007s.__file__).resolve().parent
        / "artifacts"
        / "q007s_finite_tube_enlargement.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def q007p_artifact() -> dict:
    artifact_path = (
        Path(q007s.__file__).resolve().parent
        / "artifacts"
        / q007s.Q007P_ARTIFACT
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def fresh_cycle() -> dict:
    return q007s.run_finite_tube_enlargement_audit()


def test_q007s_accepts_the_registered_larger_tube(
    q007s_artifact,
    fresh_cycle,
) -> None:
    cycle = q007s_artifact["cycle"]

    assert cycle == fresh_cycle
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered exact-manifold tube enlarged on the fixed rational "
        "candidate grid"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    )
    assert all(cycle["theorem_consequence"].values())


def test_q007s_evaluates_the_complete_preregistered_grid(
    q007s_artifact,
    fresh_cycle,
) -> None:
    base_radii, normal_radii = q007s._registered_grids()
    audit = q007s_artifact["cycle"]["candidate_grid_audit"]
    slices = audit["base_slice_boundaries"]

    assert base_radii == [Fraction(mantissa, 10**19) for mantissa in range(1, 10)]
    assert normal_radii == sorted(
        Fraction(mantissa, 10**exponent)
        for exponent in range(10, 21)
        for mantissa in range(1, 10)
    )
    assert len(set(base_radii)) == audit["base_radius_count"] == 9
    assert len(set(normal_radii)) == audit["normal_radius_count"] == 99
    assert audit["candidate_count"] == 891
    assert len(audit["candidate_summaries"]) == 891
    assert len(slices) == 9
    assert sum(record["candidate_count"] for record in slices) == 891
    assert sum(record["passing_count"] for record in slices) == 676
    expected_digest = (
        "91fcc70355acfc4b7163c951227188960ef275408b06a678d45d5e4ec4c85300"
    )
    assert audit["canonical_candidate_digest_sha256"] == expected_digest
    assert (
        fresh_cycle["candidate_grid_audit"][
            "canonical_candidate_digest_sha256"
        ]
        == expected_digest
    )
    assert audit["decision_arithmetic"] == "exact fractions.Fraction signs only"
    assert audit["unique_cartesian_product"]


def test_q007s_reproduces_every_q007p_control_quantity_exactly(
    q007s_artifact,
    q007p_artifact,
) -> None:
    reproduction = q007s_artifact["cycle"]["control_reproduction"]
    control = reproduction["control_candidate"]
    majorant = q007p_artifact["cycle"]["finite_tube_majorant"]
    field_map = {
        "base_radius": "base_modal_l1_radius",
        "normal_radius": "normal_coordinate_radius",
        "chart_radius": "chart_radius_at_base_upper",
        "reduced_radius": "reduced_radius_at_base_upper",
        "state_radius": "tube_state_wiener_l1_upper",
        "nonlinear_derivative": "nonlinear_derivative_at_tube_state_upper",
        "base_image": "base_image_modal_l1_upper",
        "chart_derivative": "chart_derivative_at_base_image_upper",
        "reduced_derivative": "reduced_derivative_at_base_upper",
        "normal_contraction": "normal_fiber_contraction_upper",
        "tangent_conorm": "tangent_conorm_lower",
        "domination_ratio": "normal_domination_ratio_upper",
    }
    margin_map = {
        "population_wiener": "density",
        "analytic_base": "analytic_base",
        "base_forward_invariance": "base_forward_invariance",
        "normal_contraction_to_cap": "normal_contraction_to_registered_cap",
        "normal_tube_forward_invariance": "normal_tube_forward_invariance",
        "tangent_invertibility": "tangent_invertibility",
        "domination_to_cap": "domination_to_registered_cap",
        "domination_to_one": "domination_to_one",
    }

    assert all(reproduction["field_matches"].values())
    assert all(reproduction["margin_matches"].values())
    for candidate_name, q007p_name in field_map.items():
        assert _fraction(control[candidate_name]) == _fraction(
            majorant[q007p_name]
        )
    for candidate_name, q007p_name in margin_map.items():
        assert _fraction(control["strict_margins"][candidate_name]) == _fraction(
            majorant["strict_margins"][q007p_name]
        )
    assert control["passed"]
    assert reproduction["passed"]


def test_q007s_selected_majorant_reconstructs_as_exact_fractions(
    q007s_artifact,
) -> None:
    cycle = q007s_artifact["cycle"]
    selected = cycle["selection"]["selected_candidate"]
    constants = {
        name: _fraction(record)
        for name, record in cycle["constant_reuse_audit"]["constants"].items()
    }
    r = _fraction(selected["base_radius"])
    zeta = _fraction(selected["normal_radius"])
    chart = constants["c_v"] * r + constants["tau"] + sum(
        constants[f"h{degree}"] * r**degree for degree in (2, 3, 4)
    )
    reduced = constants["selected_radius"] * r + constants["tau"] / constants[
        "c_v"
    ] + sum(constants[f"g{degree}"] * r**degree for degree in (2, 3, 4))
    state = chart + constants["synthesis"] * zeta
    nonlinear = constants["nonlinear_constant"] * state * (2 - state) / (
        1 - state
    ) ** 2
    base_image = (
        reduced
        + constants["selected_analysis"]
        * nonlinear
        * constants["synthesis"]
        * zeta
    )
    chart_derivative = constants["tau"] / (constants["rho"] - base_image) + sum(
        degree * constants[f"h{degree}"] * base_image ** (degree - 1)
        for degree in (2, 3, 4)
    )
    reduced_derivative = constants["tau"] / (
        constants["c_v"] * (constants["rho"] - r)
    ) + sum(
        degree * constants[f"g{degree}"] * r ** (degree - 1)
        for degree in (2, 3, 4)
    )
    normal = constants["q0"] + constants["analysis"] * constants[
        "synthesis"
    ] * nonlinear * (
        1 + constants["selected_analysis"] * chart_derivative
    )
    tangent = constants["selected_minimum"] - reduced_derivative
    domination = normal / tangent

    assert r == Fraction(9, 10**19)
    assert zeta == Fraction(5, 10**12)
    assert _fraction(selected["chart_radius"]) == chart
    assert _fraction(selected["reduced_radius"]) == reduced
    assert _fraction(selected["state_radius"]) == state
    assert _fraction(selected["nonlinear_derivative"]) == nonlinear
    assert _fraction(selected["base_image"]) == base_image
    assert _fraction(selected["chart_derivative"]) == chart_derivative
    assert _fraction(selected["reduced_derivative"]) == reduced_derivative
    assert _fraction(selected["normal_contraction"]) == normal
    assert _fraction(selected["tangent_conorm"]) == tangent
    assert _fraction(selected["domination_ratio"]) == domination
    assert base_image < r
    assert normal < Fraction(99, 100)
    assert tangent > 0
    assert domination < Fraction(999, 1000)
    assert selected["passed"] and all(selected["gates"].values())


def test_q007s_selection_boundary_is_lexicographic_and_strict(
    q007s_artifact,
) -> None:
    cycle = q007s_artifact["cycle"]
    selection = cycle["selection"]
    selected = selection["selected_candidate"]
    selected_slice = cycle["candidate_grid_audit"]["base_slice_boundaries"][-1]
    first_larger = selected_slice["first_larger_registered_candidate"]

    assert _fraction(selected["base_radius"]) == Fraction(9, 10**19)
    assert _fraction(selected["normal_radius"]) == Fraction(5, 10**12)
    assert _fraction(selection["base_radius_improvement_factor"]) == 9
    assert _fraction(selection["normal_radius_improvement_factor"]) == 500_000_000
    assert selected_slice["passing_count"] == 77
    assert _fraction(selected_slice["largest_passing_normal_radius"]) == Fraction(
        5, 10**12
    )
    assert _fraction(first_larger["normal_radius"]) == Fraction(6, 10**12)
    assert first_larger["failed_gate_names"] == ["base_forward_invariance"]
    assert not first_larger["passed"]
    assert selected_slice["all_larger_registered_normal_candidates_fail"]
    assert selection["all_larger_normals_on_selected_slice_fail_or_absent"]
    assert selection["all_larger_base_slices_fail_or_absent"]
    assert selection["selection_boundary_reproduced"]


def test_q007s_records_provenance_scope_and_claim_boundary(
    q007s_artifact,
) -> None:
    cycle = q007s_artifact["cycle"]
    runner_path = Path(q007s.__file__).resolve()

    assert q007s_artifact["schema_version"] == 1
    assert q007s_artifact["source"] == source_metadata()
    assert q007s_artifact["runner_source"] == {
        "filename": "q007s_finite_tube_enlargement.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert cycle["input_artifact"]["sha256"] == (
        q007s.REGISTERED_Q007P_ARTIFACT_SHA256
    )
    assert cycle["input_artifact"]["observed_runner_sha256"] == (
        q007s.REGISTERED_Q007P_RUNNER_SHA256
    )
    assert cycle["input_artifact"]["passed"]
    assert q007s_artifact["mathematical_scope"]["construction_grid"] == [17, 17]
    assert q007s_artifact["mathematical_scope"]["conservation_treatment"] == (
        "fixed global mass and momentum leaf"
    )
    assert "not a continuous optimum" in cycle["claim_boundary"]
    assert "Q007q/Q007r positivity remains sealed to the old tube" in cycle[
        "claim_boundary"
    ]
    assert not any(cycle["preserved_prior_outcomes"].values())
    json.dumps(q007s_artifact, allow_nan=False)
