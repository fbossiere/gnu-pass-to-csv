# Releasing

Releases are immutable states shared by the source tree, package metadata, tag,
GitHub Release, and PyPI artifacts.

## One-time owner setup

1. Create a PyPI trusted publisher for project `gnu-pass-to-csv` with owner
   `fbossiere`, repository `gnu-pass-to-csv`, workflow `release.yml`, and
   environment `pypi`.
2. Create the protected GitHub `pypi` environment. No API token is required.
3. Apply the branch, tag, Actions, and security settings in
   [repository-settings.md](repository-settings.md).

## Release checklist

1. Create `release/vX.Y.Z` from current `main`.
2. Update the single version in `pyproject.toml`, the dated changelog heading,
   supported-version table if needed, and examples.
3. Run the exact gate from `CONTRIBUTING.md` in a clean checkout.
4. Inspect the wheel and sdist, install the wheel in a clean environment, and
   smoke-test `gnu-pass-to-csv --version` and `--help`.
5. Open a release pull request describing user-visible changes, non-goals,
   security-boundary impact, commands run, and observed results.
6. After required CI passes and the pull request is squash-merged, create tag
   `vX.Y.Z` from that exact `main` commit and push it.
7. The release workflow verifies the tag/version match, rebuilds and checks the
   artifacts, publishes them to PyPI with OIDC, and creates the GitHub Release.
8. Verify the PyPI metadata, provenance, hashes, GitHub assets, and installation
   from a clean environment.

Never reuse or move a published version tag. Correct a release with a new patch
version.

