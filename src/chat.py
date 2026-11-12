"""Rule-based conversation for "Describe it in words" (owner: Lâm).

The rider types freely; every reply is built from the knowledge base, not from
canned answers:

    question      kb.question() and its hint, plus the faults it separates (interview.py)
    "why?"        the rules that use the symptom being asked, each premise marked
                  ✓ known yes, ✗ known no, ? being asked, · not known yet
    "how?"        the rule chain of the leading fault (forward chaining's how)
    "what to do"  the fault's action and severity, with the rules that proved it
    "others?"     the most likely faults now and whether a rule has proved them
    "X là gì?"    the fault / fact / symptom X and the rules that conclude or use it
    an answer     what changed: rules that can now fire, rules that no longer can
    more symptoms read by nlu.extract and added to the description

Only the connecting words (IF / AND / THEN, "you said", ...) are fixed text.
The state lives in the diagnosis dict (dx["text"], dx["replies"], dx["chat"]),
so a rebuilt window shows the same conversation.

    start(kb, dx, "đề chỉ nghe tạch tạch", "vi")   # first description
    respond(kb, dx, "tại sao hỏi vậy?", "vi")      # every later message
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

from kb import KnowledgeBase
from nlu import extract, fold
from present import how_rows, near_misses, short
from theme import SEVERITY_TEXT
from wang import entails

TEXT = {
    "vi": {
        "IF": "NẾU", "AND": "VÀ", "THEN": "THÌ",
        "read": "Mình đọc được từ câu bạn kể:", "read_none": "Mình chưa nhận ra triệu chứng nào trong câu này.",
        "yes": "có", "no": "không", "unknown": "không rõ",
        "noted": "Ghi nhận: {s}: {v}.", "added": "Đã hiểu thêm: {s}.",
        "fired": "Luật {rule} chạy được: ⇒ {c} (CF {cf:.2f}).",
        "blocked": "Luật {rules} không dùng được nữa.",
        "splits": "Câu này giúp phân biệt: {faults}.",
        "why": "Câu trả lời quyết định các luật sau:",
        "why_none": "Hiện không có câu hỏi nào đang chờ.",
        "how": "{fault} (độ tin cậy {cf:.0%}) được suy ra như sau:",
        "you_said": "Bạn nói: {s}",
        "rule_row": "Luật {rule} ⇒ {c} (CF {cf:.2f})",
        "near": "Chưa lỗi nào đủ độ tin cậy 20%. Đã suy ra: {c} (luật {rule}); còn cần biết: {missing}.",
        "nothing": "Chưa có luật nào chạy được với những gì bạn kể.",
        "fix": "Cách xử lý {fault}: {action} ({severity}).",
        "fix_maybe": "Nếu đúng là {fault} (chưa luật nào chứng minh): {action} ({severity}).",
        "proved_by": "Lỗi này được chứng minh bởi luật {rules}.",
        "others": "Các khả năng lúc này:",
        "other_row": "{fault}: {p:.0%}, {state}",
        "proved": "luật đã chứng minh (CF {cf:.2f})", "not_proved": "chưa đủ điều kiện luật nào",
        "what_fault": "{name} là một lỗi thuộc bộ phận {part} ({severity}). Cách xử lý: {action}",
        "what_fact": "{name} là kết luận trung gian.",
        "what_symptom": "{name} là một triệu chứng. Câu hỏi: {q}",
        "concluded_by": "Được kết luận bởi:", "used_by": "Được dùng trong:",
        "what_none": "Mình không tìm thấy điều này trong cơ sở tri thức.",
        "final": "Kết luận: {fault}, độ tin cậy {cf:.0%}, theo chuỗi luật {chain}.",
        "wang_yes": "Kiểm tra chéo bằng thuật toán Wang: chứng minh được từ luật và các câu trả lời \"có\".",
        "wang_no": "Kiểm tra chéo bằng thuật toán Wang: không chứng minh được.",
        "final_none": "Mình đã hỏi hết những câu đáng hỏi nhưng chưa lỗi nào đủ độ tin cậy 20%.",
        "not_understood": "Mình chưa hiểu câu này. Bạn có thể trả lời {answers}, kể thêm triệu chứng, "
                          "hoặc hỏi: {asks}.",
        "answer_words": "\"có\", \"không\" hoặc \"không rõ\"",
        "ask_words": "\"tại sao?\", \"làm sao biết?\", \"sửa thế nào?\", \"còn khả năng nào?\", \"... là gì?\"",
    },
    "en": {
        "IF": "IF", "AND": "AND", "THEN": "THEN",
        "read": "From your description I read:", "read_none": "I could not find any symptom in that.",
        "yes": "yes", "no": "no", "unknown": "not sure",
        "noted": "Noted: {s}: {v}.", "added": "Also understood: {s}.",
        "fired": "Rule {rule} can now fire: ⇒ {c} (CF {cf:.2f}).",
        "blocked": "Rule {rules} can no longer be used.",
        "splits": "This question separates: {faults}.",
        "why": "Your answer decides these rules:",
        "why_none": "There is no question waiting right now.",
        "how": "{fault} (confidence {cf:.0%}) was found like this:",
        "you_said": "You said: {s}",
        "rule_row": "Rule {rule} ⇒ {c} (CF {cf:.2f})",
        "near": "No fault reaches 20% confidence yet. Derived: {c} (rule {rule}); still to check: {missing}.",
        "nothing": "No rule can fire yet with what you told me.",
        "fix": "What to do about {fault}: {action} ({severity}).",
        "fix_maybe": "If it is {fault} (no rule has proved it yet): {action} ({severity}).",
        "proved_by": "This fault is proved by rule {rules}.",
        "others": "The possibilities now:",
        "other_row": "{fault}: {p:.0%}, {state}",
        "proved": "proved by the rules (CF {cf:.2f})", "not_proved": "no rule satisfied yet",
        "what_fault": "{name} is a fault of the {part} system ({severity}). What to do: {action}",
        "what_fact": "{name} is an intermediate conclusion.",
        "what_symptom": "{name} is a symptom. Question: {q}",
        "concluded_by": "Concluded by:", "used_by": "Used in:",
        "what_none": "I could not find that in the knowledge base.",
        "final": "Conclusion: {fault}, confidence {cf:.0%}, by the rule chain {chain}.",
        "wang_yes": "Cross-check with Wang's algorithm: proved from the rules and your \"yes\" answers.",
        "wang_no": "Cross-check with Wang's algorithm: not proved.",
        "final_none": "I have asked everything worth asking, but no fault reaches 20% confidence.",
        "not_understood": "I did not understand that. You can answer {answers}, describe more symptoms, "
                          "or ask: {asks}.",
        "answer_words": "\"yes\", \"no\" or \"not sure\"",
        "ask_words": "\"why?\", \"how do you know?\", \"how to fix?\", \"what else?\", \"what is ...?\"",
    },
}

# Words that make a whole answer; compared without accents, after dropping FILLER words.
ANSWERS: Dict[Optional[bool], set] = {
    None: {"khong ro", "khong biet", "chua biet", "ko biet", "k biet", "khong chac", "bo qua", "chiu",
           "not sure", "dont know", "don t know", "i don t know", "idk", "skip", "no idea", "maybe"},
    True: {"co", "u", "uh", "um", "vang", "da", "dung", "u dung", "chac vay", "chac la co", "phai", "co ban",
           "yes", "yeah", "yep", "y", "correct", "true", "right", "sure"},
    False: {"khong", "ko", "k", "khong co", "chua", "sai", "khong phai", "khong he",
            "no", "nope", "not really", "n", "false", "never"},
}
FILLER = {"a", "roi", "nha", "nhe", "day", "dau", "oi", "lam", "ma", "thi", "nhi", "ha", "ah", "oh", "well",
          "i", "think", "so"}

# What the rider asks for; checked in this order (the first match wins).
INTENTS: List[Tuple[str, List[str]]] = [
    ("restart", ["lam lai", "bat dau lai", "noi lai tu dau", "restart", "start over"]),
    ("result", ["xem ket qua", "ket qua", "ket luan di", "show result", "result", "conclusion"]),
    ("fix", ["sua the nao", "sua sao", "sua nhu the nao", "phai lam gi", "lam gi bay gio", "xu ly the nao",
             "xu ly sao", "xu ly nhu the nao", "khac phuc", "cach sua", "fix it", "how to fix", "how do i fix",
             "repair", "what should i do", "what to do", "what do i do"]),
    ("what", ["la gi", "nghia la gi", "what is", "what s a", "what does", "what are"]),
    ("how", ["lam sao biet", "sao biet", "dua vao dau", "can cu vao dau", "vi sao ket luan", "tai sao ket luan",
             "tai sao la", "vi sao la", "giai thich", "how do you know", "how did you", "explain"]),
    ("others", ["kha nang khac", "loi khac", "con loi nao", "con kha nang", "con gi nua", "nhung loi nao",
                "other faults", "what else", "alternatives", "other possibilities", "anything else"]),
    ("why", ["tai sao", "vi sao", "sao lai hoi", "sao hoi", "hoi de lam gi", "why"]),
]


WHAT_WORDS = {"la", "gi", "nghia", "cai", "what", "is", "a", "an", "the", "does", "mean", "s", "are"}


def _words(text: str) -> List[str]:
    return re.findall(r"[a-z0-9]+", fold(text).replace("'", " "))


def parse_answer(text: str) -> Tuple[bool, Optional[bool]]:
    """(is an answer, value) from the first clause: "có, mà đèn cũng tối" -> (True, True)."""
    first = re.split(r"[,.;:!?\n]", text, maxsplit=1)[0]
    key = " ".join(w for w in _words(first) if w not in FILLER)
    for value in (None, True, False):  # "không rõ" before "không"
        if key in ANSWERS[value]:
            return True, value
    return False, None


def intent(text: str) -> Optional[str]:
    """"why", "how", "fix", "others", "what", "restart", "result", or None (an answer or a description)."""
    padded = f" {' '.join(_words(text))} "
    for name, phrases in INTENTS:
        if any(f" {p} " in padded for p in phrases):
            return name
    return None


def _rest(text: str) -> str:
    """The text after the first clause (the part after an answer)."""
    parts = re.split(r"[,.;:!?\n]", text, maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""


def _interview(kb: KnowledgeBase, dx):
    from gui_diagnosis import talk_interview  # same Interview as the window; imported late (that module imports this one)
    return talk_interview(kb, dx)


# --- pieces built from the knowledge base ---------------------------------------------------------------
def _rule(kb: KnowledgeBase, rule, lang: str, iv=None, asking: str = "") -> str:
    t = TEXT[lang]
    wm = iv.result().wm if iv is not None else None
    parts = []
    for p in rule.premises:
        mark = ""
        if iv is not None:
            known = iv.answers.get(p, wm.is_true(p) or None)
            mark = "? " if p == asking else "✓ " if known else "✗ " if known is False else "· "
        parts.append(mark + short(kb, p, lang))
    return (f"{rule.id}: {t['IF']} " + f" {t['AND']} ".join(parts)
            + f" {t['THEN']} {short(kb, rule.conclusion, lang)} (CF {rule.cf:.2f})")


def _faults(kb: KnowledgeBase, pairs, lang: str) -> str:
    return ", ".join(f"{kb.text(f, lang)} ({p:.0%})" for f, p in pairs if p >= 0.005)


def ask(kb: KnowledgeBase, iv, q, lang: str) -> str:
    """The next question: its text and hint from the KB, and the faults it separates."""
    lines = [kb.question(q.symptom, lang)]
    hint = kb.symbols[q.symptom].hint.get(lang, "")
    if hint:
        lines.append(hint)
    if _faults(kb, q.splits, lang):
        lines.append(TEXT[lang]["splits"].format(faults=_faults(kb, q.splits, lang)))
    return "\n".join(lines)


def why(kb: KnowledgeBase, iv, q, lang: str) -> str:
    t = TEXT[lang]
    if q is None:
        return t["why_none"]
    rules = kb.rules_using(q.symptom)[:4]
    lines = [t["why"]] + ["• " + _rule(kb, r, lang, iv, q.symptom) for r in rules]
    if _faults(kb, q.splits, lang):
        lines.append(t["splits"].format(faults=_faults(kb, q.splits, lang)))
    return "\n".join(lines)


def how(kb: KnowledgeBase, iv, lang: str) -> str:
    t, res = TEXT[lang], iv.result()
    if res.diagnoses:
        top = res.diagnoses[0]
        lines = [t["how"].format(fault=kb.text(top.fault, lang), cf=top.cf)]
        for row in how_rows(kb, res.wm, top.fault, lang):
            lines.append("• " + (t["rule_row"].format(rule=row.label, c=row.text.lstrip("→ "), cf=row.cf)
                                 if row.is_rule else t["you_said"].format(s=row.text)))
        return "\n".join(lines)
    near = near_misses(kb, res.wm)
    if near:
        m = near[0]
        missing = "; ".join(short(kb, s, lang) for _, s in m.missing[:3]) or "—"
        return t["near"].format(c=short(kb, m.symbol, lang), rule=m.rule, missing=missing)
    return t["nothing"]


def fix(kb: KnowledgeBase, iv, lang: str) -> str:
    t, res = TEXT[lang], iv.result()
    if res.diagnoses:
        top = res.diagnoses[0].fault
        rules = ", ".join(dict.fromkeys(r for r in res.wm.get(top).by.split(",") if r))
        return "\n".join([t["fix"].format(fault=kb.text(top, lang), action=kb.action(top, lang),
                                          severity=SEVERITY_TEXT[lang][kb.symbols[top].severity or "self"]),
                          t["proved_by"].format(rules=rules)])
    top = iv.beliefs(1)[0][0]
    return t["fix_maybe"].format(fault=kb.text(top, lang), action=kb.action(top, lang),
                                 severity=SEVERITY_TEXT[lang][kb.symbols[top].severity or "self"])


def others(kb: KnowledgeBase, iv, lang: str) -> str:
    t = TEXT[lang]
    proved = {d.fault: d.cf for d in iv.result().diagnoses}
    lines = [t["others"]]
    for f, p in iv.beliefs(3):
        state = t["proved"].format(cf=proved[f]) if f in proved else t["not_proved"]
        lines.append("• " + t["other_row"].format(fault=kb.text(f, lang), p=p, state=state))
    return "\n".join(lines)


def what(kb: KnowledgeBase, text: str, iv, lang: str) -> str:
    """Find what `text` names (most of the asked words in its name; faults, then the shortest name, first)
    and explain it from the rules."""
    t = TEXT[lang]
    said = set(_words(text)) - WHAT_WORDS
    if not said:
        return t["what_none"]
    ranked = []
    for sym in list(kb.faults) + list(kb.intermediates) + list(kb.symptoms):
        words = set(_words(short(kb, sym, lang)))
        ranked.append((len(words & said) / len(said), kb.is_fault(sym), -len(words), sym))
    score, _, _, best = max(ranked)
    if score < 0.6:
        return t["what_none"]
    name = short(kb, best, lang)
    if kb.is_fault(best):
        from theme import SUBSYSTEM_NAMES
        head = t["what_fault"].format(name=name, part=SUBSYSTEM_NAMES[lang].get(kb.symbols[best].subsystem, ""),
                                      severity=SEVERITY_TEXT[lang][kb.symbols[best].severity or "self"],
                                      action=kb.action(best, lang))
    elif best in kb.intermediates:
        head = t["what_fact"].format(name=name)
    else:
        head = t["what_symptom"].format(name=name, q=kb.question(best, lang))
    lines = [head]
    for title, rules in ((t["concluded_by"], kb.rules_concluding(best)), (t["used_by"], kb.rules_using(best))):
        if rules:
            lines.append(title)
            lines += ["• " + _rule(kb, r, lang, iv) for r in rules[:4]]
    return "\n".join(lines)


def final(kb: KnowledgeBase, iv, lang: str) -> str:
    """The conclusion when nothing is worth asking: fault, CF, rule chain, Wang's check, what to do."""
    t, res = TEXT[lang], iv.result()
    if not res.diagnoses:
        return "\n".join([t["final_none"], how(kb, iv, lang)])
    top = res.diagnoses[0]
    chain = " → ".join(row.label for row in how_rows(kb, res.wm, top.fault, lang) if row.is_rule)
    proved = entails(kb, [s for s, v in iv.answers.items() if v], top.fault).valid
    return "\n".join([t["final"].format(fault=kb.text(top.fault, lang), cf=top.cf, chain=chain),
                      t["wang_yes"] if proved else t["wang_no"], fix(kb, iv, lang).split("\n")[0]])


