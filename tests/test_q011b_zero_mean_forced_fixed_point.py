from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import research.q011b_zero_mean_forced_fixed_point as q011b
from ttim_lbm.d2q9 import D2Q9_VELOCITIES, uniform_equilibrium
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011b_cycle() -> dict:
    return q011b.run_zero_mean_forced_fixed_point_audit()


def test_q011b_public_source_and_map_use_the_registered_cosine() -> None:
    waveform = q011b.force_waveform()
    source = q011b.spatial_body_force_source(waveform[:, None])
    reference = np.vstack(
        [q011b.q011a.rest_linear_body_force_source((value, 0.0)) for value in waveform]
    )
    np.testing.assert_array_equal(source[:, 0, :], reference)

    moments = np.column_stack(
        (
            np.sum(source[:, 0, :], axis=1),
            source[:, 0, :] @ D2Q9_VELOCITIES[:, 0],
            source[:, 0, :] @ D2Q9_VELOCITIES[:, 1],
        )
    )
    expected = np.column_stack((np.zeros(q011b.SIZE), waveform, np.zeros(q011b.SIZE)))
    np.testing.assert_allclose(
        moments,
        expected,
        atol=q011b.SOURCE_MOMENT_TOLERANCE,
        rtol=0.0,
    )

    rest = uniform_equilibrium(q011b.SIZE, 1, np.zeros(3))
    observed = q011b.zero_mean_forced_filtered_bgk_periodic_step(
        rest,
        q011b.OMEGA,
        q011b.ETA,
        waveform[:, None],
    )
    np.testing.assert_array_equal(observed, q011b._stripe_step(rest))

    with pytest.raises(ValueError, match="two-dimensional"):
        q011b.spatial_body_force_source(waveform)
    with pytest.raises(ValueError, match="spatial shape"):
        q011b.zero_mean_forced_filtered_bgk_periodic_step(
            rest,
            q011b.OMEGA,
            q011b.ETA,
            np.zeros((q011b.SIZE, 2)),
        )


def test_q011b_replays_q011a_and_the_registered_source(
    q011b_cycle: dict,
) -> None:
    replay = q011b_cycle["q011a_replay_audit"]
    source = q011b_cycle["source_and_stage_audit"]

    assert replay["artifact_sha256"] == q011b.Q011A_ARTIFACT_SHA256
    assert replay["runner_sha256"] == q011b.Q011A_RUNNER_SHA256
    assert replay["source_digest_sha256"] == q011b.Q011A_SOURCE_DIGEST
    assert replay["probe_digest_sha256"] == q011b.Q011A_PROBE_DIGEST
    assert replay["result_digest_sha256"] == q011b.Q011A_RESULT_DIGEST
    assert replay["passed"]
    assert abs(source["float_waveform_sum"]) <= (q011b.WAVEFORM_SUM_TOLERANCE)
    assert (
        source["waveform_fft_relative_leakage_outside_plus_minus_one"]
        <= q011b.WAVEFORM_LEAKAGE_TOLERANCE
    )
    assert source["maximum_source_moment_residual"] <= (q011b.SOURCE_MOMENT_TOLERANCE)
    assert source["maximum_stage_replay_discrepancy"] <= (q011b.STAGE_REPLAY_TOLERANCE)
    assert source["passed"]


def test_q011b_fixed_leaf_basis_linear_response_and_jacobian_pass(
    q011b_cycle: dict,
) -> None:
    basis = q011b_cycle["fixed_leaf_basis_audit"]
    linear = q011b_cycle["linear_response_audit"]
    derivative = q011b_cycle["derivative_audit"]

    assert basis["basis_shape"] == [
        q011b.STRIPE_DIMENSION,
        q011b.FIXED_LEAF_DIMENSION,
    ]
    assert basis["orthogonality_frobenius_residual"] <= (q011b.BASIS_TOLERANCE)
    assert basis["moment_annihilation_frobenius_residual"] <= (q011b.BASIS_TOLERANCE)
    assert basis["passed"]
    assert linear["equation_relative_residual"] <= (q011b.LINEAR_RESPONSE_RESIDUAL_TOLERANCE)
    assert linear["passed"]
    assert derivative["seed"] == 20260812
    assert derivative["direction_count"] == 4
    assert derivative["steps"] == list(q011b.DERIVATIVE_STEPS)
    assert derivative["maximum_best_relative_error"] <= (q011b.DERIVATIVE_RELATIVE_TOLERANCE)
    assert all(record["passed"] for record in derivative["records"])
    assert derivative["passed"]


