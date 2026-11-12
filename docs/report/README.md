# Quy định chung cho báo cáo

File mẫu của giảng viên: [sample/Final_Project_report_sample.docx](sample/Final_Project_report_sample.docx). Mỗi người viết phần của mình bằng Markdown trong thư mục này, Lâm gộp vào file Word theo mẫu.

## Thứ tự trong báo cáo

Bìa (Ministry of Education and Training, Van Lang University, tên môn, Final Project, Title, Lecturer, Course code, Group và MSSV, Ho Chi Minh City + tháng năm), Acknowledgments, Commitment, mục lục tự động, các chương, References. Viết bằng tiếng Anh.

| Chương | Người viết |
|---|---|
| Chapter 1: Introduction | Lâm |
| Chapter 2: Background | Lâm |
| Chapter 3: Methodology | Giang (forward, CF, Wang), Khoa (backward, why/how), Lâm (cơ sở tri thức, giao diện) |
| Chapter 4: Experiments and Results | Khoa |
| Chapter 5: Discussion | Giang |
| Chapter 6: Conclusion | Lâm |

## File của từng phần

| File | Phần | Người viết |
|---|---|---|
| `front_matter_lam.md` | Bìa (tên, MSSV), Acknowledgments, Commitment | Lâm |
| `introduction_background_lam.md` | Chapter 1, Chapter 2, References | Lâm |
| `methodology_lam.md` | 3.1 Knowledge base and interface | Lâm |
| `methodology_giang.md` | Forward chaining, CF, Wang; Chapter conclusion của Ch3 | Giang |
| `methodology_khoa.md` | Backward chaining, why/how | Khoa |
| `assistant_lam.md` | Trợ lý và chat (mục cuối của Ch3) | Lâm |
| `experiments_results_khoa.md` | Chapter 4 | Khoa |
| `discussion.md` | Chapter 5 | Giang |
| `conclusion_lam.md` | Chapter 6 | Lâm |

## Ghép thành file Word

```
pip install python-docx
python tools/build_report.py      # -> build/report/Final_Report_Group2.docx
```

Script lấy bìa (khung, logo), khổ giấy, lề, style và footer từ file mẫu; tự đánh số mục và hình; tạo mục lục (Word hỏi cập nhật khi mở file, chọn Yes); đặt mỗi hình ngay sau đoạn đầu tiên nhắc tới nó. Quy ước để script đọc đúng:

- Phần trước dòng `## ` đầu tiên là ghi chú cho nhóm, không đưa vào báo cáo.
- Mục viết `## 3.y Tên mục`. Số tạm (`3.y`) được thay bằng số thật ở mọi chỗ trong chương (`Figure 3.y.1` thành `Figure 3.2.1`). Mục tên "Chapter conclusion" luôn được đưa xuống cuối chương.
- Hình: dòng `Figure 3.y.1: chú thích` rồi dòng ``File: `figures/ten.png` ``. Trong bài phải có chữ `(Figure 3.y.1)`, nếu không script cảnh báo và đặt hình ở cuối chương.
- Bảng Markdown, ngay sau là dòng `Table 4.2.1: chú thích`.
- Viết đoạn văn liền, không gạch đầu dòng (dòng bắt đầu bằng `- ` chỉ dùng trong References và Cover).

## Định dạng theo mẫu

- Mỗi chương kết thúc bằng mục **Chapter conclusion**.
- Tiêu đề chương dạng `Chapter 1: Introduction`; mục con đánh số `1.1`, `1.2`.
- Hình có chú thích ngay bên dưới, số theo chương.mục.thứ tự: `Figure 1.1.1: ...`. Trong bài phải nhắc đến từng hình.
- Times New Roman, chữ thường 13 pt, tiêu đề chương 18 pt đậm, tiêu đề mục 13 pt; khổ Letter, lề 1 inch, có số trang.
- Giãn dòng **double-spaced**, tổng **10 trang** theo đề bài (file mẫu để 1.3, không theo chỗ này).

## Số trang mỗi phần (double-spaced, khoảng 240 từ một trang, mỗi hình khoảng 1/3 trang)

| Phần | Trang | Tối đa khoảng |
|---|---|---|
| Chapter 1: Introduction | 1 | 170 từ + 1 hình |
| Chapter 2: Background | 1.5 | 250 từ + 1 hình |
| Chapter 3: Methodology | 3 | 480 từ + 3 hình |
| Chapter 4: Experiments and Results | 1.5 | 200 từ + 2 biểu đồ |
| Chapter 5: Discussion | 1.5 | 300 từ + 1 hình |
| Chapter 6: Conclusion | 0.5 | 120 từ |
| References | 1 | |

## Hình mỗi phần cần có

Lưu ảnh vào `figures/`, tên `fig_<nội_dung>.png`. Biểu đồ và sơ đồ dùng màu trong `src/theme.py` ([ui_guide.md](../ui_guide.md) mục 6).

| Chương | Hình | Người làm | Trạng thái |
|---|---|---|---|
| 1 | Figure 1.1.1: tổng quan hệ thống | Lâm | Có: `fig_system_overview.png` |
| 2 | Figure 2.2.1: forward và backward trên luật SF01, SF02 | Lâm | Có: `fig_forward_backward.png` |
| 3 | Cấu trúc luật và các lớp triệu chứng → trung gian → lỗi | Lâm | Bỏ: Ch3 chỉ còn 3 hình, mỗi người 1; các lớp này đã thấy trong `fig_cf_example.png` (Giang) |
| 3 | Màn chat của trợ lý đang hỏi, có câu "tại sao" và khả năng từng lỗi | Lâm | Có: `fig_motologic_chat.png` (Figure 3.5.1) |
| 3 | Ví dụ forward chaining tính CF | Giang | Có: `fig_cf_example.png` (`python src/report_figures.py`) |
| 3 | Màn hình MotoLogic: kết quả SE01 có đồng hồ CF và Wang | Giang | Có: `fig_motologic_4_result.png` (thêm `fig_motologic_1_setup`, `_2_guided`, `_3_symptoms`) |
| 3 | Ví dụ cây chứng minh Wang | Giang | Có: `fig_wang_proof.png` (`python src/report_figures.py`) |
| 3 | Luồng backward chaining hỏi từng câu | Khoa | Có: `fig_backward_flow.png` (`python src/evaluate.py --charts`) |
| 3 | Màn hình Hỏi đáp, đang mở Why | Khoa | Có: `fig_backward_screen_why.png` (BT10, câu 8) |
| 4 | Biểu đồ độ chính xác theo nhóm kịch bản | Khoa | Có: `fig_accuracy_by_group.png` |
| 4 | Biểu đồ số câu hỏi: mọi bộ phận và đúng bộ phận | Khoa | Có: `fig_backward_questions.png` |
| 5 | Sơ đồ trung gian "ngõ cụt" và luật dự phòng | Giang | Có: `fig_dead_end.png` (`python src/report_figures.py`) |
| 5 | Màn hình khi chưa đủ dữ kiện | Giang | Có: `fig_forward_screen_no_fault.png` |
