"""ExchangeRate-API client (FR-07: plain messages for network and API errors).

Messages never include the request URL or exception text, because the URL
contains the API key.
"""

from datetime import datetime

import requests

from models.rate_snapshot import RateSnapshot

API_ERROR_MESSAGES = {
    "invalid-key": "The API key is invalid. Check EXCHANGE_RATE_API_KEY in your .env file.",
    "inactive-account": "The API account is not active. Confirm your email with ExchangeRate-API.",
    "quota-reached": "The API request limit has been reached. Try again later.",
    "malformed-request": "The request to the rate service was not valid.",
    "unsupported-code": "A currency code is not supported by the rate service.",
    "unknown-code": "A currency code is not supported by the rate service.",
}
DEFAULT_API_ERROR = "The rate service returned an error. Please try again later."


class RateApiError(Exception):
    """A failed fetch. str(error) is a plain message safe to show to the user."""


class ExchangeRateClient:
    BASE_URL = "https://v6.exchangerate-api.com/v6"

    def __init__(self, api_key: str, base: str = "USD", timeout: float = 10):
        self._api_key = api_key
        self._base = base
        self._timeout = timeout

    def fetch(self) -> RateSnapshot:
        url = f"{self.BASE_URL}/{self._api_key}/latest/{self._base}"
        try:
            response = requests.get(url, timeout=self._timeout)
        except requests.Timeout:
            raise RateApiError("The request timed out. Please try again.")
        except requests.ConnectionError:
            raise RateApiError(
                "No internet connection. Check your network and try again."
            )
        except requests.RequestException:
            raise RateApiError("Could not reach the rate service. Please try again.")

        try:
            data = response.json()
        except ValueError:
            if response.status_code >= 500:
                raise RateApiError("The rate service is temporarily unavailable.")
            raise RateApiError(
                "The rate service sent a response that could not be read."
            )

        if not isinstance(data, dict):
            raise RateApiError(
                "The rate service sent a response that could not be read."
            )

        if data.get("result") != "success":
            kind = data.get("error-type")
            raise RateApiError(API_ERROR_MESSAGES.get(kind, DEFAULT_API_ERROR))

        raw = data.get("conversion_rates")
        if not isinstance(raw, dict):
            raise RateApiError("The rate service sent incomplete data.")
        rates = {
            code: float(rate)
            for code, rate in raw.items()
            if isinstance(rate, (int, float))
            and not isinstance(rate, bool)
            and rate > 0
        }
        if not rates:
            raise RateApiError("The rate service sent incomplete data.")

        return RateSnapshot(
            base=data.get("base_code", self._base),
            rates=rates,
            fetched_at=datetime.now(),
        )
