# Methodology: backward chaining and explanations (draft)

Author: Nguyen Nam Khoa. Draft for the final report, 11/11/2026, for Lâm to merge into Chapter 3.
Limit for this part: about 120 words and 2 figures. Section and figure numbers (3.x) are fixed by Lâm when merging.

## 3.x Backward chaining and explanations

Backward chaining is goal-driven (Figure 3.x.1). Each fault of the part the rider chooses is
taken as a hypothesis. For every rule that concludes the goal, the premises are proved in turn:
an intermediate fact becomes a new goal, and a symptom is asked once and kept in working
memory. A rule is dropped at its first false premise, so questions that cannot change the result
are never asked. All rules of a goal are tried and combined with the formulas of Section 3.y,
which gives the same CF as forward chaining. For the interface, the engine returns the next
question and resumes with the answer. "Why" shows the chain of rules from the hypothesis down
to the current question (Figure 3.x.2); "how" lists the facts and rules behind a reported fault.

Figure 3.x.1: Backward chaining loop that asks one question at a time.
File: `figures/fig_backward_flow.png` (made by `python src/evaluate.py --charts`).

Figure 3.x.2: Step-by-step screen with the "why" explanation open (scenario BT10, question 8).
File: `figures/fig_backward_screen_why.png` (screenshot of `python src/gui.py`).
