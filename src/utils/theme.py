"""Look and feel: colours, fonts and small canvas-drawn widgets.

Tkinter cannot blur what is behind a window, so the "glass" look is faked:
a soft gradient backdrop with faint colour blobs, a frosted card with a white
edge and a layered shadow, and a pale title bar that reads as translucent.
"""

import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

# ---------- palette ----------
BG_TOP = "#EAF2FF"
BG_BOTTOM = "#D3E2FB"
BLOB_BLUE = "#BCD4FF"
BLOB_VIOLET = "#D8D2FF"
BAR_BG = "#F2F7FF"
BAR_LINE = "#D5E2F8"
WINDOW_EDGE = "#C6D6F2"

CARD = "#F9FBFF"
CARD_EDGE = "#FFFFFF"
SHADOW = "#7F9ACB"

FIELD_BG = "#FFFFFF"
FIELD_BORDER = "#DCE6F5"
RESULT_BG = "#EEF4FF"
RESULT_BORDER = "#D6E3FB"

TEXT = "#1B2433"
MUTED = "#64748B"
ACCENT = "#2563EB"
ACCENT_HOVER = "#1D55D0"
ACCENT_PRESS = "#1A4BB8"
ACCENT_SOFT = "#EAF1FF"
ERROR = "#D92D20"
OK = "#15803D"

# ---------- fonts ----------
_FAMILY = "TkDefaultFont"
_PREFERRED = (
    "Plus Jakarta Sans",
    "Segoe UI",
    "SF Pro Text",
    "Helvetica Neue",
    "DejaVu Sans",
)


def init_fonts(root: tk.Misc) -> None:
    """Pick the first installed font from the preferred list."""
    global _FAMILY
    available = set(tkfont.families(root))
    for name in _PREFERRED:
        if name in available:
            _FAMILY = name
            return


def font(size: int, weight: str = "normal"):
    return (_FAMILY, size, weight)


# ---------- drawing helpers ----------
def _rgb(hex_color: str):
    return tuple(int(hex_color[i : i + 2], 16) for i in (1, 3, 5))


def blend(a: str, b: str, t: float) -> str:
    """Colour t of the way from a to b (t in 0..1)."""
    mixed = (round(x + (y - x) * t) for x, y in zip(_rgb(a), _rgb(b)))
    return "#%02x%02x%02x" % tuple(mixed)


def rounded_rect(canvas: tk.Canvas, x1, y1, x2, y2, r, **kw) -> int:
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    pts = [
        x1 + r,
        y1,
        x1 + r,
        y1,
        x2 - r,
        y1,
        x2 - r,
        y1,
        x2,
        y1,
        x2,
        y1 + r,
        x2,
        y1 + r,
        x2,
        y2 - r,
        x2,
        y2 - r,
        x2,
        y2,
        x2 - r,
        y2,
        x2 - r,
        y2,
        x1 + r,
        y2,
        x1 + r,
        y2,
        x1,
        y2,
        x1,
        y2 - r,
        x1,
        y2 - r,
        x1,
        y1 + r,
        x1,
        y1 + r,
        x1,
        y1,
    ]
    return canvas.create_polygon(pts, smooth=True, **kw)


def backdrop_color(y: float, height: float) -> str:
    return blend(BG_TOP, BG_BOTTOM, min(max(y / max(height - 1, 1), 0), 1))


def _blob(canvas, cx, cy, radius, tint, height, strength=0.85, steps=26) -> None:
    """A soft radial glow made of concentric circles."""
    base = backdrop_color(cy, height)
    for i in range(steps):
        r = radius * (1 - i / steps)
        color = blend(base, tint, strength * (i / steps) ** 1.4)
        canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="")


def draw_backdrop(canvas: tk.Canvas, width: int, height: int) -> None:
    for y in range(height):
        canvas.create_line(0, y, width, y, fill=backdrop_color(y, height))
    _blob(canvas, width - 10, 90, 150, BLOB_BLUE, height)
    _blob(canvas, 20, height - 60, 160, BLOB_VIOLET, height)


def draw_card(canvas: tk.Canvas, x1, y1, x2, y2, height: int, radius=20) -> None:
    """Layered shadow, then a frosted card with a white edge."""
    bg = backdrop_color((y1 + y2) / 2, height)
    for i in range(8, 0, -1):
        rounded_rect(
            canvas,
            x1 - i,
            y1 - i + 6,
            x2 + i,
            y2 + i + 6,
            radius + i,
            fill=blend(bg, SHADOW, 0.022 * (9 - i)),
            outline="",
        )
    rounded_rect(canvas, x1, y1, x2, y2, radius, fill=CARD, outline=CARD_EDGE, width=2)


# ---------- widgets ----------
class RoundedPanel(tk.Canvas):
    """A rounded box. Put widgets in `.inner`. Used for fields and the result."""

    def __init__(
        self,
        parent,
        width,
        height,
        *,
        radius=12,
        fill=FIELD_BG,
        outline=FIELD_BORDER,
        pad=12,
        valign="center",
        canvas_bg=CARD,
    ):
        super().__init__(
            parent, width=width, height=height, bg=canvas_bg, highlightthickness=0, bd=0
        )
        self._width, self._radius, self._fill = width, radius, fill
        self._outline, self._pad = outline, pad
        self._shape = rounded_rect(
            self,
            1,
            1,
            width - 1,
            height - 1,
            radius,
            fill=fill,
            outline=outline,
            width=1,
        )
        self.inner = tk.Frame(self, bg=fill)
        if valign == "top":
            self.create_window(
                pad, pad - 2, window=self.inner, anchor="nw", width=width - 2 * pad
            )
        else:
            self.create_window(
                pad, height / 2, window=self.inner, anchor="w", width=width - 2 * pad
            )

    def set_focus(self, on: bool) -> None:
        self.itemconfigure(
            self._shape, outline=ACCENT if on else self._outline, width=2 if on else 1
        )

    def fit(self) -> None:
        """Resize to the natural height of the contents (top-aligned panels)."""
        self.update_idletasks()
        height = self.inner.winfo_reqheight() + 2 * self._pad - 2
        self.configure(height=height)
        self.delete(self._shape)
        self._shape = rounded_rect(
            self,
            1,
            1,
            self._width - 1,
            height - 1,
            self._radius,
            fill=self._fill,
            outline=self._outline,
            width=1,
        )
        self.tag_lower(self._shape)


