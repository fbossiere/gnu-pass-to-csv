# Entry mapping

Each decrypted `pass` entry becomes one Proton Pass generic CSV login row.

## Example

Given an entry named `Work/example.com/alice`:

```text
correct horse battery staple
username: alice
email: alice@example.com
url: https://example.com/login
totp: JBSWY3DPEHPK3PXP
recovery codes are stored offline
```

the exporter writes the schema:

```text
name,url,email,username,password,note,totp,vault
```

with these values:

| CSV field | Value |
| --- | --- |
| `name` | `Work/example.com/alice` |
| `url` | `https://example.com/login` |
| `email` | `alice@example.com` |
| `username` | `alice` |
| `password` | First decrypted line |
| `note` | `recovery codes are stored offline` |
| `totp` | `JBSWY3DPEHPK3PXP` |
| `vault` | The value passed to `--vault`, default `Personal` |

All examples here are synthetic. Do not copy real credentials into an issue or
documentation change.

## Recognized labels

Labels are case-insensitive, and spaces, `_`, and `-` are ignored when matching.
The first non-empty value recognized for a field wins.

| Destination | Recognized labels |
| --- | --- |
| `url` | `url`, `uri`, `website`, `site` |
| `email` | `email`, `email address` |
| `username` | `username`, `user`, `login` |
| `totp` | `totp`, `otp`, `otp secret`, `otpauth` |

A standalone `otpauth://...` line also populates `totp`. Recognized metadata
lines are removed from the note; unknown lines remain in their original order.

## Fallbacks

- If `email` is missing, the first email-shaped value in metadata is used.
- If `url` is missing, the first URL or domain-shaped value in metadata is used.
- If no URL appears in metadata, domain-shaped components of the entry name are
  checked from right to left.
- If `username` is missing, the resolved email becomes the username.
- If no field can be resolved, its CSV cell is empty.

## Output behavior

- Entry names preserve their complete path below the password store.
- Rows are sorted by entry name.
- Every field is quoted in UTF-8 CSV output.
- Embedded commas, quotes, and newlines are preserved by standard CSV quoting.
- Formula-like values beginning with `=`, `+`, `-`, or `@` are preserved exactly.

!!! danger "Do not inspect the export in a spreadsheet"

    Spreadsheet software may interpret formula-like cells. Import the file
    directly into Proton Pass instead of opening it in Excel, Google Sheets, or
    another spreadsheet application.
