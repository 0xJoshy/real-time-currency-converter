import pytest
from utils.validators import parse_amount, parse_currency


@pytest.mark.parametrize("bad", ["abc", "-5", "nan", "inf", ""])
def test_bad_amounts(bad):
    with pytest.raises(ValueError):
        parse_amount(bad)


def test_good_amount():
    assert parse_amount("1,250.50") == 1250.5


def test_currency():
    assert parse_currency(" php ", {"PHP": 1}) == "PHP"
    with pytest.raises(ValueError):
        parse_currency("XYZ", {"PHP": 1})
