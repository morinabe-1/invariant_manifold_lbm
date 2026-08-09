from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q011o_graph_transform_setup as q011o
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011o_cycle() -> dict[str, object]:
    return q011o.run_graph_transform_setup_audit()


def test_q011o_seals_all_four_direct_inputs_and_claim_boundaries() -> None:
    audit, artifacts = q011o._sealed_input_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert set(artifacts) == {"q011k", "q011l", "q011m", "q011n"}
    assert artifacts["q011k"]["cycle"]["hypothesis_outcome"] == "accepted"
    assert artifacts["q011l"]["cycle"]["hypothesis_outcome"] == "accepted"
    assert artifacts["q011m"]["cycle"]["hypothesis_outcome"] == "accepted"
    assert artifacts["q011n"]["cycle"]["hypothesis_outcome"] == "not_ready"
    assert audit["checks"][
        "q011n_nested_seals_reproduce_but_are_not_substituted"
    ]


def test_q011o_coordinate_audit_closes_dimensions_and_exact_bounds(
    q011o_cycle: dict[str, object],
) -> None:
    audit = q011o_cycle["fixed_leaf_coordinate_audit"]
    records = audit["block_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(records) == 17
    assert records[0]["dimension"] == 150
    assert records[0]["selected_dimension"] == 6
    assert records[0]["population_lift_factor"] == 186
    assert all(record["dimension"] == 153 for record in records[1:])
    assert all(record["population_lift_factor"] == 1 for record in records[1:])
    assert audit["total_fixed_leaf_real_dimension"] == 2598
    assert audit["selected_real_dimension"] == 24
    assert audit["external_real_dimension"] == 2574
    assert _fraction(audit["physical_lift_norm_upper"]) == sum(
        (_fraction(record["physical_lift_contribution"]) for record in records),
        start=Fraction(0),
    )
    assert _fraction(audit["coordinate_inverse_norm_upper"]) == max(
        _fraction(record["coordinate_inverse_contribution"])
        for record in records
    )
    assert audit["coordinate_inverse_witness_block"] == 13
    assert not audit["cross_block_cancellation_used"]


def test_q011o_isolates_the_zero_block_real_typing_obstruction(
    q011o_cycle: dict[str, object],
) -> None:
    checks = q011o_cycle["fixed_leaf_coordinate_audit"]["conjugacy_checks"]

    assert checks == {
        "all_nonzero_center_families_are_exact_conjugates": True,
        "all_nonzero_metric_families_are_exact_conjugates": True,
        "selected_one_and_sixteen_indices_match": True,
        "selected_one_and_sixteen_graph_bounds_match": True,
        "zero_selected_multiset_is_closed_under_conjugacy": False,
    }


def test_q011o_same_norm_linear_bounds_reproduce_exactly(
    q011o_cycle: dict[str, object],
) -> None:
    audit = q011o_cycle["same_norm_linear_split_audit"]
    records = audit["block_records"]
    selected = [
        record for record in records if record["selected_conorm_lower"] is not None
    ]
    selected_conorm = _fraction(audit["selected_conorm_lower"])
    external_norm = _fraction(audit["external_operator_norm_upper"])

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(records) == 17
    assert audit["exact_modulus_record_count"] == 2598
    assert [record["block_index"] for record in selected] == [0, 1, 16]
    assert selected_conorm == min(
        _fraction(record["selected_conorm_lower"]) for record in selected
    )
    assert external_norm == max(
        _fraction(record["external_operator_norm_upper"]) for record in records
    )
    assert _fraction(audit["linear_domination_gap_lower"]) == (
        selected_conorm - external_norm
    )
    assert _fraction(audit["linear_domination_ratio_upper"]) == (
        external_norm / selected_conorm
    )
    assert _fraction(audit["selected_base_inverse_norm_upper"]) == (
        1 / selected_conorm
    )
    assert audit["selected_conorm_witness_block"] == 1
    assert audit["selected_conorm_witness_center"] == 144
    assert audit["external_norm_witness_block"] == 0
    assert audit["external_norm_witness_center"] == 0
    assert audit["selected_external_coupling_witness_block"] == 0
    assert all(audit["conjugacy_checks"].values())
    assert not audit["q011k_eigenvalue_gap_used_as_operator_bound"]


def test_q011o_registered_numeric_caps_all_pass(
    q011o_cycle: dict[str, object],
) -> None:
    coordinate = q011o_cycle["fixed_leaf_coordinate_audit"]
    linear = q011o_cycle["same_norm_linear_split_audit"]
    localization = q011o_cycle["localized_graph_space_audit"]

    assert _fraction(coordinate["physical_lift_norm_upper"]) <= Fraction(2600)
    assert _fraction(coordinate["coordinate_inverse_norm_upper"]) <= Fraction(900)
    assert _fraction(localization["physical_localization_upper"]) <= Fraction(
        3, 10**8
    )
    assert _fraction(linear["selected_conorm_lower"]) >= Fraction(983, 1000)
    assert _fraction(linear["external_operator_norm_upper"]) <= Fraction(491, 500)
    assert _fraction(linear["linear_domination_gap_lower"]) >= Fraction(1, 1000)
    assert _fraction(linear["linear_domination_ratio_upper"]) <= Fraction(999, 1000)
    assert _fraction(linear["selected_base_inverse_norm_upper"]) <= Fraction(51, 50)
    assert _fraction(linear["selected_external_coupling_upper"]) <= Fraction(
        1, 10**6
    )


def test_q011o_localization_is_typed_without_a_nonlinear_claim(
    q011o_cycle: dict[str, object],
) -> None:
    audit = q011o_cycle["localized_graph_space_audit"]
    coordinate = q011o_cycle["fixed_leaf_coordinate_audit"]
    cutoff = audit["cutoff"]
    localized_map = audit["localized_map"]
    graph_space = audit["graph_banach_space"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert _fraction(audit["localization_radius"]) == Fraction(1, 10**11)
    assert _fraction(audit["physical_localization_upper"]) == (
        _fraction(coordinate["physical_lift_norm_upper"]) / 10**11
    )
    assert cutoff["identity_on_core_ball"]
    assert cutoff["preserves_complex_conjugacy"]
    assert _fraction(cutoff["global_lipschitz_constant"]) == 1
    assert localized_map["equals_original_map_on_core_ball"]
    assert not localized_map["nonlinear_derivative_bound_certified"]
    assert graph_space["closed_complete_space"]
    assert not graph_space["induced_graph_transform_is_defined_in_this_gate"]
    assert not graph_space["graph_transform_self_map_is_certified"]
    assert not graph_space["graph_transform_contraction_is_certified"]


def test_q011o_validly_rejects_only_the_registered_real_coordinate(
    q011o_cycle: dict[str, object],
) -> None:
    assert q011o_cycle["study_validity"] == "passed"
    assert q011o_cycle["hypothesis_outcome"] == "rejected"
    assert q011o_cycle["scientific_classification"] == (
        "the registered block-sup norm does not support the localized "
        "graph-transform setup"
    )
    assert len(q011o_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011o_cycle["validity_gates"].values())
    assert len(q011o_cycle["hypothesis_gates"]) == 5
    assert q011o_cycle["failed_hypothesis_order"] == [
        "fixed_leaf_triangular_coordinate_is_bijective_and_real_typed"
    ]
    assert not q011o_cycle["hypothesis_gates"][
        "fixed_leaf_triangular_coordinate_is_bijective_and_real_typed"
    ]["passed"]
    assert all(
        gate["passed"]
        for name, gate in q011o_cycle["hypothesis_gates"].items()
        if name != "fixed_leaf_triangular_coordinate_is_bijective_and_real_typed"
    )


def test_q011o_preserves_the_claim_boundary(
    q011o_cycle: dict[str, object],
) -> None:
    theorem = q011o_cycle["theorem_consequence"]

    assert not theorem["fixed_leaf_fourier_eigen_graph_coordinate_is_type_correct"]
    assert not theorem["registered_same_norm_linear_domination_is_rigorous"]
    assert not theorem["nonlinear_graph_transform_is_well_defined"]
    assert not theorem["nonlinear_graph_transform_is_a_self_map_or_contraction"]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_certified"]
    assert not theorem["an_exact_local_invariant_manifold_or_ssm_is_disproved"]
    assert not theorem["q011l_q011m_or_q011n_outcome_is_changed"]
    assert "exact invariant manifold or SSM" in q011o_cycle["claim_boundary"]


def test_q011o_cycle_has_reproducible_strict_json_digests(
    q011o_cycle: dict[str, object],
) -> None:
    json.dumps(q011o_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "0bddd90fc21a745b910ff47e133e72045842c77b589a818a21e946f85ba63da0"
        ),
        "coordinate_digest_sha256": (
            "6c00ce5d9df986830a4ad2d98df3970417d47e4fb9f1784364ce32b64d7396b7"
        ),
        "linear_digest_sha256": (
            "f9aaea144b0e79c6adf42296b7e8dcd562f2b75525b6abf4ac99c43dcbd1859c"
        ),
        "localization_digest_sha256": (
            "5799e9997ac1ec692ddce97465174204ee22debaea942ed7fab637209c912e0d"
        ),
        "result_digest_sha256": (
            "6ec0a97c1b3d653e5edd3ffc7f4b8b9fa746e86e8d706e251753eecb8ab9a864"
        ),
    }
    assert {name: q011o_cycle[name] for name in expected} == expected
    assert q011o_cycle["result_digest_sha256"] == (
        q011o.q011b._canonical_json_sha256(
            q011o._result_digest_sections(q011o_cycle)
        )
    )


def test_q011o_artifact_records_the_valid_rejection() -> None:
    runner_path = Path(q011o.__file__).resolve()
    artifact_path = (
        runner_path.parent / "artifacts" / "q011o_graph_transform_setup.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011o artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "bbbc26939d4ef73aae95ad6517f5f1549f2eaf7b6edcbac5e5171f329064bc07"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011o_graph_transform_setup.py",
        "sha256": "60d9c445dace16d114e46263f2b47fe2db993b894337cdd462f204da09543f1f",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "rejected"
    assert cycle["result_digest_sha256"] == (
        q011o.q011b._canonical_json_sha256(q011o._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
