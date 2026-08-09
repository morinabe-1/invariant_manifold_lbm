from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q011c1_endpoint_localization as q011c1
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011c1_cycle() -> dict:
    return q011c1.run_endpoint_localization_audit()


def test_q011c1_registered_orbits_partition_every_wave_once() -> None:
    flattened = [index for orbit in q011c1.ORBIT_PARTITION for index in orbit]

    assert sorted(flattened) == list(range(q011c1.SIZE))
    assert len(flattened) == len(set(flattened))
    assert q011c1._orbit_for_index(0) == (0,)
    assert q011c1._orbit_for_index(1) == (1, 16)
    assert q011c1._orbit_for_index(16) == (1, 16)
    assert q011c1._orbit_for_index(8) == (8, 9)
    with pytest.raises(ValueError, match="outside"):
        q011c1._orbit_for_index(q011c1.SIZE)


def test_q011c1_replays_the_sealed_inconclusive_q011c_cycle(
    q011c1_cycle: dict,
) -> None:
    sealed = q011c1_cycle["sealed_replay_audit"]

    assert sealed["passed"]
    assert all(sealed["checks"].values())
    assert sealed["q011c_artifact"]["failed_validity_gates"] == [
        "checkpoint_spectrum_and_q011b_endpoint_reproduce"
    ]
    assert sealed["q011c_artifact"]["study_validity"] == "failed"
    assert sealed["q011c_artifact"]["hypothesis_outcome"] == "inconclusive"
    assert sealed["raw_q011c_diagnostics"]["fixed_point_path_passed"]
    assert sealed["raw_q011c_diagnostics"]["cluster_structural_passed"]
    assert sealed["raw_q011c_diagnostics"]["cluster_hypothesis_passed"]
    assert sealed["raw_q011c_diagnostics"]["checkpoint_hypothesis_passed"]


def test_q011c1_full_svd_and_matrix_conjugacy_are_structural(
    q011c1_cycle: dict,
) -> None:
    for key in (
        "stored_endpoint_block_audit",
        "continued_endpoint_block_audit",
    ):
        audit = q011c1_cycle[key]
        assert len(audit["block_records"]) == q011c1.SIZE
        assert audit["maximum_svd_reconstruction_relative_residual"] <= (
            q011c1.SVD_STRUCTURAL_TOLERANCE
        )
        assert audit["maximum_svd_unitarity_frobenius_residual"] <= (
            q011c1.SVD_STRUCTURAL_TOLERANCE
        )
        assert audit["passed"]

    for key in (
        "stored_matrix_conjugacy_audit",
        "continued_matrix_conjugacy_audit",
    ):
        audit = q011c1_cycle[key]
        assert len(audit["records"]) == 8
        assert audit["maximum_matrix_conjugacy_relative_frobenius_residual"] <= (
            q011c1.MATRIX_CONJUGACY_TOLERANCE
        )
        assert audit["passed"]


def test_q011c1_preserves_the_original_controls_and_failure(
    q011c1_cycle: dict,
) -> None:
    audit = q011c1_cycle["endpoint_control_audit"]
    stored = audit["stored_endpoint_control"]
    continued = audit["continued_endpoint_control"]

    assert audit["passed"]
    assert stored["passed"]
    assert audit["stored_witness_indices"] == {
        "spectral_radius": 0,
        "minimum_singular_value": 16,
        "maximum_condition_number": 16,
    }
    assert not continued["passed"]
    assert continued["checks"]["spectral_radius_reproduces"]
    assert continued["checks"]["minimum_singular_value_reproduces"]
    assert not continued["checks"]["maximum_condition_number_reproduces"]
    assert audit["continued_witness_indices"] == {
        "spectral_radius": 0,
        "minimum_singular_value": 1,
        "maximum_condition_number": 1,
    }


def test_q011c1_encloses_changes_and_separates_extremal_orbits(
    q011c1_cycle: dict,
) -> None:
    audit = q011c1_cycle["perturbation_enclosure_audit"]

    assert len(audit["block_records"]) == q011c1.SIZE
    assert all(record["passed"] for record in audit["block_records"])
    assert all(audit["checks"].values())
    assert audit["maximum_minimum_singular_change_utilization"] <= 1.0
    assert audit["maximum_maximum_singular_change_utilization"] <= 1.0
    assert audit["minimum_singular_orbit_separation_margin"] > 0.0
    assert audit["maximum_condition_orbit_separation_margin"] > 0.0
    expected_orbits = {
        "spectral_radius": [0],
        "minimum_singular_value": [1, 16],
        "maximum_condition_number": [1, 16],
    }
    assert audit["stored_extremal_orbits"] == expected_orbits
    assert audit["continued_extremal_orbits"] == expected_orbits
    assert audit["exact_control_witness_exchange"] == {
        "stored_minimum_singular_witness": 16,
        "continued_minimum_singular_witness": 1,
        "stored_maximum_condition_witness": 16,
        "continued_maximum_condition_witness": 1,
    }
    assert audit["passed"]


