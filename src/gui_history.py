"""MotoLogic "Lịch sử phiên" screen: every result of this run of the program (owner: Giang).

Each finished diagnosis is a gui_diagnosis.Record in app.state["history"]; clicking a
row opens its step 3 again. Nothing is written to disk: the list lasts while the app runs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import tkinter as tk

from gui_diagnosis import TEXT as DX_TEXT
from gui_diagnosis import Record, bike_text, model_name, new_dx
from gui_widgets import (SUBSYSTEM_ICONS, Page, PillButton, RoundCard, ScrollFrame, autowrap, bind_tree, chip,
                         eyebrow, icon, label, px)
from kb import KnowledgeBase
from theme import COLORS as C

TEXT = {
    "vi": {"eyebrow": "Lịch sử phiên", "title": "Các lần chẩn đoán",
           "sub": "Mỗi kết quả trong lần chạy chương trình này. Bấm một dòng để mở lại kết quả.",
           "session": "Phiên {n:03d}", "none": "Chưa có kết quả nào. Tìm lỗi phù hợp ở màn Chẩn đoán.",
           "no_fault": "Chưa đủ dữ kiện", "go": "Bắt đầu chẩn đoán", "count": "{n} phiên", "count_one": "1 phiên"},
    "en": {"eyebrow": "Session history", "title": "Your diagnoses",
           "sub": "Every result of this run of the program. Click a row to open the result again.",
           "session": "Session {n:03d}", "none": "No result yet. Find a fault on the Diagnosis screen.",
           "no_fault": "Not enough evidence", "go": "Start diagnosis", "count": "{n} sessions", "count_one": "1 session"},
}


@dataclass
class Row:
    index: int          # position in app.state["history"]
    session: str
    time: str
    bike: str
    method: str
    fault: str          # fault name, or "not enough evidence"
    cf: float
    subsystem: str


def rows(kb: KnowledgeBase, history: List[Record], lang: str) -> List[Row]:
    """The history, newest first."""
    t = TEXT[lang]
    out = []
    for i, rec in enumerate(history):
        ds = rec.result.diagnoses
        top = ds[0] if ds else None
        out.append(Row(i, t["session"].format(n=rec.number), rec.time, bike_text(rec.kind, rec.fuel, lang, model_name(kb, rec.model)),
                       DX_TEXT[lang]["method_" + rec.method], kb.text(top.fault, lang) if top else t["no_fault"],
                       top.cf if top else 0.0, kb.symbols[top.fault].subsystem if top else ""))
    return out[::-1]


def reopen(state: dict, index: int) -> None:
    """Show step 3 of a past session on the Diagnosis screen."""
    rec = state["history"][index]
    state["dx"] = dict(new_dx(), kind=rec.kind, fuel=rec.fuel, model=rec.model, method=rec.method, step=3,
                       record=index)


class HistoryPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.scroll = ScrollFrame(self, bg="bg")
        self.scroll.pack(fill="both", expand=True)

    def on_show(self) -> None:  # results are added on another screen, so draw on every visit
        t, app = TEXT[self.app.lang], self.app
        history = app.state.setdefault("history", [])
        self.scroll.clear()
        page = tk.Frame(self.scroll.inner, bg=C["bg"], padx=px(8))
        page.pack(fill="both", expand=True)
        eyebrow(page, t["eyebrow"]).pack(anchor="w")
        head = tk.Frame(page, bg=C["bg"])
        head.pack(fill="x", pady=(px(6), 0))
        label(head, t["title"], "hero", bg="bg").pack(side="left")
        label(head, t["count_one"] if len(history) == 1 else t["count"].format(n=len(history)), "lead", "muted", bg="bg").pack(side="right", anchor="s")
        autowrap(label(page, t["sub"], "lead", "muted", bg="bg")).pack(fill="x", pady=(px(4), px(20)))
        if not history:
            card = RoundCard(page)
            card.pack(fill="x")
            label(card.body, t["none"], "lead", "muted").pack(anchor="w", pady=(0, px(14)))
            PillButton(card.body, t["go"], lambda: app.show("diagnosis"), bg="surface").pack(anchor="w")
            return
        for r in rows(app.kb, history, app.lang):
            card = RoundCard(page, radius=14, pad=16)
            card.pack(fill="x", pady=(0, px(10)))
            b = card.body
            b.columnconfigure(1, weight=1)
            icon(b, SUBSYSTEM_ICONS.get(r.subsystem, "info"), 28, "accent").grid(row=0, column=0, rowspan=2,
                                                                                 padx=(0, px(14)))
            label(b, r.fault, "title").grid(row=0, column=1, sticky="w")
            label(b, f"{r.session} · {r.time} · {r.bike} · {r.method}", "body", "muted").grid(row=1, column=1,
                                                                                             sticky="w")
            if r.cf:
                chip(b, f"CF {r.cf:.2f}", C["on_lime"], C["lime"]).grid(row=0, column=2, rowspan=2)
            card.configure(cursor="hand2")
            bind_tree(card, "<Button-1>", lambda e, i=r.index: self.open(i))

    def open(self, index: int) -> None:
        reopen(self.app.state, index)
        self.app.show("diagnosis")
