"""Schema definitions — the core of crashbytes-schema."""

from __future__ import annotations

import copy
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from crashbytes_schema._errors import ParseResult, SchemaError, ValidationError

# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------


@dataclass(frozen=False)
class _Rule:
    """Internal rule: a check function plus metadata."""

    check: Any  # Callable[[Any, str], list[ValidationError]]
    name: str


class Schema(ABC):
    """Base class for all schemas."""

    def __init__(self) -> None:
        self._rules: list[_Rule] = []

    def _clone(self) -> Schema:
        """Return a shallow copy so mutations don't affect the original."""
        new = copy.copy(self)
        new._rules = list(self._rules)
        return new

    def _add_rule(self, name: str, check: Any) -> Schema:
        clone = self._clone()
        clone._rules.append(_Rule(check=check, name=name))
        return clone

    @abstractmethod
    def _validate(self, data: object, path: str) -> list[ValidationError]:
        """Run type-level validation (before rules)."""

    def _run_rules(self, data: object, path: str) -> list[ValidationError]:
        errors: list[ValidationError] = []
        for rule in self._rules:
            errors.extend(rule.check(data, path))
        return errors

    def _full_validate(self, data: object, path: str) -> list[ValidationError]:
        errors = self._validate(data, path)
        if errors:
            return errors
        return self._run_rules(data, path)

    def parse(self, data: object) -> object:
        """Validate and return data, or raise SchemaError."""
        errors = self._full_validate(data, "")
        if errors:
            raise SchemaError(errors)
        return data

    def safe_parse(self, data: object) -> ParseResult:
        """Validate and return a ParseResult (never raises)."""
        errors = self._full_validate(data, "")
        if errors:
            return ParseResult(success=False, data=None, errors=errors)
        return ParseResult(success=True, data=data, errors=[])


# ---------------------------------------------------------------------------
# String
# ---------------------------------------------------------------------------


class StringSchema(Schema):
    """Schema for string values."""

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        if not isinstance(data, str):
            return [ValidationError(path=path, message="Expected string", code="invalid_type")]
        return []

    def min(self, n: int) -> StringSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, str)
            if len(data) < n:
                return [
                    ValidationError(
                        path=path,
                        message=f"String must be at least {n} characters",
                        code="too_small",
                    )
                ]
            return []

        return self._add_rule("min", check)  # type: ignore[return-value]

    def max(self, n: int) -> StringSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, str)
            if len(data) > n:
                return [
                    ValidationError(
                        path=path,
                        message=f"String must be at most {n} characters",
                        code="too_big",
                    )
                ]
            return []

        return self._add_rule("max", check)  # type: ignore[return-value]

    def regex(self, pattern: str) -> StringSchema:
        compiled = re.compile(pattern)

        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, str)
            if not compiled.search(data):
                return [
                    ValidationError(
                        path=path,
                        message=f"String must match pattern {pattern}",
                        code="invalid_string",
                    )
                ]
            return []

        return self._add_rule("regex", check)  # type: ignore[return-value]

    def email(self) -> StringSchema:
        email_re = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, str)
            if not email_re.match(data):
                return [
                    ValidationError(
                        path=path, message="Invalid email address", code="invalid_string"
                    )
                ]
            return []

        return self._add_rule("email", check)  # type: ignore[return-value]

    def url(self) -> StringSchema:
        url_re = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")

        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, str)
            if not url_re.match(data):
                return [ValidationError(path=path, message="Invalid URL", code="invalid_string")]
            return []

        return self._add_rule("url", check)  # type: ignore[return-value]

    def nonempty(self) -> StringSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, str)
            if len(data) == 0:
                return [
                    ValidationError(
                        path=path, message="String must not be empty", code="too_small"
                    )
                ]
            return []

        return self._add_rule("nonempty", check)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Integer
# ---------------------------------------------------------------------------


