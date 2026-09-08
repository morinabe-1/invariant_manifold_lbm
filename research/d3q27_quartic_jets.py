"""Exact GMP Gaussian-rational mixed derivatives for the Q012h1 main route.

Labeled nilpotent slots extract mixed Frechet derivatives directly. This is not
the independent worker's global-coordinate Fraction polynomial representation.
"""

from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement
from math import factorial

from gmpy2 import mpq


@dataclass(frozen=True, slots=True)
class Gaussian:
    real: object = 0
    imag: object = 0

    def __post_init__(self):
        object.__setattr__(self, "real", mpq(self.real))
        object.__setattr__(self, "imag", mpq(self.imag))

    def __bool__(self):
        return bool(self.real or self.imag)

    def __complex__(self):
        return complex(float(self.real), float(self.imag))

    def __add__(self, other):
        other = other if isinstance(other, Gaussian) else Gaussian(other)
        return Gaussian(self.real + other.real, self.imag + other.imag)

    __radd__ = __add__

    def __neg__(self):
        return Gaussian(-self.real, -self.imag)

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        other = other if isinstance(other, Gaussian) else Gaussian(other)
        return Gaussian(
            self.real * other.real - self.imag * other.imag,
            self.real * other.imag + self.imag * other.real,
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = other if isinstance(other, Gaussian) else Gaussian(other)
        denominator = other.real**2 + other.imag**2
        if not denominator:
            raise ZeroDivisionError("zero Gaussian rational")
        return self * Gaussian(other.real / denominator, -other.imag / denominator)

    def conjugate(self):
        return Gaussian(self.real, -self.imag)

    def record(self):
        return [str(v) for q in (self.real, self.imag) for v in (q.numerator, q.denominator)]


ZERO, ONE, IMAG = Gaussian(), Gaussian(1), Gaussian(0, 1)


def dot(left, right):
    return sum((a * b for a, b in zip(left, right, strict=True)), ZERO)


def matvec(matrix, vector):
    return tuple(dot(row, vector) for row in matrix)


def scale(vector, scalar):
    return tuple(v * scalar for v in vector)


def add(*vectors):
    return tuple(sum(values, ZERO) for values in zip(*vectors, strict=True))


def multiply(values):
    result = ONE
    for value in values:
        result *= value
    return result


class Jet:
    """Coefficient of each subset of labeled variables; each variable squares to zero."""

    def __init__(self, order, values):
        if type(order) is not int or not 1 <= order <= 4:
            raise ValueError("one through four labeled slots required")
        self.order = order
        self.values = tuple(values)
        if len(self.values) != 2**order or any(not isinstance(v, Gaussian) for v in self.values):
            raise ValueError("one Gaussian coefficient per subset required")

    @classmethod
    def linear(cls, coefficients):
        coefficients = tuple(coefficients)
        values = [ZERO] * 2 ** len(coefficients)
        for slot, value in enumerate(coefficients):
            values[1 << slot] = value
        return cls(len(coefficients), values)

    def __add__(self, other):
        if not isinstance(other, Jet) or self.order != other.order:
            raise ValueError("matching labeled-jet orders required")
        return Jet(self.order, (a + b for a, b in zip(self.values, other.values, strict=True)))

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        if not isinstance(other, Jet):
            return Jet(self.order, (v * other for v in self.values))
        if self.order != other.order:
            raise ValueError("matching labeled-jet orders required")
        values = [ZERO] * len(self.values)
        for i, a in enumerate(self.values):
            if a:
                for j, b in enumerate(other.values):
                    if b and not i & j:
                        values[i | j] += a * b
        return Jet(self.order, values)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return self * (ONE / scalar)

    def coefficient(self):
        return self.values[-1]


def tail(value):
    square = value * value
    cube = square * value
    return square / 2 + cube / 6 + cube * value / 24


class Manufactured:
    """The preregistered graph map, evaluated through five linear features."""

    def __init__(self, external, representation):
        if type(external) is not int or external not in (23, 27):
            raise ValueError("external dimension 23 or 27 required")
        if representation not in ("real", "complex"):
            raise ValueError("registered real or complex representation required")
        self.external, self.representation = external, representation
        self.width = 8 + external + 4
        self.ell = tuple(Gaussian(mpq(i + 1, 8)) for i in range(8))
        self.m = tuple(Gaussian(mpq((-1) ** i, 8)) for i in range(8))
        self.alpha = tuple(Gaussian(mpq(z + 1, 32)) for z in range(external))
        self.beta = tuple(Gaussian(mpq((-1) ** z, 64)) for z in range(external))
        self.gamma = tuple(Gaussian(mpq((-1) ** i, 32)) for i in range(8))
        self.delta = tuple(Gaussian(mpq(i + 1, 64)) for i in range(8))
        self.u = tuple(Gaussian(mpq(i + 1, 128)) for i in range(8))
        self.t = tuple(Gaussian(mpq(z + 1, 128)) for z in range(external))
        physical, transform, inverse = ([[ZERO] * 8 for _ in range(8)] for _ in range(3))
        for b in range(4):
            a, rate, s = Gaussian(mpq(3, 5) + mpq(b, 40)), Gaussian(mpq(b + 1, 40)), b + 1
            local = ((a + s * rate, -(s * s + 1) * rate), (rate, a - s * rate))
            p = (
                ((ONE, ZERO), (ZERO, ONE))
                if representation == "real"
                else ((ONE - s * IMAG, ONE + s * IMAG), (-IMAG, IMAG))
            )
            determinant = p[0][0] * p[1][1] - p[0][1] * p[1][0]
            pinv = (
                (p[1][1] / determinant, -p[0][1] / determinant),
                (-p[1][0] / determinant, p[0][0] / determinant),
            )
            for i in range(2):
                for j in range(2):
                    physical[2 * b + i][2 * b + j] = local[i][j]
                    transform[2 * b + i][2 * b + j] = p[i][j]
                    inverse[2 * b + i][2 * b + j] = pinv[i][j]
        self.physical, self.transform, self.inverse = map(
            lambda rows: tuple(map(tuple, rows)), (physical, transform, inverse)
        )
        self.units = tuple(tuple(ONE if j == i else ZERO for j in range(8)) for i in range(8))
        self.linear_units = tuple(
            matvec(self.inverse, matvec(self.physical, matvec(self.transform, e)))
            for e in self.units
        )
        self.vectors = tuple(
            (*matvec(self.transform, e), *((ZERO,) * (external + 4))) for e in self.units
        )
        self.a = tuple(
            tuple(
                -Gaussian(mpq(1, 5) + mpq(z, 10 * external))
                if z == j
                else Gaussian(mpq(1, 100))
                if j == z + 1
                else ZERO
                for j in range(external)
            )
            for z in range(external)
        )
        self.a_alpha, self.a_beta = matvec(self.a, self.alpha), matvec(self.a, self.beta)
        self.y_unit = (*((ZERO,) * 8), Gaussian(external + 1), *((ZERO,) * (external + 3)))
        self._b_vy = tuple(self.phi_derivative((v, self.y_unit)) for v in self.vectors)
        self._b_yy = self.phi_derivative((self.y_unit, self.y_unit))
        self._c_vvy = {
            (i, j): self.phi_derivative((self.vectors[i], self.vectors[j], self.y_unit))
            for i, j in combinations_with_replacement(range(8), 2)
        }

    def features(self, directions):
        directions = tuple(directions)
        if not 2 <= len(directions) <= 4 or any(len(value) != 8 for value in directions):
            raise ValueError("two through four eight-coordinate directions required")
        physical = tuple(matvec(self.transform, value) for value in directions)
        return multiply(dot(self.ell, value) for value in physical), multiply(
            dot(self.m, value) for value in physical
        )

    def h(self, directions):
        ell, m = self.features(directions)
        return (*((ZERO,) * 8), *add(scale(self.alpha, ell), scale(self.beta, m)), *((ZERO,) * 4))

    def g(self, directions):
        ell, m = self.features(directions)
        return matvec(self.inverse, add(scale(self.gamma, ell), scale(self.delta, m)))

    def mean_y(self, value):
        return sum(value[8 : 8 + self.external], ZERO) / (self.external + 1)

    def phi_derivative(self, directions):
        directions = tuple(directions)
        if not 1 <= len(directions) <= 4 or any(len(v) != self.width for v in directions):
            raise ValueError("one through four full physical directions required")
        xs = tuple(v[:8] for v in directions)
        ell = Jet.linear(dot(self.ell, x) for x in xs)
        m = Jet.linear(dot(self.m, x) for x in xs)
        le = Jet.linear(dot(self.ell, matvec(self.physical, x)) for x in xs)
        me = Jet.linear(dot(self.m, matvec(self.physical, x)) for x in xs)
        ey = Jet.linear(self.mean_y(v) for v in directions)
        hl, hm = tail(ell), tail(m)
        er = (
            ey
            - hl * (sum(self.alpha, ZERO) / (self.external + 1))
            - hm * (sum(self.beta, ZERO) / (self.external + 1))
        )
        lr = le + hl * dot(self.ell, self.gamma) + hm * dot(self.ell, self.delta)
        mr = me + hl * dot(self.m, self.gamma) + hm * dot(self.m, self.delta)
        hr_l, hr_m = tail(lr), tail(mr)
        u = ell * er + er * er + ell * ell * er
        t = ell * er * 2 - er * er + ell * ell * er * 3
        linear_x = matvec(self.physical, xs[0]) if len(directions) == 1 else (ZERO,) * 8
        linear_y = (
            matvec(self.a, directions[0][8 : 8 + self.external])
            if len(directions) == 1
            else (ZERO,) * self.external
        )
        first = add(
            linear_x,
            scale(self.gamma, hl.coefficient()),
            scale(self.delta, hm.coefficient()),
            scale(self.u, u.coefficient()),
        )
        second = add(
            linear_y,
            scale(self.alpha, hr_l.coefficient()),
            scale(self.beta, hr_m.coefficient()),
            scale(self.a_alpha, -hl.coefficient()),
            scale(self.a_beta, -hm.coefficient()),
            scale(self.t, t.coefficient()),
        )
        return (*first, *second, *(directions[0][-4:] if len(directions) == 1 else (ZERO,) * 4))

    def forcing_groups(self, key):
        if (
            len(key) != 4
            or tuple(sorted(key)) != tuple(key)
            or any(type(i) is not int or i not in range(8) for i in key)
        ):
            raise ValueError("sorted four-coordinate monomial required")
        directions = tuple(self.units[i] for i in key)
        terms = {
            name: (ZERO,) * self.width
            for name in (
                "B_V_H3",
                "B_H2_H2",
                "C_V_V_H2",
                "D_V4",
                "minus_H2_L_G3",
                "minus_H2_G2_G2",
                "minus_H3_L_L_G2",
            )
        }
        for slot in range(4):
            others = tuple(directions[i] for i in range(4) if i != slot)
            terms["B_V_H3"] = add(
                terms["B_V_H3"], scale(self._b_vy[key[slot]], self.mean_y(self.h(others)))
            )
            terms["minus_H2_L_G3"] = add(
                terms["minus_H2_L_G3"],
                scale(self.h((self.linear_units[key[slot]], self.g(others))), -1),
            )
        for partner in (1, 2, 3):
            first = (directions[0], directions[partner])
            second = tuple(directions[i] for i in range(1, 4) if i != partner)
            terms["B_H2_H2"] = add(
                terms["B_H2_H2"],
                scale(self._b_yy, self.mean_y(self.h(first)) * self.mean_y(self.h(second))),
            )
            terms["minus_H2_G2_G2"] = add(
                terms["minus_H2_G2_G2"], scale(self.h((self.g(first), self.g(second))), -1)
            )
        for pair in combinations(range(4), 2):
            rest = tuple(i for i in range(4) if i not in pair)
            h = self.h(tuple(directions[i] for i in pair))
            indices = tuple(sorted(key[i] for i in rest))
            terms["C_V_V_H2"] = add(terms["C_V_V_H2"], scale(self._c_vvy[indices], self.mean_y(h)))
            args = (
                *tuple(self.linear_units[key[i]] for i in rest),
                self.g(tuple(directions[i] for i in pair)),
            )
            terms["minus_H3_L_L_G2"] = add(terms["minus_H3_L_L_G2"], scale(self.h(args), -1))
        terms["D_V4"] = self.phi_derivative(tuple(self.vectors[i] for i in key))
        return terms

    def known_identity(self, key):
        directions = tuple(self.units[i] for i in key)
        response, reduced = self.h(directions), self.g(directions)
        composed = self.h(tuple(self.linear_units[i] for i in key))
        linear_response = (
            *((ZERO,) * 8),
            *matvec(self.a, response[8 : 8 + self.external]),
            *((ZERO,) * 4),
        )
        selected = (*matvec(self.transform, reduced), *((ZERO,) * (self.external + 4)))
        return response, reduced, add(composed, scale(linear_response, -1), selected)


def raw_factor(key):
    return multiply(Gaussian(factorial(key.count(i))) for i in set(key))
