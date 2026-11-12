# Methodology: knowledge base and interface

Author: Tang Thoai Lam. Final draft, 12/11/2026. First section of Chapter 3; together with `assistant_lam.md` about 180 words and 1 figure.

## 3.a Knowledge base and interface

The knowledge base is one JSON file per subsystem. Each symptom has a yes/no question in Vietnamese and English, each fault a severity and an action, and each rule its premises, one conclusion, a CF and the source it was based on. Six popular models are vehicle facts with their own rules and owner's-manual specs, shown with a matching fault. A validator reports duplicate rules, unused symbols, missing sources and cycles before any engine runs. The MotoLogic interface guides the rider in three steps: the motorbike type, one of three ways to describe the problem, and the result with its rule chain and Wang's check.
