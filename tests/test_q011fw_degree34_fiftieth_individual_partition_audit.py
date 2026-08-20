from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fw_degree34_fiftieth_individual_partition_audit as q011fw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "3bd5663e7e8643d7a0dd3678a4396149003187ac6de0c45e4bfe075cc7a68ce9"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "4e4e6738308904c24e858e29ac1236eb02e893288c5d0e6eaa59a8d72c3e5e5f"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "3faecea507ad79fe271a3df219efdc46587b03aefb170b64291711bd566f7e7a",
    "partition_input_digest_sha256": "8fd4e1646e6db323eb03ef2e65cb260c426c2959aae42845b188e2fa438a611f",
    "allocation_audit_digest_sha256": "7a93acdde695681e1c28242ba424dcebc91382a25b7864a6721cb22df1233dec",
    "result_digest_sha256": "f423c7433a79dae424ddca2e5be50ebb5c788f27c92e749ebe415e1a950b28a8",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": "37ed48405c78732a4738c913d8e0952000293b68d0856c8a4abb156a75c8594d",
    "parent_center_product_interval_digest_sha256": "8b67078709ca7fae558d5da464a58076f527a76de36fb1607e6144bb8143b11d",
    "parent_target_interval_digest_sha256": "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679",
    "parent_intersection_interval_digest_sha256": "43f7d84f2ec35dae64dc7640becfb700cf5b034dd5ae315d50c13b6d17cd60e1",
    "allocation_classification_record_digest_sha256": "5b53fb999f3001c2b90dfe3aa7cbe1c23688db2eb8767c37a3e02e33e764186f",
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011fw_structure() -> dict[str, Any]:
    sealed, artifacts = q011fw._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011fw._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011fw_study() -> dict[str, Any]:
    return q011fw.run_q011fw_study()


@pytest.fixture(scope="module")
def q011fw_cycle(q011fw_study: dict[str, Any]) -> dict[str, Any]:
    return q011fw_study["cycle"]


def test_q011fw_seals_q011fv_and_all_prior_inputs(
    q011fw_structure: dict[str, Any],
) -> None:
    sealed = q011fw_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 157
    assert sealed["direct_digest_count"] == 719
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fv"]["digests"]) == q011fw.Q011FV_DIGESTS
    assert sealed["q011fv"]["artifact_sha256"] == q011fw.Q011FV_ARTIFACT_SHA256
    assert sealed["q011fv"]["runner_sha256"] == q011fw.Q011FV_RUNNER_SHA256
    assert sealed["q011fv"]["resolved_witness_digest_sha256"] == (
        q011fw.EXPECTED_ORDINAL_FORTY_EIGHT_RESOLUTION_DIGEST
    )


def test_q011fw_selects_exactly_flatten_ordinal_forty_nine(
    q011fw_structure: dict[str, Any],
) -> None:
    fixed = q011fw_structure["fixed"]
    selection = fixed["fiftieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 49
    assert selection["selected_left_index"] == 6
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(49))
    assert selection["ordinal_forty_eight_resolution_digest_sha256"] == (
        q011fw.EXPECTED_ORDINAL_FORTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["fiftieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [6, 3], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 1_854
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fw_reconstructs_registered_partition_and_inventory(
    q011fw_structure: dict[str, Any],
) -> None:
    fixed = q011fw_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [6, 3],
        [5],
        [1, 6],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 6, 3, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fw.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 32_928
    assert fixed["full_allocation_digest_sha256"] == q011fw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_854
    assert q011fw_structure["compatible_count"] == 1_854
    assert fixed["compatible_allocation_digest_sha256"] == (q011fw.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 6, 0, 3, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [13, 0, 6, 0, 3, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 32_844
    assert fixed["parent_witness_compatible_index"] == 1_853
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fw result is not sealed")
def test_q011fw_classifies_every_registered_exact_interval(
    q011fw_cycle: dict[str, Any],
) -> None:
    partition = q011fw_cycle["individual_allocation_interval_audit"]
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
        assert record["intersection_width_hex"] == q011fw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fw.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_854,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fw result is not sealed")
def test_q011fw_applies_the_registered_exclusive_stopping_rule(
    q011fw_cycle: dict[str, Any],
) -> None:
    assert q011fw_cycle["study_validity"] == "passed"
    assert q011fw_cycle["failed_validity_order"] == []
    assert q011fw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fw_cycle["diagnostic_gates"].values())
    assert q011fw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fw_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fw_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fw_cycle["diagnostic_classification"] == q011fw.INERT_CLASSIFICATION
    assert not q011fw_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fiftieth_q011cb_witness"],
        theorem["fiftieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fiftieth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fw result is not sealed")
def test_q011fw_preserves_boundary_and_reproducible_digests(
    q011fw_cycle: dict[str, Any],
) -> None:
    theorem = q011fw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_fiftieth_q011cb_witness"],
        theorem["fiftieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_fiftieth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
    assert theorem["q011fv_ordinal_forty_eight_phase_resolution_is_preserved"]
    assert theorem["q011fu_ordinal_forty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ft_ordinal_forty_seven_phase_resolution_is_preserved"]
    assert theorem["q011fs_ordinal_forty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fr_ordinal_forty_six_phase_resolution_is_preserved"]
    assert theorem["q011fq_ordinal_forty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fp_ordinal_forty_five_phase_resolution_is_preserved"]
    assert theorem["q011fo_ordinal_forty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fn_ordinal_forty_four_phase_resolution_is_preserved"]
    assert theorem["q011fm_ordinal_forty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fl_ordinal_forty_three_phase_resolution_is_preserved"]
    assert theorem["q011fk_ordinal_forty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fj_ordinal_forty_two_phase_resolution_is_preserved"]
    assert theorem["q011fi_ordinal_forty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fh_ordinal_forty_one_phase_resolution_is_preserved"]
    assert theorem["q011fg_ordinal_forty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ff_ordinal_forty_phase_resolution_is_preserved"]
    assert theorem["q011fe_ordinal_forty_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fd_ordinal_thirty_nine_phase_resolution_is_preserved"]
    assert theorem["q011fc_ordinal_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011fb_ordinal_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011fa_ordinal_thirty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ez_ordinal_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011ey_ordinal_thirty_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ex_ordinal_thirty_six_phase_resolution_is_preserved"]
    assert theorem["q011ew_ordinal_thirty_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ev_ordinal_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011et_ordinal_thirty_four_phase_resolution_is_preserved"]
    assert theorem["q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011er_ordinal_thirty_three_phase_resolution_is_preserved"]
    assert theorem["q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 49" in q011fw_cycle["claim_boundary"]
    assert "ordinals 0 through 48" in q011fw_cycle["claim_boundary"]
    assert "later 44750 Q011cb refined signatures" in q011fw_cycle["claim_boundary"]
    assert "Q011fx" in q011fw_cycle["next_change"]
    json.dumps(q011fw_cycle, allow_nan=False)
    assert {name: q011fw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fw_cycle["result_digest_sha256"] == (
        q011fw.q011b._canonical_json_sha256(q011fw._result_digest_sections(q011fw_cycle))
    )
    assert q011fw._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fw result is not sealed")
def test_q011fw_study_metadata_and_optional_artifact_are_scoped(
    q011fw_study: dict[str, Any],
) -> None:
    assert q011fw_study["schema_version"] == 1
    assert q011fw_study["source"] == source_metadata()
    assert q011fw_study["study_gate"] == "passed"
    assert q011fw_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_854
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 49
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fw_study, allow_nan=False)

    runner_path = Path(q011fw.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fw_degree34_fiftieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fw_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fw.q011b._canonical_json_sha256(q011fw._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
