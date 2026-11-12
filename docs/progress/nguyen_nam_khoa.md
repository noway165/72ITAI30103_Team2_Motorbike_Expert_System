# Tiến độ của Khoa

Kiểm thử: `python -m unittest discover tests`, `python src/kb.py`.

## Phân công v4 (12/11 khuya), nhánh `feature/khoa-v4`

| Việc | Trạng thái |
|---|---|
| K1. Ch3 `methodology_khoa.md` ≤ 120 từ + 1 hình | Xong: 115 từ, giữ `fig_backward_flow.png`, thêm nửa câu “9,0 thay vì 39,7 câu” |
| K2. Ch4: kiểm tra phần Lâm đã sửa | Đồng ý. Đã chạy lại `evaluate.py`, `evaluate_assistant.py`: mọi số khớp (5,5 câu 30/30; giữ riêng 10,8 / 11,5 câu, 8/10 và 7/10; dòng xe 9/9, bỏ dòng xe 4/9). Thêm 1 câu về đảo câu trả lời (K6); 191 từ |
| K3. Thử bản .exe mới, 5 kịch bản + 1 kịch bản dòng xe | Bảng mục 5: số mong đợi đã tính lại trên KB mới; Khoa chạy .exe và điền |
| K4. Đo lại bảng so sánh công bằng | Xong (mục 3), `python tools/compare_fair.py`; gửi Giang mục 4 |
| K5. Thử chat trên động cơ, truyền động (5 cuộc) | Xong (mục 7); 5 góp ý cho Lâm |
| K6. (tuỳ chọn) Đảo 10–20% câu trả lời | Xong (mục 6), `python tools/compare_fair.py --noise` |

## Phân công 12/11 (đã merge, PR #18)

| Việc | Trạng thái |
|---|---|
| A1. Màn Hỏi đáp đọc rõ ở Sáng và Tối (`src/theme.py`) | Xong, có test `tests/test_theme_contrast.py` |
| A2. Hỗ trợ Giang nối `BackwardSession` vào màn Chẩn đoán (bước 2a) | Đã kiểm code của Giang, chạy đúng; thêm `fixed=` (mục 2) |
| A3. Đọc lại `src/interview.py`, góp ý cách so sánh số câu hỏi | Xong (mục 3) |
| A4. Thêm cột Trợ lý vào `fig_backward_questions.png` | Xong (`python src/evaluate.py --charts`) |
| B1, B2. Chapter 4 khoảng 200 từ, bảng chung | Xong |
| C1, C2. Slide, lời thoại, demo BT03 | `docs/slides/khoa_backward_eval.pptx`, `docs/slides/khoa_script.md` (số liệu Trợ lý trong slide là của 12/11, sửa khi làm slide) |

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

## 3. So sánh công bằng backward và Trợ lý (đo lại 13/11, K4)

KB 79 triệu chứng, 88 luật; NLU mới. Chạy `python tools/compare_fair.py`. Câu hỏi về dòng xe không tính (chọn ở bước 1).

| Cách chạy | 30 kịch bản: câu hỏi | Top-1 | 10 mô tả giữ riêng: câu hỏi | Top-1 |
|---|---|---|---|---|
| Backward, mọi bộ phận | 39.7 | 30/30 | 36.4 | 10/10 |
| Backward, đúng bộ phận | 9.0 | 30/30 | 8.3 | 10/10 |
| Backward, đọc cùng mô tả tiếng Việt trước (chỉ đếm câu hỏi thêm) | 36.3 | 30/30 | 35.7 | 10/10 |
| Backward, dừng ở lỗi đầu tiên chứng minh được | 22.2 | 28/30 | 24.8 | 10/10 |
| Trợ lý, mô tả tiếng Việt | 5.5 | 30/30 | 10.8 | 8/10 |
| Trợ lý, mô tả tiếng Anh | 5.5 | 30/30 | 11.5 | 7/10 |

Ba điểm làm so sánh 39,7 với 5,5 câu chưa ngang nhau:

1. **Mô tả bằng lời:** Trợ lý không đếm triệu chứng đọc từ mô tả. Cho backward đọc cùng mô tả chỉ giảm còn 36,3 câu,
   nên lợi thế của Trợ lý không chủ yếu đến từ đây.
2. **Cách dừng:** backward chứng minh hết 40 giả thuyết; Trợ lý dừng khi lỗi đứng đầu đã chứng minh được và đủ xác suất.
   Backward dừng sớm còn 22,2 câu nhưng chỉ đúng 28/30.
3. **Giới hạn 15 câu:** 7/30 kịch bản chạm giới hạn (BT02, BT05, BT06, BT09, ET06, ET08, ET09), vẫn đúng. Ở tập giữ riêng
   5/10 (vi) và 6/10 (en) chạm giới hạn, gồm mọi kịch bản sai: HO05 (bó phanh), HO08 (rò phớt phuộc), HO10 (bạc cổ lái, chỉ en).

