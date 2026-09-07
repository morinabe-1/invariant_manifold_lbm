"""Audit all stored Q012g worker cases; fresh physical replay belongs to the main run."""

import re

import numpy as np
import pytest

from research import d3q27 as d3
from research import q012g_d3q27_cubic_chart as runner
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = runner.foundation.ARTIFACT_DIRECTORY / "q012g_d3q27_cubic_chart_replay.json"
WORKER_SHA = "84e4d6f9ce241b0eab4a6eda380dbf242a83c084e4fc4bc872291bb48ef56891"


@pytest.fixture(scope="module")
def worker():
    assert _file_sha256(PATH) == WORKER_SHA
    result = runner.prior.read_json(PATH)
    assert result["kind"] == "Q012g independent 144-case full-map worker"
    assert runner.source_equal(result, runner.metadata()) and result["source_unchanged_after"]
    assert runner.foundation._digest(result["evidence"]) == result["evidence_digest_sha256"]
    assert _all_numeric_values_finite(result)
    return result


def test_full_input_seals_controls_and_144_registered_witnesses(worker):
    evidence = worker["evidence"]
    assert evidence["input_audit"] == runner.input_audit()
    assert evidence["controls"] == runner.controls()
    assert evidence["input_audit"]["passed"] and evidence["controls"]["passed"]
    assert [g["size"] for g in evidence["grids"]] == [17, 33, 65]
    assert all(runner.coverage(g, worker=True) for g in evidence["grids"])
    assert sum(len(g["records"]) for g in evidence["grids"]) == 144
    assert runner.worker_readiness(
        worker, runner.metadata(), evidence["input_audit"], evidence["controls"]
    )


@pytest.fixture(scope="module", params=(17, 33, 65), ids=("n17", "n33", "n65"))
def grid(request, worker):
    evidence = next(g for g in worker["evidence"]["grids"] if g["size"] == request.param)
    metadata = next(
        g for g in worker["grid_artifacts"] if f"_n{request.param}.json" in g["filename"]
    )
    path = PATH.parent / metadata["filename"]
    assert _file_sha256(path) == metadata["sha256"] and metadata["roundtrip_passed"]
    document = runner.prior.read_json(path)
    assert runner.source_equal(document, worker) and document["process_id"] == worker["process_id"]
    assert document["grid_digest_sha256"] == runner.foundation._digest(document["grid"])
    assert runner.scientific_worker_grid(document["grid"]) == evidence
    previous = runner.prior.read_json(runner.PRIOR_PATH)
    old_grid = next(g for g in previous["cycle"]["grids"] if g["size"] == request.param)
    assert evidence["input_rebuild"] == old_grid["input_rebuild"]
    assert evidence["fiber_load"]["entries"] == old_grid["fiber_archive"]["entries"]
    assert evidence["fiber_load"]["sha256"] == old_grid["fiber_archive"]["sha256"]
    base = d3.uniform_equilibrium((request.param,) * 3, np.zeros(4))
    return evidence, document["grid"]["offline_cost"], base


def check_field_metadata(metadata, size):
    assert metadata["shape"] == [size, size, size, 27]
    assert metadata["dtype"] == np.dtype(np.float64).str
    assert metadata["bytes"] == size**3 * 27 * 8
    assert re.fullmatch("[0-9a-f]{64}", metadata["sha256"])


