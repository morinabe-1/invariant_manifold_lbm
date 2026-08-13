from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ch_degree34_third_component_safe_phase_discs as q011ch
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "17f85796df17fc8cc06f961421ad5a76fa19af7502d22fd552c4315227774c24"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "26941b40908a64c32ec529a996a687fe64d9257d993faecf45619712fb38a4bd"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "0501ac79003012b0bc0eed0ba358e161bbd58985b719c2ed559f25dce87a6d98",
    "phase_input_digest_sha256": (
        "374f286a7b816058d445fe5e80b04fdb6d84f31538c1e9fe335d29fca7b00364"
    ),
    "allocation_digest_sha256": (
        "b8757924d92579525263a161ac7b6416690f2a139d2292dfac212c41a2c29136"
    ),
    "phase_comparison_digest_sha256": (
        "a5079f4feecc58031ffee55ec2638f2822131423c3917d81741ec20c03c4cd67"
    ),
    "result_digest_sha256": "328aae2da9afbfe8d69e919cddf0d9459b1c921ac546f2b6f7ee19044c10b322",
}
EXPECTED_STREAM_DIGEST = "ff113285c032296966864a9cb8984527a516d75583b7e4d7e1462e2255a10ba2"
EXPECTED_MINIMUM_WITNESS_DIGEST = (
    "fcbac38dd950f2aedb42ca9b4f2543d54616a5938c7f645e2a2437c3ad04e645"
)


@pytest.fixture(scope="module")
def q011ch_study() -> dict[str, Any]:
    return q011ch.run_q011ch_study()


@pytest.fixture(scope="module")
def q011ch_cycle(q011ch_study: dict[str, Any]) -> dict[str, Any]:
    return q011ch_study["cycle"]


def test_q011ch_seals_q011cg_and_all_prior_inputs(
    q011ch_cycle: dict[str, Any],
) -> None:
    sealed = q011ch_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 64
    assert sealed["direct_digest_count"] == 300
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011cg"]["digests"]) == q011ch.Q011CG_DIGESTS
    assert sealed["q011cg"]["artifact_sha256"] == q011ch.Q011CG_ARTIFACT_SHA256
    assert sealed["q011cg"]["runner_sha256"] == q011ch.Q011CG_RUNNER_SHA256


