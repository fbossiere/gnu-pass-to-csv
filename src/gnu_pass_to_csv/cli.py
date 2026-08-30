"""Command-line interface for gnu-pass-to-csv."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path

from gnu_pass_to_csv import __version__
from gnu_pass_to_csv.backend import PassClient, PassError
from gnu_pass_to_csv.exporter import ExportError, export_passwords


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI parser."""
    default_store = os.environ.get("PASSWORD_STORE_DIR", "~/.password-store")
    parser = argparse.ArgumentParser(
        prog="gnu-pass-to-csv",
        description=(
            "Export a pass password store to a Proton Pass-compatible generic CSV."
        ),
        epilog=(
            "The output contains plaintext credentials. Import it promptly, verify the "
            "result, and delete it securely."
        ),
    )
    parser.add_argument(
        "-s",
        "--password-store-dir",
        type=Path,
        default=Path(default_store),
        help=f"password-store directory (default: {default_store})",
    )
    parser.add_argument(
        "-o",
        "--output",
        "--output-csv",
        type=Path,
        required=True,
        help="destination CSV path (required; must be outside the password store)",
    )
    parser.add_argument(
        "--vault",
        default="Personal",
        help="vault value written to every CSV row (default: Personal)",
    )
    parser.add_argument(
        "--max-workers",
        type=_positive_int,
        default=1,
        help="parallel pass processes (default: 1; unlock gpg-agent first)",
    )
    parser.add_argument(
        "--pass-executable",
        default="pass",
        help="pass executable name or path (default: pass)",
    )
    parser.add_argument(
        "--timeout",
        type=_positive_float,
        default=60.0,
        help="per-entry decryption timeout in seconds (default: 60)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing output file",
    )
    parser.add_argument(
        "--skip-errors",
        action="store_true",
        help="write a partial export when entries fail (disabled by default)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the exporter and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    store_dir = args.password_store_dir.expanduser()
    output = args.output.expanduser()
    client = PassClient(
        store_dir=store_dir,
        executable=args.pass_executable,
        timeout=args.timeout,
    )

    print(
        "WARNING: the output CSV contains plaintext passwords; handle it as a secret.",
        file=sys.stderr,
    )
    try:
        summary = export_passwords(
            client,
            store_dir,
            output,
            vault=args.vault,
            max_workers=args.max_workers,
            force=args.force,
            skip_errors=args.skip_errors,
        )
    except (ExportError, OSError, PassError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("error: interrupted", file=sys.stderr)
        return 130

    print(f"Exported {summary.exported} entries to {summary.output}")
    if summary.skipped:
        print(
            f"WARNING: skipped {len(summary.skipped)} entries: "
            + ", ".join(summary.skipped),
            file=sys.stderr,
        )
    return 0


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


if __name__ == "__main__":
    raise SystemExit(main())
