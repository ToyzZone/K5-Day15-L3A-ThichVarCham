# Tổng hợp bằng chứng pain

## 1. Nguồn đã dùng

Nguồn chính là [dữ liệu Discord](data-mining.md) từ 05–27/11/2026. Nhóm đếm 848 lượt Kute trả lời học viên từ 1.848 tin trên kênh hỏi trợ lý và tạo ticket. Mục 1 ghi luật đếm và lệnh chạy lại với dữ liệu gốc lưu riêng. Nhóm đối chiếu một số lượt với thông báo, diễn đàn và các lượt trả lời trước đó trong [phân tích câu trả lời của Kute](frozen-kute.md). Chưa có kết quả phỏng vấn hoặc khảo sát trong repo.

## 2. Số chính

| Quan sát | Kết quả | Nguồn |
|---|---|---|
| Học viên chủ động xin ticket | 170/848 (20%) | [Đào dữ liệu, mục 3b](data-mining.md) |
| Kute chỉ gọi Mod | 43/848 (5%) | [Đào dữ liệu, mục 3c](data-mining.md) |
| Kute trả lời rồi vẫn nhắc Mod | 69/848 (8%) | [Đào dữ liệu, mục 3c](data-mining.md) |
| Kute không trả lời được dù học viên không xin ticket | 52/848 (6%), gồm 43 lượt chỉ gọi Mod, 8 lượt timeout và 1 lượt chỉ đưa khung ticket | [Đào dữ liệu, mục 3c](data-mining.md) |
| Trong 282 lượt xin ticket, chỉ gọi Mod hoặc trả lời rồi nhắc Mod, AI nhận diện câu hỏi kiến thức hoặc thông tin riêng | 93/282 (33%), gồm 90 câu hỏi kiến thức và 3 câu hỏi thông tin riêng | [Đào dữ liệu, mục 3e](data-mining.md) |

## 3. Ví dụ nguyên văn đã bỏ tên

| Mã tin | Học viên hỏi | Kute xử lý |
|---|---|---|
| 218300 | “bao giờ nộp được mentor duty, hiện tại trên phoenix tôi chưa thấy chỗ để nộp” | Gọi Mod. |
| 398147 | “office hour học qua đâu” | Chỉ gọi Mod. Kênh đã có câu trả lời về nơi tổ chức từ 07/11. |
| 404171 | “có quy định về URL Production không” | Chỉ gọi Mod. Diễn đàn đã có câu trả lời từ 20/11. |
| 221272 | “có còn đổi được đề tài nưa không” | Hướng dẫn đổi trong hạn, dù lượt hỏi ngày 19/11 diễn ra sau hạn 14/11. |
| 503667 | “tôi cần nộp lại bài lab day 09 vì nộp nhầm link” | Hướng dẫn nộp dự án Demo Day. |
| 470631 | “làm sao để biết mình được điểm danh buổi học hay chưa?” | Chỉ cách tự xem trên portal. |

Nguồn trích dẫn và đối chiếu ở mục 4 của [Đào dữ liệu](data-mining.md) và [Phân tích câu trả lời của Kute](frozen-kute.md).

## 4. Đối chiếu và giới hạn

Phép đếm cho thấy học viên thường phải tìm đến người hỗ trợ. Đối chiếu theo từng tin cho thấy có ít nhất 6 lượt thuộc 5 chủ đề mà Kute không trả lời được dù đã có người trả lời trước đó trên kênh hoặc diễn đàn. Một số lượt khác nhận hướng dẫn lạc đề hoặc đã cũ. Các ví dụ được tìm có chủ đích và do AI đọc, nên chưa dùng để ước lượng tỉ lệ câu sai của toàn bộ tập. [Phân tích câu trả lời của Kute, mục 2 và 6](frozen-kute.md)

Dữ liệu chỉ bao phủ một kênh hỏi trợ lý. Nhóm chưa quan sát được kết quả trong ticket riêng, chưa đo thời gian chờ và chưa biết vì sao từng học viên chủ động xin ticket. Kết quả chấm độc lập của nhóm ở mục 3g vẫn đang chờ. [Đào dữ liệu, mục 3g và 5](data-mining.md)

## 5. Kết luận

**Phải đổi giả thuyết làm việc.** [File giả thuyết](hypothesis.md) còn trống, nên nhóm dựa vào hướng ban đầu ghi trong [issue về bằng chứng](https://github.com/ToyzZone/K5-Day15-L3A-ThichVarCham/issues/14). Dữ liệu hiện có cho thấy học viên có lúc không nhận được câu trả lời dùng được từ Kute, kể cả khi lời giải đã xuất hiện trên kênh hoặc diễn đàn. Nhóm chuyển trọng tâm từ việc lab coach phải trả lời lặp sang việc học viên nhận câu trả lời có căn cứ hoặc được chuyển đến người hỗ trợ. Phỏng vấn học viên sẽ giúp kiểm tra lý do họ chọn ticket, cách họ tìm câu trả lời cuối cùng và thời gian chờ.
