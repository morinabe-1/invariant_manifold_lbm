"""Real-LBM quartic forcing from complete, unmodified Taylor fibers.

This is a derivative kernel, not a fourth-order chart or an existence claim.
Only exact Fourier zeros are omitted in contractions. In particular, the
internal arguments are not restricted to the four incoming coordinates.
"""

from collections import Counter
from dataclasses import dataclass
from itertools import combinations, product
from math import comb, factorial, prod

import numpy as np

from research import d3q27 as lattice
from research import d3q27_chart as chart
from research import d3q27_cubic_chart as cubic_chart
from research import d3q27_damping as damping

TERM_NAMES = (
    "B_V_H3",
    "B_H2_H2",
    "C_V_V_H2",
    "D_V_V_V_V",
    "H2_L_G3",
    "H2_G2_G2",
    "H3_L_L_G2",
)
MUTATIONS = ("fft_degree", "streaming_sign", "filter", "G2", "G3")


def monomial_ranks(indices, dimension):
    """Lexicographic ranks of canonical pairs/triples, without a dense H3 cube."""
    ids = np.asarray(indices)
    if (
        ids.ndim != 2
        or ids.shape[1] not in (2, 3)
        or ids.dtype.kind not in "iu"
        or np.any(ids < 0)
        or np.any(ids >= dimension)
        or np.any(ids[:, :-1] > ids[:, 1:])
    ):
        raise ValueError("canonical in-range integer pairs/triples required")
    i, j = ids[:, 0], ids[:, 1]
    if ids.shape[1] == 2:
        return i * dimension - i * (i + 1) // 2 + j
    count = comb(dimension + 2, 3)
    remaining = dimension - i
    before_i = count - remaining * (remaining + 1) * (remaining + 2) // 6
    before_j = (j - i) * dimension - (i + j - 1) * (j - i) // 2
    return before_i + before_j + ids[:, 2] - j


def raw_factors(indices):
    """Multiindex factorial, not a uniform degree factorial."""
    ids = np.asarray(indices)
    if ids.shape[1] == 2:
        return 1 + (ids[:, 0] == ids[:, 1]).astype(np.int64)
    if ids.shape[1] != 3:
        raise ValueError("only lower-order pairs/triples are converted here")
    return (
        1
        + (ids[:, 0] == ids[:, 1]).astype(np.int64)
        + (ids[:, 1] == ids[:, 2]).astype(np.int64)
        + 3 * (ids[:, 0] == ids[:, 2]).astype(np.int64)
    )


