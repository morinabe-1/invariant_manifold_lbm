"""All-row/all-fiber Q012f2 verification plus fresh worst-case and physical checks."""

from fractions import Fraction
from hashlib import sha256
from itertools import product
from pathlib import Path

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_exact_residual as exact
from research import d3q27_refined_cubic as refined
from research import q012a_d3q27_foundation as q012a
from research import q012f2_d3q27_refined_cubic as runner
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = q012a.ARTIFACT_DIRECTORY / "q012f2_d3q27_refined_cubic.json"


@pytest.fixture(scope="module")
def artifact():
    assert _file_sha256(PATH) == "65a0046d2b54c1192a84fbce481da0e804364cf62566d2e9c18204e372158ec1"
    return runner.read_json(PATH)


@pytest.fixture(scope="module", params=(17, 33, 65), ids=("n17", "n33", "n65"))
def grid(request):
    # A closed grid can be audited while the same master process scans the next grid.
    # Final three-grid classification tests still require the complete main artifact.
    saved_grid = runner.read_json(PATH.with_name(PATH.stem + f"_n{request.param}.json"))
    assert saved_grid["kind"] == "Q012f2 complete grid evidence"
    current = runner.metadata()
    assert all(saved_grid[k] == current[k] for k in ("source", "runner_source", "helper_sources"))
    data = saved_grid["grid"]
    core = dict(data)
    digest = core.pop("result_digest_sha256")
    assert q012a._digest(core) == digest
    assert data["size"] == request.param and data["summary"]["coverage_passed"]
    archive = data["fiber_archive"]
    path = PATH.parent / archive["filename"]
    assert refined.file_hash(path) == archive["sha256"]
    assert path.stat().st_size == archive["bytes"]
    with np.load(path, allow_pickle=False) as saved:
        arrays = {k: saved[k] for k in saved.files}
    assert set(arrays) == {"input_triples", "output_waves", "forcing", "response", "reduced"}
    assert {k: chart.array_metadata(v) for k, v in arrays.items()} == archive["entries"]
    assert all(np.all(np.isfinite(v)) for v in arrays.values())
    return data, arrays


def test_main_source_and_previous_scientific_decisions_are_sealed(artifact):
    cycle = dict(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert (
        q012a._digest(cycle)
        == digest
        == "ca64e1235a4dc94a4736bc051f9bbd780835a77d3ed0718bf886f93064c1ef7f"
    )
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(runner.__file__))
    for name, module in runner.HELPERS:
        assert artifact["helper_sources"][name]["sha256"] == _file_sha256(Path(module.__file__))
    assert runner.input_audit() == cycle["input_audit"]
    assert cycle["input_audit"]["passed"] and runner.controls() == cycle["controls"]
    assert _all_numeric_values_finite(artifact)
    assert runner.read_json(runner.PRIOR_PATH)["scientific_outcome"] == "accepted"
    assert runner.read_json(runner.previous.PRIOR_PATH)["scientific_outcome"] == "rejected"
    assert runner.PRECISION_RUNNER.prior_artifact()["scientific_outcome"] == "rejected"


def test_grid_results_match_final_result_and_preserve_cost_scope(artifact):
    for grid_data, meta in zip(
        artifact["cycle"]["grids"], artifact["cycle"]["grid_artifacts"], strict=True
    ):
        path = PATH.parent / meta["filename"]
        assert _file_sha256(path) == meta["sha256"]
        saved = runner.read_json(path)
        assert saved["grid"] == grid_data
        assert all(saved[k] == artifact[k] for k in ("source", "runner_source", "helper_sources"))
        copy = dict(grid_data)
        digest = copy.pop("result_digest_sha256")
        assert q012a._digest(copy) == digest
        cost = copy["cost"]
        assert cost["wall_seconds"] > 0 and cost["cpu_seconds"] > 0
        assert cost["record_archive_bytes"] == copy["record_archive"]["bytes"]
        assert cost["fiber_archive_bytes"] == copy["fiber_archive"]["bytes"]


def rational(pair):
    return Fraction(int(pair[0]), int(pair[1]))


