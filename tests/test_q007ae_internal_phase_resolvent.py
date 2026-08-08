from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ae_internal_phase_resolvent as q007ae
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ae_cycle() -> dict:
    return q007ae.run_internal_phase_resolvent_audit()


@pytest.fixture(scope="module")
def q007ae_artifact() -> dict:
    path = (
        Path(q007ae.__file__).resolve().parent
        / "artifacts"
        / "q007ae_internal_phase_resolvent.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def test_q007ae_reuses_registered_gap_above_internal_critical_gap() -> None:
    assert q007ae.PHASE_GAP == Fraction(21, 10**9)
    assert q007ae.REGISTERED_CRITICAL_GAP == Fraction(
        q007ae.REGISTERED_CRITICAL_GAP_NUMERATOR,
        q007ae.REGISTERED_CRITICAL_GAP_DENOMINATOR,
    )
    assert q007ae.PHASE_GAP > q007ae.REGISTERED_CRITICAL_GAP
    assert q007ae.PHASE_GAP / q007ae.REGISTERED_CRITICAL_GAP > 3


def test_q007ae_reproduces_nonselected_global_witness_and_targets(
    q007ae_cycle: dict,
) -> None:
    prior = q007ae_cycle["q007ad_accepted_input_audit"]
    bottleneck = q007ae_cycle["bottleneck_reproduction_audit"]
    targets = q007ae_cycle["selected_output_target_center_audit"]
    discs = q007ae_cycle["original_selected_disc_audit"]

    assert prior["passed"]
    assert prior["study_gate"] == "passed"
    assert prior["scientific_outcome"] == "accepted"
    assert bottleneck["global_witness_reproduced"]
    assert not bottleneck["global_witness_is_selected_output"]
    assert bottleneck["q007i_global_minimum_gap_witness"] == (
        q007ae.EXPECTED_GLOBAL_WITNESS
    )
    assert targets["target_center_count"] == 12
    assert targets["target_radius_is_zero"]
    assert targets["all_indices_match_q007o"]
    assert targets["all_proof_digests_match_q007o"]
    assert targets["c4_selected_output_wave_coverage"] == 8
    assert not targets["fourier_wave_sum_restriction_used"]
    assert discs["disc_count"] == 6
    assert discs["all_original_discs_within_q007n_working_sigma"]


def test_q007ae_completes_phase_screen_without_counterexample(
    q007ae_cycle: dict,
) -> None:
    separation = q007ae_cycle["phase_aware_separation_audit"]
    screen = separation["screen"]
    phase = separation["phase"]

    assert screen["aggregate_count"] == (
        q007ae.q007ad.q007ac.EXPECTED_AGGREGATE_COUNT
    )
    assert screen["counts_and_partition_passed"]
    assert phase["complete"]
    assert phase["expanded_product_count"] == screen[
        "dangerous_expanded_product_count"
    ]
    assert phase["comparison_count"] == screen["phase_comparison_count"]
    assert phase["failed_comparison_count"] == 0
    assert phase["all_phase_comparisons_strict"]
    assert _fraction(phase["minimum_squared_margin"]) > 0
    assert _fraction(
        phase["minimum_margin_witness"][
            "certified_complex_distance_lower"
        ]
    ) > q007ae.PHASE_GAP
    assert _fraction(phase["maximum_threshold_rounding_increment"]) < (
        Fraction(1, 2**256)
    )


def test_q007ae_internal_inverse_falls_below_zero_and_total_is_external(
    q007ae_cycle: dict,
) -> None:
    internal = q007ae_cycle["internal_inverse_refinement"]
    total = q007ae_cycle["total_inverse_refinement"]

    assert internal["critical_gap_matches_registration"]
    assert _fraction(
        internal["working_internal_pair_inverse_upper"]
    ) < Fraction(2 * 10**9)
    assert internal["working_internal_strictly_below_zero"]
    assert total["new_total_is_q007ad_external_limited"]
    assert _fraction(total["q007ae_working_internal_inverse_upper"]) < (
        _fraction(total["q007n_zero_wave_inverse_upper"])
    )
    assert _fraction(total["q007n_zero_wave_inverse_upper"]) < (
        _fraction(total["q007ad_working_external_inverse_upper"])
    )
    assert total["total_inverse_improvement_factor"]["float"] == (
        pytest.approx(1.0402168828423712)
    )


def test_q007ae_accepts_bottleneck_removal_without_radius_upgrade(
    q007ae_cycle: dict,
) -> None:
    search = q007ae_cycle["radius_comparison"][
        "internal_phase_refined_radius_search"
    ]

    assert q007ae_cycle["study_validity"] == "passed"
    assert q007ae_cycle["hypothesis_outcome"] == "accepted"
    assert q007ae_cycle["scientific_classification"] == (
        "phase-aware selected-output centers remove the internal "
        "resolvent bottleneck"
    )
    assert all(
        gate["passed"]
        for gate in q007ae_cycle["validity_gates"].values()
    )
    assert all(
        gate["passed"]
        for gate in q007ae_cycle["hypothesis_gates"].values()
    )
    assert search["selected_candidate"]["modal_radius_decimal"] == "1e-16"
    assert search["previous_larger_candidate"][
        "modal_radius_decimal"
    ] == "1e-15"
    assert not search["previous_larger_candidate"]["passed"]
    consequence = q007ae_cycle["theorem_consequence"]
    assert consequence[
        "selected_output_internal_resolvent_bottleneck_removed"
    ]
    assert consequence["new_total_is_nonselected_external_limited"]
    assert not consequence[
        "strictly_larger_decimal_grid_radius_certified"
    ]
    assert not consequence[
        "q007p_through_q007ab_tube_constants_enlarged"
    ]


def test_q007ae_artifact_reproduces_the_accepted_certificate(
    q007ae_cycle: dict,
    q007ae_artifact: dict,
) -> None:
    runner_path = Path(q007ae.__file__).resolve()
    separation = q007ae_cycle["phase_aware_separation_audit"]

    assert q007ae_artifact["schema_version"] == 1
    assert q007ae_artifact["source"] == source_metadata()
    assert q007ae_artifact["runner_source"] == {
        "filename": "q007ae_internal_phase_resolvent.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert q007ae_artifact["cycle"] == q007ae_cycle
    assert q007ae_artifact["study_gate"] == "passed"
    assert q007ae_artifact["scientific_outcome"] == "accepted"
    assert q007ae_cycle["input_digest_sha256"] == (
        "23fba479cfa07ec50721d9b05bcaf40a0ac04126497ff64b04785e1d20534e0e"
    )
    assert q007ae_cycle["result_digest_sha256"] == (
        "3e1792c5215952d9126bf5bd61409a2a0d72ebc12970ad1e4aaca481d4fcb687"
    )
    assert separation["phase"]["comparison_digest_sha256"] == (
        "4aea091076179e7ef8eb14c9c4828b41d6af3ef25665e5b2dbbf562acf692b3b"
    )
    assert separation["selected_center_certificate_digest_sha256"] == (
        "3cc524ebb82c3e375bf35d456f96be11fa5d124728873046ed59a7032a2058d7"
    )
