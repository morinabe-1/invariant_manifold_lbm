from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011t_c1_tangent_graph as q011t
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011t_cycle() -> dict[str, Any]:
    return q011t.run_c1_tangent_graph_audit()


def test_q011t_seals_five_direct_inputs_and_twenty_five_digests(
    q011t_cycle: dict[str, Any],
) -> None:
    audit = q011t_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 25
    assert {
        label: audit[label]["hypothesis_outcome"]
        for label in ("q011k", "q011m", "q011q", "q011r", "q011s")
    } == {
        "q011k": "accepted",
        "q011m": "accepted",
        "q011q": "accepted",
        "q011r": "accepted",
        "q011s": "accepted",
    }
    assert audit["checks"]["q011k_spectral_scope_is_preserved"]
    assert audit["checks"]["q011m_derivative_scope_is_preserved"]
    assert audit["checks"]["q011q_real_coordinate_scope_is_preserved"]
    assert audit["checks"]["q011r_lipschitz_localization_scope_is_preserved"]
    assert audit["checks"]["q011s_original_lipschitz_core_scope_is_preserved"]


def test_q011t_scalar_cutoff_is_c1_real_typed_and_has_exact_caps(
    q011t_cycle: dict[str, Any],
) -> None:
    audit = q011t_cycle["scalar_c1_localization_audit"]
    bump = audit["scalar_c1_bump"]
    cutoff = audit["smooth_scalar_cutoff"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert bump["is_c1_across_both_endpoints"]
    assert _fraction(bump["absolute_derivative_upper"]) == Fraction(1, 2)
    assert _fraction(cutoff["identity_ratio_upper"]) == Fraction(1299, 32768)
    assert cutoff["identity_on_closed_radius_r_ball"]
    assert cutoff["support_factor_upper"] == 4
    assert _fraction(cutoff["global_derivative_norm_upper"]) == 129
    assert cutoff["preserves_conjugacy_fixed_real_space"]
    assert cutoff["preserves_selected_and_external_real_subspaces"]
    assert not cutoff["componentwise_disk_projection_is_used"]
    assert not cutoff["q011r_nonsmooth_radial_retraction_is_used"]
    assert audit["exact_cutoff_record_digest_sha256"] == (
        "85d341171d487328b5a7aecf3a3ca05a9a3914c78a0b18843f1fe34e2782d5cd"
    )


def test_q011t_c1_graph_and_fiber_transform_are_explicitly_typed(
    q011t_cycle: dict[str, Any],
) -> None:
    audit = q011t_cycle["c1_graph_transform_definition_audit"]
    graph_space = audit["c1_graph_space"]
    base = audit["global_c1_base_inverse"]
    transform = audit["c1_graph_transform"]
    fiber = audit["fiber_contraction_theorem"]
    tangent = audit["origin_derivative_and_tangent"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert graph_space["ambient_space"] == "C_b^1(S_R,E_R)"
    assert graph_space["closed_complete_space"]
    assert base["global_fixed_point_inverse_is_combined_with_c1_inverse_theorem"]
    assert base["finite_dimensional_surjectivity_is_not_assumed"]
    assert "D(T_r psi)" in transform["derivative_formula"]
    assert not transform["direct_c1_norm_contraction_is_assumed"]
    assert fiber["fiber_contraction_theorem_yields_a_c1_fixed_graph"]
    assert not fiber["direct_c1_norm_contraction_is_required"]
    assert tangent["fiber_fixed_point_uniqueness_implies_Dpsi_origin_zero"]
    assert not tangent["q011s_lipschitz_graph_equality_is_assumed"]
    assert audit["exact_graph_constant_digest_sha256"] == (
        "8779d34eedf5d8488348a822fe94339feb3e19fdb4c9f35fd394d05ca6007e32"
    )


def test_q011t_campaign_selects_the_largest_registered_c1_scale(
    q011t_cycle: dict[str, Any],
) -> None:
    audit = q011t_cycle["c1_radius_campaign_audit"]
    records = audit["radius_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["monotonicity_checks"].values())
    assert len(records) == 11
    assert [record["passed"] for record in records] == [
        False,
        False,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
        True,
    ]
    assert audit["passing_scale_count"] == 9
    assert _fraction(audit["selected_scale"]) == Fraction(1, 256)
    assert _fraction(audit["selected_radius"]) == Fraction(3, 256 * 10**16)
    assert _fraction(audit["first_failed_larger_radius"]) == Fraction(3, 128 * 10**16)
    assert audit["first_failed_larger_constraints"] == [
        "localized_derivative_fits_cap",
        "c1_graph_slope_fits_cap",
        "derivative_fiber_contraction_fits_cap",
        "input_graph_is_in_smooth_cutoff_identity_core",
    ]
    assert audit["exact_radius_record_digest_sha256"] == (
        "18c3cd9dd25ee3505d0ac1e85f28ee626ce0aea7354c4431ca6a6829df5bb907"
    )


def test_q011t_selected_scale_reproduces_graph_and_original_core_formulas(
    q011t_cycle: dict[str, Any],
) -> None:
    graph = q011t_cycle["c1_graph_transform_definition_audit"]
    selected = q011t_cycle["c1_radius_campaign_audit"]["selected_record"]
    values = graph["transported_exact_constants"]
    radius = _fraction(selected["radius"])
    mu_2 = _fraction(values["mu_2"])
    m_value = _fraction(values["m"])
    q_value = _fraction(values["q"])
    coupling = _fraction(values["b"])
    alpha = _fraction(values["alpha"])
    p_selected = _fraction(values["p_S"])
    lift = _fraction(values["K_L"])
    amplitude = _fraction(selected["localized_nonlinear_amplitude"])
    delta = _fraction(selected["localized_nonlinear_derivative"])
    base_conorm = _fraction(selected["base_conorm"])
    slope = _fraction(selected["c1_graph_slope"])
    selected_ratio = _fraction(selected["original_selected_image_ratio"])

    assert selected["passed"]
    assert all(selected["checks"].values())
    assert amplitude == 8 * mu_2 * radius**2
    assert delta == 516 * mu_2 * radius
    assert base_conorm == m_value - coupling - delta
    assert _fraction(selected["base_inverse_utilization"]) == (alpha * (coupling + delta))
    assert _fraction(selected["height_ratio"]) == q_value + 8 * mu_2 * radius
    assert slope == (q_value + delta) / base_conorm
    assert _fraction(selected["c0_graph_contraction"]) == (
        m_value * (q_value + delta) / base_conorm
    )
    assert _fraction(selected["derivative_fiber_contraction"]) == (
        (q_value + delta) / base_conorm + (q_value + delta) * (coupling + delta) / base_conorm**2
    )
    assert selected_ratio == (p_selected + coupling * slope + Fraction(1, 2) * mu_2 * radius)
    assert _fraction(selected["original_external_image_ratio"]) == (slope * selected_ratio)
    assert _fraction(selected["input_physical_displacement"]) == (lift * radius)
    assert _fraction(selected["output_physical_displacement"]) == (lift * selected_ratio * radius)


def test_q011t_selected_scale_has_all_registered_strict_margins(
    q011t_cycle: dict[str, Any],
) -> None:
    selected = q011t_cycle["c1_radius_campaign_audit"]["selected_record"]

    assert _fraction(selected["localized_nonlinear_derivative"]) <= Fraction(1, 1000)
    assert _fraction(selected["base_inverse_utilization"]) <= Fraction(1, 100)
    assert _fraction(selected["height_ratio"]) <= Fraction(99, 100)
    assert _fraction(selected["c1_graph_slope"]) <= Fraction(999, 1000)
    assert _fraction(selected["c0_graph_contraction"]) <= Fraction(99, 100)
    assert _fraction(selected["derivative_fiber_contraction"]) <= Fraction(1999, 2000)
    assert _fraction(selected["smooth_cutoff_support_physical_displacement"]) <= Fraction(1, 10**11)
    assert _fraction(selected["original_selected_image_ratio"]) <= Fraction(999, 1000)
    assert _fraction(selected["original_external_image_ratio"]) <= Fraction(999, 1000)
    assert _fraction(selected["output_population_floor"]) >= Fraction(1, 50)
    assert _fraction(selected["output_density_floor"]) >= Fraction(99, 100)


def test_q011t_reconstructs_all_spectral_intervals_and_quotient_witnesses(
    q011t_cycle: dict[str, Any],
) -> None:
    audit = q011t_cycle["rigorous_spectral_quotient_audit"]
    records = audit["eigencenter_modulus_records"]
    blocks = audit["block_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(blocks) == 17
    assert len(records) == 2598
    assert audit["modulus_interval_record_count"] == 2598
    assert sum(record["selected"] for record in records) == 24
    assert sum(not record["selected"] for record in records) == 2574
    assert [block["dimension"] for block in blocks] == [150] + [153] * 16
    assert sum(block["selected_count"] for block in blocks) == 24
    assert sum(block["external_count"] for block in blocks) == 2574
    assert audit["exact_modulus_interval_record_digest_sha256"] == (
        "120d9214caa90d3eff168fca272ce8da3ee47eb5e11cbd65b0d462139b2d73fb"
    )


def test_q011t_spectral_quotient_bracket_preserves_missing_degree_boundary(
    q011t_cycle: dict[str, Any],
) -> None:
    audit = q011t_cycle["rigorous_spectral_quotient_audit"]
    quotient = audit["spectral_quotient_record"]
    evidence = audit["degree_evidence_inventory"]

    assert quotient["excluded_lower_quotient"] == 89
    assert quotient["sufficient_upper_quotient"] == 90
    assert quotient["quotient_bracket_width"] == 1
    assert _fraction(quotient["upper_boundary_power_ratio"]) < 1
    assert _fraction(quotient["upper_previous_power_ratio"]) >= 1
    assert _fraction(quotient["lower_boundary_power_ratio"]) >= 1
    assert _fraction(quotient["lower_next_power_ratio"]) < 1
    assert evidence["q011k_certified_external_nonresonance_degrees"] == [2]
    assert evidence["missing_external_nonresonance_degrees_through_upper_quotient"] == list(
        range(3, 91)
    )
    assert evidence["missing_degree_count"] == 88
    assert not evidence["spectral_quotient_ssm_uniqueness_is_certified"]
    assert not evidence["higher_smoothness_is_certified"]
    assert audit["exact_spectral_quotient_record_digest_sha256"] == (
        "cc2b8e2bed6f40fa191a843b7eea95784b860053415617e161c768bfc2bc77d8"
    )


def test_q011t_accepts_only_the_c1_tangent_forward_invariant_claim(
    q011t_cycle: dict[str, Any],
) -> None:
    theorem = q011t_cycle["theorem_consequence"]
    proof = q011t_cycle["c1_radius_campaign_audit"]["selected_c1_original_transfer_proof"]

    assert q011t_cycle["study_validity"] == "passed"
    assert q011t_cycle["hypothesis_outcome"] == "accepted"
    assert q011t_cycle["scientific_classification"] == (
        "the original repaired exact map has a certified C1 "
        "forward-invariant graph patch tangent to the selected real "
        "spectral subspace"
    )
    assert len(q011t_cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in q011t_cycle["validity_gates"].values())
    assert len(q011t_cycle["hypothesis_gates"]) == 6
    assert all(gate["passed"] for gate in q011t_cycle["hypothesis_gates"].values())
    assert q011t_cycle["failed_hypothesis_order"] == []
    assert proof["origin_derivative_is_zero_by_unique_fiber_fixed_point"]
    assert proof["graph_tangent_is_selected_real_spectral_subspace"]
    assert proof["original_map_is_forward_invariant_by_induction"]
    assert not proof["q011s_graph_equality_is_used"]
    assert theorem["the_original_map_has_a_forward_invariant_c1_graph_patch"]
    assert theorem["the_localized_c1_graph_has_zero_derivative_at_the_origin"]
    assert theorem["the_graph_tangent_is_the_selected_real_spectral_subspace"]
    assert theorem["a_rigorous_spectral_quotient_bracket_is_certified"]
    assert not theorem["the_q011s_lipschitz_graph_is_the_same_graph"]
    assert not theorem["backward_invariance_or_onto_is_certified"]
    assert not theorem["c2_or_higher_smoothness_is_certified"]
    assert not theorem["all_nonresonances_through_the_spectral_quotient_are_certified"]
    assert not theorem["spectral_quotient_ssm_uniqueness_is_certified"]
    assert not theorem["normal_attraction_or_a_basin_is_certified"]
    assert "does not identify this graph" in q011t_cycle["claim_boundary"]


def test_q011t_cycle_has_reproducible_strict_json_digests(
    q011t_cycle: dict[str, Any],
) -> None:
    json.dumps(q011t_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("79864489c522a7d50e7534091c283167de3b11d9af58365164b7084095a972eb"),
        "cutoff_digest_sha256": (
            "5c194baab4c8be74cba91c398037839c6b313f80123416819cc6aedf7bf027d2"
        ),
        "graph_digest_sha256": ("6d7e09295d3b60d07d4abe9d658fea506752e20300e87e8d1c4158f5f0772bec"),
        "radius_digest_sha256": (
            "ba1cf6a77e95a52cba33d360632bfae0967a4d8b947daf04761dbfbd7926fcb9"
        ),
        "spectral_digest_sha256": (
            "d899cf7872d69b5adf75cddc9c0dafe42930ff53130099a8bdb5b7cb1b04559c"
        ),
        "result_digest_sha256": (
            "ac1019fd526cd4f21caddfb27d4cd8e0c4f7b312a742b84dbc3b3605ee827231"
        ),
    }
    assert {name: q011t_cycle[name] for name in expected} == expected
    assert q011t_cycle["result_digest_sha256"] == (
        q011t.q011b._canonical_json_sha256(q011t._result_digest_sections(q011t_cycle))
    )


def test_q011t_artifact_records_the_c1_tangent_graph_certificate() -> None:
    runner_path = Path(q011t.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011t_c1_tangent_graph.json"
    if not artifact_path.exists():
        pytest.skip("Q011t artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "7848a915f384a4b51c93fa8201bf357b01cedcec52590defacd15ba22bf99fe2"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011t_c1_tangent_graph.py",
        "sha256": ("b6eff63f29a4274502923a31b98fd774b89d1f21512c5e181c124f493efc8f10"),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == (
        q011t.q011b._canonical_json_sha256(q011t._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
