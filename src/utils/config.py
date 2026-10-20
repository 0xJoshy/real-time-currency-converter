"""Loads settings from .env / environment (never hardcode the key)."""
import os
from pathlib import Path

from dotenv import load_dotenv

# ExchangeRate-API free tier: ~1,500 requests/month and data that updates
# about once a day. Refreshing more often than hourly gains nothing.
MIN_REFRESH_MINUTES = 60
DEFAULT_REFRESH_MINUTES = 360  # ~4 calls/day, ~120/month
BASE_CURRENCY = "USD"


def load_settings() -> dict:
    root = Path(__file__).resolve().parents[2]
    load_dotenv(root / ".env")

    api_key = os.getenv("EXCHANGE_RATE_API_KEY")
    if not api_key:
        raise SystemExit(
            "EXCHANGE_RATE_API_KEY is missing. Copy .env.example to .env "
            "and add your API key."
        )

    try:
        minutes = float(os.getenv("REFRESH_INTERVAL_MINUTES", DEFAULT_REFRESH_MINUTES))
    except ValueError:
        minutes = DEFAULT_REFRESH_MINUTES
    minutes = max(minutes, MIN_REFRESH_MINUTES)  # protect the quota

    return {"api_key": api_key, "refresh_minutes": minutes, "base": BASE_CURRENCY}
