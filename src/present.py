"""Turning engine results into text the rider understands (owner: Lâm).

Used by both cli.py and gui.py, so the two show exactly the same thing.
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


# ---------------------------------------------------------------------------
# "Why" explanation as rows (GUI); the console uses backward_chaining.explain_why
# ---------------------------------------------------------------------------

@dataclass
class WhyRow:
    rule: str
    goal: str
    premises: List[str]
    conclusion: str


def why_rows(kb: KnowledgeBase, chain, lang: str = "vi") -> List[WhyRow]:
    """Rules being tried while a question is asked, innermost first."""
    return [WhyRow(step.rule.id, short(kb, step.goal, lang),
                   [short(kb, p, lang) for p in step.rule.premises],
                   short(kb, step.rule.conclusion, lang))
            for step in reversed(list(chain))]


# ---------------------------------------------------------------------------
# Step-by-step backward chaining for a GUI (no blocking input())
# ---------------------------------------------------------------------------

class NeedAnswer(Exception):
    """Raised inside ask() when the engine reaches a symptom with no answer yet."""

    def __init__(self, symptom: str, chain) -> None:
        super().__init__(symptom)
        self.symptom = symptom
        self.chain = list(chain)


@dataclass
class BackwardStep:
    question: str = ""          # symptom to ask next ("" when finished)
    chain: list = None          # WhyStep list for the "why" explanation
    result: object = None       # BackwardResult when finished
    rules_tried: int = 0


def backward_step(kb: KnowledgeBase, answers: dict, goals=None, threshold: float = 0.2) -> BackwardStep:
    """Run backward chaining again from the start with the answers given so far.

    The search is deterministic, so replaying the same answers reaches the same
    point; the first symptom with no answer is returned as the next question.
    Undo is simply: remove the last answer and call this again.
    """
    from backward_chaining import BackwardChainer

    def ask(symptom, chain):
        if symptom in answers:
            return answers[symptom]
        raise NeedAnswer(symptom, chain)

    chainer = BackwardChainer(kb, ask)
    try:
        result = chainer.diagnose(goals=goals, threshold=threshold)
    except NeedAnswer as need:
        return BackwardStep(need.symptom, need.chain, None, chainer.rules_tried)
    return BackwardStep("", [], result, result.rules_tried)


# ---------------------------------------------------------------------------
# Inference graph of one fault (drawn by the GUI)
# ---------------------------------------------------------------------------

@dataclass
class GraphNode:
    symbol: str
    kind: str     # symptom / intermediate / fault
    column: int   # 0 = symptoms, last = the fault
    row: int
    cf: float


@dataclass
class GraphEdge:
    source: str
    target: str
    rule: str


def inference_graph(kb: KnowledgeBase, wm: WorkingMemory, fault: str):
    """Nodes and edges of the derivation of `fault`, laid out in columns."""
    facts = dict(wm.explain(fault))
    if fault not in facts:
        return [], []
    depth = {}

    def d(symbol):
        if symbol not in depth:
            f = facts[symbol]
            depth[symbol] = 0 if f.by == "user" else 1 + max(d(p) for p in f.premises)
        return depth[symbol]

    for s in facts:
        d(s)
    edges = []
    for s, f in facts.items():
        if f.by == "user":
            continue
        rules = f.by.split(",")
        for p in f.premises:
            # the rule (of possibly several) that uses p
            rid = next((r for r in rules if p in kb.rule(r).premises), rules[0])
            edges.append(GraphEdge(p, s, rid))
    columns = {}
    for s in sorted(facts, key=lambda s: (depth[s], s)):
        columns.setdefault(depth[s], []).append(s)
    nodes = [GraphNode(s, kb.symbols[s].kind, c, i, facts[s].cf)
             for c, syms in columns.items() for i, s in enumerate(syms)]
    return nodes, edges


# ---------------------------------------------------------------------------
# Wang trace, shortened: each rule formula is replaced by its id
# ---------------------------------------------------------------------------

def short_trace(kb: KnowledgeBase, lines: List[str]) -> List[str]:
    from wang import rule_formula

    names = sorted(((str(rule_formula(r)), r.id) for r in kb.rules), key=lambda x: -len(x[0]))
    out = []
    for line in lines:
        for formula, rid in names:
            if formula in line:
                line = line.replace(formula, rid)
        out.append(line)
    return out