def _next(kb: KnowledgeBase, iv, lang: str) -> List[str]:
    q = iv.next_question()
    return [ask(kb, iv, q, lang)] if q is not None else [final(kb, iv, lang)]


def _effect(kb: KnowledgeBase, before, iv, lang: str, noted: str, value, added) -> str:
    """What the new facts changed: rules that now fire, rules a "no" switched off."""
    t, after = TEXT[lang], iv.result()
    lines = []
    if noted:
        v = t["unknown"] if value is None else t["yes"] if value else t["no"]
        lines.append(t["noted"].format(s=short(kb, noted, lang), v=v))
    if added:
        lines.append(t["added"].format(s="; ".join(("" if m.value else t["no"] + " ") + short(kb, m.symptom, lang)
                                                   for m in added)))
    old = set(before.wm.true_facts())
    for name in after.wm.true_facts():
        fact = after.wm.get(name)
        if name not in old and fact.by != "user":
            lines.append(t["fired"].format(rule=fact.by.replace(",", ", "), c=short(kb, name, lang), cf=fact.cf))
    if noted and value is False:
        off = [r.id for r in kb.rules_using(noted)]
        if off:
            lines.append(t["blocked"].format(rules=", ".join(off)))
    return "\n".join(lines)


# --- conversation -----------------------------------------------------------------------------------------
def _log(dx, who: str, text: str) -> None:
    dx.setdefault("chat", []).append((who, text))


