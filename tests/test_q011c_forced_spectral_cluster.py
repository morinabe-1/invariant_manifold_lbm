from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import research.q011b_zero_mean_forced_fixed_point as q011b
import research.q011c_forced_spectral_cluster as q011c
from ttim_lbm.d2q9 import uniform_equilibrium
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011c_cycle() -> dict:
    return q011c.run_forced_spectral_cluster_audit()


def test_q011c_scaled_map_reuses_the_q011b_endpoint_force() -> None:
    rest = uniform_equilibrium(q011c.SIZE, 1, np.zeros(3))

    np.testing.assert_allclose(q011c._scaled_step(rest, 0.0), rest, atol=1.0e-16, rtol=0.0)
    np.testing.assert_array_equal(q011c._scaled_step(rest, 1.0), q011b._stripe_step(rest))
    assert q011c.AMPLITUDE_FACTORS == tuple(index / 8.0 for index in range(9))
    assert q011c.CHECKPOINT_FACTORS == (0.0, 0.5, 1.0)


def test_q011c_ordered_cluster_selects_a_subspace_not_branch_labels() -> None:
    matrix = np.diag(np.asarray([0.92 + 0.03j, 0.81 - 0.02j, 0.4, -0.2j]))
    targets = np.asarray([0.81 - 0.02j, 0.92 + 0.03j])

    cluster = q011c._ordered_cluster(matrix, targets)

    assert cluster.selected_dimension == 2
    assert cluster.selector_count == 2
    assert q011c._hausdorff(cluster.selected_eigenvalues, targets) <= 1.0e-15
    assert cluster.external_eigenvalue_separation > 0.4
    assert cluster.projector_norm == pytest.approx(1.0)
    assert cluster.schur_reconstruction_relative_residual <= 1.0e-15
    assert cluster.invariance_relative_residual <= 1.0e-15


def test_q011c_replays_sealed_inputs_and_closes_fixed_point_paths(
    q011c_cycle: dict,
) -> None:
    sealed = q011c_cycle["sealed_input_audit"]
    path = q011c_cycle["fixed_point_path_audit"]

    assert sealed["passed"]
    assert all(sealed["checks"].values())
    assert path["passed"]
    assert path["amplitude_factors"] == list(q011c.AMPLITUDE_FACTORS)
    assert len(path["forward_records"]) == 9
    assert len(path["backward_records"]) == 9
    assert len(path["forward_backward_comparisons"]) == 9
    assert path["endpoint_population_l2_distance"] <= q011c.STATE_DISTANCE_TOLERANCE
    assert path["endpoint_relative_distance"] <= q011c.STATE_RELATIVE_DISTANCE_TOLERANCE
    assert not path["forward_backward_comparisons"][0]["relative_gate_applicable"]
    assert all(
        record["relative_gate_applicable"] for record in path["forward_backward_comparisons"][1:]
    )


def test_q011c_reference_and_cluster_path_pass_registered_diagnostics(
    q011c_cycle: dict,
) -> None:
    reference = q011c_cycle["unforced_reference_audit"]
    path = q011c_cycle["cluster_path_audit"]
    summary = path["summary"]

    assert reference["total_selected_complex_dimension"] == 24
    assert reference["physical_real_dimension_under_conjugacy"] == 24
    assert reference["passed"]
    assert path["structural_passed"]
    assert path["hypothesis_passed"]
    assert all(path["structural_checks"].values())
    assert all(path["hypothesis_checks"].values())
    assert summary["maximum_adjacent_principal_angle"] <= q011c.ADJACENT_ANGLE_TOLERANCE
    assert summary["minimum_reference_alignment"] >= q011c.REFERENCE_ALIGNMENT_FLOOR
    assert (
        summary["minimum_external_eigenvalue_separation"]
        >= q011c.EXTERNAL_EIGENVALUE_SEPARATION_FLOOR
    )
    assert summary["maximum_projector_two_norm"] <= q011c.PROJECTOR_NORM_CEILING
    assert summary["maximum_structural_residual"] <= q011c.STRUCTURAL_RESIDUAL_TOLERANCE
    assert summary["maximum_path_reversal_principal_angle"] <= q011c.REVERSAL_ANGLE_TOLERANCE
    assert summary["maximum_direct_endpoint_principal_angle"] <= (
        q011c.DIRECT_ENDPOINT_ANGLE_TOLERANCE
    )


