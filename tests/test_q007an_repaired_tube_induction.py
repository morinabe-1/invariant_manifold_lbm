from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007an_repaired_tube_induction as q007an
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007an_cycle() -> dict:
    return q007an.run_repaired_tube_induction_audit()


def test_q007an_seals_and_replays_all_upstream_certificates(
    q007an_cycle: dict,
) -> None:
    inputs = q007an_cycle["input_artifacts"]
    reproduction = q007an_cycle["fresh_reproductions"]

    assert set(inputs) == {"q007ag", "q007ai", "q007al", "q007am"}
    assert all(record["passed"] for record in inputs.values())
    assert set(reproduction["cycles"]) == {"q007ag", "q007ai", "q007am"}
    for record in reproduction["cycles"].values():
        assert record["stored_cycle_reproduced_exactly"]
        assert record["all_validity_gates_pass"]
        assert record["all_hypothesis_gates_pass"]
        assert record["passed"]
    nested = reproduction["q007am_nested_reproductions"]
    assert nested["q007al_stored_cycle_reproduced_exactly"]
    assert nested["q007al_digests_match"]
    assert nested["q007al_passed"]
    assert nested["q007y_stored_cycle_reproduced_exactly"]
    assert nested["q007y_passed"]
    assert nested["passed"]
    assert reproduction["passed"]


def test_q007an_aligns_tube_coordinates_backend_target_and_repair(
    q007an_cycle: dict,
) -> None:
    alignment = q007an_cycle["scope_alignment"]

    assert _fraction(alignment["base_radius"]) == Fraction(9, 10**17)
    assert _fraction(alignment["normal_radius"]) == Fraction(5, 10**11)
    assert alignment["q007al_probe_component_radius_count"] == 1
    assert alignment["radius_alignment"]
    assert alignment["common_grid_omega_eta"]
    assert alignment["coordinate_manifold_and_norm_alignment"]
    assert alignment["repair_backend_target_and_distribution_alignment"]
    target = alignment["target_conserved"]
    assert _fraction(target["mass"]) == 289
    assert _fraction(target["momentum_x"]) == 0
    assert _fraction(target["momentum_y"]) == 0
    assert alignment["passed"]


def test_q007an_composes_exact_margins_with_repair_aware_errors(
    q007an_cycle: dict,
) -> None:
    composition = q007an_cycle["self_map_composition"]
    base_radius = _fraction(composition["base_radius"])
    normal_radius = _fraction(composition["normal_radius"])
    exact_base = _fraction(composition["exact_base_image_upper"])
    exact_normal = _fraction(composition["exact_normal_image_upper"])
    base_margin = _fraction(composition["q007ag_base_margin"])
    normal_margin = _fraction(composition["q007ag_normal_margin"])
    base_error = _fraction(composition["repair_aware_base_error_upper"])
    normal_error = _fraction(composition["repair_aware_normal_error_upper"])
    repaired_base = _fraction(composition["repaired_base_image_upper"])
    repaired_normal = _fraction(composition["repaired_normal_image_upper"])

    assert base_radius - exact_base == base_margin
    assert normal_radius - exact_normal == normal_margin
    assert repaired_base == exact_base + base_error
    assert repaired_normal == exact_normal + normal_error
    assert _fraction(composition["base_headroom"]) == base_margin - base_error
    assert _fraction(composition["normal_headroom"]) == (
        normal_margin - normal_error
    )
    assert float(_fraction(composition["base_headroom"])) == pytest.approx(
        4.863002361769267e-20
    )
    assert float(_fraction(composition["normal_headroom"])) == pytest.approx(
        9.144950829176811e-13
    )
    assert float(_fraction(composition["base_margin_utilization"])) == (
        pytest.approx(0.02326102601246388)
    )
    assert float(_fraction(composition["normal_margin_utilization"])) == (
        pytest.approx(2.5079552005207522e-8)
    )
    assert repaired_base < base_radius
    assert repaired_normal < normal_radius
    assert all(composition["arithmetic_identities"].values())
    assert composition["all_arithmetic_identities_pass"]
    assert composition["registered_float_values_match"]
    assert composition["base_strict_reentry"]
    assert composition["normal_strict_reentry"]
    assert not composition["triangle_bound_uses_center_cancellation"]
    assert not composition["triangle_bound_uses_spatial_fourier_phase"]
    assert not composition["q007z_selected_wave_bound_used"]
    assert composition["coarse_q007am_bound_preserved"]
    assert composition["passed"]


def test_q007an_composes_exact_mpfr_and_repaired_stage_positivity(
    q007an_cycle: dict,
) -> None:
    stages = q007an_cycle["stage_composition"]

    assert all(
        _fraction(record) > 0
        for record in stages["exact_stage_population_lowers"].values()
    )
    assert float(_fraction(stages["exact_minimum_stage_lower"])) == (
        pytest.approx(0.027777777320468006)
    )
    assert float(_fraction(stages["mpfr_minimum_stage_lower"])) == (
        pytest.approx(0.027777777145968227)
    )
    assert all(
        _fraction(record) >= Fraction(1, 64)
        for record in stages["repaired_diagonal_population_lowers"].values()
    )
    assert _fraction(stages["repaired_diagonal_minimum_lower"]) >= Fraction(
        1, 64
    )
    assert stages["q007ai_exact_all_iterate_stagewise_positivity"]
    assert stages["q007al_mpfr85_tube_wide_stage_positivity"]
    assert stages["q007am_postfilter_repair_binade_and_positivity"]
    assert stages["passed"]