def independent_residual_gates(row):
    proof = row["exact_residual"]
    norms = {k: rational(v) for k, v in proof["norms_squared"].items()}
    assert all(v >= 0 for v in norms.values())
    stored2 = Fraction.from_float(row["stored_denominator"]) ** 2
    exact2 = max(Fraction.from_float(1e-14) ** 2, norms["forcing_norm_squared"])
    decimal2 = max(Fraction(1, 10**28), norms["forcing_norm_squared"])
    tolerance2 = Fraction.from_float(1e-10) ** 2
    assert stored2 == rational(proof["stored_denominator_squared"])
    assert exact2 == rational(proof["exact_denominator_squared"])
    assert decimal2 == rational(proof["decimal_denominator_squared"])
    assert tolerance2 == rational(proof["binary_tolerance_squared"])
    rr = norms["exact_residual_norm_squared"]
    gates = {
        "legacy": row["refined"]["external_relative_residual"] <= 1e-10,
        "rounded_vector_exact_norm": norms["rounded_residual_norm_squared"] <= tolerance2 * stored2,
        "exact_residual_stored_denominator": rr <= tolerance2 * stored2,
        "exact_residual_exact_denominator": rr <= tolerance2 * exact2,
        "exact_decimal_constants": rr <= Fraction(1, 10**20) * decimal2,
    }
    assert gates == proof["gates"]
    assert proof["legacy_relative_residual"] == row["refined"]["external_relative_residual"]
    assert proof["evaluation_only_mismatch"] == (
        not gates["legacy"]
        and not gates["rounded_vector_exact_norm"]
        and all(gates[k] for k in exact.EXACT_GATES)
    )
    assert proof["mp128_agrees"] == (
        norms["evaluation128_error_squared"] <= Fraction(1, 10**48) * exact2
    )
    return gates, rr / exact2


def independent_coordinate_columns(block_ids):
    # Each wave owns a two-dimensional shear block followed by acoustic + / -.
    # Enumerate coordinate monomials directly, without the solver's symmetric basis.
    indices = []
    for block in block_ids:
        wave, branch = divmod(block, 3)
        indices.append((4 * wave, 4 * wave + 1) if branch == 0 else (4 * wave + branch + 1,))
    return np.asarray(
        list(dict.fromkeys(tuple(sorted(values)) for values in product(*indices[::-1]))),
        dtype=np.int64,
    )


