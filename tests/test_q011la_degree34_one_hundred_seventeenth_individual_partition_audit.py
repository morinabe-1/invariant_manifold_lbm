from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011la_degree34_one_hundred_seventeenth_individual_partition_audit as q011la
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "0011915d47e5652e482f996aa754ded7c094ff75f59ef9e3912940e10ce71489"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "a52b6864ca4c91481543ebdbb315bbbe015256439fd25a9d46e85f92b444cba2"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "49da674e72abf0bbfb069bce562bfe2fa67f44dd32b82e64e8c8c4dae7cabcb8",
    "partition_input_digest_sha256": (
        "2c42c549cd70d683dd26be889f94333d2e03dc908495eb737e6c9cccf4975a74"
    ),
    "allocation_audit_digest_sha256": (
        "4b3ece7b29c1721f6a23a604bd533272b665ab957b2bf7917a3fa0cc710d97b5"
    ),
    "result_digest_sha256": "5002d8a0905044663fe5ecb5146100fdf5a7db3746308e546892f9151d6670d9",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "d61f96482e98a389f88f3c73cfd6a6e74c7625e14f89e6f9698401f7c5780f75"
    ),
    "parent_center_product_interval_digest_sha256": (
        "c868e8338e03546fd5860778fc97ec6699af928685db4f2bddc0ab98603ec609"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "ac75f2f42349ced87c22b5569d7ad3f4cd91fe99110ab86845b99ca5f1138372"
    ),
    "allocation_classification_record_digest_sha256": (
        "586064316256e4b37ec088181bc06e0d35822bf1420ba4235d2fef259e3bc482"
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
def q011la_structure() -> dict[str, Any]:
    sealed, artifacts = q011la._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011la._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011la_study() -> dict[str, Any]:
    return q011la.run_q011la_study()


@pytest.fixture(scope="module")
def q011la_cycle(q011la_study: dict[str, Any]) -> dict[str, Any]:
    return q011la_study["cycle"]


def test_q011la_seals_q011kz_and_all_prior_inputs(
    q011la_structure: dict[str, Any],
) -> None:
    sealed = q011la_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 291
    assert sealed["direct_digest_count"] == 1_322
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011kz"]["digests"]) == q011la.Q011KZ_DIGESTS
    assert sealed["q011kz"]["artifact_sha256"] == q011la.Q011KZ_ARTIFACT_SHA256
    assert sealed["q011kz"]["runner_sha256"] == q011la.Q011KZ_RUNNER_SHA256
    assert sealed["q011kz"]["resolved_witness_digest_sha256"] == (
        q011la.EXPECTED_ORDINAL_ONE_HUNDRED_FIFTEEN_RESOLUTION_DIGEST
    )


def test_q011la_selects_exactly_flatten_ordinal_one_hundred_sixteen(
    q011la_structure: dict[str, Any],
) -> None:
    fixed = q011la_structure["fixed"]
    selection = fixed["one_hundred_seventeenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 116
    assert selection["selected_left_index"] == 14
    assert selection["selected_right_index"] == 4
    assert selection["previous_phase_resolved_ordinals"] == list(range(116))
    assert selection["ordinal_one_hundred_fifteen_resolution_digest_sha256"] == (
        q011la.EXPECTED_ORDINAL_ONE_HUNDRED_FIFTEEN_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_seventeenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [4, 5], [5], [4, 3]]
    assert parent["wave_multiplicity"] == 5_174
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011la.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011la.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011la.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011la_reconstructs_registered_partition_and_inventory(
    q011la_structure: dict[str, Any],
) -> None:
    fixed = q011la_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [4, 5], [5], [4, 3]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 4, 5, 5, 4, 3]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011la.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011la.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 93_600
    assert fixed["full_allocation_digest_sha256"] == q011la.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 5_174
    assert q011la_structure["compatible_count"] == 5_174
    assert fixed["compatible_allocation_digest_sha256"] == q011la.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 4, 0, 5, 0, 5, 2, 2, 3, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 4, 0, 5, 0, 0, 5, 0, 4, 0, 3]
    assert fixed["parent_witness_allocation_index"] == 93_480
    assert fixed["parent_witness_compatible_index"] == 5_173
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011la result is not sealed")
def test_q011la_classifies_every_registered_exact_interval(
    q011la_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011la_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 5_174
    records = partition["allocation_classification_records"]
    assert len(records) == 5_174
    assert [record["compatible_allocation_index"] for record in records] == list(range(5_174))
    assert sum(partition["exact_relation_counts"].values()) == 5_174
    assert sum(partition["binary64_outward_relation_counts"].values()) == 5_174
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011la result is not sealed")
def test_q011la_applies_registered_stopping_rule(
    q011la_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011la_cycle["study_validity"] == "passed"
    assert q011la_cycle["failed_validity_order"] == []
    assert q011la_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011la_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011la_cycle["diagnostic_gates"].values())
    assert q011la_cycle["scientific_outcome"] == "not_evaluated"
    assert q011la_cycle["actual_resonance_outcome"] == "not_established"
    assert q011la_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011la.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011la.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011la.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011la_cycle["diagnostic_classification"] == expected
    assert not q011la_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011la_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_seventeenth_q011cb_witness"
        ],
        theorem["one_hundred_seventeenth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_seventeenth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011la result is not sealed")
def test_q011la_preserves_boundary_and_reproducible_digests(
    q011la_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011la_cycle["theorem_consequence"]
    assert theorem["q011kz_ordinal_one_hundred_fifteen_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 116" in q011la_cycle["claim_boundary"]
    assert "ordinals 0 through 115" in q011la_cycle["claim_boundary"]
    assert "later 44683 Q011cb refined signatures" in q011la_cycle["claim_boundary"]
    assert "Q011lb" in q011la_cycle["next_change"]
    assert {name: q011la_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011la_cycle["result_digest_sha256"] == (
        q011la.q011b._canonical_json_sha256(q011la._result_digest_sections(q011la_cycle))
    )
    assert q011la._protocol_globals_are_restored()
    json.dumps(q011la_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011la result is not sealed")
def test_q011la_study_metadata_and_optional_artifact_are_scoped(
    q011la_study: dict[str, Any],
) -> None:
    assert q011la_study["schema_version"] == 1
    assert q011la_study["source"] == source_metadata()
    assert q011la_study["study_gate"] == "passed"
    assert q011la_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011la_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 5_174
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011la_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 116
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011la_study, allow_nan=False)

    runner_path = Path(q011la.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011la_degree34_one_hundred_seventeenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011la artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011la_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011la.q011b._canonical_json_sha256(q011la._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
