# Motorbike Fault Diagnosis Expert System

Final Project — Nhập môn Trí tuệ Nhân tạo (261_72ITSE30303_01)
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

Cách viết luật: xem [docs/kb_format.md](docs/kb_format.md). Hướng dẫn chạy chương trình chẩn đoán sẽ được bổ sung khi có giao diện CLI.

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
