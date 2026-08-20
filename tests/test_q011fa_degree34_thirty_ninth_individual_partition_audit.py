from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fa_degree34_thirty_ninth_individual_partition_audit as q011fa
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "263cc17faf6ac14d0d88038e2400369c54c6c92ca112a9fe7fd07bce4c97616b"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "5b450638493cb6eebf80d56a5a76b9bffb4faae30d607ee26e8cccf22621f881"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "cde531cef0a4c58cc5965aa03f05fd0d19c6fefccbc21c356548d572dc770d6d",
    "partition_input_digest_sha256": "6aa5bbac2497b3c802d868b8b41af747141c47f29e290036ba1c3b1ec5e00d70",
    "allocation_audit_digest_sha256": "8e866b739a9a5ab9b9d754c7872f9aefb1d555b6e37938d599999152c94c86a8",
    "result_digest_sha256": "1581afb48418ff65e9eb4170e042af356d36a9d19e7f0044aa6770cc3a222070",
}
EXPECTED_PARTITION_DIGESTS = {
    "parent_product_interval_digest_sha256": (
        "f3cc609045a4303e46732494bc0494168a5c9b778dd9b84da33388a8275add95"
    ),
    "parent_center_product_interval_digest_sha256": (
        "79d96a1f69f46a17790b6b1e67f2870d65633f90912d110a85d127f8def9a801"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "5b7e1c7e0b740125eaf8ed517bdd6d904764b051e2fd36e5243a16a78a569241"
    ),
    "allocation_classification_record_digest_sha256": (
        "01f33fc65ae1d4202dc276c1024291b8951fcdfdb831d39f1190caea372bf252"
    ),
}


@pytest.fixture(scope="module")
def q011fa_study() -> dict[str, Any]:
    return q011fa.run_q011fa_study()


@pytest.fixture(scope="module")
def q011fa_cycle(q011fa_study: dict[str, Any]) -> dict[str, Any]:
    return q011fa_study["cycle"]


def test_q011fa_seals_q011ez_and_all_prior_inputs(
    q011fa_cycle: dict[str, Any],
) -> None:
    sealed = q011fa_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 135
    assert sealed["direct_digest_count"] == 620
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ez"]["digests"]) == q011fa.Q011EZ_DIGESTS
    assert sealed["q011ez"]["artifact_sha256"] == q011fa.Q011EZ_ARTIFACT_SHA256
    assert sealed["q011ez"]["runner_sha256"] == q011fa.Q011EZ_RUNNER_SHA256
    assert sealed["q011ez"]["resolved_witness_digest_sha256"] == (
        q011fa.EXPECTED_ORDINAL_THIRTY_SEVEN_RESOLUTION_DIGEST
    )


def test_q011fa_selects_exactly_flatten_ordinal_thirty_eight(
    q011fa_cycle: dict[str, Any],
) -> None:
    fixed = q011fa_cycle["fixed_individual_partition_input_audit"]
    selection = fixed["thirty_ninth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 38
    assert selection["selected_left_index"] == 4
    assert selection["selected_right_index"] == 6
    assert selection["previous_phase_resolved_ordinals"] == list(range(38))
    assert selection["ordinal_thirty_seven_resolution_digest_sha256"] == (
        q011fa.EXPECTED_ORDINAL_THIRTY_SEVEN_RESOLUTION_DIGEST
    )
    parent = selection["thirty_ninth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [4, 5], [5], [6, 1]]
    assert parent["wave_multiplicity"] == 1_986
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fa.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fa.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fa.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fa_reconstructs_registered_partition_and_inventory(
    q011fa_cycle: dict[str, Any],
) -> None:
    fixed = q011fa_cycle["fixed_individual_partition_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [4, 5],
        [5],
        [6, 1],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 4, 5, 5, 6, 1]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fa.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fa.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 35_280
    assert fixed["full_allocation_digest_sha256"] == q011fa.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_986
    assert fixed["compatible_allocation_digest_sha256"] == (q011fa.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 4, 0, 5, 0, 5, 4, 2, 1, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 4, 0, 5, 0, 0, 5, 0, 6, 0, 1]
    assert fixed["parent_witness_allocation_index"] == 35_196
    assert fixed["parent_witness_compatible_index"] == 1_985
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


def test_q011fa_classifies_every_registered_exact_interval(
    q011fa_cycle: dict[str, Any],
) -> None:
    partition = q011fa_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_986
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_986
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_986))
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
        assert record["intersection_width_hex"] == q011fa.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fa.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_986,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


def test_q011fa_applies_the_registered_exclusive_stopping_rule(
    q011fa_cycle: dict[str, Any],
) -> None:
    assert q011fa_cycle["study_validity"] == "passed"
    assert q011fa_cycle["failed_validity_order"] == []
    assert q011fa_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fa_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fa_cycle["diagnostic_gates"].values())
    assert q011fa_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fa_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fa_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fa_cycle["diagnostic_classification"] == q011fa.INERT_CLASSIFICATION
    assert not q011fa_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fa_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_thirty_ninth_q011cb_witness"],
        theorem["thirty_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_thirty_ninth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


def test_q011fa_preserves_boundary_and_reproducible_digests(
    q011fa_cycle: dict[str, Any],
) -> None:
    theorem = q011fa_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_thirty_ninth_q011cb_witness"],
        theorem["thirty_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_thirty_ninth_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 38" in q011fa_cycle["claim_boundary"]
    assert "later 44761 Q011cb refined signatures" in q011fa_cycle["claim_boundary"]
    assert "Q011fb" in q011fa_cycle["next_change"]
    json.dumps(q011fa_cycle, allow_nan=False)
    assert {name: q011fa_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fa_cycle["result_digest_sha256"] == (
        q011fa.q011b._canonical_json_sha256(q011fa._result_digest_sections(q011fa_cycle))
    )
    assert q011fa._protocol_globals_are_restored()


def test_q011fa_study_metadata_and_optional_artifact_are_scoped(
    q011fa_study: dict[str, Any],
) -> None:
    assert q011fa_study["schema_version"] == 1
    assert q011fa_study["source"] == source_metadata()
    assert q011fa_study["study_gate"] == "passed"
    assert q011fa_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fa_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_986
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fa_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 38
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fa_study, allow_nan=False)

    runner_path = Path(q011fa.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fa_degree34_thirty_ninth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fa artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fa_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fa.q011b._canonical_json_sha256(q011fa._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
