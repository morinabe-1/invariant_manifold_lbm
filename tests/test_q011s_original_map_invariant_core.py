from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011s_original_map_invariant_core as q011s
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011s_cycle() -> dict[str, Any]:
    return q011s.run_original_map_invariant_core_audit()


def test_q011s_seals_four_direct_inputs_and_twenty_digests(
    q011s_cycle: dict[str, Any],
) -> None:
    audit = q011s_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 20
    assert {
        label: audit[label]["hypothesis_outcome"]
        for label in ("q011k", "q011l", "q011q", "q011r")
    } == {
        "q011k": "accepted",
        "q011l": "accepted",
        "q011q": "accepted",
        "q011r": "accepted",
    }
    assert audit["checks"][
        "q011k_spectral_claim_boundary_is_preserved"
    ]
    assert audit["checks"][
        "q011l_graph_and_inverse_claim_boundary_is_preserved"
    ]
    assert audit["checks"][
        "q011q_real_setup_claim_boundary_is_preserved"
    ]
    assert audit["checks"][
        "q011r_localized_fixed_graph_claim_boundary_is_preserved"
    ]


def test_q011s_reconstructs_all_selected_operator_upper_bounds(
    q011s_cycle: dict[str, Any],
) -> None:
    audit = q011s_cycle["selected_linear_operator_audit"]
    records = audit["block_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_blocks"] == [0, 1, 16]
    assert audit["selected_center_count"] == 24
    assert [record["selected_dimension"] for record in records] == [6, 9, 9]
    assert all(record["passed"] for record in records)
    for record in records:
        maximum = max(
            _fraction(center["modulus_upper"])
            for center in record["center_records"]
        )
        assert (
            _fraction(record["selected_operator_norm_upper"])
            == maximum
            + _fraction(record["triangular_selected_residual_upper"])
        )
    assert (
        _fraction(audit["global_selected_operator_norm_upper"])
        == max(
            _fraction(record["selected_operator_norm_upper"])
            for record in records
        )
    )
    assert audit["global_selected_operator_witness_block"] == 0
    assert (
        _fraction(records[1]["selected_operator_norm_upper"])
        == _fraction(records[2]["selected_operator_norm_upper"])
    )
    assert _fraction(
        audit["global_selected_operator_norm_upper"]
    ) <= Fraction(993, 1000)
    assert audit["exact_selected_center_record_digest_sha256"] == (
        "d948ea7ea2b84c0b4124a8bfca012dadbed0c7e4e81d8bf874967845336c3b4e"
    )
    assert audit["exact_selected_block_record_digest_sha256"] == (
        "2cb9a0dbf2ed73a6ea9e996b496adec8b5b7b3d3dd6b1be44d11a108f6756cfe"
    )


def test_q011s_uses_the_real_shear_only_for_the_coupling(
    q011s_cycle: dict[str, Any],
) -> None:
    audit = q011s_cycle["selected_linear_operator_audit"]

    assert audit["checks"][
        "q011q_real_shear_preserves_zero_selected_diagonal"
    ]
    assert audit["checks"]["q011q_real_coupling_is_used_directly"]
    assert audit["checks"][
        "same_complex_absolute_row_sum_norm_is_used"
    ]
    assert audit["checks"][
        "eigenvalue_only_conorm_or_external_bounds_are_not_substituted"
    ]
    assert _fraction(
        audit["real_selected_external_coupling_upper"]
    ) > 0


