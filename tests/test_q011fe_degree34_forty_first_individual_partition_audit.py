from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011fe_degree34_forty_first_individual_partition_audit as q011fe
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "44046645e957e400ce0e87b037220a3725c72a04912dbf030ff50c5aead87f21"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "03191a7c5ab64d7bc9a0d100c509606c44465ae1eb06f2790d56f9cdbac2ad6c"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "84b5002354d5982d72f3019484ff335cb1da441c0b44dc41da31993316bc29d7",
    "partition_input_digest_sha256": "e6a7c9a70a85fee2de1360ca7116ea444bbe04557de40dfa2abb6ca9bc2cff1e",
    "allocation_audit_digest_sha256": "befc3bf6ae5652b57f4f2f10f4ca338d0552d7cc7137d85b5a42828f672c9aed",
    "result_digest_sha256": "114f06c600a8a7fa0842d9232f0e9b457457675b687cab6517086771acbf1d03",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "a870e567acd9731df414175d6980709270ad3274d92bfda2ca7eec1c07ad80e0"
    ),
    "parent_center_product_interval_digest_sha256": (
        "c8df7e1575e539a47bdca7444afeaa08a1afc297b8efad02cd700c935507442b"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "f7291a4298c2f8c3320a7b2de6682f43a31dfe260dc7ef2cd746830c471867dc"
    ),
    "allocation_classification_record_digest_sha256": (
        "e4bd7d6a3b540dd1a212de6ef5fd801d4c8e28423f53bbd7ad5a392a9eb54fcf"
    ),
}
RESULT_EXPECTATIONS_FIXED = (
    EXPECTED_SECTION_DIGESTS is not None and EXPECTED_PARTITION_DIGESTS is not None
)


@pytest.fixture(scope="module")
def q011fe_structure() -> dict[str, Any]:
    sealed, artifacts = q011fe._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011fe._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011fe_study() -> dict[str, Any]:
    return q011fe.run_q011fe_study()


@pytest.fixture(scope="module")
def q011fe_cycle(q011fe_study: dict[str, Any]) -> dict[str, Any]:
    return q011fe_study["cycle"]


def test_q011fe_seals_q011fd_and_all_prior_inputs(
    q011fe_structure: dict[str, Any],
) -> None:
    sealed = q011fe_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 139
    assert sealed["direct_digest_count"] == 638
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011fd"]["digests"]) == q011fe.Q011FD_DIGESTS
    assert sealed["q011fd"]["artifact_sha256"] == q011fe.Q011FD_ARTIFACT_SHA256
    assert sealed["q011fd"]["runner_sha256"] == q011fe.Q011FD_RUNNER_SHA256
    assert sealed["q011fd"]["resolved_witness_digest_sha256"] == (
        q011fe.EXPECTED_ORDINAL_THIRTY_NINE_RESOLUTION_DIGEST
    )


def test_q011fe_selects_exactly_flatten_ordinal_forty(
    q011fe_structure: dict[str, Any],
) -> None:
    fixed = q011fe_structure["fixed"]
    selection = fixed["forty_first_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 40
    assert selection["selected_left_index"] == 5
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(40))
    assert selection["ordinal_thirty_nine_resolution_digest_sha256"] == (
        q011fe.EXPECTED_ORDINAL_THIRTY_NINE_RESOLUTION_DIGEST
    )
    parent = selection["forty_first_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [5, 4], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_136
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011fe.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011fe.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011fe.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011fe_reconstructs_registered_partition_and_inventory(
    q011fe_structure: dict[str, Any],
) -> None:
    fixed = q011fe_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [
        [0, 0, 0, 13],
        [5, 4],
        [5],
        [0, 7],
    ]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 5, 4, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011fe.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011fe.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 20_160
    assert fixed["full_allocation_digest_sha256"] == q011fe.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_136
    assert q011fe_structure["compatible_count"] == 1_136
    assert fixed["compatible_allocation_digest_sha256"] == (q011fe.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 13, 0, 5, 0, 4, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [13, 0, 5, 0, 4, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 20_112
    assert fixed["parent_witness_compatible_index"] == 1_135
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fe result is not sealed")
def test_q011fe_classifies_every_registered_exact_interval(
    q011fe_cycle: dict[str, Any],
) -> None:
    partition = q011fe_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_136
    assert partition["all_product_target_intersection_and_center_records_equal_parent"]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_136
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_136))
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
        assert record["intersection_width_hex"] == q011fe.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
        assert record["center_only_gap_hex"] == q011fe.EXPECTED_PARENT_CENTER_GAP_HEX
    expected_relations = {
        "product_below_target": 0,
        "target_below_product": 0,
        "overlap": 1_136,
    }
    assert partition["exact_relation_counts"] == expected_relations
    assert partition["binary64_outward_relation_counts"] == expected_relations
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fe result is not sealed")
def test_q011fe_applies_the_registered_exclusive_stopping_rule(
    q011fe_cycle: dict[str, Any],
) -> None:
    assert q011fe_cycle["study_validity"] == "passed"
    assert q011fe_cycle["failed_validity_order"] == []
    assert q011fe_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011fe_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011fe_cycle["diagnostic_gates"].values())
    assert q011fe_cycle["scientific_outcome"] == "not_evaluated"
    assert q011fe_cycle["actual_resonance_outcome"] == "not_established"
    assert q011fe_cycle["refinement_outcome"] == "partition_inert_persistent"
    assert q011fe_cycle["diagnostic_classification"] == q011fe.INERT_CLASSIFICATION
    assert not q011fe_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011fe_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_first_q011cb_witness"],
        theorem["forty_first_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_first_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fe result is not sealed")
def test_q011fe_preserves_boundary_and_reproducible_digests(
    q011fe_cycle: dict[str, Any],
) -> None:
    theorem = q011fe_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_forty_first_q011cb_witness"],
        theorem["forty_first_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_forty_first_q011cb_witness_persists"],
    )
    assert flags == (True, False, False)
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
    assert "flatten ordinal 40" in q011fe_cycle["claim_boundary"]
    assert "ordinals 0 through 39" in q011fe_cycle["claim_boundary"]
    assert "later 44759 Q011cb refined signatures" in q011fe_cycle["claim_boundary"]
    assert "Q011ff" in q011fe_cycle["next_change"]
    json.dumps(q011fe_cycle, allow_nan=False)
    assert {name: q011fe_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011fe_cycle["result_digest_sha256"] == (
        q011fe.q011b._canonical_json_sha256(q011fe._result_digest_sections(q011fe_cycle))
    )
    assert q011fe._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011fe result is not sealed")
def test_q011fe_study_metadata_and_optional_artifact_are_scoped(
    q011fe_study: dict[str, Any],
) -> None:
    assert q011fe_study["schema_version"] == 1
    assert q011fe_study["source"] == source_metadata()
    assert q011fe_study["study_gate"] == "passed"
    assert q011fe_study["refinement_outcome"] == "partition_inert_persistent"
    runtime = q011fe_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_136
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011fe_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 40
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011fe_study, allow_nan=False)

    runner_path = Path(q011fe.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011fe_degree34_forty_first_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011fe artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011fe_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011fe.q011b._canonical_json_sha256(q011fe._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
