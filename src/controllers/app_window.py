"""Tkinter window for the currency converter.

Validation (FR-06) and error handling (FR-07) live in models/currency.py and
services/; this file only shows their messages. Network calls run on a
background thread so the window never freezes.
"""

import os
import queue
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from dotenv import load_dotenv

from models.currency import ValidationError, validate_conversion
from services.converter import ConverterService
from services.rate_client import ExchangeRateClient, RateApiError
from services.rate_service import RateService, RefreshResult
from services.strategy import RoundedRateStrategy

AUTO_REFRESH_MS = 60 * 60 * 1000   # hourly = ~720 requests/month, under the free tier
MANUAL_COOLDOWN_S = 30             # FR-08
POLL_MS = 100
ERROR_COLOR = "#b00020"
OK_COLOR = "#1b5e20"


def _make_fetch():
    """Build the fetch function. A missing key becomes a message, not a crash."""
    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")
    api_key = os.getenv("EXCHANGE_RATE_API_KEY")

    def fetch():
        if not api_key:
            raise RateApiError(
                "EXCHANGE_RATE_API_KEY is missing. Copy .env.example to .env "
                "and add your API key."
            )
        return ExchangeRateClient(api_key).fetch()

    return fetch


class AppWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.service = RateService(_make_fetch())
        self.converter = ConverterService(RoundedRateStrategy())
        self._results = queue.Queue()
        self._refreshing = False
        self._next_manual_ok = 0.0

        self.amount_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.rate_var = tk.StringVar()
        self.updated_var = tk.StringVar(value="Rates last updated: not yet")
        self.status_var = tk.StringVar(value="Loading rates...")

        self._build()
        self.root.after(POLL_MS, self._poll_results)
        self._start_refresh()
        self.root.after(AUTO_REFRESH_MS, self._auto_refresh)

    # ---------- layout ----------
    def _build(self) -> None:
        self.root.title("Real-Time Currency Converter")
        self.root.resizable(False, False)
        frame = ttk.Frame(self.root, padding=16)
        frame.grid()

        ttk.Label(frame, text="Amount").grid(row=0, column=0, sticky="w")
        self.amount_entry = ttk.Entry(frame, textvariable=self.amount_var, width=20)
        self.amount_entry.grid(row=1, column=0, columnspan=3, sticky="we", pady=(0, 8))
        self.amount_entry.bind("<Return>", lambda _e: self.on_convert())  # Enter converts
        self.amount_entry.focus()

        ttk.Label(frame, text="From").grid(row=2, column=0, sticky="w")
        ttk.Label(frame, text="To").grid(row=2, column=2, sticky="w")
        # Typable on purpose: a typo like "XYZ" is caught by validation (FR-06).
        self.source_box = ttk.Combobox(frame, textvariable=self.source_var, width=8)
        self.target_box = ttk.Combobox(frame, textvariable=self.target_var, width=8)
        self.source_box.grid(row=3, column=0, sticky="we")
        ttk.Button(frame, text="Swap", width=6, command=self.on_swap).grid(
            row=3, column=1, padx=6)
        self.target_box.grid(row=3, column=2, sticky="we")

        buttons = ttk.Frame(frame)
        buttons.grid(row=4, column=0, columnspan=3, pady=12)
        ttk.Button(buttons, text="Convert", command=self.on_convert).pack(side="left", padx=4)
        ttk.Button(buttons, text="Refresh", command=self.on_refresh).pack(side="left", padx=4)

        ttk.Label(frame, textvariable=self.result_var,
                  font=("TkDefaultFont", 12, "bold")).grid(row=5, column=0, columnspan=3, sticky="w")
        ttk.Label(frame, textvariable=self.rate_var).grid(row=6, column=0, columnspan=3, sticky="w")
        ttk.Label(frame, textvariable=self.updated_var).grid(row=7, column=0, columnspan=3, sticky="w")
        self.status_label = ttk.Label(frame, textvariable=self.status_var,
                                      wraplength=320, justify="left")
        self.status_label.grid(row=8, column=0, columnspan=3, sticky="w", pady=(8, 0))

    def _set_status(self, message: str, error: bool = False) -> None:
        self.status_var.set(message)
        self.status_label.configure(foreground=ERROR_COLOR if error else OK_COLOR)

    # ---------- convert (FR-01, FR-02, FR-06) ----------
    def on_convert(self) -> None:
        snapshot = self.service.snapshot
        try:
            req = validate_conversion(
                self.amount_var.get(), self.source_var.get(), self.target_var.get(),
                snapshot.currencies() if snapshot else [],
            )
        except ValidationError as err:
            self.result_var.set("")
            self.rate_var.set("")
            self._set_status(str(err), error=True)
            return

        rate = snapshot.rate(req.source, req.target)
        converted = self.converter.convert(req.amount, rate)
        self.result_var.set(f"{req.amount:,.2f} {req.source} = {converted:,.2f} {req.target}")
        self.rate_var.set(f"1 {req.source} = {rate:.6f} {req.target}")
        self._set_status("Converted.")

    def on_swap(self) -> None:  # FR-09
        src, tgt = self.source_var.get(), self.target_var.get()
        self.source_var.set(tgt)
        self.target_var.set(src)

    # ---------- refresh (FR-04, FR-07, FR-08) ----------
    def on_refresh(self) -> None:
        wait = self._next_manual_ok - time.monotonic()
        if wait > 0:
            self._set_status(
                f"Please wait {int(wait) + 1} more second(s) before refreshing again.",
                error=True)
            return
        if self._start_refresh():
            self._next_manual_ok = time.monotonic() + MANUAL_COOLDOWN_S

    def _auto_refresh(self) -> None:
        self._start_refresh()
        self.root.after(AUTO_REFRESH_MS, self._auto_refresh)

    def _start_refresh(self) -> bool:
        """Fetch on a background thread. Returns False if one is already running."""
        if self._refreshing:
            return False
        self._refreshing = True
        self._set_status("Updating rates...")
        threading.Thread(target=self._worker, daemon=True).start()
        return True

    def _worker(self) -> None:
        try:
            result = self.service.refresh()  # never raises
        except Exception:
            result = RefreshResult(False, "Something went wrong while updating the rates.")
        self._results.put(result)

    def _poll_results(self) -> None:
        """Runs on the Tk thread; the only place the UI is touched after a fetch."""
        try:
            while True:
                self._on_refresh_done(self._results.get_nowait())
        except queue.Empty:
            pass
        self.root.after(POLL_MS, self._poll_results)

    def _on_refresh_done(self, result: RefreshResult) -> None:
        self._refreshing = False
        snapshot = self.service.snapshot
        if snapshot is not None:  # keep showing the last good rates on failure
            codes = snapshot.currencies()
            self.source_box["values"] = codes
            self.target_box["values"] = codes
            if not self.source_var.get() and "USD" in codes:
                self.source_var.set("USD")
            if not self.target_var.get() and "PHP" in codes:
                self.target_var.set("PHP")
            self.updated_var.set(f"Rates last updated: {snapshot.fetched_at:%Y-%m-%d %H:%M:%S}")
        self._set_status(result.message, error=not result.ok)
