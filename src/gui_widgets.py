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


# ---------------------------------------------------------------------------
# MotoLogic components (owner: Giang; spec: docs/design/motologic_spec.md, section 2)
# Tk has no rounded frames, so each one is a Canvas that draws round_rect and holds a Frame.
# ---------------------------------------------------------------------------

def bind_tree(widget, sequence: str, func) -> None:
    """Bind an event on a widget and every widget inside it (a click anywhere on a card)."""
    widget.bind(sequence, func, add="+")
    for child in widget.winfo_children():
        bind_tree(child, sequence, func)


def eyebrow(parent, text: str, bg: str = "bg", fg: str = "accent") -> tk.Frame:
    """Small capital label with a dot in front, above a screen or panel title."""
    f = tk.Frame(parent, bg=C[bg])
    dot(f, C[fg], bg=bg, size=6).pack(side="left", padx=(0, px(8)))
    label(f, text.upper(), "eyebrow", fg, bg=bg).pack(side="left")
    return f


class RoundCard(tk.Canvas):
    """Rounded card. Put widgets in `.body` (background C[fill]).

    The height follows the content, unless grow=True: then the card fills the height
    its parent gives it (a right-hand panel as tall as the card next to it).
    """

    def __init__(self, parent, fill: str = "surface", border: Optional[str] = "border", radius: int = 18,
                 bg: str = "bg", pad: int = 22, grow: bool = False):
        super().__init__(parent, bg=C[bg], highlightthickness=0, bd=0, height=px(40), width=px(40))
        self.fill, self.border, self.radius, self.pad, self.grow = fill, border, px(radius), px(pad), grow
        self.body = tk.Frame(self, bg=C[fill])
        self._win = self.create_window(self.pad, self.pad, window=self.body, anchor="nw")
        self.bind("<Configure>", self._draw)
        self.body.bind("<Configure>", self._fit)
        self._job = None
        if grow:  # the body height is fixed, so labels that wrap later never fire body <Configure>
            self.bind("<Destroy>", lambda e: e.widget is self and self._job and self.after_cancel(self._job))

    def _refit(self) -> None:
        self._job = None
        self._fit()

    def _fit(self, _=None) -> None:
        # request the height of the content; a grow card may still be stretched taller by its parent
        h = self.body.winfo_reqheight() + 2 * self.pad
        if abs(int(self.cget("height")) - h) > 1:
            self.configure(height=h)

    def _draw(self, _=None) -> None:
        w, h = self.winfo_width(), self.winfo_height()
        self.delete("card")
        outline = C[self.border] if self.border else C[self.fill]
        round_rect(self, 1, 1, w - 1, h - 1, self.radius, fill=C[self.fill], outline=outline, tags="card")
        self.tag_lower("card")
        self.itemconfigure(self._win, width=max(1, w - 2 * self.pad))
        if self.grow:
            self.itemconfigure(self._win, height=max(1, h - 2 * self.pad))
            if self._job:
                self.after_cancel(self._job)
            self._job = self.after(60, self._refit)


class PillButton(tk.Canvas):
    """Rounded button. style "dark": panel colour with a lime arrow box; "lime"; "outline"."""

    STYLES = {"dark": ("panel", "on_panel", "accent"), "lime": ("lime", "on_lime", "highlight"),
              "outline": ("surface", "accent", "chrome")}

    def __init__(self, parent, text: str, command: Callable[[], None], style: str = "dark", bg: str = "bg",
                 arrow: bool = True, height: int = 48, width: int = 0):
        import tkinter.font as tkfont
        font = (theme.UI_FONT, 11, "bold")
        h = px(height)
        box = h - px(16) if arrow else 0
        w = max(px(width), tkfont.Font(font=font).measure(text) + px(48) + (box + px(12) if arrow else 0))
        super().__init__(parent, width=w, height=h, bg=C[bg], highlightthickness=0, bd=0, cursor="hand2")
        self.command, self.enabled = command, True
        self.colors = self.STYLES[style]
        fill, fg, _ = self.colors
        self._bg = round_rect(self, 1, 1, w - 1, h - 1, px(14), fill=C[fill],
                              outline=C["border"] if style == "outline" else C[fill])
        self._text = self.create_text(px(24), h / 2, text=text, anchor="w", font=font, fill=C[fg])
        if arrow:
            x0 = w - px(8) - box
            round_rect(self, x0, px(8), x0 + box, px(8) + box, px(9), fill=C["lime"], outline="")
            self.create_text(x0 + box / 2, h / 2, text="→", font=(theme.UI_FONT, 12, "bold"), fill=C["on_lime"])
        self.bind("<Button-1>", lambda e: self.enabled and self.command())
        self.bind("<Enter>", lambda e: self.enabled and self.itemconfigure(self._bg, fill=C[self.colors[2]]))
        self.bind("<Leave>", lambda e: self.itemconfigure(
            self._bg, fill=C[self.colors[0]] if self.enabled else C["chrome"]))

    def set_enabled(self, on: bool) -> None:
        self.enabled = on
        self.configure(cursor="hand2" if on else "arrow")
        self.itemconfigure(self._bg, fill=C[self.colors[0]] if on else C["chrome"])
        self.itemconfigure(self._text, fill=C[self.colors[1]] if on else C["muted"])


