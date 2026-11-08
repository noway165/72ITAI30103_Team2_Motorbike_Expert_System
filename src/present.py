"""Turning engine results into text the rider understands (owner: Lâm).

Used by cli.py; GUI screens can use the same functions so both show the same thing.
Nothing here prints or draws; it only returns plain data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from kb import KnowledgeBase, WorkingMemory

TEXT = {
    "vi": {
        "you_chose": "bạn chọn",
        "results": "Kết quả chẩn đoán",
        "rules_fired": "{n} luật đã chạy",
        "confidence": "Độ tin cậy",
        "action": "Cách xử lý",
        "why_result": "Vì sao ra kết quả này?",
        "no_fault": "Chưa đủ dữ kiện để kết luận lỗi nào (CF ≥ {t:.2f})",
        "derived": "Chương trình đã suy ra được:",
        "check_more": "Kiểm tra thêm để kết luận chắc hơn:",
        "nothing_derived": "Các triệu chứng đã chọn chưa khớp luật nào. Hãy chọn thêm triệu chứng "
                           "hoặc chuyển sang chế độ hỏi đáp.",
        "questions": "Đã hỏi {q} câu, đã thử {r} luật",
    },
    "en": {
        "you_chose": "you said",
        "results": "Diagnosis",
        "rules_fired": "{n} rules fired",
        "confidence": "Confidence",
        "action": "What to do",
        "why_result": "How was this found?",
        "no_fault": "Not enough evidence for any fault (CF ≥ {t:.2f})",
        "derived": "What the program could work out:",
        "check_more": "Check these to be more certain:",
        "nothing_derived": "The symptoms you chose do not match any rule. Add more symptoms "
                           "or switch to step-by-step questions.",
        "questions": "{q} questions asked, {r} rules tried",
    },
}


def t(key: str, lang: str = "vi", **kwargs) -> str:
    return TEXT.get(lang, TEXT["vi"])[key].format(**kwargs)


def short(kb: KnowledgeBase, symbol: str, lang: str = "vi") -> str:
    """Display text of a symbol without the trailing question mark."""
    return kb.text(symbol, lang).rstrip(" ?")


@dataclass
class HowRow:
    label: str      # "bạn chọn" or a rule id such as "SF01"
    text: str
    cf: float
    is_rule: bool


def how_rows(kb: KnowledgeBase, wm: WorkingMemory, symbol: str, lang: str = "vi") -> List[HowRow]:
    """The "how" explanation of `symbol`, premises first.

    Vehicle-type answers (is_scooter, ...) are left out to keep it short.
    """
    rows = []
    for name, fact in wm.explain(symbol):
        if fact.by == "user":
            if kb.symbols[name].subsystem == "vehicle":
                continue
            rows.append(HowRow(t("you_chose", lang), short(kb, name, lang), fact.cf, False))
        else:
            rows.append(HowRow(fact.by.replace(",", ", "), "→ " + short(kb, name, lang), fact.cf, True))
    return rows


@dataclass
class NearMiss:
    """An intermediate that was derived but did not lead to any fault."""

    symbol: str
    cf: float
    rule: str                      # rule that derived it
    missing: List[Tuple[str, str]]  # (rule id, symptom) still to check


def near_misses(kb: KnowledgeBase, wm: WorkingMemory) -> List[NearMiss]:
    """Intermediates in working memory, with the symptoms that would carry them to a fault.

    Shown when no fault reaches the threshold, instead of only "no fault found".
    """
    out = []
    for symbol in wm.true_facts():
        if symbol not in kb.intermediates:
            continue
        fact = wm.get(symbol)
        missing: List[Tuple[str, str]] = []
        for rule in kb.rules_using(symbol):
            for p in rule.premises:
                if p != symbol and kb.is_askable(p) and not wm.is_true(p) \
                        and kb.symbols[p].subsystem != "vehicle" \
                        and all(m[1] != p for m in missing):
                    missing.append((rule.id, p))
        out.append(NearMiss(symbol, fact.cf, fact.by, missing))
    out.sort(key=lambda n: -n.cf)
    return out


def cf_bar(cf: float, width: int = 20) -> str:
    """Text bar for the console, e.g. [##############      ]."""
    filled = round(max(0.0, min(1.0, cf)) * width)
    return "[" + "#" * filled + " " * (width - filled) + "]"
