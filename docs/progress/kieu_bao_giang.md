# Tiến độ — Kiều Bảo Giang

Phần chính: forward chaining, xếp hạng bằng certainty factor. Phần phụ: kiểm tra bằng thuật toán Wang. Hệ thống xe: động cơ, truyền động. Phần báo cáo: Methodology (forward chaining, xếp hạng, Wang), Discussion.

Cập nhật lần cuối: 03/11/2026 (nhánh `feature/forward-chaining`). Theo lịch trình và phân công ngày 02/10.

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
| | Nháp Discussion: [docs/report/discussion.md](../report/discussion.md) | Xong (nháp, còn chỗ [TODO] chờ số liệu đánh giá của Khoa) |
| 6 (09/11–15/11) | Gửi Methodology, Discussion cho Lâm; sửa theo góp ý; slide phần forward chaining, xếp hạng, Wang (14/11) | Chưa tới |
| 7 (16/11–22/11) | Thuyết trình Oral 19/11; kiểm tra trích dẫn phần mình | Chưa tới |

## Kết quả hiện tại

- Cơ sở tri thức: 73 triệu chứng, 9 trung gian, 40 lỗi, **76 luật** (Giang 30: EN01–EN18, TR01–TR12). `python src/kb.py`: 0 lỗi.
- Unit test: 57/57 qua (`python -m unittest discover tests`).
- 20 kịch bản (BT, SE): forward chaining top-1 18/20, top-3 18/20. Backward chaining cho cùng kết quả.
- Wang và forward chaining khớp trên 20 kịch bản và 500 bộ triệu chứng ngẫu nhiên.

## Cần người khác

- **Lâm:** 10 kịch bản cho động cơ, truyền động (`scenarios/engine_transmission.json`, tiền tố `ET`), để đánh giá phần luật của Giang. Thêm luật SF14 (sửa SE10), xem `docs/scenario_analysis.md`.
- **Khoa:** thêm luật TS15 (sửa BT10). Script đánh giá có thể dùng `load_scenarios()` trong `src/scenarios.py`.

- Nguồn (04/11): cả 30 luật EN/TR đã có nguồn; mọi link đã được mở lại và kiểm tra nội dung. Một link Partzilla chết đã được thay. EN06 giảm CF 0.6 → 0.5 vì nguồn yếu. Chi tiết: `docs/sources.md`.

## Còn tồn đọng

- `docs/report/discussion.md` còn chỗ [TODO] chờ số liệu đánh giá đầy đủ của Khoa.
- Gửi Methodology, Discussion cho Lâm (09/11) và sửa theo góp ý.
- Phần thuyết trình (slide 14/11, Oral 19/11) làm sau.
