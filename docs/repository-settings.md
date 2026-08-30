# GitHub repository settings

Apply these after the first successful CI run so exact check names exist.

| Area | Desired state | Why / dependency |
| --- | --- | --- |
| Visibility | Public | Requested distribution model |
| Default branch | `main` | Consistent links and release flow |
| Merge methods | Squash only; delete merged branches | Linear, reviewable history |
| `main` ruleset | Pull request required, 0 approvals for solo maintenance, conversation resolution, linear history, no force push or deletion | CI provides the independent gate without blocking the solo author |
| Required checks | `quality`, `tests (3.11)`, `tests (3.12)`, `tests (3.13)`, `tests (3.14)`, `integration (pass + GPG)`, `macos smoke`, `package`, `analyze (python)` | Enable only after these checks have completed successfully |
| Tag ruleset | Target `v*`; block update, deletion, and force push; empty bypass list | Immutable releases |
| Actions permissions | Read-only `GITHUB_TOKEN` by default; no Actions-created approvals; allow only pinned actions used here | Workflows grant narrower job-level write access |
| Fork workflows | Require approval for all external contributors | Prevent secret or write-token exposure |
| Security | Dependency graph, Dependabot alerts and security updates, secret scanning, push protection, private vulnerability reporting, CodeQL default setup or the checked-in workflow | Enable CodeQL gating only after a clean baseline |
| Other features | Disable unused Wiki and Projects; leave Discussions and Pages off until maintained | Reduce unattended surfaces |
| Metadata | Description and focused topics from README; upload `docs/assets/github-social-preview.png`; no homepage until one is maintained | Keep claims aligned |

The owner account should use a passkey or strong MFA and receive repository
security alerts. Review collaborators, deploy keys, webhooks, environments,
secrets, and installed apps for least privilege at each release.
