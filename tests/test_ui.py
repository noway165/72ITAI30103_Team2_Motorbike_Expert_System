"""Tests for the user interface code: present.py, cli.py, theme.py and a GUI smoke test."""

import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import theme  # noqa: E402
from backward_chaining import backward_chain  # noqa: E402
from cli import format_result, main as cli_main  # noqa: E402
from forward_chaining import forward_chain  # noqa: E402
from kb import load_kb  # noqa: E402
from present import (backward_step, cf_bar, how_rows, inference_graph, near_misses,  # noqa: E402
                     short, short_trace, why_rows)
from wang import entails  # noqa: E402

BATTERY = ["is_scooter", "starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"]


class PresentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def test_short_removes_question_mark(self):
        self.assertFalse(short(self.kb, "horn_weak").endswith("?"))

    def test_how_rows_skip_vehicle_type_and_end_with_the_fault(self):
        result = forward_chain(self.kb, BATTERY)
        rows = how_rows(self.kb, result.wm, "weak_battery")
        texts = " ".join(r.text for r in rows)
        self.assertNotIn(short(self.kb, "is_scooter"), texts)
        self.assertTrue(rows[-1].is_rule)
        self.assertIn("SF02", rows[-1].label)
        self.assertEqual([r.is_rule for r in rows].count(False), 3)

    def test_near_misses_name_the_missing_symptoms(self):
        # scenario BT10: the intermediate is reached but no fault (until rule TS15 is added)
        result = forward_chain(self.kb, ["is_manual", "rear_shock_bouncy", "sits_low_parked"])
        misses = near_misses(self.kb, result.wm)
        if result.diagnoses:
            self.skipTest("a rule now carries this case to a fault")
        self.assertEqual(misses[0].symbol, "suspension_damping_lost")
        missing = {s for _, s in misses[0].missing}
        self.assertIn("tyre_wear_uneven", missing)
        self.assertNotIn("is_manual", missing)

    def test_backward_step_replays_to_the_same_result(self):
        brakes = sorted(f for f, s in self.kb.faults.items() if s.subsystem == "brakes")
        truth = {"brake_lever_spongy", "brake_fluid_leak_visible", "brake_fluid_low"}
        answers = {}
        for _ in range(60):
            step = backward_step(self.kb, answers, brakes)
            if not step.question:
                break
            answers[step.question] = step.question in truth
        self.assertFalse(step.question)
        expected = backward_chain(self.kb, {s: True for s in truth if s in answers}, goals=brakes)
        self.assertEqual([(d.fault, d.cf) for d in step.result.diagnoses],
                         [(d.fault, d.cf) for d in expected.diagnoses])

    def test_backward_step_undo_asks_the_same_question_again(self):
        first = backward_step(self.kb, {})
        second = backward_step(self.kb, {first.question: False})
        self.assertNotEqual(first.question, second.question)
        self.assertEqual(backward_step(self.kb, {}).question, first.question)

    def test_why_rows_follow_the_chain(self):
        step = backward_step(self.kb, {})
        rows = why_rows(self.kb, step.chain)
        self.assertEqual(rows[0].rule, step.chain[-1].rule.id)  # innermost first

    def test_inference_graph_columns(self):
        result = forward_chain(self.kb, BATTERY)
        nodes, edges = inference_graph(self.kb, result.wm, "weak_battery")
        col = {n.symbol: n.column for n in nodes}
        self.assertEqual(col["horn_weak"], 0)
        self.assertEqual(col["low_electrical_power"], 1)
        self.assertEqual(col["weak_battery"], 2)
        self.assertIn(("low_electrical_power", "weak_battery"), {(e.source, e.target) for e in edges})
        self.assertEqual(inference_graph(self.kb, result.wm, "out_of_fuel"), ([], []))

    def test_short_trace_uses_rule_ids(self):
        proof = entails(self.kb, BATTERY, "weak_battery", trace=True)
        lines = short_trace(self.kb, proof.trace)
        self.assertTrue(proof.valid)
        self.assertIn("SF01", lines[0])
        self.assertNotIn("→ low_electrical_power", lines[0].split("[")[0])

    def test_cf_bar(self):
        self.assertEqual(cf_bar(0.5, 10), "[#####     ]")
        self.assertEqual(cf_bar(1.5, 4), "[####]")


class CliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def run_cli(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            code = cli_main(list(args))
        return code, out.getvalue()

    def test_forward_prints_ranked_fault_and_explanation(self):
        code, out = self.run_cli("forward", *BATTERY)
        self.assertEqual(code, 0)
        self.assertIn(self.kb.text("weak_battery"), out)
        self.assertIn("SF01", out)
        self.assertIn("Tự xử lý được", out)

    def test_backward_with_symptoms_and_english(self):
        code, out = self.run_cli("--lang", "en", "backward", "--subsystem", "starting_fuel",
                                 "--symptoms", *BATTERY)
        self.assertEqual(code, 0)
        self.assertIn(self.kb.text("weak_battery", "en"), out)

    def test_unknown_symptom_is_an_error(self):
        code, out = self.run_cli("forward", "no_such_symptom")
        self.assertEqual(code, 1)
        self.assertIn("Error", out)

    def test_no_fault_shows_what_was_derived(self):
        result = forward_chain(self.kb, ["is_manual", "rear_shock_bouncy", "sits_low_parked"])
        lines = format_result(self.kb, result, "vi", 0.2, "-")
        if result.diagnoses:
            self.skipTest("a rule now carries this case to a fault")
        self.assertTrue(any("TS09" in line for line in lines))


class ThemeTest(unittest.TestCase):
    def test_every_subsystem_has_a_colour_and_a_name(self):
        kb = load_kb()
        subsystems = {s.subsystem for s in kb.symbols.values()} - {"vehicle"}
        self.assertEqual(subsystems, set(theme.SUBSYSTEM_ORDER))
        for sub in subsystems:
            self.assertIn(sub, theme.SUBSYSTEM_COLORS)
            for lang in ("vi", "en"):
                self.assertIn(sub, theme.SUBSYSTEM_NAMES[lang])

    def test_colours_are_hex(self):
        for name, value in {**theme.COLORS, **theme.SUBSYSTEM_COLORS}.items():
            self.assertRegex(value, r"^#[0-9A-F]{6}$", name)


class GuiSmokeTest(unittest.TestCase):
    """Builds every screen once; skipped where there is no display."""

    def test_every_page_builds_in_both_languages(self):
        try:
            import tkinter as tk
            root = tk.Tk()
        except Exception as e:  # no display (e.g. a CI server)
            self.skipTest(f"no display: {e}")
        root.withdraw()
        errors = []
        root.report_callback_exception = lambda *a: errors.append(a)
        try:
            import gui
            app = gui.App(root)
            sc = next(s for s in app.scenarios if s.id == "SE01")
            app.load_scenario(sc)
            self.assertTrue(app.state["forward"].diagnoses)
            for lang in ("vi", "en"):
                app.set_lang(lang)
                for key, _, _ in gui.PAGES:
                    app.show(key)
                    root.update()
            back = app.pages["backward"]
            back.answer(True)
            back.undo()
            self.assertEqual(app.state["bw_answers"], {})
        finally:
            root.destroy()
        self.assertEqual(errors, [])

    def test_fold_ignores_vietnamese_accents(self):
        import gui
        self.assertEqual(gui.fold("Đèn Phanh"), "den phanh")


if __name__ == "__main__":
    unittest.main()
