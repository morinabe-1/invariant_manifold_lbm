"""Audit every saved Q012d1 direction/sign/amplitude; no whole-trajectory claim."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import d3q27_negative_control as diagnostic
from research import q012a_d3q27_foundation as q012a
from research import q012d1_d3q27_negative_control as runner
from research import q012d_d3q27_quadratic_chart as prior
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

ARTIFACT = q012a.ARTIFACT_DIRECTORY / "q012d1_d3q27_negative_control.json"


@pytest.fixture(scope="module")
def artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_manifest_seals_and_complete_separate_process_replay(artifact: dict) -> None:
    assert (
        _file_sha256(ARTIFACT) == "812cda7e30678029b91f2a2a56f1ec2cc8cad73ba170d42c3c805769f15c5190"
    )
    cycle = copy.deepcopy(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    experiment = dict(cycle["experiment"])
    experiment_digest = experiment.pop("result_digest_sha256")
    assert q012a._digest(experiment) == experiment_digest
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(runner.__file__))
    for name, module in runner.HELPERS:
        assert artifact["helper_sources"][name]["sha256"] == _file_sha256(Path(module.__file__))
    replay_path = ARTIFACT.parent / cycle["independent_replay"]["filename"]
    assert _file_sha256(replay_path) == cycle["independent_replay"]["sha256"]
    checked = runner.replay_audit(replay_path, cycle["experiment"], artifact)
    assert checked == cycle["independent_replay"] and checked["passed"]
    assert runner.input_audit()["passed"] and _all_numeric_values_finite(artifact)
    assert len(cycle["validity_gates"]) == 5 and all(cycle["validity_gates"].values())
    assert artifact["study_gate"] == cycle["study_validity"] == "passed"


def test_every_registered_direction_and_sample_is_present(artifact: dict) -> None:
    experiment = artifact["cycle"]["experiment"]
    assert experiment["configuration"] == {
        "size": 17,
        "omega": 1.5,
        "eta": 0.02,
        "power": 2,
        "real_coordinate_count": 104,
        "known_direction_seed": 2026090711,
        "holdout_direction_seed": 2026090716,
    }
    assert experiment["original_amplitudes"] == list(diagnostic.ORIGINAL_AMPLITUDES)
    assert experiment["asymptotic_amplitudes"] == list(diagnostic.ASYMPTOTIC_AMPLITUDES)
    records = experiment["records"]
    expected_directions = {
        "known": chart.normalized_directions(2026090711, 8),
        "holdout": chart.normalized_directions(2026090716, 32),
    }
    assert len(records) == 40 and {(r["group"], r["direction_index"]) for r in records} == {
        (group, index) for group, count in (("known", 8), ("holdout", 32)) for index in range(count)
    }
    for row in records:
        np.testing.assert_array_equal(
            row["direction"], expected_directions[row["group"]][row["direction_index"]]
        )
        assert len(row["samples"]) == 14 and {
            (s["amplitude"], s["sign"]) for s in row["samples"]
        } == {(amplitude, sign) for amplitude in diagnostic.AMPLITUDES for sign in (1, -1)}
        assert len(row["parity"]) == 7
    assert experiment["coefficient_rebuild"] == {
        "all_array_hashes_equal": True,
        "pair_count": 3081,
        "product_dimension_sum": 5460,
        "passed": True,
    }


def test_all_gram_matrices_predict_signed_norms_and_keep_composition_error(artifact: dict) -> None:
    for row in artifact["cycle"]["experiment"]["records"]:
        coefficients = row["coefficient_audit"]
        coefficient_gram = np.asarray(coefficients["coefficient_gram"])
        norms = np.asarray(coefficients["coefficient_norms"])
        np.testing.assert_allclose(np.diag(coefficient_gram), norms**2, rtol=1e-13)
        np.testing.assert_allclose(coefficient_gram, coefficient_gram.T, rtol=1e-14, atol=1e-25)
        assert np.min(np.linalg.eigvalsh(coefficient_gram)) >= -1e-12 * np.max(norms**2)
        assert coefficients["c3_to_c2_norm_ratio"] == norms[1] / norms[0]
        assert coefficients["passed"] == (
            coefficients["independent_quadratic_equation_relative_error"] <= 1e-9
            and coefficients["independent_cubic_derivative_relative_error"] <= 1e-10
            and norms[0] > 1e-6
        )
        for sample in row["samples"]:
            t = sample["sign"] * sample["amplitude"]
            for field, powers in (
                ("quadratic_prediction_norm", (t**2, 0, 0)),
                ("cubic_prediction_norm", (t**2, t**3, 0)),
                ("quartic_prediction_norm", (t**2, t**3, t**4)),
            ):
                np.testing.assert_allclose(
                    np.asarray(powers) @ coefficient_gram @ powers,
                    sample[field] ** 2,
                    rtol=1e-12,
                    atol=1e-35,
                )
            composition = np.asarray(sample["composition_gram"])
            np.testing.assert_allclose(composition, composition.T, rtol=1e-13, atol=1e-35)
            np.testing.assert_allclose(
                np.diag(composition),
                [
                    sample["full_norm"] ** 2,
                    sample["quadratic_prediction_norm"] ** 2,
                    t**6 * coefficients["composition_cubic_norm"] ** 2,
                    t**8 * coefficients["composition_quartic_norm"] ** 2,
                ],
                rtol=1e-12,
                atol=1e-35,
            )
            assert (
                abs(np.sqrt(composition.sum()) - sample["dropped_norm"]) <= sample["roundoff_floor"]
            )
            assert sample["composition_passed"] == (
                sample["composition_absolute_error"] <= sample["roundoff_floor"]
            )
            assert sample["raw_defect_resolved"] == (
                sample["dropped_norm"] > sample["roundoff_floor"]
            )
            assert sample["full_defect_resolved"] == (
                sample["full_norm"] > sample["roundoff_floor"]
            )
            assert sample["finite_positive_passed"] == (
                sample["finite"] and sample["minimum_population"] > 0
            )


def test_original_data_predictions_and_every_asymptotic_fit(artifact: dict) -> None:
    old = runner.prior_artifact()["cycle"]["residual_campaign"]["generic_records"]
    for row in artifact["cycle"]["experiment"]["records"]:
        for label, sign in (("positive", 1), ("negative", -1)):
            for key, window, field in (
                ("original_raw", diagnostic.ORIGINAL_AMPLITUDES, "dropped_norm"),
                (
                    "original_cubic_prediction",
                    diagnostic.ORIGINAL_AMPLITUDES,
                    "cubic_prediction_norm",
                ),
                (
                    "original_quartic_prediction",
                    diagnostic.ORIGINAL_AMPLITUDES,
                    "quartic_prediction_norm",
                ),
                ("asymptotic_raw", diagnostic.ASYMPTOTIC_AMPLITUDES, "dropped_norm"),
            ):
                assert row["fits"][label][key] == diagnostic.fit_window(
                    row["samples"], window, sign, field
                )
        assert row["asymptotic_resolved"] == all(
            r["asymptotic_raw"]["above_roundoff_floor"] for r in row["fits"].values()
        )
        if row["group"] == "known":
            assert row["legacy_reproduction"]["full_prior_record"] == old[row["direction_index"]]
            assert row["legacy_reproduction"]["passed"]
            fits = row["fits"]["positive"]
            raw = fits["original_raw"]
            assert raw == old[row["direction_index"]]["omitted_reduced_quadratic"]
            prediction = row["legacy_slope_prediction"]
            assert prediction["cubic_slope_error"] == abs(
                raw["slope"] - fits["original_cubic_prediction"]["slope"]
            )
            assert prediction["quartic_slope_error"] == abs(
                raw["slope"] - fits["original_quartic_prediction"]["slope"]
            )
            assert (
                prediction["passed"]
                and prediction["cubic_slope_error"] <= 0.01
                and prediction["quartic_slope_error"] <= 0.001
            )
            assert (
                raw["passed"]
                == fits["original_cubic_prediction"]["passed"]
                == fits["original_quartic_prediction"]["passed"]
            )
        else:
            assert row["legacy_reproduction"] is None and row["legacy_slope_prediction"] is None


def test_all_direction_gates_are_recomputed_from_raw_evidence(artifact: dict) -> None:
    for row in artifact["cycle"]["experiment"]["records"]:
        samples, parity = row["samples"], row["parity"]
        original = [s for s in samples if s["amplitude"] in diagnostic.ORIGINAL_AMPLITUDES]
        floor = samples[0]["roundoff_floor"]
        for record in parity:
            registered = record["amplitude"] in diagnostic.ORIGINAL_AMPLITUDES
            assert record["registered_odd_test"] == registered
            assert record["odd_above_roundoff_floor"] == (record["odd_defect_norm"] > floor)
            assert record["registered_odd_passed"] == (
                None
                if not registered
                else record["odd_cubic_relative_error"] <= 0.001
                and record["odd_defect_norm"] > floor
            )
        assert row["gates"] == {
            "independent_nonzero_coefficients": row["coefficient_audit"]["passed"],
            "exact_chart_composition": all(s["composition_passed"] for s in samples),
            "original_window_vector_prediction": all(
                s["cubic_vector_relative_error"] <= 0.02
                and s["quartic_vector_relative_error"] <= 0.001
                for s in original
            ),
            "odd_part_independent_cubic": all(
                p["registered_odd_passed"] for p in parity if p["registered_odd_test"]
            ),
            "asymptotic_quadratic_behavior": all(
                r["asymptotic_raw"]["passed"] for r in row["fits"].values()
            )
            and all(
                s["leading_vector_relative_error"] <= 0.05
                for s in samples
                if s["amplitude"] == diagnostic.ASYMPTOTIC_AMPLITUDES[-1]
            ),
            "finite_positive_samples": all(s["finite_positive_passed"] for s in samples),
        }


def test_finite_window_cubic_rejection_is_preserved_without_hiding_quartic_success(
    artifact: dict,
) -> None:
    cycle = artifact["cycle"]
    experiment = cycle["experiment"]
    gates = experiment["hypothesis_gates"]
    assert len(gates) == 7 and [key for key, passed in gates.items() if not passed] == [
        "cubic_quartic_explanation_of_original_window"
    ]
    assert (
        cycle["hypothesis_gates"] == gates
        and cycle["scientific_outcome"] == artifact["scientific_outcome"] == "rejected"
    )
    assert (
        prior.classify(cycle["validity_gates"], gates, experiment["asymptotic_resolved"])
        == "rejected"
    )
    samples = [
        s
        for r in experiment["records"]
        for s in r["samples"]
        if s["amplitude"] in diagnostic.ORIGINAL_AMPLITUDES
    ]
    failures = [s for s in samples if s["cubic_vector_relative_error"] > 0.02]
    assert len(failures) == 40 and all(s["amplitude"] == 0.008 for s in failures)
    assert all(s["quartic_vector_relative_error"] <= 0.001 for s in samples)
    assert all(
        row["legacy_slope_prediction"]["passed"]
        for row in experiment["records"]
        if row["group"] == "known"
    )
    assert all(
        fit["asymptotic_raw"]["passed"]
        for row in experiment["records"]
        for fit in row["fits"].values()
    )


def test_one_fresh_known_and_holdout_direction_reproduces_all_fields(artifact: dict) -> None:
    model = chart.build_chart()
    old = runner.prior_artifact()["cycle"]["residual_campaign"]["generic_records"]
    for row in (
        artifact["cycle"]["experiment"]["records"][0],
        artifact["cycle"]["experiment"]["records"][10],
    ):
        legacy = old[row["direction_index"]] if row["group"] == "known" else None
        fresh = diagnostic.diagnose_direction(
            model, np.asarray(row["direction"]), row["group"], row["direction_index"], legacy
        )
        assert fresh == row
