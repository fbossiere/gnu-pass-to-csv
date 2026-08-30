# Changelog

All notable changes are documented here. The project follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Version-controlled GitHub Pages documentation with getting-started, command,
  entry-mapping, security, troubleshooting, architecture, development, and
  release guides.
- Strict documentation builds on pull requests and deployment from `main` with
  GitHub Actions.

## [2.0.0] - 2026-08-30

### Added

- Automated dependency updates, CI, CodeQL analysis, artifact validation,
  GitHub Releases, and PyPI trusted publishing.
- Real `pass`/GPG integration coverage and macOS package smoke testing.
- Proton Pass generic CSV field parsing for labeled URLs, email addresses,
  usernames, TOTP secrets, and notes.
- Atomic, deterministic CSV output with `0600` permissions and overwrite
  protection.
- Typed, dependency-free Python implementation tested on Python 3.11-3.14.

### Changed

- Decryption now runs through `pass show` and the user's configured `gpg-agent`.
- Output is required and must be outside the encrypted password store.
- A failed entry aborts the export unless `--skip-errors` is selected.
- Full password-store paths are preserved as entry names to avoid collisions.

### Removed

- Insecure `--passphrase` and `GPG_PASSPHRASE` handling.
- Pandas, Typer, Loguru, python-dotenv, Poetry, and the prototype notebook.

### Security

- GPG passphrases are no longer placed in process arguments.
- Decrypted data is no longer sent to process workers or logged on failures.

## [1.0.8] - 2024-08-24

- Last release from the original GitLab implementation.

[Unreleased]: https://github.com/fbossiere/gnu-pass-to-csv/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/fbossiere/gnu-pass-to-csv/compare/1.0.8...v2.0.0
[1.0.8]: https://gitlab.com/fbossiere/gnu-pass-to-csv/-/tags/1.0.8
