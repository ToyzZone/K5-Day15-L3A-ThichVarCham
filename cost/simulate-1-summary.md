# Tóm tắt mô phỏng simulate-1@20261127-233726

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 34 | 1 | 1956 | 218 | 1.3 | 1.8 |
| dung_vua | 13 | 1 | 2439 | 274 | 1.7 | 1.8 |
| dung_nhieu | 3 | 1 | 2673 | 419 | 1.7 | 2.0 |

Tỉ lệ đạt dùng để tính: 28/30 (93%) — lượt run-2@20261127-233031

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (169 người) | Chi phí / tháng — cơ sở (303 người) | Chi phí / tháng — cao (450 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-6-luna (vào 0.1 · ra 0.5 $/1M) | $0.00033 | $0.00036 | $0.00036 | $0.2421 | $0.4341 | $0.6446 | $0.0014 |
| gpt-6.2-sol (vào 2.0 · ra 10.0 $/1M) | $0.0067 | $0.0072 | $0.0072 | $4.84 | $8.68 | $12.89 | $0.0287 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (1.0) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: gpt-6-luna. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
