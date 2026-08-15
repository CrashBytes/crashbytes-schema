# crashbytes-schema

**Zero-dependency schema validation for Python** — define, parse, and validate data with chainable rules.

`crashbytes-schema` lets you describe the shape of the data your code expects — strings, numbers, booleans, arrays, objects, optionals, and unions — and validate untrusted input against that description in one line. No dependencies, no code generation, no magic. Just small immutable schema objects you can build, combine, and reuse.

```python
from crashbytes_schema import s

user = s.object(
    {
        "name": s.string().min(1).max(80),
        "email": s.string().email(),
        "age": s.integer().min(18),
        "roles": s.array(s.string()).min(1),
    }
)

user.parse({"name": "Ada", "email": "ada@example.com", "age": 36, "roles": ["admin"]})
# {'name': 'Ada', 'email': 'ada@example.com', 'age': 36, 'roles': ['admin']}
```

## Features

- **Chainable rules** — `s.string().min(1).max(80).regex(r"^[A-Z]")`
- **Immutable by design** — every rule returns a *new* schema; the original is never mutated
- **Precise error paths** — `"users[2].email"`, `"billing.address.zip"`, ready for API responses
- **Strict & partial objects** — reject unknown keys or make every field optional
- **Unions, optionals, and literals** — express `str | int | None`, enums, and discriminated objects
- **`parse` or `safe_parse`** — raise on failure or get a structured `ParseResult`
- **Zero dependencies** — pure Python standard library, works on 3.10+
- **Fully typed** — `py.typed` included, strict-mypy clean

## Installation

```bash
pip install crashbytes-schema
```

## Quick start

```python
from crashbytes_schema import s, SchemaError

schema = s.object(
    {
        "id": s.integer().positive(),
        "title": s.string().min(1).max(200),
        "tags": s.array(s.string()).max(10),
        "status": s.union(s.literal("draft"), s.literal("published")),
        "author": s.optional(s.object({"name": s.string(), "email": s.string().email()})),
    }
)

try:
    schema.parse({"id": 1, "title": "Hello", "tags": ["a"], "status": "draft"})
except SchemaError as exc:
    for err in exc.errors:
        print(err.path, err.message, err.code)
```

## Schemas

All schemas are built through the shared builder object `s` (an instance of `SchemaBuilder`).

### `s.string()`

Validates `str` values.

| Rule | Description |
|---|---|
| `.min(n)` | at least `n` characters |
| `.max(n)` | at most `n` characters |
| `.length(n)` | exactly `n` characters |
| `.regex(pattern)` | matches `pattern` (search semantics) |
| `.email()` | syntactically valid email address |
| `.url()` | valid `http(s)` URL with a well-formed hostname |
| `.nonempty()` | not the empty string |
| `.startswith(prefix)` | starts with `prefix` |
| `.endswith(suffix)` | ends with `suffix` |
| `.one_of(*values)` | one of the given strings |

```python
s.string().email().parse("ada@example.com")
s.string().url().parse("https://example.com/docs")
s.string().one_of("draft", "published").parse("draft")
```

### `s.integer()`

Validates `int` values. **Bools are rejected** (a `bool` is not an integer here).

| Rule | Description |
|---|---|
| `.min(n)` | `>= n` |
| `.max(n)` | `<= n` |
| `.positive()` | `> 0` |
| `.negative()` | `< 0` |
| `.multiple_of(n)` | divisible by `n` |
| `.one_of(*values)` | one of the given integers |

```python
s.integer().min(0).max(100).parse(42)
s.integer().multiple_of(10).parse(30)
```

### `s.number()`

Validates `int` **or** `float` values. Bools are rejected.

| Rule | Description |
|---|---|
| `.min(n)` | `>= n` |
| `.max(n)` | `<= n` |
| `.positive()` | `> 0` |
| `.negative()` | `< 0` |
| `.multiple_of(n)` | multiple of `n` |
| `.one_of(*values)` | one of the given numbers |

```python
s.number().min(0.0).max(1.0).parse(0.75)
```

### `s.boolean()`

Validates `bool` values. Integers and strings like `"true"` are rejected.

```python
s.boolean().parse(True)
```

### `s.literal(value)`

Matches one exact value, with exact type equality: `1` does **not** match `True` or `1.0`.

```python
s.literal("admin").parse("admin")
s.literal(42).parse(42)
```

