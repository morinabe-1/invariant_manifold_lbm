"""Algebraic/physical unit checks, not a receipt for the registered real pilot."""

from itertools import combinations_with_replacement, permutations
from math import factorial

import numpy as np
import pytest
from scipy.linalg import block_diag

from research import d3q27 as lattice
from research import d3q27_quartic_lbm as primary
from research import d3q27_quartic_physical as physical
from research import d3q27_quartic_polynomial as reference


def inventory(*, size=9, seed=2026090801):
    rng = np.random.default_rng(seed)
    waves = np.repeat(np.array([[-1, 0, 0], [0, 0, 0], [1, 0, 0]], dtype=np.int64), 2, axis=0)
    n = len(waves)
    indices = {
        d: np.array(list(combinations_with_replacement(range(n), d)), dtype=np.int64)
        for d in (2, 3)
    }
    complex_random = lambda shape: rng.standard_normal(shape) + 1j * rng.standard_normal(shape)
    h = {d: complex_random((len(ids), 27)) / 17 for d, ids in indices.items()}
    g = {d: complex_random((len(ids), 2)) / 13 for d, ids in indices.items()}
    for degree, ids in indices.items():
        output = waves[ids].sum(axis=1)
        g[degree][np.abs(output[:, 0]) > 1] = 0
    linear = block_diag(*(np.array([[0.6 + 0.1j, 0.3], [0, 0.7 - 0.1j]]) for _ in range(3)))
    return {
        "size": size,
        "omega": 1.5,
        "eta": 0.02,
        "power": 2,
        "waves": waves,
        "basis": complex_random((27, n)) / 9,
        "linear": linear,
        "indices": indices,
        "h": h,
        "g": g,
    }


@pytest.fixture(scope="module")
def data():
    return primary.TaylorData(**inventory())


@pytest.mark.parametrize("dimension", [1, 2, 6, 104])
@pytest.mark.parametrize("degree", [2, 3])
def test_complete_lexicographic_rank(dimension, degree):
    ids = np.array(list(combinations_with_replacement(range(dimension), degree)), dtype=np.int64)
    np.testing.assert_array_equal(primary.monomial_ranks(ids, dimension), np.arange(len(ids)))
    rng = np.random.default_rng(51)
    order = rng.permutation(len(ids))
    np.testing.assert_array_equal(primary.monomial_ranks(ids[order], dimension), order)


@pytest.mark.parametrize(
    "ids,expected",
    [([0, 0], 2), ([0, 1], 1), ([0, 0, 0], 6), ([0, 0, 1], 2), ([0, 1, 1], 2), ([0, 1, 2], 1)],
)
def test_raw_multiindex_not_uniform_factor(ids, expected):
    assert primary.raw_factors(np.array([ids]))[0] == expected


def test_shuffled_archives_preserve_all_derivatives(data):
    inputs = inventory()
    for degree in (2, 3):
        for key in ("indices", "h", "g"):
            inputs[key][degree] = inputs[key][degree][::-1].copy()
    other = primary.TaylorData(**inputs)
    for degree in (2, 3):
        for ids in data.indices[degree]:
            np.testing.assert_array_equal(data.derivative(ids), other.derivative(ids))
            np.testing.assert_array_equal(
                data.derivative(ids, reduced=True), other.derivative(ids, reduced=True)
            )


@pytest.mark.parametrize("kind", ["missing", "duplicate", "off_shell", "linear_wave", "nan"])
def test_input_corruption_rejected(kind):
    inputs = inventory()
    if kind == "missing":
        inputs["indices"][3] = inputs["indices"][3][:-1]
    elif kind == "duplicate":
        inputs["indices"][3][-1] = inputs["indices"][3][0]
    elif kind == "off_shell":
        inputs["g"][3][0, 0] = 1
    elif kind == "linear_wave":
        inputs["linear"][5, 0] = 1e-100
    else:
        inputs["h"][3][-1, -1] = np.nan
    with pytest.raises(ValueError):
        primary.TaylorData(**inputs)


def test_nilpotent_algebra_known_multiplicity():
    z = np.zeros(16, dtype=complex)
    z[[1, 2, 4, 8]] = 1
    power = z
    for _ in range(3):
        power = reference.multiply(power, z)
    assert power[15] == factorial(4)
    assert np.count_nonzero(power) == 1
    density = 1j * z
    density[0] = 1
    identity = reference.multiply(density, reference.inverse_density(density))
    np.testing.assert_array_equal(identity, np.r_[1, np.zeros(15)])


