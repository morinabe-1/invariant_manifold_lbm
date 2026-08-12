from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

import research.q011ax_degree21_coalesced_sweep as q011ax
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256

EXPECTED_RUNNER_SHA256 = "f66825a7da2875ba913378b51424cbffa2b8ffbf925f03ed0f15885621bebb1b"
EXPECTED_ARTIFACT_SHA256 = "9491de98d4e598290d18cab3397ca33c77d9a657b41c9ef2e92d720202a656f6"
EXPECTED_SECTION_DIGESTS = {
    "input_digest_sha256": "ae807c1263b3eca590f364a692d3e2b3f7b7fd4439e495c43394b032b06ff7dd",
    "preparation_digest_sha256": (
        "dbc04b7b5a74cc09aed1dbcc7dd23777e6abe7ce549f7e28b19f023dc5c1844f"
    ),
    "sweep_digest_sha256": "2f01475c317e70c9153b7d0a9dfe0d3d2e594e0baf784b4f1c4b39d732213b78",
    "result_digest_sha256": "f6e10009cb266cc0a99cdbdcafd6c38f8864bc21c2adbfd58585865115c88da2",
}
EXPECTED_SWEEP_DIGESTS = {
    "aggregate_record_digest_sha256": (
        "444a9f0603b6fd608fa44571eda8b26ca4fb0e97639c61b0ace537ba3593c4f3"
    ),
    "bound_matrix_digest_sha256": (
        "1b5d67bba1b8dd46f3ebcd6248660cad5edac9922ae975728c125ada89b2590e"
    ),
    "coefficient_matrix_digest_sha256": (
        "093d132560102afdadd6d77baa4ba09370d87df220af96b30cffe422e6d574c5"
    ),
    "classification_matrix_digest_sha256": (
        "d28efdc3ff55a69dedeaaecf946d8bec61a579aad0cafcad01df58050e5bfc52"
    ),
}


@pytest.fixture(scope="module")
def q011ax_study() -> dict[str, Any]:
    return q011ax.run_q011ax_study()


@pytest.fixture(scope="module")
def q011ax_cycle(q011ax_study: dict[str, Any]) -> dict[str, Any]:
    return q011ax_study["cycle"]


def test_q011ax_seals_q011aw_and_all_prior_inputs(q011ax_cycle: dict[str, Any]) -> None:
    sealed = q011ax_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["artifact_count"] == 28
    assert sealed["direct_digest_count"] == 140
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011aw"]["digests"]) == q011ax.Q011AW_DIGESTS
    assert sealed["q011aw"]["artifact_sha256"] == q011ax.Q011AW_ARTIFACT_SHA256
    assert sealed["q011aw"]["runner_sha256"] == q011ax.Q011AW_RUNNER_SHA256
    assert sealed["q011aw"]["degree_twenty_one_relation_evaluation_count"] == 0


def test_q011ax_reconstructs_registered_inputs_bitwise(q011ax_cycle: dict[str, Any]) -> None:
    fixed = q011ax_cycle["fixed_coalesced_input_audit"]
    assert fixed["passed"]
    assert all(fixed["checks"].values())
    assert fixed["degree"] == 21
    assert fixed["degree_aggregate_count"] == 2_024
    assert fixed["old_modulus_separated_aggregate_count"] == 1_660
    assert fixed["direct_overlap_aggregate_count"] == 364
    assert fixed["selected_identifier_count"] == 24
    assert fixed["target_identifier_count"] == 228
    assert fixed["final_identifier_count"] == 252
    assert fixed["merged_class_counts"] == [1, 1, 2, 2]
    assert fixed["inventory_digest_sha256"] == q011ax.q011aw.EXPECTED_INVENTORY_DIGEST
    assert fixed["final_disc_record_digest_sha256"] == (
        q011ax.q011aw.EXPECTED_FINAL_RECORD_DIGEST
    )
    assert fixed["hull_record_digest_sha256"] == q011ax.q011aw.EXPECTED_HULL_RECORD_DIGEST
    assert fixed["merged_class_membership_digest_sha256"] == (
        q011ax.q011aw.EXPECTED_MERGED_MEMBERSHIP_DIGEST
    )


def test_q011ax_processes_every_registered_aggregate_once(
    q011ax_cycle: dict[str, Any],
) -> None:
    sweep = q011ax_cycle["degree_twenty_one_block_support_coalesced_sweep"]
    assert sweep["registered_passed"]
    assert all(sweep["registered_checks"].values())
    assert sweep["degree"] == 21
    assert sweep["audited_overlap_aggregate_count"] == 364
    assert len(sweep["aggregate_records"]) == 364
    assert [record["aggregate_index"] for record in sweep["aggregate_records"]] == list(
        range(364)
    )
    assert sweep["bound_matrix_record_count"] == 364
    assert sweep["fully_separated_overlap_aggregate_count"] <= 364


def test_q011ax_reproduces_preregistered_resource_identities(
    q011ax_cycle: dict[str, Any],
) -> None:
    sweep = q011ax_cycle["degree_twenty_one_block_support_coalesced_sweep"]
    assert sweep["class_power_record_count"] == 121
    assert sweep["group_signature_record_count"] == 482
    assert sweep["pair_pool_record_count"] == 192
    assert sweep["convolution_call_count"] == 6_448
    assert sweep["original_monomial_count"] == 294_674_427_372
    assert sweep["modulus_signature_count"] == 12_458
    assert sweep["maximum_live_combined_signature_count"] == 126
    assert sweep["distinct_comparison_upper_bound"] == 146_928
    assert sweep["weighted_comparison_upper_bound"] == 3_951_865_509_552
    assert sweep["maximum_convolution_crude_int64_bound"] <= 133_491_072_000
    assert sweep["maximum_fourier_crude_int64_bound"] < 2**63
    registered = q011ax_cycle["registered_parameters"]
    assert registered["full_monomial_list_retained"] is False
    assert registered["full_classification_matrices_retained"] is False


