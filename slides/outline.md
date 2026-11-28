# Dàn slide → lấy số từ file nào

> Làm ở guide bước 5.1. Luật: **không có bằng chứng thì không có slide** — mỗi trang ≥1 con số / trích dẫn có nguồn / kết quả đo.
> Xuất PDF thành `demo-slides.pdf` ở thư mục gốc repo, nộp tại CP4 14:30 Thứ Bảy 28/11. Nộp PDF, không nộp link.

| # | Trang | Có gì | Số lấy từ | Xong |
|---|---|---|---|---|
| 1 | Người dùng & pain | Ai · việc gì · chỗ đau + số và trích dẫn | `evidence/summary.md` | Đã lên slide, có trích dẫn phỏng vấn P2 |
| 2 | Vì sao chọn bài này | Bảng impact rút gọn + hướng bị loại | `spec.md` §2, `evidence/summary.md` | Đã lên slide. Phỏng vấn cho 20, 20 và khoảng 5 phút của ba đoạn khác nhau, chưa đổi ra giờ |
| 3 | Giải pháp | Lát cắt một câu · sơ đồ · AI tự làm đến đâu, vì sao | `spec.md` §4, `evidence/data-mining.md` 3e | Đã lên slide |
| 4 | Demo live | Ba chỗ trợ lý làm khác Kute: hạn Gate 3 trả lời kèm nguồn → vòng học với câu "office hour học qua đâu" (B19): ticket → lab coach `!traloi` → **Duyệt và công khai** → hỏi lại bằng câu khác → group giả có bình luận; [kịch bản 120 giây](../docs/demo-2-phut.md) | `evidence/frozen-kute.md` mục 4, 4b · `eval/benchmark.csv` B19, `eval/run-1.csv`, `eval/run-2.csv` · `spec.md` §4b | Đã lên slide (#89). Link video dự phòng (#49) vẫn là luồng trước (B01 + B06), chưa quay lại |
| 5 | **Đánh giá thế nào** | Bộ câu thử, ngưỡng, run ID, lỗi chính và kết quả hai lượt | `eval/README.md`, `eval/report.md` | Có kết quả từng metric của hai lượt |
| 6 | **Chi phí khi dùng thật** | Chi phí / task thành công · 3 kịch bản · so với impact | `cost/cost-estimate.md` | Có kết quả 50 phiên và dòng so với impact |
| 7 | Kết luận | Iterate, dựa trên bằng chứng, điểm hai lượt và chi phí | `evidence/summary.md`, `eval/report.md`, `cost/cost-estimate.md` | Đã lên slide |
| 8 | Nếu có thêm 1 tuần | 2–3 việc, trỏ về lỗi còn lại / phản hồi người dùng | `eval/report.md` mục 4 · `evidence/summary.md` mục 5–6 · `evidence/frozen-kute.md` mục 2, 5b · `spec.md` §4b, §4c | Đã lên slide, đã rà sau lượt 2 và phỏng vấn; thêm một đoạn về thời khoá biểu (#92) |

Nguồn chỉnh sửa là [demo.html](demo.html). [PDF 8 trang ở thư mục gốc](../demo-slides.pdf) đã có kết quả hai lượt, số chi phí và phỏng vấn; xuất lại lúc 13:35 ngày 28/11 sau khi trang 4 đổi sang luồng demo mới (hạn Gate 3 · vòng học Office Hour · group giả) và trang 8 thêm một dòng về group thật (#89); xuất lại lần nữa lúc 13:58 ngày 28/11 sau khi trang 8 thêm một đoạn về thời khoá biểu (#92), bảy trang còn lại không đổi. Link video dự phòng ở chân trang 4; video đó vẫn quay luồng trước (B01 + B06), chưa quay lại theo luồng mới. Sửa slide thì xuất lại PDF khổ 16:9 với đầu và chân trang của trình duyệt tắt, ví dụ bằng Edge: `--headless --no-pdf-header-footer --print-to-pdf=demo-slides.pdf slides/demo.html`.

**Trước khi lên:** tải repo về một máy khác (hoặc thư mục mới), chạy theo mục "Chạy trong 3 phút" của `README.md` · `.env` có trên máy demo, đã gọi thử 1 câu trong vòng 1 giờ trước giờ demo · video dự phòng mở được bằng cửa sổ ẩn danh · biết bản chạy thử sẽ làm gì với **1 câu thử lạ** của giám khảo.

Ai nói trang nào (mỗi người ≥1 phần):

| Trang | Người nói |
|---|---|
| | |
