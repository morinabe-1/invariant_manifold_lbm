from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011gr_degree34_sixtieth_component_safe_phase_discs as q011gr
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "32106f2e8cfeed4eb2cfcce07309917afb3db239f1ac1c256ddd93e38c89625c"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "cf3c3600ffbcef49d1aae48b9ce240e15691285c8a354fe82e0006e2882bc3b9"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "415e29693cd63a2dfa258fa8d579c7e6c3b7e21801a3a82fd0c5d6a7425e95d3",
    "phase_input_digest_sha256": "71eb74cbc7ec0c0b8126a325f649eda302fa153606035bfd137897a3b0126b33",
    "allocation_digest_sha256": "69e25e0fd4e4acfd1832bc6224d115f4f2ac89ec6933695075f487c4ea5408e3",
    "phase_comparison_digest_sha256": "c71a00c50aba4e0a2520deb629d138557957570c2c96028cb8209eaddf1134dd",
    "result_digest_sha256": "1ac3e694a83a66b317c49521b79dd32f79f041336e75181dd557a705ff3bb330",
}
EXPECTED_STREAM_DIGEST: str | None = (
    "dc06d180d061237c9f5db468fbb9346722a014ea837e97140bff453e1eab9939"
)
EXPECTED_MINIMUM_WITNESS_DIGEST: str | None = (
    "4d81a833f38342bf959039d0b9e3f85fd2fc2edae6f7fde6aa7fe9f8f46e3a71"
)
EXPECTED_MINIMUM_INDEX: int | None = 12_816
EXPECTED_MINIMUM_COUNTS: list[int] | None = [11, 2, 0, 6, 0, 3, 0, 5, 3, 0, 2, 2]
EXPECTED_MINIMUM_MARGIN_HEX: str | None = "0x1.a8f10a6dc85dep-6"
EXPECTED_CATEGORY_COUNTS: dict[str, int] | None = {
    "individual_modulus_separation": 0,
    "complex_phase_separation": 20_786,
    "unresolved_product_disk_overlap": 0,
}
EXPECTED_REFINEMENT_OUTCOME: str | None = "component_safe_phase_resolved"
RESULT_EXPECTATIONS_FIXED = all(
    value is not None
    for value in (
        EXPECTED_RUNNER_SHA256,
        EXPECTED_ARTIFACT_SHA256,
        EXPECTED_SECTION_DIGESTS,
        EXPECTED_STREAM_DIGEST,
        EXPECTED_MINIMUM_WITNESS_DIGEST,
        EXPECTED_MINIMUM_INDEX,
        EXPECTED_MINIMUM_COUNTS,
        EXPECTED_MINIMUM_MARGIN_HEX,
        EXPECTED_CATEGORY_COUNTS,
        EXPECTED_REFINEMENT_OUTCOME,
    )
)


@pytest.fixture(scope="module")
def q011gr_structure() -> dict[str, Any]:
    sealed, artifacts = q011gr._sealed_input_audit()
    fixed, sources, target, wave_compatible = q011gr._fixed_phase_input_audit(artifacts)
    allocation, compatible = q011gr._allocation_inventory(sources, wave_compatible)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "target": target,
        "allocation": allocation,
        "compatible_count": len(compatible),
    }


@pytest.fixture(scope="module")
def q011gr_study() -> dict[str, Any]:
    return q011gr.run_q011gr_study()


@pytest.fixture(scope="module")
def q011gr_cycle(q011gr_study: dict[str, Any]) -> dict[str, Any]:
    return q011gr_study["cycle"]


def test_q011gr_seals_q011gq_and_all_prior_inputs(
    q011gr_structure: dict[str, Any],
) -> None:
    sealed = q011gr_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 178
    assert sealed["direct_digest_count"] == 813
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gq"]["digests"]) == q011gr.Q011GQ_DIGESTS
    assert sealed["q011gq"]["artifact_sha256"] == q011gr.Q011GQ_ARTIFACT_SHA256
    assert sealed["q011gq"]["runner_sha256"] == q011gr.Q011GQ_RUNNER_SHA256


