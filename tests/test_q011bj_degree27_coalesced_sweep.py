from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bj_degree27_coalesced_sweep as q011bj
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "ebc93c5114b9b96f7cdff5b764119e08f14575c616c3427b30cc4de7be41349b"
EXPECTED_ARTIFACT_SHA256 = "e3ac46e0e44fb4138980ddecfa5a41d65c0ebadfa5755e936281f0157152ff3e"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "7ac35285a7ada2fb49dd682f19f00a47409cc787df38efd161f71a2f7a14a97a",
    "preparation_digest_sha256": (
        "487e461a87c3ff5348bec8a7d2a9aa2edf6a0cf395d75621cadbb1488eac794d"
    ),
    "sweep_digest_sha256": "c03d4005541cd1d2ebb6479cfb141cac890c54b61df600e7cfaa7f5ae4f097e1",
    "result_digest_sha256": "39d7e3966f6369077d7de9d1ad0838a40be14ac68c53cbb5fb2a1c6a1a8b19fc",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "e6933afdca13059928dab12a82fb972d1562ec32ffa41c3a4d6ee94415e0f3f1"
    ),
    "bound_matrix_digest_sha256": (
        "48709bca4cc1f09abaf22b17a4db00cb0da3ef60f58b1224fcda8868a4e33dde"
    ),
    "coefficient_matrix_digest_sha256": (
        "aca12bc21c171b413340e670cbbd15ef682af26864ef5c88b05826d0d8acae8b"
    ),
    "classification_matrix_digest_sha256": (
        "dfcf3675643745a1e5dd8b192c40b658025d76596ebb9d58ba13a0ba0a38bbee"
    ),
}


@pytest.fixture(scope="module")
def q011bj_study() -> dict[str, Any]:
    return q011bj.run_q011bj_study()


@pytest.fixture(scope="module")
def q011bj_cycle(q011bj_study: dict[str, Any]) -> dict[str, Any]:
    return q011bj_study["cycle"]


def test_q011bj_seals_q011bi_and_all_prior_inputs(q011bj_cycle: dict[str, Any]) -> None:
    sealed = q011bj_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 40
    assert sealed["direct_digest_count"] == 194
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bi"]["digests"]) == q011bj.Q011BI_DIGESTS
    assert sealed["q011bi"]["artifact_sha256"] == q011bj.Q011BI_ARTIFACT_SHA256
    assert sealed["q011bi"]["runner_sha256"] == q011bj.Q011BI_RUNNER_SHA256
    assert sealed["q011bi"]["degree_twenty_seven_relation_evaluation_count"] == 0


def test_q011bj_reconstructs_registered_inputs_bitwise(q011bj_cycle: dict[str, Any]) -> None:
    fixed = q011bj_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 27
    assert fixed["degree_aggregate_count"] == 4_060
    assert fixed["old_modulus_separated_aggregate_count"] == 3_101
    assert fixed["direct_overlap_aggregate_count"] == 959
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 488
    assert fixed["active_identifier_count"] == 512
    assert fixed["monotone_identifier_count"] == 604
    assert fixed["inactive_retained_identifier_count"] == 92
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bj.q011bi.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bj.q011bi.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bj.q011bi.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bj.q011bi.EXPECTED_HULL_RECORD_DIGEST


def test_q011bj_processes_every_registered_aggregate_once(
    q011bj_cycle: dict[str, Any],
) -> None:
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 27
    assert sweep["audited_overlap_aggregate_count"] == 959
    assert len(sweep["aggregate_records"]) == 959
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(959)
    )
    assert sweep["bound_matrix_record_count"] == 959
    assert sweep["fully_separated_overlap_aggregate_count"] <= 959


def test_q011bj_reproduces_preregistered_resource_identities(
    q011bj_cycle: dict[str, Any],
) -> None:
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 154
    assert sweep["group_signature_record_count"] == 705
    assert sweep["pair_pool_record_count"] == 341
    assert sweep["convolution_call_count"] == 11_649
    assert sweep["original_monomial_count"] == 25_561_324_661_692
    assert sweep["modulus_signature_count"] == 43_285
    assert sweep["maximum_live_combined_signature_count"] == 180
    assert sweep["distinct_comparison_upper_bound"] == 763_404
    assert sweep["weighted_comparison_upper_bound"] == 502_998_748_050_560
    assert sweep["maximum_convolution_crude_int64_bound"] <= 4_633_252_624_000
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bj_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bj_applies_the_preregistered_stopping_rule(
    q011bj_cycle: dict[str, Any],
) -> None:
    assert q011bj_cycle["study_validity"] == "passed"
    assert q011bj_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bj_cycle["validity_gates"].values())
    assert q011bj_cycle["scientific_outcome"] == "accepted"
    assert q011bj_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bj_cycle["hypothesis_gates"].values())
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 959
    assert sweep["distinct_comparison_count"] == 707_186
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 316_264,
        "target_below_product": 390_922,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 29_993_903_701_818
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 14_443_886_576_412,
        "target_below_product": 15_550_017_125_406,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 272
    assert minimum["selected_type_counts"] == [3, 1, 0, 23]
    assert minimum["target_identifier"] == "block=15;center=114"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.066c1647fffffp-20"
    assert minimum["exact_gap_hex"] == "0x1.066c167e0f62bp-20"
    assert minimum["witness_digest_sha256"] == (
        "4818ab08768314689e9c469d894ea496887b7c418d8f8d2dbf41a64a66a0146e"
    )
    assert q011bj_cycle["scientific_classification"] == q011bj.ACCEPTED_CLASSIFICATION
    assert (
        q011bj_cycle["actual_resonance_outcome"]
        == q011bj.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011bj_preserves_the_scientific_boundary(q011bj_cycle: dict[str, Any]) -> None:
    theorem = q011bj_cycle["theorem_consequence"]
    assert theorem["degree_twenty_seven_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_twenty_seven_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_twenty_seven_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 28))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(28, 91))
    assert theorem["q011bh_degree_twenty_six_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 28--90" in q011bj_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bj_cycle[
        "claim_boundary"
    ]


def test_q011bj_cycle_has_strict_reproducible_digests(q011bj_cycle: dict[str, Any]) -> None:
    json.dumps(q011bj_cycle, allow_nan=False)
    assert {
        name: q011bj_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bj_cycle["degree_twenty_seven_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bj_cycle["result_digest_sha256"] == q011bj.q011b._canonical_json_sha256(
        q011bj._result_digest_sections(q011bj_cycle)
    )


def test_q011bj_study_metadata_and_optional_artifact_are_scoped(
    q011bj_study: dict[str, Any],
) -> None:
    assert q011bj_study["schema_version"] == 1
    assert q011bj_study["source"] == source_metadata()
    assert q011bj_study["study_gate"] == "passed"
    assert q011bj_study["scientific_outcome"] == "accepted"
    assert q011bj_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bj_study["mathematical_scope"]
    assert scope["degree"] == 27
    assert scope["degree_twenty_eight_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bj_study, allow_nan=False)

    runner_path = Path(q011bj.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bj_degree27_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bj artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bj_degree27_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bj_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bj_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bj.q011b._canonical_json_sha256(
        q011bj._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
