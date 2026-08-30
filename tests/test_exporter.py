from __future__ import annotations

import csv
import stat
from pathlib import Path

import pytest

from gnu_pass_to_csv.exporter import (
    ExportError,
    discover_entries,
    export_passwords,
)


class FakeReader:
    def __init__(self, entries: dict[str, str | Exception]) -> None:
        self.entries = entries

    def show(self, entry_name: str) -> str:
        value = self.entries[entry_name]
        if isinstance(value, Exception):
            raise value
        return value


def create_store(root: Path, *entries: str) -> Path:
    store = root / "store"
    for entry in entries:
        target = store / f"{entry}.gpg"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()
    return store


def test_discover_entries_is_recursive_and_deterministic(tmp_path: Path) -> None:
    store = create_store(tmp_path, "z-last", "Folder/a-first", "name.with.dots")

    assert discover_entries(store) == ["Folder/a-first", "name.with.dots", "z-last"]


def test_export_writes_atomic_private_deterministic_csv(tmp_path: Path) -> None:
    store = create_store(tmp_path, "z-last", "Folder/a-first")
    reader = FakeReader(
        {
            "z-last": "z-password\nusername: zoe\n",
            "Folder/a-first": "a-password\nemail: alice@example.com\n",
        }
    )
    output = tmp_path / "result" / "export.csv"

    summary = export_passwords(
        reader,
        store,
        output,
        vault="Personal",
        max_workers=2,
    )

    assert summary.exported == 2
    assert summary.skipped == ()
    assert stat.S_IMODE(output.stat().st_mode) == 0o600
    with output.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert [row["name"] for row in rows] == ["Folder/a-first", "z-last"]
    assert rows[0]["password"] == "a-password"
    assert not list(output.parent.glob("*.tmp"))


def test_export_aborts_without_partial_file_on_failure(tmp_path: Path) -> None:
    store = create_store(tmp_path, "good", "bad")
    reader = FakeReader({"good": "secret\n", "bad": RuntimeError("decrypt failed")})
    output = tmp_path / "export.csv"

    with pytest.raises(ExportError, match="Export aborted"):
        export_passwords(reader, store, output, vault="Personal")

    assert not output.exists()


def test_export_can_explicitly_skip_failures(tmp_path: Path) -> None:
    store = create_store(tmp_path, "good", "bad")
    reader = FakeReader({"good": "secret\n", "bad": RuntimeError("decrypt failed")})
    output = tmp_path / "export.csv"

    summary = export_passwords(
        reader,
        store,
        output,
        vault="Personal",
        skip_errors=True,
    )

    assert summary.exported == 1
    assert summary.skipped == ("bad",)
    assert output.exists()


def test_parallel_export_can_explicitly_skip_failures(tmp_path: Path) -> None:
    store = create_store(tmp_path, "good", "bad")
    reader = FakeReader({"good": "secret\n", "bad": RuntimeError("decrypt failed")})

    summary = export_passwords(
        reader,
        store,
        tmp_path / "export.csv",
        vault="Personal",
        max_workers=2,
        skip_errors=True,
    )

    assert summary.exported == 1
    assert summary.skipped == ("bad",)


def test_export_refuses_to_overwrite_without_force(tmp_path: Path) -> None:
    store = create_store(tmp_path, "entry")
    reader = FakeReader({"entry": "new-secret\n"})
    output = tmp_path / "export.csv"
    output.write_text("original", encoding="utf-8")

    with pytest.raises(ExportError, match="already exists"):
        export_passwords(reader, store, output, vault="Personal")

    assert output.read_text(encoding="utf-8") == "original"


def test_export_replaces_with_force(tmp_path: Path) -> None:
    store = create_store(tmp_path, "entry")
    reader = FakeReader({"entry": "new-secret\n"})
    output = tmp_path / "export.csv"
    output.write_text("original", encoding="utf-8")

    export_passwords(reader, store, output, vault="Personal", force=True)

    assert "new-secret" in output.read_text(encoding="utf-8")
    assert stat.S_IMODE(output.stat().st_mode) == 0o600


def test_export_refuses_plaintext_inside_store(tmp_path: Path) -> None:
    store = create_store(tmp_path, "entry")

    with pytest.raises(ExportError, match="inside the encrypted password store"):
        export_passwords(
            FakeReader({"entry": "secret\n"}),
            store,
            store / "export.csv",
            vault="Personal",
        )


def test_export_rejects_invalid_worker_count(tmp_path: Path) -> None:
    store = create_store(tmp_path, "entry")

    with pytest.raises(ExportError, match="at least 1"):
        export_passwords(
            FakeReader({"entry": "secret\n"}),
            store,
            tmp_path / "export.csv",
            vault="Personal",
            max_workers=0,
        )


def test_export_rejects_when_every_entry_fails(tmp_path: Path) -> None:
    store = create_store(tmp_path, "bad")

    with pytest.raises(ExportError, match="no entries"):
        export_passwords(
            FakeReader({"bad": RuntimeError("decrypt failed")}),
            store,
            tmp_path / "export.csv",
            vault="Personal",
            skip_errors=True,
        )


def test_discover_rejects_missing_empty_and_file_paths(tmp_path: Path) -> None:
    with pytest.raises(ExportError, match="does not exist"):
        discover_entries(tmp_path / "missing")

    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(ExportError, match=r"No \.gpg"):
        discover_entries(empty)

    file_path = tmp_path / "file"
    file_path.touch()
    with pytest.raises(ExportError, match="not a directory"):
        discover_entries(file_path)
