"""Tests for Giang's MotoLogic screens: gui_diagnosis.py and gui_history.py (logic, then the window)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import theme  # noqa: E402
from backward_chaining import UNKNOWN  # noqa: E402
from gui_diagnosis import (TEXT, VEHICLE, checklist, guided_session, make_record, new_dx, session_number,  # noqa: E402
                           subsystem_counts, summarize, talk_interview, vehicle_answers, wang_check)
from gui_history import reopen, rows  # noqa: E402
from kb import load_kb  # noqa: E402
from scenarios import load_scenarios  # noqa: E402

KB = load_kb()
SCENARIOS = {s.id: s for s in load_scenarios()}


def dx_for(scenario, method, **kw):
    """A diagnosis set up like step 1 would do it for a scenario."""
    s = set(scenario.symptoms)
    dx = new_dx()
    dx.update(kind="scooter" if "is_scooter" in s else "manual" if "is_manual" in s else "",
              fuel="fi" if "is_fuel_injected" in s else "carb" if "is_carburetor" in s else "",
              method=method, step=2, **kw)
    return dx


def answer_guided(dx, truth):
    """Answer every question of the step-by-step diagnosis from the scenario's symptoms."""
    while True:
        session = guided_session(KB, dx)
        if session.finished:
            return session
        dx["answers"].append((session.question.symptom, session.question.symptom in truth))


def answer_talk(dx, truth):
    while True:
        iv, _ = talk_interview(KB, dx)
        q = iv.next_question()
        if q is None:
            return iv
        dx["replies"].append((q.symptom, q.symptom in truth))


class LogicTest(unittest.TestCase):
    def test_both_languages_have_the_same_wording_keys(self):
        self.assertEqual(set(TEXT["vi"]), set(TEXT["en"]))

    def test_every_talk_example_is_understood(self):
        for lang in ("vi", "en"):
            for sentence in TEXT[lang]["examples"]:
                with self.subTest(lang=lang, sentence=sentence):
                    dx = new_dx()
                    dx.update(method="talk", text=sentence)
                    self.assertTrue(talk_interview(KB, dx)[1])

    def test_vehicle_answers(self):
        self.assertEqual(vehicle_answers("scooter", "fi"), {"is_scooter": True, "is_manual": False,
                                                            "is_fuel_injected": True, "is_carburetor": False})
        self.assertEqual(vehicle_answers("", ""), {})
        self.assertTrue(VEHICLE <= set(KB.symptoms))

    def test_subsystem_counts_cover_every_fault(self):
        self.assertEqual(sum(n for _, n in subsystem_counts(KB)), len(KB.faults))

    def test_checklist_search_and_filter(self):
        groups = checklist(KB, "vi", "coi", "")
        self.assertIn("horn_weak", [s for _, ids in groups for s in ids])
        only = checklist(KB, "vi", "", "brakes")
        self.assertEqual([sub for sub, _ in only], ["brakes"])
        self.assertFalse(VEHICLE & {s for _, ids in checklist(KB, "en") for s in ids})

    def test_se01_by_all_three_methods(self):
        se01 = SCENARIOS["SE01"]
        truth = set(se01.symptoms)
        guided = dx_for(se01, "guided", part="starting_fuel")
        answer_guided(guided, truth)
        symptoms = dx_for(se01, "symptoms", selected=[s for s in se01.symptoms if s not in VEHICLE])
        talk = dx_for(se01, "talk", text="Sáng nay xe Vision đề chỉ nghe tạch tạch, còi cũng yếu")
        answer_talk(talk, truth)
        for i, dx in enumerate((guided, symptoms, talk), 1):
            with self.subTest(method=dx["method"]):
                rec = make_record(KB, dx, i)
                s = summarize(KB, rec, "vi")
                self.assertEqual(s.fault, "weak_battery")
                self.assertEqual(s.name, KB.text("weak_battery", "vi"))
                self.assertTrue(wang_check(KB, rec, s.fault))
                self.assertEqual(s.steps[-1].conclusion, "Ắc quy yếu hoặc hết điện")
                self.assertEqual(s.observations, len([x for x in rec.yes if x not in VEHICLE]))

    def test_bt03_needs_a_mechanic(self):
        bt03 = SCENARIOS["BT03"]
        for dx in (dx_for(bt03, "guided", part="brakes"),
                   dx_for(bt03, "symptoms", selected=[s for s in bt03.symptoms if s not in VEHICLE])):
            if dx["method"] == "guided":
                answer_guided(dx, set(bt03.symptoms))
            s = summarize(KB, make_record(KB, dx, 1), "en")
            with self.subTest(method=dx["method"]):
                self.assertEqual(s.fault, "brake_fluid_leak")
                self.assertEqual(s.severity, "mechanic")

    def test_unknown_answer_and_undo_keep_the_session(self):
        dx = dx_for(SCENARIOS["SE01"], "guided", part="starting_fuel")
        first = guided_session(KB, dx).question.symptom
        dx["answers"].append((first, UNKNOWN))
        self.assertNotEqual(guided_session(KB, dx).question.symptom, first)
        dx["answers"].pop()
        self.assertEqual(guided_session(KB, dx).question.symptom, first)

    def test_no_fault_shows_near_misses(self):
        dx = dx_for(SCENARIOS["SE01"], "symptoms", selected=["rear_shock_bouncy", "sits_low_parked"])
        s = summarize(KB, make_record(KB, dx, 1), "vi")
        if s.fault:
            self.skipTest("a rule now carries this case to a fault")
        self.assertTrue(s.near)

    def test_every_scenario_by_symptoms_gives_its_expected_fault(self):
        for sc in SCENARIOS.values():
            dx = dx_for(sc, "symptoms", selected=[s for s in sc.symptoms if s not in VEHICLE])
            with self.subTest(scenario=sc.id):
                self.assertEqual(summarize(KB, make_record(KB, dx, 1), "vi").fault, sc.expected)

    def test_history_rows_newest_first_and_reopen(self):
        se01 = SCENARIOS["SE01"]
        state = {"history": [], "dx": new_dx()}
        for i in (1, 2):
            dx = dx_for(se01, "symptoms", selected=[s for s in se01.symptoms if s not in VEHICLE])
            state["history"].append(make_record(KB, dx, i))
        self.assertEqual(session_number(state), 3)
        r = rows(KB, state["history"], "vi")
        self.assertEqual([x.index for x in r], [1, 0])
        self.assertEqual(r[0].fault, KB.text("weak_battery", "vi"))
        reopen(state, 0)
        self.assertEqual((state["dx"]["step"], state["dx"]["record"]), (3, 0))
        self.assertEqual(session_number(state), 1)


