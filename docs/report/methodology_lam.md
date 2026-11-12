# Methodology: knowledge base and interface

Author: Tang Thoai Lam. Final draft, 12/11/2026. First section of Chapter 3; together with `assistant_lam.md` about 180 words and 1 figure.

## 3.a Knowledge base and interface

The knowledge base is one JSON file per subsystem: yes/no questions in Vietnamese and English, faults with a severity and an action, and rules with a CF and a source. Six popular bike models add their own rules and owner's-manual specs. A validator rejects duplicate rules, unused symbols, missing sources and cycles. The MotoLogic interface has three steps: the bike, one of three ways to describe the problem, and the result with its rule chain and Wang's check.
