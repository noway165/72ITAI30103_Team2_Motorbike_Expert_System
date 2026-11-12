# Tiến độ của Khoa (phân công 12/11/2026)

Nhánh: `feature/khoa-final`. Kiểm thử: `python -m unittest discover tests`.

| Việc | Trạng thái |
|---|---|
| A1. Màn Hỏi đáp đọc rõ ở Sáng và Tối (`src/theme.py`) | Xong, có test `tests/test_theme_contrast.py`. Cần mở app trên Windows xem lại bằng mắt |
| A2. Hỗ trợ Giang nối `BackwardSession` vào màn Chẩn đoán (bước 2a) | Đã kiểm code của Giang, chạy đúng; thêm `fixed=` (mục 2) |
| A3. Đọc lại `src/interview.py`, góp ý cách so sánh số câu hỏi | Xong (mục 3) |
| A4. Thêm cột Trợ lý vào `fig_backward_questions.png` | Xong (`python src/evaluate.py --charts`) |
| A5. Thử bản .exe cuối với 5 kịch bản backward | Tối 14/11, điền bảng mục 5 |
| B1. Cắt Experiments & Results xuống khoảng 200 từ | Xong (`docs/report/experiments_results_khoa.md`) |
| B2. Gộp bảng Trợ lý vào bảng chung Chapter 4 | Xong (Table 4.2.1) |
| B3. Gửi số liệu cho Giang viết Discussion | Mục 4, gửi trước trưa 14/11 |
| C1. Slide và lời thoại Backward + đánh giá | `docs/slides/khoa_backward_eval.pptx`, `docs/slides/khoa_script.md` |
| C2. Demo BT03 phần Phanh | Kịch bản demo trong `khoa_script.md` |

## 1. Màu màn Hỏi đáp (theme.py)

Đo độ tương phản WCAG 2.1 (chữ thường cần ≥ 4.5:1) cho mọi cặp màu chữ / nền mà `gui_backward.py` vẽ.
Chỗ khó đọc trước khi sửa:

| Chế độ | Chỗ | Trước | Sau |
|---|---|---|---|
| Tối | Nút Có (chữ trắng trên `ok`) | 2.55 | 6.99 |
| Tối | Nút Không (chữ trắng trên `danger`) | 3.26 | 5.47 |
| Tối | Nút Bắt đầu / Hỏi lại, huy hiệu hạng 1 (chữ trắng trên `accent`) | 3.31 | 6.99 |
| Tối | Nút chính khi rê chuột | 2.49 | 9.21 |
| Tối | Số hạng 2–5 (`accent` trên `accent_soft`) | 3.69 | 4.78 |
| Sáng | Dòng phím tắt ở thanh trạng thái (`muted` trên `chrome`) | 4.26 | 5.11 |
| Sáng | Chip “Tự xử lý được” (`ok` trên `ok_soft`) | 4.33 | 4.95 |

Thay đổi: ở bản Tối `on_accent` thành chữ tối `#0F191C` (nền nút Tối là màu sáng), `accent` `#3FB0C4`,
`accent_hover` `#5CC9DB`; ở bản Sáng `muted` `#4F5F64`, `ok` `#2A7347`. Thêm khoá `ok_hover`, `danger_hover`
(trước đây gõ cứng `#256A42`, `#931F18` trong `apply()`, nên ở bản Tối nút Có chuyển sang xanh đậm khi rê chuột).

