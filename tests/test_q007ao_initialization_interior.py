from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ao_initialization_interior as q007ao
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ao_cycle() -> dict:
    return q007ao.run_initialization_interior_audit()


def test_q007ao_preregistered_inner_set_and_margins_are_exact() -> None:
    assert q007ao.OUTER_BASE_RADIUS == Fraction(9, 10**17)
    assert q007ao.OUTER_NORMAL_RADIUS == Fraction(5, 10**11)
    assert q007ao.INITIAL_BASE_RADIUS == Fraction(89_998, 10**21)
    assert q007ao.INITIAL_NORMAL_RADIUS == Fraction(
        4_999_999_999, 10**20
    )
    assert q007ao.BASE_INWARD_MARGIN == Fraction(2, 10**21)
    assert q007ao.NORMAL_INWARD_MARGIN == Fraction(1, 10**20)
    assert q007ao.INITIAL_BASE_RADIUS == 100 * Fraction(
        89_998, 10**23
    )
    assert q007ao.INITIAL_NORMAL_RADIUS == 10 * Fraction(
        4_999_999_999, 10**21
    )


def test_q007ao_seals_inputs_and_replays_q007an_transitively(
    q007ao_cycle: dict,
) -> None:
    inputs = q007ao_cycle["input_artifacts"]
    reproduction = q007ao_cycle["fresh_q007an_reproduction"]

    assert set(inputs) == {"q007ag", "q007am", "q007an"}
    assert all(record["passed"] for record in inputs.values())
    assert reproduction["stored_cycle_reproduced_exactly"]
    assert reproduction["validity_gate_count"] == 7
    assert reproduction["all_validity_gates_pass"]
    assert reproduction["hypothesis_gate_count"] == 7
    assert reproduction["all_hypothesis_gates_pass"]
    assert reproduction["nested_fresh_reproductions_pass"]
    assert reproduction["nested_cycle_names"] == [
        "q007ag",
        "q007ai",
        "q007am",
    ]
    assert reproduction["q007am_nested_reproductions_pass"]
    assert reproduction["conditional_tube_induction_ready"]
    assert reproduction["conditional_stage_positivity_ready"]
    assert reproduction["initialization_was_not_already_certified"]
    assert reproduction["shadowing_was_not_already_certified"]
    assert reproduction["passed"]


def test_q007ao_aligns_fixed_leaf_tube_coordinates_and_repair(
    q007ao_cycle: dict,
) -> None:
    alignment = q007ao_cycle["scope_alignment"]

    assert _fraction(alignment["outer_base_radius"]) == (
        q007ao.OUTER_BASE_RADIUS
    )
    assert _fraction(alignment["outer_normal_radius"]) == (
        q007ao.OUTER_NORMAL_RADIUS
    )
    assert _fraction(alignment["initial_base_radius"]) == (
        q007ao.INITIAL_BASE_RADIUS
    )
    assert _fraction(alignment["initial_normal_radius"]) == (
        q007ao.INITIAL_NORMAL_RADIUS
    )
    assert _fraction(alignment["analytic_base_radius"]) == Fraction(
        1, 10**16
    )
    assert alignment["old_q007aa_radius_scaling"] == {
        "base_factor": 100,
        "normal_factor": 10,
        "passed": True,
    }
    assert alignment["radius_alignment"]
    assert alignment["registered_inner_set_is_strict_subset"]
    assert alignment["fixed_leaf_target_alignment"]
    assert alignment["repair_lattice_and_distribution_alignment"]
    assert alignment["passed"]


def test_q007ao_reproduces_coarse_input_encoding_and_repair_bound(
    q007ao_cycle: dict,
) -> None:
    constants = q007ao_cycle["exact_input_constants"]
    raw = _fraction(constants["raw_encoding_wiener_upper"])
    repair = _fraction(constants["repair_wiener_upper"])
    total = _fraction(
        constants["total_encoding_repair_wiener_upper"]
    )

    assert total == raw + repair
    assert constants["repair_input_bound_passed"]
    assert constants[
        "repair_is_tube_wide_lattice_defined_positive_and_exact"
    ]
    assert constants["q007an_conditional_induction_ready"]
    assert not constants["coarse_bound_uses_center_cancellation"]
    assert not constants["coarse_bound_uses_spatial_fourier_phase"]
    assert not constants["q007z_selected_wave_bound_used"]
    assert all(constants["arithmetic_identities"].values())
    assert constants["all_arithmetic_identities_pass"]
    assert constants["registered_float_values_match"]
    assert constants["passed"]


def test_q007ao_encoding_repair_increments_fit_both_inner_margins(
    q007ao_cycle: dict,
) -> None:
    constants = q007ao_cycle["exact_input_constants"]
    bound = q007ao_cycle["initialization_bound"]
    total = _fraction(
        bound["total_encoding_repair_wiener_upper"]
    )
    selected_analysis = _fraction(constants["selected_analysis_upper"])
    external_analysis = _fraction(
        constants["external_analysis_upper"]
    )
    chart_derivative = _fraction(constants["chart_derivative_upper"])
    base = _fraction(bound["base_coordinate_increment_upper"])
    direct = _fraction(
        bound["direct_external_coordinate_increment_upper"]
    )
    graph = _fraction(
        bound["graph_shift_external_coordinate_increment_upper"]
    )
    normal = _fraction(bound["normal_coordinate_increment_upper"])

    assert base == selected_analysis * total
    assert direct == external_analysis * total
    assert graph == external_analysis * chart_derivative * base
    assert normal == direct + graph
    assert base < q007ao.BASE_INWARD_MARGIN
    assert normal < q007ao.NORMAL_INWARD_MARGIN
    assert _fraction(bound["base_headroom"]) == (
        q007ao.BASE_INWARD_MARGIN - base
    )
    assert _fraction(bound["normal_headroom"]) == (
        q007ao.NORMAL_INWARD_MARGIN - normal
    )
    assert bound["base_inward_margin_utilization"]["float"] == (
        pytest.approx(0.015048591648551374)
    )
    assert bound["normal_inward_margin_utilization"]["float"] == (
        pytest.approx(0.05960355768038998)
    )
    assert bound["base_inward_margin_passed"]
    assert bound["normal_inward_margin_passed"]
    assert bound["encoded_repaired_membership_passed"]
    assert bound["passed"]


