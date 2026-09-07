"""Cluster-preserving cubic preflight; all 104 coordinates and Fourier fibers."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from functools import cache
from itertools import combinations_with_replacement, product
from math import factorial

import numpy as np

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import d3q27_damping as damping
from research import d3q27_negative_control as degree
from research import d3q27_quadratic as q
from research import d3q27_svd_fallback as fallback

SIZES = (17, 33, 65)
BLOCK_TRIPLES = tuple(combinations_with_replacement(range(78), 3))
TRIPLE_COUNT, COLUMN_COUNT = 82160, 192920
DIRECTION_SEED, REPLAY_SEED = 2026090719, 2026090720
REPLAY_ORDINALS = tuple(
    sorted(
        [0, TRIPLE_COUNT - 1]
        + np.random.default_rng(REPLAY_SEED)
        .choice(np.arange(1, TRIPLE_COUNT - 1), 14, replace=False)
        .tolist()
    )
)


@cache
def symmetric_product(
    groups: tuple, dimensions: tuple
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Orthonormal repeated-block product, canonical local triples, Taylor factors.

    Full products have first index fastest. Forcing is a raw third derivative;
    returned factors convert its S-restricted columns into Taylor monomials.
    """
    if len(groups) != 3 or len(dimensions) != 3 or any(d < 1 for d in dimensions):
        raise ValueError("three positive dimensions and three group labels required")
    positions = [[i for i, g in enumerate(groups) if g == label] for label in dict.fromkeys(groups)]
    if any(len({dimensions[i] for i in slots}) != 1 for slots in positions):
        raise ValueError("repeated blocks must have the same dimension")
    full = [
        (i, j, k)
        for k, j, i in product(range(dimensions[2]), range(dimensions[1]), range(dimensions[0]))
    ]
    lookup, columns, representatives = {}, [], []
    for row, values in enumerate(full):
        canonical = list(values)
        for slots in positions:
            for slot, value in zip(slots, sorted(values[i] for i in slots), strict=True):
                canonical[slot] = value
        key = tuple(canonical)
        if key not in lookup:
            lookup[key] = len(columns)
            representatives.append(key)
            columns.append([])
        columns[lookup[key]].append(row)
    basis = np.zeros((len(full), len(columns)))
    multiplicities = np.array([len(rows) for rows in columns])
    for col, rows in enumerate(columns):
        basis[rows, col] = 1 / np.sqrt(len(rows))
    denominator = np.prod([factorial(len(slots)) for slots in positions])
    return basis, np.asarray(representatives, dtype=np.int64), np.sqrt(multiplicities) / denominator


@dataclass
class CubicContext:
    model: chart.QuadraticChart
    blocks: tuple
    indices: tuple
    linear_moments: np.ndarray
    hessian_moments: np.ndarray
    linear_cj: np.ndarray
    hessian_cj: np.ndarray
    equilibrium_vv: np.ndarray
    hessian_linear_input: np.ndarray
    reduced_pairs: np.ndarray
    sectors: dict


def build_context(model: chart.QuadraticChart) -> CubicContext:
    blocks = tuple(b for wave in chart.WAVES for b in model.frames[wave].blocks)
    offset, indices = 0, []
    for block in blocks:
        indices.append(np.arange(offset, offset + block.dimension))
        offset += block.dimension
    v = np.column_stack([model.frames[w].basis for w in chart.WAVES]).T
    raw_h = np.zeros((104, 104, 27), dtype=complex)
    raw_g = np.zeros((104, 104, 4), dtype=complex)
    for column, (i, j) in enumerate(model.input_pairs):
        factor = 2 if i == j else 1
        raw_h[i, j] = raw_h[j, i] = factor * model.hessian_fibers[column]
        raw_g[i, j] = raw_g[j, i] = factor * model.reduced_fibers[column]
    mv = v @ d3.conserved_moment_matrix().T
    mh = raw_h @ d3.conserved_moment_matrix().T
    cv, ch = mv[:, 1:] @ d3.VELOCITIES.T, mh[..., 1:] @ d3.VELOCITIES.T
    vv = d3.WEIGHTS * (
        9 * cv[:, None] * cv[None, :] - 3 * np.einsum("ia,ja->ij", mv[:, 1:], mv[:, 1:])[..., None]
    )
    hl = np.einsum("pi,pjq->ijq", model.complex_linear, raw_h, optimize=True)
    return CubicContext(model, blocks, tuple(indices), mv, mh, cv, ch, vv, hl, raw_g, {})


