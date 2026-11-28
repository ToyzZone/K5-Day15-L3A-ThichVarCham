# Khai báo dùng AI

> Luật của đề: dùng AI để làm bài thoải mái, nhưng **ai không giải thích được phần có tên mình thì phần đó nhận 0 điểm**. Khai thiếu không bị trừ; giấu mới bị.

| Việc | Công cụ AI | AI làm gì | Người kiểm/sửa gì | Ai phụ trách |
|---|---|---|---|---|
| Code bản chạy thử | Codex · Claude Code | Codex hỗ trợ viết/sửa bot Discord, ticket, SQLite, bảng kiến thức, API portal giả và MCP. Claude Code soạn nháp code lõi (`spec.md` §10) và sửa chốt chặn con số ngày 28/11 | Người vận hành chạy trên Discord, cung cấp lỗi thực tế và yêu cầu sửa; chưa có bằng chứng kiểm độc lập toàn bộ hệ thống. Phần Claude Code: test `unittest` chạy trước và sau khi sửa chốt chặn (PR #83) | Hoàng · Thông |
| Prompt / thiết kế lời gọi mô hình | Codex; model runtime theo `.env` | Codex hỗ trợ luồng công cụ, thứ tự nguồn và phân loại đề xuất; model runtime trả lời/soạn đề xuất. Lượt eval hiện có ghi `gpt-6-luna` | Người quyết định coach có quyền duyệt cuối; cảnh báo không được tự ngăn duyệt, câu trả lời ngắn cần hiểu theo câu hỏi gốc | Hoàng |
| Đào data (viết script đếm, gợi ý nhãn) | Claude Code (tên công cụ ghi ở `evidence/frozen-kute.md`) | Đọc và gán nhãn: chia 282 lượt theo điều học viên cần (`evidence/data-mining.md` mục 3e), phân loại câu trả lời của Kute (`evidence/frozen-kute.md`), kiểm chéo 30 lượt, trùng 27/30 (`evidence/summary.md`) | Chưa có người chấm lại nhãn AI gán. Một người đã chấm đúng sai 249/478 câu trả lời của Kute theo luật ở `evidence/data-mining.md` mục 3g, nhưng chưa so với nhãn AI. Số ghi "script" ở `evidence/frozen-kute.md` chạy lại được bằng công thức ở mục 3 của file đó | Thông |
| Đối chiếu nhãn người chấm (lô 1) | Claude Code | Chấm mù 249 câu trả lời của Kute theo luật `evidence/data-mining.md` mục 3g, chỉ dựa vào thông báo và diễn đàn đăng trước giờ hỏi; trùng với người chấm 72/249 (kappa 0,12) | Nhãn AI không dùng làm kết quả. 14 câu AI chỉ ra căn cứ được người chấm lô 1 xem lại và đổi; 7/14 câu đã được đọc lại đối chiếu với nguồn | Thông + Hạnh |
| Rà câu hỏi phỏng vấn / khảo sát | Codex | Hỗ trợ chuẩn bị câu hỏi P2/P3 và ghi chép từ câu trả lời người phỏng vấn gửi | Người cung cấp lời kể thực tế. Không suy ra P3 đã tạo ticket hay đã nhận phản hồi BTC | Hoàng |
| Viết câu thử (benchmark) | Claude Code | Soạn nháp bộ câu thử (`spec.md` §10) | Đội trưởng chốt 30 câu ở ticket bộ câu thử. Cột `source` ghi 15 câu `data_that` trích nguyên văn từ Discord và 15 câu `tu_viet`. B14–B30 thêm tối 27/11, trước lượt chạy model thật đầu tiên; B01–B13 và metric không sửa | Thông |
| Sinh data `synthetic` (nếu có) | Claude Code · Codex | Claude Code soạn nháp dữ liệu giả trong `data/` (`spec.md` §10, `data/DATA_CARD.md`). Codex hỗ trợ API portal giả đọc `data/portal_gia.json` | Viết tay bằng script một lần, không sinh ngẫu nhiên nên không có seed; chưa có người thứ hai kiểm từng dòng (`data/DATA_CARD.md`). Chỉ dùng dữ liệu giả, không nối portal thật | Thông + Hoàng |
| Chấm cột `pass` bằng LLM (nếu có) | Codex | Đối chiếu output, trace và metric, điền `pass`/`ghi_chu` B01–B15 của `run-1@20261127-222949` theo yêu cầu | AI hỗ trợ chấm 15 câu: 14 đạt, B13 trượt do `them` thay vì `sua`. B16–B30 đã chấm ở ticket #27. Người thứ hai chấm lại 5 câu của lượt 1: trùng 4/5, lệch ở B13 (`eval/README.md`) | Người chấm của nhóm cần duyệt; chưa tuyên bố kiểm tay khớp 15/15 |
| Slide, văn bản | Codex · Claude Code | Codex hỗ trợ kịch bản demo, tài liệu chạy, README, ghi chép phỏng vấn và bản nháp reflection. Claude Code soạn nháp spec (`spec.md` §10) và cập nhật README ngày 28/11 | Người đọc lại, bổ sung thông tin còn thiếu và xác nhận nhận xét cá nhân. `demo-slides.pdf` và link hai video đã có ở README | Tác giả/người trình bày cần xác nhận phần của mình |

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

Ba điều chưa có ai khai, người làm phần đó cần điền:

- `evidence/count.py` có AI viết hay không.
- AI hỗ trợ tới đâu khi chấm B16–B30 của lượt 1 và khi chấm lượt 2.
- Slide (`demo-slides.pdf`, `slides/demo.html`) làm với công cụ AI nào.

Không tự khai hoạt động chưa có bằng chứng.
