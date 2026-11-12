# Motorbike Fault Diagnosis Expert System (MotoLogic)

Final Project, Nhập môn Trí tuệ Nhân tạo (261_72ITSE30303_01), Nhóm 2.
Giảng viên: Dr. Huy T. Nguyen.

Hệ chuyên gia dựa trên luật, chẩn đoán các lỗi thường gặp của xe máy từ triệu chứng người lái nhận thấy. Chương trình có:

- **forward chaining**: từ các triệu chứng đã biết suy ra lỗi, xếp hạng bằng certainty factor (CF);
- **backward chaining**: chọn một lỗi làm giả thuyết rồi hỏi từng câu cần thiết;
- **giải thích why / how**: vì sao hỏi câu này, kết luận được suy ra qua những luật nào;
- **thuật toán Wang**: kiểm tra lại kết luận bằng một cách chứng minh độc lập, không dùng CF;
- **trợ lý chẩn đoán**: đọc câu người lái kể bằng tiếng Việt hoặc tiếng Anh, rồi chỉ hỏi câu có information gain cao nhất.

Chương trình chạy offline. Giao diện có hai ngôn ngữ (tiếng Việt / tiếng Anh) và hai chế độ (sáng / tối). Có bản `.exe` cho Windows, không cần cài Python.

## Mục lục

