from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011go_degree34_fifty_ninth_individual_partition_audit as q011go
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "303fa473482e335a3913276304416096516c5b4bc12225d263584849692d680f"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "9ae2c196ca74319c96d0030b410d98dafb8012806c2e6b65e3f9e1d8952e90c1"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "1469645c4021c082e4e87b63675f040df3988de5683cc972ed5873d05b8c3405",
    "partition_input_digest_sha256": "86aa22ef19d00b458fd15ec19bdbd51dbcc0e0e81cb33bb312d09280dc902808",
    "allocation_audit_digest_sha256": "9d95d80b0186d1740075f29d3a617333c70a4d1d4866ebf86b7f844fa594798b",
    "result_digest_sha256": "09cc13bbea2d8bb6e961cf152de45a291f18df2bb672d7400ca49e8867ecc56c",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "69be97c85b396a22af0763921ddefcfbda40bcca2ca0a15f0e186b20a414e9a4",
    "parent_center_product_interval_digest_sha256": "00440703df9ef1d41c5b1613f014c199a89897669e6a687c5d52474d30cb460e",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "86bfec87014158cb112ec405452befcb37836dbf948ae92ddaea9440a81809bf",
    "allocation_classification_record_digest_sha256": "d786457684d074566ec4f8a62414eae3a26065bb2ad790469c1617e0290a6326",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011go_structure() -> dict[str, Any]:
    sealed, artifacts = q011go._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011go._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011go_study() -> dict[str, Any]:
    return q011go.run_q011go_study()


@pytest.fixture(scope="module")
def q011go_cycle(q011go_study: dict[str, Any]) -> dict[str, Any]:
    return q011go_study["cycle"]


def test_q011go_seals_q011gn_and_all_prior_inputs(
    q011go_structure: dict[str, Any],
) -> None:
    sealed = q011go_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 175
    assert sealed["direct_digest_count"] == 800
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011gn"]["digests"]) == q011go.Q011GN_DIGESTS
    assert sealed["q011gn"]["artifact_sha256"] == q011go.Q011GN_ARTIFACT_SHA256
    assert sealed["q011gn"]["runner_sha256"] == q011go.Q011GN_RUNNER_SHA256
    assert sealed["q011gn"]["resolved_witness_digest_sha256"] == (
        q011go.EXPECTED_ORDINAL_FIFTY_SEVEN_RESOLUTION_DIGEST
    )


def test_q011go_selects_exactly_flatten_ordinal_fifty_eight(
    q011go_structure: dict[str, Any],
) -> None:
    fixed = q011go_structure["fixed"]
    selection = fixed["fifty_ninth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 58
    assert selection["selected_left_index"] == 7
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(58))
    assert selection["ordinal_fifty_seven_resolution_digest_sha256"] == (
        q011go.EXPECTED_ORDINAL_FIFTY_SEVEN_RESOLUTION_DIGEST
    )
    parent = selection["fifty_ninth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [7, 2], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 2_041
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011go.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011go.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011go.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011go_reconstructs_registered_partition_and_inventory(
    q011go_structure: dict[str, Any],
) -> None:
    fixed = q011go_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [7, 2],
        [5],
        [2, 5],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 7, 2, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011go.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011go.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 36_288
    assert fixed["full_allocation_digest_sha256"] == q011go.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_041
    assert q011go_structure["compatible_count"] == 2_041
    assert fixed["compatible_allocation_digest_sha256"] == q011go.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 7, 0, 2, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 7, 0, 2, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 36_180
    assert fixed["parent_witness_compatible_index"] == 2_040
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011go result is not sealed")
def test_q011go_classifies_every_registered_exact_interval(
    q011go_cycle: dict[str, Any],
) -> None:
    partition = q011go_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_041
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 2_041
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_041))
    for record in records:
        assert record["degree"] == 34
        assert record["output_block"] == 7
        assert record["exact_relation"] == "overlap"
        assert record["binary64_outward_relation"] == "overlap"
        assert not record["exact_gap_positive"]
        assert not record["binary64_outward_gap_positive"]
        assert record["product_equals_parent"]
        assert record["center_product_equals_parent"]
        assert record["target_equals_parent"]
        assert record["intersection_equals_parent"]
        assert record["center_diagnostic_equals_parent"]
        assert record["intersection_width_hex"] == q011go.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011go.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 2_041,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011go result is not sealed")
def test_q011go_applies_the_registered_exclusive_stopping_rule(
    q011go_cycle: dict[str, Any],
) -> None:
    assert q011go_cycle["study_validity"] == "passed"
    assert q011go_cycle["failed_validity_order"] == []
    assert q011go_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011go_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011go_cycle["diagnostic_gates"].values())
    assert q011go_cycle["scientific_outcome"] == "not_evaluated"
    assert q011go_cycle["actual_resonance_outcome"] == "not_established"
    assert q011go_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011go_cycle["diagnostic_classification"] == q011go.INERT_CLASSIFICATION
    assert not q011go_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011go_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fifty_ninth_q011cb_witness"],
        theorem["fifty_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fifty_ninth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011go result is not sealed")
def test_q011go_preserves_boundary_and_reproducible_digests(
    q011go_cycle: dict[str, Any],
) -> None:
    theorem = q011go_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fifty_ninth_q011cb_witness"],
        theorem["fifty_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fifty_ninth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011gn_ordinal_fifty_seven_phase_resolution_is_preserved"]
    assert theorem["q011gm_ordinal_fifty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gl_ordinal_fifty_six_phase_resolution_is_preserved"]
    assert theorem["q011gk_ordinal_fifty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011gj_ordinal_fifty_five_phase_resolution_is_preserved"]
    assert theorem["q011gi_ordinal_fifty_five_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 58" in q011go_cycle["claim_boundary"]
    assert "ordinals 0 through 57" in q011go_cycle["claim_boundary"]
    assert "later 44741 Q011cb refined signatures" in q011go_cycle["claim_boundary"]
    assert "Q011gp" in q011go_cycle["next_change"]
    json.dumps(q011go_cycle, allow_nan=False)
    assert {name: q011go_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011go_cycle["result_digest_sha256"] == (
        q011go.q011b._canonical_json_sha256(q011go._result_digest_sections(q011go_cycle))
    )
    assert q011go._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011go result is not sealed")
def test_q011go_study_metadata_and_optional_artifact_are_scoped(
    q011go_study: dict[str, Any],
) -> None:
    assert q011go_study["schema_version"] == 1
    assert q011go_study["source"] == source_metadata()
    assert q011go_study["study_gate"] == "passed"
    assert q011go_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011go_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_041
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011go_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 58
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011go_study, allow_nan=False)

    runner_path = Path(q011go.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011go_degree34_fifty_ninth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011go artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011go_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011go.q011b._canonical_json_sha256(q011go._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
