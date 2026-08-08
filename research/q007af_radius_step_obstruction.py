"""Sealed Q007af external phase-disc radius-step obstruction audit.

The Q007n scalar majorant, Q007ad original asymmetric phase discs, and
Q007ae inverse ordering are held fixed.  Exact arithmetic brackets the
largest inverse compatible with the registered 1e-15 candidate, then one
sealed Q007ad comparison is used to test whether the necessary external gap
can belong to that certificate family.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from pathlib import Path
from typing import Any

import research.q007ac_phase_aware_resolvent as q007ac
import research.q007ad_asymmetric_phase_resolvent as q007ad
import research.q007ae_internal_phase_resolvent as q007ae
import research.q007n_explicit_local_radius as q007n
import research.q007o_external_complement_radius as q007o
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _default_artifact_directory,
    _file_sha256,
    _fraction_record,
    _sqrt_bounds,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_COMPLEX_DIMENSION = 24
TARGET_CANDIDATE_EXPONENT = 15
SEARCH_INVERSE_LOWER = 1
SEARCH_INVERSE_UPPER = 10**13
REGISTERED_PASSING_INVERSE = 173_791_195_571
REGISTERED_FAILING_INVERSE = 173_791_195_572
MAXIMUM_WITNESS_TO_REQUIRED_RATIO = Fraction(95, 100)
MINIMUM_GAP_SHORTFALL = Fraction(14, 10**10)
MINIMUM_OPTIMISTIC_INVERSE_RATIO = Fraction(105, 100)
SQRT_ENCLOSURE_WIDTH = Fraction(1, 10**100)

REGISTERED_ARTIFACTS = {
    "q007n": {
        "filename": "q007n_explicit_local_radius.json",
        "sha256": (
            "7fe09089744e41229e71666540e4885d560a4c27a2e8bc95a94d5959af0fbc36"
        ),
        "runner_sha256": (
            "6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9"
        ),
        "classification": (
            "registered quartic-centered contraction gives an explicit "
            "fixed-leaf local radius"
        ),
    },
    "q007ad": {
        "filename": "q007ad_asymmetric_phase_resolvent.json",
        "sha256": (
            "6a6f642cb681409ca160773180e025c1ffbc1929d6ec84423c384c57007571e4"
        ),
        "runner_sha256": (
            "3ca5e39c3ddb79c886ef7bf4d6e6ad923deb66e53da3663251f183abbab7b0ae"
        ),
        "classification": (
            "original asymmetric discs certify the critical "
            "external-output phase gap"
        ),
    },
    "q007ae": {
        "filename": "q007ae_internal_phase_resolvent.json",
        "sha256": (
            "c6d28bba13fcf831dfccaf03854072256f7e8ff1a241b54aaf84552dd06a2a55"
        ),
        "runner_sha256": (
            "f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600"
        ),
        "classification": (
            "phase-aware selected-output centers remove the internal "
            "resolvent bottleneck"
        ),
    },
}

REGISTERED_IMPLEMENTATIONS = {
    "q007ac": {
        "path": "research/q007ac_phase_aware_resolvent.py",
        "sha256": (
            "8c2757c4c3771007dc15135bc407551bbef74906294ab897b1a4f251d5abe2ae"
        ),
    },
    "q007ad": {
        "path": "research/q007ad_asymmetric_phase_resolvent.py",
        "sha256": (
            "3ca5e39c3ddb79c886ef7bf4d6e6ad923deb66e53da3663251f183abbab7b0ae"
        ),
    },
    "q007ae": {
        "path": "research/q007ae_internal_phase_resolvent.py",
        "sha256": (
            "f2e0d90ae6bb5f9694c799d2ea850a014f66f2ab9681d94dc1c850cc753db600"
        ),
    },
    "q007n": {
        "path": "research/q007n_explicit_local_radius.py",
        "sha256": (
            "6eefae3386e5c49f151b1cd4537eb84fbb92858578fe4fce7768e50ad43c5dc9"
        ),
    },
    "q007o": {
        "path": "research/q007o_external_complement_radius.py",
        "sha256": (
            "d34afda382784610ea2b8997e6c44376188b02c42668ade8e2d53ff9bc9afea7"
        ),
    },
}

REGISTERED_DIGESTS = {
    "q007ad": {
        "input": (
            "b1b1b2750e871c6ee3b243f7df590ec19dd6d604d9699f183af007b89d0f7935"
        ),
        "result": (
            "f5df89c55a86978c85542eeec82e6419884b69b919c0385ca77e9677b1c1d17f"
        ),
        "phase": (
            "086516b273f30d7c94c276399c16f8a6433bd90e3dc03fb740d2ab45754e4a37"
        ),
    },
    "q007ae": {
        "input": (
            "23fba479cfa07ec50721d9b05bcaf40a0ac04126497ff64b04785e1d20534e0e"
        ),
        "result": (
            "3e1792c5215952d9126bf5bd61409a2a0d72ebc12970ad1e4aaca481d4fcb687"
        ),
        "phase": (
            "4aea091076179e7ef8eb14c9c4828b41d6af3ef25665e5b2dbbf562acf692b3b"
        ),
        "selected_center": (
            "3cc524ebb82c3e375bf35d456f96be11fa5d124728873046ed59a7032a2058d7"
        ),
    },
}

EXPECTED_WITNESS = {
    "degree": 71,
    "counts": [24, 38, 2, 7],
    "axis_acoustic_positive_count": 12,
    "axis_acoustic_negative_count": 12,
    "diagonal_acoustic_positive_count": 1,
    "diagonal_acoustic_negative_count": 1,
    "external_identifier": "wave=-7,-7;eigenvalue_index=6",
}

_IMPLEMENTATION_MODULES = {
    "q007ac": q007ac,
    "q007ad": q007ad,
    "q007ae": q007ae,
    "q007n": q007n,
    "q007o": q007o,
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


def _complex_fraction_from_record(
    record: dict[str, Any],
) -> tuple[Fraction, Fraction]:
    return (
        _fraction_from_record(record["real"]),
        _fraction_from_record(record["imaginary"]),
    )


def _common_scope_matches(payload: dict[str, Any]) -> bool:
    scope = payload.get("mathematical_scope", {})
    return bool(
        scope.get("construction_grid") == [SIZE, SIZE]
        and float(scope.get("omega")) == OMEGA
        and float(scope.get("eta")) == ETA
        and scope.get("conservation_treatment")
        == "fixed global mass and momentum leaf"
    )


def _observed_digest_record(name: str, cycle: dict[str, Any]) -> dict[str, Any]:
    if name == "q007n":
        return {"registered": {}, "observed": {}, "matches": True}
    if name == "q007ad":
        observed = {
            "input": cycle.get("input_digest_sha256"),
            "result": cycle.get("result_digest_sha256"),
            "phase": cycle.get("phase_aware_separation_audit", {})
            .get("phase", {})
            .get("comparison_digest_sha256"),
        }
    else:
        observed = {
            "input": cycle.get("input_digest_sha256"),
            "result": cycle.get("result_digest_sha256"),
            "phase": cycle.get("phase_aware_separation_audit", {})
            .get("phase", {})
            .get("comparison_digest_sha256"),
            "selected_center": cycle.get(
                "phase_aware_separation_audit", {}
            ).get("selected_center_certificate_digest_sha256"),
        }
    registered = REGISTERED_DIGESTS[name]
    return {
        "registered": registered,
        "observed": observed,
        "matches": observed == registered,
    }


def _load_registered_inputs(
    directory: Path,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    payloads = {}
    records = {}
    for name, registration in REGISTERED_ARTIFACTS.items():
        path = directory / registration["filename"]
        payload = json.loads(path.read_text(encoding="utf-8"))
        payloads[name] = payload
        cycle = payload.get("cycle", {})
        observed_sha = _file_sha256(path)
        runner = _IMPLEMENTATION_MODULES[name]
        runner_path = Path(runner.__file__).resolve()
        observed_runner_sha = _file_sha256(runner_path)
        digest_record = _observed_digest_record(name, cycle)
        record = {
            "filename": path.name,
            "sha256": observed_sha,
            "registered_sha256": registration["sha256"],
            "sha256_matches": observed_sha == registration["sha256"],
            "runner_filename": runner_path.name,
            "runner_sha256": observed_runner_sha,
            "registered_runner_sha256": registration["runner_sha256"],
            "runner_sha256_matches": (
                observed_runner_sha == registration["runner_sha256"]
            ),
            "source_matches": payload.get("source") == source_metadata(),
            "scope_matches": _common_scope_matches(payload),
            "study_gate": payload.get("study_gate"),
            "scientific_outcome": payload.get("scientific_outcome"),
            "scientific_classification": cycle.get(
                "scientific_classification"
            ),
            "registered_digest_audit": digest_record,
        }
        record["passed"] = bool(
            record["sha256_matches"]
            and record["runner_sha256_matches"]
            and record["source_matches"]
            and record["scope_matches"]
            and record["study_gate"] == "passed"
            and record["scientific_outcome"] == "accepted"
            and record["scientific_classification"]
            == registration["classification"]
            and digest_record["matches"]
        )
        records[name] = record
    return payloads, records


def _implementation_source_audit() -> dict[str, Any]:
    records = {}
    for name, registration in REGISTERED_IMPLEMENTATIONS.items():
        path = Path(_IMPLEMENTATION_MODULES[name].__file__).resolve()
        observed = _file_sha256(path)
        records[name] = {
            "path": registration["path"],
            "sha256": observed,
            "registered_sha256": registration["sha256"],
            "passed": observed == registration["sha256"],
        }
    return {
        "records": records,
        "all_registered_implementation_sha256_match": all(
            record["passed"] for record in records.values()
        ),
    }


def _candidate(
    inverse: int | Fraction,
    coefficients: dict[str, Fraction],
    selected_radius: Fraction,
    polynomials: dict[str, q007n.Polynomial],
) -> tuple[dict[str, Any], dict[str, Fraction | bool | None]]:
    return q007n._candidate_record(
        TARGET_CANDIDATE_EXPONENT,
        coefficients,
        {
            "selected_maximum": selected_radius,
            "pair_inverse": Fraction(inverse),
        },
        polynomials,
    )


def _integer_inverse_threshold_audit(
    coefficients: dict[str, Fraction],
    selected_radius: Fraction,
    polynomials: dict[str, q007n.Polynomial],
) -> tuple[dict[str, Any], dict[str, dict[str, Fraction | bool | None]]]:
    initial_lower_record, initial_lower_exact = _candidate(
        SEARCH_INVERSE_LOWER,
        coefficients,
        selected_radius,
        polynomials,
    )
    initial_upper_record, initial_upper_exact = _candidate(
        SEARCH_INVERSE_UPPER,
        coefficients,
        selected_radius,
        polynomials,
    )
    lower = SEARCH_INVERSE_LOWER
    upper = SEARCH_INVERSE_UPPER
    decisions = []
    while upper - lower > 1:
        midpoint = (lower + upper) // 2
        _record, exact = _candidate(
            midpoint,
            coefficients,
            selected_radius,
            polynomials,
        )
        passed = bool(exact["passed"])
        decisions.append({"inverse": midpoint, "passed": passed})
        if passed:
            lower = midpoint
        else:
            upper = midpoint

    lower_record, lower_exact = _candidate(
        lower, coefficients, selected_radius, polynomials
    )
    upper_record, upper_exact = _candidate(
        upper, coefficients, selected_radius, polynomials
    )
    decision_digest = q007ac._canonical_json_sha256(decisions)
    audit = {
        "target_candidate_exponent": TARGET_CANDIDATE_EXPONENT,
        "target_modal_radius_decimal": "1e-15",
        "initial_inverse_interval": [
            SEARCH_INVERSE_LOWER,
            SEARCH_INVERSE_UPPER,
        ],
        "initial_lower_passed": bool(initial_lower_exact["passed"]),
        "initial_upper_passed": bool(initial_upper_exact["passed"]),
        "bisection_iteration_count": len(decisions),
        "bisection_decisions": decisions,
        "bisection_decision_digest_sha256": decision_digest,
        "maximum_passing_integer_inverse": lower,
        "minimum_failing_integer_inverse": upper,
        "final_integer_width": upper - lower,
        "registered_passing_inverse": REGISTERED_PASSING_INVERSE,
        "registered_failing_inverse": REGISTERED_FAILING_INVERSE,
        "registered_bracket_reproduced": bool(
            lower == REGISTERED_PASSING_INVERSE
            and upper == REGISTERED_FAILING_INVERSE
        ),
        "passing_endpoint": {
            "pair_inverse": _fraction_record(Fraction(lower)),
            "candidate_record": lower_record,
            "exact_certificate": q007n._exact_candidate_certificate(
                lower_exact
            ),
        },
        "failing_endpoint": {
            "pair_inverse": _fraction_record(Fraction(upper)),
            "candidate_record": upper_record,
            "exact_certificate": q007n._exact_candidate_certificate(
                upper_exact
            ),
        },
        "initial_endpoint_records": {
            "lower": initial_lower_record,
            "upper": initial_upper_record,
        },
        "complete": bool(
            initial_lower_exact["passed"]
            and not initial_upper_exact["passed"]
            and upper - lower == 1
            and lower_exact["passed"]
            and not upper_exact["passed"]
        ),
    }
    return audit, {
        "passing": lower_exact,
        "failing": upper_exact,
        "initial_lower": initial_lower_exact,
        "initial_upper": initial_upper_exact,
    }


def _required_fraction(
    exact: dict[str, Fraction | bool | None],
    key: str,
) -> Fraction:
    value = exact[key]
    if not isinstance(value, Fraction):
        raise TypeError(f"{key} is not available as an exact fraction")
    return value


def _monotonicity_audit(
    coefficients: dict[str, Fraction],
    selected_radius: Fraction,
    polynomials: dict[str, q007n.Polynomial],
    endpoints: dict[str, dict[str, Fraction | bool | None]],
) -> tuple[dict[str, Any], bool]:
    _zero_record, zero = _candidate(
        Fraction(0), coefficients, selected_radius, polynomials
    )
    passing = endpoints["passing"]
    failing = endpoints["failing"]
    residual_tail = _required_fraction(zero, "residual_tail")
    chart_value = _required_fraction(zero, "chart_value")
    reduced_value = _required_fraction(zero, "reduced_value")
    state_center = _required_fraction(zero, "state_center")
    base_density_buffer = _required_fraction(zero, "density_buffer")
    base_reduced_range_buffer = _required_fraction(
        zero, "reduced_range_buffer"
    )
    c_v = coefficients["c_v"]

    exact_formula_matches = []
    radii_identity_matches = []
    for inverse, exact in (
        (Fraction(REGISTERED_PASSING_INVERSE), passing),
        (Fraction(REGISTERED_FAILING_INVERSE), failing),
    ):
        state_upper = _required_fraction(exact, "state_upper")
        density_buffer = _required_fraction(exact, "density_buffer")
        reduced_range_buffer = _required_fraction(
            exact, "reduced_range_buffer"
        )
        correction = _required_fraction(exact, "correction_radius")
        nonlinear_derivative = q007n.NONLINEAR_MAJORANT_CONSTANT * (
            Fraction(1, density_buffer**2) - 1
        )
        composition_derivative = (
            (reduced_value + correction / c_v) / reduced_range_buffer
            + (chart_value + correction)
            / (c_v * reduced_range_buffer)
        )
        derivative = _required_fraction(exact, "derivative_bound")
        contraction = _required_fraction(exact, "contraction_bound")
        margin = _required_fraction(exact, "radii_margin")
        exact_formula_matches.append(
            bool(
                density_buffer == 1 - state_upper
                and derivative
                == nonlinear_derivative + composition_derivative
                and contraction == inverse * derivative
            )
        )
        radii_identity_matches.append(
            margin
            == inverse
            * residual_tail
            * (1 - 2 * contraction)
        )

    passing_z = _required_fraction(passing, "contraction_bound")
    failing_z = _required_fraction(failing, "contraction_bound")
    passing_margin = _required_fraction(passing, "radii_margin")
    failing_margin = _required_fraction(failing, "radii_margin")
    endpoint_domains_positive = all(
        _required_fraction(exact, "density_buffer") > 0
        and _required_fraction(exact, "reduced_range_buffer") > 0
        for exact in (passing, failing)
    )
    structural_signs = bool(
        residual_tail > 0
        and c_v > 0
        and q007n.NONLINEAR_MAJORANT_CONSTANT > 0
        and chart_value >= 0
        and reduced_value >= 0
        and state_center >= 0
        and base_density_buffer > 0
        and base_reduced_range_buffer > 0
    )
    monotonicity_proved = bool(
        structural_signs
        and endpoint_domains_positive
        and all(exact_formula_matches)
        and all(radii_identity_matches)
        and passing_z < q007n.MAXIMUM_CONTRACTION < failing_z
        and passing_margin > 0
        and failing_margin < 0
    )
    audit = {
        "proof_domain": (
            "For C>0 while density and reduced-range buffers are positive, "
            "x(C) and both composition numerators increase, their common "
            "buffer decreases, and (1-x(C))^-2-1 increases. Hence D(C) is "
            "nondecreasing and Z(C)=C*D(C) is strictly increasing. Outside "
            "that domain the candidate fails its buffer gate."
        ),
        "nonlinear_derivative_identity": (
            "(21/2) * ((1 - state_upper)^-2 - 1)"
        ),
        "radii_margin_identity": "C*T*(1-2*Z)",
        "residual_tail": _fraction_record(residual_tail),
        "chart_value_nonnegative": chart_value >= 0,
        "reduced_value_nonnegative": reduced_value >= 0,
        "state_center_nonnegative": state_center >= 0,
        "tangent_norm_positive": c_v > 0,
        "base_density_buffer": _fraction_record(base_density_buffer),
        "base_reduced_range_buffer": _fraction_record(
            base_reduced_range_buffer
        ),
        "endpoint_domains_positive": endpoint_domains_positive,
        "endpoint_derivative_formula_matches": exact_formula_matches,
        "endpoint_radii_identity_matches": radii_identity_matches,
        "passing_contraction_bound": _fraction_record(passing_z),
        "failing_contraction_bound": _fraction_record(failing_z),
        "passing_radii_margin": _fraction_record(passing_margin),
        "failing_radii_margin": _fraction_record(failing_margin),
        "structural_signs_passed": structural_signs,
        "contraction_crosses_one_half": bool(
            passing_z < q007n.MAXIMUM_CONTRACTION < failing_z
        ),
        "all_inverse_at_or_above_failing_endpoint_fail": (
            monotonicity_proved
        ),
        "passed": monotonicity_proved,
    }
    return audit, monotonicity_proved


def _majorant_reproduction_audit(
    payloads: dict[str, dict[str, Any]],
    coefficients: dict[str, Fraction],
    selected_radius: Fraction,
) -> tuple[dict[str, Any], bool]:
    q007n_cycle = payloads["q007n"]["cycle"]
    q007ae_cycle = payloads["q007ae"]["cycle"]
    q007ae_total = _fraction_from_record(
        q007ae_cycle["total_inverse_refinement"][
            "working_new_total_pair_inverse_upper"
        ]
    )
    reproduced_scan, _exact = q007o._radius_scan(
        coefficients, selected_radius, q007ae_total
    )
    stored_scan = q007ae_cycle["radius_comparison"][
        "internal_phase_refined_radius_search"
    ]
    records_match = reproduced_scan["records"] == stored_scan["records"]
    boundary_matches = bool(
        reproduced_scan["selected_candidate"]["modal_radius_decimal"]
        == "1e-16"
        and reproduced_scan["previous_larger_candidate"][
            "modal_radius_decimal"
        ]
        == "1e-15"
        and not reproduced_scan["previous_larger_candidate"]["passed"]
    )
    total = q007ae_cycle["total_inverse_refinement"]
    internal = _fraction_from_record(
        total["q007ae_working_internal_inverse_upper"]
    )
    zero = _fraction_from_record(total["q007n_zero_wave_inverse_upper"])
    external = _fraction_from_record(
        total["q007ad_working_external_inverse_upper"]
    )
    inverse_ordering = internal < zero < external == q007ae_total
    coefficient_section = q007n_cycle[
        "coefficient_reproduction_and_norms"
    ]
    audit = {
        "coefficient_section_sha256": q007ac._canonical_json_sha256(
            coefficient_section
        ),
        "working_coefficient_count": len(coefficients),
        "all_working_coefficients_positive": all(
            value > 0 for value in coefficients.values()
        ),
        "working_selected_spectral_radius_upper": _fraction_record(
            selected_radius
        ),
        "q007ae_internal_inverse_upper": _fraction_record(internal),
        "q007n_zero_wave_inverse_upper": _fraction_record(zero),
        "q007ad_external_inverse_upper": _fraction_record(external),
        "q007ae_total_inverse_upper": _fraction_record(q007ae_total),
        "inverse_ordering_reproduced": inverse_ordering,
        "q007ae_candidate_count": len(reproduced_scan["records"]),
        "q007ae_candidate_records_sha256": (
            q007ac._canonical_json_sha256(reproduced_scan["records"])
        ),
        "stored_candidate_records_sha256": (
            q007ac._canonical_json_sha256(stored_scan["records"])
        ),
        "q007ae_candidate_records_reproduced_exactly": records_match,
        "q007ae_radius_boundary_reproduced": boundary_matches,
    }
    passed = bool(
        len(coefficients) == 13
        and all(value > 0 for value in coefficients.values())
        and inverse_ordering
        and len(reproduced_scan["records"]) == len(q007n.CANDIDATE_EXPONENTS)
        and records_match
        and boundary_matches
    )
    audit["passed"] = passed
    return audit, passed


def _witness_obstruction_audit(
    payloads: dict[str, dict[str, Any]],
    beta_maximum: Fraction,
    required_gap: Fraction,
) -> tuple[dict[str, Any], bool]:
    witness = payloads["q007ad"]["cycle"][
        "phase_aware_separation_audit"
    ]["phase"]["minimum_margin_witness"]
    observed_identity = {
        key: witness[key] for key in EXPECTED_WITNESS
    }
    product_center = _complex_fraction_from_record(
        witness["original_product_center"]
    )
    external_center = _complex_fraction_from_record(
        witness["external_center"]
    )
    real_difference = product_center[0] - external_center[0]
    imaginary_difference = product_center[1] - external_center[1]
    reconstructed_distance_squared = (
        real_difference**2 + imaginary_difference**2
    )
    stored_distance_squared = _fraction_from_record(
        witness["distance_squared"]
    )
    uncertainty = _fraction_from_record(
        witness["product_uncertainty_upper"]
    )
    external_radius = _fraction_from_record(witness["external_radius"])
    square_root = _sqrt_bounds(reconstructed_distance_squared)
    allowable_gap_lower = (
        square_root.lower - uncertainty - external_radius
    )
    allowable_gap_upper = (
        square_root.upper - uncertainty - external_radius
    )
    stored_allowable_gap_lower = _fraction_from_record(
        witness["certified_complex_distance_lower"]
    )
    shortfall = required_gap - allowable_gap_upper
    witness_to_required_ratio = allowable_gap_upper / required_gap
    optimistic_raw_inverse = 81 * beta_maximum / allowable_gap_upper
    optimistic_working_inverse = q007n._round_up(
        optimistic_raw_inverse, q007n.MAJORANT_DECIMAL_DIGITS
    )
    optimistic_inverse_ratio = (
        optimistic_raw_inverse / REGISTERED_FAILING_INVERSE
    )
    exact_required_gap_squared_margin = reconstructed_distance_squared - (
        required_gap + uncertainty + external_radius
    ) ** 2
    identity_matches = observed_identity == EXPECTED_WITNESS
    reconstruction_matches = bool(
        reconstructed_distance_squared == stored_distance_squared
        and allowable_gap_lower == stored_allowable_gap_lower
    )
    obstruction_passed = bool(
        identity_matches
        and reconstruction_matches
        and square_root.width <= SQRT_ENCLOSURE_WIDTH
        and allowable_gap_upper > 0
        and allowable_gap_upper < required_gap
        and witness_to_required_ratio
        < MAXIMUM_WITNESS_TO_REQUIRED_RATIO
        and shortfall > MINIMUM_GAP_SHORTFALL
        and optimistic_raw_inverse > REGISTERED_FAILING_INVERSE
        and optimistic_inverse_ratio > MINIMUM_OPTIMISTIC_INVERSE_RATIO
        and exact_required_gap_squared_margin < 0
    )
    audit = {
        "witness_identity": observed_identity,
        "registered_witness_identity": EXPECTED_WITNESS,
        "witness_identity_matches": identity_matches,
        "counts_sum_to_degree": (
            sum(witness["counts"]) == witness["degree"]
        ),
        "reconstructed_center_distance_squared": _fraction_record(
            reconstructed_distance_squared
        ),
        "stored_center_distance_squared": _fraction_record(
            stored_distance_squared
        ),
        "center_distance_squared_reproduced": (
            reconstructed_distance_squared == stored_distance_squared
        ),
        "product_uncertainty_upper": _fraction_record(uncertainty),
        "external_radius": _fraction_record(external_radius),
        "sqrt_center_distance_lower": _fraction_record(square_root.lower),
        "sqrt_center_distance_upper": _fraction_record(square_root.upper),
        "sqrt_enclosure_width": _fraction_record(square_root.width),
        "registered_maximum_sqrt_enclosure_width": _fraction_record(
            SQRT_ENCLOSURE_WIDTH
        ),
        "allowable_gap_lower": _fraction_record(allowable_gap_lower),
        "allowable_gap_upper": _fraction_record(allowable_gap_upper),
        "stored_allowable_gap_lower": _fraction_record(
            stored_allowable_gap_lower
        ),
        "stored_allowable_gap_lower_reproduced": (
            allowable_gap_lower == stored_allowable_gap_lower
        ),
        "required_gap_lower": _fraction_record(required_gap),
        "absolute_gap_shortfall": _fraction_record(shortfall),
        "witness_to_required_gap_ratio": _fraction_record(
            witness_to_required_ratio
        ),
        "registered_maximum_witness_to_required_ratio": _fraction_record(
            MAXIMUM_WITNESS_TO_REQUIRED_RATIO
        ),
        "exact_required_gap_squared_margin": _fraction_record(
            exact_required_gap_squared_margin
        ),
        "required_gap_fails_even_without_threshold_rounding": (
            exact_required_gap_squared_margin < 0
        ),
        "optimistic_raw_external_inverse_floor": _fraction_record(
            optimistic_raw_inverse
        ),
        "optimistic_working_external_inverse_floor": _fraction_record(
            optimistic_working_inverse
        ),
        "optimistic_inverse_to_failing_endpoint_ratio": _fraction_record(
            optimistic_inverse_ratio
        ),
        "single_witness_obstructs_required_uniform_gap": (
            obstruction_passed
        ),
        "full_phase_reenumeration_needed": False,
        "passed": obstruction_passed,
    }
    return audit, obstruction_passed


def run_radius_step_obstruction_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        _default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    payloads, input_records = _load_registered_inputs(directory)
    implementation_audit = _implementation_source_audit()
    q007n_cycle = payloads["q007n"]["cycle"]
    q007n_spectral = q007n_cycle["spectral_separation_and_inverse"]
    coefficients = q007o._working_coefficients_from_q007n(q007n_cycle)
    selected_radius = _fraction_from_record(
        q007n_spectral["working_selected_spectral_radius_upper"]
    )
    beta_maximum = _fraction_from_record(
        q007n_spectral["working_maximum_beta_upper"]
    )
    polynomials = q007n._scalar_majorant_polynomials(
        coefficients, selected_radius
    )

    majorant_audit, majorant_passed = _majorant_reproduction_audit(
        payloads, coefficients, selected_radius
    )
    threshold_audit, endpoints = _integer_inverse_threshold_audit(
        coefficients, selected_radius, polynomials
    )
    monotonicity_audit, monotonicity_passed = _monotonicity_audit(
        coefficients, selected_radius, polynomials, endpoints
    )
    required_gap = (
        81 * beta_maximum / REGISTERED_FAILING_INVERSE
    )
    raw_inverse_at_required_gap = 81 * beta_maximum / required_gap
    working_inverse_at_required_gap = q007n._round_up(
        raw_inverse_at_required_gap, q007n.MAJORANT_DECIMAL_DIGITS
    )
    q007ad_gap = _fraction_from_record(
        payloads["q007ad"]["cycle"]["phase_aware_separation_audit"][
            "phase"
        ]["target_phase_gap"]
    )
    required_gap_audit = {
        "external_inverse_formula": "81 * beta_maximum / phase_gap",
        "q007n_working_beta_maximum": _fraction_record(beta_maximum),
        "registered_failing_inverse_endpoint": _fraction_record(
            Fraction(REGISTERED_FAILING_INVERSE)
        ),
        "necessary_external_gap_lower": _fraction_record(required_gap),
        "necessary_condition": (
            "candidate pass requires total inverse < failing endpoint, "
            "so a phase-gap certificate must satisfy gap > "
            "81*beta_maximum/failing_endpoint"
        ),
        "raw_inverse_at_necessary_gap": _fraction_record(
            raw_inverse_at_required_gap
        ),
        "working_inverse_at_necessary_gap": _fraction_record(
            working_inverse_at_required_gap
        ),
        "integer_endpoint_is_fixed_by_decimal_rounding": bool(
            raw_inverse_at_required_gap
            == REGISTERED_FAILING_INVERSE
            and working_inverse_at_required_gap
            == REGISTERED_FAILING_INVERSE
        ),
        "q007ad_registered_phase_gap": _fraction_record(q007ad_gap),
        "necessary_to_registered_gap_ratio": _fraction_record(
            required_gap / q007ad_gap
        ),
    }
    witness_audit, witness_passed = _witness_obstruction_audit(
        payloads, beta_maximum, required_gap
    )
    q007ae_consequence = payloads["q007ae"]["cycle"][
        "theorem_consequence"
    ]
    preservation_audit = {
        "q007ae_1e_minus_16_radius_preserved": bool(
            q007ae_consequence[
                "q007ad_explicit_radius_1e_minus_16_preserved"
            ]
            and majorant_audit["q007ae_radius_boundary_reproduced"]
        ),
        "q007ae_1e_minus_15_candidate_still_fails": bool(
            threshold_audit["failing_endpoint"]["candidate_record"][
                "modal_radius_decimal"
            ]
            == "1e-15"
            and not threshold_audit["failing_endpoint"][
                "candidate_record"
            ]["passed"]
        ),
        "q007p_through_q007ab_tube_constants_enlarged": bool(
            q007ae_consequence[
                "q007p_through_q007ab_tube_constants_enlarged"
            ]
        ),
        "q007ad_external_certificate_changed": False,
        "q007ae_internal_certificate_changed": False,
        "only_obstruction_audited": True,
    }

    registered_parameters = {
        "target_candidate_exponent": TARGET_CANDIDATE_EXPONENT,
        "search_inverse_interval": [
            SEARCH_INVERSE_LOWER,
            SEARCH_INVERSE_UPPER,
        ],
        "registered_passing_inverse": REGISTERED_PASSING_INVERSE,
        "registered_failing_inverse": REGISTERED_FAILING_INVERSE,
        "maximum_witness_to_required_ratio": _fraction_record(
            MAXIMUM_WITNESS_TO_REQUIRED_RATIO
        ),
        "minimum_gap_shortfall": _fraction_record(MINIMUM_GAP_SHORTFALL),
        "minimum_optimistic_inverse_ratio": _fraction_record(
            MINIMUM_OPTIMISTIC_INVERSE_RATIO
        ),
        "sqrt_decimal_digits": 100,
        "expected_witness": EXPECTED_WITNESS,
    }
    input_digest = q007ac._canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "implementation_source_audit": implementation_audit,
            "registered_parameters": registered_parameters,
        }
    )
    result_sections = {
        "majorant_reproduction_audit": majorant_audit,
        "integer_inverse_threshold_audit": threshold_audit,
        "monotonicity_audit": monotonicity_audit,
        "required_external_gap_audit": required_gap_audit,
        "witness_obstruction_audit": witness_audit,
        "preservation_audit": preservation_audit,
    }
    result_digest = q007ac._canonical_json_sha256(result_sections)
    finite_strict_json = bool(
        _all_numeric_values_finite(result_sections)
        and _strict_json_serializable(result_sections)
    )

    input_passed = all(record["passed"] for record in input_records.values())
    implementation_passed = implementation_audit[
        "all_registered_implementation_sha256_match"
    ]
    threshold_passed = bool(
        threshold_audit["complete"]
        and threshold_audit["registered_bracket_reproduced"]
    )
    witness_validity = bool(
        witness_audit["witness_identity_matches"]
        and witness_audit["counts_sum_to_degree"]
        and witness_audit["center_distance_squared_reproduced"]
        and witness_audit["stored_allowable_gap_lower_reproduced"]
        and _fraction_from_record(
            witness_audit["sqrt_enclosure_width"]
        )
        <= SQRT_ENCLOSURE_WIDTH
    )
    validity_gates = {
        "sealed_artifacts_source_scope_and_digests": {
            "passed": input_passed,
            "threshold": (
                "three artifact and runner SHA values, common scope, "
                "accepted outcomes, classifications, and sealed digests "
                "match"
            ),
            "value": {
                "accepted_input_count": sum(
                    record["passed"] for record in input_records.values()
                ),
                "expected_input_count": len(input_records),
            },
        },
        "sealed_implementation_sources": {
            "passed": implementation_passed,
            "threshold": "all five registered implementation SHA values match",
            "value": {
                "matching_source_count": sum(
                    record["passed"]
                    for record in implementation_audit["records"].values()
                ),
                "expected_source_count": len(
                    implementation_audit["records"]
                ),
            },
        },
        "q007n_majorant_and_q007ae_boundary_reproduced": {
            "passed": majorant_passed,
            "threshold": (
                "13 positive coefficients, inverse ordering, all 119 "
                "candidate records, and 1e-16/1e-15 boundary match"
            ),
            "value": {
                "working_coefficient_count": majorant_audit[
                    "working_coefficient_count"
                ],
                "candidate_count": majorant_audit[
                    "q007ae_candidate_count"
                ],
                "records_match": majorant_audit[
                    "q007ae_candidate_records_reproduced_exactly"
                ],
            },
        },
        "integer_inverse_bisection_complete": {
            "passed": threshold_passed,
            "threshold": (
                "exact bisection from [1,1e13] ends at the registered "
                "unit-width pass/fail bracket"
            ),
            "value": {
                "passing": threshold_audit[
                    "maximum_passing_integer_inverse"
                ],
                "failing": threshold_audit[
                    "minimum_failing_integer_inverse"
                ],
                "width": threshold_audit["final_integer_width"],
            },
        },
        "exact_monotonicity_and_witness_reconstruction": {
            "passed": monotonicity_passed and witness_validity,
            "threshold": (
                "positive-domain monotonicity and radii identity hold; "
                "sealed witness and 100-digit sqrt enclosure reproduce"
            ),
            "value": {
                "monotonicity_passed": monotonicity_passed,
                "witness_validity": witness_validity,
                "sqrt_width": witness_audit["sqrt_enclosure_width"][
                    "float"
                ],
            },
        },
        "finite_strict_json_and_deterministic_digests": {
            "passed": finite_strict_json,
            "threshold": (
                "all result sections are finite strict JSON and emit "
                "canonical input/result digests"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest,
                "result_digest_sha256": result_digest,
            },
        },
    }
    study_validity = (
        "passed"
        if all(gate["passed"] for gate in validity_gates.values())
        else "failed"
    )

    hypothesis_gates = {
        "unit_width_inverse_threshold_crossing": {
            "passed": bool(
                threshold_passed
                and endpoints["passing"]["passed"]
                and not endpoints["failing"]["passed"]
                and _required_fraction(
                    endpoints["passing"], "contraction_bound"
                )
                < q007n.MAXIMUM_CONTRACTION
                < _required_fraction(
                    endpoints["failing"], "contraction_bound"
                )
                and _required_fraction(
                    endpoints["passing"], "radii_margin"
                )
                > 0
                > _required_fraction(
                    endpoints["failing"], "radii_margin"
                )
            ),
            "threshold": (
                "passing endpoint has Z<1/2 and positive radii margin; "
                "adjacent failing endpoint has Z>1/2 and negative margin"
            ),
            "value": {
                "passing_z": monotonicity_audit[
                    "passing_contraction_bound"
                ]["float"],
                "failing_z": monotonicity_audit[
                    "failing_contraction_bound"
                ]["float"],
            },
        },
        "all_larger_inverse_values_fail": {
            "passed": monotonicity_audit[
                "all_inverse_at_or_above_failing_endpoint_fail"
            ],
            "threshold": (
                "exact structural signs and formulas prove monotone Z "
                "on the positive domain; leaving the domain also fails"
            ),
            "value": monotonicity_audit[
                "all_inverse_at_or_above_failing_endpoint_fail"
            ],
        },
        "sealed_witness_gap_shortfall": {
            "passed": bool(
                witness_passed
                and _fraction_from_record(
                    witness_audit["witness_to_required_gap_ratio"]
                )
                < MAXIMUM_WITNESS_TO_REQUIRED_RATIO
                and _fraction_from_record(
                    witness_audit["absolute_gap_shortfall"]
                )
                > MINIMUM_GAP_SHORTFALL
            ),
            "threshold": (
                "sqrt-upper witness gap is below the necessary gap, "
                "ratio <0.95, and absolute shortfall >1.4e-9"
            ),
            "value": {
                "allowable_gap_upper": witness_audit[
                    "allowable_gap_upper"
                ]["float"],
                "required_gap": required_gap_audit[
                    "necessary_external_gap_lower"
                ]["float"],
                "ratio": witness_audit[
                    "witness_to_required_gap_ratio"
                ]["float"],
                "shortfall": witness_audit[
                    "absolute_gap_shortfall"
                ]["float"],
            },
        },
        "optimistic_external_inverse_still_too_large": {
            "passed": bool(
                _fraction_from_record(
                    witness_audit[
                        "optimistic_raw_external_inverse_floor"
                    ]
                )
                > REGISTERED_FAILING_INVERSE
                and _fraction_from_record(
                    witness_audit[
                        "optimistic_inverse_to_failing_endpoint_ratio"
                    ]
                )
                > MINIMUM_OPTIMISTIC_INVERSE_RATIO
            ),
            "threshold": (
                "even the sqrt-upper optimistic inverse floor exceeds "
                "the failing endpoint by a factor >1.05"
            ),
            "value": {
                "optimistic_inverse": witness_audit[
                    "optimistic_raw_external_inverse_floor"
                ]["float"],
                "ratio": witness_audit[
                    "optimistic_inverse_to_failing_endpoint_ratio"
                ]["float"],
            },
        },
        "q007ae_boundary_and_downstream_scope_preserved": {
            "passed": bool(
                preservation_audit[
                    "q007ae_1e_minus_16_radius_preserved"
                ]
                and preservation_audit[
                    "q007ae_1e_minus_15_candidate_still_fails"
                ]
                and not preservation_audit[
                    "q007p_through_q007ab_tube_constants_enlarged"
                ]
                and preservation_audit["only_obstruction_audited"]
            ),
            "threshold": (
                "Q007ae 1e-16 pass/1e-15 fail remains and no downstream "
                "tube or MPFR constant is enlarged"
            ),
            "value": preservation_audit,
        },
    }
    all_hypotheses = all(
        gate["passed"] for gate in hypothesis_gates.values()
    )
    if study_validity != "passed":
        hypothesis_outcome = "inconclusive"
        classification = (
            "radius-step obstruction audit invalid; prior certificates "
            "remain unchanged"
        )
    elif all_hypotheses:
        hypothesis_outcome = "accepted"
        classification = (
            "sealed external phase-disc family cannot certify the "
            "1e-15 radius step"
        )
    else:
        hypothesis_outcome = "not_certified"
        classification = (
            "sealed witness does not obstruct the 1e-15 radius step"
        )

    return {
        "question": (
            "Can any gap certified by the sealed Q007ad original-disc "
            "comparison family reduce the Q007ae total inverse enough "
            "for the 1e-15 modal-radius candidate?"
        ),
        "registered_parameters": registered_parameters,
        "input_artifacts": input_records,
        "implementation_source_audit": implementation_audit,
        **result_sections,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": study_validity,
        "hypothesis_outcome": hypothesis_outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "sealed_q007ad_disc_family_obstructs_1e_minus_15": bool(
                study_validity == "passed" and all_hypotheses
            ),
            "q007ae_explicit_radius_1e_minus_16_preserved": bool(
                preservation_audit[
                    "q007ae_1e_minus_16_radius_preserved"
                ]
            ),
            "true_analytic_radius_upper_bound_proved": False,
            "alternative_norm_or_spectral_certificate_excluded": False,
            "q007p_through_q007ab_tube_constants_enlarged": False,
        },
        "claim_boundary": (
            "An accepted result excludes the next decimal radius only "
            "within the simultaneous use of the Q007n scalar majorant, "
            "Q007ad original asymmetric discs, and Q007ad norm formula. "
            "It is not an upper bound on the true spectral separation or "
            "analytic radius and does not exclude wave-sum, blockwise, "
            "alternative-norm, higher-order, or sharper spectral proofs. "
            "No downstream tube, MPFR, Euclidean, grid-uniform, global, "
            "boundary, forcing, or D3Q27 claim is changed."
        ),
        "preserved_prior_outcomes": {
            "q007ad_external_phase_certificate_changed": False,
            "q007ae_internal_phase_certificate_changed": False,
            "q007ae_explicit_radius_changed": False,
            "q007p_through_q007ab_tube_results_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q010_sparse_cost_dominance_changed": False,
        },
        "next_change": (
            "Do not continue scalar gap micro-sharpening inside the same "
            "Q007ad disc family. Separately preregister a Q007p-style "
            "downstream tube re-audit using the certified 1e-16 chart "
            "domain, or introduce a structurally different blockwise or "
            "wave-sum external certificate."
        ),
    }


def run_q007af_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_radius_step_obstruction_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "exact inverse-threshold and sealed-witness "
                "radius-step obstruction audit"
            ),
            "construction_grid": [SIZE, SIZE],
            "omega": OMEGA,
            "eta": ETA,
            "conservation_treatment": (
                "fixed global mass and momentum leaf"
            ),
            "selected_real_dimension": SELECTED_COMPLEX_DIMENSION,
            "selected_complex_dimension": SELECTED_COMPLEX_DIMENSION,
            "claim": (
                "certificate-family obstruction only; no true analytic-"
                "radius upper bound or downstream tube enlargement"
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
    result = run_q007af_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
