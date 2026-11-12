# Tiến độ — Kiều Bảo Giang

Phần chính: forward chaining, xếp hạng bằng certainty factor. Phần phụ: kiểm tra bằng thuật toán Wang. Hệ thống xe: động cơ, truyền động. Phần báo cáo: Methodology (forward chaining, xếp hạng, Wang), Discussion.

Cập nhật lần cuối: 12/11/2026 (nhánh `feature/motologic`). Theo lịch trình ngày 02/10 và phân công ngày 09/11, 12/11.

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
| | Thử file .exe (`build_exe.bat`, 09/11): chọn kịch bản mẫu trên màn Theo triệu chứng | Xong: 7 kịch bản đều đúng như khi chạy bằng Python (bảng dưới) |
| 7 (16/11–22/11) | Thuyết trình Oral 19/11; kiểm tra trích dẫn phần mình | Chưa tới |

## Phân công ngày 12/11 (PhanCong_Nhom2_12-11.pdf)

| Việc | Trạng thái |
|---|---|
| A. Bảng màu MotoLogic trong `src/theme.py` (giữ khoá cũ; thêm `panel`, `panel_soft`, `on_panel`, `panel_muted`, `lime`, `lime_soft`, `on_lime`), Sáng và Tối cùng bộ khoá | Xong |
| A. `src/gui_widgets.py`: `RoundCard`, `PillButton`, `Stepper`, `ChoiceCard`, `CheckRow`, `Gauge` (đồng hồ CF), icon vẽ tay cho xe và 6 bộ phận | Xong |
| A. `src/gui.py`: thanh bên sáng (MotoLogic, Làm việc / Màn cũ, thẻ số luật và lỗi lấy từ cơ sở tri thức, VI/EN, Sáng/Tối), thanh trên (đường dẫn, mã phiên, "Chạy offline"); màn mở đầu là Chẩn đoán | Xong |
| A. `src/gui_diagnosis.py`: 3 bước, 3 cách (hỏi đáp của Khoa, chọn triệu chứng, kể bằng lời của Lâm), kết quả có đồng hồ CF, chuỗi luật, bước tiếp theo, Wang, "Cũng có thể là", gợi ý khi chưa đủ dữ kiện | Xong |
| A. `src/gui_history.py`: lịch sử phiên, bấm để mở lại kết quả | Xong |
| A. `tests/test_gui_diagnosis.py`: SE01 bằng cả 3 cách ra Ắc quy yếu và Wang ✓; BT03 ra Rò rỉ dầu phanh, cần thợ; đổi VI/EN và Sáng/Tối giữa chừng không mất câu trả lời; toàn bộ test qua; `build_exe.bat` build được | Xong |
| B. Methodology còn 247 từ + Chapter conclusion (`docs/report/methodology_giang.md`) | Xong |
| B. Discussion còn 280 từ + Chapter conclusion, thêm đoạn đánh đổi của Trợ lý (5,8 câu, 27/30 so với 39,7 câu, 30/30) | Xong |
| B. Số liệu mới: 79 luật, top-1 30/30 | Xong |
| B. 3 hình: `fig_cf_example.png`, `fig_wang_proof.png`, `fig_dead_end.png` (`python src/report_figures.py`, mọi số lấy từ cơ sở tri thức) | Xong |
| B. 4 ảnh MotoLogic: `docs/report/figures/fig_motologic_1_setup.png` … `_4_result.png` | Xong |
| C. Slide và lời thoại phần Forward + Wang theo số mới, kèm kịch bản demo SE01 và BT03 (`docs/slides/`) | Xong |

## Kết quả hiện tại

- Cơ sở tri thức: 73 triệu chứng, 9 trung gian, 40 lỗi, **79 luật**. `python src/kb.py`: 0 lỗi.
- 30 kịch bản: top-1 30/30 với forward và backward chaining; Wang khớp forward chaining trên 30 kịch bản và 500 bộ ngẫu nhiên.

## Còn lại

- Gửi Lâm phần báo cáo và hình (đã có trong PR); Lâm duyệt, merge, build `.exe` cuối (tối 14/11).
- Tập demo 2 phút theo `docs/slides/giang_script.md`; vấn đáp 16/11.