def test_q007ao_accepts_initialization_without_claiming_shadowing(
    q007ao_cycle: dict,
) -> None:
    assert q007ao_cycle["study_validity"] == "passed"
    assert q007ao_cycle["hypothesis_outcome"] == "accepted"
    assert q007ao_cycle["scientific_classification"] == (
        "registered propagated-tube exact-state interior survives "
        "MPFR-85 encoding and repair"
    )
    assert len(q007ao_cycle["validity_gates"]) == 7
    assert all(
        gate["passed"] for gate in q007ao_cycle["validity_gates"].values()
    )
    assert len(q007ao_cycle["hypothesis_gates"]) == 6
    assert all(
        gate["passed"]
        for gate in q007ao_cycle["hypothesis_gates"].values()
    )
    theorem = q007ao_cycle["theorem_consequence"]
    assert theorem["registered_exact_state_inner_set_is_certified"]
    assert theorem["initial_encoding_and_repair_enter_q007ag_tube"]
    assert theorem["initial_repair_restores_exact_fixed_leaf"]
    assert theorem[
        "all_iterate_repaired_mpfr85_q007ag_tube_invariance_from_inner_set"
    ]
    assert theorem[
        "all_iterate_mpfr85_internal_stage_positivity_from_inner_set"
    ]
    assert not theorem[
        "arbitrary_q007ag_boundary_state_initialization_certified"
    ]
    assert not theorem["same_initial_q007ag_forward_shadowing_certified"]
    assert "preregistered strict inner" in q007ao_cycle["claim_boundary"]
    assert "same-initial shadowing" in q007ao_cycle["claim_boundary"]
    assert not any(q007ao_cycle["preserved_prior_outcomes"].values())


def test_q007ao_records_provenance_and_deterministic_digests(
    q007ao_cycle: dict,
) -> None:
    runner_path = Path(q007ao.__file__).resolve()
    bound_sections = {
        key: q007ao_cycle[key]
        for key in (
            "fresh_q007an_reproduction",
            "scope_alignment",
            "exact_input_constants",
            "initialization_bound",
        )
    }
    result_sections = {
        **bound_sections,
        "validity_gates": q007ao_cycle["validity_gates"],
        "hypothesis_gates": q007ao_cycle["hypothesis_gates"],
        "study_validity": q007ao_cycle["study_validity"],
        "hypothesis_outcome": q007ao_cycle["hypothesis_outcome"],
        "scientific_classification": q007ao_cycle[
            "scientific_classification"
        ],
    }

    assert q007ao._runner_source_metadata() == {
        "filename": "q007ao_initialization_interior.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert source_metadata()["package_version"] == "0.1.0"
    assert q007ao_cycle["input_digest_sha256"] == (
        q007ao._canonical_json_sha256(
            {
                "input_artifacts": q007ao_cycle["input_artifacts"],
                "registered_parameters": q007ao_cycle[
                    "registered_parameters"
                ],
            }
        )
    )
    assert q007ao_cycle["bound_digest_sha256"] == (
        q007ao._canonical_json_sha256(bound_sections)
    )
    assert q007ao_cycle["result_digest_sha256"] == (
        q007ao._canonical_json_sha256(result_sections)
    )
    assert all(
        len(q007ao_cycle[key]) == 64
        for key in (
            "input_digest_sha256",
            "bound_digest_sha256",
            "result_digest_sha256",
        )
    )
    json.dumps(q007ao_cycle, allow_nan=False)


def test_q007ao_artifact_reproduces_the_accepted_initialization(
    q007ao_cycle: dict,
) -> None:
    runner_path = Path(q007ao.__file__).resolve()
    artifact_path = (
        runner_path.parent / "artifacts" / "q007ao_initialization_interior.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "c6262043848a479b90634fc8aa82dbd02bfcaea4bcb3467d240b956fd7602b8f"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007ao_initialization_interior.py",
        "sha256": "2cd4c852c2855b93efaeb618bc3b1cb488885375c69f11e2c7624f0ea84614f7",
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["cycle"] == q007ao_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert artifact["cycle"]["input_digest_sha256"] == (
        "4793702239a7bc6252b71b5fff43cc68e78dcad1d1b9446db94544b85270deb3"
    )
    assert artifact["cycle"]["bound_digest_sha256"] == (
        "b747e0a635cf4d747728fd5447e613b62a0b951813634f8a98c9e80a17f3308a"
    )
    assert artifact["cycle"]["result_digest_sha256"] == (
        "6c2a41f2ff2d610d8f542cb132a50a678298098245063d54bcd2a38b6e6a8360"
    )
