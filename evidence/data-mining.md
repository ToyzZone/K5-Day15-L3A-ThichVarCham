# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Ôn lại: ngày 2, ngày 6 · lab ngày 2, lab ngày 6.
> Không đào data thì xoá file này. Script / công thức đếm để trong repo (vd `evidence/count.py` hoặc ghi công thức Sheets ngay dưới), người khác chạy lại phải ra cùng số.
> Repo chỉ chứa số đã tổng hợp và vài dòng ví dụ — không chép lại nguyên file data.

## 1. Cách đếm — viết TRƯỚC khi chạy

- Data dùng: 1.848 tin ở kênh hỏi trợ lý và tạo ticket trên Discord của khoá (kênh mọi học viên đều đọc được), từ 05/11/2026 đến 27/11/2026. Thu bằng trình duyệt ngày 27/11; tên người gửi đã thay bằng mã `P…` ngay lúc thu, email, số điện thoại và mã học viên bị che. Bản thô để ngoài repo (`evidence/discord/raw-2026-11-27.jsonl`, đã gitignore).
- Data thêm tối 27/11 (dùng cho mục 3d): 27 tin kênh thông báo Build Phase (05–27/11), 10 tin kênh thông báo chung (03–25/11), 18 bài của diễn đàn hỏi-đáp (64 tin, 05–24/11). Cùng cách thu và che tên; bản thô để ngoài repo.
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
  - Tối 27/11 tên biến trong script đổi sang tiếng Anh theo quy ước nhóm. Luật đếm không đổi: output trên file thô trước và sau khi đổi giống từng byte (cả khi chạy thêm `--vd`).

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
| · nội dung có `@Mod` | 112/848 | 13% | **đã đính chính ở mục 3c:** chỉ 43 lượt là Kute gọi Mod mà không trả lời |
| · chỉ đưa khung tạo ticket | 171/848 | 20% | gồm cả lượt học viên chủ động xin tạo ticket |
| · báo `request timeout` | 8/848 | 1% | |
| Kute có trả lời | 557/848 | 66% | đã chấm đúng sai 250/478 lượt, hai lô (mục 3g) |
| Câu trả lời lặp (cùng câu trả lời ≥3 lần) | 108/557 | 19% | 23 câu trả lời khác nhau bị lặp |
| Câu hỏi phụ thuộc thời điểm | 30/848 | 4% | trong đó 8/30 (27%) Kute không tự trả lời được |
| Câu hỏi thông tin riêng (theo từ khoá) | 27/848 | 3% | ước lượng thấp: chỉ bắt câu có ngôi thứ nhất |

### 3b. Đếm bổ sung (thêm lúc 19:07 ngày 27/11, sau khi đã xem kết quả mục 3)

Không thuộc luật đếm ghi trước; thêm vì loại `menu_ticket` gộp hai việc khác nhau.

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| Lượt `menu_ticket` mà tin hỏi có chữ "ticket" | 170/171 | 99% | học viên chủ động xin tạo ticket, Kute làm đúng việc được nhờ |
| ~~Kute không trả lời được dù học viên không xin ticket~~ | ~~121/848~~ | ~~14%~~ | sai, xem mục 3c: đúng là 52/848 (6%) |
| Học viên bỏ qua Kute, xin ticket để gặp người | 170/848 | 20% | chưa biết vì sao: cần phỏng vấn |

### 3c. Đính chính (19:28 ngày 27/11, sau khi đọc nội dung các lượt có `@Mod`)

Luật ghi trước xếp mọi lượt có `@Mod` vào "Kute gọi Mod vì chưa đủ thông tin". Đọc lại thì loại này gộp hai kiểu khác nhau, nên con số 112/848 (13%) **không được dùng** với nghĩa "Kute bó tay". Luật ghi trước giữ nguyên ở mục 1; số đúng để dùng là bảng dưới.

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| Kute chỉ gọi Mod, không trả lời | 43/848 | 5% | tin bắt đầu bằng `@Mod`, kiểu "mình chưa đủ thông tin" |
| Kute có trả lời dài rồi nhắc tới Mod | 69/848 | 8% | thường là việc cần người xử lý (tài khoản, quyền), không hẳn thiếu kiến thức |
| Kute không trả lời được dù học viên không xin ticket | 52/848 | 6% | 43 chỉ gọi Mod + 8 timeout + 1 khung ticket |
| Kute hỏi lại bằng danh sách lựa chọn | 148/848 | 17% | tin có cụm "mô tả rõ hơn"; đếm thêm, chưa biết sau đó học viên có được trả lời không |

