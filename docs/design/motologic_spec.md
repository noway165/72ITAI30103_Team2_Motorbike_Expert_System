# Giao diện MotoLogic: đặc tả cho Giang

Người làm: **Giang**. Người duyệt: Lâm. Hạn: **tối 14/11/2026**. Ngày 15/11 tập demo, vấn đáp 16/11. Nếu tối 14/11 chưa chạy ổn, demo bằng app hiện tại.

Mục tiêu: đổi toàn bộ app sang phong cách trong 4 ảnh mẫu, thêm chi tiết riêng của xe máy. Bộ suy luận, cơ sở tri thức và test hiện có **không đổi**: màn hình mới chỉ gọi lại các hàm đã có.

| Ảnh mẫu | Màn hình |
|---|---|
| [motologic_1_setup.png](motologic_1_setup.png) | Bước 1: khai báo xe và chọn cách chẩn đoán |
| [motologic_2_guided_question.png](motologic_2_guided_question.png) | Bước 2a: hỏi đáp từng câu |
| [motologic_3_symptom_checklist.png](motologic_3_symptom_checklist.png) | Bước 2b: chọn triệu chứng |
| [motologic_4_result.png](motologic_4_result.png) | Bước 3: kết quả |

## 1. Màu và chữ (`src/theme.py`)

Giữ nguyên **tên** các khoá trong `COLORS` (màn của Khoa, màn Trợ lý và màn Cơ sở tri thức đều dùng), chỉ đổi giá trị và thêm khoá mới. Cả `LIGHT` và `DARK` phải có cùng bộ khoá (có test kiểm tra).

Giá trị gợi ý, lấy từ ảnh mẫu (chỉnh lại cho khớp khi so trên màn hình):

| Khoá | Sáng | Tối | Dùng cho |
|---|---|---|---|
| `bg` | `#F2F3EC` | `#0F1B17` | nền kem |
| `surface` | `#FFFFFF` | `#17261F` | thẻ trắng bo góc |
| `panel` (mới) | `#1B3B33` | `#0B1612` | khối xanh rêu đậm bên phải, thẻ số liệu |
| `on_panel` (mới) | `#FFFFFF` | `#E6F0EC` | chữ trên khối đậm |
| `panel_muted` (mới) | `#B9CCC4` | `#8FA89F` | chữ phụ trên khối đậm |
| `lime` (mới) | `#DDF57A` | `#C9E86A` | mục đang chọn, nút mũi tên, số liệu nổi bật |
| `lime_soft` (mới) | `#EEF7CF` | `#26341C` | thẻ được chọn, chip "Recommended" |
| `accent` | `#1F6B57` | `#4FB394` | chữ nhấn, viền thẻ được chọn, thanh tiến trình |
| `text` | `#14352C` | `#E3EEEA` | chữ chính |
| `muted` | `#5F6F67` | `#93A9A0` | chữ phụ |
| `border` | `#DCE1D6` | `#2C4038` | viền thẻ |
| `sidebar` | `#FFFFFF` | `#0B1612` | thanh bên sáng như mẫu |

