## Summary

Describe the user-visible change and why it is needed.

## Security boundary

- [ ] No passphrase, decrypted content, private path, key ID, or real export is in this pull request.
- [ ] The change preserves the invariants in `CONTRIBUTING.md`, or the exception is explicitly justified.

## Validation

List exact commands run and observed results. Do not check work that was not run.

- [ ] `uv lock --check`
- [ ] `uv run ruff format --check .`
- [ ] `uv run ruff check .`
- [ ] `uv run mypy`
- [ ] `uv run pytest`
- [ ] `uv build && uv run twine check dist/*`

## Non-goals

State what this pull request intentionally does not change.

