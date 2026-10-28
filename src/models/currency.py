"""Input validation for the converter (FR-06).

No Tkinter and no network code here, so it can be tested without a window.
Every ValidationError message is plain text that is safe to show to the user.
"""

import math
import re
from dataclasses import dataclass

# Accepts 1000, 1,000, 1,250,000.50 but not 1,5 or 12,34,567
_THOUSANDS = re.compile(r"\d{1,3}(,\d{3})+(\.\d+)?")


class ValidationError(ValueError):
    """Raised when user input is not acceptable. str(error) is the message."""


@dataclass(frozen=True)
class ConversionRequest:
    amount: float
    source: str
    target: str


def validate_amount(text) -> float:
    """Return a non-negative, finite number or raise ValidationError."""
    cleaned = "" if text is None else str(text).strip()
    if not cleaned:
        raise ValidationError("Please enter an amount.")

    if "," in cleaned:
        if not _THOUSANDS.fullmatch(cleaned):
            raise ValidationError("Amount must be a number, for example 100 or 25.50.")
        cleaned = cleaned.replace(",", "")

    try:
        value = float(cleaned)
    except ValueError:
        raise ValidationError("Amount must be a number, for example 100 or 25.50.")

    if not math.isfinite(value):
        raise ValidationError("Amount must be a real number.")
    if value < 0:
        raise ValidationError("Amount cannot be negative.")
    return value


def validate_currency(code, supported) -> str:
    """Return an uppercase supported currency code or raise ValidationError."""
    cleaned = "" if code is None else str(code).strip().upper()
    if not cleaned:
        raise ValidationError("Please select a currency.")
    if cleaned not in supported:
        raise ValidationError(f"'{cleaned}' is not a supported currency.")
    return cleaned


def swap_currencies(source, target):
    """Return (target, source) so the Swap button can exchange the two (FR-09)."""
    return target, source


def validate_conversion(amount_text, source, target, supported) -> ConversionRequest:
    """Validate everything the Convert button needs in one call."""
    if not supported:
        raise ValidationError("Rates are not loaded yet. Click Refresh and try again.")
    amount = validate_amount(amount_text)
    return ConversionRequest(
        amount=amount,
        source=validate_currency(source, supported),
        target=validate_currency(target, supported),
    )