def test_q011c_checkpoint_science_passes_but_endpoint_reproduction_is_invalid(
    q011c_cycle: dict,
) -> None:
    audit = q011c_cycle["checkpoint_spectrum_audit"]
    endpoint = audit["checkpoint_records"][-1]["q011b_endpoint_reproduction"]

    assert len(audit["checkpoint_records"]) == 3
    assert all(
        record["full_fixed_leaf_eigenvalue_count"] == q011c.SIZE * q011c.SIZE * 9 - 3
        for record in audit["checkpoint_records"]
    )
    assert audit["hypothesis_passed"]
    assert all(audit["hypothesis_checks"].values())
    assert audit["minimum_sylvester_separation"] >= q011c.SYLVESTER_SEPARATION_FLOOR
    assert audit["minimum_global_modulus_normal_dominance_gap"] >= q011c.NORMAL_DOMINANCE_GAP_FLOOR
    assert audit["maximum_full_fixed_leaf_spectral_radius"] <= q011b.SPECTRAL_RADIUS_CEILING

    assert not audit["validity_passed"]
    assert not audit["validity_checks"]["q011b_endpoint_spectrum_reproduces"]
    assert endpoint["checks"]["unit_count_matches"]
    assert endpoint["checks"]["spectral_radius_reproduces"]
    assert endpoint["checks"]["spectral_radius_witness_matches"]
    assert endpoint["checks"]["minimum_singular_value_reproduces"]
    assert not endpoint["checks"]["maximum_condition_number_reproduces"]
    assert not endpoint["checks"]["minimum_singular_witness_matches"]
    assert not endpoint["checks"]["maximum_condition_witness_matches"]
    assert (
        endpoint["absolute_differences_from_q011b"]["maximum_condition_number"]
        > q011c.ENDPOINT_REPRODUCTION_TOLERANCE
    )
    assert endpoint["full_spectrum_radius_reproduces"]
    assert not endpoint["passed"]


def test_q011c_reports_the_preregistered_inconclusive_outcome(
    q011c_cycle: dict,
) -> None:
    validity = q011c_cycle["validity_gates"]

    assert len(validity) == 6
    assert sum(not gate["passed"] for gate in validity.values()) == 1
    assert not validity["checkpoint_spectrum_and_q011b_endpoint_reproduce"]["passed"]
    assert q011c_cycle["study_validity"] == "failed"
    assert q011c_cycle["hypothesis_outcome"] == "inconclusive"
    assert q011c_cycle["scientific_classification"] == (
        "registered forced spectral-cluster audit is invalid"
    )
    assert not any(gate["passed"] for gate in q011c_cycle["hypothesis_gates"].values())
    assert not q011c_cycle["numerical_consequence"][
        "registered_forced_cluster_is_linearly_selected"
    ]
    assert not any(q011c_cycle["preserved_prior_outcomes"].values())
    assert "Localize the first failed" in q011c_cycle["next_change"]


def test_q011c_records_reproducible_digests_and_runner_provenance(
    q011c_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011c_cycle["registered_parameters"],
        "sealed_input_audit": q011c_cycle["sealed_input_audit"],
        "fixed_leaf_basis_audit": q011c_cycle["fixed_leaf_basis_audit"],
        "unforced_reference_audit": q011c_cycle["unforced_reference_audit"],
    }
    path_sections = {
        "fixed_point_path_audit": q011c_cycle["fixed_point_path_audit"],
        "cluster_path_audit": q011c_cycle["cluster_path_audit"],
    }
    spectrum_sections = {
        "checkpoint_spectrum_audit": q011c_cycle["checkpoint_spectrum_audit"],
    }

    assert q011c_cycle["input_digest_sha256"] == q011c._canonical_json_sha256(input_sections)
    assert q011c_cycle["path_digest_sha256"] == q011c._canonical_json_sha256(path_sections)
    assert q011c_cycle["spectrum_digest_sha256"] == q011c._canonical_json_sha256(spectrum_sections)
    assert q011c_cycle["result_digest_sha256"] == q011c._canonical_json_sha256(
        q011c._result_digest_sections(q011c_cycle)
    )
    runner_path = Path(q011c.__file__).resolve()
    assert q011c_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    json.dumps(q011c_cycle, allow_nan=False)


def test_q011c_artifact_reproduces_the_inconclusive_endpoint_audit(
    q011c_cycle: dict,
) -> None:
    runner_path = Path(q011c.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011c_forced_spectral_cluster.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "dbb562dd3628dc7589219baa94ae6791e084847f302c69dbcdc328b94ac6d2b3"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011c_forced_spectral_cluster.py",
        "sha256": "10222da26fe14b97cd9565c517838d3a03e21f19e605d4a60cb2461e011d1d13",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["cycle"] == q011c_cycle
    assert artifact["study_gate"] == "failed"
    assert artifact["scientific_outcome"] == "inconclusive"
    assert artifact["cycle"]["input_digest_sha256"] == (
        "7d8d4a593dc29a715c995e237890da4de17314c4feffabe10111b289120435ee"
    )
    assert artifact["cycle"]["path_digest_sha256"] == (
        "06254ea5569d8b0c8c5369477c82ea685284aec9970574c46c24fea749280b92"
    )
    assert artifact["cycle"]["spectrum_digest_sha256"] == (
        "5b1e79280b752268248f5150dd12c73a96719cb20d86cbd34fb3ff1e1b8b472c"
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        "4b41c4e7bda3a45f1ece871c183d321bed637d255053e22a82e7000dd83f5751"
    )
