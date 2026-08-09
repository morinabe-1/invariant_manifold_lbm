from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011p_zero_block_reality as q011p
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011p_cycle() -> dict[str, Any]:
    return q011p.run_zero_block_reality_audit()


def test_q011p_seals_all_four_direct_inputs_and_claim_boundaries(
    q011p_cycle: dict[str, Any],
) -> None:
    audit = q011p_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert {
        label: audit[label]["hypothesis_outcome"]
        for label in ("q011j", "q011k", "q011l", "q011o")
    } == {
        "q011j": "accepted",
        "q011k": "accepted",
        "q011l": "accepted",
        "q011o": "rejected",
    }
    assert audit["checks"][
        "q011o_valid_rejection_and_claim_boundary_are_preserved"
    ]
    assert audit["checks"][
        "q011o_nested_seals_reproduce_but_are_not_substituted"
    ]


def test_q011p_reconstructs_the_exactly_real_zero_block_and_q011l_graph(
    q011p_cycle: dict[str, Any],
) -> None:
    audit = q011p_cycle["zero_block_reconstruction_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["zero_block_dimension"] == 150
    assert audit["selected_dimension"] == 6
    assert audit["external_dimension"] == 144
    assert audit["selected_indices"] == list(range(144, 150))
    assert audit["actual_root_operator_family_is_exactly_real"]
    assert audit["external_indices_digest_sha256"] == (
        "a0eaa611c79879ac3b2fd6b96567f62acbe1e320826093c4eb9d218c25126fdc"
    )
    assert audit["proposal_sha256"] == (
        "a159d3328aa85c77da3c23e8b2e3726b6246c9b1a9fcab070de2531d705c48ca"
    )
    assert audit["eigenvalues_sha256"] == (
        "d7f5d03b69dc29fb52c10f22766ef761630728c5ed4f4860eb1c0dea48c9e2e2"
    )
    assert audit["eigenvectors_sha256"] == (
        "718ea52d421e7c75d4d5a92dafdba4df1a37eda2e168b7520aafe183e93b56a5"
    )
    assert audit["inverse_candidate_sha256"] == (
        "806522c57313f3534b4616db3fc610626cfba18e18b1dbc6f649b719b5b22511"
    )
    assert _fraction(audit["q011l_zero_graph_radius_upper"]) < Fraction(
        1, 10**5
    )


def test_q011p_directed_conjugation_bounds_reproduce_exact_formulas(
    q011p_cycle: dict[str, Any],
) -> None:
    audit = q011p_cycle["dual_precision_conjugation_audit"]
    proof = audit["primary_precision_proof"]
    epsilon = _fraction(proof["conjugation_point_error_upper"])
    defect = _fraction(proof["inverse_defect_infinity_norm_upper"])
    inverse_norm = _fraction(proof["inverse_candidate_infinity_norm_upper"])
    vector_norm = _fraction(proof["vector_infinity_norm_upper"])

    assert audit["passed"]
    assert proof["passed"]
    assert all(proof["checks"].values())
    assert proof["precision_bits"] == 256
    assert epsilon == defect * inverse_norm * vector_norm / (1 - defect)
    for name in ("J_EE", "J_ES", "J_SE", "J_SS"):
        assert _fraction(
            proof["actual_conjugation_block_norm_uppers"][name]
        ) == (
            _fraction(proof["point_conjugation_block_norm_uppers"][name])
            + epsilon
        )

    point_inverse = _fraction(proof["selected_point_inverse_norm_upper"])
    perturbation = _fraction(
        proof["selected_actual_inverse_perturbation_upper"]
    )
    actual_inverse = _fraction(proof["selected_actual_inverse_norm_upper"])
    selected_conorm = _fraction(proof["selected_actual_conorm_lower"])
    assert perturbation == point_inverse * epsilon
    assert actual_inverse == point_inverse / (1 - perturbation)
    assert selected_conorm == 1 / actual_inverse


def test_q011p_dual_precision_protocol_is_contained_and_fits_caps(
    q011p_cycle: dict[str, Any],
) -> None:
    audit = q011p_cycle["dual_precision_conjugation_audit"]
    primary = audit["primary_precision_proof"]
    replay = audit["independent_containment_proof"]
    actual = primary["actual_conjugation_block_norm_uppers"]

    assert primary["precision_bits"] == 256
    assert replay["precision_bits"] == 192
    assert primary["passed"] and replay["passed"]
    assert all(audit["containment_checks"].values())
    assert all(audit["q011k_reproduction_checks"].values())
    assert _fraction(primary["conjugation_point_error_upper"]) <= Fraction(
        1, 10**8
    )
    assert _fraction(actual["J_ES"]) <= Fraction(1, 10**6)
    assert _fraction(actual["J_EE"]) <= 100
    assert _fraction(actual["J_SE"]) <= 100
    assert _fraction(primary["selected_actual_inverse_norm_upper"]) <= 20


def test_q011p_conjugated_graph_and_expanded_uniqueness_formulas_close(
    q011p_cycle: dict[str, Any],
) -> None:
    conjugation = q011p_cycle["dual_precision_conjugation_audit"][
        "primary_precision_proof"
    ]
    blocks = conjugation["actual_conjugation_block_norm_uppers"]
    uniqueness = q011p_cycle["expanded_riccati_uniqueness_audit"]
    graph_radius = _fraction(uniqueness["q011l_graph_radius_upper"])
    h_value = _fraction(uniqueness["q011l_h_upper"])
    gap = _fraction(uniqueness["q011l_gap_lower"])
    radius = _fraction(uniqueness["expanded_reality_radius"])
    conorm = _fraction(conjugation["selected_actual_conorm_lower"])
    denominator = conorm - _fraction(blocks["J_SE"]) * graph_radius

    assert uniqueness["passed"]
    assert all(uniqueness["checks"].values())
    assert denominator == _fraction(
        uniqueness["conjugated_graph_denominator_lower"]
    )
    assert _fraction(uniqueness["conjugated_graph_radius_upper"]) == (
        _fraction(blocks["J_EE"]) * graph_radius
        + _fraction(blocks["J_ES"])
    ) / denominator
    assert _fraction(uniqueness["expanded_riccati_self_map_upper"]) == (
        h_value * (1 + 2 * radius + radius**2)
    )
    assert _fraction(uniqueness["expanded_riccati_contraction_upper"]) == (
        h_value * (2 + 2 * radius)
    )
    assert _fraction(
        uniqueness["expanded_spectral_identification_margin_lower"]
    ) == gap - 2 * h_value * gap * (1 + radius)
    assert graph_radius <= radius
    assert _fraction(uniqueness["conjugated_graph_radius_upper"]) <= radius
    assert _fraction(uniqueness["expanded_riccati_self_map_upper"]) <= radius
    assert _fraction(uniqueness["expanded_riccati_contraction_upper"]) < 1
    assert _fraction(
        uniqueness["expanded_spectral_identification_margin_lower"]
    ) > 0


def test_q011p_accepts_all_registered_validity_and_hypothesis_gates(
    q011p_cycle: dict[str, Any],
) -> None:
    assert q011p_cycle["study_validity"] == "passed"
    assert q011p_cycle["hypothesis_outcome"] == "accepted"
    assert q011p_cycle["scientific_classification"] == (
        "the Q011l zero-block selected invariant subspace is the "
        "complexification of a six-dimensional real invariant subspace"
    )
    assert len(q011p_cycle["validity_gates"]) == 7
    assert all(
        gate["passed"] for gate in q011p_cycle["validity_gates"].values()
    )
    assert len(q011p_cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"] for gate in q011p_cycle["hypothesis_gates"].values()
    )
    assert q011p_cycle["failed_hypothesis_order"] == []


def test_q011p_preserves_the_registered_claim_boundary(
    q011p_cycle: dict[str, Any],
) -> None:
    theorem = q011p_cycle["theorem_consequence"]

    assert theorem[
        "zero_block_selected_invariant_subspace_is_conjugation_invariant"
    ]
    assert theorem[
        "zero_block_selected_invariant_subspace_has_real_dimension_six"
    ]
    assert theorem[
        "zero_block_selected_invariant_subspace_is_a_real_complexification"
    ]
    assert not theorem["an_explicit_real_zero_block_frame_is_certified"]
    assert not theorem["q011o_real_typed_coordinate_rejection_is_changed"]
    assert not theorem[
        "a_conjugacy_equivariant_nonlinear_cutoff_is_certified"
    ]
    assert not theorem["a_nonlinear_graph_transform_or_fixed_graph_is_certified"]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_certified"]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_disproved"]
    assert "no explicit real frame" in q011p_cycle["claim_boundary"]


