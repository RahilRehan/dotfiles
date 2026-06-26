# Quality Bar — Senior Engineering Standards

What seniors do that mid-levels often miss.

## A) API & Naming Discipline

- Define a small public API per module
- Hide internals with leading underscores (`_helper`, `_parse_raw`)
- Keep functions small (<20 lines preferred) and names specific
- Avoid generic names: `process`, `handle`, `do_thing`

```python
# Public API
__all__ = ["parse_config", "Config"]

# Internal — not exported
def _resolve_env_vars(raw: dict[str, str]) -> dict[str, str]: ...
```

## B) Types & Contracts

- Use precise types: `Literal["asc", "desc"]`, `NewType("UserId", str)`, `Protocol`
- Validate inputs at boundaries; trust validated values inside
- Avoid `Any` unless interfacing with untyped libraries (document why)

```python
from typing import Literal, NewType

UserId = NewType("UserId", str)
SortOrder = Literal["asc", "desc"]

def list_users(order: SortOrder = "asc") -> Sequence[User]: ...
```

## C) Error Handling & Reliability

- Raise specific exceptions (not bare `Exception` or `ValueError` for everything)
- Make retries/timeouts configurable and only at I/O edges
- Ensure idempotency where operations may repeat

```python
class RetryConfig:
    max_attempts: int = 3
    backoff_seconds: float = 1.0

def fetch_with_retry(url: str, config: RetryConfig = RetryConfig()) -> Response:
    for attempt in range(config.max_attempts):
        try:
            return _do_fetch(url)
        except TransientError:
            if attempt == config.max_attempts - 1:
                raise
            time.sleep(config.backoff_seconds * (2 ** attempt))
```

## D) Observability

- Use `logging` module, never `print` for operational output
- Log important state transitions at INFO, details at DEBUG
- Don't configure logging inside libraries — let the caller configure

```python
import logging

logger = logging.getLogger(__name__)

def process_batch(items: Sequence[Item]) -> BatchResult:
    logger.info("Processing batch of %d items", len(items))
    for item in items:
        logger.debug("Processing item %s", item.id)
        ...
    logger.info("Batch complete: %d succeeded, %d failed", ok, err)
```

## E) Security Hygiene

| Rule | Rationale |
|------|-----------|
| No `eval()` or `exec()` | Arbitrary code execution |
| No `subprocess(..., shell=True)` | Shell injection |
| No secrets in source | Use env vars or secret managers |
| Sanitize file paths | Prevent path traversal |
| Explicit encoding (`utf-8`) | Prevent platform-dependent bugs |
| Safe parsing (json, tomllib) | Avoid unsafe deserialization |

## F) Performance & Complexity

- Prefer simple, readable code first
- Avoid accidental O(n²): use sets for membership, dicts for lookups
- If performance constraints exist, explain the trade-off in a comment or docstring
- Profile before optimizing

```python
# Bad — O(n²) membership check
result = [x for x in items if x.id not in [i.id for i in excluded]]

# Good — O(n) with set lookup
excluded_ids = {i.id for i in excluded}
result = [x for x in items if x.id not in excluded_ids]
```

## G) Documentation & Developer Experience

- Concise docstrings on public functions (what, not how)
- Minimal README: purpose, setup, run, test
- Usage examples in docstrings for non-obvious APIs

```python
def parse_config(path: Path) -> Config:
    """Load and validate application config from a TOML file.

    Raises:
        FileNotFoundError: If path does not exist.
        ValidationError: If required fields are missing.
    """
```

## H) Resource Management

- Always use context managers (`with`) for files, connections, locks, temp resources
- Never leave resources open across function boundaries without explicit ownership
- Use `contextlib.suppress` instead of empty `except` blocks

```python
# Bad: resource may leak on exception
f = open("data.txt")
data = f.read()
f.close()

# Good: guaranteed cleanup
with open("data.txt", encoding="utf-8") as f:
    data = f.read()

# Bad: silent exception swallowing
try:
    os.remove(path)
except FileNotFoundError:
    pass

# Good: explicit and readable
from contextlib import suppress
with suppress(FileNotFoundError):
    os.remove(path)
```

## I) Configuration Management

- Follow 12-factor app: config via environment variables
- Validate config eagerly at startup, not when first used
- Never hardcode secrets, URLs, or environment-specific values
- Use typed config objects, not raw `os.environ` lookups scattered through code

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class AppConfig:
    db_url: str
    api_key: str
    debug: bool = False

    @classmethod
    def from_env(cls) -> "AppConfig":
        db_url = os.environ.get("DB_URL")
        api_key = os.environ.get("API_KEY")
        if not db_url:
            raise ConfigError("DB_URL environment variable is required")
        if not api_key:
            raise ConfigError("API_KEY environment variable is required")
        return cls(
            db_url=db_url,
            api_key=api_key,
            debug=os.environ.get("DEBUG", "").lower() in ("1", "true"),
        )
```

> **Why validate at startup?** Fail fast. A missing config value at 3 AM in a request handler is much harder to diagnose than a clear error at boot time.

## J) Reviewability

- Clean project layout matching the architectural layers
- Each commit/change is minimal and coherent
- Explain trade-offs briefly (2–4 lines max, no essays)
- Use type hints as living documentation
- Keep PRs small and focused — one concern per PR

## Quick Checklist

```
- [ ] All public functions have type hints
- [ ] All public functions have docstrings
- [ ] No `Any` without justification
- [ ] No `print` statements (use logging)
- [ ] No `eval`, `exec`, or `shell=True`
- [ ] Inputs validated at boundaries
- [ ] Errors are specific, not generic
- [ ] Domain logic is pure (no I/O)
- [ ] Immutable domain data (frozen dataclasses)
- [ ] Tests cover happy, edge, and failure paths
- [ ] Resources managed with context managers
- [ ] Config validated at startup, not scattered
- [ ] No hardcoded secrets or environment-specific values
- [ ] Generators used for large data processing
- [ ] @wraps used on all decorators
```
