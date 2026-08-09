"""Q011j rigorous interval Krawczyk proof for the repaired forced fixed point."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import gmpy2
import numpy as np
import numpy.typing as npt
from scipy import linalg

import research.q011i_exact_zero_mean_repair as q011i
from research.q007x_mpfr_backend import fraction_from_mpfr
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    RationalInterval,
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

Array = npt.NDArray[np.float64]
ExactVector = list[Fraction]
IntervalVector = list[RationalInterval]
ExactMatrix = list[list[Fraction]]
IntervalMatrix = list[list[RationalInterval]]

SIZE = 17
POPULATION_COUNT = 9
STRIPE_DIMENSION = SIZE * POPULATION_COUNT
COORDINATE_DIMENSION = STRIPE_DIMENSION - 3
PIVOT_INDICES = (0, 1, 2)
FREE_INDICES = tuple(index for index in range(STRIPE_DIMENSION) if index not in PIVOT_INDICES)
TARGET_MOMENTS = (Fraction(SIZE), Fraction(0), Fraction(0))

VELOCITIES = (
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
WEIGHTS = (
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
OMEGA = Fraction(3, 2)
ETA = Fraction(1, 100)
FILTER_CENTER = Fraction(1) - ETA / 2
FILTER_NEIGHBOUR = ETA / 4

Q011I_ARTIFACT_SHA256 = "1c8b11a3ae47895a79639a5cfe901ec936fbdde8d10273c56c1578b9a88780ea"
Q011I_RUNNER_SHA256 = "2cec0472422ba02bb925e8c90336000058def7c36303479a4037405f873b9b88"
Q011I_INPUT_DIGEST = "81a1dc3f9fe934d8e9391dbfe6b80701d68c04b7db954da2f62e92b581dd5b51"
Q011I_REPAIR_DIGEST = "910a82fa1485ce8ad6b488c5bb71ad0c8bcb12b98b6202ebc3805caa8f4a3239"
Q011I_FIXED_POINT_DIGEST = "3adfbcfc7d5e9c3396bbfb60b8d10dce6ff080b90097b82f40b4c057b8518f1e"
Q011I_SPECTRUM_DIGEST = "5e63b9cc22a662238391dc83b8de1a81eb259af25b3ad2335e481bb0cf83466d"
Q011I_RESULT_DIGEST = "ac94658b95d2ae1f190fab57af3bd80dbf50a4addd37f6bb7bee27d6aa1d2398"
Q011I_WAVEFORM_SHA256 = "025d6122db8e0d3512224ce4a2af82d57b5728ce0c7450425436218dd561bcbf"
Q011I_SOURCE_SHA256 = "24bb558464cce4ac154b3f2574bd1fe816d11d58c9365e8312f12b0a389df490"
Q011I_STATE_SHA256 = "612ef4aca91a5c0100286988e0e7979342a9046c3c78fe60ee59ca4e232a7613"
SEALED_PACKAGE_SOURCE_SHA256 = "114228341b120021f1269ca22ff2503165a0c13dc4f146b8308e94298630f4c2"

RADIUS_CANDIDATES = tuple(Fraction(1, 10**power) for power in range(12, 2, -1))
PRIMARY_PRECISION_BITS = 256
REPLAY_PRECISION_BITS = 384
KRAWCZYK_CAP = Fraction(9, 10)
MAXIMUM_POINT_INVERSE_DEFECT = Fraction(1, 10**8)
MAXIMUM_CENTER_PIVOT_CORRECTION = Fraction(1, 10**14)
MAXIMUM_MAP_RELATIVE_DISCREPANCY = 1.0e-12
MAXIMUM_JACOBIAN_RELATIVE_DISCREPANCY = 1.0e-12
EXPECTED_LIFT_INFINITY_NORM = 186


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _fraction_from_float(value: float | np.floating[Any]) -> Fraction:
    return Fraction.from_float(float(value))


def _fraction_sequence_sha256(values: list[Fraction] | tuple[Fraction, ...]) -> str:
    return q011i.q011b._canonical_json_sha256(
        [[hex(value.numerator), hex(value.denominator)] for value in values]
    )


def _fraction_matrix_sha256(matrix: ExactMatrix) -> str:
    return _fraction_sequence_sha256([value for row in matrix for value in row])


def _interval_record(value: RationalInterval) -> dict[str, Any]:
    return {
        "lower": _fraction_record(value.lower),
        "upper": _fraction_record(value.upper),
        "width": _fraction_record(value.width),
    }


def _maximum_absolute(value: RationalInterval) -> Fraction:
    return max(abs(value.lower), abs(value.upper))


def _interval_reciprocal(value: RationalInterval) -> RationalInterval:
    if value.lower <= 0 <= value.upper:
        raise ZeroDivisionError("interval reciprocal contains zero")
    endpoints = (Fraction(1, value.lower), Fraction(1, value.upper))
    return RationalInterval(min(endpoints), max(endpoints))


def _interval_sum(values: list[RationalInterval]) -> RationalInterval:
    total = RationalInterval.point(0)
    for value in values:
        total = total + value
    return total


def _signed_interval(value: RationalInterval, multiplier: int | Fraction) -> RationalInterval:
    return value.scale(multiplier)


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


def _proof_context(precision: int, rounding: int) -> gmpy2.context:
    return gmpy2.context(
        precision=precision,
        round=rounding,
        emin=-10_000,
        emax=10_000,
        subnormalize=False,
        trap_underflow=True,
        trap_overflow=True,
        trap_divzero=True,
        trap_invalid=True,
        trap_inexact=False,
        allow_complex=False,
        rational_division=False,
        allow_release_gil=False,
    )


def _context_flags(context: gmpy2.context) -> dict[str, bool]:
    return {
        "underflow": bool(context.underflow),
        "overflow": bool(context.overflow),
        "invalid": bool(context.invalid),
        "division_by_zero": bool(context.divzero),
        "erange": bool(context.erange),
        "inexact": bool(context.inexact),
    }


def _mpq(value: Fraction) -> gmpy2.mpq:
    return gmpy2.mpq(value.numerator, value.denominator)


def _sealed_q011i_artifact_audit() -> tuple[dict[str, Any], dict[str, Any]]:
    artifact_path = (
        Path(q011i.__file__).resolve().parent / "artifacts" / "q011i_exact_zero_mean_repair.json"
    )
    runner_path = Path(q011i.__file__).resolve()
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    observed_digests = tuple(
        cycle[key]
        for key in (
            "input_digest_sha256",
            "repair_digest_sha256",
            "fixed_point_digest_sha256",
            "spectrum_digest_sha256",
            "result_digest_sha256",
        )
    )
    fixed_point = cycle["repaired_fixed_point_bridge_audit"]
    checks = {
        "artifact_sha256_matches": _file_sha256(artifact_path) == Q011I_ARTIFACT_SHA256,
        "runner_sha256_matches": (
            _file_sha256(runner_path) == Q011I_RUNNER_SHA256
            and artifact["runner_source"]["sha256"] == Q011I_RUNNER_SHA256
        ),
        "package_source_matches": (
            artifact["source"]["package_source_sha256"]
            == SEALED_PACKAGE_SOURCE_SHA256
            == source_metadata()["package_source_sha256"]
        ),
        "five_digests_match": observed_digests
        == (
            Q011I_INPUT_DIGEST,
            Q011I_REPAIR_DIGEST,
            Q011I_FIXED_POINT_DIGEST,
            Q011I_SPECTRUM_DIGEST,
            Q011I_RESULT_DIGEST,
        ),
        "valid_accepted_outcome_reproduces": (
            artifact["study_gate"] == "passed"
            and artifact["scientific_outcome"] == "accepted"
            and cycle["study_validity"] == "passed"
            and cycle["hypothesis_outcome"] == "accepted"
            and len(cycle["validity_gates"]) == 6
            and all(gate["passed"] for gate in cycle["validity_gates"].values())
            and len(cycle["hypothesis_gates"]) == 4
            and all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
        ),
        "registered_hashes_match": (
            cycle["waveform_repair_audit"]["repaired_waveform_sha256"] == Q011I_WAVEFORM_SHA256
            and cycle["source_repair_audit"]["source_sha256"] == Q011I_SOURCE_SHA256
            and fixed_point["representative_repaired_state_sha256"] == Q011I_STATE_SHA256
        ),
        "claim_boundary_and_nontransfer_reproduce": (
            cycle["decision_consequence"]["interval_fixed_point_proof_is_authorized"]
            and not cycle["decision_consequence"]["q011b_numerical_accepted_outcome_changed"]
            and not cycle["decision_consequence"][
                "q011e_through_q011h_coefficients_transfer_to_repaired_map"
            ]
            and not cycle["decision_consequence"]["forced_ssm_exists_or_is_unique"]
        ),
        "artifact_is_strict_finite_json": bool(
            _all_numeric_values_finite(artifact) and _strict_json_serializable(artifact)
        ),
    }
    return (
        {
            "artifact": {
                "filename": artifact_path.name,
                "sha256": _file_sha256(artifact_path),
                "runner_filename": runner_path.name,
                "runner_sha256": _file_sha256(runner_path),
                "input_digest_sha256": observed_digests[0],
                "repair_digest_sha256": observed_digests[1],
                "fixed_point_digest_sha256": observed_digests[2],
                "spectrum_digest_sha256": observed_digests[3],
                "result_digest_sha256": observed_digests[4],
                "study_validity": cycle["study_validity"],
                "hypothesis_outcome": cycle["hypothesis_outcome"],
                "scientific_classification": cycle["scientific_classification"],
            },
            "checks": checks,
            "passed": all(checks.values()),
        },
        artifact,
    )


def _lift_linear_matrix() -> npt.NDArray[np.int64]:
    matrix = np.zeros((STRIPE_DIMENSION, COORDINATE_DIMENSION), dtype=np.int64)
    for column, flat_index in enumerate(FREE_INDICES):
        matrix[flat_index, column] = 1
        cx, cy = VELOCITIES[flat_index % POPULATION_COUNT]
        matrix[1, column] = -cx
        matrix[2, column] = -cy
        matrix[0, column] = -1 + cx + cy
    return matrix


def _extract_exact(state: ExactVector) -> ExactVector:
    return [state[index] for index in FREE_INDICES]


def _lift_exact(coordinate: ExactVector) -> ExactVector:
    if len(coordinate) != COORDINATE_DIMENSION:
        raise ValueError("coordinate has the wrong dimension")
    state = [Fraction(0) for _ in range(STRIPE_DIMENSION)]
    for flat_index, value in zip(FREE_INDICES, coordinate, strict=True):
        state[flat_index] = value
    free_mass = sum(coordinate, Fraction(0))
    free_momentum_x = sum(
        (
            VELOCITIES[flat_index % POPULATION_COUNT][0] * value
            for flat_index, value in zip(FREE_INDICES, coordinate, strict=True)
        ),
        Fraction(0),
    )
    free_momentum_y = sum(
        (
            VELOCITIES[flat_index % POPULATION_COUNT][1] * value
            for flat_index, value in zip(FREE_INDICES, coordinate, strict=True)
        ),
        Fraction(0),
    )
    state[1] = -free_momentum_x
    state[2] = -free_momentum_y
    state[0] = Fraction(SIZE) - free_mass - state[1] - state[2]
    return state


def _lift_interval(coordinate: IntervalVector) -> IntervalVector:
    if len(coordinate) != COORDINATE_DIMENSION:
        raise ValueError("coordinate has the wrong dimension")
    state = [RationalInterval.point(0) for _ in range(STRIPE_DIMENSION)]
    for flat_index, value in zip(FREE_INDICES, coordinate, strict=True):
        state[flat_index] = value
    free_mass = _interval_sum(coordinate)
    free_momentum_x = _interval_sum(
        [
            _signed_interval(value, VELOCITIES[index % POPULATION_COUNT][0])
            for index, value in zip(FREE_INDICES, coordinate, strict=True)
        ]
    )
    free_momentum_y = _interval_sum(
        [
            _signed_interval(value, VELOCITIES[index % POPULATION_COUNT][1])
            for index, value in zip(FREE_INDICES, coordinate, strict=True)
        ]
    )
    state[1] = -free_momentum_x
    state[2] = -free_momentum_y
    state[0] = RationalInterval.point(SIZE) - free_mass - state[1] - state[2]
    return state


def _exact_moments(state: ExactVector) -> tuple[Fraction, Fraction, Fraction]:
    mass = sum(state, Fraction(0))
    momentum_x = sum(
        (VELOCITIES[index % POPULATION_COUNT][0] * value for index, value in enumerate(state)),
        Fraction(0),
    )
    momentum_y = sum(
        (VELOCITIES[index % POPULATION_COUNT][1] * value for index, value in enumerate(state)),
        Fraction(0),
    )
    return mass, momentum_x, momentum_y


def _determinant_three(matrix: list[list[Fraction]]) -> Fraction:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def _repaired_source_exact() -> tuple[ExactVector, Array, dict[str, Any]]:
    waveform, waveform_audit = q011i._waveform_repair_audit()
    source, source_audit = q011i._source_repair_audit(waveform)
    exact = [_fraction_from_float(value) for value in source.ravel()]
    audit = {
        "waveform_sha256": waveform_audit["repaired_waveform_sha256"],
        "source_sha256": source_audit["source_sha256"],
        "waveform_exact_sum": waveform_audit["repaired_exact_sum"],
        "source_global_exact_moment_ledger": source_audit["global_exact_moment_ledger"],
        "checks": {
            "waveform_repair_reproduces": (
                waveform_audit["passed"]
                and waveform_audit["repaired_waveform_sha256"] == Q011I_WAVEFORM_SHA256
            ),
            "source_repair_reproduces": (
                source_audit["passed"] and source_audit["source_sha256"] == Q011I_SOURCE_SHA256
            ),
            "global_exact_ledger_is_zero": all(
                record["numerator_base16"] == "0x0"
                for record in source_audit["global_exact_moment_ledger"]
            ),
        },
    }
    audit["passed"] = all(audit["checks"].values())
    return exact, np.asarray(source, dtype=np.float64), audit


def _exact_equilibrium(state: ExactVector) -> ExactVector:
    result: ExactVector = []
    for site in range(SIZE):
        row = state[site * POPULATION_COUNT : (site + 1) * POPULATION_COUNT]
        density = sum(row, Fraction(0))
        if density <= 0:
            raise ValueError("exact equilibrium requires positive density")
        momentum_x = sum(
            (velocity[0] * value for velocity, value in zip(VELOCITIES, row, strict=True)),
            Fraction(0),
        )
        momentum_y = sum(
            (velocity[1] * value for velocity, value in zip(VELOCITIES, row, strict=True)),
            Fraction(0),
        )
        momentum_square = momentum_x * momentum_x + momentum_y * momentum_y
        for weight, (cx, cy) in zip(WEIGHTS, VELOCITIES, strict=True):
            projection = cx * momentum_x + cy * momentum_y
            result.append(
                weight
                * (
                    density
                    + 3 * projection
                    + Fraction(9, 2) * projection * projection / density
                    - Fraction(3, 2) * momentum_square / density
                )
            )
    return result


def _exact_repaired_stripe_step(state: ExactVector, source: ExactVector) -> ExactVector:
    if len(state) != STRIPE_DIMENSION or len(source) != STRIPE_DIMENSION:
        raise ValueError("stripe state or source has the wrong dimension")
    equilibrium = _exact_equilibrium(state)
    post_source = [
        (Fraction(1) - OMEGA) * value + OMEGA * eq + forcing
        for value, eq, forcing in zip(state, equilibrium, source, strict=True)
    ]
    streamed = [Fraction(0) for _ in range(STRIPE_DIMENSION)]
    for site in range(SIZE):
        for population, (_, cy) in enumerate(VELOCITIES):
            source_site = (site - cy) % SIZE
            streamed[site * POPULATION_COUNT + population] = post_source[
                source_site * POPULATION_COUNT + population
            ]
    output = [Fraction(0) for _ in range(STRIPE_DIMENSION)]
    for site in range(SIZE):
        lower = (site - 1) % SIZE
        upper = (site + 1) % SIZE
        for population in range(POPULATION_COUNT):
            index = site * POPULATION_COUNT + population
            output[index] = (
                FILTER_CENTER * streamed[index]
                + FILTER_NEIGHBOUR * streamed[lower * POPULATION_COUNT + population]
                + FILTER_NEIGHBOUR * streamed[upper * POPULATION_COUNT + population]
            )
    return output


def _equilibrium_derivative_blocks(
    state: IntervalVector,
) -> tuple[list[list[list[RationalInterval]]], list[RationalInterval]]:
    blocks: list[list[list[RationalInterval]]] = []
    densities: list[RationalInterval] = []
    for site in range(SIZE):
        row = state[site * POPULATION_COUNT : (site + 1) * POPULATION_COUNT]
        density = _interval_sum(row)
        if density.lower <= 0:
            raise ValueError("interval equilibrium requires positive density")
        densities.append(density)
        momentum_x = _interval_sum(
            [value.scale(velocity[0]) for velocity, value in zip(VELOCITIES, row, strict=True)]
        )
        momentum_y = _interval_sum(
            [value.scale(velocity[1]) for velocity, value in zip(VELOCITIES, row, strict=True)]
        )
        inverse_density = _interval_reciprocal(density)
        inverse_density_square = inverse_density * inverse_density
        momentum_square = momentum_x * momentum_x + momentum_y * momentum_y
        block: list[list[RationalInterval]] = []
        for weight, (cqx, cqy) in zip(WEIGHTS, VELOCITIES, strict=True):
            projected_q = momentum_x.scale(cqx) + momentum_y.scale(cqy)
            output_row: list[RationalInterval] = []
            for cpx, cpy in VELOCITIES:
                q_dot_p = cqx * cpx + cqy * cpy
                projected_p = momentum_x.scale(cpx) + momentum_y.scale(cpy)
                derivative = (
                    RationalInterval.point(1 + 3 * q_dot_p)
                    + (projected_q * inverse_density).scale(9 * q_dot_p)
                    - (projected_q * projected_q * inverse_density_square).scale(Fraction(9, 2))
                    - (projected_p * inverse_density).scale(3)
                    + (momentum_square * inverse_density_square).scale(Fraction(3, 2))
                ).scale(weight)
                output_row.append(derivative)
            block.append(output_row)
        blocks.append(block)
    return blocks, densities


def _reduced_derivative_factors(
    state: IntervalVector,
) -> tuple[IntervalMatrix, IntervalMatrix, list[RationalInterval]]:
    equilibrium_blocks, densities = _equilibrium_derivative_blocks(state)
    collision_blocks: list[list[list[RationalInterval]]] = []
    for block in equilibrium_blocks:
        collision_blocks.append(
            [
                [
                    value.scale(OMEGA)
                    + RationalInterval.point((Fraction(1) - OMEGA) * int(row == column))
                    for column, value in enumerate(output_row)
                ]
                for row, output_row in enumerate(block)
            ]
        )

    free_lookup = {flat_index: column for column, flat_index in enumerate(FREE_INDICES)}
    s_matrix: IntervalMatrix = []
    a_matrix: IntervalMatrix = []
    for output_flat in FREE_INDICES:
        site, population = divmod(output_flat, POPULATION_COUNT)
        cy = VELOCITIES[population][1]
        sources = (
            ((site - cy) % SIZE, FILTER_CENTER),
            ((site - 1 - cy) % SIZE, FILTER_NEIGHBOUR),
            ((site + 1 - cy) % SIZE, FILTER_NEIGHBOUR),
        )
        sparse_row = [RationalInterval.point(0) for _ in range(COORDINATE_DIMENSION)]
        pivot_row = [RationalInterval.point(0) for _ in PIVOT_INDICES]
        for source_site, filter_weight in sources:
            collision_row = collision_blocks[source_site][population]
            for input_population, derivative in enumerate(collision_row):
                input_flat = source_site * POPULATION_COUNT + input_population
                contribution = derivative.scale(filter_weight)
                if input_flat in free_lookup:
                    column = free_lookup[input_flat]
                    sparse_row[column] = sparse_row[column] + contribution
                else:
                    pivot_column = PIVOT_INDICES.index(input_flat)
                    pivot_row[pivot_column] = pivot_row[pivot_column] + contribution
        sparse_row[free_lookup[output_flat]] = sparse_row[
            free_lookup[output_flat]
        ] - RationalInterval.point(1)
        s_matrix.append(sparse_row)
        a_matrix.append(pivot_row)
    return s_matrix, a_matrix, densities


def _point_matrix(matrix: IntervalMatrix) -> ExactMatrix:
    result: ExactMatrix = []
    for row in matrix:
        if any(value.width != 0 for value in row):
            raise ValueError("point matrix expected")
        result.append([value.lower for value in row])
    return result


def _combine_reduced_factors(
    sparse: IntervalMatrix,
    pivot_action: IntervalMatrix,
    lift_matrix: npt.NDArray[np.int64],
) -> IntervalMatrix:
    pivot_lift = lift_matrix[list(PIVOT_INDICES), :]
    result: IntervalMatrix = []
    for row, pivot_row in zip(sparse, pivot_action, strict=True):
        combined: list[RationalInterval] = []
        for column, value in enumerate(row):
            total = value
            for pivot_column in range(3):
                multiplier = int(pivot_lift[pivot_column, column])
                if multiplier:
                    total = total + pivot_row[pivot_column].scale(multiplier)
            combined.append(total)
        result.append(combined)
    return result


def _quadrature_audit() -> dict[str, Any]:
    zeroth = sum(WEIGHTS, Fraction(0))
    first = [
        sum(
            (weight * velocity[axis] for weight, velocity in zip(WEIGHTS, VELOCITIES, strict=True)),
            Fraction(0),
        )
        for axis in range(2)
    ]
    second = [
        [
            sum(
                (
                    weight * velocity[left] * velocity[right]
                    for weight, velocity in zip(WEIGHTS, VELOCITIES, strict=True)
                ),
                Fraction(0),
            )
            for right in range(2)
        ]
        for left in range(2)
    ]
    third = [
        [
            [
                sum(
                    (
                        weight * velocity[a] * velocity[b] * velocity[c]
                        for weight, velocity in zip(WEIGHTS, VELOCITIES, strict=True)
                    ),
                    Fraction(0),
                )
                for c in range(2)
            ]
            for b in range(2)
        ]
        for a in range(2)
    ]
    checks = {
        "zeroth_moment_is_one": zeroth == 1,
        "first_moments_are_zero": first == [0, 0],
        "second_moments_are_isotropic": second
        == [[Fraction(1, 3), Fraction(0)], [Fraction(0), Fraction(1, 3)]],
        "third_moments_are_zero": all(
            value == 0 for plane in third for row in plane for value in row
        ),
        "filter_weights_sum_to_one": FILTER_CENTER + 2 * FILTER_NEIGHBOUR == 1,
    }
    return {
        "zeroth_moment": _fraction_record(zeroth),
        "first_moments": [_fraction_record(value) for value in first],
        "second_moments": [[_fraction_record(value) for value in row] for row in second],
        "third_moments": [
            [[_fraction_record(value) for value in row] for row in plane] for plane in third
        ],
        "filter_center": _fraction_record(FILTER_CENTER),
        "filter_neighbour": _fraction_record(FILTER_NEIGHBOUR),
        "checks": checks,
        "passed": all(checks.values()),
    }


def _coordinate_audit(
    q011i_artifact: dict[str, Any],
) -> tuple[ExactVector, ExactVector, Array, npt.NDArray[np.int64], dict[str, Any]]:
    sealed_values = q011i_artifact["cycle"]["repaired_fixed_point_bridge_audit"][
        "physical_fourier_audit"
    ]["stripe_state"]
    sealed_state_array = np.asarray(sealed_values, dtype=np.float64).reshape(SIZE, 1, 9)
    sealed_state = [_fraction_from_float(value) for value in sealed_state_array.ravel()]
    coordinate = _extract_exact(sealed_state)
    lifted = _lift_exact(coordinate)
    lift_matrix = _lift_linear_matrix()
    pivot_matrix = [
        [Fraction((1, *VELOCITIES[pivot])[moment]) for pivot in PIVOT_INDICES]
        for moment in range(3)
    ]
    pivot_determinant = _determinant_three(pivot_matrix)
    pivot_corrections = [lifted[index] - sealed_state[index] for index in PIVOT_INDICES]
    maximum_pivot_correction = max(abs(value) for value in pivot_corrections)
    row_sums = np.sum(np.abs(lift_matrix), axis=1)
    column_sums = np.sum(np.abs(lift_matrix), axis=0)
    rank = int(np.linalg.matrix_rank(lift_matrix.astype(np.float64)))
    checks = {
        "sealed_state_hash_matches": q011i.q011b._array_sha256(sealed_state_array)
        == Q011I_STATE_SHA256,
        "dimensions_are_registered": (
            lift_matrix.shape == (STRIPE_DIMENSION, COORDINATE_DIMENSION)
            and len(FREE_INDICES) == COORDINATE_DIMENSION
        ),
        "pivot_matrix_determinant_is_one": pivot_determinant == 1,
        "lift_rank_is_registered": rank == COORDINATE_DIMENSION,
        "lift_infinity_norm_is_registered": int(np.max(row_sums)) == EXPECTED_LIFT_INFINITY_NORM,
        "extraction_roundtrip_is_exact": _extract_exact(lifted) == coordinate,
        "lifted_center_moments_are_exact": _exact_moments(lifted) == TARGET_MOMENTS,
        "free_entries_match_sealed_state": all(
            lifted[index] == sealed_state[index] for index in FREE_INDICES
        ),
        "only_pivots_change": all(
            lifted[index] == sealed_state[index] or index in PIVOT_INDICES
            for index in range(STRIPE_DIMENSION)
        ),
        "pivot_correction_within_registered_bound": maximum_pivot_correction
        <= MAXIMUM_CENTER_PIVOT_CORRECTION,
    }
    audit = {
        "pivot_indices": list(PIVOT_INDICES),
        "pivot_velocities": [list(VELOCITIES[index]) for index in PIVOT_INDICES],
        "free_index_count": len(FREE_INDICES),
        "free_index_sha256": q011i.q011b._canonical_json_sha256(list(FREE_INDICES)),
        "pivot_moment_matrix": [[_fraction_record(value) for value in row] for row in pivot_matrix],
        "pivot_moment_determinant": _fraction_record(pivot_determinant),
        "lift_matrix_shape": list(lift_matrix.shape),
        "lift_matrix_rank": rank,
        "lift_infinity_operator_norm": int(np.max(row_sums)),
        "lift_one_operator_norm": int(np.max(column_sums)),
        "lift_matrix_sha256": q011i.q011b._array_sha256(lift_matrix),
        "sealed_state_sha256": q011i.q011b._array_sha256(sealed_state_array),
        "coordinate_exact_sha256": _fraction_sequence_sha256(coordinate),
        "lifted_center_exact_sha256": _fraction_sequence_sha256(lifted),
        "pivot_corrections": [_fraction_record(value) for value in pivot_corrections],
        "maximum_pivot_correction": _fraction_record(maximum_pivot_correction),
        "lifted_center_moments": [_fraction_record(value) for value in _exact_moments(lifted)],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return coordinate, lifted, sealed_state_array, lift_matrix, audit


def _oracle_audit(
    coordinate: ExactVector,
    lifted: ExactVector,
    lift_matrix: npt.NDArray[np.int64],
    source_exact: ExactVector,
    source_float: Array,
) -> tuple[ExactVector, ExactMatrix, ExactMatrix, ExactMatrix, dict[str, Any]]:
    exact_output = _exact_repaired_stripe_step(lifted, source_exact)
    exact_residual = [output - value for output, value in zip(exact_output, lifted, strict=True)]
    reduced_residual = _extract_exact(exact_residual)
    point_state = [RationalInterval.point(value) for value in lifted]
    sparse_interval, pivot_interval, densities = _reduced_derivative_factors(point_state)
    sparse_point = _point_matrix(sparse_interval)
    pivot_point = _point_matrix(pivot_interval)
    combined_point = _point_matrix(
        _combine_reduced_factors(sparse_interval, pivot_interval, lift_matrix)
    )

    state_float = np.asarray([float(value) for value in lifted], dtype=np.float64).reshape(
        SIZE, 1, POPULATION_COUNT
    )
    exact_output_float = np.asarray(
        [float(value) for value in exact_output], dtype=np.float64
    ).reshape(SIZE, 1, POPULATION_COUNT)
    binary_output = q011i.repaired_stripe_step(state_float, source_float)
    map_denominator = max(float(np.linalg.norm(exact_output_float)), np.finfo(float).tiny)
    map_discrepancy = float(np.linalg.norm(binary_output - exact_output_float) / map_denominator)

    analytic = q011i.q011b.RectangularFilteredBGKJacobian.at_state(
        state_float,
        q011i.q011b.OMEGA,
        q011i.q011b.ETA,
    )
    lift_float = lift_matrix.astype(np.float64)
    independent_reduced = analytic.matmat(lift_float)[list(FREE_INDICES), :] - np.eye(
        COORDINATE_DIMENSION
    )
    exact_reduced_float = np.asarray(combined_point, dtype=np.float64)
    jacobian_denominator = max(float(np.linalg.norm(exact_reduced_float)), np.finfo(float).tiny)
    jacobian_discrepancy = float(
        np.linalg.norm(independent_reduced - exact_reduced_float) / jacobian_denominator
    )
    jacobian_maximum_absolute_discrepancy = float(
        np.max(np.abs(independent_reduced - exact_reduced_float))
    )

    output_moments = _exact_moments(exact_output)
    residual_moments = _exact_moments(exact_residual)
    quadrature = _quadrature_audit()
    source_moments = _exact_moments(source_exact)
    pivot_residual = [exact_residual[index] for index in PIVOT_INDICES]
    reduced_zero_implies_full_zero = (
        _determinant_three(
            [
                [Fraction((1, *VELOCITIES[pivot])[moment]) for pivot in PIVOT_INDICES]
                for moment in range(3)
            ]
        )
        == 1
    )
    checks = {
        "quadrature_and_filter_identities_are_exact": quadrature["passed"],
        "source_global_moments_are_exact_zero": source_moments == (0, 0, 0),
        "center_map_preserves_exact_moments": (
            _exact_moments(lifted) == TARGET_MOMENTS
            and output_moments == TARGET_MOMENTS
            and residual_moments == (0, 0, 0)
        ),
        "reduced_zero_implies_full_zero_structurally": reduced_zero_implies_full_zero,
        "x_independent_filter_reduction_is_exact": (
            Fraction(1) - ETA + 2 * FILTER_NEIGHBOUR == FILTER_CENTER
            and FILTER_CENTER + 2 * FILTER_NEIGHBOUR == 1
        ),
        "binary64_map_comparison_within_tolerance": map_discrepancy
        <= MAXIMUM_MAP_RELATIVE_DISCREPANCY,
        "analytic_jacobian_comparison_within_tolerance": jacobian_discrepancy
        <= MAXIMUM_JACOBIAN_RELATIVE_DISCREPANCY,
        "point_density_is_strictly_positive": min(value.lower for value in densities) > 0,
        "all_exact_objects_have_registered_dimensions": (
            len(coordinate) == COORDINATE_DIMENSION
            and len(reduced_residual) == COORDINATE_DIMENSION
            and len(combined_point) == COORDINATE_DIMENSION
            and all(len(row) == COORDINATE_DIMENSION for row in combined_point)
        ),
    }
    audit = {
        "exact_output_sha256": _fraction_sequence_sha256(exact_output),
        "exact_full_residual_sha256": _fraction_sequence_sha256(exact_residual),
        "exact_reduced_residual_sha256": _fraction_sequence_sha256(reduced_residual),
        "exact_reduced_jacobian_sha256": _fraction_matrix_sha256(combined_point),
        "exact_sparse_factor_sha256": _fraction_matrix_sha256(sparse_point),
        "exact_pivot_factor_sha256": _fraction_matrix_sha256(pivot_point),
        "maximum_exact_reduced_residual_absolute_value": _fraction_record(
            max(abs(value) for value in reduced_residual)
        ),
        "binary64_map_relative_l2_discrepancy": map_discrepancy,
        "analytic_jacobian_relative_frobenius_discrepancy": jacobian_discrepancy,
        "analytic_jacobian_maximum_absolute_discrepancy": (jacobian_maximum_absolute_discrepancy),
        "minimum_point_density": _fraction_record(min(value.lower for value in densities)),
        "input_moments": [_fraction_record(value) for value in _exact_moments(lifted)],
        "output_moments": [_fraction_record(value) for value in output_moments],
        "residual_moments": [_fraction_record(value) for value in residual_moments],
        "pivot_residual_at_center": [_fraction_record(value) for value in pivot_residual],
        "quadrature_audit": quadrature,
        "checks": checks,
        "passed": all(checks.values()),
    }
    return reduced_residual, combined_point, sparse_point, pivot_point, audit


def _radius_interval_audit(
    coordinate: ExactVector,
    point_jacobian: ExactMatrix,
    lift_matrix: npt.NDArray[np.int64],
) -> tuple[list[dict[str, Any]], list[Fraction]]:
    records: list[dict[str, Any]] = []
    variations: list[Fraction] = []
    for radius in RADIUS_CANDIDATES:
        coordinate_box = [RationalInterval(value - radius, value + radius) for value in coordinate]
        state_box = _lift_interval(coordinate_box)
        minimum_population = min(value.lower for value in state_box)
        sparse, pivot, densities = _reduced_derivative_factors(state_box)
        combined = _combine_reduced_factors(sparse, pivot, lift_matrix)
        point_containment = True
        row_variations: list[Fraction] = []
        for interval_row, point_row in zip(combined, point_jacobian, strict=True):
            row_sum = Fraction(0)
            for interval_value, point_value in zip(interval_row, point_row, strict=True):
                if not (interval_value.lower <= point_value <= interval_value.upper):
                    point_containment = False
                row_sum += max(
                    abs(interval_value.lower - point_value),
                    abs(interval_value.upper - point_value),
                )
            row_variations.append(row_sum)
        variation = max(row_variations)
        variations.append(variation)
        minimum_density = min(value.lower for value in densities)
        checks = {
            "population_box_is_strictly_positive": minimum_population > 0,
            "density_box_is_strictly_positive": minimum_density > 0,
            "point_jacobian_is_entrywise_contained": point_containment,
            "variation_is_nonnegative": variation >= 0,
        }
        records.append(
            {
                "radius": _fraction_record(radius),
                "minimum_population_lower": _fraction_record(minimum_population),
                "minimum_density_lower": _fraction_record(minimum_density),
                "maximum_ambient_coordinate_radius": _fraction_record(
                    EXPECTED_LIFT_INFINITY_NORM * radius
                ),
                "jacobian_variation_infinity_norm_upper": _fraction_record(variation),
                "checks": checks,
                "passed": all(checks.values()),
            }
        )
    return records, variations


def _sparse_columns(matrix: ExactMatrix) -> list[list[tuple[int, Fraction]]]:
    columns: list[list[tuple[int, Fraction]]] = []
    for column in range(len(matrix[0])):
        columns.append(
            [(row, matrix[row][column]) for row in range(len(matrix)) if matrix[row][column] != 0]
        )
    return columns


def _bulk_endpoint_pairs(
    values: list[Fraction],
    precision: int,
) -> tuple[list[gmpy2.mpfr], list[gmpy2.mpfr], dict[str, dict[str, bool]]]:
    down_context = _proof_context(precision, gmpy2.RoundDown)
    up_context = _proof_context(precision, gmpy2.RoundUp)
    with down_context:
        lower = [gmpy2.mpfr(_mpq(value)) for value in values]
    with up_context:
        upper = [gmpy2.mpfr(_mpq(value)) for value in values]
    return (
        lower,
        upper,
        {
            "endpoint_round_down": _context_flags(down_context),
            "endpoint_round_up": _context_flags(up_context),
        },
    )


def _directed_dot_products(
    preconditioner: Array,
    sparse_point: ExactMatrix,
    pivot_point: ExactMatrix,
    reduced_residual: ExactVector,
    lift_matrix: npt.NDArray[np.int64],
    precision: int,
) -> dict[str, Any]:
    caller_signature = _context_signature(gmpy2.get_context())
    c_exact = [[_fraction_from_float(value) for value in row] for row in preconditioner]
    c_flat = [value for row in c_exact for value in row]
    c_lower, c_upper, c_flags = _bulk_endpoint_pairs(c_flat, precision)
    if any(left != right for left, right in zip(c_lower, c_upper, strict=True)):
        raise RuntimeError("binary64 preconditioner did not convert exactly")
    c_mpfr = [
        c_lower[row * COORDINATE_DIMENSION : (row + 1) * COORDINATE_DIMENSION]
        for row in range(COORDINATE_DIMENSION)
    ]

    sparse_columns = _sparse_columns(sparse_point)
    sparse_values = [value for column in sparse_columns for _, value in column]
    sparse_lower, sparse_upper, sparse_flags = _bulk_endpoint_pairs(sparse_values, precision)
    sparse_endpoint_columns: list[list[tuple[int, gmpy2.mpfr, gmpy2.mpfr]]] = []
    offset = 0
    for column in sparse_columns:
        endpoint_column = []
        for row, _ in column:
            endpoint_column.append((row, sparse_lower[offset], sparse_upper[offset]))
            offset += 1
        sparse_endpoint_columns.append(endpoint_column)

    pivot_values = [value for row in pivot_point for value in row]
    pivot_lower, pivot_upper, pivot_flags = _bulk_endpoint_pairs(pivot_values, precision)
    pivot_endpoints = [
        [
            (
                pivot_lower[row * 3 + column],
                pivot_upper[row * 3 + column],
            )
            for column in range(3)
        ]
        for row in range(COORDINATE_DIMENSION)
    ]
    residual_lower, residual_upper, residual_flags = _bulk_endpoint_pairs(
        reduced_residual, precision
    )

    lower_context = _proof_context(precision, gmpy2.RoundDown)
    upper_context = _proof_context(precision, gmpy2.RoundUp)
    with lower_context:
        cs_lower: list[list[gmpy2.mpfr]] = []
        for output_row in range(COORDINATE_DIMENSION):
            output = []
            coefficients = c_mpfr[output_row]
            for column in sparse_endpoint_columns:
                total = gmpy2.mpfr(0)
                for input_row, value_lower, value_upper in column:
                    coefficient = coefficients[input_row]
                    endpoint = value_lower if coefficient >= 0 else value_upper
                    total = total + coefficient * endpoint
                output.append(total)
            cs_lower.append(output)
        ca_lower: list[list[gmpy2.mpfr]] = []
        z_lower: list[gmpy2.mpfr] = []
        for output_row in range(COORDINATE_DIMENSION):
            coefficients = c_mpfr[output_row]
            ca_row = []
            for pivot_column in range(3):
                total = gmpy2.mpfr(0)
                for input_row, coefficient in enumerate(coefficients):
                    low, high = pivot_endpoints[input_row][pivot_column]
                    endpoint = low if coefficient >= 0 else high
                    total = total + coefficient * endpoint
                ca_row.append(total)
            ca_lower.append(ca_row)
            total = gmpy2.mpfr(0)
            for input_row, coefficient in enumerate(coefficients):
                endpoint = (
                    residual_lower[input_row] if coefficient >= 0 else residual_upper[input_row]
                )
                total = total + coefficient * endpoint
            z_lower.append(total)
    with upper_context:
        cs_upper: list[list[gmpy2.mpfr]] = []
        for output_row in range(COORDINATE_DIMENSION):
            output = []
            coefficients = c_mpfr[output_row]
            for column in sparse_endpoint_columns:
                total = gmpy2.mpfr(0)
                for input_row, value_lower, value_upper in column:
                    coefficient = coefficients[input_row]
                    endpoint = value_upper if coefficient >= 0 else value_lower
                    total = total + coefficient * endpoint
                output.append(total)
            cs_upper.append(output)
        ca_upper: list[list[gmpy2.mpfr]] = []
        z_upper: list[gmpy2.mpfr] = []
        for output_row in range(COORDINATE_DIMENSION):
            coefficients = c_mpfr[output_row]
            ca_row = []
            for pivot_column in range(3):
                total = gmpy2.mpfr(0)
                for input_row, coefficient in enumerate(coefficients):
                    low, high = pivot_endpoints[input_row][pivot_column]
                    endpoint = high if coefficient >= 0 else low
                    total = total + coefficient * endpoint
                ca_row.append(total)
            ca_upper.append(ca_row)
            total = gmpy2.mpfr(0)
            for input_row, coefficient in enumerate(coefficients):
                endpoint = (
                    residual_upper[input_row] if coefficient >= 0 else residual_lower[input_row]
                )
                total = total + coefficient * endpoint
            z_upper.append(total)

    pivot_lift = lift_matrix[list(PIVOT_INDICES), :]
    defect_rows: list[list[RationalInterval]] = []
    for row in range(COORDINATE_DIMENSION):
        defect_row = []
        for column in range(COORDINATE_DIMENSION):
            product_lower = fraction_from_mpfr(cs_lower[row][column])
            product_upper = fraction_from_mpfr(cs_upper[row][column])
            for pivot_column in range(3):
                multiplier = int(pivot_lift[pivot_column, column])
                if multiplier >= 0:
                    product_lower += multiplier * fraction_from_mpfr(ca_lower[row][pivot_column])
                    product_upper += multiplier * fraction_from_mpfr(ca_upper[row][pivot_column])
                else:
                    product_lower += multiplier * fraction_from_mpfr(ca_upper[row][pivot_column])
                    product_upper += multiplier * fraction_from_mpfr(ca_lower[row][pivot_column])
            identity = Fraction(int(row == column))
            defect_row.append(RationalInterval(identity - product_upper, identity - product_lower))
        defect_rows.append(defect_row)
    point_inverse_defect = max(
        sum((_maximum_absolute(value) for value in row), Fraction(0)) for row in defect_rows
    )
    correction_intervals = [
        RationalInterval(
            fraction_from_mpfr(lower),
            fraction_from_mpfr(upper),
        )
        for lower, upper in zip(z_lower, z_upper, strict=True)
    ]
    correction_upper = max(_maximum_absolute(value) for value in correction_intervals)
    preconditioner_norm = max(sum((abs(value) for value in row), Fraction(0)) for row in c_exact)
    forbidden_flags = ("underflow", "overflow", "invalid", "division_by_zero", "erange")
    flag_groups = {
        **{f"preconditioner_{key}": value for key, value in c_flags.items()},
        **{f"sparse_{key}": value for key, value in sparse_flags.items()},
        **{f"pivot_{key}": value for key, value in pivot_flags.items()},
        **{f"residual_{key}": value for key, value in residual_flags.items()},
        "dot_round_down": _context_flags(lower_context),
        "dot_round_up": _context_flags(upper_context),
    }
    no_forbidden_flags = all(
        not flags[name] for flags in flag_groups.values() for name in forbidden_flags
    )
    caller_unchanged = _context_signature(gmpy2.get_context()) == caller_signature
    checks = {
        "preconditioner_converts_exactly": all(
            left == right for left, right in zip(c_lower, c_upper, strict=True)
        ),
        "all_dot_intervals_are_ordered": (
            all(value.lower <= value.upper for row in defect_rows for value in row)
            and all(value.lower <= value.upper for value in correction_intervals)
        ),
        "no_forbidden_mpfr_flags": no_forbidden_flags,
        "caller_context_is_unchanged": caller_unchanged,
    }
    return {
        "precision_bits": precision,
        "preconditioner_infinity_norm": _fraction_record(preconditioner_norm),
        "point_inverse_defect_infinity_norm_upper": _fraction_record(point_inverse_defect),
        "center_correction_infinity_norm_upper": _fraction_record(correction_upper),
        "point_inverse_defect_interval_sha256": q011i.q011b._canonical_json_sha256(
            [
                [
                    [
                        hex(value.lower.numerator),
                        hex(value.lower.denominator),
                        hex(value.upper.numerator),
                        hex(value.upper.denominator),
                    ]
                    for value in row
                ]
                for row in defect_rows
            ]
        ),
        "center_correction_interval_sha256": q011i.q011b._canonical_json_sha256(
            [
                [
                    hex(value.lower.numerator),
                    hex(value.lower.denominator),
                    hex(value.upper.numerator),
                    hex(value.upper.denominator),
                ]
                for value in correction_intervals
            ]
        ),
        "mpfr_context": {
            "gmpy2_version": gmpy2.version(),
            "mpfr_version": gmpy2.mpfr_version(),
            "precision_bits": precision,
            "rounding_modes": ["RoundDown", "RoundUp"],
            "emin": -10_000,
            "emax": 10_000,
        },
        "mpfr_flag_groups": flag_groups,
        "checks": checks,
        "passed": all(checks.values()),
        "_exact": {
            "preconditioner_norm": preconditioner_norm,
            "point_inverse_defect": point_inverse_defect,
            "correction_upper": correction_upper,
        },
    }


def _proof_precision_audit(
    directed: dict[str, Any],
    variations: list[Fraction],
) -> dict[str, Any]:
    exact = directed.pop("_exact")
    records: list[dict[str, Any]] = []
    passing_radii: list[Fraction] = []
    for radius, variation in zip(RADIUS_CANDIDATES, variations, strict=True):
        contraction = exact["point_inverse_defect"] + exact["preconditioner_norm"] * variation
        utilization = exact["correction_upper"] / radius + contraction
        passed = bool(
            exact["point_inverse_defect"] <= MAXIMUM_POINT_INVERSE_DEFECT
            and contraction <= KRAWCZYK_CAP
            and utilization <= KRAWCZYK_CAP
        )
        if passed:
            passing_radii.append(radius)
        records.append(
            {
                "radius": _fraction_record(radius),
                "jacobian_variation_infinity_norm_upper": _fraction_record(variation),
                "contraction_upper": _fraction_record(contraction),
                "krawczyk_utilization_upper": _fraction_record(utilization),
                "krawczyk_image_radius_upper": _fraction_record(
                    exact["correction_upper"] + contraction * radius
                ),
                "passed": passed,
            }
        )
    selected = max(passing_radii) if passing_radii else None
    protocol_checks = {
        "directed_protocol_passes": directed["passed"],
        "registered_radius_count_is_complete": len(records) == len(RADIUS_CANDIDATES) == 10,
    }
    hypothesis_checks = {
        "point_inverse_defect_within_registered_bound": exact["point_inverse_defect"]
        <= MAXIMUM_POINT_INVERSE_DEFECT,
        "at_least_one_radius_passes": bool(passing_radii),
        "selected_radius_is_maximum_pass": selected is None or selected == max(passing_radii),
    }
    return {
        **directed,
        "radius_records": records,
        "passing_radius_count": len(passing_radii),
        "selected_radius": None if selected is None else _fraction_record(selected),
        "protocol_checks": protocol_checks,
        "hypothesis_checks": hypothesis_checks,
        "protocol_passed": all(protocol_checks.values()),
        "hypothesis_passed": all(hypothesis_checks.values()),
        "passed": all(protocol_checks.values()) and all(hypothesis_checks.values()),
        "_exact": {
            **exact,
            "selected_radius": selected,
            "records": [
                {
                    "radius": radius,
                    "variation": variation,
                    "contraction": exact["point_inverse_defect"]
                    + exact["preconditioner_norm"] * variation,
                    "utilization": exact["correction_upper"] / radius
                    + exact["point_inverse_defect"]
                    + exact["preconditioner_norm"] * variation,
                }
                for radius, variation in zip(RADIUS_CANDIDATES, variations, strict=True)
            ],
        },
    }


def _interval_proof_audit(
    coordinate: ExactVector,
    point_jacobian: ExactMatrix,
    sparse_point: ExactMatrix,
    pivot_point: ExactMatrix,
    reduced_residual: ExactVector,
    lift_matrix: npt.NDArray[np.int64],
) -> dict[str, Any]:
    radius_records, variations = _radius_interval_audit(coordinate, point_jacobian, lift_matrix)
    point_jacobian_float = np.asarray(point_jacobian, dtype=np.float64)
    preconditioner = linalg.inv(point_jacobian_float, check_finite=True)
    preconditioner_condition = float(np.linalg.cond(point_jacobian_float))
    preconditioner_sha256 = q011i.q011b._array_sha256(preconditioner)
    primary = _proof_precision_audit(
        _directed_dot_products(
            preconditioner,
            sparse_point,
            pivot_point,
            reduced_residual,
            lift_matrix,
            PRIMARY_PRECISION_BITS,
        ),
        variations,
    )
    replay = _proof_precision_audit(
        _directed_dot_products(
            preconditioner,
            sparse_point,
            pivot_point,
            reduced_residual,
            lift_matrix,
            REPLAY_PRECISION_BITS,
        ),
        variations,
    )
    primary_exact = primary.pop("_exact")
    replay_exact = replay.pop("_exact")
    upper_containment = bool(
        replay_exact["point_inverse_defect"] <= primary_exact["point_inverse_defect"]
        and replay_exact["correction_upper"] <= primary_exact["correction_upper"]
        and all(
            right["contraction"] <= left["contraction"]
            and right["utilization"] <= left["utilization"]
            for left, right in zip(primary_exact["records"], replay_exact["records"], strict=True)
        )
    )
    selected_matches = primary_exact["selected_radius"] == replay_exact["selected_radius"]
    selected_radius = primary_exact["selected_radius"] if selected_matches else None
    selected_index = (
        RADIUS_CANDIDATES.index(selected_radius) if selected_radius is not None else None
    )
    selected_primary = (
        primary_exact["records"][selected_index] if selected_index is not None else None
    )
    selected_replay = (
        replay_exact["records"][selected_index] if selected_index is not None else None
    )
    radius_protocol_complete = all(record["passed"] for record in radius_records)
    selected_box_positive = bool(
        selected_index is not None
        and radius_records[selected_index]["checks"]["population_box_is_strictly_positive"]
        and radius_records[selected_index]["checks"]["density_box_is_strictly_positive"]
    )
    strict_inclusion = bool(
        selected_primary is not None
        and selected_replay is not None
        and selected_primary["utilization"] <= KRAWCZYK_CAP < 1
        and selected_replay["utilization"] <= KRAWCZYK_CAP < 1
    )
    strict_contraction = bool(
        selected_primary is not None
        and selected_replay is not None
        and selected_primary["contraction"] <= KRAWCZYK_CAP < 1
        and selected_replay["contraction"] <= KRAWCZYK_CAP < 1
    )
    protocol_checks = {
        "all_radius_interval_protocols_complete": radius_protocol_complete,
        "both_directed_precision_protocols_pass": primary["protocol_passed"]
        and replay["protocol_passed"],
        "higher_precision_uppers_are_contained": upper_containment,
        "selected_radius_matches_between_precisions": selected_matches,
    }
    proof_checks = {
        "both_precision_hypothesis_protocols_pass": primary["hypothesis_passed"]
        and replay["hypothesis_passed"],
        "selected_box_is_strictly_positive": selected_box_positive,
        "selected_krawczyk_image_is_strictly_interior": strict_inclusion,
        "selected_interval_derivative_is_a_strict_contraction": strict_contraction,
    }
    return {
        "radius_candidates": [_fraction_record(value) for value in RADIUS_CANDIDATES],
        "radius_interval_records": radius_records,
        "preconditioner_shape": list(preconditioner.shape),
        "preconditioner_sha256": preconditioner_sha256,
        "point_jacobian_condition_number": preconditioner_condition,
        "primary_precision_audit": primary,
        "replay_precision_audit": replay,
        "higher_precision_uppers_are_contained": upper_containment,
        "selected_radius_matches_between_precisions": selected_matches,
        "selected_radius": None if selected_radius is None else _fraction_record(selected_radius),
        "selected_primary_contraction_upper": (
            None if selected_primary is None else _fraction_record(selected_primary["contraction"])
        ),
        "selected_primary_utilization_upper": (
            None if selected_primary is None else _fraction_record(selected_primary["utilization"])
        ),
        "selected_replay_contraction_upper": (
            None if selected_replay is None else _fraction_record(selected_replay["contraction"])
        ),
        "selected_replay_utilization_upper": (
            None if selected_replay is None else _fraction_record(selected_replay["utilization"])
        ),
        "preconditioner_is_nonsingular_by_neumann": bool(
            primary_exact["point_inverse_defect"] < 1 and replay_exact["point_inverse_defect"] < 1
        ),
        "point_jacobian_is_nonsingular_by_neumann": bool(
            primary_exact["point_inverse_defect"] < 1 and replay_exact["point_inverse_defect"] < 1
        ),
        "strict_krawczyk_inclusion": strict_inclusion,
        "strict_interval_contraction": strict_contraction,
        "protocol_checks": protocol_checks,
        "proof_checks": proof_checks,
        "protocol_passed": all(protocol_checks.values()),
        "proof_passed": all(proof_checks.values()),
        "passed": all(protocol_checks.values()) and all(proof_checks.values()),
    }


def _registered_parameters() -> dict[str, Any]:
    return {
        "size": SIZE,
        "stripe_dimension": STRIPE_DIMENSION,
        "coordinate_dimension": COORDINATE_DIMENSION,
        "omega": _fraction_record(OMEGA),
        "eta": _fraction_record(ETA),
        "target_stripe_moments": [_fraction_record(value) for value in TARGET_MOMENTS],
        "pivot_indices": list(PIVOT_INDICES),
        "free_index_order": "ascending site-major D2Q9 order excluding pivots",
        "radius_candidates": [_fraction_record(value) for value in RADIUS_CANDIDATES],
        "primary_precision_bits": PRIMARY_PRECISION_BITS,
        "replay_precision_bits": REPLAY_PRECISION_BITS,
        "krawczyk_cap": _fraction_record(KRAWCZYK_CAP),
        "maximum_point_inverse_defect": _fraction_record(MAXIMUM_POINT_INVERSE_DEFECT),
        "maximum_center_pivot_correction": _fraction_record(MAXIMUM_CENTER_PIVOT_CORRECTION),
        "maximum_map_relative_discrepancy": MAXIMUM_MAP_RELATIVE_DISCREPANCY,
        "maximum_jacobian_relative_discrepancy": MAXIMUM_JACOBIAN_RELATIVE_DISCREPANCY,
    }


def _result_digest_sections(cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "study_validity": cycle["study_validity"],
        "hypothesis_outcome": cycle["hypothesis_outcome"],
        "scientific_classification": cycle["scientific_classification"],
        "validity_gates": cycle["validity_gates"],
        "hypothesis_gates": cycle["hypothesis_gates"],
        "input_digest_sha256": cycle["input_digest_sha256"],
        "coordinate_digest_sha256": cycle["coordinate_digest_sha256"],
        "oracle_digest_sha256": cycle["oracle_digest_sha256"],
        "proof_digest_sha256": cycle["proof_digest_sha256"],
    }


def run_interval_fixed_point_audit() -> dict[str, Any]:
    sealed_audit, q011i_artifact = _sealed_q011i_artifact_audit()
    coordinate, lifted, _, lift_matrix, coordinate_audit = _coordinate_audit(q011i_artifact)
    source_exact, source_float, source_audit = _repaired_source_exact()
    reduced_residual, point_jacobian, sparse_point, pivot_point, oracle_audit = _oracle_audit(
        coordinate,
        lifted,
        lift_matrix,
        source_exact,
        source_float,
    )
    proof_audit = _interval_proof_audit(
        coordinate,
        point_jacobian,
        sparse_point,
        pivot_point,
        reduced_residual,
        lift_matrix,
    )
    registered = _registered_parameters()
    runner = _runner_source_metadata()
    input_sections = {
        "registered_parameters": registered,
        "sealed_q011i_artifact_audit": sealed_audit,
        "repaired_source_audit": source_audit,
    }
    coordinate_sections = {"exact_affine_coordinate_audit": coordinate_audit}
    oracle_sections = {"exact_map_and_jacobian_oracle_audit": oracle_audit}
    proof_sections = {"interval_krawczyk_proof_audit": proof_audit}
    input_digest = q011i.q011b._canonical_json_sha256(input_sections)
    coordinate_digest = q011i.q011b._canonical_json_sha256(coordinate_sections)
    oracle_digest = q011i.q011b._canonical_json_sha256(oracle_sections)
    proof_digest = q011i.q011b._canonical_json_sha256(proof_sections)
    strict_payload = {
        **input_sections,
        **coordinate_sections,
        **oracle_sections,
        **proof_sections,
        "runner_source": runner,
    }
    digests_reproduce = bool(
        input_digest == q011i.q011b._canonical_json_sha256(input_sections)
        and coordinate_digest == q011i.q011b._canonical_json_sha256(coordinate_sections)
        and oracle_digest == q011i.q011b._canonical_json_sha256(oracle_sections)
        and proof_digest == q011i.q011b._canonical_json_sha256(proof_sections)
    )
    strict_json = bool(
        _all_numeric_values_finite(strict_payload)
        and _strict_json_serializable(strict_payload)
        and json.dumps(strict_payload, allow_nan=False)
    )
    validity_gates = {
        "q011i_and_prior_claim_boundaries_are_sealed": {
            "passed": sealed_audit["passed"],
            "threshold": "Q011i artifact, runner, package source, five digests, three hashes and outcome reproduce",
            "value": sealed_audit["checks"],
        },
        "exact_affine_fixed_leaf_coordinate_is_complete": {
            "passed": coordinate_audit["passed"] and source_audit["passed"],
            "threshold": "registered pivots, determinant, 153x150 rank, norm, exact moments, center and repaired source reproduce",
            "value": {
                "coordinate_checks": coordinate_audit["checks"],
                "source_checks": source_audit["checks"],
            },
        },
        "exact_map_and_jacobian_oracle_is_valid": {
            "passed": oracle_audit["passed"],
            "threshold": "exact structural identities and independent map/Jacobian comparisons pass registered thresholds",
            "value": oracle_audit["checks"],
        },
        "all_registered_interval_boxes_are_complete": {
            "passed": all(record["passed"] for record in proof_audit["radius_interval_records"]),
            "threshold": "all ten boxes have positive density and population and contain the point Jacobian",
            "value": [record["checks"] for record in proof_audit["radius_interval_records"]],
        },
        "dual_precision_outward_protocol_is_complete": {
            "passed": proof_audit["protocol_passed"],
            "threshold": "256/384-bit directed MPFR protocols, upper containment and deterministic radius selection complete",
            "value": proof_audit["protocol_checks"],
        },
        "strict_serialization_digests_and_runner_reproduce": {
            "passed": bool(strict_json and digests_reproduce),
            "threshold": "finite strict JSON, four section digests and runner provenance reproduce",
            "value": {
                "strict_json": strict_json,
                "digests_reproduce": digests_reproduce,
                "runner_sha256": runner["sha256"],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())
    selected_exists = proof_audit["selected_radius"] is not None
    hypothesis_gates = {
        "repaired_exact_map_preserves_the_fixed_leaf_and_replication": {
            "passed": bool(
                validity_passed
                and oracle_audit["checks"]["source_global_moments_are_exact_zero"]
                and oracle_audit["checks"]["center_map_preserves_exact_moments"]
                and oracle_audit["checks"]["reduced_zero_implies_full_zero_structurally"]
                and oracle_audit["checks"]["x_independent_filter_reduction_is_exact"]
            ),
            "threshold": "exact repaired source and map preserve the global fixed leaf and stripe replication, with reduced zero implying full zero",
            "value": oracle_audit["checks"],
        },
        "registered_boxes_are_in_the_analytic_domain_and_point_inverse_is_regular": {
            "passed": bool(
                validity_passed
                and selected_exists
                and proof_audit["primary_precision_audit"]["hypothesis_checks"][
                    "point_inverse_defect_within_registered_bound"
                ]
                and proof_audit["replay_precision_audit"]["hypothesis_checks"][
                    "point_inverse_defect_within_registered_bound"
                ]
                and proof_audit["proof_checks"]["selected_box_is_strictly_positive"]
            ),
            "threshold": "selected box has positive population/density and both point inverse defects are <=1e-8",
            "value": {
                "selected_radius": proof_audit["selected_radius"],
                "primary_point_inverse_defect": proof_audit["primary_precision_audit"][
                    "point_inverse_defect_infinity_norm_upper"
                ],
                "replay_point_inverse_defect": proof_audit["replay_precision_audit"][
                    "point_inverse_defect_infinity_norm_upper"
                ],
            },
        },
        "a_common_maximum_registered_radius_passes_both_precisions": {
            "passed": bool(
                validity_passed
                and selected_exists
                and proof_audit["selected_radius_matches_between_precisions"]
                and proof_audit["higher_precision_uppers_are_contained"]
            ),
            "threshold": "at least one radius passes q,u<=0.9 in both precisions and the maximum common radius agrees",
            "value": {
                "selected_radius": proof_audit["selected_radius"],
                "primary_passing_count": proof_audit["primary_precision_audit"][
                    "passing_radius_count"
                ],
                "replay_passing_count": proof_audit["replay_precision_audit"][
                    "passing_radius_count"
                ],
            },
        },
        "selected_krawczyk_image_certifies_existence_and_local_uniqueness": {
            "passed": bool(
                validity_passed
                and selected_exists
                and proof_audit["strict_krawczyk_inclusion"]
                and proof_audit["strict_interval_contraction"]
                and proof_audit["preconditioner_is_nonsingular_by_neumann"]
                and proof_audit["point_jacobian_is_nonsingular_by_neumann"]
            ),
            "threshold": "selected Krawczyk image is strictly interior and interval derivative contracts with nonsingular preconditioner",
            "value": {
                "selected_radius": proof_audit["selected_radius"],
                "primary_contraction_upper": proof_audit["selected_primary_contraction_upper"],
                "primary_utilization_upper": proof_audit["selected_primary_utilization_upper"],
                "replay_contraction_upper": proof_audit["selected_replay_contraction_upper"],
                "replay_utilization_upper": proof_audit["selected_replay_utilization_upper"],
            },
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered Q011j interval fixed-point proof is invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "the repaired periodic forcing admits a locally unique exact fixed-leaf "
            "fixed point in the registered rational box"
        )
    else:
        outcome = "rejected"
        classification = (
            "the registered interval boxes do not certify a locally unique repaired fixed point"
        )
    cycle: dict[str, Any] = {
        "question": (
            "Does the exact-rational repaired periodic stripe map admit a fixed point "
            "that is locally unique in one of the preregistered affine fixed-leaf boxes?"
        ),
        **strict_payload,
        "input_digest_sha256": input_digest,
        "coordinate_digest_sha256": coordinate_digest,
        "oracle_digest_sha256": oracle_digest,
        "proof_digest_sha256": proof_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
    }
    result_digest = q011i.q011b._canonical_json_sha256(_result_digest_sections(cycle))
    cycle["result_digest_sha256"] = result_digest
    cycle["theorem_consequence"] = {
        "repaired_exact_stripe_fixed_point_exists": bool(validity_passed and hypotheses_passed),
        "repaired_exact_full_17x17_x_independent_fixed_point_exists": bool(
            validity_passed and hypotheses_passed
        ),
        "fixed_point_is_unique_within_the_selected_affine_box": bool(
            validity_passed and hypotheses_passed
        ),
        "raw_q011b_exact_map_fixed_point_is_certified": False,
        "q011b_numerical_outcome_is_changed": False,
        "q011e_through_q011h_coefficients_transfer_to_repaired_map": False,
        "rigorous_fixed_leaf_spectrum_is_certified": False,
        "forced_ssm_exists_or_is_unique": False,
        "normal_attraction_is_certified": False,
    }
    cycle["claim_boundary"] = (
        "This computer-assisted proof concerns the fixed 17x17 periodic repaired "
        "exact-rational map, its x-independent fixed-conservation leaf, and local "
        "uniqueness inside the selected affine box. It does not certify the raw "
        "Q011b exact map, transfer Q011e--Q011h coefficients, enclose the spectrum, "
        "prove a forced SSM or normal attraction, establish a basin or global "
        "uniqueness, or cover another grid, force, wall boundary, or D3Q27."
    )
    cycle["preserved_prior_outcomes"] = {
        "q011i_acceptance_changed": False,
        "q011b_numerical_acceptance_changed": False,
        "q011h_sparse_equivalence_acceptance_changed": False,
        "q011g_tt_rejection_changed": False,
    }
    cycle["next_change"] = (
        "Preregister a rigorous interval fixed-leaf spectrum and selected/external "
        "split over the certified repaired fixed-point box."
        if outcome == "accepted"
        else (
            "Localize the first valid inverse-defect, analytic-domain, Jacobian-variation "
            "or Krawczyk-inclusion failure without changing the registered protocol."
            if outcome == "rejected"
            else (
                "Localize the first failed sealing, coordinate, oracle, interval, "
                "directed-rounding or serialization validity gate."
            )
        )
    )
    if not (
        _all_numeric_values_finite(cycle)
        and _strict_json_serializable(cycle)
        and result_digest == q011i.q011b._canonical_json_sha256(_result_digest_sections(cycle))
    ):
        raise RuntimeError("Q011j cycle failed strict serialization or digest")
    return cycle


def run_q011j_study() -> dict[str, Any]:
    cycle = run_interval_fixed_point_audit()
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "interval_runtime": {
            "gmpy2_version": gmpy2.version(),
            "mpfr_version": gmpy2.mpfr_version(),
            "gmp_version": gmpy2.mp_version(),
            "primary_precision_bits": PRIMARY_PRECISION_BITS,
            "replay_precision_bits": REPLAY_PRECISION_BITS,
        },
        "mathematical_scope": {
            "diagnostic": "outward interval Krawczyk existence and local-uniqueness proof",
            "grid": [SIZE, SIZE],
            "x_independent_stripe": True,
            "fixed_conservation_leaf": True,
            "exact_rational_repaired_map": True,
            "claim": "fixed-point existence and local uniqueness in the registered affine box only",
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
    result = run_q011j_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
