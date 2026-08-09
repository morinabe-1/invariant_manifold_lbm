from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q011f_multistep_shadowing as q011f
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011f_cycle() -> dict:
    return q011f.run_multistep_shadowing_audit()


def test_q011f_seals_q011e1_and_preserves_q011e(q011f_cycle: dict) -> None:
    audit = q011f_cycle["sealed_q011e1_artifact_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["artifact"]["study_validity"] == "passed"
    assert audit["artifact"]["hypothesis_outcome"] == "accepted"
    assert audit["artifact"]["direction_sha256"] == q011f.Q011E1_DIRECTION_SHA256
    assert audit["preserved_q011e_outcome"] == {
        "study_validity": "passed",
        "hypothesis_outcome": "rejected",
        "failed_hypothesis_gates": ["linear_and_quadratic_residual_orders_pass"],
    }


def test_q011f_reconstructs_the_same_chart_once(q011f_cycle: dict) -> None:
    audit = q011f_cycle["q011e_chart_reconstruction_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["q011e1_chart_reconstruction_digest_sha256"] == (q011f.Q011E1_CHART_DIGEST)
    assert audit["array_hashes"] == {
        "real_tangent_sha256": q011f.q011e1.REAL_TANGENT_SHA256,
        "real_extractor_sha256": q011f.q011e1.REAL_EXTRACTOR_SHA256,
        "real_reduced_linear_sha256": q011f.q011e1.REAL_LINEAR_SHA256,
        "analytic_second_derivative_sha256": (q011f.q011e1.ANALYTIC_SECOND_DERIVATIVE_SHA256),
        "real_chart_hessian_sha256": q011f.q011e1.REAL_CHART_HESSIAN_SHA256,
        "real_reduced_hessian_sha256": (q011f.q011e1.REAL_REDUCED_HESSIAN_SHA256),
    }


def test_q011f_trajectory_campaign_is_complete(q011f_cycle: dict) -> None:
    audit = q011f_cycle["multistep_trajectory_audit"]

    assert audit["seed"] == 20260826
    assert audit["direction_count"] == 32
    assert audit["amplitudes"] == list(q011f.AMPLITUDES)
    assert audit["maximum_step"] == 64
    assert audit["horizons"] == [1, 2, 4, 8, 16, 32, 64]
    assert audit["trajectory_count_per_chart"] == 160
    assert audit["step_record_count"] == 10_240
    assert audit["checkpoint_record_count"] == 1_120
    assert len(audit["trajectory_records"]) == 160
    assert len(audit["direction_horizon_fit_records"]) == 224
    assert all(len(record["step_records"]) == 64 for record in audit["trajectory_records"])
    assert audit["structural_passed"]
    assert all(audit["checks"].values())


def test_q011f_localizes_two_underresolved_early_horizon_fits(
    q011f_cycle: dict,
) -> None:
    audit = q011f_cycle["multistep_trajectory_audit"]

    assert audit["slope_eligible_direction_horizon_count"] == 222
    assert audit["degenerate_direction_horizon_count"] == 2
    degenerate = [
        record for record in audit["direction_horizon_fit_records"] if not record["slope_eligible"]
    ]
    assert [
        (
            record["direction_index"],
            record["horizon"],
            record["linear_fit_point_count"],
            record["quadratic_fit_point_count"],
        )
        for record in degenerate
    ] == [(4, 1, 5, 3), (4, 2, 5, 3)]
    assert all(
        record["quadratic_fit_mask"] == [False, False, True, True, True] for record in degenerate
    )
    assert q011f.LINEAR_SHADOW_SLOPE_INTERVAL[0] <= audit["minimum_linear_shadow_error_slope"]
    assert audit["maximum_linear_shadow_error_slope"] <= (q011f.LINEAR_SHADOW_SLOPE_INTERVAL[1])
    assert q011f.QUADRATIC_SHADOW_SLOPE_INTERVAL[0] <= audit["minimum_quadratic_shadow_error_slope"]
    assert (
        audit["maximum_quadratic_shadow_error_slope"] <= (q011f.QUADRATIC_SHADOW_SLOPE_INTERVAL[1])
    )
    assert audit["maximum_checkpoint_quadratic_linear_error_ratio"] <= 0.05
    assert audit["maximum_final_quadratic_error_over_initial_amplitude"] <= 1.0e-3
    assert audit["minimum_full_or_lifted_population"] > 0.0
    assert audit["maximum_global_conservation_drift"] <= 1.0e-10
    assert not audit["hypothesis_passed"]
    failed = [name for name, passed in audit["hypothesis_checks"].items() if not passed]
    assert failed == ["all_direction_horizon_fits_are_slope_eligible"]


def test_q011f_is_valid_but_rejects_the_registered_finite_window(
    q011f_cycle: dict,
) -> None:
    assert len(q011f_cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in q011f_cycle["validity_gates"].values())
    assert len(q011f_cycle["hypothesis_gates"]) == 6
    failed = [name for name, gate in q011f_cycle["hypothesis_gates"].items() if not gate["passed"]]
    assert failed == ["all_direction_horizon_fits_are_slope_eligible"]
    assert q011f_cycle["study_validity"] == "passed"
    assert q011f_cycle["hypothesis_outcome"] == "rejected"
    assert q011f_cycle["scientific_classification"] == (
        "the forced quadratic chart fails the registered finite shadowing window"
    )
    consequence = q011f_cycle["numerical_consequence"]
    assert not consequence["registered_finite_multistep_shadowing_window_passes"]
    assert not consequence["q011e_original_rejected_outcome_changed"]
    assert not consequence["q011e1_accepted_residual_window_changed"]
    assert not consequence["q011e_dense_quadratic_chart_changed"]
    assert not consequence["all_time_shadowing_is_certified"]
    assert not consequence["nonlinear_normal_attraction_is_certified"]
    assert not any(q011f_cycle["preserved_prior_outcomes"].values())


def test_q011f_records_reproducible_digests_and_provenance(
    q011f_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011f_cycle["registered_parameters"],
        "sealed_q011e1_artifact_audit": q011f_cycle["sealed_q011e1_artifact_audit"],
    }
    chart_sections = {
        "q011e_chart_reconstruction_audit": q011f_cycle["q011e_chart_reconstruction_audit"],
    }
    trajectory_sections = {
        "multistep_trajectory_audit": q011f_cycle["multistep_trajectory_audit"],
    }

    assert q011f_cycle["input_digest_sha256"] == (
        q011f.q011e.q011c._canonical_json_sha256(input_sections)
    )
    assert q011f_cycle["chart_reconstruction_digest_sha256"] == (
        q011f.q011e.q011c._canonical_json_sha256(chart_sections)
    )
    assert q011f_cycle["trajectory_digest_sha256"] == (
        q011f.q011e.q011c._canonical_json_sha256(trajectory_sections)
    )
    assert q011f_cycle["result_digest_sha256"] == (
        q011f.q011e.q011c._canonical_json_sha256(q011f._result_digest_sections(q011f_cycle))
    )
    runner_path = Path(q011f.__file__).resolve()
    assert q011f_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_source_sha256"] == (q011f.SEALED_PACKAGE_SOURCE_SHA256)
    json.dumps(q011f_cycle, allow_nan=False)


def test_q011f_artifact_reproduces_the_rejected_window(
    q011f_cycle: dict,
) -> None:
    runner_path = Path(q011f.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011f_multistep_shadowing.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "9c091dbafd60617850cd3168f3ad9235a353b0990cbd003df9be0b487ead1591"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011f_multistep_shadowing.py",
        "sha256": ("e9c0a8e38b94dbe693855dc836f8cf02393675b417ff3f43fc43059ab361a741"),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["cycle"] == q011f_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["cycle"]["input_digest_sha256"] == (
        "e9b29c95d41af0062259d3aab19ab2c58175cd98582ed82f3af36863f023bc53"
    )
    assert artifact["cycle"]["chart_reconstruction_digest_sha256"] == (
        "aa1da452db8ff6b84e88a32f7a7119c63816b12e283147daaa303e9e09c3ae42"
    )
    assert artifact["cycle"]["trajectory_digest_sha256"] == (
        "aa62fc11a36bef881bbcdb05919818f6db167f3f95eee396fcdaf79fead5e182"
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        "629a5a7a3d3bfed12a590646c375d4977db1726ddc521ddb86394786b1005f22"
    )
    assert (
        artifact["cycle"]["multistep_trajectory_audit"]["direction_sha256"]
        == "4d0bef57236d4f70a8a8f422b1bdfa39cd5737c88401c2441decdd98d886d2f9"
    )
