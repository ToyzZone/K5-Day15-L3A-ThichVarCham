# Kute Pro Max — trợ lý Discord khoá AI20K

Ngôn ngữ chung của nhóm Thích Var Chạm cho bài hackathon Track A · A2: một trợ lý trên Discord trả lời câu hỏi của học viên và học thêm từ câu trả lời của lab coach.

## Language

**Kute Pro Max**:
Tên sản phẩm của nhóm: trợ lý trên Discord trả lời câu hỏi của học viên và soạn đề xuất cập nhật. Trong tài liệu gọi tắt là "trợ lý".
_Avoid_: bot (dễ lẫn với Kute), chatbot, Kute (khi nói về sản phẩm của nhóm)

**Kute**:
Bot đang chạy trên Discord của chương trình; có kho kiến thức đóng băng và chỉ tạo, xoá được ticket. Không phải sản phẩm của nhóm.
_Avoid_: bot của khoá, trợ lý, Kute Pro Max

**Lab coach**:
Người có vai trò chính thức trong khoá, trả lời câu hỏi của học viên trên Discord và chịu trách nhiệm về những gì mình đã duyệt.
_Avoid_: admin, mod, TA (khi nói về người duyệt)

**Ticket**:
Kênh riêng trên Discord giữa một học viên và các lab coach cho một câu hỏi; là cách trợ lý chuyển câu hỏi cho lab coach.
_Avoid_: ca chuyển, escalation, tag coach

**Kho kiến thức**:
Tập các mục đã được lab coach duyệt mà trợ lý được phép dùng để trả lời câu hỏi chung của học viên.
_Avoid_: knowledge base, KB, FAQ

**Bảng cố định**:
Phần kho kiến thức giữ thông tin không đổi qua các khoá; lab coach không sửa được.
_Avoid_: persistent, bảng gốc, KB chính

**Bảng theo khoá**:
Phần kho kiến thức giữ thông tin riêng của khoá đang chạy; mọi đề xuất cập nhật được duyệt đều vào đây, và nó thắng bảng cố định khi hai bên mâu thuẫn.
_Avoid_: tentative, bảng tạm

**Ghi đè**:
Quan hệ giữa một mục theo khoá và mục cố định mà nó thay thế trong khoá đang chạy; mục cố định vẫn còn nguyên.
_Avoid_: sửa mục cố định, override

**Mục kho**:
Một câu hỏi kèm câu trả lời trong kho kiến thức, luôn đi cùng nguồn gốc và người đã duyệt.
_Avoid_: bài viết, entry

**Đề xuất cập nhật**:
Bản nháp mục kho được soạn từ một câu trả lời của lab coach, chưa có hiệu lực cho tới khi lab coach duyệt.
_Avoid_: cập nhật tự động

**Duyệt**:
Hành động của lab coach xác nhận một đề xuất cập nhật là đúng; từ lúc đó lab coach chịu trách nhiệm về nội dung mục kho.
_Avoid_: verify, approve

**Thông báo chính thức**:
Tin do ban đào tạo hoặc lab coach đăng ở kênh thông báo của khoá; khi mâu thuẫn với một mục kho thì thông báo luôn thắng.
_Avoid_: announcement, tin ghim

**Tạm ngưng**:
Trạng thái của một mục kho đã duyệt nhưng đang mâu thuẫn với thông báo chính thức; trợ lý không dùng mục đó cho tới khi lab coach duyệt lại.
_Avoid_: xoá, gỡ

**Lỗi thời**:
Trạng thái lab coach gắn cho một mục kho không còn đúng; trợ lý không dùng mục đó nữa.
_Avoid_: hết hạn, cũ

**Thông tin riêng**:
Dữ liệu của một học viên cụ thể (lịch, nhóm, điểm, điểm danh…), chỉ chính học viên đó được xem.
_Avoid_: thông tin cá nhân hoá, data user

**Portal giả**:
Trang web nhóm tự dựng bằng dữ liệu giả, mô phỏng portal của khoá, là nơi duy nhất trợ lý tra thông tin riêng.
_Avoid_: portal (khi không nói rõ thật hay giả), trang web
