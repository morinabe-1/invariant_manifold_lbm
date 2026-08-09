from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011w_degree4_phase_disks as q011w
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011w_cycle() -> dict[str, Any]:
    return q011w.run_degree4_phase_disk_audit()


def test_q011w_seals_three_inputs_seventeen_digests_and_helpers(
    q011w_cycle: dict[str, Any],
) -> None:
    audit = q011w_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 17
    assert {label: audit[label]["hypothesis_outcome"] for label in ("q011k", "q011u", "q011v")} == {
        "q011k": "accepted",
        "q011u": "rejected",
        "q011v": "accepted",
    }
    assert audit["helper_sources"] == {
        "q011l": {
            "filename": "q011l_interval_homological_inverse.py",
            "sha256": q011w.Q011L_SOURCE_SHA256,
        },
        "q011o": {
            "filename": "q011o_graph_transform_setup.py",
            "sha256": q011w.Q011O_SOURCE_SHA256,
        },
    }
    assert audit["checks"]["q011k_eigendisc_scope_is_preserved"]
    assert audit["checks"]["q011u_c91_tail_and_valid_rejection_scope_is_preserved"]
    assert audit["checks"]["q011v_degree_three_certificate_and_boundary_are_preserved"]


def test_q011w_reproduces_the_complete_degree_four_modulus_inventory(
    q011w_cycle: dict[str, Any],
) -> None:
    audit = q011w_cycle["degree4_modulus_inventory_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree"] == 4
    assert audit["degree_modulus_aggregate_count"] == 35
    assert audit["degree_expanded_product_control_count"] == 126
    assert audit["modulus_separated_aggregate_count"] == 33
    assert audit["modulus_overlap_aggregate_count"] == 2
    assert [record["selected_type_counts"] for record in audit["overlap_records"]] == [
        [0, 0, 0, 4],
        [0, 0, 1, 3],
    ]
    assert {tuple(record["external_group_indices"]) for record in audit["overlap_records"]} == {
        (183,)
    }
    assert audit["selected_source_group_sizes"] == [8, 4, 4, 8]
    assert len(audit["external_target_identifiers"]) == 8
    assert audit["eigencenter_reconstruction"]["eigencenter_count"] == 2598
    assert audit["eigencenter_reconstruction"]["selected_count"] == 24
    assert audit["eigencenter_reconstruction"]["external_count"] == 2574
    assert (
        audit["eigencenter_reconstruction"]["exact_modulus_interval_digest_sha256"]
        == "120d9214caa90d3eff168fca272ce8da3ee47eb5e11cbd65b0d462139b2d73fb"
    )
    assert len(audit["exact_inventory_digest_sha256"]) == 64


