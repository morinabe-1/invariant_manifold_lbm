from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011r_nonlinear_graph_transform as q011r
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011r_cycle() -> dict[str, Any]:
    return q011r.run_nonlinear_graph_transform_audit()


def test_q011r_seals_both_direct_inputs_and_ten_digests(
    q011r_cycle: dict[str, Any],
) -> None:
    audit = q011r_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 10
    assert {
        label: audit[label]["hypothesis_outcome"]
        for label in ("q011m", "q011q")
    } == {"q011m": "accepted", "q011q": "accepted"}
    assert audit["checks"][
        "q011m_derivative_and_claim_boundary_are_preserved"
    ]
    assert audit["checks"]["q011m_nonlinear_outputs_are_on_the_fixed_leaf"]
    assert audit["checks"][
        "q011q_real_setup_and_claim_boundary_are_preserved"
    ]
    assert audit["checks"][
        "nested_q011m_seal_reproduces_but_is_not_substituted"
    ]


def test_q011r_transports_both_derivatives_into_the_same_real_norm(
    q011r_cycle: dict[str, Any],
) -> None:
    audit = q011r_cycle["real_derivative_transport_audit"]
    second = _fraction(audit["physical_second_derivative_upper"])
    third = _fraction(audit["physical_third_derivative_upper"])
    lift = _fraction(audit["real_physical_lift_norm_upper"])
    analysis = _fraction(audit["real_coordinate_analysis_norm_upper"])

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert _fraction(audit["real_second_derivative_bilinear_upper"]) == (
        analysis * second * lift**2
    )
    assert _fraction(audit["real_third_derivative_trilinear_upper"]) == (
        analysis * third * lift**3
    )
    assert _fraction(audit["real_second_derivative_bilinear_upper"]) <= 10**12
    assert _fraction(audit["real_third_derivative_trilinear_upper"]) <= 10**17
    assert audit["fixed_leaf_second_and_third_conserved_moments_are_zero"]
    assert audit["third_derivative_is_provenance_not_a_sharpening_term"]


