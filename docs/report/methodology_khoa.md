# Methodology: backward chaining and explanations

Author: Nguyen Nam Khoa. Final draft, 13/11/2026 (K1: cut from 138 to about 115 words, one figure; the old
screenshot `fig_backward_screen_why.png` showed the previous screen and is dropped).
Limit for this part: about 120 words and 1 figure. Section and figure numbers (3.y) are set by `tools/build_report.py`.

## 3.y Backward chaining and explanations

Backward chaining is goal-driven (Figure 3.y.1). Each fault of the part the rider chooses is a hypothesis.
For every rule that concludes it, the premises are proved in turn: an intermediate fact becomes a new goal,
and a symptom is asked once and remembered. A rule is dropped at its first false premise, so questions that
cannot change the result are never asked. All rules of a goal are tried and combined with the CF formulas
above, so the result equals forward chaining; asking the part first needs only 9.0 questions instead of 39.7.
"Why" shows the rule chain from the hypothesis to the current question; "how" lists the facts and rules
behind a fault.

Figure 3.y.1: Backward chaining loop that asks one question at a time.
File: `figures/fig_backward_flow.png` (made by `python src/evaluate.py --charts`).
