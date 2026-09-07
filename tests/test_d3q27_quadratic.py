from __future__ import annotations

import copy
import json
from itertools import combinations_with_replacement
from pathlib import Path

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_quadratic as q
from research import d3q27_spectra as spectra
from research import q012a_d3q27_foundation as q012a
from research import q012b_d3q27_spectral as q012b
from research import q012c_d3q27_preflight as q012c
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256


@pytest.fixture(scope="module")
def frames() -> dict:
    frames, audit = q.build_frames(17, 1.2)
    assert audit["passed"]
    return frames


@pytest.fixture(scope="module")
def study() -> dict:
    return q012c.run_study()


def test_input_artifact_and_sources_are_sealed() -> None:
    assert q012c.input_audit()["passed"]


def test_registered_independent_algebra_and_derivative_controls() -> None:
    audit = q012c.algebra_controls()
    assert audit["passed"] and len(audit["gates"]) == 8
    errors = [r["relative_error"] for r in audit["mixed_derivative_records"]]
    assert errors[-1] < errors[0] and errors[-1] <= 1e-5
    assert audit["singular_compatible"]["passed"] is False
    assert audit["singular_incompatible"]["passed"] is False


def test_frames_keep_two_dimensional_shear_and_complete_symmetric_inventory(frames: dict) -> None:
    for shell, expected_waves, pairs, coordinates in (
        (1, 6, 171, 24),
        (2, 18, 1485, 72),
        (3, 26, 3081, 104),
    ):
        waves = q.shell_waves(shell)
        blocks = [b for wave in waves for b in frames[wave].blocks]
        assert len(waves) == expected_waves and len(blocks) == 3 * expected_waves
        assert all(frames[w].blocks[0].dimension == 2 for w in waves)
        block_pairs = list(combinations_with_replacement(blocks, 2))
        assert len(block_pairs) == pairs
        product_dimensions = [
            a.dimension * b.dimension if a.key != b.key else a.dimension * (a.dimension + 1) // 2
            for a, b in block_pairs
        ]
        assert sum(product_dimensions) == coordinates * (coordinates + 1) // 2
        for wave in waves:
            frame = frames[wave]
            np.testing.assert_allclose(frame.dual @ frame.basis, np.eye(4), atol=5e-12, rtol=0)
            assert frame.diagnostics["frame_condition"] <= 100


def test_zero_wave_is_kinetic_and_selected_external_is_invariant(frames: dict) -> None:
    zero = q.external_sector((0, 0, 0), 17, 1.2, None)
    assert zero.basis.shape == (27, 23)
    np.testing.assert_allclose(d3.conserved_moment_matrix() @ zero.basis, 0, atol=5e-14)
    np.testing.assert_allclose(zero.dynamics, -0.2 * np.eye(23), atol=5e-14)
    for wave in ((0, 0, 1), (1, 1, 0), (1, 1, 1)):
        external = q.external_sector(wave, 17, 1.2, frames[wave])
        assert external.structural_error < 5e-12 and external.basis.shape == (27, 23)
        assert np.linalg.norm(external.projection - external.projection.conj().T) > 0.1
        np.testing.assert_allclose(frames[wave].dual @ external.basis, 0, atol=5e-12)


def test_forcing_matches_streamed_complex_fourier_fields(frames: dict) -> None:
    left = frames[(1, 0, 0)].blocks[0]
    right = frames[(0, 1, 0)].blocks[1]
    a, b = np.array((0.3 + 0.1j, -0.2 + 0.4j)), np.array((0.7 - 0.1j,))
    size, omega = 5, 1.2
    _z, y, x = np.indices((size,) * 3)
    left_field = np.exp(2j * np.pi * x / size)[..., None] * (left.basis @ a)
    right_field = np.exp(2j * np.pi * y / size)[..., None] * (right.basis @ b)
    moments = d3.conserved_moment_matrix()
    physical = d3.stream_periodic(
        omega
        * np.einsum(
            "qab,...a,...b->...q",
            d3.equilibrium_hessian_at_rest(),
            np.einsum("aq,...q->...a", moments, left_field),
            np.einsum("aq,...q->...a", moments, right_field),
        )
    )
    _, forcing, _ = q.product_forcing(left, right, (1, 1, 0), size, omega)
    predicted = np.exp(2j * np.pi * (x + y) / size)[..., None] * (forcing @ np.kron(b, a))
    np.testing.assert_allclose(physical, predicted, atol=3e-14, rtol=1e-13)
    assert np.linalg.norm(physical) > 1e-3


