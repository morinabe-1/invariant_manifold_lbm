from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q011n_correction_readiness as q011n
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011n_cycle() -> dict[str, object]:
    return q011n.run_correction_readiness_audit()


def test_q011n_seals_q011k_q011l_and_q011m() -> None:
    audit, q011k_artifact, q011l_artifact, q011m_artifact = (
        q011n._sealed_input_audit()
    )

    assert audit["passed"]
    assert all(audit["checks"].values())
    for artifact in (q011k_artifact, q011l_artifact, q011m_artifact):
        assert artifact["cycle"]["study_validity"] == "passed"
        assert artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert not q011m_artifact["cycle"]["theorem_consequence"][
        "finite_cubic_defect_implies_exact_invariance"
    ]
    assert not q011m_artifact["cycle"]["theorem_consequence"][
        "an_exact_invariant_manifold_or_forced_ssm_exists"
    ]


def test_q011n_distinguishes_the_degree_two_operator_from_the_function_defect(
    q011n_cycle: dict[str, object],
) -> None:
    audit = q011n_cycle["operator_typing_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["q011l_operator"] == {
        "name": "H_q^(2)(Z) = E_q Z - Z K_q(S)",
        "degree": 2,
        "total_monomial_columns": 300,
        "sector_pair_dimensions": {
            "0": 102,
            "1": 54,
            "16": 54,
            "2": 45,
            "15": 45,
        },
        "domain": "five external-by-degree-two-monomial matrix spaces",
        "codomain": "the same five external-by-degree-two-monomial matrix spaces",
    }
    assert audit["q011m_defect"]["minimum_degree"] == 3
    assert audit["invalid_unregistered_composition"] == (
        "(H^(2))^(-1) E^[2] is undefined"
    )
    assert audit["first_missing_proof_object"] == (
        "specified_a_posteriori_theorem"
    )
    assert audit["missing_proof_objects"] == [
        "specified_a_posteriori_theorem",
        "banach_function_space_and_norm",
        "full_linearized_invariance_inverse",
        "all_degree_or_analytic_tail_bound",
        "self_contained_graph_transform_contraction",
        "typed_defect_to_correction_map",
    ]


def test_q011n_inverse_surrogate_reproduces_but_is_not_a_function_inverse(
    q011n_cycle: dict[str, object],
) -> None:
    audit = q011n_cycle["inverse_surrogate_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert _fraction(audit["reconstructed_total_inverse_surrogate"]) == (
        186 * 3_400_000 + 2 * 24_000 + 2 * 2_300_000
    )
    assert _fraction(audit["q011m_observed_total_inverse_surrogate"]) == (
        q011n.TOTAL_INVERSE_SURROGATE
    )
    assert audit["checks"]["surrogate_is_not_typed_as_a_function_inverse"]


