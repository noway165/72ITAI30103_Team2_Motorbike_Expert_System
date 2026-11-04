import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from kb import load_kb  # noqa: E402
from scenarios import check_scenarios, load_scenarios  # noqa: E402
from test_kb import TempKB, rule, small_kb  # noqa: E402
from wang import (And, Atom, Implies, Not, Or, check_engines, entails,  # noqa: E402
                  prove, random_answers, relevant_rules)

p, q, r = Atom("p"), Atom("q"), Atom("r")


class WangSmallExamplesTest(unittest.TestCase):
    def valid(self, left, right):
        return prove(left, right).valid

    def test_axiom(self):
        self.assertTrue(self.valid([p], [p]))
        self.assertFalse(self.valid([p], [q]))
        self.assertFalse(self.valid([], [p]))

    def test_tautologies(self):
        self.assertTrue(self.valid([], [Or((p, Not(p)))]))           # excluded middle
        self.assertTrue(self.valid([], [Implies(p, p)]))
        self.assertTrue(self.valid([], [Not(And((p, Not(p))))]))     # no contradiction
        self.assertFalse(self.valid([], [Or((p, q))]))

    def test_modus_ponens_and_tollens(self):
        self.assertTrue(self.valid([Implies(p, q), p], [q]))
        self.assertTrue(self.valid([Implies(p, q), Not(q)], [Not(p)]))
        self.assertFalse(self.valid([Implies(p, q)], [q]))           # p is not known
        self.assertFalse(self.valid([Implies(p, q), q], [p]))        # affirming the consequent

    def test_de_morgan(self):
        self.assertTrue(self.valid([Not(And((p, q)))], [Or((Not(p), Not(q)))]))
        self.assertTrue(self.valid([Or((Not(p), Not(q)))], [Not(And((p, q)))]))

    def test_horn_rule_needs_every_premise(self):
        rule_pq_r = Implies(And((p, q)), r)
        self.assertFalse(self.valid([rule_pq_r, p], [r]))
        self.assertTrue(self.valid([rule_pq_r, p, q], [r]))

    def test_chain_of_rules(self):
        self.assertTrue(self.valid([Implies(p, q), Implies(q, r), p], [r]))
        self.assertFalse(self.valid([Implies(p, q), Implies(q, r), r], [p]))

    def test_trace_ends_with_axioms(self):
        proof = prove([Implies(p, q), p], [q], trace=True)
        self.assertTrue(proof.valid)
        self.assertEqual(proof.steps, len(proof.trace))
        self.assertIn("→ on the left", proof.trace[0])
        self.assertTrue(all("axiom" in line for line in proof.trace[1:]))


class WangOnKnowledgeBaseTest(unittest.TestCase):
    def test_small_kb(self):
        with TempKB({"kb.json": small_kb()}) as d:
            kb = load_kb(d)
        self.assertTrue(entails(kb, ["a", "b"], "f").valid)
        self.assertFalse(entails(kb, ["a"], "f").valid)
        self.assertFalse(entails(kb, {"a": True, "b": False}, "f").valid)
        with self.assertRaises(ValueError):
            entails(kb, ["mid"], "f")  # only symptoms can be given
        with self.assertRaises(ValueError):
            entails(kb, ["a"], "typo")  # unknown goal

    def test_relevant_rules_skip_unrelated_rules(self):
        data = small_kb(rules=[rule("R1", ["a"], "mid"), rule("R2", ["mid", "b"], "f"),
                               rule("R3", ["b"], "g")],
                        faults={"f": small_kb()["faults"]["f"], "g": small_kb()["faults"]["f"]})
        with TempKB({"kb.json": data}) as d:
            kb = load_kb(d)
        self.assertEqual([r.id for r in relevant_rules(kb, "f")], ["R1", "R2"])

    def test_real_kb_example(self):
        kb = load_kb()
        proof = entails(kb, ["starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"],
                        "weak_battery")
        self.assertTrue(proof.valid)
        self.assertFalse(entails(kb, ["horn_weak"], "weak_battery").valid)

    def test_agrees_with_forward_chaining(self):
        kb = load_kb()
        sets = [s.symptoms for s in load_scenarios()] + random_answers(kb, 100, seed=1)
        for i, answers in enumerate(sets):
            check = check_engines(kb, str(i), answers)
            with self.subTest(answers=answers):
                self.assertEqual(check.wang, check.forward)


class ScenarioFilesTest(unittest.TestCase):
    def test_scenario_files_are_valid(self):
        scenarios = load_scenarios()
        self.assertGreaterEqual(len(scenarios), 20)
        self.assertEqual(check_scenarios(load_kb(), scenarios), [])

    def test_nobody_tests_their_own_rules(self):
        for s in load_scenarios():
            with self.subTest(scenario=s.id):
                self.assertNotEqual(s.written_by, s.rules_by)


if __name__ == "__main__":
    unittest.main()
