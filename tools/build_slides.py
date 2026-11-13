"""The team's English slide deck for the 15-minute oral on 16/11 (owner: Lâm).

    python tools/build_slides.py        # -> docs/slides/Group2_Presentation.pptx

Built with python-pptx on the theme of Giang's deck (the MotoLogic colours and layouts Giang's and Khoa's Vietnamese
slides use). Thirteen slides: about 7 minutes of talk, a 5-minute live demo and time to change speakers; the order,
timing and demo steps are in docs/slides/lam_script.md. Figures come from docs/report/figures, the numbers from
src/evaluate.py, src/evaluate_assistant.py, src/wang.py and tools/compare_fair.py (13/11).
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
THEME_DECK = ROOT / "docs" / "slides" / "giang_forward_wang.pptx"
FIG = ROOT / "docs" / "report" / "figures"
OUT = ROOT / "docs" / "slides" / "Group2_Presentation.pptx"
FOOTER = "Group 2 · Motorbike Fault Diagnosis Expert System"

TEXT, PANEL, PANEL_SOFT, ACCENT, MUTED = "14352C", "1B3B33", "24493F", "1F6B57", "5B6B70"
SOFT, ON_DARK, LIME, WHITE, BORDER = "F2F3EC", "A9C7CE", "DDF57A", "FFFFFF", "DCE1D6"


def rgb(hex_: str) -> RGBColor:
    return RGBColor.from_string(hex_)


def text(slide, x, y, w, h, lines, size=14, color=TEXT, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         bullets=False, space=0, font=None):
    """A text box with no inner margin; `lines` is a string or a list of paragraphs."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, line in enumerate([lines] if isinstance(lines, str) else lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        if space:
            p.space_after = Pt(space)
        if bullets:
            pPr = p._p.get_or_add_pPr()
            pPr.set("marL", str(Inches(0.25)))
            pPr.set("indent", str(-Inches(0.25)))
            pPr.append(pPr.makeelement(qn("a:buChar"), {"char": "•"}))
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)
        if font:
            run.font.name = font
    return box


