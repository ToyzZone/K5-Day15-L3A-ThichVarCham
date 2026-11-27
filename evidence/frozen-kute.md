# Kute bị "đóng băng kiến thức": bằng chứng từ kênh hỏi trợ lý

> Phân loại do AI (Claude Code) đọc và gán ngày 27/11/2026, **chưa có người chấm lại**. Những số ghi "script" thì chạy lại được bằng công thức ở mục 3. Những số ghi "AI đọc" là nhãn gán tay, có danh sách từng lượt trong file ở máy `evidence/discord/raw-dong-bang-2026-11-27.md` (đã gitignore).
> Trích dẫn nguyên văn tối đa 2 câu, đã bỏ tên và lời gọi `@Kute`. `ma` là 6 số cuối mã tin Kute trả lời. Giờ là giờ Việt Nam.

## 1. Dữ liệu

- **Kênh hỏi trợ lý và tạo ticket** (05–27/11/2026): 848 lượt Kute trả lời một tin của người. Đây là mẫu số chung, giống `evidence/data-mining.md`.
- **Nguồn để đối chiếu**, dùng để biết câu trả lời đã có ở đâu và từ lúc nào:
  - kênh thông báo Build Phase: 27 tin;
  - kênh thông báo của lớp học: 11 tin;
  - diễn đàn hỏi-đáp: 18 bài, 64 tin.

  Vai trò của người trả lời trên kênh và trên diễn đàn **chưa xác minh**. File này chỉ ghi "có người trả lời", không gọi họ là Mod hay coach, và không khẳng định câu trả lời đó đúng.

## 2. Các kiểu và số đếm

Năm kiểu đầu được đếm bằng script và loại trừ nhau: mỗi lượt thuộc đúng một kiểu. Kiểu S do AI đọc, chỉ xét trong các lượt "có trả lời". Ba kiểu B, C, D chồng lên các kiểu trên, nên **không cộng** vào tổng.

| Kiểu | Định nghĩa | Đếm bằng | Số |
|---|---|---|---|
| **A** · chỉ gọi Mod | `kute_loai = chuyen_mod` và tin của Kute **bắt đầu** bằng `@Mod`, chỉ có một câu kiểu "chưa đủ thông tin, nhờ Mod" | script | **43/848** |
| ↳ A là câu hậu cần chung | trong 43 lượt A, câu hỏi là việc hậu cần chung mà một mục kho cập nhật trả lời được. Không tính lời chào, chọn số trên menu, thông tin riêng, câu mơ hồ | AI đọc | **30/43** |
| **T** · timeout | `kute_loai = loi_timeout` | script | **8/848**. 6 lượt là câu hỏi thật (4 về track, 2 về việc nội bộ đội) |
| **K** · tự nhận không có thông tin | không thuộc A hay H; 400 ký tự đầu câu trả lời khớp regex ở mục 3. Đã loại tay 2 lượt bắt nhầm | script + lọc tay | **38/848** |
| **H** · chỉ hỏi lại | `kute_loai = co_tra_loi` và câu trả lời có cụm `mô tả rõ hơn` (Kute đưa danh sách lựa chọn) | script | **148/848** |
| **S** · trả lời sai, lạc đề hoặc đã cũ | Kute có trả lời, nhưng trái với thông báo chính thức, lạc sang chủ đề khác, hoặc không còn đúng ở thời điểm hỏi | AI đọc, tìm có chủ đích | **≥15** (cận dưới). Chưa đọc hết 440 lượt có trả lời. Trong đó có 69 lượt `chuyen_mod` vừa trả lời vừa nhắc Mod: đã đọc đoạn quanh `@Mod` của cả 69 lượt, đọc toàn văn khoảng 20 |
| **B** · câu phụ thuộc thời điểm | câu hỏi khớp regex thời điểm ở mục 3. Kute không đưa được thông tin đúng lúc: bó tay, chỉ hỏi lại, chỉ chỗ xem chung chung, hoặc trả lời cũ | regex chọn tập, AI đọc | **21/90** |
| **C** · lặp câu trả lời đã lỗi thời, hoặc bị học viên báo sai | **C1**: lặp nguyên một câu trả lời dù tình hình đã khác (mẫu số: 108 lượt thuộc nhóm "câu trả lời lặp ≥3 lần"). **C2**: học viên phản hồi ngay rằng câu trả lời sai hoặc không dùng được | AI đọc | **C1 4/108 · C2 3**. C2 không có mẫu số đầy đủ: tìm trong 67 tin reply thẳng vào Kute và trong ngữ cảnh ngay sau đó |
| **D** · đã có người trả lời mà Kute vẫn bó tay | một tin đăng **trước** lượt hỏi, trên kênh hoặc diễn đàn, đã trả lời đúng điều được hỏi, nhưng Kute vẫn ra A, T hoặc K | AI đọc toàn bộ khoảng 20 tin người trả lời người trên kênh và 18 bài diễn đàn | **6 lượt, 5 chủ đề** (3 lượt nhờ kênh, 3 nhờ diễn đàn). Đã loại 3 lượt cùng chủ đề nhưng tin trước không trả lời đúng ý được hỏi |

