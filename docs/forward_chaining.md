# Forward chaining và certainty factor

Phụ trách: Giang. Mã nguồn: [`src/forward_chaining.py`](../src/forward_chaining.py), test: [`tests/test_forward_chaining.py`](../tests/test_forward_chaining.py).

## 1. Ý tưởng

Forward chaining là suy luận hướng dữ liệu (data-driven): người lái khai báo trước các triệu chứng đúng, bộ suy luận cho chạy mọi luật có **tất cả** điều kiện đúng, thêm kết luận vào bộ nhớ làm việc, rồi lặp lại cho tới khi không suy ra thêm được gì. Cuối cùng các lỗi suy ra được xếp hạng theo certainty factor (CF).

## 2. Thuật toán

Phần chạy luật theo PL-FC-ENTAILS? trong AIMA, chương 7:

1. Mỗi luật giữ `count` = số điều kiện chưa biết là đúng.
2. `agenda` (hàng đợi) ban đầu chứa các triệu chứng người lái trả lời "có".
3. Lấy một ký hiệu `p` ra khỏi agenda (bỏ qua nếu đã xử lý). Với mỗi luật có `p` làm điều kiện, giảm `count`; khi `count` về 0 thì luật chạy (fire), kết luận được đưa vào agenda.
4. Dừng khi agenda rỗng.

Mỗi ký hiệu chỉ được xử lý một lần, nên thời gian chạy tỉ lệ với tổng kích thước các luật.

Triệu chứng trả lời "không" hoặc chưa hỏi được coi là **không đúng**, nên luật cần chúng không chạy (luật là Horn clause, không có phủ định).

## 3. Certainty factor

| Trường hợp | Công thức |
|---|---|
| Triệu chứng người lái trả lời "có" | CF = 1.0 (hoặc CF người lái tự đánh giá, trong (0, 1]) |
| Điều kiện của luật (AND) | CF(điều kiện) = min(CF của từng điều kiện) |
| Kết luận của một luật | CF = `cf` của luật × CF(điều kiện) |
| Nhiều luật cùng kết luận | CF = CF₁ + CF₂ × (1 − CF₁), gộp lần lượt từng luật (thứ tự không ảnh hưởng kết quả) |
| Ngưỡng báo lỗi | CF ≥ 0.2 (đổi được bằng tham số `threshold`) |

Đây là cách của hệ chuyên gia MYCIN (Buchanan & Shortliffe, 1984), chỉ dùng phần bằng chứng dương vì luật của nhóm không có phủ định.

CF được tính **sau** khi chạy xong các luật, theo thứ tự phụ thuộc: một ký hiệu do nhiều luật kết luận được gộp CF xong rồi mới dùng làm điều kiện cho luật tiếp theo. Cơ sở tri thức không có luật vòng tròn (`validate()` đã kiểm tra), nên luôn tìm được thứ tự này.

### Ví dụ (cơ sở tri thức thật)

Triệu chứng: `starter_clicks_or_silent`, `horn_weak`, `battery_older_than_2_years`, `bike_unused_over_2_weeks`.

| Luật | Tính | CF |
|---|---|---|
| SF01 → `low_electrical_power` | 0.9 × min(1, 1) | 0.90 |
| SF02 → `weak_battery` | 0.85 × min(0.9, 1) | 0.765 |
| SF03 → `weak_battery` | 0.75 × min(0.9, 1) | 0.675 |
| Gộp SF02, SF03 | 0.765 + 0.675 × (1 − 0.765) | **0.92** |

## 4. Cách dùng

Dòng lệnh (ở thư mục gốc repo):

```bash
python src/forward_chaining.py --list-symptoms
python src/forward_chaining.py starter_clicks_or_silent horn_weak battery_older_than_2_years
python src/forward_chaining.py --lang en is_scooter revs_rise_but_slow cvt_belt_overdue
```

Trong code (cho CLI/GUI của Lâm và phần đánh giá):

```python
from kb import load_kb
from forward_chaining import forward_chain

kb = load_kb()
result = forward_chain(kb, {"starter_clicks_or_silent": True, "horn_weak": True,
                            "battery_older_than_2_years": True, "is_scooter": False})
result.diagnoses        # [Diagnosis(fault, cf, rules, severity), ...] xếp CF giảm dần
result.top(3)           # 3 lỗi đứng đầu (đánh giá top-1 / top-3)
result.fired            # các luật đã chạy, theo thứ tự (đếm bằng result.rules_fired)
result.how("weak_battery")  # chuỗi sự kiện dẫn tới kết luận, điều kiện trước
result.wm               # WorkingMemory sau khi suy luận
```

`facts` có thể là `WorkingMemory`, dict `{triệu chứng: True / False / CF}` hoặc danh sách các triệu chứng đúng. Truyền ký hiệu không phải triệu chứng (hoặc gõ sai tên) sẽ báo `ValueError`.

Một kết luận do nhiều luật suy ra được ghi trong bộ nhớ làm việc với `by` là danh sách id luật, ví dụ `"SF02,SF03"`, và `premises` là hợp các điều kiện của các luật đó.

## 5. Việc tiếp theo

- Kiểm tra bằng thuật toán Wang (31/10 – 06/11): KB + triệu chứng ⊨ lỗi, so với kết quả forward chaining trên các kịch bản test.
- Bổ sung nguồn cho các luật EN/TR còn trống `source` sau khi hỏi thợ.
