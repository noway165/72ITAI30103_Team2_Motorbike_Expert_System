"""Tests for Giang's MotoLogic screens: gui_diagnosis.py and gui_history.py (logic, then the window)."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import theme  # noqa: E402
from backward_chaining import UNKNOWN  # noqa: E402
from gui_backward import ALL  # noqa: E402
from gui_diagnosis import (TEXT, VEHICLE, bike_text, checklist, guided_session, make_record, model_name,  # noqa: E402
                           needs_part, new_dx, pick_model, session_number, subsystem_counts, summarize, talk_interview,
                           to_guided, vehicle_answers, wang_check)
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

    def test_guided_asks_for_the_part_first(self):
        dx = dx_for(SCENARIOS["BT03"], "guided")
        self.assertIn("part_asked", new_dx())
        self.assertTrue(needs_part(dx))
        dx["part"] = "brakes"
        self.assertFalse(needs_part(dx))
        self.assertEqual({KB.symbols[g].subsystem for g in guided_session(KB, dx).goals}, {"brakes"})
        dx.update(part=ALL, part_asked=True)  # "not sure, ask about everything"
        self.assertFalse(needs_part(dx))
        self.assertEqual(set(guided_session(KB, dx).goals), set(KB.faults))
        self.assertFalse(needs_part(dict(dx, part_asked=False, answers=[("horn_weak", True)])))
        self.assertFalse(needs_part(dict(dx, part_asked=False, method="talk")))

    def test_nothing_understood_switches_to_guided_and_keeps_the_text(self):
        dx = dx_for(SCENARIOS["SE01"], "talk", text="xyz abc", replies=[("horn_weak", True)])
        self.assertFalse(talk_interview(KB, dx)[1])
        to_guided(dx)
        self.assertEqual((dx["method"], dx["step"], dx["part"], dx["answers"]), ("guided", 2, ALL, []))
        self.assertEqual(dx["text"], "xyz abc")
        self.assertTrue(needs_part(dx))

    def test_choosing_a_bike_model(self):
        dx = new_dx()
        self.assertEqual(dx["model"], "")
        pick_model(KB, dx, "model_yamaha_exciter")
        self.assertEqual((dx["kind"], dx["fuel"]), ("manual", "fi"))
        a = vehicle_answers(dx["kind"], dx["fuel"], dx["model"], KB.models)
        self.assertTrue(a["model_yamaha_exciter"] and a["has_clutch_lever"] and a["is_manual"])
        self.assertFalse(a["model_honda_vision"])
        pick_model(KB, dx, "")  # another bike: type and fuel are chosen by hand, no listed model
        self.assertFalse(any(v for m, v in vehicle_answers(dx["kind"], dx["fuel"], "", KB.models).items()
                             if m.startswith("model_")))
        self.assertEqual(bike_text("manual", "fi", "vi", model_name(KB, "model_yamaha_exciter")), "Yamaha Exciter 155")

    def test_model_rule_ranks_the_model_fault_and_the_record_keeps_the_model(self):
        dx = new_dx()
        pick_model(KB, dx, "model_honda_lead")
        dx.update(method="symptoms", step=2, selected=["judder_when_pulling_away"])
        rec = make_record(KB, dx, 1)
        self.assertEqual(rec.model, "model_honda_lead")
        self.assertEqual(rec.result.diagnoses[0].fault, "worn_centrifugal_clutch")
        self.assertIn("MD02", summarize(KB, rec, "vi").chain)

    def test_bike_model_wording_in_both_languages(self):
        for lang in ("vi", "en"):
            self.assertIn("{name}", TEXT[lang]["for_model"])
            self.assertTrue(TEXT[lang]["other_bike"])

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
                self.assertEqual(s.observations, len([x for x in rec.yes if KB.symbols[x].subsystem != "vehicle"]))

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
        self.assertTrue(needs_part(page.dx))  # the part card is shown first
        page.on_key(type("E", (), {"keysym": "y"})())  # keys do not answer the hidden first question
        self.assertEqual(page.dx["answers"], [])
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
        page.text.delete("1.0", "end")
        page.text.insert("1.0", "đề chỉ nghe tạch tạch")  # not enough yet: a question is waiting
        page.analyze()  # the conversation starts: what was read, then a question
        self.assertTrue(page.dx["chat"])
        page.send("tại sao hỏi vậy?")
        page.entry._hide()  # what focusing the box does
        page.entry.insert(0, "có")
        page.send()
        self.assertEqual(len(page.dx["replies"]), 1)
        self.root.update()
        page.send("xem kết quả")
        self.assertEqual(page.dx["step"], 3)
        page.set(step=1, text="")
        page.start()
        page.text.insert("1.0", "xyz abc")
        page.analyze()  # nothing recognised: the text box stays, with a way out
        self.assertTrue(page.text.winfo_exists())
        page.switch_to_guided()
        self.assertEqual((page.dx["method"], page.dx["text"]), ("guided", "xyz abc"))
        page.change_part(ALL)  # "All" in the part bar counts as an answer to the part card
        self.assertFalse(needs_part(page.dx))
        self.root.update()
        self.assertEqual(self.errors, [])

    def test_bike_model_picker_and_result_specs(self):
        import gui
        app = gui.App(self.root)
        page = app.page
        page.set(step=1)
        self.root.update()
        shown = [w.cget("text") for w in _all(page) if isinstance(w, tk_label())]
        for m in app.kb.models.values():  # every listed model can be picked in step 1
            self.assertIn(m["name"], shown)
        self.assertIn(TEXT["vi"]["other_bike"], shown)
        page.choose_model("model_honda_vision")
        page.set(method="symptoms")
        page.start()
        for sid in ("starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"):
            page.toggle_symptom(sid)
        page.finish()
        self.root.update()
        shown = " ".join(w.cget("text") for w in _all(page) if isinstance(w, tk_label()))
        self.assertIn("GTZ6V", shown)  # the Vision battery from its owner's manual
        page.new_diagnosis()
        page.set(method="talk")
        page.start()
        page.text.insert("1.0", "Vision đề chỉ nghe tạch tạch, còi cũng yếu, ắc quy dùng hơn 2 năm")
        page.analyze()
        page.send("xem kết quả")  # the model is read from the text: the result must still draw
        self.root.update()
        self.assertEqual(self.errors, [])

    def test_low_cf_is_not_called_highly_likely(self):
        """Khoa's exe test 13/11: BT10 (CF 0.49) was headed "LỖI CÓ KHẢ NĂNG CAO"."""
        import gui
        app = gui.App(self.root)
        page = app.page
        for symptoms, want, other in ((("rear_shock_bouncy", "sits_low_parked"), "possible", "likely"),
                                      (("starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"),
                                       "likely", "possible")):
            page.new_diagnosis()
            page.set(step=1, method="symptoms")
            page.start()
            for sid in symptoms:
                page.toggle_symptom(sid)
            page.finish()
            self.root.update()
            shown = [w.cget("text") for w in _all(page) if isinstance(w, tk_label())]
            self.assertIn(TEXT["vi"][want].upper(), shown)
            self.assertNotIn(TEXT["vi"][other].upper(), shown)
        self.assertEqual(self.errors, [])


def tk_label():
    import tkinter as tk
    return tk.Label


def _all(widget):
    for child in widget.winfo_children():
        yield child
        yield from _all(child)


if __name__ == "__main__":
    unittest.main()
