from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q011c2_heldout_cluster_reissue as q011c2
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011c2_cycle() -> dict:
    return q011c2.run_heldout_cluster_reissue_audit()


def test_q011c2_training_and_holdout_nodes_partition_the_fine_path() -> None:
    training = set(q011c2.TRAINING_FACTORS)
    heldout = set(q011c2.HELDOUT_FACTORS)

    assert len(q011c2.FINE_FACTORS) == 17
    assert len(training) == 9
    assert len(heldout) == 8
    assert training.isdisjoint(heldout)
    assert training | heldout == set(q011c2.FINE_FACTORS)
    assert q011c2.FINE_FACTORS == tuple(index / 16.0 for index in range(17))
    assert q011c2.HELDOUT_FACTORS == tuple((2 * index + 1) / 16.0 for index in range(8))


def test_q011c2_replays_sealed_q011c1_and_preserves_q011c(
    q011c2_cycle: dict,
) -> None:
    sealed = q011c2_cycle["sealed_replay_audit"]

    assert sealed["passed"]
    assert all(sealed["checks"].values())
    assert sealed["q011c1_artifact"]["study_validity"] == "passed"
    assert sealed["q011c1_artifact"]["hypothesis_outcome"] == "accepted"
    assert sealed["q011c_artifact"]["study_validity"] == "failed"
    assert sealed["q011c_artifact"]["hypothesis_outcome"] == "inconclusive"


def test_q011c2_seventeen_node_fixed_point_paths_close_and_stay_positive(
    q011c2_cycle: dict,
) -> None:
    audit = q011c2_cycle["fine_fixed_point_path_audit"]

    assert audit["amplitude_factors"] == list(q011c2.FINE_FACTORS)
    assert audit["training_factors"] == list(q011c2.TRAINING_FACTORS)
    assert audit["heldout_factors"] == list(q011c2.HELDOUT_FACTORS)
    assert len(audit["forward_records"]) == 17
    assert len(audit["backward_records"]) == 17
    assert len(audit["forward_backward_comparisons"]) == 17
    assert len(audit["training_state_comparisons"]) == 9
    assert all(record["converged"] for record in audit["forward_records"])
    assert all(record["converged"] for record in audit["backward_records"])
    assert audit["endpoint_population_l2_distance"] <= (q011c2.STATE_DISTANCE_TOLERANCE)
    assert audit["endpoint_relative_distance"] <= (q011c2.STATE_RELATIVE_DISTANCE_TOLERANCE)
    assert audit["minimum_population"] > 0.0
    assert audit["minimum_density"] > 0.0
    assert all(audit["checks"].values())
    assert audit["passed"]


def test_q011c2_cluster_path_and_controls_pass_at_all_nodes(
    q011c2_cycle: dict,
) -> None:
    audit = q011c2_cycle["fine_cluster_path_audit"]
    summary = audit["summary"]

    assert len(audit["forward_node_records"]) == 17
    assert len(audit["backward_node_records"]) == 17
    assert len(audit["training_cluster_comparisons"]) == 27
    assert len(audit["canonical_stored_endpoint_records"]) == 3
    assert audit["structural_passed"]
    assert audit["control_passed"]
    assert audit["hypothesis_passed"]
    assert all(audit["structural_checks"].values())
    assert all(audit["control_checks"].values())
    assert all(audit["hypothesis_checks"].values())
    assert summary["maximum_adjacent_principal_angle"] <= (q011c2.q011c.ADJACENT_ANGLE_TOLERANCE)
    assert summary["minimum_reference_alignment"] >= (q011c2.q011c.REFERENCE_ALIGNMENT_FLOOR)
    assert summary["minimum_external_eigenvalue_separation"] >= (
        q011c2.q011c.EXTERNAL_EIGENVALUE_SEPARATION_FLOOR
    )
    assert summary["maximum_projector_two_norm"] <= (q011c2.q011c.PROJECTOR_NORM_CEILING)
    assert summary["maximum_training_cluster_principal_angle"] <= (
        q011c2.TRAINING_CLUSTER_ANGLE_TOLERANCE
    )
    assert summary["maximum_training_spectrum_hausdorff_error"] <= (
        q011c2.TRAINING_SPECTRUM_TOLERANCE
    )
    assert summary["maximum_canonical_endpoint_principal_angle"] <= (
        q011c2.CANONICAL_ENDPOINT_ANGLE_TOLERANCE
    )


