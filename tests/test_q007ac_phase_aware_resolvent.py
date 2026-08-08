from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ac_phase_aware_resolvent as q007ac
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ac_cycle() -> dict:
    return q007ac.run_phase_aware_resolvent_audit()


@pytest.fixture(scope="module")
def q007ac_artifact() -> dict:
    path = (
        Path(q007ac.__file__).resolve().parent
        / "artifacts"
        / "q007ac_phase_aware_resolvent.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def test_q007ac_screen_is_complete_and_phase_expansion_is_exact(
    q007ac_cycle: dict,
) -> None:
    separation = q007ac_cycle["phase_aware_separation_audit"]
    screen = separation["screen"]
    phase = separation["phase"]

    assert screen["aggregate_count"] == q007ac.EXPECTED_AGGREGATE_COUNT
    assert screen["expanded_product_count"] == (
        q007ac.EXPECTED_EXPANDED_PRODUCT_COUNT
    )
    assert screen["dangerous_aggregate_count"] == 826
    assert screen["dangerous_expanded_product_count"] == 108_273
    assert screen["phase_comparison_count"] == 287_929
    assert screen["counts_and_partition_passed"]
    assert phase["expanded_product_count"] == 108_273
    assert phase["comparison_count"] == 287_929
    assert phase["complete"]
    assert phase["threshold_outward_binary_bits"] == 256
    assert _fraction(phase["maximum_threshold_rounding_increment"]) < Fraction(
        1, 2**256
    )


def test_q007ac_preregistered_phase_gap_has_four_counterexamples(
    q007ac_cycle: dict,
) -> None:
    phase = q007ac_cycle["phase_aware_separation_audit"]["phase"]
    witness = phase["minimum_margin_witness"]

    assert phase["failed_comparison_count"] == 4
    assert not phase["all_phase_comparisons_strict"]
    assert _fraction(phase["minimum_squared_margin"]) < 0
    assert _fraction(witness["certified_complex_distance_lower"]) < (
        q007ac.PHASE_GAP
    )
    assert witness["degree"] == 71
    assert witness["counts"] == [24, 38, 2, 7]
    assert witness["axis_acoustic_positive_count"] == 12
    assert witness["axis_acoustic_negative_count"] == 12
    assert witness["diagonal_acoustic_positive_count"] == 1
    assert witness["diagonal_acoustic_negative_count"] == 1
    assert witness["external_identifier"] == (
        "wave=-7,-7;eigenvalue_index=6"
    )
    assert phase["comparison_digest_sha256"] == (
        "5039563c60ab57b85b683b324506049535372847b1a5adef3362da2b16a954ab"
    )


def test_q007ac_registered_nominal_radius_condition_is_invalid(
    q007ac_cycle: dict,
) -> None:
    nominal = q007ac_cycle["nominal_selected_disc_audit"]
    validity = q007ac_cycle["validity_gates"]

    assert nominal["selected_index_registration_matches"]
    assert nominal["all_original_selected_discs_contained"]
    assert not nominal["all_nominal_discs_within_working_spectral_radius"]
    assert _fraction(
        nominal["working_product_factor_modulus_inflation_over_q007n"]
    ) == pytest.approx(1.6653345369377348e-16)
    assert not validity["spectral_disc_reconstruction"]["passed"]
    assert all(
        gate["passed"]
        for name, gate in validity.items()
        if name != "spectral_disc_reconstruction"
    )


def test_q007ac_stops_as_inconclusive_without_using_counterfactual_gain(
    q007ac_cycle: dict,
) -> None:
    inverse = q007ac_cycle["inverse_refinement"]
    search = q007ac_cycle["radius_comparison"][
        "phase_refined_radius_search"
    ]

    assert q007ac_cycle["study_validity"] == "failed"
    assert q007ac_cycle["hypothesis_outcome"] == "inconclusive"
    assert q007ac_cycle["scientific_classification"] == (
        "registered Q007ac phase-aware audit invalid"
    )
    assert not q007ac_cycle["hypothesis_gates"][
        "registered_phase_gap_certified"
    ]["passed"]
    assert inverse["new_total_is_internal_limited"]
    assert inverse["total_inverse_improvement_factor"]["float"] == pytest.approx(
        125.28856057411295
    )
    assert search["selected_candidate"]["modal_radius_decimal"] == "1e-16"
    assert search["previous_larger_candidate"]["modal_radius_decimal"] == "1e-15"
    assert not q007ac_cycle["theorem_consequence"][
        "larger_registered_explicit_modal_l1_radius_certified"
    ]
    assert q007ac_cycle["input_digest_sha256"] == (
        "15166f90e39b132c0d6956b7a14f821095cc1b31da9d9e83b9b3f5b9cf3314b9"
    )
    assert q007ac_cycle["result_digest_sha256"] == (
        "369809e953652c9e99ade3553e2754a06c1b0add52549e2f53dbcdb0ab15f018"
    )


def test_q007ac_dyadic_outward_rounding_is_exact() -> None:
    value = Fraction(1, 10**7) + Fraction(1, 3 * 10**20)
    rounded = q007ac._round_fraction_up_to_dyadic(value, 256)
    rounded_fraction = q007ac._dyadic_to_fraction(rounded)

    assert rounded_fraction >= value
    assert rounded_fraction - value < Fraction(1, 2**256)
    squared = q007ac._square_dyadic(rounded)
    assert q007ac._dyadic_to_fraction(squared) >= value * value


def test_q007ac_artifact_reproduces_the_invalid_stop(
    q007ac_cycle: dict,
    q007ac_artifact: dict,
) -> None:
    runner_path = Path(q007ac.__file__).resolve()

    assert q007ac_artifact["schema_version"] == 1
    assert q007ac_artifact["source"] == source_metadata()
    assert q007ac_artifact["runner_source"] == {
        "filename": "q007ac_phase_aware_resolvent.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert q007ac_artifact["cycle"] == q007ac_cycle
    assert q007ac_artifact["study_gate"] == "failed"
    assert q007ac_artifact["scientific_outcome"] == "inconclusive"
