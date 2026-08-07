from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.mode_closure import (
    _build_sector,
    _initial_blocks,
    _make_block,
    _ordered_selection,
    _product_block_and_forcing,
    _symmetric_product_basis,
    run_mode_added_closure_audit,
)
from ttim_lbm.nonresonance import (
    quadratic_fourier_forcing,
    simple_hydrodynamic_modes,
    wave_vector_from_index,
)


@pytest.fixture(scope="module")
def registered_audit() -> dict[str, object]:
    return run_mode_added_closure_audit()


def test_symmetric_product_basis_is_orthonormal_and_invariant() -> None:
    dimension = 3
    symmetric = _symmetric_product_basis(dimension)
    dynamics = np.array(
        [
            [0.8, 0.2, -0.1],
            [0.0, 0.7, 0.3],
            [0.0, 0.0, 0.6],
        ],
        dtype=np.complex128,
    )
    full = np.kron(dynamics, dynamics)
    restricted = symmetric.conj().T @ full @ symmetric

    np.testing.assert_allclose(
        symmetric.conj().T @ symmetric,
        np.eye(symmetric.shape[1]),
        atol=1.0e-14,
    )
    np.testing.assert_allclose(
        full @ symmetric,
        symmetric @ restricted,
        atol=1.0e-14,
    )


def test_ordered_selection_constructs_an_oblique_riesz_projector() -> None:
    eigenvalues = np.array([0.95 + 0.1j, 0.95 - 0.1j, 0.4], dtype=np.complex128)
    similarity = np.array(
        [
            [1.0, 1.7, -0.8],
            [0.2, 1.0, 0.9],
            [-0.1, 0.4, 1.0],
        ],
        dtype=np.complex128,
    )
    matrix = similarity @ np.diag(eigenvalues) @ np.linalg.inv(similarity)
    selection = _ordered_selection(matrix, eigenvalues[:2])

    assert selection.basis.shape == (3, 2)
    assert np.linalg.norm(selection.projector, ord=2) > 1.0
    np.testing.assert_allclose(
        selection.projector @ selection.projector,
        selection.projector,
        atol=1.0e-12,
    )
    np.testing.assert_allclose(
        matrix @ selection.projector,
        selection.projector @ matrix,
        atol=1.0e-12,
    )


def test_product_forcing_and_sylvester_vectorization_match_direct_actions() -> None:
    size = 17
    omega = 1.2
    left_modes = simple_hydrodynamic_modes(
        *wave_vector_from_index((1, 0), size), omega
    )
    right_modes = simple_hydrodynamic_modes(
        *wave_vector_from_index((0, 1), size), omega
    )
    labels = ("shear", "acoustic_positive", "acoustic_negative")
    left = _make_block(
        "left",
        (1, 0),
        np.column_stack([left_modes[label].right_eigenvector for label in labels]),
        "test",
        "hydrodynamic cluster",
        size,
        omega,
    )
    right = _make_block(
        "right",
        (0, 1),
        np.column_stack([right_modes[label].right_eigenvector for label in labels]),
        "test",
        "hydrodynamic cluster",
        size,
        omega,
    )
    output_wave = (1, 1)
    product, forcing, basis_kind, leakage = _product_block_and_forcing(
        left, right, output_wave, size, omega
    )
    rng = np.random.default_rng(20260808)
    left_coordinates = rng.normal(size=3) + 1j * rng.normal(size=3)
    right_coordinates = rng.normal(size=3) + 1j * rng.normal(size=3)
    monomials = np.kron(left_coordinates, right_coordinates)

    assert basis_kind == "Kronecker"
    assert leakage == 0.0
    np.testing.assert_allclose(
        product @ monomials,
        np.kron(
            left.dynamics @ left_coordinates,
            right.dynamics @ right_coordinates,
        ),
        atol=1.0e-13,
    )
    np.testing.assert_allclose(
        forcing @ monomials,
        quadratic_fourier_forcing(
            left.basis @ left_coordinates,
            right.basis @ right_coordinates,
            wave_vector_from_index(output_wave, size),
            omega,
        ),
        atol=1.0e-13,
    )

    selected = _initial_blocks(size, omega)
    sector = _build_sector(output_wave, selected, size, omega)
    active_forcing = sector.active_basis.conj().T @ forcing
    projected_forcing = sector.external_projector @ active_forcing
    external_forcing = sector.external_basis.conj().T @ projected_forcing
    np.testing.assert_allclose(
        sector.external_basis @ external_forcing,
        projected_forcing,
        atol=1.0e-13,
    )
    operator = (
        np.kron(np.eye(product.shape[0]), sector.external_matrix)
        - np.kron(product.T, np.eye(sector.external_dimension))
    )
    coefficient = rng.normal(
        size=(sector.external_dimension, product.shape[0])
    ) + 1j * rng.normal(size=(sector.external_dimension, product.shape[0]))
    direct = sector.external_matrix @ coefficient - coefficient @ product
    np.testing.assert_allclose(
        operator @ coefficient.reshape(-1, order="F"),
        direct.reshape(-1, order="F"),
        atol=1.0e-13,
    )


