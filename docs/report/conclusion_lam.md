# Conclusion

Author: Tang Thoai Lam. Final draft, 12/11/2026. Chapter 6, about 120 words.

## Chapter 6: Conclusion

### 6.1 Summary and future work

We built a rule-based expert system that diagnoses 40 common motorbike faults with 88 rules, plus owner's-manual specs for six popular models. Both chaining directions rank the expected fault first in all 30 test scenarios, and Wang's algorithm agrees with forward chaining. Choosing the subsystem first cuts backward chaining from 39.7 to 9.0 questions, and the rule-based chat keeps every reply traceable to the rules. Its weak point is language: on ten held-out descriptions it found the right fault in 8 (Vietnamese) and 7 (English). Next come phrases from real repair logs, negative evidence and CFs measured on real cases.

### 6.2 Chapter conclusion

Rules that explain themselves make a useful first diagnosis for riders.
