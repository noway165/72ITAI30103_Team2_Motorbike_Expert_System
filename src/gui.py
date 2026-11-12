"""Main window of the GUI (owner: Lâm). Look and wording: docs/ui_guide.md.

Run from the repository root:
    python src/gui.py            (add --lang=en for English)

The window is the MotoLogic sidebar, a top bar and one screen at a time (Ctrl+1 ... Ctrl+7):
    1. Chẩn đoán          gui_diagnosis.py, class DiagnosisPage (Giang): 3 steps, 3 methods
    2. Lịch sử phiên       gui_history.py, class HistoryPage (Giang)
    3. Cơ sở tri thức      KBPage below: rules and the rule checker (Lâm)
    Classic screens:
    4. Trợ lý chẩn đoán    gui_assistant.py, class AssistantPage  (Lâm): free text, adaptive questions
    5. Theo triệu chứng   src/gui_forward.py,  class ForwardPage   (Giang)
    6. Hỏi đáp từng câu    src/gui_backward.py, class BackwardPage  (Khoa)
    4. Giới thiệu          AboutPage below (Lâm)

Screens 1 and 2 are plugged in: while their file does not exist yet, the
window shows a note saying who builds it. How to write a screen:
docs/ui_guide.md, section 9. Shared widgets are in gui_widgets.py.
"""

from __future__ import annotations

import importlib
import sys
from typing import Dict, Optional

import tkinter as tk
from tkinter import ttk

import gui_widgets as w
import theme
from gui_assistant import AssistantPage
from gui_diagnosis import DiagnosisPage, session_number
from gui_history import HistoryPage
from gui_widgets import (CFBar, HintEntry, Page, Panel, RoundCard, ScrollFrame, Segmented, autowrap, bind_tree,
                         chip, data_root, dot, fold, icon, label, link, page_header, px, tile)
from kb import KnowledgeBase, load_kb, validate
from present import short
from scenarios import load_scenarios
from theme import COLORS as C
from theme import FONTS as F
from theme import PAD, SUBSYSTEM_COLORS, SUBSYSTEM_NAMES, SUBSYSTEM_ORDER

# ---------------------------------------------------------------------------
# Wording of the shell, KB and About screens (see docs/ui_guide.md, section 4).
# Each plugged-in screen keeps its own wording in its own file.
# ---------------------------------------------------------------------------