def test_q011b_newton_starts_converge_deterministically(
    q011b_cycle: dict,
) -> None:
    solver = q011b_cycle["solver_audit"]

    assert set(solver["primary_runs"]) == {"zero", "linear_response"}
    assert solver["validity_passed"]
    assert solver["hypothesis_passed"]
    for run in solver["primary_runs"].values():
        assert run["converged"]
        assert run["terminal_metrics"]["projected_l2"] <= (q011b.PROJECTED_RESIDUAL_TOLERANCE)
        assert run["terminal_metrics"]["full_l2"] <= (q011b.FULL_RESIDUAL_TOLERANCE)
        assert run["terminal_metrics"]["maximum_component"] <= (q011b.COMPONENT_RESIDUAL_TOLERANCE)
        assert len(run["trace"]) <= q011b.NEWTON_MAXIMUM_STEPS + 1
        for record in run["trace"]:
            if record["decision"] == "accepted_step":
                assert record["accepted_factor"] in (q011b.LINE_SEARCH_FACTORS)
                assert record["accepted_projected_l2"] < (record["projected_l2"])
    for replay in solver["determinism_replays"].values():
        assert replay["terminal_coordinate_bitwise_matches"]
        assert replay["trace_exact_json_matches"]
        assert replay["terminal_record_exact_json_matches"]
    assert solver["solution_population_l2_distance"] <= (q011b.SOLUTION_DISTANCE_TOLERANCE)
    assert solver["solution_relative_distance"] <= (q011b.SOLUTION_RELATIVE_DISTANCE_TOLERANCE)


def test_q011b_fixed_point_is_positive_on_the_registered_leaf(
    q011b_cycle: dict,
) -> None:
    physical = q011b_cycle["physical_fourier_audit"]

    assert physical["minimum_population"] > 0.0
    assert physical["minimum_density"] > 0.0
    assert physical["maximum_compensated_global_target_residual"] <= (q011b.GLOBAL_MOMENT_TOLERANCE)
    assert physical["first_harmonic_momentum_x_cosine_amplitude"] > q011b.AMPLITUDE
    assert (
        physical["departure_fft_relative_leakage_outside_zero_plus_minus_one_two"]
        <= q011b.SECTOR_LEAKAGE_TOLERANCE
    )
    assert physical["checks"]["lift_restriction_roundtrip_is_bitwise"]
    assert physical["checks"]["lift_is_exactly_x_independent"]
    assert physical["passed"]


def test_q011b_full_fixed_leaf_spectrum_passes(
    q011b_cycle: dict,
) -> None:
    spectrum = q011b_cycle["spectrum_audit"]

    assert spectrum["block_count"] == q011b.SIZE
    assert spectrum["zero_wave_unrestricted_unit_eigenvalue_count"] == 3
    assert spectrum["fixed_leaf_eigenvalue_count"] == (q011b.SITE_COUNT * 9 - 3)
    assert (
        spectrum["maximum_schur_reconstruction_relative_residual"] <= q011b.SCHUR_RESIDUAL_TOLERANCE
    )
    assert spectrum["maximum_schur_unitarity_frobenius_residual"] <= q011b.SCHUR_RESIDUAL_TOLERANCE
    assert (
        spectrum["maximum_conjugate_spectrum_absolute_hausdorff_error"]
        <= q011b.SPECTRUM_HAUSDORFF_TOLERANCE
    )
    assert spectrum["block_action_audit"]["maximum_relative_error"] <= (
        q011b.BLOCK_ACTION_RELATIVE_TOLERANCE
    )
    assert spectrum["maximum_fixed_leaf_eigenvalue_modulus"] <= (q011b.SPECTRAL_RADIUS_CEILING)
    assert spectrum["minimum_i_minus_j_singular_value"] >= (q011b.MINIMUM_RESOLVENT_SINGULAR_VALUE)
    assert spectrum["maximum_i_minus_j_condition_number"] <= (
        q011b.MAXIMUM_RESOLVENT_CONDITION_NUMBER
    )
    assert spectrum["passed"]
    assert spectrum["hypothesis_passed"]


