"""Evaluation of the diagnosis assistant (owner: Lâm).

Uses the 30 scenarios in scenarios/. Each has a description written in plain
Vietnamese and English by a team member, the symptoms that are true, and the
expected fault, so it can test the whole pipeline:

1. Understanding: symptoms read from the description vs the scenario's symptoms.
   SE and ET descriptions were used while writing nlu.py (development set).
   BT descriptions were held out for the first version, then used for error
   analysis (12/11), so they are no longer a test set.
   HO descriptions (tests/data/heldout_descriptions.json, 10 brake / tyre /
   suspension cases) were written before reading nlu.py and never used to
   change it: they are the test set now.
2. Adaptive interview: every question is answered from the scenario's symptoms.
   Compared with the team's backward chaining, asking about every fault and
   asking only the faults of the right subsystem.

Run from the repository root:
    python src/evaluate_assistant.py            # print the tables
    python src/evaluate_assistant.py --write    # also write docs/report/assistant_results.md
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

from backward_chaining import backward_chain
from interview import simulate
from kb import ROOT, load_kb
from nlu import answers, extract
from scenarios import load_scenarios

DEV, ANALYSED, HELD_OUT, MODELS = ("SE", "ET"), ("BT",), ("HO",), ("MS",)
HELD_OUT_DIR = Path(ROOT) / "tests" / "data"


def understanding(kb, scenarios, prefixes, lang: str) -> Dict[str, float]:
    tp = fp = fn = 0
    for sc in scenarios:
        if not sc.id.startswith(prefixes):
            continue
        got = {m.symptom for m in extract(sc.description.get(lang, ""), kb.symptoms) if m.value}
        exp = set(sc.symptoms)
        tp, fp, fn = tp + len(got & exp), fp + len(got - exp), fn + len(exp - got)
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return {"precision": p, "recall": r, "f1": 2 * p * r / (p + r) if p + r else 0.0}


def interviews(kb, scenarios) -> List[dict]:
    rows = []
    for sc in scenarios:
        top = lambda iv: [d.fault for d in iv.result().diagnoses][:1] == [sc.expected]  # noqa: E731
        cold, q_cold = simulate(kb, sc.symptoms)
        warm_vi, q_vi = simulate(kb, sc.symptoms, answers(sc.description["vi"], kb.symptoms))
        warm_en, q_en = simulate(kb, sc.symptoms, answers(sc.description["en"], kb.symptoms))
        sub = kb.symbols[sc.expected].subsystem
        goals = [f for f, s in kb.faults.items() if s.subsystem == sub]
        rows.append({
            "id": sc.id, "expected": sc.expected,
            "cold_q": q_cold, "cold_ok": top(cold),
            "vi_q": q_vi, "vi_ok": top(warm_vi), "en_q": q_en, "en_ok": top(warm_en),
            "bw_all": backward_chain(kb, sc.symptoms).questions_asked,
            "bw_sub": backward_chain(kb, sc.symptoms, goals=goals).questions_asked,
            "bw_ok": [d.fault for d in backward_chain(kb, sc.symptoms).diagnoses][:1] == [sc.expected],
        })
    return rows


def held_out(kb, scenarios) -> List[dict]:
    """The assistant on the held-out descriptions: questions and top-1 per language."""
    rows = []
    for sc in scenarios:
        row = {"id": sc.id}
        for lang in ("vi", "en"):
            iv, q = simulate(kb, sc.symptoms, answers(sc.description[lang], kb.symptoms))
            row[lang + "_q"], row[lang + "_ok"] = q, [d.fault for d in iv.result().diagnoses][:1] == [sc.expected]
        rows.append(row)
    return rows


def model_rows(kb, scenarios) -> List[dict]:
    """Bike-model scenarios (MS): each engine with the model, and forward chaining without it."""
    from forward_chaining import forward_chain
    from wang import entails
    rows = []
    for sc in scenarios:
        top = lambda ds: [d.fault for d in ds][:1] == [sc.expected]  # noqa: E731
        plain = [s for s in sc.symptoms if s not in kb.models]
        row = {"fw": top(forward_chain(kb, sc.symptoms).diagnoses), "fw_plain": top(forward_chain(kb, plain).diagnoses),
               "bw": top(backward_chain(kb, sc.symptoms).diagnoses), "wang": entails(kb, sc.symptoms, sc.expected).valid}
        for lang in ("vi", "en"):
            iv, q = simulate(kb, sc.symptoms, answers(sc.description[lang], kb.symptoms))
            row[lang + "_q"], row[lang + "_ok"] = q, top(iv.result().diagnoses)
        rows.append(row)
    return rows


def report(kb, scenarios, heldout=()) -> str:
    out = ["# Diagnosis assistant: results", "",
           f"Knowledge base: {kb.summary()}. {len(scenarios)} scenarios, "
           f"{sum(s.id.startswith(HELD_OUT) for s in heldout)} held-out descriptions, "
           f"{sum(s.id.startswith(MODELS) for s in heldout)} bike-model scenarios. "
           "Produced by `python src/evaluate_assistant.py --write`.", "",
           "## 1. Understanding the rider's description", "",
           "| Descriptions | Language | Precision | Recall | F1 |", "|---|---|---|---|---|"]
    for name, pool, pre in (("SE + ET (development)", scenarios, DEV),
                            ("BT (used for error analysis on 12/11)", scenarios, ANALYSED),
                            ("HO (held-out: never used to change nlu.py)", heldout, HELD_OUT)):
        for lang in ("vi", "en"):
            u = understanding(kb, pool, pre, lang)
            out.append(f"| {name} | {lang} | {u['precision']:.2f} | {u['recall']:.2f} | {u['f1']:.2f} |")
    rows = interviews(kb, scenarios)
    n = len(rows)
    avg = lambda k: sum(r[k] for r in rows) / n  # noqa: E731
    ok = lambda k: sum(r[k] for r in rows)  # noqa: E731
    out += ["", "## 2. Questions asked and accuracy", "",
            "| Method | Average questions | Top-1 correct |", "|---|---|---|",
            f"| Backward chaining, every fault | {avg('bw_all'):.1f} | {ok('bw_ok')}/{n} |",
            f"| Backward chaining, right subsystem chosen by the rider | {avg('bw_sub'):.1f} | – |",
            f"| Assistant, no description (information gain only) | {avg('cold_q'):.1f} | {ok('cold_ok')}/{n} |",
            f"| Assistant, Vietnamese description + information gain | {avg('vi_q'):.1f} | {ok('vi_ok')}/{n} |",
            f"| Assistant, English description + information gain | {avg('en_q'):.1f} | {ok('en_ok')}/{n} |",
            "", "Questions asked by the assistant do not count what was read from the description. "
            "All 30 scenario descriptions have now been used while writing nlu.py, so the held-out set below "
            "is the fair estimate.",
            "", "## 3. Per scenario", "",
            "| Id | Expected fault | Backward (all / right part) | No text | VI text | EN text |", "|---|---|---|---|---|---|"]
    for r in rows:
        mark = lambda b: "✓" if b else "✕"  # noqa: E731
        out.append(f"| {r['id']} | {r['expected']} | {r['bw_all']} / {r['bw_sub']} | {r['cold_q']} {mark(r['cold_ok'])} "
                   f"| {r['vi_q']} {mark(r['vi_ok'])} | {r['en_q']} {mark(r['en_ok'])} |")
    ms = [s for s in heldout if s.id.startswith(MODELS)]
    heldout = [s for s in heldout if s.id.startswith(HELD_OUT)]
    if heldout:
        ho = held_out(kb, heldout)
        m = len(ho)
        out += ["", "## 4. Held-out descriptions (HO)", "",
                "| Language | Average questions | Top-1 correct |", "|---|---|---|"]
        for lang, name in (("vi", "Vietnamese"), ("en", "English")):
            out.append(f"| {name} | {sum(r[lang + '_q'] for r in ho) / m:.1f} | "
                       f"{sum(r[lang + '_ok'] for r in ho)}/{m} |")
    if ms:
        rows, n = model_rows(kb, ms), len(ms)
        ok = lambda k: f"{sum(r[k] for r in rows)}/{n}"  # noqa: E731
        out += ["", "## 5. Bike-model scenarios (MS, tests/data/model_scenarios.json)", "",
                "One scenario per model rule MD01-MD09, written by the author of the rules.", "",
                "| Method | Top-1 correct | Average questions |", "|---|---|---|",
                f"| Forward chaining, bike model given | {ok('fw')} | – |",
                f"| Forward chaining, bike model left out | {ok('fw_plain')} | – |",
                f"| Backward chaining | {ok('bw')} | – |",
                f"| Wang's algorithm proves the expected fault | {ok('wang')} | – |",
                f"| Assistant, Vietnamese description | {ok('vi_ok')} | {sum(r['vi_q'] for r in rows) / n:.1f} |",
                f"| Assistant, English description | {ok('en_ok')} | {sum(r['en_q'] for r in rows) / n:.1f} |"]
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Evaluate the diagnosis assistant on the scenarios.")
    ap.add_argument("--write", action="store_true", help="write docs/report/assistant_results.md")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    kb = load_kb()
    text = report(kb, load_scenarios(), load_scenarios(HELD_OUT_DIR))
    print(text)
    if args.write:
        path = Path(ROOT) / "docs" / "report" / "assistant_results.md"
        path.write_text(text, encoding="utf-8")
        print(f"Written: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
