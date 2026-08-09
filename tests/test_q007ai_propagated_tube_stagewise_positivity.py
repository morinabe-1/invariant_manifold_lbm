from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ai_propagated_tube_stagewise_positivity as q007ai
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ai_cycle() -> dict:
    return q007ai.run_propagated_tube_stagewise_positivity_audit()


def test_q007ai_reproduces_all_sealed_inputs_and_oracles(
    q007ai_cycle: dict,
) -> None:
    inputs = q007ai_cycle["input_artifacts"]
    implementations = q007ai_cycle["implementation_source_audit"]
    full_map = q007ai_cycle["q007ah_exact_reproduction"]
    old_oracle = q007ai_cycle["q007u_oracle_reproduction"]

    assert set(inputs) == {"q007ah", "q007u"}
    assert all(record["passed"] for record in inputs.values())
    assert implementations[
        "all_registered_implementation_sha256_match"
    ]
    assert implementations["matching_source_count"] == 2
    assert full_map["stored_cycle_reproduced_exactly"]
    assert full_map["observed_digests"] == (
        q007ai.REGISTERED_Q007AH_DIGESTS
    )
    assert full_map["passed"]
    assert old_oracle["stored_cycle_reproduced_exactly"]
    assert old_oracle["old_exact_stage_bounds_reproduced"]
    assert old_oracle["linear_operator_audit_passed"]
    assert old_oracle["nonlinear_majorant_audit_passed"]
    assert old_oracle["stage_structure_audit_passed"]
    assert old_oracle["passed"]


def test_q007ai_reconstructs_exact_linear_operators(
    q007ai_cycle: dict,
) -> None:
    audit = q007ai_cycle["linear_operator_audit"]
    projector_columns = [
        _fraction(record)
        for record in audit["equilibrium_projector_column_l1_sums"]
    ]
    collision_columns = [
        _fraction(record) for record in audit["collision_column_l1_sums"]
    ]

    assert projector_columns == [
        Fraction(1),
        *([Fraction(5, 3)] * 4),
        *([Fraction(13, 6)] * 4),
    ]
    assert collision_columns == [
        Fraction(1),
        *([Fraction(2)] * 4),
        *([Fraction(19, 6)] * 4),
    ]
    assert _fraction(audit["equilibrium_projector_l1_norm"]) == Fraction(
        13, 6
    )
    assert _fraction(audit["collision_l1_norm"]) == Fraction(19, 6)
    assert audit["collision_matches_rational_map"]
    assert audit["passed"]


def test_q007ai_reconstructs_new_stage_bounds_as_exact_fractions(
    q007ai_cycle: dict,
) -> None:
    nonlinear = q007ai_cycle["nonlinear_majorant_audit"]
    bounds = q007ai_cycle["stage_bounds"]
    state = _fraction(bounds["input_state_wiener_l1_upper"])
    equilibrium_nonlinear = Fraction(7) * state**2 / (1 - state)
    collision_nonlinear = Fraction(21, 2) * state**2 / (1 - state)
    equilibrium_deviation = Fraction(13, 6) * state + (
        equilibrium_nonlinear
    )
    collision_deviation = Fraction(19, 6) * state + collision_nonlinear

    assert float(state) == q007ai.EXPECTED_STATE_RADIUS_FLOAT
    assert _fraction(nonlinear["density_denominator_lower"]) == 1 - state
    assert _fraction(
        nonlinear["equilibrium_nonlinear_remainder_upper"]
    ) == equilibrium_nonlinear
    assert _fraction(
        nonlinear["collision_nonlinear_remainder_upper"]
    ) == collision_nonlinear
    assert _fraction(
        bounds["equilibrium_deviation_wiener_l1_upper"]
    ) == equilibrium_deviation
    assert _fraction(
        bounds["post_collision_deviation_wiener_l1_upper"]
    ) == collision_deviation
    assert _fraction(bounds["equilibrium_population_lower"]) == (
        Fraction(1, 36) - equilibrium_deviation
    )
    assert _fraction(bounds["post_collision_population_lower"]) == (
        Fraction(1, 36) - collision_deviation
    )
    assert _fraction(bounds["post_streaming_population_lower"]) == _fraction(
        bounds["post_collision_population_lower"]
    )
    assert _fraction(bounds["post_filter_population_lower"]) == _fraction(
        bounds["post_collision_population_lower"]
    )
    assert _fraction(bounds["post_filter_population_lower"]) > 0
    assert bounds["preregistered_float_values_match"]


