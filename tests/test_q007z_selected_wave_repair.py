from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import research.q007z_selected_wave_repair as q007z


@pytest.fixture(scope="module")
def q007z_artifact() -> dict:
    artifact_path = (
        Path(q007z.__file__).resolve().parent
        / "artifacts"
        / "q007z_selected_wave_repair.json"
    )
    return json.loads(artifact_path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("wave", q007z.SELECTED_WAVES)
def test_q007z_nonzero_selected_characters_cancel_on_the_full_grid(
    wave: tuple[int, int],
) -> None:
    histogram = q007z.phase_histogram(wave, q007z.WAVE_COUNT)

    assert wave != (0, 0)
    assert histogram == (q007z.SIZE,) * q007z.SIZE
    assert sum(histogram) == q007z.WAVE_COUNT


@pytest.mark.parametrize(
    ("wave", "site", "expected"),
    [
        ((1, 0), 0, 0),
        ((1, 0), 16, 16),
        ((1, 0), 17, 0),
        ((0, 1), 17, 1),
        ((-1, -1), 18, 15),
    ],
)
def test_q007z_phase_residue_uses_registered_row_major_order(
    wave: tuple[int, int],
    site: int,
    expected: int,
) -> None:
    assert q007z.phase_residue(wave, site) == expected


def test_q007z_phase_helpers_reject_invalid_arguments() -> None:
    with pytest.raises(TypeError, match="two integers"):
        q007z.phase_residue((True, 0), 0)
    with pytest.raises(TypeError, match="integer"):
        q007z.phase_residue((1, 0), 0.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="registered grid"):
        q007z.phase_residue((1, 0), 289)
    with pytest.raises(TypeError, match="integer"):
        q007z.phase_histogram((1, 0), True)
    with pytest.raises(ValueError, match="zero and 289"):
        q007z.phase_histogram((1, 0), 290)


def test_q007z_exhaustive_prefix_certificate_is_exact_and_float_free() -> None:
    audit = q007z._phase_histogram_audit()

    assert audit["selected_wave_count"] == 8
    assert audit["remainder_count_per_wave"] == 289
    assert audit["phase_histogram_case_count"] == 2312
    assert audit["balanced_distribution_case_count"] == 4624
    assert audit["maximum_prefix_or_complement_bound"] == 144
    assert audit["maximum_bound_witness_count"] == 16
    assert audit["phase_digest_sha256"] == (
        "f0da04edcc58edd6b96b2869ee67c79cc44b020278545bc52d03a142c0fa4a83"
    )
    assert not audit["uses_complex_float_in_proof"]
    assert all(
        record["full_grid_character_cancels_by_cyclotomic_identity"]
        and record["all_remainders_passed"]
        for record in audit["wave_records"]
    )
    assert audit["passed"]


def test_q007z_closes_the_conditional_repaired_backend_induction(
    q007z_artifact: dict,
) -> None:
    cycle = q007z_artifact["cycle"]

    assert cycle == q007z.run_selected_wave_repair_audit()
    assert q007z_artifact["study_gate"] == "passed"
    assert q007z_artifact["scientific_outcome"] == "accepted"
    assert cycle["scientific_classification"] == (
        "selected-wave certificate closes the repaired MPFR-85 fixed-leaf "
        "tube induction"
    )
    assert len(cycle["validity_gates"]) == 6
    assert all(gate["passed"] for gate in cycle["validity_gates"].values())
    assert len(cycle["hypothesis_gates"]) == 7
    assert all(gate["passed"] for gate in cycle["hypothesis_gates"].values())
    bound = cycle["selected_repair_bound"]
    assert Fraction(
        int(
            bound["per_selected_wave_population_l1_upper"][
                "numerator_base16"
            ],
            16,
        ),
        int(
            bound["per_selected_wave_population_l1_upper"][
                "denominator_base16"
            ],
            16,
        ),
    ) == 4 * Fraction(144, 289) * Fraction(1, 2**90)
    assert bound["repair_base_coordinate_error_upper"][
        "float"
    ] == pytest.approx(1.9216710236250915e-26)
    assert bound["base_margin_utilization"]["float"] == pytest.approx(
        0.8213071928437413
    )
    assert bound["normal_margin_utilization"]["float"] == pytest.approx(
        2.507922842743146e-7
    )
    assert bound["base_reentry_passed"]
    assert bound["normal_reentry_passed"]
    assert cycle["result_digest_sha256"] == (
        "62262fe2cfb0bf361e5b79aaf89c8ba319ad1df046bf59aff56be8b7a54d4054"
    )
    assert all(cycle["theorem_consequence"].values())
    assert "already encoded, repaired MPFR-85 state" in cycle["claim_boundary"]
