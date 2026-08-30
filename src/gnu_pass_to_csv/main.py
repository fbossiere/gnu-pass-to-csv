"""Backward-compatible import for the command-line entry point."""

from gnu_pass_to_csv.cli import main

app = main

__all__ = ["app", "main"]


if __name__ == "__main__":
    raise SystemExit(main())
