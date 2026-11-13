# Chapter 4: Experiments and Results

Author: Nguyen Nam Khoa. Final draft for the report, 13/11/2026. K2: numbers edited by Lâm (5.5 questions,
held-out 10.8 / 11.5 and 8/10, 7/10, nine bike-model scenarios) checked against the scripts and agreed;
one sentence on flipped answers added (K6, `docs/progress/nguyen_nam_khoa.md` section 6).
Numbers: `python src/evaluate.py --charts` and `python src/evaluate_assistant.py`
([evaluation_results.md](evaluation_results.md), [assistant_results.md](assistant_results.md));
knowledge base of 12/11/2026: 79 symptoms, 40 faults, 88 rules.

## 4.1 Experimental setup

The system was tested on 30 scenarios, ten per subsystem group, each written by a member who did not
write the rules under test. Answers follow the scenario's symptoms; the assistant also starts from the
scenario's description.

## 4.2 Results

| Method | Mean questions | Top-1 correct |
|---|---|---|
| Backward chaining, every part | 39.7 | 30/30 |
| Backward chaining, correct part chosen first | 9.0 | 30/30 |
| Assistant, Vietnamese description | 5.5 | 30/30 |
| Assistant, English description | 5.5 | 30/30 |
| Assistant, 10 held-out descriptions (vi / en) | 10.8 / 11.5 | 8/10 / 7/10 |

Table 4.2.1: Questions asked and top-1 accuracy of each way of asking.

Forward and backward chaining return the same faults and CFs and rank the expected fault first in all
30 scenarios; without the four fallback rules, two scenarios fail (Figure 4.2.1). Choosing the part
first shortens the dialogue 4.4 times. The assistant asks about seven times fewer questions on the
30 scenarios, whose descriptions were all used while writing it; on ten held-out descriptions it
misses two or three brake, fork and steering faults (Figure 4.2.2). With 10% of the answers flipped, top-1 falls
to 76% for backward chaining on the chosen part and 92% for the assistant. Nine scenarios for the bike-model
rules, written by their author, are ranked first by both engines and proved by Wang; without the bike model
only four are ranked first.

Figure 4.2.1: Top-1 accuracy by scenario group, with and without the fallback rules.
File: `figures/fig_accuracy_by_group.png`.

Figure 4.2.2: Mean questions asked by backward chaining and by the assistant, by scenario group.
File: `figures/fig_backward_questions.png`.

## 4.3 Chapter conclusion

The rule base finds every expected fault. The assistant trades a few misses for far shorter dialogues;
with only 30 scenarios, 100% is an optimistic estimate for real riders.
