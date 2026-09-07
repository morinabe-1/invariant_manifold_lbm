"""Q012f1 diagnostic inputs and mixed-precision solves; frozen predecessors stay intact."""

from __future__ import annotations

from dataclasses import replace
from itertools import combinations_with_replacement

import gmpy2 as mp
import numpy as np
from scipy.linalg import solve_sylvester

from research import d3q27 as d3
from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_damping as damping
from research import d3q27_quadratic as q
from research import d3q27_svd_fallback as fallback
from research import q012a_d3q27_foundation as q012a

INPUTS, SOLVERS = ("raw", "paired"), ("svd", "sylvester", "refined")
BLOCK_OFFSETS = np.r_[0, np.cumsum([2, 1, 1] * 26)]
COORDINATE_BLOCK = np.repeat(np.arange(78), [2, 1, 1] * 26)
TRIPLE_LOOKUP = {ids: ordinal for ordinal, ids in enumerate(cubic.BLOCK_TRIPLES)}


def conjugate_ordinal(ordinal: int) -> int:
    blocks = []
    for b in cubic.BLOCK_TRIPLES[ordinal]:
        wave = chart.WAVES[b // 3]
        opposite = tuple(-k for k in wave)
        blocks.append(3 * chart.WAVES.index(opposite) + (0, 2, 1)[b % 3])
    return TRIPLE_LOOKUP[tuple(sorted(blocks))]


def selection(prior: dict, failed_records: list[dict]) -> dict:
    reasons: dict[int, set[str]] = {}

    def add(ordinal, reason):
        reasons.setdefault(int(ordinal), set()).add(reason)

    for row in failed_records:
        if not row["passed"]:
            add(row["ordinal"], "prior_n65_residual_failure")
    for ordinal in cubic.REPLAY_ORDINALS:
        add(ordinal, "registered_success_and_replay_control")
    for grid in prior["cycle"]["grids"]:
        for name, data in grid["conjugacy"]["fields"].items():
            ids = tuple(sorted(COORDINATE_BLOCK[data["worst_monomial"]].tolist()))
            add(TRIPLE_LOOKUP[ids], f"prior_n{grid['size']}_{name}_conjugacy_worst")
    for ordinal in list(reasons):
        add(conjugate_ordinal(ordinal), f"conjugate_of_{ordinal}")
    replay = sorted(
        set(cubic.REPLAY_ORDINALS) | {conjugate_ordinal(o) for o in cubic.REPLAY_ORDINALS}
    )
    result = {
        "records": [{"ordinal": o, "reasons": sorted(reasons[o])} for o in sorted(reasons)],
        "ordinals": sorted(reasons),
        "replay_ordinals": replay,
        "original_failure_ordinals": sorted(
            r["ordinal"] for r in failed_records if not r["passed"]
        ),
    }
    result["digest_sha256"] = q012a._digest(result)
    return result


def pair_partners(model: chart.QuadraticChart) -> np.ndarray:
    lookup = {tuple(pair): i for i, pair in enumerate(model.input_pairs)}
    return np.array(
        [lookup[tuple(sorted(model.conjugate_indices[pair]))] for pair in model.input_pairs]
    )


def pair_projection(values: np.ndarray, partners: np.ndarray, reduced=False) -> np.ndarray:
    opposite = values[partners].conj()
    if reduced:
        opposite = opposite[:, chart.CONJUGATE_COMPONENT]
    return (values + opposite) * 0.5


def real_reduced(model: chart.QuadraticChart, fibers: np.ndarray) -> tuple[np.ndarray, float]:
    tensor = np.zeros((104, 104, 104), dtype=complex)
    for column, ((i, j), wave) in enumerate(zip(model.input_pairs, map(tuple, model.output_waves))):
        if wave in chart.WAVES:
            start = 4 * chart.WAVES.index(wave)
            tensor[start : start + 4, i, j] = fibers[column] * (2 if i == j else 1)
            if i != j:
                tensor[start : start + 4, j, i] = fibers[column]
    transformed = np.einsum(
        "ri,ijk,ja,kb->rab",
        model.transform.conj().T,
        tensor,
        model.transform,
        model.transform,
        optimize=True,
    )
    return transformed.real, float(np.linalg.norm(transformed.imag))


def paired_input(model: chart.QuadraticChart) -> tuple[chart.QuadraticChart, dict]:
    before = {k: chart.array_metadata(v) for k, v in model.archive_arrays().items()}
    partners = pair_partners(model)
    h = pair_projection(model.hessian_fibers, partners)
    g = pair_projection(model.reduced_fibers, partners, True)
    real_g, imaginary = real_reduced(model, g)
    jets, offset = [], 0
    for old in model.pair_jets:
        if old.same_block:
            pairs = list(combinations_with_replacement(range(len(old.left_indices)), 2))
            factors = np.array([0.5 if i == j else 1 / np.sqrt(2) for i, j in pairs])
        else:
            factors = np.ones(len(old.left_indices) * len(old.right_indices))
        stop = offset + len(factors)
        jets.append(
            replace(
                old,
                hessian=(h[offset:stop] / factors[:, None]).T,
                reduced=(g[offset:stop] / factors[:, None]).T,
            )
        )
        offset = stop
    paired = replace(
        model,
        hessian_fibers=h,
        reduced_fibers=g,
        reduced_hessian=real_g,
        pair_jets=tuple(jets),
        construction={"kind": "Q012f1 paired diagnostic input"},
    )
    checks = {
        "partner_involution": np.array_equal(partners[partners], np.arange(len(partners))),
        "wave_reversal": np.array_equal(model.output_waves[partners], -model.output_waves),
        "h_idempotence": np.array_equal(pair_projection(h, partners), h),
        "g_idempotence": np.array_equal(pair_projection(g, partners, True), g),
        "complete_pair_jets": offset == 5460 and len(jets) == 3081,
        "original_unmodified": before
        == {k: chart.array_metadata(v) for k, v in model.archive_arrays().items()},
    }
    return paired, {
        "checks": {k: bool(v) for k, v in checks.items()},
        "passed": all(checks.values()),
        "h_change_relative": damping.relative_error(h, model.hessian_fibers),
        "g_change_relative": damping.relative_error(g, model.reduced_fibers),
        "real_g_imaginary_norm": imaginary,
        "arrays": {k: chart.array_metadata(v) for k, v in paired.archive_arrays().items()},
    }


def quadratic_audit(model: chart.QuadraticChart) -> dict:
    blocks = tuple(b for wave in chart.WAVES for b in model.frames[wave].blocks)
    records, sectors = [], {}
    for ordinal, ((left, right), jet) in enumerate(
        zip(combinations_with_replacement(blocks, 2), model.pair_jets)
    ):
        wave = jet.wave
        if wave not in sectors:
            sectors[wave] = q.external_sector(wave, model.size, model.omega, model.frames.get(wave))
        sector = sectors[wave]
        ml, mr, mo = [
            damping.wave_multiplier(w, model.size, model.eta, model.power)
            for w in (left.wave, right.wave, wave)
        ]
        inputs, forcing, product_error = q.product_forcing(
            q.InputBlock(left.wave, left.label, left.basis, ml * left.dynamics),
            q.InputBlock(right.wave, right.label, right.basis, mr * right.dynamics),
            wave,
            model.size,
            model.omega * mo,
        )
        forcing /= model.size**1.5
        external = sector.basis.conj().T @ sector.projection @ forcing
        x = sector.basis.conj().T @ jet.hessian
        residual = float(
            np.linalg.norm(mo * sector.dynamics @ x - x @ inputs + external)
            / max(1e-14, np.linalg.norm(external))
        )
        selected = (
            model.frames[wave].basis @ jet.reduced
            if wave in model.frames
            else np.zeros_like(forcing)
        )
        matrix = damping.fourier_symbol(
            2 * np.pi * np.asarray(wave) / model.size, model.omega, model.eta, model.power
        )
        full = float(
            np.linalg.norm(matrix @ jet.hessian - jet.hessian @ inputs + forcing - selected)
            / max(1e-14, np.linalg.norm(forcing))
        )
        gauge = float(
            np.linalg.norm(sector.selected_projector @ jet.hessian)
            / max(1, np.linalg.norm(jet.hessian))
        )
        mean = (
            float(
                np.linalg.norm(d3.conserved_moment_matrix() @ jet.hessian)
                / max(1, np.linalg.norm(jet.hessian))
            )
            if wave == (0, 0, 0)
            else 0.0
        )
        structure = max(gauge, mean, product_error, sector.structural_error)
        records.append(
            {
                "ordinal": ordinal,
                "external_relative_residual": residual,
                "full_relative_residual": full,
                "structural_error": structure,
                "forcing_equal": bool(np.array_equal(forcing, jet.forcing)),
                "passed": residual <= 1e-10 and full <= 1e-9 and structure <= 5e-12,
            }
        )
    return {
        "records": records,
        "record_digest_sha256": q012a._digest(records),
        "passed": len(records) == 3081 and all(r["passed"] for r in records),
        "forcing_unchanged": all(r["forcing_equal"] for r in records),
        "failed_count": sum(not r["passed"] for r in records),
    }


def residual_mpc(
    a: np.ndarray, d: np.ndarray, f: np.ndarray, x: np.ndarray, bits=128
) -> np.ndarray:
    """Accurate residual of the supplied float64 problem, NOT a high-precision symbol."""
    if bits < 106:
        raise ValueError("at least 106 residual precision bits are required")
    with mp.context(precision=bits):
        arrays = [
            np.array([mp.mpc(complex(v)) for v in v.ravel()], dtype=object).reshape(v.shape)
            for v in (a, d, f, x)
        ]
        aa, dd, ff, xx = arrays
        result = aa @ xx - xx @ dd + ff
        return np.array([complex(v) for v in result.ravel()]).reshape(f.shape)


def structured_solutions(a: np.ndarray, d: np.ndarray, f: np.ndarray) -> tuple[dict, list]:
    initial = solve_sylvester(a, -d, -f)
    x = initial.copy()
    history = []
    for iteration in range(4):
        residual = residual_mpc(a, d, f, x)
        row = {
            "iteration": iteration,
            "float64_relative_residual": float(
                np.linalg.norm(a @ x - x @ d + f) / max(1e-14, np.linalg.norm(f))
            ),
            "mp128_relative_residual": float(
                np.linalg.norm(residual) / max(1e-14, np.linalg.norm(f))
            ),
        }
        if iteration < 3:
            correction = solve_sylvester(a, -d, -residual)
            row["correction_norm"] = float(np.linalg.norm(correction))
            x += correction
        history.append(row)
    return {"sylvester": initial, "refined": x}, history


def known_controls() -> dict:
    rng = np.random.default_rng(2026090722)
    records = []
    problems = [
        (
            np.array([[0.2, 0.07j], [0, 0.24]], dtype=complex),
            np.array([[0.7 + 0.1j, 0.03j], [0, 0.6 - 0.2j]]),
            rng.normal(size=(2, 2)) + 1j * rng.normal(size=(2, 2)),
        )
    ]
    problems.append(
        (
            np.diag([0.5 + 2**-24, 0.125]).astype(complex),
            np.array([[0.5]]),
            np.array([[2**24 + 0.5j], [1 + 1j]]),
        )
    )
    for a, d, known in problems:
        f = known @ d - a @ known
        solutions, history = structured_solutions(a, d, f)
        errors = {name: damping.relative_error(value, known) for name, value in solutions.items()}
        cross = float(
            np.linalg.norm(
                residual_mpc(a, d, f, solutions["refined"])
                - residual_mpc(a, d, f, solutions["refined"], 192)
            )
            / max(1e-14, np.linalg.norm(f))
        )
        records.append(
            {
                "errors": errors,
                "history": history,
                "mp128_mp192_scaled_difference": cross,
                "passed": max(errors.values()) <= 1e-11 and cross <= 1e-24 and len(history) == 4,
            }
        )
    negatives = []
    for expected, gap, f in (
        ("singular_compatible", 0.0, [[0.0], [1.0]]),
        ("singular_incompatible", 0.0, [[1.0], [0.0]]),
        ("nonsingular_ill_conditioned", 2**-36, [[1.0], [1.0]]),
    ):
        a, d, f = np.diag([0.5 + gap, 0.125]), np.array([[0.5]]), np.array(f)
        _, solve, _ = fallback.solve_with_fallback(a, d, f)
        negatives.append(
            {
                "expected": expected,
                "solve": solve,
                "passed": solve["status"] == expected and not solve["passed"],
            }
        )
    return {
        "positive": records,
        "negative": negatives,
        "passed": all(r["passed"] for r in records + negatives),
    }


def problem(context: cubic.CubicContext, ordinal: int, jet: cubic.TripleJet) -> tuple:
    ids = cubic.BLOCK_TRIPLES[ordinal]
    blocks = [context.blocks[b] for b in ids]
    symmetric, _, _ = cubic.symmetric_product(
        tuple(ids.index(b) for b in ids), tuple(b.dimension for b in blocks)
    )
    full = np.kron(blocks[2].dynamics, np.kron(blocks[1].dynamics, blocks[0].dynamics))
    model = context.model
    full *= np.prod(
        [damping.wave_multiplier(b.wave, model.size, model.eta, model.power) for b in blocks]
    )
    inputs = symmetric.T @ full @ symmetric
    sector = context.sectors[jet.wave]
    a = damping.wave_multiplier(jet.wave, model.size, model.eta, model.power) * sector.dynamics
    f = sector.basis.conj().T @ sector.projection @ jet.forcing
    return a, inputs, f, sector


def solve_case(context: cubic.CubicContext, ordinal: int, crosscheck: bool) -> tuple[dict, dict]:
    jet = cubic.solve_triple(context, ordinal)
    a, d, f, sector = problem(context, ordinal, jet)
    x, solve, backend = fallback.solve_with_fallback(a, d, f)
    assert np.array_equal(sector.basis @ x, jet.response)
    assert all(jet.record[k] == v for k, v in solve.items() if k != "passed")
    assert jet.record["backend"] == backend
    solutions, history = structured_solutions(a, d, f)
    solutions["svd"] = x
    model = context.model
    frame = model.frames.get(jet.wave)
    selected = frame.basis @ jet.reduced if frame is not None else np.zeros_like(jet.forcing)
    symbol = damping.fourier_symbol(
        2 * np.pi * np.asarray(jet.wave) / model.size, model.omega, model.eta, model.power
    )
    records, fields = {}, {}
    for name in SOLVERS:
        solution = solutions[name]
        response = sector.basis @ solution
        extres = float(
            np.linalg.norm(a @ solution - solution @ d + f) / max(1e-14, np.linalg.norm(f))
        )
        high = residual_mpc(a, d, f, solution)
        full = float(
            np.linalg.norm(symbol @ response - response @ d + jet.forcing - selected)
            / max(1e-14, np.linalg.norm(jet.forcing))
        )
        gauge = float(
            np.linalg.norm(sector.selected_projector @ response) / max(1, np.linalg.norm(response))
        )
        mean = (
            float(
                np.linalg.norm(d3.conserved_moment_matrix() @ response)
                / max(1, np.linalg.norm(response))
            )
            if jet.wave == (0, 0, 0)
            else 0.0
        )
        structural = max(
            gauge,
            mean,
            sector.structural_error,
            jet.record["symmetric_product_error"],
            jet.record["zero_wave_forcing_moment_error"],
        )
        precision = None
        if name == "refined" and crosscheck:
            difference = float(
                np.linalg.norm(high - residual_mpc(a, d, f, solution, 192))
                / max(1e-14, np.linalg.norm(f))
            )
            precision = {"mp128_mp192_scaled_difference": difference, "passed": difference <= 1e-24}
        records[name] = {
            "external_relative_residual": extres,
            "mp128_relative_residual": float(np.linalg.norm(high) / max(1e-14, np.linalg.norm(f))),
            "full_relative_residual": full,
            "structural_error": structural,
            "response_norm": float(np.linalg.norm(response)),
            "precision_crosscheck": precision,
            "arrays": {
                "external_solution": chart.array_metadata(solution),
                "population_response": chart.array_metadata(response),
            },
            "passed": solve["status"] == "nonsingular_practical"
            and extres <= 1e-10
            and full <= 1e-9
            and structural <= 5e-12,
        }
        fields[name] = {
            "forcing": (jet.forcing * jet.factors).T,
            "response": (response * jet.factors).T,
            "reduced": (jet.reduced * jet.factors).T,
        }
    return {
        "original_record": jet.record,
        "problem_arrays": {
            name: chart.array_metadata(value)
            for name, value in (
                ("external_dynamics", a),
                ("input_dynamics", d),
                ("external_forcing", f),
                ("forcing", jet.forcing),
            )
        },
        "solvers": records,
        "refinement_history": history,
        "solver_response_changes": {
            name: damping.relative_error(fields[name]["response"], fields["svd"]["response"])
            for name in ("sylvester", "refined")
        },
    }, {"triples": jet.input_triples, "wave": jet.wave, "fields": fields}


def selected_conjugacy(
    triples: np.ndarray, waves: np.ndarray, values: dict, conjugate: np.ndarray
) -> dict:
    lookup = {tuple(row): i for i, row in enumerate(triples)}
    partners = np.array([lookup[tuple(sorted(conjugate[row]))] for row in triples])
    checks = {
        "unique": len(lookup) == len(triples),
        "partner_involution": np.array_equal(partners[partners], np.arange(len(partners))),
        "wave_reversal": np.array_equal(waves[partners], -waves),
    }
    fields = {}
    for name, value in values.items():
        moved = value[partners]
        if name == "reduced":
            moved = moved[:, chart.CONJUGATE_COMPONENT]
        errors = np.linalg.norm(moved - value.conj(), axis=1) / np.maximum(
            1, np.linalg.norm(value, axis=1)
        )
        worst = int(np.argmax(errors))
        fields[name] = {
            "maximum_scaled_error": float(errors[worst]),
            "worst_monomial": triples[worst].tolist(),
            "failed_count": int(np.count_nonzero(errors > 1e-8)),
            "passed": bool(np.all(errors <= 1e-8)),
        }
    return {
        "coverage": all(checks.values()),
        "checks": {k: bool(v) for k, v in checks.items()},
        "fields": fields,
        "passed": all(checks.values()) and all(r["passed"] for r in fields.values()),
    }


def full_forcing_audit(context: cubic.CubicContext, progress=None) -> dict:
    triples = np.zeros((cubic.COLUMN_COUNT, 3), dtype=np.int64)
    waves = np.zeros_like(triples)
    forcing = np.zeros((cubic.COLUMN_COUNT, 27), dtype=complex)
    offset = 0
    for ordinal, ids in enumerate(cubic.BLOCK_TRIPLES):
        symmetric, local, factors = cubic.symmetric_product(
            tuple(ids.index(b) for b in ids), tuple(context.blocks[b].dimension for b in ids)
        )
        wave = tuple(sum(context.blocks[b].wave[axis] for b in ids) for axis in range(3))
        stop = offset + len(factors)
        triples[offset:stop] = np.column_stack(
            [context.indices[ids[axis]][local[:, axis]] for axis in range(3)]
        )
        waves[offset:stop] = wave
        forcing[offset:stop] = ((cubic.raw_forcing(context, ids, wave) @ symmetric) * factors).T
        offset = stop
        if progress is not None and (ordinal + 1) % 16384 == 0:
            progress(
                {
                    "phase": "full_forcing_assembly",
                    "size": context.model.size,
                    "completed": ordinal + 1,
                }
            )
    return {
        "arrays": {
            name: chart.array_metadata(value)
            for name, value in (
                ("input_triples", triples),
                ("output_waves", waves),
                ("forcing", forcing),
            )
        },
        "directional": cubic.directional_audit(context.model, triples, waves, forcing, progress),
    }
