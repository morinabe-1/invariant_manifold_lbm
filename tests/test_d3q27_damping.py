from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_damping as damping
from research import d3q27_quadratic as q
from research import q012c1_d3q27_damping as runner
from research import q012c_d3q27_preflight as q012c


@pytest.fixture(scope="module")
def context() -> damping.CoefficientContext:
    return damping.build_context(17, 1.2)


@pytest.fixture(scope="module")
def controls() -> dict:
    return {
        "map": damping.map_controls(),
        "hydrodynamics": damping.hydrodynamic_controls(),
        "hessian": damping.hessian_controls(),
        "direct_grid": damping.direct_grid_control(),
    }


def test_prior_valid_rejection_and_source_seals_are_intact() -> None:
    assert runner.input_audit()["passed"]


def test_all_registered_independent_controls(controls: dict) -> None:
    assert all(value["passed"] for value in controls.values())
    assert len(controls["map"]["records"]) == 8
    assert len(controls["hydrodynamics"]["records"]) == 128
    assert len(controls["hydrodynamics"]["direct_nyquist"]) == 96
    assert len(controls["hessian"]["records"]) == 8
    for row in controls["map"]["records"]:
        assert len(row["rollouts"]) == 4
        assert row["stencil"]["negative_count"] == (0 if row["power"] == 1 else 18)
    for row in controls["hessian"]["records"]:
        assert row["wrong_input_filter_relative_error"] > 1e-3
        assert row["samples"][-1]["relative_error"] < row["samples"][0]["relative_error"]
    assert controls["direct_grid"]["direct"]["orbit_count"] == 17**3


def test_filter_squared_sum_includes_cross_terms_and_preserves_mean() -> None:
    size = 7
    z, y, x = np.indices((size,) * 3)
    wave = (1, 2, 1)
    phase = np.exp(2j * np.pi * (x + 2 * y + z) / size)
    field = np.broadcast_to(phase[..., None], (size,) * 3 + (27,)).copy()
    for power in damping.POWERS:
        filtered = damping.apply_filter(field, 0.05, power)
        mu = damping.wave_multiplier(wave, size, 0.05, power)
        np.testing.assert_allclose(filtered, mu * field, rtol=0, atol=3e-15)
        np.testing.assert_allclose(damping.fft_filter(field, 0.05, power), filtered, atol=3e-15)
    k = 2 * np.pi * np.asarray(wave) / size
    wrong_mu = 1 - 0.05 * np.sum(np.sin(k / 2) ** 4)
    assert abs(wrong_mu - damping.multiplier(k, 0.05, 2)) > 0.02
    constant = np.broadcast_to(d3.WEIGHTS, field.shape).copy()
    np.testing.assert_array_equal(damping.apply_filter(constant, 0.1, 2), constant)


def test_eta_zero_is_bitwise_and_nonmutating() -> None:
    rng = np.random.default_rng(12)
    field = rng.standard_normal((3, 5, 7, 27))
    saved = field.copy()
    result = damping.apply_filter(field, 0, 2)
    np.testing.assert_array_equal(field, saved)
    np.testing.assert_array_equal(result, field)
    assert result is not field


@pytest.mark.parametrize(
    "eta,power",
    [
        (-0.1, 1),
        (0.1001, 2),
        (float("nan"), 1),
        (float("inf"), 2),
        (True, 1),
        (0.01, 0),
        (0.01, 3),
        (0.01, True),
        (0.01, 1.5),
    ],
)
def test_invalid_filter_parameters_are_rejected(eta: float, power: int) -> None:
    with pytest.raises(ValueError):
        damping.apply_filter(np.zeros((3, 3, 3, 27)), eta, power)


def test_invalid_wave_and_state_shapes_are_rejected() -> None:
    with pytest.raises(ValueError):
        damping.multiplier(np.ones(2), 0.05, 2)
    with pytest.raises(ValueError):
        damping.multiplier(np.array([0, 1j, 2]), 0.05, 2)
    with pytest.raises(ValueError):
        damping.apply_filter(np.zeros((3, 3, 27)), 0.05, 2)


