# Chapter 5: Discussion (draft)

Author: Kieu Bao Giang. Draft for the final report, 12/11/2026, for Lâm to merge.
Limit: about 300 words and 1 figure. Numbers: [evaluation_results.md](evaluation_results.md) (Khoa) and
[assistant_results.md](assistant_results.md) (Lâm), knowledge base of 79 rules.

## 5.1 Where the system went wrong

All 30 scenarios now give the expected fault first, with both forward and backward chaining, and
Wang's prover agreed with forward chaining on every scenario and on 500 random sets of answers.
The errors therefore came from the knowledge base, not from the engines. The first run missed two
cases with the same shape: a rule derived an intermediate fact, but every rule going on needed one
more symptom that the rider did not have, so the program stopped with no fault although the cause
was almost known (Figure 5.1.1). A fallback rule with a lower CF from each such fact to its most
common fault (SF14, TS15, BR13 and three engine and transmission rules) fixed both cases; without
them top-1 drops to 28/30. The more specific rules still rank first when the extra symptom is given.

## 5.2 Fewer questions or more accuracy

Backward chaining over every fault asks 39.7 questions per scenario and is right 30/30; choosing
the part first cuts this to 9.0. The assistant reads the rider's own description and then asks only
the most informative questions: 5.8 questions and 27/30 with a Vietnamese description, 6.4 and
28/30 in English. It trades about three misses for seven times fewer questions, because a symptom
the rider never mentions may never be asked. The interface therefore keeps step-by-step questions
as the recommended method and the assistant as the fastest one.

## 5.3 Limitations

The rules are definite clauses, so a "no" answer cannot lower a fault's CF: in ET05 "low coolant"
stays second (CF 0.45) although the rider says the coolant level is fine. The CFs are the authors'
estimates, not measured on repair data, and the scenarios were written by the team rather than
collected from workshops.

## 5.4 Chapter conclusion

The engines are correct with respect to the rules; the remaining errors and trade-offs come from
what the rules and the questions can express. Negative evidence and real repair cases are the next
steps.

## Figure

Figure 5.1.1: A "dead-end" intermediate fact (scenario BT10) and the fallback rule TS15 that fixed it.
File: `figures/fig_dead_end.png` (made by `python src/report_figures.py`).