class Stepper(tk.Frame):
    """The 3 steps at the top of the diagnosis screen: done ✓, current (lime), still to do."""

    def __init__(self, parent, steps, current: int, bg: str = "bg"):
        super().__init__(parent, bg=C[bg])
        d = px(30)
        for i, text in enumerate(steps, 1):
            self.columnconfigure(i - 1, weight=1, uniform="step")
            col = tk.Frame(self, bg=C[bg])
            col.grid(row=0, column=i - 1, sticky="we", padx=(0 if i == 1 else px(10), 0))
            row = tk.Frame(col, bg=C[bg])
            row.pack(fill="x", pady=(0, px(10)))
            c = tk.Canvas(row, width=d, height=d, bg=C[bg], highlightthickness=0, bd=0)
            done, now = i < current, i == current
            c.create_oval(1, 1, d - 1, d - 1, outline="",
                          fill=C["lime"] if now else C["accent_soft"] if done else C["chrome"])
            c.create_text(d / 2, d / 2, text="✓" if done else f"{i:02d}", font=F["small_bold"],
                          fill=C["accent"] if done else C["on_lime"] if now else C["muted"])
            c.pack(side="left")
            label(row, text, "heading" if now else "body",  # the circle already shows ✓ for a done step
                  "text" if now else "muted", bg=bg).pack(side="left", padx=(px(10), 0))
            tk.Frame(col, bg=C["accent"] if i <= current else C["border"], height=px(2)).pack(fill="x")


def radio_mark(parent, on: bool, bg: str, size: int = 16, dark: bool = False) -> tk.Canvas:
    d = px(size)
    c = tk.Canvas(parent, width=d, height=d, bg=C[bg], highlightthickness=0, bd=0)
    if on:
        c.create_oval(2, 2, d - 2, d - 2, fill=C["lime"] if dark else C["accent"], outline="")
    else:
        c.create_oval(2, 2, d - 2, d - 2, outline=C["muted"], width=max(1, px(1.5)))
    return c


class ChoiceCard(RoundCard):
    """Card with a radio mark: vehicle type, diagnosis method. Selected = lime_soft with accent border."""

    def __init__(self, parent, title: str, subtitle: str, selected: bool, command: Callable[[], None],
                 note: str = "", badge: str = "", icon_name: str = "", bg: str = "surface", radio: bool = True):
        fill = "lime_soft" if selected else "surface"
        super().__init__(parent, fill=fill, border="accent" if selected else "border", radius=14, bg=bg, pad=16)
        b = self.body
        b.columnconfigure(2, weight=1)
        if radio:  # off for one-click choices (nothing stays selected)
            radio_mark(b, selected, fill).grid(row=0, column=0, rowspan=3, sticky="n", padx=(0, px(12)), pady=px(4))
        if icon_name:
            icon(b, icon_name, 34, "accent", fill).grid(row=0, column=1, rowspan=3, sticky="n", padx=(0, px(12)))
        head = tk.Frame(b, bg=C[fill])
        head.grid(row=0, column=2, sticky="we")
        if badge:  # own line: beside the title it squeezed "questions" into "questio/ns" in a small window
            chip(head, badge, C["on_lime"], C["lime"]).pack(side="top", anchor="w", pady=(0, px(6)))
        autowrap(label(head, title, "title", bg=fill)).pack(side="top", fill="x", expand=True)
        if subtitle:
            autowrap(label(b, subtitle, "body", "muted", bg=fill)).grid(row=1, column=2, sticky="we", pady=(px(2), 0))
        if note:
            label(b, note, "small", "accent", bg=fill).grid(row=2, column=2, sticky="w", pady=(px(4), 0))
        self.configure(cursor="hand2")
        bind_tree(self, "<Button-1>", lambda e: command())


