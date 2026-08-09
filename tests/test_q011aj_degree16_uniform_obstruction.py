from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011aj_degree16_uniform_obstruction as q011aj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011aj_study() -> dict[str, Any]:
    return q011aj.run_q011aj_study()


@pytest.fixture(scope="module")
def q011aj_cycle(q011aj_study: dict[str, Any]) -> dict[str, Any]:
    return q011aj_study["cycle"]


def test_q011aj_seals_q011ai_and_all_prior_inputs(
    q011aj_cycle: dict[str, Any],
) -> None:
    sealed = q011aj_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 73
    assert all(sealed["checks"].values())
    prior = sealed["prior_q011ai_sealed_input_audit"]
    assert prior["passed"]
    assert prior["direct_digest_count"] == 68
    assert tuple(sealed["q011ai"]["digests"]) == q011aj.Q011AI_DIGESTS
    assert sealed["q011ai"]["artifact_sha256"] == q011aj.Q011AI_ARTIFACT_SHA256
    assert sealed["q011ai"]["runner_sha256"] == q011aj.Q011AI_RUNNER_SHA256


def test_q011aj_reconstructs_degree_sixteen_and_the_multi_target_union(
    q011aj_cycle: dict[str, Any],
) -> None:
    audit = q011aj_cycle["degree16_modulus_inventory_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_modulus_aggregate_count"] == 969
    assert audit["degree_expanded_product_control_count"] == 20_349
    assert audit["old_modulus_separated_aggregate_count"] == 815
    assert audit["old_modulus_overlap_aggregate_count"] == 154
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert audit["unique_external_group_indices"] == list(
        q011aj.EXPECTED_EXTERNAL_GROUP_INDICES
    )
    assert audit["unique_external_target_count"] == 136
    assert audit["multi_target_aggregate_indices"] == [73]
    record = audit["overlap_records"][73]
    assert record["selected_type_counts"] == [4, 6, 2, 4]
    assert record["external_group_indices"] == [156, 157]
    assert audit["exact_inventory_digest_sha256"] == q011aj.EXPECTED_INVENTORY_DIGEST


