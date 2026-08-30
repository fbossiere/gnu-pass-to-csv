# Architecture

The package follows a one-way, local-only pipeline:

```text
password-store paths → pass show → field parser → atomic CSV writer
       encrypted       gpg-agent       process memory       mode 0600
```

`exporter.discover_entries` turns sorted `.gpg` paths into the entry names
understood by `pass`. `backend.PassClient` sets `PASSWORD_STORE_DIR` and invokes
the fixed argument vector `pass show -- <entry>` without a shell. `models` maps
the decrypted first line and recognized metadata to the eight-column Proton Pass
generic CSV schema. `exporter.write_csv` creates a private temporary file next to
the destination, flushes it, and installs it atomically.

The default path is single-threaded so one pinentry prompt can unlock `gpg-agent`.
Users with an already-unlocked agent can opt into threads; each thread owns a
separate `pass` subprocess, while result rows are sorted before writing.

The package has no network code, telemetry, configuration file loader, plugin
system, or runtime Python dependency. Decrypted content is scoped to the current
process and subprocess pipes. See [security.md](security.md) for residual risks.