def card(slide, x, y, w, h, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    shape.adjustments[0] = 0.06
    shape.fill.solid()
    shape.fill.fore_color.rgb = rgb(fill)
    if line:
        shape.line.color.rgb = rgb(line)
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    shape.shadow.inherit = False
    return shape


def step(slide, n, x, y, head, body, w=4.6):
    """Numbered step as on Giang's and Khoa's slides: a green circle, a bold head and a muted line."""
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.55), Inches(0.55))
    dot.fill.solid()
    dot.fill.fore_color.rgb = rgb(ACCENT)
    dot.line.fill.background()
    dot.shadow.inherit = False
    text(slide, x, y, 0.55, 0.55, str(n), 16, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(slide, x + 0.8, y - 0.02, w, 0.4, head, 18, TEXT, True)
    text(slide, x + 0.8, y + 0.4, w, 0.9, body, 14, MUTED)


def picture(slide, path, x, y, w, h, border=False):
    """The image fitted inside the box (x, y, w, h), centred horizontally, aspect kept."""
    iw, ih = Image.open(path).size
    scale = min(w / iw, h / ih)
    pw, ph = iw * scale, ih * scale
    pic = slide.shapes.add_picture(str(path), Inches(x + (w - pw) / 2), Inches(y), Inches(pw), Inches(ph))
    if border:
        pic.line.color.rgb = rgb(BORDER)
        pic.line.width = Pt(1)
    return pic


def stat(slide, x, y, w, h, number, label, dark=False):
    card(slide, x, y, w, h, PANEL if dark else SOFT)
    text(slide, x + 0.25, y + 0.15, w - 0.5, 0.6, number, 28, LIME if dark else ACCENT, True)
    text(slide, x + 0.25, y + 0.8, w - 0.5, h - 0.9, label, 13, ON_DARK if dark else MUTED)


def new_slide(prs, layout, title, notes, subtitle=None):
    s = prs.slides.add_slide(next(l for l in prs.slide_layouts if l.name == layout))
    phs = {ph.placeholder_format.idx: ph for ph in s.placeholders}
    phs[100].text = title
    if subtitle is not None:
        phs[101].text = subtitle
    for ph in phs.values():  # as on Giang's and Khoa's slides: no inner margin, title centred in its box
        tf = ph.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE if layout == "CONTENT" else MSO_ANCHOR.TOP
    s.notes_slide.notes_text_frame.text = notes
    return s


def slides(prs) -> None:
    # 1. Title (Lâm) -------------------------------------------------------------------------------------------
    s = new_slide(prs, "DARK", "Motorbike Fault Diagnosis Expert System",
                  "Lâm: Good morning. We are Group 2, and our project is a rule-based expert system that diagnoses "
                  "common motorbike faults.",
                  "Group 2 · Introduction to Artificial Intelligence (261_72ITSE30303_01) · Lecturer: Dr. Nguyen Thanh Huy")
    text(s, 0.8, 5.6, 11.7, 0.4, "Tăng Thoại Lâm  ·  Kiều Bảo Giang  ·  Nguyễn Nam Khoa", 16, LIME, True)

    # 2. Team and tasks (Lâm) ----------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Team and tasks",
                  "Lâm: Our team has three members. I led the team and built the knowledge base, the bike-model data, "
                  "the MotoLogic interface, the executable and the chat assistant. Giang built forward chaining, the "
                  "certainty factors and Wang's prover, and designed the MotoLogic screens. Khoa built backward "
                  "chaining with its explanations, the step-by-step screen and the evaluation.")
    team = [("Tăng Thoại Lâm", "Team leader · 2474802010210",
             ["Knowledge base: 79 symptoms, 40 faults, 88 rules with sources", "Six bike models and owner's-manual specs",
              "MotoLogic interface, CLI and .exe", "Diagnosis assistant and rule-based chat"],
             "Report: Ch. 1, 2, 3.1, 3.5, 6; merged report and slides"),
            ("Kiều Bảo Giang", "Member · 2474802010095",
             ["Forward chaining engine", "Certainty factors (MYCIN)", "Wang's algorithm prover",
              "MotoLogic design and By-symptoms screen"],
             "Report: Ch. 3.2, 3.3, 5"),
            ("Nguyễn Nam Khoa", "Member · 2474802010194",
             ["Backward chaining engine", "Why / how explanations", "Step-by-step screen",
              "Evaluation on 30 scenarios, charts"],
             "Report: Ch. 3.4, 4")]
    for i, (name, line, tasks, report) in enumerate(team):
        x, dark = 0.6 + i * 4.13, i == 0
        card(s, x, 1.4, 3.9, 4.6, PANEL if dark else SOFT)
        text(s, x + 0.3, 1.6, 3.3, 0.45, name, 20, WHITE if dark else TEXT, True)
        text(s, x + 0.3, 2.05, 3.3, 0.3, line, 12, ON_DARK if dark else MUTED)
        text(s, x + 0.3, 2.6, 3.3, 2.4, tasks, 15, WHITE if dark else TEXT, bullets=True, space=8)
        text(s, x + 0.3, 5.15, 3.3, 0.7, report, 13, LIME if dark else ACCENT, True)

    # 3. Contents (Lâm) ----------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Contents",
                  "Lâm: I start with the problem and the architecture. Giang then presents forward chaining, "
                  "certainty factors and Wang's algorithm, and Khoa backward chaining and the evaluation. I present "
                  "the diagnosis assistant, then we show the program live and conclude.")
    agenda = [("Problem and architecture", "Lâm", "2:00"), ("Forward chaining, CF, Wang", "Giang", "1:45"),
              ("Backward chaining and evaluation", "Khoa", "1:45"), ("Diagnosis assistant and chat", "Lâm", "0:45"),
              ("Live demo", "All", "5:00"), ("Conclusion and questions", "Lâm", "0:45")]
    for i, (part, who, mins) in enumerate(agenda):
        x, y = 0.6 + (i % 2) * 6.2, 1.45 + (i // 2) * 1.65
        demo = part == "Live demo"
        card(s, x, y, 5.95, 1.4, PANEL if demo else SOFT)
        text(s, x + 0.3, y + 0.2, 0.9, 1.0, f"{i + 1:02d}", 32, LIME if demo else ACCENT, True)
        text(s, x + 1.35, y + 0.25, 4.3, 0.45, part, 18, WHITE if demo else TEXT, True)
        text(s, x + 1.35, y + 0.75, 4.3, 0.4, f"{who} · {mins}", 14, ON_DARK if demo else MUTED)

    # 2. Problem (Lâm) -----------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "The problem: riders only see symptoms",
                  "Lâm: Viet Nam has about 74 million motorbikes, more than it has adults. When one breaks down, the "
                  "rider only sees symptoms, and the same 'it won't start' can be a flat battery or a fault for a "
                  "mechanic. Our system ranks the likely faults by certainty factor, says which ones need a mechanic, "
                  "and explains every conclusion with its rules. The knowledge base has 79 symptoms, 40 faults in six "
                  "subsystems and 88 rules, each with a CF and a source, plus specs for six popular models.")
    text(s, 0.6, 1.45, 5.9, 1.0, "74 million", 54, ACCENT, True)
    text(s, 0.6, 2.45, 5.6, 0.7, "motorbikes in Viet Nam, more than it has adults (WHO, 2024)", 14, MUTED)
    text(s, 0.6, 3.3, 5.6, 1.0, "The same “it won't start” can be a flat battery or a fault for a mechanic.", 16)
    text(s, 0.6, 4.45, 5.6, 0.4, "Goals", 18, TEXT, True)
    text(s, 0.6, 4.9, 5.6, 1.5, ["Rank the likely faults by certainty factor (CF)", "Say which faults need a mechanic",
                                 "Explain every conclusion with its rules"], 14, MUTED, bullets=True, space=4)
    for i, (num, label, desc, dark) in enumerate([
            ("79", "symptoms", "yes / no questions in Vietnamese and English", False),
            ("40", "faults", "6 subsystems, each with a severity and an action", False),
            ("88", "rules", "IF … THEN, each with a CF and a source", True),
            ("6", "bike models", "Vision, Air Blade, Lead, Wave, Future, Exciter", False)]):
        x, y = 6.9 + (i % 2) * 2.95, 1.4 + (i // 2) * 2.6
        card(s, x, y, 2.8, 2.4, PANEL if dark else SOFT)
        text(s, x + 0.25, y + 0.2, 2.3, 0.9, num, 40, LIME if dark else ACCENT, True)
        text(s, x + 0.25, y + 1.1, 2.3, 0.35, label, 16, WHITE if dark else TEXT, True)
        text(s, x + 0.25, y + 1.5, 2.3, 0.8, desc, 12, ON_DARK if dark else MUTED)

    # 3. Architecture (Lâm) ------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "One knowledge base, three ways to reason",
                  "Lâm: The knowledge base is one JSON file per subsystem, and a rule checker reports duplicate rules, "
                  "unused symbols, missing sources and cycles; it reports none. The same rules drive forward chaining, "
                  "backward chaining and the chat assistant, and Wang's algorithm proves the conclusions "
                  "independently. The program is a desktop app, MotoLogic, that runs offline. Giang, please.")
    picture(s, FIG / "fig_system_overview.png", 0.9, 1.4, 11.5, 4.4)
    text(s, 0.9, 5.9, 11.5, 0.7, "One JSON file per subsystem. The rule checker reports duplicate rules, unused symbols, "
                                 "missing sources and cycles: 0 errors, 0 warnings.", 14, MUTED)

    # 4. Forward chaining and CF (Giang) -----------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Forward chaining ranks faults by certainty",
                  "Giang: Forward chaining is data-driven. Each rule counts its unproved premises, and when the count "
                  "reaches zero the rule fires and its conclusion joins the agenda, as in PL-FC-ENTAILS in the "
                  "textbook. To rank faults we use MYCIN certainty factors: premises joined by AND take the minimum, "
                  "a rule multiplies that by its own CF, and rules with the same conclusion combine as CF1 plus CF2 "
                  "times one minus CF1. For a weak battery three rules give 0.765, 0.675 and 0.54, which combine to "
                  "0.96. Faults with a CF of at least 0.2 are reported, best first.")
    for i, (head, body) in enumerate([
            ("Facts in, rules fire", "Each rule counts its unproved premises; at zero it fires (PL-FC-ENTAILS, AIMA ch. 7)."),
            ("MYCIN certainty factors", "AND: min CF of the premises. Rule: its CF × that. Same conclusion: "
                                        "CF1 + CF2 × (1 − CF1)."),
            ("Report", "Faults with CF ≥ 0.20, best first.")]):
        step(s, i + 1, 0.6, 1.55 + i * 1.6, head, body, w=4.4)
    picture(s, FIG / "fig_cf_example.png", 6.3, 1.5, 6.45, 4.6)
    text(s, 6.3, 5.95, 6.45, 0.6, "Scenario SE01: SF01, then SF02, SF03 and SF14 combined to CF 0.96.", 13, MUTED)

    # 5. Wang (Giang) ------------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Wang's algorithm checks the reasoning",
                  "Giang: Our inference engine is our own code, so it could be wrong. We check it with Wang's "
                  "algorithm, an independent theorem prover. Each rule becomes an implication, each yes answer an "
                  "atom, and Wang removes one connective at a time until every branch has the same atom on both "
                  "sides. Forward chaining is sound and complete for definite clauses, so both must find the same "
                  "faults. On 30 scenarios and 500 random symptom sets, more than 21,000 comparisons, they never "
                  "disagree. The first run failed two scenarios, and Wang failed them too, so rules were missing: "
                  "four fallback rules fixed them. Khoa, please.")
    card(s, 0.6, 1.45, 6.0, 1.2, SOFT)
    text(s, 0.85, 1.6, 5.5, 0.3, "The question for Wang", 13, MUTED)
    text(s, 0.85, 1.95, 5.5, 0.6, "rules, answers  ⇒  fault", 24, ACCENT, True, font="Consolas")
    text(s, 0.6, 2.95, 6.0, 2.6, ["Each rule becomes (p1 ∧ … ∧ pk) → q; each “yes” is an atom.",
                                  "Wang removes one connective at a time until every branch is an axiom.",
                                  "Forward chaining is sound and complete for definite clauses, so both must find "
                                  "the same faults."], 15, TEXT, bullets=True, space=10)
    stat(s, 7.1, 1.45, 5.63, 2.05, "0 disagreements", "between Wang and forward chaining on 30 scenarios and 500 random "
                                                       "symptom sets (21,200 comparisons)", dark=True)
    stat(s, 7.1, 3.75, 5.63, 2.05, "28/30 → 30/30", "the two failures were missing rules, not engine bugs; four fallback "
                                                    "rules for “dead-end” intermediate facts fixed them")

    # 6. Backward chaining (Khoa) ------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Backward chaining asks only what it needs",
                  "Khoa: Backward chaining is goal-driven. Each fault of the part the rider chooses is a hypothesis. "
                  "For every rule that concludes it, the premises become sub-goals; an intermediate fact is proved "
                  "the same way, and a symptom is asked once and remembered. A rule is dropped at its first false "
                  "premise, so questions that cannot change the result are never asked. All rules of a goal are "
                  "combined with the same CF formulas, so the result equals forward chaining. 'Why' shows the rule "
                  "chain to the current question, and 'how' shows the facts and rules behind a fault.")
    for i, (head, body) in enumerate([
            ("Pick a hypothesis", "Each fault of the chosen part is a goal to prove."),
            ("Work back through the rules", "Premises become sub-goals; intermediate facts are proved the same way."),
            ("Ask, remember, prune", "A symptom is asked once; a false premise drops the rule.")]):
        step(s, i + 1, 0.6, 1.55 + i * 1.45, head, body, w=4.4)
    text(s, 0.6, 5.95, 5.4, 0.7, "Why: the rule chain to this question.  How: the facts and rules behind a fault.",
         14, ACCENT, True)
    picture(s, FIG / "fig_backward_flow.png", 6.3, 1.45, 6.45, 5.0)

    # 7. Evaluation (Khoa) -------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Evaluation on 30 scenarios",
                  "Khoa: We tested 30 scenarios, ten per subsystem group, each written by a member who did not write "
                  "the rules. Both engines rank the expected fault first in all 30, with the same CFs. Backward "
                  "chaining over every part asks 39.7 questions; if the rider picks the part first it asks 9, four "
                  "times fewer. The assistant asks 5.5, but those descriptions were used to write its phrase list; on "
                  "ten new descriptions it is right 8 times in Vietnamese and 7 in English. Read the same description, "
                  "backward chaining still asks 36.3, so the assistant is fast mostly because it picks good questions "
                  "and stops early.")
    data = CategoryChartData()
    data.categories = ["Assistant, with description", "Backward, right part first", "Backward, every part"]
    data.add_series("Mean questions", (5.5, 9.0, 39.7))
    chart = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(0.6), Inches(1.4), Inches(6.4), Inches(4.4),
                               data).chart
    chart.has_legend = False
    chart.has_title = True
    chart.chart_title.text_frame.text = "Mean questions asked (30 scenarios)"
    chart.chart_title.text_frame.paragraphs[0].runs[0].font.size = Pt(14)
    chart.chart_title.text_frame.paragraphs[0].runs[0].font.color.rgb = rgb(MUTED)
    plot = chart.plots[0]
    plot.gap_width = 60
    plot.has_data_labels = True
    plot.data_labels.font.size = Pt(13)
    plot.data_labels.font.color.rgb = rgb(TEXT)
    plot.data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
    plot.data_labels.number_format = "0.0"
    plot.data_labels.number_format_is_linked = False
    plot.series[0].format.fill.solid()
    plot.series[0].format.fill.fore_color.rgb = rgb(ACCENT)
    chart.value_axis.visible = False
    chart.value_axis.has_major_gridlines = False
    chart.value_axis.maximum_scale = 45
    chart.category_axis.tick_labels.font.size = Pt(13)
    chart.category_axis.tick_labels.font.color.rgb = rgb(TEXT)
    chart.category_axis.format.line.color.rgb = rgb(BORDER)
    stat(s, 7.4, 1.4, 5.33, 1.35, "30/30", "top-1 with forward and backward chaining, same CFs", dark=True)
    stat(s, 7.4, 2.9, 5.33, 1.35, "9.0 questions", "when the rider picks the part first: 4.4× fewer than 39.7")
    stat(s, 7.4, 4.4, 5.33, 1.35, "8/10 · 7/10", "assistant on 10 new descriptions (Vietnamese / English)")
    text(s, 0.6, 6.0, 12.1, 0.6, "Fair comparison: reading the same description, backward chaining still asks 36.3; "
                                 "stopping at the first proved fault gives 22.2 (28/30).", 13, MUTED)

    # 8. Assistant and chat (Lâm) ------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "The assistant: words in, rule-based answers out",
                  "Lâm: The third way is to describe the problem in words. A phrase matcher reads the symptoms, "
                  "without accents and with negation. The assistant then asks the question with the largest expected "
                  "information gain and stops when the leading fault is proved; the final ranking still comes from "
                  "forward chaining. While it asks, the rider can ask back: why, how do you know, how to fix it, what "
                  "else. There are no canned replies: every answer is built from the rules, the questions and the CFs. "
                  "Its weak point is language: it only understands phrasings in its phrase list.")
    picture(s, FIG / "fig_motologic_chat.png", 0.6, 1.4, 6.6, 4.4, border=True)
    text(s, 0.6, 5.55, 6.6, 0.4, "The rider asks “why?” and gets the rule SF01 with each premise marked.", 13, MUTED)
    for i, (head, body) in enumerate([
            ("Read the description", "Phrase matching without accents, with negation."),
            ("Ask the most informative question", "Largest expected information gain; stop when the leader is proved."),
            ("Answer from the rules", "why? how? how to fix? what else? Every reply quotes the rules.")]):
        step(s, i + 1, 7.6, 1.5 + i * 1.45, head, body, w=4.3)
    text(s, 7.6, 5.95, 5.1, 0.6, "5.5 questions · 30/30 on the 30 scenarios", 16, ACCENT, True)

    # 9. Live demo (all) ---------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Live demo (5 minutes)",
                  "Lâm: Now the live demo, about five minutes, in the English interface of MotoLogic. Each of us "
                  "shows one way to diagnose. If MotoLogic fails, we use the classic screens, Control 5 and "
                  "Control 6, with the same scenarios.")
    for i, (who, way, steps, shows) in enumerate([
            ("Lâm", "Describe it in words", ["Honda Vision → Describe it in words",
                                             "“the starter only clicks, the horn is weak”", "ask “why?”, answer “yes”",
                                             "See the full result"],
             "Rule-based replies; the Vision's battery spec from its owner's manual"),
            ("Giang", "I know my symptoms", ["Another bike → I know my symptoms", "starter only clicks, weak horn, "
                                             "battery over 2 years", "See the result", "Click “Cross-check” (Wang)"],
             "Weak or flat battery, confidence 89%; Wang proves it"),
            ("Khoa", "Guide me with questions", ["Guide me with questions → Brakes", "yes: soft lever, fluid below MIN",
                                                 "“Why this question?” at question 3", "Answer to the end (9 questions)"],
             "Brake fluid leak, CF 0.96, take it to a mechanic")]):
        x = 0.6 + i * 4.13
        card(s, x, 1.4, 3.9, 4.65, SOFT)
        text(s, x + 0.3, 1.6, 3.3, 0.35, who, 13, MUTED, True)
        text(s, x + 0.3, 1.95, 3.3, 0.45, way, 18, ACCENT, True)
        text(s, x + 0.3, 2.55, 3.3, 2.2, steps, 14, TEXT, bullets=True, space=6)
        card(s, x + 0.2, 4.6, 3.5, 1.25, WHITE)
        text(s, x + 0.4, 4.72, 3.1, 0.3, "Shows", 12, MUTED, True)
        text(s, x + 0.4, 5.02, 3.1, 0.8, shows, 13, ACCENT, True)
    text(s, 0.6, 6.2, 12.1, 0.4, "Backup: the classic screens (Ctrl+5 By symptoms, Ctrl+6 Step-by-step) with the same "
                                 "scenarios.", 13, MUTED)

    # 10. Conclusion (Lâm) -------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Conclusion",
                  "Lâm: To sum up, both chaining directions rank the expected fault first in all 30 scenarios, Wang "
                  "agrees with forward chaining every time, choosing the part first cuts the questions from 39.7 to 9, "
                  "and every answer can be traced to its rules. The limits: rules have only positive premises, so a "
                  "'no' cannot lower a CF; the chat only knows the phrasings in its list; and the CFs and scenarios "
                  "were written by our team. Next we would add negative evidence, phrases from real repair logs and "
                  "CFs measured on real repairs.")
    for i, (head, items, dark) in enumerate([
            ("Achieved", ["30/30 scenarios ranked first, forward and backward", "Wang agrees with forward chaining: "
                          "0 disagreements", "Part first: 9.0 questions instead of 39.7",
                          "Every answer traced to its rules"], True),
            ("Limits", ["A “no” cannot lower a CF (positive premises only)", "The chat knows only the phrasings in "
                        "its list", "CFs and scenarios written by the team"], False),
            ("Next", ["Negative evidence", "Phrases from real repair logs", "CFs measured on real repairs"], False)]):
        x = 0.6 + i * 4.13
        card(s, x, 1.4, 3.9, 4.5, PANEL if dark else SOFT)
        text(s, x + 0.3, 1.65, 3.3, 0.45, head, 20, LIME if dark else ACCENT, True)
        text(s, x + 0.3, 2.3, 3.3, 3.4, items, 14, WHITE if dark else TEXT, bullets=True, space=8)
    text(s, 0.6, 6.1, 12.1, 0.5, "Rules that explain themselves give riders a first diagnosis they can check.", 15,
         TEXT, True)

    # 11. Thanks -----------------------------------------------------------------------------------------------
    s = new_slide(prs, "DARK", "Thank you for listening",
                  "Lâm: Thank you for listening. We are happy to take your questions.",
                  "Questions are welcome")
    for i, (name, sid) in enumerate([("Tăng Thoại Lâm", "2474802010210"), ("Kiều Bảo Giang", "2474802010095"),
                                     ("Nguyễn Nam Khoa", "2474802010194")]):
        x = 0.8 + i * 3.95
        card(s, x, 5.35, 3.75, 1.0, PANEL_SOFT)
        text(s, x + 0.25, 5.5, 3.3, 0.35, name, 16, WHITE, True)
        text(s, x + 0.25, 5.88, 3.3, 0.3, "Student ID " + sid, 12, ON_DARK)
    text(s, 0.8, 6.55, 11.7, 0.35, "Group 2 · MotorbikeExpert.exe runs offline on Windows", 12, ON_DARK)


