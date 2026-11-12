"""Shared Tkinter widgets for every screen of the GUI (owner: Lâm).

Use these instead of plain tk widgets so all screens look the same
(see docs/ui_guide.md). Colours and fonts come from theme.py.

A screen is a subclass of Page:

    from gui_widgets import Page, Panel, label, page_header

    class ForwardPage(Page):
        def __init__(self, parent, app):
            super().__init__(parent, app)
            page_header(self, "Title", "One line about the screen").pack(fill="x")
            ...

`app` gives: app.kb (KnowledgeBase), app.lang ("vi" / "en"), app.scenarios,
app.state (dict shared by all screens), app.show(key) to change screen.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path
from typing import Callable, Optional

import tkinter as tk
from tkinter import ttk

import theme
from kb import ROOT
from theme import COLORS as C
from theme import FONTS as F
from theme import SEVERITY_TEXT

K = 1.0  # screen scale (1.25 on a 125 % Windows display); set by App


def px(n: float) -> int:
    """Pixel size scaled to the screen, so the layout looks the same at 100 % and 150 %."""
    return int(round(n * K))


def data_root() -> Path:
    """Repository root, or the unpacked folder when running as a PyInstaller .exe."""
    return Path(getattr(sys, "_MEIPASS", ROOT))


def fold(text: str) -> str:
    """Lower case without Vietnamese accents, so "phanh" finds "Phanh" and "con" finds "còi"."""
    text = text.lower().replace("đ", "d")
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")



# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------

def label(parent, text="", font="body", fg="text", bg="surface", **kw) -> tk.Label:
    return tk.Label(parent, text=text, font=F[font], fg=C[fg], bg=C[bg], anchor="w", justify="left", **kw)


def autowrap(widget: tk.Label, pad: int = 4) -> tk.Label:
    """Wrap the label's text to its current width."""
    widget.bind("<Configure>", lambda e: widget.configure(wraplength=max(40, e.width - pad)), add="+")
    return widget


def round_rect(canvas: tk.Canvas, x1, y1, x2, y2, r, **kw):
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class CFBar(tk.Canvas):
    def __init__(self, parent, cf: float, bg="surface", height=8):
        super().__init__(parent, height=px(height), bg=C[bg], highlightthickness=0, bd=0, width=120)
        self.cf = cf
        self.bind("<Configure>", self._draw)

    def _draw(self, _=None):
        self.delete("all")
        w, h = self.winfo_width(), int(self["height"])
        round_rect(self, 0, 0, w, h, h / 2, fill=C["chrome"], outline="")
        if self.cf > 0:
            round_rect(self, 0, 0, max(h, w * min(1.0, self.cf)), h, h / 2, fill=C["accent"], outline="")


def chip(parent, text, fg, bg) -> tk.Label:
    return tk.Label(parent, text=text, font=F["small_bold"], fg=fg, bg=bg, padx=8, pady=1)


def severity_chip(parent, severity, lang) -> tk.Label:
    fg, bg = theme.severity_colors(severity)
    return chip(parent, SEVERITY_TEXT[lang].get(severity or "self", ""), fg, bg)


def dot(parent, color, bg="surface", size=8) -> tk.Canvas:
    size = px(size)
    c = tk.Canvas(parent, width=size, height=size, bg=C[bg], highlightthickness=0, bd=0)
    c.create_oval(0, 0, size - 1, size - 1, fill=color, outline=color)
    return c


def rank_badge(parent, n: int, top: bool) -> tk.Canvas:
    d = px(24)
    c = tk.Canvas(parent, width=d, height=d, bg=C["surface"], highlightthickness=0, bd=0)
    c.create_oval(1, 1, d - 1, d - 1, fill=C["accent"] if top else C["accent_soft"], outline="")
    c.create_text(d / 2, d / 2, text=str(n), font=F["small_bold"], fill=C["on_accent"] if top else C["accent"])
    return c


def link(parent, text, command, bg="surface", fg="accent", font="small_bold") -> tk.Label:
    lbl = tk.Label(parent, text=text, font=F[font], fg=C[fg], bg=C[bg], cursor="hand2", anchor="w",
                   justify="left")
    lbl.bind("<Button-1>", lambda e: command())
    lbl.bind("<Enter>", lambda e: lbl.configure(fg=C["accent_hover"]))
    lbl.bind("<Leave>", lambda e: lbl.configure(fg=C[fg]))
    return lbl