class IntSchema(Schema):
    """Schema for integer values."""

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        # Reject bools (bool is subclass of int in Python)
        if isinstance(data, bool) or not isinstance(data, int):
            return [ValidationError(path=path, message="Expected integer", code="invalid_type")]
        return []

    def min(self, n: int) -> IntSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, int)
            if data < n:
                return [
                    ValidationError(path=path, message=f"Number must be >= {n}", code="too_small")
                ]
            return []

        return self._add_rule("min", check)  # type: ignore[return-value]

    def max(self, n: int) -> IntSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, int)
            if data > n:
                return [
                    ValidationError(path=path, message=f"Number must be <= {n}", code="too_big")
                ]
            return []

        return self._add_rule("max", check)  # type: ignore[return-value]

    def positive(self) -> IntSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, int)
            if data <= 0:
                return [
                    ValidationError(path=path, message="Number must be positive", code="too_small")
                ]
            return []

        return self._add_rule("positive", check)  # type: ignore[return-value]

    def negative(self) -> IntSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, int)
            if data >= 0:
                return [
                    ValidationError(path=path, message="Number must be negative", code="too_big")
                ]
            return []

        return self._add_rule("negative", check)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Number (float)
# ---------------------------------------------------------------------------


class NumberSchema(Schema):
    """Schema for numeric (int or float) values."""

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        if isinstance(data, bool) or not isinstance(data, (int, float)):
            return [ValidationError(path=path, message="Expected number", code="invalid_type")]
        return []

    def min(self, n: float) -> NumberSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, (int, float))
            if data < n:
                return [
                    ValidationError(path=path, message=f"Number must be >= {n}", code="too_small")
                ]
            return []

        return self._add_rule("min", check)  # type: ignore[return-value]

    def max(self, n: float) -> NumberSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, (int, float))
            if data > n:
                return [
                    ValidationError(path=path, message=f"Number must be <= {n}", code="too_big")
                ]
            return []

        return self._add_rule("max", check)  # type: ignore[return-value]

    def positive(self) -> NumberSchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, (int, float))
            if data <= 0:
                return [
                    ValidationError(path=path, message="Number must be positive", code="too_small")
                ]
            return []

        return self._add_rule("positive", check)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Boolean
# ---------------------------------------------------------------------------


class BoolSchema(Schema):
    """Schema for boolean values."""

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        if not isinstance(data, bool):
            return [ValidationError(path=path, message="Expected boolean", code="invalid_type")]
        return []


# ---------------------------------------------------------------------------
# Literal
# ---------------------------------------------------------------------------


class LiteralSchema(Schema):
    """Schema that matches a single literal value."""

    def __init__(self, value: object) -> None:
        super().__init__()
        self._value = value

    def _clone(self) -> LiteralSchema:
        new = copy.copy(self)
        new._rules = list(self._rules)
        return new

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        if data != self._value:
            return [
                ValidationError(
                    path=path,
                    message=f"Expected literal {self._value!r}",
                    code="invalid_literal",
                )
            ]
        return []


# ---------------------------------------------------------------------------
# Array
# ---------------------------------------------------------------------------


class ArraySchema(Schema):
    """Schema for list values with inner element validation."""

    def __init__(self, inner: Schema) -> None:
        super().__init__()
        self._inner = inner

    def _clone(self) -> ArraySchema:
        new = copy.copy(self)
        new._rules = list(self._rules)
        return new

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        if not isinstance(data, list):
            return [ValidationError(path=path, message="Expected array", code="invalid_type")]
        errors: list[ValidationError] = []
        for i, item in enumerate(data):
            item_path = f"{path}[{i}]" if path else f"[{i}]"
            errors.extend(self._inner._full_validate(item, item_path))
        return errors

    def min(self, n: int) -> ArraySchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, list)
            if len(data) < n:
                return [
                    ValidationError(
                        path=path, message=f"Array must have at least {n} items", code="too_small"
                    )
                ]
            return []

        return self._add_rule("min", check)  # type: ignore[return-value]

    def max(self, n: int) -> ArraySchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, list)
            if len(data) > n:
                return [
                    ValidationError(
                        path=path, message=f"Array must have at most {n} items", code="too_big"
                    )
                ]
            return []

        return self._add_rule("max", check)  # type: ignore[return-value]

    def nonempty(self) -> ArraySchema:
        def check(data: object, path: str) -> list[ValidationError]:
            assert isinstance(data, list)
            if len(data) == 0:
                return [
                    ValidationError(path=path, message="Array must not be empty", code="too_small")
                ]
            return []

        return self._add_rule("nonempty", check)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Object
