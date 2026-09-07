from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from research import d3q27 as d3
from research import q012a_d3q27_foundation as q012a
from ttim_lbm import d2q9 as d2
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def study() -> dict:
    return q012a.run_study()


def test_q012_prerequisites_preserve_rejections_and_map_scopes(study: dict) -> None:
    audit = study["cycle"]["prerequisites"]
    assert audit["passed"]
    assert len(audit["records"]) == 10
    assert all(audit["decisions"].values())
    assert "no historical trajectory rerun" in audit["evidence_mode"]
    assert audit["repaired_map_degrees_34_through_90_remain_open"]
    assert "MPFR" in audit["records"]["q007ap_forward_shadowing"]["mathematical_scope"]["claim"]


def test_scientific_failure_cannot_be_hidden_behind_study_validity() -> None:
    artifacts = {
        name: json.loads((q012a.ARTIFACT_DIRECTORY / (name + ".json")).read_text(encoding="utf-8"))
        for name in q012a.INPUT_SEALS
    }
    changed = copy.deepcopy(artifacts)
    changed["q006h_cluster_complete"]["cycle"]["selected_family"]["coefficient_gates"][
        "no_numerical_singularity"
    ]["passed"] = False
    assert changed["q006h_cluster_complete"]["study_gate"] == "passed"
    assert not q012a.prerequisite_decisions(changed)["repaired_sector_aware_family"]
    changed = copy.deepcopy(artifacts)
    changed["q005_nonresonance"]["cycle"]["hypothesis_outcome"] = "accepted"
    assert not q012a.prerequisite_decisions(changed)[
        "original_isotropic_candidate_rejection_preserved"
    ]


def test_q012a_quadrature_and_rank_six_negative_control(study: dict) -> None:
    audit = study["cycle"]["audits"]["quadrature"]
    assert audit["passed"] and audit["monomial_count"] == 216
    assert audit["rank_two_and_four_isotropy_exact"]
    assert audit["sixth_order_negative_control"]["mismatch_detected"]
    assert Fraction(audit["sixth_order_negative_control"]["axis_discrete"]) == Fraction(1, 3)
    assert Fraction(audit["sixth_order_negative_control"]["axis_gaussian"]) == Fraction(5, 9)
    assert Fraction(
        audit["sixth_order_negative_control"]["unit_face_diagonal_discrete"]
    ) == Fraction(1, 2)
    assert audit["sixth_order_negative_control"]["axis_and_face_differ"]
    assert not d3.VELOCITIES.flags.writeable and not d3.WEIGHTS.flags.writeable


def test_streaming_uses_xyz_velocity_on_zyx_spatial_axes(study: dict) -> None:
    audit = study["cycle"]["audits"]["moments_and_streaming"]
    assert audit["passed"]
    assert len(audit["impulse_passes"]) == 27 and all(audit["impulse_passes"])
    assert audit["streaming_population_multisets_unchanged"]
    assert max(audit["moment_errors"].values()) <= 5e-15


def test_fixed_conservation_leaf_and_finite_3d_rollouts(study: dict) -> None:
    audit = study["cycle"]["audits"]["conservation"]
    assert audit["passed"] and audit["trajectory_count"] == 16 and audit["step_count"] == 512
    assert {r["omega"] for r in audit["records"]} == set(q012a.OMEGAS)
    assert all(r["minimum_population"] > 0 for r in audit["records"])


@pytest.mark.parametrize("nz", [1, 3, 5])
def test_d2q9_lift_has_weighted_z_structure_and_exact_marginal(nz: int) -> None:
    state = d2.uniform_equilibrium(2, 4, (0.02, 0.01, -0.015))
    lifted = d3.lift_d2q9(state, nz)
    np.testing.assert_allclose(
        d3.d2q9_marginal(lifted), np.broadcast_to(state, (nz, 2, 4, 9)), rtol=0, atol=2e-16
    )
    lookup = {tuple(v): q for q, v in enumerate(d2.D2Q9_VELOCITIES)}
    for q, (cx, cy, cz) in enumerate(d3.VELOCITIES):
        expected = state[..., lookup[(cx, cy)]] * float(d3.D1Q3_WEIGHTS[cz + 1])
        np.testing.assert_allclose(
            lifted[..., q], np.broadcast_to(expected, (nz, 2, 4)), rtol=0, atol=0
        )
    rho, j = d3.macroscopic(lifted)
    np.testing.assert_allclose(d3.equilibrium(rho, j), lifted, rtol=0, atol=2e-16)


def test_d2q9_nonlinear_and_fourier_intertwining_reject_wrong_lift(study: dict) -> None:
    audit = study["cycle"]["audits"]["d2q9_lift"]
    assert audit["passed"] and audit["trajectory_count"] == 12
    assert len(audit["symbol_errors"]) == 12
    assert audit["wrong_z_weight_intertwining_error"] > 1e-4


