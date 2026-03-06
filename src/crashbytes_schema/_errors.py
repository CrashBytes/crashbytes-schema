"""Validation error types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ValidationError:
    """A single validation error with path and message."""

    path: str
    message: str
    code: str


@dataclass(frozen=True)
class ParseResult:
    """Result of a safe_parse call."""

    success: bool
    data: object = None
    errors: list[ValidationError] = field(default_factory=list)


class SchemaError(Exception):
    """Raised when parse() fails validation."""

    def __init__(self, errors: list[ValidationError]) -> None:
        self.errors = errors
        messages = "; ".join(f"{e.path}: {e.message}" for e in errors)
        super().__init__(f"Validation failed: {messages}")
