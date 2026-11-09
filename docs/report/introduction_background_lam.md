# Introduction and Background (draft)

Author: Tang Thoai Lam. Draft for the final report, 09/11/2026.
Numbers refer to the knowledge base of 09/11/2026 (73 symptoms, 9 intermediate facts, 40 faults, 77 rules).

## 1 Introduction

Viet Nam has about 74 million motorcycles, more than it has adults [WHO 2024]. When one of them breaks down, the rider has to decide what to do with little to go on. A starter that only clicks, together with a weak horn, usually needs no more than a battery charge. Brake fluid leaking from a hose means the motorbike should not be ridden at all. Many common faults can be told apart by things a rider can check without tools, such as the sound of the horn, the colour of the exhaust smoke or the level in the brake fluid window.

This knowledge has the form "if these symptoms appear, suspect this fault", which suits a rule-based expert system. Such a system can also show a rider the rules behind its advice.

We built an expert system for common faults on scooters and manual motorbikes. From the symptoms a rider reports, it ranks the likely faults by certainty factor, says which ones need a mechanic, and gives the action to take. The knowledge base covers six subsystems with 73 symptoms, 9 intermediate facts, 40 faults and 77 rules.

Two inference engines use this knowledge base. Forward chaining starts from the symptoms the rider selects. Backward chaining starts from possible faults and asks yes/no questions. The rider can ask why a question is asked and how a conclusion was reached. Because we wrote the engines ourselves, we compare the faults derived by forward chaining with those proved by an independent theorem prover based on Wang's algorithm. We evaluate the system on 30 scenarios, each written by a team member who did not write the rules for that subsystem. The program runs as a Windows executable in Vietnamese and English.

The system covers only faults with rules in the knowledge base, and its answers do not replace an inspection by a mechanic.

Section 2 gives the background, Section 3 the methods, Section 4 the experiments and results, Section 5 the discussion and Section 6 the conclusion.

## 2 Background

### 2.1 Rule-based expert systems

A rule-based expert system keeps knowledge of a narrow domain as IF ... THEN rules in a knowledge base. An inference engine applies the rules to the facts of the current case, which are held in working memory, so the knowledge can change without changing the program. MYCIN, developed at Stanford in the 1970s to advise on bacterial infections, is the classic example and the source of two techniques we use: certainty factors and why/how explanations [Buchanan and Shortliffe 1984].

### 2.2 Horn clauses, forward and backward chaining

Our rules are definite clauses of propositional logic: a conjunction of positive premises implies one positive conclusion. For such a knowledge base, entailment can be decided in time linear in its size [Russell and Norvig, ch. 7]. Forward chaining is data-driven: it fires every rule whose premises are known and adds the conclusions until nothing new can be derived. It is sound and complete for definite clauses. Backward chaining is goal-driven: it works back from a query through the rules that conclude it, so a diagnosis program can ask the user for one fact at a time.

### 2.3 Certainty factors

Diagnostic rules are rarely certain: a weak horn suggests a weak battery but does not prove it. MYCIN attached to each rule a certainty factor (CF), a number that expresses how strongly the premises support the conclusion [Shortliffe and Buchanan 1975]. CFs are estimates of the strength of evidence and are not probabilities. Our rules use only positive evidence, so we need only the positive part of the model (Section 3).

### 2.4 Explanation

MYCIN answered two kinds of question [Buchanan and Shortliffe 1984]. "Why" asks why the program wants a piece of information, and the answer is the rule it is trying to apply. "How" asks how a conclusion was reached, and the answer is the chain of rules and facts behind it.

### 2.5 Wang's algorithm

Wang's algorithm decides whether a sequent of propositional logic is valid [Wang 1960]. It removes one connective at a time until only atoms remain; a branch closes when the same atom appears on both sides, and the sequent is valid when every branch closes. The question "do the rules and the rider's answers entail this fault?" can be written as a sequent. The algorithm shares no code with our inference engines, so it can reveal engine bugs such as a rule that fires when a premise is missing.

### 2.6 Related work

Aditya et al. [2022] built a mobile application that uses forward chaining to diagnose damage on automatic motorcycles and checked it with black-box testing. Anggrawan et al. [2026] compared certainty factors with case-based reasoning and reported accuracies of 98% and up to 100%. Our project uses forward and backward chaining on the same knowledge base, adds why/how explanations, and checks the derived faults with a separate theorem prover.

## References

- Aditya, M. N., Delimayanti, M. K., Musyono, A. D. N. I., Kriswanto, Naryanto, R. F., and Sukoco, I. (2022). Development of a mobile expert system for the diagnosis on motorcycle damage using forward chaining algorithm. Indonesian Journal of Electrical Engineering and Computer Science, 27(3), 1601-1609. https://doi.org/10.11591/ijeecs.v27.i3.pp1601-1609
- Anggrawan, A., Satria, C., Triwijoyo, B. K., Priyanto, D., Hasbullah, H., and Rebecca, V. C. (2026). Expert system for motorcycle damage diagnosis using certainty factor and case-based reasoning methods. International Journal of Informatics and Communication Technology, 15(4), 1829-1840. https://doi.org/10.11591/ijict.v15i4.pp1829-1840
- Buchanan, B. G., and Shortliffe, E. H. (Eds.) (1984). Rule-Based Expert Systems: The MYCIN Experiments of the Stanford Heuristic Programming Project. Addison-Wesley.
- Russell, S., and Norvig, P. (2021). Artificial Intelligence: A Modern Approach (4th ed.). Pearson. Chapter 7, Logical Agents.
- Shortliffe, E. H., and Buchanan, B. G. (1975). A model of inexact reasoning in medicine. Mathematical Biosciences, 23(3-4), 351-379. https://doi.org/10.1016/0025-5564(75)90047-4
- Wang, H. (1960). Toward mechanical mathematics. IBM Journal of Research and Development, 4(1), 2-22.
- World Health Organization (2024, November 25). WHO convenes global motorcycle safety experts in Viet Nam. https://www.who.int/news/item/25-11-2024-who-convenes-global-motorcycle-safety-experts-in-viet-nam
