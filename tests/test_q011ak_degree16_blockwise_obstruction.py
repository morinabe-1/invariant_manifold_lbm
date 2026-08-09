from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011ak_degree16_blockwise_obstruction as q011ak
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ak_study() -> dict[str, Any]:
    return q011ak.run_q011ak_study()


@pytest.fixture(scope="module")
def q011ak_cycle(q011ak_study: dict[str, Any]) -> dict[str, Any]:
    return q011ak_study["cycle"]


def test_q011ak_seals_q011aj_and_all_prior_inputs(
    q011ak_cycle: dict[str, Any],
) -> None:
    sealed = q011ak_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 78
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011aj_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 73
    assert tuple(sealed["q011aj"]["digests"]) == q011ak.Q011AJ_DIGESTS
    assert sealed["q011aj"]["artifact_sha256"] == q011ak.Q011AJ_ARTIFACT_SHA256
    assert sealed["q011aj"]["runner_sha256"] == q011ak.Q011AJ_RUNNER_SHA256


def test_q011ak_reconstructs_the_registered_obstruction_input(
    q011ak_cycle: dict[str, Any],
) -> None:
    audit = q011ak_cycle["registered_obstruction_input_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["aggregate_index"] == 99
    assert audit["selected_type_counts"] == [5, 6, 4, 1]
    assert audit["external_group_indices"] == [155]
    assert tuple(audit["target_identifiers"]) == q011ak.EXPECTED_OBSTRUCTION_TARGETS
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]


