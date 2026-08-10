from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011an_active_block_structured_rows as q011an
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011an_study() -> dict[str, Any]:
    return q011an.run_q011an_study()


@pytest.fixture(scope="module")
def q011an_cycle(q011an_study: dict[str, Any]) -> dict[str, Any]:
    return q011an_study["cycle"]


def test_q011an_seals_q011am_and_all_prior_inputs(
    q011an_cycle: dict[str, Any],
) -> None:
    sealed = q011an_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 93
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011am_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 88
    assert tuple(sealed["q011am"]["digests"]) == q011an.Q011AM_DIGESTS
    assert sealed["q011am"]["artifact_sha256"] == q011an.Q011AM_ARTIFACT_SHA256
    assert sealed["q011am"]["runner_sha256"] == q011an.Q011AM_RUNNER_SHA256


def test_q011an_reconstructs_both_exact_families(
    q011an_cycle: dict[str, Any],
) -> None:
    audit = q011an_cycle["active_block_structured_row_audit"]
    assert audit["passed"]
    assert audit["representative_block_count"] == 2
    assert audit["active_identifier_count"] == 24
    for block_index, expected in q011an.EXPECTED_BLOCK_RECORDS.items():
        block = audit["representative_block_records"][block_index]
        assert block["transported_block"] == expected["transported_block"]
        assert block["proposal_matches"]
        assert block["family_distance_matches"]
        assert block["transport_metadata_matches"]
        assert block["eigendecomposition_matches"]
        assert block["centers_match"]
        assert block["transported_centers_are_exact_conjugates"]
        family = block["family"]
        assert family["entry_count"] == 153**2
        assert family["entry_digest_sha256"] == expected["family_digest"]
        assert family["minimum_sparse_nonzeros_per_row"] == 27
        assert family["maximum_sparse_nonzeros_per_row"] == 27


def test_q011an_certifies_dual_precision_row_radii(
    q011an_cycle: dict[str, Any],
) -> None:
    blocks = q011an_cycle["active_block_structured_row_audit"]["representative_block_records"]
    for block_index, expected in q011an.EXPECTED_BLOCK_RECORDS.items():
        block = blocks[block_index]
        primary = block["primary"]
        replay = block["replay"]
        assert primary["passed"] and replay["passed"] and block["replay_strict"]
        assert primary["precision_bits"] == 256
        assert replay["precision_bits"] == 384
        assert primary["basis_absolute_stream_count"] == 2 * 153**2
        assert replay["basis_absolute_stream_count"] == 2 * 153**2
        assert primary["basis_absolute_stream_digest_sha256"] == expected["primary_basis_digest"]
        assert replay["basis_absolute_stream_digest_sha256"] == expected["replay_basis_digest"]
        assert primary["row_record_digest_sha256"] == expected["primary_row_digest"]
        assert replay["row_record_digest_sha256"] == expected["replay_row_digest"]
        assert primary["maximum_row_radius_index"] == expected["maximum_row_radius_index"]
        assert primary["maximum_row_radius_binary64_hex"] == expected["maximum_row_radius_hex"]
        assert primary["neumann_correction_binary64_hex"] == expected["neumann_correction_hex"]
        for primary_row, replay_row in zip(
            primary["row_records"], replay["row_records"], strict=True
        ):
            assert q011an.q011z._fraction(
                replay_row["row_eigendisc_radius_upper"]
            ) < q011an.q011z._fraction(primary_row["row_eigendisc_radius_upper"])


def test_q011an_isolates_active_gershgorin_components(
    q011an_cycle: dict[str, Any],
) -> None:
    blocks = q011an_cycle["active_block_structured_row_audit"]["representative_block_records"]
    for block_index, expected in q011an.EXPECTED_BLOCK_RECORDS.items():
        block = blocks[block_index]
        for component in (
            block["representative_component"],
            block["transported_component"],
        ):
            assert component["component_count"] == expected["component_count"]
            assert component["component_digest_sha256"] == expected["component_digest"]
            assert component["mixed_component_count"] == 0
            assert (
                tuple(tuple(indices) for indices in component["active_component_memberships"])
                == expected["active_components"]
            )
            gap = component["minimum_active_inactive_gap"]
            assert (gap["active_center_index"], gap["inactive_center_index"]) == expected[
                "gap_pair"
            ]
            assert q011an.q011z._fraction(gap["maximum_coordinate_distance_minus_radii"]) > 0
            assert gap["gap_binary64_hex"] == expected["gap_hex"]


