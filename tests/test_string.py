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

    def test_valid_email_plus_tag(self) -> None:
        assert (
            s.string().email().parse("user+tag@sub.example.co.uk") == "user+tag@sub.example.co.uk"
        )

    def test_valid_email_dotted_local(self) -> None:
        assert s.string().email().parse("first.last@example.com") == "first.last@example.com"

    def test_invalid_email(self) -> None:
        with pytest.raises(SchemaError):
            s.string().email().parse("not-an-email")

    def test_missing_tld(self) -> None:
        with pytest.raises(SchemaError):
            s.string().email().parse("user@localhost")

    def test_consecutive_dots_local_part(self) -> None:
        with pytest.raises(SchemaError):
            s.string().email().parse("a..b@example.com")

    def test_consecutive_dots_domain(self) -> None:
        with pytest.raises(SchemaError):
            s.string().email().parse("user@example..com")

    def test_leading_hyphen_domain(self) -> None:
        with pytest.raises(SchemaError):
            s.string().email().parse("user@-example.com")


class TestStringUrl:
    def test_valid_http(self) -> None:
        assert s.string().url().parse("http://example.com") == "http://example.com"

    def test_valid_https(self) -> None:
        assert s.string().url().parse("https://example.com/path") == "https://example.com/path"

    def test_valid_subdomain_port(self) -> None:
        assert (
            s.string().url().parse("http://sub.example.co.uk:8080/p")
            == "http://sub.example.co.uk:8080/p"
        )

    def test_valid_localhost(self) -> None:
        assert s.string().url().parse("http://localhost:8000") == "http://localhost:8000"

    def test_valid_ipv4(self) -> None:
        assert s.string().url().parse("http://127.0.0.1:8080/x") == "http://127.0.0.1:8080/x"

    def test_invalid_url(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("not-a-url")

    def test_consecutive_dots(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("http://a..b")

    def test_leading_hyphen_label(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("http://-example.com")

    def test_trailing_hyphen_label(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("http://example-.com")

    def test_single_label_host(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("http://a")

    def test_empty_first_label(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("http://.com")

    def test_ftp_scheme_rejected(self) -> None:
        with pytest.raises(SchemaError):
            s.string().url().parse("ftp://example.com")


class TestStringNonempty:
    def test_nonempty_with_content(self) -> None:
        assert s.string().nonempty().parse("a") == "a"

    def test_nonempty_empty_string(self) -> None:
        with pytest.raises(SchemaError):
            s.string().nonempty().parse("")


class TestStringLength:
    def test_exact_length(self) -> None:
        assert s.string().length(5).parse("hello") == "hello"

    def test_too_short(self) -> None:
        with pytest.raises(SchemaError):
            s.string().length(5).parse("hi")

    def test_too_long(self) -> None:
        with pytest.raises(SchemaError):
            s.string().length(2).parse("hello")

    def test_zero_length(self) -> None:
        assert s.string().length(0).parse("") == ""


class TestStringStartswith:
    def test_matching_prefix(self) -> None:
        assert s.string().startswith("http").parse("http://example.com") == "http://example.com"

    def test_non_matching_prefix(self) -> None:
        with pytest.raises(SchemaError):
            s.string().startswith("https").parse("http://example.com")

    def test_empty_prefix(self) -> None:
        assert s.string().startswith("").parse("anything") == "anything"


class TestStringEndswith:
    def test_matching_suffix(self) -> None:
        assert s.string().endswith(".py").parse("main.py") == "main.py"

    def test_non_matching_suffix(self) -> None:
        with pytest.raises(SchemaError):
            s.string().endswith(".js").parse("main.py")


class TestStringOneOf:
    def test_matching_value(self) -> None:
        assert s.string().one_of("draft", "published").parse("draft") == "draft"

    def test_non_matching_value(self) -> None:
        with pytest.raises(SchemaError):
            s.string().one_of("draft", "published").parse("archived")

    def test_single_value(self) -> None:
        assert s.string().one_of("admin").parse("admin") == "admin"

    def test_invalid_choice_code(self) -> None:
        with pytest.raises(SchemaError) as exc_info:
            s.string().one_of("a", "b").parse("c")
        assert any(e.code == "invalid_choice" for e in exc_info.value.errors)


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
