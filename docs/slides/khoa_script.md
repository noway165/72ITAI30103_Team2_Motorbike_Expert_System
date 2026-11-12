# Lời thoại phần của Khoa: suy diễn lùi, giải thích và đánh giá (vấn đáp 16/11/2026)

Slide: [khoa_backward_eval.pptx](khoa_backward_eval.pptx) (5 slide, cùng mẫu với slide của Giang; lời thoại cũng có trong phần Notes của từng slide). Nói khoảng 3 phút 30 giây, cộng demo khoảng 2 phút.

Số liệu từ `python src/evaluate.py --charts` và `python src/evaluate_assistant.py` ngày 13/11 (79 luật, 30 kịch bản). Số so sánh công bằng (36,6 câu; 22,2 câu, 28/30) xem `docs/progress/nguyen_nam_khoa.md`, mục 3. Nếu luật đổi trước 16/11, chạy lại và sửa slide 4.

## Slide 1. Mở đầu (khoảng 20 giây)

Em là Nguyễn Nam Khoa. Phần của em gồm ba việc: bộ suy diễn lùi (backward chaining) dùng cho màn Hỏi đáp từng câu, phần giải thích Tại sao và Như thế nào, và đánh giá cả hệ thống trên 30 kịch bản, có so sánh với Trợ lý chẩn đoán của bạn Lâm. Cuối phần em demo màn Hỏi đáp.

## Slide 2. Suy diễn lùi: từ giả thuyết tới câu hỏi (khoảng 60 giây)

Suy diễn lùi đi từ giả thuyết. Chương trình lần lượt lấy từng lỗi làm mục tiêu, tìm các luật kết luận lỗi đó, và biến điều kiện của luật thành mục tiêu con. Gặp kết luận trung gian thì đi lùi tiếp; gặp triệu chứng chưa biết thì mới hỏi người lái. Một điều kiện trả lời Không thì bỏ cả luật, nên các câu còn lại của luật đó không bị hỏi. Ví dụ bên phải là kịch bản BT03: để chứng minh rò rỉ dầu phanh, luật BR13 cần mạch dầu phanh bị hụt dầu, luật BR04 lại cần tay phanh mềm và dầu phanh dưới vạch MIN, nên đó chính là các câu được hỏi. Câu trả lời được nhớ lại, nên không câu nào bị hỏi hai lần.

## Slide 3. Giải thích: Tại sao và Như thế nào (khoảng 60 giây)

Hệ chuyên gia phải giải thích được. Trong khi hỏi, người lái bấm Tại sao hỏi câu này thì thấy chuỗi luật đang thử, ví dụ BR08 dùng kết luận của BR04, và câu đang hỏi là điều kiện của luật nào. Khi có kết quả, bấm Vì sao ra kết quả này thì thấy triệu chứng đã chọn, các luật đã chạy và CF. Bên phải là cách ra 0.96 cho rò rỉ dầu phanh: BR06 cho 0.9, BR13 cho 0.6 nhân 0.98, gộp theo MYCIN được 0.96. Vì backward thử mọi luật kết luận một lỗi, CF giống hệt forward chaining của bạn Giang. Ngoài ra người lái có thể trả lời Không biết, được coi như Không và được nhắc kiểm tra lại, và có thể quay lại câu trước.

## Slide 4. Đánh giá trên 30 kịch bản (khoảng 75 giây)

Em đánh giá trên 30 kịch bản, mỗi nhóm bộ phận 10 kịch bản, do người không viết luật soạn. Backward đúng lỗi hạng 1 ở cả 30 kịch bản và cho cùng lỗi, cùng CF với forward. Nếu hỏi mọi bộ phận thì trung bình 39,7 câu trên 73 triệu chứng; nếu người lái chọn đúng bộ phận trước thì chỉ còn 9 câu, ít hơn 4,4 lần. Trợ lý của bạn Lâm đọc mô tả bằng lời rồi chọn câu theo information gain, chỉ cần 5,8 câu nhưng đúng 27 trên 30, sót các lỗi phanh và giảm xóc có một triệu chứng mà mô tả không nhắc tới. Em có kiểm tra so sánh có công bằng không: cho backward đọc cùng mô tả thì vẫn 36,6 câu, còn nếu backward dừng ở lỗi đầu tiên chứng minh được thì 22,2 câu, đúng 28 trên 30. Vậy Trợ lý nhanh chủ yếu nhờ chọn câu thông minh và dừng sớm, đổi lại là có thể sót lỗi; backward chậm hơn nhưng không bỏ sót lỗi nào mà luật chứng minh được.

## Slide 5. Màn hình Hỏi đáp và demo BT03 (khoảng 2 phút, gồm demo)

