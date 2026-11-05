"""Tkinter GUI of the expert system (owner: Lâm). Look and wording: docs/ui_guide.md.

Run from the repository root:
    python src/gui.py

Screens (sidebar, Ctrl+1 ... Ctrl+5):
    1. Chẩn đoán theo triệu chứng  forward chaining, ranked faults, how + inference graph
    2. Hỏi đáp từng câu             backward chaining, yes / no, why, undo
    3. Kiểm chứng Wang              proof of KB + symptoms => fault, compared with forward chaining
    4. Cơ sở tri thức               browse rules, validator report
    5. Giới thiệu                   team, course, how to use
"""

from __future__ import annotations

import datetime as _dt
import sys
import unicodedata
from pathlib import Path
from typing import Callable, Dict, List, Optional

import tkinter as tk
from tkinter import filedialog, ttk

import theme
from cli import format_result
from forward_chaining import DEFAULT_THRESHOLD, forward_chain
from kb import ROOT, KnowledgeBase, load_kb, validate
from present import (backward_step, how_rows, inference_graph, near_misses, short,
                     short_trace, why_rows)
from scenarios import load_scenarios
from theme import COLORS as C
from theme import FONTS as F
from theme import PAD, SEVERITY_TEXT, SUBSYSTEM_COLORS, SUBSYSTEM_NAMES, SUBSYSTEM_ORDER
from wang import check_engines, entails, relevant_rules


K = 1.0  # screen scale (1.25 on a 125 % Windows display); set by App


def px(n: float) -> int:
    """Pixel size scaled to the screen, so the layout looks the same at 100 % and 150 %."""
    return int(round(n * K))


def data_root() -> Path:
    """Repository root, or the unpacked folder when running as a PyInstaller .exe."""
    return Path(getattr(sys, "_MEIPASS", ROOT))


# ---------------------------------------------------------------------------
# Wording (see docs/ui_guide.md, "Cách gọi tên")
# ---------------------------------------------------------------------------

S = {
    "vi": {
        "app": "Chẩn đoán lỗi xe máy",
        "app_sub": "Hệ chuyên gia dựa trên luật · Nhóm 2",
        "sec_diag": "CHẨN ĐOÁN", "sec_check": "LUẬT VÀ CHỨNG MINH", "sec_sys": "KHÁC",
        "nav_forward": "Theo triệu chứng", "nav_backward": "Hỏi đáp từng câu",
        "nav_wang": "Kiểm chứng Wang", "nav_kb": "Cơ sở tri thức",
        "nav_about": "Giới thiệu",
        "lang": "Ngôn ngữ",
        "fw_title": "Chẩn đoán theo triệu chứng",
        "fw_sub": "Chọn loại xe và các triệu chứng đang gặp. Chương trình suy diễn tiến (forward chaining) và xếp hạng lỗi theo độ tin cậy.",
        "input": "Thông tin xe và triệu chứng", "n_selected": "{n} đã chọn",
        "step_vehicle": "1. LOẠI XE", "step_symptoms": "2. TRIỆU CHỨNG",
        "manual": "Xe số", "scooter": "Xe tay ga", "unknown": "Không rõ",
        "fi": "Phun xăng (FI)", "carb": "Bình xăng con",
        "search": "Tìm triệu chứng: còi, phanh, khói…",
        "sample": "Kịch bản mẫu", "sample_pick": "Chọn kịch bản để tải…",
        "diagnose": "Chẩn đoán", "clear": "Xoá hết",
        "results": "Kết quả chẩn đoán", "rules_fired": "{n} luật đã chạy",
        "view_list": "Danh sách", "view_graph": "Sơ đồ suy luận",
        "check_wang": "Kiểm chứng Wang", "save": "Lưu kết quả",
        "empty_fw": "Chọn loại xe và triệu chứng, rồi bấm Chẩn đoán (Ctrl+Enter).\nHoặc tải một kịch bản mẫu ở góc trên bên trái.",
        "no_symptom": "Chưa chọn triệu chứng nào.",
        "confidence": "Độ tin cậy", "action": "Cách xử lý",
        "why_result": "Vì sao ra kết quả này?",
        "no_fault": "Chưa đủ dữ kiện để kết luận lỗi nào (CF ≥ {t:.2f})",
        "derived": "Chương trình đã suy ra được:",
        "check_more": "Bấm để thêm triệu chứng và chẩn đoán lại:",
        "nothing_derived": "Các triệu chứng đã chọn chưa khớp luật nào. Hãy chọn thêm triệu chứng hoặc chuyển sang Hỏi đáp từng câu.",
        "graph_cols": ["Triệu chứng", "Kết luận trung gian", "Lỗi"],
        "graph_empty": "Chưa có kết quả để vẽ sơ đồ.",
        "graph_hint": "Sơ đồ của: {f}. Bấm vào một thẻ lỗi để đổi.",
        "wang_ok": "Wang chứng minh đúng {n} lỗi mà forward chaining suy ra",
        "wang_bad": "Wang và forward chaining khác nhau: {d}",
        "saved": "Đã lưu: {p}",
        "bw_title": "Hỏi đáp từng câu",
        "bw_sub": "Chương trình đặt giả thuyết rồi hỏi để kiểm chứng (backward chaining). Bấm “Tại sao hỏi câu này?” để xem luật đang thử.",
        "where": "Xe đang bị ở bộ phận nào?", "all_parts": "Tất cả (hỏi nhiều câu hơn)",
        "answered": "ĐÃ TRẢ LỜI", "none_yet": "Chưa có câu trả lời.",
        "restart": "Làm lại từ đầu", "undo": "↶ Sửa câu trước",
        "question": "Câu hỏi", "q_meta": "Đã hỏi {q} câu · đã thử {r} luật",
        "q_num": "Câu {n}", "trying": "Đang thử luật",
        "yes": "Có", "no": "Không", "why": "Tại sao hỏi câu này?",
        "why_head": "Mình hỏi vì đang thử các luật sau (luật trong cùng nằm đầu tiên):",
        "why_direct": "Đây là câu hỏi trực tiếp về triệu chứng.",
        "to_prove": "để chứng minh", "IF": "NẾU", "AND": "VÀ", "THEN": "THÌ",
        "keys": "Phím tắt: C = Có · K = Không · W = Tại sao",
        "bw_done": "Đã hỏi xong · {q} câu · {r} luật đã thử",
        "wg_title": "Kiểm chứng bằng thuật toán Wang",
        "wg_sub": "Chứng minh logic: luật + triệu chứng ⇒ lỗi. Không dùng CF. Forward chaining phải suy ra đúng các lỗi mà Wang chứng minh được.",
        "premises": "Giả thiết (lấy từ màn Theo triệu chứng)",
        "no_premise": "Chưa có triệu chứng. Hãy chọn ở màn Theo triệu chứng.",
        "go_forward": "Đi tới màn Theo triệu chứng",
        "goal": "Lỗi cần chứng minh", "prove": "Chứng minh",
        "rel_rules": "Luật liên quan", "proof": "Các bước chứng minh",
        "proved": "Chứng minh được: luật + triệu chứng ⇒ {f}",
        "not_proved": "Không chứng minh được {f} từ các triệu chứng đã cho",
        "sequents": "{n} sequent đã xét",
        "compare": "So sánh với forward chaining",
        "wang_set": "Wang chứng minh", "fc_set": "Forward chaining suy ra",
        "agree": "Khớp nhau", "disagree": "Khác nhau",
        "kb_title": "Cơ sở tri thức",
        "kb_sub": "Toàn bộ luật NẾU … THÌ … của hệ thống, và kết quả bộ kiểm tra luật (kb.validate).",
        "t_sym": "Triệu chứng", "t_int": "Trung gian", "t_fault": "Lỗi", "t_rule": "Luật",
        "t_valid": "Kiểm tra luật", "t_valid_v": "{e} lỗi · {w} cảnh báo",
        "all_sys": "Tất cả bộ phận", "filter": "Lọc theo mã hoặc nội dung…",
        "col_id": "Mã", "col_if": "NẾU", "col_then": "THÌ", "col_cf": "CF", "col_src": "Nguồn",
        "rule_detail": "Chi tiết luật", "pick_rule": "Chọn một luật trong bảng để xem chi tiết.",
        "k_symptom": "triệu chứng", "k_intermediate": "trung gian", "k_fault": "lỗi",
        "source": "Nguồn", "no_source": "chưa có nguồn", "file": "File",
        "used_by": "Luật dùng kết luận này", "warnings": "Cảnh báo của bộ kiểm tra",
        "ab_title": "Giới thiệu",
        "ab_sub": "Đồ án cuối kỳ môn Nhập môn Trí tuệ nhân tạo (261_72ITSE30303_01) · GV: TS. Nguyễn Thanh Huy",
    },
    "en": {
        "app": "Motorbike Fault Diagnosis",
        "app_sub": "Rule-based expert system · Group 2",
        "sec_diag": "DIAGNOSIS", "sec_check": "RULES AND PROOF", "sec_sys": "OTHER",
        "nav_forward": "By symptoms", "nav_backward": "Step-by-step questions",
        "nav_wang": "Wang's algorithm", "nav_kb": "Knowledge base",
        "nav_about": "About",
        "lang": "Language",
        "fw_title": "Diagnosis by symptoms",
        "fw_sub": "Choose the motorbike type and the symptoms. The program runs forward chaining and ranks faults by confidence.",
        "input": "Motorbike and symptoms", "n_selected": "{n} selected",
        "step_vehicle": "1. MOTORBIKE TYPE", "step_symptoms": "2. SYMPTOMS",
        "manual": "Manual", "scooter": "Scooter", "unknown": "Not sure",
        "fi": "Fuel injection (FI)", "carb": "Carburettor",
        "search": "Search symptoms: horn, brake, smoke…",
        "sample": "Sample scenario", "sample_pick": "Choose a scenario to load…",
        "diagnose": "Diagnose", "clear": "Clear all",
        "results": "Diagnosis", "rules_fired": "{n} rules fired",
        "view_list": "List", "view_graph": "Inference graph",
        "check_wang": "Check with Wang", "save": "Save result",
        "empty_fw": "Choose the motorbike type and symptoms, then press Diagnose (Ctrl+Enter).\nOr load a sample scenario at the top left.",
        "no_symptom": "No symptom selected.",
        "confidence": "Confidence", "action": "What to do",
        "why_result": "How was this found?",
        "no_fault": "Not enough evidence for any fault (CF ≥ {t:.2f})",
        "derived": "What the program could work out:",
        "check_more": "Click to add a symptom and diagnose again:",
        "nothing_derived": "The symptoms you chose do not match any rule. Add more symptoms or switch to step-by-step questions.",
        "graph_cols": ["Symptoms", "Intermediate findings", "Fault"],
        "graph_empty": "No result to draw yet.",
        "graph_hint": "Graph of: {f}. Click a fault card to change it.",
        "wang_ok": "Wang proves exactly the {n} fault(s) that forward chaining derived",
        "wang_bad": "Wang and forward chaining differ: {d}",
        "saved": "Saved: {p}",
        "bw_title": "Step-by-step questions",
        "bw_sub": "The program picks a hypothesis and asks questions to check it (backward chaining). Press “Why this question?” to see the rules being tried.",
        "where": "Which part has the problem?", "all_parts": "All parts (more questions)",
        "answered": "ANSWERED", "none_yet": "No answers yet.",
        "restart": "Start again", "undo": "↶ Change last answer",
        "question": "Question", "q_meta": "{q} questions asked · {r} rules tried",
        "q_num": "Question {n}", "trying": "Trying rule",
        "yes": "Yes", "no": "No", "why": "Why this question?",
        "why_head": "I am asking because I am trying these rules (innermost first):",
        "why_direct": "This question is about the symptom itself.",
        "to_prove": "to prove", "IF": "IF", "AND": "AND", "THEN": "THEN",
        "keys": "Keys: Y = Yes · N = No · W = Why",
        "bw_done": "Finished · {q} questions · {r} rules tried",
        "wg_title": "Checking with Wang's algorithm",
        "wg_sub": "A logic proof: rules + symptoms ⇒ fault, without CF. Forward chaining must derive exactly the faults that Wang proves.",
        "premises": "Premises (from the By symptoms screen)",
        "no_premise": "No symptoms yet. Choose them on the By symptoms screen.",
        "go_forward": "Go to By symptoms",
        "goal": "Fault to prove", "prove": "Prove",
        "rel_rules": "Relevant rules", "proof": "Proof steps",
        "proved": "Proved: rules + symptoms ⇒ {f}",
        "not_proved": "{f} cannot be proved from these symptoms",
        "sequents": "{n} sequents examined",
        "compare": "Compared with forward chaining",
        "wang_set": "Wang proves", "fc_set": "Forward chaining derives",
        "agree": "Same", "disagree": "Different",
        "kb_title": "Knowledge base",
        "kb_sub": "Every IF … THEN … rule of the system, and the result of the rule checker (kb.validate).",
        "t_sym": "Symptoms", "t_int": "Intermediates", "t_fault": "Faults", "t_rule": "Rules",
        "t_valid": "Rule check", "t_valid_v": "{e} errors · {w} warnings",
        "all_sys": "All parts", "filter": "Filter by id or text…",
        "col_id": "Id", "col_if": "IF", "col_then": "THEN", "col_cf": "CF", "col_src": "Source",
        "rule_detail": "Rule details", "pick_rule": "Select a rule in the table to see its details.",
        "k_symptom": "symptom", "k_intermediate": "intermediate", "k_fault": "fault",
        "source": "Source", "no_source": "no source yet", "file": "File",
        "used_by": "Rules that use this conclusion", "warnings": "Rule checker warnings",
        "ab_title": "About",
        "ab_sub": "Final project, Introduction to Artificial Intelligence (261_72ITSE30303_01) · Lecturer: Dr. Huy T. Nguyen",
    },
}

