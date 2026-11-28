# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ đạt | [`data-mining.md`](data-mining.md): luật đếm, số, script [`count.py`](count.py) · [`frozen-kute.md`](frozen-kute.md): đối chiếu với nguồn chính thức |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☑ đạt (3/3) | [`P1`](interviews/P1.md) · [`P2`](interviews/P2.md) · [`P3`](interviews/P3.md) |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ không làm | |

Data là **848 lượt** Kute (bot đang chạy trên Discord của khoá) trả lời một tin của người, ở kênh hỏi trợ lý và tạo ticket, từ 05/11 đến 27/11/2026 (23 ngày, 303 người hỏi). Để biết câu trả lời đã có ở đâu và từ lúc nào, nhóm đối chiếu thêm với kênh thông báo Build Phase (27 tin), kênh thông báo lớp học và diễn đàn hỏi-đáp (18 bài, 64 tin).

Luật đếm được commit trước khi đếm (`6a88ea9`, 19:03 ngày 27/11). Lệnh chạy lại: `python evidence/count.py evidence/discord/raw-2026-11-27.jsonl`. Bản thô có tin nhắn thật của học viên nên để ngoài repo; repo chỉ có luật đếm, script và số đã tổng hợp.

Phỏng vấn làm sau khi đếm, để kiểm lại data bằng lời người dùng: ba học viên AI20K ngoài nhóm, đều đã hỏi Kute, phỏng vấn ngày 27–28/11 (hai người qua Discord, một người trực tiếp). Mỗi file ghi câu đã hỏi, ghi chép theo thứ tự kể và trích nguyên văn, đã bỏ tên.

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
| Người được phỏng vấn mà ở lần hỏi Kute gần nhất vẫn phải tìm đến người (lab coach hoặc BTC) | 3/3 | — | mục 4 dưới đây; theo lời kể |

Ba số không có dạng x/N:

- **Thông tin đã có mà Kute vẫn hụt:** 21 mục thông tin có căn cứ là câu trả lời đã tồn tại lúc học viên hỏi, tổng 121 lượt hỏi. Trong đó Kute bó tay 23 lượt, nói không có thông tin 3 lượt, trả lời sai, lạc đề hoặc đã cũ 13 lượt (`frozen-kute.md` 5a).
- **Hạn Gate 3:** Kute nêu 23:59 ngày 29/11 ở cả 13 lượt được hỏi (09–27/11). Portal của khoá ghi 23:59 ngày 06/12 (đội trưởng xem ngày 27/11). Chưa biết portal ghi ngày này từ khi nào (`frozen-kute.md` 4b).
- **Tần suất:** trung vị 35 lượt hỏi mỗi ngày (ít nhất 5, nhiều nhất 91). Trung vị 1 lượt mỗi người; 24 người (8%) hỏi từ 7 lượt trở lên, chiếm 307/848 lượt (36%) (`data-mining.md` 3f).

Theo lời kể ở phỏng vấn: P2 hỏi Kute 3 lần trong tháng, 2 lần phải hỏi người; P1 và P3 mỗi người 1 lần, lần đó đều cần người. Thời gian kể là 20, 20 và khoảng 5 phút, nhưng mỗi người đo một đoạn khác nhau (xem mục 4), nên không cộng hay lấy trung bình. Khảo sát: không làm.

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

Thêm ví dụ: `frozen-kute.md` mục 4.

## 4. Phỏng vấn ba học viên

