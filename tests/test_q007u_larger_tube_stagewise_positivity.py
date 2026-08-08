from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007u_larger_tube_stagewise_positivity as q007u
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007u_artifact() -> dict:
    artifact_path = (
        Path(q007u.__file__).resolve().parent
        / "artifacts"
        / "q007u_larger_tube_stagewise_positivity.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def q007r_artifact() -> dict:
    artifact_path = (
        Path(q007u.__file__).resolve().parent
        / "artifacts"
        / "q007r_stagewise_positivity.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007u_accepts_exact_stagewise_population_positivity(
    q007u_artifact,
) -> None:
    cycle = q007u_artifact["cycle"]

    assert cycle == q007u.run_larger_tube_stagewise_positivity_audit()
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered Q007s larger tube is population-positive at every exact "
        "BGK, streaming, and filter stage"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    )
    assert all(cycle["theorem_consequence"].values())


def test_q007u_reconstructs_the_exact_linear_operator_norms(
    q007u_artifact,
) -> None:
    audit = q007u_artifact["cycle"]["linear_operator_audit"]
    projector_columns = [
        _fraction(record)
        for record in audit["equilibrium_projector_column_l1_sums"]
    ]
    collision_columns = [
        _fraction(record) for record in audit["collision_column_l1_sums"]
    ]

    assert audit["moment_matrix_shape"] == [3, 9]
    assert audit["equilibrium_tangent_shape"] == [9, 3]
    assert projector_columns == [
        Fraction(1),
        *([Fraction(5, 3)] * 4),
        *([Fraction(13, 6)] * 4),
    ]
    assert collision_columns == [
        Fraction(1),
        *([Fraction(2)] * 4),
        *([Fraction(19, 6)] * 4),
    ]
    assert _fraction(audit["equilibrium_projector_l1_norm"]) == Fraction(
        13, 6
    )
    assert _fraction(audit["collision_l1_norm"]) == Fraction(19, 6)
    assert audit["collision_matches_rational_map"]
    assert audit["passed"]


def test_q007u_reconstructs_each_stage_bound_as_an_exact_fraction(
    q007u_artifact,
) -> None:
    cycle = q007u_artifact["cycle"]
    nonlinear = cycle["nonlinear_majorant_audit"]
    bounds = cycle["stage_bounds"]
    state_radius = _fraction(bounds["input_state_wiener_l1_upper"])
    equilibrium_nonlinear = Fraction(7) * state_radius**2 / (
        1 - state_radius
    )
    collision_nonlinear = Fraction(21, 2) * state_radius**2 / (
        1 - state_radius
    )
    equilibrium_deviation = Fraction(13, 6) * state_radius + (
        equilibrium_nonlinear
    )
    collision_deviation = Fraction(19, 6) * state_radius + (
        collision_nonlinear
    )

    assert _fraction(nonlinear["d2q9_weight_sum"]) == 1
    assert _fraction(
        nonlinear["weighted_absolute_velocity_quadratic"]
    ) == Fraction(8, 9)
    assert _fraction(
        nonlinear["equilibrium_nonlinear_majorant_constant"]
    ) == 7
    assert _fraction(
        nonlinear["collision_nonlinear_majorant_constant"]
    ) == Fraction(21, 2)
    assert _fraction(
        nonlinear["equilibrium_nonlinear_remainder_upper"]
    ) == equilibrium_nonlinear
    assert _fraction(
        nonlinear["collision_nonlinear_remainder_upper"]
    ) == collision_nonlinear
    assert _fraction(
        bounds["equilibrium_deviation_wiener_l1_upper"]
    ) == equilibrium_deviation
    assert _fraction(
        bounds["post_collision_deviation_wiener_l1_upper"]
    ) == collision_deviation
    assert _fraction(bounds["equilibrium_population_lower"]) == (
        Fraction(1, 36) - equilibrium_deviation
    )
    assert _fraction(bounds["post_collision_population_lower"]) == (
        Fraction(1, 36) - collision_deviation
    )
    assert _fraction(bounds["post_streaming_population_lower"]) == _fraction(
        bounds["post_collision_population_lower"]
    )
    assert _fraction(bounds["post_filter_population_lower"]) == _fraction(
        bounds["post_collision_population_lower"]
    )
    assert _fraction(bounds["post_filter_population_lower"]) > 0


