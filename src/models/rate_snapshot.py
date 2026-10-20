"""Immutable record of one successful rate fetch."""
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class RateSnapshot:
    """Rates against a fixed base currency, plus when they were fetched."""

    base: str
    rates: dict
    fetched_at: datetime

    def currencies(self) -> list:
        return sorted(self.rates)

    def supports(self, code: str) -> bool:
        return code in self.rates

    def rate(self, source: str, target: str) -> float:
        """Cross rate source -> target, derived from the base rates.

        One request for the base currency serves every pair, which keeps
        API usage low (see SRS section 8).
        """
        return self.rates[target] / self.rates[source]