### 3d. Đối chiếu với nguồn chính thức (tối 27/11, dò bằng từ khoá rồi đọc tay; không thuộc luật ghi trước)

Câu hỏi: có thông tin nào đã được công bố chính thức trước lúc học viên hỏi mà Kute vẫn không đưa ra được không? Cách làm: lấy 12 mục thông tin có trong kênh thông báo hoặc trong câu trả lời trên diễn đàn hỏi-đáp, tìm các lượt hỏi Kute về đúng mục đó sau ngày công bố (35 lượt), rồi đọc nguyên câu trả lời của Kute.

| Thông tin | Đã có từ | Học viên hỏi Kute | Kute làm gì |
|---|---|---|---|
| Nộp lab muộn, nộp nhiều lần | thông báo chung, 07/11 | 22/11 · `833697` · "nộp muộn có sao không" | trả lời dài nhưng lẫn sang Mentor Duty, nội dung khác thông báo, rồi nhắc Mod |
| Nộp nhầm bài lab | thông báo chung, 12/11 | 14/11 · `233977` · "nộp nhầm link lab trên lms" | phần chữ nói về nộp Demo Day; có kèm khung ticket soạn sẵn |
| Hạn Gate 3 | portal của khoá ghi 23:59 ngày 06/12 (đội trưởng xem ngày 27/11) | 13 lượt, 09/11–27/11 | Kute nêu 23:59 ngày 29/11 ở cả 13 lượt; chưa biết portal ghi 06/12 từ khi nào |

**Đính chính (tối 27/11):** bản trước có thêm dòng "quy tắc tên domain khi deploy" và ghi Kute chưa lần nào nêu quy tắc này. Sai: Kute đã nêu quy tắc (tên miền phải chứa mã đội) ở 3 lượt trong 23–25/11, nên dòng đó bị rút. Còn 2 mục đứng vững trong lượt dò này; các lượt còn lại Kute trả lời tạm ổn hoặc câu hỏi không trùng nội dung đã công bố. Bảng đầy đủ hơn (21 mục có căn cứ, 22 mục chưa chứng minh được) ở [`frozen-kute.md`](frozen-kute.md). Lý do ít: theo thông báo ngày 04/11, mọi thắc mắc được xử lý qua ticket riêng, nên câu trả lời của lab coach không nằm ở kênh mà nhóm đọc được.

### 3e. Gán nhãn 282 lượt kết thúc ở người — luật viết TRƯỚC khi gán

- Tập gán nhãn: 170 lượt học viên xin thẳng ticket + 43 lượt Kute chỉ gọi Mod + 69 lượt Kute trả lời rồi nhắc Mod = 282 lượt.
- Mỗi lượt đúng một nhãn, xét theo điều học viên cần:
  - `hoi_kien_thuc`: cần một thông tin giống nhau cho mọi học viên (quy định, hạn, cách làm, ở đâu). Kho kiến thức có mục này thì trả lời được.
  - `thong_tin_rieng`: cần tra dữ liệu của chính người hỏi mà portal có (XP, điểm danh, trạng thái, đội), chỉ đọc.
  - `can_nguoi_lam`: cần một người làm hoặc quyết định (sửa điểm danh, mở khoá tài khoản, đổi email, cấp quyền, xin ngoại lệ, khiếu nại).
  - `khong_ro`: tin không nêu vấn đề (chỉ "tạo ticket", lời chào, thử bot).
- Vừa hỏi thông tin vừa cần người làm thì gán `can_nguoi_lam`.
- Người gán: một agent AI đọc từng lượt, một lượt gán. Kiểm chéo: 30 lượt rút ngẫu nhiên (seed 42) được gán lại độc lập, báo số lượt trùng nhãn.
- Con số cần báo: (`hoi_kien_thuc` + `thong_tin_rieng`) / 282 và / 848.

