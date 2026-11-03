# Methodology: forward chaining, ranking and verification (draft)

Author: Kieu Bao Giang. Draft for the final report (05/11/2026), to be sent to Lâm on 09/11.
Numbers refer to the knowledge base of 03/11/2026 (73 symptoms, 9 intermediate facts, 40 faults, 76 rules).

## 3.x Forward chaining

The knowledge base is a set of propositional Horn clauses. Each rule has the form

    IF p1 AND p2 AND ... AND pk THEN q   (certainty factor c)

where the premises are symptoms or intermediate facts and the conclusion is an
intermediate fact or a fault. Symptoms are only asked, never concluded, and faults
are never used as premises, so every chain of reasoning goes
symptom → intermediate → fault.

Forward chaining is data-driven. The rider first answers the symptom questions;
every symptom answered "yes" is put in working memory. The engine then follows
PL-FC-ENTAILS? [Russell and Norvig, ch. 7]:

1. every rule keeps a counter of the premises not yet known to be true;
2. an agenda (queue) starts with the symptoms that are true;
3. a symbol is taken from the agenda; the counter of every rule that uses it is
   decreased, and a rule whose counter reaches zero fires, putting its conclusion
   on the agenda;
4. the process stops when the agenda is empty.

Each symbol is processed once, so the running time is linear in the total size of
the rules. Symptoms answered "no" are simply not true; since the rules contain no
negation, no rule needs them.

## 3.y Ranking with certainty factors

Several faults can be derived from the same answers, so the result is a ranked
list. We use the certainty factor (CF) model of MYCIN [Buchanan and Shortliffe],
restricted to positive evidence because our rules contain no negation:

| Case | Certainty factor |
|---|---|
| symptom answered "yes" | 1.0 (or the rider's own estimate in (0, 1]) |
| premises of one rule (AND) | min of the premises' CFs |
| conclusion of one rule | rule CF × CF of the premises |
| several rules with the same conclusion | CF = CF1 + CF2 × (1 − CF1), applied rule by rule |

Faults with CF ≥ 0.2 are reported, best first. Rule CFs were set by the rule's
author: 0.9–1.0 when the conclusion is almost certain (for example an empty fuel
gauge), 0.7–0.85 for the most common cause of a group of symptoms, and 0.5–0.65
when other causes are likely.

The CFs are computed after the rules have fired, in dependency order: a symbol
concluded by several rules is combined before it is used as a premise by the next
rule. This order always exists because the knowledge base checker rejects
circular rules. The combination is commutative, so the result does not depend on
the order in which rules fire, and forward and backward chaining give the same
CF for the same answers.

Example (real knowledge base). The starter only clicks, the horn is weak, the
battery is more than two years old and the motorbike has not been used for three
weeks:

| Rule | Computation | CF |
|---|---|---|
| SF01 → low_electrical_power | 0.9 × min(1, 1) | 0.90 |
| SF02 → weak_battery | 0.85 × min(0.90, 1) | 0.765 |
| SF03 → weak_battery | 0.75 × min(0.90, 1) | 0.675 |
| combined | 0.765 + 0.675 × (1 − 0.765) | **0.92** |

Every reported fault keeps the rules and facts that produced it, so the program
can explain *how* it reached the conclusion.

## 3.z Verification with Wang's algorithm

Forward and backward chaining are our own code, so they may contain mistakes. To
check them we use an independent theorem prover for propositional logic, Wang's
algorithm [Wang 1960]. A sequent A1, ..., An ⇒ B1, ..., Bm is valid when at
least one B is true whenever all the A are true. The algorithm removes one
connective at a time (¬ moves a formula to the other side; ∧ on the left and ∨ on
the right are kept; ∧ on the right, ∨ on the left and → on the left split the
proof into two branches). A branch is closed when the same atom appears on both
sides; the sequent is valid when every branch is closed.

To check that a fault f follows from the answers, every rule becomes a formula
(p1 ∧ ... ∧ pk) → q, every "yes" answer an atom and every "no" answer a negated
atom, and we prove

    rules, answers ⇒ f

Certainty factors are ignored: Wang's algorithm decides logical entailment only.
Two optimisations keep the proofs small without changing the result: only the
rules that can contribute to f are included (rules concluding f, rules concluding
their premises, and so on), and on the left side a rule whose premises are all
known is decomposed first, so its first branch closes at once.

Forward chaining is sound and complete for Horn clauses [Russell and Norvig], so
the set of faults it derives (with the threshold set to 0) must equal the set of
faults proved by Wang's algorithm. We compared the two on the 20 test scenarios
and on 500 random sets of answers (each symptom "yes" with probability 0.15),
that is 20,800 entailment checks (40 faults per set of answers; 1,227 faults
were proved in the random sets). They agreed in every
case. Any wrong diagnosis is therefore caused by the knowledge base, not by the
inference engine; Section 5 uses this to analyse the misdiagnosed scenarios.

## References

- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., Pearson, 2020, chapter 7.
- B. G. Buchanan and E. H. Shortliffe, *Rule-Based Expert Systems: The MYCIN Experiments of the Stanford Heuristic Programming Project*, Addison-Wesley, 1984.
- H. Wang, "Toward Mechanical Mathematics," *IBM Journal of Research and Development*, vol. 4, no. 1, pp. 2–22, 1960.
