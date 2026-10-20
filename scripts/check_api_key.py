import os
from pathlib import Path

import requests
from dotenv import load_dotenv

project_root = Path(__file__).resolve().parents[1]
load_dotenv(project_root / ".env")
api_key = os.getenv("EXCHANGE_RATE_API_KEY")
if not api_key:
    raise SystemExit(
        "EXCHANGE_RATE_API_KEY is missing. Copy .env.example to .env "
        "and add your API key."
    )

url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/USD/PHP/100"

try:
    response = requests.get(url, timeout=10)
    data = response.json()
except requests.RequestException:
    raise SystemExit("Could not reach the API. Check your internet connection.")

# Print only the response. Never print the URL: it contains your key.
print(data)