S = {
    "vi": {
        "app": "Chẩn đoán lỗi xe máy",
        "app_sub": "Hệ chuyên gia dựa trên luật · Nhóm 2",
        "sec_diag": "CHẨN ĐOÁN", "sec_other": "HỆ THỐNG",
        "nav_assistant": "Trợ lý chẩn đoán", "nav_forward": "Theo triệu chứng", "nav_backward": "Hỏi đáp từng câu",
        "nav_kb": "Cơ sở tri thức", "nav_about": "Giới thiệu",
        "nav_diagnosis": "Chẩn đoán", "nav_history": "Lịch sử phiên",
        "sec_workspace": "LÀM VIỆC", "sec_legacy": "MÀN CŨ", "workspace": "Làm việc",
        "session": "Phiên {n:03d}", "offline": "Chạy offline",
        "transparent": "Minh bạch từ thiết kế.", "transparent_sub": "Mọi kết luận đều dẫn về câu trả lời của bạn.",
        "rules": "luật", "faults": "lỗi", "proto": "ACADEMIC PROTOTYPE", "proto_group": "Nhóm 2 · Đề tài A",
        "proto_note": "Luật minh hoạ. Không thay cho việc kiểm tra của thợ.",
        "lang": "Ngôn ngữ", "n_rules": "{r} luật · {f} lỗi", "mode": "Giao diện", "light": "Sáng", "dark": "Tối",
        "todo_title": "Màn hình đang được làm",
        "todo_body": "Màn hình này do {owner} phụ trách. Tạo file src/{module}.py có class {cls}(Page); "
                     "cửa sổ sẽ tự hiện màn hình khi file có mặt. Hướng dẫn: docs/ui_guide.md, mục 9.",
        "todo_error": "File src/{module}.py có lỗi khi nạp:",
        "kb_title": "Cơ sở tri thức",
        "kb_sub": "Toàn bộ luật NẾU … THÌ … của hệ thống, và kết quả bộ kiểm tra luật (kb.validate).",
        "t_sym": "Triệu chứng", "t_int": "Trung gian", "t_fault": "Lỗi", "t_rule": "Luật",
        "t_valid": "Kiểm tra luật", "t_valid_v": "{e} lỗi · {w} cảnh báo",
        "all_sys": "Tất cả bộ phận", "filter": "Lọc theo mã hoặc nội dung…",
        "col_id": "Mã", "col_if": "NẾU", "col_then": "THÌ", "col_cf": "CF", "col_src": "Nguồn",
        "rule_detail": "Chi tiết luật", "pick_rule": "Chọn một luật trong bảng để xem chi tiết.",
        "k_symptom": "triệu chứng", "k_intermediate": "trung gian", "k_fault": "lỗi",
        "IF": "NẾU", "THEN": "THÌ",
        "source": "Nguồn", "no_source": "chưa có nguồn", "file": "File",
        "used_by": "Luật dùng kết luận này", "warnings": "Cảnh báo của bộ kiểm tra",
        "ab_title": "Giới thiệu",
        "ab_sub": "Đồ án cuối kỳ môn Nhập môn Trí tuệ nhân tạo (261_72ITSE30303_01) · GV: TS. Nguyễn Thanh Huy",
    },
    "en": {
        "app": "Motorbike Fault Diagnosis",
        "app_sub": "Rule-based expert system · Group 2",
        "sec_diag": "DIAGNOSIS", "sec_other": "SYSTEM",
        "nav_assistant": "Diagnosis assistant", "nav_forward": "By symptoms", "nav_backward": "Step-by-step questions",
        "nav_kb": "Knowledge base", "nav_about": "About",
        "nav_diagnosis": "Diagnosis", "nav_history": "Session history",
        "sec_workspace": "WORKSPACE", "sec_legacy": "CLASSIC SCREENS", "workspace": "Workspace",
        "session": "Session {n:03d}", "offline": "Local mode",
        "transparent": "Transparent by design.", "transparent_sub": "Every conclusion connects back to your answers.",
        "rules": "rules", "faults": "faults", "proto": "ACADEMIC PROTOTYPE", "proto_group": "Group 2 · Topic A",
        "proto_note": "Illustrative rules. Not a mechanic's inspection.",
        "lang": "Language", "n_rules": "{r} rules · {f} faults", "mode": "Theme", "light": "Light", "dark": "Dark",
        "todo_title": "Screen in progress",
        "todo_body": "{owner} builds this screen. Create src/{module}.py with class {cls}(Page); "
                     "the window shows it as soon as the file exists. Guide: docs/ui_guide.md, section 9.",
        "todo_error": "src/{module}.py failed to load:",
        "kb_title": "Knowledge base",
        "kb_sub": "Every IF … THEN … rule of the system, and the result of the rule checker (kb.validate).",
        "t_sym": "Symptoms", "t_int": "Intermediates", "t_fault": "Faults", "t_rule": "Rules",
        "t_valid": "Rule check", "t_valid_v": "{e} errors · {w} warnings",
        "all_sys": "All parts", "filter": "Filter by id or text…",
        "col_id": "Id", "col_if": "IF", "col_then": "THEN", "col_cf": "CF", "col_src": "Source",
        "rule_detail": "Rule details", "pick_rule": "Select a rule in the table to see its details.",
        "k_symptom": "symptom", "k_intermediate": "intermediate", "k_fault": "fault",
        "IF": "IF", "THEN": "THEN",
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
        ("Thành viên", "Tăng Thoại Lâm (nhóm trưởng): cơ sở tri thức, CLI, khung giao diện, file .exe\n"
                       "Kiều Bảo Giang: suy diễn tiến, CF, thuật toán Wang, màn hình Theo triệu chứng\n"
                       "Nguyễn Nam Khoa: suy diễn lùi, giải thích why / how, màn hình Hỏi đáp, đánh giá"),
        ("Lưu ý", "Kết quả chỉ mang tính tham khảo; lỗi “Cần mang ra thợ” nên được kiểm tra tại tiệm."),
        ("Phím tắt", "Ctrl+1 … Ctrl+7: chuyển màn hình"),
    ],
    "en": [
        ("Project", "An expert system that diagnoses common motorbike faults. The knowledge base holds IF … THEN … "
                    "rules with certainty factors (CF); the program runs forward and backward chaining, explains "
                    "why and how, and checks its conclusions with Wang's algorithm."),
        ("Team", "Tăng Thoại Lâm (leader): knowledge base, CLI, GUI shell, .exe\n"
                 "Kiều Bảo Giang: forward chaining, CF, Wang's algorithm, By symptoms screen\n"
                 "Nguyễn Nam Khoa: backward chaining, why / how, Step-by-step screen, evaluation"),
        ("Note", "Results are advice only; faults marked “Take it to a mechanic” should be checked at a workshop."),
        ("Shortcuts", "Ctrl+1 … Ctrl+7: change screen"),
    ],
}


