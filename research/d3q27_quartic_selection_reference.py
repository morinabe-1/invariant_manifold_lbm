"""Independent S0 route: scalar nested enumeration and cached pair products.

Only the saved numerical spectral inputs are shared. No primary tuple iterator,
distance kernel, bin reducer, or Fourier-symbol routine is imported here.
"""

from collections import Counter
from itertools import product
from math import comb

import numpy as np


def direct_input_audit(arrays, size):
    """Rebuild population symbols independently; retain the shared graph gauge."""
    velocities = np.array(list(product([-1, 0, 1], repeat=3)))
    weights = np.array([np.prod([2 / 3 if v == 0 else 1 / 6 for v in c]) for c in velocities])
    moments = np.vstack((np.ones(27), velocities.T))
    equilibrium = weights[:, None] * np.column_stack((np.ones(27), 3 * velocities))
    collision = -0.5 * np.eye(27) + 1.5 * equilibrium @ moments

    def symbol(wave):
        k = 2 * np.pi * np.asarray(wave) / size
        phase = velocities @ k
        damping = 1 - 0.02 * (np.sum((1 - np.cos(k)) / 2)) ** 2
        return damping * (np.cos(phase) - 1j * np.sin(phase))[:, None] * collision

    errors = {
        "block_invariance": 0.0,
        "external_invariance": 0.0,
        "external_projection": 0.0,
        "orthogonality": 0.0,
        "zero_conservation": 0.0,
    }
    for index, (wave, dim) in enumerate(
        zip(arrays["block_waves"], arrays["block_dimensions"], strict=True)
    ):
        v = arrays["block_basis"][index, :, :dim]
        matrix = arrays["block_dynamics"][index, :dim, :dim]
        errors["block_invariance"] = max(
            errors["block_invariance"], float(np.linalg.norm(symbol(wave) @ v - v @ matrix))
        )
    for index, (wave, dim) in enumerate(
        zip(arrays["external_waves"], arrays["external_dimensions"], strict=True)
    ):
        v = arrays["external_basis"][index, :, :dim]
        matrix = arrays["external_dynamics"][index, :dim, :dim]
        projection = arrays["external_projection"][index]
        errors["external_invariance"] = max(
            errors["external_invariance"], float(np.linalg.norm(symbol(wave) @ v - v @ matrix))
        )
        errors["external_projection"] = max(
            errors["external_projection"], float(np.linalg.norm(projection @ v - v))
        )
        errors["orthogonality"] = max(
            errors["orthogonality"], float(np.linalg.norm(v.conj().T @ v - np.eye(dim)))
        )
        if not np.any(wave):
            errors["zero_conservation"] = float(np.linalg.norm(moments @ v))
    return {**errors, "passed": all(np.isfinite(x) and x <= 5e-12 for x in errors.values())}


def nested_groups(count):
    for a in range(count):
        for b in range(a, count):
            for c in range(b, count):
                for d in range(c, count):
                    yield a, b, c, d


def pair_cache(eigenvalues, dimensions):
    return {
        (a, b): np.multiply.outer(
            eigenvalues[b, : dimensions[b]], eigenvalues[a, : dimensions[a]]
        ).reshape(-1)
        for a in range(len(dimensions))
        for b in range(a, len(dimensions))
    }


def scalar_distance(group, waves, pairs, external, external_lookup):
    a, b, c, d = group
    wave = tuple(int(x) for x in waves[a] + waves[b] + waves[c] + waves[d])
    values = np.multiply.outer(pairs[c, d], pairs[a, b]).reshape(-1)
    output = external[external_lookup[wave]]
    return float(np.min(np.abs(output[:, None] - values[None, :])))


def scan(arrays, progress=None):
    dimensions, waves = arrays["block_dimensions"], arrays["block_waves"]
    pairs = pair_cache(arrays["block_eigenvalues"], dimensions)
    external = [
        e[:n]
        for e, n in zip(arrays["external_eigenvalues"], arrays["external_dimensions"], strict=True)
    ]
    lookup = {tuple(w): i for i, w in enumerate(arrays["external_waves"])}
    distances = np.empty(comb(len(dimensions) + 3, 4))
    completed = 0
    try:
        for ordinal, group in enumerate(nested_groups(len(dimensions))):
            distances[ordinal] = scalar_distance(group, waves, pairs, external, lookup)
            completed = ordinal + 1
            if progress and completed % 4096 == 0:
                progress(completed)
    except Exception as error:
        error.partial_distances = distances[:completed].copy()
        raise
    if progress:
        progress(len(distances))
    return distances


def bin_summary(distances):
    """Independently count/reduce the *primary* scores to audit exact selection."""
    if (
        distances.shape != (comb(81, 4),)
        or not np.isfinite(distances).all()
        or np.any(distances < 0)
    ):
        raise ValueError("full finite nonnegative score inventory required")
    waves = tuple(
        (x, y, z) for x in range(-1, 2) for y in range(-1, 2) for z in range(-1, 2) if x or y or z
    )
    counts, best = Counter(), {}
    for ordinal, group in enumerate(nested_groups(78)):
        copies = sorted((group.count(b) for b in set(group)), reverse=True)
        output = tuple(sum(waves[b // 3][j] for b in group) for j in range(3))
        output_sector = (
            "zero" if output == (0, 0, 0) else "selected" if output in waves else "other"
        )
        key = (tuple(copies), output_sector)
        counts[key] += 1
        candidate = (float(distances[ordinal]), ordinal, group)
        if key not in best or candidate[:2] < best[key][:2]:
            best[key] = candidate
    patterns = ((4,), (3, 1), (2, 2), (2, 1, 1), (1, 1, 1, 1))
    return [
        {
            "pattern": list(p),
            "sector": s,
            "count": counts[p, s],
            "minimum": None if (p, s) not in best else best[p, s][0],
            "ordinal": None if (p, s) not in best else best[p, s][1],
            "group": None if (p, s) not in best else list(best[p, s][2]),
        }
        for p in patterns
        for s in ("zero", "selected", "other")
    ]
