from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007x_mpfr_fixed_leaf as q007x
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict) -> Fraction:
    return Fraction(
        int(record["numerator_base16"], 16),
        int(record["denominator_base16"], 16),
    )


@pytest.fixture(scope="module")
def q007x_artifact() -> dict:
    artifact_path = (
        Path(q007x.__file__).resolve().parent
        / "artifacts"
        / "q007x_mpfr_fixed_leaf.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q007x_returns_a_valid_fixed_leaf_noncertificate(
    q007x_artifact,
) -> None:
    cycle = q007x_artifact["cycle"]

    assert cycle == q007x.run_mpfr_fixed_leaf_audit()
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "not_certified"
    assert cycle["scientific_classification"] == (
        "MPFR-85 realizes the Q007w one-step arithmetic bound but not "
        "the fixed conservation leaf"
    )
    assert len(cycle["validity_gates"]) == 8
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert {
        name: gate["passed"]
        for name, gate in cycle["hypothesis_gates"].items()
    } == {
        "mpfr_backend_realizes_q007w_85bit_semantics": True,
        "q007w_one_step_bounds_apply_to_backend": True,
        "componentwise_encoding_preserves_fixed_leaf": False,
        "collision_preserves_fixed_leaf": False,
        "streaming_and_filter_preserve_fixed_leaf": False,
        "fixed_leaf_all_iterate_induction_closes": False,
    }


def test_q007x_seals_the_backend_source_and_context(
    q007x_artifact,
) -> None:
    cycle = q007x_artifact["cycle"]
    source = cycle["source_audit"]
    context = cycle["context_audit"]

    assert source["files"]["backend"]["sha256"] == (
        q007x.REGISTERED_BACKEND_SOURCE_SHA256
    )
    assert source["files"]["pyproject"]["sha256"] == (
        q007x.REGISTERED_PYPROJECT_SHA256
    )
    assert source["files"]["d2q9"]["sha256"] == (
        q007x.REGISTERED_D2Q9_SOURCE_SHA256
    )
    assert source["files"]["filter"]["sha256"] == (
        q007x.REGISTERED_FILTER_SOURCE_SHA256
    )
    assert all(record["sha256_matches"] for record in source["files"].values())
    assert source["dependency_pin_count"] == 1
    assert source["forbidden_implicit_or_fused_operations_absent"]
    assert source["passed"]

    assert context["runtime"]["gmpy2_version"] == "2.3.1"
    assert context["runtime"]["mpfr_version"] == "MPFR 4.2.2"
    assert context["runtime"]["gmp_version"] == "GMP 6.3.0"
    assert context["runtime"]["precision_bits"] == 85
    assert context["runtime"]["emin"] == -1105
    assert context["runtime"]["emax"] == 1024
    assert context["runtime"]["subnormalize"]
    assert context["q007w_subnormal_fallback_match"]
    assert context["context_restored"]
    assert not any(context["dangerous_construction_flags"].values())
    assert context["passed"]


def test_q007x_matches_every_registered_mpfr_operation_bitwise(
    q007x_artifact,
) -> None:
    campaign = q007x_artifact["cycle"]["backend_campaign"]

    assert campaign["probe_count"] == 4
    assert campaign["expected_trace_records_per_probe"] == 70824
    assert campaign["expected_map_trace_records_per_probe"] == 70805
    assert campaign["aggregate_trace_digest_sha256"] == (
        "49ce9b304b4b6a07fdf7d7baed6c9118a97c5a08e489e3aa5eacde28662c2351"
    )
    assert campaign["result_digest_sha256"] == (
        "12cb83a87895d50523c909ad314b9ad155ac507af73e05f1b28cfb2a65328c7d"
    )
    assert campaign["summary"]["all_traces_match"]
    assert campaign["summary"]["all_operation_domains_pass"]
    assert campaign["summary"]["context_restored"]
    for probe in campaign["probes"]:
        assert probe["trace"]["record_count"] == 70824
        assert probe["trace"]["map_record_count"] == 70805
        assert probe["trace"]["mismatch_count"] == 0
        assert probe["trace"]["first_mismatch"] is None
        assert probe["trace"]["passed"]
        assert probe["operation_domain"]["operation_counts"] == (
            probe["operation_domain"]["expected_operation_counts"]
        )
        assert probe["operation_domain"]["passed"]


