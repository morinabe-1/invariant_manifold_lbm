from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ci_degree34_fourth_individual_partition_audit as q011ci
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "059c5cf346e74357b44d1da0bc198ce62b91618e8fe8a5e39412697a2bee2873"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "e81f2cdc9b90d46a68fa005310a8a68d72365fe7d353ff88459e3073aa438093"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "23c31f9aff320c06a988495ae9f0dc1da15b7f161527c8a775a0c260d92b0244",
    "partition_input_digest_sha256": (
        "cf0ee6a1dee99ed05810f4dd9c715e8618e17edfcdfaf06f0f97230cf3382518"
    ),
    "allocation_audit_digest_sha256": (
        "71dbd6ebd367cf015c54cf21b036e9fb48b152e145e81210f658715eaeae11be"
    ),
    "result_digest_sha256": "6fded001843d7bb729f40fab35d59b4c9b231c814a244b8585b1e8c9ced8cd97",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "22266084469c53df1fdf3e583fec6f1727a6e543ac158ea78e4c2fc74e1f3318"
    ),
    "parent_center_product_interval_digest_sha256": (
        "e155fd6fbdbfc78a9c8c5a006d335a365b536b308ac1e7c8c68a3e4c4a0c2374"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "695ea79d90eb41053f8a299b16958af0f114f5cc6df67a31ce5c50bf49fd16ba"
    ),
    "allocation_classification_record_digest_sha256": (
        "834f09c5c4c7c16166436dbf97770ba841599f7a98845134f0c2ce952ce8a990"
    ),
}


@pytest.fixture(scope="module")
def q011ci_study() -> dict[str, Any]:
    return q011ci.run_q011ci_study()


@pytest.fixture(scope="module")
def q011ci_cycle(q011ci_study: dict[str, Any]) -> dict[str, Any]:
    return q011ci_study["cycle"]


def test_q011ci_seals_q011ch_and_restores_adapter_globals(
    q011ci_cycle: dict[str, Any],
) -> None:
    sealed = q011ci_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 65
    assert sealed["direct_digest_count"] == 305
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ch"]["digests"]) == q011ci.Q011CH_DIGESTS
    assert sealed["q011ch"]["artifact_sha256"] == q011ci.Q011CH_ARTIFACT_SHA256
    assert sealed["q011ch"]["runner_sha256"] == q011ci.Q011CH_RUNNER_SHA256
    assert sealed["q011ch"]["resolved_witness_digest_sha256"] == (
        q011ci.EXPECTED_ORDINAL_TWO_RESOLUTION_DIGEST
    )
    adapter = q011ci_cycle["registered_parameters"]["q011cg_protocol_adapter"]
    assert adapter["globals_restored_after_use"]
    assert set(adapter["temporary_override_names"]) == set(q011ci._PROTOCOL_OVERRIDES)
    assert q011ci._protocol_globals_are_restored()


def test_q011ci_selects_exactly_flatten_ordinal_three(
    q011ci_cycle: dict[str, Any],
) -> None:
    fixed = q011ci_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 3
    assert selection["selected_left_index"] == 0
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == [0, 1, 2]
    assert selection["ordinal_two_resolution_digest_sha256"] == (
        q011ci.EXPECTED_ORDINAL_TWO_RESOLUTION_DIGEST
    )
    parent = selection["fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [0, 9], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 945
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ci.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ci.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ci.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ci_reconstructs_registered_partition_and_inventory(
    q011ci_cycle: dict[str, Any],
) -> None:
    fixed = q011ci_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [0, 9],
        [5],
        [3, 4],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011ci.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == (
        q011ci.EXPECTED_IDENTIFIER_ORDER
    )
    assert fixed["full_allocation_count"] == 16_800
    assert fixed["full_allocation_digest_sha256"] == q011ci.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 945
    assert fixed["compatible_allocation_digest_sha256"] == (
        q011ci.EXPECTED_COMPATIBLE_DIGEST
    )
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 16_680
    assert fixed["parent_witness_compatible_index"] == 944
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ci_all_exact_intervals_are_parent_identical(
    q011ci_cycle: dict[str, Any],
) -> None:
    partition = q011ci_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 945
    assert partition[
        "all_product_target_intersection_and_center_records_equal_parent"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 945
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(945)
    )
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
        assert record["intersection_width_hex"] == q011ci.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011ci.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ci_records_interval_inert_persistence(
    q011ci_cycle: dict[str, Any],
) -> None:
    assert q011ci_cycle["study_validity"] == "passed"
    assert q011ci_cycle["failed_validity_order"] == []
    assert q011ci_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ci_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ci_cycle["diagnostic_gates"].values())
    assert q011ci_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011ci_cycle["diagnostic_classification"] == q011ci.INERT_CLASSIFICATION
    assert q011ci_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ci_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 945,
    }
    partition = q011ci_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011ci_preserves_boundary_and_reproducible_digests(
    q011ci_cycle: dict[str, Any],
) -> None:
    theorem = q011ci_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_fourth_q011cb_witness"]
    assert not theorem["fourth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011ch_ordinal_two_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 3" in q011ci_cycle["claim_boundary"]
    assert "later 44796 Q011cb refined signatures" in q011ci_cycle["claim_boundary"]
    json.dumps(q011ci_cycle, allow_nan=False)
    assert {
        name: q011ci_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    assert q011ci_cycle["result_digest_sha256"] == (
        q011ci.q011b._canonical_json_sha256(q011ci._result_digest_sections(q011ci_cycle))
    )
    assert q011ci._protocol_globals_are_restored()


def test_q011ci_study_metadata_and_optional_artifact_are_scoped(
    q011ci_study: dict[str, Any],
) -> None:
    assert q011ci_study["schema_version"] == 1
    assert q011ci_study["source"] == source_metadata()
    assert q011ci_study["study_gate"] == "passed"
    assert q011ci_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011ci_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 945
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ci_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 3
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ci_study, allow_nan=False)

    runner_path = Path(q011ci.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011ci_degree34_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ci artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ci.q011b._canonical_json_sha256(
            q011ci._result_digest_sections(artifact["cycle"])
        )
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
