"""Discover, decrypt, parse, and atomically export password-store entries."""

from __future__ import annotations

import csv
import os
import tempfile
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from gnu_pass_to_csv.models import CSV_FIELDS, PasswordRecord, parse_entry


class EntryReader(Protocol):
    """A source capable of decrypting a named password-store entry."""

    def show(self, entry_name: str) -> str:
        """Return the decrypted entry."""


class ExportError(RuntimeError):
    """Raised when a safe, complete export cannot be produced."""


@dataclass(frozen=True, slots=True)
class ExportSummary:
    """Non-secret result details for a completed export."""

    exported: int
    skipped: tuple[str, ...]
    output: Path


def discover_entries(store_dir: Path) -> list[str]:
    """Return deterministic pass entry names from a password-store directory."""
    store_dir = store_dir.expanduser()
    if not store_dir.exists():
        raise ExportError(f"Password store does not exist: {store_dir}")
    if not store_dir.is_dir():
        raise ExportError(f"Password store is not a directory: {store_dir}")

    entries = [
        path.relative_to(store_dir).with_suffix("").as_posix()
        for path in store_dir.rglob("*.gpg")
        if path.is_file()
    ]
    entries.sort()
    if not entries:
        raise ExportError(f"No .gpg entries found in password store: {store_dir}")
    return entries


def export_passwords(  # noqa: PLR0913 - explicit public API options
    reader: EntryReader,
    store_dir: Path,
    output: Path,
    *,
    vault: str,
    max_workers: int = 1,
    force: bool = False,
    skip_errors: bool = False,
) -> ExportSummary:
    """Create a plaintext CSV, failing atomically unless skipping is explicit."""
    if max_workers < 1:
        raise ExportError("max_workers must be at least 1")
    output = output.expanduser()
    _ensure_output_outside_store(store_dir.expanduser(), output)
    entries = discover_entries(store_dir)

    records: list[PasswordRecord] = []
    failures: list[tuple[str, Exception]] = []

    if max_workers == 1:
        for entry_name in entries:
            _collect_entry(reader, entry_name, vault, records, failures)
    else:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_read_entry, reader, entry_name, vault): entry_name
                for entry_name in entries
            }
            for future in as_completed(futures):
                entry_name = futures[future]
                try:
                    records.append(future.result())
                except Exception as error:  # noqa: BLE001 - summarized without secrets
                    failures.append((entry_name, error))

    failures.sort(key=lambda item: item[0])
    if failures and not skip_errors:
        first_entry, first_error = failures[0]
        raise ExportError(
            f"Export aborted: {len(failures)} of {len(entries)} entries failed; "
            f"first failure was {first_entry!r}: {first_error}"
        ) from first_error
    if not records:
        raise ExportError("Export aborted: no entries were decrypted successfully")

    records.sort(key=lambda record: record.name)
    write_csv(records, output, force=force)
    return ExportSummary(
        exported=len(records),
        skipped=tuple(entry_name for entry_name, _ in failures),
        output=output,
    )


def write_csv(records: Iterable[PasswordRecord], output: Path, *, force: bool) -> None:
    """Write a mode-0600 CSV through an atomic same-directory temporary file."""
    output = output.expanduser()
    output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="",
            prefix=f".{output.name}.",
            suffix=".tmp",
            dir=output.parent,
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            temporary_path.chmod(0o600)
            writer = csv.DictWriter(
                temporary,
                fieldnames=CSV_FIELDS,
                extrasaction="raise",
                quoting=csv.QUOTE_ALL,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(record.as_dict() for record in records)
            temporary.flush()
            os.fsync(temporary.fileno())

        if force:
            temporary_path.replace(output)
        else:
            try:
                os.link(temporary_path, output)
            except FileExistsError as error:
                raise ExportError(
                    f"Output already exists: {output}; use --force to replace it"
                ) from error
            temporary_path.unlink()
        output.chmod(0o600)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def _read_entry(reader: EntryReader, entry_name: str, vault: str) -> PasswordRecord:
    return parse_entry(entry_name, reader.show(entry_name), vault)


def _collect_entry(
    reader: EntryReader,
    entry_name: str,
    vault: str,
    records: list[PasswordRecord],
    failures: list[tuple[str, Exception]],
) -> None:
    try:
        records.append(_read_entry(reader, entry_name, vault))
    except Exception as error:  # noqa: BLE001 - summarized without secrets
        failures.append((entry_name, error))


def _ensure_output_outside_store(store_dir: Path, output: Path) -> None:
    resolved_store = store_dir.resolve(strict=False)
    resolved_output = output.resolve(strict=False)
    try:
        resolved_output.relative_to(resolved_store)
    except ValueError:
        return
    raise ExportError(
        "Refusing to write a plaintext export inside the encrypted password store"
    )