**"Kute bó tay"** gồm A + T + K = **89/848 (10%)**: gọi Mod thuần, timeout, hoặc tự nói không có thông tin. Đây là số chính.

Kiểu H (148 lượt chỉ hỏi lại) để riêng. Nhiều lượt hỏi lại là hợp lý, và lượt kế tiếp có câu trả lời. Nếu vẫn cộng H thì A + T + K + H = 237/848 (28%); bỏ 171 lượt khung tạo ticket (học viên tự xin ticket) thì là 237/677 (35%).

Kiểu S tính riêng: Kute có trả lời nhưng câu trả lời không dùng được.

**Khớp với `data-mining.md` mục 3c:** trong 112 lượt có `@Mod`, chỉ 43 lượt là gọi Mod thuần (kiểu A); 69 lượt còn lại Kute đã trả lời rồi mới nhắc Mod. `spec.md` §2 và canvas đã dùng số đã đính chính.

## 3. Công thức chạy lại

```python
# r là một dòng của raw-cap-2026-11-27.jsonl; xét theo thứ tự
KTT = re.compile(r"(không|chưa) có (đủ )?(thông tin|dữ liệu|dữ kiện|lịch)|không có .{0,40}trong (dữ liệu|tài liệu|FAQ)"
                 r"|(không|chưa) thấy đề cập|chưa nắm|ngoài hiểu biết|chưa có quy định cụ thể|không có nội dung", re.I)
def kieu(r):
    k = r["kute_tra_loi"]
    if r["kute_loai"] == "menu_ticket": return "M"
    if r["kute_loai"] == "loi_timeout": return "T"
    if r["kute_loai"] == "chuyen_mod" and k.lstrip().startswith("@Mod"): return "A"
    if r["kute_loai"] == "co_tra_loi" and "mô tả rõ hơn" in k: return "H"
    if KTT.search(k[:400]) and r["ma"] not in {"176947", "615795"}: return "K"   # 2 lượt regex bắt nhầm, loại tay
    return "TL"
# Kết quả: M 171 · TL 440 · H 148 · A 43 · K 38 · T 8 (tổng 848)

# Tập B: câu hỏi (không tính menu_ticket) khớp regex dưới → 90 lượt
THOI_DIEM = r"hôm nay|hôm qua|ngày mai|tối nay|sáng nay|chiều nay|sáng mai|tuần này|tuần sau|tuần tới|tuần kế|bây giờ|hiện tại|hiện đã" \
            r"|mấy giờ|link zoom|khi nào|bao giờ|lịch|deadline|hạn|chưa thấy|đã có chưa|có chưa|record|thông báo|tbao|tkb" \
            r"|còn .{0,20}(không|ko|k)\b|mở chưa|đã mở|lùi|gia hạn"
# Mẫu số C1: lượt co_tra_loi có 60 ký tự đầu câu trả lời (bỏ mã người, gộp khoảng trắng, chữ thường) trùng ≥3 lượt → 108 lượt
```

## 4. Mười ví dụ

