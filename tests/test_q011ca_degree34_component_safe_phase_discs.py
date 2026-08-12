from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ca_degree34_component_safe_phase_discs as q011ca
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a4fc7f9bbcee84b587cd57721636e826070ae8a0ec1237c7e2a29f1bc11cc253"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "df97cbade918c7b71fee33be97779b4615982c13a8f3fbd7715255ba8ee1b1ae"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "f404ad913fd8b46298b70a6e333489ad0cd2d1a7b7ee42789dc943facf761251",
    "phase_input_digest_sha256": (
        "88b59df6111f44524da55737bccfa3675ac1f8a24b77e56e7406f58bd8e95fa4"
    ),
    "allocation_digest_sha256": (
        "323f5249f5c2b827bf125ef74af9a9dd67c6eae2afd41213d8e28f1e426d8cc4"
    ),
    "phase_comparison_digest_sha256": (
        "e56d72fef79d91f307173985b322d52c0f4152be4ac20ed949f03ca99c720193"
    ),
    "result_digest_sha256": (
        "8b0e9c1b02231c950ef117b6517ffce97dbd1383617d84ad8d79e3a92febca2c"
    ),
}
EXPECTED_STREAM_DIGEST = (
    "0095b012cab089b477e20a3729d91f601ade466df2090c9ddbd330d69791653c"
)
EXPECTED_MINIMUM_WITNESS_DIGEST = (
    "20759a775ed6963035559c2acafa9f2811345f0d3e5ddd6db85f3604d7b45477"
)


@pytest.fixture(scope="module")
def q011ca_study() -> dict[str, Any]:
    return q011ca.run_q011ca_study()


@pytest.fixture(scope="module")
def q011ca_cycle(q011ca_study: dict[str, Any]) -> dict[str, Any]:
    return q011ca_study["cycle"]


def test_q011ca_seals_q011bz_and_all_prior_inputs(
    q011ca_cycle: dict[str, Any],
) -> None:
    sealed = q011ca_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 57
    assert sealed["direct_digest_count"] == 269
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bz"]["digests"]) == q011ca.Q011BZ_DIGESTS
    assert sealed["q011bz"]["artifact_sha256"] == q011ca.Q011BZ_ARTIFACT_SHA256
    assert sealed["q011bz"]["runner_sha256"] == q011ca.Q011BZ_RUNNER_SHA256


def test_q011ca_reconstructs_component_safe_phase_discs(
    q011ca_cycle: dict[str, Any],
) -> None:
    fixed = q011ca_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 972
    assert fixed["target_identifier"] == "block=12;center=124"
    assert fixed["source_variant_count"] == 8
    assert fixed["source_phase_disc_record_digest_sha256"] == (
        q011ca.EXPECTED_SOURCE_RECORD_DIGEST
    )
    assert fixed["target_phase_disc_record_digest_sha256"] == (
        q011ca.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert tuple(fixed["source_radius_binary64_hex"]) == (
        q011ca.EXPECTED_SOURCE_RADIUS_HEX
    )
    assert fixed["target_radius_binary64_hex"] == q011ca.EXPECTED_TARGET_RADIUS_HEX
    assert fixed["active_component_memberships_by_block"]["1"] == (
        fixed["active_component_memberships_by_block"]["16"]
    )
    assert [145] in fixed["active_component_memberships_by_block"]["1"]
    assert [150, 151] in fixed["active_component_memberships_by_block"]["1"]
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]


def test_q011ca_enumerates_the_registered_label_free_phase_inventory(
    q011ca_cycle: dict[str, Any],
) -> None:
    allocation = q011ca_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 81_200
    assert allocation["full_allocation_digest_sha256"] == (
        q011ca.EXPECTED_FULL_ALLOCATION_DIGEST
    )
    assert allocation["compatible_allocation_count"] == 5_140
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ca.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 4, 0, 8, 0, 19, 3, 0]
    assert allocation["last_compatible_counts"] == [4, 0, 24, 0, 3, 0, 0, 3]
    assert allocation["wave_projection_count"] == 39
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ca.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 28
    assert allocation["maximum_phase_allocations_per_wave"] == 204
    assert sum(
        record["phase_allocation_count"]
        for record in allocation["wave_projection_records"]
    ) == 5_140
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False


def test_q011ca_certifies_all_complex_phase_product_discs(
    q011ca_cycle: dict[str, Any],
) -> None:
    comparison = q011ca_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 5_140
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 5_140,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 5_140,
    }
    assert comparison["unique_product_radius_count"] == 28
    assert comparison["comparison_stream_count"] == 5_140
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False


def test_q011ca_minimum_exact_phase_margin_is_fixed(
    q011ca_cycle: dict[str, Any],
) -> None:
    comparison = q011ca_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 1767
    assert witness["counts"] == [1, 3, 10, 0, 17, 0, 0, 3]
    assert witness["degree"] == 34
    assert witness["output_block"] == 12
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        "0x1.a0f2b87810ac7p-4"
    )
    assert q011ca.q011z._fraction(
        witness["complex_separation_margin_lower"]["exact"]
    ) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011ca_records_the_scoped_resolution(q011ca_cycle: dict[str, Any]) -> None:
    assert q011ca_cycle["study_validity"] == "passed"
    assert q011ca_cycle["failed_validity_order"] == []
    assert q011ca_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ca_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ca_cycle["diagnostic_gates"].values())
    assert q011ca_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ca_cycle["diagnostic_classification"] == (
        q011ca.RESOLVED_CLASSIFICATION
    )
    assert q011ca_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ca_cycle["actual_resonance_outcome"] == "not_established"
    assert "aggregate 2340" in q011ca_cycle["next_change"]


def test_q011ca_preserves_the_scientific_boundary(
    q011ca_cycle: dict[str, Any],
) -> None:
    theorem = q011ca_cycle["theorem_consequence"]
    assert theorem[
        "component_safe_complex_phase_discs_resolve_first_q011by_witness_family"
    ]
    assert not theorem[
        "first_q011by_witness_family_persists_under_component_safe_phase_discs"
    ]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011bz_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011by_persistent_diagnostic_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "other 9799 Q011by signatures" in q011ca_cycle["claim_boundary"]
    assert "aggregate 2340" in q011ca_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ca_cycle["claim_boundary"]


def test_q011ca_cycle_has_strict_reproducible_digests(
    q011ca_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ca_cycle, allow_nan=False)
    assert {
        name: q011ca_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011ca_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ca_cycle["result_digest_sha256"] == (
        q011ca.q011b._canonical_json_sha256(
            q011ca._result_digest_sections(q011ca_cycle)
        )
    )


def test_q011ca_study_metadata_and_optional_artifact_are_scoped(
    q011ca_study: dict[str, Any],
) -> None:
    assert q011ca_study["schema_version"] == 1
    assert q011ca_study["source"] == source_metadata()
    assert q011ca_study["study_gate"] == "passed"
    assert q011ca_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ca_study["scientific_outcome"] == "not_evaluated"
    assert q011ca_study["actual_resonance_outcome"] == "not_established"
    runtime = q011ca_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 5_140
    assert runtime["floating_point_used_for_gate_decisions"] is False
    scope = q011ca_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 972
    assert scope["target_identifier"] == "block=12;center=124"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ca_study, allow_nan=False)

    runner_path = Path(q011ca.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011ca_degree34_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ca artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011ca_degree34_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ca.q011b._canonical_json_sha256(
            q011ca._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