def test_all_cubic_symmetries_are_distinct_and_full_map_equivariant(study: dict) -> None:
    symmetries = d3.cubic_symmetries()
    assert len({tuple(r.ravel()) for r in symmetries}) == 48
    audit = study["cycle"]["audits"]["cubic_symmetry"]
    assert audit["passed"] and audit["proper_rotation_count"] == 24
    assert all(r["closure_exact"] for r in audit["records"])
    rng = np.random.default_rng(991)
    state = rng.standard_normal((3, 3, 3, 27))
    for rotation in symmetries:
        rotated = d3.rotate_periodic_state(state, rotation)
        assert np.array_equal(d3.rotate_periodic_state(rotated, rotation.T), state)


def test_real_and_complex_derivative_actions_match_fourier_space(study: dict) -> None:
    audit = study["cycle"]["audits"]["linearization"]
    assert audit["passed"]
    for record in audit["records"]:
        assert record["fft_symbol_relative_error"] <= 2e-14
        assert all(3.5 <= ratio <= 4.5 for ratio in record["error_halving_ratios"])
    rng = np.random.default_rng(990)
    real, imag = rng.standard_normal((2, 3, 4, 27)), rng.standard_normal((2, 3, 4, 27))
    np.testing.assert_allclose(
        d3.linearized_periodic_step(real + 1j * imag, 1.2),
        d3.linearized_periodic_step(real, 1.2) + 1j * d3.linearized_periodic_step(imag, 1.2),
        atol=2e-14,
        rtol=0,
    )


def test_homological_solver_improves_3d_center_residual_order(study: dict) -> None:
    audit = study["cycle"]["audits"]["center_oracle"]
    assert audit["passed"] and audit["direction_count"] == 32
    assert audit["homological_diagnostics"]["augmented_rank"] == 31
    assert audit["coordinate_gauge_error"] < 1e-12
    assert audit["independent_fd_second_derivative_error"] < 5e-7
    for record in audit["records"]:
        assert abs(record["direction"][0]) >= 0.1
        assert 1.9 <= record["linear_slope"] <= 2.1
        assert 2.9 <= record["quadratic_slope"] <= 3.1


def test_study_claims_and_result_digest(study: dict) -> None:
    assert study["study_gate"] == "passed" and study["scientific_outcome"] == "accepted"
    cycle = copy.deepcopy(study["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert digest == q012a._digest(cycle)
    assert cycle["failed_audits"] == []
    assert all(cycle["validity_gates"].values())
    assert "no nonzero-mode manifold" in cycle["claim_boundary"]
    assert study["helper_source"]["sha256"] == _file_sha256(Path(d3.__file__))
    json.dumps(study, allow_nan=False)


def test_stored_artifact_replays_and_matches_both_sources(study: dict) -> None:
    path = q012a.ARTIFACT_DIRECTORY / "q012a_d3q27_foundation.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(q012a.__file__))
    assert artifact["helper_source"]["sha256"] == _file_sha256(Path(d3.__file__))
    assert artifact["cycle"] == study["cycle"]
    assert artifact["source"] == study["source"]


@pytest.mark.parametrize(
    "bad",
    [
        np.zeros((3, 3, 27)),
        np.zeros((0, 3, 3, 27)),
        np.zeros((3, 3, 3, 9)),
        np.full((1, 1, 1, 27), np.nan),
        np.zeros((1, 1, 1, 27), dtype=complex),
    ],
)
def test_invalid_nonlinear_states_are_rejected(bad: np.ndarray) -> None:
    with pytest.raises(ValueError):
        d3.bgk_periodic_step(bad, 1.2)


@pytest.mark.parametrize("omega", [0.0, 2.0, np.inf, np.nan])
def test_invalid_relaxation_is_rejected(omega: float) -> None:
    with pytest.raises(ValueError):
        d3.collision_symbol(omega)


def test_invalid_coordinates_grid_and_rotation_are_rejected() -> None:
    with pytest.raises(ValueError):
        d3.equilibrium(0.0, np.zeros(3))
    with pytest.raises(ValueError):
        d3.equilibrium(1.0, np.zeros(2))
    with pytest.raises(ValueError):
        d3.uniform_equilibrium((True, 3, 3), np.zeros(4))
    with pytest.raises(ValueError):
        d3.fourier_symbol((0.0, 0.0), 1.2)
    with pytest.raises(ValueError):
        d3.population_permutation(np.eye(3) * 2)
    with pytest.raises(ValueError):
        d3.rotate_periodic_state(np.zeros((3, 4, 5, 27)), np.eye(3))
