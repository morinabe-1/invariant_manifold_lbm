"""Small, explicitly synthetic paths; no registered 17/33/65 LBM chart is built."""

from dataclasses import replace
from fractions import Fraction as F
from types import SimpleNamespace

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_chart as quadratic
from research import d3q27_cubic_chart as cubic
from research import d3q27_cubic_defect as diagnosis
from research import d3q27_damping as damping
from research import polynomial_path as poly


def physical(spectrum):
    return cubic.checked_real(
        np.fft.ifftn(spectrum, axes=(0, 1, 2), norm="ortho"), "synthetic field"
    )


class ToyChart:
    """Two real coordinates with conjugate Fourier slots and nonzero G2/G3."""

    def __init__(self, size=7):
        q = SimpleNamespace(size=size, omega=1.5, eta=0.02, power=2)
        q.base = d3.uniform_equilibrium((size,) * 3, np.array((0.125, 0.012, -0.006, 0.009)))
        # Deliberately not a fixed point: deleting C0 must be detectable.
        q.base[..., 13] += 0.001
        q.real_linear = np.array(((0.7, -0.15), (0.15, 0.7)))
        q.reduced_hessian = np.array(
            (((0.06, 0.02), (0.02, -0.03)), ((0.01, -0.02), (-0.02, 0.04)))
        )
        transform = np.array(((1, 1j), (1, -1j))) / np.sqrt(2)
        q.complex_coordinates = lambda a: transform @ np.asarray(a)
        q.input_pairs = np.array(((0, 0), (0, 1), (1, 1)))
        q.output_waves = np.array(((2, 0, 0), (0, 0, 0), (-2, 0, 0)))
        q.hessian_fibers = np.stack(
            (0.015 * d3.WEIGHTS, 0.009 * d3.WEIGHTS * d3.VELOCITIES[:, 1], 0.015 * d3.WEIGHTS)
        )
        self.quadratic = q
        self.waves = np.array(((-3, 0, 0), (-1, 0, 0), (1, 0, 0), (3, 0, 0)))
        self.response = cubic.GroupedPolynomial(
            np.array(((0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1))),
            np.array((3, 2, 1, 0)),
            np.stack(
                (0.012 * d3.WEIGHTS, 0.006 * d3.WEIGHTS, 0.006 * d3.WEIGHTS, 0.012 * d3.WEIGHTS)
            ),
            dimension=2,
            group_count=4,
        )
        q.linear_fourier = self.linear_fourier
        q.linear_field = lambda a: physical(self.linear_fourier(a))[0]
        q.quadratic_field = lambda a: physical(self.quadratic_fourier(a))[0]

    def linear_fourier(self, a):
        q = self.quadratic
        z = q.complex_coordinates(a)
        field = np.zeros_like(q.base, dtype=complex)
        for wave, value in zip(((1, 0, 0), (-1, 0, 0)), z, strict=True):
            field[quadratic.wave_slot(wave, q.size)] = value * d3.WEIGHTS
        return field

    def quadratic_fourier(self, a):
        q = self.quadratic
        z = q.complex_coordinates(a)
        field = np.zeros_like(q.base, dtype=complex)
        for indices, wave, coefficient in zip(
            q.input_pairs, q.output_waves, q.hessian_fibers, strict=True
        ):
            field[quadratic.wave_slot(wave, q.size)] += coefficient * np.prod(z[indices])
        return field

    def cubic_fourier(self, a):
        q = self.quadratic
        field = np.zeros_like(q.base, dtype=complex)
        for wave, value in zip(
            self.waves, self.response.evaluate(q.complex_coordinates(a)), strict=True
        ):
            field[quadratic.wave_slot(wave, q.size)] = value
        return field

    def cubic_field(self, a):
        return physical(self.cubic_fourier(a))[0]

    def reduced_cubic(self, a):
        x, y = a
        return np.array((0.005 * x**3 - 0.003 * x * y * y, 0.004 * y**3 + 0.002 * x * x * y))

    def physical_with_audit(self, spectrum):
        return physical(spectrum)

    def reduced(self, a, degree):
        q = self.quadratic
        value = q.real_linear @ a + 0.5 * np.einsum("ijk,j,k->i", q.reduced_hessian, a, a)
        return value if degree == 2 else value + self.reduced_cubic(a)

    def embed(self, a, degree):
        spectrum = self.linear_fourier(a) + self.quadratic_fourier(a)
        if degree == 3:
            spectrum += self.cubic_fourier(a)
        return self.quadratic.base + physical(spectrum)[0]


