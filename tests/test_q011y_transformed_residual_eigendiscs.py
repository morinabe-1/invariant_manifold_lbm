from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011y_transformed_residual_eigendiscs as q011y
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


@pytest.fixture(scope="module")
def q011y_cycle() -> dict[str, Any]:
    return q011y.run_transformed_residual_eigendisc_audit()


def test_q011y_seals_four_prior_certificates_and_q011o(
    q011y_cycle: dict[str, Any],
) -> None:
    sealed = q011y_cycle["sealed_input_audit"]
    assert sealed["passed"]
    assert sealed["direct_digest_count"] == 22
    assert sealed["helper_source"] == {
        "filename": "q011o_graph_transform_setup.py",
        "sha256": q011y.Q011O_SOURCE_SHA256,
    }
    assert all(sealed["checks"].values())
    assert tuple(sealed["q011k"]["digests"]) == q011y.Q011K_DIGESTS
    assert tuple(sealed["q011l"]["digests"]) == q011y.Q011L_DIGESTS
    assert tuple(sealed["q011u"]["digests"]) == q011y.Q011U_DIGESTS
    assert tuple(sealed["q011x"]["digests"]) == q011y.Q011X_DIGESTS


def test_q011y_proves_the_transformed_residual_inclusion(
    q011y_cycle: dict[str, Any],
) -> None:
    theorem = q011y_cycle["transformed_residual_theorem_audit"]
    assert theorem["passed"]
    assert all(theorem["checks"].values())
    assert theorem["finite_block_dimensions"] == {
        "block_0": 150,
        "blocks_1_through_16": 153,
    }
    assert theorem["literature_basis"]["original_paper"] == ("http://eudml.org/doc/131452")
    assert theorem["matrix_identity"] == ("V^{-1} A V = D + V^{-1}(A V - V D)")
    assert theorem["gershgorin_consequence"] == (
        "spectrum(A) is contained in the union over j of D(d_j, theta)"
    )


