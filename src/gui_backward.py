"""Màn hình "Hỏi đáp từng câu": backward chaining, why / how (owner: Khoa).

The rider picks the part of the motorbike to check (or all parts) and presses
"Bắt đầu". The program then asks one yes / no question at a time, chosen by
backward chaining (BackwardSession in backward_chaining.py). While a question is
shown the rider can open "Tại sao hỏi câu này?" (why) and see which hypotheses are
still open. When no question is left, the result cards show the fault, its CF,
what to do and, when clicked, how the fault was concluded (how).

The top half of this file is plain logic with no drawing (tests/test_gui_backward.py);
BackwardPage at the bottom only draws. Look and wording: docs/ui_guide.md.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Set, Tuple

import tkinter as tk
from tkinter import ttk

from backward_chaining import UNKNOWN, BackwardSession, WhyStep
from forward_chaining import DEFAULT_THRESHOLD
from gui_widgets import (CFBar, Page, Panel, ScrollFrame, autowrap, dot, label, link, page_header, px,
                         rank_badge, severity_chip)
from kb import KnowledgeBase
from present import HowRow, NearMiss, how_rows, near_misses, short
from present import t as present_text
from theme import COLORS as C
from theme import LEFT_COLUMN_WIDTH, MAX_RESULTS, PAD, SUBSYSTEM_COLORS, SUBSYSTEM_NAMES, SUBSYSTEM_ORDER

TEXT = {
    "vi": {
        "title": "Hỏi đáp từng câu",
        "sub": "Chọn bộ phận cần kiểm tra rồi bấm Bắt đầu. Chương trình suy diễn lùi (backward chaining): "
               "đặt giả thuyết về từng lỗi và chỉ hỏi những câu cần để kiểm tra giả thuyết đó.",
        "setup": "Bộ phận cần kiểm tra", "all": "Tất cả bộ phận", "n_faults": "{n} lỗi",
        "start": "Bắt đầu", "restart": "Hỏi lại từ đầu", "again": "Hỏi lại",
        "open": "GIẢ THUYẾT CÒN LẠI", "open_count": "{n} / {total}",
        "open_idle": "Danh sách lỗi đang xét sẽ hiện ở đây.", "open_none": "Không còn giả thuyết nào.",
        "more": "+ {n} lỗi khác",
        "question": "Câu hỏi", "results": "Kết quả",
        "idle": "Chọn bộ phận ở bên trái rồi bấm Bắt đầu (hoặc Enter). Chọn đúng bộ phận thì số câu hỏi "
                "ít hơn nhiều so với kiểm tra tất cả.",
        "number": "CÂU {n}", "progress": "Đã loại {done} / {total} giả thuyết",
        "yes": "Có", "no": "Không", "unknown": "Không biết",
        "keys": "Phím tắt: C = Có, K = Không, B = Không biết, ? = Tại sao",
        "back": "◂ Quay lại câu trước",
        "why": "Tại sao hỏi câu này?",
        "why_head": "Chương trình đang kiểm tra giả thuyết “{goal}”. Câu hỏi này là điều kiện của luật "
                    "trên cùng; các luật bên dưới dùng kết luận của luật phía trên nó.",
        "why_direct": "Câu hỏi này được hỏi trực tiếp, không qua luật nào.",
        "IF": "NẾU", "AND": "VÀ", "THEN": "THÌ", "asking": "(đang hỏi)",
        "history": "ĐÃ TRẢ LỜI",
        "skipped": "Bạn trả lời “Không biết” {n} câu; chương trình coi như “Không”. Kiểm tra lại các "
                   "điểm sau rồi hỏi lại để kết quả chắc hơn:",
        "rules": "Luật",
        "add": "Trả lời “Có” cho một trong các câu sau thì chương trình mới kết luận được:",
    },
    "en": {
        "title": "Step-by-step questions",
        "sub": "Choose the part to check and press Start. The program uses backward chaining: it takes "
               "each fault as a hypothesis and asks only the questions needed to test it.",
        "setup": "Part to check", "all": "All parts", "n_faults": "{n} faults",
        "start": "Start", "restart": "Start again", "again": "Ask again",
        "open": "OPEN HYPOTHESES", "open_count": "{n} / {total}",
        "open_idle": "The faults being considered are listed here.", "open_none": "No hypothesis is left.",
        "more": "+ {n} more faults",
        "question": "Question", "results": "Diagnosis",
        "idle": "Choose a part on the left and press Start (or Enter). Choosing the right part needs far "
                "fewer questions than checking every part.",
        "number": "QUESTION {n}", "progress": "{done} / {total} hypotheses ruled out",
        "yes": "Yes", "no": "No", "unknown": "I don't know",
        "keys": "Keys: Y = Yes, N = No, U = I don't know, ? = Why",
        "back": "◂ Previous question",
        "why": "Why this question?",
        "why_head": "The program is testing the hypothesis “{goal}”. This question is a condition of the "
                    "first rule; each rule below uses the conclusion of the rule above it.",
        "why_direct": "This question is asked directly, not through a rule.",
        "IF": "IF", "AND": "AND", "THEN": "THEN", "asking": "(asking now)",
        "history": "ANSWERED",
        "skipped": "You answered “I don't know” {n} time(s); the program treated them as “No”. Check "
                   "these points and ask again for a more certain result:",
        "rules": "Rules",
        "add": "The program can only conclude if the answer to one of these is “Yes”:",
    },
}

ALL = "all"  # the choice "every part"

# Keys of on_key(): what the rider typed -> answer
KEYS = {"c": True, "y": True, "k": False, "n": False, "b": UNKNOWN, "u": UNKNOWN}


# ---------------------------------------------------------------------------
# Logic (no drawing)
# ---------------------------------------------------------------------------

def subsystem_options(kb: KnowledgeBase, lang: str) -> List[Tuple[str, str, int]]:
    """(key, name, number of faults) for "all parts" and every part that has faults."""
    counts: Dict[str, int] = {}
    for sym in kb.faults.values():
        counts[sym.subsystem] = counts.get(sym.subsystem, 0) + 1
    options = [(ALL, TEXT[lang]["all"], len(kb.faults))]
    options += [(sub, SUBSYSTEM_NAMES[lang][sub], counts[sub]) for sub in SUBSYSTEM_ORDER if counts.get(sub)]
    return options


def goals_for(kb: KnowledgeBase, subsystem: str) -> List[str]:
    """Faults to prove: every fault, or only the faults of one part."""
    return sorted(f for f, sym in kb.faults.items() if subsystem == ALL or sym.subsystem == subsystem)


def start_session(kb: KnowledgeBase, subsystem: str = ALL, answers: Optional[Dict[str, object]] = None,
                  threshold: float = DEFAULT_THRESHOLD, fixed: Optional[Dict[str, object]] = None) -> BackwardSession:
    """A new diagnosis; `answers` restores one that was in progress (after a language change),
    `fixed` holds facts chosen before the questions (vehicle type), which are not numbered."""
    return BackwardSession(kb, goals_for(kb, subsystem), threshold=threshold, answers=answers, fixed=fixed)


@dataclass
class WhyRow:
    rule: str                              # rule id, e.g. "TS09"
    premises: List[Tuple[str, str]]        # (text, state): "asking", "yes" or "todo"
    conclusion: str
    cf: float


def why_rows(kb: KnowledgeBase, chain: Sequence[WhyStep], symptom: str, answers: Dict[str, object],
             lang: str = "vi") -> List[WhyRow]:
    """The "why" explanation: the rules being tried, the one that needs the question first."""
    rows = []
    for step in reversed(chain):
        premises = []
        for p in step.rule.premises:
            if p == symptom:
                state = "asking"
            elif answers.get(p) not in (None, False):   # answered yes (or with a CF)
                state = "yes"
            else:
                state = "todo"
            premises.append((short(kb, p, lang), state))
        rows.append(WhyRow(step.rule.id, premises, short(kb, step.rule.conclusion, lang), step.rule.cf))
    return rows


@dataclass
class QuestionView:
    number: int
    symptom: str
    text: str
    hint: str
    goal: str                              # name of the fault being tested ("" if none)
    why: List[WhyRow]
    open: List[Tuple[str, str]]            # (fault id, name) of the hypotheses not ruled out
    total: int                             # number of hypotheses at the start


def open_hypotheses(kb: KnowledgeBase, session: BackwardSession, lang: str = "vi") -> List[Tuple[str, str]]:
    """(fault id, name) of the goal faults still possible, in the order of the parts."""
    order = {sub: i for i, sub in enumerate(SUBSYSTEM_ORDER)}
    faults = sorted(session.remaining(),
                    key=lambda f: (order.get(kb.symbols[f].subsystem, len(order)), kb.text(f, lang)))
    return [(f, kb.text(f, lang)) for f in faults]


def question_view(kb: KnowledgeBase, session: BackwardSession, lang: str = "vi") -> Optional[QuestionView]:
    """Everything the screen shows for the current question; None when the diagnosis is finished."""
    q = session.question
    if q is None:
        return None
    goal = kb.text(q.chain[0].goal, lang) if q.chain else ""
    return QuestionView(q.number, q.symptom, kb.question(q.symptom, lang),
                        kb.symbols[q.symptom].hint.get(lang, ""), goal,
                        why_rows(kb, q.chain, q.symptom, session.known(), lang),
                        open_hypotheses(kb, session, lang), len(session.goals))


def answer_key(value) -> str:
    """"yes", "no" or "unknown" for an answer kept in the session."""
    if value is UNKNOWN:
        return "unknown"
    return "yes" if value else "no"


def history(kb: KnowledgeBase, session: BackwardSession, lang: str = "vi") -> List[Tuple[str, str]]:
    """(question text, "yes" / "no" / "unknown") of every answer, newest first."""
    return [(short(kb, s, lang), answer_key(v)) for s, v in reversed(list(session.answers.items()))]


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


@dataclass
class Outcome:
    cards: List[Card]                      # at most MAX_RESULTS, best first
    hidden: int                            # faults above the threshold that are not shown
    questions: int
    rules_tried: int
    unknown: List[str] = field(default_factory=list)     # questions answered "I don't know"
    near: List[NearMiss] = field(default_factory=list)   # only when no fault reached the threshold


def outcome(kb: KnowledgeBase, session: BackwardSession, lang: str = "vi") -> Optional[Outcome]:
    """The result cards of a finished diagnosis; None while questions are left."""
    result = session.result
    if result is None:
        return None
    cards = [Card(i, d.fault, kb.text(d.fault, lang), d.cf, d.severity, kb.action(d.fault, lang), d.rules,
                  how_rows(kb, result.wm, d.fault, lang))
             for i, d in enumerate(result.diagnoses[:MAX_RESULTS], 1)]
    near = near_misses(kb, result.wm) if not result.diagnoses else []
    return Outcome(cards, max(0, len(result.diagnoses) - MAX_RESULTS), result.questions_asked,
                   result.rules_tried, [short(kb, s, lang) for s in session.unknown], near)


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

class BackwardPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.t = TEXT[app.lang]
        st = app.state
        st.setdefault("bw_subsystem", ALL)
        st.setdefault("bw_answers", None)   # dict while a diagnosis is running or finished, else None
        self.session: Optional[BackwardSession] = None
        self.why_open = False
        self.open: Set[str] = set()         # result cards with the "how" explanation open

        page_header(self, self.t["title"], self.t["sub"]).pack(fill="x", pady=(0, PAD["m"]))
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)
        self.build_setup(body)
        self.build_main(body)
        if st["bw_answers"] is not None:    # language changed: carry on with the same answers
            self.session = start_session(app.kb, st["bw_subsystem"], st["bw_answers"])
            self.first_card_open()
        self.render()

    # --- left: part to check and open hypotheses ---
    def build_setup(self, body) -> None:
        app, t = self.app, self.t
        left = Panel(body, t["setup"], footer=True)
        left.pack(side="left", fill="y")
        left.configure(width=px(LEFT_COLUMN_WIDTH))
        left.pack_propagate(False)
        self.left = left
        top = tk.Frame(left.body, bg=C["surface"], padx=14, pady=10)
        top.pack(fill="x")
        self.subsystem = tk.StringVar(value=app.state["bw_subsystem"])
        for key, name, n in subsystem_options(app.kb, app.lang):
            row = tk.Frame(top, bg=C["surface"])
            row.pack(fill="x", pady=1)
            ttk.Radiobutton(row, text=name, value=key, variable=self.subsystem).pack(side="left")
            label(row, t["n_faults"].format(n=n), "small", "muted").pack(side="right")
            if key != ALL:
                dot(row, SUBSYSTEM_COLORS[key]).pack(side="right", padx=(0, 6))

        tk.Frame(left.body, bg=C["border"], height=1).pack(fill="x", pady=(4, 0))
        head = tk.Frame(left.body, bg=C["surface"], padx=14)
        head.pack(fill="x", pady=(10, 4))
        label(head, t["open"], "small_bold", "muted").pack(side="left")
        self.open_count = label(head, "", "small", "muted")
        self.open_count.pack(side="right")
        self.open_list = ScrollFrame(left.body)
        self.open_list.pack(fill="both", expand=True, padx=(14, 0), pady=(0, 6))

        self.start_button = ttk.Button(left.foot, text=t["start"], style="Primary.TButton", command=self.start)
        self.start_button.pack(side="left", padx=(14, 8), pady=10)

    # --- right: the question, then the results ---
    def build_main(self, body) -> None:
        right = Panel(body, self.t["question"])
        right.pack(side="left", fill="both", expand=True, padx=(PAD["m"], 0))
        self.right = right
        self.status = label(right, "", "small", "muted", bg="chrome", padx=14, pady=6)
        self.main = ScrollFrame(right.body)
        self.main.pack(fill="both", expand=True, pady=(10, 0))

    # --- actions ---
    def start(self) -> None:
        """Start a new diagnosis for the part that is selected."""
        app = self.app
        app.state["bw_subsystem"] = self.subsystem.get()
        self.session = start_session(app.kb, app.state["bw_subsystem"])
        self.why_open = False
        self.after_answer()

    def answer(self, value) -> None:
        if self.session is None or self.session.finished:
            return
        self.session.answer(value)
        self.why_open = False
        self.after_answer()

    def back(self) -> None:
        if self.session is not None and self.session.undo():
            self.why_open = False
            self.after_answer()

    def after_answer(self) -> None:
        self.app.state["bw_answers"] = dict(self.session.answers)
        self.first_card_open()
        self.main.to_top()
        self.render()

    def first_card_open(self) -> None:
        result = self.session.result if self.session is not None else None
        self.open = {result.diagnoses[0].fault} if result is not None and result.diagnoses else set()

    def toggle_why(self) -> None:
        self.why_open = not self.why_open
        self.render()

    def toggle(self, fault: str) -> None:
        self.open ^= {fault}
        self.render()

    def set_status(self, text: str) -> None:
        self.status.configure(text=text)
        if text:
            self.status.pack(fill="x", side="bottom", before=self.right.body)
        else:
            self.status.pack_forget()

    # --- drawing ---
    def render(self) -> None:
        t, s = self.t, self.session
        y = self.main.canvas.yview()[0]
        self.main.clear()
        self.start_button.configure(text=t["start"] if s is None else t["restart"],
                                    style="Primary.TButton" if s is None else "Secondary.TButton")
        if s is None:
            self.right.title.configure(text=t["question"])
            self.right.meta.configure(text="")
            self.set_status("")
            autowrap(label(self.main.inner, t["idle"], "body", "muted")).pack(fill="x", padx=14, pady=30)
            self.render_open(None)
            return
        if s.finished:
            self.render_results(outcome(self.app.kb, s, self.app.lang))
        else:
            self.render_question(question_view(self.app.kb, s, self.app.lang))
        self.render_open(open_hypotheses(self.app.kb, s, self.app.lang))
        self.after_idle(lambda: self.main.canvas.yview_moveto(y))

    def render_open(self, faults: Optional[List[Tuple[str, str]]]) -> None:
        t, kb = self.t, self.app.kb
        self.open_list.clear()
        inner = self.open_list.inner
        if faults is None:
            self.open_count.configure(text="")
            autowrap(label(inner, t["open_idle"], "small", "muted")).pack(fill="x", pady=4)
            return
        self.open_count.configure(text=t["open_count"].format(n=len(faults), total=len(self.session.goals)),
                                  fg=C["accent"])
        if not faults:
            autowrap(label(inner, t["open_none"], "small", "muted")).pack(fill="x", pady=4)
        for fault, name in faults:
            row = tk.Frame(inner, bg=C["surface"])
            row.pack(fill="x", pady=2)
            dot(row, SUBSYSTEM_COLORS.get(kb.symbols[fault].subsystem, C["muted"])).pack(
                side="left", padx=(0, 7), pady=(5, 0), anchor="n")
            autowrap(label(row, name, "small")).pack(side="left", fill="x", expand=True, padx=(0, 8))

    def render_question(self, q: QuestionView) -> None:
        t, inner = self.t, self.main.inner
        self.right.title.configure(text=t["question"])
        self.right.meta.configure(text=t["progress"].format(done=q.total - len(q.open), total=q.total))
        self.set_status(t["keys"])

        box = tk.Frame(inner, bg=C["surface"], padx=14)
        box.pack(fill="x", padx=(0, 6))
        CFBar(box, (q.total - len(q.open)) / q.total if q.total else 0.0).pack(fill="x", pady=(0, 14))
        label(box, t["number"].format(n=q.number), "small_bold", "muted").pack(anchor="w")
        autowrap(label(box, q.text, "question")).pack(fill="x", pady=(4, 0))
        if q.hint:
            autowrap(label(box, q.hint, "small", "muted")).pack(fill="x", pady=(4, 0))

        buttons = tk.Frame(box, bg=C["surface"])
        buttons.pack(fill="x", pady=(16, 0))
        ttk.Button(buttons, text=t["yes"], style="Yes.TButton", command=lambda: self.answer(True)).pack(
            side="left")
        ttk.Button(buttons, text=t["no"], style="No.TButton", command=lambda: self.answer(False)).pack(
            side="left", padx=8)
        ttk.Button(buttons, text=t["unknown"], style="Secondary.TButton",
                   command=lambda: self.answer(UNKNOWN)).pack(side="left")

        links = tk.Frame(box, bg=C["surface"])
        links.pack(fill="x", pady=(14, 0))
        link(links, ("▾ " if self.why_open else "▸ ") + t["why"], self.toggle_why).pack(side="left")
        if q.number > 1:
            link(links, t["back"], self.back, fg="muted").pack(side="right")
        if self.why_open:
            self.render_why(box, q)

        answered = history(self.app.kb, self.session, self.app.lang)
        if answered:
            label(box, t["history"], "small_bold", "muted").pack(anchor="w", pady=(20, 4))
            colors = {"yes": "ok", "no": "danger", "unknown": "muted"}
            for text, key in answered:
                row = tk.Frame(box, bg=C["surface"])
                row.pack(fill="x", pady=1)
                label(row, t[key], "small_bold", colors[key], width=10).pack(side="left", anchor="n")
                autowrap(label(row, text, "small", "muted")).pack(side="left", fill="x", expand=True)

    def render_why(self, box, q: QuestionView) -> None:
        t = self.t
        why = tk.Frame(box, bg=C["accent_soft"], padx=10, pady=8)
        why.pack(fill="x", pady=(6, 0))
        why.columnconfigure(1, weight=1)
        head = t["why_head"].format(goal=q.goal) if q.why else t["why_direct"]
        autowrap(label(why, head, "small", bg="accent_soft")).grid(row=0, column=0, columnspan=3, sticky="we",
                                                                 pady=(0, 6))
        for r, row in enumerate(q.why, 1):
            parts = []
            for text, state in row.premises:
                mark = {"asking": " " + t["asking"], "yes": " ✓", "todo": ""}[state]
                parts.append(text + mark)
            rule_text = f"{t['IF']} {(' ' + t['AND'] + ' ').join(parts)} {t['THEN']} {row.conclusion}"
            label(why, row.rule, "mono_bold", bg="accent_soft").grid(row=r, column=0, sticky="nw", padx=(0, 10),
                                                                    pady=2)
            autowrap(label(why, rule_text, "small", bg="accent_soft")).grid(row=r, column=1, sticky="we", pady=2)
            label(why, f"{row.cf:.2f}", "mono", "muted", bg="accent_soft").grid(row=r, column=2, sticky="ne",
                                                                               padx=(10, 0), pady=2)

    def render_results(self, o: Outcome) -> None:
        t, lang, inner = self.t, self.app.lang, self.main.inner
        self.right.title.configure(text=t["results"])
        self.right.meta.configure(text=present_text("questions", lang, q=o.questions, r=o.rules_tried))
        self.set_status("")
        if not o.cards:
            self.render_near_misses(o)
        for card in o.cards:
            self.render_card(card)
        if o.hidden:
            label(inner, t["more"].format(n=o.hidden), "small", "muted").pack(anchor="w", padx=14)
        if o.unknown:
            box = tk.Frame(inner, bg=C["warn_soft"], padx=14, pady=10, highlightthickness=1,
                           highlightbackground=C["border"])
            box.pack(fill="x", padx=(14, 6), pady=(0, 10))
            autowrap(label(box, t["skipped"].format(n=len(o.unknown)), "small", "warn", bg="warn_soft")).pack(
                fill="x")
            for text in o.unknown:
                autowrap(label(box, "• " + text, "small", bg="warn_soft")).pack(fill="x", pady=1)
        foot = tk.Frame(inner, bg=C["surface"])
        foot.pack(fill="x", padx=14, pady=(4, 14))
        ttk.Button(foot, text=t["again"], style="Primary.TButton", command=self.start).pack(side="left")
        link(foot, t["back"], self.back, fg="muted").pack(side="left", padx=16)

    def render_card(self, c: Card) -> None:
        lang = self.app.lang
        box = tk.Frame(self.main.inner, bg=C["surface"], highlightthickness=2 if c.rank == 1 else 1,
                       highlightbackground=C["accent"] if c.rank == 1 else C["border"], padx=14, pady=10)
        box.pack(fill="x", padx=(14, 6), pady=(0, 10))
        head = tk.Frame(box, bg=C["surface"])
        head.pack(fill="x")
        rank_badge(head, c.rank, c.rank == 1).pack(side="left")
        name = autowrap(label(head, c.name, "title"))
        name.pack(side="left", fill="x", expand=True, padx=(10, 8))
        severity_chip(head, c.severity, lang).pack(side="right")

        cf = tk.Frame(box, bg=C["surface"])
        cf.pack(fill="x", pady=(8, 0))
        label(cf, present_text("confidence", lang), "small", "muted", width=12).pack(side="left")
        label(cf, f"{c.cf:.2f}", "mono_bold").pack(side="right", padx=(8, 0))
        CFBar(cf, c.cf).pack(side="left", fill="x", expand=True)

        action = tk.Frame(box, bg=C["surface"])
        action.pack(fill="x", pady=(8, 0))
        label(action, present_text("action", lang) + ":", "small_bold", "muted").pack(anchor="w")
        autowrap(label(action, c.action, "body")).pack(fill="x")

        foot = tk.Frame(box, bg=C["surface"])
        foot.pack(fill="x", pady=(8, 0))
        is_open = c.fault in self.open
        link(foot, ("▾ " if is_open else "▸ ") + present_text("why_result", lang),
             lambda f=c.fault: self.toggle(f)).pack(side="left")
        label(foot, f"{self.t['rules']} {', '.join(c.rules)}", "mono", "muted").pack(side="right")

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

    def render_near_misses(self, o: Outcome) -> None:
        kb, lang = self.app.kb, self.app.lang
        box = tk.Frame(self.main.inner, bg=C["warn_soft"], padx=14, pady=12, highlightthickness=1,
                       highlightbackground=C["border"])
        box.pack(fill="x", padx=(14, 6), pady=(0, 10))
        label(box, present_text("no_fault", lang, t=self.session.threshold), "heading", "warn",
              bg="warn_soft").pack(anchor="w")
        if not o.near:
            return
        label(box, present_text("derived", lang), "body", bg="warn_soft").pack(anchor="w", pady=(6, 2))
        for m in o.near:
            row = tk.Frame(box, bg=C["warn_soft"])
            row.pack(fill="x")
            label(row, m.rule, "mono_bold", bg="warn_soft", width=7).pack(side="left")
            label(row, f"{m.cf:.2f}", "mono", "muted", bg="warn_soft").pack(side="right")
            autowrap(label(row, short(kb, m.symbol, lang), "body", bg="warn_soft")).pack(side="left", fill="x",
                                                                                       expand=True)
        missing = list(dict.fromkeys(s for m in o.near for _, s in m.missing))
        if missing:
            autowrap(label(box, self.t["add"], "body", bg="warn_soft")).pack(fill="x", pady=(8, 2))
            for sid in missing:
                autowrap(label(box, "• " + short(kb, sid, lang), "body", bg="warn_soft")).pack(fill="x", pady=1)

    # --- keys ---
    def on_key(self, event) -> None:
        if self.session is None:
            if event.keysym == "Return":
                self.start()
            return
        if self.session.finished:
            return
        key = (event.char or "").lower()
        if key in KEYS:
            self.answer(KEYS[key])
        elif key == "?":
            self.toggle_why()
        elif event.keysym == "BackSpace":
            self.back()
