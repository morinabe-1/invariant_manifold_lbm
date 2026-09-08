"""Independent full-coefficient controls for Q012h1, before its formal runner."""

from itertools import combinations_with_replacement

import numpy as np
import pytest

from research import d3q27_quartic_fraction as f
from research import d3q27_quartic_jets as j
from research import d3q27_quartic_operator as q


def test_fraction_polynomial_products_substitution_and_truncation():
    x, y = {(0,): f.ONE}, {(1,): f.ONE}
    p = f.add(x, f.scale(y, f.IMAG))
    square = f.mul(p, p)
    assert square == {(0, 0): f.ONE, (0, 1): (f.Fraction(0), f.Fraction(2)), (1, 1): f.real(-1)}
    assert f.substitute((square,), (y, x)) == (
        {(1, 1): f.ONE, (0, 1): (f.Fraction(0), f.Fraction(2)), (0, 0): f.real(-1)},
    )
    fourth = f.mul(square, square)
    assert set(map(len, fourth)) == {4}
    assert f.mul(fourth, x) == {}
    assert f.add(fourth, f.scale(fourth, f.real(-1))) == {}
    assert f.record(f.real(6, 8)) == ["3", "4", "0", "1"]


@pytest.fixture(scope="module", params=[(p, r) for p in (23, 27) for r in ("real", "complex")])
def compared(request):
    p, representation = request.param
    main = j.Manufactured(p, representation)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(j, "Manufactured", lambda *args: pytest.fail("reference used main recipe"))
        patch.setattr(j, "Jet", lambda *args: pytest.fail("reference used main mixed derivatives"))
        patch.setattr(
            q, "build_product", lambda *args: pytest.fail("reference used symmetric product")
        )
        patch.setattr(np, "kron", lambda *args: pytest.fail("reference used Kronecker product"))
        reference = f.manufactured(p, representation)
    return main, reference


def test_reference_recipe_bases_and_full_graph_identity(compared):
    main, reference = compared
    assert reference["known_graph_identity"] and reference["full_coefficient_realification"]
    assert reference["external_dimension"] == main.external
    assert reference["representation"] == main.representation
    for name in ("transform", "inverse"):
        assert [[v.record() for v in row] for row in getattr(main, name)] == [
            [f.record(v) for v in row] for row in reference[name]
        ]


def test_all_lower_and_fourth_known_coefficients_match(compared):
    main, reference = compared
    for degree in (2, 3, 4):
        expected_keys = tuple(combinations_with_replacement(range(8), degree))
        for name, evaluate in (("h", main.h), ("g", main.g)):
            keys, values = reference["known"][degree][name]
            assert keys == expected_keys
            for key, value in zip(keys, values, strict=True):
                direct = evaluate(tuple(main.units[i] for i in key))
                assert [v.record() for v in direct] == [f.record(v) for v in value], (name, key)


def test_every_forcing_column_matches_independent_composition(compared):
    main, reference = compared
    keys, values = reference["forcing"]
    assert keys == tuple(combinations_with_replacement(range(8), 4)) and len(keys) == 330
    nonzero_groups, conjugate_mutations = set(), set()
    omitted_reduced = {"G2": False, "G3": False}
    for key, expected in zip(keys, values, strict=True):
        groups = main.forcing_groups(key)
        actual = j.add(*groups.values())
        expected_records = [f.record(v) for v in expected]
        assert [v.record() for v in actual] == expected_records, key
        assert len(actual) == 8 + main.external + 4
        assert not any(actual[-4:])
        for name, group in groups.items():
            if any(group):
                nonzero_groups.add(name)
                mutant = j.add(actual, j.scale(group, -1))
                assert [v.record() for v in mutant] != expected_records
            if any(v.imag for v in group):
                conjugate_mutations.add(name)
                mutant = j.add(actual, j.scale(group, -1), tuple(v.conjugate() for v in group))
                assert [v.record() for v in mutant] != expected_records
        composition = j.add(*(v for name, v in groups.items() if name.startswith("minus_")))
        if any(composition):
            assert [v.record() for v in j.add(actual, j.scale(composition, -2))] != expected_records
        for label, names in (
            ("G2", ("minus_H2_G2_G2", "minus_H3_L_L_G2")),
            ("G3", ("minus_H2_L_G3",)),
        ):
            removed = j.add(*(groups[name] for name in names))
            if any(removed):
                omitted_reduced[label] = True
                mutant = j.add(actual, j.scale(removed, -1))
                assert [v.record() for v in mutant] != expected_records
    assert len(nonzero_groups) == 7
    assert all(omitted_reduced.values())
    if main.representation == "complex":
        assert len(conjugate_mutations) == 7


@pytest.mark.parametrize(
    "external,representation", ((4, "real"), (23.0, "real"), (True, "complex"), (27, "invalid"))
)
def test_unregistered_fraction_recipe_is_rejected(external, representation):
    with pytest.raises(ValueError):
        f.manufactured(external, representation)
