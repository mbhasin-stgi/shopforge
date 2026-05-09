# CI/CD Pipeline

GitHub Actions workflows run automatically on pull requests and pushes to `main`.

## Workflows

| Workflow | File | Trigger |
|----------|------|---------|
| Lint & Format | `.github/workflows/lint.yml` | PR (Python files) |
| Tests | `.github/workflows/test.yml` | PR + push to main |
| Security Scanning | `.github/workflows/security.yml` | PR + weekly |
| Frontend Checks | `.github/workflows/frontend.yml` | PR (frontend files) |
| Migration Check | `.github/workflows/migrations.yml` | PR (model files) |
| Build & Push | `.github/workflows/build.yml` | Push to main / version tags |

## Branch Protection

Configure in GitHub Settings → Branches → Protection rules for `main`:

- Require PR before merging (1 approval)
- Required status checks: Pre-commit Hooks, Python Tests, ESLint & TypeScript
- Require conversation resolution
- No force pushes

## Required Secrets

Set in GitHub Settings → Secrets → Actions:

| Secret | Used by |
|--------|---------|
| `CODECOV_TOKEN` | `test.yml` — coverage upload |
| `SEMGREP_APP_TOKEN` | `security.yml` — Semgrep SAST |
| `GITHUB_TOKEN` | `build.yml` — ghcr.io push (auto-provided) |

## Docker Image Tags

Images are pushed to `ghcr.io/yourorg/shopforge` with these tags:

- `main` — latest commit on main branch
- `v1.2.3` — semantic version tags
- `abc1234` — git SHA (every push)
