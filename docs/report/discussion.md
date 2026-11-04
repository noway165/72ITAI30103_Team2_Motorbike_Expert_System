# Discussion (draft)

Author: Kieu Bao Giang. Draft for the final report (07/11/2026), to be sent to Lâm on 09/11.
Marked [TODO] = numbers to take from Khoa's full evaluation in `results/` once it is merged.

## 5.1 Where the system goes wrong

On the 20 scenarios written so far for the starting, fuel, electrical, brake,
tyre and suspension systems, forward chaining put the expected fault first in 18
cases (90%) [TODO: final top-1 / top-3 on all 30 scenarios]. Wang's algorithm
proved exactly the faults that forward chaining derived, so the two misses are
not bugs in the engine: the knowledge base had no rule that matched the rider's
answers.

Both misses had the same shape. A rule derived an intermediate fact (for example
"low electrical power" from "the starter only clicks" and "the horn is weak"),
but every rule leading from that fact to a fault needed one more symptom, such
as "the battery is more than two years old". A rider whose battery was drained by
leaving the key on does not have that symptom, so the program stopped half way
and reported no fault, although it already knew where the problem was. A check of
the whole knowledge base found nine such intermediate facts, three of them in the
engine and transmission rules. Adding a "fallback" rule with a lower CF from each
intermediate fact to its most common fault fixes the problem while keeping the
more specific rules on top when the extra symptom is present.

## 5.2 Forward versus backward chaining

Both engines use the same rules and the same CF combination, and gave identical
ranked lists on every scenario. They differ in how the rider uses them. Forward
chaining needs the rider to describe all the symptoms first, which is fast for an
experienced rider but easy to get wrong for a beginner. Backward chaining asks
only questions that can still change the result and can explain *why* it asks,
but without a chosen subsystem it asked 36–45 of the 73 questions per scenario
[TODO: average questions, with and without choosing the subsystem]. Choosing the
subsystem first, as a mechanic would ("the problem is with starting"), is the
simplest way to shorten the dialogue.

## 5.3 Certainty factors

CFs give a useful ranking, but they are not probabilities. The rule CFs were set
by each author from the sources and common sense, not measured on real repair
data, so a CF of 0.7 from one author may not mean the same as 0.7 from another.
The combination formula also assumes that the rules are independent pieces of
evidence, which is not true when two rules share a premise (SF02 and SF03 both
use "low electrical power"). In our tests these limits mostly affected the
distance between the first and second fault, not which fault came first.

## 5.4 Limitations

- **Horn clauses only.** The rules cannot say "not", so a "no" answer can never
  rule a fault out; it can only stop a rule from firing. Negative evidence (MYCIN's
  negative CFs) would let the system lower a fault's CF.
- **Size.** 76 rules for 40 faults cover the common problems of Vietnamese
  scooters and manual motorbikes, but not electronic faults (ABS, smart key) or
  model-specific problems.
- **Sources.** Many rules are based on owner's manuals of models sold abroad,
  and a few rely on retailer guides or on a car-engine guide rather than a
  motorcycle service manual (for example the CVT belt and throttle body rules)
  [TODO: rules still without a source in the other subsystems at the deadline].
  A mechanic should review the rules before the system is used for real.
- **Test scenarios.** The scenarios were written by team members, not collected
  from real repair shops, so the accuracy measures how well the rules match our
  own understanding of each fault.

## 5.5 Future work

- Fallback rules for the remaining dead-end intermediate facts, and a checker
  warning for them.
- Negative certainty factors, so that "no" answers can lower a fault's CF.
- Scenarios from real repair records, and rule CFs estimated from them.
