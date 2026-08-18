from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011dy_degree34_twenty_fifth_individual_partition_audit as q011dy
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "1e8cddca3f0a942b0248339f940ff73e13133908e921c56649e29eca366c6eb7"
)
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "b10550591abd0b42d6dd48a7e20ef23017e9abc5d58c6527271ecf4c1200d99b",
    "partition_input_digest_sha256": "8627898a66a6eb756b989e06e54003cda47b0c7c7b81009be76843ab69ddff2e",
    "allocation_audit_digest_sha256": "aa30f5d2b5193860dfd7ec34430a80f9099cf32793bb07c9985461eab264c20b",
    "result_digest_sha256": "b2931a291407b3328139e23768e96e217899edf3452e5cb0c6b40ee5ac09af35",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "9870167a9cb445538c31d52447a3f52f6c84ce30859076febff8d888c292ef3f"
    ),
    "parent_center_product_interval_digest_sha256": (
        "9da9fb06335c9be54cab798fcf579fd53042546e4f29d7ba80ca1d5b33df7467"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "fdd668cb09ecf2897ce0464e9032de8010f60d7572bd1d2a68c8c77154570eb0"
    ),
    "allocation_classification_record_digest_sha256": (
        "1586a07f6f70891b4546b8481d72ffe192f57204a5012775c9643dc172c61ec2"
    ),
}


@pytest.fixture(scope="module")
def q011dy_study() -> dict[str, Any]:
    return q011dy.run_q011dy_study()


@pytest.fixture(scope="module")
def q011dy_cycle(q011dy_study: dict[str, Any]) -> dict[str, Any]:
    return q011dy_study["cycle"]


def test_q011dy_seals_q011dx_and_all_prior_inputs(
    q011dy_cycle: dict[str, Any],
) -> None:
    sealed = q011dy_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 107
    assert sealed["direct_digest_count"] == 494
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011dx"]["digests"]) == q011dy.Q011DX_DIGESTS
    assert sealed["q011dx"]["artifact_sha256"] == q011dy.Q011DX_ARTIFACT_SHA256
    assert sealed["q011dx"]["runner_sha256"] == q011dy.Q011DX_RUNNER_SHA256
    assert sealed["q011dx"]["resolved_witness_digest_sha256"] == (
        q011dy.EXPECTED_ORDINAL_TWENTY_THREE_RESOLUTION_DIGEST
    )


def test_q011dy_selects_exactly_flatten_ordinal_twenty_four(
    q011dy_cycle: dict[str, Any],
) -> None:
    fixed = q011dy_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["twenty_fifth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 24
    assert selection["selected_left_index"] == 3
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(24))
    assert selection["ordinal_twenty_three_resolution_digest_sha256"] == (
        q011dy.EXPECTED_ORDINAL_TWENTY_THREE_RESOLUTION_DIGEST
    )
    parent = selection["twenty_fifth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [3, 6], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_061
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011dy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011dy.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011dy.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011dy_reconstructs_registered_partition_and_inventory(
    q011dy_cycle: dict[str, Any],
) -> None:
    fixed = q011dy_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [3, 6],
        [5],
        [0, 7],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 3, 6, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011dy.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011dy.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 18_816
    assert fixed["full_allocation_digest_sha256"] == q011dy.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_061
    assert fixed["compatible_allocation_digest_sha256"] == (q011dy.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 3, 0, 6, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 3, 0, 6, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 18_768
    assert fixed["parent_witness_compatible_index"] == 1_060
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011dy_all_exact_intervals_are_parent_identical(
    q011dy_cycle: dict[str, Any],
) -> None:
    partition = q011dy_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_061
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_061
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_061))
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
        assert record["intersection_width_hex"] == (q011dy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX)
        assert record["center_only_gap_hex"] == q011dy.EXPECTED_PARENT_CENTER_GAP_HEX
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011dy_records_interval_inert_persistence(
    q011dy_cycle: dict[str, Any],
) -> None:
    assert q011dy_cycle["study_validity"] == "passed"
    assert q011dy_cycle["failed_validity_order"] == []
    assert q011dy_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011dy_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011dy_cycle["diagnostic_gates"].values())
    assert q011dy_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011dy_cycle["diagnostic_classification"] == q011dy.INERT_CLASSIFICATION
    assert q011dy_cycle["scientific_outcome"] == "not_evaluated"
    assert q011dy_cycle["actual_resonance_outcome"] == "not_established"
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_061,
    }
    partition = q011dy_cycle["individual_allocation_interval_audit"]
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert not partition["complex_phase_product_evaluated"]


