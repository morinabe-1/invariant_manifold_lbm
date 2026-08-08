from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.checkerboard_filter import filtered_bgk_periodic_step
from ttim_lbm.d2q9 import uniform_equilibrium
from ttim_lbm.normal_cocycle import (
    FilteredBGKJacobian,
    FixedLeafProjector,
    run_normal_cocycle_audit,
)


def test_arbitrary_state_filtered_bgk_jacobian_and_adjoint() -> None:
    state = uniform_equilibrium(3, 3, np.array([0.01, 0.002, -0.001]))
    rng = np.random.default_rng(20260904)
    perturbation = rng.normal(size=state.size)
    perturbation /= np.linalg.norm(perturbation)
    cotangent = rng.normal(size=state.size)
    cotangent /= np.linalg.norm(cotangent)
    jacobian = FilteredBGKJacobian.at_state(state, 1.5, 0.01)

    step = 1.0e-5
    finite_difference = (
        filtered_bgk_periodic_step(
            (state.ravel() + step * perturbation).reshape(state.shape),
            1.5,
            0.01,
        )
        - filtered_bgk_periodic_step(
            (state.ravel() - step * perturbation).reshape(state.shape),
            1.5,
            0.01,
        )
    ).ravel() / (2.0 * step)
    analytic = jacobian.matvec(perturbation)
    derivative_error = np.linalg.norm(finite_difference - analytic) / np.linalg.norm(
        analytic
    )
    forward_inner = np.vdot(analytic, cotangent)
    adjoint_inner = np.vdot(perturbation, jacobian.rmatvec(cotangent))

    assert derivative_error <= 2.0e-8
    assert abs(forward_inner - adjoint_inner) <= 5.0e-13
    matrix = np.column_stack((perturbation, cotangent))
    assert np.allclose(
        jacobian.matmat(matrix),
        np.column_stack(tuple(jacobian.matvec(matrix[:, index]) for index in range(2))),
        rtol=1.0e-14,
        atol=1.0e-14,
    )


def test_fixed_leaf_projector_is_symmetric_and_idempotent() -> None:
    leaf = FixedLeafProjector.for_square_grid(3)
    rng = np.random.default_rng(20260905)
    left = rng.normal(size=leaf.dimension)
    right = rng.normal(size=leaf.dimension)
    projected_left = leaf.project(left)
    projected_right = leaf.project(right)

    assert np.linalg.norm(leaf.conservation @ projected_left) <= 1.0e-12
    assert np.linalg.norm(leaf.project(projected_left) - projected_left) <= 1.0e-12
    assert abs(np.vdot(projected_left, right) - np.vdot(left, projected_right)) <= 1.0e-12


@pytest.fixture(scope="module")
def normal_cocycle():
    return run_normal_cocycle_audit()


def test_q007d_passes_every_registered_validity_gate(normal_cocycle) -> None:
    assert normal_cocycle["study_validity"] == "passed"
    assert all(gate["passed"] for gate in normal_cocycle["validity_gates"].values())
    assert normal_cocycle["direction_registration"]["duplicate_count"] == 0
    assert normal_cocycle["coefficient_reproduction"]["match"]


def test_q007d_validates_analytic_derivatives_projectors_and_solver(
    normal_cocycle,
) -> None:
    derivative = normal_cocycle["derivative_validation"]["summary"]
    campaign = normal_cocycle["cocycle_campaign"]["summary"]

    assert derivative["maximum_best_full_map_relative_error"] <= 2.0e-8
    assert derivative["maximum_best_chart_relative_error"] <= 2.0e-9
    assert derivative["maximum_adjoint_inner_product_relative_error"] <= 5.0e-13
    assert campaign["maximum_conservation_derivative_relative_residual"] <= 5.0e-13
    assert campaign["maximum_q_orthogonality_residual"] <= 1.0e-12
    assert campaign["maximum_projector_idempotency_relative_residual"] <= 1.0e-12
    assert campaign["maximum_normal_triplet_relative_residual"] <= 1.0e-8
    assert campaign["maximum_normal_singular_value_relative_disagreement"] <= 1.0e-6
    assert campaign["maximum_tangent_leakage"] <= 1.0e-3


def test_q007d_validly_rejects_euclidean_normal_dominance(normal_cocycle) -> None:
    campaign = normal_cocycle["cocycle_campaign"]

    assert normal_cocycle["hypothesis_outcome"] == "rejected"
    assert normal_cocycle["scientific_classification"] == (
        "registered finite-sample projected normal-cocycle dominance not observed"
    )
    assert not any(gate["passed"] for gate in normal_cocycle["hypothesis_gates"].values())
    assert campaign["equilibrium_control"]["gamma_10"] > 2.0
    assert all(
        record["summary"]["gamma_10_failure_count"] == 16
        for record in campaign["amplitude_records"]
    )
    assert not any(normal_cocycle["preserved_prior_outcomes"].values())
    assert "not a full-ball" in normal_cocycle["claim_boundary"]
    json.dumps(normal_cocycle, allow_nan=False)
