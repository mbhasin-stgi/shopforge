# Code Style

## Python

- **Formatter**: Black (line length 120)
- **Import sorter**: isort (black profile)
- **Linter**: flake8 + flake8-bugbear + flake8-comprehensions
- **Security**: bandit
- **Docstrings**: interrogate (80% coverage minimum)

Auto-format with:
```bash
make format
# or individually:
poetry run black .
poetry run isort .
```

## TypeScript / Vue

- **Formatter**: Prettier
- **Linter**: ESLint with TypeScript + Vue plugins
- **Style**: Composition API (`<script setup lang="ts">`), no Options API

Auto-format with:
```bash
npm run lint-fix
npx prettier --write "shopforge/webapp/src/**"
```

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(products): add product search endpoint
fix(orders): prevent negative quantities
docs(readme): update quick start guide
test(inventory): add low-stock alert coverage
refactor(users): extract auth logic to service
ci(github): add CodeQL security scanning
chore(deps): update Django to 4.2.16
```

Enforced by `conventional-pre-commit` hook on every commit.
