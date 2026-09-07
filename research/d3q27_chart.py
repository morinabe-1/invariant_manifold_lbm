"""Real-coordinate quadratic jet for the selected, modified D3Q27 map.

Dense population fibers retain every Fourier-allowed coefficient. No TT
approximation, coordinate removal, or invariant-manifold existence claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations_with_replacement
from typing import Any

import numpy as np
from scipy.linalg import block_diag

from research import d3q27 as d3
from research import d3q27_damping as damping
from research import d3q27_quadratic as q
from research import d3q27_svd_fallback as fallback

SIZE, OMEGA, ETA, POWER = 17, 1.5, 0.02, 2
DIMENSION = 104
WAVES = q.shell_waves(3)
POSITIVE_WAVES = tuple(w for w in WAVES if next(v for v in w if v) > 0)
CONJUGATE_COMPONENT = np.array((0, 1, 3, 2))


def normalized_directions(seed: int, count: int) -> np.ndarray:
    directions = np.random.default_rng(seed).standard_normal((count, DIMENSION))
    return directions / np.linalg.norm(directions, axis=1)[:, None]


def array_metadata(array: np.ndarray) -> dict[str, Any]:
    value = np.ascontiguousarray(array)
    return {
        "shape": list(value.shape),
        "dtype": value.dtype.str,
        "bytes": value.nbytes,
        "sha256": sha256(value.tobytes()).hexdigest(),
    }


def wave_slot(wave: q.Wave, size: int) -> tuple[int, int, int]:
    x, y, z = wave
    return z % size, y % size, x % size


def paired_frames(size: int, omega: float) -> tuple[dict, dict]:
    original, original_audit = q.build_frames(size, omega)
    frames = {}
    source_subspace_error = 0.0
    for wave in POSITIVE_WAVES:
        frame = original[wave]
        frames[wave] = frame
        opposite = tuple(-v for v in wave)
        matched = (frame.blocks[0], frame.blocks[2], frame.blocks[1])
        blocks = tuple(
            q.InputBlock(opposite, label, block.basis.conj(), block.dynamics.conj())
            for label, block in zip(q.LABELS, matched)
        )
        frames[opposite] = q.HydroFrame(
            opposite,
            blocks,
            frame.projector.conj(),
            frame.dual.conj()[CONJUGATE_COMPONENT],
            dict(original[opposite].diagnostics),
        )
        source_subspace_error = max(
            source_subspace_error,
            float(np.linalg.norm(frames[opposite].projector - original[opposite].projector)),
        )
    errors = {"invariance": 0.0, "left_invariance": 0.0, "duality": 0.0, "projector": 0.0}
    for wave, frame in frames.items():
        matrix = d3.fourier_symbol(2 * np.pi * np.asarray(wave) / size, omega)
        dynamics = block_diag(*(b.dynamics for b in frame.blocks))
        errors["invariance"] = max(
            errors["invariance"],
            float(np.linalg.norm(matrix @ frame.basis - frame.basis @ dynamics)),
        )
        errors["left_invariance"] = max(
            errors["left_invariance"],
            float(np.linalg.norm(frame.dual @ matrix - dynamics @ frame.dual)),
        )
        errors["duality"] = max(
            errors["duality"], float(np.linalg.norm(frame.dual @ frame.basis - np.eye(4)))
        )
        errors["projector"] = max(
            errors["projector"], float(np.linalg.norm(frame.basis @ frame.dual - frame.projector))
        )
    return frames, {
        "original_frame_audit": original_audit,
        "paired_frame_errors": errors,
        "source_projector_difference": source_subspace_error,
        "passed": original_audit["passed"]
        and max(errors.values()) <= 5e-12
        and source_subspace_error <= 5e-12,
    }


def realification() -> tuple[np.ndarray, np.ndarray]:
    transform = np.zeros((DIMENSION, DIMENSION), dtype=complex)
    conjugate = np.empty(DIMENSION, dtype=np.int64)
    for index, wave in enumerate(POSITIVE_WAVES):
        positive = 4 * WAVES.index(wave)
        negative = 4 * WAVES.index(tuple(-v for v in wave))
        for component in range(4):
            col = 8 * index + 2 * component
            partner = negative + CONJUGATE_COMPONENT[component]
            transform[positive + component, col : col + 2] = np.array((1, 1j)) / np.sqrt(2)
            transform[partner, col : col + 2] = np.array((1, -1j)) / np.sqrt(2)
            conjugate[positive + component] = partner
            conjugate[partner] = positive + component
    return transform, conjugate


@dataclass(frozen=True)
class PairJet:
    left_indices: np.ndarray
    right_indices: np.ndarray
    wave: q.Wave
    same_block: bool
    hessian: np.ndarray
    forcing: np.ndarray
    reduced: np.ndarray


@dataclass
class QuadraticChart:
    size: int
    omega: float
    eta: float
    power: int
    frames: dict
    transform: np.ndarray
    conjugate_indices: np.ndarray
    complex_linear: np.ndarray
    real_linear: np.ndarray
    input_pairs: np.ndarray
    output_waves: np.ndarray
    hessian_fibers: np.ndarray
    forcing_fibers: np.ndarray
    reduced_fibers: np.ndarray
    reduced_hessian: np.ndarray
    pair_jets: tuple[PairJet, ...]
    construction: dict

    def __post_init__(self) -> None:
        self.base = d3.uniform_equilibrium((self.size,) * 3, np.zeros(4))
        self._flat_outputs = np.array(
            [
                np.ravel_multi_index(wave_slot(tuple(w), self.size), (self.size,) * 3)
                for w in self.output_waves
            ]
        )
        self._sort = np.argsort(self._flat_outputs, kind="stable")
        sorted_outputs = self._flat_outputs[self._sort]
        self._starts = np.r_[0, np.flatnonzero(np.diff(sorted_outputs)) + 1]
        self._unique_outputs = sorted_outputs[self._starts]
        self._hessian_sorted = self.hessian_fibers[self._sort]
        self._forcing_sorted = self.forcing_fibers[self._sort]

    def coordinates(self, value: np.ndarray) -> np.ndarray:
        a = d3._real_array(value)
        if a.shape != (DIMENSION,):
            raise ValueError("104 real coordinates are required")
        return a

    def complex_coordinates(self, value: np.ndarray) -> np.ndarray:
        return self.transform @ self.coordinates(value)

    def linear_fourier(self, value: np.ndarray) -> np.ndarray:
        z = self.complex_coordinates(value)
        spectrum = np.zeros((self.size,) * 3 + (27,), dtype=complex)
        for index, wave in enumerate(WAVES):
            spectrum[wave_slot(wave, self.size)] = (
                self.frames[wave].basis @ z[4 * index : 4 * index + 4]
            )
        return spectrum

    def quadratic_fourier(self, value: np.ndarray, *, forcing: bool = False) -> np.ndarray:
        z = self.complex_coordinates(value)
        monomials = z[self.input_pairs[:, 0]] * z[self.input_pairs[:, 1]]
        fibers = self._forcing_sorted if forcing else self._hessian_sorted
        contracted = np.add.reduceat(fibers * monomials[self._sort, None], self._starts, axis=0)
        spectrum = np.zeros((self.size**3, 27), dtype=complex)
        spectrum[self._unique_outputs] = contracted
        return spectrum.reshape((self.size,) * 3 + (27,))

    def physical(self, spectrum: np.ndarray) -> np.ndarray:
        field = np.fft.ifftn(spectrum, axes=(0, 1, 2), norm="ortho")
        if np.linalg.norm(field.imag) > 1e-9 * max(1, np.linalg.norm(field.real)):
            raise ValueError("conjugate Fourier data did not reconstruct a real field")
        return field.real

    def linear_field(self, value: np.ndarray) -> np.ndarray:
        return self.physical(self.linear_fourier(value))

    def quadratic_field(self, value: np.ndarray) -> np.ndarray:
        """The Taylor contribution 1/2 H[a,a], not H[a,a]."""
        return self.physical(self.quadratic_fourier(value))

    def embed(self, value: np.ndarray, *, quadratic: bool = True) -> np.ndarray:
        spectrum = self.linear_fourier(value)
        if quadratic:
            spectrum += self.quadratic_fourier(value)
        return self.base + self.physical(spectrum)

    def reduced(self, value: np.ndarray, *, quadratic: bool = True) -> np.ndarray:
        a = self.coordinates(value)
        result = self.real_linear @ a
        if quadratic:
            result += 0.5 * np.einsum("ijk,j,k->i", self.reduced_hessian, a, a, optimize=True)
        return result

    def reduced_quadratic_fourier(self, value: np.ndarray) -> np.ndarray:
        z = self.complex_coordinates(value)
        monomials = z[self.input_pairs[:, 0]] * z[self.input_pairs[:, 1]]
        result = np.zeros(DIMENSION, dtype=complex)
        for index, wave in enumerate(WAVES):
            selected = np.all(self.output_waves == wave, axis=1)
            result[4 * index : 4 * index + 4] = monomials[selected] @ self.reduced_fibers[selected]
        return result

    def project(self, perturbation: np.ndarray) -> np.ndarray:
        field = d3._state(perturbation)
        if field.shape != self.base.shape:
            raise ValueError("projection grid does not match the chart")
        spectrum = np.fft.fftn(field, axes=(0, 1, 2), norm="ortho")
        z = np.concatenate([self.frames[w].dual @ spectrum[wave_slot(w, self.size)] for w in WAVES])
        a = self.transform.conj().T @ z
        if np.linalg.norm(a.imag) > 1e-9 * max(1, np.linalg.norm(a.real)):
            raise ValueError("projection failed real-coordinate consistency")
        return a.real

    def pair_loop(self, value: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        z = self.complex_coordinates(value)
        h = np.zeros_like(self.linear_fourier(value))
        b, g = np.zeros_like(h), np.zeros(DIMENSION, dtype=complex)
        for pair in self.pair_jets:
            product = np.kron(z[pair.right_indices], z[pair.left_indices])
            if pair.same_block:
                product = 0.5 * q.symmetric_square_basis(len(pair.left_indices)).T @ product
            slot = wave_slot(pair.wave, self.size)
            h[slot] += pair.hessian @ product
            b[slot] += pair.forcing @ product
            if pair.wave in WAVES:
                index = WAVES.index(pair.wave)
                g[4 * index : 4 * index + 4] += pair.reduced @ product
        return h, b, g

    def rotation_action(self, rotation: np.ndarray) -> np.ndarray:
        p = d3.population_permutation(rotation)
        action = np.zeros((DIMENSION, DIMENSION), dtype=complex)
        for index, wave in enumerate(WAVES):
            target = tuple(int(v) for v in rotation @ wave)
            target_index = WAVES.index(target)
            action[4 * target_index : 4 * target_index + 4, 4 * index : 4 * index + 4] = (
                self.frames[target].dual @ p @ self.frames[wave].basis
            )
        real = self.transform.conj().T @ action @ self.transform
        if np.linalg.norm(real.imag) > 5e-12:
            raise ValueError("cubic action is not real")
        return real.real

    def archive_arrays(self) -> dict[str, np.ndarray]:
        return {
            "waves": np.asarray(WAVES, dtype=np.int64),
            "input_pairs": self.input_pairs,
            "output_waves": self.output_waves,
            "transform": self.transform,
            "complex_linear": self.complex_linear,
            "real_linear": self.real_linear,
            "hessian_taylor_fibers": self.hessian_fibers,
            "forcing_taylor_fibers": self.forcing_fibers,
            "reduced_taylor_fibers": self.reduced_fibers,
            "reduced_real_hessian": self.reduced_hessian,
            "frame_bases": np.stack([self.frames[w].basis for w in WAVES]),
            "frame_duals": np.stack([self.frames[w].dual for w in WAVES]),
        }


def build_chart(
    size: int = SIZE, omega: float = OMEGA, eta: float = ETA, power: int = POWER
) -> QuadraticChart:
    size = q.odd_size(size)
    damping.parameters(eta, power)
    frames, frame_audit = paired_frames(size, omega)
    transform, conjugate = realification()
    blocks = [b for wave in WAVES for b in frames[wave].blocks]
    offsets, offset = {}, 0
    for block in blocks:
        offsets[block.key] = np.arange(offset, offset + block.dimension)
        offset += block.dimension
    dynamics = block_diag(
        *(damping.wave_multiplier(b.wave, size, eta, power) * b.dynamics for b in blocks)
    )
    real_linear_complex = transform.conj().T @ dynamics @ transform
    records, pair_jets, inputs_list, waves_list, hs, bs, gs = [], [], [], [], [], [], []
    sectors = {}
    for left, right in combinations_with_replacement(blocks, 2):
        wave = q.canonical_wave(tuple(a + b for a, b in zip(left.wave, right.wave)), size)
        if wave not in sectors:
            sectors[wave] = q.external_sector(wave, size, omega, frames.get(wave))
        sector = sectors[wave]
        ml = damping.wave_multiplier(left.wave, size, eta, power)
        mr = damping.wave_multiplier(right.wave, size, eta, power)
        mo = damping.wave_multiplier(wave, size, eta, power)
        scaled_left = q.InputBlock(left.wave, left.label, left.basis, ml * left.dynamics)
        scaled_right = q.InputBlock(right.wave, right.label, right.basis, mr * right.dynamics)
        product, forcing, product_error = q.product_forcing(
            scaled_left, scaled_right, wave, size, omega * mo
        )
        external_forcing = sector.basis.conj().T @ sector.projection @ forcing
        solution, solve, backend = fallback.solve_with_fallback(
            mo * sector.dynamics, product, external_forcing
        )
        hessian = sector.basis @ solution
        reduced = (
            frames[wave].dual @ forcing
            if wave in frames
            else np.zeros((4, forcing.shape[1]), dtype=complex)
        )
        scale = max(1, float(np.linalg.norm(hessian)))
        gauge = float(np.linalg.norm(sector.selected_projector @ hessian) / scale)
        mean = (
            float(np.linalg.norm(d3.conserved_moment_matrix() @ hessian) / scale)
            if wave == (0, 0, 0)
            else 0.0
        )
        full_symbol = damping.fourier_symbol(2 * np.pi * np.asarray(wave) / size, omega, eta, power)
        selected_term = frames[wave].basis @ reduced if wave in frames else np.zeros_like(forcing)
        full_residual = float(
            np.linalg.norm(full_symbol @ hessian - hessian @ product + forcing - selected_term)
            / max(1e-14, np.linalg.norm(forcing))
        )
        record = {
            "left_wave": list(left.wave),
            "left_label": left.label,
            "right_wave": list(right.wave),
            "right_label": right.label,
            "output_wave": list(wave),
            "product_dimension": len(product),
            **solve,
            "backend": backend,
            "graph_gauge_error": gauge,
            "zero_wave_moment_error": mean,
            "full_homological_relative_residual": full_residual,
            "structural_error": max(gauge, mean, product_error, sector.structural_error),
            "passed": solve["passed"]
            and backend["passed"]
            and max(gauge, mean, product_error, sector.structural_error) <= 5e-12
            and full_residual <= 1e-9,
        }
        records.append(record)
        hessian, forcing, reduced = hessian / size**1.5, forcing / size**1.5, reduced / size**1.5
        li, ri = offsets[left.key], offsets[right.key]
        same = left.key == right.key
        pair_jets.append(PairJet(li, ri, wave, same, hessian, forcing, reduced))
        if same:
            component_pairs = list(combinations_with_replacement(range(left.dimension), 2))
            factors = np.array([0.5 if i == j else 1 / np.sqrt(2) for i, j in component_pairs])
            indices = [(li[i], ri[j]) for i, j in component_pairs]
        else:
            indices = [(i, j) for j in ri for i in li]
            factors = np.ones(len(indices))
        inputs_list.extend(indices)
        waves_list.extend([wave] * len(indices))
        hs.extend((hessian * factors).T)
        bs.extend((forcing * factors).T)
        gs.extend((reduced * factors).T)
    input_pairs = np.asarray(inputs_list, dtype=np.int64)
    output_waves = np.asarray(waves_list, dtype=np.int64)
    h, b, g = np.asarray(hs), np.asarray(bs), np.asarray(gs)
    complex_g = np.zeros((DIMENSION, DIMENSION, DIMENSION), dtype=complex)
    for column, ((i, j), wave) in enumerate(zip(input_pairs, map(tuple, output_waves))):
        if wave in WAVES:
            index = 4 * WAVES.index(wave)
            complex_g[index : index + 4, i, j] = g[column] * (2 if i == j else 1)
            if i != j:
                complex_g[index : index + 4, j, i] = g[column]
    real_g_complex = np.einsum(
        "ri,ijk,ja,kb->rab", transform.conj().T, complex_g, transform, transform, optimize=True
    )
    lookup = {tuple(pair): index for index, pair in enumerate(input_pairs)}
    conjugate_columns = np.array(
        [lookup[tuple(sorted((conjugate[i], conjugate[j])))] for i, j in input_pairs]
    )
    h_conjugacy = damping.relative_error(h[conjugate_columns], h.conj())
    b_conjugacy = damping.relative_error(b[conjugate_columns], b.conj())
    g_conjugacy = damping.relative_error(g[conjugate_columns][:, CONJUGATE_COMPONENT], g.conj())
    g_imag = float(
        np.linalg.norm(real_g_complex.imag) / max(1e-14, np.linalg.norm(real_g_complex.real))
    )
    zero = np.all(output_waves == 0, axis=1)
    zero_norm = float(np.linalg.norm(h[zero]))
    zero_moment = float(
        np.linalg.norm(h[zero] @ d3.conserved_moment_matrix().T) / max(1, zero_norm)
    )
    coverage = (
        len(records) == 3081
        and len(input_pairs) == 5460
        and len(lookup) == 5460
        and set(lookup) == set(combinations_with_replacement(range(104), 2))
    )
    construction = {
        "frame_audit": frame_audit,
        "pair_records": records,
        "pair_count": len(records),
        "product_dimension_sum": len(input_pairs),
        "real_coordinate_count": DIMENSION,
        "realification_unitarity_error": float(
            np.linalg.norm(transform.conj().T @ transform - np.eye(DIMENSION))
        ),
        "real_linear_imaginary_error": float(np.linalg.norm(real_linear_complex.imag)),
        "hessian_conjugacy_relative_error": h_conjugacy,
        "forcing_conjugacy_relative_error": b_conjugacy,
        "reduced_conjugacy_relative_error": g_conjugacy,
        "real_hessian_imaginary_relative_error": g_imag,
        "real_hessian_symmetry_error": damping.relative_error(
            real_g_complex, real_g_complex.swapaxes(1, 2)
        ),
        "reduced_hessian_frobenius_norm": float(np.linalg.norm(real_g_complex.real)),
        "zero_wave_kinetic_norm": zero_norm,
        "zero_wave_moment_error": zero_moment,
        "coverage_passed": coverage,
        "coefficient_passed": all(r["passed"] for r in records),
    }
    return QuadraticChart(
        size,
        omega,
        eta,
        power,
        frames,
        transform,
        conjugate,
        dynamics,
        real_linear_complex.real,
        input_pairs,
        output_waves,
        h,
        b,
        g,
        real_g_complex.real,
        tuple(pair_jets),
        construction,
    )