| Người | Lần gần nhất hỏi Kute và bước tiếp theo | Tần suất tự kể | Thời gian được kể | Trích nguyên văn |
|---|---|---|---|---|
| [P1](interviews/P1.md) | Hỏi điểm bài lab công bố ở đâu (13/11). Kute nhờ Mod hỗ trợ. P1 hỏi lab coach và nhận câu trả lời từ coach. | 1 lần tương tự trong tháng | 20 phút gồm tự tìm và chờ, chưa tách từng phần | "Sau khi đọc câu trả lời mình đi hỏi labcoach, cuối cùng nhận từ lab coach" |
| [P2](interviews/P2.md) | Hỏi hạn nộp lab khi LMS lỗi (27/11). Kute không đáp ứng được nên P2 hỏi lab coach. Chưa biết kết quả cuối. | 3 lần hỏi Kute, 2 lần cần người | 20 phút; chưa rõ tính từ lúc nào tới lúc nào | "Kute không đưa ra được câu trả lời tôi muốn. tôi phải hỏi lab coach để có câu trả lời" |
| [P3](interviews/P3.md) | Hỏi về xin nghỉ buổi hackathon mà vẫn làm remote. Đã hỏi vài lab coach trước mà chưa có thông tin chính xác. Kute trả lời khá đầy đủ nhưng bảo xác nhận với BTC qua ticket. Chưa biết đã có xác nhận chưa. | 1 lần hỏi Kute, lần đó cần BTC xác nhận | Khoảng 5 phút gồm chờ và đọc câu trả lời; chưa tính tới lúc có xác nhận | "Kute trả lời khá đầy đủ nhưng cũng kêu tôi xác nhận với btc" |

## 5. Các nguồn có khớp nhau không

**Data và phỏng vấn khớp nhau ở điểm chính:** học viên hỏi Kute xong vẫn phải tìm đến người. Data đếm được 282/848 lượt (33%) kết thúc ở người và 169/303 người hỏi (56%) gặp ít nhất một lần; cả ba người được phỏng vấn đều kể lần gần nhất như vậy. Câu Kute trả P1 theo lời kể ("…nên mình nhờ Mod hỗ trợ giải đáp cho bạn nhé!") cùng kiểu với 43 lượt "Kute chỉ gọi Mod" trong data.

**Phỏng vấn cho thêm hai điều data không thấy được:**

- **Vì sao phải tìm người:** ở P1 và P2, Kute không trả lời được điều cần biết. Ở P3, Kute trả lời khá đầy đủ nhưng chuyện cần người *xác nhận* chính sách. Kiểu thứ hai khớp với 64 lượt "cần người làm thật" ở `data-mining.md` 3e: một phần lượt kết thúc ở người là việc trợ lý không nên tự quyết.
- **Học viên hỏi bot trước tiên để nhanh:** P2 chưa tìm ở đâu khác trước khi hỏi Kute, "hỏi bot để có thể có được câu trả lời nhanh nhất". Nên khi Kute hụt, học viên mất thêm một vòng chờ người.

**Chưa khớp hoặc chưa kiểm được:**

- Thời gian: 20, 20 và khoảng 5 phút đo ba đoạn khác nhau (tự tìm cộng chờ; cả lần hỏi; chờ cộng đọc), chưa ai kể tới lúc việc xong hẳn. Chưa dùng để tính số phút tiết kiệm.
- Chưa ai trong ba người cho biết câu trả lời của coach nằm ở đâu, nên "câu trả lời của lab coach nằm trong ticket riêng, Kute không học được" vẫn là suy luận từ thông báo ngày 04/11.

**Trong phạm vi data:**

- **Kênh hỏi trợ lý so với nguồn chính thức:** có 21 mục thông tin đã tồn tại lúc hỏi mà Kute vẫn hụt ở một phần số lượt (mục 2 ở trên). Rõ nhất là hạn Gate 3: Kute và portal lệch nhau một tuần.
- **Lệch đã sửa:** luật ghi trước xếp cả 112 lượt có `@Mod` vào "Kute gọi Mod vì chưa đủ thông tin". Đọc lại thì chỉ 43 lượt đúng nghĩa đó, nên số 112/848 không dùng nữa (`data-mining.md` 3c).

## 6. Kết luận

