"""Tests for Lâm's interface code: present.py, cli.py, theme.py and the GUI shell."""

import io
import sys
import types
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import theme  # noqa: E402
from cli import format_result, main as cli_main  # noqa: E402
from forward_chaining import forward_chain  # noqa: E402
from kb import load_kb  # noqa: E402
from present import cf_bar, how_rows, near_misses, short  # noqa: E402

BATTERY = ["is_scooter", "starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"]
BT10 = ["is_manual", "rear_shock_bouncy", "sits_low_parked"]


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
        self.assertEqual([r.is_rule for r in rows].count(False), 3)

    def test_near_misses_name_the_missing_symptoms(self):
        result = forward_chain(self.kb, BT10)
        if result.diagnoses:
            self.skipTest("a rule now carries this case to a fault")
        misses = near_misses(self.kb, result.wm)
        self.assertEqual(misses[0].symbol, "suspension_damping_lost")
        missing = {s for _, s in misses[0].missing}
        self.assertIn("tyre_wear_uneven", missing)
        self.assertNotIn("is_manual", missing)

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
        result = forward_chain(self.kb, BT10)
        if result.diagnoses:
            self.skipTest("a rule now carries this case to a fault")
        lines = format_result(self.kb, result, "vi", 0.2, "-")
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


class GuiShellTest(unittest.TestCase):
    """Builds the window once; skipped where there is no display."""

    def setUp(self):
        try:
            import tkinter as tk
            self.root = tk.Tk()
        except Exception as e:  # no display (e.g. a CI server)
            self.skipTest(f"no display: {e}")
        self.root.withdraw()
        self.errors = []
        self.root.report_callback_exception = lambda *a: self.errors.append(a)

    def tearDown(self):
        self.root.destroy()
        for name in ("gui_forward", "gui_backward"):
            sys.modules.pop(name, None)

    def test_every_screen_builds_in_both_languages(self):
        import gui
        app = gui.App(self.root)
        for lang in ("vi", "en"):
            app.set_lang(lang)
            for key in gui.PAGES:
                app.show(key)
                self.root.update()
        self.assertEqual(self.errors, [])

    def test_missing_screen_file_shows_a_placeholder(self):
        import gui
        sys.modules.pop("gui_forward", None)
        if (ROOT / "src" / "gui_forward.py").exists():
            self.skipTest("gui_forward.py exists now")
        app = gui.App(self.root)
        app.show("forward")
        self.assertIsInstance(app.page, gui.PlaceholderPage)

    def test_teammate_screen_is_plugged_in(self):
        import gui
        from gui_widgets import Page

        class ForwardPage(Page):
            def __init__(self, parent, app):
                super().__init__(parent, app)
                self.shown = 0

            def on_show(self):
                self.shown += 1

        fake = types.ModuleType("gui_forward")
        fake.ForwardPage = ForwardPage
        sys.modules["gui_forward"] = fake
        app = gui.App(self.root)
        app.show("forward")
        app.show("kb")
        app.show("forward")
        self.assertIsInstance(app.page, ForwardPage)
        self.assertEqual(app.page.shown, 2)  # built once, shown twice

    def test_fold_ignores_vietnamese_accents(self):
        from gui_widgets import fold
        self.assertEqual(fold("Đèn Phanh"), "den phanh")


if __name__ == "__main__":
    unittest.main()
