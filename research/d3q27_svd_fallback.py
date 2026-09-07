"""Q012c1a: exception-only SVD fallback, preserving sealed scientific gates.

Normally converged pairs run through the original, unmodified implementation.
Only the SVD nonconvergence exception enables a gesvd solve of the same matrix.
"""

from __future__ import annotations

from dataclasses import replace
from itertools import combinations_with_replacement
from typing import Any

import numpy as np
from scipy.linalg import svd

from research import d3q27 as d3
from research import d3q27_damping as damping
from research import d3q27_quadratic as q


def factor_integrity(
    matrix: np.ndarray, u: np.ndarray, singular: np.ndarray, vh: np.ndarray
) -> dict:
    errors = {
        "reconstruction_relative_error": damping.relative_error((u * singular) @ vh, matrix),
        "left_orthogonality_error": float(np.linalg.norm(u.conj().T @ u - np.eye(len(singular)))),
        "right_orthogonality_error": float(
            np.linalg.norm(vh @ vh.conj().T - np.eye(len(singular)))
        ),
    }
    return {
        **errors,
        "passed": bool(np.isfinite(singular).all() and (singular >= 0).all())
        and all(np.isfinite(value) and value <= 1e-12 for value in errors.values()),
    }


def solve_gesvd(
    output: np.ndarray, inputs: np.ndarray, forcing: np.ndarray
) -> tuple[np.ndarray, dict, dict]:
    """Same Q012c rank, solution and record arithmetic with one explicit driver."""
    operator = q.homological_operator(output, inputs)
    forcing = np.asarray(forcing, dtype=complex)
    if forcing.shape != (len(output), len(inputs)) or not np.all(np.isfinite(forcing)):
        raise ValueError("forcing must be finite with output by input dimensions")
    u, singular, vh = svd(operator, full_matrices=False, check_finite=False, lapack_driver="gesvd")
    integrity = factor_integrity(operator, u, singular, vh)
    if not integrity["passed"]:
        raise np.linalg.LinAlgError("alternative SVD failed factor integrity")
    threshold = float(100 * np.finfo(float).eps * len(operator) * singular[0])
    retained = singular > threshold
    vector = forcing.reshape(-1, order="F")
    null_norm = float(np.linalg.norm(u[:, ~retained].conj().T @ vector))
    nonsingular = bool(np.all(retained))
    condition = float(singular[0] / singular[-1]) if nonsingular else None
    solution = -(vh[retained].conj().T @ ((u[:, retained].conj().T @ vector) / singular[retained]))
    solution = solution.reshape(forcing.shape, order="F")
    residual = float(
        np.linalg.norm(output @ solution - solution @ inputs + forcing)
        / max(float(np.linalg.norm(forcing)), 1e-14)
    )
    near = singular <= max(10 * singular[-1], 1e-4 * singular[0])
    status = (
        (
            "nonsingular_practical"
            if condition <= q.CONDITION_LIMIT
            else "nonsingular_ill_conditioned"
        )
        if nonsingular
        else (
            "singular_compatible"
            if null_norm <= 1e-10 * max(1, np.linalg.norm(forcing))
            else "singular_incompatible"
        )
    )
    return (
        solution,
        {
            "operator_dimension": len(operator),
            "numerical_rank": int(np.count_nonzero(retained)),
            "rank_threshold": threshold,
            "smallest_singular_value": float(singular[-1]),
            "largest_singular_value": float(singular[0]),
            "condition_number": condition,
            "minimum_eigenvalue_detuning": float(
                np.min(
                    np.abs(np.linalg.eigvals(output)[:, None] - np.linalg.eigvals(inputs)[None, :])
                )
            ),
            "forcing_norm": float(np.linalg.norm(forcing)),
            "left_null_forcing_norm": null_norm,
            "weak_left_subspace_dimension": int(np.count_nonzero(near)),
            "weak_left_forcing_norm": float(np.linalg.norm(u[:, near].conj().T @ vector)),
            "response_local_norm": float(np.linalg.norm(solution)),
            "solve_relative_residual": residual,
            "status": status,
            "passed": status == "nonsingular_practical" and residual <= 1e-10,
        },
        integrity,
    )


