from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011iy_degree34_ninetieth_individual_partition_audit as q011iy
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "8011d7573c61fc8b1b71a6982323c7885c13fb5ecab37d2f01ec583bcb9f6503"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "056001d024c4fbc2177bb7e525a54694e088818be8fcb6ad46fac52ac9b4f12b"
)
EXPECTED_SECTION_DIGESTS: dict[str, str] | None = {
    "input_digest_sha256": "0a54275db985b269181add21a3141e646d5f84bea1b697b16847fa081370d4c0",
    "partition_input_digest_sha256": (
        "cc8f301a84f4251490783319b0d0d864da612920b256c5cd25f2c071e91ac99f"
    ),
    "allocation_audit_digest_sha256": (
        "de46a956bd3c438c802a60686bc13a05bcf8be675154e32d683aaa781c2d7569"
    ),
    "result_digest_sha256": "527ec5d3894eed2e027b25e1ebb6d11fc625a8ed0a603d03e6e7110a431fccd3",
}
EXPECTED_PARTITION_DIGESTS: dict[str, str] | None = {
    "parent_product_interval_digest_sha256": (
        "51edd24550c16a9f3ab61675ab55e78faea66d9e579a17f50006f5625d5fac7d"
    ),
    "parent_center_product_interval_digest_sha256": (
        "6e56e96e451ca7afb743079bcba97a04d43b8dfd055294d5bdd877addd223c0a"
    ),
    "parent_target_interval_digest_sha256": (
        "64553c5af9c572adf0305dda9679e26c0ec8e165e8ab707f8902b4e227b35679"
    ),
    "parent_intersection_interval_digest_sha256": (
        "79ec3645af349629a88cbc2057e1df0a00cc160c1bdc1c85303c26df1c10dd17"
    ),
    "allocation_classification_record_digest_sha256": (
        "c18e1481b3173f00be6f6b53d374da6a97b4adcc74250dfac1debb00d7c3fa18"
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
def q011iy_structure() -> dict[str, Any]:
    sealed, artifacts = q011iy._sealed_input_audit()
    fixed, _lookup, compatible, parent = q011iy._fixed_individual_input_audit(artifacts)
    return {
        "sealed": sealed,
        "fixed": fixed,
        "compatible_count": len(compatible),
        "parent": parent,
    }


@pytest.fixture(scope="module")
def q011iy_study() -> dict[str, Any]:
    return q011iy.run_q011iy_study()


@pytest.fixture(scope="module")
def q011iy_cycle(q011iy_study: dict[str, Any]) -> dict[str, Any]:
    return q011iy_study["cycle"]


def test_q011iy_seals_q011ix_and_all_prior_inputs(
    q011iy_structure: dict[str, Any],
) -> None:
    sealed = q011iy_structure["sealed"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 237
    assert sealed["direct_digest_count"] == 1_079
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ix"]["digests"]) == q011iy.Q011IX_DIGESTS
    assert sealed["q011ix"]["artifact_sha256"] == q011iy.Q011IX_ARTIFACT_SHA256
    assert sealed["q011ix"]["runner_sha256"] == q011iy.Q011IX_RUNNER_SHA256
    assert sealed["q011ix"]["resolved_witness_digest_sha256"] == (
        q011iy.EXPECTED_ORDINAL_EIGHTY_EIGHT_RESOLUTION_DIGEST
    )


def test_q011iy_selects_exactly_flatten_ordinal_eighty_nine(
    q011iy_structure: dict[str, Any],
) -> None:
    fixed = q011iy_structure["fixed"]
    selection = fixed["ninetieth_parent_witness_selection_audit"]
    assert selection["passed"]
    assert all(selection["checks"].values())
    assert selection["flatten_shape"] == [5_600, 8]
    assert selection["selected_flat_ordinal"] == 89
    assert selection["selected_left_index"] == 11
    assert selection["selected_right_index"] == 1
    assert selection["previous_phase_resolved_ordinals"] == list(range(89))
    assert selection["ordinal_eighty_eight_resolution_digest_sha256"] == (
        q011iy.EXPECTED_ORDINAL_EIGHTY_EIGHT_RESOLUTION_DIGEST
    )
    parent = selection["ninetieth_parent_witness"]
    assert parent["class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [1, 6]]
    assert parent["wave_multiplicity"] == 2_185
    assert parent["block_zero_multiplicity"] == 0
    assert parent["intersection_interval"]["width_hex"] == (
        q011iy.EXPECTED_PARENT_INTERSECTION_WIDTH_HEX
    )
    assert parent["center_only_diagnostic"]["relation"] == "target_below_product"
    assert parent["center_only_diagnostic"]["gap_hex"] == (q011iy.EXPECTED_PARENT_CENTER_GAP_HEX)
    assert parent["witness_digest_sha256"] == q011iy.EXPECTED_PARENT_WITNESS_DIGEST


def test_q011iy_reconstructs_registered_partition_and_inventory(
    q011iy_structure: dict[str, Any],
) -> None:
    fixed = q011iy_structure["fixed"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_class_counts"] == [[0, 0, 1, 12], [1, 8], [5], [1, 6]]
    occupied = fixed["occupied_class_records"]
    assert [record["source_count"] for record in occupied] == [1, 12, 1, 8, 5, 1, 6]
    assert all(record["all_member_intervals_equal"] for record in occupied)
    assert fixed["occupied_class_record_digest_sha256"] == (q011iy.EXPECTED_OCCUPIED_RECORD_DIGEST)
    assert tuple(fixed["singleton_identifier_order"]) == q011iy.EXPECTED_IDENTIFIER_ORDER
    assert fixed["full_allocation_count"] == 39_312
    assert fixed["full_allocation_digest_sha256"] == q011iy.EXPECTED_ALLOCATION_DIGEST
    assert fixed["compatible_allocation_count"] == 2_185
    assert q011iy_structure["compatible_count"] == 2_185
    assert fixed["compatible_allocation_digest_sha256"] == (q011iy.EXPECTED_COMPATIBLE_DIGEST)
    assert fixed["first_compatible_counts"] == [0, 1, 0, 12, 0, 1, 0, 8, 0, 5, 0, 1, 5, 1]
    assert fixed["last_compatible_counts"] == [1, 0, 12, 0, 1, 0, 8, 0, 0, 5, 0, 1, 0, 6]
    assert fixed["parent_witness_allocation_index"] == 39_228
    assert fixed["parent_witness_compatible_index"] == 2_184
    assert fixed["compatible_allocations_exactly_partition_parent_wave_multiplicity"]


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iy result is not sealed")
def test_q011iy_classifies_every_registered_exact_interval(
    q011iy_cycle: dict[str, Any],
) -> None:
    partition = q011iy_cycle["individual_allocation_interval_audit"]
    assert partition["passed"]
    assert all(partition["checks"].values())
    assert partition["compatible_allocation_count"] == 2_185
    records = partition["allocation_classification_records"]
    assert len(records) == 2_185
    assert [record["compatible_allocation_index"] for record in records] == list(range(2_185))
    assert sum(partition["exact_relation_counts"].values()) == 2_185
    assert sum(partition["binary64_outward_relation_counts"].values()) == 2_185
    assert {name: partition[name] for name in EXPECTED_PARTITION_DIGESTS} == (
        EXPECTED_PARTITION_DIGESTS
    )


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iy result is not sealed")
def test_q011iy_applies_registered_stopping_rule(
    q011iy_cycle: dict[str, Any],
) -> None:
    assert q011iy_cycle["study_validity"] == "passed"
    assert q011iy_cycle["failed_validity_order"] == []
    assert q011iy_cycle["failed_diagnostic_order"] == []
    assert all(gate["passed"] for gate in q011iy_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011iy_cycle["diagnostic_gates"].values())
    assert q011iy_cycle["scientific_outcome"] == "not_evaluated"
    assert q011iy_cycle["actual_resonance_outcome"] == "not_established"
    assert q011iy_cycle["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    expected = {
        "partition_inert_persistent": q011iy.INERT_CLASSIFICATION,
        "resolved_by_individual_partition": q011iy.RESOLVED_CLASSIFICATION,
        "partition_effective_but_persistent": q011iy.EFFECTIVE_PERSISTENT_CLASSIFICATION,
    }[EXPECTED_REFINEMENT_OUTCOME]
    assert q011iy_cycle["diagnostic_classification"] == expected
    assert not q011iy_cycle["individual_allocation_interval_audit"][
        "complex_phase_product_evaluated"
    ]
    theorem = q011iy_cycle["theorem_consequence"]
    flags = (
        theorem["individual_partition_is_interval_inert_for_ninetieth_q011cb_witness"],
        theorem["ninetieth_q011cb_witness_is_resolved_by_individual_partition"],
        theorem["individual_partition_changes_intervals_but_ninetieth_q011cb_witness_persists"],
    )
    assert sum(flags) == 1


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iy result is not sealed")
def test_q011iy_preserves_boundary_and_reproducible_digests(
    q011iy_cycle: dict[str, Any],
) -> None:
    theorem = q011iy_cycle["theorem_consequence"]
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
    assert "flatten ordinal 89" in q011iy_cycle["claim_boundary"]
    assert "ordinals 0 through 88" in q011iy_cycle["claim_boundary"]
    assert "later 44710 Q011cb refined signatures" in q011iy_cycle["claim_boundary"]
    assert "Q011iz" in q011iy_cycle["next_change"]
    assert {name: q011iy_cycle[name] for name in EXPECTED_SECTION_DIGESTS} == (
        EXPECTED_SECTION_DIGESTS
    )
    assert q011iy_cycle["result_digest_sha256"] == (
        q011iy.q011b._canonical_json_sha256(q011iy._result_digest_sections(q011iy_cycle))
    )
    assert q011iy._protocol_globals_are_restored()
    json.dumps(q011iy_cycle, allow_nan=False)


@pytest.mark.skipif(not RESULT_EXPECTATIONS_FIXED, reason="Q011iy result is not sealed")
def test_q011iy_study_metadata_and_optional_artifact_are_scoped(
    q011iy_study: dict[str, Any],
) -> None:
    assert q011iy_study["schema_version"] == 1
    assert q011iy_study["source"] == source_metadata()
    assert q011iy_study["study_gate"] == "passed"
    assert q011iy_study["refinement_outcome"] == EXPECTED_REFINEMENT_OUTCOME
    runtime = q011iy_study["arithmetic_runtime"]
    assert runtime["target_comparisons"] == 2_185
    assert runtime["complex_phase_product_evaluated"] is False
    assert runtime["protocol_globals_restored_after_use"] is True
    scope = q011iy_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 2_340
    assert scope["parent_flat_ordinal"] == 89
    assert scope["target_identifier"] == "block=7;center=44"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    json.dumps(q011iy_study, allow_nan=False)

    runner_path = Path(q011iy.__file__).resolve()
    if EXPECTED_RUNNER_SHA256 is not None:
        assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011iy_degree34_ninetieth_individual_partition_audit.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011iy artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    if EXPECTED_RUNNER_SHA256 is not None:
        assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == q011iy_study["refinement_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011iy.q011b._canonical_json_sha256(q011iy._result_digest_sections(artifact["cycle"]))
    )
    if EXPECTED_ARTIFACT_SHA256 is not None:
        assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
