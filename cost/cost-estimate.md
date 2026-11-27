# Chi phí khi dùng thật

## 1. Đầu vào

- Ba persona dùng ít, vừa và nhiều có tỉ lệ 70%, 22%, 8%, ứng với 1,64, 5,33 và 16,68 phiên/người/tháng. Tần suất quy đổi từ lượt hỏi trong 23 ngày sang tháng 30 ngày, với một lượt bằng một phiên. [Đào dữ liệu, mục 3f](../evidence/data-mining.md)
- Quy mô thấp 169 người lấy theo số người có lượt kết thúc ở người hỗ trợ. Quy mô cơ sở 303 người lấy theo số người hỏi Kute. Quy mô cao 450 người là *tự ước tính*. Đây là giả định về số người dùng mỗi tháng dựa trên mẫu quan sát. [Cấu hình persona](personas.yaml)
- Giá Standard trên mỗi triệu token đầu vào/đầu ra là 0,10/0,50 USD cho GPT-6 Luna và 2,00/10,00 USD cho GPT-6.2 Sol, tra ngày 27/11/2026. [Giá Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) · [Bảng giá OpenAI](https://developers.openai.com/api/docs/pricing)
- Tỉ lệ đạt dùng để ước tính chi phí mỗi task thành công là **28/30 (93,3%)** từ lượt 2. [Kết quả lượt 2](../eval/run-2.csv)

## 2. Kết quả mô phỏng

Run ID `simulate-1@20261127-233726`, **50 phiên**, seed 42, **0 phiên lỗi**. Mẫu có 34 phiên dùng ít, 13 phiên dùng vừa và 3 phiên dùng nhiều. Khung lấy các sự kiện thường và khó từ benchmark, gồm câu hỏi học viên và câu trả lời của coach. [CSV](simulate-1.csv) · [Tóm tắt tự động](simulate-1-summary.md)

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (169 người) | Chi phí / tháng — cơ sở (303 người) | Chi phí / tháng — cao (450 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-6-luna (vào 0.1 · ra 0.5 $/1M) | $0.00033 | $0.00036 | $0.00036 | $0.2421 | $0.4341 | $0.6446 | $0.0014 |
| gpt-6.2-sol (vào 2.0 · ra 10.0 $/1M) | $0.0067 | $0.0072 | $0.0072 | $4.84 | $8.68 | $12.89 | $0.0287 |

Chia chi phí trung bình mỗi phiên cho tỉ lệ đạt để ước tính chi phí mỗi task thành công. Cả hai dòng dùng cùng số token đo trên GPT-6 Luna. Dòng GPT-6.2 Sol áp giá tham chiếu lên số token này, nên chi phí và tỉ lệ đạt khi chạy model đó vẫn cần đo riêng. Giá chỉ tính token, với đầu vào theo giá chưa cache.

## 3. So với impact

Ở quy mô cơ sở, chi phí model Luna khoảng **0,0014 USD/người/tháng**. Impact ước tính ở §2 là khoảng **121 lượt/tháng** hiện phải nhờ người mà trợ lý có thể tự trả lời, tương đương khoảng 0,40 lượt/người/tháng nếu phân bổ trên 303 người. Nhóm chưa đo số phút tiết kiệm, nên chưa quy đổi impact sang tiền. Chi phí mô phỏng cũng chưa gồm hosting và thời gian coach duyệt.

**Kết luận:** Nên tiếp tục thử nghiệm có người duyệt. Mức phí token thấp ở cả ba quy mô ước tính, nhưng hai lượt eval đều đạt 28/30 và còn dưới ngưỡng 95%. [Đánh giá](../eval/report.md) · [Impact, mục 2](../spec.md)
