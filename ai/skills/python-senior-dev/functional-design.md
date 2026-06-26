# Functional-First Design — Detailed Reference

## Core Principles

### FP-1: Pure Functions by Default

Core logic must be deterministic and side-effect free.

```python
# Pure — no I/O, no mutation, deterministic
def compute_totals(items: tuple[Item, ...]) -> Money:
    return Money(sum(item.price.cents for item in items))

# Pure — transforms data, doesn't fetch it
def filter_active(users: Sequence[User]) -> tuple[User, ...]:
    return tuple(u for u in users if u.is_active)
```

### FP-2: Immutability

No in-place mutation in domain logic.

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Cart:
    items: tuple[Item, ...]

    def add(self, item: Item) -> "Cart":
        return Cart(items=(*self.items, item))

    def remove(self, item_id: str) -> "Cart":
        return Cart(items=tuple(i for i in self.items if i.id != item_id))
```

Use `tuple` over `list`, `frozenset` over `set` for domain data.

### FP-3: Explicit Effects at the Boundary

Isolate I/O into thin functions/modules.

```python
# infra/file_io.py — thin effectful boundary
def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")

# app/main.py — imperative shell wires effects to pure core
def main(argv: list[str]) -> int:
    text = read_text(Path(argv[1]))
    result = process(text)          # pure
    write_text(Path(argv[2]), result)
    return 0
```

### FP-4: Dependency Injection for Effects

Pass collaborators as parameters — functions or small `Protocol` interfaces.

```python
from typing import Protocol

# Function-style DI (preferred for simple cases)
def make_id(rng: Callable[[], int]) -> str:
    return f"id-{rng():08x}"

# Protocol-style DI (for richer interfaces)
class Clock(Protocol):
    def now(self) -> datetime: ...

def create_event(clock: Clock, name: str) -> Event:
    return Event(name=name, created_at=clock.now())

# Test with fake
class FakeClock:
    def now(self) -> datetime:
        return datetime(2025, 1, 1, tzinfo=UTC)

def test_create_event_uses_clock():
    event = create_event(FakeClock(), "launch")
    assert event.created_at.year == 2025
```

### FP-5: Consistent Error Model

Choose ONE per module and stick to it.

**Option A: Exception hierarchy** (preferred for most Python apps)

```python
class AppError(Exception): ...
class ValidationError(AppError): ...
class NotFoundError(AppError): ...

def get_user(user_id: str) -> User:
    if not user_id:
        raise ValidationError("user_id must be non-empty")
    user = repo.find(user_id)
    if user is None:
        raise NotFoundError(f"User {user_id} not found")
    return user
```

**Option B: Result type** (useful for pipelines)

```python
@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err(Generic[E]):
    error: E

Result = Ok[T] | Err[E]

def parse_age(raw: str) -> Result[int, str]:
    try:
        age = int(raw)
    except ValueError:
        return Err(f"Invalid integer: {raw!r}")
    if age < 0:
        return Err(f"Age cannot be negative: {age}")
    return Ok(age)
```

## Architecture: Functional Core, Imperative Shell

```
┌─────────────────────────────────┐
│         Imperative Shell        │  ← wiring, I/O, orchestration
│  app/main.py                    │
│  ┌───────────────────────────┐  │
│  │     Functional Core       │  │  ← pure logic, tested in isolation
│  │  domain/models.py         │  │
│  │  domain/rules.py          │  │
│  └───────────────────────────┘  │
│  infra/db.py  infra/api.py      │  ← thin adapters
└─────────────────────────────────┘
```

## FP-Friendly Patterns

| Pattern | FP Translation | When |
|---------|---------------|------|
| Strategy | Pass a function | Varying behavior at runtime |
| Adapter | Translate external types to internal | Wrapping 3rd-party APIs |
| Repository | Interface + implementation | Persistence boundary |
| Pipeline | Function composition | Sequential transformations |

### Pipeline Example

```python
from functools import reduce

def pipeline(*fns: Callable[[str], str]) -> Callable[[str], str]:
    def apply(data: str) -> str:
        return reduce(lambda d, f: f(d), fns, data)
    return apply

process = pipeline(strip_html, normalize_whitespace, truncate_to(500))
result = process(raw_text)
```
