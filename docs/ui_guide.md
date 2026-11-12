# Giao diện chuẩn của nhóm

Người phụ trách: Lâm. Áp dụng cho GUI, CLI, biểu đồ trong báo cáo và slide.

Mọi màu, font, kích thước đều nằm trong [`src/theme.py`](../src/theme.py). **Import từ đó, không tự gõ mã màu hay tên font.** Cần màu mới thì thêm vào `theme.py` qua Pull Request và cập nhật file này.

```python
import theme
from theme import COLORS, FONTS, PAD

theme.apply(root)                      # ngay sau tk.Tk()
tk.Label(root, text="Lỗi", fg=COLORS["text"], font=FONTS["heading"])

theme.apply_matplotlib()               # trước khi vẽ biểu đồ
plt.bar(x, y, color=theme.ENGINE_COLORS["forward"])
```

## 1. Màu

Chỉ có một màu chính là xanh dầu `accent`. Xanh lá và đỏ chỉ dùng cho ý nghĩa, không dùng để trang trí.

| Tên trong `COLORS` | Mã | Dùng cho |
|---|---|---|
| `accent` | `#0E5E6F` | Nút chính, thanh CF, lỗi xếp hạng 1, tiêu đề |
| `accent_hover` | `#0A4A58` | Nút chính khi rê chuột hoặc nhấn |
| `accent_soft` | `#DCECEF` | Khung “Tại sao?”, mục đang chọn |
| `bg` | `#E9EEF0` | Nền cửa sổ |
| `surface` | `#FFFFFF` | Panel, thẻ kết quả, ô nhập |
| `chrome` | `#DAE3E6` | Thanh trạng thái, rãnh thanh CF, nút bị tắt |
| `border` | `#C8D3D7` | Viền 1 px của panel, thẻ, ô nhập |
| `text` | `#132228` | Chữ chính |
| `muted` | `#5B6B70` | Chữ phụ, gợi ý, số đếm |
| `ok` / `ok_soft` | `#2E7D4F` / `#E3F1E8` | “Tự xử lý được”, nút Có, Wang khớp |
| `danger` / `danger_soft` | `#B3261E` / `#F8E1DF` | “Cần mang ra thợ”, nút Không, lỗi |
| `warn` / `warn_soft` | `#8A5A00` / `#FBEFD6` | Chưa đủ dữ kiện để kết luận |
| `sidebar` | `#082E37` | Thanh điều hướng bên trái của GUI |
| `highlight` / `highlight_soft` | `#E9A23B` / `#FCEFD9` | Mục đang chọn ở thanh bên, gạch dưới tiêu đề màn hình, điểm nhấn màn Tổng quan |

### Màu theo bộ phận (`SUBSYSTEM_COLORS`)

Dùng cho chấm màu cạnh nhóm triệu chứng và mọi biểu đồ chia theo bộ phận. Thứ tự luôn theo `SUBSYSTEM_ORDER`.

| Bộ phận | Tên hiển thị | Mã |
|---|---|---|
| `starting_fuel` | Khởi động, nhiên liệu | `#0E5E6F` |
| `ignition_electrical` | Đánh lửa, điện | `#C98A0B` |
| `engine` | Động cơ | `#B5561D` |
| `transmission` | Truyền động | `#4A5BA8` |
| `brakes` | Phanh | `#7A4C9A` |
| `tyres_suspension` | Lốp, giảm xóc | `#5F6B3A` |

### Màu theo bộ suy luận (`ENGINE_COLORS`)

Trong mọi biểu đồ và slide: forward chaining luôn là `#0E5E6F`, backward chaining luôn là `#C98A0B`, Wang luôn là `#4A5BA8`.

## 2. Chữ

GUI chỉ dùng **Segoe UI** (có sẵn trên mọi máy Windows, nên file .exe chạy ở máy nào cũng giống nhau) và **Consolas** cho mã luật, số CF. Cỡ tính bằng point của Tkinter.

| Tên trong `FONTS` | Font | Cỡ | Dùng cho |
|---|---|---|---|
| `display` | Segoe UI đậm | 22 | Tiêu đề màn hình, số lớn |
| `title` | Segoe UI đậm | 12 | Tên chương trình, tên lỗi trên thẻ |
| `question` | Segoe UI đậm | 13 | Câu hỏi ở chế độ hỏi đáp |
| `heading` | Segoe UI đậm | 10 | Tiêu đề panel, chữ trên nút |
| `body` | Segoe UI | 10 | Nội dung chung |
| `small` / `small_bold` | Segoe UI | 9 | Gợi ý, số đếm, giải thích why/how, nhãn |
| `mono` / `mono_bold` | Consolas | 9 | Mã luật (SF01, BR04), giá trị CF |