### `s.array(inner)`

Validates `list` values where every element validates against `inner`.

| Rule | Description |
|---|---|
| `.min(n)` | at least `n` items |
| `.max(n)` | at most `n` items |
| `.length(n)` | exactly `n` items |
| `.nonempty()` | at least one item |

```python
s.array(s.integer()).min(1).parse([1, 2, 3])
s.array(s.object({"id": s.integer()})).parse([{"id": 1}, {"id": 2}])
```

### `s.object(shape)`

Validates `dict` values against a shape of named fields.

- **Required by default** — every field in the shape must be present (unless wrapped in `s.optional(...)` or the schema is `.partial()`).
- `.strict()` — reject unknown keys.
- `.partial()` — make *all* fields optional.

```python
config = s.object(
    {
        "host": s.string().nonempty(),
        "port": s.integer().min(1).max(65535),
    }
).strict()

config.parse({"host": "localhost", "port": 8080})
# strict: {"host": "localhost", "port": 8080, "debug": True} -> SchemaError
```

### `s.optional(inner)`

Accepts `None` or anything `inner` validates. Useful for optional object fields.

```python
s.object({"nickname": s.optional(s.string())}).parse({"nickname": None})
```

### `s.union(*schemas)`

Accepts data that validates against **any** of the given schemas.

```python
s.union(s.string(), s.integer()).parse(42)
s.union(s.literal("active"), s.literal("inactive")).parse("active")
```

## Chaining & immutability

Every rule method returns a **new schema** — building a schema never mutates a previously created one, so shared base schemas are safe to reuse:

```python
base = s.string()
with_min = base.min(3)

base.parse("ab")  # ok — base has no rules
with_min.parse("ab")  # SchemaError
```

Schemas are plain objects and can be stored, combined, and passed around:

```python
id_field = s.integer().positive()
user_schema = s.object({"id": id_field, "name": s.string()})
```

## Error handling

### `parse` raises `SchemaError`

```python
from crashbytes_schema import s, SchemaError

try:
    s.object({"age": s.integer().min(18)}).parse({"age": 12})
except SchemaError as exc:
    print(exc)  # Validation failed: age: Number must be >= 18
    for err in exc.errors:
        print(err.path, err.message, err.code)
        # age  Number must be >= 18  too_small
```

### `safe_parse` returns a `ParseResult`

```python
result = s.object({"age": s.integer()}).safe_parse({"age": "old"})
result.success  # False
result.data  # None
result.errors  # [ValidationError(path='age', message='Expected integer', code='invalid_type')]
```

### `is_valid` for quick checks

```python
s.string().email().is_valid("ada@example.com")  # True
s.string().email().is_valid("nope")  # False
```

### Error codes

| Code | Meaning |
|---|---|
| `invalid_type` | value has the wrong Python type |
| `invalid_literal` | value does not equal the literal |
| `invalid_union` | value matches no branch of the union |
| `invalid_string` | value fails a string rule (regex/email/url/prefix/suffix) |
| `invalid_choice` | value not in `one_of(...)` |
| `invalid_length` | value fails an exact-length rule |
| `invalid_number` | value fails a numeric rule (e.g. `multiple_of`) |
| `too_small` | below a minimum / must be positive / must be non-empty |
| `too_big` | above a maximum / must be negative |
| `missing` | required object field absent |
| `unrecognized_key` | unknown key in strict mode |

## Real-world example

Validating an API request body:

```python
from crashbytes_schema import s

CreateOrder = s.object(
    {
        "customer": s.object(
            {
                "name": s.string().min(1).max(120),
                "email": s.string().email(),
            }
        ).strict(),
        "items": s.array(
            s.object(
                {
                    "sku": s.string().regex(r"^[A-Z]{2}-\d{4}$"),
                    "qty": s.integer().min(1).max(99),
                    "unit_price": s.number().positive(),
                }
            )
        )
        .min(1)
        .max(50),
        "discount_code": s.optional(s.string().regex(r"^[A-Z0-9]{6,12}$")),
    }
).strict()


def create_order(payload: dict) -> dict:
    return CreateOrder.parse(payload)  # raises SchemaError -> 400
```

## Development

```bash
pip install -e ".[dev]"
pytest                      # run the test suite
ruff check . && ruff format --check .
mypy src/
```

## License

MIT