class CheckRow(RoundCard):
    """One symptom with a tick box (MotoLogic symptom checklist)."""

    def __init__(self, parent, text: str, checked: bool, command: Callable[[], None], bg: str = "surface"):
        fill = "lime_soft" if checked else "surface"
        super().__init__(parent, fill=fill, border="border", radius=10, bg=bg, pad=12)
        d = px(20)
        box = tk.Canvas(self.body, width=d, height=d, bg=C[fill], highlightthickness=0, bd=0)
        if checked:
            round_rect(box, 1, 1, d - 1, d - 1, px(4), fill=C["panel"], outline="")
            box.create_line(d * .27, d * .52, d * .45, d * .7, d * .75, d * .32, fill=C["lime"], width=px(2))
        else:
            round_rect(box, 1, 1, d - 1, d - 1, px(4), fill=C["surface"], outline=C["muted"])
        box.pack(side="left", padx=(0, px(12)))
        autowrap(label(self.body, text, "lead", bg=fill)).pack(side="left", fill="x", expand=True)
        self.configure(cursor="hand2")
        bind_tree(self, "<Button-1>", lambda e: command())


class Gauge(tk.Canvas):
    """CF as a speedometer: half circle from 0 to 1.0 with a needle."""

    def __init__(self, parent, cf: float, size: int = 150, bg: str = "panel", caption: str = "", note: str = ""):
        import math
        on_panel = bg == "panel"
        fg, soft = ("on_panel", "panel_muted") if on_panel else ("text", "muted")
        w = px(size)
        r = w / 2 - px(10)
        super().__init__(parent, width=w, height=int(r + px(62 if note else 46)), bg=C[bg], highlightthickness=0,
                         bd=0)
        cx, cy, thick = w / 2, r + px(10), px(10)
        box = (cx - r, cy - r, cx + r, cy + r)
        self.create_arc(*box, start=0, extent=180, style="arc", width=thick,
                        outline=C["panel_soft"] if on_panel else C["chrome"])
        cf = max(0.0, min(1.0, cf))
        if cf > 0:
            self.create_arc(*box, start=180, extent=-180 * cf, style="arc", outline=C["lime"], width=thick)
        for v in (0, 0.25, 0.5, 0.75, 1.0):  # ticks, as on a speedometer
            a = math.radians(180 - 180 * v)
            r1, r2 = r - thick, r - thick - px(6)
            self.create_line(cx + r1 * math.cos(a), cy - r1 * math.sin(a), cx + r2 * math.cos(a),
                             cy - r2 * math.sin(a), fill=C[soft])
        a = math.radians(180 - 180 * cf)
        self.create_line(cx, cy, cx + (r - px(18)) * math.cos(a), cy - (r - px(18)) * math.sin(a),
                         fill=C[fg], width=px(3), capstyle="round")
        self.create_oval(cx - px(6), cy - px(6), cx + px(6), cy + px(6), fill=C["lime"], outline="")
        self.create_text(cx - r, cy + px(14), text="0", font=F["small"], fill=C[soft])
        self.create_text(cx + r, cy + px(14), text="1.0", font=F["small"], fill=C[soft])
        self.create_text(cx, cy + px(28), text=caption or f"CF {cf:.2f}", font=(theme.UI_FONT, 13, "bold"), fill=C[fg])
        if note:  # e.g. the raw CF under a plain-language caption
            self.create_text(cx, cy + px(48), text=note, font=F["mono"], fill=C[soft])


