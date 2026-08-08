from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007q_population_positivity as q007q
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007q_artifact() -> dict:
    artifact_path = (
        Path(q007q.__file__).resolve().parent
        / "artifacts"
        / "q007q_population_positivity.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007q_accepts_population_positivity_on_the_registered_tube(
    q007q_artifact,
) -> None:
    cycle = q007q_artifact["cycle"]

    assert cycle == q007q.run_population_positivity_audit()
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "registered Q007p tube lies in the strictly positive population "
        "cone at every full-map iterate"
    )
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert all(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    )
    assert all(cycle["theorem_consequence"].values())


def test_q007q_audits_the_exact_d2q9_weight_table(q007q_artifact) -> None:
    audit = q007q_artifact["cycle"]["d2q9_weight_audit"]
    observed = {
        _fraction(record["weight"]): record["multiplicity"]
        for record in audit["observed_weight_multiplicities"]
    }

    assert audit["population_count"] == 9
    assert audit["rest_axis_diagonal_multiplicity"] == [1, 4, 4]
    assert observed == {
        Fraction(4, 9): 1,
        Fraction(1, 9): 4,
        Fraction(1, 36): 4,
    }
    assert _fraction(audit["weight_sum"]) == 1
    assert _fraction(audit["minimum_weight"]) == Fraction(1, 36)
    assert _fraction(audit["maximum_weight"]) == Fraction(4, 9)
    assert audit["velocity_class_assignment_exact"]
    assert audit["multiplicities_match"]
    assert audit["all_weights_strictly_positive"]
    assert audit["passed"]


def test_q007q_reconstructs_the_strict_bounds_as_exact_fractions(
    q007q_artifact,
) -> None:
    cycle = q007q_artifact["cycle"]
    bounds = cycle["positivity_bounds"]
    tube = cycle["q007p_tube_reuse"]
    state_radius = _fraction(tube["tube_state_wiener_l1_upper"])
    chart_radius = _fraction(tube["chart_radius_at_base_upper"])
    synthesis = _fraction(tube["synthesis_to_wiener_l1_upper"])
    normal_radius = _fraction(tube["normal_coordinate_radius"])

    assert state_radius == chart_radius + synthesis * normal_radius
    assert _fraction(bounds["tube_population_deviation_linf_upper"]) == (
        state_radius
    )
    assert _fraction(bounds["registered_population_lower"]) == (
        Fraction(1, 36) - state_radius
    )
    assert _fraction(bounds["registered_population_upper"]) == (
        Fraction(4, 9) + state_radius
    )
    assert _fraction(bounds["registered_density_lower"]) == 1 - state_radius
    assert _fraction(bounds["registered_population_lower"]) > 0
    assert _fraction(bounds["registered_density_lower"]) > 0


def test_q007q_reuses_the_sealed_q007p_forward_invariant_tube(
    q007q_artifact,
) -> None:
    cycle = q007q_artifact["cycle"]
    input_record = cycle["input_artifact"]
    tube = cycle["q007p_tube_reuse"]
    triangle = cycle["wiener_triangle_audit"]

    assert input_record["sha256"] == q007q.REGISTERED_Q007P_ARTIFACT_SHA256
    assert input_record["observed_runner_sha256"] == (
        q007q.REGISTERED_Q007P_RUNNER_SHA256
    )
    assert input_record["passed"]
    assert _fraction(tube["base_modal_l1_radius"]) == Fraction(1, 10**19)
    assert _fraction(tube["normal_coordinate_radius"]) == Fraction(1, 10**20)
    assert tube["state_radius_reproduced_exactly"]
    assert tube["q007p_forward_invariance"]
    assert tube["q007p_normal_contraction"]
    assert tube["q007p_strict_normal_domination"]
    assert tube["q007p_exact_manifold_identification"]
    assert tube["passed"]
    assert triangle["fourier_wave_count"] == 17**2
    assert triangle["norm_definition_match"]
    assert triangle["passed"]


def test_q007q_records_provenance_and_the_full_map_only_boundary(
    q007q_artifact,
) -> None:
    cycle = q007q_artifact["cycle"]
    runner_path = Path(q007q.__file__).resolve()

    assert q007q_artifact["schema_version"] == 1
    assert q007q_artifact["source"] == source_metadata()
    assert q007q_artifact["runner_source"] == {
        "filename": "q007q_population_positivity.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert q007q_artifact["mathematical_scope"]["sampling_times"] == (
        "full one-step map input/output only"
    )
    assert "does not certify positivity after collision" in cycle[
        "claim_boundary"
    ]
    assert "larger tube" in cycle["claim_boundary"]
    assert not cycle["preserved_prior_outcomes"][
        "q007c1_finite_amplitude_rejection_changed"
    ]
    assert not cycle["preserved_prior_outcomes"][
        "q007d_euclidean_rejection_changed"
    ]
    json.dumps(q007q_artifact, allow_nan=False)
