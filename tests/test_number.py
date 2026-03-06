"""Tests for IntSchema and NumberSchema."""

import pytest

from crashbytes_schema import SchemaError, s


class TestIntBasic:
    def test_valid_int(self) -> None:
        assert s.integer().parse(42) == 42

    def test_rejects_float(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().parse(3.14)

    def test_rejects_string(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().parse("42")

    def test_rejects_bool(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().parse(True)

    def test_zero(self) -> None:
        assert s.integer().parse(0) == 0

    def test_negative(self) -> None:
        assert s.integer().parse(-5) == -5


class TestIntMin:
    def test_at_minimum(self) -> None:
        assert s.integer().min(0).parse(0) == 0

    def test_below_minimum(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().min(0).parse(-1)


class TestIntMax:
    def test_at_maximum(self) -> None:
        assert s.integer().max(100).parse(100) == 100

    def test_above_maximum(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().max(100).parse(101)


class TestIntPositive:
    def test_positive_number(self) -> None:
        assert s.integer().positive().parse(1) == 1

    def test_zero_not_positive(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().positive().parse(0)

    def test_negative_not_positive(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().positive().parse(-1)


class TestIntNegative:
    def test_negative_number(self) -> None:
        assert s.integer().negative().parse(-1) == -1

    def test_zero_not_negative(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().negative().parse(0)

    def test_positive_not_negative(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().negative().parse(1)


class TestNumberBasic:
    def test_valid_float(self) -> None:
        assert s.number().parse(3.14) == 3.14

    def test_valid_int_as_number(self) -> None:
        assert s.number().parse(42) == 42

    def test_rejects_string(self) -> None:
        with pytest.raises(SchemaError):
            s.number().parse("3.14")

    def test_rejects_bool(self) -> None:
        with pytest.raises(SchemaError):
            s.number().parse(False)


class TestNumberMin:
    def test_at_minimum(self) -> None:
        assert s.number().min(0.0).parse(0.0) == 0.0

    def test_below_minimum(self) -> None:
        with pytest.raises(SchemaError):
            s.number().min(0.0).parse(-0.1)


class TestNumberMax:
    def test_at_maximum(self) -> None:
        assert s.number().max(99.9).parse(99.9) == 99.9

    def test_above_maximum(self) -> None:
        with pytest.raises(SchemaError):
            s.number().max(99.9).parse(100.0)


class TestNumberPositive:
    def test_positive_float(self) -> None:
        assert s.number().positive().parse(0.001) == 0.001

    def test_zero_not_positive(self) -> None:
        with pytest.raises(SchemaError):
            s.number().positive().parse(0)


class TestNumberChaining:
    def test_min_max_chain(self) -> None:
        schema = s.number().min(0).max(100)
        assert schema.parse(50.5) == 50.5

        with pytest.raises(SchemaError):
            schema.parse(-1)

        with pytest.raises(SchemaError):
            schema.parse(101)

    def test_immutability(self) -> None:
        base = s.integer()
        positive = base.positive()
        assert base.parse(-1) == -1
        with pytest.raises(SchemaError):
            positive.parse(-1)
