"""Adaptive interview: ask the question that tells the most (owner: Lâm).

Backward chaining asks questions in rule order. This module asks, at every
step, the question with the highest expected information gain, so a rider
answers fewer questions.

Hypotheses. Every fault is unfolded through the rules into its derivations: the
sets of symptoms that together prove it (for example weak_battery <-
{starter_clicks_or_silent, horn_weak, battery_older_than_2_years}). Each
derivation h has a weight w(h), the CF the chain of rules would give, and the
interview keeps a probability for each one:

    P(h | answers) ∝ w(h) · Π P(answer_s | h)
    P(yes_s | h) = 1 - MISS   if s is in h   (a rider can miss a symptom)
                 = NOISE      otherwise      (or report one that is unrelated)

A "none of these faults" hypothesis with weight OTHER keeps the model honest
when nothing fits. The probability of a fault is the sum over its derivations.

Question choice. For every unanswered symptom s that some hypothesis uses,
    IG(s) = H(F) - [P(yes) H(F | yes) + P(no) H(F | no)]
where H(F) is the entropy of the fault distribution. The symptom with the
largest IG is asked. The interview stops when one fault reaches STOP_AT, when
no question gains more than MIN_GAIN bits, or after MAX_QUESTIONS.

The final ranking uses the team's forward chaining on the "yes" answers, so
CFs, explanations and the Wang check stay exactly as in the other screens.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import product
from typing import Dict, FrozenSet, List, Optional, Tuple

from forward_chaining import ForwardResult, forward_chain
from kb import KnowledgeBase

MISS = 0.05
NOISE = 0.1
NEUTRAL = {"is_scooter", "is_manual", "is_fuel_injected", "is_carburetor", "has_clutch_lever"}  # facts about
# the motorbike, not symptoms: they say nothing against a fault whose rules do not mention them
OTHER = "__other__"
OTHER_WEIGHT = 0.05
STOP_AT = 0.85
PROVED_STOP_AT = 0.7
MIN_GAIN = 0.02
MAX_QUESTIONS = 15
MAX_DERIVATIONS = 64  # per symbol; the knowledge base is small, this is never reached today

# Answers that exclude each other: a "yes" to one is a "no" to the others.
EXCLUSIVE = [
    {"horn_weak", "horn_normal", "horn_silent"},
    {"fuel_gauge_empty", "fuel_level_ok"},
    {"is_scooter", "is_manual"},
    {"is_fuel_injected", "is_carburetor"},
    {"brake_held_when_starting", "starting_without_brake"},
    {"battery_older_than_2_years", "battery_recently_replaced"},
    {"starter_clicks_or_silent", "engine_cranks"},
]


@dataclass(frozen=True)
class Hypothesis:
    fault: str
    symptoms: FrozenSet[str]
    weight: float


def derivations(kb: KnowledgeBase, symbol: str, memo: Optional[dict] = None) -> List[Tuple[FrozenSet[str], float]]:
    """Every set of symptoms that proves `symbol`, with the CF of that chain of rules."""
    memo = {} if memo is None else memo
    if symbol in memo:
        return memo[symbol]
    if kb.is_askable(symbol):
        memo[symbol] = [(frozenset([symbol]), 1.0)]
        return memo[symbol]
    memo[symbol] = []  # guards against cycles (validate() reports them)
    best: Dict[FrozenSet[str], float] = {}
    for rule in kb.rules_concluding(symbol):
        options = [derivations(kb, p, memo) for p in rule.premises]
        for combo in product(*options):
            syms = frozenset().union(*(c[0] for c in combo))
            w = rule.cf * min(c[1] for c in combo)
            if w > best.get(syms, 0):
                best[syms] = w
    memo[symbol] = sorted(best.items(), key=lambda kv: -kv[1])[:MAX_DERIVATIONS]
    return memo[symbol]


def hypotheses(kb: KnowledgeBase) -> List[Hypothesis]:
    memo: dict = {}
    hs = [Hypothesis(f, syms, w) for f in sorted(kb.faults) for syms, w in derivations(kb, f, memo)]
    return hs + [Hypothesis(OTHER, frozenset(), OTHER_WEIGHT)]


def _entropy(probs) -> float:
    return -sum(p * math.log2(p) for p in probs if p > 0)


def _p_yes(h: Hypothesis, s: str) -> float:
    if s in h.symptoms:
        return 1 - MISS
    return 0.5 if s in NEUTRAL or s.startswith("model_") else NOISE


@dataclass
class Question:
    symptom: str
    gain: float                    # expected information gain in bits
    p_yes: float                   # how likely the answer is "yes"
    splits: List[Tuple[str, float]] = field(default_factory=list)  # top faults that use this symptom


class Interview:
    """One conversation. Feed answers, ask next_question() until it returns None."""

    def __init__(self, kb: KnowledgeBase, answers: Optional[Dict[str, bool]] = None):
        self.kb = kb
        self.models = set(kb.models)  # bike models: given in step 1 or the text, never asked, one at most
        self.hyps = hypotheses(kb)
        self.answers: Dict[str, bool] = {}
        self.skipped: set = set()
        self.asked: List[str] = []
        for s, v in (answers or {}).items():
            self._set(s, v)
        for m in self.models:  # no model given (step 1 or the text): not one of the listed models
            self.answers.setdefault(m, False)

    # --- answers ---------------------------------------------------------------
    def _set(self, symptom: str, value: bool) -> None:
        self.answers[symptom] = value
        if value and symptom in self.models:
            for other in self.models - {symptom}:
                self.answers.setdefault(other, False)
        if value:
            for group in EXCLUSIVE:
                if symptom in group:
                    for other in group - {symptom}:
                        self.answers.setdefault(other, False)

    def answer(self, symptom: str, value: Optional[bool]) -> None:
        """value None = "I don't know": the question is not asked again."""
        self.asked.append(symptom)
        if value is None:
            self.skipped.add(symptom)
        else:
            self._set(symptom, value)

    # --- beliefs ---------------------------------------------------------------
    def _posterior(self, extra: Optional[Tuple[str, bool]] = None) -> List[float]:
        answers = dict(self.answers)
        if extra:
            answers[extra[0]] = extra[1]
        ws = []
        for h in self.hyps:
            w = h.weight
            for s, v in answers.items():
                p = _p_yes(h, s)
                w *= p if v else 1 - p
            ws.append(w)
        total = sum(ws) or 1.0
        return [w / total for w in ws]

    def _faults(self, post: List[float]) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for h, p in zip(self.hyps, post):
            out[h.fault] = out.get(h.fault, 0.0) + p
        return out

    def beliefs(self, n: int = 5) -> List[Tuple[str, float]]:
        """Most likely faults now, best first (the "none of these" hypothesis is left out)."""
        fs = self._faults(self._posterior())
        ranked = sorted(((f, p) for f, p in fs.items() if f != OTHER), key=lambda kv: -kv[1])
        return ranked[:n]

    # --- choosing the next question -------------------------------------------
    def next_question(self) -> Optional[Question]:
        if len(self.asked) >= MAX_QUESTIONS:
            return None
        post = self._posterior()
        fs = self._faults(post)
        top_fault, top = max(((f, p) for f, p in fs.items() if f != OTHER), key=lambda kv: kv[1])
        proved = {d.fault for d in self.result().diagnoses}
        if top_fault in proved and top >= PROVED_STOP_AT:
            return None  # the most likely fault is already proved by the rules: stop asking
        if top >= STOP_AT:
            # confident but not proved yet: only ask what the best derivation still needs
            h_best = max((hp for hp in zip(self.hyps, post) if hp[0].fault == top_fault), key=lambda hp: hp[1])[0]
            candidates = set(h_best.symptoms)
        else:
            candidates = {s for h, p in zip(self.hyps, post) if p > 1e-4 for s in h.symptoms}
        candidates -= set(self.answers) | self.skipped | self.models
        h_now = _entropy(fs.values())
        best: Optional[Question] = None
        for s in sorted(candidates):
            p_yes = sum(p * _p_yes(h, s) for h, p in zip(self.hyps, post))
            h_yes = _entropy(self._faults(self._posterior((s, True))).values())
            h_no = _entropy(self._faults(self._posterior((s, False))).values())
            gain = h_now - (p_yes * h_yes + (1 - p_yes) * h_no)
            if best is None or gain > best.gain + 1e-12:
                best = Question(s, gain, p_yes)
        if best is None or (best.gain < MIN_GAIN and top < STOP_AT):
            return None
        users = {}
        for h, p in zip(self.hyps, post):
            if best.symptom in h.symptoms:
                users[h.fault] = users.get(h.fault, 0) + p
        best.splits = sorted(users.items(), key=lambda kv: -kv[1])[:3]
        return best

    # --- result ----------------------------------------------------------------
    def result(self) -> ForwardResult:
        """Forward chaining on the "yes" answers (the same engine as the By symptoms screen)."""
        return forward_chain(self.kb, [s for s, v in self.answers.items() if v])


def simulate(kb: KnowledgeBase, truth, start: Optional[Dict[str, bool]] = None) -> Tuple[Interview, int]:
    """Run an interview where every answer comes from `truth` (the symptoms that are true).

    Returns the finished interview and the number of questions asked.
    """
    truth = set(truth)
    iv = Interview(kb, start)
    while True:
        q = iv.next_question()
        if q is None:
            return iv, len(iv.asked)
        iv.answer(q.symptom, q.symptom in truth)
