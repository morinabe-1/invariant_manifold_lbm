"""Sealed Q007o exact-external-complement resolvent refinement.

The Q007n all-degree gap, scalar majorants, and 119-candidate radius grid are
held fixed.  Only the selected-output graph-gauge inverse bound is replaced by
an interval-certified six-dimensional external-complement resolvent bound.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import numpy as np

from research.q007n_explicit_local_radius import (
    CANDIDATE_EXPONENTS,
    MAJORANT_DECIMAL_DIGITS,
    MAXIMUM_CONTRACTION,
    NONLINEAR_MAJORANT_CONSTANT,
    _candidate_record,
    _exact_candidate_certificate,
    _round_up,
    _scalar_majorant_polynomials,
)
from ttim_lbm.checkerboard_filter import filtered_fourier_symbol
from ttim_lbm.equivariant_spectrum import (
    _c4_orbits,
    _certify_transported_block,
    _transport_preconditioner,
    rotate_wave,
)
from ttim_lbm.full2d_chart import MODE_ORDER, WAVE_ORDER, _build_complex_modes
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
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
    _matrix_multiply,
    _matrix_subtract,
    _sqrt_bounds,
    _strict_json_serializable,
    machin_pi_interval,
    rational_collision_symbol,
    rational_fourier_symbol,
    trigonometric_intervals,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_COMPLEX_DIMENSION = 24
EXTERNAL_BLOCK_DIMENSION = 6
REPRESENTATIVE_SELECTORS: tuple[
    tuple[WaveIndex, tuple[int, ...]], ...
] = (
    ((1, 0), (0, 1, 2, 3, 7, 8)),
    ((1, 1), (0, 1, 2, 3, 4, 5)),
)
MAXIMUM_COORDINATE_DEFECT = Fraction(1, 10**8)
MAXIMUM_RESIDUAL_GAP_FRACTION = Fraction(1, 2)
MAXIMUM_INTERNAL_PAIR_INVERSE = Fraction(10**14)
MINIMUM_IMPROVEMENT_FACTOR = Fraction(10**40)

ARTIFACT_FILENAMES = {
    "q007h1": "q007h1_equivariant_spectrum.json",
    "q007j": "q007j_eigencoordinate_bridge.json",
    "q007n": "q007n_explicit_local_radius.json",
}
REGISTERED_INPUT_SHA256 = {
    "q007h1": (
        "caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4"
    ),
    "q007j": (
        "feae846b81dc0991aa2c9babbd38ee72eb9ae493526655435cf0bf5951c7ec44"
    ),
    "q007n": (
        "7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36"
    ),
}
REGISTERED_Q007N_RUNNER_SHA256 = (
    "6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9"
)


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


def _canonical_json_sha256(value: Any) -> str:
    serialized = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return sha256(serialized.encode("utf-8")).hexdigest()


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    for name, filename in ARTIFACT_FILENAMES.items():
        path = directory / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        observed_sha256 = _file_sha256(path)
        scope = payload.get("mathematical_scope", {})
        base_scope_match = bool(
            scope.get("construction_grid") == [SIZE, SIZE]
            and float(scope.get("omega", np.nan)) == OMEGA
            and float(scope.get("eta", np.nan)) == ETA
        )
        if name == "q007h1":
            scope_match = bool(
                base_scope_match
                and scope.get("selected_complex_dimension")
                == SELECTED_COMPLEX_DIMENSION
                and scope.get("tail_degree") == 90
            )
        elif name == "q007j":
            scope_match = bool(
                base_scope_match
                and scope.get("selected_real_dimension")
                == SELECTED_COMPLEX_DIMENSION
                and scope.get("representative_eigenpair_count") == 6
                and scope.get("right_left_system_count") == 12
                and scope.get("conservation_treatment")
                == "fixed global mass and momentum leaf"
            )
        else:
            scope_match = bool(
                base_scope_match
                and scope.get("selected_real_dimension")
                == SELECTED_COMPLEX_DIMENSION
                and scope.get("selected_complexified_dimension")
                == SELECTED_COMPLEX_DIMENSION
                and scope.get("conservation_treatment")
                == "fixed global mass and momentum leaf"
            )
        expected_outcome = "accepted"
        runner_matches = True
        current_runner_sha256 = None
        if name == "q007n":
            current_runner_sha256 = _file_sha256(
                Path(__file__).resolve().with_name(
                    "q007n_explicit_local_radius.py"
                )
            )
            runner_matches = bool(
                payload.get("runner_source", {}).get("sha256")
                == REGISTERED_Q007N_RUNNER_SHA256
                and current_runner_sha256 == REGISTERED_Q007N_RUNNER_SHA256
            )
        record = {
            "filename": filename,
            "registered_sha256": REGISTERED_INPUT_SHA256[name],
            "sha256": observed_sha256,
            "sha256_matches": observed_sha256 == REGISTERED_INPUT_SHA256[name],
            "source_match": payload.get("source") == source_metadata(),
            "scope_match": scope_match,
            "schema_version": payload.get("schema_version"),
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "all_validity_gates_pass": _all_gates_pass(
                payload, "validity_gates"
            ),
            "all_hypothesis_gates_pass": _all_gates_pass(
                payload, "hypothesis_gates"
            ),
            "registered_q007n_runner_matches": runner_matches,
            "current_dependency_runner_sha256": current_runner_sha256,
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["source_match"]
            and record["scope_match"]
            and record["schema_version"] == 1
            and record["study_gate"] == "passed"
            and record["scientific_outcome"] == expected_outcome
            and record["all_validity_gates_pass"]
            and record["all_hypothesis_gates_pass"]
            and runner_matches
        )
        payloads[name] = payload
        records[name] = record
    return payloads, records


def _complex_box(
    value: complex,
    radius: Fraction,
) -> ComplexRationalInterval:
    point = _complex_point(value)
    return ComplexRationalInterval(
        RationalInterval(
            point.real.lower - radius,
            point.real.upper + radius,
        ),
        RationalInterval(
            point.imag.lower - radius,
            point.imag.upper + radius,
        ),
    )


def _complex_conjugate(
    value: ComplexRationalInterval,
) -> ComplexRationalInterval:
    return ComplexRationalInterval(value.real, -value.imag)


def _matrix_adjoint(
    matrix: ComplexIntervalMatrix,
) -> ComplexIntervalMatrix:
    return [
        [
            _complex_conjugate(matrix[row][column])
            for row in range(len(matrix))
        ]
        for column in range(len(matrix[0]))
    ]


def _matrix_rows(
    matrix: ComplexIntervalMatrix,
    rows: Sequence[int],
) -> ComplexIntervalMatrix:
    return [matrix[int(row)] for row in rows]


def _diagonal_matrix(values: Sequence[complex]) -> ComplexIntervalMatrix:
    dimension = len(values)
    return [
        [
            _complex_point(values[row])
            if row == column
            else ComplexRationalInterval.zero()
            for column in range(dimension)
        ]
        for row in range(dimension)
    ]


def _matrix_l1_norm_upper(matrix: ComplexIntervalMatrix) -> Fraction:
    if not matrix or not matrix[0]:
        raise ValueError("matrix must be nonempty")
    return max(
        sum(
            (
                _complex_rectangle_absolute_upper(matrix[row][column])
                for row in range(len(matrix))
            ),
            Fraction(0),
        )
        for column in range(len(matrix[0]))
    )


def _matrix_midpoint_numpy(matrix: ComplexIntervalMatrix) -> np.ndarray:
    return np.asarray(
        [
            [
                complex(
                    float((value.real.lower + value.real.upper) / 2),
                    float((value.imag.lower + value.imag.upper) / 2),
                )
                for value in row
            ]
            for row in matrix
        ],
        dtype=np.complex128,
    )


def _mode_boxes(
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    wave: WaveIndex,
    right_radius: Fraction,
    left_radius: Fraction,
) -> tuple[ComplexIntervalMatrix, ComplexIntervalMatrix]:
    right = [
        [
            _complex_box(
                modes[lookup[(wave, branch)]].right[row],
                right_radius,
            )
            for branch in MODE_ORDER
        ]
        for row in range(9)
    ]
    left = [
        [
            _complex_box(
                modes[lookup[(wave, branch)]].left[row],
                left_radius,
            )
            for branch in MODE_ORDER
        ]
        for row in range(9)
    ]
    return right, left


def _representative_certificate(
    wave: WaveIndex,
    selector_rows: tuple[int, ...],
    modes: Sequence[Any],
    lookup: dict[tuple[WaveIndex, str], int],
    right_radius: Fraction,
    left_radius: Fraction,
    all_degree_gap: Fraction,
    tangent_norm: Fraction,
    trigonometric: dict[int, tuple[RationalInterval, RationalInterval]],
    collision: tuple[tuple[Fraction, ...], ...],
    q007h1_records: dict[WaveIndex, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    orbit = next(orbit for orbit in _c4_orbits() if wave in orbit.members)
    source_wave = orbit.representative
    rotation_power = orbit.members.index(wave)
    source_kx = 2.0 * np.pi * source_wave[0] / SIZE
    source_ky = 2.0 * np.pi * source_wave[1] / SIZE
    source_center = filtered_fourier_symbol(
        source_kx,
        source_ky,
        OMEGA,
        ETA,
    )
    eigenvalues, source_eigenvectors = np.linalg.eig(source_center)
    source_inverse_candidate = np.linalg.inv(source_eigenvectors)
    eigenvectors, inverse_candidate = _transport_preconditioner(
        source_eigenvectors,
        source_inverse_candidate,
        rotation_power,
    )
    selected_indices = tuple(
        int(index) for index in np.argsort(np.abs(eigenvalues))[::-1][:3]
    )
    selected_index_set = frozenset(selected_indices)
    external_indices = tuple(
        index for index in range(9) if index not in selected_index_set
    )
    symbol = rational_fourier_symbol(wave, trigonometric, collision)
    block_proof = _certify_transported_block(
        wave,
        symbol,
        eigenvalues,
        eigenvectors,
        inverse_candidate,
        selected_indices,
    )
    stored_digest = q007h1_records[wave]["exact_proof_digest_sha256"]
    digest_matches = block_proof.proof_digest == stored_digest

    selected_right, selected_left = _mode_boxes(
        modes,
        lookup,
        wave,
        right_radius,
        left_radius,
    )
    left_adjoint = _matrix_adjoint(selected_left)
    selected_projector = _matrix_multiply(selected_right, left_adjoint)
    external_projector = _matrix_subtract(
        _identity_matrix(9),
        selected_projector,
    )
    external_vectors = _matrix_from_numpy(eigenvectors[:, external_indices])
    external_diagonal = _diagonal_matrix(eigenvalues[list(external_indices)])
    external_basis = _matrix_multiply(
        external_projector,
        external_vectors,
    )
    coordinate_matrix = _matrix_rows(external_basis, selector_rows)
    coordinate_midpoint = _matrix_midpoint_numpy(coordinate_matrix)
    coordinate_preconditioner = _matrix_from_numpy(
        np.linalg.inv(coordinate_midpoint)
    )
    coordinate_defect_matrix = _matrix_subtract(
        _identity_matrix(EXTERNAL_BLOCK_DIMENSION),
        _matrix_multiply(
            coordinate_preconditioner,
            coordinate_matrix,
        ),
    )
    coordinate_defect = _matrix_l1_norm_upper(coordinate_defect_matrix)
    preconditioner_norm = _matrix_l1_norm_upper(coordinate_preconditioner)
    coordinate_inverse = (
        preconditioner_norm / (1 - coordinate_defect)
        if coordinate_defect < 1
        else Fraction(10**1000)
    )

    residual = _matrix_subtract(
        _matrix_multiply(symbol, external_vectors),
        _matrix_multiply(external_vectors, external_diagonal),
    )
    projected_residual = _matrix_multiply(external_projector, residual)
    selected_projected_residual = _matrix_rows(
        projected_residual,
        selector_rows,
    )
    coordinate_residual_norm = _matrix_l1_norm_upper(
        selected_projected_residual
    )
    representation_perturbation = (
        coordinate_inverse * coordinate_residual_norm
    )
    external_basis_norm = _matrix_l1_norm_upper(external_basis)
    selected_projector_rows_norm = _matrix_l1_norm_upper(
        _matrix_rows(external_projector, selector_rows)
    )
    left_operator_norm = _matrix_l1_norm_upper(left_adjoint)
    gap_margin = all_degree_gap - representation_perturbation
    chart_inverse = (
        external_basis_norm
        * coordinate_inverse
        * selected_projector_rows_norm
        / gap_margin
        if gap_margin > 0
        else Fraction(10**1000)
    )
    weighted_reduced_inverse = tangent_norm * left_operator_norm
    pair_inverse = max(chart_inverse, weighted_reduced_inverse)

    center_selected_order = tuple(sorted(selected_indices))
    finite_centers = bool(
        np.all(np.isfinite(source_center))
        and np.all(np.isfinite(eigenvalues))
        and np.all(np.isfinite(eigenvectors))
        and np.all(np.isfinite(inverse_candidate))
        and np.all(np.isfinite(coordinate_midpoint))
    )
    exact: dict[str, Fraction | bool] = {
        "coordinate_defect": coordinate_defect,
        "preconditioner_norm": preconditioner_norm,
        "coordinate_inverse": coordinate_inverse,
        "external_projector_norm": _matrix_l1_norm_upper(
            external_projector
        ),
        "external_basis_norm": external_basis_norm,
        "selected_projector_rows_norm": selected_projector_rows_norm,
        "coordinate_residual_norm": coordinate_residual_norm,
        "representation_perturbation": representation_perturbation,
        "gap_margin": gap_margin,
        "left_operator_norm": left_operator_norm,
        "chart_inverse": chart_inverse,
        "weighted_reduced_inverse": weighted_reduced_inverse,
        "pair_inverse": pair_inverse,
        "digest_matches": digest_matches,
        "finite_centers": finite_centers,
    }
    serializable = {
        "wave_index": list(wave),
        "q007h1_source_wave_index": list(source_wave),
        "q007h1_rotation_power": rotation_power,
        "selector_rows": list(selector_rows),
        "selected_indices_by_decreasing_modulus": list(selected_indices),
        "selected_indices_sorted": list(center_selected_order),
        "external_indices_in_returned_order": list(external_indices),
        "selected_count": len(selected_indices),
        "external_count": len(external_indices),
        "q007h1_proof_digest_sha256": block_proof.proof_digest,
        "q007h1_artifact_digest_sha256": stored_digest,
        "q007h1_proof_digest_matches": digest_matches,
        "q007h1_bauer_fike_radius": _fraction_record(
            block_proof.bauer_fike_radius
        ),
        "finite_numpy_centers": finite_centers,
        "coordinate_defect_l1_upper": _fraction_record(coordinate_defect),
        "registered_coordinate_defect_upper": _fraction_record(
            MAXIMUM_COORDINATE_DEFECT
        ),
        "coordinate_preconditioner_l1_norm": _fraction_record(
            preconditioner_norm
        ),
        "coordinate_inverse_l1_upper": _fraction_record(coordinate_inverse),
        "external_projector_l1_upper": _fraction_record(
            exact["external_projector_norm"]
        ),
        "external_basis_l1_upper": _fraction_record(external_basis_norm),
        "selector_projector_l1_upper": _fraction_record(
            selected_projector_rows_norm
        ),
        "selector_projected_residual_l1_upper": _fraction_record(
            coordinate_residual_norm
        ),
        "representation_perturbation_gamma": _fraction_record(
            representation_perturbation
        ),
        "registered_gamma_upper": _fraction_record(
            all_degree_gap * MAXIMUM_RESIDUAL_GAP_FRACTION
        ),
        "all_degree_gap_margin": _fraction_record(gap_margin),
        "left_operator_l1_upper": _fraction_record(left_operator_norm),
        "chart_internal_inverse_l1_upper": _fraction_record(chart_inverse),
        "weighted_reduced_inverse_upper": _fraction_record(
            weighted_reduced_inverse
        ),
        "pair_internal_inverse_upper": _fraction_record(pair_inverse),
        "coordinate_certificate_passed": bool(
            finite_centers
            and digest_matches
            and len(selected_indices) == 3
            and len(external_indices) == EXTERNAL_BLOCK_DIMENSION
            and coordinate_defect < MAXIMUM_COORDINATE_DEFECT
            and representation_perturbation
            < all_degree_gap * MAXIMUM_RESIDUAL_GAP_FRACTION
            and gap_margin > 0
        ),
    }
    return serializable, exact


def _working_coefficients_from_q007n(
    q007n_cycle: dict[str, Any],
) -> dict[str, Fraction]:
    section = q007n_cycle["coefficient_reproduction_and_norms"]
    coefficients = {
        "c_v": _fraction_from_record(
            section["working_tangent_l1_operator_norm_upper"]
        )
    }
    for record in section["degree_records"]:
        degree = int(record["degree"])
        coefficients[f"h{degree}"] = _fraction_from_record(
            record["working_chart_operator_norm_upper"]
        )
        coefficients[f"g{degree}"] = _fraction_from_record(
            record["working_reduced_operator_norm_upper"]
        )
        coefficients[f"h{degree}_box"] = _fraction_from_record(
            record["working_chart_box_operator_norm_upper"]
        )
        coefficients[f"g{degree}_box"] = _fraction_from_record(
            record["working_reduced_box_operator_norm_upper"]
        )
    return coefficients


def _radius_scan(
    coefficients: dict[str, Fraction],
    selected_radius: Fraction,
    pair_inverse: Fraction,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    spectral = {
        "selected_maximum": selected_radius,
        "pair_inverse": pair_inverse,
    }
    polynomials = _scalar_majorant_polynomials(
        coefficients,
        selected_radius,
    )
    records = []
    exact_records = []
    for exponent in CANDIDATE_EXPONENTS:
        record, exact = _candidate_record(
            exponent,
            coefficients,
            spectral,
            polynomials,
        )
        records.append(record)
        exact_records.append(exact)

    passing_indices = [
        index for index, record in enumerate(exact_records) if record["passed"]
    ]
    selected_index = passing_indices[0] if passing_indices else None
    selected = (
        records[selected_index] if selected_index is not None else None
    )
    selected_exact = (
        exact_records[selected_index] if selected_index is not None else None
    )
    previous = (
        records[selected_index - 1]
        if selected_index is not None and selected_index > 0
        else None
    )
    previous_exact = (
        exact_records[selected_index - 1]
        if selected_index is not None and selected_index > 0
        else None
    )
    selected_summary = None
    if selected is not None and selected_exact is not None:
        radius = selected_exact["radius"]
        correction_radius = selected_exact["correction_radius"]
        assert isinstance(radius, Fraction)
        assert isinstance(correction_radius, Fraction)
        chart_box = sum(
            coefficients[f"h{degree}_box"] * radius**degree
            for degree in (2, 3, 4)
        )
        reduced_box = sum(
            coefficients[f"g{degree}_box"] * radius**degree
            for degree in (2, 3, 4)
        )
        center_error = correction_radius + max(
            chart_box,
            coefficients["c_v"] * reduced_box,
        )
        real_radius = 17 * radius / _sqrt_bounds(Fraction(24)).upper
        selected_summary = {
            **selected,
            "real_euclidean_radius_lower": _fraction_record(real_radius),
            "real_radius_formula": "17 * modal_radius / sqrt(24)",
            "registered_numerical_quartic_center_pair_error_upper": (
                _fraction_record(center_error)
            ),
            "is_largest_passing_registered_candidate": True,
        }

    maximal_selection_valid = bool(
        selected_index is not None
        and selected is not None
        and selected["passed"]
        and (
            selected_index == 0
            or (previous is not None and not previous["passed"])
        )
        and all(not records[index]["passed"] for index in range(selected_index))
    )
    summary = {
        "candidate_exponents": list(CANDIDATE_EXPONENTS),
        "candidate_count": len(CANDIDATE_EXPONENTS),
        "candidate_order": "1e-2, 1e-3, ..., 1e-120",
        "nonnegative_tail_count": sum(
            record["tail_nonnegative"] for record in records
        ),
        "positive_domain_buffer_count": sum(
            bool(
                record["density_buffer_positive"]
                and record["reduced_range_buffer_positive"]
            )
            for record in records
        ),
        "passing_candidate_count": len(passing_indices),
        "selected_candidate": selected_summary,
        "previous_larger_candidate": previous,
        "maximal_selection_valid": maximal_selection_valid,
        "exact_boundary_certificate": {
            "selected": _exact_candidate_certificate(selected_exact),
            "previous_larger": _exact_candidate_certificate(previous_exact),
            "representation_note": (
                "All 119 decisions use the unchanged Q007n Fraction "
                "majorant; full base-16 rationals are retained at the new "
                "pass/fail boundary."
            ),
        },
        "records": records,
    }
    return summary, exact_records


def _c4_coverage() -> tuple[tuple[WaveIndex, ...], bool]:
    covered: list[WaveIndex] = []
    for representative, _selector in REPRESENTATIVE_SELECTORS:
        wave = representative
        for _ in range(4):
            covered.append(wave)
            wave = rotate_wave(wave)
    unique = tuple(dict.fromkeys(covered))
    return unique, set(unique) == set(WAVE_ORDER) and len(unique) == 8


def run_external_complement_radius_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    q007n_cycle = payloads["q007n"]["cycle"]
    q007n_spectral = q007n_cycle["spectral_separation_and_inverse"]
    q007j_transport = payloads["q007j"]["cycle"][
        "transport_and_normalization"
    ]
    right_radius = _fraction_from_record(
        q007j_transport["maximum_right_correction_upper"]
    )
    left_radius = _fraction_from_record(
        q007j_transport["maximum_biorthogonal_left_correction_upper"]
    )
    all_degree_gap = _fraction_from_record(
        q007n_spectral["working_uniform_absolute_gap_lower"]
    )
    coefficients = _working_coefficients_from_q007n(q007n_cycle)
    tangent_norm = coefficients["c_v"]
    old_pair_inverse = _fraction_from_record(
        q007n_spectral["pair_homological_inverse_upper"]
    )
    external_inverse = _fraction_from_record(
        q007n_spectral["external_resolvent_l1_upper"]
    )
    zero_inverse = _fraction_from_record(
        q007n_spectral["zero_wave_fixed_leaf_inverse_upper"]
    )
    selected_radius = _fraction_from_record(
        q007n_spectral["working_selected_spectral_radius_upper"]
    )

    trigonometric = trigonometric_intervals(machin_pi_interval())
    collision = rational_collision_symbol()
    modes, lookup = _build_complex_modes(SIZE, OMEGA, ETA)
    q007h1_records = {
        tuple(record["wave_index"]): record
        for record in payloads["q007h1"]["cycle"]["eigencertification"][
            "block_records"
        ]
    }
    representative_records = []
    representative_exact = []
    for wave, selector in REPRESENTATIVE_SELECTORS:
        record, exact = _representative_certificate(
            wave,
            selector,
            modes,
            lookup,
            right_radius,
            left_radius,
            all_degree_gap,
            tangent_norm,
            trigonometric,
            collision,
            q007h1_records,
        )
        representative_records.append(record)
        representative_exact.append(exact)

    raw_internal_inverse = max(
        exact["pair_inverse"] for exact in representative_exact
    )
    assert isinstance(raw_internal_inverse, Fraction)
    working_internal_inverse = _round_up(
        raw_internal_inverse,
        MAJORANT_DECIMAL_DIGITS,
    )
    raw_total_inverse = max(
        raw_internal_inverse,
        external_inverse,
        zero_inverse,
    )
    working_total_inverse = _round_up(
        raw_total_inverse,
        MAJORANT_DECIMAL_DIGITS,
    )
    upper_bound_reduction_factor = old_pair_inverse / working_total_inverse

    old_scan, _old_exact = _radius_scan(
        coefficients,
        selected_radius,
        old_pair_inverse,
    )
    q007n_records = q007n_cycle["radius_search"]["records"]
    old_records_reproduced = old_scan["records"] == q007n_records
    new_scan, new_exact = _radius_scan(
        coefficients,
        selected_radius,
        working_total_inverse,
    )
    old_selected = q007n_cycle["radius_search"]["selected_candidate"]
    new_selected = new_scan["selected_candidate"]
    previous = new_scan["previous_larger_candidate"]
    old_selected_exponent = int(old_selected["candidate_exponent"])
    new_selected_exponent = (
        None if new_selected is None else int(new_selected["candidate_exponent"])
    )
    old_radius_still_passes = bool(
        new_exact[old_selected_exponent - CANDIDATE_EXPONENTS[0]]["passed"]
    )

    reused_section = {
        "coefficient_reproduction_and_norms_sha256": _canonical_json_sha256(
            q007n_cycle["coefficient_reproduction_and_norms"]
        ),
        "structural_majorant_audit_sha256": _canonical_json_sha256(
            q007n_cycle["structural_majorant_audit"]
        ),
        "candidate_exponents_match": (
            q007n_cycle["radius_search"]["candidate_exponents"]
            == list(CANDIDATE_EXPONENTS)
        ),
        "candidate_count_match": (
            q007n_cycle["radius_search"]["candidate_count"]
            == len(CANDIDATE_EXPONENTS)
        ),
        "maximum_contraction": _fraction_record(MAXIMUM_CONTRACTION),
        "nonlinear_majorant_constant": _fraction_record(
            NONLINEAR_MAJORANT_CONSTANT
        ),
        "external_resolvent_l1_upper": q007n_spectral[
            "external_resolvent_l1_upper"
        ],
        "zero_wave_fixed_leaf_inverse_upper": q007n_spectral[
            "zero_wave_fixed_leaf_inverse_upper"
        ],
        "old_119_candidate_records_reproduced_exactly": (
            old_records_reproduced
        ),
        "only_pair_inverse_changed_in_new_scan": True,
    }
    coverage, coverage_passed = _c4_coverage()
    inverse_refinement = {
        "norm": "complex induced l1 with rational rectangle modulus upper",
        "selected_projector_identity": (
            "P=V L*, Q=I-P, L*V=I, and AQ=QA exactly"
        ),
        "external_coordinate_identity": (
            "U=QE, C=JU, A U=U D+Q(AE-ED)"
        ),
        "center_gap_transfer": (
            "the Q007i modulus intervals used by Q007n contain the Q007h1 "
            "approximate external center moduli, so the unchanged absolute "
            "gap lower also bounds min_j |d_j-p|"
        ),
        "graph_gauge_reduced_identity": "G=-L*F",
        "all_degree_gap_lower_reused_from_q007n": _fraction_record(
            all_degree_gap
        ),
        "q007j_right_component_box_radius": _fraction_record(right_radius),
        "q007j_left_component_box_radius": _fraction_record(left_radius),
        "representative_records": representative_records,
        "raw_internal_pair_inverse_upper": _fraction_record(
            raw_internal_inverse
        ),
        "working_internal_pair_inverse_upper": _fraction_record(
            working_internal_inverse
        ),
        "q007n_external_inverse_upper": _fraction_record(external_inverse),
        "q007n_zero_inverse_upper": _fraction_record(zero_inverse),
        "raw_total_pair_inverse_upper": _fraction_record(raw_total_inverse),
        "working_total_pair_inverse_upper": _fraction_record(
            working_total_inverse
        ),
        "q007n_pair_inverse_upper": _fraction_record(old_pair_inverse),
        "pair_inverse_upper_reduction_factor": _fraction_record(
            upper_bound_reduction_factor
        ),
        "outward_decimal_grid_digits": MAJORANT_DECIMAL_DIGITS,
    }
    radius_comparison = {
        "q007n_selected_candidate_exponent": old_selected_exponent,
        "q007n_selected_modal_radius_decimal": old_selected[
            "modal_radius_decimal"
        ],
        "q007n_candidate_passes_with_refined_inverse": (
            old_radius_still_passes
        ),
        "refined_radius_search": new_scan,
    }

    representative_reconstruction_passed = all(
        record["q007h1_proof_digest_matches"]
        and record["selected_count"] == 3
        and record["external_count"] == EXTERNAL_BLOCK_DIMENSION
        and tuple(record["selector_rows"]) == selector
        for record, (_wave, selector) in zip(
            representative_records,
            REPRESENTATIVE_SELECTORS,
            strict=True,
        )
    )
    coordinate_certificates_passed = all(
        record["coordinate_certificate_passed"]
        for record in representative_records
    )
    q007h1_covariance = payloads["q007h1"]["cycle"]["validity_gates"][
        "exact_symbol_covariance"
    ]["passed"]
    q007j_transport_passed = bool(
        q007j_transport["transported_mode_count"] == 24
        and q007j_transport["unique_mode_label_count"] == 24
        and q007j_transport["conjugate_label_mismatch_count"] == 0
    )
    reuse_passed = bool(
        reused_section["candidate_exponents_match"]
        and reused_section["candidate_count_match"]
        and old_records_reproduced
        and _fraction_from_record(
            reused_section["nonlinear_majorant_constant"]
        )
        == NONLINEAR_MAJORANT_CONSTANT
    )
    serializable_sections = {
        "input_artifacts": input_records,
        "q007n_reuse_audit": reused_section,
        "external_complement_inverse_refinement": inverse_refinement,
        "radius_comparison": radius_comparison,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    validity_gates = {
        "registered_inputs": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": (
                "three registered artifact hashes/source/scope/gates and the "
                "Q007n runner hash match"
            ),
            "value": {
                name: record["passed"] for name, record in input_records.items()
            },
        },
        "representative_reconstruction": {
            "passed": representative_reconstruction_passed,
            "threshold": (
                "two Q007h1 proof digests, 3/6 columns, and fixed selectors match"
            ),
            "value": [
                {
                    "wave_index": record["wave_index"],
                    "digest_matches": record[
                        "q007h1_proof_digest_matches"
                    ],
                    "selected_count": record["selected_count"],
                    "external_count": record["external_count"],
                    "selector_rows": record["selector_rows"],
                }
                for record in representative_records
            ],
        },
        "external_coordinate_certificates": {
            "passed": coordinate_certificates_passed,
            "threshold": (
                "each epsilon_C <1e-8 and gamma < delta/2 with positive gap"
            ),
            "value": [
                {
                    "wave_index": record["wave_index"],
                    "epsilon_C": record["coordinate_defect_l1_upper"]["float"],
                    "gamma": record[
                        "representation_perturbation_gamma"
                    ]["float"],
                    "gap_margin": record["all_degree_gap_margin"]["float"],
                }
                for record in representative_records
            ],
        },
        "c4_selected_wave_coverage": {
            "passed": bool(
                coverage_passed
                and q007h1_covariance
                and q007j_transport_passed
            ),
            "threshold": (
                "two representatives cover all eight selected waves and "
                "registered exact covariance/24-mode transport passed"
            ),
            "value": {
                "covered_waves": [list(wave) for wave in coverage],
                "q007h1_exact_covariance": q007h1_covariance,
                "q007j_transport": q007j_transport_passed,
            },
        },
        "q007n_majorants_reused": {
            "passed": reuse_passed,
            "threshold": (
                "external/zero bounds, scalar majorants, grid, and all 119 "
                "old candidate records reproduce exactly"
            ),
            "value": {
                "old_records_reproduced": old_records_reproduced,
                "candidate_exponents_match": reused_section[
                    "candidate_exponents_match"
                ],
                "candidate_count_match": reused_section[
                    "candidate_count_match"
                ],
            },
        },
        "finite_strict_json": {
            "passed": finite_strict_json,
            "threshold": "all summaries finite and strict JSON serializable",
            "value": finite_strict_json,
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    selected_boundary_passed = bool(
        new_selected is not None
        and previous is not None
        and new_selected["density_buffer_positive"]
        and new_selected["reduced_range_buffer_positive"]
        and new_selected["contraction_strictly_below_one_half"]
        and new_selected["radii_inequality_strict"]
        and new_selected["passed"]
        and not previous["passed"]
        and new_scan["maximal_selection_valid"]
    )
    hypothesis_gates = {
        "registered_internal_inverse_upper": {
            "passed": working_internal_inverse
            <= MAXIMUM_INTERNAL_PAIR_INVERSE,
            "threshold": "new internal pair inverse upper <=1e14",
            "value": float(working_internal_inverse),
        },
        "pair_inverse_strictly_improved": {
            "passed": bool(
                working_total_inverse < old_pair_inverse
                and upper_bound_reduction_factor
                >= MINIMUM_IMPROVEMENT_FACTOR
            ),
            "threshold": (
                "new total inverse is strict smaller with improvement >=1e40"
            ),
            "value": {
                "new": float(working_total_inverse),
                "old": float(old_pair_inverse),
                "upper_bound_reduction_factor": float(
                    upper_bound_reduction_factor
                ),
            },
        },
        "registered_radius_strictly_improved": {
            "passed": bool(
                old_radius_still_passes
                and new_selected_exponent is not None
                and new_selected_exponent < old_selected_exponent
            ),
            "threshold": (
                "Q007n radius remains passing and largest passing candidate "
                "is strictly larger"
            ),
            "value": {
                "old_exponent": old_selected_exponent,
                "new_exponent": new_selected_exponent,
                "old_radius_still_passes": old_radius_still_passes,
            },
        },
        "new_boundary_radii_inequality": {
            "passed": selected_boundary_passed,
            "threshold": (
                "new maximum has positive buffers, Z<1/2, strict radii "
                "inequality, and previous candidate fails"
            ),
            "value": {
                "selected_exponent": new_selected_exponent,
                "previous_exponent": (
                    None
                    if previous is None
                    else previous["candidate_exponent"]
                ),
                "selected_passed": (
                    False if new_selected is None else new_selected["passed"]
                ),
                "previous_passed": (
                    None if previous is None else previous["passed"]
                ),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = (
            "registered external-complement resolvent audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "exact external-complement resolvent strictly sharpens the "
            "registered explicit radius"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered external-complement resolvent did not certify a "
            "sharper radius"
        )

    return {
        "question": (
            "Does the exact six-dimensional external-complement resolvent "
            "strictly sharpen Q007n without changing its gap or majorants?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "representative_selectors": [
                {
                    "wave_index": list(wave),
                    "selector_rows": list(selector),
                }
                for wave, selector in REPRESENTATIVE_SELECTORS
            ],
            "maximum_coordinate_defect": _fraction_record(
                MAXIMUM_COORDINATE_DEFECT
            ),
            "maximum_gamma_gap_fraction": _fraction_record(
                MAXIMUM_RESIDUAL_GAP_FRACTION
            ),
            "maximum_internal_pair_inverse": _fraction_record(
                MAXIMUM_INTERNAL_PAIR_INVERSE
            ),
            "minimum_improvement_factor": _fraction_record(
                MINIMUM_IMPROVEMENT_FACTOR
            ),
            "candidate_exponents": list(CANDIDATE_EXPONENTS),
            "maximum_contraction": _fraction_record(MAXIMUM_CONTRACTION),
        },
        "input_artifacts": input_records,
        "q007n_reuse_audit": reused_section,
        "external_complement_inverse_refinement": inverse_refinement,
        "radius_comparison": radius_comparison,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "q007n_explicit_radius_preserved": bool(
                validity_passed and old_radius_still_passes
            ),
            "refined_explicit_modal_l1_radius_certified": hypotheses_passed,
            "identified_with_q007i_theorem_manifold": hypotheses_passed,
        },
        "claim_boundary": (
            "This sharpens only the explicit analytic existence radius for "
            "the fixed 17x17 filtered map on one conservation leaf. It is the "
            "largest passing member of the unchanged decimal grid, not an "
            "optimal radius. It does not certify finite-ball normal "
            "attraction, forward invariance, positivity, grid uniformity, a "
            "continuum limit, or individual external eigenvectors, and it "
            "does not alter Q007c1's finite-amplitude rejection."
        ),
        "preserved_prior_outcomes": {
            "q007n_explicit_radius_acceptance_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007i_qualitative_theorem_acceptance_changed": False,
            "q007j_linear_eigencoordinate_acceptance_changed": False,
            "q007h1_linear_spectral_acceptance_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, use the refined local radius as fixed input to a "
            "separate finite-ball normal-attraction gate."
        ),
    }


def run_q007o_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_external_complement_radius_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "rational exact-external-complement explicit-radius refinement"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": SELECTED_COMPLEX_DIMENSION,
            "selected_complex_dimension": SELECTED_COMPLEX_DIMENSION,
            "claim": (
                "sharper explicit analytic existence radius only; no finite-"
                "ball normal-attraction, forward-invariance, positivity, "
                "grid-uniform, or continuum claim"
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
    result = run_q007o_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
