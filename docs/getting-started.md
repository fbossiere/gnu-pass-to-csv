# Getting started

This guide installs GNU pass to CSV, creates a Proton Pass-compatible export,
and walks through the plaintext cleanup boundary.

## Prerequisites

- Linux or macOS.
- Python 3.11 or newer.
- A working [`pass`](https://www.passwordstore.org/) installation.
- An initialized password store with at least one `.gpg` entry.
- Proton Pass with access to **Settings → Import**.

## 1. Verify `pass` first

Before installing the exporter, confirm that your normal `pass` and `gpg-agent`
flow can decrypt a synthetic or non-sensitive test entry:

```bash
pass show -- path/to/test-entry
```

Resolve any GPG, pinentry, or password-store issue before continuing. The
exporter deliberately does not add another passphrase mechanism.

## 2. Install a reviewed release

=== "pipx"

    ```bash
    pipx install gnu-pass-to-csv==2.0.0
    ```

=== "uv"

    ```bash
    uv tool install gnu-pass-to-csv==2.0.0
    ```

Confirm the installed command and version:

```bash
gnu-pass-to-csv --version
```

To work on the project itself, follow [Development](development.md) instead.

## 3. Choose a safe destination

Use a local, non-synced directory on an encrypted filesystem. The destination
must be outside the password store, and the output path is always explicit.

!!! danger "Treat the destination as a secret"

    Do not use a cloud-synced folder, shared directory, source repository, or
    network drive. The CSV is readable plaintext even though the source entries
    remain encrypted.

## 4. Export the store

The default store is `PASSWORD_STORE_DIR` when set, otherwise
`~/.password-store`:

```bash
gnu-pass-to-csv --output ~/Downloads/proton-pass-import.csv
```

A successful run reports the number of exported entries and the destination:

```text
WARNING: the output CSV contains plaintext passwords; handle it as a secret.
Exported 42 entries to /home/alice/Downloads/proton-pass-import.csv
```

For a custom store and vault:

```bash
gnu-pass-to-csv \
  --password-store-dir ~/.password-store-work \
  --output ~/Downloads/work-import.csv \
  --vault Work
```

## 5. Import into Proton Pass

1. Open Proton Pass.
2. Choose **Settings → Import**.
3. Select **Generic CSV**.
4. Import the generated file.
5. Verify representative logins, notes, nested names, and TOTP entries.

Do not remove the source password store until you have verified the migration.
The exporter targets login entries; it does not represent cards, identities,
aliases, attachments, or arbitrary custom fields.

## 6. Remove the plaintext export

Remove the CSV after verification and account for copies in trash, backups,
snapshots, recent-file lists, and sync history. A normal file deletion or
overwrite is not a guaranteed secure erase on SSDs, copy-on-write filesystems,
or backed-up volumes.

Read the [security model](security.md) for the residual risks that remain during
and after a migration.
