from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import gmpy2
import numpy as np
import pytest

import research.q011j_interval_fixed_point as q011j
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import RationalInterval, _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011j_cycle() -> dict[str, object]:
    return q011j.run_interval_fixed_point_audit()


def test_q011j_seals_the_repaired_q011i_map_and_claim_boundary() -> None:
    audit, artifact = q011j._sealed_q011i_artifact_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["artifact"]["hypothesis_outcome"] == "accepted"
    consequence = artifact["cycle"]["decision_consequence"]
    assert consequence["interval_fixed_point_proof_is_authorized"]
    assert not consequence["q011b_numerical_accepted_outcome_changed"]
    assert not consequence["q011e_through_q011h_coefficients_transfer_to_repaired_map"]
    assert not consequence["forced_ssm_exists_or_is_unique"]


def test_q011j_affine_coordinate_is_exactly_the_fixed_leaf() -> None:
    _, artifact = q011j._sealed_q011i_artifact_audit()
    coordinate, lifted, sealed, lift_matrix, audit = q011j._coordinate_audit(artifact)

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(coordinate) == q011j.COORDINATE_DIMENSION == 150
    assert len(lifted) == q011j.STRIPE_DIMENSION == 153
    assert lift_matrix.shape == (153, 150)
    assert np.linalg.matrix_rank(lift_matrix.astype(np.float64)) == 150
    assert np.max(np.sum(np.abs(lift_matrix), axis=1)) == 186
    assert q011j._extract_exact(lifted) == coordinate
    assert q011j._exact_moments(lifted) == q011j.TARGET_MOMENTS
    assert audit["pivot_moment_determinant"]["float"] == 1.0
    assert _fraction(audit["maximum_pivot_correction"]) <= (q011j.MAXIMUM_CENTER_PIVOT_CORRECTION)
    assert audit["coordinate_exact_sha256"] == (
        "508f175fc7d1d62d253b5e34877a25fded6f4d207ef26f281a01d10eb5571ed8"
    )
    assert audit["lifted_center_exact_sha256"] == (
        "c85cddc2072cb2e86d1a73024da97828d4a7f21f10b631c86a5d9ee0297c72dd"
    )
    assert audit["lift_matrix_sha256"] == (
        "29fa38981648d04b9bb3e58106303ce4f741400761744080c8258e04f328baeb"
    )
    for index in q011j.FREE_INDICES:
        assert lifted[index] == Fraction.from_float(float(sealed.ravel()[index]))


def test_q011j_exact_map_and_jacobian_oracle_pass() -> None:
    _, artifact = q011j._sealed_q011i_artifact_audit()
    coordinate, lifted, _, lift_matrix, _ = q011j._coordinate_audit(artifact)
    source_exact, source_float, source_audit = q011j._repaired_source_exact()
    residual, jacobian, sparse, pivot, audit = q011j._oracle_audit(
        coordinate,
        lifted,
        lift_matrix,
        source_exact,
        source_float,
    )

    assert source_audit["passed"]
    assert audit["passed"]
    assert all(audit["checks"].values())
    assert len(residual) == 150
    assert len(jacobian) == len(sparse) == len(pivot) == 150
    assert audit["binary64_map_relative_l2_discrepancy"] <= (q011j.MAXIMUM_MAP_RELATIVE_DISCREPANCY)
    assert audit["analytic_jacobian_relative_frobenius_discrepancy"] <= (
        q011j.MAXIMUM_JACOBIAN_RELATIVE_DISCREPANCY
    )
    assert audit["exact_reduced_residual_sha256"] == (
        "e715de2f18545e856cd42949c2b5387eae9a7a4cfc57a7979163f4e3601dfc2d"
    )
    assert audit["exact_reduced_jacobian_sha256"] == (
        "236083b8ad6f5f8426deb3371df3043bd9a8ee50071a90f466659173fe1dc504"
    )
    assert q011j._exact_moments(q011j._exact_repaired_stripe_step(lifted, source_exact)) == (
        q011j.TARGET_MOMENTS
    )


