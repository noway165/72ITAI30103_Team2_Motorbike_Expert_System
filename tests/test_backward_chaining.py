"""Unit tests for src/backward_chaining.py (owner: Khoa).

Run from the repository root:
    python -m unittest discover tests
"""

import json
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from backward_chaining import (  # noqa: E402
    UNKNOWN, BackwardChainer, BackwardSession, backward_chain, explain_why,
)
from forward_chaining import forward_chain  # noqa: E402
from kb import load_kb, validate  # noqa: E402
from scenarios import load_scenarios  # noqa: E402


def _text(vi):
    return {"vi": vi, "en": vi}


TINY_KB = {
    "subsystem": "tiny",
    "symptoms": {s: {"question": _text(f"{s}?")} for s in ("a", "b", "c", "d")},
    "intermediates": {"m": {"description": _text("m")}},
    "faults": {
        f: {"name": _text(f), "action": _text("fix " + f), "severity": "self"}
        for f in ("f1", "f2")
    },
    "rules": [
        {"id": "R1", "if": ["a", "b"], "then": "m", "cf": 0.8, "source": "test"},
        {"id": "R2", "if": ["m", "c"], "then": "f1", "cf": 0.9, "source": "test"},
        {"id": "R3", "if": ["d"], "then": "f1", "cf": 0.5, "source": "test"},
        {"id": "R4", "if": ["a", "d"], "then": "f2", "cf": 0.7, "source": "test"},
    ],
}


class TinyKbTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        Path(cls._tmp.name, "tiny.json").write_text(json.dumps(TINY_KB), encoding="utf-8")
        cls.kb = load_kb(cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_tiny_kb_is_valid(self):
        self.assertTrue(validate(self.kb).ok)

    def test_proof_through_two_levels(self):
        result = backward_chain(self.kb, ["a", "b", "c"], goals=["f1"])
        self.assertEqual(len(result.diagnoses), 1)
        d = result.diagnoses[0]
        self.assertEqual(d.fault, "f1")
        self.assertAlmostEqual(d.cf, 0.9 * (0.8 * 1.0), places=4)  # R2 * min(R1, c)
        self.assertEqual(d.rules, ["R2"])

    def test_two_rules_are_combined(self):
        result = backward_chain(self.kb, ["a", "b", "c", "d"], goals=["f1"])
        self.assertAlmostEqual(result.diagnoses[0].cf, 0.72 + 0.5 * (1 - 0.72), places=4)
        self.assertEqual(result.diagnoses[0].rules, ["R2", "R3"])

    def test_nothing_proven_when_all_answers_are_no(self):
        result = backward_chain(self.kb, [], goals=["f1", "f2"])
        self.assertEqual(result.diagnoses, [])

    def test_rider_cf_is_used(self):
        result = backward_chain(self.kb, {"d": 0.5}, goals=["f1"])
        self.assertAlmostEqual(result.diagnoses[0].cf, 0.5 * 0.5, places=4)

    def test_false_premise_skips_remaining_questions(self):
        asked = []

        def ask(symptom, chain):
            asked.append(symptom)
            return False

        BackwardChainer(self.kb, ask).diagnose(goals=["f1"])
        # R1 asks a (false) and never asks b; R2 reuses m (not proven) and never asks c; R3 asks d
        self.assertEqual(asked, ["a", "d"])

    def test_same_question_is_never_asked_twice(self):
        counts = {}

        def ask(symptom, chain):
            counts[symptom] = counts.get(symptom, 0) + 1
            return True

        result = BackwardChainer(self.kb, ask).diagnose(goals=["f1", "f2"])
        self.assertTrue(all(n == 1 for n in counts.values()), counts)  # a and d appear in two rules
        self.assertEqual(result.questions_asked, len(counts))

    def test_why_chain_when_a_question_is_asked(self):
        seen = {}

        def ask(symptom, chain):
            seen[symptom] = [(step.goal, step.rule.id) for step in chain]
            return True

        BackwardChainer(self.kb, ask).diagnose(goals=["f1"])
        self.assertEqual(seen["a"], [("f1", "R2"), ("m", "R1")])  # outermost rule first
        self.assertEqual(seen["c"], [("f1", "R2")])
        self.assertEqual(seen["d"], [("f1", "R3")])

    def test_explain_why_text(self):
        lines = []

        def ask(symptom, chain):
            if symptom == "c":
                lines.extend(explain_why(self.kb, chain, "en"))
            return True

        BackwardChainer(self.kb, ask).diagnose(goals=["f1"])
        self.assertEqual(len(lines), 2)  # a heading and the one rule being tried
        self.assertIn("Rule R2", lines[1])
        self.assertIn("m", lines[1])

    def test_how_lists_premises_first(self):
        result = backward_chain(self.kb, ["a", "b", "c"], goals=["f1"])
        lines = result.how("f1")
        self.assertEqual(len(lines), 5)  # a, b, m, c, f1
        self.assertTrue(lines[0].startswith("a:"))
        self.assertTrue(lines[-1].startswith("f1: rule R2"))

    def test_counters(self):
        result = backward_chain(self.kb, ["a", "b", "c"], goals=["f1"])
        self.assertEqual(result.rules_fired, 2)       # R1 and R2
        self.assertEqual(result.rules_tried, 3)       # R2, R1, R3
        self.assertEqual(result.questions_asked, 4)   # a, b, c, d

    def test_threshold(self):
        result = backward_chain(self.kb, {"d": 0.5}, goals=["f1"], threshold=0.3)
        self.assertEqual(result.diagnoses, [])

    def test_bad_input(self):
        with self.assertRaises(ValueError):
            backward_chain(self.kb, ["a"], goals=["not_a_fault"])
        with self.assertRaises(ValueError):
            backward_chain(self.kb, ["m"], goals=["f1"])  # m is not a symptom
        with self.assertRaises(ValueError):
            BackwardChainer(self.kb, lambda s, c: 1.5).diagnose(goals=["f1"])


class SessionTests(unittest.TestCase):
    """BackwardSession: next question, answer, repeat (no input(), used by the GUI)."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        Path(cls._tmp.name, "tiny.json").write_text(json.dumps(TINY_KB), encoding="utf-8")
        cls.kb = load_kb(cls._tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def run_session(self, yes, goals=None):
        session = BackwardSession(self.kb, goals=goals)
        asked = []
        while not session.finished:
            asked.append(session.question.symptom)
            session.answer(session.question.symptom in yes)
        return session, asked

    def test_questions_come_one_at_a_time_with_the_why_chain(self):
        session = BackwardSession(self.kb, goals=["f1"])
        q = session.question
        self.assertEqual((q.symptom, q.number), ("a", 1))
        self.assertEqual([(step.goal, step.rule.id) for step in q.chain], [("f1", "R2"), ("m", "R1")])
        self.assertIsNone(session.result)
        session.answer(True)
        self.assertEqual((session.question.symptom, session.question.number), ("b", 2))

    def test_same_result_and_questions_as_backward_chain(self):
        for yes in (["a", "b", "c"], ["a", "b", "c", "d"], ["d"], []):
            session, asked = self.run_session(yes)
            reference = backward_chain(self.kb, yes)
            self.assertEqual([(d.fault, d.cf) for d in session.result.diagnoses],
                             [(d.fault, d.cf) for d in reference.diagnoses])
            self.assertEqual(session.result.questions_asked, reference.questions_asked)
            self.assertEqual(len(asked), len(set(asked)))  # never asks twice

    def test_a_false_premise_skips_the_rest_of_the_rule(self):
        session, asked = self.run_session([], goals=["f1"])
        self.assertEqual(asked, ["a", "d"])  # b and c cannot change the result any more

    def test_unknown_is_treated_as_no_and_remembered(self):
        session = BackwardSession(self.kb, goals=["f1"])
        session.answer(UNKNOWN)          # a
        session.answer(True)             # d
        self.assertTrue(session.finished)
        self.assertEqual(session.unknown, ["a"])
        self.assertAlmostEqual(session.result.diagnoses[0].cf, 0.5, places=4)  # only R3

    def test_undo_asks_the_last_question_again(self):
        session = BackwardSession(self.kb, goals=["f1"])
        self.assertFalse(session.undo())
        session.answer(False)
        self.assertEqual(session.question.symptom, "d")
        self.assertTrue(session.undo())
        self.assertEqual(session.question.symptom, "a")
        session.answer(True)
        self.assertEqual(session.question.symptom, "b")

    def test_remaining_hypotheses_shrink_with_no_answers(self):
        session = BackwardSession(self.kb)
        self.assertEqual(session.remaining(), ["f1", "f2"])
        session.answer(False)            # a: R1 and R4 are dead; f1 is still possible through R3
        self.assertEqual(session.remaining(), ["f1"])
        session.answer(False)            # d
        self.assertEqual(session.remaining(), [])
        self.assertTrue(session.finished)

    def test_answers_can_be_restored(self):
        session = BackwardSession(self.kb, goals=["f1"], answers={"a": True, "b": True})
        self.assertEqual((session.question.symptom, session.question.number), ("c", 3))

    def test_bad_calls_raise(self):
        with self.assertRaises(ValueError):
            BackwardSession(self.kb, goals=["nope"])
        with self.assertRaises(ValueError):
            BackwardSession(self.kb, answers={"m": True})
        session, _ = self.run_session([])
        with self.assertRaises(RuntimeError):
            session.answer(True)
        with self.assertRaises(ValueError):
            BackwardSession(self.kb).answer(1.5)


class RealKnowledgeBaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def test_brake_and_suspension_files_have_no_errors(self):
        report = validate(self.kb)
        mine = [e for e in report.errors if "brakes.json" in e or "tyres_suspension.json" in e]
        self.assertEqual(mine, [])

    def test_worn_brake_pads_example(self):
        result = backward_chain(self.kb, ["brake_squeal", "brake_pad_thin_visible"],
                                goals=["worn_brake_pads"])
        self.assertEqual(result.diagnoses[0].fault, "worn_brake_pads")
        self.assertAlmostEqual(result.diagnoses[0].cf, 0.9, places=4)

    def test_ts15_lost_damping_alone_gives_worn_rear_shock(self):
        """Scenario BT10: bouncy rear shock and a low stance, nothing else."""
        result = backward_chain(self.kb, ["rear_shock_bouncy", "sits_low_parked"])
        self.assertEqual(result.diagnoses[0].fault, "worn_rear_shock")
        self.assertEqual(result.diagnoses[0].rules, ["TS15"])
        self.assertAlmostEqual(result.diagnoses[0].cf, 0.7 * 0.7, places=4)  # TS09 then TS15
        more = backward_chain(self.kb, ["rear_shock_bouncy", "sits_low_parked", "suspension_clunk"],
                              goals=["worn_rear_shock"])
        self.assertGreater(more.diagnoses[0].cf, result.diagnoses[0].cf)     # TS11 adds to TS15

    def test_brake_hydraulic_loss_is_not_a_dead_end(self):
        """BR13: low fluid with a soft lever points to a leak even when no leak is seen."""
        result = backward_chain(self.kb, ["brake_lever_spongy", "brake_fluid_low"])
        cfs = {d.fault: d.cf for d in result.diagnoses}
        self.assertAlmostEqual(cfs["brake_fluid_leak"], 0.8 * 0.6, places=4)   # BR04 then BR13
        self.assertEqual(result.diagnoses[0].fault, "brake_air_in_lines")      # BR08 stays first
        seen = backward_chain(self.kb, ["brake_fluid_leak_visible", "brake_fluid_low"])
        self.assertEqual(seen.diagnoses[0].fault, "brake_fluid_leak")
        self.assertGreater(seen.diagnoses[0].cf, 0.9)                         # BR06 and BR13 combined

    def test_every_intermediate_of_my_files_reaches_a_fault_alone(self):
        for symbol, sym in self.kb.intermediates.items():
            if sym.subsystem in ("brakes", "tyres_suspension"):
                alone = [r for r in self.kb.rules_using(symbol) if list(r.premises) == [symbol]]
                self.assertTrue(alone, f"{symbol} is a dead end")

    def test_my_rules_all_have_a_source(self):
        missing = [r.id for r in self.kb.rules if r.subsystem in ("brakes", "tyres_suspension") and not r.source]
        self.assertEqual(missing, [])

    def test_session_matches_backward_chain_on_every_scenario(self):
        for s in load_scenarios():
            with self.subTest(scenario=s.id):
                session = BackwardSession(self.kb)
                while not session.finished:
                    session.answer(session.question.symptom in s.symptoms)
                reference = backward_chain(self.kb, s.symptoms)
                self.assertEqual([(d.fault, d.cf) for d in session.result.diagnoses],
                                 [(d.fault, d.cf) for d in reference.diagnoses])
                self.assertEqual(session.result.questions_asked, reference.questions_asked)
                self.assertIn(s.expected, session.remaining())

    def test_same_diagnosis_as_forward_chaining(self):
        symptoms = sorted(self.kb.symptoms)
        rng = random.Random(0)
        for _ in range(40):
            chosen = rng.sample(symptoms, rng.randint(1, min(8, len(symptoms))))
            forward = {d.fault: d.cf for d in forward_chain(self.kb, chosen).diagnoses}
            backward = {d.fault: d.cf for d in backward_chain(self.kb, chosen).diagnoses}
            self.assertEqual(set(forward), set(backward), f"symptoms: {chosen}")
            for fault, cf in forward.items():
                self.assertAlmostEqual(cf, backward[fault], places=3, msg=f"{fault}, symptoms: {chosen}")


if __name__ == "__main__":
    unittest.main()
