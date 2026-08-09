from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q011l_interval_homological_inverse as q011l
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011l_cycle() -> dict[str, object]:
    return q011l.run_interval_homological_inverse_audit()


def test_q011l_seals_q011k_and_q011d() -> None:
    audit, q011k_artifact, q011d_artifact = q011l._sealed_input_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert q011k_artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert q011d_artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert not q011k_artifact["cycle"]["theorem_consequence"][
        "nonnormal_homological_inverse_is_certified"
    ]
    assert q011d_artifact["cycle"]["external_homological_block_audit"]["block_count"] == 300


def test_q011l_exact_eigencoordinate_bounds_reconstruct(
    q011l_cycle: dict[str, object],
) -> None:
    audit = q011l_cycle["exact_eigencoordinate_residual_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["block_count"] == 17
    assert audit["selected_block_dimensions"] == {"0": 6, "1": 9, "16": 9}
    assert len(audit["block_records"]) == 17
    for record in audit["block_records"]:
        assert _fraction(record["transformed_perturbation_upper"]) == (
            _fraction(record["beta_upper"]) * _fraction(record["family_residual_upper"])
        )
    for index in range(9, 17):
        left = audit["block_records"][index]
        right = audit["block_records"][17 - index]
        assert left["conjugated"]
        assert left["bauer_fike_radius_upper"] == right["bauer_fike_radius_upper"]
        assert left["transformed_perturbation_upper"] == right[
            "transformed_perturbation_upper"
        ]


def test_q011l_selected_invariant_graphs_are_rigorous(
    q011l_cycle: dict[str, object],
) -> None:
    audit = q011l_cycle["selected_invariant_graph_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["graph_blocks"] == [0, 1, 16]
    assert audit["maximum_graph_radius_block"] == 0
    assert _fraction(audit["maximum_graph_radius_upper"]) <= q011l.MAXIMUM_GRAPH_RADIUS
    assert _fraction(audit["maximum_self_map_utilization_upper"]) <= (
        q011l.MAXIMUM_GRAPH_UTILIZATION
    )
    assert _fraction(audit["maximum_contraction_upper"]) <= (
        q011l.MAXIMUM_GRAPH_CONTRACTION
    )
    for record in audit["block_records"]:
        assert record["passed"]
        assert all(record["checks"].values())
        h_value = _fraction(record["h_upper"])
        radius = _fraction(record["graph_radius_upper"])
        assert radius == 2 * h_value
        assert _fraction(record["self_map_bound_upper"]) <= radius
        assert _fraction(record["contraction_upper"]) < 1
        assert _fraction(record["selected_external_identification_margin_lower"]) > 0


def test_q011l_does_not_replace_the_external_quotient_by_full_space(
    q011l_cycle: dict[str, object],
) -> None:
    audit = q011l_cycle["full_space_substitution_obstruction_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["unsafe_pair_count"] == 8
    assert tuple(audit["unsafe_pair_indices"]) == q011l.EXPECTED_UNSAFE_PAIR_INDICES
    assert all(
        _fraction(record["selected_disc_margin_upper_test"]) <= 0
        for record in audit["unsafe_pair_records"]
    )


def test_q011l_quadratic_pair_family_is_complete(
    q011l_cycle: dict[str, object],
) -> None:
    audit = q011l_cycle["quadratic_pair_family_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_count"] == 24
    assert audit["unordered_pair_count"] == 300
    assert audit["sector_pair_counts"] == {
        "0": 102,
        "1": 54,
        "16": 54,
        "2": 45,
        "15": 45,
    }
    assert audit["external_comparison_count"] == 44_010
    assert audit["exact_base_pair_digest_sha256"] == (
        "e6068c78d608d765d77dcfdaa0efb0f15a24d941c45c2859e51482d4c70d83bf"
    )
    assert audit["reproduced_q011k_exact_pair_digest_sha256"] == (
        "be8548cd8ac4bea69b71b7bb0617f232ddcc9535d33b13279e371cc242cf2b79"
    )


def test_q011l_full_sector_homological_inverse_bounds_pass(
    q011l_cycle: dict[str, object],
) -> None:
    symmetric = q011l_cycle["symmetric_product_perturbation_audit"]
    audit = q011l_cycle["sector_homological_inverse_audit"]

    assert symmetric["passed"]
    assert all(symmetric["checks"].values())
    selected_scale = _fraction(symmetric["selected_center_complex_l1_upper"])
    selected_error = _fraction(symmetric["selected_dynamics_perturbation_upper"])
    assert _fraction(symmetric["symmetric_product_action_perturbation_upper"]) == (
        2 * selected_scale * selected_error + selected_error**2
    )
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["sector_order"] == [0, 1, 16, 2, 15]
    assert len(audit["sector_records"]) == 5
    assert audit["minimum_base_distance_sector"] == 0
    assert audit["minimum_base_distance_witness"] == {
        "pair_index": 173,
        "external_center_index": 143,
    }
    assert _fraction(audit["minimum_base_distance"]) >= (
        q011l.MINIMUM_BASE_HOMOLOGICAL_DISTANCE
    )
    assert _fraction(audit["maximum_neumann_quotient_upper"]) <= (
        q011l.MAXIMUM_NEUMANN_QUOTIENT
    )
    assert _fraction(audit["maximum_coordinate_inverse_bound"]) <= (
        q011l.MAXIMUM_COORDINATE_INVERSE_BOUND
    )
    assert _fraction(audit["maximum_ambient_lifted_inverse_bound"]) <= (
        q011l.MAXIMUM_AMBIENT_INVERSE_BOUND
    )
    assert audit["exact_sector_digest_sha256"] == (
        "6cfb130f45822becdca29ae6841e7c4069b03c670781501f94a59c0d2a5b2fc3"
    )
    for record in audit["sector_records"]:
        assert record["passed"]
        assert all(record["checks"].values())
        margin = _fraction(record["neumann_margin"])
        assert margin > 0
        assert _fraction(record["coordinate_inverse"]) == 1 / margin


def test_q011l_accepts_only_the_registered_inverse_theorem(
    q011l_cycle: dict[str, object],
) -> None:
    assert q011l_cycle["study_validity"] == "passed"
    assert q011l_cycle["hypothesis_outcome"] == "accepted"
    assert q011l_cycle["scientific_classification"] == (
        "the exact repaired selected/external split has a rigorously bounded "
        "quadratic homological inverse in the registered quotient norm"
    )
    assert len(q011l_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011l_cycle["validity_gates"].values())
    assert len(q011l_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011l_cycle["hypothesis_gates"].values())
    theorem = q011l_cycle["theorem_consequence"]
    assert theorem["exact_selected_invariant_graphs_are_certified"]
    assert theorem["all_five_quadratic_sector_homological_operators_are_invertible"]
    assert theorem["registered_coordinate_inverse_bound_is_rigorous"]
    assert theorem["registered_ambient_lifted_inverse_bound_is_rigorous"]
    assert not theorem["full_space_resolvent_substitution_is_valid_for_all_pairs"]
    assert not theorem["raw_q011b_map_is_certified"]
    assert not theorem["q011d_or_q011e_raw_coefficients_transfer_to_repaired_map"]
    assert not theorem["repaired_quadratic_jet_or_coefficients_are_certified"]
    assert not theorem["forced_ssm_exists_or_is_unique"]
    assert not theorem["nonlinear_normal_attraction_is_certified"]


def test_q011l_cycle_is_strict_json_with_reproducible_digests(
    q011l_cycle: dict[str, object],
) -> None:
    json.dumps(q011l_cycle, allow_nan=False)
    assert q011l_cycle["input_digest_sha256"] == (
        "1810f989a0328521e8b6d6ccbc2153cb9a945bb2c129c70d7b25a0c227fc7011"
    )
    assert q011l_cycle["graph_digest_sha256"] == (
        "a7d0f320fa7391c506f42853a94ede66fc73e81b004dfccda144028082cb8db3"
    )
    assert q011l_cycle["pair_digest_sha256"] == (
        "694cc2955bcef05df13ad30582f46f84bb627aaa7b336b5278e9b5139e29d377"
    )
    assert q011l_cycle["homological_digest_sha256"] == (
        "14d67f1d915aa3bd6bc34117562da4908e19036943e60fb638eddf6a42b20915"
    )
    assert q011l_cycle["result_digest_sha256"] == (
        "c372aa5962a7f3d0c83a126303a9e36e4f0830d113f9c49b922d03beb2f09a45"
    )
    assert q011l_cycle["result_digest_sha256"] == q011l.q011b._canonical_json_sha256(
        q011l._result_digest_sections(q011l_cycle)
    )


def test_q011l_artifact_records_the_homological_inverse_proof() -> None:
    runner_path = Path(q011l.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011l_interval_homological_inverse.json"
    if not artifact_path.exists():
        pytest.skip("Q011l artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "2878d8ebaaedc29990700ccac25b78185e0b6139dd371521f14602caf4514c0a"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011l_interval_homological_inverse.py",
        "sha256": "59234badf8c490b36f32ea79f2e3cc4c8399eadd4b5e7f35b9993fa1ba9dceb7",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == q011l.q011b._canonical_json_sha256(
        q011l._result_digest_sections(cycle)
    )
    json.dumps(artifact, allow_nan=False)
