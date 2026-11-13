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
        self.assertIn("3.1 Knowledge base and interface", heads)
        self.assertEqual(heads[heads.index("Chapter 4: Experiments and Results") - 1], "3.6 Chapter conclusion")
        self.assertFalse(re.search(r"\b\d\.[a-z]\b", text), "a placeholder such as 3.y was not renumbered")
        self.assertTrue(re.search(r"Figure 3\.\d\.1:", text))
        self.assertIn("References", heads)
        self.assertIn("Wang, H. (1960)", text)
        self.assertIn("Motorbike Fault Diagnosis Expert System", text)  # cover title
        self.assertGreaterEqual(len(doc.inline_shapes), 5)  # v4 cuts Ch3 to 3 figures (K1, G1)


if __name__ == "__main__":
    unittest.main()
