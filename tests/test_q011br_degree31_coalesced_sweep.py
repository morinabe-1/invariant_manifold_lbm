from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011br_degree31_coalesced_sweep as q011br
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "c6e3e6db74ee71421938bf3fd3df760f22480bde6f5d589c576acd634d9b9d02"
EXPECTED_ARTIFACT_SHA256 = "63a5a3cc5076edef2dfeb5e8f0d82cb588b9de4436fbebc57e0e39349b9e1cfe"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "323340a53f85746834f68825a3725eaa525c68aafe2f71c6ba7c87e89a2d2d9b",
    "preparation_digest_sha256": (
        "351c05f98a9eedcd03af8ded5e5dccf4def334c0f6ded7374f6d64a53160514f"
    ),
    "sweep_digest_sha256": "0e4ff2b20ccff36016e289be3eefdc0cd8c7f3e1d711c1189a65e973711c2116",
    "result_digest_sha256": "165f85fff115e56a5f3bfc3b2fe0661b09620d6394267720a165302b38aef5e0",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "a4c528a1ea87fe764e3a74829e1a0995ef406f610308faa780c355a384a4457a"
    ),
    "bound_matrix_digest_sha256": (
        "c6ba13aab5988594a1dab77fa4df9f8f4cef55e6e84ef2f191b86bbefb239663"
    ),
    "coefficient_matrix_digest_sha256": (
        "87cc0f3a6192f5442f508622bc9b2dfdeec4cc864a239b40326e9c6a6fa7ba28"
    ),
    "classification_matrix_digest_sha256": (
        "edc9c18b17bf2a6ffac9414e09e630e7c59ac8bf3eda95fbce22bcf781e8897e"
    ),
}


@pytest.fixture(scope="module")
def q011br_study() -> dict[str, Any]:
    return q011br.run_q011br_study()


@pytest.fixture(scope="module")
def q011br_cycle(q011br_study: dict[str, Any]) -> dict[str, Any]:
    return q011br_study["cycle"]


def test_q011br_seals_q011bq_and_all_prior_inputs(q011br_cycle: dict[str, Any]) -> None:
    sealed = q011br_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 48
    assert sealed["direct_digest_count"] == 230
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bq"]["digests"]) == q011br.Q011BQ_DIGESTS
    assert sealed["q011bq"]["artifact_sha256"] == q011br.Q011BQ_ARTIFACT_SHA256
    assert sealed["q011bq"]["runner_sha256"] == q011br.Q011BQ_RUNNER_SHA256
    assert sealed["q011bq"]["degree_thirty_one_relation_evaluation_count"] == 0


def test_q011br_reconstructs_registered_inputs_bitwise(q011br_cycle: dict[str, Any]) -> None:
    fixed = q011br_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 31
    assert fixed["degree_aggregate_count"] == 5_984
    assert fixed["old_modulus_separated_aggregate_count"] == 3_995
    assert fixed["direct_overlap_aggregate_count"] == 1_989
    assert fixed["multi_target_aggregate_count"] == 8
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 892
    assert fixed["active_identifier_count"] == 916
    assert fixed["monotone_identifier_count"] == 1_032
    assert fixed["inactive_retained_identifier_count"] == 116
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011br.q011bq.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011br.q011bq.EXPECTED_ACTIVE_RECORD_DIGEST
    )

    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011br.q011bq.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011br.q011bq.EXPECTED_HULL_RECORD_DIGEST


def test_q011br_processes_every_registered_aggregate_once(
    q011br_cycle: dict[str, Any],
) -> None:
    sweep = q011br_cycle["degree_thirty_one_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 31
    assert sweep["audited_overlap_aggregate_count"] == 1_989
    assert len(sweep["aggregate_records"]) == 1_989
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(1_989)
    )
    assert sweep["bound_matrix_record_count"] == 1_989
    assert sweep["fully_separated_overlap_aggregate_count"] <= 1_989


def test_q011br_reproduces_preregistered_resource_identities(
    q011br_cycle: dict[str, Any],
) -> None:
    sweep = q011br_cycle["degree_thirty_one_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 186
    assert sweep["group_signature_record_count"] == 1_084
    assert sweep["pair_pool_record_count"] == 626
    assert sweep["convolution_call_count"] == 31_408
    assert sweep["original_monomial_count"] == 364_024_527_216_492
    assert sweep["modulus_signature_count"] == 121_932
    assert sweep["maximum_live_combined_signature_count"] == 272
    assert sweep["distinct_comparison_upper_bound"] == 1_869_852
    assert sweep["weighted_comparison_upper_bound"] == 5_248_950_250_612_032
    assert sweep["maximum_convolution_crude_int64_bound"] <= 33_745_395_640_320
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011br_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 8
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011br_applies_the_preregistered_stopping_rule(
    q011br_cycle: dict[str, Any],
) -> None:
    assert q011br_cycle["study_validity"] == "passed"
    assert q011br_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011br_cycle["validity_gates"].values())
    assert q011br_cycle["scientific_outcome"] == "accepted"
    assert q011br_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011br_cycle["hypothesis_gates"].values())
    sweep = q011br_cycle["degree_thirty_one_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 1_989
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["distinct_comparison_count"] == 1_785_782
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 748_956,
        "target_below_product": 1_036_826,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 307_717_456_383_684
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 159_451_554_446_488,
        "target_below_product": 148_265_901_937_196,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 1_585
    assert minimum["selected_type_counts"] == [13, 12, 5, 1]
    assert minimum["target_identifier"] == "block=8;center=41"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.aeb65657fffffp-24"
    assert minimum["exact_gap_hex"] == "0x1.aeb65961f1c07p-24"
    assert minimum["witness_digest_sha256"] == (
        "81bcf3cfa9c09a5d7db7a81e4954a36000d903444ff046f131d28524894344f1"
    )
    assert q011br_cycle["scientific_classification"] == q011br.ACCEPTED_CLASSIFICATION
    assert q011br_cycle["actual_resonance_outcome"] == q011br.ACCEPTED_ACTUAL_RESONANCE_OUTCOME


def test_q011br_preserves_the_scientific_boundary(q011br_cycle: dict[str, Any]) -> None:
    theorem = q011br_cycle["theorem_consequence"]
    assert theorem["degree_thirty_one_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_thirty_one_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_thirty_one_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 32))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(32, 91))
    assert theorem["q011bp_degree_thirty_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 32--90" in q011br_cycle["claim_boundary"]
    assert (
        "inactive monotone proof records are retained but not compared"
        in q011br_cycle["claim_boundary"]
    )


def test_q011br_cycle_has_strict_reproducible_digests(q011br_cycle: dict[str, Any]) -> None:
    json.dumps(q011br_cycle, allow_nan=False)
    assert {
        name: q011br_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011br_cycle["degree_thirty_one_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011br_cycle["result_digest_sha256"] == q011br.q011b._canonical_json_sha256(
        q011br._result_digest_sections(q011br_cycle)
    )


def test_q011br_study_metadata_and_optional_artifact_are_scoped(
    q011br_study: dict[str, Any],
) -> None:
    assert q011br_study["schema_version"] == 1
    assert q011br_study["source"] == source_metadata()
    assert q011br_study["study_gate"] == "passed"
    assert q011br_study["scientific_outcome"] == "accepted"
    assert q011br_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011br_study["mathematical_scope"]
    assert scope["degree"] == 31
    assert scope["degree_thirty_two_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011br_study, allow_nan=False)

    runner_path = Path(q011br.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011br_degree31_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011br artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011br_degree31_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011br_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011br_study["actual_resonance_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == q011br.q011b._canonical_json_sha256(
        q011br._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
