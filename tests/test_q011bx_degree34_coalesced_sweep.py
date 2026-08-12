from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bx_degree34_coalesced_sweep as q011bx
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256: str | None = (
    "cfae443c9934a202c34e9455aaf6499d1bff636d3b45e617245426e9449e221d"
)
EXPECTED_ARTIFACT_SHA256: str | None = (
    "01307870ef93c219009b56a77cff58ecf55fe32f987cd9365dc43122b04eb9e2"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "e69981e0c318bcc0f29f25a7c0e568db2f088841949b5a3a008ccabdc9f705a6",
    "preparation_digest_sha256": (
        "7ea445c2c4d8297dc523e4543b37caba35daafc8cddb4625e39b4039d0cf467f"
    ),
    "sweep_digest_sha256": "4741be104eefef8eafc43ea13e221e23521dec80adf51969cc7d7a112241f9b9",
    "result_digest_sha256": "595044021e943ee98cdf00e6413da53a47db3e6ebb6aa823a03cf4069278170f",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "65b9e54c79a3cd19e46b8294ac91aee7ec7ad1ffee82171cfc95356284d35421"
    ),
    "bound_matrix_digest_sha256": (
        "e296f3d09bb544857306b7e42e8df6f844fa3485ea2cbe7ce2c7ebe4188a603a"
    ),
    "coefficient_matrix_digest_sha256": (
        "3288acbee533599f41e662f9065d9a68ef8d7a77a2884fa6e3a5fa1da2a3aadd"
    ),
    "classification_matrix_digest_sha256": (
        "718cd6281e6a0dce3ca6c3700f7975ec5d87a32636450c047fc83e7f48f7673a"
    ),
}


@pytest.fixture(scope="module")
def q011bx_study() -> dict[str, Any]:
    return q011bx.run_q011bx_study()


@pytest.fixture(scope="module")
def q011bx_cycle(q011bx_study: dict[str, Any]) -> dict[str, Any]:
    return q011bx_study["cycle"]


def test_q011bx_seals_q011bw_and_all_prior_inputs(q011bx_cycle: dict[str, Any]) -> None:
    sealed = q011bx_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 54
    assert sealed["direct_digest_count"] == 257
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bw"]["digests"]) == q011bx.Q011BW_DIGESTS
    assert sealed["q011bw"]["artifact_sha256"] == q011bx.Q011BW_ARTIFACT_SHA256
    assert sealed["q011bw"]["runner_sha256"] == q011bx.Q011BW_RUNNER_SHA256
    assert sealed["q011bw"]["degree_thirty_four_relation_evaluation_count"] == 0


def test_q011bx_reconstructs_registered_inputs_bitwise(q011bx_cycle: dict[str, Any]) -> None:
    fixed = q011bx_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 34
    assert fixed["degree_aggregate_count"] == 7_770
    assert fixed["old_modulus_separated_aggregate_count"] == 4_632
    assert fixed["direct_overlap_aggregate_count"] == 3_138
    assert fixed["multi_target_aggregate_count"] == 48
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 1_300
    assert fixed["active_identifier_count"] == 1_324
    assert fixed["monotone_identifier_count"] == 1_464
    assert fixed["inactive_retained_identifier_count"] == 140
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bx.q011bw.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bx.q011bw.EXPECTED_ACTIVE_RECORD_DIGEST
    )

    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bx.q011bw.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bx.q011bw.EXPECTED_HULL_RECORD_DIGEST


def test_q011bx_processes_every_registered_aggregate_once(
    q011bx_cycle: dict[str, Any],
) -> None:
    sweep = q011bx_cycle["degree_thirty_four_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 34
    assert sweep["audited_overlap_aggregate_count"] == 3_138
    assert len(sweep["aggregate_records"]) == 3_138
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(3_138)
    )
    assert sweep["bound_matrix_record_count"] == 3_138
    assert sweep["fully_separated_overlap_aggregate_count"] <= 3_138


