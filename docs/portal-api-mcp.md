# Portal giả qua API và MCP — issue #57, #51

Chỉ dùng dữ liệu tổng hợp trong `data/portal_gia.json`. Không kết nối portal thật,
không dùng thông tin cá nhân hay ảnh chụp thật làm dữ liệu. Phần này chưa dựng giao
diện web theo ảnh tham khảo; giao diện là issue #58 và có thể dùng API bên dưới.

## Luồng dữ liệu

```text
Discord ID → runtime/accounts.json → mã hồ sơ giả (code xác minh)
→ MCP client qua stdio, _meta["kute/student_id"]
→ MCP server đổi mã hồ sơ thành token tương ứng
→ API /api/me/<mục> với Authorization: Bearer <token>
→ dữ liệu hồ sơ chủ token → code định dạng con số → DM cho người hỏi
```

Tool `tra_portal` chỉ có tham số `muc`, không nhận mã học viên, token hay URL.
MCP server chỉ chạy qua stdio như tiến trình con nội bộ; metadata là ngữ cảnh do
host tin cậy chèn, không phải cơ chế đăng nhập cho MCP server công khai. Không mở
server MCP này thành endpoint cho người dùng tùy ý truyền metadata.

## Chạy trên Windows PowerShell

Cài SDK trong môi trường dự án:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Terminal thứ nhất chạy API, tự tạo token lần đầu:

```powershell
.\.venv\Scripts\python.exe codebase/portal_api.py
```

API mặc định tại `http://127.0.0.1:8765`. Giữ terminal này mở.
Token được sinh ngẫu nhiên vào `runtime/portal_tokens.json`, mỗi hồ sơ giả một token,
không in ra terminal. Chạy lại không đổi token. Thư mục `runtime/` đã bị Git bỏ qua.
Nếu chỉ muốn chuẩn bị token mà chưa chạy API:

```powershell
.\.venv\Scripts\python.exe codebase/portal_api.py --init
```

Giữ cấu hình model/Discord hiện có trong `.env`; bổ sung nếu cần:

```dotenv
PORTAL_API_URL=http://127.0.0.1:8765
PORTAL_TOKENS_FILE=
```

`PORTAL_TOKENS_FILE` trống nghĩa là dùng `runtime/portal_tokens.json` trong repo.
Nếu đổi cổng API, chạy `portal_api.py --port 8766` và đổi URL cho khớp. Nếu triển
khai API trên máy khác, phải dùng HTTPS; HTTP không phải loopback sẽ bị chặn.

Tạo hoặc bổ sung `runtime/accounts.json` để ghép tài khoản Discord thử nghiệm:

```json
{
  "ID_DISCORD_HOC_VIEN_THU_1": "HV001",
  "ID_DISCORD_HOC_VIEN_THU_2": "HV002"
}
```

Thay khóa bằng ID thật của tài khoản dùng để thử, giữ giá trị là mã hồ sơ giả.
Không mượn chung hồ sơ cho nhiều người khi thử quyền riêng tư. Chưa liên kết thì
không đọc được portal; không tự dùng hồ sơ mặc định. Việc ánh xạ chỉ do người vận
hành sửa file trên máy, không nhận từ câu hỏi hoặc lệnh của learner.

Terminal thứ hai chạy bot:

```powershell
.\.venv\Scripts\python.exe codebase/discord_bot.py
```

Bot tự khởi chạy/đóng MCP server cho mỗi lượt tra, không cần terminal MCP thứ ba.
Mỗi lượt tạo session mới để tránh giữ nhầm danh tính giữa người hỏi. Cách này phù
hợp MVP, đổi lại có chi phí khởi động subprocess ở mỗi lượt. Các lệnh eval/simulate
cũng cần giữ API chạy và dùng Python đã cài SDK MCP. Không sửa file khung của BTC.

## API chỉ đọc

| Endpoint | Nội dung | Xác thực |
|---|---|---|
| `GET /health` | Trạng thái, đánh dấu dữ liệu giả | Không yêu cầu token, không trả hồ sơ |
| `GET /api/me` | Sáu mục của chủ token | Bearer token |
| `GET /api/me/xp` | XP và role | Bearer token |
| `GET /api/me/diem_danh` | Điểm danh workshop/mentor duty | Bearer token |
| `GET /api/me/daily_standup` | Trạng thái standup | Bearer token |
| `GET /api/me/gate` | Các trạng thái gate | Bearer token |
| `GET /api/me/deadline` | Deadline | Bearer token |
| `GET /api/me/coach_phu_trach` | Coach phụ trách | Bearer token |

Không có URL nhận mã học viên. Thiếu/sai token → 401; thêm query để chọn người khác
→ 400; đường dẫn hồ sơ khác → 404; POST/PUT/PATCH/DELETE → 405. API trả `Cache-Control:
no-store`, không ghi token hoặc nội dung hồ sơ vào access log.

## Thao tác thử trực tiếp

- Với hai tài khoản đã liên kết khác nhau, hỏi `!hoi XP của mình?` trong kênh chung.
  Kết quả gửi DM: dữ liệu giả hiện tại HV001 có 240 XP, HV002 có 410 XP.
- Hỏi điểm danh, standup, gate, deadline, coach phụ trách để xem sáu mục.
- Hỏi XP người khác: bot phải từ chối; tool không có tham số chọn người khác.
- Chặn DM rồi hỏi thông tin riêng: số liệu không được rơi ra kênh chung.
- Dừng API rồi hỏi: không đọc file JSON dự phòng; bot chuyển hướng hỗ trợ khi thiếu căn cứ.
- Chưa liên kết tài khoản: không trả số của hồ sơ khác.

Đã chạy thử trực tiếp HTTP cho 3 hồ sơ/sáu mục và MCP cho hai hồ sơ; thiếu/sai token
trả 401, query chọn người trả 400, đường dẫn hồ sơ khác trả 404. Chưa ghi nhận lượt
Discord thật của nhánh này. Không thêm/chạy bộ unit test theo yêu cầu người dùng,
dù mô tả issue gốc có yêu cầu unittest; cần nhóm xác nhận điều kiện bàn giao đó.

Tài liệu kỹ thuật: [SDK MCP chính thức, nhánh v1.x](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x).
Dependency giới hạn `<2` vì SDK v2 có thay đổi giao diện.
