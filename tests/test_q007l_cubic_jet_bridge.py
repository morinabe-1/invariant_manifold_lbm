from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q007k_quadratic_jet_bridge as q007k
from research.q007l_cubic_jet_bridge import (
    EXPECTED_COMPLEX_UNKNOWN_COUNT,
    EXPECTED_EXTERNAL_COUNT,
    EXPECTED_INTERNAL_COUNT,
    EXPECTED_OUTPUT_SUPPORT_COUNT,
    EXPECTED_Q007J_PROOF_COUNT,
    EXPECTED_Q007K_PROOF_COUNT,
    EXPECTED_TRIPLE_COUNT,
    EXPECTED_ZERO_WAVE_COUNT,
    MAXIMUM_KRAWCZYK_UTILIZATION,
    MAXIMUM_REGISTERED_CORRECTION,
    REGISTERED_COEFFICIENT_HASHES,
    REGISTERED_INPUT_SHA256,
    REGISTERED_Q007K_RUNNER_SHA256,
    run_q007l_study,
)
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q007l_study():
    return run_q007l_study()


def test_q007l_certifies_all_registered_cubic_systems(q007l_study) -> None:
    audit = q007l_study["cycle"]
    certification = audit["krawczyk_certification"]

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert audit["scientific_classification"] == (
        "registered Q007b cubic coefficients identify the "
        "theorem-manifold graph-gauge cubic jet"
    )
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert all(gate["passed"] for gate in audit["hypothesis_gates"].values())
    assert certification["system_count"] == EXPECTED_TRIPLE_COUNT
    assert certification["included_count"] == EXPECTED_TRIPLE_COUNT
    assert certification["maximum_krawczyk_utilization"]["float"] <= float(
        MAXIMUM_KRAWCZYK_UTILIZATION
    )
    assert certification["maximum_interval_contraction_bound"]["float"] < 1.0
    assert certification["maximum_registered_correction_upper"][
        "float"
    ] <= float(MAXIMUM_REGISTERED_CORRECTION)
    assert all(record["included"] for record in certification["records"])
    json.dumps(audit, allow_nan=False)


def test_q007l_reconstructs_registered_inputs_and_lower_jet_proofs(
    q007l_study,
) -> None:
    audit = q007l_study["cycle"]
    inputs = audit["input_artifacts"]
    reconstruction = audit["quadratic_jet_reconstruction"]

    assert all(record["passed"] for record in inputs.values())
    assert inputs["q007b"]["sha256"] == REGISTERED_INPUT_SHA256["q007b"]
    assert inputs["q007k"]["sha256"] == REGISTERED_INPUT_SHA256["q007k"]
    assert inputs["q007k"]["observed_runner_sha256"] == (
        REGISTERED_Q007K_RUNNER_SHA256
    )
    assert _file_sha256(Path(q007k.__file__).resolve()) == (
        REGISTERED_Q007K_RUNNER_SHA256
    )
    assert audit["coefficient_reproduction"]["observed"] == (
        REGISTERED_COEFFICIENT_HASHES
    )
    assert audit["coefficient_reproduction"]["matches"]
    assert reconstruction["q007j_representative_proof_count"] == (
        EXPECTED_Q007J_PROOF_COUNT
    )
    assert reconstruction["q007j_proof_digest_mismatch_count"] == 0
    assert reconstruction["q007k_artifact_proof_count"] == (
        EXPECTED_Q007K_PROOF_COUNT
    )
    assert reconstruction["q007k_reconstructed_proof_count"] == (
        EXPECTED_Q007K_PROOF_COUNT
    )
    assert reconstruction["q007k_proof_digest_mismatch_count"] == 0
    assert reconstruction["q007k_pair_metadata_mismatch_count"] == 0
    assert reconstruction["q007k_included_count"] == EXPECTED_Q007K_PROOF_COUNT


def test_q007l_preserves_triple_order_fixed_leaf_and_graph_gauge(
    q007l_study,
) -> None:
    audit = q007l_study["cycle"]
    enumeration = audit["enumeration"]
    structure = audit["structural_conservation"]
    certification = audit["krawczyk_certification"]

    assert enumeration["triple_count"] == EXPECTED_TRIPLE_COUNT
    assert enumeration["kind_counts"] == {
        "zero_wave_kinetic": EXPECTED_ZERO_WAVE_COUNT,
        "internal_selected": EXPECTED_INTERNAL_COUNT,
        "external": EXPECTED_EXTERNAL_COUNT,
    }
    assert enumeration["output_wave_support_count"] == (
        EXPECTED_OUTPUT_SUPPORT_COUNT
    )
    assert enumeration["complex_unknown_count"] == EXPECTED_COMPLEX_UNKNOWN_COUNT
    assert enumeration["singular_system_count"] == 0
    assert enumeration["unassigned_system_count"] == 0
    assert audit["triple_correspondence"]["mismatch_count"] == 0
    assert structure["quadratic_moment_hessian_all_zero"]
    assert structure["zero_wave_moment_symbol_exact"]
    assert structure["moment_third_derivative_all_zero"]
    assert structure["zero_wave_selection_chain_count"] == (
        EXPECTED_ZERO_WAVE_COUNT
    )
    assert certification["zero_wave_product_separation_count"] == (
        EXPECTED_ZERO_WAVE_COUNT
    )
    assert certification["minimum_zero_wave_product_separation_lower"][
        "float"
    ] > 0.0
    assert certification["zero_wave_structural_fixed_leaf_count"] == (
        EXPECTED_ZERO_WAVE_COUNT
    )
    assert certification["internal_graph_gauge_inclusion_count"] == (
        EXPECTED_INTERNAL_COUNT
    )


def test_q007l_study_records_package_and_runner_provenance(q007l_study) -> None:
    assert q007l_study["schema_version"] == 1
    assert q007l_study["source"] == source_metadata()
    assert q007l_study["runner_source"]["filename"] == (
        "q007l_cubic_jet_bridge.py"
    )
    assert len(q007l_study["runner_source"]["sha256"]) == 64
    assert q007l_study["study_gate"] == "passed"
    assert q007l_study["scientific_outcome"] == "accepted"
    assert not any(q007l_study["cycle"]["preserved_prior_outcomes"].values())