Không in nghiêng, không dùng font khác.

## 3. Kích thước và thành phần

- Khoảng cách chỉ dùng `PAD`: 4, 8, 12, 16 px. Giữa các panel là 12.
- Viền luôn 1 px màu `border`. Không dùng relief `raised`, `sunken`, `groove` của Tk.
- Nút (style ttk): `Primary.TButton` (mỗi màn chỉ 1 nút), `Secondary.TButton`, `Yes.TButton`, `No.TButton`, `Link.TButton`.
- Chip mức độ: lấy màu bằng `theme.severity_colors(severity)`, chữ lấy từ `theme.SEVERITY_TEXT`.
- Thanh CF: cao 8 px, màu `accent`, đầy = CF 1.00. Luôn ghi số 2 chữ số thập phân bên phải. **Không đổi màu theo giá trị**, vì màu đỏ đã dành cho “cần thợ”.
- Thẻ kết quả theo thứ tự: hạng, tên lỗi, chip mức độ, rồi CF, rồi cách xử lý, rồi “Vì sao ra kết quả này?”. Hiện tối đa `MAX_RESULTS` = 5 thẻ.

## 4. Cách gọi tên

Người dùng là người đi xe, không phải dân AI. Trên giao diện dùng cột “Hiển thị”, trong báo cáo dùng cột “Báo cáo”. Chữ của triệu chứng, lỗi và cách xử lý luôn lấy từ `kb.text()`, `kb.question()`, `kb.action()`. Không hiện id kỹ thuật như `weak_battery` cho người dùng, trừ mã luật.

| Trong code | Hiển thị (VI) | Hiển thị (EN) | Báo cáo |
|---|---|---|---|
| symptom | Triệu chứng | Symptom | triệu chứng (symptom) |
| intermediate | Kết luận trung gian | Intermediate finding | sự kiện trung gian |
| fault | Lỗi | Fault | lỗi (fault) |
| cf | Độ tin cậy | Confidence | hệ số chắc chắn CF |
| rule | Luật | Rule | luật (rule) |
| forward | Theo triệu chứng | By symptoms | suy diễn tiến (forward chaining) |
| backward | Hỏi đáp từng câu | Step-by-step questions | suy diễn lùi (backward chaining) |
| severity `self` | Tự xử lý được | You can fix it | tự xử lý |
| severity `mechanic` | Cần mang ra thợ | Take it to a mechanic | cần thợ |
| why / how | Tại sao hỏi câu này? / Vì sao ra kết quả này? | Why this question? / How was this found? | giải thích why / how |

## 5. CLI

Không dùng màu ANSI (cmd của Windows hiện sai). Thứ tự giống thẻ kết quả của GUI:

```text
Kết quả chẩn đoán  (2 luật đã chạy: SF01, SF02)
----------------------------------------------------------------
1. Ắc quy yếu hoặc hết điện
   Độ tin cậy 0.77  [###############     ]  Tự xử lý được
   Cách xử lý: Sạc lại ắc quy; nếu sạc xong vẫn yếu thì thay ắc quy mới.
   Vì sao ra kết quả này?
     bạn chọn  Còi kêu yếu hơn bình thường                    1.00
     SF01      → Điện yếu: ắc quy không đủ điện để đề         0.90
     SF02      → Ắc quy yếu hoặc hết điện                     0.77
```

## 6. Biểu đồ trong báo cáo và slide

- Gọi `theme.apply_matplotlib()` trước khi vẽ: nền trắng, lưới ngang mờ, bỏ viền trên và phải, chữ Segoe UI, lưu 200 dpi.
- Màu theo mục 1 (bộ phận hoặc bộ suy luận). Không dùng màu mặc định của matplotlib.
- Tiêu đề và nhãn trục bằng tiếng Anh, vì báo cáo viết tiếng Anh.
- Lưu ảnh vào `docs/report/figures/`, tên file dạng `fig_<nội_dung>.png`.

## 7. Ảnh chụp màn hình cho báo cáo

Chụp cửa sổ ở kích thước mặc định, giao diện tiếng Việt, dùng kịch bản mẫu (ví dụ SE01) để mọi ảnh cùng dữ liệu.

