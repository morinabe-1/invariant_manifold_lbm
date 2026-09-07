"""Q012b: continuous D3Q27 cluster tracking, shear planes and Nyquist parity."""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

from research import d3q27 as d3
from research import d3q27_spectra as spectra
from research import q012a_d3q27_foundation as q012a
from ttim_lbm.provenance import runtime_metadata, source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

Q012A_ARTIFACT_SHA256 = "b26c6dfde65b24f424fcadffe9c9c75f4236171242e819921e6e0d06cf5ba327"
Q012A_RESULT_SHA256 = "385e0e55211c24f99b8dd4b5591862b5c83295f5199beb286f0db56bbce4801b"
RAYS = {"axis": (1, 0, 0), "face": (1, 1, 0), "body": (1, 1, 1), "generic": (1, 2, 3)}
OMEGAS = (1.0, 1.2, 1.5, 1.8)
RADII = np.linspace(0, 1.8, 145)


def input_audit() -> dict[str, Any]:
    path = q012a.ARTIFACT_DIRECTORY / "q012a_d3q27_foundation.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    prior = q012a.audit_prerequisites()
    checks = {
        "artifact_seal": _file_sha256(path) == Q012A_ARTIFACT_SHA256,
        "runner_seal": _file_sha256(Path(q012a.__file__)) == artifact["runner_source"]["sha256"],
        "helper_seal": _file_sha256(Path(d3.__file__)) == artifact["helper_source"]["sha256"],
        "result_digest": q012a._digest(cycle) == digest == Q012A_RESULT_SHA256,
        "all_foundation_audits_accepted": artifact["scientific_outcome"] == "accepted"
        and artifact["study_gate"] == "passed"
        and len(cycle["audits"]) == 7
        and all(a["passed"] for a in cycle["audits"].values()),
        "d2q9_prerequisites_still_reproduce": prior["passed"],
    }
    return {
        "filename": path.name,
        "sha256": _file_sha256(path),
        "checks": checks,
        "passed": all(checks.values()),
    }


def path_campaign() -> dict[str, Any]:
    rotations = (
        np.array(((0, 1, 0), (1, 0, 0), (0, 0, 1))),
        np.array(((0, 0, 1), (1, 0, 0), (0, 1, 0))),
    )
    records = []
    for omega, (name, raw_direction) in product(OMEGAS, RAYS.items()):
        direction = np.array(raw_direction, dtype=float)
        direction /= np.linalg.norm(direction)
        forward, first_failure = spectra.track_ray(direction, omega, RADII)
        backwards = []
        for source in reversed(forward):
            backwards.append(
                spectra.cluster_point(
                    source.wavevector,
                    omega,
                    backwards[-1] if backwards else None,
                    reference_values=source.eigenvalues if not backwards else None,
                )
            )
        backwards.reverse()
        reversal_error = max(
            (spectra.subspace_difference(a.basis, b.basis) for a, b in zip(forward, backwards)),
            default=0.0,
        )
        shear_reversal_error = max(
            (
                spectra.subspace_difference(a.shear_basis, b.shear_basis)
                for a, b in zip(forward, backwards)
                if a.shear_basis is not None and b.shear_basis is not None
            ),
            default=0.0,
        )
        symmetry_error = shear_symmetry_error = 0.0
        symmetry_lengths = []
        for rotation in rotations:
            rotated, _ = (
                spectra.track_ray(rotation @ direction, omega, RADII[: len(forward)])
                if forward
                else ([], None)
            )
            symmetry_lengths.append(len(rotated))
            p = d3.population_permutation(rotation)
            for a, b in zip(forward, rotated):
                symmetry_error = max(
                    symmetry_error, spectra.subspace_difference(p @ a.basis, b.basis)
                )
                if a.shear_basis is not None and b.shear_basis is not None:
                    shear_symmetry_error = max(
                        shear_symmetry_error,
                        spectra.subspace_difference(p @ a.shear_basis, b.shear_basis),
                    )
        last_radius = float(RADII[len(forward) - 1]) if forward else 0.0
        record = {
            "omega": omega,
            "ray": name,
            "unit_direction": direction.tolist(),
            "accepted_sample_count": len(forward),
            "accepted_samples": [p.record() for p in forward],
            "cutoff_bracket": {
                "last_pass": last_radius,
                "first_fail": None if first_failure is None else first_failure["radius"],
                "right_censored": first_failure is None,
            },
            "first_failure": first_failure,
            "reversal_subspace_error": reversal_error,
            "shear_reversal_subspace_error": shear_reversal_error,
            "rotated_sample_counts": symmetry_lengths,
            "rotation_subspace_error": symmetry_error,
            "shear_rotation_subspace_error": shear_symmetry_error,
            "passed": last_radius >= 0.5
            and max(reversal_error, shear_reversal_error, symmetry_error, shear_symmetry_error)
            <= 1e-10
            and all(p.passed for p in backwards)
            and all(n == len(forward) for n in symmetry_lengths),
        }
        records.append(record)
    return {
        "path_count": len(records),
        "registered_radius_count": len(RADII),
        "records": records,
        "passed": len(records) == 16 and all(r["passed"] for r in records),
    }


