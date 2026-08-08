"""Sealed Q007j rational Krawczyk eigencoordinate bridge.

NumPy proposes eigenpair centers and inverse Jacobians.  All inclusion,
separation, normalization, and correction gates use exact ``Fraction``
endpoints through rational complex rectangles.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from ttim_lbm.checkerboard_filter import filtered_fourier_symbol
from ttim_lbm.equivariant_spectrum import (
    QUARTER_TURN_MAPPING,
    _certify_transported_block,
    rotate_wave,
)
from ttim_lbm.full2d_chart import (
    CONJUGATE_LABEL,
    MODE_ORDER,
    WAVE_ORDER,
    _build_complex_modes,
    build_full2d_quadratic_model,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    MAXIMUM_PI_TRIGONOMETRIC_WIDTH,
    MAXIMUM_SYMBOL_ENTRY_WIDTH,
    ComplexIntervalMatrix,
    ComplexRationalInterval,
    RationalInterval,
    WaveIndex,
    _all_numeric_values_finite,
    _complex_point,
    _complex_rectangle_absolute_upper,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _identity_matrix,
    _matrix_from_numpy,
    _matrix_infinity_norm_upper,
    _matrix_multiply,
    _matrix_subtract,
    _proof_digest,
    _sqrt_bounds,
    _strict_json_serializable,
    machin_pi_interval,
    rational_collision_symbol,
    rational_fourier_symbol,
    trigonometric_intervals,
)

Q006I_ARTIFACT = "q006i_full2d_quadratic.json"
Q007H1_ARTIFACT = "q007h1_equivariant_spectrum.json"
Q007I_ARTIFACT = "q007i_direct_nonresonance.json"

REGISTERED_INPUT_SHA256 = {
    "q006i": "347d5349af349618333df17733ba372c8ca6f5ee02784a9e788898acefb5db89",
    "q007h1": "caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4",
    "q007i": "c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f",
}
REGISTERED_COEFFICIENT_HASHES = {
    "dense_hessian_sha256": (
        "3f26eadcc6d25514671d9b741c53df5cf87c0dc598d0ff1cf9b9fd19f47d412f"
    ),
    "reduced_hessian_sha256": (
        "61f5f3a9663a29022e1b41f56df0a6408d93d770a2821d012ba1974954645da5"
    ),
}

SIZE = 17
OMEGA = 1.5
ETA = 0.01
REPRESENTATIVE_WAVES: tuple[WaveIndex, ...] = ((1, 0), (1, 1))
NEGATIVE_PROOF_WAVES: tuple[WaveIndex, ...] = ((-1, 0), (-1, -1))
BRANCH_ORDER = MODE_ORDER
RIGHT_PIVOTS = (2, 0, 0, 1, 0, 0)
LEFT_PIVOTS = (5, 7, 8, 8, 7, 5)
SEARCH_RADIUS = Fraction(1, 10**10)
MAXIMUM_KRAWCZYK_UTILIZATION = Fraction(1, 10**3)
MINIMUM_OVERLAP_MODULUS = Fraction(1, 2)
MAXIMUM_MODE_CORRECTION = Fraction(1, 10**9)
EXPECTED_SYSTEM_COUNT = 12
EXPECTED_BRANCH_COUNT = 6
EXPECTED_TRANSPORTED_MODE_COUNT = 24


@dataclass(frozen=True, slots=True)
class _KrawczykProof:
    wave_index: WaveIndex
    branch: str
    role: str
    pivot: int
    eigenvalue_center: complex
    normalized_center: np.ndarray
    root_vector: tuple[ComplexRationalInterval, ...]
    root_eigenvalue: ComplexRationalInterval
    utilization: Fraction
    point_inverse_defect: Fraction
    contraction_bound: Fraction
    residual_bound: Fraction
    proof_digest: str

    @property
    def included(self) -> bool:
        return self.utilization < 1 and self.contraction_bound < 1


@dataclass(frozen=True, slots=True)
class _DiscProof:
    wave_index: WaveIndex
    eigenvalues: np.ndarray
    selected_indices: tuple[int, ...]
    radius: Fraction
    digest_matches: bool
    proof_digest: str
    artifact_digest: str


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _matrix_add(
    left: ComplexIntervalMatrix,
    right: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    if len(left) != len(right) or any(
        len(left_row) != len(right_row)
        for left_row, right_row in zip(left, right, strict=True)
    ):
        raise ValueError("matrix shapes differ")
    return [
        [
            left_value + right_value
            for left_value, right_value in zip(left_row, right_row, strict=True)
        ]
        for left_row, right_row in zip(left, right, strict=True)
    ]


def _complex_conjugate(
    value: ComplexRationalInterval,
) -> ComplexRationalInterval:
    return ComplexRationalInterval(value.real, -value.imag)


def _complex_adjoint(matrix: ComplexIntervalMatrix) -> ComplexIntervalMatrix:
    return [
        [_complex_conjugate(matrix[column][row]) for column in range(len(matrix))]
        for row in range(len(matrix[0]))
    ]


def _real_square(value: RationalInterval) -> RationalInterval:
    upper = max(value.lower * value.lower, value.upper * value.upper)
    lower = (
        Fraction(0)
        if value.lower <= 0 <= value.upper
        else min(value.lower * value.lower, value.upper * value.upper)
    )
    return RationalInterval(lower, upper)


def _real_reciprocal(value: RationalInterval) -> RationalInterval:
    if value.lower <= 0 <= value.upper:
        raise ZeroDivisionError("interval reciprocal contains zero")
    candidates = (Fraction(1, value.lower), Fraction(1, value.upper))
    return RationalInterval(min(candidates), max(candidates))


def _complex_reciprocal(
    value: ComplexRationalInterval,
) -> ComplexRationalInterval:
    denominator = _real_square(value.real) + _real_square(value.imag)
    if denominator.lower <= 0:
        raise ZeroDivisionError("complex rectangle contains the origin")
    return _complex_conjugate(value) * ComplexRationalInterval(
        _real_reciprocal(denominator),
        RationalInterval.point(0),
    )


def _real_distance_from_zero(value: RationalInterval) -> Fraction:
    if value.lower <= 0 <= value.upper:
        return Fraction(0)
    return min(abs(value.lower), abs(value.upper))


def _complex_absolute_bounds(
    value: ComplexRationalInterval,
) -> RationalInterval:
    lower_square = (
        _real_distance_from_zero(value.real) ** 2
        + _real_distance_from_zero(value.imag) ** 2
    )
    upper_square = (
        value.real.maximum_absolute_value**2
        + value.imag.maximum_absolute_value**2
    )
    return RationalInterval(
        _sqrt_bounds(lower_square).lower,
        _sqrt_bounds(upper_square).upper,
    )


def _complex_interval_record(value: ComplexRationalInterval) -> dict[str, Any]:
    return {
        "real": {
            "lower": _fraction_record(value.real.lower),
            "upper": _fraction_record(value.real.upper),
        },
        "imag": {
            "lower": _fraction_record(value.imag.lower),
            "upper": _fraction_record(value.imag.upper),
        },
        "modulus": {
            "lower": _fraction_record(_complex_absolute_bounds(value).lower),
            "upper": _fraction_record(_complex_absolute_bounds(value).upper),
        },
    }


def _complex_box(value: complex, radius: Fraction) -> ComplexRationalInterval:
    center = _complex_point(value)
    return ComplexRationalInterval(
        RationalInterval(center.real.lower - radius, center.real.upper + radius),
        RationalInterval(center.imag.lower - radius, center.imag.upper + radius),
    )


def _column(
    values: Sequence[ComplexRationalInterval],
) -> ComplexIntervalMatrix:
    return [[value] for value in values]


def _flatten_column(
    matrix: ComplexIntervalMatrix,
) -> tuple[ComplexRationalInterval, ...]:
    if any(len(row) != 1 for row in matrix):
        raise ValueError("matrix is not a column")
    return tuple(row[0] for row in matrix)


def _full_eigenvector(
    free_values: Sequence[ComplexRationalInterval],
    pivot: int,
) -> tuple[ComplexRationalInterval, ...]:
    result = []
    free_iterator = iter(free_values)
    for index in range(9):
        result.append(
            ComplexRationalInterval.point(1)
            if index == pivot
            else next(free_iterator)
        )
    return tuple(result)


def _interval_jacobian(
    matrix: ComplexIntervalMatrix,
    vector: Sequence[ComplexRationalInterval],
    eigenvalue: ComplexRationalInterval,
    free_indices: Sequence[int],
) -> ComplexIntervalMatrix:
    result: ComplexIntervalMatrix = []
    for row in range(9):
        result_row = []
        for source in free_indices:
            value = matrix[row][source]
            if row == source:
                value = value - eigenvalue
            result_row.append(value)
        result_row.append(-vector[row])
        result.append(result_row)
    return result


def _numeric_jacobian(
    matrix: np.ndarray,
    vector: np.ndarray,
    eigenvalue: complex,
    free_indices: Sequence[int],
) -> np.ndarray:
    result = np.empty((9, 9), dtype=np.complex128)
    result[:, :8] = (matrix - eigenvalue * np.eye(9))[:, free_indices]
    result[:, 8] = -vector
    return result


def _proof_digest_for_boxes(
    boxes: Sequence[ComplexRationalInterval],
    extra: Sequence[Fraction],
) -> str:
    values = []
    for box in boxes:
        values.extend(
            (box.real.lower, box.real.upper, box.imag.lower, box.imag.upper)
        )
    values.extend(extra)
    return _proof_digest(values)


def _krawczyk_utilization(
    image: Sequence[ComplexRationalInterval],
    centers: Sequence[complex],
) -> Fraction:
    utilization = Fraction(0)
    for value, center_value in zip(image, centers, strict=True):
        center = _complex_point(center_value)
        real_deviation = max(
            abs(value.real.lower - center.real.lower),
            abs(value.real.upper - center.real.upper),
        )
        imag_deviation = max(
            abs(value.imag.lower - center.imag.lower),
            abs(value.imag.upper - center.imag.upper),
        )
        utilization = max(
            utilization,
            real_deviation / SEARCH_RADIUS,
            imag_deviation / SEARCH_RADIUS,
        )
    return utilization


def _certify_eigenpair(
    *,
    wave_index: WaveIndex,
    branch: str,
    role: str,
    interval_matrix: ComplexIntervalMatrix,
    numeric_matrix: np.ndarray,
    vector_center: np.ndarray,
    eigenvalue_center: complex,
    pivot: int,
) -> _KrawczykProof:
    normalized = np.asarray(
        vector_center / vector_center[pivot],
        dtype=np.complex128,
    )
    free_indices = tuple(index for index in range(9) if index != pivot)
    z_center = np.asarray(
        [*(normalized[index] for index in free_indices), eigenvalue_center],
        dtype=np.complex128,
    )
    z_point = tuple(_complex_point(value) for value in z_center)
    z_box = tuple(_complex_box(value, SEARCH_RADIUS) for value in z_center)
    vector_point = _full_eigenvector(z_point[:8], pivot)
    vector_box = _full_eigenvector(z_box[:8], pivot)

    matrix_vector = _flatten_column(
        _matrix_multiply(interval_matrix, _column(vector_point))
    )
    eigenvalue_point = z_point[-1]
    residual = tuple(
        matrix_value - eigenvalue_point * vector_value
        for matrix_value, vector_value in zip(
            matrix_vector,
            vector_point,
            strict=True,
        )
    )

    numeric_jacobian = _numeric_jacobian(
        numeric_matrix,
        normalized,
        eigenvalue_center,
        free_indices,
    )
    inverse_candidate = np.linalg.inv(numeric_jacobian)
    inverse_interval = _matrix_from_numpy(inverse_candidate)
    numeric_jacobian_interval = _matrix_from_numpy(numeric_jacobian)
    point_inverse_defect_matrix = _matrix_subtract(
        _identity_matrix(9),
        _matrix_multiply(inverse_interval, numeric_jacobian_interval),
    )
    point_inverse_defect = _matrix_infinity_norm_upper(
        point_inverse_defect_matrix
    )

    jacobian_box = _interval_jacobian(
        interval_matrix,
        vector_box,
        z_box[-1],
        free_indices,
    )
    contraction_matrix = _matrix_subtract(
        _identity_matrix(9),
        _matrix_multiply(inverse_interval, jacobian_box),
    )
    contraction_bound = _matrix_infinity_norm_upper(contraction_matrix)

    center_term = _matrix_subtract(
        _column(z_point),
        _matrix_multiply(inverse_interval, _column(residual)),
    )
    centered_box = tuple(
        ComplexRationalInterval(
            RationalInterval(-SEARCH_RADIUS, SEARCH_RADIUS),
            RationalInterval(-SEARCH_RADIUS, SEARCH_RADIUS),
        )
        for _ in range(9)
    )
    variation = _matrix_multiply(contraction_matrix, _column(centered_box))
    image = _flatten_column(_matrix_add(center_term, variation))
    utilization = _krawczyk_utilization(image, z_center)
    root_vector = _full_eigenvector(image[:8], pivot)
    residual_bound = _matrix_infinity_norm_upper(_column(residual))
    digest = _proof_digest_for_boxes(
        image,
        (
            utilization,
            point_inverse_defect,
            contraction_bound,
            residual_bound,
        ),
    )
    return _KrawczykProof(
        wave_index=wave_index,
        branch=branch,
        role=role,
        pivot=pivot,
        eigenvalue_center=complex(eigenvalue_center),
        normalized_center=normalized,
        root_vector=root_vector,
        root_eigenvalue=image[-1],
        utilization=utilization,
        point_inverse_defect=point_inverse_defect,
        contraction_bound=contraction_bound,
        residual_bound=residual_bound,
        proof_digest=digest,
    )


def _artifact_record(
    path: Path,
    registered_sha256: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    observed_sha256 = _file_sha256(path)
    return payload, {
        "filename": path.name,
        "sha256": observed_sha256,
        "registered_sha256": registered_sha256,
        "sha256_matches": observed_sha256 == registered_sha256,
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
        "source_match": payload.get("source") == source_metadata(),
        "study_gate": payload.get("study_gate"),
        "scientific_outcome": payload.get("scientific_outcome"),
    }


def _load_registered_inputs(
    artifact_directory: Path,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    q006i, q006i_record = _artifact_record(
        artifact_directory / Q006I_ARTIFACT,
        REGISTERED_INPUT_SHA256["q006i"],
    )
    q007h1, q007h1_record = _artifact_record(
        artifact_directory / Q007H1_ARTIFACT,
        REGISTERED_INPUT_SHA256["q007h1"],
    )
    q007i, q007i_record = _artifact_record(
        artifact_directory / Q007I_ARTIFACT,
        REGISTERED_INPUT_SHA256["q007i"],
    )

    q006i_scope = q006i.get("mathematical_scope", {})
    q006i_cycle = q006i.get("cycle", {})
    q006i_failed_hypotheses = sorted(
        name
        for name, gate in q006i_cycle.get("hypothesis_gates", {}).items()
        if not gate.get("passed", False)
    )
    q006i_record.update(
        {
            "scope_match": bool(
                q006i_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q006i_scope.get("omega", math.nan)) == OMEGA
                and float(q006i_scope.get("eta", math.nan)) == ETA
                and q006i_scope.get("selected_real_dimension") == 24
                and q006i_scope.get("conservation_treatment")
                == "fixed global mass and momentum leaf"
            ),
            "all_validity_gates_passed": bool(
                q006i_cycle.get("validity_gates")
                and all(
                    gate.get("passed", False)
                    for gate in q006i_cycle["validity_gates"].values()
                )
            ),
            "failed_hypothesis_gates": q006i_failed_hypotheses,
        }
    )
    q006i_record["passed"] = bool(
        q006i_record["sha256_matches"]
        and q006i_record["source_match"]
        and q006i.get("study_gate") == "passed"
        and q006i.get("scientific_outcome") == "rejected"
        and q006i_record["scope_match"]
        and q006i_record["all_validity_gates_passed"]
        and q006i_failed_hypotheses == ["global_conservation"]
    )

    q007h1_scope = q007h1.get("mathematical_scope", {})
    q007h1_cycle = q007h1.get("cycle", {})
    q007h1_record.update(
        {
            "scope_match": bool(
                q007h1_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q007h1_scope.get("omega", math.nan)) == OMEGA
                and float(q007h1_scope.get("eta", math.nan)) == ETA
                and q007h1_scope.get("selected_complex_dimension") == 24
                and q007h1_scope.get("fixed_leaf_complex_dimension") == 2598
            ),
            "all_validity_gates_passed": bool(
                len(q007h1_cycle.get("validity_gates", {})) == 10
                and all(
                    gate.get("passed", False)
                    for gate in q007h1_cycle["validity_gates"].values()
                )
            ),
            "all_hypothesis_gates_passed": bool(
                len(q007h1_cycle.get("hypothesis_gates", {})) == 5
                and all(
                    gate.get("passed", False)
                    for gate in q007h1_cycle["hypothesis_gates"].values()
                )
            ),
        }
    )
    q007h1_record["passed"] = bool(
        q007h1_record["sha256_matches"]
        and q007h1_record["source_match"]
        and q007h1.get("study_gate") == "passed"
        and q007h1.get("scientific_outcome") == "accepted"
        and q007h1_record["scope_match"]
        and q007h1_record["all_validity_gates_passed"]
        and q007h1_record["all_hypothesis_gates_passed"]
    )

    q007i_scope = q007i.get("mathematical_scope", {})
    q007i_cycle = q007i.get("cycle", {})
    q007i_record.update(
        {
            "scope_match": bool(
                q007i_scope.get("construction_grid") == [SIZE, SIZE]
                and float(q007i_scope.get("omega", math.nan)) == OMEGA
                and float(q007i_scope.get("eta", math.nan)) == ETA
                and q007i_scope.get("selected_real_dimension") == 24
                and q007i_scope.get("fixed_leaf_real_dimension") == 2598
            ),
            "theorem_applies": bool(
                q007i_cycle.get("theorem_consequence", {}).get(
                    "theorem_applies",
                    False,
                )
            ),
        }
    )
    q007i_record["passed"] = bool(
        q007i_record["sha256_matches"]
        and q007i_record["source_match"]
        and q007i.get("study_gate") == "passed"
        and q007i.get("scientific_outcome") == "accepted"
        and q007i_record["scope_match"]
        and q007i_record["theorem_applies"]
    )
    return q006i, q007h1, q007i, {
        "q006i": q006i_record,
        "q007h1": q007h1_record,
        "q007i": q007i_record,
    }


def _reproduce_q006i_model(q006i: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    model = build_full2d_quadratic_model()
    observed = {
        "dense_hessian_sha256": model.diagnostics.dense_hessian_sha256,
        "reduced_hessian_sha256": model.diagnostics.reduced_hessian_sha256,
    }
    artifact_diagnostics = q006i["cycle"]["construction"]["diagnostics"]
    artifact = {
        name: artifact_diagnostics[name] for name in REGISTERED_COEFFICIENT_HASHES
    }
    return model, {
        "registered": REGISTERED_COEFFICIENT_HASHES,
        "artifact": artifact,
        "observed": observed,
        "matches": bool(
            observed == REGISTERED_COEFFICIENT_HASHES
            and artifact == REGISTERED_COEFFICIENT_HASHES
        ),
    }


def _rebuild_q007h1_disc_proofs(
    q007h1: dict[str, Any],
    trig: dict[int, tuple[RationalInterval, RationalInterval]],
    collision: tuple[tuple[Fraction, ...], ...],
) -> tuple[dict[WaveIndex, _DiscProof], dict[str, Any]]:
    artifact_records = {
        tuple(record["wave_index"]): record
        for record in q007h1["cycle"]["eigencertification"]["block_records"]
    }
    result = {}
    records = []
    for wave_index in NEGATIVE_PROOF_WAVES:
        kx = 2.0 * np.pi * wave_index[0] / SIZE
        ky = 2.0 * np.pi * wave_index[1] / SIZE
        center = filtered_fourier_symbol(kx, ky, OMEGA, ETA)
        eigenvalues, eigenvectors = np.linalg.eig(center)
        inverse_candidate = np.linalg.inv(eigenvectors)
        selected_indices = tuple(
            int(index) for index in np.argsort(np.abs(eigenvalues))[::-1][:3]
        )
        proof = _certify_transported_block(
            wave_index,
            rational_fourier_symbol(wave_index, trig, collision),
            eigenvalues,
            eigenvectors,
            inverse_candidate,
            selected_indices,
        )
        artifact_digest = artifact_records[wave_index][
            "exact_proof_digest_sha256"
        ]
        disc_proof = _DiscProof(
            wave_index=wave_index,
            eigenvalues=eigenvalues,
            selected_indices=selected_indices,
            radius=proof.bauer_fike_radius,
            digest_matches=proof.proof_digest == artifact_digest,
            proof_digest=proof.proof_digest,
            artifact_digest=artifact_digest,
        )
        result[wave_index] = disc_proof
        records.append(
            {
                "wave_index": list(wave_index),
                "selected_indices": list(selected_indices),
                "bauer_fike_radius": _fraction_record(proof.bauer_fike_radius),
                "proof_digest_sha256": proof.proof_digest,
                "artifact_digest_sha256": artifact_digest,
                "digest_matches": disc_proof.digest_matches,
            }
        )
    return result, {
        "representative_count": len(result),
        "proof_digest_mismatch_count": sum(
            not proof.digest_matches for proof in result.values()
        ),
        "records": records,
    }


def _proof_record(proof: _KrawczykProof) -> dict[str, Any]:
    return {
        "wave_index": list(proof.wave_index),
        "branch": proof.branch,
        "role": proof.role,
        "pivot": proof.pivot,
        "search_radius": _fraction_record(SEARCH_RADIUS),
        "included": proof.included,
        "utilization": _fraction_record(proof.utilization),
        "point_inverse_defect": _fraction_record(proof.point_inverse_defect),
        "contraction_bound": _fraction_record(proof.contraction_bound),
        "center_residual_bound": _fraction_record(proof.residual_bound),
        "root_eigenvalue": _complex_interval_record(proof.root_eigenvalue),
        "proof_digest_sha256": proof.proof_digest,
    }


def _disc_association(
    right_proofs: Sequence[_KrawczykProof],
    disc_proofs: dict[WaveIndex, _DiscProof],
) -> dict[str, Any]:
    records = []
    assignments = []
    for proof in right_proofs:
        negative_wave = (-proof.wave_index[0], -proof.wave_index[1])
        disc_proof = disc_proofs[negative_wave]
        conjugate_root = _complex_conjugate(proof.root_eigenvalue)
        memberships = []
        distance_records = []
        for index in disc_proof.selected_indices:
            difference = conjugate_root - _complex_point(
                disc_proof.eigenvalues[index]
            )
            distance_upper = _complex_rectangle_absolute_upper(difference)
            contained = distance_upper <= disc_proof.radius
            if contained:
                memberships.append(index)
            distance_records.append(
                {
                    "eigenvalue_index": index,
                    "distance_upper": _fraction_record(distance_upper),
                    "contained": contained,
                }
            )
        assignment = (
            None
            if len(memberships) != 1
            else (negative_wave[0], negative_wave[1], memberships[0])
        )
        if assignment is not None:
            assignments.append(assignment)
        records.append(
            {
                "source_wave": list(proof.wave_index),
                "negative_proof_wave": list(negative_wave),
                "branch": proof.branch,
                "membership_count": len(memberships),
                "assigned_eigenvalue_index": (
                    None if assignment is None else assignment[2]
                ),
                "distances": distance_records,
            }
        )
    collision_count = len(assignments) - len(set(assignments))
    return {
        "root_count": len(right_proofs),
        "unique_membership_count": sum(
            record["membership_count"] == 1 for record in records
        ),
        "assignment_collision_count": collision_count,
        "all_roots_uniquely_assigned": bool(
            len(assignments) == EXPECTED_BRANCH_COUNT and collision_count == 0
        ),
        "records": records,
    }


def _permutation_power(power: int) -> tuple[int, ...]:
    mapping = tuple(range(9))
    for _ in range(power % 4):
        mapping = tuple(QUARTER_TURN_MAPPING[index] for index in mapping)
    return mapping


def _transport_vector(
    vector: Sequence[ComplexRationalInterval],
    power: int,
) -> tuple[ComplexRationalInterval, ...]:
    mapping = _permutation_power(power)
    result = [ComplexRationalInterval.zero() for _ in range(9)]
    for source, target in enumerate(mapping):
        result[target] = vector[source]
    return tuple(result)


def _scale_vector(
    vector: Sequence[ComplexRationalInterval],
    scalar: ComplexRationalInterval,
) -> tuple[ComplexRationalInterval, ...]:
    return tuple(value * scalar for value in vector)


def _normalize_to_registered_scale(
    vector: Sequence[ComplexRationalInterval],
    registered: np.ndarray,
    pivot: int,
) -> tuple[ComplexRationalInterval, ...]:
    normalized = _scale_vector(vector, _complex_reciprocal(vector[pivot]))
    return _scale_vector(normalized, _complex_point(registered[pivot]))


def _inner_product(
    left: Sequence[ComplexRationalInterval],
    right: Sequence[ComplexRationalInterval],
) -> ComplexRationalInterval:
    result = ComplexRationalInterval.zero()
    for left_value, right_value in zip(left, right, strict=True):
        result = result + _complex_conjugate(left_value) * right_value
    return result


def _biorthogonal_left(
    left: Sequence[ComplexRationalInterval],
    right: Sequence[ComplexRationalInterval],
) -> tuple[tuple[ComplexRationalInterval, ...], RationalInterval]:
    overlap = _inner_product(left, right)
    overlap_modulus = _complex_absolute_bounds(overlap)
    normalization = _complex_reciprocal(_complex_conjugate(overlap))
    return _scale_vector(left, normalization), overlap_modulus


def _maximum_vector_correction(
    enclosure: Sequence[ComplexRationalInterval],
    registered: np.ndarray,
) -> Fraction:
    return max(
        _complex_rectangle_absolute_upper(value - _complex_point(center))
        for value, center in zip(enclosure, registered, strict=True)
    )


def _intervals_intersect(
    left: ComplexRationalInterval,
    right: ComplexRationalInterval,
) -> bool:
    return bool(
        max(left.real.lower, right.real.lower)
        <= min(left.real.upper, right.real.upper)
        and max(left.imag.lower, right.imag.lower)
        <= min(left.imag.upper, right.imag.upper)
    )


def _rotation_power(source: WaveIndex, target: WaveIndex) -> int:
    current = source
    for power in range(4):
        if current == target:
            return power
        current = rotate_wave(current)
    raise ValueError(f"{target} is not in the C4 orbit of {source}")


def _transport_and_normalization_audit(
    proofs: dict[tuple[WaveIndex, str, str], _KrawczykProof],
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
) -> dict[str, Any]:
    records = []
    maximum_right_correction = Fraction(0)
    maximum_left_correction = Fraction(0)
    minimum_overlap: Fraction | None = None
    covered = []
    for target_wave in WAVE_ORDER:
        source_wave = (
            REPRESENTATIVE_WAVES[0]
            if 0 in target_wave
            else REPRESENTATIVE_WAVES[1]
        )
        power = _rotation_power(source_wave, target_wave)
        for branch in BRANCH_ORDER:
            right_proof = proofs[(source_wave, branch, "right")]
            left_proof = proofs[(source_wave, branch, "left")]
            target_mode = modes[lookup[(target_wave, branch)]]
            right_pivot = int(np.argmax(np.abs(target_mode.right)))
            left_pivot = int(np.argmax(np.abs(target_mode.left)))
            transported_right = _transport_vector(
                right_proof.root_vector,
                power,
            )
            transported_left = _transport_vector(
                left_proof.root_vector,
                power,
            )
            right_enclosure = _normalize_to_registered_scale(
                transported_right,
                target_mode.right,
                right_pivot,
            )
            left_pivot_normalized = _scale_vector(
                transported_left,
                _complex_reciprocal(transported_left[left_pivot]),
            )
            left_enclosure, overlap = _biorthogonal_left(
                left_pivot_normalized,
                right_enclosure,
            )
            right_correction = _maximum_vector_correction(
                right_enclosure,
                target_mode.right,
            )
            left_correction = _maximum_vector_correction(
                left_enclosure,
                target_mode.left,
            )
            maximum_right_correction = max(
                maximum_right_correction,
                right_correction,
            )
            maximum_left_correction = max(
                maximum_left_correction,
                left_correction,
            )
            minimum_overlap = (
                overlap.lower
                if minimum_overlap is None
                else min(minimum_overlap, overlap.lower)
            )
            identifier = f"wave={target_wave[0]},{target_wave[1]};branch={branch}"
            covered.append(identifier)
            records.append(
                {
                    "identifier": identifier,
                    "source_wave": list(source_wave),
                    "rotation_power": power,
                    "right_pivot": right_pivot,
                    "left_pivot": left_pivot,
                    "overlap_modulus_lower": _fraction_record(overlap.lower),
                    "right_correction_upper": _fraction_record(right_correction),
                    "biorthogonal_left_correction_upper": _fraction_record(
                        left_correction
                    ),
                }
            )
    if minimum_overlap is None:
        minimum_overlap = Fraction(0)

    conjugate_mismatch_count = 0
    for source_wave in REPRESENTATIVE_WAVES:
        negative_wave = (-source_wave[0], -source_wave[1])
        power = _rotation_power(source_wave, negative_wave)
        for branch in BRANCH_ORDER:
            conjugate_branch = CONJUGATE_LABEL[branch]
            target_mode = modes[lookup[(negative_wave, conjugate_branch)]]
            pivot = int(np.argmax(np.abs(target_mode.right)))
            conjugated = tuple(
                _complex_conjugate(value)
                for value in proofs[(source_wave, branch, "right")].root_vector
            )
            rotated = _transport_vector(
                proofs[(source_wave, conjugate_branch, "right")].root_vector,
                power,
            )
            conjugated_scaled = _normalize_to_registered_scale(
                conjugated,
                target_mode.right,
                pivot,
            )
            rotated_scaled = _normalize_to_registered_scale(
                rotated,
                target_mode.right,
                pivot,
            )
            if not all(
                _intervals_intersect(left, right)
                for left, right in zip(
                    conjugated_scaled,
                    rotated_scaled,
                    strict=True,
                )
            ):
                conjugate_mismatch_count += 1

    return {
        "transported_mode_count": len(records),
        "unique_mode_label_count": len(set(covered)),
        "conjugate_label_mismatch_count": conjugate_mismatch_count,
        "minimum_overlap_modulus_lower": _fraction_record(minimum_overlap),
        "maximum_right_correction_upper": _fraction_record(
            maximum_right_correction
        ),
        "maximum_biorthogonal_left_correction_upper": _fraction_record(
            maximum_left_correction
        ),
        "records": records,
        "_minimum_overlap_exact": minimum_overlap,
        "_maximum_correction_exact": max(
            maximum_right_correction,
            maximum_left_correction,
        ),
    }


def run_eigencoordinate_bridge_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    """Run the sealed Q007j selected-eigencoordinate certification."""

    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    q006i, q007h1, _q007i, input_records = _load_registered_inputs(directory)
    _, coefficient_reproduction = _reproduce_q006i_model(q006i)
    modes, lookup = _build_complex_modes(SIZE, OMEGA, ETA)

    pi_interval = machin_pi_interval()
    trig = trigonometric_intervals(pi_interval)
    collision = rational_collision_symbol()
    symbols = {
        wave: rational_fourier_symbol(wave, trig, collision)
        for wave in REPRESENTATIVE_WAVES
    }
    maximum_trigonometric_width = max(
        max(sine.width, cosine.width) for sine, cosine in trig.values()
    )
    maximum_symbol_width = max(
        max(value.real.width, value.imag.width)
        for matrix in symbols.values()
        for row in matrix
        for value in row
    )

    disc_proofs, disc_reconstruction = _rebuild_q007h1_disc_proofs(
        q007h1,
        trig,
        collision,
    )
    proofs: dict[tuple[WaveIndex, str, str], _KrawczykProof] = {}
    proof_records = []
    observed_right_pivots = []
    observed_left_pivots = []
    for wave_index in REPRESENTATIVE_WAVES:
        kx = 2.0 * np.pi * wave_index[0] / SIZE
        ky = 2.0 * np.pi * wave_index[1] / SIZE
        numeric_matrix = filtered_fourier_symbol(kx, ky, OMEGA, ETA)
        for branch in BRANCH_ORDER:
            mode = modes[lookup[(wave_index, branch)]]
            right_pivot = int(np.argmax(np.abs(mode.right)))
            left_pivot = int(np.argmax(np.abs(mode.left)))
            observed_right_pivots.append(right_pivot)
            observed_left_pivots.append(left_pivot)
            right_proof = _certify_eigenpair(
                wave_index=wave_index,
                branch=branch,
                role="right",
                interval_matrix=symbols[wave_index],
                numeric_matrix=numeric_matrix,
                vector_center=mode.right,
                eigenvalue_center=mode.eigenvalue,
                pivot=right_pivot,
            )
            left_proof = _certify_eigenpair(
                wave_index=wave_index,
                branch=branch,
                role="left",
                interval_matrix=_complex_adjoint(symbols[wave_index]),
                numeric_matrix=numeric_matrix.conj().T,
                vector_center=mode.left,
                eigenvalue_center=np.conjugate(mode.eigenvalue),
                pivot=left_pivot,
            )
            for proof in (right_proof, left_proof):
                proofs[(wave_index, branch, proof.role)] = proof
                proof_records.append(_proof_record(proof))

    right_proofs = tuple(
        proofs[(wave, branch, "right")]
        for wave in REPRESENTATIVE_WAVES
        for branch in BRANCH_ORDER
    )
    association = _disc_association(right_proofs, disc_proofs)
    transport_internal = _transport_and_normalization_audit(
        proofs,
        modes,
        lookup,
    )
    minimum_overlap = transport_internal.pop("_minimum_overlap_exact")
    maximum_correction = transport_internal.pop("_maximum_correction_exact")

    maximum_utilization = max(proof.utilization for proof in proofs.values())
    maximum_point_inverse_defect = max(
        proof.point_inverse_defect for proof in proofs.values()
    )
    maximum_contraction = max(
        proof.contraction_bound for proof in proofs.values()
    )
    all_included = all(proof.included for proof in proofs.values())
    interval_construction = {
        "pi_width": _fraction_record(pi_interval.width),
        "maximum_trigonometric_width": _fraction_record(
            maximum_trigonometric_width
        ),
        "maximum_symbol_entry_width": _fraction_record(maximum_symbol_width),
        "maximum_point_inverse_defect": _fraction_record(
            maximum_point_inverse_defect
        ),
        "maximum_interval_contraction_bound": _fraction_record(
            maximum_contraction
        ),
    }
    certification = {
        "representative_wave_count": len(REPRESENTATIVE_WAVES),
        "branch_count": len(right_proofs),
        "system_count": len(proofs),
        "registered_right_pivots": list(RIGHT_PIVOTS),
        "observed_right_pivots": observed_right_pivots,
        "registered_left_pivots": list(LEFT_PIVOTS),
        "observed_left_pivots": observed_left_pivots,
        "all_krawczyk_images_interior": all_included,
        "maximum_krawczyk_utilization": _fraction_record(maximum_utilization),
        "records": proof_records,
    }
    serializable_sections = {
        "input_artifacts": input_records,
        "coefficient_reproduction": coefficient_reproduction,
        "interval_construction": interval_construction,
        "disc_reconstruction": disc_reconstruction,
        "krawczyk_certification": certification,
        "disc_association": association,
        "transport_and_normalization": transport_internal,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )

    validity_gates = {
        "registered_inputs_and_q006i_reproduction": {
            "passed": bool(
                all(record["passed"] for record in input_records.values())
                and coefficient_reproduction["matches"]
            ),
            "threshold": "three fixed artifact SHAs/scopes/outcomes and Q006i coefficient hashes match",
            "value": {
                "inputs": {
                    name: record["passed"]
                    for name, record in input_records.items()
                },
                "coefficient_hashes_match": coefficient_reproduction["matches"],
            },
        },
        "registered_enumeration_and_pivots": {
            "passed": bool(
                len(REPRESENTATIVE_WAVES) == 2
                and len(right_proofs) == EXPECTED_BRANCH_COUNT
                and len(proofs) == EXPECTED_SYSTEM_COUNT
                and transport_internal["transported_mode_count"]
                == EXPECTED_TRANSPORTED_MODE_COUNT
                and tuple(observed_right_pivots) == RIGHT_PIVOTS
                and tuple(observed_left_pivots) == LEFT_PIVOTS
            ),
            "threshold": "2 representatives, 6 branches, 12 systems, 24 modes, registered pivots",
            "value": {
                "representatives": len(REPRESENTATIVE_WAVES),
                "branches": len(right_proofs),
                "systems": len(proofs),
                "transported_modes": transport_internal[
                    "transported_mode_count"
                ],
                "right_pivots": observed_right_pivots,
                "left_pivots": observed_left_pivots,
            },
        },
        "rational_interval_construction": {
            "passed": bool(
                pi_interval.width <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_trigonometric_width
                <= MAXIMUM_PI_TRIGONOMETRIC_WIDTH
                and maximum_symbol_width <= MAXIMUM_SYMBOL_ENTRY_WIDTH
                and maximum_point_inverse_defect < 1
            ),
            "threshold": "pi/trig <=1e-120, symbol <=1e-110, all point inverse defects <1",
            "value": interval_construction,
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all summaries finite and strict JSON serializable",
            "value": finite_strict_json,
        },
        "registered_disc_and_symmetry_correspondence": {
            "passed": bool(
                disc_reconstruction["representative_count"] == 2
                and disc_reconstruction["proof_digest_mismatch_count"] == 0
                and association["assignment_collision_count"] == 0
                and transport_internal["conjugate_label_mismatch_count"] == 0
                and transport_internal["unique_mode_label_count"]
                == EXPECTED_TRANSPORTED_MODE_COUNT
            ),
            "threshold": "zero proof-digest, disc-collision, C4/conjugate-label mismatches",
            "value": {
                "proof_digest_mismatches": disc_reconstruction[
                    "proof_digest_mismatch_count"
                ],
                "disc_assignment_collisions": association[
                    "assignment_collision_count"
                ],
                "conjugate_label_mismatches": transport_internal[
                    "conjugate_label_mismatch_count"
                ],
                "unique_mode_labels": transport_internal[
                    "unique_mode_label_count"
                ],
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    hypothesis_gates = {
        "all_twelve_krawczyk_inclusions": {
            "passed": bool(
                all_included
                and maximum_utilization <= MAXIMUM_KRAWCZYK_UTILIZATION
                and maximum_contraction < 1
            ),
            "threshold": "12 strict inclusions, maximum utilization <=1e-3, contraction <1",
            "value": {
                "included_count": sum(proof.included for proof in proofs.values()),
                "maximum_utilization": float(maximum_utilization),
                "maximum_contraction": float(maximum_contraction),
            },
        },
        "six_unique_selected_disc_assignments": {
            "passed": association["all_roots_uniquely_assigned"],
            "threshold": "six right roots map one-to-one into distinct Q007h1 selected discs",
            "value": association["unique_membership_count"],
        },
        "biorthogonal_overlap": {
            "passed": minimum_overlap >= MINIMUM_OVERLAP_MODULUS,
            "threshold": "minimum overlap modulus lower >=0.5",
            "value": float(minimum_overlap),
        },
        "all_twenty_four_mode_corrections": {
            "passed": maximum_correction <= MAXIMUM_MODE_CORRECTION,
            "threshold": "maximum right/biorthogonal-left component correction <=1e-9",
            "value": float(maximum_correction),
        },
    }
    hypotheses_passed = all(gate["passed"] for gate in hypothesis_gates.values())
    if not validity_passed:
        outcome = "inconclusive"
        scientific_classification = (
            "registered selected eigencoordinate bridge audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        scientific_classification = (
            "registered selected eigencoordinates rigorously bridge to the theorem spectral subspace"
        )
    else:
        outcome = "not_certified"
        scientific_classification = (
            "registered selected eigencoordinate bridge not certified"
        )

    return {
        "question": (
            "Do the registered Q006i right/left eigencoordinates rigorously "
            "represent the selected theorem spectral subspace?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "representative_waves": [list(wave) for wave in REPRESENTATIVE_WAVES],
            "branch_order": list(BRANCH_ORDER),
            "right_pivots": list(RIGHT_PIVOTS),
            "left_pivots": list(LEFT_PIVOTS),
            "search_box_component_radius": _fraction_record(SEARCH_RADIUS),
        },
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": scientific_classification,
        "claim_boundary": (
            "This identifies the registered linear eigencoordinates with the "
            "exact selected spectral subspace for the fixed 17x17 conservation "
            "leaf. It does not certify any quadratic, cubic, or quartic "
            "coefficient, an explicit neighborhood radius, finite-ball normal "
            "attraction, grid uniformity, or a continuum limit."
        ),
        "preserved_prior_outcomes": {
            "q007i_theorem_acceptance_changed": False,
            "q007h1_linear_acceptance_changed": False,
            "q007h_independent_preconditioner_inconclusive_changed": False,
            "q007f_finite_sample_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, certify the 300 quadratic forcing and homological "
            "systems before considering cubic or quartic jets."
        ),
    }


def run_q007j_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_eigencoordinate_bridge_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational Krawczyk selected-eigencoordinate bridge",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": 24,
            "representative_eigenpair_count": 6,
            "right_left_system_count": EXPECTED_SYSTEM_COUNT,
            "claim": (
                "linear eigencoordinate identification only; no Taylor-jet, "
                "explicit-radius, finite-ball, grid-uniform, or continuum claim"
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
    result = run_q007j_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