def composition_term(
    context: CubicContext, i: np.ndarray, j: np.ndarray, k: np.ndarray, pair_wave: tuple
) -> np.ndarray:
    if pair_wave not in chart.WAVES:
        return np.zeros((len(i), 27), dtype=complex)
    output = 4 * chart.WAVES.index(pair_wave) + np.arange(4)
    return np.einsum(
        "cpq,cp->cq",
        context.hessian_linear_input[i[:, None], output[None, :]],
        context.reduced_pairs[j, k],
    )


def raw_forcing(context: CubicContext, block_ids: tuple, wave: tuple) -> np.ndarray:
    """Unrestricted raw third derivative with first input index fastest."""
    li, mi, ri = (context.indices[b] for b in block_ids)
    i = np.tile(li, len(mi) * len(ri))
    j = np.tile(np.repeat(mi, len(li)), len(ri))
    k = np.repeat(ri, len(li) * len(mi))
    first, second = context.linear_moments, context.hessian_moments
    nonlinear = np.zeros((len(i), 27), dtype=complex)
    cubic = np.zeros_like(nonlinear)
    composition = np.zeros_like(nonlinear)
    for x, y, z, pair in (
        (i, j, k, (block_ids[1], block_ids[2])),
        (j, i, k, (block_ids[0], block_ids[2])),
        (k, i, j, (block_ids[0], block_ids[1])),
    ):
        nonlinear += d3.WEIGHTS * (
            9 * context.linear_cj[x] * context.hessian_cj[y, z]
            - 3 * np.sum(first[x, 1:] * second[y, z, 1:], axis=-1)[:, None]
        )
        cubic -= first[x, :1] * context.equilibrium_vv[y, z]
        pair_wave = tuple(
            a + b
            for a, b in zip(context.blocks[pair[0]].wave, context.blocks[pair[1]].wave, strict=True)
        )
        composition += composition_term(context, x, y, z, pair_wave)
    model = context.model
    phase = np.exp(-2j * np.pi * (d3.VELOCITIES @ np.asarray(wave)) / model.size)
    scale = model.omega * damping.wave_multiplier(wave, model.size, model.eta, model.power)
    return (scale * phase * (nonlinear / model.size**1.5 + cubic / model.size**3) - composition).T


@dataclass
class TripleJet:
    input_triples: np.ndarray
    wave: tuple
    factors: np.ndarray
    forcing: np.ndarray
    response: np.ndarray
    reduced: np.ndarray
    record: dict


