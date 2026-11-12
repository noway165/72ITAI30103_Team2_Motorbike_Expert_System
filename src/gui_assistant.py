"""Diagnosis assistant screen (owner: Lâm).

The rider describes the problem in their own words (Vietnamese or English).
nlu.py turns the text into symptoms, interview.py asks the few questions that
tell the most, and the team's forward chaining, how explanation and Wang's
algorithm give and check the answer.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import ttk

from gui_widgets import (CFBar, Page, Panel, ScrollFrame, autowrap, chip, label, link, page_header, px,
                         severity_chip)
from interview import Interview, Question
from nlu import Match, extract
from present import how_rows, short
from theme import COLORS as C
from theme import FONTS as F
from theme import PAD
from wang import entails

TEXT = {
    "vi": {
        "title": "Trợ lý chẩn đoán",
        "sub": "Kể tình trạng xe bằng lời của bạn (tiếng Việt hoặc tiếng Anh). Trợ lý tách ra các triệu chứng, "
               "chỉ hỏi thêm những câu đáng hỏi nhất, rồi kết luận bằng luật và kiểm chứng bằng Wang.",
        "tell": "Kể tình trạng xe", "examples": "VÍ DỤ", "analyze": "Phân tích", "reset": "Làm lại",
        "understood": "TRỢ LÝ HIỂU ĐƯỢC", "nothing": "Chưa nhận ra triệu chứng nào. Thử kể cụ thể hơn, "
                                                   "ví dụ: còi yếu, khói đen, tay phanh mềm.",
        "chat": "Trò chuyện", "beliefs": "KHẢ NĂNG HIỆN TẠI", "you": "Bạn", "bot": "Trợ lý",
        "heard": "Mình hiểu là:{items}", "heard_none": "Mình chưa nhận ra triệu chứng nào trong câu này.",
        "yes": "Có", "no": "Không", "dunno": "Không biết", "why": "Tại sao hỏi?",
        "why_text": "Câu này giúp phân biệt {faults}. Thông tin kỳ vọng: {gain:.2f} bit.",
        "done": "Mình đã đủ dữ kiện sau {n} câu hỏi.",
        "result": "Kết luận", "confidence": "Độ tin cậy", "action": "Cách xử lý", "how": "Vì sao ra kết quả này?",
        "wang_ok": "Đã chứng minh bằng thuật toán Wang", "wang_no": "Wang không chứng minh được",
        "others": "Cũng có thể:", "no_fault": "Chưa đủ dữ kiện để kết luận. Khả năng cao nhất: {f} ({p:.0%}).",
        "keys": "Phím: C/Y = Có · K/N = Không · B/U = Không biết · W = Tại sao",
        "placeholder": "Ví dụ: Sáng nay xe đề chỉ nghe tạch tạch, còi cũng yếu…",
        "remove": "Bỏ",
    },
    "en": {
        "title": "Diagnosis assistant",
        "sub": "Describe the problem in your own words (English or Vietnamese). The assistant picks out the "
               "symptoms, asks only the most useful questions, then concludes with the rules and checks the "
               "result with Wang's algorithm.",
        "tell": "Describe the problem", "examples": "EXAMPLES", "analyze": "Analyse", "reset": "Start again",
        "understood": "WHAT THE ASSISTANT UNDERSTOOD", "nothing": "No symptom recognised yet. Try to be more "
                                                                "specific, e.g. weak horn, black smoke, spongy brake.",
        "chat": "Conversation", "beliefs": "CURRENT LIKELIHOOD", "you": "You", "bot": "Assistant",
        "heard": "I understood:{items}", "heard_none": "I did not recognise any symptom in that.",
        "yes": "Yes", "no": "No", "dunno": "Don't know", "why": "Why ask?",
        "why_text": "This question separates {faults}. Expected information: {gain:.2f} bits.",
        "done": "I have enough after {n} questions.",
        "result": "Conclusion", "confidence": "Confidence", "action": "What to do", "how": "How was this found?",
        "wang_ok": "Proved with Wang's algorithm", "wang_no": "Wang could not prove it",
        "others": "It could also be:", "no_fault": "Not enough evidence yet. Most likely: {f} ({p:.0%}).",
        "keys": "Keys: Y = Yes · N = No · U = Don't know · W = Why",
        "placeholder": "e.g. The starter just clicks this morning and the horn is weak…",
        "remove": "Remove",
    },
}

EXAMPLES = [
    "Sáng nay xe Vision đề chỉ nghe tạch tạch, còi cũng yếu",
    "Xe Wave bình xăng con chạy ra khói đen, dạo này hao xăng",
    "My Air Blade's brake lever feels spongy and the brake fluid is low",
]


class AssistantPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.t = TEXT[app.lang]
        t, kb = self.t, app.kb
        self.removed: set = set()
        self.matches: List[Match] = []
        self.iv: Optional[Interview] = None
        self.question: Optional[Question] = None
        self.log: List[Tuple[str, Optional[bool]]] = []
        page_header(self, t["title"], t["sub"]).pack(fill="x", pady=(0, PAD["m"]))
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # --- left: the rider's words -----------------------------------------
        left = Panel(body, t["tell"], footer=True)
        left.pack(side="left", fill="y")
        left.configure(width=px(390))
        left.pack_propagate(False)
        lb = tk.Frame(left.body, bg=C["surface"], padx=14, pady=12)
        lb.pack(fill="both", expand=True)
        self.text = tk.Text(lb, height=6, wrap="word", font=F["body"], bg=C["surface"], fg=C["text"],
                            insertbackground=C["text"], relief="flat", highlightthickness=1,
                            highlightbackground=C["border"], highlightcolor=C["accent"], padx=8, pady=6)
        self.text.pack(fill="x")
        self.text.tag_configure("hit", background=C["highlight_soft"], foreground=C["text"])
        self.text.tag_configure("neg", background=C["danger_soft"], foreground=C["text"])
        self.text.bind("<Control-Return>", lambda e: (self.analyze(), "break")[1])
        label(lb, t["examples"], "small_bold", "muted").pack(anchor="w", pady=(10, 2))
        for ex in EXAMPLES:
            autowrap(link(lb, "› " + ex, lambda ex=ex: self.use_example(ex), font="small")).pack(fill="x", pady=1)
        label(lb, t["understood"], "small_bold", "muted").pack(anchor="w", pady=(14, 4))
        self.found = ScrollFrame(lb)
        self.found.pack(fill="both", expand=True)
        ttk.Button(left.foot, text=t["analyze"], style="Primary.TButton", command=self.analyze).pack(
            side="left", padx=(14, 8), pady=10)
        ttk.Button(left.foot, text=t["reset"], style="Secondary.TButton", command=self.reset).pack(side="left")

        # --- right: beliefs and conversation ---------------------------------
        right = Panel(body, t["chat"])
        right.pack(side="left", fill="both", expand=True, padx=(PAD["m"], 0))
        self.right = right
        self.beliefs_box = tk.Frame(right.body, bg=C["surface"], padx=14, pady=10)
        self.beliefs_box.pack(fill="x")
        tk.Frame(right.body, bg=C["border"], height=1).pack(fill="x")
        self.chat = ScrollFrame(right.body)
        self.chat.pack(fill="both", expand=True, padx=(14, 0), pady=8)
        label(right.body, t["keys"], "small", "muted").pack(anchor="w", padx=14, pady=(0, 8))

        st = app.state
        if st.get("as_text"):
            self.text.insert("1.0", st["as_text"])
            self.removed = set(st.get("as_removed", set()))
            self.analyze(replay=list(st.get("as_log", [])))
        else:
            self.show_beliefs()
            self.say(t["sub"], who="bot")

    # --- input --------------------------------------------------------------
    def use_example(self, text: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", text)
        self.removed.clear()
        self.analyze()

    def reset(self) -> None:
        self.text.delete("1.0", "end")
        self.removed.clear()
        for k in ("as_text", "as_log", "as_removed"):
            self.app.state.pop(k, None)
        self.iv, self.question, self.log, self.matches = None, None, [], []
        self.found.clear()
        self.chat.clear()
        self.show_beliefs()

    def remove(self, symptom: str) -> None:
        self.removed.add(symptom)
        self.analyze()

    def analyze(self, replay: Optional[List[Tuple[str, Optional[bool]]]] = None) -> None:
        kb, t = self.app.kb, self.t
        raw = self.text.get("1.0", "end").strip()
        self.app.state.update(as_text=raw, as_removed=set(self.removed), as_log=[])
        self.matches = [m for m in extract(raw, kb.symptoms) if m.symptom not in self.removed]
        # highlight what was understood
        for tag in ("hit", "neg"):
            self.text.tag_remove(tag, "1.0", "end")
        for m in self.matches:
            self.text.tag_add("hit" if m.value else "neg", f"1.0+{m.start}c", f"1.0+{m.end}c")
        self.render_found()
        self.chat.clear()
        self.log = []
        if raw:
            self.say(raw, who="you")
        if self.matches:
            items = "".join("\n" + ("✓ " if m.value else "✕ ") + short(kb, m.symptom, self.app.lang)
                            for m in self.matches)
            self.say(t["heard"].format(items=items), who="bot")
        elif raw:
            self.say(t["heard_none"], who="bot")
        self.iv = Interview(kb, {m.symptom: m.value for m in self.matches})
        for symptom, value in replay or []:
            self.iv.answer(symptom, value)
            self.log.append((symptom, value))
            self.say_answer(symptom, value)
        self.app.state["as_log"] = list(self.log)
        self.ask()

    def render_found(self) -> None:
        kb, lang = self.app.kb, self.app.lang
        self.found.clear()
        if not self.matches:
            autowrap(label(self.found.inner, self.t["nothing"], "small", "muted")).pack(fill="x")
            return
        for m in self.matches:
            row = tk.Frame(self.found.inner, bg=C["surface"])
            row.pack(fill="x", pady=2)
            fg, bg = (C["ok"], C["ok_soft"]) if m.value else (C["danger"], C["danger_soft"])
            chip(row, "✓" if m.value else "✕", fg, bg).pack(side="left", anchor="n")
            box = tk.Frame(row, bg=C["surface"])
            box.pack(side="left", fill="x", expand=True, padx=8)
            autowrap(label(box, short(kb, m.symptom, lang), "small")).pack(fill="x")
            label(box, f"“{m.phrase}”", "small", "muted").pack(anchor="w")
            link(row, "×", lambda s=m.symptom: self.remove(s), fg="muted", font="heading").pack(side="right")

    # --- conversation -------------------------------------------------------
    def say(self, text: str, who: str = "bot") -> tk.Frame:
        mine = who == "you"
        wrap = tk.Frame(self.chat.inner, bg=C["surface"])
        wrap.pack(fill="x", pady=4, padx=(px(60) if mine else 0, 6 if mine else px(60)))
        label(wrap, self.t["you"] if mine else self.t["bot"], "small_bold", "accent" if not mine else "muted").pack(
            anchor="e" if mine else "w")
        bubble = tk.Frame(wrap, bg=C["accent_soft"] if not mine else C["bg"], padx=12, pady=8)
        bubble.pack(anchor="e" if mine else "w", fill="x")
        autowrap(label(bubble, text, "body", bg="accent_soft" if not mine else "bg")).pack(fill="x")
        self.after_idle(lambda: self.chat.canvas.yview_moveto(1.0))
        return bubble

    def say_answer(self, symptom: str, value: Optional[bool]) -> None:
        t = self.t
        word = t["yes"] if value else t["no"] if value is False else t["dunno"]
        self.say(word, who="you")

    def ask(self) -> None:
        self.show_beliefs()
        q = self.iv.next_question() if self.iv else None
        self.question = q
        if q is None:
            if self.iv is not None and (self.matches or self.log):
                self.finish()
            return
        kb, t = self.app.kb, self.t
        bubble = self.say(kb.question(q.symptom, self.app.lang), who="bot")
        hint = kb.symbols[q.symptom].hint.get(self.app.lang)
        if hint:
            autowrap(label(bubble, hint, "small", "muted", bg="accent_soft")).pack(fill="x", pady=(2, 0))
        btns = tk.Frame(bubble, bg=C["accent_soft"])
        btns.pack(anchor="w", pady=(8, 0))
        ttk.Button(btns, text=t["yes"], style="Yes.TButton", width=8, command=lambda: self.answer(True)).pack(side="left")
        ttk.Button(btns, text=t["no"], style="No.TButton", width=8,
                   command=lambda: self.answer(False)).pack(side="left", padx=6)
        ttk.Button(btns, text=t["dunno"], style="Secondary.TButton", command=lambda: self.answer(None)).pack(side="left")
        self.why_box = tk.Frame(bubble, bg=C["accent_soft"])
        self.why_box.pack(fill="x")
        link(btns, t["why"], self.show_why, bg="accent_soft").pack(side="left", padx=10)
        self.active_buttons = btns

    def show_why(self) -> None:
        q, kb, lang = self.question, self.app.kb, self.app.lang
        if q is None:
            return
        for w in self.why_box.winfo_children():
            w.destroy()
        faults = ", ".join(f"{kb.text(f, lang)} ({p:.0%})" for f, p in q.splits) or "—"
        autowrap(label(self.why_box, self.t["why_text"].format(faults=faults, gain=q.gain), "small", "accent",
                       bg="accent_soft")).pack(fill="x", pady=(8, 0))

    def answer(self, value: Optional[bool]) -> None:
        q = self.question
        if q is None or self.iv is None:
            return
        for w in self.active_buttons.winfo_children():
            w.destroy()
        self.iv.answer(q.symptom, value)
        self.log.append((q.symptom, value))
        self.app.state["as_log"] = list(self.log)
        self.say_answer(q.symptom, value)
        self.ask()

    def on_key(self, event) -> None:
        if self.question is None or self.focus_get() is self.text:
            return
        ch = (event.char or "").lower()
        if ch in ("c", "y"):
            self.answer(True)
        elif ch in ("k", "n"):
            self.answer(False)
        elif ch in ("b", "u"):
            self.answer(None)
        elif ch == "w":
            self.show_why()

    # --- beliefs and result ------------------------------------------------
    def show_beliefs(self) -> None:
        for w in self.beliefs_box.winfo_children():
            w.destroy()
        label(self.beliefs_box, self.t["beliefs"], "small_bold", "muted").pack(anchor="w", pady=(0, 4))
        if self.iv is None:
            return
        kb, lang = self.app.kb, self.app.lang
        for i, (f, p) in enumerate(self.iv.beliefs(4)):
            row = tk.Frame(self.beliefs_box, bg=C["surface"])
            row.pack(fill="x", pady=2)
            label(row, f"{p:.0%}", "mono_bold" if i == 0 else "mono", "text" if i == 0 else "muted",
                  width=5).pack(side="right")
            bar = CFBar(row, p)
            bar.configure(width=px(170))
            bar.pack(side="right", padx=8)
            label(row, kb.text(f, lang), "small_bold" if i == 0 else "small").pack(side="left", fill="x", expand=True)

    def finish(self) -> None:
        kb, lang, t = self.app.kb, self.app.lang, self.t
        result = self.iv.result()
        n = len([1 for _, v in self.log])
        self.say(t["done"].format(n=n), who="bot")
        card = tk.Frame(self.chat.inner, bg=C["surface"], highlightthickness=2, highlightbackground=C["accent"],
                        padx=16, pady=12)
        card.pack(fill="x", pady=(6, 10), padx=(0, 6))
        if not result.diagnoses:
            f, p = (self.iv.beliefs(1) or [("", 0)])[0]
            autowrap(label(card, t["no_fault"].format(f=kb.text(f, lang) if f else "—", p=p), "heading", "warn")
                     ).pack(fill="x")
            return
        d = result.diagnoses[0]
        label(card, t["result"].upper(), "small_bold", "muted").pack(anchor="w")
        head = tk.Frame(card, bg=C["surface"])
        head.pack(fill="x", pady=(2, 0))
        label(head, kb.text(d.fault, lang), "title").pack(side="left")
        severity_chip(head, d.severity, lang).pack(side="right")
        cf = tk.Frame(card, bg=C["surface"])
        cf.pack(fill="x", pady=(8, 0))
        label(cf, t["confidence"], "small", "muted", width=12).pack(side="left")
        label(cf, f"{d.cf:.2f}", "mono_bold").pack(side="right", padx=(8, 0))
        CFBar(cf, d.cf).pack(side="left", fill="x", expand=True)
        autowrap(label(card, kb.action(d.fault, lang), "body")).pack(fill="x", pady=(8, 0))
        yes = [s for s, v in self.iv.answers.items() if v]
        proved = entails(kb, yes, d.fault).valid
        fg, bg = (C["ok"], C["ok_soft"]) if proved else (C["danger"], C["danger_soft"])
        chip(card, ("✓ " if proved else "✕ ") + (t["wang_ok"] if proved else t["wang_no"]), fg, bg).pack(
            anchor="w", pady=(8, 0))
        label(card, t["how"], "small_bold", "accent").pack(anchor="w", pady=(10, 2))
        how = tk.Frame(card, bg=C["surface"])
        how.pack(fill="x")
        how.columnconfigure(1, weight=1)
        for r, row in enumerate(how_rows(kb, result.wm, d.fault, lang)):
            label(how, row.label, "mono_bold" if row.is_rule else "small",
                  "text" if row.is_rule else "muted").grid(row=r, column=0, sticky="nw", padx=(0, 10), pady=1)
            autowrap(label(how, row.text, "small")).grid(row=r, column=1, sticky="we", pady=1)
            label(how, f"{row.cf:.2f}", "mono", "muted").grid(row=r, column=2, sticky="ne", padx=(10, 0))
        others = result.diagnoses[1:3]
        if others:
            label(card, t["others"], "small", "muted").pack(anchor="w", pady=(10, 0))
            for o in others:
                label(card, f"• {kb.text(o.fault, lang)}  ({o.cf:.2f})", "small").pack(anchor="w")
        self.after_idle(lambda: self.chat.canvas.yview_moveto(1.0))
