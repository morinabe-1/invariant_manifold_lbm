"""Independent Fraction composition of the Q012h1 manufactured map.

Polynomial keys are sorted global-coordinate monomials, truncated at degree 4.
This module imports no main-route arithmetic, derivative, or forcing kernels.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations_with_replacement
from math import factorial, prod

ZERO = (Fraction(0), Fraction(0))
ONE = (Fraction(1), Fraction(0))
IMAG = (Fraction(0), Fraction(1))


def real(numerator, denominator=1):
    return Fraction(numerator, denominator), Fraction(0)


def cadd(a, b):
    return a[0] + b[0], a[1] + b[1]


def cneg(a):
    return -a[0], -a[1]


def cmul(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def csum(values):
    result = ZERO
    for value in values:
        result = cadd(result, value)
    return result


def record(value):
    return [str(part) for number in value for part in (number.numerator, number.denominator)]


def add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for key, value in polynomial.items():
            result[key] = cadd(result.get(key, ZERO), value)
    return {k: v for k, v in result.items() if v != ZERO}


def scale(polynomial, scalar):
    return {
        key: cmul(value, scalar)
        for key, value in polynomial.items()
        if value != ZERO and scalar != ZERO
    }


def mul(left, right):
    result = {}
    for a, x in left.items():
        for b, y in right.items():
            if len(a) + len(b) <= 4:
                key = tuple(sorted(a + b))
                result[key] = cadd(result.get(key, ZERO), cmul(x, y))
    return {key: value for key, value in result.items() if value != ZERO}


def tail(polynomial, maximum=4):
    result, powered = {}, polynomial
    for degree in range(2, maximum + 1):
        powered = mul(powered, polynomial)
        result = add(result, scale(powered, real(1, factorial(degree))))
    return result


def linear(coefficients, polynomials):
    return add(*(scale(p, c) for c, p in zip(coefficients, polynomials, strict=True)))


def apply(matrix, polynomials):
    return tuple(linear(row, polynomials) for row in matrix)


def substitute(polynomials, coordinates):
    expansions = {}
    for key in {key for polynomial in polynomials for key in polynomial}:
        value = {(): ONE}
        for i in key:
            value = mul(value, coordinates[i])
        expansions[key] = value
    return tuple(
        add(*(scale(expansions[key], coefficient) for key, coefficient in polynomial.items()))
        for polynomial in polynomials
    )


def recipe(external, representation):
    if (
        type(external) is not int
        or external not in (23, 27)
        or representation not in ("real", "complex")
    ):
        raise ValueError("registered external dimension and representation required")
    lam, p, inverse = ([[ZERO for _ in range(8)] for _ in range(8)] for _ in range(3))
    for b in range(4):
        a, w, s = Fraction(3, 5) + Fraction(b, 40), Fraction(b + 1, 40), b + 1
        lam[2 * b][2 * b] = real(a + s * w)
        lam[2 * b][2 * b + 1] = real(-(1 + s * s) * w)
        lam[2 * b + 1][2 * b] = real(w)
        lam[2 * b + 1][2 * b + 1] = real(a - s * w)
        if representation == "real":
            p[2 * b][2 * b] = p[2 * b + 1][2 * b + 1] = ONE
            inverse[2 * b][2 * b] = inverse[2 * b + 1][2 * b + 1] = ONE
        else:
            p[2 * b][2 * b], p[2 * b][2 * b + 1] = (
                (Fraction(1), Fraction(-s)),
                (Fraction(1), Fraction(s)),
            )
            p[2 * b + 1][2 * b], p[2 * b + 1][2 * b + 1] = cneg(IMAG), IMAG
            inverse[2 * b][2 * b] = inverse[2 * b + 1][2 * b] = real(1, 2)
            inverse[2 * b][2 * b + 1] = Fraction(-s, 2), Fraction(1, 2)
            inverse[2 * b + 1][2 * b + 1] = Fraction(-s, 2), Fraction(-1, 2)
    a = tuple(
        tuple(
            real(-Fraction(1, 5) - Fraction(i, 10 * external))
            if i == k
            else real(1, 100)
            if k == i + 1
            else ZERO
            for k in range(external)
        )
        for i in range(external)
    )
    return {
        "lambda": tuple(map(tuple, lam)),
        "transform": tuple(map(tuple, p)),
        "inverse": tuple(map(tuple, inverse)),
        "a": a,
        "ell": tuple(real(i + 1, 8) for i in range(8)),
        "m": tuple(real((-1) ** i, 8) for i in range(8)),
        "alpha": tuple(real(i + 1, 32) for i in range(external)),
        "beta": tuple(real((-1) ** i, 64) for i in range(external)),
        "gamma": tuple(real((-1) ** i, 32) for i in range(8)),
        "delta": tuple(real(i + 1, 64) for i in range(8)),
        "u": tuple(real(i + 1, 128) for i in range(8)),
        "t": tuple(real(i + 1, 128) for i in range(external)),
    }


def h(recipe, physical, maximum=4):
    ell, m = (tail(linear(recipe[name], physical), maximum) for name in ("ell", "m"))
    return tuple(
        add(scale(ell, a), scale(m, b))
        for a, b in zip(recipe["alpha"], recipe["beta"], strict=True)
    )


def reduced(recipe, physical):
    ell, m = (tail(linear(recipe[name], physical)) for name in ("ell", "m"))
    return tuple(
        add(v, scale(ell, a), scale(m, b))
        for v, a, b in zip(
            apply(recipe["lambda"], physical), recipe["gamma"], recipe["delta"], strict=True
        )
    )


def phi(recipe, physical, external):
    full_h, r = h(recipe, physical), reduced(recipe, physical)
    error = tuple(add(y, scale(hh, real(-1))) for y, hh in zip(external, full_h, strict=True))
    e = linear((real(1, len(external) + 1),) * len(external), error)
    ell = linear(recipe["ell"], physical)
    le, ee, lle = mul(ell, e), mul(e, e), mul(mul(ell, ell), e)
    u, t = add(le, ee, lle), add(scale(le, real(2)), scale(ee, real(-1)), scale(lle, real(3)))
    first = tuple(
        add(value, scale(u, coefficient)) for value, coefficient in zip(r, recipe["u"], strict=True)
    )
    second = tuple(
        add(value, correction, scale(t, coefficient))
        for value, correction, coefficient in zip(
            h(recipe, r), apply(recipe["a"], error), recipe["t"], strict=True
        )
    )
    return (*first, *second, {}, {}, {}, {})


def raw_columns(polynomials, degree):
    keys = tuple(combinations_with_replacement(range(8), degree))
    columns = tuple(
        tuple(
            cmul(p.get(key, ZERO), real(prod(factorial(n) for n in Counter(key).values())))
            for p in polynomials
        )
        for key in keys
    )
    return keys, columns


def manufactured(external, representation):
    params = recipe(external, representation)
    variables = tuple({(i,): ONE} for i in range(8))
    x = apply(params["transform"], variables)
    hh = h(params, x)
    r = apply(params["inverse"], reduced(params, x))
    lower_h = tuple({k: v for k, v in p.items() if len(k) <= 3} for p in hh)
    lower_r = tuple({k: v for k, v in p.items() if len(k) <= 3} for p in r)
    phi_lower = phi(params, x, lower_h)
    physical_lower_r = apply(params["transform"], lower_r)
    composed_lower = (*physical_lower_r, *h(params, physical_lower_r, 3), {}, {}, {}, {})
    defect = tuple(
        add(left, scale(right, real(-1)))
        for left, right in zip(phi_lower, composed_lower, strict=True)
    )
    if any(len(key) < 4 for polynomial in defect for key in polynomial):
        raise ValueError("known cubic chart has a lower-order defect")
    phi_full = phi(params, x, hh)
    physical_r = apply(params["transform"], r)
    composed_full = (*physical_r, *h(params, physical_r), {}, {}, {}, {})
    if phi_full != composed_full:
        raise ValueError("known full graph map identity failed")
    known = {
        degree: {
            "h": raw_columns(({},) * 8 + hh + ({},) * 4, degree),
            "g": raw_columns(r, degree),
        }
        for degree in (2, 3, 4)
    }
    # Recover the real-chart coefficients by actual substitution, including
    # the reduced output transform, rather than merely checking inverse P.
    transformed_variables = apply(params["inverse"], variables)
    real_h = substitute(hh, transformed_variables)
    real_r = apply(params["transform"], substitute(r, transformed_variables))
    baseline = recipe(external, "real")
    if real_h != h(baseline, variables) or real_r != reduced(baseline, variables):
        raise ValueError("full coefficient realification failed")
    return {
        "external_dimension": external,
        "representation": representation,
        "transform": params["transform"],
        "inverse": params["inverse"],
        "known": known,
        "forcing": raw_columns(defect, 4),
        "known_graph_identity": True,
        "full_coefficient_realification": True,
    }
