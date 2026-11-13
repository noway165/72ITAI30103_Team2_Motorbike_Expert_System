# Thuyết trình nhóm 2 (vấn đáp 16/11/2026): thứ tự, thời gian và lời thoại phần của Lâm

Slide chung: [nhom2_thuyet_trinh.pptx](nhom2_thuyet_trinh.pptx), 19 slide; lời thoại của từng slide cũng có trong phần Notes. File được tạo bằng `python tools/build_slides.py` (cần python-pptx và PowerPoint trên Windows). Script lấy slide của Lâm, chèn nguyên slide của Giang ([giang_forward_wang.pptx](giang_forward_wang.pptx)) và Khoa ([khoa_backward_eval.pptx](khoa_backward_eval.pptx)), rồi sửa các số đã đổi từ 12/11 (88 luật, 79 triệu chứng, Trợ lý 5,5 câu 30/30, 36,3 câu, 4 luật dự phòng). Hai ảnh màn hình cũ cũng được thay bằng ảnh giao diện hiện tại. Giang và Khoa sửa slide của mình thì chạy lại lệnh trên.

## Thứ tự và thời gian (thầy cho 15 phút)

| Slide | Người nói | Nội dung | Thời gian |
|---|---|---|---|
| 1–4 | Lâm | Mở đầu, bài toán, kiến trúc, MotoLogic | 2:15 |
| 5–10 | Giang | Suy diễn tiến, CF, Wang, màn kết quả + demo SE01 | 4:00 (nói 3:00, demo 1:00) |
| 11–15 | Khoa | Suy diễn lùi, giải thích, đánh giá + demo BT03 | 3:45 (nói 2:45, demo 1:00) |
| 16–17 | Lâm | Trợ lý chẩn đoán, chat theo luật + demo chat | 2:30 (nói 1:30, demo 1:00) |
| 18–19 | Lâm | Kết luận, cảm ơn | 0:45 |
| | | Cộng | 13:15, còn khoảng 1:45 để chuyển người và mở app |

Lời thoại cũ của Giang (4:20 + 2:00 demo) và Khoa (3:30 + 2:00 demo) dài hơn khung này, nên mỗi bạn chỉ demo một kịch bản và rút phần nói. Giang demo SE01 bằng "Tôi biết triệu chứng" và bấm kiểm chứng Wang; BT03 để dành nếu thầy hỏi. Khoa demo BT03 ở "Hỏi đáp từng câu", bấm "Tại sao" ở câu 3.

Trước buổi vấn đáp: mở sẵn `MotorbikeExpert.exe`, giao diện Sáng, tiếng Việt. Mỗi bạn demo xong bấm "Kể lại từ đầu" hoặc "Chẩn đoán mới".

## Lời thoại của Lâm

**Slide 1. Mở đầu (20 giây).** Em chào thầy. Em là Tăng Thoại Lâm, nhóm trưởng nhóm 2. Đề tài của nhóm là hệ chuyên gia chẩn đoán các lỗi thường gặp của xe máy. Em mở đầu bằng bài toán, kiến trúc và giao diện. Bạn Giang trình bày suy diễn tiến, hệ số chắc chắn và thuật toán Wang. Bạn Khoa trình bày suy diễn lùi và đánh giá. Cuối cùng em trình bày trợ lý chẩn đoán, phần chat và kết luận.

**Slide 2. Bài toán (40 giây).** Việt Nam có khoảng 74 triệu xe máy, nhiều hơn số người trưởng thành, theo WHO năm 2024. Khi xe hỏng, người lái chỉ biết triệu chứng. Cùng là đề không nổ, có khi chỉ cần sạc ắc quy, có khi lại là lỗi phải mang ra thợ. Nhóm xây hệ chuyên gia dựa trên luật với ba mục tiêu: xếp hạng lỗi theo độ tin cậy, báo lỗi nào tự xử lý được và lỗi nào cần thợ, và giải thích mọi kết luận bằng luật. Cơ sở tri thức có 79 triệu chứng, 40 lỗi trong 6 bộ phận và 88 luật, mỗi luật có CF và nguồn. Ngoài ra có luật và thông số riêng cho 6 dòng xe phổ biến.

**Slide 3. Kiến trúc (35 giây).** Cơ sở tri thức là các file JSON, mỗi bộ phận một file. Bộ kiểm tra luật, hiện ở màn Cơ sở tri thức, báo luật trùng, ký hiệu không dùng, thiếu nguồn hay vòng lặp; hiện tại không có lỗi nào. Cùng một bộ luật được dùng cho suy diễn tiến, suy diễn lùi và trợ lý chat. Thuật toán Wang chứng minh lại kết luận một cách độc lập. Giao diện gồm GUI MotoLogic, CLI và file exe chạy offline.

**Slide 4. MotoLogic (40 giây).** Giao diện có ba bước. Bước một chọn dòng xe, hoặc loại xe và kiểu cấp xăng nếu là xe khác, rồi chọn một trong ba cách chẩn đoán. Hỏi đáp từng câu dùng suy diễn lùi, phần của Khoa. Chọn triệu chứng dùng suy diễn tiến, phần của Giang. Kể bằng lời là trợ lý chat, phần của em. Cả ba ra cùng một màn kết quả: lỗi đứng đầu, độ tin cậy, chuỗi luật, cách xử lý, thông số theo sách hướng dẫn của dòng xe và kiểm chứng Wang. Mời bạn Giang.

