# Thuyết trình nhóm 2 (vấn đáp 16/11/2026): thứ tự, thời gian, demo và lời thoại

Slide chung: [Group2_Presentation.pptx](Group2_Presentation.pptx), 13 slide tiếng Anh; lời thoại (tiếng Anh) nằm trong phần Notes của từng slide. File được tạo bằng `python tools/build_slides.py` (cần python-pptx; dùng theme của deck Giang). Muốn sửa chữ hay lời thoại thì sửa trong script rồi chạy lại lệnh. Số liệu lấy từ `src/evaluate.py`, `src/evaluate_assistant.py`, `src/wang.py`, `tools/compare_fair.py` ngày 13/11.

Deck tiếng Việt cũ của Giang ([giang_forward_wang.pptx](giang_forward_wang.pptx), [giang_script.md](giang_script.md)) và Khoa ([khoa_backward_eval.pptx](khoa_backward_eval.pptx), [khoa_script.md](khoa_script.md)) giữ lại để tham khảo khi trả lời vấn đáp; số liệu trong đó là của 12/11.

## Thứ tự và thời gian (thầy cho 15 phút)

| Slide | Người nói | Nội dung | Thời gian |
|---|---|---|---|
| 1–5 | Lâm | Tiêu đề, thành viên và nhiệm vụ, nội dung, bài toán, kiến trúc | 2:00 |
| 6–7 | Giang | Suy diễn tiến và CF, thuật toán Wang | 1:45 |
| 8–9 | Khoa | Suy diễn lùi và giải thích, đánh giá trên 30 kịch bản | 1:45 |
| 10 | Lâm | Trợ lý chẩn đoán và chat theo luật | 0:45 |
| 11 | Cả nhóm | Demo trực tiếp (mỗi bạn khoảng 1:30) | 5:00 |
| 12–13 | Lâm | Kết luận, cảm ơn | 0:45 |
| | | Cộng | 12:00, còn khoảng 3 phút để chuyển người và mở app |

Lời thoại ước khoảng 900 từ tiếng Anh, khoảng 7 phút nếu nói 130 từ một phút.

## Demo (slide 11)

Trước buổi vấn đáp: mở sẵn `MotorbikeExpert.exe`, chọn **EN** và **Light**. Mỗi bạn demo xong bấm "New diagnosis" ở màn kết quả để về bước 1.

1. **Lâm, Describe it in words.** Chọn Honda Vision → Describe it in words → gõ "the starter only clicks, the horn is weak" → Analyse. Hỏi "why?", trả lời "yes", rồi bấm "See the full result": ắc quy yếu, khối "For your Honda Vision" có loại ắc quy theo sách hướng dẫn (tr. 145–147).
2. **Giang, I know my symptoms.** Another bike → I know my symptoms → tick "starter only clicks", "horn weaker than usual", "battery more than 2 years old" → See the result: Weak or flat battery, confidence 89%, chuỗi SF01 → SF02, SF14. Bấm "Cross-check" (thuật toán Wang): hiện dấu ✓.
3. **Khoa, Guide me with questions.** Guide me with questions → Brakes. Trả lời Yes cho "brake lever soft or spongy" (câu 1) và "fluid below MIN" (câu 2). Ở câu 3 ("brake fluid leaking") bấm xem "Why this question?", rồi trả lời tới hết (9 câu): Brake fluid leak, CF 0.96, "Take it to a mechanic".

Dự phòng: nếu màn MotoLogic lỗi, dùng màn cũ Ctrl+5 (By symptoms, ô "Sample scenario" → SE01) và Ctrl+6 (Step-by-step, chọn Brakes → BT03). Ở màn Ctrl+6, thứ tự câu hỏi khác: câu 1 là mức dầu dưới MIN.

## Câu hỏi vấn đáp có thể gặp

- **CF là gì, có phải xác suất không?** Không phải xác suất. Đó là độ tin cậy của luật theo cách của MYCIN, do nhóm ước lượng từ nguồn của từng luật. Các điều kiện lấy min, luật nhân CF của nó, nhiều luật cùng kết luận thì gộp CF1 + CF2 × (1 − CF1). Lỗi có CF từ 0,2 trở lên mới được báo. (Lâm, Giang)
- **Tại sao cần Wang khi đã có suy diễn tiến?** Bộ suy diễn là code nhóm tự viết. Wang là bộ chứng minh độc lập, không dùng chung code. Hai bên phải ra cùng tập lỗi vì suy diễn tiến đúng và đủ với Horn clause. (Giang)
- **Suy diễn lùi khác suy diễn tiến thế nào?** Lùi đi từ giả thuyết và chỉ hỏi điều cần để chứng minh, nên khi chọn đúng bộ phận chỉ còn 9 câu. Nó thử mọi luật của một lỗi nên ra cùng lỗi và cùng CF với suy diễn tiến. (Khoa)
- **Information gain tính thế nào?** Mỗi lỗi có các tập triệu chứng chứng minh được nó qua luật. Với mỗi câu chưa hỏi, trợ lý tính entropy của các lỗi trước và sau hai câu trả lời có thể, rồi chọn câu giảm nhiều nhất. Câu trả lời được cho phép nhiễu 10%. (Lâm)
- **Tại sao 30/30 mà vẫn nói chat yếu?** 30 mô tả đó đã dùng khi viết danh sách cụm từ. Với 10 mô tả mới, kết quả là 8/10 (tiếng Việt) và 7/10 (tiếng Anh): "tay phanh mềm" thì hiểu, "bóp phanh thấy mềm" thì không. (Lâm)
- **Có dùng mô hình ngôn ngữ để trả lời chat không?** Không. Chương trình chạy offline; câu trả lời ghép từ luật, câu hỏi và CF trong cơ sở tri thức. (Lâm)
- **Luật dòng xe lấy từ đâu?** Thông số (ắc quy, bugi, nhớt, áp suất lốp…) lấy từ sách hướng dẫn của hãng, có số trang. Chín luật MD01–MD09 dựa trên báo và trang của tiệm sửa xe, nên nguồn yếu hơn; báo cáo ghi rõ. (Lâm)
- **Hạn chế lớn nhất?** Luật chỉ có điều kiện khẳng định, nên trả lời "không" không làm giảm CF (ví dụ ET05: thiếu nước làm mát vẫn đứng thứ 2 với CF 0,45 dù nước đủ). (Giang)