def test_q011ak_reconstructs_exact_blockwise_radii_and_containment(
    q011ak_cycle: dict[str, Any],
) -> None:
    radius = q011ak_cycle["blockwise_transformed_residual_radius_audit"]
    assert len(radius["radius_records"]) == 17
    assert radius["radius_record_digest_sha256"] == (
        q011ak.EXPECTED_RADIUS_RECORD_DIGEST
    )
    assert radius["active_radius_binary64_hex"] == {
        str(key): value for key, value in q011ak.EXPECTED_ACTIVE_RADIUS_HEX.items()
    }
    envelope = q011ak_cycle["blockwise_transformed_residual_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["identifier_record_count"] == 204
    assert envelope["unique_center_modulus_evaluation_count"] == 114
    assert envelope["blockwise_record_digest_sha256"] == (
        q011ak.EXPECTED_BLOCKWISE_RECORD_DIGEST
    )
    assert all(
        record["contained_in_uniform_envelope"]
        for record in envelope["blockwise_disc_records"]
    )


def test_q011ak_preserves_classes_and_uses_class_constant_radii(
    q011ak_cycle: dict[str, Any],
) -> None:
    audit = q011ak_cycle["blockwise_fourier_modulus_compression_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert audit["class_membership_digest_sha256"] == (
        q011ak.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )
    assert len(audit["class_radius_records"]) == sum(q011ak.EXPECTED_CLASS_COUNTS)


def test_q011ak_reproduces_blockwise_relations_and_histogram(
    q011ak_cycle: dict[str, Any],
) -> None:
    audit = q011ak_cycle["registered_blockwise_obstruction_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    record = audit["registered_obstruction_record"]
    assert record["modulus_signature_count"] == 35_280
    assert audit["compatible_modulus_signature_count"] == 35_280
    assert audit["compatible_original_monomial_count"] == 1_732_864
    assert record["weighted_comparison_count"] == 3_465_728
    assert record["distinct_comparison_count"] == 141_120
    assert record["weighted_relation_counts"] == q011ak.EXPECTED_WEIGHTED_RELATIONS
    assert record["distinct_relation_counts"] == q011ak.EXPECTED_DISTINCT_RELATIONS
    assert record["block_zero_multiplicity_histogram"] == (
        q011ak.EXPECTED_BLOCK_ZERO_HISTOGRAM
    )
    assert record["block_zero_multiplicity_histogram_digest_sha256"] == (
        q011ak.EXPECTED_BLOCK_ZERO_HISTOGRAM_DIGEST
    )
    assert audit["registered_obstruction_record_digest_sha256"] == (
        q011ak.EXPECTED_OBSTRUCTION_RECORD_DIGEST
    )


def test_q011ak_seals_both_boundary_witnesses(
    q011ak_cycle: dict[str, Any],
) -> None:
    record = q011ak_cycle["registered_blockwise_obstruction_audit"][
        "registered_obstruction_record"
    ]
    separated = record["minimum_separated_outward_witness"]
    assert separated["block_zero_multiplicity"] == 1
    assert separated["target_identifier"] == "block=11;center=4"
    assert separated["left_index"] == 385
    assert separated["right_index"] == 2
    assert separated["wave_multiplicity"] == 6
    assert separated["outward_gap_hex"] == q011ak.EXPECTED_MINIMUM_SEPARATED_GAP_HEX
    assert record["minimum_separated_outward_witness_digest_sha256"] == (
        q011ak.EXPECTED_MINIMUM_SEPARATED_WITNESS_DIGEST
    )

    unresolved = record["first_unresolved_witness"]
    assert unresolved["block_zero_multiplicity"] == 2
    assert unresolved["target_identifier"] == "block=11;center=3"
    assert unresolved["left_index"] == 0
    assert unresolved["right_index"] == 8
    assert unresolved["wave_multiplicity"] == 14
    assert tuple(unresolved["source_identifiers"]) == (
        q011ak.EXPECTED_FIRST_UNRESOLVED_SOURCES
    )
    assert unresolved["center_gap_hex"] == (
        q011ak.EXPECTED_FIRST_UNRESOLVED_CENTER_GAP_HEX
    )
    width = q011ak.q011z._fraction(unresolved["intersection_interval"]["width"])
    assert width > Fraction(0)
    assert unresolved["intersection_interval"]["width_hex"] == (
        q011ak.EXPECTED_FIRST_UNRESOLVED_INTERSECTION_WIDTH_HEX
    )
    assert record["first_unresolved_witness_digest_sha256"] == (
        q011ak.EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST
    )


def test_q011ak_rejects_only_the_blockwise_certificate(
    q011ak_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011ak_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ak_cycle["hypothesis_gates"].values())
    assert q011ak_cycle["study_validity"] == "passed"
    assert q011ak_cycle["hypothesis_outcome"] == "rejected"
    assert q011ak_cycle["actual_resonance_outcome"] == "not_established"
    assert q011ak_cycle["scientific_classification"] == q011ak.COMBINED_CLASSIFICATION
    theorem = q011ak_cycle["theorem_consequence"]
    assert theorem["q011y_blockwise_transformed_residual_enclosure_is_certified"]
    assert theorem["blockwise_radius_strictly_improves_the_registered_uniform_obstruction"]
    assert theorem[
        "degree_sixteen_blockwise_radius_certificate_is_rejected_at_the_registered_obstruction"
    ]
    assert theorem["block_zero_multiplicity_boundary_is_certified_for_this_aggregate"]
    assert not theorem["remaining_blockwise_overlaps_are_actual_resonances"]
    assert not theorem["an_actual_degree_sixteen_complex_resonance_is_established"]
    assert not theorem["degree_sixteen_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 16))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(16, 91))
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "aggregate-index-99" in q011ak_cycle["claim_boundary"]
    assert "Q011al" in q011ak_cycle["next_change"]


def test_q011ak_cycle_has_strict_reproducible_digests(
    q011ak_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ak_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "710bcb6b724112bcf8f7c6cc166009accb176d325c5f6b2b911621d6a4b0ff42"
        ),
        "radius_digest_sha256": (
            "2c6fc37c40262ba5b76121ca1e3655e1ecd760b88ad27063f932bda532ff62ab"
        ),
        "interval_digest_sha256": (
            "25174294bfe13f1de5124793594bb14702617337d41f69e8ff9b43afd3c12386"
        ),
        "obstruction_digest_sha256": (
            "984f9cd6c4d2db107385e500f64f89e242f2764a826d44f78bb56cbd283e3ec4"
        ),
        "result_digest_sha256": (
            "e95e11a93a688170e0538d16d9956e487dbd5a1e7a9262b823cb60d0e1b0166a"
        ),
    }
    assert {name: q011ak_cycle[name] for name in expected} == expected
    assert q011ak_cycle["result_digest_sha256"] == (
        q011ak.q011b._canonical_json_sha256(
            q011ak._result_digest_sections(q011ak_cycle)
        )
    )


def test_q011ak_study_metadata_and_generated_artifact_are_scoped(
    q011ak_study: dict[str, Any],
) -> None:
    assert q011ak_study["schema_version"] == 1
    assert q011ak_study["source"] == source_metadata()
    assert q011ak_study["study_gate"] == "passed"
    assert q011ak_study["scientific_outcome"] == "rejected"
    assert q011ak_study["actual_resonance_outcome"] == "not_established"
    arithmetic = q011ak_study["arithmetic_runtime"]
    assert arithmetic["floating_point_used_for_gate_decisions"] is True
    assert arithmetic["floating_point_gate_is_rigorous_interval_logic"] is True
    scope = q011ak_study["mathematical_scope"]
    assert scope["aggregate_index"] == 99
    assert scope["blockwise_radius_certificate_claim"] is False
    assert scope["degree_sixteen_external_nonresonance_claim"] is False
    assert scope["actual_complex_resonance_claim"] is False
    assert scope["degrees_17_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ak_study, allow_nan=False)

    runner_path = Path(q011ak.__file__).resolve()
    artifact_path = (
        runner_path.parent / "artifacts" / "q011ak_degree16_blockwise_obstruction.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011ak artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ak.q011b._canonical_json_sha256(
            q011ak._result_digest_sections(artifact["cycle"])
        )
    )
    json.dumps(artifact, allow_nan=False)
