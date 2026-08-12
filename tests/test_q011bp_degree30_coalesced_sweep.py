from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bp_degree30_coalesced_sweep as q011bp
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "a1d6478ccecd8a3d00e3ca98a5a2544ae4d6a13ca40bac8d8e35ff3f69fdac3e"
EXPECTED_ARTIFACT_SHA256 = "f7198b0c295ee44a0c72d272de1a427bac10bc9201bb41b41ec5cd5acf785509"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "be1ca9502d413c681d1623dbac682ef54f82708467e3e539ee5f65533ad54a71",
    "preparation_digest_sha256": (
        "a05c7985e1956b747c3fbda94d072904ff06ed3606d09e69d3df7072826697b9"
    ),
    "sweep_digest_sha256": "bc88cdb5e82dda547712e54f1c2e56d1c1f746821981c2b0afafc7650f6eff02",
    "result_digest_sha256": "bba3191ef8d864f5393e4c3aefd7f17dd4b89c8497c40160d928f59dd7ec6bdd",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "e1c909c09543815dea5c66f288ed7c5553a4a9f23fd257a9d84aa8945609e4f6"
    ),
    "bound_matrix_digest_sha256": (
        "00feb9b1d08cf2a2ee498b3c71ee744d11d0e509346c22746e038394b8bc3836"
    ),
    "coefficient_matrix_digest_sha256": (
        "95c95399a47d5476e5292406ba660230aebebd07b9c2ee878f6cbe948d77d0c1"
    ),
    "classification_matrix_digest_sha256": (
        "0ca84a2bc8662bf438fc30109e316a415a9f47d6044b661e7f0c2a67d9fed41b"
    ),
}


@pytest.fixture(scope="module")
def q011bp_study() -> dict[str, Any]:
    return q011bp.run_q011bp_study()


@pytest.fixture(scope="module")
def q011bp_cycle(q011bp_study: dict[str, Any]) -> dict[str, Any]:
    return q011bp_study["cycle"]


def test_q011bp_seals_q011bo_and_all_prior_inputs(q011bp_cycle: dict[str, Any]) -> None:
    sealed = q011bp_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 46
    assert sealed["direct_digest_count"] == 221
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bo"]["digests"]) == q011bp.Q011BO_DIGESTS
    assert sealed["q011bo"]["artifact_sha256"] == q011bp.Q011BO_ARTIFACT_SHA256
    assert sealed["q011bo"]["runner_sha256"] == q011bp.Q011BO_RUNNER_SHA256
    assert sealed["q011bo"]["degree_thirty_relation_evaluation_count"] == 0


def test_q011bp_reconstructs_registered_inputs_bitwise(q011bp_cycle: dict[str, Any]) -> None:
    fixed = q011bp_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 30
    assert fixed["degree_aggregate_count"] == 5_456
    assert fixed["old_modulus_separated_aggregate_count"] == 3_781
    assert fixed["direct_overlap_aggregate_count"] == 1_675
    assert fixed["multi_target_aggregate_count"] == 2
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 772
    assert fixed["active_identifier_count"] == 796
    assert fixed["monotone_identifier_count"] == 912
    assert fixed["inactive_retained_identifier_count"] == 116
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bp.q011bo.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bp.q011bo.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bp.q011bo.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bp.q011bo.EXPECTED_HULL_RECORD_DIGEST


def test_q011bp_processes_every_registered_aggregate_once(
    q011bp_cycle: dict[str, Any],
) -> None:
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 30
    assert sweep["audited_overlap_aggregate_count"] == 1_675
    assert len(sweep["aggregate_records"]) == 1_675
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(1_675)
    )
    assert sweep["bound_matrix_record_count"] == 1_675
    assert sweep["fully_separated_overlap_aggregate_count"] <= 1_675


def test_q011bp_reproduces_preregistered_resource_identities(
    q011bp_cycle: dict[str, Any],
) -> None:
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 179
    assert sweep["group_signature_record_count"] == 989
    assert sweep["pair_pool_record_count"] == 536
    assert sweep["convolution_call_count"] == 24_223
    assert sweep["original_monomial_count"] == 199_600_479_347_738
    assert sweep["modulus_signature_count"] == 97_583
    assert sweep["maximum_live_combined_signature_count"] == 240
    assert sweep["distinct_comparison_upper_bound"] == 1_552_420
    assert sweep["weighted_comparison_upper_bound"] == 3_078_782_483_959_528
    assert sweep["maximum_convolution_crude_int64_bound"] <= 20_622_186_224_640
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bp_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 2
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bp_applies_the_preregistered_stopping_rule(
    q011bp_cycle: dict[str, Any],
) -> None:
    assert q011bp_cycle["study_validity"] == "passed"
    assert q011bp_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bp_cycle["validity_gates"].values())
    assert q011bp_cycle["scientific_outcome"] == "accepted"
    assert q011bp_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bp_cycle["hypothesis_gates"].values())
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 1_675
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["distinct_comparison_count"] == 1_470_044
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 617_492,
        "target_below_product": 852_552,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 181_192_339_421_108
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 86_848_258_700_160,
        "target_below_product": 94_344_080_720_948,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 1_474
    assert minimum["selected_type_counts"] == [15, 8, 7, 0]
    assert minimum["target_identifier"] == "block=13;center=11"
    assert minimum["relation"] == "product_below_target"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.51b8c20bfffffp-22"
    assert minimum["exact_gap_hex"] == "0x1.51b8c2e3fc8b8p-22"
    assert minimum["witness_digest_sha256"] == (
        "dfd36368b2110405dad7616df04adb48d2e90857dcb9b9e346e0f31b4878b1d4"
    )
    assert q011bp_cycle["scientific_classification"] == q011bp.ACCEPTED_CLASSIFICATION
    assert (
        q011bp_cycle["actual_resonance_outcome"]
        == q011bp.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011bp_preserves_the_scientific_boundary(q011bp_cycle: dict[str, Any]) -> None:
    theorem = q011bp_cycle["theorem_consequence"]
    assert theorem["degree_thirty_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_thirty_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_thirty_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 31))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(31, 91))
    assert theorem["q011bn_degree_twenty_nine_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 31--90" in q011bp_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bp_cycle[
        "claim_boundary"
    ]


def test_q011bp_cycle_has_strict_reproducible_digests(q011bp_cycle: dict[str, Any]) -> None:
    json.dumps(q011bp_cycle, allow_nan=False)
    assert {
        name: q011bp_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bp_cycle["degree_thirty_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bp_cycle["result_digest_sha256"] == q011bp.q011b._canonical_json_sha256(
        q011bp._result_digest_sections(q011bp_cycle)
    )


def test_q011bp_study_metadata_and_optional_artifact_are_scoped(
    q011bp_study: dict[str, Any],
) -> None:
    assert q011bp_study["schema_version"] == 1
    assert q011bp_study["source"] == source_metadata()
    assert q011bp_study["study_gate"] == "passed"
    assert q011bp_study["scientific_outcome"] == "accepted"
    assert q011bp_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bp_study["mathematical_scope"]
    assert scope["degree"] == 30
    assert scope["degree_thirty_one_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bp_study, allow_nan=False)

    runner_path = Path(q011bp.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bp_degree30_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bp artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bp_degree30_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bp_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bp_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bp.q011b._canonical_json_sha256(
        q011bp._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
