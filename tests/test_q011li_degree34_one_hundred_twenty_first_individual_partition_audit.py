from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011li_degree34_one_hundred_twenty_first_individual_partition_audit as q011li
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "d473e3d8eb578042f195ba48904b0fd8105d13a3264c08da361dca0d45df3e42"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "bd1a52fbb6b71a679a5919d9a2222827eb2818a85ce8e0be0cb8695aacf2c61d"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "6f7ec15b93687b3b4bc546b6a0317e5a9d2136d129238cc826e0ed3042409eb9",
    "partition_input_digest_sha256": (
        "e0ac99819fe2a37160024473eb0886eb7e2c6afeb30f8c60dfce0e6b5c09b221"
    ),
    "allocation_audit_digest_sha256": (
        "f702ca7d2f92000f2a677b336cc760ea32fbc1b82541e198b1d2e0eaa0bbf971"
    ),
    "result_digest_sha256": "249e60478ce186925e2a1cf69d8d948a75bff2c652dffa681658cede7e132de7",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "cbef9410d289289fef503429766ec5c49c5aadf001d4522a5851fde52550fd5b"
    ),
    "parent_center_product_interval_digest_sha256": (
        "44e0bd7c370aad39356bae85720a82d6516de457a1be81844ff0b1dc00d0a098"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "45bd8185d9c7cd686c9224886a5a82a6f04365ff105097d7dc3f43fd963d41fb"
    ),
    "allocation_classification_record_digest_sha256": (
        "213263f2f8a4f9918f65e51387d12c8199a2f953a617ca82b0139f7a23103f52"
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
def q011li_structure() -> dict[str, Any]:
    sealed, artifacts = q011li._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011li._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011li_study() -> dict[str, Any]:
    return q011li.run_q011li_study()


@pytest.fixture(scope="module")
def q011li_cycle(q011li_study: dict[str, Any]) -> dict[str, Any]:
    return q011li_study["cycle"]


def test_q011li_seals_q011lh_and_all_prior_inputs(
    q011li_structure: dict[str, Any],
) -> None:
    sealed = q011li_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 299
    assert sealed["direct_digest_count"] == 1_358
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011lh"]["digests"]) == q011li.Q011LH_DIGESTS
    assert sealed["q011lh"]["artifact_sha256"] == q011li.Q011LH_ARTIFACT_SHA256
    assert sealed["q011lh"]["runner_sha256"] == q011li.Q011LH_RUNNER_SHA256
    assert sealed["q011lh"]["resolved_witness_digest_sha256"] == (
        q011li.EXPECTED_ORDINAL_ONE_HUNDRED_NINETEEN_RESOLUTION_DIGEST
    )


def test_q011li_selects_exactly_flatten_ordinal_one_hundred_twenty(
    q011li_structure: dict[str, Any],
) -> None:
    fixed = q011li_structure["fixed"]
    selection = fixed["one_hundred_twenty_first_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 120
    assert selection["selected_left_index"] == 15
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(120))
    assert selection["ordinal_one_hundred_nineteen_resolution_digest_sha256"] == (
        q011li.EXPECTED_ORDINAL_ONE_HUNDRED_NINETEEN_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_twenty_first_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [5, 4], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 2_076
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011li.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011li.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011li.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011li_reconstructs_registered_partition_and_inventory(
    q011li_structure: dict[str, Any],
) -> None:
    fixed = q011li_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [5, 4], [5], [0, 7]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 5, 4, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011li.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011li.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 37_440
    assert fixed["full_allocation_digest_sha256"] == q011li.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_076
    assert q011li_structure["compatible_count"] == 2_076
    assert fixed["compatible_allocation_digest_sha256"] == q011li.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 5, 0, 4, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 5, 0, 4, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 37_392
    assert fixed["parent_witness_compatible_index"] == 2_075
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011li result is not sealed")
def test_q011li_classifies_every_registered_exact_interval(
    q011li_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011li_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_076
    records = partition["allocation_classification_records"]
    assert len(records) == 2_076
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_076))
    assert sum(partition["exact_relation_counts"].values()) == 2_076
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_076
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011li result is not sealed")
def test_q011li_applies_registered_stopping_rule(
    q011li_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011li_cycle["study_validity"] == "passed"
    assert q011li_cycle["failed_validity_order"] == []
    assert q011li_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011li_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011li_cycle["diagnostic_gates"].values())
    assert q011li_cycle["scientific_outcome"] == "not_evaluated"
    assert q011li_cycle["actual_resonance_outcome"] == "not_established"
    assert q011li_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011li.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011li.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011li.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011li_cycle["diagnostic_classification"] == expected
    assert not q011li_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011li_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_twenty_first_q011cb_witness"
        ],
        theorem["one_hundred_twenty_first_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_twenty_first_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011li result is not sealed")
