from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from gnu_pass_to_csv.backend import PassClient, PassEntryError, PassNotFoundError


def test_show_uses_pass_agent_and_selected_store() -> None:
    completed = subprocess.CompletedProcess(
        args=["pass"], returncode=0, stdout="secret\n", stderr=""
    )
    with patch("gnu_pass_to_csv.backend.subprocess.run", return_value=completed) as run:
        result = PassClient(Path("/store"), timeout=12).show("Work/example")

    assert result == "secret\n"
    command = run.call_args.args[0]
    options = run.call_args.kwargs
    assert command == ["pass", "show", "--", "Work/example"]
    assert options["env"]["PASSWORD_STORE_DIR"] == "/store"
    assert options["timeout"] == 12
    assert "passphrase" not in " ".join(command).lower()


def test_show_reports_missing_executable() -> None:
    with (
        patch("gnu_pass_to_csv.backend.subprocess.run", side_effect=FileNotFoundError),
        pytest.raises(PassNotFoundError, match="missing-pass"),
    ):
        PassClient(Path("/store"), executable="missing-pass").show("entry")


def test_show_reports_timeout_without_secret_output() -> None:
    timeout = subprocess.TimeoutExpired(["pass"], timeout=1, output="do-not-leak")
    with (
        patch("gnu_pass_to_csv.backend.subprocess.run", side_effect=timeout),
        pytest.raises(PassEntryError, match="Timed out") as error,
    ):
        PassClient(Path("/store")).show("entry")

    assert "do-not-leak" not in str(error.value)


def test_show_reports_nonzero_exit_without_stderr() -> None:
    completed = subprocess.CompletedProcess(
        args=["pass"], returncode=2, stdout="", stderr="sensitive diagnostic"
    )
    with (
        patch("gnu_pass_to_csv.backend.subprocess.run", return_value=completed),
        pytest.raises(PassEntryError, match="exit code 2") as error,
    ):
        PassClient(Path("/store")).show("entry")

    assert "sensitive diagnostic" not in str(error.value)


def test_show_reports_non_utf8_output() -> None:
    with (
        patch(
            "gnu_pass_to_csv.backend.subprocess.run",
            side_effect=UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid"),
        ),
        pytest.raises(PassEntryError, match="not valid UTF-8"),
    ):
        PassClient(Path("/store")).show("entry")