## 8. Nên và không nên

Nên:
- Import màu, font, kích thước từ `theme.py`.
- Lấy chữ hiển thị từ cơ sở tri thức (`kb.text()`, `kb.question()`, `kb.action()`).
- Cần màu hoặc kiểu mới thì nhắn nhóm, thêm vào `theme.py` qua PR.

Không nên:
- Gõ mã màu `"#..."` hoặc tên màu Tk (`"red"`, `"lightblue"`) trong code.
- Dùng font khác Segoe UI / Consolas.
- Đổi màu thanh CF theo giá trị.
- Thêm icon, emoji hoặc ảnh nền.

## 9. Cắm màn hình vào GUI

Khung cửa sổ (`src/gui.py`, Lâm) có thanh bên trái và 4 màn hình. Hai màn chẩn đoán do người viết bộ suy luận làm, mỗi người một file riêng:

| Màn hình | File | Class | Người làm |
|---|---|---|---|
| Trợ lý chẩn đoán (lời kể, câu hỏi thông minh) | `src/gui_assistant.py` | `AssistantPage` | Lâm |
| Theo triệu chứng (forward, Wang) | `src/gui_forward.py` | `ForwardPage` | Giang |
| Hỏi đáp từng câu (backward, why/how) | `src/gui_backward.py` | `BackwardPage` | Khoa |
| Cơ sở tri thức | `src/gui.py` | `KBPage` | Lâm |
| Giới thiệu | `src/gui.py` | `AboutPage` | Lâm |

Khi chưa có file, cửa sổ hiện ghi chú “Màn hình đang được làm”. Khi file có mặt, màn hình tự hiện; nếu file lỗi lúc nạp, cửa sổ hiện thông báo lỗi thay vì tắt.

Mẫu tối thiểu:

```python
"""Màn hình Theo triệu chứng (owner: Giang)."""
import tkinter as tk
from gui_widgets import Page, Panel, label, page_header
from theme import PAD

TEXT = {"vi": {"title": "Chẩn đoán theo triệu chứng"}, "en": {"title": "Diagnosis by symptoms"}}


class ForwardPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app)
        t = TEXT[app.lang]
        page_header(self, t["title"], "...").pack(fill="x", pady=(0, PAD["m"]))
        panel = Panel(self, "...")
        panel.pack(fill="both", expand=True)
        label(panel.body, "...").pack(anchor="w")

    def on_show(self):        # gọi mỗi lần người dùng chuyển tới màn hình này (không bắt buộc)
        pass

    def on_key(self, event):  # phím bấm khi đang ở màn hình này (không bắt buộc)
        pass
```

`app` cho mỗi màn hình dùng:
- `app.kb`: cơ sở tri thức (`kb.text()`, `kb.question()`, `kb.action()`).
- `app.lang`: `"vi"` hoặc `"en"`. Đổi ngôn ngữ thì cả cửa sổ được dựng lại, màn hình chỉ cần đọc `app.lang` trong `__init__`.
- `app.scenarios`: các kịch bản trong `scenarios/` (dùng cho nút tải kịch bản mẫu nếu muốn).
- `app.state`: dict dùng chung giữa các màn hình; giữ dữ liệu cần còn lại khi đổi ngôn ngữ (ví dụ triệu chứng đã chọn).
- `app.show("kb")`: chuyển màn hình.

Thành phần có sẵn trong `src/gui_widgets.py` (dùng thay cho widget tk thường để mọi màn hình giống nhau): `Page`, `Panel`, `ScrollFrame`, `Segmented`, `HintEntry`, `page_header`, `tile`, `label`, `autowrap`, `link`, `chip`, `severity_chip`, `rank_badge`, `CFBar`, `dot`, `px` (nhân kích thước theo độ phân giải màn hình), `fold` (tìm kiếm không dấu). Hàm chuyển kết quả thành chữ cho người dùng: `src/present.py` (`how_rows`, `near_misses`, `short`).

Chạy thử: `python src/gui.py`. Có nút Sáng/Tối ở thanh bên: khi đổi, `theme.set_mode()` thay giá trị trong `COLORS` rồi dựng lại mọi màn hình, nên màn hình nào chỉ dùng `C["..."]` sẽ tự đổi màu; đừng tự gõ mã màu. Phần logic (không vẽ) nên tách thành hàm riêng để viết unit test.