| # | `ma` · ngày | Kiểu | Học viên hỏi (nguyên văn) | Kute đáp | Vì sao là bằng chứng |
|---|---|---|---|---|---|
| 1 | `398147` · 09/11 | A, D | "office hour học qua đâu" | Chỉ gọi Mod ("chưa có đủ thông tin") | Ngày 07/11 đã có người trả lời trên kênh: Office Hour tổ chức trên Discord. Thông báo lúc 15:53 ngày 09/11 nêu giờ và kênh Office Hour Stage. |
| 2 | `404171` · 26/11 | A, D | "có quy định về URL Production không" | Chỉ gọi Mod | Diễn đàn đã trả lời ngày 20/11 (URL phải chứa mã đội). Chính Kute trả lời quy định tên miền 3 lần trong 23–25/11. |
| 3 | `753199` · 16/11 | T | "Các track của chương trình gồm những track nào?" | "Xin lỗi, request timeout." | Câu về track được hỏi 15 lượt trong 09–25/11, chưa lượt nào nhận được danh sách track. |
| 4 | `837757` · 27/11 | K | "Kick off hackathon là làm gì? Có thi chưa?" | Nói dữ liệu FAQ không có thông tin về sự kiện này | Câu về hackathon được hỏi 6 lượt trong 23–27/11. Ba nguồn đã đọc không có thông báo chi tiết, nên chưa chứng minh được là thông tin đã có (mục 5b). |
| 5 | `430700` · 11/11 | A, D | "cái link trong cái mentor duty là link gì" | Chỉ gọi Mod | Cùng buổi sáng, Kute trả lời được câu này 3 lần. Trên diễn đàn có người trả lời 1 phút trước lượt hỏi. |
| 6 | `221272` · 19/11 | S, B, C1 | "có còn đổi được đề tài nưa không" | "Còn trong hạn chọn đề thì đổi trực tiếp ở tab Đề tài…" | Thông báo 09/11: hạn chọn đề là 23:59 14/11, sau đó BTC không hỗ trợ. Kute lặp câu đã dùng từ 09/11. |
| 7 | `557631` · 11/11 | S, B, C1 | "bây giờ còn hạn trao đổi thành viên trong nhóm không vậy" | "Bạn bấm Rời đội trên nền tảng Phoenix, sau đó tìm và tham gia đội mới." | Thông báo 05/11: sau 13:00 08/11 không tự lập hay vào đội được nữa. Ngày 08/11, chính Kute từng trả lời là đội đã cố định. |
| 8 | `503667` · 17/11 | S | "tôi cần nộp lại bài lab day 09 vì nộp nhầm link" | Hướng dẫn nộp dự án Demo Day | Lạc đề; cùng câu này được dùng cho 4 câu hỏi về lab trong 07–18/11. Thông báo lớp học 07/11 nói nộp lại được nhiều lần. |
| 9 | `724207` · 12/11 | B | "Link zoom cho buổi Lecture (Lớp học) hom nay" | Liệt kê các chỗ có thể tìm link | Link buổi lý thuyết ngày 12/11 đã đăng ở kênh thông báo lớp học tối 10/11. |
| 10 | `785755` · 26/11 | C2 | "tôi nộp gate 2 đúng hạn mà không được cộng xp" | "Mentor cần thời gian review và chấm PASS cho đội thì hệ thống mới cộng XP nhé." | Học viên trả lời ngay: "đã thấy pass gate 2 rồi mà". Câu trả lời lặp này (4 lần, 15–26/11) không dùng được cho trường hợp đã PASS. |

## 4b. Hạn Gate 3: Kute và portal nói hai ngày khác nhau

- **Kute:** 13 lượt từ 09/11 đến 00:45 ngày 27/11 nêu hạn Gate 3 là **23:59 ngày 29/11**; không lượt nào nêu ngày khác (đếm bằng script: câu trả lời của Kute có "Gate 3" hoặc "G3" đi cùng "29/11"). Ví dụ ngày 25/11: Kute nhắc "chỉ còn 4 ngày nữa là đến hạn chót nộp Gate 3".
- **Portal của khoá:** đội trưởng xem ngày 27/11, hạn Gate 3 là **23:59 ngày 06/12**.
- Ba kênh đã đọc (thông báo Build Phase, thông báo lớp học, diễn đàn hỏi-đáp) không có tin nào nhắc hạn Gate 3.

Điều biết chắc: ngày 27/11, Kute và portal lệch nhau một tuần về một hạn nộp, và không có thông báo nào trên Discord giúp học viên biết bên nào đúng. Điều **chưa biết**: hạn được ghi trên portal từ khi nào, nên chưa nói được những lượt nào của Kute sai ngay lúc trả lời. Đây là ví dụ rõ nhất cho việc kho của Kute không tự cập nhật theo nguồn chính thức.

## 5. Thông tin Kute lẽ ra phải trả lời được

Mỗi dòng là một điều học viên cần biết. Câu hỏi được gom vào mục bằng regex rồi AI đọc lọc tay; danh sách `ma` của từng mục nằm trong file ở máy.

