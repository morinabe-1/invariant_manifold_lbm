from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ao_degree17_hierarchical_sweep as q011ao
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011ao_study() -> dict[str, Any]:
    return q011ao.run_q011ao_study()


@pytest.fixture(scope="module")
def q011ao_cycle(q011ao_study: dict[str, Any]) -> dict[str, Any]:
    return q011ao_study["cycle"]


def test_q011ao_seals_q011an_and_all_prior_inputs(
    q011ao_cycle: dict[str, Any],
) -> None:
    sealed = q011ao_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 19
    assert sealed["direct_digest_count"] == 98
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011an"]["digests"]) == q011ao.Q011AN_DIGESTS
    assert sealed["q011an"]["artifact_sha256"] == q011ao.Q011AN_ARTIFACT_SHA256
    assert sealed["q011an"]["runner_sha256"] == q011ao.Q011AN_RUNNER_SHA256


def test_q011ao_reconstructs_the_exact_degree_seventeen_inventory(
    q011ao_cycle: dict[str, Any],
) -> None:
    inventory = q011ao_cycle["degree_seventeen_inventory_audit"]
    assert inventory["passed"]
    assert all(inventory["checks"].values())
    assert inventory["degree_aggregate_count"] == 1_140
    assert inventory["degree_expanded_product_control_count"] == 26_334
    assert inventory["old_modulus_separated_aggregate_count"] == 941
    assert inventory["old_modulus_overlap_aggregate_count"] == 199
    assert inventory["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert inventory["unique_external_group_count"] == 15
    assert inventory["unique_external_target_count"] == 152
    assert inventory["multi_target_external_component_aggregate_count"] == 2
    assert inventory["maximum_external_component_count"] == 2
    assert inventory["target_identifier_block_counts"] == list(q011ao.EXPECTED_TARGET_BLOCK_COUNTS)
    assert inventory["overlap_count_tuple_digest_sha256"] == (q011ao.EXPECTED_COUNT_TUPLE_DIGEST)
    assert inventory["external_group_index_tuple_digest_sha256"] == (
        q011ao.EXPECTED_EXTERNAL_GROUP_DIGEST
    )
    assert inventory["overlap_record_digest_sha256"] == (q011ao.EXPECTED_OVERLAP_RECORD_DIGEST)
    assert inventory["external_target_record_digest_sha256"] == (
        q011ao.EXPECTED_TARGET_RECORD_DIGEST
    )
    assert inventory["exact_inventory_digest_sha256"] == q011ao.EXPECTED_INVENTORY_DIGEST


def test_q011ao_builds_the_registered_component_safe_envelope(
    q011ao_cycle: dict[str, Any],
) -> None:
    envelope = q011ao_cycle["degree_seventeen_component_safe_envelope_audit"]
    assert envelope["passed"]
    assert all(envelope["checks"].values())
    assert envelope["selected_source_identifier_count"] == 24
    assert envelope["external_target_identifier_count"] == 152
    assert envelope["reused_q011an_identifier_count"] == 152
    assert envelope["reused_q011an_selected_identifier_count"] == 24
    assert envelope["reused_q011an_target_identifier_count"] == 128
    assert envelope["new_q011ak_target_identifier_count"] == 24
    assert envelope["final_identifier_count"] == 176
    assert tuple(envelope["new_q011ak_target_identifiers"]) == q011ao.NEW_TARGET_IDENTIFIERS
    assert envelope["new_target_identifier_digest_sha256"] == (
        q011ao.EXPECTED_NEW_TARGET_IDENTIFIER_DIGEST
    )
    assert envelope["new_q011ak_target_record_digest_sha256"] == (
        q011ao.EXPECTED_NEW_TARGET_RECORD_DIGEST
    )
    assert envelope["final_disc_record_digest_sha256"] == (q011ao.EXPECTED_FINAL_RECORD_DIGEST)
    assert envelope["q011ak_formula_replay_record_count"] == 204
    assert envelope["selected_modulus_class_counts"] == [4, 2, 3, 6]
    assert envelope["selected_class_membership_digest_sha256"] == (
        q011ao.EXPECTED_CLASS_MEMBERSHIP_DIGEST
    )
    assert (
        "no component-internal eigenvalue-to-disc label is assumed" in envelope["disc_label_logic"]
    )


def test_q011ao_resource_estimate_matches_the_streaming_contract(
    q011ao_cycle: dict[str, Any],
) -> None:
    resource = q011ao_cycle["degree_seventeen_resource_estimate_audit"]
    assert resource["passed"]
    assert all(resource["checks"].values())
    assert resource["class_power_record_count"] == 238
    assert resource["group_signature_record_count"] == 104_672
    assert resource["pair_pool_cache_key_count"] == 101
    assert resource["cached_pair_signature_entry_count"] == 720_101
    assert resource["exact_convolution_call_count"] == 1_339_913
    assert resource["modulus_signature_count"] == 55_452_003
    assert resource["peak_live_combined_signature_count"] == 1_201_200
    assert resource["peak_two_product_bound_array_bytes"] == 19_219_200
    assert resource["original_monomial_count"] == 20_467_791_608
    assert not resource["full_degree_seventeen_monomial_list_retained"]
    assert not resource["full_classification_matrices_retained"]
    assert not resource["design_only_elapsed_seconds_is_an_acceptance_threshold"]
    assert not resource["design_only_measured_memory_is_an_acceptance_threshold"]


def test_q011ao_full_sweep_separates_every_registered_relation(
    q011ao_cycle: dict[str, Any],
) -> None:
    sweep = q011ao_cycle["degree_seventeen_hierarchical_sweep_audit"]
    assert sweep["passed"]
    assert all(sweep["checks"].values())
    assert sweep["degree"] == 17
    assert sweep["audited_overlap_aggregate_count"] == 199
    assert sweep["fully_separated_overlap_aggregate_count"] == 199
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["remaining_overlap_aggregate_indices"] == []
    assert sweep["original_monomial_count"] == 20_467_791_608
    assert sweep["modulus_signature_count"] == 55_452_003
    assert sweep["compatible_modulus_signature_count"] == 49_831_491
    assert sweep["compatible_original_monomial_count"] == 4_949_877_042
    assert sweep["distinct_comparison_count"] == 301_592_258
    assert sweep["weighted_comparison_count"] == 10_786_916_138
    assert sweep["distinct_relation_counts"] == q011ao.EXPECTED_DISTINCT_RELATIONS
    assert sweep["weighted_relation_counts"] == q011ao.EXPECTED_WEIGHTED_RELATIONS
    assert sweep["class_power_record_digest_sha256"] == q011ao.EXPECTED_CLASS_POWER_DIGEST
    assert sweep["group_signature_digest_sha256"] == (q011ao.EXPECTED_GROUP_SIGNATURE_DIGEST)
    assert sweep["pair_pool_record_digest_sha256"] == q011ao.EXPECTED_PAIR_POOL_DIGEST
    assert sweep["aggregate_record_digest_sha256"] == q011ao.EXPECTED_AGGREGATE_DIGEST
    assert sweep["bound_matrix_digest_sha256"] == q011ao.EXPECTED_BOUND_MATRIX_DIGEST
    assert sweep["coefficient_matrix_digest_sha256"] == (q011ao.EXPECTED_COEFFICIENT_MATRIX_DIGEST)
    assert sweep["classification_matrix_digest_sha256"] == (
        q011ao.EXPECTED_CLASSIFICATION_MATRIX_DIGEST
    )
    assert sweep["convolution_call_count"] == 1_339_913
    assert sweep["maximum_convolution_crude_int64_bound"] == 1_700
    assert sweep["maximum_live_combined_signature_count"] == 1_201_200
    assert sweep["maximum_wave_coefficient"] == 1_422
    assert sweep["maximum_fourier_crude_int64_bound"] == 10_132
    assert sweep["first_unresolved_witness"] is None
    assert sweep["degree_seventeen_bridge"] == {
        "old_modulus_separated_aggregate_count": 941,
        "directly_separated_overlap_inventory_aggregate_count": 199,
        "degree_seventeen_aggregate_count": 1_140,
        "remaining_degree_seventeen_aggregate_count": 0,
    }


def test_q011ao_global_minimum_witness_is_reproduced(
    q011ao_cycle: dict[str, Any],
) -> None:
    witness = q011ao_cycle["degree_seventeen_hierarchical_sweep_audit"][
        "global_minimum_separated_witness"
    ]
    assert witness["aggregate_index"] == 113
    assert witness["selected_type_counts"] == [5, 5, 4, 3]
    assert witness["target_identifier"] == "block=11;center=3"
    assert witness["left_index"] == 5
    assert witness["right_index"] == 55
    assert witness["wave_multiplicity"] == 15
    assert witness["relation"] == "target_below_product"
    assert tuple(tuple(group) for group in witness["class_counts"]) == (
        q011ao.EXPECTED_MINIMUM_CLASS_COUNTS
    )
    assert tuple(witness["source_identifiers"]) == q011ao.EXPECTED_MINIMUM_SOURCES
    assert witness["outward_gap_lower"]["binary64_hex"] == (q011ao.EXPECTED_MINIMUM_OUTWARD_GAP_HEX)
    assert witness["exact_gap_hex"] == q011ao.EXPECTED_MINIMUM_EXACT_GAP_HEX
    assert witness["witness_digest_sha256"] == q011ao.EXPECTED_MINIMUM_WITNESS_DIGEST


def test_q011ao_acceptance_and_claim_boundary_are_scoped(
    q011ao_cycle: dict[str, Any],
) -> None:
    assert q011ao_cycle["study_validity"] == "passed"
    assert q011ao_cycle["hypothesis_outcome"] == "accepted"
    assert q011ao_cycle["actual_resonance_outcome"] == q011ao.ACTUAL_RESONANCE_OUTCOME
    assert q011ao_cycle["scientific_classification"] == q011ao.ACCEPTED_CLASSIFICATION
    assert all(gate["passed"] for gate in q011ao_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011ao_cycle["hypothesis_gates"].values())
    theorem = q011ao_cycle["theorem_consequence"]
    assert theorem["degree_seventeen_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_seventeen_external_resonance_is_ruled_out"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 18))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(18, 91))
    assert not theorem["degrees_18_through_90_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert (
        "only within those registered degree-seventeen relations" in q011ao_cycle["claim_boundary"]
    )
    assert "Q011ap" in q011ao_cycle["next_change"]


