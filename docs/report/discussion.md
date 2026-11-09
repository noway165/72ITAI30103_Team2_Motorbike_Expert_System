# Discussion (draft)

Author: Kieu Bao Giang. Draft for the final report, updated 09/11/2026 and sent to Lâm.
Numbers: 30 test scenarios (BT, SE, ET) and the knowledge base of 09/11 (77 rules,
40 faults), measured with `python src/wang.py --scenarios` and the same top-1 /
top-3 / question counts as the evaluation plan. Khoa's script in `results/` is not
merged yet; when it is, check that its numbers match the ones below and keep his
charts as the reference.

## 5.1 Where the system goes wrong

On the 30 scenarios, forward chaining put the expected fault first in 29 cases
(96.7%), and the same 29 were in the top 3. The scenarios for each subsystem were
written by a team member who did not write its rules: 10/10 correct for starting,
fuel and electrics, 10/10 for engine and transmission, 9/10 for brakes, tyres and
suspension. Wang's algorithm proved exactly the faults that forward chaining
derived, in every scenario and in 500 random sets of answers, so the miss is not
a bug in the engine: the knowledge base had no rule that matched the rider's
answers.

The first run (20 scenarios, 4 November) found two misses with the same shape. A
rule derived an intermediate fact (for example "low electrical power" from "the
starter only clicks" and "the horn is weak"), but every rule leading from that
fact to a fault needed one more symptom, such as "the battery is more than two
years old". A rider whose battery was drained by leaving the key on does not have
that symptom, so the program stopped half way and reported no fault, although it
already knew where the problem was. A check of the whole knowledge base found nine
such "dead-end" intermediate facts. Adding a fallback rule with a lower CF from
the intermediate fact to its most common fault fixes the problem while keeping the
more specific rules on top when the extra symptom is present; this fixed the
battery case (rule SF14) and the three cases in the engine and transmission rules.
The remaining miss (worn rear shock, BT10) needs the same kind of rule. Until then,
the "By symptoms" screen shows the intermediate fact it found and the symptoms that
would complete the diagnosis, instead of only "no fault found".

## 5.2 Forward versus backward chaining

Both engines use the same rules and the same CF combination, and gave identical
ranked lists on all 30 scenarios. They differ in how the rider uses them. Forward
chaining needs the rider to describe all the symptoms first, which is fast for an
experienced rider but easy to get wrong for a beginner. Backward chaining asks
only questions that can still change the result and can explain *why* it asks,
but without a chosen subsystem it asked on average 39.7 of the 73 questions per
scenario. When the rider first chooses the part of the motorbike with the problem,
as a mechanic would ("the problem is with starting"), the average drops to 9.0
questions, about four times fewer, and 29 of 30 scenarios are still correct.
Forward chaining fired 2.0 rules per scenario on average.

## 5.3 Certainty factors

CFs give a useful ranking, but they are not probabilities. The rule CFs were set
by each author from the sources and common sense, not measured on real repair
data, so a CF of 0.7 from one author may not mean the same as 0.7 from another.
The combination formula also assumes that the rules are independent pieces of
evidence, which is not true when rules share a premise (SF02, SF03 and SF14 all
use "low electrical power", so three rules built on the same fact push the CF of
a weak battery to 0.96). In our tests these limits mostly affected the distance
between the first and second fault, not which fault came first.

## 5.4 Limitations

- **Horn clauses only.** The rules cannot say "not", so a "no" answer can never
  rule a fault out; it can only stop a rule from firing. In scenario ET05 the
  rider says the coolant level is fine, but "low coolant" still appears in second
  place (CF 0.45) through a fallback rule, because "coolant is fine" cannot be
  expressed. Negative evidence (MYCIN's negative CFs) would let the system lower
  a fault's CF.
- **Size.** 77 rules for 40 faults cover the common problems of Vietnamese
  scooters and manual motorbikes, but not electronic faults (ABS, smart key) or
  model-specific problems.
- **Sources.** Many rules are based on owner's manuals of models sold abroad,
  and a few rely on retailer guides or on a car-engine guide rather than a
  motorcycle service manual (for example the CVT belt and throttle body rules).
  On 9 November, 23 rules of the starting, electrical and tyre subsystems still
  had no source. A mechanic should review the rules before the system is used
  for real.
- **Test scenarios.** The scenarios were written by team members, not collected
  from real repair shops, so the accuracy measures how well the rules match our
  own understanding of each fault. With 30 scenarios, one more miss changes the
  accuracy by more than three points.

## 5.5 Future work

- Fallback rules for the remaining dead-end intermediate facts, and a checker
  warning for them.
- Negative certainty factors, so that "no" answers can lower a fault's CF.
- Scenarios from real repair records, and rule CFs estimated from them.
