"""Independent Fraction monomial substitution for the Q012h1 input products.

No imports from the numerical product, orbit-basis or Kronecker implementations.
The reference uses global coordinate monomials and exact coefficient expansion.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement
from math import factorial, prod, sqrt
from numbers import Integral


def matrix(block, dimension):
    if type(block) is not int or block not in range(4) or type(dimension) is not int:
        raise ValueError("registered integer block label/dimension required")
    a, rate, shear = Fraction(3, 5) + Fraction(block, 40), Fraction(block + 1, 40), block + 1
    if dimension == 1:
        return ((a,),)
    if dimension != 2:
        raise ValueError("dimension must be one or two")
    # Explicit multiplication of S J S^-1, independent of matrix inversion.
    return ((a + shear * rate, -(shear * shear + 1) * rate), (rate, a - shear * rate))


def substitute(dimensions, groups):
    dimensions, groups = tuple(dimensions), tuple(groups)
    if len(dimensions) != 4 or any(
        not isinstance(v, Integral) or isinstance(v, bool) or v not in (1, 2) for v in dimensions
    ):
        raise ValueError("four integer dimensions from one or two required")
    if len(groups) != 4 or any(
        not isinstance(v, Integral) or isinstance(v, bool) or v < 0 or v > 3 for v in groups
    ):
        raise ValueError("four registered integer block indices required")
    dimensions, groups = tuple(map(int, dimensions)), tuple(map(int, groups))
    coordinate_blocks, coordinates = [], []
    offset = 0
    for block, size in enumerate(dimensions):
        local = matrix(block, size)
        for i in range(size):
            coordinate_blocks.append(block)
            coordinates.append({offset + j: v for j, v in enumerate(local[i]) if v})
        offset += size
    expected_counts = Counter(groups)
    keys = tuple(
        key
        for key in combinations_with_replacement(range(offset), 4)
        if Counter(coordinate_blocks[i] for i in key) == expected_counts
    )
    key_set = set(keys)
    coefficient_rows = []
    for key in keys:
        polynomial = {(): Fraction(1)}
        for index in key:
            updated = {}
            for monomial, coefficient in polynomial.items():
                for column, entry in coordinates[index].items():
                    target = tuple(sorted((*monomial, column)))
                    updated[target] = updated.get(target, Fraction(0)) + coefficient * entry
            polynomial = {k: v for k, v in updated.items() if v}
        if not set(polynomial) <= key_set:
            raise ValueError("linear substitution escaped its repeated-block space")
        coefficient_rows.append(tuple(polynomial.get(column, Fraction(0)) for column in keys))
    block_factorial = prod(factorial(n) for n in expected_counts.values())
    coordinate_factorials = [prod(factorial(n) for n in Counter(key).values()) for key in keys]
    multiplicities = [block_factorial // denominator for denominator in coordinate_factorials]
    normalized = [
        [float(entry) * sqrt(multiplicities[i] / multiplicities[j]) for j, entry in enumerate(row)]
        for i, row in enumerate(coefficient_rows)
    ]
    return {
        "keys": keys,
        "coefficients": tuple(coefficient_rows),
        "multiplicities": tuple(multiplicities),
        "taylor_denominators": tuple(coordinate_factorials),
        "normalized": normalized,
    }