**Sau khi gộp với bảng màu MotoLogic (PR #17):** giữ nguyên màu của Giang, chỉ thêm `ok_hover`, `danger_hover` và đổi
`muted` bản Sáng từ `#5F6F67` thành `#56655E`: màu cũ chỉ đạt 4.36:1 trên `chrome` (dòng phím tắt) và 4.49:1 trong
khung “Tại sao”. Bản Tối của Giang đã để `on_accent` tối nên nút đọc rõ. Mọi cặp màu trong `tests/test_theme_contrast.py` đều qua.

## 2. Nối BackwardSession vào màn Chẩn đoán (bước 2a)

Đã xem `guided_session()` trong `src/gui_diagnosis.py` (PR #17): Giang truyền loại xe qua `answers=` nhưng tự đếm số câu
(`len(dx["answers"]) + 1`) và tự giữ danh sách câu trả lời cho “Câu trước”, nên không bị hai lỗi “CÂU 02” và
undo xoá loại xe. Không cần sửa.

Nếu sau này muốn gọn hơn, `BackwardSession` có thêm tham số `fixed=` cho dữ kiện khai ở bước 1: không đánh số,
không tính vào `result.questions_asked`, `undo()` không xoá được:

```python
session = BackwardSession(kb, goals_for(kb, part), answers=dict(dx["answers"]),
                          fixed=vehicle_answers(dx["kind"], dx["fuel"]))
q = session.question            # None khi xong; q.number bắt đầu từ 1
session.known()                 # loại xe + câu trả lời
```

Test: `test_fixed_vehicle_type_is_not_a_question`, `test_bt03_demo_path` trong `tests/test_backward_chaining.py`.

## 3. Góp ý về interview.py và cách so sánh số câu hỏi

Cách chọn câu bằng information gain đúng với mô tả trong `assistant_lam.md`. Về so sánh 39,7 câu (backward)
với 5,8 câu (Trợ lý), ba điểm làm so sánh chưa ngang nhau; em đã đo lại bằng cùng mô phỏng:

| Cách chạy | Câu hỏi trung bình | Top-1 |
|---|---|---|
| Backward, mọi bộ phận (bảng hiện tại) | 39.7 | 30/30 |
| Backward, đọc cùng mô tả tiếng Việt trước (chỉ đếm câu hỏi thêm) | 36.6 | 30/30 |
| Backward, dừng ở lỗi đầu tiên chứng minh được | 22.2 | 28/30 |
| Trợ lý, mô tả tiếng Việt | 5.8 | 27/30 |

1. **Mô tả bằng lời:** Trợ lý không đếm các triệu chứng đọc được từ mô tả, backward thì không được đọc. Cho backward
   đọc cùng mô tả chỉ giảm còn 36,6 câu, nên lợi thế của Trợ lý không chủ yếu đến từ đây. Nên ghi rõ trong báo cáo.
2. **Cách dừng:** backward chứng minh hết 40 giả thuyết để xếp hạng đầy đủ; Trợ lý dừng khi lỗi đứng đầu đã chứng minh
   được và có xác suất ≥ 0,7. Đây là phần lớn chênh lệch (39,7 → 22,2 nếu backward cũng dừng sớm).
3. **Giới hạn 15 câu (`MAX_QUESTIONS`):** 7/30 kịch bản tiếng Việt chạm giới hạn, gồm cả 3 kịch bản sai (BT02, BT06,
   BT09); tiếng Anh 8/30. Nên nói số câu của Trợ lý bị chặn trên ở 15, còn backward không bị chặn.

Ngoài ra: các câu loại trừ nhau trong `EXCLUSIVE` được điền “Không” tự động và không tính là câu hỏi (hợp lý, nhưng
nên ghi một câu); `MISS`, `NOISE`, `STOP_AT` chọn khi đã xem cả 30 kịch bản, chỉ phần đọc mô tả có tách SE/ET và BT.
Không cần sửa code `interview.py`; đề nghị Lâm hoặc Giang thêm một câu về ba điểm trên vào Discussion.

## 4. Số liệu gửi Giang cho Discussion (5.x, đánh đổi của Trợ lý)

- Backward: 39,7 câu khi hỏi mọi bộ phận, 9,0 câu khi chọn đúng bộ phận (ít hơn 4,4 lần); top-1 30/30, cùng lỗi và CF với forward ở 30/30.
- Trợ lý: 5,8 câu, đúng 27/30 (mô tả tiếng Việt); 6,4 câu, 28/30 (tiếng Anh); không có mô tả: 11,0 câu, 19/30.
- Kịch bản Trợ lý sai: BT02, BT06, BT09 (tiếng Việt); BT01, BT06 (tiếng Anh) — đều là lỗi phanh, giảm xóc chỉ có một triệu chứng phân biệt mà mô tả không nhắc.
- So sánh công bằng hơn: mục 3. Câu gợi ý: “The assistant needs about seven times fewer questions, mostly because it
  stops as soon as the leading fault is proved; backward chaining asks more but never misses a fault the rules can prove.”
- Nguồn: `python src/evaluate.py`, `python src/evaluate_assistant.py`, KB 79 luật, 30 kịch bản.

## 5. Thử bản .exe cuối (tối 14/11)

Mở màn Hỏi đáp, chọn đúng bộ phận, trả lời “Có” cho triệu chứng của kịch bản và “Không” cho câu khác. Số câu mong đợi
lấy từ `evaluation_results.md`.

| Kịch bản | Bộ phận | Lỗi mong đợi | Số câu mong đợi | Kết quả trên .exe | Sáng / Tối đọc rõ? |
|---|---|---|---|---|---|
| SE01 | Khởi động, nhiên liệu | weak_battery | 10 | | |
| ET03 | Động cơ | low_engine_oil | 10 | | |
| ET07 | Truyền động | worn_cvt_belt | 7 | | |
| BT03 | Phanh | brake_fluid_leak | 9 | | |
| BT10 | Lốp, giảm xóc | worn_rear_shock | 11 | | |

Kiểm thêm: nút “Tại sao”, “Câu trước”, “Không biết”, đổi VI/EN giữa chừng vẫn giữ câu trả lời.
