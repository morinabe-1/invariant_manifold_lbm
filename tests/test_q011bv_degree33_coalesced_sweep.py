from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bv_degree33_coalesced_sweep as q011bv
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "4892919530f53036cb208917ba6459fdf8737666255677908aff76dfc301d531"
EXPECTED_ARTIFACT_SHA256 = "c6f8ed59698b9652a51e706d935fef42f3602dfa21902ff8aa424a129296f50b"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "31a5668eac97a7426b3a9cc349a0e2fabbb76efd5ff2e9136184db3de73a8708",
    "preparation_digest_sha256": (
        "3fc7c55a006d9e3c1e19ff8689819a22b23ff7c853821c4a364d6831fdeb7d43"
    ),
    "sweep_digest_sha256": "5b3d2e15da883ef298f634cb3e9d1828e3c61f0f3d628b4e5eed7121b8a0a8a1",
    "result_digest_sha256": "f083727b3d749d215f21bd43a56cc521680d35581c5a1fcd4d696f9dc6f0ffc5",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "598e7e583fb280e00dbfcfa6bc5ec97655ebd23b2f560298d345242dcc81baff"
    ),
    "bound_matrix_digest_sha256": (
        "2fd889128e3fb4c32b041321c07bdbaf07636c1a94e666c108b7f8addc33cc84"
    ),
    "coefficient_matrix_digest_sha256": (
        "29101a3316b4d90aaf0a0b418fa9016d07feabdc34893282ea0bd3dabc3f5f71"
    ),
    "classification_matrix_digest_sha256": (
        "eb9c7989c9abfeb9d7c8f785a697576630bd52cd96555d86aa9cbff718550e08"
    ),
}


@pytest.fixture(scope="module")
def q011bv_study() -> dict[str, Any]:
    return q011bv.run_q011bv_study()


@pytest.fixture(scope="module")
def q011bv_cycle(q011bv_study: dict[str, Any]) -> dict[str, Any]:
    return q011bv_study["cycle"]


def test_q011bv_seals_q011bu_and_all_prior_inputs(q011bv_cycle: dict[str, Any]) -> None:
    sealed = q011bv_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 52
    assert sealed["direct_digest_count"] == 248
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bu"]["digests"]) == q011bv.Q011BU_DIGESTS
    assert sealed["q011bu"]["artifact_sha256"] == q011bv.Q011BU_ARTIFACT_SHA256
    assert sealed["q011bu"]["runner_sha256"] == q011bv.Q011BU_RUNNER_SHA256
    assert sealed["q011bu"]["degree_thirty_three_relation_evaluation_count"] == 0


def test_q011bv_reconstructs_registered_inputs_bitwise(q011bv_cycle: dict[str, Any]) -> None:
    fixed = q011bv_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 33
    assert fixed["degree_aggregate_count"] == 7_140
    assert fixed["old_modulus_separated_aggregate_count"] == 4_454
    assert fixed["direct_overlap_aggregate_count"] == 2_686
    assert fixed["multi_target_aggregate_count"] == 25
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 1_128
    assert fixed["active_identifier_count"] == 1_152
    assert fixed["monotone_identifier_count"] == 1_292
    assert fixed["inactive_retained_identifier_count"] == 140
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bv.q011bu.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bv.q011bu.EXPECTED_ACTIVE_RECORD_DIGEST
    )

    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bv.q011bu.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bv.q011bu.EXPECTED_HULL_RECORD_DIGEST


def test_q011bv_processes_every_registered_aggregate_once(
    q011bv_cycle: dict[str, Any],
) -> None:
    sweep = q011bv_cycle["degree_thirty_three_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 33
    assert sweep["audited_overlap_aggregate_count"] == 2_686
    assert len(sweep["aggregate_records"]) == 2_686
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(2_686)
    )
    assert sweep["bound_matrix_record_count"] == 2_686
    assert sweep["fully_separated_overlap_aggregate_count"] <= 2_686


