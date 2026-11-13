"""MotoLogic "Chẩn đoán" screen: 3 steps, 3 ways to diagnose (owner: Giang).

    Step 1  the motorbike (scooter / manual, FI / carburettor) and the method
    Step 2  a: step-by-step questions  (backward chaining, Khoa's BackwardSession)
            b: tick the symptoms        (forward chaining, Giang)
            c: describe in words        (Lâm's nlu.extract + interview.Interview)
    Step 3  the result: fault, CF gauge, how it was found, next step, Wang check

Every answer lives in app.state["dx"], so changing the language or light / dark
mode (the window is rebuilt) keeps the diagnosis. Each result is also added to
app.state["history"] (gui_history.py).

The top half is plain logic (tests/test_gui_diagnosis.py); DiagnosisPage only draws.
Spec and mock-ups: docs/design/motologic_spec.md.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import tkinter as tk

import chat
from backward_chaining import UNKNOWN, BackwardSession
from forward_chaining import forward_chain
from gui_backward import ALL, goals_for, question_view
from gui_forward import matches, search_key, symptom_groups
from gui_widgets import (SUBSYSTEM_ICONS, CheckRow, ChoiceCard, Gauge, HintEntry, Page, PillButton, RoundCard,
                         ScrollFrame, Segmented, Stepper, _draw_icon, autowrap, chip, eyebrow, icon, label, link, px,
                         round_rect)
from interview import Interview
from kb import KnowledgeBase
from nlu import extract
from present import how_rows, model_notes, model_of, near_misses, short
from present import t as present_text
from theme import COLORS as C
from theme import FONTS as F
from theme import SEVERITY_TEXT, SUBSYSTEM_NAMES, SUBSYSTEM_ORDER
from wang import entails

TEXT = {
    "vi": {
        "steps": ["Khai báo xe", "Kể triệu chứng", "Hiểu kết quả"],
        "steps_done": ["Đã khai báo xe", "Đã xem triệu chứng", "Hiểu kết quả"],
        "e1": "Cùng tìm nguyên nhân", "t1": "Trả lời rõ hơn. Bước tiếp theo đúng hơn.",
        "s1": "Cho biết bạn thấy gì. Chương trình nối các triệu chứng lại và giải thích vì sao.",
        "bike": "Xe của bạn", "other_bike": "Xe khác", "for_model": "Riêng cho {name}",
        "scooter": "Xe tay ga", "scooter_sub": "Tự động / dây curoa CVT",
        "manual": "Xe số", "manual_sub": "Có số / truyền động xích",
        "fuel": "Nhiên liệu", "fi": "Phun xăng (FI)", "carb": "Bình xăng con", "unsure": "Không rõ",
        "how": "Bạn muốn chẩn đoán thế nào?",
        "guided": "Hỏi đáp từng câu", "guided_sub": "Chỉ trả lời những câu cần thiết, từng câu một.",
        "guided_note": "Suy diễn lùi (backward chaining)", "recommended": "Gợi ý",
        "symptoms": "Tôi biết triệu chứng", "symptoms_sub": "Chọn mọi triệu chứng bạn biết để tìm lỗi phù hợp.",
        "symptoms_note": "Suy diễn tiến (forward chaining)",
        "talk": "Kể bằng lời", "talk_sub": "Gõ một câu mô tả tình trạng xe; trợ lý hiểu và hỏi thêm.",
        "talk_note": "Trợ lý chẩn đoán",
        "n_faults": "{n} lỗi",
        "safety": "An toàn trước tiên",
        "safety_sub": "Dựng xe ở nơi an toàn và tắt máy trước khi kiểm tra.",
        "no_sensor": "Không cần cảm biến, ảnh hay ghi âm.",
        "start": "Bắt đầu chẩn đoán",
        "e2a": "Hỏi đáp từng câu", "t2a": "Cùng thu hẹp dần.",
        "part": "Bộ phận", "all": "Tất cả",
        "where": "Sự cố nằm ở đâu?", "where_sub": "Chọn bộ phận để chỉ hỏi những câu liên quan.",
        "not_sure_part": "Chưa rõ, hỏi tất cả", "not_sure_part_sub": "Hỏi về cả 6 bộ phận, sẽ nhiều câu hơn.",
        "where_why_sub": "Khi biết bộ phận, chương trình chỉ thử các lỗi của bộ phận "
                                                        "đó: trung bình 9 câu thay vì khoảng 40 câu cho cả 40 lỗi.",
        "where_note": "Số đo trên 30 kịch bản thử (evaluate.py). Sau đó vẫn đổi được bộ phận.",
        "question": "CÂU {n:02d}", "yes": "Có", "no": "Không", "skip": "Không chắc, bỏ qua câu này",
        "why": "Tại sao hỏi câu này?", "checking": "Đang kiểm tra: {goal}",
        "why_sub": "Câu trả lời của bạn quyết định luật bên dưới có chạy được hay không.",
        "testing": "{rule} · LUẬT ĐANG THỬ", "leads": "Kết luận đó dùng cho luật:",
        "open": "Còn {n} / {total} giả thuyết", "illustrative": "Luật minh hoạ · cần thợ kiểm duyệt",
        "answered": "ĐÃ TRẢ LỜI", "none_yet": "Chưa có câu trả lời.", "edit": "Sửa câu trả lời",
        "previous": "Câu trước", "change": "Đổi cách chẩn đoán",
        "a_yes": "có", "a_no": "không", "a_unknown": "không chắc",
        "e2b": "Danh sách triệu chứng", "t2b": "Bạn đã thấy gì?",
        "s2b": "Chỉ chọn những gì bạn chắc chắn. Triệu chứng không chọn được coi là chưa biết.",
        "search": "Tìm triệu chứng: còi, phanh, khói…", "checks": "Triệu chứng: {part}",
        "all_checks": "Mọi triệu chứng", "no_match": "Không có triệu chứng nào khớp.",
        "observations": "Quan sát của bạn", "n_selected": "{n} đã chọn",
        "nothing_selected": "Chưa chọn triệu chứng nào.", "more": "+ {n} triệu chứng khác",
        "next": "Điều gì xảy ra tiếp theo?",
        "next_sub": "Chương trình so các triệu chứng đã chọn với mọi luật rồi chỉ ra các lỗi được luật ủng hộ.",
        "next_note": "Mỗi kết quả đều xem lại được chuỗi luật.",
        "find": "Tìm lỗi phù hợp",
        "e2c": "Kể bằng lời", "t2c": "Kể cho chương trình nghe.",
        "s2c": "Gõ tự nhiên như khi kể với thợ, tiếng Việt có hoặc không dấu, hoặc tiếng Anh.",
        "talk_box": "Tình trạng xe", "try": "Hoặc bấm một câu ví dụ:",
        "examples": ["Sáng nay đề chỉ nghe tạch tạch, còi cũng yếu, ắc quy dùng hơn 2 năm rồi",
                     "Bóp phanh trước nghe kêu rít",
                     "Đi đường gồ ghề thấy xe nhún nhiều, lốp mòn không đều"],
        "how_read": "Chương trình đọc gì?",
        "talk_reads": "Kể càng cụ thể, chương trình hiểu càng đúng. Nó tìm trong câu của bạn:",
        "talk_kinds": ["Triệu chứng: không nổ, chết máy, còi yếu…", "Âm thanh: tạch tạch, kêu rít, ken két…",
                       "Bộ phận: ắc quy, phanh, lốp, phuộc…"],
        "analyze": "Phân tích", "to_guided": "Chuyển sang hỏi đáp từng câu", "understood": "Đã hiểu từ câu bạn kể", "understood_none":
            "Chưa nhận ra triệu chứng nào. Thử kể rõ hơn, ví dụ “còi yếu”, “đề không nổ”.",
        "chat_title": "Trò chuyện với MotoLogic", "chat_sub": "Mọi câu trả lời đều lấy từ luật trong cơ sở tri thức.",
        "chat_hint": "Trả lời, kể thêm triệu chứng hoặc hỏi lại…", "send": "Gửi",
        "quick_q": ["Có", "Không", "Không rõ", "Tại sao hỏi vậy?"],
        "quick": ["Làm sao biết?", "Sửa thế nào?", "Còn khả năng nào?"],
        "beliefs": "Khả năng lúc này", "by_rules": "luật đã chứng minh",
        "see_result": "Xem kết quả đầy đủ", "restart_chat": "Kể lại từ đầu",
        "e3": "Kết quả chẩn đoán", "t3": "Đây là điều triệu chứng của bạn gợi ý.",
        "likely": "Lỗi có khả năng cao", "possible": "Lỗi có thể gặp", "chain": "Theo chuỗi luật {chain}",
        "obs": "Quan sát", "rules_used": "Luật đã dùng",
        "reach": "Chương trình suy ra thế nào?", "reach_sub": "Quan sát của bạn → kết luận trung gian → lỗi",
        "you": "Bạn trả lời", "next_step": "Bước tiếp theo", "alt": "Cũng có thể là",
        "wang": "Kiểm tra chéo kết luận", "wang_sub": "Chứng minh lại bằng logic (thuật toán Wang), "
                                                     "không dựa vào điểm tin cậy.",
        "wang_not_run": "Chưa kiểm tra", "verify": "Kiểm tra chéo",
        "wang_yes": "✓ Đã chứng minh: luật + câu trả lời của bạn ⇒ lỗi này",
        "wang_no": "✕ Không chứng minh được lỗi này từ câu trả lời",
        "confidence": "Độ tin cậy {p:.0%}",
        "no_fault": "Chưa đủ dữ kiện", "no_fault_sub": "Không lỗi nào đạt độ tin cậy 20%.",
        "derived": "Chương trình đã suy ra được", "check_more": "Kiểm tra thêm các điểm sau rồi chẩn đoán lại:",
        "nothing_derived": "Các câu trả lời chưa khớp luật nào. Thử cách chẩn đoán khác hoặc bộ phận khác.",
        "disclaimer": "Luật minh hoạ; kết quả không thay cho việc kiểm tra của thợ.",
        "new": "Chẩn đoán mới",
        "method_guided": "Hỏi đáp từng câu", "method_symptoms": "Chọn triệu chứng", "method_talk": "Kể bằng lời",
        "unknown_bike": "Chưa rõ loại xe",
    },
    "en": {
        "steps": ["Set up your bike", "Share symptoms", "Understand the result"],
        "steps_done": ["Bike set up", "Symptoms reviewed", "Understand the result"],
        "e1": "Let's find the cause", "t1": "A clearer answer. A better next step.",
        "s1": "Tell us what you notice. We'll connect the symptoms and explain the reasoning.",
        "bike": "Your motorbike", "other_bike": "Another bike", "for_model": "For your {name}",
        "scooter": "Scooter", "scooter_sub": "Automatic / CVT belt",
        "manual": "Manual motorbike", "manual_sub": "Gears / chain drive",
        "fuel": "Fuel system", "fi": "Fuel injection", "carb": "Carburettor", "unsure": "Not sure",
        "how": "How would you like to diagnose?",
        "guided": "Guide me with questions", "guided_sub": "Answer only what matters, one question at a time.",
        "guided_note": "Backward chaining", "recommended": "Recommended",
        "symptoms": "I know my symptoms", "symptoms_sub": "Select all known symptoms to find matching faults.",
        "symptoms_note": "Forward chaining",
        "talk": "Describe it in words", "talk_sub": "Type a sentence about your bike; the assistant asks the rest.",
        "talk_note": "Diagnosis assistant",
        "n_faults": "{n} faults",
        "safety": "Safety comes first", "safety_sub": "Park safely and switch off the engine before checking your bike.",
        "no_sensor": "No sensors, photos or sound recordings needed.",
        "start": "Start diagnosis",
        "e2a": "Guided diagnosis", "t2a": "Let's narrow it down.",
        "part": "System", "all": "All",
        "where": "Where is the problem?", "where_sub": "Pick a system so that only related questions are asked.",
        "not_sure_part": "Not sure, ask about everything", "not_sure_part_sub": "Covers all 6 systems; more questions.",
        "where_why_sub": "With a system chosen, only its faults are tested: 9 "
                                                         "questions on average instead of about 40 for all 40 faults.",
        "where_note": "Measured on the 30 test scenarios (evaluate.py). You can change the system later.",
        "question": "QUESTION {n:02d}", "yes": "Yes", "no": "No", "skip": "Not sure — skip this question",
        "why": "Why this question?", "checking": "Checking: {goal}",
        "why_sub": "Your answer decides whether the rule below can fire.",
        "testing": "{rule} · RULE BEING TESTED", "leads": "Its conclusion is used by:",
        "open": "{n} / {total} hypotheses still open", "illustrative": "Illustrative rule · pending mechanic review",
        "answered": "ANSWERS SO FAR", "none_yet": "No answer yet.", "edit": "Edit answer",
        "previous": "Previous question", "change": "Change diagnosis method",
        "a_yes": "yes", "a_no": "no", "a_unknown": "not sure",
        "e2b": "Symptom checklist", "t2b": "What have you noticed?",
        "s2b": "Select only what you know is true. Unselected symptoms remain unknown.",
        "search": "Search: horn, brake, smoke…", "checks": "{part} checks",
        "all_checks": "All symptoms", "no_match": "No symptom matches.",
        "observations": "Your observations", "n_selected": "{n} selected",
        "nothing_selected": "Nothing selected yet.", "more": "+ {n} more",
        "next": "What happens next?",
        "next_sub": "We'll match all selected facts against the rules, then show any faults they support.",
        "next_note": "You can review the rule chain with every result.",
        "find": "Find matching faults",
        "e2c": "Describe it", "t2c": "Tell the program what happens.",
        "s2c": "Write as you would tell a mechanic, in Vietnamese (with or without accents) or English.",
        "talk_box": "What is wrong with the bike", "try": "Or click an example:",
        "examples": ["The starter only clicks and the horn is weak",
                     "The brakes squeal loudly when I stop",
                     "The rear shock bounces a lot on bumpy roads"],
        "how_read": "What does it read?",
        "talk_reads": "The more specific you are, the better it understands. It looks for:",
        "talk_kinds": ["Symptoms: won't start, stalls, weak horn…", "Sounds: clicking, squealing, grinding…",
                       "Parts: battery, brakes, tyres, forks…"],
        "analyze": "Analyse", "to_guided": "Switch to guided questions", "understood": "Understood from your text", "understood_none":
            "No symptom recognised yet. Try to be more specific, e.g. “weak horn”, “won't start”.",
        "chat_title": "Chat with MotoLogic", "chat_sub": "Every reply comes from the rules in the knowledge base.",
        "chat_hint": "Answer, add symptoms or ask…", "send": "Send",
        "quick_q": ["Yes", "No", "Not sure", "Why this question?"],
        "quick": ["How do you know?", "How to fix?", "What else?"],
        "beliefs": "Most likely now", "by_rules": "proved by the rules",
        "see_result": "See the full result", "restart_chat": "Start over",
        "e3": "Diagnosis result", "t3": "Here's what your symptoms suggest.",
        "likely": "Likely fault", "possible": "Possible fault", "chain": "Supported by the {chain} rule chain",
        "obs": "Observations", "rules_used": "Rules used",
        "reach": "How did we reach this?", "reach_sub": "Your observations → intermediate fact → likely fault",
        "you": "You said", "next_step": "Recommended next step", "alt": "It could also be",
        "wang": "Cross-check the conclusion", "wang_sub": "Proves it again with logic (Wang's algorithm), "
                                                          "without the confidence scores.",
        "wang_not_run": "Not checked yet", "verify": "Cross-check",
        "wang_yes": "✓ Proved: the rules + your answers ⇒ this fault",
        "wang_no": "✕ Your answers do not prove this fault",
        "confidence": "Confidence {p:.0%}",
        "no_fault": "Not enough evidence", "no_fault_sub": "No fault reached a confidence of 20%.",
        "derived": "What the program could work out", "check_more": "Check these points, then diagnose again:",
        "nothing_derived": "Your answers match no rule. Try another method or another system.",
        "disclaimer": "Illustrative rules; a likely fault is not a confirmed inspection.",
        "new": "New diagnosis",
        "method_guided": "Guided questions", "method_symptoms": "Symptom checklist", "method_talk": "Described in words",
        "unknown_bike": "Bike type not given",
    },
}

KINDS = {"scooter": "is_scooter", "manual": "is_manual"}
FUELS = {"fi": "is_fuel_injected", "carb": "is_carburetor"}
METHODS = ("guided", "symptoms", "talk")
LIKELY_AT = 0.6  # below this CF the result is headed "possible fault", not "likely fault"
VEHICLE = set(KINDS.values()) | set(FUELS.values())


# ---------------------------------------------------------------------------
# Logic (no drawing)
# ---------------------------------------------------------------------------

def new_dx() -> Dict[str, object]:
    """A fresh diagnosis (what app.state["dx"] holds)."""
    return {"step": 1, "kind": "scooter", "fuel": "", "model": "", "method": "guided", "part": ALL, "part_asked": False,
            "answers": [],
            "selected": [], "filter": "", "query": "", "text": "", "replies": [], "chat": [], "record": None,
            "wang": None}


def vehicle_answers(kind: str, fuel: str, model: str = "", models: Optional[Dict[str, dict]] = None
                    ) -> Dict[str, bool]:
    """Answers given by step 1: the chosen type is yes, the other one no; "" = not sure.
    With the knowledge base's `models`, every listed model is answered too, and a model gives its clutch."""
    out: Dict[str, bool] = {}
    for choice, table in ((kind, KINDS), (fuel, FUELS)):
        if choice:
            out.update({sym: key == choice for key, sym in table.items()})
    if models:
        out.update({m: m == model for m in models})
        if model in models:
            out["has_clutch_lever"] = bool(models[model]["clutch"])
    return out


