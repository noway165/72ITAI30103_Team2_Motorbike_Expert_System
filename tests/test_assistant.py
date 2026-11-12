"""Tests for the diagnosis assistant: nlu.py, interview.py, gui_assistant.py and the dark theme."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import theme  # noqa: E402
from interview import EXCLUSIVE, Interview, derivations, hypotheses, simulate  # noqa: E402
from kb import load_kb  # noqa: E402
from nlu import PHRASES, answers, extract, fold  # noqa: E402


class NluTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def test_every_symptom_has_phrases_and_no_unknown_ids(self):
        self.assertEqual(set(PHRASES), set(self.kb.symptoms))

    def test_vietnamese_with_words_in_between(self):
        a = answers("Sáng nay đề chỉ nghe tạch tạch, còi cũng yếu", self.kb.symptoms)
        self.assertEqual(a, {"starter_clicks_or_silent": True, "horn_weak": True})

    def test_english(self):
        a = answers("The starter only clicks and the horn is weak", self.kb.symptoms)
        self.assertTrue(a["starter_clicks_or_silent"])
        self.assertTrue(a["horn_weak"])

    def test_negation(self):
        a = answers("Xe không có khói đen nhưng hao xăng", self.kb.symptoms)
        self.assertFalse(a["black_exhaust_smoke"])
        self.assertTrue(a["fuel_consumption_increased"])

    def test_negation_does_not_cross_a_comma(self):
        a = answers("đề không nổ, còi yếu", self.kb.symptoms)
        self.assertTrue(a["horn_weak"])

    def test_longer_overlapping_phrase_wins(self):
        a = answers("Wave bình xăng con", self.kb.symptoms)  # not "xăng còn" (fuel left)
        self.assertNotIn("fuel_level_ok", a)
        self.assertTrue(a["is_carburetor"])

    def test_offsets_point_into_the_original_text(self):
        text = "Còi cũng yếu lắm"
        m = extract(text, self.kb.symptoms)[0]
        self.assertEqual(text[m.start:m.end], "Còi cũng yếu")

    def test_fold_keeps_length(self):
        s = "Đề không nổ, còi yếu"
        self.assertEqual(len(fold(s)), len(s))
        self.assertEqual(fold(s), "de khong no, coi yeu")


class InterviewTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def test_derivations_unfold_intermediates(self):
        sets = [d[0] for d in derivations(self.kb, "weak_battery")]
        self.assertIn(frozenset({"starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"}), sets)
        self.assertIn(frozenset({"starter_clicks_or_silent", "horn_weak"}), sets)  # SF14

    def test_every_fault_has_a_hypothesis(self):
        faults = {h.fault for h in hypotheses(self.kb)}
        self.assertTrue(set(self.kb.faults) <= faults)

    def test_yes_to_one_answer_excludes_the_others(self):
        iv = Interview(self.kb, {"horn_weak": True})
        self.assertFalse(iv.answers["horn_normal"])
        self.assertFalse(iv.answers["horn_silent"])
        self.assertTrue(all(len(g) >= 2 for g in EXCLUSIVE))

    def test_question_comes_from_a_likely_fault_and_has_gain(self):
        iv = Interview(self.kb, {"starter_clicks_or_silent": True, "horn_weak": True, "is_scooter": True})
        q = iv.next_question()
        if q is not None:  # SF14 may already prove weak battery strongly enough to stop
            self.assertGreater(q.gain, 0)
            self.assertNotIn(q.symptom, iv.answers)

    def test_dont_know_is_not_asked_again(self):
        iv = Interview(self.kb, {"brake_lever_spongy": True})
        q = iv.next_question()
        iv.answer(q.symptom, None)
        q2 = iv.next_question()
        self.assertTrue(q2 is None or q2.symptom != q.symptom)

    def test_simulated_rider_reaches_the_expected_fault(self):
        truth = ["is_scooter", "is_fuel_injected", "starter_clicks_or_silent", "horn_weak",
                 "battery_older_than_2_years"]
        iv, n = simulate(self.kb, truth, answers("Vision đề chỉ nghe tạch tạch, còi yếu", self.kb.symptoms))
        self.assertEqual(iv.result().diagnoses[0].fault, "weak_battery")
        self.assertLessEqual(n, 3)


class AssistantScreenTest(unittest.TestCase):
    """Builds the assistant and every screen in the dark theme; skipped without a display."""

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
        theme.set_mode("light")
        self.root.destroy()

    def test_conversation_ends_with_a_result(self):
        import gui
        app = gui.App(self.root)
        app.show("assistant")
        page = app.page
        page.use_example("Sáng nay xe Vision đề chỉ nghe tạch tạch, còi cũng yếu")
        for _ in range(15):
            if page.question is None:
                break
            page.answer(page.question.symptom == "battery_older_than_2_years")
        self.assertIsNone(page.question)
        self.assertEqual(page.iv.result().diagnoses[0].fault, "weak_battery")
        self.assertEqual(self.errors, [])

    def test_dark_theme_builds_every_screen_and_keeps_the_conversation(self):
        import gui
        app = gui.App(self.root)
        app.show("assistant")  # the MotoLogic Diagnosis screen opens first now
        app.page.use_example("Còi yếu, đề chỉ nghe tạch tạch")
        app.set_mode("dark")
        self.assertEqual(theme.MODE, "dark")
        self.assertEqual(theme.COLORS["bg"], theme.DARK["bg"])
        self.assertTrue(app.page.matches)  # rebuilt with the same text
        for key in gui.PAGES:
            app.show(key)
            self.root.update()
        app.set_mode("light")
        self.assertEqual(theme.COLORS["bg"], theme.LIGHT["bg"])
        self.assertEqual(self.errors, [])

    def test_palettes_have_the_same_keys(self):
        self.assertEqual(set(theme.DARK), set(theme.LIGHT))


if __name__ == "__main__":
    unittest.main()
