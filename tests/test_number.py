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


class TestIntMultipleOf:
    def test_multiple(self) -> None:
        assert s.integer().multiple_of(5).parse(15) == 15

    def test_not_multiple(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().multiple_of(5).parse(12)

    def test_zero_is_multiple_of_anything(self) -> None:
        assert s.integer().multiple_of(7).parse(0) == 0

    def test_negative_multiple(self) -> None:
        assert s.integer().multiple_of(3).parse(-9) == -9

    def test_invalid_number_code(self) -> None:
        with pytest.raises(SchemaError) as exc_info:
            s.integer().multiple_of(2).parse(3)
        assert any(e.code == "invalid_number" for e in exc_info.value.errors)


class TestIntOneOf:
    def test_matching_value(self) -> None:
        assert s.integer().one_of(1, 2, 3).parse(2) == 2

    def test_non_matching_value(self) -> None:
        with pytest.raises(SchemaError):
            s.integer().one_of(1, 2, 3).parse(4)

    def test_invalid_choice_code(self) -> None:
        with pytest.raises(SchemaError) as exc_info:
            s.integer().one_of(1, 2).parse(9)
        assert any(e.code == "invalid_choice" for e in exc_info.value.errors)


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


class TestNumberNegative:
    def test_negative_float(self) -> None:
        assert s.number().negative().parse(-3.5) == -3.5

    def test_zero_not_negative(self) -> None:
        with pytest.raises(SchemaError):
            s.number().negative().parse(0)

    def test_positive_not_negative(self) -> None:
        with pytest.raises(SchemaError):
            s.number().negative().parse(1)


class TestNumberMultipleOf:
    def test_multiple(self) -> None:
        assert s.number().multiple_of(0.5).parse(2.5) == 2.5

    def test_not_multiple(self) -> None:
        with pytest.raises(SchemaError):
            s.number().multiple_of(0.5).parse(1.3)


class TestNumberOneOf:
    def test_matching_value(self) -> None:
        assert s.number().one_of(0.5, 1.0).parse(1.0) == 1.0

    def test_non_matching_value(self) -> None:
        with pytest.raises(SchemaError):
            s.number().one_of(0.5, 1.0).parse(2.5)


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
