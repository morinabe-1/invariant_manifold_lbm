from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q007j_eigencoordinate_bridge as q007j
from research.q007k_quadratic_jet_bridge import (
    EXPECTED_COMPLEX_UNKNOWN_COUNT,
    EXPECTED_EXTERNAL_COUNT,
    EXPECTED_INTERNAL_COUNT,
    EXPECTED_MODE_COUNT,
    EXPECTED_OUTPUT_SUPPORT_COUNT,
    EXPECTED_PAIR_COUNT,
    EXPECTED_ZERO_WAVE_COUNT,
    MAXIMUM_KRAWCZYK_UTILIZATION,
    MAXIMUM_REGISTERED_CORRECTION,
    REGISTERED_INPUT_SHA256,
    REGISTERED_Q007J_RUNNER_SHA256,
    run_q007k_study,
)
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q007k_study():
    return run_q007k_study()


def test_q007k_certifies_all_registered_quadratic_systems(
    q007k_study,
) -> None:
    audit = q007k_study["cycle"]
    certification = audit["krawczyk_certification"]

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert audit["scientific_classification"] == (
        "registered Q006i quadratic coefficients identify the "
        "theorem-manifold graph-gauge quadratic jet"
    )
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert all(gate["passed"] for gate in audit["hypothesis_gates"].values())
    assert certification["system_count"] == EXPECTED_PAIR_COUNT
    assert certification["included_count"] == EXPECTED_PAIR_COUNT
    assert certification["maximum_krawczyk_utilization"]["float"] <= float(
        MAXIMUM_KRAWCZYK_UTILIZATION
    )
    assert certification["maximum_interval_contraction_bound"]["float"] < 1.0
    assert certification["maximum_registered_correction_upper"][
        "float"
    ] <= float(MAXIMUM_REGISTERED_CORRECTION)
    assert all(record["included"] for record in certification["records"])
    json.dumps(audit, allow_nan=False)


def test_q007k_reconstructs_inputs_coefficients_and_exact_identities(
    q007k_study,
) -> None:
    audit = q007k_study["cycle"]
    inputs = audit["input_artifacts"]
    reconstruction = audit["eigencoordinate_reconstruction"]
    identities = audit["exact_identities"]

    assert all(record["passed"] for record in inputs.values())
    assert {
        name: record["sha256"] for name, record in inputs.items()
    } == REGISTERED_INPUT_SHA256
    assert inputs["q007j"]["observed_runner_sha256"] == (
        REGISTERED_Q007J_RUNNER_SHA256
    )
    assert _file_sha256(Path(q007j.__file__).resolve()) == (
        REGISTERED_Q007J_RUNNER_SHA256
    )
    assert audit["coefficient_reproduction"]["matches"]
    assert reconstruction["representative_system_count"] == 12
    assert reconstruction["proof_digest_mismatch_count"] == 0
    assert reconstruction["transported_mode_count"] == EXPECTED_MODE_COUNT
    assert identities["moment_hessian_all_zero"]
    assert identities["zero_wave_moment_symbol_exact"]


def test_q007k_preserves_pair_order_fixed_leaf_and_graph_gauge(
    q007k_study,
) -> None:
    audit = q007k_study["cycle"]
    enumeration = audit["enumeration"]
    certification = audit["krawczyk_certification"]

    assert enumeration["pair_count"] == EXPECTED_PAIR_COUNT
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
    assert audit["pair_correspondence"]["mismatch_count"] == 0
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


def test_q007k_study_records_package_and_runner_provenance(q007k_study) -> None:
    assert q007k_study["schema_version"] == 1
    assert q007k_study["source"] == source_metadata()
    assert q007k_study["runner_source"]["filename"] == (
        "q007k_quadratic_jet_bridge.py"
    )
    assert len(q007k_study["runner_source"]["sha256"]) == 64
    assert q007k_study["study_gate"] == "passed"
    assert q007k_study["scientific_outcome"] == "accepted"
    assert not any(
        q007k_study["cycle"]["preserved_prior_outcomes"].values()
    )