def test_q011aj_extends_the_uniform_envelope_monotonically(
    q011aj_cycle: dict[str, Any],
) -> None:
    audit = q011aj_cycle["uniform_refined_envelope_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["active_selected_group_indices"] == [0, 1, 2, 3]
    assert audit["directly_relevant_identifier_count"] == 160
    assert audit["relevant_identifier_count"] == 204
    assert len(audit["new_external_identifiers"]) == 60
    assert audit["unique_center_modulus_evaluation_count"] == 114
    assert q011aj.q011z._fraction(audit["uniform_radius"]) == Fraction(1, 20_000_000)
    assert audit["checks"]["all_q011ai_144_uniform_records_are_preserved_exactly"]
    assert audit["uniform_record_digest_sha256"] == q011aj.EXPECTED_UNIFORM_RECORD_DIGEST


def test_q011aj_reproduces_the_registered_stopping_prefix(
    q011aj_cycle: dict[str, Any],
) -> None:
    compression = q011aj_cycle["fourier_modulus_compression_audit"]
    assert compression["passed"]
    assert all(compression["checks"].values())
    assert compression["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert compression["class_membership_digest_sha256"] == (
        q011aj.q011ai.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )
    audit = q011aj_cycle["first_uniform_envelope_obstruction_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["scanned_prefix_count"] == 100
    assert len(audit["prefix_records"]) == 100
    assert all(
        record["has_outward_separated_comparison"]
        for record in audit["prefix_records"][:-1]
    )
    assert not audit["prefix_records"][-1]["has_outward_separated_comparison"]
    assert audit["prefix_digest_sha256"] == q011aj.EXPECTED_PREFIX_DIGEST
    assert audit["maximum_wave_coefficient"] == 1_142
    assert audit["maximum_crude_int64_dot_product_bound"] == 7_140
    assert audit["maximum_live_signature_count"] == 900_900


def test_q011aj_certifies_the_first_uniform_envelope_obstruction(
    q011aj_cycle: dict[str, Any],
) -> None:
    audit = q011aj_cycle["first_uniform_envelope_obstruction_audit"]
    record = audit["first_fully_unresolved_aggregate"]
    assert record["aggregate_index"] == 99
    assert record["selected_type_counts"] == [5, 6, 4, 1]
    assert record["external_group_indices"] == [155]
    assert record["target_identifier_count"] == 4
    assert record["modulus_signature_count"] == 35_280
    assert record["compatible_modulus_signature_count"] == 35_280
    assert record["compatible_original_monomial_count"] == 1_732_864
    assert record["weighted_comparison_count"] == 3_465_728
    assert record["distinct_comparison_count"] == 141_120
    assert record["weighted_relation_counts"] == {
        "overlap": 3_465_728,
        "product_below_target": 0,
        "target_below_product": 0,
    }
    assert record["distinct_relation_counts"] == {
        "overlap": 141_120,
        "product_below_target": 0,
        "target_below_product": 0,
    }
    assert audit["first_obstruction_record_digest_sha256"] == (
        q011aj.EXPECTED_OBSTRUCTION_DIGEST
    )


def test_q011aj_separates_all_center_comparisons_without_promoting_them(
    q011aj_cycle: dict[str, Any],
) -> None:
    audit = q011aj_cycle["center_only_counterdiagnostic_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(audit["center_target_records"]) == 4
    for record in audit["center_target_records"]:
        assert record["active_distinct"] == 35_280
        assert record["product_below_distinct"] == 35_280
        assert record["target_below_distinct"] == 0
        assert record["overlap_distinct"] == 0
    assert audit["center_target_record_digest_sha256"] == (
        q011aj.EXPECTED_CENTER_RECORD_DIGEST
    )
    assert len(audit["exact_candidate_records"]) == 28
    assert audit["exact_candidate_record_digest_sha256"] == (
        q011aj.EXPECTED_EXACT_CENTER_CANDIDATE_DIGEST
    )
    assert audit["exact_center_minimum_hex"] == q011aj.EXPECTED_EXACT_CENTER_MINIMUM_HEX
    assert audit["exact_center_minimum_tie_count"] == 2


def test_q011aj_exact_witness_distinguishes_center_gap_from_disc_intersection(
    q011aj_cycle: dict[str, Any],
) -> None:
    audit = q011aj_cycle["center_only_counterdiagnostic_audit"]
    witness = audit["uniform_intersection_witness"]
    canonical = witness["canonical_center_minimum"]
    assert canonical["target_identifier"] == "block=11;center=4"
    assert canonical["output_block"] == 11
    assert canonical["left_index"] == 385
    assert canonical["right_index"] == 2
    assert canonical["wave_multiplicity"] == 6
    assert canonical["relation"] == "product_below_target"
    assert tuple(tuple(group) for group in canonical["class_counts"]) == (
        q011aj.EXPECTED_CANONICAL_CLASS_COUNTS
    )
    assert tuple(witness["source_identifiers"]) == (
        q011aj.EXPECTED_CANONICAL_SOURCE_IDENTIFIERS
    )
    assert q011aj.q011z._fraction(witness["exact_center_minimum"]) > 0
    intersection = witness["uniform_intersection_interval"]
    width = q011aj.q011z._fraction(intersection["width"])
    assert width > Fraction(1, 10**7)
    excess = width - Fraction(1, 10**7)
    assert float(excess).hex() == q011aj.EXPECTED_UNIFORM_INTERSECTION_EXCESS_HEX
    assert q011aj.q011b._canonical_json_sha256(
        q011aj.q011z._exact_fraction_record(excess)
    ) == q011aj.EXPECTED_UNIFORM_INTERSECTION_EXCESS_DIGEST
    assert intersection["width_hex"] == q011aj.EXPECTED_UNIFORM_INTERSECTION_WIDTH_HEX
    assert audit["uniform_intersection_witness_digest_sha256"] == (
        q011aj.EXPECTED_WITNESS_DIGEST
    )


def test_q011aj_rejects_only_the_uniform_certificate(
    q011aj_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011aj_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011aj_cycle["hypothesis_gates"].values())
    assert q011aj_cycle["study_validity"] == "passed"
    assert q011aj_cycle["hypothesis_outcome"] == "rejected"
    assert q011aj_cycle["actual_resonance_outcome"] == "not_established"
    assert q011aj_cycle["scientific_classification"] == q011aj.COMBINED_CLASSIFICATION
    theorem = q011aj_cycle["theorem_consequence"]
    assert theorem["degree_sixteen_uniform_rho_external_nonresonance_certificate_is_rejected"]
    assert theorem["first_fully_unresolved_aggregate_is_certified"]
    assert theorem["center_only_obstruction_comparisons_are_separated"]
    assert not theorem["center_only_separation_is_an_actual_spectrum_certificate"]
    assert not theorem["an_actual_degree_sixteen_complex_resonance_is_established"]
    assert not theorem["degree_sixteen_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 16))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(16, 91))
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "fixed 17x17" in q011aj_cycle["claim_boundary"]
    assert "Q011ak" in q011aj_cycle["next_change"]


def test_q011aj_cycle_has_strict_reproducible_digests(
    q011aj_cycle: dict[str, Any],
) -> None:
    json.dumps(q011aj_cycle, allow_nan=False)
    for name in (
        "input_digest_sha256",
        "inventory_digest_sha256",
        "obstruction_digest_sha256",
        "center_digest_sha256",
        "result_digest_sha256",
    ):
        assert len(q011aj_cycle[name]) == 64
        int(q011aj_cycle[name], 16)
    assert q011aj_cycle["result_digest_sha256"] == q011aj.q011b._canonical_json_sha256(
        q011aj._result_digest_sections(q011aj_cycle)
    )


def test_q011aj_study_metadata_and_generated_artifact_are_scoped(
    q011aj_study: dict[str, Any],
) -> None:
    assert q011aj_study["schema_version"] == 1
    assert q011aj_study["source"] == source_metadata()
    assert q011aj_study["study_gate"] == "passed"
    assert q011aj_study["scientific_outcome"] == "rejected"
    assert q011aj_study["actual_resonance_outcome"] == "not_established"
    arithmetic = q011aj_study["arithmetic_runtime"]
    assert arithmetic["floating_point_used_for_gate_decisions"] is True
    assert arithmetic["floating_point_gate_is_rigorous_interval_logic"] is True
    scope = q011aj_study["mathematical_scope"]
    assert scope["uniform_rho_certificate_claim"] is False
    assert scope["degree_sixteen_external_nonresonance_claim"] is False
    assert scope["actual_complex_resonance_claim"] is False
    assert scope["degrees_17_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011aj_study, allow_nan=False)

    runner_path = Path(q011aj.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011aj_degree16_uniform_obstruction.json"
    if not artifact_path.exists():
        pytest.skip("Q011aj artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011aj.q011b._canonical_json_sha256(
            q011aj._result_digest_sections(artifact["cycle"])
        )
    )
    json.dumps(artifact, allow_nan=False)
