# Demo Kute Pro Max — 2 phút (issue #47)

**Thông điệp:** câu trả lời của coach được lưu thành kiến thức có nguồn, sau khi người duyệt đồng ý. **Vai:** A thuyết trình và dùng tài khoản Learner; B dùng tài khoản Lab Coach. **Ca thường:** B01; **ca khó:** B06 trong `eval/benchmark.csv`. Phòng H209 dưới đây là **dữ liệu giả minh họa**, không phải lịch thật.

## Chuẩn bị trước khi bấm giờ

- Mở sẵn kênh hỏi đáp, kênh duyệt và kênh dữ liệu trên server thử; A/B có đúng role. Chỉ một tiến trình bot chạy, model thật được cấu hình, không chiếu `.env` hoặc token.
- Coach kiểm tra `!kb xem K04` để bảo đảm có kiến thức cách tính XP; `!kb tim Demo Day` để bảo đảm câu hỏi phòng chưa có đáp án hiệu lực. Nếu đã học từ lần trước, dùng môi trường demo riêng với kho nền ban đầu; không xóa database đang dùng, không sửa benchmark.
- Chuẩn bị sẵn ba tin bên dưới để dán nhanh. Không duyệt phòng minh họa trên server thật. Kho nền có link nguồn mô phỏng; nguồn tin coach trong demo mới là link Discord trên server thử.
- Quay video dự phòng theo đúng kịch bản, lưu bản mở offline. Chạy thử một lượt có bấm giờ trước khi trình diễn.

## Kịch bản 120 giây

| Giây | Ai, thao tác | Lời nói / kết quả cần thấy |
|---|---|---|
| 0–10 | A giới thiệu, mở kênh hỏi đáp | “Bot trả lời từ kho đã duyệt. Khi chưa biết, bot nhờ coach; câu trả lời mới chỉ được học sau khi duyệt.” |
| 10–25 | A gửi `!hoi XP được tính thế nào ạ?` — **B01** | Bot trả cách tính XP, có mã/nguồn K04. A: “Thông tin có sẵn thì học viên nhận ngay câu trả lời kèm nguồn.” |
| 25–45 | A gửi `!hoi Demo Day tổ chức ở phòng nào vậy ạ?` — **B06**; bấm **Xác nhận gửi coach** | Trước khi xác nhận chỉ có bản nháp; sau xác nhận có ticket riêng và báo coach. A: “Không có căn cứ thì bot không đoán phòng; người hỏi quyết định gửi ticket.” |
| 45–65 | B vào ticket, gửi `!traloi Trong môi trường demo giả này, Demo Day tổ chức tại phòng H209.` | Bot tạo đề xuất trong kênh duyệt. B: “Tôi chủ động gửi câu trả lời; chat thường không trở thành kiến thức.” |
| 65–85 | B mở đề xuất, đọc câu hỏi–trả lời–nguồn rồi bấm **Duyệt** | B: “Chưa duyệt thì chưa dùng. Tôi chịu trách nhiệm cho thông tin đưa vào kho.” Nếu cần hoàn thiện bản nháp, ghi câu trả lời rõ là dữ liệu demo rồi duyệt. |
| 85–105 | A hỏi lại nguyên câu B06 ở kênh hỏi đáp; mở nguồn Discord của câu trả lời | Bot trả phòng H209, có mã mục mới và link tin coach. A: “Người hỏi sau đã nhận được kiến thức vừa duyệt, không cần coach trả lời lại.” |
| 105–120 | A chỉ bảng kiến thức cập nhật hoặc nguồn tin | “AI đề xuất, coach quyết định. Đây là server và dữ liệu thử; kết quả demo minh họa một vòng xử lý, không thay thế kết quả đánh giá toàn bộ bộ câu hỏi.” |

## Nếu giám khảo đưa câu lạ hoặc có lỗi

- Câu có căn cứ: trả lời kèm nguồn; câu chưa biết: xác nhận ticket; câu mơ hồ: hỏi lại. Không hứa bot biết mọi câu.
- Xin thông tin của người khác: phải từ chối, không tra hộ. Ca tham chiếu B04; không thêm vào 120 giây nếu chưa có thời gian.
- Model chậm quá 10 giây ở một bước hoặc mất mạng: nói rõ “Kết nối/model đang chậm, nhóm chuyển sang video dự phòng của cùng luồng.” Không giả lời bot hoặc gọi video là chạy trực tiếp.
- Cảnh báo mâu thuẫn: đọc nguồn trước. Chỉ coach duyệt ghi đè khi có căn cứ; không bấm chỉ để ép demo đi tiếp.
- Không đưa luồng XP cá nhân vào demo chính lúc này: đã có API/MCP nhưng lượt hỏi Discord gần nhất vẫn chuyển ticket, cần xử lý riêng trước khi trình bày thành tính năng đã chạy đúng.

**Tình trạng:** đã đối chiếu kịch bản với code và ca B01/B06; **chưa xác nhận tổng duyệt có bấm giờ trên server của phiên bản hiện tại**. Sau khi làm thật, ghi ngày giờ, người đảm nhiệm A/B, thời lượng thực tế và link video vào issue #47. Không đánh dấu issue xong trước bước đó.
