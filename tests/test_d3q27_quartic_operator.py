"""Implementation controls, not the complete Q012h1 scientific decision."""

from collections import Counter
from itertools import product
from math import comb, factorial

import numpy as np
import pytest

from research import d3q27_quartic_operator as q
from research import d3q27_quartic_reference as ref


@pytest.mark.parametrize("dimensions", tuple(product((1, 2), repeat=4)))
def test_full_inventory_against_fraction_substitution(dimensions):
    count, patterns, column_sizes = 0, set(), set()
    for groups in q.GROUPS:
        value, reference = q.build_product(dimensions, groups), ref.substitute(dimensions, groups)
        assert value.keys == reference["keys"]
        assert tuple(value.multiplicities) == reference["multiplicities"]
        np.testing.assert_allclose(value.dynamics, reference["normalized"], atol=5e-13, rtol=5e-13)
        assert q.structural_audit(value)["passed"]
        assert (
            len(q.structural_audit(value, permutations_required=False)["slot_permutation_errors"])
            == 0
        )
        # For a raw symmetric derivative equal to one, S restriction gives
        # sqrt(orbit size); the fiber factor must produce 1 / multiindex!.
        np.testing.assert_allclose(
            np.ones(len(value.full_coordinates)) @ value.basis * value.factors,
            [1 / n for n in reference["taylor_denominators"]],
            atol=5e-15,
            rtol=5e-15,
        )
        count += len(value.keys)
        patterns.add(tuple(sorted(Counter(groups).values(), reverse=True)))
        column_sizes.add(len(value.keys))
    assert len(q.GROUPS) == 35
    assert count == comb(sum(dimensions) + 3, 4)
    assert patterns == {(4,), (3, 1), (2, 2), (2, 1, 1), (1, 1, 1, 1)}
    if dimensions == (2, 2, 2, 2):
        assert column_sizes == {5, 8, 9, 12, 16}


def test_total_registered_operator_and_column_counts():
    values = [q.build_product(dims, groups) for dims in q.DIMENSIONS for groups in q.GROUPS]
    assert 2 * len(values) == 1120
    assert 2 * sum(len(v.keys) for v in values) == 4482
    assert {len(v.keys) for v in values} == {1, 2, 3, 4, 5, 6, 8, 9, 12, 16}
    assert max(p * len(v.keys) for p in q.EXTERNAL_DIMENSIONS for v in values) == 432


@pytest.mark.parametrize("block", range(4))
@pytest.mark.parametrize("dimension", (1, 2))
def test_block_recipe_stability_and_nonnormality(block, dimension):
    observed = q.dynamics(block, dimension)
    expected = np.array(ref.matrix(block, dimension), dtype=complex)
    np.testing.assert_allclose(observed, expected, atol=1e-15, rtol=1e-15)
    assert np.max(np.abs(np.linalg.eigvals(observed))) < 1
    if dimension == 2:
        assert np.linalg.norm(observed.conj().T @ observed - observed @ observed.conj().T) > 0
        eigenvalues = np.linalg.eigvals(observed)
        np.testing.assert_allclose(eigenvalues[0], eigenvalues[1].conjugate(), atol=1e-14)


@pytest.mark.parametrize(
    "dimensions,groups",
    (
        ((2, 2, 2), (0, 1, 2, 3)),
        ((2, 2, 2, 0), (0, 1, 2, 3)),
        ((2, 2, 2, 3), (0, 1, 2, 3)),
        ((2, 2, 2, True), (0, 1, 2, 3)),
        ((2, 2, 2, 1.0), (0, 1, 2, 3)),
        ((2, 2, 2, 1), (0, 1, 2)),
        ((2, 2, 2, 1), (0, 1, 2, 4)),
        ((2, 2, 2, 1), (0, 1, 2, -1)),
        ((2, 2, 2, 1), (0, 1, 2, True)),
        ((2, 2, 2, 1), (0, 1, 2, 1.0)),
    ),
)
def test_invalid_inventory_is_rejected_by_both_routes(dimensions, groups):
    with pytest.raises(ValueError):
        q.build_product(dimensions, groups)
    with pytest.raises(ValueError):
        ref.substitute(dimensions, groups)


def test_single_pass_inventory_and_reference_independence(monkeypatch):
    expected = ref.substitute((2, 1, 2, 1), (0, 0, 1, 2))
    monkeypatch.setattr(q, "build_product", lambda *args: pytest.fail("reference used primary"))
    monkeypatch.setattr(np, "kron", lambda *args: pytest.fail("reference used Kronecker product"))
    actual = ref.substitute(iter((2, 1, 2, 1)), iter((0, 0, 1, 2)))
    assert actual == expected


def test_first_input_index_fastest_and_nonuniform_taylor_factors():
    value = q.build_product((2, 2, 2, 2), (0, 1, 2, 3))
    assert value.full_coordinates[:3] == ((0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0))
    assert np.all(value.factors == 1)
    assert not np.allclose(value.factors, 1 / factorial(4))
    repeated = q.build_product((2, 2, 2, 2), (0, 0, 0, 0))
    assert len(set(repeated.factors)) > 1


@pytest.mark.parametrize("external", (23, 27))
def test_known_problem_shape_and_equation(external):
    value, a, forcing, known = q.known_problem((2, 2, 2, 2), (0, 1, 2, 3), external)
    assert a.shape == (external, external) and forcing.shape == known.shape == (external, 16)
    np.testing.assert_allclose(a @ known - known @ value.dynamics + forcing, 0, atol=1e-15)
    assert np.all(np.real(np.linalg.eigvals(a)) < 0)


@pytest.mark.parametrize("dimension", (0, 23.0, True, 4, 26, 28))
def test_unregistered_external_dimension_is_rejected(dimension):
    with pytest.raises(ValueError):
        q.external_dynamics(dimension)