def start(kb: KnowledgeBase, dx, text: str, lang: str) -> List[str]:
    """First description: what was read, then the first question (or the conclusion)."""
    dx.update(text=text.strip(), replies=[], chat=[])
    _log(dx, "you", dx["text"])
    iv, found = _interview(kb, dx)
    t = TEXT[lang]
    read = [t["read"]] + ["• " + ("" if m.value else t["no"] + " ") + short(kb, m.symptom, lang) for m in found] \
        if found else [t["read_none"]]
    out = ["\n".join(read)] + (_next(kb, iv, lang) if found else [])
    for m in out:
        _log(dx, "bot", m)
    return out


def respond(kb: KnowledgeBase, dx, text: str, lang: str) -> List[str]:
    """Reply to one message; the conversation is kept in dx["chat"]."""
    text = text.strip()
    kind = intent(text)
    if kind == "restart":
        dx.update(text="", replies=[], chat=[])
        return []
    _log(dx, "you", text)
    out = _reply(kb, dx, text, kind, lang)
    for m in out:
        _log(dx, "bot", m)
    return out


def _reply(kb: KnowledgeBase, dx, text: str, kind: Optional[str], lang: str) -> List[str]:
    iv, _ = _interview(kb, dx)
    q = iv.next_question()
    if kind == "result":
        return [final(kb, iv, lang)]
    if kind in ("fix", "others", "what"):
        return [{"fix": lambda: fix(kb, iv, lang), "others": lambda: others(kb, iv, lang),
                 "what": lambda: what(kb, text, iv, lang)}[kind]()]
    if kind == "how" or (kind == "why" and q is None):
        return [how(kb, iv, lang)]
    if kind == "why":
        return [why(kb, iv, q, lang)]
    is_answer, value = parse_answer(text)
    noted = q.symptom if is_answer and q is not None else ""
    rest = _rest(text) if noted else text
    added = extract(rest, kb.symptoms) if rest else []
    if not noted and not added:
        t = TEXT[lang]
        return [t["not_understood"].format(answers=t["answer_words"], asks=t["ask_words"])]
    before = iv.result()
    if noted:
        dx["replies"].append((noted, value))
    if added:
        dx["text"] = f"{dx['text']}. {rest}".strip(". ")
    iv, _ = _interview(kb, dx)
    return [_effect(kb, before, iv, lang, noted, value, added)] + _next(kb, iv, lang)
