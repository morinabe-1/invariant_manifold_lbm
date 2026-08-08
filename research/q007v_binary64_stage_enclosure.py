"""Sealed Q007v binary64 stage-roundoff and tube-reentry audit."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from ttim_lbm.checkerboard_filter import (
    conservative_checkerboard_filter,
    filtered_bgk_periodic_step,
)
from ttim_lbm.d2q9 import (
    D2Q9_VELOCITIES,
    D2Q9_WEIGHTS,
    collide_bgk,
    equilibrium,
    macroscopic,
    stream_periodic,
)
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

SIZE = 17
WAVE_COUNT = SIZE * SIZE
OMEGA = Fraction(3, 2)
ETA = Fraction(1, 100)
BASE_RADIUS = Fraction(9, 10**19)
NORMAL_RADIUS = Fraction(5, 10**12)
UNIT_ROUNDOFF = Fraction(1, 2**53)
SUBNORMAL_FALLBACK = Fraction(1, 2**1075)

Q007U_ARTIFACT = "q007u_larger_tube_stagewise_positivity.json"
REGISTERED_Q007U_ARTIFACT_SHA256 = (
    "b568fc304fd939121dd52543f316cb571ae6f4be4f4f664c68fe1c749b566c55"
)
REGISTERED_Q007U_RUNNER_SHA256 = (
    "56fc99f1f381e97e70710c7da0cee8d1262d0c10190cf617316f822d1eb29014"
)
Q007S_ARTIFACT = "q007s_finite_tube_enlargement.json"
REGISTERED_Q007S_ARTIFACT_SHA256 = (
    "7b70fd20df8fb7db5e5460a08d3f86fe8b81a55b56864c860a2c24e9cab63292"
)
REGISTERED_Q007S_RUNNER_SHA256 = (
    "6c8633f7e99874ac3be7dd14d3caa253b0dc8c499bb2f6edbb392fa695975b1e"
)
REGISTERED_D2Q9_SOURCE_SHA256 = (
    "6e6c5aa6734844d0393eb402e21203831faaf5f325b35249941eaa59145c6f53"
)
REGISTERED_FILTER_SOURCE_SHA256 = (
    "5fb6b67e8527b0b1f5f45511ba7cd5d077ee443220632ba3019b7bf28010a7ea"
)
EXPECTED_OPERATION_COUNTS = {
    "input_roundings": 9,
    "exact_sign_or_zero_products": 36,
    "binary_additions": 36,
    "binary_subtractions": 18,
    "binary_multiplications": 83,
    "binary_divisions": 2,
    "reduction_calls": 22,
    "reduction_additions": 61,
}


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


def _load_registered_q007u(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007U_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha256 = _file_sha256(artifact_path)
    runner_path = Path(__file__).resolve().with_name(
        "q007u_larger_tube_stagewise_positivity.py"
    )
    observed_runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    scope = payload.get("mathematical_scope", {})
    cycle = payload.get("cycle", {})
    validity = cycle.get("validity_gates", {})
    hypotheses = cycle.get("hypothesis_gates", {})
    theorem = cycle.get("theorem_consequence", {})
    scope_match = bool(
        scope.get("diagnostic")
        == "rational larger-tube exact stagewise-positivity certificate"
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == float(OMEGA)
        and float(scope.get("eta", np.nan)) == float(ETA)
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and float(scope.get("base_modal_l1_radius", np.nan))
        == float(BASE_RADIUS)
        and float(scope.get("normal_coordinate_radius", np.nan))
        == float(NORMAL_RADIUS)
        and scope.get("arithmetic_scope")
        == "exact mathematical map; no IEEE-754 intermediate roundoff enclosure"
    )
    record = {
        "filename": Q007U_ARTIFACT,
        "registered_sha256": REGISTERED_Q007U_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha256,
        "sha256_matches": (
            observed_artifact_sha256 == REGISTERED_Q007U_ARTIFACT_SHA256
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
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload, "hypothesis_gates"
        ),
        "theorem_consequence_count": len(theorem),
        "all_theorem_consequences_true": bool(theorem) and all(theorem.values()),
        "q007s_tube_reuse_passed": bool(
            cycle.get("q007s_tube_reuse", {}).get("passed", False)
        ),
        "registered_runner_sha256": REGISTERED_Q007U_RUNNER_SHA256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "observed_runner_sha256": observed_runner_sha256,
        "runner_sha_matches": bool(
            artifact_runner_sha256 == REGISTERED_Q007U_RUNNER_SHA256
            and observed_runner_sha256 == REGISTERED_Q007U_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and record["validity_gate_count"] == 6
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"] == 5
        and record["all_hypothesis_gates_pass"]
        and record["theorem_consequence_count"] == 5
        and record["all_theorem_consequences_true"]
        and record["q007s_tube_reuse_passed"]
        and record["runner_sha_matches"]
    )
    return payload, record


def _load_registered_q007s(
    directory: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = directory / Q007S_ARTIFACT
    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    observed_artifact_sha256 = _file_sha256(artifact_path)
    runner_path = Path(__file__).resolve().with_name(
        "q007s_finite_tube_enlargement.py"
    )
    observed_runner_sha256 = _file_sha256(runner_path)
    artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
    scope = payload.get("mathematical_scope", {})
    cycle = payload.get("cycle", {})
    validity = cycle.get("validity_gates", {})
    hypotheses = cycle.get("hypothesis_gates", {})
    theorem = cycle.get("theorem_consequence", {})
    selected = cycle.get("selection", {}).get("selected_candidate", {})
    candidate_gates = selected.get("gates", {})
    scope_match = bool(
        scope.get("diagnostic") == "rational finite-tube enlargement certificate"
        and scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == float(OMEGA)
        and float(scope.get("eta", np.nan)) == float(ETA)
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and scope.get("candidate_grid") == "9 base radii by 99 normal radii"
        and scope.get("selection")
        == "lexicographically maximize base then normal radius"
    )
    selected_match = bool(
        selected
        and _fraction_from_record(selected["base_radius"]) == BASE_RADIUS
        and _fraction_from_record(selected["normal_radius"]) == NORMAL_RADIUS
        and len(candidate_gates) == 6
        and all(candidate_gates.values())
        and selected.get("passed", False)
    )
    record = {
        "filename": Q007S_ARTIFACT,
        "registered_sha256": REGISTERED_Q007S_ARTIFACT_SHA256,
        "sha256": observed_artifact_sha256,
        "sha256_matches": (
            observed_artifact_sha256 == REGISTERED_Q007S_ARTIFACT_SHA256
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
        "all_hypothesis_gates_pass": _all_gates_pass(
            payload, "hypothesis_gates"
        ),
        "theorem_consequence_count": len(theorem),
        "all_theorem_consequences_true": bool(theorem) and all(theorem.values()),
        "selected_candidate_matches": selected_match,
        "registered_runner_sha256": REGISTERED_Q007S_RUNNER_SHA256,
        "artifact_runner_sha256": artifact_runner_sha256,
        "observed_runner_sha256": observed_runner_sha256,
        "runner_sha_matches": bool(
            artifact_runner_sha256 == REGISTERED_Q007S_RUNNER_SHA256
            and observed_runner_sha256 == REGISTERED_Q007S_RUNNER_SHA256
        ),
    }
    record["passed"] = bool(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["schema_version"] == 1
        and record["study_gate"] == "passed"
        and record["scientific_outcome"] == "accepted"
        and record["validity_gate_count"] == 6
        and record["all_validity_gates_pass"]
        and record["hypothesis_gate_count"] == 5
        and record["all_hypothesis_gates_pass"]
        and record["theorem_consequence_count"] == 4
        and record["all_theorem_consequences_true"]
        and record["selected_candidate_matches"]
        and record["runner_sha_matches"]
    )
    return payload, record


@dataclass(frozen=True)
class RationalInterval:
    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower > self.upper:
            raise ValueError("interval lower endpoint exceeds upper endpoint")

    @property
    def magnitude(self) -> Fraction:
        return max(abs(self.lower), abs(self.upper))


@dataclass(frozen=True)
class PairedQuantity:
    target: RationalInterval
    error: Fraction

    def __post_init__(self) -> None:
        if self.error < 0:
            raise ValueError("forward-error upper must be nonnegative")

    @property
    def computed_magnitude(self) -> Fraction:
        return self.target.magnitude + self.error

    @property
    def computed_lower(self) -> Fraction:
        return self.target.lower - self.error

    @property
    def computed_upper(self) -> Fraction:
        return self.target.upper + self.error


@dataclass
class ArithmeticContext:
    counts: dict[str, int] = field(
        default_factory=lambda: {key: 0 for key in EXPECTED_OPERATION_COUNTS}
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


def _constant(exact: Fraction, actual: float | None = None) -> PairedQuantity:
    error = (
        Fraction(0)
        if actual is None
        else abs(Fraction.from_float(float(actual)) - exact)
    )
    return PairedQuantity(_point(exact), error)


def _interval_add(
    left: RationalInterval,
    right: RationalInterval,
) -> RationalInterval:
    return RationalInterval(left.lower + right.lower, left.upper + right.upper)


def _interval_subtract(
    left: RationalInterval,
    right: RationalInterval,
) -> RationalInterval:
    return RationalInterval(left.lower - right.upper, left.upper - right.lower)


def _interval_multiply(
    left: RationalInterval,
    right: RationalInterval,
) -> RationalInterval:
    products = (
        left.lower * right.lower,
        left.lower * right.upper,
        left.upper * right.lower,
        left.upper * right.upper,
    )
    return RationalInterval(min(products), max(products))


def _interval_divide(
    numerator: RationalInterval,
    denominator: RationalInterval,
) -> RationalInterval:
    if denominator.lower <= 0:
        raise ValueError("division interval must be strictly positive")
    quotients = (
        numerator.lower / denominator.lower,
        numerator.lower / denominator.upper,
        numerator.upper / denominator.lower,
        numerator.upper / denominator.upper,
    )
    return RationalInterval(min(quotients), max(quotients))


def _roundoff_for_magnitude(magnitude: Fraction) -> Fraction:
    return UNIT_ROUNDOFF * magnitude + SUBNORMAL_FALLBACK


def _add(
    left: PairedQuantity,
    right: PairedQuantity,
    context: ArithmeticContext,
) -> PairedQuantity:
    target = _interval_add(left.target, right.target)
    pre_error = left.error + right.error
    result = PairedQuantity(
        target,
        pre_error + _roundoff_for_magnitude(target.magnitude + pre_error),
    )
    context.counts["binary_additions"] += 1
    context.observe(result)
    return result


def _subtract(
    left: PairedQuantity,
    right: PairedQuantity,
    context: ArithmeticContext,
) -> PairedQuantity:
    target = _interval_subtract(left.target, right.target)
    pre_error = left.error + right.error
    result = PairedQuantity(
        target,
        pre_error + _roundoff_for_magnitude(target.magnitude + pre_error),
    )
    context.counts["binary_subtractions"] += 1
    context.observe(result)
    return result


def _multiply(
    left: PairedQuantity,
    right: PairedQuantity,
    context: ArithmeticContext,
) -> PairedQuantity:
    target = _interval_multiply(left.target, right.target)
    pre_error = (
        left.target.magnitude * right.error
        + right.target.magnitude * left.error
        + left.error * right.error
    )
    result = PairedQuantity(
        target,
        pre_error + _roundoff_for_magnitude(target.magnitude + pre_error),
    )
    context.counts["binary_multiplications"] += 1
    context.observe(result)
    return result


def _divide(
    numerator: PairedQuantity,
    denominator: PairedQuantity,
    context: ArithmeticContext,
) -> PairedQuantity:
    divisor_margin = denominator.target.lower - denominator.error
    if divisor_margin <= 0:
        raise ValueError("computed denominator enclosure reaches zero")
    target = _interval_divide(numerator.target, denominator.target)
    pre_error = (
        numerator.error * denominator.target.magnitude
        + numerator.target.magnitude * denominator.error
    ) / (denominator.target.lower * divisor_margin)
    result = PairedQuantity(
        target,
        pre_error + _roundoff_for_magnitude(target.magnitude + pre_error),
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
    context: ArithmeticContext,
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
        denominator = 1 - additions * UNIT_ROUNDOFF
        gamma = additions * UNIT_ROUNDOFF / denominator
        term_magnitude_sum = sum(
            (term.computed_magnitude for term in terms),
            Fraction(0),
        )
        reduction_error = (
            gamma * term_magnitude_sum
            + additions * SUBNORMAL_FALLBACK / denominator
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
    context: ArithmeticContext,
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


def _quantity_record(quantity: PairedQuantity) -> dict[str, Any]:
    return {
        "target_lower": _fraction_record(quantity.target.lower),
        "target_upper": _fraction_record(quantity.target.upper),
        "forward_error_upper": _fraction_record(quantity.error),
        "computed_lower": _fraction_record(quantity.computed_lower),
        "computed_upper": _fraction_record(quantity.computed_upper),
    }


def _stage_record(quantities: list[PairedQuantity]) -> dict[str, Any]:
    lower = min(quantity.computed_lower for quantity in quantities)
    upper = max(quantity.computed_upper for quantity in quantities)
    maximum_error = max(quantity.error for quantity in quantities)
    return {
        "population_records": [
            {"population": index, **_quantity_record(quantity)}
            for index, quantity in enumerate(quantities)
        ],
        "binary64_population_lower": _fraction_record(lower),
        "binary64_population_upper": _fraction_record(upper),
        "maximum_component_forward_error_upper": _fraction_record(
            maximum_error
        ),
    }


def _paired_stage_enclosure(
    state_radius: Fraction,
) -> tuple[dict[str, Any], dict[str, Any]]:
    context = ArithmeticContext()
    inputs: list[PairedQuantity] = []
    for weight in WEIGHTS:
        target = RationalInterval(weight - state_radius, weight + state_radius)
        quantity = PairedQuantity(
            target,
            _roundoff_for_magnitude(target.magnitude),
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

    one = _constant(Fraction(1))
    three = _constant(Fraction(3))
    four_point_five = _constant(Fraction(9, 2))
    one_point_five = _constant(Fraction(3, 2))
    omega = _constant(OMEGA, float(OMEGA))
    weight_constants = [
        _constant(weight, float(actual))
        for weight, actual in zip(WEIGHTS, D2Q9_WEIGHTS, strict=True)
    ]

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
        density_weight = _multiply(
            density,
            weight_constants[population],
            context,
        )
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
    center_coefficient = _constant(
        1 - ETA,
        1.0 - float(ETA),
    )
    neighbour_coefficient = _constant(
        ETA / 4,
        0.25 * float(ETA),
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

    counts_match = context.counts == EXPECTED_OPERATION_COUNTS
    minimum_divisor = context.minimum_divisor_margin
    section = {
        "input_component_box": {
            "state_wiener_l1_upper": _fraction_record(state_radius),
            "formula": "f_i in [w_i-x_*, w_i+x_*]",
            "correct_rounding_model": "absolute error <= u*|f_i|+h",
        },
        "density": _quantity_record(density),
        "momentum": [_quantity_record(value) for value in momentum],
        "velocity": [_quantity_record(value) for value in velocity],
        "speed_squared": _quantity_record(speed_squared),
        "stages": {
            "equilibrium": _stage_record(equilibria),
            "post_collision": _stage_record(collisions),
            "post_streaming": _stage_record(streamed),
            "post_filter": _stage_record(filtered),
        },
        "operation_counts": context.counts,
        "registered_operation_counts": EXPECTED_OPERATION_COUNTS,
        "operation_counts_match": counts_match,
        "minimum_computed_density_denominator": _fraction_record(
            minimum_divisor if minimum_divisor is not None else Fraction(0)
        ),
        "maximum_intermediate_magnitude_upper": _fraction_record(
            context.maximum_intermediate_magnitude
        ),
    }
    exact = {
        "inputs": inputs,
        "equilibria": equilibria,
        "collisions": collisions,
        "streamed": streamed,
        "filtered": filtered,
        "operation_counts_match": counts_match,
        "minimum_divisor": minimum_divisor,
        "maximum_intermediate_magnitude": context.maximum_intermediate_magnitude,
    }
    return section, exact


def _primitive_interval_audit() -> dict[str, Any]:
    left = RationalInterval(Fraction(-2), Fraction(-1))
    right = RationalInterval(Fraction(3), Fraction(4))
    addition = _interval_add(left, right)
    subtraction = _interval_subtract(left, right)
    multiplication = _interval_multiply(left, right)
    division = _interval_divide(left, right)
    context = ArithmeticContext()
    left_pair = PairedQuantity(left, Fraction(1, 1000))
    right_pair = PairedQuantity(right, Fraction(1, 2000))
    paired_results = [
        _add(left_pair, right_pair, context),
        _subtract(left_pair, right_pair, context),
        _multiply(left_pair, right_pair, context),
        _divide(left_pair, right_pair, context),
        _sum_reduction([left_pair, right_pair], context),
    ]
    passed = bool(
        addition == RationalInterval(Fraction(1), Fraction(3))
        and subtraction == RationalInterval(Fraction(-6), Fraction(-4))
        and multiplication == RationalInterval(Fraction(-8), Fraction(-3))
        and division
        == RationalInterval(Fraction(-2, 3), Fraction(-1, 4))
        and all(result.error > 0 for result in paired_results)
        and context.minimum_divisor_margin is not None
        and context.minimum_divisor_margin > 0
    )
    return {
        "addition_target": {
            "lower": _fraction_record(addition.lower),
            "upper": _fraction_record(addition.upper),
        },
        "subtraction_target": {
            "lower": _fraction_record(subtraction.lower),
            "upper": _fraction_record(subtraction.upper),
        },
        "multiplication_target": {
            "lower": _fraction_record(multiplication.lower),
            "upper": _fraction_record(multiplication.upper),
        },
        "division_target": {
            "lower": _fraction_record(division.lower),
            "upper": _fraction_record(division.upper),
        },
        "all_paired_errors_strictly_positive": all(
            result.error > 0 for result in paired_results
        ),
        "passed": passed,
    }


def _binary64_model_audit() -> dict[str, Any]:
    finfo = np.finfo(np.float64)
    smallest_subnormal = float(np.nextafter(np.float64(0), np.float64(1)))
    exact_weights = []
    for population, (weight, actual) in enumerate(
        zip(WEIGHTS, D2Q9_WEIGHTS, strict=True)
    ):
        actual_fraction = Fraction.from_float(float(actual))
        exact_weights.append(
            {
                "population": population,
                "exact": _fraction_record(weight),
                "binary64_dyadic": _fraction_record(actual_fraction),
                "absolute_representation_error": _fraction_record(
                    abs(actual_fraction - weight)
                ),
            }
        )
    coefficient_records = []
    for name, exact, actual in (
        ("eta", ETA, float(ETA)),
        ("filter_center", 1 - ETA, 1.0 - float(ETA)),
        ("filter_neighbour", ETA / 4, 0.25 * float(ETA)),
        ("omega", OMEGA, float(OMEGA)),
    ):
        actual_fraction = Fraction.from_float(actual)
        coefficient_records.append(
            {
                "name": name,
                "exact": _fraction_record(exact),
                "binary64_dyadic": _fraction_record(actual_fraction),
                "absolute_representation_error": _fraction_record(
                    abs(actual_fraction - exact)
                ),
            }
        )
    velocities_match = bool(
        D2Q9_VELOCITIES.dtype == np.float64
        and tuple(map(tuple, D2Q9_VELOCITIES.astype(int))) == VELOCITIES
    )
    weights_match = bool(
        D2Q9_WEIGHTS.dtype == np.float64
        and D2Q9_WEIGHTS.shape == (9,)
        and len(exact_weights) == 9
    )
    passed = bool(
        np.dtype(np.float64).itemsize == 8
        and finfo.nmant == 52
        and finfo.nexp == 11
        and Fraction.from_float(float(finfo.eps)) == Fraction(1, 2**52)
        and Fraction.from_float(float(finfo.tiny)) == Fraction(1, 2**1022)
        and Fraction.from_float(smallest_subnormal) == Fraction(1, 2**1074)
        and UNIT_ROUNDOFF == Fraction(1, 2**53)
        and SUBNORMAL_FALLBACK == Fraction(1, 2**1075)
        and velocities_match
        and weights_match
        and coefficient_records[-1]["absolute_representation_error"][
            "numerator_base16"
        ]
        == "0x0"
    )
    return {
        "dtype": "float64",
        "itemsize_bytes": np.dtype(np.float64).itemsize,
        "explicit_fraction_bits": finfo.nmant,
        "exponent_bits": finfo.nexp,
        "unit_roundoff": _fraction_record(UNIT_ROUNDOFF),
        "subnormal_absolute_fallback": _fraction_record(
            SUBNORMAL_FALLBACK
        ),
        "machine_epsilon": _fraction_record(Fraction(1, 2**52)),
        "smallest_normal": _fraction_record(Fraction(1, 2**1022)),
        "smallest_subnormal": _fraction_record(Fraction(1, 2**1074)),
        "maximum_finite": _fraction_record(
            Fraction.from_float(float(finfo.max))
        ),
        "weight_constants": exact_weights,
        "scalar_constants": coefficient_records,
        "velocities_exact_binary64_integers": velocities_match,
        "weights_are_binary64": weights_match,
        "rounding_model": "round-to-nearest ties-to-even",
        "passed": passed,
    }


def _normalized_source_text(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def _implementation_source_audit(q007u: dict[str, Any]) -> dict[str, Any]:
    repository = Path(__file__).resolve().parents[1]
    d2q9_path = repository / "src" / "ttim_lbm" / "d2q9.py"
    filter_path = repository / "src" / "ttim_lbm" / "checkerboard_filter.py"
    d2q9_sha = _file_sha256(d2q9_path)
    filter_sha = _file_sha256(filter_path)
    d2q9_text = _normalized_source_text(d2q9_path)
    filter_text = _normalized_source_text(filter_path)
    d2q9_snippets = (
        "density = populations.sum(axis=-1)",
        "momentum = np.einsum(\"...q,qd->...d\", populations, D2Q9_VELOCITIES)",
        "velocity = j / rho[..., None]",
        "cu = np.einsum(\"...d,qd->...q\", velocity, D2Q9_VELOCITIES)",
        "speed_squared = np.sum(velocity * velocity, axis=-1)",
        "1.0 + 3.0 * cu + 4.5 * cu * cu - 1.5 * speed_squared[..., None]",
        "return populations + omega * (equilibrium(density, momentum) - populations)",
        "streamed[..., q] = np.roll",
    )
    filter_snippets = (
        "np.roll(populations, 1, axis=0)",
        "+ np.roll(populations, -1, axis=0)",
        "+ np.roll(populations, 1, axis=1)",
        "+ np.roll(populations, -1, axis=1)",
        "return (1.0 - eta) * populations + 0.25 * eta * neighbours",
        "return conservative_checkerboard_filter(bgk_periodic_step(state, omega), eta)",
    )
    d2q9_matches = {
        snippet: snippet in d2q9_text for snippet in d2q9_snippets
    }
    filter_matches = {
        snippet: snippet in filter_text for snippet in filter_snippets
    }
    expected_stages = [
        "equilibrium evaluation",
        "BGK collision output",
        "periodic streaming output",
        "five-point filter output",
    ]
    stage_order_match = bool(
        q007u.get("mathematical_scope", {}).get("stages") == expected_stages
    )
    passed = bool(
        d2q9_sha == REGISTERED_D2Q9_SOURCE_SHA256
        and filter_sha == REGISTERED_FILTER_SOURCE_SHA256
        and all(d2q9_matches.values())
        and all(filter_matches.values())
        and stage_order_match
    )
    return {
        "d2q9_source": {
            "filename": "src/ttim_lbm/d2q9.py",
            "registered_sha256": REGISTERED_D2Q9_SOURCE_SHA256,
            "sha256": d2q9_sha,
            "sha256_matches": d2q9_sha == REGISTERED_D2Q9_SOURCE_SHA256,
            "required_snippets": d2q9_matches,
        },
        "filter_source": {
            "filename": "src/ttim_lbm/checkerboard_filter.py",
            "registered_sha256": REGISTERED_FILTER_SOURCE_SHA256,
            "sha256": filter_sha,
            "sha256_matches": filter_sha == REGISTERED_FILTER_SOURCE_SHA256,
            "required_snippets": filter_matches,
        },
        "stage_order": expected_stages,
        "q007u_stage_order_match": stage_order_match,
        "streaming_is_population_permutation_without_arithmetic": bool(
            d2q9_matches["streamed[..., q] = np.roll"]
        ),
        "passed": passed,
    }


def _deterministic_implementation_replay(
    paired_section: dict[str, Any],
) -> dict[str, Any]:
    rest = np.broadcast_to(
        D2Q9_WEIGHTS,
        (SIZE, SIZE, 9),
    ).copy()
    density, momentum = macroscopic(rest)
    equilibrium_state = equilibrium(density, momentum)
    collision_state = collide_bgk(rest, float(OMEGA))
    streamed_state = stream_periodic(collision_state)
    filtered_state = conservative_checkerboard_filter(
        streamed_state,
        float(ETA),
    )
    wrapped_state = filtered_bgk_periodic_step(
        rest,
        float(OMEGA),
        float(ETA),
    )
    arrays = {
        "equilibrium": equilibrium_state,
        "post_collision": collision_state,
        "post_streaming": streamed_state,
        "post_filter": filtered_state,
    }
    records: dict[str, Any] = {}
    all_contained = True
    for name, array in arrays.items():
        bounds = paired_section["stages"][name]
        lower = _fraction_from_record(bounds["binary64_population_lower"])
        upper = _fraction_from_record(bounds["binary64_population_upper"])
        observed_minimum = Fraction.from_float(float(np.min(array)))
        observed_maximum = Fraction.from_float(float(np.max(array)))
        contained = bool(
            observed_minimum >= lower and observed_maximum <= upper
        )
        all_contained = all_contained and contained
        records[name] = {
            "shape": list(array.shape),
            "dtype": str(array.dtype),
            "all_finite": bool(np.all(np.isfinite(array))),
            "observed_minimum": _fraction_record(observed_minimum),
            "observed_maximum": _fraction_record(observed_maximum),
            "inside_registered_enclosure": contained,
        }
    wrapper_match = bool(np.array_equal(filtered_state, wrapped_state))
    all_float64 = all(array.dtype == np.float64 for array in arrays.values())
    all_shapes_match = all(
        array.shape == (SIZE, SIZE, 9) for array in arrays.values()
    )
    all_finite = all(np.all(np.isfinite(array)) for array in arrays.values())
    passed = bool(
        density.shape == (SIZE, SIZE)
        and momentum.shape == (SIZE, SIZE, 2)
        and all_float64
        and all_shapes_match
        and all_finite
        and all_contained
        and wrapper_match
    )
    return {
        "input": "uniform rest equilibrium encoded by D2Q9_WEIGHTS",
        "density_shape": list(density.shape),
        "momentum_shape": list(momentum.shape),
        "stage_records": records,
        "all_stage_dtypes_float64": all_float64,
        "all_stage_shapes_match": all_shapes_match,
        "all_stage_values_finite": bool(all_finite),
        "all_stage_values_inside_registered_enclosures": all_contained,
        "wrapped_composition_bitwise_match": wrapper_match,
        "passed": passed,
    }


def _sealed_bound_reuse_audit(
    q007u: dict[str, Any],
    q007s: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    q007u_cycle = q007u["cycle"]
    q007u_tube = q007u_cycle["q007s_tube_reuse"]
    q007u_bounds = q007u_cycle["stage_bounds"]
    q007s_cycle = q007s["cycle"]
    selected = q007s_cycle["selection"]["selected_candidate"]
    constants = q007s_cycle["constant_reuse_audit"]["constants"]
    margins = selected["strict_margins"]

    state_radius = _fraction_from_record(
        q007u_tube["tube_state_wiener_l1_upper"]
    )
    base_radius = _fraction_from_record(q007u_tube["base_modal_l1_radius"])
    normal_radius = _fraction_from_record(
        q007u_tube["normal_coordinate_radius"]
    )
    selected_state_radius = _fraction_from_record(selected["state_radius"])
    selected_analysis = _fraction_from_record(constants["selected_analysis"])
    external_analysis = _fraction_from_record(constants["analysis"])
    base_margin = _fraction_from_record(
        margins["base_forward_invariance"]
    )
    normal_margin = _fraction_from_record(
        margins["normal_tube_forward_invariance"]
    )
    exact_stage_lowers = {
        "equilibrium": _fraction_from_record(
            q007u_bounds["equilibrium_population_lower"]
        ),
        "post_collision": _fraction_from_record(
            q007u_bounds["post_collision_population_lower"]
        ),
        "post_streaming": _fraction_from_record(
            q007u_bounds["post_streaming_population_lower"]
        ),
        "post_filter": _fraction_from_record(
            q007u_bounds["post_filter_population_lower"]
        ),
    }
    candidate_gates = selected["gates"]
    passed = bool(
        state_radius == selected_state_radius
        and base_radius == BASE_RADIUS
        and base_radius == _fraction_from_record(selected["base_radius"])
        and normal_radius == NORMAL_RADIUS
        and normal_radius == _fraction_from_record(selected["normal_radius"])
        and selected_analysis > 0
        and external_analysis > 0
        and base_margin > 0
        and normal_margin > 0
        and all(value > 0 for value in exact_stage_lowers.values())
        and len(candidate_gates) == 6
        and all(candidate_gates.values())
        and q007u_tube["q007s_forward_invariance"]
        and q007u_tube["passed"]
    )
    section = {
        "base_modal_l1_radius": _fraction_record(base_radius),
        "normal_coordinate_radius": _fraction_record(normal_radius),
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "q007s_selected_state_radius": _fraction_record(
            selected_state_radius
        ),
        "selected_analysis_from_wiener_l1_upper": _fraction_record(
            selected_analysis
        ),
        "external_analysis_from_wiener_l1_upper": _fraction_record(
            external_analysis
        ),
        "base_forward_invariance_margin": _fraction_record(base_margin),
        "normal_tube_forward_invariance_margin": _fraction_record(
            normal_margin
        ),
        "q007u_exact_stage_population_lowers": {
            name: _fraction_record(value)
            for name, value in exact_stage_lowers.items()
        },
        "selected_candidate_gates": candidate_gates,
        "all_selected_candidate_gates_pass": bool(
            len(candidate_gates) == 6 and all(candidate_gates.values())
        ),
        "q007s_forward_invariance": q007u_tube[
            "q007s_forward_invariance"
        ],
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "state_radius": state_radius,
        "selected_analysis": selected_analysis,
        "external_analysis": external_analysis,
        "base_margin": base_margin,
        "normal_margin": normal_margin,
        "passed": passed,
    }
    return section, exact


def _roundoff_reentry_audit(
    filtered: list[PairedQuantity],
    reuse_exact: dict[str, Fraction | bool],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    selected_analysis = reuse_exact["selected_analysis"]
    external_analysis = reuse_exact["external_analysis"]
    base_margin = reuse_exact["base_margin"]
    normal_margin = reuse_exact["normal_margin"]
    assert isinstance(selected_analysis, Fraction)
    assert isinstance(external_analysis, Fraction)
    assert isinstance(base_margin, Fraction)
    assert isinstance(normal_margin, Fraction)
    component_error_sum = sum(
        (quantity.error for quantity in filtered),
        Fraction(0),
    )
    wiener_error = WAVE_COUNT * component_error_sum
    base_coordinate_error = selected_analysis * wiener_error
    normal_coordinate_error = external_analysis * wiener_error
    base_pass = base_coordinate_error < base_margin
    normal_pass = normal_coordinate_error < normal_margin
    passed = bool(base_pass and normal_pass)
    section = {
        "normalized_dft_wave_count": WAVE_COUNT,
        "component_forward_error_sum_upper": _fraction_record(
            component_error_sum
        ),
        "wiener_error_upper": _fraction_record(wiener_error),
        "wiener_formula": "epsilon_W = 289*sum_i epsilon_i",
        "selected_analysis_upper": _fraction_record(selected_analysis),
        "external_analysis_upper": _fraction_record(external_analysis),
        "base_coordinate_error_upper": _fraction_record(
            base_coordinate_error
        ),
        "normal_coordinate_error_upper": _fraction_record(
            normal_coordinate_error
        ),
        "base_forward_invariance_margin": _fraction_record(base_margin),
        "normal_tube_forward_invariance_margin": _fraction_record(
            normal_margin
        ),
        "base_margin_utilization": _fraction_record(
            base_coordinate_error / base_margin
        ),
        "normal_margin_utilization": _fraction_record(
            normal_coordinate_error / normal_margin
        ),
        "base_reentry_passed": base_pass,
        "normal_reentry_passed": normal_pass,
        "passed": passed,
    }
    exact: dict[str, Fraction | bool] = {
        "wiener_error": wiener_error,
        "base_coordinate_error": base_coordinate_error,
        "normal_coordinate_error": normal_coordinate_error,
        "base_margin": base_margin,
        "normal_margin": normal_margin,
        "base_pass": base_pass,
        "normal_pass": normal_pass,
        "passed": passed,
    }
    return section, exact


def run_binary64_stage_enclosure_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q007u, q007u_record = _load_registered_q007u(directory)
    q007s, q007s_record = _load_registered_q007s(directory)
    reuse_section, reuse_exact = _sealed_bound_reuse_audit(q007u, q007s)
    state_radius = reuse_exact["state_radius"]
    assert isinstance(state_radius, Fraction)

    paired_section, paired_exact = _paired_stage_enclosure(state_radius)
    primitive_section = _primitive_interval_audit()
    binary64_section = _binary64_model_audit()
    source_section = _implementation_source_audit(q007u)
    replay_section = _deterministic_implementation_replay(paired_section)
    reentry_section, reentry_exact = _roundoff_reentry_audit(
        paired_exact["filtered"],
        reuse_exact,
    )

    maximum_finite = _fraction_from_record(
        binary64_section["maximum_finite"]
    )
    minimum_divisor = paired_exact["minimum_divisor"]
    maximum_intermediate = paired_exact["maximum_intermediate_magnitude"]
    assert isinstance(minimum_divisor, Fraction)
    assert isinstance(maximum_intermediate, Fraction)
    arithmetic_passed = bool(
        primitive_section["passed"]
        and paired_exact["operation_counts_match"]
        and minimum_divisor > 0
        and maximum_intermediate < maximum_finite
    )
    operation_replay_passed = bool(
        paired_section["operation_counts_match"]
        and source_section["passed"]
        and replay_section["passed"]
    )

    serializable_sections = {
        "q007u_input_artifact": q007u_record,
        "q007s_input_artifact": q007s_record,
        "sealed_bound_reuse": reuse_section,
        "binary64_model_audit": binary64_section,
        "primitive_interval_audit": primitive_section,
        "implementation_source_audit": source_section,
        "paired_stage_enclosure": paired_section,
        "deterministic_implementation_replay": replay_section,
        "roundoff_reentry_audit": reentry_section,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_q007u_and_q007s_inputs": {
            "passed": bool(q007u_record["passed"] and q007s_record["passed"]),
            "threshold": (
                "registered artifact/runner SHA, source, scope, all sealed "
                "gates and theorem flags, and the Q007s selected tube match"
            ),
            "value": {
                "q007u": q007u_record["passed"],
                "q007s": q007s_record["passed"],
            },
        },
        "registered_implementation_sources": {
            "passed": source_section["passed"],
            "threshold": (
                "D2Q9 and filter source SHA, required operations, and Q007u "
                "stage order match"
            ),
            "value": source_section["passed"],
        },
        "binary64_rounding_model": {
            "passed": binary64_section["passed"],
            "threshold": (
                "binary64 53-bit precision, exponent range, u=2^-53, "
                "h=2^-1075, velocities, weights, and scalar dyadics match"
            ),
            "value": binary64_section["passed"],
        },
        "exact_paired_interval_arithmetic": {
            "passed": arithmetic_passed,
            "threshold": (
                "Fraction interval primitives pass, operation counts match, "
                "all divisors stay positive, and all intermediates are finite"
            ),
            "value": {
                "minimum_divisor": float(minimum_divisor),
                "maximum_intermediate": float(maximum_intermediate),
            },
        },
        "operation_schedule_and_replay": {
            "passed": operation_replay_passed,
            "threshold": (
                "registered reduction/operation counts, source schedule, "
                "float64 shapes, and deterministic wrapped replay all match"
            ),
            "value": operation_replay_passed,
        },
        "sealed_bounds_reused": {
            "passed": reuse_section["passed"],
            "threshold": (
                "Q007u x_* and exact stage lowers plus Q007s radii, analysis "
                "norms, strict margins, candidate gates, and invariance match"
            ),
            "value": reuse_section["passed"],
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all rational enclosures are finite and strict JSON serializable",
            "value": finite_strict_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    stages = paired_section["stages"]
    stage_lowers = {
        name: _fraction_from_record(record["binary64_population_lower"])
        for name, record in stages.items()
    }
    equilibrium_positive = stage_lowers["equilibrium"] > 0
    collision_positive = stage_lowers["post_collision"] > 0
    streaming_positive = bool(
        source_section["streaming_is_population_permutation_without_arithmetic"]
        and stage_lowers["post_streaming"]
        == stage_lowers["post_collision"]
        and stage_lowers["post_streaming"] > 0
    )
    filter_positive = stage_lowers["post_filter"] > 0
    one_step_positive = bool(
        equilibrium_positive
        and collision_positive
        and streaming_positive
        and filter_positive
    )
    robust_reentry = bool(reentry_exact["passed"])
    hypothesis_gates = {
        "binary64_equilibrium_positive": {
            "passed": equilibrium_positive,
            "threshold": "registered binary64 equilibrium lower > 0",
            "value": float(stage_lowers["equilibrium"]),
        },
        "binary64_post_collision_positive": {
            "passed": collision_positive,
            "threshold": "registered binary64 post-collision lower > 0",
            "value": float(stage_lowers["post_collision"]),
        },
        "streaming_preserves_binary64_lower": {
            "passed": streaming_positive,
            "threshold": (
                "population-wise np.roll performs no arithmetic and preserves "
                "the post-collision lower"
            ),
            "value": float(stage_lowers["post_streaming"]),
        },
        "binary64_post_filter_positive": {
            "passed": filter_positive,
            "threshold": "registered binary64 post-filter lower > 0",
            "value": float(stage_lowers["post_filter"]),
        },
        "one_step_binary64_stage_positivity": {
            "passed": one_step_positive,
            "threshold": "all four registered binary64 stage lowers are strict positive",
            "value": {
                name: float(value) for name, value in stage_lowers.items()
            },
        },
        "roundoff_robust_q007s_tube_reentry": {
            "passed": robust_reentry,
            "threshold": (
                "selected and external coordinate error uppers are both "
                "strictly below the Q007s forward-invariance margins"
            ),
            "value": {
                "base_margin_utilization": reentry_section[
                    "base_margin_utilization"
                ]["float"],
                "normal_margin_utilization": reentry_section[
                    "normal_margin_utilization"
                ]["float"],
            },
        },
    }
    all_hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    one_step_certified = validity_passed and one_step_positive
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q007v binary64 enclosure audit invalid"
    elif all_hypotheses_passed:
        outcome = "accepted"
        classification = (
            "binary64 stage positivity and roundoff-robust Q007s tube "
            "invariance certified"
        )
    elif one_step_certified and not robust_reentry:
        outcome = "not_certified"
        classification = (
            "binary64 one-step stages remain positive, but the registered "
            "Q007s tube is not certified roundoff-invariant"
        )
    else:
        outcome = "not_certified"
        classification = (
            "binary64 stage positivity is not certified on the registered "
            "Q007s input tube"
        )

    return {
        "question": (
            "Does a Fraction-based binary64 enclosure preserve every one-step "
            "stage lower and fit inside the Q007s robust re-entry margins?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": _fraction_record(OMEGA),
            "eta": _fraction_record(ETA),
            "base_radius": _fraction_record(BASE_RADIUS),
            "normal_radius": _fraction_record(NORMAL_RADIUS),
            "unit_roundoff": _fraction_record(UNIT_ROUNDOFF),
            "subnormal_fallback": _fraction_record(SUBNORMAL_FALLBACK),
        },
        "q007u_input_artifact": q007u_record,
        "q007s_input_artifact": q007s_record,
        "sealed_bound_reuse": reuse_section,
        "binary64_model_audit": binary64_section,
        "primitive_interval_audit": primitive_section,
        "implementation_source_audit": source_section,
        "paired_stage_enclosure": paired_section,
        "deterministic_implementation_replay": replay_section,
        "roundoff_reentry_audit": reentry_section,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "one_step_outcome": "accepted" if one_step_certified else "not_certified",
        "robust_reentry_outcome": (
            "accepted"
            if validity_passed and robust_reentry
            else "not_certified"
        ),
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "binary64_equilibrium_population_strictly_positive": (
                one_step_certified and equilibrium_positive
            ),
            "binary64_post_collision_population_strictly_positive": (
                one_step_certified and collision_positive
            ),
            "binary64_post_streaming_population_strictly_positive": (
                one_step_certified and streaming_positive
            ),
            "binary64_post_filter_population_strictly_positive": (
                one_step_certified and filter_positive
            ),
            "one_step_binary64_stagewise_population_strictly_positive": (
                one_step_certified
            ),
            "all_iterate_roundoff_robust_q007s_tube_invariance": (
                all_hypotheses_passed
            ),
        },
        "claim_boundary": (
            "A passed one-step result applies only to correctly rounded "
            "binary64 encodings of exact real states in the Q007s selected "
            "tube, under the registered source and round-to-nearest model. If "
            "robust re-entry is not certified, the one-step conclusion is not "
            "iterated. Re-entry failure is not a counterexample or an observed "
            "tube escape; it says this fixed worst-case enclosure exceeds the "
            "sealed margins. This excludes nonstandard rounding, FTZ/DAZ, GPU "
            "kernels, BLAS changes, compiler fast-math, entropy, monotonicity, "
            "a maximum principle, a continuous-optimum tube, a global basin, "
            "grid-uniformity, and a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007u_exact_stagewise_acceptance_changed": False,
            "q007t_full_map_positivity_acceptance_changed": False,
            "q007s_finite_tube_enlargement_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If robust re-entry is not certified, preregister either a "
            "roundoff-robust tube enlargement or a higher-precision map; do "
            "not iterate the one-step binary64 positivity certificate."
        ),
    }


def run_q007v_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_binary64_stage_enclosure_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "rational binary64 stage-roundoff enclosure and tube-reentry audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": float(OMEGA),
            "eta": float(ETA),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "input_encoding": (
                "correctly rounded binary64 encoding of an exact real Q007s tube state"
            ),
            "rounding_model": (
                "IEEE-754 binary64 round-to-nearest ties-to-even with u=2^-53 "
                "and absolute subnormal fallback h=2^-1075"
            ),
            "claim": (
                "separate one-step internal-stage positivity and robust-tube "
                "re-entry decisions for the registered implementation only"
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
    result = run_q007v_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
