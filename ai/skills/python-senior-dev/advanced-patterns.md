# Advanced Patterns — Reference

## Concurrency

### Choosing the Right Model

| Model | Best for | GIL? | Example |
|-------|----------|------|---------|
| `asyncio` | I/O-bound (HTTP, DB, files) | Doesn't matter — single thread | API clients, web scrapers |
| `threading` | I/O-bound, simpler mental model | Yes, but I/O releases it | Background tasks, watchers |
| `multiprocessing` | CPU-bound (math, parsing, image) | Bypassed — separate processes | Data crunching, ML inference |
| `concurrent.futures` | Simple parallelism, either model | Depends on executor | Batch processing |

### asyncio Basics

```python
import asyncio
from typing import Sequence

async def fetch_page(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()

async def fetch_all(urls: Sequence[str]) -> list[str]:
    return await asyncio.gather(*(fetch_page(u) for u in urls))

# Entry point — don't scatter asyncio.run() everywhere
def main() -> None:
    results = asyncio.run(fetch_all(["https://example.com"]))
```

> **Why asyncio over threading for I/O?** No shared mutable state, no locks, no race conditions. The event loop gives you concurrency without parallelism, which is simpler to reason about.

### Common Concurrency Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Blocking call in async | Event loop freezes | Use `asyncio.to_thread()` for blocking I/O |
| Shared mutable state | Intermittent wrong results | Use immutable data or `asyncio.Lock` |
| No timeout on network calls | Hanging forever | Always set `timeout=` on HTTP/DB calls |
| Too many concurrent requests | Remote server throttles you | Use `asyncio.Semaphore` to limit concurrency |
| Fire-and-forget tasks | Silent exceptions, lost work | Always `await` or use `TaskGroup` (3.11+) |

### TaskGroup (Python 3.11+)

```python
async def process_batch(items: Sequence[Item]) -> list[Result]:
    results: list[Result] = []
    async with asyncio.TaskGroup() as tg:
        for item in items:
            tg.create_task(process_one(item, results))
    return results
```

> **Why TaskGroup over gather?** If one task fails, TaskGroup cancels all others and raises an ExceptionGroup. `gather` silently collects exceptions unless you check `return_exceptions=True`.

## Context Managers

Always use context managers for resources that need cleanup.

### Standard Usage

```python
# Files
with open("data.txt", encoding="utf-8") as f:
    content = f.read()

# Database connections
with get_connection() as conn:
    conn.execute(query)

# Locks
with threading.Lock():
    shared_resource.update()
```

### Writing Custom Context Managers

```python
# Class-based (when you need complex state)
class Timer:
    def __enter__(self) -> "Timer":
        self.start = time.monotonic()
        return self

    def __exit__(self, *exc: object) -> None:
        self.elapsed = time.monotonic() - self.start

with Timer() as t:
    do_work()
print(f"Took {t.elapsed:.2f}s")

# Function-based with contextlib (simpler for most cases)
from contextlib import contextmanager

@contextmanager
def temporary_env(key: str, value: str):
    old = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old is None:
            del os.environ[key]
        else:
            os.environ[key] = old
```

> **Why `contextlib.contextmanager` over a class?** Less boilerplate when you just need setup/teardown. Use the class form when you need to store state on the manager itself (like `Timer` above).

### Async Context Managers

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def db_transaction(pool: Pool):
    conn = await pool.acquire()
    try:
        yield conn
        await conn.commit()
    except Exception:
        await conn.rollback()
        raise
    finally:
        await pool.release(conn)
```

## Generators & Lazy Evaluation

### When to Use Generators

Use generators when processing large datasets that don't fit in memory, or when you want lazy pipelines.

```python
# Bad: loads all lines into memory
def get_errors(path: Path) -> list[str]:
    return [line for line in path.read_text().splitlines() if "ERROR" in line]

# Good: yields one line at a time
def get_errors(path: Path) -> Iterator[str]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            if "ERROR" in line:
                yield line.rstrip()

# Composable pipelines
def parse_logs(lines: Iterable[str]) -> Iterator[LogEntry]:
    for line in lines:
        yield LogEntry.from_line(line)

def recent_errors(entries: Iterable[LogEntry], since: datetime) -> Iterator[LogEntry]:
    for entry in entries:
        if entry.level == "ERROR" and entry.timestamp >= since:
            yield entry

# Usage: nothing executes until iteration
errors = recent_errors(parse_logs(get_errors(log_path)), cutoff)
for error in errors:
    print(error)
```

> **Why generators?** Memory is O(1) instead of O(n). You can process a 10GB log file on a machine with 256MB of RAM. They also compose cleanly into pipelines.

### `yield from` for Delegation

```python
def flatten(nested: Iterable[Iterable[T]]) -> Iterator[T]:
    for inner in nested:
        yield from inner
```

## Decorators

### When to Use Decorators

Use decorators for cross-cutting concerns that wrap many functions the same way: logging, timing, retry, auth checks.

**Don't** use decorators when a simple function call would be clearer.

### Writing Decorators Correctly

```python
from functools import wraps
from typing import TypeVar, Callable, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")

def log_calls(func: Callable[P, R]) -> Callable[P, R]:
    @wraps(func)  # preserves __name__, __doc__, type hints
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        logger.info("Calling %s", func.__name__)
        result = func(*args, **kwargs)
        logger.info("%s returned", func.__name__)
        return result
    return wrapper

@log_calls
def process(data: str) -> int:
    """Process data and return count."""
    return len(data.split())
```

> **Why `@wraps`?** Without it, `process.__name__` becomes `"wrapper"`, `help(process)` shows the wrapper's docstring, and debuggers show the wrong function name. Always use `@wraps`.

> **Why `ParamSpec`?** It preserves the original function's parameter types through the decorator, so type checkers still work correctly on the decorated function.

### Decorator with Arguments

```python
def retry(max_attempts: int = 3, delay: float = 1.0):
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_err: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    time.sleep(delay * (2 ** attempt))
            raise last_err  # type: ignore[misc]
        return wrapper
    return decorator

@retry(max_attempts=5, delay=0.5)
def call_api(url: str) -> Response: ...
```

## Project Setup & Packaging

### Modern pyproject.toml

```toml
[project]
name = "mypackage"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8.0", "mypy>=1.8", "ruff>=0.3"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q"

[tool.mypy]
strict = true

[tool.ruff]
target-version = "py311"
select = ["E", "F", "I", "N", "UP", "B", "SIM"]
```

### Project Layout

```
mypackage/
├── pyproject.toml
├── README.md
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   └── models.py
│       ├── app/
│       │   ├── __init__.py
│       │   └── service.py
│       └── infra/
│           ├── __init__.py
│           └── db.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_models.py
    └── test_service.py
```

> **Why `src/` layout?** It prevents accidentally importing from the working directory instead of the installed package. This catches missing files in your package before deployment.

### Development Workflow

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Type checking
mypy src/

# Linting
ruff check src/ tests/
```
