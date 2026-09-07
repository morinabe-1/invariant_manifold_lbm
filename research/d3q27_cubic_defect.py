"""Q012g3 directional defect profiles for the unchanged, filtered D3Q27 map.

This module evaluates existing jets. It never solves, projects, or removes their
low-degree residuals. The independent arm uses explicit degree combinations,
multinomial inverse coefficients and the equilibrium Hessian bilinear form.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from math import factorial

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as quadratic
from research import d3q27_cubic_chart as cubic
from research import d3q27_damping as damping
from research import polynomial_path as poly

ORDER = 9
ARMS = ("primary", "independent")


def _arm(arm):
    if arm not in ARMS:
        raise ValueError("arm must be primary or independent")


def _degree(degree):
    if type(degree) is not int or degree not in (2, 3):
        raise ValueError("only degree 2 or 3 is registered")


def _fields(values):
    fields = tuple(np.asarray(v) for v in values)
    if len(fields) not in (3, 4):
        raise ValueError("a degree 2 or 3 physical path, including its constant, is required")
    shape = fields[0].shape
    if len(shape) != 4 or shape[-1] != 27 or min(shape[:3]) < 1:
        raise ValueError("physical path fields must have shape (nz, ny, nx, 27)")
    if any(v.shape != shape or v.dtype != np.float64 or not np.all(np.isfinite(v)) for v in fields):
        raise ValueError("matching finite binary64 physical fields are required")
    return fields


def norm(value):
    result = float(np.linalg.norm(value))
    if not np.isfinite(result):
        raise ValueError("nonfinite norm cannot establish a diagnostic bound")
    return result


def metadata(value):
    return {**quadratic.array_metadata(value), "norm": norm(value)}


def horner(fields, parameter):
    """Evaluate a sequence without stacking all large physical fields."""
    if isinstance(parameter, bool) or not np.isscalar(parameter) or not np.isfinite(parameter):
        raise ValueError("finite real scalar path parameter required")
    if np.iscomplexobj(parameter):
        raise ValueError("physical path parameter must be real")
    if not len(fields):
        raise ValueError("empty coefficient sequence")
    out = np.zeros_like(fields[0])
    with np.errstate(over="raise", invalid="raise"):
        for field in reversed(fields):
            out = out * parameter + field
    if not np.all(np.isfinite(out)):
        raise ValueError("nonfinite physical path value")
    return out


def inverse_multinomial(rho, order=ORDER):
    """Closed multinomial sum for a degree <= 3 denominator; no recurrence."""
    rho = np.asarray(rho)
    if rho.ndim < 1 or not 1 <= len(rho) <= 4 or rho.dtype != np.float64:
        raise ValueError("one to four binary64 density coefficients required")
    if type(order) is not int or order < 0 or not np.all(np.isfinite(rho)) or np.any(rho[0] == 0):
        raise ValueError("finite density with nonzero constant and nonnegative order required")
    result = []
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        ratios = [rho[j] / rho[0] if j < len(rho) else np.zeros_like(rho[0]) for j in (1, 2, 3)]
        for n in range(order + 1):
            coefficient = np.zeros_like(rho[0])
            for i in range(n + 1):
                for j in range(n // 2 + 1):
                    remainder = n - i - 2 * j
                    if remainder < 0 or remainder % 3:
                        continue
                    k = remainder // 3
                    multinomial = factorial(i + j + k) // (
                        factorial(i) * factorial(j) * factorial(k)
                    )
                    coefficient += (
                        (-1) ** (i + j + k)
                        * multinomial
                        * ratios[0] ** i
                        * ratios[1] ** j
                        * ratios[2] ** k
                        / rho[0]
                    )
            if not np.all(np.isfinite(coefficient)):
                raise ValueError("nonfinite inverse coefficient")
            result.append(coefficient)
    return tuple(result)


def lift_engine(engine, coordinate_path, *, arm):
    """Lift a sealed GroupedPolynomial, without changing its coefficient rows."""
    _arm(arm)
    z = np.asarray(coordinate_path)
    if (
        z.ndim != 2
        or z.shape[0] < 1
        or z.shape[1] != engine.dimension
        or z.dtype.kind not in "fc"
        or not np.all(np.isfinite(z))
    ):
        raise ValueError("finite real/complex coordinate coefficient matrix required")
    counts = np.diff(np.r_[engine.starts, len(engine.indices)])
    groups = np.repeat(engine.outputs, counts)
    if arm == "primary":
        return poly.homogeneous_composition(
            engine.indices, groups, engine.coefficients, z, group_count=engine.group_count
        )
    result = np.zeros(
        ((len(z) - 1) * engine.degree + 1, engine.group_count, engine.width), dtype=complex
    )
    with np.errstate(over="raise", invalid="raise"):
        for powers in product(range(len(z)), repeat=engine.degree):
            weights = np.ones(len(engine.indices), dtype=complex)
            for slot, power in enumerate(powers):
                weights *= z[power, engine.indices[:, slot]]
            if len(engine.indices):
                result[sum(powers), engine.outputs] += np.add.reduceat(
                    engine.coefficients * weights[:, None], engine.starts, axis=0
                )
    if not np.all(np.isfinite(result)):
        raise ValueError("nonfinite independently lifted monomial")
    return result


def physical_path(model, direction, degree):
    _degree(degree)
    q = model.quadratic
    u = cubic.real_coordinates(direction, q.real_linear.shape[0])
    fields = [q.base, q.linear_field(u), q.quadratic_field(u)]
    reduced = [
        np.zeros_like(u),
        q.real_linear @ u,
        0.5 * np.einsum("ijk,j,k->i", q.reduced_hessian, u, u, optimize=True),
    ]
    if degree == 3:
        fields.append(model.cubic_field(u))
        reduced.append(model.reduced_cubic(u))
    return _fields(fields), np.asarray(reduced)


@dataclass
class CompositionPath:
    model: object
    waves: np.ndarray
    coefficients: np.ndarray

    def physical(self, coefficients):
        q = self.model.quadratic
        spectrum = np.zeros_like(q.base, dtype=complex)
        slots = tuple(self.waves[:, axis] % q.size for axis in (2, 1, 0))
        spectrum[slots] = coefficients
        return self.model.physical_with_audit(spectrum)

    def coefficient(self, degree):
        if degree == 0:
            if np.any(self.coefficients[0] != 0):
                raise ValueError("composition has a nonzero constant reduced coordinate")
            return self.model.quadratic.base, {"passed": True, "constant_is_original_base": True}
        return self.physical(self.coefficients[degree])

    def evaluate(self, parameter):
        perturbation, audit = self.physical(poly.evaluate(self.coefficients, parameter))
        return self.model.quadratic.base + perturbation, audit


def composition_path(model, reduced, degree, *, arm):
    _degree(degree)
    _arm(arm)
    q = model.quadratic
    reduced = np.asarray(reduced)
    if (
        reduced.shape != (degree + 1, q.real_linear.shape[0])
        or reduced.dtype != np.float64
        or not np.all(np.isfinite(reduced))
        or np.any(reduced[0] != 0)
    ):
        raise ValueError("registered real reduced path with an exact zero constant required")
    z = np.stack([q.complex_coordinates(v) for v in reduced])
    qwaves, groups = np.unique(q.output_waves, axis=0, return_inverse=True)
    blocks = [np.asarray(quadratic.WAVES), qwaves]
    if degree == 3:
        blocks.append(model.waves)
    waves = np.unique(np.vstack(blocks), axis=0)
    if q.size <= 2 * int(np.max(np.abs(waves))):
        raise ValueError("composition support aliases on this synthetic grid")
    lookup = {tuple(w): i for i, w in enumerate(waves)}
    result = np.zeros((ORDER + 1, len(waves), 27), dtype=complex)
    slots = tuple(waves[:, axis] % q.size for axis in (2, 1, 0))
    for n, coordinates in enumerate(reduced):
        full_linear = q.linear_fourier(coordinates)
        result[n] += full_linear[slots]
        del full_linear
    engine = cubic.GroupedPolynomial(
        q.input_pairs, groups, q.hessian_fibers, dimension=z.shape[1], group_count=len(qwaves)
    )
    second = lift_engine(engine, z, arm=arm)
    result[: len(second), [lookup[tuple(w)] for w in qwaves]] += second
    if degree == 3:
        third = lift_engine(model.response, z, arm=arm)
        result[: len(third), [lookup[tuple(w)] for w in model.waves]] += third
    return CompositionPath(model, waves, result)


def _numerator_coefficients(momentum, arm):
    degree = len(momentum) - 1
    shape = momentum.shape[1:-1] + (27,)
    result = []
    if arm == "primary":
        projections = [np.einsum("...d,qd->...q", j, d3.VELOCITIES) for j in momentum]
    else:
        hessian = d3.equilibrium_hessian_at_rest()[:, 1:, 1:]
    with np.errstate(over="raise", invalid="raise"):
        for n in range(2 * degree + 1):
            value = np.zeros(shape)
            for i in range(max(0, n - degree), min(n, degree) + 1):
                j = n - i
                if arm == "primary":
                    value += (
                        4.5 * projections[i] * projections[j]
                        - 1.5 * np.sum(momentum[i] * momentum[j], axis=-1)[..., None]
                    )
                else:
                    value += 0.5 * np.einsum(
                        "qij,...i,...j->...q", hessian, momentum[i], momentum[j]
                    )
            result.append(value)
    return tuple(result)


@dataclass
class LocalExpansion:
    fields: tuple
    rho: np.ndarray
    momentum: np.ndarray
    quotient: tuple
    remainder: tuple
    arm: str
    audit: dict

    def equilibrium_coefficient(self, n):
        if n < len(self.rho):
            linear = self.rho[n, ..., None] + 3 * np.einsum(
                "...d,qd->...q", self.momentum[n], d3.VELOCITIES
            )
        else:
            linear = np.zeros_like(self.fields[0])
        if self.arm == "primary":
            return d3.WEIGHTS * (linear + self.quotient[n])
        return d3.WEIGHTS * linear + self.quotient[n]

    def mapped_coefficient(self, n, omega, eta, power):
        value = self.fields[n] if n < len(self.fields) else np.zeros_like(self.fields[0])
        collision = value + omega * (self.equilibrium_coefficient(n) - value)
        return damping.apply_filter(d3.stream_periodic(collision), eta, power)

    def tail(self, parameter, omega, eta, power):
        density = horner(self.rho, parameter)
        if np.any(density <= 0) or not np.all(np.isfinite(density)):
            raise ValueError("nonpositive reconstructed local density")
        value = omega * horner(self.remainder, parameter) / density[..., None]
        if self.arm == "primary":
            value *= d3.WEIGHTS
        return damping.apply_filter(d3.stream_periodic(value), eta, power)


def local_expansion(fields, *, arm):
    _arm(arm)
    fields = _fields(fields)
    moments = [d3.macroscopic(v) for v in fields]
    rho = np.stack([v[0] for v in moments])
    momentum = np.stack([v[1] for v in moments])
    if np.any(rho[0] <= 0):
        raise ValueError("positive constant density is required for the physical path")
    numerator = _numerator_coefficients(momentum, arm)
    quotient = [np.empty_like(fields[0]) for _ in range(ORDER + 1)]
    if arm == "primary":
        # Pointwise population slices have identical arithmetic to full-tensor
        # division, without the frozen generic routine's large temporary copies.
        for population in range(27):
            num = np.stack([v[..., population] for v in numerator])
            divided = poly.quotient(num, rho, order=ORDER)
            for n, coefficient in enumerate(divided):
                quotient[n][..., population] = coefficient
    else:
        inverse = inverse_multinomial(rho)
        for n in range(ORDER + 1):
            quotient[n].fill(0.0)
            for i in range(min(n + 1, len(numerator))):
                quotient[n] += numerator[i] * inverse[n - i][..., None]
    remainder = []
    # Keep every coefficient, including the nominally cancelling low orders.
    with np.errstate(over="raise", invalid="raise"):
        for n in range(ORDER + len(rho)):
            coefficient = numerator[n].copy() if n < len(numerator) else np.zeros_like(fields[0])
            for j in range(max(0, n - ORDER), min(n + 1, len(rho))):
                coefficient -= rho[j, ..., None] * quotient[n - j]
            remainder.append(coefficient)
    audit = {
        "rho": metadata(rho),
        "momentum": metadata(momentum),
        "constant_density_range": [float(rho[0].min()), float(rho[0].max())],
        "constant_momentum_component_ranges": [
            [float(momentum[0, ..., j].min()), float(momentum[0, ..., j].max())] for j in range(3)
        ],
        "numerator": [metadata(v) for v in numerator],
        "quotient": [metadata(v) for v in quotient],
        "remainder": [metadata(v) for v in remainder],
        "numerator_has_population_weights": arm == "independent",
    }
    return LocalExpansion(fields, rho, momentum, tuple(quotient), tuple(remainder), arm, audit)


@dataclass
class DefectProfile:
    model: object
    degree: int
    fields: tuple
    reduced: np.ndarray
    composition: CompositionPath
    local: LocalExpansion
    coefficients: tuple
    gram: np.ndarray
    audit: dict

    def evaluate(self, parameter):
        q = self.model.quadratic
        state = horner(self.fields, parameter)
        composed, realification = self.composition.evaluate(parameter)
        prediction = horner(self.coefficients, parameter)
        tail = self.local.tail(parameter, q.omega, q.eta, q.power)
        defect = prediction + tail
        return {
            "W_path": state,
            "R_path": poly.evaluate(self.reduced, parameter),
            "W_R_path": composed,
            "P9": prediction,
            "tail": tail,
            "defect_reconstructed": defect,
            "Phi_reconstructed": composed + defect,
        }, realification


def build_profile(model, direction, degree, *, arm="primary"):
    _arm(arm)
    fields, reduced = physical_path(model, direction, degree)
    composition = composition_path(model, reduced, degree, arm=arm)
    local = local_expansion(fields, arm=arm)
    q = model.quadratic
    coefficients, map_audits, composition_audits, reals = [], [], [], []
    for n in range(ORDER + 1):
        mapped = local.mapped_coefficient(n, q.omega, q.eta, q.power)
        composed, realification = composition.coefficient(n)
        coefficients.append(mapped - composed)
        map_audits.append(metadata(mapped))
        composition_audits.append(metadata(composed))
        reals.append(realification)
    gram = np.empty((ORDER + 1, ORDER + 1))
    for i in range(ORDER + 1):
        for j in range(i + 1):
            gram[i, j] = gram[j, i] = float(np.vdot(coefficients[i], coefficients[j]))
    audit = {
        "degree": degree,
        "arm": arm,
        "direction": np.asarray(direction).tolist(),
        "state_path": [metadata(v) for v in fields],
        "reduced_path": metadata(reduced),
        "reduced_path_values": reduced.tolist(),
        "compact_composition_waves": quadratic.array_metadata(composition.waves),
        "compact_composition": metadata(composition.coefficients),
        "local": local.audit,
        "mapped_coefficients": map_audits,
        "composition_coefficients": composition_audits,
        "composition_realification": reals,
        "defect_coefficients": [metadata(v) for v in coefficients],
        "gram": gram.tolist(),
    }
    return DefectProfile(
        model, degree, fields, reduced, composition, local, tuple(coefficients), gram, audit
    )


def compare_profiles(primary, independent):
    """Full-vector arm comparison before discarding large coefficient fields."""
    if (
        primary.degree != independent.degree
        or primary.local.arm != "primary"
        or independent.local.arm != "independent"
        or primary.audit["direction"] != independent.audit["direction"]
    ):
        raise ValueError("matching primary and independent profiles are required")
    rows = []

    def compare(name, left, right):
        if left.shape != right.shape or left.dtype != right.dtype:
            raise ValueError("independent coefficient arrays have different shape/dtype")
        difference = norm(left - right)
        reference = norm(right)
        tolerance = 1e-10 * max(1.0, reference)
        rows.append(
            {
                "name": name,
                "primary": quadratic.array_metadata(left),
                "independent": quadratic.array_metadata(right),
                "difference_norm": difference,
                "reference_norm": reference,
                "tolerance": tolerance,
                "passed": difference <= tolerance,
            }
        )

    for n, (left, right) in enumerate(zip(primary.fields, independent.fields, strict=True)):
        compare(f"v{n}", left, right)
    compare("reduced_path", primary.reduced, independent.reduced)
    compare("rho", primary.local.rho, independent.local.rho)
    compare("momentum", primary.local.momentum, independent.local.momentum)
    q = primary.model.quadratic
    other = independent.model.quadratic
    if (q.omega, q.eta, q.power) != (other.omega, other.eta, other.power):
        raise ValueError("independent profiles must use the same physical map")
    for n in range(ORDER + 1):
        compare(
            f"mapped{n}",
            primary.local.mapped_coefficient(n, q.omega, q.eta, q.power),
            independent.local.mapped_coefficient(n, q.omega, q.eta, q.power),
        )
        compare(
            f"composed{n}",
            primary.composition.coefficient(n)[0],
            independent.composition.coefficient(n)[0],
        )
        compare(f"C{n}", primary.coefficients[n], independent.coefficients[n])
    return {
        "rows": rows,
        "full_vector_comparisons": len(rows),
        "passed": all(r["passed"] for r in rows),
    }


def sample_diagnostics(profile, parameter, original_fields):
    """Numerical reconstruction and every truncated vector, without old-case relabeling."""
    q = profile.model.quadratic
    for key in ("W", "Phi_W", "W_R"):
        field = np.asarray(original_fields[key])
        if (
            field.shape != q.base.shape
            or field.dtype != np.float64
            or not np.all(np.isfinite(field))
        ):
            raise ValueError("original comparison fields must match the finite binary64 grid")
    values, realification = profile.evaluate(parameter)
    floor = float(100 * np.finfo(float).eps * max(1.0, norm(q.base)))
    raw = original_fields["Phi_W"] - original_fields["W_R"]
    raw_norm = norm(raw)
    mapping = {"W_path": "W", "W_R_path": "W_R", "Phi_reconstructed": "Phi_W"}
    errors = {key: norm(values[key] - original_fields[target]) for key, target in mapping.items()}
    errors["defect_reconstructed"] = norm(values["defect_reconstructed"] - raw)
    partial = np.zeros_like(q.base)
    truncations = []
    for n, coefficient in enumerate(profile.coefficients):
        partial += parameter**n * coefficient
        if n >= profile.degree + 1:
            vector_norm, difference = norm(partial), norm(partial - raw)
            powers = parameter ** np.arange(n + 1)
            by_gram = float(powers @ profile.gram[: n + 1, : n + 1] @ powers)
            tolerance = 1e-9 * max(floor**2, vector_norm**2)
            truncations.append(
                {
                    "degree": n,
                    "norm": vector_norm,
                    "vector_difference_norm": difference,
                    "relative_vector_error": difference / raw_norm if raw_norm > 0 else None,
                    "gram_norm_squared": by_gram,
                    "direct_norm_squared": vector_norm**2,
                    "gram_error": abs(by_gram - vector_norm**2),
                    "gram_tolerance": tolerance,
                    "gram_passed": bool(
                        by_gram >= 0 and abs(by_gram - vector_norm**2) <= tolerance
                    ),
                }
            )
    powers = parameter ** np.arange(ORDER + 1)
    weighted = profile.gram * np.outer(powers, powers)
    cross = 2 * np.triu(weighted, k=1)
    groups = (
        (0, profile.degree + 1),
        (profile.degree + 1, profile.degree + 2),
        (profile.degree + 2, ORDER + 1),
    )
    group_norms = []
    for start, stop in groups:
        contribution = np.zeros_like(q.base)
        for n in range(start, stop):
            contribution += powers[n] * profile.coefficients[n]
        group_norms.append(norm(contribution))
    p9_error = norm(values["P9"] - raw)
    return {
        "parameter": float(parameter),
        "degree": profile.degree,
        "roundoff_floor": floor,
        "raw_defect_norm": raw_norm,
        "raw_resolved": raw_norm > floor,
        "reconstruction_errors": errors,
        "H1_reconstruction_passed": all(v <= floor for v in errors.values()),
        "P9_norm": norm(values["P9"]),
        "P9_vector_difference_norm": p9_error,
        "P9_vector_relative_error": p9_error / raw_norm if raw_norm > 0 else None,
        "P9_vector_passed": bool(raw_norm > floor and p9_error <= 1e-3 * raw_norm),
        "tail_norm": norm(values["tail"]),
        "truncations": truncations,
        "group_order": ["low_0_to_d", "leading_d_plus_1", "higher_d_plus_2_to_9"],
        "group_contribution_norms": group_norms,
        "weighted_gram": weighted.tolist(),
        "signed_cross_terms": cross.tolist(),
        "composition_realification": realification,
        "reconstructed_reduced_coordinates": values["R_path"].tolist(),
        "reconstruction_fields": {k: metadata(v) for k, v in values.items()},
    }
