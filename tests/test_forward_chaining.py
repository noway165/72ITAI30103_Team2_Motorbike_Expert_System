import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

from forward_chaining import combine_cf, forward_chain  # noqa: E402
from kb import WorkingMemory, load_kb  # noqa: E402
from test_kb import T, TempKB, fault, rule, small_kb, symptom  # noqa: E402


def run(data, facts, **kwargs):
    with TempKB({"kb.json": data}) as d:
        kb = load_kb(d)
    return forward_chain(kb, facts, **kwargs)


class CombineTest(unittest.TestCase):
    def test_combine(self):
        self.assertEqual(combine_cf([]), 0.0)
        self.assertAlmostEqual(combine_cf([0.8]), 0.8)
        self.assertAlmostEqual(combine_cf([0.8, 0.5]), 0.9)
        self.assertAlmostEqual(combine_cf([0.5, 0.8]), 0.9)  # order does not matter


class ForwardChainTest(unittest.TestCase):
    def test_chain_multiplies_cf(self):
        # R1: a -> mid (0.8), R2: mid AND b -> f (0.8)
        result = run(small_kb(), ["a", "b"])
        self.assertEqual([r.id for r in result.fired], ["R1", "R2"])
        self.assertEqual(result.rules_fired, 2)
        self.assertEqual(len(result.diagnoses), 1)
        self.assertEqual(result.diagnoses[0].fault, "f")
        self.assertAlmostEqual(result.diagnoses[0].cf, 0.64)  # 0.8 * min(0.8, 1.0)
        self.assertAlmostEqual(result.wm.get("mid").cf, 0.8)

    def test_missing_or_false_premise_does_not_fire(self):
        self.assertEqual(run(small_kb(), ["a"]).diagnoses, [])
        result = run(small_kb(), {"a": True, "b": False})
        self.assertEqual([r.id for r in result.fired], ["R1"])
        self.assertEqual(result.diagnoses, [])

    def test_rider_cf_is_used(self):
        result = run(small_kb(), {"a": 0.5, "b": True})
        self.assertAlmostEqual(result.wm.get("mid").cf, 0.4)   # 0.8 * 0.5
        self.assertAlmostEqual(result.diagnoses[0].cf, 0.32)   # 0.8 * min(0.4, 1.0)

    def test_two_rules_combined_before_next_rule(self):
        # mid is concluded by R1 (from a) and R3 (from c); f uses mid
        data = small_kb(
            symptoms={"a": symptom(), "b": symptom(), "c": symptom()},
            rules=[rule("R1", ["a"], "mid", cf=0.8), rule("R3", ["c"], "mid", cf=0.5),
                   rule("R2", ["mid", "b"], "f", cf=1.0)],
        )
        result = run(data, ["a", "b", "c"])
        self.assertAlmostEqual(result.wm.get("mid").cf, 0.9)
        self.assertEqual(result.wm.get("mid").by, "R1,R3")
        self.assertAlmostEqual(result.diagnoses[0].cf, 0.9)

    def test_ranking_and_threshold(self):
        data = small_kb(
            faults={"f": fault(), "g": fault(), "h": fault()},
            rules=[rule("R1", ["a"], "mid"), rule("R2", ["mid", "b"], "f"),
                   rule("R3", ["a"], "g", cf=0.9), rule("R4", ["b"], "h", cf=0.1)],
        )
        result = run(data, ["a", "b"])
        self.assertEqual([d.fault for d in result.diagnoses], ["g", "f"])  # h is below 0.2
        self.assertEqual(result.diagnoses[0].rules, ["R3"])
        self.assertEqual([d.fault for d in run(data, ["a", "b"], threshold=0.05).diagnoses], ["g", "f", "h"])

    def test_how_lists_premises_first(self):
        result = run(small_kb(), ["a", "b"])
        how = result.how("f")
        self.assertEqual(len(how), 4)
        self.assertTrue(how[0].startswith("a: given by the rider"))
        self.assertTrue(how[-1].startswith("f: rule R2"))

    def test_accepts_working_memory(self):
        wm = WorkingMemory()
        wm.tell("a", True)
        wm.tell("b", True)
        result = run(small_kb(), wm)
        self.assertEqual(result.diagnoses[0].fault, "f")
        self.assertIsNot(result.wm, wm)  # the rider's memory is not changed

    def test_rejects_unknown_symbol_and_non_symptom(self):
        with self.assertRaises(ValueError):
            run(small_kb(), ["a", "typo"])
        with self.assertRaises(ValueError):
            run(small_kb(), ["mid"])
        with self.assertRaises(ValueError):
            run(small_kb(), {"a": 1.5})


class ProjectScenarioTest(unittest.TestCase):
    """Scenarios on the real knowledge base: the expected fault must be ranked first."""

    @classmethod
    def setUpClass(cls):
        cls.kb = load_kb()

    def top(self, symptoms):
        result = forward_chain(self.kb, symptoms)
        self.assertTrue(result.diagnoses, f"no diagnosis for {symptoms}")
        return result.diagnoses[0]

    def test_scenarios(self):
        scenarios = {
            "weak_battery": ["starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years"],
            "out_of_fuel": ["engine_cranks", "engine_wont_start", "fuel_gauge_empty"],
            "clogged_air_filter": ["black_exhaust_smoke", "fuel_consumption_increased", "air_filter_overdue"],
            "low_engine_oil": ["oil_level_low", "engine_ticking_noise"],
            "engine_burning_oil": ["blue_white_exhaust_smoke", "oil_drops_between_changes"],
            "low_coolant": ["temp_warning_light_on", "coolant_below_min"],
            "cooling_fan_problem": ["temp_warning_light_on", "radiator_fan_not_running"],
            "worn_cvt_belt": ["is_scooter", "revs_rise_but_slow", "cvt_belt_overdue"],
            "worn_centrifugal_clutch": ["is_scooter", "judder_when_pulling_away"],
            "clutch_slipping": ["is_manual", "has_clutch_lever", "revs_rise_but_slow"],
            "loose_or_worn_chain": ["is_manual", "clicking_noise_from_rear", "chain_slack_high"],
            "chain_needs_lubrication": ["is_manual", "chain_dry_or_rusty"],
        }
        for expected, symptoms in scenarios.items():
            with self.subTest(fault=expected):
                self.assertEqual(self.top(symptoms).fault, expected)

    def test_weak_battery_cf_combines_two_rules(self):
        d = self.top(["starter_clicks_or_silent", "horn_weak", "battery_older_than_2_years",
                      "bike_unused_over_2_weeks"])
        self.assertEqual(d.fault, "weak_battery")
        self.assertEqual(d.rules, ["SF02", "SF03"])
        # SF01 gives 0.9; SF02: 0.85 * 0.9 = 0.765; SF03: 0.75 * 0.9 = 0.675
        self.assertAlmostEqual(d.cf, 0.765 + 0.675 * (1 - 0.765), places=4)

    def test_black_smoke_on_carburetor_bike_ranks_air_filter_first(self):
        result = forward_chain(self.kb, ["black_exhaust_smoke", "fuel_consumption_increased",
                                         "air_filter_overdue", "is_carburetor"])
        self.assertEqual([d.fault for d in result.diagnoses],
                         ["clogged_air_filter", "carburetor_mixture_too_rich"])


if __name__ == "__main__":
    unittest.main()