def test_q007x_observed_stages_fit_the_q007w_bounds(
    q007x_artifact,
) -> None:
    campaign = q007x_artifact["cycle"]["backend_campaign"]
    utilizations = []

    assert campaign["summary"]["all_stage_bounds_and_positivity_pass"]
    for probe in campaign["probes"]:
        for stage in probe["stage_comparisons"].values():
            observed = _fraction(stage["maximum_observed_component_error"])
            bound = _fraction(stage["registered_component_error_upper"])
            utilization = _fraction(stage["error_bound_utilization"])
            assert observed <= bound
            assert utilization == observed / bound
            assert utilization < 1
            assert _fraction(stage["minimum_mpfr_population"]) > 0
            assert stage["error_enclosed"]
            assert stage["strictly_positive"]
            assert stage["passed"]
            utilizations.append(utilization)

    assert max(utilizations) == pytest.approx(0.15250294804773457)
    bridge = q007x_artifact["cycle"]["q007w_reentry_bridge"]
    assert _fraction(bridge["base_error"]) < _fraction(
        bridge["base_margin"]
    )
    assert _fraction(bridge["normal_error"]) < _fraction(
        bridge["normal_margin"]
    )
    assert bridge["strict_base_and_normal_reentry"]
    assert bridge["semantic_bridge_passed"]
    assert bridge["one_step_bound_passed"]


def test_q007x_identifies_encoding_collision_and_filter_leaf_defects(
    q007x_artifact,
) -> None:
    cycle = q007x_artifact["cycle"]
    algebra = cycle["constant_algebra"]
    campaign = cycle["backend_campaign"]

    assert _fraction(algebra["weight_sum_defect"]) == Fraction(
        1,
        154742504910672534362390528,
    )
    assert _fraction(algebra["weight_momentum_x_defect"]) == 0
    assert _fraction(algebra["weight_momentum_y_defect"]) == 0
    assert _fraction(
        algebra["filter_partition_of_unity_defect"]
    ) == Fraction(
        5,
        618970019642690137449562112,
    )
    assert algebra["nonzero_mass_and_filter_obstructions_reproduced"]
    assert algebra["passed"]

    summary = campaign["summary"]
    assert not summary["all_encodings_conserve"]
    assert not summary["all_collisions_conserve"]
    assert summary["all_streaming_conserves"]
    assert not summary["all_filters_conserve"]
    assert not summary["all_full_steps_conserve"]
    for probe in campaign["probes"]:
        conservation = probe["conservation"]
        assert not conservation["encoding_exact"]
        assert conservation["streaming_exact"]
        assert not conservation["filter_exact"]
        assert not conservation["full_step_exact"]
        assert _fraction(
            conservation["streaming_minus_collision"]["mass"]
        ) == 0
        assert _fraction(
            conservation["streaming_minus_collision"]["momentum_x"]
        ) == 0
        assert _fraction(
            conservation["streaming_minus_collision"]["momentum_y"]
        ) == 0


def test_q007x_records_provenance_and_preserves_prior_claims(
    q007x_artifact,
) -> None:
    cycle = q007x_artifact["cycle"]
    runner_path = Path(q007x.__file__).resolve()

    assert q007x_artifact["schema_version"] == 1
    assert q007x_artifact["source"] == source_metadata()
    assert q007x_artifact["runner_source"] == {
        "filename": "q007x_mpfr_fixed_leaf.py",
        "sha256": _file_sha256(runner_path),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert q007x_artifact["study_gate"] == "passed"
    assert q007x_artifact["scientific_outcome"] == "not_certified"
    assert cycle["input_artifact"]["sha256"] == (
        q007x.REGISTERED_Q007W_ARTIFACT_SHA256
    )
    assert cycle["input_artifact"]["observed_runner_sha256"] == (
        q007x.REGISTERED_Q007W_RUNNER_SHA256
    )
    assert cycle["input_artifact"]["passed"]
    assert "fixed-leaf induction is not certified" in cycle["claim_boundary"]
    assert not any(cycle["preserved_prior_outcomes"].values())
    assert cycle["theorem_consequence"] == {
        "concrete_backend_realizes_q007w_85bit_semantics": True,
        "concrete_backend_one_step_stages_strictly_positive": True,
        "componentwise_encoding_preserves_fixed_conservation_leaf": False,
        "one_step_backend_preserves_fixed_conservation_leaf": False,
        "all_iterate_mpfr85_q007s_tube_invariance": False,
    }
    json.dumps(q007x_artifact, allow_nan=False)
