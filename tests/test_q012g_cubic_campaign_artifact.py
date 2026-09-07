"""Whole-campaign closure checks; run only once Q012g's parent artifact exists.

The sibling all-row and prepared-fiber audit suites pin and inspect each child.
These tests additionally verify their exact inclusion in the final parent and
rederive the aggregate scientific judgement without calling runner.decision.
"""

from copy import deepcopy

import pytest

from research import q012g_d3q27_cubic_chart as runner
from ttim_lbm.rational_spectrum import _all_numeric_values_finite, _file_sha256

PATH = runner.foundation.ARTIFACT_DIRECTORY / "q012g_d3q27_cubic_chart.json"
WORKER_PATH = PATH.with_name("q012g_d3q27_cubic_chart_replay.json")
MAIN_SHA = "6a201f212b321d8d7b3d4d143306633608c9df4c50c763e05dcd044695002944"


@pytest.fixture(scope="module")
def completed():
    # Absence is an error, not a skip, empty result, or partial-grid acceptance.
    assert _file_sha256(PATH) == MAIN_SHA
    document = runner.prior.read_json(PATH)
    assert runner.source_equal(document, runner.metadata())
    assert document["process_id"] == 29360
    cycle = deepcopy(document["cycle"])
    digest = cycle.pop("result_digest_sha256")
    assert runner.foundation._digest(cycle) == digest
    assert _all_numeric_values_finite(document)
    return document


def test_whole_parent_contains_all_closed_children_and_fixed_configuration(completed):
    cycle = completed["cycle"]
    assert (
        cycle["protocol"]
        == "Q012g fixed real cubic evaluation and full-map finite-amplitude validation"
    )
    assert cycle["configuration"] == {
        "sizes": [17, 33, 65],
        "omega": 1.5,
        "eta": 0.02,
        "power": 2,
        "real_coordinates": 104,
        "order_seed": 2026090724,
        "amplitude_seed": 2026090725,
        "symmetry_seed": 2026090726,
        "cost_seed": 2026090727,
        "amplitudes": [0.008, 0.004, 0.002, 0.001],
        "holdout_amplitudes": [0.008, 0.032],
    }
    assert [g["size"] for g in cycle["grids"]] == [17, 33, 65]
    assert len(cycle["grid_artifacts"]) == 3
    for grid, entry in zip(cycle["grids"], cycle["grid_artifacts"], strict=True):
        name = f"q012g_d3q27_cubic_chart_n{grid['size']}.json"
        assert entry["filename"] == name and entry["roundtrip_passed"]
        child_path = PATH.with_name(name)
        assert _file_sha256(child_path) == entry["sha256"]
        child = runner.prior.read_json(child_path)
        assert runner.source_equal(child, completed)
        assert child["process_id"] == completed["process_id"]
        assert child["generated_at_utc"] == completed["generated_at_utc"]
        assert child["grid_digest_sha256"] == runner.foundation._digest(child["grid"])
        assert "roundtrip_passed" not in child["grid"]
        assert {**child["grid"], "roundtrip_passed": True} == grid
    rows = [r for g in cycle["grids"] for r in g["records"]]
    assert len(rows) == 1248
    assert {
        kind: sum(r["kind"] == kind for r in rows) for kind in ("order", "amplitude", "special")
    } == {"order": 768, "amplitude": 192, "special": 288}


def test_all_inputs_controls_and_144_fresh_replay_cases_are_in_final_validity(completed):
    cycle = completed["cycle"]
    inputs, controls = runner.input_audit(), runner.controls()
    assert cycle["input_audit"] == inputs and inputs["passed"]
    assert cycle["controls"] == controls and controls["passed"]
    replay = runner.replay_audit(WORKER_PATH, inputs, controls, cycle["grids"], completed)
    assert cycle["independent_replay"] == {"status": "computed", **replay}
    assert replay["passed"]
    validity = cycle["validity_gates"]
    assert set(validity) == {
        "sealed_preflight_inputs",
        "manufactured_and_retained_solver_controls",
        "source_unchanged_after",
        "full_registered_three_grid_case_coverage",
        "fresh_paired_inputs",
        "all_diagnostic_phases_computed",
        "full_registered_diagnostic_coverage",
        "saved_order_summaries_match_cases",
        "finite_full_map_evidence",
        "complete_separated_timing_measurements",
        "independent_144_case_replay",
        "grid_evidence_roundtrip",
    }
    assert all(validity.values())
    for g in cycle["grids"]:
        assert runner.coverage(g, worker=False) and runner.diagnostic_coverage(g)
        assert g["input_rebuild"]["passed"] and g["fiber_load"]["passed"]
        for name in ("evaluation", "homogeneity", "physical_structure", "symmetry", "timing"):
            assert g[name]["status"] == "computed"
        assert g["generic_fits"] == runner.fits(g["records"])
        assert g["special_fits"] == runner.fits(g["records"], special=True)
        assert all(r["finite"] for r in g["records"]) and g["timing"]["valid"]
        assert g["roundtrip_passed"]


def test_aggregate_judgement_distinguishes_validity_orders_and_finite_amplitude(completed):
    cycle = completed["cycle"]
    grids = cycle["grids"]
    resolved = all(
        r["resolved"] for g in grids for r in g["records"] if r["kind"] in ("order", "amplitude")
    )
    hypotheses = {
        "H1_real_sparse_evaluation_and_fixed_leaf_structure": all(
            g["evaluation"]["passed"]
            and g["homogeneity"]["passed"]
            and g["physical_structure"]["structure_passed"]
            for g in grids
        ),
        "H2_all_48_cubic_symmetries": all(g["symmetry"]["passed"] for g in grids),
        "H3_independent_physical_cubic_identity": all(
            g["physical_structure"]["physics_passed"] for g in grids
        ),
        "H4_order_three_to_four": all(fit["passed"] for g in grids for fit in g["generic_fits"]),
        "H5_finite_holdout_improvement_positive_and_conserved": all(
            r["amplitude_passed"] for g in grids for r in g["records"] if r["kind"] == "amplitude"
        ),
    }
    assert sum(len(g["generic_fits"]) for g in grids) == 192
    assert cycle["generic_and_holdout_resolved"] == resolved
    assert cycle["hypothesis_gates"] == hypotheses
    valid = all(cycle["validity_gates"].values())
    outcome = (
        "inconclusive"
        if not valid or not resolved
        else "accepted"
        if all(hypotheses.values())
        else "rejected"
    )
    assert cycle["scientific_outcome"] == completed["scientific_outcome"] == outcome
    assert cycle["study_validity"] == completed["study_gate"] == ("passed" if valid else "failed")
    assert "not common-initial trajectories" in cycle["claim_boundary"]
    assert "SSM existence" in cycle["claim_boundary"] and "TT advantage" in cycle["claim_boundary"]
    assert valid and resolved and outcome == "rejected"
    assert list(hypotheses.values()) == [True, True, True, False, False]
