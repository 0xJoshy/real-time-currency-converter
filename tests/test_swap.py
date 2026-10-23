from models.currency import swap_currencies


def test_swap_exchanges_codes():
    assert swap_currencies("USD", "PHP") == ("PHP", "USD")


def test_swap_twice_restores_original():
    assert swap_currencies(*swap_currencies("USD", "PHP")) == ("USD", "PHP")


def test_swap_with_empty_value():
    assert swap_currencies("", "PHP") == ("PHP", "")


def test_swap_same_currency():
    assert swap_currencies("EUR", "EUR") == ("EUR", "EUR")