def test_post_stream_hessian_uses_output_wave_not_input_damping(
    context: damping.CoefficientContext,
) -> None:
    left = context.frames[(1, 0, 0)].blocks[0]
    right = context.frames[(0, 1, 0)].blocks[1]
    size, omega, eta, power = 5, 1.2, 0.05, 2
    a, b = np.array([0.3 + 0.1j, -0.2 + 0.4j]), np.array([0.7 - 0.1j])
    _z, y, x = np.indices((size,) * 3)
    left_field = np.exp(2j * np.pi * x / size)[..., None] * (left.basis @ a)
    right_field = np.exp(2j * np.pi * y / size)[..., None] * (right.basis @ b)
    physical = damping.apply_filter(
        damping.mixed_hessian(left_field, right_field, omega), eta, power
    )
    mu = damping.wave_multiplier((1, 1, 0), size, eta, power)
    _, forcing, _ = q.product_forcing(left, right, (1, 1, 0), size, omega * mu)
    predicted = np.exp(2j * np.pi * (x + y) / size)[..., None] * (forcing @ np.kron(b, a))
    np.testing.assert_allclose(physical, predicted, rtol=1e-13, atol=3e-14)
    wrong = damping.mixed_hessian(
        damping.apply_filter(left_field, eta, power),
        damping.apply_filter(right_field, eta, power),
        omega,
    )
    assert damping.relative_error(wrong, physical) > 1e-3


def test_scaled_operator_equals_independent_matrix_assembly(
    context: damping.CoefficientContext,
) -> None:
    left = context.frames[(1, 0, 0)].blocks[0]
    right = context.frames[(0, 1, 0)].blocks[0]
    output = (1, 1, 0)
    sector = context.sectors[output]
    eta, power = 0.05, 2
    mu_l = damping.wave_multiplier(left.wave, 17, eta, power)
    mu_r = damping.wave_multiplier(right.wave, 17, eta, power)
    mu_o = damping.wave_multiplier(output, 17, eta, power)
    product, forcing, _ = q.product_forcing(left, right, output, 17, 1.2)
    expected_dynamics = mu_l * mu_r * product
    expected_output = mu_o * sector.dynamics
    expected_forcing = sector.basis.conj().T @ sector.projection @ (mu_o * forcing)
    solution, expected = q.solve_homological(expected_output, expected_dynamics, expected_forcing)
    actual = damping.audit_scaled_pair(left, right, context, eta, power)
    # Different, algebraically equivalent floating association is intentional.
    for key in (
        "smallest_singular_value",
        "largest_singular_value",
        "forcing_norm",
        "response_local_norm",
    ):
        assert abs(actual[key] - expected[key]) <= 5e-11 * max(1, abs(expected[key]))
    assert actual["graph_gauge_error"] < 5e-12
    assert np.linalg.norm(context.frames[output].dual @ sector.basis @ solution) < 5e-11
    # A global multiple of the old operator would scale the input product
    # incorrectly: its factor is mu_l*mu_r, not mu_o.
    assert abs(mu_l * mu_r - mu_o) > 1e-4


def test_zero_wave_remains_on_fixed_conservation_leaf(context: damping.CoefficientContext) -> None:
    left = context.frames[(1, 0, 0)].blocks[0]
    right = context.frames[(-1, 0, 0)].blocks[1]
    for power in damping.POWERS:
        record = damping.audit_scaled_pair(left, right, context, 0.1, power)
        assert record["external_dimension"] == 23
        assert record["zero_wave_moment_error"] < 5e-12
        assert record["zero_wave_forcing_moment_error"] < 5e-12
        assert damping.wave_multiplier((0, 0, 0), 17, 0.1, power) == 1


