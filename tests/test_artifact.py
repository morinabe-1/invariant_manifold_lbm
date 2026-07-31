from __future__ import annotations

import json
from pathlib import Path

from ttim_lbm.experiments import run_d2q9_baseline


def test_committed_artifact_matches_current_package_source() -> None:
    artifact_path = (
        Path(__file__).resolve().parents[1]
        / "research"
        / "artifacts"
        / "d2q9_baseline.json"
    )
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    fresh = run_d2q9_baseline()

    assert artifact["schema_version"] == fresh["schema_version"]
    assert artifact["source"] == fresh["source"]
    assert artifact["baseline_gate"] == "passed"
