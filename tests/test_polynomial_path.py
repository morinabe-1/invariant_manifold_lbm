"""Independent elementary and combinatorial checks of ascending path algebra."""

from fractions import Fraction
from itertools import product

import numpy as np
import pytest

from research import polynomial_path as p


def test_horner_and_coefficient_padding_with_pointwise_broadcast():
    np.testing.assert_array_equal(
        p.add([1, 2], [[10, 20], [30, 40], [50, 60]]), [[11, 21], [32, 42], [50, 60]]
    )
    assert p.evaluate([1, 2, 3], 0.25) == 1 + 2 * 0.25 + 3 * 0.25**2
    np.testing.assert_array_equal(p.evaluate([[1, 2], [3, 4]], 1j), [1 + 3j, 2 + 4j])


@pytest.mark.parametrize(
    "order, expected", [(None, [3, 10, 8]), (0, [3]), (5, [3, 10, 8, 0, 0, 0])]
)
def test_convolution_retains_requested_length(order, expected):
    np.testing.assert_array_equal(p.convolve([1, 2], [3, 4], order=order), expected)


def test_quotient_pointwise_denominator_broadcast_and_nonunit_constant():
    numerator = np.arange(18, dtype=float).reshape(3, 2, 3) / 8
    denominator = np.array([[[2.0], [4.0]], [[0.5], [-0.25]]])
    result = p.quotient(numerator, denominator, order=9)
    for site, component in product(range(2), range(3)):
        a, b = map(Fraction.from_float, denominator[:, site, 0])
        for n in range(10):
            reference = sum(
                Fraction.from_float(numerator[i, site, component]) * (-b / a) ** (n - i) / a
                for i in range(min(n + 1, 3))
            )
            assert result[n, site, component] == float(reference)


def test_remainder_keeps_low_degree_residues_and_full_numerator_degree():
    approximate = np.array([np.nextafter(1.0, 2.0), -0.25])
    remainder = p.remainder_numerator([1.0], [1.0, 0.25, 0.125], approximate)
    assert remainder.shape == (4,)
    assert remainder[0] == -np.finfo(float).eps
    for t in (-0.25, 0.125):
        exact = 1 / p.evaluate([1.0, 0.25, 0.125], t)
        combined = p.evaluate(approximate, t) + p.evaluate(remainder, t) / p.evaluate(
            [1.0, 0.25, 0.125], t
        )
        assert abs(exact - combined) < 1e-15


@pytest.mark.parametrize(
    "path_degree, monomial_degree, complex_data",
    tuple(product((0, 1, 3), (1, 2, 3), (False, True))),
)
def test_grouped_composition_matches_naive_multinomial_enumeration(
    path_degree, monomial_degree, complex_data
):
    rng = np.random.default_rng(2026090801)
    path = rng.integers(-3, 4, size=(path_degree + 1, 3)) / 8
    coefficients = rng.integers(-3, 4, size=(5, 2)) / 8
    if complex_data:
        path = path + 1j * rng.integers(-2, 3, size=path.shape) / 8
        coefficients = coefficients + 1j * rng.integers(-2, 3, size=coefficients.shape) / 8
    indices = rng.integers(0, 3, size=(5, monomial_degree))
    indices[1] = indices[0]
    groups = np.array((2, 2, 0, 2, 0))
    copies = [v.copy() for v in (path, indices, groups, coefficients)]
    actual = p.homogeneous_composition(indices, groups, coefficients, path, group_count=4)
    expected = np.zeros_like(actual)
    for row in range(5):
        for powers in product(range(path_degree + 1), repeat=monomial_degree):
            weight = 1
            for slot, power in enumerate(powers):
                weight *= path[power, indices[row, slot]]
            expected[sum(powers), groups[row]] += weight * coefficients[row]
    np.testing.assert_array_equal(actual, expected)
    np.testing.assert_array_equal(actual[:, (1, 3)], 0)
    for original, copy in zip((path, indices, groups, coefficients), copies, strict=True):
        np.testing.assert_array_equal(original, copy)


def test_empty_support_keeps_degree_shape_and_complex_dtype():
    result = p.homogeneous_composition(
        np.empty((0, 3), dtype=int),
        np.empty(0, dtype=int),
        np.empty((0, 2), dtype=complex),
        np.zeros((4, 2)),
        group_count=2,
    )
    assert result.shape == (10, 2, 2) and result.dtype == np.complex128
    assert not np.any(result)


@pytest.mark.parametrize("value", [[], 1.0, [np.nan], [np.inf], [True], ["1"], [object()]])
def test_rejects_invalid_coefficient_arrays(value):
    with pytest.raises((ValueError, TypeError)):
        p.evaluate(value, 0.1)


@pytest.mark.parametrize("order", [-1, True, 1.5, "2"])
def test_rejects_noninteger_or_negative_order(order):
    with pytest.raises(ValueError):
        p.quotient([1.0], [1.0], order=order)
    with pytest.raises(ValueError):
        p.convolve([1.0], [1.0], order=order)


@pytest.mark.parametrize(
    "operation",
    [
        lambda: p.evaluate([1.0, 2.0], [1.0]),
        lambda: p.evaluate([1e308, 1e308], 2.0),
        lambda: p.add([1e308], [1e308]),
        lambda: p.convolve([1e308], [1e308]),
        lambda: p.quotient([1e308], [1e-308], order=1),
        lambda: p.quotient([1.0], [0.0, 1.0], order=2),
        lambda: p.add(np.zeros((2, 2)), np.zeros((2, 3))),
    ],
)
def test_rejects_invalid_or_overflowing_operations(operation):
    with pytest.raises((ValueError, FloatingPointError)):
        operation()


@pytest.mark.parametrize(
    "damaged", ["path", "index_type", "index_range", "groups", "width", "count"]
)
def test_rejects_invalid_sparse_shape_index_and_group_metadata(damaged):
    args = {
        "indices": np.array(((0, 1),)),
        "groups": np.array((0,)),
        "coefficients": np.ones((1, 1)),
        "coordinate_path": np.zeros((2, 2)),
        "group_count": 1,
    }
    key, value = {
        "path": ("coordinate_path", np.zeros(3)),
        "index_type": ("indices", np.array(((0.0, 1.0),))),
        "index_range": ("indices", np.array(((0, 2),))),
        "groups": ("groups", np.array((1,))),
        "width": ("coefficients", np.ones((1, 0))),
        "count": ("group_count", True),
    }[damaged]
    args[key] = value
    with pytest.raises(ValueError):
        p.homogeneous_composition(**args)