**Kết quả (gán xong tối 27/11; file nhãn để ngoài repo cùng bản thô):**

| Nhãn | Xin ticket (170) | Kute chỉ gọi Mod (43) | Kute trả lời rồi nhắc Mod (69) | Tổng (282) | % của 282 |
|---|---|---|---|---|---|
| `hoi_kien_thuc` | 15 | 29 | 46 | 90 | 32% |
| `thong_tin_rieng` | 0 | 0 | 3 | 3 | 1% |
| `can_nguoi_lam` | 38 | 6 | 20 | 64 | 23% |
| `khong_ro` | 117 | 8 | 0 | 125 | 44% |

- **Con số cần báo:** (`hoi_kien_thuc` + `thong_tin_rieng`) = 93/282 (33%) = 93/848 (11%) tổng số lượt hỏi Kute. Đây là mức **ít nhất**, vì 125 lượt `khong_ro` không biết được học viên cần gì.
- Trong 112 lượt có nhắc Mod, 78 lượt (70%) là câu hỏi kiến thức hoặc thông tin riêng. Trong 170 lượt xin ticket, 117 lượt (69%) chỉ ghi "tạo ticket", nội dung nằm trong form ticket riêng.
- Độ chắc: agent đánh dấu 64/282 lượt là phân vân; nếu đảo hết các lượt phân vân thì `hoi_kien_thuc` nằm trong khoảng 80–110 lượt.
- Kiểm chéo 30 lượt ngẫu nhiên (seed 42), gán độc lập trước khi xem nhãn của agent: trùng 27/30. Bỏ 15 lượt "tạo ticket" trơn (trùng hiển nhiên) thì trùng 12/15. Ba lượt lệch: hai câu cụt kiểu "1", "cả 3" (một bên dựa vào câu Kute đáp để đoán, một bên gán `khong_ro`) và một câu xin bảo lưu.
- Chủ đề nhiều nhất trong 90 lượt `hoi_kien_thuc` (agent gom tay): cách tạo ticket và ai xử lý (17) · nộp bài và gate (11) · XP và level (8) · lịch, phòng, mốc thời gian (7) · workshop và sự kiện (6) · mentor duty (6) · repo GitHub của nhóm (6).
- Giới hạn: cả hai lượt gán đều do AI làm, chưa có người chấm; ranh giới giữa "hỏi cách xử lý một sự cố" và "cần người làm" là chỗ lệch nhiều nhất (30 lượt phân vân).

### 3f. Người dùng và tần suất (mô tả, tối 27/11; dùng cho §2 của spec và persona chi phí)

Trong 23 ngày (05–27/11) có **303 người** hỏi Kute, tổng 848 lượt; trung vị 1 lượt/người, người hỏi nhiều nhất 24 lượt. Mỗi ngày trung vị 35 lượt (ít nhất 5, nhiều nhất 91).

| Kiểu người dùng | Số người | % người | Số lượt | % lượt | Trung bình lượt / người / 23 ngày |
|---|---|---|---|---|---|
| Ít (1–2 lượt) | 212 | 70% | 267 | 31% | 1,3 |
| Vừa (3–6 lượt) | 67 | 22% | 274 | 32% | 4,1 |
| Nhiều (≥7 lượt) | 24 | 8% | 307 | 36% | 12,8 |

169/303 người (56%) có ít nhất một lượt kết thúc ở người (xin ticket hoặc Kute nhắc Mod). Chưa có số phút lab coach bỏ ra cho mỗi lượt và thời gian học viên chờ: lấy từ phỏng vấn.

### 3g. Người chấm câu trả lời của Kute — luật viết TRƯỚC khi chấm

Vì sao cần: các lượt Kute "có trả lời" chưa ai kiểm đúng sai, và các nhãn ở mục 3e, `frozen-kute.md` đều do AI gán. Phần này để người trong nhóm chấm.

