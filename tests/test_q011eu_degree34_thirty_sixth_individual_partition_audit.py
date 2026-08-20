from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011eu_degree34_thirty_sixth_individual_partition_audit as q011eu
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
        "a406329140c983c0cd71e3e64da267740f2a3fc4983dc30166de85e7a196916c"
    ),
    "parent_center_product_interval_digest_sha256": (
        "23cdfa409652402b366882a0f15b3cfdced94eab4be6b065af1fe0fbe103c11a"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "b771967506f64580b4fc006aa340c93578b96fb092643aa1483c947c4c9ed131"
    ),
    "allocation_classification_record_digest_sha256": "",
}


@pytest.fixture(scope="module")
def q011eu_study() -> dict[str, Any]:
    return q011eu.run_q011eu_study()


@pytest.fixture(scope="module")
def q011eu_cycle(q011eu_study: dict[str, Any]) -> dict[str, Any]:
    return q011eu_study["cycle"]


def test_q011eu_seals_q011et_and_all_prior_inputs(
    q011eu_cycle: dict[str, Any],
) -> None:
    sealed = q011eu_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 129
    assert sealed["direct_digest_count"] == 593
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011et"]["digests"]) == q011eu.Q011ET_DIGESTS
    assert sealed["q011et"]["artifact_sha256"] == q011eu.Q011ET_ARTIFACT_SHA256
    assert sealed["q011et"]["runner_sha256"] == q011eu.Q011ET_RUNNER_SHA256
    assert sealed["q011et"]["resolved_witness_digest_sha256"] == (
        q011eu.EXPECTED_ORDINAL_THIRTY_FOUR_RESOLUTION_DIGEST
    )


def test_q011eu_selects_exactly_flatten_ordinal_thirty_five(
    q011eu_cycle: dict[str, Any],
) -> None:
    fixed = q011eu_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_sixth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 35
    assert selection["selected_left_index"] == 4
    assert selection["selected_right_index"] == 3
    assert selection["previous_phase_resolved_ordinals"] == list(range(35))
    assert selection["ordinal_thirty_four_resolution_digest_sha256"] == (
        q011eu.EXPECTED_ORDINAL_THIRTY_FOUR_RESOLUTION_DIGEST
    )
    parent = selection["thirty_sixth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [4, 5], [5], [3, 4]]
    assert parent["wave_multiplicity"] == 2_837
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011eu.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011eu.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011eu.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011eu_reconstructs_registered_partition_and_inventory(
    q011eu_cycle: dict[str, Any],
) -> None:
    fixed = q011eu_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [4, 5],
        [5],
        [3, 4],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 4, 5, 5, 3, 4]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011eu.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011eu.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 50_400
    assert fixed["full_allocation_digest_sha256"] == q011eu.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_837
    assert fixed["compatible_allocation_digest_sha256"] == (q011eu.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 4, 0, 5, 0, 5, 1, 2, 4, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 4, 0, 5, 0, 0, 5, 0, 3, 0, 4]
    assert fixed["parent_witness_allocation_index"] == 50_280
    assert fixed["parent_witness_compatible_index"] == 2_836
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011eu_classifies_every_registered_exact_interval(
    q011eu_cycle: dict[str, Any],
) -> None:
    partition = q011eu_cycle["individual_allocation_interval_audit"]
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
        assert record["binary64_outward_relation"] == record["exact_relation"]
        assert isinstance(record["product_equals_parent"], bool)
        assert isinstance(record["intersection_equals_parent"], bool)
    if not EXPECTED_PARTITION_DIGESTS["allocation_classification_record_digest_sha256"]:
        pytest.skip("Q011eu partition record digest has not been sealed yet")
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011eu_applies_the_registered_exclusive_stopping_rule(
    q011eu_cycle: dict[str, Any],
) -> None:
    assert q011eu_cycle["study_validity"] == "passed"
    assert q011eu_cycle["failed_validity_order"] == []
    assert q011eu_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011eu_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011eu_cycle["diagnostic_gates"].values())
    assert q011eu_cycle["scientific_outcome"] == "not_evaluated"
    assert q011eu_cycle["actual_resonance_outcome"] == "not_established"
    partition = q011eu_cycle["individual_allocation_interval_audit"]
    assert sum(partition["exact_relation_counts"].values()) == 2_837
    assert partition["binary64_outward_relation_counts"] == partition["exact_relation_counts"]
    assert not partition["complex_phase_product_evaluated"]
    theorem = q011eu_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_thirty_sixth_q011cb_witness"],
        theorem["thirty_sixth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_thirty_sixth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1
    assert q011eu_cycle["refinement_outcome"] in {
        "partition_inert_persistent",
        "resolved_by_individual_partition",
        "partition_effective_but_persistent",
    }


def test_q011eu_preserves_boundary_and_reproducible_digests(
    q011eu_cycle: dict[str, Any],
) -> None:
    theorem = q011eu_cycle["theorem_consequence"]
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
    assert "flatten ordinal 35" in q011eu_cycle["claim_boundary"]
    assert "later 44764 Q011cb refined signatures" in q011eu_cycle["claim_boundary"]
    assert "Q011ev" in q011eu_cycle["next_change"]
    json.dumps(q011eu_cycle, allow_nan=False)
    if not all(EXPECTED_SECTION_DIGESTS.values()):
        pytest.skip("Q011eu section digests have not been sealed yet")
    assert {name: q011eu_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011eu_cycle["result_digest_sha256"] == (
        q011eu.q011b._canonical_json_sha256(q011eu._result_digest_sections(q011eu_cycle))
    )
    assert q011eu._protocol_globals_are_restored()


def test_q011eu_study_metadata_and_optional_artifact_are_scoped(
    q011eu_study: dict[str, Any],
) -> None:
    assert q011eu_study["schema_version"] == 1
    assert q011eu_study["source"] == source_metadata()
    assert q011eu_study["study_gate"] == "passed"
    assert q011eu_study["refinement_outcome"] in {
        "partition_inert_persistent",
        "resolved_by_individual_partition",
        "partition_effective_but_persistent",
    }
    runtime = q011eu_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_837
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011eu_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 35
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011eu_study, allow_nan=False)

    if EXPECTED_RUNNER_SHA256 is None:
        pytest.skip("Q011eu runner hash has not been sealed yet")
    runner_path = Path(q011eu.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011eu_degree34_thirty_sixth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011eu artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011eu_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011eu.q011b._canonical_json_sha256(q011eu._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
