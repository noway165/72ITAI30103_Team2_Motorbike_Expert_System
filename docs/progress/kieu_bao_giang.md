# Tiến độ — Kiều Bảo Giang

Phần chính: forward chaining, xếp hạng bằng certainty factor. Phần phụ: kiểm tra bằng thuật toán Wang. Hệ thống xe: động cơ, truyền động. Phần báo cáo: Methodology (forward chaining, xếp hạng, Wang), Discussion.

Cập nhật lần cuối: 09/11/2026 (nhánh `feature/forward-chaining`). Theo lịch trình ngày 02/10 và danh sách việc ngày 09/11.

## Theo lịch

| Tuần | Việc của Giang | Trạng thái |
|---|---|---|
| 1 (05/10–11/10) | Tài liệu động cơ, truyền động; góp ý JSON; đề xuất cách tính CF; danh sách lỗi và luật mẫu | Xong |
| 2 (12/10–18/10) | `forward_chaining.py` có unit test; luật động cơ, truyền động (20 luật EN01–EN12, TR01–TR08); CF và xếp hạng | Xong (21/10, trễ 5 ngày) |
| 3 (19/10–25/10) | Slide và thuyết trình Logical Agents (22/10) | Xong |
| | 10 kịch bản test cho phanh, lốp, giảm xóc (hệ thống của Khoa): `scenarios/brakes_tyres_suspension.json` | Xong |
| | Thêm 7 luật: EN13–EN16, TR09–TR11 | Xong |
| 4 (26/10–01/11) | Thuật toán Wang: `src/wang.py`, ví dụ nhỏ có unit test (`tests/test_wang.py`) | Xong |
| | 10 kịch bản test cho khởi động, nhiên liệu, điện (hệ thống của Lâm): `scenarios/starting_fuel_electrical.json` | Xong |
| | Wang trên cơ sở tri thức thật, so với forward chaining trên kịch bản và 500 bộ ngẫu nhiên: khớp 100% | Xong |
| 5 (02/11–08/11) | Phân tích kịch bản chẩn đoán sai, đề xuất sửa luật: [docs/scenario_analysis.md](../scenario_analysis.md) | Xong |
| | Sửa luật của mình theo kết quả: thêm EN17, EN18, TR12 (luật dự phòng cho trung gian "ngõ cụt") | Xong |
| | Chạy lại Wang sau khi sửa luật | Xong |
| | Nháp Methodology: [docs/report/methodology_giang.md](../report/methodology_giang.md) | Xong (nháp) |
| | Nháp Discussion: [docs/report/discussion.md](../report/discussion.md) | Xong; [TODO] đã điền bằng số đo 30 kịch bản (09/11) |
| 6 (09/11–15/11) | Màn hình Theo triệu chứng: `src/gui_forward.py` (`ForwardPage`), unit test `tests/test_gui_forward.py` | Xong |
| | Sửa test CF ắc quy trên nhánh `feature/sf14` (SF02, SF03, SF14) | Xong |
| | Xem 10 kịch bản ET của Lâm: 10/10 đúng hạng 1, không cần sửa luật | Xong |
| | Cập nhật `docs/scenario_analysis.md`, Methodology, Discussion với 30 kịch bản | Xong |
| | Slide và lời thoại phần forward chaining, CF, Wang: `docs/slides/` | Xong (chờ Lâm ghép) |
| | Thử file .exe | Build được, mở đúng màn Theo triệu chứng; còn chạy tay 5 kịch bản |
| 7 (16/11–22/11) | Thuyết trình Oral 19/11; kiểm tra trích dẫn phần mình | Chưa tới |

## Kết quả hiện tại

- Cơ sở tri thức: 73 triệu chứng, 9 trung gian, 40 lỗi, **77 luật** (Giang 30: EN01–EN18, TR01–TR12). `python src/kb.py`: 0 lỗi.
- Unit test: 83 test qua, 1 bỏ qua (`python -m unittest discover tests`).
- 30 kịch bản (BT, SE, ET): forward chaining top-1 29/30, top-3 29/30. Backward chaining cho cùng kết quả.
- Wang và forward chaining khớp trên 30 kịch bản và 500 bộ triệu chứng ngẫu nhiên.
- Nguồn: cả 30 luật EN/TR đã có nguồn đã kiểm tra (`docs/sources.md`).

## Cần người khác

- **Khoa:** thêm luật TS15 (sửa BT10, kịch bản sai duy nhất còn lại). Khi script đánh giá trong `results/` xong, đối chiếu với số trong `docs/report/discussion.md`.
- **Lâm:** merge `feature/sf14` trước nhánh này; ghép slide `docs/slides/giang_forward_wang.pptx`.

## Còn tồn đọng

- Chạy tay 5 kịch bản trên file .exe (xem `docs/slides/giang_script.md` không cần; danh sách trong tin nhắn PR).
- Sửa phần viết theo góp ý của Lâm; thuyết trình Oral 19/11.
