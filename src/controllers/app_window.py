"""Tkinter window for the currency converter.

Validation (FR-06) and error handling (FR-07) live in models/currency.py and
services/; this file only shows their messages. Network calls run on a
background thread so the window never freezes.

Look and feel comes from sv_ttk (Sun Valley theme). Colors and fonts that the
theme does not provide are set in _apply_styles(), which must run again after
every theme switch because ttk styles belong to the active theme.
"""

import os
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import font as tkfont
from tkinter import ttk

import sv_ttk
from dotenv import load_dotenv

from models.currency import ValidationError, swap_currencies, validate_conversion
from services.converter import ConverterService
from services.cooldown import Cooldown
from services.rate_client import ExchangeRateClient, RateApiError
from services.rate_service import RateService, RefreshResult
from services.strategy import RoundedRateStrategy

AUTO_REFRESH_MS = 60 * 60 * 1000  # hourly = ~720 requests/month, under the free tier
MANUAL_COOLDOWN_S = 30  # FR-08
POLL_MS = 100

DEFAULT_THEME = "dark"
PALETTE = {
    "dark": {"ok": "#6fcf97", "error": "#ff6b6b", "muted": "#a6a6a6"},
    "light": {"ok": "#1b5e20", "error": "#b00020", "muted": "#5f5f5f"},
}


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
        self._cooldown = Cooldown(MANUAL_COOLDOWN_S)

        self.amount_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.target_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.rate_var = tk.StringVar()
        self.updated_var = tk.StringVar(value="Rates last updated: not yet")
        self.status_var = tk.StringVar(value="Loading rates...")
        self.dark_var = tk.BooleanVar(value=DEFAULT_THEME == "dark")

        sv_ttk.set_theme(DEFAULT_THEME)
        self._make_fonts()
        self._build()
        self.root.after(POLL_MS, self._poll_results)
        self._start_refresh()
        self.root.after(AUTO_REFRESH_MS, self._auto_refresh)

    # ---------- theme ----------
    def _make_fonts(self) -> None:
        """Bigger fonts derived from the default one, so they match the platform."""
        base = tkfont.nametofont("TkDefaultFont")
        size = abs(int(base.cget("size")))
        self._title_font = base.copy()
        self._title_font.configure(size=size + 5, weight="bold")
        self._result_font = base.copy()
        self._result_font.configure(size=size + 9, weight="bold")

    def _theme_name(self) -> str:
        return "dark" if self.dark_var.get() else "light"

    def _apply_styles(self) -> None:
        colors = PALETTE[self._theme_name()]
        style = ttk.Style()
        style.configure("Title.TLabel", font=self._title_font)
        style.configure("Result.TLabel", font=self._result_font)
        style.configure("Muted.TLabel", foreground=colors["muted"])
        style.configure("Ok.TLabel", foreground=colors["ok"])
        style.configure("Error.TLabel", foreground=colors["error"])

    def on_toggle_theme(self) -> None:
        sv_ttk.set_theme(self._theme_name())
        self._apply_styles()

    # ---------- layout ----------
    def _build(self) -> None:
        self.root.title("Real-Time Currency Converter")
        self.root.resizable(False, False)
        self._apply_styles()

        frame = ttk.Frame(self.root, padding=24)
        frame.pack(fill="both", expand=True)
        frame.columnconfigure(0, weight=1, uniform="currency")
        frame.columnconfigure(2, weight=1, uniform="currency")

        # Header: title on the left, theme switch on the right.
        ttk.Label(frame, text="Currency Converter", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Checkbutton(
            frame,
            text="Dark",
            style="Switch.TCheckbutton",
            variable=self.dark_var,
            command=self.on_toggle_theme,
        ).grid(row=0, column=2, sticky="e")

        ttk.Label(frame, text="Amount").grid(row=1, column=0, sticky="w", pady=(20, 4))
        self.amount_entry = ttk.Entry(frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=2, column=0, columnspan=3, sticky="we")
        self.amount_entry.bind(
            "<Return>", lambda _e: self.on_convert()
        )  # Enter converts
        self.amount_entry.focus()

        ttk.Label(frame, text="From").grid(row=3, column=0, sticky="w", pady=(16, 4))
        ttk.Label(frame, text="To").grid(row=3, column=2, sticky="w", pady=(16, 4))
        # Typable on purpose: a typo like "XYZ" is caught by validation (FR-06).
        self.source_box = ttk.Combobox(frame, textvariable=self.source_var, width=10)
        self.target_box = ttk.Combobox(frame, textvariable=self.target_var, width=10)
        self.source_box.grid(row=4, column=0, sticky="we")
        ttk.Button(frame, text="\u21c4 Swap", command=self.on_swap).grid(
            row=4, column=1, padx=8
        )
        self.target_box.grid(row=4, column=2, sticky="we")

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=3, sticky="we", pady=(20, 0))
        buttons.columnconfigure((0, 1), weight=1, uniform="buttons")
        ttk.Button(
            buttons, text="Convert", style="Accent.TButton", command=self.on_convert
        ).grid(row=0, column=0, sticky="we", padx=(0, 4))
        ttk.Button(buttons, text="Refresh", command=self.on_refresh).grid(
            row=0, column=1, sticky="we", padx=(4, 0)
        )

        # Result "card": converted amount, rate used (FR-02), last updated (FR-03).
        card = ttk.LabelFrame(frame, text="Result", padding=16)
        card.grid(row=6, column=0, columnspan=3, sticky="we", pady=(20, 0))
        card.columnconfigure(0, weight=1)
        ttk.Label(
            card, textvariable=self.result_var, style="Result.TLabel", wraplength=340
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(card, textvariable=self.rate_var).grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )
        ttk.Label(card, textvariable=self.updated_var, style="Muted.TLabel").grid(
            row=2, column=0, sticky="w", pady=(10, 0)
        )

        self.status_label = ttk.Label(
            frame,
            textvariable=self.status_var,
            style="Ok.TLabel",
            wraplength=360,
            justify="left",
        )
        self.status_label.grid(row=7, column=0, columnspan=3, sticky="w", pady=(14, 0))

    def _set_status(self, message: str, error: bool = False) -> None:
        self.status_var.set(message)
        self.status_label.configure(style="Error.TLabel" if error else "Ok.TLabel")

    # ---------- convert (FR-01, FR-02, FR-06) ----------
    def on_convert(self) -> None:
        snapshot = self.service.snapshot
        try:
            req = validate_conversion(
                self.amount_var.get(),
                self.source_var.get(),
                self.target_var.get(),
                snapshot.currencies() if snapshot else [],
            )
        except ValidationError as err:
            self.result_var.set("")
            self.rate_var.set("")
            self._set_status(str(err), error=True)
            return

        rate = snapshot.rate(req.source, req.target)
        converted = self.converter.convert(req.amount, rate)
        self.result_var.set(
            f"{req.amount:,.2f} {req.source} = {converted:,.2f} {req.target}"
        )
        self.rate_var.set(f"1 {req.source} = {rate:.6f} {req.target}")
        self._set_status("Converted.")

    def on_swap(self) -> None:  # FR-09
        source, target = swap_currencies(self.source_var.get(), self.target_var.get())
        self.source_var.set(source)
        self.target_var.set(target)
        # The old result no longer matches the dropdowns, so clear it.
        self.result_var.set("")
        self.rate_var.set("")

    # ---------- refresh (FR-04, FR-07, FR-08) ----------
    def on_refresh(self) -> None:
        wait = self._cooldown.remaining()
        if wait > 0:
            self._set_status(
                f"Please wait {wait} more second(s) before refreshing again.",
                error=True,
            )
            return
        if self._start_refresh():
            self._cooldown.start()
        else:
            self._set_status("Rates are already being updated. Please wait.")

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
            result = RefreshResult(
                False, "Something went wrong while updating the rates."
            )
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
            self.updated_var.set(
                f"Rates last updated: {snapshot.fetched_at:%Y-%m-%d %H:%M:%S}"
            )
        self._set_status(result.message, error=not result.ok)