class WindowTest(unittest.TestCase):
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
        theme.set_mode("light")
        self.root.destroy()

    def test_three_steps_survive_language_and_mode_changes(self):
        import gui
        app = gui.App(self.root)
        self.assertEqual(app.state["page"], "diagnosis")
        page = app.page
        page.set(method="guided")
        page.start()
        page.change_part("starting_fuel")
        truth = set(SCENARIOS["SE01"].symptoms)
        first = guided_session(app.kb, page.dx).question.symptom
        page.answer_guided(first in truth)
        app.set_lang("en")
        app.set_mode("dark")  # the window is rebuilt twice; the answer must still be there
        page = app.page
        self.assertEqual(page.dx["answers"][0][0], first)
        while page.dx["step"] == 2:
            page.answer_guided(guided_session(app.kb, page.dx).question.symptom in truth)
            self.root.update()
        rec = app.state["history"][page.dx["record"]]
        self.assertEqual(rec.result.diagnoses[0].fault, "weak_battery")
        page.verify(rec, "weak_battery")
        self.assertTrue(page.dx["wang"])
        app.show("history")
        self.root.update()
        app.page.open(0)
        self.assertEqual(app.state["page"], "diagnosis")
        page = app.page
        page.new_diagnosis()
        page.set(method="symptoms")
        page.start()
        page.toggle_symptom("horn_weak")
        page.finish()
        page.set(step=1)
        page.set(method="talk")
        page.start()
        page.use_example(TEXT["vi"]["examples"][0])
        self.assertEqual(page.text.get("1.0", "end").strip(), TEXT["vi"]["examples"][0])
        page.analyze()
        self.assertTrue(page.dx["text"])
        self.root.update()
        self.assertEqual(self.errors, [])


if __name__ == "__main__":
    unittest.main()