def test_general_symmetric_square_action_and_vectorization() -> None:
    rng = np.random.default_rng(3102)
    matrix = rng.standard_normal((3, 3)) + 1j * rng.standard_normal((3, 3))
    a = rng.standard_normal(3) + 1j * rng.standard_normal(3)
    symmetric = q.symmetric_square_basis(3)
    assert symmetric.shape == (9, 6)
    np.testing.assert_allclose(symmetric.T @ symmetric, np.eye(6), atol=1e-15)
    product = symmetric.T @ np.kron(matrix, matrix) @ symmetric
    np.testing.assert_allclose(
        product @ (symmetric.T @ np.kron(a, a)),
        symmetric.T @ np.kron(matrix @ a, matrix @ a),
        atol=1e-13,
    )
    output, inputs = matrix[:2, :2], product
    coefficient = rng.standard_normal((2, 6)) + 1j * rng.standard_normal((2, 6))
    np.testing.assert_allclose(
        q.homological_operator(output, inputs) @ coefficient.reshape(-1, order="F"),
        (output @ coefficient - coefficient @ inputs).reshape(-1, order="F"),
        atol=1e-13,
    )


def test_near_resonance_condition_and_response_are_not_hidden() -> None:
    records = []
    for delta in (1e-4, 1e-7, 1e-11):
        _, record = q.solve_homological(
            np.diag((0.49 + delta, 0.2)), np.array([[0.49]]), np.ones((2, 1))
        )
        records.append(record)
    assert (
        records[0]["condition_number"]
        < records[1]["condition_number"]
        < records[2]["condition_number"]
    )
    assert records[2]["response_local_norm"] > 1e10
    assert records[2]["status"] == "nonsingular_ill_conditioned" and not records[2]["passed"]


def test_small_grid_orbit_reconstruction_matches_full_inventory() -> None:
    audit = q012c.brute_force_control()
    assert audit["passed"]
    assert audit["orbit"]["fixed_leaf_dimension"] == 27 * 5**3 - 4
    assert audit["brute_force"]["orbit_count"] == 5**3


def test_selected_first_shell_subtraction_matches_full_17_grid(frames: dict) -> None:
    quotient = q.grid_spectrum(17, 1.2, frames)
    brute = q.grid_spectrum(17, 1.2, frames, brute_force=True)
    for shell in (1, 2, 3):
        first, second = q.normal_ordering(quotient, shell), q.normal_ordering(brute, shell)
        assert first["coverage_passed"] and second["coverage_passed"]
        assert first["selected_dimension"] == second["selected_dimension"]
        assert first["external_dimension"] == second["external_dimension"]
        assert abs(first["normal_modulus_gap"] - second["normal_modulus_gap"]) <= 5e-12
        assert (
            abs(first["maximum_external_one_step_norm"] - second["maximum_external_one_step_norm"])
            <= 5e-12
        )


def test_incomplete_family_cannot_be_selected() -> None:
    single = {
        "size": 17,
        "omega": 1.0,
        "shell": 1,
        "coefficient_screen": {"coefficient_prequalified": True},
        "normal_ordering": {"normal_ordering_prequalified": True},
        "jointly_prequalified": True,
    }
    families, chosen = q012c.classify_families([single])
    assert chosen is None and not any(f["jointly_viable"] for f in families)
    complete = [{**single, "size": n} for n in q012c.GRID_SIZES]
    _, chosen = q012c.classify_families(complete)
    assert chosen["shell"] == 1 and chosen["omega"] == 1.0
    complete[1]["normal_ordering"] = {"normal_ordering_prequalified": False}
    complete[1]["jointly_prequalified"] = False
    assert q012c.classify_families(complete)[1] is None