Trên tập giữ riêng (mô tả Trợ lý chưa từng thấy), khoảng cách hẹp lại: 10,8 câu so với 8,3 câu của backward đúng bộ phận,
và backward đúng 10/10.

## 4. Số liệu gửi Giang cho Discussion (G3)

- Backward: 39,7 câu mọi bộ phận, 9,0 câu đúng bộ phận (ít hơn 4,4 lần); top-1 30/30, cùng lỗi và CF với forward.
- Trợ lý: 5,5 câu, 30/30 trên 30 kịch bản (mô tả đã dùng khi viết NLU); tập giữ riêng 10,8 câu 8/10 (vi), 11,5 câu 7/10 (en).
- So sánh công bằng (mục 3): backward đọc cùng mô tả vẫn 36,3 câu; backward dừng sớm 22,2 câu, 28/30; trên tập giữ riêng
  backward đúng bộ phận 8,3 câu 10/10, Trợ lý 10,8 câu 8/10.
- Câu gợi ý cho 5.2 (26 từ): “The comparison favours the assistant: on held-out descriptions it asks 10.8 questions and
  finds 8 of 10 faults, while backward chaining on the chosen part asks 8.3 and finds all.”
- Đảo câu trả lời (mục 6), nếu cần cho 5.3: đảo 10% thì backward đúng bộ phận còn 76%, Trợ lý 92%.

## 5. Thử bản .exe mới (K3, tối 14/11)

Màn Chẩn đoán → Hỏi đáp từng câu; chọn bộ phận ở thẻ “Sự cố nằm ở đâu?”. Trả lời “Có” cho triệu chứng của kịch bản,
“Không” cho câu khác. Số câu mong đợi tính trên KB mới bằng `BackwardSession` (đã khai loại xe ở bước 1).

| Kịch bản | Xe (bước 1) | Bộ phận | Trả lời Có | Mong đợi | Kết quả trên .exe | Sáng / Tối |
|---|---|---|---|---|---|---|
| SE01 | Tay ga, FI, Xe khác | Khởi động, nhiên liệu | đề chỉ tạch tạch; còi yếu; ắc quy hơn 2 năm | Ắc quy yếu, CF 0.89, 9 câu | | |
| ET03 | Xe số, bình xăng con | Động cơ | máy gõ lạch cạch; quá hạn thay nhớt; nhớt đen đặc | Thiếu nhớt, CF 0.88, 13 câu | | |
| ET07 | Tay ga, FI | Truyền động | rú ga nhưng tăng tốc chậm; curoa quá mốc thay | Dây curoa mòn, CF 0.86, 9 câu | | |
| BT03 | Xe số, FI | Phanh | tay phanh mềm; dầu phanh dưới MIN; rỉ dầu phanh | Rò rỉ dầu phanh, CF 0.96, 9 câu | | |
| BT10 | Xe số, bình xăng con | Lốp, giảm xóc | giảm xóc sau nảy nhiều; xe đứng thấp | Giảm xóc sau yếu, CF 0.49, 12 câu | | |
| MS04 (dòng xe) | Honda Vision | Động cơ | máy gõ lạch cạch | Thiếu nhớt, CF 0.65 (luật MD04), khoảng 9 câu; có khối “Riêng cho Honda Vision” | | |

Bản thử 12/11 (trước khi có dòng xe): SE01 ra Ắc quy yếu, CF 0.89, Wang chứng minh được, chế độ Sáng đọc rõ.
Kiểm thêm: “Tại sao”, “Câu trước”, “Không biết”, đổi VI/EN và Sáng/Tối giữa chừng vẫn giữ câu trả lời.

## 6. Đảo 10–20% câu trả lời (K6)

Mỗi câu trả lời (trừ loại xe) bị đảo với xác suất 10% hoặc 20%; 30 kịch bản × 20 lần chạy. `python tools/compare_fair.py --noise`
(khoảng 12 phút). Tỉ lệ lỗi mong đợi đứng đầu / số câu hỏi trung bình:

| Tỉ lệ đảo | Backward, mọi bộ phận | Backward, đúng bộ phận | Trợ lý, mô tả tiếng Việt | Trợ lý, không mô tả |
|---|---|---|---|---|
| 0% | 100% / 39.7 | 100% / 9.0 | 100% / 5.5 | 66.7% / 10.9 |
| 10% | 46.7% / 41.8 | 75.8% / 9.0 | 91.7% / 5.9 | 42.7% / 11.9 |
| 20% | 26.3% / 44.2 | 53.2% / 9.2 | 80.3% / 6.3 | 26.0% / 11.5 |