def drop_slides(prs) -> None:
    ids = prs.slides._sldIdLst
    for sid in list(ids):
        prs.part.drop_rel(sid.rId)
        ids.remove(sid)


def neutral_footer(prs) -> None:
    for layout in prs.slide_layouts:
        for shape in layout.shapes:
            if shape.has_text_frame and shape.text_frame.text.startswith("Nhóm 2 ·"):
                shape.text_frame.paragraphs[0].runs[0].text = FOOTER


def slide_numbers(prs, template) -> None:
    """Content slides get the slide-number box that Giang's slides carry (python-pptx does not add it)."""
    import copy
    num = next(sh for sh in template.slides[1].shapes if sh.is_placeholder and sh.placeholder_format.type == 13)
    for slide in prs.slides:
        if slide.slide_layout.name == "CONTENT":
            slide.shapes._spTree.append(copy.deepcopy(num._element))


def build(out: Path = OUT) -> Path:
    template = Presentation(str(THEME_DECK))
    prs = Presentation(str(THEME_DECK))
    drop_slides(prs)
    neutral_footer(prs)
    slides(prs)
    slide_numbers(prs, template)
    assert len(prs.slides) == 13, len(prs.slides)
    prs.save(str(out))
    return out


if __name__ == "__main__":
    print("Written:", build())
    sys.exit(0)