# ---------------------------------------------------------------------------
# Screens built by teammates are loaded from their own files
# ---------------------------------------------------------------------------

SLOTS = {  # key: (module in src/, class name, owner)
    "forward": ("gui_forward", "ForwardPage", "Giang"),
    "backward": ("gui_backward", "BackwardPage", "Khoa"),
}


def load_slot(key: str):
    """(page class or None, error text or "") for a plugged-in screen."""
    module, cls, _ = SLOTS[key]
    try:
        return getattr(importlib.import_module(module), cls), ""
    except ModuleNotFoundError as e:
        if e.name == module:
            return None, ""  # file not written yet
        return None, f"{type(e).__name__}: {e}"
    except Exception as e:  # show the problem instead of crashing the whole window
        return None, f"{type(e).__name__}: {e}"


class PlaceholderPage(Page):
    """Shown while a teammate's screen file does not exist (or fails to load)."""

    def __init__(self, parent, app, key: str, error: str = ""):
        super().__init__(parent, app)
        module, cls, owner = SLOTS[key]
        s = app.s
        page_header(self, s("nav_" + key), "").pack(fill="x", pady=(0, PAD["m"]))
        box = Panel(self, s("todo_title"))
        box.pack(fill="x")
        body = tk.Frame(box.body, bg=C["surface"], padx=16, pady=14)
        body.pack(fill="x")
        autowrap(label(body, s("todo_body").format(owner=owner, module=module, cls=cls))).pack(fill="x")
        if error:
            label(body, s("todo_error").format(module=module), "small_bold", "danger").pack(anchor="w", pady=(10, 2))
            autowrap(label(body, error, "mono", "danger")).pack(fill="x")


# ---------------------------------------------------------------------------
# Lâm's screens
# ---------------------------------------------------------------------------

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
# Application shell: sidebar + one screen at a time
# ---------------------------------------------------------------------------

NAV = [  # (section, [(key, nav text key, icon or "" for a small item), ...])
    ("sec_workspace", [("diagnosis", "nav_diagnosis", "pulse"), ("history", "nav_history", "history"),
                       ("kb", "nav_kb", "layers")]),
    ("sec_legacy", [("assistant", "nav_assistant", ""), ("forward", "nav_forward", ""),
                    ("backward", "nav_backward", ""), ("about", "nav_about", "")]),
]
PAGES = [key for _, items in NAV for key, _, _ in items]
OWN_PAGES = {"diagnosis": DiagnosisPage, "history": HistoryPage, "assistant": AssistantPage, "kb": KBPage,
             "about": AboutPage}


