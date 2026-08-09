from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import research.q011e1_enlarged_residual_window as q011e1
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011e1_cycle() -> dict:
    return q011e1.run_enlarged_residual_window_audit()


def test_q011e1_secondary_slope_uses_the_registered_upper_window() -> None:
    amplitudes = np.asarray(q011e1.AMPLITUDES)
    quadratic = amplitudes**3

    all_points_slope, all_points_indices = q011e1._secondary_slope(
        amplitudes,
        quadratic,
        np.ones(5, dtype=bool),
    )
    upper_points_slope, upper_points_indices = q011e1._secondary_slope(
        amplitudes,
        quadratic,
        np.asarray([False, True, True, True, True]),
    )

    assert all_points_indices == [1, 2, 3, 4]
    assert upper_points_indices == [1, 2, 3, 4]
    assert all_points_slope == pytest.approx(3.0, rel=0.0, abs=1.0e-14)
    assert upper_points_slope == pytest.approx(3.0, rel=0.0, abs=1.0e-14)


def test_q011e1_seals_q011e_without_regrading(q011e1_cycle: dict) -> None:
    audit = q011e1_cycle["sealed_q011e_artifact_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["artifact"]["study_validity"] == "passed"
    assert audit["artifact"]["hypothesis_outcome"] == "rejected"
    assert audit["artifact"]["failed_validity_gates"] == []
    assert audit["artifact"]["failed_hypothesis_gates"] == [
        "linear_and_quadratic_residual_orders_pass"
    ]
    assert audit["q011e_original_residual_campaign"] == {
        "seed": 20260824,
        "amplitudes": [1.0e-5, 2.0e-5, 4.0e-5, 8.0e-5, 1.6e-4],
        "noise_floor": 1.0e-13,
        "slope_eligible_direction_count": 0,
        "degenerate_direction_count": 32,
    }


def test_q011e1_reconstructs_the_sealed_chart_once(q011e1_cycle: dict) -> None:
    audit = q011e1_cycle["q011e_chart_reconstruction_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["input_digest_sha256"] == q011e1.Q011E_INPUT_DIGEST
    assert audit["derivative_digest_sha256"] == q011e1.Q011E_DERIVATIVE_DIGEST
    assert audit["chart_digest_sha256"] == q011e1.Q011E_CHART_DIGEST
    assert audit["array_hashes"] == {
        "real_tangent_sha256": q011e1.REAL_TANGENT_SHA256,
        "real_extractor_sha256": q011e1.REAL_EXTRACTOR_SHA256,
        "real_reduced_linear_sha256": q011e1.REAL_LINEAR_SHA256,
        "analytic_second_derivative_sha256": (q011e1.ANALYTIC_SECOND_DERIVATIVE_SHA256),
        "real_chart_hessian_sha256": q011e1.REAL_CHART_HESSIAN_SHA256,
        "real_reduced_hessian_sha256": q011e1.REAL_REDUCED_HESSIAN_SHA256,
    }


def test_q011e1_independent_campaign_is_complete(q011e1_cycle: dict) -> None:
    audit = q011e1_cycle["enlarged_residual_window_audit"]

    assert audit["seed"] == 20260825
    assert audit["direction_count"] == 32
    assert audit["amplitudes"] == list(q011e1.AMPLITUDES)
    assert audit["noise_floor"] == 1.0e-13
    assert audit["sample_count"] == 160
    assert len(audit["direction_records"]) == 32
    assert all(len(record["samples"]) == 5 for record in audit["direction_records"])
    assert all(
        record["direction_norm"] == pytest.approx(1.0, rel=0.0, abs=1.0e-14)
        for record in audit["direction_records"]
    )
    assert audit["structural_passed"]
    assert all(audit["checks"].values())


def test_q011e1_resolves_registered_residual_orders(q011e1_cycle: dict) -> None:
    audit = q011e1_cycle["enlarged_residual_window_audit"]

    assert audit["slope_eligible_direction_count"] >= 28
    assert audit["degenerate_direction_count"] <= 4
    assert q011e1.LINEAR_SLOPE_INTERVAL[0] <= audit["minimum_linear_primary_slope"]
    assert audit["maximum_linear_primary_slope"] <= q011e1.LINEAR_SLOPE_INTERVAL[1]
    assert q011e1.LINEAR_SLOPE_INTERVAL[0] <= audit["minimum_linear_secondary_slope"]
    assert audit["maximum_linear_secondary_slope"] <= q011e1.LINEAR_SLOPE_INTERVAL[1]
    assert q011e1.QUADRATIC_SLOPE_INTERVAL[0] <= audit["minimum_quadratic_primary_slope"]
    assert audit["maximum_quadratic_primary_slope"] <= (q011e1.QUADRATIC_SLOPE_INTERVAL[1])
    assert q011e1.QUADRATIC_SLOPE_INTERVAL[0] <= audit["minimum_quadratic_secondary_slope"]
    assert audit["maximum_quadratic_secondary_slope"] <= (q011e1.QUADRATIC_SLOPE_INTERVAL[1])
    assert audit["maximum_linear_primary_secondary_slope_difference"] <= 0.15
    assert audit["maximum_quadratic_primary_secondary_slope_difference"] <= 0.15
    assert audit["maximum_largest_amplitude_residual_ratio"] <= 0.25
    assert audit["minimum_chart_reduced_or_mapped_population"] > 0.0
    assert audit["maximum_global_conservation_drift"] <= 1.0e-10
    assert audit["hypothesis_passed"]
    assert all(audit["hypothesis_checks"].values())


def test_q011e1_accepts_only_the_independent_window(q011e1_cycle: dict) -> None:
    assert len(q011e1_cycle["validity_gates"]) == 5
    assert all(gate["passed"] for gate in q011e1_cycle["validity_gates"].values())
    assert len(q011e1_cycle["hypothesis_gates"]) == 6
    assert all(gate["passed"] for gate in q011e1_cycle["hypothesis_gates"].values())
    assert q011e1_cycle["study_validity"] == "passed"
    assert q011e1_cycle["hypothesis_outcome"] == "accepted"
    assert q011e1_cycle["scientific_classification"] == (
        "the independent enlarged window resolves second- and third-order forced chart residuals"
    )
    consequence = q011e1_cycle["numerical_consequence"]
    assert consequence["independent_enlarged_window_confirms_residual_orders"]
    assert not consequence["q011e_original_rejected_outcome_changed"]
    assert not consequence["q011e_original_residual_campaign_regraded"]
    assert not consequence["q011e_dense_quadratic_chart_changed"]
    assert not consequence["uniform_taylor_remainder_is_certified"]
    assert not consequence["forced_ssm_exists_or_is_unique"]
    assert not any(q011e1_cycle["preserved_prior_outcomes"].values())


def test_q011e1_records_reproducible_digests_and_provenance(
    q011e1_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011e1_cycle["registered_parameters"],
        "sealed_q011e_artifact_audit": q011e1_cycle["sealed_q011e_artifact_audit"],
    }
    chart_sections = {
        "q011e_chart_reconstruction_audit": q011e1_cycle["q011e_chart_reconstruction_audit"],
    }
    residual_sections = {
        "enlarged_residual_window_audit": q011e1_cycle["enlarged_residual_window_audit"],
    }

    assert q011e1_cycle["input_digest_sha256"] == (
        q011e1.q011e.q011c._canonical_json_sha256(input_sections)
    )
    assert q011e1_cycle["chart_reconstruction_digest_sha256"] == (
        q011e1.q011e.q011c._canonical_json_sha256(chart_sections)
    )
    assert q011e1_cycle["residual_window_digest_sha256"] == (
        q011e1.q011e.q011c._canonical_json_sha256(residual_sections)
    )
    assert q011e1_cycle["result_digest_sha256"] == (
        q011e1.q011e.q011c._canonical_json_sha256(q011e1._result_digest_sections(q011e1_cycle))
    )
    runner_path = Path(q011e1.__file__).resolve()
    assert q011e1_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_source_sha256"] == (q011e1.SEALED_PACKAGE_SOURCE_SHA256)
    json.dumps(q011e1_cycle, allow_nan=False)


def test_q011e1_artifact_reproduces_the_accepted_window(
    q011e1_cycle: dict,
) -> None:
    runner_path = Path(q011e1.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / ("q011e1_enlarged_residual_window.json")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "989801d1e4e1396ebba279e11c396f7f6d4e9616d2aa170f5687f9ba08a95840"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011e1_enlarged_residual_window.py",
        "sha256": ("bb8a052f387d2748fee823af10f2ab4ea4a9a08ebe62e8b4ff87d68d55c2929f"),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["cycle"] == q011e1_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["input_digest_sha256"] == (
        "8e979deeed0e5f4151addb5f3b06c1a9815a28f4e0c5762726d7c29a03d035c0"
    )
    assert artifact["cycle"]["chart_reconstruction_digest_sha256"] == (
        "2e739657032352d7d0496568a216b761000a68beb6d00749e1e427e6447598fb"
    )
    assert artifact["cycle"]["residual_window_digest_sha256"] == (
        "20267150710538f797f21cc2846ee6be14060ad9ea6bef98ef29e4731121410b"
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        "0370a24ce7a74da71ee978b3892ea23412c3d18adb110e2b2b53aaf02ccdf039"
    )
    assert (
        artifact["cycle"]["enlarged_residual_window_audit"]["direction_sha256"]
        == "64b017fb5a3c55378ccee4d457b4d2a8c75a92cd5b421897f9b7de1ad6a77b1d"
    )
