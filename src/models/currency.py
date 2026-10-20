"""Currency model and input validation (FR-06).

Every validator raises ValidationError with a message that is safe to show
directly to the user.
"""

import math
from dataclasses import dataclass
from typing import Iterable


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_amount(raw: object) -> float:
    """Return `raw` as a float, or raise ValidationError.

    Rejects empty, non-numeric, negative, NaN and infinite values.
    Zero is allowed.
    """
    if isinstance(raw, bool):
        raise ValidationError("Amount must be a number.")

    if isinstance(raw, str):
        text = raw.strip().replace(",", "")
        if not text:
            raise ValidationError("Amount is required.")
    else:
        text = raw

    try:
        amount = float(text)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        raise ValidationError(f"Amount must be a number, got {raw!r}.") from None

    if not math.isfinite(amount):
        raise ValidationError("Amount must be a finite number.")
    if amount < 0:
        raise ValidationError("Amount cannot be negative.")
    return amount


def validate_currency_code(raw: object, supported: Iterable[str]) -> str:
    """Return the normalized (upper-case) code, or raise ValidationError."""
    if not isinstance(raw, str) or not raw.strip():
        raise ValidationError("Currency code is required.")

    code = raw.strip().upper()
    supported_codes = {c.upper() for c in supported}
    if code not in supported_codes:
        raise ValidationError(f"Unsupported currency code: {code}.")
    return code


@dataclass(frozen=True)
class ConversionRequest:
    """A validated request to convert `amount` from `source` to `target`."""

    amount: float
    source: str
    target: str

    @classmethod
    def create(
        cls,
        amount: object,
        source: object,
        target: object,
        supported: Iterable[str],
    ) -> "ConversionRequest":
        """Validate raw user input and build a request.

        Raises ValidationError on the first invalid field.
        """
        supported = list(supported)
        return cls(
            amount=validate_amount(amount),
            source=validate_currency_code(source, supported),
            target=validate_currency_code(target, supported),
        )