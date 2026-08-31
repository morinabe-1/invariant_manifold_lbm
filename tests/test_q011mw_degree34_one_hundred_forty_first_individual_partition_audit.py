from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011mw_degree34_one_hundred_forty_first_individual_partition_audit as q011mw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "48b0aaa643fb6c06c29079f6db24438f196c20cf3df0d8046ade42a354245c60"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "6b7ed93a023c832e965eee7c92d1ea799c4758ac3f8aae140a8f28fc908e8db3"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "00aa3f5f1bf05ae613c3c2b62372e42c29bb74a719207cd81fe58b8a830dcd35",
    "partition_input_digest_sha256": (
        "c992195def35918c7890d0e10f2bb5dd5322cbe2c11ec6ea76166a1a3b14ea50"
    ),
    "allocation_audit_digest_sha256": (
        "169cc1694c9014b97b291768b565bcdb161125dc93fd69b7413a65d37f090c4b"
    ),
    "result_digest_sha256": "88e553a016693249c4da1763ac6381177a9fdf840b61790ff830fafc04252ed2",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "99712ec650e8852d2ece78339ca6d2c5c60ac2396d1a42509a74dd34ba7a94b9"
    ),
    "parent_center_product_interval_digest_sha256": (
        "b4064fc4c76dd501cc8fdb53bae1161f0c4d877d63b7a34446efe17e0c0c6b27"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "5b1918de7bbef114ccb8c6d66d862f37204fc9056742e79543f27e9bfa6b654e"
    ),
    "allocation_classification_record_digest_sha256": (
        "9c18034ec9216df3a22429cfd214470a79a71f909eb83d0398f57fb679e8e0ef"
    ),
}
EXPECTED_REFINEMENT_OUTCOME: str | None = "partition_inert_persistent"
RESULT_EXPECTATIONS_FIXED = all(
    value is not None
    for value in (
        EXPECTED_RUNNER_SHA256,
        EXPECTED_ARTIFACT_SHA256,
        EXPECTED_SECTION_DIGESTS,
        EXPECTED_PARTITION_DIGESTS,
        EXPECTED_REFINEMENT_OUTCOME,
    )
)


@pytest.fixture(scope="module")
def q011mw_structure() -> dict[str, Any]:
    sealed, artifacts = q011mw._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011mw._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011mw_study() -> dict[str, Any]:
    return q011mw.run_q011mw_study()


@pytest.fixture(scope="module")
def q011mw_cycle(q011mw_study: dict[str, Any]) -> dict[str, Any]:
    return q011mw_study["cycle"]


def test_q011mw_seals_q011mv_and_all_prior_inputs(
    q011mw_structure: dict[str, Any],
) -> None:
    sealed = q011mw_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 339
    assert sealed["direct_digest_count"] == 1_538
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mv"]["digests"]) == q011mw.Q011MV_DIGESTS
    assert sealed["q011mv"]["artifact_sha256"] == q011mw.Q011MV_ARTIFACT_SHA256
    assert sealed["q011mv"]["runner_sha256"] == q011mw.Q011MV_RUNNER_SHA256
    assert sealed["q011mv"]["resolved_witness_digest_sha256"] == (
        q011mw.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_NINE_RESOLUTION_DIGEST
    )


