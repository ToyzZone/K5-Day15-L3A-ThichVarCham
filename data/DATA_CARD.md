# Data card — dữ liệu bản chạy thử dùng

> Bản đầu ở CP2. Mọi dataset dưới đây là `synthetic`, nhóm tự dựng. **Không phải bằng chứng pain.**
> Không có giá trị nào chép từ portal hay Discord thật của khoá. Chỉ **cấu trúc** của portal giả là dựng theo portal thật, sau khi một thành viên xem bằng tài khoản của mình ngày 27/11 (danh sách mục ở ticket "Liệt kê các mục trên portal của khoá" trên repo).

## Dataset 1 · `data/portal_gia.json` — portal giả

| | |
|---|---|
| Dùng để làm gì | nguồn cho công cụ `tra_portal` · đáp án của các câu thử về thông tin riêng |
| Từ đâu | nhóm tự viết (có Claude Code hỗ trợ) |
| Xử lý những bước gì | dựng 3 hồ sơ học viên giả HV001–HV003, mỗi hồ sơ 6 mục: xp, diem_danh, daily_standup, gate, deadline, coach_phu_trach |
| Số dòng / số đoạn | 3 hồ sơ |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Chỉ 3 học viên, mỗi mục vài dòng. Thiếu lịch sự kiện, lịch sử XP và điểm mentor duty của đội. Tên role XP lấy theo nhãn hệ thống của portal thật |

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
| Giới hạn | Giờ và ngày là dựng, không phải hạn thật của khoá. Chưa có trường hợp hai thông báo mâu thuẫn nhau |

## Dataset 4 · `data/kho_kien_thuc.json` — kho kiến thức ban đầu

| | |
|---|---|
| Dùng để làm gì | nguồn cho công cụ `tra_kho_kien_thuc` |
| Từ đâu | nhóm tự viết |
| Xử lý những bước gì | 4 mục, mỗi mục có mã, câu hỏi, câu trả lời, nguồn, người duyệt, ngày duyệt, trạng thái. Mục K03 cố ý chứa thông tin cũ để thử loại đề xuất "sửa" |
| Số dòng / số đoạn | 4 |
| Phiên bản / ngày lấy | 27/11/2026 |
| Nhãn | `synthetic` |
| Giới hạn | Kho rất nhỏ nên tra bằng so khớp từ khoá vẫn đủ; kho thật sẽ cần cách tra tốt hơn |

**Cách sinh:** viết tay bằng script một lần (không có seed vì không sinh ngẫu nhiên). **Người kiểm:** chưa có người thứ hai kiểm từng dòng; cần làm trước CP3.
