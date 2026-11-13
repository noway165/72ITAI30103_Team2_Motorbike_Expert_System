"""Build the Word report from the Markdown sections in docs/report (owner: Lâm).

    python tools/build_report.py        # -> build/report/Final_Report_Group2.docx

The lecturer's sample (docs/report/sample/Final_Project_report_sample.docx) gives the cover (frame,
logo, layout), the page size, margins, styles and the footer; everything else comes from the section files:

    front_matter_lam.md            cover (## Cover, "- Key: value" lines), Acknowledgments, Commitment
    introduction_background_lam.md Chapter 1 and 2 (## Chapter N: ... with ### sections), References
    methodology_lam.md, methodology_giang.md, methodology_khoa.md, assistant_lam.md   Chapter 3
    experiments_results_khoa.md    Chapter 4
    discussion.md                  Chapter 5
    conclusion_lam.md              Chapter 6

Conventions the files already follow:
  - everything before the first "## " heading is a note for the team and is skipped;
  - "## 3.y Title" is a section; its number is replaced by the next number of the chapter,
    and "3.y" is replaced everywhere in the chapter ("Figure 3.y.1" -> "Figure 3.2.1");
  - a "Chapter conclusion" section is moved to the end of its chapter (Chapter 3 has parts from three people);
  - a figure is "Figure ID: caption" followed by "File: `figures/x.png`", or "![..](figures/x.png)" followed by
    the caption line; it is placed after the first paragraph that mentions it;
  - "## Figure(s)" sections only hold figures; "## References" lists the references (one "- " per item);
  - tables are Markdown tables, followed by a "Table ID: caption" line.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "report"
SAMPLE = REPORT / "sample" / "Final_Project_report_sample.docx"
OUT = ROOT / "build" / "report" / "Final_Report_Group2.docx"

CHAPTERS = [  # (number, title, [file or (file, "Chapter N")])
    (1, "Introduction", [("introduction_background_lam.md", "Chapter 1")]),
    (2, "Background", [("introduction_background_lam.md", "Chapter 2")]),
    (3, "Methodology", ["methodology_lam.md", "methodology_giang.md", "methodology_khoa.md", "assistant_lam.md"]),
    (4, "Experiments and Results", ["experiments_results_khoa.md"]),
    (5, "Discussion", ["discussion.md"]),
    (6, "Conclusion", [("conclusion_lam.md", "Chapter 6")]),
]
FONT = "Times New Roman"
FIG = re.compile(r"^Figure ([\w.]+):\s*(.+)$")
FILE = re.compile(r"^File:\s*`([^`]+)`")
IMG = re.compile(r"^!\[[^\]]*\]\(([^)]+)\)")
TOKEN = re.compile(r"^(\d+\.[\w]+)\s+")  # "3.y " or "4.1 " in front of a section title


# --- reading the Markdown ----------------------------------------------------------------------------------
def lines_of(name: str, chapter: str = "") -> list:
    """The lines of a section file after the team notes; with `chapter`, only that chapter's part (### -> ##)."""
    lines = (REPORT / name).read_text(encoding="utf-8").splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("## ")), len(lines))
    lines = lines[start:]
    if not chapter:
        return lines
    out, inside = [], False
    for ln in lines:
        if ln.startswith("## "):
            inside = ln[3:].startswith(chapter + ":")
            continue
        if inside:
            out.append(ln[1:] if ln.startswith("### ") else ln)
    return out


