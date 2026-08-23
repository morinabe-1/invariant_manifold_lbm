from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ia_degree34_seventy_eighth_individual_partition_audit as q011ia
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "b6b35f36170330a1f2ab718dca596d13be164bec1eba5c4607163152c21b1b4c"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "d1e0d5456e813e608b8815d6fee533411590e1c2f59aa5bbd7ccb872c69fd3b3"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "2224306d8150f5f95a185eafaadb45b0823f6ab392701fb7edb7d87ef987c195",
    "partition_input_digest_sha256": (
        "07b047230a3d269ca0ee9a5a9e455ebe4dd03888ed74d369bad00c79a492a1d3"
    ),
    "allocation_audit_digest_sha256": (
        "78fdbe494132e3341dacc92da59a6c4c914c31e86f4cb399a6fe8969ed6fa6c1"
    ),
    "result_digest_sha256": "35de21afb3a0a597859b8aa911fc2b2543b0b43204fa43624448cd2fd45327c7",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "d51ddc20f6fbb322bf9ec2b7850a9f0b20ce2524781936a7dabe720f2c0f9541"
    ),
    "parent_center_product_interval_digest_sha256": (
        "f5d1badf0cf6b57025bea18b3ff16c6a25d2773400b1b3483ad71a2ca796a966"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "4085b1000706b319f8f58fe4ef371e1ea76201d8d48edd066ffa1ace02014504"
    ),
    "allocation_classification_record_digest_sha256": (
        "af16dbd59d70ca2723704f53387d77416e4a394b06546c9f3513a338d0894881"
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
def q011ia_structure() -> dict[str, Any]:
    sealed, artifacts = q011ia._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011ia._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011ia_study() -> dict[str, Any]:
    return q011ia.run_q011ia_study()


@pytest.fixture(scope="module")
def q011ia_cycle(q011ia_study: dict[str, Any]) -> dict[str, Any]:
    return q011ia_study["cycle"]


def test_q011ia_seals_q011hz_and_all_prior_inputs(q011ia_structure: dict[str, Any]) -> None:
    sealed = q011ia_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 213
    assert sealed["direct_digest_count"] == 971
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011hz"]["digests"]) == q011ia.Q011HZ_DIGESTS
    assert sealed["q011hz"]["artifact_sha256"] == q011ia.Q011HZ_ARTIFACT_SHA256
    assert sealed["q011hz"]["runner_sha256"] == q011ia.Q011HZ_RUNNER_SHA256
    assert sealed["q011hz"]["resolved_witness_digest_sha256"] == (
        q011ia.EXPECTED_ORDINAL_SEVENTY_SIX_RESOLUTION_DIGEST
    )


def test_q011ia_selects_exactly_flatten_ordinal_seventy_seven(
    q011ia_structure: dict[str, Any],
) -> None:
    fixed = q011ia_structure["fixed"]
    selection = fixed["seventy_eighth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5600, 8]
    assert selection["selected_flat_ordinal"] == 77
    assert selection["selected_left_index"] == 9
    assert selection["selected_right_index"] == 5
    assert selection["previous_phase_resolved_ordinals"] == list(range(77))
    assert selection["ordinal_seventy_six_resolution_digest_sha256"] == (
        q011ia.EXPECTED_ORDINAL_SEVENTY_SIX_RESOLUTION_DIGEST
    )
    parent = selection["seventy_eighth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [5, 2]]
    assert parent["wave_multiplicity"] == 852
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011ia.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (
        q011ia.EXPECTED_PARENT_CENTER_GAP_HEX
    )
    assert parent["witness_digest_sha256"] == q011ia.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011ia_reconstructs_registered_partition_and_inventory(
    q011ia_structure: dict[str, Any],
) -> None:
    fixed = q011ia_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 0, 13], [9, 0], [5], [5, 2]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [13, 9, 5, 5, 2]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (
        q011ia.EXPECTED_OCCUPIED_RECORD_DIGEST
    )
    assert tuple(fixed["singleton_identifier_order"]) == q011ia.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 15_120
    assert fixed["full_allocation_digest_sha256"] == q011ia.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 852
    assert q011ia_structure["compatible_count"] == 852
    assert fixed["compatible_allocation_digest_sha256"] == q011ia.EXPECTED_COMPATIBLE_DIGEST
    assert fixed["first_compatible_counts"] == [0, 13, 0, 9, 0, 5, 3, 2, 2, 0]
    assert fixed["last_compatible_counts"] == [13, 0, 9, 0, 0, 5, 0, 5, 0, 2]
    assert fixed["parent_witness_allocation_index"] == 15_012
    assert fixed["parent_witness_compatible_index"] == 851
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ia result is not sealed")
def test_q011ia_classifies_every_registered_exact_interval(q011ia_cycle: dict[str, Any]) -> None:
    partition = q011ia_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 852
    records = partition["allocation_classification_records"]
    assert len(records) == 852
    assert [record["compatible_allocation_index"] for record in records] == list(range(852))
    assert sum(partition["exact_relation_counts"].values()) == 852
    assert sum(partition["binary64_outward_relation_counts"].values()) == 852
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ia result is not sealed")
def test_q011ia_applies_the_registered_exclusive_stopping_rule(
    q011ia_cycle: dict[str, Any],
) -> None:
    assert q011ia_cycle["study_validity"] == "passed"
    assert q011ia_cycle["failed_validity_order"] == []
    assert q011ia_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011ia_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ia_cycle["diagnostic_gates"].values())
    assert q011ia_cycle["scientific_outcome"] == "not_evaluated"
    assert q011ia_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ia_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011ia.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011ia.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011ia.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011ia_cycle["diagnostic_classification"] == expected
    assert not q011ia_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011ia_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_seventy_eighth_q011cb_witness"],
        theorem["seventy_eighth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem[
            "individual_partition_changes_intervals_but_seventy_eighth_q011cb_witness_persists"
        ],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ia result is not sealed")
def test_q011ia_preserves_boundary_and_reproducible_digests(
    q011ia_cycle: dict[str, Any],
) -> None:
    theorem = q011ia_cycle["theorem_consequence"]
    assert theorem["q011hz_ordinal_seventy_six_phase_resolution_is_preserved"]
    assert theorem["q011hy_ordinal_seventy_six_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hx_ordinal_seventy_five_phase_resolution_is_preserved"]
    assert theorem["q011hw_ordinal_seventy_five_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hv_ordinal_seventy_four_phase_resolution_is_preserved"]
    assert theorem["q011hu_ordinal_seventy_four_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hr_ordinal_seventy_two_phase_resolution_is_preserved"]
    assert theorem["q011hq_ordinal_seventy_two_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hp_ordinal_seventy_one_phase_resolution_is_preserved"]
    assert theorem["q011ho_ordinal_seventy_one_interval_inert_diagnostic_is_preserved"]
    assert theorem["q011hn_ordinal_seventy_phase_resolution_is_preserved"]
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
    assert "flatten ordinal 77" in q011ia_cycle["claim_boundary"]
    assert "ordinals 0 through 76" in q011ia_cycle["claim_boundary"]
    assert "later 44722 Q011cb refined signatures" in q011ia_cycle["claim_boundary"]
    assert "Q011ib" in q011ia_cycle["next_change"]
    json.dumps(q011ia_cycle, allow_nan=False)
    assert {name: q011ia_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011ia_cycle["result_digest_sha256"] == (
        q011ia.q011b._canonical_json_sha256(q011ia._result_digest_sections(q011ia_cycle))
    )
    assert q011ia._protocol_globals_are_restored()


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011ia result is not sealed")
def test_q011ia_study_metadata_and_optional_artifact_are_scoped(
    q011ia_study: dict[str, Any],
) -> None:
    assert q011ia_study["schema_version"] == 1
    assert q011ia_study["source"] == source_metadata()
    assert q011ia_study["study_gate"] == "passed"
    assert q011ia_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011ia_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 852
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011ia_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2340
    assert scope["parent_flat_ordinal"] == 77
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011ia_study, allow_nan=False)

    runner_path = Path(q011ia.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011ia_degree34_seventy_eighth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ia artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011ia_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ia.q011b._canonical_json_sha256(q011ia._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
