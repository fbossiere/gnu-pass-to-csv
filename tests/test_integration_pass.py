from __future__ import annotations

import csv
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def _tool(name: str) -> str:
    path = shutil.which(name)
    if path is None:
        pytest.skip(f"{name} is required for the real pass/GPG integration test")
    return path


def _run(
    command: list[str],
    env: dict[str, str],
    *,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        capture_output=True,
        env=env,
        input=input_text,
        text=True,
        timeout=30,
    )


def test_real_pass_and_gpg_export(tmp_path: Path) -> None:
    pass_executable = _tool("pass")
    gpg_executable = _tool("gpg")
    gpgconf_executable = _tool("gpgconf")

    gnupg_home = tmp_path / "gnupg"
    gnupg_home.mkdir(mode=0o700)
    store = tmp_path / "password-store"
    output = tmp_path / "export.csv"
    env = os.environ.copy()
    env.update(
        {
            "GNUPGHOME": str(gnupg_home),
            "PASSWORD_STORE_DIR": str(store),
            "LC_ALL": "C",
        }
    )

    identity = "GNU Pass CSV Tests <tests@example.invalid>"
    try:
        _run(
            [
                gpg_executable,
                "--batch",
                "--pinentry-mode",
                "loopback",
                "--passphrase",
                "",
                "--quick-generate-key",
                identity,
                "rsa2048",
                "encr",
                "0",
            ],
            env,
        )
        key_listing = _run(
            [
                gpg_executable,
                "--batch",
                "--with-colons",
                "--list-secret-keys",
                identity,
            ],
            env,
        )
        fingerprint = next(
            line.split(":")[9]
            for line in key_listing.stdout.splitlines()
            if line.startswith("fpr:")
        )

        _run([pass_executable, "init", fingerprint], env)
        _run(
            [
                pass_executable,
                "insert",
                "--multiline",
                "--force",
                "Work/example.com/alice",
            ],
            env,
            input_text=(
                "integration-secret\n"
                "username: alice\n"
                "email: alice@example.com\n"
                "url: https://example.com/login\n"
                "totp: JBSWY3DPEHPK3PXP\n"
                "synthetic integration note\n"
            ),
        )

        completed = _run(
            [
                sys.executable,
                "-m",
                "gnu_pass_to_csv",
                "--password-store-dir",
                str(store),
                "--output",
                str(output),
                "--vault",
                "Integration",
            ],
            env,
        )
    finally:
        subprocess.run(
            [gpgconf_executable, "--kill", "gpg-agent"],
            capture_output=True,
            env=env,
            text=True,
            timeout=10,
            check=False,
        )

    assert "Exported 1 entries" in completed.stdout
    assert "plaintext passwords" in completed.stderr
    assert "integration-secret" not in completed.stdout
    assert "integration-secret" not in completed.stderr
    assert stat.S_IMODE(output.stat().st_mode) == 0o600

    with output.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)

    assert reader.fieldnames == [
        "name",
        "url",
        "email",
        "username",
        "password",
        "note",
        "totp",
        "vault",
    ]
    assert rows == [
        {
            "name": "Work/example.com/alice",
            "url": "https://example.com/login",
            "email": "alice@example.com",
            "username": "alice",
            "password": "integration-secret",
            "note": "synthetic integration note",
            "totp": "JBSWY3DPEHPK3PXP",
            "vault": "Integration",
        }
    ]
