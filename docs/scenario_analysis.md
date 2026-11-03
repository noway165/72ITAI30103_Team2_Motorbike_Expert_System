# Phân tích kịch bản chẩn đoán sai (02/11 – 04/11/2026)

Người viết: Giang. Dữ liệu: 20 kịch bản Giang soạn cho hệ thống của Lâm (`SE01–SE10`) và Khoa (`BT01–BT10`), xem [scenarios/README.md](../scenarios/README.md). Chạy lại:

```bash
python src/wang.py --scenarios --random 500
```

10 kịch bản động cơ và truyền động (Lâm soạn) chưa có trong repo, nên phần đánh giá hệ thống của Giang sẽ bổ sung khi có.

## 1. Kết quả forward chaining

| | Số kịch bản | Top-1 đúng | Top-3 đúng | Không ra lỗi nào |
|---|---|---|---|---|
| Phanh, lốp, giảm xóc (BT) | 10 | 9 | 9 | 1 (BT10) |
| Khởi động, nhiên liệu, điện (SE) | 10 | 9 | 9 | 1 (SE10) |
| **Tổng** | **20** | **18 (90%)** | **18 (90%)** | 2 |

- Backward chaining (`backward_chain`, không giới hạn hệ thống) cho đúng cùng danh sách lỗi và CF như forward chaining trên cả 20 kịch bản.
- Wang chứng minh đúng các lỗi forward chaining suy ra, không thừa không thiếu (20 kịch bản + 500 bộ ngẫu nhiên, xem [wang.md](wang.md)). Vậy 2 kịch bản sai là do **cơ sở tri thức thiếu luật**, không phải do bộ suy luận.
- Không kịch bản nào bị lỗi của hệ thống khác chen vào top-3. Lỗi thứ 2 xuất hiện ở BT03 (`brake_air_in_lines`, CF 0.74, sau `brake_fluid_leak` 0.90) và BT09 (`weak_fork_spring_or_oil`, 0.65, sau `fork_seal_leak` 0.85); cả hai đều hợp lý về kỹ thuật.

## 2. Hai kịch bản sai

### BT10: giảm xóc sau yếu (luật của Khoa)

Triệu chứng: `rear_shock_bouncy`, `sits_low_parked` (xe Wave hay chở người). Mong đợi: `worn_rear_shock`.

- TS09 chạy, suy ra trung gian `suspension_damping_lost` (CF 0.7).
- Nhưng từ trung gian này tới lỗi `worn_rear_shock` cần thêm `tyre_wear_uneven` (TS10) hoặc `suspension_clunk` (TS11). Người lái không có 2 triệu chứng đó, nên chương trình báo "không có lỗi nào".

**Đề xuất cho Khoa:** thêm luật `TS15: suspension_damping_lost → worn_rear_shock` với CF khoảng 0.7. TS10, TS11 vẫn giữ để tăng CF khi có thêm bằng chứng.

### SE10: ắc quy hết điện (luật của Lâm)

Triệu chứng: `starter_clicks_or_silent`, `horn_weak` (ắc quy 1 năm, tối qua quên tắt khóa). Mong đợi: `weak_battery`.

- SF01 chạy, suy ra `low_electrical_power` (CF 0.9).
- SF02, SF03 cần thêm "ắc quy hơn 2 năm" hoặc "xe để lâu hơn 2 tuần". Ắc quy bị xả cạn vì quên tắt khóa không khớp luật nào, nên không ra lỗi.

**Đề xuất cho Lâm:** thêm luật `SF14: low_electrical_power → weak_battery` với CF khoảng 0.6. Đây vẫn là nguyên nhân thường gặp nhất của "đề tạch tạch, còi yếu"; SF02, SF03 nâng CF khi có thêm bằng chứng.

## 3. Nguyên nhân chung: trung gian "ngõ cụt"