def test_baseline_exact_full_pair_reproduction(
    context: damping.CoefficientContext, controls: dict
) -> None:
    prior = runner.prior_baselines()[17, 1.2]
    cycle = runner.condition_cycle(context, 1, 0, controls, prior)
    assert cycle["baseline_reproduction"]["passed"]
    assert cycle["coefficient_screen"]["pair_count"] == 3081
    assert cycle["coefficient_screen"]["product_dimension_sum"] == 5460
    assert not cycle["jointly_prequalified"]


def test_selected_projector_is_unchanged_but_normal_gap_is_not(
    context: damping.CoefficientContext,
) -> None:
    grid = damping.scaled_grid(context.grid, 0.05, 2)
    for original, modified in zip(context.grid["rows"], grid["rows"]):
        mu = damping.wave_multiplier(original["wave"], 17, 0.05, 2)
        np.testing.assert_array_equal(modified["full_values"], mu * original["full_values"])
        if "projector_norm" in original:
            assert original["projector_norm"] == modified["projector_norm"]
            assert modified["local_schur_sep"] == mu * original["local_schur_sep"]
    assert damping.scaled_grid(context.grid, 0, 1) is context.grid
    assert q.normal_ordering(context.grid, 3)["normal_modulus_gap"] < 0
    assert q.normal_ordering(grid, 3)["normal_modulus_gap"] > 0


def test_family_selection_requires_three_grids_and_biharmonic() -> None:
    def row(size: int, power: int, eta: float, omega: float = 1.2) -> dict:
        return {
            "size": size,
            "power": power,
            "eta": eta,
            "omega": omega,
            "coefficient_screen": {"coefficient_prequalified": True},
            "normal_ordering": {"normal_ordering_prequalified": True},
            "jointly_prequalified": True,
        }

    assert runner.classify_families([row(17, 2, 0.01)])[1] is None
    laplacian = [row(n, 1, 0.01) for n in runner.GRID_SIZES]
    assert runner.classify_families(laplacian)[1] is None
    rows = (
        laplacian
        + [row(n, 2, 0.02) for n in runner.GRID_SIZES]
        + [row(n, 2, 0.01, 1.8) for n in runner.GRID_SIZES]
    )
    assert runner.classify_families(rows)[1]["omega"] == 1.8
    rows += [row(n, 2, 0.01, 1.0) for n in runner.GRID_SIZES]
    assert runner.classify_families(rows)[1]["omega"] == 1.0
    assert len(runner.classify_families(rows)[0]) == 32


def test_invalid_inputs_create_no_tables_or_vacuous_acceptance(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runner, "input_audit", lambda: {"passed": False})
    result = runner.run_study(tmp_path / "tables")
    assert result["study_gate"] == "failed" and result["scientific_outcome"] == "inconclusive"
    assert result["cycle"]["selected_family"] is None
    assert not (tmp_path / "tables").exists()


def test_shear_basis_gauge_invariance_is_retained(context: damping.CoefficientContext) -> None:
    shear = context.frames[(0, 0, 1)].blocks[0]
    unitary = np.array(((1, 1j), (1j, 1))) / np.sqrt(2)
    rotated = replace(
        shear, basis=shear.basis @ unitary, dynamics=unitary.conj().T @ shear.dynamics @ unitary
    )
    first = damping.audit_scaled_pair(shear, shear, context, 0.05, 2)
    second = damping.audit_scaled_pair(rotated, rotated, context, 0.05, 2)
    for key in (
        "smallest_singular_value",
        "largest_singular_value",
        "forcing_norm",
        "response_local_norm",
    ):
        assert abs(first[key] - second[key]) < 5e-11 * max(1, abs(first[key]))


def test_pair_storage_rejects_inconsistent_rows() -> None:
    with pytest.raises(ValueError):
        q012c.pack_pairs({"pair_records": [{"one": 1}, {"two": 2}]})