def test_q011bx_reproduces_preregistered_resource_identities(
    q011bx_cycle: dict[str, Any],
) -> None:
    sweep = q011bx_cycle["degree_thirty_four_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 200
    assert sweep["group_signature_record_count"] == 1_191
    assert sweep["pair_pool_record_count"] == 885
    assert sweep["convolution_call_count"] == 52_596
    assert sweep["original_monomial_count"] == 2_119_833_971_218_270
    assert sweep["modulus_signature_count"] == 221_676
    assert sweep["maximum_live_combined_signature_count"] == 306
    assert sweep["distinct_comparison_upper_bound"] == 3_448_960
    assert sweep["weighted_comparison_upper_bound"] == 30_455_371_778_893_216
    assert sweep["maximum_convolution_crude_int64_bound"] <= 123_300_484_070_400
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bx_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 48
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bx_applies_the_preregistered_stopping_rule(
    q011bx_cycle: dict[str, Any],
) -> None:
    assert q011bx_cycle["study_validity"] == "passed"
    assert q011bx_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bx_cycle["validity_gates"].values())
    assert q011bx_cycle["scientific_outcome"] == "rejected"
    assert q011bx_cycle["failed_hypothesis_order"] == [
        "every_direct_comparison_is_strictly_separated",
        "old_and_direct_aggregates_cover_degree_thirty_four",
    ]
    assert not all(gate["passed"] for gate in q011bx_cycle["hypothesis_gates"].values())
    sweep = q011bx_cycle["degree_thirty_four_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 3_136
    assert sweep["remaining_overlap_aggregate_count"] == 2
    assert sweep["distinct_comparison_count"] == 3_338_044
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 1_548_122,
        "target_below_product": 1_789_858,
        "overlap": 64,
    }
    assert sweep["weighted_comparison_count"] == 1_781_675_618_428_090
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 1_050_468_146_510_558,
        "target_below_product": 731_124_946_110_332,
        "overlap": 82_525_807_200,
    }
    assert sweep["first_unresolved_witness"] is not None
    first_overlap = sweep["first_unresolved_witness"]
    assert first_overlap["aggregate_index"] == 972
    assert first_overlap["selected_type_counts"] == [4, 27, 3, 0]
    assert first_overlap["target_identifier"] == "block=12;center=124"
    assert first_overlap["output_block"] == 12
    assert first_overlap["left_index"] == first_overlap["right_index"] == 0
    assert first_overlap["wave_multiplicity"] == 341_000
    assert first_overlap["relation"] == "overlap"
    assert first_overlap["intersection_interval"]["width_hex"] == "0x1.570c9fb70fc7dp-28"
    assert first_overlap["witness_digest_sha256"] == (
        "ad3f2cb8d8ad0f75eacaec10b8ff606e709bc5ff037542ca612ecc97a40d8ce5"
    )
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 2_340
    assert minimum["selected_type_counts"] == [13, 9, 5, 7]
    assert minimum["target_identifier"] == "block=10;center=45"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.4fc7fffffffffp-37"
    assert minimum["exact_gap_hex"] == "0x1.5031e5ffb89ebp-37"
    assert minimum["witness_digest_sha256"] == (
        "ef82f39ac2982ec7206b48875f467b05c355333b98ab48e092d74af864122dfd"
    )
    assert q011bx_cycle["scientific_classification"] == q011bx.REJECTED_CLASSIFICATION
    assert q011bx_cycle["actual_resonance_outcome"] == "not_established"


def test_q011bx_preserves_the_scientific_boundary(q011bx_cycle: dict[str, Any]) -> None:
    theorem = q011bx_cycle["theorem_consequence"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_ruled_out"]
    assert theorem["registered_degree_thirty_four_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert theorem["q011bv_degree_thirty_three_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 35--90" in q011bx_cycle["claim_boundary"]
    assert (
        "inactive monotone proof records are retained but not compared"
        in q011bx_cycle["claim_boundary"]
    )


def test_q011bx_cycle_has_strict_reproducible_digests(q011bx_cycle: dict[str, Any]) -> None:
    json.dumps(q011bx_cycle, allow_nan=False)
    assert {
        name: q011bx_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bx_cycle["degree_thirty_four_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bx_cycle["result_digest_sha256"] == q011bx.q011b._canonical_json_sha256(
        q011bx._result_digest_sections(q011bx_cycle)
    )


def test_q011bx_study_metadata_and_optional_artifact_are_scoped(
    q011bx_study: dict[str, Any],
) -> None:
    assert q011bx_study["schema_version"] == 1
    assert q011bx_study["source"] == source_metadata()
    assert q011bx_study["study_gate"] == "passed"
    assert q011bx_study["scientific_outcome"] == "rejected"
    assert q011bx_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bx_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["degree_thirty_five_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bx_study, allow_nan=False)

    runner_path = Path(q011bx.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bx_degree34_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bx artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bx_degree34_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert EXPECTED_RUNNER_SHA256 is not None
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bx_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bx_study["actual_resonance_outcome"]
    assert artifact["cycle"]["result_digest_sha256"] == q011bx.q011b._canonical_json_sha256(
        q011bx._result_digest_sections(artifact["cycle"])
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
