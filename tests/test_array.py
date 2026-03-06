"""Tests for ArraySchema."""

import pytest

from crashbytes_schema import SchemaError, s


class TestArrayBasic:
    def test_valid_array(self) -> None:
        schema = s.array(s.integer())
        assert schema.parse([1, 2, 3]) == [1, 2, 3]

    def test_empty_array(self) -> None:
        schema = s.array(s.string())
        assert schema.parse([]) == []

    def test_rejects_non_list(self) -> None:
        schema = s.array(s.string())
        with pytest.raises(SchemaError):
            schema.parse("not a list")

    def test_rejects_dict(self) -> None:
        schema = s.array(s.string())
        with pytest.raises(SchemaError):
            schema.parse({"a": 1})

    def test_invalid_element(self) -> None:
        schema = s.array(s.string())
        with pytest.raises(SchemaError) as exc_info:
            schema.parse(["a", 42, "c"])
        assert any("[1]" in e.path for e in exc_info.value.errors)


class TestArrayMin:
    def test_at_minimum(self) -> None:
        schema = s.array(s.integer()).min(2)
        assert schema.parse([1, 2]) == [1, 2]

    def test_below_minimum(self) -> None:
        schema = s.array(s.integer()).min(2)
        with pytest.raises(SchemaError):
            schema.parse([1])


class TestArrayMax:
    def test_at_maximum(self) -> None:
        schema = s.array(s.integer()).max(3)
        assert schema.parse([1, 2, 3]) == [1, 2, 3]

    def test_above_maximum(self) -> None:
        schema = s.array(s.integer()).max(2)
        with pytest.raises(SchemaError):
            schema.parse([1, 2, 3])


class TestArrayNonempty:
    def test_nonempty_with_items(self) -> None:
        schema = s.array(s.string()).nonempty()
        assert schema.parse(["a"]) == ["a"]

    def test_nonempty_empty_array(self) -> None:
        schema = s.array(s.string()).nonempty()
        with pytest.raises(SchemaError):
            schema.parse([])


class TestArrayNested:
    def test_array_of_objects(self) -> None:
        schema = s.array(s.object({"id": s.integer()}))
        data = [{"id": 1}, {"id": 2}]
        assert schema.parse(data) == data

    def test_array_of_arrays(self) -> None:
        schema = s.array(s.array(s.integer()))
        data = [[1, 2], [3, 4]]
        assert schema.parse(data) == data

    def test_nested_error_path(self) -> None:
        schema = s.array(s.object({"name": s.string()}))
        with pytest.raises(SchemaError) as exc_info:
            schema.parse([{"name": "ok"}, {"name": 42}])
        assert any("[1].name" in e.path for e in exc_info.value.errors)


class TestArrayChaining:
    def test_min_max_chain(self) -> None:
        schema = s.array(s.integer()).min(1).max(3)
        assert schema.parse([1, 2]) == [1, 2]

        with pytest.raises(SchemaError):
            schema.parse([])

        with pytest.raises(SchemaError):
            schema.parse([1, 2, 3, 4])

    def test_immutability(self) -> None:
        base = s.array(s.integer())
        nonempty = base.nonempty()
        assert base.parse([]) == []
        with pytest.raises(SchemaError):
            nonempty.parse([])
