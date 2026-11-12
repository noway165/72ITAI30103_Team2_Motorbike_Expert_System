# Chapter 5: Discussion (draft)

Author: Kieu Bao Giang. Draft for the final report, 13/11/2026, for Lâm to merge.
Limit: at most 300 words and 1 figure. Numbers: [evaluation_results.md](evaluation_results.md) (Khoa),
[assistant_results.md](assistant_results.md) (Lâm), knowledge base of 88 rules. The fair comparison in 5.2
(36.3 questions when backward chaining reads the same description; 22.2 and 28/30 when it stops at the first
proved fault; 7/30 assistant runs reach the 15-question cap) was re-measured by Giang on main on 13/11 with
the same simulation as Khoa's section 3 in [nguyen_nam_khoa.md](../progress/nguyen_nam_khoa.md). Replace
it with Khoa's K4 numbers if they differ.

## 5.1 Where the system went wrong

All 30 scenarios rank the expected fault first with both engines, and Wang's prover agrees with
forward chaining on every scenario and 500 random answer sets, so the errors came from the
knowledge base. Two cases failed the same way: an intermediate fact was derived, but every rule
going on needed a symptom the rider did not have (Figure 5.1.1). A lower-CF fallback rule to the
most common fault (for example TS15) fixed both; without these rules top-1 drops to 28/30.

## 5.2 Fewer questions or more accuracy

Backward chaining over every fault asks 39.7 questions and is right 30/30; choosing the part first
cuts this to 9.0. The assistant asks 5.5 questions and is right 30/30 on descriptions used to write
its phrase list, but 8/10 (Vietnamese) and 7/10 (English) with about 11 questions on ten held-out
ones. The comparison is not equal: the assistant does not count what it reads, stops once the
leading fault is proved and is capped at 15 questions (reached in 7/30). Reading the same
description, backward chaining still asks 36.3; stopping at the first proved fault gives 22.2
(28/30). Most of the gap comes from stopping early; step-by-step questions stay recommended.

## 5.3 Limitations

The rules are definite clauses, so a "no" answer cannot lower a fault's CF: in ET05 "low coolant"
stays second (CF 0.45) although the coolant is fine. The chat understands only phrasings in
its phrase list: "tay phanh mềm" (soft brake lever) is read, "bóp phanh thấy mềm" is not. The
bike-model rules rest on weak sources (news articles and repair-shop websites), and the CFs and
scenarios were written by the team.

## 5.4 Chapter conclusion

The engines are correct with respect to the rules; the remaining errors come from what the rules
and the phrase list can express. Negative evidence, a larger phrase list and real repair cases come
next.

## Figure

Figure 5.1.1: A "dead-end" intermediate fact (scenario BT10) and the fallback rule TS15 that fixed it.
File: `figures/fig_dead_end.png` (made by `python src/report_figures.py`).