class TaylorData:
    """Borrowed read-only views; the caller must retain and seal the originals.

    The complete degree-two and degree-three coordinate sets are mandatory.
    Small artificial inventories are supported for algebraic unit tests only;
    ``from_model`` requires the registered 104-coordinate real-LBM inventory.
    """

    def __init__(self, *, size, omega, eta, power, waves, basis, linear, indices, h, g):
        if type(size) is not int or size < 3 or not size % 2:
            raise ValueError("odd physical grid required")
        damping.parameters(eta, power)
        if not np.isfinite(omega) or not 0 < omega < 2:
            raise ValueError("finite BGK relaxation in (0,2) required")
        self.size, self.omega, self.eta, self.power = size, omega, eta, power
        self.waves, self.basis, self.linear = map(np.asarray, (waves, basis, linear))
        self.dimension = n = len(self.waves)
        if (
            self.waves.shape != (n, 3)
            or self.waves.dtype != np.dtype("int64")
            or self.basis.shape != (27, n)
            or self.linear.shape != (n, n)
            or n == 0
        ):
            raise ValueError("coordinate waves, population basis and linear map disagree")
        self.wave_indices = {
            tuple(w): np.flatnonzero(np.all(self.waves == w, axis=1))
            for w in np.unique(self.waves, axis=0)
        }
        widths = {len(row) for row in self.wave_indices.values()}
        if len(widths) != 1:
            raise ValueError("every selected wave must have the same reduced width")
        self.width = widths.pop()
        different = np.any(self.waves[:, None] != self.waves[None, :], axis=-1)
        if np.any(self.linear[different] != 0):
            raise ValueError("linear reduced dynamics violates exact Fourier support")
        if set(indices) != {2, 3} or set(h) != {2, 3} or set(g) != {2, 3}:
            raise ValueError("both complete Taylor degrees are required")
        self.indices, self.h, self.g, self.lookup, self.outputs = {}, {}, {}, {}, {}
        for degree in (2, 3):
            count = comb(n + degree - 1, degree)
            ids, response, reduced = map(np.asarray, (indices[degree], h[degree], g[degree]))
            if (
                ids.shape != (count, degree)
                or ids.dtype != np.dtype("int64")
                or response.shape != (count, 27)
                or reduced.shape != (count, self.width)
            ):
                raise ValueError("complete Taylor arrays with matching shapes required")
            ranks = monomial_ranks(ids, n)
            if not np.array_equal(np.sort(ranks), np.arange(count)):
                raise ValueError("duplicate or missing Taylor monomials")
            lookup = np.empty(count, dtype=np.int64)
            lookup[ranks] = np.arange(count)
            outputs = self.waves[ids].sum(axis=1)
            selected = np.array([tuple(w) in self.wave_indices for w in outputs])
            if np.any(reduced[~selected] != 0):
                raise ValueError("nonzero off-shell internal coefficient cannot be discarded")
            self.indices[degree], self.h[degree], self.g[degree] = ids, response, reduced
            self.lookup[degree], self.outputs[degree] = lookup, outputs
        for value in (self.basis, self.linear, *self.h.values(), *self.g.values()):
            if value.dtype != np.dtype("complex128") or not np.isfinite(value).all():
                raise ValueError("finite complex128 coefficients required")
        for name in ("waves", "basis", "linear"):
            view = getattr(self, name).view()
            view.setflags(write=False)
            setattr(self, name, view)
        for mapping in (self.indices, self.h, self.g, self.lookup, self.outputs):
            for degree, value in mapping.items():
                view = value.view()
                view.setflags(write=False)
                mapping[degree] = view
        self.moments = self.basis.T @ lattice.conserved_moment_matrix().T

    def check_slots(self, slots):
        ids = np.asarray(slots)
        if (
            ids.shape != (4,)
            or ids.dtype.kind not in "iu"
            or np.any(ids < 0)
            or np.any(ids >= self.dimension)
        ):
            raise ValueError("four in-range coordinate indices required")
        return tuple(map(int, ids))

    def rows(self, ids):
        ids = np.sort(np.asarray(ids, dtype=np.int64), axis=1)
        return self.lookup[ids.shape[1]][monomial_ranks(ids, self.dimension)], raw_factors(ids)

    def derivative(self, ids, *, reduced=False):
        ids = tuple(ids)
        row, factor = self.rows([ids])
        values = self.g if reduced else self.h
        return factor[0] * values[len(ids)][row[0]]

    def internal(self, ids):
        wave = tuple(self.waves[list(ids)].sum(axis=0))
        indices = self.wave_indices.get(wave, np.empty(0, dtype=np.int64))
        value = self.derivative(ids, reduced=True)
        if not len(indices):
            if np.any(value != 0):
                raise ValueError("unexpected off-shell reduced forcing")
            return indices, np.empty(0, dtype=complex)
        active = value != 0
        return indices[active], value[active]

    def linear_argument(self, coordinate):
        values = self.linear[:, coordinate]
        active = np.flatnonzero(values != 0)
        return active, values[active]

    def contract(self, arguments):
        if any(len(indices) == 0 for indices, _ in arguments):
            return np.zeros(27, dtype=complex)
        positions = np.array(list(product(*(range(len(ids)) for ids, _ in arguments))))
        ids = np.column_stack([arg[0][positions[:, k]] for k, arg in enumerate(arguments)])
        weights = np.prod(
            np.column_stack([arg[1][positions[:, k]] for k, arg in enumerate(arguments)]), axis=1
        )
        rows, factors = self.rows(ids)
        return (weights * factors) @ self.h[len(arguments)][rows]


