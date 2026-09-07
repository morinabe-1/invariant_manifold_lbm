"""Independent controls for the new real-coordinate D3Q27 chart assembly."""

from __future__ import annotations

from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import q012d_d3q27_quadratic_chart as runner


@pytest.fixture(scope="module")
def model() -> chart.QuadraticChart:
    return chart.build_chart()


def test_previous_evidence_remains_sealed() -> None:
    audit = runner.input_audit()
    assert audit["passed"], audit


def test_realification_covers_all_real_and_conjugate_coordinates() -> None:
    transform, partners = chart.realification()
    assert transform.shape == (104, 104)
    assert len(chart.POSITIVE_WAVES) == 13 and len(chart.WAVES) == 26
    np.testing.assert_allclose(transform.conj().T @ transform, np.eye(104), atol=1e-15)
    np.testing.assert_array_equal(partners[partners], np.arange(104))
    a = chart.normalized_directions(2026090713, 1)[0]
    z = transform @ a
    np.testing.assert_array_equal(z[partners], z.conj())
    for index, wave in enumerate(chart.POSITIVE_WAVES):
        offset = 4 * chart.WAVES.index(wave)
        for component in range(4):
            col = 8 * index + 2 * component
            assert z[offset + component] == (a[col] + 1j * a[col + 1]) / np.sqrt(2)


def test_full_chart_has_no_dropped_pairs_and_retains_solver_gates(
    model: chart.QuadraticChart,
) -> None:
    c = model.construction
    assert c["coverage_passed"] and c["coefficient_passed"]
    assert set(map(tuple, model.input_pairs)) == set(combinations_with_replacement(range(104), 2))
    assert len(c["pair_records"]) == len(model.pair_jets) == 3081
    assert len(model.hessian_fibers) == c["product_dimension_sum"] == 5460
    for pair in c["pair_records"]:
        assert pair["passed"] and pair["status"] == "nonsingular_practical"
        assert pair["condition_number"] <= 1e8 and pair["solve_relative_residual"] <= 1e-10
        assert pair["full_homological_relative_residual"] <= 1e-9
        assert pair["structural_error"] <= 5e-12
        assert pair["numerical_rank"] == pair["operator_dimension"]
    assert all(runner.construction_gates(c).values())


def test_fourier_selection_is_exact(model: chart.QuadraticChart) -> None:
    for (left, right), output in zip(model.input_pairs, model.output_waves):
        expected = np.asarray(chart.WAVES[left // 4]) + chart.WAVES[right // 4]
        np.testing.assert_array_equal(output, expected)
    a = chart.normalized_directions(2026090713, 1)[0]
    spectrum = model.quadratic_fourier(a)
    allowed = {chart.wave_slot(tuple(w), 17) for w in model.output_waves}
    actual = {tuple(w) for w in np.argwhere(np.linalg.norm(spectrum, axis=-1) > 0)}
    assert actual <= allowed


def test_mean_generation_is_kinetic_and_R2_is_nonzero(model: chart.QuadraticChart) -> None:
    zero = np.all(model.output_waves == 0, axis=1)
    h = model.hessian_fibers[zero]
    assert np.linalg.norm(h) > 1e-8
    assert np.linalg.norm(h @ d3.conserved_moment_matrix().T) <= 5e-12
    assert np.linalg.norm(model.reduced_hessian) > 1e-6
    np.testing.assert_allclose(
        model.reduced_hessian, model.reduced_hessian.swapaxes(1, 2), atol=1e-14
    )
    np.testing.assert_array_equal(
        model.reduced_fibers[zero], np.zeros_like(model.reduced_fibers[zero])
    )


def test_pair_loop_dense_real_and_fourier_evaluations(model: chart.QuadraticChart) -> None:
    result = runner.evaluation_controls(model)
    assert result["passed"], result["records"]
    assert len(result["records"]) == 8


def test_independent_physical_hessian_and_finite_difference(model: chart.QuadraticChart) -> None:
    result = runner.hessian_controls(model)
    assert result["passed"], result["records"]
    assert len(result["records"]) == 8
    assert all(
        tuple(r["step"] for r in record["finite_differences"]) == runner.FD_STEPS
        for record in result["records"]
    )


def test_full_cubic_group_on_W_and_R(model: chart.QuadraticChart) -> None:
    result = runner.symmetry_controls(model)
    assert result["passed"], [r for r in result["records"] if not r["passed"]]
    assert len(result["records"]) == 48 * 4
    rotations = d3.cubic_symmetries()
    left, right = rotations[7], rotations[19]
    np.testing.assert_allclose(
        model.rotation_action(left @ right),
        model.rotation_action(left) @ model.rotation_action(right),
        atol=1e-12,
    )


@pytest.mark.parametrize(
    "value", [np.zeros(103), np.zeros(104, dtype=complex), np.full(104, np.nan)]
)
def test_invalid_coordinates_are_rejected(model: chart.QuadraticChart, value: np.ndarray) -> None:
    with pytest.raises(ValueError):
        model.embed(value)


def test_projection_rejects_wrong_grid(model: chart.QuadraticChart) -> None:
    with pytest.raises(ValueError, match="grid"):
        model.project(np.zeros((3, 3, 3, 27)))


def test_buried_residuals_cannot_establish_order() -> None:
    record = runner.order_record(runner.AMPLITUDES, [1e-16] * 4, 1e-13)
    assert not record["above_roundoff_floor"] and record["slope"] is None
    resolved = runner.order_record(runner.AMPLITUDES, [a**3 for a in runner.AMPLITUDES], 1e-13)
    assert resolved["above_roundoff_floor"] and abs(resolved["slope"] - 3) < 1e-12


@pytest.mark.parametrize(
    "validity,hypotheses,resolved,expected",
    [
        ({"a": True}, {"b": True}, True, "accepted"),
        ({"a": True}, {"b": False}, True, "rejected"),
        ({"a": False}, {"b": True}, True, "inconclusive"),
        ({"a": True}, {"b": True}, False, "inconclusive"),
    ],
)
def test_outcome_separates_validity_hypothesis_and_resolution(
    validity: dict, hypotheses: dict, resolved: bool, expected: str
) -> None:
    assert runner.classify(validity, hypotheses, resolved) == expected


def test_npz_roundtrip_records_binary_and_array_hashes_without_overwrite(tmp_path: Path) -> None:
    path = tmp_path / "archive.npz"
    arrays = {"x": np.arange(12).reshape(3, 4).T, "z": np.array([1 + 2j, 3 - 4j])}
    result = runner.write_archive(path, arrays)
    assert result["roundtrip_passed"] and result["all_arrays_finite"]
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        runner.write_archive(path, {"x": np.zeros(5)})
    assert path.read_bytes() == original
    with np.load(path, allow_pickle=False) as archive:
        assert result["arrays"] == {key: chart.array_metadata(archive[key]) for key in arrays}


def test_invalid_inputs_do_not_construct_or_save_coefficients(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(runner, "input_audit", lambda: {"passed": False})

    def forbidden():
        raise AssertionError("no computation on invalid inputs")

    monkeypatch.setattr(chart, "build_chart", forbidden)
    result = runner.run_study(tmp_path / "chart.npz")
    assert result["study_gate"] == "failed" and result["scientific_outcome"] == "inconclusive"
    assert result["cycle"]["coefficient_archive"] is None
    assert not (tmp_path / "chart.npz").exists()