@pytest.mark.parametrize("degree", [2, 3, 4])
def test_local_derivative_from_original_rational_equilibrium(degree):
    rng = np.random.default_rng(734)
    u = rng.standard_normal((4, 4)) + 1j * rng.standard_normal((4, 4))
    rho, momentum = np.zeros(16, dtype=complex), np.zeros((16, 3), dtype=complex)
    rho[0] = 1
    for j in range(degree):
        rho[1 << j] = u[j, 0]
        momentum[1 << j] = u[j, 1:]
    inverse = reference.inverse_density(rho)
    actual = []
    for q, c in enumerate(lattice.VELOCITIES):
        cj = momentum @ c
        numerator = 4.5 * reference.multiply(cj, cj)
        for axis in range(3):
            numerator -= 1.5 * reference.multiply(momentum[:, axis], momentum[:, axis])
        actual.append(
            lattice.WEIGHTS[q] * reference.multiply(numerator, inverse)[(1 << degree) - 1]
        )
    expected = (
        primary.local_b(*u[:2])
        if degree == 2
        else primary.local_c(*u[:3])
        if degree == 3
        else primary.local_d(u)
    )
    np.testing.assert_allclose(actual, expected, rtol=3e-14, atol=1e-13)
    assert np.linalg.norm(np.asarray(actual).imag) > 1e-3


def test_every_mixed_coefficient_and_seven_nonzero_groups(data):
    maxima = np.zeros(7)
    for slots in combinations_with_replacement(range(data.dimension), 4):
        groups = primary.raw_terms(data, slots)
        other = reference.raw_forcing(data, slots)
        np.testing.assert_allclose(
            primary.forcing(groups), other["forcing"], rtol=2e-12, atol=3e-16
        )
        np.testing.assert_allclose(
            groups[:4].sum(axis=0), other["collision"], rtol=2e-12, atol=3e-16
        )
        np.testing.assert_allclose(
            groups[4:].sum(axis=0), other["composition"], rtol=2e-12, atol=3e-16
        )
        maxima = np.maximum(maxima, np.linalg.norm(groups, axis=1))
    assert np.all(maxima > 1e-6)


def test_slot_permutations_and_complex_multilinearity(data):
    slots = (0, 2, 3, 5)
    original = primary.raw_terms(data, slots)
    for order in permutations(slots):
        np.testing.assert_allclose(primary.raw_terms(data, order), original, rtol=1e-12, atol=1e-16)
        np.testing.assert_allclose(
            reference.raw_forcing(data, order)["forcing"],
            primary.forcing(original),
            rtol=1e-12,
            atol=1e-16,
        )


@pytest.mark.parametrize(
    "groups", [(0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 2), (0, 1, 2, 3)]
)
def test_actual_nonnormal_product_and_independent_columns(data, groups):
    # Use six one-coordinate blocks only in the all-distinct case; diagonalize
    # by specifying diagonal input dynamics, not by changing any actual LBM data.
    if groups == (0, 1, 2, 3):
        inputs = inventory()
        inputs["linear"] = np.diag(np.diag(inputs["linear"]))
        data = primary.TaylorData(**inputs)
        blocks = tuple((i,) for i in range(6))
    else:
        blocks = ((0, 1), (2, 3), (4, 5))
    value = primary.block_product(data, groups, blocks)
    np.testing.assert_allclose(value.basis.T @ value.basis, np.eye(len(value.keys)), atol=1e-15)
    np.testing.assert_allclose(
        value.full_dynamics @ value.basis, value.basis @ value.dynamics, atol=1e-15
    )
    for permutation in set(permutations(groups)):
        other = primary.block_product(data, permutation, blocks)
        assert value.keys == other.keys
        np.testing.assert_allclose(value.dynamics, other.dynamics, atol=1e-15)
    terms = primary.group_terms(data, value)
    independent = reference.group_forcing(data, groups, blocks)
    np.testing.assert_allclose(
        primary.forcing(terms), independent["forcing"], rtol=1e-12, atol=1e-15
    )
    assert tuple(ids for ids, _ in reference.columns(groups, blocks)) == value.keys
    # Taylor coefficient of a direct homogeneous quartic evaluation.
    rng = np.random.default_rng(873)
    z = rng.standard_normal(6) + 1j * rng.standard_normal(6)
    monomials = np.array([np.prod(z[list(ids)]) for ids in value.keys])
    full_z = np.array([np.prod(z[list(ids)]) for ids in value.rows])
    denominator = np.prod([factorial(groups.count(b)) for b in set(groups)])
    np.testing.assert_allclose(
        (primary.forcing(terms) * value.factors) @ monomials,
        primary.forcing(terms) @ (value.basis.T @ full_z) / denominator,
        rtol=1e-12,
        atol=1e-15,
    )


def test_internal_coordinates_outside_input_tuple_are_not_lost(data):
    slots = (0, 0, 4, 5)
    terms = primary.raw_terms(data, slots)
    inputs = inventory()
    # Incoming waves -1,-1,+1,+1 create zero-wave internal coordinates 2,3.
    for degree in (2, 3):
        zero = np.all(inputs["waves"][inputs["indices"][degree]].sum(axis=1) == 0, axis=1)
        inputs["g"][degree][zero] = 0
    truncated = primary.TaylorData(**inputs)
    wrong = primary.forcing(primary.raw_terms(truncated, slots))
    correct = reference.raw_forcing(data, slots)["forcing"]
    assert np.linalg.norm(wrong - correct) > 1e-4
    np.testing.assert_allclose(primary.forcing(terms), correct, rtol=1e-12, atol=1e-15)


