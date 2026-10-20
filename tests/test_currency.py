import pytest

from models.currency import (
    ValidationError,
    validate_amount,
    validate_conversion,
    validate_currency,
)

SUPPORTED = {"USD": 1.0, "PHP": 58.0, "EUR": 0.9}


@pytest.mark.parametrize("bad", ["", "   ", None])
def test_empty_amount_rejected(bad):
    with pytest.raises(ValidationError):
        validate_amount(bad)


@pytest.mark.parametrize("bad", ["abc", "12abc", "1.2.3", "1,5", "12,34,567", "--5", "$100"])
def test_non_numeric_amount_rejected(bad):
    with pytest.raises(ValidationError):
        validate_amount(bad)


@pytest.mark.parametrize("bad", ["-1", "-0.01", "nan", "inf", "-inf"])
def test_negative_or_non_finite_rejected(bad):
    with pytest.raises(ValidationError):
        validate_amount(bad)


@pytest.mark.parametrize("text,expected", [
    ("100", 100.0), (" 25.50 ", 25.5), ("0", 0.0), ("1,250.50", 1250.5), ("1,000,000", 1000000.0),
])
def test_valid_amounts(text, expected):
    assert validate_amount(text) == expected


def test_currency_normalised():
    assert validate_currency(" php ", SUPPORTED) == "PHP"


@pytest.mark.parametrize("bad", ["", None, "XYZ", "US"])
def test_bad_currency_rejected(bad):
    with pytest.raises(ValidationError):
        validate_currency(bad, SUPPORTED)


def test_conversion_ok():
    req = validate_conversion("10", "usd", "php", SUPPORTED)
    assert (req.amount, req.source, req.target) == (10.0, "USD", "PHP")


def test_conversion_without_rates_loaded():
    with pytest.raises(ValidationError) as exc:
        validate_conversion("10", "USD", "PHP", {})
    assert "Refresh" in str(exc.value)


def test_messages_are_plain_text():
    with pytest.raises(ValidationError) as exc:
        validate_amount("-5")
    assert str(exc.value) == "Amount cannot be negative."