Nhận xét: càng hỏi nhiều câu thì càng dễ gặp câu trả lời sai, nên backward mọi bộ phận giảm mạnh nhất; một “Có” sai có thể
chứng minh một lỗi khác với CF cao hơn. Trợ lý có mô tả bền hơn một phần vì triệu chứng đọc từ mô tả không bị đảo (chỉ đảo
câu trả lời), nên cột “không mô tả” mới là so sánh ngang với backward. Ch4 dùng một câu: đảo 10% thì 76% và 92%.

## 7. Thử chat “Kể bằng lời” trên động cơ, truyền động (K5)

Năm cuộc trò chuyện tự viết (không lấy từ `scenarios/`), chạy qua `chat.start` / `chat.respond` như cửa sổ thật; trả lời theo
triệu chứng của lỗi định sẵn, mỗi cuộc có ít nhất một câu hỏi lại.

| # | Xe | Câu gõ đầu tiên | Bot hiểu đúng không | Câu hỏi lại và trả lời | Lỗi cuối cùng |
|---|---|---|---|---|---|
| 1 | Xe số, bình xăng con | “Xe số nhà em mấy bữa nay chạy nghe tiếng tạch tạch ở bánh sau, nhìn sên thấy khô rang, có chỗ rỉ sét” | Một nửa: đúng “xích khô, gỉ sét”; sai “tạch tạch ở bánh sau” thành “bấm đề chỉ nghe tạch tạch” | “tại sao hỏi câu này?” → nêu luật SF01 (còi yếu): đúng theo điều bot hiểu nhưng lạc đề. “còn khả năng nào khác không?” → danh sách hợp lý | Đúng: Xích thiếu dầu bôi trơn, CF 0.94, 4 câu |
| 2 | Tay ga, FI | “Lên dốc em vặn hết ga máy gào to mà xe cứ ì ì, bò lên chậm rì” | Không: “chưa nhận ra triệu chứng nào” | “sao lại hỏi cái đó?” → nêu luật TR01, hợp lý. “sửa thế nào?” → cách xử lý + luật TR12, hợp lý | Đúng: Dây curoa mòn, CF 0.49, sau 15 câu |
| 3 | Xe số, FI | “Pô xe em nhả khói trắng xanh, mà chưa tới lúc thay nhớt đã thấy hụt nhớt rồi” | Gần đúng: đúng khói và hụt nhớt; sai “chưa tới lúc thay nhớt” thành “đã quá hạn thay nhớt” | “làm sao biết là ăn nhớt?” → 2 triệu chứng + luật EN07, hợp lý. “xéc-măng là gì?” → trả về lỗi có chữ đó, không giải thích từ | Đúng: Động cơ ăn nhớt, CF 0.80, 7 câu |
| 4 | Tay ga, bình xăng con (tiếng Anh) | “My scooter keeps dying whenever I stop at a red light, it just cuts out at idle” | Sai: hiểu thành “máy chạy không đều”, không phải “tắt máy khi ga nhỏ” | “why do you ask?” → liệt kê luật IE01, IE02, SF11, SF12, hợp lý. “how do I fix it?” → gợi ý bugi, có ghi “chưa luật nào chứng minh” | Sai: hết 15 câu, không ra lỗi (mong đợi: bình xăng con bẩn / ga-răng-ti thấp) |
| 5 | Xe số, FI | “Xe côn tay của em lên ga thì vòng tua vọt lên mà xe không đi nhanh theo, như bị tuột” | Một phần: chỉ nhận “có tay côn”, không nhận triệu chứng trượt | “tại sao?” → nêu luật đang xét, hợp lý. “còn lỗi nào khác không?” → danh sách hợp lý | Đúng: Côn tay bị trượt, CF 0.68, sau 15 câu |

Kết quả: 4/5 ra đúng lỗi; các câu hỏi lại đều được trả lời từ luật. Góp ý cho Lâm (`nlu.py`, `chat.py`, chưa sửa vì là file của Lâm):

1. “chưa thấy” không được nhận là câu trả lời “Không” (10 lần trong 5 cuộc); nên thêm “chưa thấy”, “không thấy”.
2. “tạch tạch” nên chỉ khớp triệu chứng đề khi có “đề”, “khởi động”, “nổ máy” gần đó.
3. Thiếu cách nói về trượt truyền động: “máy gào / rú mà xe ì”, “vòng tua vọt lên mà xe không đi nhanh”.
4. Tiếng Anh: “dies / cuts out at a red light, at idle” phải ra “tắt máy khi ga nhỏ”, không phải “máy chạy không đều”.
5. Phủ định “chưa tới lúc thay nhớt” bị hiểu thành khẳng định.
