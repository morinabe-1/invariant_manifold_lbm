"""GMP seven-group real-LBM F4 and the preregistered moment-only arm.

No lower-order solves, averaging or zero projection. Caches are owned by one
tuple/precision; all original Taylor coefficients remain the complete input.
"""

from collections import Counter
from itertools import combinations, product
from math import factorial, prod

import gmpy2 as mp
import numpy as np

from research import d3q27 as lattice
from research import d3q27_damping as damping
from research import d3q27_quartic_lbm as previous
from research import d3q27_quartic_mp_numbers as numbers

VELOCITIES = tuple(tuple(map(int, row)) for row in lattice.VELOCITIES)


def zero(width=27):
    return np.full(width, mp.mpc(0), dtype=object)


def moments(population):
    return np.array(
        [
            sum(population, mp.mpc(0)),
            *[
                sum(
                    (row[axis] * z for row, z in zip(VELOCITIES, population, strict=True)),
                    mp.mpc(0),
                )
                for axis in range(3)
            ],
        ],
        dtype=object,
    )


class Inputs:
    def __init__(self, data):
        if mp.get_context().precision not in numbers.PRECISIONS:
            raise ValueError("registered arithmetic context required")
        self.data = data
        self.bits = mp.get_context().precision
        self.populations, self.reduced, self.moments = {}, {}, {}

    def population(self, indices):
        key = tuple(sorted(indices))
        if key not in self.populations:
            if len(key) == 1:
                value = numbers.exact64(self.data.basis[:, key[0]])
            else:
                row, _ = self.data.rows([key])
                factor = prod(factorial(n) for n in Counter(key).values())
                value = numbers.exact64(self.data.h[len(key)][row[0]]) * factor
            self.populations[key] = value
        return self.populations[key]

    def moment(self, indices):
        key = tuple(sorted(indices))
        if key not in self.moments:
            self.moments[key] = moments(self.population(key))
        return self.moments[key]

    def internal(self, indices):
        key = tuple(sorted(indices))
        if key not in self.reduced:
            if len(key) == 1:
                values = self.data.linear[:, key[0]]
                active = np.flatnonzero(values != 0)
                answer = tuple((int(i), mp.mpc(complex(values[i]))) for i in active)
            else:
                wave = tuple(self.data.waves[list(key)].sum(axis=0))
                row, _ = self.data.rows([key])
                values = self.data.g[len(key)][row[0]]
                active = self.data.wave_indices.get(wave)
                if active is None:
                    if np.any(values != 0):
                        raise ValueError("off-shell internal coefficient cannot be omitted")
                    answer = ()
                else:
                    factor = prod(factorial(n) for n in Counter(key).values())
                    answer = tuple(
                        (int(i), mp.mpc(complex(v)) * factor)
                        for i, v in zip(active, values, strict=True)
                        if v != 0
                    )
            self.reduced[key] = answer
        return self.reduced[key]

    def contract(self, arguments):
        result = zero()
        for row in product(*arguments):
            ids, values = zip(*row, strict=True)
            result += prod(values) * self.population(ids)
        return result


def b(u, v):
    dot = sum((x * y for x, y in zip(u[1:], v[1:], strict=True)), mp.mpc(0))
    return np.array(
        [
            mp.mpfr(float(weight))
            * (
                9
                * sum((c[j] * u[j + 1] for j in range(3)), mp.mpc(0))
                * sum((c[j] * v[j + 1] for j in range(3)), mp.mpc(0))
                - 3 * dot
            )
            for c, weight in zip(VELOCITIES, lattice.WEIGHTS, strict=True)
        ],
        dtype=object,
    )


def c(u, v, w):
    return -u[0] * b(v, w) - v[0] * b(u, w) - w[0] * b(u, v)


def d(values):
    result = zero()
    for pair in combinations(range(4), 2):
        other = [i for i in range(4) if i not in pair]
        result += (
            2 * values[pair[0]][0] * values[pair[1]][0] * b(values[other[0]], values[other[1]])
        )
    return result


