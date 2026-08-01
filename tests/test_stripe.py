from __future__ import annotations

import numpy as np
import pytest

from ttim_lbm.d2q9 import bgk_periodic_step, global_conserved_quantities
from ttim_lbm.stripe import build_stripe_quadratic_model


def test_stripe_model_solves_the_registered_fixed_leaf_homological_problem() -> None:
    model = build_stripe_quadratic_model()
    diagnostics = model.diagnostics

    assert model.chart.base.shape == (153,)
    assert model.chart.tangent.shape == (153, 6)
    assert model.chart.hessian.shape == (153, 6, 6)
    np.testing.assert_allclose(model.extractor @ model.chart.tangent, np.eye(6), atol=2e-14)
    assert diagnostics.smallest_singular_value >= 0.0193
    assert diagnostics.condition_number <= 96.1
    assert diagnostics.homological_relative_residual < 1.0e-10
    assert diagnostics.graph_gauge_relative_residual < 1.0e-10
    assert diagnostics.hessian_conservation_relative_residual < 1.0e-10
    assert diagnostics.predicted_reduced_hessian_relative_norm < 1.0e-10
    assert diagnostics.hessian_fourier_leakage_relative_norm < 1.0e-10
    assert diagnostics.zero_wave_hessian_frobenius_norm > 0.6
    assert diagnostics.positive_second_harmonic_hessian_frobenius_norm > 2.0
    np.testing.assert_allclose(
        diagnostics.negative_second_harmonic_hessian_frobenius_norm,
        diagnostics.positive_second_harmonic_hessian_frobenius_norm,
        atol=1.0e-14,
        rtol=0.0,
    )


def test_stripe_chart_stays_on_the_fixed_conservation_leaf() -> None:
    model = build_stripe_quadratic_model()
    direction = np.arange(1.0, 7.0)
    coordinates = 0.01 * direction / np.linalg.norm(direction)
    base_conserved = global_conserved_quantities(
        model.chart.base.reshape(1, model.size, 9)
    )
    chart_conserved = global_conserved_quantities(
        model.chart.evaluate(coordinates).reshape(1, model.size, 9)
    )
    np.testing.assert_allclose(chart_conserved, base_conserved, atol=2.0e-14)


def test_stripe_quotient_lifts_exactly_to_a_y_independent_square_state() -> None:
    model = build_stripe_quadratic_model()
    direction = np.arange(1.0, 7.0)
    coordinates = 0.01 * direction / np.linalg.norm(direction)
    stripe = model.chart.evaluate(coordinates).reshape(1, model.size, 9)
    quotient_step = model.full_map(stripe.ravel()).reshape(1, model.size, 9)
    square_step = bgk_periodic_step(
        np.repeat(stripe, model.size, axis=0),
        model.omega,
    )
    np.testing.assert_allclose(
        square_step,
        np.repeat(quotient_step, model.size, axis=0),
        atol=1.0e-14,
        rtol=0.0,
    )


@pytest.mark.parametrize("size", [3, 4, 18, True])
def test_stripe_model_rejects_grids_outside_the_registered_parity(size: int) -> None:
    with pytest.raises(ValueError, match="odd integer of at least five"):
        build_stripe_quadratic_model(size=size)


def test_stripe_defect_checks_coordinate_and_state_dimensions() -> None:
    model = build_stripe_quadratic_model()
    with pytest.raises(ValueError, match="coordinate dimension"):
        model.reduced_map(np.zeros(5))
    with pytest.raises(ValueError, match="state dimension"):
        model.full_map(np.zeros(152))
