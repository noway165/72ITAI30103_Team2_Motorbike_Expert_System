# Định dạng cơ sở tri thức (knowledge base)

Tài liệu này quy định cách viết luật cho hệ chuyên gia chẩn đoán lỗi xe máy. Mọi người viết luật theo đúng định dạng này để bộ suy luận (forward chaining của Giang, backward chaining của Khoa) đọc được chung một cơ sở tri thức.

## 1. Tổ chức file

Mỗi hệ thống xe là một file JSON trong thư mục `knowledge_base/`. Chương trình tự đọc **tất cả** file `.json` trong thư mục này và gộp lại.

| File | Hệ thống | Phụ trách |
|---|---|---|
| `vehicle.json` | Thông tin loại xe dùng chung (tay ga, xe số, FI, bình xăng con) | Chung |
| `starting_fuel.json` | Khởi động và nhiên liệu | Lâm |
| `ignition_electrical.json` | Đánh lửa và điện | Lâm |
| `engine.json` | Động cơ | Giang |
| `transmission.json` | Truyền động (xích, dây curoa CVT) | Giang |
| `brakes.json` | Phanh | Khoa |
| `tyres_suspension.json` | Lốp và giảm xóc | Khoa |

Mỗi người chỉ sửa file của mình để tránh xung đột khi merge. Muốn dùng lại triệu chứng của file khác thì cứ ghi tên ký hiệu vào luật, **không định nghĩa lại**.

## 2. Ba loại ký hiệu

Mỗi triệu chứng, kết luận trung gian và lỗi là một **ký hiệu mệnh đề** (propositional symbol), đặt tên bằng tiếng Anh, chữ thường, nối bằng dấu gạch dưới, ví dụ `horn_weak`.

| Loại | Mục trong file | Ý nghĩa | Ví dụ |
|---|---|---|---|
| Triệu chứng (symptom) | `symptoms` | Hỏi người lái, trả lời có/không | `horn_weak` |
| Trung gian (intermediate) | `intermediates` | Do luật suy ra, dùng làm điều kiện cho luật khác | `low_electrical_power` |
| Lỗi (fault) | `faults` | Kết luận cuối cùng báo cho người lái | `weak_battery` |

Quy tắc phân tầng: **triệu chứng → trung gian → lỗi**.
- Triệu chứng không bao giờ là kết luận của luật.
- Lỗi không bao giờ là điều kiện của luật khác. Nếu cần nối tiếp, tạo một ký hiệu trung gian.

Mỗi ký hiệu nên là câu **khẳng định** (Horn clause không có phủ định). Thay vì "không có tiếng bơm xăng = false", tạo ký hiệu riêng `no_fuel_pump_hum_key_on`.

## 3. Cấu trúc một file

```json
{
  "subsystem": "starting_fuel",
  "description": "Mô tả ngắn hệ thống và người phụ trách",
  "symptoms": {
    "horn_weak": {
      "question": {"vi": "Còi kêu yếu hơn bình thường?", "en": "Is the horn weaker than usual?"},
      "hint": {"vi": "(không bắt buộc) gợi ý cho người lái", "en": "..."}
    }
  },
  "intermediates": {
    "low_electrical_power": {
      "description": {"vi": "Điện yếu", "en": "Low electrical power"}
    }
  },
  "faults": {
    "weak_battery": {
      "name": {"vi": "Ắc quy yếu hoặc hết điện", "en": "Weak or flat battery"},
      "action": {"vi": "Sạc hoặc thay ắc quy.", "en": "Recharge or replace the battery."},
      "severity": "self"
    }
  },
  "rules": [
    {
      "id": "SF01",
      "if": ["starter_clicks_or_silent", "horn_weak"],
      "then": "low_electrical_power",
      "cf": 0.9,
      "source": "Honda Vision owner's manual, troubleshooting, p. 87",
      "note": "(không bắt buộc) ghi chú cho nhóm"
    }
  ]
}
```

### Trường bắt buộc

| Ở đâu | Trường | Ghi chú |
|---|---|---|
| Triệu chứng | `question` | Câu hỏi có/không, có cả `vi` và `en` |
| Trung gian | `description` | Mô tả ngắn |
| Lỗi | `name`, `action`, `severity` | `severity`: `self` (người lái tự xử lý được) hoặc `mechanic` (cần ra tiệm) |
| Luật | `id`, `if`, `then`, `cf`, `source` | Xem mục 4 |

