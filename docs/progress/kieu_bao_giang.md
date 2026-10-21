# Tiến độ — Kiều Bảo Giang

Phần chính: forward chaining, xếp hạng bằng certainty factor. Phần phụ: kiểm tra bằng thuật toán Wang. Hệ thống xe: động cơ, truyền động.

Cập nhật lần cuối: 21/10/2026 (nhánh `feature/forward-chaining`).

## Theo mốc thời gian

| Mốc (đề cương) | Việc của Giang | Trạng thái |
|---|---|---|
| 02/10 – 09/10: thu thập kiến thức, chốt danh sách triệu chứng và lỗi | Danh sách triệu chứng, kết luận trung gian và lỗi cho động cơ và truyền động | Xong (21/10) |
| 10/10 – 16/10: cơ sở tri thức v1 (khoảng 40 luật) và forward chaining | `knowledge_base/engine.json` (12 luật EN01–EN12), `knowledge_base/transmission.json` (8 luật TR01–TR08) | Xong (21/10, trễ 5 ngày) |
| | `src/forward_chaining.py`: forward chaining + xếp hạng CF, dòng lệnh chạy thử | Xong (21/10, trễ 5 ngày) |
| | `tests/test_forward_chaining.py`: 12 test (công thức CF, xếp hạng, ngưỡng, 12 kịch bản trên cơ sở tri thức thật) | Xong (21/10) |
| | Chốt cách kết hợp CF (`docs/kb_format.md`, `docs/forward_chaining.md`) | Xong (21/10) |
| 17/10 – 22/10: chuẩn bị thuyết trình Logical Agents | Demo tương tác Wumpus World (chứng minh B ⇔ (P ∨ P), kiểm tra mô hình, chu trình tác tử KB) | Xong (21/10), dùng cho buổi 22/10 |
| 23/10 – 30/10: backward chaining, giải thích; mở rộng cơ sở tri thức | Hỗ trợ Khoa dùng chung CF; bổ sung nguồn cho luật EN/TR còn thiếu | Chưa tới |
| 31/10 – 06/11: kịch bản test, đánh giá, kiểm tra bằng Wang, GUI | Kiểm tra bằng thuật toán Wang: KB + triệu chứng ⊨ lỗi, so với forward chaining | Chưa tới |

## Kết quả hiện tại

- Cơ sở tri thức: 49 triệu chứng, 7 trung gian, 27 lỗi, **40 luật** (Lâm 20, Giang 20). `python src/kb.py`: 0 lỗi; cảnh báo chỉ còn luật chưa có nguồn.
- Unit test: 27/27 qua (`python -m unittest discover tests`).
- 12 kịch bản trên cơ sở tri thức thật đều cho lỗi mong đợi ở vị trí số 1 (top-1).

## Còn tồn đọng

- 9 luật EN/TR chưa có nguồn đủ tin cậy (EN04, EN06, EN10, EN11, EN12, TR01–TR04), xem `docs/sources.md`. Cần hỏi thợ hoặc tìm sổ tay sửa chữa trước khi nộp báo cáo.
- Các link nguồn lấy từ kết quả tìm kiếm; nên mở lại từng link để kiểm tra trước khi đưa vào báo cáo.
- `has_clutch_lever` hiện đặt trong `transmission.json`; nếu phần khác cũng cần, có thể chuyển sang `vehicle.json` (file chung, cần cả nhóm đồng ý).
