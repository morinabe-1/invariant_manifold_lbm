"""Sealed Q007n rational explicit-local-radius certification.

The registered quartic graph-gauge jet is used as the center of a Banach
contraction in a modal-Wiener majorant space.  Every acceptance inequality is
evaluated with exact ``fractions.Fraction`` arithmetic.
"""

from __future__ import annotations

import argparse
import json
import math
from collections.abc import Iterable, Sequence
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from ttim_lbm.checkerboard_filter import filtered_fourier_symbol
from ttim_lbm.full2d_chart import _complex_coefficients
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.quartic_chart import build_full2d_quartic_model
from ttim_lbm.rational_spectrum import (
    VELOCITIES,
    WEIGHTS,
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _sqrt_bounds,
    _strict_json_serializable,
    rational_collision_symbol,
)

SIZE = 17
OMEGA = Fraction(3, 2)
ETA = Fraction(1, 100)
SELECTED_COMPLEX_DIMENSION = 24
TAIL_DEGREE = 90
CANDIDATE_EXPONENTS = tuple(range(2, 121))
MAXIMUM_CONTRACTION = Fraction(1, 2)
AUGMENTED_DIMENSION = 12
AUGMENTED_EXTERNAL_DIMENSION = 6
AUGMENTED_ENTRY_BOUND = Fraction(2)
NONLINEAR_MAJORANT_CONSTANT = Fraction(21, 2)
MAJORANT_DECIMAL_DIGITS = 80

