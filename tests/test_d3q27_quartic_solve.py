"""Known-solution controls; the formal all-1120-case campaign is separate."""

import numpy as np
import pytest

from research import d3q27_quartic_solve as s


@pytest.mark.parametrize("external", (23, 27))
@pytest.mark.parametrize(
    "groups", ((0, 0, 0, 0), (0, 0, 0, 1), (0, 0, 1, 1), (0, 0, 1, 2), (0, 1, 2, 3))
)
def test_known_solutions_for_every_pattern_and_both_external_dimensions(external, groups):
    record, arrays = s.solve_known((2, 2, 2, 2), groups, external)
    assert record["passed"]
    assert len(record["structural"]["slot_permutation_errors"]) == 24
    assert record["svd_diagnosis"]["numerical_rank"] == external * len(arrays["d"])
    assert record["svd_diagnosis"]["condition_number"] <= 1e8
    assert len(record["refinement_history"]) == 4
    assert record["initial_sylvester_is_diagnostic_only"]
    for method in ("svd", "refined"):
        assert record["methods"][method]["passed"]
        np.testing.assert_allclose(arrays[method], arrays["known"], atol=1e-10, rtol=1e-10)
        assert not np.any(arrays[method + "_full"][:8])
        assert not np.any(arrays[method + "_full"][-4:])
        assert record["methods"][method]["exact_external"]["gates"]["exact_decimal_constants"]
        assert record["methods"][method]["full_residual_passed"]
        assert record["methods"][method]["full_relative_tolerance"] == "1e-9"


def test_one_dimensional_blocks_and_all_negative_classifications():
    record, arrays = s.solve_known((1, 1, 1, 1), (0, 1, 2, 3), 23)
    assert record["passed"] and arrays["d"].shape == (1, 1)
    negatives = s.negative_controls()
    assert negatives["passed"] and len(negatives["cases"]) == 3
    assert [row["observed"]["status"] for row in negatives["cases"]] == [
        "singular_compatible",
        "singular_incompatible",
        "nonsingular_ill_conditioned",
    ]
    assert not any(row["observed"]["passed"] for row in negatives["cases"])


def test_corrupted_solution_is_rejected_by_both_exact_kernels():
    a, d, f, x = np.array([[0.25]]), np.array([[0.5]]), np.array([[0.25]]), np.array([[1.01]])
    proof, _, _ = s.residual_evidence(a, d, f, x)
    assert not any(proof["gates"][name] for name in s.exact.EXACT_GATES)


def test_full_and_external_thresholds_are_not_conflated():
    proof, _, _ = s.residual_evidence(
        np.eye(1), np.zeros((1, 1)), np.eye(1), np.array([[-1 + 5e-10]])
    )
    assert not proof["gates"]["exact_decimal_constants"]
    assert s.full_residual_passed(proof)


def test_disagreeing_exact_kernel_is_not_silently_accepted(monkeypatch):
    monkeypatch.setattr(s.exact, "audit_gmp", lambda *args: {"fabricated": True})
    with pytest.raises(ValueError, match="disagree"):
        s.residual_evidence(np.eye(1), 0.5 * np.eye(1), -0.5 * np.eye(1), np.eye(1))
