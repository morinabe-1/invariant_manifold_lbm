"""Independent four-labelled nilpotent substitution of the original W3/R3.

No imports of the seven-term kernel, derivative factorials or symmetric-product
implementation. Multiplicity comes from polynomial multiplication itself.
"""

from collections import Counter
from itertools import product

import numpy as np

from research import d3q27 as lattice


def multiply(left, right):
    """Product in C[t0,t1,t2,t3]/(t0**2,t1**2,t2**2,t3**2)."""
    left, right = np.asarray(left), np.asarray(right)
    if left.shape[0] != 16 or right.shape[0] != 16:
        raise ValueError("sixteen nilpotent coefficients required")
    result = np.zeros((16, *np.broadcast_shapes(left.shape[1:], right.shape[1:])), dtype=complex)
    for mask in range(16):
        subset = mask
        while True:
            result[mask] += left[subset] * right[mask ^ subset]
            if subset == 0:
                break
            subset = (subset - 1) & mask
    return result


def inverse_density(density):
    if not np.all(density[0] == 1):
        raise ValueError("formal expansion is at the declared density one")
    result = np.zeros_like(density, dtype=complex)
    result[0] = 1
    for mask in range(1, 16):
        subset = mask
        while subset:
            result[mask] -= density[subset] * result[mask ^ subset]
            subset = (subset - 1) & mask
    return result


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
    """Use original rows, pruning only exactly inactive coordinates, not magnitudes."""
    if coordinates.shape != (16, data.dimension) or np.any(coordinates[0] != 0):
        raise ValueError("zero-constant polynomial on the full reduced space required")
    active = np.any(coordinates != 0, axis=0)
    rows = np.flatnonzero(np.all(active[data.indices[degree]], axis=1))
    ids = data.indices[degree][rows]
    values = coordinates[:, ids[:, 0]]
    for slot in range(1, degree):
        values = multiply(values, coordinates[:, ids[:, slot]])
    for mask in range(16):
        off = np.any(data.outputs[degree][rows] != waves[mask], axis=1)
        if np.any(values[mask, off] != 0):
            raise ValueError("polynomial composition leaks outside exact Fourier support")
    return rows, values


def input_polynomials(data, slots):
    waves = slot_waves(data, slots)
    z = np.zeros((16, data.dimension), dtype=complex)
    for j, coordinate in enumerate(slots):
        z[1 << j, coordinate] = 1
    fields = z @ data.basis.T
    reduced = z @ data.linear.T
    for degree in (2, 3):
        rows, values = monomials(data, z, degree, waves)
        fields += values @ data.h[degree][rows]
        for wave, indices in data.wave_indices.items():
            selected = np.all(data.outputs[degree][rows] == wave, axis=1)
            reduced[:, indices] += values[:, selected] @ data.g[degree][rows[selected]]
    return fields, reduced, waves


def composition(data, reduced, waves):
    result = reduced[15] @ data.basis.T
    for degree in (2, 3):
        rows, values = monomials(data, reduced, degree, waves)
        result += values[15] @ data.h[degree][rows]
    return result


def equilibrium_fourth(density, momentum, velocities):
    """Extract degree four from the original rational equilibrium, not B/C/D."""
    cj = np.sum(momentum * velocities, axis=-1)
    numerator = 4.5 * multiply(cj, cj)
    for axis in range(3):
        numerator -= 1.5 * multiply(momentum[..., axis], momentum[..., axis])
    rational = multiply(numerator, inverse_density(density))
    return density[15] + 3 * cj[15] + rational[15]


def raw_forcing(data, slots):
    fields, reduced, waves = input_polynomials(data, slots)
    moments = fields @ lattice.conserved_moment_matrix().T / np.sqrt(data.size**3)
    # Each population samples the entire lower-order input at x-c_q before
    # equilibrium composition. This does not reuse the main output phase.
    phase = np.exp(-2j * np.pi * (waves @ lattice.VELOCITIES.T) / data.size)
    shifted = moments[:, None, :] * phase[:, :, None]
    density = shifted[..., 0].copy()
    density[0] = 1
    eq = equilibrium_fourth(density, shifted[..., 1:], lattice.VELOCITIES)
    angle = 2 * np.pi * waves[15] / data.size
    multiplier = 1 - data.eta * np.sum((1 - np.cos(angle)) / 2) ** data.power
    collision = data.omega * multiplier * lattice.WEIGHTS * eq * np.sqrt(data.size**3)
    composed = composition(data, reduced, waves)
    if not np.isfinite(collision).all() or not np.isfinite(composed).all():
        raise ValueError("nonfinite independent quartic coefficients")
    return {"forcing": collision - composed, "collision": collision, "composition": composed}


def columns(groups, block_indices):
    """Independent Cartesian enumeration; no derivative or basis conversion call."""
    counts = Counter(tuple(sorted(ids)) for ids in product(*(block_indices[b] for b in groups)))
    return tuple((ids, np.sqrt(counts[ids])) for ids in sorted(counts))


def group_forcing(data, groups, block_indices):
    cases = columns(groups, block_indices)
    evaluated = [(raw_forcing(data, slots), factor) for slots, factor in cases]
    return {
        name: np.column_stack([row[name] * factor for row, factor in evaluated])
        for name in ("forcing", "collision", "composition")
    }
