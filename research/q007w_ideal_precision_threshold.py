"""Sealed Q007w ideal binary precision threshold audit."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from fractions import Fraction
from itertools import pairwise
from pathlib import Path
from typing import Any

import numpy as np

import research.q007v_binary64_stage_enclosure as q007v
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    VELOCITIES,
    WEIGHTS,
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

MINIMUM_PRECISION = 53
MAXIMUM_PRECISION = 128
REGISTERED_PRECISIONS = tuple(
    range(MINIMUM_PRECISION, MAXIMUM_PRECISION + 1)
)
MINIMUM_NORMAL_EXPONENT = -1022
Q007V_ARTIFACT = "q007v_binary64_stage_enclosure.json"
REGISTERED_Q007V_ARTIFACT_SHA256 = (
    "c4c1c45941a6f6ac302691efd8e795e431f6acc1fa4f4629cb0c7a0afac3c0a5"
)
REGISTERED_Q007V_RUNNER_SHA256 = (
    "a0d3cea0fcae8a627f4a96db56d46727589411b2557e2aa91433569576a0575c"
)

RationalInterval = q007v.RationalInterval
PairedQuantity = q007v.PairedQuantity


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _fraction_from_record(record: dict[str, Any]) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _load_registered_q007v(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007V_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha256 = _file_sha256(artifact_path)
    runner_path = Path(__file__).resolve().with_name(
        "q007v_binary64_stage_enclosure.py"
    )
    observed_runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    scope = payload.get("mathematical_scope", {})
    cycle = payload.get("cycle", {})
    validity = cycle.get("validity_gates", {})
    hypotheses = cycle.get("hypothesis_gates", {})
    theorem = cycle.get("theorem_consequence", {})
    failed_hypotheses = [
        name for name, gate in hypotheses.items() if not gate.get("passed", False)
    ]
    false_theorems = [name for name, value in theorem.items() if not value]
    source_audit = cycle.get("implementation_source_audit", {})
    scope_match = bool(
        scope.get("diagnostic")
        == "rational binary64 stage-roundoff enclosure and tube-reentry audit"
        and scope.get("construction_grid") == [q007v.SIZE, q007v.SIZE]
        and float(scope.get("omega", np.nan)) == float(q007v.OMEGA)
        and float(scope.get("eta", np.nan)) == float(q007v.ETA)
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and scope.get("input_encoding")
        == "correctly rounded binary64 encoding of an exact real Q007s tube state"
    )
    mixed_outcome_match = bool(
        payload.get("study_gate") == "passed"
        and payload.get("scientific_outcome") == "not_certified"
        and cycle.get("one_step_outcome") == "accepted"
        and cycle.get("robust_reentry_outcome") == "not_certified"
        and len(validity) == 7
        and all(gate.get("passed", False) for gate in validity.values())
        and len(hypotheses) == 6
        and failed_hypotheses == ["roundoff_robust_q007s_tube_reentry"]
        and len(theorem) == 6
        and false_theorems
        == ["all_iterate_roundoff_robust_q007s_tube_invariance"]
    )
    source_match = bool(
        source_audit.get("passed", False)
        and source_audit.get("d2q9_source", {}).get("sha256")
        == q007v.REGISTERED_D2Q9_SOURCE_SHA256
        and source_audit.get("filter_source", {}).get("sha256")
        == q007v.REGISTERED_FILTER_SOURCE_SHA256
    )
    record = {
        "filename": Q007V_ARTIFACT,
        "registered_sha256": REGISTERED_Q007V_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha256,
        "sha256_matches": (
            observed_artifact_sha256 == REGISTERED_Q007V_ARTIFACT_SHA256
        ),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "scope_match": scope_match,
        "schema_version": payload.get("schema_version"),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
        "validity_gate_count": len(validity),
        "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
        "hypothesis_gate_count": len(hypotheses),
        "failed_hypothesis_names": failed_hypotheses,
        "theorem_consequence_count": len(theorem),
        "false_theorem_names": false_theorems,
        "mixed_outcome_match": mixed_outcome_match,
        "implementation_sources_match": source_match,
        "registered_runner_sha256": REGISTERED_Q007V_RUNNER_SHA256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "observed_runner_sha256": observed_runner_sha256,
        "runner_sha_matches": bool(
            artifact_runner_sha256 == REGISTERED_Q007V_RUNNER_SHA256
            and observed_runner_sha256 == REGISTERED_Q007V_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["mixed_outcome_match"]
        and record["implementation_sources_match"]
        and cycle.get("q007u_input_artifact", {}).get("passed", False)
        and cycle.get("q007s_input_artifact", {}).get("passed", False)
        and record["runner_sha_matches"]
    )
    return payload, record


def _power_of_two(exponent: int) -> Fraction:
    return (
        Fraction(2**exponent)
        if exponent >= 0
        else Fraction(1, 2 ** (-exponent))
    )


def _floor_log2_positive(value: Fraction) -> int:
    if value <= 0:
        raise ValueError("binary exponent requires a positive rational")
    numerator = value.numerator
    denominator = value.denominator
    exponent = numerator.bit_length() - denominator.bit_length()
    if exponent >= 0:
        if numerator < denominator << exponent:
            exponent -= 1
    elif numerator << (-exponent) < denominator:
        exponent -= 1
    return exponent


def _nearest_integer_ties_even(value: Fraction) -> int:
    if value < 0:
        return -_nearest_integer_ties_even(-value)
    quotient, remainder = divmod(value.numerator, value.denominator)
    doubled = 2 * remainder
    if doubled < value.denominator:
        return quotient
    if doubled > value.denominator:
        return quotient + 1
    return quotient if quotient % 2 == 0 else quotient + 1


def _round_to_binary_precision(value: Fraction, precision: int) -> Fraction:
    if precision < 2:
        raise ValueError("precision must include at least two significand bits")
    if value == 0:
        return Fraction(0)
    sign = -1 if value < 0 else 1
    magnitude = abs(value)
    exponent = _floor_log2_positive(magnitude)
    quantum = _power_of_two(exponent - precision + 1)
    rounded_integer = _nearest_integer_ties_even(magnitude / quantum)
    return sign * rounded_integer * quantum


@dataclass(frozen=True)
class PrecisionModel:
    significand_bits: int
    unit_roundoff: Fraction
    subnormal_fallback: Fraction

    @classmethod
    def from_bits(cls, significand_bits: int) -> PrecisionModel:
        return cls(
            significand_bits=significand_bits,
            unit_roundoff=Fraction(1, 2**significand_bits),
            subnormal_fallback=Fraction(
                1,
                2 ** (-MINIMUM_NORMAL_EXPONENT + significand_bits),
            ),
        )


@dataclass
class PrecisionContext:
    model: PrecisionModel
    counts: dict[str, int] = field(
        default_factory=lambda: {
            key: 0 for key in q007v.EXPECTED_OPERATION_COUNTS
        }
    )
    maximum_intermediate_magnitude: Fraction = Fraction(0)
    minimum_divisor_margin: Fraction | None = None

    def observe(self, quantity: PairedQuantity) -> None:
        self.maximum_intermediate_magnitude = max(
            self.maximum_intermediate_magnitude,
            quantity.computed_magnitude,
        )


def _point(value: Fraction) -> RationalInterval:
    return RationalInterval(value, value)


def _constant(exact: Fraction, actual: Fraction | None = None) -> PairedQuantity:
    return PairedQuantity(
        _point(exact),
        Fraction(0) if actual is None else abs(actual - exact),
    )


def _roundoff(magnitude: Fraction, model: PrecisionModel) -> Fraction:
    return model.unit_roundoff * magnitude + model.subnormal_fallback


def _add(
    left: PairedQuantity,
    right: PairedQuantity,
    context: PrecisionContext,
) -> PairedQuantity:
    target = q007v._interval_add(left.target, right.target)
    pre_error = left.error + right.error
    result = PairedQuantity(
        target,
        pre_error + _roundoff(target.magnitude + pre_error, context.model),
    )
    context.counts["binary_additions"] += 1
    context.observe(result)
    return result


def _subtract(
    left: PairedQuantity,
    right: PairedQuantity,
    context: PrecisionContext,
) -> PairedQuantity:
    target = q007v._interval_subtract(left.target, right.target)
    pre_error = left.error + right.error
    result = PairedQuantity(
        target,
        pre_error + _roundoff(target.magnitude + pre_error, context.model),
    )
    context.counts["binary_subtractions"] += 1
    context.observe(result)
    return result


def _multiply(
    left: PairedQuantity,
    right: PairedQuantity,
    context: PrecisionContext,
) -> PairedQuantity:
    target = q007v._interval_multiply(left.target, right.target)
    pre_error = (
        left.target.magnitude * right.error
        + right.target.magnitude * left.error
        + left.error * right.error
    )
    result = PairedQuantity(
        target,
        pre_error + _roundoff(target.magnitude + pre_error, context.model),
    )
    context.counts["binary_multiplications"] += 1
    context.observe(result)
    return result


def _divide(
    numerator: PairedQuantity,
    denominator: PairedQuantity,
    context: PrecisionContext,
) -> PairedQuantity:
    divisor_margin = denominator.target.lower - denominator.error
    if divisor_margin <= 0:
        raise ValueError("computed denominator enclosure reaches zero")
    target = q007v._interval_divide(numerator.target, denominator.target)
    pre_error = (
        numerator.error * denominator.target.magnitude
        + numerator.target.magnitude * denominator.error
    ) / (denominator.target.lower * divisor_margin)
    result = PairedQuantity(
        target,
        pre_error + _roundoff(target.magnitude + pre_error, context.model),
    )
    context.counts["binary_divisions"] += 1
    context.minimum_divisor_margin = (
        divisor_margin
        if context.minimum_divisor_margin is None
        else min(context.minimum_divisor_margin, divisor_margin)
    )
    context.observe(result)
    return result


def _sum_reduction(
    terms: list[PairedQuantity],
    context: PrecisionContext,
) -> PairedQuantity:
    if not terms:
        raise ValueError("reduction requires at least one term")
    target = RationalInterval(
        sum((term.target.lower for term in terms), Fraction(0)),
        sum((term.target.upper for term in terms), Fraction(0)),
    )
    input_error = sum((term.error for term in terms), Fraction(0))
    additions = len(terms) - 1
    if additions:
        denominator = 1 - additions * context.model.unit_roundoff
        gamma = additions * context.model.unit_roundoff / denominator
        term_magnitude_sum = sum(
            (term.computed_magnitude for term in terms),
            Fraction(0),
        )
        reduction_error = (
            gamma * term_magnitude_sum
            + additions * context.model.subnormal_fallback / denominator
        )
    else:
        reduction_error = Fraction(0)
    result = PairedQuantity(target, input_error + reduction_error)
    context.counts["reduction_calls"] += 1
    context.counts["reduction_additions"] += additions
    context.observe(result)
    return result


def _exact_sign_or_zero_product(
    quantity: PairedQuantity,
    coefficient: int,
    context: PrecisionContext,
) -> PairedQuantity:
    if coefficient not in (-1, 0, 1):
        raise ValueError("exact sign product requires -1, 0, or 1")
    context.counts["exact_sign_or_zero_products"] += 1
    if coefficient == 0:
        result = PairedQuantity(_point(Fraction(0)), Fraction(0))
    elif coefficient == 1:
        result = quantity
    else:
        result = PairedQuantity(
            RationalInterval(-quantity.target.upper, -quantity.target.lower),
            quantity.error,
        )
    context.observe(result)
    return result


def _stage_summary(quantities: list[PairedQuantity]) -> dict[str, Any]:
    lower = min(quantity.computed_lower for quantity in quantities)
    upper = max(quantity.computed_upper for quantity in quantities)
    maximum_error = max(quantity.error for quantity in quantities)
    return {
        "population_lower": _fraction_record(lower),
        "population_upper": _fraction_record(upper),
        "maximum_component_error": _fraction_record(maximum_error),
    }


def _evaluate_precision(
    precision: int,
    state_radius: Fraction,
    selected_analysis: Fraction,
    external_analysis: Fraction,
    base_margin: Fraction,
    normal_margin: Fraction,
) -> tuple[dict[str, Any], dict[str, Any]]:
    model = PrecisionModel.from_bits(precision)
    context = PrecisionContext(model)
    inputs: list[PairedQuantity] = []
    for weight in WEIGHTS:
        target = RationalInterval(weight - state_radius, weight + state_radius)
        quantity = PairedQuantity(
            target,
            _roundoff(target.magnitude, model),
        )
        context.counts["input_roundings"] += 1
        context.observe(quantity)
        inputs.append(quantity)

    density = _sum_reduction(inputs, context)
    momentum: list[PairedQuantity] = []
    for dimension in range(2):
        terms = [
            _exact_sign_or_zero_product(
                inputs[population],
                VELOCITIES[population][dimension],
                context,
            )
            for population in range(9)
        ]
        momentum.append(_sum_reduction(terms, context))
    velocity = [
        _divide(component, density, context) for component in momentum
    ]

    velocity_dots: list[PairedQuantity] = []
    for cx, cy in VELOCITIES:
        velocity_dots.append(
            _sum_reduction(
                [
                    _exact_sign_or_zero_product(velocity[0], cx, context),
                    _exact_sign_or_zero_product(velocity[1], cy, context),
                ],
                context,
            )
        )
    speed_squared = _sum_reduction(
        [
            _multiply(component, component, context)
            for component in velocity
        ],
        context,
    )

    weight_actuals = [
        _round_to_binary_precision(weight, precision) for weight in WEIGHTS
    ]
    eta_actual = _round_to_binary_precision(q007v.ETA, precision)
    center_actual = _round_to_binary_precision(1 - eta_actual, precision)
    neighbour_actual = _round_to_binary_precision(
        Fraction(1, 4) * eta_actual,
        precision,
    )
    weights = [
        _constant(exact, actual)
        for exact, actual in zip(WEIGHTS, weight_actuals, strict=True)
    ]
    one = _constant(Fraction(1))
    three = _constant(Fraction(3))
    four_point_five = _constant(Fraction(9, 2))
    one_point_five = _constant(Fraction(3, 2))
    omega = _constant(q007v.OMEGA, q007v.OMEGA)

    equilibria: list[PairedQuantity] = []
    collisions: list[PairedQuantity] = []
    for population, dot in enumerate(velocity_dots):
        linear = _multiply(three, dot, context)
        quadratic_coefficient = _multiply(four_point_five, dot, context)
        quadratic = _multiply(quadratic_coefficient, dot, context)
        polynomial = _add(one, linear, context)
        polynomial = _add(polynomial, quadratic, context)
        speed_term = _multiply(one_point_five, speed_squared, context)
        polynomial = _subtract(polynomial, speed_term, context)
        density_weight = _multiply(density, weights[population], context)
        equilibrium_population = _multiply(
            density_weight,
            polynomial,
            context,
        )
        equilibria.append(equilibrium_population)
        difference = _subtract(
            equilibrium_population,
            inputs[population],
            context,
        )
        relaxed_difference = _multiply(omega, difference, context)
        collisions.append(
            _add(inputs[population], relaxed_difference, context)
        )

    streamed = list(collisions)
    center_coefficient = _constant(1 - q007v.ETA, center_actual)
    neighbour_coefficient = _constant(
        q007v.ETA / 4,
        neighbour_actual,
    )
    filtered: list[PairedQuantity] = []
    for population in range(9):
        neighbours = _sum_reduction(
            [streamed[population] for _ in range(4)],
            context,
        )
        center_term = _multiply(
            center_coefficient,
            streamed[population],
            context,
        )
        neighbour_term = _multiply(
            neighbour_coefficient,
            neighbours,
            context,
        )
        filtered.append(_add(center_term, neighbour_term, context))

    stages = {
        "equilibrium": equilibria,
        "post_collision": collisions,
        "post_streaming": streamed,
        "post_filter": filtered,
    }
    stage_summaries = {
        name: _stage_summary(quantities)
        for name, quantities in stages.items()
    }
    minimum_stage_lower = min(
        _fraction_from_record(summary["population_lower"])
        for summary in stage_summaries.values()
    )
    component_error_sum = sum(
        (quantity.error for quantity in filtered),
        Fraction(0),
    )
    wiener_error = q007v.WAVE_COUNT * component_error_sum
    base_error = selected_analysis * wiener_error
    normal_error = external_analysis * wiener_error
    base_pass = base_error < base_margin
    normal_pass = normal_error < normal_margin
    one_step_pass = minimum_stage_lower > 0
    counts_match = context.counts == q007v.EXPECTED_OPERATION_COUNTS
    passed = bool(one_step_pass and base_pass and normal_pass)
    summary = {
        "precision_bits": precision,
        "unit_roundoff": _fraction_record(model.unit_roundoff),
        "subnormal_fallback": _fraction_record(model.subnormal_fallback),
        "rounded_constants": {
            "weights": [
                _fraction_record(value) for value in weight_actuals
            ],
            "eta": _fraction_record(eta_actual),
            "filter_center": _fraction_record(center_actual),
            "filter_neighbour": _fraction_record(neighbour_actual),
        },
        "stage_bounds": stage_summaries,
        "minimum_stage_lower": _fraction_record(minimum_stage_lower),
        "post_filter_component_error_sum": _fraction_record(
            component_error_sum
        ),
        "wiener_error_upper": _fraction_record(wiener_error),
        "base_coordinate_error_upper": _fraction_record(base_error),
        "normal_coordinate_error_upper": _fraction_record(normal_error),
        "base_margin_utilization": _fraction_record(base_error / base_margin),
        "normal_margin_utilization": _fraction_record(
            normal_error / normal_margin
        ),
        "minimum_density_divisor": _fraction_record(
            context.minimum_divisor_margin
            if context.minimum_divisor_margin is not None
            else Fraction(0)
        ),
        "maximum_intermediate_magnitude": _fraction_record(
            context.maximum_intermediate_magnitude
        ),
        "operation_counts": context.counts,
        "operation_counts_match": counts_match,
        "one_step_stage_positivity_passed": one_step_pass,
        "base_reentry_passed": base_pass,
        "normal_reentry_passed": normal_pass,
        "passed": passed,
    }
    exact = {
        "inputs": inputs,
        "equilibria": equilibria,
        "collisions": collisions,
        "streamed": streamed,
        "filtered": filtered,
        "weight_actuals": weight_actuals,
        "eta_actual": eta_actual,
        "center_actual": center_actual,
        "neighbour_actual": neighbour_actual,
        "component_error_sum": component_error_sum,
        "wiener_error": wiener_error,
        "base_error": base_error,
        "normal_error": normal_error,
        "minimum_stage_lower": minimum_stage_lower,
        "minimum_divisor": context.minimum_divisor_margin,
        "maximum_intermediate": context.maximum_intermediate_magnitude,
        "counts_match": counts_match,
        "base_pass": base_pass,
        "normal_pass": normal_pass,
        "one_step_pass": one_step_pass,
        "passed": passed,
    }
    return summary, exact


def _fixed_q007v_values(
    q007v_payload: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    cycle = q007v_payload["cycle"]
    reuse = cycle["sealed_bound_reuse"]
    values = {
        "state_radius": _fraction_from_record(
            reuse["tube_state_wiener_l1_upper"]
        ),
        "selected_analysis": _fraction_from_record(
            reuse["selected_analysis_from_wiener_l1_upper"]
        ),
        "external_analysis": _fraction_from_record(
            reuse["external_analysis_from_wiener_l1_upper"]
        ),
        "base_margin": _fraction_from_record(
            reuse["base_forward_invariance_margin"]
        ),
        "normal_margin": _fraction_from_record(
            reuse["normal_tube_forward_invariance_margin"]
        ),
    }
    operation_counts_match = bool(
        cycle["paired_stage_enclosure"]["operation_counts"]
        == q007v.EXPECTED_OPERATION_COUNTS
    )
    source = cycle["implementation_source_audit"]
    source_match = bool(
        source["d2q9_source"]["sha256"]
        == q007v.REGISTERED_D2Q9_SOURCE_SHA256
        and source["filter_source"]["sha256"]
        == q007v.REGISTERED_FILTER_SOURCE_SHA256
        and source["passed"]
    )
    wave_count_match = bool(
        cycle["roundoff_reentry_audit"]["normalized_dft_wave_count"]
        == q007v.WAVE_COUNT
    )
    radii_match = bool(
        _fraction_from_record(reuse["base_modal_l1_radius"])
        == q007v.BASE_RADIUS
        and _fraction_from_record(reuse["normal_coordinate_radius"])
        == q007v.NORMAL_RADIUS
    )
    passed = bool(
        operation_counts_match
        and source_match
        and wave_count_match
        and radii_match
        and all(value > 0 for value in values.values())
    )
    section = {
        "state_wiener_l1_upper": _fraction_record(values["state_radius"]),
        "selected_analysis_upper": _fraction_record(
            values["selected_analysis"]
        ),
        "external_analysis_upper": _fraction_record(
            values["external_analysis"]
        ),
        "base_forward_invariance_margin": _fraction_record(
            values["base_margin"]
        ),
        "normal_tube_forward_invariance_margin": _fraction_record(
            values["normal_margin"]
        ),
        "normalized_dft_wave_count": q007v.WAVE_COUNT,
        "operation_counts": q007v.EXPECTED_OPERATION_COUNTS,
        "operation_counts_match": operation_counts_match,
        "d2q9_source_sha256": source["d2q9_source"]["sha256"],
        "filter_source_sha256": source["filter_source"]["sha256"],
        "source_match": source_match,
        "radii_match": radii_match,
        "passed": passed,
    }
    return section, values


def _ties_to_even_audit() -> dict[str, Any]:
    cases = (
        (Fraction(9, 8), 3, Fraction(1)),
        (Fraction(11, 8), 3, Fraction(3, 2)),
        (Fraction(-9, 8), 3, Fraction(-1)),
        (Fraction(-11, 8), 3, Fraction(-3, 2)),
    )
    records = []
    for value, precision, expected in cases:
        observed = _round_to_binary_precision(value, precision)
        records.append(
            {
                "input": _fraction_record(value),
                "precision_bits": precision,
                "expected": _fraction_record(expected),
                "observed": _fraction_record(observed),
                "passed": observed == expected,
            }
        )
    return {
        "halfway_cases": records,
        "passed": all(record["passed"] for record in records),
    }


def _p53_control_audit(
    q007v_payload: dict[str, Any],
    p53_summary: dict[str, Any],
    p53_exact: dict[str, Any],
) -> dict[str, Any]:
    cycle = q007v_payload["cycle"]
    binary64 = cycle["binary64_model_audit"]
    q007v_stages = cycle["paired_stage_enclosure"]["stages"]
    q007v_reentry = cycle["roundoff_reentry_audit"]
    weight_records = binary64["weight_constants"]
    scalar_records = {
        record["name"]: record for record in binary64["scalar_constants"]
    }
    weight_match = all(
        p53_exact["weight_actuals"][index]
        == _fraction_from_record(record["binary64_dyadic"])
        for index, record in enumerate(weight_records)
    )
    scalar_match = bool(
        p53_exact["eta_actual"]
        == _fraction_from_record(scalar_records["eta"]["binary64_dyadic"])
        and p53_exact["center_actual"]
        == _fraction_from_record(
            scalar_records["filter_center"]["binary64_dyadic"]
        )
        and p53_exact["neighbour_actual"]
        == _fraction_from_record(
            scalar_records["filter_neighbour"]["binary64_dyadic"]
        )
    )
    stage_pairs = {
        "equilibrium": p53_exact["equilibria"],
        "post_collision": p53_exact["collisions"],
        "post_streaming": p53_exact["streamed"],
        "post_filter": p53_exact["filtered"],
    }
    stage_population_match = all(
        q007v._quantity_record(quantity)
        == {key: value for key, value in stored.items() if key != "population"}
        for name, quantities in stage_pairs.items()
        for quantity, stored in zip(
            quantities,
            q007v_stages[name]["population_records"],
            strict=True,
        )
    )
    stage_summary_match = all(
        p53_summary["stage_bounds"][name]["population_lower"]
        == q007v_stages[name]["binary64_population_lower"]
        and p53_summary["stage_bounds"][name]["population_upper"]
        == q007v_stages[name]["binary64_population_upper"]
        and p53_summary["stage_bounds"][name]["maximum_component_error"]
        == q007v_stages[name]["maximum_component_forward_error_upper"]
        for name in stage_pairs
    )
    reentry_match = bool(
        p53_summary["post_filter_component_error_sum"]
        == q007v_reentry["component_forward_error_sum_upper"]
        and p53_summary["wiener_error_upper"]
        == q007v_reentry["wiener_error_upper"]
        and p53_summary["base_coordinate_error_upper"]
        == q007v_reentry["base_coordinate_error_upper"]
        and p53_summary["normal_coordinate_error_upper"]
        == q007v_reentry["normal_coordinate_error_upper"]
        and p53_summary["base_margin_utilization"]
        == q007v_reentry["base_margin_utilization"]
        and p53_summary["normal_margin_utilization"]
        == q007v_reentry["normal_margin_utilization"]
        and p53_summary["one_step_stage_positivity_passed"]
        and not p53_summary["base_reentry_passed"]
        and not p53_summary["normal_reentry_passed"]
    )
    passed = bool(
        weight_match
        and scalar_match
        and stage_population_match
        and stage_summary_match
        and reentry_match
        and p53_summary["operation_counts_match"]
    )
    return {
        "precision_bits": 53,
        "weight_dyadics_match": weight_match,
        "filter_scalar_dyadics_match": scalar_match,
        "all_population_target_and_error_records_match": stage_population_match,
        "all_stage_summaries_match": stage_summary_match,
        "all_reentry_quantities_match": reentry_match,
        "operation_counts_match": p53_summary["operation_counts_match"],
        "passed": passed,
    }


def _candidate_digest(candidates: list[dict[str, Any]]) -> str:
    canonical = json.dumps(
        candidates,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _nonincreasing(
    candidates: list[dict[str, Any]],
    key: str,
) -> bool:
    values = [_fraction_from_record(candidate[key]) for candidate in candidates]
    return all(right <= left for left, right in pairwise(values))


def _stage_lowers_nondecreasing(candidates: list[dict[str, Any]]) -> bool:
    for name in (
        "equilibrium",
        "post_collision",
        "post_streaming",
        "post_filter",
    ):
        values = [
            _fraction_from_record(
                candidate["stage_bounds"][name]["population_lower"]
            )
            for candidate in candidates
        ]
        if not all(right >= left for left, right in pairwise(values)):
            return False
    return True


def run_ideal_precision_threshold_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007v_payload, input_record = _load_registered_q007v(directory)
    fixed_section, fixed = _fixed_q007v_values(q007v_payload)
    ties_section = _ties_to_even_audit()

    candidates: list[dict[str, Any]] = []
    exact_records: dict[int, dict[str, Any]] = {}
    for precision in REGISTERED_PRECISIONS:
        summary, exact = _evaluate_precision(
            precision,
            fixed["state_radius"],
            fixed["selected_analysis"],
            fixed["external_analysis"],
            fixed["base_margin"],
            fixed["normal_margin"],
        )
        candidates.append(summary)
        exact_records[precision] = exact

    p53_control = _p53_control_audit(
        q007v_payload,
        candidates[0],
        exact_records[53],
    )
    passing = [candidate for candidate in candidates if candidate["passed"]]
    selected = passing[0] if passing else None
    selected_precision = (
        int(selected["precision_bits"]) if selected is not None else None
    )
    previous = (
        candidates[selected_precision - MINIMUM_PRECISION - 1]
        if selected_precision is not None
        and selected_precision > MINIMUM_PRECISION
        else None
    )
    precisions = [candidate["precision_bits"] for candidate in candidates]
    coverage_match = bool(
        precisions == list(REGISTERED_PRECISIONS)
        and len(set(precisions)) == len(REGISTERED_PRECISIONS)
        and len(candidates) == 76
    )
    first_pass_match = bool(
        selected is None
        or selected["precision_bits"]
        == min(candidate["precision_bits"] for candidate in passing)
    )
    boundary_reproduced = bool(
        selected is not None
        and selected_precision is not None
        and selected_precision > MINIMUM_PRECISION
        and previous is not None
        and not previous["passed"]
        and (
            not previous["base_reentry_passed"]
            or not previous["normal_reentry_passed"]
        )
        and selected["passed"]
    )
    monotonic_fields = {
        key: _nonincreasing(candidates, key)
        for key in (
            "post_filter_component_error_sum",
            "wiener_error_upper",
            "base_coordinate_error_upper",
            "normal_coordinate_error_upper",
            "base_margin_utilization",
            "normal_margin_utilization",
        )
    }
    monotonic_fields["stage_lowers_nondecreasing"] = (
        _stage_lowers_nondecreasing(candidates)
    )
    monotonic_passed = all(monotonic_fields.values())
    all_domains_pass = all(
        _fraction_from_record(candidate["minimum_density_divisor"]) > 0
        and _fraction_from_record(candidate["maximum_intermediate_magnitude"])
        < _power_of_two(1024)
        and candidate["one_step_stage_positivity_passed"]
        and candidate["operation_counts_match"]
        for candidate in candidates
    )
    digest = _candidate_digest(candidates)
    selection = {
        "candidate_count": len(candidates),
        "passing_candidate_count": len(passing),
        "registered_precision_minimum": MINIMUM_PRECISION,
        "registered_precision_maximum": MAXIMUM_PRECISION,
        "selection_rule": "minimum passing significand precision",
        "selected_candidate": selected,
        "previous_precision_candidate": previous,
        "selected_precision_bits": selected_precision,
        "first_pass_matches_selection": first_pass_match,
        "selection_boundary_reproduced": boundary_reproduced,
    }
    campaign = {
        "registered_precisions": list(REGISTERED_PRECISIONS),
        "candidate_count": len(candidates),
        "candidate_digest_sha256": digest,
        "candidate_digest_canonicalization": (
            "UTF-8 strict JSON, sorted keys, separators comma/colon"
        ),
        "coverage_match": coverage_match,
        "monotonicity_checks": monotonic_fields,
        "all_monotonicity_checks_pass": monotonic_passed,
        "all_candidate_domains_pass": all_domains_pass,
        "candidates": candidates,
    }

    serializable_sections = {
        "input_artifact": input_record,
        "fixed_q007v_values": fixed_section,
        "ties_to_even_audit": ties_section,
        "p53_control_audit": p53_control,
        "precision_campaign": campaign,
        "selection": selection,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_q007v_input": {
            "passed": input_record["passed"],
            "threshold": (
                "Q007v artifact/runner SHA, source, scope, seven validity "
                "gates, mixed six-hypothesis outcome, and mixed theorem flags match"
            ),
            "value": input_record["passed"],
        },
        "fixed_q007v_values_reused": {
            "passed": fixed_section["passed"],
            "threshold": (
                "x_*, analysis norms, margins, source SHA, operation counts, "
                "radii, and normalized DFT coefficient reproduce exactly"
            ),
            "value": fixed_section["passed"],
        },
        "p53_exact_control_reproduction": {
            "passed": bool(ties_section["passed"] and p53_control["passed"]),
            "threshold": (
                "ties-to-even halfway cases pass and p=53 reproduces every "
                "Q007v constant, stage pair, summary, and re-entry quantity"
            ),
            "value": {
                "ties": ties_section["passed"],
                "p53": p53_control["passed"],
            },
        },
        "complete_registered_precision_campaign": {
            "passed": coverage_match,
            "threshold": (
                "all 76 integer precisions 53..128 are evaluated exactly "
                "once and a canonical digest is stored"
            ),
            "value": {
                "candidate_count": len(candidates),
                "digest": digest,
            },
        },
        "monotonicity_and_selection_boundary": {
            "passed": bool(
                monotonic_passed
                and first_pass_match
                and (selected is None or boundary_reproduced)
            ),
            "threshold": (
                "registered errors/utilizations are nonincreasing, stage "
                "lowers are nondecreasing, and the selected point is the first pass"
            ),
            "value": {
                "monotonic": monotonic_passed,
                "first_pass": first_pass_match,
                "boundary": boundary_reproduced,
            },
        },
        "all_candidate_domains": {
            "passed": all_domains_pass,
            "threshold": (
                "all candidates have positive density divisors, finite-range "
                "intermediates, exact operation counts, and positive one-step stages"
            ),
            "value": all_domains_pass,
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all exact candidate records are finite strict JSON",
            "value": finite_strict_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    p53 = candidates[0]
    selected_exists = selected is not None
    selected_minimal = bool(selected_exists and first_pass_match)
    selected_positive = bool(
        selected_exists and selected["one_step_stage_positivity_passed"]
    )
    selected_reentry = bool(
        selected_exists
        and selected["base_reentry_passed"]
        and selected["normal_reentry_passed"]
    )
    previous_failure = bool(boundary_reproduced)
    hypothesis_gates = {
        "p53_control_failure_reproduced": {
            "passed": bool(
                p53_control["passed"]
                and p53["one_step_stage_positivity_passed"]
                and not p53["base_reentry_passed"]
                and not p53["normal_reentry_passed"]
            ),
            "threshold": "p=53 exactly reproduces Q007v one-step pass/re-entry fail",
            "value": p53_control["passed"],
        },
        "passing_precision_exists": {
            "passed": selected_exists,
            "threshold": "at least one registered precision passes all gates",
            "value": selected_precision,
        },
        "selected_precision_is_minimal": {
            "passed": selected_minimal,
            "threshold": "selected p_* is the minimum passing candidate",
            "value": selected_precision,
        },
        "selected_one_step_stages_positive": {
            "passed": selected_positive,
            "threshold": "all selected-p_* one-step stage lowers are strict positive",
            "value": (
                selected["minimum_stage_lower"]["float"]
                if selected is not None
                else None
            ),
        },
        "selected_roundoff_robust_reentry": {
            "passed": selected_reentry,
            "threshold": "selected p_* passes both base and normal strict margins",
            "value": {
                "base": selected["base_reentry_passed"] if selected else False,
                "normal": (
                    selected["normal_reentry_passed"] if selected else False
                ),
            },
        },
        "previous_precision_fails_boundary": {
            "passed": previous_failure,
            "threshold": "p_*>53 and p_*-1 fails at least one re-entry gate",
            "value": (
                previous["precision_bits"] if previous is not None else None
            ),
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007w ideal-precision audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered ideal binary precision threshold restores "
            "roundoff-robust Q007s tube re-entry"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered ideal precision ladder does not certify "
            "roundoff-robust Q007s tube re-entry"
        )

    return {
        "question": (
            "What minimum registered ideal binary significand precision makes "
            "the unchanged Q007v enclosure fit both Q007s re-entry margins?"
        ),
        "registered_parameters": {
            "minimum_precision_bits": MINIMUM_PRECISION,
            "maximum_precision_bits": MAXIMUM_PRECISION,
            "candidate_count": len(REGISTERED_PRECISIONS),
            "minimum_normal_exponent": MINIMUM_NORMAL_EXPONENT,
            "rounding_mode": "round-to-nearest ties-to-even",
        },
        "input_artifact": input_record,
        "fixed_q007v_values": fixed_section,
        "ties_to_even_audit": ties_section,
        "p53_control_audit": p53_control,
        "precision_campaign": campaign,
        "selection": selection,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_p53_binary64_failure_reproduced": hypotheses_passed,
            "finite_minimum_passing_precision_exists": hypotheses_passed,
            "selected_precision_one_step_stages_strictly_positive": (
                hypotheses_passed
            ),
            "selected_precision_base_reentry_strict": hypotheses_passed,
            "selected_precision_normal_reentry_strict": hypotheses_passed,
            "previous_precision_fails_registered_reentry": hypotheses_passed,
        },
        "claim_boundary": (
            "This is a sufficient threshold for an ideal p-bit binary "
            "round-to-nearest arithmetic family with the frozen Q007v "
            "operation schedule and worst-case enclosure. It does not certify "
            "an implemented NumPy, MPFR, decimal, or hardware backend, its "
            "rounding mode, trajectories, or performance. It is not a necessary "
            "threshold proving that lower precisions escape the tube. The Q007v "
            "binary64 not-certified outcome, Q007u exact-map acceptance, and "
            "Q007s finite-grid tube selection remain unchanged."
        ),
        "preserved_prior_outcomes": {
            "q007v_binary64_reentry_rejection_changed": False,
            "q007u_exact_stagewise_acceptance_changed": False,
            "q007s_finite_tube_enlargement_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, preregister and validate one concrete correctly "
            "rounded backend at or above p_* before making an implemented-map "
            "roundoff-robust claim."
        ),
    }


def run_q007w_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_ideal_precision_threshold_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational ideal-binary precision-threshold certificate",
            "construction_grid": [q007v.SIZE, q007v.SIZE],
            "omega": float(q007v.OMEGA),
            "eta": float(q007v.ETA),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "precision_candidates": "all integer significand bits 53 through 128",
            "minimum_normal_exponent": MINIMUM_NORMAL_EXPONENT,
            "rounding_model": "ideal binary round-to-nearest ties-to-even",
            "claim": (
                "minimum sufficient registered precision for the unchanged "
                "Q007v worst-case re-entry enclosure; no implemented backend"
            ),
        },
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": cycle["hypothesis_outcome"],
        "next_question": cycle["next_change"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    result = run_q007w_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