@pytest.fixture(scope="module")
def models():
    toy = ToyChart()
    direction = np.array((0.6, -0.8))
    return (
        toy,
        direction,
        {
            (d, arm): diagnosis.build_profile(toy, direction, d, arm=arm)
            for d in (2, 3)
            for arm in diagnosis.ARMS
        },
    )


@pytest.fixture(scope="module")
def local_pair():
    rng = np.random.default_rng(2026090802)
    base = d3.uniform_equilibrium((2, 3, 4), np.array((0.125, 0.04, -0.015, 0.012)))
    base[..., 13] += 0.001
    fields = (base, *(rng.standard_normal(base.shape) * 0.002 for _ in range(3)))
    return fields, {arm: diagnosis.local_expansion(fields, arm=arm) for arm in diagnosis.ARMS}


@pytest.mark.parametrize("degree,arm", [(d, a) for d in (2, 3) for a in diagnosis.ARMS])
def test_composition_and_full_physical_reconstruction(models, degree, arm):
    toy, u, profiles = models
    profile = profiles[degree, arm]
    for t in (-0.08, 0.04):
        a = t * u
        w = toy.embed(a, degree)
        wr = toy.embed(toy.reduced(a, degree), degree)
        phi = damping.periodic_step(w, 1.5, 0.02, 2)
        record = diagnosis.sample_diagnostics(profile, t, {"W": w, "W_R": wr, "Phi_W": phi})
        assert record["H1_reconstruction_passed"]
        assert record["P9_vector_passed"]
        assert all(v["gram_passed"] for v in record["truncations"])
        assert record["group_order"] == ["low_0_to_d", "leading_d_plus_1", "higher_d_plus_2_to_9"]
        assert record["group_contribution_norms"][0] > 1e-6
        assert np.all(np.tril(record["signed_cross_terms"]) == 0)


@pytest.mark.parametrize("degree,n", [(d, n) for d in (2, 3) for n in range(10)])
def test_all_profile_vectors_agree_between_independent_arms(models, degree, n):
    toy, _, profiles = models
    first, second = profiles[degree, "primary"], profiles[degree, "independent"]
    for a, b in (
        (first.coefficients[n], second.coefficients[n]),
        (first.composition.coefficient(n)[0], second.composition.coefficient(n)[0]),
        (
            first.local.mapped_coefficient(n, 1.5, 0.02, 2),
            second.local.mapped_coefficient(n, 1.5, 0.02, 2),
        ),
    ):
        assert diagnosis.norm(a - b) <= 1e-10 * max(1.0, diagnosis.norm(b))
    assert first.fields[0] is toy.quadratic.base


@pytest.mark.parametrize("arm", diagnosis.ARMS)
def test_nonunit_density_nonzero_momentum_and_non_cubic_grid(local_pair, arm):
    fields, pair = local_pair
    expansion = pair[arm]
    assert np.all(expansion.rho[0] > 1)
    assert np.max(np.abs(expansion.momentum[0])) > 0.03
    mapped = [expansion.mapped_coefficient(n, 1.5, 0.02, 2) for n in range(10)]
    for t in (-0.2, 0.125):
        w = diagnosis.horner(fields, t)
        actual = damping.periodic_step(w, 1.5, 0.02, 2)
        predicted = diagnosis.horner(mapped, t) + expansion.tail(t, 1.5, 0.02, 2)
        assert diagnosis.norm(predicted - actual) < 1e-13
    # Independent Fourier filter, including the full square of the summed stencil.
    collision = d3.collide_bgk(diagnosis.horner(fields, 0.125), 1.5)
    fft = damping.fft_filter(d3.stream_periodic(collision), 0.02, 2)
    assert diagnosis.norm(actual - fft.real) < 1e-13


