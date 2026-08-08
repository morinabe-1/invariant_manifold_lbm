from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

import research.q007v_binary64_stage_enclosure as q007v
from ttim_lbm.checkerboard_filter import conservative_checkerboard_filter
from ttim_lbm.d2q9 import (
    D2Q9_WEIGHTS,
    collide_bgk,
    equilibrium,
    macroscopic,
    stream_periodic,
)
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007v_artifact() -> dict:
    artifact_path = (
        Path(q007v.__file__).resolve().parent
        / "artifacts"
        / "q007v_binary64_stage_enclosure.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007v_accepts_one_step_but_not_robust_reentry(
    q007v_artifact,
) -> None:
    cycle = q007v_artifact["cycle"]

    assert cycle == q007v.run_binary64_stage_enclosure_audit()
    assert cycle["study_validity"] == "passed"
    assert cycle["one_step_outcome"] == "accepted"
    assert cycle["robust_reentry_outcome"] == "not_certified"
    assert cycle["hypothesis_outcome"] == "not_certified"
    assert cycle["scientific_classification"] == (
        "binary64 one-step stages remain positive, but the registered Q007s "
        "tube is not certified roundoff-invariant"
    )
    assert len(cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 6
    assert all(
        gate["passed"]
        for name, gate in cycle["hypothesis_gates"].items()
        if name != "roundoff_robust_q007s_tube_reentry"
    )
    assert not cycle["hypothesis_gates"][
        "roundoff_robust_q007s_tube_reentry"
    ]["passed"]


def test_q007v_reconstructs_the_registered_binary64_model(
    q007v_artifact,
) -> None:
    audit = q007v_artifact["cycle"]["binary64_model_audit"]

    assert audit["dtype"] == "float64"
    assert audit["itemsize_bytes"] == 8
    assert audit["explicit_fraction_bits"] == 52
    assert audit["exponent_bits"] == 11
    assert _fraction(audit["unit_roundoff"]) == Fraction(1, 2**53)
    assert _fraction(audit["subnormal_absolute_fallback"]) == Fraction(
        1, 2**1075
    )
    assert _fraction(audit["machine_epsilon"]) == Fraction(1, 2**52)
    assert _fraction(audit["smallest_normal"]) == Fraction(1, 2**1022)
    assert _fraction(audit["smallest_subnormal"]) == Fraction(1, 2**1074)
    assert len(audit["weight_constants"]) == 9
    assert audit["velocities_exact_binary64_integers"]
    assert audit["weights_are_binary64"]
    assert audit["rounding_model"] == "round-to-nearest ties-to-even"
    scalar = {record["name"]: record for record in audit["scalar_constants"]}
    assert _fraction(scalar["omega"]["absolute_representation_error"]) == 0
    assert _fraction(scalar["eta"]["absolute_representation_error"]) > 0
    assert _fraction(
        scalar["filter_center"]["absolute_representation_error"]
    ) > 0
    assert audit["passed"]


def test_q007v_replays_the_preregistered_operation_schedule(
    q007v_artifact,
) -> None:
    enclosure = q007v_artifact["cycle"]["paired_stage_enclosure"]

    assert enclosure["operation_counts"] == q007v.EXPECTED_OPERATION_COUNTS
    assert enclosure["registered_operation_counts"] == (
        q007v.EXPECTED_OPERATION_COUNTS
    )
    assert enclosure["operation_counts_match"]
    assert _fraction(enclosure["minimum_computed_density_denominator"]) > 0
    assert _fraction(enclosure["maximum_intermediate_magnitude_upper"]) < 2
    assert q007v_artifact["cycle"]["primitive_interval_audit"]["passed"]


def test_q007v_all_one_step_binary64_stage_lowers_are_strict(
    q007v_artifact,
) -> None:
    stages = q007v_artifact["cycle"]["paired_stage_enclosure"]["stages"]
    lowers: dict[str, Fraction] = {}
    for name, stage in stages.items():
        reconstructed = min(
            _fraction(record["target_lower"])
            - _fraction(record["forward_error_upper"])
            for record in stage["population_records"]
        )
        stored = _fraction(stage["binary64_population_lower"])
        assert stored == reconstructed
        assert stored > 0
        lowers[name] = stored

    assert stages["post_streaming"] == stages["post_collision"]
    assert lowers["post_filter"] < lowers["post_collision"]
    assert float(lowers["post_filter"]) == pytest.approx(
        0.027777777714596753
    )


def test_q007v_reentry_bound_exceeds_both_sealed_margins(
    q007v_artifact,
) -> None:
    cycle = q007v_artifact["cycle"]
    stages = cycle["paired_stage_enclosure"]["stages"]
    filtered = stages["post_filter"]["population_records"]
    reuse = cycle["sealed_bound_reuse"]
    audit = cycle["roundoff_reentry_audit"]
    component_sum = sum(
        (_fraction(record["forward_error_upper"]) for record in filtered),
        Fraction(0),
    )
    wiener = 17**2 * component_sum
    selected_analysis = _fraction(
        reuse["selected_analysis_from_wiener_l1_upper"]
    )
    external_analysis = _fraction(
        reuse["external_analysis_from_wiener_l1_upper"]
    )
    base_margin = _fraction(reuse["base_forward_invariance_margin"])
    normal_margin = _fraction(
        reuse["normal_tube_forward_invariance_margin"]
    )

    assert _fraction(audit["component_forward_error_sum_upper"]) == (
        component_sum
    )
    assert _fraction(audit["wiener_error_upper"]) == wiener
    assert _fraction(audit["base_coordinate_error_upper"]) == (
        selected_analysis * wiener
    )
    assert _fraction(audit["normal_coordinate_error_upper"]) == (
        external_analysis * wiener
    )
    assert _fraction(audit["base_coordinate_error_upper"]) > base_margin
    assert _fraction(audit["normal_coordinate_error_upper"]) > normal_margin
    assert _fraction(audit["base_margin_utilization"]) > 10**9
    assert _fraction(audit["normal_margin_utilization"]) > 300
    assert not audit["base_reentry_passed"]
    assert not audit["normal_reentry_passed"]
    assert not audit["passed"]


def test_q007v_seals_sources_and_replays_the_numpy_composition(
    q007v_artifact,
) -> None:
    cycle = q007v_artifact["cycle"]
    source = cycle["implementation_source_audit"]
    replay = cycle["deterministic_implementation_replay"]

    assert source["d2q9_source"]["sha256"] == (
        q007v.REGISTERED_D2Q9_SOURCE_SHA256
    )
    assert source["filter_source"]["sha256"] == (
        q007v.REGISTERED_FILTER_SOURCE_SHA256
    )
    assert all(source["d2q9_source"]["required_snippets"].values())
    assert all(source["filter_source"]["required_snippets"].values())
    assert source["streaming_is_population_permutation_without_arithmetic"]
    assert source["passed"]
    assert replay["all_stage_dtypes_float64"]
    assert replay["all_stage_shapes_match"]
    assert replay["all_stage_values_finite"]
    assert replay["all_stage_values_inside_registered_enclosures"]
    assert replay["wrapped_composition_bitwise_match"]
    assert replay["passed"]


def test_q007v_enclosure_contains_a_deterministic_component_box_holdout(
    q007v_artifact,
) -> None:
    cycle = q007v_artifact["cycle"]
    state_radius = _fraction(
        cycle["sealed_bound_reuse"]["tube_state_wiener_l1_upper"]
    )
    amplitude = np.nextafter(float(state_radius), 0.0)
    rng = np.random.default_rng(20260808)
    bounds = cycle["paired_stage_enclosure"]["stages"]

    for _ in range(8):
        state = np.broadcast_to(D2Q9_WEIGHTS, (17, 17, 9)).copy()
        state += rng.uniform(-amplitude, amplitude, size=state.shape)
        density, momentum = macroscopic(state)
        equilibrium_state = equilibrium(density, momentum)
        collision_state = collide_bgk(state, 1.5)
        streaming_state = stream_periodic(collision_state)
        filter_state = conservative_checkerboard_filter(
            streaming_state,
            0.01,
        )
        arrays = {
            "equilibrium": equilibrium_state,
            "post_collision": collision_state,
            "post_streaming": streaming_state,
            "post_filter": filter_state,
        }
        for name, array in arrays.items():
            lower = _fraction(bounds[name]["binary64_population_lower"])
            upper = _fraction(bounds[name]["binary64_population_upper"])
            assert Fraction.from_float(float(np.min(array))) >= lower
            assert Fraction.from_float(float(np.max(array))) <= upper


def test_q007v_records_upstream_provenance_and_claim_boundary(
    q007v_artifact,
) -> None:
    cycle = q007v_artifact["cycle"]
    runner_path = Path(q007v.__file__).resolve()

    assert q007v_artifact["schema_version"] == 1
    assert q007v_artifact["source"] == source_metadata()
    assert q007v_artifact["runner_source"] == {
        "filename": "q007v_binary64_stage_enclosure.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert cycle["q007u_input_artifact"]["sha256"] == (
        q007v.REGISTERED_Q007U_ARTIFACT_SHA256
    )
    assert cycle["q007s_input_artifact"]["sha256"] == (
        q007v.REGISTERED_Q007S_ARTIFACT_SHA256
    )
    assert cycle["q007u_input_artifact"]["passed"]
    assert cycle["q007s_input_artifact"]["passed"]
    assert cycle["sealed_bound_reuse"]["passed"]
    assert cycle["theorem_consequence"][
        "one_step_binary64_stagewise_population_strictly_positive"
    ]
    assert not cycle["theorem_consequence"][
        "all_iterate_roundoff_robust_q007s_tube_invariance"
    ]
    assert "not a counterexample" in cycle["claim_boundary"]
    assert "not iterated" in cycle["claim_boundary"]
    assert not any(cycle["preserved_prior_outcomes"].values())
    json.dumps(q007v_artifact, allow_nan=False)
