from __future__ import annotations

import json

import numpy as np
import pytest

from ttim_lbm.coefficient_scaling import (
    ACOUSTIC_SELF,
    FIT_WINDOWS,
    SHEAR_DIAGONAL,
    audit_scaling_condition,
    run_coefficient_scaling_audit,
)


@pytest.fixture(scope="module")
def scaling_audit() -> dict[str, object]:
    return run_coefficient_scaling_audit()


def _complex_array(record: list[list[float]]) -> np.ndarray:
    return np.asarray([real + 1j * imag for real, imag in record])


def _complex_matrix(record: list[list[list[float]]]) -> np.ndarray:
    return np.asarray(
        [[real + 1j * imag for real, imag in row] for row in record]
    )


def test_reference_condition_reproduces_q006n_and_identifies_registered_orbits() -> None:
    condition = audit_scaling_condition(17, 1.2)

    assert condition["pair_count"] == 136
    assert condition["pair_enumeration_complete"]
    assert condition["target_pair_count"] == 16
    assert condition["target_pair_counts_by_class"] == {
        ACOUSTIC_SELF: 8,
        SHEAR_DIAGONAL: 8,
    }
    assert condition["numerically_singular_external_block_count"] == 0
    assert max(
        summary["maximum_relative_spread"]
        for summary in condition["orbit_summaries"].values()
    ) < 1.0e-8

    acoustic = next(
        record
        for record in condition["target_pairs"]
        if record["pair_identifier"] == "p00016"
    )
    assert acoustic["target_class"] == ACOUSTIC_SELF
    assert acoustic["smallest_singular_value"] == pytest.approx(
        0.019335067599085428,
        rel=1.0e-12,
    )
    assert acoustic["condition_number"] == pytest.approx(
        96.02046557474952,
        rel=1.0e-12,
    )
    assert acoustic["local_amplitude_response_norm"] == pytest.approx(
        23.79367005736206,
        rel=1.0e-12,
    )
    assert acoustic["global_l2_response_norm"] == pytest.approx(
        1.3996276504330625,
        rel=1.0e-12,
    )


def test_stored_pair_system_reconstructs_svd_and_solve() -> None:
    condition = audit_scaling_condition(17, 1.2)
    record = next(
        item
        for item in condition["target_pairs"]
        if item["pair_identifier"] == "p00012"
    )
    operator = _complex_matrix(record["operator"])
    forcing = _complex_array(record["forcing_vector"])
    response = _complex_array(record["minimum_norm_response"])
    left_singular = _complex_matrix(record["left_singular_vectors"])
    right_adjoint = _complex_matrix(record["right_adjoint_singular_vectors"])

    singular_values = np.linalg.svd(operator, compute_uv=False)
    assert singular_values == pytest.approx(record["singular_values"], rel=1.0e-13)
    assert np.linalg.norm(
        left_singular @ np.diag(record["singular_values"]) @ right_adjoint
        - operator
    ) / np.linalg.norm(operator) < 1.0e-12
    assert np.linalg.norm(operator @ response - forcing) / np.linalg.norm(
        forcing
    ) < 1.0e-12
    assert np.linalg.norm(response) == pytest.approx(
        record["local_amplitude_response_norm"],
        rel=1.0e-13,
    )


def test_registered_fit_table_uses_only_the_sealed_window(
    scaling_audit: dict[str, object],
) -> None:
    audit = scaling_audit

    assert len(audit["conditions"]) == 20
    assert len(audit["fits"]) == 8
    for fit in audit["fits"]:
        assert set(fit["metrics"]) == set(FIT_WINDOWS)
        for metric, record in fit["metrics"].items():
            assert record["grid_sizes"] == [33, 65, 129, 257]
            assert record["registered_window"] == list(FIT_WINDOWS[metric])
            assert np.isfinite(record["slope"])


def test_all_registered_power_windows_pass(
    scaling_audit: dict[str, object],
) -> None:
    audit = scaling_audit

    assert audit["summary"]["spectral_scaling_passed"]
    assert audit["summary"]["forcing_response_scaling_passed"]
    assert audit["summary"]["all_registered_scaling_windows_passed"]
    assert all(
        fit["all_registered_windows_passed"] for fit in audit["fits"]
    )


def test_sealed_campaign_accepts_only_the_registered_scaling_claim(
    scaling_audit: dict[str, object],
) -> None:
    audit = scaling_audit
    summary = audit["summary"]

    assert audit["study_validity"] == "passed"
    assert audit["hypothesis_outcome"] == "accepted"
    assert (
        audit["scientific_classification"]
        == "genuine weakly-forced small-k resonance supported"
    )
    assert all(gate["passed"] for gate in audit["validity_gates"].values())
    assert summary["n257_materially_forced_near_witness_count"] == 56
    assert summary["n257_outside_target_witness_count"] == 0
    assert summary["maximum_target_condition_number"] == pytest.approx(
        182598.05569576463,
        rel=1.0e-10,
    )
    assert summary["maximum_condition_number"] > 1.0e8


def test_campaign_record_is_strict_json(
    scaling_audit: dict[str, object],
) -> None:
    rendered = json.dumps(scaling_audit, allow_nan=False)
    assert "global_l2_response_norm" in rendered
    assert "n257_witness_completeness" in rendered


@pytest.mark.parametrize(
    ("size", "omega"),
    [(9, 1.2), (33, 1.1), (513, 1.8)],
)
def test_condition_audit_rejects_unregistered_parameters(
    size: int,
    omega: float,
) -> None:
    with pytest.raises(ValueError, match="sealed Q006c"):
        audit_scaling_condition(size, omega)
