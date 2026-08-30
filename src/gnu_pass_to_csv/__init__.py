"""Convert password-store entries to a Proton Pass-compatible CSV."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("gnu-pass-to-csv")
except PackageNotFoundError:  # pragma: no cover - source tree without installation
    __version__ = "0+unknown"

__all__ = ["__version__"]
