# Data card — dữ liệu bản chạy thử dùng

> Bản đầu ở CP2. Mọi dataset dưới đây là `synthetic`, nhóm tự dựng. **Không phải bằng chứng pain.**
> **Không có dữ liệu cá nhân thật:** XP, điểm danh, trạng thái nộp bài, tên và mã học viên đều là bịa.
> **Có lấy theo portal thật** (một thành viên xem bằng tài khoản của mình ngày 27/11): cấu trúc các mục, nhãn hệ thống (tên gate G1–G3, tên role theo XP, tên trạng thái), và lịch chung của khoá (giờ hạn daily standup, mentor duty, hạn gate G3, ngày workshop). Đây là thông tin chung cho mọi học viên, không phải của riêng ai. Danh sách mục ở ticket "Liệt kê các mục trên portal của khoá" trên repo.

## Dataset 1 · `data/portal_gia.json` — portal giả

Cách phục vụ dữ liệu: API riêng xác thực token của từng hồ sơ; bot tra qua MCP stdio,
không đọc trực tiếp file này. Token sinh cục bộ tại `runtime/portal_tokens.json`, không
commit và không phải một phần dataset. Nội dung dữ liệu giả vẫn giữ nguyên.

| | |
|---|---|
| Dùng để làm gì | nguồn cho công cụ `tra_portal` · đáp án của các câu thử về thông tin riêng |
| Từ đâu | nhóm tự viết (có Claude Code hỗ trợ) |
| Xử lý những bước gì | dựng 3 hồ sơ học viên giả HV001–HV003, mỗi hồ sơ 6 mục: xp, diem_danh, daily_standup, gate, deadline, coach_phu_trach |
| Số dòng / số đoạn | 3 hồ sơ |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Chỉ 3 học viên, mỗi mục vài dòng. Thiếu lịch sự kiện, lịch sử XP và điểm mentor duty của đội. Tên gate, tên role XP, ngày workshop và giờ hạn lấy theo lịch chung của portal thật |

## Dataset 2 · `data/tai_khoan.json` — bảng ghép tài khoản Discord

| | |
|---|---|
| Dùng để làm gì | code tra vai trò và mã học viên của người gửi tin |
| Từ đâu | nhóm tự viết |
| Xử lý những bước gì | 3 học viên + 1 lab coach; một học viên có tên hiển thị "Lab Coach" để thử giả danh |
| Số dòng / số đoạn | 4 tài khoản |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Bản thật cần học viên tự liên kết tài khoản; ở đây ghép sẵn |

## Dataset 3 · `data/thong_bao.json` — thông báo chính thức

| | |
|---|---|
| Dùng để làm gì | nguồn cho công cụ `tra_thong_bao` · căn cứ để phát hiện mâu thuẫn |
| Từ đâu | nhóm tự viết, theo các loại hạn thấy trên portal (daily standup, mentor duty, gate) |
| Xử lý những bước gì | 3 thông báo, mỗi cái có mã, ngày, nội dung, link giả |
| Số dòng / số đoạn | 3 |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Câu chữ do nhóm viết; giờ và ngày lấy theo lịch chung thấy trên portal ngày 27/11, có thể đã đổi. Chưa có trường hợp hai thông báo mâu thuẫn nhau |

## Dataset 4 · `data/kho_co_dinh.json` và `data/kho_theo_khoa.json` — kho kiến thức hai bảng

| | |
|---|---|
| Dùng để làm gì | nguồn cho công cụ `tra_kho_kien_thuc` |
| Từ đâu | nhóm tự viết |
| Xử lý những bước gì | Bảng cố định (4 mục: K01, K03, K04, K05) giữ thông tin dùng chung qua các khoá. Bảng theo khoá (2 mục: K02, T01) giữ thông tin riêng của khoá đang chạy. Mục T01 ghi đè K05 để thử trường hợp hai bảng mâu thuẫn (hạn nộp lab). Mục K03 cố ý chứa thông tin cũ để thử loại đề xuất "sửa" |
| Số dòng / số đoạn | 6 |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Kho rất nhỏ nên tra bằng so khớp từ khoá vẫn đủ; kho thật sẽ cần cách tra tốt hơn |

**Cách sinh:** viết tay bằng script một lần (không có seed vì không sinh ngẫu nhiên). **Người kiểm:** tính đến 28/11 chưa có người thứ hai kiểm từng dòng.

## Dataset 5 · câu hỏi và câu trả lời thật trong `eval/benchmark.csv`

| | |
|---|---|
| Dùng để làm gì | đầu vào của 15 câu thử có `source` là `data_that` (trong B14–B30) |
| Từ đâu | kênh hỏi trợ lý và diễn đàn hỏi-đáp trên Discord của khoá (kênh mọi học viên đọc được), 05–27/11/2026 |
| Xử lý những bước gì | thay tên người gửi bằng mã lúc thu · che email, số điện thoại, mã học viên · chọn câu theo lưới input · trích nguyên văn tối đa 2 câu, bỏ tên · gán tài khoản giả của `data/tai_khoan.json` làm người gửi |
| Số dòng / số đoạn | 15 câu thử (10 câu hỏi của học viên, 5 câu trả lời trên kênh) lấy từ 848 lượt hỏi và 18 bài diễn đàn |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `real`, đã ẩn danh; bản thô không nằm trong repo |
| Giới hạn | Vai trò thật của người trả lời chưa xác minh. `expected` do nhóm đặt theo dữ liệu giả trong `data/`, không phải theo câu trả lời thật của khoá |
