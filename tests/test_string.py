"""Tests for StringSchema."""

import pytest

from crashbytes_schema import SchemaError, s


class TestStringBasic:
    def test_valid_string(self) -> None:
        assert s.string().parse("hello") == "hello"

    def test_rejects_int(self) -> None:
        with pytest.raises(SchemaError):
            s.string().parse(42)

    def test_rejects_none(self) -> None:
        with pytest.raises(SchemaError):
            s.string().parse(None)

    def test_rejects_bool(self) -> None:
        with pytest.raises(SchemaError):
            s.string().parse(True)


class TestStringMin:
    def test_at_minimum(self) -> None:
        assert s.string().min(3).parse("abc") == "abc"

    def test_below_minimum(self) -> None:
        with pytest.raises(SchemaError):
            s.string().min(3).parse("ab")

    def test_above_minimum(self) -> None:
        assert s.string().min(2).parse("abc") == "abc"


class TestStringMax:
    def test_at_maximum(self) -> None:
        assert s.string().max(3).parse("abc") == "abc"

    def test_above_maximum(self) -> None:
        with pytest.raises(SchemaError):
            s.string().max(3).parse("abcd")

    def test_below_maximum(self) -> None:
        assert s.string().max(5).parse("abc") == "abc"


class TestStringRegex:
    def test_matching_pattern(self) -> None:
        assert s.string().regex(r"^\d+$").parse("123") == "123"

    def test_non_matching_pattern(self) -> None:
        with pytest.raises(SchemaError):
            s.string().regex(r"^\d+$").parse("abc")


class TestStringEmail:
    def test_valid_email(self) -> None:
        assert s.string().email().parse("user@example.com") == "user@example.com"

    def test_invalid_email(self) -> None:
        with pytest.raises(SchemaError):
            s.string().email().parse("not-an-email")

    def test_missing_tld(self) -> None:
        with pytest.raises(SchemaError):
            s.string().email().parse("user@localhost")


class TestStringUrl:
    def test_valid_http(self) -> None:
        assert s.string().url().parse("http://example.com") == "http://example.com"

    def test_valid_https(self) -> None:
        assert s.string().url().parse("https://example.com/path") == "https://example.com/path"

    def test_invalid_url(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("not-a-url")


class TestStringNonempty:
    def test_nonempty_with_content(self) -> None:
        assert s.string().nonempty().parse("a") == "a"

    def test_nonempty_empty_string(self) -> None:
        with pytest.raises(SchemaError):
            s.string().nonempty().parse("")


class TestStringChaining:
    def test_min_and_max(self) -> None:
        schema = s.string().min(2).max(5)
        assert schema.parse("abc") == "abc"

        with pytest.raises(SchemaError):
            schema.parse("a")

        with pytest.raises(SchemaError):
            schema.parse("abcdef")

    def test_immutability(self) -> None:
        base = s.string()
        with_min = base.min(3)
        # base should still accept short strings
        assert base.parse("a") == "a"
        with pytest.raises(SchemaError):
            with_min.parse("a")