class App:
    """What every screen can use: kb, lang, s(), scenarios, state, show()."""

    def __init__(self, root: tk.Tk, lang: str = "vi"):
        self.root = root
        self.lang = lang
        self.kb: KnowledgeBase = load_kb(data_root() / "knowledge_base")
        try:
            self.scenarios = load_scenarios(data_root() / "scenarios")
        except (OSError, ValueError, KeyError):
            self.scenarios = []
        self.state: Dict[str, object] = {"page": "diagnosis"}  # shared by all screens; add your own keys
        w.K = max(1.0, root.winfo_fpixels("1i") / 96)  # scale pixel sizes on 125 % / 150 % screens
        theme.apply(root)
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        width = min(px(theme.WINDOW_SIZE[0]), int(sw * 0.94))
        height = min(px(theme.WINDOW_SIZE[1]), int(sh * 0.88))
        root.geometry(f"{width}x{height}+{max(0, (sw - width) // 2)}+{max(0, (sh - height) // 3)}")
        root.minsize(min(px(theme.WINDOW_MIN_SIZE[0]), width), min(px(theme.WINDOW_MIN_SIZE[1]), height))
        root.bind_all("<MouseWheel>", self._wheel)
        root.bind("<Key>", self._key)
        for i, key in enumerate(PAGES, 1):
            root.bind(f"<Control-Key-{i}>", lambda e, k=key: self.show(k))
        self.build()

    def s(self, key: str) -> str:
        return S[self.lang][key]

    @property
    def page(self) -> Optional[Page]:
        return self.pages.get(self.state["page"])

    # --- layout ---
    def build(self) -> None:
        # pending after() calls of the old screens would run on destroyed widgets (or on a reused callback name)
        for job in self.root.tk.splitlist(self.root.tk.call("after", "info")):
            self.root.tk.call("after", "cancel", job)  # Tcl only: destroy() still deletes the Python callbacks
        for child in self.root.winfo_children():
            child.destroy()
        self.root.title(self.s("app"))
        side = tk.Frame(self.root, bg=C["sidebar"], width=px(theme.SIDEBAR_WIDTH))
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        tk.Frame(self.root, bg=C["border"], width=1).pack(side="left", fill="y")
        brand = tk.Frame(side, bg=C["sidebar"], padx=px(20), pady=px(12))
        brand.pack(fill="x")
        label(brand, "MotoLogic", "big", "sidebar_text", bg="sidebar").pack(anchor="w")
        label(brand, "MOTORBIKE EXPERT SYSTEM", "eyebrow", "sidebar_muted", bg="sidebar").pack(anchor="w")
        # packed before the navigation so that a short window clips the cards, never the switches
        bottom = tk.Frame(side, bg=C["sidebar"], padx=px(12), pady=px(10))
        bottom.pack(side="bottom", fill="x")
        self.navbox = tk.Frame(side, bg=C["sidebar"])
        self.navbox.pack(fill="x")

        card = RoundCard(side, fill="panel", border=None, radius=16, bg="sidebar", pad=12)
        card.pack(fill="x", padx=px(12), pady=(px(10), 0))
        b = card.body
        autowrap(label(b, self.s("transparent"), "title", "on_panel", bg="panel")).pack(fill="x")
        autowrap(label(b, self.s("transparent_sub"), "small", "panel_muted", bg="panel")).pack(
            fill="x", pady=(px(4), 0))
        tk.Frame(b, bg=C["panel_soft"], height=1).pack(fill="x", pady=px(8))
        nums = tk.Frame(b, bg=C["panel"])
        nums.pack(fill="x")
        for n, cap in ((len(self.kb.rules), self.s("rules")), (len(self.kb.faults), self.s("faults"))):
            col = tk.Frame(nums, bg=C["panel"])
            col.pack(side="left", padx=(0, px(28)))
            label(col, str(n), "big", "lime", bg="panel").pack(anchor="w")
            label(col, cap, "small", "panel_muted", bg="panel").pack(anchor="w")

        proto = RoundCard(bottom, fill="bg", border=None, radius=14, bg="sidebar", pad=12)
        proto.pack(fill="x")
        label(proto.body, self.s("proto"), "eyebrow", "accent", bg="bg").pack(anchor="w")
        label(proto.body, self.s("proto_group"), "body", "text", bg="bg").pack(anchor="w", pady=(px(4), px(2)))
        autowrap(label(proto.body, self.s("proto_note"), "small", "muted", bg="bg")).pack(fill="x")
        toggles = tk.Frame(bottom, bg=C["sidebar"])
        toggles.pack(fill="x", pady=(px(10), 0))
        Segmented(toggles, [("vi", "VI"), ("en", "EN")], self.lang, self.set_lang, bg="sidebar").pack(side="left")
        Segmented(toggles, [("light", self.s("light")), ("dark", self.s("dark"))], theme.MODE, self.set_mode,
                  bg="sidebar").pack(side="right")

        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(side="left", fill="both", expand=True)
        self.topbar = tk.Frame(main, bg=C["bg"], padx=px(28), pady=px(12))
        self.topbar.pack(fill="x")
        tk.Frame(main, bg=C["border"], height=1).pack(fill="x")
        self.content = tk.Frame(main, bg=C["bg"], padx=px(28), pady=px(18))
        self.content.pack(fill="both", expand=True)
        self.pages: Dict[str, Page] = {}
        self.show(self.state["page"])

    def draw_nav(self) -> None:
        for child in self.navbox.winfo_children():
            child.destroy()
        n = 0
        for sec, items in NAV:
            label(self.navbox, self.s(sec), "small_bold", "sidebar_muted", bg="sidebar").pack(
                anchor="w", padx=px(20), pady=(px(8), px(2)))
            for key, text_key, icon_name in items:
                n += 1
                on = key == self.state["page"]
                fill = "sidebar_active" if on else "sidebar"
                item = RoundCard(self.navbox, fill=fill, border=None, radius=12, bg="sidebar",
                                 pad=8 if icon_name else 2)
                item.pack(fill="x", padx=px(12), pady=px(1))
                fg = "on_lime" if on else "sidebar_text" if icon_name else "sidebar_muted"
                if icon_name:
                    icon(item.body, icon_name, 18, fg, fill).pack(side="left", padx=(px(4), px(12)))
                label(item.body, self.s(text_key), "lead" if icon_name else "body", fg, bg=fill).pack(
                    side="left", padx=(0 if icon_name else px(4), 0))
                label(item.body, f"Ctrl+{n}", "small", "on_lime" if on else "sidebar_muted", bg=fill).pack(
                    side="right")
                item.configure(cursor="hand2")
                bind_tree(item, "<Button-1>", lambda e, k=key: self.show(k))

    def refresh_topbar(self) -> None:
        """Breadcrumb, session number and the "offline" chip."""
        for child in self.topbar.winfo_children():
            child.destroy()
        names = {k: text_key for _, items in NAV for k, text_key, _ in items}
        crumb = self.s("workspace") + "   /   " + self.s(names[self.state["page"]])
        label(self.topbar, crumb, "lead", "muted", bg="bg").pack(side="left")
        chip(self.topbar, "●  " + self.s("offline"), C["accent"], C["chrome"]).pack(side="right")
        label(self.topbar, self.s("session").format(n=session_number(self.state)), "lead", "muted",
              bg="bg").pack(side="right", padx=px(20))

    def make_page(self, key: str) -> Page:
        if key in OWN_PAGES:
            return OWN_PAGES[key](self.content, self)
        cls, error = load_slot(key)
        if cls is None:
            return PlaceholderPage(self.content, self, key, error)
        return cls(self.content, self)

    def show(self, key: str) -> None:
        """Switch to a screen; the screen is built the first time it is shown."""
        self.state["page"] = key
        self.draw_nav()
        self.refresh_topbar()
        for p in self.pages.values():
            p.pack_forget()
        if key not in self.pages:
            self.pages[key] = self.make_page(key)
        page = self.pages[key]
        page.pack(fill="both", expand=True)
        page.on_show()

    def set_mode(self, mode: str) -> None:
        """Light or dark colours; every screen is built again with the new palette."""
        if mode != theme.MODE:
            theme.set_mode(mode)
            theme.apply(self.root)
            self.build()

    def set_lang(self, lang: str) -> None:
        if lang != self.lang:
            self.lang = lang
            self.build()  # every screen is built again in the new language

    # --- events ---
    def _wheel(self, event) -> None:
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        while widget is not None:
            if getattr(widget, "_scrollframe", False):
                widget.wheel(event.delta)
                return
            widget = getattr(widget, "master", None)

    def _key(self, event) -> None:
        """Pass key presses to the current screen if it has on_key(event)."""
        if isinstance(self.root.focus_get(), (tk.Entry, ttk.Entry, tk.Text)):
            return
        handler = getattr(self.page, "on_key", None)
        if handler:
            handler(event)


def main() -> int:
    try:  # sharp text on high-DPI Windows screens
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except (AttributeError, OSError, ImportError):
        pass
    lang = "en" if "--lang=en" in sys.argv else "vi"
    root = tk.Tk()
    App(root, lang)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