def test_all_82160_records_and_192920_fibers_have_independent_gate_and_hash_checks(grid):
    data, arrays = grid
    archive = data["record_archive"]
    path = PATH.parent / archive["filename"]
    assert refined.file_hash(path) == archive["sha256"]
    assert path.stat().st_size == archive["bytes"]
    digest, count, offset = sha256(), 0, 0
    failed, legacy, mismatches, selected, mp_failed = [], [], [], [], []
    maximum_exact, worst_exact = None, None
    for row in refined.iter_records(path):
        digest.update(refined.record_line(row))
        assert row["ordinal"] == count
        assert _all_numeric_values_finite(row)
        reference, current = row["paired_svd_reference"], row["refined"]
        assert reference["block_ordinals"] == list(cubic.BLOCK_TRIPLES[count])
        residual, squared = independent_residual_gates(row)
        gates = {
            "rank_and_condition": reference["status"] == "nonsingular_practical"
            and reference["numerical_rank"] == reference["operator_dimension"]
            and reference["condition_number"] is not None
            and reference["condition_number"] <= 1e8,
            "svd_backend_integrity": reference["backend"]["passed"],
            **{k: residual[k] for k in exact.EXACT_GATES},
            "full_population_equation": current["full_relative_residual"] <= 1e-9,
            "fixed_leaf_and_structure": current["structural_error"] <= 5e-12,
        }
        assert gates == row["candidate_gates"] and row["passed"] == all(gates.values())
        assert current["passed"] == (
            reference["status"] == "nonsingular_practical"
            and residual["legacy"]
            and current["full_relative_residual"] <= 1e-9
            and current["structural_error"] <= 5e-12
        )
        assert reference["rank_threshold"] == float(
            100
            * np.finfo(float).eps
            * reference["operator_dimension"]
            * reference["largest_singular_value"]
        )
        assert [h["iteration"] for h in row["refinement_history"]] == [0, 1, 2, 3]
        assert all("correction_norm" in h for h in row["refinement_history"][:3])
        assert "correction_norm" not in row["refinement_history"][3]
        if not row["passed"]:
            failed.append(count)
        if not current["passed"]:
            legacy.append(count)
        if row["exact_residual"]["evaluation_only_mismatch"]:
            mismatches.append(count)
        if not row["exact_residual"]["mp128_agrees"]:
            mp_failed.append(count)
        if row["previous_match"] is not None:
            assert row["previous_match"]["passed"]
            assert all(row["previous_match"]["checks"].values())
            selected.append(row)
        stop = offset + reference["product_dimension"]
        np.testing.assert_array_equal(
            arrays["input_triples"][offset:stop],
            independent_coordinate_columns(reference["block_ordinals"]),
        )
        for name in ("forcing", "response", "reduced"):
            assert (
                chart.array_metadata(arrays[name][offset:stop]) == row["coefficient_arrays"][name]
            )
        np.testing.assert_array_equal(
            arrays["output_waves"][offset:stop],
            np.tile(reference["output_wave"], (stop - offset, 1)),
        )
        if maximum_exact is None or squared > maximum_exact:
            maximum_exact, worst_exact = squared, row
        offset, count = stop, count + 1
    assert count == archive["record_count"] == 82160
    assert offset == len(arrays["input_triples"]) == 192920
    assert digest.hexdigest() == archive["records_digest_sha256"]
    assert data["summary"]["candidate_failed_ordinals"] == failed
    assert data["summary"]["legacy_failed_ordinals"] == legacy
    assert data["summary"]["evaluation_only_mismatch_ordinals"] == mismatches
    assert data["summary"]["mp128_agreement_failures"] == len(mp_failed)
    assert data["summary"]["worst_cases"]["exact_residual"] == worst_exact
    assert data["replay_records"] == selected and len(selected) == 324
    assert refined.summarize(refined.iter_records(path)) == data["summary"]


