# Lời thoại phần của Giang: suy diễn tiến, CF và Wang (Oral 19/11/2026)

Slide: [giang_forward_wang.pptx](giang_forward_wang.pptx) (6 slide, lời thoại cũng có trong phần Notes của từng slide). Tổng khoảng 4 phút 50 giây; phần mỗi người khoảng 5 phút. Màu và chữ theo [docs/ui_guide.md](../ui_guide.md); Lâm ghép vào bản chung.

Số liệu lấy từ `python src/wang.py --scenarios --random 500` ngày 09/11 (77 luật, 30 kịch bản). Nếu luật thay đổi trước ngày 19/11, chạy lại lệnh này và sửa slide 4, 5.

## Slide 1. Mở đầu (khoảng 20 giây)

Em là Kiều Bảo Giang. Phần của em gồm ba việc: bộ suy diễn tiến (forward chaining), cách xếp hạng lỗi bằng hệ số chắc chắn CF, và dùng thuật toán Wang để kiểm chứng rằng bộ suy diễn của nhóm không suy luận sai. Cuối phần em giới thiệu màn hình Theo triệu chứng trong chương trình.

## Slide 2. Suy diễn tiến: từ triệu chứng tới lỗi (khoảng 50 giây)

Suy diễn tiến đi theo dữ liệu. Người lái chọn trước các triệu chứng đang gặp. Mỗi luật có một bộ đếm số điều kiện chưa biết là đúng; mỗi khi một triệu chứng hay kết luận mới được xử lý, bộ đếm của các luật dùng nó giảm đi một, về 0 thì luật chạy và kết luận được đưa vào hàng đợi. Đây đúng là thuật toán PL-FC-ENTAILS trong sách AIMA chương 7. Ví dụ bên phải: xe Vision đề chỉ nghe tạch tạch và còi yếu, luật SF01 suy ra điện yếu; từ điện yếu, luật SF14 cho ra ắc quy yếu; biết thêm ắc quy đã dùng hơn hai năm thì luật SF02 nâng độ tin cậy lên.

## Slide 3. Xếp hạng lỗi bằng hệ số chắc chắn (CF) (khoảng 45 giây)

Cùng một bộ triệu chứng có thể suy ra nhiều lỗi, nên phải xếp hạng. Nhóm dùng hệ số chắc chắn CF theo cách của hệ chuyên gia MYCIN. Các điều kiện nối bằng VÀ lấy CF nhỏ nhất; luật nhân cf của nó với CF điều kiện; nhiều luật cùng kết luận thì gộp bằng công thức CF1 cộng CF2 nhân một trừ CF1. Ví dụ ắc quy yếu: ba luật SF02, SF03, SF14 cho 0.765, 0.675 và 0.54, gộp lại được 0.96. Lỗi có CF từ 0.2 trở lên mới được báo, xếp từ cao xuống thấp.

## Slide 4. Kiểm chứng bằng thuật toán Wang (khoảng 55 giây)

Bộ suy diễn là code nhóm tự viết nên có thể sai. Để kiểm tra, em dùng thuật toán Wang, một bộ chứng minh định lý logic mệnh đề độc lập. Mỗi luật thành một công thức kéo theo, triệu chứng là nguyên tử, và Wang chứng minh sequent luật, triệu chứng suy ra lỗi bằng cách bỏ dần từng phép nối theo bảng bên trái, tới khi mỗi nhánh có cùng một nguyên tử ở hai bên. Vì forward chaining đúng và đủ với Horn clause, tập lỗi nó suy ra phải trùng với tập lỗi Wang chứng minh được. Em so sánh trên 30 kịch bản và 500 bộ triệu chứng ngẫu nhiên, hơn hai mươi mốt nghìn lần, không có khác biệt nào.

## Slide 5. Kết quả trên 30 kịch bản (khoảng 50 giây)

Mỗi nhóm hệ thống có 10 kịch bản do người không viết luật soạn, để không tự chấm bài mình. Forward chaining đúng lỗi hạng 1 ở 29 trên 30 kịch bản. Kịch bản sai duy nhất là BT10, giảm xóc sau yếu: Wang cũng không chứng minh được, nghĩa là cơ sở tri thức thiếu luật chứ bộ suy diễn không sai. Khi phân tích, em thấy các lỗi kiểu này cùng một dạng: suy ra được kết luận trung gian nhưng thiếu một triệu chứng phụ để đi tới lỗi. Nhóm sửa bằng các luật dự phòng có CF thấp hơn, ví dụ SF14 của Lâm và EN17, EN18, TR12 của em.

