# Kịch bản test

Mỗi kịch bản là một tình huống thật của người lái: các triệu chứng trả lời "có" và lỗi mà thợ sửa xe sẽ kết luận. Triệu chứng không ghi trong kịch bản được coi là trả lời "không".

Quy tắc của nhóm: **ai viết luật cho hệ thống nào thì không viết kịch bản cho hệ thống đó**. Kịch bản được soạn theo kinh nghiệm thực tế, không chỉnh theo luật, để đánh giá không bị tự chấm bài mình.

| File | Hệ thống | Luật do | Kịch bản do | Số kịch bản |
|---|---|---|---|---|
| `brakes_tyres_suspension.json` | Phanh; lốp và giảm xóc | Khoa | Giang | 10 (BT01–BT10) |
| `starting_fuel_electrical.json` | Khởi động, nhiên liệu; đánh lửa, điện | Lâm | Giang | 10 (SE01–SE10) |
| `engine_transmission.json` (Lâm viết) | Động cơ; truyền động | Giang | Lâm | 10 |

## Định dạng

```json
{
  "systems": ["brakes", "tyres_suspension"],
  "rules_by": "Khoa",
  "written_by": "Giang",
  "date": "2026-10-23",
  "scenarios": [
    {
      "id": "BT01",
      "description": {"vi": "Mô tả tình huống", "en": "Description"},
      "symptoms": ["is_scooter", "brake_squeal", "brake_pad_thin_visible"],
      "expected": "worn_brake_pads"
    }
  ]
}
```

- `symptoms`: chỉ ghi triệu chứng (mục `symptoms` trong `knowledge_base/`), kể cả loại xe (`is_scooter`, `is_manual`, `is_fuel_injected`, `is_carburetor`).
- `expected`: đúng một lỗi (mục `faults`).
- `id`: duy nhất trong cả thư mục. Tiền tố theo file: `BT`, `SE`, `ET`.

## Dùng trong code

```python
from scenarios import load_scenarios, check_scenarios
scenarios = load_scenarios()            # đọc mọi file .json trong scenarios/
check_scenarios(kb, scenarios)          # [] nếu không có lỗi (ký hiệu sai, id trùng)
```

Chạy thử forward chaining và Wang trên mọi kịch bản:

```bash
python src/wang.py --scenarios
```
