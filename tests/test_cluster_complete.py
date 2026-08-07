from __future__ import annotations

import json

import pytest

from ttim_lbm.cluster_complete import (
    DIAGONAL_ACOUSTIC_SELF,
    audit_cluster_complete_condition,
    build_first_shell_cluster_blocks,
    run_cluster_complete_audit,
)
from ttim_lbm.coefficient_scaling import ACOUSTIC_SELF, SHEAR_DIAGONAL


@pytest.fixture(scope="module")
def cluster_audit() -> dict[str, object]:
    return run_cluster_complete_audit()


def test_registered_family_contains_every_first_shell_hydrodynamic_mode() -> None:
    blocks = build_first_shell_cluster_blocks(17, 1.2)
    expected_labels = {"shear", "acoustic_positive", "acoustic_negative"}
    waves = {block.wave_index for block in blocks}

    assert len(blocks) == 24
    assert sum(block.dimension for block in blocks) == 24
    assert waves == {
        (-1, -1),
        (-1, 0),
        (-1, 1),
        (0, -1),
        (0, 1),
        (1, -1),
        (1, 0),
        (1, 1),
    }
    assert all(
        {block.label for block in blocks if block.wave_index == wave}
        == expected_labels
        for wave in waves
    )


def test_unfiltered_reference_enumerates_the_registered_300_pairs() -> None:
    condition = audit_cluster_complete_condition(17, 1.2, 0.0)

    assert condition["selected_real_dimension"] == 24
    assert condition["pair_count"] == 300
    assert condition["target_pair_count"] == 16
    assert sum(condition["pair_status_counts"].values()) == 300
    assert condition["singular_classification_complete"]
    assert condition["condition_quantiles"]["maximum"] == pytest.approx(
        condition["maximum_condition_number"]
    )
    assert condition["maximum_structural_residual"] < 1.0e-10
    assert condition["maximum_solve_relative_residual"] < 1.0e-10
    assert condition["spectral"]["normal_dominance_gap"] < 0.0


def test_sealed_campaign_selects_the_first_viable_family(
    cluster_audit: dict[str, object],
) -> None:
    assert cluster_audit["study_validity"] == "passed"
    assert cluster_audit["hypothesis_outcome"] == "accepted"
    assert cluster_audit["scientific_classification"] == (
        "cluster-complete filtered finite-ladder prequalification passed"
    )
    assert len(cluster_audit["conditions"]) == 100
    assert len(cluster_audit["fits"]) == 40
    assert len(cluster_audit["families"]) == 20
    assert len(cluster_audit["viable_families"]) == 6
    assert all(
        gate["passed"] for gate in cluster_audit["validity_gates"].values()
    )

    selected = cluster_audit["selected_family"]
    assert selected["eta"] == 0.01
    assert selected["omega"] == 1.5
    assert selected["minimum_normal_dominance_gap"] == pytest.approx(
        6.938692407876257e-05
    )
    assert selected["coefficient_gates"]["external_condition_ceiling"][
        "value"
    ] == pytest.approx(595816615.5626934)
    assert selected["coefficient_gates"]["global_l2_response_ratio"][
        "value"
    ] == pytest.approx(0.9647729533192917)
    assert selected["spectral_passed"]
    assert selected["coefficient_passed"]
    assert all(gate["passed"] for gate in selected["spectral_gates"].values())
    assert all(
        gate["passed"] for gate in selected["coefficient_gates"].values()
    )


def test_selected_family_classifies_every_material_witness(
    cluster_audit: dict[str, object],
) -> None:
    selected_conditions = [
        condition
        for condition in cluster_audit["conditions"]
        if condition["eta"] == 0.01 and condition["omega"] == 1.5
    ]
    witnesses = [
        witness
        for condition in selected_conditions
        for witness in condition["materially_forced_near_witnesses"]
    ]

    assert len(selected_conditions) == 5
    assert all(condition["pair_count"] == 300 for condition in selected_conditions)
    assert all(
        condition["target_pair_count"] == 16
        for condition in selected_conditions
    )
    assert all(
        condition["numerically_singular_external_block_count"] == 0
        for condition in selected_conditions
    )
    assert len(witnesses) == 40
    assert cluster_audit["selected_family"][
        "material_witness_class_counts"
    ] == {
        ACOUSTIC_SELF: 16,
        DIAGONAL_ACOUSTIC_SELF: 8,
        SHEAR_DIAGONAL: 16,
    }
    assert all(witness["witness_class"] is not None for witness in witnesses)

    diagonal_self = [
        witness
        for witness in witnesses
        if witness["witness_class"] == DIAGONAL_ACOUSTIC_SELF
    ]
    assert len(diagonal_self) == 8
    assert {tuple(witness["output_wave_index"]) for witness in diagonal_self} == {
        (-2, -2),
        (-2, 2),
        (2, -2),
        (2, 2),
    }
    assert {witness["left_label"] for witness in diagonal_self} == {
        "acoustic_positive",
        "acoustic_negative",
    }


def test_sealed_campaign_is_strict_json(cluster_audit: dict[str, object]) -> None:
    json.dumps(cluster_audit, allow_nan=False)


@pytest.mark.parametrize(
    ("size", "omega", "eta"),
    [(9, 1.2, 0.02), (17, 1.1, 0.02), (17, 1.2, 0.015)],
)
def test_condition_audit_rejects_unregistered_parameters(
    size: int,
    omega: float,
    eta: float,
) -> None:
    with pytest.raises(ValueError, match="sealed Q006h"):
        audit_cluster_complete_condition(size, omega, eta)