ABOUT = {
    "vi": [
        ("Đề tài", "Hệ chuyên gia chẩn đoán các lỗi thường gặp của xe máy. Cơ sở tri thức gồm các luật NẾU … THÌ … "
                   "có hệ số chắc chắn (CF); chương trình suy diễn tiến, suy diễn lùi, giải thích “tại sao” và "
                   "“vì sao”, và kiểm chứng kết luận bằng thuật toán Wang."),
        ("Thành viên", "Tăng Thoại Lâm (nhóm trưởng): định dạng và bộ kiểm tra cơ sở tri thức, CLI, GUI, file .exe\n"
                       "Kiều Bảo Giang: suy diễn tiến, xếp hạng theo CF, thuật toán Wang\n"
                       "Nguyễn Nam Khoa: suy diễn lùi, giải thích why / how, đánh giá"),
        ("Cách dùng", "Theo triệu chứng: chọn loại xe và triệu chứng, bấm Chẩn đoán.\n"
                      "Hỏi đáp từng câu: chọn bộ phận, trả lời Có / Không; bấm Tại sao để xem luật đang thử.\n"
                      "Kết quả chỉ mang tính tham khảo; lỗi “Cần mang ra thợ” nên được kiểm tra tại tiệm."),
        ("Phím tắt", "Ctrl+1 … Ctrl+5: chuyển màn hình · Ctrl+Enter: Chẩn đoán · Ctrl+S: Lưu kết quả\n"
                     "Ở màn Hỏi đáp: C = Có, K = Không, W = Tại sao, Ctrl+Z = sửa câu trước"),
    ],
    "en": [
        ("Project", "An expert system that diagnoses common motorbike faults. The knowledge base holds IF … THEN … "
                    "rules with certainty factors (CF); the program runs forward and backward chaining, explains "
                    "why and how, and checks its conclusions with Wang's algorithm."),
        ("Team", "Tăng Thoại Lâm (leader): knowledge base format and checker, CLI, GUI, .exe\n"
                 "Kiều Bảo Giang: forward chaining, CF ranking, Wang's algorithm\n"
                 "Nguyễn Nam Khoa: backward chaining, why / how explanations, evaluation"),
        ("How to use", "By symptoms: choose the motorbike type and symptoms, press Diagnose.\n"
                       "Step-by-step: choose a part, answer Yes / No; press Why to see the rules being tried.\n"
                       "Results are advice only; faults marked “Take it to a mechanic” should be checked at a workshop."),
        ("Shortcuts", "Ctrl+1 … Ctrl+5: change screen · Ctrl+Enter: Diagnose · Ctrl+S: Save result\n"
                      "Step-by-step screen: Y = Yes, N = No, W = Why, Ctrl+Z = change last answer"),
    ],
}

VEHICLE_SYMPTOMS = {"manual": "is_manual", "scooter": "is_scooter", "fi": "is_fuel_injected",
                    "carb": "is_carburetor"}


def fold(text: str) -> str:
    """Lower case without Vietnamese accents, so "phanh" finds "Phanh" and "con" finds "còi"."""
    text = text.lower().replace("đ", "d")
    return "".join(ch for ch in unicodedata.normalize("NFD", text) if unicodedata.category(ch) != "Mn")


