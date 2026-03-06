"""Tests for ObjectSchema."""

import pytest

from crashbytes_schema import SchemaError, s


class TestObjectBasic:
    def test_valid_object(self) -> None:
        schema = s.object({"name": s.string(), "age": s.integer()})
        data = {"name": "Alice", "age": 30}
        assert schema.parse(data) == data

    def test_rejects_non_dict(self) -> None:
        schema = s.object({"x": s.string()})
        with pytest.raises(SchemaError):
            schema.parse("not a dict")

    def test_rejects_list(self) -> None:
        schema = s.object({"x": s.string()})
        with pytest.raises(SchemaError):
            schema.parse([1, 2, 3])

    def test_missing_required_field(self) -> None:
        schema = s.object({"name": s.string(), "age": s.integer()})
        with pytest.raises(SchemaError) as exc_info:
            schema.parse({"name": "Alice"})
        assert any(e.code == "missing" for e in exc_info.value.errors)

    def test_wrong_type_in_field(self) -> None:
        schema = s.object({"name": s.string()})
        with pytest.raises(SchemaError):
            schema.parse({"name": 42})

    def test_extra_keys_allowed_by_default(self) -> None:
        schema = s.object({"name": s.string()})
        data = {"name": "Alice", "extra": True}
        assert schema.parse(data) == data


class TestObjectStrict:
    def test_rejects_extra_keys(self) -> None:
        schema = s.object({"name": s.string()}).strict()
        with pytest.raises(SchemaError) as exc_info:
            schema.parse({"name": "Alice", "extra": True})
        assert any(e.code == "unrecognized_key" for e in exc_info.value.errors)

    def test_accepts_exact_keys(self) -> None:
        schema = s.object({"name": s.string()}).strict()
        assert schema.parse({"name": "Alice"}) == {"name": "Alice"}

    def test_strict_immutability(self) -> None:
        base = s.object({"name": s.string()})
        strict = base.strict()
        # base should still allow extra keys
        base.parse({"name": "Alice", "extra": True})
        with pytest.raises(SchemaError):
            strict.parse({"name": "Alice", "extra": True})


class TestObjectPartial:
    def test_all_fields_optional(self) -> None:
        schema = s.object({"name": s.string(), "age": s.integer()}).partial()
        assert schema.parse({}) == {}
        assert schema.parse({"name": "Alice"}) == {"name": "Alice"}

    def test_partial_still_validates_types(self) -> None:
        schema = s.object({"name": s.string()}).partial()
        with pytest.raises(SchemaError):
            schema.parse({"name": 42})

    def test_partial_immutability(self) -> None:
        base = s.object({"name": s.string()})
        partial = base.partial()
        with pytest.raises(SchemaError):
            base.parse({})
        assert partial.parse({}) == {}


class TestObjectOptionalField:
    def test_optional_field_present(self) -> None:
        schema = s.object({"name": s.string(), "bio": s.optional(s.string())})
        data = {"name": "Alice", "bio": "hello"}
        assert schema.parse(data) == data

    def test_optional_field_none(self) -> None:
        schema = s.object({"name": s.string(), "bio": s.optional(s.string())})
        data = {"name": "Alice", "bio": None}
        assert schema.parse(data) == data

    def test_optional_field_missing(self) -> None:
        schema = s.object({"name": s.string(), "bio": s.optional(s.string())})
        data = {"name": "Alice"}
        assert schema.parse(data) == data


class TestNestedObjects:
    def test_nested_valid(self) -> None:
        schema = s.object(
            {
                "user": s.object(
                    {
                        "name": s.string(),
                        "address": s.object(
                            {
                                "city": s.string(),
                            }
                        ),
                    }
                ),
            }
        )
        data = {"user": {"name": "Alice", "address": {"city": "NYC"}}}
        assert schema.parse(data) == data

    def test_nested_invalid(self) -> None:
        schema = s.object(
            {
                "user": s.object({"name": s.string()}),
            }
        )
        with pytest.raises(SchemaError) as exc_info:
            schema.parse({"user": {"name": 42}})
        assert any("user.name" in e.path for e in exc_info.value.errors)

    def test_nested_missing(self) -> None:
        schema = s.object(
            {
                "user": s.object({"name": s.string()}),
            }
        )
        with pytest.raises(SchemaError) as exc_info:
            schema.parse({"user": {}})
        assert any("user.name" in e.path for e in exc_info.value.errors)