# Icons drawn with lines in a 0..1 box, so they scale and follow the light / dark colours (no images).
def _draw_icon(c: tk.Canvas, name: str, s: float, color: str) -> None:
    lw = max(1.5, s / 14)

    def P(*xy):
        return [v * s for v in xy]

    def line(*xy, width=None):
        c.create_line(*P(*xy), fill=color, width=width or lw, capstyle="round", joinstyle="round")

    def oval(x0, y0, x1, y1, fill=""):
        c.create_oval(*P(x0, y0, x1, y1), outline=color, width=lw, fill=fill)

    def rect(x0, y0, x1, y1):
        c.create_rectangle(*P(x0, y0, x1, y1), outline=color, width=lw)

    if name in ("scooter", "manual"):
        oval(.06, .58, .34, .86)
        oval(.66, .58, .94, .86)
        if name == "scooter":
            line(.2, .72, .38, .58, .7, .58, .8, .72)
            line(.66, .58, .6, .22, .76, .22)
            line(.28, .5, .5, .5)
        else:
            line(.2, .72, .42, .44, .68, .44, .8, .72)
            line(.42, .44, .5, .72, .6, .72)
            line(.68, .44, .64, .24, .78, .24)
            line(.4, .36, .6, .36)
    elif name == "battery":
        rect(.12, .3, .88, .82)
        rect(.24, .2, .36, .3)
        rect(.64, .2, .76, .3)
        line(.24, .56, .4, .56)
        line(.32, .48, .32, .64)
        line(.6, .56, .76, .56)
    elif name == "spark_plug":
        rect(.42, .06, .58, .2)
        rect(.36, .2, .64, .46)
        rect(.4, .46, .6, .7)
        line(.5, .7, .5, .84, .62, .84)
        line(.7, .74, .8, .66)
        line(.72, .9, .84, .9)
    elif name == "engine":
        rect(.16, .36, .8, .84)
        rect(.3, .18, .66, .36)
        for y in (.48, .6, .72):
            line(.8, y, .92, y)
        line(.04, .6, .16, .6)
    elif name == "chain":
        oval(.06, .3, .46, .7)
        oval(.62, .4, .86, .64)
        line(.26, .3, .74, .4)
        line(.26, .7, .74, .64)
    elif name == "brake_disc":
        oval(.08, .08, .92, .92)
        oval(.36, .36, .64, .64)
        for x, y in ((.5, .2), (.8, .5), (.5, .8), (.2, .5)):
            oval(x - .04, y - .04, x + .04, y + .04)
    elif name == "tyre":
        oval(.06, .06, .94, .94)
        oval(.3, .3, .7, .7)
        for xy in ((.5, .06, .5, .3), (.5, .7, .5, .94), (.06, .5, .3, .5), (.7, .5, .94, .5)):
            line(*xy)
    elif name == "wrench":
        line(.2, .82, .62, .4, width=lw * 1.6)
        c.create_arc(*P(.52, .1, .92, .5), start=200, extent=270, style="arc", outline=color, width=lw * 1.4)
    elif name == "shield":
        line(.5, .06, .86, .2, .82, .56, .5, .92, .18, .56, .14, .2, .5, .06)
        line(.32, .5, .46, .64, .7, .38)
    elif name == "pulse":
        line(.04, .55, .3, .55, .4, .25, .55, .82, .66, .45, .96, .45)
    elif name == "history":
        rect(.18, .1, .82, .9)
        for y in (.32, .5, .68):
            line(.32, y, .68, y)
    elif name == "layers":
        line(.5, .14, .9, .34, .5, .54, .1, .34, .5, .14)
        line(.1, .52, .5, .72, .9, .52)
        line(.1, .7, .5, .9, .9, .7)
    elif name == "search":
        oval(.12, .12, .62, .62)
        line(.56, .56, .88, .88)
    elif name == "info":
        oval(.1, .1, .9, .9)
        line(.5, .44, .5, .7)
        oval(.47, .27, .53, .33, fill=color)
    else:  # "check" and any other name
        line(.18, .52, .4, .74, .82, .28)


ICONS = ("scooter", "manual", "battery", "spark_plug", "engine", "chain", "brake_disc", "tyre", "wrench",
         "shield", "pulse", "history", "layers", "search", "info", "check")
SUBSYSTEM_ICONS = {"starting_fuel": "battery", "ignition_electrical": "spark_plug", "engine": "engine",
                   "transmission": "chain", "brakes": "brake_disc", "tyres_suspension": "tyre"}


def icon(parent, name: str, size: int = 24, color: str = "text", bg: str = "surface") -> tk.Canvas:
    """A small line icon (vehicle, part of the motorbike, wrench, shield, ...) drawn on a Canvas."""
    s = px(size)
    c = tk.Canvas(parent, width=s, height=s, bg=C[bg], highlightthickness=0, bd=0)
    _draw_icon(c, name, s, C[color])
    return c