# ---------------------------------------------------------------------------


class ObjectSchema(Schema):
    """Schema for dict values with named fields."""

    def __init__(self, shape: dict[str, Schema]) -> None:
        super().__init__()
        self._shape = shape
        self._strict_mode = False
        self._partial_mode = False

    def _clone(self) -> ObjectSchema:
        new = copy.copy(self)
        new._rules = list(self._rules)
        new._shape = dict(self._shape)
        return new

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        if not isinstance(data, dict):
            return [ValidationError(path=path, message="Expected object", code="invalid_type")]
        errors: list[ValidationError] = []

        # Check for extra keys in strict mode
        if self._strict_mode:
            extra = set(data.keys()) - set(self._shape.keys())
            for key in sorted(extra):
                key_path = f"{path}.{key}" if path else key
                errors.append(
                    ValidationError(
                        path=key_path,
                        message=f"Unexpected key '{key}'",
                        code="unrecognized_key",
                    )
                )

        # Validate each field
        for key, schema in self._shape.items():
            key_path = f"{path}.{key}" if path else key
            if key not in data:
                if self._partial_mode:
                    continue
                if isinstance(schema, OptionalSchema):
                    continue
                errors.append(
                    ValidationError(
                        path=key_path, message=f"Required field '{key}' is missing", code="missing"
                    )
                )
            else:
                errors.extend(schema._full_validate(data[key], key_path))

        return errors

    def strict(self) -> ObjectSchema:
        """Return a new schema that rejects unrecognized keys."""
        clone = self._clone()
        clone._strict_mode = True
        return clone

    def partial(self) -> ObjectSchema:
        """Return a new schema where all fields are optional."""
        clone = self._clone()
        clone._partial_mode = True
        return clone


# ---------------------------------------------------------------------------
# Optional
# ---------------------------------------------------------------------------


class OptionalSchema(Schema):
    """Wraps a schema to also accept None."""

    def __init__(self, inner: Schema) -> None:
        super().__init__()
        self._inner = inner

    def _clone(self) -> OptionalSchema:
        new = copy.copy(self)
        new._rules = list(self._rules)
        return new

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        if data is None:
            return []
        return self._inner._full_validate(data, path)


# ---------------------------------------------------------------------------
# Union
# ---------------------------------------------------------------------------


class UnionSchema(Schema):
    """Matches if any of the provided schemas validate."""

    def __init__(self, *schemas: Schema) -> None:
        super().__init__()
        self._schemas = list(schemas)

    def _clone(self) -> UnionSchema:
        new = copy.copy(self)
        new._rules = list(self._rules)
        new._schemas = list(self._schemas)
        return new

    def _validate(self, data: object, path: str) -> list[ValidationError]:
        all_errors: list[ValidationError] = []
        for schema in self._schemas:
            errors = schema._full_validate(data, path)
            if not errors:
                return []
            all_errors.extend(errors)
        return [
            ValidationError(
                path=path,
                message="Value does not match any schema in union",
                code="invalid_union",
            )
        ]


# ---------------------------------------------------------------------------
# Builder (the `s` object)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SchemaBuilder:
    """Convenient entry point — use as `s.string()`, `s.integer()`, etc."""

    @staticmethod
    def string() -> StringSchema:
        return StringSchema()

    @staticmethod
    def integer() -> IntSchema:
        return IntSchema()

    @staticmethod
    def number() -> NumberSchema:
        return NumberSchema()

    @staticmethod
    def boolean() -> BoolSchema:
        return BoolSchema()

    @staticmethod
    def literal(value: object) -> LiteralSchema:
        return LiteralSchema(value)

    @staticmethod
    def array(inner: Schema) -> ArraySchema:
        return ArraySchema(inner)

    @staticmethod
    def object(shape: dict[str, Schema]) -> ObjectSchema:
        return ObjectSchema(shape)

    @staticmethod
    def optional(inner: Schema) -> OptionalSchema:
        return OptionalSchema(inner)

    @staticmethod
    def union(*schemas: Schema) -> UnionSchema:
        return UnionSchema(*schemas)