def test_q007ai_reconstructs_streaming_and_filter_structure(
    q007ai_cycle: dict,
) -> None:
    audit = q007ai_cycle["stage_structure_audit"]
    coefficients = [
        _fraction(record) for record in audit["filter_coefficients"]
    ]

    assert audit["streaming_population_permutation_count"] == 9
    assert audit["periodic_site_count"] == 17**2
    assert all(
        record["unique_periodic_target_count"] == 17**2
        and record["bijective"]
        and record["implementation_basis_replayed"]
        for record in audit["streaming_records"]
    )
    assert coefficients == [
        Fraction(99, 100),
        Fraction(1, 400),
        Fraction(1, 400),
        Fraction(1, 400),
        Fraction(1, 400),
    ]
    assert sum(coefficients) == 1
    assert audit["all_filter_coefficients_nonnegative"]
    assert audit["all_filter_implementation_basis_replays"]
    assert audit["wrapped_stage_composition_replayed"]
    assert audit["passed"]


def test_q007ai_accepts_exact_stagewise_but_not_binary64_positivity(
    q007ai_cycle: dict,
) -> None:
    assert q007ai_cycle["study_validity"] == "passed"
    assert q007ai_cycle["hypothesis_outcome"] == "accepted"
    assert q007ai_cycle["scientific_classification"] == (
        "registered Q007ag propagated tube is population-positive at every "
        "exact BGK, streaming, and filter stage"
    )
    assert len(q007ai_cycle["validity_gates"]) == 6
    assert all(
        gate["passed"]
        for gate in q007ai_cycle["validity_gates"].values()
    )
    assert len(q007ai_cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"]
        for gate in q007ai_cycle["hypothesis_gates"].values()
    )
    theorem = q007ai_cycle["theorem_consequence"]
    assert all(
        value
        for name, value in theorem.items()
        if name != "new_tube_binary64_stage_enclosure_certified"
    )
    assert not theorem["new_tube_binary64_stage_enclosure_certified"]
    assert "separate Q007aj gate" in q007ai_cycle["claim_boundary"]
    assert not any(q007ai_cycle["preserved_prior_outcomes"].values())


def test_q007ai_records_provenance_and_deterministic_digests(
    q007ai_cycle: dict,
) -> None:
    study = q007ai.run_q007ai_study()
    runner_path = Path(q007ai.__file__).resolve()

    assert study["schema_version"] == 1
    assert study["source"] == source_metadata()
    assert study["runner_source"] == {
        "filename": "q007ai_propagated_tube_stagewise_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert study["cycle"] == q007ai_cycle
    assert study["study_gate"] == "passed"
    assert study["scientific_outcome"] == "accepted"
    assert study["mathematical_scope"]["arithmetic_scope"] == (
        "exact mathematical map; no IEEE-754 intermediate roundoff enclosure"
    )
    assert len(q007ai_cycle["input_digest_sha256"]) == 64
    assert len(q007ai_cycle["result_digest_sha256"]) == 64
    json.dumps(study, allow_nan=False)


def test_q007ai_artifact_reproduces_the_accepted_certificate(
    q007ai_cycle: dict,
) -> None:
    runner_path = Path(q007ai.__file__).resolve()
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q007ai_propagated_tube_stagewise_positivity.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "3ce5fa6358eaa6f3a64f93fe773e3fbc1990abfb83886aad1a4ade9c82425804"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007ai_propagated_tube_stagewise_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert artifact["cycle"] == q007ai_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert q007ai_cycle["input_digest_sha256"] == (
        "0dff47e8b0ed6e9b87cb73e6dea20192088495b51283c57b9d58630b7344c6a3"
    )
    assert q007ai_cycle["result_digest_sha256"] == (
        "c101313957c738ccee9fd3d7f1ed36b77c6f3dad4e1130651f5be4d8757ef18a"
    )
