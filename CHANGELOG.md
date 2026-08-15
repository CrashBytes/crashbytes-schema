# Changelog

All notable changes to this project are documented in this file.

## [1.1.0] - 2026-08-16

### Added
- `StringSchema.length(n)` — exact-length rule
- `StringSchema.startswith(prefix)` / `StringSchema.endswith(suffix)` — prefix/suffix rules
- `StringSchema.one_of(*values)` — enum-style string rule
- `IntSchema.multiple_of(n)` and `NumberSchema.multiple_of(n)` — divisibility rules
- `IntSchema.one_of(*values)` / `NumberSchema.one_of(*values)` — enum-style numeric rules
- `NumberSchema.negative()` — parity with `IntSchema.negative()`
- `ArraySchema.length(n)` — exact-item-count rule
- `Schema.is_valid(data)` — quick boolean validation without exceptions
- `Schema.__repr__` — readable schema descriptions for debugging
- `__version__` — package version now exposed and sourced by hatchling (dynamic version)
- Full README documentation with examples for every schema and rule
- Docstrings on all public rule methods

### Fixed
- `LiteralSchema` now uses exact type equality: `s.literal(1)` rejects `True` and `1.0`
  (previously `True == 1` passed — a bool is a subclass of int)
- `StringSchema.url()` no longer accepts malformed hostnames such as `http://a..b`,
  `http://-example.com`, `http://example-.com`, or `http://a`
- `StringSchema.email()` now rejects consecutive dots in the local part
  (`a..b@example.com`) and in the domain (`user@example..com`)

## [1.0.4] - 2026-07-15

### Fixed
- Dependency updates
