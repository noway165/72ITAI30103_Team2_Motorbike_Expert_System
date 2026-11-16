"""tools/build_report.py: the Word report is assembled from docs/report (owner: Lâm). Needs python-docx."""

import re
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


class BuildReportTest(unittest.TestCase):
    def test_chapters_sections_figures_and_references(self):
        try:
            import docx
            import build_report
        except ImportError:
            self.skipTest("python-docx is not installed")
        with tempfile.TemporaryDirectory() as folder:
            doc = docx.Document(str(build_report.build(Path(folder) / "report.docx")))
        heads = [p.text for p in doc.paragraphs if p.style.name.startswith("Heading")]
        text = "\n".join(p.text for p in doc.paragraphs)
        for n, title, _ in build_report.CHAPTERS:
            self.assertIn(f"Chapter {n}: {title}", heads)
        self.assertIn("3.1 AI techniques in the system", heads)
        self.assertIn("3.2 Knowledge base and interface", heads)
        self.assertFalse([h for h in heads if "Chapter conclusion" in h])  # removed after the lecturer's feedback
        self.assertFalse(re.search(r"\b\d\.[a-z]\b", text), "a placeholder such as 3.y was not renumbered")
        self.assertTrue(re.search(r"Figure 3\.\d\.1:", text))
        # Giang and Khoa both write "3.y": each keeps its own figure and number
        self.assertIn("Figure 3.3.1: Forward chaining on scenario SE01", text)
        self.assertIn("Figure 3.5.1: Backward chaining loop", text)
        self.assertNotIn("(Figure 3.5.1)", text.split("3.4 Verification")[0])
        cells = [p for t in doc.tables[1:] for row in t.rows for c in row.cells for p in c.paragraphs]  # [0]: cover
        self.assertTrue(cells and all(p.paragraph_format.keep_with_next for p in cells), "a table may split")
        self.assertIn("References", heads)
        self.assertEqual(heads[:3], ["Acknowledgments", "Commitment", "Team Contribution"])
        self.assertIn("33.3%", [c.text for t in doc.tables for row in t.rows for c in row.cells])
        self.assertEqual(heads[-1], "References")
        self.assertIn("Figure 3.2.3: The result for a Honda Vision", text)  # the app screens are in the body
        self.assertIn("Wang, H. (1960)", text)
        refs = [p.text for p in doc.paragraphs[[p.text for p in doc.paragraphs].index("References") + 1:] if p.text]
        self.assertEqual([r.split("]")[0] for r in refs], [f"[{n}" for n in range(1, 8)])  # numbered
        self.assertTrue(refs[0].startswith("[1] World Health Organization"))  # cited first, in Chapter 1
        self.assertIn("more than it has adults [1]", text)
        self.assertIn("Table 3.1.1: AI techniques", text)
        self.assertIn("Naryanto et al. [6]", text)  # first author of the IJEECS paper (checked on its DOI page)
        links = [r.target_ref for r in doc.part.rels.values() if r.is_external]
        self.assertIn("https://doi.org/10.1147/rd.41.0002", links)  # every DOI / URL is clickable
        self.assertEqual(len([u for u in links if u.startswith("http")]), 6)
        self.assertIn("Motorbike Fault Diagnosis Expert System", text)  # cover title
        self.assertGreaterEqual(len(doc.inline_shapes), 8)  # 1 + 1 + 3 (Ch3: G1, K1, chat) + 2 + 1


if __name__ == "__main__":
    unittest.main()
