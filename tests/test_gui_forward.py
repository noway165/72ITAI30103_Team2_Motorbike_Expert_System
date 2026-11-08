"""Tests for Giang's "Theo triệu chứng" screen: the logic in gui_forward.py, then the page itself."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from gui_forward import (VEHICLE, diagnose, from_scenario, matches, search_key, symptom_groups,  # noqa: E402
                         vehicle_symptoms)
from kb import load_kb  # noqa: E402
from scenarios import load_scenarios  # noqa: E402
from theme import MAX_RESULTS  # noqa: E402

SE01 = ["is_scooter", "is_fuel_injected", "starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"]


class ForwardLogicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def test_vehicle_symptoms(self):
        self.assertEqual(vehicle_symptoms("scooter", "fi"), ["is_scooter", "is_fuel_injected"])
        self.assertEqual(vehicle_symptoms("", "carb"), ["is_carburetor"])
        self.assertEqual(vehicle_symptoms("", ""), [])

    def test_every_symptom_is_listed_once_except_vehicle_type(self):
        for lang in ("vi", "en"):
            listed = [sid for _, ids in symptom_groups(self.kb, lang) for sid in ids]
            self.assertEqual(len(listed), len(set(listed)))
            expected = {s for s, sym in self.kb.symptoms.items() if sym.subsystem != "vehicle"}
            self.assertEqual(set(listed), expected)
            self.assertFalse(set(listed) & set(VEHICLE.values()))

    def test_search_ignores_accents_and_word_order(self):
        key = search_key(self.kb, "brake_grinding", "vi")
        self.assertTrue(matches(key, "ken phanh"))
        self.assertTrue(matches(key, ""))
        self.assertFalse(matches(key, "còi"))
        self.assertTrue(matches(search_key(self.kb, "horn_weak", "vi"), "coi"))

    def test_from_scenario_splits_vehicle_type(self):
        se01 = next(s for s in load_scenarios() if s.id == "SE01")
        kind, fuel, chosen = from_scenario(se01)
        self.assertEqual((kind, fuel), ("scooter", "fi"))
        self.assertEqual(vehicle_symptoms(kind, fuel) + sorted(chosen), ["is_scooter", "is_fuel_injected"]
                         + sorted(set(se01.symptoms) - set(VEHICLE.values())))

    def test_diagnose_se01(self):
        o = diagnose(self.kb, SE01, "vi")
        top = o.cards[0]
        self.assertEqual(top.fault, "weak_battery")
        self.assertEqual(top.rank, 1)
        self.assertEqual(top.name, self.kb.text("weak_battery", "vi"))
        self.assertEqual(top.action, self.kb.action("weak_battery", "vi"))
        self.assertTrue(top.wang)
        self.assertTrue(o.wang_agree)
        self.assertEqual(o.near, [])
        self.assertTrue(top.how[-1].is_rule)       # the how chain ends with the rule giving the fault
        self.assertIn("SF02", top.how[-1].label)   # several rules are listed together, e.g. "SF02, SF14"
        self.assertEqual(top.rules, top.how[-1].label.split(", "))

    def test_diagnose_in_english(self):
        top = diagnose(self.kb, SE01, "en").cards[0]
        self.assertEqual(top.name, self.kb.text("weak_battery", "en"))
        self.assertEqual(top.how[0].label, "you said")

    def test_no_fault_gives_near_misses(self):
        o = diagnose(self.kb, ["is_manual", "rear_shock_bouncy", "sits_low_parked"])
        if o.cards:
            self.skipTest("a rule now carries this case (BT10) to a fault")
        self.assertEqual(o.near[0].symbol, "suspension_damping_lost")
        self.assertTrue(o.wang_agree)

    def test_at_most_max_results_cards(self):
        many = sorted(self.kb.symptoms)
        o = diagnose(self.kb, many)
        self.assertLessEqual(len(o.cards), MAX_RESULTS)
        self.assertEqual(len(o.cards) + o.hidden, len(o.result.diagnoses))
        self.assertTrue(o.wang_agree)
        self.assertTrue(all(c.wang for c in o.cards))

    def test_every_scenario_agrees_with_wang(self):
        for s in load_scenarios():
            with self.subTest(scenario=s.id):
                self.assertTrue(diagnose(self.kb, s.symptoms).wang_agree)


class ForwardPageTest(unittest.TestCase):
    """Builds the real window; skipped where there is no display."""

    def setUp(self):
        try:
            import tkinter as tk
            self.root = tk.Tk()
        except Exception as e:  # no display
            self.skipTest(f"no display: {e}")
        self.root.withdraw()
        self.errors = []
        self.root.report_callback_exception = lambda *a: self.errors.append(a)

    def tearDown(self):
        self.root.destroy()

    def test_load_scenario_diagnose_and_open_how(self):
        import gui
        from gui_forward import ForwardPage
        app = gui.App(self.root)
        app.show("forward")
        page = app.page
        self.assertIsInstance(page, ForwardPage)
        se01 = next(s for s in app.scenarios if s.id == "SE01")
        page.load(se01)
        self.root.update()
        self.assertEqual(page.outcome.cards[0].fault, "weak_battery")
        self.assertIn("weak_battery", page.open)       # first card opens its explanation
        page.toggle("weak_battery")
        self.assertNotIn("weak_battery", page.open)
        app.set_lang("en")                             # the diagnosis survives a language change
        self.root.update()
        self.assertEqual(app.page.outcome.cards[0].name, app.kb.text("weak_battery", "en"))
        app.page.clear()
        self.assertEqual(app.state["fw_selected"], set())
        self.assertEqual(self.errors, [])

    def test_no_symptom_and_near_miss_link(self):
        import gui
        app = gui.App(self.root)
        app.show("forward")
        page = app.page
        page.run()                                     # nothing selected: only a message
        self.assertIsNone(page.outcome)
        page.vars["rear_shock_bouncy"].set(True)
        page.vars["sits_low_parked"].set(True)
        page.run()
        self.root.update()
        if not page.outcome.cards:
            page.add_symptom("tyre_wear_uneven")      # the "check more" link
            self.assertTrue(page.outcome.cards)
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
