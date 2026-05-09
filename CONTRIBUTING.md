# Contributing to ShopForge

Thank you for contributing! Please read this guide before opening a PR.

## Development Setup

```bash
# 1. Clone and enter
git clone https://github.com/mbhasin-stgi/shopforge.git
cd shopforge

# 2. Start the dev stack
make quick-start

# 3. Install pre-commit hooks
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
```

## Branch Naming

| Pattern | Use for |
|---------|---------|
| `feature/short-description` | New features |
| `bugfix/short-description` | Bug fixes |
| `hotfix/short-description` | Urgent production fixes |
| `refactor/short-description` | Code improvements (no behavior change) |
| `docs/short-description` | Documentation only |

## Commit Messages

We enforce [Conventional Commits](https://www.conventionalcommits.org/) via the `conventional-pre-commit` hook.

**Format:** `<type>(<scope>): <description>`

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `ci`, `chore`, `revert`

```
feat(products): add product search endpoint
fix(orders): prevent negative quantities in cart
docs(readme): update quick start guide
test(inventory): add low-stock alert coverage
chore(deps): update Django to 4.2.16
```

## Pull Request Checklist

Before opening a PR, verify:

- [ ] All tests pass: `make t`
- [ ] Coverage maintained: `make coverage` (must stay ≥ 85%)
- [ ] Linting passes: `make lint`
- [ ] Migrations created if models changed: `make mm APP_LABEL=<app>`
- [ ] No debug `print()` statements left in code
- [ ] PR description explains **what** changed and **why**

## Code Review Guidelines

- Be constructive and specific — suggest solutions, not just problems
- Use "Nit:" prefix for non-blocking style suggestions
- Use "Request Changes" only for correctness or security issues
- Approve once all concerns are addressed

## Questions?

Open an issue or start a GitHub Discussion.
