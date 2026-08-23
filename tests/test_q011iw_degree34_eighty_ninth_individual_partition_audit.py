from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011iw_degree34_eighty_ninth_individual_partition_audit as q011iw
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "be135232531195a2c9a3b37df1bd12e931548a8261f3718f97652193e9bc4318"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "8be53639e5b2c57c31877c296d20761503e993faf1f2d0c83f77c957e1576861"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "c37de0bfd22becfc7ac226ac5d7b9076e336033bf9cc176661c25859f9597ed9",
    "partition_input_digest_sha256": (
        "93b0ad9d7d378c883a33cc1c3a439229742de7a0a321a00ecc8e79d14950e2e6"
    ),
    "allocation_audit_digest_sha256": (
        "a37ac1b4cfa7b717ef8bf5ad855658fe9be7baaf87ab75b7584ed8ba9a56000f"
    ),
    "result_digest_sha256": "2aff90fd2c1b7b4adba668cdd79005a69b97e4f0fbe3a902f7ac813e4aa6dda8",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "be21034c6521e94c58630e0e842796fb6445de3e0cd559e5afd7ac357e4094ee"
    ),
    "parent_center_product_interval_digest_sha256": (
        "a4dbe0452ef301131170610cf712e22aa98d35fb1e4515416c16f982017588ca"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "1b2540d2e1854bd37a4ca687d028e6222deab302d4087e98256f37d15acb5775"
    ),
    "allocation_classification_record_digest_sha256": (
        "a1d72a6624fd366426eb30b9bcbcfe012910966f1f1c4ff2c40bb467f7dc778c"
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
def q011iw_structure() -> dict[str, Any]:
    sealed, artifacts = q011iw._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011iw._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011iw_study() -> dict[str, Any]:
    return q011iw.run_q011iw_study()


@pytest.fixture(scope="module")
def q011iw_cycle(q011iw_study: dict[str, Any]) -> dict[str, Any]:
    return q011iw_study["cycle"]


def test_q011iw_seals_q011iv_and_all_prior_inputs(
    q011iw_structure: dict[str, Any],
) -> None:
    sealed = q011iw_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 235
    assert sealed["direct_digest_count"] == 1_070
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011iv"]["digests"]) == q011iw.Q011IV_DIGESTS
    assert sealed["q011iv"]["artifact_sha256"] == q011iw.Q011IV_ARTIFACT_SHA256
    assert sealed["q011iv"]["runner_sha256"] == q011iw.Q011IV_RUNNER_SHA256
    assert sealed["q011iv"]["resolved_witness_digest_sha256"] == (
        q011iw.EXPECTED_ORDINAL_EIGHTY_SEVEN_RESOLUTION_DIGEST
    )


def test_q011iw_selects_exactly_flatten_ordinal_eighty_eight(
    q011iw_structure: dict[str, Any],
) -> None:
    fixed = q011iw_structure["fixed"]
    selection = fixed["eighty_ninth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 88
    assert selection["selected_left_index"] == 11
    assert selection["selected_right_index"] == 0
    assert selection["previous_phase_resolved_ordinals"] == list(range(88))
    assert selection["ordinal_eighty_seven_resolution_digest_sha256"] == (
        q011iw.EXPECTED_ORDINAL_EIGHTY_SEVEN_RESOLUTION_DIGEST
    )
    parent = selection["eighty_ninth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [0, 7]]
    assert parent["wave_multiplicity"] == 1_255
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011iw.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011iw.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011iw.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011iw_reconstructs_registered_partition_and_inventory(
    q011iw_structure: dict[str, Any],
) -> None:
    fixed = q011iw_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [0, 7]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 1, 8, 5, 7]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011iw.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011iw.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 22_464
    assert fixed["full_allocation_digest_sha256"] == q011iw.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 1_255
    assert q011iw_structure["compatible_count"] == 1_255
    assert fixed["compatible_allocation_digest_sha256"] == (q011iw.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 1, 0, 8, 0, 5, 5, 2]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 1, 0, 8, 0, 0, 5, 0, 7]
    assert fixed["parent_witness_allocation_index"] == 22_416
    assert fixed["parent_witness_compatible_index"] == 1_254
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iw result is not sealed")
def test_q011iw_classifies_every_registered_exact_interval(
    q011iw_cycle: dict[str, Any],
) -> None:
    partition = q011iw_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 1_255
    records = partition["allocation_classification_records"]
    assert len(records) == 1_255
    assert [record["compatible_allocation_index"] for record in records] == list(range(1_255))
    assert sum(partition["exact_relation_counts"].values()) == 1_255
    assert sum(partition["binary64_outward_relation_counts"].values()) == 1_255
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iw result is not sealed")
def test_q011iw_applies_registered_stopping_rule(
    q011iw_cycle: dict[str, Any],
) -> None:
    assert q011iw_cycle["study_validity"] == "passed"
    assert q011iw_cycle["failed_validity_order"] == []
    assert q011iw_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011iw_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011iw_cycle["diagnostic_gates"].values())
    assert q011iw_cycle["scientific_outcome"] == "not_evaluated"
    assert q011iw_cycle["actual_resonance_outcome"] == "not_established"
    assert q011iw_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011iw.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011iw.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011iw.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011iw_cycle["diagnostic_classification"] == expected
    assert not q011iw_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011iw_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_eighty_ninth_q011cb_witness"],
        theorem["eighty_ninth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_eighty_ninth_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iw result is not sealed")
def test_q011iw_preserves_boundary_and_reproducible_digests(
    q011iw_cycle: dict[str, Any],
) -> None:
    theorem = q011iw_cycle["theorem_consequence"]
    assert theorem["q011iv_ordinal_eighty_seven_phase_resolution_is_preserved"]
    assert theorem["q011iu_ordinal_eighty_seven_interval_inert_diagnostic_is_preserved"]
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
    assert "flatten ordinal 88" in q011iw_cycle["claim_boundary"]
    assert "ordinals 0 through 87" in q011iw_cycle["claim_boundary"]
    assert "later 44711 Q011cb refined signatures" in q011iw_cycle["claim_boundary"]
    assert "Q011ix" in q011iw_cycle["next_change"]
    assert {name: q011iw_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011iw_cycle["result_digest_sha256"] == (
        q011iw.q011b._canonical_json_sha256(q011iw._result_digest_sections(q011iw_cycle))
    )
    assert q011iw._protocol_globals_are_restored()
    json.dumps(q011iw_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iw result is not sealed")
def test_q011iw_study_metadata_and_optional_artifact_are_scoped(
    q011iw_study: dict[str, Any],
) -> None:
    assert q011iw_study["schema_version"] == 1
    assert q011iw_study["source"] == source_metadata()
    assert q011iw_study["study_gate"] == "passed"
    assert q011iw_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011iw_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 1_255
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011iw_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 88
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011iw_study, allow_nan=False)

    runner_path = Path(q011iw.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011iw_degree34_eighty_ninth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011iw artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011iw_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011iw.q011b._canonical_json_sha256(q011iw._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
