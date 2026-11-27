# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ đạt | [`data-mining.md`](data-mining.md): luật đếm, số, script [`count.py`](count.py) · [`frozen-kute.md`](frozen-kute.md): đối chiếu với nguồn chính thức |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ chưa làm (0/3) | chưa có file |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ không làm | |

Data là **848 lượt** Kute (bot đang chạy trên Discord của khoá) trả lời một tin của người, ở kênh hỏi trợ lý và tạo ticket, từ 05/11 đến 27/11/2026 (23 ngày, 303 người hỏi). Để biết câu trả lời đã có ở đâu và từ lúc nào, nhóm đối chiếu thêm với kênh thông báo Build Phase (27 tin), kênh thông báo lớp học và diễn đàn hỏi-đáp (18 bài, 64 tin).

Luật đếm được commit trước khi đếm (`6a88ea9`, 19:03 ngày 27/11). Lệnh chạy lại: `python evidence/count.py evidence/discord/raw-2026-11-27.jsonl`. Bản thô có tin nhắn thật của học viên nên để ngoài repo; repo chỉ có luật đếm, script và số đã tổng hợp.

## 2. Số chính

Mẫu số chung là N = 848 lượt, trừ dòng ghi mẫu số khác.

| Đếm được gì | x / N | % | Lấy từ |
|---|---|---|---|
| **Lượt kết thúc ở người** (tổng ba dòng dưới) | 282/848 | 33% | `data-mining.md` 3e |
| · học viên xin thẳng ticket để gặp người | 170/848 | 20% | 3b |
| · Kute chỉ gọi Mod, không trả lời | 43/848 | 5% | 3c |
| · Kute trả lời rồi vẫn nhắc tới Mod | 69/848 | 8% | 3c |
| Người hỏi có ít nhất một lượt kết thúc ở người | 169/303 | 56% | 3f |
| Kute bó tay: chỉ gọi Mod (43), timeout (8), tự nói không có thông tin (38) | 89/848 | 10% | `frozen-kute.md` mục 2 |
| Trong 282 lượt kết thúc ở người: lượt là câu hỏi kiến thức (90) hoặc hỏi thông tin riêng (3) | 93/282 | 33% | 3e; là mức ít nhất, vì 125 lượt không rõ học viên cần gì |
| Câu trả lời lặp: cùng một câu trả lời của Kute xuất hiện ≥3 lần (23 câu khác nhau) | 108/557 | 19% | mục 3; mẫu số là số lượt Kute có trả lời |

Ba số không có dạng x/N:

- **Thông tin đã có mà Kute vẫn hụt:** 21 mục thông tin có căn cứ là câu trả lời đã tồn tại lúc học viên hỏi, tổng 121 lượt hỏi. Trong đó Kute bó tay 23 lượt, nói không có thông tin 3 lượt, trả lời sai, lạc đề hoặc đã cũ 13 lượt (`frozen-kute.md` 5a).
- **Hạn Gate 3:** Kute nêu 23:59 ngày 29/11 ở cả 13 lượt được hỏi (09–27/11). Portal của khoá ghi 23:59 ngày 06/12 (đội trưởng xem ngày 27/11). Chưa biết portal ghi ngày này từ khi nào (`frozen-kute.md` 4b).
- **Tần suất:** trung vị 35 lượt hỏi mỗi ngày (ít nhất 5, nhiều nhất 91). Trung vị 1 lượt mỗi người; 24 người (8%) hỏi từ 7 lượt trở lên, chiếm 307/848 lượt (36%) (`data-mining.md` 3f).

Phỏng vấn chưa làm, nên chưa có số theo lời kể: mỗi tháng gặp mấy lần, mỗi lần chờ bao lâu, đang xoay xở bằng gì. Khảo sát: không làm.

## 3. Tám trích dẫn nguyên văn

`mã` là 6 số cuối của mã tin Kute trả lời. Câu trong ngoặc kép là nguyên văn, giữ cả lỗi gõ, đã bỏ tên và lời gọi `@Kute`. Ngày theo giờ Việt Nam.

| # | `mã` · ngày | Học viên hỏi | Kute đáp | Cho thấy gì |
|---|---|---|---|---|
| 1 | `398147` · 09/11 | "office hour học qua đâu" | "Vì câu này mình chưa có đủ thông tin, nên để tránh đưa thông tin sai, mình xin phép tag Mod hỗ trợ trả lời câu hỏi này cho bạn nhé!" | Kute bó tay lúc 19:30, dù thông báo nhắc lịch Office Hours (có giờ và kênh Stage) đã đăng lúc 15:53 cùng ngày. |
| 2 | `949450` · 09/11 | "daily standup hằng ngày, tôi có phải nộp vào chủ nhật ko" | "Mình e là chưa đủ thông tin để trả lời đúng câu này, nên xin phép nhờ đội ngũ Mod hỗ trợ bạn nha!" | Câu hậu cần chung, giống nhau cho mọi học viên; người hỏi phải chờ lab coach trả lời. |
| 3 | `753199` · 16/11 | "Các track của chương trình gồm những track nào?" | "Xin lỗi, request timeout." | Câu về track được hỏi 15 lượt trong 09–25/11, chưa lượt nào nhận được danh sách track. |
| 4 | `221272` · 19/11 | "có còn đổi được đề tài nưa không" | "Còn trong hạn chọn đề thì đổi trực tiếp ở tab Đề tài…" | Trả lời đã cũ: thông báo ngày 09/11 ghi hạn chọn đề là 23:59 ngày 14/11. |
| 5 | `557631` · 11/11 | "bây giờ còn hạn trao đổi thành viên trong nhóm không vậy" | "Bạn bấm Rời đội trên nền tảng Phoenix, sau đó tìm và tham gia đội mới." | Trả lời trái thông báo: thông báo ngày 05/11 ghi hạn tự do ghép đội là 13:00 ngày 08/11. |
| 6 | `785755` · 26/11 | "tôi nộp gate 2 đúng hạn mà không được cộng xp" | "Mentor cần thời gian review và chấm PASS cho đội thì hệ thống mới cộng XP nhé." | Học viên đáp ngay: "đã thấy pass gate 2 rồi mà". Câu trả lời chung không dùng được cho tình trạng riêng của người hỏi. |
| 7 | `569025` | "tôi bị chấm thiếu xp wworkshop 1 thì tạo ticket gì" | (không có chữ, chỉ hiện khung tạo ticket) | Hỏi nên tạo loại ticket nào, Kute chỉ hiện khung tạo ticket; phần còn lại diễn ra trong ticket riêng. |
| 8 | `470631` | "làm sao để biết mình được điểm danh buổi học hay chưa?" | (chỉ cách tự xem trên portal) | Câu hỏi về thông tin riêng: Kute không tra hộ được. |

