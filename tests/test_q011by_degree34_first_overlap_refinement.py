from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

import research.q011by_degree34_first_overlap_refinement as q011by
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "34c251bb967561ab48f301df5ff872962c5cac8ac670b80595d3a5f60e4bb9cd"
EXPECTED_ARTIFACT_SHA256: str | None = (
    "f3bae947808b5417ca784d29a457697e25c2f06216887e2396828bea8fb66064"
)
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "9b44a32d229109b82f988030c9deaaa47c306ec8464fe9e920bf241b64bfdd05",
    "refinement_input_digest_sha256": (
        "45438704eb7c67a2f532507b17642a7d9e4a35e2313f2eace27fee647c52a22c"
    ),
    "targeted_sweep_digest_sha256": (
        "17a7eb73c45a30f9bd7bc4e4c00306483934000e1a0ac402e1dec481d2fb0b30"
    ),
    "result_digest_sha256": "81b6ad97a518722a9cc139d64d8938439470d98e14856df1873c6b45176b7fc1",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "54a6b854a22b2030db3c90e2d2bf53091eb098fdfee3c508f4d18cfe2e9f912c"
    ),
    "class_power_record_digest_sha256": (
        "7fe767dbaff93f82f77c97dbf97b6299a95b760ff4162a3adce1baaea80711e8"
    ),
    "group_signature_digest_sha256": (
        "356811cb59d987c26cb3d349cd83c69d11201093236b6e24187b5aaba77b129a"
    ),
    "pair_pool_record_digest_sha256": (
        "b7267b0a72c2d339f53c7eab69e00c50a24c54b5f4c5da74513fbf13e7bbea31"
    ),
    "bound_matrix_digest_sha256": (
        "d403cfe8ca6d0f79495288b74c5eea8ec9af629188c99b9cef532654ff637b85"
    ),
    "coefficient_matrix_digest_sha256": (
        "6fe198aa1ab2cc70f9aa7abcf772fbe9272a22dd61d45f408b9a247f07c89767"
    ),
    "classification_matrix_digest_sha256": (
        "a65dd041ff135fcb2b15de896b19ee5cc07e198ab9bd1919315782d3e31a09e9"
    ),
}


@pytest.fixture(scope="module")
def q011by_study() -> dict[str, Any]:
    return q011by.run_q011by_study()


@pytest.fixture(scope="module")
def q011by_cycle(q011by_study: dict[str, Any]) -> dict[str, Any]:
    return q011by_study["cycle"]


def test_q011by_seals_q011bx_and_all_prior_inputs(q011by_cycle: dict[str, Any]) -> None:
    sealed = q011by_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 55
    assert sealed["direct_digest_count"] == 261
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011bx"]["digests"]) == q011by.Q011BX_DIGESTS
    assert sealed["q011bx"]["artifact_sha256"] == q011by.Q011BX_ARTIFACT_SHA256
    assert sealed["q011bx"]["runner_sha256"] == q011by.Q011BX_RUNNER_SHA256
    first = sealed["q011bx"]["first_unresolved_witness"]
    assert first["aggregate_index"] == 972
    assert first["witness_digest_sha256"] == q011by.EXPECTED_FIRST_WITNESS_DIGEST


