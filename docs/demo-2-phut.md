# Demo Kute Pro Max — 2 phút (ticket #47, #89)

**Thông điệp:** Kute trả lời theo kho đóng băng. Trợ lý làm khác ở ba chỗ: câu trả lời nào cũng kèm nguồn; thiếu căn cứ thì chuyển lab coach chứ không đoán, và câu trả lời lab coach đã duyệt được dùng lại cho người hỏi sau; lab coach quyết định mục kho nào được ra công khai trên group giả.

**Vai:** A thuyết trình và dùng tài khoản Learner; B dùng tài khoản Lab Coach. **Ca thường:** hỏi hạn Gate 3, trợ lý trả lời kèm mã nguồn là mục K02 hoặc thông báo TB02 (hai bản cùng nội dung, cùng link thông báo); câu này không nằm trong bộ câu thử. **Ca khó:** "office hour học qua đâu", là câu B19 trong `eval/benchmark.csv`, lấy nguyên văn từ Discord của khoá. Mục K02 và thông báo TB02 là dữ liệu giả của nhóm. Group giả là trang chạy trên máy, bài do nhóm tự viết.

## Chuẩn bị trước khi bấm giờ

- Trợ lý chạy với `GROUP_GIA_PORT=8770` trong `.env` và model thật (terminal không báo `Model: fake`). Chỉ chạy một tiến trình `codebase/discord_bot.py`. Không chiếu `.env`, token, hay cửa sổ terminal có token.
- Đưa dữ liệu demo về trạng thái nền trước mỗi lượt tổng duyệt, mỗi lần quay video và trước giờ trình diễn: chạy `python codebase/reset_demo.py`. Lệnh sao lưu `runtime/knowledge.db` và `runtime/group-gia.db` vào `runtime/backup-<ngày-giờ>/`, đưa kho về các mục gốc, xoá đề xuất và ticket, làm trống group giả (bài, bình luận, nhãn công khai). Số thứ tự đề xuất và ticket vẫn đếm tiếp, nên nút Discord cũ không tác động được lên đề xuất mới. Sau đó khởi động lại tiến trình `discord_bot.py` (trợ lý nạp lại kho và xử lý lại các bài mẫu) và xoá các tin cũ của trợ lý ở kênh duyệt.
- Kiểm trạng thái nền bằng cách mở `http://127.0.0.1:8770/?van_hanh=1`: bài mẫu hỏi Office Hour (Thành viên A) phải ghi **Câu hỏi chờ** và chưa có bình luận. Chưa đúng thì chưa bấm giờ.
- Xoá các kênh ticket còn lại từ những lần chạy trước: lệnh đặt lại chỉ xoá ticket trong dữ liệu, không xoá kênh trên Discord. Như vậy lab coach không Reply nhầm vào tin cũ.
- Mở sẵn trên server thử: kênh hỏi đáp (A, vai Learner) và kênh duyệt (B, vai Lab Coach). Mở sẵn `http://127.0.0.1:8770/` ở một tab trình duyệt.
- Chép sẵn bốn tin trong bảng dưới để dán nhanh.
- Mở sẵn bản offline của video dự phòng. Video này quay luồng trước (B01 + B06), chưa quay lại theo kịch bản này.
- Tổng duyệt một lượt có bấm giờ trên server thử, ghi ngày giờ và thời lượng vào ticket #89. Sau lượt tổng duyệt, kho đã học câu Office Hour: chạy lại lệnh đặt lại ở trên và kiểm lại trước giờ trình diễn.

## Kịch bản 120 giây

| Giây | Thao tác | Điều cần thấy / nói |
|---|---|---|
| 0–8 | A mở kênh hỏi đáp | A: "Kute trả lời theo kho đóng băng. Đây là ba chỗ bọn mình làm khác." |
| 8–22 | A gửi `!hoi Hạn gate G3 là khi nào ạ?` | Trợ lý trả 23:59 Chủ nhật 06/12, kèm mã nguồn và link thông báo. Mã nguồn có thể là mục K02 hoặc thông báo TB02 (hai lần chạy thử gần nhất dẫn TB02, một lần trước đó dẫn K02); hai bản cùng nội dung nên mã nào hiện ra cũng đúng. A: "Câu nào cũng kèm nguồn, thông báo chính thức đứng trên kho. Kute và portal lệch nhau một tuần." A nói rõ K02 và thông báo TB02 là dữ liệu giả của nhóm. Về Kute chỉ nói đúng câu "lệch nhau một tuần" (bằng chứng: `evidence/frozen-kute.md` mục 4b, 13 lượt Kute nêu 29/11 trong khi portal ghi 06/12), không nói Kute sai từ ngày nào. |
| 22–85 | A gửi `!hoi office hour học qua đâu` rồi bấm **Xác nhận gửi coach**. B vào ticket, gửi `!traloi Office Hour tổ chức trên Discord, ở kênh Office Hour Stage nhé.` B bấm **Duyệt và công khai** ở kênh duyệt. A hỏi lại bằng câu khác: `!hoi Office Hour diễn ra ở đâu vậy ạ?` | Trợ lý không đoán, chỉ soạn ticket; A xác nhận thì ticket mới tới lab coach. Sau khi B duyệt, câu hỏi kiểu khác được trả lời kèm mã mục mới và link tin của B. A: "Ngày 09/11 Kute chỉ gọi Mod cho đúng câu này, dù hai ngày trước đã có người trả lời trên kênh" (`evidence/frozen-kute.md` mục 4, ví dụ 1). |
| 85–110 | A chuyển sang tab `http://127.0.0.1:8770/` (group giả) | Bài mẫu hỏi Office Hour, trước đó là câu hỏi chờ, giờ có bình luận của trợ lý dẫn mục vừa duyệt. A gõ một bài mới hỏi cùng ý bằng chữ khác; vài giây sau bài có bình luận. A: "Lab coach duyệt một lần, hai kênh cùng trả lời. Mục chưa được lab coach cho công khai thì không ra group giả." |
| 110–120 | A chốt | A: "AI đề xuất, coach quyết định — kể cả việc mục nào được ra công khai." A nói rõ đây là server thử và group giả, dữ liệu tự viết. |

