import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from kb import WorkingMemory, load_kb, validate  # noqa: E402


def T(text):
    return {"vi": text, "en": text}


def symptom():
    return {"question": T("?")}


def fault():
    return {"name": T("fault"), "action": T("fix"), "severity": "self"}


def rule(rid, premises, conclusion, cf=0.8, source="manual p.1"):
    return {"id": rid, "if": premises, "then": conclusion, "cf": cf, "source": source}


class TempKB:
    """Write knowledge base files into a temporary folder."""

    def __init__(self, files):
        self._dir = tempfile.TemporaryDirectory()
        self.path = Path(self._dir.name)
        for name, data in files.items():
            text = data if isinstance(data, str) else json.dumps(data)
            (self.path / name).write_text(text, encoding="utf-8")

    def __enter__(self):
        return self.path

    def __exit__(self, *exc):
        self._dir.cleanup()


def small_kb(**overrides):
    data = {
        "subsystem": "test",
        "symptoms": {"a": symptom(), "b": symptom()},
        "intermediates": {"mid": {"description": T("mid")}},
        "faults": {"f": fault()},
        "rules": [rule("R1", ["a"], "mid"), rule("R2", ["mid", "b"], "f")],
    }
    data.update(overrides)
    return data


class RealKnowledgeBaseTest(unittest.TestCase):
    def test_project_knowledge_base_has_no_errors(self):
        kb = load_kb()
        report = validate(kb)
        self.assertEqual(report.errors, [])
        self.assertGreater(len(kb.rules), 0)
        self.assertGreater(len(kb.faults), 0)

    def test_every_fault_has_action_and_severity(self):
        kb = load_kb()
        for fid, f in kb.faults.items():
            with self.subTest(fault=fid):
                self.assertTrue(kb.action(fid, "vi"))
                self.assertIn(f.severity, ("self", "mechanic"))


class LoadTest(unittest.TestCase):
    def test_loads_symbols_and_rules_across_files(self):
        other = {"subsystem": "other", "faults": {"g": fault()}, "rules": [rule("R3", ["a"], "g")]}
        with TempKB({"one.json": small_kb(), "two.json": other}) as d:
            kb = load_kb(d)
        self.assertEqual(kb.problems, [])
        self.assertEqual(set(kb.symptoms), {"a", "b"})
        self.assertEqual(set(kb.faults), {"f", "g"})
        self.assertEqual([r.id for r in kb.rules_concluding("f")], ["R2"])
        self.assertEqual({r.id for r in kb.rules_using("a")}, {"R1", "R3"})
        self.assertTrue(kb.is_askable("a"))
        self.assertFalse(kb.is_askable("mid"))
        self.assertTrue(kb.is_fault("g"))

    def test_invalid_json_is_reported(self):
        with TempKB({"bad.json": "{ not json"}) as d:
            kb = load_kb(d)
        self.assertTrue(any("invalid JSON" in p for p in kb.problems))

    def test_duplicate_symbol_and_rule_id(self):
        dup = {"symptoms": {"a": symptom()}, "rules": [rule("R1", ["a"], "f")]}
        with TempKB({"one.json": small_kb(), "two.json": dup}) as d:
            report = validate(load_kb(d))
        self.assertTrue(any("'a' is already defined" in e for e in report.errors))
        self.assertTrue(any("R1: id already used" in e for e in report.errors))

    def test_bad_cf_and_severity(self):
        data = small_kb(
            faults={"f": {"name": T("f"), "action": T("x"), "severity": "maybe"}},
            rules=[rule("R1", ["a"], "mid", cf=1.5), rule("R2", ["mid", "b"], "f")],
        )
        with TempKB({"one.json": data}) as d:
            report = validate(load_kb(d))
        self.assertTrue(any("'cf'" in e for e in report.errors))
        self.assertTrue(any("severity" in e for e in report.errors))


class ValidateTest(unittest.TestCase):
    def check(self, data):
        with TempKB({"kb.json": data}) as d:
            return validate(load_kb(d))

    def test_clean_kb(self):
        report = self.check(small_kb())
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_unknown_symbol(self):
        report = self.check(small_kb(rules=[rule("R1", ["a", "typo"], "mid"), rule("R2", ["mid", "b"], "f")]))
        self.assertTrue(any("unknown symbol 'typo'" in e for e in report.errors))

    def test_symptom_cannot_be_concluded(self):
        report = self.check(small_kb(rules=[rule("R1", ["a"], "mid"), rule("R2", ["mid"], "b"),
                                            rule("R3", ["mid", "b"], "f")]))
        self.assertTrue(any("concludes symptom 'b'" in e for e in report.errors))

    def test_fault_cannot_be_premise(self):
        data = small_kb(faults={"f": fault(), "g": fault()},
                        rules=[rule("R1", ["a"], "mid"), rule("R2", ["mid", "b"], "f"), rule("R3", ["f"], "g")])
        report = self.check(data)
        self.assertTrue(any("uses fault 'f' as a premise" in e for e in report.errors))

    def test_unreachable_fault(self):
        report = self.check(small_kb(faults={"f": fault(), "lonely": fault()}))
        self.assertTrue(any("'lonely' is not concluded by any rule" in e for e in report.errors))

    def test_cycle_and_never_firing_rule(self):
        data = small_kb(
            intermediates={"x": {"description": T("x")}, "y": {"description": T("y")}},
            rules=[rule("R1", ["y"], "x"), rule("R2", ["x"], "y"), rule("R3", ["x", "a", "b"], "f")],
        )
        report = self.check(data)
        self.assertTrue(any("circular rules" in e for e in report.errors))
        self.assertTrue(any("R3 can never fire" in e for e in report.errors))

    def test_warnings(self):
        data = small_kb(
            symptoms={"a": symptom(), "b": symptom(), "unused": {"question": {"vi": "?"}}},
            rules=[rule("R1", ["a"], "mid", source=""), rule("R2", ["mid", "b"], "f"),
                   rule("R2b", ["b", "mid"], "f")],
        )
        report = self.check(data)
        self.assertEqual(report.errors, [])
        joined = "\n".join(report.warnings)
        self.assertIn("'unused' is not used", joined)
        self.assertIn("'unused' is missing en", joined)
        self.assertIn("R2b duplicates rule R2", joined)
        self.assertIn("have no source yet (R1)", joined)


class WorkingMemoryTest(unittest.TestCase):
    def test_tell_and_ask(self):
        wm = WorkingMemory()
        self.assertIsNone(wm.ask("a"))
        self.assertTrue(wm.tell("a", True))
        self.assertFalse(wm.tell("a", True))  # nothing changed
        wm.tell("b", False)
        self.assertTrue(wm.is_true("a"))
        self.assertTrue(wm.is_false("b"))
        self.assertTrue(wm.is_known("b"))
        self.assertEqual(wm.true_facts(), ["a"])
        wm.forget("a")
        self.assertNotIn("a", wm)
        wm.reset()
        self.assertEqual(len(wm), 0)

    def test_explain_returns_premises_first(self):
        wm = WorkingMemory()
        wm.tell("a")
        wm.tell("b")
        wm.tell("mid", cf=0.8, by="R1", premises=["a"])
        wm.tell("f", cf=0.6, by="R2", premises=["mid", "b"])
        order = [s for s, _ in wm.explain("f")]
        self.assertEqual(order, ["a", "mid", "b", "f"])
        self.assertEqual(wm.get("f").by, "R2")


if __name__ == "__main__":
    unittest.main()
