# Kiểm tra bằng thuật toán Wang

Phụ trách: Giang. Mã nguồn: [`src/wang.py`](../src/wang.py), test: [`tests/test_wang.py`](../tests/test_wang.py).

## 1. Mục đích

Forward chaining và backward chaining là bộ suy luận "tự viết", có thể có lỗi (bỏ sót luật, chạy luật khi thiếu điều kiện). Thuật toán Wang là một bộ chứng minh định lý độc lập cho logic mệnh đề. Ta dùng nó để kiểm tra:

> Với mọi bộ câu trả lời, tập lỗi mà forward chaining suy ra **bằng đúng** tập lỗi mà Wang chứng minh được từ KB + câu trả lời (KB ∧ câu trả lời ⊨ lỗi).

Wang bỏ qua certainty factor: nó chỉ trả lời "có suy ra được về mặt logic hay không". Vì vậy khi so sánh, forward chaining chạy với ngưỡng 0 (lấy mọi lỗi suy ra được, kể cả CF thấp).

## 2. Thuật toán

Sequent `A1, ..., An ⇒ B1, ..., Bm` nghĩa là: nếu mọi A bên trái đúng thì ít nhất một B bên phải đúng. Mỗi bước bỏ một phép nối của một công thức:

| Phép nối | Bên trái | Bên phải |
|---|---|---|
| ¬A | chuyển A sang phải | chuyển A sang trái |
| A ∧ B | giữ A và B bên trái | **tách 2 nhánh**: A bên phải, B bên phải |
| A ∨ B | **tách 2 nhánh**: A bên trái, B bên trái | giữ A và B bên phải |
| A → B | **tách 2 nhánh**: A bên phải; B bên trái | A sang trái, B ở lại bên phải |

- Có cùng một nguyên tử ở hai bên: **tiên đề**, nhánh đúng.
- Chỉ còn nguyên tử và không có nguyên tử chung: nhánh **sai**, sequent không hợp lệ.
- Sequent hợp lệ khi mọi nhánh kết thúc bằng tiên đề.

Áp dụng cho hệ chuyên gia: luật `NẾU p1 VÀ p2 THÌ q` thành công thức `(p1 ∧ p2) → q`; triệu chứng trả lời "có" là nguyên tử bên trái, trả lời "không" là `¬triệu_chứng` bên trái. Kiểm tra một lỗi:

```
luật1, luật2, ..., triệu_chứng1, triệu_chứng2, ...  ⇒  lỗi
```

Hai cách giữ cho chứng minh nhỏ (không làm thay đổi kết quả):

1. Chỉ đưa vào các luật **liên quan** tới lỗi cần chứng minh (luật kết luận ra lỗi, luật kết luận ra điều kiện của chúng, ...). Luật là Horn clause nên các luật khác không giúp chứng minh được.
2. Khi có nhiều luật `→` bên trái, chọn trước luật có mọi điều kiện đã nằm bên trái: nhánh đầu đóng ngay bằng tiên đề, giống thứ tự forward chaining chạy luật.

### Ví dụ (cơ sở tri thức thật)

```bash
python src/wang.py --trace --goal weak_battery starter_clicks_or_silent horn_weak battery_older_than_2_years
```

Rút gọn (R1 = SF01, R2 = SF02, Γ = các luật và triệu chứng còn lại):

```
Γ, R1, R2, starter_clicks_or_silent, horn_weak, battery_older_than_2_years ⇒ weak_battery     [→ trái: R1]
  Γ, R2, ... ⇒ weak_battery, starter_clicks_or_silent ∧ horn_weak                          [∧ phải: 2 nhánh]
    ... ⇒ ..., starter_clicks_or_silent                                                     [tiên đề]
    ... ⇒ ..., horn_weak                                                                    [tiên đề]
  Γ, R2, ..., low_electrical_power ⇒ weak_battery                                           [→ trái: R2]
    ... ⇒ weak_battery, low_electrical_power ∧ battery_older_than_2_years                    [∧ phải: 2 nhánh, đều là tiên đề]
    Γ, ..., low_electrical_power, weak_battery ⇒ weak_battery                               [tiên đề]
weak_battery: proved (9 sequents)
```

## 3. Cách dùng

Ở thư mục gốc repo:

```bash
python src/wang.py horn_weak starter_clicks_or_silent battery_older_than_2_years   # lỗi Wang chứng minh được
python src/wang.py --trace --goal weak_battery horn_weak starter_clicks_or_silent battery_older_than_2_years
python src/wang.py --scenarios              # so với forward chaining trên mọi kịch bản trong scenarios/
python src/wang.py --scenarios --random 500 # thêm 500 bộ triệu chứng ngẫu nhiên
```

Trong code:

```python
from wang import entails, check_engines, prove, Atom, Implies
entails(kb, ["horn_weak", "starter_clicks_or_silent"], "weak_battery").valid   # False
check_engines(kb, "test", symptoms).agree    # True nếu Wang và forward chaining cho cùng tập lỗi
prove([Implies(Atom("p"), Atom("q")), Atom("p")], [Atom("q")]).valid          # True
```

## 4. Kết quả (03/11/2026, KB 73 luật)

| Bộ dữ liệu | Số lần so sánh | Wang khác forward chaining |
|---|---|---|
| 20 kịch bản trong `scenarios/` (BT, SE) | 20 × 40 lỗi | 0 |
| 500 bộ triệu chứng ngẫu nhiên (mỗi triệu chứng đúng với xác suất 0.15, seed 0) | 500 × 40 lỗi, 1147 lỗi được chứng minh | 0 |

Forward chaining suy ra đúng và đủ các lỗi được KB kéo theo về mặt logic. Hai kịch bản chẩn đoán sai (BT10, SE10) cũng được Wang xác nhận là **không** suy ra được: lỗi nằm ở cơ sở tri thức (thiếu luật), không phải ở bộ suy luận. Xem [scenario_analysis.md](scenario_analysis.md).

Unit test (`tests/test_wang.py`): các ví dụ nhỏ (tiên đề, luật bài trung, modus ponens, modus tollens, De Morgan, luật Horn nhiều điều kiện, chuỗi luật), KB nhỏ, KB thật, và so sánh với forward chaining trên kịch bản + 100 bộ ngẫu nhiên.

## Tài liệu

- H. Wang, "Toward Mechanical Mathematics", *IBM Journal of Research and Development*, 4(1), 2–22, 1960.
- S. Russell and P. Norvig, *Artificial Intelligence: A Modern Approach*, 4th ed., 2020, chương 7 (suy diễn, tính đúng đắn và đầy đủ của forward chaining).
