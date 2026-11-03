"""Wang's algorithm: checking the inference engines with a theorem prover (owner: Giang).

Wang's algorithm (Hao Wang, 1960) decides whether a sequent of propositional
logic is valid:

    A1, A2, ..., An  =>  B1, B2, ..., Bm

means "if every A on the left is true, at least one B on the right is true".
Each step removes one connective from a formula, using the rules below, until
only atoms are left:

    left side                          right side
    not A   : move A to the right      not A   : move A to the left
    A and B : keep A and B on left     A or B  : keep A and B on right
    A or B  : split, one branch each   A and B : split, one branch each
    A -> B  : split: prove A on the    A -> B  : move A to the left, keep B
              right, and B on the left            on the right

A sequent with the same atom on both sides is an axiom (valid). A sequent that
has only atoms, and no atom on both sides, is not valid. A sequent is valid
when every branch ends in an axiom.

For the expert system, KB + answers |= fault holds exactly when the sequent

    rule1, rule2, ..., symptom1, symptom2, ...  =>  fault

is valid, where each rule "IF p1 AND p2 THEN q" is the formula (p1 and p2) -> q.
Certainty factors are ignored: Wang checks the logic only. Forward chaining
must derive exactly the faults that Wang proves; check_engines() compares them.

Run from the repository root:
    python src/wang.py horn_weak starter_clicks_or_silent battery_older_than_2_years
    python src/wang.py --trace --goal weak_battery horn_weak starter_clicks_or_silent battery_older_than_2_years
    python src/wang.py --scenarios            # compare with forward chaining on scenarios/
    python src/wang.py --random 500           # ... and on 500 random sets of symptoms
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple, Union

from forward_chaining import forward_chain
from kb import KnowledgeBase, Rule, load_kb
from scenarios import check_scenarios, load_scenarios

MAX_STEPS = 1_000_000


# ---------------------------------------------------------------------------
# Formulas
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Atom:
    name: str

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Not:
    arg: "Formula"

    def __str__(self) -> str:
        return f"¬{_wrap(self.arg)}"


@dataclass(frozen=True)
class And:
    args: Tuple["Formula", ...]

    def __str__(self) -> str:
        return " ∧ ".join(_wrap(a) for a in self.args)


@dataclass(frozen=True)
class Or:
    args: Tuple["Formula", ...]

    def __str__(self) -> str:
        return " ∨ ".join(_wrap(a) for a in self.args)


@dataclass(frozen=True)
class Implies:
    left: "Formula"
    right: "Formula"

    def __str__(self) -> str:
        return f"{_wrap(self.left)} → {_wrap(self.right)}"


Formula = Union[Atom, Not, And, Or, Implies]


def _wrap(f: Formula) -> str:
    return str(f) if isinstance(f, (Atom, Not)) else f"({f})"


def rule_formula(rule: Rule) -> Formula:
    """IF p1 AND p2 THEN q  becomes  (p1 ∧ p2) → q."""
    premises = [Atom(p) for p in rule.premises]
    body = premises[0] if len(premises) == 1 else And(tuple(premises))
    return Implies(body, Atom(rule.conclusion))


# ---------------------------------------------------------------------------
# Wang's algorithm
# ---------------------------------------------------------------------------

@dataclass
class Proof:
    valid: bool
    steps: int                                       # sequents looked at
    trace: List[str] = field(default_factory=list)   # filled when trace=True


def _sequent(left: Sequence[Formula], right: Sequence[Formula]) -> str:
    return f"{', '.join(map(str, left)) or '∅'}  ⇒  {', '.join(map(str, right)) or '∅'}"


def prove(left: Sequence[Formula], right: Sequence[Formula], trace: bool = False) -> Proof:
    """Decide whether the sequent  left => right  is valid."""
    proof = Proof(valid=False, steps=0)
    proof.valid = _prove(list(left), list(right), proof, 0, trace)
    return proof


def _without(items: List[Formula], i: int) -> List[Formula]:
    return items[:i] + items[i + 1:]


def _prove(left: List[Formula], right: List[Formula], proof: Proof, depth: int, trace: bool) -> bool:
    proof.steps += 1
    if proof.steps > MAX_STEPS:
        raise RuntimeError(f"Wang's algorithm gave up after {MAX_STEPS} steps")

    def log(note: str) -> None:
        if trace:
            proof.trace.append(f"{'  ' * depth}{_sequent(left, right)}    [{note}]")

    def sub(new_left: List[Formula], new_right: List[Formula]) -> bool:
        return _prove(new_left, new_right, proof, depth + 1, trace)

    left_atoms = {f.name for f in left if isinstance(f, Atom)}
    right_atoms = {f.name for f in right if isinstance(f, Atom)}
    common = left_atoms & right_atoms
    if common:
        log(f"axiom: {sorted(common)[0]} on both sides")
        return True

    # 1. Rules that do not split the proof
    for i, f in enumerate(left):
        if isinstance(f, Not):
            log("¬ on the left")
            return sub(_without(left, i), right + [f.arg])
        if isinstance(f, And):
            log("∧ on the left")
            return sub(_without(left, i) + list(f.args), right)
    for i, f in enumerate(right):
        if isinstance(f, Not):
            log("¬ on the right")
            return sub(left + [f.arg], _without(right, i))
        if isinstance(f, Or):
            log("∨ on the right")
            return sub(left, _without(right, i) + list(f.args))
        if isinstance(f, Implies):
            log("→ on the right")
            return sub(left + [f.left], _without(right, i) + [f.right])

    # 2. Rules that split the proof (every branch must be valid)
    for i, f in enumerate(right):
        if isinstance(f, And):
            log("∧ on the right: one branch per conjunct")
            return all(sub(left, _without(right, i) + [a]) for a in f.args)
    for i, f in enumerate(left):
        if isinstance(f, Or):
            log("∨ on the left: one branch per disjunct")
            return all(sub(_without(left, i) + [a], right) for a in f.args)

    # → on the left. Any choice is correct; picking a rule whose premises are
    # already on the left closes the first branch at once, so the proof stays
    # small (the order forward chaining would fire the rules in).
    implications = [i for i, f in enumerate(left) if isinstance(f, Implies)]
    if implications:
        def ready(i: int) -> bool:
            body = left[i].left
            parts = body.args if isinstance(body, And) else (body,)
            return all(isinstance(p, Atom) and p.name in left_atoms for p in parts)
        i = next((i for i in implications if ready(i)), implications[0])
        f = left[i]
        rest = _without(left, i)
        log(f"→ on the left: {f}")
        return sub(rest, right + [f.left]) and sub(rest + [f.right], right)

    log("not valid: only atoms, none on both sides")
    return False


# ---------------------------------------------------------------------------
# Using Wang's algorithm on the knowledge base
# ---------------------------------------------------------------------------

Answers = Union[Mapping[str, bool], Iterable[str]]


def _answers(answers: Answers) -> Dict[str, bool]:
    return dict(answers) if isinstance(answers, Mapping) else {s: True for s in answers}


def relevant_rules(kb: KnowledgeBase, goal: str) -> List[Rule]:
    """Rules that can take part in proving `goal`: those concluding it, then
    those concluding their premises, and so on. Other rules can never help
    (all rules are Horn clauses), so leaving them out keeps the proof small."""
    needed, todo, rules = {goal}, [goal], []
    while todo:
        for rule in kb.rules_concluding(todo.pop()):
            rules.append(rule)
            for p in rule.premises:
                if p not in needed:
                    needed.add(p)
                    todo.append(p)
    return sorted(rules, key=lambda r: r.id)


def entails(kb: KnowledgeBase, answers: Answers, goal: str, trace: bool = False) -> Proof:
    """Wang's algorithm on  rules, answers  =>  goal.

    `answers` is a list of symptoms that are true or a dict {symptom: True / False};
    a symptom answered False goes on the left as ¬symptom.
    """
    left: List[Formula] = [rule_formula(r) for r in relevant_rules(kb, goal)]
    for symptom, value in _answers(answers).items():
        if not kb.is_askable(symptom):
            raise ValueError(f"{symptom!r} is not a symptom; only symptoms can be given")
        left.append(Atom(symptom) if value else Not(Atom(symptom)))
    return prove(left, [Atom(goal)], trace=trace)


def entailed_faults(kb: KnowledgeBase, answers: Answers) -> Dict[str, Proof]:
    """Every fault that Wang proves from the answers."""
    proofs = {fault: entails(kb, answers, fault) for fault in sorted(kb.faults)}
    return {f: p for f, p in proofs.items() if p.valid}


@dataclass
class Check:
    name: str
    wang: Set[str]      # faults proved by Wang
    forward: Set[str]   # faults derived by forward chaining (any CF)
    steps: int

    @property
    def agree(self) -> bool:
        return self.wang == self.forward


def check_engines(kb: KnowledgeBase, name: str, answers: Answers) -> Check:
    """Compare Wang with forward chaining on one set of answers."""
    proofs = entailed_faults(kb, answers)
    derived = {d.fault for d in forward_chain(kb, _answers(answers), threshold=0.0).diagnoses}
    return Check(name, set(proofs), derived, sum(p.steps for p in proofs.values()))


def random_answers(kb: KnowledgeBase, count: int, seed: int = 0, p_yes: float = 0.15) -> List[List[str]]:
    """`count` random sets of symptoms, each symptom true with probability p_yes."""
    rng = random.Random(seed)
    symptoms = sorted(kb.symptoms)
    return [[s for s in symptoms if rng.random() < p_yes] for _ in range(count)]


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def _run_scenarios(kb: KnowledgeBase, random_count: int) -> int:
    scenarios = load_scenarios()
    problems = check_scenarios(kb, scenarios)
    for p in problems:
        print(f"ERROR   {p}")
    if problems:
        return 1

    disagreements = 0
    top1 = top3 = 0
    print(f"{'id':6} {'expected':32} {'forward chaining top-1 (CF)':42} top-3  Wang=FC")
    for s in scenarios:
        result = forward_chain(kb, s.symptoms)
        ranked = [d.fault for d in result.diagnoses]
        best = f"{result.diagnoses[0].fault} ({result.diagnoses[0].cf:.2f})" if ranked else "-"
        in_top1 = ranked[:1] == [s.expected]
        in_top3 = s.expected in ranked[:3]
        top1 += in_top1
        top3 += in_top3
        check = check_engines(kb, s.id, s.symptoms)
        disagreements += not check.agree
        print(f"{s.id:6} {s.expected:32} {best:42} {'yes' if in_top3 else 'NO ':5}  "
              f"{'yes' if check.agree else 'NO'}")
    n = len(scenarios)
    print(f"\n{n} scenarios: top-1 {top1}/{n}, top-3 {top3}/{n}; "
          f"Wang and forward chaining disagree on {disagreements}")

    if random_count:
        checks = [check_engines(kb, f"random #{i + 1}", answers)
                  for i, answers in enumerate(random_answers(kb, random_count))]
        bad = [c for c in checks if not c.agree]
        faults = sum(len(c.wang) for c in checks)
        print(f"{random_count} random symptom sets: {faults} faults proved, "
              f"Wang and forward chaining disagree on {len(bad)}")
        for c in bad:
            print(f"  {c.name}: only Wang {sorted(c.wang - c.forward)}, "
                  f"only forward chaining {sorted(c.forward - c.wang)}")
        disagreements += len(bad)
    return 0 if disagreements == 0 else 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check entailment with Wang's algorithm.")
    parser.add_argument("symptoms", nargs="*", help="symptoms that are true")
    parser.add_argument("--goal", help="prove only this fault")
    parser.add_argument("--trace", action="store_true", help="print every sequent of the proof")
    parser.add_argument("--scenarios", action="store_true",
                        help="compare with forward chaining on every scenario in scenarios/")
    parser.add_argument("--random", type=int, default=0, metavar="N",
                        help="with --scenarios: also compare on N random sets of symptoms")
    args = parser.parse_args(argv)

    try:  # logic symbols on older Windows consoles
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    kb = load_kb()
    if args.scenarios:
        return _run_scenarios(kb, args.random)
    if not args.symptoms:
        parser.print_help()
        return 0

    try:
        if args.goal:
            proof = entails(kb, args.symptoms, args.goal, trace=args.trace)
            print("\n".join(proof.trace))
            print(f"{args.goal}: {'proved' if proof.valid else 'not proved'} ({proof.steps} sequents)")
            return 0
        check = check_engines(kb, "input", args.symptoms)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    print(f"Proved by Wang: {', '.join(sorted(check.wang)) or '-'} ({check.steps} sequents)")
    print(f"Forward chaining agrees: {'yes' if check.agree else 'NO'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