def test_full_coordinate_wave_coverage_and_unprojected_conjugacy(grid):
    data, arrays = grid
    triples, waves = arrays["input_triples"], arrays["output_waves"]
    assert triples.dtype == waves.dtype == np.dtype("int64")
    assert all(
        arrays[k].dtype == np.dtype("complex128") for k in ("forcing", "response", "reduced")
    )
    assert len(np.unique(triples, axis=0)) == 192920
    assert np.all(triples[:, :-1] <= triples[:, 1:])
    assert np.min(triples) == 0 and np.max(triples) == 103
    np.testing.assert_array_equal(waves, np.asarray(chart.WAVES)[triples // 4].sum(axis=1))
    conjugate = np.array(
        [
            4 * chart.WAVES.index(tuple(-k for k in chart.WAVES[i // 4]))
            + chart.CONJUGATE_COMPONENT[i % 4]
            for i in range(104)
        ]
    )
    lookup = np.full(104**3, -1, dtype=np.int64)
    lookup[np.ravel_multi_index(triples.T, (104, 104, 104))] = np.arange(len(triples))
    opposite = np.sort(conjugate[triples], axis=1)
    partner = lookup[np.ravel_multi_index(opposite.T, (104, 104, 104))]
    assert np.all(partner >= 0)
    np.testing.assert_array_equal(partner[partner], np.arange(len(triples)))
    np.testing.assert_array_equal(waves[partner], -waves)
    passed = True
    for name in ("forcing", "response", "reduced"):
        value = arrays[name]
        moved = value[partner]
        if name == "reduced":
            moved = moved[:, chart.CONJUGATE_COMPONENT]
        errors = np.linalg.norm(moved - value.conj(), axis=1) / np.maximum(
            1, np.linalg.norm(value, axis=1)
        )
        expected = data["conjugacy"]["fields"][name]
        assert float(np.max(errors)) == expected["maximum_scaled_error"]
        assert bool(np.all(errors <= 1e-8)) == expected["passed"]
        passed &= expected["passed"]
    assert passed == data["conjugacy"]["passed"]


def test_completed_grid_matches_independent_324_case_worker(grid):
    data, _ = grid
    worker_path = PATH.with_name(PATH.stem + "_replay.json")
    assert (
        _file_sha256(worker_path)
        == "7bdfe549c765d054514af445c10965d91f4565572fea3c4858cbce577d115147"
    )
    worker = runner.read_json(worker_path)
    saved = runner.read_json(PATH.with_name(PATH.stem + f"_n{data['size']}.json"))
    expected = next(g for g in worker["evidence"]["grids"] if g["size"] == data["size"])
    assert expected["input_rebuild"] == data["input_rebuild"]
    assert expected["records"] == data["replay_records"]
    assert len(expected["records"]) == 324
    assert worker["process_id"] != saved["process_id"]
    assert all(worker[k] == saved[k] for k in ("source", "runner_source", "helper_sources"))
    assert worker["evidence"]["input_audit"] == runner.input_audit()
    assert worker["evidence"]["controls"] == runner.controls()


def test_fresh_worst_cases_and_full_physical_forcing(grid):
    data, arrays = grid
    model, rebuild, old, old_exact = runner.fresh_input(data["size"])
    assert rebuild == data["input_rebuild"] and rebuild["passed"]
    context = cubic.build_context(model)
    candidates = {
        data["summary"]["worst_cases"][k]["ordinal"]
        for k in ("exact_residual", "condition", "full_residual")
    }
    candidates.update(data["summary"]["candidate_failed_ordinals"][:1])
    records = {
        r["ordinal"]: r
        for r in refined.iter_records(PATH.parent / data["record_archive"]["filename"])
        if r["ordinal"] in candidates
    }
    assert len(records) == len(candidates)
    for ordinal, expected in records.items():
        row, _ = runner.case(context, ordinal, old, old_exact, exact.audit_gmp)
        assert row == expected
    actual = cubic.directional_audit(
        model, arrays["input_triples"], arrays["output_waves"], arrays["forcing"]
    )
    assert actual == data["directional_forcing"] and actual["passed"]
    expected = runner.old_grid(data["size"])["full_forcing"]["paired"]
    assert actual == expected["directional"]
    assert {
        k: chart.array_metadata(arrays[k]) for k in ("input_triples", "output_waves", "forcing")
    } == expected["arrays"]


def test_full_independent_972_replay_and_classification(artifact):
    cycle = artifact["cycle"]
    path = PATH.parent / cycle["independent_replay"]["filename"]
    assert _file_sha256(path) == "7bdfe549c765d054514af445c10965d91f4565572fea3c4858cbce577d115147"
    replay = runner.replay_audit(
        path, cycle["input_audit"], cycle["controls"], cycle["grids"], artifact
    )
    assert replay == cycle["independent_replay"] and replay["passed"]
    validity, hypotheses, outcome = runner.decision(
        cycle["input_audit"], cycle["controls"], cycle["grids"], replay
    )
    assert validity == cycle["validity_gates"] and all(validity.values())
    assert hypotheses == cycle["hypothesis_gates"] and all(hypotheses.values())
    assert outcome == cycle["scientific_outcome"] == artifact["scientific_outcome"] == "accepted"
    assert artifact["study_gate"] == cycle["study_validity"] == "passed"


def test_missing_witness_cannot_be_certified_even_with_recomputed_digest(artifact, tmp_path):
    cycle = artifact["cycle"]
    source = PATH.parent / cycle["independent_replay"]["filename"]
    worker = runner.read_json(source)
    worker["evidence"]["grids"][2]["records"].pop()
    worker["evidence_digest_sha256"] = q012a._digest(worker["evidence"])
    target = tmp_path / "incomplete.json"
    runner.previous.write_json(target, worker)
    audit = runner.replay_audit(
        target, cycle["input_audit"], cycle["controls"], cycle["grids"], artifact
    )
    assert not audit["passed"] and not audit["checks"]["all_fresh_values_and_exact_proofs_equal"]
