"""Q012g: evaluate sealed cubic Taylor fibers without projection or truncation.

The coefficient arrays are already monomial coefficients, not derivatives. This
module never solves for, averages, or repairs them. The grouped sparse engine is
also exercised by an independently specified, nontrivial invariant-graph map.
"""

from __future__ import annotations

from itertools import product
from numbers import Integral
from pathlib import Path

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as quadratic
from research import d3q27_cubic as cubic
from research import d3q27_refined_cubic as refined

EVALUATION_SEED = 2026090723
REAL_TOLERANCE = 1e-9
FIBER_KEYS = frozenset(("input_triples", "output_waves", "response", "forcing", "reduced"))


def real_coordinates(value: np.ndarray, dimension: int) -> np.ndarray:
    a = d3._real_array(value)
    if a.shape != (dimension,):
        raise ValueError(f"{dimension} real coordinates are required")
    return a


def checked_real(value: np.ndarray, label: str) -> tuple[np.ndarray, dict]:
    """Measure imaginary data before taking a real, independently owned copy."""
    value = np.asarray(value)
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{label}: nonfinite values cannot be realified")
    real_norm = float(np.linalg.norm(value.real))
    imaginary_norm = float(np.linalg.norm(value.imag))
    if not np.isfinite(real_norm) or not np.isfinite(imaginary_norm):
        raise ValueError(f"{label}: norm overflow cannot establish realness")
    scale = max(1.0, real_norm)
    audit = {
        "real_norm": real_norm,
        "imaginary_norm": imaginary_norm,
        "scaled_imaginary_norm": imaginary_norm / scale,
        "passed": imaginary_norm <= REAL_TOLERANCE * scale,
    }
    if not audit["passed"]:
        raise ValueError(f"{label}: imaginary norm {imaginary_norm} exceeds realification gate")
    return np.array(value.real, dtype=np.float64, order="C", copy=True), audit


class GroupedPolynomial:
    """Homogeneous monomial sum, grouped by known output support.

    Only stable row reordering is performed. All coefficients, including zero
    coefficients on the supplied support, are retained. Owned read-only copies
    prevent subsequent mutation of caller arrays from changing the evaluator.
    """

    def __init__(self, monomials, groups, coefficients, *, dimension: int, group_count: int):
        if any(
            isinstance(v, bool) or not isinstance(v, Integral) or v <= 0
            for v in (dimension, group_count)
        ):
            raise ValueError("dimension and group_count must be positive integers")
        indices, groups, coefficients = map(np.asarray, (monomials, groups, coefficients))
        if (
            indices.ndim != 2
            or indices.shape[1] < 1
            or indices.dtype.kind not in "iu"
            or np.any(indices < 0)
            or np.any(indices >= dimension)
        ):
            raise ValueError("monomial indices must be an in-range integer matrix")
        if (
            groups.shape != (len(indices),)
            or groups.dtype.kind not in "iu"
            or np.any(groups < 0)
            or np.any(groups >= group_count)
        ):
            raise ValueError("output groups must be an in-range integer vector")
        if (
            coefficients.ndim != 2
            or coefficients.shape[0] != len(indices)
            or coefficients.shape[1] < 1
            or coefficients.dtype.kind not in "iufc"
            or not np.all(np.isfinite(coefficients))
        ):
            raise ValueError("finite numeric coefficient rows must match the monomials")
        order = np.argsort(groups, kind="stable")
        self.indices = np.array(indices[order], dtype=np.int64, copy=True)
        self.coefficients = np.array(coefficients[order], dtype=np.complex128, copy=True)
        sorted_groups = groups[order]
        self.starts = (
            np.r_[0, np.flatnonzero(np.diff(sorted_groups)) + 1].astype(np.int64)
            if len(order)
            else np.empty(0, dtype=np.int64)
        )
        self.outputs = np.array(sorted_groups[self.starts], dtype=np.int64, copy=True)
        self.dimension, self.group_count = int(dimension), int(group_count)
        self.degree, self.width = indices.shape[1], coefficients.shape[1]
        for array in (self.indices, self.coefficients, self.starts, self.outputs):
            array.setflags(write=False)

    def evaluate(self, coordinates: np.ndarray) -> np.ndarray:
        z = np.asarray(coordinates, dtype=np.complex128)
        if z.shape != (self.dimension,) or not np.all(np.isfinite(z)):
            raise ValueError("finite complex coordinates of the registered dimension are required")
        result = np.zeros((self.group_count, self.width), dtype=np.complex128)
        if len(self.indices):
            with np.errstate(over="raise", invalid="raise"):
                monomials = np.prod(z[self.indices], axis=1)
                result[self.outputs] = np.add.reduceat(
                    self.coefficients * monomials[:, None], self.starts, axis=0
                )
        if not np.all(np.isfinite(result)):
            raise ValueError("nonfinite sparse polynomial value")
        return result

    def storage(self) -> dict:
        return {
            "monomial_rows": len(self.indices),
            "degree": self.degree,
            "coefficient_scalars": self.coefficients.size,
            "coefficient_bytes": self.coefficients.nbytes,
            "sparse_index_bytes": self.indices.nbytes + self.starts.nbytes + self.outputs.nbytes,
            "prepared_arrays": {
                name: quadratic.array_metadata(getattr(self, name))
                for name in ("indices", "coefficients", "starts", "outputs")
            },
        }


