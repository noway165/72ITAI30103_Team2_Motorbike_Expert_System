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
| `bg` | `#EEF2F3` | Nền cửa sổ |
| `surface` | `#FFFFFF` | Panel, thẻ kết quả, ô nhập |
| `chrome` | `#DDE4E6` | Thanh trạng thái, rãnh thanh CF, nút bị tắt |
| `border` | `#CBD5D8` | Viền 1 px của panel, thẻ, ô nhập |
| `text` | `#17252A` | Chữ chính |
| `muted` | `#5B6B70` | Chữ phụ, gợi ý, số đếm |
| `ok` / `ok_soft` | `#2E7D4F` / `#E3F1E8` | “Tự xử lý được”, nút Có, Wang khớp |
| `danger` / `danger_soft` | `#B3261E` / `#F8E1DF` | “Cần mang ra thợ”, nút Không, lỗi |
| `warn` / `warn_soft` | `#8A5A00` / `#FBEFD6` | Chưa đủ dữ kiện để kết luận |
| `sidebar` | `#0B3D49` | Thanh điều hướng bên trái của GUI |

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
| `display` | Segoe UI đậm | 20 | Tiêu đề màn hình, số lớn |
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
- Tiêu đề và nhãn trục bằng tiếng Việt; tên phương pháp giữ tiếng Anh trong ngoặc, ví dụ “suy diễn lùi (backward chaining)”.
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