# ---------------------------------------------------------------------------
# Small widgets
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
    autowrap(label(f, subtitle, "body", "muted", bg="bg")).pack(fill="x", pady=(2, 0))
    return f


def tile(parent, caption: str, value: str, note: str = "", color: str = "text") -> tk.Frame:
    f = tk.Frame(parent, bg=C["surface"], highlightthickness=1, highlightbackground=C["border"],
                 padx=16, pady=12)
    label(f, caption.upper(), "small_bold", "muted").pack(anchor="w")
    label(f, value, "display", color).pack(anchor="w")
    label(f, note or " ", "small", "muted").pack(anchor="w")
    return f


# ---------------------------------------------------------------------------
# Result view: ranked fault cards, near misses, and the inference graph
# ---------------------------------------------------------------------------

class ResultView(tk.Frame):
    def __init__(self, parent, app: "App", on_add_symptom: Optional[Callable[[str], None]] = None):
        super().__init__(parent, bg=C["surface"])
        self.app = app
        self.on_add_symptom = on_add_symptom
        self.result = None
        self.selected: Optional[str] = None
        self.mode = "list"
        self.expanded: set = set()

        bar = tk.Frame(self, bg=C["surface"])
        bar.pack(fill="x", padx=14, pady=(10, 0))
        self.toolbar = bar
        self.seg = Segmented(bar, [("list", app.s("view_list")), ("graph", app.s("view_graph"))],
                             "list", self.set_mode)
        self.seg.pack(side="left")
        self.stack = tk.Frame(self, bg=C["surface"])
        self.stack.pack(fill="both", expand=True, pady=(8, 0))
        self.list = ScrollFrame(self.stack)
        self.graph = tk.Canvas(self.stack, bg=C["surface"], highlightthickness=0, bd=0)
        self.graph.bind("<Configure>", lambda e: self.draw_graph())
        self.list.pack(fill="both", expand=True)
        self.empty(app.s("empty_fw"))

    # --- state ---
    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.list.pack_forget()
        self.graph.pack_forget()
        (self.list if mode == "list" else self.graph).pack(fill="both", expand=True)
        if mode == "graph":
            self.draw_graph()

    def empty(self, text: str) -> None:
        self.result = None
        self.list.clear()
        box = tk.Frame(self.list.inner, bg=C["surface"])
        box.pack(fill="both", expand=True, padx=14, pady=40)
        autowrap(label(box, text, "body", "muted")).pack(fill="x")
        self.draw_graph()

    def show(self, result) -> None:
        self.result = result
        self.selected = result.diagnoses[0].fault if result.diagnoses else None
        self.expanded = {self.selected} if self.selected else set()
        self.render()

    def select(self, fault: str) -> None:
        self.selected = fault
        self.render()

    def toggle(self, fault: str) -> None:
        self.expanded ^= {fault}
        self.selected = fault
        self.render()

    # --- drawing ---
    def render(self) -> None:
        lang, kb, result = self.app.lang, self.app.kb, self.result
        y = self.list.canvas.yview()[0]
        self.list.clear()
        inner = self.list.inner
        if not result.diagnoses:
            self.render_near_misses(inner)
        for i, d in enumerate(result.diagnoses[:theme.MAX_RESULTS], 1):
            self.render_card(inner, i, d)
        self.after_idle(lambda: self.list.canvas.yview_moveto(y))
        self.draw_graph()

    def render_card(self, parent, rank: int, d) -> None:
        lang, kb = self.app.lang, self.app.kb
        sel = d.fault == self.selected
        card = tk.Frame(parent, bg=C["surface"], highlightthickness=2 if sel else 1,
                        highlightbackground=C["accent"] if sel else C["border"], padx=14, pady=10)
        card.pack(fill="x", padx=(14, 6), pady=(0, 10))
        head = tk.Frame(card, bg=C["surface"])
        head.pack(fill="x")
        rank_badge(head, rank, rank == 1).pack(side="left")
        name = label(head, kb.text(d.fault, lang), "title")
        name.pack(side="left", padx=(10, 8))
        severity_chip(head, d.severity, lang).pack(side="right")
        cf = tk.Frame(card, bg=C["surface"])
        cf.pack(fill="x", pady=(8, 0))
        label(cf, self.app.s("confidence"), "small", "muted", width=12).pack(side="left")
        label(cf, f"{d.cf:.2f}", "mono_bold").pack(side="right", padx=(8, 0))
        CFBar(cf, d.cf).pack(side="left", fill="x", expand=True)
        autowrap(label(card, kb.action(d.fault, lang), "body")).pack(fill="x", pady=(8, 0))
        open_ = d.fault in self.expanded
        link(card, ("▾ " if open_ else "▸ ") + self.app.s("why_result"),
             lambda f=d.fault: self.toggle(f)).pack(anchor="w", pady=(8, 0))
        if open_:
            how = tk.Frame(card, bg=C["surface"])
            how.pack(fill="x", pady=(4, 0))
            how.columnconfigure(1, weight=1)
            for r, row in enumerate(how_rows(kb, self.result.wm, d.fault, lang)):
                label(how, row.label, "mono_bold" if row.is_rule else "small",
                      "text" if row.is_rule else "muted").grid(row=r, column=0, sticky="nw", padx=(0, 10), pady=1)
                autowrap(label(how, row.text, "small")).grid(row=r, column=1, sticky="we", pady=1)
                label(how, f"{row.cf:.2f}", "mono", "muted").grid(row=r, column=2, sticky="ne", padx=(10, 0))
        for w in [card, head, name]:
            w.bind("<Button-1>", lambda e, f=d.fault: self.select(f))

    def render_near_misses(self, parent) -> None:
        lang, kb = self.app.lang, self.app.kb
        box = tk.Frame(parent, bg=C["warn_soft"], padx=14, pady=12, highlightthickness=1,
                       highlightbackground="#E8D3A6")
        box.pack(fill="x", padx=(14, 6), pady=(0, 10))
        label(box, self.app.s("no_fault").format(t=DEFAULT_THRESHOLD), "heading", "warn", bg="warn_soft").pack(anchor="w")
        misses = near_misses(kb, self.result.wm)
        if not misses:
            autowrap(label(box, self.app.s("nothing_derived"), "body", bg="warn_soft")).pack(fill="x", pady=(6, 0))
            return
        label(box, self.app.s("derived"), "body", bg="warn_soft").pack(anchor="w", pady=(6, 2))
        for m in misses:
            row = tk.Frame(box, bg=C["warn_soft"])
            row.pack(fill="x")
            label(row, m.rule, "mono_bold", bg="warn_soft", width=7).pack(side="left")
            label(row, f"{m.cf:.2f}", "mono", "muted", bg="warn_soft").pack(side="right")
            autowrap(label(row, short(kb, m.symbol, lang), "body", bg="warn_soft")).pack(side="left", fill="x", expand=True)
        missing = list(dict.fromkeys(s for m in misses for _, s in m.missing))
        if missing:
            label(box, self.app.s("check_more"), "body", bg="warn_soft").pack(anchor="w", pady=(8, 2))
            for s in missing:
                text = "+ " + short(self.app.kb, s, lang)
                if self.on_add_symptom:
                    autowrap(link(box, text, lambda s=s: self.on_add_symptom(s), bg="warn_soft",
                                  font="body")).pack(fill="x", pady=1)
                else:
                    autowrap(label(box, "• " + text[2:], "body", bg="warn_soft")).pack(fill="x", pady=1)

    def draw_graph(self) -> None:
        cv = self.graph
        if self.mode != "graph":
            return
        cv.delete("all")
        w, h = cv.winfo_width(), cv.winfo_height()
        if w < 50:
            return
        lang, kb = self.app.lang, self.app.kb
        if not self.result or not self.selected:
            cv.create_text(w / 2, h / 2, text=self.app.s("graph_empty"), font=F["body"], fill=C["muted"])
            return
        nodes, edges = inference_graph(kb, self.result.wm, self.selected)
        cols = max(n.column for n in nodes) + 1
        cv.create_text(px(14), px(14), anchor="w", font=F["small"], fill=C["muted"],
                       text=self.app.s("graph_hint").format(f=kb.text(self.selected, lang)))
        margin, top = px(14), px(56)
        gapx = px(104)
        boxw = min(px(250), (w - 2 * margin - gapx * (cols - 1)) / cols)
        offset = (w - 2 * margin - (cols * boxw + (cols - 1) * gapx)) / 2
        xs = [margin + offset + c * (boxw + gapx) for c in range(cols)]
        names = self.app.s("graph_cols")
        for c in range(cols):
            title = names[0] if c == 0 else names[2] if c == cols - 1 else names[1]
            cv.create_text(xs[c], px(40), anchor="w", text=title.upper(), font=F["small_bold"], fill=C["muted"])
        by_col: Dict[int, list] = {}
        for n in nodes:
            by_col.setdefault(n.column, []).append(n)
        pos = {}
        style = {"symptom": (C["surface"], C["border"], C["text"]),
                 "intermediate": (C["accent_soft"], C["accent"], C["text"]),
                 "fault": (C["accent"], C["accent"], C["on_accent"])}
        boxes = []
        for c, col in by_col.items():
            sizes = []
            for n in col:  # measure the wrapped text first
                t = cv.create_text(0, 0, text=short(kb, n.symbol, lang), width=boxw - px(20),
                                   font=F["small_bold"], anchor="nw")
                x1, y1, x2, y2 = cv.bbox(t)
                cv.delete(t)
                sizes.append(y2 - y1 + px(34))
            gap = px(16)
            total = sum(sizes) + gap * (len(col) - 1)
            y = max(top, top + (h - top - px(16) - total) / 2)
            for n, bh in zip(col, sizes):
                pos[n.symbol] = (xs[c], y, xs[c] + boxw, y + bh)
                boxes.append((n, xs[c], y, bh))
                y += bh + gap
        labelled = set()
        for e in edges:  # edges under the boxes
            sx1, sy1, sx2, sy2 = pos[e.source]
            tx1, ty1, tx2, ty2 = pos[e.target]
            ax, ay, bx, by = sx2, (sy1 + sy2) / 2, tx1, (ty1 + ty2) / 2
            mx = bx - gapx / 2
            cv.create_line(ax, ay, mx - px(14), ay, mx, by, bx - 2, by, smooth=True, width=1.5,
                           fill=C["muted"], arrow="last", arrowshape=(8, 9, 3))
            if (e.rule, e.target) not in labelled:
                labelled.add((e.rule, e.target))
                rule = kb.rule(e.rule)
                k = sum(1 for r, t_ in labelled if t_ == e.target) - 1
                lx, ly = bx - gapx / 2, by - px(22) * k
                t = cv.create_text(lx, ly, text=f"{e.rule} · {rule.cf:.2f}", font=F["mono_bold"], fill=C["accent"])
                x1, y1, x2, y2 = cv.bbox(t)
                round_rect(cv, x1 - 5, y1 - 2, x2 + 5, y2 + 2, 6, fill=C["surface"], outline=C["accent"])
                cv.tag_raise(t)
        for n, x, y, bh in boxes:
            fill, outline, fg = style[n.kind]
            round_rect(cv, x, y, x + boxw, y + bh, px(10), fill=fill, outline=outline, width=1.5)
            cv.create_text(x + px(10), y + px(8), text=short(kb, n.symbol, lang), width=boxw - px(20), anchor="nw",
                           font=F["small_bold"] if n.kind != "symptom" else F["small"], fill=fg)
            cv.create_text(x + boxw - px(10), y + bh - px(10), text=f"CF {n.cf:.2f}", anchor="e", font=F["mono"],
                           fill=fg if n.kind == "fault" else C["muted"])


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