def manual_complex_coordinates(value: np.ndarray) -> np.ndarray:
    """Positive/negative wave pairs, independently of multiplication by T."""
    a = real_coordinates(value, 104)
    z = np.empty(104, dtype=np.complex128)
    for index, wave in enumerate(quadratic.POSITIVE_WAVES):
        positive = 4 * quadratic.WAVES.index(wave)
        negative = 4 * quadratic.WAVES.index(tuple(-v for v in wave))
        for component, partner in enumerate((0, 1, 3, 2)):
            real_index = 8 * index + 2 * component
            value = (a[real_index] + 1j * a[real_index + 1]) / np.sqrt(2)
            z[positive + component] = value
            z[negative + partner] = value.conjugate()
    return z


def manual_real_coordinates(value: np.ndarray) -> tuple[np.ndarray, dict]:
    """Use BOTH partners; taking real/imag of only the positive half hides errors."""
    z = np.asarray(value, dtype=np.complex128)
    if z.shape != (104,) or not np.all(np.isfinite(z)):
        raise ValueError("104 finite complex slots are required")
    a = np.empty(104, dtype=np.complex128)
    for index, wave in enumerate(quadratic.POSITIVE_WAVES):
        positive = 4 * quadratic.WAVES.index(wave)
        negative = 4 * quadratic.WAVES.index(tuple(-v for v in wave))
        for component, partner in enumerate((0, 1, 3, 2)):
            p, n = z[positive + component], z[negative + partner]
            offset = 8 * index + 2 * component
            a[offset] = (p + n) / np.sqrt(2)
            a[offset + 1] = (-1j * p + 1j * n) / np.sqrt(2)
    return checked_real(a, "manual reduced coordinates")


