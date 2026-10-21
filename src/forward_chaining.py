"""Forward chaining with certainty factors (owner: Giang).

Data-driven inference: the rider gives the symptoms first, the engine fires
every rule whose premises are all true, adds the conclusions to working
memory, and repeats until nothing new can be derived. The faults that were
derived are then ranked by certainty factor (CF).

Certainty factors (MYCIN style, positive evidence only):
    - a symptom answered "yes" has CF 1.0 (or the CF the rider gives)
    - premises of a rule are joined by AND:   CF(premises) = min(CF of each premise)
    - a rule passes it on to its conclusion:  CF = rule.cf * CF(premises)
    - several rules with the same conclusion: CF = CF1 + CF2 * (1 - CF1), and so on
    - a fault is reported when its CF is at least `threshold` (default 0.2)

Firing follows PL-FC-ENTAILS? from AIMA (chapter 7): each rule keeps a count
of premises not yet known to be true, and an agenda holds the facts still to
be processed. CFs are computed after the firing is finished, in dependency
order, so that a conclusion reached by several rules is combined before it is
used as a premise by the next rule.

Run from the repository root:
    python src/forward_chaining.py starter_clicks_or_silent horn_weak battery_older_than_2_years
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Union

from kb import KnowledgeBase, Rule, WorkingMemory, load_kb

DEFAULT_THRESHOLD = 0.2

Facts = Union[WorkingMemory, Mapping[str, Union[bool, float]], Iterable[str]]


def combine_cf(cfs: Iterable[float]) -> float:
    """Combine positive certainty factors of several rules with the same conclusion."""
    total = 0.0
    for cf in cfs:
        total = total + cf * (1 - total)
    return total


@dataclass
class Diagnosis:
    fault: str
    cf: float
    rules: List[str]          # rules that concluded this fault
    severity: Optional[str]   # "self" or "mechanic"


@dataclass
class ForwardResult:
    wm: WorkingMemory
    fired: List[Rule] = field(default_factory=list)       # in firing order
    diagnoses: List[Diagnosis] = field(default_factory=list)  # ranked, best first

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


def _working_memory(kb: KnowledgeBase, facts: Facts) -> WorkingMemory:
    """Copy the rider's answers into a new working memory, checking the symbols."""
    if isinstance(facts, WorkingMemory):
        # only the rider's answers; facts derived by an earlier run are derived again
        items = [(s, facts.get(s).value, facts.get(s).cf) for s in kb.symptoms if s in facts]
    elif isinstance(facts, Mapping):
        items = []
        for s, v in facts.items():
            if isinstance(v, bool):
                items.append((s, v, 1.0))
            elif isinstance(v, (int, float)) and 0 < v <= 1:
                items.append((s, True, float(v)))
            else:
                raise ValueError(f"answer for {s!r} must be True, False or a CF in (0, 1]")
    else:
        items = [(s, True, 1.0) for s in facts]

    wm = WorkingMemory()
    for symbol, value, cf in items:
        if symbol not in kb.symbols:
            raise ValueError(f"unknown symbol {symbol!r}")
        if not kb.is_askable(symbol):
            raise ValueError(f"{symbol!r} is not a symptom; only symptoms can be given")
        wm.tell(symbol, value, cf=cf)
    return wm


def forward_chain(kb: KnowledgeBase, facts: Facts, threshold: float = DEFAULT_THRESHOLD) -> ForwardResult:
    """Run forward chaining from the rider's answers.

    `facts` is a WorkingMemory, a dict {symptom: True / False / CF}, or a list
    of symptoms that are true. Symptoms answered False, or not given, are not
    true, so rules that need them do not fire.
    """
    wm = _working_memory(kb, facts)

    # --- 1. Fire rules (PL-FC-ENTAILS? agenda with premise counts) ---------
    count: Dict[str, int] = {r.id: len(r.premises) for r in kb.rules}
    inferred = set()
    agenda = deque(s for s in wm.true_facts())
    fired: List[Rule] = []
    while agenda:
        p = agenda.popleft()
        if p in inferred:
            continue
        inferred.add(p)
        for rule in kb.rules_using(p):
            count[rule.id] -= 1
            if count[rule.id] == 0:
                fired.append(rule)
                if rule.conclusion not in inferred:
                    agenda.append(rule.conclusion)

    # --- 2. Certainty factors, in dependency order ---------------------------
    # The knowledge base has no cycles (checked by validate()), so every derived
    # symbol can be processed after all the symbols its fired rules use.
    by_conclusion: Dict[str, List[Rule]] = {}
    for rule in fired:
        by_conclusion.setdefault(rule.conclusion, []).append(rule)
    cf: Dict[str, float] = {s: wm.get(s).cf for s in wm.true_facts()}
    pending = dict(by_conclusion)
    while pending:
        ready = [s for s, rules in pending.items()
                 if all(p in cf for r in rules for p in r.premises)]
        if not ready:  # only possible with circular rules
            raise ValueError("circular rules: " + ", ".join(sorted(pending)))
        for symbol in sorted(ready):
            rules = pending.pop(symbol)
            contributions = [r.cf * min(cf[p] for p in r.premises) for r in rules]
            cf[symbol] = combine_cf(contributions)
            premises: List[str] = []
            for r in rules:
                premises += [p for p in r.premises if p not in premises]
            wm.tell(symbol, True, cf=round(cf[symbol], 4),
                    by=",".join(r.id for r in rules), premises=premises)

    # --- 3. Rank the faults ---------------------------------------------------
    diagnoses = [
        Diagnosis(s, round(cf[s], 4), [r.id for r in rules], kb.symbols[s].severity)
        for s, rules in by_conclusion.items()
        if kb.is_fault(s) and cf[s] >= threshold
    ]
    diagnoses.sort(key=lambda d: (-d.cf, d.fault))
    return ForwardResult(wm=wm, fired=fired, diagnoses=diagnoses)


# ---------------------------------------------------------------------------
# Command line: python src/forward_chaining.py <symptom> <symptom> ...
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnose faults by forward chaining.")
    parser.add_argument("symptoms", nargs="*", help="symptoms that are true, e.g. horn_weak")
    parser.add_argument("--lang", choices=("vi", "en"), default="vi")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    parser.add_argument("--list-symptoms", action="store_true", help="list every symptom and its question")
    args = parser.parse_args(argv)

    try:  # Vietnamese text on older Windows consoles
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    kb = load_kb()
    if args.list_symptoms or not args.symptoms:
        for sid in sorted(kb.symptoms):
            print(f"{sid:32} {kb.question(sid, args.lang)}")
        return 0

    try:
        result = forward_chain(kb, args.symptoms, threshold=args.threshold)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    print(f"Rules fired ({result.rules_fired}): {', '.join(r.id for r in result.fired) or '-'}")
    if not result.diagnoses:
        print("No fault reached the threshold.")
        return 0
    for i, d in enumerate(result.diagnoses, 1):
        print(f"\n{i}. {kb.text(d.fault, args.lang)}  [CF {d.cf:.2f}, {d.severity}]")
        print(f"   {kb.action(d.fault, args.lang)}")
        for line in result.how(d.fault):
            print(f"   - {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
