from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011q_real_frame_setup as q011q
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011q_cycle() -> dict[str, Any]:
    return q011q.run_real_frame_setup_audit()


def test_q011q_seals_six_direct_inputs_and_preserves_prior_outcomes(
    q011q_cycle: dict[str, Any],
) -> None:
    audit = q011q_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 29
    assert {
        label: audit[label]["hypothesis_outcome"]
        for label in ("q011j", "q011k", "q011l", "q011m", "q011o", "q011p")
    } == {
        "q011j": "accepted",
        "q011k": "accepted",
        "q011l": "accepted",
        "q011m": "accepted",
        "q011o": "rejected",
        "q011p": "accepted",
    }
    assert audit["checks"]["q011o_unique_typing_rejection_is_preserved"]
    assert audit["checks"]["q011p_reality_and_claim_boundary_are_preserved"]
    assert audit["checks"]["nested_seals_reproduce_but_are_not_substituted"]


def test_q011q_graph_coordinate_conjugation_closes_with_directed_error(
    q011q_cycle: dict[str, Any],
) -> None:
    audit = q011q_cycle["graph_coordinate_conjugation_audit"]
    reconstruction = audit["zero_block_reconstruction"]
    epsilon_j = _fraction(audit["q011p_conjugation_error_upper"])
    epsilon_f = _fraction(audit["primary_point_product_error_upper"])
    j_se = _fraction(audit["q011p_actual_j_se_upper"])
    graph_radius = _fraction(audit["q011l_graph_radius_upper"])

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["containment_checks"].values())
    assert reconstruction["zero_block_dimension"] == 150
    assert reconstruction["selected_dimension"] == 6
    assert reconstruction["external_dimension"] == 144
    assert audit["point_product_used_for_seed_proposal_only"]
    assert audit["point_product_sha256"] == (
        "03da151ccca29b11bc9a4be7f28278b5b7cc496d0e07e62afd0b4b475029aeee"
    )
    assert _fraction(
        audit["primary_graph_conjugation_block_error_upper"]
    ) == epsilon_j + epsilon_f + j_se * graph_radius
    assert len(audit["algebraic_identities"]) == 6


@pytest.mark.parametrize(
    ("label", "dimension", "hashes"),
    [
        (
            "selected",
            6,
            (
                "34a6b7525019c3a9ca247a52a93c4d35f0a8185fd002f18ef71f973d21f1a118",
                "dff9444f0fb1e6b11a876368f7cffcc36ba2455a5f1db65288a005b110d06c8d",
                "1d437e95b8d396ed845ee8426e59ebd81b61aa73f437331805f7992f48fd7af4",
                "a648456c3c82027d933873c5a2d59e5264648b5f5133d12eef6ebb8cbd7a04df",
            ),
        ),
        (
            "external",
            144,
            (
                "2a2ec4620047646cbebc718211119c2508b7ef5b05facfdaa677333f83f7bc5b",
                "4919adf4f674918789bea52fda01305a2c9611c7e8440f5c8e24c5655369b451",
                "ad4e293480c6c1c75edae7ea5907f5d838e4992fbab79b58293002fb9bbf5894",
                "c6652a75f58b854b88737498d5bf3fe55e51608be25b957c68343925b007fdd8",
            ),
        ),
    ],
)
def test_q011q_fixed_seed_frames_have_reproducible_inverse_proofs(
    q011q_cycle: dict[str, Any],
    label: str,
    dimension: int,
    hashes: tuple[str, str, str, str],
) -> None:
    conjugation = q011q_cycle["graph_coordinate_conjugation_audit"]
    family = q011q_cycle["symmetrized_real_frame_audit"]["frame_families"][
        label
    ]
    proof = family["primary_precision_proof"]
    replay = family["independent_containment_proof"]
    point_inverse = _fraction(proof["candidate_frame_inverse_norm_upper"])
    perturbation = _fraction(proof["actual_frame_perturbation_upper"])
    inverse_perturbation = _fraction(
        proof["actual_inverse_perturbation_upper"]
    )

    assert family["passed"]
    assert family["dimension"] == dimension
    assert family["pivot_audit"]["pivot_count"] == dimension
    assert len(set(family["pivot_audit"]["pivot_indices"])) == dimension
    assert all(family["checks"].values())
    assert all(family["containment_checks"].values())
    assert proof["passed"] and replay["passed"]
    assert proof["precision_bits"] == 256
    assert replay["precision_bits"] == 192
    assert (
        family["pivot_audit"]["pivot_indices_sha256"],
        family["candidate_frame_exact_sha256"],
        family["candidate_frame_binary64_sha256"],
        family["inverse_candidate_sha256"],
    ) == hashes
    assert perturbation == (
        _fraction(conjugation["primary_graph_conjugation_block_error_upper"])
        * family["seed_matrix_norm"]
    )
    assert inverse_perturbation == point_inverse * perturbation
    assert _fraction(proof["actual_frame_inverse_norm_upper"]) == (
        point_inverse / (1 - inverse_perturbation)
    )


