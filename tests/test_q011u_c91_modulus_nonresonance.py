from __future__ import annotations

import json
from fractions import Fraction
from math import comb, factorial
from pathlib import Path
from typing import Any

import pytest

import research.q011u_c91_modulus_nonresonance as q011u
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011u_cycle() -> dict[str, Any]:
    return q011u.run_c91_modulus_nonresonance_audit()


def test_q011u_seals_four_direct_inputs_twenty_one_digests_and_q007i_source(
    q011u_cycle: dict[str, Any],
) -> None:
    audit = q011u_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 21
    assert {
        label: audit[label]["hypothesis_outcome"]
        for label in ("q011j", "q011k", "q011m", "q011t")
    } == {
        "q011j": "accepted",
        "q011k": "accepted",
        "q011m": "accepted",
        "q011t": "accepted",
    }
    assert audit["q007i_rational_log_source"]["sha256"] == q011u.Q007I_SOURCE_SHA256
    assert audit["checks"]["q011j_fixed_point_scope_is_preserved"]
    assert audit["checks"]["q011k_spectral_scope_is_preserved"]
    assert audit["checks"]["q011m_analytic_derivative_scope_is_preserved"]
    assert audit["checks"]["q011t_c1_graph_and_missing_degree_scope_is_preserved"]