- **Tập chấm:** mọi lượt Kute trả lời một tin của người và có nội dung để chấm. Bỏ: khung tạo ticket, timeout, tin chỉ gọi `@Mod`, tin chỉ hỏi lại bằng danh sách lựa chọn (có cụm "mô tả rõ hơn"). Còn **478 lượt** (409 lượt trả lời thẳng + 69 lượt trả lời rồi nhắc Mod).
- **Chia lô:** `python evidence/make_label_lots.py` xáo tập chấm một lần với seed 2711. Chia thành 2 lô. 20 câu đầu nằm trong cả hai lô để đo độ trùng giữa hai người chấm; 458 câu còn lại chia đều, mỗi lô 249 câu. Vì đã xáo, phần đầu mà một người chấm được là mẫu ngẫu nhiên của tập chấm: chấm dở vẫn báo được x/n.
- **Sáu nhãn**, mỗi câu đúng một nhãn:
  - `dung`: đúng vào thời điểm hỏi và đúng điều được hỏi.
  - `sai`: có thông tin sai so với thông báo chính thức hoặc portal vào thời điểm hỏi.
  - `lac_de`: trả lời một việc khác với điều được hỏi.
  - `da_cu`: từng đúng, tới thời điểm hỏi thì hết đúng (hạn đã qua, quy định đã đổi).
  - `khong_tra_loi`: Kute nói không có thông tin, hoặc chỉ chỉ chỗ để tự tìm mà không đưa nội dung.
  - `khong_chac`: người chấm không đủ căn cứ để biết đúng hay sai.
- **Quy tắc:** chấm theo thời điểm hỏi (công cụ hiện ngày giờ hỏi), không theo hôm nay. Vừa có phần đúng vừa có phần sai thì gán `sai`. Không biết thì gán `khong_chac`, không đoán. Người chấm không thấy nhãn AI đã gán.
- **Công cụ:** `evidence/label-tool.html`, mở bằng trình duyệt, chạy không cần mạng. File lô có tin nhắn thật nên không nằm trong repo; đội trưởng gửi riêng cho từng người.
- **Gộp:** `python evidence/merge_labels.py <các file nhãn>`. Mỗi câu tính một lần; câu có nhiều người chấm lấy theo số đông, hoà thì tính `khong_chac`.
- **Con số sẽ báo:** tỉ lệ từng nhãn (x/n trên số câu đã chấm); trong các câu chấm được đúng sai, tỉ lệ không dùng được (`sai` + `lac_de` + `da_cu`); số câu chung mà mọi người chấm giống nhau.

Kết quả (ghi ngày 28/11/2026): lô 1 chấm đủ 249 câu; lô 2 chấm 21 câu (20 câu chung + 1 câu riêng); tổng cộng 250/478 câu của tập chấm. Lô 1 qua hai lượt: lượt 1 chấm mù, lượt 2 chấm lại 14 câu sau khi đối chiếu với AI (xem bên dưới). Số dùng ở các file khác là số gộp, kèm số của lượt chấm mù.

**Gộp hai lô.** Lệnh: `python evidence/merge_labels.py evidence/discord/raw-chamlai-lo-1-G1.json evidence/discord/raw-nhan-lo-2-G2.json`. Output của script:

| Nhãn | x / n | % |
|---|---|---|
| Đúng | 158/250 | 63% |
| Sai | 16/250 | 6% |
| Lạc đề | 10/250 | 4% |
| Đã cũ | 2/250 | 1% |
| Không trả lời | 39/250 | 16% |
| Không chắc | 25/250 | 10% |

Trong 186 câu chấm được đúng sai: 28 câu không dùng được (15%; KTC 95% Wilson 11–21%, tính ngoài script).

Câu có từ 2 người gán: 20; mọi người gán giống nhau ở 12 câu (60%). Theo luật gộp, 8 câu hai người gán khác nhau được tính là `khong_chac`. Nếu gộp bằng lượt chấm mù của lô 1 (`raw-nhan-lo-1-G1.json`) thì không dùng được là 16/188 (9%), hai người trùng 14/20 (70%).