def raw_terms(context, slots, *, mutation=None):
    data = context.data
    slots = data.check_slots(slots)
    if mp.get_context().precision != context.bits:
        raise ValueError("cached coefficients cannot be used at a different precision")
    if mutation is not None and mutation not in previous.MUTATIONS:
        raise ValueError("unknown negative control")
    result = np.array([zero() for _ in range(7)], dtype=object)
    v = [context.moment((i,)) for i in slots]
    linear = [context.internal((i,)) for i in slots]
    for single in range(4):
        rest = tuple(slots[i] for i in range(4) if i != single)
        result[0] += b(v[single], context.moment(rest))
        if mutation != "G3":
            result[4] += context.contract((linear[single], context.internal(rest)))
    for partner in (1, 2, 3):
        left = (slots[0], slots[partner])
        right = tuple(slots[i] for i in range(1, 4) if i != partner)
        result[1] += b(context.moment(left), context.moment(right))
        if mutation != "G2":
            result[5] += context.contract((context.internal(left), context.internal(right)))
    for pair in combinations(range(4), 2):
        other = [i for i in range(4) if i not in pair]
        ids = tuple(slots[i] for i in pair)
        result[2] += c(v[other[0]], v[other[1]], context.moment(ids))
        if mutation != "G2":
            result[6] += context.contract(
                (linear[other[0]], linear[other[1]], context.internal(ids))
            )
    result[3] = d(v)
    size = mp.mpfr(data.size)
    normal = mp.sqrt(size**3)
    factors = (
        [mp.mpfr(1)] * 4
        if mutation == "fft_degree"
        else [1 / normal, 1 / normal, 1 / normal**2, 1 / normal**3]
    )
    wave = data.waves[list(slots)].sum(axis=0)
    angle = [2 * mp.const_pi() * int(w) / size for w in wave]
    multiplier = (
        mp.mpfr(1)
        if mutation == "filter"
        else 1
        - mp.mpfr(float(data.eta))
        * sum((mp.sin(k / 2) ** 2 for k in angle), mp.mpfr(0)) ** data.power
    )
    sign = 1 if mutation == "streaming_sign" else -1
    phase = np.array(
        [
            mp.exp(
                mp.mpc(
                    0, sign * sum((v * k for v, k in zip(velocity, angle, strict=True)), mp.mpfr(0))
                )
            )
            for velocity in VELOCITIES
        ],
        dtype=object,
    )
    for i in range(4):
        result[i] *= mp.mpfr(float(data.omega)) * multiplier * factors[i] * phase
    return result


def group(data, groups, blocks, bits, *, mutation=None):
    value = previous.block_product(data, groups, blocks)
    multiplicities = Counter(tuple(sorted(row)) for row in value.rows)
    with numbers.context(bits):
        context = Inputs(data)
        terms = np.stack(
            [
                raw_terms(context, key, mutation=mutation) * mp.sqrt(multiplicities[key])
                for key in value.keys
            ],
            axis=-1,
        )
        collision, composition = terms[:4].sum(axis=0), terms[4:].sum(axis=0)
        return {
            "terms": terms.reshape(189, -1),
            "collision": collision,
            "composition": composition,
            "forcing": collision - composition,
        }


def moment_only(data, slots, *, promote=True):
    """Only moment formation (including integer raw factor) is promoted."""
    original = previous.raw_terms(data, slots)
    if not promote:
        return original
    with numbers.context(192):
        context = Inputs(data)
        v = [numbers.rounded(context.moment((i,))) for i in slots]
        mu = lambda ids: numbers.rounded(context.moment(ids))
        terms = np.zeros((4, 27), dtype=complex)
        for single in range(4):
            terms[0] += previous.local_b(
                v[single], mu(tuple(slots[i] for i in range(4) if i != single))
            )
        for partner in (1, 2, 3):
            terms[1] += previous.local_b(
                mu((slots[0], slots[partner])),
                mu(tuple(slots[i] for i in range(1, 4) if i != partner)),
            )
        for pair in combinations(range(4), 2):
            other = [i for i in range(4) if i not in pair]
            terms[2] += previous.local_c(
                v[other[0]], v[other[1]], mu(tuple(slots[i] for i in pair))
            )
        terms[3] = previous.local_d(v)
    wave = data.waves[list(slots)].sum(axis=0)
    factors = np.array([data.size**-1.5, data.size**-1.5, data.size**-3, data.size**-4.5])
    phase = np.exp(-2j * np.pi * (lattice.VELOCITIES @ wave) / data.size)
    multiplier = damping.wave_multiplier(tuple(wave), data.size, data.eta, data.power)
    original[:4] = terms * (data.omega * multiplier * factors[:, None] * phase)
    return original


def moment_group(data, groups, blocks):
    value = previous.block_product(data, groups, blocks)
    cache = {key: moment_only(data, key) for key in value.keys}
    terms = np.stack([cache[tuple(sorted(row))] for row in value.rows], axis=-1) @ value.basis
    return {
        "terms": terms.reshape(189, -1),
        "collision": terms[:4].sum(axis=0),
        "composition": terms[4:].sum(axis=0),
        "forcing": previous.forcing(terms),
    }
