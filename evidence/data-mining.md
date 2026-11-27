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

Chạy ngày 27/11/2026, sau commit ghi luật đếm (`6a88ea9`). N = 848 lượt Kute trả lời một tin của người, trong 23 ngày (khoảng 37 lượt/ngày).

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| Lượt không kết thúc bằng câu trả lời của Kute | 291/848 | 34% | tổng ba dòng dưới; là cận trên, xem mục 3b |
| · gọi `@Mod` vì chưa đủ thông tin | 112/848 | 13% | |
| · chỉ đưa khung tạo ticket | 171/848 | 20% | gồm cả lượt học viên chủ động xin tạo ticket |
| · báo `request timeout` | 8/848 | 1% | |
| Kute có trả lời | 557/848 | 66% | chưa kiểm câu trả lời đúng hay sai |
| Câu trả lời lặp (cùng câu trả lời ≥3 lần) | 108/557 | 19% | 23 câu trả lời khác nhau bị lặp |
| Câu hỏi phụ thuộc thời điểm | 30/848 | 4% | trong đó 8/30 (27%) Kute không tự trả lời được |
| Câu hỏi thông tin riêng (theo từ khoá) | 27/848 | 3% | ước lượng thấp: chỉ bắt câu có ngôi thứ nhất |

### 3b. Đếm bổ sung (thêm lúc 19:07 ngày 27/11, sau khi đã xem kết quả mục 3)

Không thuộc luật đếm ghi trước; thêm vì loại `menu_ticket` gộp hai việc khác nhau.

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| Lượt `menu_ticket` mà tin hỏi có chữ "ticket" | 170/171 | 99% | học viên chủ động xin tạo ticket, Kute làm đúng việc được nhờ |
| Kute không trả lời được dù học viên không xin ticket | 121/848 | 14% | 112 gọi Mod + 8 timeout + 1 khung ticket |
| Học viên bỏ qua Kute, xin ticket để gặp người | 170/848 | 20% | chưa biết vì sao: cần phỏng vấn |

## 4. ≥5 ví dụ cụ thể (mã dòng / mã đã ẩn danh, không đoán ai là ai)

Mã là 6 số cuối của mã tin. Trích nguyên văn, cắt ngắn, đã bỏ tên.

1. `218300` · "bao giờ nộp được mentor duty, hiện tại trên phoenix tôi chưa thấy chỗ để nộp" → Kute gọi `@Mod`.
2. `677635` · "Lớp L3B hôm nay học đến 20h ở trường, mà cũng có lịch họp Mentor Duty lúc 20h luôn…" → Kute gọi `@Mod`.
3. `949450` · "daily standup hằng ngày, tôi có phải nộp vào chủ nhật ko" → Kute gọi `@Mod`.
4. `457337` · "có được cấp quyền cấu hình settings repo github để cấu hình CI/CD không." → Kute gọi `@Mod`.
5. `569025` · "tôi bị chấm thiếu xp workshop 1 thì tạo ticket gì" → Kute chỉ đưa khung tạo ticket.
6. `470631` · "làm sao để biết mình được điểm danh buổi học hay chưa?" → Kute chỉ cách tự xem trên portal, không tra hộ được.
7. Câu Kute dùng khi không trả lời được: "Mình chưa nắm đủ thông tin cho câu này, nên để đảm bảo chính xác, mình sẽ tag Mod giúp bạn nhé!"

## 5. Giới hạn của data

Data cho biết người ta **làm gì**, không cho biết **vì sao**. Thiếu gì, lệch về phía nào:
- Chỉ có một kênh; câu hỏi trong ticket và tin nhắn riêng không thấy được, nên số câu Kute không xử lý được thực tế có thể cao hơn.
- Loại "chỉ đưa khung tạo ticket" gộp hai trường hợp; đã tách ở mục 3b bằng một phép đếm thêm sau khi xem kết quả, nên coi là mô tả, không phải kiểm định.
- Chưa đo thời gian chờ từ lúc Kute gọi Mod tới lúc có người trả lời, và chưa kiểm 557 câu Kute có trả lời là đúng hay đã cũ.
- Hai phép đếm theo từ khoá (thời điểm, thông tin riêng) bỏ sót câu không dùng đúng cụm từ.

→ Kiểm lại bằng phỏng vấn ≥3 học viên: lần gần nhất hỏi Kute mà không được trả lời thì bạn làm gì, chờ bao lâu.