class Page(tk.Frame):
    def __init__(self, parent, app: "App"):
        super().__init__(parent, bg=C["bg"])
        self.app = app

    def on_show(self) -> None:
        pass


class ForwardPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        s, kb, st = app.s, app.kb, app.state
        page_header(self, s("fw_title"), s("fw_sub")).pack(fill="x", pady=(0, PAD["m"]))
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        # --- left: input ---
        left = Panel(body, s("input"), footer=True)
        left.pack(side="left", fill="y")
        left.configure(width=px(theme.LEFT_COLUMN_WIDTH))
        left.pack_propagate(False)
        b = tk.Frame(left.body, bg=C["surface"], padx=14, pady=10)
        b.pack(fill="x")
        label(b, s("sample"), "small_bold", "muted").pack(anchor="w")
        self.scenarios = app.scenarios
        values = [f"{sc.id} · {sc.description.get(app.lang, '')}" for sc in self.scenarios]
        self.sample = ttk.Combobox(b, values=values, state="readonly", font=F["small"])
        self.sample.set(s("sample_pick"))
        self.sample.pack(fill="x", pady=(2, 10))
        self.sample.bind("<<ComboboxSelected>>", lambda e: app.load_scenario(self.scenarios[self.sample.current()]))

        label(b, s("step_vehicle"), "small_bold", "muted").pack(anchor="w")
        self.vtype = tk.StringVar(value=st["vehicle"].get("type", ""))
        self.vfuel = tk.StringVar(value=st["vehicle"].get("fuel", ""))
        for var, opts in ((self.vtype, ("manual", "scooter", "")), (self.vfuel, ("fi", "carb", ""))):
            row = tk.Frame(b, bg=C["surface"])
            row.pack(fill="x", pady=(4, 0))
            for o in opts:
                ttk.Radiobutton(row, text=s(o or "unknown"), value=o, variable=var,
                                command=self.sync).pack(side="left", padx=(0, 12))
        label(b, s("step_symptoms"), "small_bold", "muted").pack(anchor="w", pady=(12, 4))
        self.query = HintEntry(b, s("search"), lambda: self.filter())
        self.query.pack(fill="x")

        self.list = ScrollFrame(left.body)
        self.list.pack(fill="both", expand=True, padx=(14, 0), pady=(0, 6))
        self.vars: Dict[str, tk.BooleanVar] = {}
        self.items: Dict[str, tk.Widget] = {}
        self.groups = []
        for sub in SUBSYSTEM_ORDER:
            ids = sorted((sid for sid, sym in kb.symptoms.items() if sym.subsystem == sub),
                         key=lambda x: short(kb, x, app.lang))
            head = tk.Frame(self.list.inner, bg=C["surface"])
            dot(head, SUBSYSTEM_COLORS[sub]).pack(side="left", padx=(0, 7))
            label(head, SUBSYSTEM_NAMES[app.lang][sub], "small_bold").pack(side="left")
            count = label(head, "", "small", "muted")
            count.pack(side="right", padx=8)
            rows = []
            for sid in ids:
                var = tk.BooleanVar(value=sid in st["selected"])
                self.vars[sid] = var
                cb = tk.Checkbutton(self.list.inner, text=short(kb, sid, app.lang), variable=var,
                                    command=self.sync, font=F["body"], bg=C["surface"], fg=C["text"],
                                    activebackground=C["surface"], selectcolor=C["surface"], anchor="w",
                                    justify="left", wraplength=px(280), bd=0, highlightthickness=0,
                                    cursor="hand2")
                hint = kb.symbols[sid].hint.get(app.lang)
                rows.append((sid, cb, fold(kb.question(sid, app.lang) + " " + (hint or "") + " " + sid)))
            self.groups.append((sub, head, count, rows))
        self.filter()

        ttk.Button(left.foot, text=s("diagnose"), style="Primary.TButton", command=self.run).pack(
            side="left", padx=(14, 8), pady=10)
        ttk.Button(left.foot, text=s("clear"), style="Secondary.TButton", command=self.clear).pack(side="left")
        self.left = left

        # --- right: results ---
        right = Panel(body, s("results"))
        right.pack(side="left", fill="both", expand=True, padx=(PAD["m"], 0))
        self.right = right
        self.view = ResultView(right.body, app, on_add_symptom=self.add_symptom)
        self.view.pack(fill="both", expand=True)
        ttk.Button(self.view.toolbar, text=s("save"), style="Secondary.TButton",
                   command=self.save).pack(side="right")
        ttk.Button(self.view.toolbar, text=s("check_wang"), style="Link.TButton",
                   command=self.check_wang).pack(side="right", padx=8)
        self.status = label(right, "", "small", "muted", bg="chrome", padx=14, pady=6)
        self.sync(update_only=True)
        if st.get("forward"):
            self.view.show(st["forward"])
            self.right.meta.configure(text=st.get("forward_meta", ""))

    def filter(self) -> None:
        if not hasattr(self, "groups"):
            return
        q = fold(self.query.value().strip())
        for sub, head, count, rows in self.groups:
            head.pack_forget()
            for _, cb, _ in rows:
                cb.pack_forget()
        for sub, head, count, rows in self.groups:
            shown = [(sid, cb) for sid, cb, key in rows if all(w in key for w in q.split())]
            if not shown:
                continue
            head.pack(fill="x", pady=(10, 4))
            for sid, cb in shown:
                cb.pack(fill="x", padx=(2, 0), pady=1)
        self.list.to_top()

    def sync(self, update_only: bool = False) -> None:
        st = self.app.state
        st["selected"] = {sid for sid, v in self.vars.items() if v.get()}
        st["vehicle"] = {"type": self.vtype.get(), "fuel": self.vfuel.get()}
        for sub, head, count, rows in self.groups:
            n = sum(1 for sid, _, _ in rows if self.vars[sid].get())
            count.configure(text=f"{n} / {len(rows)}", fg=C["accent"] if n else C["muted"])
        self.left.meta.configure(text=self.app.s("n_selected").format(n=len(st["selected"])))

    def clear(self) -> None:
        for v in self.vars.values():
            v.set(False)
        self.vtype.set("")
        self.vfuel.set("")
        self.sync()
        self.app.state["forward"] = None
        self.view.empty(self.app.s("empty_fw"))
        self.right.meta.configure(text="")
        self.set_status("")

    def add_symptom(self, sid: str) -> None:
        self.vars[sid].set(True)
        self.sync()
        self.run()

    def run(self) -> None:
        app = self.app
        symptoms = app.current_symptoms()
        if not app.state["selected"]:
            self.view.empty(app.s("no_symptom"))
            return
        result = forward_chain(app.kb, symptoms)
        app.state["forward"] = result
        fired = ", ".join(r.id for r in result.fired)
        meta = app.s("rules_fired").format(n=result.rules_fired) + (f" · {fired}" if fired else "")
        app.state["forward_meta"] = meta
        self.right.meta.configure(text=meta)
        self.view.show(result)
        self.set_status("")

    def set_status(self, text: str, fg: str = "muted") -> None:
        self.status.configure(text=text, fg=C[fg])
        if text:
            self.status.pack(fill="x", side="bottom", before=self.right.body)
        else:
            self.status.pack_forget()

    def check_wang(self) -> None:
        app = self.app
        if not app.state["selected"]:
            return
        check = check_engines(app.kb, "gui", app.current_symptoms())
        if check.agree:
            self.set_status("✓ " + app.s("wang_ok").format(n=len(check.wang)), "ok")
        else:
            diff = ", ".join(sorted(check.wang ^ check.forward))
            self.set_status("✕ " + app.s("wang_bad").format(d=diff), "danger")

    def save(self) -> None:
        app = self.app
        result = app.state.get("forward")
        if not result:
            return
        path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile="chan_doan.txt",
                                            filetypes=[("Text", "*.txt")])
        if not path:
            return
        lines = [app.s("app"), _dt.datetime.now().strftime("%d/%m/%Y %H:%M"), ""]
        lines += [f"- {app.kb.question(sid, app.lang)}" for sid in app.current_symptoms()]
        lines += [""] + format_result(app.kb, result, app.lang, DEFAULT_THRESHOLD,
                                      app.state.get("forward_meta", ""))
        Path(path).write_text("\n".join(lines), encoding="utf-8")
        self.set_status(app.s("saved").format(p=path))


class BackwardPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        s, st = app.s, app.state
        page_header(self, s("bw_title"), s("bw_sub")).pack(fill="x", pady=(0, PAD["m"]))
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)

        left = Panel(body, s("where"), footer=True)
        left.pack(side="left", fill="y")
        left.configure(width=px(theme.LEFT_COLUMN_WIDTH))
        left.pack_propagate(False)
        b = tk.Frame(left.body, bg=C["surface"], padx=14, pady=10)
        b.pack(fill="x")
        self.part = tk.StringVar(value=st["bw_part"])
        for key in ["all"] + SUBSYSTEM_ORDER:
            row = tk.Frame(b, bg=C["surface"])
            row.pack(fill="x", pady=1)
            ttk.Radiobutton(row, text=s("all_parts") if key == "all" else SUBSYSTEM_NAMES[app.lang][key],
                            value=key, variable=self.part, command=self.change_part).pack(side="left")
            if key != "all":
                dot(row, SUBSYSTEM_COLORS[key]).pack(side="right", padx=4)
        label(left.body, s("answered"), "small_bold", "muted").pack(anchor="w", padx=14, pady=(8, 4))
        self.answered = ScrollFrame(left.body)
        self.answered.pack(fill="both", expand=True, padx=(14, 0), pady=(0, 6))
        ttk.Button(left.foot, text=s("restart"), style="Secondary.TButton", command=self.restart).pack(
            side="left", padx=(14, 8), pady=10)
        ttk.Button(left.foot, text=s("undo"), style="Link.TButton", command=self.undo).pack(side="left")

        right = Panel(body, s("question"))
        right.pack(side="left", fill="both", expand=True, padx=(PAD["m"], 0))
        self.right = right
        self.qframe = tk.Frame(right.body, bg=C["surface"])
        self.view = ResultView(right.body, app)
        self.show_why = False
        self.step()

    @property
    def answers(self) -> dict:
        return self.app.state["bw_answers"]

    def goals(self):
        part = self.part.get()
        if part == "all":
            return None
        return sorted(f for f, sym in self.app.kb.faults.items() if sym.subsystem == part)

    def change_part(self) -> None:
        self.app.state["bw_part"] = self.part.get()
        self.restart()

    def restart(self) -> None:
        self.answers.clear()
        self.step()

    def undo(self) -> None:
        if self.answers:
            self.answers.pop(next(reversed(self.answers)))
            self.step()

    def answer(self, value: bool) -> None:
        if self.current:
            self.answers[self.current] = value
            self.show_why = False
            self.step()

    def toggle_why(self) -> None:
        self.show_why = not self.show_why
        self.step()

    def key(self, ch: str) -> None:
        if not self.current:
            return
        if ch in "cy":
            self.answer(True)
        elif ch in "kn":
            self.answer(False)
        elif ch == "w":
            self.toggle_why()

    def step(self) -> None:
        app, s, kb, lang = self.app, self.app.s, self.app.kb, self.app.lang
        st = backward_step(kb, self.answers, self.goals())
        self.current = st.question
        q = len(self.answers)
        # answered list
        self.answered.clear()
        if not self.answers:
            label(self.answered.inner, s("none_yet"), "small", "muted").pack(anchor="w")
        for sid, v in self.answers.items():
            row = tk.Frame(self.answered.inner, bg=C["surface"])
            row.pack(fill="x", pady=2)
            label(row, s("yes") if v else s("no"), "small_bold", "ok" if v else "danger", width=6).pack(side="left", anchor="n")
            autowrap(label(row, short(kb, sid, lang), "small")).pack(side="left", fill="x", expand=True)
        self.answered.after_idle(lambda: self.answered.canvas.yview_moveto(1.0))

        self.qframe.pack_forget()
        self.view.pack_forget()
        for w in self.qframe.winfo_children():
            w.destroy()
        if not st.question:
            self.right.title.configure(text=s("results"))
            self.right.meta.configure(text=s("bw_done").format(q=q, r=st.rules_tried))
            self.view.pack(fill="both", expand=True)
            self.view.show(st.result)
            return
        self.right.title.configure(text=s("question"))
        self.right.meta.configure(text=s("q_meta").format(q=q, r=st.rules_tried))
        self.qframe.pack(fill="both", expand=True, padx=14, pady=14)
        card = tk.Frame(self.qframe, bg=C["surface"], highlightthickness=2, highlightbackground=C["accent"],
                        padx=20, pady=18)
        card.pack(fill="x")
        meta = tk.Frame(card, bg=C["surface"])
        meta.pack(fill="x")
        label(meta, s("q_num").format(n=q + 1), "small_bold", "accent").pack(side="left")
        if st.chain:
            label(meta, f"  ·  {s('trying')} ", "small", "muted").pack(side="left")
            label(meta, st.chain[-1].rule.id, "mono_bold", "accent").pack(side="left")
            sub = kb.symbols[st.chain[0].goal].subsystem
            label(meta, SUBSYSTEM_NAMES[lang].get(sub, sub), "small", "muted").pack(side="right")
            dot(meta, SUBSYSTEM_COLORS.get(sub, C["muted"])).pack(side="right", padx=6)
        autowrap(label(card, kb.question(st.question, lang), "question")).pack(fill="x", pady=(10, 4))
        hint = kb.symbols[st.question].hint.get(lang)
        if hint:
            autowrap(label(card, hint, "small", "muted")).pack(fill="x")
        btns = tk.Frame(card, bg=C["surface"])
        btns.pack(fill="x", pady=(14, 0))
        ttk.Button(btns, text=s("yes"), style="Yes.TButton", width=10,
                   command=lambda: self.answer(True)).pack(side="left")
        ttk.Button(btns, text=s("no"), style="No.TButton", width=10,
                   command=lambda: self.answer(False)).pack(side="left", padx=8)
        ttk.Button(btns, text=s("why"), style="Link.TButton", command=self.toggle_why).pack(side="left")
        label(card, s("keys"), "small", "muted").pack(anchor="w", pady=(10, 0))
        if self.show_why:
            why = tk.Frame(self.qframe, bg=C["accent_soft"], padx=16, pady=12)
            why.pack(fill="x", pady=(12, 0))
            rows = why_rows(kb, st.chain, lang)
            label(why, s("why_head") if rows else s("why_direct"), "small_bold", "accent",
                  bg="accent_soft").pack(anchor="w", pady=(0, 6))
            for r in rows:
                line = tk.Frame(why, bg=C["accent_soft"])
                line.pack(fill="x", pady=3)
                label(line, r.rule, "mono_bold", bg="accent_soft", width=6).pack(side="left", anchor="n")
                text = (f"{s('IF')} " + f" {s('AND')} ".join(r.premises) + f" {s('THEN')} {r.conclusion}"
                        f"   ({s('to_prove')}: {r.goal})")
                autowrap(label(line, text, "small", bg="accent_soft")).pack(side="left", fill="x", expand=True)


class WangPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        s = app.s
        page_header(self, s("wg_title"), s("wg_sub")).pack(fill="x", pady=(0, PAD["m"]))
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True)
        left = Panel(body, s("premises"))
        left.pack(side="left", fill="y")
        left.configure(width=px(theme.LEFT_COLUMN_WIDTH))
        left.pack_propagate(False)
        self.left = left
        self.lbody = tk.Frame(left.body, bg=C["surface"], padx=14, pady=10)
        self.lbody.pack(fill="both", expand=True)
        right = Panel(body, s("proof"))
        right.pack(side="left", fill="both", expand=True, padx=(PAD["m"], 0))
        self.right = right
        self.banner = tk.Frame(right.body, bg=C["surface"])
        self.banner.pack(fill="x", padx=14, pady=(12, 0))
        txt = tk.Frame(right.body, bg=C["surface"])
        txt.pack(fill="both", expand=True, padx=14, pady=12)
        self.text = tk.Text(txt, font=F["mono"], wrap="word", bg=C["bg"], fg=C["text"], bd=0,
                            highlightthickness=0, padx=12, pady=10, spacing1=1, spacing3=1)
        ys = ttk.Scrollbar(txt, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=ys.set)
        ys.pack(side="right", fill="y")
        self.text.pack(fill="both", expand=True)
        for d in range(40):
            self.text.tag_configure(f"d{d}", lmargin1=px(18) * d, lmargin2=px(18) * d + px(28))
        self.text.tag_configure("gap", spacing3=px(8))
        self.text.tag_configure("axiom", foreground=C["ok"])
        self.text.tag_configure("fail", foreground=C["danger"])
        self.text.tag_configure("note", foreground=C["muted"])

    def on_show(self) -> None:
        app, s, kb, lang = self.app, self.app.s, self.app.kb, self.app.lang
        for w in self.lbody.winfo_children():
            w.destroy()
        symptoms = app.current_symptoms()
        if not app.state["selected"]:
            autowrap(label(self.lbody, s("no_premise"), "body", "muted")).pack(fill="x")
            ttk.Button(self.lbody, text=s("go_forward"), style="Secondary.TButton",
                       command=lambda: app.show("forward")).pack(anchor="w", pady=10)
            self.text.configure(state="normal")
            self.text.delete("1.0", "end")
            self.text.configure(state="disabled")
            for w in self.banner.winfo_children():
                w.destroy()
            return
        chips = ScrollFrame(self.lbody)
        chips.configure(height=px(150))
        chips.pack(fill="x")
        chips.pack_propagate(False)
        for sid in symptoms:
            row = tk.Frame(chips.inner, bg=C["surface"])
            row.pack(fill="x", pady=1)
            label(row, "•", "small", "accent").pack(side="left", anchor="n")
            autowrap(label(row, short(kb, sid, lang), "small")).pack(side="left", fill="x", expand=True, padx=4)
        label(self.lbody, s("goal"), "small_bold", "muted").pack(anchor="w", pady=(12, 2))
        fw = app.state.get("forward")
        first = [d.fault for d in fw.diagnoses] if fw else []
        order = first + sorted((f for f in kb.faults if f not in first), key=lambda f: kb.text(f, lang))
        self.fault_ids = order
        self.goal = ttk.Combobox(self.lbody, values=[kb.text(f, lang) for f in order], state="readonly")
        self.goal.current(0)
        self.goal.pack(fill="x")
        self.goal.bind("<<ComboboxSelected>>", lambda e: self.prove())
        ttk.Button(self.lbody, text=s("prove"), style="Primary.TButton", command=self.prove).pack(anchor="w", pady=10)
        label(self.lbody, s("rel_rules"), "small_bold", "muted").pack(anchor="w", pady=(4, 2))
        self.rel = ScrollFrame(self.lbody)
        self.rel.pack(fill="both", expand=True)
        self.prove()

    def prove(self) -> None:
        app, s, kb, lang = self.app, self.app.s, self.app.kb, self.app.lang
        fault = self.fault_ids[self.goal.current()]
        symptoms = app.current_symptoms()
        proof = entails(kb, symptoms, fault, trace=True)
        check = check_engines(kb, "gui", symptoms)
        # relevant rules
        self.rel.clear()
        for r in relevant_rules(kb, fault):
            row = tk.Frame(self.rel.inner, bg=C["surface"])
            row.pack(fill="x", pady=1)
            label(row, r.id, "mono_bold", width=5).pack(side="left", anchor="n")
            autowrap(label(row, " ∧ ".join(r.premises) + " → " + r.conclusion, "mono", "muted")).pack(
                side="left", fill="x", expand=True)
        # banner
        for w in self.banner.winfo_children():
            w.destroy()
        ok = proof.valid
        top = tk.Frame(self.banner, bg=C["ok_soft"] if ok else C["danger_soft"], padx=14, pady=10)
        top.pack(fill="x")
        bgk = "ok_soft" if ok else "danger_soft"
        label(top, ("✓ " if ok else "✕ ") + (s("proved") if ok else s("not_proved")).format(f=kb.text(fault, lang)),
              "heading", "ok" if ok else "danger", bg=bgk).pack(side="left")
        label(top, s("sequents").format(n=proof.steps), "small", "muted", bg=bgk).pack(side="right")
        cmp_ = tk.Frame(self.banner, bg=C["surface"])
        cmp_.pack(fill="x", pady=(8, 0))
        names = lambda fs: ", ".join(kb.text(f, lang) for f in sorted(fs)) or "—"
        top2 = tk.Frame(cmp_, bg=C["surface"])
        top2.pack(fill="x")
        label(top2, s("compare"), "small_bold", "muted").pack(side="left")
        fg, bg = (C["ok"], C["ok_soft"]) if check.agree else (C["danger"], C["danger_soft"])
        chip(top2, s("agree") if check.agree else s("disagree"), fg, bg).pack(side="left", padx=8)
        grid = tk.Frame(cmp_, bg=C["surface"])
        grid.pack(fill="x", pady=(4, 0))
        grid.columnconfigure(1, weight=1)
        for i, (k, fs) in enumerate(((s("wang_set"), check.wang), (s("fc_set"), check.forward))):
            label(grid, k, "small", "muted").grid(row=i, column=0, sticky="nw", padx=(0, 10))
            autowrap(label(grid, names(fs), "small")).grid(row=i, column=1, sticky="we")
        # trace
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        for line in short_trace(kb, proof.trace):
            stripped = line.lstrip(" ")
            depth = f"d{min(39, (len(line) - len(stripped)) // 2)}"
            body, _, note = stripped.partition("    [")
            tag = "axiom" if note.startswith("axiom") else "fail" if ("not valid" in note or "no rule" in note) else None
            self.text.insert("end", body + "\n", (depth,) + ((tag,) if tag else ()))
            if note:
                self.text.insert("end", "[" + note + "\n", (depth, "gap", tag or "note"))
        self.text.configure(state="disabled")


class KBPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        s, kb, lang = app.s, app.kb, app.lang
        page_header(self, s("kb_title"), s("kb_sub")).pack(fill="x", pady=(0, PAD["m"]))
        report = validate(kb)
        self.report = report
        tiles = tk.Frame(self, bg=C["bg"])
        tiles.pack(fill="x")
        for i, (cap, val, note, color) in enumerate((
                (s("t_sym"), len(kb.symptoms), "", "text"), (s("t_int"), len(kb.intermediates), "", "text"),
                (s("t_fault"), len(kb.faults), "", "text"), (s("t_rule"), len(kb.rules), "", "accent"),
                (s("t_valid"), "✓" if report.ok else "✕",
                 s("t_valid_v").format(e=len(report.errors), w=len(report.warnings)),
                 "ok" if report.ok else "danger"))):
            tile(tiles, cap, str(val), note, color).pack(side="left", fill="x", expand=True,
                                                         padx=(0 if i == 0 else PAD["m"], 0))
        body = tk.Frame(self, bg=C["bg"])
        body.pack(fill="both", expand=True, pady=(PAD["m"], 0))
        left = tk.Frame(body, bg=C["surface"], highlightthickness=1, highlightbackground=C["border"])
        left.pack(side="left", fill="both", expand=True)
        bar = tk.Frame(left, bg=C["surface"], padx=12, pady=10)
        bar.pack(fill="x")
        self.subs = ["all"] + SUBSYSTEM_ORDER
        self.sub = ttk.Combobox(bar, state="readonly", width=24,
                                values=[s("all_sys")] + [SUBSYSTEM_NAMES[lang][x] for x in SUBSYSTEM_ORDER])
        self.sub.current(0)
        self.sub.pack(side="left")
        self.sub.bind("<<ComboboxSelected>>", lambda e: self.fill())
        self.q = HintEntry(bar, s("filter"), lambda: self.fill() if hasattr(self, "tree") else None)
        self.q.pack(side="left", fill="x", expand=True, padx=(8, 0))
        cols = ("id", "if", "then", "cf", "src")
        self.tree = ttk.Treeview(left, columns=cols, show="headings", selectmode="browse")
        for c, key, wdt, anchor in (("id", "col_id", 60, "w"), ("if", "col_if", 330, "w"),
                                    ("then", "col_then", 200, "w"), ("cf", "col_cf", 50, "center"),
                                    ("src", "col_src", 60, "center")):
            self.tree.heading(c, text=s(key), anchor=anchor)
            self.tree.column(c, width=wdt, anchor=anchor, stretch=c in ("if", "then"))
        ys = ttk.Scrollbar(left, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=ys.set)
        ys.pack(side="right", fill="y")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda e: self.detail())
        right = Panel(body, s("rule_detail"))
        right.pack(side="left", fill="y", padx=(PAD["m"], 0))
        right.configure(width=px(350))
        right.pack_propagate(False)
        self.dbody = ScrollFrame(right.body)
        self.dbody.pack(fill="both", expand=True, padx=(14, 0), pady=10)
        self.fill()
        self.detail()

    def fill(self) -> None:
        kb, lang = self.app.kb, self.app.lang
        sub = self.subs[self.sub.current()]
        q = fold(self.q.value().strip())
        self.tree.delete(*self.tree.get_children())
        for r in kb.rules:
            if sub != "all" and r.subsystem != sub:
                continue
            ifs = " + ".join(short(kb, p, lang) for p in r.premises)
            then = short(kb, r.conclusion, lang)
            if q and q not in fold(f"{r.id} {ifs} {then} {' '.join(r.premises)} {r.conclusion}"):
                continue
            self.tree.insert("", "end", iid=r.id, values=(r.id, ifs, then, f"{r.cf:.2f}", "✓" if r.source else "—"))

    def detail(self) -> None:
        app, s, kb, lang = self.app, self.app.s, self.app.kb, self.app.lang
        self.dbody.clear()
        d = self.dbody.inner
        sel = self.tree.selection()
        if not sel:
            autowrap(label(d, s("pick_rule"), "body", "muted")).pack(fill="x")
            if self.report.warnings:
                label(d, s("warnings"), "small_bold", "muted").pack(anchor="w", pady=(16, 4))
                for w in self.report.warnings:
                    autowrap(label(d, "• " + w, "small", "warn")).pack(fill="x", pady=1)
            return
        r = kb.rule(sel[0])
        head = tk.Frame(d, bg=C["surface"])
        head.pack(fill="x")
        label(head, r.id, "display", "accent").pack(side="left")
        dot(head, SUBSYSTEM_COLORS.get(r.subsystem, C["muted"])).pack(side="right", padx=(6, 8))
        label(head, SUBSYSTEM_NAMES[lang].get(r.subsystem, r.subsystem), "small", "muted").pack(side="right")

        def block(title, symbols):
            label(d, title, "small_bold", "muted").pack(anchor="w", pady=(12, 4))
            for sym in symbols:
                row = tk.Frame(d, bg=C["surface"], highlightthickness=1, highlightbackground=C["border"],
                               padx=10, pady=6)
                row.pack(fill="x", pady=2, padx=(0, 8))
                kind = kb.symbols[sym].kind
                fg, bg = {"symptom": (C["muted"], C["chrome"]), "intermediate": (C["accent"], C["accent_soft"]),
                          "fault": (C["on_accent"], C["accent"])}[kind]
                chip(row, s("k_" + kind), fg, bg).pack(anchor="w")
                autowrap(label(row, short(kb, sym, lang), "body")).pack(fill="x", pady=(3, 0))
                label(row, sym, "mono", "muted").pack(anchor="w")

        block(s("IF"), r.premises)
        block(s("THEN"), [r.conclusion])
        cf = tk.Frame(d, bg=C["surface"])
        cf.pack(fill="x", pady=(12, 0), padx=(0, 8))
        label(cf, "CF", "small_bold", "muted", width=4).pack(side="left")
        label(cf, f"{r.cf:.2f}", "mono_bold").pack(side="right", padx=(8, 0))
        CFBar(cf, r.cf).pack(side="left", fill="x", expand=True)
        label(d, s("source"), "small_bold", "muted").pack(anchor="w", pady=(12, 2))
        autowrap(label(d, r.source or s("no_source"), "small", "text" if r.source else "warn")).pack(fill="x")
        label(d, f"{s('file')}: knowledge_base/{r.file}", "mono", "muted").pack(anchor="w", pady=(6, 0))
        users = kb.rules_using(r.conclusion)
        if users:
            label(d, s("used_by"), "small_bold", "muted").pack(anchor="w", pady=(12, 2))
            row = tk.Frame(d, bg=C["surface"])
            row.pack(fill="x")
            for u in users:
                link(row, u.id, lambda u=u: self.goto(u.id), font="mono_bold").pack(side="left", padx=(0, 10))

    def goto(self, rule_id: str) -> None:
        if not self.tree.exists(rule_id):
            self.sub.current(0)
            self.q.clear()
            self.fill()
        self.tree.selection_set(rule_id)
        self.tree.see(rule_id)


class AboutPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        s, kb = app.s, app.kb
        page_header(self, s("ab_title"), s("ab_sub")).pack(fill="x", pady=(0, PAD["m"]))
        box = tk.Frame(self, bg=C["surface"], highlightthickness=1, highlightbackground=C["border"],
                       padx=24, pady=16)
        box.pack(fill="both", expand=True)
        box.columnconfigure(1, weight=1)
        for i, (k, v) in enumerate(ABOUT[app.lang]):
            label(box, k, "heading", "accent").grid(row=i, column=0, sticky="nw", padx=(0, 24), pady=10)
            autowrap(label(box, v, "body")).grid(row=i, column=1, sticky="we", pady=10)
        label(box, kb.summary(), "mono", "muted").grid(row=len(ABOUT[app.lang]), column=0, columnspan=2,
                                                      sticky="w", pady=(16, 0))


# ---------------------------------------------------------------------------
# Application shell: sidebar + pages
# ---------------------------------------------------------------------------

NAV = [
    ("sec_diag", [("forward", "nav_forward", ForwardPage), ("backward", "nav_backward", BackwardPage)]),
    ("sec_check", [("wang", "nav_wang", WangPage), ("kb", "nav_kb", KBPage)]),
    ("sec_sys", [("about", "nav_about", AboutPage)]),
]
PAGES = [item for _, items in NAV for item in items]