def test_q011mw_selects_exactly_flatten_ordinal_one_hundred_forty(
    q011mw_structure: dict[str, Any],
) -> None:
    fixed = q011mw_structure["fixed"]
    selection = fixed["one_hundred_forty_first_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 140
    assert selection["selected_left_index"] == 17
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(140))
    assert selection["ordinal_one_hundred_thirty_nine_resolution_digest_sha256"] == (
        q011mw.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTY_NINE_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_forty_first_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 4_136
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011mw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011mw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011mw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011mw_reconstructs_registered_partition_and_inventory(
    q011mw_structure: dict[str, Any],
) -> None:
    fixed = q011mw_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [4, 3]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 7, 2, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011mw.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011mw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 74_880
    assert fixed["full_allocation_digest_sha256"] == q011mw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 4_136
    assert q011mw_structure["compatible_count"] == 4_136
    assert fixed["compatible_allocation_digest_sha256"] == q011mw.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [
        0,
        1,
        0,
        12,
        0,
        7,
        0,
        2,
        0,
        5,
        2,
        2,
        3,
        0,
    ]
    assert fixed["last_compatible_counts"] == [
        1,
        0,
        12,
        0,
        7,
        0,
        2,
        0,
        0,
        5,
        0,
        4,
        0,
        3,
    ]
    assert fixed["parent_witness_allocation_index"] == 74_760
    assert fixed["parent_witness_compatible_index"] == 4_135
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mw result is not sealed")
def test_q011mw_classifies_every_registered_exact_interval(
    q011mw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011mw_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 4_136
    records = partition["allocation_classification_records"]
    assert len(records) == 4_136
    assert [record["compatible_allocation_index"] for record in records] == list(range(4_136))
    assert sum(partition["exact_relation_counts"].values()) == 4_136
    assert sum(partition["binary64_outward_relation_counts"].values()) == 4_136
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mw result is not sealed")
def test_q011mw_applies_registered_stopping_rule(
    q011mw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011mw_cycle["study_validity"] == "passed"
    assert q011mw_cycle["failed_validity_order"] == []
    assert q011mw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011mw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011mw_cycle["diagnostic_gates"].values())
    assert q011mw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011mw_cycle["actual_resonance_outcome"] == "not_established"
    assert q011mw_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011mw.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011mw.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011mw.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011mw_cycle["diagnostic_classification"] == expected
    assert not q011mw_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011mw_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_forty_first_q011cb_witness"
        ],
        theorem["one_hundred_forty_first_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_forty_first_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mw result is not sealed")
def test_q011mw_preserves_boundary_and_reproducible_digests(
    q011mw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011mw_cycle["theorem_consequence"]
    assert theorem["q011mv_ordinal_one_hundred_thirty_nine_phase_resolution_is_preserved"]
    assert theorem["q011mu_ordinal_one_hundred_thirty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mt_ordinal_one_hundred_thirty_eight_phase_resolution_is_preserved"]
    assert theorem["q011ms_ordinal_one_hundred_thirty_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mr_ordinal_one_hundred_thirty_seven_phase_resolution_is_preserved"]
    assert theorem["q011ih_ordinal_eighty_phase_resolution_is_preserved"]
    assert all(
        value
        for name, value in theorem.items()
        if name.endswith("_is_preserved") and isinstance(value, bool)
    )
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert not theorem["complex_phase_product_is_audited"]
    assert "flatten ordinal 140" in q011mw_cycle["claim_boundary"]
    assert "ordinals 0 through 139" in q011mw_cycle["claim_boundary"]
    assert "later 44659 Q011cb refined signatures" in q011mw_cycle["claim_boundary"]
    assert "Q011mx" in q011mw_cycle["next_change"]
    assert {name: q011mw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011mw_cycle["result_digest_sha256"] == (
        q011mw.q011b._canonical_json_sha256(q011mw._result_digest_sections(q011mw_cycle))
    )
    assert q011mw._protocol_globals_are_restored()
    json.dumps(q011mw_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011mw result is not sealed")
def test_q011mw_study_metadata_and_optional_artifact_are_scoped(
    q011mw_study: dict[str, Any],
) -> None:
    assert q011mw_study["schema_version"] == 1
    assert q011mw_study["source"] == source_metadata()
    assert q011mw_study["study_gate"] == "passed"
    assert q011mw_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011mw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 4_136
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011mw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 140
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011mw_study, allow_nan=False)

    runner_path = Path(q011mw.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011mw_degree34_one_hundred_forty_first_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011mw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011mw_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011mw.q011b._canonical_json_sha256(q011mw._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