def parse(lines: list) -> tuple:
    """(sections, figures, references): sections are dicts {title, token, blocks}; blocks are
    ("p", text), ("table", rows, caption)."""
    sections, figures, refs = [], {}, []
    cur = None
    i = 0
    while i < len(lines):
        ln = lines[i].rstrip()
        if ln.startswith("## "):
            title = ln[3:].strip()
            m = TOKEN.match(title)
            cur = {"title": TOKEN.sub("", title), "token": m.group(1) if m else "", "blocks": [],
                   "kind": "refs" if title.lower().startswith("references") else
                   "figs" if title.lower().startswith("figure") else "text"}
            sections.append(cur)
        elif cur is None or not ln.strip():
            pass
        elif cur["kind"] == "refs":
            if ln.startswith("- "):
                refs.append(ln[2:].strip())
        elif FIG.match(ln) or IMG.match(ln):
            fid, caption, path = None, "", ""
            if IMG.match(ln):  # ![..](path) then the caption line
                path = IMG.match(ln).group(1)
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                m = FIG.match(lines[j].strip()) if j < len(lines) else None
                if m:
                    fid, caption, i = m.group(1), m.group(2), j
            else:
                fid, caption = FIG.match(ln).groups()
                if i + 1 < len(lines) and FILE.match(lines[i + 1].strip()):
                    path, i = FILE.match(lines[i + 1].strip()).group(1), i + 1
            if fid and path:
                figures[fid] = (path, caption)
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                if not re.fullmatch(r"\|[\s\-:|]+\|", lines[i].strip()):
                    rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            caption = lines[i].strip() if i < len(lines) and lines[i].startswith("Table ") else ""
            if not caption:
                i -= 1
            cur["blocks"].append(("table", rows, caption))
        elif cur["kind"] == "text" and not FILE.match(ln) and not ln.startswith("Other ") and not ln.startswith("`"):
            text = [ln.strip()]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"(#|\||!\[|Figure |Table |File:|- )",
                                                                                 lines[i + 1]):
                i += 1
                text.append(lines[i].strip())
            cur["blocks"].append(("p", " ".join(text)))
        i += 1
    return sections, figures, refs


def chapter(parts: list) -> tuple:
    """Sections of one chapter in order (conclusion last), the figures, the references and the renumbering map."""
    sections, figures, refs = [], {}, []
    for part in parts:
        name, ch = (part, "") if isinstance(part, str) else part
        s, f, r = parse(lines_of(name, ch))
        sections += [x for x in s if x["kind"] == "text"]
        figures.update(f)
        refs += r
    sections.sort(key=lambda x: "chapter conclusion" in x["title"].lower())  # stable: conclusion last
    return sections, figures, refs


# --- writing the Word file --------------------------------------------------------------------------------
def field(paragraph, code: str) -> None:
    """A Word field (PAGE, TOC ...) that Word fills in when the document is opened."""
    run = paragraph.add_run()
    for kind, text in (("begin", None), (None, code), ("separate", None), ("end", None)):
        if kind:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), kind)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = text
        run._r.append(el)


def inline(paragraph, text: str, size: float = 13, bold: bool = False, italic: bool = False) -> None:
    """Text with **bold**, `code` and [label](url) links (kept as their label)."""
    text = re.sub(r"\[([^\]]+)\]\((?:https?://|[\w./-]+\.md)[^)]*\)", r"\1", text)
    for piece in re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text):
        if not piece:
            continue
        code = piece.startswith("`")
        run = paragraph.add_run(piece.strip("*`") if (code or piece.startswith("**")) else piece)
        run.bold = bold or piece.startswith("**")
        run.italic = italic
        run.font.size = Pt(size - 1 if code else size)
        run.font.name = "Consolas" if code else FONT
        run._r.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), run.font.name)


def para(doc, text="", size=13, bold=False, italic=False, align=None, style=None, spacing=2.0, after=0):
    p = doc.add_paragraph(style=style)
    if text:
        inline(p, text, size, bold, italic)
    if align is not None:
        p.alignment = align
    if spacing is not None:
        p.paragraph_format.line_spacing = spacing
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    return p


def page_break(doc) -> None:
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def setup(doc) -> None:
    """Fonts and spacing of the README: Times New Roman 13, headings 18 / 13, double-spaced."""
    # Normal is left as in the sample (its cover depends on it); body paragraphs set size and spacing themselves
    for name, size in (("Heading 1", 18), ("Heading 2", 13), ("Heading 3", 13)):
        st = doc.styles[name]
        st.font.name, st.font.size, st.font.bold = FONT, Pt(size), True
        st.font.color.rgb = RGBColor(0, 0, 0)
        st.element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), FONT)
        st.paragraph_format.space_before, st.paragraph_format.space_after = Pt(6), Pt(3)
        st.paragraph_format.keep_with_next = True  # a heading never ends a page
    for name, size, bold in (("toc 1", 13, True), ("toc 2", 12, False)):  # the sample's toc 1 is 22 pt italic
        st = doc.styles[name]
        st.font.name, st.font.size, st.font.bold, st.font.italic = FONT, Pt(size), bold, False
        st.paragraph_format.line_spacing, st.paragraph_format.space_after = 1.0, Pt(2)
    settings = doc.settings.element  # ask Word to fill in the table of contents when the file is opened
    upd = OxmlElement("w:updateFields")
    upd.set(qn("w:val"), "true")
    settings.append(upd)


