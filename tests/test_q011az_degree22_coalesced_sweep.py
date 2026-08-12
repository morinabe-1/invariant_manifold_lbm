from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011az_degree22_coalesced_sweep as q011az
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "d956b43019ff8067440db23c22bd1be689b588ded2281a09e0430b441a9a4b53"
EXPECTED_ARTIFACT_SHA256 = "ca8dd35c73afc60f8aa66a7c9a57c17595c13123a3e613b6ab4125d55ee85c19"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "80958bc98451a43248ee3ac246360ae6cfc42ff336a38c3291192a953f950c48",
    "preparation_digest_sha256": (
        "0b8625ae85fed8309ef566eb2f56d79df5f81c527e6a5017f6bc7af509e6e1fb"
    ),
    "sweep_digest_sha256": "3d69c53a16a88efd68c79399cc453912273d03277fe8e9ce05b113c21d5bf9d0",
    "result_digest_sha256": "43a425e1d41535a3347d1ed88c40ddf281d35713b45ecf32ec6d64fafa03437f",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "670b7a729eb3d9210c2c86c490edba25670c0dbaa3ed844a4052eeb52a9d5fbb"
    ),
    "bound_matrix_digest_sha256": (
        "b63d8fdad92f59093daecfbab0a4baaeea094debd96cd09ac3e0285087b66919"
    ),
    "coefficient_matrix_digest_sha256": (
        "76d119904eb9907164d345af06b24722af6be7f35b52a57a78be577be45cb767"
    ),
    "classification_matrix_digest_sha256": (
        "a78c7ecc5332ba711f853c8443b346c8376fb43eeb54d94cae63a98e325b2942"
    ),
}


@pytest.fixture(scope="module")
def q011az_study() -> dict[str, Any]:
    return q011az.run_q011az_study()


@pytest.fixture(scope="module")
def q011az_cycle(q011az_study: dict[str, Any]) -> dict[str, Any]:
    return q011az_study["cycle"]


def test_q011az_seals_q011ay_and_all_prior_inputs(q011az_cycle: dict[str, Any]) -> None:
    sealed = q011az_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 30
    assert sealed["direct_digest_count"] == 149
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ay"]["digests"]) == q011az.Q011AY_DIGESTS
    assert sealed["q011ay"]["artifact_sha256"] == q011az.Q011AY_ARTIFACT_SHA256
    assert sealed["q011ay"]["runner_sha256"] == q011az.Q011AY_RUNNER_SHA256
    assert sealed["q011ay"]["degree_twenty_two_relation_evaluation_count"] == 0


def test_q011az_reconstructs_registered_inputs_bitwise(q011az_cycle: dict[str, Any]) -> None:
    fixed = q011az_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 22
    assert fixed["degree_aggregate_count"] == 2_300
    assert fixed["old_modulus_separated_aggregate_count"] == 1_901
    assert fixed["direct_overlap_aggregate_count"] == 399
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 268
    assert fixed["active_identifier_count"] == 292
    assert fixed["monotone_identifier_count"] == 308
    assert fixed["inactive_retained_identifier_count"] == 16
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011az.q011ay.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011az.q011ay.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011az.q011ay.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011az.q011ay.EXPECTED_HULL_RECORD_DIGEST


def test_q011az_processes_every_registered_aggregate_once(
    q011az_cycle: dict[str, Any],
) -> None:
    sweep = q011az_cycle["degree_twenty_two_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 22
    assert sweep["audited_overlap_aggregate_count"] == 399
    assert len(sweep["aggregate_records"]) == 399
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(399)
    )
    assert sweep["bound_matrix_record_count"] == 399
    assert sweep["fully_separated_overlap_aggregate_count"] <= 399