File `evidence/hypothesis.md` không được điền. Giả thuyết sớm nhất nhóm ghi lại nằm ở `canvas.md` dòng 4 của bản CP1 (commit `8058b17`, 16:57 ngày 27/11), trước commit luật đếm (19:03) và commit số đầu tiên (19:04): "một phần đáng kể câu hỏi trên kênh hỏi đáp là câu đã từng được TA/mod trả lời", với người dùng chính là lab coach phải trả lời lặp.

Giả thuyết đó **phải đổi**:

- **Phần đứng vững:** câu hỏi lặp lại là có thật. 108/557 lượt (19%) là Kute dùng lại cùng một câu trả lời, và có 21 mục thông tin đã tồn tại lúc học viên hỏi mà Kute vẫn hụt.
- **Phần không đứng vững:** không thấy lab coach trả lời lặp trên kênh công khai; các câu lặp là do Kute trả lời. Theo thông báo ngày 04/11, thắc mắc được xử lý qua ticket riêng, nên câu trả lời của lab coach không nằm ở kênh nhóm đọc được. Chỉ chứng minh được 6 lượt (5 chủ đề) đã có người trả lời trước mà Kute vẫn bó tay.
- **Đã đổi gì:** người dùng chính đổi từ lab coach sang học viên (chốt lúc 19:31 ngày 27/11, issue #14). Nỗi đau là 282/848 lượt hỏi (33%) kết thúc ở người, và 169/303 người hỏi (56%) gặp ít nhất một lần. Phỏng vấn làm sau đó ủng hộ hướng mới: 3/3 người kể lần hỏi Kute gần nhất phải tìm tiếp lab coach hoặc BTC.

Điều vẫn chưa biết:

- Học viên chờ bao lâu tới khi xong việc, và lab coach mất bao nhiêu phút cho mỗi ticket. Phỏng vấn mới cho số phút của từng đoạn, chưa so được với nhau.
- Vì sao học viên xin thẳng ticket (117/170 lượt chỉ ghi "tạo ticket"): phỏng vấn mới cho hai lý do ở ba người.
- 557 lượt Kute có trả lời thì đúng hay sai: mới có một người chấm lô 1 (249/478 lượt). Trong 188 câu chấm được đúng sai, 31 câu (16%) không dùng được sau khi chấm lại 14 câu do AI chỉ ra căn cứ; lượt chấm mù ra 17 câu (9%). 43/249 câu (17%) được gán `khong_tra_loi` (gồm cả câu Kute chỉ chỗ tự tìm mà không đưa nội dung). Chưa đo độ trùng giữa hai người chấm, nên coi là số sơ bộ (`data-mining.md` 3g).
- "Câu trả lời của lab coach nằm trong ticket riêng" là suy luận từ thông báo ngày 04/11, phỏng vấn chưa xác nhận.
- Portal ghi hạn Gate 3 là 06/12 từ khi nào.

## 7. Giới hạn

- **Một kênh công khai.** Câu hỏi trong ticket và tin nhắn riêng không thấy được, nên số lượt Kute không xử lý được thực tế có thể cao hơn.
- **Nhãn do AI gán, chưa có người chấm.** Áp dụng cho việc chia 282 lượt theo điều học viên cần và cho các kiểu trả lời sai, cũ, lạc đề. Lượt kiểm chéo 30 lượt (trùng 27/30) cũng do AI làm.
- **Một phần số được đếm sau khi đã xem kết quả** (`data-mining.md` 3b, 3c, 3d), nên là mô tả, không phải kiểm định.
- **Hai số đã đính chính:** 112/848 thành 43/848 (Kute chỉ gọi Mod) và 121/848 thành 52/848 (Kute không trả lời được dù học viên không xin ticket).
- **Vai trò người trả lời trên kênh và diễn đàn chưa xác minh.**
- **Phỏng vấn ít người và là lời kể.** Ba người; số lần và số phút là họ nhớ lại, chưa đối chiếu với lịch sử tin nhắn. Phỏng vấn làm sau khi đã có số đếm, nên người hỏi có thể đã hướng câu hỏi theo kết quả data.
