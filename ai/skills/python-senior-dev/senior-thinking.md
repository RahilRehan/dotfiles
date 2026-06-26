# Senior Thinking — What Separates Senior from Mid-Level

## Decision Heuristics

### YAGNI — You Aren't Gonna Need It

Don't build abstractions for hypothetical future requirements.

```python
# Mid-level instinct: "We might need other exporters later"
class ExporterFactory:
    def create(self, format: str) -> Exporter: ...

# Senior approach: just write the function you need NOW
def export_csv(data: Sequence[Row], out: Path) -> None: ...
# When you actually need JSON export, THEN refactor
```

**Rule of thumb:** Wait until you have 3 concrete cases before abstracting. Two cases might be coincidence.

### When to Abstract vs Keep It Concrete

| Signal | Action |
|--------|--------|
| Same logic copy-pasted 3+ times | Extract a function |
| Two modules share the same data shape | Extract a dataclass |
| You're passing 5+ related args together | Group into a dataclass |
| You need to swap implementations at runtime | Extract a Protocol |
| You're writing "just in case" code | Stop — YAGNI |
| You're naming something `BaseAbstractManager` | Rethink — you're over-engineering |

### Simple vs Easy

"Simple" means fewer concepts interleaved. "Easy" means familiar.

```python
# Easy (familiar) but not simple — hidden coupling to global state
import settings
def get_db():
    return connect(settings.DB_URL)

# Simple (decoupled) but requires learning DI
def get_db(db_url: str) -> Connection:
    return connect(db_url)
```

Prefer simple. Easy code creates hidden dependencies that bite you later.

### Trade-off Thinking

Seniors don't look for "best" — they look for trade-offs:

- "This is simpler but less flexible"
- "This is faster but harder to test"
- "This is more correct but adds a dependency"

Always state the trade-off, even if briefly. Future-you will thank present-you.

## Python Gotchas

Things that trip up even experienced developers.

### Mutable Default Arguments

```python
# BUG: all callers share the same list!
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items

# FIX: use None sentinel
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    items.append(item)
    return items
```

### Late Binding Closures

```python
# BUG: all functions return 4 (last value of i)
fns = [lambda: i for i in range(5)]
[f() for f in fns]  # [4, 4, 4, 4, 4]

# FIX: bind with default argument
fns = [lambda i=i: i for i in range(5)]
[f() for f in fns]  # [0, 1, 2, 3, 4]
```

### `is` vs `==`

```python
# `is` checks identity (same object), `==` checks equality (same value)
a = [1, 2, 3]
b = [1, 2, 3]
a == b  # True  (same value)
a is b  # False (different objects)

# Only use `is` for: None, True, False, sentinel objects
if result is None: ...
```

### Shallow vs Deep Copy

```python
import copy

original = {"users": [{"name": "alice"}]}
shallow = original.copy()
deep = copy.deepcopy(original)

shallow["users"][0]["name"] = "bob"
# original is also modified! Shallow copy shares nested refs.
# deep copy is independent.
```

### Exception Chaining

```python
# Bad: swallows the original traceback
try:
    parse(data)
except ValueError:
    raise AppError("parse failed")

# Good: preserves the chain with `from`
try:
    parse(data)
except ValueError as e:
    raise AppError("parse failed") from e
```

### Import-Time Side Effects

```python
# Bad: connecting to DB at import time
# db.py
connection = psycopg2.connect(DB_URL)  # runs when module is imported!

# Good: lazy initialization
_connection: Connection | None = None
def get_connection() -> Connection:
    global _connection
    if _connection is None:
        _connection = psycopg2.connect(DB_URL)
    return _connection

# Better: dependency injection (no module-level state at all)
```

## Debugging Systematically

Seniors don't guess — they narrow down.

### The Process

1. **Reproduce** — Write a failing test that captures the bug
2. **Isolate** — Binary search: comment out half the code, does the bug persist?
3. **Understand** — Read the traceback bottom-to-top. What's the actual vs expected state?
4. **Fix** — Fix the root cause, not the symptom
5. **Verify** — The failing test now passes. Add a regression test if it was subtle.

### Tools

| Tool | When |
|------|------|
| `breakpoint()` / `pdb` | Inspect state at a specific point |
| `logging.debug()` | Trace execution flow across calls |
| `python -m traceback` | Get cleaner tracebacks |
| `pytest --pdb` | Drop into debugger on test failure |
| `pytest -x` | Stop on first failure |
| `pytest -k "test_name"` | Run a single test |
| `python -m cProfile` | Find performance bottlenecks |

### Common Bug Categories

| Category | Typical cause | Senior instinct |
|----------|--------------|-----------------|
| Wrong value | Mutation, stale reference | Check mutability, trace data flow |
| AttributeError | None propagation | Find where None enters |
| Silent wrong behavior | Logic inversion, off-by-one | Add assertion at intermediate steps |
| Works locally, fails in CI | Env difference, timing | Check env vars, filesystem, timezone |
| Intermittent failure | Race condition, external dependency | Look for shared mutable state |

## Code Review Mindset

### What Seniors Look For

1. **Correctness** — Does it actually do what it claims?
2. **Edge cases** — What happens with empty input, None, huge data?
3. **Naming** — Can I understand the code without reading the implementation?
4. **Coupling** — Does this change force changes elsewhere?
5. **Testability** — Could I test this function in isolation?
6. **Security** — Is user input trusted? Any injection risks?
7. **Failure modes** — What happens when the network is down? Disk is full?

### Giving Good Feedback

- **Be specific**: "This list comprehension has O(n²) because of the `in` check" not "this is slow"
- **Explain why**: "This mutable default will share state across calls because..."
- **Suggest, don't dictate**: "Consider using a frozen dataclass here — it prevents accidental mutation and makes the intent clear"
- **Praise good things**: "Nice use of dependency injection here — it makes this really easy to test"

## Mid → Senior Growth Patterns

| Mid-Level Habit | Senior Upgrade |
|----------------|----------------|
| Write code, then write tests | Write tests first — they clarify the design |
| Solve the problem in front of you | Ask "what could go wrong?" before coding |
| Use classes because OOP | Ask "does this need state?" — often a function suffices |
| Catch broad exceptions | Catch specific exceptions, let unexpected ones propagate |
| `print()` debugging | `logging` + `breakpoint()` + failing test |
| Copy-paste then tweak | Extract, parameterize, compose |
| "It works on my machine" | Think about CI, deployment, observability from the start |
| Long functions with comments | Short functions with good names (comments become unnecessary) |
| Reach for a framework first | Understand the problem domain first, choose tools second |
| Optimize prematurely | Measure first, optimize the proven bottleneck |
| "I'll refactor later" | Refactor now, in the TDD cycle, while context is fresh |