def test_q011li_preserves_boundary_and_reproducible_digests(
    q011li_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011li_cycle["theorem_consequence"]
    assert theorem["q011lh_ordinal_one_hundred_nineteen_phase_resolution_is_preserved"]
    assert theorem["q011lg_ordinal_one_hundred_nineteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011le_ordinal_one_hundred_eighteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011lc_ordinal_one_hundred_seventeen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ku_ordinal_one_hundred_thirteen_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kq_ordinal_one_hundred_eleven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011km_ordinal_one_hundred_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kj_ordinal_one_hundred_seven_phase_resolution_is_preserved"]
    assert theorem["q011ke_ordinal_one_hundred_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kd_ordinal_one_hundred_four_phase_resolution_is_preserved"]
    assert theorem["q011kc_ordinal_one_hundred_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011kb_ordinal_one_hundred_three_phase_resolution_is_preserved"]
    assert theorem["q011jw_ordinal_one_hundred_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ju_ordinal_one_hundred_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011js_ordinal_ninety_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jq_ordinal_ninety_eight_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jp_ordinal_ninety_seven_phase_resolution_is_preserved"]
    assert theorem["q011jo_ordinal_ninety_seven_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jn_ordinal_ninety_six_phase_resolution_is_preserved"]
    assert theorem["q011jm_ordinal_ninety_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jl_ordinal_ninety_five_phase_resolution_is_preserved"]
    assert theorem["q011jk_ordinal_ninety_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jj_ordinal_ninety_four_phase_resolution_is_preserved"]
    assert theorem["q011ji_ordinal_ninety_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jh_ordinal_ninety_three_phase_resolution_is_preserved"]
    assert theorem["q011jg_ordinal_ninety_three_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jf_ordinal_ninety_two_phase_resolution_is_preserved"]
    assert theorem["q011je_ordinal_ninety_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jd_ordinal_ninety_one_phase_resolution_is_preserved"]
    assert theorem["q011jc_ordinal_ninety_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011jb_ordinal_ninety_phase_resolution_is_preserved"]
    assert theorem["q011ja_ordinal_ninety_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011iz_ordinal_eighty_nine_phase_resolution_is_preserved"]
    assert theorem["q011iy_ordinal_eighty_nine_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011ix_ordinal_eighty_eight_phase_resolution_is_preserved"]
    assert theorem["q011iw_ordinal_eighty_eight_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 120" in q011li_cycle["claim_boundary"]
    assert "ordinals 0 through 119" in q011li_cycle["claim_boundary"]
    assert "later 44679 Q011cb refined signatures" in q011li_cycle["claim_boundary"]
    assert "Q011lj" in q011li_cycle["next_change"]
    assert {name: q011li_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011li_cycle["result_digest_sha256"] == (
        q011li.q011b._canonical_json_sha256(q011li._result_digest_sections(q011li_cycle))
    )
    assert q011li._protocol_globals_are_restored()
    json.dumps(q011li_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011li result is not sealed")
def test_q011li_study_metadata_and_optional_artifact_are_scoped(
    q011li_study: dict[str, Any],
) -> None:
    assert q011li_study["schema_version"] == 1
    assert q011li_study["source"] == source_metadata()
    assert q011li_study["study_gate"] == "passed"
    assert q011li_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011li_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_076
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011li_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 120
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011li_study, allow_nan=False)

    runner_path = Path(q011li.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011li_degree34_one_hundred_twenty_first_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011li artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011li_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011li.q011b._canonical_json_sha256(q011li._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
