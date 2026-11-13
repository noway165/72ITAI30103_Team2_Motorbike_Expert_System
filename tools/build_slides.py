"""The team's slide deck for the oral on 16/11 (owner: Lâm).

    python tools/build_slides.py        # -> docs/slides/nhom2_thuyet_trinh.pptx

Lâm's slides are drawn on the theme of Giang's deck (same colours and layouts as Giang's and Khoa's slides), then
PowerPoint (Windows) inserts docs/slides/giang_forward_wang.pptx and khoa_backward_eval.pptx between them. Last, the
numbers that changed since 12/11 are corrected and the two old screenshots are replaced. Needs python-pptx.
Order: Lâm 1-4 (opening), Giang 5-10, Khoa 11-15, Lâm 16-19 (assistant, chat, conclusion).
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
SLIDES = ROOT / "docs" / "slides"
IMG = SLIDES / "img"
GIANG, KHOA = SLIDES / "giang_forward_wang.pptx", SLIDES / "khoa_backward_eval.pptx"
OUT = SLIDES / "nhom2_thuyet_trinh.pptx"
FOOTER = "Nhóm 2 · Hệ chuyên gia chẩn đoán lỗi xe máy"
OPENING = 4  # Lâm's slides before Giang's part

TEXT, PANEL, PANEL_SOFT, ACCENT, MUTED = "14352C", "1B3B33", "24493F", "1F6B57", "5B6B70"
SOFT, LIME_SOFT, LIME, ON_DARK, WHITE = "F2F3EC", "EEF7CF", "DDF57A", "A9C7CE", "FFFFFF"

# Numbers in Giang's and Khoa's decks of 12/11 that the final knowledge base changed (python src/evaluate.py,
# src/evaluate_assistant.py, tools/compare_fair.py on 13/11).
FIXES = [
    ("(79 luật)", "(88 luật)"),
    ("Luật dự phòng: SF14, TS15, BR13, EN17, EN18, TR12.", "Luật dự phòng: SF14, TS15, BR13, EN18."),
    ("như SF14 của Lâm, TS15 và BR13 của Khoa, EN17, EN18, TR12 của em", "như SF14 của Lâm, TS15 và BR13 của Khoa, EN18 của em"),
    ("5,8 câu · 27/30", "5,5 câu · 30/30"),
    ("Trợ lý: ít câu nhất nhưng sót 3 lỗi phanh, giảm xóc", "Trợ lý: ít câu nhất; 10 mô tả mới: đúng 8/10"),
    ("36,6", "36,3"),
    ("39,7 câu trên 73 triệu chứng", "39,7 câu trên 79 triệu chứng"),
    ("chỉ cần 5,8 câu nhưng đúng 27 trên 30, sót các lỗi phanh và giảm xóc có một triệu chứng mà mô tả không nhắc tới",
     "chỉ cần 5,5 câu và đúng cả 30, nhưng với 10 mô tả mới chưa từng dùng để viết bộ đọc thì đúng 8 trên 10"),
]


def rgb(hex_: str) -> RGBColor:
    return RGBColor.from_string(hex_)


def text(slide, x, y, w, h, lines, size=14, color=TEXT, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         bullets=False, space=0):
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
            bu = pPr.makeelement(qn("a:buChar"), {"char": "•"})
            pPr.append(bu)
        run = p.add_run()
        run.text = line
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = rgb(color)
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
    dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(0.6), Inches(0.6))
    dot.fill.solid()
    dot.fill.fore_color.rgb = rgb(ACCENT)
    dot.line.fill.background()
    dot.shadow.inherit = False
    text(slide, x, y, 0.6, 0.6, str(n), 18, WHITE, True, PP_ALIGN.CENTER, MSO_ANCHOR.MIDDLE)
    text(slide, x + 0.85, y - 0.02, w, 0.4, head, 18, TEXT, True)
    text(slide, x + 0.85, y + 0.42, w, 0.95, body, 14, MUTED)


def picture(slide, path, x, y, w=None, h=None, border=True):
    pic = slide.shapes.add_picture(str(path), Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)
    if border:
        pic.line.color.rgb = rgb("DCE1D6")
        pic.line.width = Pt(1)
    return pic


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


def lam_slides(prs) -> None:
    # 1. Title -------------------------------------------------------------------------------------------------
    s = new_slide(prs, "DARK", "Hệ chuyên gia chẩn đoán lỗi xe máy",
                  "Em chào thầy. Em là Tăng Thoại Lâm, nhóm trưởng nhóm 2. Đề tài của nhóm là hệ chuyên gia chẩn đoán "
                  "các lỗi thường gặp của xe máy. Em mở đầu bằng bài toán, kiến trúc và giao diện; bạn Giang trình bày "
                  "suy diễn tiến, hệ số chắc chắn và thuật toán Wang; bạn Khoa trình bày suy diễn lùi và đánh giá; "
                  "cuối cùng em trình bày trợ lý chẩn đoán, phần chat và kết luận.",
                  "Nhóm 2 · Nhập môn Trí tuệ nhân tạo (261_72ITSE30303_01) · GV: TS. Nguyễn Thanh Huy")
    members = [("Tăng Thoại Lâm", "2474802010210", "Cơ sở tri thức, giao diện, trợ lý chat"),
               ("Kiều Bảo Giang", "2474802010095", "Suy diễn tiến, CF, thuật toán Wang"),
               ("Nguyễn Nam Khoa", "2474802010194", "Suy diễn lùi, giải thích, đánh giá")]
    for i, (name, sid, role) in enumerate(members):
        x = 0.8 + i * 3.95
        card(s, x, 5.35, 3.75, 1.3, PANEL_SOFT)
        text(s, x + 0.25, 5.5, 3.3, 0.35, name, 16, WHITE, True)
        text(s, x + 0.25, 5.85, 3.3, 0.3, "MSSV " + sid, 12, ON_DARK)
        text(s, x + 0.25, 6.15, 3.3, 0.35, role, 12, LIME)

    # 2. Problem -----------------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Bài toán: xe hỏng, người lái chỉ có triệu chứng",
                  "Việt Nam có khoảng 74 triệu xe máy, nhiều hơn số người trưởng thành, theo WHO năm 2024. Khi xe hỏng, "
                  "người lái chỉ biết triệu chứng: cùng là đề không nổ, có khi chỉ cần sạc ắc quy, có khi lại là lỗi "
                  "phải mang ra thợ. Nhóm xây hệ chuyên gia dựa trên luật với ba mục tiêu: xếp hạng lỗi theo độ tin "
                  "cậy, báo lỗi nào tự xử lý được và lỗi nào cần thợ, và giải thích mọi kết luận bằng luật. Cơ sở tri "
                  "thức có 79 triệu chứng, 40 lỗi trong 6 bộ phận và 88 luật, mỗi luật có CF và nguồn; ngoài ra có luật "
                  "và thông số riêng cho 6 dòng xe phổ biến.")
    text(s, 0.6, 1.45, 5.9, 1.0, "74 triệu", 54, ACCENT, True)
    text(s, 0.6, 2.45, 5.6, 0.7, "xe máy ở Việt Nam, nhiều hơn số người trưởng thành (WHO, 2024)", 14, MUTED)
    text(s, 0.6, 3.3, 5.6, 1.0, "Cùng là “đề không nổ”: có khi chỉ cần sạc ắc quy, có khi là lỗi phải mang ra thợ.",
         16, TEXT)
    text(s, 0.6, 4.45, 5.6, 0.4, "Mục tiêu", 18, TEXT, True)
    text(s, 0.6, 4.9, 5.6, 1.5, ["Xếp hạng lỗi theo độ tin cậy (CF)", "Báo lỗi tự xử lý được hay cần mang ra thợ",
                                 "Giải thích mọi kết luận bằng luật"], 14, MUTED, bullets=True, space=4)
    stats = [("79", "triệu chứng", "câu hỏi Có / Không, tiếng Việt và tiếng Anh", SOFT),
             ("40", "lỗi", "6 bộ phận, mỗi lỗi có mức độ và cách xử lý", SOFT),
             ("88", "luật", "NẾU … THÌ …, mỗi luật có CF và nguồn", PANEL),
             ("6", "dòng xe", "Vision, Air Blade, Lead, Wave, Future, Exciter", SOFT)]
    for i, (num, label, desc, fill) in enumerate(stats):
        x, y = 6.9 + (i % 2) * 2.95, 1.4 + (i // 2) * 2.6
        dark = fill == PANEL
        card(s, x, y, 2.8, 2.4, fill)
        text(s, x + 0.25, y + 0.2, 2.3, 0.9, num, 40, LIME if dark else ACCENT, True)
        text(s, x + 0.25, y + 1.1, 2.3, 0.35, label, 16, WHITE if dark else TEXT, True)
        text(s, x + 0.25, y + 1.5, 2.3, 0.8, desc, 12, ON_DARK if dark else MUTED)

    # 3. Architecture ------------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Kiến trúc: một cơ sở tri thức, ba cách suy luận",
                  "Đây là kiến trúc của hệ thống. Cơ sở tri thức là các file JSON, mỗi bộ phận một file. Bộ kiểm tra "
                  "luật, hiện ở màn Cơ sở tri thức, báo luật trùng, ký hiệu không dùng, thiếu nguồn hay vòng lặp; "
                  "hiện tại không có lỗi nào. Cùng một bộ luật được dùng cho suy diễn tiến, suy diễn lùi và trợ "
                  "lý chat. Thuật toán Wang chứng minh lại kết luận một cách độc lập. Giao diện gồm GUI MotoLogic, "
                  "CLI và file exe chạy offline.")
    picture(s, ROOT / "docs" / "report" / "figures" / "fig_system_overview.png", 1.1, 1.4, w=11.1, border=False)
    text(s, 1.1, 5.85, 11.1, 0.8, "Mỗi bộ phận một file JSON. Bộ kiểm tra luật báo luật trùng, ký hiệu không dùng, "
                                  "thiếu nguồn và vòng lặp: hiện 0 lỗi, 0 cảnh báo.", 14, MUTED)

    # 4. MotoLogic ---------------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "MotoLogic: ba bước, ba cách chẩn đoán",
                  "Giao diện MotoLogic có ba bước. Bước một chọn dòng xe, hoặc loại xe và kiểu cấp xăng nếu là xe khác, "
                  "rồi chọn một trong ba cách chẩn đoán. Hỏi đáp từng câu dùng suy diễn lùi, phần của Khoa. Chọn triệu "
                  "chứng dùng suy diễn tiến, phần của Giang. Kể bằng lời là trợ lý chat, phần của em. Cả ba cùng ra "
                  "một màn kết quả: lỗi đứng đầu, độ tin cậy, chuỗi luật, cách xử lý, thông số theo sách hướng dẫn "
                  "của dòng xe và kiểm chứng Wang. Mời bạn Giang.")
    picture(s, IMG / "motologic_setup_vi.png", 0.6, 1.4, w=7.3)
    text(s, 0.6, 5.7, 7.3, 0.8, "Kết quả chung: lỗi đứng đầu, độ tin cậy, chuỗi luật, cách xử lý, thông số theo sách "
                                "hướng dẫn của dòng xe và kiểm chứng Wang.", 14, MUTED)
    for i, (head, body) in enumerate([("Hỏi đáp từng câu", "Suy diễn lùi, hỏi Có / Không, giải thích “tại sao” (Khoa)"),
                                      ("Tôi biết triệu chứng", "Suy diễn tiến, xếp hạng bằng CF, kiểm chứng Wang (Giang)"),
                                      ("Kể bằng lời", "Trợ lý đọc lời kể và trò chuyện theo luật (Lâm)")]):
        step(s, i + 1, 8.35, 1.55 + i * 1.65, head, body, w=3.55)


def lam_closing(prs) -> None:
    # 16. Assistant --------------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Trợ lý chẩn đoán: đọc lời kể, chỉ hỏi câu đáng hỏi",
                  "Cách thứ ba là kể bằng lời. Bộ đọc so khớp cụm từ trong câu kể, bỏ dấu và hiểu phủ định, để lấy ra "
                  "các triệu chứng. Sau đó trợ lý không hỏi lần lượt như suy diễn lùi mà chọn câu có information gain "
                  "lớn nhất, tức là câu chia các lỗi còn lại tốt nhất, và dừng khi lỗi đứng đầu đã được luật chứng "
                  "minh. Kết luận cuối vẫn do suy diễn tiến và CF đưa ra. Trên 30 kịch bản, trợ lý cần trung bình 5,5 "
                  "câu và đúng cả 30. Nhưng các mô tả này đã dùng khi viết bộ đọc, nên nhóm thử thêm 10 mô tả mới: "
                  "đúng 8 trên 10 với tiếng Việt và 7 với tiếng Anh. Đây là điểm yếu chính: bộ đọc chỉ hiểu cụm từ có "
                  "trong danh sách.")
    for i, (head, body) in enumerate([
            ("Đọc lời kể", "So khớp cụm từ, bỏ dấu, hiểu phủ định (“không có mùi xăng”)."),
            ("Hỏi câu có information gain lớn nhất", "Câu chia các lỗi còn lại tốt nhất; dừng khi lỗi đầu đã được "
                                                      "luật chứng minh."),
            ("Kết luận bằng luật", "Xếp hạng cuối do suy diễn tiến và CF; Wang kiểm chứng.")]):
        step(s, i + 1, 0.6, 1.55 + i * 1.65, head, body, w=4.9)
    card(s, 6.6, 1.35, 6.13, 5.2, PANEL)
    text(s, 6.95, 1.6, 5.5, 0.35, "Kết quả (python src/evaluate_assistant.py)", 13, ON_DARK)
    for i, (num, desc) in enumerate([("5,5 câu · 30/30", "30 kịch bản, mô tả tiếng Việt hoặc tiếng Anh; suy diễn lùi "
                                                         "hỏi mọi bộ phận cần 39,7 câu"),
                                     ("8/10 · 7/10", "10 mô tả mới, chưa từng dùng khi viết bộ đọc (Việt / Anh)"),
                                     ("9/9", "kịch bản theo dòng xe: luật riêng MD01–MD09 xếp đúng hạng 1")]):
        y = 2.1 + i * 1.45
        text(s, 6.95, y, 5.5, 0.6, num, 30, LIME, True)
        text(s, 6.95, y + 0.62, 5.5, 0.7, desc, 13, ON_DARK)

    # 17. Chat -------------------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Chat theo luật: câu trả lời nào cũng chỉ ra luật",
                  "Trong lúc hỏi, người lái có thể hỏi lại trợ lý. Không có câu trả lời soạn sẵn: mỗi câu được ghép "
                  "từ luật, câu hỏi và CF trong cơ sở tri thức. Hỏi tại sao thì trợ lý liệt kê các luật dùng câu đang "
                  "hỏi, điều kiện nào đã có, điều kiện nào đang hỏi. Hỏi làm sao biết thì trợ lý đưa chuỗi luật từ câu "
                  "trả lời tới lỗi. Hỏi sửa thế nào hay có nguy hiểm không thì có cách xử lý, mức độ và thông số của "
                  "dòng xe. Bây giờ em demo nhanh: kể 'xe Vision đề chỉ nghe tạch tạch, còi cũng yếu', hỏi 'tại sao', "
                  "trả lời 'có', rồi xem kết quả.")
    picture(s, IMG / "chat_vi.png", 0.6, 1.35, h=5.25)
    rows = [("Tại sao hỏi vậy?", "Các luật dùng câu đang hỏi; điều kiện ✓ đã có, ✗ không, ? đang hỏi"),
            ("Làm sao biết?", "Chuỗi luật từ câu trả lời tới lỗi, kèm CF"),
            ("Sửa thế nào? Có nguy hiểm không?", "Cách xử lý, mức độ, thông số theo sách hướng dẫn của dòng xe"),
            ("Còn khả năng nào?", "Ba lỗi có khả năng nhất, lỗi nào đã được luật chứng minh"),
            ("Cầu chì tổng là gì?", "Tra trong cơ sở tri thức: luật kết luận ra nó, luật dùng nó")]
    for i, (q, a) in enumerate(rows):
        y = 1.4 + i * 0.93
        card(s, 6.3, y, 6.43, 0.8, SOFT)
        text(s, 6.5, y + 0.08, 2.5, 0.64, q, 14, ACCENT, True, anchor=MSO_ANCHOR.MIDDLE)
        text(s, 9.1, y + 0.08, 3.45, 0.64, a, 12, TEXT, anchor=MSO_ANCHOR.MIDDLE)
    text(s, 6.3, 6.1, 6.43, 0.5, "Không có câu trả lời soạn sẵn: mỗi câu ghép từ luật, câu hỏi và CF.", 13, MUTED)

    # 18. Conclusion -------------------------------------------------------------------------------------------
    s = new_slide(prs, "CONTENT", "Kết luận",
                  "Tóm lại, cả suy diễn tiến và suy diễn lùi đều xếp đúng lỗi ở hạng 1 trong 30 kịch bản, và Wang "
                  "không khác suy diễn tiến lần nào. Chọn bộ phận trước giảm số câu từ 39,7 xuống 9. Mọi câu trả lời "
                  "đều chỉ ra được luật. Hạn chế: luật chỉ có điều kiện khẳng định nên trả lời không không làm giảm CF, "
                  "chat chỉ hiểu cụm từ có trong danh sách, và CF cùng kịch bản là do nhóm tự viết. Hướng tiếp theo là "
                  "thêm bằng chứng phủ định, lấy cụm từ từ nhật ký sửa xe thật và đo CF trên ca sửa thật.")
    cols = [("Đạt được", ["30/30 kịch bản đúng hạng 1, cả suy diễn tiến lẫn lùi", "Wang khớp suy diễn tiến: 0 khác biệt",
                          "Chọn bộ phận trước: 9,0 câu thay vì 39,7", "Mọi câu trả lời đều chỉ ra luật"], PANEL),
            ("Hạn chế", ["Trả lời “không” không làm giảm CF (luật chỉ có điều kiện khẳng định)",
                         "Chat chỉ hiểu cụm từ có trong danh sách", "CF và kịch bản do nhóm tự viết"], SOFT),
            ("Hướng phát triển", ["Thêm bằng chứng phủ định", "Cụm từ từ nhật ký sửa xe thật",
                                  "Đo CF trên ca sửa thật"], SOFT)]
    for i, (head, items, fill) in enumerate(cols):
        x, dark = 0.6 + i * 4.13, fill == PANEL
        card(s, x, 1.4, 3.9, 4.5, fill)
        text(s, x + 0.3, 1.65, 3.3, 0.45, head, 20, LIME if dark else ACCENT, True)
        text(s, x + 0.3, 2.3, 3.3, 3.4, items, 14, WHITE if dark else TEXT, bullets=True, space=8)
    text(s, 0.6, 6.1, 12.1, 0.5, "Luật có giải thích cho người lái một chẩn đoán đầu tiên đáng tin, không cần cảm biến "
                                 "hay dữ liệu huấn luyện.", 14, TEXT, True)

    # 19. Thanks -----------------------------------------------------------------------------------------------
    new_slide(prs, "DARK", "Cảm ơn thầy đã lắng nghe",
              "Phần trình bày của nhóm em đến đây là hết. Nhóm em cảm ơn thầy đã lắng nghe, mời thầy đặt câu hỏi.",
              "Mời thầy đặt câu hỏi · Demo: MotorbikeExpert.exe (chạy offline)")


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


def merge(lam: Path, out: Path) -> None:
    """PowerPoint inserts Giang's and Khoa's slides (with their notes) after Lâm's opening."""
    script = f"""
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open('{lam}', $false, $false, $false)
[void]$p.Slides.InsertFromFile('{GIANG}', {OPENING})
[void]$p.Slides.InsertFromFile('{KHOA}', {OPENING + 6})
$p.SaveAs('{out}')
$p.Close()
$app.Quit()
"""
    subprocess.run(["powershell", "-NoProfile", "-Command", script], check=True)