def test_q011w_combination_with_replacement_and_sector_filter_are_complete(
    q011w_cycle: dict[str, Any],
) -> None:
    audit = q011w_cycle["fourier_output_sector_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["structural_proof"].values())
    assert audit["output_sector_law"] == "b_out=(b_1+b_2+b_3+b_4) mod 17"
    assert audit["indexed_monomial_count"] == 810
    assert audit["aggregate_monomial_counts"] == [330, 480]
    assert audit["aggregate_sector_histograms"] == [
        {
            "0": 84,
            "1": 64,
            "2": 38,
            "3": 16,
            "4": 5,
            "13": 5,
            "14": 16,
            "15": 38,
            "16": 64,
        },
        {
            "0": 124,
            "1": 100,
            "2": 54,
            "3": 20,
            "4": 4,
            "13": 4,
            "14": 20,
            "15": 54,
            "16": 100,
        },
    ]
    assert audit["external_target_sector_histogram"] == {
        "0": 4,
        "2": 2,
        "15": 2,
    }
    assert audit["aggregate_compatible_comparison_counts"] == [488, 712]
    assert audit["sector_compatible_comparison_count"] == 1200
    assert len(audit["monomial_records"]) == 810
    assert len(audit["compatible_pairs"]) == 1200
    assert len(audit["exact_sector_record_digest_sha256"]) == 64


def test_q011w_framed_digests_cover_every_exact_product_and_comparison(
    q011w_cycle: dict[str, Any],
) -> None:
    audit = q011w_cycle["phase_sensitive_product_disk_audit"]
    framed = audit["framed_exact_record_digests"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 810
    assert audit["comparison_record_count"] == 1200
    assert framed["exact_product_record_count"] == 810
    assert framed["exact_comparison_record_count"] == 1200
    assert framed["exact_product_record_digest_sha256"] == (
        "87afe07ba51448f4827854908fe5c6fde851ee0ce919ec107e8fd2a50d36d3f7"
    )
    assert framed["exact_comparison_record_digest_sha256"] == (
        "d3ca632166e3c2c69b947837056b5b6e416baf8160da4958dfd11e8f5d3d125c"
    )
    assert "8-byte big-endian" in framed["algorithm"]
    assert len(audit["comparison_records"]) == 1200


def test_q011w_phase_resolves_every_individual_modulus_overlap(
    q011w_cycle: dict[str, Any],
) -> None:
    audit = q011w_cycle["phase_sensitive_product_disk_audit"]

    assert audit["individual_modulus_separation_count"] == 436
    assert audit["complex_phase_separation_count"] == 764
    assert audit["unresolved_product_disk_overlap_count"] == 0
    assert audit["first_unresolved_product_disk_overlap"] is None
    assert audit["aggregate_category_counts"] == [
        {
            "aggregate_index": 0,
            "selected_type_counts": [0, 0, 0, 4],
            "individual_modulus_separation_count": 348,
            "complex_phase_separation_count": 140,
            "unresolved_product_disk_overlap_count": 0,
        },
        {
            "aggregate_index": 1,
            "selected_type_counts": [0, 0, 1, 3],
            "individual_modulus_separation_count": 88,
            "complex_phase_separation_count": 624,
            "unresolved_product_disk_overlap_count": 0,
        },
    ]
    assert {record["classification"] for record in audit["comparison_records"]} == {
        "individual_modulus_separation",
        "complex_phase_separation",
    }


def test_q011w_minimum_phase_separation_exceeds_the_registered_margin(
    q011w_cycle: dict[str, Any],
) -> None:
    audit = q011w_cycle["phase_sensitive_product_disk_audit"]
    minimum = _fraction(audit["minimum_complex_separation_lower"])
    phase_minimum = _fraction(audit["minimum_phase_only_separation_lower"])
    witness = audit["minimum_margin_witness"]

    assert minimum == phase_minimum
    assert minimum >= Fraction(1, 500)
    assert 0.004057 < float(minimum) < 0.004058
    assert witness["selected_type_counts"] == [0, 0, 0, 4]
    assert witness["source_identifiers"] == [
        "block=0;center=144",
        "block=0;center=144",
        "block=0;center=144",
        "block=0;center=145",
    ]
    assert witness["target_identifier"] == "block=0;center=137"
    assert witness["classification"] == "complex_phase_separation"


def test_q011w_accepts_exactly_the_degree_four_nonresonance_claim(
    q011w_cycle: dict[str, Any],
) -> None:
    theorem = q011w_cycle["theorem_consequence"]

    assert q011w_cycle["study_validity"] == "passed"
    assert q011w_cycle["hypothesis_outcome"] == "accepted"
    assert q011w_cycle["scientific_classification"] == q011w.ACCEPTED_CLASSIFICATION
    assert len(q011w_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011w_cycle["validity_gates"].values())
    assert len(q011w_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011w_cycle["hypothesis_gates"].values())
    assert q011w_cycle["failed_hypothesis_order"] == []
    assert theorem["both_degree_four_modulus_overlaps_are_phase_sensitively_eliminated"]
    assert theorem["degree_four_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == [2, 3, 4]
    assert theorem["missing_external_nonresonance_degrees"] == list(range(5, 91))
    assert theorem["degree_91_and_higher_modulus_tail_is_preserved"]
    assert not theorem["degrees_5_through_90_are_certified"]
    assert not theorem["an_actual_complex_resonance_is_established"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "no degree from 5 through 90" in q011w_cycle["claim_boundary"]
    assert "Q011x" in q011w_cycle["next_change"]


def test_q011w_cycle_has_reproducible_strict_json_digests(
    q011w_cycle: dict[str, Any],
) -> None:
    json.dumps(q011w_cycle, allow_nan=False)
    expected_stable_sections = {
        "input_digest_sha256": ("ed3eea9c2a0f5c07de59dbddb0579b2dbb36e15409c3372729efc1e0d65c7a8d"),
        "inventory_digest_sha256": (
            "51c97d78b13ba2d9e787f833fe0f3c805848723710096da566f569c2fd301416"
        ),
        "sector_digest_sha256": (
            "369ef47a86630f84d96033539d3a7a7e94b34a45a95a15cef6bde71174eaa455"
        ),
        "product_digest_sha256": (
            "182672f831dd715402b4f52ab9aa2628ff9eba09a3c4a8de07d32a10bf736476"
        ),
    }
    assert {
        name: q011w_cycle[name] for name in expected_stable_sections
    } == expected_stable_sections
    assert len(q011w_cycle["result_digest_sha256"]) == 64
    assert q011w_cycle["result_digest_sha256"] == (
        q011w.q011v.q011b._canonical_json_sha256(q011w._result_digest_sections(q011w_cycle))
    )


def test_q011w_artifact_records_degree_four_nonresonance_if_generated() -> None:
    runner_path = Path(q011w.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011w_degree4_phase_disks.json"
    if not artifact_path.exists():
        pytest.skip("Q011w artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["filename"] == ("q011w_degree4_phase_disks.py")
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["scientific_classification"] == q011w.ACCEPTED_CLASSIFICATION
    assert cycle["result_digest_sha256"] == (
        q011w.q011v.q011b._canonical_json_sha256(q011w._result_digest_sections(cycle))
    )
    json.dumps(artifact, allow_nan=False)
