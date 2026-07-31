from __future__ import annotations

import json

from ttim_lbm.studies import (
    run_manufactured_quadratic_study,
    run_q004b_branch_tracking_study,
)


def test_q004b_rejects_global_labels_and_accepts_valid_cluster_prefixes() -> None:
    result = run_q004b_branch_tracking_study()
    assert result["outcome"] == "accepted"
    assert result["superseded_question_outcome"]["outcome"] == "rejected"
    assert len(result["paths"]) == 12
    assert min(path["validated_k_c"] for path in result["paths"]) > 0.7
    assert max(
        path["path_reversal_maximum_principal_angle"]
        for path in result["paths"]
    ) < 1.0e-6
    assert max(
        path["quarter_turn_maximum_principal_angle"]
        for path in result["paths"]
    ) < 1.0e-6
    json.dumps(result)


def test_manufactured_study_passes_nontrivial_and_resonance_gates() -> None:
    result = run_manufactured_quadratic_study()
    assert result["outcome"] == "accepted"
    assert result["reduced_hessian_relative_error"] < 1.0e-12
    assert result["exact_resonance_rejected"] is True
    assert result["near_resonance_sweep"][-1]["condition_number"] > 1.0e4
    json.dumps(result)
