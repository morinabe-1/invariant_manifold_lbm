from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bb_degree23_coalesced_sweep as q011bb
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "f1602a3ef6199fd08d821c07c81364ca75040335210bf076151cbf5a18afc63d"
EXPECTED_ARTIFACT_SHA256 = "bd89978432eaf2f5203b9f8cf6a06e7ca1b07cee55eb63cd967e589ed390c8c9"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "8d88eaecd1a711eb0732453df55c688fd148888faf06c95352b004c6f85d0f82",
    "preparation_digest_sha256": (
        "ce253864c388d80fff70620a5acf965c5003b5f26e5ce26f6fa8ee8065a2ad77"
    ),
    "sweep_digest_sha256": "34ee1fd45e880b4676212122515ef87ab4a8dce7906695e702a3fe4fc738c8eb",
    "result_digest_sha256": "eb85fac8d6fffa1cf1262f8519666bc79eeeda160f03a7e4de0c6f0f004657fe",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "a9a15fc1cf3dcc396b09e84d1729dec81b56c2f1741c7e041f9eb73ae1a6a1d3"
    ),
    "bound_matrix_digest_sha256": (
        "53cc8cc95a7185b9f47f62a2dbaacb1a27e15154e4a2b058b7f326b60fd5d2b9"
    ),
    "coefficient_matrix_digest_sha256": (
        "2674524adcbee42508d5437ed2b33f03459627e0df817001b5375559b84d9446"
    ),
    "classification_matrix_digest_sha256": (
        "43c206175ddd975d725609e0878700009d56ce26f9b55197265a80d2c9dfb56e"
    ),
}


@pytest.fixture(scope="module")
def q011bb_study() -> dict[str, Any]:
    return q011bb.run_q011bb_study()


@pytest.fixture(scope="module")
def q011bb_cycle(q011bb_study: dict[str, Any]) -> dict[str, Any]:
    return q011bb_study["cycle"]


def test_q011bb_seals_q011ba_and_all_prior_inputs(q011bb_cycle: dict[str, Any]) -> None:
    sealed = q011bb_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 32
    assert sealed["direct_digest_count"] == 158
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ba"]["digests"]) == q011bb.Q011BA_DIGESTS
    assert sealed["q011ba"]["artifact_sha256"] == q011bb.Q011BA_ARTIFACT_SHA256
    assert sealed["q011ba"]["runner_sha256"] == q011bb.Q011BA_RUNNER_SHA256
    assert sealed["q011ba"]["degree_twenty_three_relation_evaluation_count"] == 0


def test_q011bb_reconstructs_registered_inputs_bitwise(q011bb_cycle: dict[str, Any]) -> None:
    fixed = q011bb_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 23
    assert fixed["degree_aggregate_count"] == 2_600
    assert fixed["old_modulus_separated_aggregate_count"] == 2_161
    assert fixed["direct_overlap_aggregate_count"] == 439
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 300
    assert fixed["active_identifier_count"] == 324
    assert fixed["monotone_identifier_count"] == 356
    assert fixed["inactive_retained_identifier_count"] == 32
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bb.q011ba.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bb.q011ba.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bb.q011ba.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bb.q011ba.EXPECTED_HULL_RECORD_DIGEST


def test_q011bb_processes_every_registered_aggregate_once(
    q011bb_cycle: dict[str, Any],
) -> None:
    sweep = q011bb_cycle["degree_twenty_three_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 23
    assert sweep["audited_overlap_aggregate_count"] == 439
    assert len(sweep["aggregate_records"]) == 439
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(439)
    )
    assert sweep["bound_matrix_record_count"] == 439
    assert sweep["fully_separated_overlap_aggregate_count"] <= 439


