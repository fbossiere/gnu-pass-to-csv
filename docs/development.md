# Development

The unit test suite uses synthetic data and fake readers. A separate integration
test creates a temporary GPG key and password store when `pass`, `gpg`, and
`gpgconf` are available.

## Setup

```bash
git clone https://github.com/fbossiere/gnu-pass-to-csv.git
cd gnu-pass-to-csv
uv sync --locked --extra dev --extra docs
uv run pre-commit install
```

## Quality gate

Run the same checks used for review and release:

```bash
uv lock --check
uv run ruff format --check .
uv run ruff check .
uv run mypy
uv run pytest
uv run mkdocs build --strict
uv build
uv run twine check dist/*
```

Run the real `pass` and GPG test explicitly with:

```bash
uv run pytest --no-cov -m integration tests/test_integration_pass.py
```

## Documentation workflow

Documentation sources live in `docs/`, with navigation and theme configuration
in `mkdocs.yml`.

```bash
uv run mkdocs serve
```

Open the local URL printed by MkDocs. Before committing, run the strict build so
broken navigation, links, and configuration warnings fail locally.

Pull requests build the documentation but never deploy it. A push to `main`
builds the same sources and deploys the generated static site to GitHub Pages.

## Design invariants

1. Never accept or forward a GPG passphrase.
2. Invoke `pass` without a shell and keep arguments independent of decrypted content.
3. Never log decrypted content or include it in exceptions.
4. Make complete exports the default; partial output must be explicit.
5. Write plaintext with restrictive permissions outside the encrypted store.
6. Preserve deterministic row ordering and the documented CSV field order.

Read the canonical
[`CONTRIBUTING.md`](https://github.com/fbossiere/gnu-pass-to-csv/blob/main/CONTRIBUTING.md)
before opening a pull request.
