"""ExchangeRate-API client (FR-07: meaningful errors)."""
from datetime import datetime

import requests

from models.rate_snapshot import RateSnapshot


class RateApiError(Exception):
    """Raised with a user-friendly message when a fetch fails."""


class ExchangeRateClient:
    BASE_URL = "https://v6.exchangerate-api.com/v6"

    def __init__(self, api_key: str, base: str = "USD", timeout: float = 10):
        self._api_key = api_key
        self._base = base
        self._timeout = timeout

    def fetch(self) -> RateSnapshot:
        # Never log or print this URL: it contains the API key.
        url = f"{self.BASE_URL}/{self._api_key}/latest/{self._base}"
        try:
            response = requests.get(url, timeout=self._timeout)
            data = response.json()
        except requests.Timeout:
            raise RateApiError("The request timed out. Please try again.")
        except requests.ConnectionError:
            raise RateApiError("No internet connection. Check your network.")
        except (requests.RequestException, ValueError):
            raise RateApiError("Could not read a valid response from the API.")

        if data.get("result") != "success":
            kind = data.get("error-type", "unknown-error")
            raise RateApiError(f"The API returned an error: {kind}")

        return RateSnapshot(
            base=data["base_code"],
            rates=data["conversion_rates"],
            fetched_at=datetime.now(),
        )