def test_q011az_reproduces_preregistered_resource_identities(
    q011az_cycle: dict[str, Any],
) -> None:
    sweep = q011az_cycle["degree_twenty_two_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 118
    assert sweep["group_signature_record_count"] == 459
    assert sweep["pair_pool_record_count"] == 202
    assert sweep["convolution_call_count"] == 7_438
    assert sweep["original_monomial_count"] == 508_134_615_924
    assert sweep["modulus_signature_count"] == 14_686
    assert sweep["maximum_live_combined_signature_count"] == 121
    assert sweep["distinct_comparison_upper_bound"] == 194_280
    assert sweep["weighted_comparison_upper_bound"] == 7_968_716_751_096
    assert sweep["maximum_convolution_crude_int64_bound"] <= 226_934_822_400
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011az_cycle["registered_parameters"]
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011az_validity_and_preregistered_stopping_rule(
    q011az_cycle: dict[str, Any],
) -> None:
    assert q011az_cycle["study_validity"] == "passed"
    assert q011az_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011az_cycle["validity_gates"].values())
    assert q011az_cycle["scientific_outcome"] == "accepted"
    sweep = q011az_cycle["degree_twenty_two_block_support_coalesced_sweep"]
    assert q011az_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011az_cycle["hypothesis_gates"].values())
    assert sweep["fully_separated_overlap_aggregate_count"] == 399
    assert sweep["distinct_comparison_count"] == 166_542
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 62_360,
        "target_below_product": 104_182,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 483_294_136_022
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 283_722_068_460,
        "target_below_product": 199_572_067_562,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 246
    assert minimum["selected_type_counts"] == [5, 0, 4, 13]
    assert minimum["target_identifier"] == "block=11;center=3"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.13e7d9c1fffffp-21"
    assert minimum["exact_gap_hex"] == "0x1.13e7da1c6ee42p-21"
    assert minimum["witness_digest_sha256"] == (
        "f6e5e73e18074d527863d9679221d8eaf0f714b5ea416f58fa53af216d060526"
    )
    assert q011az_cycle["scientific_classification"] == q011az.ACCEPTED_CLASSIFICATION
    assert q011az_cycle["actual_resonance_outcome"] == (
        q011az.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011az_preserves_the_scientific_boundary(q011az_cycle: dict[str, Any]) -> None:
    theorem = q011az_cycle["theorem_consequence"]
    accepted = q011az_cycle["scientific_outcome"] == "accepted"
    assert theorem["degree_twenty_two_external_nonresonance_is_certified"] is accepted
    assert theorem[
        "an_actual_degree_twenty_two_external_resonance_is_ruled_out"
    ] is accepted
    assert theorem["registered_degree_twenty_two_sufficient_certificate_is_rejected"] is (
        not accepted
    )
    assert theorem["certified_external_nonresonance_degrees"] == (
        list(range(2, 23)) if accepted else list(range(2, 22))
    )
    assert theorem["missing_external_nonresonance_degrees"] == (
        list(range(23, 91)) if accepted else list(range(22, 91))
    )
    assert theorem["q011ax_degree_twenty_one_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 23--90" in q011az_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011az_cycle[
        "claim_boundary"
    ]


def test_q011az_cycle_has_strict_reproducible_digests(q011az_cycle: dict[str, Any]) -> None:
    json.dumps(q011az_cycle, allow_nan=False)
    for name, digest in EXPECTED_SECTION_DIGESTS.items():
        assert q011az_cycle[name] == digest
    assert q011az_cycle["result_digest_sha256"] == q011az.q011b._canonical_json_sha256(
        q011az._result_digest_sections(q011az_cycle)
    )


def test_q011az_study_metadata_and_optional_artifact_are_scoped(
    q011az_study: dict[str, Any],
) -> None:
    assert q011az_study["schema_version"] == 1
    assert q011az_study["source"] == source_metadata()
    assert q011az_study["study_gate"] == "passed"
    assert q011az_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011az_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011az_study["mathematical_scope"]
    assert scope["degree"] == 22
    assert scope["degree_twenty_three_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011az_study, allow_nan=False)

    runner_path = Path(q011az.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011az_degree22_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011az artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011az_degree22_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["actual_resonance_outcome"] == (
        q011az.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )
    assert artifact["cycle"]["result_digest_sha256"] == q011az.q011b._canonical_json_sha256(
        q011az._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