def validate_fibers(arrays: dict[str, np.ndarray]) -> dict:
    if set(arrays) != FIBER_KEYS:
        raise ValueError("the complete five-array cubic fiber archive is required")
    count = cubic.COLUMN_COUNT
    shapes = {
        "input_triples": (count, 3),
        "output_waves": (count, 3),
        "response": (count, 27),
        "forcing": (count, 27),
        "reduced": (count, 4),
    }
    for name, shape in shapes.items():
        value = np.asarray(arrays[name])
        dtype = np.dtype("int64" if name in ("input_triples", "output_waves") else "complex128")
        if value.shape != shape or value.dtype != dtype or not np.all(np.isfinite(value)):
            raise ValueError(f"{name}: invalid shape, dtype, or nonfinite coefficients")
    triples, waves = arrays["input_triples"], arrays["output_waves"]
    if np.any(triples < 0) or np.any(triples >= 104) or np.any(triples[:, :-1] > triples[:, 1:]):
        raise ValueError("ordered in-range i <= j <= k monomials are required")
    if len(np.unique(np.ravel_multi_index(triples.T, (104,) * 3))) != count:
        raise ValueError("duplicate or missing cubic monomials")
    expected_waves = np.asarray(quadratic.WAVES, dtype=np.int64)[triples // 4].sum(axis=1)
    if not np.array_equal(waves, expected_waves):
        raise ValueError("cubic output support violates the Fourier selection rule")
    selected = np.max(np.abs(waves), axis=1) <= 1
    selected &= np.any(waves != 0, axis=1)
    if np.any(arrays["reduced"][~selected] != 0):
        raise ValueError("nonzero reduced fibers outside the first shell cannot be dropped")
    return {
        "complete_monomials": count,
        "output_wave_count": len(np.unique(waves, axis=0)),
        "reduced_first_shell_rows": int(np.sum(selected)),
        "reduced_exact_zero_rows_omitted": int(np.sum(~selected)),
        "entries": {k: quadratic.array_metadata(v) for k, v in arrays.items()},
        "passed": True,
    }


def load_fibers(path: Path, expected: dict) -> tuple[dict, dict]:
    """Read a hash-pinned archive; no pickle, repair, missing-array filling, or write."""
    path = Path(path)
    if path.name != expected["filename"]:
        raise ValueError("fiber archive filename differs from sealed metadata")
    if path.stat().st_size != expected["bytes"] or refined.file_hash(path) != expected["sha256"]:
        raise ValueError("fiber archive byte seal failed")
    with np.load(path, allow_pickle=False) as archive:
        if len(archive.files) != len(FIBER_KEYS) or set(archive.files) != FIBER_KEYS:
            raise ValueError("missing, duplicate, or unexpected cubic fiber arrays")
        arrays = {name: archive[name] for name in archive.files}
    audit = validate_fibers(arrays)
    if audit["entries"] != expected["entries"]:
        raise ValueError("fiber archive array metadata differs from the sealed input")
    for value in arrays.values():
        value.setflags(write=False)
    return arrays, {"filename": path.name, "sha256": expected["sha256"], **audit}


class CubicChart:
    """All 104 real coordinates, the paired quadratic input, and the saved cubic jet."""

    def __init__(self, model: quadratic.QuadraticChart, arrays: dict):
        if (
            model.size not in cubic.SIZES
            or (model.omega, model.eta, model.power) != (1.5, 0.02, 2)
            or not np.array_equal(model.transform, quadratic.realification()[0])
        ):
            raise ValueError("Q012g requires the registered grid, modified map, and realification")
        self.input_audit = validate_fibers(arrays)
        self.quadratic = model
        self.waves, groups = np.unique(arrays["output_waves"], axis=0, return_inverse=True)
        self.slots = tuple(self.waves[:, axis] % model.size for axis in (2, 1, 0))
        self.response = GroupedPolynomial(
            arrays["input_triples"],
            groups,
            arrays["response"],
            dimension=104,
            group_count=len(self.waves),
        )
        self.forcing = GroupedPolynomial(
            arrays["input_triples"],
            groups,
            arrays["forcing"],
            dimension=104,
            group_count=len(self.waves),
        )
        wave_to_index = {wave: i for i, wave in enumerate(quadratic.WAVES)}
        output_slots = np.array([wave_to_index.get(tuple(w), -1) for w in arrays["output_waves"]])
        # validate_fibers verified exact zeros on EVERY excluded row, not a norm cutoff.
        selected = output_slots >= 0
        self.internal = GroupedPolynomial(
            arrays["input_triples"][selected],
            output_slots[selected],
            arrays["reduced"][selected],
            dimension=104,
            group_count=26,
        )
        self.waves.setflags(write=False)
        for slot in self.slots:
            slot.setflags(write=False)

    def cubic_fourier(self, value: np.ndarray, *, forcing: bool = False) -> np.ndarray:
        engine = self.forcing if forcing else self.response
        values = engine.evaluate(self.quadratic.complex_coordinates(value))
        spectrum = np.zeros(self.quadratic.base.shape, dtype=np.complex128)
        spectrum[self.slots] = values
        return spectrum

    def physical_with_audit(self, spectrum: np.ndarray) -> tuple[np.ndarray, dict]:
        if spectrum.shape != self.quadratic.base.shape or not np.all(np.isfinite(spectrum)):
            raise ValueError("finite spectrum on the registered grid is required")
        field = np.fft.ifftn(spectrum, axes=(0, 1, 2), norm="ortho")
        return checked_real(field, "cubic physical field")

    def cubic_field_with_audit(self, value: np.ndarray) -> tuple[np.ndarray, dict]:
        return self.physical_with_audit(self.cubic_fourier(value))

    def cubic_field(self, value: np.ndarray) -> np.ndarray:
        return self.cubic_field_with_audit(value)[0]

    def reduced_cubic_with_audit(self, value: np.ndarray) -> tuple[np.ndarray, dict]:
        z = self.quadratic.complex_coordinates(value)
        g = self.internal.evaluate(z).reshape(104)
        return checked_real(self.quadratic.transform.conj().T @ g, "cubic reduced coordinates")

    def reduced_cubic(self, value: np.ndarray) -> np.ndarray:
        return self.reduced_cubic_with_audit(value)[0]

    def embed_with_audit(self, value: np.ndarray, *, degree: int = 3) -> tuple[np.ndarray, dict]:
        if type(degree) is not int or degree not in (2, 3):
            raise ValueError("only the registered quadratic and cubic charts are supported")
        model = self.quadratic
        spectrum = model.linear_fourier(value) + model.quadratic_fourier(value)
        if degree == 3:
            spectrum += self.cubic_fourier(value)
        perturbation, audit = self.physical_with_audit(spectrum)
        return model.base + perturbation, audit

    def embed(self, value: np.ndarray, *, degree: int = 3) -> np.ndarray:
        return self.embed_with_audit(value, degree=degree)[0]

    def reduced_with_audit(self, value: np.ndarray, *, degree: int = 3) -> tuple[np.ndarray, dict]:
        if type(degree) is not int or degree not in (2, 3):
            raise ValueError("only the registered quadratic and cubic charts are supported")
        result = self.quadratic.reduced(value)
        audit = None
        if degree == 3:
            g, audit = self.reduced_cubic_with_audit(value)
            result = result + g
        if not np.all(np.isfinite(result)):
            raise ValueError("nonfinite reduced map value")
        return result, {"cubic_realification": audit}

    def reduced(self, value: np.ndarray, *, degree: int = 3) -> np.ndarray:
        return self.reduced_with_audit(value, degree=degree)[0]

    def storage(self) -> dict:
        engines = {
            name: getattr(self, name).storage() for name in ("response", "forcing", "internal")
        }
        return {
            "engines": engines,
            "coefficient_bytes": sum(v["coefficient_bytes"] for v in engines.values()),
            "sparse_index_bytes": sum(v["sparse_index_bytes"] for v in engines.values())
            + self.waves.nbytes
            + sum(slot.nbytes for slot in self.slots),
            "scope": "owned cubic evaluation and forcing-audit buffers; quadratic input, base field, caller archives, and transient contraction/FFT arrays excluded",
        }


def direct_cubic_sum(arrays: dict, value: np.ndarray, size: int) -> tuple[np.ndarray, np.ndarray]:
    """Row-by-row monomial reference, without T, sorting, or grouped reduction."""
    z = manual_complex_coordinates(value)
    h = np.zeros((size, size, size, 27), dtype=np.complex128)
    g = np.zeros(104, dtype=np.complex128)
    shell_indices = {wave: 4 * index for index, wave in enumerate(quadratic.WAVES)}
    for (i, j, k), wave, response, reduced in zip(
        arrays["input_triples"],
        arrays["output_waves"],
        arrays["response"],
        arrays["reduced"],
        strict=True,
    ):
        monomial = z[i] * z[j] * z[k]
        x, y, z_wave = wave
        h[z_wave % size, y % size, x % size] += response * monomial
        offset = shell_indices.get(tuple(wave))
        if offset is not None:
            g[offset : offset + 4] += reduced * monomial
    return h, g


def transformed_polynomial(terms: dict, transform: np.ndarray, *, complex_output: bool):
    """Expand explicit real monomials into conjugate slots, not sampled fitting.

    This is used for the manufactured map only. The LBM fibers are never changed.
    Binomial coefficients arise from adding repeated expansion terms; no generic
    derivative factorial is inserted in the common evaluation engine.
    """
    transform = np.asarray(transform, dtype=np.complex128)
    dimension = len(transform)
    if transform.shape != (dimension, dimension) or not np.all(np.isfinite(transform)):
        raise ValueError("a finite square realification transform is required")
    if np.linalg.norm(transform.conj().T @ transform - np.eye(dimension)) > 1e-12:
        raise ValueError("the manufactured transform must be unitary")
    if not terms:
        raise ValueError("explicit manufactured polynomial terms are required")
    degree = len(next(iter(terms)))
    widths = {np.asarray(coefficient).shape for coefficient in terms.values()}
    if degree < 1 or len(widths) != 1:
        raise ValueError("consistent manufactured polynomial degree and output width are required")
    width_shape = widths.pop()
    if (
        len(width_shape) != 1
        or width_shape[0] < 1
        or (complex_output and width_shape != (dimension,))
    ):
        raise ValueError("manufactured polynomial output dimension mismatch")
    expanded = {}
    inverse = transform.conj().T
    for indices, coefficient in terms.items():
        if len(indices) != degree or any(
            isinstance(i, bool) or not isinstance(i, Integral) or not 0 <= i < dimension
            for i in indices
        ):
            raise ValueError("invalid manufactured monomial indices")
        coefficient = d3._real_array(coefficient)
        vector = transform @ coefficient if complex_output else coefficient.astype(complex)
        supports = [np.flatnonzero(inverse[i] != 0) for i in indices]
        for slots in product(*supports):
            factor = np.prod([inverse[i, slot] for i, slot in zip(indices, slots, strict=True)])
            key = tuple(sorted(slots))
            expanded[key] = expanded.get(key, np.zeros_like(vector)) + vector * factor
    keys = sorted(expanded)
    return GroupedPolynomial(
        np.asarray(keys, dtype=np.int64),
        np.zeros(len(keys), dtype=np.int64),
        np.stack([expanded[k] for k in keys]),
        dimension=dimension,
        group_count=1,
    )


def manufactured_explicit(value: np.ndarray) -> dict[str, np.ndarray]:
    a0, a1, a2, a3 = a = real_coordinates(value, 4)
    linear = np.array(
        (
            0.64 * a0 - 0.48 * a1,
            0.48 * a0 + 0.64 * a1,
            0.42 * a2 + 0.56 * a3,
            -0.56 * a2 + 0.42 * a3,
        )
    )
    r2 = 0.01 * np.array((a0 * a1, a1 * a2, a2 * a3, a3 * a0))
    r3 = np.array((0.03 * a0**3, -0.02 * a1 * a2 * a3, 0.01 * a0**2 * a2, 0.015 * a0 * a1 * a3))
    h2 = 0.02 * np.array((a0 * a1, a1 * a2, a2 * a3))
    h3 = 0.01 * np.array(
        (a0**3 + 2 * a0 * a1 * a2 - a1 * a3**2, a0**2 * a2 + a1 * a2 * a3, a2**3 - a0 * a1**2)
    )
    return {"a": a, "linear": linear, "r2": r2, "r3": r3, "h2": h2, "h3": h3}


def manufactured_map(value: np.ndarray) -> np.ndarray:
    state = real_coordinates(value, 7)
    here = manufactured_explicit(state[:4])
    r = here["linear"] + here["r2"] + here["r3"]
    there = manufactured_explicit(r)
    return np.r_[
        r,
        np.array((0.2, 0.25, 0.3)) * (state[4:] - here["h2"] - here["h3"])
        + there["h2"]
        + there["h3"],
    ]


class ManufacturedChart:
    def __init__(self):
        self.transform = np.zeros((4, 4), dtype=np.complex128)
        for offset in (0, 2):
            self.transform[offset : offset + 2, offset : offset + 2] = np.array(
                ((1, 1j), (1, -1j))
            ) / np.sqrt(2)
        self.linear = np.diag((0.64 + 0.48j, 0.64 - 0.48j, 0.42 - 0.56j, 0.42 + 0.56j))
        terms = {
            "r2": {
                (0, 1): (0.01, 0, 0, 0),
                (1, 2): (0, 0.01, 0, 0),
                (2, 3): (0, 0, 0.01, 0),
                (0, 3): (0, 0, 0, 0.01),
            },
            "r3": {
                (0, 0, 0): (0.03, 0, 0, 0),
                (1, 2, 3): (0, -0.02, 0, 0),
                (0, 0, 2): (0, 0, 0.01, 0),
                (0, 1, 3): (0, 0, 0, 0.015),
            },
            "h2": {(0, 1): (0.02, 0, 0), (1, 2): (0, 0.02, 0), (2, 3): (0, 0, 0.02)},
            "h3": {
                (0, 0, 0): (0.01, 0, 0),
                (0, 1, 2): (0.02, 0, 0),
                (1, 3, 3): (-0.01, 0, 0),
                (0, 0, 2): (0, 0.01, 0),
                (1, 2, 3): (0, 0.01, 0),
                (2, 2, 2): (0, 0, 0.01),
                (0, 1, 1): (0, 0, -0.01),
            },
        }
        self.polynomials = {
            name: transformed_polynomial(terms[name], self.transform, complex_output=name[0] == "r")
            for name in terms
        }

    def parts(self, value: np.ndarray) -> dict[str, np.ndarray]:
        z = self.transform @ real_coordinates(value, 4)
        return {name: polynomial.evaluate(z)[0] for name, polynomial in self.polynomials.items()}

    def embed(self, value: np.ndarray, *, cubic_scale: float = 1.0) -> np.ndarray:
        a = real_coordinates(value, 4)
        parts = self.parts(a)
        h, _ = checked_real(parts["h2"] + cubic_scale * parts["h3"], "manufactured graph")
        return np.r_[a, h]

    def reduced(self, value: np.ndarray, *, cubic: bool = True) -> np.ndarray:
        a = real_coordinates(value, 4)
        parts = self.parts(a)
        result = self.linear @ (self.transform @ a) + parts["r2"]
        if cubic:
            result += parts["r3"]
        return checked_real(self.transform.conj().T @ result, "manufactured reduced map")[0]


def manufactured_controls() -> dict:
    model = ManufacturedChart()
    directions = np.random.default_rng(EVALUATION_SEED).standard_normal((8, 4))
    directions /= np.linalg.norm(directions, axis=1)[:, None]
    records = []
    for index, direction in enumerate(directions):
        a = 0.1 * direction
        explicit = manufactured_explicit(a)
        w_reference = np.r_[a, explicit["h2"] + explicit["h3"]]
        r_reference = explicit["linear"] + explicit["r2"] + explicit["r3"]
        w, r = model.embed(a), model.reduced(a)
        errors = {
            "embedding": float(
                np.linalg.norm(w - w_reference) / max(1, np.linalg.norm(w_reference))
            ),
            "reduced": float(np.linalg.norm(r - r_reference) / max(1, np.linalg.norm(r_reference))),
            "invariance": float(
                np.linalg.norm(manufactured_map(w) - model.embed(r))
                / max(1, np.linalg.norm(model.embed(r)))
            ),
        }
        records.append(
            {
                "direction_index": index,
                "a": a.tolist(),
                "errors": errors,
                "passed": max(errors.values()) <= 1e-12,
            }
        )
    a = np.array((0.08, -0.06, 0.04, -0.02))
    omitted = float(
        np.linalg.norm(
            manufactured_map(model.embed(a)) - model.embed(model.reduced(a, cubic=False))
        )
    )
    doubled = float(
        np.linalg.norm(
            manufactured_map(model.embed(a, cubic_scale=2))
            - model.embed(model.reduced(a), cubic_scale=2)
        )
    )
    negative = {
        "a": a.tolist(),
        "omitted_R3_defect": omitted,
        "doubled_H3_defect": doubled,
        "passed": omitted > 1e-10 and doubled > 1e-10,
    }
    return {
        "seed": EVALUATION_SEED,
        "directions": directions.tolist(),
        "amplitude": 0.1,
        "records": records,
        "negative_controls": negative,
        "passed": all(r["passed"] for r in records) and negative["passed"],
    }
