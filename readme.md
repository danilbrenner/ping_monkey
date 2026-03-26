# Ping Monkey

A Python application for monitoring web endpoints and publishing probe results to Kafka.

## Branching Convention

| Prefix | Purpose |
|--------|---------|
| `feat/` | New feature |
| `fix/` | Bug fix |
| `refactor/` | Code refactoring without behaviour change |
| `chore/` | Non-code changes (deps, config, tooling, CI) |
| `docs/` | Documentation-only changes |
| `test/` | Adding or updating tests |

Examples: `feat/ssl-retry`, `fix/kafka-timeout`, `chore/update-deps`

## Development Setup

```shell
# Create a fresh virtual environment
python -m venv venv
source venv/bin/activate

# Install only what you need
pip install -r requirements-dev.txt

# This will install the 4 core packages + their transitive deps + dev tools
```

### Manual Docker Commands

Build: 
```shell
docker build -t ping_monkey:latest .
```

Dev:
```shell
docker compose up -d
```

### Configuration