def small_wave_campaign() -> dict[str, Any]:
    records = []
    radii = (0.04, 0.02, 0.01, 0.005)
    for omega, (name, raw_direction) in product(OMEGAS, RAYS.items()):
        n = np.asarray(raw_direction, dtype=float)
        n /= np.linalg.norm(n)
        viscosity = (1 / omega - 0.5) / 3
        samples = []
        for radius in radii:
            point = spectra.cluster_point(radius * n, omega)
            if point.shear_values is None or point.acoustic_values is None:
                raise RuntimeError("small-wave shear/acoustic split was not resolved")
            shear_rates = -np.log(np.abs(point.shear_values)) / radius**2
            acoustic_speeds = np.abs(np.angle(point.acoustic_values)) / radius
            samples.append(
                {
                    "radius": radius,
                    "shear_decay_rates": shear_rates.tolist(),
                    "acoustic_speeds": acoustic_speeds.tolist(),
                    "cluster_passed": point.passed,
                    "maximum_shear_relative_error": float(
                        np.max(np.abs(shear_rates / viscosity - 1))
                    ),
                    "maximum_acoustic_relative_error": float(
                        np.max(np.abs(acoustic_speeds * np.sqrt(3) - 1))
                    ),
                }
            )
        last = samples[-1]
        records.append(
            {
                "omega": omega,
                "ray": name,
                "viscosity": viscosity,
                "samples": samples,
                "passed": all(s["cluster_passed"] for s in samples)
                and last["maximum_shear_relative_error"] <= 0.01
                and last["maximum_acoustic_relative_error"] <= 0.01,
            }
        )
    return {
        "ray_omega_count": len(records),
        "sample_count": 4 * len(records),
        "records": records,
        "passed": all(r["passed"] for r in records),
    }


def parity_campaign() -> dict[str, Any]:
    grids = [spectra.parity_audit(n) for n in (16, 17, 32, 33)]
    controls = []
    for size in (4, 5):
        quotient = spectra.parity_audit(size)
        full = spectra.parity_audit(size, brute_force=True)
        controls.append(
            {
                "size": size,
                "orbit_audit": quotient,
                "brute_force_audit": full,
                "passed": quotient["passed"]
                and full["passed"]
                and quotient["strict_unit_count"] == full["strict_unit_count"]
                and abs(quotient["largest_nonunit_modulus"] - full["largest_nonunit_modulus"])
                <= 5e-14,
            }
        )
    direct = []
    for omega, axis in product(OMEGAS, range(3)):
        k = np.zeros(3)
        k[axis] = np.pi
        values = np.linalg.eigvals(d3.fourier_symbol(k, omega))
        count = int(np.count_nonzero(np.abs(values + 1) < 1e-10))
        direct.append(
            {
                "omega": omega,
                "axis": axis,
                "minus_one_count": count,
                "minimum_distance_to_minus_one": float(np.min(np.abs(values + 1))),
                "passed": count == 1,
            }
        )
    return {
        "grids": grids,
        "brute_force_controls": controls,
        "direct_nyquist_symbols": direct,
        "passed": all(r["passed"] for r in (*grids, *controls, *direct)),
    }


