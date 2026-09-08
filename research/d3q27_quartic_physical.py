"""Physical-grid calibration of mixed fourth derivatives, one population at a time.

The equilibrium is expanded at the declared rho=1,j=0. These formal Taylor
coefficients do not remove constant/lower-order rounding errors from Phi(W(a)).
"""

import numpy as np

from research import d3q27 as lattice
from research import d3q27_quartic_polynomial as polynomial


def stencil(field):
    result = np.zeros_like(field)
    for axis in range(3):
        result += (2 * field - np.roll(field, 1, axis) - np.roll(field, -1, axis)) / 4
    return result


def fourth_coefficient(data, slots, *, sample=None):
    """Measure every off-wave FFT coefficient; never subtract squared norms.

    Input and output FFTs are orthonormal. The population loop bounds memory;
    the optional resource callback also samples physical allocation/FFT stages.
    """
    fields, reduced, waves = polynomial.input_polynomials(data, slots)
    moments = fields @ lattice.conserved_moment_matrix().T
    size = data.size
    shape = (size,) * 3
    physical = np.zeros((16, *shape, 4), dtype=complex)
    for mask in range(1, 15):
        spectrum = np.zeros((*shape, 4), dtype=complex)
        x, y, z = waves[mask]
        spectrum[z % size, y % size, x % size] = moments[mask]
        physical[mask] = np.fft.ifftn(spectrum, axes=(0, 1, 2), norm="ortho")
    del spectrum
    density = physical[..., 0].copy()
    density[0] = 1
    inverse = polynomial.inverse_density(density)
    if sample is not None:
        sample("physical_moments_and_inverse")
    # The kinetic numerator is shared across populations but kept as a
    # polynomial, independent of the raw derivative grouping.
    momentum_square = np.zeros((16, *shape), dtype=complex)
    for axis in range(3):
        momentum_square += polynomial.multiply(physical[..., axis + 1], physical[..., axis + 1])
    collision = np.empty(27, dtype=complex)
    composition = polynomial.composition(data, reduced, waves)
    target = tuple(int(v % size) for v in waves[15, ::-1])
    leakage_squared = 0.0
    for q, (cx, cy, cz) in enumerate(lattice.VELOCITIES):
        cj = cx * physical[..., 1] + cy * physical[..., 2] + cz * physical[..., 3]
        numerator = 4.5 * polynomial.multiply(cj, cj) - 1.5 * momentum_square
        eq = polynomial.multiply(numerator, inverse)[15] * lattice.WEIGHTS[q]
        streamed = np.roll(data.omega * eq, (cz, cy, cx), axis=(0, 1, 2))
        derivative = stencil(streamed)
        if data.power == 2:
            derivative = stencil(derivative)
        filtered = streamed - data.eta * derivative
        spectrum = np.fft.fftn(filtered, norm="ortho")
        collision[q] = spectrum[target]
        spectrum[target] = 0  # Exclude only the expected output coefficient from leakage.
        leakage_squared += float(np.sum(np.abs(spectrum) ** 2))
        if sample is not None:
            sample(f"physical_population_{q}")
    result = {
        "forcing": collision - composition,
        "collision": collision,
        "composition": composition,
        "off_wave_norm": float(np.sqrt(leakage_squared)),
        "output_wave": waves[15].tolist(),
        "fft_coefficients_inspected": 27 * size**3,
    }
    if any(not np.isfinite(result[k]).all() for k in ("forcing", "collision", "composition")):
        raise ValueError("nonfinite physical calibration")
    return result


def calibration_cases(groups, block_indices, *, mandatory=(0, 3, 6, 9)):
    """Lex-first populated pattern/sector bins, plus the preregistered 432 case."""
    from collections import Counter

    from research.d3q27_quartic_selection import group_wave, sector

    groups = tuple(sorted(tuple(g) for g in groups))
    chosen = {}
    for group in groups:
        key = (tuple(sorted(Counter(group).values(), reverse=True)), sector(group_wave(group)))
        chosen.setdefault(key, group)
    if mandatory not in set(groups):
        raise ValueError("mandatory maximum-dimension calibration tuple is missing")
    tuples = sorted(set(chosen.values()) | {mandatory})
    result = []
    for group in tuples:
        columns = polynomial.columns(group, block_indices)
        for column in sorted({0, len(columns) - 1}):
            slots, scale = columns[column]
            result.append({"group": group, "column": column, "slots": slots, "scale": scale})
    return result
