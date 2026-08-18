from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ea_degree34_twenty_sixth_individual_partition_audit as q011ea
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "a47d9798e87f1ab06aa9772e0830ae7cb2ecc2f1126628882c13a4f423cdca79"
)
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "ce603076aea464b94ed0bee5391ec62f249206abf26336b7e4c8396f7ab993c3",
    "partition_input_digest_sha256": "6ced61538e5ffb7929185c8b89f0983d3e2f8a9ec5d49cdf5f54b7807f6d98ad",
    "allocation_audit_digest_sha256": "14fc3b4ed4368948cfc0f1bdbb82d7f51daa50ae6071ee724ee50164789111da",
    "result_digest_sha256": "66569dd2e073cd2f174818a38d710933da8f9b4f328661af484ef0e34e4a8a72",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "9af4b6d38527a9fee6ab54981cef83acafa29820666d12a95e0576a120dab8e7"
    ),
    "parent_center_product_interval_digest_sha256": (
        "e386a7d775881d33900b5f7c8ce43762df19eb48213d11e6cb34fa47cc8212dd"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "f14e1a549037b0bf266d3582049350317e74cd127e60f6ae80548387c2bf678d"
    ),
    "allocation_classification_record_digest_sha256": (
        "5f7690a09840838846e924c2eae00ddc7677afcffb0b15c5d45af8b922357ce4"
    ),
}


@pytest.fixture(scope="module")
def q011ea_study() -> dict[str, Any]:
    return q011ea.run_q011ea_study()


@pytest.fixture(scope="module")
def q011ea_cycle(q011ea_study: dict[str, Any]) -> dict[str, Any]:
    return q011ea_study["cycle"]


def test_q011ea_seals_q011dz_and_all_prior_inputs(
    q011ea_cycle: dict[str, Any],
) -> None:
    sealed = q011ea_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 109
    assert sealed["direct_digest_count"] == 503
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dz"]["digests"]) == q011ea.Q011DZ_DIGESTS
    assert sealed["q011dz"]["artifact_sha256"] == q011ea.Q011DZ_ARTIFACT_SHA256
    assert sealed["q011dz"]["runner_sha256"] == q011ea.Q011DZ_RUNNER_SHA256
    assert sealed["q011dz"]["resolved_witness_digest_sha256"] == (
        q011ea.EXPECTED_ORDINAL_TWENTY_FOUR_RESOLUTION_DIGEST
    )


def test_q011ea_selects_exactly_flatten_ordinal_twenty_five(
    q011ea_cycle: dict[str, Any],
) -> None:
    fixed = q011ea_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_sixth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 25
    assert selection["selected_left_index"] == 3
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(25))
    assert selection["ordinal_twenty_four_resolution_digest_sha256"] == (
        q011ea.EXPECTED_ORDINAL_TWENTY_FOUR_RESOLUTION_DIGEST
    )
    parent = selection["twenty_sixth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [3, 6], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 1_854
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ea.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ea.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ea.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ea_reconstructs_registered_partition_and_inventory(
    q011ea_cycle: dict[str, Any],
) -> None:
    fixed = q011ea_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [3, 6],
        [5],
        [1, 6],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 3, 6, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ea.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ea.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 32_928
    assert fixed["full_allocation_digest_sha256"] == q011ea.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_854
    assert fixed["compatible_allocation_digest_sha256"] == (q011ea.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 3, 0, 6, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 3, 0, 6, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 32_844
    assert fixed["parent_witness_compatible_index"] == 1_853
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ea_all_exact_intervals_are_parent_identical(
    q011ea_cycle: dict[str, Any],
) -> None:
    partition = q011ea_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_854
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_854
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_854))
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
        assert record["intersection_width_hex"] == (q011ea.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011ea.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011ea partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ea_records_interval_inert_persistence(
    q011ea_cycle: dict[str, Any],
) -> None:
    assert q011ea_cycle["study_validity"] == "passed"
    assert q011ea_cycle["failed_validity_order"] == []
    assert q011ea_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ea_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ea_cycle["diagnostic_gates"].values())
    assert q011ea_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ea_cycle["diagnostic_classification"] == q011ea.INERT_CLASSIFICATION
    assert q011ea_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ea_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_854,
    }
    partition = q011ea_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ea_preserves_boundary_and_reproducible_digests(
    q011ea_cycle: dict[str, Any],
) -> None:
    theorem = q011ea_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_sixth_q011cb_witness"]
    assert not theorem["twenty_sixth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011dz_ordinal_twenty_four_phase_resolution_is_preserved"]
    assert theorem["q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 25" in q011ea_cycle["claim_boundary"]
    assert "later 44774 Q011cb refined signatures" in q011ea_cycle["claim_boundary"]
    assert "Q011eb" in q011ea_cycle["next_change"]
    json.dumps(q011ea_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011ea section digests have not been sealed yet")
    assert {name: q011ea_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ea_cycle["result_digest_sha256"] == (
        q011ea.q011b._canonical_json_sha256(q011ea._result_digest_sections(q011ea_cycle))
    )
    assert q011ea._protocol_globals_are_restored()


def test_q011ea_study_metadata_and_optional_artifact_are_scoped(
    q011ea_study: dict[str, Any],
) -> None:
    assert q011ea_study["schema_version"] == 1
    assert q011ea_study["source"] == source_metadata()
    assert q011ea_study["study_gate"] == "passed"
    assert q011ea_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ea_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_854
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ea_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 25
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ea_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011ea runner hash has not been sealed yet")
    runner_path = Path(q011ea.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ea_degree34_twenty_sixth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ea artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ea.q011b._canonical_json_sha256(q011ea._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
