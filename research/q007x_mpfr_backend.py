"""Research-only 85-bit MPFR implementation of the filtered periodic D2Q9 map."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any

import gmpy2
import numpy as np
import numpy.typing as npt

MPFR_PRECISION_BITS = 85
MPFR_EMIN = -1105
MPFR_EMAX = 1024
MPFR_ROUNDING_NAME = "RoundToNearest"

D2Q9_INTEGER_VELOCITIES = (
    (0, 0),
    (1, 0),
    (0, 1),
    (-1, 0),
    (0, -1),
    (1, 1),
    (-1, 1),
    (-1, -1),
    (1, -1),
)
D2Q9_EXACT_WEIGHTS = (
    Fraction(4, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 9),
    Fraction(1, 36),
    Fraction(1, 36),
    Fraction(1, 36),
    Fraction(1, 36),
)
EXACT_OMEGA = Fraction(3, 2)
EXACT_ETA = Fraction(1, 100)

PER_SITE_OPERATION_COUNTS = {
    "input_roundings": 9,
    "exact_sign_or_zero_products": 36,
    "binary_additions": 36,
    "binary_subtractions": 18,
    "binary_multiplications": 83,
    "binary_divisions": 2,
    "reduction_calls": 22,
    "reduction_additions": 61,
}

MPFRArray = npt.NDArray[np.object_]
ExactArray = npt.NDArray[np.object_]
TraceCallback = Callable[
    [str, tuple[Fraction, ...], Fraction],
    None,
]


def mpfr_context() -> gmpy2.context:
    """Return the sealed Q007x binary85 context without mutating the caller."""

    return gmpy2.context(
        precision=MPFR_PRECISION_BITS,
        round=gmpy2.RoundToNearest,
        emin=MPFR_EMIN,
        emax=MPFR_EMAX,
        subnormalize=True,
        trap_underflow=True,
        trap_overflow=True,
        trap_divzero=True,
        trap_invalid=True,
        trap_inexact=False,
        allow_complex=False,
        rational_division=False,
        allow_release_gil=False,
    )


def fraction_from_mpfr(value: gmpy2.mpfr) -> Fraction:
    """Return the exact dyadic rational represented by an MPFR value."""

    numerator, denominator = value.as_integer_ratio()
    return Fraction(int(numerator), int(denominator))


def _context_flags(context: gmpy2.context) -> dict[str, bool]:
    return {
        "underflow": bool(context.underflow),
        "overflow": bool(context.overflow),
        "invalid": bool(context.invalid),
        "division_by_zero": bool(context.divzero),
        "inexact": bool(context.inexact),
        "erange": bool(context.erange),
    }


def expected_operation_counts(
    site_count: int,
    *,
    include_input_roundings: bool = True,
) -> dict[str, int]:
    """Scale the registered one-site operation schedule."""

    if isinstance(site_count, bool) or not isinstance(site_count, int):
        raise TypeError("site_count must be an integer")
    if site_count <= 0:
        raise ValueError("site_count must be positive")
    counts = {
        name: count * site_count
        for name, count in PER_SITE_OPERATION_COUNTS.items()
    }
    if not include_input_roundings:
        counts["input_roundings"] = 0
    return counts


@dataclass
class OperationAudit:
    """Operation counts and exact trace hooks for one backend evaluation."""

    trace: TraceCallback | None = None
    counts: dict[str, int] = field(
        default_factory=lambda: {
            name: 0 for name in PER_SITE_OPERATION_COUNTS
        }
    )
    maximum_intermediate_magnitude: Fraction = Fraction(0)
    minimum_density_divisor: Fraction | None = None
    all_results_finite: bool = True
    trace_record_count: int = 0

    def observe(
        self,
        operation: str,
        operands: Iterable[Fraction | gmpy2.mpfr],
        result: gmpy2.mpfr,
    ) -> None:
        operand_fractions = tuple(
            operand
            if isinstance(operand, Fraction)
            else fraction_from_mpfr(operand)
            for operand in operands
        )
        result_fraction = fraction_from_mpfr(result)
        self.maximum_intermediate_magnitude = max(
            self.maximum_intermediate_magnitude,
            abs(result_fraction),
        )
        self.all_results_finite = bool(
            self.all_results_finite and gmpy2.is_finite(result)
        )
        self.trace_record_count += 1
        if self.trace is not None:
            self.trace(operation, operand_fractions, result_fraction)

    def observe_density(self, density: gmpy2.mpfr) -> None:
        value = fraction_from_mpfr(density)
        self.minimum_density_divisor = (
            value
            if self.minimum_density_divisor is None
            else min(self.minimum_density_divisor, value)
        )


@dataclass(frozen=True)
class MPFRConstants:
    zero: gmpy2.mpfr
    one: gmpy2.mpfr
    three: gmpy2.mpfr
    four: gmpy2.mpfr
    four_point_five: gmpy2.mpfr
    one_point_five: gmpy2.mpfr
    omega: gmpy2.mpfr
    weights: tuple[gmpy2.mpfr, ...]
    eta: gmpy2.mpfr
    filter_center: gmpy2.mpfr
    filter_neighbour: gmpy2.mpfr


@dataclass(frozen=True)
class MPFRStages:
    encoded_input: MPFRArray
    equilibrium: MPFRArray
    post_collision: MPFRArray
    post_streaming: MPFRArray
    post_filter: MPFRArray
    operation_counts: dict[str, int]
    maximum_intermediate_magnitude: Fraction
    minimum_density_divisor: Fraction
    all_results_finite: bool
    trace_record_count: int
    context_flags: dict[str, bool]


def _mpfr_from_fraction(
    value: Fraction,
    audit: OperationAudit,
    operation: str,
) -> gmpy2.mpfr:
    rational = gmpy2.mpq(value.numerator, value.denominator)
    result = gmpy2.mpfr(rational)
    audit.observe(operation, (value,), result)
    return result


def _constant_subtract(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    audit: OperationAudit,
) -> gmpy2.mpfr:
    result = left - right
    audit.observe("constant_subtraction", (left, right), result)
    return result


def _constant_divide(
    numerator: gmpy2.mpfr,
    denominator: gmpy2.mpfr,
    audit: OperationAudit,
) -> gmpy2.mpfr:
    result = numerator / denominator
    audit.observe("constant_division", (numerator, denominator), result)
    return result


def _add(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    audit: OperationAudit,
) -> gmpy2.mpfr:
    result = left + right
    audit.counts["binary_additions"] += 1
    audit.observe("binary_addition", (left, right), result)
    return result


def _subtract(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    audit: OperationAudit,
) -> gmpy2.mpfr:
    result = left - right
    audit.counts["binary_subtractions"] += 1
    audit.observe("binary_subtraction", (left, right), result)
    return result


def _multiply(
    left: gmpy2.mpfr,
    right: gmpy2.mpfr,
    audit: OperationAudit,
) -> gmpy2.mpfr:
    result = left * right
    audit.counts["binary_multiplications"] += 1
    audit.observe("binary_multiplication", (left, right), result)
    return result


def _divide(
    numerator: gmpy2.mpfr,
    denominator: gmpy2.mpfr,
    audit: OperationAudit,
) -> gmpy2.mpfr:
    audit.observe_density(denominator)
    result = numerator / denominator
    audit.counts["binary_divisions"] += 1
    audit.observe("binary_division", (numerator, denominator), result)
    return result


def _reduce(
    values: list[gmpy2.mpfr],
    audit: OperationAudit,
) -> gmpy2.mpfr:
    if not values:
        raise ValueError("reduction requires at least one value")
    audit.counts["reduction_calls"] += 1
    result = values[0]
    for value in values[1:]:
        previous = result
        result = previous + value
        audit.counts["reduction_additions"] += 1
        audit.observe("reduction_addition", (previous, value), result)
    return result


def _signed_or_zero(
    value: gmpy2.mpfr,
    coefficient: int,
    zero: gmpy2.mpfr,
    audit: OperationAudit,
) -> gmpy2.mpfr:
    if coefficient not in (-1, 0, 1):
        raise ValueError("exact coefficient must be -1, 0, or 1")
    audit.counts["exact_sign_or_zero_products"] += 1
    if coefficient == -1:
        result = -value
        operation = "exact_negation"
        operands = (value,)
    elif coefficient == 0:
        result = zero
        operation = "exact_zero"
        operands = ()
    else:
        result = value
        operation = "exact_identity"
        operands = (value,)
    audit.observe(operation, operands, result)
    return result


def _require_exact_state(state: npt.ArrayLike) -> ExactArray:
    array = np.asarray(state, dtype=object)
    if array.ndim != 3 or array.shape[-1] != 9:
        raise ValueError("exact D2Q9 state must have shape (ny, nx, 9)")
    if array.shape[0] <= 0 or array.shape[1] <= 0:
        raise ValueError("grid dimensions must be positive")
    exact = np.empty(array.shape, dtype=object)
    for index in np.ndindex(array.shape):
        value = array[index]
        if isinstance(value, bool):
            raise TypeError("exact state values must be rational")
        try:
            exact[index] = Fraction(value)
        except (TypeError, ValueError, ZeroDivisionError) as error:
            raise TypeError("exact state values must be rational") from error
    return exact


def _require_mpfr_state(state: npt.ArrayLike) -> MPFRArray:
    array = np.asarray(state, dtype=object)
    if array.ndim != 3 or array.shape[-1] != 9:
        raise ValueError("MPFR D2Q9 state must have shape (ny, nx, 9)")
    if array.shape[0] <= 0 or array.shape[1] <= 0:
        raise ValueError("grid dimensions must be positive")
    for value in array.flat:
        if not isinstance(value, gmpy2.mpfr):
            raise TypeError("MPFR state values must be gmpy2.mpfr")
        if value.precision != MPFR_PRECISION_BITS:
            raise ValueError("MPFR state values must have 85-bit precision")
        if not gmpy2.is_finite(value):
            raise ValueError("MPFR state values must be finite")
    return array


class MPFRD2Q9Backend:
    """Concrete filtered D2Q9 map evaluated in the sealed MPFR context."""

    def __init__(self, trace: TraceCallback | None = None) -> None:
        self._trace = trace
        construction_audit = OperationAudit(trace=trace)
        with mpfr_context() as context:
            zero = _mpfr_from_fraction(
                Fraction(0),
                construction_audit,
                "constant_rounding",
            )
            one = _mpfr_from_fraction(
                Fraction(1),
                construction_audit,
                "constant_rounding",
            )
            three = _mpfr_from_fraction(
                Fraction(3),
                construction_audit,
                "constant_rounding",
            )
            four = _mpfr_from_fraction(
                Fraction(4),
                construction_audit,
                "constant_rounding",
            )
            four_point_five = _mpfr_from_fraction(
                Fraction(9, 2),
                construction_audit,
                "constant_rounding",
            )
            one_point_five = _mpfr_from_fraction(
                Fraction(3, 2),
                construction_audit,
                "constant_rounding",
            )
            omega = _mpfr_from_fraction(
                EXACT_OMEGA,
                construction_audit,
                "constant_rounding",
            )
            weights = tuple(
                _mpfr_from_fraction(
                    weight,
                    construction_audit,
                    "constant_rounding",
                )
                for weight in D2Q9_EXACT_WEIGHTS
            )
            eta = _mpfr_from_fraction(
                EXACT_ETA,
                construction_audit,
                "constant_rounding",
            )
            filter_center = _constant_subtract(
                one,
                eta,
                construction_audit,
            )
            filter_neighbour = _constant_divide(
                eta,
                four,
                construction_audit,
            )
            self.construction_context_flags = _context_flags(context)
        self.constants = MPFRConstants(
            zero=zero,
            one=one,
            three=three,
            four=four,
            four_point_five=four_point_five,
            one_point_five=one_point_five,
            omega=omega,
            weights=weights,
            eta=eta,
            filter_center=filter_center,
            filter_neighbour=filter_neighbour,
        )
        self.construction_trace_record_count = (
            construction_audit.trace_record_count
        )
        self.construction_all_results_finite = (
            construction_audit.all_results_finite
        )

    def encode_fraction_state(
        self,
        state: npt.ArrayLike,
        audit: OperationAudit | None = None,
    ) -> tuple[MPFRArray, OperationAudit]:
        """Correctly round an exact rational state componentwise."""

        exact = _require_exact_state(state)
        active_audit = (
            OperationAudit(trace=self._trace) if audit is None else audit
        )
        encoded = np.empty(exact.shape, dtype=object)
        with mpfr_context():
            for index in np.ndindex(exact.shape):
                encoded[index] = _mpfr_from_fraction(
                    exact[index],
                    active_audit,
                    "input_rounding",
                )
                active_audit.counts["input_roundings"] += 1
        return encoded, active_audit

    def evaluate_fraction_stages(self, state: npt.ArrayLike) -> MPFRStages:
        """Encode an exact rational state and evaluate every registered stage."""

        audit = OperationAudit(trace=self._trace)
        encoded, audit = self.encode_fraction_state(state, audit)
        return self._evaluate_encoded_stages(encoded, audit)

    def evaluate_encoded_stages(self, state: npt.ArrayLike) -> MPFRStages:
        """Evaluate an already encoded 85-bit state without input rounding."""

        encoded = _require_mpfr_state(state)
        return self._evaluate_encoded_stages(
            encoded,
            OperationAudit(trace=self._trace),
        )

    def step(self, state: npt.ArrayLike) -> MPFRArray:
        """Return the filtered post-step state for an encoded MPFR state."""

        return self.evaluate_encoded_stages(state).post_filter

    def _evaluate_encoded_stages(
        self,
        encoded: MPFRArray,
        audit: OperationAudit,
    ) -> MPFRStages:
        encoded = _require_mpfr_state(encoded)
        ny, nx, _ = encoded.shape
        equilibrium = np.empty(encoded.shape, dtype=object)
        collision = np.empty(encoded.shape, dtype=object)
        constants = self.constants

        with mpfr_context() as context:
            for y in range(ny):
                for x in range(nx):
                    populations = [
                        encoded[y, x, population]
                        for population in range(9)
                    ]
                    density = _reduce(populations, audit)
                    audit.observe_density(density)
                    momentum: list[gmpy2.mpfr] = []
                    for dimension in range(2):
                        momentum.append(
                            _reduce(
                                [
                                    _signed_or_zero(
                                        populations[population],
                                        D2Q9_INTEGER_VELOCITIES[population][
                                            dimension
                                        ],
                                        constants.zero,
                                        audit,
                                    )
                                    for population in range(9)
                                ],
                                audit,
                            )
                        )
                    velocity = [
                        _divide(component, density, audit)
                        for component in momentum
                    ]
                    velocity_dots = [
                        _reduce(
                            [
                                _signed_or_zero(
                                    velocity[0],
                                    cx,
                                    constants.zero,
                                    audit,
                                ),
                                _signed_or_zero(
                                    velocity[1],
                                    cy,
                                    constants.zero,
                                    audit,
                                ),
                            ],
                            audit,
                        )
                        for cx, cy in D2Q9_INTEGER_VELOCITIES
                    ]
                    speed_squared = _reduce(
                        [
                            _multiply(component, component, audit)
                            for component in velocity
                        ],
                        audit,
                    )

                    for population, dot in enumerate(velocity_dots):
                        linear = _multiply(constants.three, dot, audit)
                        quadratic_coefficient = _multiply(
                            constants.four_point_five,
                            dot,
                            audit,
                        )
                        quadratic = _multiply(
                            quadratic_coefficient,
                            dot,
                            audit,
                        )
                        polynomial = _add(constants.one, linear, audit)
                        polynomial = _add(polynomial, quadratic, audit)
                        speed_term = _multiply(
                            constants.one_point_five,
                            speed_squared,
                            audit,
                        )
                        polynomial = _subtract(
                            polynomial,
                            speed_term,
                            audit,
                        )
                        density_weight = _multiply(
                            density,
                            constants.weights[population],
                            audit,
                        )
                        equilibrium_population = _multiply(
                            density_weight,
                            polynomial,
                            audit,
                        )
                        equilibrium[y, x, population] = (
                            equilibrium_population
                        )
                        difference = _subtract(
                            equilibrium_population,
                            populations[population],
                            audit,
                        )
                        relaxed_difference = _multiply(
                            constants.omega,
                            difference,
                            audit,
                        )
                        collision[y, x, population] = _add(
                            populations[population],
                            relaxed_difference,
                            audit,
                        )

            streamed = np.empty(encoded.shape, dtype=object)
            for y in range(ny):
                for x in range(nx):
                    for population, (cx, cy) in enumerate(
                        D2Q9_INTEGER_VELOCITIES
                    ):
                        streamed[
                            (y + cy) % ny,
                            (x + cx) % nx,
                            population,
                        ] = collision[y, x, population]

            filtered = np.empty(encoded.shape, dtype=object)
            for y in range(ny):
                for x in range(nx):
                    for population in range(9):
                        neighbours = _reduce(
                            [
                                streamed[(y - 1) % ny, x, population],
                                streamed[(y + 1) % ny, x, population],
                                streamed[y, (x - 1) % nx, population],
                                streamed[y, (x + 1) % nx, population],
                            ],
                            audit,
                        )
                        center_term = _multiply(
                            constants.filter_center,
                            streamed[y, x, population],
                            audit,
                        )
                        neighbour_term = _multiply(
                            constants.filter_neighbour,
                            neighbours,
                            audit,
                        )
                        filtered[y, x, population] = _add(
                            center_term,
                            neighbour_term,
                            audit,
                        )
            flags = _context_flags(context)

        minimum_density = audit.minimum_density_divisor
        if minimum_density is None:
            raise RuntimeError("density divisor audit was not populated")
        return MPFRStages(
            encoded_input=encoded.copy(),
            equilibrium=equilibrium,
            post_collision=collision,
            post_streaming=streamed,
            post_filter=filtered,
            operation_counts=dict(audit.counts),
            maximum_intermediate_magnitude=(
                audit.maximum_intermediate_magnitude
            ),
            minimum_density_divisor=minimum_density,
            all_results_finite=audit.all_results_finite,
            trace_record_count=audit.trace_record_count,
            context_flags=flags,
        )


def backend_runtime_metadata() -> dict[str, Any]:
    """Return version and context metadata needed by the Q007x seal."""

    context = mpfr_context()
    return {
        "gmpy2_version": gmpy2.version(),
        "mpfr_version": gmpy2.mpfr_version(),
        "gmp_version": gmpy2.mp_version(),
        "mpc_version": gmpy2.mpc_version(),
        "precision_bits": context.precision,
        "rounding": MPFR_ROUNDING_NAME,
        "rounding_code": int(context.round),
        "emin": context.emin,
        "emax": context.emax,
        "subnormalize": context.subnormalize,
        "trap_underflow": context.trap_underflow,
        "trap_overflow": context.trap_overflow,
        "trap_divzero": context.trap_divzero,
        "trap_invalid": context.trap_invalid,
        "trap_inexact": context.trap_inexact,
        "allow_complex": context.allow_complex,
        "rational_division": context.rational_division,
        "allow_release_gil": context.allow_release_gil,
    }
