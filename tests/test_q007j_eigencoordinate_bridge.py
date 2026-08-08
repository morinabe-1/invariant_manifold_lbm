from __future__ import annotations

import json

import pytest

from research.q007j_eigencoordinate_bridge import (
    EXPECTED_SYSTEM_COUNT,
    EXPECTED_TRANSPORTED_MODE_COUNT,
    MAXIMUM_KRAWCZYK_UTILIZATION,
    MAXIMUM_MODE_CORRECTION,
    MINIMUM_OVERLAP_MODULUS,
    REGISTERED_INPUT_SHA256,
    run_eigencoordinate_bridge_audit,
    run_q007j_study,
)
from ttim_lbm.provenance import source_metadata


@pytest.fixture(scope="module")
def eigencoordinate_audit():
    return run_eigencoordinate_bridge_audit()


def test_q007j_certifies_all_twelve_krawczyk_systems(
    eigencoordinate_audit,
) -> None:
    audit = eigencoordinate_audit
    certification = audit["krawczyk_certification"]

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert audit["scientific_classification"] == (
        "registered selected eigencoordinates rigorously bridge to the "
        "theorem spectral subspace"
    )
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert all(gate["passed"] for gate in audit["hypothesis_gates"].values())
    assert certification["system_count"] == EXPECTED_SYSTEM_COUNT
    assert certification["all_krawczyk_images_interior"]
    assert certification["maximum_krawczyk_utilization"]["float"] <= float(
        MAXIMUM_KRAWCZYK_UTILIZATION
    )
    assert all(record["included"] for record in certification["records"])
    assert audit["interval_construction"][
        "maximum_interval_contraction_bound"
    ]["float"] < 1.0
    json.dumps(audit, allow_nan=False)


def test_q007j_reproduces_inputs_and_assigns_six_distinct_discs(
    eigencoordinate_audit,
) -> None:
    audit = eigencoordinate_audit
    inputs = audit["input_artifacts"]
    association = audit["disc_association"]

    assert all(record["passed"] for record in inputs.values())
    assert {
        name: record["sha256"] for name, record in inputs.items()
    } == REGISTERED_INPUT_SHA256
    assert audit["coefficient_reproduction"]["matches"]
    assert audit["disc_reconstruction"]["proof_digest_mismatch_count"] == 0
    assert association["root_count"] == 6
    assert association["unique_membership_count"] == 6
    assert association["assignment_collision_count"] == 0
    assert association["all_roots_uniquely_assigned"]


def test_q007j_transports_and_biorthogonalizes_all_registered_modes(
    eigencoordinate_audit,
) -> None:
    transport = eigencoordinate_audit["transport_and_normalization"]

    assert transport["transported_mode_count"] == EXPECTED_TRANSPORTED_MODE_COUNT
    assert transport["unique_mode_label_count"] == EXPECTED_TRANSPORTED_MODE_COUNT
    assert transport["conjugate_label_mismatch_count"] == 0
    assert transport["minimum_overlap_modulus_lower"]["float"] >= float(
        MINIMUM_OVERLAP_MODULUS
    )
    assert transport["maximum_right_correction_upper"]["float"] <= float(
        MAXIMUM_MODE_CORRECTION
    )
    assert transport["maximum_biorthogonal_left_correction_upper"][
        "float"
    ] <= float(MAXIMUM_MODE_CORRECTION)


def test_q007j_study_records_package_and_runner_provenance() -> None:
    artifact = run_q007j_study()

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q007j_eigencoordinate_bridge.py"
    )
    assert len(artifact["runner_source"]["sha256"]) == 64
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert not any(artifact["cycle"]["preserved_prior_outcomes"].values())
