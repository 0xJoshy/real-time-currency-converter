"""Tkinter window for the currency converter.

Validation (FR-06) and error handling (FR-07) live in models/currency.py and
services/; this file only shows their messages. Network calls run on a
background thread so the window never freezes. Colours and drawing helpers
live in utils/theme.py; the custom title bar is in controllers/title_bar.py.
"""

import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from dotenv import load_dotenv

from controllers.title_bar import TitleBar
from models.currency import ValidationError, swap_currencies, validate_conversion
from services.converter import ConverterService
from services.cooldown import Cooldown
from services.rate_client import ExchangeRateClient, RateApiError
from services.rate_service import RateService, RefreshResult
from services.strategy import RoundedRateStrategy
from utils import theme, window_chrome

AUTO_REFRESH_MS = 60 * 60 * 1000  # hourly = ~720 requests/month, under the free tier
MANUAL_COOLDOWN_S = 30  # FR-08
POLL_MS = 100
PLACEHOLDER = "\u2014"

# macOS can't give a frameless Tk window keyboard focus, so it keeps its native frame.
CUSTOM_TITLE_BAR = sys.platform != "darwin"

WINDOW_W = 420
CARD_MARGIN = 20
CARD_PAD = 20
BODY_W = WINDOW_W - 2 * CARD_MARGIN - 2 * CARD_PAD  # 340


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
        self.result_var = tk.StringVar(value=PLACEHOLDER)
        self.rate_var = tk.StringVar()
        self.updated_var = tk.StringVar(value="Rates last updated: not yet")
        self.status_var = tk.StringVar(value="Loading rates...")

        self._build()
        self.root.after(POLL_MS, self._poll_results)
        self._start_refresh()
        self.root.after(AUTO_REFRESH_MS, self._auto_refresh)

    # ---------- layout ----------
    def _build(self) -> None:
        root = self.root
        theme.init_fonts(root)
        theme.apply_ttk_style(root)
        root.title("Real-Time Currency Converter")
        root.resizable(False, False)

        bar_h = TitleBar.HEIGHT if CUSTOM_TITLE_BAR else 0
        canvas = tk.Canvas(
            root,
            width=WINDOW_W,
            height=100,
            highlightthickness=0,
            bd=0,
            bg=theme.BG_TOP,
        )
        canvas.pack(fill="both", expand=True)

        # Build the body first so the window can be sized to fit it exactly.
        self.body = tk.Frame(canvas, bg=theme.CARD)
        self._build_body(self.body)
        self.body.update_idletasks()

        card_top = bar_h + 16
        card_h = self.body.winfo_reqheight() + 2 * CARD_PAD
        height = card_top + card_h + 24
        canvas.configure(height=height)

        theme.draw_backdrop(canvas, WINDOW_W, height)
        theme.draw_card(
            canvas,
            CARD_MARGIN,
            card_top,
            WINDOW_W - CARD_MARGIN,
            card_top + card_h,
            height,
        )
        canvas.create_window(
            WINDOW_W / 2,
            card_top + CARD_PAD,
            window=self.body,
            anchor="n",
            width=BODY_W,
        )

        if CUSTOM_TITLE_BAR:
            canvas.create_line(0, bar_h, WINDOW_W, bar_h, fill=theme.BAR_LINE)
            canvas.create_window(
                0,
                0,
                window=TitleBar(canvas, root),
                anchor="nw",
                width=WINDOW_W,
                height=bar_h,
            )
            canvas.create_rectangle(
                0, 0, WINDOW_W - 1, height - 1, outline=theme.WINDOW_EDGE
            )

        x = (root.winfo_screenwidth() - WINDOW_W) // 2
        y = (root.winfo_screenheight() - height) // 3
        root.geometry(f"{WINDOW_W}x{height}+{x}+{y}")

        if CUSTOM_TITLE_BAR:
            root.overrideredirect(True)
            root.bind("<Map>", self._on_map)
            root.after(100, lambda: window_chrome.apply(root, refresh=True))
            root.after(250, self._grab_focus)
        self.amount_entry.focus_set()

    def _build_body(self, body: tk.Frame) -> None:
        def caption(parent, text):
            return tk.Label(
                parent,
                text=text,
                bg=theme.CARD,
                fg=theme.MUTED,
                font=theme.font(9, "bold"),
                anchor="w",
            )

        # Amount
        caption(body, "Amount").pack(fill="x")
        amount_panel = theme.RoundedPanel(body, BODY_W, 44)
        amount_panel.pack(pady=(4, 14))
        self.amount_entry = tk.Entry(
            amount_panel.inner,
            textvariable=self.amount_var,
            relief="flat",
            bd=0,
            bg=theme.FIELD_BG,
            fg=theme.TEXT,
            insertbackground=theme.ACCENT,
            selectbackground="#CFE0FF",
            selectforeground=theme.TEXT,
            highlightthickness=0,
            font=theme.font(12),
        )
        self.amount_entry.pack(fill="x")
        self.amount_entry.bind(
            "<Return>", lambda _e: self.on_convert()
        )  # Enter converts
        self._focus_ring(self.amount_entry, amount_panel)

        # From / Swap / To
        row = tk.Frame(body, bg=theme.CARD)
        row.pack(fill="x")
        caption(row, "From").grid(row=0, column=0, sticky="w")
        caption(row, "To").grid(row=0, column=2, sticky="w")
        # Typable on purpose: a typo like "XYZ" is caught by validation (FR-06).
        self.source_box = self._combo(row, self.source_var, column=0)
        self.target_box = self._combo(row, self.target_var, column=2)
        theme.RoundedButton(
            row, "\u21c4", self.on_swap, width=44, kind="secondary", font_size=14
        ).grid(row=1, column=1, padx=5, pady=(4, 0))

        # Buttons
        buttons = tk.Frame(body, bg=theme.CARD)
        buttons.pack(pady=16)
        theme.RoundedButton(buttons, "Convert", self.on_convert, width=166).pack(
            side="left", padx=(0, 8)
        )
        theme.RoundedButton(
            buttons, "Refresh", self.on_refresh, width=166, kind="secondary"
        ).pack(side="left")

        # Result
        panel = theme.RoundedPanel(
            body,
            BODY_W,
            140,
            radius=14,
            fill=theme.RESULT_BG,
            outline=theme.RESULT_BORDER,
            pad=16,
            valign="top",
        )
        panel.pack()
        inner, bg = panel.inner, theme.RESULT_BG
        tk.Label(
            inner,
            text="RESULT",
            bg=bg,
            fg=theme.ACCENT,
            anchor="w",
            font=theme.font(8, "bold"),
        ).pack(fill="x")
        tk.Label(
            inner,
            textvariable=self.result_var,
            bg=bg,
            fg=theme.TEXT,
            font=theme.font(15, "bold"),
            anchor="nw",
            justify="left",
            wraplength=BODY_W - 32,
            height=2,
        ).pack(fill="x", pady=(4, 2))
        tk.Label(
            inner,
            textvariable=self.rate_var,
            bg=bg,
            fg=theme.TEXT,
            font=theme.font(9),
            anchor="w",
        ).pack(fill="x")
        tk.Label(
            inner,
            textvariable=self.updated_var,
            bg=bg,
            fg=theme.MUTED,
            font=theme.font(8),
            anchor="w",
        ).pack(fill="x", pady=(6, 0))
        panel.fit()  # size the panel to its contents so nothing is cut off

        # Status: fixed height so a long error never resizes the window.
        status_frame = tk.Frame(body, bg=theme.CARD, width=BODY_W, height=48)
        status_frame.pack(pady=(10, 0))
        status_frame.pack_propagate(False)
        self.status_label = tk.Label(
            status_frame,
            textvariable=self.status_var,
            bg=theme.CARD,
            fg=theme.OK,
            font=theme.font(9),
            wraplength=BODY_W,
            justify="left",
            anchor="nw",
        )
        self.status_label.pack(fill="both", expand=True)

    def _combo(self, parent, variable, column) -> ttk.Combobox:
        panel = theme.RoundedPanel(parent, 143, 44, pad=6)
        panel.grid(row=1, column=column, pady=(4, 0))
        box = ttk.Combobox(
            panel.inner,
            textvariable=variable,
            width=8,
            style="Glass.TCombobox",
            font=theme.font(11),
        )
        box.pack(fill="x")
        box.bind("<<ComboboxSelected>>", lambda _e: box.selection_clear())
        self._focus_ring(box, panel)
        return box

    @staticmethod
    def _focus_ring(widget, panel) -> None:
        widget.bind("<FocusIn>", lambda _e: panel.set_focus(True), add="+")
        widget.bind("<FocusOut>", lambda _e: panel.set_focus(False), add="+")

    # ---------- frameless window helpers ----------
    def _on_map(self, event) -> None:
        """Restoring from minimize: take the OS frame off again."""
        if event.widget is self.root and not self.root.overrideredirect():

            def restore():
                self.root.overrideredirect(True)
                window_chrome.apply(self.root)

            self.root.after(10, restore)

    def _grab_focus(self) -> None:
        self.root.focus_force()
        self.amount_entry.focus_set()

    # ---------- status / result ----------
    def _set_status(self, message: str, error: bool = False) -> None:
        self.status_var.set(message)
        self.status_label.configure(fg=theme.ERROR if error else theme.OK)

    def _clear_result(self) -> None:
        self.result_var.set(PLACEHOLDER)
        self.rate_var.set("")

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
            self._clear_result()
            self._set_status(str(err), error=True)
            return

        rate = snapshot.rate(req.source, req.target)
        converted = self.converter.convert(req.amount, rate)
        self.result_var.set(
            f"{req.amount:,.2f} {req.source} = {converted:,.2f} {req.target}"
        )
        self.rate_var.set(f"1 {req.source} = {rate:.6f} {req.target}")
        self._set_status("")

    def on_swap(self) -> None:  # FR-09
        source, target = swap_currencies(self.source_var.get(), self.target_var.get())
        self.source_var.set(source)
        self.target_var.set(target)
        # The old result no longer matches the dropdowns, so clear it.
        self._clear_result()

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
        self._set_status("" if result.ok else result.message, error=not result.ok)