Thêm ví dụ: `data-mining.md` mục 4 và `frozen-kute.md` mục 4.

## 4. Các nguồn có khớp nhau không

Mới có một loại nguồn là đào data, nên **chưa đối chiếu được data với lời người dùng**. Trong phạm vi data:

- **Kênh hỏi trợ lý so với nguồn chính thức:** có 21 mục thông tin đã tồn tại lúc hỏi mà Kute vẫn hụt ở một phần số lượt (mục 2 ở trên). Rõ nhất là hạn Gate 3: Kute và portal lệch nhau một tuần.
- **Lệch đã sửa:** luật ghi trước xếp cả 112 lượt có `@Mod` vào "Kute gọi Mod vì chưa đủ thông tin". Đọc lại thì chỉ 43 lượt đúng nghĩa đó, nên số 112/848 không dùng nữa (`data-mining.md` 3c).

Phỏng vấn cần trả lời ba điều data không cho biết: vì sao học viên xin thẳng ticket (117/170 lượt chỉ ghi "tạo ticket"), chờ bao lâu thì có câu trả lời, và câu trả lời cuối cùng đến từ đâu.

## 5. Kết luận

File `evidence/hypothesis.md` không được điền. Giả thuyết viết trước khi thu data nằm ở `canvas.md` dòng 4 của bản CP1 (commit `8058b17`, 16:57 ngày 27/11; luật đếm commit lúc 19:03): "một phần đáng kể câu hỏi trên kênh hỏi đáp là câu đã từng được TA/mod trả lời", với người dùng chính là lab coach phải trả lời lặp.

Giả thuyết đó **phải đổi**:

- **Phần đứng vững:** câu hỏi lặp lại là có thật. 108/557 lượt (19%) là Kute dùng lại cùng một câu trả lời, và có 21 mục thông tin đã tồn tại lúc học viên hỏi mà Kute vẫn hụt.
- **Phần không đứng vững:** không thấy lab coach trả lời lặp trên kênh công khai; các câu lặp là do Kute trả lời. Theo thông báo ngày 04/11, thắc mắc được xử lý qua ticket riêng, nên câu trả lời của lab coach không nằm ở kênh nhóm đọc được. Chỉ chứng minh được 6 lượt (5 chủ đề) đã có người trả lời trước mà Kute vẫn bó tay.
- **Đã đổi gì:** người dùng chính đổi từ lab coach sang học viên (chốt lúc 19:31 ngày 27/11, issue #14). Nỗi đau là 282/848 lượt hỏi (33%) kết thúc ở người, và 169/303 người hỏi (56%) gặp ít nhất một lần.

Điều vẫn chưa biết:

- Vì sao học viên xin thẳng ticket, chờ bao lâu, và lab coach mất bao nhiêu phút cho mỗi ticket.
- 557 lượt Kute có trả lời thì đúng hay sai: người trong nhóm đang chấm 478 lượt, chưa có kết quả (`data-mining.md` 3g).
- "Câu trả lời của lab coach nằm trong ticket riêng" là suy luận từ thông báo ngày 04/11, chưa có ai xác nhận.
- Portal ghi hạn Gate 3 là 06/12 từ khi nào.

## 6. Giới hạn

- **Một kênh công khai.** Câu hỏi trong ticket và tin nhắn riêng không thấy được, nên số lượt Kute không xử lý được thực tế có thể cao hơn.
- **Nhãn do AI gán, chưa có người chấm.** Áp dụng cho việc chia 282 lượt theo điều học viên cần và cho các kiểu trả lời sai, cũ, lạc đề. Lượt kiểm chéo 30 lượt (trùng 27/30) cũng do AI làm.
- **Một phần số được đếm sau khi đã xem kết quả** (`data-mining.md` 3b, 3c, 3d), nên là mô tả, không phải kiểm định.
- **Hai số đã đính chính:** 112/848 thành 43/848 (Kute chỉ gọi Mod) và 121/848 thành 52/848 (Kute không trả lời được dù học viên không xin ticket).
- **Vai trò người trả lời trên kênh và diễn đàn chưa xác minh.**
- **Chưa có nguồn thứ hai.** Mọi kết luận ở mục 5 mới dựa trên việc học viên đã làm gì, chưa có lời giải thích vì sao.

## Lịch hẹn (dùng cho CP2 — chỉ ghi vai và giờ, không tên)

| Vai | Giờ hẹn | Đã xong? |
|---|---|---|
| Học viên có dùng Kute (P1) | chưa ghi | chưa |
| Học viên có dùng Kute (P2) | chưa ghi | chưa |
| Học viên có dùng Kute (P3), hoặc một lab coach | chưa ghi | chưa |