def test_q011j_registered_box_encloses_an_independent_exact_corner_jacobian() -> None:
    _, artifact = q011j._sealed_q011i_artifact_audit()
    coordinate, _, _, lift_matrix, _ = q011j._coordinate_audit(artifact)
    radius = Fraction(1, 10**8)
    coordinate_box = [RationalInterval(value - radius, value + radius) for value in coordinate]
    box_state = q011j._lift_interval(coordinate_box)
    box_sparse, box_pivot, _ = q011j._reduced_derivative_factors(box_state)
    box_jacobian = q011j._combine_reduced_factors(box_sparse, box_pivot, lift_matrix)

    corner_coordinate = [
        value + (radius if index % 2 == 0 else -radius) for index, value in enumerate(coordinate)
    ]
    corner_state = q011j._lift_exact(corner_coordinate)
    assert q011j._exact_moments(corner_state) == q011j.TARGET_MOMENTS
    point_state = [RationalInterval.point(value) for value in corner_state]
    corner_sparse, corner_pivot, densities = q011j._reduced_derivative_factors(point_state)
    corner_jacobian = q011j._point_matrix(
        q011j._combine_reduced_factors(corner_sparse, corner_pivot, lift_matrix)
    )

    assert min(value.lower for value in box_state) > 0
    assert min(value.lower for value in densities) > 0
    assert all(
        interval.lower <= point <= interval.upper
        for box_row, point_row in zip(box_jacobian, corner_jacobian, strict=True)
        for interval, point in zip(box_row, point_row, strict=True)
    )


def test_q011j_dual_precision_krawczyk_proof_passes(
    q011j_cycle: dict[str, object],
) -> None:
    proof = q011j_cycle["interval_krawczyk_proof_audit"]
    primary = proof["primary_precision_audit"]
    replay = proof["replay_precision_audit"]

    assert proof["protocol_passed"]
    assert proof["proof_passed"]
    assert all(proof["protocol_checks"].values())
    assert all(proof["proof_checks"].values())
    assert _fraction(proof["selected_radius"]) == Fraction(1, 10**8)
    assert primary["passing_radius_count"] == replay["passing_radius_count"] == 5
    assert primary["radius_records"][4]["passed"]
    assert replay["radius_records"][4]["passed"]
    assert not primary["radius_records"][5]["passed"]
    assert not replay["radius_records"][5]["passed"]
    assert _fraction(primary["point_inverse_defect_infinity_norm_upper"]) <= (
        q011j.MAXIMUM_POINT_INVERSE_DEFECT
    )
    assert _fraction(proof["selected_primary_contraction_upper"]) <= q011j.KRAWCZYK_CAP
    assert _fraction(proof["selected_primary_utilization_upper"]) <= q011j.KRAWCZYK_CAP
    assert _fraction(proof["selected_replay_contraction_upper"]) <= q011j.KRAWCZYK_CAP
    assert _fraction(proof["selected_replay_utilization_upper"]) <= q011j.KRAWCZYK_CAP
    assert proof["higher_precision_uppers_are_contained"]
    assert proof["selected_radius_matches_between_precisions"]
    assert proof["preconditioner_is_nonsingular_by_neumann"]
    assert proof["point_jacobian_is_nonsingular_by_neumann"]
    assert proof["strict_krawczyk_inclusion"]
    assert proof["strict_interval_contraction"]
    assert proof["preconditioner_sha256"] == (
        "1d157cd3ef26ae109f45698dd049e50677f6ec6432be0d17b8a09b6d41152035"
    )


