# Chapter 4: Experiments and Results (draft)

Author: Nguyen Nam Khoa. Draft for the final report, 11/11/2026.
Limit: about 200 words and 2 charts. Every number comes from `python src/evaluate.py`
(full tables: [evaluation_results.md](evaluation_results.md)); knowledge base of 11/11/2026:
73 symptoms, 9 intermediate facts, 40 faults, 79 rules.

## 4.1 Experimental setup

The system was tested on 30 scenarios, ten for each pair of subsystems. A scenario lists the
symptoms a rider reports and the fault a mechanic would expect; each was written by a team
member who did not write the rules under test. For every scenario, forward chaining runs on the
symptoms, and backward chaining is answered "yes" for those symptoms and "no" for all others.

## 4.2 Results

| Scenario group | Top-1 | Top-3 | Questions, all parts | Questions, correct part |
|---|---|---|---|---|
| Starting, fuel, electrics | 10/10 | 10/10 | 41.5 | 9.0 |
| Engine, transmission | 10/10 | 10/10 | 38.6 | 9.6 |
| Brakes, tyres, suspension | 10/10 | 10/10 | 39.1 | 8.3 |
| All | 30/30 | 30/30 | 39.7 | 9.0 |

Table 4.2.1: Accuracy of the diagnosis and mean number of questions asked by backward chaining.

The expected fault is ranked first in all 30 scenarios (Figure 4.2.1). Without the four fallback
rules that lead from an intermediate fact straight to a fault, two scenarios (SE10, BT10) end
with no diagnosis, and top-1 accuracy is 28/30 (93.3%). Backward chaining returns the same
faults and CFs as forward chaining in every scenario. Checking every part, it asks 39.7 of the
73 questions on average; when the rider first names the correct part it asks 9.0, about 4.4 times
fewer, with the same result (Figure 4.2.2).

Figure 4.2.1: Top-1 accuracy by scenario group, with and without the fallback rules.
File: `figures/fig_accuracy_by_group.png`.

Figure 4.2.2: Mean number of questions asked by backward chaining, all parts and correct part only.
File: `figures/fig_backward_questions.png`.

## 4.3 Chapter conclusion

Both engines agree and find the expected fault in all 30 scenarios, and choosing the part first
makes the dialogue about four times shorter. Two fallback rules (SF14, TS15) were added after
the failures they fix were analysed, and the scenarios are few, so 100% is an optimistic estimate
for real riders.