def test_q011ao_cycle_has_strict_reproducible_digests(
    q011ao_cycle: dict[str, Any],
) -> None:
    json.dumps(q011ao_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("8a893e802bc4b93cd2f9be5da7e872b5a79a2e956a1b445386a63cd97aed9aad"),
        "inventory_digest_sha256": (
            "4806963b4e1cc0ace653881e6102dd055220b95d9d5157f1a4699f71cd85f02c"
        ),
        "envelope_digest_sha256": (
            "8eebcf226ffb9ad38d0d14f2ae42c4b89cea37c553a1b88d72dfc1ce6a4c5f50"
        ),
        "sweep_digest_sha256": ("e046e2d7675155aba98b97266dda283e4cfd3b3a22698a7e6edbad6e2dcfa9a8"),
        "result_digest_sha256": (
            "f76db860a63b31c3152ddbe8ef6ce1ea6ee58e2d62b3554895bce4a25834b746"
        ),
    }
    assert {name: q011ao_cycle[name] for name in expected} == expected
    assert q011ao_cycle["result_digest_sha256"] == (
        q011ao.q011b._canonical_json_sha256(q011ao._result_digest_sections(q011ao_cycle))
    )


def test_q011ao_study_metadata_and_generated_artifact_are_scoped(
    q011ao_study: dict[str, Any],
) -> None:
    assert q011ao_study["schema_version"] == 1
    assert q011ao_study["source"] == source_metadata()
    assert q011ao_study["study_gate"] == "passed"
    assert q011ao_study["scientific_outcome"] == "accepted"
    assert q011ao_study["actual_resonance_outcome"] == q011ao.ACTUAL_RESONANCE_OUTCOME
    scope = q011ao_study["mathematical_scope"]
    assert scope["degree"] == 17
    assert scope["degree_seventeen_external_nonresonance_claim"] is True
    assert scope["degrees_18_through_90_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ao_study, allow_nan=False)

    runner_path = Path(q011ao.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ao_degree17_hierarchical_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011ao artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == runner_path.name
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["actual_resonance_outcome"] == q011ao.ACTUAL_RESONANCE_OUTCOME
    assert artifact["cycle"]["result_digest_sha256"] == (
        q011ao.q011b._canonical_json_sha256(q011ao._result_digest_sections(artifact["cycle"]))
    )
    assert len(_file_sha256(artifact_path)) == 64
    json.dumps(artifact, allow_nan=False)
