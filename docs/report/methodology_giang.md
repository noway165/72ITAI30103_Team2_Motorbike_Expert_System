# Methodology: forward chaining, certainty factors and Wang's check (draft)

Author: Kieu Bao Giang. Draft for the final report, 12/11/2026, for Lâm to merge into Chapter 3.
Limit for this part: about 250 words and 3 figures. Section and figure numbers (3.y, 3.z) are fixed by Lâm when merging.
Numbers: knowledge base of 79 rules and 40 faults; `python src/wang.py --scenarios --random 500`.

## 3.y Forward chaining and certainty factors

Forward chaining is data-driven. The symptoms the rider confirms enter working memory and an
agenda. Every rule counts its premises not yet known to be true; when the count reaches zero the
rule fires and its conclusion joins the agenda (PL-FC-ENTAILS? [Russell and Norvig, ch. 7]).
Each symbol is processed once, so a diagnosis takes time linear in the size of the rules.

Faults are ranked with MYCIN-style certainty factors on positive evidence only. The premises of a
rule take their minimum CF, the rule multiplies it by its own CF, and rules with the same
conclusion are combined as CF1 + CF2 × (1 − CF1). CFs are computed after the rules have fired, in
dependency order, so an intermediate fact is combined before it is used. Faults with CF ≥ 0.20
are reported, best first (Figure 3.y.1). The MotoLogic result screen shows the top fault on a CF
gauge, with the chain of rules that produced it (Figure 3.y.2).

## 3.z Verification with Wang's algorithm

Each rule becomes the formula (p1 ∧ … ∧ pk) → q, each "yes" answer an atom and each "no" answer a
negated atom, and the prover decides whether "rules, answers ⇒ fault" is valid (Figure 3.z.1).
Only the rules that can conclude the fault are included, which keeps a proof to a few sequents.
Forward chaining is sound and complete for definite clauses, so the faults it derives (with the
threshold set to 0) must equal the faults Wang proves; any difference reveals a bug.

## 3.w Chapter conclusion

One knowledge base of 79 rules feeds two inference engines that share one CF model, a
conversational assistant and an independent proof check. The MotoLogic interface lets the rider
choose any of the three ways to diagnose and always shows the rules behind the answer. Chapter 4
measures how well these methods work.

## Figures

Figure 3.y.1: Forward chaining on scenario SE01 with every CF step: rule SF01, then SF02, SF03 and SF14 combined.
File: `figures/fig_cf_example.png` (made by `python src/report_figures.py`).

Figure 3.y.2: MotoLogic result screen for SE01: CF gauge, rule chain SF01 → SF02, SF14 and Wang's check.
File: `figures/fig_motologic_4_result.png`.

Figure 3.z.1: Wang's proof that the rules and the three answers of SE01 entail "weak battery" (9 sequents).
File: `figures/fig_wang_proof.png` (made by `python src/report_figures.py`).

Other MotoLogic screens, if Lâm needs them for the interface section:
`figures/fig_motologic_1_setup.png` (step 1), `fig_motologic_2_guided.png` (step 2, question with "why"),
`fig_motologic_3_symptoms.png` (step 2, symptom checklist).