def test_q011gr_reconstructs_component_safe_phase_discs(
    q011gr_structure: dict[str, Any],
) -> None:
    fixed = q011gr_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 59
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == q011gr.EXPECTED_SOURCE_RECORD_DIGEST
    assert fixed["target_phase_disc_record_digest_sha256"] == q011gr.EXPECTED_TARGET_RECORD_DIGEST
    assert tuple(fixed["source_radius_binary64_hex"]) == q011gr.EXPECTED_SOURCE_RADIUS_HEX
    assert fixed["target_radius_binary64_hex"] == q011gr.EXPECTED_TARGET_RADIUS_HEX
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert memberships == fixed["active_component_memberships_by_block"]["16"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011gq_compatible_wave_allocation_count"] == 2_266
    assert fixed["q011gq_compatible_wave_allocation_digest_sha256"] == (
        q011gr.q011gq.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]
    assert q011gr._protocol_globals_are_restored()


def test_q011gr_enumerates_registered_label_free_phase_inventory(
    q011gr_structure: dict[str, Any],
) -> None:
    allocation = q011gr_structure["allocation"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 369_600
    assert allocation["full_allocation_digest_sha256"] == q011gr.EXPECTED_FULL_ALLOCATION_DIGEST
    assert allocation["compatible_allocation_count"] == 20_786
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011gr.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [0, 13, 0, 0, 0, 9, 0, 5, 1, 2, 4, 0]
    assert allocation["last_compatible_counts"] == [13, 0, 9, 0, 0, 0, 0, 5, 0, 3, 0, 4]
    assert allocation["individual_wave_allocation_count"] == 2_266
    assert allocation["component_wave_projection_count"] == 945
    assert allocation["individual_to_component_bridge_record_digest_sha256"] == (
        q011gr.EXPECTED_BRIDGE_RECORD_DIGEST
    )
    assert allocation["minimum_individual_allocations_per_component_wave"] == 1
    assert allocation["maximum_individual_allocations_per_component_wave"] == 3
    assert allocation["individual_allocation_count_per_component_wave_histogram"] == {
        "1": 191,
        "2": 187,
        "3": 567,
    }
    assert (
        sum(
            record["individual_wave_allocation_count"]
            for record in allocation["individual_to_component_bridge_records"]
        )
        == 2_266
    )
    assert allocation["bridge_phase_paired_record_digest_sha256"] == (
        q011gr.EXPECTED_PAIRED_RECORD_DIGEST
    )
    assert allocation["wave_projection_count"] == 945
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011gr.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 191,
        "18": 187,
        "24": 187,
        "28": 189,
        "30": 191,
    }
    assert (
        sum(record["phase_allocation_count"] for record in allocation["wave_projection_records"])
        == 20_786
    )
    assert q011gr_structure["compatible_count"] == 20_786
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False
    adapter = allocation["allocation_protocol_adapter"]
    assert adapter["ordinal_fifty_nine_totals"] == [13, 9, 5, 3, 4]
    assert adapter["active_singleton_component_wave_identifiers"] == [
        "block=16;center=148",
        "block=1;center=148",
        "block=16;center=149",
        "block=1;center=149",
    ]
    assert adapter["inherited_hardcoded_ordinal_totals_used"] is False
    assert adapter["protocol_globals_modified"] is False


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gr result is not sealed")
def test_q011gr_classifies_all_complex_phase_product_discs(
    q011gr_cycle: dict[str, Any],
) -> None:
    comparison = q011gr_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["compatible_phase_allocation_count"] == 20_786
    assert comparison["category_counts"] == EXPECTED_CATEGORY_COUNTS
    assert sum(comparison["category_counts"].values()) == 20_786
    assert comparison["comparison_stream_count"] == 20_786
    assert comparison["comparison_stream_domain"] == "q011gr-component-safe-phase-comparisons-v1"
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 20_786,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["first_unresolved_witness"] is None


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gr result is not sealed")
def test_q011gr_minimum_exact_phase_margin_is_fixed(
    q011gr_cycle: dict[str, Any],
) -> None:
    comparison = q011gr_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness["compatible_allocation_index"] == EXPECTED_MINIMUM_INDEX
    assert witness["counts"] == EXPECTED_MINIMUM_COUNTS
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        EXPECTED_MINIMUM_MARGIN_HEX
    )
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST
    assert q011gr.q011z._fraction(witness["complex_separation_margin_lower"]["exact"]) > 0


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gr result is not sealed")
def test_q011gr_records_scoped_outcome(q011gr_cycle: dict[str, Any]) -> None:
    assert q011gr_cycle["study_validity"] == "passed"
    assert q011gr_cycle["failed_validity_order"] == []
    assert q011gr_cycle["failed_diagnostic_order"] == []
    assert len(q011gr_cycle["validity_gates"]) == 7
    assert len(q011gr_cycle["diagnostic_gates"]) == 4
    assert all(gate["passed"] for gate in q011gr_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011gr_cycle["diagnostic_gates"].values())
    assert q011gr_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    assert q011gr_cycle["diagnostic_classification"] == q011gr.RESOLVED_CLASSIFICATION
    assert q011gr_cycle["scientific_outcome"] == "not_evaluated"
    assert q011gr_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011gs" in q011gr_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011gr_cycle["next_change"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gr result is not sealed")
def test_q011gr_preserves_scientific_boundary(q011gr_cycle: dict[str, Any]) -> None:
    theorem = q011gr_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_sixtieth_q011cb_witness"]
    assert not theorem["sixtieth_q011cb_witness_persists_under_component_safe_phase_discs"]
    assert not theorem["q011an_component_internal_eigenvalue_labels_are_assumed"]
    assert theorem["q011gq_ordinal_fifty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gp_ordinal_fifty_eight_phase_resolution_is_preserved"]
    assert theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
    assert theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 59" in q011gr_cycle["claim_boundary"]
    assert "reevaluate ordinals 0 through 58" in q011gr_cycle["claim_boundary"]
    assert "later 44740 Q011cb refined signatures" in q011gr_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011gr_cycle["claim_boundary"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gr result is not sealed")
def test_q011gr_cycle_has_strict_reproducible_digests(
    q011gr_cycle: dict[str, Any],
) -> None:
    json.dumps(q011gr_cycle, allow_nan=False)
    assert {name: q011gr_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    comparison = q011gr_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011gr_cycle["result_digest_sha256"] == (
        q011gr.q011b._canonical_json_sha256(q011gr._result_digest_sections(q011gr_cycle))
    )
    assert q011gr._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011gr result is not sealed")
def test_q011gr_study_metadata_and_optional_artifact_are_scoped(
    q011gr_study: dict[str, Any],
) -> None:
    assert q011gr_study["schema_version"] == 1
    assert q011gr_study["source"] == source_metadata()
    assert q011gr_study["study_gate"] == "passed"
    assert q011gr_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011gr_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 20_786
    assert runtime["floating_point_used_for_gate_decisions"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011gr_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 59
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011gr_study, allow_nan=False)

    runner_path = Path(q011gr.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011gr_degree34_sixtieth_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011gr artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011gr_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011gr.q011b._canonical_json_sha256(q011gr._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
