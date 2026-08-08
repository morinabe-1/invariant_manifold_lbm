from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.adapted_finite_cocycle import (
    AdaptedMapJacobian,
    run_adapted_finite_cocycle_audit,
)
from ttim_lbm.adapted_metric import build_adapted_fourier_metric
from ttim_lbm.d2q9 import uniform_equilibrium
from ttim_lbm.normal_cocycle import FilteredBGKJacobian


@pytest.fixture(scope="module")
def adapted_equilibrium_jacobian():
    metric = build_adapted_fourier_metric()[0]
    state = uniform_equilibrium(17, 17, np.array([1.0, 0.0, 0.0]))
    physical = FilteredBGKJacobian.at_state(state, 1.5, 0.01)
    return AdaptedMapJacobian(metric, physical)


@pytest.fixture(scope="module")
def adapted_finite_cocycle():
    return run_adapted_finite_cocycle_audit()


def test_adapted_map_jacobian_has_the_registered_complex_adjoint(
    adapted_equilibrium_jacobian,
) -> None:
    jacobian = adapted_equilibrium_jacobian
    rng = np.random.default_rng(20260909)
    left = rng.normal(size=(jacobian.dimension, 3)) + 1j * rng.normal(
        size=(jacobian.dimension, 3)
    )
    right = rng.normal(size=(jacobian.dimension, 3)) + 1j * rng.normal(
        size=(jacobian.dimension, 3)
    )

    forward_inner = np.vdot(jacobian.matmat(left), right)
    adjoint_inner = np.vdot(left, jacobian.rmatmat(right))

    assert abs(forward_inner - adjoint_inner) <= 2.0e-12 * max(
        abs(forward_inner),
        abs(adjoint_inner),
        1.0,
    )


def test_q007f_passes_every_registered_validity_gate(
    adapted_finite_cocycle,
) -> None:
    assert adapted_finite_cocycle["study_validity"] == "passed"
    assert len(adapted_finite_cocycle["validity_gates"]) == 7
    assert all(
        gate["passed"]
        for gate in adapted_finite_cocycle["validity_gates"].values()
    )
    assert adapted_finite_cocycle["coefficient_reproduction"]["match"]
    assert adapted_finite_cocycle["direction_registration"][
        "direction_sha256"
    ] == "99861e73b9204938e254cbfc1c01a81de7be0bd6fed726ab131b26708c741424"


def test_q007f_validates_the_fixed_transform_derivative_and_solver(
    adapted_finite_cocycle,
) -> None:
    derivative = adapted_finite_cocycle["derivative_validation"]
    campaign = adapted_finite_cocycle["adapted_cocycle_campaign"]
    summary = campaign["summary"]

    assert derivative["summary"]["maximum_best_map_relative_error"] <= 2.0e-8
    assert derivative["summary"][
        "maximum_adjoint_inner_product_relative_error"
    ] <= 5.0e-12
    assert summary["maximum_equilibrium_blockwise_relative_error"] <= 1.0e-8
    assert summary["maximum_normal_triplet_relative_residual"] <= 1.0e-8
    assert summary[
        "maximum_normal_singular_value_relative_disagreement"
    ] <= 1.0e-6
    assert summary["maximum_tangent_leakage"] <= 1.0e-3
    assert campaign["starting_point_count"] == 33


def test_q007f_accepts_only_the_registered_ten_step_finite_sample(
    adapted_finite_cocycle,
) -> None:
    campaign = adapted_finite_cocycle["adapted_cocycle_campaign"]

    assert adapted_finite_cocycle["hypothesis_outcome"] == "accepted"
    assert adapted_finite_cocycle["scientific_classification"] == (
        "registered finite-sample adapted-metric projected normal-cocycle "
        "dominance observed"
    )
    assert all(
        record["summary"]["maximum_gamma_10"] < 1.0
        and record["summary"]["gamma_10_failure_count"] == 0
        for record in campaign["amplitude_records"]
    )
    assert campaign["equilibrium_control"]["gamma_10"] < 1.0
    assert not any(adapted_finite_cocycle["preserved_prior_outcomes"].values())
    assert "not an independent holdout" in adapted_finite_cocycle[
        "claim_boundary"
    ]
    json.dumps(adapted_finite_cocycle, allow_nan=False)