1. [Thành viên và phân công](#1-thành-viên-và-phân-công)
2. [Kết quả chính](#2-kết-quả-chính)
3. [Cài đặt](#3-cài-đặt)
4. [Chạy chương trình](#4-chạy-chương-trình)
5. [Hướng dẫn dùng giao diện MotoLogic](#5-hướng-dẫn-dùng-giao-diện-motologic)
6. [Cách hệ thống hoạt động](#6-cách-hệ-thống-hoạt-động)
7. [Kiểm thử và đánh giá](#7-kiểm-thử-và-đánh-giá)
8. [Cấu trúc thư mục](#8-cấu-trúc-thư-mục)
9. [Tạo file .exe](#9-tạo-file-exe)
10. [Quy trình làm việc nhóm](#10-quy-trình-làm-việc-nhóm)
11. [Mốc thời gian và sản phẩm bàn giao](#11-mốc-thời-gian-và-sản-phẩm-bàn-giao)
12. [Hạn chế](#12-hạn-chế)
13. [Tài liệu liên quan](#13-tài-liệu-liên-quan)

## 1. Thành viên và phân công

| Thành viên | Phần chính | Phần phụ | Luật của hệ thống xe |
|---|---|---|---|
| Tăng Thoại Lâm (nhóm trưởng) | Định dạng cơ sở tri thức, bộ đọc và kiểm tra luật (`kb.py`) | CLI, khung giao diện, trợ lý chẩn đoán, file `.exe`, tích hợp | Khởi động và nhiên liệu; đánh lửa và điện |
| Kiều Bảo Giang | Forward chaining, xếp hạng bằng CF | Thuật toán Wang; giao diện MotoLogic | Động cơ; truyền động |
| Nguyễn Nam Khoa | Backward chaining, giải thích why / how | Script đánh giá và biểu đồ | Phanh; lốp và giảm xóc |

Người viết luật của một hệ thống xe không viết kịch bản kiểm thử cho hệ thống đó (xem `written_by` và `rules_by` trong `scenarios/*.json`).

Màn hình trong giao diện:

| Màn | File | Người làm |
|---|---|---|
| Khung cửa sổ, Cơ sở tri thức, Giới thiệu | `src/gui.py`, `src/gui_widgets.py`, `src/theme.py` | Lâm |
| MotoLogic: Chẩn đoán, Lịch sử phiên | `src/gui_diagnosis.py`, `src/gui_history.py` | Giang |
| Trợ lý chẩn đoán (màn cũ) | `src/gui_assistant.py` | Lâm |
| Theo triệu chứng (màn cũ) | `src/gui_forward.py` | Giang |
| Hỏi đáp từng câu (màn cũ) | `src/gui_backward.py` | Khoa |

## 2. Kết quả chính

Cơ sở tri thức: 73 triệu chứng (gồm 4 câu về loại xe), 9 kết luận trung gian, 40 lỗi, 79 luật. Lệnh `python src/kb.py` báo 0 lỗi, 0 cảnh báo. Mọi luật đều ghi nguồn tham khảo.

| Phép đo | Kết quả |
|---|---|
| Forward chaining, lỗi mong đợi xếp thứ nhất (30 kịch bản) | 30/30 |
| Forward chaining khi bỏ 4 luật dự phòng (BR13, EN18, SF14, TS15) | 28/30 |
| Wang so với forward chaining (30 kịch bản + 500 bộ triệu chứng ngẫu nhiên) | khớp 100% |
| Backward chaining hỏi mọi lỗi | trung bình 39,7 câu, đúng 30/30 |
| Backward chaining khi chọn đúng bộ phận trước | trung bình 9,0 câu |
| Trợ lý, mô tả của 30 kịch bản (tiếng Việt / tiếng Anh) | 5,3 câu, 30/30 / 5,3 câu, 30/30 |
| Trợ lý, 10 mô tả giữ riêng để kiểm tra (tiếng Việt / tiếng Anh) | 10,5 câu, 8/10 / 11,4 câu, 7/10 |

Các mô tả của 30 kịch bản đều đã được dùng khi viết bộ đọc câu (`src/nlu.py`), nên con số 30/30 của trợ lý là lạc quan. Tập 10 mô tả giữ riêng (`tests/data/heldout_descriptions.json`) được viết trước khi đọc `nlu.py` và không bao giờ dùng để sửa nó. Đây mới là ước lượng công bằng. Số liệu đầy đủ: [docs/report/evaluation_results.md](docs/report/evaluation_results.md) và [docs/report/assistant_results.md](docs/report/assistant_results.md).

## 3. Cài đặt

Yêu cầu:

- Python 3.10 trở lên (đã thử với 3.12). Tkinter có sẵn trong bản Python cài từ python.org.
- Không cần thư viện ngoài để chạy chương trình và test.
- Chỉ khi vẽ biểu đồ cho báo cáo mới cần `matplotlib`. `tools/shots.py` cần `Pillow`.

```bash
git clone https://github.com/noway165/72ITAI30103_Team2_Motorbike_Expert_System.git
cd 72ITAI30103_Team2_Motorbike_Expert_System
python -m unittest discover tests
```

Thư viện tuỳ chọn:

```bash
pip install matplotlib pillow
```

Mọi lệnh trong README chạy ở thư mục gốc của repo.

## 4. Chạy chương trình

### Giao diện cửa sổ

```bash
python src/gui.py
```

```bash
python src/gui.py --lang=en
```

Cửa sổ mở ở màn **Chẩn đoán**. Ngôn ngữ và chế độ sáng / tối đổi ở góc dưới thanh bên trái. Khi đổi, các câu trả lời đang dở vẫn được giữ.

### File .exe

Chạy `MotorbikeExpert.exe` (tạo bằng `build_exe.bat`, xem [mục 9](#9-tạo-file-exe)). File chứa sẵn cơ sở tri thức và kịch bản, không cần Python.

### Dòng lệnh

```bash
python src/cli.py list symptoms
```

```bash
python src/cli.py forward horn_weak starter_clicks_or_silent battery_older_than_2_years
```

```bash
python src/cli.py forward
```

```bash
python src/cli.py backward --subsystem brakes
```

- `forward` không kèm triệu chứng: chọn từ danh sách có đánh số.
- `backward`: trả lời `c` (có) hoặc `k` (không). Gõ `why` để hỏi vì sao chương trình hỏi câu đó.
- Tuỳ chọn chung: `--lang vi|en`, `--threshold 0.2` (ngưỡng CF để báo một lỗi).
- `python src/cli.py list faults`: liệt kê các lỗi.

Có thể gọi trực tiếp từng bộ suy luận:

```bash
python src/forward_chaining.py --list-symptoms
```

```bash
python src/forward_chaining.py starter_clicks_or_silent horn_weak battery_older_than_2_years
```

```bash
python src/kb.py --list
```

## 5. Hướng dẫn dùng giao diện MotoLogic

Thanh bên trái:

| Phím tắt | Màn |
|---|---|
| Ctrl+1 | Chẩn đoán (MotoLogic) |
| Ctrl+2 | Lịch sử phiên |
| Ctrl+3 | Cơ sở tri thức |
| Ctrl+4 đến Ctrl+7 | Màn cũ: Trợ lý chẩn đoán, Theo triệu chứng, Hỏi đáp từng câu, Giới thiệu |

### Bước 1: Khai báo xe

- Chọn **xe tay ga** hoặc **xe số**.
- Chọn kiểu cấp nhiên liệu: **phun xăng (FI)**, **bình xăng con** hoặc **không rõ**. Một số luật chỉ đúng với một loại xe, nên trả lời ở đây giúp bỏ bớt câu hỏi.
- Chọn một trong ba cách chẩn đoán, rồi bấm **Bắt đầu chẩn đoán**.

### Bước 2: Ba cách chẩn đoán

**a. Hỏi đáp từng câu (backward chaining, cách được gợi ý)**

1. Thẻ đầu tiên hỏi **"Sự cố nằm ở đâu?"**. Có 6 bộ phận và lựa chọn "Chưa rõ, hỏi tất cả".
2. Chọn đúng bộ phận thì trung bình chỉ cần 9 câu. Hỏi tất cả cần khoảng 40 câu.
3. Mỗi câu trả lời **Có**, **Không** hoặc **Không chắc, bỏ qua câu này**. Phím tắt: `c` / `y` = có, `k` / `n` = không, `b` / `u` = không chắc.
4. Khối bên phải cho biết **vì sao hỏi câu này**: luật nào đang được thử, kết luận của nó dùng cho luật nào tiếp theo, và còn bao nhiêu giả thuyết.
5. Khung **Đã trả lời** dưới câu hỏi liệt kê các câu trả lời gần nhất. Bấm **Câu trước** để sửa.
6. Thanh **Bộ phận** phía trên dùng để đổi bộ phận bất cứ lúc nào.

**b. Tôi biết triệu chứng (forward chaining)**

1. Tìm triệu chứng bằng ô tìm kiếm. Có thể gõ không dấu, ví dụ "coi" tìm ra "còi".
2. Có thể lọc theo bộ phận.
3. Tick mọi triệu chứng bạn chắc chắn. Triệu chứng không tick được coi là chưa biết, không phải "không".
4. Bấm **Tìm lỗi phù hợp**.

**c. Kể bằng lời (trò chuyện với MotoLogic)**

1. Gõ tình trạng xe như khi kể với thợ, tiếng Việt có hoặc không dấu, hoặc tiếng Anh, rồi bấm **Phân tích**. Có thể bấm một câu ví dụ để điền sẵn.
2. Màn chuyển thành khung chat. Bot nhắc lại những triệu chứng đã đọc được, rồi hỏi câu có information gain cao nhất. Câu hỏi lấy từ cơ sở tri thức, kèm các lỗi mà câu đó giúp phân biệt.
3. Mỗi lượt có thể gõ (hoặc bấm nút nhanh):
   - **trả lời**: "có", "ừ", "chắc vậy", "không", "ko", "không rõ"… Bot báo luật nào vừa chạy được, hoặc luật nào không dùng được nữa;
   - **kể thêm**: "à còi cũng yếu". Câu trả lời và phần kể thêm có thể chung một câu: "có, mà đèn pha cũng không sáng";
   - **hỏi lại**:
     - "tại sao hỏi vậy?": các luật dùng câu đó, mỗi điều kiện đánh dấu ✓ đã có, ✗ không, ? đang hỏi, · chưa biết;
     - "làm sao biết?": chuỗi luật tới lỗi dẫn đầu;
     - "sửa thế nào?": cách xử lý và luật đã chứng minh;
     - "còn khả năng nào?": 3 lỗi có khả năng nhất, và lỗi nào đã được luật chứng minh;
     - "đứt cầu chì tổng là gì?": lỗi đó, các luật kết luận ra nó và các luật dùng nó;
   - **lệnh**: "xem kết quả" sang bước 3; "làm lại" bắt đầu lại.
4. Khi không còn câu đáng hỏi, bot nêu kết luận, độ tin cậy, chuỗi luật, kết quả kiểm tra chéo bằng thuật toán Wang và cách xử lý. Bấm **Xem kết quả đầy đủ** để sang bước 3.
5. Nếu câu đầu không nhận ra triệu chứng nào, ô nhập vẫn giữ nguyên và có nút **Chuyển sang hỏi đáp từng câu**.

Mọi nội dung bot trả lời đều sinh từ luật (`src/chat.py`). Chỉ các chữ nối như "NẾU / VÀ / THÌ", "Ghi nhận" là cố định. Kết luận luôn do forward chaining đưa ra; chat không tự thêm lỗi nào ngoài luật.

### Bước 3: Kết quả

- **Lỗi có khả năng cao**, kèm đồng hồ **Độ tin cậy** (ví dụ 89%, CF 0.89 ghi nhỏ bên dưới), số quan sát và số luật đã dùng.
- **Chương trình suy ra thế nào?**: chuỗi luật từ câu trả lời của bạn, qua kết luận trung gian, tới lỗi. Mỗi bước có mã luật và CF.
- **Bước tiếp theo**: việc nên làm, và lỗi này tự xử lý được hay cần đưa thợ.
- **Kiểm tra chéo kết luận**: chứng minh lại bằng thuật toán Wang từ luật và các câu trả lời "có", không dựa vào CF.
- **Cũng có thể là**: hai lỗi xếp sau, kèm phần trăm.
- Khi không lỗi nào đạt ngưỡng 20%, màn này cho biết chương trình đã suy ra được gì và nên kiểm tra thêm điểm nào.

Mỗi lần chẩn đoán được lưu vào **Lịch sử phiên** (chỉ trong lúc chương trình đang mở). Từ đó có thể mở lại kết quả cũ.

### Màn Cơ sở tri thức

Xem mọi luật theo bộ phận: điều kiện, kết luận, CF và nguồn tham khảo.

## 6. Cách hệ thống hoạt động

### Cơ sở tri thức (`knowledge_base/*.json`)

Mỗi bộ phận có một file. Mỗi file gồm:

- `symptoms`: câu hỏi (vi / en), có thể kèm gợi ý cách kiểm tra;
- `intermediates`: kết luận trung gian, ví dụ `low_electrical_power`;
- `faults`: lỗi, mức độ (tự xử lý / cần thợ) và việc nên làm;
- `rules`: `IF điều kiện 1 AND điều kiện 2 THEN kết luận`, kèm `cf` và `source`.

| File | Triệu chứng | Trung gian | Lỗi | Luật |
|---|---|---|---|---|
| `starting_fuel.json` | 17 | 3 | 8 | 14 |
| `ignition_electrical.json` | 6 | 1 | 4 | 7 |
| `engine.json` | 14 | 2 | 8 | 18 |
| `transmission.json` | 10 | 1 | 7 | 12 |
| `brakes.json` | 10 | 1 | 6 | 13 |
| `tyres_suspension.json` | 12 | 1 | 7 | 15 |
| `vehicle.json` (loại xe) | 4 | – | – | – |

Cách viết luật: [docs/kb_format.md](docs/kb_format.md). Nguồn tham khảo: [docs/sources.md](docs/sources.md). `python src/kb.py` kiểm tra id trùng, triệu chứng không dùng, luật thiếu nguồn, vòng lặp…

### Forward chaining và CF (`src/forward_chaining.py`)

- Các điều kiện của một luật nối bằng AND: CF(điều kiện) = min(CF của từng điều kiện).
- CF mà luật đóng góp = CF của luật × CF(điều kiện).
- Nhiều luật cùng kết luận: CF = CF1 + CF2 × (1 − CF1).
- Lỗi được báo khi CF ≥ 0.2, xếp từ cao xuống thấp.

Chi tiết: [docs/forward_chaining.md](docs/forward_chaining.md).

### Backward chaining (`src/backward_chaining.py`)

Lần lượt lấy từng lỗi làm mục tiêu. Hệ thống tìm luật kết luận ra lỗi đó, rồi hỏi các điều kiện chưa biết. Kết luận trung gian được chứng minh đệ quy. Câu nào đã trả lời thì không hỏi lại. Lệnh `why` cho biết luật nào cần câu trả lời đó; `how` cho biết kết luận được suy ra qua những luật nào.

### Thuật toán Wang (`src/wang.py`)

Viết luật và các câu trả lời "có" thành sequent, rồi chứng minh `luật, câu trả lời ⊢ lỗi` bằng các bước của Wang. Không dùng CF, nên đây là phép kiểm tra độc lập với forward chaining. Chi tiết: [docs/wang.md](docs/wang.md).

### Trợ lý chẩn đoán (`src/nlu.py`, `src/interview.py`)

**Đọc câu kể (`nlu.py`)**
- Mỗi triệu chứng có danh sách cụm từ tiếng Việt (gồm từ miền Nam như "thắng", "bố thắng") và tiếng Anh.
- Câu và cụm từ được so khớp sau khi bỏ dấu, theo từng từ. Giữa các từ của một cụm cho phép chen tối đa 2 từ.
- Chữ phủ định ("không", "chưa", "not"…) đứng trước cụm, hoặc chen giữa cụm, đổi câu trả lời thành "không".
- Không cần internet hay mô hình học máy, nên chạy được trong file `.exe`.

**Chọn câu hỏi (`interview.py`)**
- Mỗi lỗi được trải qua các luật thành những tập triệu chứng chứng minh được nó, mỗi tập có trọng số bằng CF của chuỗi luật.
- Giả định người lái bỏ sót một triệu chứng đúng với xác suất 0,05 và báo nhầm với xác suất 0,1.
- Mỗi bước hỏi triệu chứng có information gain lớn nhất.
- Dừng khi một lỗi đạt 85% xác suất (70% nếu forward chaining đã chứng minh được), khi không câu nào còn đáng hỏi, hoặc sau 15 câu.
- Kết quả cuối cùng vẫn lấy từ forward chaining và Wang, nên CF và giải thích giống các màn khác.

## 7. Kiểm thử và đánh giá

| Lệnh | Việc |
|---|---|
| `python -m unittest discover tests` | toàn bộ unit test. Test giao diện tự bỏ qua nếu máy không có màn hình. |
| `python src/kb.py` | kiểm tra cơ sở tri thức (phải là 0 lỗi, 0 cảnh báo) |
| `python src/wang.py --scenarios --random 500` | so Wang với forward chaining |
| `python src/evaluate.py` | top-1, top-3, số câu hỏi của backward chaining trên 30 kịch bản |
| `python src/evaluate.py --charts --markdown` | thêm 3 biểu đồ vào `docs/report/figures/` và ghi `docs/report/evaluation_results.md` (cần matplotlib) |
| `python src/evaluate_assistant.py` | đánh giá trợ lý: độ đọc đúng (precision / recall / F1) và số câu hỏi; thêm `--write` để ghi `docs/report/assistant_results.md` |
| `python tools/shots.py` | chụp mọi màn chẩn đoán (vi / en × sáng / tối × cửa sổ mặc định / nhỏ nhất) vào một thư mục tạm, để soát giao diện bằng mắt (cần Pillow; cửa sổ phải hiện trên màn hình) |

Dữ liệu kiểm thử:

- `scenarios/*.json`: 30 kịch bản. Mỗi kịch bản có triệu chứng đúng, lỗi mong đợi và một câu mô tả bằng tiếng Việt và tiếng Anh. Có 3 nhóm: SE (khởi động, nhiên liệu, điện), ET (động cơ, truyền động), BT (phanh, lốp, giảm xóc).
- `tests/data/heldout_descriptions.json`: 10 mô tả (HO01–HO10) chỉ dùng để kiểm tra bộ đọc câu. Đặt ngoài `scenarios/` để số kịch bản cố định không đổi.

Cách đọc số đo của bộ đọc câu:

| Tập | Vai trò |
|---|---|
| SE + ET | dùng khi viết `nlu.py` |
| BT | dùng để phân tích lỗi ngày 12/11, nên không còn là tập kiểm tra |
| HO | tập kiểm tra hiện tại; không được thêm cụm từ theo tập này |

## 8. Cấu trúc thư mục

```
├── knowledge_base/        # luật, triệu chứng, lỗi theo bộ phận (JSON)
├── scenarios/             # 30 kịch bản kiểm thử (JSON) + README
├── src/
│   ├── kb.py              # đọc và kiểm tra cơ sở tri thức
│   ├── forward_chaining.py
│   ├── backward_chaining.py
│   ├── wang.py            # thuật toán Wang
│   ├── nlu.py             # đọc câu người lái kể
│   ├── interview.py       # chọn câu hỏi theo information gain
│   ├── chat.py            # hội thoại Kể bằng lời: hiểu ý câu gõ, trả lời từ luật
│   ├── present.py         # dựng giải thích why / how cho CLI và giao diện
│   ├── scenarios.py       # đọc kịch bản
│   ├── evaluate.py        # đánh giá forward / backward, biểu đồ
│   ├── evaluate_assistant.py
│   ├── report_figures.py  # hình minh hoạ cho báo cáo
│   ├── cli.py             # giao diện dòng lệnh
│   ├── gui.py             # cửa sổ chính, thanh bên, màn Cơ sở tri thức, Giới thiệu
│   ├── gui_diagnosis.py   # MotoLogic: 3 bước chẩn đoán
│   ├── gui_history.py     # Lịch sử phiên
│   ├── gui_assistant.py, gui_forward.py, gui_backward.py   # các màn cũ
│   ├── gui_widgets.py     # widget dùng chung (thẻ bo góc, nút, đồng hồ CF, icon)
│   └── theme.py           # màu sáng / tối, font
├── tests/                 # unit test; tests/data/ chứa tập mô tả giữ riêng
├── tools/shots.py         # chụp màn hình để soát giao diện
├── docs/
│   ├── kb_format.md, forward_chaining.md, wang.md, sources.md, scenario_analysis.md, ui_guide.md
│   ├── design/            # thiết kế MotoLogic (ảnh mẫu + motologic_spec.md)
│   ├── report/            # bản nháp các chương báo cáo, số liệu, hình (figures/), mẫu của giảng viên (sample/)
│   ├── slides/            # slide và kịch bản thuyết trình
│   └── progress/          # ghi chép tiến độ từng thành viên
├── build_exe.bat          # tạo dist\MotorbikeExpert.exe
└── README.md
```

## 9. Tạo file .exe

```bash
build_exe.bat
```

Script này:
1. tạo môi trường ảo `.venv-build` và cài PyInstaller vào đó, không đụng Python chính;
2. chạy toàn bộ unit test, dừng nếu có test lỗi;
3. đóng gói `src/gui.py` cùng `knowledge_base/` và `scenarios/` thành `dist\MotorbikeExpert.exe`.

Nếu đường dẫn repo quá dài (Windows giới hạn 260 ký tự) và lỗi khi tạo venv, đặt venv ở chỗ khác rồi chạy lại:

```bash
set BUILD_VENV=%LOCALAPPDATA%\Temp\mb-venv && build_exe.bat
```

Trước buổi demo, chạy thử file `.exe` trên một máy Windows khác, đi hết ba cách chẩn đoán.

## 10. Quy trình làm việc nhóm

- Không push thẳng vào `main`. Mọi thay đổi đi qua Pull Request; Lâm review rồi merge.
- Mỗi người làm trên nhánh riêng, đặt tên theo việc, ví dụ `feature/motologic`, `feature/khoa-final`.
- Trước khi mở PR, chạy `python -m unittest discover tests` và `python src/kb.py`.
- Sửa giao diện thì chạy thêm `python tools/shots.py` và xem ảnh.
- Muốn sửa file của người khác thì báo trước qua nhóm Zalo.
- Commit message ngắn, nói rõ đã làm gì, ví dụ `add brake rules`, `fix backward chaining loop`.
- Cách cắm thêm một màn hình vào giao diện: [docs/ui_guide.md](docs/ui_guide.md) mục 9.

## 11. Mốc thời gian và sản phẩm bàn giao

| Mốc | Ngày |
|---|---|
| Cơ sở tri thức v1 và forward chaining | 16/10/2026 |
| Thuyết trình Logical Agents | 22/10/2026 |
| Mã nguồn, slide và các phần báo cáo gửi Lâm | tối 14/11/2026 |
| Ghép báo cáo Word, tập demo | 15/11/2026 |
| Vấn đáp, demo trực tiếp và trình bày báo cáo | 16/11/2026 |
| Sửa báo cáo theo góp ý của giảng viên | 17–21/11/2026 |
| Nộp báo cáo cuối | 22/11/2026 |

Sản phẩm bàn giao:

1. Báo cáo 10 trang (tiếng Anh, theo mẫu trong `docs/report/sample/`).
2. Mã nguồn kèm unit test.
3. File thực thi chạy trên Windows.

## 12. Hạn chế

- Luật là mệnh đề Horn: câu trả lời "không" không làm giảm CF của một lỗi. Ví dụ ở ET05, lỗi "thiếu nước làm mát" vẫn xếp thứ hai dù người lái nói mức nước đủ.
- CF là ước lượng của nhóm, không đo từ dữ liệu sửa chữa thật.
- Luật được viết trước, nguồn tìm sau. Các nguồn yếu được ghi trong `docs/sources.md`.
- Kịch bản do nhóm tự viết, không lấy từ ca sửa xe thật.
- Bộ đọc câu chỉ hiểu những cách nói có trong danh sách cụm từ. Trên tập giữ riêng, recall chỉ khoảng 0,33–0,39.
- Một số dòng xe như Wave có cả bản bình xăng con và phun xăng, nên loại nhiên liệu cần chọn ở bước 1, không đoán từ tên xe.
- Kết quả chỉ mang tính minh hoạ, không thay cho việc kiểm tra của thợ.

## 13. Tài liệu liên quan

- [docs/kb_format.md](docs/kb_format.md): định dạng luật
- [docs/forward_chaining.md](docs/forward_chaining.md): forward chaining và CF
- [docs/wang.md](docs/wang.md): thuật toán Wang
- [docs/sources.md](docs/sources.md): nguồn của từng luật
- [docs/scenario_analysis.md](docs/scenario_analysis.md): phân tích kịch bản
- [docs/ui_guide.md](docs/ui_guide.md): màu sắc, widget, cách thêm màn hình
- [docs/design/motologic_spec.md](docs/design/motologic_spec.md): đặc tả giao diện MotoLogic
- [docs/report/README.md](docs/report/README.md): cấu trúc và số trang của báo cáo