def test_q011u_c91_beta_polynomial_has_exact_normalization_and_flat_endpoints(
    q011u_cycle: dict[str, Any],
) -> None:
    audit = q011u_cycle["c91_scalar_localization_audit"]
    polynomial = audit["beta_polynomial"]
    cutoff = audit["scalar_c91_localization"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert polynomial["coefficient_count"] == 92
    assert _fraction(polynomial["normalizer"]) == Fraction(
        factorial(183), factorial(91) ** 2
    )
    assert _fraction(polynomial["value_at_zero"]) == 0
    assert _fraction(polynomial["value_at_one"]) == 1
    assert polynomial["derivative_identity_reproduces"]
    assert polynomial["endpoint_derivative_order_range"] == [1, 91]
    assert polynomial["endpoint_derivative_count"] == 91
    assert polynomial["all_endpoint_derivatives_are_zero"]
    assert cutoff["is_c91_across_both_transition_endpoints"]
    assert cutoff["identity_on_closed_radius_r_ball"]
    assert cutoff["support_factor_upper"] == 4
    assert cutoff["preserves_conjugacy_fixed_real_space"]
    assert cutoff["preserves_selected_and_external_real_subspaces"]
    assert not cutoff["quantitative_high_derivative_graph_transform_cap_is_claimed"]
    assert not cutoff["q011t_graph_equality_is_claimed"]
    assert audit["exact_cutoff_record_digest_sha256"] == (
        "4e6d2f9962271394639bc8a8aad56ec5f379d94220e48c3ef8a80d62ba5d1051"
    )


def test_q011u_reconstructs_and_merges_every_registered_modulus_interval(
    q011u_cycle: dict[str, Any],
) -> None:
    audit = q011u_cycle["exact_modulus_compression_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["individual_modulus_interval_count"] == 2598
    assert audit["selected_individual_interval_count"] == 24
    assert audit["external_individual_interval_count"] == 2574
    assert audit["selected_merged_interval_count"] == 4
    assert audit["selected_group_multiplicities"] == [8, 4, 4, 8]
    assert audit["external_merged_interval_count"] == 186
    assert len(audit["block_records"]) == 17
    assert [record["dimension"] for record in audit["block_records"]] == [150] + [153] * 16
    assert _fraction(audit["minimum_selected_component_gap"]) > 0
    assert _fraction(audit["minimum_external_component_gap"]) > 0
    assert audit["exact_individual_modulus_interval_digest_sha256"] == (
        "120d9214caa90d3eff168fca272ce8da3ee47eb5e11cbd65b0d462139b2d73fb"
    )
    assert audit["exact_compression_record_digest_sha256"] == (
        "57c9dd6cc7a3d3ab422698cf77a964036fbc2e4116f3ff79a0b7822f9fec7963"
    )


def test_q011u_uses_the_sealed_rational_log_algorithm_and_outward_grids(
    q011u_cycle: dict[str, Any],
) -> None:
    audit = q011u_cycle["rational_log_enclosure_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["series_terms"] == 96
    assert audit["internal_outward_decimal_digits"] == 110
    assert audit["final_outward_decimal_digits"] == 60
    assert len(audit["selected_log_records"]) == 4
    assert len(audit["external_log_records"]) == 186
    assert _fraction(audit["maximum_endpoint_tail_bound"]) <= Fraction(1, 10**90)
    assert audit["exact_log_record_digest_sha256"] == (
        "a4e193d4314674636d7f20e3b50c792ed1844a981d0438b021cef760bf6e19a5"
    )


def test_q011u_enumerates_all_registered_products_and_finds_exact_overlaps(
    q011u_cycle: dict[str, Any],
) -> None:
    audit = q011u_cycle["degree_3_through_90_enumeration_audit"]
    records = audit["degree_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_range"] == [3, 90]
    assert audit["degree_count"] == 88
    assert audit["aggregate_count"] == 3_049_486
    assert audit["aggregate_count"] == sum(comb(degree + 3, 3) for degree in range(3, 91))
    assert audit["expanded_product_control_count"] == 927_048_276
    assert audit["expanded_product_control_count"] == sum(
        comb(degree + 5, 5) for degree in range(3, 91)
    )
    assert audit["overlap_count"] == 423_729
    assert audit["nonoverlap_count"] == 2_625_757
    assert records[0]["degree"] == 3
    assert records[0]["overlap_count"] == 1
    assert records[-1]["degree"] == 90
    assert records[-1]["overlap_count"] == 2
    assert _fraction(audit["global_minimum_nonoverlap_log_gap"]) > Fraction(1, 10**12)
    assert audit["degree_record_digest_sha256"] == (
        "f23f333ea13a8d6542928ad812419ce72a2ecaac40694b38ccbc3add5657541a"
    )


def test_q011u_records_the_first_overlap_without_calling_it_a_resonance(
    q011u_cycle: dict[str, Any],
) -> None:
    audit = q011u_cycle["degree_3_through_90_enumeration_audit"]
    witness = audit["first_overlap"]

    assert witness["degree"] == 3
    assert witness["selected_type_counts"] == [0, 1, 1, 1]
    assert witness["external_group_index"] == 183
    aggregate = witness["aggregate_log_interval"]
    external = witness["external_log_interval"]
    assert int(aggregate["lower_scaled_integer"]) <= int(external["upper_scaled_integer"])
    assert int(external["lower_scaled_integer"]) <= int(aggregate["upper_scaled_integer"])
    assert witness["external_source_interval_count"] == 8
    assert "does not prove an actual complex resonance" in audit["overlap_interpretation"]


def test_q011u_certifies_degree_two_and_the_degree_91_tail(
    q011u_cycle: dict[str, Any],
) -> None:
    audit = q011u_cycle["degree_2_and_91_tail_audit"]
    selected_upper = _fraction(audit["selected_modulus_upper"])
    external_lower = _fraction(audit["external_modulus_lower"])
    tail_ratio = _fraction(audit["degree_91_tail_ratio"])

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree_two_certificate"] == {
        "certified": True,
        "unordered_pair_count": 300,
    }
    assert audit["tail_start_degree"] == 91
    assert tail_ratio == selected_upper**91 / external_lower
    assert tail_ratio <= Fraction(999, 1000)
    assert selected_upper < 1
    assert audit["all_degrees_at_least_91_are_modulus_separated"]
    assert audit["analytic_local_diffeomorphism_assumptions"][
        "analytic_inverse_function_theorem_applies_locally"
    ]


def test_q011u_validly_rejects_only_the_modulus_only_nonresonance_route(
    q011u_cycle: dict[str, Any],
) -> None:
    theorem = q011u_cycle["theorem_consequence"]

    assert q011u_cycle["study_validity"] == "passed"
    assert q011u_cycle["hypothesis_outcome"] == "rejected"
    assert q011u_cycle["scientific_classification"] == q011u.REJECTED_CLASSIFICATION
    assert len(q011u_cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in q011u_cycle["validity_gates"].values())
    assert len(q011u_cycle["hypothesis_gates"]) == 5
    assert q011u_cycle["failed_hypothesis_order"] == [
        "all_degree_3_through_90_aggregates_have_zero_external_modulus_overlap",
        "zero_overlap_global_minimum_log_gap_fits_registered_floor",
        "degree_two_middle_degrees_tail_and_local_diffeomorphism_are_complete",
    ]
    assert theorem[
        "a_c91_scalar_localization_matching_the_original_map_near_origin_is_certified"
    ]
    assert theorem["the_degree_91_and_higher_modulus_tail_is_certified"]
    assert theorem["degree_two_phase_sensitive_nonresonance_is_preserved"]
    assert not theorem["degrees_3_through_90_modulus_only_nonresonance_is_certified"]
    assert not theorem["the_registered_c91_spectral_subspace_theorem_applies"]
    assert not theorem["an_actual_complex_resonance_is_established"]
    assert not theorem["an_analytic_invariant_manifold_is_disproved"]
    assert not theorem["the_q011t_c1_graph_is_disproved_or_shown_nonsmooth"]
    assert "not an actual complex resonance" in q011u_cycle["claim_boundary"]
    assert "Q011v" in q011u_cycle["next_change"]


def test_q011u_cycle_has_reproducible_strict_json_digests(
    q011u_cycle: dict[str, Any],
) -> None:
    json.dumps(q011u_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "ba768da7be5663c607a24fa4a399bae06a8d8b4128a45ab9bb2b57f8a12461f4"
        ),
        "cutoff_digest_sha256": (
            "55a374a5d91d2c88e5e34be2173f9861ee14915daaee55efd8848f0cd7ebaf94"
        ),
        "spectrum_digest_sha256": (
            "a514c3a13142d379886c56b08109f28b69aee4cbcef2d4c5c9bed8d29182e89d"
        ),
        "log_digest_sha256": (
            "10f9aa954446e1e7d8095488ef82abc48fcc99fde3ddabd93a1a188b17ea51b5"
        ),
        "enumeration_digest_sha256": (
            "5c94deb8acd69b1346e6d46af829804b401027ecea48caf7e5ce2d9b22d6631c"
        ),
        "tail_digest_sha256": (
            "307ca2762bb5aecb626983acb8d38eb5728e2a8eb9e64769cc0b632b40da66c6"
        ),
        "result_digest_sha256": (
            "b005bb622e7f3abad98a1ef6875af289fa2dccdc16911faf11e7ee04b822722c"
        ),
    }
    assert {name: q011u_cycle[name] for name in expected} == expected
    assert q011u_cycle["result_digest_sha256"] == q011u.q011b._canonical_json_sha256(
        q011u._result_digest_sections(q011u_cycle)
    )


def test_q011u_artifact_records_the_valid_rejection_if_generated() -> None:
    runner_path = Path(q011u.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011u_c91_modulus_nonresonance.json"
    if not artifact_path.exists():
        pytest.skip("Q011u artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "4e0a74cffaeb6781b85621362d4463ac8d9ab98ee14bcf3b5764642b5a15d5e4"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011u_c91_modulus_nonresonance.py",
        "sha256": "fa3c7c01355c0b3c19b58618fe97edc5863dc2d0fa02c4f810ddbc57053a419e",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert cycle["scientific_classification"] == q011u.REJECTED_CLASSIFICATION
    assert cycle["result_digest_sha256"] == q011u.q011b._canonical_json_sha256(
        q011u._result_digest_sections(cycle)
    )
    json.dumps(artifact, allow_nan=False)
