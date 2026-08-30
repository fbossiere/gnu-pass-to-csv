# gnu-pass-to-csv

[![CI](https://github.com/fbossiere/gnu-pass-to-csv/actions/workflows/ci.yml/badge.svg)](https://github.com/fbossiere/gnu-pass-to-csv/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/gnu-pass-to-csv)](https://pypi.org/project/gnu-pass-to-csv/)
[![Python](https://img.shields.io/pypi/pyversions/gnu-pass-to-csv)](https://pypi.org/project/gnu-pass-to-csv/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Diagram showing an encrypted pass folder converted to a Proton Pass CSV without passphrase handling](https://raw.githubusercontent.com/fbossiere/gnu-pass-to-csv/main/docs/assets/github-social-preview.png)

Export a [`pass`](https://www.passwordstore.org/) password store to a
Proton Pass-compatible generic CSV. It is for people migrating login entries
from the standard Unix password manager to Proton Pass. Unlike the previous
implementation, it delegates decryption to `pass` and `gpg-agent`: the tool never
asks for, stores, or forwards a GPG passphrase.

- Preserves nested entry names and extracts common URL, email, username, note,
  and TOTP fields.
- Produces deterministic UTF-8 CSV files with private `0600` permissions.
- Fails atomically on a decryption error unless a partial export is explicitly
  requested.

> [!CAUTION]
> The generated CSV contains every exported password in plaintext. Import it
> promptly, verify the result, then remove the file according to your system's
> secure-data handling policy. Do not commit, sync, email, or open it in an
> online spreadsheet.

## Quick start

Requirements: Linux or macOS, Python 3.11+, a working `pass` installation, and
an initialized password store that `pass show <entry>` can decrypt.

```console
$ pipx install gnu-pass-to-csv
$ gnu-pass-to-csv --output ~/Downloads/proton-pass-import.csv
WARNING: the output CSV contains plaintext passwords; handle it as a secret.
Exported 42 entries to /home/alice/Downloads/proton-pass-import.csv
```

In Proton Pass, choose **Settings → Import → Generic CSV**, import the file,
verify a representative sample including TOTP entries, and remove the CSV.

`pipx` is recommended because it keeps command-line applications isolated. A
regular installation also works:

```console
python -m pip install gnu-pass-to-csv
```

## How entries are mapped

Given a `pass` entry named `Work/example.com/alice`:

```text
example-password
username: alice
email: alice@example.com
url: https://example.com/login
totp: JBSWY3DPEHPK3PXP
recovery codes are stored offline
```

the exporter writes one row with this schema:

```text
name,url,email,username,password,note,totp,vault
```

The first decrypted line is always the password. Metadata labels are
case-insensitive; `url`, `uri`, `website`, `email`, `username`, `user`, `login`,
`totp`, `otp`, and `otp-secret` are recognized. Unknown lines remain in `note`.
When no URL label exists, the exporter looks for a URL in the entry and then for
a domain-shaped component in the entry name.

The output is intended for Proton Pass **Generic CSV** login imports. It does not
represent cards, identities, aliases, attachments, or arbitrary custom fields.

## Usage

```console
gnu-pass-to-csv --help
```

Common options:

| Option | Purpose |
| --- | --- |
| `-o, --output PATH` | Required destination; must be outside the password store |
| `-s, --password-store-dir PATH` | Store location; defaults to `PASSWORD_STORE_DIR` or `~/.password-store` |
| `--vault NAME` | Value written to the CSV `vault` column; default `Personal` |
| `--force` | Replace an existing output file |
| `--skip-errors` | Create an explicitly partial export when entries fail |
| `--max-workers N` | Run several `pass` processes after unlocking `gpg-agent`; default `1` |
| `--pass-executable PATH` | Select a compatible `pass` executable |
| `--timeout SECONDS` | Per-entry timeout; default `60` |

Use a custom store either way:

```console
PASSWORD_STORE_DIR=~/.password-store-work \
  gnu-pass-to-csv --output ~/Downloads/work-import.csv --vault Work

gnu-pass-to-csv \
  --password-store-dir ~/.password-store-work \
  --output ~/Downloads/work-import.csv \
  --vault Work
```

The output is never written inside the encrypted store. Existing files are not
overwritten without `--force`. By default, any failed or empty entry aborts the
whole export before the destination file is created.

## Security model

The exporter discovers `.gpg` files but reads their plaintext only through the
fixed command `pass show -- <entry>`. It does not invoke a shell and does not
accept a passphrase option or environment variable. Authentication and prompts
remain the responsibility of the user's existing `gpg-agent` configuration.

Plaintext necessarily exists in process memory and in the final CSV. Temporary
output is created in the destination directory with mode `0600`, flushed, and
atomically installed. Filenames can still reveal account or service names in
errors and process arguments; the tool never logs decrypted content.

See [the detailed security model](docs/security.md), the
[architecture](docs/architecture.md), and the [security policy](SECURITY.md).

## Version 2 migration

Version 2 is intentionally incompatible with 1.x:

- `--passphrase` and `GPG_PASSPHRASE` were removed because command arguments can
  expose secrets to other local processes and diagnostics.
- `pass` is now required and handles all GPG interaction through `gpg-agent`.
- `--output` is required and refuses accidental overwrite or placement inside
  the encrypted store.
- Runtime dependencies were removed; Python 3.11 through 3.14 are tested.

## Development and support

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the reproducible local quality gate,
[SUPPORT.md](SUPPORT.md) for usage help, and [CHANGELOG.md](CHANGELOG.md) for
release history. Security reports belong in GitHub's private vulnerability
reporting flow, not in public issues.

This independent project is not affiliated with, sponsored by, or endorsed by
Proton AG or the password-store project. “Proton Pass” is used only to describe
the supported import format.

## License

[MIT](LICENSE)