**Các cột:**
- **Lượt hỏi**: số lượt hỏi đúng mục đó.
- **Bó tay**: A + T (gọi Mod thuần hoặc timeout).
- **K**: số lượt Kute nói không có thông tin.
- **S**: số lượt trả lời sai, lạc đề hoặc đã cũ.

**Mức căn cứ cho thấy câu trả lời đã tồn tại lúc hỏi:**
- **Mức 1:** trước lượt hỏi đã có người trả lời đúng ngay trên kênh hoặc trên diễn đàn. Chỉ ghi ngày.
- **Mức 2:** chính Kute trả lời được ở một lượt khác, trước hoặc sau. Tức là lúc trả lời được, lúc bó tay.
- **Mức 3 (đã chứng minh):** thông tin nằm trong một thông báo chính thức đăng trước lượt hỏi.
- **Mức 3 (suy đoán):** chỉ đoán là thông tin có ở nguồn chính thức, dữ liệu hiện có không chứng minh được.

### 5a. Có căn cứ: 21 mục · 121 lượt hỏi · bó tay 23 (A 21, T 2) · K 3 · S 13

Mức 2 chỉ được tính khi Kute đưa thông tin cụ thể của khoá, không tính câu trả lời chung chung.

| Mục thông tin | Lượt hỏi | Bó tay | K | S | Ngày hỏi | Căn cứ |
|---|---|---|---|---|---|---|
| Office Hour là gì, diễn ra ở đâu, mấy giờ | 9 | 3 | 0 | 0 | 07/11–09/11 | Mức 1 (kênh, 07/11) · Mức 2 (08/11, 09/11) · Mức 3 đã chứng minh (thông báo 09/11 15:53, trước lượt 19:30) |
| Repo nhóm để private có cần chuyển public để nộp, để mentor chấm | 4 | 2 | 0 | 1 | 11/11–22/11 | Mức 2 (13/11, 8 phút trước lượt gọi Mod đầu tiên) |
| Cách xin nghỉ buổi học (gửi email cho ai) | 20 | 2 | 0 | 0 | 05/11–26/11 | Mức 2 (05/11, 06/11) |
| Ô Link trong report mentor duty điền gì | 6 | 2 | 0 | 0 | 11/11 | Mức 2 (ba lần trong cùng buổi sáng, xen giữa hai lượt gọi Mod) · Mức 1 (diễn đàn 11/11) |
| Thủ tục xin bảo lưu sang khoá sau | 4 | 2 | 0 | 0 | 10/11–11/11 | Mức 2 (10/11) |
| Thắc mắc nội bộ đội thì liên hệ ở đâu | 4 | 2 (T) | 0 | 0 | 12/11–16/11 | Mức 2 (09/11, 12/11, 15/11) · Mức 3 đã chứng minh (thông báo lớp học 04/11) |
| Điểm bài lab: ai chấm, khi nào có, xem ở đâu | 5 | 1 | 0 | 1 | 12/11–15/11 | Mức 2 (12/11, 13/11) · Mức 3 đã chứng minh (thông báo lớp học 12/11) |
| Điều kiện được điểm danh workshop (email, tên Zoom, tương tác) | 6 | 1 | 0 | 0 | 06/11–25/11 | Mức 3 đã chứng minh (thông báo 06/11, trước lượt gọi Mod) · Mức 2 (06/11) |
| Đổi `runs-on` sang self-hosted khi CI lỗi billing, dùng runner riêng | 6 | 1 | 0 | 0 | 15/11–23/11 | Mức 2 (23/11, 5 tiếng sau lượt gọi Mod). Cần người xem: lượt gọi Mod hỏi riêng nhãn `runs-on` cho runner tự cài |
| Hạn các gate, khoảng cách giữa các gate | 5 | 1 | 0 | 0 | 10/11–16/11 | Mức 2 (từ 09/11) |
| Quy định tên miền, URL production | 5 | 1 | 0 | 0 | 23/11–26/11 | Mức 1 (diễn đàn 20/11) · Mức 2 (23/11, 25/11) |
| Office Hour có điểm danh, có tính XP không | 4 | 1 | 0 | 0 | 09/11 | Mức 2 (09/11 sáng, trước lượt gọi Mod buổi chiều) · Mức 1 (kênh 09/11 tối) |
| Daily standup để làm gì | 4 | 1 | 0 | 0 | 08/11–09/11 | Mức 2 (08/11, 7 phút trước lượt gọi Mod) |
| Ai duyệt đề tài tự đề xuất | 4 | 1 | 0 | 0 | 10/11–12/11 | Mức 3 đã chứng minh (thông báo 09/11; chỉ phần "ai duyệt") · Mức 2 (10/11) |
| Cách tính hạn nộp gate (lần nộp đầu hay lần sửa) | 4 | 1 | 0 | 0 | 15/11–16/11 | Mức 2 (15/11; 16/11, 2 phút trước lượt gọi Mod) |
| Buổi mentor duty họp chung nhiều đội hay riêng một đội | 2 | 1 | 0 | 0 | 11/11 | Mức 2 (11/11, có rào đón) |
| Nộp bài lab trên LMS: nộp, nộp lại khi nhầm, commit thêm sau khi nộp | 15 | 0 | 1 | 6 | 06/11–21/11 | Mức 3 đã chứng minh (thông báo lớp học 07/11, 12/11) · Mức 1 (diễn đàn 12/11) · Mức 2 (07/11) |
| Có được đổi đội sau hạn ghép đội | 4 | 0 | 0 | 3 | 08/11–13/11 | Mức 3 đã chứng minh (thông báo 05/11) · Mức 2 (08/11) |
| Wifi ở trường đăng nhập thế nào | 3 | 0 | 2 | 0 | 05/11–19/11 | Mức 1 (kênh 05/11; vai trò người trả lời chưa xác minh, câu trả lời chưa kiểm đúng sai) |
| Nộp lab muộn có bị trừ điểm không | 4 | 0 | 0 | 1 | 07/11–22/11 | Mức 3 đã chứng minh (thông báo lớp học 07/11) · Mức 1 (diễn đàn 12/11) |
| Còn đổi đề tài được không (sau hạn chọn đề) | 3 | 0 | 0 | 1 | 09/11–19/11 | Mức 3 đã chứng minh (thông báo 09/11) |