Chữ: Segoe UI (có sẵn trên Windows). Tiêu đề màn khoảng 28 pt đậm; dòng "eyebrow" (LET'S FIND THE CAUSE) 9 pt đậm, viết hoa, màu `accent`, có chấm tròn phía trước; thân bài 10–11 pt.

## 2. Thành phần dùng chung (`src/gui_widgets.py`)

Tk không có khung bo góc, nên làm bằng `tk.Canvas` vẽ `round_rect` (hàm đã có) rồi đặt `tk.Frame` vào trong bằng `create_window`.

- `RoundCard(parent, fill, border, radius=18)`: thẻ bo góc, chiều cao tự theo nội dung bên trong.
- `PillButton(parent, text, command, style="dark" | "lime" | "outline")`: nút bo tròn; nút chính màu `panel`, ô mũi tên → màu `lime` ở bên phải.
- `Stepper(parent, steps, current)`: 3 bước có số trong vòng tròn, bước xong hiện ✓, gạch chân bước đang làm.
- `ChoiceCard(parent, title, subtitle, selected, command, icon=None)`: thẻ chọn có nút radio (loại xe, cách chẩn đoán), thẻ được chọn nền `lime_soft` viền `accent`.
- `CheckRow(...)`: dòng tick triệu chứng như ảnh 3.
- `Gauge(parent, cf)`: **đồng hồ kiểu công-tơ-mét** vẽ nửa vòng cung 0 → 1.0, kim chỉ CF. Dùng thay thanh CF ở màn kết quả.
- Icon vẽ trên Canvas, không dùng ảnh hay emoji: xe tay ga, xe số, ắc quy, bugi, động cơ, bánh răng/xích, đĩa phanh, lốp, cờ-lê (cần thợ), khiên (an toàn). Mỗi bộ phận (`theme.SUBSYSTEM_ORDER`) có 1 icon.
- Mọi kích thước pixel đi qua `px()` để không vỡ trên màn hình 125–150%.

## 3. Khung cửa sổ (`src/gui.py`)

- **Thanh bên** (ảnh 1): logo "MotoLogic" + "MOTORBIKE EXPERT SYSTEM"; mục WORKSPACE gồm Chẩn đoán, Lịch sử phiên, Cơ sở tri thức; mục đang chọn là khối `lime` bo góc. Giữ thêm một mục nhỏ "Màn cũ" chứa Theo triệu chứng, Hỏi đáp từng câu, Trợ lý để không mất phần đã làm.
- Thẻ đậm "Transparent by design" với 2 số lấy từ `len(kb.rules)` và `len(kb.faults)` (không gõ cứng 79, 40).
- Thẻ "ACADEMIC PROTOTYPE · Group 2 · Topic A" ở đáy thanh bên.
- Nút ngôn ngữ VI/EN và Sáng/Tối giữ nguyên chức năng (đặt ở đáy thanh bên hoặc thanh trên).
- **Thanh trên**: breadcrumb "Workspace / Chẩn đoán", mã phiên ("Phiên 001"), chip "Chạy offline".

## 4. Màn Chẩn đoán (`src/gui_diagnosis.py`, class `DiagnosisPage`)

Một màn 3 bước, đăng ký trong `OWN_PAGES` của `gui.py` và đặt làm màn mở đầu.

### Bước 1: Khai báo xe (ảnh 1)
- 2 thẻ chọn loại xe có icon xe: Xe tay ga (`is_scooter`), Xe số (`is_manual`). **Thêm**: chọn Phun xăng (FI) / Bình xăng con (`is_fuel_injected` / `is_carburetor`).
- 3 cách chẩn đoán (ảnh mẫu có 2, thêm cách thứ 3):
  - **Hỏi đáp từng câu** (gợi ý, chip "Recommended"): backward chaining.
  - **Tôi biết triệu chứng**: forward chaining.
  - **Kể bằng lời**: trợ lý đọc câu tiếng Việt/Anh.
- Khối đậm bên phải: "Made for everyday symptoms", 6 bộ phận kèm icon và số lỗi của từng bộ phận; ô "An toàn trước tiên: dựng xe nơi an toàn, tắt máy trước khi kiểm tra".
- Nút "Bắt đầu chẩn đoán →".

### Bước 2a: Hỏi đáp từng câu (ảnh 2), dùng code của Khoa
```python
from backward_chaining import BackwardSession, UNKNOWN
from gui_backward import goals_for, why_rows   # hàm có sẵn của Khoa
session = BackwardSession(kb, goals_for(kb, subsystem), answers={"is_scooter": True, ...})
q = session.question            # q.symptom, q.chain, q.number ; None khi xong
session.answer(True / False / UNKNOWN)
session.undo()                  # "Câu trước"
session.result                  # BackwardResult khi xong
```
- Chip "CÂU 02", câu hỏi chữ lớn (`kb.question`), gợi ý nhỏ (`kb.symbols[s].hint`).
- 2 nút lớn "Có" / "Không", dòng "Không chắc, bỏ qua câu này" (= `UNKNOWN`).
- Khối đậm bên phải "Tại sao hỏi câu này?": luật đang thử lấy từ `q.chain[-1].rule` (mã luật, NẾU … → THÌ …), kèm số giả thuyết còn lại `len(session.remaining())`.
- Dải "Đã trả lời" ở dưới: các câu đã trả lời dạng chip, có "Sửa câu trả lời".
- Cho phép chọn bộ phận cần hỏi (giống màn của Khoa) để ít câu hỏi hơn.

### Bước 2b: Chọn triệu chứng (ảnh 3), dùng code của Giang
- Ô tìm kiếm (dùng `gui_widgets.fold` để gõ không dấu), 6 chip lọc theo bộ phận, danh sách `CheckRow`.
- Khối đậm bên phải "Quan sát của bạn": số đã chọn và danh sách đã tick; "Điều gì xảy ra tiếp theo?".
- Nút "Tìm lỗi phù hợp →" gọi `forward_chain(kb, symptoms)`.

### Bước 2c: Kể bằng lời (dùng code của Lâm)
```python
from nlu import extract                 # các cụm từ hiểu được, có vị trí để tô sáng
from interview import Interview         # chọn câu hỏi bằng information gain
iv = Interview(kb, {m.symptom: m.value for m in extract(text, kb.symptoms)})
q = iv.next_question()                  # None khi đủ dữ kiện
iv.answer(q.symptom, True / False / None)
iv.result()                             # ForwardResult
```
Giao diện câu hỏi dùng lại khung của bước 2a.

### Bước 3: Kết quả (ảnh 4)
- Băng đậm trên cùng: icon theo bộ phận của lỗi, "LỖI CÓ KHẢ NĂNG CAO", tên lỗi (`kb.text`), "Theo chuỗi luật R1 → R2" (mã luật thật), 2 ô số: Quan sát (số câu trả lời "có") và Luật đã dùng.
- **Đồng hồ CF** (`Gauge`) cạnh tên lỗi.
- "Chương trình suy ra thế nào?": mỗi luật một thẻ, lấy từ `present.how_rows(kb, result.wm, fault, lang)`; thẻ cuối nền `lime_soft`.
- "Bước tiếp theo": `kb.action(fault)` và mức độ: tự xử lý được hoặc cần mang ra thợ (icon cờ-lê, màu `danger`).
- Thẻ "Kiểm chứng bằng Wang": nút "Kiểm chứng kết luận" → `wang.entails(kb, symptoms_yes, fault).valid` → ✓ hoặc ✕ (ảnh mẫu ghi "Not run", bấm mới chạy).
- "Cũng có thể là": 2 lỗi tiếp theo trong `result.diagnoses`.
- Nếu không có lỗi nào: hiện `present.near_misses` (kết luận trung gian đã suy ra và triệu chứng nên kiểm tra thêm).
- Nút "Chẩn đoán mới →". Dòng nhỏ: "Luật minh hoạ; kết quả không thay cho việc kiểm tra của thợ".

## 5. Lịch sử phiên (`src/gui_history.py`)
Lưu mỗi lần ra kết quả vào `app.state["history"]` (giờ, loại xe, cách chẩn đoán, lỗi, CF). Màn hình là danh sách; bấm một dòng thì mở lại bước 3 của phiên đó. Chỉ lưu trong lúc app đang chạy, không cần ghi file.

## 6. Yêu cầu chung
- Tiếng Việt và tiếng Anh (`app.lang`), chữ của triệu chứng và lỗi lấy từ `kb.text` / `kb.question` / `kb.action`.
- Chạy đúng ở cả chế độ Sáng và Tối: chỉ dùng `C["..."]`, không gõ mã màu trong màn hình.
- Tách phần logic (chọn câu, gom kết quả, lịch sử) khỏi phần vẽ để viết unit test, ví dụ `tests/test_gui_diagnosis.py`.
- `python -m unittest discover tests` phải qua hết. `build_exe.bat` build được.
- Không sửa `kb.py`, `forward_chaining.py`, `backward_chaining.py`, `wang.py`, `nlu.py`, `interview.py`; cần thêm gì thì nhắn chủ của file đó.

## 7. Nghiệm thu (Lâm kiểm tra trước khi merge)
- ☐ 4 màn giống ảnh mẫu về bố cục, màu, kích thước chữ; có icon xe và đồng hồ CF.
- ☐ Kịch bản SE01 đi hết 3 bước bằng cả 3 cách chẩn đoán, đều ra "Ắc quy yếu", Wang ✓.
- ☐ BT03 ra "Rò rỉ dầu phanh", hiện "Cần mang ra thợ".
- ☐ Đổi VI/EN và Sáng/Tối giữa chừng không mất câu trả lời.
- ☐ Màn hình 125% không bị cắt chữ.
- ☐ Ảnh chụp 4 màn cho báo cáo lưu ở `docs/report/figures/fig_motologic_*.png`.