def test_q011ch_reconstructs_component_safe_phase_discs(
    q011ch_cycle: dict[str, Any],
) -> None:
    fixed = q011ch_cycle["fixed_component_safe_phase_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["parent_q011bx_aggregate_index"] == 2340
    assert fixed["parent_q011cb_local_aggregate_index"] == 0
    assert fixed["parent_flat_ordinal"] == 2
    assert fixed["target_identifier"] == "block=7;center=44"
    assert fixed["source_variant_count"] == 12
    assert fixed["source_phase_disc_record_digest_sha256"] == (
        q011ch.EXPECTED_SOURCE_RECORD_DIGEST
    )
    assert fixed["target_phase_disc_record_digest_sha256"] == (
        q011ch.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert tuple(fixed["source_radius_binary64_hex"]) == (
        q011ch.EXPECTED_SOURCE_RADIUS_HEX
    )
    assert fixed["target_radius_binary64_hex"] == q011ch.EXPECTED_TARGET_RADIUS_HEX
    assert (
        fixed["active_component_memberships_by_block"]["1"]
        == fixed["active_component_memberships_by_block"]["16"]
    )
    memberships = fixed["active_component_memberships_by_block"]["1"]
    assert [145] in memberships
    assert [148] in memberships
    assert [149] in memberships
    assert [150, 151] in memberships
    assert fixed["q011cg_compatible_wave_allocation_count"] == 852
    assert fixed["q011cg_compatible_wave_allocation_digest_sha256"] == (
        q011ch.q011cg.EXPECTED_COMPATIBLE_DIGEST
    )
    assert "no component-internal eigenvalue label" in fixed["label_semantics"]


def test_q011ch_enumerates_registered_label_free_phase_inventory(
    q011ch_cycle: dict[str, Any],
) -> None:
    allocation = q011ch_cycle["component_safe_phase_allocation_audit"]
    assert allocation["passed"]
    assert all(allocation["checks"].values())
    assert allocation["full_allocation_count"] == 332_640
    assert allocation["full_allocation_digest_sha256"] == (
        q011ch.EXPECTED_FULL_ALLOCATION_DIGEST
    )
    assert allocation["compatible_allocation_count"] == 18_718
    assert allocation["compatible_allocation_digest_sha256"] == (
        q011ch.EXPECTED_COMPATIBLE_ALLOCATION_DIGEST
    )
    assert allocation["first_compatible_counts"] == [
        0,
        13,
        0,
        0,
        0,
        9,
        0,
        5,
        0,
        2,
        5,
        0,
    ]
    assert allocation["last_compatible_counts"] == [
        13,
        0,
        9,
        0,
        0,
        0,
        0,
        5,
        0,
        2,
        0,
        5,
    ]
    assert allocation["wave_projection_count"] == 852
    assert allocation["wave_projection_record_digest_sha256"] == (
        q011ch.EXPECTED_WAVE_PROJECTION_DIGEST
    )
    assert allocation["minimum_phase_allocations_per_wave"] == 10
    assert allocation["maximum_phase_allocations_per_wave"] == 30
    assert allocation["phase_allocation_count_per_wave_histogram"] == {
        "10": 173,
        "18": 169,
        "24": 169,
        "28": 170,
        "30": 171,
    }
    assert (
        sum(
            record["phase_allocation_count"]
            for record in allocation["wave_projection_records"]
        )
        == 18_718
    )
    assert allocation["full_allocation_records_retained"] is False
    assert allocation["compatible_allocation_records_retained"] is False


def test_q011ch_certifies_all_complex_phase_product_discs(
    q011ch_cycle: dict[str, Any],
) -> None:
    comparison = q011ch_cycle["complex_phase_product_disc_audit"]
    assert comparison["passed"]
    assert all(comparison["checks"].values())
    assert comparison["parent_flat_ordinal"] == 2
    assert comparison["compatible_phase_allocation_count"] == 18_718
    assert comparison["category_counts"] == {
        "individual_modulus_separation": 0,
        "complex_phase_separation": 18_718,
        "unresolved_product_disk_overlap": 0,
    }
    assert comparison["individual_modulus_relation_counts"] == {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 18_718,
    }
    assert comparison["unique_product_radius_count"] == 10
    assert comparison["comparison_stream_count"] == 18_718
    assert comparison["comparison_stream_domain"] == (
        "q011ch-component-safe-phase-comparisons-v1"
    )
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert comparison["first_unresolved_witness"] is None
    assert comparison["full_comparison_records_retained"] is False
    assert comparison["previous_q011cb_refined_signatures_recomputed"] is False
    assert comparison["later_q011cb_refined_signatures_recomputed"] is False


def test_q011ch_minimum_exact_phase_margin_is_fixed(
    q011ch_cycle: dict[str, Any],
) -> None:
    comparison = q011ch_cycle["complex_phase_product_disc_audit"]
    witness = comparison["global_minimum_margin_witness"]
    assert witness == comparison["minimum_separated_witness"]
    assert witness["compatible_allocation_index"] == 11_706
    assert witness["counts"] == [11, 2, 0, 7, 0, 2, 0, 5, 2, 0, 2, 3]
    assert witness["degree"] == 34
    assert witness["output_block"] == 7
    assert witness["individual_modulus_relation"] == "overlap"
    assert witness["classification"] == "complex_phase_separation"
    assert witness["complex_separation_margin_lower"]["binary64_hex"] == (
        "0x1.a8f10a6dc8560p-6"
    )
    assert q011ch.q011z._fraction(
        witness["complex_separation_margin_lower"]["exact"]
    ) > 0
    assert witness["witness_digest_sha256"] == EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011ch_records_scoped_resolution(q011ch_cycle: dict[str, Any]) -> None:
    assert q011ch_cycle["study_validity"] == "passed"
    assert q011ch_cycle["failed_validity_order"] == []
    assert q011ch_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ch_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ch_cycle["diagnostic_gates"].values())
    assert q011ch_cycle["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ch_cycle["diagnostic_classification"] == q011ch.RESOLVED_CLASSIFICATION
    assert q011ch_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ch_cycle["actual_resonance_outcome"] == "not_established"
    assert "Q011ci" in q011ch_cycle["next_change"]
    assert "next Q011cb refined overlap" in q011ch_cycle["next_change"]


def test_q011ch_preserves_scientific_boundary(q011ch_cycle: dict[str, Any]) -> None:
    theorem = q011ch_cycle["theorem_consequence"]
    assert theorem["component_safe_complex_phase_discs_resolve_third_q011cb_witness"]
    assert not theorem[
        "third_q011cb_witness_persists_under_component_safe_phase_discs"
    ]
    assert theorem["q011an_component_internal_eigenvalue_labels_are_assumed"] is False
    assert theorem["q011cg_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cf_ordinal_one_phase_resolution_is_preserved"]
    assert theorem["q011cd_ordinal_zero_phase_resolution_is_preserved"]
    assert theorem["q011cb_persistent_diagnostic_is_preserved"]
    assert theorem["q011ca_first_family_phase_resolution_is_preserved"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem[
        "an_actual_degree_thirty_four_external_resonance_is_established"
    ]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert "flatten ordinal 2" in q011ch_cycle["claim_boundary"]
    assert "does not reevaluate ordinals 0 or 1" in q011ch_cycle["claim_boundary"]
    assert "later 44797 Q011cb refined signatures" in q011ch_cycle["claim_boundary"]
    assert "does not establish an actual resonance" in q011ch_cycle["claim_boundary"]


def test_q011ch_cycle_has_strict_reproducible_digests(
    q011ch_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ch_cycle, allow_nan=False)
    assert {
        name: q011ch_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    comparison = q011ch_cycle["complex_phase_product_disc_audit"]
    assert comparison["comparison_stream_digest_sha256"] == EXPECTED_STREAM_DIGEST
    assert q011ch_cycle["result_digest_sha256"] == (
        q011ch.q011b._canonical_json_sha256(
            q011ch._result_digest_sections(q011ch_cycle)
        )
    )


def test_q011ch_study_metadata_and_optional_artifact_are_scoped(
    q011ch_study: dict[str, Any],
) -> None:
    assert q011ch_study["schema_version"] == 1
    assert q011ch_study["source"] == source_metadata()
    assert q011ch_study["study_gate"] == "passed"
    assert q011ch_study["refinement_outcome"] == "component_safe_phase_resolved"
    assert q011ch_study["scientific_outcome"] == "not_evaluated"
    assert q011ch_study["actual_resonance_outcome"] == "not_established"
    runtime = q011ch_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 18_718
    assert runtime["floating_point_used_for_gate_decisions"] is False
    scope = q011ch_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 2
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["component_internal_eigenvalue_labels_assumed"] is False
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ch_study, allow_nan=False)

    runner_path = Path(q011ch.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011ch_degree34_third_component_safe_phase_discs.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ch artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011ch_degree34_third_component_safe_phase_discs.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "component_safe_phase_resolved"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ch.q011b._canonical_json_sha256(
            q011ch._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
