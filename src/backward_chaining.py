"""Backward chaining with certainty factors and why / how explanations (owner: Khoa).

Goal-driven inference: the engine starts from a hypothesis (a fault), finds the
rules that conclude it, and turns each premise into a sub-goal. A symptom that
nobody has answered yet is asked to the rider (yes / no); the answer is kept in
working memory, so the same question is never asked twice.

Certainty factors follow exactly the same rules as forward_chaining.py, so both
engines give the same diagnosis for the same symptoms:
    - a symptom answered "yes" has CF 1.0 (or the CF the rider gives)
    - premises of a rule are joined by AND:   CF(premises) = min(CF of each premise)
    - a rule passes it on to its conclusion:  CF = rule.cf * CF(premises)
    - several rules with the same conclusion: CF = CF1 + CF2 * (1 - CF1), and so on
    - a fault is reported when its CF is at least `threshold` (default 0.2)

To get the same CF as forward chaining, every rule that concludes a goal is
tried (not only the first one that succeeds). A rule is abandoned as soon as one
of its premises is false, so questions that cannot change the result are not asked.

Explanations:
    why - while a question is shown, the chain of rules being tried (WhyStep list)
    how - after the diagnosis, the facts and rules that led to a fault (result.how)

Run from the repository root:
    python src/backward_chaining.py                       # ask the rider questions
    python src/backward_chaining.py --subsystem brakes    # only brake faults
    python src/backward_chaining.py --goal worn_brake_pads
    python src/backward_chaining.py --symptoms brake_squeal brake_pad_thin_visible
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Union

from forward_chaining import DEFAULT_THRESHOLD, Diagnosis, combine_cf
from kb import KnowledgeBase, Rule, WorkingMemory, load_kb


@dataclass(frozen=True)
class WhyStep:
    """One level of the proof in progress: `rule` is being tried to prove `goal`."""

    goal: str
    rule: Rule


# An answer is True / False, or a CF in (0, 1] for "yes, with this much certainty".
Answer = Union[bool, float]
# ask(symptom, chain): `chain` lists the rules being tried, outermost first.
AskFn = Callable[[str, List[WhyStep]], Answer]


def _normalise(answer: Answer):
    """Turn an answer into (value, cf)."""
    if isinstance(answer, bool):
        return answer, 1.0
    if isinstance(answer, (int, float)):
        if answer == 0:
            return False, 1.0
        if 0 < answer <= 1:
            return True, float(answer)
    raise ValueError(f"answer must be True, False or a CF in (0, 1], got {answer!r}")


@dataclass
class BackwardResult:
    wm: WorkingMemory
    diagnoses: List[Diagnosis] = field(default_factory=list)  # ranked, best first
    questions_asked: int = 0
    rules_tried: int = 0
    fired: List[Rule] = field(default_factory=list)  # rules whose premises all held

    @property
    def rules_fired(self) -> int:
        return len(self.fired)

    def top(self, n: int = 3) -> List[Diagnosis]:
        return self.diagnoses[:n]

    def how(self, symbol: str) -> List[str]:
        """Lines explaining how `symbol` was derived, premises first."""
        lines = []
        for name, fact in self.wm.explain(symbol):
            if fact.by == "user":
                lines.append(f"{name}: given by the rider (CF {fact.cf:.2f})")
            else:
                lines.append(f"{name}: rule {fact.by} from {', '.join(fact.premises)} (CF {fact.cf:.2f})")
        return lines


class BackwardChainer:
    """One diagnosis session. Create a new object for each rider."""

    def __init__(self, kb: KnowledgeBase, ask: AskFn, wm: Optional[WorkingMemory] = None) -> None:
        self.kb = kb
        self.ask = ask
        self.wm = wm if wm is not None else WorkingMemory()
        self.cf: Dict[str, float] = {}          # derived symbols already settled (0.0 = not proven)
        self.used_rules: Dict[str, List[str]] = {}  # derived symbol -> ids of the rules that held
        self.fired: List[Rule] = []
        self.questions_asked = 0
        self.rules_tried = 0
        self._chain: List[WhyStep] = []

    # --- the proof ---------------------------------------------------------

    def prove(self, symbol: str) -> float:
        """Return the CF of `symbol`: 0.0 if it cannot be proven, otherwise in (0, 1]."""
        if self.kb.is_askable(symbol):
            return self._symptom_cf(symbol)
        if symbol in self.cf:
            return self.cf[symbol]
        if any(step.goal == symbol for step in self._chain):
            return 0.0  # circular rules; kb.validate() reports them as errors

        contributions: List[float] = []
        used: List[Rule] = []
        premises: List[str] = []
        for rule in self.kb.rules_concluding(symbol):
            self.rules_tried += 1
            self._chain.append(WhyStep(symbol, rule))
            premise_cfs: List[float] = []
            for p in rule.premises:
                c = self.prove(p)
                if c <= 0:
                    break  # one false premise is enough: skip the remaining questions
                premise_cfs.append(c)
            self._chain.pop()
            if len(premise_cfs) == len(rule.premises):
                contributions.append(rule.cf * min(premise_cfs))
                used.append(rule)
                self.fired.append(rule)
                premises += [p for p in rule.premises if p not in premises]

        result = combine_cf(contributions)
        self.cf[symbol] = result
        if used:
            self.used_rules[symbol] = [r.id for r in used]
            self.wm.tell(symbol, True, cf=round(result, 4),
                         by=",".join(r.id for r in used), premises=premises)
        return result

    def _symptom_cf(self, symptom: str) -> float:
        fact = self.wm.get(symptom)
        if fact is None:  # not asked yet
            answer = self.ask(symptom, list(self._chain))
            value, cf = _normalise(answer)
            self.questions_asked += 1
            self.wm.tell(symptom, value, cf=cf)
            fact = self.wm.get(symptom)
        return fact.cf if fact.value else 0.0

    # --- diagnosis ---------------------------------------------------------

    def diagnose(self, goals: Optional[Iterable[str]] = None,
                 threshold: float = DEFAULT_THRESHOLD) -> BackwardResult:
        """Try to prove each goal fault (default: every fault) and rank the results."""
        fault_ids = sorted(self.kb.faults) if goals is None else list(goals)
        for g in fault_ids:
            if not self.kb.is_fault(g):
                raise ValueError(f"unknown fault {g!r}")

        diagnoses: List[Diagnosis] = []
        for g in fault_ids:
            c = self.prove(g)
            if c >= threshold:
                diagnoses.append(Diagnosis(
                    fault=g, cf=round(c, 4), rules=list(self.used_rules.get(g, [])),
                    severity=self.kb.symbols[g].severity))
        diagnoses.sort(key=lambda d: (-d.cf, d.fault))
        return BackwardResult(wm=self.wm, diagnoses=diagnoses,
                              questions_asked=self.questions_asked,
                              rules_tried=self.rules_tried, fired=list(self.fired))


def backward_chain(kb: KnowledgeBase, symptoms: Union[Iterable[str], Dict[str, Answer]],
                   goals: Optional[Iterable[str]] = None,
                   threshold: float = DEFAULT_THRESHOLD) -> BackwardResult:
    """Run backward chaining with the answers already known (no interaction).

    `symptoms` is a list of symptoms that are true, or a dict {symptom: True / False / CF}.
    Every symptom that is not mentioned is answered "no" when the engine asks.
    """
    answers = dict(symptoms) if isinstance(symptoms, dict) else {s: True for s in symptoms}
    for s in answers:
        if not kb.is_askable(s):
            raise ValueError(f"{s!r} is not a symptom; only symptoms can be given")

    def ask(symptom: str, chain: List[WhyStep]) -> Answer:
        return answers.get(symptom, False)

    return BackwardChainer(kb, ask).diagnose(goals=goals, threshold=threshold)


# ---------------------------------------------------------------------------
# "Why" explanation
# ---------------------------------------------------------------------------

_WHY_TEXT = {
    "vi": {
        "direct": "Mình hỏi câu này vì bạn muốn kiểm tra trực tiếp triệu chứng này.",
        "head": "Mình hỏi câu này vì đang thử các luật sau (luật trong cùng nằm đầu tiên):",
        "rule": "Luật {id} (để chứng minh: {goal}): NẾU {premises} THÌ {conclusion}",
        "and": " VÀ ",
    },
    "en": {
        "direct": "I am asking this because you chose to check this symptom directly.",
        "head": "I am asking because I am trying these rules (innermost first):",
        "rule": "Rule {id} (to prove: {goal}): IF {premises} THEN {conclusion}",
        "and": " AND ",
    },
}


def explain_why(kb: KnowledgeBase, chain: Sequence[WhyStep], lang: str = "vi") -> List[str]:
    """Lines telling the rider why the current question is asked."""
    t = _WHY_TEXT.get(lang, _WHY_TEXT["vi"])
    if not chain:
        return [t["direct"]]
    lines = [t["head"]]
    for step in reversed(chain):
        rule = step.rule
        lines.append("  - " + t["rule"].format(
            id=rule.id,
            goal=kb.text(step.goal, lang),
            premises=t["and"].join(kb.text(p, lang) for p in rule.premises),
            conclusion=kb.text(rule.conclusion, lang)))
    return lines


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

_YES = {"y", "yes", "c", "co", "có", "1"}
_NO = {"n", "no", "k", "khong", "không", "0"}
_WHY = {"why", "?", "w", "tai sao", "tại sao"}


def make_console_asker(kb: KnowledgeBase, lang: str = "vi") -> AskFn:
    """Ask the rider on the console: c / k (yes / no) or `why`."""
    prompt = "[c = có, k = không, why = tại sao hỏi]" if lang == "vi" else "[y = yes, n = no, why]"

    def ask(symptom: str, chain: List[WhyStep]) -> Answer:
        print(f"\n? {kb.question(symptom, lang)}")
        hint = kb.symbols[symptom].hint.get(lang)
        if hint:
            print(f"  ({hint})")
        while True:
            raw = input(f"  {prompt} ").strip().lower()
            if raw in _YES:
                return True
            if raw in _NO:
                return False
            if raw in _WHY:
                for line in explain_why(kb, chain, lang):
                    print(f"  {line}")
                continue
            print("  Vui lòng trả lời c, k hoặc why." if lang == "vi" else "  Please answer y, n or why.")

    return ask


def _print_result(kb: KnowledgeBase, result: BackwardResult, lang: str) -> None:
    print(f"\nQuestions asked: {result.questions_asked}, rules tried: {result.rules_tried}, "
          f"rules fired: {result.rules_fired}")
    if not result.diagnoses:
        print("No fault reached the threshold.")
        return
    for i, d in enumerate(result.diagnoses, 1):
        print(f"\n{i}. {kb.text(d.fault, lang)}  [CF {d.cf:.2f}, {d.severity}]")
        print(f"   {kb.action(d.fault, lang)}")
        for line in result.how(d.fault):
            print(f"   - {line}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnose faults by backward chaining.")
    parser.add_argument("--goal", action="append", default=[],
                        help="fault to prove (repeat the option for several); default: all faults")
    parser.add_argument("--subsystem", help="only prove the faults of this subsystem, e.g. brakes")
    parser.add_argument("--symptoms", nargs="*", default=None,
                        help="answer without asking: these symptoms are true, all others false")
    parser.add_argument("--lang", choices=("vi", "en"), default="vi")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--list-faults", action="store_true", help="list every fault that can be proven")
    args = parser.parse_args(argv)

    try:  # Vietnamese text on older Windows consoles
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    kb = load_kb()
    if args.list_faults:
        for fid, fault in sorted(kb.faults.items(), key=lambda kv: (kv[1].subsystem, kv[0])):
            print(f"[{fault.subsystem}] {fid:32} {kb.text(fid, args.lang)}")
        return 0

    goals = list(args.goal) or None
    if args.subsystem:
        goals = [f for f, sym in sorted(kb.faults.items()) if sym.subsystem == args.subsystem]
        if not goals:
            print(f"Error: no faults in subsystem {args.subsystem!r}")
            return 1

    try:
        if args.symptoms is not None:
            result = backward_chain(kb, args.symptoms, goals=goals, threshold=args.threshold)
        else:
            chainer = BackwardChainer(kb, make_console_asker(kb, args.lang))
            result = chainer.diagnose(goals=goals, threshold=args.threshold)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nStopped.")
        return 1

    _print_result(kb, result, args.lang)
    return 0


if __name__ == "__main__":
    sys.exit(main())