def test_bad_inputs_do_not_trigger_an_experiment_or_vacuous_acceptance(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(q012c, "input_audit", lambda: {"passed": False})
    result = q012c.run_study()
    assert result["study_gate"] == "failed" and result["scientific_outcome"] == "inconclusive"
    assert result["cycle"]["conditions"] == [] and result["cycle"]["selected_family"] is None


def test_complete_registered_campaign_has_separate_scientific_axes(study: dict) -> None:
    cycle = study["cycle"]
    assert study["study_gate"] == "passed", cycle["validity_gates"]
    assert len(cycle["conditions"]) == 36 and len(cycle["families"]) == 12
    for condition in cycle["conditions"]:
        screen, normal = condition["coefficient_screen"], condition["normal_ordering"]
        rows = q012c.unpack_pairs(screen)
        assert len(rows) == screen["pair_count"] == (171, 1485, 3081)[condition["shell"] - 1]
        assert sum(r["product_dimension"] for r in rows) == screen["product_dimension_sum"]
        assert max(r["operator_dimension"] for r in rows) <= 108
        assert screen["coefficient_prequalified"] == all(r["passed"] for r in rows)
        assert normal["coverage_passed"] and normal["size"] == condition["size"]
        assert (
            normal["external_dimension"] + normal["selected_dimension"]
            == 27 * condition["size"] ** 3 - 4
        )
        assert condition["jointly_prequalified"] == (
            screen["coefficient_prequalified"] and normal["normal_ordering_prequalified"]
        )
        for row in rows:
            assert (
                row["response_global_l2_norm"]
                == row["response_local_norm"] / condition["size"] ** 1.5
            )
            if row["output_wave"] == [0, 0, 0]:
                assert row["external_dimension"] == 23 and row["zero_wave_moment_error"] <= 5e-12
            if row["status"].startswith("singular"):
                assert not row["passed"] and row["condition_number"] is None
    assert (
        cycle["map"].startswith("unmodified")
        and "neither actual exact resonance" in cycle["claim_boundary"]
    )
    assert _all_numeric_values_finite(cycle)


def test_stored_artifact_replays_all_pairs_and_matches_sources(study: dict) -> None:
    path = q012a.ARTIFACT_DIRECTORY / "q012c_d3q27_preflight.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(q012c.__file__))
    for name, module in (
        ("lattice", d3),
        ("spectra", spectra),
        ("quadratic", q),
        ("foundation_runner", q012a),
        ("spectral_runner", q012b),
    ):
        assert artifact["helper_sources"][name]["sha256"] == _file_sha256(Path(module.__file__))
    assert artifact["source"] == study["source"]
    assert artifact["cycle"] == study["cycle"]
    cycle = copy.deepcopy(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest


@pytest.mark.parametrize("size", [0, 2, 16, True, 3.5])
def test_invalid_grids_are_rejected(size: int) -> None:
    with pytest.raises(ValueError):
        q.odd_size(size)


def test_invalid_wave_shell_operator_and_table_are_rejected() -> None:
    for shell in (0, 4, True):
        with pytest.raises(ValueError):
            q.shell_waves(shell)
    with pytest.raises(ValueError):
        q.canonical_wave((1, 2), 17)
    with pytest.raises(ValueError):
        q.homological_operator(np.ones((2, 3)), np.eye(2))
    with pytest.raises(ValueError):
        q.solve_homological(np.eye(2), np.eye(2), np.ones((2, 1)))
    with pytest.raises(ValueError):
        q012c.unpack_pairs({"pair_columns": ["a", "b"], "pair_rows": [[1]]})
    assert q.canonical_wave((9, -9, 17), 17) == (-8, 8, 0)
