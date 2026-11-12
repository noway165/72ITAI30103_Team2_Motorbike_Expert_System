# Conclusion

Author: Tang Thoai Lam. Final draft, 12/11/2026. Chapter 6, about 120 words.

## Chapter 6: Conclusion

### 6.1 Summary and future work

We built a rule-based expert system that diagnoses 40 common motorbike faults from 79 symptoms with 88 rules, each with a certainty factor and a source; for six popular models it adds their own rules and owner's-manual specs. Forward and backward chaining rank the expected fault first in all 30 test scenarios, and Wang's algorithm agrees with forward chaining on these and on 500 random answer sets. Choosing the subsystem first cuts backward chaining from 39.7 to 9.0 questions, and the rule-based chat lets riders describe a fault in their own words while every reply stays traceable to the rules. Its weak point is language: on ten held-out descriptions it found the right fault in 8 (Vietnamese) and 7 (English). Next steps are phrases learned from real repair logs, negative evidence in the rules and CFs measured on real cases.

### 6.2 Chapter conclusion

Rules that explain themselves make a useful first diagnosis for riders.
