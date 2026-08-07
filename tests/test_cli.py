from __future__ import annotations

import json
import sys

import pytest

from ttim_lbm.__main__ import main


def test_q004b_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q004b", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q005_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q005", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006s_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006s", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006s_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006s"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006s_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006s"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006r_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006r", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006r_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006r"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006r_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006r"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006n_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006n", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006n_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006n"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006n_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006n"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006c_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006c", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006c_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006c"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006c_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006c"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006f_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006f", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006f_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006f"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006f_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006f"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006g_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006g", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006g_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006g"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006g_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006g"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006h_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006h", "--omega", "1.2"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006h_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006h"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006h_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006h"])

    main()

    assert json.loads(capsys.readouterr().out) == expected