def test_q011c1_accepts_only_failure_localization(
    q011c1_cycle: dict,
) -> None:
    assert len(q011c1_cycle["validity_gates"]) == 5
    assert all(gate["passed"] for gate in q011c1_cycle["validity_gates"].values())
    assert len(q011c1_cycle["hypothesis_gates"]) == 4
    assert all(gate["passed"] for gate in q011c1_cycle["hypothesis_gates"].values())
    assert q011c1_cycle["study_validity"] == "passed"
    assert q011c1_cycle["hypothesis_outcome"] == "accepted"
    assert q011c1_cycle["scientific_classification"] == (
        "the Q011c endpoint failure is localized to perturbation-"
        "consistent conjugate-witness tie instability"
    )
    consequence = q011c1_cycle["numerical_consequence"]
    assert consequence["q011c_endpoint_failure_is_localized"]
    assert not consequence["q011c_original_inconclusive_outcome_changed"]
    assert not consequence["q011c_cluster_is_regraded_as_accepted"]
    assert not consequence["forced_spectral_cluster_is_selected"]
    assert not any(q011c1_cycle["preserved_prior_outcomes"].values())
    assert "does not regrade Q011c" in q011c1_cycle["claim_boundary"]


def test_q011c1_records_reproducible_digests_and_runner_provenance(
    q011c1_cycle: dict,
) -> None:
    input_sections = {
        "registered_parameters": q011c1_cycle["registered_parameters"],
        "sealed_replay_audit": q011c1_cycle["sealed_replay_audit"],
    }
    metric_sections = {
        "stored_endpoint_block_audit": q011c1_cycle["stored_endpoint_block_audit"],
        "continued_endpoint_block_audit": q011c1_cycle["continued_endpoint_block_audit"],
        "stored_matrix_conjugacy_audit": q011c1_cycle["stored_matrix_conjugacy_audit"],
        "continued_matrix_conjugacy_audit": q011c1_cycle["continued_matrix_conjugacy_audit"],
        "endpoint_control_audit": q011c1_cycle["endpoint_control_audit"],
    }
    enclosure_sections = {
        "perturbation_enclosure_audit": q011c1_cycle["perturbation_enclosure_audit"],
    }

    assert q011c1_cycle["input_digest_sha256"] == q011c1.q011c._canonical_json_sha256(
        input_sections
    )
    assert q011c1_cycle["metric_digest_sha256"] == q011c1.q011c._canonical_json_sha256(
        metric_sections
    )
    assert q011c1_cycle["enclosure_digest_sha256"] == q011c1.q011c._canonical_json_sha256(
        enclosure_sections
    )
    assert q011c1_cycle["result_digest_sha256"] == q011c1.q011c._canonical_json_sha256(
        q011c1._result_digest_sections(q011c1_cycle)
    )
    runner_path = Path(q011c1.__file__).resolve()
    assert q011c1_cycle["runner_source"] == {
        "filename": runner_path.name,
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    json.dumps(q011c1_cycle, allow_nan=False)


def test_q011c1_artifact_reproduces_the_accepted_localization(
    q011c1_cycle: dict,
) -> None:
    runner_path = Path(q011c1.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011c1_endpoint_localization.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "939baa85fa4db1efaf701985d81665f863e5f77f6ec2c95cfc2bacf004c0c45c"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011c1_endpoint_localization.py",
        "sha256": "1f777dc50c6748cb8d8a64d643822b55733ac247b5de7d08b119d628b63c52a6",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["cycle"] == q011c1_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["input_digest_sha256"] == (
        "e9ea01348fe839dd745c3ccb7cf2e622bec3c0a4f080a1ab1c62a92a02ced064"
    )
    assert artifact["cycle"]["metric_digest_sha256"] == (
        "fca5a81f3fc47e24a6f17578065adb527d892400d5d88c8eb18cf7089e234a9e"
    )
    assert artifact["cycle"]["enclosure_digest_sha256"] == (
        "7a6cd761f88b328c2ffa74de5b9fb7952f454b86a99630d6266973e8fa6fea20"
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        "ad8b47548ebc04595246301864314502158e686520197377b3a33d30db1d4f86"
    )
