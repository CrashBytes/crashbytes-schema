"""Tests for UnionSchema and LiteralSchema."""

import pytest

from crashbytes_schema import SchemaError, s


class TestLiteral:
    def test_matching_string(self) -> None:
        assert s.literal("admin").parse("admin") == "admin"

    def test_non_matching_string(self) -> None:
        with pytest.raises(SchemaError):
            s.literal("admin").parse("user")

    def test_matching_int(self) -> None:
        assert s.literal(42).parse(42) == 42

    def test_matching_bool(self) -> None:
        assert s.literal(True).parse(True) is True

    def test_non_matching_type(self) -> None:
        with pytest.raises(SchemaError):
            s.literal("1").parse(1)

    def test_int_literal_rejects_bool(self) -> None:
        # True == 1 in Python, but a literal must match type exactly
        with pytest.raises(SchemaError):
            s.literal(1).parse(True)

    def test_bool_literal_rejects_int(self) -> None:
        with pytest.raises(SchemaError):
            s.literal(True).parse(1)

    def test_int_literal_rejects_float(self) -> None:
        with pytest.raises(SchemaError):
            s.literal(1).parse(1.0)

    def test_none_literal(self) -> None:
        assert s.literal(None).parse(None) is None


class TestUnion:
    def test_matches_first(self) -> None:
        schema = s.union(s.string(), s.integer())
        assert schema.parse("hello") == "hello"

    def test_matches_second(self) -> None:
        schema = s.union(s.string(), s.integer())
        assert schema.parse(42) == 42

    def test_no_match(self) -> None:
        schema = s.union(s.string(), s.integer())
        with pytest.raises(SchemaError) as exc_info:
            schema.parse(3.14)
        assert any(e.code == "invalid_union" for e in exc_info.value.errors)

    def test_literal_union(self) -> None:
        status = s.union(s.literal("active"), s.literal("inactive"), s.literal("pending"))
        assert status.parse("active") == "active"
        assert status.parse("pending") == "pending"

        with pytest.raises(SchemaError):
            status.parse("unknown")

    def test_union_with_objects(self) -> None:
        dog = s.object({"type": s.literal("dog"), "bark": s.boolean()})
        cat = s.object({"type": s.literal("cat"), "purr": s.boolean()})
        animal = s.union(dog, cat)

        assert animal.parse({"type": "dog", "bark": True}) == {"type": "dog", "bark": True}
        assert animal.parse({"type": "cat", "purr": True}) == {"type": "cat", "purr": True}

        with pytest.raises(SchemaError):
            animal.parse({"type": "fish"})


class TestBoolean:
    def test_true(self) -> None:
        assert s.boolean().parse(True) is True

    def test_false(self) -> None:
        assert s.boolean().parse(False) is False

    def test_rejects_int(self) -> None:
        with pytest.raises(SchemaError):
            s.boolean().parse(1)

    def test_rejects_string(self) -> None:
        with pytest.raises(SchemaError):
            s.boolean().parse("true")
