# Methodology: diagnosis assistant and rule-based chat

Author: Tang Thoai Lam. Final draft, 12/11/2026. Last section of Chapter 3 before the chapter conclusion; together with `methodology_lam.md` about 180 words and 1 figure.
The results table is in Chapter 4 (Table 4.2.1, Khoa); numbers come from `python src/evaluate_assistant.py --write` ([assistant_results.md](assistant_results.md)).

## 3.b Diagnosis assistant and rule-based chat

The third way to diagnose is a chat. A phrase matcher reads symptoms from free Vietnamese or English text, compared without accents and with negation. The assistant then asks the symptom with the largest expected information gain over the faults, using the sets of symptoms that prove each fault through the rules. Every reply is built from the knowledge base: "why?" lists the rules that use the asked symptom with each premise marked, an answer reports the rules that fire or are switched off, and "how?" shows the rule chain (Figure 3.b.1). The final ranking still comes from forward chaining.

Figure 3.b.1: The rule-based chat: the rider answers in words and asks why a question is asked.
File: `figures/fig_motologic_chat.png` (made by `python tools/shots.py`).