def replace_text(prs) -> int:
    done = 0
    for slide in prs.slides:
        frames = [sh.text_frame for sh in slide.shapes if sh.has_text_frame]
        frames += [c.text_frame for sh in slide.shapes if sh.has_table for row in sh.table.rows for c in row.cells]
        if slide.has_notes_slide:
            frames.append(slide.notes_slide.notes_text_frame)
        for tf in frames:
            for p in tf.paragraphs:
                for r in p.runs:
                    for old, new in FIXES:
                        if old in r.text:
                            r.text = r.text.replace(old, new)
                            done += 1
    return done


def swap_picture(slide, path: Path) -> None:
    """Put a new screenshot in the old one's place, fitted inside its box."""
    from PIL import Image
    pic = next(sh for sh in slide.shapes if sh.shape_type == 13)
    w, h = Image.open(path).size
    scale = min(pic.width / w, pic.height / h)
    nw, nh = int(w * scale), int(h * scale)
    new = slide.shapes.add_picture(str(path), pic.left + (pic.width - nw) // 2, pic.top, nw, nh)
    new.line.color.rgb = rgb("DCE1D6")
    new.line.width = Pt(1)
    pic._element.addprevious(new._element)  # keep the old z-order
    pic._element.getparent().remove(pic._element)


def slide_numbers(prs) -> None:
    """Lâm's content slides get the slide-number box that Giang's and Khoa's slides carry."""
    import copy
    giang = prs.slides[OPENING + 1]
    num = next(sh for sh in giang.shapes if sh.is_placeholder and sh.placeholder_format.type == 13)  # SLIDE_NUMBER
    for i, slide in enumerate(prs.slides):
        teammate = OPENING <= i < OPENING + 11
        if not teammate and slide.slide_layout.name == "CONTENT":
            slide.shapes._spTree.append(copy.deepcopy(num._element))


def fix_teammates(prs) -> None:
    giang_screen, khoa_chart, khoa_screen = prs.slides[OPENING + 5], prs.slides[OPENING + 9], prs.slides[OPENING + 10]
    for sh in khoa_chart.shapes:  # red marked the 3 misses of 12/11; now 30/30, so the same green as the others
        if sh.has_text_frame:
            for r in (r for p in sh.text_frame.paragraphs for r in p.runs if r.text == "5,5 câu · 30/30"):
                r.font.color.rgb = rgb(ACCENT)
    swap_picture(giang_screen, IMG / "motologic_result_vi.png")
    swap_picture(khoa_screen, IMG / "backward_why_vi.png")
    chart = next(sh for sh in khoa_chart.shapes if sh.has_chart).chart
    cats = list(chart.plots[0].categories)
    data = CategoryChartData()
    data.categories = cats
    values = {"Trợ lý, mô tả tiếng Việt": 5.5, "Lùi, đúng bộ phận": 9.0, "Lùi, mọi bộ phận": 39.7}
    data.add_series(chart.plots[0].series[0].name, [values[c] for c in cats])
    chart.replace_data(data)


def build(out: Path = OUT) -> Path:
    prs = Presentation(str(GIANG))
    drop_slides(prs)
    neutral_footer(prs)
    lam_slides(prs)
    lam_closing(prs)
    with tempfile.TemporaryDirectory() as tmp:
        lam, merged = Path(tmp) / "lam.pptx", Path(tmp) / "merged.pptx"
        prs.save(str(lam))
        merge(lam, merged)
        prs = Presentation(str(merged))
    assert len(prs.slides) == 19, len(prs.slides)
    print(f"{replace_text(prs)} numbers corrected")
    fix_teammates(prs)
    slide_numbers(prs)
    prs.save(str(out))
    return out


if __name__ == "__main__":
    print("Written:", build())
    sys.exit(0)