ARTIFACT_FILENAMES = {
    "q007h1": "q007h1_equivariant_spectrum.json",
    "q007i": "q007i_direct_nonresonance.json",
    "q007j": "q007j_eigencoordinate_bridge.json",
    "q007k": "q007k_quadratic_jet_bridge.json",
    "q007l": "q007l_cubic_jet_bridge.json",
    "q007m": "q007m_quartic_jet_bridge.json",
}
REGISTERED_INPUT_SHA256 = {
    "q007h1": "caee8fe382c0282e11e8139b8f434a944013f630288adf2e99223d0123c91af4",
    "q007i": "c256b30ac5bfe0a6bc5e5f8e293016d3e0aa37c4bfa82ba81a0a2679d89e082f",
    "q007j": "feae846b81dc0991aa2c9babbd38ee72eb9ae493526655435cf0bf5951c7ec44",
    "q007k": "022f9ded6b40dc754a1b935f69554db9407e5e07715bd9132990ca9876fc8bbf",
    "q007l": "aa0e572b43ed4f5544e2b8ead9d01c13bc08c47f40ec8963bcd37a1b51fc1bbd",
    "q007m": "19090371bb7f8be1f59e47502f303f1c3eea18d3ccb365972363d377a214364b",
}
REGISTERED_RUNNER_SHA256 = {
    "q007j": "7ef97e55ffff46244fee98d8017db1637a0e6c73ba3f1caf5c7dad77b7a26b57",
    "q007k": "963862710b772a63a9293bbb100ea50a21f3469932ee54d84cfd197a384f89cb",
    "q007l": "bb2be852c5413ceb2d27abd4f48db36ed2045ed79f2330e45ae89818067d33a4",
    "q007m": "d086f2cc27684521c13daf7d2594cd21e5c0ad92f3953cca884c57d06986a918",
}
REGISTERED_COEFFICIENT_HASHES = {
    "quartet_indices_sha256": (
        "968b35d36cbd28c1f30e6cacb906649a42b36ba4e7bf4122394c2722cd809c16"
    ),
    "output_waves_sha256": (
        "9f9720e1114cc489ef7bbca81562e7d4cf211999e8d4a4958c06c02ee0df1fe8"
    ),
    "chart_coefficients_sha256": (
        "9597e0d31c32c940c76526754f0ec70c666e5fe03511977e80b3fd0610a7f29b"
    ),
    "reduced_coefficients_sha256": (
        "061cd66caf83850a45eeec05ed0f62fafb748a3076d7a6eb591bc69be2e008f7"
    ),
    "forcing_coefficients_sha256": (
        "6ab2337ea60b87dbe404e1aeb6b9c090fa8f950d43815966e0933879901b8eef"
    ),
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


def _round_down(value: Fraction, digits: int = MAJORANT_DECIMAL_DIGITS) -> Fraction:
    scale = 10**digits
    return Fraction(value.numerator * scale // value.denominator, scale)


def _round_up(value: Fraction, digits: int = MAJORANT_DECIMAL_DIGITS) -> Fraction:
    scale = 10**digits
    numerator = -((-value.numerator * scale) // value.denominator)
    return Fraction(numerator, scale)


def _all_gates_pass(cycle: dict[str, Any], key: str) -> bool:
    gates = cycle.get(key, {})
    return bool(gates) and all(gate.get("passed", False) for gate in gates.values())


def _load_registered_inputs(
    artifact_directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads: dict[str, dict[str, Any]] = {}
    records: dict[str, dict[str, Any]] = {}
    runner_directory = Path(__file__).resolve().parent
    for name, filename in ARTIFACT_FILENAMES.items():
        path = artifact_directory / filename
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads[name] = payload
        cycle = payload.get("cycle", {})
        scope = payload.get("mathematical_scope", {})
        observed_sha256 = _file_sha256(path)
        runner_registered = REGISTERED_RUNNER_SHA256.get(name)
        runner_path = runner_directory / filename.replace(".json", ".py")
        observed_runner_sha256 = (
            _file_sha256(runner_path) if runner_registered is not None else None
        )
        artifact_runner_sha256 = payload.get("runner_source", {}).get("sha256")
        runner_matches = bool(
            runner_registered is None
            or (
                observed_runner_sha256 == runner_registered
                and artifact_runner_sha256 == runner_registered
            )
        )
        scope_matches = bool(
            scope.get("construction_grid") == [SIZE, SIZE]
            and float(scope.get("omega", math.nan)) == float(OMEGA)
            and float(scope.get("eta", math.nan)) == float(ETA)
        )
        gates_pass = bool(
            _all_gates_pass(cycle, "validity_gates")
            and _all_gates_pass(cycle, "hypothesis_gates")
        )
        theorem_match = bool(
            name != "q007i"
            or cycle.get("theorem_consequence", {}).get("theorem_applies", False)
        )
        record = {
            "filename": filename,
            "sha256": observed_sha256,
            "registered_sha256": REGISTERED_INPUT_SHA256[name],
            "sha256_matches": observed_sha256 == REGISTERED_INPUT_SHA256[name],
            "sha256_newline_normalization": "UTF-8 text with universal newlines",
            "source_match": payload.get("source") == source_metadata(),
            "scope_match": scope_matches,
            "schema_version": payload.get("schema_version"),
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "all_validity_and_hypothesis_gates_passed": gates_pass,
            "theorem_match": theorem_match,
            "registered_runner_sha256": runner_registered,
            "artifact_runner_sha256": artifact_runner_sha256,
            "observed_runner_sha256": observed_runner_sha256,
            "runner_sha_matches": runner_matches,
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["source_match"]
            and record["scope_match"]
            and record["schema_version"] == 1
            and record["study_gate"] == "passed"
            and record["scientific_outcome"] == "accepted"
            and gates_pass
            and theorem_match
            and runner_matches
        )
        records[name] = record
    return payloads, records


def _dyadic_absolute_one(value: complex) -> Fraction:
    point = complex(value)
    return abs(Fraction.from_float(point.real)) + abs(
        Fraction.from_float(point.imag)
    )


def _center_vector_l1(value: Sequence[complex]) -> Fraction:
    return sum((_dyadic_absolute_one(entry) for entry in value), Fraction(0))


def _maximum_center_vector_l1(
    rows: Iterable[Sequence[complex]],
) -> tuple[Fraction, int]:
    array = np.asarray(tuple(rows) if not isinstance(rows, np.ndarray) else rows)
    if array.ndim != 2 or array.shape[0] == 0:
        raise ValueError("coefficient collection is empty")
    observed = np.sum(
        np.abs(array.real) + np.abs(array.imag),
        axis=1,
        dtype=np.float64,
    )
    witness = int(np.argmax(observed))
    unit_roundoff = Fraction(1, 2**53)
    operation_allowance = 4 * int(array.shape[1])
    gamma = (
        operation_allowance
        * unit_roundoff
        / (1 - operation_allowance * unit_roundoff)
    )
    maximum_upper = Fraction.from_float(float(observed[witness])) / (1 - gamma)
    return maximum_upper, witness


def _coefficient_majorants(
    payloads: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Fraction], Any]:
    model = build_full2d_quartic_model()
    modes = list(model.modes)
    hessian, reduced_hessian, _, _ = _complex_coefficients(
        modes,
        model.lookup,
        model.size,
        model.cubic.quadratic.omega,
        model.cubic.quadratic.eta,
    )
    observed_hashes = model.coefficient_hashes()
    q007m_hashes = payloads["q007m"]["cycle"]["coefficient_reproduction"]

    correction_records: dict[int, tuple[Fraction, Fraction]] = {}
    for degree, name in ((2, "q007k"), (3, "q007l"), (4, "q007m")):
        certification = payloads[name]["cycle"]["krawczyk_certification"]
        correction_records[degree] = (
            _fraction_from_record(
                certification["maximum_hessian_correction_upper"]
            ),
            _fraction_from_record(
                certification["maximum_reduced_correction_upper"]
            ),
        )

    h2_rows = hessian.reshape(-1, 9)
    g2_rows = np.moveaxis(reduced_hessian, 0, -1).reshape(-1, 24)
    h3_rows = model.cubic.cubic_coefficients.reshape(-1, 9)
    g3_rows = model.cubic.reduced_cubic_coefficients.reshape(-1, 24)
    h4_rows = model.quartic_coefficients.reshape(-1, 9)
    g4_rows = model.reduced_quartic_coefficients.reshape(-1, 24)
    row_sets = {
        2: (h2_rows, g2_rows),
        3: (h3_rows, g3_rows),
        4: (h4_rows, g4_rows),
    }

    exact: dict[str, Fraction] = {}
    degree_records = []
    for degree, (chart_rows, reduced_rows) in row_sets.items():
        chart_center, chart_witness = _maximum_center_vector_l1(chart_rows)
        reduced_center, reduced_witness = _maximum_center_vector_l1(reduced_rows)
        chart_correction, reduced_correction = correction_records[degree]
        factorial = math.factorial(degree)
        chart_norm = (
            chart_center + len(chart_rows[0]) * chart_correction
        ) / factorial
        reduced_norm = (
            reduced_center + len(reduced_rows[0]) * reduced_correction
        ) / factorial
        chart_box_norm = len(chart_rows[0]) * chart_correction / factorial
        reduced_box_norm = (
            len(reduced_rows[0]) * reduced_correction / factorial
        )
        exact[f"h{degree}"] = chart_norm
        exact[f"g{degree}"] = reduced_norm
        exact[f"h{degree}_box"] = chart_box_norm
        exact[f"g{degree}_box"] = reduced_box_norm
        degree_records.append(
            {
                "degree": degree,
                "factorial_normalization": factorial,
                "chart_output_dimension": len(chart_rows[0]),
                "reduced_output_dimension": len(reduced_rows[0]),
                "chart_center_l1_upper": _fraction_record(chart_center),
                "reduced_center_l1_upper": _fraction_record(reduced_center),
                "chart_component_correction_upper": _fraction_record(
                    chart_correction
                ),
                "reduced_component_correction_upper": _fraction_record(
                    reduced_correction
                ),
                "chart_operator_norm_upper": _fraction_record(chart_norm),
                "reduced_operator_norm_upper": _fraction_record(reduced_norm),
                "chart_box_operator_norm_upper": _fraction_record(
                    chart_box_norm
                ),
                "reduced_box_operator_norm_upper": _fraction_record(
                    reduced_box_norm
                ),
                "chart_center_witness_flat_index": chart_witness,
                "reduced_center_witness_flat_index": reduced_witness,
            }
        )

    q007j_transport = payloads["q007j"]["cycle"][
        "transport_and_normalization"
    ]
    right_correction = _fraction_from_record(
        q007j_transport["maximum_right_correction_upper"]
    )
    left_correction = _fraction_from_record(
        q007j_transport["maximum_biorthogonal_left_correction_upper"]
    )
    tangent_norm = max(
        _center_vector_l1(mode.right) + 9 * right_correction for mode in modes
    )
    right_entry_bound = max(
        _dyadic_absolute_one(entry) + right_correction
        for mode in modes
        for entry in mode.right
    )
    left_entry_bound = max(
        _dyadic_absolute_one(entry) + left_correction
        for mode in modes
        for entry in mode.left
    )
    exact["c_v"] = tangent_norm
    exact["right_entry"] = right_entry_bound
    exact["left_entry"] = left_entry_bound

    working = {name: _round_up(value) for name, value in exact.items()}
    for record in degree_records:
        degree = record["degree"]
        record["working_chart_operator_norm_upper"] = _fraction_record(
            working[f"h{degree}"]
        )
        record["working_reduced_operator_norm_upper"] = _fraction_record(
            working[f"g{degree}"]
        )
        record["working_chart_box_operator_norm_upper"] = _fraction_record(
            working[f"h{degree}_box"]
        )
        record["working_reduced_box_operator_norm_upper"] = _fraction_record(
            working[f"g{degree}_box"]
        )

    all_coefficients_finite = bool(
        np.all(np.isfinite(hessian))
        and np.all(np.isfinite(reduced_hessian))
        and np.all(np.isfinite(model.cubic.cubic_coefficients))
        and np.all(np.isfinite(model.cubic.reduced_cubic_coefficients))
        and np.all(np.isfinite(model.quartic_coefficients))
        and np.all(np.isfinite(model.reduced_quartic_coefficients))
    )
    reproduction = {
        "registered": REGISTERED_COEFFICIENT_HASHES,
        "q007m_registered": q007m_hashes["registered"],
        "q007m_artifact": q007m_hashes["artifact"],
        "q007m_observed": q007m_hashes["observed"],
        "observed": observed_hashes,
        "matches": bool(
            observed_hashes == REGISTERED_COEFFICIENT_HASHES
            and q007m_hashes["registered"] == REGISTERED_COEFFICIENT_HASHES
            and q007m_hashes["artifact"] == REGISTERED_COEFFICIENT_HASHES
            and q007m_hashes["observed"] == REGISTERED_COEFFICIENT_HASHES
        ),
        "all_coefficients_finite": all_coefficients_finite,
        "complex_absolute_majorant": (
            "nonnegative abs(real)+abs(imag) row sum with rational IEEE-754 "
            "gamma_(4*output_dimension) outward correction"
        ),
        "majorant_outward_decimal_grid_digits": MAJORANT_DECIMAL_DIGITS,
        "tangent_l1_operator_norm_upper": _fraction_record(tangent_norm),
        "working_tangent_l1_operator_norm_upper": _fraction_record(
            working["c_v"]
        ),
        "right_component_absolute_upper": _fraction_record(right_entry_bound),
        "left_component_absolute_upper": _fraction_record(left_entry_bound),
        "right_component_correction_upper": _fraction_record(right_correction),
        "left_component_correction_upper": _fraction_record(left_correction),
        "degree_records": degree_records,
    }
    return reproduction, working, model


def _spectral_and_inverse_majorants(
    payloads: dict[str, dict[str, Any]],
    exact_coefficients: dict[str, Fraction],
) -> tuple[dict[str, Any], dict[str, Fraction]]:
    q007h1 = payloads["q007h1"]
    global_bounds = q007h1["cycle"]["global_bounds"]
    selected_minimum = _fraction_from_record(
        global_bounds["selected_minimum_modulus"]
    )
    selected_maximum = _fraction_from_record(
        global_bounds["selected_spectral_radius"]
    )
    excluded_minimum = _fraction_from_record(
        global_bounds["excluded_minimum_modulus"]
    )
    log_gap = _fraction_from_record(
        payloads["q007i"]["cycle"]["enumeration"][
            "global_minimum_log_gap"
        ]
    )
    beta_maximum = max(
        _fraction_from_record(record["beta"])
        for record in q007h1["cycle"]["eigencertification"]["block_records"]
    )
    finite_minimum_modulus = min(
        excluded_minimum,
        selected_minimum ** (TAIL_DEGREE - 1),
    )
    finite_degree_gap = finite_minimum_modulus * log_gap
    tail_gap = excluded_minimum - selected_maximum**TAIL_DEGREE
    uniform_gap = min(finite_degree_gap, tail_gap)
    working_selected_maximum = _round_up(selected_maximum)
    working_uniform_gap = _round_down(uniform_gap)
    working_beta_maximum = _round_up(beta_maximum)

    q007i_reconstruction = payloads["q007i"]["cycle"][
        "spectral_reconstruction"
    ]
    representative_records = q007i_reconstruction["records"]
    reconstruction = {
        "source": "sealed Q007i representative proof reconstruction",
        "representative_count": q007i_reconstruction["representative_count"],
        "proof_digest_mismatch_count": q007i_reconstruction[
            "proof_digest_mismatch_count"
        ],
        "all_proof_digests_match": q007i_reconstruction[
            "all_proof_digests_match"
        ],
    }
    maximum_eigenvector_infinity_norm = Fraction(0)
    for representative in representative_records:
        wave_index = representative["wave_index"]
        kx = 2.0 * np.pi * wave_index[0] / SIZE
        ky = 2.0 * np.pi * wave_index[1] / SIZE
        center = filtered_fourier_symbol(kx, ky, float(OMEGA), float(ETA))
        _, eigenvectors = np.linalg.eig(center)
        norm = max(
            sum(
                (
                    _dyadic_absolute_one(eigenvectors[row, column])
                    for column in range(9)
                ),
                Fraction(0),
            )
            for row in range(9)
        )
        maximum_eigenvector_infinity_norm = max(
            maximum_eigenvector_infinity_norm,
            norm,
        )

    collision = rational_collision_symbol()
    maximum_collision_entry = max(
        abs(entry) for row in collision for entry in row
    )
    product_modulus_upper = selected_maximum**2
    working_product_modulus_upper = working_selected_maximum**2
    augmented_entry_upper = max(
        maximum_collision_entry + working_product_modulus_upper,
        exact_coefficients["right_entry"],
        exact_coefficients["left_entry"],
        Fraction(1),
    )

    external_inverse = 81 * working_beta_maximum / working_uniform_gap
    zero_inverse = 1 / working_uniform_gap
    internal_inverse = (
        math.factorial(AUGMENTED_DIMENSION)
        * AUGMENTED_ENTRY_BOUND ** (AUGMENTED_DIMENSION - 1)
        / working_uniform_gap**AUGMENTED_EXTERNAL_DIMENSION
    )
    pair_inverse = max(
        external_inverse,
        zero_inverse,
        max(Fraction(1), exact_coefficients["c_v"]) * internal_inverse,
    )
    exact = {
        "selected_minimum": selected_minimum,
        "excluded_minimum": excluded_minimum,
        "log_gap": log_gap,
        "finite_degree_gap": finite_degree_gap,
        "tail_gap": tail_gap,
        "uniform_gap_raw": uniform_gap,
        "uniform_gap": working_uniform_gap,
        "beta_maximum_raw": beta_maximum,
        "beta_maximum": working_beta_maximum,
        "selected_maximum_raw": selected_maximum,
        "selected_maximum": working_selected_maximum,
        "maximum_eigenvector_infinity_norm": maximum_eigenvector_infinity_norm,
        "maximum_collision_entry": maximum_collision_entry,
        "product_modulus_upper_raw": product_modulus_upper,
        "product_modulus_upper": working_product_modulus_upper,
        "augmented_entry_upper": augmented_entry_upper,
        "external_inverse": external_inverse,
        "zero_inverse": zero_inverse,
        "internal_inverse": internal_inverse,
        "pair_inverse": pair_inverse,
    }
    serializable = {
        "selected_minimum_modulus": _fraction_record(selected_minimum),
        "selected_spectral_radius": _fraction_record(selected_maximum),
        "working_selected_spectral_radius_upper": _fraction_record(
            working_selected_maximum
        ),
        "excluded_minimum_modulus": _fraction_record(excluded_minimum),
        "global_rational_log_gap_lower": _fraction_record(log_gap),
        "finite_degree_minimum_modulus": _fraction_record(
            finite_minimum_modulus
        ),
        "degree_2_through_89_absolute_gap_lower": _fraction_record(
            finite_degree_gap
        ),
        "degree_90_tail_absolute_gap_lower": _fraction_record(tail_gap),
        "raw_uniform_absolute_gap_lower": _fraction_record(uniform_gap),
        "working_uniform_absolute_gap_lower": _fraction_record(
            working_uniform_gap
        ),
        "maximum_beta_upper": _fraction_record(beta_maximum),
        "working_maximum_beta_upper": _fraction_record(
            working_beta_maximum
        ),
        "majorant_outward_decimal_grid_digits": MAJORANT_DECIMAL_DIGITS,
        "representative_proof_reconstruction": reconstruction,
        "maximum_representative_eigenvector_infinity_norm_upper": (
            _fraction_record(maximum_eigenvector_infinity_norm)
        ),
        "registered_eigenvector_infinity_norm_bound": 9,
        "maximum_collision_entry_absolute": _fraction_record(
            maximum_collision_entry
        ),
        "raw_degree_at_least_two_product_modulus_upper": _fraction_record(
            product_modulus_upper
        ),
        "working_degree_at_least_two_product_modulus_upper": _fraction_record(
            working_product_modulus_upper
        ),
        "maximum_augmented_entry_absolute_upper": _fraction_record(
            augmented_entry_upper
        ),
        "registered_augmented_entry_bound": _fraction_record(
            AUGMENTED_ENTRY_BOUND
        ),
        "external_resolvent_l1_upper": _fraction_record(external_inverse),
        "zero_wave_fixed_leaf_inverse_upper": _fraction_record(zero_inverse),
        "internal_bordered_inverse_l1_upper": _fraction_record(
            internal_inverse
        ),
        "pair_homological_inverse_upper": _fraction_record(pair_inverse),
        "internal_determinant_lower_exponent": AUGMENTED_EXTERNAL_DIMENSION,
        "internal_adjugate_dimension": AUGMENTED_DIMENSION,
        "internal_determinant_identity": (
            "abs(det bordered(A-pI,-V;L*,0)) equals the product of the "
            "six excluded eigenvalue distances"
        ),
    }
    return serializable, exact


Polynomial = dict[int, Fraction]


def _polynomial_add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for degree, value in right.items():
        result[degree] = result.get(degree, Fraction(0)) + value
        if result[degree] == 0:
            del result[degree]
    return result


def _polynomial_scale(value: Polynomial, scalar: Fraction) -> Polynomial:
    return {
        degree: coefficient * scalar
        for degree, coefficient in value.items()
        if coefficient * scalar
    }


def _polynomial_multiply(
    left: Polynomial,
    right: Polynomial,
    maximum_degree: int | None = None,
) -> Polynomial:
    result: Polynomial = {}
    for left_degree, left_value in left.items():
        for right_degree, right_value in right.items():
            degree = left_degree + right_degree
            if maximum_degree is not None and degree > maximum_degree:
                continue
            result[degree] = result.get(degree, Fraction(0)) + (
                left_value * right_value
            )
    return {degree: value for degree, value in result.items() if value}


def _polynomial_power(
    value: Polynomial,
    exponent: int,
    maximum_degree: int | None = None,
) -> Polynomial:
    result: Polynomial = {0: Fraction(1)}
    for _ in range(exponent):
        result = _polynomial_multiply(result, value, maximum_degree)
    return result


def _polynomial_evaluate(
    value: Polynomial,
    argument: Fraction,
    minimum_degree: int = 0,
    maximum_degree: int | None = None,
) -> Fraction:
    return sum(
        (
            coefficient * argument**degree
            for degree, coefficient in value.items()
            if degree >= minimum_degree
            and (maximum_degree is None or degree <= maximum_degree)
        ),
        Fraction(0),
    )


def _scalar_majorant_polynomials(
    coefficients: dict[str, Fraction],
    selected_radius: Fraction,
) -> dict[str, Polynomial]:
    h = {degree: coefficients[f"h{degree}"] for degree in (2, 3, 4)}
    g = {degree: coefficients[f"g{degree}"] for degree in (2, 3, 4)}
    state = _polynomial_add({1: coefficients["c_v"]}, h)
    nonlinear_low: Polynomial = {}
    for power in (2, 3, 4):
        nonlinear_low = _polynomial_add(
            nonlinear_low,
            _polynomial_scale(
                _polynomial_power(state, power, maximum_degree=4),
                NONLINEAR_MAJORANT_CONSTANT,
            ),
        )

    reduced_linear = {1: selected_radius}
    reduced = _polynomial_add(reduced_linear, g)
    composition: Polynomial = {}
    for power in (2, 3, 4):
        difference = _polynomial_add(
            _polynomial_power(reduced, power),
            _polynomial_scale(
                _polynomial_power(reduced_linear, power),
                Fraction(-1),
            ),
        )
        composition = _polynomial_add(
            composition,
            _polynomial_scale(difference, coefficients[f"h{power}"]),
        )
    return {
        "h": h,
        "g": g,
        "state": state,
        "nonlinear_low": nonlinear_low,
        "composition": composition,
    }


def _candidate_record(
    exponent: int,
    coefficients: dict[str, Fraction],
    spectral: dict[str, Fraction],
    polynomials: dict[str, Polynomial],
) -> tuple[dict[str, Any], dict[str, Fraction | bool | None]]:
    radius = Fraction(1, 10**exponent)
    chart_value = _polynomial_evaluate(polynomials["h"], radius)
    reduced_value = _polynomial_evaluate(polynomials["g"], radius)
    state_center = coefficients["c_v"] * radius + chart_value
    nonlinear_total = (
        NONLINEAR_MAJORANT_CONSTANT
        * state_center**2
        / (1 - state_center)
    )
    nonlinear_low = _polynomial_evaluate(
        polynomials["nonlinear_low"], radius
    )
    nonlinear_tail = nonlinear_total - nonlinear_low
    composition_tail = _polynomial_evaluate(
        polynomials["composition"],
        radius,
        minimum_degree=5,
    )
    residual_tail = nonlinear_tail + composition_tail
    y_bound = spectral["pair_inverse"] * residual_tail
    correction_radius = 2 * y_bound
    state_upper = state_center + correction_radius
    reduced_range_upper = (
        spectral["selected_maximum"] * radius
        + reduced_value
        + correction_radius / coefficients["c_v"]
    )
    density_buffer = 1 - state_upper
    reduced_range_buffer = radius - reduced_range_upper
    derivative_bound: Fraction | None = None
    contraction_bound: Fraction | None = None
    radii_margin: Fraction | None = None
    if density_buffer > 0 and reduced_range_buffer > 0:
        nonlinear_derivative = (
            NONLINEAR_MAJORANT_CONSTANT
            * state_upper
            * (2 - state_upper)
            / density_buffer**2
        )
        total_chart = chart_value + correction_radius
        total_reduced = (
            reduced_value + correction_radius / coefficients["c_v"]
        )
        composition_derivative = (
            total_reduced / reduced_range_buffer
            + total_chart
            / (coefficients["c_v"] * reduced_range_buffer)
        )
        derivative_bound = nonlinear_derivative + composition_derivative
        contraction_bound = spectral["pair_inverse"] * derivative_bound
        radii_margin = correction_radius - (
            y_bound + contraction_bound * correction_radius
        )
    passed = bool(
        nonlinear_tail >= 0
        and composition_tail >= 0
        and density_buffer > 0
        and reduced_range_buffer > 0
        and contraction_bound is not None
        and contraction_bound < MAXIMUM_CONTRACTION
        and radii_margin is not None
        and radii_margin > 0
    )
    exact: dict[str, Fraction | bool | None] = {
        "radius": radius,
        "chart_value": chart_value,
        "reduced_value": reduced_value,
        "state_center": state_center,
        "nonlinear_tail": nonlinear_tail,
        "composition_tail": composition_tail,
        "residual_tail": residual_tail,
        "y_bound": y_bound,
        "correction_radius": correction_radius,
        "state_upper": state_upper,
        "reduced_range_upper": reduced_range_upper,
        "density_buffer": density_buffer,
        "reduced_range_buffer": reduced_range_buffer,
        "derivative_bound": derivative_bound,
        "contraction_bound": contraction_bound,
        "radii_margin": radii_margin,
        "passed": passed,
    }

    def compact_record(value: Fraction) -> dict[str, int | float]:
        return {
            "float": float(value),
            "sign": int(value > 0) - int(value < 0),
            "numerator_bit_length": abs(value.numerator).bit_length(),
            "denominator_bit_length": value.denominator.bit_length(),
        }

    def optional_record(value: Fraction | None) -> dict[str, Any] | None:
        return None if value is None else compact_record(value)

    serializable = {
        "candidate_exponent": exponent,
        "modal_radius": compact_record(radius),
        "modal_radius_decimal": f"1e-{exponent}",
        "quartic_chart_majorant": compact_record(chart_value),
        "quartic_reduced_majorant": compact_record(reduced_value),
        "quartic_center_state_majorant": compact_record(state_center),
        "nonlinear_degree_five_tail": compact_record(nonlinear_tail),
        "composition_degree_five_tail": compact_record(composition_tail),
        "invariance_residual_tail": compact_record(residual_tail),
        "newton_y_bound": compact_record(y_bound),
        "registered_correction_radius_tau": compact_record(correction_radius),
        "state_norm_upper": compact_record(state_upper),
        "reduced_range_upper": compact_record(reduced_range_upper),
        "density_buffer": compact_record(density_buffer),
        "reduced_range_buffer": compact_record(reduced_range_buffer),
        "nonlinear_derivative_majorant": optional_record(derivative_bound),
        "contraction_bound_z": optional_record(contraction_bound),
        "radii_inequality_margin": optional_record(radii_margin),
        "tail_nonnegative": bool(
            nonlinear_tail >= 0 and composition_tail >= 0
        ),
        "density_buffer_positive": density_buffer > 0,
        "reduced_range_buffer_positive": reduced_range_buffer > 0,
        "contraction_strictly_below_one_half": bool(
            contraction_bound is not None
            and contraction_bound < MAXIMUM_CONTRACTION
        ),
        "radii_inequality_strict": bool(
            radii_margin is not None and radii_margin > 0
        ),
        "passed": passed,
    }
    return serializable, exact


def _exact_candidate_certificate(
    exact: dict[str, Fraction | bool | None] | None,
) -> dict[str, Any] | None:
    if exact is None:
        return None
    fields = (
        "radius",
        "nonlinear_tail",
        "composition_tail",
        "residual_tail",
        "y_bound",
        "correction_radius",
        "density_buffer",
        "reduced_range_buffer",
        "derivative_bound",
        "contraction_bound",
        "radii_margin",
    )
    return {
        **{
            field: (
                None
                if exact[field] is None
                else _fraction_record(exact[field])
            )
            for field in fields
        },
        "passed": bool(exact["passed"]),
    }


def _structural_majorant_audit() -> tuple[dict[str, Any], bool]:
    weight_sum = sum(WEIGHTS, Fraction(0))
    velocity_quadratic = sum(
        (
            weight * (abs(cx) + abs(cy)) ** 2
            for (cx, cy), weight in zip(VELOCITIES, WEIGHTS, strict=True)
        ),
        Fraction(0),
    )
    equilibrium_quadratic = (
        Fraction(9, 2) * velocity_quadratic + Fraction(3, 2) * 2
    )
    collision_nonlinear = OMEGA * equilibrium_quadratic
    collision = rational_collision_symbol()
    conservation_rows = (
        tuple(Fraction(1) for _ in VELOCITIES),
        tuple(Fraction(cx) for cx, _ in VELOCITIES),
        tuple(Fraction(cy) for _, cy in VELOCITIES),
    )
    kinetic_identity = all(
        sum(
            (conservation_rows[moment][row] * collision[row][column]
             for row in range(9)),
            Fraction(0),
        ) == conservation_rows[moment][column]
        for moment in range(3)
        for column in range(9)
    )
    passed = bool(
        weight_sum == 1
        and velocity_quadratic == Fraction(8, 9)
        and equilibrium_quadratic == 7
        and collision_nonlinear == NONLINEAR_MAJORANT_CONSTANT
        and kinetic_identity
    )
    return {
        "cyclic_fourier_convolution_l1_constant": 1,
        "d2q9_weight_sum": _fraction_record(weight_sum),
        "weighted_absolute_velocity_quadratic": _fraction_record(
            velocity_quadratic
        ),
        "equilibrium_quadratic_majorant_before_omega": _fraction_record(
            equilibrium_quadratic
        ),
        "omega": _fraction_record(OMEGA),
        "nonlinear_majorant_constant": _fraction_record(
            collision_nonlinear
        ),
        "registered_nonlinear_majorant_constant": _fraction_record(
            NONLINEAR_MAJORANT_CONSTANT
        ),
        "collision_conserves_three_moments_exactly": kinetic_identity,
        "zero_wave_fixed_leaf_collision_action": "-I/2",
        "bordered_determinant_derivation": (
            "in the exact (V, ker L*) splitting, determinant-preserving row/"
            "column changes reduce the bordered matrix to an external "
            "six-dimensional block and a selected identity saddle block"
        ),
        "banach_pair_norm": "max(chart Wiener l1, c_V * reduced modal l1)",
        "analytic_derivative_bound": (
            "sum n*p_n*s^(n-1) <= norm_rho/(rho-s)"
        ),
        "passed": passed,
    }, passed


def run_explicit_local_radius_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    coefficient_reproduction, coefficients, _model = _coefficient_majorants(
        payloads
    )
    spectral_serializable, spectral = _spectral_and_inverse_majorants(
        payloads,
        coefficients,
    )
    structural_audit, structural_passed = _structural_majorant_audit()
    polynomials = _scalar_majorant_polynomials(
        coefficients,
        spectral["selected_maximum"],
    )
    candidate_records = []
    candidate_exact = []
    for exponent in CANDIDATE_EXPONENTS:
        serializable, exact = _candidate_record(
            exponent,
            coefficients,
            spectral,
            polynomials,
        )
        candidate_records.append(serializable)
        candidate_exact.append(exact)

    passing_indices = [
        index for index, record in enumerate(candidate_exact) if record["passed"]
    ]
    selected_index = passing_indices[0] if passing_indices else None
    selected_record = (
        candidate_records[selected_index] if selected_index is not None else None
    )
    selected_exact = (
        candidate_exact[selected_index] if selected_index is not None else None
    )
    previous_larger_record = (
        candidate_records[selected_index - 1]
        if selected_index is not None and selected_index > 0
        else None
    )
    previous_larger_exact = (
        candidate_exact[selected_index - 1]
        if selected_index is not None and selected_index > 0
        else None
    )

    exact_center_error = None
    real_radius_lower = None
    if selected_exact is not None:
        selected_radius = selected_exact["radius"]
        correction_radius = selected_exact["correction_radius"]
        assert isinstance(selected_radius, Fraction)
        assert isinstance(correction_radius, Fraction)
        chart_box = sum(
            coefficients[f"h{degree}_box"] * selected_radius**degree
            for degree in (2, 3, 4)
        )
        reduced_box = sum(
            coefficients[f"g{degree}_box"] * selected_radius**degree
            for degree in (2, 3, 4)
        )
        exact_center_error = correction_radius + max(
            chart_box,
            coefficients["c_v"] * reduced_box,
        )
        sqrt_24_upper = _sqrt_bounds(Fraction(24)).upper
        real_radius_lower = 17 * selected_radius / sqrt_24_upper

    selected_summary = None
    if selected_record is not None and selected_exact is not None:
        selected_summary = {
            **selected_record,
            "real_euclidean_radius_lower": _fraction_record(real_radius_lower),
            "real_radius_formula": "17 * modal_radius / sqrt(24)",
            "registered_numerical_quartic_center_pair_error_upper": (
                _fraction_record(exact_center_error)
            ),
            "is_largest_passing_registered_candidate": True,
        }

    pass_count = len(passing_indices)
    positive_buffer_count = sum(
        bool(
            record["density_buffer_positive"]
            and record["reduced_range_buffer_positive"]
        )
        for record in candidate_records
    )
    nonnegative_tail_count = sum(
        bool(record["tail_nonnegative"]) for record in candidate_records
    )
    maximal_selection_valid = bool(
        selected_index is not None
        and selected_record is not None
        and selected_record["passed"]
        and (
            selected_index == 0
            or (
                previous_larger_record is not None
                and not previous_larger_record["passed"]
            )
        )
        and all(
            not candidate_records[index]["passed"]
            for index in range(selected_index)
        )
    )

    serializable_sections = {
        "input_artifacts": input_records,
        "coefficient_reproduction_and_norms": coefficient_reproduction,
        "spectral_separation_and_inverse": spectral_serializable,
        "structural_majorant_audit": structural_audit,
        "radius_search": {
            "candidate_exponents": list(CANDIDATE_EXPONENTS),
            "candidate_count": len(CANDIDATE_EXPONENTS),
            "candidate_order": "1e-2, 1e-3, ..., 1e-120",
            "nonnegative_tail_count": nonnegative_tail_count,
            "positive_domain_buffer_count": positive_buffer_count,
            "passing_candidate_count": pass_count,
            "selected_candidate": selected_summary,
            "previous_larger_candidate": previous_larger_record,
            "exact_boundary_certificate": {
                "selected": _exact_candidate_certificate(selected_exact),
                "previous_larger": _exact_candidate_certificate(
                    previous_larger_exact
                ),
                "representation_note": (
                    "All 119 decisions use Fraction exactly; compact records "
                    "store exact signs and bit lengths, while full base-16 "
                    "rationals are retained for the pass/fail boundary."
                ),
            },
            "records": candidate_records,
        },
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )

    input_valid = all(record["passed"] for record in input_records.values())
    coefficient_valid = bool(
        coefficient_reproduction["matches"]
        and coefficient_reproduction["all_coefficients_finite"]
        and all(coefficients[f"h{degree}"] > 0 for degree in (2, 3, 4))
        and all(coefficients[f"g{degree}"] > 0 for degree in (2, 3, 4))
        and coefficients["c_v"] > 0
    )
    spectral_valid = bool(
        spectral["uniform_gap"] > 0
        and spectral["tail_gap"] > 0
        and spectral["maximum_eigenvector_infinity_norm"] < 9
        and spectral["augmented_entry_upper"] < AUGMENTED_ENTRY_BOUND
        and spectral_serializable["representative_proof_reconstruction"][
            "proof_digest_mismatch_count"
        ]
        == 0
    )
    candidate_valid = bool(
        len(candidate_records) == len(CANDIDATE_EXPONENTS)
        and nonnegative_tail_count == len(CANDIDATE_EXPONENTS)
        and finite_strict_json
    )
    validity_gates = {
        "registered_inputs_and_runners": {
            "passed": input_valid,
            "threshold": (
                "all six artifact SHA/source/scope/outcomes/gates and four "
                "standalone runner SHA values match"
            ),
            "value": {
                name: record["passed"] for name, record in input_records.items()
            },
        },
        "coefficient_reproduction_and_exact_norms": {
            "passed": coefficient_valid,
            "threshold": (
                "five Q007c1 hashes reproduce and all rational c_V/H2-4/R2-4 "
                "operator majorants are positive and finite"
            ),
            "value": {
                "hashes_match": coefficient_reproduction["matches"],
                "all_coefficients_finite": coefficient_reproduction[
                    "all_coefficients_finite"
                ],
            },
        },
        "spectral_gap_and_homological_inverse": {
            "passed": spectral_valid,
            "threshold": (
                "positive finite/tail gap, 72 proof digests reproduce, S_inf "
                "<9, and bordered entries <2"
            ),
            "value": {
                "uniform_gap": float(spectral["uniform_gap"]),
                "proof_digest_mismatch_count": spectral_serializable[
                    "representative_proof_reconstruction"
                ]["proof_digest_mismatch_count"],
                "eigenvector_infinity_norm": float(
                    spectral["maximum_eigenvector_infinity_norm"]
                ),
                "augmented_entry_upper": float(
                    spectral["augmented_entry_upper"]
                ),
            },
        },
        "wiener_and_d2q9_structural_majorants": {
            "passed": structural_passed,
            "threshold": (
                "exact D2Q9 weight, velocity, conservation, fixed-leaf, and "
                "21/2 nonlinear-majorant identities"
            ),
            "value": structural_audit["passed"],
        },
        "registered_candidate_audit_and_strict_json": {
            "passed": candidate_valid,
            "threshold": (
                "all 119 candidates evaluated, all scalar tails nonnegative, "
                "and every summary finite strict JSON"
            ),
            "value": {
                "candidate_count": len(candidate_records),
                "nonnegative_tail_count": nonnegative_tail_count,
                "finite_strict_json": finite_strict_json,
            },
        },
    }
    validity_passed = all(gate["passed"] for gate in validity_gates.values())

    hypothesis_gates = {
        "uniform_all_degree_separation_and_inverse": {
            "passed": bool(
                spectral["uniform_gap"] > 0 and spectral["pair_inverse"] > 0
            ),
            "threshold": "delta >0 and finite positive C_L",
            "value": {
                "uniform_gap": float(spectral["uniform_gap"]),
                "pair_inverse_upper": float(spectral["pair_inverse"]),
            },
        },
        "nonempty_density_and_reduced_range_domain": {
            "passed": positive_buffer_count > 0,
            "threshold": (
                "at least one registered radius has x<1 and reduced range s<rho"
            ),
            "value": positive_buffer_count,
        },
        "strict_quartic_centered_contraction": {
            "passed": pass_count > 0,
            "threshold": (
                "at least one same candidate has Z<1/2 and Y+Z*tau<tau"
            ),
            "value": pass_count,
        },
        "largest_registered_candidate_selected": {
            "passed": maximal_selection_valid,
            "threshold": (
                "the saved radius is the largest passing member of 1e-2..1e-120"
            ),
            "value": {
                "selected_exponent": (
                    selected_record["candidate_exponent"]
                    if selected_record is not None
                    else None
                ),
                "previous_larger_passed": (
                    previous_larger_record["passed"]
                    if previous_larger_record is not None
                    else None
                ),
            },
        },
    }
    hypotheses_passed = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if not validity_passed:
        outcome = "inconclusive"
        classification = "registered explicit-local-radius audit invalid"
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "registered quartic-centered contraction gives an explicit "
            "fixed-leaf local radius"
        )
    else:
        outcome = "not_certified"
        classification = "registered explicit local radius not certified"

    return {
        "question": (
            "Does the certified quartic graph-gauge jet center a rigorous "
            "Banach contraction on one registered modal l1 ball?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": float(OMEGA),
            "eta": float(ETA),
            "selected_complex_dimension": SELECTED_COMPLEX_DIMENSION,
            "candidate_exponent_range": [
                CANDIDATE_EXPONENTS[0],
                CANDIDATE_EXPONENTS[-1],
            ],
            "candidate_count": len(CANDIDATE_EXPONENTS),
            "contraction_threshold": _fraction_record(MAXIMUM_CONTRACTION),
            "correction_radius_rule": "tau = 2Y",
            "majorant_outward_decimal_grid_digits": MAJORANT_DECIMAL_DIGITS,
            "chart_center_degree": 4,
            "state_norm": "Fourier-population Wiener l1",
            "reduced_norm": "selected complex modal l1",
            "pair_norm": "max(H, c_V G)",
        },
        **serializable_sections,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "explicit_modal_l1_radius_certified": bool(
                validity_passed and hypotheses_passed
            ),
            "selected_candidate": selected_summary,
            "analytic_chart_and_reduced_map_exist": bool(
                validity_passed and hypotheses_passed
            ),
            "unique_in_registered_correction_ball": bool(
                validity_passed and hypotheses_passed
            ),
            "identified_with_q007i_theorem_manifold": bool(
                validity_passed and hypotheses_passed
            ),
        },
        "claim_boundary": (
            "This is a deliberately coarse explicit existence radius for the "
            "fixed 17x17 filtered map on one conservation leaf. It is only the "
            "largest passing member of the preregistered decimal grid, not an "
            "optimal radius. It does not certify finite-ball normal attraction, "
            "forward invariance, positivity, grid uniformity, or a continuum "
            "limit, and it does not alter Q007c1's finite-amplitude rejection."
        ),
        "preserved_prior_outcomes": {
            "q007c1_finite_amplitude_rejection_changed": False,
            "q007i_qualitative_theorem_acceptance_changed": False,
            "q007j_linear_eigencoordinate_acceptance_changed": False,
            "q007k_quadratic_jet_acceptance_changed": False,
            "q007l_cubic_jet_acceptance_changed": False,
            "q007m_quartic_jet_acceptance_changed": False,
            "q007h_independent_preconditioner_inconclusive_changed": False,
            "q008c_tt_rejection_changed": False,
        },
        "next_change": (
            "If accepted, sharpen the internal bordered-resolvent bound in a "
            "separate preregistered gate before attempting finite-ball normal "
            "attraction."
        ),
    }


def run_q007n_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_explicit_local_radius_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": "rational quartic-centered explicit local radius",
            "construction_grid": [SIZE, SIZE],
            "omega": float(OMEGA),
            "eta": float(ETA),
            "conservation_treatment": "fixed global mass and momentum leaf",
            "selected_real_dimension": SELECTED_COMPLEX_DIMENSION,
            "selected_complexified_dimension": SELECTED_COMPLEX_DIMENSION,
            "claim": (
                "explicit analytic existence radius only; no finite-ball "
                "normal-attraction, forward-invariance, positivity, grid-"
                "uniform, or continuum claim"
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
    result = run_q007n_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
