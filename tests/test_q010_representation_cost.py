from __future__ import annotations

import json
from pathlib import Path

import pytest

import research.q010_representation_cost as q010


@pytest.fixture(scope="module")
def q010_artifact() -> dict:
    artifact_path = (
        Path(q010.__file__).resolve().parent
        / "artifacts"
        / "q010_representation_cost.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


def test_q010_registered_protocol_is_fixed() -> None:
    assert q010.HOLDOUT_SEED == 20260901
    assert q010.HOLDOUT_DIRECTION_COUNT == 16
    assert q010.OFFLINE_WARMUP_BLOCKS == 1
    assert q010.OFFLINE_MEASURED_BLOCKS == 3
    assert q010.ONLINE_WARMUP_BLOCKS == 1
    assert q010.ONLINE_MEASURED_BLOCKS == 5
    assert q010.MAXIMUM_CHECKSUM_RELATIVE_ERROR == 1.0e-11
    assert q010.MINIMUM_MEDIAN_ONLINE_SLOWDOWN == 2.0
    assert len(q010.TT_CANDIDATE_IDS) == 8
    assert q010.METHOD_IDS[:2] == (
        "sparse-fiber",
        "ordered-dense-control",
    )


def test_q010_first_median_break_even_handles_all_cost_line_cases() -> None:
    assert q010._first_median_break_even(5.0, 2.0, 6.0, 1.0) == 0
    assert q010._first_median_break_even(10.0, 3.0, 5.0, 2.0) is None
    assert q010._first_median_break_even(10.0, 1.0, 4.0, 3.0) == 3
    assert q010._first_median_break_even(10.1, 1.0, 4.0, 3.0) == 4


def test_q010_registered_q008_inputs_are_sealed() -> None:
    _, audit = q010._load_registered_inputs(
        q010._default_artifact_directory()
    )

    assert audit["passed"]
    assert audit["observed_package_source_sha256"] == (
        q010.REGISTERED_PACKAGE_SOURCE_SHA256
    )
    assert all(
        record["sha256_matches"]
        and record["source_match"]
        and record["scope_match"]
        and record["classification_match"]
        and record["all_validity_gates_pass"]
        and record["all_candidate_fidelity_passes"]
        and record["selected_candidate_is_none"]
        for record in audit["artifacts"].values()
    )


def test_q010_break_even_audit_requires_strict_envelope_dominance() -> None:
    sparse_storage = {
        "coefficient_stored_real_scalar_count": 10,
        "raw_array_payload_bytes": 100,
        "uncompressed_npz_serialized_bytes": 120,
    }
    candidate_storage = {
        "core_stored_real_scalar_count": 20,
        "raw_array_payload_bytes": 200,
        "uncompressed_npz_serialized_bytes": 240,
    }
    offline_records = {
        q010.SPARSE_METHOD_ID: {
            "minimum_nanoseconds": 8,
            "maximum_nanoseconds": 10,
            "median_nanoseconds": 9.0,
            "storage": sparse_storage,
        },
        q010.DENSE_METHOD_ID: {
            "minimum_nanoseconds": 18,
            "maximum_nanoseconds": 20,
            "median_nanoseconds": 19.0,
            "storage": {},
        },
    }
    online_records = {
        q010.SPARSE_METHOD_ID: {
            "minimum_nanoseconds_per_sample": 4.0,
            "maximum_nanoseconds_per_sample": 5.0,
            "median_nanoseconds_per_sample": 4.5,
        },
        q010.DENSE_METHOD_ID: {
            "minimum_nanoseconds_per_sample": 19.0,
            "maximum_nanoseconds_per_sample": 21.0,
            "median_nanoseconds_per_sample": 20.0,
        },
    }
    for candidate_id in q010.TT_CANDIDATE_IDS:
        offline_records[candidate_id] = {
            "minimum_nanoseconds": 11,
            "maximum_nanoseconds": 13,
            "median_nanoseconds": 12.0,
            "storage": candidate_storage,
        }
        online_records[candidate_id] = {
            "minimum_nanoseconds_per_sample": 10.0,
            "maximum_nanoseconds_per_sample": 12.0,
            "median_nanoseconds_per_sample": 11.0,
        }

    audit = q010._break_even_audit(
        {"method_records": offline_records},
        {"method_records": online_records},
    )

    assert audit["all_tt_storage_strictly_dominated"]
    assert audit["all_tt_offline_envelopes_strictly_dominated"]
    assert audit[
        "all_tt_online_envelopes_and_slowdowns_strictly_dominated"
    ]
    assert audit["all_tt_have_robust_no_finite_sparse_time_break_even"]
    assert audit["candidate_beating_time_and_storage_count"] == 0
    assert all(
        not record[
            "storage_strictly_beats_sparse_in_all_registered_metrics"
        ]
        for record in audit["candidate_records"].values()
    )
    assert audit["passed"]


def test_q010_artifact_seals_the_registered_cost_campaign(
    q010_artifact: dict,
) -> None:
    cycle = q010_artifact["cycle"]

    assert q010_artifact["study_gate"] == "passed"
    assert q010_artifact["scientific_outcome"] == "accepted"
    assert q010_artifact["runner_source"]["sha256"] == (
        "c6e99082a3418d604f7d09687685cf5e6ab9efe341ea36153123bb8ad4b26b4e"
    )
    assert cycle["input_digest_sha256"] == (
        "566d3ce0569736c140dae7c4f19d36223957e5ad2b25abc4b9d6a012558d0841"
    )
    assert cycle["result_digest_sha256"] == (
        "79545f0cbf14a53fef52d46bc44cbb8586efb95e1b6645d7c8cc00b45ceed6dc"
    )
    assert cycle["study_validity"] == "passed"
    assert cycle["hypothesis_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "sealed TT-SVD path is cost-dominated by natural quartic "
        "sparse-fiber"
    )
    assert len(cycle["validity_gates"]) == 6
    assert all(
        gate["passed"] for gate in cycle["validity_gates"].values()
    )
    assert len(cycle["hypothesis_gates"]) == 5
    assert all(
        gate["passed"] for gate in cycle["hypothesis_gates"].values()
    )
    assert cycle["direction_audit"]["exact_duplicate_count_vs_prior"] == 0
    assert cycle["protocol_audit"]["passed"]
    assert cycle["break_even_audit"]["passed"]
    assert cycle["selected_candidate"] is None
    consequence = cycle["decision_consequence"]
    assert consequence[
        "fixed_q007c1_tt_svd_path_cost_dominated_in_campaign"
    ]
    assert consequence[
        "q009_tt_cross_remains_held_for_fixed_coefficients"
    ]
    assert consequence["natural_sparse_fiber_remains_mandatory_baseline"]
    assert not consequence["ordered_dense_control_interpreted_as_full_lbm"]


def test_q010_artifact_digests_recompute_from_sealed_records(
    q010_artifact: dict,
) -> None:
    cycle = q010_artifact["cycle"]
    input_payload = {
        "artifact_sha256": {
            name: record["sha256"]
            for name, record in cycle["input_audit"]["artifacts"].items()
        },
        "package_source_sha256": q010.REGISTERED_PACKAGE_SOURCE_SHA256,
        "quartic_coefficient_sha256": (
            q010.REGISTERED_QUARTIC_COEFFICIENT_SHA256
        ),
        "candidate_ids": list(q010.TT_CANDIDATE_IDS),
        "method_ids": list(q010.METHOD_IDS),
        "holdout": cycle["direction_audit"],
        "offline_protocol": {
            "warmup_blocks": q010.OFFLINE_WARMUP_BLOCKS,
            "measured_blocks": q010.OFFLINE_MEASURED_BLOCKS,
        },
        "online_protocol": {
            "warmup_blocks": q010.ONLINE_WARMUP_BLOCKS,
            "measured_blocks": q010.ONLINE_MEASURED_BLOCKS,
            "checksum_tolerance": q010.MAXIMUM_CHECKSUM_RELATIVE_ERROR,
            "minimum_median_slowdown": (
                q010.MINIMUM_MEDIAN_ONLINE_SLOWDOWN
            ),
        },
    }
    input_digest = q010._digest_payload(input_payload)
    result_payload = {
        "input_digest": input_digest,
        "common_input": cycle["common_input_audit"],
        "fidelity": cycle["fresh_fidelity_audit"],
        "offline": cycle["offline_cost_campaign"],
        "online": cycle["online_cost_campaign"],
        "protocol": cycle["protocol_audit"],
        "break_even": cycle["break_even_audit"],
    }

    assert input_digest == cycle["input_digest_sha256"]
    assert q010._digest_payload(result_payload) == cycle[
        "result_digest_sha256"
    ]