Cả 2 lỗi cùng một dạng: luật suy ra được **trung gian**, nhưng mọi luật đi tiếp từ trung gian đó đều cần thêm một triệu chứng phụ. Thiếu triệu chứng phụ thì chương trình dừng giữa chừng, dù đã biết khá chắc vấn đề nằm ở đâu.

Kiểm tra toàn bộ cơ sở tri thức (trung gian đứng một mình, cộng thêm loại xe, có tới được lỗi nào không):

| Trung gian | File | Tới được lỗi khi đứng một mình? |
|---|---|---|
| `suspension_damping_lost` | tyres_suspension (Khoa) | Không → gây ra BT10 |
| `brake_hydraulic_loss` | brakes (Khoa) | Không (BR08 cần thêm tay phanh mềm) |
| `low_electrical_power` | starting_fuel (Lâm) | Không → gây ra SE10 |
| `no_electrical_power` | starting_fuel (Lâm) | Không |
| `cranks_but_no_start` | starting_fuel (Lâm) | Không |
| `ignition_misfire_suspected` | ignition_electrical (Lâm) | Không |
| `rich_running` | engine (Giang) | Chỉ xe bình xăng con (EN03); xe FI thì không |
| `engine_overheating` | engine (Giang) | Không |
| `drive_slipping` | transmission (Giang) | Chỉ xe có tay côn (TR05); xe tay ga thì không |

## 4. Đã sửa ở hệ thống của Giang (03/11)

Áp dụng bài học trên cho động cơ và truyền động. Mỗi trung gian có thêm một luật "dự phòng" với CF thấp hơn, chỉ ra nguyên nhân thường gặp nhất:

| Luật | Nội dung | CF | Ví dụ trước → sau |
|---|---|---|---|
| EN17 | `rich_running` ∧ `is_fuel_injected` → `clogged_air_filter` | 0.5 | Xe FI khói đen, hao xăng: không có lỗi → lọc gió (0.42) |
| EN18 | `engine_overheating` → `low_coolant` | 0.5 | Chỉ đèn nhiệt độ sáng: không có lỗi → thiếu nước làm mát (0.45) |
| TR12 | `drive_slipping` ∧ `is_scooter` → `worn_cvt_belt` | 0.55 | Tay ga rú ga mà chậm: không có lỗi → dây curoa (0.49) |

Khi có thêm triệu chứng phụ, luật cũ vẫn xếp lỗi cụ thể hơn lên đầu (ví dụ đèn nhiệt độ + quạt không quay: `cooling_fan_problem` 0.63 trên `low_coolant` 0.45). Test mới: `test_engine_and_transmission_intermediates_always_reach_a_fault`.

Chạy lại sau khi sửa (04/11): 57/57 unit test qua; 20 kịch bản: top-1 18/20 (2 kịch bản sai chờ Lâm, Khoa sửa luật); Wang và forward chaining khác nhau 0 lần trên 20 kịch bản và 500 bộ ngẫu nhiên.

## 5. Đề xuất cho cả nhóm

1. **Lâm, Khoa:** thêm luật dự phòng cho các trung gian ngõ cụt ở bảng mục 3 (ít nhất TS15 và SF14 để sửa BT10, SE10).
2. **Lâm (bộ kiểm tra luật):** thêm cảnh báo "trung gian không tới được lỗi nào khi đứng một mình", để bắt lỗi dạng này sớm.
3. **Lâm (GUI):** khi không lỗi nào đạt ngưỡng, hiện các trung gian đã suy ra được (ví dụ "Điện yếu: ắc quy không đủ điện để đề") thay vì chỉ báo "không tìm thấy lỗi".
4. **Khoa (script đánh giá):** backward chaining khi không giới hạn hệ thống hỏi 36–45 câu trên 73 triệu chứng mỗi kịch bản. Nên đo thêm số câu hỏi khi chọn đúng hệ thống (`--subsystem`), để báo cáo có số liệu so sánh.