Cuối cùng là màn Hỏi đáp từng câu. Bên trái chọn bộ phận, danh sách giả thuyết còn lại thu hẹp dần sau mỗi câu. Bên phải là câu hỏi, gợi ý và ba nút Có, Không, Không biết, có phím tắt. Em demo nhanh kịch bản BT03: chọn Phanh, trả lời Có cho tay phanh mềm, ở câu 2 và 3 bấm Tại sao để thấy chuỗi BR08, BR04 rồi BR08, BR05. Sau 9 câu, kết quả đứng đầu là rò rỉ dầu phanh, CF 0.96, kèm nhãn Cần mang ra thợ. Phần của em đến đây là hết, em cảm ơn thầy đã lắng nghe.

## Kịch bản demo (khoảng 2 phút, sau Lâm và Giang)

1. Mở màn Hỏi đáp từng câu (màn MotoLogic: Chẩn đoán → Hỏi đáp từng câu; nếu màn mới chưa ổn thì dùng màn Hỏi đáp cũ).
2. Chọn bộ phận **Phanh**, bấm Bắt đầu.
3. Câu 1 “Tay phanh mềm, phải bóp sâu mới ăn?” → **Có**.
4. Câu 2 “Mức dầu phanh thấp hơn vạch MIN?” → bấm **Tại sao** trước: thấy BR08 (lọt khí) dùng kết luận của BR04 (hụt dầu phanh). Trả lời **Có**.
5. Câu 3 “Thấy dầu phanh rỉ ướt…?” → bấm **Tại sao**: chuỗi BR08 ← BR05. Trả lời **Có**.
6. Câu 4 đến 9 trả lời **Không** (quãng phanh dài hơn, dầu phanh cũ, phanh bó, rung, kêu rít, kêu ken két).
7. Kết quả: **Rò rỉ dầu phanh, CF 0.96, Cần mang ra thợ**; thứ 2 là Lọt khí trong đường dầu phanh 0.74. Mở “Vì sao ra kết quả này?”: 3 triệu chứng → BR04, BR05 (0.98) → BR06, BR13 (0.96).

Thứ tự câu hỏi này được kiểm bằng test `test_bt03_demo_path` trong `tests/test_backward_chaining.py`.

## Câu hỏi vấn đáp có thể gặp

**Backward chaining chọn giả thuyết theo thứ tự nào?**
Theo thứ tự tên lỗi trong bộ phận đã chọn. Thứ tự không đổi kết quả hay CF (mọi luật đều được thử), chỉ đổi thứ tự câu hỏi. Đây là chỗ Trợ lý cải tiến: chọn câu theo information gain.

**Vì sao backward hỏi tới 39,7 câu?**
Vì nó chứng minh hết 40 giả thuyết để xếp hạng đầy đủ như forward, không dừng ở lỗi đầu tiên. Nếu dừng ở lỗi đầu tiên chứng minh được thì 22,2 câu nhưng chỉ đúng 28/30, vì lỗi chứng minh được trước chưa chắc có CF cao nhất.

**So sánh với Trợ lý có công bằng không?**
Em kiểm tra ba điểm. Một, Trợ lý được đọc mô tả còn backward thì không: cho backward đọc cùng mô tả vẫn 36,6 câu, nên lợi thế chủ yếu không nằm ở mô tả. Hai, cách dừng khác nhau: backward chứng minh hết, Trợ lý dừng khi lỗi đứng đầu đã chứng minh được và chiếm ≥ 70% xác suất. Ba, Trợ lý giới hạn 15 câu; 7 kịch bản (tiếng Việt) chạm giới hạn này, trong đó có cả 3 kịch bản sai. Ngoài ra câu trả lời loại trừ nhau (ví dụ còi yếu / còi bình thường) được Trợ lý điền tự động, không tính là câu hỏi.

**“Không biết” xử lý thế nào?**
Coi như “Không” để suy luận tiếp, nhưng ghi lại và hiện danh sách cần kiểm tra lại ở màn kết quả. Hướng phát triển: cho trả lời bằng CF (engine đã nhận số trong (0, 1]).

**Why và how khác nhau thế nào?**
Why trả lời trong lúc hỏi: câu này là điều kiện của luật nào, luật đó phục vụ giả thuyết nào. How trả lời sau khi có kết quả: từ triệu chứng nào, qua luật nào, CF bao nhiêu.

**Undo làm thế nào?**
Bỏ câu trả lời cuối rồi chạy lại suy luận từ đầu với các câu trả lời còn lại. Engine tất định nên câu hỏi ra lại đúng như trước; cơ sở tri thức nhỏ nên chạy lại không tốn thời gian.
