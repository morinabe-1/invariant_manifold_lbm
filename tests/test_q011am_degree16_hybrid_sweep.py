from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011am_degree16_hybrid_sweep as q011am
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011am_study() -> dict[str, Any]:
    return q011am.run_q011am_study()


@pytest.fixture(scope="module")
def q011am_cycle(q011am_study: dict[str, Any]) -> dict[str, Any]:
    return q011am_study["cycle"]


def test_q011am_seals_q011al_and_all_prior_inputs(
    q011am_cycle: dict[str, Any],
) -> None:
    sealed = q011am_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 88
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011al_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 83
    assert tuple(sealed["q011al"]["digests"]) == q011am.Q011AL_DIGESTS
    assert sealed["q011al"]["artifact_sha256"] == q011am.Q011AL_ARTIFACT_SHA256
    assert sealed["q011al"]["runner_sha256"] == q011am.Q011AL_RUNNER_SHA256


def test_q011am_reconstructs_the_hybrid_inventory(
    q011am_cycle: dict[str, Any],
) -> None:
    audit = q011am_cycle["hybrid_input_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["hybrid_identifier_count"] == 204
    assert audit["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert audit["old_modulus_separated_aggregate_count"] == 815
    assert audit["old_modulus_overlap_aggregate_count"] == 154
    assert audit["hybrid_record_digest_sha256"] == (q011am.q011al.EXPECTED_HYBRID_RECORD_DIGEST)


def test_q011am_hierarchical_integer_factorization_is_exact(
    q011am_cycle: dict[str, Any],
) -> None:
    sweep = q011am_cycle["hierarchical_degree_sixteen_sweep_audit"]
    assert sweep["class_power_record_count"] == q011am.EXPECTED_CLASS_POWER_COUNT
    assert sweep["class_power_record_digest_sha256"] == (q011am.EXPECTED_CLASS_POWER_DIGEST)
    assert sweep["group_signature_record_count"] == (q011am.EXPECTED_GROUP_SIGNATURE_COUNT)
    assert sweep["group_signature_digest_sha256"] == (q011am.EXPECTED_GROUP_SIGNATURE_DIGEST)
    assert sweep["pair_pool_record_count"] == q011am.EXPECTED_PAIR_POOL_COUNT
    assert sweep["pair_pool_record_digest_sha256"] == (q011am.EXPECTED_PAIR_POOL_DIGEST)
    assert sweep["convolution_call_count"] == (q011am.EXPECTED_CONVOLUTION_CALL_COUNT)
    assert sweep["maximum_convolution_crude_int64_bound"] == (
        q011am.EXPECTED_MAXIMUM_CONVOLUTION_CRUDE_BOUND
    )
    assert sweep["all_convolutions_nonnegative"]
    assert sweep["all_convolution_fiber_sums_exact"]
    assert sweep["all_original_monomial_counts_match_multiset_coefficients"]
    assert sweep["all_modulus_signature_counts_match_weak_compositions"]


def test_q011am_classifies_all_registered_comparisons(
    q011am_cycle: dict[str, Any],
) -> None:
    sweep = q011am_cycle["hierarchical_degree_sixteen_sweep_audit"]
    assert sweep["audited_overlap_aggregate_count"] == 154
    assert sweep["original_monomial_count"] == q011am.EXPECTED_ORIGINAL_MONOMIAL_COUNT
    assert sweep["modulus_signature_count"] == q011am.EXPECTED_MODULUS_SIGNATURE_COUNT
    assert sweep["compatible_modulus_signature_count"] == (
        q011am.EXPECTED_COMPATIBLE_SIGNATURE_COUNT
    )
    assert sweep["compatible_original_monomial_count"] == (
        q011am.EXPECTED_COMPATIBLE_MONOMIAL_COUNT
    )
    assert sweep["weighted_comparison_count"] == (q011am.EXPECTED_WEIGHTED_COMPARISON_COUNT)
    assert sweep["distinct_comparison_count"] == (q011am.EXPECTED_DISTINCT_COMPARISON_COUNT)
    assert sweep["weighted_relation_counts"] == q011am.EXPECTED_WEIGHTED_RELATIONS
    assert sweep["distinct_relation_counts"] == q011am.EXPECTED_DISTINCT_RELATIONS
    assert sweep["aggregate_record_digest_sha256"] == q011am.EXPECTED_AGGREGATE_DIGEST
    assert sweep["bound_matrix_digest_sha256"] == q011am.EXPECTED_BOUND_MATRIX_DIGEST
    assert sweep["coefficient_matrix_digest_sha256"] == (q011am.EXPECTED_COEFFICIENT_MATRIX_DIGEST)
    assert sweep["classification_matrix_digest_sha256"] == (
        q011am.EXPECTED_CLASSIFICATION_MATRIX_DIGEST
    )


def test_q011am_leaves_only_aggregate_fifty_five_overlapping(
    q011am_cycle: dict[str, Any],
) -> None:
    sweep = q011am_cycle["hierarchical_degree_sixteen_sweep_audit"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 153
    assert sweep["remaining_overlap_aggregate_count"] == 1
    assert sweep["remaining_overlap_aggregate_indices"] == [55]
    record = sweep["aggregate_records"][55]
    assert tuple(record["selected_type_counts"]) == q011am.EXPECTED_OBSTRUCTION_COUNTS
    assert record["target_identifier_count"] == q011am.EXPECTED_OBSTRUCTION_TARGET_COUNT
    assert record["weighted_relation_counts"] == (q011am.EXPECTED_OBSTRUCTION_WEIGHTED_RELATIONS)
    assert record["distinct_relation_counts"] == (q011am.EXPECTED_OBSTRUCTION_DISTINCT_RELATIONS)
    assert q011am.q011b._canonical_json_sha256(record) == (
        q011am.EXPECTED_OBSTRUCTION_RECORD_DIGEST
    )


def test_q011am_seals_the_unresolved_and_positive_witnesses(
    q011am_cycle: dict[str, Any],
) -> None:
    sweep = q011am_cycle["hierarchical_degree_sixteen_sweep_audit"]
    first = sweep["first_unresolved_witness"]
    assert first["aggregate_index"] == 55
    assert first["target_identifier"] == "block=13;center=114"
    assert first["block_zero_multiplicity"] == 0
    assert tuple(tuple(group) for group in first["class_counts"]) == (
        q011am.EXPECTED_FIRST_UNRESOLVED_COUNTS
    )
    assert tuple(first["source_identifiers"]) == q011am.EXPECTED_FIRST_UNRESOLVED_SOURCES
    assert first["intersection_interval"]["width_hex"] == (
        q011am.EXPECTED_FIRST_INTERSECTION_WIDTH_HEX
    )
    assert q011am.q011z._fraction(first["intersection_interval"]["width"]) > Fraction(0)
    assert first["center_only_diagnostic"]["relation"] == "product_below_target"
    assert first["center_only_diagnostic"]["gap_hex"] == (q011am.EXPECTED_FIRST_CENTER_GAP_HEX)
    assert first["witness_digest_sha256"] == (q011am.EXPECTED_FIRST_UNRESOLVED_WITNESS_DIGEST)

    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 99
    assert minimum["outward_gap_lower"]["binary64_hex"] == (q011am.EXPECTED_GLOBAL_MINIMUM_GAP_HEX)
    assert minimum["exact_gap_hex"] == q011am.EXPECTED_GLOBAL_EXACT_GAP_HEX
    assert minimum["witness_digest_sha256"] == q011am.EXPECTED_GLOBAL_WITNESS_DIGEST


def test_q011am_reproduces_q011aj_and_q011al_bridges(
    q011am_cycle: dict[str, Any],
) -> None:
    bridge = q011am_cycle["q011aj_prefix_and_q011al_clearance_bridge_audit"]
    assert bridge["passed"]
    assert all(bridge["checks"].values())
    assert bridge["q011aj_prefix_record_count"] == 100
    assert bridge["q011aj_prefix_bridge_digest_sha256"] == (
        "2b68f90194319e0dc8d062f876e4b6f1b7c949248c941f794edbd78676d142d5"
    )
    assert bridge["q011al_registered_aggregate_index"] == 99
    assert bridge["q011al_hierarchical_outward_gap_hex"] == (q011am.EXPECTED_GLOBAL_MINIMUM_GAP_HEX)


def test_q011am_rejects_only_the_registered_hybrid_certificate(
    q011am_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011am_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011am_cycle["hypothesis_gates"].values())
    assert q011am_cycle["study_validity"] == "passed"
    assert q011am_cycle["hypothesis_outcome"] == "rejected"
    assert q011am_cycle["actual_resonance_outcome"] == "not_established"
    assert q011am_cycle["scientific_classification"] == q011am.REJECTED_CLASSIFICATION
    theorem = q011am_cycle["theorem_consequence"]
    assert theorem["q011al_hybrid_eigendisc_inclusion_is_preserved"]
    assert theorem["newly_fully_separated_overlap_aggregate_count"] == 153
    assert theorem["aggregate_fifty_five_is_the_sole_remaining_interval_obstruction"]
    assert theorem["six_source_hybrid_degree_sixteen_certificate_is_rejected"]
    assert not theorem["degree_sixteen_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_sixteen_complex_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 16))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(16, 91))
    assert "sole aggregate-55 interval overlap" in q011am_cycle["claim_boundary"]
    assert "Q011an" in q011am_cycle["next_change"]


def test_q011am_cycle_has_strict_reproducible_digests(
    q011am_cycle: dict[str, Any],
) -> None:
    json.dumps(q011am_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("5378793ad9b9f0f681fbcf145e10a32ec217939ab4daa5f5014b1ba0d7b465ba"),
        "factorization_digest_sha256": (
            "894ad9beb5d5bbd6bf72d3f82b8c303d669d7dc344ce044c4651af20e499d5f1"
        ),
        "enumeration_digest_sha256": (
            "24a2c1bd3efd8a9d82c25323c4c379b727c022dc2af084cf1e949bd1bade614c"
        ),
        "obstruction_digest_sha256": (
            "ce39bfbc7ef0de8320782de9b8108408cac5359524d9b3ab8339d3be9518dc6d"
        ),
        "result_digest_sha256": (
            "1daa072b1a92ed2582a44cde106fa9dc06697d39b6985f99ca9643409d1285a8"
        ),
    }
    assert {name: q011am_cycle[name] for name in expected} == expected
    assert q011am_cycle["result_digest_sha256"] == (
        q011am.q011b._canonical_json_sha256(q011am._result_digest_sections(q011am_cycle))
    )


def test_q011am_study_metadata_and_generated_artifact_are_scoped(
    q011am_study: dict[str, Any],
) -> None:
    assert q011am_study["schema_version"] == 1
    assert q011am_study["source"] == source_metadata()
    assert q011am_study["study_gate"] == "passed"
    assert q011am_study["scientific_outcome"] == "rejected"
    assert q011am_study["actual_resonance_outcome"] == "not_established"
    scope = q011am_study["mathematical_scope"]
    assert scope["audited_overlap_aggregate_count"] == 154
    assert scope["registered_hybrid_certificate_claim"] is True
    assert scope["degree_sixteen_external_nonresonance_claim"] is False
    assert scope["actual_complex_resonance_claim"] is False
    assert scope["degrees_17_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011am_study, allow_nan=False)

    runner_path = Path(q011am.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011am_degree16_hybrid_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011am artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert _file_sha256(artifact_path) == (
        "c4808edd49dec80cb613834d829b6f411c516838f7183c13f6a1e01371cf8f51"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011am_degree16_hybrid_sweep.py",
        "sha256": "c703511110165f66ebcc24ddb93b309c94a2e7b8e7e7372d4fa492e54ee25e53",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011am.q011b._canonical_json_sha256(q011am._result_digest_sections(artifact["cycle"]))
    )
    json.dumps(artifact, allow_nan=False)
