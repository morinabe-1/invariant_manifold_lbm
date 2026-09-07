"""Full saved-evidence audit; only the explicitly named fresh case is replayed."""

from __future__ import annotations

import copy
import json
from hashlib import sha256
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import q012a_d3q27_foundation as q012a
from research import q012d_d3q27_quadratic_chart as runner
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

ARTIFACT = q012a.ARTIFACT_DIRECTORY / "q012d_d3q27_quadratic_chart.json"


@pytest.fixture(scope="module")
def artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_manifest_sources_digest_and_evidence_validity(artifact: dict) -> None:
    assert (
        _file_sha256(ARTIFACT) == "d33ca861d7b51096e09de93550e24d33f0722fc12ac531ff591f56383dd4fea8"
    )
    cycle = copy.deepcopy(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(runner.__file__))
    for name, module in runner.HELPERS:
        assert artifact["helper_sources"][name]["sha256"] == _file_sha256(Path(module.__file__))
    assert runner.input_audit()["passed"]
    assert _all_numeric_values_finite(artifact)
    assert artifact["study_gate"] == cycle["study_validity"] == "passed", cycle["validity_gates"]
    assert len(cycle["validity_gates"]) == 8 and all(cycle["validity_gates"].values())
    assert cycle["configuration"] == {
        "size": 17,
        "omega": 1.5,
        "eta": 0.02,
        "power": 2,
        "real_coordinate_count": 104,
        "fft_normalization": "ortho",
    }


