from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import gmpy2
import pytest

import research.q011k_interval_spectral_split as q011k
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011k_cycle() -> dict[str, object]:
    return q011k.run_interval_spectral_split_audit()


def test_q011k_seals_q011j_and_q011c2() -> None:
    audit, q011j_artifact, q011c2_artifact = q011k._sealed_input_audit()

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert q011j_artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert q011c2_artifact["cycle"]["hypothesis_outcome"] == "accepted"
    assert audit["q011c2_artifact"]["selected_endpoint_dimensions"] == {
        "0": 6,
        "1": 9,
        "16": 9,
    }


def test_q011k_contraction_derived_root_box_is_exact(
    q011k_cycle: dict[str, object],
) -> None:
    root = q011k_cycle["contraction_derived_root_enclosure_audit"]
    correction = _fraction(root["primary_center_correction_upper"])
    contraction = _fraction(root["primary_contraction_upper"])
    radius = _fraction(root["primary_root_coordinate_radius_upper"])

    assert root["passed"]
    assert all(root["checks"].values())
    assert radius == correction / (1 - contraction)
    assert radius <= q011k.ROOT_RADIUS_CAP
    assert _fraction(root["replay_root_coordinate_radius_upper"]) <= radius
    assert _fraction(root["ambient_population_component_radius_upper"]) == 186 * radius
    assert _fraction(root["minimum_population_lower"]) > 0
    assert _fraction(root["minimum_density_lower"]) > 0
    assert root["coordinate_exact_sha256"] == (
        "508f175fc7d1d62d253b5e34877a25fded6f4d207ef26f281a01d10eb5571ed8"
    )
    assert root["lifted_center_exact_sha256"] == (
        "c85cddc2072cb2e86d1a73024da97828d4a7f21f10b631c86a5d9ee0297c72dd"
    )


def test_q011k_exact_interval_block_family_is_complete(
    q011k_cycle: dict[str, object],
) -> None:
    block = q011k_cycle["exact_interval_block_family_audit"]

    assert block["passed"]
    assert all(block["checks"].values())
    assert block["block_count"] == 17
    assert block["zero_block_dimension"] == 150
    assert block["nonzero_block_dimension"] == 153
    assert block["fixed_leaf_dimension"] == 2598
    assert block["representative_blocks"] == list(range(9))
    assert block["transported_conjugate_blocks"] == list(range(9, 17))
    assert _fraction(block["maximum_point_proposal_distance_infinity_upper"]) <= (
        q011k.MAXIMUM_POINT_BLOCK_DISCREPANCY
    )
    assert _fraction(block["maximum_interval_family_distance_infinity_upper"]) > 0
    for record in block["block_records"]:
        if record["block_index"] != 0:
            assert record["minimum_sparse_nonzeros_per_row"] == 27
            assert record["maximum_sparse_nonzeros_per_row"] == 27


def test_q011k_dual_precision_bauer_fike_proof_passes_without_context_leak(
    q011k_cycle: dict[str, object],
) -> None:
    proof = q011k_cycle["dual_precision_bauer_fike_audit"]
    caller_signature = q011k.q011j._context_signature(gmpy2.get_context())
    forbidden = {"underflow", "overflow", "invalid", "division_by_zero", "erange"}

    assert proof["protocol_passed"]
    assert proof["hypothesis_passed"]
    assert all(proof["protocol_checks"].values())
    assert all(proof["hypothesis_checks"].values())
    assert len(proof["representative_block_records"]) == 9
    assert _fraction(proof["maximum_inverse_defect_infinity_norm_upper"]) <= (
        q011k.MAXIMUM_INVERSE_DEFECT
    )
    assert proof["maximum_bauer_fike_radius_block"] == 4
    for record in proof["representative_block_records"]:
        assert record["passed"]
        assert all(record["checks"].values())
        for precision_name, precision in (
            ("primary_precision_proof", q011k.PRIMARY_PRECISION_BITS),
            ("replay_precision_proof", q011k.REPLAY_PRECISION_BITS),
        ):
            precision_record = record[precision_name]
            assert precision_record["precision_bits"] == precision
            assert precision_record["passed"]
            assert all(precision_record["checks"].values())
            for flags in precision_record["mpfr_flag_groups"].values():
                assert not any(flags[name] for name in forbidden)
    assert q011k.q011j._context_signature(gmpy2.get_context()) == caller_signature


def test_q011k_selected_external_split_is_rigorous(
    q011k_cycle: dict[str, object],
) -> None:
    split = q011k_cycle["selected_external_split_audit"]

    assert split["protocol_passed"]
    assert split["hypothesis_passed"]
    assert all(split["protocol_checks"].values())
    assert all(split["hypothesis_checks"].values())
    assert split["selected_eigenvalue_count"] == 24
    assert split["external_eigenvalue_count"] == 2574
    assert split["fixed_leaf_eigenvalue_count"] == 2598
    assert split["maximum_selected_matching_distance"] <= (q011k.MAXIMUM_SELECTED_MATCHING_DISTANCE)
    assert _fraction(split["maximum_fixed_leaf_modulus_upper"]) <= (q011k.SPECTRAL_RADIUS_CEILING)
    assert _fraction(split["minimum_selected_external_disc_gap_lower"]) >= (
        q011k.MINIMUM_DISC_SPLIT_GAP
    )
    assert _fraction(split["normal_dominance_gap_lower"]) >= (q011k.MINIMUM_NORMAL_DOMINANCE_GAP)


