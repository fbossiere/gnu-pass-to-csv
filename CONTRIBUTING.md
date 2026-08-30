# Contributing

Thank you for helping improve gnu-pass-to-csv. Bug reports, focused fixes, tests,
documentation, and format-compatibility evidence are welcome.

## Before opening an issue

Use only synthetic password stores and redact usernames, home paths, key IDs,
emails, URLs, passwords, and TOTP seeds. Never attach a real `.gpg` file or CSV
export. Use GitHub private vulnerability reporting for security defects.

## Development setup

Install [uv](https://docs.astral.sh/uv/), clone the repository, then run:

```console
uv sync --locked --extra dev
uv run pre-commit install
```

For documentation work, also install the documentation extra:

```console
uv sync --locked --extra dev --extra docs
```

The exact local quality gate is:

```console
uv lock --check
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv run mkdocs build --strict
uv build
uv run twine check dist/*
```

CI must pass on every supported Python version before merge.

The regular suite skips the real integration test when `pass`, `gpg`, or
`gpgconf` is unavailable. CI installs those tools and requires an export from a
temporary GPG key and password store to pass. Run that test locally with:

```console
uv run pytest --no-cov -m integration tests/test_integration_pass.py
```

CI also runs the full test suite, builds the wheel, installs it, and smoke-tests
the command on macOS.

## Design invariants

- Never accept or forward a GPG passphrase.
- Use `pass` without a shell and keep command arguments independent of decrypted
  content.
- Never log decrypted content or include it in an exception.
- Make complete exports the default; partial output must be an explicit choice.
- Write plaintext with restrictive permissions, outside the encrypted store, and
  do not silently overwrite an existing file.
- Keep the runtime dependency-free unless a demonstrated requirement outweighs
  the added supply-chain and installation cost.
- Preserve deterministic row ordering and the documented CSV field order.

Add tests for every behavior change. Compatibility claims must reference a
reproducible synthetic example or upstream format documentation.

## Pull requests

Keep changes focused and explain user-visible behavior, security-boundary impact,
tests run, and explicit non-goals. Maintainers normally squash-merge after CI and
all review conversations are resolved.
