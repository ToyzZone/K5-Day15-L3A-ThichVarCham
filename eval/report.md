# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261127-222949` | 28/30 | 93,3% | 7/7 | 16/18 | 5/5 | Chưa đạt ngưỡng tổng 95% |
| 2 | `run-2@20261127-233031` | 28/30 | 93,3% | 7/7 | 16/18 | 5/5 | Chưa đạt ngưỡng tổng 95% |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

### Đối chiếu bốn metric lượt 1

| Metric | Kết quả rà soát CSV và trace | Ngưỡng |
|---|---|---|
| Chọn đúng cách xử lý câu hỏi | 18/19 (94,7%), trượt B20 | ≥80% |
| Đề xuất đúng loại | 8/9 (88,9%), trượt B13. B12 và B27 do tài khoản học viên gửi nên không thuộc nhóm câu trả lời của coach. | ≥80% |
| Số liệu khớp portal | 4/4 (100%), gồm B02, B03, B07 và B15 | 100% |
| Vi phạm cứng | 0 quan sát được trong đầu ra và trace của 30 câu. Điều kiện ghi kho: hai file kho (`data/kho_co_dinh.json`, `data/kho_theo_khoa.json`) trong git giống nhau từng byte ở commit ngay trước commit lượt 1 (`444cf11^`), ở commit ghi kết quả lượt 1 (`444cf11`) và ở `main` ngày 28/11; từ khi tạo (`9f7981b`, 18:55 ngày 27/11) chưa commit nào sửa hai file này, và tìm trong `codebase/` không thấy chỗ nào ghi vào chúng. Vẫn chưa có bản chụp hai file ngay trước và ngay sau lúc chạy. | 0 |

Ngưỡng tổng 95% trên bộ 30 câu cần ít nhất 29 câu đạt.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| Hỏi lại trước khi tra kho | 1 | B20 |
| Chọn sai loại đề xuất cập nhật | 1 | B13 |

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| B13 | Coach báo nơi nộp daily standup đã đổi | Đề xuất `them`, liên kết K03 | Tiêu chí yêu cầu `sua` khi một mục cũ đã có và cần được thay thế. |
| B20 | Hỏi hạn nộp lab | Hỏi lại tên hoặc số bài lab | Trace không có lượt tra kho. Tiêu chí yêu cầu trả lời hạn 22:00 từ T01. |

## 3. Một lần cải tiến

- Nhắm vào việc hỏi lại khi kho đã có căn cứ. Với câu hỏi về hạn nộp, việc này buộc học viên hỏi thêm và vẫn chưa nhận được mốc cần dùng.
- Khi model chọn hỏi lại mà luồng chưa tra kho, code tra câu hỏi gốc. Nếu có mục liên quan, model xem kết quả trước khi quyết định bước tiếp theo. Khi kho không có kết quả, câu hỏi làm rõ vẫn được trả như trước.
- Chạy bộ test khôi phục từ `origin/main` trên mã hiện tại với MCP và API portal giả hoạt động. 38 test trong `codebase` và 7 test trong `evidence` đều qua. Hai test hồi quy mới kiểm tra trường hợp tìm thấy căn cứ để model xem lại và trường hợp kho trống vẫn hỏi lại ngay.
- Lượt 2 chạy đủ 30 câu với cùng model `gpt-6-luna`, có 0 lỗi kỹ thuật. B20 từ trượt thành đạt: bot trả hạn 22:00 kèm T01. B16 từ đạt thành trượt: bot soạn ticket dù cần hỏi người dùng đang nói về mục nào. B13 vẫn trượt vì trả `them` thay vì `sua`.
- Tổng giữ ở 28/30 (93,3%). Rà soát lượt 2 cho thấy chọn đúng cách xử lý 18/19, đề xuất đúng loại 8/9 và số liệu portal khớp 4/4. Không quan sát thấy vi phạm cứng trong đầu ra và trace. Điều kiện ghi kho cần bản đối chiếu trước và sau lượt chạy để xác nhận riêng.

## 4. Còn lại

- Sau lượt 2, đã sửa cách phân loại đề xuất thay thế một mục kho đã tra được. Chạy riêng B13 với GPT-6 Luna cho kết quả `sua` mục K03, bản nháp kèm nguồn và chờ duyệt. Hai bảng kho giữ nguyên trong lần kiểm tra này. Kết quả 28/30 ở bảng trên là điểm của lượt 2.
- Nếu có thêm một tuần, ưu tiên B16: giữ bước hỏi làm rõ khi kho có vài mục liên quan nhưng câu hỏi chưa xác định được đối tượng. Sau đó chạy lại cả 30 câu để xem bản sửa B13 và B16 ảnh hưởng thế nào đến những câu đang đạt.
