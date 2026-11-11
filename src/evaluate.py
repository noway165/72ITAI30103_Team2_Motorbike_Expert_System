"""Evaluation on the test scenarios, and the charts of the report (owner: Khoa).

For every scenario in scenarios/ (30 riders' situations with the fault a mechanic expects):
    - forward chaining on the symptoms: is the expected fault ranked 1st (top-1), in the first 3 (top-3)?
    - backward chaining answering "yes" to the scenario's symptoms and "no" to everything else:
        * same faults and CF as forward chaining?
        * how many questions when every part is checked (all 40 faults are hypotheses)?
        * how many questions when only the part of the expected fault is checked?
    - the same top-1 without the fallback rules (single-premise rules from an intermediate
      to a fault), to measure what those rules add.

Run from the repository root:
    python src/evaluate.py                 # table of every scenario and the summary
    python src/evaluate.py --charts        # also save the two charts of Chapter 4 and the flow figure
    python src/evaluate.py --markdown      # also write docs/report/evaluation_results.md
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from backward_chaining import backward_chain
from forward_chaining import forward_chain
from kb import ROOT, KnowledgeBase, load_kb
from scenarios import Scenario, check_scenarios, load_scenarios

FIGURE_DIR = ROOT / "docs" / "report" / "figures"
RESULTS_FILE = ROOT / "docs" / "report" / "evaluation_results.md"

# Scenario groups: the prefix of the scenario id (see scenarios/README.md).
GROUPS = {
    "SE": "Starting, fuel,\nelectrics",
    "ET": "Engine,\ntransmission",
    "BT": "Brakes, tyres,\nsuspension",
}
ALL = "All"


@dataclass
class Row:
    """What happened on one scenario."""

    id: str
    group: str
    expected: str
    rank: Optional[int]           # rank of the expected fault in forward chaining (1 = first); None = not found
    cf: float                     # CF of the expected fault (0.0 if not found)
    engines_agree: bool           # backward chaining gives the same faults and CF as forward chaining
    questions_all: int            # backward chaining, every part
    questions_part: int           # backward chaining, only the part of the expected fault
    rank_part: Optional[int]      # rank of the expected fault when only that part is checked
    rank_no_fallback: Optional[int]  # rank in forward chaining without the fallback rules

    @property
    def top1(self) -> bool:
        return self.rank == 1

    @property
    def top3(self) -> bool:
        return self.rank is not None and self.rank <= 3


@dataclass
class Summary:
    group: str
    n: int
    top1: int
    top3: int
    top1_part: int
    top1_no_fallback: int
    engines_agree: int
    questions_all: float          # mean
    questions_part: float         # mean
    mean_cf: float                # mean CF of the expected fault

    @property
    def top1_pct(self) -> float:
        return 100.0 * self.top1 / self.n

    @property
    def top3_pct(self) -> float:
        return 100.0 * self.top3 / self.n


def fallback_rules(kb: KnowledgeBase) -> List[str]:
    """Ids of the rules "IF one intermediate THEN fault": they keep an intermediate from being a dead end."""
    return [r.id for r in kb.rules
            if len(r.premises) == 1 and r.premises[0] in kb.intermediates and kb.is_fault(r.conclusion)]


def without_rules(kb: KnowledgeBase, rule_ids: Iterable[str]) -> KnowledgeBase:
    """A copy of the knowledge base without the given rules."""
    drop = set(rule_ids)
    return KnowledgeBase(kb.symbols, [r for r in kb.rules if r.id not in drop], list(kb.problems))


def _rank(faults: List[str], expected: str) -> Optional[int]:
    return faults.index(expected) + 1 if expected in faults else None


def evaluate(kb: KnowledgeBase, scenarios: List[Scenario]) -> List[Row]:
    """Run both engines on every scenario."""
    plain = without_rules(kb, fallback_rules(kb))
    rows = []
    for s in scenarios:
        forward = forward_chain(kb, s.symptoms)
        backward = backward_chain(kb, s.symptoms)
        part = [f for f, sym in sorted(kb.faults.items()) if sym.subsystem == kb.symbols[s.expected].subsystem]
        backward_part = backward_chain(kb, s.symptoms, goals=part)
        ranked = [d.fault for d in forward.diagnoses]
        cf = next((d.cf for d in forward.diagnoses if d.fault == s.expected), 0.0)
        agree = ([(d.fault, round(d.cf, 3)) for d in forward.diagnoses]
                 == [(d.fault, round(d.cf, 3)) for d in backward.diagnoses])
        rows.append(Row(
            id=s.id, group=s.id[:2], expected=s.expected, rank=_rank(ranked, s.expected), cf=cf,
            engines_agree=agree, questions_all=backward.questions_asked,
            questions_part=backward_part.questions_asked,
            rank_part=_rank([d.fault for d in backward_part.diagnoses], s.expected),
            rank_no_fallback=_rank([d.fault for d in forward_chain(plain, s.symptoms).diagnoses], s.expected)))
    return rows


def summarise(rows: List[Row]) -> List[Summary]:
    """One Summary per scenario group (in the order of GROUPS), then one for all scenarios."""
    groups = [g for g in GROUPS if any(r.group == g for r in rows)]
    groups += sorted({r.group for r in rows} - set(GROUPS))
    out = []
    for name, chosen in [(g, [r for r in rows if r.group == g]) for g in groups] + [(ALL, rows)]:
        n = len(chosen)
        if not n:
            continue
        out.append(Summary(
            group=name, n=n, top1=sum(r.top1 for r in chosen), top3=sum(r.top3 for r in chosen),
            top1_part=sum(r.rank_part == 1 for r in chosen),
            top1_no_fallback=sum(r.rank_no_fallback == 1 for r in chosen),
            engines_agree=sum(r.engines_agree for r in chosen),
            questions_all=sum(r.questions_all for r in chosen) / n,
            questions_part=sum(r.questions_part for r in chosen) / n,
            mean_cf=sum(r.cf for r in chosen) / n))
    return out


# ---------------------------------------------------------------------------
# Text output
# ---------------------------------------------------------------------------

def format_table(rows: List[Row]) -> List[str]:
    lines = [f"{'id':6}{'expected':34}{'rank':>5}{'CF':>6}  {'FC=BC':6}{'questions: all':>15}{'part':>6}"
             f"{'rank w/o fallback':>19}"]
    for r in rows:
        lines.append(f"{r.id:6}{r.expected:34}{r.rank or '-':>5}{r.cf:>6.2f}  "
                     f"{'yes' if r.engines_agree else 'NO':6}{r.questions_all:>15}{r.questions_part:>6}"
                     f"{r.rank_no_fallback or '-':>19}")
    return lines


def format_summary(summaries: List[Summary]) -> List[str]:
    lines = [f"{'group':7}{'n':>4}{'top-1':>8}{'top-3':>8}{'top-1 (part only)':>19}{'top-1 w/o fallback':>20}"
             f"{'FC=BC':>7}{'questions: all':>16}{'part':>7}{'mean CF':>9}"]
    for s in summaries:
        lines.append(f"{s.group:7}{s.n:>4}{s.top1:>8}{s.top3:>8}{s.top1_part:>19}{s.top1_no_fallback:>20}"
                     f"{s.engines_agree:>7}{s.questions_all:>16.1f}{s.questions_part:>7.1f}{s.mean_cf:>9.2f}")
    return lines


def format_markdown(kb: KnowledgeBase, rows: List[Row], summaries: List[Summary]) -> str:
    """The numbers of Chapter 4 as Markdown tables (docs/report/evaluation_results.md)."""
    total = summaries[-1]
    names = {g: label.replace("\n", " ") for g, label in GROUPS.items()}
    out = [
        "# Evaluation results",
        "",
        "Written by `python src/evaluate.py --markdown`; do not edit by hand.",
        "",
        f"Knowledge base: {kb.summary()}. Fallback rules: {', '.join(fallback_rules(kb))}.",
        "",
        "## Summary by scenario group",
        "",
        "| Group | Scenarios | Top-1 | Top-3 | Top-1, correct part only | Top-1 without fallback rules "
        "| Mean CF of expected fault | Questions, all parts | Questions, correct part |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for s in summaries:
        name = f"**{s.group}**" if s.group == ALL else f"{names.get(s.group, s.group)} ({s.group})"
        out.append(f"| {name} | {s.n} | {s.top1} ({s.top1_pct:.1f}%) | {s.top3} ({s.top3_pct:.1f}%) | "
                   f"{s.top1_part} | {s.top1_no_fallback} | {s.mean_cf:.2f} | {s.questions_all:.1f} | "
                   f"{s.questions_part:.1f} |")
    ratio = total.questions_all / total.questions_part if total.questions_part else 0.0
    out += [
        "",
        f"- Backward chaining gives the same faults and CF as forward chaining on "
        f"{total.engines_agree}/{total.n} scenarios.",
        f"- Checking only the correct part needs {ratio:.1f} times fewer questions "
        f"({total.questions_part:.1f} instead of {total.questions_all:.1f}; the knowledge base has "
        f"{len(kb.symptoms)} symptoms).",
        f"- Without the fallback rules, top-1 is {total.top1_no_fallback}/{total.n}; with them, "
        f"{total.top1}/{total.n}.",
        "",
        "## Every scenario",
        "",
        "| Scenario | Expected fault | Rank | CF | Questions, all parts | Questions, correct part "
        "| Rank without fallback rules |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        out.append(f"| {r.id} | `{r.expected}` | {r.rank or 'not found'} | {r.cf:.2f} | {r.questions_all} | "
                   f"{r.questions_part} | {r.rank_no_fallback or 'not found'} |")
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# Charts (docs/ui_guide.md, section 6)
# ---------------------------------------------------------------------------

def _pyplot():
    import matplotlib
    matplotlib.use("Agg")  # draw to files; no window needed
    import matplotlib.pyplot as plt

    import theme
    theme.apply_matplotlib()
    return plt, theme


def _group_labels(summaries: List[Summary]) -> List[str]:
    return [f"{GROUPS.get(s.group, s.group)}\n(n = {s.n})" if s.group != ALL else f"All scenarios\n(n = {s.n})"
            for s in summaries]


def chart_accuracy(summaries: List[Summary], path: Path) -> Path:
    """Top-1 accuracy by scenario group, with and without the fallback rules."""
    plt, theme = _pyplot()
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    x = range(len(summaries))
    width = 0.36
    before = [100.0 * s.top1_no_fallback / s.n for s in summaries]
    after = [s.top1_pct for s in summaries]
    bars = [ax.bar([i - width / 2 for i in x], before, width, color=theme.COLORS["chrome"],
                   label="Without fallback rules"),
            ax.bar([i + width / 2 for i in x], after, width, color=theme.COLORS["accent"],
                   label="Final knowledge base")]
    counts = [[s.top1_no_fallback for s in summaries], [s.top1 for s in summaries]]
    for group, numbers in zip(bars, counts):
        for bar, k, s in zip(group, numbers, summaries):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f"{k}/{s.n}", ha="center",
                    va="bottom", fontsize=9, color=theme.COLORS["text"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(_group_labels(summaries))
    ax.set_ylim(0, 132)
    ax.set_yticks(range(0, 101, 20))
    ax.set_ylabel("Top-1 accuracy (%)")
    ax.set_title("Expected fault ranked first, by scenario group")
    ax.legend(loc="upper left", ncols=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def chart_questions(summaries: List[Summary], n_symptoms: int, path: Path) -> Path:
    """Mean number of questions of backward chaining: every part against the correct part only."""
    plt, theme = _pyplot()
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    x = range(len(summaries))
    width = 0.36
    series = [([s.questions_all for s in summaries], theme.COLORS["muted"], "All parts (40 hypotheses)"),
              ([s.questions_part for s in summaries], theme.ENGINE_COLORS["backward"], "Correct part only")]
    for k, (values, color, name) in enumerate(series):
        bars = ax.bar([i + (k - 0.5) * width for i in x], values, width, color=color, label=name)
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{v:.1f}", ha="center",
                    va="bottom", fontsize=9, color=theme.COLORS["text"])
    ax.axhline(n_symptoms, color=theme.COLORS["danger"], linewidth=1, linestyle="--")
    ax.text(len(summaries) - 0.5, n_symptoms + 1, f"{n_symptoms} symptoms in the knowledge base", ha="right",
            va="bottom", fontsize=9, color=theme.COLORS["danger"])
    ax.set_xticks(list(x))
    ax.set_xticklabels(_group_labels(summaries))
    ax.set_ylim(0, n_symptoms + 24)
    ax.set_yticks(range(0, n_symptoms + 1, 20))
    ax.set_ylabel("Questions asked (mean)")
    ax.set_title("Questions asked by backward chaining")
    ax.legend(loc="upper left", ncols=2)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def figure_backward_flow(path: Path) -> Path:
    """Flow of the question-by-question backward chaining loop (Chapter 3)."""
    plt, theme = _pyplot()
    from matplotlib.patches import FancyBboxPatch

    c = theme.COLORS
    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)
    ax.axis("off")
    ax.grid(False)

    def box(x, y, w, h, text, fill=c["surface"], edge=c["border"], color=c["text"], bold=False):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.5", linewidth=1,
                                    facecolor=fill, edgecolor=edge))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8, color=color,
                fontweight="bold" if bold else "normal")

    def arrow(x1, y1, x2, y2, text="", dx=0.0, dy=0.0, color=c["muted"]):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", color=color, linewidth=1, shrinkA=0, shrinkB=0))
        if text:
            ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, text, ha="center", va="center", fontsize=8,
                    color=color)

    backward = theme.ENGINE_COLORS["backward"]
    w, h = 30, 10
    left, mid, right = 0.5, 35, 69.5
    top, middle, bottom, out = 49, 32, 15, 0.5
    box(left, top, w, h, "Hypothesis H:\nnext fault to prove", fill=backward, edge=backward,
        color=c["on_accent"], bold=True)
    box(mid, top, w, h, "Next rule R that\nconcludes the goal")
    box(right, top, w, h, "Next premise P of R")
    box(right, middle, w, h, "Is P a symptom?")
    box(mid, middle, w, h, "P is an intermediate:\nP becomes the goal")
    box(right, bottom, w, h, "Ask the rider:\nYes / No / I don't know", fill=c["accent"],
        edge=c["accent"], color=c["on_accent"], bold=True)
    box(mid, bottom, w, h, "No: drop R, next rule\nYes: keep CF(P), next P")
    box(left, middle, w, h, "Every premise true:\nCF = CF(R) × min CF(P)")
    box(left, bottom, w, h, "Every rule of H tried:\nCF1 + CF2 × (1 − CF1)")
    box(left, out, w, 9, "Ranked faults, CF ≥ 0.2,\nwith how explanation", fill=c["accent_soft"],
        edge=c["accent"], bold=True)
    box(right, out, w, 9, "Why: the chain of rules\nfrom H to this question", fill=c["accent_soft"],
        edge=c["accent"], bold=True)

    arrow(left + w, top + h / 2, mid, top + h / 2)
    arrow(mid + w, top + h / 2, right, top + h / 2)
    arrow(right + w / 2, top, right + w / 2, middle + h)
    arrow(right, middle + h / 2, mid + w, middle + h / 2, "no", dy=2.2)
    arrow(mid + w / 2, middle + h, mid + w / 2, top, "recursion", dx=7.5)
    arrow(right + w / 2, middle, right + w / 2, bottom + h, "yes", dx=4)
    arrow(right, bottom + h / 2, mid + w, bottom + h / 2)
    arrow(right + w / 2, bottom, right + w / 2, out + 9, color=c["accent"])
    arrow(mid, bottom + h, left + w, middle, "last P true", dx=8.5, dy=1.2)
    arrow(left + w / 2, middle, left + w / 2, bottom + h)
    arrow(left + w / 2, bottom, left + w / 2, out + 9, "after the last H", dx=10)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def save_charts(kb: KnowledgeBase, rows: List[Row], folder: Path = FIGURE_DIR) -> List[Path]:
    summaries = summarise(rows)
    return [chart_accuracy(summaries, folder / "fig_accuracy_by_group.png"),
            chart_questions(summaries, len(kb.symptoms), folder / "fig_backward_questions.png"),
            figure_backward_flow(folder / "fig_backward_flow.png")]


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate both engines on the test scenarios.")
    parser.add_argument("--charts", action="store_true", help=f"save the charts in {FIGURE_DIR.relative_to(ROOT)}")
    parser.add_argument("--markdown", action="store_true",
                        help=f"write the tables to {RESULTS_FILE.relative_to(ROOT)}")
    args = parser.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

    kb = load_kb()
    scenarios = load_scenarios()
    problems = check_scenarios(kb, scenarios)
    for p in problems:
        print(f"ERROR   {p}")
    if problems:
        return 1

    rows = evaluate(kb, scenarios)
    summaries = summarise(rows)
    print("\n".join(format_table(rows)))
    print()
    print("\n".join(format_summary(summaries)))
    print(f"\nFallback rules: {', '.join(fallback_rules(kb))}")
    if args.markdown:
        RESULTS_FILE.write_text(format_markdown(kb, rows, summaries), encoding="utf-8")
        print(f"Wrote {RESULTS_FILE.relative_to(ROOT)}")
    if args.charts:
        for path in save_charts(kb, rows):
            print(f"Saved {path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
