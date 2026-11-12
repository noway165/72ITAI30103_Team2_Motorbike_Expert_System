# Chapter 5: Discussion (draft)

Author: Kieu Bao Giang. Draft for the final report, 12/11/2026, for Lâm to merge.
Limit: at most 300 words and 1 figure. Numbers: [evaluation_results.md](evaluation_results.md) (Khoa),
[assistant_results.md](assistant_results.md) (Lâm) and Khoa's re-run in [nguyen_nam_khoa.md](../progress/nguyen_nam_khoa.md)
section 3 (K3), knowledge base of 79 rules.

## 5.1 Where the system went wrong

All 30 scenarios give the expected fault first with both engines, and Wang's prover agreed with
forward chaining on every scenario and on 500 random answer sets, so the errors came from the
knowledge base. Two cases failed the same way: an intermediate fact was derived, but every rule
going on needed a symptom the rider did not have, so no fault was reported (Figure 5.1.1). A
lower-CF fallback rule from each such fact to its most common fault (for example TS15) fixed both;
without these rules top-1 drops to 28/30.

## 5.2 Fewer questions or more accuracy

Backward chaining over every fault asks 39.7 questions and is right 30/30; choosing the part first
cuts this to 9.0. The assistant asks 5.3 questions and is right 30/30 on descriptions used to write
its phrase list, but 8/10 (Vietnamese) and 7/10 (English) with about 11 questions on ten held-out
ones. The comparison is not equal: the assistant does not count what it reads, stops once the
leading fault is proved and is capped at 15 questions; backward chaining that reads the same
description still asks 36.6, but stopping at the first proved fault gives 22.2 (28/30).
Step-by-step questions therefore stay the recommended method.

## 5.3 Limitations

The rules are definite clauses, so a "no" answer cannot lower a fault's CF: in ET05 "low coolant"
stays second (CF 0.45) although the coolant level is fine. The chat understands only phrasings in
its phrase list: "tay phanh mềm" (soft brake lever) is read, "bóp phanh thấy mềm" is not. The CFs
are the authors' estimates and the scenarios were written by the team.

## 5.4 Chapter conclusion

The engines are correct with respect to the rules; the remaining errors and trade-offs come from
what the rules and the phrase list can express. Negative evidence, a larger phrase list and real
repair cases are the next steps.

## Figure

Figure 5.1.1: A "dead-end" intermediate fact (scenario BT10) and the fallback rule TS15 that fixed it.
File: `figures/fig_dead_end.png` (made by `python src/report_figures.py`).