def test_q011b_accepts_only_the_registered_numerical_result(
    q011b_cycle: dict,
) -> None:
    assert q011b_cycle["study_validity"] == "passed"
    assert q011b_cycle["hypothesis_outcome"] == "accepted"
    assert q011b_cycle["scientific_classification"] == (
        "zero-mean single-wave periodic forcing yields a numerically "
        "resolved stable fixed-leaf fixed point"
    )
    assert len(q011b_cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in q011b_cycle["validity_gates"].values())
    assert len(q011b_cycle["hypothesis_gates"]) == 4
    assert all(gate["passed"] for gate in q011b_cycle["hypothesis_gates"].values())
    consequence = q011b_cycle["numerical_consequence"]
    assert consequence["registered_fixed_point_is_numerically_resolved"]
    assert consequence["registered_fixed_point_is_strictly_stable_on_fixed_leaf"]
    assert not consequence["forced_slow_spectral_subspace_has_been_selected"]
    assert not consequence["forced_invariant_manifold_has_been_constructed"]
    assert not consequence["rigorous_existence_or_uniqueness_has_been_proved"]
    assert "binary64 Newton" in q011b_cycle["claim_boundary"]
    assert "not a rigorous existence" in q011b_cycle["claim_boundary"]
    assert not any(q011b_cycle["preserved_prior_outcomes"].values())


def test_q011b_records_reproducible_digests_and_runner_provenance(
    q011b_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011b_cycle["registered_parameters"],
        "q011a_replay_audit": q011b_cycle["q011a_replay_audit"],
        "source_and_stage_audit": q011b_cycle["source_and_stage_audit"],
        "fixed_leaf_basis_audit": q011b_cycle["fixed_leaf_basis_audit"],
    }
    fixed_point_sections = {
        "linear_response_audit": q011b_cycle["linear_response_audit"],
        "derivative_audit": q011b_cycle["derivative_audit"],
        "solver_audit": q011b_cycle["solver_audit"],
        "physical_fourier_audit": q011b_cycle["physical_fourier_audit"],
    }
    spectrum_sections = {
        "spectrum_audit": q011b_cycle["spectrum_audit"],
    }
    assert q011b_cycle["input_digest_sha256"] == (q011b._canonical_json_sha256(input_sections))
    assert q011b_cycle["fixed_point_digest_sha256"] == (
        q011b._canonical_json_sha256(fixed_point_sections)
    )
    assert q011b_cycle["spectrum_digest_sha256"] == (
        q011b._canonical_json_sha256(spectrum_sections)
    )
    assert q011b_cycle["result_digest_sha256"] == (
        q011b._canonical_json_sha256(q011b._result_digest_sections(q011b_cycle))
    )
    runner_path = Path(q011b.__file__).resolve()
    assert q011b_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert source_metadata()["package_version"] == "0.1.0"
    json.dumps(q011b_cycle, allow_nan=False)


def test_q011b_artifact_reproduces_the_accepted_fixed_point(
    q011b_cycle: dict,
) -> None:
    runner_path = Path(q011b.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011b_zero_mean_forced_fixed_point.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "477202184694da1386c6b5bc0f0441e004a7a44f7a7b064f1d060d50adc66c27"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011b_zero_mean_forced_fixed_point.py",
        "sha256": ("bac9448f280ce2dfb2e1627ce1558b792cb53e05746b94246baa6c329b8c8ef0"),
        "sha256_newline_normalization": ("UTF-8 text with universal newlines"),
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["cycle"] == q011b_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["input_digest_sha256"] == (
        "53dea81353ed4bcd77ab0c06533528f6d867d8b1bfa80d3d2ac3eddd7cf7dfbb"
    )
    assert artifact["cycle"]["fixed_point_digest_sha256"] == (
        "8db05ad1e7ae7806b70b6330d798f6dad05bc8718027ba13cb315116b021b17c"
    )
    assert artifact["cycle"]["spectrum_digest_sha256"] == (
        "3ab8866e141b64a4d1d81bdfae1a70c61d8e7964d8480e2bd7ec7c7e174850fc"
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        "66c4b579dbd7d7c391fd2017f165c2de251ecf850b7c485cb936b9742c8addf6"
    )
