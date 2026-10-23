"""Immutable record of one successful rate fetch."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RateSnapshot:
    base: str
    rates: dict
    fetched_at: datetime

    def currencies(self) -> list:
        return sorted(self.rates)

    def rate(self, source: str, target: str) -> float:
        """Cross rate source -> target, derived from the base-currency rates."""
        return self.rates[target] / self.rates[source]