def test_q011bv_reproduces_preregistered_resource_identities(
    q011bv_cycle: dict[str, Any],
) -> None:
    sweep = q011bv_cycle["degree_thirty_three_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 193
    assert sweep["group_signature_record_count"] == 1_121
    assert sweep["pair_pool_record_count"] == 771
    assert sweep["convolution_call_count"] == 41_820
    assert sweep["original_monomial_count"] == 1_182_191_544_739_044
    assert sweep["modulus_signature_count"] == 181_711
    assert sweep["maximum_live_combined_signature_count"] == 272
    assert sweep["distinct_comparison_upper_bound"] == 2_754_464
    assert sweep["weighted_comparison_upper_bound"] == 16_429_979_607_740_272
    assert sweep["maximum_convolution_crude_int64_bound"] <= 82_200_322_713_600
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bv_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 25
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bv_applies_the_preregistered_stopping_rule(
    q011bv_cycle: dict[str, Any],
) -> None:
    assert q011bv_cycle["study_validity"] == "passed"
    assert q011bv_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bv_cycle["validity_gates"].values())
    assert q011bv_cycle["scientific_outcome"] == "accepted"
    assert q011bv_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bv_cycle["hypothesis_gates"].values())
    sweep = q011bv_cycle["degree_thirty_three_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 2_686
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["distinct_comparison_count"] == 2_661_180
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 1_182_232,
        "target_below_product": 1_478_948,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 960_452_962_070_374
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 557_876_114_806_544,
        "target_below_product": 402_576_847_263_830,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 2_058
    assert minimum["selected_type_counts"] == [13, 10, 5, 5]
    assert minimum["target_identifier"] == "block=10;center=44"
    assert minimum["relation"] == "product_below_target"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.0e46abe7fffffp-24"
    assert minimum["exact_gap_hex"] == "0x1.0e46af95a5480p-24"
    assert minimum["witness_digest_sha256"] == (
        "e8ad410989a56a9f82844639974c041c016fc8a180278624c4907001e056da6b"
    )
    assert q011bv_cycle["scientific_classification"] == q011bv.ACCEPTED_CLASSIFICATION
    assert q011bv_cycle["actual_resonance_outcome"] == q011bv.ACCEPTED_ACTUAL_RESONANCE_OUTCOME


def test_q011bv_preserves_the_scientific_boundary(q011bv_cycle: dict[str, Any]) -> None:
    theorem = q011bv_cycle["theorem_consequence"]
    assert theorem["degree_thirty_three_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_thirty_three_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_thirty_three_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert theorem["q011bt_degree_thirty_two_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 34--90" in q011bv_cycle["claim_boundary"]
    assert (
        "inactive monotone proof records are retained but not compared"
        in q011bv_cycle["claim_boundary"]
    )


def test_q011bv_cycle_has_strict_reproducible_digests(q011bv_cycle: dict[str, Any]) -> None:
    json.dumps(q011bv_cycle, allow_nan=False)
    assert {
        name: q011bv_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bv_cycle["degree_thirty_three_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bv_cycle["result_digest_sha256"] == q011bv.q011b._canonical_json_sha256(
        q011bv._result_digest_sections(q011bv_cycle)
    )


def test_q011bv_study_metadata_and_optional_artifact_are_scoped(
    q011bv_study: dict[str, Any],
) -> None:
    assert q011bv_study["schema_version"] == 1
    assert q011bv_study["source"] == source_metadata()
    assert q011bv_study["study_gate"] == "passed"
    assert q011bv_study["scientific_outcome"] == "accepted"
    assert q011bv_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bv_study["mathematical_scope"]
    assert scope["degree"] == 33
    assert scope["degree_thirty_four_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bv_study, allow_nan=False)

    runner_path = Path(q011bv.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bv_degree33_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bv artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bv_degree33_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bv_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bv_study["actual_resonance_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == q011bv.q011b._canonical_json_sha256(
        q011bv._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