def test_self_product_forcing_uses_the_registered_symmetric_normalization() -> None:
    size = 17
    omega = 1.2
    modes = simple_hydrodynamic_modes(
        *wave_vector_from_index((1, 0), size), omega
    )
    labels = ("shear", "acoustic_positive", "acoustic_negative")
    block = _make_block(
        "self",
        (1, 0),
        np.column_stack([modes[label].right_eigenvector for label in labels]),
        "test",
        "hydrodynamic cluster",
        size,
        omega,
    )
    product, forcing, basis_kind, leakage = _product_block_and_forcing(
        block, block, (2, 0), size, omega
    )
    symmetric = _symmetric_product_basis(block.dimension)
    coordinates = np.array(
        [0.3 + 0.2j, -0.4 + 0.1j, 0.6 - 0.5j],
        dtype=np.complex128,
    )
    symmetric_coordinates = symmetric.conj().T @ np.kron(coordinates, coordinates)

    assert basis_kind == "orthonormal symmetric tensor product"
    assert leakage < 1.0e-13
    np.testing.assert_allclose(
        product @ symmetric_coordinates,
        symmetric.conj().T
        @ np.kron(block.dynamics @ coordinates, block.dynamics @ coordinates),
        atol=1.0e-13,
    )
    np.testing.assert_allclose(
        forcing @ symmetric_coordinates,
        quadratic_fourier_forcing(
            block.basis @ coordinates,
            block.basis @ coordinates,
            wave_vector_from_index((2, 0), size),
            omega,
        ),
        atol=1.0e-13,
    )


def test_registered_initial_set_internalizes_the_diagonal_resonance(
    registered_audit: dict[str, object],
) -> None:
    audit = registered_audit
    initial = audit["initial_mode_order"]
    symmetry = audit["initial_symmetry_maps"]
    internalization = audit["diagonal_resonance_internalization"]

    assert sum(record["dimension"] for record in initial) == 16
    assert len(initial) == 16
    assert all(record["target"] is not None for record in symmetry["c4_mapping"])
    assert all(
        record["target"] is not None for record in symmetry["conjugate_pairing"]
    )
    assert symmetry["maximum_c4_subspace_residual"] < 1.0e-10
    assert symmetry["maximum_conjugacy_subspace_residual"] < 1.0e-10
    assert internalization["unprojected_status"] == "compatible_nonunique"
    assert internalization["external_projected_status"] == "nonsingular"
    assert internalization["output_wave_index"] == [1, 1]
    assert internalization["external_smallest_singular_value"] > 0.13


def test_registered_q006r_coefficient_closure_stops_without_addition(
    registered_audit: dict[str, object],
) -> None:
    audit = registered_audit
    terminal = audit["terminal_summary"]
    coefficient = audit["coefficient_solvability"]
    round_record = audit["rounds"][0]

    assert audit["study_validity"] == "passed"
    assert terminal["closure_stopped"]
    assert terminal["nonempty_additions"] == 0
    assert terminal["round_count"] == 1
    assert terminal["final_real_dimension"] == 16
    assert terminal["terminal_pair_count"] == 136
    assert terminal["terminal_numerically_singular_external_block_count"] == 0
    assert terminal["terminal_near_singular_external_block_count"] == 0
    assert terminal["terminal_maximum_condition_number"] < 1.9e3
    assert terminal["terminal_maximum_structural_residual"] < 1.0e-10
    assert round_record["pair_enumeration_complete"]
    assert round_record["maximum_fixed_leaf_residual"] < 1.0e-10
    assert round_record["maximum_external_cluster_structural_residual"] < 1.0e-10
    assert coefficient["passed"]
    assert all(gate["passed"] for gate in coefficient["gates"].values())
    assert all(
        len(record["singular_values"]) == record["operator_dimension"]
        for record in round_record["pair_table"]
    )


def test_registered_q006r_rejects_linear_normal_dominance(
    registered_audit: dict[str, object],
) -> None:
    audit = registered_audit
    normal = audit["linear_normal_dominance_prequalification"]

    assert not normal["passed"]
    assert audit["hypothesis_outcome"] == "rejected"
    assert normal["normal_dominance_gap"] < -0.013
    assert normal["maximum_excluded_wave_index"] in ([0, -8], [-8, 0])
    assert normal["minimum_local_sylvester_separation"] > 0.13
    assert normal["maximum_selected_riesz_projector_norm"] < 2.0
    assert not normal["gates"]["normal_dominance_gap"]["passed"]
    assert all(
        gate["passed"]
        for name, gate in normal["gates"].items()
        if name != "normal_dominance_gap"
    )


def test_registered_q006r_record_is_strict_json(
    registered_audit: dict[str, object],
) -> None:
    rendered = json.dumps(registered_audit, allow_nan=False)
    assert "coefficient-solvable finite-grid candidate" in rendered


@pytest.mark.parametrize(
    ("size", "omega"),
    [(16, 1.2), (19, 1.2), (17, 0.0), (17, 1.3), (17, 2.0)],
)
def test_q006r_rejects_unregistered_domains(size: int, omega: float) -> None:
    with pytest.raises(ValueError):
        run_mode_added_closure_audit(size=size, omega=omega)
