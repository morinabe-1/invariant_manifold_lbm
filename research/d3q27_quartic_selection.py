"""Q012h2 S0: full-scope spectral-distance selection, not quartic solves.

The shear blocks remain two-dimensional. Eigenvalues are used only to score
whole blocks; they never replace the invariant-plane coordinates of the chart.
"""

from collections import Counter
from itertools import combinations_with_replacement, islice, product
from math import comb, prod
from numbers import Integral

import numpy as np

from research import d3q27_chart as chart
from research import d3q27_damping as damping
from research import d3q27_quadratic as quadratic

SIZES = (17, 33, 65)
TUPLE_COUNT = comb(81, 4)
CHUNK_SIZE = 4096
PATTERNS = ((4,), (3, 1), (2, 2), (2, 1, 1), (1, 1, 1, 1))
SECTORS = ("zero", "selected", "other")
WAVES = tuple(w for w in product((-1, 0, 1), repeat=3) if any(w))
OUTPUT_WAVES = tuple(product(range(-4, 5), repeat=3))
MANDATORY = (0, 3, 6, 9)
SPECTRAL_KEYS = {
    "block_waves",
    "block_dimensions",
    "block_basis",
    "block_dynamics",
    "block_eigenvalues",
    "external_waves",
    "external_dimensions",
    "external_basis",
    "external_dynamics",
    "external_projection",
    "external_eigenvalues",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalized_group(group):
    group = tuple(group)
    require(
        len(group) == 4
        and all(isinstance(b, Integral) and not isinstance(b, bool) and 0 <= b < 78 for b in group),
        "four registered block indices required",
    )
    return tuple(sorted(map(int, group)))


def conjugate(group):
    return tuple(
        sorted(
            3 * WAVES.index(tuple(-v for v in WAVES[b // 3])) + (0, 2, 1)[b % 3]
            for b in normalized_group(group)
        )
    )


def group_wave(group):
    return tuple(sum(WAVES[b // 3][axis] for b in group) for axis in range(3))


def sector(wave):
    return "zero" if not any(wave) else "selected" if tuple(wave) in WAVES else "other"


def pattern(group):
    return tuple(sorted(Counter(group).values(), reverse=True))


def column_count(group):
    return prod(comb((2 if b % 3 == 0 else 1) + n - 1, n) for b, n in Counter(group).items())


def group_ordinal(group):
    group = normalized_group(group)
    ordinal, previous = 0, 0
    for slot, value in enumerate(group):
        ordinal += sum(comb(80 - i - slot, 3 - slot) for i in range(previous, value))
        previous = value
    return ordinal


def seed_groups():
    result = set()
    for b in range(78):
        c, d, e = (b + 1) % 78, (b + 2) % 78, (b + 3) % 78
        for row in ((b, b, b, b), (b, b, b, c), (b, b, c, c), (b, b, c, d), (b, c, d, e)):
            result.update((tuple(sorted(row)), conjugate(row)))
    require(len(result) == 650, "cyclic seed coverage changed")
    result.update((MANDATORY, conjugate(MANDATORY)))
    require(len(result) == 652, "mandatory seed coverage changed")
    return tuple(sorted(result))


def sorted_eigenvalues(matrix):
    values = np.linalg.eigvals(matrix)
    return values[np.lexsort((values.imag, values.real))]


def spectral_inputs(size):
    require(type(size) is int and size in SIZES, "registered grid required")
    frames, frame_audit = chart.paired_frames(size, 1.5)
    require(frame_audit["passed"] is True, "paired frame audit failed")
    blocks = [b for w in WAVES for b in frames[w].blocks]
    require(
        [(b.wave, b.label, b.dimension) for b in blocks]
        == [
            (w, label, dimension)
            for w in WAVES
            for label, dimension in (("shear", 2), ("acoustic_plus", 1), ("acoustic_minus", 1))
        ],
        "full 78-block inventory differs",
    )
    arrays = {
        "block_waves": np.array([b.wave for b in blocks], dtype=np.int64),
        "block_dimensions": np.array([b.dimension for b in blocks], dtype=np.int64),
        "block_basis": np.zeros((78, 27, 2), dtype=complex),
        "block_dynamics": np.zeros((78, 2, 2), dtype=complex),
        "block_eigenvalues": np.empty((78, 2), dtype=complex),
        "external_waves": np.array(OUTPUT_WAVES, dtype=np.int64),
        "external_dimensions": np.empty(729, dtype=np.int64),
        "external_basis": np.zeros((729, 27, 27), dtype=complex),
        "external_dynamics": np.zeros((729, 27, 27), dtype=complex),
        "external_projection": np.empty((729, 27, 27), dtype=complex),
        "external_eigenvalues": np.empty((729, 27), dtype=complex),
    }
    for index, block in enumerate(blocks):
        dim = block.dimension
        matrix = damping.wave_multiplier(block.wave, size, 0.02, 2) * block.dynamics
        arrays["block_basis"][index, :, :dim] = block.basis
        arrays["block_dynamics"][index, :dim, :dim] = matrix
        eigs = sorted_eigenvalues(matrix)
        # Duplicate a real eigenvalue of this sector, never introduce a zero/NaN.
        arrays["block_eigenvalues"][index] = eigs[0]
        arrays["block_eigenvalues"][index, :dim] = eigs
    maximum_error = 0.0
    for index, wave in enumerate(OUTPUT_WAVES):
        output = quadratic.external_sector(wave, size, 1.5, frames.get(wave))
        require(output.structural_error <= 5e-12, "external sector structure failed")
        maximum_error = max(maximum_error, output.structural_error)
        dim = output.basis.shape[1]
        matrix = damping.wave_multiplier(wave, size, 0.02, 2) * output.dynamics
        arrays["external_dimensions"][index] = dim
        arrays["external_basis"][index, :, :dim] = output.basis
        arrays["external_dynamics"][index, :dim, :dim] = matrix
        arrays["external_projection"][index] = output.projection
        eigs = sorted_eigenvalues(matrix)
        arrays["external_eigenvalues"][index] = eigs[0]
        arrays["external_eigenvalues"][index, :dim] = eigs
    validate_spectra(arrays)
    return arrays, {"frames": frame_audit, "maximum_external_structure_error": maximum_error}


def validate_spectra(arrays):
    require(isinstance(arrays, dict) and set(arrays) == SPECTRAL_KEYS, "spectral keys differ")
    shapes = {
        "block_waves": (78, 3),
        "block_dimensions": (78,),
        "block_basis": (78, 27, 2),
        "block_dynamics": (78, 2, 2),
        "block_eigenvalues": (78, 2),
        "external_waves": (729, 3),
        "external_dimensions": (729,),
        "external_basis": (729, 27, 27),
        "external_dynamics": (729, 27, 27),
        "external_projection": (729, 27, 27),
        "external_eigenvalues": (729, 27),
    }
    for name, shape in shapes.items():
        dtype = np.dtype("int64" if name.endswith(("waves", "dimensions")) else "complex128")
        value = arrays[name]
        require(
            isinstance(value, np.ndarray)
            and value.shape == shape
            and value.dtype == dtype
            and np.isfinite(value).all(),
            f"invalid spectral array: {name}",
        )
    require(
        np.array_equal(arrays["block_waves"], np.repeat(WAVES, 3, axis=0))
        and np.array_equal(arrays["block_dimensions"], np.tile([2, 1, 1], 26))
        and np.array_equal(arrays["external_waves"], OUTPUT_WAVES),
        "wave inventory changed",
    )
    expected = [23 if sector(w) != "other" else 27 for w in OUTPUT_WAVES]
    require(np.array_equal(arrays["external_dimensions"], expected), "external dimensions differ")
    for prefix in ("block", "external"):
        maximum = 2 if prefix == "block" else 27
        for index, dim in enumerate(arrays[prefix + "_dimensions"]):
            matrix = arrays[prefix + "_dynamics"][index]
            basis = arrays[prefix + "_basis"][index]
            eigs = arrays[prefix + "_eigenvalues"][index]
            require(
                np.all(matrix[dim:] == 0)
                and np.all(matrix[:, dim:] == 0)
                and np.all(basis[:, dim:] == 0),
                "nonzero matrix padding",
            )
            require(
                np.array_equal(eigs[:dim], sorted_eigenvalues(matrix[:dim, :dim])),
                "saved eigenvalues do not match their rounded matrix",
            )
            if dim < maximum:
                require(np.all(eigs[dim:] == eigs[0]), "invalid eigenvalue padding")


def tuple_chunks(count=78, chunk_size=CHUNK_SIZE):
    require(type(count) is int and 1 <= count <= 78, "invalid block count")
    require(type(chunk_size) is int and 1 <= chunk_size <= CHUNK_SIZE, "invalid chunk size")
    iterator = combinations_with_replacement(range(count), 4)
    while rows := tuple(islice(iterator, chunk_size)):
        yield np.array(rows, dtype=np.int64)


def distances_for_groups(block_eigenvalues, external_eigenvalues, waves, groups):
    """Left-associated products, with the first input index fastest."""
    values = np.ones((len(groups), 1), dtype=complex)
    for slot in range(4):
        values = (block_eigenvalues[groups[:, slot], :, None] * values[:, None, :]).reshape(
            len(groups), -1
        )
    output = waves[groups].sum(axis=1) + 4
    indices = 81 * output[:, 0] + 9 * output[:, 1] + output[:, 2]
    return np.min(np.abs(external_eigenvalues[indices, :, None] - values[:, None, :]), axis=(1, 2))


def scan(arrays, progress=None):
    validate_spectra(arrays)
    distances = np.empty(TUPLE_COUNT, dtype=float)
    start = 0
    try:
        for groups in tuple_chunks():
            stop = start + len(groups)
            distances[start:stop] = distances_for_groups(
                arrays["block_eigenvalues"],
                arrays["external_eigenvalues"],
                arrays["block_waves"],
                groups,
            )
            start = stop
            if progress:
                progress(start)
    except Exception as error:
        error.partial_distances = distances[:start].copy()
        raise
    require(
        start == TUPLE_COUNT and np.isfinite(distances).all() and (distances >= 0).all(),
        "incomplete or nonfinite distance scan",
    )
    return distances


def bin_summary(distances):
    require(
        isinstance(distances, np.ndarray)
        and distances.dtype == np.dtype("float64")
        and distances.shape == (TUPLE_COUNT,)
        and np.isfinite(distances).all()
        and (distances >= 0).all(),
        "full finite distance vector required",
    )
    counts = np.zeros((5, 3), dtype=np.int64)
    best = {}
    for ordinal, group in enumerate(combinations_with_replacement(range(78), 4)):
        key = (PATTERNS.index(pattern(group)), SECTORS.index(sector(group_wave(group))))
        counts[key] += 1
        candidate = (float(distances[ordinal]), ordinal, group)
        if key not in best or candidate[:2] < best[key][:2]:
            best[key] = candidate
    return [
        {
            "pattern": list(p),
            "sector": s,
            "count": int(counts[i, j]),
            "minimum": None if (i, j) not in best else best[i, j][0],
            "ordinal": None if (i, j) not in best else best[i, j][1],
            "group": None if (i, j) not in best else list(best[i, j][2]),
        }
        for i, p in enumerate(PATTERNS)
        for j, s in enumerate(SECTORS)
    ]


def select_groups(grid_bins):
    require(set(grid_bins) == set(SIZES), "all three grids required for common selection")
    reasons = {row: {"seed"} for row in seed_groups()}
    for size in SIZES:
        rows = grid_bins[size]
        require(
            len(rows) == 15
            and [(r["pattern"], r["sector"]) for r in rows]
            == [(list(p), s) for p in PATTERNS for s in SECTORS],
            "full pattern/sector bins required",
        )
        require(sum(row["count"] for row in rows) == TUPLE_COUNT, "full bin count required")
        for row in rows:
            require(
                set(row) == {"pattern", "sector", "count", "minimum", "ordinal", "group"}
                and type(row["count"]) is int
                and row["count"] >= 0,
                "invalid bin record",
            )
            if row["count"] == 0:
                require(
                    all(row[k] is None for k in ("minimum", "ordinal", "group")),
                    "nonempty representative of an empty bin",
                )
                continue
            group = normalized_group(row["group"])
            require(
                type(row["minimum"]) is float
                and np.isfinite(row["minimum"])
                and row["minimum"] >= 0
                and type(row["ordinal"]) is int
                and row["ordinal"] == group_ordinal(group),
                "invalid bin score/ordinal",
            )
            require(
                list(group) == row["group"]
                and list(pattern(group)) == row["pattern"]
                and sector(group_wave(group)) == row["sector"],
                "representative bin mismatch",
            )
            reason = f"n{size}:{','.join(map(str, row['pattern']))}:{row['sector']}"
            reasons.setdefault(group, set()).add(reason)
            reasons.setdefault(conjugate(group), set()).add(reason + ":conjugate")
    require(652 <= len(reasons) <= 742, "pilot selection count outside preregistration")
    return [
        {
            "group": list(g),
            "wave": list(group_wave(g)),
            "pattern": list(pattern(g)),
            "sector": sector(group_wave(g)),
            "columns": column_count(g),
            "operator_dimension": column_count(g)
            * (27 if sector(group_wave(g)) == "other" else 23),
            "reasons": sorted(reasons[g]),
        }
        for g in sorted(reasons)
    ]
