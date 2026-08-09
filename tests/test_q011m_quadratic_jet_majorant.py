from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q011m_quadratic_jet_majorant as q011m
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011m_cycle() -> dict[str, object]:
    return q011m.run_quadratic_jet_majorant_audit()


def test_q011m_seals_q011j_q011k_and_q011l() -> None:
    audit, q011j_artifact, q011k_artifact, q011l_artifact = (
        q011m._sealed_input_audit()
    )

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert q011j_artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert q011k_artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert q011l_artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert not q011j_artifact["cycle"]["theorem_consequence"][
        "q011e_through_q011h_coefficients_transfer_to_repaired_map"
    ]
    assert not q011l_artifact["cycle"]["theorem_consequence"][
        "repaired_quadratic_jet_or_coefficients_are_certified"
    ]


def test_q011m_exact_root_fits_every_simple_envelope(
    q011m_cycle: dict[str, object],
) -> None:
    audit = q011m_cycle["exact_root_and_simple_envelope_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert _fraction(audit["root_population_component_radius_upper"]) <= (
        q011m.ROOT_COMPONENT_RADIUS_ENVELOPE
    )
    assert _fraction(audit["root_population_floor_lower"]) >= (
        q011m.ROOT_POPULATION_FLOOR
    )
    assert _fraction(audit["root_density_floor_lower"]) >= q011m.ROOT_DENSITY_FLOOR
    assert _fraction(audit["enclosed_root_momentum_component_absolute_upper"]) <= (
        q011m.ROOT_MOMENTUM_COMPONENT_ENVELOPE
    )
    assert audit["zero_block_population_lift_infinity_norm"] == 186
    for record in audit["selected_block_records"]:
        assert _fraction(record["vector_infinity_norm_upper"]) <= _fraction(
            record["vector_norm_envelope"]
        )
        assert _fraction(record["graph_radius_upper"]) <= _fraction(
            record["graph_radius_envelope"]
        )
        assert _fraction(record["inverse_coordinate_norm_upper"]) <= _fraction(
            record["inverse_coordinate_envelope"]
        )
    for record in audit["sector_ambient_inverse_records"]:
        assert _fraction(record["observed_upper"]) <= _fraction(
            record["simple_envelope"]
        )


