from __future__ import annotations

import copy
import json
from itertools import permutations
from pathlib import Path

import numpy as np
import pytest

from research import d3q27 as d3
from research import d3q27_spectra as spectra
from research import q012a_d3q27_foundation as q012a
from research import q012b_d3q27_spectral as q012b
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def study() -> dict:
    return q012b.run_study()


def test_schur_projector_is_oblique_invariant_and_rank_four() -> None:
    k = np.array((0.1, 0.07, 0.04))
    point = spectra.cluster_point(k, 1.2)
    matrix = d3.fourier_symbol(k, 1.2)
    p = point.spectral_projector
    assert point.passed and np.linalg.matrix_rank(p, tol=1e-10) == 4
    np.testing.assert_allclose(p @ p, p, atol=1e-13, rtol=0)
    np.testing.assert_allclose(p @ matrix, matrix @ p, atol=1e-13, rtol=0)
    assert np.linalg.norm(p - p.conj().T) > 0.1


def test_degenerate_shear_is_a_plane_and_internal_permutations_are_harmless() -> None:
    k = np.array((0.1, 0.0, 0.0))
    point = spectra.cluster_point(k, 1.2)
    assert point.shear_basis is not None and point.shear_basis.shape == (27, 2)
    assert abs(point.shear_values[0] - point.shear_values[1]) < 1e-12
    for indices in permutations(range(4)):
        reordered = spectra.cluster_point(k, 1.2, reference_values=point.eigenvalues[list(indices)])
        assert spectra.subspace_difference(point.basis, reordered.basis) < 1e-12
        assert spectra.subspace_difference(point.shear_basis, reordered.shear_basis) < 1e-12
    unitary = np.array(((1, 1j), (1j, 1))) / np.sqrt(2)
    assert spectra.subspace_difference(point.shear_basis, point.shear_basis @ unitary) < 1e-13


def test_exact_external_collision_is_not_arbitrarily_split() -> None:
    with pytest.raises(np.linalg.LinAlgError, match="do not split"):
        spectra._ordered_schur(np.eye(3, dtype=complex), np.ones(2), np.ones(1))


def test_path_stops_at_first_failure_without_mutating_direction() -> None:
    direction = np.array((1.0, 2.0, 3.0))
    before = direction.copy()
    accepted, failure = spectra.track_ray(direction, 1.2, np.array((0.0, 0.01, 2.8)))
    assert np.array_equal(direction, before)
    assert len(accepted) == 2 and failure is not None and failure["failed_gates"]
    assert all(p.passed for p in accepted)


def test_registered_paths_have_reversible_and_rotation_consistent_prefixes(study: dict) -> None:
    audit = study["cycle"]["audits"]["paths"]
    assert audit["path_count"] == 16 and audit["registered_radius_count"] == 145
    assert audit["passed"]
    for record in audit["records"]:
        assert record["cutoff_bracket"]["last_pass"] >= 0.5
        assert record["reversal_subspace_error"] <= 1e-10
        assert record["shear_rotation_subspace_error"] <= 1e-10
        assert len(record["accepted_samples"]) == record["accepted_sample_count"]
        if record["first_failure"] is not None:
            assert record["first_failure"]["failed_gates"]
            assert record["cutoff_bracket"]["first_fail"] > record["cutoff_bracket"]["last_pass"]


def test_small_wave_two_shear_rates_and_acoustic_pair(study: dict) -> None:
    audit = study["cycle"]["audits"]["small_wave"]
    assert audit["passed"] and audit["sample_count"] == 64
    for record in audit["records"]:
        assert len(record["samples"]) == 4
        for sample in record["samples"]:
            assert len(sample["shear_decay_rates"]) == len(sample["acoustic_speeds"]) == 2
            assert min(sample["shear_decay_rates"]) > 0
        assert record["samples"][-1]["maximum_shear_relative_error"] <= 0.01


def test_orbit_multiplicity_and_brute_force_parity(study: dict) -> None:
    audit = study["cycle"]["audits"]["parity"]
    assert audit["passed"]
    for record in audit["grids"]:
        assert record["represented_wave_count"] == record["size"] ** 3
        assert record["zero_wave_unit_count"] == 4
        assert record["classification_boundary_count"] == 0
        assert record["strict_unit_count"] == (4 if record["size"] % 2 else 7)
        if record["size"] % 2 == 0:
            nonzero = [r for r in record["unit_records"] if r["index"] != [0, 0, 0]]
            assert len(nonzero) == 1 and nonzero[0]["orbit_multiplicity"] == 3
            assert nonzero[0]["index"] == [0, 0, record["size"] // 2]
    assert len(audit["brute_force_controls"]) == 2
    assert all(r["passed"] for r in audit["brute_force_controls"])
    assert len(audit["direct_nyquist_symbols"]) == 12
    assert all(r["minus_one_count"] == 1 for r in audit["direct_nyquist_symbols"])


def test_inventory_is_only_a_radial_proxy_and_does_not_claim_normal_dominance(study: dict) -> None:
    cycle = study["cycle"]
    assert len(cycle["audits"]["radial_inventory"]) == 8
    for record in cycle["audits"]["radial_inventory"]:
        assert record["size"] % 2 == 1
        assert (
            record["four_mode_real_coordinate_count"]
            == 4 * record["nonzero_wave_count_in_radial_proxy"]
        )
        assert "untested directions" in record["scope"]
    assert "no ball-wide spectral split, normal dominance" in cycle["claim_boundary"]


def test_study_gate_and_result_digest(study: dict) -> None:
    assert study["study_gate"] == "passed" and study["scientific_outcome"] == "accepted"
    cycle = copy.deepcopy(study["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert all(cycle["validity_gates"].values()) and all(cycle["hypothesis_gates"].values())


def test_stored_artifact_replays_and_matches_all_sources(study: dict) -> None:
    path = q012a.ARTIFACT_DIRECTORY / "q012b_d3q27_spectral.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(q012b.__file__))
    for name, module in (("lattice", d3), ("spectra", spectra), ("foundation_runner", q012a)):
        assert artifact["helper_sources"][name]["sha256"] == _file_sha256(Path(module.__file__))
    assert artifact["cycle"] == study["cycle"]
    assert artifact["source"] == study["source"]


@pytest.mark.parametrize("radii", [[], [0.01, 0.02], [0, 0], [0, float("nan")]])
def test_invalid_paths_are_rejected(radii: list) -> None:
    with pytest.raises(ValueError):
        spectra.track_ray(np.array((1, 0, 0)), 1.2, np.asarray(radii))