def test_primary_population_slicing_matches_full_tensor_quotient(local_pair):
    _, pair = local_pair
    expansion = pair["primary"]
    numerator = np.stack(diagnosis._numerator_coefficients(expansion.momentum, "primary"))
    full = poly.quotient(numerator, expansion.rho[..., None], order=9)
    np.testing.assert_array_equal(np.stack(expansion.quotient), full)


def test_multinomial_inverse_matches_exact_scalar_geometric_formula():
    rho = np.array((1.125, 0.0625, -0.03125, 0.015625))
    actual = diagnosis.inverse_multinomial(rho)
    from research.q012g2_cubic_defect_oracle import geometric_quotient

    expected = geometric_quotient([F(1)], list(map(F.from_float, rho)), 9)
    np.testing.assert_allclose(actual, list(map(float, expected)), rtol=2e-14, atol=1e-16)


def test_independent_arm_cannot_call_primary_lift_division_or_convolution(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("independent arm called primary path algebra")

    monkeypatch.setattr(poly, "homogeneous_composition", forbidden)
    monkeypatch.setattr(poly, "quotient", forbidden)
    monkeypatch.setattr(poly, "convolve", forbidden)
    profile = diagnosis.build_profile(ToyChart(), np.array((0.6, -0.8)), 3, arm="independent")
    assert len(profile.coefficients) == 10


def test_deleting_constant_defect_and_dropping_G3_are_detected(models):
    toy, u, profiles = models
    profile = profiles[3, "primary"]
    t = 0.2
    a = t * u
    original = {"W": toy.embed(a, 3), "W_R": toy.embed(toy.reduced(a, 3), 3)}
    original["Phi_W"] = damping.periodic_step(original["W"], 1.5, 0.02, 2)
    damaged = replace(
        profile, coefficients=(np.zeros_like(profile.coefficients[0]),) + profile.coefficients[1:]
    )
    assert not diagnosis.sample_diagnostics(damaged, t, original)["H1_reconstruction_passed"]
    reduced = profile.reduced.copy()
    reduced[3] = 0
    missing = diagnosis.composition_path(toy, reduced, 3, arm="primary").evaluate(t)[0]
    assert diagnosis.norm(missing - original["W_R"]) > 1e-9
    replacement = cubic.GroupedPolynomial(
        toy.response.indices,
        np.repeat(
            toy.response.outputs, np.diff(np.r_[toy.response.starts, len(toy.response.indices)])
        ),
        toy.response.coefficients / 6,
        dimension=2,
        group_count=4,
    )
    bad = SimpleNamespace(
        quadratic=toy.quadratic,
        waves=toy.waves,
        response=replacement,
        physical_with_audit=toy.physical_with_audit,
    )
    wrong = diagnosis.composition_path(bad, profile.reduced, 3, arm="primary").evaluate(t)[0]
    assert diagnosis.norm(wrong - original["W_R"]) > 1e-9


@pytest.mark.parametrize("bad", ["dtype", "shape", "nonfinite", "zero_density", "degree", "arm"])
def test_invalid_local_paths_are_rejected(local_pair, bad):
    fields, _ = local_pair
    values = [v.copy() for v in fields]
    arm = "primary"
    if bad == "dtype":
        values[1] = values[1].astype(np.float32)
    elif bad == "shape":
        values[1] = values[1][..., :1]
    elif bad == "nonfinite":
        values[1][0, 0, 0, 0] = np.nan
    elif bad == "zero_density":
        values[0].fill(0)
    elif bad == "degree":
        values = values[:2]
    else:
        arm = "unknown"
    with pytest.raises(ValueError):
        diagnosis.local_expansion(values, arm=arm)


@pytest.mark.parametrize(
    "bad", [np.array((0.0, 1.0)), np.array((1.0, np.inf)), np.array((1.0,), dtype=np.float32)]
)
def test_bad_independent_denominators_are_rejected(bad):
    with pytest.raises(ValueError):
        diagnosis.inverse_multinomial(bad)


def test_overflow_and_invalid_original_field_cannot_be_silently_accepted(models):
    with pytest.raises(FloatingPointError):
        diagnosis.horner([np.array([1e308]), np.array([1e308])], 2.0)
    with pytest.raises((ValueError, FloatingPointError)):
        diagnosis.inverse_multinomial(np.array((1e-308, 1e308)))
    _, _, profiles = models
    with pytest.raises(ValueError):
        diagnosis.sample_diagnostics(
            profiles[3, "primary"],
            0.1,
            dict.fromkeys(("W", "W_R", "Phi_W"), np.zeros((7, 7, 7, 1))),
        )


def test_reduced_constant_and_support_aliasing_are_not_ignored(models):
    toy, _, profiles = models
    reduced = profiles[3, "primary"].reduced.copy()
    reduced[0, 0] = 0.001
    with pytest.raises(ValueError):
        diagnosis.composition_path(toy, reduced, 3, arm="primary")
    with pytest.raises(ValueError):
        diagnosis.physical_path(toy, np.array((1.0, 0.0)), True)
    with pytest.raises(ValueError):
        diagnosis.composition_path(ToyChart(5), profiles[3, "primary"].reduced, 3, arm="primary")


@pytest.mark.parametrize("degree", (2, 3))
def test_complete_independent_vector_report_and_last_coefficient_tampering(models, degree):
    _, _, profiles = models
    first, second = profiles[degree, "primary"], profiles[degree, "independent"]
    report = diagnosis.compare_profiles(first, second)
    assert report["passed"] and report["full_vector_comparisons"] == 34 + degree
    assert report["rows"][-1]["name"] == "C9"
    last = second.coefficients[-1].copy()
    last[-1, -1, -1, -1] += 1e-4
    altered = replace(second, coefficients=second.coefficients[:-1] + (last,))
    report = diagnosis.compare_profiles(first, altered)
    assert not report["passed"] and not report["rows"][-1]["passed"]


def test_nonpositive_evaluated_density_and_wrong_arm_pair_are_rejected(models, local_pair):
    _, _, profiles = models
    with pytest.raises(ValueError):
        diagnosis.compare_profiles(profiles[3, "primary"], profiles[3, "primary"])
    _, pair = local_pair
    rho = pair["primary"].rho.copy()
    rho[1].fill(-100.0)
    altered = replace(pair["primary"], rho=rho)
    with pytest.raises(ValueError):
        altered.tail(0.125, 1.5, 0.02, 2)


def test_lift_handles_nonzero_constant_complex_paths_and_duplicate_monomials():
    engine = cubic.GroupedPolynomial(
        np.array(((0, 0, 1), (0, 0, 1), (1, 1, 1))),
        np.array((1, 1, 0)),
        np.array(((1 + 1j,), (2 - 1j,), (3.0,))),
        dimension=2,
        group_count=3,
    )
    path = np.array(((1 + 1j, 2.0), (0.25, -0.125j), (0.03125, 0.0625)))
    first = diagnosis.lift_engine(engine, path, arm="primary")
    second = diagnosis.lift_engine(engine, path, arm="independent")
    np.testing.assert_allclose(first, second, rtol=1e-14, atol=1e-14)
    for t in (-0.25, 0.125):
        np.testing.assert_allclose(
            poly.evaluate(first, t), engine.evaluate(poly.evaluate(path, t)), rtol=1e-14, atol=1e-14
        )
