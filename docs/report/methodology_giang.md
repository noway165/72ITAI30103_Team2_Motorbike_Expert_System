# Methodology: forward chaining, certainty factors and Wang's check (draft)

Author: Kieu Bao Giang. Draft for the final report, 13/11/2026, for Lâm to merge into Chapter 3.
Limit for this part: about 180 words including the Chapter 3 conclusion, and 1 figure (PhanCong_Nhom2_12-11_v4, G1). Section and figure numbers (3.y, 3.z) are fixed by Lâm when merging.
Numbers: knowledge base of 79 symptoms, 40 faults and 88 rules; `python src/wang.py --scenarios --random 500`.

MotoLogic screenshots (not in Chapter 3; for the slides or for Lâm's sections if needed):

Retaken on 13/11 on main (with the bike-model picker) using `python tools/shots.py --lang=vi --mode=light --size=default` (1600×950).

- `figures/fig_motologic_1_setup.png`: step 1, Honda Vision chosen and the three ways to diagnose.
- `figures/fig_motologic_2_guided.png`: step 2, step-by-step questions on the starting and fuel system.
- `figures/fig_motologic_3_symptoms.png`: step 2, symptom checklist with three symptoms ticked.
- `figures/fig_motologic_4_result.png`: result for a weak battery on a Honda Vision: confidence gauge, rule chain, the model's own specs and Wang's check.

`figures/fig_wang_proof.png` (Wang's proof for SE01, 9 sequents) is not used in Chapter 3; keep it for the slides.

## 3.y Forward chaining and certainty factors

Forward chaining is data-driven: confirmed symptoms enter an agenda, each rule counts its unproved
premises, and a rule whose count reaches zero fires and adds its conclusion (PL-FC-ENTAILS?
[Russell and Norvig, ch. 7]). Faults are ranked with MYCIN-style certainty factors: a rule passes on
its CF times the minimum CF of its premises, and rules with the same conclusion combine as
CF1 + CF2 × (1 − CF1). Faults with CF ≥ 0.20 are reported, best first (Figure 3.y.1).

## 3.z Verification with Wang's algorithm

Each rule becomes (p1 ∧ … ∧ pk) → q, each "yes" an atom and each "no" a negated atom.
Wang's prover decides whether "rules, answers ⇒ fault" is valid. Forward chaining is sound and
complete for definite clauses, so at threshold 0 both must find the same faults; they agree on
30 scenarios and 500 random answer sets.

## 3.w Chapter conclusion

One knowledge base of 88 rules, nine of them for six bike models, serves three ways
to diagnose: backward chaining with "why" and "how", forward chaining with certainty factors checked
by Wang's prover, and a rule-based chat. MotoLogic shows the rules behind every answer.

## Figure

Figure 3.y.1: Forward chaining on scenario SE01 with every CF step: rule SF01, then SF02, SF03 and SF14 combined.
File: `figures/fig_cf_example.png` (made by `python src/report_figures.py`).