def test_q011ax_validity_and_preregistered_stopping_rule(
    q011ax_cycle: dict[str, Any],
) -> None:
    assert q011ax_cycle["study_validity"] == "passed"
    assert q011ax_cycle["failed_validity_order"] == []
    assert all(gate["passed"] for gate in q011ax_cycle["validity_gates"].values())
    assert q011ax_cycle["scientific_outcome"] == "accepted"
    sweep = q011ax_cycle["degree_twenty_one_block_support_coalesced_sweep"]
    assert q011ax_cycle["failed_hypothesis_order"] == []
    assert all(gate["passed"] for gate in q011ax_cycle["hypothesis_gates"].values())
    assert sweep["fully_separated_overlap_aggregate_count"] == 364
    assert sweep["distinct_comparison_count"] == 123_690
    assert sweep["distinct_relation_counts"] == {
        "product_below_target": 42_998,
        "target_below_product": 80_692,
        "overlap": 0,
    }
    assert sweep["weighted_comparison_count"] == 242_133_612_486
    assert sweep["weighted_relation_counts"] == {
        "product_below_target": 128_472_523_232,
        "target_below_product": 113_661_089_254,
        "overlap": 0,
    }
    assert sweep["first_unresolved_witness"] is None
    for name, digest in EXPECTED_SWEEP_DIGESTS.items():
        assert sweep[name] == digest
    minimum = sweep["global_minimum_separated_witness"]
    assert minimum["aggregate_index"] == 226
    assert minimum["selected_type_counts"] == [5, 1, 4, 11]
    assert minimum["target_identifier"] == "block=11;center=3"
    assert minimum["relation"] == "target_below_product"
    assert minimum["outward_gap_lower"]["binary64_hex"] == "0x1.c510b8f1fffffp-22"
    assert minimum["exact_gap_hex"] == "0x1.c510b99b5cafep-22"
    assert minimum["witness_digest_sha256"] == (
        "7439d084e1d5ace037acc0b81b17a87b5efbe544561c52429f6ebb4548478dfc"
    )
    assert q011ax_cycle["scientific_classification"] == q011ax.ACCEPTED_CLASSIFICATION
    assert q011ax_cycle["actual_resonance_outcome"] == (
        q011ax.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )


def test_q011ax_preserves_the_scientific_boundary(q011ax_cycle: dict[str, Any]) -> None:
    theorem = q011ax_cycle["theorem_consequence"]
    assert theorem["degree_twenty_one_external_nonresonance_is_certified"]
    assert theorem["an_actual_degree_twenty_one_external_resonance_is_ruled_out"]
    assert not theorem["registered_degree_twenty_one_sufficient_certificate_is_rejected"]
    assert theorem["certified_external_nonresonance_degrees"] == list(range(2, 22))
    assert theorem["missing_external_nonresonance_degrees"] == list(range(22, 91))
    assert theorem["q011av_degree_twenty_certificate_is_preserved"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "degrees 22--90" in q011ax_cycle["claim_boundary"]


def test_q011ax_cycle_has_strict_reproducible_digests(q011ax_cycle: dict[str, Any]) -> None:
    json.dumps(q011ax_cycle, allow_nan=False)
    for name, digest in EXPECTED_SECTION_DIGESTS.items():
        assert q011ax_cycle[name] == digest
    assert q011ax_cycle["result_digest_sha256"] == q011ax.q011b._canonical_json_sha256(
        q011ax._result_digest_sections(q011ax_cycle)
    )


def test_q011ax_study_metadata_and_optional_artifact_are_scoped(
    q011ax_study: dict[str, Any],
) -> None:
    assert q011ax_study["schema_version"] == 1
    assert q011ax_study["source"] == source_metadata()
    assert q011ax_study["study_gate"] == "passed"
    assert q011ax_study["scientific_outcome"] == "accepted"
    scope = q011ax_study["mathematical_scope"]
    assert scope["degree"] == 21
    assert scope["degree_twenty_two_or_higher_claim"] is False
    assert scope["all_order_nonresonance_claim"] is False
    assert scope["ssm_uniqueness_claim"] is False
    json.dumps(q011ax_study, allow_nan=False)

    runner_path = Path(q011ax.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011ax_degree21_coalesced_sweep.json"
    if not artifact_path.exists():
        pytest.skip("Q011ax artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == "q011ax_degree21_coalesced_sweep.py"
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["runner_source"]["sha256"] == EXPECTED_RUNNER_SHA256
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["actual_resonance_outcome"] == (
        q011ax.ACCEPTED_ACTUAL_RESONANCE_OUTCOME
    )
    assert artifact["cycle"]["result_digest_sha256"] == q011ax.q011b._canonical_json_sha256(
        q011ax._result_digest_sections(artifact["cycle"])
    )
    assert _file_sha256(artifact_path) == EXPECTED_ARTIFACT_SHA256
    json.dumps(artifact, allow_nan=False)
