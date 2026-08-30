# Security model and limitations

## Protected by design

- GPG authentication remains in the user's existing `pass` and `gpg-agent` flow.
- The exporter does not accept passphrases, invoke a shell, access the network, or
  emit telemetry.
- The destination is not created if any entry fails by default.
- Output is deterministic, private (`0600` on POSIX), and atomically installed.
- Existing files require `--force`; plaintext inside the encrypted store is
  refused.
- Tests use only synthetic data, and CI never receives password-store secrets.

## Residual risks

The CSV and decrypted strings exist as plaintext. Python and subprocess memory
cannot be reliably zeroized. A privileged local actor, debugger, crash dump,
filesystem backup, malware process, or compromised `pass` executable may observe
them. Entry names appear in process arguments and may contain identifying data.
Mode `0600` is a POSIX permission and may not provide the same guarantee on every
mounted filesystem.

CSV cells are preserved exactly because changing a password would corrupt the
migration. A cell beginning with `=`, `+`, `-`, or `@` may be interpreted as a
formula by spreadsheet software. Do not open exports in a spreadsheet; import
them directly into Proton Pass.

`--skip-errors` deliberately creates an incomplete migration. `--max-workers`
may cause multiple agent prompts when entries use different keys. URL, username,
email, and TOTP extraction is heuristic; always verify a representative sample
after import before removing the source store.

## Safer operating procedure

1. Update `pass`, GnuPG, Python, and this package from trusted sources.
2. Run `pass show` once and verify the intended store and key.
3. Write the export to a local, non-synced directory on an encrypted filesystem.
4. Import immediately and verify login, note, and TOTP examples.
5. Remove the CSV and account for backups, trash, snapshots, and sync history.

