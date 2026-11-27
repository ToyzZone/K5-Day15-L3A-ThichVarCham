# Nộp checkpoint

Dành cho người trong nhóm và các phiên agent. Cả bốn mốc nộp qua **một** Google Form của BTC:

- Xem form: https://docs.google.com/forms/d/e/1FAIpQLSdFqBLvf--GLbTUQ2vcFkkKDGsgT-LGT7oftBG_x8Pk-gMVwg/viewform
- Gửi câu trả lời (POST): https://docs.google.com/forms/d/e/1FAIpQLSdFqBLvf--GLbTUQ2vcFkkKDGsgT-LGT7oftBG_x8Pk-gMVwg/formResponse

## Luật của nhóm

- **Chỉ gửi khi đội trưởng nói gửi.** Soạn nội dung, đưa đội trưởng đọc, rồi mới gửi.
- Mọi con số trong form phải có trong repo (file kết quả, script đếm). Không ghi số chưa đo.
- Link nộp phải mở được ở cửa sổ ẩn danh.
- Gửi sai thì gửi lại một câu trả lời nữa, mở đầu ô cuối bằng "[BẢN SỬA của lần nộp lúc HH:MM: sửa gì]".

## Tình trạng

| Mốc | Hạn | Tình trạng |
|---|---|---|
| CP1 | 17:00 Thứ Sáu 27/11 | đã nộp |
| CP2 | 19:30 Thứ Sáu 27/11 | đã nộp 19:07, bản sửa 19:28 (đính chính một số đếm; chuẩn "đạt" không đổi) |
| CP3 | 10:00 Thứ Bảy 28/11 | chưa nộp |
| CP4 | 14:30 Thứ Bảy 28/11 | chưa nộp |

## Các ô của form

Ô chung (trang đầu), mốc nào cũng điền:

| Ô | Mã | Giá trị |
|---|---|---|
| Phòng thi | `entry.15831452` | `H210` |
| Tên đội | `entry.985403413` | `Thích Var Chạm` |
| MSSV đội trưởng | `entry.1129402847` | mã ở dòng 1 của `TEAMS.md` |
| Mốc đang nộp | `entry.876659114` | chép đúng chuỗi ở bảng dưới |

Mỗi mốc là một trang riêng; `pageHistory` là `0,<số trang>`.

| Mốc | Chuỗi của ô "Mốc đang nộp" | `pageHistory` | Ô riêng của mốc |
|---|---|---|---|
| CP3 | `CP3 · 10:00 T7 (4đ) - Evidence, Video 30s AI thật & Lượt 1` | `0,3` | `entry.1325977975` link `evidence/summary.md` · `entry.755612318` link video 30 giây gọi AI thật · `entry.294721640` kết quả lượt 1 (x/N câu đạt, run ID) và phần chưa xong |
| CP4 | `CP4 · 14:30 T7 (4đ) - Lượt 2, Chi phí, Slide PDF & 4 ĐK xét giải` | `0,4` | `entry.1346310620` link `demo-slides.pdf` · `entry.951838028` link video demo dự phòng · `entry.172163015` lượt 1 → lượt 2, chi phí / task thành công, tên model · `entry.1309429580` bốn ô xác nhận (xem dưới) |

Ô `entry.1309429580` của CP4 là ô đánh dấu nhiều lựa chọn: gửi tham số này một lần cho mỗi điều kiện **đã thật sự đạt**, chép đúng chuỗi:

- `Đã có bản chạy thử gọi AI thật ở quyết định trung tâm`
- `Đã có bằng chứng pain ≥1 nguồn đạt ngưỡng trong evidence/`
- `Đã có bộ câu thử ≥20 câu + kết quả có % đạt (eval/report.md)`
- `Đã có file demo-slides.pdf ở thư mục gốc repo`

Mã ô (CP1: trang 1, CP2: trang 2) và chuỗi lựa chọn được đọc từ form ngày 27/11. BTC có thể sửa form, nên **đọc lại trước khi gửi** (bước 1).

## Cách gửi bằng dòng lệnh

1. Tải form, lấy `fbzx` mới và kiểm các mã ô còn đúng:

   ```bash
   FORM=https://docs.google.com/forms/d/e/1FAIpQLSdFqBLvf--GLbTUQ2vcFkkKDGsgT-LGT7oftBG_x8Pk-gMVwg
   curl -sL "$FORM/viewform" -o /tmp/form.html
   grep -o 'name="fbzx" value="[^"]*"' /tmp/form.html
   for e in 1325977975 755612318 294721640; do grep -c "$e" /tmp/form.html; done   # mỗi dòng phải > 0
   ```

2. Ghi nội dung ô dài vào file văn bản (tránh lỗi dấu nháy), rồi gửi. Ví dụ CP3:

   ```bash
   curl -sL -o /tmp/resp.html "$FORM/formResponse" \
     --data-urlencode "entry.15831452=H210" \
     --data-urlencode "entry.985403413=Thích Var Chạm" \
     --data-urlencode "entry.1129402847=<MSSV đội trưởng>" \
     --data-urlencode "entry.876659114=CP3 · 10:00 T7 (4đ) - Evidence, Video 30s AI thật & Lượt 1" \
     --data-urlencode "entry.1325977975=https://github.com/ToyzZone/K5-Day15-L3A-ThichVarCham/blob/main/evidence/summary.md" \
     --data-urlencode "entry.755612318=<link video>" \
     --data-urlencode "entry.294721640@/tmp/cp3-ket-qua.txt" \
     --data-urlencode "fvv=1" --data-urlencode "pageHistory=0,3" \
     --data-urlencode "fbzx=<giá trị vừa lấy>"
   ```

3. Kiểm đã ghi nhận. Không thấy dòng này thì form chưa nhận: đọc `/tmp/resp.html`, sửa rồi gửi lại.

   ```bash
   grep -o "Câu trả lời của bạn đã được ghi lại" /tmp/resp.html
   ```

4. Cập nhật bảng "Tình trạng" ở trên và commit.