def test_q011y_reconstructs_contained_radii_with_registered_improvement(
    q011y_cycle: dict[str, Any],
) -> None:
    audit = q011y_cycle["exact_radius_refinement_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["representative_block_count"] == 9
    assert audit["transported_conjugate_block_count"] == 8
    assert audit["maximum_refined_radius_block"] == 4
    assert audit["minimum_improvement_ratio_block"] == 8
    assert q011y._fraction(audit["maximum_refined_radius_upper"]) == pytest.approx(
        4.7369170150175137e-8
    )
    assert q011y._fraction(audit["minimum_old_to_refined_improvement_ratio"]) == (
        pytest.approx(370.0132423109111)
    )
    assert q011y._fraction(audit["maximum_refined_radius_upper"]) <= (q011y.MAXIMUM_REFINED_RADIUS)
    assert (
        q011y._fraction(audit["minimum_old_to_refined_improvement_ratio"])
        >= q011y.MINIMUM_IMPROVEMENT_RATIO
    )
    assert all(
        record["exact_radius_identity_reproduces"]
        for record in audit["representative_block_records"]
    )


def test_q011y_checks_all_2598_disc_containments_and_stability(
    q011y_cycle: dict[str, Any],
) -> None:
    audit = q011y_cycle["all_eigendisc_containment_audit"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["eigendisc_count"] == 2598
    assert audit["unique_center_modulus_evaluation_count"] == 2597
    assert audit["selected_eigendisc_count"] == 24
    assert audit["external_eigendisc_count"] == 2574
    assert audit["maximum_refined_modulus_witness"] == {
        "block_index": 0,
        "center_index": 147,
    }
    assert audit["framed_exact_eigendisc_digest_sha256"] == (
        "7421634849c0f732045e576793863f758a09bddf6ab70205bfbd3aca45f9f18b"
    )
    maximum = q011y._fraction(audit["maximum_refined_modulus_upper"])
    assert maximum == pytest.approx(0.9920954876550118)
    assert maximum <= q011y.MAXIMUM_REFINED_MODULUS_UPPER < 1


def test_q011y_clears_only_the_fixed_degree_six_witness(
    q011y_cycle: dict[str, Any],
) -> None:
    witness = q011y_cycle["first_degree_six_witness_audit"]
    assert witness["passed"]
    assert all(witness["checks"].values())
    assert witness["degree"] == 6
    assert witness["overlap_selected_type_counts"] == [0, 2, 2, 2]
    assert witness["output_block"] == 15
    assert witness["target_identifier"] == "block=15;center=148"
    assert q011y._fraction(witness["old_separation_margin_upper"]) < 0
    refined_margin = q011y._fraction(witness["refined_separation_margin_lower"])
    assert refined_margin == pytest.approx(4.72250069801592e-5)
    assert refined_margin >= Fraction(4, 10**5)


def test_q011y_accepts_without_overclaiming_degree_six_or_ssm(
    q011y_cycle: dict[str, Any],
) -> None:
    assert all(gate["passed"] for gate in q011y_cycle["validity_gates"].values())
    assert all(gate["passed"] for gate in q011y_cycle["hypothesis_gates"].values())
    assert q011y_cycle["study_validity"] == "passed"
    assert q011y_cycle["hypothesis_outcome"] == "accepted"
    assert q011y_cycle["scientific_classification"] == q011y.ACCEPTED_CLASSIFICATION
    theorem = q011y_cycle["theorem_consequence"]
    assert theorem["transformed_residual_eigendisc_inclusion_is_certified"]
    assert theorem["all_refined_discs_are_contained_in_q011k_discs"]
    assert theorem["all_2598_refined_eigendiscs_are_strictly_stable"]
    assert theorem["first_degree_six_enclosure_obstruction_is_cleared"]
    assert not theorem["all_degree_six_external_nonresonances_are_certified"]
    assert not theorem["degrees_7_through_90_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "other 6955" in q011y_cycle["claim_boundary"]
    assert "Q011z" in q011y_cycle["next_change"]


def test_q011y_cycle_has_reproducible_strict_json_digests(
    q011y_cycle: dict[str, Any],
) -> None:
    json.dumps(q011y_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": ("a31fe1606f7be3931567ec63bbad3037d38a9a57eef43f73d7b8f9afc7523c03"),
        "theorem_digest_sha256": (
            "f3b9518fe67e85f0e701c4e6a97eac95db188ce85f813e358ddc0ecf85ba1ad5"
        ),
        "radius_digest_sha256": (
            "70919d4697068d7500609551a17325533e83f40bb2e309f5e98b3313a6a93ee5"
        ),
        "containment_digest_sha256": (
            "54e13cb993a0b99bc2d85dcf687d470cebe5692b4d10ab03865115230c53712c"
        ),
        "witness_digest_sha256": (
            "933d2841e5501bd48827ead0ea836fb54ebca7f42e36f8bc6228c3f7dcfaaa4b"
        ),
        "result_digest_sha256": (
            "51d83bad9b0c2188c05b147f0075b5e7f05f3dea0dd291e0c282e9236914bff8"
        ),
    }
    assert {name: q011y_cycle[name] for name in expected} == expected
    assert q011y_cycle["result_digest_sha256"] == (
        q011y.q011b._canonical_json_sha256(q011y._result_digest_sections(q011y_cycle))
    )


def test_q011y_study_metadata_is_strict_and_scoped() -> None:
    study = q011y.run_q011y_study()
    assert study["schema_version"] == 1
    assert study["source"] == source_metadata()
    assert study["study_gate"] == "passed"
    assert study["scientific_outcome"] == "accepted"
    assert study["arithmetic_runtime"]["floating_point_used_for_gate_decisions"] is False
    assert study["mathematical_scope"]["refined_linear_eigendisc_claim"] is True
    assert study["mathematical_scope"]["complete_degree_six_nonresonance_claim"] is False
    assert study["mathematical_scope"]["ssm_uniqueness_claim"] is False
    json.dumps(study, allow_nan=False)


def test_q011y_artifact_records_the_refinement_if_generated() -> None:
    runner_path = Path(q011y.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011y_transformed_residual_eigendiscs.json"
    if not artifact_path.exists():
        pytest.skip("Q011y artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == ("q011y_transformed_residual_eigendiscs.py")
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["scientific_classification"] == q011y.ACCEPTED_CLASSIFICATION
    assert cycle["result_digest_sha256"] == (
        q011y.q011b._canonical_json_sha256(q011y._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
