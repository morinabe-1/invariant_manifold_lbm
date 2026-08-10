from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011aq_degree18_hierarchical_sweep as q011aq
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _artifact_path() -> Path:
    return Path(q011aq.__file__).resolve().parent / "artifacts" / (
        "q011aq_degree18_hierarchical_sweep.json"
    )


@pytest.fixture(scope="module")
def q011aq_preparation() -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, dict[str, Any]],
]:
    sealed, artifacts = q011aq._sealed_input_audit()
    preparation, *_ = q011aq._fixed_input_audit(artifacts)
    return sealed, preparation, artifacts


@pytest.fixture(scope="module")
def q011aq_study() -> dict[str, Any]:
    if not _artifact_path().exists():
        pytest.skip("Q011aq artifact has not been generated; do not run the full sweep early")
    return q011aq.run_q011aq_study()


def test_q011aq_seals_q011ap_and_all_prior_inputs(
    q011aq_preparation: tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]],
) -> None:
    sealed, _, _ = q011aq_preparation
    assert sealed["passed"]
    assert sealed["artifact_count"] == 21
    assert sealed["direct_digest_count"] == 108
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011ap"]["digests"]) == q011aq.Q011AP_DIGESTS
    assert sealed["q011ap"]["artifact_sha256"] == q011aq.Q011AP_ARTIFACT_SHA256
    assert sealed["q011ap"]["runner_sha256"] == q011aq.Q011AP_RUNNER_SHA256
    assert sealed["q011ap"]["resource_decision"] == q011aq.q011ap.GO_DECISION
    assert sealed["q011ap"]["scientific_outcome"] == "not_evaluated"


def test_q011aq_reconstructs_the_fixed_degree_eighteen_inputs_without_relations(
    q011aq_preparation: tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]],
) -> None:
    _, preparation, _ = q011aq_preparation
    assert preparation["passed"]
    assert all(preparation["checks"].values())
    assert preparation["degree"] == 18
    assert preparation["degree_aggregate_count"] == 1_330
    assert preparation["old_modulus_separated_aggregate_count"] == 1_078
    assert preparation["direct_overlap_inventory_aggregate_count"] == 252
    assert preparation["selected_source_identifier_count"] == 24
    assert preparation["external_target_identifier_count"] == 164
    assert preparation["final_identifier_count"] == 188
    assert preparation["selected_modulus_class_counts"] == [4, 2, 3, 6]
    resources = preparation["registered_resource_identity"]
    assert resources == {
        "class_power_record_count": 268,
        "group_signature_record_count": 139_922,
        "pair_pool_cache_key_count": 125,
        "cached_pair_signature_entry_count": 1_450_127,
        "exact_convolution_call_count": 2_277_951,
        "original_monomial_count": 50_931_347_136,
        "modulus_signature_count": 112_289_821,
        "peak_live_combined_signature_count": 2_102_100,
        "peak_two_product_bound_array_bytes": 33_633_600,
        "distinct_comparison_upper_bound": 996_565_068,
        "weighted_comparison_upper_bound": 485_076_664_408,
    }
    assert "no component-internal eigenvalue-to-disc label is assumed" in preparation[
        "disc_label_logic"
    ]


def test_q011aq_registered_parameters_do_not_prejudge_unobserved_outcomes() -> None:
    registered = q011aq._registered_parameters()
    assert registered["accepted_classification"] == q011aq.ACCEPTED_CLASSIFICATION
    assert registered["rejected_classification"] == q011aq.REJECTED_CLASSIFICATION
    assert not registered["unobserved_relation_counts_are_preregistered_thresholds"]
    assert not registered["unobserved_matrix_digests_are_preregistered_thresholds"]
    assert not registered["unobserved_minimum_witness_is_a_preregistered_threshold"]
    assert not registered["degrees_nineteen_through_ninety_claimed"]
    assert not registered["all_order_nonresonance_claimed"]
    assert not registered["ssm_existence_or_uniqueness_claimed"]


def test_q011aq_full_replay_matches_the_first_official_artifact(
    q011aq_study: dict[str, Any],
) -> None:
    artifact = json.loads(_artifact_path().read_text(encoding="utf-8"))
    assert _file_sha256(_artifact_path()) == (
        "246540feb2733de13f7a5a982c609aaca6188982d927d6a2f82aa50cc35f157a"
    )
    assert q011aq_study["cycle"] == artifact["cycle"]
    assert q011aq_study["source"] == source_metadata()
    assert q011aq_study["study_gate"] == "passed"
    assert q011aq_study["scientific_outcome"] in {"accepted", "rejected"}
    assert q011aq_study["actual_resonance_outcome"] in {
        q011aq.ACCEPTED_ACTUAL_RESONANCE_OUTCOME,
        "not_established",
    }
    assert artifact["runner_source"] == {
        "filename": "q011aq_degree18_hierarchical_sweep.py",
        "sha256": "358c89e86f8e6b5bb82cc47cafe553bee4549a197af57648b6e698e49d6dd52f",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(q011aq.__file__).resolve())
    assert artifact["cycle"]["result_digest_sha256"] == q011aq.q011b._canonical_json_sha256(
        q011aq._result_digest_sections(artifact["cycle"])
    )
    json.dumps(artifact, allow_nan=False)


