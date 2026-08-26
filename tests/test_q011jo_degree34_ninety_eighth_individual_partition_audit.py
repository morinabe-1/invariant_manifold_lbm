from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011jo_degree34_ninety_eighth_individual_partition_audit as q011jo
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "13eaca3f83634e5a2746fe70929a4fca0bab58b3e775efaaaeda96033a3ecb83"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "dbd62d41bf8ceaca792557bf1ed1c7fd5ef87b124ab457d0bbca464c27e814fd"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "03adb44cb15536f3616d2c228f7ce8806f0df93f4627193cd764340af285bb4b",
    "partition_input_digest_sha256": (
        "e586e423c2a77fba39f44e08e25406861fc5fdba2a15c2bd746fbd7459bd14b3"
    ),
    "allocation_audit_digest_sha256": (
        "d96108b27edc9580756c1537d6a34128bc09af519bb6c7105085cdf4b66ad2ed"
    ),
    "result_digest_sha256": "bbed89c75d55b7b18ae2b3610b82be605c653e4d63d0dfacbfcf5085341e5aca",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "f3c8bda99cfd6857026bb872bdf2b5e876cb0766c813eb2a02140b3a8ef9c7e3"
    ),
    "parent_center_product_interval_digest_sha256": (
        "7ec3d67d34225c0392af92bf4240d46004297634564a9bc883b1015d4eb8b30a"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "54d05d04894583a9fb1b91c5ea06be8dde849c377a360cd2f13d1efdf53f1bbb"
    ),
    "allocation_classification_record_digest_sha256": (
        "a47f5155b2431c40ea208ffb3648bf97444b3cf1a9b4cb27def8a29a8a58a6d4"
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
def q011jo_structure() -> dict[str, Any]:
    sealed, artifacts = q011jo._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011jo._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011jo_study() -> dict[str, Any]:
    return q011jo.run_q011jo_study()


@pytest.fixture(scope="module")
def q011jo_cycle(q011jo_study: dict[str, Any]) -> dict[str, Any]:
    return q011jo_study["cycle"]


def test_q011jo_seals_q011jn_and_all_prior_inputs(
    q011jo_structure: dict[str, Any],
) -> None:
    sealed = q011jo_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 253
    assert sealed["direct_digest_count"] == 1_151
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011jn"]["digests"]) == q011jo.Q011JN_DIGESTS
    assert sealed["q011jn"]["artifact_sha256"] == q011jo.Q011JN_ARTIFACT_SHA256
    assert sealed["q011jn"]["runner_sha256"] == q011jo.Q011JN_RUNNER_SHA256
    assert sealed["q011jn"]["resolved_witness_digest_sha256"] == (
        q011jo.EXPECTED_ORDINAL_NINETY_SIX_RESOLUTION_DIGEST
    )


def test_q011jo_selects_exactly_flatten_ordinal_ninety_seven(
    q011jo_structure: dict[str, Any],
) -> None:
    fixed = q011jo_structure["fixed"]
    selection = fixed["ninety_eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 97
    assert selection["selected_left_index"] == 12
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(97))
    assert selection["ordinal_ninety_six_resolution_digest_sha256"] == (
        q011jo.EXPECTED_ORDINAL_NINETY_SIX_RESOLUTION_DIGEST
    )
    parent = selection["ninety_eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 2_906
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011jo.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011jo.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011jo.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011jo_reconstructs_registered_partition_and_inventory(
    q011jo_structure: dict[str, Any],
) -> None:
    fixed = q011jo_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [2, 7], [5], [1, 6]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 2, 7, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011jo.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011jo.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 52_416
    assert fixed["full_allocation_digest_sha256"] == q011jo.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_906
    assert q011jo_structure["compatible_count"] == 2_906
    assert fixed["compatible_allocation_digest_sha256"] == q011jo.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [
        0,
        1,
        0,
        12,
        0,
        2,
        0,
        7,
        0,
        5,
        0,
        1,
        5,
        1,
    ]
    assert fixed["last_compatible_counts"] == [
        1,
        0,
        12,
        0,
        2,
        0,
        7,
        0,
        0,
        5,
        0,
        1,
        0,
        6,
    ]
    assert fixed["parent_witness_allocation_index"] == 52_332
    assert fixed["parent_witness_compatible_index"] == 2_905
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jo result is not sealed")
def test_q011jo_classifies_every_registered_exact_interval(
    q011jo_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011jo_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_906
    records = partition["allocation_classification_records"]
    assert len(records) == 2_906
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_906))
    assert sum(partition["exact_relation_counts"].values()) == 2_906
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_906
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jo result is not sealed")
def test_q011jo_applies_registered_stopping_rule(
    q011jo_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011jo_cycle["study_validity"] == "passed"
    assert q011jo_cycle["failed_validity_order"] == []
    assert q011jo_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011jo_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011jo_cycle["diagnostic_gates"].values())
    assert q011jo_cycle["scientific_outcome"] == "not_evaluated"
    assert q011jo_cycle["actual_resonance_outcome"] == "not_established"
    assert q011jo_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011jo.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011jo.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011jo.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011jo_cycle["diagnostic_classification"] == expected
    assert not q011jo_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011jo_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninety_eighth_q011cb_witness"],
        theorem["ninety_eighth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_ninety_eighth_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jo result is not sealed")
def test_q011jo_preserves_boundary_and_reproducible_digests(
    q011jo_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011jo_cycle["theorem_consequence"]
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
    assert "flatten ordinal 97" in q011jo_cycle["claim_boundary"]
    assert "ordinals 0 through 96" in q011jo_cycle["claim_boundary"]
    assert "later 44702 Q011cb refined signatures" in q011jo_cycle["claim_boundary"]
    assert "Q011jp" in q011jo_cycle["next_change"]
    assert {name: q011jo_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011jo_cycle["result_digest_sha256"] == (
        q011jo.q011b._canonical_json_sha256(q011jo._result_digest_sections(q011jo_cycle))
    )
    assert q011jo._protocol_globals_are_restored()
    json.dumps(q011jo_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011jo result is not sealed")
def test_q011jo_study_metadata_and_optional_artifact_are_scoped(
    q011jo_study: dict[str, Any],
) -> None:
    assert q011jo_study["schema_version"] == 1
    assert q011jo_study["source"] == source_metadata()
    assert q011jo_study["study_gate"] == "passed"
    assert q011jo_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011jo_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_906
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011jo_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 97
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011jo_study, allow_nan=False)

    runner_path = Path(q011jo.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011jo_degree34_ninety_eighth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011jo artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011jo_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011jo.q011b._canonical_json_sha256(q011jo._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
