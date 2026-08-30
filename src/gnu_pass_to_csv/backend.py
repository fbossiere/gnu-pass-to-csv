"""Safe, minimal adapter for the standard ``pass`` command."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


class PassError(RuntimeError):
    """Base class for password-store access failures."""


class PassNotFoundError(PassError):
    """Raised when the pass executable is unavailable."""


class PassEntryError(PassError):
    """Raised when pass cannot decrypt an entry."""


@dataclass(frozen=True, slots=True)
class PassClient:
    """Read entries through ``pass`` and its configured ``gpg-agent``."""

    store_dir: Path
    executable: str = "pass"
    timeout: float = 60.0

    def show(self, entry_name: str) -> str:
        """Decrypt and return one entry without accepting or forwarding a passphrase."""
        environment = os.environ.copy()
        environment["PASSWORD_STORE_DIR"] = str(self.store_dir)
        try:
            result = subprocess.run(
                [self.executable, "show", "--", entry_name],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="strict",
                env=environment,
                timeout=self.timeout,
            )
        except FileNotFoundError as error:
            raise PassNotFoundError(
                f"Could not find the pass executable {self.executable!r}"
            ) from error
        except subprocess.TimeoutExpired as error:
            raise PassEntryError(
                f"Timed out while decrypting entry {entry_name!r}"
            ) from error
        except UnicodeDecodeError as error:
            raise PassEntryError(
                f"Entry {entry_name!r} is not valid UTF-8 text"
            ) from error

        if result.returncode != 0:
            raise PassEntryError(
                f"pass could not decrypt entry {entry_name!r} "
                f"(exit code {result.returncode})"
            )
        return result.stdout
