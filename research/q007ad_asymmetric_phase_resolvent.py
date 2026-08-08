"""Sealed Q007ad asymmetric-disc critical phase certificate.

The invalid Q007ac result is preserved.  This follow-up uses the six original
Q007h1 selected eigenvalue discs, fixes the target gap above the exact Q007o
internal-inverse critical gap, and changes only the nonzero nonselected-output
resolvent in the Q007o radius scan.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
from typing import Any

import research.q007ac_phase_aware_resolvent as q007ac
from research.q007n_explicit_local_radius import (
    CANDIDATE_EXPONENTS,
    MAJORANT_DECIMAL_DIGITS,
    MAXIMUM_CONTRACTION,
    _round_up,
)
from research.q007o_external_complement_radius import (
    _radius_scan,
    _working_coefficients_from_q007n,
)
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import (
    _all_numeric_values_finite,
    _file_sha256,
    _fraction_record,
    _strict_json_serializable,
)

SIZE = 17
OMEGA = 1.5
ETA = 0.01
SELECTED_COMPLEX_DIMENSION = 24
REPRESENTATIVE_COUNT = 72
TARGET_DISC_COUNT = 630
SCREEN_LOG_GAP = Fraction(1, 10**6)
PHASE_GAP = Fraction(21, 10**9)
PHASE_THRESHOLD_OUTWARD_BINARY_BITS = 256
MINIMUM_TOTAL_IMPROVEMENT_FACTOR = Fraction(100)
EXPECTED_DANGEROUS_AGGREGATE_COUNT = 826
EXPECTED_DANGEROUS_EXPANDED_PRODUCT_COUNT = 108_273
EXPECTED_PHASE_COMPARISON_COUNT = 287_929

REGISTERED_CRITICAL_GAP_NUMERATOR = int(
    "137064b41f6973f11f3f0d50cba3d16b9eacb4ae5b8d89232971db9f7ebae6994c7dad",
    16,
)
REGISTERED_CRITICAL_GAP_DENOMINATOR = int(
    "3964a0243f0d52700d16c0516ff99b6188ae3fabc5034ea22cf4ab1268f148a006530509af97",
    16,
)
REGISTERED_CRITICAL_GAP = Fraction(
    REGISTERED_CRITICAL_GAP_NUMERATOR,
    REGISTERED_CRITICAL_GAP_DENOMINATOR,
)

Q007AC_ARTIFACT_FILENAME = "q007ac_phase_aware_resolvent.json"
Q007AC_ARTIFACT_SHA256 = (
    "b3c9d99088492bf157cbb651d958597573a9c7b5386a189b6b9e4ee5d88dbcf5"
)
Q007AC_RUNNER_SHA256 = (
    "8c2757c4c3771007dc15135bc407551bbef74906294ab897b1a4f251d5abe2ae"
)
Q007AC_INPUT_DIGEST = (
    "15166f90e39b132c0d6956b7a14f821095cc1b31da9d9e83b9b3f5b9cf3314b9"
)
Q007AC_RESULT_DIGEST = (
    "369809e953652c9e99ade3553e2754a06c1b0add52549e2f53dbcdb0ab15f018"
)
Q007AC_PHASE_DIGEST = (
    "5039563c60ab57b85b683b324506049535372847b1a5adef3362da2b16a954ab"
)


def _runner_source_metadata() -> dict[str, str]:
    path = Path(__file__).resolve()
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }


def _load_registered_inputs(
    directory: Path,
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, Any],
    dict[str, Any],
]:
    payloads, input_records = q007ac._load_registered_inputs(directory)
    q007ac_path = directory / Q007AC_ARTIFACT_FILENAME
    q007ac_payload = json.loads(q007ac_path.read_text(encoding="utf-8"))
    cycle = q007ac_payload.get("cycle", {})
    scope = q007ac_payload.get("mathematical_scope", {})
    runner_path = Path(q007ac.__file__).resolve()
    observed_artifact_sha = _file_sha256(q007ac_path)
    observed_runner_sha = _file_sha256(runner_path)
    failed_validity = [
        name
        for name, gate in cycle.get("validity_gates", {}).items()
        if not gate.get("passed", False)
    ]
    failed_hypotheses = [
        name
        for name, gate in cycle.get("hypothesis_gates", {}).items()
        if not gate.get("passed", False)
    ]
    q007ac_record = {
        "filename": Q007AC_ARTIFACT_FILENAME,
        "sha256": observed_artifact_sha,
        "registered_sha256": Q007AC_ARTIFACT_SHA256,
        "sha256_matches": observed_artifact_sha == Q007AC_ARTIFACT_SHA256,
        "runner_filename": runner_path.name,
        "runner_sha256": observed_runner_sha,
        "registered_runner_sha256": Q007AC_RUNNER_SHA256,
        "runner_sha256_matches": observed_runner_sha == Q007AC_RUNNER_SHA256,
        "source_match": q007ac_payload.get("source") == source_metadata(),
        "scope_match": bool(
            scope.get("construction_grid") == [SIZE, SIZE]
            and float(scope.get("omega")) == OMEGA
            and float(scope.get("eta")) == ETA
        ),
        "study_gate": q007ac_payload.get("study_gate"),
        "scientific_outcome": q007ac_payload.get("scientific_outcome"),
        "scientific_classification": cycle.get("scientific_classification"),
        "failed_validity_gates": failed_validity,
        "failed_hypothesis_gates": failed_hypotheses,
        "input_digest_sha256": cycle.get("input_digest_sha256"),
        "result_digest_sha256": cycle.get("result_digest_sha256"),
        "phase_comparison_digest_sha256": cycle.get(
            "phase_aware_separation_audit", {}
        )
        .get("phase", {})
        .get("comparison_digest_sha256"),
    }
    q007ac_record["passed"] = bool(
        q007ac_record["sha256_matches"]
        and q007ac_record["runner_sha256_matches"]
        and q007ac_record["source_match"]
        and q007ac_record["scope_match"]
        and q007ac_record["study_gate"] == "failed"
        and q007ac_record["scientific_outcome"] == "inconclusive"
        and q007ac_record["scientific_classification"]
        == "registered Q007ac phase-aware audit invalid"
        and failed_validity == ["spectral_disc_reconstruction"]
        and failed_hypotheses == ["registered_phase_gap_certified"]
        and q007ac_record["input_digest_sha256"] == Q007AC_INPUT_DIGEST
        and q007ac_record["result_digest_sha256"] == Q007AC_RESULT_DIGEST
        and q007ac_record["phase_comparison_digest_sha256"]
        == Q007AC_PHASE_DIGEST
    )
    return payloads, input_records, q007ac_payload, q007ac_record


def _implementation_source_audit() -> dict[str, Any]:
    audit = q007ac._implementation_source_audit()
    records = dict(audit["records"])
    runner_path = Path(q007ac.__file__).resolve()
    observed = _file_sha256(runner_path)
    records["q007ac"] = {
        "path": "research/q007ac_phase_aware_resolvent.py",
        "sha256": observed,
        "registered_sha256": Q007AC_RUNNER_SHA256,
        "passed": observed == Q007AC_RUNNER_SHA256,
    }
    return {
        "records": records,
        "all_registered_implementation_sha256_match": all(
            record["passed"] for record in records.values()
        ),
    }


def _original_selected_discs(
    representatives: tuple[Any, ...],
    selected_radius_upper: Fraction,
) -> tuple[dict[str, q007ac._NominalDisc], dict[str, Any], bool]:
    by_wave = {proof.wave_index: proof for proof in representatives}
    discs: dict[str, q007ac._NominalDisc] = {}
    representative_records = []
    indices_match = True
    all_within = True
    for family, registration in q007ac.SELECTED_REPRESENTATIVES.items():
        proof = by_wave[registration["wave_index"]]
        acoustic_indices = registration["acoustic_indices"]
        shear_index = registration["shear_index"]
        indices_match = indices_match and set(proof.selected_indices) == {
            *acoustic_indices,
            shear_index,
        }
        registrations = (
            ("acoustic_positive", acoustic_indices[0]),
            ("acoustic_negative", acoustic_indices[1]),
            ("shear", shear_index),
        )
        family_records = []
        for branch, eigenvalue_index in registrations:
            name = f"{family}_{branch}"
            center = q007ac._complex_fraction(
                proof.eigenvalues[eigenvalue_index]
            )
            disc = q007ac._NominalDisc(
                name=name,
                center=center,
                radius=proof.radius,
                original_center=center,
                original_radius=proof.radius,
            )
            discs[name] = disc
            modulus_radius_upper = (
                q007ac._modulus_upper(center) + proof.radius
            )
            within = modulus_radius_upper <= selected_radius_upper
            all_within = all_within and within
            family_records.append(
                {
                    "name": name,
                    "eigenvalue_index": eigenvalue_index,
                    "center": q007ac._complex_fraction_record(center),
                    "radius": _fraction_record(proof.radius),
                    "modulus_plus_radius_upper": _fraction_record(
                        modulus_radius_upper
                    ),
                    "slack_to_q007n_working_sigma": _fraction_record(
                        selected_radius_upper - modulus_radius_upper
                    ),
                    "within_q007n_working_sigma": within,
                }
            )
        representative_records.append(
            {
                "family": family,
                "wave_index": list(proof.wave_index),
                "selected_indices": list(proof.selected_indices),
                "registered_acoustic_indices": list(acoustic_indices),
                "registered_shear_index": shear_index,
                "proof_digest_matches": proof.digest_matches,
                "discs": family_records,
            }
        )
    factor_upper = selected_radius_upper
    maximum_original_disc_upper = max(
        q007ac._modulus_upper(disc.center) + disc.radius
        for disc in discs.values()
    )
    paired_radii_equal = bool(
        discs["axis_acoustic_positive"].radius
        == discs["axis_acoustic_negative"].radius
        and discs["diagonal_acoustic_positive"].radius
        == discs["diagonal_acoustic_negative"].radius
    )
    passed = bool(
        len(discs) == 6
        and indices_match
        and all_within
        and paired_radii_equal
        and all(proof.digest_matches for proof in representatives)
    )
    audit = {
        "disc_construction": (
            "six original Q007h1 dyadic centers and representative "
            "Bauer--Fike radii; no recentering or inflation"
        ),
        "representative_records": representative_records,
        "original_selected_discs": {
            name: {
                "center": q007ac._complex_fraction_record(disc.center),
                "radius": _fraction_record(disc.radius),
            }
            for name, disc in discs.items()
        },
        "selected_index_registration_matches": indices_match,
        "all_original_discs_within_q007n_working_sigma": all_within,
        "paired_acoustic_radii_equal": paired_radii_equal,
        "disc_count": len(discs),
        "c4_selected_mode_coverage": SELECTED_COMPLEX_DIMENSION,
        "maximum_original_disc_modulus_upper": _fraction_record(
            maximum_original_disc_upper
        ),
        "q007n_working_product_factor_modulus_upper": _fraction_record(
            factor_upper
        ),
        "product_factor_modulus_inflation_over_q007n": _fraction_record(
            Fraction(0)
        ),
        "minimum_sigma_slack": _fraction_record(
            selected_radius_upper - maximum_original_disc_upper
        ),
    }
    return discs, audit, passed


def _phase_certificate(
    dangerous: tuple[q007ac._DangerousAggregate, ...],
    discs: dict[str, q007ac._NominalDisc],
    targets: tuple[q007ac._TargetDisc, ...],
    product_factor_modulus_upper: Fraction,
) -> tuple[dict[str, Any], bool]:
    target_lookup = {target.identifier: target for target in targets}
    dyadic_targets = {
        target.identifier: q007ac._dyadic_complex(target.center)
        for target in targets
    }
    maximum_degree = 89
    dyadic_discs = {
        name: q007ac._dyadic_complex(disc.center)
        for name, disc in discs.items()
    }
    powers = {
        name: q007ac._dyadic_power_table(value, maximum_degree)
        for name, value in dyadic_discs.items()
    }
    acoustic_products = {
        "axis": tuple(
            tuple(
                q007ac._dyadic_multiply(
                    powers["axis_acoustic_positive"][positive],
                    powers["axis_acoustic_negative"][total - positive],
                )
                for positive in range(total + 1)
            )
            for total in range(maximum_degree + 1)
        ),
        "diagonal": tuple(
            tuple(
                q007ac._dyadic_multiply(
                    powers["diagonal_acoustic_positive"][positive],
                    powers["diagonal_acoustic_negative"][total - positive],
                )
                for positive in range(total + 1)
            )
            for total in range(maximum_degree + 1)
        ),
    }
    digest = sha256()
    digest_header = {
        "phase_gap": _fraction_record(PHASE_GAP),
        "product_factor_modulus_upper": _fraction_record(
            product_factor_modulus_upper
        ),
        "original_selected_discs": {
            name: {
                "center": q007ac._complex_fraction_record(disc.center),
                "radius": _fraction_record(disc.radius),
            }
            for name, disc in discs.items()
        },
        "dangerous": [
            {
                "degree": aggregate.degree,
                "counts": list(aggregate.counts),
                "external_identifiers": list(
                    aggregate.external_identifiers
                ),
            }
            for aggregate in dangerous
        ],
    }
    digest.update(
        q007ac._canonical_json_sha256(digest_header).encode("ascii")
    )
    digest.update(b"\0")

    comparison_count = 0
    expanded_count = 0
    failed_count = 0
    minimum_margin: q007ac._DyadicScalar | None = None
    minimum_context: dict[str, Any] | None = None
    maximum_product_uncertainty = Fraction(0)
    maximum_threshold_rounding_increment = Fraction(0)

    for aggregate in dangerous:
        aa, axis_shear, da, diagonal_shear = aggregate.counts
        uncertainty = product_factor_modulus_upper ** (
            aggregate.degree - 1
        ) * (
            aa * discs["axis_acoustic_positive"].radius
            + axis_shear * discs["axis_shear"].radius
            + da * discs["diagonal_acoustic_positive"].radius
            + diagonal_shear * discs["diagonal_shear"].radius
        )
        maximum_product_uncertainty = max(
            maximum_product_uncertainty, uncertainty
        )
        thresholds = {}
        for identifier in aggregate.external_identifiers:
            exact_threshold = (
                PHASE_GAP
                + uncertainty
                + target_lookup[identifier].radius
            )
            working_threshold = q007ac._round_fraction_up_to_dyadic(
                exact_threshold,
                PHASE_THRESHOLD_OUTWARD_BINARY_BITS,
            )
            working_threshold_fraction = q007ac._dyadic_to_fraction(
                working_threshold
            )
            maximum_threshold_rounding_increment = max(
                maximum_threshold_rounding_increment,
                working_threshold_fraction - exact_threshold,
            )
            thresholds[identifier] = (
                exact_threshold**2,
                q007ac._square_dyadic(working_threshold),
            )

        shear_product = q007ac._dyadic_multiply(
            powers["axis_shear"][axis_shear],
            powers["diagonal_shear"][diagonal_shear],
        )
        for axis_positive in range(aa + 1):
            axis_negative = aa - axis_positive
            axis_product = acoustic_products["axis"][aa][axis_positive]
            for diagonal_positive in range(da + 1):
                diagonal_negative = da - diagonal_positive
                diagonal_product = acoustic_products["diagonal"][da][
                    diagonal_positive
                ]
                center = q007ac._dyadic_multiply(
                    shear_product,
                    q007ac._dyadic_multiply(
                        axis_product, diagonal_product
                    ),
                )
                expanded_count += 1
                for identifier in aggregate.external_identifiers:
                    target = target_lookup[identifier]
                    distance_squared = q007ac._dyadic_squared_distance(
                        center, dyadic_targets[identifier]
                    )
                    (
                        exact_threshold_squared,
                        working_threshold_squared,
                    ) = thresholds[identifier]
                    margin = q007ac._subtract_dyadic(
                        distance_squared, working_threshold_squared
                    )
                    passed = margin.numerator > 0
                    comparison_count += 1
                    if not passed:
                        failed_count += 1
                    magnitude = abs(margin.numerator).to_bytes(
                        max(1, (abs(margin.numerator).bit_length() + 7) // 8),
                        byteorder="big",
                    )
                    digest.update(b"\x01" if margin.numerator < 0 else b"\x00")
                    digest.update(len(magnitude).to_bytes(4, byteorder="big"))
                    digest.update(magnitude)
                    digest.update(
                        margin.denominator_exponent.to_bytes(
                            4, byteorder="big"
                        )
                    )
                    if minimum_margin is None or q007ac._dyadic_less(
                        margin, minimum_margin
                    ):
                        minimum_margin = margin
                        minimum_context = {
                            "degree": aggregate.degree,
                            "counts": list(aggregate.counts),
                            "axis_acoustic_positive_count": axis_positive,
                            "axis_acoustic_negative_count": axis_negative,
                            "diagonal_acoustic_positive_count": (
                                diagonal_positive
                            ),
                            "diagonal_acoustic_negative_count": (
                                diagonal_negative
                            ),
                            "external_identifier": identifier,
                            "_center": center,
                            "_external_center": target.center,
                            "_uncertainty": uncertainty,
                            "_external_radius": target.radius,
                            "_distance_squared": distance_squared,
                            "_exact_threshold_squared": (
                                exact_threshold_squared
                            ),
                            "_working_threshold_squared": (
                                working_threshold_squared
                            ),
                        }

    expected_expanded = sum(
        aggregate.expanded_product_count for aggregate in dangerous
    )
    expected_comparisons = sum(
        aggregate.comparison_count for aggregate in dangerous
    )
    complete = bool(
        expanded_count == expected_expanded
        and comparison_count == expected_comparisons
        and minimum_margin is not None
        and minimum_context is not None
    )
    passed = bool(
        complete and failed_count == 0 and minimum_margin.numerator > 0
    )
    minimum_witness = None
    minimum_margin_fraction = Fraction(0)
    if minimum_context is not None and minimum_margin is not None:
        minimum_margin_fraction = q007ac._dyadic_to_fraction(minimum_margin)
        distance_squared_fraction = q007ac._dyadic_to_fraction(
            minimum_context["_distance_squared"]
        )
        certified_distance_lower = (
            q007ac._sqrt_bounds(distance_squared_fraction).lower
            - minimum_context["_uncertainty"]
            - minimum_context["_external_radius"]
        )
        minimum_witness = {
            key: value
            for key, value in minimum_context.items()
            if not key.startswith("_")
        }
        minimum_witness.update(
            {
                "original_product_center": (
                    q007ac._complex_fraction_record(
                        q007ac._dyadic_to_complex_fraction(
                            minimum_context["_center"]
                        )
                    )
                ),
                "external_center": q007ac._complex_fraction_record(
                    minimum_context["_external_center"]
                ),
                "product_uncertainty_upper": _fraction_record(
                    minimum_context["_uncertainty"]
                ),
                "external_radius": _fraction_record(
                    minimum_context["_external_radius"]
                ),
                "distance_squared": _fraction_record(
                    distance_squared_fraction
                ),
                "exact_threshold_squared": _fraction_record(
                    minimum_context["_exact_threshold_squared"]
                ),
                "working_outward_dyadic_threshold_squared": (
                    _fraction_record(
                        q007ac._dyadic_to_fraction(
                            minimum_context[
                                "_working_threshold_squared"
                            ]
                        )
                    )
                ),
                "squared_margin": _fraction_record(
                    minimum_margin_fraction
                ),
                "certified_complex_distance_lower": _fraction_record(
                    certified_distance_lower
                ),
            }
        )
    return {
        "target_phase_gap": _fraction_record(PHASE_GAP),
        "selected_disc_construction": "original asymmetric Q007h1 discs",
        "product_factor_modulus_upper": _fraction_record(
            product_factor_modulus_upper
        ),
        "dangerous_aggregate_count": len(dangerous),
        "expanded_product_count": expanded_count,
        "expected_expanded_product_count": expected_expanded,
        "comparison_count": comparison_count,
        "expected_comparison_count": expected_comparisons,
        "failed_comparison_count": failed_count,
        "maximum_product_uncertainty_upper": _fraction_record(
            maximum_product_uncertainty
        ),
        "threshold_outward_binary_bits": (
            PHASE_THRESHOLD_OUTWARD_BINARY_BITS
        ),
        "maximum_threshold_rounding_increment": _fraction_record(
            maximum_threshold_rounding_increment
        ),
        "minimum_squared_margin": _fraction_record(
            minimum_margin_fraction
        ),
        "minimum_margin_witness": minimum_witness,
        "comparison_digest_sha256": digest.hexdigest(),
        "complete": complete,
        "all_phase_comparisons_strict": passed,
    }, passed


def run_asymmetric_phase_resolvent_audit(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    directory = (
        q007ac._default_artifact_directory()
        if artifact_directory is None
        else Path(artifact_directory)
    )
    (
        payloads,
        input_records,
        q007ac_payload,
        q007ac_input_audit,
    ) = _load_registered_inputs(directory)
    implementation_audit = _implementation_source_audit()
    q007h1 = payloads["q007h1"]
    q007n_cycle = payloads["q007n"]["cycle"]
    q007o_cycle = payloads["q007o"]["cycle"]
    q007n_spectral = q007n_cycle["spectral_separation_and_inverse"]
    q007o_refinement = q007o_cycle[
        "external_complement_inverse_refinement"
    ]
    q007ac_cycle = q007ac_payload["cycle"]

    representatives, reconstruction = (
        q007ac._rebuild_representative_proofs(q007h1)
    )
    selected_radius_upper = q007ac._fraction_from_record(
        q007n_spectral["working_selected_spectral_radius_upper"]
    )
    discs, disc_audit, discs_passed = _original_selected_discs(
        representatives, selected_radius_upper
    )
    targets, target_audit, targets_passed = (
        q007ac._target_external_discs(representatives)
    )
    selected_types, _unused_external, _classification_internal = (
        q007ac._selected_types_and_external_disks(representatives)
    )
    target_log_inputs = q007ac._target_log_inputs(targets)
    selected_logs, external_logs, logarithms_internal = (
        q007ac._log_enclosures(selected_types, target_log_inputs)
    )
    merged_external = q007ac._merge_external_logs(external_logs)
    dangerous, screen_audit, screen_passed = q007ac._screen_aggregates(
        selected_logs, merged_external
    )
    stored_q007ac_separation = q007ac_cycle[
        "phase_aware_separation_audit"
    ]
    stored_q007ac_screen = stored_q007ac_separation["screen"]
    screen_reproduced = screen_audit == stored_q007ac_screen
    target_reproduced = (
        target_audit == q007ac_cycle["target_external_disc_audit"]
    )
    phase_audit, phase_passed = _phase_certificate(
        dangerous,
        discs,
        targets,
        selected_radius_upper,
    )

    finite_modulus_floor = q007ac._fraction_from_record(
        q007n_spectral["finite_degree_minimum_modulus"]
    )
    safe_absolute_gap = finite_modulus_floor * SCREEN_LOG_GAP
    tail_gap = q007ac._fraction_from_record(
        q007n_spectral["degree_90_tail_absolute_gap_lower"]
    )
    beta_maximum = q007ac._fraction_from_record(
        q007n_spectral["working_maximum_beta_upper"]
    )
    internal_inverse = q007ac._fraction_from_record(
        q007o_refinement["working_internal_pair_inverse_upper"]
    )
    zero_inverse = q007ac._fraction_from_record(
        q007n_spectral["zero_wave_fixed_leaf_inverse_upper"]
    )
    old_total_inverse = q007ac._fraction_from_record(
        q007o_refinement["working_total_pair_inverse_upper"]
    )
    critical_gap = 81 * beta_maximum / internal_inverse
    critical_gap_matches_registration = (
        critical_gap == REGISTERED_CRITICAL_GAP
    )
    target_to_critical_ratio = PHASE_GAP / critical_gap
    raw_external_inverse = 81 * beta_maximum / PHASE_GAP
    working_external_inverse = _round_up(
        raw_external_inverse, MAJORANT_DECIMAL_DIGITS
    )
    raw_total_inverse = max(
        working_external_inverse, internal_inverse, zero_inverse
    )
    working_total_inverse = _round_up(
        raw_total_inverse, MAJORANT_DECIMAL_DIGITS
    )
    total_improvement_factor = old_total_inverse / working_total_inverse

    coefficients = _working_coefficients_from_q007n(q007n_cycle)
    old_scan, _old_exact = _radius_scan(
        coefficients, selected_radius_upper, old_total_inverse
    )
    stored_old_scan = q007o_cycle["radius_comparison"][
        "refined_radius_search"
    ]
    old_records_reproduced = (
        old_scan["records"] == stored_old_scan["records"]
    )
    new_scan, new_exact = _radius_scan(
        coefficients, selected_radius_upper, working_total_inverse
    )
    old_selected = stored_old_scan["selected_candidate"]
    new_selected = new_scan["selected_candidate"]
    previous = new_scan["previous_larger_candidate"]
    old_exponent = int(old_selected["candidate_exponent"])
    old_exact_index = old_exponent - CANDIDATE_EXPONENTS[0]
    old_radius_still_passes = bool(
        new_exact[old_exact_index]["passed"]
    )
    registered_radius_boundary_matches = bool(
        new_selected is not None
        and new_selected["modal_radius_decimal"] == "1e-16"
        and previous is not None
        and previous["modal_radius_decimal"] == "1e-15"
        and not previous["passed"]
    )
    new_boundary_passed = bool(
        registered_radius_boundary_matches
        and new_selected["passed"]
        and new_selected["density_buffer_positive"]
        and new_selected["reduced_range_buffer_positive"]
        and new_selected["contraction_strictly_below_one_half"]
        and new_selected["radii_inequality_strict"]
    )

    logarithms = {
        key: value
        for key, value in logarithms_internal.items()
        if not key.endswith("_exact")
    }
    merged_records = [
        {
            "merged_index": index,
            "lower_scaled_integer": str(interval.lower),
            "upper_scaled_integer": str(interval.upper),
            "source_disc_count": len(interval.identifiers),
            "identifiers": list(interval.identifiers),
        }
        for index, interval in enumerate(merged_external)
    ]
    separation_audit = {
        "log_series_terms": q007ac.LOG_SERIES_TERMS,
        "log_internal_decimal_digits": (
            q007ac.LOG_INTERNAL_DECIMAL_DIGITS
        ),
        "log_final_decimal_digits": q007ac.LOG_FINAL_DECIMAL_DIGITS,
        "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
        "phase_gap": _fraction_record(PHASE_GAP),
        "finite_modulus_floor_reused_from_q007n": _fraction_record(
            finite_modulus_floor
        ),
        "safe_absolute_gap_lower": _fraction_record(safe_absolute_gap),
        "degree_90_tail_gap_reused_from_q007n": _fraction_record(
            tail_gap
        ),
        "safe_screen_exceeds_phase_gap": (
            safe_absolute_gap > PHASE_GAP
        ),
        "tail_exceeds_phase_gap": tail_gap > PHASE_GAP,
        "selected_log_records": logarithms["selected_type_records"],
        "target_external_log_digest_sha256": logarithms[
            "external_disk_log_digest_sha256"
        ],
        "target_log_digest_matches_q007ac": (
            logarithms["external_disk_log_digest_sha256"]
            == stored_q007ac_separation[
                "target_external_log_digest_sha256"
            ]
        ),
        "merged_external_interval_count": len(merged_external),
        "merged_external_intervals": merged_records,
        "screen": screen_audit,
        "q007ac_screen_reproduced_exactly": screen_reproduced,
        "phase": phase_audit,
    }
    critical_gap_audit = {
        "formula": "81 * beta_maximum / q007o_internal_inverse",
        "registered_critical_gap": _fraction_record(
            REGISTERED_CRITICAL_GAP
        ),
        "reconstructed_critical_gap": _fraction_record(critical_gap),
        "critical_gap_matches_registration": (
            critical_gap_matches_registration
        ),
        "registered_target_phase_gap": _fraction_record(PHASE_GAP),
        "target_to_critical_ratio": _fraction_record(
            target_to_critical_ratio
        ),
        "target_strictly_exceeds_critical": PHASE_GAP > critical_gap,
        "working_external_inverse_strictly_below_internal": (
            working_external_inverse < internal_inverse
        ),
    }
    inverse_audit = {
        "norm_formula": "81 * beta_maximum / phase_gap",
        "q007n_working_beta_maximum": _fraction_record(beta_maximum),
        "raw_asymmetric_phase_external_inverse_upper": _fraction_record(
            raw_external_inverse
        ),
        "working_asymmetric_phase_external_inverse_upper": (
            _fraction_record(working_external_inverse)
        ),
        "q007o_working_internal_pair_inverse_upper": _fraction_record(
            internal_inverse
        ),
        "q007n_zero_wave_inverse_upper": _fraction_record(zero_inverse),
        "raw_new_total_pair_inverse_upper": _fraction_record(
            raw_total_inverse
        ),
        "working_new_total_pair_inverse_upper": _fraction_record(
            working_total_inverse
        ),
        "q007o_working_total_pair_inverse_upper": _fraction_record(
            old_total_inverse
        ),
        "total_inverse_improvement_factor": _fraction_record(
            total_improvement_factor
        ),
        "new_total_is_internal_limited": (
            working_total_inverse == internal_inverse
        ),
        "only_external_output_inverse_changed": True,
        "q007ac_counterfactual_inverse_not_reused": True,
    }
    radius_comparison = {
        "q007o_old_candidate_records_reproduced_exactly": (
            old_records_reproduced
        ),
        "q007o_selected_candidate_exponent": old_exponent,
        "q007o_selected_modal_radius_decimal": old_selected[
            "modal_radius_decimal"
        ],
        "q007o_candidate_passes_with_asymmetric_phase_inverse": (
            old_radius_still_passes
        ),
        "registered_radius_boundary_matches": (
            registered_radius_boundary_matches
        ),
        "asymmetric_phase_refined_radius_search": new_scan,
    }

    input_digest = q007ac._canonical_json_sha256(
        {
            "input_artifacts": input_records,
            "q007ac_invalid_input_audit": q007ac_input_audit,
            "implementation_source_audit": implementation_audit,
            "registered_parameters": {
                "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
                "phase_gap": _fraction_record(PHASE_GAP),
                "registered_critical_gap": _fraction_record(
                    REGISTERED_CRITICAL_GAP
                ),
                "phase_threshold_outward_binary_bits": (
                    PHASE_THRESHOLD_OUTWARD_BINARY_BITS
                ),
                "target_disc_count": TARGET_DISC_COUNT,
                "candidate_exponents": list(CANDIDATE_EXPONENTS),
            },
        }
    )
    result_digest = q007ac._canonical_json_sha256(
        {
            "original_selected_disc_audit": disc_audit,
            "target_external_disc_audit": target_audit,
            "critical_gap_audit": critical_gap_audit,
            "separation_summary": {
                "target_external_log_digest_sha256": separation_audit[
                    "target_external_log_digest_sha256"
                ],
                "q007ac_screen_reproduced_exactly": screen_reproduced,
                "screen": {
                    key: value
                    for key, value in screen_audit.items()
                    if key not in {"degree_records", "dangerous_records"}
                },
                "phase": phase_audit,
            },
            "inverse_refinement": inverse_audit,
            "radius_comparison": radius_comparison,
        }
    )

    serializable_sections = {
        "input_artifacts": input_records,
        "q007ac_invalid_input_audit": q007ac_input_audit,
        "implementation_source_audit": implementation_audit,
        "spectral_reconstruction": reconstruction,
        "original_selected_disc_audit": disc_audit,
        "target_external_disc_audit": target_audit,
        "critical_gap_audit": critical_gap_audit,
        "phase_aware_separation_audit": separation_audit,
        "inverse_refinement": inverse_audit,
        "radius_comparison": radius_comparison,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
    }
    finite_strict_json = bool(
        _all_numeric_values_finite(serializable_sections)
        and _strict_json_serializable(serializable_sections)
    )
    input_passed = bool(
        all(record["passed"] for record in input_records.values())
        and q007ac_input_audit["passed"]
        and implementation_audit[
            "all_registered_implementation_sha256_match"
        ]
    )
    reconstruction_passed = bool(
        reconstruction["representative_count"] == REPRESENTATIVE_COUNT
        and reconstruction["proof_digest_mismatch_count"] == 0
        and discs_passed
        and targets_passed
        and target_reproduced
    )
    screen_floor_passed = bool(
        screen_passed
        and screen_reproduced
        and separation_audit["target_log_digest_matches_q007ac"]
        and safe_absolute_gap > PHASE_GAP
        and screen_audit["aggregate_count"]
        == q007ac.EXPECTED_AGGREGATE_COUNT
        and screen_audit["dangerous_aggregate_count"]
        == EXPECTED_DANGEROUS_AGGREGATE_COUNT
        and screen_audit["dangerous_expanded_product_count"]
        == EXPECTED_DANGEROUS_EXPANDED_PRODUCT_COUNT
        and screen_audit["phase_comparison_count"]
        == EXPECTED_PHASE_COMPARISON_COUNT
    )
    phase_execution_passed = bool(
        phase_audit["complete"]
        and tail_gap > PHASE_GAP
        and phase_audit["expanded_product_count"]
        == EXPECTED_DANGEROUS_EXPANDED_PRODUCT_COUNT
        and phase_audit["comparison_count"]
        == EXPECTED_PHASE_COMPARISON_COUNT
    )
    reuse_passed = bool(
        critical_gap_matches_registration
        and old_records_reproduced
        and q007n_cycle["radius_search"]["candidate_exponents"]
        == list(CANDIDATE_EXPONENTS)
        and q007o_cycle["q007n_reuse_audit"][
            "only_pair_inverse_changed_in_new_scan"
        ]
        and working_total_inverse
        == max(working_external_inverse, internal_inverse, zero_inverse)
        and inverse_audit["q007ac_counterfactual_inverse_not_reused"]
    )
    validity_gates = {
        "registered_inputs_and_q007ac_invalid_stop": {
            "passed": input_passed,
            "threshold": (
                "five artifact and five implementation SHA values match; "
                "Q007ac remains invalid/inconclusive with sealed digests"
            ),
            "value": {
                "accepted_input_count": sum(
                    record["passed"] for record in input_records.values()
                ),
                "q007ac_invalid_input_passed": q007ac_input_audit[
                    "passed"
                ],
            },
        },
        "original_asymmetric_spectral_disc_reconstruction": {
            "passed": reconstruction_passed,
            "threshold": (
                "72 proof digests, six original selected discs inside "
                "Q007n sigma, and 630 original target discs match"
            ),
            "value": {
                "representative_count": reconstruction[
                    "representative_count"
                ],
                "proof_digest_mismatch_count": reconstruction[
                    "proof_digest_mismatch_count"
                ],
                "selected_disc_count": disc_audit["disc_count"],
                "minimum_sigma_slack": disc_audit[
                    "minimum_sigma_slack"
                ]["float"],
                "target_disc_count": target_audit["target_disc_count"],
            },
        },
        "q007ac_screen_partition_reproduced": {
            "passed": screen_floor_passed,
            "threshold": (
                "Q007ac 2,919,730/826/108,273/287,929 partition and "
                "identifiers reproduce; safe floor exceeds 2.1e-8"
            ),
            "value": {
                "screen_reproduced_exactly": screen_reproduced,
                "aggregate_count": screen_audit["aggregate_count"],
                "dangerous_aggregate_count": screen_audit[
                    "dangerous_aggregate_count"
                ],
                "phase_comparison_count": screen_audit[
                    "phase_comparison_count"
                ],
            },
        },
        "complete_original_center_phase_expansion_and_tail": {
            "passed": phase_execution_passed,
            "threshold": (
                "108,273 products and 287,929 comparisons complete; "
                "degree-90 tail exceeds 2.1e-8"
            ),
            "value": {
                "expanded_product_count": phase_audit[
                    "expanded_product_count"
                ],
                "comparison_count": phase_audit["comparison_count"],
                "tail_gap": float(tail_gap),
            },
        },
        "critical_gap_majorant_and_candidate_reuse": {
            "passed": reuse_passed,
            "threshold": (
                "critical fraction, Q007o records, internal/zero bounds, "
                "majorants, and 119 candidates reproduce exactly"
            ),
            "value": {
                "critical_gap_matches_registration": (
                    critical_gap_matches_registration
                ),
                "old_records_reproduced": old_records_reproduced,
                "only_external_output_inverse_changed": (
                    inverse_audit["only_external_output_inverse_changed"]
                ),
            },
        },
        "finite_strict_json_and_digests": {
            "passed": finite_strict_json,
            "threshold": (
                "finite strict JSON with input/phase/result digests"
            ),
            "value": {
                "finite_strict_json": finite_strict_json,
                "input_digest_sha256": input_digest,
                "phase_certificate_digest_sha256": phase_audit[
                    "comparison_digest_sha256"
                ],
                "result_digest_sha256": result_digest,
            },
        },
    }
    validity_passed = all(
        gate["passed"] for gate in validity_gates.values()
    )

    external_no_longer_limits = (
        working_external_inverse < internal_inverse
        and working_total_inverse == internal_inverse
    )
    improvement_passed = (
        total_improvement_factor >= MINIMUM_TOTAL_IMPROVEMENT_FACTOR
    )
    hypothesis_gates = {
        "registered_asymmetric_phase_gap_certified": {
            "passed": bool(phase_passed and tail_gap > PHASE_GAP),
            "threshold": (
                "every finite-degree comparison and the degree-90 tail "
                "strictly exceed 2.1e-8"
            ),
            "value": {
                "failed_comparison_count": phase_audit[
                    "failed_comparison_count"
                ],
                "minimum_squared_margin": phase_audit[
                    "minimum_squared_margin"
                ]["float"],
            },
        },
        "working_external_output_is_below_internal": {
            "passed": external_no_longer_limits,
            "threshold": (
                "80-digit external inverse < Q007o internal inverse and "
                "new total is internal-limited"
            ),
            "value": {
                "external": float(working_external_inverse),
                "internal": float(internal_inverse),
                "target_to_critical_ratio": float(
                    target_to_critical_ratio
                ),
            },
        },
        "total_inverse_improves_by_one_hundred": {
            "passed": improvement_passed,
            "threshold": "Q007o total / new total >=100",
            "value": float(total_improvement_factor),
        },
        "registered_radius_boundary_is_1e_minus_16": {
            "passed": bool(
                old_radius_still_passes
                and registered_radius_boundary_matches
            ),
            "threshold": (
                "Q007o 1e-18 passes, selected radius is 1e-16, and "
                "preceding 1e-15 fails"
            ),
            "value": {
                "old_radius_still_passes": old_radius_still_passes,
                "new_selected_radius": (
                    None
                    if new_selected is None
                    else new_selected["modal_radius_decimal"]
                ),
                "previous_radius": (
                    None
                    if previous is None
                    else previous["modal_radius_decimal"]
                ),
            },
        },
        "new_boundary_is_strict": {
            "passed": new_boundary_passed,
            "threshold": (
                "1e-16 has strict density/range buffers, Z<1/2, and "
                "Y+Z tau<tau"
            ),
            "value": {
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
            "registered Q007ad asymmetric-disc phase audit invalid"
        )
    elif hypotheses_passed:
        outcome = "accepted"
        classification = (
            "original asymmetric discs certify the critical "
            "external-output phase gap"
        )
    else:
        outcome = "not_certified"
        classification = (
            "registered asymmetric-disc critical phase certificate "
            "did not pass"
        )

    return {
        "question": (
            "Do the original asymmetric Q007h1 selected discs certify a "
            "2.1e-8 external-output gap above the exact Q007o internal "
            "critical gap while all other radius inputs remain fixed?"
        ),
        "registered_parameters": {
            "size": SIZE,
            "omega": OMEGA,
            "eta": ETA,
            "screen_log_gap": _fraction_record(SCREEN_LOG_GAP),
            "phase_gap": _fraction_record(PHASE_GAP),
            "registered_critical_gap": _fraction_record(
                REGISTERED_CRITICAL_GAP
            ),
            "phase_threshold_outward_binary_bits": (
                PHASE_THRESHOLD_OUTWARD_BINARY_BITS
            ),
            "minimum_total_improvement_factor": _fraction_record(
                MINIMUM_TOTAL_IMPROVEMENT_FACTOR
            ),
            "selected_disc_construction": (
                "original asymmetric Q007h1 centers and radii"
            ),
            "target_disc_count": TARGET_DISC_COUNT,
            "fourier_wave_sum_restriction_used": False,
            "candidate_exponents": list(CANDIDATE_EXPONENTS),
            "maximum_contraction": _fraction_record(MAXIMUM_CONTRACTION),
            "follow_up_informed_by_q007ac_failure": True,
            "independent_exploratory_hypothesis": False,
        },
        "input_artifacts": input_records,
        "q007ac_invalid_input_audit": q007ac_input_audit,
        "implementation_source_audit": implementation_audit,
        "spectral_reconstruction": reconstruction,
        "original_selected_disc_audit": disc_audit,
        "target_external_disc_audit": target_audit,
        "critical_gap_audit": critical_gap_audit,
        "phase_aware_separation_audit": separation_audit,
        "inverse_refinement": inverse_audit,
        "radius_comparison": radius_comparison,
        "input_digest_sha256": input_digest,
        "result_digest_sha256": result_digest,
        "validity_gates": validity_gates,
        "hypothesis_gates": hypothesis_gates,
        "study_validity": "passed" if validity_passed else "failed",
        "hypothesis_outcome": outcome,
        "scientific_classification": classification,
        "theorem_consequence": {
            "q007o_explicit_radius_preserved": bool(
                validity_passed and old_radius_still_passes
            ),
            "external_output_resolvent_bottleneck_removed": bool(
                validity_passed and external_no_longer_limits
            ),
            "registered_modal_l1_radius_1e_minus_16_certified": (
                hypotheses_passed
            ),
            "identified_with_q007i_theorem_manifold": hypotheses_passed,
            "q007p_through_q007ab_tube_constants_enlarged": False,
        },
        "claim_boundary": (
            "This follow-up certificate was selected after Q007ac failed "
            "and is not an independent exploratory hypothesis. If accepted, "
            "it sharpens only the analytic existence radius to 1e-16 for "
            "the fixed 17x17 filtered map, conservation leaf, and modal/"
            "Wiener norms. It neither restores Q007ac's 1e-7 claim nor "
            "proves the 2.1e-8 threshold optimal. It does not use Fourier "
            "wave-sum restrictions, improve selected-output or zero-wave "
            "inverses, enlarge Q007p--Q007ab tube/MPFR constants, or "
            "certify Euclidean/grid-uniform attraction, a global basin, "
            "finite-amplitude performance, boundaries, forcing, or D3Q27."
        ),
        "preserved_prior_outcomes": {
            "q007ac_invalid_inconclusive_result_changed": False,
            "q007p_through_q007ab_tube_results_changed": False,
            "q007c1_finite_amplitude_rejection_changed": False,
            "q008c_tt_rejection_changed": False,
            "q010_sparse_cost_dominance_changed": False,
        },
        "next_change": (
            "If accepted, treat Q007o's selected-output internal inverse as "
            "the remaining analytic-radius bottleneck. Any enlargement of "
            "the downstream finite tube or MPFR shadowing constants remains "
            "a separate preregistered gate."
        ),
    }


def run_q007ad_study(
    artifact_directory: str | Path | None = None,
) -> dict[str, Any]:
    cycle = run_asymmetric_phase_resolvent_audit(artifact_directory)
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runner_source": _runner_source_metadata(),
        "runtime": runtime_metadata(),
        "mathematical_scope": {
            "diagnostic": (
                "rational original-asymmetric-disc nonselected-output "
                "resolvent certificate"
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
                "sharper explicit analytic existence radius only; no "
                "enlargement of the certified tube, attraction, positivity, "
                "MPFR, grid-uniform, or continuum claims"
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
    result = run_q007ad_study()
    serialized = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if arguments.output is None:
        print(serialized, end="")
        return
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