def pick_model(kb: KnowledgeBase, dx: Dict[str, object], model: str) -> None:
    """Step 1: a listed model fills in its type and fuel; "" = another bike (type and fuel chosen by hand)."""
    dx["model"] = model
    if model:
        dx.update(kind=kb.models[model]["kind"], fuel=kb.models[model]["fuel"])


def model_name(kb: KnowledgeBase, model: str) -> str:
    return kb.models.get(model, {}).get("name", "")


def subsystem_counts(kb: KnowledgeBase) -> List[Tuple[str, int]]:
    """(part, number of faults) in the usual order."""
    counts: Dict[str, int] = {}
    for sym in kb.faults.values():
        counts[sym.subsystem] = counts.get(sym.subsystem, 0) + 1
    return [(sub, counts.get(sub, 0)) for sub in SUBSYSTEM_ORDER]


# --- step 2a: step-by-step questions (Khoa's BackwardSession) ---------------------------------------------
def guided_session(kb: KnowledgeBase, dx: Dict[str, object]) -> BackwardSession:
    """The backward session for the answers kept in dx (rebuilt each time: the engine is deterministic)."""
    answers = dict(vehicle_answers(dx["kind"], dx["fuel"], dx.get("model", ""), kb.models))
    answers.update(dict(dx["answers"]))
    return BackwardSession(kb, goals_for(kb, dx["part"]), answers=answers)