def set_text(paragraph, text: str) -> None:
    """Replace a paragraph's text, keeping the formatting of its first run."""
    runs = [r for r in paragraph.runs if r.text]
    if runs:
        runs[0].text = text
        for r in runs[1:]:
            r.text = ""


def set_lines(cell, lines: list) -> None:
    """Replace a table cell's text with lines (line breaks), keeping the first run's formatting."""
    first = cell.paragraphs[0]
    for extra in cell.paragraphs[1:]:
        extra._p.getparent().remove(extra._p)
    runs = [r for r in first.runs if r.text]
    run = runs[0] if runs else first.add_run()
    for r in first.runs:
        if r._r is not run._r:  # python-docx makes a new Run object on every access
            r._r.getparent().remove(r._r)
    run.text = lines[0]
    for line in lines[1:]:
        run.add_break()
        run.add_text(line)


def cover(doc, info: dict) -> None:
    """The sample's own cover (frame, logo, layout) with our course, title, group and date."""
    for p in doc.paragraphs:
        t = p.text.strip()
        if t == "Discrete Mathematics":
            set_text(p, info.get("Course", ""))
        elif t.startswith("Applying BFS"):
            set_text(p, info.get("Title", ""))
        elif t.startswith("Lecturer:"):
            set_text(p, "Lecturer: " + info.get("Lecturer", ""))
        elif t.startswith("Course code:"):
            set_text(p, "Course code: " + info.get("Course code", ""))
        elif t.startswith("Ho Chi Minh City"):
            set_text(p, info.get("Place and date", ""))
    members = [m.partition("|") for m in info.get("Member", [])]
    cells = doc.tables[0].rows[0].cells
    set_lines(cells[0], [info.get("Group", "Group") + ":"] + [name.strip() for name, _, _ in members])
    set_lines(cells[1], ["MSSV:"] + [sid.replace("MSSV:", "").strip() for _, _, sid in members])
    # the sample's table has 2 lines: drop as many empty lines below it as we added, so the date stays on page 1
    # those empty lines anchor the cover frame, so they are made low instead of removed
    from docx.text.paragraph import Paragraph
    nxt = doc.tables[0]._tbl.getnext()
    while nxt is not None and not "".join(nxt.itertext()).strip().startswith("Ho Chi Minh City"):
        if nxt.tag.endswith("}p") and not "".join(nxt.itertext()).strip():
            pf = Paragraph(nxt, None).paragraph_format
            pf.space_before = pf.space_after = Pt(0)
            pf.line_spacing = Pt(8)
        nxt = nxt.getnext()


def table(doc, rows: list, caption: str) -> None:
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    try:
        t.style = doc.styles["Table Grid"]
    except KeyError:  # the sample has no table style: draw the borders
        borders = OxmlElement("w:tblBorders")
        for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
            b = OxmlElement(f"w:{side}")
            for k, v in (("val", "single"), ("sz", "4"), ("color", "000000")):
                b.set(qn(f"w:{k}"), v)
            borders.append(b)
        t._tbl.tblPr.append(borders)
    longest = [max(len(row[c]) for row in rows) for c in range(len(rows[0]))]
    t.autofit = False
    for r, row in enumerate(rows):
        for c, text in enumerate(row):
            t.cell(r, c).width = Inches(6.0 * longest[c] / sum(longest))  # wide columns for long text
            p = t.cell(r, c).paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            inline(p, text, 12, bold=r == 0)
    if caption:
        para(doc, caption, 12, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, after=6)


def figure(doc, path: str, fid: str, caption: str) -> None:
    p = para(doc, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0)
    p.add_run().add_picture(str(REPORT / path), width=Inches(5.0))
    para(doc, f"Figure {fid}: {caption}", 12, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, spacing=1.0, after=6)


