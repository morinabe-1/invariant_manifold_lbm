"""Full saved-corpus audit of Q012c1a, not a second 108-condition sweep."""

from __future__ import annotations

import copy
import json
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path

import pytest

from research import d3q27_quadratic as q
from research import q012a_d3q27_foundation as q012a
from research import q012c1_d3q27_damping as prior
from research import q012c1a_d3q27_damping as runner
from research import q012c_d3q27_preflight as q012c
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

ARTIFACT = q012a.ARTIFACT_DIRECTORY / "q012c1a_d3q27_damping.json"


@pytest.fixture(scope="module")
def artifact() -> dict:
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_manifest_sources_seals_and_complete_validity(artifact: dict) -> None:
    cycle = copy.deepcopy(artifact["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert q012a._digest(cycle) == digest
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(Path(runner.__file__))
    for name, module in runner.HELPERS:
        assert artifact["helper_sources"][name]["sha256"] == _file_sha256(Path(module.__file__))
    assert artifact["study_gate"] == cycle["study_validity"] == "passed", cycle["validity_gates"]
    assert len(cycle["validity_gates"]) == 11 and all(cycle["validity_gates"].values())
    assert cycle["numerical_failure"] is None
    assert _all_numeric_values_finite(artifact)
    assert runner.input_audit()["passed"]


def test_all_tables_all_pairs_and_backend_metadata_are_consistent(artifact: dict) -> None:
    directory = ARTIFACT.parent / artifact["table_directory"]
    summaries = artifact["cycle"]["conditions"]
    assert len(summaries) == 108
    assert {(r["size"], r["omega"], r["power"], r["eta"]) for r in summaries} == {
        (n, w, p, e)
        for n in prior.GRID_SIZES
        for w in prior.OMEGAS
        for p, e in prior.CONFIGURATIONS
    }
    assert {p.name for p in directory.glob("*.json")} == {r["table"]["filename"] for r in summaries}
    waves = set(q.shell_waves(3))
    blocks = [(w, label) for w in q.shell_waves(3) for label in q.LABELS]
    expected_pairs = list(combinations_with_replacement(blocks, 2))
    baselines = prior.prior_baselines()
    old_partials = {
        (r["size"], r["omega"], r["power"], r["eta"]): r
        for r in runner.prior_artifact()["cycle"]["conditions"]
    }
    pair_count = product_count = baseline_count = partial_count = 0
    for summary in summaries:
        path = directory / summary["table"]["filename"]
        assert path.parent == directory and _file_sha256(path) == summary["table"]["sha256"]
        table = json.loads(path.read_text(encoding="utf-8"))
        cycle = table["cycle"]
        assert (
            q012a._digest(cycle)
            == table["result_digest_sha256"]
            == summary["table"]["result_digest_sha256"]
        )
        assert _all_numeric_values_finite(table)
        for key, value in cycle.items():
            if key == "coefficient_screen":
                value = {k: v for k, v in value.items() if k not in ("pair_columns", "pair_rows")}
            elif key == "backend":
                value = {k: v for k, v in value.items() if k != "pair_drivers"}
            assert value == summary[key]
        screen, backend = cycle["coefficient_screen"], cycle["backend"]
        rows = q012c.unpack_pairs(screen)
        assert len(rows) == screen["pair_count"] == len(backend["pair_drivers"]) == 3081
        assert screen["product_dimension_sum"] == sum(r["product_dimension"] for r in rows) == 5460
        assert screen["real_coordinate_count"] == 104 and screen["coverage_passed"]
        for row, (left, right) in zip(rows, expected_pairs):
            assert (tuple(row["left_wave"]), row["left_label"]) == left
            assert (tuple(row["right_wave"]), row["right_label"]) == right
            output = q.canonical_wave(
                tuple(a + b for a, b in zip(left[0], right[0])), cycle["size"]
            )
            assert tuple(row["output_wave"]) == output and row["output_is_selected"] == (
                output in waves
            )
            assert row["external_dimension"] == (
                23 if output in waves or output == (0, 0, 0) else 27
            )
            ld, rd = (2 if left[1] == "shear" else 1), (2 if right[1] == "shear" else 1)
            assert row["product_dimension"] == (ld * (ld + 1) // 2 if left == right else ld * rd)
            assert row["symmetric_square"] == (left == right)
            assert row["operator_dimension"] == row["product_dimension"] * row["external_dimension"]
            assert row["passed"] == (
                row["status"] == "nonsingular_practical"
                and row["solve_relative_residual"] <= 1e-10
                and max(row["graph_gauge_error"], row["zero_wave_moment_error"]) <= 5e-12
            )
            if row["status"].startswith("singular"):
                assert (
                    row["numerical_rank"] < row["operator_dimension"]
                    and row["condition_number"] is None
                )
                assert not row["passed"]
            else:
                assert row["numerical_rank"] == row["operator_dimension"]
                assert (row["status"] == "nonsingular_practical") == (
                    row["condition_number"] <= 1e8
                )
            assert (
                row["response_global_l2_norm"] == row["response_local_norm"] / cycle["size"] ** 1.5
            )
            assert row["structural_error"] <= 5e-12
        assert screen["coefficient_prequalified"] == all(r["passed"] for r in rows)
        assert screen["failed_pair_count"] == sum(not r["passed"] for r in rows)
        assert screen["status_counts"] == dict(Counter(r["status"] for r in rows))
        assert screen["maximum_structural_error"] == max(r["structural_error"] for r in rows)
        assert screen["worst_nonsingular_condition"] == max(
            (r for r in rows if r["condition_number"] is not None),
            key=lambda r: r["condition_number"],
        )
        assert screen["first_singular_pair"] == next(
            (r for r in rows if r["condition_number"] is None), None
        )
        assert screen["residual_only_failure_count"] == sum(
            r["status"] == "nonsingular_practical"
            and r["solve_relative_residual"] > 1e-10
            and max(r["graph_gauge_error"], r["zero_wave_moment_error"]) <= 5e-12
            for r in rows
        )
        assert screen["maximum_solve_relative_residual"] == max(
            r["solve_relative_residual"] for r in rows
        )
        assert screen["maximum_response_global_l2_norm"] == max(
            r["response_global_l2_norm"] for r in rows
        )
        assert set(backend["pair_drivers"]) <= {"gesdd", "gesvd"}
        assert (
            backend["fallback_count"]
            == backend["pair_drivers"].count("gesvd")
            == len(backend["fallback_records"])
        )
        assert backend["passed"]
        assert {r["pair_ordinal_zero_based"] for r in backend["fallback_records"]} == {
            i for i, driver in enumerate(backend["pair_drivers"]) if driver == "gesvd"
        }
        for record in backend["fallback_records"]:
            assert record["original_error"] == "SVD did not converge" and record["passed"]
            assert record["reconstruction_relative_error"] <= 1e-12
            assert (
                max(record["left_orthogonality_error"], record["right_orthogonality_error"])
                <= 1e-12
            )
        normal = cycle["normal_ordering"]
        assert normal["coverage_passed"] and normal["selected_dimension"] == 104
        assert normal["external_dimension"] + 104 == 27 * cycle["size"] ** 3 - 4
        assert (
            normal["normal_modulus_gap"]
            == normal["fastest_selected"]["modulus"] - normal["slowest_external"]["modulus"]
        )
        assert normal["n_squared_gap"] == cycle["size"] ** 2 * normal["normal_modulus_gap"]
        assert cycle["jointly_prequalified"] == (
            screen["coefficient_prequalified"]
            and normal["normal_ordering_prequalified"]
            and cycle["map_control_passed"]
            and cycle["hydrodynamic_control_passed"]
            and cycle["hessian_control_passed"]
        )
        if cycle["eta"] == 0:
            baseline_count += 1
            original = baselines[cycle["size"], cycle["omega"]]
            assert all(
                screen.get(key) == value for key, value in original["coefficient_screen"].items()
            )
            assert (
                normal == original["normal_ordering"] and cycle["baseline_reproduction"]["passed"]
            )
            assert not cycle["jointly_prequalified"]
        key = cycle["size"], cycle["omega"], cycle["power"], cycle["eta"]
        if key in old_partials:
            partial_count += 1
            legacy = {
                k: v for k, v in cycle.items() if k not in ("backend", "prior_partial_reproduction")
            }
            assert q012a._digest(legacy) == old_partials[key]["table"]["result_digest_sha256"]
            assert cycle["prior_partial_reproduction"] is True
        else:
            assert cycle["prior_partial_reproduction"] is None
        pair_count += len(rows)
        product_count += screen["product_dimension_sum"]
    assert (pair_count, product_count, baseline_count, partial_count) == (332748, 589680, 12, 4)


def test_selection_and_fresh_family_replay_obey_preregistration(artifact: dict) -> None:
    cycle = artifact["cycle"]
    families, chosen = prior.classify_families(cycle["conditions"])
    assert len(families) == 32 and families == cycle["families"]
    assert chosen == cycle["selected_family"]
    assert artifact["scientific_outcome"] == ("accepted" if chosen is not None else "rejected")
    if chosen is not None:
        assert (
            chosen["power"] == 2
            and chosen["leading_viscosity_preserved"]
            and chosen["jointly_viable"]
        )
    replay = cycle["independent_replay"]
    expected = (
        {"power": 2, "eta": 0.05, "omega": 1.2}
        if chosen is None
        else {key: chosen[key] for key in ("power", "eta", "omega")}
    )
    assert replay["configuration"] == expected and replay["passed"]
    assert [r["size"] for r in replay["records"]] == list(prior.GRID_SIZES)
    for row in replay["records"]:
        original = next(
            r
            for r in cycle["conditions"]
            if r["size"] == row["size"] and all(r[k] == v for k, v in expected.items())
        )
        assert row["passed"] and row["pair_count"] == 3081
        assert row["result_digest_sha256"] == original["table"]["result_digest_sha256"]
    assert "not all 108 conditions rerun" in replay["scope"]
    assert "Q012c1 remains inconclusive" in cycle["protocol"]
