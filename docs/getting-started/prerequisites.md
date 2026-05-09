# Prerequisites

## Required Tools

| Tool | Version | Install |
|------|---------|---------|
| Docker Desktop | Latest | https://www.docker.com/products/docker-desktop |
| Git | 2.x+ | https://git-scm.com |
| Make | Any | Pre-installed on macOS/Linux |
| Node.js | 20+ | https://nodejs.org (for local frontend work) |
| Python | 3.11+ | https://python.org (for pre-commit hooks) |
| Poetry | 1.7+ | `pip install poetry` |

## macOS Setup

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install tools
brew install git make node@20 pyenv
pyenv install 3.11.13
pip install poetry
```

## Windows Setup

Use WSL2 (Windows Subsystem for Linux 2) with Ubuntu. Docker Desktop integrates with WSL2 automatically.

```powershell
# Install WSL2
wsl --install -d Ubuntu

# Then follow Linux/macOS instructions inside WSL2
```

## Verify Installation

```bash
docker --version        # Docker version 26+
docker compose version  # Docker Compose version 2+
node --version          # v20+
python --version        # Python 3.11+
poetry --version        # Poetry 1.7+
make --version          # GNU Make 4+
```