def solve_triple(context: CubicContext, ordinal: int) -> TripleJet:
    if not isinstance(ordinal, int) or isinstance(ordinal, bool) or not 0 <= ordinal < TRIPLE_COUNT:
        raise ValueError("ordinal must identify one of the 82160 registered triples")
    ids = BLOCK_TRIPLES[ordinal]
    blocks = [context.blocks[b] for b in ids]
    groups = tuple(ids.index(b) for b in ids)
    symmetric, local_triples, factors = symmetric_product(
        groups, tuple(b.dimension for b in blocks)
    )
    full_input = np.kron(blocks[2].dynamics, np.kron(blocks[1].dynamics, blocks[0].dynamics))
    model = context.model
    full_input *= np.prod(
        [damping.wave_multiplier(b.wave, model.size, model.eta, model.power) for b in blocks]
    )
    inputs = symmetric.T @ full_input @ symmetric
    product_error = float(np.linalg.norm(full_input @ symmetric - symmetric @ inputs))
    wave = q.canonical_wave(
        tuple(sum(b.wave[axis] for b in blocks) for axis in range(3)), model.size
    )
    if wave not in context.sectors:
        context.sectors[wave] = q.external_sector(
            wave, model.size, model.omega, model.frames.get(wave)
        )
    sector = context.sectors[wave]
    mo = damping.wave_multiplier(wave, model.size, model.eta, model.power)
    forcing = raw_forcing(context, ids, wave) @ symmetric
    output = mo * sector.dynamics
    external_forcing = sector.basis.conj().T @ sector.projection @ forcing
    solution, solve, backend = fallback.solve_with_fallback(output, inputs, external_forcing)
    response = sector.basis @ solution
    frame = model.frames.get(wave)
    reduced = (
        frame.dual @ forcing if frame is not None else np.zeros((4, len(inputs)), dtype=complex)
    )
    selected = frame.basis @ reduced if frame is not None else np.zeros_like(forcing)
    matrix = damping.fourier_symbol(
        2 * np.pi * np.asarray(wave) / model.size, model.omega, model.eta, model.power
    )
    full_residual = float(
        np.linalg.norm(matrix @ response - response @ inputs + forcing - selected)
        / max(1e-14, np.linalg.norm(forcing))
    )
    gauge = float(
        np.linalg.norm(sector.selected_projector @ response) / max(1, np.linalg.norm(response))
    )
    zero_h = (
        float(
            np.linalg.norm(d3.conserved_moment_matrix() @ response)
            / max(1, np.linalg.norm(response))
        )
        if wave == (0, 0, 0)
        else 0.0
    )
    zero_f = (
        float(
            np.linalg.norm(d3.conserved_moment_matrix() @ forcing) / max(1, np.linalg.norm(forcing))
        )
        if wave == (0, 0, 0)
        else 0.0
    )
    structural = max(product_error, sector.structural_error, gauge, zero_h, zero_f)
    triples = np.column_stack(
        [context.indices[ids[axis]][local_triples[:, axis]] for axis in range(3)]
    )
    record = {
        "ordinal": ordinal,
        "block_ordinals": list(ids),
        "input_waves": [list(b.wave) for b in blocks],
        "input_labels": [b.label for b in blocks],
        "output_wave": list(wave),
        "product_dimension": len(inputs),
        "external_dimension": len(output),
        **solve,
        "response_normalization": "raw derivative, orthonormal-Fourier global l2",
        "backend": backend,
        "internal_forcing_norm": float(np.linalg.norm(reduced)),
        "symmetric_product_error": product_error,
        "graph_gauge_error": gauge,
        "zero_wave_response_moment_error": zero_h,
        "zero_wave_forcing_moment_error": zero_f,
        "structural_error": structural,
        "full_homological_relative_residual": full_residual,
        "passed": solve["passed"]
        and backend["passed"]
        and structural <= 5e-12
        and full_residual <= 1e-9,
    }
    if ordinal in REPLAY_ORDINALS:
        record["array_hashes"] = {
            name: chart.array_metadata(value)
            for name, value in (
                ("external_dynamics", output),
                ("input_dynamics", inputs),
                ("forcing", forcing),
                ("external_forcing", external_forcing),
                ("response", response),
                ("reduced", reduced),
            )
        }
    return TripleJet(triples, wave, factors, forcing, response, reduced, record)


def summarize_records(records: list[dict]) -> dict:
    numeric = [r for r in records if "execution_error" not in r]
    conditioned = [r for r in numeric if r["condition_number"] is not None]
    extreme = lambda key, kind: None if not numeric else kind(numeric, key=lambda r: r[key])
    return {
        "record_count": len(records),
        "completed_count": len(numeric),
        "product_dimension_sum": sum(r["product_dimension"] for r in numeric),
        "status_counts": dict(sorted(Counter(r["status"] for r in numeric).items())),
        "failed_count": sum(not r["passed"] for r in numeric),
        "fallback_count": sum(r["backend"]["fallback"] for r in numeric),
        "first_failure": next((r for r in records if not r.get("passed", False)), None),
        "worst_condition": max(conditioned, key=lambda r: r["condition_number"])
        if conditioned
        else None,
        "smallest_singular": extreme("smallest_singular_value", min),
        "largest_response": extreme("response_local_norm", max),
        "worst_residual": extreme("solve_relative_residual", max),
        "maximum_full_residual": max(
            (r["full_homological_relative_residual"] for r in numeric), default=0.0
        ),
        "maximum_structural_error": max((r["structural_error"] for r in numeric), default=0.0),
        "coverage_passed": len(numeric) == TRIPLE_COUNT
        and [r["ordinal"] for r in numeric] == list(range(TRIPLE_COUNT))
        and sum(r["product_dimension"] for r in numeric) == COLUMN_COUNT,
        "all_solves_passed": len(numeric) == TRIPLE_COUNT and all(r["passed"] for r in numeric),
    }


