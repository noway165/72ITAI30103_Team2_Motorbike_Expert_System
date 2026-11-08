"""Command-line interface (owner: Lâm). Output format: docs/ui_guide.md, "CLI".

Run from the repository root:
    python src/cli.py forward                      # pick symptoms from a numbered list
    python src/cli.py forward horn_weak starter_clicks_or_silent battery_older_than_2_years
    python src/cli.py backward                     # yes / no questions, type "why" at any question
    python src/cli.py backward --subsystem brakes
    python src/cli.py backward --symptoms brake_lever_spongy brake_fluid_below_min
    python src/cli.py list symptoms | faults
Add --lang en for English.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from backward_chaining import BackwardChainer, backward_chain, make_console_asker
from forward_chaining import DEFAULT_THRESHOLD, forward_chain
from kb import KnowledgeBase, load_kb
from present import cf_bar, how_rows, near_misses, short, t
from theme import MAX_RESULTS, SEVERITY_TEXT, SUBSYSTEM_NAMES, SUBSYSTEM_ORDER

LINE = "-" * 64


def format_result(kb: KnowledgeBase, result, lang: str, threshold: float, header: str) -> List[str]:
    """Ranked faults (or what was derived when there is none), in the same order as the GUI."""
    out = [f"{t('results', lang)}  ({header})", LINE]
    if not result.diagnoses:
        out.append(t("no_fault", lang, t=threshold))
        misses = near_misses(kb, result.wm)
        if not misses:
            out.append(t("nothing_derived", lang))
            return out
        out.append(t("derived", lang))
        for m in misses:
            out.append(f"  {m.rule:<8} {short(kb, m.symbol, lang)}  {m.cf:.2f}")
        missing = [s for miss in misses for _, s in miss.missing]
        if missing:
            out.append(t("check_more", lang))
            out += [f"  - {kb.question(s, lang)}" for s in dict.fromkeys(missing)]
        return out

    for i, d in enumerate(result.diagnoses[:MAX_RESULTS], 1):
        severity = SEVERITY_TEXT[lang].get(d.severity or "self", "")
        out.append(f"{i}. {kb.text(d.fault, lang)}")
        out.append(f"   {t('confidence', lang)} {d.cf:.2f}  {cf_bar(d.cf)}  {severity}")
        out.append(f"   {t('action', lang)}: {kb.action(d.fault, lang)}")
        out.append(f"   {t('why_result', lang)}")
        for row in how_rows(kb, result.wm, d.fault, lang):
            out.append(f"     {row.label:<9} {row.text:<46} {row.cf:.2f}")
        out.append("")
    return out


def print_result(kb: KnowledgeBase, result, lang: str, threshold: float, header: str) -> None:
    print()
    print("\n".join(format_result(kb, result, lang, threshold, header)))


def choose_symptoms(kb: KnowledgeBase, lang: str) -> List[str]:
    """Numbered list of symptoms grouped by subsystem; the rider types the numbers."""
    numbered: List[str] = []
    for sub in ["vehicle"] + SUBSYSTEM_ORDER:
        ids = sorted(s for s, sym in kb.symptoms.items() if sym.subsystem == sub)
        if not ids:
            continue
        print(f"\n== {SUBSYSTEM_NAMES[lang].get(sub, sub)} ==")
        for sid in ids:
            numbered.append(sid)
            print(f"  {len(numbered):>3}. {kb.question(sid, lang)}")
    prompt = ("\nNhập số các triệu chứng đúng với xe, cách nhau bằng dấu cách: " if lang == "vi"
              else "\nType the numbers of the symptoms that are true, separated by spaces: ")
    while True:
        raw = input(prompt).replace(",", " ").split()
        try:
            picks = [numbered[int(x) - 1] for x in raw if 0 < int(x) <= len(numbered)]
        except ValueError:
            picks = []
        if picks:
            return list(dict.fromkeys(picks))
        print("Chưa chọn được triệu chứng nào." if lang == "vi" else "No symptom selected.")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Motorbike fault diagnosis expert system.")
    parser.add_argument("--lang", choices=("vi", "en"), default="vi")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD)
    sub = parser.add_subparsers(dest="mode", required=True)

    fwd = sub.add_parser("forward", help="give the symptoms, get ranked faults")
    fwd.add_argument("symptoms", nargs="*", help="symptom ids; none = choose from a list")

    bwd = sub.add_parser("backward", help="answer yes / no questions")
    bwd.add_argument("--subsystem", choices=SUBSYSTEM_ORDER, help="only check faults of this part")
    bwd.add_argument("--symptoms", nargs="*", default=None,
                     help="answer without asking: these symptoms are true, all others false")

    lst = sub.add_parser("list", help="list symptoms or faults")
    lst.add_argument("what", choices=("symptoms", "faults"))

    args = parser.parse_args(argv)
    try:  # Vietnamese text on older Windows consoles
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    kb = load_kb()
    lang = args.lang
    try:
        if args.mode == "list":
            table = kb.symptoms if args.what == "symptoms" else kb.faults
            for sid, sym in sorted(table.items(), key=lambda kv: (kv[1].subsystem, kv[0])):
                print(f"[{sym.subsystem}] {sid:34} {kb.text(sid, lang)}")
            return 0

        if args.mode == "forward":
            symptoms = args.symptoms or choose_symptoms(kb, lang)
            result = forward_chain(kb, symptoms, threshold=args.threshold)
            fired = ", ".join(r.id for r in result.fired) or "-"
            print_result(kb, result, lang, args.threshold,
                         f"{t('rules_fired', lang, n=result.rules_fired)}: {fired}")
            return 0

        goals = None
        if args.subsystem:
            goals = sorted(f for f, sym in kb.faults.items() if sym.subsystem == args.subsystem)
        if args.symptoms is not None:
            result = backward_chain(kb, args.symptoms, goals=goals, threshold=args.threshold)
        else:
            chainer = BackwardChainer(kb, make_console_asker(kb, lang))
            result = chainer.diagnose(goals=goals, threshold=args.threshold)
        print_result(kb, result, lang, args.threshold,
                     t("questions", lang, q=result.questions_asked, r=result.rules_tried))
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except (EOFError, KeyboardInterrupt):
        print("\nĐã dừng." if lang == "vi" else "\nStopped.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