def solve_with_fallback(
    output: np.ndarray, inputs: np.ndarray, forcing: np.ndarray
) -> tuple[np.ndarray, dict, dict]:
    try:
        solution, record = q.solve_homological(output, inputs, forcing)
        return solution, record, {"driver": "gesdd", "fallback": False, "passed": True}
    except np.linalg.LinAlgError as error:
        if str(error) != "SVD did not converge":
            raise
        solution, record, integrity = solve_gesvd(output, inputs, forcing)
        return (
            solution,
            record,
            {"driver": "gesvd", "fallback": True, "original_error": str(error), **integrity},
        )


def scaled_problem(
    left: q.InputBlock,
    right: q.InputBlock,
    context: damping.CoefficientContext,
    eta: float,
    power: int,
) -> tuple:
    wave = q.canonical_wave(tuple(a + b for a, b in zip(left.wave, right.wave)), context.size)
    sector = context.sectors[wave]
    ml = damping.wave_multiplier(left.wave, context.size, eta, power)
    mr = damping.wave_multiplier(right.wave, context.size, eta, power)
    mo = damping.wave_multiplier(wave, context.size, eta, power)
    inputs, forcing, product_error = q.product_forcing(
        replace(left, dynamics=ml * left.dynamics),
        replace(right, dynamics=mr * right.dynamics),
        wave,
        context.size,
        context.omega * mo,
    )
    return sector, mo * sector.dynamics, inputs, forcing, product_error


def audit_pair(
    left: q.InputBlock,
    right: q.InputBlock,
    context: damping.CoefficientContext,
    eta: float,
    power: int,
) -> tuple[dict, dict]:
    try:
        record = damping.audit_scaled_pair(left, right, context, eta, power)
        return record, {"driver": "gesdd", "fallback": False, "passed": True}
    except np.linalg.LinAlgError as error:
        if str(error) != "SVD did not converge":
            raise
        original_error = str(error)
    sector, output, inputs, forcing, product_error = scaled_problem(
        left, right, context, eta, power
    )
    external_forcing = sector.basis.conj().T @ sector.projection @ forcing
    solution, record, integrity = solve_gesvd(output, inputs, external_forcing)
    population_response = sector.basis @ solution
    scale = max(1, float(np.linalg.norm(population_response)))
    gauge_error = float(np.linalg.norm(sector.selected_projector @ population_response) / scale)
    mean_error = (
        float(np.linalg.norm(d3.conserved_moment_matrix() @ population_response) / scale)
        if sector.wave == (0, 0, 0)
        else 0.0
    )
    mean_forcing = (
        float(np.linalg.norm(d3.conserved_moment_matrix() @ forcing))
        if sector.wave == (0, 0, 0)
        else 0.0
    )
    output_frame = context.frames.get(sector.wave)
    return {
        "left_wave": list(left.wave),
        "left_label": left.label,
        "right_wave": list(right.wave),
        "right_label": right.label,
        "output_wave": list(sector.wave),
        "output_is_selected": output_frame is not None,
        "product_dimension": len(inputs),
        "external_dimension": len(output),
        "symmetric_square": left.key == right.key,
        **record,
        "response_global_l2_norm": record["response_local_norm"] / context.size**1.5,
        "internal_forcing_norm": 0.0
        if output_frame is None
        else float(np.linalg.norm(output_frame.dual @ forcing)),
        "graph_gauge_error": gauge_error,
        "zero_wave_moment_error": mean_error,
        "zero_wave_forcing_moment_error": mean_forcing,
        "structural_error": max(
            product_error, sector.structural_error, gauge_error, mean_error, mean_forcing
        ),
        "passed": record["passed"] and max(gauge_error, mean_error) <= q.STRUCTURAL_TOL,
    }, {"driver": "gesvd", "fallback": True, "original_error": original_error, **integrity}


