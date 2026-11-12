# Lời thoại phần của Giang: suy diễn tiến, CF và Wang (vấn đáp 16/11/2026)

Slide: [giang_forward_wang.pptx](giang_forward_wang.pptx) (6 slide, lời thoại cũng có trong phần Notes của từng slide), khoảng 4 phút 20 giây, cộng 2 phút demo. Thứ tự demo của nhóm: Lâm (Trợ lý) → Giang → Khoa. Màu theo giao diện MotoLogic ([docs/design/motologic_spec.md](../design/motologic_spec.md)); Lâm ghép vào bản chung.

Số liệu ngày 12/11: 79 luật, 30/30 kịch bản đúng hạng 1, Wang khớp forward chaining trên 30 kịch bản và 500 bộ ngẫu nhiên (`python src/wang.py --scenarios --random 500`). Nếu luật thay đổi trước ngày 16/11, chạy lại lệnh này và sửa slide 4, 5.

## Slide 1. Mở đầu (khoảng 20 giây)

Em là Kiều Bảo Giang. Phần của em gồm ba việc: bộ suy diễn tiến (forward chaining), cách xếp hạng lỗi bằng hệ số chắc chắn CF, và dùng thuật toán Wang để kiểm chứng rằng bộ suy diễn của nhóm không suy luận sai. Cuối phần em giới thiệu giao diện MotoLogic và demo hai kịch bản.

## Slide 2. Suy diễn tiến: từ triệu chứng tới lỗi (khoảng 50 giây)

Suy diễn tiến đi theo dữ liệu. Người lái chọn trước các triệu chứng đang gặp. Mỗi luật có một bộ đếm số điều kiện chưa biết là đúng; mỗi khi một triệu chứng hay kết luận mới được xử lý, bộ đếm của các luật dùng nó giảm đi một, về 0 thì luật chạy và kết luận được đưa vào hàng đợi. Đây đúng là thuật toán PL-FC-ENTAILS trong sách AIMA chương 7. Ví dụ bên phải: xe Vision đề chỉ nghe tạch tạch và còi yếu, luật SF01 suy ra điện yếu; từ điện yếu, luật SF14 cho ra ắc quy yếu; biết thêm ắc quy đã dùng hơn hai năm thì luật SF02 nâng độ tin cậy lên.

## Slide 3. Xếp hạng lỗi bằng hệ số chắc chắn (CF) (khoảng 45 giây)

Cùng một bộ triệu chứng có thể suy ra nhiều lỗi, nên phải xếp hạng. Nhóm dùng hệ số chắc chắn CF theo cách của hệ chuyên gia MYCIN. Các điều kiện nối bằng VÀ lấy CF nhỏ nhất; luật nhân cf của nó với CF điều kiện; nhiều luật cùng kết luận thì gộp bằng công thức CF1 cộng CF2 nhân một trừ CF1. Ví dụ ắc quy yếu: ba luật SF02, SF03, SF14 cho 0.765, 0.675 và 0.54, gộp lại được 0.96. Lỗi có CF từ 0.2 trở lên mới được báo, xếp từ cao xuống thấp.

## Slide 4. Kiểm chứng bằng thuật toán Wang (khoảng 55 giây)

Bộ suy diễn là code nhóm tự viết nên có thể sai. Để kiểm tra, em dùng thuật toán Wang, một bộ chứng minh định lý logic mệnh đề độc lập. Mỗi luật thành một công thức kéo theo, triệu chứng là nguyên tử, và Wang chứng minh sequent luật, triệu chứng suy ra lỗi bằng cách bỏ dần từng phép nối theo bảng bên trái, tới khi mỗi nhánh có cùng một nguyên tử ở hai bên. Vì forward chaining đúng và đủ với Horn clause, tập lỗi nó suy ra phải trùng với tập lỗi Wang chứng minh được. Em so sánh trên 30 kịch bản và 500 bộ triệu chứng ngẫu nhiên, hơn hai mươi mốt nghìn lần, không có khác biệt nào.

## Slide 5. Kết quả trên 30 kịch bản (khoảng 50 giây)

