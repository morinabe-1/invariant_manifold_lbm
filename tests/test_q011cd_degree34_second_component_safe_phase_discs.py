from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011cd_degree34_second_component_safe_phase_discs as q011cd
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "b8e39391097f7739748e4993bc3193ded10390e857b4462e5fff290f43b3d97a"
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "345631d9d333e27a566499c1f132094177cc6c7ea22a95d1df0f9fd948747dfd",
    "phase_input_digest_sha256": (
        "8dca9e90800e4970d0861707e3ae77962b4c1c6fcbe66b70d6a920a6b240ca65"
    ),
    "allocation_digest_sha256": (
        "e32ce2fede47c4e21238fa95abda3c6154543eab3e37662df60daa2113a4e2c7"
    ),
    "phase_comparison_digest_sha256": (
        "e50593eb3580d3ca556148aaff36c05383e120804599fd8119b2ec351f438b96"
    ),
    "result_digest_sha256": "4c2ec0fa7660c48154dac7ea4bddd7dd7b336b4622f75939fa63b7c0402dbdb1",
}
EXPECTED_STREAM_DIGEST = "ed18cd8eea0af9322d42e6c4af4c37339ddb48f1cc2e72f0083b24989e0238cc"
EXPECTED_MINIMUM_WITNESS_DIGEST = "007eb3bba89fc2e306b38227d01d6e922bbb9a863dba81e87df29da5e1675933"


@pytest.fixture(scope="module")
def q011cd_study() -> dict[str, Any]:
    return q011cd.run_q011cd_study()


@pytest.fixture(scope="module")
def q011cd_cycle(q011cd_study: dict[str, Any]) -> dict[str, Any]:
    return q011cd_study["cycle"]


def test_q011cd_seals_q011cc_and_all_prior_inputs(
    q011cd_cycle: dict[str, Any],
) -> None:
    sealed = q011cd_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 60
    assert sealed["direct_digest_count"] == 282
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cc"]["digests"]) == q011cd.Q011CC_DIGESTS
    assert sealed["q011cc"]["artifact_sha256"] == q011cd.Q011CC_ARTIFACT_SHA256
    assert sealed["q011cc"]["runner_sha256"] == q011cd.Q011CC_RUNNER_SHA256


def test_q011cd_reconstructs_component_safe_phase_discs(
    q011cd_cycle: dict[str, Any],
) -> None:
    fixed = q011cd_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 10
    assert fixed["source_phase_disc_record_digest_sha256"] == (q011cd.EXPECTED_SOURCE_RECORD_DIGEST)
    assert fixed["target_phase_disc_record_digest_sha256"] == (q011cd.EXPECTED_TARGET_RECORD_DIGEST)
    assert tuple(fixed["source_radius_binary64_hex"]) == (q011cd.EXPECTED_SOURCE_RADIUS_HEX)
    assert fixed["target_radius_binary64_hex"] == q011cd.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == (fixed["active_component_memberships_by_block"]["16"])
    )
    assert [145] in fixed["active_component_memberships_by_block"]["1"]
    assert [149] in fixed["active_component_memberships_by_block"]["1"]
    assert [150, 151] in fixed["active_component_memberships_by_block"]["1"]
    assert fixed["q011cc_compatible_wave_allocation_count"] == 382
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]


def test_q011cd_enumerates_the_registered_label_free_phase_inventory(
    q011cd_cycle: dict[str, Any],
) -> None:
    allocation = q011cd_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 147_840
    assert allocation["full_allocation_digest_sha256"] == (q011cd.EXPECTED_FULL_ALLOCATION_DIGEST)
    assert allocation["compatible_allocation_count"] == 8_350
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011cd.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 5, 2]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 7]
    assert allocation["wave_projection_count"] == 382
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011cd.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 79,
        "18": 77,
        "24": 76,
        "28": 75,
        "30": 75,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 8_350
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False


def test_q011cd_certifies_all_complex_phase_product_discs(
    q011cd_cycle: dict[str, Any],
) -> None:
    comparison = q011cd_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 8_350
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 8_350,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 8_350,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 8_350
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False


def test_q011cd_minimum_exact_phase_margin_is_fixed(
    q011cd_cycle: dict[str, Any],
) -> None:
    comparison = q011cd_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 5455
    assert witness["counts"] == [11, 2, 0, 9, 0, 0, 0, 5, 2, 5]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == ("0x1.a8f10a6dc8463p-6")
    assert q011cd.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011cd_records_the_scoped_resolution(q011cd_cycle: dict[str, Any]) -> None:
    assert q011cd_cycle["study_validity"] == "passed"
    assert q011cd_cycle["failed_validity_order"] == []
    assert q011cd_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011cd_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011cd_cycle["diagnostic_gates"].values())
    assert q011cd_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cd_cycle["diagnostic_classification"] == (q011cd.RESOLVED_CLASSIFICATION)
    assert q011cd_cycle["scientific_outcome"] == "not_evaluated"
    assert q011cd_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ce" in q011cd_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011cd_cycle["next_change"]


def test_q011cd_preserves_the_scientific_boundary(
    q011cd_cycle: dict[str, Any],
) -> None:
    theorem = q011cd_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_first_q011cb_witness"]
    assert not theorem["first_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cc_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cb_persistent_diagnostic_is_preserved"]
    assert theorem["q011ca_first_family_phase_resolution_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "other 44799 Q011cb refined signatures" in q011cd_cycle["claim_boundary"]
    assert "other 31 parent coalesced overlaps" in q011cd_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011cd_cycle["claim_boundary"]


def test_q011cd_cycle_has_strict_reproducible_digests(
    q011cd_cycle: dict[str, Any],
) -> None:
    json.dumps(q011cd_cycle, allow_nan=False)
    assert {
        name: q011cd_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011cd_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011cd_cycle["result_digest_sha256"] == (
        q011cd.q011b._canonical_json_sha256(q011cd._result_digest_sections(q011cd_cycle))
    )


def test_q011cd_study_metadata_and_optional_artifact_are_scoped(
    q011cd_study: dict[str, Any],
) -> None:
    assert q011cd_study["schema_version"] == 1
    assert q011cd_study["source"] == source_metadata()
    assert q011cd_study["study_gate"] == "passed"
    assert q011cd_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011cd_study["scientific_outcome"] == "not_evaluated"
    assert q011cd_study["actual_resonance_outcome"] == "not_established"
    runtime = q011cd_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 8_350
    assert runtime["floating_point_used_for_gate_decisions"] is False
    scope = q011cd_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011cd_study, allow_nan=False)

    runner_path = Path(q011cd.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / ("q011cd_degree34_second_component_safe_phase_discs.json")
    )
    if not artifact_path.exists():
        pytest.skip("Q011cd artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011cd_degree34_second_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011cd.q011b._canonical_json_sha256(q011cd._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