**Mục được chứng minh nhờ từng nguồn.** Một mục có thể nhờ nhiều nguồn. "Chỉ nhờ" nghĩa là bỏ nguồn đó đi thì mục rơi xuống bảng 5b.

| Nguồn | Có căn cứ từ nguồn này | Chỉ nhờ nguồn này |
|---|---|---|
| Kênh thông báo Build Phase | 5 mục | 1 |
| Kênh thông báo lớp học | 4 mục | 0 |
| Diễn đàn hỏi-đáp | 4 mục | 0 |
| Người trả lời trên kênh hỏi trợ lý | 3 mục | 1 |
| Kute tự trả lời được ở lượt khác (mức 2) | 18 mục | 8 |

### 5b. Chưa chứng minh được: 22 mục · 69 lượt hỏi · bó tay 13 (A 9, T 4) · K 32

Các mục dưới đây chỉ có mức 3 suy đoán. Không mục nào được chuyển lên bảng 5a.

| Mục thông tin | Lượt hỏi | Bó tay | K | Ngày hỏi | Cần thêm dữ liệu gì để chứng minh |
|---|---|---|---|---|---|
| Các track của chương trình (số lượng, nội dung, khác nhau) | 15 | 4 (T) | 3 | 09/11–25/11 | Tài liệu track: slide hoặc bản ghi buổi định hướng 15/11, kênh tài nguyên, email nguyện vọng track. Thông báo 09/11 chỉ nêu ví dụ một track. |
| Thẻ học viên dùng làm gì, khi nào có | 5 | 2 | 2 | 10/11–11/11 | Thông báo hoặc email nhập học về thẻ, từ 05/11 |
| Lịch học lý thuyết, thực hành sắp tới | 6 | 1 | 2 | 05/11–14/11 | Email lịch học. Thông báo lớp học 04/11 nói lịch gửi qua email |
| Role Active Builder là gì, làm sao được cấp | 2 | 1 | 1 | 08/11–18/11 | Ảnh trang Tiến độ trên portal, hoặc thông báo về role theo XP. Trong thông báo, tên role đã bị che |
| Tài khoản GitHub bị gắn cờ, bị khoá khi đăng nhập Phoenix | 3 | 1 | 0 | 05/11–06/11 | Có người trả lời trên kênh 05/11, nhưng sau lượt gọi Mod duy nhất. Cần hướng dẫn onboarding trước 05/11 tối |
| Tổng XP tối đa của chương trình | 2 | 1 | 0 | 08/11 | Bảng cách tính XP trên portal |
| Mentor, coach có đọc daily standup không | 1 | 1 | 0 | 08/11 | Hướng dẫn cho mentor, hoặc câu trả lời của coach |
| Daily standup có phải nộp Chủ nhật không | 1 | 1 | 0 | 09/11 | Lịch standup trên portal. Kute nói "mỗi ngày" nhưng chưa từng nói rõ Chủ nhật |
| Bảng xếp hạng XP xem ở đâu | 1 | 1 | 0 | 13/11 | Ảnh portal. Lưu ý: trợ lý của nhóm không trả lời thứ hạng |
| Cơ sở vật chất, dịch vụ của trường (chỗ nghỉ trưa, phòng nghỉ, gym, mang cơm, giá trọ, liên hệ IT, email trường) | 8 | 0 | 8 | 05/11–24/11 | Sổ tay của trường. Gộp 7 việc nhỏ; có thể nằm ngoài phạm vi kho của BTC |
| Hackathon là gì, kick-off khi nào | 6 | 0 | 3 | 23/11–27/11 | Thông báo hackathon (kênh khác hoặc email), khoảng từ 20/11. Thông báo lớp học 25/11 chỉ nhắc tên |
| Phòng học theo mã phòng nằm ở đâu | 3 | 0 | 3 | 05/11–13/11 | Sơ đồ campus. Thông báo lớp học 03/11 chỉ nêu tên kênh theo phòng |
| Bài kiểm tra tuần 6 (có không, thi gì, có theo track không) | 4 | 0 | 1 | 14/11–27/11 | Quy chế đánh giá. Diễn đàn 05/11 chỉ xác nhận có bài kiểm tra và kiến thức trải 6 tuần đầu; bài FAQ 26/11 nhắc "thi kiến thức" nhưng đăng sau lượt hỏi |
| Lập đội có cần cùng lớp, cùng level, cùng track | 2 | 0 | 1 | 05/11 | Diễn đàn trả lời 05/11, nhưng 5 tiếng sau lượt hỏi Kute |
| Được vắng tối đa bao nhiêu buổi workshop | 2 | 0 | 1 | 08/11–09/11 | Quy chế chuyên cần |
| Đổi tên đội sau hạn lập đội | 1 | 0 | 1 | 08/11 | Hướng dẫn Phoenix hoặc câu trả lời của coach |
| BTC xử lý ticket trong bao lâu, khung giờ nào | 1 | 0 | 1 | 16/11 | Quy trình ticket của BTC |
| Lịch nghỉ lễ, Tết | 1 | 0 | 1 | 10/11 | Lịch năm học |
| Ngày diễn ra Showcase | 1 | 0 | 1 | 09/11 | Thông báo trước 09/11. Thông báo mở build-showcase đăng ngày 25/11 |
| Có hỗ trợ kinh phí phần cứng để demo không | 1 | 0 | 1 | 07/11 | Quy định của BTC |
| Mentor chọn đề tài hay hệ thống phân ngẫu nhiên | 1 | 0 | 1 | 12/11 | Quy trình phân đề |
| Mỗi lần daily standup được bao nhiêu XP | 2 | 0 | 1 | 08/11 | Bảng cách tính XP trên portal |

