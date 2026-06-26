# TDD Workflow — Detailed Reference

## The Cycle

```
RED ──→ GREEN ──→ REFACTOR ──→ (repeat)
 │         │          │
 │         │          └─ improve names, split modules,
 │         │             remove duplication
 │         └─ minimal code to pass
 └─ smallest failing test
```

## Rules

1. Always write tests first and show them first
2. Start with the smallest possible failing test
3. Implement only enough code to make the test pass
4. Refactor only after green
5. Never skip failure-path tests

## Test Naming Convention

```python
def test_<function>_<scenario>_<expected>():
    ...

# Examples:
def test_normalize_whitespace_collapses_spaces():
    assert normalize(" a  b ") == "a b"

def test_normalize_whitespace_handles_empty_string():
    assert normalize("") == ""

def test_normalize_whitespace_raises_on_none():
    with pytest.raises(TypeError):
        normalize(None)
```

## Mini Example: Full TDD Cycle

### RED — Write failing test

```python
# tests/test_normalize.py
from mylib.text import normalize

def test_normalizes_whitespace():
    assert normalize(" a  b ") == "a b"
```

### GREEN — Minimal implementation

```python
# src/mylib/text.py
def normalize(s: str) -> str:
    return " ".join(s.split())
```

### REFACTOR — Improve

```python
# src/mylib/text.py
def normalize(text: str) -> str:
    """Collapse all whitespace runs into single spaces, strip edges."""
    return " ".join(text.split())
```

### EXPAND — Edge and failure cases

```python
def test_normalize_empty_string():
    assert normalize("") == ""

def test_normalize_already_clean():
    assert normalize("hello world") == "hello world"

def test_normalize_raises_on_non_string():
    with pytest.raises(AttributeError):
        normalize(42)  # type: ignore
```

## Test Doubles for Effects

Use test doubles to isolate effects. Prefer simple callables over heavy mocks.

```python
# Production: reads from filesystem
def load_config(read_file: Callable[[Path], str], path: Path) -> Config:
    raw = read_file(path)
    return parse_config(raw)

# Test: inject a fake
def test_load_config_parses_toml():
    fake_read = lambda _: '[db]\nhost = "localhost"'
    config = load_config(fake_read, Path("unused"))
    assert config.db.host == "localhost"
```

### When to use which double

| Double | Use when |
|--------|----------|
| Lambda/function | Simple return value or side effect |
| `unittest.mock.Mock` | Need to assert call count/args |
| Fake class | Complex behavior needed in multiple tests |
| `pytest.fixture` | Shared setup across test module |

## Fixture Patterns

```python
@pytest.fixture
def sample_items() -> tuple[Item, ...]:
    return (
        Item(name="widget", price=Money(1099)),
        Item(name="gadget", price=Money(2499)),
    )

def test_compute_totals(sample_items: tuple[Item, ...]):
    assert compute_totals(sample_items) == Money(3598)
```

## Parametrized Tests

Use when testing the same logic with multiple inputs:

```python
@pytest.mark.parametrize("input_text,expected", [
    ("  a  b  ", "a b"),
    ("", ""),
    ("no change", "no change"),
    ("\t\nnewlines\t\n", "newlines"),
])
def test_normalize_parametrized(input_text: str, expected: str):
    assert normalize(input_text) == expected
```

## Property-Based Testing (Hypothesis)

When unit tests check specific examples, property-based tests check *invariants* across random inputs. Use for parsers, serializers, data transformations, and anything with a clear "for all X, Y must hold" property.

```python
from hypothesis import given, strategies as st

@given(st.text())
def test_normalize_roundtrip_is_idempotent(s: str):
    """Normalizing twice should give the same result as normalizing once."""
    once = normalize(s)
    twice = normalize(once)
    assert once == twice

@given(st.lists(st.integers()))
def test_sort_preserves_length(xs: list[int]):
    assert len(sorted(xs)) == len(xs)

@given(st.dictionaries(st.text(), st.integers()))
def test_serialize_deserialize_roundtrip(data: dict[str, int]):
    assert deserialize(serialize(data)) == data
```

> **When to use property-based tests:** When you can express a *property* (idempotency, roundtrip, ordering, length preservation) rather than specific input/output pairs. They find edge cases you'd never think of.

### Common Properties to Test

| Property | Example |
|----------|---------|
| Roundtrip / inverse | `decode(encode(x)) == x` |
| Idempotency | `f(f(x)) == f(x)` |
| Invariant preservation | `len(sort(xs)) == len(xs)` |
| Commutativity | `merge(a, b) == merge(b, a)` |
| No crash | Function doesn't raise on any valid input |

## Integration Test Strategy

### The Test Pyramid

```
        /  E2E  \          Few, slow, expensive
       /─────────\
      / Integration\       Some, moderate speed
     /──────────────\
    /   Unit Tests   \     Many, fast, cheap
   /──────────────────\
```

- **Unit tests** (80%): Pure functions, domain logic. Fast, isolated, no I/O.
- **Integration tests** (15%): Test boundaries — database queries, API calls, file I/O. Use real (or containerized) dependencies.
- **E2E tests** (5%): Full system tests. Slow, brittle, but catch wiring bugs.

### Integration Test Patterns

```python
# Mark integration tests so they can be skipped in fast CI
import pytest

@pytest.mark.integration
def test_user_repository_saves_and_loads(db_connection):
    repo = UserRepository(db_connection)
    user = User(name="alice", email="alice@example.com")
    repo.save(user)
    loaded = repo.find_by_email("alice@example.com")
    assert loaded == user

# conftest.py — shared fixtures for integration tests
@pytest.fixture(scope="session")
def db_connection():
    conn = create_test_database()
    yield conn
    conn.close()
    drop_test_database()
```

```ini
# pyproject.toml — register custom markers
[tool.pytest.ini_options]
markers = ["integration: tests that require external dependencies"]
```

Run fast vs full:
```bash
pytest -m "not integration"   # fast: unit only
pytest                         # full: unit + integration
```

## Testing Async Code

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_user_returns_data():
    fake_client = FakeHttpClient(responses={"/user/1": '{"name": "alice"}'})
    user = await fetch_user(fake_client, user_id="1")
    assert user.name == "alice"

@pytest.mark.asyncio
async def test_fetch_user_raises_on_404():
    fake_client = FakeHttpClient(responses={}, default_status=404)
    with pytest.raises(NotFoundError):
        await fetch_user(fake_client, user_id="999")
```

> **Why fake clients over `unittest.mock.AsyncMock`?** Fakes let you test real behavior (routing, status codes), not just that a method was called. They're more resilient to refactoring.

## Coverage Targets

- Aim for high coverage on domain/pure logic (>90%)
- Lower coverage acceptable for thin I/O wrappers
- Never chase 100% as a goal — cover meaningful behavior
- Use property-based tests to find edge cases you wouldn't think of
