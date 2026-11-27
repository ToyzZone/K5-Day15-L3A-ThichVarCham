# Khai báo dùng AI

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Codex | Hỗ trợ viết/sửa bot Discord, ticket, SQLite, bảng kiến thức, API portal giả và MCP | Người vận hành chạy trên Discord, cung cấp lỗi thực tế và yêu cầu sửa; chưa có bằng chứng kiểm độc lập toàn bộ hệ thống | Hoàng |
| Prompt / thiết kế lời gọi mô hình | Codex; model runtime theo `.env` | Codex hỗ trợ luồng công cụ, thứ tự nguồn và phân loại đề xuất; model runtime trả lời/soạn đề xuất. Lượt eval hiện có ghi `gpt-6-luna` | Người quyết định coach có quyền duyệt cuối; cảnh báo không được tự ngăn duyệt, câu trả lời ngắn cần hiểu theo câu hỏi gốc | Hoàng |
| Đào data (viết script đếm, gợi ý nhãn) | Chưa đủ thông tin để khai tên công cụ | Chưa xác nhận lịch sử AI hỗ trợ phần này | Đối chiếu script và nguồn ở `evidence/data-mining.md`; chưa khai số kiểm tay khi chưa có bằng chứng | Thành viên phụ trách cần bổ sung |
| Rà câu hỏi phỏng vấn / khảo sát | Codex | Hỗ trợ chuẩn bị câu hỏi P2/P3 và ghi chép từ câu trả lời người phỏng vấn gửi | Người cung cấp lời kể thực tế. Không suy ra P3 đã tạo ticket hay đã nhận phản hồi BTC | Hoàng |
| Viết câu thử (benchmark) | Chưa xác nhận mức tham gia của AI | Chưa đủ lịch sử để quy toàn bộ bộ câu hỏi cho người hoặc AI | Giữ `source`, `expected` và metric đã khóa; cần đối chiếu nguồn từng câu và khai phần AI viết nếu có | Thành viên làm benchmark cần xác nhận |
| Sinh data `synthetic` (nếu có) | Codex hỗ trợ phần portal giả/API | Hỗ trợ triển khai việc sử dụng hồ sơ mẫu trong `data/portal_gia.json`; chưa xác nhận nguồn tạo mọi bản ghi mẫu trong repo | Người yêu cầu chỉ dùng dữ liệu giả, không nối portal thật; chưa có số kiểm tay hoặc seed đã xác nhận để công bố | Thông + Hoàng |
| Chấm cột `pass` bằng LLM (nếu có) | Codex | Đối chiếu output, trace và metric, điền `pass`/`ghi_chu` B01–B15 của `run-1@20261127-222949` theo yêu cầu | AI hỗ trợ chấm 15 câu: 14 đạt, B13 trượt do `them` thay vì `sua`; chưa ghi nhận số câu được người kiểm độc lập, B16–B30 còn chưa chấm | Người chấm của nhóm cần duyệt; chưa tuyên bố kiểm tay khớp 15/15 |
| Slide, văn bản | Codex | Hỗ trợ kịch bản demo, tài liệu chạy, README, ghi chép phỏng vấn và bản nháp reflection | Người đọc lại, bổ sung thông tin còn thiếu và xác nhận nhận xét cá nhân; chưa có PDF slide hoặc link video trong repo khi cập nhật | Tác giả/người trình bày cần xác nhận phần của mình |

**Không dùng AI để:** tạo người được phỏng vấn, trích dẫn, câu trả lời khảo sát hoặc số liệu chưa có nguồn; sửa output, token, error, run ID hay trace của các lượt đã chạy. Ngoại lệ được phép là điền `pass` và `ghi_chu` theo chuẩn đã khóa, có khai báo AI hỗ trợ như bảng trên.

## Phần người quyết định

- Phạm vi sản phẩm, cấu hình triển khai và yêu cầu hành vi do người vận hành quyết định. Các thay đổi đã được yêu cầu từ chạy thử gồm nhận đúng reply coach, tránh học chat thường và cho phép coach duyệt cảnh báo.
- Learner xác nhận bản nháp trước khi gửi ticket; Lab Coach duyệt hoặc bỏ qua đề xuất trước khi đưa vào kho. Model không tự phê duyệt kiến thức.
- Người phỏng vấn cung cấp lời kể, thông tin làm rõ và xác nhận tính đúng của ghi chép. Phần chưa hỏi/chưa trả lời được ghi thiếu, không tự điền.
- Nhóm chịu trách nhiệm duyệt cách chấm eval, kết luận hiệu quả, số liệu chi phí và nội dung nộp. Kết quả AI hỗ trợ chấm chưa đồng nghĩa đã được người kiểm độc lập.

## Ví dụ đã phải sửa sau chạy thử

Người vận hành báo bot tạo đề xuất từ chat thường trong ticket, bỏ qua câu trả lời ngắn như “phòng H209”, hoặc không dùng kiến thức vừa duyệt khi hỏi lại. Codex hỗ trợ sửa sau phản hồi thực tế; các lỗi này cho thấy đầu ra code/prompt AI cần được chạy thử và rà lại.

Trong eval, B13 vẫn trượt vì loại đề xuất không đúng hợp đồng dù có nguồn và chờ duyệt. Không sửa `expected` hoặc output cũ để biến câu này thành đạt. Xem [kết quả hiện có](../eval/run-1.csv) và [README](../README.md).

## Cần bổ sung trước khi nộp

Xác nhận tên người phụ trách từng phần, nguồn tạo benchmark/dữ liệu mẫu, số câu người đã kiểm độc lập và các hoạt động AI của thành viên khác chưa được ghi nhận ở đây. Không tự khai hoạt động chưa có bằng chứng.
