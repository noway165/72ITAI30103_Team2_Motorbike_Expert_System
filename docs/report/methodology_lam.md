# Methodology: knowledge base and interface

Author: Tang Thoai Lam. Final draft, 13/11/2026. First section of Chapter 3; three screenshots of MotoLogic (English, light), taken with `python tools/shots.py --lang=en --mode=light --size=default` and cropped to the content area.

## 3.a Knowledge base and interface

The knowledge base is one JSON file per subsystem: yes/no questions in Vietnamese and English, faults with a severity and an action, and rules with a CF and a source. Six popular bike models add their own rules and owner's-manual specs. A validator rejects duplicate rules, unused symbols, missing sources and cycles.

MotoLogic has three steps. The rider picks the bike model and one of three ways to diagnose (Figure 3.a.1); step-by-step questions show the rule each question tests (Figure 3.a.2); the result gives the leading fault with its confidence, rule chain, action, the model's owner's-manual specs and Wang's check (Figure 3.a.3).

Figure 3.a.1: Step 1 of MotoLogic: the bike model and the way to diagnose.
File: `figures/fig_app_setup.png`

Figure 3.a.2: Step-by-step questions: the rule being tested is shown beside the question.
File: `figures/fig_app_guided.png`

Figure 3.a.3: The result for a Honda Vision that only clicks when started.
File: `figures/fig_app_result.png`
