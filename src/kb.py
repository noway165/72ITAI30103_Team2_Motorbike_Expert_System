"""Knowledge base for the motorbike fault diagnosis expert system.

This module is shared by every part of the system:
    - load_kb()      reads every JSON file in knowledge_base/ into one KnowledgeBase
    - validate()     checks the knowledge base for mistakes (run it after editing rules)
    - WorkingMemory  stores the facts known during one diagnosis session

The file format is described in docs/kb_format.md.

Run from the repository root to check the knowledge base:
    python src/kb.py
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KB_DIR = ROOT / "knowledge_base"

KINDS = ("symptom", "intermediate", "fault")
LANGUAGES = ("vi", "en")
SEVERITIES = ("self", "mechanic")

# JSON section name -> (symbol kind, field holding the display text)
SECTIONS = {
    "symptoms": ("symptom", "question"),
    "intermediates": ("intermediate", "description"),
    "faults": ("fault", "name"),
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Symbol:
    """A propositional symbol: a symptom the rider is asked about, an
    intermediate fact derived by rules, or a fault (final diagnosis)."""

    id: str
    kind: str
    subsystem: str
    file: str
    text: Dict[str, str]  # question (symptom), description (intermediate), name (fault)
    hint: Dict[str, str] = field(default_factory=dict)  # symptoms only, optional
    action: Dict[str, str] = field(default_factory=dict)  # faults only
    severity: Optional[str] = None  # faults only: "self" or "mechanic"


@dataclass(frozen=True)
class Rule:
    """A Horn clause: if every premise is true, the conclusion is true
    with certainty factor `cf`."""

    id: str
    premises: Tuple[str, ...]
    conclusion: str
    cf: float
    subsystem: str
    file: str
    source: str = ""
    note: str = ""

    def __str__(self) -> str:
        return f"{self.id}: IF {' AND '.join(self.premises)} THEN {self.conclusion} (CF {self.cf})"


class KnowledgeBase:
    def __init__(self, symbols: Dict[str, Symbol], rules: List[Rule], problems: List[str]):
        self.symbols = symbols
        self.rules = rules
        # Problems found while reading the files (bad JSON, missing fields, duplicates).
        # validate() reports them as errors.
        self.problems = problems
        self._by_conclusion: Dict[str, List[Rule]] = {}
        self._by_premise: Dict[str, List[Rule]] = {}
        for rule in rules:
            self._by_conclusion.setdefault(rule.conclusion, []).append(rule)
            for premise in rule.premises:
                self._by_premise.setdefault(premise, []).append(rule)

    # --- symbols ---------------------------------------------------------

    def _of_kind(self, kind: str) -> Dict[str, Symbol]:
        return {s.id: s for s in self.symbols.values() if s.kind == kind}

    @property
    def symptoms(self) -> Dict[str, Symbol]:
        return self._of_kind("symptom")

    @property
    def intermediates(self) -> Dict[str, Symbol]:
        return self._of_kind("intermediate")

    @property
    def faults(self) -> Dict[str, Symbol]:
        return self._of_kind("fault")

    def is_askable(self, symbol: str) -> bool:
        """Symptoms are asked to the rider; other symbols are only derived."""
        return symbol in self.symbols and self.symbols[symbol].kind == "symptom"

    def is_fault(self, symbol: str) -> bool:
        return symbol in self.symbols and self.symbols[symbol].kind == "fault"

    def text(self, symbol: str, lang: str = "vi") -> str:
        """Question, description or fault name in the given language."""
        texts = self.symbols[symbol].text
        return texts.get(lang) or texts.get("en") or symbol

    def question(self, symbol: str, lang: str = "vi") -> str:
        if not self.is_askable(symbol):
            raise ValueError(f"{symbol!r} is not a symptom, so it cannot be asked")
        return self.text(symbol, lang)

    def action(self, fault: str, lang: str = "vi") -> str:
        actions = self.symbols[fault].action
        return actions.get(lang) or actions.get("en") or ""

    # --- rules -----------------------------------------------------------

    def rule(self, rule_id: str) -> Rule:
        for r in self.rules:
            if r.id == rule_id:
                return r
        raise KeyError(rule_id)

    def rules_concluding(self, symbol: str) -> List[Rule]:
        """Rules whose conclusion is `symbol` (used by backward chaining)."""
        return list(self._by_conclusion.get(symbol, []))

    def rules_using(self, symbol: str) -> List[Rule]:
        """Rules that have `symbol` as a premise (useful for forward chaining)."""
        return list(self._by_premise.get(symbol, []))

    def summary(self) -> str:
        return (f"{len(self.symptoms)} symptoms, {len(self.intermediates)} intermediates, "
                f"{len(self.faults)} faults, {len(self.rules)} rules")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _texts(value, where: str, problems: List[str], required: bool = True) -> Dict[str, str]:
    if value is None:
        if required:
            problems.append(f"{where}: missing text")
        return {}
    if isinstance(value, str):  # allow a plain string, treated as Vietnamese
        return {"vi": value}
    if not isinstance(value, dict) or not all(isinstance(v, str) for v in value.values()):
        problems.append(f"{where}: text must be an object like {{\"vi\": ..., \"en\": ...}}")
        return {}
    return dict(value)


def load_kb(kb_dir: Path | str = DEFAULT_KB_DIR) -> KnowledgeBase:
    """Read every *.json file under `kb_dir` (sorted, recursive) into one knowledge base."""
    kb_dir = Path(kb_dir)
    symbols: Dict[str, Symbol] = {}
    rules: List[Rule] = []
    problems: List[str] = []
    seen_rule_ids: Dict[str, str] = {}

    files = sorted(kb_dir.rglob("*.json"))
    if not files:
        problems.append(f"no .json files found in {kb_dir}")

    for path in files:
        name = path.relative_to(kb_dir).as_posix()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            problems.append(f"{name}: invalid JSON at line {e.lineno}, column {e.colno}: {e.msg}")
            continue
        if not isinstance(data, dict):
            problems.append(f"{name}: top level must be a JSON object")
            continue

        subsystem = data.get("subsystem") or path.stem

        for section, (kind, text_field) in SECTIONS.items():
            entries = data.get(section, {})
            if not isinstance(entries, dict):
                problems.append(f"{name}: '{section}' must be an object keyed by symbol id")
                continue
            for sid, spec in entries.items():
                where = f"{name}: {kind} '{sid}'"
                if sid in symbols:
                    problems.append(f"{where} is already defined in {symbols[sid].file}")
                    continue
                if not isinstance(spec, dict):
                    problems.append(f"{where}: definition must be an object")
                    continue
                symbol = Symbol(
                    id=sid, kind=kind, subsystem=subsystem, file=name,
                    text=_texts(spec.get(text_field), f"{where}.{text_field}", problems),
                )
                if kind == "symptom":
                    symbol.hint = _texts(spec.get("hint"), f"{where}.hint", problems, required=False)
                if kind == "fault":
                    symbol.action = _texts(spec.get("action"), f"{where}.action", problems)
                    symbol.severity = spec.get("severity")
                    if symbol.severity not in SEVERITIES:
                        problems.append(f"{where}: severity must be one of {SEVERITIES}")
                symbols[sid] = symbol

        raw_rules = data.get("rules", [])
        if not isinstance(raw_rules, list):
            problems.append(f"{name}: 'rules' must be a list")
            continue
        for i, spec in enumerate(raw_rules):
            where = f"{name}: rule #{i + 1}"
            if not isinstance(spec, dict):
                problems.append(f"{where}: must be an object")
                continue
            rid = spec.get("id")
            if not rid or not isinstance(rid, str):
                problems.append(f"{where}: missing 'id'")
                continue
            where = f"{name}: rule {rid}"
            if rid in seen_rule_ids:
                problems.append(f"{where}: id already used in {seen_rule_ids[rid]}")
                continue
            premises = spec.get("if")
            conclusion = spec.get("then")
            cf = spec.get("cf", 1.0)
            if not isinstance(premises, list) or not premises or not all(isinstance(p, str) for p in premises):
                problems.append(f"{where}: 'if' must be a non-empty list of symbol ids")
                continue
            if not isinstance(conclusion, str) or not conclusion:
                problems.append(f"{where}: 'then' must be one symbol id")
                continue
            if isinstance(cf, bool) or not isinstance(cf, (int, float)) or not 0 < cf <= 1:
                problems.append(f"{where}: 'cf' must be a number in (0, 1]")
                continue
            if len(set(premises)) != len(premises):
                problems.append(f"{where}: a premise is listed twice")
            seen_rule_ids[rid] = name
            rules.append(Rule(
                id=rid, premises=tuple(premises), conclusion=conclusion, cf=float(cf),
                subsystem=subsystem, file=name,
                source=str(spec.get("source", "")), note=str(spec.get("note", "")),
            ))

    return KnowledgeBase(symbols, rules, problems)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

@dataclass
class Report:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def derivable_symbols(kb: KnowledgeBase) -> set:
    """Symbols that some combination of symptoms can make true (forward closure)."""
    derivable = set(kb.symptoms)
    changed = True
    while changed:
        changed = False
        for rule in kb.rules:
            if rule.conclusion not in derivable and all(p in derivable for p in rule.premises):
                derivable.add(rule.conclusion)
                changed = True
    return derivable


def _find_cycle(kb: KnowledgeBase) -> Optional[List[str]]:
    """Return one cycle of symbols (conclusion depends on itself), or None."""
    graph: Dict[str, List[str]] = {}
    for rule in kb.rules:
        graph.setdefault(rule.conclusion, []).extend(rule.premises)
    WHITE, GREY, BLACK = 0, 1, 2
    color: Dict[str, int] = {}
    stack: List[str] = []

    def visit(node: str) -> Optional[List[str]]:
        color[node] = GREY
        stack.append(node)
        for nxt in graph.get(node, []):
            if color.get(nxt, WHITE) == GREY:
                return stack[stack.index(nxt):] + [nxt]
            if color.get(nxt, WHITE) == WHITE:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        color[node] = BLACK
        return None

    for node in list(graph):
        if color.get(node, WHITE) == WHITE:
            found = visit(node)
            if found:
                return found
    return None


def validate(kb: KnowledgeBase) -> Report:
    report = Report(errors=list(kb.problems))
    symbols = kb.symbols

    # Rules refer to known symbols, and respect the symptom -> intermediate -> fault layering
    for rule in kb.rules:
        for p in rule.premises:
            if p not in symbols:
                report.errors.append(f"{rule.file}: rule {rule.id} uses unknown symbol '{p}'")
            elif symbols[p].kind == "fault":
                report.errors.append(
                    f"{rule.file}: rule {rule.id} uses fault '{p}' as a premise; "
                    "make it an intermediate if other rules build on it")
        if rule.conclusion not in symbols:
            report.errors.append(f"{rule.file}: rule {rule.id} concludes unknown symbol '{rule.conclusion}'")
        elif symbols[rule.conclusion].kind == "symptom":
            report.errors.append(
                f"{rule.file}: rule {rule.id} concludes symptom '{rule.conclusion}'; "
                "symptoms are only asked, never derived")

    # Two rules with the same premises and conclusion
    seen: Dict[Tuple[frozenset, str], str] = {}
    for rule in kb.rules:
        key = (frozenset(rule.premises), rule.conclusion)
        if key in seen:
            report.warnings.append(f"rule {rule.id} duplicates rule {seen[key]}")
        else:
            seen[key] = rule.id

    cycle = _find_cycle(kb)
    if cycle:
        report.errors.append("circular rules: " + " -> ".join(cycle))

    # Every fault and intermediate must be reachable from symptoms
    derivable = derivable_symbols(kb)
    for sid, sym in symbols.items():
        if sym.kind == "symptom":
            continue
        if not kb.rules_concluding(sid):
            report.errors.append(f"{sym.file}: {sym.kind} '{sid}' is not concluded by any rule")
        elif sid not in derivable:
            report.errors.append(f"{sym.file}: {sym.kind} '{sid}' can never be derived from symptoms")
    for rule in kb.rules:
        blocked = [p for p in rule.premises if p in symbols and p not in derivable]
        if blocked:
            report.errors.append(
                f"{rule.file}: rule {rule.id} can never fire (no way to derive {', '.join(blocked)})")

    # Unused symbols
    for sid, sym in symbols.items():
        if sym.kind in ("symptom", "intermediate") and not kb.rules_using(sid):
            report.warnings.append(f"{sym.file}: {sym.kind} '{sid}' is not used by any rule")

    # Missing translations
    for sid, sym in symbols.items():
        missing = [lang for lang in LANGUAGES if not sym.text.get(lang)]
        if sym.kind == "fault":
            missing += [f"action.{lang}" for lang in LANGUAGES if not sym.action.get(lang)]
        if missing:
            report.warnings.append(f"{sym.file}: {sym.kind} '{sid}' is missing {', '.join(missing)}")

    # Rules without a source (needed for citations in the report); one line per file
    no_source: Dict[str, List[str]] = {}
    for rule in kb.rules:
        if not rule.source.strip():
            no_source.setdefault(rule.file, []).append(rule.id)
    for file, ids in no_source.items():
        report.warnings.append(f"{file}: {len(ids)} rule(s) have no source yet ({', '.join(ids)})")

    return report


# ---------------------------------------------------------------------------
# Working memory
# ---------------------------------------------------------------------------

@dataclass
class Fact:
    value: bool
    cf: float = 1.0
    by: str = "user"  # "user" for an answer, otherwise the id of the rule that derived it
    premises: Tuple[str, ...] = ()


class WorkingMemory:
    """Facts known during one diagnosis session.

    A symbol can be known true, known false, or unknown (not in memory).
    Derived facts remember which rule produced them, so the explanation
    module can answer "how".
    """

    def __init__(self) -> None:
        self._facts: Dict[str, Fact] = {}

    def tell(self, symbol: str, value: bool = True, cf: float = 1.0,
             by: str = "user", premises: Iterable[str] = ()) -> bool:
        """Record a fact. Returns True if memory changed.

        A later call for the same symbol replaces the earlier fact; combining
        certainty factors from several rules is the inference engine's job.
        """
        new = Fact(bool(value), float(cf), by, tuple(premises))
        if self._facts.get(symbol) == new:
            return False
        self._facts[symbol] = new
        return True

    def ask(self, symbol: str) -> Optional[bool]:
        """True, False, or None if unknown."""
        fact = self._facts.get(symbol)
        return None if fact is None else fact.value

    def is_true(self, symbol: str) -> bool:
        return self.ask(symbol) is True

    def is_false(self, symbol: str) -> bool:
        return self.ask(symbol) is False

    def is_known(self, symbol: str) -> bool:
        return symbol in self._facts

    def get(self, symbol: str) -> Optional[Fact]:
        return self._facts.get(symbol)

    def true_facts(self) -> List[str]:
        return [s for s, f in self._facts.items() if f.value]

    def forget(self, symbol: str) -> None:
        self._facts.pop(symbol, None)

    def reset(self) -> None:
        self._facts.clear()

    def explain(self, symbol: str) -> List[Tuple[str, Fact]]:
        """Facts that led to `symbol`, premises first ("how" explanation)."""
        order: List[Tuple[str, Fact]] = []
        visited = set()

        def walk(s: str) -> None:
            if s in visited or s not in self._facts:
                return
            visited.add(s)
            fact = self._facts[s]
            for p in fact.premises:
                walk(p)
            order.append((s, fact))

        walk(symbol)
        return order

    def __contains__(self, symbol: str) -> bool:
        return symbol in self._facts

    def __len__(self) -> int:
        return len(self._facts)


# ---------------------------------------------------------------------------
# Command line: python src/kb.py
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Load and check the knowledge base.")
    parser.add_argument("--kb", default=str(DEFAULT_KB_DIR), help="knowledge base folder")
    parser.add_argument("--list", action="store_true", help="list faults and the rules that conclude them")
    args = parser.parse_args(argv)

    kb = load_kb(args.kb)
    print(f"Knowledge base: {kb.summary()}")

    if args.list:
        for fid, fault in sorted(kb.faults.items(), key=lambda kv: (kv[1].subsystem, kv[0])):
            rule_ids = ", ".join(r.id for r in kb.rules_concluding(fid)) or "-"
            print(f"  [{fault.subsystem}] {fid} ({fault.severity}): {rule_ids}")

    report = validate(kb)
    for e in report.errors:
        print(f"ERROR   {e}")
    for w in report.warnings:
        print(f"WARNING {w}")
    print(f"\n{len(report.errors)} error(s), {len(report.warnings)} warning(s)")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