Giao diện hiển thị tiếng Việt; tiếng Anh dùng khi trích dẫn trong báo cáo. Thiếu một ngôn ngữ chương trình vẫn chạy nhưng sẽ báo cảnh báo.

## 4. Viết luật

- **`id`**: duy nhất trong toàn bộ cơ sở tri thức. Tiền tố theo hệ thống:

  | Tiền tố | Hệ thống |
  |---|---|
  | `SF` | Khởi động và nhiên liệu |
  | `IE` | Đánh lửa và điện |
  | `EN` | Động cơ |
  | `TR` | Truyền động |
  | `BR` | Phanh |
  | `TS` | Lốp và giảm xóc |

- **`if`**: danh sách điều kiện, tất cả phải đúng (phép AND). Muốn diễn đạt "A hoặc B thì C", viết **2 luật** cùng kết luận C.
- **`then`**: đúng một ký hiệu (trung gian hoặc lỗi).
- **`cf`** (certainty factor): mức độ tin cậy của luật, từ 0 đến 1. Gợi ý:

  | CF | Khi nào dùng |
  |---|---|
  | 0.9 – 1.0 | Gần như chắc chắn (hết xăng khi kim xăng ở E) |
  | 0.7 – 0.85 | Nguyên nhân thường gặp nhất của nhóm triệu chứng này |
  | 0.5 – 0.65 | Có thể đúng nhưng còn nguyên nhân khác |

  Cách kết hợp CF khi suy luận (nhân qua chuỗi luật, gộp khi nhiều luật cùng kết luận) do Giang chốt.
- **`source`**: nguồn tài liệu của luật (tên tài liệu, trang hoặc link). Bắt buộc phải có trước khi nộp vì báo cáo cần trích dẫn. Luật chưa có nguồn sẽ bị cảnh báo.

## 5. Kiểm tra sau khi sửa

Ở thư mục gốc repo, chạy:

```bash
python src/kb.py          # kiểm tra lỗi
python src/kb.py --list   # liệt kê các lỗi xe và luật kết luận ra chúng
python -m unittest discover tests
```

Bộ kiểm tra báo **ERROR** (phải sửa trước khi mở Pull Request) khi:
- JSON sai cú pháp, thiếu trường bắt buộc, `cf` ngoài khoảng (0, 1], `severity` sai
- trùng tên ký hiệu hoặc trùng `id` luật
- luật dùng ký hiệu chưa định nghĩa (thường do gõ sai tên)
- luật kết luận ra triệu chứng, hoặc dùng lỗi làm điều kiện
- luật vòng tròn (A suy ra B, B lại suy ra A)
- lỗi hoặc trung gian không có luật nào suy ra, hoặc không thể suy ra từ triệu chứng
- luật không bao giờ chạy được

Và **WARNING** (nên sửa) khi: triệu chứng hoặc trung gian không được luật nào dùng, thiếu bản dịch, hai luật trùng nhau, luật chưa có nguồn.

## 6. Dùng trong code

```python
from kb import load_kb, validate, WorkingMemory

kb = load_kb()                          # đọc knowledge_base/
kb.rules_concluding("weak_battery")     # luật kết luận ra một ký hiệu (backward chaining)
kb.rules_using("horn_weak")             # luật có ký hiệu làm điều kiện (forward chaining)
kb.is_askable("horn_weak")              # True nếu là triệu chứng, được hỏi người lái
kb.question("horn_weak", "vi")          # câu hỏi
kb.action("weak_battery", "vi")         # hướng xử lý

wm = WorkingMemory()
wm.tell("horn_weak", True)                               # câu trả lời của người lái
wm.tell("low_electrical_power", cf=0.9, by="SF01",
        premises=["starter_clicks_or_silent", "horn_weak"])  # sự kiện do luật suy ra
wm.ask("horn_weak")                    # True / False / None (chưa biết)
wm.explain("weak_battery")             # chuỗi sự kiện dẫn tới kết luận (cho câu hỏi "how")
```
