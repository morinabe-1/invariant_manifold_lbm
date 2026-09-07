"""Exact proof checks for the explanatory table; not Q012g3 campaign controls."""

from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
from itertools import product
from math import prod
from pathlib import Path

import pytest

DOC = Path(__file__).resolve().parents[1] / "docs" / "D3Q27_COMPOSITION_IDENTITY.md"
ORDERS = {"f": 0, "V": 1, "B": 2, "T": 3}
TABLE = {
    0: {("f", ()): 1},
    1: {("V", (1,)): 1},
    2: {("V", (2,)): 1, ("B", (1, 1)): 1},
    3: {("V", (3,)): 1, ("B", (1, 2)): 2, ("T", (1, 1, 1)): 1},
    4: {("B", (1, 3)): 2, ("B", (2, 2)): 1, ("T", (1, 1, 2)): 3},
    5: {("B", (2, 3)): 2, ("T", (1, 1, 3)): 3, ("T", (1, 2, 2)): 3},
    6: {("B", (3, 3)): 1, ("T", (1, 2, 3)): 6, ("T", (2, 2, 2)): 1},
    7: {("T", (1, 3, 3)): 3, ("T", (2, 2, 3)): 3},
    8: {("T", (2, 3, 3)): 3},
    9: {("T", (3, 3, 3)): 1},
}


def restrict_table(chart_degree, path_degree):
    return {
        n: {
            (family, indices): factor
            for (family, indices), factor in terms.items()
            if ORDERS[family] <= chart_degree and all(i <= path_degree for i in indices)
        }
        for n, terms in TABLE.items()
    }


def enumerate_symbols(chart_degree, path_degree):
    result = {n: Counter() for n in range(10)}
    result[0][("f", ())] = 1
    for family, order in ORDERS.items():
        if not 1 <= order <= chart_degree:
            continue
        for indices in product(range(1, path_degree + 1), repeat=order):
            result[sum(indices)][(family, tuple(sorted(indices)))] += 1
    return {n: dict(terms) for n, terms in result.items()}


def test_all_twenty_symbolic_terms_and_forty_ordered_contributions():
    assert TABLE == enumerate_symbols(3, 3)
    assert sum(len(terms) for terms in TABLE.values()) == 20
    assert sum(sum(terms.values()) for terms in TABLE.values()) == 40


def test_document_table_matches_the_verified_symbolic_identity():
    document = DOC.read_text(encoding="utf-8")
    for n, terms in TABLE.items():
        names = []
        for (family, indices), factor in terms.items():
            name = "f*" if family == "f" else family + "".join(map(str, indices))
            names.append(name if factor == 1 else f"{factor} {name}")
        row = f"| {n} | `{' + '.join(names)}` |"
        assert document.count(row) == 1


@pytest.mark.parametrize("chart_degree,path_degree", [(2, 2), (2, 3), (3, 2)])
def test_zero_cubic_terms_and_highest_degree_are_not_silently_discarded(chart_degree, path_degree):
    result = restrict_table(chart_degree, path_degree)
    assert result == enumerate_symbols(chart_degree, path_degree)
    assert max(n for n, terms in result.items() if terms) == chart_degree * path_degree
    if chart_degree == 3 and path_degree == 2:
        assert result[6] == {("T", (2, 2, 2)): 1}
    if chart_degree == path_degree == 2:
        assert result[4] == {("B", (2, 2)): 1}


def tensor_entry(output, indices):
    """Signed, symmetric, non-diagonal rational tensors with two outputs."""
    return F(
        (-1) ** (output + sum(indices)) * (prod(i + 1 for i in indices) + output + len(indices)),
        (sum(indices) + len(indices) + 2) * (output + 2),
    )


def contraction(output, vectors):
    dimension = len(vectors[0])
    return sum(
        (
            tensor_entry(output, indices)
            * prod(v[i] for v, i in zip(vectors, indices, strict=True))
            for indices in product(range(dimension), repeat=len(vectors))
        ),
        F(0),
    )


def exact_table_coefficients(base, path, chart_degree):
    coefficients = [[F(0), F(0)] for _ in range(10)]
    for n, terms in restrict_table(chart_degree, len(path)).items():
        for (family, indices), factor in terms.items():
            for output in range(2):
                value = (
                    base[output]
                    if family == "f"
                    else contraction(output, [path[i - 1] for i in indices])
                )
                coefficients[n][output] += factor * value
    return coefficients


def multiply(a, b):
    result = [F(0) for _ in range(len(a) + len(b) - 1)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


def component_composition(base, path, chart_degree):
    """Independent coordinate-polynomial products, without the grouped table."""
    dimension = len(path[0])
    coefficients = [[F(0), F(0)] for _ in range(10)]
    coefficients[0] = list(base)
    for output in range(2):
        for order in range(1, chart_degree + 1):
            for indices in product(range(dimension), repeat=order):
                polynomial = [F(1)]
                for index in indices:
                    polynomial = multiply(polynomial, [F(0), *(v[index] for v in path)])
                for n, value in enumerate(polynomial):
                    coefficients[n][output] += tensor_entry(output, indices) * value
    return coefficients


@pytest.mark.parametrize("dimension", [2, 3])
@pytest.mark.parametrize("chart_degree,path_degree", [(2, 2), (2, 3), (3, 2), (3, 3)])
def test_all_coefficients_and_direct_values_with_exact_rational_arithmetic(
    dimension, chart_degree, path_degree
):
    base = [F(2, 7), F(-3, 11)]
    path = [
        [F((-1) ** (i + p) * ((i + 1) ** p + p), i + p + 1) for i in range(dimension)]
        for p in range(1, path_degree + 1)
    ]
    coefficients = exact_table_coefficients(base, path, chart_degree)
    assert coefficients == component_composition(base, path, chart_degree)
    for parameter in (F(0), F(-2, 9), F(1, 7)):
        coordinate = [
            sum((parameter**p * v[i] for p, v in enumerate(path, 1)), F(0))
            for i in range(dimension)
        ]
        for output in range(2):
            direct = base[output] + sum(
                (contraction(output, [coordinate] * order) for order in range(1, chart_degree + 1)),
                F(0),
            )
            assert (
                sum((parameter**n * c[output] for n, c in enumerate(coefficients)), F(0)) == direct
            )


@pytest.mark.parametrize(
    "degree,symbol,wrong_factor",
    [
        (3, ("B", (1, 2)), 1),
        (4, ("T", (1, 1, 2)), 1),
        (6, ("T", (1, 2, 3)), 3),
        (9, ("T", (3, 3, 3)), F(1, 6)),
    ],
)
def test_missing_permutations_and_a_second_factorial_fail_the_identity(
    degree, symbol, wrong_factor
):
    wrong = deepcopy(TABLE)
    wrong[degree][symbol] = wrong_factor
    assert wrong != enumerate_symbols(3, 3)