@pytest.mark.parametrize("mutation", primary.MUTATIONS)
def test_each_mutation_has_an_actual_nonzero_witness(data, mutation):
    errors = []
    for slots in ((0, 0, 0, 0), (0, 0, 2, 4), (0, 2, 4, 5)):
        expected = reference.raw_forcing(data, slots)["forcing"]
        wrong = primary.forcing(primary.raw_terms(data, slots, mutation=mutation))
        errors.append(np.linalg.norm(wrong - expected) / max(1e-14, np.linalg.norm(expected)))
    assert max(errors) > 1e-8


@pytest.mark.parametrize(
    "slots", [(0, 0, 0, 0), (0, 0, 0, 2), (0, 0, 4, 4), (0, 0, 2, 4), (0, 1, 2, 5)]
)
def test_physical_fft_stencil_all_output_coefficients(data, slots):
    expected = reference.raw_forcing(data, slots)
    samples = []
    actual = physical.fourth_coefficient(data, slots, sample=samples.append)
    scale = max(1e-14, np.linalg.norm(expected["forcing"]))
    assert (
        np.hypot(np.linalg.norm(actual["forcing"] - expected["forcing"]), actual["off_wave_norm"])
        / scale
        < 1e-11
    )
    np.testing.assert_allclose(actual["collision"], expected["collision"], rtol=1e-11, atol=1e-16)
    assert actual["fft_coefficients_inspected"] == 27 * data.size**3
    assert len(samples) == 28


def test_reference_does_not_call_main_formula_factor_or_product(data, monkeypatch):
    expected = reference.raw_forcing(data, (0, 0, 2, 5))

    def forbidden(*args, **kwargs):
        raise AssertionError("reference shared the primary derivative machinery")

    for name in ("raw_terms", "raw_factors", "block_product", "local_b", "local_c", "local_d"):
        monkeypatch.setattr(primary, name, forbidden)
    for name in ("derivative", "rows", "contract", "internal", "linear_argument"):
        monkeypatch.setattr(data, name, forbidden)
    np.testing.assert_array_equal(
        reference.raw_forcing(data, (0, 0, 2, 5))["forcing"], expected["forcing"]
    )


def test_calibration_selection_keeps_lex_first_and_mandatory():
    from research.d3q27_quartic_selection import seed_groups

    blocks = tuple(
        tuple(range(4 * (b // 3) + (0, 2, 3)[b % 3], 4 * (b // 3) + (2, 3, 4)[b % 3]))
        for b in range(78)
    )
    groups = seed_groups()
    cases = physical.calibration_cases(groups, blocks)
    assert cases == physical.calibration_cases(groups[::-1], blocks)
    mandatory = [row for row in cases if row["group"] == (0, 3, 6, 9)]
    assert [row["column"] for row in mandatory] == [0, 15]
    assert all(
        row["column"] in (0, len(reference.columns(row["group"], blocks)) - 1) for row in cases
    )
    with pytest.raises(ValueError, match="mandatory"):
        physical.calibration_cases([g for g in groups if g != (0, 3, 6, 9)], blocks)


@pytest.mark.parametrize("axes", [(1, 1, 0), (1, 1, 1), (0, 1, -1)])
def test_physical_cross_axis_filter_and_streaming(axes):
    inputs = inventory()
    inputs["waves"] = inputs["waves"][:, :1] * np.array(axes, dtype=np.int64)
    data = primary.TaylorData(**inputs)
    slots = (0, 0, 0, 2)
    expected = primary.forcing(primary.raw_terms(data, slots))
    actual = physical.fourth_coefficient(data, slots)
    assert (
        np.hypot(np.linalg.norm(actual["forcing"] - expected), actual["off_wave_norm"])
        / np.linalg.norm(expected)
        < 1e-11
    )


def test_all_560_products_match_frozen_oracle_including_sixteen_columns():
    from research import d3q27_quartic_operator as oracle

    maximum = 0
    for dimensions in oracle.DIMENSIONS:
        n = sum(dimensions)
        offsets = np.cumsum((0, *dimensions))
        blocks = tuple(tuple(range(offsets[b], offsets[b + 1])) for b in range(4))
        indices = {
            d: np.array(list(combinations_with_replacement(range(n), d)), dtype=np.int64)
            for d in (2, 3)
        }
        data = primary.TaylorData(
            size=9,
            omega=1.5,
            eta=0.02,
            power=2,
            waves=np.zeros((n, 3), dtype=np.int64),
            basis=np.zeros((27, n), dtype=complex),
            linear=block_diag(*(oracle.dynamics(b, d) for b, d in enumerate(dimensions))),
            indices=indices,
            h={d: np.zeros((len(ids), 27), dtype=complex) for d, ids in indices.items()},
            g={d: np.zeros((len(ids), n), dtype=complex) for d, ids in indices.items()},
        )
        for groups in oracle.GROUPS:
            actual, expected = (
                primary.block_product(data, groups, blocks),
                oracle.build_product(dimensions, groups),
            )
            assert actual.keys == expected.keys
            for name in ("basis", "factors", "full_dynamics", "dynamics"):
                np.testing.assert_array_equal(getattr(actual, name), getattr(expected, name))
            maximum = max(maximum, len(actual.keys))
    assert maximum == 16
