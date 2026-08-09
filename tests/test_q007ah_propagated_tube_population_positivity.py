from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007ah_propagated_tube_population_positivity as q007ah
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007ah_cycle() -> dict:
    return q007ah.run_propagated_tube_population_positivity_audit()


def test_q007ah_reproduces_all_sealed_inputs_and_oracles(
    q007ah_cycle: dict,
) -> None:
    inputs = q007ah_cycle["input_artifacts"]
    propagated = q007ah_cycle["q007ag_exact_reproduction"]
    old_oracle = q007ah_cycle["q007t_oracle_reproduction"]

    assert set(inputs) == {"q007ag", "q007t", "q007p"}
    assert all(record["passed"] for record in inputs.values())
    assert inputs["q007ag"]["validity_gate_count"] == 6
    assert inputs["q007ag"]["hypothesis_gate_count"] == 5
    assert inputs["q007t"]["validity_gate_count"] == 5
    assert inputs["q007t"]["hypothesis_gate_count"] == 3
    assert propagated["stored_cycle_reproduced_exactly"]
    assert propagated["observed_digests"] == (
        q007ah.REGISTERED_Q007AG_DIGESTS
    )
    assert propagated["passed"]
    assert old_oracle["stored_cycle_reproduced_exactly"]
    assert old_oracle["old_exact_bounds_reproduced"]
    assert old_oracle["weight_table_passed"]
    assert old_oracle["wiener_triangle_audit_passed"]
    assert old_oracle["passed"]


def test_q007ah_reuses_the_exact_q007ag_tube(
    q007ah_cycle: dict,
) -> None:
    tube = q007ah_cycle["q007ag_tube_reuse"]
    state = _fraction(tube["tube_state_wiener_l1_upper"])
    chart = _fraction(tube["chart_radius_at_base_upper"])
    synthesis = _fraction(tube["synthesis_to_wiener_l1_upper"])
    normal = _fraction(tube["normal_coordinate_radius"])

    assert _fraction(tube["base_modal_l1_radius"]) == Fraction(9, 10**17)
    assert normal == Fraction(5, 10**11)
    assert state == chart + synthesis * normal
    assert float(state) == q007ah.EXPECTED_STATE_RADIUS_FLOAT
    assert tube["state_radius_reproduced_exactly"]
    assert tube["all_selected_candidate_gates_pass"]
    assert tube["q007ag_forward_invariance"]
    assert tube["q007ag_normal_contraction"]
    assert tube["q007ag_strict_normal_domination"]
    assert tube["q007ag_both_radii_enlarged"]
    assert tube["passed"]


def test_q007ah_reconstructs_weights_and_the_wiener_triangle(
    q007ah_cycle: dict,
) -> None:
    weights = q007ah_cycle["d2q9_weight_audit"]
    triangle = q007ah_cycle["wiener_triangle_audit"]
    observed = {
        _fraction(record["weight"]): record["multiplicity"]
        for record in weights["observed_weight_multiplicities"]
    }

    assert observed == {
        Fraction(4, 9): 1,
        Fraction(1, 9): 4,
        Fraction(1, 36): 4,
    }
    assert _fraction(weights["weight_sum"]) == 1
    assert _fraction(weights["minimum_weight"]) == Fraction(1, 36)
    assert _fraction(weights["maximum_weight"]) == Fraction(4, 9)
    assert weights["velocity_class_assignment_exact"]
    assert weights["multiplicities_match"]
    assert weights["all_weights_strictly_positive"]
    assert weights["passed"]
    assert triangle["fourier_wave_count"] == 17**2
    assert triangle["norm_definition_match"]
    assert triangle["transitive_q007p_input_passed"]
    assert triangle["passed"]


def test_q007ah_reconstructs_strict_population_bounds_exactly(
    q007ah_cycle: dict,
) -> None:
    bounds = q007ah_cycle["positivity_bounds"]
    state = _fraction(bounds["tube_population_deviation_linf_upper"])
    lower = _fraction(bounds["registered_population_lower"])
    upper = _fraction(bounds["registered_population_upper"])
    density = _fraction(bounds["registered_density_lower"])

    assert lower == Fraction(1, 36) - state
    assert upper == Fraction(4, 9) + state
    assert density == 1 - state
    assert lower > 0
    assert density > 0
    assert float(lower) == q007ah.EXPECTED_POPULATION_LOWER_FLOAT
    assert float(upper) == q007ah.EXPECTED_POPULATION_UPPER_FLOAT
    assert float(density) == q007ah.EXPECTED_DENSITY_LOWER_FLOAT
    assert bounds["preregistered_float_values_match"]


def test_q007ah_accepts_full_map_positivity_but_not_stagewise_positivity(
    q007ah_cycle: dict,
) -> None:
    assert q007ah_cycle["study_validity"] == "passed"
    assert q007ah_cycle["hypothesis_outcome"] == "accepted"
    assert q007ah_cycle["scientific_classification"] == (
        "registered Q007ag propagated tube lies in the strictly positive "
        "population cone at every full-map iterate"
    )
    assert len(q007ah_cycle["validity_gates"]) == 6
    assert all(
        gate["passed"]
        for gate in q007ah_cycle["validity_gates"].values()
    )
    assert len(q007ah_cycle["hypothesis_gates"]) == 3
    assert all(
        gate["passed"]
        for gate in q007ah_cycle["hypothesis_gates"].values()
    )
    theorem = q007ah_cycle["theorem_consequence"]
    assert theorem[
        "registered_q007ag_tube_population_strictly_positive"
    ]
    assert theorem["registered_q007ag_tube_density_strictly_positive"]
    assert theorem["all_full_map_iterates_population_strictly_positive"]
    assert not theorem[
        "registered_q007ag_tube_stagewise_positivity_certified"
    ]
    assert "separate Q007ai gate" in q007ah_cycle["claim_boundary"]
    assert not any(q007ah_cycle["preserved_prior_outcomes"].values())


def test_q007ah_records_provenance_and_deterministic_digests(
    q007ah_cycle: dict,
) -> None:
    study = q007ah.run_q007ah_study()
    runner_path = Path(q007ah.__file__).resolve()

    assert study["schema_version"] == 1
    assert study["source"] == source_metadata()
    assert study["runner_source"] == {
        "filename": "q007ah_propagated_tube_population_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert study["cycle"] == q007ah_cycle
    assert study["study_gate"] == "passed"
    assert study["scientific_outcome"] == "accepted"
    assert study["mathematical_scope"]["sampling_times"] == (
        "full one-step map input/output only"
    )
    assert len(q007ah_cycle["input_digest_sha256"]) == 64
    assert len(q007ah_cycle["result_digest_sha256"]) == 64
    json.dumps(study, allow_nan=False)


def test_q007ah_artifact_reproduces_the_accepted_certificate(
    q007ah_cycle: dict,
) -> None:
    runner_path = Path(q007ah.__file__).resolve()
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q007ah_propagated_tube_population_positivity.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert _file_sha256(artifact_path) == (
        "cab5ecc090b794a21a21fded8e5c503eca40be2bbc6502767c29844ba8209fa9"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q007ah_propagated_tube_population_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": (
            "UTF-8 text with universal newlines"
        ),
    }
    assert artifact["cycle"] == q007ah_cycle
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert q007ah_cycle["input_digest_sha256"] == (
        "6d7bd69b5c90ff7dbabd5193a4536809f4b79eef36a41fb288ab7caec44321b4"
    )
    assert q007ah_cycle["result_digest_sha256"] == (
        "caea5280667e909f17922260ef0d78998b6a8b374cd048b4b3e526185f040921"
    )
