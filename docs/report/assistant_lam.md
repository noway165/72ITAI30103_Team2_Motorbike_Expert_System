# Diagnosis assistant (draft)

Author: Tang Thoai Lam. Draft for the final report, 12/11/2026. Methods go into Chapter 3, the table into Chapter 4.
Numbers come from `python src/evaluate_assistant.py --write` ([assistant_results.md](assistant_results.md)).

## 3.x Conversational diagnosis assistant

Riders describe a fault in their own words, not as a list of symptom codes. The assistant adds two steps in front of the rule base.

**Reading the description.** Each of the 73 symptoms has a list of short Vietnamese and English phrases, including Southern words such as "thắng" for brake. The text and the phrases are compared without accents, word by word, allowing up to two extra words inside a phrase ("còi cũng yếu"). A negation word just before a phrase turns the answer into "no", and when two matches overlap the longer one is kept, so "bình xăng con" (carburettor) is not read as "xăng còn" (fuel left). The method needs no internet or model files, so it runs inside the executable.

**Choosing questions.** Every fault is unfolded through the rules into the sets of symptoms that prove it, each weighted by the CF of its chain. The assistant keeps a probability for each set, assuming a rider misses a true symptom with probability 0.05 and reports an unrelated one with probability 0.1. At each step it asks the unanswered symptom with the largest expected information gain over the faults, and it stops once the most likely fault is proved by forward chaining and holds at least 70% of the probability. The final ranking, the how explanation and the Wang check come from the existing engines.

## 4.x Results

| Method | Average questions | Top-1 correct |
|---|---|---|
| Backward chaining, every fault | 39.7 | 30/30 |
| Assistant, Vietnamese description | 5.8 | 27/30 |
| Assistant, English description | 6.4 | 28/30 |

Reading the descriptions reached F1 0.96 on the SE and ET scenarios, which were used while writing the phrases, and 0.79 (Vietnamese) and 0.76 (English) on the BT scenarios, which were not. The assistant asks about seven times fewer questions than backward chaining but misses two or three scenarios, mostly brake and tyre faults with a single symptom that the description did not mention. Backward chaining asks about every fault and therefore never misses one that the rules can prove.
