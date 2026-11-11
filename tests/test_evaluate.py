"""Unit tests for src/evaluate.py (owner: Khoa)."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from evaluate import (ALL, GROUPS, Row, evaluate, fallback_rules, format_markdown, format_summary,  # noqa: E402
                      format_table, save_charts, summarise, without_rules)
from forward_chaining import forward_chain  # noqa: E402
from kb import load_kb  # noqa: E402
from scenarios import load_scenarios  # noqa: E402


def row(id, rank, cf=0.8, q_all=40, q_part=10, rank_part=1, rank_plain=1, agree=True):
    return Row(id=id, group=id[:2], expected="f", rank=rank, cf=cf, engines_agree=agree, questions_all=q_all,
               questions_part=q_part, rank_part=rank_part, rank_no_fallback=rank_plain)


class SummaryTest(unittest.TestCase):
    """summarise() on hand-made rows, so the expected numbers are known."""

    def test_counts_and_means(self):
        rows = [row("BT01", 1, cf=0.9, q_all=30, q_part=6), row("BT02", 2, cf=0.5, q_all=50, q_part=10),
                row("SE01", None, cf=0.0, rank_part=None, rank_plain=None, agree=False),
                row("SE02", 4, cf=0.3)]
        by_group = {s.group: s for s in summarise(rows)}
        self.assertEqual(list(by_group), ["SE", "BT", ALL])   # order of GROUPS, then the total
        bt, se, total = by_group["BT"], by_group["SE"], by_group[ALL]
        self.assertEqual((bt.n, bt.top1, bt.top3), (2, 1, 2))
        self.assertEqual((se.n, se.top1, se.top3), (2, 0, 0))  # not found, and rank 4
        self.assertEqual((total.n, total.top1, total.top3), (4, 1, 2))
        self.assertAlmostEqual(bt.questions_all, 40.0)
        self.assertAlmostEqual(bt.questions_part, 8.0)
        self.assertAlmostEqual(bt.mean_cf, 0.7)
        self.assertAlmostEqual(total.top1_pct, 25.0)
        self.assertAlmostEqual(total.top3_pct, 50.0)
        self.assertEqual((total.top1_part, total.top1_no_fallback, total.engines_agree), (3, 3, 3))

    def test_top1_and_top3_of_a_row(self):
        self.assertEqual((row("BT01", 1).top1, row("BT01", 1).top3), (True, True))
        self.assertEqual((row("BT01", 3).top1, row("BT01", 3).top3), (False, True))
        self.assertEqual((row("BT01", None).top1, row("BT01", None).top3), (False, False))


class RealScenariosTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()
        cls.scenarios = load_scenarios()
        cls.rows = evaluate(cls.kb, cls.scenarios)
        cls.summaries = summarise(cls.rows)

    def test_one_row_per_scenario_in_a_known_group(self):
        self.assertEqual([r.id for r in self.rows], [s.id for s in self.scenarios])
        self.assertTrue(all(r.group in GROUPS for r in self.rows))
        self.assertEqual(self.summaries[-1].n, len(self.scenarios))

    def test_rank_matches_forward_chaining(self):
        for s, r in zip(self.scenarios, self.rows):
            ranked = [d.fault for d in forward_chain(self.kb, s.symptoms).diagnoses]
            self.assertEqual(r.rank, ranked.index(s.expected) + 1 if s.expected in ranked else None, s.id)

    def test_backward_agrees_with_forward_on_every_scenario(self):
        self.assertEqual([r.id for r in self.rows if not r.engines_agree], [])

    def test_checking_one_part_asks_fewer_questions_and_finds_the_same_fault(self):
        for r in self.rows:
            self.assertLess(r.questions_part, r.questions_all, r.id)
            self.assertLessEqual(r.questions_all, len(self.kb.symptoms), r.id)
            self.assertEqual(r.rank_part, r.rank, r.id)

    def test_bt10_is_solved_by_ts15(self):
        bt10 = next(r for r in self.rows if r.id == "BT10")
        self.assertEqual(bt10.rank, 1)
        self.assertIsNone(bt10.rank_no_fallback)             # without TS15 the fault is not found
        self.assertIn("TS15", fallback_rules(self.kb))

    def test_fallback_rules_never_hurt(self):
        for r in self.rows:
            if r.rank_no_fallback == 1:
                self.assertEqual(r.rank, 1, r.id)

    def test_without_rules_leaves_the_original_alone(self):
        n = len(self.kb.rules)
        smaller = without_rules(self.kb, ["TS15", "BR13"])
        self.assertEqual(len(smaller.rules), n - 2)
        self.assertEqual(len(self.kb.rules), n)
        self.assertEqual(smaller.rules_concluding("worn_rear_shock"),
                         [r for r in self.kb.rules_concluding("worn_rear_shock") if r.id != "TS15"])

    def test_text_output(self):
        self.assertEqual(len(format_table(self.rows)), len(self.rows) + 1)
        self.assertEqual(len(format_summary(self.summaries)), len(self.summaries) + 1)
        markdown = format_markdown(self.kb, self.rows, self.summaries)
        for s in self.scenarios:
            self.assertIn(f"| {s.id} |", markdown)
        self.assertIn("**All**", markdown)

    def test_charts_are_saved(self):
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            self.skipTest("matplotlib is not installed")
        with tempfile.TemporaryDirectory() as folder:
            paths = save_charts(self.kb, self.rows, Path(folder))
            self.assertEqual([p.name for p in paths], ["fig_accuracy_by_group.png", "fig_backward_questions.png",
                                                       "fig_backward_flow.png"])
            for p in paths:
                self.assertGreater(p.stat().st_size, 5000)


if __name__ == "__main__":
    unittest.main()