**Độ trùng trên 20 câu chung.** Ở lượt chấm mù, hai người trùng 14/20 câu. Kappa chỉ 0,10 vì người chấm lô 2 gán `dung` 19/20 câu, nên tỉ lệ trùng do ngẫu nhiên vốn đã cao. Các chỗ lệch:
- 4 câu Kute chỉ sang portal hoặc ticket: người chấm lô 1 gán `khong_tra_loi`, người chấm lô 2 gán `dung`. Với câu hỏi kiểu "kiểm tra ở đâu", chỉ chỗ cũng là câu trả lời; luật chưa tách trường hợp này.
- 2 câu lượt 2 đã đổi theo căn cứ AI (một câu về runner, đã đối chiếu nguồn; một câu về nộp lại bài lab): người chấm lô 2 cũng gán `dung`. Hai người chấm mù đều bỏ sót, khớp với nhận định `sai` và `da_cu` dễ bị đếm thiếu.
- 2 câu còn lại: một câu lô 1 gán `lac_de`, lô 2 gán `dung`; một câu lô 1 gán `khong_chac`, lô 2 gán `sai`.

Lô 2 được chấm tay bằng công cụ, trung vị 20 giây mỗi câu. Một file lô 2 có trước đó gán đủ 249 câu, nhưng mọi nhãn cùng một giờ gán và ghi chú lặp theo mẫu, tức không qua thao tác chấm tay trong công cụ, nên không dùng.

**Lượt 1 · chấm mù.** Lệnh: `python evidence/merge_labels.py evidence/discord/raw-nhan-lo-1-G1.json`. Đầu vào là một file nhãn: lô 1, một người chấm, xong 249/249 câu của lô (20 câu chung + 229 câu riêng), tức 249/478 câu của tập chấm. Vì lô đã xáo, 249 câu này là mẫu ngẫu nhiên của tập chấm. Output của script:

| Nhãn | x / n | % |
|---|---|---|
| Đúng | 171/249 | 69% |
| Sai | 6/249 | 2% |
| Lạc đề | 11/249 | 4% |
| Đã cũ | 0/249 | 0% |
| Không trả lời | 43/249 | 17% |
| Không chắc | 18/249 | 7% |

Trong 188 câu chấm được đúng sai: 17 câu không dùng được (9%).

Khoảng tin cậy 95% (Wilson), tính thêm ngoài script: không dùng được 17/188 là 6–14%; không trả lời 43/249 là 13–22%.

**Đối chiếu bằng AI.** Claude Code (4 agent, mỗi agent khoảng 62 câu) chấm mù lại 249 câu theo đúng luật trên. Agent không thấy nhãn người, chỉ được đối chiếu với ba file thông báo, thông báo chung và diễn đàn hỏi đáp, tính tin đăng trước giờ hỏi. Người và AI trùng 72/249 câu (29%, kappa 0,12). Phần lớn chỗ lệch là do độ khắt khe: 100 câu người gán `dung` thì AI gán `khong_chac`, vì ba file kia không nhắc tới điều đó; người chấm là học viên trong khoá nên biết thêm portal và LMS. `khong_tra_loi` trùng nhiều nhất (22 câu), `lac_de` gần như không trùng (1 câu). Bốn agent khắt khe không đều nhau (mỗi phần có 8–16 câu `dung`). Nhãn AI không dùng làm kết quả; file ở máy: `evidence/discord/raw-doi-chieu-agent-lo-1.json`.

**Lượt 2 · chấm lại.** Có 14 câu người gán `dung` mà AI gán `sai` (11) hoặc `da_cu` (3) và chỉ ra được tin đăng trước giờ hỏi. Người chấm lô 1 xem lại 14 câu này cùng căn cứ và đổi cả 14 theo AI. Trong 14 câu, 7 câu đã được đọc lại đối chiếu với nguồn (trong phiên Claude Code). Ví dụ: ba câu hỏi về runner ngày 20–25/11, Kute trả lời chỉ đội trưởng cấu hình được, trong khi bài hỏi đáp trên diễn đàn ngày 17/11 ghi mọi thành viên đều cấu hình được. Lệnh: `python evidence/merge_labels.py evidence/discord/raw-chamlai-lo-1-G1.json` (file này giữ nhãn cũ ở trường `label_mu`):

