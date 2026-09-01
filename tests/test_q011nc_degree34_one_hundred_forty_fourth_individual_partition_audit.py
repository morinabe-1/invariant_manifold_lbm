from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011nc_degree34_one_hundred_forty_fourth_individual_partition_audit as q011nc
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "80db0141e28cbd3c9505492b6308799e01df5e35fbfe721abedbe9ad99ac977e"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "2916eef4fbb78f6dffe5c5189023b54e27c8e93c90036142e71f1a2227469aeb"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "f7205a5ce7ec5abb5f23f52813eda4ad75c5bf715e0865e2692f90490025cd04",
    "partition_input_digest_sha256": (
        "2fc7595c74b4b8d05f033e507d0145161abb37be6df976b1782d2cec670c9f8e"
    ),
    "allocation_audit_digest_sha256": (
        "3de4c3c1652c6e8bea9137ce23c019d61bd6dc7df4d458af1d4d42526ff4fb80"
    ),
    "result_digest_sha256": "22cfee445dd217c7e0e6cba13475def33200982c4d0a27ac56e147cbe3d26811",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "8cac361587f274489eda6f25cbe50e48c2a6d1a6f7b8376e89951754d258f59d"
    ),
    "parent_center_product_interval_digest_sha256": (
        "899745fbf92a682e7ecea24114cd8bc9bc71bd202f2d0cd4266cc34f4913bd11"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "0944367ccfef97e7548c7dd30e9abf86f510af3fb1d5df7d6c5212ddd934cc6b"
    ),
    "allocation_classification_record_digest_sha256": (
        "2dd8dc7b6b0f3a302532c2119b5455df0def114f7bedf29581d6f184d5dfbae4"
    ),
    "allocation_classification_stream_digest_sha256": (
        "8205bed0d4fe324087e12288801f675e41d770ab8f061cb86304f3e709a47b21"
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
def q011nc_structure() -> dict[str, Any]:
    sealed, artifacts = q011nc._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011nc._fixed_individual_input_audit(
        artifacts
    )
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011nc_study() -> dict[str, Any]:
    return q011nc.run_q011nc_study()


@pytest.fixture(scope="module")
def q011nc_cycle(q011nc_study: dict[str, Any]) -> dict[str, Any]:
    return q011nc_study["cycle"]


def test_q011nc_seals_q011nb_and_all_prior_inputs(
    q011nc_structure: dict[str, Any],
) -> None:
    sealed = q011nc_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 345
    assert sealed["direct_digest_count"] == 1_565
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011nb"]["digests"]) == q011nc.Q011NB_DIGESTS
    assert sealed["q011nb"]["artifact_sha256"] == q011nc.Q011NB_ARTIFACT_SHA256
    assert sealed["q011nb"]["runner_sha256"] == q011nc.Q011NB_RUNNER_SHA256
    assert sealed["q011nb"]["resolved_witness_digest_sha256"] == (
        q011nc.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_TWO_RESOLUTION_DIGEST
    )
    repeated, repeated_artifacts = q011nc._sealed_input_audit()
    parent, parent_artifacts = q011nc.q011nb._sealed_input_audit()
    assert repeated["passed"] and repeated["artifact_count"] == 345
    assert len(repeated_artifacts) == 345
    assert parent["passed"] and parent["artifact_count"] == 344
    assert len(parent_artifacts) == 344


def test_q011nc_selects_exactly_flatten_ordinal_one_hundred_forty_three(
    q011nc_structure: dict[str, Any],
) -> None:
    fixed = q011nc_structure["fixed"]
    selection = fixed["one_hundred_forty_fourth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 143
    assert selection["selected_left_index"] == 17
    assert selection["selected_right_index"] == 7
    assert selection["previous_phase_resolved_ordinals"] == list(range(143))
    assert selection["ordinal_one_hundred_forty_two_resolution_digest_sha256"] == (
        q011nc.EXPECTED_ORDINAL_ONE_HUNDRED_FORTY_TWO_RESOLUTION_DIGEST
    )
    parent = selection["one_hundred_forty_fourth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [7, 0]]
    assert parent["wave_multiplicity"] == 1_667
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011nc.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011nc.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011nc.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011nc_reconstructs_registered_partition_and_inventory(
    q011nc_structure: dict[str, Any],
) -> None:
    fixed = q011nc_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [7, 2], [5], [7, 0]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 7, 2, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert (
        fixed["occupied_class_record_digest_sha256"]
        == q011nc.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011nc.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 29_952
    assert fixed["full_allocation_digest_sha256"] == q011nc.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_667
    assert q011nc_structure["compatible_count"] == 1_667
    assert (
        fixed["compatible_allocation_digest_sha256"]
        == q011nc.EXPECTED_COMPATIBLE_DIGEST
    )
    assert tuple(fixed["first_compatible_counts"]) == (
        q011nc.EXPECTED_FIRST_COMPATIBLE_COUNTS
    )
    assert tuple(fixed["last_compatible_counts"]) == q011nc.EXPECTED_SOURCE_COUNTS
    assert fixed["parent_witness_allocation_index"] == 29_904
    assert fixed["parent_witness_compatible_index"] == 1_666
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]
    assert q011nc._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nc result is not sealed")
def test_q011nc_classifies_every_registered_exact_interval_once(
    q011nc_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_PARTITION_DIGESTS is not None
    partition = q011nc_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_667
    assert partition["registered_class_totals"] == [1, 12, 7, 2, 5, 7]
    assert partition["all_compatible_allocations_preserve_registered_class_totals"]
    assert partition["exact_product_evaluation_count"] == 1
    assert partition[
        "exact_product_evaluation_reused_only_after_equal_interval_and_class_total_proofs"
    ]
    records = partition["allocation_classification_records"]
    assert len(records) == 1_667
    assert [record["compatible_allocation_index"] for record in records] == list(
        range(1_667)
    )
    assert all(
        record["class_totals"] == [1, 12, 7, 2, 5, 7] for record in records
    )
    assert sum(partition["exact_relation_counts"].values()) == 1_667
    assert sum(partition["binary64_outward_relation_counts"].values()) == 1_667
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nc result is not sealed")
def test_q011nc_applies_registered_stopping_rule(
    q011nc_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_REFINEMENT_OUTCOME is not None
    assert q011nc_cycle["study_validity"] == "passed"
    assert q011nc_cycle["failed_validity_order"] == []
    assert q011nc_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011nc_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011nc_cycle["diagnostic_gates"].values())
    assert q011nc_cycle["scientific_outcome"] == "not_evaluated"
    assert q011nc_cycle["actual_resonance_outcome"] == "not_established"
    assert q011nc_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011nc.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011nc.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011nc.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011nc_cycle["diagnostic_classification"] == expected
    assert not q011nc_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011nc_cycle["theorem_consequence"]
    flags = (
        theorem[
            "individual_partition_is_interval_inert_for_one_hundred_forty_fourth_q011cb_witness"
        ],
        theorem[
            "one_hundred_forty_fourth_q011cb_witness_is_resolved_by_individual_partition"
        ],
        theorem[
            "individual_partition_changes_intervals_but_one_hundred_forty_fourth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nc result is not sealed")
def test_q011nc_preserves_boundary_and_reproducible_digests(
    q011nc_cycle: dict[str, Any],
) -> None:
    assert EXPECTED_SECTION_DIGESTS is not None
    theorem = q011nc_cycle["theorem_consequence"]
    assert theorem["q011nb_ordinal_one_hundred_forty_two_phase_resolution_is_preserved"]
    assert theorem["q011na_ordinal_one_hundred_forty_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011my_ordinal_one_hundred_forty_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011mx_ordinal_one_hundred_forty_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 143" in q011nc_cycle["claim_boundary"]
    assert "ordinals 0 through 142" in q011nc_cycle["claim_boundary"]
    assert "later 44656 Q011cb refined signatures" in q011nc_cycle["claim_boundary"]
    assert "Q011nd" in q011nc_cycle["next_change"]
    assert {name: q011nc_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011nc_cycle["result_digest_sha256"] == (
        q011nc.q011b._canonical_json_sha256(
            q011nc._result_digest_sections(q011nc_cycle)
        )
    )
    assert q011nc._protocol_globals_are_restored()
    json.dumps(q011nc_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011nc result is not sealed")
def test_q011nc_study_metadata_and_optional_artifact_are_scoped(
    q011nc_study: dict[str, Any],
) -> None:
    assert q011nc_study["schema_version"] == 1
    assert q011nc_study["source"] == source_metadata()
    assert q011nc_study["study_gate"] == "passed"
    assert q011nc_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011nc_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_667
    assert runtime["exact_product_evaluations"] == 1
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011nc_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 143
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011nc_study, allow_nan=False)

    runner_path = Path(q011nc.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011nc_degree34_one_hundred_forty_fourth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011nc artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011nc_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011nc.q011b._canonical_json_sha256(
            q011nc._result_digest_sections(artifact["cycle"])
        )
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