def test_q011by_reconstructs_the_registered_refinement(
    q011by_cycle: dict[str, Any],
) -> None:
    fixed = q011by_cycle["fixed_uncoalesced_refinement_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["parent_aggregate_index"] == 972
    assert fixed["selected_type_counts"] == [4, 27, 3, 0]
    assert fixed["target_identifier"] == "block=12;center=124"
    assert fixed["parent_external_group_indices"] == [71]
    assert fixed["parent_target_identifier_count"] == 24
    assert fixed["uncoalesced_class_counts"] == [4, 2, 3, 6]
    assert fixed["uncoalesced_class_membership_digest_sha256"] == (
        q011by.EXPECTED_CLASS_RECORD_DIGEST
    )
    assert fixed["selected_identifier_digest_sha256"] == (
        q011by.EXPECTED_SELECTED_IDENTIFIER_DIGEST
    )
    assert fixed["selected_record_digest_sha256"] == q011by.EXPECTED_SELECTED_RECORD_DIGEST
    assert fixed["target_record_digest_sha256"] == q011by.EXPECTED_TARGET_RECORD_DIGEST
    assert fixed["uncoalesced_class_signature_upper_bound"] == 9_800
    assert fixed["individual_source_monomial_upper_bound"] == 26_796_000
    assert fixed["other_parent_targets_recomputed"] is False
    assert fixed["second_q011bx_overlap_recomputed"] is False


def test_q011by_processes_only_the_registered_relation(
    q011by_cycle: dict[str, Any],
) -> None:
    sweep = q011by_cycle["targeted_uncoalesced_blockwise_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 34
    assert sweep["audited_overlap_aggregate_count"] == 1
    assert sweep["parent_q011bx_aggregate_index"] == 972
    assert sweep["aggregate_records"][0]["parent_q011bx_aggregate_index"] == 972
    assert sweep["aggregate_records"][0]["external_group_indices"] == [71]
    assert sweep["aggregate_records"][0]["target_identifier_count"] == 1
    assert sweep["bound_matrix_record_count"] == 1
    assert sweep["coefficient_matrix_record_count"] == 1
    assert sweep["classification_matrix_record_count"] == 1
    assert sweep["original_monomial_count"] == 26_796_000
    assert sweep["modulus_signature_count"] == 9_800
    assert sweep["compatible_modulus_signature_count"] == 9_800
    assert sweep["distinct_comparison_count"] == 9_800
    assert sweep["weighted_comparison_count"] == 1_570_380
    assert sweep["class_power_record_count"] == 94
    assert sweep["group_signature_record_count"] == 74
    assert sweep["pair_pool_record_count"] == 2
    assert sweep["convolution_call_count"] == 1_222
    assert sweep["maximum_convolution_crude_int64_bound"] == 1_428
    assert sweep["maximum_fourier_crude_int64_bound"] == 3_689
    assert sweep["maximum_wave_coefficient"] == 768


def test_q011by_records_persistence_without_a_resonance_claim(
    q011by_cycle: dict[str, Any],
) -> None:
    assert q011by_cycle["study_validity"] == "passed"
    assert q011by_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011by_cycle["validity_gates"].values())
    assert q011by_cycle["refinement_outcome"] == "persistent"
    assert q011by_cycle["diagnostic_classification"] == q011by.PERSISTENT_CLASSIFICATION
    assert q011by_cycle["scientific_outcome"] == "not_evaluated"
    assert q011by_cycle["actual_resonance_outcome"] == "not_established"
    assert q011by_cycle["failed_diagnostic_order"] == [
        "every_uncoalesced_subclass_comparison_is_strict",
        "global_minimum_outward_and_exact_gaps_are_positive",
    ]
    sweep = q011by_cycle["targeted_uncoalesced_blockwise_sweep"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 0
    assert sweep["remaining_overlap_aggregate_count"] == 1
    assert sweep["remaining_overlap_aggregate_indices"] == [0]
    assert sweep["separated_comparison_exists"] is False
    assert sweep["global_minimum_separated_witness"] is None
    assert sweep["distinct_relation_counts"] == {
        "overlap": 9_800,
        "product_below_target": 0,
        "target_below_product": 0,
    }
    assert sweep["weighted_relation_counts"] == {
        "overlap": 1_570_380,
        "product_below_target": 0,
        "target_below_product": 0,
    }


def test_q011by_records_the_first_exact_persistent_witness(
    q011by_cycle: dict[str, Any],
) -> None:
    witness = q011by_cycle["targeted_uncoalesced_blockwise_sweep"][
        "first_unresolved_witness"
    ]
    assert witness is not None
    assert witness["aggregate_index"] == 0
    assert witness["selected_type_counts"] == [4, 27, 3, 0]
    assert witness["target_identifier"] == "block=12;center=124"
    assert witness["output_block"] == 12
    assert witness["left_index"] == witness["right_index"] == 0
    assert witness["wave_multiplicity"] == 39
    assert witness["relation"] == "overlap"
    assert witness["class_counts"] == [
        [0, 0, 0, 4],
        [0, 27],
        [0, 0, 3],
        [0, 0, 0, 0, 0, 0],
    ]
    assert Counter(witness["source_identifiers"]) == {
        "block=16;center=145": 4,
        "block=16;center=151": 24,
        "block=1;center=151": 3,
        "block=1;center=152": 3,
    }
    assert witness["intersection_interval"]["width_hex"] == "0x1.3a21ae03356a4p-28"
    assert witness["center_only_diagnostic"]["relation"] == "target_below_product"
    assert witness["center_only_diagnostic"]["gap_hex"] == "0x1.b808da9a742c2p-27"
    assert witness["witness_digest_sha256"] == (
        "8137019a4a58e788c37a789b4e69533eef687941ac14ac8f8bb58acf568d9f69"
    )


def test_q011by_preserves_the_scientific_boundary(q011by_cycle: dict[str, Any]) -> None:
    theorem = q011by_cycle["theorem_consequence"]
    assert not theorem["first_q011bx_overlap_is_resolved_by_registered_partition"]
    assert theorem["first_q011bx_overlap_persists_under_registered_partition"]
    assert theorem["q011bx_degree_thirty_four_sufficient_certificate_remains_rejected"]
    assert not theorem["degree_thirty_four_external_nonresonance_is_certified"]
    assert not theorem["an_actual_degree_thirty_four_external_resonance_is_established"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 34))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(34, 91))
    assert theorem["second_q011bx_overlap_is_audited"] is False
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "does not re-audit the other twenty-three parent targets" in q011by_cycle[
        "claim_boundary"
    ]
    assert "actual resonance" in q011by_cycle["claim_boundary"]


