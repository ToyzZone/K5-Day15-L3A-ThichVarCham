# Reflection — Nguyễn Tuấn Hiếu

## 1. Vai trò và phần việc

Mình phụ trách phần chấm B16–B30 và tổng hợp kết quả lượt 1. Phần mình phụ trách có 14/15 câu đạt. Sau khi ghép điểm với Hoàng, cả nhóm đạt 28/30. [Báo cáo đánh giá](../eval/report.md)

Mình cũng phụ trách tổng hợp bằng chứng từ Discord, làm giao diện portal cho ba hồ sơ giả và chuẩn bị slide. Phần demo dùng hai ca B01 và B06 để trình bày cách trả lời có nguồn và cách coach bổ sung kiến thức sau khi duyệt. [Bằng chứng](../evidence/summary.md) · [Portal](../codebase/portal_demo.html) · [Slide](../slides/demo.html)

## 2. AI hỗ trợ thế nào

Codex hỗ trợ đối chiếu số liệu, soạn bản tổng hợp, triển khai portal đọc dữ liệu từ API và xuất thử PDF. Một điểm cần kiểm là hai nhóm lượt nhắc Mod. Dữ liệu đính chính ghi riêng 43 lượt chỉ gọi Mod và 69 lượt có trả lời rồi mới nhắc Mod. [Đối chiếu dữ liệu, mục 3c](../evidence/data-mining.md)

Mình tự cấu hình kết nối OpenAI và chạy `python run.py eval --try` trên ba câu đầu. Mình kiểm tra terminal báo đã nối model và thấy B01, B03 có token từ GPT-6 Luna. B02 chạy qua công cụ, với 0 lần gọi model, nhưng vẫn có kết quả. Lượt thử này giúp mình kiểm tra cấu hình trước khi chạy đủ 30 câu. [Hồ sơ đánh giá](../eval/README.md)

## 3. Một câu thử trượt và bài học

B20 hỏi hạn nộp lab. Lượt 1 hỏi lại tên bài, trong khi kho đã có mục T01 ghi hạn 22:00. Trace cho thấy model chọn hỏi lại trước khi gọi công cụ tra kho.
Bài học từ ca này là kiểm tra căn cứ sẵn có trước khi yêu cầu học viên giải thích thêm. Lượt 2 với model thật trả đúng hạn 22:00 từ T01 cho B20. B16 lại chuyển coach khi cần hỏi học viên đang nói về mục nào. So từng câu giữa hai lượt cho thấy bản sửa giải được một lỗi, còn điểm tổng vẫn là 28/30. [Test hồi quy](../codebase/test_clarification_lookup.py) · [Báo cáo](../eval/report.md)
