# Command reference

GNU pass to CSV exposes one explicit export command:

```bash
gnu-pass-to-csv --output PATH [OPTIONS]
```

## Options

| Option | Default | Purpose |
| --- | --- | --- |
| `-o`, `--output`, `--output-csv PATH` | Required | Destination CSV; must be outside the password store. |
| `-s`, `--password-store-dir PATH` | `PASSWORD_STORE_DIR` or `~/.password-store` | Source password-store directory. |
| `--vault NAME` | `Personal` | Value written to the `vault` column of every row. |
| `--max-workers N` | `1` | Number of concurrent `pass` processes. |
| `--pass-executable PATH` | `pass` | Compatible `pass` executable to invoke. |
| `--timeout SECONDS` | `60` | Positive per-entry decryption timeout. |
| `--force` | Off | Replace an existing output file. |
| `--skip-errors` | Off | Write an explicitly partial export when entries fail. |
| `--version` | — | Print the installed version and exit. |

Run `gnu-pass-to-csv --help` for the help text from the installed version.

## Store selection

Choose the store with an environment variable:

```bash
PASSWORD_STORE_DIR=~/.password-store-work \
  gnu-pass-to-csv --output ~/Downloads/work-import.csv
```

Or use the command-line option, which takes precedence:

```bash
gnu-pass-to-csv \
  --password-store-dir ~/.password-store-work \
  --output ~/Downloads/work-import.csv
```

## Complete versus partial exports

The default is atomic and complete: if any entry is empty, cannot be decrypted,
times out, or is not valid UTF-8, the exporter aborts before installing the
destination file.

`--skip-errors` changes that guarantee. It writes the entries that succeeded,
lists skipped entry names on standard error, and should be used only when an
explicitly incomplete migration is acceptable.

!!! warning "Review skipped entry names"

    Entry names can reveal services or accounts. Redact them before sharing logs
    or bug reports, and never share decrypted content or the generated CSV.

## Parallel decryption

The default `--max-workers 1` avoids competing pinentry prompts. If `gpg-agent`
is already unlocked, a larger value can run several `pass` processes at once:

```bash
gnu-pass-to-csv \
  --output ~/Downloads/proton-pass-import.csv \
  --max-workers 4
```

Different keys can still produce multiple prompts. Output rows remain sorted by
entry name regardless of worker count.

## Existing destinations

Existing files are never overwritten by default. Use `--force` only after
confirming that the exact destination may be replaced:

```bash
gnu-pass-to-csv \
  --output ~/Downloads/proton-pass-import.csv \
  --force
```

The writer creates a private temporary file in the destination directory,
flushes it, and installs it atomically. On POSIX systems the final mode is
`0600`.