class App:
    def __init__(self, root: tk.Tk, lang: str = "vi"):
        self.root = root
        self.lang = lang
        self.kb: KnowledgeBase = load_kb(data_root() / "knowledge_base")
        try:
            self.scenarios = load_scenarios(data_root() / "scenarios")
        except (OSError, ValueError, KeyError):
            self.scenarios = []
        self.state = {"selected": set(), "vehicle": {}, "forward": None, "forward_meta": "",
                      "bw_answers": {}, "bw_part": "all", "page": "forward"}
        global K
        K = max(1.0, root.winfo_fpixels("1i") / 96)
        theme.apply(root)
        root.title(self.s("app"))
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        w = min(px(theme.WINDOW_SIZE[0]), int(sw * 0.94))
        h = min(px(theme.WINDOW_SIZE[1]), int(sh * 0.88))
        root.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+{max(0, (sh - h) // 3)}")
        root.minsize(min(px(theme.WINDOW_MIN_SIZE[0]), w), min(px(theme.WINDOW_MIN_SIZE[1]), h))
        root.bind_all("<MouseWheel>", self._wheel)
        root.bind("<Control-Return>", lambda e: self.page_call("forward", "run"))
        root.bind("<Control-s>", lambda e: self.page_call("forward", "save"))
        root.bind("<Control-z>", lambda e: self.page_call("backward", "undo"))
        root.bind("<Key>", self._key)
        for i, (key, _, _) in enumerate(PAGES, 1):
            root.bind(f"<Control-Key-{i}>", lambda e, k=key: self.show(k))
        self.build()

    def s(self, key: str) -> str:
        return S[self.lang][key]

    def current_symptoms(self) -> List[str]:
        v = self.state["vehicle"]
        extra = [VEHICLE_SYMPTOMS[x] for x in (v.get("type"), v.get("fuel")) if x]
        return extra + sorted(self.state["selected"])

    # --- layout ---
    def build(self) -> None:
        for w in self.root.winfo_children():
            w.destroy()
        self.root.title(self.s("app"))
        side = tk.Frame(self.root, bg=C["sidebar"], width=px(theme.SIDEBAR_WIDTH))
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        top = tk.Frame(side, bg=C["sidebar"], padx=18, pady=18)
        top.pack(fill="x")
        q = K
        logo = tk.Canvas(top, width=34 * q, height=34 * q, bg=C["sidebar"], highlightthickness=0)
        round_rect(logo, 0, 0, 34 * q, 34 * q, 9 * q, fill=C["accent"], outline="")
        # two wheels and a frame: a small motorbike mark
        logo.create_oval(6 * q, 16 * q, 15 * q, 25 * q, outline=C["on_accent"], width=2 * q)
        logo.create_oval(19 * q, 16 * q, 28 * q, 25 * q, outline=C["on_accent"], width=2 * q)
        logo.create_line(10 * q, 20 * q, 15 * q, 11 * q, 22 * q, 11 * q, 24 * q, 20 * q,
                         fill=C["on_accent"], width=2 * q)
        logo.pack(anchor="w")
        tk.Label(top, text=self.s("app"), font=F["title"], fg="#FFFFFF", bg=C["sidebar"], anchor="w",
                 justify="left", wraplength=px(180)).pack(anchor="w", pady=(10, 0))
        tk.Label(top, text=self.s("app_sub"), font=F["small"], fg=C["sidebar_muted"], bg=C["sidebar"],
                 anchor="w", justify="left", wraplength=px(180)).pack(anchor="w")
        self.nav = {}
        n = 0
        for sec, items in NAV:
            tk.Label(side, text=self.s(sec), font=F["small_bold"], fg=C["sidebar_muted"], bg=C["sidebar"],
                     anchor="w", padx=18).pack(fill="x", pady=(14, 4))
            for key, text_key, _ in items:
                n += 1
                self.nav[key] = self._nav_item(side, key, self.s(text_key), f"Ctrl+{n}")
        bottom = tk.Frame(side, bg=C["sidebar"], padx=18, pady=16)
        bottom.pack(side="bottom", fill="x")
        tk.Label(bottom, text=self.s("lang"), font=F["small"], fg=C["sidebar_muted"], bg=C["sidebar"]).pack(anchor="w")
        langs = tk.Frame(bottom, bg=C["sidebar"])
        langs.pack(anchor="w", pady=(4, 10))
        for code in ("vi", "en"):
            on = code == self.lang
            b = tk.Label(langs, text=code.upper(), font=F["small_bold"], padx=10, pady=2, cursor="hand2",
                         bg="#FFFFFF" if on else C["sidebar"], fg=C["sidebar"] if on else C["sidebar_text"],
                         highlightthickness=1, highlightbackground=C["sidebar_muted"])
            b.pack(side="left")
            b.bind("<Button-1>", lambda e, c=code: self.set_lang(c))
        tk.Label(bottom, text=f"{len(self.kb.rules)} luật · {len(self.kb.faults)} lỗi" if self.lang == "vi"
                 else f"{len(self.kb.rules)} rules · {len(self.kb.faults)} faults",
                 font=F["small"], fg=C["sidebar_muted"], bg=C["sidebar"]).pack(anchor="w")

        self.content = tk.Frame(self.root, bg=C["bg"], padx=24, pady=20)
        self.content.pack(side="left", fill="both", expand=True)
        self.pages: Dict[str, Page] = {}
        self.show(self.state["page"])

    def _nav_item(self, parent, key: str, text: str, shortcut: str):
        row = tk.Frame(parent, bg=C["sidebar"], cursor="hand2")
        row.pack(fill="x")
        bar = tk.Frame(row, bg=C["sidebar"], width=4)
        bar.pack(side="left", fill="y")
        lbl = tk.Label(row, text=text, font=F["body"], fg=C["sidebar_text"], bg=C["sidebar"], anchor="w",
                       padx=14, pady=8)
        lbl.pack(side="left", fill="x", expand=True)
        sc = tk.Label(row, text=shortcut, font=F["small"], fg=C["sidebar_muted"], bg=C["sidebar"], padx=10)
        sc.pack(side="right")
        parts = (row, lbl, sc)

        def paint(bg, fg=C["sidebar_text"], ind=C["sidebar"]):
            for w in parts:
                w.configure(bg=bg)
            lbl.configure(fg=fg)
            bar.configure(bg=ind)

        def enter(_):
            if self.state["page"] != key:
                paint(C["sidebar_hover"])

        def leave(_):
            if self.state["page"] != key:
                paint(C["sidebar"])
        for w in parts:
            w.bind("<Button-1>", lambda e: self.show(key))
            w.bind("<Enter>", enter)
            w.bind("<Leave>", leave)
        return paint

    def show(self, key: str) -> None:
        self.state["page"] = key
        for k, paint in self.nav.items():
            if k == key:
                paint(C["sidebar_active"], "#FFFFFF", "#7FD3E0")
            else:
                paint(C["sidebar"])
        for p in self.pages.values():
            p.pack_forget()
        if key not in self.pages:
            cls = next(c for k, _, c in PAGES if k == key)
            self.pages[key] = cls(self.content, self)
        page = self.pages[key]
        page.pack(fill="both", expand=True)
        page.on_show()

    def page_call(self, key: str, method: str) -> None:
        if self.state["page"] == key and key in self.pages:
            getattr(self.pages[key], method)()

    def set_lang(self, lang: str) -> None:
        if lang != self.lang:
            self.lang = lang
            self.build()

    def load_scenario(self, sc) -> None:
        v = {}
        for key, sid in VEHICLE_SYMPTOMS.items():
            if sid in sc.symptoms:
                v["type" if key in ("manual", "scooter") else "fuel"] = key
        self.state["vehicle"] = v
        self.state["selected"] = {x for x in sc.symptoms if self.kb.symbols[x].subsystem != "vehicle"}
        old = self.pages.pop("forward", None)
        if old is not None:
            old.destroy()
        self.show("forward")
        self.pages["forward"].run()

    # --- events ---
    def _wheel(self, event) -> None:
        w = self.root.winfo_containing(event.x_root, event.y_root)
        while w is not None:
            if getattr(w, "_scrollframe", False):
                w.wheel(event.delta)
                return
            w = getattr(w, "master", None)

    def _key(self, event) -> None:
        if self.state["page"] != "backward" or event.state & 0x4:  # ignore with Ctrl
            return
        if isinstance(self.root.focus_get(), (tk.Entry, ttk.Entry, tk.Text)):
            return
        ch = (event.char or "").lower()
        if ch:
            self.pages["backward"].key(ch)


def main() -> int:
    try:  # sharp text on high-DPI Windows screens
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError, ImportError):
        pass
    lang = "en" if "--lang=en" in sys.argv or ("--lang" in sys.argv and "en" in sys.argv) else "vi"
    root = tk.Tk()
    App(root, lang)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