def test_q011by_cycle_has_strict_reproducible_digests(q011by_cycle: dict[str, Any]) -> None:
    json.dumps(q011by_cycle, allow_nan=False)
    assert {
        name: q011by_cycle[name] for name in EXPECTED_SECTION_DIGESTS
    } == EXPECTED_SECTION_DIGESTS
    sweep = q011by_cycle["targeted_uncoalesced_blockwise_sweep"]
    assert {name: sweep[name] for name in EXPECTED_SWEEP_DIGESTS} == EXPECTED_SWEEP_DIGESTS
    assert q011by_cycle["result_digest_sha256"] == q011by.q011b._canonical_json_sha256(
        q011by._result_digest_sections(q011by_cycle)
    )


def test_q011by_study_metadata_and_optional_artifact_are_scoped(
    q011by_study: dict[str, Any],
) -> None:
    assert q011by_study["schema_version"] == 1
    assert q011by_study["source"] == source_metadata()
    assert q011by_study["study_gate"] == "passed"
    assert q011by_study["refinement_outcome"] == "persistent"
    assert q011by_study["scientific_outcome"] == "not_evaluated"
    assert q011by_study["actual_resonance_outcome"] == "not_established"
    assert q011by_study["arithmetic_runtime"]["target_comparisons"] == (
        "one fixed target disc without folding"
    )
    scope = q011by_study["mathematical_scope"]
    assert scope["degree"] == 34
    assert scope["parent_aggregate_index"] == 972
    assert scope["target_identifier"] == "block=12;center=124"
    assert scope["degree_thirty_four_nonresonance_claim"] is False
    assert scope["actual_resonance_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011by_study, allow_nan=False)

    runner_path = Path(q011by.__file__).resolve()
    assert _file_sha256(runner_path) == EXPECTED_RUNNER_SHA256
    artifact_path = runner_path.parent / "artifacts" / (
        "q011by_degree34_first_overlap_refinement.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011by artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == (
        "q011by_degree34_first_overlap_refinement.py"
    )
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["refinement_outcome"] == "persistent"
    assert artifact["scientific_outcome"] == "not_evaluated"
    assert artifact["actual_resonance_outcome"] == "not_established"
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011by.q011b._canonical_json_sha256(q011by._result_digest_sections(artifact["cycle"]))
    )
    assert EXPECTED_ARTIFACT_SHA256 is not None
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
