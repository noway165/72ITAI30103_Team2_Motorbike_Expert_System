"""Test scenarios: the symptoms a rider answers "yes" to, and the fault a
mechanic would expect. Every symptom not listed is answered "no".

Each file in scenarios/ is written by someone who did NOT write the rules for
that system (see scenarios/README.md). Used by wang.py and the evaluation script.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

from kb import ROOT, KnowledgeBase

DEFAULT_SCENARIO_DIR = ROOT / "scenarios"


@dataclass
class Scenario:
    id: str
    file: str
    symptoms: List[str]
    expected: str
    description: Dict[str, str] = field(default_factory=dict)
    written_by: str = ""
    rules_by: str = ""


def load_scenarios(folder: Path | str = DEFAULT_SCENARIO_DIR) -> List[Scenario]:
    """Read every *.json file in `folder` (sorted)."""
    scenarios = []
    for path in sorted(Path(folder).glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for spec in data["scenarios"]:
            scenarios.append(Scenario(
                id=spec["id"], file=path.name, symptoms=list(spec["symptoms"]),
                expected=spec["expected"], description=spec.get("description", {}),
                written_by=data.get("written_by", ""), rules_by=data.get("rules_by", ""),
            ))
    return scenarios


def check_scenarios(kb: KnowledgeBase, scenarios: List[Scenario]) -> List[str]:
    """Mistakes in the scenario files: unknown symptoms, unknown faults, repeated ids."""
    problems = []
    seen = set()
    for s in scenarios:
        if s.id in seen:
            problems.append(f"{s.file}: scenario id {s.id} is used twice")
        seen.add(s.id)
        for symptom in s.symptoms:
            if not kb.is_askable(symptom):
                problems.append(f"{s.file}: {s.id} uses {symptom!r}, which is not a symptom")
        if not kb.is_fault(s.expected):
            problems.append(f"{s.file}: {s.id} expects {s.expected!r}, which is not a fault")
    return problems