def test_q011n_scalar_surrogate_reuses_all_exact_q011m_records(
    q011n_cycle: dict[str, object],
) -> None:
    audit = q011n_cycle["scalar_correction_obstruction_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(audit["radius_records"]) == 8
    assert audit["passing_radius_count"] == 0
    assert audit["selected_radius"] is None
    assert audit["first_candidate_failed_constraints"] == [
        "formal_contraction_is_below_one_half",
        "formal_radii_inequality_is_strict",
        "correction_does_not_exceed_chart_state",
    ]
    assert audit["constraint_failure_counts"] == {
        "corrected_population_and_density_buffers_are_positive": 6,
        "corrected_state_is_in_derivative_domain": 7,
        "correction_does_not_exceed_chart_state": 8,
        "formal_contraction_is_below_one_half": 8,
        "formal_radii_inequality_is_strict": 8,
        "q011m_original_candidate_passed": 1,
    }


def test_q011n_first_scalar_record_reproduces_the_registered_formulas(
    q011n_cycle: dict[str, object],
) -> None:
    audit = q011n_cycle["scalar_correction_obstruction_audit"]
    record = audit["first_candidate_record"]
    displacement = _fraction(record["state_displacement_upper"])
    defect = _fraction(record["cubic_defect_upper"])
    variation = _fraction(record["derivative_variation_surrogate"])
    newton_y = _fraction(record["newton_y_surrogate"])
    contraction_z = _fraction(record["contraction_z_surrogate"])
    correction = _fraction(record["correction_radius_tau"])

    assert _fraction(record["radius"]) == Fraction(1, 10**14)
    assert variation == 145 * displacement + 2000 * displacement**2
    assert newton_y == q011n.TOTAL_INVERSE_SURROGATE * defect
    assert contraction_z == q011n.TOTAL_INVERSE_SURROGATE * variation
    assert correction == 2 * newton_y
    assert _fraction(record["state_with_correction_upper"]) == (
        displacement + correction
    )
    assert _fraction(record["radii_inequality_margin"]) == (
        correction - (newton_y + contraction_z * correction)
    )
    assert _fraction(record["correction_to_chart_state_utilization"]) == (
        correction / displacement
    )


def test_q011n_records_the_scalar_obstruction_without_overclaiming(
    q011n_cycle: dict[str, object],
) -> None:
    assert q011n_cycle["study_validity"] == "passed"
    assert q011n_cycle["hypothesis_outcome"] == "not_ready"
    assert q011n_cycle["scientific_classification"] == (
        "the registered Q011l/Q011m certificates are not sufficient for an "
        "a posteriori invariant-manifold proof"
    )
    assert len(q011n_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011n_cycle["validity_gates"].values())
    assert len(q011n_cycle["hypothesis_gates"]) == 5
    assert not any(
        gate["passed"] for gate in q011n_cycle["hypothesis_gates"].values()
    )
    theorem = q011n_cycle["theorem_consequence"]
    assert not theorem[
        "q011l_degree_two_inverse_and_q011m_function_defect_are_type_compatible"
    ]
    assert not theorem["registered_scalar_surrogate_closes_on_a_q011m_radius"]
    assert not theorem[
        "registered_inputs_are_ready_for_an_a_posteriori_manifold_proof"
    ]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_certified"]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_disproved"]
    assert not theorem["q011l_homological_inverse_acceptance_is_changed"]
    assert not theorem["q011m_quadratic_majorant_acceptance_is_changed"]


def test_q011n_cycle_has_reproducible_strict_json_digests(
    q011n_cycle: dict[str, object],
) -> None:
    json.dumps(q011n_cycle, allow_nan=False)
    assert q011n_cycle["input_digest_sha256"] == (
        "f916b59d1c9fba0e4ace57b110f4b960d5dce078578a77ac28f8a8d005e1e0d0"
    )
    assert q011n_cycle["typing_digest_sha256"] == (
        "e3952e5ac897ba9250f3a77ec5d8760c0f3ee2a3df350ba4451837a46dd91f76"
    )
    assert q011n_cycle["scalar_digest_sha256"] == (
        "ee7f21a6075963c510e234a032aa8de40f65989c609d10228aca54f6e371ed8d"
    )
    assert q011n_cycle["result_digest_sha256"] == (
        "9893aed4a7ce4d05cbd21e849de4ddd4f1c9f86c7fcc3fad7a4504b823d6a321"
    )
    assert q011n_cycle["result_digest_sha256"] == (
        q011n.q011b._canonical_json_sha256(
            q011n._result_digest_sections(q011n_cycle)
        )
    )


def test_q011n_artifact_records_the_not_ready_outcome() -> None:
    runner_path = Path(q011n.__file__).resolve()
    artifact_path = (
        runner_path.parent / "artifacts" / "q011n_correction_readiness.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011n artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "1277170b85d2f515a5b9dabbc1cf23cfdf36e109c5ab212e3a123ee07a50683b"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011n_correction_readiness.py",
        "sha256": "7e526dcf013efce628137023f69de7b929d31e52f19378cb05c483284e36dc57",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "not_ready"
    assert cycle["result_digest_sha256"] == (
        q011n.q011b._canonical_json_sha256(q011n._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
