from abc import ABC, abstractmethod


class ConversionStrategy(ABC):
    """Base class: every conversion method implements convert()."""

    @abstractmethod
    def convert(self, amount: float, rate: float) -> float:
        """Return the converted amount for `amount` at `rate`."""


class DirectRateStrategy(ConversionStrategy):
    """Multiplies the amount by the live rate."""

    def convert(self, amount: float, rate: float) -> float:
        return amount * rate


class RoundedRateStrategy(ConversionStrategy):
    """Multiplies by the live rate, then rounds to 2 decimal places."""

    def convert(self, amount: float, rate: float) -> float:
        return round(amount * rate, 2)
