from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q007l_cubic_jet_bridge as q007l
import research.q007m_quartic_jet_bridge as q007m
from research.q007m_quartic_jet_bridge import (
    EXPECTED_COMPLEX_UNKNOWN_COUNT,
    EXPECTED_EXTERNAL_COUNT,
    EXPECTED_INTERNAL_COUNT,
    EXPECTED_MULTIPLICITY_SUM,
    EXPECTED_OUTPUT_SUPPORT_COUNT,
    EXPECTED_Q007J_PROOF_COUNT,
    EXPECTED_Q007K_PROOF_COUNT,
    EXPECTED_Q007L_PROOF_COUNT,
    EXPECTED_QUARTET_COUNT,
    EXPECTED_ZERO_WAVE_COUNT,
    MAXIMUM_KRAWCZYK_UTILIZATION,
    MAXIMUM_REGISTERED_CORRECTION,
    Q007L_ARTIFACT,
    REGISTERED_COEFFICIENT_HASHES,
    REGISTERED_INPUT_SHA256,
    REGISTERED_Q007L_RUNNER_SHA256,
)
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q007m_artifact() -> dict:
    artifact_path = (
        Path(q007m.__file__).resolve().parent
        / "artifacts"
        / "q007m_quartic_jet_bridge.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007m_artifact_certifies_all_registered_quartic_systems(
    q007m_artifact,
) -> None:
    audit = q007m_artifact["cycle"]
    certification = audit["krawczyk_certification"]

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert audit["scientific_classification"] == (
        "registered Q007c1 quartic coefficients identify the "
        "theorem-manifold graph-gauge quartic jet"
    )
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert all(gate["passed"] for gate in audit["hypothesis_gates"].values())
    assert certification["system_count"] == EXPECTED_QUARTET_COUNT
    assert certification["included_count"] == EXPECTED_QUARTET_COUNT
    assert certification["maximum_krawczyk_utilization"]["float"] <= float(
        MAXIMUM_KRAWCZYK_UTILIZATION
    )
    assert certification["maximum_interval_contraction_bound"]["float"] < 1.0
    assert certification["maximum_registered_correction_upper"][
        "float"
    ] <= float(MAXIMUM_REGISTERED_CORRECTION)
    assert len(certification["records"]) == EXPECTED_QUARTET_COUNT
    assert all(record["included"] for record in certification["records"])
    json.dumps(q007m_artifact, allow_nan=False)


def test_q007m_artifact_reconstructs_inputs_and_lower_jet_proofs(
    q007m_artifact,
) -> None:
    audit = q007m_artifact["cycle"]
    inputs = audit["input_artifacts"]
    reconstruction = audit["lower_jet_reconstruction"]

    assert all(record["passed"] for record in inputs.values())
    assert inputs["q007c1"]["sha256"] == REGISTERED_INPUT_SHA256["q007c1"]
    assert inputs["q007l"]["sha256"] == REGISTERED_INPUT_SHA256["q007l"]
    assert inputs["q007l"]["observed_runner_sha256"] == (
        REGISTERED_Q007L_RUNNER_SHA256
    )
    q007l_runner = Path(q007l.__file__).resolve()
    assert q007l_runner.name == Q007L_ARTIFACT.replace(".json", ".py")
    assert _file_sha256(q007l_runner) == REGISTERED_Q007L_RUNNER_SHA256
    assert audit["coefficient_reproduction"]["observed"] == (
        REGISTERED_COEFFICIENT_HASHES
    )
    assert audit["coefficient_reproduction"]["matches"]
    assert reconstruction["q007j_representative_proof_count"] == (
        EXPECTED_Q007J_PROOF_COUNT
    )
    assert reconstruction["q007k_reconstructed_proof_count"] == (
        EXPECTED_Q007K_PROOF_COUNT
    )
    assert reconstruction["q007l_reconstructed_proof_count"] == (
        EXPECTED_Q007L_PROOF_COUNT
    )
    assert reconstruction["q007j_proof_digest_mismatch_count"] == 0
    assert reconstruction["q007k_proof_digest_mismatch_count"] == 0
    assert reconstruction["q007l_proof_digest_mismatch_count"] == 0
    assert reconstruction["q007k_pair_metadata_mismatch_count"] == 0
    assert reconstruction["q007l_triple_metadata_mismatch_count"] == 0


def test_q007m_artifact_preserves_quartet_order_fixed_leaf_and_graph_gauge(
    q007m_artifact,
) -> None:
    audit = q007m_artifact["cycle"]
    enumeration = audit["enumeration"]
    structure = audit["structural_conservation"]
    certification = audit["krawczyk_certification"]

    assert enumeration["quartet_count"] == EXPECTED_QUARTET_COUNT
    assert enumeration["kind_counts"] == {
        "zero_wave_kinetic": EXPECTED_ZERO_WAVE_COUNT,
        "internal_selected": EXPECTED_INTERNAL_COUNT,
        "external": EXPECTED_EXTERNAL_COUNT,
    }
    assert enumeration["permutation_multiplicity_sum"] == (
        EXPECTED_MULTIPLICITY_SUM
    )
    assert enumeration["output_wave_support_count"] == (
        EXPECTED_OUTPUT_SUPPORT_COUNT
    )
    assert enumeration["complex_unknown_count"] == EXPECTED_COMPLEX_UNKNOWN_COUNT
    assert enumeration["singular_system_count"] == 0
    assert enumeration["unassigned_system_count"] == 0
    assert audit["quartet_correspondence"]["mismatch_count"] == 0
    assert structure["quadratic_moment_hessian_all_zero"]
    assert structure["zero_wave_moment_symbol_exact"]
    assert structure["moment_third_derivative_all_zero"]
    assert structure["moment_fourth_derivative_all_zero"]
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


def test_q007m_artifact_records_package_and_runner_provenance(
    q007m_artifact,
) -> None:
    runner_path = Path(q007m.__file__).resolve()

    assert q007m_artifact["schema_version"] == 1
    assert q007m_artifact["source"] == source_metadata()
    assert q007m_artifact["runner_source"] == {
        "filename": "q007m_quartic_jet_bridge.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert q007m_artifact["study_gate"] == "passed"
    assert q007m_artifact["scientific_outcome"] == "accepted"
    assert not any(
        q007m_artifact["cycle"]["preserved_prior_outcomes"].values()
    )