def test_q011p_cycle_has_reproducible_strict_json_digests(
    q011p_cycle: dict[str, Any],
) -> None:
    json.dumps(q011p_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "49a2df9f7f8db4ba95ebb93413324e667d2237a52a390e2e6f44b512c5fd953f"
        ),
        "conjugation_digest_sha256": (
            "087bcf415559cf0985194ad50dcbb0748ecdadda4df6b53ad7172f5b7cba1a05"
        ),
        "uniqueness_digest_sha256": (
            "41eee5097e7a0c2ea18ac79cd1b48abb1223d1925e953d7b2f34a4fb24777339"
        ),
        "result_digest_sha256": (
            "19edd32732a658a3811ebedc07a9a4483f1fff3d4a26ff64d7917ad2ea01c7f7"
        ),
    }
    assert {name: q011p_cycle[name] for name in expected} == expected
    assert q011p_cycle["result_digest_sha256"] == (
        q011p.q011b._canonical_json_sha256(
            q011p._result_digest_sections(q011p_cycle)
        )
    )


def test_q011p_artifact_records_the_zero_block_reality_certificate() -> None:
    runner_path = Path(q011p.__file__).resolve()
    artifact_path = (
        runner_path.parent / "artifacts" / "q011p_zero_block_reality.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011p artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "68968f8d01135fa3575a69c878b5ab89952ae39ec8e44b7fb398a3384f2fa6e1"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011p_zero_block_reality.py",
        "sha256": "fec9509068939663d6172539630f577383ad4da15f4c4575ef5caab7c65971f7",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == (
        q011p.q011b._canonical_json_sha256(
            q011p._result_digest_sections(cycle)
        )
    )
    json.dumps(artifact, allow_nan=False)