def coefficient_screen(
    context: damping.CoefficientContext, eta: float, power: int
) -> tuple[dict, dict]:
    damping.parameters(eta, power)
    records, drivers, fallbacks = [], [], []
    for ordinal, (left, right) in enumerate(combinations_with_replacement(context.blocks, 2)):
        record, backend = audit_pair(left, right, context, eta, power)
        records.append(record)
        drivers.append(backend["driver"])
        if backend["fallback"]:
            fallbacks.append({"pair_ordinal_zero_based": ordinal, **backend})
    return damping.summarize_pairs(records, len(context.blocks)), {
        "pair_drivers": drivers,
        "fallback_count": len(fallbacks),
        "fallback_records": fallbacks,
        "passed": len(drivers) == 3081 and all(r["passed"] for r in fallbacks),
    }


def backend_controls(failure: dict) -> dict[str, Any]:
    context = damping.build_context(failure["size"], failure["omega"])
    left = next(
        b
        for b in context.frames[tuple(failure["left_wave"])].blocks
        if b.label == failure["left_label"]
    )
    right = next(
        b
        for b in context.frames[tuple(failure["right_wave"])].blocks
        if b.label == failure["right_label"]
    )
    sector, output, inputs, forcing, _ = scaled_problem(
        left, right, context, failure["eta"], failure["power"]
    )
    operator = q.homological_operator(output, inputs)
    stored = np.empty(operator.shape, dtype=complex)
    stored.real, stored.imag = failure["operator_real"], failure["operator_imag"]
    identical = operator.tobytes() == stored.tobytes()
    repetitions = []
    for repeat in range(3):
        _solution, record, backend = solve_with_fallback(
            output, inputs, sector.basis.conj().T @ sector.projection @ forcing
        )
        repetitions.append({"repeat": repeat, "record": record, "backend": backend})
    rng = np.random.default_rng(2026090710)
    stable = np.array(((0.74 * np.exp(0.21j), 0.035j), (0, 0.68 * np.exp(-0.31j))))
    external = np.array(((0.23, 0.07j), (0, 0.29)), dtype=complex)
    symmetric = q.symmetric_square_basis(2)
    product = symmetric.T @ np.kron(stable, stable) @ symmetric
    known = rng.standard_normal((2, 3)) + 1j * rng.standard_normal((2, 3))
    rhs = known @ product - external @ known
    original, old_record = q.solve_homological(external, product, rhs)
    alternative, new_record, factors = solve_gesvd(external, product, rhs)
    singular_cases = []
    for name, delta, rhs2 in (
        ("compatible", 0, [0, 1]),
        ("incompatible", 0, [1, 0]),
        ("ill_conditioned", 1e-11, [1, 1]),
    ):
        _h, row, backend = solve_with_fallback(
            np.diag((0.49 + delta, 0.2)), np.array([[0.49]]), np.array(rhs2)[:, None]
        )
        singular_cases.append({"name": name, "record": row, "backend": backend})
    errors = {
        "gesdd": damping.relative_error(original, known),
        "gesvd": damping.relative_error(alternative, known),
    }
    gates = {
        "bitwise_failure_matrix_reconstruction": identical,
        "three_exception_only_replays": all(
            r["backend"]["fallback"] and r["backend"]["passed"] and r["record"]["passed"]
            for r in repetitions
        ),
        "known_complex_quadratic_solution": max(errors.values()) <= 1e-12
        and old_record["passed"]
        and new_record["passed"]
        and factors["passed"],
        "mathematical_failures_not_switched_or_accepted": all(
            not r["record"]["passed"] and not r["backend"]["fallback"] for r in singular_cases
        ),
    }
    return {
        "repetitions": repetitions,
        "known_solution_errors": errors,
        "mathematical_negative_controls": singular_cases,
        "gates": gates,
        "passed": all(gates.values()),
    }
