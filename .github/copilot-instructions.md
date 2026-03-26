# Copilot Instructions

## Project Overview
Ping Monkey monitors web endpoints on cron schedules and publishes probe results to Apache Kafka. It is a Python 3.12 async application with a layered architecture: `domain` → `infra` → `common`.

## Code Style & Conventions

### Python Version & Features
- Target **Python 3.12**. Use modern syntax: `str | None` unions, PEP 695 type aliases (`type Result[T, E] = ...`), pattern matching (`match/case`), and `from __future__ import annotations`.
- All I/O must be **async/await**.

### Type Hints
- Add full type annotations to every function and method.
- Use `Protocol` for dependency interfaces (`Publisher`, `Requestor`, `Logger`) to keep coupling loose.

### Error Handling
- Use the `Result[T, E]` monadic pattern (`Ok` / `Err`) from `src/common/result.py` instead of raising exceptions for expected failures.
- Compose results with `map_result()` and `bind_result()` combinators.

### Data Classes
- Model domain objects as `@dataclass(frozen=True, slots=True)`.

### Naming
- `snake_case` for functions, variables, and modules.
- `PascalCase` for classes.
- `_leading_underscore` for private methods.
- `SCREAMING_SNAKE_CASE` for module-level constants.

### Logging
- Use `structlog` via the wrapper in `src/common/logging.py`. Never use `print` or the stdlib `logging` module directly.

## Project Structure
```
src/
  main.py                     # Entry point, async scheduler & signal handling
  domain.py                   # Domain models (Probe, HttpResult, CertInfo, Setup)
  probe_execution_service.py  # Core orchestration service
  common/                     # Shared utilities (logging, Result type)
  infra/                      # External integrations (Kafka, HTTP, config loader)
tests/
  conftest.py
  test_config_loader.py
  test_probe_execution_service.py
```

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

## Testing
- Use **pytest**. Place tests under `tests/`.
- Mock external dependencies (`Publisher`, `Requestor`) with `unittest.mock.AsyncMock` / `Mock`.
- Verify `Result` values with `match/case` pattern matching, not bare attribute access.
- Run tests: `pytest`
- Run type checker: `mypy src`