def test_q011c2_all_eight_heldout_spectra_and_sylvester_families_pass(
    q011c2_cycle: dict,
) -> None:
    audit = q011c2_cycle["heldout_checkpoint_audit"]

    assert audit["heldout_factors"] == list(q011c2.HELDOUT_FACTORS)
    assert len(audit["checkpoint_records"]) == 8
    assert sum(len(record["sylvester_records"]) for record in audit["checkpoint_records"]) == 24
    for record in audit["checkpoint_records"]:
        assert record["selected_eigenvalue_count"] == 24
        assert record["external_eigenvalue_count"] == 2574
        assert record["full_fixed_leaf_eigenvalue_count"] == 2598
        assert all(record["checks"].values())
        assert all(record["hypothesis_checks"].values())
    assert audit["minimum_sylvester_separation"] >= (q011c2.q011c.SYLVESTER_SEPARATION_FLOOR)
    assert audit["minimum_global_modulus_normal_dominance_gap"] >= (
        q011c2.q011c.NORMAL_DOMINANCE_GAP_FLOOR
    )
    assert audit["maximum_full_fixed_leaf_spectral_radius"] <= (
        q011c2.q011b.SPECTRAL_RADIUS_CEILING
    )
    assert audit["validity_passed"]
    assert audit["hypothesis_passed"]


def test_q011c2_endpoint_orbit_semantics_pass_without_index_gate(
    q011c2_cycle: dict,
) -> None:
    audit = q011c2_cycle["endpoint_orbit_semantics_audit"]
    expected = {
        "spectral_radius": [0],
        "minimum_singular_value": [1, 16],
        "maximum_condition_number": [1, 16],
    }

    assert len(audit["perturbation_records"]) == 17
    assert all(record["passed"] for record in audit["perturbation_records"])
    assert audit["stored_extremal_orbits"] == expected
    assert audit["continued_extremal_orbits"] == expected
    assert audit["minimum_singular_orbit_separation_margin"] > 0.0
    assert audit["maximum_condition_orbit_separation_margin"] > 0.0
    assert audit["structural_passed"]
    assert audit["hypothesis_passed"]
    assert all(audit["structural_checks"].values())
    assert all(audit["hypothesis_checks"].values())


def test_q011c2_accepts_the_heldout_cluster_without_regrading_q011c(
    q011c2_cycle: dict,
) -> None:
    assert len(q011c2_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011c2_cycle["validity_gates"].values())
    assert len(q011c2_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011c2_cycle["hypothesis_gates"].values())
    assert q011c2_cycle["study_validity"] == "passed"
    assert q011c2_cycle["hypothesis_outcome"] == "accepted"
    assert q011c2_cycle["scientific_classification"] == (
        "the forced first-shell cluster passes a conjugacy-orbit "
        "reissue with eight held-out amplitude nodes"
    )
    consequence = q011c2_cycle["numerical_consequence"]
    assert consequence["forced_candidate_spectral_cluster_is_selected"]
    assert not consequence["q011c_original_inconclusive_outcome_changed"]
    assert not consequence["q011c1_localization_outcome_changed"]
    assert not consequence["individual_forced_modes_are_labeled"]
    assert not consequence["forced_external_nonresonance_is_certified"]
    assert not consequence["forced_invariant_manifold_is_constructed"]
    assert not any(q011c2_cycle["preserved_prior_outcomes"].values())


def test_q011c2_records_reproducible_digests_and_runner_provenance(
    q011c2_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011c2_cycle["registered_parameters"],
        "sealed_replay_audit": q011c2_cycle["sealed_replay_audit"],
    }
    path_sections = {
        "fine_fixed_point_path_audit": q011c2_cycle["fine_fixed_point_path_audit"],
        "fine_cluster_path_audit": q011c2_cycle["fine_cluster_path_audit"],
    }
    holdout_sections = {
        "heldout_checkpoint_audit": q011c2_cycle["heldout_checkpoint_audit"],
    }
    endpoint_sections = {
        "endpoint_orbit_semantics_audit": q011c2_cycle["endpoint_orbit_semantics_audit"],
    }

    assert q011c2_cycle["input_digest_sha256"] == (
        q011c2.q011c._canonical_json_sha256(input_sections)
    )
    assert q011c2_cycle["path_digest_sha256"] == (
        q011c2.q011c._canonical_json_sha256(path_sections)
    )
    assert q011c2_cycle["holdout_spectrum_digest_sha256"] == (
        q011c2.q011c._canonical_json_sha256(holdout_sections)
    )
    assert q011c2_cycle["endpoint_digest_sha256"] == (
        q011c2.q011c._canonical_json_sha256(endpoint_sections)
    )
    assert q011c2_cycle["result_digest_sha256"] == (
        q011c2.q011c._canonical_json_sha256(q011c2._result_digest_sections(q011c2_cycle))
    )
    runner_path = Path(q011c2.__file__).resolve()
    assert q011c2_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    json.dumps(q011c2_cycle, allow_nan=False)
