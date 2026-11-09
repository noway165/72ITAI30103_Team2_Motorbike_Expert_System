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

## Định dạng theo mẫu

- Mỗi chương kết thúc bằng mục **Chapter conclusion**.
- Tiêu đề chương dạng `Chapter 1: Introduction`; mục con đánh số `1.1`, `1.2`.
- Hình có chú thích ngay bên dưới, số theo chương.mục.thứ tự: `Figure 1.1.1: ...`. Trong bài phải nhắc đến từng hình.
- Times New Roman, chữ thường 13 pt, tiêu đề chương 18 pt đậm, tiêu đề mục 13 pt; khổ Letter, lề 1 inch, có số trang.
- Giãn dòng: đề bài yêu cầu double-spaced, tối đa 10 trang (file mẫu đang để 1.3).

## Hình mỗi phần cần có

Lưu ảnh vào `figures/`, tên `fig_<nội_dung>.png`. Biểu đồ và sơ đồ dùng màu trong `src/theme.py` ([ui_guide.md](../ui_guide.md) mục 6).

| Chương | Hình | Người làm | Trạng thái |
|---|---|---|---|
| 1 | Figure 1.1.1: tổng quan hệ thống | Lâm | Có: `fig_system_overview.png` |
| 2 | Figure 2.2.1: forward và backward trên luật SF01, SF02 | Lâm | Có: `fig_forward_backward.png` |
| 3 | Cấu trúc luật và các lớp triệu chứng → trung gian → lỗi | Lâm | Chưa |
| 3 | Ví dụ forward chaining tính CF | Giang | Chưa |
| 3 | Màn hình Theo triệu chứng | Giang | Có: `fig_forward_screen_se01.png` |
| 3 | Ví dụ cây chứng minh Wang | Giang | Chưa |
| 3 | Luồng backward chaining hỏi từng câu | Khoa | Chưa |
| 3 | Màn hình Hỏi đáp, đang mở Why | Khoa | Chưa |
| 4 | Biểu đồ độ chính xác theo nhóm kịch bản | Khoa | Chưa |
| 4 | Biểu đồ số câu hỏi: mọi bộ phận và đúng bộ phận | Khoa | Chưa |
| 5 | Sơ đồ trung gian "ngõ cụt" và luật dự phòng | Giang | Chưa |
| 5 | Màn hình khi chưa đủ dữ kiện | Giang | Có: `fig_forward_screen_no_fault.png` |