def test_every_stored_physical_case_and_all_four_conservation_components(grid):
    evidence, _, base = grid
    size = evidence["size"]
    base_sums = d3.global_conserved_quantities(base)
    floor = float(100 * np.finfo(float).eps * max(1, np.linalg.norm(base)))
    for row in evidence["records"]:
        assert row["finite"] and set(row["models"]) == {"2", "3"}
        assert row["roundoff_floor"] == floor
        expected_resolved = all(data["defect_norm"] > floor for data in row["models"].values())
        assert row["resolved"] == expected_resolved
        expected_ratio = (
            row["models"]["3"]["defect_norm"] / row["models"]["2"]["defect_norm"]
            if expected_resolved
            else None
        )
        assert row["cubic_to_quadratic_defect_ratio"] == expected_ratio
        for degree in (2, 3):
            data = row["models"][str(degree)]
            assert data["degree"] == degree and data["status"] == "computed"
            check_field_metadata(data["defect_array"], size)
            assert data["defect_norm"] >= 0 and len(data["reduced_coordinates"]) == 104
            assert set(data["fields"]) == {"W", "Phi_W", "W_R"}
            for field in data["fields"].values():
                check_field_metadata(field["array"], size)
                assert field["finite"] and field["norm"] >= 0 and field["perturbation_norm"] >= 0
                assert field["maximum_local_density_deviation"] >= 0
                assert len(field["global_conserved_sums"]) == 4
            assert data["positive"] == all(
                f["minimum_population"] > 0 for f in data["fields"].values()
            )
            sums = {k: np.asarray(v["global_conserved_sums"]) for k, v in data["fields"].items()}
            differences = {
                "W_leaf": sums["W"] - base_sums,
                "W_R_leaf": sums["W_R"] - base_sums,
                "Phi_conservation": sums["Phi_W"] - sums["W"],
            }
            assert data["global_conservation_errors"] == {
                k: v.tolist() for k, v in differences.items()
            }
            means = {k: v / size**3 for k, v in differences.items()}
            assert data["site_average_conservation_errors"] == {
                k: v.tolist() for k, v in means.items()
            }
            assert data["maximum_site_average_conservation_error"] == max(
                float(np.max(np.abs(v))) for v in means.values()
            )
            for name in ("W", "W_R"):
                real = data["realification"][name]
                assert real["passed"] and real["imaginary_norm"] <= 1e-9 * max(1, real["real_norm"])
            internal = data["realification"]["R"]["cubic_realification"]
            assert (internal is None) == (degree == 2)
            if internal is not None:
                assert internal["passed"] and internal["imaginary_norm"] <= 1e-9 * max(
                    1, internal["real_norm"]
                )
        expected_amplitude_pass = (
            bool(
                expected_resolved
                and expected_ratio <= 0.5
                and all(
                    data["positive"] and data["maximum_site_average_conservation_error"] <= 5e-13
                    for data in row["models"].values()
                )
            )
            if row["kind"] == "amplitude"
            else None
        )
        assert row["amplitude_passed"] == expected_amplitude_pass


def test_worker_has_only_eight_order_directions_and_cannot_certify_full_question(grid):
    evidence, _, _ = grid
    fitted = runner.fits(evidence["records"])
    assert len(fitted) == 64
    assert all(r["complete"] for r in fitted[:8])
    assert not any(r["complete"] for r in fitted[8:])
    assert not runner.coverage(evidence, worker=False)
    assert not runner.diagnostic_coverage(evidence)
    order_records = [r for r in evidence["records"] if r["kind"] == "order"]
    for i, fit in enumerate(fitted[:8]):
        direction = [r for r in order_records if r["direction_index"] == i]
        if all(r["resolved"] for r in direction):
            for degree in (2, 3):
                logs = np.log([r["models"][str(degree)]["defect_norm"] for r in direction])
                x = np.log(runner.AMPLITUDES)
                # Independent centered least-squares expression, not the production polyfit.
                slope = np.dot(x - x.mean(), logs - logs.mean()) / np.dot(
                    x - x.mean(), x - x.mean()
                )
                np.testing.assert_allclose(fit["slopes"][str(degree)], slope, atol=1e-12)
        else:
            assert fit["slopes"] == {"2": None, "3": None} and not fit["passed"]


def test_offline_cost_and_memory_scope_remain_separate(grid):
    evidence, cost, _ = grid
    assert all(
        cost[k] > 0
        for k in (
            "fresh_quadratic_rebuild_seconds",
            "cubic_archive_load_and_audit_seconds",
            "cubic_evaluator_preparation_seconds",
        )
    )
    assert cost["cubic_original_array_bytes"] == sum(
        v["bytes"] for v in evidence["fiber_load"]["entries"].values()
    )
    assert (
        cost["cubic_original_array_bytes"]
        == cost["cubic_original_coefficient_bytes"] + cost["cubic_original_sparse_index_bytes"]
    )
    assert cost["prepared_cubic_buffers"]["engines"]["response"]["monomial_rows"] == 192920
    assert (
        cost["prepared_cubic_buffers"]["engines"]["internal"]["monomial_rows"]
        == evidence["fiber_load"]["reduced_first_shell_rows"]
    )
    inventory = cost["resident_numpy_buffers"]
    assert inventory["bytes"] == sum(g["bytes_added"] for g in inventory["groups"].values())
    assert inventory["unique_buffers"] == sum(
        g["unique_buffers_added"] for g in inventory["groups"].values()
    )
    assert "allocator overhead" in inventory["scope"]