def test_all_pairs_keep_rank_residual_structure_and_backend_rules(artifact: dict) -> None:
    c = artifact["cycle"]["construction"]
    assert c["coverage_passed"] and c["pair_count"] == 3081 and c["product_dimension_sum"] == 5460
    blocks = [
        (w, label) for w in chart.WAVES for label in ("shear", "acoustic_plus", "acoustic_minus")
    ]
    expected = list(combinations_with_replacement(blocks, 2))
    assert len(c["pair_records"]) == len(expected)
    for row, (left, right) in zip(c["pair_records"], expected):
        assert (tuple(row["left_wave"]), row["left_label"]) == left
        assert (tuple(row["right_wave"]), row["right_label"]) == right
        wave = tuple(a + b for a, b in zip(left[0], right[0]))
        assert tuple(row["output_wave"]) == wave
        dl, dr = (2 if left[1] == "shear" else 1), (2 if right[1] == "shear" else 1)
        assert row["product_dimension"] == (dl * (dl + 1) // 2 if left == right else dl * dr)
        assert row["operator_dimension"] == row["product_dimension"] * (
            23 if wave in chart.WAVES or wave == (0, 0, 0) else 27
        )
        assert row["status"] == "nonsingular_practical"
        assert row["numerical_rank"] == row["operator_dimension"] and row["condition_number"] <= 1e8
        assert row["passed"] == (
            row["solve_relative_residual"] <= 1e-10
            and row["structural_error"] <= 5e-12
            and row["full_homological_relative_residual"] <= 1e-9
            and row["backend"]["passed"]
        )
        if row["backend"]["fallback"]:
            assert (
                row["backend"]["driver"] == "gesvd"
                and row["backend"]["original_error"] == "SVD did not converge"
            )
            assert row["backend"]["reconstruction_relative_error"] <= 1e-12
        else:
            assert row["backend"] == {"driver": "gesdd", "fallback": False, "passed": True}
    assert c["coefficient_passed"] == all(row["passed"] for row in c["pair_records"])
    assert c["gates"] == runner.construction_gates(c)


def test_npz_binary_seal_every_array_and_complete_sparse_support(artifact: dict) -> None:
    archive = artifact["cycle"]["coefficient_archive"]
    path = ARTIFACT.parent / archive["filename"]
    assert path.parent == ARTIFACT.parent
    assert sha256(path.read_bytes()).hexdigest() == archive["sha256"]
    assert path.stat().st_size == archive["serialized_bytes"]
    assert archive["all_arrays_finite"] and archive["roundtrip_passed"]
    with np.load(path, allow_pickle=False) as arrays:
        assert (
            set(arrays.files)
            == set(archive["arrays"])
            == {
                "waves",
                "input_pairs",
                "output_waves",
                "transform",
                "complex_linear",
                "real_linear",
                "hessian_taylor_fibers",
                "forcing_taylor_fibers",
                "reduced_taylor_fibers",
                "reduced_real_hessian",
                "frame_bases",
                "frame_duals",
            }
        )
        for name, metadata in archive["arrays"].items():
            assert chart.array_metadata(arrays[name]) == metadata
            assert np.all(np.isfinite(arrays[name]))
        assert (
            arrays["hessian_taylor_fibers"].shape
            == arrays["forcing_taylor_fibers"].shape
            == (5460, 27)
        )
        assert arrays["reduced_taylor_fibers"].shape == (5460, 4)
        assert arrays["reduced_real_hessian"].shape == (104, 104, 104)
        assert set(map(tuple, arrays["input_pairs"])) == set(
            combinations_with_replacement(range(104), 2)
        )
        expected = arrays["waves"][arrays["input_pairs"] // 4].sum(axis=1)
        np.testing.assert_array_equal(expected, arrays["output_waves"])
    replay = artifact["cycle"]["independent_rebuild"]
    assert replay["passed"] and replay["coverage_passed"] and replay["coefficient_passed"]
    assert set(replay["array_checks"]) == set(archive["arrays"]) and all(
        replay["array_checks"].values()
    )


def test_registered_independent_controls_are_classified_from_errors(artifact: dict) -> None:
    controls = artifact["cycle"]["controls"]
    for name, seed, count in (("evaluation", 2026090713, 8), ("symmetry", 2026090715, 4)):
        section = controls[name]
        assert section["seed"] == seed
        np.testing.assert_array_equal(
            section["directions"], chart.normalized_directions(seed, count)
        )
        assert len(section["records"]) == (8 if name == "evaluation" else 192)
        threshold = 1e-10 if name == "evaluation" else 1e-9
        for record in section["records"]:
            assert record["passed"] == (max(record["errors"].values()) <= threshold)
        assert section["passed"] == all(r["passed"] for r in section["records"])
    assert {
        (r["rotation_index"], r["direction_index"]) for r in controls["symmetry"]["records"]
    } == {(rotation, direction) for rotation in range(48) for direction in range(4)}
    section = controls["hessian"]
    assert section["seed"] == 2026090714 and len(section["records"]) == 8
    np.testing.assert_array_equal(
        section["direction_pairs"], chart.normalized_directions(2026090714, 16).reshape(8, 2, 104)
    )
    for record in section["records"]:
        assert [r["step"] for r in record["finite_differences"]] == list(runner.FD_STEPS)
        assert record["passed"] == (
            record["fourier_vs_physical_relative_error"] <= 1e-10
            and record["physical_homological_relative_error"] <= 1e-9
            and record["finite_differences"][-1]["relative_error"] <= 1e-5
        )
    assert section["passed"] == all(r["passed"] for r in section["records"])


def test_every_saved_residual_fit_roundoff_gate_and_negative_control(artifact: dict) -> None:
    section = artifact["cycle"]["residual_campaign"]
    assert section["seed"] == 2026090711 and section["amplitudes"] == list(runner.AMPLITUDES)
    np.testing.assert_array_equal(
        section["directions"], chart.normalized_directions(2026090711, 64)
    )
    assert len(section["generic_records"]) == 64 and len(section["special_records"]) == 24
    for record in section["generic_records"] + section["special_records"]:
        for name in ("linear", "quadratic"):
            value = record[name]
            assert value == runner.order_record(
                runner.AMPLITUDES, value["defects"], record["roundoff_floor"]
            )
        first, second = record["linear"], record["quadratic"]
        resolved = first["above_roundoff_floor"] and second["above_roundoff_floor"]
        ratio = second["defects"][-1] / max(1e-300, first["defects"][-1])
        assert record["resolved"] == resolved and record["smallest_amplitude_ratio"] == ratio
        assert record["passed"] == (
            resolved
            and 1.9 <= first["slope"] <= 2.1
            and 2.9 <= second["slope"] <= 3.1
            and ratio <= 0.1
        )
    controls = []
    for index, record in enumerate(section["generic_records"]):
        assert record["direction_index"] == index
        assert ("omitted_reduced_quadratic" in record) == (index < 8)
        if index < 8:
            control = dict(record["omitted_reduced_quadratic"])
            passed = control.pop("passed")
            assert control == runner.order_record(
                runner.AMPLITUDES, control["defects"], record["roundoff_floor"]
            )
            assert passed == (control["above_roundoff_floor"] and 1.9 <= control["slope"] <= 2.1)
            controls.append(passed)
    assert section["generic_orders_resolved"] == all(
        r["resolved"] for r in section["generic_records"]
    )
    assert section["generic_orders_passed"] == all(r["passed"] for r in section["generic_records"])
    assert section["nonzero_reduced_negative_control_passed"] == all(controls)
    assert {(tuple(r["wave"]), r["real_component"]) for r in section["special_records"]} == {
        (wave, component) for wave in ((1, 0, 0), (1, 1, 0), (1, 1, 1)) for component in range(8)
    }


def test_all_trajectory_steps_and_conservation_units(artifact: dict) -> None:
    section = artifact["cycle"]["trajectory_campaign"]
    assert section["seed"] == 2026090712 and section["steps"] == 64
    assert "initial states differ" in section["initialization"]
    np.testing.assert_array_equal(
        section["directions"], chart.normalized_directions(2026090712, 16)
    )
    assert len(section["records"]) == 48 and {
        (r["direction_index"], r["amplitude"]) for r in section["records"]
    } == {
        (direction, amplitude)
        for direction in range(16)
        for amplitude in runner.TRAJECTORY_AMPLITUDES
    }
    for record in section["records"]:
        for mode in record["modes"].values():
            errors = mode["state_error_by_step"]
            assert len(errors) == 65 and errors[0] == 0
            assert (
                mode["maximum_state_error"] == max(errors)
                and mode["final_state_error"] == errors[-1]
            )
            low = mode["full_minimum_population_by_step"] + mode["chart_minimum_population_by_step"]
            assert len(low) == 130 and mode["positive"] == (min(low) > 0)
            full, reconstructed = (
                mode["full_global_conservation_drift_by_step"],
                mode["chart_global_conservation_drift_by_step"],
            )
            assert np.shape(full) == np.shape(reconstructed) == (65, 4)
            drift = float(np.max(np.abs((full, reconstructed))))
            assert mode["maximum_global_conservation_drift"] == drift
            assert mode["maximum_site_average_conservation_drift"] == drift / 17**3
            assert mode["conservation_passed"] == (
                drift / 17**3 <= 5e-13 and mode["initial_site_average_leaf_error"] <= 5e-13
            )
            assert mode["finite"] and _all_numeric_values_finite(mode)
        ratios = {
            key: record["modes"]["quadratic"][key] / max(1e-300, record["modes"]["linear"][key])
            for key in ("maximum_state_error", "final_state_error")
        }
        assert record["quadratic_to_linear_ratios"] == ratios
        assert record["accuracy_passed"] == (max(ratios.values()) <= 0.5)
        assert record["positive_finite_conservation_passed"] == all(
            m["finite"] and m["positive"] and m["conservation_passed"]
            for m in record["modes"].values()
        )
    assert section["accuracy_passed"] == all(r["accuracy_passed"] for r in section["records"])
    assert section["positive_finite_conservation_passed"] == all(
        r["positive_finite_conservation_passed"] for r in section["records"]
    )


def test_scientific_outcome_keeps_all_registered_gates(artifact: dict) -> None:
    cycle = artifact["cycle"]
    controls, residuals, trajectories = (
        cycle["controls"],
        cycle["residual_campaign"],
        cycle["trajectory_campaign"],
    )
    expected = {
        "quadratic_structure_and_nontrivial_R2": all(cycle["construction"]["gates"].values()),
        "independent_coefficient_evaluations": controls["evaluation"]["passed"],
        "independent_physical_hessian_and_equation": controls["hessian"]["passed"],
        "all_48_cubic_operations": controls["symmetry"]["passed"],
        "all_64_generic_orders_and_defect_reduction": residuals["generic_orders_passed"],
        "nonzero_reduced_negative_control": residuals["nonzero_reduced_negative_control_passed"],
        "all_48_trajectory_improvements": trajectories["accuracy_passed"],
        "finite_positive_conserved_trajectory_samples": trajectories[
            "positive_finite_conservation_passed"
        ],
    }
    assert cycle["hypothesis_gates"] == expected
    # Preserve this registered finite-window rejection, including its four witnesses.
    assert artifact["scientific_outcome"] == "rejected"
    assert [key for key, passed in expected.items() if not passed] == [
        "nonzero_reduced_negative_control"
    ]
    assert [
        row["direction_index"]
        for row in residuals["generic_records"][:8]
        if not row["omitted_reduced_quadratic"]["passed"]
    ] == [0, 2, 4, 5]
    assert (
        artifact["scientific_outcome"]
        == cycle["scientific_outcome"]
        == runner.classify(cycle["validity_gates"], expected, residuals["generic_orders_resolved"])
    )


def test_fresh_all_coefficient_hashes_and_one_trajectory_case(artifact: dict) -> None:
    model = chart.build_chart()
    expected = artifact["cycle"]["coefficient_archive"]["arrays"]
    assert {
        key: chart.array_metadata(value) for key, value in model.archive_arrays().items()
    } == expected
    section = artifact["cycle"]["trajectory_campaign"]
    row = section["records"][0]
    a0 = row["amplitude"] * np.asarray(section["directions"])[row["direction_index"]]
    result = runner.trajectory_case(model, a0)
    assert result == {
        key: value for key, value in row.items() if key not in ("direction_index", "amplitude")
    }