def conjugacy_audit(
    model: chart.QuadraticChart, triples: np.ndarray, waves: np.ndarray, fields: dict
) -> dict:
    ids = np.ravel_multi_index(triples.T, (104, 104, 104))
    lookup = np.full(104**3, -1, dtype=np.int64)
    lookup[ids] = np.arange(len(ids))
    opposite = np.sort(model.conjugate_indices[triples], axis=1)
    partners = lookup[np.ravel_multi_index(opposite.T, (104, 104, 104))]
    coverage = (
        len(ids) == COLUMN_COUNT
        and len(np.unique(ids)) == COLUMN_COUNT
        and np.all(triples[:, :-1] <= triples[:, 1:])
        and np.all(partners >= 0)
    )
    errors = {}
    for name, values in fields.items():
        moved = values[partners]
        if name == "reduced":
            moved = moved[:, chart.CONJUGATE_COMPONENT]
        error = np.linalg.norm(moved - values.conj(), axis=1) / np.maximum(
            1, np.linalg.norm(values, axis=1)
        )
        worst = int(np.argmax(error))
        errors[name] = {
            "maximum_scaled_error": float(error[worst]),
            "worst_monomial": triples[worst].tolist(),
            "partner": triples[partners[worst]].tolist(),
            "passed": bool(np.all(error <= 1e-8)),
        }
    wave_match = bool(np.array_equal(waves[partners], -waves))
    return {
        "coverage": bool(coverage),
        "opposite_output_waves": wave_match,
        "fields": errors,
        "passed": bool(coverage) and wave_match and all(r["passed"] for r in errors.values()),
    }


def contract_fourier(
    model: chart.QuadraticChart,
    triples: np.ndarray,
    waves: np.ndarray,
    fibers: np.ndarray,
    u: np.ndarray,
) -> np.ndarray:
    z = model.complex_coordinates(u)
    slots = np.array(
        [
            np.ravel_multi_index(chart.wave_slot(tuple(w), model.size), (model.size,) * 3)
            for w in waves
        ]
    )
    order = np.argsort(slots, kind="stable")
    starts = np.r_[0, np.flatnonzero(np.diff(slots[order])) + 1]
    monomials = np.prod(z[triples], axis=1)
    spectrum = np.zeros((model.size**3, 27), dtype=complex)
    spectrum[slots[order[starts]]] = np.add.reduceat(
        fibers[order] * monomials[order, None], starts, axis=0
    )
    return np.fft.ifftn(spectrum.reshape(model.base.shape), axes=(0, 1, 2), norm="ortho")


def direct_physical_forcing(model: chart.QuadraticChart, u: np.ndarray) -> np.ndarray:
    v, h = model.linear_field(u), model.quadratic_field(u)
    mv = np.einsum("aq,...q->...a", d3.conserved_moment_matrix(), v)
    bilinear = damping.mixed_hessian(v, h, model.omega)
    third = d3.stream_periodic(
        -model.omega * mv[..., :1] * degree.momentum_quadratic(mv[..., 1:], mv[..., 1:])
    )
    nonlinear = damping.apply_filter(bilinear + third, model.eta, model.power)
    l = model.real_linear @ u
    g = 0.5 * np.einsum("ijk,j,k->i", model.reduced_hessian, u, u, optimize=True)
    composition = model.quadratic_field(l + g) - model.quadratic_field(l) - model.quadratic_field(g)
    return nonlinear - composition


def directional_audit(
    model: chart.QuadraticChart,
    triples: np.ndarray,
    waves: np.ndarray,
    forcing: np.ndarray,
    progress=None,
) -> dict:
    directions = chart.normalized_directions(DIRECTION_SEED, 8)
    records = []
    for index, u in enumerate(directions):
        contracted = contract_fourier(model, triples, waves, forcing, u)
        direct = direct_physical_forcing(model, u)
        error = damping.relative_error(contracted, direct)
        row = {
            "direction_index": index,
            "direct_norm": float(np.linalg.norm(direct)),
            "contracted_norm": float(np.linalg.norm(contracted)),
            "relative_error": error,
            "imaginary_norm": float(np.linalg.norm(contracted.imag)),
            "passed": error <= 1e-8,
        }
        records.append(row)
        if progress is not None:
            progress({"phase": "independent_cubic_forcing", "size": model.size, **row})
    return {
        "seed": DIRECTION_SEED,
        "directions": directions.tolist(),
        "records": records,
        "passed": len(records) == 8 and all(r["passed"] for r in records),
    }
