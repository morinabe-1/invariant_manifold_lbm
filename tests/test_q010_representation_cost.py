from __future__ import annotations

import research.q010_representation_cost as q010


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
