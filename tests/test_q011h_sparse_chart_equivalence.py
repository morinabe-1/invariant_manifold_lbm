from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q011h_sparse_chart_equivalence as q011h
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011h_cycle() -> dict[str, object]:
    return q011h.run_sparse_chart_equivalence_audit()


def test_q011h_registered_inputs_are_held_out_and_reproducible() -> None:
    directions, amplitudes, audit = q011h._direction_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert directions.shape == (q011h.DIRECTION_COUNT, q011h.SELECTED_DIMENSION)
    assert amplitudes.tolist() == list(q011h.AMPLITUDES)
    assert audit["direction_sha256"] == q011h.DIRECTION_SHA256
    assert audit["amplitude_sha256"] == q011h.AMPLITUDE_SHA256
    assert audit["prior_direction_exact_duplicate_count"] == 0
    assert audit["prior_amplitude_exact_duplicate_count"] == 0


def test_q011h_seals_q011g_and_preserves_prior_outcomes() -> None:
    audit, artifact = q011h._sealed_q011g_artifact_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["artifact"]["hypothesis_outcome"] == "rejected"
    assert audit["preserved_q011f1_outcome"]["hypothesis_outcome"] == "accepted"
    assert audit["preserved_q011f_outcome"]["hypothesis_outcome"] == "rejected"
    assert not artifact["cycle"]["decision_consequence"]["tt_cross_followup_is_authorized"]


def test_q011h_sparse_runtime_excludes_dense_quadratic_coefficients(
    q011h_cycle: dict[str, object],
) -> None:
    audit = q011h_cycle["sparse_runtime_path_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert set(audit["field_names"]).isdisjoint(
        {
            "hessian",
            "reduced_hessian",
            "w_tensor",
            "r_tensor",
            "native_chart_hessian",
            "native_reduced_hessian",
        }
    )


def test_q011h_registered_campaign_is_complete_and_accepted(
    q011h_cycle: dict[str, object],
) -> None:
    campaign = q011h_cycle["trajectory_campaign"]

    assert q011h_cycle["study_validity"] == "passed"
    assert q011h_cycle["hypothesis_outcome"] == "accepted"
    assert q011h_cycle["scientific_classification"] == (
        "the natural Fourier-sparse chart reproduces the dense forced "
        "quadratic reduced trajectory through 64 steps"
    )
    assert len(q011h_cycle["validity_gates"]) == 5
    assert all(gate["passed"] for gate in q011h_cycle["validity_gates"].values())
    assert len(q011h_cycle["hypothesis_gates"]) == 4
    assert all(gate["passed"] for gate in q011h_cycle["hypothesis_gates"].values())
    assert campaign["trajectory_count"] == q011h.TRAJECTORY_COUNT
    assert campaign["state_record_count"] == q011h.STATE_RECORD_COUNT
    assert campaign["dense_reduced_update_count"] == q011h.UPDATE_COUNT_PER_IMPLEMENTATION
    assert campaign["sparse_reduced_update_count"] == q011h.UPDATE_COUNT_PER_IMPLEMENTATION
    assert campaign["common_input_action_comparison_count"] == (q011h.ACTION_COMPARISON_COUNT)
    assert campaign["dense_checkpoint_defect_count"] == (q011h.CHECKPOINT_COUNT_PER_IMPLEMENTATION)
    assert campaign["sparse_checkpoint_defect_count"] == (q011h.CHECKPOINT_COUNT_PER_IMPLEMENTATION)
    assert campaign["maximum_common_input_joint_action_relative_error"] <= (
        q011h.MAXIMUM_ACTION_RELATIVE_ERROR
    )
    assert campaign["maximum_sparse_realification_imaginary_leakage"] <= (
        q011h.MAXIMUM_IMAGINARY_LEAKAGE
    )
    assert campaign["maximum_coordinate_error_over_initial_coordinate_norm"] <= (
        q011h.MAXIMUM_COORDINATE_SCALED_ERROR
    )
    assert campaign["maximum_state_error_over_initial_tangent_perturbation_norm"] <= (
        q011h.MAXIMUM_STATE_SCALED_ERROR
    )
    assert campaign["maximum_defect_vector_error_over_initial_coordinate_norm"] <= (
        q011h.MAXIMUM_DEFECT_SCALED_ERROR
    )
    assert campaign["maximum_defect_norm_difference_over_initial_coordinate_norm"] <= (
        q011h.MAXIMUM_DEFECT_NORM_SCALED_DIFFERENCE
    )
    assert campaign["minimum_population"] > 0.0
    assert campaign["maximum_global_conservation_drift"] <= (q011h.MAXIMUM_CONSERVATION_DRIFT)
    assert campaign["passed"]
    assert all(campaign["checks"].values())


def test_q011h_cycle_is_strict_json_with_reproducible_result_digest(
    q011h_cycle: dict[str, object],
) -> None:
    json.dumps(q011h_cycle, allow_nan=False)
    assert q011h_cycle["result_digest_sha256"] == (
        q011h.q011e.q011c._canonical_json_sha256(q011h._result_digest_sections(q011h_cycle))
    )
    assert not q011h_cycle["decision_consequence"]["tt_cross_followup_is_authorized"]
    assert not q011h_cycle["decision_consequence"][
        "full_state_64_step_shadowing_is_newly_certified"
    ]


def test_q011h_artifact_records_the_registered_equivalence_campaign() -> None:
    runner_path = Path(q011h.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011h_sparse_chart_equivalence.json"
    if not artifact_path.exists():
        pytest.skip("Q011h artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]
    campaign = cycle["trajectory_campaign"]

    assert _file_sha256(artifact_path) == (
        "2cfcf5cb76698ae8e451f448a3048e3d29a1b8aed034d3afa5c25f7fd66038f5"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011h_sparse_chart_equivalence.py",
        "sha256": "1e6848e572137d019531514235741b18ca10644dd7d14e304dc26d92d81cda9e",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    assert cycle["input_digest_sha256"] == (
        "c9ea06c8961940f54dd3c02e3d68d7ba777e77fc9be2f0a7c3eecab5ab257b83"
    )
    assert cycle["coefficient_digest_sha256"] == (
        "2ab44a23811ef9f7e1975fb27561dd92660938778bf73ef149e46ed04f399669"
    )
    assert cycle["campaign_digest_sha256"] == (
        "bbb6a489fc76af150a3a162f585b0b2e1a65d0445d5eb14ab11b280bc492a035"
    )
    assert cycle["result_digest_sha256"] == (
        "a78812d93063ed7deeaca09dad5feb2cf018fb1bec315dab94b4f02d27f75864"
    )
    assert campaign["state_metric_sha256"] == (
        "298efab077e38fe3d31b146460558219675ab88ab9c0182ad3fb14e25a52d854"
    )
    assert campaign["checkpoint_metric_sha256"] == (
        "7fd9446be00f5822f7aee5a2750b03b36d5b0f4b1916e123878b824cba95757b"
    )
    assert cycle["result_digest_sha256"] == (
        q011h.q011e.q011c._canonical_json_sha256(q011h._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