def renumber(text: str, mapping: dict) -> str:
    for old, new in mapping.items():
        text = re.sub(rf"(?<![\w.]){re.escape(old)}(?=\.\d|[\s,;:)]|$)", new, text)
    return text


def write_chapter(doc, number: int, title: str, parts: list) -> list:
    sections, figures, refs = chapter(parts)
    mapping = {s["token"]: f"{number}.{k}" for k, s in enumerate(sections, 1) if s["token"]}
    placed = set()
    doc.add_paragraph(f"Chapter {number}: {title}", style="Heading 1")
    for k, s in enumerate(sections, 1):
        doc.add_paragraph(f"{number}.{k} {s['title']}", style="Heading 2")
        for block in s["blocks"]:
            if block[0] == "table":
                table(doc, block[1], renumber(block[2], mapping))
                continue
            text = block[1]
            para(doc, renumber(text, mapping), align=WD_ALIGN_PARAGRAPH.JUSTIFY)
            for fid, (path, cap) in figures.items():
                if fid not in placed and re.search(rf"Figure {re.escape(fid)}(?!\.\d|\w)", text):
                    figure(doc, path, renumber(fid, mapping), renumber(cap, mapping))
                    placed.add(fid)
    for fid, (path, cap) in figures.items():  # figures nobody mentions still appear, at the chapter end
        if fid not in placed:
            print(f"warning: Figure {fid} is not mentioned in the text of chapter {number}")
            figure(doc, path, renumber(fid, mapping), renumber(cap, mapping))
    return refs


def front_matter() -> tuple:
    sections, _, _ = parse(lines_of("front_matter_lam.md"))
    info, texts = {"Member": []}, {}
    for line in (REPORT / "front_matter_lam.md").read_text(encoding="utf-8").split("## Cover", 1)[1] \
            .split("## ", 1)[0].splitlines():
        if line.startswith("- ") and ":" in line:
            key, value = line[2:].split(":", 1)
            if key == "Member":
                info["Member"].append(value.strip())
            else:
                info[key.strip()] = value.strip()
    for s in sections:
        texts[s["title"]] = [b[1] for b in s["blocks"] if b[0] == "p"]
    return info, texts


def group_footer(doc) -> None:
    """The sample's footer already has "Group 1" and the page number: change the group only."""
    texts = doc.sections[0].footer._element.iter(qn("w:t"))
    prev = None
    for t in texts:
        if prev is not None and prev.text.strip() == "Group" and t.text.strip() == "1":
            t.text = " 2"
        prev = t


def build(out: Path = OUT) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    doc = Document(str(SAMPLE))
    body = doc.element.body
    kids = [el for el in body if not el.tag.endswith("sectPr")]
    end = next(i for i, el in enumerate(kids) if "".join(el.itertext()).strip().startswith("Ho Chi Minh City"))
    for el in kids[end + 1:]:  # keep the sample's cover, drop its example content
        body.remove(el)
    setup(doc)
    info, texts = front_matter()
    cover(doc, info)
    for title in ("Acknowledgments", "Commitment"):
        page_break(doc)
        doc.add_paragraph(title, style="Heading 1")
        for text in texts.get(title, []):
            para(doc, text, align=WD_ALIGN_PARAGRAPH.JUSTIFY)
    page_break(doc)
    para(doc, "Table of Contents", 18, True, spacing=1.0, after=6)
    field(para(doc, spacing=1.0), r'TOC \o "1-2" \h \z \u')
    refs = parse(lines_of("introduction_background_lam.md"))[2]
    for number, title, parts in CHAPTERS:
        if number == 1:  # chapters run on without page breaks: the body must fit about 10 pages
            page_break(doc)
        else:
            doc.paragraphs[-1].paragraph_format.space_after = Pt(12)
        refs += write_chapter(doc, number, title, parts)
    page_break(doc)
    doc.add_paragraph("References", style="Heading 1")
    for ref in dict.fromkeys(refs):
        p = para(doc, ref, 12, spacing=1.0, after=6)
        p.paragraph_format.left_indent, p.paragraph_format.first_line_indent = Inches(0.4), Inches(-0.4)
    group_footer(doc)
    doc.save(str(out))
    return out


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    print(f"Written: {build()}")
