"""Parse decrypted pass entries into the Proton Pass generic CSV schema."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

CSV_FIELDS = ("name", "url", "email", "username", "password", "note", "totp", "vault")

_EMAIL_RE = re.compile(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
_URL_RE = re.compile(
    r"(?<!@)\b(?:https?://|www\.)[^\s<>\"]+"
    r"|(?<!@)\b(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,}(?:/[^\s<>\"]*)?"
)
_DOMAIN_RE = re.compile(
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,}"
)
_KEY_NORMALIZER_RE = re.compile(r"[\s_-]+")

_FIELD_ALIASES = {
    "email": "email",
    "emailaddress": "email",
    "login": "username",
    "otp": "totp",
    "otpsecret": "totp",
    "otpauth": "totp",
    "site": "url",
    "totp": "totp",
    "uri": "url",
    "url": "url",
    "user": "username",
    "username": "username",
    "website": "url",
}


class EmptyEntryError(ValueError):
    """Raised when a decrypted entry has no password line."""


@dataclass(frozen=True, slots=True)
class PasswordRecord:
    """One row in a Proton Pass generic CSV import."""

    name: str
    url: str
    email: str
    username: str
    password: str
    note: str
    totp: str
    vault: str

    def as_dict(self) -> dict[str, str]:
        """Return field names and values for ``csv.DictWriter``."""
        return asdict(self)


def parse_entry(entry_name: str, decrypted: str, vault: str) -> PasswordRecord:
    """Parse one decrypted ``pass`` entry.

    The first line remains the password. Recognized, case-insensitive metadata labels
    populate CSV fields; unrecognized lines remain in the note.
    """
    lines = decrypted.splitlines()
    if not lines or not lines[0]:
        raise EmptyEntryError(f"Entry {entry_name!r} has no password line")

    values: dict[str, str] = {"email": "", "username": "", "url": "", "totp": ""}
    note_lines: list[str] = []
    metadata_lines = lines[1:]

    for line in metadata_lines:
        if line.strip().lower().startswith("otpauth://") and not values["totp"]:
            values["totp"] = line.strip()
            continue
        parsed = _recognized_field(line)
        if parsed is not None:
            field, value = parsed
            if value and not values[field]:
                values[field] = value
            continue
        note_lines.append(line)

    searchable_metadata = "\n".join(metadata_lines)
    if not values["email"]:
        email_match = _EMAIL_RE.search(searchable_metadata)
        values["email"] = email_match.group(0) if email_match else ""
    if not values["url"]:
        url_match = _URL_RE.search(searchable_metadata)
        values["url"] = url_match.group(0).rstrip(".,);]") if url_match else ""
    if not values["url"]:
        values["url"] = _url_from_entry_name(entry_name)
    if not values["username"]:
        values["username"] = values["email"]

    return PasswordRecord(
        name=entry_name,
        url=values["url"],
        email=values["email"],
        username=values["username"],
        password=lines[0],
        note="\n".join(_trim_blank_edges(note_lines)),
        totp=values["totp"],
        vault=vault,
    )


def _recognized_field(line: str) -> tuple[str, str] | None:
    key, separator, value = line.partition(":")
    if not separator:
        return None
    normalized_key = _KEY_NORMALIZER_RE.sub("", key.strip().lower())
    field = _FIELD_ALIASES.get(normalized_key)
    if field is None:
        return None
    return field, value.strip()


def _url_from_entry_name(entry_name: str) -> str:
    for component in reversed(entry_name.split("/")):
        if _DOMAIN_RE.fullmatch(component):
            return component
    return ""


def _trim_blank_edges(lines: list[str]) -> list[str]:
    start = 0
    end = len(lines)
    while start < end and not lines[start].strip():
        start += 1
    while end > start and not lines[end - 1].strip():
        end -= 1
    return lines[start:end]
