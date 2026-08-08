from __future__ import annotations

from fractions import Fraction

import gmpy2
import numpy as np
import pytest

import research.q007w_ideal_precision_threshold as q007w
from research.q007x_mpfr_backend import (
    D2Q9_EXACT_WEIGHTS,
    MPFR_EMAX,
    MPFR_EMIN,
    MPFR_PRECISION_BITS,
    PER_SITE_OPERATION_COUNTS,
    MPFRD2Q9Backend,
    backend_runtime_metadata,
    expected_operation_counts,
    fraction_from_mpfr,
    mpfr_context,
)


def _rest_state(ny: int, nx: int) -> np.ndarray:
    state = np.empty((ny, nx, 9), dtype=object)
    for y in range(ny):
        for x in range(nx):
            state[y, x, :] = D2Q9_EXACT_WEIGHTS
    return state


def _context_signature(context: gmpy2.context) -> tuple[object, ...]:
    return (
        context.precision,
        context.round,
        context.emin,
        context.emax,
        context.subnormalize,
        context.trap_underflow,
        context.trap_overflow,
        context.trap_divzero,
        context.trap_invalid,
        context.trap_inexact,
        context.allow_complex,
        context.rational_division,
        context.allow_release_gil,
    )


def test_mpfr_backend_runtime_and_context_are_sealed_without_leakage() -> None:
    caller_signature = _context_signature(gmpy2.get_context())
    registered = mpfr_context()

    assert registered.precision == MPFR_PRECISION_BITS == 85
    assert registered.round == gmpy2.RoundToNearest
    assert registered.emin == MPFR_EMIN == -1105
    assert registered.emax == MPFR_EMAX == 1024
    assert registered.subnormalize
    assert registered.trap_underflow
    assert registered.trap_overflow
    assert registered.trap_divzero
    assert registered.trap_invalid
    assert not registered.trap_inexact
    assert not registered.allow_complex
    assert not registered.rational_division
    assert not registered.allow_release_gil

    with registered as active:
        assert active.precision == 85
        assert gmpy2.mpfr(gmpy2.mpq(1, 10)).precision == 85

    assert _context_signature(gmpy2.get_context()) == caller_signature
    assert backend_runtime_metadata() == {
        "gmpy2_version": "2.3.1",
        "mpfr_version": "MPFR 4.2.2",
        "gmp_version": "GMP 6.3.0",
        "mpc_version": "MPC 1.4.0",
        "precision_bits": 85,
        "rounding": "RoundToNearest",
        "rounding_code": 0,
        "emin": -1105,
        "emax": 1024,
        "subnormalize": True,
        "trap_underflow": True,
        "trap_overflow": True,
        "trap_divzero": True,
        "trap_invalid": True,
        "trap_inexact": False,
        "allow_complex": False,
        "rational_division": False,
        "allow_release_gil": False,
    }


def test_mpfr_backend_trace_matches_q007w_rounding_for_every_operation() -> None:
    mismatches: list[tuple[str, Fraction, Fraction]] = []
    record_count = 0

    def trace(
        operation: str,
        operands: tuple[Fraction, ...],
        result: Fraction,
    ) -> None:
        nonlocal record_count
        record_count += 1
        if operation in {"constant_rounding", "input_rounding"}:
            exact = operands[0]
            expected = q007w._round_to_binary_precision(exact, 85)
        elif operation in {
            "constant_subtraction",
            "binary_subtraction",
        }:
            expected = q007w._round_to_binary_precision(
                operands[0] - operands[1],
                85,
            )
        elif operation in {
            "constant_division",
            "binary_division",
        }:
            expected = q007w._round_to_binary_precision(
                operands[0] / operands[1],
                85,
            )
        elif operation in {"binary_addition", "reduction_addition"}:
            expected = q007w._round_to_binary_precision(
                operands[0] + operands[1],
                85,
            )
        elif operation == "binary_multiplication":
            expected = q007w._round_to_binary_precision(
                operands[0] * operands[1],
                85,
            )
        elif operation == "exact_identity":
            expected = operands[0]
        elif operation == "exact_negation":
            expected = -operands[0]
        elif operation == "exact_zero":
            expected = Fraction(0)
        else:  # pragma: no cover - guards additions to the backend trace API
            raise AssertionError(f"unregistered trace operation: {operation}")
        if result != expected:
            mismatches.append((operation, result, expected))

    backend = MPFRD2Q9Backend(trace=trace)
    stages = backend.evaluate_fraction_stages(_rest_state(1, 1))

    assert backend.construction_trace_record_count == 19
    assert stages.trace_record_count == 245
    assert record_count == 264
    assert not mismatches


def test_mpfr_backend_replays_the_registered_per_site_schedule() -> None:
    ny, nx = 2, 3
    backend = MPFRD2Q9Backend()
    stages = backend.evaluate_fraction_stages(_rest_state(ny, nx))

    assert PER_SITE_OPERATION_COUNTS == {
        "input_roundings": 9,
        "exact_sign_or_zero_products": 36,
        "binary_additions": 36,
        "binary_subtractions": 18,
        "binary_multiplications": 83,
        "binary_divisions": 2,
        "reduction_calls": 22,
        "reduction_additions": 61,
    }
    assert stages.operation_counts == expected_operation_counts(ny * nx)
    assert stages.minimum_density_divisor > 0
    assert stages.all_results_finite
    assert stages.context_flags == {
        "underflow": False,
        "overflow": False,
        "invalid": False,
        "division_by_zero": False,
        "inexact": True,
        "erange": False,
    }
    for stage in (
        stages.encoded_input,
        stages.equilibrium,
        stages.post_collision,
        stages.post_streaming,
        stages.post_filter,
    ):
        assert stage.shape == (ny, nx, 9)
        assert all(
            isinstance(value, gmpy2.mpfr)
            and value.precision == MPFR_PRECISION_BITS
            and value > 0
            for value in stage.flat
        )


def test_mpfr_backend_constants_expose_the_fixed_leaf_obstruction() -> None:
    constants = MPFRD2Q9Backend().constants
    weight_sum = sum(
        (fraction_from_mpfr(weight) for weight in constants.weights),
        Fraction(0),
    )
    filter_sum = fraction_from_mpfr(
        constants.filter_center
    ) + 4 * fraction_from_mpfr(constants.filter_neighbour)

    assert weight_sum - 1 == Fraction(
        1,
        154742504910672534362390528,
    )
    assert filter_sum - 1 == Fraction(
        5,
        618970019642690137449562112,
    )
    assert weight_sum != 1
    assert filter_sum != 1


def test_mpfr_backend_rejects_unregistered_state_encodings() -> None:
    backend = MPFRD2Q9Backend()

    with pytest.raises(ValueError, match="shape"):
        backend.evaluate_fraction_stages(np.zeros((2, 9), dtype=object))
    with pytest.raises(TypeError, match="rational"):
        bad_exact = _rest_state(1, 1)
        bad_exact[0, 0, 0] = object()
        backend.evaluate_fraction_stages(bad_exact)
    with pytest.raises(TypeError, match="gmpy2"):
        backend.evaluate_encoded_stages(
            np.zeros((1, 1, 9), dtype=object)
        )
    with mpfr_context():
        encoded = np.empty((1, 1, 9), dtype=object)
        encoded[:] = gmpy2.mpfr(1)
    encoded[0, 0, 0] = gmpy2.mpfr(1, precision=53)
    with pytest.raises(ValueError, match="85-bit"):
        backend.evaluate_encoded_stages(encoded)

    with pytest.raises(TypeError, match="integer"):
        expected_operation_counts(1.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="positive"):
        expected_operation_counts(0)
