from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import pytest

import research.q011v_degree3_phase_disks as q011v
from ttim_lbm.provenance import source_metadata
from ttim_lbm.rational_spectrum import _file_sha256


def _fraction(record: dict[str, object]) -> Fraction:
    return Fraction(
        int(str(record["numerator_base16"]), 16),
        int(str(record["denominator_base16"]), 16),
    )


@pytest.fixture(scope="module")
def q011v_cycle() -> dict[str, Any]:
    return q011v.run_degree3_phase_disk_audit()


def test_q011v_seals_four_inputs_twenty_two_digests_and_helper_sources(
    q011v_cycle: dict[str, Any],
) -> None:
    audit = q011v_cycle["sealed_input_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["direct_digest_count"] == 22
    assert {
        label: audit[label]["hypothesis_outcome"]
        for label in ("q011j", "q011k", "q011m", "q011u")
    } == {
        "q011j": "accepted",
        "q011k": "accepted",
        "q011m": "accepted",
        "q011u": "rejected",
    }
    assert audit["helper_sources"] == {
        "q011l": {
            "filename": "q011l_interval_homological_inverse.py",
            "sha256": q011v.Q011L_SOURCE_SHA256,
        },
        "q011o": {
            "filename": "q011o_graph_transform_setup.py",
            "sha256": q011v.Q011O_SOURCE_SHA256,
        },
    }
    assert audit["checks"]["q011j_x_independent_fixed_point_scope_is_preserved"]
    assert audit["checks"]["q011k_eigendisc_scope_is_preserved"]
    assert audit["checks"]["q011m_derivative_and_sector_scope_is_preserved"]
    assert audit["checks"]["q011u_valid_rejection_scope_is_preserved"]


def test_q011v_reproduces_the_complete_degree_three_modulus_inventory(
    q011v_cycle: dict[str, Any],
) -> None:
    audit = q011v_cycle["degree3_modulus_inventory_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["degree"] == 3
    assert audit["degree_modulus_aggregate_count"] == 20
    assert audit["degree_expanded_product_control_count"] == 56
    assert audit["modulus_separated_aggregate_count"] == 19
    assert audit["modulus_overlap_aggregate_count"] == 1
    assert audit["sole_overlap_selected_type_counts"] == [0, 1, 1, 1]
    assert audit["sole_overlap_external_group_index"] == 183
    assert audit["selected_source_group_indices"] == [1, 2, 3]
    assert audit["selected_source_group_sizes"] == [4, 4, 8]
    assert audit["indexed_triple_count"] == 128
    assert len(audit["external_target_identifiers"]) == 8
    assert audit["eigencenter_reconstruction"]["eigencenter_count"] == 2598
    assert audit["eigencenter_reconstruction"]["selected_count"] == 24
    assert audit["eigencenter_reconstruction"]["external_count"] == 2574
    assert audit["eigencenter_reconstruction"][
        "exact_modulus_interval_digest_sha256"
    ] == "120d9214caa90d3eff168fca272ce8da3ee47eb5e11cbd65b0d462139b2d73fb"
    assert audit["exact_inventory_digest_sha256"] == (
        "8a0e025230faade977fcf04be45441f74cf32368089dabb3ddacce4e0349fc5b"
    )


def test_q011v_fourier_sector_filter_has_the_registered_complete_histograms(
    q011v_cycle: dict[str, Any],
) -> None:
    audit = q011v_cycle["fourier_output_sector_audit"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert all(audit["structural_proof"].values())
    assert audit["output_sector_law"] == "b_out=(b_1+b_2+b_3) mod 17"
    assert audit["indexed_triple_count"] == 128
    assert audit["triple_sector_histogram"] == {
        "0": 32,
        "1": 28,
        "2": 16,
        "3": 4,
        "14": 4,
        "15": 16,
        "16": 28,
    }
    assert audit["external_target_sector_histogram"] == {"0": 4, "2": 2, "15": 2}
    assert audit["sector_compatible_triple_count"] == 64
    assert audit["sector_incompatible_triple_count"] == 64
    assert audit["sector_compatible_comparison_count"] == 192
    assert audit["exact_sector_record_digest_sha256"] == (
        "3e372ba3750c06c2a4d48003e6c45bc96fd404cf76511412de9147de92bb2467"
    )


def test_q011v_product_disk_radius_expansion_is_exact_for_every_triple(
    q011v_cycle: dict[str, Any],
) -> None:
    audit = q011v_cycle["phase_sensitive_product_disk_audit"]
    records = audit["product_records"]

    assert audit["passed"]
    assert all(audit["checks"].values())
    assert audit["product_record_count"] == 128
    assert len(records) == 128
    assert all(record["radius_expansion_identity_reproduces"] for record in records)
    assert all(_fraction(record["product_radius"]) > 0 for record in records)
    assert all(
        0 < _fraction(record["product_modulus_lower"])
        <= _fraction(record["product_modulus_upper"])
        < 1
        for record in records
    )


def test_q011v_phase_resolves_every_individual_modulus_overlap(
    q011v_cycle: dict[str, Any],
) -> None:
    audit = q011v_cycle["phase_sensitive_product_disk_audit"]
    records = audit["comparison_records"]

    assert audit["comparison_record_count"] == 192
    assert len(records) == 192
    assert audit["individual_modulus_separation_count"] == 64
    assert audit["complex_phase_separation_count"] == 128
    assert audit["unresolved_product_disk_overlap_count"] == 0
    assert audit["first_unresolved_product_disk_overlap"] is None
    assert {record["classification"] for record in records} == {
        "individual_modulus_separation",
        "complex_phase_separation",
    }
    assert all(_fraction(record["complex_separation_margin_lower"]) > 0 for record in records)
    assert audit["exact_product_comparison_digest_sha256"] == (
        "dbb690b311e5ff065295c6e5ae42e46da05259c94e9e1a90b8d8c96a952c2a89"
    )


def test_q011v_minimum_phase_separation_has_the_registered_robust_margin(
    q011v_cycle: dict[str, Any],
) -> None:
    audit = q011v_cycle["phase_sensitive_product_disk_audit"]
    minimum = _fraction(audit["minimum_complex_separation_lower"])
    phase_minimum = _fraction(audit["minimum_phase_only_separation_lower"])
    witness = audit["minimum_margin_witness"]

    assert minimum == phase_minimum
    assert minimum >= Fraction(1, 10)
    assert 0.2015 < float(minimum) < 0.2016
    assert witness["source_identifiers"] == [
        "block=16;center=150",
        "block=0;center=148",
        "block=1;center=148",
    ]
    assert witness["target_identifier"] == "block=0;center=139"
    assert witness["classification"] == "complex_phase_separation"


def test_q011v_accepts_exactly_the_degree_three_nonresonance_claim(
    q011v_cycle: dict[str, Any],
) -> None:
    theorem = q011v_cycle["theorem_consequence"]

    assert q011v_cycle["study_validity"] == "passed"
    assert q011v_cycle["hypothesis_outcome"] == "accepted"
    assert q011v_cycle["scientific_classification"] == q011v.ACCEPTED_CLASSIFICATION
    assert len(q011v_cycle["validity_gates"]) == 7
    assert all(gate["passed"] for gate in q011v_cycle["validity_gates"].values())
    assert len(q011v_cycle["hypothesis_gates"]) == 5
    assert all(gate["passed"] for gate in q011v_cycle["hypothesis_gates"].values())
    assert q011v_cycle["failed_hypothesis_order"] == []
    assert theorem["the_sole_degree_three_modulus_overlap_is_phase_sensitively_eliminated"]
    assert theorem["degree_three_external_nonresonance_is_certified"]
    assert theorem["certified_external_nonresonance_degrees"] == [2, 3]
    assert theorem["missing_external_nonresonance_degrees"] == list(range(4, 91))
    assert theorem["degree_91_and_higher_modulus_tail_is_preserved"]
    assert not theorem["degrees_4_through_90_are_certified"]
    assert not theorem["an_actual_complex_resonance_is_established"]
    assert not theorem["all_spectral_quotient_nonresonances_are_certified"]
    assert not theorem["ssm_existence_or_uniqueness_is_certified"]
    assert "no degree from 4 through 90" in q011v_cycle["claim_boundary"]
    assert "Q011w" in q011v_cycle["next_change"]


def test_q011v_cycle_has_reproducible_strict_json_digests(
    q011v_cycle: dict[str, Any],
) -> None:
    json.dumps(q011v_cycle, allow_nan=False)
    expected = {
        "input_digest_sha256": (
            "10153049ce3cc7f50aa5a57ca6f4e8f92556bbefb3980e1d4c7dd61164aab470"
        ),
        "inventory_digest_sha256": (
            "591e6261238ac2253b0e0f11aaa13ce8a0c78948780633ea890a824ea9c5ccba"
        ),
        "sector_digest_sha256": (
            "8988ade3f1fc974423040a2fe168904eb6610897f281e681387da7e3e2d3e919"
        ),
        "product_digest_sha256": (
            "a93737bcf662b154fcbea83905d733628e1ae397f4f70265d811e7ce657665db"
        ),
        "result_digest_sha256": (
            "1a2a83c6ae0d6f512a48f5f6d20e869abd0b69126504adbf5ba50054e1b749fc"
        ),
    }
    assert {name: q011v_cycle[name] for name in expected} == expected
    assert q011v_cycle["result_digest_sha256"] == q011v.q011b._canonical_json_sha256(
        q011v._result_digest_sections(q011v_cycle)
    )


def test_q011v_artifact_records_degree_three_nonresonance_if_generated() -> None:
    runner_path = Path(q011v.__file__).resolve()
    artifact_path = runner_path.parent / "artifacts" / "q011v_degree3_phase_disks.json"
    if not artifact_path.exists():
        pytest.skip("Q011v artifact has not been generated yet")
    artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
    cycle = artifact["cycle"]

    assert artifact["schema_version"] == 1
    assert artifact["source"] == source_metadata()
    assert artifact["runner_source"]["sha256"] == _file_sha256(runner_path)
    assert artifact["study_gate"] == "passed"
    assert artifact["scientific_outcome"] == "accepted"
    assert cycle["scientific_classification"] == q011v.ACCEPTED_CLASSIFICATION
    assert cycle["result_digest_sha256"] == q011v.q011b._canonical_json_sha256(
        q011v._result_digest_sections(cycle)
    )
    json.dumps(artifact, allow_nan=False)