## Slide 6. Màn hình Theo triệu chứng (khoảng 50 giây)

Cuối cùng là màn hình Theo triệu chứng trong chương trình. Bên trái người lái chọn loại xe và tích các triệu chứng, gom theo bộ phận và tìm được không cần gõ dấu. Bấm Chẩn đoán thì bên phải hiện các thẻ kết quả xếp theo độ tin cậy: tên lỗi, thanh CF, tự xử lý được hay cần mang ra thợ, và cách xử lý. Bấm vào một thẻ để xem vì sao ra kết quả này: từng triệu chứng, từng luật đã chạy kèm CF; mỗi thẻ còn cho biết Wang có chứng minh được lỗi đó không. Phần của em đến đây là hết, em xin chuyển lời cho bạn Khoa.

## Câu hỏi vấn đáp có thể gặp

**Forward chaining khác backward chaining thế nào? Khi nào dùng cái nào?**
Forward đi từ dữ liệu: người lái khai hết triệu chứng rồi chương trình suy ra mọi thứ có thể. Backward đi từ giả thuyết: chọn một lỗi rồi hỏi các câu cần để chứng minh nó. Forward nhanh khi người lái biết rõ triệu chứng; backward hợp khi người lái không biết nên khai gì, vì chương trình hỏi từng câu. Trên 30 kịch bản, hai bên cho cùng kết quả.

**Vì sao thời gian chạy tuyến tính?**
Mỗi ký hiệu chỉ được lấy ra khỏi hàng đợi một lần, và mỗi lần chỉ giảm bộ đếm của các luật dùng nó. Tổng số lần giảm bằng tổng số điều kiện của mọi luật.

**CF có phải xác suất không?**
Không. CF là mức tin của người viết luật, lấy từ tài liệu và kinh nghiệm, chưa đo trên dữ liệu sửa xe thật. Nó dùng để xếp hạng, không nói "70% khả năng".

**Vì sao gộp nhiều luật bằng CF1 + CF2 × (1 − CF1)?**
Đây là công thức của MYCIN cho bằng chứng dương: mỗi luật thêm vào làm CF tăng nhưng không vượt quá 1, và thứ tự gộp không làm đổi kết quả. Nhược điểm: nó coi các luật là độc lập, trong khi SF02, SF03, SF14 cùng dùng "điện yếu".

**Vì sao cần Wang khi đã có unit test?**
Unit test chỉ kiểm tra những trường hợp mình nghĩ ra. Wang là bộ chứng minh độc lập với code suy diễn, nên có thể so trên hàng nghìn bộ triệu chứng ngẫu nhiên. Forward chaining đúng và đủ với Horn clause (AIMA chương 7), nên hai bên phải ra cùng tập lỗi; nếu khác là code suy diễn sai.

**Wang có chậm không?**
Về lý thuyết, mỗi luật bên trái tách 2 nhánh nên có thể rất nhiều nhánh. Em chỉ đưa vào các luật liên quan tới lỗi cần chứng minh, và tách trước luật đã đủ điều kiện, nên nhánh đầu đóng ngay. Ví dụ ắc quy yếu chỉ mất 9 sequent; 21.200 lần so sánh chạy trong vài giây.

**Wang có dùng CF không?**
Không. Wang chỉ trả lời "có suy ra được về mặt logic hay không". Vì vậy khi so sánh, forward chaining được chạy với ngưỡng 0 để lấy mọi lỗi suy ra được.

**Câu trả lời "không" được xử lý thế nào?**
Luật chỉ có VÀ, không có phủ định, nên "không" chỉ làm luật không chạy, không hạ CF của lỗi. Ví dụ ET05: người lái nói nước làm mát vẫn đủ, nhưng "thiếu nước làm mát" vẫn đứng thứ 2 với CF 0.45. Hướng phát triển: CF âm như MYCIN.

**Kịch bản sai BT10 là do đâu?**
Luật suy ra được "giảm xóc mất giảm chấn" nhưng mọi luật đi tiếp đều cần thêm một triệu chứng người lái không có. Wang cũng không chứng minh được, nên đây là thiếu luật, không phải lỗi bộ suy diễn. Cách sửa là luật dự phòng TS15, như SF14 đã sửa SE10.
