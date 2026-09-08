"""GMP substitution of the original Taylor polynomials in four labelled variables.

This route does not import the primary kernel, derivative factorials, moments,
or symmetric-product implementation. Sparse polynomial omissions are exact
nilpotent/support zeros, never amplitude thresholds or a reduced input model.
"""

from collections import Counter
from itertools import product

import gmpy2 as mp
import numpy as np

from research import d3q27 as lattice
from research import d3q27_quartic_mp_numbers as numbers

VELOCITIES = tuple(tuple(map(int, row)) for row in lattice.VELOCITIES)


def multiply(left, right):
    """Sparse product in C[t0,t1,t2,t3]/(t0**2,t1**2,t2**2,t3**2)."""
    result = {}
    for a, u in left.items():
        for b, v in right.items():
            if not (a & b):
                mask = a | b
                result[mask] = result.get(mask, mp.mpc(0)) + u * v
    return {mask: value for mask, value in result.items() if value != 0}


def inverse_density(density):
    if density.get(0) != 1:
        raise ValueError("formal density-one expansion required")
    inverse = {0: mp.mpc(1)}
    for mask in range(1, 16):
        value = mp.mpc(0)
        for subset, coefficient in density.items():
            if subset and (subset & mask) == subset:
                value -= coefficient * inverse.get(mask ^ subset, mp.mpc(0))
        if value != 0:
            inverse[mask] = value
    return inverse


def slot_waves(data, slots):
    if len(slots) != 4 or any(
        not isinstance(i, (int, np.integer))
        or isinstance(i, (bool, np.bool_))
        or not 0 <= i < data.dimension
        for i in slots
    ):
        raise ValueError("four labelled in-range coordinates required")
    return np.array(
        [
            sum(
                (data.waves[slots[j]] for j in range(4) if mask & (1 << j)),
                start=np.zeros(3, dtype=np.int64),
            )
            for mask in range(16)
        ]
    )


def monomials(data, coordinates, degree, waves):
    """Original monomial rows on the entire reduced space, including R3 outputs."""
    if len(coordinates) != data.dimension or any(p.get(0, 0) != 0 for p in coordinates):
        raise ValueError("full zero-constant reduced polynomials required")
    active = np.array([any(v != 0 for v in p.values()) for p in coordinates])
    rows = np.flatnonzero(np.all(active[data.indices[degree]], axis=1))
    for row in rows:
        ids = data.indices[degree][row]
        values = coordinates[ids[0]]
        for coordinate in ids[1:]:
            values = multiply(values, coordinates[coordinate])
        for mask, value in values.items():
            if value != 0 and not np.array_equal(data.outputs[degree][row], waves[mask]):
                raise ValueError("composition violates exact Fourier support")
        if values:
            yield int(row), values


def input_polynomials(data, slots):
    waves = slot_waves(data, slots)
    z = [{} for _ in range(data.dimension)]
    fields = np.full((16, 27), mp.mpc(0), dtype=object)
    reduced = [{} for _ in range(data.dimension)]
    for label, coordinate in enumerate(slots):
        mask = 1 << label
        z[coordinate][mask] = mp.mpc(1)
        fields[mask] = numbers.exact64(data.basis[:, coordinate])
        for i, coefficient in enumerate(numbers.exact64(data.linear[:, coordinate])):
            if coefficient != 0:
                reduced[i][mask] = coefficient
    for degree in (2, 3):
        for row, values in monomials(data, z, degree, waves):
            response = numbers.exact64(data.h[degree][row])
            for mask, value in values.items():
                fields[mask] += response * value
            output = tuple(data.outputs[degree][row])
            indices = data.wave_indices.get(output)
            if indices is None:
                if np.any(data.g[degree][row] != 0):
                    raise ValueError("off-shell reduced coefficient cannot be discarded")
                continue
            coefficients = numbers.exact64(data.g[degree][row])
            for i, coefficient in zip(indices, coefficients, strict=True):
                if coefficient != 0:
                    for mask, value in values.items():
                        reduced[i][mask] = reduced[i].get(mask, mp.mpc(0)) + coefficient * value
    return fields, reduced, waves


