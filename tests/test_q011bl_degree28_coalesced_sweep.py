from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011bl_degree28_coalesced_sweep as q011bl
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "d42a801207a8dcc5b76c5fd39f1f3ac8c041d2a438a4e4b4f05f8396a415c450"
EXPECTED_ARTIFACT_SHA256 = "e33843ffbda88cd41ad82147b6206352f4b0bb1f76b4c95b74f5111918843861"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "fe73db0266b94fe46cc01792da8243aefd0d207ef91943d8e774d42d3fc0055c",
    "preparation_digest_sha256": (
        "fb0b8b3b793ca3e33f8582c43c532b9139770f40302c91dd9ba2615e34a14256"
    ),
    "sweep_digest_sha256": "05a33a4427dfca5ddd5bca3fecbbcd3338d90634be9fd2e81136fbe666274a34",
    "result_digest_sha256": "8b8e5492af4d50b2be22af8b43ebb3449131f03a26c22203a3895708e65548e3",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "68e6078552ccd179b4d9183b95093b7ef71cc128d755d6982af60c45d9acb76f"
    ),
    "bound_matrix_digest_sha256": (
        "9193747e93acc6999ff55501dcdc0bbfe30ed992edb02bc072537303bb502022"
    ),
    "coefficient_matrix_digest_sha256": (
        "3310cc32c60fa5ad60429194bd8716be6e13a76824ab60cef9f80647a07ac0f6"
    ),
    "classification_matrix_digest_sha256": (
        "255d3d6364e2b9473e815f64cff74d317a2e38bce130c9f61a196f89ac98ef44"
    ),
}


@pytest.fixture(scope="module")
def q011bl_study() -> dict[str, Any]:
    return q011bl.run_q011bl_study()


@pytest.fixture(scope="module")
def q011bl_cycle(q011bl_study: dict[str, Any]) -> dict[str, Any]:
    return q011bl_study["cycle"]


def test_q011bl_seals_q011bk_and_all_prior_inputs(q011bl_cycle: dict[str, Any]) -> None:
    sealed = q011bl_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 42
    assert sealed["direct_digest_count"] == 203
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bk"]["digests"]) == q011bl.Q011BK_DIGESTS
    assert sealed["q011bk"]["artifact_sha256"] == q011bl.Q011BK_ARTIFACT_SHA256
    assert sealed["q011bk"]["runner_sha256"] == q011bl.Q011BK_RUNNER_SHA256
    assert sealed["q011bk"]["degree_twenty_eight_relation_evaluation_count"] == 0


