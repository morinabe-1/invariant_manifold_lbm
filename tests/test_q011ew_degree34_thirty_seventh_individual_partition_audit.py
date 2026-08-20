from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ew_degree34_thirty_seventh_individual_partition_audit as q011ew
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "",
    "partition_input_digest_sha256": "",
    "allocation_audit_digest_sha256": "",
    "result_digest_sha256": "",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "5f670704c6c692648f104bcd8fbb5558bfbc3db70a3f50a26624b018d852e6bc"
    ),
    "parent_center_product_interval_digest_sha256": (
        "98697b262f8bdc6faed0dbba557f43407ffa20ea38cc7463927cc11d11a14443"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "4fc40b082b4110001da5b77106ca6ac78c2b1be1697909a908399bba04a0c007"
    ),
    "allocation_classification_record_digest_sha256": "",
}


@pytest.fixture(scope="module")
def q011ew_study() -> dict[str, Any]:
    return q011ew.run_q011ew_study()


@pytest.fixture(scope="module")
def q011ew_cycle(q011ew_study: dict[str, Any]) -> dict[str, Any]:
    return q011ew_study["cycle"]


def test_q011ew_seals_q011ev_and_all_prior_inputs(
    q011ew_cycle: dict[str, Any],
) -> None:
    sealed = q011ew_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 131
    assert sealed["direct_digest_count"] == 602
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ev"]["digests"]) == q011ew.Q011EV_DIGESTS
    assert sealed["q011ev"]["artifact_sha256"] == q011ew.Q011EV_ARTIFACT_SHA256
    assert sealed["q011ev"]["runner_sha256"] == q011ew.Q011EV_RUNNER_SHA256
    assert sealed["q011ev"]["resolved_witness_digest_sha256"] == (
        q011ew.EXPECTED_ORDINAL_THIRTY_FIVE_RESOLUTION_DIGEST
    )


def test_q011ew_selects_exactly_flatten_ordinal_thirty_six(
    q011ew_cycle: dict[str, Any],
) -> None:
    fixed = q011ew_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_seventh_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 36
    assert selection["selected_left_index"] == 4
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(36))
    assert selection["ordinal_thirty_five_resolution_digest_sha256"] == (
        q011ew.EXPECTED_ORDINAL_THIRTY_FIVE_RESOLUTION_DIGEST
    )
    parent = selection["thirty_seventh_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [4, 5], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 2_837
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ew.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011ew.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011ew.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ew_reconstructs_registered_partition_and_inventory(
    q011ew_cycle: dict[str, Any],
) -> None:
    fixed = q011ew_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [4, 5],
        [5],
        [4, 3],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 4, 5, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011ew.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011ew.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 50_400
    assert fixed["full_allocation_digest_sha256"] == q011ew.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_837
    assert fixed["compatible_allocation_digest_sha256"] == (q011ew.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 4, 0, 5, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 4, 0, 5, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 50_280
    assert fixed["parent_witness_compatible_index"] == 2_836
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011ew_classifies_every_registered_exact_interval(
    q011ew_cycle: dict[str, Any],
) -> None:
    partition = q011ew_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_837
    records = partition["allocation_classification_records"]
    assert len(records) == 2_837
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_837))
    for record in records:
        assert record["degree"] == 34
        assert record["output_block"] == 7
        assert record["exact_relation"] in {
            "product_below_target",
            "target_below_product",
            "overlap",
        }
        assert record["binary64_outward_relation"] in {
            "product_below_target",
            "target_below_product",
            "overlap",
        }
        assert isinstance(record["product_equals_parent"], bool)
        assert isinstance(record["intersection_equals_parent"], bool)
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011ew partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011ew_applies_the_registered_exclusive_stopping_rule(
    q011ew_cycle: dict[str, Any],
) -> None:
    assert q011ew_cycle["study_validity"] == "passed"
    assert q011ew_cycle["failed_validity_order"] == []
    assert q011ew_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ew_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ew_cycle["diagnostic_gates"].values())
    assert q011ew_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ew_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ew_cycle["refinement_outcome"] in {
        "partition_inert_persistent",
        "resolved_by_individual_partition",
        "partition_effective_but_persistent",
    }
    assert q011ew_cycle["diagnostic_classification"] in {
        q011ew.INERT_CLASSIFICATION,
        q011ew.RESOLVED_CLASSIFICATION,
        q011ew.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }
    partition = q011ew_cycle["individual_allocation_interval_audit"]
    assert set(partition["exact_relation_counts"]) == {
        "product_below_target",
        "target_below_product",
        "overlap",
    }
    assert sum(partition["exact_relation_counts"].values()) == 2_837
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_837
    assert not partition["complex_phase_product_evaluated"]
    theorem = q011ew_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_thirty_seventh_q011cb_witness"],
        theorem["thirty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_thirty_seventh_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


def test_q011ew_preserves_boundary_and_reproducible_digests(
    q011ew_cycle: dict[str, Any],
) -> None:
    theorem = q011ew_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_thirty_seventh_q011cb_witness"],
        theorem["thirty_seventh_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_thirty_seventh_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1
    assert theorem["q011ev_ordinal_thirty_five_phase_resolution_is_preserved"]
    assert theorem["q011eu_ordinal_thirty_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011et_ordinal_thirty_four_phase_resolution_is_preserved"]
    assert theorem["q011es_ordinal_thirty_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011er_ordinal_thirty_three_phase_resolution_is_preserved"]
    assert theorem["q011eq_ordinal_thirty_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ep_ordinal_thirty_two_phase_resolution_is_preserved"]
    assert theorem["q011eo_ordinal_thirty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011en_ordinal_thirty_one_phase_resolution_is_preserved"]
    assert theorem["q011em_ordinal_thirty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011el_ordinal_thirty_phase_resolution_is_preserved"]
    assert theorem["q011ek_ordinal_thirty_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 36" in q011ew_cycle["claim_boundary"]
    assert "later 44763 Q011cb refined signatures" in q011ew_cycle["claim_boundary"]
    assert "Q011ex" in q011ew_cycle["next_change"]
    json.dumps(q011ew_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011ew section digests have not been sealed yet")
    assert {name: q011ew_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ew_cycle["result_digest_sha256"] == (
        q011ew.q011b._canonical_json_sha256(q011ew._result_digest_sections(q011ew_cycle))
    )
    assert q011ew._protocol_globals_are_restored()


def test_q011ew_study_metadata_and_optional_artifact_are_scoped(
    q011ew_study: dict[str, Any],
) -> None:
    assert q011ew_study["schema_version"] == 1
    assert q011ew_study["source"] == source_metadata()
    assert q011ew_study["study_gate"] == "passed"
    assert q011ew_study["refinement_outcome"] in {
        "partition_inert_persistent",
        "resolved_by_individual_partition",
        "partition_effective_but_persistent",
    }
    runtime = q011ew_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_837
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ew_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 36
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ew_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011ew runner hash has not been sealed yet")
    runner_path = Path(q011ew.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ew_degree34_thirty_seventh_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ew artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ew_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ew.q011b._canonical_json_sha256(q011ew._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
