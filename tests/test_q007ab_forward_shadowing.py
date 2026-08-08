from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ab_forward_shadowing as q007ab


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ab_cycle() -> dict:
    return q007ab.run_forward_shadowing_audit()


@pytest.fixture(scope="module")
def q007ab_artifact() -> dict:
    artifact_path = (
        Path(q007ab.__file__).resolve().parent
        / "artifacts"
        / "q007ab_forward_shadowing.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007ab_fixed_coordinate_lipschitz_formula_is_exact(
    q007ab_cycle: dict,
) -> None:
    audit = q007ab_cycle["coordinate_lipschitz_audit"]
    selected_linear = _fraction(
        audit["selected_linear_contraction_upper"]
    )
    external_linear = _fraction(
        audit["external_linear_contraction_upper"]
    )
    selected_synthesis = _fraction(audit["selected_synthesis_upper"])
    external_synthesis = _fraction(audit["external_synthesis_upper"])
    selected_analysis = _fraction(
        audit["selected_nonlinear_analysis_upper"]
    )
    external_analysis = _fraction(
        audit["external_nonlinear_analysis_upper"]
    )
    derivative = _fraction(
        audit["nonlinear_derivative_at_tube_state_upper"]
    )
    nonlinear = _fraction(
        audit["nonlinear_coordinate_lipschitz_increment_upper"]
    )
    lipschitz = _fraction(
        audit["fixed_coordinate_full_map_lipschitz_upper"]
    )

    assert nonlinear == (
        selected_analysis + external_analysis
    ) * derivative * max(selected_synthesis, external_synthesis)
    assert lipschitz == max(selected_linear, external_linear) + nonlinear
    assert lipschitz < 1
    assert audit["coordinate_is_fixed_linear_not_graph_relative"]
    assert audit["exact_arithmetic_identities_passed"]


def test_q007ab_geometric_recurrence_interval_is_invariant(
    q007ab_cycle: dict,
) -> None:
    shadow = q007ab_cycle["shadow_recurrence_audit"]
    initial = _fraction(shadow["initial_coordinate_error_upper"])
    step = _fraction(shadow["step_coordinate_defect_upper"])
    lipschitz = _fraction(shadow["fixed_coordinate_lipschitz_upper"])
    stationary = _fraction(shadow["stationary_coordinate_error_upper"])
    uniform = _fraction(
        shadow["uniform_all_iterate_coordinate_error_upper"]
    )

    assert (1 - lipschitz) * stationary == step
    assert lipschitz * stationary + step == stationary
    assert uniform == max(initial, stationary)
    assert initial <= uniform
    assert lipschitz * uniform + step <= uniform
    assert shadow["fixed_point_identity_passed"]
    assert shadow["recurrence_interval_invariant"]


def test_q007ab_uniform_physical_bound_meets_preregistered_gate(
    q007ab_cycle: dict,
) -> None:
    coordinate = q007ab_cycle["coordinate_lipschitz_audit"]
    shadow = q007ab_cycle["shadow_recurrence_audit"]

    assert coordinate["fixed_coordinate_full_map_lipschitz_upper"][
        "float"
    ] == pytest.approx(0.9920954948836456)
    assert shadow["initial_coordinate_error_upper"]["float"] == pytest.approx(
        6.073403211214871e-22
    )
    assert shadow["step_coordinate_defect_upper"]["float"] == pytest.approx(
        2.3344049524038155e-20
    )
    assert shadow["uniform_all_iterate_coordinate_error_upper"][
        "float"
    ] == pytest.approx(2.9532588290365307e-18)
    assert shadow["uniform_all_iterate_physical_wiener_error_upper"][
        "float"
    ] == pytest.approx(8.529800645544777e-18)
    ratio = _fraction(
        shadow["uniform_physical_to_tube_state_radius_ratio"]
    )
    assert ratio < q007ab.RELATIVE_TUBE_ACCURACY_THRESHOLD
    assert shadow["registered_accuracy_threshold_passed"]


def test_q007ab_certifies_same_initial_all_iterate_forward_shadowing(
    q007ab_cycle: dict,
) -> None:
    assert q007ab_cycle["study_validity"] == "passed"
    assert q007ab_cycle["hypothesis_outcome"] == "accepted"
    assert q007ab_cycle["scientific_classification"] == (
        "fixed-coordinate contraction certifies all-iterate MPFR-85 "
        "forward shadowing"
    )
    assert len(q007ab_cycle["validity_gates"]) == 6
    assert all(
        gate["passed"] for gate in q007ab_cycle["validity_gates"].values()
    )
    assert len(q007ab_cycle["hypothesis_gates"]) == 6
    assert all(
        gate["passed"] for gate in q007ab_cycle["hypothesis_gates"].values()
    )
    assert all(q007ab_cycle["theorem_consequence"].values())
    assert q007ab_cycle["input_audit"]["artifacts"]["q007aa"][
        "fresh_cycle_matches"
    ]
    assert "not a bi-infinite shadowing lemma" in q007ab_cycle[
        "claim_boundary"
    ]


def test_q007ab_artifact_seals_the_accepted_forward_shadowing_result(
    q007ab_cycle: dict,
    q007ab_artifact: dict,
) -> None:
    assert q007ab_artifact["cycle"] == q007ab_cycle
    assert q007ab_artifact["study_gate"] == "passed"
    assert q007ab_artifact["scientific_outcome"] == "accepted"
    assert q007ab_artifact["runner_source"]["sha256"] == (
        "4958e1aa5140bdbd1a32ce074c77ce2739636a34f7da2531c792ec165401c01a"
    )
    assert q007ab_cycle["input_digest_sha256"] == (
        "83c98750b8a18aa98cae710fad0a4d2fa139428d791a085bdd086e39e435225f"
    )
    assert q007ab_cycle["result_digest_sha256"] == (
        "268a5e2098011561c3bc521c845e6eb804692713502fbbd54c3b3106b8f9c014"
    )
