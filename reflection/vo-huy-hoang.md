# Reflection — Võ Huy Hoàng

1. Vai trò + phần mình làm (trỏ tới file / commit):

   Tôi tham gia triển khai và chạy thử luồng hỏi đáp của Kute Pro Max trên server Discord thử nghiệm.
   Tôi cấu hình role/kênh, thao tác bằng tài khoản learner và coach để phát hiện lỗi ở luồng trả lời, ticket và duyệt kiến thức; phần code được Codex hỗ trợ viết trong [`discord_bot.py`](../codebase/discord_bot.py), [`tickets.py`](../codebase/tickets.py) và [`knowledge_store.py`](../codebase/knowledge_store.py).
   Tôi tiếp tục làm phần API portal giả và kết nối MCP, tham chiếu [`portal_api.py`](../codebase/portal_api.py), [`portal_mcp_client.py`](../codebase/portal_mcp_client.py) và [`portal_mcp_server.py`](../codebase/portal_mcp_server.py); không nối portal thật của khóa.
   Tôi cũng thực hiện phỏng vấn P2 và P3, bổ sung hồ sơ [`P2.md`](../evidence/interviews/P2.md), [`P3.md`](../evidence/interviews/P3.md), và nhờ Codex hỗ trợ đối chiếu, điền kết quả B01–B15 trong [`run-1.csv`](../eval/run-1.csv).

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):

   Tôi dùng Codex để đọc spec/issue, viết code kết nối Discord, lưu kiến thức bằng SQLite và nối portal giả qua MCP/API; AI cũng hỗ trợ soạn tài liệu thao tác và bộ câu hỏi phỏng vấn.
   Tôi chạy bot trên Discord và gửi lại hành vi thực tế để sửa: coach chat thường cũng tạo đề xuất, câu trả lời ngắn như tên phòng bị bỏ qua, và kiến thức đã duyệt chưa được dùng khi hỏi lại.
   Những lần đó cho thấy code hoặc prompt AI tạo ra vẫn cần được đối chiếu với hành vi người dùng và hợp đồng dữ liệu; thay vì chấp nhận ngay, tôi yêu cầu sửa điều kiện nhận câu trả lời và luồng duyệt.
   Với phỏng vấn, tôi cung cấp hội thoại và thông tin làm rõ; AI chỉ hỗ trợ ghi chép, không tự tạo lời người tham gia hoặc số liệu chưa thu thập.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:

   Trong lượt `run-1@20261127-222949`, câu B13 yêu cầu đề xuất `sua` cho mục K03 về nơi nộp daily standup, nhưng output trả `them`, dù vẫn trỏ K03, có nguồn và chờ duyệt.
   Theo tiêu chí đã chốt, câu này phải được chấm 0; kết quả B01–B15 là 14 câu đạt và B13 trượt. Nguồn đối chiếu: [`benchmark.csv`](../eval/benchmark.csv), [`run-1.csv`](../eval/run-1.csv) và [`metric_spec.yaml`](../eval/metric_spec.yaml).
   Bài học đề xuất của tôi là cần phân biệt thao tác lưu một bản ghi theo khóa mới với ý nghĩa nghiệp vụ sửa kiến thức cũ: có thể không sửa bảng cố định nhưng loại đề xuất vẫn phải khớp hợp đồng `sua`.
   Cách cải tiến cần nhắm vào cách phân loại hoặc chuẩn hóa đầu ra ở lượt sau; giữ nguyên output và tiêu chí của lượt đã chạy để đánh giá trung thực. [Người viết xác nhận hoặc sửa nhận xét này theo điều mình thực sự rút ra.]