def test_q011aq_outcome_and_claim_boundary_are_coherent(
    q011aq_study: dict[str, Any],
) -> None:
    cycle = q011aq_study["cycle"]
    sweep = cycle["degree_eighteen_hierarchical_sweep_audit"]
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert sweep["passed"]
    assert all(sweep["checks"].values())
    assert sweep["audited_overlap_aggregate_count"] == 252
    assert sweep["original_monomial_count"] == 50_931_347_136
    assert sweep["modulus_signature_count"] == 112_289_821
    assert sweep["convolution_call_count"] == 2_277_951
    assert sweep["maximum_live_combined_signature_count"] == 2_102_100
    theorem = cycle["theorem_consequence"]
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == q011aq.ACCEPTED_CLASSIFICATION
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    accepted = True
    assert theorem["degree_eighteen_external_nonresonance_is_certified"] is accepted
    assert theorem["an_actual_degree_eighteen_external_resonance_is_ruled_out"] is accepted
    if accepted:
        assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
        assert sweep["remaining_overlap_aggregate_count"] == 0
        assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 19))
        assert theorem["missing_external_nonresonance_degrees"] == list(range(19, 91))
        assert q011aq_study["actual_resonance_outcome"] == (
            q011aq.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
        )
    else:
        assert cycle["hypothesis_outcome"] == "rejected"
        assert sweep["remaining_overlap_aggregate_count"] > 0
        assert sweep["first_unresolved_witness"] is not None
        assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 18))
        assert theorem["missing_external_nonresonance_degrees"] == list(range(18, 91))
        assert q011aq_study["actual_resonance_outcome"] == "not_established"
    assert "degree-eighteen relations" in cycle["claim_boundary"]
    assert not theorem["degrees_nineteen_through_ninety_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]


def test_q011aq_first_official_counts_digests_and_minimum_are_sealed(
    q011aq_study: dict[str, Any],
) -> None:
    cycle = q011aq_study["cycle"]
    sweep = cycle["degree_eighteen_hierarchical_sweep_audit"]
    assert sweep["fully_separated_overlap_aggregate_count"] == 252
    assert sweep["remaining_overlap_aggregate_count"] == 0
    assert sweep["first_unresolved_witness"] is None
    assert sweep["compatible_modulus_signature_count"] == 105_895_597
    assert sweep["compatible_original_monomial_count"] == 12_958_923_958
    assert sweep["distinct_comparison_count"] == 694_302_588
    assert sweep["weighted_comparison_count"] == 29_855_319_268
    assert sweep["distinct_relation_counts"] == {
        "overlap": 0,
        "product_below_target": 286_270_668,
        "target_below_product": 408_031_920,
    }
    assert sweep["weighted_relation_counts"] == {
        "overlap": 0,
        "product_below_target": 13_265_995_204,
        "target_below_product": 16_589_324_064,
    }
    assert sweep["maximum_convolution_crude_int64_bound"] == 1_870
    assert sweep["maximum_wave_coefficient"] == 2_404
    assert sweep["maximum_fourier_crude_int64_bound"] == 14_960
    assert (
        sweep["aggregate_record_digest_sha256"]
        == "607d8929146ed83e6ac9a1b2896d4c78f1295860e1d3facf76115fddbcd41600"
    )
    assert (
        sweep["class_power_record_digest_sha256"]
        == "0544d674a52e9503567cc2f8c8b0799fb4174d1f38700a1b37e4eba2414e9ea5"
    )
    assert (
        sweep["group_signature_digest_sha256"]
        == "6d2c035109b7dd640bf2677f6a042977645c5d33fff00154cc1446fc97add425"
    )
    assert (
        sweep["pair_pool_record_digest_sha256"]
        == "8cd03036cbf4a04478642e28dce1eb6f2a7576bc1eabc8f7c06d97b6f6a7a84d"
    )
    assert sweep["bound_matrix_record_count"] == 252
    assert (
        sweep["bound_matrix_digest_sha256"]
        == "7c5c0f4827d6eb278c9cfeaa4282579bd43a52b1383163fecfcb61926297f402"
    )
    assert sweep["coefficient_matrix_record_count"] == 1_132
    assert (
        sweep["coefficient_matrix_digest_sha256"]
        == "99052decb2790d3bc14b4f159e85c094074bf8d61219d0632392292c26e80169"
    )
    assert sweep["classification_matrix_record_count"] == 2_728
    assert (
        sweep["classification_matrix_digest_sha256"]
        == "4d29dce45467d9b5f50102a77b43b553343a7a76fc85b8fea1ca3b643cdf9dc4"
    )
    witness = sweep["global_minimum_separated_witness"]
    assert witness["aggregate_index"] == 135
    assert witness["selected_type_counts"] == [5, 4, 4, 5]
    assert witness["target_identifier"] == "block=11;center=3"
    assert witness["left_index"] == 9
    assert witness["right_index"] == 251
    assert witness["wave_multiplicity"] == 4
    assert witness["relation"] == "target_below_product"
    assert witness["outward_gap_lower"]["binary64_hex"] == "0x1.39a9cf37fffffp-23"
    assert witness["exact_gap_hex"] == "0x1.39a9d05be5218p-23"
    assert (
        witness["witness_digest_sha256"]
        == "efe0b2b3ea7635ac39197bbfb8be7bcb1e2d5bfb811ecbdb3214532b8419e8a5"
    )
    assert {
        name: cycle[name]
        for name in (
            "input_digest_sha256",
            "preparation_digest_sha256",
            "sweep_digest_sha256",
            "result_digest_sha256",
        )
    } == {
        "input_digest_sha256": "b872654abf4e29b9c6d4fb40c6bf9e7ba5d1a05589f443b72a63bc37e338a501",
        "preparation_digest_sha256": (
            "063d871e07ce95e0bd66219544e6406a0869074e18cd3ac8e6bbb44f65208d3c"
        ),
        "sweep_digest_sha256": (
            "86ac41c9499150e6c9fa26a24924b7db71a48b8a05ade2f90c2d74ba83078d34"
        ),
        "result_digest_sha256": (
            "0011b3f04770f7b2ff4528b2db9e2c71c3455dee9db23f378a3f699b78e697d4"
        ),
    }