def test_q011m_fourier_lift_and_dimensions_reproduce(
    q011m_cycle: dict[str, object],
) -> None:
    audit = q011m_cycle["fourier_and_dimension_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["selected_blocks"] == [0, 1, 16]
    assert audit["selected_dimensions"] == {"0": 6, "1": 9, "16": 9}
    assert audit["selected_coordinate_count"] == 24
    assert audit["quadratic_pair_count"] == 300
    assert audit["sector_pair_counts"] == {
        "0": 102,
        "1": 54,
        "16": 54,
        "2": 45,
        "15": 45,
    }
    assert audit["zero_block_population_lift_infinity_norm"] == 186
    assert not audit["cross_sector_cancellation_used"]


def test_q011m_analytic_derivative_bounds_and_identities_are_exact(
    q011m_cycle: dict[str, object],
) -> None:
    audit = q011m_cycle["analytic_map_derivative_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(audit["population_derivative_records"]) == 9
    assert audit["maximum_second_derivative_population"] == 0
    assert audit["maximum_third_derivative_population"] == 0
    assert _fraction(audit["maximum_map_second_derivative_bilinear_upper"]) <= (
        q011m.SECOND_DERIVATIVE_CAP
    )
    assert _fraction(audit["maximum_map_third_derivative_trilinear_upper"]) <= (
        q011m.THIRD_DERIVATIVE_CAP
    )
    assert audit["signed_tensor_sample"]["exact_tensor_digest_sha256"] == (
        "f77acf8cff113b906284b077841284de307649e1afc04019b6de7147d0670b08"
    )
    assert audit["exact_zero_second_conserved_component_count"] == 27
    assert audit["exact_zero_third_conserved_component_count"] == 81
    assert all(
        record["passed"] for record in audit["equilibrium_conserved_moment_identity"]
    )


def test_q011m_implicit_quadratic_coefficient_majorants_reproduce(
    q011m_cycle: dict[str, object],
) -> None:
    audit = q011m_cycle["implicit_quadratic_jet_coefficient_audit"]
    values = {name: _fraction(record) for name, record in audit["coefficient_values"].items()}

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert values["K_T"] == (
        186 * 13 * (1 + Fraction(2, 10**6))
        + 2 * 16 * (1 + Fraction(1, 10**7))
    )
    assert values["K_F"] == Fraction(145, 2) * values["K_T"] ** 2
    assert values["K_Z"] == values["K_F"] * (
        186 * 3_400_000 + 2 * 24_000 + 2 * 2_300_000
    )
    assert values["K_P"] == 53 * values["K_F"]
    assert values["K_S"] == Fraction(31, 25)
    assert values["K_T"] <= q011m.TANGENT_CAP
    assert values["K_F"] <= q011m.FORCING_CAP
    assert values["K_Z"] <= q011m.CHART_CAP
    assert values["K_P"] <= q011m.REDUCED_QUADRATIC_CAP
    assert not audit["componentwise_coefficient_array_constructed"]


def test_q011m_radius_campaign_selects_the_registered_cubic_window(
    q011m_cycle: dict[str, object],
) -> None:
    coefficient = q011m_cycle["implicit_quadratic_jet_coefficient_audit"]
    values = {
        name: _fraction(record) for name, record in coefficient["coefficient_values"].items()
    }
    audit = q011m_cycle["cubic_defect_radius_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["monotonicity_checks"].values())
    assert len(audit["radius_records"]) == 8
    assert audit["passing_radius_count"] == 7
    assert _fraction(audit["selected_radius"]) == Fraction(1, 10**11)
    assert _fraction(audit["first_failed_larger_radius"]) == Fraction(3, 10**11)
    assert audit["first_failed_larger_constraints"] == [
        "state_displacement_is_in_derivative_domain",
        "cubic_defect_is_bounded",
        "defect_to_state_displacement_is_bounded",
    ]
    selected = audit["selected_record"]
    radius = _fraction(selected["radius"])
    displacement = _fraction(selected["state_displacement_upper"])
    assert displacement == values["K_T"] * radius + values["K_Z"] * radius**2
    assert _fraction(selected["reduced_amplitude_upper"]) == (
        values["K_S"] * radius + values["K_P"] * radius**2
    )
    assert selected["passed"]
    assert all(selected["checks"].values())
    assert audit["exact_radius_record_digest_sha256"] == (
        "dd14364d4c60d8c47bf593538a414178db440a6a25e226088a69332188618f52"
    )


def test_q011m_accepts_only_the_registered_quadratic_jet_majorant(
    q011m_cycle: dict[str, object],
) -> None:
    assert q011m_cycle["study_validity"] == "passed"
    assert q011m_cycle["hypothesis_outcome"] == "accepted"
    assert q011m_cycle["scientific_classification"] == (
        "the repaired exact map admits a unique graph-gauge quadratic jet with "
        "the registered coefficient and cubic-defect majorants"
    )
    assert len(q011m_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011m_cycle["validity_gates"].values())
    assert len(q011m_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011m_cycle["hypothesis_gates"].values())
    theorem = q011m_cycle["theorem_consequence"]
    assert theorem["unique_graph_gauge_quadratic_jet_exists_in_all_five_sectors"]
    assert theorem["registered_quadratic_coefficient_majorants_are_rigorous"]
    assert theorem["registered_uniform_cubic_defect_majorant_is_rigorous"]
    assert theorem["selected_finite_reduced_radius_is_certified"]
    assert not theorem["componentwise_quadratic_coefficients_are_certified"]
    assert not theorem["finite_cubic_defect_implies_exact_invariance"]
    assert not theorem["raw_q011b_map_is_certified"]
    assert not theorem["q011e_through_q011h_raw_coefficients_transfer_to_repaired_map"]
    assert not theorem["an_exact_invariant_manifold_or_forced_ssm_exists"]
    assert not theorem["nonlinear_normal_attraction_or_a_basin_is_certified"]


def test_q011m_cycle_is_strict_json_with_reproducible_digests(
    q011m_cycle: dict[str, object],
) -> None:
    json.dumps(q011m_cycle, allow_nan=False)
    assert q011m_cycle["input_digest_sha256"] == (
        "dd30ead5c7c6081502bc34a6163ce64321dd4f9a339c7f24959dfc76891591cb"
    )
    assert q011m_cycle["derivative_digest_sha256"] == (
        "0b8f345fdf2bda5b95f2c1624920968f1ad499f4d5e765c0b8305e2045ac7e3a"
    )
    assert q011m_cycle["coefficient_digest_sha256"] == (
        "1d708042f97c8c42164b07ff7104a68bdef95c14faf90dcb0171749d92b8a514"
    )
    assert q011m_cycle["majorant_digest_sha256"] == (
        "bf7144f407dd3e6aabf2161bf3d8c48dbb2e6c89a48cde9cfccf1cff60455e00"
    )
    assert q011m_cycle["result_digest_sha256"] == (
        "f47a1a4c1712fcff129c3840d7e64dfe1bbbe4bdacc049e28be6f868dbfc9cd4"
    )
    assert q011m_cycle["result_digest_sha256"] == q011m.q011b._canonical_json_sha256(
        q011m._result_digest_sections(q011m_cycle)
    )


def test_q011m_artifact_records_the_accepted_majorant() -> None:
    runner_path = Path(q011m.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011m_quadratic_jet_majorant.json"
    if not artifact_path.exists():
        pytest.skip("Q011m artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "b76b0ec1a1436aa3c2b48fcc29485e60e03675bf9a1f4f85ac3106d30687da3f"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011m_quadratic_jet_majorant.py",
        "sha256": "0cdc6ec9697d25bea3b28cf90f01f3f639062b3c04a64c4a88e6bd7221163150",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == q011m.q011b._canonical_json_sha256(
        q011m._result_digest_sections(cycle)
    )
    json.dumps(artifact, allow_nan=False)
