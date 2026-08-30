from __future__ import annotations

import pytest

from gnu_pass_to_csv.models import EmptyEntryError, parse_entry


def test_parse_labeled_fields_and_keep_unknown_notes() -> None:
    record = parse_entry(
        "Work/example.com/alice",
        "secret\n"
        "URL: https://example.com/login\n"
        "Email Address: alice@example.com\n"
        "login: alice-id\n"
        "OTP Secret: JBSWY3DPEHPK3PXP\n"
        "custom field: keep me\n"
        "\n"
        "recovery code is elsewhere\n",
        "Migrated",
    )

    assert record.name == "Work/example.com/alice"
    assert record.url == "https://example.com/login"
    assert record.email == "alice@example.com"
    assert record.username == "alice-id"
    assert record.password == "secret"
    assert record.note == "custom field: keep me\n\nrecovery code is elsewhere"
    assert record.totp == "JBSWY3DPEHPK3PXP"
    assert record.vault == "Migrated"


def test_parse_infers_email_url_and_username_from_free_text() -> None:
    record = parse_entry(
        "Personal/account",
        "secret\nContact alice@example.net at https://login.example.net/path).\n",
        "Personal",
    )

    assert record.email == "alice@example.net"
    assert record.username == "alice@example.net"
    assert record.url == "https://login.example.net/path"
    assert record.note.startswith("Contact alice@example.net")


def test_parse_infers_domain_from_any_entry_path_component() -> None:
    record = parse_entry("Personal/example.org/alice", "secret\n", "Personal")

    assert record.url == "example.org"
    assert record.note == ""


def test_parse_extracts_unlabeled_otpauth_uri() -> None:
    uri = "otpauth://totp/Example:alice?secret=ABC&issuer=Example"
    record = parse_entry("example", f"secret\n{uri}\nnotes\n", "Personal")

    assert record.totp == uri
    assert record.note == "notes"


def test_parse_uses_first_value_for_repeated_recognized_fields() -> None:
    record = parse_entry(
        "example",
        "secret\nusername: first\nUser: second\nURL:\nwebsite: example.com\n",
        "Personal",
    )

    assert record.username == "first"
    assert record.url == "example.com"


def test_parse_trims_only_edge_blank_note_lines() -> None:
    record = parse_entry(
        "example",
        "secret\n\nfirst note\n\nsecond note\n\n",
        "Personal",
    )

    assert record.note == "first note\n\nsecond note"


@pytest.mark.parametrize("decrypted", ["", "\nnotes only"])
def test_parse_rejects_entry_without_password(decrypted: str) -> None:
    with pytest.raises(EmptyEntryError, match="no password line"):
        parse_entry("empty", decrypted, "Personal")