def test_q011j_mpfr_contexts_are_outward_and_do_not_leak(
    q011j_cycle: dict[str, object],
) -> None:
    proof = q011j_cycle["interval_krawczyk_proof_audit"]
    caller_signature = q011j._context_signature(gmpy2.get_context())
    forbidden = {"underflow", "overflow", "invalid", "division_by_zero", "erange"}

    for name, precision in (
        ("primary_precision_audit", q011j.PRIMARY_PRECISION_BITS),
        ("replay_precision_audit", q011j.REPLAY_PRECISION_BITS),
    ):
        audit = proof[name]
        assert audit["mpfr_context"]["precision_bits"] == precision
        assert audit["mpfr_context"]["rounding_modes"] == ["RoundDown", "RoundUp"]
        assert audit["protocol_passed"]
        for flags in audit["mpfr_flag_groups"].values():
            assert not any(flags[key] for key in forbidden)
    assert q011j._context_signature(gmpy2.get_context()) == caller_signature


def test_q011j_accepts_only_the_registered_local_theorem(
    q011j_cycle: dict[str, object],
) -> None:
    assert q011j_cycle["study_validity"] == "passed"
    assert q011j_cycle["hypothesis_outcome"] == "accepted"
    assert q011j_cycle["scientific_classification"] == (
        "the repaired periodic forcing admits a locally unique exact fixed-leaf "
        "fixed point in the registered rational box"
    )
    assert len(q011j_cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in q011j_cycle["validity_gates"].values())
    assert len(q011j_cycle["hypothesis_gates"]) == 4
    assert all(gate["passed"] for gate in q011j_cycle["hypothesis_gates"].values())
    theorem = q011j_cycle["theorem_consequence"]
    assert theorem["repaired_exact_stripe_fixed_point_exists"]
    assert theorem["repaired_exact_full_17x17_x_independent_fixed_point_exists"]
    assert theorem["fixed_point_is_unique_within_the_selected_affine_box"]
    assert not theorem["raw_q011b_exact_map_fixed_point_is_certified"]
    assert not theorem["q011e_through_q011h_coefficients_transfer_to_repaired_map"]
    assert not theorem["rigorous_fixed_leaf_spectrum_is_certified"]
    assert not theorem["forced_ssm_exists_or_is_unique"]
    assert not theorem["normal_attraction_is_certified"]


def test_q011j_cycle_is_strict_json_with_reproducible_digests(
    q011j_cycle: dict[str, object],
) -> None:
    json.dumps(q011j_cycle, allow_nan=False)
    assert q011j_cycle["input_digest_sha256"] == (
        "a183f4830c757b58122132cf64111fd5375636affdb6c0b31e1cd90e89085799"
    )
    assert q011j_cycle["coordinate_digest_sha256"] == (
        "adaef353b8b64509334794c6014dc8b88e81ca2b776c3b65bd4d50911ae9452b"
    )
    assert q011j_cycle["oracle_digest_sha256"] == (
        "177468a48f667ddd922ed4b979d3e7e5d4cc0ed3afffe27a34651060da8e0f5f"
    )
    assert q011j_cycle["proof_digest_sha256"] == (
        "1080fcea24358422514bba7fb9881928269c853cb4d12b0282e63840c56124c0"
    )
    assert q011j_cycle["result_digest_sha256"] == (
        "ddad5beca9693eeab726382ac864d01a27b749d579c2ec8f12dd9f8c499db934"
    )
    assert q011j_cycle["result_digest_sha256"] == q011j.q011i.q011b._canonical_json_sha256(
        q011j._result_digest_sections(q011j_cycle)
    )


def test_q011j_artifact_records_the_interval_fixed_point_proof() -> None:
    runner_path = Path(q011j.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011j_interval_fixed_point.json"
    if not artifact_path.exists():
        pytest.skip("Q011j artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "74a2e084137699739c14d980b05676e14e6802b4018b3893d3d05270850c2c5a"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011j_interval_fixed_point.py",
        "sha256": "23a7a3a272264be3eb5330b2456192bd797aa968c4f795e2cbe8e337fc8fe4b5",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == q011j.q011i.q011b._canonical_json_sha256(
        q011j._result_digest_sections(cycle)
    )
    json.dumps(artifact, allow_nan=False)