**Slide 16. Trợ lý chẩn đoán (50 giây).** Cách thứ ba là kể bằng lời. Bộ đọc so khớp cụm từ trong câu kể, bỏ dấu và hiểu phủ định, để lấy ra các triệu chứng. Sau đó trợ lý không hỏi lần lượt như suy diễn lùi. Nó chọn câu có information gain lớn nhất, tức là câu chia các lỗi còn lại tốt nhất, và dừng khi lỗi đứng đầu đã được luật chứng minh. Kết luận cuối vẫn do suy diễn tiến và CF đưa ra. Trên 30 kịch bản, trợ lý cần trung bình 5,5 câu và đúng cả 30. Nhưng các mô tả này đã dùng khi viết bộ đọc, nên nhóm thử thêm 10 mô tả mới: đúng 8 trên 10 với tiếng Việt và 7 với tiếng Anh. Đây là điểm yếu chính: bộ đọc chỉ hiểu cụm từ có trong danh sách.

**Slide 17. Chat theo luật (40 giây, rồi demo 1 phút).** Trong lúc hỏi, người lái có thể hỏi lại trợ lý. Không có câu trả lời soạn sẵn: mỗi câu được ghép từ luật, câu hỏi và CF trong cơ sở tri thức. Hỏi "tại sao" thì trợ lý liệt kê các luật dùng câu đang hỏi, điều kiện nào đã có, điều kiện nào đang hỏi. Hỏi "làm sao biết" thì có chuỗi luật từ câu trả lời tới lỗi. Hỏi "sửa thế nào" hay "có nguy hiểm không" thì có cách xử lý, mức độ và thông số của dòng xe.

Demo: Chẩn đoán → Honda Vision → Kể bằng lời → gõ "đề chỉ nghe tạch tạch, còi cũng yếu" → Phân tích. Hỏi "tại sao hỏi vậy?", trả lời "có", hỏi "sửa thế nào?", rồi bấm "Xem kết quả đầy đủ": ắc quy yếu, khối "Riêng cho Honda Vision" có loại ắc quy theo sách hướng dẫn.

**Slide 18. Kết luận (35 giây).** Cả suy diễn tiến và suy diễn lùi đều xếp đúng lỗi ở hạng 1 trong 30 kịch bản, và Wang không khác suy diễn tiến lần nào. Chọn bộ phận trước giảm số câu từ 39,7 xuống 9. Mọi câu trả lời đều chỉ ra được luật. Hạn chế: luật chỉ có điều kiện khẳng định nên trả lời "không" không làm giảm CF, chat chỉ hiểu cụm từ có trong danh sách, và CF cùng kịch bản là do nhóm tự viết. Hướng tiếp theo là thêm bằng chứng phủ định, lấy cụm từ từ nhật ký sửa xe thật và đo CF trên ca sửa thật.

**Slide 19. Cảm ơn (10 giây).** Phần trình bày của nhóm em đến đây là hết. Nhóm em cảm ơn thầy đã lắng nghe, mời thầy đặt câu hỏi.

## Câu hỏi vấn đáp có thể gặp (phần của Lâm)

- **CF là gì, có phải xác suất không?** Không phải xác suất. Đó là độ tin cậy của luật theo cách của MYCIN, do nhóm ước lượng từ nguồn của từng luật. Các điều kiện lấy min, luật nhân CF của nó, nhiều luật cùng kết luận thì gộp CF1 + CF2 × (1 − CF1). Lỗi có CF từ 0,2 trở lên mới được báo.
- **Information gain tính thế nào?** Mỗi lỗi có các tập triệu chứng chứng minh được nó qua luật. Với mỗi câu chưa hỏi, trợ lý tính độ bất định (entropy) của các lỗi trước và sau hai câu trả lời có thể, rồi chọn câu giảm nhiều nhất. Câu trả lời được cho phép nhiễu 10%, nên một câu trả lời sai không loại hẳn một lỗi.
- **Tại sao 30/30 mà vẫn nói chat yếu?** 30 mô tả đó đã dùng khi viết danh sách cụm từ. Với 10 mô tả mới, chưa từng dùng, kết quả là 8/10 (tiếng Việt) và 7/10 (tiếng Anh). Ví dụ "tay phanh mềm" thì hiểu, "bóp phanh thấy mềm" thì không.
- **Luật dòng xe lấy từ đâu?** Thông số (ắc quy, bugi, nhớt, áp suất lốp…) lấy từ sách hướng dẫn của hãng, có ghi số trang. Chín luật MD01–MD09 dựa trên bài báo và trang của tiệm sửa xe, nên nguồn yếu hơn; báo cáo đã ghi rõ hạn chế này.
- **Có dùng AI hay mô hình ngôn ngữ để trả lời chat không?** Không. Chương trình chạy offline. Câu trả lời ghép từ luật, câu hỏi và CF trong cơ sở tri thức, nên câu nào cũng chỉ ra được luật.