def needs_part(dx: Dict[str, object]) -> bool:
    """Ask "where is the problem?" before the first question (9 questions instead of ~40)."""
    return dx["method"] == "guided" and dx["part"] == ALL and not dx["answers"] and not dx.get("part_asked")


def to_guided(dx: Dict[str, object]) -> None:
    """Leave "describe in words" for the guided questions; the text is kept to come back to."""
    dx.update(method="guided", step=2, part=ALL, part_asked=False, answers=[], record=None, wang=None)


def answer_label(value, lang: str) -> str:
    return TEXT[lang]["a_unknown" if value is UNKNOWN else "a_yes" if value else "a_no"]


# --- step 2b: symptom checklist (forward chaining) --------------------------------------------------------
def checklist(kb: KnowledgeBase, lang: str, query: str = "", part: str = "") -> List[Tuple[str, List[str]]]:
    """(part, symptoms) matching the search and the part filter; vehicle-type questions are in step 1."""
    out = []
    for sub, ids in symptom_groups(kb, lang):
        if part and sub != part:
            continue
        shown = [s for s in ids if matches(search_key(kb, s, lang), query)]
        if shown:
            out.append((sub, shown))
    return out


# --- step 2c: described in words (Lâm's nlu + interview) ---------------------------------------------------
def talk_interview(kb: KnowledgeBase, dx: Dict[str, object]):
    """(Interview, matches) for the text and the replies kept in dx."""
    found = extract(dx["text"], kb.symptoms) if dx["text"].strip() else []
    start = dict(vehicle_answers(dx["kind"], dx["fuel"], dx.get("model", ""), kb.models))
    start.update({m.symptom: m.value for m in found})
    iv = Interview(kb, start)
    for symptom, value in dx["replies"]:
        iv.answer(symptom, value)
    return iv, found


# --- step 3: result -----------------------------------------------------------------------------------------
@dataclass
class Record:
    """One finished diagnosis (also one row of the session history)."""
    number: int
    time: str
    kind: str
    fuel: str
    method: str
    yes: List[str]          # every "yes" answer, vehicle type included (what Wang uses)
    result: object          # ForwardResult or BackwardResult: .diagnoses and .wm
    model: str = ""         # bike model (models.json), "" for another bike


def make_record(kb: KnowledgeBase, dx: Dict[str, object], number: int) -> Record:
    """Run the chosen engine on the answers in dx."""
    method = dx["method"]
    if method == "guided":
        session = guided_session(kb, dx)
        yes = [s for s, v in session.answers.items() if v not in (None, False)]
        result = session.result
    elif method == "talk":
        iv, _ = talk_interview(kb, dx)
        yes = [s for s, v in iv.answers.items() if v]
        result = iv.result()
    else:
        yes = [s for s, v in vehicle_answers(dx["kind"], dx["fuel"], dx.get("model", ""), kb.models).items() if v] \
            + list(dx["selected"])
        result = forward_chain(kb, yes)
    model = model_of(kb, {s: True for s in yes}, dx.get("model", ""))  # chosen in step 1, or named in the text
    return Record(number, _dt.datetime.now().strftime("%H:%M"), dx["kind"], dx["fuel"], method, yes, result, model)


@dataclass
class RuleStep:
    rules: str              # "SF02, SF14"
    inputs: List[str]       # what the rider said, used by this step
    conclusion: str
    cf: float


@dataclass
class Summary:
    fault: str              # "" when no fault reached the threshold
    name: str
    cf: float
    severity: Optional[str]
    action: str
    subsystem: str
    chain: List[str]        # rule ids in firing order
    observations: int
    steps: List[RuleStep]
    alternatives: List[Tuple[str, float]]
    near: list