def test_q011dy_preserves_boundary_and_reproducible_digests(
    q011dy_cycle: dict[str, Any],
) -> None:
    theorem = q011dy_cycle["theorem_consequence"]
    assert theorem["individual_partition_is_interval_inert_for_twenty_fifth_q011cb_witness"]
    assert not theorem["twenty_fifth_q011cb_witness_is_resolved_by_individual_partition"]
    assert theorem["q011dx_ordinal_twenty_three_phase_resolution_is_preserved"]
    assert theorem["q011dw_ordinal_twenty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dv_ordinal_twenty_two_phase_resolution_is_preserved"]
    assert theorem["q011du_ordinal_twenty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dt_ordinal_twenty_one_phase_resolution_is_preserved"]
    assert theorem["q011ds_ordinal_twenty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dr_ordinal_twenty_phase_resolution_is_preserved"]
    assert theorem["q011dq_ordinal_twenty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dp_ordinal_nineteen_phase_resolution_is_preserved"]
    assert theorem["q011do_ordinal_nineteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dn_ordinal_eighteen_phase_resolution_is_preserved"]
    assert theorem["q011dm_ordinal_eighteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dl_ordinal_seventeen_phase_resolution_is_preserved"]
    assert theorem["q011dk_ordinal_seventeen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dj_ordinal_sixteen_phase_resolution_is_preserved"]
    assert theorem["q011di_ordinal_sixteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dh_ordinal_fifteen_phase_resolution_is_preserved"]
    assert theorem["q011dg_ordinal_fifteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011df_ordinal_fourteen_phase_resolution_is_preserved"]
    assert theorem["q011de_ordinal_fourteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011dd_ordinal_thirteen_phase_resolution_is_preserved"]
    assert theorem["q011dc_ordinal_thirteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011db_ordinal_twelve_phase_resolution_is_preserved"]
    assert theorem["q011da_ordinal_twelve_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011cx_ordinal_ten_phase_resolution_is_preserved"]
    assert theorem["q011cv_ordinal_nine_phase_resolution_is_preserved"]
    assert theorem["q011ct_ordinal_eight_phase_resolution_is_preserved"]
    assert theorem["q011cr_ordinal_seven_phase_resolution_is_preserved"]
    assert theorem["q011cp_ordinal_six_phase_resolution_is_preserved"]
    assert theorem["q011cn_ordinal_five_phase_resolution_is_preserved"]
    assert theorem["q011cl_ordinal_four_phase_resolution_is_preserved"]
    assert theorem["q011cj_ordinal_three_phase_resolution_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 24" in q011dy_cycle["claim_boundary"]
    assert "later 44775 Q011cb refined signatures" in q011dy_cycle["claim_boundary"]
    assert "Q011dz" in q011dy_cycle["next_change"]
    json.dumps(q011dy_cycle, allow_nan=False)
    assert {name: q011dy_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011dy_cycle["result_digest_sha256"] == (
        q011dy.q011b._canonical_json_sha256(q011dy._result_digest_sections(q011dy_cycle))
    )
    assert q011dy._protocol_globals_are_restored()


def test_q011dy_study_metadata_and_optional_artifact_are_scoped(
    q011dy_study: dict[str, Any],
) -> None:
    assert q011dy_study["schema_version"] == 1
    assert q011dy_study["source"] == source_metadata()
    assert q011dy_study["study_gate"] == "passed"
    assert q011dy_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011dy_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_061
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011dy_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 24
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011dy_study, allow_nan=False)

    runner_path = Path(q011dy.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011dy runner hash has not been sealed yet")
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011dy_degree34_twenty_fifth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011dy artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "partition_inert_persistent"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011dy.q011b._canonical_json_sha256(q011dy._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
