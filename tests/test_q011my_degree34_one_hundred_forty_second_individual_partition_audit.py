from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011my_degree34_one_hundred_forty_second_individual_partition_audit as q011my
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "1f647a3540422cc79b661b5a0742b886495569150f590c12349417cf1cccd309"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "6547b9c5f768bf417475e536be710ef4944d2bf4dc59d29b6cbd50433943cd47"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "1f6388f2cf9464415c66a4e790bb3a3203f8969ebc7a4c59d052f2aaea7391f6",
    "partition_input_digest_sha256": (
        "c4339c946932b961ab577e925e147c7b8e938efe274949a93a38f74d3f9e0a46"
    ),
    "allocation_audit_digest_sha256": (
        "6f77918b468c81cd43ff5522b1812f7923ed03942883ecc094915050100bddfb"
    ),
    "result_digest_sha256": "6015bee7c6f0b09e4d3cfee26b05f2332374c4016b7765e3fb175fb7efef5d74",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "0d6d6b787b1b8ab8fb2c7ffefbec0a65cbc7511fc9e9f19a437493f534911db1"
    ),
    "parent_center_product_interval_digest_sha256": (
        "f3b5d66ea0cab421e8294a0e15528c7e140b85e1306b5c22fb3f0b39cdde7ca3"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "4b2f1e93743ec82451accdbec4f6e89f66a347d925c6ad8ce850d932f22b3d0d"
    ),
    "allocation_classification_record_digest_sha256": (
        "3cbb6c04b9d2f92e4c9d2304f6b04b827f2c3f7b8e0e7b847d61df1808a4197b"
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
def q011my_structure() -> dict[str, Any]:
    sealed, artifacts = q011my._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011my._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011my_study() -> dict[str, Any]:
    return q011my.run_q011my_study()


@pytest.fixture(scope="module")
def q011my_cycle(q011my_study: dict[str, Any]) -> dict[str, Any]:
    return q011my_study["cycle"]


def test_q011my_seals_q011mx_and_all_prior_inputs(
    q011my_structure: dict[str, Any],
) -> None:
    sealed = q011my_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 341
    assert sealed["direct_digest_count"] == 1_547
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011mx"]["digests"]) == q011my.Q011MX_DIGESTS
    assert sealed["q011mx"]["artifact_sha256"] == q011my.Q011MX_ARTIFACT_SHA256
    assert sealed["q011mx"]["runner_sha256"] == q011my.Q011MX_RUNNER_SHA256
    assert sealed["q011mx"]["resolved_witness_digest_sha256"] == (
        q011my.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_RESOLUTION_DIGEST
    )


def test_q011my_selects_exactly_flatten_ordinal_one_hundred_forty_one(
    q011my_structure: dict[str, Any],
) -> None:
    fixed = q011my_structure["fixed"]
    selection = fixed["one_hundred_forty_second_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 141
    assert selection["selected_left_index"] == 17
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(141))
    assert selection["ordinal_one_hundred_forty_resolution_digest_sha256"] == (
        q011my.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_forty_second_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 3_727
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011my.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011my.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011my.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011my_reconstructs_registered_partition_and_inventory(
    q011my_structure: dict[str, Any],
) -> None:
    fixed = q011my_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [5, 2]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 7, 2, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == q011my.EXPECTED_OCCUPIED_RECORD_DIGEST
    assert tuple(fixed["singleton_identifier_order"]) == q011my.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 67_392
    assert fixed["full_allocation_digest_sha256"] == q011my.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 3_727
    assert q011my_structure["compatible_count"] == 3_727
    assert fixed["compatible_allocation_digest_sha256"] == q011my.EXPECTED_COMPATIBLE_DIGEST
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
        3,
        2,
        2,
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
        5,
        0,
        2,
    ]
    assert fixed["parent_witness_allocation_index"] == 67_284
    assert fixed["parent_witness_compatible_index"] == 3_726
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011my result is not sealed")
def test_q011my_classifies_every_registered_exact_interval(
    q011my_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011my_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 3_727
    records = partition["allocation_classification_records"]
    assert len(records) == 3_727
    assert [record["compatible_allocation_index"] for record in records] == list(range(3_727))
    assert sum(partition["exact_relation_counts"].values()) == 3_727
    assert sum(partition["binary64_outward_relation_counts"].values()) == 3_727
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011my result is not sealed")
def test_q011my_applies_registered_stopping_rule(
    q011my_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011my_cycle["study_validity"] == "passed"
    assert q011my_cycle["failed_validity_order"] == []
    assert q011my_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011my_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011my_cycle["diagnostic_gates"].values())
    assert q011my_cycle["scientific_outcome"] == "not_evaluated"
    assert q011my_cycle["actual_resonance_outcome"] == "not_established"
    assert q011my_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011my.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011my.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011my.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011my_cycle["diagnostic_classification"] == expected
    assert not q011my_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011my_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_forty_second_q011cb_witness"
        ],
        theorem["one_hundred_forty_second_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_forty_second_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011my result is not sealed")
def test_q011my_preserves_boundary_and_reproducible_digests(
    q011my_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011my_cycle["theorem_consequence"]
    assert theorem["q011mx_ordinal_one_hundred_forty_phase_resolution_is_preserved"]
    assert theorem["q011mw_ordinal_one_hundred_forty_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 141" in q011my_cycle["claim_boundary"]
    assert "ordinals 0 through 140" in q011my_cycle["claim_boundary"]
    assert "later 44658 Q011cb refined signatures" in q011my_cycle["claim_boundary"]
    assert "Q011mz" in q011my_cycle["next_change"]
    assert {name: q011my_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011my_cycle["result_digest_sha256"] == (
        q011my.q011b._canonical_json_sha256(q011my._result_digest_sections(q011my_cycle))
    )
    assert q011my._protocol_globals_are_restored()
    json.dumps(q011my_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011my result is not sealed")
def test_q011my_study_metadata_and_optional_artifact_are_scoped(
    q011my_study: dict[str, Any],
) -> None:
    assert q011my_study["schema_version"] == 1
    assert q011my_study["source"] == source_metadata()
    assert q011my_study["study_gate"] == "passed"
    assert q011my_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011my_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 3_727
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011my_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 141
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011my_study, allow_nan=False)

    runner_path = Path(q011my.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011my_degree34_one_hundred_forty_second_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011my artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011my_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011my.q011b._canonical_json_sha256(q011my._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
