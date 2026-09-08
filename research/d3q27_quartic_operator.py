"""Q012h1 numerical quartic products; no change to frozen scientific sources.

Raw product rows have the first input slot fastest. Symmetric columns are
ordered by sorted global coordinate tuples, not by arbitrary eigensolver labels.
"""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement, permutations, product
from math import factorial, prod
from numbers import Integral

import numpy as np

DIMENSIONS = tuple(product((1, 2), repeat=4))
GROUPS = tuple(combinations_with_replacement(range(4), 4))
EXTERNAL_DIMENSIONS = (23, 27)


def validate(dimensions, groups):
    dimensions, groups = tuple(dimensions), tuple(groups)
    if len(dimensions) != 4 or any(
        not isinstance(s, Integral) or isinstance(s, bool) or s not in (1, 2) for s in dimensions
    ):
        raise ValueError("four dimensions from {1,2} required")
    if len(groups) != 4 or any(
        not isinstance(b, Integral) or isinstance(b, bool) or b not in range(4) for b in groups
    ):
        raise ValueError("four block labels from {0,1,2,3} required")
    return tuple(map(int, dimensions)), tuple(map(int, groups))


def dynamics(block, dimension):
    validate((dimension,) * 4, (block,) * 4)
    a = 3 / 5 + block / 40
    if dimension == 1:
        return np.array([[a]], dtype=complex)
    shear = np.array([[1, block + 1], [0, 1]], dtype=complex)
    rotation = np.array([[a, -(block + 1) / 40], [(block + 1) / 40, a]], dtype=complex)
    return shear @ rotation @ np.linalg.inv(shear)


@dataclass
class Product:
    dimensions: tuple
    groups: tuple
    full_coordinates: tuple
    keys: tuple
    basis: np.ndarray
    multiplicities: np.ndarray
    factors: np.ndarray
    full_dynamics: np.ndarray
    dynamics: np.ndarray


def build_product(dimensions, groups):
    dimensions, groups = validate(dimensions, groups)
    offsets = np.cumsum((0, *dimensions[:-1])).tolist()
    rows = tuple(
        tuple(reversed(values))
        for values in product(*(range(dimensions[b]) for b in reversed(groups)))
    )
    orbits = {}
    for index, row in enumerate(rows):
        key = tuple(sorted(offsets[b] + i for b, i in zip(groups, row, strict=True)))
        orbits.setdefault(key, []).append(index)
    keys = tuple(sorted(orbits))
    multiplicities = np.array([len(orbits[key]) for key in keys], dtype=np.int64)
    basis = np.zeros((len(rows), len(keys)))
    for column, key in enumerate(keys):
        basis[orbits[key], column] = 1 / np.sqrt(len(orbits[key]))
    denominator = prod(factorial(m) for m in Counter(groups).values())
    factors = np.sqrt(multiplicities) / denominator
    full = np.ones((1, 1), dtype=complex)
    for block in groups:
        full = np.kron(dynamics(block, dimensions[block]), full)
    restricted = basis.T @ full @ basis
    return Product(dimensions, groups, rows, keys, basis, multiplicities, factors, full, restricted)


def structural_audit(value, *, permutations_required=True):
    basis, restricted = value.basis, value.dynamics
    orthogonality = float(np.linalg.norm(basis.T @ basis - np.eye(len(value.keys))))
    invariance = float(np.linalg.norm(value.full_dynamics @ basis - basis @ restricted))
    permutation_errors = []
    if permutations_required:
        for perm in permutations(range(4)):
            other = build_product(value.dimensions, tuple(value.groups[i] for i in perm))
            if other.keys != value.keys:
                raise ValueError("slot permutation changed coordinate coverage")
            permutation_errors.append(float(np.linalg.norm(restricted - other.dynamics)))
    return {
        "orthogonality_error": orthogonality,
        "invariance_error": invariance,
        "slot_permutation_errors": permutation_errors,
        "passed": max([orthogonality, invariance, *permutation_errors]) <= 5e-12,
    }


def external_dynamics(dimension):
    if type(dimension) is not int or dimension not in EXTERNAL_DIMENSIONS:
        raise ValueError("registered external dimension must be 23 or 27")
    diagonal = 1 / 5 + np.arange(dimension) / (10 * dimension)
    return (-np.diag(diagonal) + np.diag(np.full(dimension - 1, 1 / 100), 1)).astype(complex)


def known_problem(dimensions, groups, external):
    value = build_product(dimensions, groups)
    output = external_dynamics(external)
    known = (np.arange(external)[:, None] + 1) / 32 + 1j * (
        np.arange(len(value.keys))[None, :] + 1
    ) / 32
    forcing = known @ value.dynamics - output @ known
    return value, output, forcing, known