class ScrollFrame(tk.Frame):
    """A vertically scrolling frame. Put widgets in `.inner`."""

    def __init__(self, parent, bg="surface"):
        super().__init__(parent, bg=C[bg])
        self._scrollframe = True
        self.canvas = tk.Canvas(self, bg=C[bg], highlightthickness=0, bd=0, width=1, height=1)
        self.bar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=C[bg])
        self._win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=self._set)
        self.bar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self._win, width=e.width))

    def _set(self, lo, hi) -> None:
        """Show the scroll bar only when the content is taller than the frame."""
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            self.bar.pack_forget()
        elif not self.bar.winfo_ismapped():
            self.bar.pack(side="right", fill="y", before=self.canvas)
        self.bar.set(lo, hi)

    def wheel(self, delta: int) -> None:
        if self.inner.winfo_height() > self.canvas.winfo_height():
            self.canvas.yview_scroll(int(-delta / 120) or (-1 if delta > 0 else 1), "units")

    def to_top(self) -> None:
        self.canvas.yview_moveto(0)

    def clear(self) -> None:
        for w in self.inner.winfo_children():
            w.destroy()
        self.to_top()


class Panel(tk.Frame):
    """White box with a header (title + meta), a body and an optional footer."""

    def __init__(self, parent, title: str, meta: str = "", footer: bool = False):
        super().__init__(parent, bg=C["surface"], highlightthickness=1, highlightbackground=C["border"])
        head = tk.Frame(self, bg=C["surface"])
        head.pack(fill="x")
        self.title = label(head, title, "heading")
        self.title.pack(side="left", padx=(14, 8), pady=10)
        self.meta = label(head, meta, "small", "muted")
        self.meta.pack(side="right", padx=14)
        self.head = head
        tk.Frame(self, bg=C["border"], height=1).pack(fill="x")
        if footer:
            self.foot = tk.Frame(self, bg=C["surface"])
            self.foot.pack(side="bottom", fill="x")
            tk.Frame(self, bg=C["border"], height=1).pack(side="bottom", fill="x")
        self.body = tk.Frame(self, bg=C["surface"])
        self.body.pack(fill="both", expand=True)


class Segmented(tk.Frame):
    """Two or more options side by side, one selected."""

    def __init__(self, parent, options, value: str, command: Callable[[str], None], bg="surface"):
        super().__init__(parent, bg=C["chrome"], padx=3, pady=3)
        self.labels = {}
        self.command = command
        for key, text in options:
            lbl = tk.Label(self, text=text, font=F["small_bold"], padx=12, pady=3, cursor="hand2")
            lbl.pack(side="left", padx=1)
            lbl.bind("<Button-1>", lambda e, k=key: self.select(k, notify=True))
            self.labels[key] = lbl
        self.select(value)

    def select(self, key: str, notify: bool = False) -> None:
        self.value = key
        for k, lbl in self.labels.items():
            on = k == key
            lbl.configure(bg=C["surface"] if on else C["chrome"], fg=C["accent"] if on else C["muted"])
        if notify:
            self.command(key)


class HintEntry(ttk.Entry):
    """ttk.Entry that shows a grey hint while empty. Read the text with .value()."""

    def __init__(self, parent, hint: str, on_change: Optional[Callable[[], None]] = None):
        self.var = tk.StringVar()
        super().__init__(parent, textvariable=self.var)
        self.hint = hint
        self.showing = False
        self.bind("<FocusIn>", self._hide)
        self.bind("<FocusOut>", self._show)
        self._show()
        if on_change:
            self.var.trace_add("write", lambda *a: on_change())

    def _show(self, _=None):
        if not self.var.get():
            self.showing = True
            self.configure(foreground=C["muted"])
            self.var.set(self.hint)

    def _hide(self, _=None):
        if self.showing:
            self.showing = False
            self.var.set("")
            self.configure(foreground=C["text"])

    def value(self) -> str:
        return "" if self.showing else self.var.get()

    def clear(self) -> None:
        self._hide()
        if self.focus_get() is not self:
            self._show()


def page_header(parent, title: str, subtitle: str) -> tk.Frame:
    f = tk.Frame(parent, bg=C["bg"])
    label(f, title, "display", bg="bg").pack(anchor="w")
    tk.Frame(f, bg=C["highlight"], width=px(44), height=px(4)).pack(anchor="w", pady=(2, 4))
    autowrap(label(f, subtitle, "body", "muted", bg="bg")).pack(fill="x", pady=(2, 0))
    return f


def tile(parent, caption: str, value: str, note: str = "", color: str = "text") -> tk.Frame:
    f = tk.Frame(parent, bg=C["surface"], highlightthickness=1, highlightbackground=C["border"],
                 padx=16, pady=12)
    label(f, caption.upper(), "small_bold", "muted").pack(anchor="w")
    label(f, value, "display", color).pack(anchor="w")
    label(f, note or " ", "small", "muted").pack(anchor="w")
    return f


class Page(tk.Frame):
    def __init__(self, parent, app: "App"):
        super().__init__(parent, bg=C["bg"])
        self.app = app

    def on_show(self) -> None:
        pass
