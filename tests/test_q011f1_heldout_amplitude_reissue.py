from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q011f1_heldout_amplitude_reissue as q011f1
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011f1_cycle() -> dict:
    return q011f1.run_heldout_amplitude_reissue_audit()


def test_q011f1_seals_the_original_failure_without_regrading(
    q011f1_cycle: dict,
) -> None:
    audit = q011f1_cycle["sealed_q011f_artifact_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["artifact"]["study_validity"] == "passed"
    assert audit["artifact"]["hypothesis_outcome"] == "rejected"
    assert audit["artifact"]["failed_hypothesis_gates"] == [
        "all_direction_horizon_fits_are_slope_eligible"
    ]
    assert [
        (
            record["direction_index"],
            record["horizon"],
            record["linear_fit_point_count"],
            record["quadratic_fit_point_count"],
        )
        for record in audit["degenerate_witnesses"]
    ] == [(4, 1, 5, 3), (4, 2, 5, 3)]


def test_q011f1_reconstructs_the_same_chart_once(q011f1_cycle: dict) -> None:
    audit = q011f1_cycle["q011e_chart_reconstruction_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["q011f_chart_reconstruction_digest_sha256"] == (q011f1.Q011F_CHART_DIGEST)
    assert audit["array_hashes"] == {
        "real_tangent_sha256": q011f1.q011e1.REAL_TANGENT_SHA256,
        "real_extractor_sha256": q011f1.q011e1.REAL_EXTRACTOR_SHA256,
        "real_reduced_linear_sha256": q011f1.q011e1.REAL_LINEAR_SHA256,
        "analytic_second_derivative_sha256": (q011f1.q011e1.ANALYTIC_SECOND_DERIVATIVE_SHA256),
        "real_chart_hessian_sha256": q011f1.q011e1.REAL_CHART_HESSIAN_SHA256,
        "real_reduced_hessian_sha256": (q011f1.q011e1.REAL_REDUCED_HESSIAN_SHA256),
    }


def test_q011f1_heldout_campaign_is_complete(q011f1_cycle: dict) -> None:
    audit = q011f1_cycle["heldout_trajectory_audit"]

    assert audit["direction_seed"] == 20260826
    assert audit["direction_count"] == 32
    assert audit["direction_sha256"] == q011f1.Q011F_DIRECTION_SHA256
    assert audit["heldout_amplitude"] == 4.8e-4
    assert audit["trajectory_count_per_chart"] == 32
    assert audit["step_record_count"] == 2_048
    assert audit["checkpoint_record_count"] == 224
    assert len(audit["trajectory_records"]) == 32
    assert all(len(record["step_records"]) == 64 for record in audit["trajectory_records"])
    assert audit["passed"]
    assert all(audit["checks"].values())


def test_q011f1_repairs_all_merged_fits(q011f1_cycle: dict) -> None:
    audit = q011f1_cycle["merged_fit_audit"]

    assert audit["original_amplitudes"] == list(q011f1.q011f.AMPLITUDES)
    assert audit["heldout_amplitude"] == 4.8e-4
    assert audit["merged_amplitudes"] == list(q011f1.MERGED_AMPLITUDES)
    assert audit["fit_count"] == 224
    assert audit["slope_eligible_direction_horizon_count"] == 224
    assert audit["degenerate_direction_horizon_count"] == 0
    assert len(audit["repaired_witness_records"]) == 2
    assert all(
        record["heldout_quadratic_point_is_fit_eligible"]
        and record["quadratic_fit_point_count"] >= 4
        for record in audit["repaired_witness_records"]
    )
    assert (
        q011f1.q011f.LINEAR_SHADOW_SLOPE_INTERVAL[0] <= audit["minimum_linear_shadow_error_slope"]
    )
    assert (
        audit["maximum_linear_shadow_error_slope"] <= (q011f1.q011f.LINEAR_SHADOW_SLOPE_INTERVAL[1])
    )
    assert (
        q011f1.q011f.QUADRATIC_SHADOW_SLOPE_INTERVAL[0]
        <= audit["minimum_quadratic_shadow_error_slope"]
    )
    assert (
        audit["maximum_quadratic_shadow_error_slope"]
        <= (q011f1.q011f.QUADRATIC_SHADOW_SLOPE_INTERVAL[1])
    )
    assert audit["maximum_merged_checkpoint_quadratic_linear_error_ratio"] <= 0.05
    assert audit["maximum_merged_final_quadratic_error_over_initial_amplitude"] <= 1.0e-3
    assert audit["minimum_merged_full_or_lifted_population"] > 0.0
    assert audit["maximum_merged_global_conservation_drift"] <= 1.0e-10
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]
    assert all(audit["checks"].values())
    assert all(audit["hypothesis_checks"].values())


def test_q011f1_accepts_only_the_heldout_reissue(q011f1_cycle: dict) -> None:
    assert len(q011f1_cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in q011f1_cycle["validity_gates"].values())
    assert len(q011f1_cycle["hypothesis_gates"]) == 6
    assert all(gate["passed"] for gate in q011f1_cycle["hypothesis_gates"].values())
    assert q011f1_cycle["study_validity"] == "passed"
    assert q011f1_cycle["hypothesis_outcome"] == "accepted"
    assert q011f1_cycle["scientific_classification"] == (
        "the forced quadratic chart passes a held-out-amplitude 64-step shadowing reissue"
    )
    consequence = q011f1_cycle["numerical_consequence"]
    assert consequence["heldout_amplitude_reissue_confirms_finite_shadowing_window"]
    assert not consequence["q011f_original_rejected_outcome_changed"]
    assert not consequence["q011e1_accepted_residual_window_changed"]
    assert not consequence["q011e_original_rejected_outcome_changed"]
    assert not consequence["all_time_shadowing_is_certified"]
    assert not consequence["nonlinear_normal_attraction_is_certified"]
    assert not any(q011f1_cycle["preserved_prior_outcomes"].values())


def test_q011f1_records_reproducible_digests_and_provenance(
    q011f1_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011f1_cycle["registered_parameters"],
        "sealed_q011f_artifact_audit": q011f1_cycle["sealed_q011f_artifact_audit"],
    }
    chart_sections = {
        "q011e_chart_reconstruction_audit": q011f1_cycle["q011e_chart_reconstruction_audit"],
    }
    heldout_sections = {
        "heldout_trajectory_audit": q011f1_cycle["heldout_trajectory_audit"],
    }
    merged_sections = {
        "merged_fit_audit": q011f1_cycle["merged_fit_audit"],
    }

    assert q011f1_cycle["input_digest_sha256"] == (
        q011f1.q011e.q011c._canonical_json_sha256(input_sections)
    )
    assert q011f1_cycle["chart_reconstruction_digest_sha256"] == (
        q011f1.q011e.q011c._canonical_json_sha256(chart_sections)
    )
    assert q011f1_cycle["heldout_trajectory_digest_sha256"] == (
        q011f1.q011e.q011c._canonical_json_sha256(heldout_sections)
    )
    assert q011f1_cycle["merged_fit_digest_sha256"] == (
        q011f1.q011e.q011c._canonical_json_sha256(merged_sections)
    )
    assert q011f1_cycle["result_digest_sha256"] == (
        q011f1.q011e.q011c._canonical_json_sha256(q011f1._result_digest_sections(q011f1_cycle))
    )
    runner_path = Path(q011f1.__file__).resolve()
    assert q011f1_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_source_sha256"] == (q011f1.SEALED_PACKAGE_SOURCE_SHA256)
    json.dumps(q011f1_cycle, allow_nan=False)
