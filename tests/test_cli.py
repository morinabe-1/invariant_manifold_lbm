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


def test_q006i_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006i", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006i_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006i"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006i_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006i"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006j_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006j", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006j_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006j"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006j_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006j"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006k_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006k", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006k_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006k"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006k_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006k"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006l_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006l", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006l_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006l"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006l_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006l"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006m_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006m", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006m_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006m"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006m_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006m"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006o_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006o", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006o_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006o"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006o_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006o"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006p_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006p", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006p_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006p"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006p_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006p"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q006q_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q006q", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q006q_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q006q"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q006q_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q006q"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q007a_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q007a", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q007a_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q007a"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q007a_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q007a"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q007b_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q007b", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q007b_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q007b"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q007b_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q007b"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q007b1_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q007b1", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q007b1_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q007b1"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q007b1_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q007b1"])

    main()

    assert json.loads(capsys.readouterr().out) == expected


def test_q007c_rejects_an_omega_override(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        ["ttim_lbm", "--study", "q007c", "--omega", "1.5"],
    )
    with pytest.raises(SystemExit, match="2"):
        main()
    assert "--omega is only valid with --study baseline" in capsys.readouterr().err


def test_q007c_dispatches_the_registered_study(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    expected = {"study_gate": "passed", "cycle": {"question": "q007c"}}
    monkeypatch.setattr("ttim_lbm.__main__.run_q007c_study", lambda: expected)
    monkeypatch.setattr(sys, "argv", ["ttim_lbm", "--study", "q007c"])

    main()

    assert json.loads(capsys.readouterr().out) == expected
