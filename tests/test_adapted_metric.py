from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.adapted_metric import (
    build_adapted_fourier_metric,
    run_adapted_metric_audit,
)


@pytest.fixture(scope="module")
def adapted_fourier_metric():
    return build_adapted_fourier_metric()[0]


@pytest.fixture(scope="module")
def adapted_metric_audit():
    return run_adapted_metric_audit()


def test_adapted_transform_supports_columns_and_exact_adjoint_pairs(
    adapted_fourier_metric,
) -> None:
    metric = adapted_fourier_metric
    rng = np.random.default_rng(20260909)
    adapted_left = rng.normal(size=(metric.dimension, 3)) + 1j * rng.normal(
        size=(metric.dimension, 3)
    )
    adapted_right = rng.normal(size=(metric.dimension, 3)) + 1j * rng.normal(
        size=(metric.dimension, 3)
    )
    physical_left = metric.inverse(adapted_left)
    physical_right = metric.inverse(adapted_right)

    assert np.allclose(
        metric.forward(physical_left),
        adapted_left,
        rtol=2.0e-13,
        atol=2.0e-13,
    )
    assert np.allclose(
        np.vdot(metric.forward(physical_left), adapted_right),
        np.vdot(physical_left, metric.forward_adjoint(adapted_right)),
        rtol=2.0e-13,
        atol=2.0e-13,
    )
    assert np.allclose(
        np.vdot(metric.inverse(adapted_left), physical_right),
        np.vdot(adapted_left, metric.inverse_adjoint(physical_right)),
        rtol=2.0e-13,
        atol=2.0e-13,
    )


def test_q007e_passes_every_registered_validity_gate(adapted_metric_audit) -> None:
    assert adapted_metric_audit["study_validity"] == "passed"
    assert all(
        gate["passed"]
        for gate in adapted_metric_audit["validity_gates"].values()
    )
    assert adapted_metric_audit["q007d_reproduction"][
        "maximum_relative_error"
    ] <= 1.0e-10


def test_q007e_constructs_the_registered_fixed_leaf_metric(
    adapted_metric_audit,
) -> None:
    construction = adapted_metric_audit["metric_construction"]
    spectral = construction["spectral_gap"]
    summary = construction["summary"]

    assert summary["wave_block_count"] == 289
    assert summary["fixed_leaf_dimension"] == 2598
    assert summary["selected_complex_dimension"] == 24
    assert summary["selected_wave_count"] == 8
    assert len(summary["metric_sha256"]) == 64
    assert len(summary["whitening_sha256"]) == 64
    assert not summary["missing_selected_waves"]
    assert not summary["unexpected_selected_waves"]
    assert (
        spectral["maximum_excluded_modulus"]
        < spectral["registered_rate"]
        < spectral["minimum_selected_modulus"]
    )
    assert summary["maximum_stein_relative_residual"] <= 1.0e-10
    assert summary["minimum_stein_eigenvalue"] > 1.0e-12
    assert summary["global_metric_condition_number"] <= 1.0e10


def test_q007e_validates_real_transform_and_matrix_free_svd(
    adapted_metric_audit,
) -> None:
    conjugacy = adapted_metric_audit["conjugacy_audit"]
    roundtrip = adapted_metric_audit["transform_roundtrip_audit"]["summary"]
    svd = adapted_metric_audit["adapted_svd_audit"]

    assert conjugacy["maximum_metric_conjugacy_relative_residual"] <= 1.0e-10
    assert roundtrip["maximum_roundtrip_relative_error"] <= 1.0e-10
    assert roundtrip["maximum_imaginary_leakage_relative_norm"] <= 1.0e-10
    assert svd["summary"][
        "maximum_matrix_free_vs_blockwise_normal_relative_error"
    ] <= 1.0e-8
    assert svd["summary"]["maximum_triplet_relative_residual"] <= 1.0e-8
    assert svd["summary"][
        "maximum_two_start_singular_value_relative_disagreement"
    ] <= 1.0e-6


def test_q007e_prequalifies_only_the_equilibrium_adapted_metric(
    adapted_metric_audit,
) -> None:
    horizons = {
        record["horizon"]: record
        for record in adapted_metric_audit["adapted_svd_audit"][
            "horizon_records"
        ]
    }

    assert adapted_metric_audit["hypothesis_outcome"] == "accepted"
    assert adapted_metric_audit["scientific_classification"] == (
        "equilibrium Riesz/Stein metric prequalified for finite-radius testing"
    )
    assert horizons[1]["gamma"] < 1.0
    assert horizons[10]["gamma"] < 1.0
    assert not any(adapted_metric_audit["preserved_prior_outcomes"].values())
    assert "not finite-radius normal attraction" in adapted_metric_audit[
        "claim_boundary"
    ]
    json.dumps(adapted_metric_audit, allow_nan=False)