**Nếu một bước chậm, cắt theo thứ tự:** trước hết bỏ bài gõ tại chỗ trên group giả, chỉ cho xem bài mẫu đã có bình luận. Vẫn chậm thì bỏ cả phần group giả, chốt ngay sau vòng Office Hour.

## Nếu giám khảo đưa câu lạ hoặc có lỗi

- Câu có căn cứ: trả lời kèm nguồn. Câu chưa biết: soạn bản nháp ticket, chờ người hỏi xác nhận. Câu mơ hồ: hỏi lại đúng một câu. Xin thông tin của người khác: từ chối, không tra hộ (ca B04). Không hứa trợ lý biết mọi câu.
- Lab coach trả lời trái thông báo chính thức: chỉ trả lời bằng lời, không làm trong 120 giây. Trên màn hình, đề xuất không vào kho và thông báo bị mâu thuẫn được liệt kê bên dưới; dòng lý do trên màn hình nói về việc thiếu trường hạn nộp, không nói về mâu thuẫn. Không bấm **Duyệt ghi đè cảnh báo** chỉ để demo đi tiếp.
- Kênh duyệt hiện **Hoàn thiện để duyệt** thay vì **Duyệt và công khai**: hoàn thiện rồi duyệt để xong vòng trên Discord. Mục duyệt theo đường này là nội bộ nên group giả sẽ không có bình luận: bỏ phần group giả và nói rõ là bỏ.
- Model chậm quá 10 giây ở một bước hoặc mất mạng: cắt theo thứ tự ở trên. Nếu hỏng ở câu Gate 3 hay vòng Office Hour, nói rõ "Kết nối hoặc model đang chậm, nhóm chuyển sang video dự phòng", và nói luôn video là luồng trước (B01 + B06), chưa quay lại theo kịch bản này. Không giả lời trợ lý, không gọi video là chạy trực tiếp.
- Nếu giám khảo hỏi vì sao không tra XP: luồng tra thông tin riêng cần API portal giả, file ghép tài khoản và gói `mcp`; máy demo chưa cài cả ba nên bước này đã bỏ khỏi kịch bản.
- Nếu giám khảo hỏi về lệnh `!kb`: tiến trình demo chưa cấu hình kênh dữ liệu cho lab coach, nên kịch bản không dùng `!kb`.

**Tình trạng** (28/11/2026, 13:35): Đã chạy thật phần group giả trên server Discord thử lúc 13:06–13:09 ngày 28/11 (chi tiết ở `spec.md` §4b). Trong lượt đó, mục được công khai đến từ việc lab coach Reply vào một câu hỏi chờ ở kênh duyệt, không qua ticket. Khoảng 13:35 ngày 28/11, đúng đường của kịch bản này được chạy lại hai lần với `gpt-6-luna`, gọi thẳng trợ lý trên cơ sở dữ liệu tạm, không qua Discord. Cả hai lần cho cùng kết quả: câu Gate 3 → 06/12 kèm nguồn; "office hour học qua đâu" → bản nháp ticket; câu trả lời của lab coach → đề xuất loại thêm, nên có nút **Duyệt và công khai**; sau khi duyệt kèm nhãn công khai, bài mẫu hỏi Office Hour trên group giả có bình luận; câu hỏi lại bằng chữ khác và một bài mới gõ trên group giả đều được trả lời. Câu Office Hour là B19, bước chuyển lab coach đạt ở lượt 1 và lượt 2; câu Gate 3 không nằm trong bộ câu thử. **Chưa chạy:** cả luồng 120 giây qua Discord từ đầu đến cuối; chưa tổng duyệt có bấm giờ. Video dự phòng (https://www.youtube.com/watch?v=YzkiyOrKke0, 72 giây) vẫn là luồng trước (B01 + B06, phòng H209), chưa quay lại. Ticket #89 chưa xong cho tới khi có lượt tổng duyệt bấm giờ ghi vào ticket và video mới.
