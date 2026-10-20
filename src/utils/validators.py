"""Input validation (FR-06)."""
import math


def parse_amount(text: str) -> float:
    """Return a non-negative finite float or raise ValueError with a clear message."""
    try:
        value = float(text.strip().replace(",", ""))
    except ValueError:
        raise ValueError("Amount must be a number, e.g. 100 or 25.50.")
    if math.isnan(value) or math.isinf(value):
        raise ValueError("Amount must be a real number.")
    if value < 0:
        raise ValueError("Amount cannot be negative.")
    return value


def parse_currency(text: str, supported) -> str:
    """Return an uppercase supported code or raise ValueError."""
    code = text.strip().upper()
    if code not in supported:
        raise ValueError(
            f"'{code or text}' is not a supported currency code. "
            "Choose option 4 to see the list."
        )
    return code
