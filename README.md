# Motorbike Fault Diagnosis Expert System

Final Project - Nhập môn Trí tuệ Nhân tạo (261_72ITSE30303_01)
Giảng viên: Dr. Huy T. Nguyen

Hệ chuyên gia dựa trên luật, chẩn đoán các lỗi thường gặp của xe máy từ triệu chứng người lái mô tả, dùng **forward chaining** và **backward chaining**, và giải thích được vì sao đưa ra mỗi kết luận (why / how).

## Thành viên và phân công

| Thành viên | Phần chính | Phần phụ | Hệ thống xe |
|---|---|---|---|
| Tăng Thoại Lâm (Leader) | Định dạng cơ sở tri thức, bộ đọc và kiểm tra luật | CLI, GUI, file .exe, tích hợp | Khởi động và nhiên liệu; đánh lửa và điện |
| Kiều Bảo Giang | Forward chaining, xếp hạng bằng certainty factor | Kiểm tra bằng thuật toán Wang | Động cơ; truyền động |
| Nguyễn Nam Khoa | Backward chaining, giải thích why/how | Script đánh giá và biểu đồ | Phanh; lốp và giảm xóc |

## Cấu trúc thư mục (dự kiến)

```
72ITAI30103_Team2_Motorbike_Expert_System/
├── knowledge_base/     # Luật, triệu chứng, lỗi (file JSON)
├── src/                # Mã nguồn: bộ đọc luật, forward/backward chaining, giải thích, giao diện
├── scenarios/          # Kịch bản test (triệu chứng + lỗi mong đợi)
├── tests/              # Unit test
├── results/            # Kết quả đánh giá, biểu đồ
├── docs/               # Định dạng luật (kb_format.md), nguồn tài liệu (sources.md)
└── README.md
```

## Quy trình Git

- Không push thẳng vào `main`; mọi thay đổi qua Pull Request, Lâm review rồi merge.
- Nhánh: `feature/kb-interface` (Lâm), `feature/forward-chaining` (Giang), `feature/backward-chaining` (Khoa).
- Commit message ngắn gọn, nói rõ việc đã làm, ví dụ: `add brake rules`, `fix backward chaining loop`.

## Cài đặt

Yêu cầu Python 3.10+.

```bash
git clone https://github.com/noway165/72ITAI30103_Team2_Motorbike_Expert_System.git
cd 72ITAI30103_Team2_Motorbike_Expert_System
```

Kiểm tra cơ sở tri thức và chạy unit test (ở thư mục gốc repo):

```bash
python src/kb.py          # báo lỗi và cảnh báo trong các file luật
python src/kb.py --list   # liệt kê các lỗi xe và luật suy ra chúng
python -m unittest discover tests
```

Chẩn đoán thử bằng forward chaining (truyền các triệu chứng đúng):

```bash
python src/forward_chaining.py --list-symptoms
python src/forward_chaining.py starter_clicks_or_silent horn_weak battery_older_than_2_years
```

Kiểm tra bằng thuật toán Wang, so với forward chaining trên các kịch bản test trong `scenarios/` ([docs/wang.md](docs/wang.md)):

```bash
python src/wang.py --scenarios --random 500
```

Đánh giá cả hai bộ suy luận trên 30 kịch bản (top-1, top-3, số câu hỏi của backward chaining) và vẽ biểu đồ cho báo cáo vào `docs/report/figures/` (cần `pip install matplotlib` khi dùng `--charts`):

```bash
python src/evaluate.py                       # bảng từng kịch bản và tổng kết
python src/evaluate.py --charts --markdown   # thêm 3 hình và docs/report/evaluation_results.md
```

Cách viết luật: xem [docs/kb_format.md](docs/kb_format.md); forward chaining và cách tính CF: [docs/forward_chaining.md](docs/forward_chaining.md).

### Chạy chương trình

Giao diện cửa sổ (Tkinter, có sẵn trong Python), có chế độ sáng và tối. Màn mở đầu là **Trợ lý chẩn đoán** (Lâm): kể tình trạng xe bằng tiếng Việt hoặc tiếng Anh, trợ lý tách triệu chứng (`src/nlu.py`), chỉ hỏi những câu có information gain cao nhất (`src/interview.py`), rồi kết luận bằng luật và kiểm chứng bằng Wang. Đánh giá: `python src/evaluate_assistant.py`. Khung và màn Cơ sở tri thức: Lâm; màn Theo triệu chứng: Giang (`src/gui_forward.py`); màn Hỏi đáp từng câu: Khoa (`src/gui_backward.py`). Cách cắm màn hình: [docs/ui_guide.md](docs/ui_guide.md) mục 9. Thêm `--lang=en` để chạy tiếng Anh.

```bash
python src/gui.py
```

Dòng lệnh:

```bash
python src/cli.py forward                      # chọn triệu chứng từ danh sách có đánh số
python src/cli.py forward horn_weak starter_clicks_or_silent battery_older_than_2_years
python src/cli.py backward --subsystem brakes  # trả lời c / k, gõ why để hỏi tại sao
python src/cli.py list symptoms
```

Tạo file chạy Windows `dist\MotorbikeExpert.exe` (chạy test trước, PyInstaller cài vào `.venv-build`, không đụng Python chính):

```bash
build_exe.bat
```

Nếu đường dẫn repo quá dài và lỗi khi tạo venv, đặt venv ở chỗ khác: `set BUILD_VENV=C:\Temp\mb-venv` rồi chạy lại. Giao diện và màu sắc chung: [docs/ui_guide.md](docs/ui_guide.md).

## Mốc thời gian

| Mốc | Ngày |
|---|---|
| Cơ sở tri thức v1 và forward chaining | 16/10/2026 |
| Thuyết trình Logical Agents | 22/10/2026 |
| Final ready | 12/11/2026 |
| Thuyết trình Oral | 19/11/2026 |
| Nộp báo cáo (ETC) | 22/11/2026 |

## Sản phẩm bàn giao

1. Báo cáo 10 trang
2. Mã nguồn kèm unit test
3. File thực thi chạy trên Windows