Mỗi nhóm hệ thống có 10 kịch bản do người không viết luật soạn, để không tự chấm bài mình. Hiện cả 30 kịch bản đều ra đúng lỗi ở hạng 1, với cả suy diễn tiến lẫn suy diễn lùi. Lần chạy đầu sai 2 kịch bản, và Wang cũng không chứng minh được, nghĩa là thiếu luật chứ bộ suy diễn không sai. Hai lỗi cùng một dạng: suy ra được kết luận trung gian nhưng thiếu một triệu chứng phụ để đi tới lỗi. Nhóm sửa bằng luật dự phòng có CF thấp hơn, như SF14 của Lâm, TS15 và BR13 của Khoa, EN17, EN18, TR12 của em; bỏ các luật này thì chỉ còn 28 trên 30.

## Slide 6. Màn Chẩn đoán MotoLogic (khoảng 40 giây)

Cuối cùng là màn Chẩn đoán MotoLogic. Sau 3 bước khai báo xe, kể triệu chứng, xem kết quả, chương trình hiện lỗi có khả năng cao trên một đồng hồ CF kiểu công-tơ-mét, kèm chuỗi luật thật đã dùng. Phần “Chương trình suy ra thế nào” liệt kê từng luật, từ câu trả lời của người lái tới kết luận. Ô Kiểm chứng bằng Wang cho bấm để chứng minh kết luận; hiện dấu ✓ khi luật và câu trả lời kéo theo lỗi đó. Bây giờ em demo nhanh 2 kịch bản.

## Demo trên màn MotoLogic (khoảng 2 phút)

Mở `dist\MotorbikeExpert.exe` (hoặc `python src/gui.py`). Màn đầu tiên là **Chẩn đoán**, giao diện tiếng Việt, chế độ Sáng.

**Kịch bản SE01: ắc quy yếu (khoảng 70 giây)**
1. Bước 1: chọn **Xe tay ga**, **Phun xăng (FI)**, cách **Tôi biết triệu chứng**, bấm **Bắt đầu chẩn đoán**.
   Lời nói: "Xe Vision để qua đêm, sáng bấm đề chỉ nghe tạch tạch, còi yếu, ắc quy đã dùng hơn 2 năm."
2. Bước 2: bấm chip **Khởi động, nhiên liệu**, tick 3 dòng: *Khi bấm nút đề… chỉ nghe tiếng tạch tạch*, *Còi kêu yếu hơn bình thường*, *Ắc quy đã dùng hơn 2 năm*. Chỉ vào khối "Quan sát của bạn" bên phải ("3 đã chọn"). Bấm **Tìm lỗi phù hợp**.
3. Bước 3: chỉ vào đồng hồ CF (0.89) và dòng "Theo chuỗi luật SF01 → SF02, SF14".
   Lời nói: "Đây là phần Vì sao: SF01 từ đề tạch tạch và còi yếu ra điện yếu, rồi SF02 và SF14 ra ắc quy yếu."
4. Bấm **Kiểm chứng kết luận** trong ô Wang → hiện "✓ Wang chứng minh được".
   Lời nói: "Bộ chứng minh độc lập xác nhận luật cộng câu trả lời kéo theo lỗi này."

**Kịch bản BT03: rò rỉ dầu phanh (khoảng 50 giây)**
1. Bấm **Chẩn đoán mới**. Bước 1: chọn **Xe số**, **Phun xăng (FI)**, cách **Tôi biết triệu chứng**, bấm **Bắt đầu chẩn đoán**.
   Lời nói: "Xe Winner: tay phanh trước mềm, bình dầu dưới vạch MIN, cùm phanh ướt dầu."
2. Bước 2: bấm chip **Phanh**, tick *Tay phanh mềm*, *Mức dầu phanh … thấp hơn vạch thấp nhất*, *Thấy dầu phanh rỉ ướt*. Bấm **Tìm lỗi phù hợp**.
3. Bước 3: tên lỗi **Rò rỉ dầu phanh**; chỉ vào icon cờ-lê đỏ **Cần mang ra thợ** ở "Bước tiếp theo", và "Cũng có thể là: Lọt khí trong đường dầu phanh".
4. Mở **Lịch sử phiên** (thanh bên) để thấy 2 phiên vừa làm, rồi chuyển lời cho Khoa.

