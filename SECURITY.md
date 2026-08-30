# Security policy

## Supported versions

| Version | Supported |
| --- | --- |
| 2.x | Yes |
| 1.x and earlier | No |

Version 1.x accepted a GPG passphrase and forwarded it in a process argument.
Users should upgrade to 2.x, remove `GPG_PASSPHRASE` from shell profiles and
`.env` files, and rotate a passphrase if they believe it was exposed.

## Report a vulnerability privately

Use [GitHub private vulnerability reporting](https://github.com/fbossiere/gnu-pass-to-csv/security/advisories/new).
Do not include real passwords, private keys, passphrases, decrypted exports,
password-store archives, or unredacted home-directory paths. A minimal synthetic
entry and the affected version are sufficient.

Please include the impact, reproduction steps using fake data, and any suggested
mitigation. You should receive an acknowledgement within seven days. There is no
bug bounty or guaranteed remediation timeline.

## Credential boundaries

This project must never:

- request, store, log, or forward a GPG passphrase;
- invoke `pass` through a shell or construct a command from decrypted content;
- write plaintext inside the encrypted password store;
- publish a partial export without explicit user selection;
- upload a password store or export in tests, issues, telemetry, or CI artifacts.

The user's `pass`, GnuPG, `gpg-agent`, operating system, destination filesystem,
and Proton Pass account remain outside the project's trust boundary.

## If plaintext may have escaped

Stop the export, remove unexpected CSV and temporary files, inspect shell and CI
logs, rotate affected account credentials and TOTP seeds, and change the GPG
passphrase if it was exposed. Treat synced folders, backups, and spreadsheet
history as potential copies.