def test_q007an_proves_input_repair_identity_and_output_closure(
    q007an_cycle: dict,
) -> None:
    repair = q007an_cycle["repair_identity_and_closure"]
    generic = repair["generic_zero_defect_argument"]
    witness = repair["finite_idempotence_witness"]

    assert generic["exact_mpfr_conserved_sum_uses_fraction_conversion"]
    assert generic["zero_defect_requested_units"] == [0, 0, 0]
    assert generic["zero_solution_free_unit"] == 0
    assert generic["zero_solution_diagonal_units"] == [0, 0, 0, 0]
    assert generic["all_balanced_distribution_units_zero"]
    assert generic["passed"]
    assert witness["probe_name"] == "rest"
    assert witness["probe_registration_passed"]
    assert witness["first_repair_passed"]
    assert witness["second_requested_units"] == {
        "mass": 0,
        "momentum_x": 0,
        "momentum_y": 0,
    }
    assert witness["second_solution_diagonal_units"] == [0, 0, 0, 0]
    assert _fraction(witness["second_maximum_component_correction"]) == 0
    assert witness["state_unchanged_exactly"]
    assert witness["second_repair_passed"]
    assert witness["passed"]
    assert repair["input_repair_is_identity_on_exact_fixed_leaf"]
    assert repair["postfilter_repair_restores_exact_fixed_leaf_tube_wide"]
    assert repair["repair_output_remains_mpfr85_representable"]
    assert repair["passed"]


def test_q007an_accepts_conditional_induction_without_initialization_or_shadowing(
    q007an_cycle: dict,
) -> None:
    assert q007an_cycle["study_validity"] == "passed"
    assert q007an_cycle["hypothesis_outcome"] == "accepted"
    assert q007an_cycle["scientific_classification"] == (
        "coarse repair certificate closes the Q007ag repaired MPFR-85 "
        "fixed-leaf tube induction"
    )
    assert len(q007an_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q007an_cycle["validity_gates"].values())
    assert len(q007an_cycle["hypothesis_gates"]) == 7
    assert all(
        gate["passed"] for gate in q007an_cycle["hypothesis_gates"].values()
    )
    theorem = q007an_cycle["theorem_consequence"]
    assert theorem["input_repair_is_identity_on_registered_fixed_leaf"]
    assert theorem["registered_repaired_mpfr85_map_is_q007ag_tube_self_map"]
    assert theorem["sampling_times_preserve_exact_mass_and_momentum"]
    assert theorem[
        "conditional_all_iterate_repaired_mpfr85_q007ag_tube_invariance"
    ]
    assert theorem["conditional_all_iterate_mpfr85_internal_stage_positivity"]
    assert not theorem["arbitrary_exact_state_initialization_interior_certified"]
    assert not theorem["same_initial_q007ag_forward_shadowing_certified"]
    assert "conditional on an already encoded and repaired" in (
        q007an_cycle["claim_boundary"]
    )
    assert "not a tube sampling proof" in q007an_cycle["claim_boundary"]
    assert not any(q007an_cycle["preserved_prior_outcomes"].values())


def test_q007an_records_provenance_and_deterministic_digests(
    q007an_cycle: dict,
) -> None:
    runner_path = Path(q007an.__file__).resolve()
    composition_sections = {
        key: q007an_cycle[key]
        for key in (
            "fresh_reproductions",
            "scope_alignment",
            "self_map_composition",
            "stage_composition",
            "repair_identity_and_closure",
        )
    }
    result_sections = {
        **composition_sections,
        "validity_gates": q007an_cycle["validity_gates"],
        "hypothesis_gates": q007an_cycle["hypothesis_gates"],
        "study_validity": q007an_cycle["study_validity"],
        "hypothesis_outcome": q007an_cycle["hypothesis_outcome"],
        "scientific_classification": q007an_cycle["scientific_classification"],
    }

    assert q007an._runner_source_metadata() == {
        "filename": "q007an_repaired_tube_induction.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert source_metadata()["package_version"] == "0.1.0"
    assert q007an_cycle["input_digest_sha256"] == q007an._canonical_json_sha256(
        {
            "input_artifacts": q007an_cycle["input_artifacts"],
            "registered_parameters": q007an_cycle["registered_parameters"],
        }
    )
    assert q007an_cycle["composition_digest_sha256"] == (
        q007an._canonical_json_sha256(composition_sections)
    )
    assert q007an_cycle["result_digest_sha256"] == q007an._canonical_json_sha256(
        result_sections
    )
    assert all(
        len(q007an_cycle[key]) == 64
        for key in (
            "input_digest_sha256",
            "composition_digest_sha256",
            "result_digest_sha256",
        )
    )
    json.dumps(q007an_cycle, allow_nan=False)