def from_model(model, arrays):
    cubic_chart.validate_fibers(arrays)
    if (
        model.size not in (17, 33, 65)
        or (model.omega, model.eta, model.power) != (1.5, 0.02, 2)
        or model.complex_linear.shape != (104, 104)
        or not np.array_equal(
            model.output_waves, np.asarray(chart.WAVES)[model.input_pairs // 4].sum(axis=1)
        )
    ):
        raise ValueError("registered full real-LBM quadratic input required")
    return TaylorData(
        size=model.size,
        omega=model.omega,
        eta=model.eta,
        power=model.power,
        waves=np.repeat(np.asarray(chart.WAVES, dtype=np.int64), 4, axis=0),
        basis=np.column_stack([model.frames[w].basis for w in chart.WAVES]),
        linear=model.complex_linear,
        indices={2: model.input_pairs, 3: arrays["input_triples"]},
        h={2: model.hessian_fibers, 3: arrays["response"]},
        g={2: model.reduced_fibers, 3: arrays["reduced"]},
    )


def local_b(u, v):
    """B0 of population moments (rho,jx,jy,jz), complex bilinear, not Hermitian."""
    return lattice.WEIGHTS * (
        9 * (lattice.VELOCITIES @ u[1:]) * (lattice.VELOCITIES @ v[1:]) - 3 * np.dot(u[1:], v[1:])
    )


def local_c(u, v, w):
    return -u[0] * local_b(v, w) - v[0] * local_b(u, w) - w[0] * local_b(u, v)


def local_d(arguments):
    result = np.zeros(27, dtype=complex)
    for pair in combinations(range(4), 2):
        other = [i for i in range(4) if i not in pair]
        result += (
            2
            * arguments[pair[0]][0]
            * arguments[pair[1]][0]
            * local_b(arguments[other[0]], arguments[other[1]])
        )
    return result


def raw_terms(data, slots, *, mutation=None):
    """Seven positive-sign groups; F4 = sum(first four) - sum(last three)."""
    slots = data.check_slots(slots)
    if mutation is not None and mutation not in MUTATIONS:
        raise ValueError("unknown forcing mutation")
    moments = lattice.conserved_moment_matrix()
    v = data.moments[list(slots)]
    linear = [data.linear_argument(i) for i in slots]
    result = np.zeros((7, 27), dtype=complex)
    for single in range(4):
        rest = tuple(slots[i] for i in range(4) if i != single)
        result[0] += local_b(v[single], moments @ data.derivative(rest))
        if mutation != "G3":
            result[4] += data.contract((linear[single], data.internal(rest)))
    for partner in (1, 2, 3):
        left = (slots[0], slots[partner])
        right = tuple(slots[i] for i in range(1, 4) if i != partner)
        result[1] += local_b(moments @ data.derivative(left), moments @ data.derivative(right))
        if mutation != "G2":
            result[5] += data.contract((data.internal(left), data.internal(right)))
    for pair in combinations(range(4), 2):
        other = [i for i in range(4) if i not in pair]
        ids = tuple(slots[i] for i in pair)
        result[2] += local_c(v[other[0]], v[other[1]], moments @ data.derivative(ids))
        if mutation != "G2":
            result[6] += data.contract((linear[other[0]], linear[other[1]], data.internal(ids)))
    result[3] = local_d(v)
    factors = (
        np.ones(4)
        if mutation == "fft_degree"
        else np.array([data.size**-1.5, data.size**-1.5, data.size**-3, data.size**-4.5])
    )
    wave = data.waves[list(slots)].sum(axis=0)
    sign = 1 if mutation == "streaming_sign" else -1
    phase = np.exp(sign * 2j * np.pi * (lattice.VELOCITIES @ wave) / data.size)
    multiplier = (
        1
        if mutation == "filter"
        else damping.wave_multiplier(tuple(wave), data.size, data.eta, data.power)
    )
    result[:4] *= data.omega * multiplier * factors[:, None] * phase
    if not np.isfinite(result).all():
        raise ValueError("nonfinite quartic terms")
    return result


@dataclass
class Product:
    groups: tuple
    keys: tuple
    rows: tuple
    basis: np.ndarray
    factors: np.ndarray
    full_dynamics: np.ndarray
    dynamics: np.ndarray


def block_product(data, groups, block_indices):
    groups = tuple(groups)
    if len(groups) != 4 or any(
        type(b) is not int or not 0 <= b < len(block_indices) for b in groups
    ):
        raise ValueError("four valid block labels required")
    block_indices = tuple(tuple(map(int, ids)) for ids in block_indices)
    flat = [i for block in block_indices for i in block]
    if sorted(flat) != list(range(data.dimension)) or any(not ids for ids in block_indices):
        raise ValueError("blocks must partition all coordinates exactly once")
    labels = np.empty(data.dimension, dtype=np.int64)
    for b, ids in enumerate(block_indices):
        labels[list(ids)] = b
    if np.any(data.linear[labels[:, None] != labels[None, :]] != 0):
        raise ValueError("linear map exchanges distinct input blocks")
    rows = tuple(
        tuple(reversed(row)) for row in product(*(block_indices[b] for b in reversed(groups)))
    )
    orbits = {}
    for row, ids in enumerate(rows):
        orbits.setdefault(tuple(sorted(ids)), []).append(row)
    keys = tuple(sorted(orbits))
    basis = np.zeros((len(rows), len(keys)))
    multiplicities = np.array([len(orbits[key]) for key in keys])
    for column, key in enumerate(keys):
        basis[orbits[key], column] = 1 / np.sqrt(len(orbits[key]))
    full = np.ones((1, 1), dtype=complex)
    for b in groups:
        ids = block_indices[b]
        full = np.kron(data.linear[np.ix_(ids, ids)], full)
    denominator = prod(factorial(n) for n in Counter(groups).values())
    return Product(
        groups,
        keys,
        rows,
        basis,
        np.sqrt(multiplicities) / denominator,
        full,
        basis.T @ full @ basis,
    )


def group_terms(data, value, *, mutation=None):
    cache = {key: raw_terms(data, key, mutation=mutation) for key in value.keys}
    full = np.stack([cache[tuple(sorted(ids))] for ids in value.rows], axis=-1)
    return full @ value.basis


def forcing(terms):
    return terms[:4].sum(axis=0) - terms[4:].sum(axis=0)