## 6. Giới hạn

- **Ai gán nhãn:** AI gán, chưa có người chấm lại. Kiểu S, B, C, D và việc gom mục là phán đoán khi đọc. S là cận dưới, vì AI chỉ tìm có chủ đích trong các nhóm câu trả lời lặp và các chủ đề có nguồn chính thức, chưa đọc hết 440 lượt có trả lời.
- **Mức 2 chưa chắc là do đóng băng.** Kute lúc trả lời được, lúc bó tay; lỗi có thể nằm ở cách tra hoặc ở model, không phải do kho đóng băng.
- **Kho của Kute có thể đã được bổ sung tay vài lần.** Câu trả lời về tên miền từ 23–25/11 có nội dung giống câu trả lời trên diễn đàn ngày 20/11. Vì vậy "đóng băng" ở đây nên hiểu là kho không tự cập nhật từ câu trả lời mới, không phải là không bao giờ đổi.
- **Người trả lời:** vai trò chưa xác minh. Câu trả lời về wifi và gym do người có màu tên thường gửi, chưa kiểm đúng sai.
- **Regex bỏ sót** cách diễn đạt khác (K, B). Câu hỏi trong ticket và tin nhắn riêng không thấy được.
- **Kênh thông báo lớp học** (11 tin) được dùng thêm, không nằm trong mô tả dữ liệu ban đầu.
- **Hai lượt trùng `ma`:** đều là khung tạo ticket, không ảnh hưởng số đếm.
