"""Tests for Khoa's "Hỏi đáp từng câu" screen: the logic in gui_backward.py, then the page itself."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from backward_chaining import UNKNOWN, backward_chain  # noqa: E402
from gui_backward import (ALL, KEYS, TEXT, answer_key, goals_for, history, open_hypotheses, outcome,  # noqa: E402
                          question_view, start_session, subsystem_options)
from kb import load_kb  # noqa: E402
from scenarios import load_scenarios  # noqa: E402
from theme import MAX_RESULTS, SUBSYSTEM_ORDER  # noqa: E402

BT10 = ["is_manual", "is_carburetor", "rear_shock_bouncy", "sits_low_parked"]


def run(kb, yes, subsystem=ALL):
    """Answer every question: yes for the symptoms in `yes`, no for the rest."""
    session = start_session(kb, subsystem)
    while not session.finished:
        session.answer(session.question.symptom in yes)
    return session


class BackwardLogicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def test_both_languages_have_the_same_wording_keys(self):
        self.assertEqual(set(TEXT["vi"]), set(TEXT["en"]))

    def test_subsystem_options(self):
        for lang in ("vi", "en"):
            options = subsystem_options(self.kb, lang)
            self.assertEqual([key for key, _, _ in options], [ALL] + SUBSYSTEM_ORDER)
            self.assertEqual(options[0][2], len(self.kb.faults))
            self.assertEqual(sum(n for _, _, n in options[1:]), len(self.kb.faults))

    def test_goals_for(self):
        self.assertEqual(goals_for(self.kb, ALL), sorted(self.kb.faults))
        brakes = goals_for(self.kb, "brakes")
        self.assertIn("worn_brake_pads", brakes)
        self.assertTrue(all(self.kb.symbols[f].subsystem == "brakes" for f in brakes))

    def test_first_question_view(self):
        session = start_session(self.kb, "tyres_suspension")
        q = question_view(self.kb, session, "vi")
        self.assertEqual(q.number, 1)
        self.assertEqual(q.text, self.kb.question(q.symptom, "vi"))
        self.assertEqual(q.total, len(goals_for(self.kb, "tyres_suspension")))
        self.assertEqual(len(q.open), q.total)              # nothing ruled out yet
        self.assertTrue(q.goal)
        self.assertIn("asking", [state for _, state in q.why[0].premises])   # innermost rule first
        self.assertEqual(question_view(self.kb, session, "en").text, self.kb.question(q.symptom, "en"))

    def test_why_marks_premises_already_answered_yes(self):
        session = start_session(self.kb, "tyres_suspension")
        while session.question.symptom != "sits_low_parked":
            session.answer(session.question.symptom == "rear_shock_bouncy")
        q = question_view(self.kb, session, "vi")
        ts09 = q.why[0]
        self.assertEqual(ts09.rule, "TS09")
        self.assertEqual([state for _, state in ts09.premises], ["yes", "asking"])
        self.assertEqual(q.why[-1].conclusion, q.goal)       # the outermost rule concludes the hypothesis

    def test_open_hypotheses_only_shrink(self):
        session = start_session(self.kb, "brakes")
        before = len(open_hypotheses(self.kb, session))
        while not session.finished:
            session.answer(False)
            now = len(open_hypotheses(self.kb, session))
            self.assertLessEqual(now, before)
            before = now
        self.assertEqual(open_hypotheses(self.kb, session), [])

    def test_history_is_newest_first(self):
        session = start_session(self.kb, "brakes")
        first = session.question.symptom
        session.answer(True)
        session.answer(False)
        session.answer(UNKNOWN)
        rows = history(self.kb, session, "vi")
        self.assertEqual([key for _, key in rows], ["unknown", "no", "yes"])
        self.assertEqual(rows[-1][0], self.kb.text(first, "vi").rstrip(" ?"))
        self.assertEqual([answer_key(v) for v in (True, 0.6, False, UNKNOWN)], ["yes", "yes", "no", "unknown"])

    def test_outcome_of_bt10(self):
        session = start_session(self.kb, "tyres_suspension")
        self.assertIsNone(outcome(self.kb, session))         # questions are left
        session = run(self.kb, BT10, "tyres_suspension")
        o = outcome(self.kb, session, "vi")
        self.assertEqual(o.cards[0].fault, "worn_rear_shock")
        self.assertEqual(o.cards[0].name, self.kb.text("worn_rear_shock", "vi"))
        self.assertEqual(o.cards[0].action, self.kb.action("worn_rear_shock", "vi"))
        self.assertEqual([r.label for r in o.cards[0].how if r.is_rule], ["TS09", "TS15"])
        self.assertEqual(o.questions, session.result.questions_asked)
        self.assertEqual((o.unknown, o.near), ([], []))

    def test_outcome_with_no_fault_and_unknown_answers(self):
        session = start_session(self.kb, "brakes")
        session.answer(UNKNOWN)
        while not session.finished:
            session.answer(False)
        o = outcome(self.kb, session, "en")
        self.assertEqual(o.cards, [])
        self.assertEqual(len(o.unknown), 1)

    def test_at_most_max_results_cards(self):
        session = run(self.kb, set(self.kb.symptoms))
        o = outcome(self.kb, session)
        self.assertLessEqual(len(o.cards), MAX_RESULTS)
        self.assertEqual(len(o.cards) + o.hidden, len(session.result.diagnoses))

    def test_every_scenario_gives_the_same_faults_as_the_engine(self):
        for s in load_scenarios():
            with self.subTest(scenario=s.id):
                o = outcome(self.kb, run(self.kb, s.symptoms))
                reference = backward_chain(self.kb, s.symptoms)
                self.assertEqual([c.fault for c in o.cards], [d.fault for d in reference.diagnoses[:MAX_RESULTS]])
                self.assertEqual(o.cards[0].fault, s.expected)

    def test_keys(self):
        self.assertIs(KEYS["c"], True)
        self.assertIs(KEYS["k"], False)
        self.assertIs(KEYS["b"], UNKNOWN)


class BackwardPageTest(unittest.TestCase):
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

    def test_ask_why_answer_and_show_result(self):
        import gui
        from gui_backward import BackwardPage
        app = gui.App(self.root)
        app.show("backward")
        page = app.page
        self.assertIsInstance(page, BackwardPage)
        self.assertIsNone(page.session)
        page.subsystem.set("tyres_suspension")
        page.start()
        self.root.update()
        page.toggle_why()                                  # open "Tại sao hỏi câu này?"
        self.root.update()
        self.assertTrue(page.why_open)
        page.answer(False)
        page.back()                                        # the same question again
        self.assertEqual(page.session.question.number, 1)
        while not page.session.finished:
            page.answer(page.session.question.symptom in BT10)
        self.root.update()
        self.assertEqual(page.session.result.diagnoses[0].fault, "worn_rear_shock")
        self.assertIn("worn_rear_shock", page.open)        # first card opens its explanation
        page.toggle("worn_rear_shock")
        self.assertNotIn("worn_rear_shock", page.open)
        app.set_lang("en")                                 # the diagnosis survives a language change
        self.root.update()
        self.assertTrue(app.page.session.finished)
        self.assertEqual(app.page.session.result.diagnoses[0].fault, "worn_rear_shock")
        app.page.start()                                   # "Hỏi lại"
        self.root.update()
        self.assertEqual(app.page.session.question.number, 1)
        self.assertEqual(self.errors, [])

    def test_keys_and_unknown(self):
        import gui

        class Key:
            def __init__(self, char="", keysym=""):
                self.char, self.keysym = char, keysym

        app = gui.App(self.root)
        app.show("backward")
        page = app.page
        page.on_key(Key(keysym="Return"))                  # Enter starts the diagnosis
        self.assertIsNotNone(page.session)
        page.on_key(Key("?"))
        self.assertTrue(page.why_open)
        page.on_key(Key("c"))
        page.on_key(Key("b"))
        self.assertEqual(len(page.session.answers), 2)
        self.assertEqual(len(page.session.unknown), 1)
        while not page.session.finished:
            page.on_key(Key("k"))
        self.root.update()
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
