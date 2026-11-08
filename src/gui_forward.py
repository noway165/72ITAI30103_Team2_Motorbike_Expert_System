"""Màn hình "Theo triệu chứng": forward chaining, xếp hạng CF và kiểm chứng Wang (owner: Giang).

The rider picks the vehicle type and ticks the symptoms (grouped by part, with a
search box), then presses "Chẩn đoán". Each result card shows the fault, its CF,
the severity, what to do, whether Wang's algorithm proves the fault, and, when
clicked, how the fault was found (present.how_rows).

The top half of this file is plain logic with no drawing (tests/test_gui_forward.py);
ForwardPage at the bottom only draws. Look and wording: docs/ui_guide.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

import tkinter as tk
from tkinter import ttk

from forward_chaining import DEFAULT_THRESHOLD, ForwardResult, forward_chain
from gui_widgets import (CFBar, HintEntry, Page, Panel, ScrollFrame, autowrap, chip, dot, fold, label, link,
                         page_header, px, rank_badge, severity_chip)
from kb import KnowledgeBase
from present import HowRow, NearMiss, how_rows, near_misses, short
from present import t as present_text
from theme import COLORS as C
from theme import FONTS as F
from theme import LEFT_COLUMN_WIDTH, MAX_RESULTS, PAD, SUBSYSTEM_COLORS, SUBSYSTEM_NAMES, SUBSYSTEM_ORDER
from wang import check_engines, entails

TEXT = {
    "vi": {
        "title": "Chẩn đoán theo triệu chứng",
        "sub": "Chọn loại xe và các triệu chứng đang gặp, rồi bấm Chẩn đoán. Chương trình suy diễn tiến "
               "(forward chaining), xếp hạng lỗi theo độ tin cậy và kiểm chứng bằng thuật toán Wang.",
        "input": "Xe và triệu chứng", "n_selected": "{n} đã chọn",
        "sample": "KỊCH BẢN MẪU", "sample_pick": "Chọn để tải một kịch bản…",
        "vehicle": "1. LOẠI XE", "symptoms": "2. TRIỆU CHỨNG",
        "manual": "Xe số", "scooter": "Xe tay ga", "fi": "Phun xăng (FI)", "carb": "Bình xăng con",
        "unknown": "Không rõ",
        "search": "Tìm: còi, phanh, khói…", "no_match": "Không có triệu chứng nào khớp.",
        "diagnose": "Chẩn đoán", "clear": "Xoá hết",
        "results": "Kết quả", "empty": "Chọn loại xe và triệu chứng, rồi bấm Chẩn đoán (hoặc Enter).",
        "no_symptom": "Chưa chọn triệu chứng nào.",
        "wang_yes": "Wang: chứng minh được", "wang_no": "Wang: không chứng minh được",
        "wang_ok": "Wang và forward chaining khớp nhau ({n} lỗi chứng minh được).",
        "wang_bad": "Wang và forward chaining khác nhau: {d}",
        "rules": "Luật", "more": "+ {n} lỗi có độ tin cậy thấp hơn",
        "add": "Bấm để thêm triệu chứng và chẩn đoán lại:",
    },
    "en": {
        "title": "Diagnosis by symptoms",
        "sub": "Choose the vehicle type and the symptoms you notice, then press Diagnose. The program runs "
               "forward chaining, ranks the faults by confidence and checks them with Wang's algorithm.",
        "input": "Vehicle and symptoms", "n_selected": "{n} selected",
        "sample": "SAMPLE SCENARIO", "sample_pick": "Pick one to load it…",
        "vehicle": "1. VEHICLE TYPE", "symptoms": "2. SYMPTOMS",
        "manual": "Manual", "scooter": "Scooter", "fi": "Fuel injection", "carb": "Carburettor",
        "unknown": "Not sure",
        "search": "Search: horn, brake, smoke…", "no_match": "No symptom matches.",
        "diagnose": "Diagnose", "clear": "Clear",
        "results": "Results", "empty": "Choose the vehicle type and symptoms, then press Diagnose (or Enter).",
        "no_symptom": "No symptom selected yet.",
        "wang_yes": "Wang: proved", "wang_no": "Wang: not proved",
        "wang_ok": "Wang and forward chaining agree (proved: {n}).",
        "wang_bad": "Wang and forward chaining differ: {d}",
        "rules": "Rules", "more": "+ {n} more faults with lower confidence",
        "add": "Click to add a symptom and diagnose again:",
    },
}

# Vehicle-type answers (vehicle.json) chosen with radio buttons instead of the symptom list
VEHICLE = {"manual": "is_manual", "scooter": "is_scooter", "fi": "is_fuel_injected", "carb": "is_carburetor"}


# ---------------------------------------------------------------------------
# Logic (no drawing)
# ---------------------------------------------------------------------------

def vehicle_symptoms(kind: str, fuel: str) -> List[str]:
    """Symptoms for the chosen vehicle type; "" means "not sure" and adds nothing."""
    return [VEHICLE[v] for v in (kind, fuel) if v]


def symptom_groups(kb: KnowledgeBase, lang: str) -> List[Tuple[str, List[str]]]:
    """(subsystem, symptom ids sorted by their text) for every part, vehicle type left out."""
    groups = []
    for sub in SUBSYSTEM_ORDER:
        ids = [sid for sid, sym in kb.symptoms.items() if sym.subsystem == sub]
        if ids:
            groups.append((sub, sorted(ids, key=lambda s: fold(short(kb, s, lang)))))
    return groups


def search_key(kb: KnowledgeBase, sid: str, lang: str) -> str:
    """Text a search looks in: the question, the hint and the id, without accents."""
    return fold(" ".join((kb.question(sid, lang), kb.symbols[sid].hint.get(lang, ""), sid)))


def matches(key: str, query: str) -> bool:
    """Every word of the query is in the key ("phanh ken" finds "Phanh kêu ken két")."""
    return all(word in key for word in fold(query).split())


def from_scenario(scenario) -> Tuple[str, str, Set[str]]:
    """(kind, fuel, other symptoms) of a scenario, to fill the form."""
    kind = next((k for k in ("manual", "scooter") if VEHICLE[k] in scenario.symptoms), "")
    fuel = next((k for k in ("fi", "carb") if VEHICLE[k] in scenario.symptoms), "")
    return kind, fuel, {s for s in scenario.symptoms if s not in VEHICLE.values()}


@dataclass
class Card:
    rank: int
    fault: str
    name: str
    cf: float
    severity: Optional[str]
    action: str
    rules: List[str]
    how: List[HowRow]
    wang: bool          # Wang's algorithm proves the fault from the rules and the answers
    wang_steps: int


@dataclass
class Outcome:
    result: ForwardResult
    cards: List[Card]                 # at most MAX_RESULTS, best first
    hidden: int                       # faults above the threshold that are not shown
    wang_agree: bool                  # Wang proves exactly the faults forward chaining derived
    wang_diff: List[str] = field(default_factory=list)
    near: List[NearMiss] = field(default_factory=list)  # only when no fault reached the threshold


def diagnose(kb: KnowledgeBase, symptoms: Iterable[str], lang: str = "vi",
             threshold: float = DEFAULT_THRESHOLD) -> Outcome:
    """Forward chaining on the symptoms, ranked cards, and Wang's check of every derived fault."""
    symptoms = list(dict.fromkeys(symptoms))
    result = forward_chain(kb, symptoms, threshold=threshold)
    cards = []
    for i, d in enumerate(result.diagnoses[:MAX_RESULTS], 1):
        proof = entails(kb, symptoms, d.fault)
        cards.append(Card(i, d.fault, kb.text(d.fault, lang), d.cf, d.severity, kb.action(d.fault, lang),
                          d.rules, how_rows(kb, result.wm, d.fault, lang), proof.valid, proof.steps))
    # Wang ignores CF, so it is compared with every fault forward chaining derived (any CF)
    check = check_engines(kb, "gui", symptoms)
    near = near_misses(kb, result.wm) if not result.diagnoses else []
    return Outcome(result, cards, max(0, len(result.diagnoses) - MAX_RESULTS), check.agree,
                   sorted(check.wang ^ check.forward), near)


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

class ForwardPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.t = TEXT[app.lang]
        st = app.state
        st.setdefault("fw_selected", set())
        st.setdefault("fw_vehicle", ("", ""))
        st.setdefault("fw_done", False)
        self.outcome: Optional[Outcome] = None
        self.open: Set[str] = set()   # cards with the "how" explanation open

        page_header(self, self.t["title"], self.t["sub"]).pack(fill="x", pady=(0, PAD["m"]))
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)
        self.build_input(body)
        self.build_results(body)
        self.refresh_count()
        if st["fw_done"]:   # language changed: show the same diagnosis again
            self.run()

    # --- left: vehicle and symptoms ---
    def build_input(self, body) -> None:
        app, t, kb, lang = self.app, self.t, self.app.kb, self.app.lang
        left = Panel(body, t["input"], footer=True)
        left.pack(side="left", fill="y")
        left.configure(width=px(LEFT_COLUMN_WIDTH))
        left.pack_propagate(False)
        self.left = left
        top = tk.Frame(left.body, bg=C["surface"], padx=14, pady=10)
        top.pack(fill="x")

        if app.scenarios:
            label(top, t["sample"], "small_bold", "muted").pack(anchor="w")
            self.sample = ttk.Combobox(top, state="readonly", font=F["small"],
                                       values=[f"{s.id} · {s.description.get(lang, '')}" for s in app.scenarios])
            self.sample.set(t["sample_pick"])
            self.sample.pack(fill="x", pady=(2, 10))
            self.sample.bind("<<ComboboxSelected>>", lambda e: self.load(app.scenarios[self.sample.current()]))

        label(top, t["vehicle"], "small_bold", "muted").pack(anchor="w")
        kind, fuel = app.state["fw_vehicle"]
        self.kind, self.fuel = tk.StringVar(value=kind), tk.StringVar(value=fuel)
        for var, options in ((self.kind, ("manual", "scooter", "")), (self.fuel, ("fi", "carb", ""))):
            row = tk.Frame(top, bg=C["surface"])
            row.pack(fill="x", pady=(4, 0))
            for o in options:
                ttk.Radiobutton(row, text=t[o or "unknown"], value=o, variable=var,
                                command=self.save_form).pack(side="left", padx=(0, 12))
        label(top, t["symptoms"], "small_bold", "muted").pack(anchor="w", pady=(12, 4))
        self.query = HintEntry(top, t["search"], lambda: self.filter())
        self.query.pack(fill="x")

        self.list = ScrollFrame(left.body)
        self.list.pack(fill="both", expand=True, padx=(14, 0), pady=(0, 6))
        self.vars: Dict[str, tk.BooleanVar] = {}
        self.groups = []
        for sub, ids in symptom_groups(kb, lang):
            head = tk.Frame(self.list.inner, bg=C["surface"])
            dot(head, SUBSYSTEM_COLORS[sub]).pack(side="left", padx=(0, 7))
            label(head, SUBSYSTEM_NAMES[lang][sub], "small_bold").pack(side="left")
            count = label(head, "", "small", "muted")
            count.pack(side="right", padx=8)
            rows = []
            for sid in ids:
                var = tk.BooleanVar(value=sid in app.state["fw_selected"])
                self.vars[sid] = var
                cb = tk.Checkbutton(self.list.inner, text=short(kb, sid, lang), variable=var, command=self.save_form,
                                    font=F["body"], bg=C["surface"], fg=C["text"], activebackground=C["surface"],
                                    selectcolor=C["surface"], anchor="w", justify="left", bd=0,
                                    highlightthickness=0, wraplength=px(LEFT_COLUMN_WIDTH - 80), cursor="hand2")
                rows.append((sid, cb, search_key(kb, sid, lang)))
            self.groups.append((head, count, rows))
        self.no_match = label(self.list.inner, t["no_match"], "small", "muted")
        self.filter()

        ttk.Button(left.foot, text=t["diagnose"], style="Primary.TButton", command=self.run).pack(
            side="left", padx=(14, 8), pady=10)
        ttk.Button(left.foot, text=t["clear"], style="Secondary.TButton", command=self.clear).pack(side="left")

    # --- right: results ---
    def build_results(self, body) -> None:
        right = Panel(body, self.t["results"])
        right.pack(side="left", fill="both", expand=True, padx=(PAD["m"], 0))
        self.right = right
        self.status = label(right, "", "small", "muted", bg="chrome", padx=14, pady=6)
        self.cards = ScrollFrame(right.body)
        self.cards.pack(fill="both", expand=True, pady=(10, 0))
        self.message(self.t["empty"])

    # --- form ---
    def selected(self) -> Set[str]:
        return {sid for sid, v in self.vars.items() if v.get()}

    def symptoms(self) -> List[str]:
        return vehicle_symptoms(self.kind.get(), self.fuel.get()) + sorted(self.selected())

    def save_form(self) -> None:
        self.app.state["fw_selected"] = self.selected()
        self.app.state["fw_vehicle"] = (self.kind.get(), self.fuel.get())
        self.refresh_count()

    def refresh_count(self) -> None:
        for head, count, rows in self.groups:
            n = sum(self.vars[sid].get() for sid, _, _ in rows)
            count.configure(text=f"{n} / {len(rows)}", fg=C["accent"] if n else C["muted"])
        self.left.meta.configure(text=self.t["n_selected"].format(n=len(self.selected())))

    def filter(self) -> None:
        if not hasattr(self, "groups"):
            return
        q = self.query.value().strip()
        self.no_match.pack_forget()
        for head, _, rows in self.groups:
            head.pack_forget()
            for _, cb, _ in rows:
                cb.pack_forget()
        shown_any = False
        for head, _, rows in self.groups:
            shown = [cb for _, cb, key in rows if matches(key, q)]
            if shown:
                shown_any = True
                head.pack(fill="x", pady=(10, 4))
                for cb in shown:
                    cb.pack(fill="x", padx=(2, 0), pady=1)
        if not shown_any:
            self.no_match.pack(anchor="w", pady=10)
        self.list.to_top()

    def load(self, scenario) -> None:
        kind, fuel, chosen = from_scenario(scenario)
        self.kind.set(kind)
        self.fuel.set(fuel)
        for sid, v in self.vars.items():
            v.set(sid in chosen)
        self.save_form()
        self.run()

    def clear(self) -> None:
        for v in self.vars.values():
            v.set(False)
        self.kind.set("")
        self.fuel.set("")
        self.save_form()
        self.app.state["fw_done"] = False
        self.outcome = None
        self.right.meta.configure(text="")
        self.set_status("")
        self.message(self.t["empty"])

    def add_symptom(self, sid: str) -> None:
        self.vars[sid].set(True)
        self.save_form()
        self.run()

    # --- diagnosis ---
    def run(self) -> None:
        if not self.selected():
            self.message(self.t["no_symptom"])
            return
        app = self.app
        self.outcome = diagnose(app.kb, self.symptoms(), app.lang)
        app.state["fw_done"] = True
        self.open = {self.outcome.cards[0].fault} if self.outcome.cards else set()
        fired = [r.id for r in self.outcome.result.fired]
        meta = present_text("rules_fired", app.lang, n=len(fired)) + (": " + ", ".join(fired) if fired else "")
        self.right.meta.configure(text=meta)
        if self.outcome.wang_agree:
            n = len([c for c in self.outcome.cards if c.wang])
            self.set_status("✓ " + self.t["wang_ok"].format(n=n), "ok")
        else:
            self.set_status("✕ " + self.t["wang_bad"].format(d=", ".join(self.outcome.wang_diff)), "danger")
        self.render()

    def set_status(self, text: str, fg: str = "muted") -> None:
        self.status.configure(text=text, fg=C[fg])
        if text:
            self.status.pack(fill="x", side="bottom", before=self.right.body)
        else:
            self.status.pack_forget()

    def message(self, text: str) -> None:
        self.cards.clear()
        autowrap(label(self.cards.inner, text, "body", "muted")).pack(fill="x", padx=14, pady=30)

    def toggle(self, fault: str) -> None:
        self.open ^= {fault}
        self.render()

    def render(self) -> None:
        y = self.cards.canvas.yview()[0]
        self.cards.clear()
        o = self.outcome
        if not o.cards:
            self.render_near_misses()
        for card in o.cards:
            self.render_card(card)
        if o.hidden:
            label(self.cards.inner, self.t["more"].format(n=o.hidden), "small", "muted").pack(anchor="w", padx=14)
        self.after_idle(lambda: self.cards.canvas.yview_moveto(y))

    def render_card(self, c: Card) -> None:
        app = self.app
        box = tk.Frame(self.cards.inner, bg=C["surface"], highlightthickness=2 if c.rank == 1 else 1,
                       highlightbackground=C["accent"] if c.rank == 1 else C["border"], padx=14, pady=10)
        box.pack(fill="x", padx=(14, 6), pady=(0, 10))
        head = tk.Frame(box, bg=C["surface"])
        head.pack(fill="x")
        rank_badge(head, c.rank, c.rank == 1).pack(side="left")
        name = autowrap(label(head, c.name, "title"))
        name.pack(side="left", fill="x", expand=True, padx=(10, 8))
        severity_chip(head, c.severity, app.lang).pack(side="right")

        cf = tk.Frame(box, bg=C["surface"])
        cf.pack(fill="x", pady=(8, 0))
        label(cf, present_text("confidence", app.lang), "small", "muted", width=12).pack(side="left")
        label(cf, f"{c.cf:.2f}", "mono_bold").pack(side="right", padx=(8, 0))
        CFBar(cf, c.cf).pack(side="left", fill="x", expand=True)

        action = tk.Frame(box, bg=C["surface"])
        action.pack(fill="x", pady=(8, 0))
        label(action, present_text("action", app.lang) + ":", "small_bold", "muted").pack(anchor="w")
        autowrap(label(action, c.action, "body")).pack(fill="x")

        foot = tk.Frame(box, bg=C["surface"])
        foot.pack(fill="x", pady=(8, 0))
        is_open = c.fault in self.open
        link(foot, ("▾ " if is_open else "▸ ") + present_text("why_result", app.lang),
             lambda f=c.fault: self.toggle(f)).pack(side="left")
        wang_fg, wang_bg = (C["ok"], C["ok_soft"]) if c.wang else (C["danger"], C["danger_soft"])
        chip(foot, (self.t["wang_yes"] if c.wang else self.t["wang_no"]), wang_fg, wang_bg).pack(side="right")
        label(foot, f"{self.t['rules']} {', '.join(c.rules)}", "mono", "muted").pack(side="right", padx=8)

        if is_open:
            how = tk.Frame(box, bg=C["accent_soft"], padx=10, pady=6)
            how.pack(fill="x", pady=(6, 0))
            how.columnconfigure(1, weight=1)
            for r, row in enumerate(c.how):
                label(how, row.label, "mono_bold" if row.is_rule else "small", "text" if row.is_rule else "muted",
                      bg="accent_soft").grid(row=r, column=0, sticky="nw", padx=(0, 10), pady=1)
                autowrap(label(how, row.text, "small", bg="accent_soft")).grid(row=r, column=1, sticky="we", pady=1)
                label(how, f"{row.cf:.2f}", "mono", "muted", bg="accent_soft").grid(row=r, column=2, sticky="ne",
                                                                                   padx=(10, 0))
        for widget in (box, head, name):
            widget.bind("<Button-1>", lambda e, f=c.fault: self.toggle(f))

    def render_near_misses(self) -> None:
        app, kb, lang = self.app, self.app.kb, self.app.lang
        box = tk.Frame(self.cards.inner, bg=C["warn_soft"], padx=14, pady=12, highlightthickness=1,
                       highlightbackground=C["border"])
        box.pack(fill="x", padx=(14, 6), pady=(0, 10))
        label(box, present_text("no_fault", lang, t=DEFAULT_THRESHOLD), "heading", "warn",
              bg="warn_soft").pack(anchor="w")
        if not self.outcome.near:
            autowrap(label(box, present_text("nothing_derived", lang), "body", bg="warn_soft")).pack(fill="x",
                                                                                                   pady=(6, 0))
            return
        label(box, present_text("derived", lang), "body", bg="warn_soft").pack(anchor="w", pady=(6, 2))
        for m in self.outcome.near:
            row = tk.Frame(box, bg=C["warn_soft"])
            row.pack(fill="x")
            label(row, m.rule, "mono_bold", bg="warn_soft", width=7).pack(side="left")
            label(row, f"{m.cf:.2f}", "mono", "muted", bg="warn_soft").pack(side="right")
            autowrap(label(row, short(kb, m.symbol, lang), "body", bg="warn_soft")).pack(side="left", fill="x",
                                                                                       expand=True)
        missing = list(dict.fromkeys(s for m in self.outcome.near for _, s in m.missing if s in self.vars))
        if missing:
            label(box, self.t["add"], "body", bg="warn_soft").pack(anchor="w", pady=(8, 2))
            for sid in missing:
                autowrap(link(box, "+ " + short(kb, sid, lang), lambda s=sid: self.add_symptom(s), bg="warn_soft",
                              font="body")).pack(fill="x", pady=1)

    def on_key(self, event) -> None:
        if event.keysym == "Return":
            self.run()
