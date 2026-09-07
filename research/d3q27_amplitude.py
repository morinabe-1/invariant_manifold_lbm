"""Q012e rational tails and same-initial-state finite-time comparisons."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import d3q27_damping as damping
from research import d3q27_negative_control as degree
from research import q012d_d3q27_quadratic_chart as prior

AMPLITUDES = (0.008, 0.032, 0.128, 0.512, 1.0, 2.0, 4.0)
SEEDS = {"calibration": 2026090717, "holdout": 2026090718}
STEPS = 64
REPLAY_CASES = (
    ("calibration", 0, 0.008, 1),
    ("calibration", 0, 0.512, -1),
    ("holdout", 0, 0.032, 1),
    ("holdout", 0, 2.0, -1),
)


def moments(field: np.ndarray) -> np.ndarray:
    return np.einsum("aq,...q->...a", d3.conserved_moment_matrix(), field)


def macro_norm(moment_field: np.ndarray) -> float:
    return float(
        np.sqrt(np.sum(moment_field[..., 0] ** 2) + 3 * np.sum(moment_field[..., 1:] ** 2))
    )


def ratio(numerator: float, denominator: float, floor: float) -> float | None:
    return numerator / denominator if denominator > floor else None


@dataclass
class RationalPath:
    r: np.ndarray
    s: np.ndarray
    a2: np.ndarray
    a3: np.ndarray
    a4: np.ndarray

    def density(self, t: float) -> np.ndarray:
        return 1 + t * self.r + t**2 * self.s

    def tail(self, t: float) -> np.ndarray:
        rho = self.density(t)
        if np.any(rho <= 0):
            raise ValueError("nonpositive rational-path density")
        return -(t**5) * (self.r * self.a4 + self.s * self.a3 + t * self.s * self.a4) / rho


def rational_path(v: np.ndarray, h: np.ndarray) -> RationalPath:
    first, second = moments(v), moments(h)
    r, s = first[..., :1], second[..., :1]
    a2 = degree.momentum_quadratic(first[..., 1:], first[..., 1:])
    q12 = degree.momentum_quadratic(first[..., 1:], second[..., 1:])
    q22 = degree.momentum_quadratic(second[..., 1:], second[..., 1:])
    return RationalPath(r, s, a2, 2 * q12 - r * a2, q22 - 2 * r * q12 + (r**2 - s) * a2)


@dataclass
class PathTerms:
    u: np.ndarray
    local: RationalPath
    c3: np.ndarray
    c4: np.ndarray
    d0: np.ndarray
    d1: np.ndarray
    d2: np.ndarray
    audit: dict


def path_terms(model: chart.QuadraticChart, u: np.ndarray) -> PathTerms:
    known = degree.direction_terms(model, u)
    v, h = model.linear_field(u), model.quadratic_field(u)
    l = model.real_linear @ u
    c3, c4 = known.c3 - known.composition_c3, known.c4 - known.composition_c4
    d0 = prior.map_step(model, model.base) - model.base
    d1 = prior.linear_step(model, v) - model.linear_field(l)
    d2 = (
        prior.linear_step(model, h)
        + 0.5
        * damping.apply_filter(damping.mixed_hessian(v, v, model.omega), model.eta, model.power)
        - model.quadratic_field(l)
        - known.c2
    )
    fields = {"c3": c3, "c4": c4, "d0": d0, "d1": d1, "d2": d2}
    audit = {
        "previous_independent_coefficient_audit": known.audit,
        "full_defect_coefficient_norms": {
            name: degree.norm(value) for name, value in fields.items()
        },
        "full_defect_coefficient_hashes": {
            name: chart.array_metadata(value)["sha256"] for name, value in fields.items()
        },
    }
    return PathTerms(u, rational_path(v, h), c3, c4, d0, d1, d2, audit)


def one_step(model: chart.QuadraticChart, terms: PathTerms, t: float) -> dict:
    a = t * terms.u
    state, reconstructed = model.embed(a), model.embed(model.reduced(a))
    minimum_density = min(float(terms.local.density(t).min()), float(moments(state)[..., 0].min()))
    if minimum_density <= 0:
        return {"in_domain": False, "minimum_density": minimum_density, "identity_passed": None}
    advanced = prior.map_step(model, state)
    actual = advanced - reconstructed
    tail = damping.apply_filter(
        d3.stream_periodic(model.omega * terms.local.tail(t)), model.eta, model.power
    )
    third, fourth = t**3 * terms.c3, t**4 * terms.c4
    coefficient_error = terms.d0 + t * terms.d1 + t**2 * terms.d2
    p3, p4 = coefficient_error + third, coefficient_error + third + fourth
    prediction = p4 + tail
    budget = float(
        100
        * np.finfo(float).eps
        * max(1, degree.norm(advanced), degree.norm(reconstructed), degree.norm(prediction))
    )
    norm_actual = degree.norm(actual)
    perturbation = degree.norm(state - model.base)
    absolute = degree.norm(actual - prediction)
    return {
        "in_domain": True,
        "minimum_density": minimum_density,
        "defect_norm": norm_actual,
        "initial_population_perturbation_norm": perturbation,
        "relative_initial_defect": ratio(norm_actual, perturbation, budget),
        "resolved": norm_actual > budget,
        "roundoff_budget": budget,
        "cubic_prediction_error": degree.norm(actual - p3),
        "quartic_prediction_error": degree.norm(actual - p4),
        "tail_prediction_error": absolute,
        "cubic_prediction_relative_error": ratio(degree.norm(actual - p3), norm_actual, budget),
        "quartic_prediction_relative_error": ratio(degree.norm(actual - p4), norm_actual, budget),
        "tail_prediction_relative_error": ratio(absolute, norm_actual, budget),
        "term_order": ["coefficient_roundoff", "cubic", "quartic", "rational_tail"],
        "term_norms": [degree.norm(f) for f in (coefficient_error, third, fourth, tail)],
        "term_gram": degree.gram((coefficient_error, third, fourth, tail)).tolist(),
        "identity_passed": absolute <= budget,
    }


def observables(state: np.ndarray) -> tuple[dict, np.ndarray]:
    m = moments(state)
    minimum_density = float(m[..., 0].min())
    return {
        "minimum_population": float(state.min()),
        "minimum_density": minimum_density,
        "maximum_density_deviation": float(np.max(np.abs(m[..., 0] - 1))),
        "maximum_mach": None
        if minimum_density <= 0
        else float(np.max(np.linalg.norm(m[..., 1:], axis=-1) / m[..., 0]) / np.sqrt(d3.CS2)),
    }, m


def usage_gates(trajectory: dict, defect: dict) -> dict:
    summary = trajectory["summary"]
    return {
        "complete_positive_density": trajectory["complete"] and trajectory["stop_reason"] is None,
        "population_accuracy": summary["maximum_relative_population_error"] is not None
        and summary["maximum_relative_population_error"] <= 0.1,
        "macro_accuracy": summary["maximum_relative_macro_error"] is not None
        and summary["maximum_relative_macro_error"] <= 0.1,
        "improvement_over_same_initial_linear": summary["quadratic_to_linear_maximum_error_ratio"]
        is not None
        and summary["quadratic_to_linear_maximum_error_ratio"] <= 0.5,
        "one_step_accuracy": defect["in_domain"]
        and defect["relative_initial_defect"] is not None
        and defect["relative_initial_defect"] <= 0.01,
        "fixed_leaf_conservation": trajectory["initial_site_average_leaf_error"] <= 5e-13
        and summary["maximum_site_average_conservation_drift"] <= 5e-13,
    }


def trajectory_case(model: chart.QuadraticChart, a0: np.ndarray, steps: int = STEPS) -> dict:
    a = a0.copy()
    reconstructed = model.embed(a)
    state = reconstructed.copy()
    linear_perturbation = state - model.base
    initial_norm = degree.norm(linear_perturbation)
    initial_macro_norm = macro_norm(moments(linear_perturbation))
    initial_global = d3.global_conserved_quantities(state)
    initial_leaf = float(
        np.max(np.abs(initial_global - d3.global_conserved_quantities(model.base))) / model.size**3
    )
    floor = float(100 * np.finfo(float).eps * max(1, degree.norm(model.base)))
    trace, stop_reason, execution_error = [], None, None
    try:
        with np.errstate(over="raise", invalid="raise", divide="raise"):
            for step in range(steps + 1):
                if step:
                    state = prior.map_step(model, state)
                    a = model.reduced(a)
                    reconstructed = model.embed(a)
                    linear_perturbation = prior.linear_step(model, linear_perturbation)
                linear = model.base + linear_perturbation
                fields = {"full": state, "quadratic": reconstructed, "linear": linear}
                if not all(np.all(np.isfinite(field)) for field in fields.values()):
                    raise FloatingPointError("nonfinite iterate")
                obs, moment_fields, drift = {}, {}, {}
                for name, field in fields.items():
                    obs[name], moment_fields[name] = observables(field)
                    drift[name] = (d3.global_conserved_quantities(field) - initial_global).tolist()
                trace.append(
                    {
                        "step": step,
                        "population_error": degree.norm(state - reconstructed),
                        "linear_population_error": degree.norm(state - linear),
                        "macro_error": macro_norm(
                            moment_fields["full"] - moment_fields["quadratic"]
                        ),
                        "linear_macro_error": macro_norm(
                            moment_fields["full"] - moment_fields["linear"]
                        ),
                        "observables": obs,
                        "global_conservation_drift": drift,
                    }
                )
                failing = [
                    name
                    for name in ("full", "quadratic")
                    if obs[name]["minimum_population"] <= 0 or obs[name]["minimum_density"] < 0.5
                ]
                if failing:
                    stop_reason = {
                        "step": step,
                        "reason": "population_or_density_guard",
                        "fields": failing,
                    }
                    break
    except (FloatingPointError, ValueError) as error:
        execution_error = {"type": type(error).__name__, "message": str(error)}
        stop_reason = {"step": len(trace), "reason": "numerical_execution_failure"}
    maximum = lambda key: max((r[key] for r in trace), default=0.0)
    summary = {
        "maximum_population_error": maximum("population_error"),
        "maximum_linear_population_error": maximum("linear_population_error"),
        "maximum_macro_error": maximum("macro_error"),
        "maximum_linear_macro_error": maximum("linear_macro_error"),
        "maximum_relative_population_error": ratio(
            maximum("population_error"), initial_norm, floor
        ),
        "maximum_relative_macro_error": ratio(maximum("macro_error"), initial_macro_norm, floor),
        "quadratic_to_linear_maximum_error_ratio": ratio(
            maximum("population_error"), maximum("linear_population_error"), floor
        ),
        "maximum_site_average_conservation_drift": max(
            (
                abs(v)
                for r in trace
                for name in ("full", "quadratic")
                for v in r["global_conservation_drift"][name]
            ),
            default=0.0,
        )
        / model.size**3,
    }
    return {
        "initial_population_perturbation_norm": initial_norm,
        "initial_macro_perturbation_norm": initial_macro_norm,
        "initial_global_conserved_quantities": initial_global.tolist(),
        "initial_site_average_leaf_error": initial_leaf,
        "roundoff_floor": floor,
        "requested_steps": steps,
        "complete": len(trace) == steps + 1 and stop_reason is None,
        "stop_reason": stop_reason,
        "execution_error": execution_error,
        "trace": trace,
        "summary": summary,
    }


def evaluate_case(
    model: chart.QuadraticChart,
    terms: PathTerms,
    group: str,
    index: int,
    amplitude: float,
    sign: int,
) -> dict:
    t = amplitude * sign
    with np.errstate(over="raise", invalid="raise", divide="raise"):
        defect = one_step(model, terms, t)
        trajectory = trajectory_case(model, t * terms.u)
    gates = usage_gates(trajectory, defect)
    return {
        "group": group,
        "direction_index": index,
        "amplitude": amplitude,
        "sign": sign,
        "one_step": defect,
        "trajectory": trajectory,
        "usage_gates": gates,
        "usage_passed": all(gates.values()),
    }


def case_key(row: dict) -> tuple:
    return row["group"], row["direction_index"], row["amplitude"], row["sign"]


def amplitude_inventory(records: list[dict], group: str) -> list[dict]:
    result = []
    for amplitude in AMPLITUDES:
        selected = [r for r in records if r["group"] == group and r["amplitude"] == amplitude]
        coverage = len(selected) == 16 and {
            (r["direction_index"], r["sign"]) for r in selected
        } == {(i, sign) for i in range(8) for sign in (1, -1)}
        result.append(
            {
                "amplitude": amplitude,
                "case_count": len(selected),
                "coverage": coverage,
                "passing_cases": sum(r["usage_passed"] for r in selected),
                "failed_cases": [
                    {
                        "direction_index": r["direction_index"],
                        "sign": r["sign"],
                        "gates": [k for k, v in r["usage_gates"].items() if not v],
                    }
                    for r in selected
                    if not r["usage_passed"]
                ],
                "passed": coverage and all(r["usage_passed"] for r in selected),
            }
        )
    return result


def select_prefix(inventory: list[dict]) -> list[float]:
    prefix = []
    for row in inventory:
        if not row["passed"]:
            break
        prefix.append(row["amplitude"])
    return prefix
