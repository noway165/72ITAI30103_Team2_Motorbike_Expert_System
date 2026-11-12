"""Figures for Giang's parts of the report (Chapter 3 and Chapter 5).

Every number on the figures (rule ids, CFs, the proof) is computed from the knowledge
base, so the figures stay true when the rules change. Run from the repository root:

    python src/report_figures.py        # writes docs/report/figures/fig_*.png
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Tuple

from forward_chaining import forward_chain
from kb import ROOT, KnowledgeBase, load_kb
from wang import entails, rule_formula

FIGURE_DIR = ROOT / "docs" / "report" / "figures"
SE01 = ["starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years", "bike_unused_over_2_weeks"]
SHORT = {  # short labels for the figures
    "starter_clicks_or_silent": "starter only clicks", "horn_weak": "weak horn",
    "battery_older_than_2_years": "battery > 2 years", "bike_unused_over_2_weeks": "unused > 2 weeks",
    "low_electrical_power": "low electrical power", "weak_battery": "weak battery",
    "rear_shock_bouncy": "rear bounces", "sits_low_parked": "sits low", "suspension_damping_lost":
    "damping lost", "tyre_wear_uneven": "uneven tyre wear", "suspension_clunk": "clunk over bumps",
    "worn_rear_shock": "worn rear shock",
}


def _pyplot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import theme
    theme.set_mode("light")  # figures are always on white paper
    theme.apply_matplotlib()
    return plt, theme


def _canvas(plt, w: float, h: float, xmax: float, ymax: float):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    ax.grid(False)
    return fig, ax


def _box(ax, c, x, y, w, h, text, fill=None, edge=None, color=None, bold=False, dashed=False, size=8,
         family=None):
    from matplotlib.patches import FancyBboxPatch
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.2", linewidth=1,
                                facecolor=fill or c["surface"], edgecolor=edge or c["border"],
                                linestyle="--" if dashed else "-"))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=size, color=color or c["text"],
            fontweight="bold" if bold else "normal", family=family)


def _arrow(ax, x1, y1, x2, y2, color, text="", dx=0.0, dy=0.0, dashed=False):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(
        arrowstyle="-|>", color=color, linewidth=1, shrinkA=0, shrinkB=0, linestyle="--" if dashed else "-"))
    if text:
        ax.text((x1 + x2) / 2 + dx, (y1 + y2) / 2 + dy, text, ha="center", va="center", fontsize=7.5,
                color=color, family="Consolas", fontweight="bold")


def figure_cf_example(kb: KnowledgeBase, path: Path) -> Path:
    """Figure 3.y.1: forward chaining on scenario SE01 (plus "unused > 2 weeks") with every CF step."""
    plt, theme = _pyplot()
    c, fw = theme.COLORS, theme.ENGINE_COLORS["forward"]
    result = forward_chain(kb, SE01)
    mid = result.wm.get("low_electrical_power")
    top = next(d for d in result.diagnoses if d.fault == "weak_battery")
    fig, ax = _canvas(plt, 7.2, 3.6, 100, 50)
    ys = [40, 30, 20, 10]
    for y, s in zip(ys, SE01):
        _box(ax, c, 0.5, y, 21, 7, f"{SHORT[s]}\nCF 1.00")
    _box(ax, c, 33, 32, 22, 9, f"{SHORT['low_electrical_power']}\nCF {mid.cf:.2f}", fill=theme.LIGHT["accent_soft"],
         edge=fw, bold=True)
    _arrow(ax, 21.5, 43.5, 33, 37.5, fw, mid.by, dx=0, dy=2.5)
    _arrow(ax, 21.5, 33.5, 33, 35.5, fw)
    contributions = []
    y = 32
    for rid in top.rules:
        rule = kb.rule(rid)
        cf_in = min(result.wm.get(p).cf for p in rule.premises)
        contributions.append(rule.cf * cf_in)
        _arrow(ax, 55, 36.5, 63, y - (len(contributions) - 1) * 10 + 4, fw)
        _box(ax, c, 63, y - (len(contributions) - 1) * 10, 19, 8,
             f"{rid}\n{rule.cf:.2f} × {cf_in:.2f} = {rule.cf * cf_in:.3f}", size=7.5)
    for p in ("battery_older_than_2_years", "bike_unused_over_2_weeks"):
        users = [i for i, rid in enumerate(top.rules) if p in kb.rule(rid).premises]
        for i in users:
            _arrow(ax, 21.5, ys[SE01.index(p)] + 3.5, 63, 32 - i * 10 + 4, c["muted"])
    combined = contributions[0]
    steps = [f"{combined:.3f}"]
    for cf in contributions[1:]:
        combined = combined + cf * (1 - combined)
        steps.append(f"{combined:.3f}")
    _box(ax, c, 84, 17, 15.5, 12, f"{SHORT['weak_battery']}\nCF {top.cf:.2f}", fill=fw, edge=fw,
         color=theme.LIGHT["on_accent"], bold=True)
    for i in range(len(contributions)):
        _arrow(ax, 82, 32 - i * 10 + 4, 84, 23, fw)
    ax.text(0.5, 2.5, "CF of a rule = rule CF × min(CF of its premises);  several rules: CF1 + CF2 × (1 − CF1)  →  "
            + " → ".join(steps), fontsize=7.5, color=c["muted"])
    assert abs(combined - top.cf) < 1e-3, (combined, top.cf)
    return _save(fig, plt, path)


def _proof_tree(kb: KnowledgeBase, answers: List[str], goal: str) -> List[Tuple[int, str, str]]:
    """(depth, right-hand side, rule applied) of each sequent of Wang's proof."""
    proof = entails(kb, answers, goal, trace=True)
    assert proof.valid
    nodes = []
    for line in proof.trace:
        depth = (len(line) - len(line.lstrip(" "))) // 2
        sequent, note = line.strip().rsplit("    [", 1)
        right = sequent.split("⇒", 1)[1].strip()
        for sym, short in SHORT.items():
            right = right.replace(sym, short)
        note = note.rstrip("]")
        if note.startswith("→ on the left: "):  # name the rule instead of printing its formula again
            formula = note[len("→ on the left: "):]
            rid = next(r.id for r in kb.rules if str(rule_formula(r)) == formula)
            note = f"→ on the left: rule {rid}"
        elif note.startswith("axiom"):
            note = "axiom"
        elif note.startswith("∧ on the right"):
            note = "∧ on the right: split"
        nodes.append((depth, right, note))
    return nodes


