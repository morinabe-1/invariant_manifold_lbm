"""Degree-resolved full-map diagnosis, without fitting or changing the chart."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import d3q27_damping as damping
from research import q012d_d3q27_quadratic_chart as prior

ORIGINAL_AMPLITUDES = prior.AMPLITUDES
ASYMPTOTIC_AMPLITUDES = (0.001, 0.0005, 0.00025, 0.000125)
AMPLITUDES = ORIGINAL_AMPLITUDES + ASYMPTOTIC_AMPLITUDES[1:]
HOLDOUT_SEED = 2026090716


def gram(fields: tuple[np.ndarray, ...]) -> np.ndarray:
    """Real physical-space inner products, retaining signs of cross terms."""
    rows = np.stack([field.ravel() for field in fields])
    return rows @ rows.T


def norm(field: np.ndarray) -> float:
    return float(np.linalg.norm(field))


def momentum_quadratic(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    cj = np.einsum("...d,qd->...q", left, d3.VELOCITIES)
    ck = np.einsum("...d,qd->...q", right, d3.VELOCITIES)
    return d3.WEIGHTS * (4.5 * cj * ck - 1.5 * np.sum(left * right, axis=-1)[..., None])


def nonlinear_path_coefficients(
    v: np.ndarray, h: np.ndarray, omega: float, eta: float, power: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """t^3/t^4 of Phi(f*+t v+t^2 h), plus an independent derivative expression."""
    moments = d3.conserved_moment_matrix()
    first = np.einsum("aq,...q->...a", moments, v)
    second = np.einsum("aq,...q->...a", moments, h)
    r, s = first[..., 0, None], second[..., 0, None]
    q11 = momentum_quadratic(first[..., 1:], first[..., 1:])
    q12 = momentum_quadratic(first[..., 1:], second[..., 1:])
    q22 = momentum_quadratic(second[..., 1:], second[..., 1:])
    third = damping.apply_filter(d3.stream_periodic(omega * (2 * q12 - r * q11)), eta, power)
    fourth = damping.apply_filter(
        d3.stream_periodic(omega * (q22 - 2 * r * q12 + (r**2 - s) * q11)), eta, power
    )
    local_hessian = np.einsum("qab,...a,...b->...q", d3.equilibrium_hessian_at_rest(), first, first)
    # D^3 Phi[v,v,v]/6: rho multiplies the equilibrium Hessian BEFORE streaming.
    third_derivative_term = damping.apply_filter(
        d3.stream_periodic(-0.5 * omega * r * local_hessian), eta, power
    )
    third_independent = (
        damping.apply_filter(damping.mixed_hessian(v, h, omega), eta, power) + third_derivative_term
    )
    return third, fourth, third_independent


@dataclass
class DirectionTerms:
    direction: np.ndarray
    c2: np.ndarray
    c3: np.ndarray
    c4: np.ndarray
    composition_c3: np.ndarray
    composition_c4: np.ndarray
    audit: dict


def direction_terms(model: chart.QuadraticChart, u: np.ndarray) -> DirectionTerms:
    v, h = model.linear_field(u), model.quadratic_field(u)
    l = model.real_linear @ u
    reduced_quadratic = 0.5 * np.einsum("ijk,j,k->i", model.reduced_hessian, u, u, optimize=True)
    c2 = model.linear_field(reduced_quadratic)
    physical_c2 = (
        prior.linear_step(model, h)
        + 0.5
        * damping.apply_filter(damping.mixed_hessian(v, v, model.omega), model.eta, model.power)
        - model.quadratic_field(l)
    )
    c3, c4, independent_c3 = nonlinear_path_coefficients(v, h, model.omega, model.eta, model.power)
    composition_c3 = (
        model.quadratic_field(l + reduced_quadratic)
        - model.quadratic_field(l)
        - model.quadratic_field(reduced_quadratic)
    )
    composition_c4 = model.quadratic_field(reduced_quadratic)
    c2_error = damping.relative_error(physical_c2, c2)
    c3_error = damping.relative_error(c3, independent_c3)
    coefficient_gram = gram((c2, c3, c4))
    audit = {
        "coefficient_norms": [norm(c2), norm(c3), norm(c4)],
        "coefficient_gram": coefficient_gram.tolist(),
        "coefficient_hashes": {
            name: chart.array_metadata(value)["sha256"]
            for name, value in (("c2", c2), ("c3", c3), ("c4", c4))
        },
        "composition_cubic_norm": norm(composition_c3),
        "composition_quartic_norm": norm(composition_c4),
        "c3_to_c2_norm_ratio": norm(c3) / max(1e-14, norm(c2)),
        "c2_c3_cosine": float(coefficient_gram[0, 1] / max(1e-14, norm(c2) * norm(c3))),
        "independent_quadratic_equation_relative_error": c2_error,
        "independent_cubic_derivative_relative_error": c3_error,
        "passed": c2_error <= 1e-9 and c3_error <= 1e-10 and norm(c2) > 1e-6,
    }
    return DirectionTerms(u, c2, c3, c4, composition_c3, composition_c4, audit)


def signed_sample(
    model: chart.QuadraticChart, terms: DirectionTerms, amplitude: float, sign: int
) -> tuple[dict, np.ndarray]:
    t = sign * amplitude
    a = t * terms.direction
    la, ra = model.reduced(a, quadratic=False), model.reduced(a)
    state, mapped_linear, mapped_quadratic = model.embed(a), model.embed(la), model.embed(ra)
    advanced = prior.map_step(model, state)
    dropped, full = advanced - mapped_linear, advanced - mapped_quadratic
    c2, c3, c4 = t**2 * terms.c2, t**3 * terms.c3, t**4 * terms.c4
    composition3, composition4 = t**3 * terms.composition_c3, t**4 * terms.composition_c4
    p3, p4 = c2 + c3, c2 + c3 + c4
    floor = float(100 * np.finfo(float).eps * max(1, norm(model.base)))
    composition_error = norm(dropped - full - c2 - composition3 - composition4)
    minimum = min(
        float(value.min()) for value in (state, advanced, mapped_linear, mapped_quadratic)
    )
    finite = all(
        bool(np.all(np.isfinite(value)))
        for value in (state, advanced, mapped_linear, mapped_quadratic)
    )
    result = {
        "amplitude": amplitude,
        "sign": sign,
        "roundoff_floor": floor,
        "dropped_norm": norm(dropped),
        "full_norm": norm(full),
        "quadratic_prediction_norm": norm(c2),
        "cubic_prediction_norm": norm(p3),
        "quartic_prediction_norm": norm(p4),
        "leading_vector_relative_error": damping.relative_error(dropped, c2),
        "cubic_vector_relative_error": damping.relative_error(p3, dropped),
        "quartic_vector_relative_error": damping.relative_error(p4, dropped),
        "quartic_to_cubic_error_ratio": norm(dropped - p4) / max(1e-300, norm(dropped - p3)),
        "composition_term_order": ["full_defect", "quadratic", "chart_cubic", "chart_quartic"],
        "composition_gram": gram((full, c2, composition3, composition4)).tolist(),
        "composition_absolute_error": composition_error,
        "composition_passed": composition_error <= floor,
        "raw_defect_resolved": norm(dropped) > floor,
        "full_defect_resolved": norm(full) > floor,
        "finite": finite,
        "minimum_population": minimum,
        "finite_positive_passed": finite and minimum > 0,
    }
    return result, dropped


def fit_window(records: list[dict], amplitudes: tuple, sign: int, field: str) -> dict:
    selected = [
        next(row for row in records if row["amplitude"] == amplitude and row["sign"] == sign)
        for amplitude in amplitudes
    ]
    result = prior.order_record(
        amplitudes, [row[field] for row in selected], selected[0]["roundoff_floor"]
    )
    result["passed"] = result["above_roundoff_floor"] and 1.9 <= result["slope"] <= 2.1
    return result


def diagnose_direction(
    model: chart.QuadraticChart, u: np.ndarray, group: str, index: int, legacy: dict | None
) -> dict:
    terms = direction_terms(model, u)
    records, parity = [], []
    for amplitude in AMPLITUDES:
        plus, positive = signed_sample(model, terms, amplitude, 1)
        minus, negative = signed_sample(model, terms, amplitude, -1)
        records.extend((plus, minus))
        odd, even = (positive - negative) / 2, (positive + negative) / 2
        odd_error = damping.relative_error(odd, amplitude**3 * terms.c3)
        parity.append(
            {
                "amplitude": amplitude,
                "odd_defect_norm": norm(odd),
                "even_defect_norm": norm(even),
                "odd_cubic_relative_error": odd_error,
                "even_quadratic_relative_error": damping.relative_error(
                    even, amplitude**2 * terms.c2
                ),
                "even_quartic_relative_error": damping.relative_error(
                    even, amplitude**2 * terms.c2 + amplitude**4 * terms.c4
                ),
                "odd_above_roundoff_floor": norm(odd) > plus["roundoff_floor"],
                "registered_odd_test": amplitude in ORIGINAL_AMPLITUDES,
                "registered_odd_passed": None
                if amplitude not in ORIGINAL_AMPLITUDES
                else odd_error <= 0.001 and norm(odd) > plus["roundoff_floor"],
            }
        )
    fits = {}
    for sign, label in ((1, "positive"), (-1, "negative")):
        fits[label] = {
            "original_raw": fit_window(records, ORIGINAL_AMPLITUDES, sign, "dropped_norm"),
            "original_cubic_prediction": fit_window(
                records, ORIGINAL_AMPLITUDES, sign, "cubic_prediction_norm"
            ),
            "original_quartic_prediction": fit_window(
                records, ORIGINAL_AMPLITUDES, sign, "quartic_prediction_norm"
            ),
            "asymptotic_raw": fit_window(records, ASYMPTOTIC_AMPLITUDES, sign, "dropped_norm"),
        }
    legacy_check = None
    if legacy is not None:
        replayed = {"direction_index": index, **prior.residual_direction(model, u, drop_g=True)}
        current = fits["positive"]["original_raw"]
        legacy_check = {
            "full_prior_record": replayed,
            "passed": replayed == legacy and current == legacy["omitted_reduced_quadratic"],
        }
    original = [r for r in records if r["amplitude"] in ORIGINAL_AMPLITUDES]
    vector_prediction = all(
        r["cubic_vector_relative_error"] <= 0.02 and r["quartic_vector_relative_error"] <= 0.001
        for r in original
    )
    legacy_slope_prediction = None
    if legacy is not None:
        positive = fits["positive"]
        raw, cubic, quartic = (
            positive[key]
            for key in ("original_raw", "original_cubic_prediction", "original_quartic_prediction")
        )
        legacy_slope_prediction = {
            "cubic_slope_error": abs(cubic["slope"] - raw["slope"]),
            "quartic_slope_error": abs(quartic["slope"] - raw["slope"]),
            "passed": abs(cubic["slope"] - raw["slope"]) <= 0.01
            and abs(quartic["slope"] - raw["slope"]) <= 0.001
            and raw["passed"] == cubic["passed"] == quartic["passed"],
        }
    asymptotic = all(row["asymptotic_raw"]["passed"] for row in fits.values()) and all(
        r["leading_vector_relative_error"] <= 0.05
        for r in records
        if r["amplitude"] == ASYMPTOTIC_AMPLITUDES[-1]
    )
    return {
        "group": group,
        "direction_index": index,
        "direction": u.tolist(),
        "coefficient_audit": terms.audit,
        "samples": records,
        "parity": parity,
        "fits": fits,
        "legacy_reproduction": legacy_check,
        "legacy_slope_prediction": legacy_slope_prediction,
        "gates": {
            "independent_nonzero_coefficients": terms.audit["passed"],
            "exact_chart_composition": all(r["composition_passed"] for r in records),
            "original_window_vector_prediction": vector_prediction,
            "odd_part_independent_cubic": all(
                r["registered_odd_passed"] for r in parity if r["registered_odd_test"]
            ),
            "asymptotic_quadratic_behavior": asymptotic,
            "finite_positive_samples": all(r["finite_positive_passed"] for r in records),
        },
        "asymptotic_resolved": all(
            row["asymptotic_raw"]["above_roundoff_floor"] for row in fits.values()
        ),
    }
