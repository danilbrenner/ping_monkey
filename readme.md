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
make install   # create .venv and install all dependencies
```

All available targets:

```shell
make           # show help
make init      # create virtual environment at .venv/
make install   # install runtime + dev dependencies
make test      # run pytest
make tc        # run mypy (alias: type-check)
make docker-build  # build Docker image
```

### Docker

Build the image:
```shell
make docker-build
```

Start the local Kafka stack:
```shell
docker compose up -d
```

### Configuration
