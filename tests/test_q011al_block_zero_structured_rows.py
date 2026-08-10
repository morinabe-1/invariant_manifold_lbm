from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011al_block_zero_structured_rows as q011al
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011al_study() -> dict[str, Any]:
    return q011al.run_q011al_study()


@pytest.fixture(scope="module")
def q011al_cycle(q011al_study: dict[str, Any]) -> dict[str, Any]:
    return q011al_study["cycle"]


def test_q011al_seals_q011ak_and_all_prior_inputs(
    q011al_cycle: dict[str, Any],
) -> None:
    sealed = q011al_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 83
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011ak_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 78
    assert tuple(sealed["q011ak"]["digests"]) == q011al.Q011AK_DIGESTS
    assert sealed["q011ak"]["artifact_sha256"] == q011al.Q011AK_ARTIFACT_SHA256
    assert sealed["q011ak"]["runner_sha256"] == q011al.Q011AK_RUNNER_SHA256


def test_q011al_reconstructs_the_block_zero_exact_family(
    q011al_cycle: dict[str, Any],
) -> None:
    audit = q011al_cycle["block_zero_exact_family_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["block_index"] == 0
    assert audit["dimension"] == 150
    assert audit["selected_center_indices"] == list(range(144, 150))
    assert audit["entrywise_family_record_count"] == 22_500
    assert audit["entrywise_family_digest_sha256"] == q011al.EXPECTED_FAMILY_DIGEST


def test_q011al_certifies_dual_precision_structured_row_radii(
    q011al_cycle: dict[str, Any],
) -> None:
    audit = q011al_cycle["block_zero_structured_row_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    primary = audit["primary_protocol"]
    replay = audit["replay_protocol"]
    assert primary["passed"] and replay["passed"]
    assert primary["precision_bits"] == 256
    assert replay["precision_bits"] == 384
    assert primary["basis_absolute_stream_count"] == 45_000
    assert replay["basis_absolute_stream_count"] == 45_000
    assert primary["basis_absolute_stream_digest_sha256"] == (
        q011al.EXPECTED_PRIMARY_BASIS_DIGEST
    )
    assert replay["basis_absolute_stream_digest_sha256"] == (
        q011al.EXPECTED_REPLAY_BASIS_DIGEST
    )
    assert primary["row_record_digest_sha256"] == q011al.EXPECTED_PRIMARY_ROW_DIGEST
    assert replay["row_record_digest_sha256"] == q011al.EXPECTED_REPLAY_ROW_DIGEST
    assert len(primary["row_records"]) == len(replay["row_records"]) == 150
    for primary_record, replay_record in zip(
        primary["row_records"], replay["row_records"], strict=True
    ):
        assert q011al.q011z._fraction(
            replay_record["row_eigendisc_radius_upper"]
        ) < q011al.q011z._fraction(primary_record["row_eigendisc_radius_upper"])
        assert primary_record["contained_in_q011y_block_radius"]
    assert primary["maximum_row_radius_index"] == 34
    assert primary["maximum_row_radius_binary64_hex"] == (
        q011al.EXPECTED_MAXIMUM_ROW_RADIUS_HEX
    )


def test_q011al_selected_rows_and_gershgorin_components_are_isolated(
    q011al_cycle: dict[str, Any],
) -> None:
    rows = q011al_cycle["block_zero_structured_row_audit"]
    assert rows["selected_primary_row_digest_sha256"] == (
        q011al.EXPECTED_SELECTED_ROW_DIGEST
    )
    selected = rows["selected_primary_row_records"]
    assert tuple(record["center_index"] for record in selected) == tuple(range(144, 150))
    assert tuple(record["row_eigendisc_radius_binary64_hex"] for record in selected) == (
        q011al.EXPECTED_SELECTED_RADIUS_HEX
    )

    components = q011al_cycle["block_zero_gershgorin_component_audit"]
    assert components["passed"]
    assert all(components["checks"].values())
    assert len(components["component_records"]) == 73
    assert components["mixed_component_count"] == 0
    assert tuple(
        tuple(record["center_indices"])
        for record in components["selected_component_records"]
    ) == q011al.EXPECTED_SELECTED_COMPONENTS
    assert components["component_record_digest_sha256"] == (
        q011al.EXPECTED_COMPONENT_DIGEST
    )
    gap = components["minimum_selected_external_gap"]
    assert (gap["selected_center_index"], gap["external_center_index"]) == (149, 143)
    assert q011al.q011z._fraction(gap["maximum_coordinate_distance_minus_radii"]) > 0
    assert gap["gap_binary64_hex"] == q011al.EXPECTED_SELECTED_EXTERNAL_GAP_HEX


def test_q011al_builds_the_registered_six_source_hybrid_envelope(
    q011al_cycle: dict[str, Any],
) -> None:
    audit = q011al_cycle["hybrid_selected_block_zero_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["identifier_record_count"] == 204
    assert audit["refined_identifier_count"] == 6
    assert audit["unchanged_identifier_count"] == 198
    assert audit["refined_identifiers"] == [
        f"block=0;center={index}" for index in range(144, 150)
    ]
    assert audit["hybrid_record_digest_sha256"] == (
        q011al.EXPECTED_HYBRID_RECORD_DIGEST
    )
    assert audit["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert audit["class_membership_digest_sha256"] == (
        q011al.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )


def test_q011al_clears_every_registered_obstruction_comparison(
    q011al_cycle: dict[str, Any],
) -> None:
    audit = q011al_cycle["registered_obstruction_clearance_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    record = audit["clearance_record"]
    assert record["modulus_signature_count"] == 35_280
    assert audit["compatible_modulus_signature_count"] == 35_280
    assert audit["compatible_original_monomial_count"] == 1_732_864
    assert record["weighted_comparison_count"] == 3_465_728
    assert record["distinct_comparison_count"] == 141_120
    assert record["weighted_relation_counts"] == q011al.EXPECTED_RELATIONS_WEIGHTED
    assert record["distinct_relation_counts"] == q011al.EXPECTED_RELATIONS_DISTINCT
    assert audit["clearance_record_digest_sha256"] == (
        q011al.EXPECTED_CLEARANCE_RECORD_DIGEST
    )


def test_q011al_seals_the_positive_minimum_witness(
    q011al_cycle: dict[str, Any],
) -> None:
    witness = q011al_cycle["registered_obstruction_clearance_audit"][
        "clearance_record"
    ]["minimum_outward_witness"]
    assert witness["target_identifier"] == "block=11;center=4"
    assert witness["left_index"] == 385
    assert witness["right_index"] == 0
    assert witness["wave_multiplicity"] == 35
    assert witness["block_zero_multiplicity"] == 0
    assert witness["relation"] == "product_below_target"
    assert tuple(tuple(group) for group in witness["class_counts"]) == (
        q011al.EXPECTED_MINIMUM_CLASS_COUNTS
    )
    assert tuple(witness["source_identifiers"]) == q011al.EXPECTED_MINIMUM_SOURCES
    assert witness["outward_gap_hex"] == q011al.EXPECTED_MINIMUM_GAP_HEX
    assert witness["exact_gap_hex"] == q011al.EXPECTED_EXACT_GAP_HEX
    assert q011al.q011z._fraction(witness["exact_gap"]) > Fraction(0)


def test_q011al_accepts_only_the_registered_obstruction_clearance(
    q011al_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011al_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011al_cycle["hypothesis_gates"].values())
    assert q011al_cycle["study_validity"] == "passed"
    assert q011al_cycle["hypothesis_outcome"] == "accepted"
    assert q011al_cycle["actual_resonance_outcome"] == "not_established"
    assert q011al_cycle["scientific_classification"] == q011al.ACCEPTED_CLASSIFICATION
    theorem = q011al_cycle["theorem_consequence"]
    assert theorem["block_zero_structured_row_eigendisc_inclusion_is_certified"]
    assert theorem[
        "selected_block_zero_eigenvalues_are_covered_with_exact_multiplicity"
    ]
    assert theorem["registered_degree_sixteen_obstruction_is_cleared"]
    assert theorem["q011ak_block_common_radius_rejection_is_preserved"]
    assert not theorem["all_degree_sixteen_overlap_aggregates_are_cleared"]
    assert not theorem["degree_sixteen_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 16))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(16, 91))
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "other 153" in q011al_cycle["claim_boundary"]
    assert "Q011am" in q011al_cycle["next_change"]


def test_q011al_cycle_has_strict_reproducible_digests(
    q011al_cycle: dict[str, Any],
) -> None:
    json.dumps(q011al_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "97bfc790c2a761d63678b3396e2f1f6ba1b28be1605d0e0b9dae6b63f2f57a93"
        ),
        "family_digest_sha256": (
            "79f442ff7bbb874c79f7692b58f3986a34a6df0f0ee9ffc618fa21608ef6e41c"
        ),
        "row_digest_sha256": (
            "6d4a96cb71535048f34e6a3e1cb9c1afe895cc87558bb98cb791288336aa5816"
        ),
        "clearance_digest_sha256": (
            "708e866d675f2328cca388191c35062f1dd0f7dbee46aa7355976bb31461db31"
        ),
        "result_digest_sha256": (
            "9befdd9e0b81914e1f18c7b7aff772471b17d1454d81725f44d3736625f8c7c1"
        ),
    }
    assert {name: q011al_cycle[name] for name in expected} == expected
    assert q011al_cycle["result_digest_sha256"] == (
        q011al.q011b._canonical_json_sha256(
            q011al._result_digest_sections(q011al_cycle)
        )
    )


def test_q011al_study_metadata_and_generated_artifact_are_scoped(
    q011al_study: dict[str, Any],
) -> None:
    assert q011al_study["schema_version"] == 1
    assert q011al_study["source"] == source_metadata()
    assert q011al_study["study_gate"] == "passed"
    assert q011al_study["scientific_outcome"] == "accepted"
    assert q011al_study["actual_resonance_outcome"] == "not_established"
    scope = q011al_study["mathematical_scope"]
    assert scope["aggregate_index"] == 99
    assert scope["registered_obstruction_clearance_claim"] is True
    assert scope["degree_sixteen_external_nonresonance_claim"] is False
    assert scope["actual_complex_resonance_claim"] is False
    assert scope["degrees_17_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011al_study, allow_nan=False)

    runner_path = Path(q011al.__file__).resolve()
    artifact_path = (
        runner_path.parent / "artifacts" / "q011al_block_zero_structured_rows.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011al artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "b0fe7be52da885e28b9e29d580a187d232ef6fe4c233be2db3cf7a18974420dc"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011al_block_zero_structured_rows.py",
        "sha256": "72211072fdc657ba1931dda983b167d2ac44a8f71e18aa016b22ea3f7a7cedf2",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011al.q011b._canonical_json_sha256(
            q011al._result_digest_sections(artifact["cycle"])
        )
    )
    json.dumps(artifact, allow_nan=False)