class RoundedButton(tk.Canvas):
    STYLES = {
        "primary": dict(
            fill=ACCENT,
            hover=ACCENT_HOVER,
            press=ACCENT_PRESS,
            fg="#FFFFFF",
            outline=ACCENT,
        ),
        "secondary": dict(
            fill=FIELD_BG,
            hover=ACCENT_SOFT,
            press="#DCE8FF",
            fg=TEXT,
            outline=FIELD_BORDER,
        ),
    }

    def __init__(
        self,
        parent,
        text,
        command,
        width,
        height=44,
        radius=12,
        kind="primary",
        canvas_bg=CARD,
        font_size=10,
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=canvas_bg,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._s = self.STYLES[kind]
        self._command = command
        self._shape = rounded_rect(
            self,
            1,
            1,
            width - 1,
            height - 1,
            radius,
            fill=self._s["fill"],
            outline=self._s["outline"],
        )
        self.create_text(
            width / 2,
            height / 2,
            text=text,
            fill=self._s["fg"],
            font=font(font_size, "bold"),
        )
        self.bind("<Enter>", lambda _e: self._paint(self._s["hover"]))
        self.bind("<Leave>", lambda _e: self._paint(self._s["fill"]))
        self.bind("<ButtonPress-1>", lambda _e: self._paint(self._s["press"]))
        self.bind("<ButtonRelease-1>", self._on_release)

    def _paint(self, color: str) -> None:
        self.itemconfigure(self._shape, fill=color)

    def _on_release(self, event) -> None:
        inside = (
            0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()
        )
        self._paint(self._s["hover"] if inside else self._s["fill"])
        if inside:
            self._command()


def apply_ttk_style(root: tk.Tk) -> None:
    """Flat, borderless combobox that blends into its RoundedPanel."""
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(
        "Glass.TCombobox",
        fieldbackground=FIELD_BG,
        background=FIELD_BG,
        foreground=TEXT,
        arrowcolor=MUTED,
        bordercolor=FIELD_BG,
        lightcolor=FIELD_BG,
        darkcolor=FIELD_BG,
        borderwidth=0,
        relief="flat",
        padding=2,
        selectbackground=ACCENT_SOFT,
        selectforeground=TEXT,
    )
    style.map(
        "Glass.TCombobox",
        fieldbackground=[("readonly", FIELD_BG), ("focus", FIELD_BG)],
        background=[("active", ACCENT_SOFT), ("pressed", ACCENT_SOFT)],
        arrowcolor=[("active", ACCENT)],
        bordercolor=[("focus", FIELD_BG)],
        lightcolor=[("focus", FIELD_BG)],
        darkcolor=[("focus", FIELD_BG)],
        selectbackground=[("focus", ACCENT_SOFT)],
        selectforeground=[("focus", TEXT)],
    )
    # ---- dropdown list ----
    root.option_add("*TCombobox*Listbox.background", FIELD_BG)
    root.option_add("*TCombobox*Listbox.foreground", TEXT)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT_SOFT)
    root.option_add("*TCombobox*Listbox.selectForeground", ACCENT)
    root.option_add("*TCombobox*Listbox.borderWidth", 0)
    root.option_add("*TCombobox*Listbox.highlightThickness", 0)
    root.option_add("*TCombobox*Listbox.relief", "flat")
    root.option_add("*TCombobox*Listbox.activeStyle", "none")
    root.option_add("*TCombobox*Listbox.font", f"{{{_FAMILY}}} 10")

    # thin outline around the popup instead of the default black border
    style.configure(
        "ComboboxPopdownFrame",
        bordercolor=FIELD_BORDER,
        lightcolor=FIELD_BORDER,
        darkcolor=FIELD_BORDER,
        borderwidth=1,
        relief="flat",
    )

    # slim, arrow-less scrollbar with a soft rounded-looking thumb
    style.layout(
        "Vertical.TScrollbar",
        [
            (
                "Vertical.Scrollbar.trough",
                {
                    "sticky": "ns",
                    "children": [
                        ("Vertical.Scrollbar.thumb", {"expand": "1", "sticky": "nswe"})
                    ],
                },
            )
        ],
    )
    style.configure(
        "Vertical.TScrollbar",
        troughcolor=RESULT_BG,
        background="#C5D3EC",
        bordercolor=RESULT_BG,
        lightcolor="#C5D3EC",
        darkcolor="#C5D3EC",
        gripcount=0,
        arrowsize=10,
        width=10,
        relief="flat",
    )
    style.map(
        "Vertical.TScrollbar",
        background=[("active", "#A9BCE0"), ("pressed", "#8FA9D8")],
        lightcolor=[("active", "#A9BCE0"), ("pressed", "#8FA9D8")],
        darkcolor=[("active", "#A9BCE0"), ("pressed", "#8FA9D8")],
    )
