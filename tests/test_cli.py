from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from gnu_pass_to_csv import main as legacy_main
from gnu_pass_to_csv.cli import build_parser, main
from gnu_pass_to_csv.exporter import ExportError, ExportSummary


def test_cli_runs_export_and_reports_summary(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    store = tmp_path / "store"
    output = tmp_path / "out.csv"
    summary = ExportSummary(2, ("failed",), output)

    with patch("gnu_pass_to_csv.cli.export_passwords", return_value=summary) as export:
        exit_code = main(
            [
                "--password-store-dir",
                str(store),
                "--output",
                str(output),
                "--vault",
                "Migrated",
                "--max-workers",
                "2",
                "--force",
                "--skip-errors",
            ]
        )

    assert exit_code == 0
    assert export.call_args.kwargs["vault"] == "Migrated"
    assert export.call_args.kwargs["max_workers"] == 2
    assert export.call_args.kwargs["force"] is True
    captured = capsys.readouterr()
    assert "Exported 2 entries" in captured.out
    assert "plaintext passwords" in captured.err
    assert "skipped 1 entries" in captured.err


def test_cli_reports_export_error(capsys: pytest.CaptureFixture[str]) -> None:
    with patch(
        "gnu_pass_to_csv.cli.export_passwords",
        side_effect=ExportError("safe failure"),
    ):
        exit_code = main(["--output", "out.csv"])

    assert exit_code == 1
    assert "error: safe failure" in capsys.readouterr().err


def test_cli_reports_filesystem_error(capsys: pytest.CaptureFixture[str]) -> None:
    with patch(
        "gnu_pass_to_csv.cli.export_passwords",
        side_effect=PermissionError("read-only destination"),
    ):
        exit_code = main(["--output", "out.csv"])

    assert exit_code == 1
    assert "read-only destination" in capsys.readouterr().err


def test_cli_reports_keyboard_interrupt(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("gnu_pass_to_csv.cli.export_passwords", side_effect=KeyboardInterrupt):
        exit_code = main(["--output", "out.csv"])

    assert exit_code == 130
    assert "interrupted" in capsys.readouterr().err


@pytest.mark.parametrize("option", ["--max-workers", "--timeout"])
@pytest.mark.parametrize("value", ["0", "-1"])
def test_cli_rejects_non_positive_numeric_options(option: str, value: str) -> None:
    with pytest.raises(SystemExit) as error:
        build_parser().parse_args(["--output", "out.csv", option, value])

    assert error.value.code == 2


def test_cli_uses_password_store_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PASSWORD_STORE_DIR", "/custom/store")

    args = build_parser().parse_args(["--output", "out.csv"])

    assert args.password_store_dir == Path("/custom/store")


def test_legacy_main_module_exposes_entry_point() -> None:
    assert legacy_main.app is legacy_main.main