def test_q011q_real_frames_and_section_give_a_six_plus_144_direct_sum(
    q011q_cycle: dict[str, Any],
) -> None:
    audit = q011q_cycle["symmetrized_real_frame_audit"]
    j_se = _fraction(
        q011q_cycle["graph_coordinate_conjugation_audit"][
            "q011p_actual_j_se_upper"
        ]
    )

    assert audit["passed"]
    assert all(audit["direct_sum_checks"].values())
    assert audit["zero_block_selected_real_dimension"] == 6
    assert audit["zero_block_external_real_dimension"] == 144
    assert audit["zero_block_total_real_dimension"] == 150
    assert _fraction(audit["section_norm_upper"]) == j_se / 2
    assert audit["algebraic_identities"]["canonical_real_section"] == (
        "H(e)=K_SE conjugate(e)/2"
    )


def test_q011q_reissues_the_fixed_leaf_coordinate_as_a_real_direct_sum(
    q011q_cycle: dict[str, Any],
) -> None:
    audit = q011q_cycle["real_fixed_leaf_coordinate_audit"]
    section = _fraction(audit["section_norm_upper"])
    old_lift = _fraction(audit["q011o_physical_lift_norm_upper"])
    old_zero_lift = _fraction(audit["q011o_zero_lift_contribution"])
    real_zero_lift = _fraction(audit["real_zero_lift_contribution"])
    old_zero_inverse = _fraction(audit["q011o_zero_inverse_contribution"])

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["coordinate_definition"]["real_coefficient_frames_are_explicit"]
    assert not audit["cross_block_cancellation_used"]
    assert (audit["selected_real_dimension"], audit["external_real_dimension"]) == (
        24,
        2574,
    )
    assert audit["total_fixed_leaf_real_dimension"] == 2598
    assert real_zero_lift == old_zero_lift * (1 + section)
    assert _fraction(audit["real_physical_lift_norm_upper"]) == (
        old_lift - old_zero_lift + real_zero_lift
    )
    assert _fraction(audit["real_zero_inverse_contribution"]) == (
        old_zero_inverse * (1 + section)
    )


def test_q011q_same_norm_real_linear_bounds_are_strictly_dominated(
    q011q_cycle: dict[str, Any],
) -> None:
    audit = q011q_cycle["real_same_norm_linear_split_audit"]
    selected_operator = _fraction(audit["zero_selected_operator_norm_upper"])
    external_zero = _fraction(audit["zero_external_operator_norm_upper"])
    old_coupling = _fraction(audit["q011o_zero_coupling_upper"])
    section = _fraction(audit["section_norm_upper"])
    selected_conorm = _fraction(audit["real_selected_conorm_lower"])
    external_norm = _fraction(audit["real_external_operator_norm_upper"])

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert _fraction(audit["real_zero_coupling_upper"]) == (
        old_coupling + (selected_operator + external_zero) * section
    )
    assert _fraction(audit["real_linear_domination_gap_lower"]) == (
        selected_conorm - external_norm
    )
    assert _fraction(audit["real_linear_domination_ratio_upper"]) == (
        external_norm / selected_conorm
    )
    assert _fraction(audit["real_selected_base_inverse_norm_upper"]) == (
        1 / selected_conorm
    )
    assert selected_conorm >= Fraction(983, 1000)
    assert external_norm <= Fraction(491, 500)
    assert _fraction(audit["real_linear_domination_gap_lower"]) >= Fraction(
        1, 1000
    )
    assert _fraction(audit["real_selected_external_coupling_upper"]) <= Fraction(
        1, 10**6
    )


