"""Sealed Q007p finite-tube normal-attraction certification.

The Q007o analytic manifold and its radius are held fixed.  This audit builds
an interval-certified external-coordinate norm on every Fourier block and
checks a registered finite tube by exact ``fractions.Fraction`` majorants.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from research.q007n_explicit_local_radius import (
    NONLINEAR_MAJORANT_CONSTANT,
)
from research.q007o_external_complement_radius import (
    _diagonal_matrix,
    _fraction_from_record,
    _matrix_l1_norm_upper,
    _working_coefficients_from_q007n,
    run_external_complement_radius_audit,
)
from ttim_lbm.checkerboard_filter import filtered_fourier_symbol
from ttim_lbm.equivariant_spectrum import (
    QUARTER_TURN_MAPPING,
    _c4_orbits,
    _certify_transported_block,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    SELECTED_WAVES,
    VELOCITIES,
    WEIGHTS,
    ComplexIntervalMatrix,
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
EXTERNAL_COMPLEX_DIMENSION = 2574
NONSELECTED_REPRESENTATIVE_COUNT = 70
SELECTED_REPRESENTATIVE_COUNT = 2
TOTAL_WAVE_COUNT = 289

ANALYTIC_RADIUS = Fraction(1, 10**18)
BASE_RADIUS = Fraction(1, 10**19)
NORMAL_RADIUS = Fraction(1, 10**20)
MAXIMUM_COORDINATE_DEFECT = Fraction(1, 10**8)
MAXIMUM_SYNTHESIS_CONSTANT = Fraction(4)
MAXIMUM_ANALYSIS_CONSTANT = Fraction(40)
MAXIMUM_SELECTED_ANALYSIS_CONSTANT = Fraction(2)
MAXIMUM_NORMAL_CONTRACTION = Fraction(99, 100)
MAXIMUM_DOMINATION_RATIO = Fraction(999, 1000)

ARTIFACT_FILENAMES = {
    "q007h1": "q007h1_equivariant_spectrum.json",
    "q007n": "q007n_explicit_local_radius.json",
    "q007o": "q007o_external_complement_radius.json",
}
REGISTERED_INPUT_SHA256 = {
    "q007h1": (
        "caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4"
    ),
    "q007n": (
        "7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36"
    ),
    "q007o": (
        "36a350b27658ce0699727640d65c48cf0700f999ca1881b07d45825d086158fd"
    ),
}
REGISTERED_RUNNER_SHA256 = {
    "q007n": (
        "6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9"
    ),
    "q007o": (
        "d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7"
    ),
}


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _all_gates_pass(payload: dict[str, Any], key: str) -> bool:
    gates = payload.get("cycle", {}).get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _scope_matches(name: str, payload: dict[str, Any]) -> bool:
    scope = payload.get("mathematical_scope", {})
    base = bool(
        scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega", np.nan)) == OMEGA
        and float(scope.get("eta", np.nan)) == ETA
    )
    if name == "q007h1":
        return bool(
            base
            and scope.get("selected_complex_dimension")
            == SELECTED_COMPLEX_DIMENSION
            and scope.get("excluded_complex_dimension")
            == EXTERNAL_COMPLEX_DIMENSION
            and scope.get("nonzero_c4_representative_count") == 72
            and scope.get("nonzero_fourier_block_count") == 288
            and scope.get("tail_degree") == 90
        )
    if name == "q007n":
        return bool(
            base
            and scope.get("conservation_treatment")
            == "fixed global mass and momentum leaf"
            and scope.get("selected_real_dimension")
            == SELECTED_COMPLEX_DIMENSION
            and scope.get("selected_complexified_dimension")
            == SELECTED_COMPLEX_DIMENSION
        )
    return bool(
        base
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
        and scope.get("selected_real_dimension") == SELECTED_COMPLEX_DIMENSION
        and scope.get("selected_complex_dimension")
        == SELECTED_COMPLEX_DIMENSION
    )


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    runner_directory = Path(__file__).resolve().parent
    for name, filename in ARTIFACT_FILENAMES.items():
        path = directory / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        observed_sha256 = _file_sha256(path)
        registered_runner = REGISTERED_RUNNER_SHA256.get(name)
        observed_runner = None
        artifact_runner = payload.get("runner_source", {}).get("sha256")
        if registered_runner is not None:
            observed_runner = _file_sha256(
                runner_directory / filename.replace(".json", ".py")
            )
        runner_matches = bool(
            registered_runner is None
            or (
                observed_runner == registered_runner
                and artifact_runner == registered_runner
            )
        )
        record = {
            "filename": filename,
            "registered_sha256": REGISTERED_INPUT_SHA256[name],
            "sha256": observed_sha256,
            "sha256_matches": observed_sha256 == REGISTERED_INPUT_SHA256[name],
            "sha256_newline_normalization": "UTF-8 text with universal newlines",
            "source_match": payload.get("source") == source_metadata(),
            "scope_match": _scope_matches(name, payload),
            "schema_version": payload.get("schema_version"),
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "all_validity_gates_pass": _all_gates_pass(payload, "validity_gates"),
            "all_hypothesis_gates_pass": _all_gates_pass(
                payload, "hypothesis_gates"
            ),
            "registered_runner_sha256": registered_runner,
            "artifact_runner_sha256": artifact_runner,
            "observed_runner_sha256": observed_runner,
            "runner_sha_matches": runner_matches,
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["source_match"]
            and record["scope_match"]
            and record["schema_version"] == 1
            and record["study_gate"] == "passed"
            and record["scientific_outcome"] == "accepted"
            and record["all_validity_gates_pass"]
            and record["all_hypothesis_gates_pass"]
            and runner_matches
        )
        payloads[name] = payload
        records[name] = record
    return payloads, records


def _complex_center_modulus_upper(value: complex) -> Fraction:
    return _complex_rectangle_absolute_upper(_complex_point(value))


def _nonselected_coordinate_certificate(
    wave: WaveIndex,
    symbol: ComplexIntervalMatrix,
    stored_record: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    kx = 2.0 * np.pi * wave[0] / SIZE
    ky = 2.0 * np.pi * wave[1] / SIZE
    center = filtered_fourier_symbol(kx, ky, OMEGA, ETA)
    eigenvalues, eigenvectors = np.linalg.eig(center)
    inverse_candidate = np.linalg.inv(eigenvectors)
    proof = _certify_transported_block(
        wave,
        symbol,
        eigenvalues,
        eigenvectors,
        inverse_candidate,
        (),
    )

    eigenvector_box = _matrix_from_numpy(eigenvectors)
    inverse_box = _matrix_from_numpy(inverse_candidate)
    diagonal_box = _diagonal_matrix(eigenvalues)
    defect_matrix = _matrix_subtract(
        _identity_matrix(9),
        _matrix_multiply(inverse_box, eigenvector_box),
    )
    coordinate_defect = _matrix_l1_norm_upper(defect_matrix)
    inverse_candidate_norm = _matrix_l1_norm_upper(inverse_box)
    coordinate_inverse = (
        inverse_candidate_norm / (1 - coordinate_defect)
        if coordinate_defect < 1
        else Fraction(10**1000)
    )
    residual_matrix = _matrix_subtract(
        _matrix_multiply(symbol, eigenvector_box),
        _matrix_multiply(eigenvector_box, diagonal_box),
    )
    residual = _matrix_l1_norm_upper(residual_matrix)
    representation_perturbation = coordinate_inverse * residual
    center_radius = max(
        _complex_center_modulus_upper(value) for value in eigenvalues
    )
    linear_contraction = center_radius + representation_perturbation
    synthesis = _matrix_l1_norm_upper(eigenvector_box)
    finite_centers = bool(
        np.all(np.isfinite(center))
        and np.all(np.isfinite(eigenvalues))
        and np.all(np.isfinite(eigenvectors))
        and np.all(np.isfinite(inverse_candidate))
    )
    digest_matches = proof.proof_digest == stored_record[
        "exact_proof_digest_sha256"
    ]
    exact: dict[str, Fraction | bool] = {
        "coordinate_defect": coordinate_defect,
        "inverse_candidate_norm": inverse_candidate_norm,
        "coordinate_inverse": coordinate_inverse,
        "residual": residual,
        "representation_perturbation": representation_perturbation,
        "center_radius": center_radius,
        "linear_contraction": linear_contraction,
        "synthesis": synthesis,
        "analysis": coordinate_inverse,
        "finite_centers": finite_centers,
        "digest_matches": digest_matches,
    }
    orbit = next(orbit for orbit in _c4_orbits() if orbit.representative == wave)
    serializable = {
        "wave_index": list(wave),
        "orbit_members": [list(member) for member in orbit.members],
        "orbit_member_count": len(orbit.members),
        "coordinate_dimension": 9,
        "selected_count": proof.selected_count,
        "excluded_count": proof.excluded_count,
        "q007h1_proof_digest_sha256": proof.proof_digest,
        "q007h1_artifact_digest_sha256": stored_record[
            "exact_proof_digest_sha256"
        ],
        "q007h1_proof_digest_matches": digest_matches,
        "finite_numpy_centers": finite_centers,
        "coordinate_defect_l1_upper": _fraction_record(coordinate_defect),
        "inverse_candidate_l1_upper": _fraction_record(inverse_candidate_norm),
        "coordinate_inverse_l1_upper": _fraction_record(coordinate_inverse),
        "synthesis_l1_upper": _fraction_record(synthesis),
        "eigen_residual_l1_upper": _fraction_record(residual),
        "representation_perturbation_gamma": _fraction_record(
            representation_perturbation
        ),
        "center_maximum_modulus_upper": _fraction_record(center_radius),
        "linear_external_contraction_upper": _fraction_record(
            linear_contraction
        ),
        "coordinate_certificate_passed": bool(
            finite_centers
            and digest_matches
            and proof.selected_count == 0
            and proof.excluded_count == 9
            and coordinate_defect < MAXIMUM_COORDINATE_DEFECT
        ),
    }
    return serializable, exact


def _selected_coordinate_certificates(
    q007o_payload: dict[str, Any],
    replayed_q007o: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Fraction | bool]], bool]:
    stored_records = q007o_payload["cycle"][
        "external_complement_inverse_refinement"
    ]["representative_records"]
    replayed_records = replayed_q007o[
        "external_complement_inverse_refinement"
    ]["representative_records"]
    replay_matches = replayed_records == stored_records
    records: list[dict[str, Any]] = []
    exact_records: list[dict[str, Fraction | bool]] = []
    for stored in stored_records:
        source_wave = tuple(stored["q007h1_source_wave_index"])
        kx = 2.0 * np.pi * source_wave[0] / SIZE
        ky = 2.0 * np.pi * source_wave[1] / SIZE
        center = filtered_fourier_symbol(kx, ky, OMEGA, ETA)
        eigenvalues, _eigenvectors = np.linalg.eig(center)
        external_indices = tuple(stored["external_indices_in_returned_order"])
        center_radius = max(
            _complex_center_modulus_upper(eigenvalues[index])
            for index in external_indices
        )
        perturbation = _fraction_from_record(
            stored["representation_perturbation_gamma"]
        )
        coordinate_inverse = _fraction_from_record(
            stored["coordinate_inverse_l1_upper"]
        )
        selector_projector = _fraction_from_record(
            stored["selector_projector_l1_upper"]
        )
        synthesis = _fraction_from_record(stored["external_basis_l1_upper"])
        analysis = coordinate_inverse * selector_projector
        selected_analysis = _fraction_from_record(
            stored["left_operator_l1_upper"]
        )
        linear_contraction = center_radius + perturbation
        wave = tuple(stored["wave_index"])
        orbit = next(orbit for orbit in _c4_orbits() if wave in orbit.members)
        exact_records.append(
            {
                "center_radius": center_radius,
                "representation_perturbation": perturbation,
                "linear_contraction": linear_contraction,
                "synthesis": synthesis,
                "analysis": analysis,
                "selected_analysis": selected_analysis,
                "certificate_passed": bool(
                    stored["coordinate_certificate_passed"] and replay_matches
                ),
            }
        )
        records.append(
            {
                "wave_index": list(wave),
                "q007h1_source_wave_index": list(source_wave),
                "orbit_members": [list(member) for member in orbit.members],
                "orbit_member_count": len(orbit.members),
                "coordinate_dimension": 6,
                "external_indices_in_returned_order": list(external_indices),
                "q007h1_proof_digest_sha256": stored[
                    "q007h1_proof_digest_sha256"
                ],
                "q007h1_proof_digest_matches": stored[
                    "q007h1_proof_digest_matches"
                ],
                "q007o_certificate_reproduced": replay_matches,
                "coordinate_defect_l1_upper": stored[
                    "coordinate_defect_l1_upper"
                ],
                "coordinate_inverse_l1_upper": stored[
                    "coordinate_inverse_l1_upper"
                ],
                "selector_projector_l1_upper": stored[
                    "selector_projector_l1_upper"
                ],
                "external_basis_l1_upper": stored[
                    "external_basis_l1_upper"
                ],
                "analysis_l1_upper": _fraction_record(analysis),
                "selected_analysis_l1_upper": stored[
                    "left_operator_l1_upper"
                ],
                "representation_perturbation_gamma": stored[
                    "representation_perturbation_gamma"
                ],
                "center_maximum_modulus_upper": _fraction_record(center_radius),
                "linear_external_contraction_upper": _fraction_record(
                    linear_contraction
                ),
                "coordinate_certificate_passed": bool(
                    stored["coordinate_certificate_passed"] and replay_matches
                ),
            }
        )
    return records, exact_records, replay_matches


def _maximum_with_witness(
    records: list[tuple[str, WaveIndex, Fraction]],
) -> tuple[Fraction, dict[str, Any]]:
    label, wave, value = max(records, key=lambda item: item[2])
    return value, {"block_type": label, "wave_index": list(wave)}


def _conversion_and_linear_bounds(
    nonselected_records: list[dict[str, Any]],
    nonselected_exact: list[dict[str, Fraction | bool]],
    selected_records: list[dict[str, Any]],
    selected_exact: list[dict[str, Fraction | bool]],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    linear_entries: list[tuple[str, WaveIndex, Fraction]] = [
        (
            "nonselected_full",
            tuple(record["wave_index"]),
            exact["linear_contraction"],
        )
        for record, exact in zip(
            nonselected_records, nonselected_exact, strict=True
        )
    ]
    synthesis_entries: list[tuple[str, WaveIndex, Fraction]] = [
        (
            "nonselected_full",
            tuple(record["wave_index"]),
            exact["synthesis"],
        )
        for record, exact in zip(
            nonselected_records, nonselected_exact, strict=True
        )
    ]
    analysis_entries: list[tuple[str, WaveIndex, Fraction]] = [
        (
            "nonselected_full",
            tuple(record["wave_index"]),
            exact["analysis"],
        )
        for record, exact in zip(
            nonselected_records, nonselected_exact, strict=True
        )
    ]
    selected_analysis_entries: list[tuple[str, WaveIndex, Fraction]] = []
    for record, exact in zip(selected_records, selected_exact, strict=True):
        wave = tuple(record["wave_index"])
        linear_entries.append(
            ("selected_external", wave, exact["linear_contraction"])
        )
        synthesis_entries.append(
            ("selected_external", wave, exact["synthesis"])
        )
        analysis_entries.append(
            ("selected_external", wave, exact["analysis"])
        )
        selected_analysis_entries.append(
            ("selected_left", wave, exact["selected_analysis"])
        )
    zero = Fraction(1, 2)
    linear_entries.append(("zero_wave_fixed_leaf", (0, 0), zero))
    synthesis_entries.append(("zero_wave_fixed_leaf", (0, 0), Fraction(1)))
    analysis_entries.append(("zero_wave_fixed_leaf", (0, 0), Fraction(1)))

    q0, q0_witness = _maximum_with_witness(linear_entries)
    synthesis, synthesis_witness = _maximum_with_witness(synthesis_entries)
    analysis, analysis_witness = _maximum_with_witness(analysis_entries)
    selected_analysis, selected_analysis_witness = _maximum_with_witness(
        selected_analysis_entries
    )
    exact = {
        "linear_external_contraction": q0,
        "synthesis": synthesis,
        "analysis": analysis,
        "selected_analysis": selected_analysis,
    }
    serializable = {
        "norm_definition": (
            "block-sum external-coordinate l1; physical population l1 at "
            "zero wave, Q007o six-coordinate norm at selected waves, and "
            "Q007h1 transported full eigencoordinates elsewhere"
        ),
        "linear_external_contraction_upper": _fraction_record(q0),
        "linear_external_contraction_witness": q0_witness,
        "synthesis_to_wiener_l1_upper": _fraction_record(synthesis),
        "synthesis_witness": synthesis_witness,
        "analysis_from_wiener_l1_upper": _fraction_record(analysis),
        "analysis_witness": analysis_witness,
        "selected_left_operator_l1_upper": _fraction_record(selected_analysis),
        "selected_left_witness": selected_analysis_witness,
        "registered_caps": {
            "synthesis": _fraction_record(MAXIMUM_SYNTHESIS_CONSTANT),
            "analysis": _fraction_record(MAXIMUM_ANALYSIS_CONSTANT),
            "selected_left": _fraction_record(
                MAXIMUM_SELECTED_ANALYSIS_CONSTANT
            ),
        },
    }
    return serializable, exact


def _exact_matrix_multiply(
    left: tuple[tuple[Fraction, ...], ...],
    right: tuple[tuple[Fraction, ...], ...],
) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(
        tuple(
            sum(
                (left[row][inner] * right[inner][column] for inner in range(len(right))),
                Fraction(0),
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def _zero_wave_structural_audit() -> dict[str, Any]:
    collision = rational_collision_symbol()
    moment = (
        tuple(Fraction(1) for _ in VELOCITIES),
        tuple(Fraction(cx) for cx, _cy in VELOCITIES),
        tuple(Fraction(cy) for _cx, cy in VELOCITIES),
    )
    lift = tuple(
        (
            weight,
            3 * weight * cx,
            3 * weight * cy,
        )
        for (cx, cy), weight in zip(VELOCITIES, WEIGHTS, strict=True)
    )
    projector = _exact_matrix_multiply(lift, moment)
    expected_collision = tuple(
        tuple(
            -Fraction(int(row == column), 2)
            + Fraction(3, 2) * projector[row][column]
            for column in range(9)
        )
        for row in range(9)
    )
    moment_projector = _exact_matrix_multiply(moment, projector)
    return {
        "collision_factorization_exact": collision == expected_collision,
        "moment_projector_identity_exact": moment_projector == moment,
        "fixed_leaf_action": "C z = -z/2 whenever M z = 0",
        "fixed_leaf_linear_contraction": _fraction_record(Fraction(1, 2)),
        "passed": bool(
            collision == expected_collision and moment_projector == moment
        ),
    }


def _polynomial_value(
    coefficients: dict[str, Fraction], prefix: str, value: Fraction
) -> Fraction:
    return sum(
        (coefficients[f"{prefix}{degree}"] * value**degree for degree in (2, 3, 4)),
        Fraction(0),
    )


def _polynomial_derivative(
    coefficients: dict[str, Fraction], prefix: str, value: Fraction
) -> Fraction:
    return sum(
        (
            degree * coefficients[f"{prefix}{degree}"] * value ** (degree - 1)
            for degree in (2, 3, 4)
        ),
        Fraction(0),
    )


def _nonlinear_derivative(value: Fraction) -> Fraction:
    return (
        NONLINEAR_MAJORANT_CONSTANT
        * value
        * (2 - value)
        / (1 - value) ** 2
    )


def _finite_tube_majorant(
    q007h1_payload: dict[str, Any],
    q007n_payload: dict[str, Any],
    q007o_payload: dict[str, Any],
    conversion: dict[str, Fraction],
) -> tuple[dict[str, Any], dict[str, Fraction | bool]]:
    q007n_cycle = q007n_payload["cycle"]
    coefficients = _working_coefficients_from_q007n(q007n_cycle)
    spectral = q007n_cycle["spectral_separation_and_inverse"]
    selected_radius = _fraction_from_record(
        spectral["working_selected_spectral_radius_upper"]
    )
    selected_minimum = _fraction_from_record(
        q007h1_payload["cycle"]["global_bounds"]["selected_minimum_modulus"]
    )
    boundary = q007o_payload["cycle"]["radius_comparison"][
        "refined_radius_search"
    ]["exact_boundary_certificate"]["selected"]
    analytic_radius = _fraction_from_record(boundary["radius"])
    correction_radius = _fraction_from_record(boundary["correction_radius"])

    r = BASE_RADIUS
    zeta = NORMAL_RADIUS
    chart_value = (
        coefficients["c_v"] * r
        + _polynomial_value(coefficients, "h", r)
        + correction_radius
    )
    reduced_value = (
        selected_radius * r
        + _polynomial_value(coefficients, "g", r)
        + correction_radius / coefficients["c_v"]
    )
    state_radius = chart_value + conversion["synthesis"] * zeta
    nonlinear_derivative_at_state = _nonlinear_derivative(state_radius)
    base_image_radius = (
        reduced_value
        + conversion["selected_analysis"]
        * nonlinear_derivative_at_state
        * conversion["synthesis"]
        * zeta
    )
    chart_derivative = (
        _polynomial_derivative(coefficients, "h", base_image_radius)
        + correction_radius / (analytic_radius - base_image_radius)
    )
    reduced_derivative = (
        _polynomial_derivative(coefficients, "g", r)
        + correction_radius
        / (coefficients["c_v"] * (analytic_radius - r))
    )
    normal_contraction = (
        conversion["linear_external_contraction"]
        + conversion["analysis"]
        * conversion["synthesis"]
        * nonlinear_derivative_at_state
        * (1 + conversion["selected_analysis"] * chart_derivative)
    )
    tangent_conorm = selected_minimum - reduced_derivative
    domination_ratio = normal_contraction / tangent_conorm

    exact: dict[str, Fraction | bool] = {
        "c_v": coefficients["c_v"],
        "selected_radius": selected_radius,
        "selected_minimum": selected_minimum,
        "analytic_radius": analytic_radius,
        "correction_radius": correction_radius,
        "chart_value": chart_value,
        "reduced_value": reduced_value,
        "state_radius": state_radius,
        "nonlinear_derivative_at_state": nonlinear_derivative_at_state,
        "base_image_radius": base_image_radius,
        "chart_derivative": chart_derivative,
        "reduced_derivative": reduced_derivative,
        "normal_contraction": normal_contraction,
        "tangent_conorm": tangent_conorm,
        "domination_ratio": domination_ratio,
        "analytic_radius_reproduced": analytic_radius == ANALYTIC_RADIUS,
    }
    coefficient_records = {
        name: _fraction_record(value) for name, value in coefficients.items()
    }
    serializable = {
        "arithmetic": "exact fractions.Fraction",
        "base_modal_l1_radius": _fraction_record(r),
        "normal_coordinate_radius": _fraction_record(zeta),
        "analytic_chart_radius": _fraction_record(analytic_radius),
        "correction_pair_radius_tau": _fraction_record(correction_radius),
        "working_coefficients_reused_from_q007n": coefficient_records,
        "selected_spectral_radius_upper": _fraction_record(selected_radius),
        "selected_minimum_modulus_lower": _fraction_record(selected_minimum),
        "nonlinear_derivative_majorant_constant": _fraction_record(
            NONLINEAR_MAJORANT_CONSTANT
        ),
        "chart_radius_at_base_upper": _fraction_record(chart_value),
        "reduced_radius_at_base_upper": _fraction_record(reduced_value),
        "tube_state_wiener_l1_upper": _fraction_record(state_radius),
        "nonlinear_derivative_at_tube_state_upper": _fraction_record(
            nonlinear_derivative_at_state
        ),
        "base_image_modal_l1_upper": _fraction_record(base_image_radius),
        "chart_derivative_at_base_image_upper": _fraction_record(
            chart_derivative
        ),
        "reduced_derivative_at_base_upper": _fraction_record(
            reduced_derivative
        ),
        "normal_fiber_contraction_upper": _fraction_record(normal_contraction),
        "tangent_conorm_lower": _fraction_record(tangent_conorm),
        "normal_domination_ratio_upper": _fraction_record(domination_ratio),
        "strict_margins": {
            "density": _fraction_record(1 - state_radius),
            "analytic_base": _fraction_record(analytic_radius - r),
            "base_forward_invariance": _fraction_record(r - base_image_radius),
            "normal_contraction_to_registered_cap": _fraction_record(
                MAXIMUM_NORMAL_CONTRACTION - normal_contraction
            ),
            "normal_tube_forward_invariance": _fraction_record(
                zeta - normal_contraction * zeta
            ),
            "tangent_invertibility": _fraction_record(tangent_conorm),
            "domination_to_registered_cap": _fraction_record(
                MAXIMUM_DOMINATION_RATIO - domination_ratio
            ),
            "domination_to_one": _fraction_record(1 - domination_ratio),
        },
        "formulae": {
            "state_radius": "w(r) + K_s*zeta",
            "base_image_radius": "r_R(r) + K_L*dN(state_radius)*K_s*zeta",
            "normal_contraction": (
                "q0 + K_a*K_s*dN(state_radius)*(1 + K_L*dH(base_image_radius))"
            ),
            "tangent_conorm": "selected_minimum - dG(r)",
            "domination_ratio": "normal_contraction / tangent_conorm",
        },
    }
    return serializable, exact


def run_finite_tube_attraction_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    replayed_q007o = run_external_complement_radius_audit(directory)

    trigonometric = trigonometric_intervals(machin_pi_interval())
    collision = rational_collision_symbol()
    q007h1_records = {
        tuple(record["wave_index"]): record
        for record in payloads["q007h1"]["cycle"]["eigencertification"][
            "block_records"
        ]
    }
    nonselected_orbits = tuple(
        orbit
        for orbit in _c4_orbits()
        if orbit.representative != (0, 0)
        and orbit.representative not in SELECTED_WAVES
    )
    nonselected_records: list[dict[str, Any]] = []
    nonselected_exact: list[dict[str, Fraction | bool]] = []
    for orbit in nonselected_orbits:
        wave = orbit.representative
        record, exact = _nonselected_coordinate_certificate(
            wave,
            rational_fourier_symbol(wave, trigonometric, collision),
            q007h1_records[wave],
        )
        nonselected_records.append(record)
        nonselected_exact.append(exact)

    selected_records, selected_exact, selected_replay_matches = (
        _selected_coordinate_certificates(
            payloads["q007o"], replayed_q007o
        )
    )
    conversion_section, conversion_exact = _conversion_and_linear_bounds(
        nonselected_records,
        nonselected_exact,
        selected_records,
        selected_exact,
    )
    majorant_section, majorant_exact = _finite_tube_majorant(
        payloads["q007h1"],
        payloads["q007n"],
        payloads["q007o"],
        conversion_exact,
    )

    q007h1_cycle = payloads["q007h1"]["cycle"]
    q007n_structural = payloads["q007n"]["cycle"][
        "structural_majorant_audit"
    ]
    q007o_refinement = payloads["q007o"]["cycle"][
        "external_complement_inverse_refinement"
    ]
    zero_audit = _zero_wave_structural_audit()
    orbit_member_count = sum(
        record["orbit_member_count"] for record in nonselected_records
    ) + sum(record["orbit_member_count"] for record in selected_records)
    total_wave_count = orbit_member_count + 1
    external_dimension = (
        sum(
            record["orbit_member_count"] * record["coordinate_dimension"]
            for record in nonselected_records
        )
        + sum(
            record["orbit_member_count"] * record["coordinate_dimension"]
            for record in selected_records
        )
        + 6
    )
    coordinate_section = {
        "nonselected_representative_count": len(nonselected_records),
        "selected_representative_count": len(selected_records),
        "zero_wave_block_count": 1,
        "represented_wave_count_formula": "70*4 + 2*4 + 1",
        "represented_wave_count": total_wave_count,
        "external_complex_dimension_formula": "70*4*9 + 2*4*6 + 6",
        "external_complex_dimension": external_dimension,
        "nonselected_representative_records": nonselected_records,
        "selected_representative_records": selected_records,
        "zero_wave_record": {
            "wave_index": [0, 0],
            "coordinate_dimension": 6,
            "norm": "physical complex population l1 on ker(M)",
            "linear_external_contraction_upper": _fraction_record(
                Fraction(1, 2)
            ),
            "synthesis_l1_upper": _fraction_record(Fraction(1)),
            "analysis_l1_upper": _fraction_record(Fraction(1)),
        },
        "q007o_selected_certificates_reproduced_exactly": (
            selected_replay_matches
        ),
    }

    coefficient_reuse_passed = bool(
        majorant_exact["analytic_radius_reproduced"]
        and _fraction_from_record(
            q007n_structural["nonlinear_majorant_constant"]
        )
        == NONLINEAR_MAJORANT_CONSTANT
        and _fraction_from_record(
            payloads["q007o"]["cycle"]["radius_comparison"][
                "refined_radius_search"
            ]["exact_boundary_certificate"]["selected"]["radius"]
        )
        == ANALYTIC_RADIUS
    )
    majorant_reuse = {
        "q007n_structural_majorant_passed": q007n_structural["passed"],
        "q007n_nonlinear_constant_matches": (
            _fraction_from_record(
                q007n_structural["nonlinear_majorant_constant"]
            )
            == NONLINEAR_MAJORANT_CONSTANT
        ),
        "q007o_analytic_radius_matches": majorant_exact[
            "analytic_radius_reproduced"
        ],
        "q007o_selected_boundary_passed": payloads["q007o"]["cycle"][
            "radius_comparison"
        ]["refined_radius_search"]["exact_boundary_certificate"]["selected"][
            "passed"
        ],
        "coefficient_and_radius_reuse_passed": coefficient_reuse_passed,
    }

    permutation_invariant = bool(
        sorted(QUARTER_TURN_MAPPING) == list(range(9))
        and all(record["orbit_member_count"] == 4 for record in nonselected_records)
        and all(record["orbit_member_count"] == 4 for record in selected_records)
    )
    linear_splitting_identity = bool(
        q007o_refinement["selected_projector_identity"]
        == "P=V L*, Q=I-P, L*V=I, and AQ=QA exactly"
        and selected_replay_matches
    )
    structural_section = {
        "zero_wave": zero_audit,
        "external_linear_splitting": {
            "upstream_identity": q007o_refinement[
                "selected_projector_identity"
            ],
            "deduction": "L A Q = L Q A = 0",
            "passed": linear_splitting_identity,
        },
        "c4_norm_invariance": {
            "quarter_turn_mapping": list(QUARTER_TURN_MAPPING),
            "population_mapping_is_permutation": sorted(
                QUARTER_TURN_MAPPING
            )
            == list(range(9)),
            "q007h1_exact_symbol_covariance": q007h1_cycle[
                "symbol_covariance"
            ]["entrywise_exact"],
            "all_nonzero_orbits_have_four_members": permutation_invariant,
            "deduction": (
                "row/column population permutations preserve induced and "
                "vector complex l1 norms"
            ),
            "passed": bool(
                permutation_invariant
                and q007h1_cycle["symbol_covariance"]["entrywise_exact"]
            ),
        },
        "real_state_constraint": (
            "Fourier conjugate blocks are paired; the certified complex l1 "
            "bounds restrict unchanged to the real conjugacy subspace"
        ),
    }

    reconstruction_passed = bool(
        len(nonselected_records) == NONSELECTED_REPRESENTATIVE_COUNT
        and len(selected_records) == SELECTED_REPRESENTATIVE_COUNT
        and all(
            record["q007h1_proof_digest_matches"]
            for record in nonselected_records
        )
        and total_wave_count == TOTAL_WAVE_COUNT
        and external_dimension == EXTERNAL_COMPLEX_DIMENSION
    )
    coordinate_certificates_passed = bool(
        all(
            record["coordinate_certificate_passed"]
            for record in nonselected_records
        )
        and all(
            record["coordinate_certificate_passed"]
            for record in selected_records
        )
        and selected_replay_matches
    )
    conversion_caps_passed = bool(
        conversion_exact["synthesis"] <= MAXIMUM_SYNTHESIS_CONSTANT
        and conversion_exact["analysis"] <= MAXIMUM_ANALYSIS_CONSTANT
        and conversion_exact["selected_analysis"]
        <= MAXIMUM_SELECTED_ANALYSIS_CONSTANT
        and all(value > 0 for value in conversion_exact.values())
    )
    serializable_sections = {
        "input_artifacts": input_records,
        "external_coordinate_certification": coordinate_section,
        "global_conversion_and_linear_bounds": conversion_section,
        "majorant_reuse_audit": majorant_reuse,
        "finite_tube_majorant": majorant_section,
        "structural_audit": structural_section,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    structural_passed = bool(
        zero_audit["passed"]
        and linear_splitting_identity
        and structural_section["c4_norm_invariance"]["passed"]
        and finite_strict_json
    )

    validity_gates = {
        "registered_inputs": {
            "passed": all(record["passed"] for record in input_records.values()),
            "threshold": (
                "three artifact hashes/source/scope/gates and registered "
                "Q007n/Q007o runner hashes match"
            ),
            "value": {
                name: record["passed"] for name, record in input_records.items()
            },
        },
        "representative_reconstruction": {
            "passed": reconstruction_passed,
            "threshold": (
                "70 nonselected proof digests, two selected orbits, 289 "
                "waves, and external dimension 2574 reproduce"
            ),
            "value": {
                "nonselected_representatives": len(nonselected_records),
                "proof_digest_mismatch_count": sum(
                    not record["q007h1_proof_digest_matches"]
                    for record in nonselected_records
                ),
                "selected_representatives": len(selected_records),
                "represented_waves": total_wave_count,
                "external_complex_dimension": external_dimension,
            },
        },
        "external_coordinate_certificates": {
            "passed": coordinate_certificates_passed,
            "threshold": (
                "all 70 full-coordinate defects <1e-8 and both Q007o "
                "selected certificates reproduce exactly"
            ),
            "value": {
                "maximum_nonselected_defect": max(
                    record["coordinate_defect_l1_upper"]["float"]
                    for record in nonselected_records
                ),
                "selected_q007o_replay": selected_replay_matches,
            },
        },
        "registered_conversion_caps": {
            "passed": conversion_caps_passed,
            "threshold": "K_s<=4, K_a<=40, K_L<=2 and all are positive",
            "value": {
                "K_s": float(conversion_exact["synthesis"]),
                "K_a": float(conversion_exact["analysis"]),
                "K_L": float(conversion_exact["selected_analysis"]),
            },
        },
        "registered_majorants_reused": {
            "passed": bool(
                coefficient_reuse_passed and q007n_structural["passed"]
            ),
            "threshold": (
                "Q007n working coefficients and 21/2 constant plus Q007o "
                "rho/tau are reused exactly"
            ),
            "value": majorant_reuse,
        },
        "fixed_leaf_splitting_c4_and_json": {
            "passed": structural_passed,
            "threshold": (
                "zero-wave fixed-leaf action, L A Q=0, C4 norm invariance, "
                "finite values, and strict JSON pass"
            ),
            "value": {
                "zero_wave": zero_audit["passed"],
                "linear_splitting": linear_splitting_identity,
                "c4_norm_invariance": structural_section[
                    "c4_norm_invariance"
                ]["passed"],
                "finite_strict_json": finite_strict_json,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    state_radius = majorant_exact["state_radius"]
    base_image_radius = majorant_exact["base_image_radius"]
    normal_contraction = majorant_exact["normal_contraction"]
    tangent_conorm = majorant_exact["tangent_conorm"]
    domination_ratio = majorant_exact["domination_ratio"]
    assert isinstance(state_radius, Fraction)
    assert isinstance(base_image_radius, Fraction)
    assert isinstance(normal_contraction, Fraction)
    assert isinstance(tangent_conorm, Fraction)
    assert isinstance(domination_ratio, Fraction)
    hypothesis_gates = {
        "density_and_analytic_domain": {
            "passed": bool(
                state_radius < 1
                and base_image_radius < BASE_RADIUS < ANALYTIC_RADIUS
            ),
            "threshold": "x_*<1 and a_*<r<rho",
            "value": {
                "x_star": float(state_radius),
                "a_star": float(base_image_radius),
                "r": float(BASE_RADIUS),
                "rho": float(ANALYTIC_RADIUS),
            },
        },
        "base_forward_invariance": {
            "passed": base_image_radius < BASE_RADIUS,
            "threshold": "a_*<r strictly",
            "value": {
                "a_star": float(base_image_radius),
                "margin": float(BASE_RADIUS - base_image_radius),
            },
        },
        "normal_fiber_contraction": {
            "passed": bool(
                normal_contraction < MAXIMUM_NORMAL_CONTRACTION
                and normal_contraction * NORMAL_RADIUS < NORMAL_RADIUS
            ),
            "threshold": "q_*<0.99 and q_* zeta<zeta",
            "value": {
                "q_star": float(normal_contraction),
                "tube_margin": float(
                    NORMAL_RADIUS - normal_contraction * NORMAL_RADIUS
                ),
            },
        },
        "tangent_invertibility_and_normal_domination": {
            "passed": bool(
                tangent_conorm > 0
                and domination_ratio < MAXIMUM_DOMINATION_RATIO
            ),
            "threshold": "m_T>0 and Gamma_*=q_*/m_T<0.999",
            "value": {
                "m_T": float(tangent_conorm),
                "Gamma_star": float(domination_ratio),
                "margin": float(MAXIMUM_DOMINATION_RATIO - domination_ratio),
            },
        },
    }
    hypotheses_passed = validity_passed and all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered finite-tube attraction audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered fixed-leaf tube is uniformly normally attracting "
            "in the external-coordinate norm"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered finite tube did not certify uniform normal attraction"
        )

    return {
        "question": (
            "Is the registered finite tube around the exact Q007o manifold "
            "forward invariant, fiber-contracting, and normally dominated?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "analytic_radius": _fraction_record(ANALYTIC_RADIUS),
            "base_radius": _fraction_record(BASE_RADIUS),
            "normal_radius": _fraction_record(NORMAL_RADIUS),
            "maximum_coordinate_defect": _fraction_record(
                MAXIMUM_COORDINATE_DEFECT
            ),
            "maximum_synthesis_constant": _fraction_record(
                MAXIMUM_SYNTHESIS_CONSTANT
            ),
            "maximum_analysis_constant": _fraction_record(
                MAXIMUM_ANALYSIS_CONSTANT
            ),
            "maximum_selected_analysis_constant": _fraction_record(
                MAXIMUM_SELECTED_ANALYSIS_CONSTANT
            ),
            "maximum_normal_contraction": _fraction_record(
                MAXIMUM_NORMAL_CONTRACTION
            ),
            "maximum_domination_ratio": _fraction_record(
                MAXIMUM_DOMINATION_RATIO
            ),
        },
        "input_artifacts": input_records,
        "external_coordinate_certification": coordinate_section,
        "global_conversion_and_linear_bounds": conversion_section,
        "majorant_reuse_audit": majorant_reuse,
        "finite_tube_majorant": majorant_section,
        "structural_audit": structural_section,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "registered_tube_forward_invariant": hypotheses_passed,
            "uniform_one_step_normal_fiber_contraction": hypotheses_passed,
            "strict_normal_domination": hypotheses_passed,
            "identified_with_q007o_exact_manifold": hypotheses_passed,
        },
        "claim_boundary": (
            "This certifies only the registered r=1e-19, zeta=1e-20 tube "
            "for the exact manifold of the fixed 17x17 filtered map on one "
            "conservation leaf, in the registered Fourier external-coordinate "
            "block-sum l1 norm. It is not a Euclidean contraction result and "
            "does not alter Q007d's Euclidean rejection or Q007c1's finite-"
            "amplitude rejection. It does not certify positivity, a larger "
            "tube, a global basin, grid-uniform attraction, or a continuum "
            "limit."
        ),
        "preserved_prior_outcomes": {
            "q007o_explicit_radius_acceptance_changed": False,
            "q007d_euclidean_rejection_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, seal the theorem package and move to the next "
            "registered unresolved research gate without enlarging this tube."
        ),
    }


def run_q007p_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_finite_tube_attraction_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational finite-tube normal-attraction certificate",
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": SELECTED_COMPLEX_DIMENSION,
            "external_complex_dimension": EXTERNAL_COMPLEX_DIMENSION,
            "base_modal_l1_radius": float(BASE_RADIUS),
            "normal_coordinate_radius": float(NORMAL_RADIUS),
            "claim": (
                "registered finite-tube forward invariance and normal "
                "attraction in one fixed external-coordinate norm only; no "
                "Euclidean, positivity, larger-tube, basin, grid-uniform, or "
                "continuum claim"
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
    result = run_q007p_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
