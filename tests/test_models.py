"""Model rules MD01-MD09 (knowledge_base/models.json, owner: Lâm): each fires only for its own bike model.

These check the rules work as written. Evaluation scenarios for them (MD01...) are written by
Giang and Khoa, who did not write the rules.
"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from backward_chaining import backward_chain  # noqa: E402
from forward_chaining import forward_chain  # noqa: E402
from kb import load_kb  # noqa: E402

KB = load_kb()


class ModelRulesTest(unittest.TestCase):
    def test_each_model_rule_puts_its_fault_first_only_for_its_model(self):
        rules = [r for r in KB.rules if r.id.startswith("MD")]
        self.assertEqual(len(rules), 9)
        for rule in rules:
            model, symptoms = rule.premises[0], list(rule.premises[1:])
            m = KB.models[model]
            bike = ["is_scooter" if m["kind"] == "scooter" else "is_manual",
                    "is_fuel_injected" if m["fuel"] == "fi" else "is_carburetor"]
            asked = [s for s in symptoms if KB.is_askable(s)]
            if len(asked) != len(symptoms):  # an intermediate premise: give the symptoms of its strongest rule
                inter = symptoms[0]
                asked = list(max(KB.rules_concluding(inter), key=lambda r: r.cf).premises)
            with self.subTest(rule=rule.id):
                own = forward_chain(KB, bike + asked + [model])
                self.assertEqual(own.diagnoses[0].fault, rule.conclusion)
                self.assertIn(rule.id, own.wm.get(rule.conclusion).by)
                generic = forward_chain(KB, bike + asked)
                cf = {d.fault: d.cf for d in generic.diagnoses}.get(rule.conclusion, 0.0)
                self.assertGreater(own.diagnoses[0].cf, cf, "the model rule raises the CF of its fault")

    def test_backward_chaining_agrees_and_does_not_count_the_model(self):
        truth = ["is_scooter", "is_fuel_injected", "judder_when_pulling_away", "model_honda_lead"]
        fw = forward_chain(KB, truth)
        bw = backward_chain(KB, truth)
        self.assertEqual([d.fault for d in bw.diagnoses][:1], [d.fault for d in fw.diagnoses][:1])
        self.assertAlmostEqual(bw.diagnoses[0].cf, fw.diagnoses[0].cf, places=3)
        without = backward_chain(KB, [s for s in truth if s != "model_honda_lead"])
        self.assertEqual(bw.questions_asked, without.questions_asked)


if __name__ == "__main__":
    unittest.main()
