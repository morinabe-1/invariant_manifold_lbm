from __future__ import annotations

import json

from ttim_lbm.experiments import run_d2q9_baseline


def test_research_baseline_passes_and_records_all_cycles() -> None:
    result = run_d2q9_baseline()
    assert result["baseline_gate"] == "passed"
    assert result["source"]["package_version"] == "0.1.0"
    assert len(result["source"]["package_source_sha256"]) == 64
    assert [cycle["outcome"] for cycle in result["cycles"]] == [
        "rejected",
        "accepted",
        "accepted",
        "accepted",
    ]
    parameterization = result["cycles"][2]
    assert parameterization["hessian_relative_error_against_analytic_equilibrium"] < 1.0e-12
    assert parameterization["direction_sweep"]["minimum_quadratic_order"] > 2.9
    json.dumps(result)
