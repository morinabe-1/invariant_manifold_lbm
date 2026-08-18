from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ek_degree34_thirty_first_individual_partition_audit as q011ek
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "4c1fdf4f978350c98648af2772eaad36b794bb3276973f042a1887f771c95212"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "5802ffa515c52f4a1467e69bbc60725ae788be224eb6348eaddac8666f3a7cb2"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "6e4bd6d04ea757a7e845900c0c90c45592389f6d3903535a7df2310e514370ae",
    "partition_input_digest_sha256": "9468a01ef21f3d29aa3ecfdf099e2a6bd95281a502a9f7ffda565547fc717ebb",
    "allocation_audit_digest_sha256": "af3bb6b42f3c9370430393960fd00f0fc70a4241e20c8cc7694a41da8ee30adf",
    "result_digest_sha256": "d3b9141d9f2d9a638b94ba5a32422786ea9c583fdaf5225d9296d1045760b434",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "bad78de29ebda9e056ccd9f7ef319412b0fe8fba936681f001ea9fccb5942868"
    ),
    "parent_center_product_interval_digest_sha256": (
        "d85cd7111524b7854e7cd6c1e3d1feb4b717b3f714f565ad57e4944534041217"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "03e2575b58594c7ebacfe9459e6d6c8df280fc954f508fe7f77dc295ea122cbf"
    ),
    "allocation_classification_record_digest_sha256": (
        "ed0b2b6876e220abdbb6d1da9c9f78cfc2ead9381371ff3f6e2d80e4a70e5c5a"
    ),
}


@pytest.fixture(scope="module")
def q011ek_study() -> dict[str, Any]:
    return q011ek.run_q011ek_study()


@pytest.fixture(scope="module")
def q011ek_cycle(q011ek_study: dict[str, Any]) -> dict[str, Any]:
    return q011ek_study["cycle"]


def test_q011ek_seals_q011ej_and_all_prior_inputs(
    q011ek_cycle: dict[str, Any],
) -> None:
    sealed = q011ek_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 119
    assert sealed["direct_digest_count"] == 548
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ej"]["digests"]) == q011ek.Q011EJ_DIGESTS
    assert sealed["q011ej"]["artifact_sha256"] == q011ek.Q011EJ_ARTIFACT_SHA256
    assert sealed["q011ej"]["runner_sha256"] == q011ek.Q011EJ_RUNNER_SHA256
    assert sealed["q011ej"]["resolved_witness_digest_sha256"] == (
        q011ek.EXPECTED_ORDINAL_TWENTY_NINE_RESOLUTION_DIGEST
    )


def test_q011ek_selects_exactly_flatten_ordinal_thirty(
    q011ek_cycle: dict[str, Any],
) -> None:
    fixed = q011ek_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_first_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 30
    assert selection["selected_left_index"] == 3
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(30))
    assert selection["ordinal_twenty_nine_resolution_digest_sha256"] == (
        q011ek.EXPECTED_ORDINAL_TWENTY_NINE_RESOLUTION_DIGEST
    )
    parent = selection["thirty_first_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [3, 6], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_854
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ek.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ek.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ek.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ek_reconstructs_registered_partition_and_inventory(
    q011ek_cycle: dict[str, Any],
) -> None:
    fixed = q011ek_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [3, 6],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 3, 6, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ek.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ek.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 32_928
    assert fixed["full_allocation_digest_sha256"] == q011ek.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_854
    assert fixed["compatible_allocation_digest_sha256"] == (q011ek.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 3, 0, 6, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 3, 0, 6, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 32_844
    assert fixed["parent_witness_compatible_index"] == 1_853
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ek_all_exact_intervals_are_parent_identical(
    q011ek_cycle: dict[str, Any],
) -> None:
    partition = q011ek_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == (q011ek.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011ek.EXPECTED_PARENT_CENTER_GAP_HEX
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011ek partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ek_records_interval_inert_persistence(
    q011ek_cycle: dict[str, Any],
) -> None:
    assert q011ek_cycle["study_validity"] == "passed"
    assert q011ek_cycle["failed_validity_order"] == []
    assert q011ek_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ek_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ek_cycle["diagnostic_gates"].values())
    assert q011ek_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ek_cycle["diagnostic_classification"] == q011ek.INERT_CLASSIFICATION
    assert q011ek_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ek_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_854,
    }
    partition = q011ek_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ek_preserves_boundary_and_reproducible_digests(
    q011ek_cycle: dict[str, Any],
) -> None:
    theorem = q011ek_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_thirty_first_q011cb_witness"]
    assert not theorem["thirty_first_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011ej_ordinal_twenty_nine_phase_resolution_is_preserved"]
    assert theorem["q011ei_ordinal_twenty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eh_ordinal_twenty_eight_phase_resolution_is_preserved"]
    assert theorem["q011eg_ordinal_twenty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ee_ordinal_twenty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ec_ordinal_twenty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011eb_ordinal_twenty_five_phase_resolution_is_preserved"]
    assert theorem["q011ea_ordinal_twenty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dz_ordinal_twenty_four_phase_resolution_is_preserved"]
    assert theorem["q011dy_ordinal_twenty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 30" in q011ek_cycle["claim_boundary"]
    assert "later 44769 Q011cb refined signatures" in q011ek_cycle["claim_boundary"]
    assert "Q011el" in q011ek_cycle["next_change"]
    json.dumps(q011ek_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011ek section digests have not been sealed yet")
    assert {name: q011ek_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ek_cycle["result_digest_sha256"] == (
        q011ek.q011b._canonical_json_sha256(q011ek._result_digest_sections(q011ek_cycle))
    )
    assert q011ek._protocol_globals_are_restored()


def test_q011ek_study_metadata_and_optional_artifact_are_scoped(
    q011ek_study: dict[str, Any],
) -> None:
    assert q011ek_study["schema_version"] == 1
    assert q011ek_study["source"] == source_metadata()
    assert q011ek_study["study_gate"] == "passed"
    assert q011ek_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ek_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_854
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ek_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 30
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ek_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011ek runner hash has not been sealed yet")
    runner_path = Path(q011ek.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ek_degree34_thirty_first_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ek artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ek.q011b._canonical_json_sha256(q011ek._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
