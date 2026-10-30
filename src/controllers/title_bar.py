"""Custom title bar: logo tile, title, drag area, minimize and close."""

import tkinter as tk

from utils import theme


class _CaptionButton(tk.Label):
    def __init__(self, parent, text, command, hover_bg, hover_fg=theme.TEXT):
        super().__init__(
            parent,
            text=text,
            width=5,
            bg=theme.BAR_BG,
            fg=theme.MUTED,
            font=theme.font(10),
            cursor="hand2",
        )
        self._normal = (theme.BAR_BG, theme.MUTED)
        self._hover = (hover_bg, hover_fg)
        self.bind(
            "<Enter>", lambda _e: self.configure(bg=self._hover[0], fg=self._hover[1])
        )
        self.bind(
            "<Leave>", lambda _e: self.configure(bg=self._normal[0], fg=self._normal[1])
        )
        self.bind("<ButtonRelease-1>", lambda _e: command())


class TitleBar(tk.Frame):
    HEIGHT = 52

    def __init__(self, parent, root: tk.Tk, on_minimize):
        super().__init__(parent, bg=theme.BAR_BG, height=self.HEIGHT)
        self.root = root
        self.pack_propagate(False)

        logo = tk.Canvas(
            self, width=32, height=32, bg=theme.BAR_BG, highlightthickness=0
        )
        theme.rounded_rect(
            logo, 1, 1, 31, 31, 10, fill=theme.ACCENT_SOFT, outline="#D3E2FF"
        )
        logo.create_text(
            16, 16, text="\u21c4", fill=theme.ACCENT, font=theme.font(12, "bold")
        )
        logo.pack(side="left", padx=(16, 10))

        titles = tk.Frame(self, bg=theme.BAR_BG)
        titles.pack(side="left")
        title = tk.Label(
            titles,
            text="Currency Converter",
            bg=theme.BAR_BG,
            fg=theme.TEXT,
            font=theme.font(11, "bold"),
            anchor="w",
        )
        subtitle = tk.Label(
            titles,
            text="Real-time exchange rates",
            bg=theme.BAR_BG,
            fg=theme.MUTED,
            font=theme.font(8),
            anchor="w",
        )
        title.pack(fill="x")
        subtitle.pack(fill="x")

        _CaptionButton(self, "\u2715", self.root.destroy, "#E5484D", "#FFFFFF").pack(
            side="right", fill="y"
        )
        _CaptionButton(self, "\u2014", on_minimize, "#E3ECFB").pack(
            side="right", fill="y"
        )

        for widget in (self, logo, titles, title, subtitle):  # drag from anywhere blank
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._drag)

    def _start_drag(self, event) -> None:
        self._dx = event.x_root - self.root.winfo_x()
        self._dy = event.y_root - self.root.winfo_y()

    def _drag(self, event) -> None:
        self.root.geometry(f"+{event.x_root - self._dx}+{event.y_root - self._dy}")