def test_q011bl_reconstructs_registered_inputs_bitwise(q011bl_cycle: dict[str, Any]) -> None:
    fixed = q011bl_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 28
    assert fixed["degree_aggregate_count"] == 4_495
    assert fixed["old_modulus_separated_aggregate_count"] == 3_325
    assert fixed["direct_overlap_aggregate_count"] == 1_170
    assert fixed["multi_target_aggregate_count"] == 2
    assert fixed["maximum_external_component_count"] == 3
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 612
    assert fixed["active_identifier_count"] == 636
    assert fixed["monotone_identifier_count"] == 728
    assert fixed["inactive_retained_identifier_count"] == 92
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011bl.q011bk.EXPECTED_INVENTORY_DIGEST
    assert fixed["active_disc_record_digest_sha256"] == (
        q011bl.q011bk.EXPECTED_ACTIVE_RECORD_DIGEST
    )
    assert fixed["monotone_disc_record_digest_sha256"] == (
        q011bl.q011bk.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011bl.q011bk.EXPECTED_HULL_RECORD_DIGEST


def test_q011bl_processes_every_registered_aggregate_once(
    q011bl_cycle: dict[str, Any],
) -> None:
    sweep = q011bl_cycle["degree_twenty_eight_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 28
    assert sweep["audited_overlap_aggregate_count"] == 1_170
    assert len(sweep["aggregate_records"]) == 1_170
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(1_170)
    )
    assert sweep["bound_matrix_record_count"] == 1_170
    assert sweep["fully_separated_overlap_aggregate_count"] <= 1_170


def test_q011bl_reproduces_preregistered_resource_identities(
    q011bl_cycle: dict[str, Any],
) -> None:
    sweep = q011bl_cycle["degree_twenty_eight_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 161
    assert sweep["group_signature_record_count"] == 810
    assert sweep["pair_pool_record_count"] == 398
    assert sweep["convolution_call_count"] == 14_505
    assert sweep["original_monomial_count"] == 53_517_100_201_931
    assert sweep["modulus_signature_count"] == 57_529
    assert sweep["maximum_live_combined_signature_count"] == 182
    assert sweep["distinct_comparison_upper_bound"] == 995_152
    assert sweep["weighted_comparison_upper_bound"] == 971_674_189_747_228
    assert sweep["maximum_convolution_crude_int64_bound"] <= 7_581_686_112_000
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011bl_cycle["registered_parameters"]
    assert registered["multi_target_aggregate_count"] == 2
    assert registered["maximum_external_component_count"] == 3
    assert registered["inactive_monotone_records_compared"] is False
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011bl_applies_the_preregistered_stopping_rule(
    q011bl_cycle: dict[str, Any],
) -> None:
    assert q011bl_cycle["study_validity"] == "passed"
    assert q011bl_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011bl_cycle["validity_gates"].values())
    assert q011bl_cycle["scientific_outcome"] == "accepted"
    assert q011bl_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011bl_cycle["hypothesis_gates"].values())
    sweep = q011bl_cycle["degree_twenty_eight_block_support_coalesced_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 1_170
    assert sweep["distinct_comparison_count"] == 929_344
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 418_956,
        "target_below_product": 510_388,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 57_716_604_325_850
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 26_932_451_117_752,
        "target_below_product": 30_784_153_208_098,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 956
    assert minimum["selected_type_counts"] == [12, 15, 1, 0]
    assert minimum["target_identifier"] == "block=12;center=143"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.2b0b5984fffffp-21"
    assert minimum["exact_gap_hex"] == "0x1.2b0b59e145674p-21"
    assert minimum["witness_digest_sha256"] == (
        "f455a3882a86972703f13bae000dced5bf47c39702edff57c6d8dbfc09f41f30"
    )
    assert q011bl_cycle["scientific_classification"] == q011bl.ACCEPTED_CLASSIFICATION
    assert (
        q011bl_cycle["actual_resonance_outcome"]
        == q011bl.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011bl_preserves_the_scientific_boundary(q011bl_cycle: dict[str, Any]) -> None:
    theorem = q011bl_cycle["theorem_consequence"]
    assert theorem["degree_twenty_eight_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_twenty_eight_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_twenty_eight_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 29))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(29, 91))
    assert theorem["q011bj_degree_twenty_seven_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 29--90" in q011bl_cycle["claim_boundary"]
    assert "inactive monotone proof records are retained but not compared" in q011bl_cycle[
        "claim_boundary"
    ]


def test_q011bl_cycle_has_strict_reproducible_digests(q011bl_cycle: dict[str, Any]) -> None:
    json.dumps(q011bl_cycle, allow_nan=False)
    assert {
        name: q011bl_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011bl_cycle["degree_twenty_eight_block_support_coalesced_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011bl_cycle["result_digest_sha256"] == q011bl.q011b._canonical_json_sha256(
        q011bl._result_digest_sections(q011bl_cycle)
    )


def test_q011bl_study_metadata_and_optional_artifact_are_scoped(
    q011bl_study: dict[str, Any],
) -> None:
    assert q011bl_study["schema_version"] == 1
    assert q011bl_study["source"] == source_metadata()
    assert q011bl_study["study_gate"] == "passed"
    assert q011bl_study["scientific_outcome"] == "accepted"
    assert q011bl_study["arithmetic_runtime"]["inactive_monotone_records_compared"] is False
    scope = q011bl_study["mathematical_scope"]
    assert scope["degree"] == 28
    assert scope["degree_twenty_nine_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011bl_study, allow_nan=False)

    runner_path = Path(q011bl.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011bl_degree28_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011bl artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011bl_degree28_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == q011bl_study["scientific_outcome"]
    assert artifact["actual_resonance_outcome"] == q011bl_study[
        "actual_resonance_outcome"
    ]
    assert artifact["cycle"]["result_digest_sha256"] == q011bl.q011b._canonical_json_sha256(
        q011bl._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
