from __future__ import annotations

import json
from pathlib import Path

from ttim_lbm.experiments import run_d2q9_baseline
from ttim_lbm.provenance import source_metadata

ARTIFACT_DIRECTORY = (
    Path(__file__).resolve().parents[1] / "research" / "artifacts"
)


def test_committed_artifact_matches_current_package_source() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "d2q9_baseline.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    fresh = run_d2q9_baseline()

    assert artifact["schema_version"] == fresh["schema_version"]
    assert artifact["source"] == fresh["source"]
    assert artifact["baseline_gate"] == "passed"


def test_q004b_artifact_preserves_registered_scope_and_passed_gates() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q004b_and_manufactured.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["mathematical_scope"] == {
        "construction_grid_parity": "odd periodic square grids only",
        "even_grids": "diagnostic parity and obstruction analysis only",
        "conservation_treatment": (
            "fixed global mass and momentum leaf for future nonzero-mode charts"
        ),
        "manifold_claim": (
            "candidate until Q005 nonresonance and normal-attraction gates pass"
        ),
    }
    branch_tracking, manufactured = artifact["cycles"]
    assert branch_tracking["outcome"] == "accepted"
    assert branch_tracking["superseded_question_outcome"]["outcome"] == "rejected"
    assert manufactured["outcome"] == "accepted"
    assert all(gate["passed"] for gate in branch_tracking["gates"].values())
    assert all(gate["passed"] for gate in manufactured["gates"].values())


def test_q005_artifact_records_a_valid_falsification() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q005_nonresonance.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["cycle"]["study_validity"] == "passed"
    assert artifact["cycle"]["hypothesis_outcome"] == "rejected"
    assert all(
        gate["passed"] for gate in artifact["cycle"]["gates"].values()
    )
    assert (
        artifact["cycle"]["summary"]["minimum_shell_compatible_nonunique_count"]
        == 16
    )
    assert (
        artifact["cycle"]["summary"][
            "falsified_registered_isotropic_candidate_count"
        ]
        == 16
    )


def test_q006s_artifact_records_only_the_finite_grid_stripe_claim() -> None:
    artifact_path = ARTIFACT_DIRECTORY / "q006s_stripe.json"
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["study_gate"] == "passed"
    assert artifact["mathematical_scope"] == {
        "construction": "finite-grid y-independent stripe solver oracle",
        "construction_grid": [1, 17],
        "square_grid_lift": [17, 17],
        "conservation_treatment": "fixed global mass and momentum leaf",
        "manifold_claim": (
            "local quadratic candidate chart only; no full 2D or "
            "grid-uniform SSM existence claim"
        ),
    }
    cycle = artifact["cycle"]
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert all(gate["passed"] for gate in cycle["gates"].values())
    assert cycle["registered_scope"]["residual_seed"] == 20260802
    assert cycle["registered_scope"]["shadow_seed"] == 20260803
    assert (
        cycle["non_gating_domain_stress"][
            "maximum_directional_residual_ratio_at_0p1"
        ]
        > 0.1
    )