def figure_wang_proof(kb: KnowledgeBase, path: Path) -> Path:
    """Figure 3.z.1: Wang's proof that the rules and SE01's answers entail weak_battery."""
    plt, theme = _pyplot()
    c, wang = theme.COLORS, theme.ENGINE_COLORS["wang"]
    nodes = _proof_tree(kb, SE01[:3], "weak_battery")
    n = len(nodes)
    fig, ax = _canvas(plt, 7.2, 0.42 * n + 0.8, 100, n * 6 + 6)
    for i, (depth, right, note) in enumerate(nodes):
        y = (n - i) * 6
        x = 1 + depth * 6
        axiom = note == "axiom"
        _box(ax, c, x, y, 75 - x, 4.6, "Γ  ⇒  " + right, size=7,
             fill=theme.LIGHT["ok_soft"] if axiom else c["surface"], edge=theme.LIGHT["ok"] if axiom else wang,
             family="DejaVu Sans")  # Segoe UI has no ⇒ or ∧
        ax.text(77, y + 2.3, note, fontsize=7, va="center", color=theme.LIGHT["ok"] if axiom else wang,
                family="DejaVu Sans")
        if depth:
            parent = max(j for j in range(i) if nodes[j][0] == depth - 1)
            px_, py_ = 1 + (depth - 1) * 6 + 3, (n - parent) * 6
            ax.plot([px_, px_, x], [py_, y + 2.3, y + 2.3], color=c["muted"], linewidth=0.8)
    ax.text(1, 1.5, f"Γ = the rules that can conclude weak battery and the three \"yes\" answers.  "
            f"{n} sequents, every branch ends in an axiom: proved.", fontsize=7.5, color=c["muted"])
    return _save(fig, plt, path)


def figure_dead_end(kb: KnowledgeBase, path: Path) -> Path:
    """Figure 5.1.1: a "dead-end" intermediate fact and the fallback rule that fixed it (scenario BT10)."""
    plt, theme = _pyplot()
    c, fw = theme.COLORS, theme.ENGINE_COLORS["forward"]
    mid = "suspension_damping_lost"
    fault = "worn_rear_shock"
    into = [r for r in kb.rules_concluding(mid) if "rear_shock_bouncy" in r.premises and "sits_low_parked" in r.premises][0]
    outs = [r for r in kb.rules_using(mid) if r.conclusion == fault]
    fallback = [r for r in outs if r.premises == (mid,)]
    needs = [r for r in outs if r.premises != (mid,)]
    fig, ax = _canvas(plt, 7.2, 3.6, 100, 52)
    _box(ax, c, 0.5, 32, 19, 7, "rear bounces\n(rider: yes)")
    _box(ax, c, 0.5, 19, 19, 7, "sits low\n(rider: yes)")
    _box(ax, c, 29, 24, 20, 9, f"{SHORT[mid]}\nCF {into.cf:.2f}", fill=theme.LIGHT["accent_soft"], edge=fw, bold=True)
    _arrow(ax, 19.5, 35.5, 29, 30, fw, into.id, dy=3)
    _arrow(ax, 19.5, 22.5, 29, 27, fw)
    _box(ax, c, 79, 24, 20.5, 9, SHORT[fault], fill=fw, edge=fw, color=theme.LIGHT["on_accent"], bold=True)
    for i, r in enumerate(needs):
        extra = [p for p in r.premises if p != mid][0]
        y = 41 if i == 0 else 9
        _box(ax, c, 54, y, 21, 7, f"needs: {SHORT.get(extra, extra)}\n(rider: unknown)", dashed=True,
             edge=c["muted"], color=c["muted"], size=7)
        _arrow(ax, 49, 31 if i == 0 else 26, 54, y + 3.5, c["muted"], dashed=True)
        _arrow(ax, 75, y + 3.5, 82, 33 if i == 0 else 24, c["muted"], r.id, dx=4.5, dashed=True)
    if fallback:
        r = fallback[0]
        _arrow(ax, 49, 28.5, 79, 28.5, theme.LIGHT["ok"], f"{r.id} fallback\nCF {r.cf:.2f}", dy=3.2)
    ax.text(0.5, 1, "Without the fallback rule the program stopped at the intermediate fact: every rule going "
            "on needed a\nsymptom the rider did not have, so no fault was reported although the cause was "
            "almost known.", fontsize=7.5, color=c["muted"])
    return _save(fig, plt, path)


def _save(fig, plt, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> int:
    kb = load_kb()
    for p in (figure_cf_example(kb, FIGURE_DIR / "fig_cf_example.png"),
              figure_wang_proof(kb, FIGURE_DIR / "fig_wang_proof.png"),
              figure_dead_end(kb, FIGURE_DIR / "fig_dead_end.png")):
        print(p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
