"""Cluster-preserving Fourier quadratic operators for D3Q27 research.

All coordinates here are symbol-local complex Fourier coordinates.  The shear
plane is never split into individual eigenvectors.  This module does not claim
an invariant manifold from a successful finite-degree coefficient solve.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import combinations_with_replacement, product
from numbers import Integral
from typing import Any

import numpy as np
from scipy.linalg import block_diag, null_space, svd

from research import d3q27 as d3
from research import d3q27_spectra as spectra

Wave = tuple[int, int, int]
LABELS = ("shear", "acoustic_plus", "acoustic_minus")
STRUCTURAL_TOL = 5e-12
CONDITION_LIMIT = 1e8


def odd_size(size: int) -> int:
    if isinstance(size, bool) or not isinstance(size, Integral) or size < 3 or size % 2 == 0:
        raise ValueError("size must be an odd integer at least three")
    return int(size)


def canonical_wave(wave: Wave, size: int) -> Wave:
    n = odd_size(size)
    if len(wave) != 3 or any(isinstance(v, bool) or not isinstance(v, Integral) for v in wave):
        raise ValueError("wave must contain three integers")
    return tuple(int((int(v) + n // 2) % n - n // 2) for v in wave)


def shell_waves(shell: int) -> tuple[Wave, ...]:
    if isinstance(shell, bool) or not isinstance(shell, Integral) or shell not in (1, 2, 3):
        raise ValueError("shell must be 1, 2 or 3")
    return tuple(w for w in product((-1, 0, 1), repeat=3) if 0 < sum(v * v for v in w) <= shell)


def complex_record(value: complex) -> list[float]:
    return [float(value.real), float(value.imag)]


@dataclass(frozen=True)
class InputBlock:
    wave: Wave
    label: str
    basis: np.ndarray
    dynamics: np.ndarray

    @property
    def dimension(self) -> int:
        return self.basis.shape[1]

    @property
    def key(self) -> tuple[Wave, str]:
        return self.wave, self.label


@dataclass(frozen=True)
class HydroFrame:
    wave: Wave
    blocks: tuple[InputBlock, ...]
    projector: np.ndarray
    dual: np.ndarray
    diagnostics: dict[str, float]

    @property
    def basis(self) -> np.ndarray:
        return np.column_stack([b.basis for b in self.blocks])


@dataclass(frozen=True)
class ExternalSector:
    wave: Wave
    basis: np.ndarray
    dynamics: np.ndarray
    selected_projector: np.ndarray
    projection: np.ndarray
    structural_error: float


def build_frames(size: int, omega: float) -> tuple[dict[Wave, HydroFrame], dict[str, Any]]:
    """Continue three rays and transport their invariant blocks to all 26 waves."""
    size = odd_size(size)
    representatives = ((0, 0, 1), (0, 1, 1), (1, 1, 1))
    frames: dict[Wave, HydroFrame] = {}
    path_records = []
    for representative in representatives:
        k = 2 * np.pi * np.asarray(representative) / size
        radius = float(np.linalg.norm(k))
        radii = np.linspace(0, radius, int(np.ceil(radius / 0.0125)) + 1)
        path, failure = spectra.track_ray(k, omega, radii)
        if failure is not None or len(path) != len(radii):
            raise np.linalg.LinAlgError(
                f"first-shell continuation failed: {representative}: {failure}"
            )
        point = path[-1]
        matrix = d3.fourier_symbol(k, omega)
        hydro = point.basis.conj().T @ matrix @ point.basis
        bases = {"shear": point.shear_basis}
        for label, index in (
            ("acoustic_plus", np.argmax(point.acoustic_values.imag)),
            ("acoustic_minus", np.argmin(point.acoustic_values.imag)),
        ):
            value = point.acoustic_values[index]
            excluded = np.delete(point.eigenvalues, np.argmin(np.abs(point.eigenvalues - value)))
            _, unitary = spectra._ordered_schur(hydro, np.asarray([value]), excluded)
            bases[label] = point.basis @ unitary[:, :1]
        path_records.append(
            {
                "representative": list(representative),
                "samples": len(path),
                "endpoint": point.record(),
            }
        )
        for rotation in d3.cubic_symmetries():
            wave = tuple(int(v) for v in rotation @ representative)
            if wave in frames:
                continue
            p = d3.population_permutation(rotation)
            symbol = d3.fourier_symbol(2 * np.pi * np.asarray(wave) / size, omega)
            blocks = tuple(
                InputBlock(
                    wave, label, p @ bases[label], bases[label].conj().T @ matrix @ bases[label]
                )
                for label in LABELS
            )
            frame = np.column_stack([b.basis for b in blocks])
            dynamics = block_diag(*(b.dynamics for b in blocks))
            projector = p @ point.spectral_projector @ p.T
            dual = np.linalg.solve(frame.conj().T @ frame, frame.conj().T) @ projector
            diagnostics = {
                "frame_condition": float(np.linalg.cond(frame)),
                "frame_invariance": float(np.linalg.norm(symbol @ frame - frame @ dynamics)),
                "left_invariance": float(np.linalg.norm(dual @ symbol - dynamics @ dual)),
                "duality": float(np.linalg.norm(dual @ frame - np.eye(4))),
                "projector_reconstruction": float(np.linalg.norm(frame @ dual - projector)),
                "symbol_covariance": float(np.linalg.norm(symbol - p @ matrix @ p.T)),
                "projector_norm": point.measurements["spectral_projector_norm"],
                "local_schur_sep": point.measurements["schur_sylvester_sep"],
            }
            frames[wave] = HydroFrame(wave, blocks, projector, dual, diagnostics)
    conjugacy_error = symmetry_error = 0.0
    conjugate_label = {
        "shear": "shear",
        "acoustic_plus": "acoustic_minus",
        "acoustic_minus": "acoustic_plus",
    }
    for wave, frame in frames.items():
        opposite = {b.label: b for b in frames[tuple(-v for v in wave)].blocks}
        for block in frame.blocks:
            conjugacy_error = max(
                conjugacy_error,
                spectra.subspace_difference(
                    block.basis.conj(), opposite[conjugate_label[block.label]].basis
                ),
            )
        for rotation in d3.cubic_symmetries():
            moved = tuple(int(v) for v in rotation @ wave)
            p = d3.population_permutation(rotation)
            for left, right in zip(frame.blocks, frames[moved].blocks):
                symmetry_error = max(
                    symmetry_error, spectra.subspace_difference(p @ left.basis, right.basis)
                )
    structural_names = (
        "frame_invariance",
        "left_invariance",
        "duality",
        "projector_reconstruction",
        "symbol_covariance",
    )
    structural = max(
        conjugacy_error,
        symmetry_error,
        max(f.diagnostics[name] for f in frames.values() for name in structural_names),
    )
    condition = max(f.diagnostics["frame_condition"] for f in frames.values())
    return frames, {
        "frame_count": len(frames),
        "path_records": path_records,
        "maximum_structural_error": structural,
        "maximum_frame_condition": condition,
        "conjugacy_subspace_error": conjugacy_error,
        "cubic_subspace_error": symmetry_error,
        "maximum_projector_norm": max(f.diagnostics["projector_norm"] for f in frames.values()),
        "minimum_local_schur_sep": min(f.diagnostics["local_schur_sep"] for f in frames.values()),
        "passed": len(frames) == 26 and structural <= STRUCTURAL_TOL and condition <= 100,
    }


def external_sector(
    wave: Wave, size: int, omega: float, frame: HydroFrame | None
) -> ExternalSector:
    wave = canonical_wave(wave, size)
    matrix = d3.fourier_symbol(2 * np.pi * np.asarray(wave) / size, omega)
    selected = np.zeros((27, 27), dtype=complex) if frame is None else frame.projector
    projection = np.eye(27) - selected
    if wave == (0, 0, 0):
        if frame is not None:
            raise ValueError("the fixed leaf has no zero-wave conserved input frame")
        basis = null_space(d3.conserved_moment_matrix()).astype(complex)
    elif frame is None:
        basis = np.eye(27, dtype=complex)
    else:
        if frame.wave != wave:
            raise ValueError("frame and output wave do not match")
        basis = null_space(selected)
    expected = 23 if wave == (0, 0, 0) or frame is not None else 27
    if basis.shape != (27, expected):
        raise np.linalg.LinAlgError("external invariant complement has the wrong dimension")
    dynamics = basis.conj().T @ matrix @ basis
    error = max(
        float(np.linalg.norm(matrix @ basis - basis @ dynamics)),
        float(np.linalg.norm(selected @ basis)),
        float(np.linalg.norm(basis.conj().T @ basis - np.eye(expected))),
    )
    if wave == (0, 0, 0):
        error = max(error, float(np.linalg.norm(d3.conserved_moment_matrix() @ basis)))
    return ExternalSector(wave, basis, dynamics, selected, projection, error)


def symmetric_square_basis(dimension: int) -> np.ndarray:
    if isinstance(dimension, bool) or not isinstance(dimension, Integral) or dimension < 1:
        raise ValueError("dimension must be a positive integer")
    columns = []
    for i, j in combinations_with_replacement(range(dimension), 2):
        column = np.zeros((dimension, dimension))
        if i == j:
            column[i, j] = 1
        else:
            column[i, j] = column[j, i] = 1 / np.sqrt(2)
        columns.append(column.reshape(-1, order="F"))
    return np.column_stack(columns)


def product_forcing(
    left: InputBlock, right: InputBlock, output: Wave, size: int, omega: float
) -> tuple[np.ndarray, np.ndarray, float]:
    moments = d3.conserved_moment_matrix()
    hessian = d3.equilibrium_hessian_at_rest()
    k = 2 * np.pi * np.asarray(canonical_wave(output, size)) / size
    local = np.einsum("qab,ai,bj->qij", hessian, moments @ left.basis, moments @ right.basis)
    forcing = (omega * np.exp(-1j * (d3.VELOCITIES @ k)))[:, None] * local.reshape(
        27, -1, order="F"
    )
    dynamics = np.kron(right.dynamics, left.dynamics)
    if left.key != right.key:
        return dynamics, forcing, 0.0
    symmetric = symmetric_square_basis(left.dimension)
    restricted = symmetric.T @ dynamics @ symmetric
    error = float(np.linalg.norm(dynamics @ symmetric - symmetric @ restricted))
    return restricted, forcing @ symmetric, error


def homological_operator(output: np.ndarray, inputs: np.ndarray) -> np.ndarray:
    output, inputs = np.asarray(output, dtype=complex), np.asarray(inputs, dtype=complex)
    if (
        output.ndim != 2
        or inputs.ndim != 2
        or output.shape[0] != output.shape[1]
        or inputs.shape[0] != inputs.shape[1]
        or min(len(output), len(inputs)) == 0
        or not np.all(np.isfinite(output))
        or not np.all(np.isfinite(inputs))
    ):
        raise ValueError("homological blocks must be finite nonempty square matrices")
    return np.kron(np.eye(len(inputs)), output) - np.kron(inputs.T, np.eye(len(output)))


def solve_homological(
    output: np.ndarray, inputs: np.ndarray, forcing: np.ndarray
) -> tuple[np.ndarray, dict[str, Any]]:
    operator = homological_operator(output, inputs)
    forcing = np.asarray(forcing, dtype=complex)
    if forcing.shape != (len(output), len(inputs)) or not np.all(np.isfinite(forcing)):
        raise ValueError("forcing must be a finite output-dimension by input-dimension matrix")
    u, singular, vh = svd(operator, full_matrices=False, check_finite=False)
    threshold = float(100 * np.finfo(float).eps * len(operator) * singular[0])
    retained = singular > threshold
    vector = forcing.reshape(-1, order="F")
    null_norm = float(np.linalg.norm(u[:, ~retained].conj().T @ vector))
    nonsingular = bool(np.all(retained))
    condition = float(singular[0] / singular[-1]) if nonsingular else None
    solution = -(vh[retained].conj().T @ ((u[:, retained].conj().T @ vector) / singular[retained]))
    solution = solution.reshape(forcing.shape, order="F")
    residual = float(
        np.linalg.norm(output @ solution - solution @ inputs + forcing)
        / max(float(np.linalg.norm(forcing)), 1e-14)
    )
    near = singular <= max(10 * singular[-1], 1e-4 * singular[0])
    status = (
        ("nonsingular_practical" if condition <= CONDITION_LIMIT else "nonsingular_ill_conditioned")
        if nonsingular
        else (
            "singular_compatible"
            if null_norm <= 1e-10 * max(1, np.linalg.norm(forcing))
            else "singular_incompatible"
        )
    )
    return solution, {
        "operator_dimension": len(operator),
        "numerical_rank": int(np.count_nonzero(retained)),
        "rank_threshold": threshold,
        "smallest_singular_value": float(singular[-1]),
        "largest_singular_value": float(singular[0]),
        "condition_number": condition,
        "minimum_eigenvalue_detuning": float(
            np.min(np.abs(np.linalg.eigvals(output)[:, None] - np.linalg.eigvals(inputs)[None, :]))
        ),
        "forcing_norm": float(np.linalg.norm(forcing)),
        "left_null_forcing_norm": null_norm,
        "weak_left_subspace_dimension": int(np.count_nonzero(near)),
        "weak_left_forcing_norm": float(np.linalg.norm(u[:, near].conj().T @ vector)),
        "response_local_norm": float(np.linalg.norm(solution)),
        "solve_relative_residual": residual,
        "status": status,
        "passed": status == "nonsingular_practical" and residual <= 1e-10,
    }


def audit_pair(
    left: InputBlock,
    right: InputBlock,
    size: int,
    omega: float,
    sector: ExternalSector,
    output_frame: HydroFrame | None,
) -> dict[str, Any]:
    dynamics, forcing, product_error = product_forcing(left, right, sector.wave, size, omega)
    external_forcing = sector.basis.conj().T @ sector.projection @ forcing
    solution, record = solve_homological(sector.dynamics, dynamics, external_forcing)
    population_response = sector.basis @ solution
    scale = max(1, float(np.linalg.norm(population_response)))
    gauge_error = float(np.linalg.norm(sector.selected_projector @ population_response) / scale)
    mean_error = (
        float(np.linalg.norm(d3.conserved_moment_matrix() @ population_response) / scale)
        if sector.wave == (0, 0, 0)
        else 0.0
    )
    mean_forcing = (
        float(np.linalg.norm(d3.conserved_moment_matrix() @ forcing))
        if sector.wave == (0, 0, 0)
        else 0.0
    )
    return {
        "left_wave": list(left.wave),
        "left_label": left.label,
        "right_wave": list(right.wave),
        "right_label": right.label,
        "output_wave": list(sector.wave),
        "output_is_selected": output_frame is not None,
        "product_dimension": len(dynamics),
        "external_dimension": len(sector.dynamics),
        "symmetric_square": left.key == right.key,
        **record,
        "response_global_l2_norm": record["response_local_norm"] / size**1.5,
        "internal_forcing_norm": 0.0
        if output_frame is None
        else float(np.linalg.norm(output_frame.dual @ forcing)),
        "graph_gauge_error": gauge_error,
        "zero_wave_moment_error": mean_error,
        "zero_wave_forcing_moment_error": mean_forcing,
        "structural_error": max(
            product_error, sector.structural_error, gauge_error, mean_error, mean_forcing
        ),
        "passed": record["passed"] and max(gauge_error, mean_error) <= STRUCTURAL_TOL,
    }


def coefficient_campaign(size: int, omega: float, frames: dict[Wave, HydroFrame]) -> list[dict]:
    """Audit every pair; only identical problems shared by nested sets are cached."""
    pair_cache, sector_cache = {}, {}
    records = []
    for shell in (1, 2, 3):
        waves = shell_waves(shell)
        blocks = [b for w in waves for b in frames[w].blocks]
        pair_records = []
        for left, right in combinations_with_replacement(blocks, 2):
            wave = canonical_wave(tuple(a + b for a, b in zip(left.wave, right.wave)), size)
            selected = wave in waves
            frame = frames[wave] if selected else None
            sector_key = wave, selected
            if sector_key not in sector_cache:
                sector_cache[sector_key] = external_sector(wave, size, omega, frame)
            key = left.key, right.key, selected
            if key not in pair_cache:
                pair_cache[key] = audit_pair(
                    left, right, size, omega, sector_cache[sector_key], frame
                )
            pair_records.append(pair_cache[key])
        dimension = sum(b.dimension for b in blocks)
        conditioned = [r for r in pair_records if r["condition_number"] is not None]
        counts = Counter(r["status"] for r in pair_records)
        records.append(
            {
                "shell": shell,
                "wave_count": len(waves),
                "real_coordinate_count": dimension,
                "input_block_count": len(blocks),
                "pair_count": len(pair_records),
                "product_dimension_sum": sum(r["product_dimension"] for r in pair_records),
                "coverage_passed": len(pair_records) == len(blocks) * (len(blocks) + 1) // 2
                and sum(r["product_dimension"] for r in pair_records)
                == dimension * (dimension + 1) // 2,
                "status_counts": dict(sorted(counts.items())),
                "maximum_structural_error": max(r["structural_error"] for r in pair_records),
                "worst_nonsingular_condition": max(
                    conditioned, key=lambda r: r["condition_number"]
                ),
                "first_singular_pair": next(
                    (r for r in pair_records if r["condition_number"] is None), None
                ),
                "pair_records": pair_records,
                "coefficient_prequalified": all(r["passed"] for r in pair_records),
            }
        )
    return records


def grid_spectrum(
    size: int,
    omega: float,
    frames: dict[Wave, HydroFrame] | None = None,
    *,
    brute_force: bool = False,
) -> dict[str, Any]:
    """Full-grid eigenvalue inventory, with optional first-shell restrictions."""
    size = odd_size(size)
    frames = {} if frames is None else frames
    indices = list(product(range(-size // 2 + 1, size // 2 + 1), repeat=3))
    multiplicities = (
        Counter(tuple(sorted(abs(v) for v in w)) for w in indices)
        if not brute_force
        else {w: 1 for w in indices}
    )
    rows = []
    # Streaming is unitary, so every unselected full block has ||A(k)||2 = ||C||2.
    collision_norm = float(np.linalg.norm(d3.collision_symbol(omega), ord=2))
    for wave, multiplicity in sorted(multiplicities.items()):
        matrix = d3.fourier_symbol(2 * np.pi * np.asarray(wave) / size, omega)
        if wave == (0, 0, 0):
            sector = external_sector(wave, size, omega, None)
            values = np.linalg.eigvals(sector.dynamics)
            full_norm = float(np.linalg.norm(sector.dynamics, ord=2))
        else:
            values = np.linalg.eigvals(matrix)
            full_norm = collision_norm
        row = {
            "wave": wave,
            "multiplicity": multiplicity,
            "full_values": values,
            "full_norm": full_norm,
        }
        if wave in frames:
            frame = frames[wave]
            sector = external_sector(wave, size, omega, frame)
            row.update(
                {
                    "selected_values": np.concatenate(
                        [np.linalg.eigvals(b.dynamics) for b in frame.blocks]
                    ),
                    "external_values": np.linalg.eigvals(sector.dynamics),
                    "external_norm": float(np.linalg.norm(sector.dynamics, ord=2)),
                    "projector_norm": frame.diagnostics["projector_norm"],
                    "local_schur_sep": frame.diagnostics["local_schur_sep"],
                }
            )
        rows.append(row)
    return {
        "size": size,
        "omega": omega,
        "orbit_count": len(rows),
        "represented_wave_count": sum(multiplicities.values()),
        "fixed_leaf_dimension": sum(r["multiplicity"] * len(r["full_values"]) for r in rows),
        "rows": rows,
    }


def normal_ordering(grid: dict[str, Any], shell: int | None) -> dict[str, Any]:
    waves = set() if shell is None else set(shell_waves(shell))
    selected_count = external_count = 0
    selected_records, external_records = [], []
    largest_norm, largest_projector, smallest_sep = 0.0, 0.0, None
    for row in grid["rows"]:
        selected = row["wave"] in waves
        if selected:
            values = row["selected_values"]
            selected_count += row["multiplicity"] * len(values)
            selected_records.extend((float(abs(v)), row["wave"], complex(v)) for v in values)
            largest_projector = max(largest_projector, row["projector_norm"])
            smallest_sep = (
                row["local_schur_sep"]
                if smallest_sep is None
                else min(smallest_sep, row["local_schur_sep"])
            )
        external = row["external_values"] if selected else row["full_values"]
        external_count += row["multiplicity"] * len(external)
        external_records.extend((float(abs(v)), row["wave"], complex(v)) for v in external)
        largest_norm = max(largest_norm, row["external_norm"] if selected else row["full_norm"])
    slowest_external = max(external_records, key=lambda r: r[0])
    fastest_selected = min(selected_records, key=lambda r: r[0]) if selected_records else None
    gap = None if fastest_selected is None else fastest_selected[0] - slowest_external[0]

    def witness(record: tuple | None) -> dict | None:
        return (
            None
            if record is None
            else {
                "modulus": record[0],
                "wave": list(record[1]),
                "eigenvalue": complex_record(record[2]),
            }
        )

    size = grid["size"]
    coverage = (
        grid["represented_wave_count"] == size**3
        and grid["fixed_leaf_dimension"] == 27 * size**3 - 4
        and selected_count == 4 * len(waves)
        and external_count == 27 * size**3 - 4 - selected_count
    )
    return {
        "size": size,
        "omega": grid["omega"],
        "shell": shell,
        "orbit_count": grid["orbit_count"],
        "represented_wave_count": grid["represented_wave_count"],
        "fixed_leaf_dimension": grid["fixed_leaf_dimension"],
        "selected_dimension": selected_count,
        "external_dimension": external_count,
        "fastest_selected": witness(fastest_selected),
        "slowest_external": witness(slowest_external),
        "normal_modulus_gap": gap,
        "n_squared_gap": None if gap is None else size**2 * gap,
        "maximum_external_one_step_norm": largest_norm,
        "maximum_selected_projector_norm": largest_projector,
        "minimum_selected_local_schur_sep": smallest_sep,
        "coverage_passed": coverage,
        "normal_ordering_prequalified": gap is not None
        and gap > 1e-10
        and slowest_external[0] < 1 - 1e-12
        and all(0 < r[0] < 1 for r in selected_records)
        and largest_projector <= 100
        and smallest_sep >= 0.02,
    }
