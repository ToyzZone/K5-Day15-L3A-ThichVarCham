# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Không đào data thì xoá file này. Script / công thức đếm để trong repo (vd `evidence/count.py` hoặc ghi công thức Sheets ngay dưới), người khác chạy lại phải ra cùng số.
> Repo chỉ chứa số đã tổng hợp và vài dòng ví dụ — không chép lại nguyên file data.

## 1. Cách đếm — viết TRƯỚC khi chạy

- Data dùng: 1.848 tin ở kênh hỏi trợ lý và tạo ticket trên Discord của khoá (kênh mọi học viên đều đọc được), từ 05/11/2026 đến 27/11/2026. Thu bằng trình duyệt ngày 27/11; tên người gửi đã thay bằng mã `P…` ngay lúc thu, email, số điện thoại và mã học viên bị che. Bản thô để ngoài repo (`evidence/discord/raw-2026-11-27.jsonl`, đã gitignore).
- Đếm gì, trên tập nào: mỗi lượt Kute trả lời (reply) một tin của người được xếp vào đúng một loại, theo thứ tự:
  1. `chuyen_mod`: nội dung có `@Mod` (Kute nói chưa đủ thông tin và gọi Mod);
  2. `loi_timeout`: nội dung có `request timeout`;
  3. `menu_ticket`: không có chữ, chỉ có khung "Tạo ticket hỗ trợ";
  4. `co_tra_loi`: còn lại.
- Đếm thêm, cùng mẫu số:
  - câu trả lời lặp: trong các lượt `co_tra_loi`, lượt có 60 ký tự đầu (bỏ mã người, gộp khoảng trắng) trùng với ít nhất 2 lượt khác;
  - câu hỏi phụ thuộc thời điểm: 120 ký tự đầu của tin được trả lời có một trong các cụm `hôm nay, hôm qua, ngày mai, tối nay, sáng nay, chiều nay, sáng mai, tuần này, tuần sau, bây giờ, hiện tại, mấy giờ, link zoom`; trong đó bao nhiêu lượt Kute không tự trả lời được (ba loại 1–3);
  - câu hỏi thông tin riêng (ước lượng bằng từ khoá): tin được trả lời vừa có một mục riêng (`xp, điểm danh, điểm, mã học viên, mssv, nhóm, đội, level, gate, bài nộp, standup, tên hiển thị`) vừa có ngôi thứ nhất (`của mình/tôi/em/tớ` hoặc `mình/tôi/em/tớ đã/có/bị/được/chưa/vẫn`).
- **Mẫu số là gì:** N = số lượt Kute reply một tin của người (không tính tin Kute tự đăng, không tính tin người với người). Mẫu số của "câu trả lời lặp" là số lượt `co_tra_loi`.
- Script / công thức: `python evidence/count.py evidence/discord/raw-2026-11-27.jsonl`

## 2. Đọc trước, đếm sau

Đã đọc 40 tin đầu của học viên, 12 mẫu câu Kute dùng nhiều nhất và 14 mẫu câu Kute có từ khoá "chưa đủ thông tin / tag Mod / ticket / timeout". Lúc đọc đã biết tổng số tin theo người gửi (901 tin của Kute, 947 tin của người); chưa tính tỉ lệ nào ở mục 3. Các kiểu hành vi thấy được:
- Học viên gắn tên Kute rồi hỏi một câu ngắn; nhiều tin chỉ là lời chào để thử.
- Kute có ba cách đáp khi không trả lời được: gọi `@Mod`, đưa khung tạo ticket, hoặc báo `request timeout`.
- Cùng một câu trả lời của Kute xuất hiện nhiều lần (ví dụ cách xem XP, nộp daily standup), tức là cùng một câu hỏi được hỏi lại.
- Có câu hỏi về chính người hỏi (mã học viên, tên hiển thị, XP) mà Kute không có cách tra.

## 3. Kết quả

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| | | | |
| | | | |

Ghi dạng "x/N (y%)". "Nhiều bạn…" không phải số.

## 4. ≥5 ví dụ cụ thể (mã dòng / mã đã ẩn danh, không đoán ai là ai)

1.
2.
3.
4.
5.

## 5. Giới hạn của data

Data cho biết người ta **làm gì**, không cho biết **vì sao**. Thiếu gì, lệch về phía nào: __
→ Kiểm lại bằng phỏng vấn / khảo sát nào: __