def test_q011r_uses_a_complete_global_bounded_real_graph_space(
    q011r_cycle: dict[str, Any],
) -> None:
    audit = q011r_cycle["global_graph_transform_definition_audit"]
    graph_space = audit["real_graph_space"]
    base = audit["base_inverse"]
    transform = audit["graph_transform"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert graph_space["domain"] == "the full selected real space S_R"
    assert graph_space["codomain"] == "the full external real space E_R"
    assert graph_space["metric_is_finite_from_uniform_height_cap"]
    assert graph_space["closed_complete_space"]
    assert graph_space["restriction_to_selected_rho_ball_is_in_q011q_local_space"]
    assert not graph_space["unproved_one_lipschitz_extension_is_used"]
    assert base["global_bijection_follows_from_fixed_point_inverse"]
    assert base["finite_dimensional_surjectivity_is_not_assumed"]
    assert transform["origin_is_fixed"]
    assert transform["real_selected_and_external_spaces_are_preserved"]
    assert transform["domain"] == "G_global_(rho,1)"


def test_q011r_radius_campaign_selects_the_largest_registered_pass(
    q011r_cycle: dict[str, Any],
) -> None:
    audit = q011r_cycle["graph_transform_radius_campaign_audit"]
    records = audit["radius_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["monotonicity_checks"].values())
    assert len(records) == 15
    assert audit["passing_radius_count"] == 6
    assert [record["passed"] for record in records] == [True] * 6 + [False] * 9
    assert _fraction(audit["selected_radius"]) == Fraction(3, 10**16)
    assert _fraction(audit["first_failed_larger_radius"]) == Fraction(
        1, 10**15
    )
    assert audit["first_failed_larger_constraints"] == [
        "localized_nonlinear_lipschitz_fits_cap",
        "graph_slope_fits_cap",
    ]
    assert audit["exact_radius_record_digest_sha256"] == (
        "dcdb73e941880debf5a1059a06f8f0c1d51fecde9afb4ea1e32c2405f5fbe6f1"
    )


def test_q011r_selected_radius_reproduces_every_graph_transform_formula(
    q011r_cycle: dict[str, Any],
) -> None:
    transport = q011r_cycle["real_derivative_transport_audit"]
    selected = q011r_cycle["graph_transform_radius_campaign_audit"][
        "selected_record"
    ]
    rho = _fraction(selected["radius"])
    mu_2 = _fraction(transport["real_second_derivative_bilinear_upper"])
    lift = _fraction(transport["real_physical_lift_norm_upper"])
    m_value = _fraction(transport["real_selected_conorm_lower"])
    q_value = _fraction(transport["real_external_operator_norm_upper"])
    coupling = _fraction(
        transport["real_selected_external_coupling_upper"]
    )
    alpha = _fraction(transport["real_selected_inverse_norm_upper"])
    amplitude = _fraction(selected["nonlinear_amplitude"])
    delta = _fraction(selected["nonlinear_lipschitz"])
    base_conorm = _fraction(selected["base_conorm"])
    preimage = _fraction(selected["preimage_sensitivity"])

    assert selected["passed"]
    assert all(selected["checks"].values())
    assert _fraction(selected["physical_state_radius"]) == lift * rho
    assert amplitude == Fraction(1, 2) * mu_2 * rho**2
    assert delta == 2 * mu_2 * rho
    assert base_conorm == m_value - coupling - delta
    assert _fraction(selected["base_inverse_utilization"]) == (
        alpha * (coupling + delta)
    )
    assert _fraction(selected["base_inverse_lipschitz"]) == 1 / base_conorm
    assert _fraction(selected["height_ratio"]) == q_value + amplitude / rho
    assert preimage == (coupling + delta) / base_conorm
    assert _fraction(selected["graph_slope"]) == (
        (q_value + delta) / base_conorm
    )
    assert _fraction(selected["graph_transform_contraction"]) == (
        m_value * (q_value + delta) / base_conorm
    )
    assert _fraction(selected["graph_transform_contraction"]) == (
        (q_value + delta) * (1 + preimage)
    )


def test_q011r_selected_radius_has_registered_strict_margins(
    q011r_cycle: dict[str, Any],
) -> None:
    selected = q011r_cycle["graph_transform_radius_campaign_audit"][
        "selected_record"
    ]

    assert _fraction(selected["nonlinear_lipschitz"]) <= Fraction(1, 1000)
    assert _fraction(selected["base_inverse_utilization"]) <= Fraction(1, 100)
    assert _fraction(selected["height_ratio"]) <= Fraction(99, 100)
    assert _fraction(selected["graph_slope"]) <= Fraction(999, 1000)
    assert _fraction(selected["graph_transform_contraction"]) <= Fraction(
        99, 100
    )
    assert _fraction(selected["population_floor"]) >= Fraction(1, 50)
    assert _fraction(selected["density_floor"]) >= Fraction(99, 100)


def test_q011r_accepts_all_gates_and_certifies_only_the_localized_graph(
    q011r_cycle: dict[str, Any],
) -> None:
    theorem = q011r_cycle["theorem_consequence"]

    assert q011r_cycle["study_validity"] == "passed"
    assert q011r_cycle["hypothesis_outcome"] == "accepted"
    assert q011r_cycle["scientific_classification"] == (
        "the registered real localized graph transform is a strict "
        "contraction at a certified finite radius"
    )
    assert len(q011r_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011r_cycle["validity_gates"].values())
    assert len(q011r_cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"] for gate in q011r_cycle["hypothesis_gates"].values()
    )
    assert q011r_cycle["failed_hypothesis_order"] == []
    assert theorem[
        "q011m_derivative_bounds_are_transported_to_the_q011q_real_norm"
    ]
    assert theorem["the_nonlinear_graph_transform_is_a_self_map"]
    assert theorem["the_nonlinear_graph_transform_is_a_strict_contraction"]
    assert theorem["a_unique_lipschitz_fixed_graph_for_the_localized_map_exists"]
    assert not theorem[
        "an_original_map_local_invariant_manifold_or_ssm_is_certified"
    ]
    assert not theorem["c1_or_higher_smoothness_is_certified"]
    assert not theorem["normal_attraction_or_a_basin_is_certified"]
    assert "only for the localized map" in q011r_cycle["claim_boundary"]


def test_q011r_cycle_has_reproducible_strict_json_digests(
    q011r_cycle: dict[str, Any],
) -> None:
    json.dumps(q011r_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "7e9fa7b147ede559cffd117b7a6b8592d2939774f9821494759bbf3d634badd2"
        ),
        "transport_digest_sha256": (
            "3b8fba9cd370521880be3d4b77a9e2fc715e67ac22dc78e631f96e0d71317191"
        ),
        "graph_digest_sha256": (
            "77f2ac35d83726d0868ab08dd7648aee26bed7b00a40fb1405df1e1f162e023b"
        ),
        "radius_digest_sha256": (
            "8d33d01931c42730b18778c674282e6870224336cca72f66e81b447178d32d79"
        ),
        "result_digest_sha256": (
            "b0520673f844d3f94a735c27800ff40d025a9437b01899e3d400b3c3fe0661ea"
        ),
    }
    assert {name: q011r_cycle[name] for name in expected} == expected
    assert q011r_cycle["result_digest_sha256"] == (
        q011r.q011b._canonical_json_sha256(
            q011r._result_digest_sections(q011r_cycle)
        )
    )


def test_q011r_artifact_records_the_nonlinear_graph_transform_certificate() -> None:
    runner_path = Path(q011r.__file__).resolve()
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011r_nonlinear_graph_transform.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011r artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "2d45e3c64965ee1e8bc47f1a7d75070fbeabbcb2711a62b1711da92878a58e11"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011r_nonlinear_graph_transform.py",
        "sha256": "8169e2fc7d5f7dccdc424bba31f37d4c03e6a669ab2e3f04d6289f03240b6d09",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == (
        q011r.q011b._canonical_json_sha256(
            q011r._result_digest_sections(cycle)
        )
    )
    json.dumps(artifact, allow_nan=False)
