# Tổng hợp bằng chứng pain

## 1. Nguồn đã dùng

Nguồn chính là dữ liệu Discord từ 05–27/11/2026. Nhóm đếm 848 lượt Kute trả lời học viên từ 1.848 tin trên kênh hỏi trợ lý và tạo ticket. Mục 1 ghi luật đếm và lệnh chạy lại với dữ liệu gốc lưu riêng. Nhóm đối chiếu một số lượt với thông báo, diễn đàn và các lượt trả lời trước đó. Ba cuộc phỏng vấn học viên P1–P3 bổ sung góc nhìn về cách họ tìm sự trợ giúp sau khi hỏi Kute. [Đào dữ liệu](data-mining.md) · [Phân tích câu trả lời của Kute](frozen-kute.md)

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

## 4. Phỏng vấn học viên

| Người tham gia | Lần gần nhất hỏi Kute và bước tiếp theo | Tần suất tự báo cáo | Thời gian được kể |
|---|---|---|---|
| [P1](interviews/P1.md) | Hỏi nơi công bố điểm lab. Kute nhờ Mod hỗ trợ. P1 hỏi lab coach và nhận câu trả lời từ coach. | 1 lần tương tự trong tháng | 20 phút tổng cộng để tự tìm và chờ. Chưa tách được từng phần. |
| [P2](https://github.com/ToyzZone/K5-Day15-L3A-ThichVarCham/blob/60d2754/evidence/interviews/P2.md) | Hỏi về hạn nộp lab khi LMS lỗi. Kute chưa đáp ứng nhu cầu nên P2 hỏi lab coach. Chưa biết kết quả cuối. | 3 lần hỏi Kute, 2 lần cần hỏi lại | P2 kể lần đó mất 20 phút. Chưa rõ cách xác định và mốc kết thúc. |
| [P3](https://github.com/ToyzZone/K5-Day15-L3A-ThichVarCham/blob/60d2754/evidence/interviews/P3.md) | Hỏi về việc xin nghỉ và tham gia từ xa. P3 thấy Kute trả lời khá đầy đủ nhưng vẫn cần BTC xác nhận. Chưa biết P3 có mở ticket hay nhận phản hồi sau đó. | 1 lần hỏi Kute, lần đó cần BTC xác nhận | Khoảng 5 phút gồm chờ và đọc câu trả lời. Chưa biết thời gian đến khi có xác nhận cuối. |

Trong cả ba ca, học viên đã hỏi người hỗ trợ tiếp hoặc vẫn cần người xác nhận. P3 đánh giá câu trả lời của Kute khá đầy đủ, cho thấy nhu cầu gặp người còn có thể đến từ việc cần xác nhận chính sách. Các mốc 20, 20 và khoảng 5 phút đo những phần khác nhau của quá trình, nên chưa dùng để tính thời gian chờ trung bình hay số phút có thể tiết kiệm.

## 5. Đối chiếu và giới hạn

Phép đếm cho thấy học viên thường phải tìm đến người hỗ trợ. Đối chiếu theo từng tin cho thấy có ít nhất 6 lượt thuộc 5 chủ đề mà Kute không trả lời được dù đã có người trả lời trước đó trên kênh hoặc diễn đàn. Một số lượt khác nhận hướng dẫn lạc đề hoặc đã cũ. Các ví dụ được tìm có chủ đích và do AI đọc, nên chưa dùng để ước lượng tỉ lệ câu sai của toàn bộ tập. [Phân tích câu trả lời của Kute, mục 2 và 6](frozen-kute.md)

Dữ liệu chỉ bao phủ một kênh hỏi trợ lý. Nhóm chưa quan sát được kết quả trong ticket riêng và chưa biết vì sao từng học viên chủ động xin ticket. Các cuộc phỏng vấn dựa trên lời kể của ba người. Chỉ P1 xác nhận đã nhận câu trả lời cuối từ lab coach. Kết quả chấm độc lập của nhóm ở mục 3g vẫn đang chờ. [Đào dữ liệu, mục 3g và 5](data-mining.md)

## 6. Kết luận

**Phải đổi giả thuyết làm việc.** [File giả thuyết](hypothesis.md) còn trống, nên nhóm dựa vào hướng ban đầu ghi trong [issue về bằng chứng](https://github.com/ToyzZone/K5-Day15-L3A-ThichVarCham/issues/14). Dữ liệu cho thấy có lúc lời giải đã xuất hiện trên kênh hoặc diễn đàn nhưng Kute vẫn chưa trả lời được. Phỏng vấn bổ sung hai tình huống học viên phải hỏi coach và một tình huống cần BTC xác nhận. Nhóm chuyển trọng tâm sang việc học viên nhận câu trả lời có căn cứ hoặc được chuyển đến người hỗ trợ. Cần ghi riêng thời gian tự tìm, thời gian chờ và mốc giải quyết xong trước khi ước tính lợi ích thời gian.
