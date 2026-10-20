import requests

from config import get_api_key

BASE_URL = "https://v6.exchangerate-api.com/v6"
TIMEOUT_SECONDS = 10


def get_rate(base_code: str, target_code: str) -> float:
    """Return the conversion rate from base_code to target_code."""
    url = f"{BASE_URL}/{get_api_key()}/pair/{base_code}/{target_code}"
    response = requests.get(url, timeout=TIMEOUT_SECONDS)
    data = response.json()
    if data.get("result") != "success":
        raise RuntimeError(data.get("error-type", "unknown-error"))
    return float(data["conversion_rate"])
