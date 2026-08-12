from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bh_degree26_coalesced_sweep as q011bh
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "b934c50138890dd329d2d0dc75c78f98df9540d3e9b5eb3a463347f2c1a9b192"
EXPECTED_ARTIFACT_SHA256 = "34294fc77fd5ade05ab61812088fdee6d8cec63a5e22c0eac555c3647b073349"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "895a724a63a66c04929fbaaf95149b93444f8199f78a8494e2ae835bc800877a",
    "preparation_digest_sha256": (
        "8d61ae48890284651ca81e458478f1716a64f28f64149daf92aa0936ddf08b9f"
    ),
    "sweep_digest_sha256": "d8b4ca8a9dfdc34b8fd4cb4574f0b0c54fdb158c3cd8b2a6ecf6fe06dfb3c333",
    "result_digest_sha256": "86269e13f502c70439a1381edf2f532c50491a5c313ce974307db623a4ae9db4",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "301806ea34bdd8e24d444b1ad8064e9cae55ae7bef824e6de64b25e40bddd80d"
    ),
    "bound_matrix_digest_sha256": (
        "963b5c735035a1d26f4b23fc6b82e16573fad1580792240020ade99eec814a1d"
    ),
    "coefficient_matrix_digest_sha256": (
        "3123b9b702fa23dba3fdbc6fe5a82568796e994d0aa62c9e57a9fff76f95d356"
    ),
    "classification_matrix_digest_sha256": (
        "6708141594e652e8f0e74af67098993dfd595c6324be2b05eeef428b9ec3657c"
    ),
}


@pytest.fixture(scope="module")
def q011bh_study() -> dict[str, Any]:
    return q011bh.run_q011bh_study()


@pytest.fixture(scope="module")
def q011bh_cycle(q011bh_study: dict[str, Any]) -> dict[str, Any]:
    return q011bh_study["cycle"]


def test_q011bh_seals_q011bg_and_all_prior_inputs(q011bh_cycle: dict[str, Any]) -> None:
    sealed = q011bh_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 38
    assert sealed["direct_digest_count"] == 185
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bg"]["digests"]) == q011bh.Q011BG_DIGESTS
    assert sealed["q011bg"]["artifact_sha256"] == q011bh.Q011BG_ARTIFACT_SHA256
    assert sealed["q011bg"]["runner_sha256"] == q011bh.Q011BG_RUNNER_SHA256
    assert sealed["q011bg"]["degree_twenty_six_relation_evaluation_count"] == 0


def test_q011bh_reconstructs_registered_inputs_bitwise(q011bh_cycle: dict[str, Any]) -> None:
    fixed = q011bh_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 26
    assert fixed["degree_aggregate_count"] == 3_654
    assert fixed["old_modulus_separated_aggregate_count"] == 2_875
    assert fixed["direct_overlap_aggregate_count"] == 779
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 460
    assert fixed["active_identifier_count"] == 484
    assert fixed["monotone_identifier_count"] == 568
    assert fixed["inactive_retained_identifier_count"] == 84
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bh.q011bg.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bh.q011bg.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bh.q011bg.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bh.q011bg.EXPECTED_HULL_RECORD_DIGEST


def test_q011bh_processes_every_registered_aggregate_once(
    q011bh_cycle: dict[str, Any],
) -> None:
    sweep = q011bh_cycle["degree_twenty_six_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 26
    assert sweep["audited_overlap_aggregate_count"] == 779
    assert len(sweep["aggregate_records"]) == 779
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(779)
    )
    assert sweep["bound_matrix_record_count"] == 779
    assert sweep["fully_separated_overlap_aggregate_count"] <= 779


def test_q011bh_reproduces_preregistered_resource_identities(
    q011bh_cycle: dict[str, Any],
) -> None:
    sweep = q011bh_cycle["degree_twenty_six_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 150
    assert sweep["group_signature_record_count"] == 632
    assert sweep["pair_pool_record_count"] == 290
    assert sweep["convolution_call_count"] == 9_474
    assert sweep["original_monomial_count"] == 11_279_576_045_274
    assert sweep["modulus_signature_count"] == 32_455
    assert sweep["maximum_live_combined_signature_count"] == 156
    assert sweep["distinct_comparison_upper_bound"] == 576_636
    assert sweep["weighted_comparison_upper_bound"] == 241_078_715_222_912
    assert sweep["maximum_convolution_crude_int64_bound"] <= 2_725_442_720_000
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bh_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bh_applies_the_preregistered_stopping_rule(
    q011bh_cycle: dict[str, Any],
) -> None:
    assert q011bh_cycle["study_validity"] == "passed"
    assert q011bh_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bh_cycle["validity_gates"].values())
    assert q011bh_cycle["scientific_outcome"] == "accepted"
    assert q011bh_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bh_cycle["hypothesis_gates"].values())
    sweep = q011bh_cycle["degree_twenty_six_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 779
    assert sweep["distinct_comparison_count"] == 530_266
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 227_952,
        "target_below_product": 302_314,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 14_415_713_946_704
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 7_310_145_276_356,
        "target_below_product": 7_105_568_670_348,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 745
    assert minimum["selected_type_counts"] == [19, 0, 3, 4]
    assert minimum["target_identifier"] == "block=12;center=146"
    assert minimum["relation"] == "product_below_target"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.37b3c41bfffffp-22"
    assert minimum["exact_gap_hex"] == "0x1.37b3c4df5b7b2p-22"
    assert minimum["witness_digest_sha256"] == (
        "6aeb6451b7007926cef4a25f7f5014504f80c22d7c0d0fe77b34e0692ac09c6a"
    )
    assert q011bh_cycle["scientific_classification"] == q011bh.ACCEPTED_CLASSIFICATION
    assert (
        q011bh_cycle["actual_resonance_outcome"]
        == q011bh.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011bh_preserves_the_scientific_boundary(q011bh_cycle: dict[str, Any]) -> None:
    theorem = q011bh_cycle["theorem_consequence"]
    assert theorem["degree_twenty_six_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_twenty_six_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_twenty_six_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 27))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(27, 91))
    assert theorem["q011bf_degree_twenty_five_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 27--90" in q011bh_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bh_cycle[
        "claim_boundary"
    ]


def test_q011bh_cycle_has_strict_reproducible_digests(q011bh_cycle: dict[str, Any]) -> None:
    json.dumps(q011bh_cycle, allow_nan=False)
    assert {
        name: q011bh_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bh_cycle["degree_twenty_six_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bh_cycle["result_digest_sha256"] == q011bh.q011b._canonical_json_sha256(
        q011bh._result_digest_sections(q011bh_cycle)
    )


def test_q011bh_study_metadata_and_optional_artifact_are_scoped(
    q011bh_study: dict[str, Any],
) -> None:
    assert q011bh_study["schema_version"] == 1
    assert q011bh_study["source"] == source_metadata()
    assert q011bh_study["study_gate"] == "passed"
    assert q011bh_study["scientific_outcome"] == "accepted"
    assert q011bh_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bh_study["mathematical_scope"]
    assert scope["degree"] == 26
    assert scope["degree_twenty_seven_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bh_study, allow_nan=False)

    runner_path = Path(q011bh.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bh_degree26_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bh artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bh_degree26_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bh_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bh_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bh.q011b._canonical_json_sha256(
        q011bh._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