def test_q007u_audits_streaming_permutations_and_the_convex_filter(
    q007u_artifact,
) -> None:
    audit = q007u_artifact["cycle"]["stage_structure_audit"]
    coefficients = [
        _fraction(record) for record in audit["filter_coefficients"]
    ]

    assert audit["streaming_population_permutation_count"] == 9
    assert audit["periodic_site_count"] == 17**2
    assert len(audit["streaming_records"]) == 9
    assert all(
        record["unique_periodic_target_count"] == 17**2
        and record["bijective"]
        and record["implementation_basis_replayed"]
        for record in audit["streaming_records"]
    )
    assert coefficients == [
        Fraction(99, 100),
        Fraction(1, 400),
        Fraction(1, 400),
        Fraction(1, 400),
        Fraction(1, 400),
    ]
    assert sum(coefficients) == 1
    assert audit["all_filter_coefficients_nonnegative"]
    assert audit["all_filter_implementation_basis_replays"]
    assert audit["wrapped_stage_composition_replayed"]
    assert audit["passed"]


def test_q007u_stage_bounds_cover_a_strictly_larger_tube(
    q007u_artifact,
    q007r_artifact,
) -> None:
    larger = q007u_artifact["cycle"]
    old = q007r_artifact["cycle"]
    larger_bounds = larger["stage_bounds"]
    old_bounds = old["stage_bounds"]

    assert _fraction(
        larger["q007s_tube_reuse"]["base_modal_l1_radius"]
    ) == Fraction(9, 10**19)
    assert _fraction(
        larger["q007s_tube_reuse"]["normal_coordinate_radius"]
    ) == Fraction(5, 10**12)
    assert _fraction(
        larger_bounds["input_state_wiener_l1_upper"]
    ) > _fraction(old_bounds["input_state_wiener_l1_upper"])
    assert _fraction(
        larger_bounds["equilibrium_deviation_wiener_l1_upper"]
    ) > _fraction(old_bounds["equilibrium_deviation_wiener_l1_upper"])
    assert _fraction(
        larger_bounds["post_collision_deviation_wiener_l1_upper"]
    ) > _fraction(old_bounds["post_collision_deviation_wiener_l1_upper"])
    assert _fraction(larger_bounds["post_filter_population_lower"]) > 0


def test_q007u_records_provenance_and_the_exact_arithmetic_boundary(
    q007u_artifact,
) -> None:
    cycle = q007u_artifact["cycle"]
    runner_path = Path(q007u.__file__).resolve()

    assert q007u_artifact["schema_version"] == 1
    assert q007u_artifact["source"] == source_metadata()
    assert q007u_artifact["runner_source"] == {
        "filename": "q007u_larger_tube_stagewise_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert cycle["input_artifact"]["sha256"] == (
        q007u.REGISTERED_Q007T_ARTIFACT_SHA256
    )
    assert cycle["input_artifact"]["observed_runner_sha256"] == (
        q007u.REGISTERED_Q007T_RUNNER_SHA256
    )
    assert cycle["input_artifact"]["validity_gate_count"] == 5
    assert cycle["input_artifact"]["hypothesis_gate_count"] == 3
    assert cycle["input_artifact"]["theorem_consequence_count"] == 3
    assert cycle["input_artifact"]["q007s_input_passed"]
    assert cycle["input_artifact"]["q007s_tube_reuse_passed"]
    assert cycle["input_artifact"]["passed"]
    assert cycle["q007s_tube_reuse"]["all_selected_candidate_gates_pass"]
    assert cycle["q007s_tube_reuse"]["q007s_forward_invariance"]
    assert cycle["q007s_tube_reuse"]["passed"]
    assert "exact mathematical" in cycle["claim_boundary"]
    assert "IEEE-754" in cycle["claim_boundary"]
    assert "continuous-optimum tube" in cycle["claim_boundary"]
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert not cycle["preserved_prior_outcomes"][
        "q007d_euclidean_rejection_changed"
    ]
    json.dumps(q007u_artifact, allow_nan=False)
