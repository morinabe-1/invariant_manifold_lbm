from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bn_degree29_coalesced_sweep as q011bn
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "51300c89409410c45db678bb70801e0c974990ab4f8097cc2ea002dcc2a2e236"
EXPECTED_ARTIFACT_SHA256 = "a648d594c2e37a75666628ea060b364cec37c5902dd412285b2499aeb23ab78d"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "e02a2468a57cbcee6c852c3f05415f1b5742fe61e380fe03ea5986defecf3d31",
    "preparation_digest_sha256": (
        "08edb42c612411d32a4cbb1c3da80f7f309e143f602fc80b2756fae520c44d60"
    ),
    "sweep_digest_sha256": "f2ae412d3504c1823360b9fd62f1c55ad1859470a38aa897025f3df0969504bf",
    "result_digest_sha256": "fdcd23a9310d8272cd5df248431d177b5925c0432a4f97ec21855f7928a523da",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "974b08b0cc54ce7adda1cc23ace87b7d6b200d51daffedb305925e0446b8b625"
    ),
    "bound_matrix_digest_sha256": (
        "708820edd22a0cb525d3ba444f30200d873642d782d03015c29d56339de933e2"
    ),
    "coefficient_matrix_digest_sha256": (
        "8695e1c80ec97038d4be8346da85c4958e0585c3885ec2467bb39eae9f8cf6fc"
    ),
    "classification_matrix_digest_sha256": (
        "e13d3b9a6493c87f2b8f9e2175c320a110610ee28a1990ad8bec10982ba4361c"
    ),
}


@pytest.fixture(scope="module")
def q011bn_study() -> dict[str, Any]:
    return q011bn.run_q011bn_study()


@pytest.fixture(scope="module")
def q011bn_cycle(q011bn_study: dict[str, Any]) -> dict[str, Any]:
    return q011bn_study["cycle"]


def test_q011bn_seals_q011bm_and_all_prior_inputs(q011bn_cycle: dict[str, Any]) -> None:
    sealed = q011bn_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 44
    assert sealed["direct_digest_count"] == 212
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bm"]["digests"]) == q011bn.Q011BM_DIGESTS
    assert sealed["q011bm"]["artifact_sha256"] == q011bn.Q011BM_ARTIFACT_SHA256
    assert sealed["q011bm"]["runner_sha256"] == q011bn.Q011BM_RUNNER_SHA256
    assert sealed["q011bm"]["degree_twenty_nine_relation_evaluation_count"] == 0


def test_q011bn_reconstructs_registered_inputs_bitwise(q011bn_cycle: dict[str, Any]) -> None:
    fixed = q011bn_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 29
    assert fixed["degree_aggregate_count"] == 4_960
    assert fixed["old_modulus_separated_aggregate_count"] == 3_563
    assert fixed["direct_overlap_aggregate_count"] == 1_397
    assert fixed["multi_target_aggregate_count"] == 3
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 684
    assert fixed["active_identifier_count"] == 708
    assert fixed["monotone_identifier_count"] == 808
    assert fixed["inactive_retained_identifier_count"] == 100
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bn.q011bm.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bn.q011bm.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bn.q011bm.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bn.q011bm.EXPECTED_HULL_RECORD_DIGEST


def test_q011bn_processes_every_registered_aggregate_once(
    q011bn_cycle: dict[str, Any],
) -> None:
    sweep = q011bn_cycle["degree_twenty_nine_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 29
    assert sweep["audited_overlap_aggregate_count"] == 1_397
    assert len(sweep["aggregate_records"]) == 1_397
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(1_397)
    )
    assert sweep["bound_matrix_record_count"] == 1_397
    assert sweep["fully_separated_overlap_aggregate_count"] <= 1_397


def test_q011bn_reproduces_preregistered_resource_identities(
    q011bn_cycle: dict[str, Any],
) -> None:
    sweep = q011bn_cycle["degree_twenty_nine_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 173
    assert sweep["group_signature_record_count"] == 928
    assert sweep["pair_pool_record_count"] == 465
    assert sweep["convolution_call_count"] == 18_653
    assert sweep["original_monomial_count"] == 104_792_593_656_144
    assert sweep["modulus_signature_count"] == 75_504
    assert sweep["maximum_live_combined_signature_count"] == 210
    assert sweep["distinct_comparison_upper_bound"] == 1_254_872
    assert sweep["weighted_comparison_upper_bound"] == 1_742_501_892_291_632
    assert sweep["maximum_convolution_crude_int64_bound"] <= 12_888_866_390_400
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bn_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 3
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bn_applies_the_preregistered_stopping_rule(
    q011bn_cycle: dict[str, Any],
) -> None:
    assert q011bn_cycle["study_validity"] == "passed"
    assert q011bn_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bn_cycle["validity_gates"].values())
    assert q011bn_cycle["scientific_outcome"] == "accepted"
    assert q011bn_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bn_cycle["hypothesis_gates"].values())
    sweep = q011bn_cycle["degree_twenty_nine_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 1_397
    assert sweep["distinct_comparison_count"] == 1_179_356
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 513_292,
        "target_below_product": 666_064,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 102_976_446_197_590
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 47_839_692_143_362,
        "target_below_product": 55_136_754_054_228,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 1_111
    assert minimum["selected_type_counts"] == [12, 14, 1, 2]
    assert minimum["target_identifier"] == "block=12;center=143"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.5271cf21fffffp-21"
    assert minimum["exact_gap_hex"] == "0x1.5271cf8295befp-21"
    assert minimum["witness_digest_sha256"] == (
        "cb82da3e1b34fb34371ba33b35fcf1c506b33732d020f6a432c0889068387f53"
    )
    assert q011bn_cycle["scientific_classification"] == q011bn.ACCEPTED_CLASSIFICATION
    assert (
        q011bn_cycle["actual_resonance_outcome"]
        == q011bn.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011bn_preserves_the_scientific_boundary(q011bn_cycle: dict[str, Any]) -> None:
    theorem = q011bn_cycle["theorem_consequence"]
    assert theorem["degree_twenty_nine_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_twenty_nine_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_twenty_nine_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 30))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(30, 91))
    assert theorem["q011bl_degree_twenty_eight_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 30--90" in q011bn_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bn_cycle[
        "claim_boundary"
    ]


def test_q011bn_cycle_has_strict_reproducible_digests(q011bn_cycle: dict[str, Any]) -> None:
    json.dumps(q011bn_cycle, allow_nan=False)
    assert {
        name: q011bn_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bn_cycle["degree_twenty_nine_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bn_cycle["result_digest_sha256"] == q011bn.q011b._canonical_json_sha256(
        q011bn._result_digest_sections(q011bn_cycle)
    )


def test_q011bn_study_metadata_and_optional_artifact_are_scoped(
    q011bn_study: dict[str, Any],
) -> None:
    assert q011bn_study["schema_version"] == 1
    assert q011bn_study["source"] == source_metadata()
    assert q011bn_study["study_gate"] == "passed"
    assert q011bn_study["scientific_outcome"] == "accepted"
    assert q011bn_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bn_study["mathematical_scope"]
    assert scope["degree"] == 29
    assert scope["degree_thirty_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bn_study, allow_nan=False)

    runner_path = Path(q011bn.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bn_degree29_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bn artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bn_degree29_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bn_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bn_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bn.q011b._canonical_json_sha256(
        q011bn._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