def test_q011an_builds_component_label_safe_common_hulls(
    q011an_cycle: dict[str, Any],
) -> None:
    audit = q011an_cycle["component_safe_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["identifier_record_count"] == 204
    assert audit["active_identifier_count"] == 24
    assert audit["q011al_component_relabel_identifier_count"] == 6
    assert audit["unmodified_identifier_count"] == 174
    assert audit["component_safe_record_digest_sha256"] == (q011an.EXPECTED_HYBRID_RECORD_DIGEST)
    assert audit["active_record_digest_sha256"] == q011an.EXPECTED_ACTIVE_RECORD_DIGEST
    assert audit["q011al_component_relabel_record_digest_sha256"] == (
        q011an.EXPECTED_Q011AL_RELABEL_RECORD_DIGEST
    )
    assert tuple(audit["selected_modulus_class_counts"]) == q011an.EXPECTED_CLASS_COUNTS
    assert audit["class_membership_digest_sha256"] == q011an.EXPECTED_CLASS_DIGEST

    intervals_by_component: dict[tuple[int, tuple[int, ...]], set[tuple[str, str]]] = {}
    for record in audit["component_safe_records"]:
        members = record["gershgorin_component_center_indices"]
        if members is None:
            continue
        key = (record["block_index"], tuple(members))
        intervals_by_component.setdefault(key, set()).add(
            (
                json.dumps(record["modulus_lower"], sort_keys=True),
                json.dumps(record["modulus_upper"], sort_keys=True),
            )
        )
        assert record["contained_in_q011ak_blockwise_interval"]
        if record["radius_kind"] == "active_block_component_hull":
            assert record["contained_in_q011am_hybrid_interval"]
    assert all(len(intervals) == 1 for intervals in intervals_by_component.values())


def test_q011an_clears_aggregate_fifty_five(
    q011an_cycle: dict[str, Any],
) -> None:
    audit = q011an_cycle["aggregate_fifty_five_clearance_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["group_pool_sizes"] == [20, 13, 1, 6]
    assert audit["left_pool_size"] == 260
    assert audit["right_pool_size"] == 6
    assert audit["distinct_relation_counts"] == (q011an.EXPECTED_OBSTRUCTION_DISTINCT_RELATIONS)
    assert audit["weighted_relation_counts"] == (q011an.EXPECTED_OBSTRUCTION_WEIGHTED_RELATIONS)
    assert audit["first_unresolved"] is None
    minimum = audit["minimum_separated_witness"]
    assert minimum["target_identifier"] == q011an.EXPECTED_MINIMUM_TARGET
    assert minimum["left_index"] == q011an.EXPECTED_MINIMUM_LEFT_INDEX
    assert minimum["right_index"] == q011an.EXPECTED_MINIMUM_RIGHT_INDEX
    assert tuple(minimum["source_identifiers"]) == q011an.EXPECTED_MINIMUM_SOURCES
    assert minimum["outward_gap_lower"]["binary64_hex"] == (q011an.EXPECTED_MINIMUM_OUTWARD_GAP_HEX)
    assert minimum["exact_gap_hex"] == q011an.EXPECTED_MINIMUM_EXACT_GAP_HEX
    assert minimum["witness_digest_sha256"] == q011an.EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011an_directly_separates_all_component_safe_aggregates(
    q011an_cycle: dict[str, Any],
) -> None:
    sweep = q011an_cycle["full_component_safe_degree_sixteen_sweep_audit"]
    assert sweep["passed"]
    assert all(sweep["checks"].values())
    assert sweep["audited_overlap_aggregate_count"] == 154
    assert sweep["fully_separated_overlap_aggregate_count"] == 154
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["remaining_overlap_aggregate_indices"] == []
    assert sweep["first_unresolved_witness"] is None
    assert sweep["distinct_relation_counts"] == q011an.EXPECTED_DISTINCT_RELATIONS
    assert sweep["weighted_relation_counts"] == q011an.EXPECTED_WEIGHTED_RELATIONS
    assert sweep["aggregate_record_digest_sha256"] == (q011an.EXPECTED_FULL_AGGREGATE_DIGEST)
    assert sweep["bound_matrix_digest_sha256"] == q011an.EXPECTED_FULL_BOUND_DIGEST
    assert sweep["coefficient_matrix_digest_sha256"] == (q011an.EXPECTED_FULL_COEFFICIENT_DIGEST)
    assert sweep["classification_matrix_digest_sha256"] == (
        q011an.EXPECTED_FULL_CLASSIFICATION_DIGEST
    )
    assert sweep["degree_sixteen_bridge"] == {
        "old_modulus_separated_aggregate_count": 815,
        "directly_separated_overlap_inventory_aggregate_count": 154,
        "degree_sixteen_aggregate_count": 969,
        "remaining_degree_sixteen_aggregate_count": 0,
    }


def test_q011an_accepts_degree_sixteen_only(
    q011an_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011an_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011an_cycle["hypothesis_gates"].values())
    assert q011an_cycle["study_validity"] == "passed"
    assert q011an_cycle["hypothesis_outcome"] == "accepted"
    assert q011an_cycle["actual_resonance_outcome"] == q011an.ACTUAL_RESONANCE_OUTCOME
    assert q011an_cycle["scientific_classification"] == q011an.ACCEPTED_CLASSIFICATION
    theorem = q011an_cycle["theorem_consequence"]
    assert theorem["component_label_safe_eigendisc_inclusion_is_certified"]
    assert theorem["degree_sixteen_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_sixteen_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 17))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(17, 91))
    assert not theorem["degrees_17_through_90_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "only within those registered degree-sixteen relations" in q011an_cycle["claim_boundary"]
    assert "Q011ao" in q011an_cycle["next_change"]


def test_q011an_cycle_has_strict_reproducible_digests(
    q011an_cycle: dict[str, Any],
) -> None:
    json.dumps(q011an_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("d617a48bdca98ff949645394948527573b6574176eadcb15eab7de7feda60dfd"),
        "row_digest_sha256": ("5c558564ec862d621a75bff1cc6882c4ead98910b67f02559d1f8bec537e0c13"),
        "envelope_digest_sha256": (
            "b3a40b84b19d69adabea11a53963a47584f361c96abf91224f6c4fe9e41b5a9f"
        ),
        "sweep_digest_sha256": ("db38109e4a83209a28a8f982f88b9eec6c3b8a9f07c0b3a13be3592db2a91e53"),
        "result_digest_sha256": (
            "263a56ba3b426376f3e82d29c7815f6338063e3f682d68ee995f5c129a721309"
        ),
    }
    assert {name: q011an_cycle[name] for name in expected} == expected
    assert q011an_cycle["result_digest_sha256"] == (
        q011an.q011b._canonical_json_sha256(q011an._result_digest_sections(q011an_cycle))
    )


def test_q011an_study_metadata_and_generated_artifact_are_scoped(
    q011an_study: dict[str, Any],
) -> None:
    assert q011an_study["schema_version"] == 1
    assert q011an_study["source"] == source_metadata()
    assert q011an_study["study_gate"] == "passed"
    assert q011an_study["scientific_outcome"] == "accepted"
    assert q011an_study["actual_resonance_outcome"] == q011an.ACTUAL_RESONANCE_OUTCOME
    scope = q011an_study["mathematical_scope"]
    assert scope["degree"] == 16
    assert scope["active_block_identifier_count"] == 24
    assert scope["q011al_component_relabel_identifier_count"] == 6
    assert scope["degree_sixteen_external_nonresonance_claim"] is True
    assert scope["actual_degree_sixteen_external_resonance_ruled_out_claim"] is True
    assert scope["degrees_17_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011an_study, allow_nan=False)

    runner_path = Path(q011an.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011an_active_block_structured_rows.json"
    if not artifact_path.exists():
        pytest.skip("Q011an artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == runner_path.name
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["actual_resonance_outcome"] == q011an.ACTUAL_RESONANCE_OUTCOME
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011an.q011b._canonical_json_sha256(q011an._result_digest_sections(artifact["cycle"]))
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
