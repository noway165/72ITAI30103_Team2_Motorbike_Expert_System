# Chapter 4: Experiments and Results

Author: Nguyen Nam Khoa. Final draft for the report, 13/11/2026 (cut from 377 to about 200 words; the
assistant table of Lâm, `assistant_lam.md` section 4.x, is merged into Table 4.2.1).
Numbers: `python src/evaluate.py --charts` and `python src/evaluate_assistant.py`
([evaluation_results.md](evaluation_results.md), [assistant_results.md](assistant_results.md));
knowledge base of 12/11/2026: 73 symptoms, 40 faults, 79 rules.

## 4.1 Experimental setup

The system was tested on 30 scenarios, ten per subsystem group, each written by a member who did not
write the rules under test. Questions are answered "yes" for the scenario's symptoms and "no" otherwise;
the assistant also starts from the scenario's Vietnamese or English description.

## 4.2 Results

| Method | Mean questions | Top-1 correct |
|---|---|---|
| Backward chaining, every part | 39.7 | 30/30 |
| Backward chaining, correct part chosen first | 9.0 | 30/30 |
| Assistant, Vietnamese description | 5.8 | 27/30 |
| Assistant, English description | 6.4 | 28/30 |

Table 4.2.1: Questions asked and top-1 accuracy of each way of asking.

Forward and backward chaining return the same faults and CFs and rank the expected fault first in all
30 scenarios; without the four fallback rules, two scenarios fail (Figure 4.2.1). Choosing the part
first shortens the dialogue 4.4 times, and the assistant asks about seven times fewer questions but
misses two or three brake and suspension faults (Figure 4.2.2).

Figure 4.2.1: Top-1 accuracy by scenario group, with and without the fallback rules.
File: `figures/fig_accuracy_by_group.png`.

Figure 4.2.2: Mean questions asked by backward chaining and by the assistant, by scenario group.
File: `figures/fig_backward_questions.png`.

## 4.3 Chapter conclusion

The rule base finds every expected fault. The assistant trades a few misses for far shorter dialogues;
with only 30 scenarios, 100% is an optimistic estimate for real riders.
