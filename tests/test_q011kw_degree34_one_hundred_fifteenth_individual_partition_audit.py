from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011kw_degree34_one_hundred_fifteenth_individual_partition_audit as q011kw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = None
EXPECTED_ARTIFACT_SHA256: str | None = None
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = None
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = None
EXPECTED_REFINEMENT_OUTCOME: str | None = None
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
def q011kw_structure() -> dict[str, Any]:
    sealed, artifacts = q011kw._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011kw._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011kw_study() -> dict[str, Any]:
    return q011kw.run_q011kw_study()


@pytest.fixture(scope="module")
def q011kw_cycle(q011kw_study: dict[str, Any]) -> dict[str, Any]:
    return q011kw_study["cycle"]


def test_q011kw_seals_q011kv_and_all_prior_inputs(
    q011kw_structure: dict[str, Any],
) -> None:
    sealed = q011kw_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 287
    assert sealed["direct_digest_count"] == 1_304
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011kv"]["digests"]) == q011kw.Q011KV_DIGESTS
    assert sealed["q011kv"]["artifact_sha256"] == q011kw.Q011KV_ARTIFACT_SHA256
    assert sealed["q011kv"]["runner_sha256"] == q011kw.Q011KV_RUNNER_SHA256
    assert sealed["q011kv"]["resolved_witness_digest_sha256"] == (
        q011kw.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTEEN_RESOLUTION_DIGEST
    )


def test_q011kw_selects_exactly_flatten_ordinal_one_hundred_fourteen(
    q011kw_structure: dict[str, Any],
) -> None:
    fixed = q011kw_structure["fixed"]
    selection = fixed["one_hundred_fifteenth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 114
    assert selection["selected_left_index"] == 14
    assert selection["selected_right_index"] == 2
    assert selection["previous_phase_resolved_ordinals"] == list(range(114))
    assert selection["ordinal_one_hundred_thirteen_resolution_digest_sha256"] == (
        q011kw.EXPECTED_ORDINAL_ONE_HUNDRED_THIRTEEN_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_fifteenth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [4, 5], [5], [2, 5]]
    assert parent["wave_multiplicity"] == 4_658
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011kw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011kw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011kw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011kw_reconstructs_registered_partition_and_inventory(
    q011kw_structure: dict[str, Any],
) -> None:
    fixed = q011kw_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [4, 5], [5], [2, 5]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 4, 5, 5, 2, 5]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011kw.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011kw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 84_240
    assert fixed["full_allocation_digest_sha256"] == q011kw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 4_658
    assert q011kw_structure["compatible_count"] == 4_658
    assert fixed["compatible_allocation_digest_sha256"] == q011kw.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 4, 0, 5, 0, 5, 0, 2, 5, 0]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 4, 0, 5, 0, 0, 5, 0, 2, 0, 5]
    assert fixed["parent_witness_allocation_index"] == 84_132
    assert fixed["parent_witness_compatible_index"] == 4_657
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kw result is not sealed")
def test_q011kw_classifies_every_registered_exact_interval(
    q011kw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011kw_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 4_658
    records = partition["allocation_classification_records"]
    assert len(records) == 4_658
    assert [record["compatible_allocation_index"] for record in records] == list(range(4_658))
    assert sum(partition["exact_relation_counts"].values()) == 4_658
    assert sum(partition["binary64_outward_relation_counts"].values()) == 4_658
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kw result is not sealed")
def test_q011kw_applies_registered_stopping_rule(
    q011kw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011kw_cycle["study_validity"] == "passed"
    assert q011kw_cycle["failed_validity_order"] == []
    assert q011kw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011kw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011kw_cycle["diagnostic_gates"].values())
    assert q011kw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011kw_cycle["actual_resonance_outcome"] == "not_established"
    assert q011kw_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011kw.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011kw.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011kw.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011kw_cycle["diagnostic_classification"] == expected
    assert not q011kw_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011kw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_one_hundred_fifteenth_q011cb_witness"],
        theorem["one_hundred_fifteenth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_fifteenth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kw result is not sealed")
def test_q011kw_preserves_boundary_and_reproducible_digests(
    q011kw_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011kw_cycle["theorem_consequence"]
    assert theorem["q011kv_ordinal_one_hundred_thirteen_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 114" in q011kw_cycle["claim_boundary"]
    assert "ordinals 0 through 113" in q011kw_cycle["claim_boundary"]
    assert "later 44685 Q011cb refined signatures" in q011kw_cycle["claim_boundary"]
    assert "Q011kx" in q011kw_cycle["next_change"]
    assert {name: q011kw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011kw_cycle["result_digest_sha256"] == (
        q011kw.q011b._canonical_json_sha256(q011kw._result_digest_sections(q011kw_cycle))
    )
    assert q011kw._protocol_globals_are_restored()
    json.dumps(q011kw_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011kw result is not sealed")
def test_q011kw_study_metadata_and_optional_artifact_are_scoped(
    q011kw_study: dict[str, Any],
) -> None:
    assert q011kw_study["schema_version"] == 1
    assert q011kw_study["source"] == source_metadata()
    assert q011kw_study["study_gate"] == "passed"
    assert q011kw_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011kw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 4_658
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011kw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 114
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011kw_study, allow_nan=False)

    runner_path = Path(q011kw.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011kw_degree34_one_hundred_fifteenth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011kw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011kw_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011kw.q011b._canonical_json_sha256(q011kw._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
