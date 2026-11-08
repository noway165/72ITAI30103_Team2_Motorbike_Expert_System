# Phân tích kết quả 30 kịch bản test (cập nhật 09/11/2026)

Người viết: Giang. Dữ liệu: 30 kịch bản trong [scenarios/](../scenarios/README.md), mỗi file do người **không** viết luật của hệ thống đó soạn:

| Kịch bản | Hệ thống | Luật do | Kịch bản do |
|---|---|---|---|
| BT01–BT10 | Phanh; lốp và giảm xóc | Khoa | Giang |
| SE01–SE10 | Khởi động, nhiên liệu; đánh lửa, điện | Lâm | Giang |
| ET01–ET10 | Động cơ; truyền động | Giang | Lâm |

Cơ sở tri thức lúc chạy: 73 triệu chứng, 9 trung gian, 40 lỗi, 77 luật (đã có SF14 của Lâm). Chạy lại:

```bash
python src/wang.py --scenarios --random 500
```

## 1. Kết quả

| | Số kịch bản | Top-1 đúng | Top-3 đúng | Không ra lỗi nào |
|---|---|---|---|---|
| Phanh, lốp, giảm xóc (BT) | 10 | 9 | 9 | 1 (BT10) |
| Khởi động, nhiên liệu, điện (SE) | 10 | 10 | 10 | 0 |
| Động cơ, truyền động (ET) | 10 | 10 | 10 | 0 |
| **Tổng** | **30** | **29 (96.7%)** | **29 (96.7%)** | 1 |

- Trung bình mỗi kịch bản forward chaining chạy 2.0 luật.
- Backward chaining cho đúng cùng danh sách lỗi và CF như forward chaining trên cả 30 kịch bản. Không chọn bộ phận thì nó hỏi trung bình 39.7 câu (trên 73 triệu chứng); chọn đúng bộ phận của lỗi thì chỉ còn 9.0 câu, và vẫn đúng hạng 1 ở 29/30 kịch bản.
- Wang chứng minh đúng các lỗi forward chaining suy ra, không thừa không thiếu, trên 30 kịch bản và 500 bộ triệu chứng ngẫu nhiên (1239 lỗi được chứng minh). Vậy kịch bản sai còn lại là do **cơ sở tri thức thiếu luật**, không phải do bộ suy luận.
- Không kịch bản nào bị lỗi của hệ thống khác chen vào top-3.

So với lần chạy đầu (04/11, 20 kịch bản, top-1 18/20): SE10 đã đúng nhờ luật SF14 của Lâm; BT10 vẫn chờ luật TS15 của Khoa.

## 2. Kịch bản động cơ và truyền động (ET, luật của Giang)

Cả 10 kịch bản Lâm soạn đều cho lỗi mong đợi ở hạng 1, nên **không cần sửa luật**.

| Kịch bản | Lỗi mong đợi | Hạng 1 (CF) | Luật đã chạy | Lỗi khác |
|---|---|---|---|---|
| ET01 | Lọc gió bẩn | đúng (0.68) | EN01, EN02, EN03 | Bình xăng con chỉnh giàu xăng (0.51) |
| ET02 | Động cơ ăn nhớt | đúng (0.80) | EN07 | |
| ET03 | Thiếu nhớt hoặc nhớt quá hạn | đúng (0.88) | EN06, EN16 | |
| ET04 | Thiếu nước làm mát | đúng (0.96) | EN08, EN09, EN15, EN18 | |
| ET05 | Quạt két nước không chạy | đúng (0.63) | EN08, EN10, EN18 | Thiếu nước làm mát (0.45) |
| ET06 | Họng ga bẩn | đúng (0.55) | EN11 | |
| ET07 | Dây curoa mòn | đúng (0.86) | TR01, TR02, TR12 | |
| ET08 | Dây côn cần chỉnh | đúng (0.94) | TR08, TR11 | |
| ET09 | Côn tay bị trượt | đúng (0.68) | TR01, TR05 | |
| ET10 | Xích thiếu dầu | đúng (0.94) | TR07, TR10 | |

