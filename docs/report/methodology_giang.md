# Methodology: forward chaining, certainty factors and Wang's check (draft)

Author: Kieu Bao Giang. Draft for the final report, 12/11/2026, for Lâm to merge into Chapter 3.
Limit for this part: about 180 words and 1 figure (PhanCong_Nhom2_12-11_v3). Section and figure numbers (3.y, 3.z) are fixed by Lâm when merging.
Numbers: knowledge base of 79 rules and 40 faults; `python src/wang.py --scenarios --random 500`.

MotoLogic screenshots (not in Chapter 3; for the slides or for Lâm's sections if needed):

Retaken on 12/11 with `python tools/shots.py --lang=vi --mode=light --size=default` (1600×950).

- `figures/fig_motologic_1_setup.png`: step 1, vehicle and the three ways to diagnose.
- `figures/fig_motologic_2_guided.png`: step 2, step-by-step questions on the starting and fuel system.
- `figures/fig_motologic_3_symptoms.png`: step 2, symptom checklist with three symptoms ticked.
- `figures/fig_motologic_4_result.png`: result for SE01: confidence gauge, rule chain SF01 → SF02, SF14 and Wang's check.

`figures/fig_wang_proof.png` (Wang's proof for SE01, 9 sequents) is no longer used in Chapter 3; keep it for the slides.

## 3.y Forward chaining and certainty factors

Forward chaining is data-driven: confirmed symptoms enter an agenda, every rule counts its premises
not yet proved, and a rule whose count reaches zero fires and adds its conclusion to the agenda
(PL-FC-ENTAILS? [Russell and Norvig, ch. 7]), in time linear in the size of the rules.

Faults are ranked with MYCIN-style certainty factors on positive evidence. A rule passes on its own
CF times the minimum CF of its premises; rules with the same conclusion combine as
CF1 + CF2 × (1 − CF1), in dependency order, so an intermediate fact is complete before it is used.
Faults with CF ≥ 0.20 are reported, best first (Figure 3.y.1).

## 3.z Verification with Wang's algorithm

Each rule becomes the formula (p1 ∧ … ∧ pk) → q, each "yes" answer an atom and each "no" answer a
negated atom. Wang's prover decides whether "rules, answers ⇒ fault" is valid, using only the rules
that can conclude the fault. Forward chaining is sound and complete for definite clauses, so with
the threshold at 0 its faults must equal the faults Wang proves; they agree on all 30 scenarios and
500 random answer sets.

## 3.w Chapter conclusion

One knowledge base of 79 rules serves three ways to diagnose: backward chaining with "why" and
"how", forward chaining with certainty factors checked by Wang's prover, and a chat assistant that
asks only the most informative questions. The MotoLogic interface offers all three and always
shows the rules behind an answer.

## Figure

Figure 3.y.1: Forward chaining on scenario SE01 with every CF step: rule SF01, then SF02, SF03 and SF14 combined.
File: `figures/fig_cf_example.png` (made by `python src/report_figures.py`).