def test_q011s_reproduces_the_localized_fixed_graph_core_data(
    q011s_cycle: dict[str, Any],
) -> None:
    audit = q011s_cycle["localized_fixed_graph_core_data_audit"]
    graph = audit["localized_fixed_graph"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert graph["origin"] == "psi_*(0)=0"
    assert _fraction(graph["uniform_height_upper"]) == Fraction(
        3, 10**16
    )
    assert _fraction(graph["refined_lipschitz_upper"]) < 1
    assert _fraction(graph["refined_lipschitz_upper"]) <= Fraction(
        999, 1000
    )
    assert audit["fixed_leaf_selected_real_dimension"] == 24
    assert audit["fixed_leaf_external_real_dimension"] == 2574
    assert audit["checks"][
        "localized_fixed_graph_invariance_is_certified"
    ]
    assert audit["checks"][
        "q011q_cutoff_is_identity_on_the_core_ball"
    ]


def test_q011s_campaign_selects_the_full_registered_radius(
    q011s_cycle: dict[str, Any],
) -> None:
    audit = q011s_cycle[
        "original_map_invariant_core_campaign_audit"
    ]
    records = audit["core_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["monotonicity_checks"].values())
    assert len(records) == 11
    assert [record["passed"] for record in records] == [True] * 11
    assert audit["passing_scale_count"] == 11
    assert _fraction(audit["selected_scale"]) == 1
    assert _fraction(audit["selected_radius"]) == Fraction(3, 10**16)
    assert audit["first_failed_larger_radius"] is None
    assert audit["first_failed_larger_constraints"] == []
    assert audit["exact_core_record_digest_sha256"] == (
        "8f7aec78b72bcec3b7464a16c8bfd5940bdf63b7a20ea79b33d10b50207b1abf"
    )


def test_q011s_selected_core_reproduces_every_transfer_formula(
    q011s_cycle: dict[str, Any],
) -> None:
    linear = q011s_cycle["selected_linear_operator_audit"]
    graph = q011s_cycle["localized_fixed_graph_core_data_audit"]
    campaign = q011s_cycle[
        "original_map_invariant_core_campaign_audit"
    ]
    selected = campaign["selected_record"]
    data = graph["core_transfer_data"]

    radius = _fraction(selected["radius"])
    slope = _fraction(
        graph["localized_fixed_graph"]["refined_lipschitz_upper"]
    )
    p_selected = _fraction(
        linear["global_selected_operator_norm_upper"]
    )
    coupling = _fraction(
        data["real_selected_external_coupling_upper"]
    )
    mu_2 = _fraction(data["real_second_derivative_bilinear_upper"])
    lift = _fraction(data["real_physical_lift_norm_upper"])
    selected_ratio = _fraction(selected["selected_image_ratio_upper"])
    external_ratio = _fraction(selected["external_image_ratio_upper"])

    assert selected["passed"]
    assert all(selected["checks"].values())
    assert selected_ratio == (
        p_selected + coupling * slope + Fraction(1, 2) * mu_2 * radius
    )
    assert external_ratio == slope * selected_ratio
    assert _fraction(selected["selected_image_radius_upper"]) == (
        selected_ratio * radius
    )
    assert _fraction(selected["external_image_radius_upper"]) == (
        external_ratio * radius
    )
    assert _fraction(selected["input_physical_displacement_upper"]) == (
        lift * radius
    )
    assert _fraction(selected["output_physical_displacement_upper"]) == (
        lift * selected_ratio * radius
    )


def test_q011s_selected_core_has_registered_strict_margins(
    q011s_cycle: dict[str, Any],
) -> None:
    selected = q011s_cycle[
        "original_map_invariant_core_campaign_audit"
    ]["selected_record"]

    assert _fraction(selected["selected_image_ratio_upper"]) <= Fraction(
        999, 1000
    )
    assert _fraction(selected["external_image_ratio_upper"]) <= Fraction(
        999, 1000
    )
    assert _fraction(
        selected["input_physical_displacement_upper"]
    ) <= Fraction(1, 10**11)
    assert _fraction(
        selected["output_physical_displacement_upper"]
    ) <= Fraction(1, 10**11)
    assert _fraction(selected["input_population_floor_lower"]) >= Fraction(
        1, 50
    )
    assert _fraction(selected["output_population_floor_lower"]) >= Fraction(
        1, 50
    )
    assert _fraction(selected["input_density_floor_lower"]) >= Fraction(
        99, 100
    )
    assert _fraction(selected["output_density_floor_lower"]) >= Fraction(
        99, 100
    )


def test_q011s_accepts_only_the_forward_invariant_lipschitz_claim(
    q011s_cycle: dict[str, Any],
) -> None:
    theorem = q011s_cycle["theorem_consequence"]
    proof = q011s_cycle[
        "original_map_invariant_core_campaign_audit"
    ]["selected_core_transfer_proof"]

    assert q011s_cycle["study_validity"] == "passed"
    assert q011s_cycle["hypothesis_outcome"] == "accepted"
    assert q011s_cycle["scientific_classification"] == (
        "the original repaired exact map has a certified "
        "forward-invariant Lipschitz graph patch on the fixed "
        "conservation leaf"
    )
    assert len(q011s_cycle["validity_gates"]) == 7
    assert all(
        gate["passed"] for gate in q011s_cycle["validity_gates"].values()
    )
    assert len(q011s_cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"] for gate in q011s_cycle["hypothesis_gates"].values()
    )
    assert q011s_cycle["failed_hypothesis_order"] == []
    assert proof[
        "original_map_is_forward_invariant_by_induction"
    ]
    assert not proof["backward_invariance_or_onto_is_used"]
    assert theorem[
        "the_original_map_has_a_forward_invariant_lipschitz_graph_patch"
    ]
    assert theorem[
        "the_graph_patch_is_twenty_four_real_dimensional_on_the_fixed_leaf"
    ]
    assert theorem["all_forward_iterates_remain_in_the_certified_core"]
    assert not theorem["backward_invariance_or_onto_is_certified"]
    assert not theorem["c1_or_higher_smoothness_is_certified"]
    assert not theorem["origin_tangency_is_certified"]
    assert not theorem["spectral_quotient_ssm_uniqueness_is_certified"]
    assert not theorem["normal_attraction_or_a_basin_is_certified"]
    assert "no backward invariance" in q011s_cycle["claim_boundary"]


def test_q011s_cycle_has_reproducible_strict_json_digests(
    q011s_cycle: dict[str, Any],
) -> None:
    json.dumps(q011s_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "4808619d977f8d14c4f8b454e846558ad047337e4343c6b9bef791e2c2b99af5"
        ),
        "linear_digest_sha256": (
            "6a657463b847ce242346aea8b582f1f4e108b0abb0935e270a5c03c1ceb3cc36"
        ),
        "graph_digest_sha256": (
            "b9837d31b26bced4243457e3357a93c8d546883390104f1b43d5e182e92f98a7"
        ),
        "core_digest_sha256": (
            "ab837deb8459678d4fce223e06d03cc8e6f4d391ff35bad191392a923825e622"
        ),
        "result_digest_sha256": (
            "3e01d86f279bc6c5a2f0769a9728a98e3e49fa749be15a2c6c6e0f32132ca270"
        ),
    }
    assert {name: q011s_cycle[name] for name in expected} == expected
    assert q011s_cycle["result_digest_sha256"] == (
        q011s.q011b._canonical_json_sha256(
            q011s._result_digest_sections(q011s_cycle)
        )
    )


def test_q011s_artifact_records_the_original_map_core_certificate() -> None:
    runner_path = Path(q011s.__file__).resolve()
    artifact_path = (
        runner_path.parent
        / "artifacts"
        / "q011s_original_map_invariant_core.json"
    )
    if not artifact_path.exists():
        pytest.skip("Q011s artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "d7399671504cc513aecc491210108c31365c63a74864ecf04e629b3d1348bc52"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011s_original_map_invariant_core.py",
        "sha256": (
            "beeeb6699b5c3a7e7636b2c7afd6036bc6959213e81339f39961c325d9347367"
        ),
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == (
        q011s.q011b._canonical_json_sha256(
            q011s._result_digest_sections(cycle)
        )
    )
    json.dumps(artifact, allow_nan=False)
