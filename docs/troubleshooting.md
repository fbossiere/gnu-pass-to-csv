# Troubleshooting

## Installation and startup

### `gnu-pass-to-csv: command not found`

Confirm that the tool directory used by `pipx` or `uv` is on your `PATH`, then
run the installer-specific command that exposes its location:

```bash
pipx ensurepath
uv tool dir --bin
```

Restart the shell after changing `PATH`.

### `Could not find the pass executable 'pass'`

Install the standard `pass` command through your operating system, or provide a
compatible executable explicitly:

```bash
gnu-pass-to-csv \
  --pass-executable /absolute/path/to/pass \
  --output ~/Downloads/proton-pass-import.csv
```

## Password-store discovery

### `Password store does not exist`

Check `PASSWORD_STORE_DIR` and `--password-store-dir`. The explicit option wins
when both are present.

### `No .gpg entries found in password store`

Confirm that the selected directory is the root of the intended `pass` store
and contains `.gpg` entry files. Test the same store directly:

```bash
PASSWORD_STORE_DIR=/path/to/store pass ls
```

## GPG and decryption

### `pass could not decrypt entry ...`

Run `pass show -- <entry>` directly with the same `PASSWORD_STORE_DIR`. Check
your GPG key availability, trust, `gpg-agent`, and pinentry configuration. The
exporter does not accept a passphrase option and cannot repair GPG setup.

### `Timed out while decrypting entry ...`

Complete any pending pinentry prompt. If decryption is legitimately slow, retry
with a larger positive timeout:

```bash
gnu-pass-to-csv \
  --output ~/Downloads/proton-pass-import.csv \
  --timeout 120
```

### Several pinentry prompts appear

Return to the default `--max-workers 1`, or unlock all required keys with
`pass show` before choosing parallel workers.

## Output safety

### `Output already exists`

Choose a new destination. Use `--force` only when replacing that exact plaintext
file is intentional.

### `Refusing to write a plaintext export inside the encrypted password store`

Choose a destination outside the store. Placing a `.csv` beside encrypted `.gpg`
entries would defeat the store's confidentiality boundary.

### File permissions are not `0600`

The exporter applies `0600` on POSIX systems. Some network, removable, Windows,
or unusual mounted filesystems do not enforce POSIX permissions equivalently.
Move the export to a local encrypted filesystem with appropriate access control.

## Import results

### A field is empty or mapped incorrectly

Compare a synthetic entry with [Entry mapping](entry-mapping.md). Add an
explicit recognized label when a heuristic is ambiguous. Never paste a real
decrypted entry or CSV row into a public issue.

### Some entries are missing

Check standard error for skipped names. Missing entries are possible only after
an explicitly partial run with `--skip-errors`; without it, any failed entry
aborts the complete export.

## Getting support

Follow the redaction checklist in
[`SUPPORT.md`](https://github.com/fbossiere/gnu-pass-to-csv/blob/main/SUPPORT.md).
Security vulnerabilities belong in GitHub's private vulnerability reporting
flow, not in a public issue.