| Nhãn | x / n | % |
|---|---|---|
| Đúng | 157/249 | 63% |
| Sai | 17/249 | 7% |
| Lạc đề | 11/249 | 4% |
| Đã cũ | 3/249 | 1% |
| Không trả lời | 43/249 | 17% |
| Không chắc | 18/249 | 7% |

Trong 188 câu chấm được đúng sai: 31 câu không dùng được (16%; KTC 95% Wilson 12–22%, tính ngoài script).

Lượt 2 chỉ xem lại một chiều (người `dung` → AI `sai`/`da_cu`). Còn 3 câu chiều ngược lại chưa xem lại: người gán `sai`/`lac_de`, AI gán `dung` có căn cứ. Nếu cả 3 cũng đổi theo AI thì tỉ lệ là 28/188 (15%). Một trong 14 câu dựa vào tin chào mừng ngày 05/11, nhưng tin này bị sửa lúc 15:52 ngày 08/11, sau giờ hỏi của câu đó (14:59 cùng ngày). Vì vậy chưa chắc lúc hỏi đã có nội dung ấy.

Giới hạn. Phần này viết sau khi đọc lại nhãn và giờ gán, không nằm trong luật viết trước:
- Lô 2 chỉ có 21 câu, nên số gộp gần như là số của lô 1 do một người chấm; độ trùng chỉ đo trên 20 câu. Lượt 2 chỉ xem lại 14 câu do AI chỉ ra, không chấm lại cả lô.
- Chấm nhanh: 249 câu trong khoảng 96 phút (không tính một quãng nghỉ 7 giờ). Trung vị 6 giây giữa hai lần gán, nhanh dần từ 13 giây ở 62 câu đầu xuống 4 giây ở 63 câu cuối. Ở tốc độ này khó đối chiếu từng câu với thông báo chính thức tại thời điểm hỏi như luật yêu cầu, nên `sai` và `da_cu` dễ bị đếm thiếu; lượt 2 cho thấy đúng như vậy với 14 câu. Các câu AI chỉ gán `khong_chac` thì không ai xem lại, nên `sai` có thể vẫn còn thiếu.
- Cách chấm có thể đã đổi theo thời gian: 8/11 câu `lac_de` nằm trong 62 câu đầu, chỉ 3 câu trong 187 câu sau (kiểm định Fisher, p ≈ 0,001; 2 trong 8 câu là câu menu ở gạch dưới). Lô đã xáo nên tỉ lệ thật không đổi theo thứ tự chấm. Mốc 62 câu chọn sau khi đã xem dữ liệu, cùng khoảng mười phép chia khác, nên đây là gợi ý, không phải kiểm định.
- 14 câu có câu hỏi chỉ là lựa chọn trên menu ("1", "2 và 3"…). Công cụ không hiện menu nên người chấm không biết câu hỏi thật: 12 câu thành `khong_chac`, 2 câu thành `lac_de`. Bỏ 14 câu này thì tỉ lệ không dùng được là 15/186 (8%). Tập chấm lẽ ra phải loại các câu này hoặc hiện kèm menu.
- 43 câu `khong_tra_loi`. Nhãn này rộng hơn kiểu K ở `frozen-kute.md` vì gồm cả "chỉ chỗ để tự tìm": regex kiểu K chỉ bắt 14/43 câu. Đọc lại 12 trong 29 câu còn lại: phần lớn là Kute chỉ sang portal, ticket hoặc phòng ban của trường, nhiều câu hỏi về thông tin riêng (điểm danh, XP). Hai cách đếm khác định nghĩa nên không so thẳng với số "Kute bó tay" (A + T + K).

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
- Chưa đo thời gian chờ từ lúc Kute gọi Mod tới lúc có người trả lời, và mới chấm đúng sai 250/478 câu Kute có trả lời (mục 3g); người thứ hai chỉ chấm 21 câu.
- Hai phép đếm theo từ khoá (thời điểm, thông tin riêng) bỏ sót câu không dùng đúng cụm từ.

→ Kiểm lại bằng phỏng vấn ≥3 học viên: lần gần nhất hỏi Kute mà không được trả lời thì bạn làm gì, chờ bao lâu.