def composition(data, reduced, waves):
    result = np.full(27, mp.mpc(0), dtype=object)
    for i, coordinate in enumerate(reduced):
        if coordinate.get(15, 0) != 0:
            result += numbers.exact64(data.basis[:, i]) * coordinate[15]
    for degree in (2, 3):
        for row, values in monomials(data, reduced, degree, waves):
            if values.get(15, 0) != 0:
                result += numbers.exact64(data.h[degree][row]) * values[15]
    return result


def rational_equilibrium(density, momentum, velocity):
    """Original rational equilibrium coefficient, with no B/C/D calls."""
    cj = {}
    for axis in range(3):
        for mask, value in momentum[axis].items():
            cj[mask] = cj.get(mask, mp.mpc(0)) + velocity[axis] * value
    numerator = {mask: value * mp.mpfr(9) / 2 for mask, value in multiply(cj, cj).items()}
    for polynomial in momentum:
        for mask, value in multiply(polynomial, polynomial).items():
            numerator[mask] = numerator.get(mask, mp.mpc(0)) - value * mp.mpfr(3) / 2
    rational = multiply(numerator, inverse_density(density))
    return density.get(15, mp.mpc(0)) + 3 * cj.get(15, mp.mpc(0)) + rational.get(15, mp.mpc(0))


def raw_forcing(data, slots):
    if mp.get_context().precision not in numbers.PRECISIONS:
        raise ValueError("registered GMP context required")
    fields, reduced, waves = input_polynomials(data, slots)
    normal = mp.sqrt(mp.mpfr(data.size) ** 3)
    # Sum original population coefficients in reverse population order. All
    # operations, including integer velocities and FFT normalization, are GMP.
    moments = []
    for field in fields:
        moments.append(
            [
                sum(
                    (
                        field[q] * (1 if axis == 0 else VELOCITIES[q][axis - 1])
                        for q in range(26, -1, -1)
                    ),
                    mp.mpc(0),
                )
                / normal
                for axis in range(4)
            ]
        )
    angles = [[2 * mp.const_pi() * int(w) / data.size for w in wave] for wave in waves]
    multiplier = (
        1
        - mp.mpfr(float(data.eta))
        * sum(((1 - mp.cos(k)) / 2 for k in angles[15]), mp.mpfr(0)) ** data.power
    )
    collision = []
    for q, velocity in enumerate(VELOCITIES):
        density, momentum = {0: mp.mpc(1)}, [{}, {}, {}]
        for mask in range(1, 16):
            # Shift every lower-order input at x-c_q before composing the
            # equilibrium; do not borrow the primary output-wave phase.
            phase = mp.exp(
                mp.mpc(
                    0, -sum((velocity[axis] * angles[mask][axis] for axis in range(3)), mp.mpfr(0))
                )
            )
            density[mask] = moments[mask][0] * phase
            for axis in range(3):
                momentum[axis][mask] = moments[mask][axis + 1] * phase
        coefficient = rational_equilibrium(density, momentum, velocity)
        collision.append(
            coefficient
            * mp.mpfr(float(lattice.WEIGHTS[q]))
            * mp.mpfr(float(data.omega))
            * multiplier
            * normal
        )
    collision = np.array(collision, dtype=object)
    composed = composition(data, reduced, waves)
    return {"forcing": collision - composed, "collision": collision, "composition": composed}


def columns(groups, blocks, dimension):
    if len(groups) != 4 or any(type(b) is not int or not 0 <= b < len(blocks) for b in groups):
        raise ValueError("four valid block labels required")
    if any(not row for row in blocks) or sorted(i for row in blocks for i in row) != list(
        range(dimension)
    ):
        raise ValueError("blocks must partition the full coordinate inventory")
    counts = Counter(tuple(sorted(ids)) for ids in product(*(blocks[b] for b in groups)))
    return tuple((ids, counts[ids]) for ids in sorted(counts))


def group(data, groups, blocks, bits):
    with numbers.context(bits):
        evaluated = [
            (raw_forcing(data, slots), mp.sqrt(count))
            for slots, count in columns(groups, blocks, data.dimension)
        ]
        normalized = {
            name: np.column_stack([row[name] * factor for row, factor in evaluated])
            for name in ("collision", "composition")
        }
        # Define the persisted F4 from the persisted normalized contributions.
        # Scaling an already rounded difference is not bitwise distributive.
        return {
            "forcing": normalized["collision"] - normalized["composition"],
            **normalized,
        }
