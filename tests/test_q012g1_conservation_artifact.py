"""Closed 192-case integer campaign, independently checked against parent and GMP.

Missing final evidence fails this suite; a worker subset cannot certify H1.
No physical field is recomputed by these saved-artifact checks.
"""

from copy import deepcopy

import pytest
import test_q012g1_conservation_replay_artifact as independent

from research import q012g1_d3q27_conservation as runner
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = runner.PARENT_PATH.with_name("q012g1_d3q27_conservation.json")
# Final parent saved 2026-09-08 at 00:39:06 JST, after all three grid readbacks.
MAIN_SHA = "ca6b15627880cbe390f6a53bc87eb9a6ba0833f1f370c5b9ea2c494625e75000"


@pytest.fixture(scope="module")
def completed():
    assert _file_sha256(PATH) == MAIN_SHA
    main = runner.read_json(PATH)
    assert main["kind"] == runner.MAIN_KIND and main["backend"] == "integer"
    assert main["source_unchanged_after"] is True
    assert runner.parent.source_equal(main, runner.metadata())
    assert main["evidence_digest_sha256"] == runner.digest(main["evidence"])
    assert _all_numeric_values_finite(main)
    assert [g["size"] for g in main["evidence"]["grids"]] == [17, 33, 65]
    assert len(main["grid_artifacts"]) == 3
    return main


@pytest.fixture(scope="module")
def worker():
    assert _file_sha256(independent.PATH) == independent.WORKER_SHA
    return runner.read_json(independent.PATH)


@pytest.mark.parametrize("size", [17, 33, 65])
def test_all_192_parent_cases_1152_fields_4608_signed_identities(completed, size):
    independent.check_grid_case_values(completed, size, direction_count=32)
    independent.test_rounded_analytic_baselines_and_all_twelve_uniform_negative_controls(
        completed, size
    )


def test_all_closed_children_are_exactly_included_with_their_full_readback(completed):
    for grid, entry in zip(
        completed["evidence"]["grids"], completed["grid_artifacts"], strict=True
    ):
        path = PATH.with_name(f"{PATH.stem}_n{grid['size']}.json")
        assert entry["filename"] == path.name and entry["sha256"] == _file_sha256(path)
        child = runner.read_json(path)
        assert child["grid"] == grid and child["grid_digest_sha256"] == runner.digest(grid)
        assert child["process_id"] == completed["process_id"]
        assert child["generated_at_utc"] == completed["generated_at_utc"]
        assert child["backend"] == "integer" and runner.parent.source_equal(child, completed)
        assert entry["roundtrip_passed"] is True
        assert entry["full_saved_audit"] == {
            "passed": True,
            "cases": 64,
            "fields": 384,
            "population_sums": 10368,
            "component_comparisons": 1536,
            "negative_controls": 4,
        }
    parent_grids = runner.read_json(runner.PARENT_PATH)["cycle"]["grids"]
    audit = runner.audit_document(completed, PATH, parent_grids, worker=False)
    assert audit["passed"] and audit["cases"] == 192
    assert audit["fields"] == 1152 and audit["component_comparisons"] == 4608


def test_all_48_separate_gmp_cases_and_controls_match_the_integer_fields(completed, worker):
    assert completed["process_id"] != worker["process_id"]
    assert runner.parent.source_equal(completed, worker)
    expected = deepcopy(completed["evidence"])
    for grid in expected["grids"]:
        grid["records"] = [r for r in grid["records"] if r["specification"]["direction_index"] < 8]
        assert len(grid["records"]) == 16
    # Includes every population rational, four moments, both original models,
    # signed decomposition/counterfactual and all twelve real-grid controls.
    assert expected == worker["evidence"]
    assert completed["evidence"]["input_audit"] == runner.input_audit()
    assert completed["evidence"]["artificial_controls"] == runner.exact.artificial_controls()
    replay = runner.replay_audit(
        worker,
        independent.PATH,
        completed,
        completed["evidence"]["input_audit"],
        completed["evidence"]["artificial_controls"],
        completed["evidence"]["grids"],
        runner.read_json(runner.PARENT_PATH)["cycle"]["grids"],
    )
    assert completed["independent_replay"] == replay and replay["passed"]


def test_final_hypothesis_is_rederived_from_all_errors_without_relabeling_parent(completed):
    measured = independent.independent_failure_summary(completed["evidence"]["grids"])
    assert measured == completed["summary"]
    assert {k: v["components"] for k, v in measured.items()} == {
        "legacy": 4608,
        "exact_field": 4608,
        "sum_only": 4608,
        "base_only": 3072,
    }
    validity = completed["validity_gates"]
    assert set(validity) == {
        "sealed_parent_and_coefficients",
        "artificial_exact_arithmetic_controls",
        "unchanged_sources",
        "full_192_case_coverage",
        "all_original_fields_and_exact_decompositions_audited",
        "finite_saved_evidence",
        "all_grid_roundtrips",
        "independent_gmp_replay",
    }
    assert all(validity.values())
    h1 = (
        measured["exact_field"]["failed_components"] == 0
        and measured["sum_only"]["failed_components"] == 0
    )
    assert completed["hypothesis_gates"] == {"H1_same_fields_conserved_and_sum_only_repair": h1}
    outcome = "accepted" if h1 else "rejected"
    assert completed["study_gate"] == "passed" and completed["scientific_outcome"] == outcome
    parent = runner.read_json(runner.PARENT_PATH)
    assert _file_sha256(runner.PARENT_PATH) == runner.PARENT_SHA
    assert parent["scientific_outcome"] == "rejected"
    assert measured["legacy"]["failed_components"] == 256
    assert "Q012g rejection" in completed["claim_boundary"]
    assert (
        "defect-ratio failures and order failures remain unchanged" in completed["claim_boundary"]
    )


@pytest.mark.parametrize("damage", ["missing_case", "late_component", "summary", "child_seal"])
def test_final_audit_rejects_missing_or_tampered_late_evidence(completed, damage):
    altered = deepcopy(completed)
    if damage == "missing_case":
        altered["evidence"]["grids"][2]["records"].pop()
    elif damage == "late_component":
        c = altered["evidence"]["grids"][2]["records"][63]["models"]["3"]["comparisons"][
            "W_R_leaf"
        ][3]
        c["terms"]["exact_field_error"] = {"numerator": "1", "denominator": "1", "float": 1.0}
    elif damage == "summary":
        altered["summary"]["exact_field"]["failed_components"] += 1
    else:
        altered["grid_artifacts"][2]["sha256"] = "0" * 64
    altered["evidence_digest_sha256"] = runner.digest(altered["evidence"])
    assert not runner.audit_document(
        altered, PATH, runner.read_json(runner.PARENT_PATH)["cycle"]["grids"], worker=False
    )["passed"]
