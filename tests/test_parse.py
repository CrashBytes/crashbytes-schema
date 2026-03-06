"""Tests for parse vs safe_parse behavior and error paths."""

import pytest

from crashbytes_schema import ParseResult, SchemaError, ValidationError, s


class TestParse:
    def test_parse_returns_data(self) -> None:
        result = s.string().parse("hello")
        assert result == "hello"

    def test_parse_raises_schema_error(self) -> None:
        with pytest.raises(SchemaError) as exc_info:
            s.string().parse(42)
        assert len(exc_info.value.errors) > 0
        assert isinstance(exc_info.value.errors[0], ValidationError)

    def test_schema_error_message(self) -> None:
        with pytest.raises(SchemaError, match="Validation failed"):
            s.integer().parse("not a number")


class TestSafeParse:
    def test_success(self) -> None:
        result = s.string().safe_parse("hello")
        assert result.success is True
        assert result.data == "hello"
        assert result.errors == []

    def test_failure(self) -> None:
        result = s.string().safe_parse(42)
        assert result.success is False
        assert result.data is None
        assert len(result.errors) > 0

    def test_never_raises(self) -> None:
        result = s.integer().safe_parse("bad")
        assert isinstance(result, ParseResult)
        assert result.success is False


class TestErrorPaths:
    def test_root_path(self) -> None:
        result = s.string().safe_parse(42)
        assert result.errors[0].path == ""

    def test_object_field_path(self) -> None:
        schema = s.object({"name": s.string()})
        result = schema.safe_parse({"name": 42})
        assert result.errors[0].path == "name"

    def test_nested_object_path(self) -> None:
        schema = s.object({"user": s.object({"email": s.string()})})
        result = schema.safe_parse({"user": {"email": 42}})
        assert result.errors[0].path == "user.email"

    def test_array_index_path(self) -> None:
        schema = s.array(s.string())
        result = schema.safe_parse(["a", 42])
        assert result.errors[0].path == "[1]"

    def test_array_in_object_path(self) -> None:
        schema = s.object({"tags": s.array(s.string())})
        result = schema.safe_parse({"tags": ["ok", 42]})
        assert result.errors[0].path == "tags[1]"

    def test_object_in_array_path(self) -> None:
        schema = s.array(s.object({"id": s.integer()}))
        result = schema.safe_parse([{"id": 1}, {"id": "bad"}])
        assert result.errors[0].path == "[1].id"

    def test_missing_field_path(self) -> None:
        schema = s.object({"name": s.string()})
        result = schema.safe_parse({})
        assert result.errors[0].path == "name"
        assert result.errors[0].code == "missing"


class TestErrorCodes:
    def test_invalid_type(self) -> None:
        result = s.string().safe_parse(42)
        assert result.errors[0].code == "invalid_type"

    def test_too_small(self) -> None:
        result = s.string().min(5).safe_parse("ab")
        assert result.errors[0].code == "too_small"

    def test_too_big(self) -> None:
        result = s.string().max(2).safe_parse("abc")
        assert result.errors[0].code == "too_big"

    def test_invalid_string(self) -> None:
        result = s.string().email().safe_parse("bad")
        assert result.errors[0].code == "invalid_string"

    def test_invalid_literal(self) -> None:
        result = s.literal("yes").safe_parse("no")
        assert result.errors[0].code == "invalid_literal"

    def test_invalid_union(self) -> None:
        result = s.union(s.string(), s.integer()).safe_parse([])
        assert result.errors[0].code == "invalid_union"

    def test_unrecognized_key(self) -> None:
        result = s.object({"a": s.string()}).strict().safe_parse({"a": "x", "b": "y"})
        assert any(e.code == "unrecognized_key" for e in result.errors)


class TestMultipleErrors:
    def test_object_multiple_missing(self) -> None:
        schema = s.object({"a": s.string(), "b": s.integer(), "c": s.boolean()})
        result = schema.safe_parse({})
        assert len(result.errors) == 3

    def test_array_multiple_invalid(self) -> None:
        schema = s.array(s.integer())
        result = schema.safe_parse(["a", "b", "c"])
        assert len(result.errors) == 3


class TestComplexSchema:
    def test_full_schema(self) -> None:
        user_schema = s.object(
            {
                "name": s.string().min(1).max(100),
                "email": s.string().email(),
                "age": s.integer().min(0).max(150),
                "role": s.union(s.literal("admin"), s.literal("user")),
                "tags": s.array(s.string()).nonempty(),
                "bio": s.optional(s.string().max(500)),
            }
        )

        valid_data = {
            "name": "Alice",
            "email": "alice@example.com",
            "age": 30,
            "role": "admin",
            "tags": ["developer"],
            "bio": None,
        }
        assert user_schema.parse(valid_data) == valid_data

    def test_full_schema_invalid(self) -> None:
        user_schema = s.object(
            {
                "name": s.string().min(1),
                "email": s.string().email(),
                "age": s.integer().positive(),
            }
        )
        result = user_schema.safe_parse(
            {
                "name": "",
                "email": "bad",
                "age": -1,
            }
        )
        assert result.success is False
        assert len(result.errors) == 3