def test_q011k_quadratic_spectral_nonresonance_is_complete(
    q011k_cycle: dict[str, object],
) -> None:
    quadratic = q011k_cycle["quadratic_spectral_nonresonance_audit"]

    assert quadratic["passed"]
    assert all(quadratic["checks"].values())
    assert quadratic["selected_eigenvalue_count"] == 24
    assert quadratic["unordered_pair_count"] == 300
    assert quadratic["external_comparison_count"] == 44010
    assert len(quadratic["pair_records"]) == 300
    assert (
        _fraction(quadratic["minimum_quadratic_external_spectral_distance_lower"])
        >= q011k.MINIMUM_QUADRATIC_DISTANCE
    )
    assert quadratic["minimum_distance_witness"] == {
        "pair_index": 173,
        "left": {"block_index": 1, "center_index": 144},
        "right": {"block_index": 16, "center_index": 144},
        "output_block_index": 0,
        "external_center_index": 143,
    }


def test_q011k_accepts_only_the_registered_spectral_theorem(
    q011k_cycle: dict[str, object],
) -> None:
    assert q011k_cycle["study_validity"] == "passed"
    assert q011k_cycle["hypothesis_outcome"] == "accepted"
    assert q011k_cycle["scientific_classification"] == (
        "the exact repaired fixed point has a rigorously stable and quadratically "
        "nonresonant selected/external spectral split"
    )
    assert len(q011k_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011k_cycle["validity_gates"].values())
    assert len(q011k_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011k_cycle["hypothesis_gates"].values())
    theorem = q011k_cycle["theorem_consequence"]
    assert theorem["exact_repaired_fixed_point_fixed_leaf_spectrum_is_strictly_stable"]
    assert theorem["q011c2_designated_selected_cluster_has_rigorous_dimension_24"]
    assert theorem["rigorous_external_dimension_is_2574"]
    assert theorem["selected_and_external_spectral_unions_do_not_exchange"]
    assert theorem["selected_quadratic_eigenvalue_products_are_external_nonresonant"]
    assert not theorem["raw_q011b_exact_map_spectrum_is_certified"]
    assert not theorem["q011c2_continuous_amplitude_path_is_rigorous"]
    assert not theorem["nonnormal_homological_inverse_is_certified"]
    assert not theorem["forced_ssm_exists_or_is_unique"]
    assert not theorem["nonlinear_normal_attraction_is_certified"]


def test_q011k_cycle_is_strict_json_with_reproducible_digests(
    q011k_cycle: dict[str, object],
) -> None:
    json.dumps(q011k_cycle, allow_nan=False)
    assert q011k_cycle["input_digest_sha256"] == (
        "f6351c136e08dc9f55dba2260ebae00f12abb9b24a6e339729dde51d475489c2"
    )
    assert q011k_cycle["root_digest_sha256"] == (
        "f5631d2e018f56a4e357a12b552d41d82d61946e6b40675641b754be58c758cc"
    )
    assert q011k_cycle["block_digest_sha256"] == (
        "7849ff7417ff73d0c6891235675ee541159941d8ea422adb7fd5cbe0447af3d8"
    )
    assert q011k_cycle["proof_digest_sha256"] == (
        "1f6fca551d0360798ed185ac8b4140ace1678fec2e6765e7530705e7d7bba4a4"
    )
    assert q011k_cycle["result_digest_sha256"] == (
        "2c6c6de5713aea5588297048f8c313acaf4f261f364a9e7e6487c588dab4ce5e"
    )
    assert q011k_cycle["result_digest_sha256"] == q011k.q011b._canonical_json_sha256(
        q011k._result_digest_sections(q011k_cycle)
    )


def test_q011k_artifact_records_the_interval_spectral_proof() -> None:
    runner_path = Path(q011k.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011k_interval_spectral_split.json"
    if not artifact_path.exists():
        pytest.skip("Q011k artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert _file_sha256(artifact_path) == (
        "8fa95cc1368e2321b9b1697c794926358257fc23cdb6bf7260364f3368129e3a"
    )
    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"] == {
        "filename": "q011k_interval_spectral_split.py",
        "sha256": "d95a41c1ad42bf388f36840e47dc02e7f385b2a402abbc72fcdbff093a601a07",
        "sha256_newline_normalization": "UTF-8 text with universal newlines",
    }
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["result_digest_sha256"] == q011k.q011b._canonical_json_sha256(
        q011k._result_digest_sections(cycle)
    )
    json.dumps(artifact, allow_nan=False)