Nhận xét:
- **ET01**: lỗi thứ 2 (bình xăng con) hợp lý, vì xe Wave dùng bình xăng con và khói đen có 2 nguyên nhân chính.
- **ET05**: mô tả nói "nước làm mát vẫn đủ", nhưng chương trình vẫn xếp "thiếu nước làm mát" thứ 2 (CF 0.45, do luật dự phòng EN18). Luật chỉ có dạng khẳng định (Horn clause) nên câu trả lời "nước đủ" không thể hạ CF của lỗi này. Lỗi đúng vẫn đứng đầu, nên giữ nguyên; đây là giới hạn chung, ghi vào phần Discussion.
- **ET06**: CF chỉ 0.55 vì nguồn (Mobil) viết cho ô tô và chết máy khi để ga nhỏ còn nhiều nguyên nhân khác; giữ CF thấp là đúng.
- Các luật dự phòng thêm ngày 03/11 (EN17, EN18, TR12) không làm sai kịch bản nào: TR12 góp thêm CF cho ET07, EN18 chỉ đứng sau lỗi cụ thể hơn ở ET04, ET05.

## 3. Kịch bản sai còn lại: BT10 (luật của Khoa)

Triệu chứng: `rear_shock_bouncy`, `sits_low_parked` (xe Wave hay chở người). Mong đợi: `worn_rear_shock`.

- TS09 chạy, suy ra trung gian `suspension_damping_lost` (CF 0.7).
- Từ trung gian này tới lỗi `worn_rear_shock` cần thêm `tyre_wear_uneven` (TS10) hoặc `suspension_clunk` (TS11). Người lái không có 2 triệu chứng đó, nên chương trình báo "chưa đủ dữ kiện".
- Màn hình Theo triệu chứng (GUI) hiện trung gian đã suy ra và cho bấm thêm 2 triệu chứng còn thiếu để chẩn đoán lại.

**Đề xuất cho Khoa:** thêm luật `TS15: suspension_damping_lost → worn_rear_shock` với CF khoảng 0.7, giống cách Lâm đã sửa SE10 bằng SF14.

## 4. Nguyên nhân chung: trung gian "ngõ cụt"

Cả SE10 (đã sửa) và BT10 cùng một dạng: luật suy ra được **trung gian**, nhưng mọi luật đi tiếp từ trung gian đó đều cần thêm một triệu chứng phụ. Thiếu triệu chứng phụ thì chương trình dừng giữa chừng, dù đã biết khá chắc vấn đề nằm ở đâu.

| Trung gian | File | Tới được lỗi khi đứng một mình? |
|---|---|---|
| `suspension_damping_lost` | tyres_suspension (Khoa) | Không → gây ra BT10 |
| `brake_hydraulic_loss` | brakes (Khoa) | Không (BR08 cần thêm tay phanh mềm) |
| `low_electrical_power` | starting_fuel (Lâm) | Có, SF14 (sửa 05/11) |
| `no_electrical_power` | starting_fuel (Lâm) | Không |
| `cranks_but_no_start` | starting_fuel (Lâm) | Không |
| `ignition_misfire_suspected` | ignition_electrical (Lâm) | Không |
| `rich_running` | engine (Giang) | Có, EN03 (bình xăng con) và EN17 (FI), sửa 03/11 |
| `engine_overheating` | engine (Giang) | Có, EN18 (sửa 03/11) |
| `drive_slipping` | transmission (Giang) | Có, TR05 (côn tay) và TR12 (tay ga), sửa 03/11 |

## 5. Đề xuất cho cả nhóm

1. **Khoa:** thêm TS15 (sửa BT10); cân nhắc luật dự phòng cho `brake_hydraulic_loss`.
2. **Lâm:** cân nhắc luật dự phòng cho `no_electrical_power`, `cranks_but_no_start`, `ignition_misfire_suspected`.
3. **Báo cáo:** nêu rõ khi có chọn bộ phận, backward chaining hỏi ít hơn khoảng 4 lần (9.0 so với 39.7 câu) mà độ chính xác không đổi.