Dự phòng: nếu màn MotoLogic lỗi, demo cùng 2 kịch bản ở màn cũ **Theo triệu chứng** (ô "Kịch bản mẫu" → SE01, BT03).

## Câu hỏi vấn đáp có thể gặp

**Forward chaining khác backward chaining thế nào? Khi nào dùng cái nào?**
Forward đi từ dữ liệu: người lái khai hết triệu chứng rồi chương trình suy ra mọi thứ có thể. Backward đi từ giả thuyết: chọn một lỗi rồi hỏi các câu cần để chứng minh nó. Trên 30 kịch bản hai bên cho cùng kết quả (30/30). Backward hỏi trung bình 39,7 câu khi xét mọi bộ phận, còn 9,0 câu khi chọn đúng bộ phận.

**Trợ lý chẩn đoán khác backward ở đâu?**
Trợ lý đọc câu người lái kể, rồi chỉ hỏi câu có information gain cao nhất: trung bình 5,8 câu và đúng 27/30 (tiếng Việt), so với 39,7 câu và 30/30 của backward. Nhanh hơn khoảng 7 lần nhưng có thể bỏ sót triệu chứng người lái không nhắc tới, nên giao diện vẫn gợi ý hỏi đáp từng câu.

**Vì sao thời gian chạy tuyến tính?**
Mỗi ký hiệu chỉ được lấy ra khỏi hàng đợi một lần, và mỗi lần chỉ giảm bộ đếm của các luật dùng nó. Tổng số lần giảm bằng tổng số điều kiện của mọi luật.

**CF có phải xác suất không?**
Không. CF là mức tin của người viết luật, lấy từ tài liệu và kinh nghiệm, chưa đo trên dữ liệu sửa xe thật. Nó dùng để xếp hạng, không nói "70% khả năng".

**Vì sao gộp nhiều luật bằng CF1 + CF2 × (1 − CF1)?**
Đây là công thức của MYCIN cho bằng chứng dương: mỗi luật thêm vào làm CF tăng nhưng không vượt quá 1, và thứ tự gộp không làm đổi kết quả. Nhược điểm: nó coi các luật là độc lập, trong khi SF02, SF03, SF14 cùng dùng "điện yếu".

**Vì sao cần Wang khi đã có unit test?**
Unit test chỉ kiểm tra những trường hợp mình nghĩ ra. Wang là bộ chứng minh độc lập với code suy diễn, nên có thể so trên hàng nghìn bộ triệu chứng ngẫu nhiên. Forward chaining đúng và đủ với Horn clause (AIMA chương 7), nên hai bên phải ra cùng tập lỗi; nếu khác là code suy diễn sai.

**Wang có chậm không?**
Mỗi luật bên trái tách 2 nhánh nên về lý thuyết có thể rất nhiều nhánh. Em chỉ đưa vào các luật liên quan tới lỗi cần chứng minh và tách trước luật đã đủ điều kiện, nên ví dụ ắc quy yếu chỉ mất 9 sequent; 21.200 lần so sánh chạy trong khoảng 1 giây.

**Câu trả lời "không" được xử lý thế nào?**
Luật chỉ có VÀ, không có phủ định, nên "không" chỉ làm luật không chạy, không hạ CF của lỗi. Ví dụ ET05: người lái nói nước làm mát vẫn đủ, nhưng "thiếu nước làm mát" vẫn đứng thứ 2 với CF 0.45. Hướng phát triển: CF âm như MYCIN.

**Luật dự phòng là gì, có làm sai kết quả khác không?**
Khi một kết luận trung gian (như "giảm xóc mất giảm chấn") chỉ đi tiếp được nếu có thêm một triệu chứng phụ, nhóm thêm một luật dự phòng CF thấp hơn tới lỗi thường gặp nhất (SF14, TS15, BR13, EN17, EN18, TR12). Bỏ các luật này thì chỉ đúng 28/30. Khi có triệu chứng phụ, luật cụ thể hơn vẫn xếp trên, và Wang vẫn khớp forward chaining 100%.
