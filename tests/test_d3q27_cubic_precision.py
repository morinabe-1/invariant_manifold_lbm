"""Independent controls for Q012f1 input realification and accurate residuals."""

import subprocess
import sys

import numpy as np
import pytest

from research import d3q27_chart as chart
from research import d3q27_cubic as cubic
from research import d3q27_cubic_precision as precision
from research import q012f1_d3q27_cubic_precision as runner


@pytest.fixture(scope="module")
def inputs():
    original = chart.build_chart()
    paired, audit = precision.paired_input(original)
    return original, paired, audit


def test_prior_rejection_and_registered_selection():
    assert runner.input_audit()["passed"]
    selected = runner.selection()
    assert len(selected["ordinals"]) == 324
    assert len(selected["replay_ordinals"]) == 32
    assert len(selected["original_failure_ordinals"]) == 272
    assert set(selected["original_failure_ordinals"]) <= set(selected["ordinals"])
    assert set(selected["replay_ordinals"]) <= set(selected["ordinals"])
    for ordinal in selected["ordinals"]:
        assert precision.conjugate_ordinal(ordinal) in selected["ordinals"]


def test_all_triple_conjugations_are_involutions():
    for ordinal in range(cubic.TRIPLE_COUNT):
        assert precision.conjugate_ordinal(precision.conjugate_ordinal(ordinal)) == ordinal


def test_paired_projection_is_real_idempotent_and_does_not_mutate(inputs):
    original, paired, audit = inputs
    assert audit["passed"]
    partners = precision.pair_partners(original)
    assert np.array_equal(paired.hessian_fibers, paired.hessian_fibers[partners].conj())
    assert np.array_equal(
        paired.reduced_fibers, paired.reduced_fibers[partners][:, chart.CONJUGATE_COMPONENT].conj()
    )
    assert not np.shares_memory(original.hessian_fibers, paired.hessian_fibers)
    assert original.pair_jets is not paired.pair_jets
    assert np.array_equal(original.forcing_fibers, paired.forcing_fibers)
    assert np.array_equal(original.complex_linear, paired.complex_linear)


def test_paired_input_matches_the_real_part_of_the_original_field(inputs):
    original, paired, _ = inputs
    u = chart.normalized_directions(2026090723, 1)[0]
    np.testing.assert_allclose(
        paired.quadratic_field(u), original.quadratic_field(u), rtol=2e-12, atol=1e-16
    )
    np.testing.assert_allclose(paired.reduced(u), original.reduced(u), rtol=2e-12, atol=1e-16)
    h, _, g = paired.pair_loop(u)
    np.testing.assert_allclose(
        paired.physical(h), paired.quadratic_field(u), rtol=2e-12, atol=1e-16
    )
    np.testing.assert_allclose(g, paired.reduced_quadratic_fourier(u), rtol=2e-12, atol=1e-16)


def test_all_paired_quadratic_equations_are_rechecked(inputs):
    audit = precision.quadratic_audit(inputs[1])
    assert len(audit["records"]) == 3081
    assert audit["forcing_unchanged"]
    assert audit["failed_count"] == sum(not r["passed"] for r in audit["records"])
    for row in audit["records"]:
        assert row["passed"] == (
            row["external_relative_residual"] <= 1e-10
            and row["full_relative_residual"] <= 1e-9
            and row["structural_error"] <= 5e-12
        )


def test_mpc_residual_recovers_product_bits_lost_in_float64():
    a = np.array([[1 + 2**-52]], dtype=complex)
    x = a.copy()
    d = np.zeros((1, 1), dtype=complex)
    f = np.array([[-(1 + 2**-51)]], dtype=complex)
    assert (a @ x + f)[0, 0] == 0
    assert precision.residual_mpc(a, d, f, x)[0, 0] == 2**-104
    assert np.array_equal(
        precision.residual_mpc(a, d, f, x), precision.residual_mpc(a, d, f, x, 192)
    )
    with pytest.raises(ValueError):
        precision.residual_mpc(a, d, f, x, 53)


def test_known_complex_and_near_resonant_controls():
    controls = precision.known_controls()
    assert controls["passed"]
    assert all(len(r["history"]) == 4 for r in controls["positive"])
    assert all(not r["solve"]["passed"] for r in controls["negative"])


@pytest.mark.parametrize("ordinal", [0, 897, 54019])
def test_same_problem_three_solvers_and_precision_crosscheck(inputs, ordinal):
    context = cubic.build_context(inputs[0])
    result, sample = precision.solve_case(context, ordinal, True)
    assert set(result["solvers"]) == set(precision.SOLVERS)
    assert result["solvers"]["refined"]["precision_crosscheck"]["passed"]
    assert len(result["refinement_history"]) == 4
    for solver in precision.SOLVERS:
        assert np.array_equal(
            sample["fields"][solver]["forcing"], sample["fields"]["svd"]["forcing"]
        )
        assert sample["fields"][solver]["response"].shape[1] == 27


def test_selected_conjugacy_keeps_small_imaginary_defects():
    conjugate = np.array([1, 0])
    triples = np.array([[0, 0, 0], [1, 1, 1]])
    waves = np.array([[1, 0, 0], [-1, 0, 0]])
    forcing = np.zeros((2, 27), dtype=complex)
    forcing[0, 0] = 1e-7j
    result = precision.selected_conjugacy(triples, waves, {"forcing": forcing}, conjugate)
    assert result["coverage"] and not result["passed"]
    assert result["fields"]["forcing"]["failed_count"] == 2


def test_cli_refuses_existing_evidence(tmp_path):
    path = tmp_path / "existing.json"
    path.write_text("preserved", encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "research.q012f1_d3q27_cubic_precision",
            "--worker-output",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert path.read_text(encoding="utf-8") == "preserved"


@pytest.mark.parametrize(
    "status", ["singular_compatible", "singular_incompatible", "nonsingular_ill_conditioned"]
)
def test_small_residual_does_not_override_a_failed_rank_condition_gate(inputs, monkeypatch, status):
    context = cubic.build_context(inputs[0])
    jet = cubic.solve_triple(context, 0)
    jet.record["status"], jet.record["passed"] = status, False
    original_solve = precision.fallback.solve_with_fallback

    def force_failed_gate(*args):
        value, record, backend = original_solve(*args)
        record["status"], record["passed"] = status, False
        return value, record, backend

    monkeypatch.setattr(cubic, "solve_triple", lambda *_: jet)
    monkeypatch.setattr(precision.fallback, "solve_with_fallback", force_failed_gate)
    record, _ = precision.solve_case(context, 0, False)
    assert all(not arm["passed"] for arm in record["solvers"].values())


def test_invalid_input_stops_before_any_diagnosis(monkeypatch):
    monkeypatch.setattr(runner, "input_audit", lambda: {"passed": False})
    monkeypatch.setattr(runner, "selection", dict)
    with pytest.raises(ValueError, match="not started"):
        runner.worker()
