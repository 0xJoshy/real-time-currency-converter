import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

API_KEY_VAR = "EXCHANGE_RATE_API_KEY"


def get_api_key() -> str:
    """Return the ExchangeRate-API key from the environment."""
    api_key = os.getenv(API_KEY_VAR)
    if not api_key:
        raise ValueError(
            f"{API_KEY_VAR} is missing. Copy .env.example to .env and add your key."
        )
    return api_key