def summarize(kb: KnowledgeBase, rec: Record, lang: str) -> Summary:
    """What step 3 shows for a record."""
    obs = len([s for s in rec.yes if s not in VEHICLE and kb.symbols[s].subsystem != "vehicle"])
    ds = rec.result.diagnoses
    if not ds:
        return Summary("", "", 0.0, None, "", "", [], obs, [], [], near_misses(kb, rec.result.wm))
    top = ds[0]
    steps, inputs, chain = [], [], []
    for row in how_rows(kb, rec.result.wm, top.fault, lang):
        if row.is_rule:
            steps.append(RuleStep(row.label, inputs, row.text.lstrip("→ "), row.cf))
            chain += row.label.split(", ")
            inputs = []
        else:
            inputs.append(row.text)
    alternatives = [(kb.text(d.fault, lang), d.cf) for d in ds[1:3]]
    return Summary(top.fault, kb.text(top.fault, lang), top.cf, top.severity, kb.action(top.fault, lang),
                   kb.symbols[top.fault].subsystem, chain, obs, steps, alternatives, [])


def wang_check(kb: KnowledgeBase, rec: Record, fault: str) -> bool:
    """Wang's algorithm: do the rules and the "yes" answers prove this fault?"""
    return entails(kb, rec.yes, fault).valid


def session_number(state: Dict[str, object]) -> int:
    """Number shown in the top bar: the opened result, or the next one."""
    history, dx = state.get("history", []), state.get("dx") or {}
    if dx.get("step") == 3 and dx.get("record") is not None:
        return history[dx["record"]].number
    return len(history) + 1


def bike_text(kind: str, fuel: str, lang: str, name: str = "") -> str:
    if name:  # a listed model says it all
        return name
    t = TEXT[lang]
    parts = [t[kind]] if kind else [t["unknown_bike"]]
    if fuel:
        parts.append(t[fuel])
    return " · ".join(parts)


# ---------------------------------------------------------------------------
# Drawing
# ---------------------------------------------------------------------------

class DiagnosisPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        self.t = TEXT[app.lang]
        self.dx = app.state.setdefault("dx", new_dx())
        app.state.setdefault("history", [])
        self.scroll = ScrollFrame(self, bg="bg")
        self.scroll.pack(fill="both", expand=True)
        self.render()

    def on_show(self) -> None:
        self.dx = self.app.state["dx"]  # history may have opened another session
        self.render()

    # --- helpers ---
    def go(self, step: int) -> None:
        self.dx["step"] = step
        self.render()

    def set(self, **kw) -> None:
        self.dx.update(kw)
        self.render()

    def header(self, parent, e: str, title: str, sub: str, step: int, compact: bool = False) -> None:
        """Title, subtitle and the 3 steps; compact (steps 2 and 3) keeps the question in view."""
        eyebrow(parent, e).pack(anchor="w")
        label(parent, title, "big" if compact else "hero", bg="bg").pack(anchor="w", pady=(px(2 if compact else 6), 0))
        autowrap(label(parent, sub, "body" if compact else "lead", "muted", bg="bg")).pack(
            fill="x", pady=(px(2), px(10 if compact else 18)))
        names = [self.t["steps_done"][i] if i < step - 1 else self.t["steps"][i] for i in range(3)]
        Stepper(parent, names, step).pack(fill="x", pady=(0, px(12 if compact else 20)))

    def columns(self, parent) -> Tuple[tk.Frame, tk.Frame]:
        row = tk.Frame(parent, bg=C["bg"])
        row.pack(fill="x")
        row.columnconfigure(0, weight=3, uniform="col")
        row.columnconfigure(1, weight=2, uniform="col")
        left = tk.Frame(row, bg=C["bg"])
        left.grid(row=0, column=0, sticky="nsew", padx=(0, px(16)))
        right = tk.Frame(row, bg=C["bg"])
        right.grid(row=0, column=1, sticky="nsew")
        return left, right

    def footer(self, parent) -> tk.Frame:
        f = tk.Frame(parent, bg=C["bg"])
        f.pack(fill="x", pady=(px(18), px(8)))
        return f

    def render(self) -> None:
        self.t = TEXT[self.app.lang]
        self.scroll.clear()
        page = tk.Frame(self.scroll.inner, bg=C["bg"], padx=px(8))
        page.pack(fill="both", expand=True)
        step = self.dx["step"]
        if step == 1:
            self.render_setup(page)
        elif step == 2:
            {"guided": self.render_guided, "symptoms": self.render_checklist, "talk": self.render_talk}[
                self.dx["method"]](page)
        else:
            self.render_result(page)

    # --- step 1 ---
    def render_setup(self, page) -> None:
        t, kb, dx = self.t, self.app.kb, self.dx
        self.header(page, t["e1"], t["t1"], t["s1"], 1, compact=True)
        card = RoundCard(page)  # full width: the 3 methods sit side by side and Start shows without scrolling
        card.pack(fill="x")
        b = card.body
        label(b, t["bike"], "h2").pack(anchor="w", pady=(0, px(12)))
        models = tk.Frame(b, bg=C["surface"])  # a listed model fills in type, fuel and clutch (models.json)
        models.pack(fill="x")
        choices = [(m, kb.models[m]["name"]) for m in sorted(kb.models, key=lambda m: (kb.models[m]["kind"] != "scooter",
                                                                                      kb.models[m]["name"]))]
        for i, (m, name) in enumerate(choices + [("", t["other_bike"])]):
            models.columnconfigure(i, weight=1, uniform="model")
            on = dx.get("model", "") == m
            c = tk.Label(models, text=name, font=F["small_bold" if on else "small"], cursor="hand2", anchor="w",
                         justify="left", bg=C["panel"] if on else C["surface"], fg=C["on_panel"] if on else C["text"],
                         padx=px(10), pady=px(7), highlightthickness=1,
                         highlightbackground=C["panel"] if on else C["border"])
            autowrap(c, pad=px(24))
            c.grid(row=0, column=i, sticky="nsew", padx=(0, px(8)))
            c.bind("<Button-1>", lambda e, m=m: self.choose_model(m))
        if not dx.get("model"):  # another bike: type by hand
            kinds = tk.Frame(b, bg=C["surface"])
            kinds.pack(fill="x", pady=(px(12), 0))
            for i, k in enumerate(("scooter", "manual")):
                kinds.columnconfigure(i, weight=1, uniform="kind")
                ChoiceCard(kinds, t[k], t[k + "_sub"], dx["kind"] == k, lambda k=k: self.set(kind=k),
                           icon_name=k).grid(row=0, column=i, sticky="we", padx=(0 if i == 0 else px(10), 0))
        fuel = tk.Frame(b, bg=C["surface"])
        fuel.pack(fill="x", pady=(px(12), 0))
        fuel.columnconfigure(2, weight=1)
        if not dx.get("model"):  # another bike: fuel by hand
            label(fuel, t["fuel"], "small_bold", "muted").grid(row=0, column=0, padx=(0, px(10)))
            Segmented(fuel, [("fi", t["fi"]), ("carb", t["carb"]), ("", t["unsure"])], dx["fuel"],
                      lambda v: self.dx.update(fuel=v)).grid(row=0, column=1)
        safe = tk.Frame(fuel, bg=C["surface"])
        safe.grid(row=0, column=2, sticky="e", padx=(px(24), 0))
        icon(safe, "shield", 20, "accent").pack(side="left", padx=(0, px(8)))
        label(safe, t["safety"] + ". " + t["safety_sub"], "small", "muted").pack(side="left")
        label(b, t["how"], "h2").pack(anchor="w", pady=(px(18), px(10)))
        methods = tk.Frame(b, bg=C["surface"])
        methods.pack(fill="x")
        for i, m in enumerate(METHODS):
            methods.columnconfigure(i, weight=1, uniform="method")
            ChoiceCard(methods, t[m], t[m + "_sub"], dx["method"] == m, lambda m=m: self.set(method=m),
                       note=t[m + "_note"], badge=t["recommended"] if m == "guided" else "").grid(
                row=0, column=i, sticky="nswe", padx=(0 if i == 0 else px(10), 0))

        f = self.footer(page)
        label(f, t["no_sensor"], "body", "muted", bg="bg").pack(side="left")
        PillButton(f, t["start"], self.start).pack(side="right")

    def choose_model(self, model: str) -> None:
        pick_model(self.app.kb, self.dx, model)
        self.render()

    def start(self) -> None:
        self.dx.update(step=2, answers=[], selected=[], replies=[], chat=[], record=None, wang=None, part_asked=False)
        if self.dx["method"] != "talk":
            self.dx["text"] = ""
        self.render()
        if self.dx["method"] == "guided":
            self.check_finished()

    # --- step 2a ---
    def render_guided(self, page) -> None:
        t, kb, dx, lang = self.t, self.app.kb, self.dx, self.app.lang
        session = guided_session(kb, dx)
        part = t["all"] if dx["part"] == ALL else SUBSYSTEM_NAMES[lang][dx["part"]]
        self.header(page, t["e2a"], t["t2a"], " · ".join((bike_text(dx["kind"], dx["fuel"], lang, model_name(kb, dx["model"])),
                                                           t["guided_note"], part)), 2, compact=True)
        if needs_part(dx):
            return self.render_part_card(page)
        parts = tk.Frame(page, bg=C["bg"])
        parts.pack(fill="x", pady=(0, px(10)))
        label(parts, t["part"], "small_bold", "muted", bg="bg").pack(side="left", padx=(0, px(10)))
        Segmented(parts, [(ALL, t["all"])] + [(s, SUBSYSTEM_NAMES[lang][s]) for s in SUBSYSTEM_ORDER],
                  dx["part"], self.change_part, bg="bg").pack(side="left")
        q = question_view(kb, session, lang)
        if q is None:  # no question left (all answered); show the result
            return self.after_idle(self.finish)
        number = len(dx["answers"]) + 1
        left, right = self.columns(page)
        self.question_card(left, number, q.text, q.hint, self.answer_guided)
        panel = RoundCard(right, fill="panel", border=None, grow=True)
        panel.pack(fill="both", expand=True)
        p = panel.body
        eyebrow(p, t["why"], bg="panel", fg="lime").pack(anchor="w")
        autowrap(label(p, t["checking"].format(goal=q.goal) if q.goal else t["why"], "h2", "on_panel",
                       bg="panel")).pack(fill="x", pady=(px(8), px(6)))
        autowrap(label(p, t["why_sub"], "body", "panel_muted", bg="panel")).pack(fill="x")
        for i, row in enumerate(q.why[:2]):
            if i == 1:
                label(p, t["leads"], "small", "panel_muted", bg="panel").pack(anchor="w", pady=(px(10), 0))
            box = RoundCard(p, fill="panel_soft", border=None, radius=12, bg="panel", pad=14)
            box.pack(fill="x", pady=(px(12) if i == 0 else px(4), 0))
            label(box.body, t["testing"].format(rule=row.rule), "eyebrow", "lime", bg="panel_soft").pack(anchor="w")
            premises = " + ".join(("▸ " if state == "asking" else "✓ " if state == "yes" else "") + text
                                  for text, state in row.premises)
            autowrap(label(box.body, premises, "body", "on_panel", bg="panel_soft")).pack(fill="x", pady=(px(6), 0))
            autowrap(label(box.body, "→ " + row.conclusion, "heading", "on_panel", bg="panel_soft")).pack(fill="x")
        label(p, t["open"].format(n=len(q.open), total=q.total), "small", "panel_muted", bg="panel").pack(
            anchor="w", pady=(px(14), 0))
        label(p, t["illustrative"], "small", "panel_muted", bg="panel").pack(anchor="w", side="bottom")
        self.answers_strip(left, [(short(kb, s, lang), answer_label(v, lang)) for s, v in dx["answers"]],
                           self.undo_guided)
        f = self.footer(page)
        link(f, "← " + t["previous"], self.undo_guided, bg="bg", font="body").pack(side="left")
        link(f, t["change"], lambda: self.go(1), bg="bg", font="body").pack(side="left", padx=(px(24), 0))

    def render_part_card(self, page) -> None:
        t, lang = self.t, self.app.lang
        card = RoundCard(page)  # full width: three columns of systems fit even the smallest window
        card.pack(fill="x")
        b = card.body
        label(b, t["where"], "big").pack(anchor="w")
        autowrap(label(b, t["where_sub"] + " " + t["where_why_sub"], "lead", "muted")).pack(
            fill="x", pady=(px(4), px(14)))
        grid = tk.Frame(b, bg=C["surface"])
        grid.pack(fill="x")
        counts = dict(subsystem_counts(self.app.kb))
        for i, sub in enumerate(SUBSYSTEM_ORDER):
            grid.columnconfigure(i % 3, weight=1, uniform="part")
            ChoiceCard(grid, SUBSYSTEM_NAMES[lang][sub], t["n_faults"].format(n=counts[sub]), False,
                       lambda s=sub: self.change_part(s), icon_name=SUBSYSTEM_ICONS[sub], radio=False).grid(
                row=i // 3, column=i % 3, sticky="nsew", padx=(0 if i % 3 == 0 else px(10), 0), pady=(0, px(10)))
        ChoiceCard(b, t["not_sure_part"], t["not_sure_part_sub"], False, self.ask_all, icon_name="info",
                   radio=False).pack(fill="x")
        autowrap(label(b, t["where_note"], "small", "muted")).pack(fill="x", pady=(px(12), 0))
        f = self.footer(page)
        link(f, "← " + t["change"], lambda: self.go(1), bg="bg", font="body").pack(side="left")

    def ask_all(self) -> None:
        self.dx["part_asked"] = True
        self.render()

    def question_card(self, parent, number: int, text: str, hint: str, on_answer) -> None:
        t = self.t
        card = RoundCard(parent)
        card.pack(fill="x")
        b = card.body
        chip(b, t["question"].format(n=number), C["accent"], C["lime_soft"]).pack(anchor="w")
        autowrap(label(b, text, "big")).pack(fill="x", pady=(px(14), px(8)))
        if hint:
            autowrap(label(b, hint, "lead", "muted")).pack(fill="x")
        row = tk.Frame(b, bg=C["surface"])
        row.pack(fill="x", pady=(px(20), px(8)))
        PillButton(row, t["yes"], lambda: on_answer(True), arrow=False, bg="surface", height=54,
                   width=170).pack(side="left")
        PillButton(row, t["no"], lambda: on_answer(False), style="outline", arrow=False, bg="surface", height=54,
                   width=170).pack(side="left", padx=(px(12), 0))
        link(b, t["skip"], lambda: on_answer(UNKNOWN), font="body", fg="muted").pack(anchor="w", pady=(px(6), 0))

    def answers_strip(self, parent, items: List[Tuple[str, str]], on_edit) -> None:
        """Latest answers, under the question card so they stay in view."""
        t = self.t
        card = RoundCard(parent, radius=14, pad=16)
        card.pack(fill="x", pady=(px(16), 0))
        head = tk.Frame(card.body, bg=C["surface"])
        head.pack(fill="x")
        label(head, t["answered"], "small_bold", "muted").pack(side="left")
        if items:
            link(head, t["edit"], on_edit).pack(side="right")
        chips = tk.Frame(card.body, bg=C["surface"])
        chips.pack(fill="x", pady=(px(8), 0))
        if not items:
            label(chips, t["none_yet"], "body", "muted").pack(anchor="w")
        for text, answer in items[-4:]:  # the latest answers, one per line, wrapped (never clipped)
            chip(chips, f"{text}: {answer}", C["text"], C["chrome"]).pack(anchor="w", pady=px(2))
        chips.bind("<Configure>", lambda e: [c.configure(wraplength=max(40, e.width - px(20)), justify="left")
                                             for c in chips.winfo_children() if isinstance(c, tk.Label)])

    def change_part(self, part: str) -> None:
        self.dx.update(part=part, answers=[], part_asked=True)
        self.render()

    def answer_guided(self, value) -> None:
        session = guided_session(self.app.kb, self.dx)
        if session.question is None:
            return self.finish()
        self.dx["answers"].append((session.question.symptom, value))
        self.check_finished()
        if self.dx["step"] == 2:
            self.render()

    def check_finished(self) -> None:
        if self.dx["method"] == "guided" and guided_session(self.app.kb, self.dx).finished:
            self.finish()

    def undo_guided(self) -> None:
        if self.dx["answers"]:
            self.dx["answers"].pop()
            self.render()

    # --- step 2b ---
    def render_checklist(self, page) -> None:
        t, dx, lang = self.t, self.dx, self.app.lang
        self.header(page, t["e2b"], t["t2b"], t["s2b"], 2, compact=True)
        left, right = self.columns(page)
        card = RoundCard(left)
        card.pack(fill="x")
        b = card.body
        self.query = HintEntry(b, t["search"], lambda: self.after_idle(self.refresh_checklist))
        if dx["query"]:
            self.query._hide()
            self.query.var.set(dx["query"])
        self.query.pack(fill="x", ipady=px(4))
        filters = tk.Frame(b, bg=C["surface"])
        filters.pack(fill="x", pady=(px(12), 0))
        for i, sub in enumerate(SUBSYSTEM_ORDER):
            filters.columnconfigure(i % 3, weight=1, uniform="filter")
            on = dx["filter"] == sub
            f = tk.Label(filters, text=SUBSYSTEM_NAMES[lang][sub], font=F["small_bold" if on else "small"],
                         bg=C["panel"] if on else C["surface"], fg=C["on_panel"] if on else C["text"], anchor="w",
                         padx=px(10), pady=px(7), cursor="hand2", highlightthickness=1,
                         highlightbackground=C["panel"] if on else C["border"])
            autowrap(f, pad=px(24))
            f.grid(row=i // 3, column=i % 3, sticky="we", padx=(0, px(8)), pady=(0, px(8)))
            f.bind("<Button-1>", lambda e, s=sub: self.set_filter(s))
        self.list = tk.Frame(b, bg=C["surface"])
        self.list.pack(fill="x")
        self.side = right
        self.refresh_checklist(first=True)
        f = self.footer(page)
        link(f, "← " + t["change"], lambda: self.go(1), bg="bg", font="body").pack(side="left")
        self.find = PillButton(f, t["find"], self.finish)
        self.find.pack(side="right")
        self.find.set_enabled(bool(dx["selected"]))

    def set_filter(self, sub: str) -> None:
        self.dx["filter"] = "" if self.dx["filter"] == sub else sub
        self.render()

    def toggle_symptom(self, sid: str) -> None:
        sel = self.dx["selected"]
        sel.remove(sid) if sid in sel else sel.append(sid)
        self.refresh_checklist()

    def refresh_checklist(self, first: bool = False) -> None:
        t, kb, dx, lang = self.t, self.app.kb, self.dx, self.app.lang
        if not first:
            dx["query"] = self.query.value()
        for w in self.list.winfo_children():
            w.destroy()
        groups = checklist(kb, lang, dx["query"], dx["filter"])
        if not groups:
            label(self.list, t["no_match"], "body", "muted").pack(anchor="w", pady=px(10))
        for sub, ids in groups:
            label(self.list, t["checks"].format(part=SUBSYSTEM_NAMES[lang][sub]), "h2").pack(
                anchor="w", pady=(px(14), px(8)))
            for sid in ids:
                CheckRow(self.list, short(kb, sid, lang), sid in dx["selected"],
                         lambda s=sid: self.toggle_symptom(s)).pack(fill="x", pady=(0, px(8)))
        for w in self.side.winfo_children():
            w.destroy()
        panel = RoundCard(self.side, fill="panel", border=None)
        panel.pack(fill="x")
        p = panel.body
        autowrap(label(p, t["observations"], "h2", "on_panel", bg="panel")).pack(fill="x")
        autowrap(label(p, f"{bike_text(dx['kind'], dx['fuel'], lang, model_name(kb, dx['model']))} · {t['symptoms_note']}", "body", "panel_muted",
                       bg="panel")).pack(fill="x", pady=(px(4), px(12)))
        chip(p, t["n_selected"].format(n=len(dx["selected"])), C["on_lime"], C["lime"]).pack(anchor="w")
        if not dx["selected"]:
            label(p, t["nothing_selected"], "body", "panel_muted", bg="panel").pack(anchor="w", pady=(px(10), 0))
        for sid in dx["selected"][:8]:
            row = tk.Frame(p, bg=C["panel"])
            row.pack(fill="x", pady=(px(8), 0))
            label(row, "✓", "heading", "lime", bg="panel").pack(side="left", anchor="n", padx=(0, px(10)))
            autowrap(label(row, short(kb, sid, lang), "body", "on_panel", bg="panel")).pack(side="left", fill="x",
                                                                                         expand=True)
        if len(dx["selected"]) > 8:
            label(p, t["more"].format(n=len(dx["selected"]) - 8), "small", "panel_muted", bg="panel").pack(
                anchor="w", pady=(px(6), 0))
        tk.Frame(p, bg=C["panel_soft"], height=1).pack(fill="x", pady=px(16))
        label(p, t["next"], "h2", "on_panel", bg="panel").pack(anchor="w")
        autowrap(label(p, t["next_sub"], "body", "panel_muted", bg="panel")).pack(fill="x", pady=(px(6), px(10)))
        autowrap(label(p, t["next_note"], "body", "lime", bg="panel")).pack(fill="x")
        if hasattr(self, "find") and not first:
            self.find.set_enabled(bool(dx["selected"]))

    # --- step 2c: a conversation; every reply is built from the rules (chat.py) ---
    def render_talk(self, page) -> None:
        t, kb, dx, lang = self.t, self.app.kb, self.dx, self.app.lang
        self.header(page, t["e2c"], t["t2c"], t["s2c"], 2, compact=True)
        talking = bool(dx.get("chat"))
        iv, found = talk_interview(kb, dx) if dx["text"].strip() else (None, [])
        left, right = self.columns(page)
        if talking:
            self.chat_card(left, iv)
        else:  # the first description, or nothing recognised in it
            card = RoundCard(left)
            card.pack(fill="x")
            label(card.body, t["talk_box"], "h2").pack(anchor="w")
            self.text = tk.Text(card.body, height=5, wrap="word", font=F["lead"], relief="flat",
                                bg=C["bg"], fg=C["text"], insertbackground=C["text"], padx=px(10), pady=px(8),
                                highlightthickness=1, highlightbackground=C["border"], highlightcolor=C["accent"])
            self.text.insert("1.0", dx["text"])
            self.text.pack(fill="x", pady=(px(10), px(6)))
            label(card.body, t["try"], "small_bold", "muted").pack(anchor="w", pady=(px(4), 0))
            for ex in t["examples"]:
                c = autowrap(chip(card.body, f"“{ex}”", C["accent"], C["chrome"]), pad=px(20))
                c.configure(cursor="hand2", anchor="w", justify="left", font=F["body"], pady=px(4))
                c.pack(fill="x", pady=(px(6), 0))
                c.bind("<Button-1>", lambda e, ex=ex: self.use_example(ex))
            if dx["text"].strip() and not found:
                autowrap(label(card.body, t["understood_none"], "body", "warn")).pack(fill="x", pady=(px(8), 0))
            row = tk.Frame(card.body, bg=C["surface"])
            row.pack(fill="x", pady=(px(14), 0))
            PillButton(row, t["analyze"], self.analyze, bg="surface").pack(side="left")
            if dx["text"].strip() and not found:
                PillButton(row, t["to_guided"], self.switch_to_guided, style="outline", bg="surface").pack(
                    side="left", padx=(px(12), 0))
        panel = RoundCard(right, fill="panel", border=None, grow=True)
        panel.pack(fill="both", expand=True)
        p = panel.body
        eyebrow(p, t["understood"] if found else t["how_read"], bg="panel", fg="lime").pack(anchor="w", pady=(0, px(6)))
        if not found:  # empty state: say what the program can read from the text
            autowrap(label(p, t["talk_reads"], "body", "panel_muted", bg="panel")).pack(fill="x")
            for line in t["talk_kinds"]:
                autowrap(label(p, "•  " + line, "body", "on_panel", bg="panel")).pack(fill="x", pady=(px(8), 0))
        for m in found:
            autowrap(label(p, ("✓ " if m.value else "✕ ") + short(kb, m.symptom, lang), "body",
                           "on_panel" if m.value else "panel_muted", bg="panel")).pack(fill="x", pady=px(2))
        if talking and found:
            proved = {d.fault for d in iv.result().diagnoses}
            eyebrow(p, t["beliefs"], bg="panel", fg="lime").pack(anchor="w", pady=(px(18), px(6)))
            for fault, prob in iv.beliefs(3):
                row = tk.Frame(p, bg=C["panel"])
                row.pack(fill="x", pady=(px(6), 0))
                label(row, f"{prob:.0%}", "heading", "lime", bg="panel", width=5).pack(side="left", anchor="n")
                autowrap(label(row, kb.text(fault, lang) + (f"  ·  {t['by_rules']}" if fault in proved else ""),
                               "body", "on_panel", bg="panel")).pack(side="left", fill="x", expand=True)
        f = self.footer(page)
        link(f, "← " + t["change"], lambda: self.go(1), bg="bg", font="body").pack(side="left")
        if talking:
            link(f, t["restart_chat"], lambda: self.send(t["restart_chat"], restart=True), bg="bg", font="body").pack(
                side="left", padx=(px(24), 0))
            PillButton(f, t["see_result"], self.finish).pack(side="right")
            # newest message in view, after RoundCard has refitted its height (60 ms)
            self.after(150, lambda: self.scroll.winfo_exists() and self.scroll.canvas.yview_moveto(1.0))

    def chat_card(self, parent, iv) -> None:
        t = self.t
        card = RoundCard(parent)
        card.pack(fill="x")
        b = card.body
        label(b, t["chat_title"], "h2").pack(anchor="w")
        autowrap(label(b, t["chat_sub"], "small", "muted")).pack(fill="x", pady=(px(2), px(10)))
        for who, text in self.dx["chat"]:
            mine = who == "you"
            fill = "lime_soft" if mine else "chrome"
            bubble = tk.Frame(b, bg=C[fill], padx=px(12), pady=px(8))
            bubble.pack(fill="x", pady=(px(6), 0), padx=(px(56), 0) if mine else (0, px(56)))
            autowrap(label(bubble, text, "body", bg=fill)).pack(fill="x")
        quick = (t["quick_q"] if iv is not None and iv.next_question() is not None else []) + t["quick"]
        row = tk.Frame(b, bg=C["surface"])
        row.pack(fill="x", pady=(px(14), 0))
        for i, text in enumerate(quick):
            c = chip(row, text, C["accent"], C["chrome"])
            c.configure(cursor="hand2", font=F["body"], pady=px(4))
            c.grid(row=i // 4, column=i % 4, sticky="w", padx=(0, px(8)), pady=(0, px(6)))
            c.bind("<Button-1>", lambda e, text=text: self.send(text))
        box = tk.Frame(b, bg=C["surface"])
        box.pack(fill="x", pady=(px(8), 0))
        self.entry = HintEntry(box, t["chat_hint"])
        self.entry.pack(side="left", fill="x", expand=True, ipady=px(6), padx=(0, px(10)))
        self.entry.bind("<Return>", lambda e: self.send())
        PillButton(box, t["send"], self.send, bg="surface").pack(side="right")
        entry = self.entry  # the screen may be rebuilt before idle time
        self.after_idle(lambda: entry.winfo_exists() and entry.focus_set())

    def send(self, text: Optional[str] = None, restart: bool = False) -> None:
        """One message from the rider: answers, more symptoms or a question; the reply comes from chat.py."""
        text = (self.entry.value() if text is None else text).strip()
        if restart:
            self.dx.update(text="", replies=[], chat=[])
        elif not text:
            return
        elif chat.intent(text) == "result":
            return self.finish()
        else:
            chat.respond(self.app.kb, self.dx, text, self.app.lang)
        self.render()

    def switch_to_guided(self) -> None:
        to_guided(self.dx)
        self.render()

    def use_example(self, sentence: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", sentence)
        self.text.focus_set()

    def analyze(self) -> None:
        text = self.text.get("1.0", "end").strip()
        if extract(text, self.app.kb.symptoms):
            chat.start(self.app.kb, self.dx, text, self.app.lang)
        else:  # nothing recognised: keep the text box, with a way out to the guided questions
            self.dx.update(text=text, replies=[], chat=[])
        self.render()

    # --- step 3 ---
    def finish(self) -> None:
        if self.dx["step"] != 2:
            return
        history = self.app.state["history"]
        history.append(make_record(self.app.kb, self.dx, len(history) + 1))
        self.dx.update(step=3, record=len(history) - 1, wang=None)
        self.refresh_topbar()
        self.render()

    def refresh_topbar(self) -> None:
        refresh = getattr(self.app, "refresh_topbar", None)
        if refresh:
            refresh()

    def render_result(self, page) -> None:
        t, kb, lang = self.t, self.app.kb, self.app.lang
        rec: Record = self.app.state["history"][self.dx["record"]]
        s = summarize(kb, rec, lang)
        self.header(page, t["e3"], t["t3"], " · ".join((bike_text(rec.kind, rec.fuel, lang, model_name(kb, rec.model)),
                                                         t["method_" + rec.method])), 3, compact=True)
        banner = RoundCard(page, fill="panel", border=None, pad=22)
        banner.pack(fill="x")
        b = banner.body
        b.columnconfigure(1, weight=1)
        box = tk.Canvas(b, width=px(72), height=px(72), bg=C["panel"], highlightthickness=0, bd=0)
        round_rect(box, 0, 0, px(72), px(72), px(16), fill=C["lime"], outline="")
        box.grid(row=0, column=0, rowspan=3, padx=(0, px(18)))
        mark = SUBSYSTEM_ICONS.get(s.subsystem, "info") if s.fault else "info"
        sub = tk.Canvas(box, width=px(40), height=px(40), bg=C["lime"], highlightthickness=0, bd=0)
        box.create_window(px(36), px(36), window=sub)
        _draw_icon(sub, mark, px(40), C["on_lime"])
        head = ("likely" if s.cf >= LIKELY_AT else "possible") if s.fault else "no_fault"
        label(b, t[head].upper(), "eyebrow", "lime", bg="panel").grid(
            row=0, column=1, sticky="w")
        autowrap(label(b, s.name if s.fault else t["no_fault_sub"], "big", "on_panel", bg="panel")).grid(
            row=1, column=1, sticky="we")
        if s.fault:
            autowrap(label(b, t["chain"].format(chain=" → ".join(st.rules for st in s.steps)), "body",
                           "panel_muted", bg="panel")).grid(row=2, column=1, sticky="we")
            Gauge(b, s.cf, size=150, caption=t["confidence"].format(p=s.cf), note=f"CF {s.cf:.2f}").grid(row=0, column=2, rowspan=3, padx=px(12))
        for col, (num, cap) in enumerate(((s.observations, t["obs"]), (len(s.chain), t["rules_used"])), 3):
            stat = tk.Frame(b, bg=C["panel"], padx=px(18))
            stat.grid(row=0, column=col, rowspan=3)
            label(stat, str(num), "big", "lime", bg="panel").pack()
            label(stat, cap, "small", "panel_muted", bg="panel").pack()

        left, right = self.columns(page)
        left.master.pack_configure(pady=(px(16), 0))
        card = RoundCard(left)
        card.pack(fill="x")
        c = card.body
        if s.fault:
            label(c, t["reach"], "h2").pack(anchor="w")
            label(c, t["reach_sub"], "body", "muted").pack(anchor="w", pady=(px(2), px(12)))
            for i, st in enumerate(s.steps):
                last = i == len(s.steps) - 1
                if i:
                    label(c, "↓", "heading", "muted").pack(anchor="w", padx=px(20))
                rc = RoundCard(c, fill="lime_soft" if last else "surface", radius=12, bg="surface", pad=14)
                rc.pack(fill="x", pady=(px(4), 0))
                r = rc.body
                fill = "lime_soft" if last else "surface"
                r.columnconfigure(1, weight=1)
                chip(r, st.rules, C["on_panel"] if last else C["accent"], C["panel"] if last else C["chrome"]).grid(
                    row=0, column=0, rowspan=2, sticky="n", padx=(0, px(12)))
                if st.inputs:
                    autowrap(label(r, " + ".join(st.inputs), "body", bg=fill)).grid(row=0, column=1, sticky="we")
                autowrap(label(r, f"→ {st.conclusion}   ({st.cf:.2f})", "heading", "accent", bg=fill)).grid(
                    row=1, column=1, sticky="we", pady=(px(4), 0))
        else:
            self.render_near(c, s)
        if s.fault:
            nxt = RoundCard(right, fill="lime_soft", border="border")
            nxt.pack(fill="x")
            n = nxt.body
            label(n, t["next_step"], "h2", bg="lime_soft").pack(anchor="w")
            autowrap(label(n, s.action, "lead", bg="lime_soft")).pack(fill="x", pady=(px(8), px(10)))
            sev = tk.Frame(n, bg=C["lime_soft"])
            sev.pack(anchor="w")
            mech = s.severity == "mechanic"
            icon(sev, "wrench" if mech else "shield", 20, "danger" if mech else "ok", "lime_soft").pack(side="left")
            label(sev, SEVERITY_TEXT[lang].get(s.severity or "self", ""), "heading", "danger" if mech else "ok",
                  bg="lime_soft").pack(side="left", padx=(px(8), 0))
            notes = model_notes(kb, rec.model, s.fault, lang)
            if notes:
                label(n, t["for_model"].format(name=model_name(kb, rec.model)), "heading", bg="lime_soft").pack(
                    anchor="w", pady=(px(12), px(2)))
                for note in notes:
                    autowrap(label(n, "•  " + note, "body", bg="lime_soft")).pack(fill="x", pady=px(1))
            wc = RoundCard(right)
            wc.pack(fill="x", pady=(px(14), 0))
            w = wc.body
            label(w, t["wang"], "h2").pack(anchor="w")
            autowrap(label(w, t["wang_sub"], "body", "muted")).pack(fill="x", pady=(px(2), 0))
            state = self.dx.get("wang")
            if state is None:
                chip(w, t["wang_not_run"], C["warn"], C["warn_soft"]).pack(anchor="w", pady=(px(8), px(10)))
            else:
                autowrap(label(w, t["wang_yes"] if state else t["wang_no"], "heading", "ok" if state else "danger")
                         ).pack(fill="x", pady=(px(8), px(10)))
            PillButton(w, t["verify"], lambda: self.verify(rec, s.fault), style="outline", bg="surface").pack(
                anchor="w")
            if s.alternatives:
                ac = RoundCard(right)
                ac.pack(fill="x", pady=(px(14), 0))
                label(ac.body, t["alt"], "h2").pack(anchor="w", pady=(0, px(6)))
                for name, cf in s.alternatives:
                    row = tk.Frame(ac.body, bg=C["surface"])
                    row.pack(fill="x", pady=px(3))
                    autowrap(label(row, name, "body")).pack(side="left", fill="x", expand=True)
                    label(row, f"CF {cf:.2f}", "mono", "muted").pack(side="right", padx=(px(6), 0))
                    label(row, f"{cf:.0%}", "heading", "accent").pack(side="right")
        f = self.footer(page)
        icon(f, "shield", 18, "muted", "bg").pack(side="left")
        label(f, t["disclaimer"], "body", "muted", bg="bg").pack(side="left", padx=(px(8), 0))
        PillButton(f, t["new"], self.new_diagnosis).pack(side="right")

    def render_near(self, c, s: Summary) -> None:
        t, kb, lang = self.t, self.app.kb, self.app.lang
        label(c, t["derived"], "h2").pack(anchor="w")
        if not s.near:
            autowrap(label(c, t["nothing_derived"], "lead", "muted")).pack(fill="x", pady=(px(8), 0))
            return
        for m in s.near:
            row = tk.Frame(c, bg=C["surface"])
            row.pack(fill="x", pady=(px(8), 0))
            chip(row, m.rule, C["accent"], C["chrome"]).pack(side="left", padx=(0, px(10)))
            autowrap(label(row, short(kb, m.symbol, lang), "lead")).pack(side="left", fill="x", expand=True)
            label(row, f"{m.cf:.2f}", "mono", "muted").pack(side="right")
        missing = list(dict.fromkeys(sym for m in s.near for _, sym in m.missing))
        if missing:
            label(c, t["check_more"], "body", "muted").pack(anchor="w", pady=(px(14), px(4)))
            for sym in missing:
                autowrap(label(c, "• " + short(kb, sym, lang), "body")).pack(fill="x", pady=px(1))

    def verify(self, rec: Record, fault: str) -> None:
        self.dx["wang"] = wang_check(self.app.kb, rec, fault)
        self.render()

    def new_diagnosis(self) -> None:
        keep = {k: self.dx.get(k, "") for k in ("kind", "fuel", "model", "method")}
        self.app.state["dx"] = self.dx = dict(new_dx(), **keep)
        self.refresh_topbar()
        self.render()

    def on_key(self, event) -> None:
        if self.dx["step"] == 2 and self.dx["method"] == "guided" and not needs_part(self.dx):
            value = {"c": True, "y": True, "k": False, "n": False, "b": UNKNOWN, "u": UNKNOWN}.get(
                event.keysym.lower(), "none")
            if value != "none":
                self.answer_guided(value)
