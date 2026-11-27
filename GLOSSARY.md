# Trợ lý Discord khoá AI20K

Ngôn ngữ chung của nhóm Thích Var Chạm cho bài hackathon Track A · A2: một trợ lý trên Discord trả lời câu hỏi của học viên và học thêm từ câu trả lời của lab coach.

## Language

**Lab coach**:
Người có vai trò chính thức trong khoá, trả lời câu hỏi của học viên trên Discord và chịu trách nhiệm về những gì mình đã duyệt.
_Avoid_: admin, mod, TA (khi nói về người duyệt)

**Kho kiến thức**:
Tập các mục đã được lab coach duyệt mà trợ lý được phép dùng để trả lời câu hỏi chung của học viên.
_Avoid_: knowledge base, KB, FAQ

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
