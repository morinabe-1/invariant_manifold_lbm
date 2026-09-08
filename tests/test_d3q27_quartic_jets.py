"""Exact main-route controls; independent worker and saved audit remain required."""

from itertools import combinations_with_replacement
from math import factorial

import pytest
from gmpy2 import mpq

from research import d3q27_quartic_jets as j


def test_gaussian_arithmetic_and_lossless_records():
    x, y = j.Gaussian(mpq(1, 3), mpq(2, 5)), j.Gaussian(mpq(-7, 4), mpq(3, 8))
    assert (x * y) / y == x
    assert x + (-x) == j.ZERO
    assert x.conjugate().conjugate() == x
    assert x * x.conjugate() == j.Gaussian(mpq(1, 9) + mpq(4, 25))
    assert x.record() == ["1", "3", "2", "5"]
    assert not j.ZERO and j.ONE
    with pytest.raises(ZeroDivisionError):
        x / j.ZERO
    # Complex multilinear products do not use an inner-product conjugation.
    assert x * y != x * y.conjugate()


@pytest.mark.parametrize("order", (1, 2, 3, 4))
def test_labeled_jet_mixed_derivative_and_factorials(order):
    coefficients = tuple(j.Gaussian(mpq(i + 1, 7), mpq(-i, 5)) for i in range(order))
    linear = j.Jet.linear(coefficients)
    powered = linear
    for _ in range(order - 1):
        powered = powered * linear
    assert powered.coefficient() == factorial(order) * j.multiply(coefficients)
    expected = j.ZERO if order == 1 else j.multiply(coefficients)
    assert j.tail(linear).coefficient() == expected


def test_labeled_jet_rejects_order_mismatch_and_has_nilpotent_slots():
    one = j.Jet.linear((j.ONE,))
    assert (one * one).coefficient() == j.ZERO
    with pytest.raises(ValueError):
        one * j.Jet.linear((j.ONE, j.ONE))
    with pytest.raises(ValueError):
        j.Jet(0, [j.ONE])
    with pytest.raises(ValueError):
        j.Jet(2, [j.ONE])


@pytest.fixture(scope="module", params=[(p, r) for p in (23, 27) for r in ("real", "complex")])
def model(request):
    return j.Manufactured(*request.param)


def test_linear_map_and_biorthogonal_frame_exactly(model):
    for i, unit in enumerate(model.units):
        assert j.matvec(model.inverse, j.matvec(model.transform, unit)) == unit
        derivative = model.phi_derivative((model.vectors[i],))
        assert derivative == (
            *j.matvec(model.transform, model.linear_units[i]),
            *((j.ZERO,) * (model.external + 4)),
        )
        if model.representation == "complex":
            b = i // 2
            eigenvalue = j.Gaussian(mpq(3, 5) + mpq(b, 40), mpq((b + 1) * (-1) ** i, 40))
            assert model.linear_units[i] == j.scale(unit, eigenvalue)
    for i in range(4):
        conserved = [j.ZERO] * model.width
        conserved[-4 + i] = j.ONE
        assert model.phi_derivative((tuple(conserved),)) == tuple(conserved)


def test_every_fourth_monomial_satisfies_known_homological_identity(model):
    nonzero = None
    for key in combinations_with_replacement(range(8), 4):
        terms = model.forcing_groups(key)
        actual = j.add(*terms.values())
        response, reduced, expected = model.known_identity(key)
        assert actual == expected, (model.external, model.representation, key)
        assert j.matvec(model.inverse, actual[:8]) == reduced
        assert all(value == j.ZERO for value in actual[-4:] + response[-4:])
        if nonzero is None:
            nonzero = dict.fromkeys(terms, 0)
        for name, values in terms.items():
            if any(values):
                nonzero[name] += 1
                # Exact nonzero coefficients make omission of this group visible.
                assert j.add(actual, j.scale(values, -1)) != expected
    assert len(nonzero) == 7 and all(count > 0 for count in nonzero.values())


def test_map_derivatives_are_complex_multilinear_not_hermitian(model):
    for degree in (2, 3, 4):
        directions = model.vectors[:degree]
        expected = j.scale(model.phi_derivative(directions), j.IMAG)
        for slot in range(degree):
            altered = list(directions)
            altered[slot] = j.scale(altered[slot], j.IMAG)
            assert model.phi_derivative(altered) == expected


def test_known_coefficients_have_exact_conjugate_structure(model):
    for degree in (2, 3, 4):
        for key in combinations_with_replacement(range(8), degree):
            directions = tuple(model.units[i] for i in key)
            h, g = model.h(directions), model.g(directions)
            assert all(value == j.ZERO for value in h[:8] + h[-4:])
            if model.representation == "real":
                assert not any(value.imag for value in h + g)
            else:
                partner = tuple(model.units[i ^ 1] for i in key)
                assert model.h(partner) == tuple(value.conjugate() for value in h)
                pg = model.g(partner)
                assert tuple(pg[i ^ 1] for i in range(8)) == tuple(value.conjugate() for value in g)


@pytest.mark.parametrize("key", ((0, 1, 2), (0, 1, 3, 2), (0, 1, 2, 8), (0, 1, 2, True)))
def test_invalid_fourth_monomial_is_rejected(model, key):
    with pytest.raises(ValueError):
        model.forcing_groups(key)


@pytest.mark.parametrize(
    "p,representation", ((4, "real"), (23.0, "real"), (True, "real"), (23, "unknown"))
)
def test_unregistered_recipe_is_rejected(p, representation):
    with pytest.raises(ValueError):
        j.Manufactured(p, representation)
