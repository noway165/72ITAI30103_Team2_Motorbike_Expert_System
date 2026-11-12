# Spec: chẩn đoán cụ thể theo dòng xe (owner: Lâm)

Ngày 12/11/2026. Nhánh `feature/lam-bike-models` (tách từ `main` = `ba53e10`). Trạng thái: **đã duyệt thiết kế, chưa code.**

## Mục tiêu

Kết quả nói cụ thể theo dòng xe người dùng chọn, không chung chung "tay ga / xe số":
1. **Thông số đúng xe** trong cách xử lý: ắc quy, dầu nhớt (dung tích, chu kỳ thay), bugi, áp suất lốp, dây curoa (tay ga) hoặc xích (xe số).
2. **Luật riêng theo dòng xe**: dòng xe + triệu chứng có sẵn ⇒ lỗi có sẵn, CF cao hơn luật chung một chút.

Phạm vi đợt đầu: **Honda Vision, Air Blade, Lead, Wave Alpha, Future; Yamaha Exciter**, theo đời đang bán (ghi năm đời xe). Có lựa chọn "Xe khác" giữ cách chọn cũ.

## Quy tắc

- Mọi thông số và mọi luật đều có nguồn. Thông số lấy từ trang thông số hoặc sách hướng dẫn của hãng (Honda Việt Nam, Yamaha Việt Nam). Luật "dòng X hay lỗi Y" thường chỉ có nguồn từ tiệm hoặc báo xe, nên ghi vào mục nguồn yếu trong `docs/sources.md`.
- Không bịa thông số. Không tìm được nguồn thì để trống, và giao diện không hiện mục đó.
- Mọi kết luận vẫn do forward chaining. Thông số chỉ thêm vào phần "cách xử lý".
- Sau khi thêm luật, 30 kịch bản phải giữ 30/30. Nếu tụt, báo Lâm trước khi sửa.
- Người viết luật không viết kịch bản: Giang và Khoa viết khoảng 5 kịch bản MD01… cho luật theo dòng xe.

## Thiết kế

**Dữ liệu: `knowledge_base/models.json`**
- `"subsystem": "vehicle"`.
- `symptoms`: mỗi dòng xe một dữ kiện, ví dụ `model_honda_vision` ("Xe của bạn là Honda Vision?"). Dùng subsystem `vehicle` để code hiện có coi đây là dữ kiện về xe: `present.how_rows` bỏ qua, checklist không liệt kê.
- `rules`: luật riêng theo dòng xe, có `source`.
- `models` (khối mới): `{id: {name, brand, year, kind: scooter|manual, fuel: fi|carb, clutch: bool, specs: {battery, oil, spark_plug, tyre_pressure, belt|chain: {vi, en, source}}}}`.

**Đã kiểm tra trong `kb.py`**
- `load_kb` đọc mọi `*.json` trong `knowledge_base/` và chỉ đọc `symptoms` / `intermediates` / `faults` / `rules`. Khối `models` bị bỏ qua mà không báo lỗi, nên cần thêm hàm đọc riêng, ví dụ `load_models()`.
- `validate` cảnh báo symptom không có luật nào dùng. Dòng xe chưa có luật riêng sẽ sinh cảnh báo. Cách xử lý: chỉ tạo symptom `model_*` cho dòng xe có luật; dòng xe khác chỉ dùng `models` để điền `kind`, `fuel`, `clutch`.
- Luật không có `source` sinh cảnh báo. `kb.py` phải giữ 0 lỗi, 0 cảnh báo.

**Nơi cần sửa**
- `gui_diagnosis.py`:
  - `vehicle_answers(kind, fuel)` thêm dòng xe → `has_clutch_lever` và `model_*` (True cho xe đã chọn, False cho các xe khác);
  - `new_dx` thêm `model`; `Record` thêm `model` (mặc định `""`); `bike_text` hiện tên xe;
  - bước 1 chọn dòng xe (các nút gọn, nhiều cột) + "Xe khác"; sửa luôn chỗ bước 1 phải cuộn (G2 của Giang, báo Giang);
  - màn kết quả: khối "Riêng cho <xe>" chỉ hiện thông số liên quan đến lỗi.
- Bảng lỗi → thông số liên quan:
  - `weak_battery` và các lỗi sạc → `battery`;
  - lỗi nhớt → `oil`;
  - lỗi bugi → `spark_plug`;
  - `underinflated_tyre` → `tyre_pressure`;
  - lỗi dây curoa → `belt`;
  - lỗi xích → `chain`.
- `chat.py`: câu trả lời "sửa thế nào?" thêm thông số đúng xe.
- `nlu.py`: tên xe → `model_*` (đang có "vision", "air blade"... → `is_scooter`).
- `interview.py`: `NEUTRAL` thêm `model_*` (dữ kiện về xe không phản bác lỗi).
- `gui_history.py`: hiện tên xe.
- Test: bảng dòng xe ra đúng câu trả lời; chọn xe trong cửa sổ; `kb.py` sạch; 30/30; `tools/shots.py` bước 1 và màn kết quả.
- Báo cáo: 2–3 câu ở 3.1, cập nhật số ở Ch4 nếu đổi.

## Thứ tự làm

1. Tìm nguồn: thông số 6 dòng xe + lỗi hay gặp theo dòng (bảng nguồn trong `docs/sources.md`).
2. `models.json` + `load_models()` + validate.
3. Luật riêng, NLU, `NEUTRAL`.
4. Bước 1, màn kết quả, chat, lịch sử.
5. Chạy lại 30 kịch bản, test, ảnh chụp.
6. README, báo cáo, commit, PR.