def test_q011q_radial_localization_is_real_typed_and_defers_nonlinearity(
    q011q_cycle: dict[str, Any],
) -> None:
    audit = q011q_cycle["real_localized_graph_space_audit"]
    cutoff = audit["cutoff"]
    localized = audit["localized_map"]
    graph_space = audit["real_graph_banach_space"]
    radius = _fraction(audit["localization_radius"])
    lift = _fraction(
        q011q_cycle["real_fixed_leaf_coordinate_audit"][
            "real_physical_lift_norm_upper"
        ]
    )

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert radius == Fraction(1, 10**11)
    assert _fraction(audit["real_physical_localization_upper"]) == lift * radius
    assert _fraction(cutoff["global_lipschitz_constant_upper"]) == 2
    assert cutoff["preserves_selected_real_fixed_space"]
    assert cutoff["preserves_external_real_fixed_space"]
    assert not cutoff["uses_q011o_componentwise_complex_disk_projection"]
    assert localized["equals_original_map_on_core_ball"]
    assert graph_space["closed_complete_space"]
    assert not localized["nonlinear_derivative_bound_certified"]
    assert not graph_space["induced_graph_transform_is_defined_in_this_gate"]
    assert not graph_space["graph_transform_self_map_is_certified"]
    assert not graph_space["graph_transform_contraction_is_certified"]


def test_q011q_accepts_every_registered_gate_and_preserves_claim_boundary(
    q011q_cycle: dict[str, Any],
) -> None:
    theorem = q011q_cycle["theorem_consequence"]

    assert q011q_cycle["study_validity"] == "passed"
    assert q011q_cycle["hypothesis_outcome"] == "accepted"
    assert q011q_cycle["scientific_classification"] == (
        "the repaired fixed-leaf split admits a certified real-frame "
        "localized graph-transform setup"
    )
    assert len(q011q_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011q_cycle["validity_gates"].values())
    assert len(q011q_cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"] for gate in q011q_cycle["hypothesis_gates"].values()
    )
    assert q011q_cycle["failed_hypothesis_order"] == []
    assert theorem["fixed_seed_zero_block_selected_real_frame_is_certified"]
    assert theorem["fixed_seed_zero_block_external_real_frame_is_certified"]
    assert theorem["zero_block_real_direct_sum_and_section_are_certified"]
    assert theorem["fixed_leaf_real_coordinate_lift_and_inverse_are_certified"]
    assert theorem["registered_same_norm_real_linear_domination_is_rigorous"]
    assert theorem["radial_cutoff_and_real_graph_space_are_type_correct"]
    assert not theorem["q011o_historical_rejection_is_changed"]
    assert not theorem["a_nonlinear_graph_transform_is_defined_or_certified"]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_certified"]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_disproved"]
    assert "nonlinear derivative bound" in q011q_cycle["claim_boundary"]


def test_q011q_cycle_has_reproducible_strict_json_digests(
    q011q_cycle: dict[str, Any],
) -> None:
    json.dumps(q011q_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "c9e57c60fe678901c5502bf163d7317c06fedb35322e8591e741c330969829b5"
        ),
        "conjugation_digest_sha256": (
            "583a28e1453b75700d0674bf090c4f8c0652d7538f84bef7c8ea7e09415db54e"
        ),
        "frame_digest_sha256": (
            "1210f4d2c85d4a0cad9978531b297b5e493bac5f8d54d5eafa6ee7a5a68a6d7b"
        ),
        "setup_digest_sha256": (
            "ec52daadd80261b9e94672beb979fd5f01e4f1c4bc0e63090a0cccbb90cda26b"
        ),
        "result_digest_sha256": (
            "274ddd32b50000c953c623285993ba533651a720c6dc79ae693a0e24a3f623ae"
        ),
    }
    assert {name: q011q_cycle[name] for name in expected} == expected
    assert q011q_cycle["result_digest_sha256"] == (
        q011q.q011b._canonical_json_sha256(
            q011q._result_digest_sections(q011q_cycle)
        )
    )


def test_q011q_artifact_records_the_real_frame_setup_certificate() -> None:
    runner_path = Path(q011q.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011q_real_frame_setup.json"
    if not artifact_path.exists():
        pytest.skip("Q011q artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "776be2af80fdbb867fd72eb3c0bdfe82ca30f5fa50bc9436818df5c7f87e676d"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011q_real_frame_setup.py",
        "sha256": "83031650f7ecd54adb048a74ace2df96068317531aeb84fb57b9f797b9e33f67",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == (
        q011q.q011b._canonical_json_sha256(
            q011q._result_digest_sections(cycle)
        )
    )
    json.dumps(artifact, allow_nan=False)
