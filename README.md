# Real-Time Currency Converter

A desktop application that converts currencies using real-time exchange rates.

## Features
- Convert between multiple currencies
- Fetch live exchange rates
- Simple desktop user interface
- Currency amount input and conversion result display

## Technologies Used
- Python
- Tkinter
- Exchange Rate API

## Run the API Key Check (Git Bash)

From the repository root, create and activate a virtual environment, install the dependencies, and create `.env` without overwriting an existing file:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

Open `.env`, replace `your_api_key_here` with your ExchangeRate-API key, then run:

```bash
python scripts/check_api_key.py
```

If the virtual environment already exists, skip the `python -m venv .venv` step. The check loads `.env` from the project root, so it also works when invoked from another working directory.