def test_q011bb_reproduces_preregistered_resource_identities(
    q011bb_cycle: dict[str, Any],
) -> None:
    sweep = q011bb_cycle["degree_twenty_three_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 124
    assert sweep["group_signature_record_count"] == 489
    assert sweep["pair_pool_record_count"] == 208
    assert sweep["convolution_call_count"] == 8_085
    assert sweep["original_monomial_count"] == 1_010_254_243_160
    assert sweep["modulus_signature_count"] == 16_792
    assert sweep["maximum_live_combined_signature_count"] == 144
    assert sweep["distinct_comparison_upper_bound"] == 252_396
    assert sweep["weighted_comparison_upper_bound"] == 18_941_796_258_208
    assert sweep["maximum_convolution_crude_int64_bound"] <= 317_708_751_360
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bb_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bb_validity_and_preregistered_stopping_rule(
    q011bb_cycle: dict[str, Any],
) -> None:
    assert q011bb_cycle["study_validity"] == "passed"
    assert q011bb_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bb_cycle["validity_gates"].values())
    assert q011bb_cycle["scientific_outcome"] == "accepted"
    sweep = q011bb_cycle["degree_twenty_three_block_support_coalesced_sweep"]
    assert q011bb_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bb_cycle["hypothesis_gates"].values())
    assert sweep["fully_separated_overlap_aggregate_count"] == 439
    assert sweep["distinct_comparison_count"] == 221_286
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 86_644,
        "target_below_product": 134_642,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 1_137_622_071_758
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 650_287_628_804,
        "target_below_product": 487_334_442_954,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 161
    assert minimum["selected_type_counts"] == [3, 5, 0, 15]
    assert minimum["target_identifier"] == "block=15;center=114"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.4d522573fffffp-21"
    assert minimum["exact_gap_hex"] == "0x1.4d5225cfe51dfp-21"
    assert minimum["witness_digest_sha256"] == (
        "d5bded00ec21bbc462e0453762ce5839bb8577e1687d88a983c408177671f956"
    )
    assert q011bb_cycle["scientific_classification"] == q011bb.ACCEPTED_CLASSIFICATION
    assert q011bb_cycle["actual_resonance_outcome"] == (
        q011bb.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011bb_preserves_the_scientific_boundary(q011bb_cycle: dict[str, Any]) -> None:
    theorem = q011bb_cycle["theorem_consequence"]
    accepted = q011bb_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_twenty_three_external_nonresonance_is_certified"] is accepted
    assert theorem[
        "an_actual_degree_twenty_three_external_resonance_is_ruled_out"
    ] is accepted
    assert theorem["registered_degree_twenty_three_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == (
        list(range(2, 24)) if accepted else list(range(2, 23))
    )
    assert theorem["missing_external_nonresonance_degrees"] == (
        list(range(24, 91)) if accepted else list(range(23, 91))
    )
    assert theorem["q011az_degree_twenty_two_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 24--90" in q011bb_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bb_cycle[
        "claim_boundary"
    ]


def test_q011bb_cycle_has_strict_reproducible_digests(q011bb_cycle: dict[str, Any]) -> None:
    json.dumps(q011bb_cycle, allow_nan=False)
    for name, digest in EXPECTED_SECTION_DIGESTS.items():
        assert q011bb_cycle[name] == digest
    assert q011bb_cycle["result_digest_sha256"] == q011bb.q011b._canonical_json_sha256(
        q011bb._result_digest_sections(q011bb_cycle)
    )


def test_q011bb_study_metadata_and_optional_artifact_are_scoped(
    q011bb_study: dict[str, Any],
) -> None:
    assert q011bb_study["schema_version"] == 1
    assert q011bb_study["source"] == source_metadata()
    assert q011bb_study["study_gate"] == "passed"
    assert q011bb_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011bb_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bb_study["mathematical_scope"]
    assert scope["degree"] == 23
    assert scope["degree_twenty_four_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bb_study, allow_nan=False)

    runner_path = Path(q011bb.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bb_degree23_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bb artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bb_degree23_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["actual_resonance_outcome"] == (
        q011bb.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )
    assert artifact["cycle"]["result_digest_sha256"] == q011bb.q011b._canonical_json_sha256(
        q011bb._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