def radial_grid_inventory(paths: dict[str, Any]) -> list[dict[str, Any]]:
    records = []
    for omega in OMEGAS:
        cutoff = min(
            r["cutoff_bracket"]["last_pass"] for r in paths["records"] if r["omega"] == omega
        )
        for size in (17, 33):
            frequencies = 2 * np.pi * np.fft.fftfreq(size)
            squared = sum(
                np.square(x)
                for x in np.meshgrid(frequencies, frequencies, frequencies, indexing="ij")
            )
            nonzero_count = int(np.count_nonzero((squared > 0) & (squared <= cutoff**2)))
            records.append(
                {
                    "omega": omega,
                    "size": size,
                    "sampled_ray_minimum_cutoff": cutoff,
                    "nonzero_wave_count_in_radial_proxy": nonzero_count,
                    "four_mode_real_coordinate_count": 4 * nonzero_count,
                    "nyquist_excluded_by_odd_grid": True,
                    "scope": "radial proxy inventory only; untested directions and nonlinear closure require Q012c",
                }
            )
    return records


def run_study() -> dict[str, Any]:
    inputs = input_audit()
    audits = {}
    if inputs["passed"]:
        audits = {
            "paths": path_campaign(),
            "small_wave": small_wave_campaign(),
            "parity": parity_campaign(),
        }
        audits["radial_inventory"] = radial_grid_inventory(audits["paths"])
    coverage = bool(audits) and (
        audits["paths"]["path_count"] == 16
        and audits["small_wave"]["sample_count"] == 64
        and len(audits["parity"]["grids"]) == 4
        and len(audits["parity"]["direct_nyquist_symbols"]) == 12
        and len(audits["radial_inventory"]) == 8
    )
    validity = {
        "sealed_inputs": inputs["passed"],
        "registered_coverage": coverage,
        "finite_numeric_evidence": _all_numeric_values_finite(audits),
    }
    hypotheses = (
        {name: audits[name]["passed"] for name in ("paths", "small_wave", "parity")}
        if audits
        else {}
    )
    outcome = (
        "inconclusive"
        if not all(validity.values())
        else "accepted"
        if all(hypotheses.values())
        else "rejected"
    )
    cycle = {
        "question": "Where is the sampled separated four-dimensional D3Q27 hydrodynamic cluster, and how does grid parity obstruct it?",
        "input_audit": inputs,
        "audits": audits,
        "validity_gates": validity,
        "hypothesis_gates": hypotheses,
        "study_validity": "passed" if all(validity.values()) else "failed",
        "scientific_outcome": outcome,
        "claim_boundary": "finite ray samples and parity regression only; no ball-wide spectral split, normal dominance, nonresonance or 3D manifold theorem",
        "next_question": "Q012c: fixed-four-conservation-leaf quadratic sector nonresonance and normal ordering for 3D first-shell candidates"
        if outcome == "accepted"
        else "Diagnose the first Q012b failure before selecting 3D reduced coordinates",
    }
    cycle["result_digest_sha256"] = q012a._digest(cycle)
    sources = {
        name: {
            "filename": Path(module.__file__).name,
            "sha256": _file_sha256(Path(module.__file__)),
        }
        for name, module in (("lattice", d3), ("spectra", spectra), ("foundation_runner", q012a))
    }
    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "source": source_metadata(),
        "runtime": runtime_metadata(),
        "helper_sources": sources,
        "runner_source": {"filename": Path(__file__).name, "sha256": _file_sha256(Path(__file__))},
        "cycle": cycle,
        "study_gate": cycle["study_validity"],
        "scientific_outcome": outcome,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_study()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "study_gate": result["study_gate"],
                "scientific_outcome": result["scientific_outcome"],
                "hypothesis_gates": result["cycle"]["hypothesis_gates"],
            }
        )
    )
    if result["scientific_outcome"] != "accepted":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
